# Mô hình Động học Thuận – Nghịch, Phân tích Kỳ dị Jacobian và Kiểm chứng Chéo của Robot Delta 3 Bậc Tự do Tịnh tiến

**Đề tài:** Nghiên cứu và mô phỏng robot Delta cho ứng dụng phân loại sản phẩm bằng camera  
**Đóng góp học thuật:** Giải quyết *Khoảng trống nghiên cứu số 1* (xem `nghien-cuu/tai-lieu/tong-quan.md`) — Thiết lập mô hình giải tích tường minh kết hợp giải số Newton–Raphson và kiểm chứng chéo định lượng vòng kín $\text{IK} \leftrightarrow \text{FK}$ trên $1\,859$ điểm lưới thuộc không gian làm việc hình trụ tham chiếu $\varnothing 300 \times 150\text{ mm}$.  
**Script kiểm chứng đi kèm:** `nghien-cuu/mo-hinh/kiem-chung-ik-fk.py`, `nghien-cuu/mo-hinh/do-nhay-hinh-hoc.py`  
**Thư mục dữ liệu & hình vẽ xuất bản:** `nghien-cuu/mo-hinh/ket-qua/`

---

## 1. Sơ đồ & ký hiệu

### 1.1. Sơ đồ cấu trúc hình học và hệ tọa độ

Robot Delta 3 bậc tự do tịnh tiến (*3-DOF translational parallel robot*, theo cấu trúc gốc của Clavel [1]) gồm **đế cố định (fixed base)** phía trên và **bàn di động (moving platform)** phía dưới, nối với nhau qua $3$ chuỗi động học đối xứng hoàn toàn ($i = 1, 2, 3$), bố trí lệch nhau góc $120^\circ$ quanh trục thẳng đứng $Oz$.

```text
                      Hệ tọa độ cố định Oxyz (Gốc O tại tâm đế cố định)
                                     ^ +z
                                     |
                   A_2               O               A_1 (phi_1 = 0 deg)
                    o================+================o----> +x
                                                      \
                                                       \  Khâu chủ động (Upper arm, r_f)
                                                        \ Góc khớp theta_1 (> 0 khi quay xuống)
                                                         o B_1 (Khớp khuỷu / Elbow)
                                                        //
                                                       // Cơ cấu hình bình hành (Lower arm, r_e)
                                                      //  (2 thanh song song nối bằng khớp cầu)
                                                     //
                             P_2     P     P_1      //
                              o======*======o======o
                                 Bàn di động (e)
                                     |
                                     v -z (Vùng làm việc: z < 0)
```

Quy ước hệ tọa độ và phương pháp mô hình hoá (thay cho tham số Denavit–Hartenberg truyền thống vốn chỉ thuận tiện cho robot chuỗi hở nối tiếp, ở đây sử dụng **Phương pháp khép kín vòng vector — Vector-Loop Closure** trong tọa độ Descartes kết hợp phép quay hệ tọa độ địa phương cho từng nhánh song song):

1. **Hệ tọa độ toàn cục $Oxyz$:**
   - Gốc $O(0, 0, 0)$ đặt tại tâm đường tròn ngoại tiếp tam giác đều đế cố định $A_1 A_2 A_3$.
   - Mặt phẳng $Oxy$ trùng với mặt phẳng chứa 3 trục khớp quay chủ động $A_1, A_2, A_3$.
   - Trục $+Ox$ hướng từ tâm $O$ tới khớp chủ động nhánh 1 ($A_1$).
   - Trục $+Oz$ hướng thẳng đứng lên trên; toàn bộ vùng làm việc của bàn di động nằm ở nửa không gian phía dưới đế cố định ($z < 0$).
2. **Hệ tọa độ địa phương nhánh $i$ ($O x_i y_i z_i$, với $i \in \{1, 2, 3\}$):**
   - Quay hệ tọa độ $Oxyz$ quanh trục $Oz$ một góc phương vị $\phi_i$:
     $$\phi_1 = 0\text{ rad}\ (0^\circ), \quad \phi_2 = \frac{2\pi}{3}\text{ rad}\ (120^\circ), \quad \phi_3 = \frac{4\pi}{3}\text{ rad}\ (240^\circ)$$
   - Trong hệ $O x_i y_i z_i$, khớp quay chủ động $A_i$ nằm trên trục $+O x_i$ tại tọa độ địa phương ${}^{(i)}\mathbf{a}_i = [R_b, 0, 0]^T$; trục quay của khớp $A_i$ song song với trục $O y_i$; khâu chủ động $A_i B_i$ luôn chuyển động phẳng trong mặt phẳng thẳng đứng $O x_i z_i$ ($y_i = 0$).
3. **Quy ước bố trí khớp trên tam giác đều (Đỉnh vs. Cạnh):**
   - Để khớp đúng giá trị tham chiếu trong đề bài ($f = 346\text{ mm}, e = 115\text{ mm} \implies R_b \approx 200\text{ mm}, r_p \approx 66\text{ mm}$), các tâm khớp $A_i$ và $P_i$ được định nghĩa tại **3 đỉnh** của tam giác đều cạnh $f$ và $e$ (bán kính đường tròn ngoại tiếp):
     $$R_b = \frac{f}{\sqrt{3}}, \qquad r_p = \frac{e}{\sqrt{3}}, \qquad R = R_b - r_p = \frac{f - e}{\sqrt{3}}$$
   - *Ghi chú quy đổi:* Nếu một bản thiết kế CAD bố trí ổ trục dọc theo trung điểm cạnh tam giác đều cạnh $f_{\text{cạnh}}, e_{\text{cạnh}}$ (bán kính đường tròn nội tiếp $R_b = f_{\text{cạnh}}/(2\sqrt{3})$), toàn bộ các phương trình dưới đây vẫn giữ nguyên khi thay trực tiếp giá trị bán kính $R_b, r_p$ và $R = R_b - r_p$.

### 1.2. Bảng ký hiệu và đơn vị chuẩn SI

Trong các công thức toán học tổng quát, đơn vị chuẩn là **SI** ($\text{m}, \text{rad}, \text{s}$); trong tính toán số và bản vẽ kỹ thuật cơ khí, chiều dài được biểu diễn thêm bằng milimét ($\text{mm}$, với $1\text{ mm} = 10^{-3}\text{ m}$) và góc bằng độ ($\text{deg}$) có ghi chú rõ ở tiêu đề cột.

| Ký hiệu | Ý nghĩa vật lý / hình học | Đơn vị SI | Đơn vị tính toán cơ khí |
| :---: | --- | :---: | :---: |
| $f$ | Chiều dài cạnh tam giác đều đế cố định $A_1 A_2 A_3$ | $\text{m}$ | $\text{mm}$ |
| $e$ | Chiều dài cạnh tam giác đều bàn di động $P_1 P_2 P_3$ | $\text{m}$ | $\text{mm}$ |
| $r_f$ | Chiều dài khâu chủ động / tay quay trên (*upper arm* $A_i B_i$) | $\text{m}$ | $\text{mm}$ |
| $r_e$ | Chiều dài khâu bị động song song / cẳng tay dưới (*lower arm* $B_i P_i$) | $\text{m}$ | $\text{mm}$ |
| $R_b$ | Bán kính tâm khớp đế cố định ($O A_i = f/\sqrt{3}$) | $\text{m}$ | $\text{mm}$ |
| $r_p$ | Bán kính tâm khớp bàn di động ($P P_i = e/\sqrt{3}$) | $\text{m}$ | $\text{mm}$ |
| $R$ | Hiệu bán kính hình học quy đổi ($R = R_b - r_p = (f - e)/\sqrt{3}$) | $\text{m}$ | $\text{mm}$ |
| $\phi_i$ | Góc định hướng nhánh thứ $i$ trong mặt phẳng $Oxy$ ($\phi_i \in \{0, 2\pi/3, 4\pi/3\}$) | $\text{rad}$ | $\text{deg}$ ($^\circ$) |
| $\theta_i$ | Góc khớp quay chủ động thứ $i$ (so với phương ngang $+O x_i$, dương khi quay xuống) | $\text{rad}$ | $\text{deg}$ ($^\circ$) |
| $\boldsymbol{\theta}$ | Vector biến khớp chủ động $\boldsymbol{\theta} = [\theta_1, \theta_2, \theta_3]^T$ | $\text{rad}$ | $\text{deg}$ ($^\circ$) |
| $\mathbf{p}$ | Vector tọa độ tâm bàn di động $\mathbf{p} = [x, y, z]^T$ trong hệ $Oxyz$ | $\text{m}$ | $\text{mm}$ |
| ${}^{(i)}\mathbf{p}$ | Vector tọa độ tâm bàn di động trong hệ địa phương nhánh $i$: $[x_i, y_i, z_i]^T$ | $\text{m}$ | $\text{mm}$ |
| $\mathbf{b}_i, \mathbf{c}_i$ | Tọa độ khớp khuỷu thực $B_i$ và tâm mặt cầu ảo $C_i = B_i - \overrightarrow{P P_i}$ | $\text{m}$ | $\text{mm}$ |
| $\mathbf{s}_i$ | Vector dọc thanh truyền cẳng tay $\mathbf{s}_i = \mathbf{p} - \mathbf{c}_i = \overrightarrow{B_i P_i}$ ($\|\mathbf{s}_i\|_2 = r_e$) | $\text{m}$ | $\text{mm}$ |
| $E_i, F_i, G_i$ | Các hệ số trung gian trong phương trình lượng giác động học nghịch nhánh $i$ | $\text{m}^2$ | $\text{mm}^2$ |
| $\Delta_i$ | Biệt thức tồn tại nghiệm động học nghịch của nhánh $i$ ($\Delta_i = E_i^2 + F_i^2 - G_i^2$) | $\text{m}^4$ | $\text{mm}^4$ |
| $t_i$ | Biến thế lượng giác nửa góc Weierstrass $t_i = \tan(\theta_i / 2)$ | $-$ | $-$ |
| $J_x$ | Ma trận Jacobian không gian thao tác ($3 \times 3$), hàng $i$ là $\mathbf{s}_i^T$ | $\text{m}$ | $\text{mm}$ |
| $J_\theta$ | Ma trận Jacobian không gian khớp ($3 \times 3$, đường chéo) | $\text{m}^2/\text{rad}$ | $\text{mm}^2/\text{rad}$ |
| $J$ | Ma trận Jacobian thuận toàn phần ($\dot{\mathbf{p}} = J \dot{\boldsymbol{\theta}} = J_x^{-1} J_\theta \dot{\boldsymbol{\theta}}$) | $\text{m}/\text{rad}$ | $\text{mm}/\text{rad}$ |
| $\hat{J}$ | Ma trận Jacobian không thứ nguyên chuẩn hóa theo $r_e$ và $r_f$ | $-$ | $-$ |
| $\kappa(\hat{J})$ | Số điều kiện (*condition number*) chuẩn Euclid của ma trận $\hat{J}$ | $-$ | $-$ |
| $\gamma_i$ | Góc truyền lực (*transmission angle*) giữa cẳng tay $\mathbf{s}_i$ và khâu chủ động | $\text{rad}$ | $\text{deg}$ ($^\circ$) |

---

## 2. Giả thiết

Mô hình động học được xây dựng dựa trên các giả thiết lý tưởng hoá có kiểm soát sau đây:

1. **Giả thiết vật rắn tuyệt đối (Rigid-body links):** Các khâu chủ động ($r_f$), thanh truyền song song ($r_e$), đế cố định ($f$) và bàn di động ($e$) không bị biến dạng đàn hồi dưới tác dụng của trọng lực và lực quán tính.
   - *Hệ quả của việc bỏ qua:* Khi gia tốc lớn hoặc tải nặng, độ võng đàn hồi của thanh carbon/nhôm làm sai lệch vị trí điểm cuối cỡ $0,05\text{–}0,2\text{ mm}$. Với ứng dụng gắp vật mẫu nhẹ (nhựa/bìa cứng vài chục gam) ở chu kỳ $1,5\text{–}1,8\text{ s}$, biến dạng đàn hồi là không đáng kể.
2. **Giả thiết hình học đối xứng danh định và không có khe hở khớp (Nominal geometry & zero backlash):** Ba nhánh cách đều nhau đúng $120^\circ$; hai thanh trong mỗi cơ cấu hình bình hành dài bằng nhau tuyệt đối ($r_e$) và luôn song song; các khớp cầu không có độ rơ (backlash) $[CẦN KIỂM CHỨNG\text{ — khi chế tạo thật cần đánh giá sai số lắp ráp theo Vischer \& Clavel 1998}]$.
   - *Hệ quả của việc bỏ qua:* Nhờ giả thiết cơ cấu hình bình hành lý tưởng, bàn di động luôn giữ nguyên hướng song song với mặt phẳng đế cố định $Oxy$ (triệt tiêu hoàn toàn 3 bậc tự do quay $\alpha = \beta = \gamma = 0$), giúp bài toán rút gọn chính xác về 3 bậc tự do tịnh tiến thuần tuý $(x, y, z)$. Trong thực tế in 3D / cắt laser (`PhuongHoai2023LowCostDelta`), khe hở khớp cầu rod-end có thể gây nghiêng bàn di động $\le 0,5^\circ$ và sai số tĩnh $0,2\text{–}0,8\text{ mm}$.
3. **Giả thiết chọn nhánh cấu hình duy nhất (Single assembly mode / Working mode):**
   - Với **Động học nghịch (IK):** Tại mỗi vị trí $(x, y, z)$, mỗi nhánh chủ động có 2 nghiệm toán học (khuỷu tay hướng ra ngoài *elbow-out* và khuỷu tay hướng vào trong *elbow-in*). Mô hình cố định chọn **nhánh khuỷu hướng ra ngoài** ($\cos\theta_i > 0$, tức $\theta_i \in (-\pi/2, \pi/2)$) cho cả 3 nhánh để tránh va chạm giữa các tay quay ở vùng tâm robot.
   - Với **Động học thuận (FK):** Giao của 3 mặt cầu cho 2 nghiệm đối xứng nhau qua mặt phẳng chứa 3 tâm cầu ảo $C_1 C_2 C_3$. Mô hình cố định chọn **nghiệm phía dưới đế cố định** ($z < 0$).
4. **Giả thiết giới hạn góc mở của khớp cầu và góc truyền lực cơ khí:** Các khớp cầu (ball joints / universal joints) trên thực tế chỉ cho phép góc lệch tối đa khoảng $\pm 40^\circ \div \pm 45^\circ$, và góc truyền lực $\gamma_i$ không được quá nhỏ (yêu cầu $\gamma_i \ge 25^\circ$) để tránh kẹt cơ khí.

---

## 3. Dẫn giải

Toàn bộ quá trình dẫn giải dưới đây được thực hiện từng bước từ hình học vector và đã được kiểm chứng đại số tự động bằng thư viện `SymPy` trong script `nghien-cuu/mo-hinh/kiem-chung-ik-fk.py` (hàm `verify_symbolic_derivation()`, sai số đại số bằng $0$ tuyệt đối).

### 3.1. Phép biến đổi tọa độ địa phương và phương trình khép kín vòng vector

Xét nhánh thứ $i$ ($i \in \{1, 2, 3\}$) với góc định hướng $\phi_i \in \{0, 2\pi/3, 4\pi/3\}$. Ma trận quay quanh trục $Oz$ từ hệ tọa độ địa phương $O x_i y_i z_i$ sang hệ tọa độ toàn cục $Oxyz$ là:
$$\mathbf{R}_z(\phi_i) = \begin{bmatrix} \cos\phi_i & -\sin\phi_i & 0 \\ \sin\phi_i & \cos\phi_i & 0 \\ 0 & 0 & 1 \end{bmatrix}, \qquad \mathbf{R}_z^{-1}(\phi_i) = \mathbf{R}_z^T(\phi_i) = \begin{bmatrix} \cos\phi_i & \sin\phi_i & 0 \\ -\sin\phi_i & \cos\phi_i & 0 \\ 0 & 0 & 1 \end{bmatrix} \tag{1}$$

Trong hệ tọa độ toàn cục $Oxyz$:
- Vị trí khớp chủ động $A_i$ trên đế cố định là:
  $$\mathbf{a}_i = \mathbf{R}_z(\phi_i) \begin{bmatrix} R_b \\ 0 \\ 0 \end{bmatrix} = \begin{bmatrix} R_b \cos\phi_i \\ R_b \sin\phi_i \\ 0 \end{bmatrix} \tag{2}$$
- Khi khâu chủ động $A_i B_i$ (chiều dài $r_f$) quay một góc $\theta_i$ (quy ước $\theta_i = 0$ khi nằm ngang hướng theo $+O x_i$, $\theta_i > 0$ khi quay xuống phía $-Oz$), vị trí khớp khuỷu $B_i$ là:
  $$\mathbf{b}_i(\theta_i) = \mathbf{R}_z(\phi_i) \begin{bmatrix} R_b + r_f \cos\theta_i \\ 0 \\ -r_f \sin\theta_i \end{bmatrix} = \begin{bmatrix} (R_b + r_f \cos\theta_i)\cos\phi_i \\ (R_b + r_f \cos\theta_i)\sin\phi_i \\ -r_f \sin\theta_i \end{bmatrix} \tag{3}$$
- Do bàn di động luôn tịnh tiến và giữ nguyên hướng song song với đế cố định, vector nối từ tâm bàn di động $P(x, y, z)$ tới khớp cầu $P_i$ luôn cố định:
  $$\mathbf{d}_i = \overrightarrow{P P_i} = \mathbf{R}_z(\phi_i) \begin{bmatrix} r_p \\ 0 \\ 0 \end{bmatrix} = \begin{bmatrix} r_p \cos\phi_i \\ r_p \sin\phi_i \\ 0 \end{bmatrix} \implies \mathbf{p}_i = \mathbf{p} + \mathbf{d}_i \tag{4}$$

Vector dọc theo cẳng tay song song thứ $i$ nối từ $B_i$ tới $P_i$ là:
$$\mathbf{s}_i = \overrightarrow{B_i P_i} = \mathbf{p}_i - \mathbf{b}_i(\theta_i) = \mathbf{p} - \big(\mathbf{b}_i(\theta_i) - \mathbf{d}_i\big) = \mathbf{p} - \mathbf{c}_i(\theta_i) \tag{5}$$
trong đó $\mathbf{c}_i(\theta_i)$ được gọi là **tâm mặt cầu ảo thứ $i$** (thu được bằng cách tịnh tiến khớp khuỷu $B_i$ vào phía tâm một đoạn $r_p$, thay $R_b$ bởi hiệu bán kính $R = R_b - r_p$):
$$\mathbf{c}_i(\theta_i) = \mathbf{b}_i(\theta_i) - \mathbf{d}_i = \mathbf{R}_z(\phi_i) \begin{bmatrix} R + r_f \cos\theta_i \\ 0 \\ -r_f \sin\theta_i \end{bmatrix} = \begin{bmatrix} (R + r_f \cos\theta_i)\cos\phi_i \\ (R + r_f \cos\theta_i)\sin\phi_i \\ -r_f \sin\theta_i \end{bmatrix} \tag{6}$$

Vì chiều dài cẳng tay luôn không đổi bằng $r_e$, phương trình ràng buộc hình học khép kín vòng vector của nhánh $i$ có dạng chuẩn:
$$\|\mathbf{s}_i\|_2^2 = \|\mathbf{p} - \mathbf{c}_i(\theta_i)\|_2^2 = r_e^2 \quad (i = 1, 2, 3) \tag{7}$$

---

### 3.2. Dẫn giải Động học Nghịch giải tích (Analytical Inverse Kinematics — IK)

**Bài toán:** Cho biết vị trí điểm tác động cuối $\mathbf{p} = [x, y, z]^T$, tìm ba góc khớp chủ động $\boldsymbol{\theta} = [\theta_1, \theta_2, \theta_3]^T$.

**Bước 1 — Chuyển sang hệ tọa độ địa phương nhánh $i$:**  
Do phép quay $\mathbf{R}_z^T(\phi_i)$ là phép biến đổi trực giao bảo toàn khoảng cách Euclid, ta chiếu phương trình (7) vào hệ tọa độ địa phương $O x_i y_i z_i$. Đặt tọa độ của $\mathbf{p}$ trong hệ địa phương nhánh $i$ là:
$$\begin{bmatrix} x_i \\ y_i \\ z_i \end{bmatrix} = \mathbf{R}_z^T(\phi_i) \begin{bmatrix} x \\ y \\ z \end{bmatrix} = \begin{bmatrix} x \cos\phi_i + y \sin\phi_i \\ -x \sin\phi_i + y \cos\phi_i \\ z \end{bmatrix} \tag{8}$$
Trong hệ tọa độ này, tâm cầu ảo $\mathbf{c}_i(\theta_i)$ có tọa độ địa phương là $[R + r_f \cos\theta_i,\ 0,\ -r_f \sin\theta_i]^T$. Phương trình (7) trở thành:
$$\big(x_i - (R + r_f \cos\theta_i)\big)^2 + (y_i - 0)^2 + \big(z_i + r_f \sin\theta_i\big)^2 = r_e^2 \tag{9}$$

*Điều kiện cần về độ lệch ngang:* Từ (9), ta có $\big(x_i - R - r_f\cos\theta_i\big)^2 + (z_i + r_f\sin\theta_i)^2 = r_e^2 - y_i^2$. Để tồn tại nghiệm thực, độ lệch ngang $y_i$ của bàn di động so với mặt phẳng nhánh $i$ không được vượt quá chiều dài cẳng tay:
$$r_e^2 - y_i^2 \ge 0 \iff |y_i| \le r_e \tag{10}$$

**Bước 2 — Khai triển thành phương trình lượng giác tuyến tính theo $\cos\theta_i$ và $\sin\theta_i$:**  
Khai triển bình phương trong phương trình (9):
$$(x_i - R)^2 - 2 r_f (x_i - R)\cos\theta_i + r_f^2 \cos^2\theta_i + y_i^2 + z_i^2 + 2 r_f z_i \sin\theta_i + r_f^2 \sin^2\theta_i - r_e^2 = 0 \tag{11}$$
Sử dụng hằng đẳng thức $\cos^2\theta_i + \sin^2\theta_i = 1$, phương trình (11) rút gọn về dạng chuẩn:
$$E_i \cos\theta_i + F_i \sin\theta_i + G_i = 0 \tag{12}$$
với các hệ số trung gian (đơn vị: $\text{m}^2$ hoặc $\text{mm}^2$):
$$\left\{ \begin{aligned} E_i &= -2 r_f (x_i - R) \\ F_i &= 2 r_f z_i \\ G_i &= (x_i - R)^2 + y_i^2 + z_i^2 + r_f^2 - r_e^2 \end{aligned} \right. \tag{13}$$

**Bước 3 — Giải phương trình bằng phép thế nửa góc Weierstrass:**  
Đặt $t_i = \tan\left(\frac{\theta_i}{2}\right)$ (với $\theta_i \ne \pi + 2k\pi$). Khi đó:
$$\cos\theta_i = \frac{1 - t_i^2}{1 + t_i^2}, \qquad \sin\theta_i = \frac{2 t_i}{1 + t_i^2} \tag{14}$$
Thay (14) vào (12) và nhân cả hai vế với $(1 + t_i^2) > 0$:
$$E_i (1 - t_i^2) + 2 F_i t_i + G_i (1 + t_i^2) = 0 \iff (G_i - E_i) t_i^2 + 2 F_i t_i + (G_i + E_i) = 0 \tag{15}$$

**Bước 4 — Điều kiện tồn tại nghiệm (Biệt thức $\Delta_i$) và cách chọn nhánh khuỷu hướng ra ngoài:**  
Biệt thức rút gọn ($\Delta'_i = \Delta_i$) của phương trình bậc hai (15) là:
$$\Delta_i = F_i^2 - (G_i - E_i)(G_i + E_i) = E_i^2 + F_i^2 - G_i^2 \tag{16}$$
- **Điều kiện tồn tại nghiệm IK:** Điểm $\mathbf{p}(x,y,z)$ thuộc không gian khả đạt toán học của robot khi và chỉ khi:
  $$\Delta_i = E_i^2 + F_i^2 - G_i^2 \ge 0, \quad \forall i \in \{1, 2, 3\} \tag{17}$$
- Khi $\Delta_i \ge 0$, phương trình (15) có hai nghiệm:
  $$t_i^{(-)} = \frac{-F_i - \sqrt{\Delta_i}}{G_i - E_i}, \qquad t_i^{(+)} = \frac{-F_i + \sqrt{\Delta_i}}{G_i - E_i} \tag{18}$$
- **Phân tích vật lý để chọn nhánh nghiệm đúng (Elbow-out):**  
  Trong vùng làm việc phía dưới đế ($z_i = z < 0$), ta có $F_i = 2 r_f z < 0 \implies -F_i > 0$.  
  - Nghiệm $t_i^{(+)}$ có tử số $-F_i + \sqrt{\Delta_i}$ lớn, cho $|t_i^{(+)}| > 1 \implies |\theta_i^{(+)}| > 90^\circ$ ($\cos\theta_i^{(+)} < 0$): khâu chủ động gập ngược vào trong lòng đế robot (*elbow-in*).
  - Nghiệm $t_i^{(-)}$ có $|t_i^{(-)}| < 1 \implies \theta_i^{(-)} \in (-90^\circ, 90^\circ)$ ($\cos\theta_i^{(-)} > 0$): khớp khuỷu $B_i$ có bán kính hướng kính $R_b + r_f\cos\theta_i > R_b$, tức **khuỷu tay hướng ra ngoài (elbow-out)**.
- **Công thức tính ổn định số học (Citardauq / Viète) tránh hủy chữ số có nghĩa:**  
  Khi $x_i \approx R$ và $y_i^2 + z_i^2 \approx r_e^2 - r_f^2$, hệ số bậc hai $a_t = G_i - E_i \to 0$. Nếu dùng trực tiếp công thức $t_i^{(-)} = (-F_i - \sqrt{\Delta_i})/(G_i - E_i)$ sẽ xảy ra phép trừ hai số thực dấu phẩy động gần bằng nhau ở tử số chia cho mẫu số rất nhỏ, làm mất $3\text{–}4$ chữ số thập phân (sai số vòng kín nhảy lên $\sim 10^{-10}\text{ mm}$). Áp dụng định lý Viète $t_i^{(-)} t_i^{(+)} = \frac{G_i + E_i}{G_i - E_i}$, vì $-F_i > 0$ (do $z < 0$), đại lượng $-F_i + \sqrt{\Delta_i} = |F_i| + \sqrt{\Delta_i} > 0$ hoàn toàn không bị hủy số và luôn khác $0$. Do đó nghiệm nhánh khuỷu ngoài được tính chính xác đến giới hạn máy ($\sim 10^{-14}\text{ mm}$) bằng công thức:
  $$t_i = \frac{-F_i - \sqrt{E_i^2 + F_i^2 - G_i^2}}{G_i - E_i} \equiv \frac{G_i + E_i}{-F_i + \sqrt{E_i^2 + F_i^2 - G_i^2}}, \qquad \theta_i = 2 \arctan(t_i) \tag{19}$$

---

### 3.3. Dẫn giải Động học Thuận (Forward Kinematics — FK)

**Bài toán:** Cho biết ba góc khớp chủ động $\boldsymbol{\theta} = [\theta_1, \theta_2, \theta_3]^T$, tìm tọa độ điểm tác động cuối $\mathbf{p} = [x, y, z]^T$.

Từ (6), khi biết $\theta_i$, tọa độ 3 tâm cầu ảo $\mathbf{c}_i = [x_{Ci}, y_{Ci}, z_{Ci}]^T$ hoàn toàn xác định:
$$x_{Ci} = (R + r_f \cos\theta_i)\cos\phi_i, \quad y_{Ci} = (R + r_f \cos\theta_i)\sin\phi_i, \quad z_{Ci} = -r_f \sin\theta_i \quad (i = 1, 2, 3) \tag{20}$$

Điểm tác động cuối $\mathbf{p}(x,y,z)$ là giao điểm của 3 mặt cầu có tâm $\mathbf{c}_i$ và cùng bán kính $r_e$:
$$(x - x_{Ci})^2 + (y - y_{Ci})^2 + (z - z_{Ci})^2 = r_e^2 \quad (i = 1, 2, 3) \tag{21}$$

#### (a) Phương pháp giải tích / Khử đại số (Analytical Trilateration)

**Bước 1 — Khử bậc hai bằng phép trừ từng cặp phương trình mặt cầu:**  
Khai triển (21) dưới dạng:
$$x^2 + y^2 + z^2 - 2 x_{Ci} x - 2 y_{Ci} y - 2 z_{Ci} z = r_e^2 - w_i, \qquad \text{với } w_i = x_{Ci}^2 + y_{Ci}^2 + z_{Ci}^2 \tag{22}$$
Lấy phương trình ($i = 1$) trừ đi phương trình ($i = 2$) và ($i = 3$), các số hạng bậc hai $(x^2 + y^2 + z^2)$ và $r_e^2$ triệt tiêu hoàn toàn, thu được hệ 2 mặt phẳng cắt nhau (giao tuyến là đường thẳng đi qua tâm đường tròn ngoại tiếp $\triangle C_1 C_2 C_3$ và vuông góc với mặt phẳng $\triangle C_1 C_2 C_3$):
$$\left\{ \begin{aligned} a_{21} x + b_{21} y + c_{21} z &= d_{21} \\ a_{31} x + b_{31} y + c_{31} z &= d_{31} \end{aligned} \right. \tag{23}$$
trong đó:
$$\begin{aligned} a_{j1} &= x_{Cj} - x_{C1}, & b_{j1} &= y_{Cj} - y_{C1}, & c_{j1} &= z_{Cj} - z_{C1}, & d_{j1} &= \frac{w_j - w_1}{2} \quad (j \in \{2, 3\}) \end{aligned} \tag{24}$$

**Bước 2 — Biểu diễn tuyến tính $x(z)$ và $y(z)$:**  
Định thức của hệ 2 ẩn $(x, y)$ trong (23) là $D = a_{21} b_{31} - a_{31} b_{21}$ (bằng $2$ lần diện tích có hướng của hình chiếu tam giác $\triangle C_1 C_2 C_3$ xuống mặt phẳng $Oxy$). Vì 3 nhánh lệch nhau $120^\circ$ và $\theta_i \in (-90^\circ, 90^\circ)$, 3 tâm cầu không bao giờ thẳng hàng nên $D \ne 0$ trên toàn vùng làm việc. Theo quy tắc Cramer, ta biểu diễn được $x$ và $y$ theo biến độc lập $z$:
$$x = u_x + v_x z, \qquad y = u_y + v_y z \tag{25}$$
với:
$$u_x = \frac{b_{31} d_{21} - b_{21} d_{31}}{D}, \quad v_x = \frac{b_{21} c_{31} - b_{31} c_{21}}{D}, \quad u_y = \frac{a_{21} d_{31} - a_{31} d_{21}}{D}, \quad v_y = \frac{a_{31} c_{21} - a_{21} c_{31}}{D} \tag{26}$$

**Bước 3 — Thế vào phương trình mặt cầu thứ nhất và chọn nghiệm vật lý ($z < 0$):**  
Thay (25) vào phương trình mặt cầu $i = 1$ trong (21), ta nhận được phương trình bậc hai một ẩn theo $z$:
$$A_q z^2 + B_q z + C_q = 0 \tag{27}$$
với:
$$\left\{ \begin{aligned} A_q &= v_x^2 + v_y^2 + 1 > 0 \\ B_q &= 2 \big[ v_x (u_x - x_{C1}) + v_y (u_y - y_{C1}) - z_{C1} \big] \\ C_q &= (u_x - x_{C1})^2 + (u_y - y_{C1})^2 + z_{C1}^2 - r_e^2 \end{aligned} \right. \tag{28}$$
Khi biệt thức $\Delta_z = B_q^2 - 4 A_q C_q \ge 0$, phương trình (27) có 2 nghiệm ứng với 2 điểm đối xứng qua mặt phẳng $\triangle C_1 C_2 C_3$. Vì bàn di động của robot Delta luôn treo phía dưới đế cố định ($z < z_{Ci} \le 0$), nghiệm vật lý duy nhất là **nghiệm có cao độ $z$ nhỏ hơn** (dấu $-$ trước căn thức):
$$z = \frac{-B_q - \sqrt{B_q^2 - 4 A_q C_q}}{2 A_q}, \qquad x = u_x + v_x z, \qquad y = u_y + v_y z \tag{29}$$

#### (b) Phương pháp giải số lặp Newton–Raphson (Iterative Numerical Method)

Để kiểm chứng độc lập công thức giải tích (29) theo hướng tiếp cận của Yang & Xiao (2024) [5], đặt vector hàm mục tiêu phi tuyến $\mathbf{F}(\mathbf{p}) = [F_1(\mathbf{p}), F_2(\mathbf{p}), F_3(\mathbf{p})]^T = \mathbf{0}$:
$$F_i(x, y, z) = (x - x_{Ci})^2 + (y - y_{Ci})^2 + (z - z_{Ci})^2 - r_e^2 = 0 \quad (i = 1, 2, 3) \tag{30}$$
Ma trận đạo hàm riêng (Jacobian của hệ phương trình đại số) $\mathbf{J}_F(\mathbf{p}) = \frac{\partial \mathbf{F}}{\partial \mathbf{p}} \in \mathbb{R}^{3 \times 3}$ có dạng rất gọn:
$$\mathbf{J}_F(\mathbf{p}) = 2 \begin{bmatrix} (x - x_{C1}) & (y - y_{C1}) & (z - z_{C1}) \\ (x - x_{C2}) & (y - y_{C2}) & (z - z_{C2}) \\ (x - x_{C3}) & (y - y_{C3}) & (z - z_{C3}) \end{bmatrix} = 2 J_x \tag{31}$$
Công thức cập nhật lặp Newton–Raphson tại bước thứ $k = 0, 1, 2, \dots$:
$$\mathbf{p}^{(k+1)} = \mathbf{p}^{(k)} - \big[\mathbf{J}_F(\mathbf{p}^{(k)})\big]^{-1} \mathbf{F}(\mathbf{p}^{(k)}) \tag{32}$$

- **Điều kiện chọn đúng nhánh và hội tụ bậc hai (Quadratic convergence):**
  1. **Chọn điểm khởi tạo $\mathbf{p}^{(0)}$:** Chọn $\mathbf{p}^{(0)} = [0,\ 0,\ -350\text{ mm}]^T$ nằm ngay tâm vùng làm việc phía dưới ($z^{(0)} < 0$). Vì hàm $\mathbf{F}(\mathbf{p})$ là đa thức bậc hai lồi theo từng mặt cầu và mặt phẳng phân chia hai nhánh nghiệm nằm ở cao độ $z \approx -r_f\sin\theta_i \in [-195, +90]\text{ mm}$, việc khởi tạo tại $z^{(0)} = -350\text{ mm}$ đảm bảo miền hút (basin of attraction) luôn hội tụ về đúng nhánh dưới ($z < 0$). Nếu ở một bước trung gian bất kỳ xảy ra $z^{(k)} > 0$, thuật toán tự động lấy đối xứng lại xuống nửa không gian $z < 0$.
  2. **Điều kiện khả nghịch:** Theo định lý Kantorovich, thuật toán hội tụ bậc hai khi $\det(\mathbf{J}_F) = 8 \det(J_x) \ne 0$, tức $\mathbf{p}^{(k)}$ không nằm trên mặt phẳng chứa 3 tâm cầu $C_1, C_2, C_3$.
  3. **Tiêu chuẩn dừng:** $\|\mathbf{F}(\mathbf{p}^{(k)})\|_2 < \varepsilon_{\text{tol}} = 10^{-11}\text{ mm}^2$ hoặc $\|\Delta \mathbf{p}^{(k)}\|_2 < 10^{-11}\text{ mm}$.

---

### 3.4. Dẫn giải Ma trận Jacobian và Phân tích Điểm kỳ dị (Singularity Analysis)

Lấy đạo hàm theo thời gian hai vế phương trình ràng buộc vòng kín (7) $\|\mathbf{p} - \mathbf{c}_i(\theta_i)\|_2^2 - r_e^2 = 0$:
$$2 \big(\mathbf{p} - \mathbf{c}_i(\theta_i)\big)^T \left( \dot{\mathbf{p}} - \frac{\mathrm{d}\mathbf{c}_i}{\mathrm{d}\theta_i} \dot{\theta}_i \right) = 0 \iff \mathbf{s}_i^T \dot{\mathbf{p}} = \left( \mathbf{s}_i^T \frac{\mathrm{d}\mathbf{c}_i}{\mathrm{d}\theta_i} \right) \dot{\theta}_i \quad (i = 1, 2, 3) \tag{33}$$
Từ (6), đạo hàm của tâm cầu ảo $\mathbf{c}_i(\theta_i)$ theo góc khớp $\theta_i$ là vector tiếp tuyến quỹ đạo khuỷu tay $\mathbf{u}_{\theta, i}$ (có độ lớn bằng $r_f$):
$$\frac{\mathrm{d}\mathbf{c}_i}{\mathrm{d}\theta_i} = \mathbf{u}_{\theta, i} = \begin{bmatrix} -r_f \sin\theta_i \cos\phi_i \\ -r_f \sin\theta_i \sin\phi_i \\ -r_f \cos\theta_i \end{bmatrix} \tag{34}$$

Gom 3 phương trình ($i = 1, 2, 3$) trong (33) về dạng ma trận chuẩn của cơ cấu song song:
$$J_x \dot{\mathbf{p}} = J_\theta \dot{\boldsymbol{\theta}} \tag{35}$$
trong đó:
$$J_x = \begin{bmatrix} \mathbf{s}_1^T \\ \mathbf{s}_2^T \\ \mathbf{s}_3^T \end{bmatrix} = \begin{bmatrix} x - x_{C1} & y - y_{C1} & z - z_{C1} \\ x - x_{C2} & y - y_{C2} & z - z_{C2} \\ x - x_{C3} & y - y_{C3} & z - z_{C3} \end{bmatrix}, \qquad J_\theta = \operatorname{diag}(J_{\theta, 11}, J_{\theta, 22}, J_{\theta, 33}) \tag{36}$$
với phần tử đường chéo thứ $i$ của $J_\theta$ là:
$$J_{\theta, ii} = \mathbf{s}_i^T \mathbf{u}_{\theta, i} = -r_f \big[ \big((x - x_{Ci})\cos\phi_i + (y - y_{Ci})\sin\phi_i\big)\sin\theta_i + (z - z_{Ci})\cos\theta_i \big] \tag{37}$$

Khi $J_x$ và $J_\theta$ khả nghịch, **ma trận Jacobian thuận** $J$ và **ma trận Jacobian nghịch** $J^{-1}$ được xác định bởi:
$$\dot{\mathbf{p}} = J \dot{\boldsymbol{\theta}}, \quad J = J_x^{-1} J_\theta \qquad \text{và} \qquad \dot{\boldsymbol{\theta}} = J^{-1} \dot{\mathbf{p}}, \quad J^{-1} = J_\theta^{-1} J_x \tag{38}$$

Để đánh giá độ nhạy động học độc lập với đơn vị chiều dài, chia cả hai vế của (33) cho $r_e$ và tách bán kính quay $r_f$, ta có **ma trận Jacobian không thứ nguyên (chuẩn hóa)** $\hat{J}$ ánh xạ vận tốc dài đầu mút khuỷu tay $(r_f \dot{\boldsymbol{\theta}})$ sang vận tốc bàn di động $\dot{\mathbf{p}}$:
$$\hat{J}_x \dot{\mathbf{p}} = \hat{J}_\theta (r_f \dot{\boldsymbol{\theta}}) \implies \hat{J} = \hat{J}_x^{-1} \hat{J}_\theta, \qquad \text{với } \hat{J}_{x, i:} = \frac{\mathbf{s}_i^T}{r_e}, \quad \hat{J}_{\theta, ii} = \frac{\mathbf{s}_i^T \mathbf{u}_{\theta, i}}{r_e r_f} = \pm \sin\gamma_i \tag{39}$$
trong đó $\gamma_i \in [0^\circ, 90^\circ]$ là **góc truyền lực (transmission angle)** giữa thanh cẳng tay $\mathbf{s}_i$ và khâu chủ động $A_i B_i$ (vì $\mathbf{u}_{\theta, i}$ vuông góc với $A_i B_i$ trong mặt phẳng nhánh $i$).

**Phân loại 3 dạng điểm kỳ dị (Singularities) của robot Delta:**
1. **Kỳ dị động học nghịch / Kỳ dị nối tiếp (Inverse / Serial Singularity — Loại I):**
   - *Điều kiện toán học:* $\det(J_\theta) = 0 \iff \exists i \in \{1,2,3\}:\ J_{\theta, ii} = \mathbf{s}_i^T \mathbf{u}_{\theta, i} = 0 \iff \sin\gamma_i = 0$.
   - *Ý nghĩa vật lý:* Vector dọc cẳng tay $\mathbf{s}_i$ vuông góc với phương chuyển động của khuỷu tay $\mathbf{u}_{\theta, i}$, tức là khâu chủ động $A_i B_i$ và hình chiếu của cẳng tay $B_i P_i$ trên mặt phẳng nhánh $i$ **duỗi thẳng hàng** ($\gamma_i = 0^\circ$) hoặc **gập trùng nhau** ($\gamma_i = 180^\circ$). Đây chính là **biên bao ngoài của không gian làm việc** (nơi biệt thức $\Delta_i = 0$). Tại đây, một vận tốc khớp $\dot{\theta}_i \ne 0$ không tạo ra thành phần vận tốc dọc thanh truyền, robot mất 1 bậc tự do chuyển động hướng ra ngoài biên.
2. **Kỳ dị động học thuận / Kỳ dị song song (Forward / Parallel Singularity — Loại II):**
   - *Điều kiện toán học:* $\det(J_x) = \mathbf{s}_1 \cdot (\mathbf{s}_2 \times \mathbf{s}_3) = 0$.
   - *Ý nghĩa vật lý:* Ba vector cẳng tay $\mathbf{s}_1, \mathbf{s}_2, \mathbf{s}_3$ đồng phẳng (tức 3 thanh cẳng tay cùng nằm trong mặt phẳng $\triangle C_1 C_2 C_3$, xảy ra khi $z \approx z_{Ci}$). Khi đó bàn di động có thể dịch chuyển vô cùng bé theo phương pháp tuyến mà các động cơ đã khóa cứng ($\dot{\boldsymbol{\theta}} = \mathbf{0}$), lực nội trong thanh truyền tiến tới vô cùng và robot mất độ cứng vững hoàn toàn.
3. **Kỳ dị kết hợp (Combined Singularity — Loại III):** Xảy ra khi đồng thời $\det(J_\theta) = 0$ và $\det(J_x) = 0$.
4. **Kỳ dị cấu hình cơ cấu hình bình hành (Parallelogram Rotational Singularity):** Khi độ lệch ngang $|y_i| \to r_e$ (tức góc nghiêng ngang của cẳng tay đạt $90^\circ$), hình bình hành suy biến thành một đường thẳng và mất khả năng khống chế bậc tự do tự quay của bàn di động.

---

## 4. Mô hình

Tổng hợp hệ phương trình toán học chuẩn hóa của hệ động học robot Delta 3-DOF:

### 4.1. Mô hình Động học Vị trí (Position Kinematics)

- **Ánh xạ Động học Nghịch $\boldsymbol{\theta} = \mathcal{IK}(\mathbf{p})$:**
  $$\begin{aligned}
  &\begin{bmatrix} x_i \\ y_i \end{bmatrix} = \begin{bmatrix} \cos\phi_i & \sin\phi_i \\ -\sin\phi_i & \cos\phi_i \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix}, \quad z_i = z \\
  &E_i = -2 r_f (x_i - R), \quad F_i = 2 r_f z_i, \quad G_i = (x_i - R)^2 + y_i^2 + z_i^2 + r_f^2 - r_e^2 \\
  &\theta_i = 2 \arctan\left( \frac{G_i + E_i}{-F_i + \sqrt{E_i^2 + F_i^2 - G_i^2}} \right), \qquad i = 1, 2, 3
  \end{aligned} \tag{40}$$

- **Ánh xạ Động học Thuận $\mathbf{p} = \mathcal{FK}(\boldsymbol{\theta})$:**
  $$\begin{aligned}
  &\mathbf{c}_i(\theta_i) = \begin{bmatrix} (R + r_f \cos\theta_i)\cos\phi_i \\ (R + r_f \cos\theta_i)\sin\phi_i \\ -r_f \sin\theta_i \end{bmatrix}, \quad w_i = \|\mathbf{c}_i\|_2^2, \quad i = 1, 2, 3 \\
  &\begin{bmatrix} u_x & v_x \\ u_y & v_y \end{bmatrix} = \begin{bmatrix} x_{C2} - x_{C1} & y_{C2} - y_{C1} \\ x_{C3} - x_{C1} & y_{C3} - y_{C1} \end{bmatrix}^{-1} \begin{bmatrix} \frac{1}{2}(w_2 - w_1) & -(z_{C2} - z_{C1}) \\ \frac{1}{2}(w_3 - w_1) & -(z_{C3} - z_{C1}) \end{bmatrix} \\
  &z = \frac{-B_q - \sqrt{B_q^2 - 4 A_q C_q}}{2 A_q}, \quad x = u_x + v_x z, \quad y = u_y + v_y z
  \end{aligned} \tag{41}$$

### 4.2. Mô hình Vi phân và Phương trình Trạng thái Động học (State-Space Representation)

Ở cấp độ quy hoạch quỹ đạo và điều khiển động học vận tốc (kinematic velocity control), đặt vector trạng thái là vị trí điểm tác động cuối $\mathbf{x}_{\text{state}} = \mathbf{p} = [x, y, z]^T \in \mathbb{R}^3$, vector điều khiển là vận tốc góc các khớp chủ động $\mathbf{u} = \dot{\boldsymbol{\theta}} = [\dot{\theta}_1, \dot{\theta}_2, \dot{\theta}_3]^T \in \mathbb{R}^3$, và vector đầu ra đo lường là $\mathbf{y} = \mathbf{p} \in \mathbb{R}^3$.

Hệ phi tuyến chuẩn theo biến trạng thái:
$$\left\{ \begin{aligned} \dot{\mathbf{x}}_{\text{state}} &= J(\mathbf{x}_{\text{state}}, \boldsymbol{\theta}) \mathbf{u} = J_x^{-1}(\mathbf{x}_{\text{state}}, \boldsymbol{\theta}) J_\theta(\mathbf{x}_{\text{state}}, \boldsymbol{\theta}) \mathbf{u} \\ \mathbf{y} &= \mathbf{x}_{\text{state}} \end{aligned} \right. \tag{42}$$

Khi tuyến tính hóa quanh một điểm làm việc cân bằng tĩnh $(\mathbf{p}_0, \boldsymbol{\theta}_0, \mathbf{u}_0 = \mathbf{0})$ (ví dụ tâm vùng làm việc $\mathbf{p}_0 = [0, 0, -0,350]^T\text{ m}$), phương trình trạng thái vi phân tuyến tính hóa $\delta \dot{\mathbf{x}} = A \delta \mathbf{x} + B \delta \mathbf{u},\ \delta \mathbf{y} = C \delta \mathbf{x} + D \delta \mathbf{u}$ có các ma trận:
$$A = \mathbf{0}_{3 \times 3}, \qquad B = J(\mathbf{p}_0, \boldsymbol{\theta}_0) = J_x^{-1}(\mathbf{p}_0, \boldsymbol{\theta}_0) J_\theta(\mathbf{p}_0, \boldsymbol{\theta}_0), \qquad C = \mathbf{I}_{3 \times 3}, \qquad D = \mathbf{0}_{3 \times 3} \tag{43}$$

Tại điểm tâm tham chiếu $\mathbf{p}_0 = [0, 0, -350\text{ mm}]^T$ (với $\theta_{1,0} = \theta_{2,0} = \theta_{3,0} = 20,66^\circ = 0,3606\text{ rad}$), ma trận $B = J(\mathbf{p}_0, \boldsymbol{\theta}_0)$ tính bằng đơn vị $\text{mm/rad}$ (chia cho $1000$ để ra $\text{m/rad}$) là:
$$B = \begin{bmatrix} -148,79 & 74,40 & 74,40 \\ 0,00 & -128,86 & 128,86 \\ -78,56 & -78,56 & -78,56 \end{bmatrix} \text{ (mm/rad)} = \begin{bmatrix} -0,1488 & 0,0744 & 0,0744 \\ 0,0000 & -0,1289 & 0,1289 \\ -0,0786 & -0,0786 & -0,0786 \end{bmatrix} \text{ (m/rad)} \tag{44}$$

---

## 5. Tham số

### 5.1. Bảng tham số hình học và vùng làm việc đã sử dụng

Bộ tham số hình học đề xuất trong nhiệm vụ ($f = 346\text{ mm}, e = 115\text{ mm}, r_f = 200\text{ mm}, r_e = 400\text{ mm}$) **hoàn toàn bao phủ được hình trụ vùng làm việc yêu cầu $\varnothing 300 \times 150\text{ mm}$** mà **không cần phải thay đổi kích thước khâu**, với điều kiện đặt dải cao độ làm việc của hình trụ tại $z \in [-425, -275]\text{ mm}$.

| Tham số | Ký hiệu | Giá trị (SI) | Giá trị (mm / deg) | Nguồn / Ghi chú |
| --- | :---: | :---: | :---: | --- |
| Cạnh tam giác đều đế cố định | $f$ | $0,3460\text{ m}$ | $346,00\text{ mm}$ | **Giả định tham chiếu** (sẽ chốt theo BOM cơ khí) |
| Cạnh tam giác đều bàn di động | $e$ | $0,1150\text{ m}$ | $115,00\text{ mm}$ | **Giả định tham chiếu** (sẽ chốt theo BOM cơ khí) |
| Bán kính ngoại tiếp đế cố định | $R_b = f/\sqrt{3}$ | $0,1998\text{ m}$ | $199,7632\text{ mm}$ | Dẫn xuất từ $f$ ($\approx 200\text{ mm}$ theo đề bài) |
| Bán kính ngoại tiếp bàn di động | $r_p = e/\sqrt{3}$ | $0,0664\text{ m}$ | $66,3953\text{ mm}$ | Dẫn xuất từ $e$ ($\approx 66\text{ mm}$ theo đề bài) |
| Hiệu bán kính quy đổi | $R = R_b - r_p$ | $0,1334\text{ m}$ | $133,3679\text{ mm}$ | Dẫn xuất chính xác $(f - e)/\sqrt{3}$ |
| Chiều dài khâu chủ động (*upper arm*) | $r_f$ | $0,2000\text{ m}$ | $200,00\text{ mm}$ | **Giả định tham chiếu** (tỷ số $r_e / r_f = 2,0$) |
| Chiều dài cẳng tay bị động (*lower arm*) | $r_e$ | $0,4000\text{ m}$ | $400,00\text{ mm}$ | **Giả định tham chiếu** (thanh truyền carbon/nhôm) |
| Góc bố trí 3 nhánh chủ động | $\phi_1, \phi_2, \phi_3$ | $0, \frac{2\pi}{3}, \frac{4\pi}{3}\text{ rad}$ | $0^\circ, 120^\circ, 240^\circ$ | Cấu trúc đối xứng chuẩn Clavel [1] |
| Đường kính vùng làm việc tham chiếu | $D_{\text{ws}} = 2 R_{\text{ws}}$ | $0,3000\text{ m}$ | $300,00\text{ mm}$ | Chỉ tiêu bắt buộc trong `nghien-cuu/de-tai.md` |
| Chiều cao vùng làm việc tham chiếu | $H_{\text{ws}}$ | $0,1500\text{ m}$ | $150,00\text{ mm}$ | Chỉ tiêu bắt buộc trong `nghien-cuu/de-tai.md` |
| Dải tọa độ $z$ của hình trụ làm việc | $[z_{\min}, z_{\max}]$ | $[-0,425, -0,275]\text{ m}$ | $[-425,0, -275,0]\text{ mm}$ | Chọn tối ưu nằm trọn trong miền an toàn cơ khí |

---

## 6. Kiểm tra tính hợp lý

### 6.1. Kiểm tra Bậc tự do (Mobility / Degrees of Freedom)

Sử dụng công thức Kutzbach–Grübler tổng quát cho cơ cấu không gian kết hợp phân tích nhóm Assur / lý thuyết vít (Screw theory):
- Với mỗi cẳng tay hình bình hành, 2 thanh song song nối bằng 4 khớp cầu tạo thành một chuỗi ràng buộc giữ cho bàn di động luôn không quay ($\alpha = \beta = \gamma = 0$) nhưng cho phép 3 chuyển động tịnh tiến tương đối $(x, y, z)$.
- Về mặt động học vị trí tương đương, mỗi nhánh $i$ ($i = 1, 2, 3$) gồm 1 khớp quay chủ động $A_i$ (1 DOF) nối với một thanh truyền tương đương $B_i P_i$ có khớp cầu hai đầu, áp đặt đúng **1 phương trình ràng buộc khoảng cách vô hướng** $\|\mathbf{p} - \mathbf{c}_i(\theta_i)\|_2^2 = r_e^2$ lên 3 tọa độ tịnh tiến $(x, y, z)$ của bàn di động.
- Số bậc tự do tịnh tiến của bàn di động khi 3 khớp chủ động $(\theta_1, \theta_2, \theta_3)$ biến thiên tự do là:
  $$\text{DOF} = 3 \text{ (tọa độ } x, y, z\text{)} - 3 \text{ (ràng buộc nhánh)} + 3 \text{ (biến khớp chủ động } \theta_1, \theta_2, \theta_3\text{)} = 3\text{ DOF (tịnh tiến)}$$

### 6.2. Kiểm tra Thứ nguyên và Đơn vị hai vế (Dimensional Homogeneity)

1. **Trong phương trình IK (12)–(13):**
   - $[E_i] = [r_f] \cdot [x_i - R] = \text{m} \cdot \text{m} = \text{m}^2$.
   - $[F_i] = [r_f] \cdot [z_i] = \text{m} \cdot \text{m} = \text{m}^2$.
   - $[G_i] = [(x_i - R)^2 + y_i^2 + z_i^2 + r_f^2 - r_e^2] = \text{m}^2$.
   - $[\Delta_i] = [E_i^2 + F_i^2 - G_i^2] = \text{m}^4 \implies [\sqrt{\Delta_i}] = \text{m}^2$.
   - $[t_i] = \frac{[\text{m}^2]}{[\text{m}^2]} = 1$ (không thứ nguyên), khớp hoàn toàn với $[\tan(\theta_i/2)] = 1$.
2. **Trong phương trình FK (23)–(29):**
   - $[w_i] = \text{m}^2 \implies [d_{j1}] = \text{m}^2$; $[a_{j1}] = [b_{j1}] = [c_{j1}] = \text{m} \implies [D] = \text{m}^2$.
   - $[u_x] = [u_y] = \frac{\text{m} \cdot \text{m}^2}{\text{m}^2} = \text{m}$; $[v_x] = [v_y] = \frac{\text{m} \cdot \text{m}}{\text{m}^2} = 1$ (không thứ nguyên).
   - $[A_q] = 1$; $[B_q] = \text{m}$; $[C_q] = \text{m}^2 \implies [z] = \frac{[-B_q - \sqrt{B_q^2 - 4 A_q C_q}]}{[2 A_q]} = \text{m}$.
3. **Trong phương trình vận tốc Jacobian (35):**
   - Vế trái: $[J_x \dot{\mathbf{p}}] = \text{m} \cdot (\text{m/s}) = \text{m}^2/\text{s}$.
   - Vế phải: $[J_\theta \dot{\boldsymbol{\theta}}] = (\text{m}^2/\text{rad}) \cdot (\text{rad/s}) = \text{m}^2/\text{s}$. Hai vế đồng nhất đơn vị tuyệt đối.

### 6.3. Kiểm tra Bảo toàn Công ảo / Đối ngẫu Tĩnh học – Động học (Virtual Work Principle)

Theo nguyên lý công ảo cho hệ lý tưởng không ma sát, công suất tức thời tại không gian khớp phải bằng công suất tại điểm tác động cuối:
$$P = \boldsymbol{\tau}^T \dot{\boldsymbol{\theta}} = \mathbf{F}_{\text{ext}}^T \dot{\mathbf{p}} = \mathbf{F}_{\text{ext}}^T J \dot{\boldsymbol{\theta}}, \quad \forall \dot{\boldsymbol{\theta}} \implies \boldsymbol{\tau} = J^T \mathbf{F}_{\text{ext}} = J_\theta^T J_x^{-T} \mathbf{F}_{\text{ext}} \tag{45}$$
trong đó $\boldsymbol{\tau} = [\tau_1, \tau_2, \tau_3]^T$ ($\text{N}\cdot\text{m}$) là mô-men tại 3 trục động cơ và $\mathbf{F}_{\text{ext}} = [F_x, F_y, F_z]^T$ ($\text{N}$) là lực tác dụng lên bàn di động. Kiểm tra đơn vị: $[J^T] \cdot [\mathbf{F}_{\text{ext}}] = (\text{m/rad}) \cdot \text{N} = \text{N}\cdot\text{m}$ (đúng bằng đơn vị mô-men xoắn).

### 6.4. Kết quả Kiểm chứng Chéo Thực tế bằng Script Python trên $1\,859$ Điểm Lưới

Script `nghien-cuu/mo-hinh/kiem-chung-ik-fk.py` đã được thực thi bằng `D:\Python312\python.exe` trên lưới trụ phân bố đều gồm **$1\,859$ điểm** ($11$ mặt cắt cao độ $z \in [-425, -275]\text{ mm}$ $\times$ $[1 \text{ điểm tâm} + 7 \text{ vòng bán kính } (r \in (0, 150]\text{ mm}) \times 24 \text{ góc phương vị}]$). Bảng số liệu thực đo (trích xuất từ `ket-qua/tom-tat-kiem-chung.json` và `ket-qua/sai-so-ik-fk.csv`):

| Chỉ tiêu kiểm chứng | Giá trị thực đo | Đánh giá so với mục tiêu đề cương |
| --- | :---: | --- |
| Kiểm chứng đại số bằng `SymPy` | Sai số đa thức $= 0$ | Khớp giải tích tuyệt đối |
| Tổng số điểm lưới trong hình trụ $\varnothing 300 \times 150\text{ mm}$ | $1\,859$ điểm | Vượt yêu cầu $\ge 1\,000$ điểm |
| Tỷ lệ điểm có nghiệm IK hợp lệ ($z \in [-425, -275]\text{ mm}$) | $1\,859 / 1\,859$ ($100,00\,\%$) | Bao phủ trọn vẹn $100\,\%$ vùng làm việc |
| Sai số vòng kín cực đại $\max \|\mathcal{FK}_{\text{ana}}(\mathcal{IK}(\mathbf{p})) - \mathbf{p}\|_2$ | $1,5826 \times 10^{-13}\text{ mm}$ | Nhỏ hơn ngưỡng $1\text{ mm}$ tới $10^{12}$ lần |
| Sai số căn quân phương $\text{RMSE}_{\text{ana}}$ | $6,9066 \times 10^{-14}\text{ mm}$ | Cấp độ nhiễu làm tròn dấu phẩy động 64-bit |
| Sai số vòng kín cực đại với FK Newton–Raphson | $1,8359 \times 10^{-13}\text{ mm}$ | Khớp hoàn toàn với phương pháp giải tích |
| Sai số căn quân phương $\text{RMSE}_{\text{NR}}$ | $6,4356 \times 10^{-14}\text{ mm}$ | Khớp hoàn toàn với phương pháp giải tích |
| Độ lệch cực đại giữa 2 bộ giải $\max \|\mathbf{p}_{\text{ana}} - \mathbf{p}_{\text{NR}}\|_2$ | $1,7288 \times 10^{-13}\text{ mm}$ | Hai phương pháp hội tụ về cùng một nghiệm |
| Số điểm Newton–Raphson không hội tụ | $0 / 1\,859$ điểm ($0\,\%$) | Hội tụ $100\,\%$ (trung bình $5,73$ vòng lặp, tối đa $6$ vòng) |
| Dải góc khớp chủ động $\theta_i$ trong hình trụ $\varnothing 300 \times 150\text{ mm}$ | $[-27,05^\circ,\ +77,30^\circ]$ | Nằm gọn trong giới hạn cơ khí $[-40^\circ, +85^\circ]$ |
| Góc truyền lực nhỏ nhất $\gamma_{\min}$ | $39,00^\circ$ | Rất an toàn ($\ge 25^\circ$, cách xa biên kỳ dị $\gamma = 0^\circ$) |
| Số điều kiện Jacobian chuẩn hóa $\kappa(\hat{J})$ | $\min = 1,013;\ \max = 1,981$ (TB: $1,403$) | Hệ đẳng hướng tốt ($\kappa < 2,0$), không có kỳ dị bên trong |

**Các hình vẽ xuất bản (300 dpi) đã sinh tự động:**
- `nghien-cuu/mo-hinh/ket-qua/ban-do-sai-so-xy.png`: Bản đồ nhiệt sai số vòng kín IK↔FK ($\sim 10^{-13}\text{ mm}$) và đường đồng mức số điều kiện Jacobian $\kappa(\hat{J})$ trên mặt phẳng ngang $z = -350\text{ mm}$.
- `nghien-cuu/mo-hinh/ket-qua/mat-cat-vung-lam-viec.png`: Mặt cắt đứng vùng làm việc trong mặt phẳng $Oxz$ ($y = 0$) và đồ thị bán kính hình trụ nội tiếp tối đa $R_{\max}(z)$ chứng minh hình trụ $\varnothing 300 \times 150\text{ mm}$ nằm lọt hoàn toàn trong vùng làm việc an toàn.

### 6.5. Khảo sát Độ nhạy Sai số Hình học bằng Mô phỏng Monte Carlo

*(Lưu ý minh bạch phương pháp: Toàn bộ số liệu trong mục này là kết quả **mô phỏng Monte Carlo trên máy tính** bằng script `nghien-cuu/mo-hinh/do-nhay-hinh-hoc.py` theo tinh thần mô hình sai số hình học của Vischer & Clavel (1998) [2], **không phải số đo thực nghiệm trên khung robot thật**).*

#### (a) Lý do thực hiện và mô hình toán học của sai số chế tạo
Sai số vòng kín $\max \|\mathcal{FK}(\mathcal{IK}(\mathbf{p})) - \mathbf{p}\|_2 = 1,5826 \times 10^{-13}\text{ mm}$ ở mục 6.4 chỉ chứng minh $\mathcal{FK}$ và $\mathcal{IK}$ là cặp hàm nghịch đảo chính xác trong mã nguồn. Trong thực tế, bộ điều khiển tính góc khớp đặt $\boldsymbol{\theta}_{\text{nom}} = \mathcal{IK}(\mathbf{p}_{\text{nom}}, \boldsymbol{\lambda}_0)$ dựa trên bộ tham số danh nghĩa $\boldsymbol{\lambda}_0 = (f_0, e_0, r_{f0}, r_{e0})$, nhưng cơ khí thực tế của từng nhánh $i \in \{1, 2, 3\}$ lại mang sai số chế tạo và lắp ráp $\Delta \boldsymbol{\lambda}_i$:
- Chiều dài thực của tay quay chủ động và cẳng tay nhánh $i$: $r_{f,i} = r_{f0} + \Delta r_{f,i}$, $r_{e,i} = r_{e0} + \Delta r_{e,i}$.
- Kích thước cạnh đế cố định và bàn di động tại nhánh $i$: $f_i = f_0 + \Delta f_i$, $e_i = e_0 + \Delta e_i$.
- Sai lệch vị trí lắp đặt ổ trục khớp đế $A_i$ theo phương hướng kính $\Delta R_{b,i}$ và phương thẳng đứng $\Delta z_{A,i}$.

Khi đó, tâm mặt cầu ảo thực tế của nhánh $i$ dịch chuyển tới:
$$\tilde{\mathbf{c}}_i(\theta_{\text{nom},i}) = \begin{bmatrix} (\tilde{R}_i + r_{f,i} \cos\theta_{\text{nom},i})\cos\phi_i \\ (\tilde{R}_i + r_{f,i} \cos\theta_{\text{nom},i})\sin\phi_i \\ \Delta z_{A,i} - r_{f,i} \sin\theta_{\text{nom},i} \end{bmatrix}, \qquad \text{với } \tilde{R}_i = \frac{f_0 + \Delta f_i - (e_0 + \Delta e_i)}{\sqrt{3}} + \Delta R_{b,i} \tag{46}$$
và 3 mặt cầu giao nhau có bán kính khác nhau $r_{e,1} \ne r_{e,2} \ne r_{e,3}$:
$$\|\mathbf{p}_{\text{thực}} - \tilde{\mathbf{c}}_i(\theta_{\text{nom},i})\|_2^2 = r_{e,i}^2 \implies \tilde{w}_i = \|\tilde{\mathbf{c}}_i\|_2^2 - r_{e,i}^2, \quad d_{j1} = \frac{\tilde{w}_j - \tilde{w}_1}{2} \quad (j \in \{2, 3\}) \tag{47}$$
Sai số vị trí điểm cuối do dung sai hình học gây ra là:
$$e_{\text{pos}}(\mathbf{p}_{\text{nom}}, \Delta\boldsymbol{\lambda}) = \|\mathbf{p}_{\text{thực}} - \mathbf{p}_{\text{nom}}\|_2 = \big\|\mathcal{FK}(\mathcal{IK}(\mathbf{p}_{\text{nom}}, \boldsymbol{\lambda}_0), \boldsymbol{\lambda}_0 + \Delta\boldsymbol{\lambda}) - \mathbf{p}_{\text{nom}}\big\|_2 \tag{48}$$

#### (b) Thống kê phân vị Monte Carlo ở hai mức dung sai $\pm 0,2\text{ mm}$ và $\pm 0,5\text{ mm}$
Script `do-nhay-hinh-hoc.py` thực hiện $N_{\text{MC}} = 300$ lần rút mẫu bộ tham số robot ngẫu nhiên độc lập theo phân bố đều $\mathcal{U}(-\delta, +\delta)$ kết hợp quét trên $567$ điểm lưới phân bố đều trong hình trụ $\varnothing 300 \times 150\text{ mm}$ ($z \in [-425, -275]\text{ mm}$), tạo ra **$170\,100$ phép đánh giá** cho mỗi kịch bản. Kết quả trích xuất từ `ket-qua/tom-tat-do-nhay.json`:

| Kịch bản dung sai chế tạo (Mô phỏng Monte Carlo, $170\,100$ mẫu/kịch bản) | Trung bình Mean ($\text{mm}$) | RMSE ($\text{mm}$) | Trung vị P50 ($\text{mm}$) | Phân vị 95 % P95 ($\text{mm}$) | Phân vị 99 % P99 ($\text{mm}$) | Cực đại Max ($\text{mm}$) | Tỷ lệ mẫu đạt $\le 1,0\text{ mm}$ | Tỷ lệ vùng làm việc có $\text{P95} \le 1,0\text{ mm}$ |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mức 1a: $\pm 0,2\text{ mm}$** (4 tham số khâu $f, e, r_f, r_e$) | $0,243$ | $0,261$ | $0,236$ | $0,402$ | $0,476$ | $0,689$ | **$100,00\,\%$** | **$100,00\,\%$** |
| **Mức 1b: $\pm 0,2\text{ mm}$ toàn phần** ($f, e, r_f, r_e$ + lệch khớp đế $\Delta R_b, \Delta z_A \in \pm 0,2\text{ mm}$) | $0,304$ | $0,328$ | $0,297$ | $0,514$ | $0,604$ | $0,795$ | **$100,00\,\%$** | **$100,00\,\%$** |
| **Mức 2a: $\pm 0,5\text{ mm}$** (4 tham số khâu $f, e, r_f, r_e$) | $0,614$ | $0,659$ | $0,596$ | $1,030$ | $1,244$ | $1,681$ | $93,99\,\%$ | $31,57\,\%$ |
| **Mức 2b: $\pm 0,5\text{ mm}$ toàn phần** ($f, e, r_f, r_e$ + lệch khớp đế $\Delta R_b, \Delta z_A \in \pm 0,5\text{ mm}$) | $0,760$ | $0,822$ | $0,733$ | $1,321$ | $1,506$ | $2,410$ | $76,45\,\%$ | $0,00\,\%$ |

#### (c) Phân tích độ nhạy riêng từng tham số (One-at-a-Time / OAT Sensitivity Analysis)
Để xác định khâu nào cần kiểm soát dung sai nghiêm ngặt nhất khi lập bản vẽ CAD và BOM (Tuần 11), từng nhóm tham số được cho biến thiên độc lập trong khoảng $\pm 0,2\text{ mm}$ (các tham số còn lại giữ đúng danh nghĩa):

| Xếp hạng mức độ nhạy | Tham số khảo sát (biến thiên độc lập $\mathcal{U}(-0,2; +0,2)\text{ mm}$) | Trung vị P50 ($\text{mm}$) | Phân vị 95 % P95 ($\text{mm}$) | Phân vị 99 % P99 ($\text{mm}$) | Cực đại Max ($\text{mm}$) | Hệ số khuếch đại xấu nhất ($\text{mm/mm}$) | Giải thích cơ học |
| :---: | --- | :---: | :---: | :---: | :---: | :---: | --- |
| **1 (Nhạy nhất — nhóm lắp ráp)** | Vị trí ổ trục khớp đế ($\Delta R_{b,i}, \Delta z_{A,i}$) | $0,202$ | $0,312$ | $0,378$ | $0,515$ | $3,40$ | Gồm đồng thời 2 phương sai lệch (hướng kính $\Delta R_{b,i}$ và cao độ $\Delta z_{A,i}$) tác động trực tiếp lên tọa độ tâm cầu $\tilde{\mathbf{c}}_i$. |
| **2 (Nhạy nhất — nhóm kích thước khâu)** | Chiều dài cẳng tay song song ($r_e$) | $0,201$ | $0,291$ | $0,347$ | $0,434$ | $2,52$ | Thay đổi trực tiếp bán kính mặt cầu $r_{e,i}$; sai số truyền dọc theo phương thanh truyền với hệ số $\sim 1/\cos\alpha_i > 1$. |
| **3 (Trung bình)** | Chiều dài tay quay chủ động ($r_f$) | $0,058$ | $0,145$ | $0,174$ | $0,212$ | $1,16$ | Tác động qua $\cos\theta_i$ và $\sin\theta_i$, chỉ ảnh hưởng mạnh khi tay quay chúc xuống sâu ở biên vùng làm việc. |
| **4 (Ít nhạy hơn)** | Cạnh tam giác đế cố định ($f$) | $0,085$ | $0,131$ | $0,152$ | $0,181$ | $0,97$ | Khi quy đổi từ cạnh tam giác đều sang bán kính ngoại tiếp ($R_b = f/\sqrt{3}$), sai số $\Delta f$ được chia giảm đi $\sqrt{3} \approx 1,732$ lần. |
| **5 (Ít nhạy hơn)** | Cạnh tam giác bàn di động ($e$) | $0,083$ | $0,128$ | $0,151$ | $0,180$ | $0,97$ | Tương tự $f$, sai số $\Delta e$ được chia giảm đi $\sqrt{3}$ lần trong hiệu bán kính $R = (f - e)/\sqrt{3}$. |

**Kết luận kỹ thuật rút ra từ khảo sát độ nhạy (Hình `ket-qua/do-nhay-sai-so-hinh-hoc.png`):**
1. **Với dung sai $\pm 0,2\text{ mm}$:** **100 % vùng làm việc** ($\varnothing 300 \times 150\text{ mm}$) đạt sai số vị trí $\le 1,0\text{ mm}$ ngay cả trong trường hợp xấu nhất ($\text{Max} = 0,689\text{ mm}$ khi xét 4 khâu; $\text{Max} = 0,795\text{ mm}$ và $\text{P95} = 0,514\text{ mm}$ khi cộng thêm sai lệch lắp đặt khớp đế $\pm 0,2\text{ mm}$). Khoảng dự trữ sai số còn lại ($1,0 - 0,514 \approx 0,486\text{ mm}$) đủ để bù cho sai số xác lập của bộ điều khiển PID và độ phân giải xung của động cơ.
2. **Với dung sai $\pm 0,5\text{ mm}$:** Sai số phân vị 95 % vượt ngưỡng $1,0\text{ mm}$ ($\text{P95} = 1,030\text{ mm}$ với 4 khâu và $\text{P95} = 1,321\text{ mm}$, $\text{Max} = 2,410\text{ mm}$ khi có lệch khớp đế), khiến tỷ lệ vùng làm việc đảm bảo độ tin cậy 95 % ($\text{P95} \le 1,0\text{ mm}$) sụt xuống chỉ còn **$31,57\,\%$** (và **$0\,\%$** nếu tính cả lệch khớp đế $\pm 0,5\text{ mm}$).
3. **Khuyến nghị thiết kế cơ khí (CAD/BOM):** Tham số khâu nhạy nhất là **chiều dài cẳng tay $r_e$** ($\text{P95} = 0,291\text{ mm}$) và **vị trí lắp đặt ổ trục khớp đế** ($\text{P95} = 0,312\text{ mm}$). Do đó, khi chế tạo thực tế phải dùng **đồ gá (jig) cố định khoảng cách tâm 2 đầu khớp cầu rod-end của 6 thanh cẳng tay $r_e$ đồng đều trong phạm vi $\pm 0,15\text{ mm}$** và cắt CNC/laser tấm đế cố định liền khối để định vị chính xác 3 cụm ổ trục $A_1, A_2, A_3$.

### 6.6. Các điểm cần lưu ý / chưa chắc chắn cần kiểm chứng tiếp

1. **`[CẦN KIỂM CHỨNG]` Sai số động học do độ phân giải góc khớp và khe hở khớp cầu (Backlash):** Mô phỏng Monte Carlo ở mục 6.5 đã giải quyết định lượng bài toán dung sai kích thước tĩnh, nhưng chưa cộng độ rơ dọc trục của khớp cầu (ball-joint clearance) và bước lượng tử hóa PWM của servo/stepper. Cần cộng thêm thành phần này trong mô phỏng điều khiển ở bước tiếp theo.
2. **Giới hạn trần vùng làm việc ($z > -265\text{ mm}$):** Như thể hiện trên Hình 2b (`mat-cat-vung-lam-viec.png`), nếu đẩy cao độ bàn di động lên quá cao ($z > -250\text{ mm}$), góc khớp $\theta_i$ sẽ vượt quá $-40^\circ$ (tay quay hướng lên trên quá cao, dễ va chạm khung đế) làm bán kính khả dụng $R_{\max,\text{safe}}(z)$ thu hẹp nhanh chóng từ $245\text{ mm}$ xuống dưới $150\text{ mm}$. Do đó, khi lắp đặt băng tải và bàn gắp, mặt phẳng gắp–thả bắt buộc phải đặt trong dải $z \in [-425, -275]\text{ mm}$.

---

## 7. Thiết kế điều khiển

*(Để trống theo đúng yêu cầu phân công của nhiệm vụ — Phần quy hoạch quỹ đạo đa thức bậc 5 và thiết kế bộ điều khiển PID / PID + Feed-forward kèm chỉ tiêu thời gian xác lập, độ vọt lố $\le 5\,\%$, và chu kỳ chuyển động $\le 1,5\text{ s}$ sẽ được thực hiện ở bước tiếp theo sau khi chốt mô hình động học này).*

---

## Tài liệu tham khảo (Trích từ `nghien-cuu/tai-lieu/references.bib`)

1. R. Clavel, "Delta, a fast robot with parallel geometry," in *Proc. 18th Int. Symp. Industrial Robots*, 1988, pp. 91–100. `[CẦN KIỂM CHỨNG]`
2. P. Vischer and R. Clavel, "Kinematic calibration of the parallel Delta robot," *Robotica*, vol. 16, no. 2, pp. 207–218, 1998, doi: `10.1017/S0263574798000538`.
3. L. A. Castañeda, A. Luviano-Juárez, and I. Chairez, "Robust Trajectory Tracking of a Delta Robot Through Adaptive Active Disturbance Rejection Control," *IEEE Transactions on Control Systems Technology*, vol. 23, no. 4, pp. 1387–1398, 2015, doi: `10.1109/TCST.2014.2367313`.
4. C. Liu, Y. Cheng, D. Liu, G. Cao, and I. Lee, "Research on a LADRC Strategy for Trajectory Tracking Control of Delta High-Speed Parallel Robots," *Mathematical Problems in Engineering*, vol. 2020, p. 9681530, 2020, doi: `10.1155/2020/9681530`.
5. H. Yang and B. Xiao, "Kinematics Analysis of Delta Parallel Robot Based on Numerical Solutions Method," in *Proc. Int. Conf. Artificial Intelligence and Digital Technology (ICAIDT)*, 2024, pp. 294–297, doi: `10.1109/ICAIDT62617.2024.00070`.
6. A. Elassal, M. Abdelaal, M. Osama, and H. Elhnidy, "Low-cost parallel delta robot for a pick-and-place application with the support of the vision system," *e-Prime — Advances in Electrical Engineering, Electronics and Energy*, vol. 8, p. 100518, 2024, doi: `10.1016/j.prime.2024.100518`.
7. P. Hoai, V. Cong, and T. Hiep, "Design a low-cost delta robot arm for pick and place applications based on computer vision," *FME Transactions*, vol. 51, no. 1, pp. 99–108, 2023, doi: `10.5937/fme2301099p`.
8. D. C. Vo and H. P. Le, "Design and development of a delta robot system to classify objects using image processing," *International Journal of Electrical and Computer Engineering (IJECE)*, vol. 13, no. 3, pp. 2669–2676, 2023, doi: `10.11591/ijece.v13i3.pp2669-2676`.
