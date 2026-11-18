# Hướng dẫn Lắp ráp, Căn chỉnh theo Độ nhạy và Quy trình Hiệu chuẩn Robot Delta 3-DOF

Thư mục `nghien-cuu/thiet-ke/` chứa toàn bộ hồ sơ thiết kế cơ khí được chuyển hóa trực tiếp từ mô hình toán học (`nghien-cuu/mo-hinh/dong-hoc-delta.md`), khảo sát độ nhạy Monte Carlo (`nghien-cuu/mo-hinh/do-nhay-hinh-hoc.py`), kết quả mô phỏng động lực học PID (`nghien-cuu/mo-phong/runs/2026-11-18-pid-quy-dao-bac5/output/metrics.json`) và cấu hình phần cứng nhúng (`nghien-cuu/firmware/uno-serial-servo/config.h`).

## 1. Cấu trúc hồ sơ thiết kế trong thư mục

| Tệp tài liệu | Nội dung chính |
| --- | --- |
| `thong-so-co-khi.md` | Bảng kích thước hình học chốt, lựa chọn vật liệu (liên hệ mô-men quán tính $J_{\text{eq}}$ và $\tau_{\max}$), kết cấu khớp quay – khớp cầu hình bình hành, bảng dung sai chế tạo dẫn từ độ nhạy và phương án gia công. |
| `BOM.md` | Tính chọn động cơ theo $\tau_{\max} = 0,457\text{ N}\cdot\text{m}$ với hệ số an toàn $\ge 2$, bảng dự toán vật tư – linh kiện (giá tham khảo VNĐ) và 2 cấp độ cắt giảm ngân sách cho sinh viên. |
| `ban-ve-so-do.svg` | Bản vẽ kỹ thuật 2 hình chiếu (Hình chiếu bằng $Oxy$ & Hình chiếu đứng $Oxz$) thể hiện đầy đủ kích thước (mm), dung sai trọng yếu và vùng làm việc $\varnothing 300 \times 150\text{ mm}$. |
| `README.md` | Tài liệu này: trình tự lắp ráp chuẩn, thứ tự ưu tiên căn chỉnh theo độ nhạy và quy trình hiệu chuẩn sau lắp ráp dùng lại `do-nhay-hinh-hoc.py`. |

---

## 2. Trình tự lắp ráp cơ khí – điện tử (7 bước chuẩn)

> **Nguyên tắc an toàn trước khi lắp:** Tuyệt đối **không gắn tay quay $r_f$ vào trục động cơ** trước khi nạp firmware `uno-serial-servo` và đưa cả 3 động cơ về vị trí góc gốc trung tính $\theta_i = 0,0^\circ$ (`SERVO_NEUTRAL_US = 1500` $\mu\text{s}$ trong `config.h`).

### Bước 1: Chế tạo và khóa chiều dài 6 thanh cẳng tay ($r_e = 400,00 \pm 0,10\text{ mm}$) trên đồ gá (Jig)
1. Chuẩn bị thanh dưỡng gá (Jig) có 2 chốt trụ thép tôi $\varnothing 5,00\text{ mm}$ ($g6$) đặt cách tâm đúng $400,00\text{ mm}$ (kiểm tra bằng thước cặp điện tử độ phân giải $0,01\text{ mm}$).
2. Lắp 12 đầu nối ren M5 và 12 khớp cầu mắt trâu SI5T/K vào 6 ống sợi carbon $\varnothing 8 \times \varnothing 6\text{ mm}$.
3. Đặt từng thanh lên 2 chốt của đồ gá để định vị cứng khoảng cách tâm–tâm $400,00\text{ mm}$, khóa chặt đai ốc hãm M5 và nhỏ keo khóa ren (hoặc chờ keo Epoxy đóng rắn hoàn toàn trên đồ gá).
4. Đánh số cặp $(1A, 1B)$, $(2A, 2B)$, $(3A, 3B)$ sao cho 2 thanh trong cùng một cặp có chênh lệch chiều dài $\le 0,05\text{ mm}$.

### Bước 2: Lắp dựng khung trụ nhôm định hình và tấm đế cố định CNC ($f = 346,00\text{ mm}$)
1. Lắp 3 trụ đứng nhôm định hình $40 \times 40\text{ mm}$ (cao $600\text{ mm}$) với các thanh giằng chân đế bằng ke góc đúc.
2. Đặt tấm đế cố định CNC (nhôm 6061-T6 dày $10\text{ mm}$) lên ở cao độ $H_{\text{base}} = 550,0\text{ mm}$ tính từ mặt bàn thí nghiệm.
3. Dùng thước thủy (spirit level) hoặc thước đo góc điện tử đặt lên mặt tấm đế, vặn 3 chân đế cao su tăng chỉnh cho tới khi độ nghiêng của tấm đế so với mặt bàn $\le 0,05^\circ$ theo cả hai phương $Ox$ và $Oy$.

### Bước 3: Lắp 3 cụm gối đỡ ổ trục khớp chủ động ($A_1, A_2, A_3$) và động cơ
1. Ép 6 ổ bi cầu rãnh sâu 688ZZ (hoặc 608ZZ) vào 3 cụm gối đỡ đôi trên tấm đế.
2. Đóng chốt định vị $\varnothing 6\text{H7}$ trước khi siết bu-lông giữ gối đỡ để đảm bảo bán kính hướng kính $R_b = 199,76 \pm 0,05\text{ mm}$ và góc lệch $120^\circ$.
3. Lắp 3 cụm động cơ + hộp giảm tốc $5:1$ (hoặc servo) đồng trục với trục khớp $\varnothing 8\text{g6}$ thông qua khớp nối trục đàn hồi không rơ (zero-backlash jaw/disc coupling).

### Bước 4: Căn chỉnh điểm gốc $\theta_i = 0,0^\circ$ (Homing) và lắp 3 tay quay chủ động ($r_f = 200,00\text{ mm}$)
1. Cấp nguồn cho Arduino Uno R3 (chạy `nghien-cuu/firmware/uno-serial-servo`), nối công tắc dừng khẩn cấp thường đóng (NC) từ chân `D2` (`ESTOP_PIN`) xuống `GND`, và gửi lệnh `H\n` qua Serial ($115\,200\text{ bps}$) để 3 kênh `D9, D10, D11` xuất xung trung tính $1\,500\text{ }\mu\text{s}$ (`HOME1_DEG = HOME2_DEG = HOME3_DEG = 0.0f`).
2. Dùng ke vuông cơ khí hoặc dưỡng đỡ phẳng ép cả 3 tay quay chủ động ($r_f = 200,00\text{ mm}$) nằm ngang trùng khít với mặt phẳng chuẩn $z = 0$ của tấm đế ($\theta_1 = \theta_2 = \theta_3 = 0,0^\circ$), sau đó mới siết khóa kẹp trục (clamping hub) nối tay quay với trục khớp $A_i$.

### Bước 5: Lắp ghép bàn di động ($e = 115,00\text{ mm}$), 12 khớp cầu và lò xo khử rơ
1. Luồn trục khuỷu $\varnothing 5\text{g6}$ qua đầu dưới của tay quay $B_i$, lắp đệm vát (cone spacer) hai bên viên bi cầu của cặp thanh $r_e$ và khóa đai ốc sao cho khoảng cách tâm 2 khớp cầu đúng bằng $w_p = 50,00 \pm 0,05\text{ mm}$.
2. Lắp đầu dưới của 6 thanh cẳng tay vào 3 cạnh của bàn di động PLA+ ($e = 115,00\text{ mm}$, $r_p = 66,40\text{ mm}$) với cùng bề rộng $w_p = 50,00 \pm 0,05\text{ mm}$.
3. Móc 3 cặp lò xo kéo inox vào giữa mỗi cặp thanh cẳng tay để tạo lực ép sơ bộ (preload), khử khe hở dọc trục của 12 khớp cầu.

### Bước 6: Kiểm tra cơ khí nguội (Dry-run) và giới hạn hành trình
1. Trước khi bật nguồn động lực, dùng tay nâng hạ nhẹ bàn di động qua toàn bộ hình trụ $\varnothing 300 \times 150\text{ mm}$ ($z \in [-425, -275]\text{ mm}$) để kiểm tra không có hiện tượng bó kẹt khớp cầu (góc truyền lực lý thuyết $\gamma_{\min} = 39,00^\circ \ge 25^\circ$).
2. Kiểm tra phần mềm kẹp góc trong `config.h` (`JOINT_MIN_DEG = -30.0f`, `JOINT_MAX_DEG = +80.0f`) bao phủ an toàn dải góc làm việc thực tế $[-27,05^\circ, +77,30^\circ]$.

---

## 3. Các điểm cần căn chỉnh theo Thứ tự Ưu tiên Độ nhạy (Sensitivity-Driven Alignment)

Từ kết quả phân tích độ nhạy riêng từng tham số (One-at-a-Time / OAT trong `nghien-cuu/mo-hinh/ket-qua/tom-tat-do-nhay.json`), thời gian và công sức đo kiểm khi lắp ráp phải tập trung theo đúng thứ tự ưu tiên sau:

| Thứ tự ưu tiên | Vị trí cần căn chỉnh | Hệ số khuếch đại sai số xấu nhất | Sai số P95 gây ra (ở mức $\pm 0,2\text{ mm}$) | Phương pháp đo & căn chỉnh thực tế tại xưởng |
| :-: | --- | :-: | :-: | --- |
| **Ưu tiên #1 (Cao nhất)** | **Vị trí hướng kính ($\Delta R_{b,i}$) và cao độ ($\Delta z_{A,i}$) của 3 ổ trục khớp đế $A_1, A_2, A_3$** | **$3,40\text{ mm/mm}$** | $0,312\text{ mm}$ | Đo khoảng cách giữa 3 trục thép $\varnothing 8\text{ mm}$ tại sát gối đỡ bằng thước cặp dài: cả 3 cạnh phải đạt $f = 346,00 \pm 0,08\text{ mm}$. Dùng đồng hồ so (dial indicator) rà mặt trên của 3 trục khớp so với mặt tấm đế, chêm lá căn (shim inox $0,02 \div 0,05\text{ mm}$) dưới đế gối đỡ nếu độ lệch cao độ $\Delta z_{A,i} > 0,05\text{ mm}$. |
| **Ưu tiên #2** | **Chiều dài tâm–tâm 6 thanh cẳng tay ($r_e = 400,00\text{ mm}$) và độ song song trong từng cặp** | **$2,52\text{ mm/mm}$** *(nhạy gấp $2,17$ lần $r_f$)* | $0,291\text{ mm}$ | Kiểm tra từng thanh trên đồ gá 2 chốt $\varnothing 5\text{g6}$: thanh nào phải ấn mạnh mới vào chốt hoặc lỏng rơ trên chốt phải nới đai ốc M5 chỉnh lại ngay. Đo khoảng cách ngoài của 2 ống đệm $w_p$ ở đầu khuỷu $B_i$ và đầu bàn $P_i$ bằng thước cặp điện tử đạt $50,00 \pm 0,05\text{ mm}$. |
| **Ưu tiên #3** | **Góc gốc Home ($\Delta \theta_{0,i}$) và chiều dài 3 tay quay chủ động ($r_f = 200,00\text{ mm}$)** | **$1,16\text{ mm/mm}$** (theo $\Delta r_f$)<br>**$3,49\text{ mm/deg}$** (theo $\Delta \theta_{0,i}$) | $0,145\text{ mm}$ | Sai lệch góc kẹp tay quay $0,1^\circ$ tương đương dịch đầu khuỷu $B_i$ theo phương đứng $\Delta z_B = r_f \Delta \theta = 200 \times \frac{0,1 \pi}{180} = 0,35\text{ mm}$. Do đó, khi đưa về lệnh `H` ($\theta_i = 0^\circ$), phải đo khoảng cách từ mặt dưới tấm đế tới tâm trục khuỷu $B_1, B_2, B_3$ bằng thước đo cao để đảm bảo cả 3 khuỷu có cùng cao độ trong phạm vi $\pm 0,10\text{ mm}$. |
| **Ưu tiên #4 & #5 (Thấp hơn)** | **Cạnh tam giác đế ($f$) và cạnh bàn di động ($e = 115,00\text{ mm}$)** | **$0,97\text{ mm/mm}$** | $0,131\text{ mm}$ ($f$)<br>$0,128\text{ mm}$ ($e$) | Nhờ hệ số chia giảm $\sqrt{3} \approx 1,732$ khi quy đổi sang bán kính $R = (f - e)/\sqrt{3}$, chỉ cần đo kiểm kích thước chi tiết in 3D của bàn di động đạt $r_p = 66,40 \pm 0,15\text{ mm}$ bằng thước cặp trước khi lắp. |

---

## 4. Quy trình Hiệu chuẩn Động học (Calibration) và Nghiệm thu sau lắp ráp bằng `do-nhay-hinh-hoc.py`

Sau khi lắp xong phần cứng (hoặc sau khi đo thực tế kích thước các chi tiết gia công), nhóm thực hiện quy trình **2 giai đoạn** dưới đây bằng cách tái sử dụng trực tiếp mã nguồn `nghien-cuu/mo-hinh/do-nhay-hinh-hoc.py`:

### Giai đoạn A: Kiểm chứng nghiệm thu kích thước chế tạo thực tế bằng hàm `forward_kinematics_perturbed_batch()`
Thay vì chỉ giả định dung sai ngẫu nhiên, ta dùng thước cặp điện tử đo kích thước thực tế của từng nhánh $i \in \{1, 2, 3\}$ sau khi gia công xong và ghi lại 6 vector sai lệch thực đo (đơn vị $\text{mm}$):
- `df_meas = [f_1 - 346.0, f_2 - 346.0, f_3 - 346.0]`
- `de_meas = [e_1 - 115.0, e_2 - 115.0, e_3 - 115.0]`
- `drf_meas = [rf_1 - 200.0, rf_2 - 200.0, rf_3 - 200.0]`
- `dre_meas = [re_1 - 400.0, re_2 - 400.0, re_3 - 400.0]`
- `dRb_meas = [Rb_1 - 199.763, Rb_2 - 199.763, Rb_3 - 199.763]`
- `dzA_meas = [zA_1, zA_2, zA_3]`

Chạy lệnh kiểm tra nhanh bằng Python chuẩn của dự án (`D:\Python312\python.exe`) gọi trực tiếp các hàm trong `nghien-cuu/mo-hinh/do-nhay-hinh-hoc.py`:

```powershell
& "D:\Python312\python.exe" -c "
import sys, numpy as np
sys.path.insert(0, r'D:\NCKH-Co-Dien-Tu\nghien-cuu\mo-hinh')
import importlib.util
spec = importlib.util.spec_from_file_location('dn', r'D:\NCKH-Co-Dien-Tu\nghien-cuu\mo-hinh\do-nhay-hinh-hoc.py')
dn = importlib.util.module_from_spec(spec); spec.loader.exec_module(dn)

pts = dn.generate_workspace_grid()
thetas_nom = dn.compute_nominal_ik_batch(pts)
# Nhập sai lệch đo thực tế trên chi tiết sau gia công (ví dụ đo mẫu nằm trong dung sai thiết kế):
df = np.array([0.05, -0.04, 0.03])
de = np.array([-0.08, 0.10, -0.05])
drf = np.array([0.06, -0.05, 0.04])
dre = np.array([0.04, -0.03, 0.05])
dRb = np.array([0.03, -0.02, 0.04])
dzA = np.array([0.02, -0.03, 0.01])

p_act = dn.forward_kinematics_perturbed_batch(thetas_nom, df, de, drf, dre, dRb, dzA)
err = np.linalg.norm(p_act - pts, axis=1)
print(f'Sai so trung binh: {np.mean(err):.3f} mm | P95: {np.percentile(err, 95):.3f} mm | Max: {np.max(err):.3f} mm')
"
```
- **Tiêu chuẩn nghiệm thu cơ khí:** Nếu kết quả in ra đạt $\text{Max} \le 0,80\text{ mm}$ và $\text{P95} \le 0,55\text{ mm}$ trên toàn bộ $567$ điểm lưới (và khi quét thêm Monte Carlo phần sai số đo lường còn dư $\pm 0,05\text{ mm}$ đạt $100\,\%$ điểm $\le 1,0\text{ mm}$), khung cơ khí được phép chuyển sang bước vận hành tự động.

### Giai đoạn B: Hiệu chuẩn bù phần mềm (Kinematic Calibration) không cần cảm biến đắt tiền
Nếu sau khi lắp ráp, sai lệch lắp đặt thực tế làm sai số vượt $0,8\text{ mm}$, ta khử sai số tĩnh bằng phần mềm theo phương pháp của Vischer & Clavel (1998) kết hợp hàm `forward_kinematics_perturbed_batch` trong `do-nhay-hinh-hoc.py`:
1. **Thu thập dữ liệu tại 9 điểm chuẩn trên mặt phẳng bàn:** Dán một tờ giấy milimét (hoặc tấm dưỡng cắt laser) có đánh dấu $M = 9$ điểm tọa độ chuẩn $\mathbf{p}_{\text{ref}}^{(k)} = (x_k, y_k, z_{\text{bàn}})$ ($1$ điểm tâm $(0,0)$ và $8$ điểm trên vòng tròn bán kính $75\text{ mm}$ và $140\text{ mm}$).
2. **Đo bộ góc khớp thực tế:** Điều khiển từng bước nhỏ (`J,<t1>,<t2>,<t3>` qua Serial) đưa đầu kim nhọn gắn tại tâm bàn di động $P$ chạm đúng vào từng điểm chuẩn $\mathbf{p}_{\text{ref}}^{(k)}$ và ghi lại $9$ bộ góc khớp $\boldsymbol{\theta}_{\text{meas}}^{(k)}$.
3. **Nhận dạng bộ tham số thực tế bằng tối ưu hóa bình phương tối tiểu (`scipy.optimize.least_squares`):**
   Tìm vector sai lệch hình học $\Delta \boldsymbol{\lambda}^* = (\Delta \mathbf{f}, \Delta \mathbf{e}, \Delta \mathbf{r}_f, \Delta \mathbf{r}_e, \Delta \mathbf{R}_b, \Delta \mathbf{z}_A, \Delta \boldsymbol{\theta}_0)$ sao cho hàm mục tiêu sử dụng `forward_kinematics_perturbed_batch(thetas_meas + dtheta0, ...)` đạt cực tiểu:
   $$\Delta \boldsymbol{\lambda}^* = \arg\min_{\Delta \boldsymbol{\lambda}} \sum_{k=1}^{9} \big\| \text{FK}_{\text{perturbed}}(\boldsymbol{\theta}_{\text{meas}}^{(k)} + \Delta \boldsymbol{\theta}_0, \Delta \boldsymbol{\lambda}) - \mathbf{p}_{\text{ref}}^{(k)} \big\|_2^2$$
4. **Cập nhật vào bộ giải IK điều khiển:** Thay bộ tham số danh nghĩa `PARAMS_NOMINAL` và góc offset `HOME_DEG` trong `config.h` bằng bộ tham số đã hiệu chuẩn $\boldsymbol{\lambda}_0 + \Delta \boldsymbol{\lambda}^*$, giúp đưa sai số vị trí tĩnh trên toàn vùng làm việc về dưới $\pm 0,25\text{ mm}$ ngay cả khi cơ khí có dung sai chế tạo thô.
