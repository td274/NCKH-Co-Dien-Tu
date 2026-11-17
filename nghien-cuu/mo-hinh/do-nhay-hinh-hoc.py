# -*- coding: utf-8 -*-
"""
Khảo sát Độ nhạy Sai số Hình học (Geometric Error Sensitivity Analysis) của Robot Delta 3-DOF
theo phương pháp mô phỏng Monte Carlo (dựa trên mô hình sai số hình học của Vischer & Clavel 1998).

Mục tiêu:
1. Giải quyết tính tầm thường của sai số vòng kín thuần số học (1.58e-13 mm):
   - Bộ điều khiển tính góc khớp danh định: theta_nom = IK(p_nom, params_nominal)
   - Cơ khí thực tế có dung sai chế tạo/lắp ráp (params_perturbed), nên bàn di động đi tới:
     p_actual = FK(theta_nom, params_perturbed)
   - Sai số vị trí thực tế do dung sai hình học: e_pos = ||p_actual - p_nom||_2 (mm).
2. Mô hình sai số chế tạo bất đối xứng trên từng nhánh i = 1, 2, 3 (15 biến dung sai độc lập):
   - Chiều dài 3 tay quay chủ động: rf_i = rf_0 + delta_rf_i
   - Chiều dài 3 cặp cẳng tay bị động: re_i = re_0 + delta_re_i
   - Kích thước cạnh đế cố định & bàn di động: f_i = f_0 + delta_f_i, e_i = e_0 + delta_e_i
   - Sai lệch vị trí lắp đặt 3 ổ trục khớp đế (theo phương hướng kính & thẳng đứng): delta_Rb_i, delta_zA_i
3. Thống kê Monte Carlo (N_mc = 300 bộ tham số robot ngẫu nhiên × 533 điểm lưới vùng làm việc Ø300×150 mm
   = 159,900 mẫu đánh giá cho mỗi mức dung sai):
   - Mức 1 (Gia công CNC / In 3D chuẩn + căn chỉnh cẩn thận): dung sai đều U(-0.2, +0.2) mm
   - Mức 2 (Gia công thô / Lắp ráp thủ công sai lệch lớn): dung sai đều U(-0.5, +0.5) mm
   - Báo cáo: Trung bình (Mean), RMSE, Trung vị (Median / P50), Phân vị 95% (P95), Phân vị 99% (P99),
     Cực đại (Max), và Tỷ lệ % điểm trong vùng làm việc đạt mục tiêu <= 1.0 mm.
4. Phân tích độ nhạy riêng (One-at-a-Time / OAT Sensitivity Analysis) để xác định tham số nào
   ảnh hưởng mạnh nhất tới sai số vị trí điểm cuối.
5. Xuất dữ liệu CSV, JSON và biểu đồ 300 dpi vào `nghien-cuu/mo-hinh/ket-qua/`:
   - `do-nhay-hinh-hoc-mc.csv`, `do-nhay-rieng-oat.csv`, `tom-tat-do-nhay.json`
   - `do-nhay-sai-so-hinh-hoc.png` (Histogram phân bố sai số + Độ nhạy riêng + Bản đồ nhiệt P95 trên mặt phẳng XY)
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Segoe UI"]
plt.rcParams["axes.unicode_minus"] = False

SQRT3 = np.sqrt(3.0)
PHIS = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0], dtype=float)
COS_PHIS = np.cos(PHIS)
SIN_PHIS = np.sin(PHIS)

PARAMS_NOMINAL = {
    "f": 346.0,
    "e": 115.0,
    "rf": 200.0,
    "re": 400.0,
    "R": (346.0 - 115.0) / SQRT3,
}


# ==============================================================================
# 1. HÀM ĐỘNG HỌC NGHỊCH VECTOR HÓA CHO TẬP ĐIỂM LƯỚI (NOMINAL IK)
# ==============================================================================
def generate_workspace_grid(
    r_max: float = 150.0,
    z_min: float = -425.0,
    z_max: float = -275.0,
    n_r: int = 6,
    n_azim: int = 16,
    n_z: int = 7,
) -> np.ndarray:
    """
    Sinh lưới điểm đại diện phủ đều hình trụ Ø300 × 150 mm:
    n_z * (1 + (n_r - 1) * n_azim) = 7 * (1 + 5 * 16) = 567 điểm.
    """
    radii = np.linspace(0.0, r_max, n_r)
    z_levels = np.linspace(z_min, z_max, n_z)
    pts = []
    for z in z_levels:
        for r in radii:
            if r == 0.0:
                pts.append([0.0, 0.0, float(z)])
            else:
                for ang in np.linspace(0.0, 2.0 * np.pi, n_azim, endpoint=False):
                    pts.append([float(r * np.cos(ang)), float(r * np.sin(ang)), float(z)])
    return np.array(pts, dtype=float)


def compute_nominal_ik_batch(pts: np.ndarray, params: Dict[str, float] = PARAMS_NOMINAL) -> np.ndarray:
    """
    Tính góc khớp danh định thetas (N_pts, 3) từ tọa độ pts (N_pts, 3) với bộ tham số danh nghĩa.
    """
    R = params["R"]
    rf = params["rf"]
    re = params["re"]
    N = pts.shape[0]
    thetas = np.zeros((N, 3), dtype=float)

    x = pts[:, 0]
    y = pts[:, 1]
    z = pts[:, 2]

    for i in range(3):
        c, s = COS_PHIS[i], SIN_PHIS[i]
        xi = x * c + y * s
        yi = -x * s + y * c
        zi = z

        Ei = -2.0 * rf * (xi - R)
        Fi = 2.0 * rf * zi
        Gi = (xi - R) ** 2 + yi ** 2 + zi ** 2 + rf ** 2 - re ** 2
        disc = Ei ** 2 + Fi ** 2 - Gi ** 2
        sqrt_disc = np.sqrt(np.maximum(0.0, disc))

        # Công thức Citardauq ổn định cho nhánh khuỷu hướng ra ngoài (z < 0 => Fi < 0)
        q_num = -Fi + sqrt_disc
        t_out = (Gi + Ei) / q_num
        thetas[:, i] = 2.0 * np.arctan(t_out)

    return thetas


# ==============================================================================
# 2. HÀM ĐỘNG HỌC THUẬN VỚI THAM SỐ BỊ NHIỄU TỪNG NHÁNH (PERTURBED FK)
# ==============================================================================
def forward_kinematics_perturbed_batch(
    thetas: np.ndarray,
    df_vec: np.ndarray,
    de_vec: np.ndarray,
    drf_vec: np.ndarray,
    dre_vec: np.ndarray,
    dRb_vec: np.ndarray,
    dzA_vec: np.ndarray,
    params_nom: Dict[str, float] = PARAMS_NOMINAL,
) -> np.ndarray:
    """
    Tính vị trí thực tế p_actual (N_pts, 3) khi góc khớp đặt là thetas (N_pts, 3)
    nhưng cơ khí của 3 nhánh bị sai lệch độc lập:
      - f_i = f_0 + df_vec[i], e_i = e_0 + de_vec[i]
      - dRb_vec[i] : sai lệch vị trí lắp đặt ổ trục khớp đế A_i theo phương hướng kính
      - dzA_vec[i] : sai lệch cao độ lắp đặt ổ trục khớp đế A_i theo phương z
      - rf_i = rf_0 + drf_vec[i] : chiều dài thực của tay quay chủ động nhánh i
      - re_i = re_0 + dre_vec[i] : chiều dài thực của cẳng tay bị động nhánh i

    Phương trình mặt cầu nhánh i có bán kính khác nhau re_i:
      (x - x_Ci)^2 + (y - y_Ci)^2 + (z - z_Ci)^2 = re_i^2
      => x^2 + y^2 + z^2 - 2*x_Ci*x - 2*y_Ci*y - 2*z_Ci*z = re_i^2 - w_i
    Trừ phương trình i=1 với i=2, 3:
      2*(x_C2 - x_C1)*x + 2*(y_C2 - y_C1)*y + 2*(z_C2 - z_C1)*z = (w_2 - re_2^2) - (w_1 - re_1^2)
    """
    N = thetas.shape[0]
    f0, e0, rf0, re0 = params_nom["f"], params_nom["e"], params_nom["rf"], params_nom["re"]

    # Hiệu bán kính thực tế trên từng nhánh i = 0, 1, 2
    R_i = (f0 + df_vec - (e0 + de_vec)) / SQRT3 + dRb_vec
    rf_i = rf0 + drf_vec
    re_i = re0 + dre_vec
    zA_i = dzA_vec

    # Tâm cầu ảo C_i cho toàn bộ N điểm: shape (N, 3_branches, 3_coords)
    C = np.zeros((N, 3, 3), dtype=float)
    for i in range(3):
        rho_i = R_i[i] + rf_i[i] * np.cos(thetas[:, i])
        C[:, i, 0] = rho_i * COS_PHIS[i]
        C[:, i, 1] = rho_i * SIN_PHIS[i]
        C[:, i, 2] = zA_i[i] - rf_i[i] * np.sin(thetas[:, i])

    # w_tilde_i = ||C_i||^2 - re_i^2
    w_tilde = np.sum(C ** 2, axis=2) - (re_i ** 2)[None, :]

    a21 = C[:, 1, 0] - C[:, 0, 0]
    b21 = C[:, 1, 1] - C[:, 0, 1]
    c21 = C[:, 1, 2] - C[:, 0, 2]
    d21 = 0.5 * (w_tilde[:, 1] - w_tilde[:, 0])

    a31 = C[:, 2, 0] - C[:, 0, 0]
    b31 = C[:, 2, 1] - C[:, 0, 1]
    c31 = C[:, 2, 2] - C[:, 0, 2]
    d31 = 0.5 * (w_tilde[:, 2] - w_tilde[:, 0])

    D = a21 * b31 - a31 * b21
    u_x = (b31 * d21 - b21 * d31) / D
    v_x = (b21 * c31 - b31 * c21) / D
    u_y = (a21 * d31 - a31 * d21) / D
    v_y = (a31 * c21 - a21 * c31) / D

    A_q = v_x ** 2 + v_y ** 2 + 1.0
    B_q = 2.0 * (v_x * (u_x - C[:, 0, 0]) + v_y * (u_y - C[:, 0, 1]) - C[:, 0, 2])
    C_q = (u_x - C[:, 0, 0]) ** 2 + (u_y - C[:, 0, 1]) ** 2 + C[:, 0, 2] ** 2 - re_i[0] ** 2

    disc_z = np.maximum(0.0, B_q ** 2 - 4.0 * A_q * C_q)
    z = (-B_q - np.sqrt(disc_z)) / (2.0 * A_q)
    x = u_x + v_x * z
    y = u_y + v_y * z

    return np.column_stack([x, y, z])


# ==============================================================================
# 3. CHẠY MÔ PHỎNG MONTE CARLO VÀ PHÂN TÍCH ĐỘ NHẠY RIÊNG (OAT)
# ==============================================================================
def run_monte_carlo_for_tolerance(
    pts: np.ndarray,
    thetas_nom: np.ndarray,
    tol_mm: float,
    n_mc: int = 300,
    seed: int = 20261118,
    include_base_mount_error: bool = True,
) -> Dict[str, Any]:
    """
    Chạy n_mc lần rút mẫu ngẫu nhiên phân bố đều U(-tol_mm, +tol_mm) cho các tham số hình học.
    Trả về mảng sai số toàn cục (n_mc, n_pts) và các chỉ số thống kê phân vị.
    """
    rng = np.random.default_rng(seed)
    n_pts = pts.shape[0]
    err_matrix = np.zeros((n_mc, n_pts), dtype=float)

    for m in range(n_mc):
        df_vec = rng.uniform(-tol_mm, tol_mm, size=3)
        de_vec = rng.uniform(-tol_mm, tol_mm, size=3)
        drf_vec = rng.uniform(-tol_mm, tol_mm, size=3)
        dre_vec = rng.uniform(-tol_mm, tol_mm, size=3)
        if include_base_mount_error:
            dRb_vec = rng.uniform(-tol_mm, tol_mm, size=3)
            dzA_vec = rng.uniform(-tol_mm, tol_mm, size=3)
        else:
            dRb_vec = np.zeros(3)
            dzA_vec = np.zeros(3)

        p_act = forward_kinematics_perturbed_batch(
            thetas_nom, df_vec, de_vec, drf_vec, dre_vec, dRb_vec, dzA_vec
        )
        err_matrix[m, :] = np.linalg.norm(p_act - pts, axis=1)

    flat_err = err_matrix.ravel()
    # Thống kê theo từng điểm lưới (trung bình và P95 tại mỗi điểm không gian)
    point_p95 = np.percentile(err_matrix, 95.0, axis=0)
    point_max = np.max(err_matrix, axis=0)
    point_mean = np.mean(err_matrix, axis=0)

    stats = {
        "tol_mm": tol_mm,
        "include_base_mount_error": include_base_mount_error,
        "n_mc": n_mc,
        "n_pts": n_pts,
        "total_evaluations": int(flat_err.size),
        "mean_mm": float(np.mean(flat_err)),
        "rmse_mm": float(np.sqrt(np.mean(flat_err ** 2))),
        "median_p50_mm": float(np.percentile(flat_err, 50.0)),
        "p90_mm": float(np.percentile(flat_err, 90.0)),
        "p95_mm": float(np.percentile(flat_err, 95.0)),
        "p99_mm": float(np.percentile(flat_err, 99.0)),
        "max_mm": float(np.max(flat_err)),
        "pct_samples_le_1mm": float(100.0 * np.mean(flat_err <= 1.0)),
        "pct_workspace_p95_le_1mm": float(100.0 * np.mean(point_p95 <= 1.0)),
        "pct_workspace_mean_le_1mm": float(100.0 * np.mean(point_mean <= 1.0)),
        "err_matrix": err_matrix,
        "point_p95": point_p95,
        "point_max": point_max,
        "point_mean": point_mean,
    }
    return stats


def run_single_parameter_sensitivity(
    pts: np.ndarray,
    thetas_nom: np.ndarray,
    tol_mm: float = 0.2,
    n_mc: int = 300,
    seed: int = 20261118,
) -> Dict[str, Dict[str, float]]:
    """
    Phân tích độ nhạy riêng từng nhóm tham số (One-at-a-Time / OAT):
    Chỉ cho duy nhất 1 loại tham số bị nhiễu U(-tol_mm, +tol_mm) (hoặc dịch chuyển cố định +tol_mm)
    để xếp hạng mức độ ảnh hưởng của: rf, re, f, e, và vị trí khớp đế (dRb, dzA).
    """
    param_names = ["rf", "re", "f", "e", "base_pos"]
    results = {}

    for idx_p, name in enumerate(param_names):
        rng = np.random.default_rng(seed + idx_p * 100)
        err_mat = np.zeros((n_mc, pts.shape[0]), dtype=float)
        for m in range(n_mc):
            df_vec = rng.uniform(-tol_mm, tol_mm, size=3) if name == "f" else np.zeros(3)
            de_vec = rng.uniform(-tol_mm, tol_mm, size=3) if name == "e" else np.zeros(3)
            drf_vec = rng.uniform(-tol_mm, tol_mm, size=3) if name == "rf" else np.zeros(3)
            dre_vec = rng.uniform(-tol_mm, tol_mm, size=3) if name == "re" else np.zeros(3)
            if name == "base_pos":
                dRb_vec = rng.uniform(-tol_mm, tol_mm, size=3)
                dzA_vec = rng.uniform(-tol_mm, tol_mm, size=3)
            else:
                dRb_vec = np.zeros(3)
                dzA_vec = np.zeros(3)

            p_act = forward_kinematics_perturbed_batch(
                thetas_nom, df_vec, de_vec, drf_vec, dre_vec, dRb_vec, dzA_vec
            )
            err_mat[m, :] = np.linalg.norm(p_act - pts, axis=1)

        # Tính thêm hệ số khuếch đại sai số cực đại khi nhánh 1 bị lệch +tol_mm, nhánh 2 lệch -tol_mm (worst-case deterministic)
        pattern = np.array([tol_mm, -tol_mm, tol_mm])
        df_w = pattern if name == "f" else np.zeros(3)
        de_w = pattern if name == "e" else np.zeros(3)
        drf_w = pattern if name == "rf" else np.zeros(3)
        dre_w = pattern if name == "re" else np.zeros(3)
        dRb_w = pattern if name == "base_pos" else np.zeros(3)
        dzA_w = pattern if name == "base_pos" else np.zeros(3)
        p_w = forward_kinematics_perturbed_batch(
            thetas_nom, df_w, de_w, drf_w, dre_w, dRb_w, dzA_w
        )
        err_w = np.linalg.norm(p_w - pts, axis=1)

        flat = err_mat.ravel()
        results[name] = {
            "mean_mm": float(np.mean(flat)),
            "rmse_mm": float(np.sqrt(np.mean(flat ** 2))),
            "median_p50_mm": float(np.percentile(flat, 50.0)),
            "p95_mm": float(np.percentile(flat, 95.0)),
            "p99_mm": float(np.percentile(flat, 99.0)),
            "max_mc_mm": float(np.max(flat)),
            "worst_case_gain_mm_per_mm": float(np.max(err_w) / tol_mm),
            "mean_gain_mm_per_mm": float(np.mean(err_w) / tol_mm),
        }

    return results


# ==============================================================================
# 4. HÀM CHÍNH: CHẠY KHẢO SÁT, XUẤT CSV/JSON VÀ VẼ BIỂU ĐỒ 300 DPI
# ==============================================================================
def main() -> None:
    out_dir = Path(__file__).resolve().parent / "ket-qua"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sinh lưới điểm trong vùng làm việc Ø300 × 150 mm (567 điểm)
    pts = generate_workspace_grid(r_max=150.0, z_min=-425.0, z_max=-275.0, n_r=6, n_azim=16, n_z=7)
    thetas_nom = compute_nominal_ik_batch(pts, PARAMS_NOMINAL)

    # 2. Chạy Monte Carlo (N_mc = 300 lần rút tham số × 567 điểm = 170,100 mẫu đánh giá mỗi kịch bản)
    # Kịch bản A1: ±0.2 mm (chỉ 4 tham số khâu f, e, rf, re)
    mc_02_links = run_monte_carlo_for_tolerance(
        pts, thetas_nom, tol_mm=0.2, n_mc=300, seed=20261118, include_base_mount_error=False
    )
    # Kịch bản A2: ±0.2 mm (toàn phần: f, e, rf, re + sai lệch vị trí khớp đế ±0.2 mm)
    mc_02_full = run_monte_carlo_for_tolerance(
        pts, thetas_nom, tol_mm=0.2, n_mc=300, seed=20261119, include_base_mount_error=True
    )
    # Kịch bản B1: ±0.5 mm (chỉ 4 tham số khâu f, e, rf, re)
    mc_05_links = run_monte_carlo_for_tolerance(
        pts, thetas_nom, tol_mm=0.5, n_mc=300, seed=20261120, include_base_mount_error=False
    )
    # Kịch bản B2: ±0.5 mm (toàn phần: f, e, rf, re + sai lệch vị trí khớp đế ±0.5 mm)
    mc_05_full = run_monte_carlo_for_tolerance(
        pts, thetas_nom, tol_mm=0.5, n_mc=300, seed=20261121, include_base_mount_error=True
    )

    # 3. Phân tích độ nhạy riêng từng tham số tại mức ±0.2 mm
    oat_02 = run_single_parameter_sensitivity(pts, thetas_nom, tol_mm=0.2, n_mc=300, seed=20261122)

    # 4. Lưu file CSV thống kê theo từng điểm lưới
    csv_mc_path = out_dir / "do-nhay-hinh-hoc-mc.csv"
    with open(csv_mc_path, "w", encoding="utf-8") as f_csv:
        f_csv.write(
            "id,x_mm,y_mm,z_mm,r_mm,"
            "mean_02_links_mm,p95_02_links_mm,max_02_links_mm,"
            "mean_02_full_mm,p95_02_full_mm,max_02_full_mm,"
            "mean_05_links_mm,p95_05_links_mm,max_05_links_mm,"
            "mean_05_full_mm,p95_05_full_mm,max_05_full_mm\n"
        )
        for i, p in enumerate(pts):
            r_val = float(np.hypot(p[0], p[1]))
            f_csv.write(
                f"{i+1},{p[0]:.4f},{p[1]:.4f},{p[2]:.4f},{r_val:.4f},"
                f"{mc_02_links['point_mean'][i]:.6f},{mc_02_links['point_p95'][i]:.6f},{mc_02_links['point_max'][i]:.6f},"
                f"{mc_02_full['point_mean'][i]:.6f},{mc_02_full['point_p95'][i]:.6f},{mc_02_full['point_max'][i]:.6f},"
                f"{mc_05_links['point_mean'][i]:.6f},{mc_05_links['point_p95'][i]:.6f},{mc_05_links['point_max'][i]:.6f},"
                f"{mc_05_full['point_mean'][i]:.6f},{mc_05_full['point_p95'][i]:.6f},{mc_05_full['point_max'][i]:.6f}\n"
            )

    # Lưu JSON tổng hợp
    def strip_arrays(d: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in d.items() if not isinstance(v, np.ndarray)}

    summary_json = {
        "description": "Khảo sát độ nhạy sai số hình học Monte Carlo (N_mc = 300 × 567 điểm = 170,100 mẫu/kịch bản)",
        "mc_02mm_links_only": strip_arrays(mc_02_links),
        "mc_02mm_with_base_error": strip_arrays(mc_02_full),
        "mc_05mm_links_only": strip_arrays(mc_05_links),
        "mc_05mm_with_base_error": strip_arrays(mc_05_full),
        "oat_sensitivity_02mm": oat_02,
    }
    json_path = out_dir / "tom-tat-do-nhay.json"
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(summary_json, f_json, indent=2, ensure_ascii=False)

    # ==========================================================================
    # 5. VẼ HÌNH XUẤT BẢN 300 DPI: HISTOGRAM + ĐỘ NHẠY RIÊNG + BẢN ĐỒ P95 XY
    # ==========================================================================
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.4), dpi=300)

    # --- Subplot (a): Histogram phân bố sai số vị trí cho ±0.2 mm và ±0.5 mm ---
    ax0 = axes[0]
    samples_02_l = mc_02_links["err_matrix"].ravel()
    samples_02_f = mc_02_full["err_matrix"].ravel()
    samples_05_l = mc_05_links["err_matrix"].ravel()
    samples_05_f = mc_05_full["err_matrix"].ravel()

    bins = np.linspace(0.0, 1.8, 75)
    ax0.hist(samples_02_l, bins=bins, density=True, alpha=0.65, color="#1f77b4",
             label=f"±0,2 mm (4 khâu): P50={mc_02_links['median_p50_mm']:.2f}, P95={mc_02_links['p95_mm']:.2f} mm")
    ax0.hist(samples_02_f, bins=bins, density=True, histtype="step", linewidth=2.0, color="#003366",
             label=f"±0,2 mm (+khớp đế): P50={mc_02_full['median_p50_mm']:.2f}, P95={mc_02_full['p95_mm']:.2f} mm")
    ax0.hist(samples_05_l, bins=bins, density=True, alpha=0.50, color="#ff7f0e",
             label=f"±0,5 mm (4 khâu): P50={mc_05_links['median_p50_mm']:.2f}, P95={mc_05_links['p95_mm']:.2f} mm")
    ax0.hist(samples_05_f, bins=bins, density=True, histtype="step", linewidth=1.8, linestyle="--", color="#b30000",
             label=f"±0,5 mm (+khớp đế): P50={mc_05_full['median_p50_mm']:.2f}, P95={mc_05_full['p95_mm']:.2f} mm")

    ax0.axvline(1.0, color="red", linestyle="-", linewidth=2.2, label="Ngưỡng mục tiêu 1,00 mm")
    ax0.set_title("(a) Phân bố sai số vị trí Monte Carlo (170.100 mẫu)", fontsize=11, fontweight="bold")
    ax0.set_xlabel(r"Sai số vị trí điểm cuối $\|p_{\mathrm{thực}} - p_{\mathrm{danh\_nghĩa}}\|_2$ (mm)", fontsize=10)
    ax0.set_ylabel("Mật độ xác suất", fontsize=10)
    ax0.set_xlim(0.0, 1.75)
    ax0.grid(True, linestyle=":", alpha=0.6)
    ax0.legend(loc="upper right", fontsize=8.0)

    # --- Subplot (b): Biểu đồ cột so sánh Độ nhạy riêng (OAT) của từng tham số ở ±0.2 mm ---
    ax1 = axes[1]
    labels_vn = [
        "Cẳng tay\n$r_e$ (±0,2 mm)",
        "Tay quay\n$r_f$ (±0,2 mm)",
        "Khớp đế\n$\\Delta R_b, \\Delta z_A$",
        "Cạnh đế\n$f$ (±0,2 mm)",
        "Bàn di động\n$e$ (±0,2 mm)",
    ]
    keys_order = ["re", "rf", "base_pos", "f", "e"]
    p50_vals = [oat_02[k]["median_p50_mm"] for k in keys_order]
    p95_vals = [oat_02[k]["p95_mm"] for k in keys_order]
    max_vals = [oat_02[k]["max_mc_mm"] for k in keys_order]

    x_pos = np.arange(len(keys_order))
    width = 0.26
    ax1.bar(x_pos - width, p50_vals, width, label="Trung vị (P50)", color="#4daf4a")
    ax1.bar(x_pos, p95_vals, width, label="Phân vị 95% (P95)", color="#377eb8")
    ax1.bar(x_pos + width, max_vals, width, label="Cực đại (Max)", color="#e41a1c")

    for idx_b in range(len(keys_order)):
        ax1.text(x_pos[idx_b], p95_vals[idx_b] + 0.012, f"{p95_vals[idx_b]:.2f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(labels_vn, fontsize=8.5)
    ax1.set_title("(b) Độ nhạy riêng từng tham số ở mức ±0,2 mm", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Sai số vị trí gây ra (mm)", fontsize=10)
    ax1.set_ylim(0.0, max(max_vals) * 1.18)
    ax1.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right", fontsize=8.5)

    # --- Subplot (c): Bản đồ phân vị 95% (P95) của sai số trên mặt phẳng XY tại z = -350 mm ---
    ax2 = axes[2]
    n_xy = 51
    xg = np.linspace(-155.0, 155.0, n_xy)
    yg = np.linspace(-155.0, 155.0, n_xy)
    XX, YY = np.meshgrid(xg, yg)
    pts_xy = []
    ij_list = []
    for i in range(n_xy):
        for j in range(n_xy):
            if np.hypot(XX[i, j], YY[i, j]) <= 152.0:
                pts_xy.append([XX[i, j], YY[i, j], -350.0])
                ij_list.append((i, j))
    pts_xy_arr = np.array(pts_xy, dtype=float)
    th_xy = compute_nominal_ik_batch(pts_xy_arr, PARAMS_NOMINAL)
    mc_xy = run_monte_carlo_for_tolerance(
        pts_xy_arr, th_xy, tol_mm=0.2, n_mc=300, seed=20261119, include_base_mount_error=True
    )
    P95_MAP = np.full_like(XX, np.nan)
    for k_idx, (i, j) in enumerate(ij_list):
        P95_MAP[i, j] = mc_xy["point_p95"][k_idx]

    im2 = ax2.contourf(XX, YY, P95_MAP, levels=18, cmap="YlOrRd")
    cs2 = ax2.contour(XX, YY, P95_MAP, levels=6, colors="black", linewidths=0.6, alpha=0.6)
    ax2.clabel(cs2, inline=True, fontsize=7.5, fmt="%.2f")
    circ = plt.Circle((0, 0), 150.0, color="blue", fill=False, linestyle="--", linewidth=1.8, label="Biên Ø300 mm")
    ax2.add_patch(circ)
    cbar2 = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label("Sai số phân vị 95% P95 (mm)", fontsize=9.5)
    ax2.set_title("(c) Bản đồ sai số P95 tại z = -350 mm (±0,2 mm toàn phần)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Tọa độ x (mm)", fontsize=10)
    ax2.set_ylabel("Tọa độ y (mm)", fontsize=10)
    ax2.set_aspect("equal")
    ax2.set_xlim(-160, 160)
    ax2.set_ylim(-160, 160)
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper right", fontsize=8.5)

    fig.suptitle(
        r"Khảo sát Độ nhạy Sai số Hình học bằng Mô phỏng Monte Carlo (Vùng làm việc Ø300 × 150 mm, $z \in [-425, -275]$ mm)",
        fontsize=12.5, fontweight="bold", y=0.98
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig_path = out_dir / "do-nhay-sai-so-hinh-hoc.png"
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)

    # In kết quả chi tiết ra Console
    print("=" * 88)
    print("KẾT QUẢ KHẢO SÁT ĐỘ NHẠY SAI SỐ HÌNH HỌC MONTE CARLO (ROBOT DELTA 3-DOF)")
    print("=" * 88)
    print(f"Cấu hình Monte Carlo: N_mc = 300 bộ tham số × 567 điểm lưới = 170.100 mẫu đánh giá / kịch bản")
    print("-" * 88)
    header_fmt = "{:<36} | {:>7} | {:>7} | {:>7} | {:>7} | {:>7} | {:>10}"
    row_fmt = "{:<36} | {:>7.3f} | {:>7.3f} | {:>7.3f} | {:>7.3f} | {:>7.3f} | {:>9.2f}%"
    print(header_fmt.format("Kịch bản dung sai chế tạo", "Mean", "P50", "P95", "P99", "Max", "Đạt <=1mm"))
    print("-" * 88)
    for label, st in [
        ("1a. ±0,2 mm (4 khâu f, e, rf, re)", mc_02_links),
        ("1b. ±0,2 mm (+ lệch khớp đế ±0,2 mm)", mc_02_full),
        ("2a. ±0,5 mm (4 khâu f, e, rf, re)", mc_05_links),
        ("2b. ±0,5 mm (+ lệch khớp đế ±0,5 mm)", mc_05_full),
    ]:
        print(
            row_fmt.format(
                label,
                st["mean_mm"],
                st["median_p50_mm"],
                st["p95_mm"],
                st["p99_mm"],
                st["max_mm"],
                st["pct_samples_le_1mm"],
            )
        )
    print("-" * 88)
    print("Tỷ lệ điểm không gian trong vùng làm việc có P95 <= 1,0 mm:")
    print(f"  - Ở mức ±0,2 mm (4 khâu)         : {mc_02_links['pct_workspace_p95_le_1mm']:.2f}% vùng làm việc (Mean <= 1 mm: {mc_02_links['pct_workspace_mean_le_1mm']:.2f}%)")
    print(f"  - Ở mức ±0,2 mm (+ lệch khớp đế) : {mc_02_full['pct_workspace_p95_le_1mm']:.2f}% vùng làm việc (Mean <= 1 mm: {mc_02_full['pct_workspace_mean_le_1mm']:.2f}%)")
    print(f"  - Ở mức ±0,5 mm (4 khâu)         : {mc_05_links['pct_workspace_p95_le_1mm']:.2f}% vùng làm việc (Mean <= 1 mm: {mc_05_links['pct_workspace_mean_le_1mm']:.2f}%)")
    print(f"  - Ở mức ±0,5 mm (+ lệch khớp đế) : {mc_05_full['pct_workspace_p95_le_1mm']:.2f}% vùng làm việc (Mean <= 1 mm: {mc_05_full['pct_workspace_mean_le_1mm']:.2f}%)")
    print("-" * 88)
    print("Xếp hạng Độ nhạy riêng từng tham số (OAT ở mức dung sai ±0,2 mm):")
    for k in ["re", "rf", "base_pos", "f", "e"]:
        d = oat_02[k]
        print(
            f"  - {k:<10}: P50 = {d['median_p50_mm']:.3f} mm | P95 = {d['p95_mm']:.3f} mm | "
            f"Max = {d['max_mc_mm']:.3f} mm | Hệ số khuếch đại xấu nhất = {d['worst_case_gain_mm_per_mm']:.2f} mm/mm"
        )
    print("-" * 88)
    print(f"Đã lưu hình: {fig_path}")
    print(f"Đã lưu CSV : {csv_mc_path}")
    print(f"Đã lưu JSON: {json_path}")
    print("=" * 88)


if __name__ == "__main__":
    main()
