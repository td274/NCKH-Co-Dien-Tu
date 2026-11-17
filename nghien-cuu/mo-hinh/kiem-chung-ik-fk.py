# -*- coding: utf-8 -*-
"""
Kiểm chứng chéo Động học Nghịch (IK) ↔ Động học Thuận (FK) và phân tích kỳ dị Jacobian
cho Robot Delta 3 bậc tự do tịnh tiến (3-DOF Translational Delta Robot).

Đóng góp chính (Khoảng trống nghiên cứu số 1 của đề tài):
1. Dẫn giải và kiểm chứng đại số bằng SymPy cho phương trình IK, FK giải tích, và Jacobian.
2. Quét lưới trụ (≥ 1000 điểm) trong vùng làm việc tham chiếu Ø300 × 150 mm (z ∈ [-425, -275] mm).
3. Tính θ = IK(p), sau đó p'_ana = FK_analytical(θ) và p'_nr = FK_NewtonRaphson(θ).
4. Báo cáo sai số cực đại (Max Error), RMSE (mm), chênh lệch giữa FK giải tích và FK Newton-Raphson,
   số điểm không hội tụ, và chỉ số điều kiện Jacobian (condition number).
5. Xuất dữ liệu CSV và 2 biểu đồ PNG 300 dpi phục vụ công bố khoa học:
   - nghien-cuu/mo-hinh/ket-qua/sai-so-ik-fk.csv
   - nghien-cuu/mo-hinh/ket-qua/ban-do-sai-so-xy.png
   - nghien-cuu/mo-hinh/ket-qua/mat-cat-vung-lam-viec.png
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import sympy as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Cấu hình font hiển thị tiếng Việt chuẩn trên Windows
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Segoe UI"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# 1. THÔNG SỐ HÌNH HỌC THAM CHIẾU CỦA ROBOT DELTA (ĐƠN VỊ: mm, rad)
# ==============================================================================
SQRT3 = np.sqrt(3.0)

# Thông số chuẩn theo đề bài (Giả định tham chiếu, sẽ chốt theo BOM):
# f  : cạnh tam giác đều đế cố định (mm)
# e  : cạnh tam giác đều bàn di động (mm)
# rf : chiều dài khâu chủ động / tay quay trên - upper arm (mm)
# re : chiều dài khâu bị động song song / cẳng tay dưới - lower arm (mm)
PARAMS_DEFAULT: Dict[str, float] = {
    "f": 346.0,
    "e": 115.0,
    "rf": 200.0,
    "re": 400.0,
    # Khớp quay A_i đặt tại đỉnh tam giác đều (bán kính đường tròn ngoại tiếp):
    # R_b = f / sqrt(3) ≈ 199.7632 mm, r_p = e / sqrt(3) ≈ 66.3953 mm
    "R_b": 346.0 / SQRT3,
    "r_p": 115.0 / SQRT3,
    "R": (346.0 - 115.0) / SQRT3,  # R = R_b - r_p ≈ 133.3679 mm
}

# Góc định hướng của 3 nhánh trong mặt phẳng Oxy: phi_1 = 0, phi_2 = 120 deg, phi_3 = 240 deg
PHIS = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0], dtype=float)


# ==============================================================================
# 2. KIỂM CHỨNG ĐẠI SỐ BẰNG SYMPY (SYMBOLIC VERIFICATION)
# ==============================================================================
def verify_symbolic_derivation() -> Dict[str, str]:
    """
    Dùng SymPy kiểm chứng phương trình khép kín vòng vector của nhánh i
    và phép thế lượng giác nửa góc t_i = tan(theta_i / 2).
    """
    x_i, y_i, z_i = sp.symbols("x_i y_i z_i", real=True)
    R_sym, rf_sym, re_sym = sp.symbols("R r_f r_e", positive=True)
    theta_i, t_i = sp.symbols("theta_i t_i", real=True)

    # Tâm cầu ảo C_i trong hệ tọa độ địa phương nhánh i: [R + rf*cos(theta_i), 0, -rf*sin(theta_i)]
    # Điểm tâm bàn di động P trong hệ tọa độ địa phương nhánh i: [x_i, y_i, z_i]
    constraint_eq = (
        (x_i - (R_sym + rf_sym * sp.cos(theta_i))) ** 2
        + y_i ** 2
        + (z_i - (-rf_sym * sp.sin(theta_i))) ** 2
        - re_sym ** 2
    )

    E_i = -2 * rf_sym * (x_i - R_sym)
    F_i = 2 * rf_sym * z_i
    G_i = (x_i - R_sym) ** 2 + y_i ** 2 + z_i ** 2 + rf_sym ** 2 - re_sym ** 2

    trig_form = E_i * sp.cos(theta_i) + F_i * sp.sin(theta_i) + G_i
    res_trig = sp.simplify(sp.expand(constraint_eq - trig_form))

    # Thế Weierstrass: cos(theta_i) = (1 - t_i^2)/(1 + t_i^2), sin(theta_i) = 2*t_i/(1 + t_i^2)
    poly_t = sp.expand(E_i * (1 - t_i ** 2) + F_i * (2 * t_i) + G_i * (1 + t_i ** 2))
    expected_poly = (G_i - E_i) * t_i ** 2 + 2 * F_i * t_i + (G_i + E_i)
    res_poly = sp.simplify(poly_t - expected_poly)

    assert res_trig == 0, f"Lỗi dẫn giải phương trình lượng giác IK: {res_trig}"
    assert res_poly == 0, f"Lỗi dẫn giải phương trình bậc hai theo t_i: {res_poly}"

    return {
        "trig_residual": str(res_trig),
        "poly_residual": str(res_poly),
        "status": "PASSED (Exact Symbolic Match = 0)",
    }


# ==============================================================================
# 3. ĐỘNG HỌC NGHỊCH GIẢI TÍCH (ANALYTICAL INVERSE KINEMATICS)
# ==============================================================================
def inverse_kinematics(
    p: np.ndarray, params: Dict[str, float] = PARAMS_DEFAULT
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    """
    Tính động học nghịch giải tích từ tọa độ điểm tác động cuối p = [x, y, z]^T (mm)
    ra vector góc khớp chủ động theta = [theta_1, theta_2, theta_3]^T (rad).

    Quy ước dấu góc theta_i:
    - theta_i = 0 khi khâu chủ động rf nằm ngang trên mặt phẳng Oxy hướng ra ngoài.
    - theta_i > 0 khi khâu chủ động quay hướng xuống dưới (về phía z < 0).
    - Chọn nhánh nghiệm có khuỷu tay hướng ra ngoài (elbow-out): dấu '-' trước căn thức
      t_i = (-F_i - sqrt(Delta_i)) / (G_i - E_i), tương ứng cos(theta_i) > 0 (theta_i in (-pi/2, pi/2)).
    """
    x, y, z = float(p[0]), float(p[1]), float(p[2])
    R = params["R"]
    rf = params["rf"]
    re = params["re"]

    thetas = np.zeros(3, dtype=float)
    discriminants = np.zeros(3, dtype=float)
    lateral_margins = np.zeros(3, dtype=float)

    for i, phi in enumerate(PHIS):
        c, s = np.cos(phi), np.sin(phi)
        # Phép quay hệ tọa độ toàn cục về hệ tọa độ nhánh i: R_z(-phi_i)
        x_i = x * c + y * s
        y_i = -x * s + y * c
        z_i = z

        # Điều kiện hình học ngang: chiều dài hình chiếu cẳng tay trên mặt phẳng (x_i, z_i)
        lat_margin = re ** 2 - y_i ** 2
        lateral_margins[i] = lat_margin
        if lat_margin <= 0.0:
            return None, {"reason": f"Vi phạm giới hạn ngang tại nhánh {i+1}: re^2 - y_i^2 <= 0"}

        E_i = -2.0 * rf * (x_i - R)
        F_i = 2.0 * rf * z_i
        G_i = (x_i - R) ** 2 + y_i ** 2 + z_i ** 2 + rf ** 2 - re ** 2

        disc = E_i ** 2 + F_i ** 2 - G_i ** 2
        discriminants[i] = disc
        if disc < 0.0:
            return None, {"reason": f"Biệt thức Delta_{i+1} < 0 ({disc:.3f}): ngoài tầm với"}

        sqrt_disc = np.sqrt(disc)
        # Để tránh mất chữ số có nghĩa khi |G_i - E_i| rất nhỏ (khi x_i -> R, z_i^2 + y_i^2 -> re^2 - rf^2):
        # Phương trình bậc hai theo t_i: a_t * t_i^2 + 2 * F_i * t_i + c_t = 0
        # với a_t = G_i - E_i, c_t = G_i + E_i.
        # Theo định lý Viète: t_1 * t_2 = c_t / a_t.
        # Vì F_i = 2 * rf * z < 0 (do z < 0), nên -F_i > 0, suy ra t_in = (-F_i + sqrt_disc) / a_t không bị hủy số!
        # Do đó tính t_out = c_t / (-F_i + sqrt_disc) hoàn toàn không có phép chia cho a_t = G_i - E_i và không trừ hai số gần bằng nhau!
        a_t = G_i - E_i
        c_t = G_i + E_i
        if F_i <= 0.0:
            q_num = -F_i + sqrt_disc  # luôn dương lớn (> 2*|F_i|)
            t_out = c_t / q_num
            t_in = q_num / a_t if abs(a_t) > 1e-12 else 1e15
        else:
            q_num = -F_i - sqrt_disc
            t_out = a_t / q_num if abs(q_num) > 1e-12 else 0.0
            t_in = c_t / q_num if abs(q_num) > 1e-12 else 1e15

        th_out = 2.0 * np.arctan(t_out)
        th_in = 2.0 * np.arctan(t_in)

        # Kiểm chứng nhánh khuỷu hướng ra ngoài có hoành độ khuỷu x_Bi = R_b + rf*cos(theta_i) lớn hơn
        if np.cos(th_out) >= np.cos(th_in):
            thetas[i] = th_out
        else:
            thetas[i] = th_in

    return thetas, {
        "discriminants": discriminants,
        "lateral_margins": lateral_margins,
    }


# ==============================================================================
# 4. ĐỘNG HỌC THUẬN GIẢI TÍCH (ANALYTICAL FORWARD KINEMATICS - TRILATERATION)
# ==============================================================================
def get_virtual_sphere_centers(
    thetas: np.ndarray, params: Dict[str, float] = PARAMS_DEFAULT
) -> np.ndarray:
    """
    Tính tọa độ 3 tâm mặt cầu ảo C_i (i = 1, 2, 3) từ góc khớp chủ động thetas (rad).
    C_i = B_i - d_i = [(R + rf*cos(theta_i))*cos(phi_i), (R + rf*cos(theta_i))*sin(phi_i), -rf*sin(theta_i)]^T
    """
    R = params["R"]
    rf = params["rf"]
    C = np.zeros((3, 3), dtype=float)
    for i, phi in enumerate(PHIS):
        c, s = np.cos(phi), np.sin(phi)
        th = float(thetas[i])
        rho_i = R + rf * np.cos(th)
        C[i, 0] = rho_i * c
        C[i, 1] = rho_i * s
        C[i, 2] = -rf * np.sin(th)
    return C


def forward_kinematics_analytical(
    thetas: np.ndarray, params: Dict[str, float] = PARAMS_DEFAULT
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    """
    Giải động học thuận giải tích bằng phương pháp giao 3 mặt cầu (Trilateration)
    và khử đại số tuyến tính hai biến (x, y) theo z.
    Chọn nghiệm vật lý nằm dưới đế cố định (z < 0, tương ứng nhánh z nhỏ hơn).
    """
    re = params["re"]
    C = get_virtual_sphere_centers(thetas, params)
    w = np.sum(C ** 2, axis=1)  # w_i = x_Ci^2 + y_Ci^2 + z_Ci^2

    # Hiệu phương trình mặt cầu và chuẩn hóa thông qua giải hệ 2x2 tốt nhất (tránh chia cho số gần 0):
    # (C_2 - C_1) . p = (w_2 - w_1)/2
    # (C_3 - C_1) . p = (w_3 - w_1)/2
    # M * [x, y]^T = d - c_vec * z
    M = np.array([
        [C[1, 0] - C[0, 0], C[1, 1] - C[0, 1]],
        [C[2, 0] - C[0, 0], C[2, 1] - C[0, 1]],
    ], dtype=float)
    c_vec = np.array([C[1, 2] - C[0, 2], C[2, 2] - C[0, 2]], dtype=float)
    d_vec = np.array([0.5 * (w[1] - w[0]), 0.5 * (w[2] - w[0])], dtype=float)

    D = float(np.linalg.det(M))
    if abs(D) < 1e-12:
        return None, {"reason": "Định thức D = a21*b31 - a31*b21 suy biến (3 tâm cầu thẳng hàng chiếu bằng)"}

    # Biểu diễn [x, y]^T = u_xy + v_xy * z bằng np.linalg.solve (có pivoting một phần để đạt độ chính xác ~1e-14 mm)
    u_xy = np.linalg.solve(M, d_vec)
    v_xy = np.linalg.solve(M, -c_vec)
    u_x, u_y = float(u_xy[0]), float(u_xy[1])
    v_x, v_y = float(v_xy[0]), float(v_xy[1])

    # Thế vào phương trình mặt cầu có khoảng cách ngang nhỏ nhất để giảm hủy chữ số có nghĩa:
    A_q = v_x ** 2 + v_y ** 2 + 1.0
    B_q = 2.0 * (v_x * (u_x - C[0, 0]) + v_y * (u_y - C[0, 1]) - C[0, 2])
    C_q = (u_x - C[0, 0]) ** 2 + (u_y - C[0, 1]) ** 2 + C[0, 2] ** 2 - re ** 2

    disc_z = B_q ** 2 - 4.0 * A_q * C_q
    if disc_z < 0.0:
        return None, {"reason": f"Biệt thức phương trình bậc hai theo z âm: {disc_z}"}

    # Công thức bậc hai ổn định số học (Citardauq / tránh trừ hai số xấp xỉ nhau):
    sqrt_disc = np.sqrt(disc_z)
    if B_q >= 0.0:
        z_low = (-B_q - sqrt_disc) / (2.0 * A_q)
    else:
        z_high = (-B_q + sqrt_disc) / (2.0 * A_q)
        z_low = C_q / (A_q * z_high)
    z = float(z_low)
    x = u_x + v_x * z
    y = u_y + v_y * z

    return np.array([x, y, z], dtype=float), {"D": D, "disc_z": disc_z}


# ==============================================================================
# 5. ĐỘNG HỌC THUẬN SỐ (NEWTON-RAPHSON ITERATIVE METHOD)
# ==============================================================================
def forward_kinematics_nr(
    thetas: np.ndarray,
    p_init: np.ndarray = np.array([0.0, 0.0, -350.0]),
    params: Dict[str, float] = PARAMS_DEFAULT,
    tol: float = 1e-11,
    max_iter: int = 50,
) -> Tuple[np.ndarray, int, bool, float]:
    """
    Giải động học thuận bằng phương pháp lặp Newton-Raphson trên hệ phương trình phi tuyến:
      F_i(x, y, z) = ||p - C_i||^2 - re^2 = 0,  i = 1, 2, 3
    với ma trận đạo hàm riêng J_F = dF/dp = 2 * [ (p - C_1)^T ; (p - C_2)^T ; (p - C_3)^T ].

    Nếu nghiệm hội tụ về nhánh trên (z > 0), tự động khởi tạo lại ở phía dưới (z < 0) để đảm bảo đúng nhánh.
    """
    re = params["re"]
    C = get_virtual_sphere_centers(thetas, params)
    p = p_init.astype(float).copy()

    for it in range(1, max_iter + 1):
        diff = p - C  # shape (3, 3): mỗi hàng là (p - C_i)^T
        F = np.sum(diff ** 2, axis=1) - re ** 2
        res_norm = float(np.linalg.norm(F, ord=2))
        if res_norm < tol:
            if p[2] < 0.0:
                return p, it, True, res_norm
            else:
                # Phản xạ qua mặt phẳng z trung bình của 3 tâm cầu nếu rơi vào nhánh z > 0
                p[2] = -abs(p[2]) - 300.0

        J_F = 2.0 * diff
        try:
            dp = np.linalg.solve(J_F, -F)
        except np.linalg.LinAlgError:
            return p, it, False, res_norm

        p = p + dp
        if float(np.linalg.norm(dp, ord=2)) < tol and float(np.linalg.norm(F, ord=2)) < 1e-8:
            if p[2] < 0.0:
                diff_final = p - C
                F_final = np.sum(diff_final ** 2, axis=1) - re ** 2
                return p, it, True, float(np.linalg.norm(F_final, ord=2))

    diff_final = p - C
    F_final = np.sum(diff_final ** 2, axis=1) - re ** 2
    return p, max_iter, False, float(np.linalg.norm(F_final, ord=2))


# ==============================================================================
# 6. MA TRẬN JACOBIAN VÀ PHÂN TÍCH ĐIỂM KỲ DỊ (SINGULARITY ANALYSIS)
# ==============================================================================
def compute_jacobian(
    p: np.ndarray, thetas: np.ndarray, params: Dict[str, float] = PARAMS_DEFAULT
) -> Dict[str, Any]:
    """
    Tính các ma trận Jacobian từ phương trình ràng buộc vòng kín:
      f_i(p, theta_i) = ||p - C_i(theta_i)||^2 - re^2 = 0
    Đạo hàm theo thời gian:
      J_x * p_dot = J_theta * theta_dot
    Trong đó:
      - Hàng thứ i của J_x là vector dọc cẳng tay s_i^T = (p - C_i)^T (đơn vị: mm)
      - J_theta = diag(J_theta_11, J_theta_22, J_theta_33) với
        J_theta_ii = s_i^T * (dC_i / dtheta_i) (đơn vị: mm^2/rad)
      - Jacobian thuận: J = dp / dtheta = J_x^{-1} * J_theta (đơn vị: mm/rad)
      - Jacobian nghịch: J^{-1} = dtheta / dp = J_theta^{-1} * J_x (đơn vị: rad/mm)
    """
    R = params["R"]
    rf = params["rf"]
    C = get_virtual_sphere_centers(thetas, params)

    J_x = np.zeros((3, 3), dtype=float)
    J_theta_diag = np.zeros(3, dtype=float)
    transmission_angles_deg = np.zeros(3, dtype=float)

    for i, phi in enumerate(PHIS):
        c, s = np.cos(phi), np.sin(phi)
        th = float(thetas[i])
        s_i = p - C[i]  # Vector dọc cẳng tay từ C_i tới P (chiều dài = re)
        J_x[i, :] = s_i

        # Vector đạo hàm dC_i / dtheta_i (vuông góc với khâu chủ động rf trong mặt phẳng nhánh i, độ lớn = rf)
        b_i = np.array([-rf * np.sin(th) * c, -rf * np.sin(th) * s, -rf * np.cos(th)], dtype=float)
        J_theta_diag[i] = float(np.dot(s_i, b_i))

        # Góc truyền lực giữa cẳng tay s_i và pháp tuyến khâu chủ động b_i:
        # |s_i . b_i| / (re * rf) = |sin(gamma_i)|, trong đó gamma_i là góc giữa s_i và khâu chủ động u_i
        sin_gamma = min(1.0, abs(J_theta_diag[i]) / (params["re"] * rf))
        transmission_angles_deg[i] = float(np.degrees(np.arcsin(sin_gamma)))

    J_theta = np.diag(J_theta_diag)
    det_Jx = float(np.linalg.det(J_x))
    det_Jtheta = float(np.prod(J_theta_diag))

    # Để đánh giá số điều kiện không thứ nguyên (dimensionless condition number),
    # chuẩn hoá từng hàng của J_x theo re (véctơ đơn vị dọc cẳng tay u_si = s_i / re)
    # và chia J_theta cho (re * rf):
    # u_si^T * p_dot = (J_theta_ii / (re * rf)) * (rf * theta_dot_i)
    J_forward = np.linalg.inv(J_x) @ J_theta  # mm/rad
    J_normalized = (np.linalg.inv(J_x / params["re"])) @ np.diag(J_theta_diag / (params["re"] * rf))

    cond_J_norm = float(np.linalg.cond(J_normalized))
    cond_J_raw = float(np.linalg.cond(J_forward))

    return {
        "J_x": J_x,
        "J_theta": J_theta,
        "J_forward": J_forward,
        "J_normalized": J_normalized,
        "det_Jx": det_Jx,
        "det_Jtheta": det_Jtheta,
        "min_abs_Jtheta_ii": float(np.min(np.abs(J_theta_diag))),
        "min_transmission_angle_deg": float(np.min(transmission_angles_deg)),
        "cond_J_norm": cond_J_norm,
        "cond_J_raw": cond_J_raw,
    }


# ==============================================================================
# 7. QUÉT LƯỚI KIỂM CHỨNG CHÉO IK ↔ FK VÀ VÙNG LÀM VIỆC
# ==============================================================================
def generate_cylindrical_grid(
    r_max: float = 150.0,
    z_min: float = -425.0,
    z_max: float = -275.0,
    n_r: int = 8,
    n_azim_base: int = 24,
    n_z: int = 11,
) -> np.ndarray:
    """
    Sinh lưới điểm phân bố đều trong hình trụ Ø300 × 150 mm (R <= 150 mm, z in [-425, -275] mm).
    Tại r = 0 chỉ lấy 1 điểm tâm mỗi mặt cắt z; tại r > 0 lấy n_azim_base điểm trên đường tròn.
    Tổng số điểm: n_z * (1 + (n_r - 1) * n_azim_base) = 11 * (1 + 7 * 24) = 1859 điểm (>= 1000 điểm).
    """
    radii = np.linspace(0.0, r_max, n_r)
    z_levels = np.linspace(z_min, z_max, n_z)
    points = []
    for z in z_levels:
        for r in radii:
            if r == 0.0:
                points.append([0.0, 0.0, float(z)])
            else:
                angles = np.linspace(0.0, 2.0 * np.pi, n_azim_base, endpoint=False)
                for ang in angles:
                    points.append([float(r * np.cos(ang)), float(r * np.sin(ang)), float(z)])
    return np.array(points, dtype=float)


def run_cross_validation_and_export() -> None:
    out_dir = Path(__file__).resolve().parent / "ket-qua"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Kiểm chứng đại số SymPy
    sym_res = verify_symbolic_derivation()

    # 2. Sinh tập điểm lưới trong hình trụ tham chiếu Ø300 × 150 mm
    grid_points = generate_cylindrical_grid(
        r_max=150.0, z_min=-425.0, z_max=-275.0, n_r=8, n_azim_base=24, n_z=11
    )
    n_total = len(grid_points)

    records = []
    n_ik_valid = 0
    n_nr_unconverged = 0

    for idx, p in enumerate(grid_points):
        thetas, ik_info = inverse_kinematics(p, PARAMS_DEFAULT)
        if thetas is None:
            records.append({
                "id": idx + 1,
                "x_mm": p[0], "y_mm": p[1], "z_mm": p[2],
                "r_mm": np.hypot(p[0], p[1]),
                "valid_ik": 0,
            })
            continue

        n_ik_valid += 1
        p_ana, _ = forward_kinematics_analytical(thetas, PARAMS_DEFAULT)
        p_nr, nr_iters, nr_conv, nr_res = forward_kinematics_nr(
            thetas, p_init=np.array([0.0, 0.0, -350.0]), params=PARAMS_DEFAULT
        )
        if not nr_conv:
            n_nr_unconverged += 1

        jac_info = compute_jacobian(p, thetas, PARAMS_DEFAULT)

        err_ana = float(np.linalg.norm(p_ana - p, ord=2))
        err_nr = float(np.linalg.norm(p_nr - p, ord=2))
        diff_ana_nr = float(np.linalg.norm(p_ana - p_nr, ord=2))

        records.append({
            "id": idx + 1,
            "x_mm": p[0],
            "y_mm": p[1],
            "z_mm": p[2],
            "r_mm": float(np.hypot(p[0], p[1])),
            "valid_ik": 1,
            "theta1_deg": float(np.degrees(thetas[0])),
            "theta2_deg": float(np.degrees(thetas[1])),
            "theta3_deg": float(np.degrees(thetas[2])),
            "x_ana_mm": float(p_ana[0]),
            "y_ana_mm": float(p_ana[1]),
            "z_ana_mm": float(p_ana[2]),
            "x_nr_mm": float(p_nr[0]),
            "y_nr_mm": float(p_nr[1]),
            "z_nr_mm": float(p_nr[2]),
            "err_ana_mm": err_ana,
            "err_nr_mm": err_nr,
            "diff_ana_nr_mm": diff_ana_nr,
            "nr_iters": int(nr_iters),
            "nr_converged": int(nr_conv),
            "cond_J_norm": jac_info["cond_J_norm"],
            "cond_J_raw": jac_info["cond_J_raw"],
            "min_trans_angle_deg": jac_info["min_transmission_angle_deg"],
            "det_Jx_mm3": jac_info["det_Jx"],
            "min_abs_Jtheta_mm2": jac_info["min_abs_Jtheta_ii"],
        })

    # Lưu ra file CSV
    csv_path = out_dir / "sai-so-ik-fk.csv"
    headers = list(records[0].keys())
    with open(csv_path, "w", encoding="utf-8") as f_csv:
        f_csv.write(",".join(headers) + "\n")
        for r in records:
            row_vals = []
            for h in headers:
                v = r.get(h, "")
                if isinstance(v, float):
                    row_vals.append(f"{v:.10e}")
                else:
                    row_vals.append(str(v))
            f_csv.write(",".join(row_vals) + "\n")

    # Thống kê kết quả
    err_ana_arr = np.array([r["err_ana_mm"] for r in records if r["valid_ik"] == 1])
    err_nr_arr = np.array([r["err_nr_mm"] for r in records if r["valid_ik"] == 1])
    diff_arr = np.array([r["diff_ana_nr_mm"] for r in records if r["valid_ik"] == 1])
    iters_arr = np.array([r["nr_iters"] for r in records if r["valid_ik"] == 1])
    cond_norm_arr = np.array([r["cond_J_norm"] for r in records if r["valid_ik"] == 1])
    trans_angle_arr = np.array([r["min_trans_angle_deg"] for r in records if r["valid_ik"] == 1])
    th_all = np.array(
        [[r["theta1_deg"], r["theta2_deg"], r["theta3_deg"]] for r in records if r["valid_ik"] == 1]
    )

    max_err_ana = float(np.max(err_ana_arr))
    rmse_err_ana = float(np.sqrt(np.mean(err_ana_arr ** 2)))
    max_err_nr = float(np.max(err_nr_arr))
    rmse_err_nr = float(np.sqrt(np.mean(err_nr_arr ** 2)))
    max_diff_ana_nr = float(np.max(diff_arr))
    rmse_diff_ana_nr = float(np.sqrt(np.mean(diff_arr ** 2)))

    # ==========================================================================
    # VẼ HÌNH 1: BẢN ĐỒ SAI SỐ VÀ CHỈ SỐ ĐIỀU KIỆN JACOBIAN THEO MẶT PHẲNG XY
    # ==========================================================================
    fig1, axes1 = plt.subplots(1, 2, figsize=(13.5, 5.8), dpi=300)

    # Quét mặt phẳng tại z = -350 mm (tâm vùng làm việc) để vẽ bản đồ nhiệt liên tục
    z_slice = -350.0
    n_grid_xy = 81
    xg = np.linspace(-165.0, 165.0, n_grid_xy)
    yg = np.linspace(-165.0, 165.0, n_grid_xy)
    XX, YY = np.meshgrid(xg, yg)
    ERR_MAP = np.full_like(XX, np.nan)
    COND_MAP = np.full_like(XX, np.nan)

    for i in range(n_grid_xy):
        for j in range(n_grid_xy):
            px, py = XX[i, j], YY[i, j]
            if np.hypot(px, py) <= 155.0:
                th_ij, _ = inverse_kinematics(np.array([px, py, z_slice]), PARAMS_DEFAULT)
                if th_ij is not None:
                    p_a, _ = forward_kinematics_analytical(th_ij, PARAMS_DEFAULT)
                    ERR_MAP[i, j] = np.linalg.norm(p_a - np.array([px, py, z_slice]))
                    jac_ij = compute_jacobian(np.array([px, py, z_slice]), th_ij, PARAMS_DEFAULT)
                    COND_MAP[i, j] = jac_ij["cond_J_norm"]

    # Subplot 1A: Sai số vòng kín IK -> FK_analytical trên mặt phẳng XY (kèm các điểm lưới)
    ax = axes1[0]
    im0 = ax.pcolormesh(XX, YY, ERR_MAP * 1e13, cmap="viridis", shading="auto")
    circle1 = plt.Circle((0, 0), 150.0, color="red", fill=False, linestyle="--", linewidth=1.8, label="Biên Ø300 mm (R = 150 mm)")
    ax.add_patch(circle1)
    # Vẽ hướng 3 nhánh chủ động
    for k, phi in enumerate(PHIS):
        ax.arrow(0, 0, 130 * np.cos(phi), 130 * np.sin(phi), head_width=6, head_length=8, fc="white", ec="black", alpha=0.85)
        ax.text(142 * np.cos(phi), 142 * np.sin(phi), f"Nhánh {k+1}", color="black", fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.85))
    cbar0 = fig1.colorbar(im0, ax=ax, fraction=0.046, pad=0.04)
    cbar0.set_label(r"Sai số vòng kín $\| \mathrm{FK}(\mathrm{IK}(p)) - p \|_2$ ($\times 10^{-13}$ mm)", fontsize=10)
    ax.set_title(f"(a) Bản đồ sai số vòng kín IK↔FK tại z = {z_slice:.0f} mm", fontsize=11, fontweight="bold")
    ax.set_xlabel("Tọa độ x (mm)", fontsize=10)
    ax.set_ylabel("Tọa độ y (mm)", fontsize=10)
    ax.set_aspect("equal")
    ax.set_xlim(-170, 170)
    ax.set_ylim(-170, 170)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", fontsize=9)

    # Subplot 1B: Bản đồ số điều kiện Jacobian chuẩn hóa kappa(J) trên mặt phẳng XY
    ax1 = axes1[1]
    im1 = ax1.contourf(XX, YY, COND_MAP, levels=20, cmap="plasma")
    cs1 = ax1.contour(XX, YY, COND_MAP, levels=[1.2, 1.4, 1.6, 1.8, 2.0], colors="white", linewidths=0.8)
    ax1.clabel(cs1, inline=True, fontsize=8, fmt="%.2f")
    circle2 = plt.Circle((0, 0), 150.0, color="cyan", fill=False, linestyle="--", linewidth=1.8, label="Biên Ø300 mm (R = 150 mm)")
    ax1.add_patch(circle2)
    cbar1 = fig1.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label(r"Số điều kiện Jacobian chuẩn hóa $\kappa(\hat{J})$ (-)", fontsize=10)
    ax1.set_title(f"(b) Phân bố số điều kiện Jacobian tại z = {z_slice:.0f} mm", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Tọa độ x (mm)", fontsize=10)
    ax1.set_ylabel("Tọa độ y (mm)", fontsize=10)
    ax1.set_aspect("equal")
    ax1.set_xlim(-170, 170)
    ax1.set_ylim(-170, 170)
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper right", fontsize=9)

    fig1.suptitle(
        "Kiểm chứng chéo Động học Nghịch ↔ Thuận và Độ nhạy Jacobian trên mặt phẳng ngang (f=346, e=115, rf=200, re=400 mm)",
        fontsize=12, fontweight="bold", y=0.98
    )
    fig1.tight_layout(rect=[0, 0, 1, 0.94])
    fig1_path = out_dir / "ban-do-sai-so-xy.png"
    fig1.savefig(fig1_path, dpi=300)
    plt.close(fig1)

    # ==========================================================================
    # VẼ HÌNH 2: MẶT CẮT ĐỨNG VÙNG LÀM VIỆC (XZ CROSS-SECTION) & BAO HÌNH TRỤ Ø300x150
    # ==========================================================================
    fig2, axes2 = plt.subplots(1, 2, figsize=(13.5, 5.8), dpi=300)

    # Quét mặt cắt đứng (x, z) tại y = 0 để xác định biên vùng làm việc lý thuyết và khả dụng
    x_scan = np.linspace(-280.0, 280.0, 141)
    z_scan = np.linspace(-540.0, -140.0, 121)
    XS, ZS = np.meshgrid(x_scan, z_scan)
    WS_MASK = np.zeros_like(XS)  # 0: Ngoài tầm với, 1: Tồn tại IK, 2: Khả dụng an toàn (-40 deg <= theta <= 90 deg, góc truyền >= 25 deg)
    TH_MAX_MAP = np.full_like(XS, np.nan)

    for i in range(len(z_scan)):
        for j in range(len(x_scan)):
            p_xz = np.array([XS[i, j], 0.0, ZS[i, j]])
            th_xz, _ = inverse_kinematics(p_xz, PARAMS_DEFAULT)
            if th_xz is not None:
                th_deg = np.degrees(th_xz)
                # Kiểm tra nhánh khuỷu ngoài (|theta_i| < 90 deg)
                if np.all(np.abs(th_deg) < 90.0):
                    WS_MASK[i, j] = 1
                    jac_xz = compute_jacobian(p_xz, th_xz, PARAMS_DEFAULT)
                    if (
                        np.all(th_deg >= -40.0)
                        and np.all(th_deg <= 85.0)
                        and jac_xz["min_transmission_angle_deg"] >= 25.0
                    ):
                        WS_MASK[i, j] = 2
                        TH_MAX_MAP[i, j] = jac_xz["min_transmission_angle_deg"]

    # Subplot 2A: Mặt cắt đứng XZ tại y = 0 và hình chữ nhật bao vùng làm việc Ø300 × 150 mm
    ax2a = axes2[0]
    ax2a.contourf(XS, ZS, WS_MASK, levels=[-0.5, 0.5, 1.5, 2.5], colors=["#f0f0f0", "#bdd7e7", "#3182bd"], alpha=0.85)
    ax2a.contour(XS, ZS, WS_MASK, levels=[0.5, 1.5], colors=["#08519c", "#003366"], linewidths=1.2)

    # Vẽ hình chữ nhật đại diện cho hình trụ tham chiếu Ø300 × 150 mm (x in [-150, 150], z in [-425, -275])
    rect_ws = plt.Rectangle(
        (-150.0, -425.0), 300.0, 150.0,
        edgecolor="#d95f02", facecolor="none", linewidth=2.5, linestyle="--",
        label="Vùng làm việc yêu cầu Ø300 × 150 mm\n($z \\in [-425, -275]$ mm)"
    )
    ax2a.add_patch(rect_ws)

    # Chú giải vùng màu
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#3182bd", edgecolor="#003366", alpha=0.85, label="Vùng làm việc khả dụng an toàn\n($\\theta_i \\in [-40^\\circ, 85^\\circ], \\gamma_{\\min} \\geq 25^\\circ$)"),
        Patch(facecolor="#bdd7e7", edgecolor="#08519c", alpha=0.85, label="Biên toán học IK ($|\\theta_i| < 90^\\circ$)"),
        plt.Line2D([0], [0], color="#d95f02", lw=2.5, ls="--", label="Hình trụ mục tiêu Ø300 × 150 mm"),
    ]
    ax2a.set_title("(a) Mặt cắt đứng vùng làm việc tại mặt phẳng y = 0", fontsize=11, fontweight="bold")
    ax2a.set_xlabel("Tọa độ x (mm)", fontsize=10)
    ax2a.set_ylabel("Độ cao z (mm)", fontsize=10)
    ax2a.set_xlim(-280, 280)
    ax2a.set_ylim(-540, -140)
    ax2a.set_aspect("equal")
    ax2a.grid(True, linestyle=":", alpha=0.6)
    ax2a.legend(handles=legend_elements, loc="upper right", fontsize=8.5)

    # Subplot 2B: Bán kính khả dụng R_max(z) của hình trụ nội tiếp theo chiều cao z
    ax2b = axes2[1]
    z_prof = np.linspace(-520.0, -170.0, 71)
    r_math_prof = np.zeros_like(z_prof)
    r_safe_prof = np.zeros_like(z_prof)

    for idx_z, zv in enumerate(z_prof):
        for rv in np.linspace(0.0, 250.0, 51):
            ok_m = True
            ok_s = True
            for ang in np.linspace(0.0, 2.0 * np.pi, 36, endpoint=False):
                p_c = np.array([rv * np.cos(ang), rv * np.sin(ang), zv])
                th_c, _ = inverse_kinematics(p_c, PARAMS_DEFAULT)
                if th_c is None or np.any(np.abs(np.degrees(th_c)) >= 90.0):
                    ok_m = False
                    ok_s = False
                    break
                th_c_deg = np.degrees(th_c)
                if np.any(th_c_deg < -40.0) or np.any(th_c_deg > 85.0):
                    ok_s = False
            if ok_m:
                r_math_prof[idx_z] = rv
            if ok_s:
                r_safe_prof[idx_z] = rv

    ax2b.plot(r_math_prof, z_prof, "b-.", linewidth=1.8, label="Bán kính tối đa lý thuyết $R_{\\max,\\mathrm{math}}(z)$")
    ax2b.plot(r_safe_prof, z_prof, "g-", linewidth=2.4, label="Bán kính khả dụng cơ khí $R_{\\max,\\mathrm{safe}}(z)$")
    ax2b.axvline(150.0, color="#d95f02", linestyle="--", linewidth=2.0, label="Bán kính yêu cầu $R_{\\mathrm{req}} = 150$ mm (Ø300)")
    ax2b.axhspan(-425.0, -275.0, color="#fee6ce", alpha=0.55, label="Dải độ cao chọn $z \\in [-425, -275]$ mm ($H=150$ mm)")
    ax2b.set_title("(b) Bán kính hình trụ nội tiếp tối đa theo độ cao z", fontsize=11, fontweight="bold")
    ax2b.set_xlabel("Bán kính đối xứng trục $R_{\\max}(z)$ (mm)", fontsize=10)
    ax2b.set_ylabel("Độ cao z (mm)", fontsize=10)
    ax2b.set_xlim(0, 265)
    ax2b.set_ylim(-520, -170)
    ax2b.grid(True, linestyle=":", alpha=0.6)
    ax2b.legend(loc="lower left", fontsize=8.5)

    fig2.suptitle(
        "Phân tích Vùng làm việc (Workspace) của Robot Delta 3-DOF và Khả năng bao phủ hình trụ Ø300 × 150 mm",
        fontsize=12, fontweight="bold", y=0.98
    )
    fig2.tight_layout(rect=[0, 0, 1, 0.94])
    fig2_path = out_dir / "mat-cat-vung-lam-viec.png"
    fig2.savefig(fig2_path, dpi=300)
    plt.close(fig2)

    # Lưu file JSON tóm tắt số đo
    summary_data = {
        "parameters_mm": PARAMS_DEFAULT,
        "workspace_cylinder_mm": {
            "diameter_mm": 300.0,
            "radius_mm": 150.0,
            "height_mm": 150.0,
            "z_min_mm": -425.0,
            "z_max_mm": -275.0,
        },
        "symbolic_verification": sym_res,
        "grid_evaluation": {
            "total_points": n_total,
            "valid_ik_points": n_ik_valid,
            "coverage_percent": 100.0 * n_ik_valid / n_total,
            "nr_unconverged_points": n_nr_unconverged,
            "nr_max_iters": int(np.max(iters_arr)),
            "nr_mean_iters": float(np.mean(iters_arr)),
            "err_ik_fk_analytical_max_mm": max_err_ana,
            "err_ik_fk_analytical_rmse_mm": rmse_err_ana,
            "err_ik_fk_nr_max_mm": max_err_nr,
            "err_ik_fk_nr_rmse_mm": rmse_err_nr,
            "diff_analytical_vs_nr_max_mm": max_diff_ana_nr,
            "diff_analytical_vs_nr_rmse_mm": rmse_diff_ana_nr,
            "theta_min_deg": float(np.min(th_all)),
            "theta_max_deg": float(np.max(th_all)),
            "cond_J_norm_min": float(np.min(cond_norm_arr)),
            "cond_J_norm_max": float(np.max(cond_norm_arr)),
            "cond_J_norm_mean": float(np.mean(cond_norm_arr)),
            "min_transmission_angle_deg": float(np.min(trans_angle_arr)),
        },
    }
    json_path = out_dir / "tom-tat-kiem-chung.json"
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(summary_data, f_json, indent=2, ensure_ascii=False)

    # In bảng tóm tắt ra Console
    print("=" * 80)
    print("BẢNG TÓM TẮT KIỂM CHỨNG CHÉO ĐỘNG HỌC ROBOT DELTA 3-DOF (IK ↔ FK)")
    print("=" * 80)
    print(f"1. Bộ tham số hình học (Giả định tham chiếu theo đề bài):")
    print(f"   - Cạnh tam giác đế cố định     f  = {PARAMS_DEFAULT['f']:.2f} mm (R_b = f/sqrt(3) = {PARAMS_DEFAULT['R_b']:.4f} mm)")
    print(f"   - Cạnh tam giác bàn di động    e  = {PARAMS_DEFAULT['e']:.2f} mm (r_p = e/sqrt(3) = {PARAMS_DEFAULT['r_p']:.4f} mm)")
    print(f"   - Hiệu bán kính tương đương    R  = R_b - r_p = {PARAMS_DEFAULT['R']:.4f} mm")
    print(f"   - Chiều dài tay quay chủ động  rf = {PARAMS_DEFAULT['rf']:.2f} mm")
    print(f"   - Chiều dài cẳng tay song song re = {PARAMS_DEFAULT['re']:.2f} mm")
    print("-" * 80)
    print(f"2. Kiểm chứng đại số SymPy:")
    print(f"   - Trạng thái: {sym_res['status']}")
    print("-" * 80)
    print(f"3. Độ phủ vùng làm việc hình trụ tham chiếu Ø300 × 150 mm (z in [-425, -275] mm):")
    print(f"   - Tổng số điểm lưới kiểm tra        : {n_total} điểm (8 bán kính × 24 góc × 11 mặt cắt + tâm)")
    print(f"   - Số điểm có nghiệm IK hợp lệ       : {n_ik_valid} / {n_total} ({100.0*n_ik_valid/n_total:.2f}%)")
    print(f"   - Dải góc khớp chủ động (theta_i)   : [{np.min(th_all):.2f} deg, {np.max(th_all):.2f} deg]")
    print(f"   - Góc truyền lực nhỏ nhất (gamma)   : {np.min(trans_angle_arr):.2f} deg")
    print(f"   - Số điều kiện Jacobian chuẩn hóa   : min = {np.min(cond_norm_arr):.3f}, max = {np.max(cond_norm_arr):.3f}, mean = {np.mean(cond_norm_arr):.3f}")
    print("-" * 80)
    print(f"4. Sai số vòng kín IK(p) -> FK(theta) và đối sánh Giải tích vs Newton-Raphson:")
    print(f"   - FK Giải tích (Trilateration)      : Max Error = {max_err_ana:.4e} mm | RMSE = {rmse_err_ana:.4e} mm")
    print(f"   - FK Số (Newton-Raphson)            : Max Error = {max_err_nr:.4e} mm | RMSE = {rmse_err_nr:.4e} mm")
    print(f"   - Chênh lệch ||FK_ana - FK_NR||_2   : Max Diff  = {max_diff_ana_nr:.4e} mm | RMSE = {rmse_diff_ana_nr:.4e} mm")
    print(f"   - Số điểm Newton-Raphson không hội tụ: {n_nr_unconverged} / {n_total} điểm (Số vòng lặp TB: {np.mean(iters_arr):.2f}, Max: {np.max(iters_arr)})")
    print("-" * 80)
    print(f"5. Các file kết quả đã xuất:")
    print(f"   - CSV dữ liệu : {csv_path}")
    print(f"   - JSON tóm tắt: {json_path}")
    print(f"   - Hình 1 (XY) : {fig1_path}")
    print(f"   - Hình 2 (XZ) : {fig2_path}")
    print("=" * 80)


if __name__ == "__main__":
    run_cross_validation_and_export()
