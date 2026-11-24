# Chương 4. Thiết kế và hiện thực hệ thống

> **Bản nháp để sinh viên kiểm chứng — không phải bản nộp.** Số liệu lấy từ `nghien-cuu/thiet-ke/`, `nghien-cuu/mo-hinh/`, `nghien-cuu/mo-phong/runs/2026-11-24-pid-v2-dung-nghi/` và `nghien-cuu/firmware/uno-serial-servo/`. Các số đo thực nghiệm chưa có được đánh dấu rõ. Chương này **không** báo cáo kết quả đo trên robot; kết quả đo thuộc chương 5.

Chương này chốt tham số hình học (4.1), thiết kế cơ khí và dung sai (4.2), phương án truyền động và mô-men yêu cầu (4.3), ngân sách sai số (4.4), kiến trúc điều khiển và firmware (4.5), và danh mục vật tư (4.6).

## 4.1 Tham số hình học chốt

Bảng 4.1 liệt kê tham số hình học dùng cho toàn bộ mô phỏng, dung sai và thiết kế cơ khí. Các giá trị này được giữ nguyên qua mô hình động học (chương 3), kiểm chứng chéo và ngân sách sai số.

**Bảng 4.1.** Tham số hình học chốt của robot Delta.

| Tham số | Ký hiệu | Giá trị | Đơn vị | Ghi chú |
| --- | :---: | :---: | :---: | --- |
| Cạnh tam giác đế cố định | $f$ | 346,00 | mm | Ba khớp $A_i$ đặt tại ba đỉnh |
| Bán kính ngoại tiếp đế | $R_b$ | 199,76 | mm | $= f/\sqrt{3}$ |
| Cạnh tam giác bàn di động | $e$ | 115,00 | mm | Ba khớp cầu $P_i$ |
| Bán kính ngoại tiếp bàn | $r_p$ | 66,40 | mm | $= e/\sqrt{3}$ |
| Hiệu bán kính | $R$ | 133,37 | mm | $= R_b - r_p$ |
| Tay quay chủ động | $r_f$ | 200,00 | mm | Từ $A_i$ tới khuỷu $B_i$ |
| Cẳng tay song song | $r_e$ | 400,00 | mm | Hai thanh mỗi nhánh |
| Khoảng cách hai thanh trong cặp | $w_p$ | 50,00 | mm | Đồng bộ tại khuỷu và bàn |
| Vùng làm việc | $\varnothing \times H$ | 300,0 × 150,0 | mm | Hình trụ |
| Dải cao độ vùng làm việc | $[z_{\min}, z_{\max}]$ | $[-425,0;\ -275,0]$ | mm | Tâm $\mathbf{p}_0 = (0, 0, -350)$ |
| Dải góc khớp thực | $[\theta_{\min}, \theta_{\max}]$ | $[-27{,}05;\ +77{,}30]$ | deg | Trong vùng làm việc |
| Giới hạn kẹp phần mềm | — | $[-30;\ +80]$ | deg | `config.h` |
| Trần cao độ gắp | $z_{\text{trần}}$ | $-250$ | mm | Xem ghi chú bên dưới |
| Khoảng hở trên mặt đế | $h_{\text{top}}$ | $\ge 115$ | mm | 100 mm khuỷu nhô lên + 15 mm dự trữ |
| Chiều cao mặt đế so với bàn | $H_{\text{base}}$ | 550,0 | mm | Từ mặt bàn đến $z = 0$ |
| Khoảng hở dưới bàn di động | $h_{\text{clear}}$ | 125 ÷ 275 | mm | Trong vùng làm việc |

Nguồn: `dong-hoc-delta.md` (mục 5.1, 6.6), `thong-so-co-khi.md` (mục 1.2), `config.h`.

**Kết quả động học trong vùng làm việc.** Dải góc khớp $[-27{,}05^\circ;\ +77{,}30^\circ]$ nằm trong giới hạn kẹp $[-30^\circ;\ +80^\circ]$. Biên dự trữ là $2{,}95^\circ$ ở phía âm và $2{,}70^\circ$ ở phía dương. Góc truyền lực nhỏ nhất là $\gamma_{\min} = 39{,}00^\circ$, cao hơn ngưỡng $25^\circ$ của giả thiết. Số điều kiện Jacobian chuẩn hóa $\kappa(\hat{J})$ dao động trong $[1{,}013;\ 1{,}981]$, trung bình $1{,}403$ [`tom-tat-kiem-chung.json`].

**Ghi chú về trần cao độ.** Giới hạn trần là $z > -250\,\text{mm}$: khi vượt mốc này, góc khớp $\theta_i$ vượt quá $-40^\circ$ và bán kính khả dụng tụt từ $245\,\text{mm}$ xuống dưới $150\,\text{mm}$ (`dong-hoc-delta.md`, mục 6.6). Vùng làm việc được giữ trong $z \in [-425;\ -275]\,\text{mm}$ để còn biên an toàn.

**Ghi chú về mặt phẳng gắp.** Mặt phẳng gắp–thả đặt trong dải $z \in [-425;\ -275]\,\text{mm}$ để tay quay không vượt góc giới hạn. Khoảng $125\,\text{mm}$ dưới đáy vùng làm việc dành cho giác hút ($45\,\text{mm}$), vật mẫu ($30\,\text{mm}$) và khay phân loại ($50\,\text{mm}$) [`thong-so-co-khi.md`, mục 1.2].

## 4.2 Thiết kế cơ khí

**Vật liệu và cấu trúc.** Nguyên tắc chọn vật liệu: đế cố định nặng và cứng; khâu chuyển động nhẹ nhưng đủ cứng. Khối lượng ảnh hưởng trực tiếp đến mô-men yêu cầu ở khớp (mục 4.3). Bảng 4.2 tóm tắt phương án chọn.

**Bảng 4.2.** Vật liệu và khối lượng ước tính các chi tiết chính.

| Chi tiết | Vật liệu | Khối lượng ước tính | Lý do chính |
| --- | --- | :---: | --- |
| Tấm đế cố định ($f = 346$ mm) | Nhôm 6061-T6 dày 10 mm (hoặc thép dày 8 mm) | ≈ 2,5–3 kg sau phay (phôi 480 × 480 × 10 mm ≈ 6,2 kg trước khi cắt góc) | Đứng yên nên khối lượng không tăng $\tau$; cần mô-đun đàn hồi cao để giữ ba ổ trục |
| Khung trụ và giằng | Nhôm định hình 40 × 40 mm | ≈ 4,5 kg | Hạ trọng tâm, giảm rung khi đảo chiều |
| Tay quay ($r_f$) | Nhôm 6061-T6 dày 6 mm, phay giảm tải | ≈ 110 g/tay | Chịu mô-men uốn; nhựa PLA bị từ biến nên không dùng |
| Cẳng tay ($r_e$) | Ống sợi carbon $\varnothing 8 \times \varnothing 6$ mm, dài 350 mm | ≈ 18 g/thanh | Chỉ chịu kéo–nén dọc trục; khối lượng nhỏ |
| Bàn di động ($e$) | PLA+ hoặc PETG (infill 40 %) | ≈ 45 g | Nằm xa trục quay nhất, nên giảm khối lượng là quan trọng |

Mỗi khớp chủ động dùng trục thép tôi mài $\varnothing 8\,\text{g6}$, đỡ ở hai đầu bằng hai ổ bi 688ZZ (hoặc 608ZZ) cách nhau $L = 36\,\text{mm}$. Cách lắp hai đầu nhằm giảm độ đảo của mặt phẳng quay so với lắp công-xôn. Mười hai khớp cầu M5 (SI5T/K) gắn ở hai đầu sáu thanh song song. Trục bu-lông đặt song song với $Oy_i$, kèm đệm vát và lò xo kéo khử rơ ở mỗi cặp thanh [`thong-so-co-khi.md`, mục 3].

**Quán tính.** Từ khối lượng ước tính, $J_{\text{mech}} = 0{,}00483\,\text{kg·m}^2$. Khi cộng quán tính rotor và puly, $J_{\text{eq,thực}} \approx 0{,}0066$–$0{,}0075\,\text{kg·m}^2$. Mô phỏng dùng $J = 0{,}01\,\text{kg·m}^2$, tức cao hơn $J_{\text{eq}}$ khoảng **33–52 %** (và gấp đôi $J_{\text{mech}}$). Mô phỏng vì vậy là cận trên bảo thủ cho mô-men. Hai con số chưa được thống nhất [`thong-so-co-khi.md`, mục 2].

**Dung sai chế tạo.** Bảng 4.3 là bảng dung sai đề xuất, suy từ độ nhạy của sai số điểm cuối. Cột "đóng góp" là tích của hệ số khuếch đại xấu nhất (`tom-tat-do-nhay.json`, phương pháp OAT trong `dong-hoc-delta.md`, mục 6.5c) với dung sai đề xuất. Tổng các đóng góp là cận trên tuyến tính của năm nhóm: đế và bốn khâu hình học.

**Bảng 4.3.** Dung sai chế tạo đề xuất và đóng góp cận trên vào sai số điểm cuối.

| TT | Chi tiết | Danh nghĩa | Dung sai | Hệ số khuếch đại xấu nhất (mm/mm) | Đóng góp cận trên (mm) |
| :-: | --- | :---: | :---: | :---: | :---: |
| 1 | Vị trí ổ trục đế ($R_b$, $z_A$) | 199,76 mm; $z_A = 0$ | ±0,05 mm | 3,40 | 0,170 |
| 2 | Cẳng tay $r_e$ | 400,00 mm | ±0,10 mm; chênh trong cặp ≤ 0,05 mm | 2,52 | 0,252 |
| 3 | Tay quay $r_f$ | 200,00 mm | ±0,10 mm | 1,16 | 0,116 |
| 4 | Cạnh đế $f$; góc chia | 346,00 mm; 120° | ±0,10 mm; ±0,03° | 0,97 | 0,097 |
| 5 | Cạnh bàn $e$ | 115,00 mm | ±0,15 mm | 0,97 | 0,145 |
| 6 | Khoảng cách cặp thanh $w_p$ | 50,00 mm | ±0,05 mm | `[CẦN BỔ SUNG]` | — |
| 7 | Khe hở khớp cầu và ổ bi | 0 mm | ≤ 0,03 mm | `[CẦN BỔ SUNG]` | — |
| | **Tổng** (năm nhóm, 1–5) | | | | **0,780** |

Nguồn hệ số khuếch đại: `dong-hoc-delta.md`, mục 6.5(c). Dung sai đề xuất: `thong-so-co-khi.md`, mục 4.

**Lý do suy từ độ nhạy.** Thứ tự dung sai theo hệ số khuếch đại: vị trí ổ trục đế (3,40), cẳng tay (2,52), tay quay (1,16), rồi hai cạnh tam giác (0,97). Vì vậy đế được gia công CNC liền khối với dung sai ±0,05 mm. Ba gối đỡ rời lắp bằng thước dây có thể lệch 0,5–1,0 mm, tương đương sai số điểm cuối 1,7–3,4 mm [`thong-so-co-khi.md`, mục 6]. Cạnh $f$ và $e$ được nới hơn vì sai số của chúng chia cho $\sqrt{3}$ qua $R_b$ và $r_p$.

Phép thử Monte Carlo cho thấy ở mức ±0,2 mm, 100 % vùng làm việc có $\text{P95} \le 1{,}0\,\text{mm}$. Ở mức ±0,5 mm, tỷ lệ này chỉ còn 31,57 % [`dong-hoc-delta.md`, mục 6.5(b)]. Đây là cơ sở để chọn dung sai ±0,2 mm làm điều kiện của kết luận.

**Ba dung sai của cụm cẳng tay.** Ba đại lượng này khác nhau, không mâu thuẫn: (1) dung sai chiều dài thanh (chi tiết) $\pm 0{,}10\,\text{mm}$; (2) chênh lệch chiều dài trong cùng một cặp bình hành $\le 0{,}05\,\text{mm}$; (3) độ chính xác định vị của đồ gá $\pm 0{,}05\,\text{mm}$. Cả ba đã được ghi thống nhất trong `thong-so-co-khi.md`, `BOM.md` và `README.md`.

**Góc chia của đế.** Yêu cầu trong bảng dung sai là $120^\circ \pm 0{,}03^\circ$; ghi chú gia công nêu năng lực của máy CNC đạt $\pm 0{,}01^\circ$, chặt hơn yêu cầu nên không mâu thuẫn. Bảng 4.3 dùng $\pm 0{,}03^\circ$.

**Phương án gia công.** Đế được gia công một lần gá để các lỗ ổ trục đạt $R_b$ với sai số khoảng cách tâm ≤ ±0,03 mm và góc chia $120^\circ \pm 0{,}01^\circ$ [`thong-so-co-khi.md`, mục 6]. Sáu thanh cẳng tay được cắt và keo vào đầu khớp trên đồ gá hai chốt $\varnothing 5\,\text{g6}$. Bàn di động in PLA+, lỗ khớp cầu khoan nhỏ rồi doa đến $\varnothing 5{,}0$ sau khi in.

## 4.3 Truyền động và mô-men yêu cầu

**Mô-men yêu cầu tại trục khớp.** Mô-men đỉnh động $\tau_{\max,\text{động}} = 0{,}940\,\text{N·m}$ và tốc độ góc đỉnh $\omega_{\max} = 7{,}25\,\text{rad/s}$ lấy từ mô phỏng tại $T = 0{,}32\,\text{s}$. Điểm này được chọn vì đạt chỉ tiêu bám (chương 5), không vượt $\omega_{\max}$ và có chu kỳ phù hợp (mục 4.5). Mô phỏng không có trọng lực. Mô-men trọng lực được cộng thủ công như Bảng 4.4. Ba phương án truyền động được so sánh ở Bảng 4.5.

**Bảng 4.4.** Mô-men và tốc độ yêu cầu tại trục khớp, $T = 0{,}32\,\text{s}$.

| Đại lượng | Giá trị | Đơn vị | Nguồn / cách tính |
| --- | :---: | :---: | --- |
| Mô-men động đỉnh $\tau_{\max,\text{động}}$ | 0,940 | N·m | Mô phỏng PID+FF, $J = 0{,}01$ |
| Mô-men trọng lực $\Delta\tau_g = m g r_f$ | 0,196 | N·m | $m = 0{,}1\,\text{kg}$, $g = 9{,}81$, $r_f = 0{,}2\,\text{m}$ |
| Mô-men yêu cầu $\tau_{\text{yc}}$ | 1,14 (1,136) | N·m | Cộng hai thành phần trên |
| Tốc độ góc đỉnh $\omega_{\max}$ | 7,25 | rad/s | Mô phỏng; tương đương 69,2 vòng/phút |
| Giới hạn tốc độ mô hình | 10,0 | rad/s | Ràng buộc mô hình |
| Hệ số $k_\omega = 10{,}0/7{,}25$ | 1,38 | — | Dư tốc độ so với giới hạn |

Ghi chú: $\Delta\tau_g$ là phép cộng bảo thủ, không mô phỏng trong vòng kín. Khối lượng $0{,}1\,\text{kg}$ là khối lượng quy đổi đã làm tròn từ $0{,}084$–$0{,}092\,\text{kg}$ [`thong-so-co-khi.md`, mục 2].

**Bảng 4.5.** So sánh ba phương án truyền động tại $\tau_{\text{yc}} = 1{,}14\,\text{N·m}$.

| Phương án | Tỷ số | $\tau_{\text{ra}}$ (N·m) | $k_\tau = \tau_{\text{ra}}/\tau_{\text{yc}}$ | $e_{\text{backlash}}$ (mm) | $e_{\text{enc}}$ (mm) | Kết luận |
| --- | :---: | :---: | :---: | :---: | :---: | --- |
| T1: hộp số hành tinh ≤ 5 arcmin | 5:1 | 2,48 | 2,18 | 0,291 | 0,063 | Đạt $k_\tau$ và đạt 0,803 mm sau hiệu chuẩn; không chọn vì chi phí 4,8–7,2 triệu VNĐ cho ba bộ |
| **T2: đai răng GT2 10 mm, căng đai** | **5:1** | **2,53** | **2,23** | ≈ 0 hình học; **0,100 giả thiết** | 0,063 | **Chọn** |
| T3: truyền trực tiếp, stepper vòng kín | 1:1 | 1,50 | 1,32 | 0,020 | 0,314 | Loại: $k_\tau < 2{,}0$; bước encoder quá thô |

Nguồn: `BOM.md`, mục 1.2. Hiệu suất đai (0,92) và hộp số (0,90), mô-men giữ động cơ (0,55 N·m) là giả định `[CẦN KIỂM CHỨNG]`.

**Vì sao không dùng hộp số hành tinh phổ thông.** Hộp số rẻ có độ rơ 10–15 arcmin. Sai số backlash quy đổi là $e_{\text{backlash}} \approx r_f\,\delta\theta_b$, với $r_f = 200\,\text{mm}$. Một arcmin tương đương $2{,}909 \times 10^{-4}\,\text{rad}$. Do đó 15 arcmin cho $0{,}873\,\text{mm}$ và 10 arcmin cho $0{,}582\,\text{mm}$ chỉ riêng backlash. Trước hiệu chuẩn, nhóm hệ thống của 15 arcmin là $1{,}222\,\text{mm}$, vượt ngân sách $1{,}0\,\text{mm}$ ngay cả khi chưa tính dung sai chế tạo. Ngay cả hộp số 5 arcmin cũng cho $0{,}640\,\text{mm}$ trước hiệu chuẩn, nên chỉ đạt sau hiệu chuẩn [`thong-so-co-khi.md`, mục 5.2b].

**Vì sao chọn đai GT2 5:1.** Đai GT2 có tỷ số 16T:80T và con lăn căng đai. Khe hở hình học gần bằng 0. Đàn hồi tĩnh của nhánh đai dưới tải gắp–thả được ước lượng theo $\Delta L = F L/(E A)$. Với $F = 4{,}7$–$7{,}7\,\text{N}$, $L = 120\,\text{mm}$ và $EA = 45\,000$–$73\,000\,\text{N}$, $\Delta L \approx 0{,}013\,\text{mm}$. Quy đổi qua $r_f/R_{80T} = 7{,}855$, sai số điểm cuối khoảng $0{,}100\,\text{mm}$.

Đây là **giả thiết**, không phải số đo. Mô-đun $EA$ chưa có datasheet của đai cụ thể. `[CẦN KIỂM CHỨNG BẰNG ĐO: độ giãn đai dưới tải tĩnh]`. Đây là đầu vào then chốt của kết luận ở mục 4.4.

**Mô-men động cơ và tốc độ.** Mô-men phía động cơ xấp xỉ $\tau_{\text{yc}}/(i\eta) = 1{,}14/(5 \times 0{,}92) \approx 0{,}25\,\text{N·m}$. Tốc độ: giới hạn mô hình $10\,\text{rad/s}$ tại khớp tương đương $95{,}5$ vòng/phút, qua tỷ số $5{:}1$ cần động cơ định mức $\ge 480$ vòng/phút; điểm vận hành thực chỉ cần $5 \times 69{,}2 \approx 346$ vòng/phút (giá trị đỉnh, không phải định mức). Cần động cơ có mô-men giữ $\ge 0{,}55\,\text{N·m}$ và tốc độ định mức $\ge 480$ vòng/phút; **hai thông số này chưa có datasheet** nên đánh dấu `[CẦN KIỂM CHỨNG]`. Dư tốc độ tại trục khớp là $1{,}38\times$ so với giới hạn mô hình, không phải $2\times$.

**Encoder.** Encoder 1 000 PPR, giải mã $4\times$, cho 4 000 cpr; qua tỷ số 5:1 đạt 20 000 xung/vòng tại khớp. Bước lượng tử điểm cuối $e_{\text{enc}} = 200 \times 2\pi/20\,000 = 0{,}063\,\text{mm}$, dùng trọn 1 count làm biên trên bảo thủ. Mô phỏng dùng 4 096 cpr, khác BOM nhưng chênh lệch sai số chỉ $0{,}0015\,\text{mm}$. `[CẦN BỔ SUNG: xác nhận 4 096 cpr trong mô phỏng là đặt ở trục khớp hay trục động cơ]`.

## 4.4 Ngân sách sai số

Sai số điểm cuối trên thực tế gồm bốn nguồn: dung sai chế tạo, backlash/đàn hồi truyền động, lượng tử encoder và lệch gốc khớp. Mô hình sai số hình học theo tinh thần của Vischer và Clavel [4] là cơ sở cho cách tiếp cận này. Tóm tắt của [4] không nêu đơn vị mm, nên ngân sách dưới đây là kết quả mô phỏng của nhóm, không phải đối chiếu trực tiếp với số liệu của [4]. Ba nguồn đầu quy về điểm cuối qua $r_f = 200\,\text{mm}$. Bảng 4.6 tách hai nhóm có bản chất khác nhau: nhóm **hệ thống** (cộng tuyến tính, vì có chiều xác định và lặp lại) và nhóm **ngẫu nhiên** (cộng căn bậc hai, giả thiết độc lập).

**Bảng 4.6.** Ngân sách sai số điểm cuối sau hiệu chuẩn gốc $0{,}03^\circ$, truyền đai GT2.

| Thành phần | Giá trị (mm) | Cách tính | Nhóm |
| --- | :---: | --- | :---: |
| Đàn hồi đai $e_{\text{belt}}$ | 0,100 | Giả thiết, mục 4.3 | Hệ thống |
| Lệch gốc sau hiệu chuẩn $e_{\text{home}}$ | 0,105 | $3{,}491\,\text{mm/°} \times 0{,}03°$ | Hệ thống |
| **Tổng nhóm hệ thống** $e_{\text{sys}}$ | **0,205** | Cộng tuyến tính | Hệ thống |
| Dung sai chế tạo P95 (±0,2 mm, 4 khâu) | 0,402 | Monte Carlo, 170 100 mẫu | Ngẫu nhiên |
| Lượng tử encoder $e_{\text{enc}}$ | 0,063 | 1 count bảo thủ | Ngẫu nhiên |
| **Tổng nhóm ngẫu nhiên P95** $e_{\text{rand}}$ | **0,407** | $\sqrt{0{,}402^2 + 0{,}063^2}$ | Ngẫu nhiên |
| **Tổng P95** $e_{\text{sys}} + e_{\text{rand}}$ | **0,612** | Cộng hai nhóm | — |
| Tổng khi dùng cực đại Monte Carlo 0,689 | 0,897 | $0{,}205 + \sqrt{0{,}689^2 + 0{,}063^2}$ | — |
| Tổng tuyến tính, cực đại Monte Carlo | 0,957 | $0{,}689 + 0{,}100 + 0{,}063 + 0{,}105$ | — |
| Cận trên giải tích, 4 khâu ±0,2 mm | 1,123 | $\sum \lvert g_i\rvert\delta$ | — |
| Cận trên giải tích, dung sai Bảng 4.3 | 1,048 | $0{,}780 + 0{,}100 + 0{,}063 + 0{,}105$ | — |

Nguồn: `thong-so-co-khi.md`, mục 5.2 và `tom-tat-do-nhay.json`. Các phép cộng được tính lại và khớp với bảng nguồn.

**Đọc đúng kết quả.** Có ba cách cộng, cho ba con số khác nhau:

1. Tách nhóm (kiến nghị): $0{,}612\,\text{mm}$. Đây là ước lượng P95 có điều kiện giả thiết độc lập giữa hai nhóm.
2. Tuyến tính theo cực đại Monte Carlo: $0{,}957\,\text{mm}$. Đây là cực đại quan sát trong mẫu, không phải cận trên toán học.
3. Cận trên giải tích với dung sai Bảng 4.3: $1{,}048\,\text{mm}$. Con số này **vượt** $1{,}0\,\text{mm}$.

**Điều kiện kết luận "đạt ≤ 1 mm".** Kết luận chỉ đúng khi thỏa đồng thời:

- (a) Dung sai chế tạo đạt thực tế: đế CNC ±0,05 mm, đồ gá cẳng tay, $r_e$ ±0,10 mm, hiệu chuẩn gốc ≤ ±0,03°, và đàn hồi đai ≤ 0,10 mm.
- (b) Kết luận được nêu như ước lượng thống kê P95, không phải bảo đảm cận trên. Với dung sai phân cấp, cận trên giải tích là $1{,}048\,\text{mm}$, nên không được viết "đảm bảo ≤ 1 mm".

Phương án hộp số phổ thông không đạt ở bất kỳ cách cộng nào. Phương án đai đạt P95 nhưng phụ thuộc giả thiết đàn hồi đai chưa đo.

`[CẦN BỔ SUNG: kết quả đo sai số điểm cuối trên khung thật sau quy trình hiệu chuẩn 9 điểm (thiết kế/README.md, mục 4B), và đo độ giãn đai]`.

## 4.5 Kiến trúc điều khiển và firmware

**Sơ đồ khối.** Hệ thống gồm một máy tính (PC) xử lý ảnh, sinh quỹ đạo và giải động học nghịch, và một Arduino Uno nhận góc khớp qua cổng Serial.

```
Webcam USB ──► PC (Python + OpenCV)
                 HSV → contour → homography (px → mm)
                 quỹ đạo bậc 5 + pha dừng → IK (3.6) → θ₁, θ₂, θ₃
                        │
                        │  Serial 115200 bps, 8N1: "J,t1,t2,t3\n"
                        ▼
              Arduino Uno (firmware uno-serial-servo)
                 kẹp góc [−30°, +80°] → xuất xung tức thì
                        │
                        ▼
              3 khớp chủ động (servo trong firmware hiện tại;
              stepper vòng kín trong phương án cơ khí — xem ghi chú)
```

**Giao thức.** Bảng 4.7 liệt kê hai lệnh và các ràng buộc của firmware.

**Bảng 4.7.** Giao thức Serial giữa PC và Arduino.

| Lệnh | Phản hồi | Ghi chú |
| --- | --- | --- |
| `J,<t1>,<t2>,<t3>\n` | `A,<micros>\n` | Đặt ba góc khớp (độ, cho phép âm); trả lời ngay khi nhận |
| `H\n` | `A,<micros>\n` | Về vị trí home |

Nguồn: `config.h`, `README.md` mục 2. Tốc độ 115 200 bps, 8N1. Lệnh dài nhất `J,-30.0,-30.0,-30.0\n` có 20 byte. Bộ đệm nhận 64 byte. Giới hạn kẹp góc là $[-30;\ +80]$ độ.

Firmware ghi góc ngay khi nhận lệnh, **không** chờ khớp đạt vị trí và không đọc lại vị trí. Vòng PID+FF chỉ có trong mô phỏng; firmware hiện không cài đặt vòng điều khiển [`GHICHU.md`, mục 1 và 6]. Lệnh `J` không có bước dốc (ramp). Khuyến nghị kiểm thử không nhảy $-30° \to +80°$ trong một lệnh [`GHICHU.md`, mục 6].

**Độ phân giải góc.** Hàm `writeMicroseconds()` nhận số nguyên µs; dải 500–2 500 µs quét 180°, nên 1 µs ≈ 0,09°. Servo có vùng chết khoảng 5–8 µs ≈ 0,5–0,7° [`GHICHU.md`, mục 4]. `micros()` có bước 4 µs [`GHICHU.md`, mục 5].

**Ngân sách trễ.** Bảng 4.8 phân biệt số tính, ước lượng và đo. Ngoài ra, không có số đo trễ thực tế nào trong repo.

**Bảng 4.8.** Ngân sách trễ khâu truyền thông và cơ cấu chấp hành. Chưa có số đo phần cứng.

| Khâu | Giá trị | Loại nguồn |
| --- | :---: | --- |
| Truyền lệnh `J,...` (≤ 20 byte) qua UART | 1,5–1,7 ms | `[TÍNH]` |
| Truyền phản hồi `A,<micros>` (≤ 13 byte) | 0,7–1,1 ms | `[TÍNH]` |
| Đệm USB–UART (CH340) | 1–4 ms | `[ƯỚC LƯỢNG]` |
| Lịch trình OS và Python `readline` | 1–15 ms | `[ƯỚC LƯỢNG]` |
| Tổng vòng đo bằng script | 3–20 ms, trung bình ≈ 5 ms | `[ƯỚC LƯỢNG]` |
| Trễ cơ khí servo, 110° | 0,18–0,37 s | `[DATASHEET]`, nằm **ngoài** phép đo |

Số `[ƯỚC LƯỢNG]` là dự đoán, chưa được đo. Script `do-tre-serial.py` đã viết; chạy trên board thật là bước cần làm `[CẦN BỔ SUNG: đo trễ vòng thật, n = 500, báo cáo mean/P95/P99]`. Trong run mô phỏng, khâu Serial là "~2,0 ms, dry-run, CHƯA ĐO THẬT" [`KETQUA.md` run v2, mục 4].

**Ghi chú về loại chấp hành.** Phương án cơ khí (`BOM.md`) chọn động cơ bước vòng kín có encoder. Firmware hiện tại xuất góc theo kiểu servo (xung `writeMicroseconds`) và đo trễ với servo. Hai hướng chưa được thống nhất. Trễ cơ khí servo $0{,}18$–$0{,}37\,\text{s}$ không áp dụng trực tiếp cho stepper. `[CẦN BỔ SUNG: chốt loại chấp hành; nếu stepper, cần firmware xuất xung bước/hướng và đo trễ cơ khí tương ứng]`.

**Bảng 4.9.** Phân rã chu kỳ toàn hệ thống tại $T = 0{,}32\,\text{s}$ (danh định và cận bảo thủ).

| Thành phần | Danh định (s) | P95 (s) | Nguồn |
| --- | :---: | :---: | --- |
| Chuyển động 3 đoạn $3T$ | 0,960 | 0,960 | Mô phỏng |
| Kẹp và thả: $2 \times 0{,}25$ | 0,500 | 0,500 | Danh định, `tong-quan.md` 7.1 |
| Xử lý ảnh | 0,00341 | 0,00412 | `metrics.json`, 273 mẫu |
| Chờ khung hình camera | 0,04105 | 0,07906 | `webcam_info.json`, 24,4 fps |
| Truyền Serial và phản hồi | 0,002 | 0,002 | Dry-run, **chưa đo** |
| **Tổng** | **1,506** | **1,545** | So với ngân sách 1,8 s |

Mốc đối chiếu 1,8 s/vật của Vo và Le [2] không nêu rõ có gồm xử lý ảnh, truyền thông và thời gian chấp hành hay không (chương 2). Vì vậy bảng này chỉ dùng để đối chiếu với ngân sách 1,8 s của đề tài, không so trực tiếp với [2]. Tổng P95 là cộng từng P95, nên là cận trên bảo thủ của P95 thật. Ngân sách 1,8 s còn dư $0{,}29\,\text{s}$ (danh định) và $0{,}26\,\text{s}$ (P95).

**Giả định cần ghi rõ.** Bảng 4.9 không bao gồm trễ cơ khí của cơ cấu chấp hành. Nếu cộng nối tiếp trễ servo $0{,}18$–$0{,}37\,\text{s}$, tổng danh định thành $1{,}69$–$1{,}88\,\text{s}$, vượt 1,8 s ở đầu trên. Cách cộng này là giả định bảo thủ, chưa được kiểm chứng. `[CẦN BỔ SUNG: đo trễ cơ khí của cơ cấu thật và bảng phân rã cuối cùng]`.

## 4.6 Danh mục vật tư (BOM)

Ba nhóm vật tư gồm cơ khí và khung (A), khớp–ổ bi–truyền động (B), và động cơ–điều khiển–thị giác (C). Bảng 4.10 tổng hợp khoảng giá tham khảo từ các dòng của BOM. Giá tham khảo theo thị trường Việt Nam, cần kiểm tra lại khi mua.

**Bảng 4.10.** Tổng hợp dự toán, triệu VNĐ (tham khảo).

| Nhóm | Số dòng | Khoảng cộng từ dòng | Ghi chú |
| --- | :---: | :---: | --- |
| A. Cơ khí, khung, tay quay, cẳng tay, bàn | 7 | 3,01–4,17 | Cộng từ 7 dòng nhóm A |
| B. Khớp cầu, ổ bi, trục, đai GT2 | 4 | 1,05–1,62 | Cộng từ 4 dòng nhóm B |
| C. Động cơ vòng kín, cảm biến gốc, nguồn, Arduino, thị giác | 5 | 2,64–3,55 | Cộng từ 5 dòng nhóm C |
| **Tổng** | **16** | **6,70–9,34** | Khớp tổng BOM |
| Tham chiếu (cột thành tiền) | — | **7,86** | Cộng đúng từng dòng |

Nguồn: `BOM.md`, mục 2. Khoảng giá từng nhóm cộng từ đơn giá × số lượng của các dòng tương ứng; tổng ba nhóm khớp tổng cộng của BOM (6,70–9,34 triệu) và cột thành tiền (7,86 triệu). Báo cáo dùng khoảng tổng và giá trị tham chiếu $7{,}86$ triệu VNĐ.

Các linh kiện đắt nhất là ba động cơ bước vòng kín với driver (1,65–2,10 triệu, 3 bộ) và tấm đế CNC (0,85–1,10 triệu). Phương án hộp số hành tinh chính xác cho ba bộ hộp số riêng 4,8–7,2 triệu VNĐ (`BOM.md`, mục 1.2). Gói phần cứng tối thiểu phục vụ đo trễ (webcam, Arduino Uno, nút E-stop, hộp đèn, 120 vật mẫu) khoảng 0,42 triệu VNĐ, không có khung cơ khí [`BOM.md`, mục 3].

Các thông số chưa có datasheet: mô-men giữ động cơ, độ cứng đai, khe hở khớp cầu, cấp ổ bi, quán tính rotor. Tất cả được đánh dấu `[CẦN KIỂM CHỨNG]` trong BOM.

## 4.7 Giả thiết và hạn chế của chương 4

**Giả thiết:**

1. Dung sai chế tạo đạt ±0,2 mm trên thực tế, nhờ đế CNC và đồ gá. Đây là điều kiện của kết luận sai số.
2. Đàn hồi đai tĩnh 0,100 mm theo mô hình thanh chịu kéo, chưa đo.
3. Sai số hệ thống và ngẫu nhiên độc lập khi cộng theo tách nhóm.
4. Mô-men trọng lực 0,196 N·m là cộng thủ công; mô-men động dùng quán tính giả định $0{,}01\,\text{kg·m}^2$.
5. Hiệu chuẩn gốc đạt $0{,}03^\circ$ bằng quy trình 9 điểm.

**Hạn chế:**

- Chưa có số đo trễ Serial hay trễ cơ cấu chấp hành trên phần cứng. Mọi số trễ trong chương là ước lượng hoặc dry-run.
- Chưa có số đo độ chính xác điểm cuối trên khung thật. Kết luận "≤ 1 mm" là ước lượng thống kê có điều kiện.
- Mô hình khớp không có trọng lực và tương tác chéo. Quán tính giả định khác ước tính khối lượng thực.
- Firmware hiện xuất góc không có ramp và không có vòng điều khiển vị trí. Loại chấp hành (servo hay stepper) chưa được chốt.
- Mâu thuẫn dung sai $r_e$ và nhận định dư tốc độ trong BOM cần sửa trước khi nộp.
