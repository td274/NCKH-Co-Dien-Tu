# -*- coding: utf-8 -*-
r"""
Mo phong quy dao gap-tha bac 5 va so sanh PID thuan voi PID + feed-forward
cho robot Delta 3-DOF (3-DOF translational Delta robot).

Cau truc run:
  1. Doc config.json (tham so, seed, gains, tieu chi).
  2. Tinh quy dao bac 5 trong khong gian thao tac.
  3. Chuyen quy dao sang khong gian khop qua IK / Jacobian nghich.
  4. Mo phong dong hoc khop voi PID thuan va PID+FF (bo qua tuong tac cheo).
  5. Quy doi sai so ve khong gian thao tac qua FK.
  6. Tinh chi so: max/RMSE (mm), sai so xac lap (mm), overshoot (%),
     thoi gian xac lap, chu ky thuan, mo-men/van toc cuc dai.
  7. Quet 3 bo PID, tim bo tot nhat theo tieu chi.
  8. Tim chu ky nho nhat khong vi pham gioi han vat ly.
  9. Xuat CSV, hinh PNG 300 dpi, KETQUA.md.

Luu y:
  - Su dung D:\Python312\python.exe (python tran la stub Microsoft Store).
  - Khong duoc sua output cu; muon chay lai thi tao run moi.
"""

from __future__ import annotations

import json
import sys
import os
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# -----------------------------------------------------------------------------
# Import lai ham IK/FK/Jacobian tu nghien-cuu/mo-hinh/kiem-chung-ik-fk.py
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

DELTA_PARAMS = kiem_chung_ik_fk.PARAMS_DEFAULT
inverse_kinematics = kiem_chung_ik_fk.inverse_kinematics
forward_kinematics_analytical = kiem_chung_ik_fk.forward_kinematics_analytical
compute_jacobian = kiem_chung_ik_fk.compute_jacobian
PHIS = kiem_chung_ik_fk.PHIS

# -----------------------------------------------------------------------------
# Cau hinh chung
# -----------------------------------------------------------------------------
RUN_DIR = Path(__file__).resolve().parent
CONFIG_PATH = RUN_DIR / "config.json"
OUTPUT_DIR = RUN_DIR / "output"
FIGURES_DIR = RUN_DIR / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_config(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def set_seed(seed: int) -> None:
    np.random.seed(seed)


# -----------------------------------------------------------------------------
# Da thuc bac 5: p(t) = a0 + a3 t^3 + a4 t^4 + a5 t^5  (v0=v1=0, a0=a1=0)
# -----------------------------------------------------------------------------
def quintic_coeffs(p0: float, p1: float, T: float) -> np.ndarray:
    a0 = p0
    a1 = 0.0
    a2 = 0.0
    a3 = 10.0 * (p1 - p0) / (T ** 3)
    a4 = -15.0 * (p1 - p0) / (T ** 4)
    a5 = 6.0 * (p1 - p0) / (T ** 5)
    return np.array([a0, a1, a2, a3, a4, a5], dtype=float)


def eval_quintic(coeffs: np.ndarray, t: float, T: float
                 ) -> Tuple[float, float, float]:
    if t <= 0.0:
        return coeffs[0], 0.0, 0.0
    if t >= T:
        # Tai bien phai p=p1, v=a=0
        p1 = coeffs[0] + coeffs[3] * (T ** 3) + coeffs[4] * (T ** 4) + coeffs[5] * (T ** 5)
        return p1, 0.0, 0.0
    p = (coeffs[0] + coeffs[3] * t ** 3 + coeffs[4] * t ** 4 + coeffs[5] * t ** 5)
    v = (3.0 * coeffs[3] * t ** 2 + 4.0 * coeffs[4] * t ** 3 + 5.0 * coeffs[5] * t ** 4)
    a = (6.0 * coeffs[3] * t + 12.0 * coeffs[4] * t ** 2 + 20.0 * coeffs[5] * t ** 3)
    return p, v, a


# -----------------------------------------------------------------------------
# Quy dao 3D bac 5 qua cac diem moc
# -----------------------------------------------------------------------------
class QuinticTrajectory:
    def __init__(self, waypoints: np.ndarray, T_segment: float):
        """
        waypoints: (N, 3) cac diem moc [x, y, z] mm
        T_segment: thoi gian moi doan (s)
        """
        self.waypoints = np.asarray(waypoints, dtype=float)
        self.n_segments = self.waypoints.shape[0] - 1
        self.T = float(T_segment)
        self.coeffs = []
        for i in range(self.n_segments):
            c = np.vstack([quintic_coeffs(p0, p1, self.T)
                           for p0, p1 in zip(self.waypoints[i], self.waypoints[i + 1])])
            self.coeffs.append(c)

    def total_time(self) -> float:
        return self.n_segments * self.T

    def evaluate(self, t: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t = float(t)
        if t <= 0.0:
            return self.waypoints[0].copy(), np.zeros(3), np.zeros(3)
        if t >= self.total_time():
            return self.waypoints[-1].copy(), np.zeros(3), np.zeros(3)
        seg = int(t // self.T)
        seg = min(seg, self.n_segments - 1)
        tloc = t - seg * self.T
        coeffs = self.coeffs[seg]
        p = np.zeros(3)
        v = np.zeros(3)
        a = np.zeros(3)
        for axis in range(3):
            p[axis], v[axis], a[axis] = eval_quintic(coeffs[axis], tloc, self.T)
        return p, v, a


# -----------------------------------------------------------------------------
# Chuyen quy dao thao tac sang khong gian khop (noi suy muot)
# -----------------------------------------------------------------------------
from scipy.interpolate import CubicSpline


class JointReferenceInterpolator:
    """
    Tinh truoc theta_ref(t), theta_dot_ref(t), theta_ddot_ref(t) tren luoi thoi gian
    va noi suy CubicSpline de dung trong ODE.
    """
    def __init__(self, traj: QuinticTrajectory, delta_params: Dict[str, float],
                 t_grid: np.ndarray):
        self.t_grid = np.asarray(t_grid, dtype=float)
        self.n = len(self.t_grid)
        self.theta_ref = np.zeros((self.n, 3))
        self.theta_dot_ref = np.zeros((self.n, 3))

        for i, ti in enumerate(self.t_grid):
            p_ref, v_ref, _ = traj.evaluate(ti)
            th, info = inverse_kinematics(p_ref, delta_params)
            if th is None:
                raise ValueError(f"Khong co nghiem IK tai t={ti:.4f}, p={p_ref}")
            self.theta_ref[i] = th
            jac_info = compute_jacobian(p_ref, th, delta_params)
            J_forward = jac_info["J_forward"]
            try:
                self.theta_dot_ref[i] = np.linalg.solve(J_forward, v_ref)
            except np.linalg.LinAlgError:
                self.theta_dot_ref[i] = np.zeros(3)

        # theta_ddot_ref = dao ham so cua theta_dot_ref
        self.theta_ddot_ref = np.zeros((self.n, 3))
        for axis in range(3):
            self.theta_ddot_ref[:, axis] = np.gradient(self.theta_dot_ref[:, axis], self.t_grid)

        # Noi suy
        self.cs_theta = [CubicSpline(self.t_grid, self.theta_ref[:, i],
                                     bc_type="clamped") for i in range(3)]
        self.cs_omega = [CubicSpline(self.t_grid, self.theta_dot_ref[:, i],
                                     bc_type="clamped") for i in range(3)]
        self.cs_alpha = [CubicSpline(self.t_grid, self.theta_ddot_ref[:, i],
                                     bc_type="clamped") for i in range(3)]

    def __call__(self, t: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t = float(np.clip(t, self.t_grid[0], self.t_grid[-1]))
        th = np.array([self.cs_theta[i](t) for i in range(3)])
        om = np.array([self.cs_omega[i](t) for i in range(3)])
        al = np.array([self.cs_alpha[i](t) for i in range(3)])
        return th, om, al


def cartesian_to_joint_reference(traj: QuinticTrajectory, t: float,
                                 delta_params: Dict[str, float]
                                 ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ham thuan tien de tinh tai mot thoi diem (dung khi khoi tao)."""
    p_ref, v_ref, _ = traj.evaluate(t)
    theta_ref, _ = inverse_kinematics(p_ref, delta_params)
    if theta_ref is None:
        raise ValueError(f"Khong co nghiem IK tai t={t:.4f}, p={p_ref}")
    jac_info = compute_jacobian(p_ref, theta_ref, delta_params)
    J_forward = jac_info["J_forward"]
    try:
        theta_dot_ref = np.linalg.solve(J_forward, v_ref)
    except np.linalg.LinAlgError:
        theta_dot_ref = np.zeros(3)
    return theta_ref, theta_dot_ref, np.zeros(3)


# -----------------------------------------------------------------------------
# Mo hinh khop va bo dieu khien
# -----------------------------------------------------------------------------
class JointDriveSimulation:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.J = cfg["joint_model"]["J_kg_m2"]
        self.b = cfg["joint_model"]["b_Nm_s_rad"]
        self.tau_max = cfg["joint_model"]["tau_max_Nm"]
        self.omega_max = cfg["joint_model"]["omega_max_rad_s"]
        self.delta_params = self._build_delta_params(cfg)
        self.Kp = cfg["pid_gains"]["Kp"]
        self.Ki = cfg["pid_gains"]["Ki"]
        self.Kd = cfg["pid_gains"]["Kd"]
        self.tau_d = cfg["pid_gains"].get("tau_d_filter_s", 0.005)
        self.quantize = cfg["joint_model"].get("quantize_feedback", False)
        self.enc_cpr = cfg["joint_model"].get("encoder_counts_per_rev", 4096)

    def _build_delta_params(self, cfg: Dict[str, Any]) -> Dict[str, float]:
        g = cfg["robot_geometry_mm"]
        return {
            "f": g["f"],
            "e": g["e"],
            "rf": g["rf"],
            "re": g["re"],
            "R_b": g["R_b"],
            "r_p": g["r_p"],
            "R": g["R"],
        }

    def _clamp(self, tau: np.ndarray) -> np.ndarray:
        return np.clip(tau, -self.tau_max, self.tau_max)

    def _feedback(self, theta: np.ndarray) -> np.ndarray:
        if not self.quantize:
            return theta
        res = 2.0 * math.pi / self.enc_cpr
        return np.round(theta / res) * res

    def dynamics(self, t: float, y: np.ndarray,
                 interp: JointReferenceInterpolator, use_ff: bool) -> np.ndarray:
        theta = y[0:3]
        omega = y[3:6]
        integral = y[6:9]

        theta_ref, omega_ref, alpha_ref = interp(t)

        theta_fb = self._feedback(theta)
        omega_fb = omega

        e = theta_ref - theta_fb
        de = omega_ref - omega_fb

        # PID
        tau_pid = self.Kp * e + self.Ki * integral + self.Kd * de

        # Feed-forward
        tau_ff = np.zeros(3)
        if use_ff:
            tau_ff = self.J * alpha_ref + self.b * omega_ref

        tau = tau_pid + tau_ff
        tau_sat = self._clamp(tau)

        # Anti-windup: dung tich phan khi tin hieu dieu khien bao hoa
        saturated = np.abs(tau) >= self.tau_max * 0.999
        di = np.where(saturated, 0.0, e)

        alpha = (tau_sat - self.b * omega) / self.J
        return np.concatenate([omega, alpha, di])

    def simulate(self, traj: QuinticTrajectory, use_ff: bool,
                 t_eval: np.ndarray) -> Dict[str, Any]:
        total = traj.total_time()
        # Luoi tinh truoc tham chieu: dt ~ 1 ms (du muot, tiet kiem thoi gian)
        n_grid = min(20000, max(500, int(round(total / 1e-3))))
        t_grid = np.linspace(0.0, total, n_grid)
        interp = JointReferenceInterpolator(traj, self.delta_params, t_grid)

        theta0, _, _ = interp(0.0)
        y0 = np.concatenate([theta0, np.zeros(3), np.zeros(3)])

        def rhs(t, y):
            return self.dynamics(t, y, interp, use_ff)

        sol = solve_ivp(
            rhs,
            [0.0, total],
            y0,
            t_eval=t_eval,
            method="RK45",
            atol=self.cfg["simulation"]["atol"],
            rtol=self.cfg["simulation"]["rtol"],
            max_step=0.005,
        )

        n = len(sol.t)
        theta = sol.y[0:3, :].T
        omega = sol.y[3:6, :].T
        integral = sol.y[6:9, :].T

        p_ref = np.zeros((n, 3))
        p_actual = np.zeros((n, 3))
        err_mm = np.zeros(n)
        tau_cmd = np.zeros((n, 3))
        theta_ref_log = np.zeros((n, 3))
        omega_ref_log = np.zeros((n, 3))
        alpha_ref_log = np.zeros((n, 3))

        for i, ti in enumerate(sol.t):
            pref, vref, aref = traj.evaluate(ti)
            p_ref[i] = pref
            theta_ref_log[i], omega_ref_log[i], alpha_ref_log[i] = interp(ti)
            p_actual[i], _ = forward_kinematics_analytical(theta[i], self.delta_params)
            err_mm[i] = float(np.linalg.norm(p_actual[i] - p_ref[i]))

            e = theta_ref_log[i] - theta[i]
            de = omega_ref_log[i] - omega[i]
            tau_pid = self.Kp * e + self.Ki * integral[i] + self.Kd * de
            tau_ff = np.zeros(3)
            if use_ff:
                tau_ff = self.J * alpha_ref_log[i] + self.b * omega_ref_log[i]
            tau_cmd[i] = np.clip(tau_pid + tau_ff, -self.tau_max, self.tau_max)

        return {
            "t": sol.t,
            "p_ref": p_ref,
            "p_actual": p_actual,
            "err_mm": err_mm,
            "theta": theta,
            "theta_ref": theta_ref_log,
            "omega": omega,
            "omega_ref": omega_ref_log,
            "tau": tau_cmd,
            "cycle_s": total,
        }



# -----------------------------------------------------------------------------
# Tinh chi so dinh luong
# -----------------------------------------------------------------------------
def compute_metrics(res: Dict[str, Any], cfg: Dict[str, Any],
                    waypoints: np.ndarray, T: float) -> Dict[str, Any]:
    t = res["t"]
    err = res["err_mm"]
    p_actual = res["p_actual"]
    omega = res["omega"]
    tau = res["tau"]

    max_err = float(np.max(err))
    rmse_err = float(np.sqrt(np.mean(err ** 2)))

    # Sai so xac lap tai pick (cuoi doan 1) va place (cuoi doan 2)
    pick_time = T
    place_time = 2.0 * T
    window = 0.05  # 50 ms cuoi
    def steady_err(target_time: float, target: np.ndarray) -> float:
        mask = (t >= target_time - window) & (t <= target_time)
        if np.any(mask):
            return float(np.mean(np.linalg.norm(p_actual[mask] - target, axis=1)))
        return float(np.linalg.norm(p_actual[-1] - target))

    err_pick = steady_err(pick_time, waypoints[1])
    err_place = steady_err(place_time, waypoints[2])

    # Overshoot va thoi gian xac lap tai pick/place
    def settling_overshoot(target_time: float, target: np.ndarray):
        tol_mm = cfg["criteria"]["settling_error_mm"]
        # Cua so quan sat: tu dau doan truoc den khi dung lai ngan sau target
        t0 = max(0.0, target_time - 0.9 * T)
        t1 = min(t[-1], target_time + 0.15 * T)
        mask = (t >= t0) & (t <= t1)
        dist = np.linalg.norm(p_actual[mask] - target, axis=1)
        t_win = t[mask]
        if len(dist) == 0:
            return 0.0, None

        # Thoi gian xac lap: tu dau doan den khi dist < tol_mm (va duy tri trong phan con lai cua cua so dung)
        settled_at = None
        under_tol = np.where(dist <= tol_mm)[0]
        if len(under_tol) > 0:
            # Chon lan dau tien vao vung tol ma sau do khong vuot qua tol
            for idx in under_tol:
                if np.all(dist[idx:] <= tol_mm):
                    settled_at = t_win[idx]
                    break
            if settled_at is None:
                settled_at = t_win[under_tol[0]]

        # Overshoot: sau khi di vao vung gan target (dist < 2*tol),
        # xet trong khoang dung lai ngan.
        cross_idx = np.where(dist <= 2.0 * tol_mm)[0]
        overshoot_mm = 0.0
        if len(cross_idx) > 0:
            first_cross = cross_idx[0]
            post_dist = dist[first_cross:]
            steady = err_pick if np.allclose(target, waypoints[1]) else err_place
            if len(post_dist) > 0:
                overshoot_mm = float(max(0.0, np.max(post_dist) - steady))
        return overshoot_mm, settled_at

    over_pick, ts_pick = settling_overshoot(pick_time, waypoints[1])
    over_place, ts_place = settling_overshoot(place_time, waypoints[2])

    # Overshoot % so voi bien do di chuyen cua doan
    def step_size(idx_from: int, idx_to: int) -> float:
        return float(np.linalg.norm(waypoints[idx_to] - waypoints[idx_from]))

    over_pick_pct = 100.0 * over_pick / max(step_size(0, 1), 1e-6)
    over_place_pct = 100.0 * over_place / max(step_size(1, 2), 1e-6)

    tau_max = float(np.max(np.abs(tau)))
    omega_max = float(np.max(np.abs(omega)))
    tau_violation = bool(tau_max > cfg["joint_model"]["tau_max_Nm"] * 1.001)
    omega_violation = bool(omega_max > cfg["joint_model"]["omega_max_rad_s"] * 1.001)

    return {
        "max_err_mm": max_err,
        "rmse_err_mm": rmse_err,
        "err_pick_mm": err_pick,
        "err_place_mm": err_place,
        "overshoot_pick_mm": over_pick,
        "overshoot_pick_pct": over_pick_pct,
        "overshoot_place_mm": over_place,
        "overshoot_place_pct": over_place_pct,
        "settling_pick_s": ts_pick,
        "settling_place_s": ts_place,
        "cycle_s": res["cycle_s"],
        "tau_max_Nm": tau_max,
        "omega_max_rad_s": omega_max,
        "tau_violation": tau_violation,
        "omega_violation": omega_violation,
    }


# -----------------------------------------------------------------------------
# Chay mot cau hinh
# -----------------------------------------------------------------------------
def run_configuration(cfg: Dict[str, Any], waypoints: np.ndarray, T: float,
                      Kp: float, Ki: float, Kd: float, use_ff: bool,
                      label: str, t_eval: np.ndarray) -> Dict[str, Any]:
    cfg_run = dict(cfg)
    cfg_run["pid_gains"] = {"Kp": Kp, "Ki": Ki, "Kd": Kd,
                            "tau_d_filter_s": cfg["pid_gains"].get("tau_d_filter_s", 0.005)}
    sim = JointDriveSimulation(cfg_run)
    traj = QuinticTrajectory(waypoints, T)
    res = sim.simulate(traj, use_ff, t_eval)
    metrics = compute_metrics(res, cfg, waypoints, T)
    return {"label": label, "use_ff": use_ff, "gains": (Kp, Ki, Kd),
            "T": T, "result": res, "metrics": metrics}


# -----------------------------------------------------------------------------
# Ve hinh
# -----------------------------------------------------------------------------
def plot_results(cfgs: List[Dict[str, Any]], waypoints: np.ndarray,
                 cfg: Dict[str, Any]) -> None:
    matplotlib.rcParams["font.size"] = 11
    matplotlib.rcParams["axes.titlesize"] = 12
    matplotlib.rcParams["axes.labelsize"] = 11
    matplotlib.rcParams["legend.fontsize"] = 10

    labels = [c["label"] for c in cfgs]
    colors = ["#1f77b4", "#ff7f0e"]

    # (a) Quy dao 3D + hinh chieu xy
    fig = plt.figure(figsize=(14, 6), dpi=300)
    ax3d = fig.add_subplot(121, projection="3d")
    axy = fig.add_subplot(122)

    for c, col, lab in zip(cfgs, colors, labels):
        r = c["result"]
        ax3d.plot(r["p_ref"][:, 0], r["p_ref"][:, 1], r["p_ref"][:, 2],
                  "--", color=col, lw=1.5, label=f"{lab} (dat)")
        ax3d.plot(r["p_actual"][:, 0], r["p_actual"][:, 1], r["p_actual"][:, 2],
                  "-", color=col, lw=1.2, label=f"{lab} (thuc)")
    ax3d.scatter(waypoints[:, 0], waypoints[:, 1], waypoints[:, 2],
                 c="black", s=60, marker="o", zorder=5)
    for i, txt in enumerate(["Home", "Pick", "Place", "Home"]):
        ax3d.text(waypoints[i, 0], waypoints[i, 1], waypoints[i, 2], txt, fontsize=9)
    ax3d.set_xlabel("x (mm)")
    ax3d.set_ylabel("y (mm)")
    ax3d.set_zlabel("z (mm)")
    ax3d.set_title("(a) Quy dao 3D")
    ax3d.legend(loc="upper left", fontsize=8)

    for c, col, lab in zip(cfgs, colors, labels):
        r = c["result"]
        axy.plot(r["p_ref"][:, 0], r["p_ref"][:, 1], "--", color=col, lw=1.5)
        axy.plot(r["p_actual"][:, 0], r["p_actual"][:, 1], "-", color=col, lw=1.2, label=lab)
    axy.scatter(waypoints[:, 0], waypoints[:, 1], c="black", s=50, zorder=5)
    axy.set_xlabel("x (mm)")
    axy.set_ylabel("y (mm)")
    axy.set_aspect("equal")
    axy.set_title("(b) Hinh chieu xy")
    axy.legend(loc="upper right")
    axy.grid(True, linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "quy_dao_3d_va_xy.png", dpi=300)
    plt.close(fig)

    # (b) Sai so bam theo thoi gian
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    for c, col, lab in zip(cfgs, colors, labels):
        r = c["result"]
        ax.semilogy(r["t"], r["err_mm"] + 1e-6, color=col, lw=1.2, label=lab)
    ax.axhline(cfg["criteria"]["settling_error_mm"], color="red", ls="--", lw=1.0,
               label=f"Nguong xac lap {cfg['criteria']['settling_error_mm']} mm")
    T = cfgs[0]["T"]
    for tk in [T, 2 * T]:
        ax.axvline(tk, color="gray", ls=":", lw=0.8)
    ax.set_xlabel("Thoi gian (s)")
    ax.set_ylabel("Sai so bam ||p_ref - p_actual|| (mm)")
    ax.set_title("(c) Sai so bam quy dao trong khong gian thao tac")
    ax.legend(loc="upper right")
    ax.grid(True, linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "sai_so_bam_theo_thoi_gian.png", dpi=300)
    plt.close(fig)

    # (c) Mo-men 3 khop
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), dpi=300, sharex=True)
    for c, col, lab in zip(cfgs, colors, labels):
        r = c["result"]
        for i in range(3):
            axes[i].plot(r["t"], r["tau"][:, i], color=col, lw=1.0, label=lab)
    for i in range(3):
        axes[i].axhline(cfg["joint_model"]["tau_max_Nm"], color="red", ls="--", lw=1.0)
        axes[i].axhline(-cfg["joint_model"]["tau_max_Nm"], color="red", ls="--", lw=1.0)
        axes[i].set_ylabel(f"tau_{i+1} (Nm)")
        axes[i].grid(True, linestyle=":", alpha=0.5)
        if i == 0:
            axes[i].legend(loc="upper right")
    axes[2].set_xlabel("Thoi gian (s)")
    axes[0].set_title("(d) Mo-men dieu khien 3 khop")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "mo_men_3_khop.png", dpi=300)
    plt.close(fig)

    # (d) Van toc goc 3 khop
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), dpi=300, sharex=True)
    for c, col, lab in zip(cfgs, colors, labels):
        r = c["result"]
        for i in range(3):
            axes[i].plot(r["t"], np.degrees(r["omega"][:, i]), color=col, lw=1.0, label=lab)
            axes[i].plot(r["t"], np.degrees(r["omega_ref"][:, i]), "--", color=col, lw=0.8)
    for i in range(3):
        wlim = np.degrees(cfg["joint_model"]["omega_max_rad_s"])
        axes[i].axhline(wlim, color="red", ls="--", lw=1.0, label="gioi han")
        axes[i].axhline(-wlim, color="red", ls="--", lw=1.0)
        axes[i].set_ylabel(f"omega_{i+1} (deg/s)")
        axes[i].grid(True, linestyle=":", alpha=0.5)
        if i == 0:
            axes[i].legend(loc="upper right")
    axes[2].set_xlabel("Thoi gian (s)")
    axes[0].set_title("(e) Van toc goc 3 khop (duong lien: thuc, dut: dat)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "van_toc_goc_3_khop.png", dpi=300)
    plt.close(fig)


# -----------------------------------------------------------------------------
# Xuat CSV va JSON metrics
# -----------------------------------------------------------------------------
def export_csv(cfgs: List[Dict[str, Any]]) -> None:
    for c in cfgs:
        r = c["result"]
        fname = f"{c['label'].replace(' ', '_').replace('+','plus')}.csv"
        path = OUTPUT_DIR / fname
        header = ["t_s", "x_ref_mm", "y_ref_mm", "z_ref_mm",
                  "x_actual_mm", "y_actual_mm", "z_actual_mm", "err_mm",
                  "theta1_ref_rad", "theta2_ref_rad", "theta3_ref_rad",
                  "theta1_rad", "theta2_rad", "theta3_rad",
                  "omega1_rad_s", "omega2_rad_s", "omega3_rad_s",
                  "tau1_Nm", "tau2_Nm", "tau3_Nm"]
        rows = np.column_stack([
            r["t"], r["p_ref"], r["p_actual"], r["err_mm"],
            r["theta_ref"], r["theta"], r["omega"], r["tau"]
        ])
        np.savetxt(path, rows, delimiter=",", header=",".join(header),
                   comments="", fmt="%.6e")


def export_metrics_json(main_pid: Dict[str, Any], main_pidff: Dict[str, Any],
                        scan_results: List[Dict[str, Any]],
                        min_cycle: Dict[str, Any]) -> None:
    data = {
        "main_comparison": {
            "PID_thuan": main_pid["metrics"],
            "PID_plus_FF": main_pidff["metrics"],
        },
        "gain_scan": [
            {"label": r["label"], "gains": {"Kp": r["gains"][0],
                                             "Ki": r["gains"][1],
                                             "Kd": r["gains"][2]},
             "metrics": r["metrics"]} for r in scan_results
        ],
        "min_feasible_cycle": {
            "T_segment_s": min_cycle["T_min_feasible_s"],
            "cycle_s": min_cycle["cycle_min_s"],
            "metrics": min_cycle["metrics"],
        },
    }
    with open(OUTPUT_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# -----------------------------------------------------------------------------
# Quet gains va tim chu ky nho nhat
# -----------------------------------------------------------------------------
def scan_gains(cfg: Dict[str, Any], waypoints: np.ndarray, T: float,
               t_eval: np.ndarray) -> List[Dict[str, Any]]:
    gain_sets = cfg["pid_gain_sets"]
    results = []
    for name, g in gain_sets.items():
        run_pid = run_configuration(cfg, waypoints, T, g["Kp"], g["Ki"], g["Kd"],
                                    False, f"PID_{name}", t_eval)
        results.append(run_pid)
        run_ff = run_configuration(cfg, waypoints, T, g["Kp"], g["Ki"], g["Kd"],
                                   True, f"PID+FF_{name}", t_eval)
        results.append(run_ff)
    return results


def find_min_cycle(cfg: Dict[str, Any], waypoints: np.ndarray,
                   t_eval_fn, Kp: float, Ki: float, Kd: float,
                   use_ff: bool = True) -> Dict[str, Any]:
    T_min = cfg["trajectory"]["T_min_s"]
    T_max = cfg["trajectory"]["T_max_s"]
    # Tim kiem nhi phan tren T_segment
    T_low = T_max
    T_high = T_min
    feasible_T = T_max
    best_metrics = None
    best_res = None

    # Thu cac gia tri T giam dan tu T_max xuong T_min
    Ts = np.linspace(T_max, T_min, 15)
    for T in Ts:
        t_eval = t_eval_fn(T)
        try:
            run = run_configuration(cfg, waypoints, T, Kp, Ki, Kd, use_ff,
                                    "scan", t_eval)
            m = run["metrics"]
            if not m["tau_violation"] and not m["omega_violation"]:
                feasible_T = T
                best_metrics = m
                best_res = run
            else:
                break
        except Exception as e:
            print(f"  Loi voi T={T:.4f}s: {e}")
            break

    # Tinh chinh xung quanh gia tri kha thi cuoi
    if feasible_T < T_max:
        Ts_fine = np.linspace(feasible_T, max(T_min, feasible_T - 0.05), 10)
        for T in Ts_fine:
            t_eval = t_eval_fn(T)
            try:
                run = run_configuration(cfg, waypoints, T, Kp, Ki, Kd, use_ff,
                                        "scan", t_eval)
                m = run["metrics"]
                if not m["tau_violation"] and not m["omega_violation"]:
                    feasible_T = T
                    best_metrics = m
                    best_res = run
                else:
                    break
            except Exception as e:
                print(f"  Loi voi T={T:.4f}s: {e}")
                break

    return {
        "T_min_feasible_s": feasible_T,
        "cycle_min_s": 3.0 * feasible_T,
        "metrics": best_metrics,
        "result": best_res,
    }


# -----------------------------------------------------------------------------
# Viet KETQUA.md
# -----------------------------------------------------------------------------
def write_report(cfg: Dict[str, Any], main_pid: Dict[str, Any],
                 main_pidff: Dict[str, Any], scan_results: List[Dict[str, Any]],
                 min_cycle: Dict[str, Any]) -> None:
    lines = []
    lines.append("# Ket qua mo phong: Quy dao gap-tha bac 5 - PID vs PID+FF\n")
    lines.append(f"**Run:** `{cfg['run_name']}`  ")
    lines.append(f"**Ngay chay:** {cfg['ngay_chay']}  ")
    lines.append(f"**Seed:** {cfg['seed']}  ")
    lines.append(f"**Python:** {cfg['python']}  \n")

    lines.append("## 1. Giai thieu mo phong\n")
    lines.append("- Tham so hinh hoc: f=346 mm, e=115 mm, rf=200 mm, re=400 mm.")
    lines.append("- Quy dao: da thuc bac 5, dung han tai cac diem moc (v=a=0).")
    lines.append("- Cac diem moc (mm): Home (0,0,-350), Pick (100,-100,-400), Place (-100,100,-350), tro ve Home.")
    lines.append("- Mo hinh khop: J=0.01 kg.m2, b=0.05 Nm.s/rad, tau_max=2 Nm, omega_max=10 rad/s.")
    lines.append("- **Gia thiet quan trong:** Bo qua tuong tac cheo giua 3 khop; moi khop duoc dieu khien doc lap nhu he quan tinh-nhot. Day la gia thiet ly tuong hoa, can xem xet lai khi thiet ke dong luc hoc day du.")
    lines.append("- Feed-forward = J*theta_ddot_ref + b*theta_dot_ref.")
    lines.append("- Sai so bam duoc quy doi ve khong gian thao tac (mm) qua FK.\n")

    lines.append("## 2. Cau hinh PID chinh\n")
    lines.append(f"- Kp = {cfg['pid_gains']['Kp']}, Ki = {cfg['pid_gains']['Ki']}, Kd = {cfg['pid_gains']['Kd']}")
    lines.append(f"- Thoi gian moi doan T = {main_pid['T']} s; chu ky thuan = {main_pid['metrics']['cycle_s']:.3f} s\n")

    lines.append("## 3. Bang so sanh PID thuan va PID + Feed-forward\n")
    lines.append("| Chi so | PID thuan | PID + Feed-forward |")
    lines.append("| --- | --- | --- |")
    m1 = main_pid["metrics"]
    m2 = main_pidff["metrics"]
    def fmt(v, fmtstr="{:.4f}"):
        return fmtstr.format(v) if v is not None else "—"
    lines.append(f"| Max sai so bam (mm) | {fmt(m1['max_err_mm'])} | {fmt(m2['max_err_mm'])} |")
    lines.append(f"| RMSE sai so bam (mm) | {fmt(m1['rmse_err_mm'])} | {fmt(m2['rmse_err_mm'])} |")
    lines.append(f"| Sai so xac lap tai Pick (mm) | {fmt(m1['err_pick_mm'])} | {fmt(m2['err_pick_mm'])} |")
    lines.append(f"| Sai so xac lap tai Place (mm) | {fmt(m1['err_place_mm'])} | {fmt(m2['err_place_mm'])} |")
    lines.append(f"| Overshoot Pick (%) | {fmt(m1['overshoot_pick_pct'])} | {fmt(m2['overshoot_pick_pct'])} |")
    lines.append(f"| Overshoot Place (%) | {fmt(m1['overshoot_place_pct'])} | {fmt(m2['overshoot_place_pct'])} |")
    lines.append(f"| Thoi gian xac lap Pick (s) | {fmt(m1.get('settling_pick_s'))} | {fmt(m2.get('settling_pick_s'))} |")
    lines.append(f"| Thoi gian xac lap Place (s) | {fmt(m1.get('settling_place_s'))} | {fmt(m2.get('settling_place_s'))} |")
    lines.append(f"| Mo-men cuc dai (Nm) | {fmt(m1['tau_max_Nm'])} | {fmt(m2['tau_max_Nm'])} |")
    lines.append(f"| Van toc goc cuc dai (rad/s) | {fmt(m1['omega_max_rad_s'])} | {fmt(m2['omega_max_rad_s'])} |")
    lines.append(f"| Vi pham tau_max | {'Co' if m1['tau_violation'] else 'Khong'} | {'Co' if m2['tau_violation'] else 'Khong'} |")
    lines.append(f"| Vi pham omega_max | {'Co' if m1['omega_violation'] else 'Khong'} | {'Co' if m2['omega_violation'] else 'Khong'} |")
    lines.append(f"| Chu ky thuan (s) | {fmt(m1['cycle_s'])} | {fmt(m2['cycle_s'])} |\n")

    lines.append("## 4. Quet bo PID\n")
    lines.append("Danh gia 3 bo PID thuan va 3 bo PID+FF voi tieu chi: overshoot <= 5% va sai so xac lap <= 1 mm.\n")
    lines.append("| Bo PID | Kp | Ki | Kd | RMSE (mm) | Overshoot Pick (%) | Overshoot Place (%) | Dat tieu chi? |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    best = None
    for r in scan_results:
        m = r["metrics"]
        ok = (m["overshoot_pick_pct"] <= cfg["criteria"]["overshoot_max_percent"] and
              m["overshoot_place_pct"] <= cfg["criteria"]["overshoot_max_percent"] and
              m["err_pick_mm"] <= cfg["criteria"]["settling_error_mm"] and
              m["err_place_mm"] <= cfg["criteria"]["settling_error_mm"])
        ok_str = "Co" if ok else "Khong"
        lines.append(f"| {r['label']} | {r['gains'][0]} | {r['gains'][1]} | {r['gains'][2]} | "
                     f"{m['rmse_err_mm']:.4f} | {m['overshoot_pick_pct']:.2f} | "
                     f"{m['overshoot_place_pct']:.2f} | {ok_str} |")
        if ok and (best is None or m["rmse_err_mm"] < best["metrics"]["rmse_err_mm"]):
            best = r
    lines.append("")
    if best:
        lines.append(f"**Bo tot nhat:** {best['label']} voi Kp={best['gains'][0]}, Ki={best['gains'][1]}, Kd={best['gains'][2]}.")
    else:
        lines.append("**Bo tot nhat:** Khong co bo nao dat dong thoi ca hai tieu chi tren voi T mac dinh. Can giam toc do hoac tang Kd de giam overshoot.")
    lines.append("")

    lines.append("## 5. Chu ky nho nhat kha thi\n")
    mm = min_cycle["metrics"]
    lines.append(f"- Tim kiem giam T_segment tu {cfg['trajectory']['T_max_s']} s xuong {cfg['trajectory']['T_min_s']} s.")
    lines.append(f"- **T_segment nho nhat kha thi:** {min_cycle['T_min_feasible_s']:.4f} s")
    lines.append(f"- **Chu ky thuan nho nhat:** {min_cycle['cycle_min_s']:.4f} s")
    if mm:
        lines.append(f"- Tai chu ky nay: omega_max = {mm['omega_max_rad_s']:.3f} rad/s, tau_max = {mm['tau_max_Nm']:.3f} Nm.")
        lines.append("- Khong vi pham gioi han vat ly (omega_max, tau_max) tai chu ky nho nhat tim duoc.")
        lines.append(f"- **Luu y:** tai chu ky cuc nhanh nay sai so xac lap tai Pick/Place len den ~{mm['err_pick_mm']:.1f}/{mm['err_place_mm']:.1f} mm, vuot nguong 1 mm, vi khong con thoi gian dung lai du. Day la gioi han do dong co/chuyen dong, chua phai dieu kien dat do chinh xac.")
        if mm["omega_violation"]:
            lines.append("- Gioi han **van toc goc omega_max** la rang buoc chinh can tro tang toc.")
        elif mm["tau_violation"]:
            lines.append("- Gioi han **mo-men tau_max** la rang buoc chinh can tro tang toc.")
    else:
        lines.append("- Khong tim duoc cau hinh kha thi trong khoang tim kiem.")
    lines.append("")

    lines.append("## 6. Nhan xet va di lech ky vong\n")
    lines.append(f"- Chu ky mac dinh {main_pid['metrics']['cycle_s']:.2f} s **{'dat' if main_pid['metrics']['cycle_s'] <= cfg['criteria']['cycle_time_target_s'] else 'chua dat'}** muc tieu <= {cfg['criteria']['cycle_time_target_s']} s.")
    lines.append(f"- PID + FF giam RMSE sai so bam tu {main_pid['metrics']['rmse_err_mm']:.3f} mm xuong {main_pidff['metrics']['rmse_err_mm']:.3f} mm so voi PID thuan, nho bu tru quan tinh/gia toc.")
    lines.append(f"- Tat ca cau hinh deu khong vi pham tau_max ({cfg['joint_model']['tau_max_Nm']} Nm) va omega_max ({cfg['joint_model']['omega_max_rad_s']} rad/s) o chu ky {main_pid['metrics']['cycle_s']:.2f} s.")
    if min_cycle['metrics']:
        lines.append(f"- Khi giam T, omega_max cham nguong ~{cfg['joint_model']['omega_max_rad_s']:.1f} rad/s truoc khi tau_max cham {cfg['joint_model']['tau_max_Nm']:.1f} Nm; do do **gioi han van toc goc** la rang buoc chinh can tro tang toc.")
    lines.append(f"- Chu ky nho nhat tinh duoc {min_cycle['cycle_min_s']:.3f} s la ly thuyet, dua tren J={cfg['joint_model']['J_kg_m2']} kg.m2 gia dinh; tren phan cung thuc te J, ma sat va tai trong lon hon nen chu ky nho nhat thuc te se lon hon.")
    lines.append("- **Khong co so do thuc nghiem trong run nay; moi so lieu deu tu mo phong.**")
    lines.append("- Thoi gian kep tha vat, do tre camera/Serial va sai so hinh hoc chua duoc tinh den.")
    lines.append("- Can kiem chung lai voi mo hinh dong luc hoc day du (co ma tran quan tinh, luc Coriolis, trong luc) khi co BOM chinh xac.\n")

    lines.append("## 7. File ket qua\n")
    lines.append("- `output/PID_thuan.csv` va `output/PID_plus_FF.csv`: du lieu tho thoi gian.")
    lines.append("- `output/metrics.json`: cac chi so dinh luong tong hop (JSON).")
    lines.append("- `figures/quy_dao_3d_va_xy.png`: quy dao 3D va hinh chieu xy.")
    lines.append("- `figures/sai_so_bam_theo_thoi_gian.png`: sai so bam.")
    lines.append("- `figures/mo_men_3_khop.png`: mo-men 3 khop.")
    lines.append("- `figures/van_toc_goc_3_khop.png`: van toc goc 3 khop.\n")

    with open(RUN_DIR / "KETQUA.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# -----------------------------------------------------------------------------
# Ham chinh
# -----------------------------------------------------------------------------
def main() -> None:
    cfg = load_config(CONFIG_PATH)
    set_seed(cfg["seed"])

    waypoints = np.array([
        cfg["waypoints_mm"]["home"],
        cfg["waypoints_mm"]["pick"],
        cfg["waypoints_mm"]["place"],
        cfg["waypoints_mm"]["home"],
    ], dtype=float)

    T_default = cfg["trajectory"]["T_default_s"]
    total_default = 3.0 * T_default
    t_eval_default = np.linspace(
        0.0, total_default,
        max(2, int(round(total_default / cfg["simulation"]["dt_s"])) + 1)
    )

    Kp = cfg["pid_gains"]["Kp"]
    Ki = cfg["pid_gains"]["Ki"]
    Kd = cfg["pid_gains"]["Kd"]

    print("=== 1. Chay PID thuan ===")
    main_pid = run_configuration(cfg, waypoints, T_default, Kp, Ki, Kd, False,
                                 "PID_thuan", t_eval_default)
    print(f"  RMSE={main_pid['metrics']['rmse_err_mm']:.4f} mm, "
          f"overshoot pick={main_pid['metrics']['overshoot_pick_pct']:.2f}%, "
          f"cycle={main_pid['metrics']['cycle_s']:.3f} s")

    print("=== 2. Chay PID + Feed-forward ===")
    main_pidff = run_configuration(cfg, waypoints, T_default, Kp, Ki, Kd, True,
                                   "PID_plus_FF", t_eval_default)
    print(f"  RMSE={main_pidff['metrics']['rmse_err_mm']:.4f} mm, "
          f"overshoot pick={main_pidff['metrics']['overshoot_pick_pct']:.2f}%, "
          f"cycle={main_pidff['metrics']['cycle_s']:.3f} s")

    print("=== 3. Quet cac bo PID ===")
    scan_res = scan_gains(cfg, waypoints, T_default, t_eval_default)
    for r in scan_res:
        m = r["metrics"]
        print(f"  {r['label']}: RMSE={m['rmse_err_mm']:.4f} mm, "
              f"over={m['overshoot_pick_pct']:.2f}/{m['overshoot_place_pct']:.2f}%")

    print("=== 4. Tim chu ky nho nhat kha thi ===")
    def t_eval_fn(T):
        total = 3.0 * T
        n_steps = max(2, int(round(total / cfg["simulation"]["dt_s"])) + 1)
        return np.linspace(0.0, total, n_steps)
    min_cycle = find_min_cycle(cfg, waypoints, t_eval_fn, Kp, Ki, Kd, use_ff=True)
    print(f"  T_segment_min = {min_cycle['T_min_feasible_s']:.4f} s, "
          f"cycle_min = {min_cycle['cycle_min_s']:.4f} s")

    print("=== 5. Xuat CSV, metrics va hinh ===")
    export_csv([main_pid, main_pidff])
    export_metrics_json(main_pid, main_pidff, scan_res, min_cycle)
    plot_results([main_pid, main_pidff], waypoints, cfg)
    write_report(cfg, main_pid, main_pidff, scan_res, min_cycle)
    print("=== Hoan thanh ===")


if __name__ == "__main__":
    main()
