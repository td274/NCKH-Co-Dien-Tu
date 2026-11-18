# Danh mục Vật tư – Linh kiện (Bill of Materials — BOM) và Tính chọn Truyền động Robot Delta

**Đề tài:** Nghiên cứu và mô phỏng robot Delta cho ứng dụng phân loại sản phẩm bằng camera  
**Nguyên tắc lập BOM:**
- Mọi thông số tải trọng (mô-men, vận tốc, độ phân giải phản hồi) được dẫn xuất trực tiếp từ kết quả mô phỏng `nghien-cuu/mo-phong/runs/2026-11-18-pid-quy-dao-bac5/output/metrics.json` và `config.json`.
- Mọi kích thước cơ khí và yêu cầu dung sai lấy từ `nghien-cuu/thiet-ke/thong-so-co-khi.md`.
- Giá tiền được ghi theo **khoảng giá thị trường Việt Nam (VNĐ)** kèm ghi chú *"giá tham khảo, cần kiểm tra lại tại thời điểm mua"*; không chỉ định nhà cung cấp cụ thể.
- Các thông số kỹ thuật của linh kiện thương mại chưa có bản cứng datasheet đính kèm trong kho dữ liệu đều được đánh dấu `[CẦN KIỂM CHỨNG]`.

---

## 1. Tính toán chọn Động cơ & Hộp giảm tốc (Actuator Sizing)

### 1.1. Yêu cầu kỹ thuật tại trục khớp chủ động ($A_1, A_2, A_3$)
Từ file kết quả `metrics.json` và cấu hình `config.json` của mô phỏng quỹ đạo đa thức bậc 5:

| Thông số yêu cầu tại trục khớp | Giá trị từ mô phỏng ($T_{\text{cycle}} = 1,5\text{ s}$) | Giá trị ở chu kỳ giới hạn ($T_{\text{cycle}} = 0,696\text{ s}$) | Hệ số an toàn áp dụng ($k_{\text{sf}}$) | Thông số thiết kế chọn linh kiện |
| --- | :---: | :---: | :---: | :---: |
| **Mô-men xoắn đỉnh ($\tau_{\max}$)** | $0,457\text{ N}\cdot\text{m}$ (`PID_can_bang`)<br>$0,484\text{ N}\cdot\text{m}$ (`PID_nhanh`) | $1,636\text{ N}\cdot\text{m}$ | **$k_{\tau} = 2,5 \ge 2,0$** (so với chu kỳ $1,5\text{ s}$) | **$\tau_{\text{định mức trục khớp}} \ge 1,15\text{ N}\cdot\text{m}$**<br>*(Chọn $\ge 2,0\text{ N}\cdot\text{m}$ để đạt $k_{\tau} = 4,38$ ở $1,5\text{ s}$ và $k_{\tau} = 1,22$ ở $0,696\text{ s}$)* |
| **Vận tốc góc đỉnh ($\omega_{\max}$)** | $4,664\text{ rad/s}$ ($\approx 44,5\text{ rpm}$) | $9,990\text{ rad/s}$ ($\approx 95,4\text{ rpm}$) | **$k_{\omega} = 1,5 \div 2,1$** | **$\omega_{\text{định mức trục khớp}} \ge 7,0 \div 10,0\text{ rad/s}$** ($\approx 67 \div 96\text{ rpm}$) |
| **Công suất cơ học đỉnh mỗi khớp ($P_{\max} = \tau_{\max} \omega_{\max}$)** | $2,13\text{ W}$ | $16,34\text{ W}$ | **$k_P = 3,0$** | Công suất định mức động cơ $\ge 25 \div 50\text{ W}$ |
| **Độ phân giải phản hồi góc khớp** | $4\,096\text{ xung/vòng}$ (`config.json`) | $4\,096\text{ xung/vòng}$ | — | Sai số lượng tử hóa góc $\Delta \theta \le 0,088^\circ$ ($\approx 0,31\text{ mm}$ tại đầu mút tay quay $r_f = 200\text{ mm}$) |
| **Dải góc làm việc an toàn** | $[-27,05^\circ, +77,30^\circ]$ | $[-27,05^\circ, +77,30^\circ]$ | Dự trữ biên $\ge 2,5^\circ$ | Khớp với giới hạn kẹp phần mềm `[-30.0f, +80.0f]` trong `config.h` |

### 1.2. Phân tích so sánh 3 phương án truyền động và lý do lựa chọn

1. **Phương án đề xuất chuẩn (Khuyến nghị cho khung cơ khí hoàn chỉnh): Động cơ bước vòng kín (Closed-loop Stepper / Hybrid Servo) NEMA 17 hoặc NEMA 23 có Encoder ($\ge 1\,000\text{ PPR}$, giải mã Quadrature 4x đạt $4\,000\text{ xung/vòng}$) kết hợp Hộp giảm tốc hành tinh tỷ số truyền $i = 5:1$ (hoặc bộ truyền đai răng GT2 $i = 4:1$)**
   - **Thông số đạt được `[CẦN KIỂM CHỨNG theo datasheet từng hãng]`:**
     - Bản thân động cơ NEMA 17 vòng kín (dài $48\text{–}60\text{ mm}$, dòng $1,8\text{–}2,0\text{ A}$) có mô-men giữ khoảng $0,55 \div 0,65\text{ N}\cdot\text{m}$ `[CẦN KIỂM CHỨNG]`. Qua hộp giảm tốc hành tinh $i = 5:1$ (hiệu suất $\eta \approx 0,90$), mô-men tại trục khớp đạt:
       $$\tau_{\text{trục khớp}} = 0,55 \times 5 \times 0,90 \approx 2,48\text{ N}\cdot\text{m}$$
       $\implies$ **Hệ số an toàn mô-men đạt $k_{\tau} = \frac{2,48}{0,457} = 5,42 > 2,0$** ở chu kỳ $1,5\text{ s}$ (và đạt $k_{\tau} = \frac{2,48}{1,636} = 1,52$ ở chu kỳ nhanh $0,696\text{ s}$).
     - Với vận tốc làm việc hiệu quả của động cơ bước vòng kín $n_{\text{motor}} \approx 500\text{ rpm}$, vận tốc đầu ra sau hộp số $5:1$ là $n_{\text{khớp}} = 100\text{ rpm} \approx 10,47\text{ rad/s} > 4,66\text{ rad/s}$ (**hệ số an toàn vận tốc $k_\omega = 2,24$**).
     - Độ phân giải góc tại trục khớp sau hộp số $5:1$ đạt $4\,000 \times 5 = 20\,000\text{ xung/vòng}$ ($\Delta \theta = 0,018^\circ$), vượt yêu cầu `4096 counts/rev` trong `config.json`.
   - **Vì sao chọn loại có phản hồi vòng kín (Closed-loop):** Khắc phục hoàn toàn hiện tượng mất bước, tự động tăng dòng theo tải (giống bộ điều khiển PID + Feed-forward trong mô phỏng), không bị nóng động cơ khi giữ tĩnh bàn di động chống trọng lực.

2. **Phương án tương thích trực tiếp Firmware hiện tại (`uno-serial-servo`): Động cơ Servo DC số mô-men cao (Digital Metal-Gear Servo / Smart Bus Servo) có tích hợp mạch PID nội và cảm biến góc**
   - **Lý do liên hệ thực tế dự án:** Firmware `nghien-cuu/firmware/uno-serial-servo/config.h` hiện đang xuất 3 kênh xung PWM chuẩn $500\text{–}2\,500\text{ }\mu\text{s}$ ($50\text{ Hz}$) trên các chân `D9, D10, D11` của Arduino Uno R3.
   - **Thông số yêu cầu:** Nếu dùng trực tiếp RC/Industrial Digital Servo (ví dụ dòng vỏ nhôm bánh răng thép không chổi than hoặc coreless $25\text{–}35\text{ kg}\cdot\text{cm}$ ở điện áp $7,4\text{–}8,4\text{ V}$ `[CẦN KIỂM CHỨNG]`), mô-men cực đại đạt $2,45 \div 3,43\text{ N}\cdot\text{m}$ và mô-men làm việc liên tục đạt $\approx 1,0 \div 1,2\text{ N}\cdot\text{m}$ (**hệ số an toàn $k_{\tau} \approx 2,2 \div 2,6$**), vận tốc không tải $0,10\text{–}0,12\text{ s}/60^\circ \approx 8,7 \div 10,5\text{ rad/s}$ `[CẦN KIỂM CHỨNG]`.
   - **Nhược điểm cần lưu ý:** Độ phân giải dải xung PWM của thư viện `Servo.h` trên ATmega328P (Timer1 16-bit, bước đếm $0,5\text{ }\mu\text{s}$) và biến trở (potentiometer) bên trong servo phổ thông có vùng chết (deadband) $\sim 2\text{–}4\text{ }\mu\text{s} \approx 0,18^\circ \div 0,36^\circ$, tạo ra sai số điểm cuối $\sim 0,6 \div 1,2\text{ mm}$ và độ rơ bánh răng hộp số lớn hơn hộp số hành tinh. Do đó chỉ phù hợp cho mô hình trình diễn hoặc thí nghiệm HIL.

3. **Cảnh báo rủi ro nếu chọn Động cơ bước vòng hở (Open-loop Stepper):**
   - Trong nhiều đồ án giá rẻ, sinh viên thường dùng động cơ bước NEMA 17 vòng hở kèm driver A4988 / DRV8825 / TB6600 không có encoder phản hồi.
   - **Rủi ro mất bước (Step-loss risk):** Ở chu kỳ $1,5\text{ s}$ (và đặc biệt khi giảm chu kỳ xuống $< 1,0\text{ s}$), tại các thời điểm tăng tốc/giảm tốc đỉnh của quỹ đạo bậc 5, nếu mô-men quán tính + ma sát khớp cầu tức thời vượt quá mô-men kéo đồng bộ (pull-out torque) của động cơ bước vòng hở, rotor sẽ bị **trượt bước (mất bước)**. Vì hệ không có encoder đọc về, bộ điều khiển hoàn toàn không biết khớp thứ $i$ đã bị lệch một góc $\Delta \theta_i$. Trong cơ cấu song song Delta, chỉ cần **1 trong 3 nhánh mất bước $1,8^\circ$** ($0,0314\text{ rad}$), tọa độ bàn di động sẽ bị **lệch vĩnh viễn $\Delta p \approx r_f \Delta \theta_i \approx 6,3\text{ mm}$** và làm nghiêng mặt phẳng gắp trong suốt các chu kỳ tiếp theo cho tới khi về lại cảm biến gốc (Home switch).

---

## 2. Bảng Dự toán Chi tiết Linh kiện (BOM) — Phương án Đầy đủ (Chế tạo Robot Hoàn chỉnh)

Bảng dưới đây liệt kê toàn bộ vật tư để chế tạo hoàn chỉnh khung cơ khí + hệ truyền động vòng kín + thị giác máy tính đạt chuẩn dung sai $\le \pm 0,2\text{ mm}$.

| TT | Hạng mục / Chi tiết | Thông số kỹ thuật yêu cầu | ĐVT | Số lượng | Đơn giá tham khảo (VNĐ) | Thành tiền tham khảo (VNĐ) | Ghi chú & Nguồn truy nguyên |
| :-: | --- | --- | :-: | :-: | ---: | ---: | --- |
| **A** | **NHÓM GIA CÔNG CƠ KHÍ & KHUNG KẾT CẤU** | | | | | | *(Giá tham khảo, cần kiểm tra lại)* |
| 1 | Tấm đế cố định CNC ($f = 346\text{ mm}$) | Nhôm tấm 6061-T6 dày $10\text{ mm}$, kích thước bao $480 \times 480\text{ mm}$, phay CNC 1 lần gá các lỗ định vị 3 cụm khớp $A_i$ ($R_b = 199,76 \pm 0,05\text{ mm}$) | Tấm | 1 | 850.000 – 1.100.000 | 950.000 | Chi tiết quan trọng số 1 (hệ số nhạy $3,40\text{ mm/mm}$). |
| 2 | Cụm gối đỡ hai đầu trục khớp đế $A_i$ | Nhôm 6061-T6 phay CNC, lỗ ổ bi $\varnothing 16\text{H7}$ (hoặc dùng 6 gối đỡ mặt bích KFL08 chọn lọc + chốt định vị $\varnothing 5\text{H7}$) | Bộ (3 nhánh) | 1 | 450.000 – 650.000 | 550.000 | Đỡ 2 đầu trục $\varnothing 8\text{ mm}$ chống uốn công-xôn. |
| 3 | Tay quay chủ động ($r_f = 200\text{ mm}$) | Nhôm 6061-T6 dày $6\text{ mm}$, khoảng cách tâm lỗ $\varnothing 8\text{H7}$ và $\varnothing 5\text{H7}$ đúng $200,00 \pm 0,10\text{ mm}$, khoét rỗng giảm khối lượng ($\le 110\text{ g}$) | Chiếc | 3 | 150.000 – 220.000 | 540.000 | Chịu mô-men uốn $\tau_{\max} = 0,457 \div 1,64\text{ N}\cdot\text{m}$. |
| 4 | Ống sợi carbon làm cẳng tay ($r_e$) | Ống carbon 3K rỗng $\varnothing 8 \times \varnothing 6\text{ mm}$, cắt đoạn $350\text{ mm}$ (6 đoạn từ 3 cây dài $1\,000\text{ mm}$) `[CẦN KIỂM CHỨNG độ thẳng]` | Cây $1\text{ m}$ | 3 | 80.000 – 120.000 | 300.000 | Siêu nhẹ ($\sim 18\text{ g/thanh}$), giảm quán tính $J_{\text{eq}}$. |
| 5 | Đầu nối ren nhôm gắn ống carbon + Đồ gá (Jig) $400\text{ mm}$ | 12 đầu trụ nhôm tiện $\varnothing 6\text{ mm}$ ren trong M5 + 1 thanh dưỡng nhôm gắn 2 chốt $\varnothing 5,00\text{ mm}$ cách tâm $400,00 \pm 0,05\text{ mm}$ | Bộ | 1 | 250.000 – 350.000 | 300.000 | Đảm bảo 6 thanh $r_e = 400,00 \pm 0,10\text{ mm}$ đồng đều. |
| 6 | Bàn di động ($e = 115\text{ mm}$) | In 3D PLA+ / PETG (infill $40\,\%$) hoặc nhôm 6061 dày $4\text{ mm}$, $r_p = 66,40 \pm 0,15\text{ mm}$, bề rộng gá khớp $w_p = 50,00\text{ mm}$ | Chiếc | 1 | 120.000 – 200.000 | 150.000 | Khối lượng $\le 45\text{ g}$; có lỗ gắn giác hút ở tâm $P$. |
| 7 | Khung nhôm định hình $40 \times 40\text{ mm}$ & Phụ kiện | 3 trụ đứng dài $600\text{ mm}$ + 6 thanh giằng ngang $450\text{ mm}$ + 18 ke góc đúc 4040 + ốc T-nut M8 + 3 chân đế cao su tăng chỉnh | Bộ | 1 | 650.000 – 850.000 | 750.000 | Tạo khoảng hở $H_{\text{base}} = 550\text{ mm}$ từ mặt bàn. |
| **B** | **NHÓM KHỚP, Ổ BI & CHI TIẾT TIÊU CHUẨN** | | | | | | |
| 8 | Khớp cầu mắt trâu (Rod-end bearing) | Mã SI5T/K hoặc PHS5 (lỗ bi $\varnothing 5\text{ mm}$, ren trong/ngoài M5), khe hở hướng kính $\le 0,03\text{ mm}$ `[CẦN KIỂM CHỨNG]` + 24 đệm vát (cone spacer) | Chiếc | 14 | 25.000 – 40.000 | 450.000 | Dùng 12 chiếc cho 6 thanh $r_e$ (+ 2 chiếc dự phòng chọn lọc độ rơ). |
| 9 | Ổ bi cầu rãnh sâu trục khớp chủ động | Mã 688ZZ ($\varnothing 8 \times \varnothing 16 \times 5\text{ mm}$) hoặc 608ZZ ($\varnothing 8 \times \varnothing 22 \times 7\text{ mm}$) cấp ABEC-3/P6 `[CẦN KIỂM CHỨNG]` | Chiếc | 6 | 20.000 – 35.000 | 150.000 | 2 ổ bi / nhánh $\times 3$ nhánh. |
| 10 | Trục thép tôi mài, chốt khuỷu & Lò xo khử rơ | 3 trục khớp đế $\varnothing 8\text{g6} \times 80\text{ mm}$; 6 trục suốt $\varnothing 5\text{g6} \times 70\text{ mm}$ (cho khuỷu $B_i$ & bàn $P_i$); 6 lò xo kéo inox dài $40\text{ mm}$; ốc lục giác inox M3, M4, M5 | Bộ | 1 | 200.000 – 300.000 | 250.000 | Lò xo kéo giữa 2 thanh bình hành giúp khử độ rơ khớp cầu. |
| **C** | **NHÓM TRUYỀN ĐỘNG, ĐIỀU KHIỂN & THỊ GIÁC** | | | | | | |
| 11 | Cụm Động cơ bước vòng kín + Driver + Hộp số $5:1$ | Closed-loop Stepper NEMA 17/23 tích hợp Encoder $1\,000\text{ PPR}$ ($4\,000\text{ cpr}$) + Driver vòng kín + Hộp giảm tốc hành tinh $i = 5:1$ (hoặc truyền đai GT2 $4:1$), $\tau_{\text{ra}} \ge 2,0\text{ N}\cdot\text{m}$ `[CẦN KIỂM CHỨNG]` | Bộ | 3 | 850.000 – 1.250.000 | 3.150.000 | Hệ số an toàn $k_{\tau} \ge 4,38$ (chu kỳ $1,5\text{ s}$); không mất bước. |
| 12 | Khớp nối trục đàn hồi (Coupling) & Cảm biến gốc (Home) | 3 khớp nối trục nhôm $\varnothing 8 - \varnothing 8\text{ mm}$ (loại 2 đĩa đàn hồi zero-backlash) + 3 cảm biến quang chữ U (Opto-switch NPN) tìm gốc $\theta_i = 0^\circ$ | Bộ | 1 | 180.000 – 250.000 | 210.000 | Căn chỉnh góc chuẩn $\theta_{\text{home}} = 0,0^\circ$ khi khởi động. |
| 13 | Bộ nguồn tổ ong DC & Nút dừng khẩn cấp (E-Stop) | Nguồn xung $24\text{ VDC} - 10\text{ A}$ ($240\text{ W}$) cấp cho 3 driver + 1 nút nhấn E-Stop thường đóng (NC) nối chân `D2` (`ESTOP_PIN` trong `config.h`) | Bộ | 1 | 250.000 – 350.000 | 300.000 | Đảm bảo dòng đỉnh khi cả 3 trục tăng tốc cùng lúc. |
| 14 | Vi điều khiển & Cơ cấu chấp hành đầu cuối (Giác hút) | 1 बोर्ड Arduino Uno R3 (ATmega328P, giao tiếp Serial $115\,200\text{ bps}$) + 1 bơm chân không mini $12/24\text{ V}$ + van điện từ $3/2$ + giác hút cao su $\varnothing 15\text{ mm}$ + module MOSFET | Bộ | 1 | 300.000 – 450.000 | 380.000 | Khối lượng đầu hút gắn trên bàn di động $\le 25\text{ g}$ (bơm đặt trên đế). |
| 15 | Hệ thống Thị giác (Camera + Đèn + Vật mẫu) | 1 Webcam USB $\ge 720\text{p}@30\text{ fps}$ + Hộp chụp nền trắng mờ + Đèn LED cố định + Bộ $120$ vật mẫu (3 màu $\times$ 3 hình dạng: tròn, vuông, tam giác) | Bộ | 1 | 350.000 – 500.000 | 420.000 | Theo đúng bảng thiết bị Mục 4 `de-tai.md`. |
| | **TỔNG CỘNG (Phương án Đầy đủ — Chuẩn kỹ thuật)** | | | | **7.350.000 – 10.670.000** | **8.850.000 VNĐ** | *(Giá tham khảo, chưa gồm phí vận chuyển)* |

---

## 3. Phương án Cắt giảm Chi phí (Khi vượt ngân sách sinh viên)

Vì ngân sách thực hiện NCKH của sinh viên năm 2 thường giới hạn, nhóm thiết kế đề xuất **2 cấp độ cắt giảm** có phân tích rõ sự đánh đổi kỹ thuật:

### Cấp độ 1: Phương án Cơ khí Tiết kiệm (Giảm từ ~8,85 triệu xuống ~3,60 – 4,20 triệu VNĐ)
Dành cho trường hợp vẫn muốn dựng khung robot Delta thật để chạy thử nghiệm gắp vật nhẹ ở chu kỳ $1,5 \div 1,8\text{ s}$ nhưng tối ưu hóa vật tư:
1. **Thay cụm Closed-loop Stepper + Hộp số hành tinh (Mục 11 — 3.150.000 VNĐ) bằng:**
   - *Lựa chọn 1A (Dùng lại trực tiếp firmware `uno-serial-servo`):* **3 động cơ Servo DC kỹ thuật số vỏ nhôm bánh răng kim loại $25\text{–}35\text{ kg}\cdot\text{cm}$** ($\approx 2,45\text{–}3,43\text{ N}\cdot\text{m}$ ở $7,4\text{ V}$ `[CẦN KIỂM CHỨNG]`, giá tham khảo $280.000\text{–}380.000\text{ VNĐ/chiếc} \times 3 \approx 1.000.000\text{ VNĐ}$) + nguồn hạ áp $7,4\text{ V} - 15\text{ A}$. **Tiết kiệm ~2.150.000 VNĐ.** *(Đánh đổi: độ rơ hộp số servo lớn hơn, sai số lặp lại khoảng $\pm 0,8 \div 1,2\text{ mm}$)*.
   - *Lựa chọn 1B (Truyền đai răng GT2 + Stepper NEMA 17 có Encoder rời AS5600):* Dùng 3 động cơ NEMA 17 ($0,55\text{ N}\cdot\text{m}$) + bộ truyền puly đai răng GT2 tỷ số $i = 4:1$ (puly $20$ răng kéo puly $80$ răng in 3D/nhôm) + 3 cảm biến từ góc tuyệt đối 12-bit AS5600 ($4\,096\text{ xung/vòng}$, giá $\sim 45.000\text{ VNĐ/mạch}$ `[CẦN KIỂM CHỨNG]`). Tổng chi phí 3 nhánh $\sim 1.150.000\text{ VNĐ}$. **Tiết kiệm ~2.000.000 VNĐ** mà vẫn giữ được độ phân giải $4\,096\text{ cpr}$ và chống mất bước.
2. **Thay tấm đế Nhôm 6061 phay CNC dày $10\text{ mm}$ (Mục 1 & 2 — 1.500.000 VNĐ) bằng:**
   - **Thép tấm CT3 dày $6\text{ mm}$ cắt Laser Fiber nguyên tấm** (giá cắt laser thép theo kg tại các xưởng gia công chỉ khoảng $350.000\text{–}450.000\text{ VNĐ/tấm}$) kết hợp 6 gối đỡ ổ bi mặt bích KFL08 định vị bằng chốt. Dung sai cắt Laser Fiber hiện đại đạt $\pm 0,05 \div 0,10\text{ mm}$, vẫn thỏa mãn kết quả khảo sát độ nhạy. **Tiết kiệm ~1.000.000 VNĐ.**
3. **Thay ống sợi Carbon (Mục 4 — 300.000 VNĐ) bằng:**
   - **Ống nhôm hợp kim rỗng $\varnothing 8 \times 1\text{ mm}$** (hoặc thanh gỗ phíp/sợi thủy tinh $\varnothing 8\text{ mm}$), giá khoảng $60.000\text{ VNĐ}$ cho cả 6 thanh, vẫn lắp trên cùng **đồ gá (Jig) 2 chốt $400,00\text{ mm}$** để không làm giảm độ chính xác chiều dài $r_e$. **Tiết kiệm ~240.000 VNĐ.**

### Cấp độ 2: Phương án Hardware-in-the-Loop (HIL) Tối thiểu (< 500.000 VNĐ — Đúng theo Mục 4 `nghien-cuu/de-tai.md`)
Trong phạm vi 12 tuần của đề tài hiện tại (Phương án 3 trong `de-tai.md`: *"không dựng khung cơ khí Delta hoàn chỉnh — phần cơ khí dừng ở bản vẽ CAD + BOM"*), nhóm chỉ mua gói phần cứng tối thiểu để đo kiểm thực nghiệm chuỗi Thị giác $\rightarrow$ Serial $\rightarrow$ PWM:

| TT | Hạng mục (Gói HIL tối thiểu) | Số lượng | Thành tiền tham khảo (VNĐ) | Mục đích sử dụng trong đề tài |
| :-: | --- | :-: | ---: | --- |
| 1 | Webcam USB $\ge 720\text{p}$, $30\text{ fps}$ | 1 | 180.000 – 250.000 | Chụp vật mẫu thật, đo trễ xử lý ảnh OpenCV. |
| 2 | Board Arduino Uno R3 (kèm cáp USB) + Nút nhấn E-Stop | 1 | 95.000 – 130.000 | Chạy firmware `uno-serial-servo`, đo trễ vòng kín Serial và xuất xung PWM trên chân `D9, D10, D11`. |
| 3 | Hộp chụp nền trắng mờ + Đèn LED chiếu sáng cố định + $120$ vật mẫu (3 màu $\times$ 3 hình) | 1 bộ | 80.000 – 110.000 | Kiểm thử độ chính xác phân loại $\ge 90\,\%$ và lập ma trận nhầm lẫn. |
| | **TỔNG CỘNG GÓI HIL TỐI THIỂU** | | **355.000 – 490.000 VNĐ** | **Đảm bảo $< 500.000\text{ VNĐ}$ theo đúng đề cương.** |
