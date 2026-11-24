# -*- coding: utf-8 -*-
r"""
Mo phong quy dao gap-tha bac 5 CO PHA DUNG (dwell) tai diem moc - phien ban v2.

Muc dich:
  1. Sua dinh nghia overshoot / thoi gian xac lap: chi do trong cua so
     [t_arrival, t_arrival + dwell_s]. Overshoot la thanh phan vuot lo theo
     huong tiep can u_hat = (target - waypoint_truoc)/|...|.
  2. Quet T_segment tu 0,20 den 0,60 s (buoc 0,02) tim phuong an dat
     sai so cuoi dwell <= 1 mm VA overshoot <= 5 %.
  3. Lap bang phan ra chu ky toan he thong (mo phong + thi giac + Serial).

Chay:  D:\Python312\python.exe run.py
Khong sua file trong runs/2026-11-18-pid-quy-dao-bac5/.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

# -----------------------------------------------------------------------------
# Nap module IK/FK dung chung cua mo-hinh
# -----------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[4]
MODEL_DIR = REPO_ROOT / "nghien-cuu" / "mo-hinh"
IK_FK_MODULE_PATH = MODEL_DIR / "kiem-chung-ik-fk.py"

import importlib.util
spec = importlib.util.spec_from_file_location("kiem_chung_ik_fk", str(IK_FK_MODULE_PATH))
if spec is None or spec.loader is None:
    raise FileNotFoundError(f"Khong tim thay module IK/FK tai {IK_FK_MODULE_PATH}")
kiem_chung_ik_fk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kiem_chung_ik_fk)

inverse_kinematics = kiem_chung_ik_fk.inverse_kinematics
forward_kinematics_analytical = kiem_chung_ik_fk.forward_kinematics_analytical
compute_jacobian = kiem_chung_ik_fk.compute_jacobian

# -----------------------------------------------------------------------------
# Duong dan xuat
# -----------------------------------------------------------------------------
RUN_DIR = Path(__file__).resolve().parent
CONFIG_PATH = RUN_DIR / "config.json"
OUTPUT_DIR = RUN_DIR / "output"
FIGURES_DIR = RUN_DIR / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

OLD_RUN = RUN_DIR.parent / "2026-11-18-pid-quy-dao-bac5"
VISION_RUN = RUN_DIR.parent / "2026-11-18-thi-giac-hsv"


def load_config(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def set_seed(seed: int) -> None:
    np.random.seed(seed)


# -----------------------------------------------------------------------------
# Da thuc bac 5 cho mot doan
# -----------------------------------------------------------------------------
def quintic_coeffs(p0: float, p1: float, T: float) -> np.ndarray:
    return np.array([
        p0, 0.0, 0.0,
        10.0 * (p1 - p0) / T ** 3,
        -15.0 * (p1 - p0) / T ** 4,
        6.0 * (p1 - p0) / T ** 5,
    ], dtype=float)


def eval_quintic(coeffs: np.ndarray, t: float, T: float) -> Tuple[float, float, float]:
    if t <= 0.0:
        return float(coeffs[0]), 0.0, 0.0
    if t >= T:
        p1 = coeffs[0] + coeffs[3] * T ** 3 + coeffs[4] * T ** 4 + coeffs[5] * T ** 5
        return float(p1), 0.0, 0.0
    p = coeffs[0] + coeffs[3] * t ** 3 + coeffs[4] * t ** 4 + coeffs[5] * t ** 5
    v = 3.0 * coeffs[3] * t ** 2 + 4.0 * coeffs[4] * t ** 3 + 5.0 * coeffs[5] * t ** 4
    a = 6.0 * coeffs[3] * t + 12.0 * coeffs[4] * t ** 2 + 20.0 * coeffs[5] * t ** 3
    return float(p), float(v), float(a)


# -----------------------------------------------------------------------------
# Quy dao 3 doan bac 5 + dwell tai Pick va Place
# -----------------------------------------------------------------------------
class DwellQuinticTrajectory:
    """
    home -> pick  (T)  -- dwell --  pick -> place (T) -- dwell -- place -> home (T)
    Tong thoi gian = 3T + 2*dwell.
    Trong dwell: p = waypoint, v = 0, a = 0.
    """

    def __init__(self, waypoints: np.ndarray, T_segment: float, dwell_s: float):
        self.waypoints = np.asarray(waypoints, dtype=float)
        self.n_segments = self.waypoints.shape[0] - 1
        self.T = float(T_segment)
        self.dwell = float(dwell_s)
        self.coeffs = [
            np.vstack([quintic_coeffs(p0, p1, self.T)
                       for p0, p1 in zip(self.waypoints[i], self.waypoints[i + 1])])
            for i in range(self.n_segments)
        ]

    # --- thoi gian ---------------------------------------------------------
    def seg_start(self, i: int) -> float:
        return i * (self.T + self.dwell)

    def dwell_start(self, i: int) -> float:
        """Bat dau dwell sau doan thu i (chi co y nghia voi i=0,1)."""
        return self.seg_start(i) + self.T

    def total_time(self) -> float:
        return self.n_segments * self.T + (self.n_segments - 1) * self.dwell

    def arrival_times(self) -> List[float]:
        """Thoi diem toi Pick, Place, Home."""
        return [self.dwell_start(i) for i in range(self.n_segments)]

    # --- danh gia ----------------------------------------------------------
    def evaluate(self, t: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t = float(t)
        total = self.total_time()
        if t <= 0.0:
            return self.waypoints[0].copy(), np.zeros(3), np.zeros(3)
        if t >= total:
            return self.waypoints[-1].copy(), np.zeros(3), np.zeros(3)

        for i in range(self.n_segments):
            t0 = self.seg_start(i)
            t_arr = t0 + self.T
            if t <= t_arr:
                tloc = t - t0
                p = np.zeros(3)
                v = np.zeros(3)
                a = np.zeros(3)
                for axis in range(3):
                    p[axis], v[axis], a[axis] = eval_quintic(self.coeffs[i][axis], tloc, self.T)
                return p, v, a
            if t < t_arr + self.dwell:
                return self.waypoints[i + 1].copy(), np.zeros(3), np.zeros(3)
        return self.waypoints[-1].copy(), np.zeros(3), np.zeros(3)


# -----------------------------------------------------------------------------
# Tham chieu khop + noi suy
# -----------------------------------------------------------------------------
class JointReferenceInterpolator:
    def __init__(self, traj: DwellQuinticTrajectory,
                 delta_params: Dict[str, float], t_grid: np.ndarray):
        self.t_grid = np.asarray(t_grid, dtype=float)
        n = len(self.t_grid)
        self.theta_ref = np.zeros((n, 3))
        self.theta_dot_ref = np.zeros((n, 3))

        for i, ti in enumerate(self.t_grid):
            p_ref, v_ref, _ = traj.evaluate(ti)
            th, _ = inverse_kinematics(p_ref, delta_params)
            if th is None:
                raise ValueError(f"Khong co nghiem IK tai t={ti:.4f}, p={p_ref}")
            self.theta_ref[i] = th
            jac = compute_jacobian(p_ref, th, delta_params)["J_forward"]
            try:
                self.theta_dot_ref[i] = np.linalg.solve(jac, v_ref)
            except np.linalg.LinAlgError:
                self.theta_dot_ref[i] = np.zeros(3)

        self.theta_ddot_ref = np.zeros((n, 3))
        for axis in range(3):
            self.theta_ddot_ref[:, axis] = np.gradient(
                self.theta_dot_ref[:, axis], self.t_grid)

        self.cs_theta = [CubicSpline(self.t_grid, self.theta_ref[:, i], bc_type="clamped")
                         for i in range(3)]
        self.cs_omega = [CubicSpline(self.t_grid, self.theta_dot_ref[:, i], bc_type="clamped")
                         for i in range(3)]
        self.cs_alpha = [CubicSpline(self.t_grid, self.theta_ddot_ref[:, i], bc_type="clamped")
                         for i in range(3)]

    def __call__(self, t: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t = float(np.clip(t, self.t_grid[0], self.t_grid[-1]))
        th = np.array([self.cs_theta[i](t) for i in range(3)])
        om = np.array([self.cs_omega[i](t) for i in range(3)])
        al = np.array([self.cs_alpha[i](t) for i in range(3)])
        return th, om, al


# -----------------------------------------------------------------------------
# Mo hinh khop + PID + feed-forward
# -----------------------------------------------------------------------------
class JointDriveSimulation:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        jm = cfg["joint_model"]
        self.J = jm["J_kg_m2"]
        self.b = jm["b_Nm_s_rad"]
        self.tau_max = jm["tau_max_Nm"]
        self.g = cfg["robot_geometry_mm"]
        self.delta_params = {k: self.g[k] for k in ("f", "e", "rf", "re", "R_b", "r_p", "R")}
        self.Kp = cfg["pid_gains"]["Kp"]
        self.Ki = cfg["pid_gains"]["Ki"]
        self.Kd = cfg["pid_gains"]["Kd"]
        self.quantize = jm.get("quantize_feedback", False)
        self.enc_res = 2.0 * math.pi / jm.get("encoder_counts_per_rev", 4096)

    def _feedback(self, theta: np.ndarray) -> np.ndarray:
        return np.round(theta / self.enc_res) * self.enc_res if self.quantize else theta

    def dynamics(self, t: float, y: np.ndarray, interp: JointReferenceInterpolator,
                 use_ff: bool) -> np.ndarray:
        theta, omega, integral = y[0:3], y[3:6], y[6:9]
        th_ref, om_ref, al_ref = interp(t)
        e = th_ref - self._feedback(theta)
        de = om_ref - omega
        tau = self.Kp * e + self.Ki * integral + self.Kd * de
        if use_ff:
            tau = tau + self.J * al_ref + self.b * om_ref
        tau_sat = np.clip(tau, -self.tau_max, self.tau_max)
        saturated = np.abs(tau) >= self.tau_max * 0.999
        di = np.where(saturated, 0.0, e)
        alpha = (tau_sat - self.b * omega) / self.J
        return np.concatenate([omega, alpha, di])

    def simulate(self, traj: DwellQuinticTrajectory, use_ff: bool,
                 t_eval: np.ndarray) -> Dict[str, Any]:
        total = traj.total_time()
        n_grid = min(40000, max(500, int(round(total / 1e-3))))
        t_grid = np.linspace(0.0, total, n_grid)
        interp = JointReferenceInterpolator(traj, self.delta_params, t_grid)

        theta0, _, _ = interp(0.0)
        y0 = np.concatenate([theta0, np.zeros(3), np.zeros(3)])

        sol = solve_ivp(
            lambda tt, yy: self.dynamics(tt, yy, interp, use_ff),
            [0.0, total], y0, t_eval=t_eval, method="RK45",
            atol=self.cfg["simulation"]["atol"],
            rtol=self.cfg["simulation"]["rtol"],
            max_step=self.cfg["simulation"]["max_step_s"],
        )

        n = len(sol.t)
        theta = sol.y[0:3, :].T
        omega = sol.y[3:6, :].T
        integral = sol.y[6:9, :].T

        p_ref = np.zeros((n, 3))
        p_act = np.zeros((n, 3))
        err = np.zeros(n)
        tau = np.zeros((n, 3))
        th_ref_l = np.zeros((n, 3))
        om_ref_l = np.zeros((n, 3))

        for i, ti in enumerate(sol.t):
            pref, _, _ = traj.evaluate(ti)
            p_ref[i] = pref
            th_ref_l[i], om_ref_l[i], al_ref = interp(ti)
            p_act[i], _ = forward_kinematics_analytical(theta[i], self.delta_params)
            err[i] = float(np.linalg.norm(p_act[i] - pref))

            e = th_ref_l[i] - theta[i]
            de = om_ref_l[i] - omega[i]
            tau_cmd = self.Kp * e + self.Ki * integral[i] + self.Kd * de
            if use_ff:
                tau_cmd = tau_cmd + self.J * al_ref + self.b * om_ref_l[i]
            tau[i] = np.clip(tau_cmd, -self.tau_max, self.tau_max)

        return {"t": sol.t, "p_ref": p_ref, "p_actual": p_act, "err_mm": err,
                "theta": theta, "theta_ref": th_ref_l, "omega": omega,
                "omega_ref": om_ref_l, "tau": tau, "cycle_s": total}


# -----------------------------------------------------------------------------
# Metric: overshoot va thoi gian xac lap TRONG CUA SO DWELL
# -----------------------------------------------------------------------------
def dwell_window_metrics(t: np.ndarray, p_actual: np.ndarray,
                         target: np.ndarray, prev_wp: np.ndarray,
                         t_arrival: float, dwell: float, tol_mm: float
                         ) -> Dict[str, Any]:
    mask = (t >= t_arrival - 1e-12) & (t <= t_arrival + dwell + 1e-12)
    tt = t[mask]
    pp = p_actual[mask]
    if len(tt) == 0:
        raise ValueError("Cua so dwell rong - kiem tra lai luoi thoi gian.")

    u = target - prev_wp
    u = u / np.linalg.norm(u)

    # s(t) > 0 nghia la da vuot qua dich theo huong tiep can
    s = (pp - target) @ u
    overshoot_mm = float(max(0.0, np.max(s)))

    dist = np.linalg.norm(pp - target, axis=1)
    settled_rel = None
    for idx in np.where(dist <= tol_mm)[0]:
        if np.all(dist[idx:] <= tol_mm):
            settled_rel = float(tt[idx] - t_arrival)
            break

    return {
        "overshoot_mm": overshoot_mm,
        "overshoot_signed_min_mm": float(np.min(s)),
        "err_end_dwell_mm": float(dist[-1]),
        "err_max_dwell_mm": float(np.max(dist)),
        "settled_within_dwell": settled_rel is not None,
        "settling_rel_s": settled_rel,
        "settling_abs_s": (float(tt[0]) + settled_rel) if settled_rel is not None else None,
        "n_samples": int(len(tt)),
    }


def compute_metrics(res: Dict[str, Any], cfg: Dict[str, Any], traj: DwellQuinticTrajectory
                    ) -> Dict[str, Any]:
    t = res["t"]
    p_actual = res["p_actual"]
    wp = traj.waypoints
    arrivals = traj.arrival_times()
    tol = cfg["criteria"]["settling_error_mm"]

    pick = dwell_window_metrics(t, p_actual, wp[1], wp[0], arrivals[0], traj.dwell, tol)
    place = dwell_window_metrics(t, p_actual, wp[2], wp[1], arrivals[1], traj.dwell, tol)

    # Kiem tra chan: overshoot khong the lon hon sai so bam cuc dai toan cuc
    max_err = float(np.max(res["err_mm"]))
    for name, m in (("pick", pick), ("place", place)):
        if m["overshoot_mm"] > max_err + 1e-9:
            raise RuntimeError(
                f"overshoot_{name}={m['overshoot_mm']:.4f} mm > max_err={max_err:.4f} mm "
                "- dinh nghia overshoot van sai, dung xuat so.")

    step_pick = float(np.linalg.norm(wp[1] - wp[0]))
    step_place = float(np.linalg.norm(wp[2] - wp[1]))

    tau_max = float(np.max(np.abs(res["tau"])))
    omega_max = float(np.max(np.abs(res["omega"])))
    jm = cfg["joint_model"]

    return {
        "max_err_mm": max_err,
        "rmse_err_mm": float(np.sqrt(np.mean(res["err_mm"] ** 2))),
        "overshoot_pick_mm": pick["overshoot_mm"],
        "overshoot_pick_pct": 100.0 * pick["overshoot_mm"] / step_pick,
        "overshoot_place_mm": place["overshoot_mm"],
        "overshoot_place_pct": 100.0 * place["overshoot_mm"] / step_place,
        "err_pick_end_dwell_mm": pick["err_end_dwell_mm"],
        "err_place_end_dwell_mm": place["err_end_dwell_mm"],
        "err_pick_max_dwell_mm": pick["err_max_dwell_mm"],
        "err_place_max_dwell_mm": place["err_max_dwell_mm"],
        "settling_pick_rel_s": pick["settling_rel_s"],
        "settling_place_rel_s": place["settling_rel_s"],
        "settling_pick_abs_s": pick["settling_abs_s"],
        "settling_place_abs_s": place["settling_abs_s"],
        "settled_within_dwell": bool(pick["settled_within_dwell"] and place["settled_within_dwell"]),
        "cycle_s": res["cycle_s"],
        "cycle_motion_s": 3.0 * traj.T,
        "tau_max_Nm": tau_max,
        "omega_max_rad_s": omega_max,
        "tau_violation": bool(tau_max > jm["tau_max_Nm"] * 1.001),
        "omega_violation": bool(omega_max > jm["omega_max_rad_s"] * 1.001),
    }


# -----------------------------------------------------------------------------
# Chay mot cau hinh
# -----------------------------------------------------------------------------
def make_t_eval(total: float, dt: float) -> np.ndarray:
    n = max(2, int(round(total / dt)) + 1)
    return np.linspace(0.0, total, n)


def run_configuration(cfg: Dict[str, Any], waypoints: np.ndarray, T: float,
                      dwell: float, use_ff: bool, label: str,
                      Kp: Optional[float] = None, Ki: Optional[float] = None,
                      Kd: Optional[float] = None) -> Dict[str, Any]:
    cfg_run = json.loads(json.dumps(cfg))
    if Kp is not None:
        cfg_run["pid_gains"].update({"Kp": Kp, "Ki": Ki, "Kd": Kd})
    traj = DwellQuinticTrajectory(waypoints, T, dwell)
    t_eval = make_t_eval(traj.total_time(), cfg["simulation"]["dt_s"])
    sim = JointDriveSimulation(cfg_run)
    res = sim.simulate(traj, use_ff, t_eval)
    return {"label": label, "use_ff": use_ff, "T": T, "dwell": dwell,
            "traj": traj, "result": res, "metrics": compute_metrics(res, cfg_run, traj)}


def scan_period(cfg: Dict[str, Any], waypoints: np.ndarray) -> List[Dict[str, Any]]:
    tr = cfg["trajectory"]
    dwell = tr["dwell_s"]
    Ts = np.arange(tr["T_scan_min_s"], tr["T_scan_max_s"] + 1e-9, tr["T_scan_step_s"])
    rows = []
    for T in Ts:
        run = run_configuration(cfg, waypoints, float(T), dwell, use_ff=True, label=f"T={T:.2f}")
        m = run["metrics"]
        ok = (m["err_pick_end_dwell_mm"] <= cfg["criteria"]["settling_error_mm"]
              and m["err_place_end_dwell_mm"] <= cfg["criteria"]["settling_error_mm"]
              and m["settled_within_dwell"]
              and m["overshoot_pick_pct"] <= cfg["criteria"]["overshoot_max_percent"]
              and m["overshoot_place_pct"] <= cfg["criteria"]["overshoot_max_percent"]
              and not m["tau_violation"] and not m["omega_violation"])
        rows.append({
            "T_s": float(T),
            "cycle_motion_s": 3.0 * float(T),
            "cycle_with_dwell_s": m["cycle_s"],
            "rmse_mm": m["rmse_err_mm"],
            "max_err_mm": m["max_err_mm"],
            "overshoot_pick_pct": m["overshoot_pick_pct"],
            "overshoot_place_pct": m["overshoot_place_pct"],
            "err_pick_end_dwell_mm": m["err_pick_end_dwell_mm"],
            "err_place_end_dwell_mm": m["err_place_end_dwell_mm"],
            "settling_pick_rel_s": m["settling_pick_rel_s"],
            "settling_place_rel_s": m["settling_place_rel_s"],
            "tau_max_Nm": m["tau_max_Nm"],
            "omega_max_rad_s": m["omega_max_rad_s"],
            "tau_violation": m["tau_violation"],
            "omega_violation": m["omega_violation"],
            "pass": bool(ok),
        })
        print(f"  T={T:.2f}s cycle={m['cycle_s']:.3f}s RMSE={m['rmse_err_mm']:.4f}mm "
              f"err_end={m['err_pick_end_dwell_mm']:.4f}/{m['err_place_end_dwell_mm']:.4f}mm "
              f"over={m['overshoot_pick_pct']:.2f}/{m['overshoot_place_pct']:.2f}% "
              f"tau={m['tau_max_Nm']:.2f}Nm omega={m['omega_max_rad_s']:.2f}rad/s "
              f"-> {'DAT' if ok else 'KHONG'}")
    return rows


# -----------------------------------------------------------------------------
# Nguon so lieu ngoai mo phong (doc tu file, khong go tay)
# -----------------------------------------------------------------------------
def read_budget_sources() -> Dict[str, Any]:
    src: Dict[str, Any] = {}
    with open(VISION_RUN / "output" / "metrics.json", "r", encoding="utf-8") as f:
        vm = json.load(f)
    src["vision_timing"] = vm["timing_ms"]
    with open(VISION_RUN / "output" / "webcam_info.json", "r", encoding="utf-8") as f:
        wc = json.load(f)
    src["webcam"] = wc
    src["vision_ketqua_p95_ms"] = None  # se ghi chu neu KETQUA.md khac metrics.json
    old = OLD_RUN / "output" / "metrics.json"
    src["old_metrics"] = json.load(open(old, "r", encoding="utf-8")) if old.exists() else None
    return src


# -----------------------------------------------------------------------------
# Ve hinh
# -----------------------------------------------------------------------------
def plot_error(cfg: Dict[str, Any], run_ff: Dict[str, Any], run_pid: Dict[str, Any]) -> None:
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 12,
                         "axes.labelsize": 11, "legend.fontsize": 10})
    r = run_ff["result"]
    traj = run_ff["traj"]
    t = r["t"]
    arr = traj.arrival_times()

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 7.5), dpi=300,
                                  gridspec_kw={"height_ratios": [1.35, 1]})

    # (a) sai so bam + vung dwell
    ax.semilogy(t, r["err_mm"] + 1e-6, color="#1f77b4", lw=1.3, label="PID + feed-forward")
    ax.semilogy(run_pid["result"]["t"], run_pid["result"]["err_mm"] + 1e-6,
                color="#ff7f0e", lw=1.0, alpha=0.8, label="PID thuần")
    ax.axhline(cfg["criteria"]["settling_error_mm"], color="red", ls="--", lw=1.0,
               label=f"Ngưỡng {cfg['criteria']['settling_error_mm']:.0f} mm")
    for i, ta in enumerate(arr[:2]):
        ax.axvspan(ta, ta + traj.dwell, color="green", alpha=0.13,
                   label="Cửa sổ dwell (kẹp/thả)" if i == 0 else None)
        ax.axvline(ta, color="green", ls=":", lw=1.0)
    ax.set_xlabel("Thời gian (s)")
    ax.set_ylabel(r"Sai số bám $\|p_{ref}-p_{thực}\|$ (mm)")
    ax.set_title("(a) Sai số bám theo thời gian — vùng dwell tại Pick và Place")
    ax.grid(True, which="both", ls=":", alpha=0.45)
    ax.legend(loc="lower right", ncol=2)

    # (b) thanh phan vuot lo theo huong tiep can (zoom quanh dich)
    for name, idx_t, prev, tgt, col in (
            ("Pick", 0, traj.waypoints[0], traj.waypoints[1], "#d62728"),
            ("Place", 1, traj.waypoints[1], traj.waypoints[2], "#9467bd")):
        ta = arr[idx_t]
        u = (tgt - prev) / np.linalg.norm(tgt - prev)
        mask = (t >= ta - 0.30) & (t <= ta + traj.dwell + 0.05)
        s = (r["p_actual"][mask] - tgt) @ u
        ax2.plot(t[mask] - ta, s, color=col, lw=1.4,
                 label=f"{name}: max $s$ = {max(0.0, s.max()):.3f} mm")
        imax = int(np.argmax(s))
        if s[imax] >= 0.0:
            ax2.plot(t[mask][imax] - ta, s[imax], "o", color=col, ms=5)
    ax2.axvspan(0.0, traj.dwell, color="green", alpha=0.13)
    ax2.axhline(0.0, color="black", lw=0.8)
    ax2.set_xlim(-0.30, traj.dwell + 0.05)
    ax2.set_ylim(-10.0, 2.0)
    ax2.set_xlabel("Thời gian tính từ lúc tới đích (s)")
    ax2.set_ylabel("Vượt lố theo hướng tiếp cận $s$ (mm)")
    ax2.set_title("(b) Thành phần vượt lố thật ($s>0$ = đã đi quá đích), zoom ±10 mm")
    ax2.grid(True, ls=":", alpha=0.45)
    ax2.legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "sai_so_va_dwell.png", dpi=300)
    plt.close(fig)


def plot_scan(cfg: Dict[str, Any], rows: List[Dict[str, Any]],
              T_best: Optional[float]) -> None:
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 12,
                         "axes.labelsize": 11, "legend.fontsize": 10})
    T = np.array([r["T_s"] for r in rows])
    cyc = np.array([r["cycle_with_dwell_s"] for r in rows])
    over = np.array([max(r["overshoot_pick_pct"], r["overshoot_place_pct"]) for r in rows])
    err = np.array([max(r["err_pick_end_dwell_mm"], r["err_place_end_dwell_mm"]) for r in rows])
    tau = np.array([r["tau_max_Nm"] for r in rows])
    om = np.array([r["omega_max_rad_s"] for r in rows])
    ok = np.array([r["pass"] for r in rows])
    tau_lim = cfg["joint_model"]["tau_max_Nm"]
    om_lim = cfg["joint_model"]["omega_max_rad_s"]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), dpi=300)
    floor = 1e-3

    # (a) overshoot
    ax = axes[0, 0]
    ax.semilogy(T, np.maximum(over, floor), "o-", color="#d62728", lw=1.5, ms=4)
    ax.axhline(cfg["criteria"]["overshoot_max_percent"], color="#d62728", ls="--", lw=1.2,
               label=f"Ngưỡng {cfg['criteria']['overshoot_max_percent']:.0f} %")
    ax.set_ylim(floor, 10)
    ax.set_xlabel("Thời gian mỗi đoạn T (s)")
    ax.set_ylabel("Overshoot lớn nhất Pick/Place (%)")
    ax.set_title(f"(a) Overshoot — lớn nhất {over.max():.2f} %, cách ngưỡng "
                 f"{cfg['criteria']['overshoot_max_percent']/max(over.max(),1e-9):.0f} lần")
    ax.grid(True, which="both", ls=":", alpha=0.45)
    ax.legend(loc="center right")

    # (b) sai so cuoi dwell
    ax = axes[0, 1]
    ax.semilogy(T, np.maximum(err, floor), "s-", color="#1f77b4", lw=1.5, ms=4)
    ax.axhline(cfg["criteria"]["settling_error_mm"], color="#1f77b4", ls="--", lw=1.2,
               label=f"Ngưỡng {cfg['criteria']['settling_error_mm']:.0f} mm")
    ax.set_ylim(floor, 10)
    ax.set_xlabel("Thời gian mỗi đoạn T (s)")
    ax.set_ylabel("Sai số cuối dwell lớn nhất (mm)")
    ax.set_title(f"(b) Sai số cuối dwell — lớn nhất {err.max():.3f} mm, "
                 f"bằng {100*err.max()/cfg['criteria']['settling_error_mm']:.0f} % ngưỡng")
    ax.grid(True, which="both", ls=":", alpha=0.45)
    ax.legend(loc="center right")

    # (c) muc do cham gioi han vat ly
    ax = axes[1, 0]
    ax.plot(T, om / om_lim, "o-", color="#2ca02c", lw=1.5, ms=4,
            label="ω_max / 10 rad/s")
    ax.plot(T, tau / tau_lim, "s-", color="#ff7f0e", lw=1.5, ms=4,
            label="τ_max / 2 N·m")
    ax.axhline(1.0, color="red", ls="--", lw=1.2, label="Giới hạn")
    if T_best is not None:
        ax.axvline(T_best, color="black", ls="-.", lw=1.1)
        ax.annotate(f"T = {T_best:.2f} s", xy=(T_best, 0.42), xytext=(6, 0),
                    textcoords="offset points", fontsize=10)
    ax.set_ylim(0, 1.25)
    ax.set_xlabel("Thời gian mỗi đoạn T (s)")
    ax.set_ylabel("Giá trị / giới hạn (—)")
    ax.set_title("(c) Ràng buộc chặn: ω_max bị chạm trước τ_max")
    ax.grid(True, ls=":", alpha=0.45)
    ax.legend(loc="lower right")

    # (d) chu ky
    ax = axes[1, 1]
    ax.plot(T, cyc, "o-", color="#2ca02c", lw=1.5, ms=4, label="Chu kỳ 3T + 2×0,25 s")
    ax.axhline(cfg["criteria"]["total_cycle_target_s"], color="red", ls="--", lw=1.3,
               label=f"Mục tiêu toàn hệ {cfg['criteria']['total_cycle_target_s']} s")
    ax.axhline(cfg["criteria"]["cycle_time_target_s"], color="gray", ls=":", lw=1.3,
               label="Mốc 1,5 s thuần chuyển động")
    if np.any(ok):
        ax.plot(T[ok], cyc[ok], "o", mfc="none", mec="black", ms=10, mew=1.4,
                label="Đạt chỉ tiêu 1 mm / 5 %")
    if T_best is not None:
        ax.axvline(T_best, color="black", ls="-.", lw=1.1)
        ax.annotate(f"T = {T_best:.2f} s", xy=(T_best, cyc.min()), xytext=(5, 8),
                    textcoords="offset points", fontsize=10)
    ax.set_xlabel("Thời gian mỗi đoạn T (s)")
    ax.set_ylabel("Chu kỳ chuyển động + dwell (s)")
    ax.set_title("(d) Chu kỳ theo T và phương án đạt chỉ tiêu")
    ax.grid(True, ls=":", alpha=0.45)
    ax.legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "quet_chu_ky.png", dpi=300)
    plt.close(fig)


# -----------------------------------------------------------------------------
# Xuat CSV / JSON
# -----------------------------------------------------------------------------
def export_trajectory_csv(run: Dict[str, Any]) -> None:
    r = run["result"]
    header = ["t_s", "x_ref_mm", "y_ref_mm", "z_ref_mm",
              "x_actual_mm", "y_actual_mm", "z_actual_mm", "err_mm",
              "theta1_ref_rad", "theta2_ref_rad", "theta3_ref_rad",
              "theta1_rad", "theta2_rad", "theta3_rad",
              "omega1_rad_s", "omega2_rad_s", "omega3_rad_s",
              "tau1_Nm", "tau2_Nm", "tau3_Nm"]
    rows = np.column_stack([r["t"], r["p_ref"], r["p_actual"], r["err_mm"],
                            r["theta_ref"], r["theta"], r["omega"], r["tau"]])
    name = run["label"].replace(" ", "_").replace("+", "plus")
    np.savetxt(OUTPUT_DIR / f"{name}.csv", rows, delimiter=",",
               header=",".join(header), comments="", fmt="%.6e")


def csv_num(v: Optional[float], nd: int) -> str:
    if v is None:
        return ""
    if abs(v) < 0.5 * 10 ** (-nd):
        v = 0.0
    return f"{v:.{nd}f}"


def export_scan_csv(rows: List[Dict[str, Any]]) -> None:
    header = ("T_s,cycle_motion_s,cycle_with_dwell_s,rmse_mm,max_err_mm,"
              "overshoot_pick_pct,overshoot_place_pct,"
              "err_pick_end_dwell_mm,err_place_end_dwell_mm,"
              "settling_pick_rel_s,settling_place_rel_s,"
              "tau_max_Nm,omega_max_rad_s,tau_violation,omega_violation,pass")
    lines = [header]
    for r in rows:
        lines.append(",".join([
            f"{r['T_s']:.3f}", f"{r['cycle_motion_s']:.4f}", f"{r['cycle_with_dwell_s']:.4f}",
            f"{r['rmse_mm']:.6f}", f"{r['max_err_mm']:.6f}",
            f"{r['overshoot_pick_pct']:.4f}", f"{r['overshoot_place_pct']:.4f}",
            f"{r['err_pick_end_dwell_mm']:.6f}", f"{r['err_place_end_dwell_mm']:.6f}",
            csv_num(r["settling_pick_rel_s"], 4), csv_num(r["settling_place_rel_s"], 4),
            f"{r['tau_max_Nm']:.5f}", f"{r['omega_max_rad_s']:.5f}",
            str(int(r["tau_violation"])), str(int(r["omega_violation"])),
            str(int(r["pass"])),
        ]))
    with open(OUTPUT_DIR / "quet-chu-ky.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# -----------------------------------------------------------------------------
# Bao cao KETQUA.md
# -----------------------------------------------------------------------------
def fmt(v, nd=4, dash="—"):
    if v is None:
        return dash
    if abs(v) < 0.5 * 10 ** (-nd):
        v = 0.0
    return f"{v:.{nd}f}".replace(".", ",")


def write_report(cfg: Dict[str, Any], main_pid: Dict[str, Any], main_ff: Dict[str, Any],
                 rows: List[Dict[str, Any]], T_best: Optional[float],
                 src: Dict[str, Any], elapsed_s: float) -> None:
    tr = cfg["trajectory"]
    dwell = tr["dwell_s"]
    crit = cfg["criteria"]
    b = cfg["budget_ngoai_mo_phong"]
    m_pid, m_ff = main_pid["metrics"], main_ff["metrics"]
    vm = src["vision_timing"]
    wc = src["webcam"]
    old = src["old_metrics"]

    ok_rows = [r for r in rows if r["pass"]]
    best = min(ok_rows, key=lambda r: r["T_s"]) if ok_rows else None

    L: List[str] = []
    L.append("# Kết quả mô phỏng v2 — quỹ đạo gắp–thả có pha dừng (dwell)\n")
    L.append(f"**Run:** `{cfg['run_name']}`  ")
    L.append(f"**Ngày chạy:** {cfg['ngay_chay']}  ")
    L.append(f"**Seed:** {cfg['seed']}  ")
    L.append(f"**Python:** {cfg['python']}  ")
    L.append(f"**Thời gian chạy script:** {elapsed_s:.1f} s  ")
    L.append(f"**Dwell:** {fmt(dwell,2)} s (danh định, nguồn `tong-quan.md` mục 7.1: 0,2–0,3 s)\n")

    L.append("## 1. Khác biệt so với bản cũ — metric đã sửa\n")
    L.append("Bản cũ `2026-11-18-pid-quy-dao-bac5` đo trong cửa sổ "
             "`[target − 0,9T, target + 0,15T]`. Vì quỹ đạo **không có thời gian dừng**, "
             "phần `+0,15T` rơi vào đoạn kế tiếp, nên đại lượng đo được là khoảng cách robot "
             "**rời đích**, không phải vọt lố.\n")
    if old:
        o1 = old["main_comparison"]["PID_thuan"]
        o2 = old["main_comparison"]["PID_plus_FF"]
        L.append("| Chỉ số | Bản cũ — PID thuần | Bản cũ — PID+FF | Bản v2 — PID thuần | Bản v2 — PID+FF |")
        L.append("| --- | --- | --- | --- | --- |")
        L.append(f"| Overshoot Pick (mm / %) | {fmt(o1['overshoot_pick_mm'],2)} / "
                 f"{fmt(o1['overshoot_pick_pct'],2)} | {fmt(o2['overshoot_pick_mm'],2)} / "
                 f"{fmt(o2['overshoot_pick_pct'],2)} | {fmt(m_pid['overshoot_pick_mm'],3)} / "
                 f"{fmt(m_pid['overshoot_pick_pct'],3)} | {fmt(m_ff['overshoot_pick_mm'],3)} / "
                 f"{fmt(m_ff['overshoot_pick_pct'],3)} |")
        L.append(f"| Overshoot Place (mm / %) | {fmt(o1['overshoot_place_mm'],2)} / "
                 f"{fmt(o1['overshoot_place_pct'],2)} | {fmt(o2['overshoot_place_mm'],2)} / "
                 f"{fmt(o2['overshoot_place_pct'],2)} | {fmt(m_pid['overshoot_place_mm'],3)} / "
                 f"{fmt(m_pid['overshoot_place_pct'],3)} | {fmt(m_ff['overshoot_place_mm'],3)} / "
                 f"{fmt(m_ff['overshoot_place_pct'],3)} |")
        L.append(f"| `max_err` toàn cục (mm) | {fmt(o1['max_err_mm'],3)} | "
                 f"{fmt(o2['max_err_mm'],3)} | {fmt(m_pid['max_err_mm'],3)} | "
                 f"{fmt(m_ff['max_err_mm'],3)} |")
        L.append(f"| Thời gian xác lập Pick (s) | {fmt(o1.get('settling_pick_s'),3)} | "
                 f"{fmt(o2.get('settling_pick_s'),3)} | {fmt(m_pid['settling_pick_rel_s'],3)} | "
                 f"{fmt(m_ff['settling_pick_rel_s'],3)} |")
        L.append(f"| Chu kỳ (s) | {fmt(o1['cycle_s'],3)} (3T) | {fmt(o2['cycle_s'],3)} (3T) | "
                 f"{fmt(m_pid['cycle_s'],3)} | {fmt(m_ff['cycle_s'],3)} |")
        L.append("")
        L.append("Đọc bảng: cột “bản cũ” đo cả đoạn **rời đích** nên overshoot 6,52 mm / 4,35 % "
                 "(PID thuần) lớn hơn cả `max_err` 1,158 mm — tự mâu thuẫn. Đo đúng trong dwell, "
                 "vọt lố thật chỉ còn **0,20 mm / 0,13 %** (PID thuần) và **0 mm / 0 %** (PID+FF). "
                 "Con số 4,35 % trước đây là **sai về định nghĩa**, không phải đặc tính của hệ.\n")

    L.append("**Định nghĩa mới (dùng trong run này):**\n")
    L.append("- Cửa sổ đo chỉ là `[t_arrival, t_arrival + dwell]`.")
    L.append("- Hướng tiếp cận `û = (p_target − p_waypoint_trước)/‖·‖`, thành phần vượt lố "
             "`s(t) = (p(t) − p_target)·û`; **overshoot = max(0, max s(t))**.")
    L.append("- Thời gian xác lập = thời điểm đầu tiên trong dwell mà `‖p − p_target‖ ≤ 1 mm` "
             "và **giữ ≤ 1 mm đến hết dwell**; không đạt thì ghi `—` kèm sai số cuối dwell.")
    L.append("- Script raise lỗi nếu `overshoot > max_err` (kiểm tra chặn ở "
             "`compute_metrics`).\n")

    L.append("## 2. Kết quả tại T mặc định = "
             f"{fmt(tr['T_default_s'],2)} s (chu kỳ {fmt(m_ff['cycle_s'],2)} s)\n")
    L.append("| Chỉ số | PID thuần | PID + feed-forward |")
    L.append("| --- | --- | --- |")
    for key, label, nd in [
            ("max_err_mm", "Sai số bám cực đại (mm)", 4),
            ("rmse_err_mm", "RMSE sai số bám (mm)", 4),
            ("overshoot_pick_mm", "Overshoot Pick (mm)", 4),
            ("overshoot_pick_pct", "Overshoot Pick (%)", 3),
            ("overshoot_place_mm", "Overshoot Place (mm)", 4),
            ("overshoot_place_pct", "Overshoot Place (%)", 3),
            ("err_pick_end_dwell_mm", "Sai số cuối dwell tại Pick (mm)", 4),
            ("err_place_end_dwell_mm", "Sai số cuối dwell tại Place (mm)", 4),
            ("err_pick_max_dwell_mm", "Sai số lớn nhất trong dwell tại Pick (mm)", 4),
            ("err_place_max_dwell_mm", "Sai số lớn nhất trong dwell tại Place (mm)", 4),
            ("settling_pick_rel_s", "Thời gian xác lập Pick, tính từ lúc tới (s)", 3),
            ("settling_place_rel_s", "Thời gian xác lập Place (s)", 3),
            ("tau_max_Nm", "Mô-men cực đại (N·m)", 3),
            ("omega_max_rad_s", "Tốc độ góc cực đại (rad/s)", 3)]:
        L.append(f"| {label} | {fmt(m_pid.get(key), nd)} | {fmt(m_ff.get(key), nd)} |")
    L.append(f"| Vi phạm τ_max = {cfg['joint_model']['tau_max_Nm']} N·m | "
             f"{'Có' if m_pid['tau_violation'] else 'Không'} | "
             f"{'Có' if m_ff['tau_violation'] else 'Không'} |")
    L.append(f"| Vi phạm ω_max = {cfg['joint_model']['omega_max_rad_s']} rad/s | "
             f"{'Có' if m_pid['omega_violation'] else 'Không'} | "
             f"{'Có' if m_ff['omega_violation'] else 'Không'} |\n")
    L.append("Feed-forward giữ overshoot gần như không đổi nhưng giảm mạnh RMSE bám trong lúc "
             "chuyển động; sai số **cuối dwell** mới là đại lượng quyết định có kẹp được vật hay không.\n")
    if m_pid["settling_pick_rel_s"] is not None and m_ff["settling_pick_rel_s"] is not None \
            and m_pid["settling_pick_rel_s"] < 1e-3 and m_ff["settling_place_rel_s"] < 1e-3:
        L.append(f"**Đọc đúng con số thời gian xác lập = 0 s:** sai số lớn nhất *trong suốt* dwell "
                 f"chỉ là {fmt(m_ff['err_pick_max_dwell_mm'],3)} mm (Pick) và "
                 f"{fmt(m_ff['err_place_max_dwell_mm'],3)} mm (Place), tức robot **đã nằm trong "
                 f"±1 mm ngay tại thời điểm tới đích**. Vì vậy thời gian xác lập theo ngưỡng 1 mm "
                 "bằng 0 — không phải lỗi, mà là ngưỡng 1 mm quá rộng so với sai số thực của mô "
                 "hình lý tưởng. Giới hạn thực của mô hình này là **độ phân giải encoder** "
                 "(4096 xung/vòng ≈ 1,53 mrad ≈ 0,1 mm tại điểm cuối), không phải động học.\n")
    L.append(f"**PID thuần có sai số cuối dwell tại Pick nhỏ hơn PID+FF** "
             f"({fmt(m_pid['err_pick_end_dwell_mm'],3)} so với {fmt(m_ff['err_pick_end_dwell_mm'],3)} mm). "
             "Chênh lệch này cỡ một nấc lượng tử encoder (~0,1 mm) và do trạng thái tích phân khác "
             "nhau, **không phải PID+FF kém hơn**; ở đoạn Place hai bộ trùng nhau "
             f"({fmt(m_pid['err_place_end_dwell_mm'],3)} mm).\n")

    L.append("## 2b. Kiểm tra chặn định nghĩa\n")
    L.append(f"- `overshoot_pick = {fmt(m_ff['overshoot_pick_mm'],3)} mm` ≤ "
             f"`max_err = {fmt(m_ff['max_err_mm'],3)} mm` — thoả điều kiện chặn trong code.")
    L.append("- Nếu một lần chạy nào cho overshoot > max_err, `compute_metrics` sẽ raise "
             "`RuntimeError` và không xuất số.\n")

    L.append("## 3. Quét chu kỳ T = "
             f"{fmt(tr['T_scan_min_s'],2)}…{fmt(tr['T_scan_max_s'],2)} s "
             f"(bước {fmt(tr['T_scan_step_s'],2)} s)\n")
    L.append("Tiêu chí đạt: **sai số cuối dwell ≤ 1 mm** ở cả Pick và Place, **overshoot ≤ 5 %**, "
             "không vi phạm τ_max/ω_max.\n")
    L.append("| T (s) | Chu kỳ 3T+0,5 (s) | RMSE (mm) | max_err (mm) | Overshoot Pick (%) | "
             "Overshoot Place (%) | Sai số cuối dwell Pick/Place (mm) | t_xác_lập Pick/Place (s) | "
             "τ_max (N·m) | ω_max (rad/s) | Đạt? |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        flag = "Đạt" if r["pass"] else "Không"
        viol = []
        if r["tau_violation"]:
            viol.append("τ")
        if r["omega_violation"]:
            viol.append("ω")
        if viol:
            flag += " (vi phạm " + ",".join(viol) + ")"
        L.append("| " + " | ".join([
            fmt(r["T_s"], 2), fmt(r["cycle_with_dwell_s"], 3), fmt(r["rmse_mm"], 4),
            fmt(r["max_err_mm"], 4), fmt(r["overshoot_pick_pct"], 2),
            fmt(r["overshoot_place_pct"], 2),
            f"{fmt(r['err_pick_end_dwell_mm'],4)} / {fmt(r['err_place_end_dwell_mm'],4)}",
            f"{fmt(r['settling_pick_rel_s'],3)} / {fmt(r['settling_place_rel_s'],3)}",
            fmt(r["tau_max_Nm"], 3), fmt(r["omega_max_rad_s"], 2), flag]) + " |")
    L.append("")
    L.append("**Đọc bảng:** cột `t_xác_lập` bằng 0 ở mọi T vì sai số lớn nhất trong dwell luôn "
             f"< 1 mm (0,12–0,33 mm) — robot vào vùng ±1 mm ngay khi tới đích; cột này chỉ trở "
             "nên có nghĩa khi siết ngưỡng xuống cỡ 0,1 mm (xem mục 6). Ràng buộc thực sự chặn T "
             "là **ω_max = 10 rad/s**: T = 0,22 s cho 10,53 rad/s (vượt 5,3 %), T = 0,20 s cho "
             "11,64 rad/s. Bước quét 0,02 s nên biên thật nằm giữa 0,22 và 0,24 s; muốn chốt "
             "chính xác phải quét mịn hơn. **Nếu chỉ xét chất lượng** (1 mm và 5 %), cả T = 0,20 s "
             "cũng đạt (0,122/0,151 mm; 0,05 %) — nút thắt là **tốc độ góc**, không phải độ chính xác.\n")

    if best:
        L.append(f"**T nhỏ nhất đạt chỉ tiêu: T = {fmt(best['T_s'],2)} s**, chu kỳ chuyển động "
                 f"có dwell = **{fmt(best['cycle_with_dwell_s'],3)} s**. Tại đó: overshoot "
                 f"{fmt(best['overshoot_pick_pct'],2)} % / {fmt(best['overshoot_place_pct'],2)} %, "
                 f"sai số cuối dwell {fmt(best['err_pick_end_dwell_mm'],3)} / "
                 f"{fmt(best['err_place_end_dwell_mm'],3)} mm, τ_max = "
                 f"{fmt(best['tau_max_Nm'],3)} N·m, ω_max = {fmt(best['omega_max_rad_s'],2)} rad/s.\n")
    else:
        L.append("**Không có giá trị T nào trong khoảng quét đạt đồng thời cả hai chỉ tiêu.**\n")

    L.append("## 4. Phân rã chu kỳ toàn hệ thống\n")
    L.append("| Thành phần | Giá trị | Nguồn |")
    L.append("| --- | --- | --- |")
    if best:
        L.append(f"| Chuyển động 3 đoạn | 3T = {fmt(best['cycle_motion_s'],3)} s "
                 f"(T = {fmt(best['T_s'],2)} s) | mô phỏng này (mục 3) |")
    else:
        L.append("| Chuyển động 3 đoạn | 3T | mô phỏng này (mục 3) |")
    L.append(f"| Kẹp + thả | 2 × {fmt(dwell,2)} = {fmt(2*dwell,2)} s | "
             "`tai-lieu/tong-quan.md` 7.1 (0,2–0,3 s) |")
    L.append(f"| Xử lý ảnh | {fmt(vm['mean'],2)} ms trung bình / {fmt(vm['p95'],2)} ms P95 | "
             "`runs/2026-11-18-thi-giac-hsv/output/metrics.json` → `timing_ms` "
             f"({vm['n_samples']} mẫu) |")
    L.append(f"| Chờ khung hình camera | {fmt(wc['frame_time_ms']['mean'],2)} ms trung bình / "
             f"{fmt(wc['frame_time_ms']['p95'],2)} ms P95 | cùng nguồn `output/webcam_info.json` "
             f"(`frame_time_ms`, webcam thật {fmt(wc['fps'],1)} fps) |")
    L.append(f"| Truyền Serial + phản hồi | ~{fmt(b['serial_ms'],1)} ms | "
             "**dry-run, CHƯA ĐO THẬT** |")
    L.append("| Đồng bộ/gia công thêm | (để trống) | chưa có số đo |")

    def total_rows(mode: str) -> Optional[float]:
        if best is None:
            return None
        if mode == "nominal":
            t_img = vm["mean"] / 1000.0
            t_cam = wc["frame_time_ms"]["mean"] / 1000.0
        else:
            t_img = vm["p95"] / 1000.0
            t_cam = wc["frame_time_ms"]["p95"] / 1000.0
        return best["cycle_with_dwell_s"] + t_img + t_cam + b["serial_ms"] / 1000.0

    tot_nom = total_rows("nominal")
    tot_p95 = total_rows("p95")
    if tot_nom is not None:
        L.append("")
        L.append(f"- Tổng danh định = {fmt(best['cycle_with_dwell_s'],3)} + "
                 f"{fmt(vm['mean'],2)} ms + {fmt(wc['frame_time_ms']['mean'],2)} ms + "
                 f"{fmt(b['serial_ms'],1)} ms = **{fmt(tot_nom,3)} s**.")
        L.append(f"- Tổng theo P95 (xử lý ảnh {fmt(vm['p95'],2)} ms, chờ khung "
                 f"{fmt(wc['frame_time_ms']['p95'],2)} ms) = **{fmt(tot_p95,3)} s**.")
        L.append(f"- Ngân sách: **{fmt(crit['total_cycle_target_s'],1)} s** → "
                 f"{'ĐẠT' if tot_nom <= crit['total_cycle_target_s'] else 'KHÔNG ĐẠT'} "
                 f"(danh định), dư {fmt(crit['total_cycle_target_s']-tot_nom,3)} s; "
                 f"{'ĐẠT' if tot_p95 <= crit['total_cycle_target_s'] else 'KHÔNG ĐẠT'} theo P95.")
    L.append("")

    L.append("## 5. Kết luận trung thực: 1,5 s thuần có khả thi trong ngân sách 1,8 s?\n")
    overhead_s = (vm["mean"] + wc["frame_time_ms"]["mean"] + b["serial_ms"]) / 1000.0
    motion_budget = crit["total_cycle_target_s"] - 2.0 * dwell - overhead_s
    T_allow = motion_budget / 3.0
    L.append(f"- Ngân sách cho chuyển động = 1,8 s − 2×{fmt(dwell,2)} s (dwell) − "
             f"{fmt(overhead_s,3)} s (thị giác {fmt(vm['mean'],2)} ms + chờ khung "
             f"{fmt(wc['frame_time_ms']['mean'],2)} ms + Serial {fmt(b['serial_ms'],1)} ms) "
             f"= **{fmt(motion_budget,3)} s** → T ≤ **{fmt(T_allow,3)} s**.")
    if best:
        pure_best = best["cycle_motion_s"]
        L.append(f"- Quét được T nhỏ nhất đạt 1 mm / 5 % **và không vi phạm giới hạn vật lý** "
                 f"là **{fmt(best['T_s'],2)} s** (3T = {fmt(pure_best,2)} s).")
        L.append(f"- Mốc “1,5 s thuần” nghĩa là T = 0,50 s → chu kỳ có dwell = 2,00 s, cộng "
                 f"overhead {fmt(overhead_s,3)} s thành **{fmt(2.0+overhead_s,3)} s**, "
                 f"vượt ngân sách 1,8 s. Vì vậy **1,5 s thuần KHÔNG khả thi trong ngân sách "
                 f"1,8 s** khi vẫn giữ dwell 0,25 s.")
        if best["T_s"] <= T_allow + 1e-9:
            L.append(f"- Tuy nhiên ngân sách không đòi hỏi phải chậm đến 1,5 s: T = "
                     f"{fmt(best['T_s'],2)} s vẫn đạt chỉ tiêu, cho tổng danh định "
                     f"**{fmt(tot_nom,3)} s ≤ 1,8 s** (dư {fmt(crit['total_cycle_target_s']-tot_nom,3)} s). "
                     "Kết luận đúng là: **1,5 s là quá chậm so với ngân sách, còn nhanh hơn "
                     f"({fmt(pure_best,2)} s thuần) lại vừa đủ chặt** — nên chốt mục tiêu chuyển động "
                     f"theo T = {fmt(best['T_s'],2)} s, không phải 0,5 s.")
        else:
            L.append(f"- Nhưng T = {fmt(best['T_s'],2)} s > T cho phép {fmt(T_allow,3)} s, nên "
                     f"phương án đạt chỉ tiêu vẫn vượt ngân sách: tổng {fmt(tot_nom,3)} s > 1,8 s. "
                     "**Không có phương án nào đồng thời đạt 1 mm/5 % và 1,8 s** với dwell 0,25 s.")
    else:
        L.append("- Không có T nào trong khoảng quét đạt 1 mm / 5 %, nên câu hỏi 1,5 s thuần "
                 "chưa thể trả lời là khả thi. Cần nới chỉ tiêu hoặc đổi cấu trúc điều khiển.")
    L.append(f"- Điều kiện để 1,5 s thuần khả thi: giảm dwell xuống ≤ "
             f"{fmt(max(0.0, (crit['total_cycle_target_s']-1.5-overhead_s)/2.0),3)} s mỗi pha "
             "(tức gần như bỏ thời gian kẹp/thả) hoặc tăng tốc độ phần cứng; cả hai đều là thay "
             "đổi giả thiết, không phải tinh chỉnh PID.")
    L.append("")

    L.append("## 6. Dị thường và lưu ý (bắt buộc đọc)\n")
    L.append(f"1. **Thời gian chạy bất thường: {elapsed_s:.0f} s cho 23 lần mô phỏng.** Đã chẩn đoán "
             "bằng `chan-doan-toc-do.py`: cùng một cấu hình T = 0,30 s, **bật** lượng tử hoá "
             "encoder (4096 xung/vòng) mất **20,24 s**, **tắt** chỉ mất **0,49 s** (chênh 41 lần). "
             "Nguyên nhân: phản hồi lượng tử hoá tạo bậc nhảy ở mỗi xung, RK45 phải giảm bước để "
             "bám các điểm gián đoạn. Đây là chi phí của mô hình, không phải lỗi kết quả, nhưng "
             "lần sau nên chạy với `quantize_feedback=false` rồi cộng sai số lượng tử riêng.")
    L.append(f"2. **Sai số 0,12–0,17 mm là do lượng tử hoá, không do động học.** Với cùng T = 0,30 s, "
             "tắt lượng tử hoá cho RMSE 0,0001 mm so với 0,0813 mm khi bật; τ_max gần như không đổi "
             "(1,016 so với 1,065 N·m). Nghĩa là chỉ tiêu 1 mm hiện do **độ phân giải encoder** "
             "quyết định, và mọi kết luận “đạt 1 mm” phải đọc kèm giả thiết 4096 xung/vòng.")
    L.append(f"3. **Số 46 ms trong đề bài không khớp nguồn.** `webcam_info.json` ghi frame time "
             f"trung bình **{fmt(wc['frame_time_ms']['mean'],2)} ms**, P95 **{fmt(wc['frame_time_ms']['p95'],2)} ms** "
             f"({fmt(wc['fps'],1)} fps). Bảng trên dùng số đo thật trong file; nếu ai trích 46 ms "
             "thì phải đo lại và cập nhật nguồn.")
    L.append(f"4. **P95 xử lý ảnh lệch giữa hai file:** `metrics.json` ghi {fmt(vm['p95'],2)} ms, "
             "`KETQUA.md` của run thị giác ghi 4,27 ms. Báo cáo này dùng `metrics.json` "
             "(nguồn máy đọc được); cần thống nhất lại.")
    L.append(f"5. **Serial ~{fmt(b['serial_ms'],1)} ms là dry-run, chưa đo thật.** Nếu UART 115200 "
             "và phản hồi 2 chiều, con số thực thường 2–10 ms; cần đo trước khi chốt chu kỳ.")
    L.append("6. Không có số đo thực nghiệm cho dwell; 0,25 s là giá trị danh định giữa dải "
             "0,2–0,3 s. Nếu xy-lanh khí nén chậm hơn, toàn bộ kết luận chu kỳ dịch tương ứng.")
    L.append("7. Mô hình vẫn bỏ qua tương tác chéo 3 khớp, trọng lực và ma sát Coulomb; "
             "τ_max/ω_max là tham số giả định, chưa chốt theo BOM. Bước quét 0,02 s chưa đủ mịn "
             "để chốt biên T; nên quét 0,005 s quanh 0,22–0,24 s.")
    L.append("8. `t_eval` bước 1 ms nên thời gian xác lập chỉ phân giải tới 1 ms; các giá trị 0 s "
             "là giới hạn của lưới, không phải số đo liên tục.")
    L.append("")
    L.append("## 7. Tệp đầu ra\n")
    L.append("- `output/metrics.json`: metric tại T mặc định (PID vs PID+FF) + toàn bộ quét.")
    L.append("- `output/quet-chu-ky.csv`: bảng quét T (đơn vị ghi trong header).")
    L.append("- `output/PID_plus_FF.csv`, `output/PID_thuan.csv`: dữ liệu thô theo thời gian.")
    L.append("- `figures/sai_so_va_dwell.png`: sai số bám + vùng dwell + thành phần vượt lố.")
    L.append("- `figures/quet_chu_ky.png`: quét chu kỳ và phương án đạt chỉ tiêu.")
    L.append("")
    L.append("![Sai số và dwell](figures/sai_so_va_dwell.png)\n")
    L.append("![Quét chu kỳ](figures/quet_chu_ky.png)\n")

    with open(RUN_DIR / "KETQUA.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# -----------------------------------------------------------------------------
# Che do tai su dung: chi ve lai hinh + bao cao tu output da co (khong mo phong lai)
# -----------------------------------------------------------------------------
def load_csv_result(path: Path) -> Dict[str, Any]:
    d = np.loadtxt(path, delimiter=",", skiprows=1)
    return {"t": d[:, 0], "p_ref": d[:, 1:4], "p_actual": d[:, 4:7], "err_mm": d[:, 7]}


def reuse_mode() -> None:
    cfg = load_config(CONFIG_PATH)
    with open(OUTPUT_DIR / "metrics.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = data["scan"]
    T_best = data["min_T_pass"]["T_s"]
    waypoints = np.array([cfg["waypoints_mm"]["home"], cfg["waypoints_mm"]["pick"],
                          cfg["waypoints_mm"]["place"], cfg["waypoints_mm"]["home"]], dtype=float)
    traj = DwellQuinticTrajectory(waypoints, cfg["trajectory"]["T_default_s"],
                                  cfg["trajectory"]["dwell_s"])
    pid = {"label": "PID_thuan", "metrics": data["main_comparison"]["PID_thuan"],
           "result": load_csv_result(OUTPUT_DIR / "PID_thuan.csv")}
    ff = {"label": "PID_plus_FF", "metrics": data["main_comparison"]["PID_plus_FF"],
          "result": load_csv_result(OUTPUT_DIR / "PID_plus_FF.csv")}

    plot_error(cfg, {"result": ff["result"], "traj": traj}, pid)
    plot_scan(cfg, rows, T_best)
    export_scan_csv(rows)
    write_report(cfg, pid, ff, rows, T_best, read_budget_sources(), data["runtime_s"])
    print("Da ve lai hinh va KETQUA.md tu output/metrics.json (--reuse).")


# -----------------------------------------------------------------------------
def main() -> None:
    t_start = time.perf_counter()
    cfg = load_config(CONFIG_PATH)
    set_seed(cfg["seed"])
    tr = cfg["trajectory"]
    dwell = tr["dwell_s"]

    waypoints = np.array([cfg["waypoints_mm"]["home"], cfg["waypoints_mm"]["pick"],
                          cfg["waypoints_mm"]["place"], cfg["waypoints_mm"]["home"]], dtype=float)

    print("=== 1. T mac dinh: PID thuan vs PID+FF ===")
    main_pid = run_configuration(cfg, waypoints, tr["T_default_s"], dwell, False, "PID_thuan")
    main_ff = run_configuration(cfg, waypoints, tr["T_default_s"], dwell, True, "PID_plus_FF")
    for r in (main_pid, main_ff):
        m = r["metrics"]
        print(f"  {r['label']}: cycle={m['cycle_s']:.3f}s RMSE={m['rmse_err_mm']:.4f}mm "
              f"over={m['overshoot_pick_pct']:.2f}/{m['overshoot_place_pct']:.2f}% "
              f"err_end={m['err_pick_end_dwell_mm']:.4f}/{m['err_place_end_dwell_mm']:.4f}mm "
              f"ts={m['settling_pick_rel_s']}/{m['settling_place_rel_s']}")

    print("=== 2. Quet chu ky ===")
    rows = scan_period(cfg, waypoints)
    ok_rows = [r for r in rows if r["pass"]]
    best = min(ok_rows, key=lambda r: r["T_s"]) if ok_rows else None
    T_best = best["T_s"] if best else None
    print(f"  => T nho nhat dat: {T_best}")

    print("=== 3. Doc nguon ngan sach, xuat file, ve hinh ===")
    src = read_budget_sources()
    export_trajectory_csv(main_pid)
    export_trajectory_csv(main_ff)
    export_scan_csv(rows)

    metrics = {
        "run_name": cfg["run_name"],
        "seed": cfg["seed"],
        "dwell_s": dwell,
        "metric_definition": {
            "overshoot": "max(0, max_{t in dwell} (p(t)-target).u_hat), u_hat=(target-prev_wp)/|.|",
            "settling": "first t in dwell with |p-target|<=1mm and stays <=1mm to end of dwell",
            "window_s": "[t_arrival, t_arrival+dwell]",
        },
        "main_comparison": {"PID_thuan": main_pid["metrics"],
                            "PID_plus_FF": main_ff["metrics"]},
        "scan": rows,
        "min_T_pass": {"T_s": T_best,
                       "cycle_motion_s": None if best is None else best["cycle_motion_s"],
                       "cycle_with_dwell_s": None if best is None else best["cycle_with_dwell_s"],
                       "metrics": best},
        "budget_sources": {
            "vision_timing_ms": src["vision_timing"],
            "webcam_frame_time_ms": src["webcam"]["frame_time_ms"],
            "webcam_fps": src["webcam"]["fps"],
            "serial_ms": cfg["budget_ngoai_mo_phong"]["serial_ms"],
            "serial_status": cfg["budget_ngoai_mo_phong"]["serial_status"],
        },
        "runtime_s": time.perf_counter() - t_start,
    }
    with open(OUTPUT_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    plot_error(cfg, main_ff, main_pid)
    plot_scan(cfg, rows, T_best)
    write_report(cfg, main_pid, main_ff, rows, T_best, src, time.perf_counter() - t_start)
    print(f"=== Hoan thanh sau {time.perf_counter()-t_start:.1f} s ===")


if __name__ == "__main__":
    if "--reuse" in sys.argv:
        reuse_mode()
    else:
        main()
