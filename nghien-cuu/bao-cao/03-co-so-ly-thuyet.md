# Chương 3. Cơ sở lý thuyết và phương pháp

> **Bản nháp để sinh viên kiểm chứng — không phải bản nộp.** Mọi số liệu lấy từ `nghien-cuu/` trong repo; nguồn ghi trong ngoặc khi cần. Chỗ thiếu dữ liệu được đánh dấu `[CẦN BỔ SUNG]`.

Chương này trình bày các mô hình mà đề tài dùng: cấu trúc cơ cấu (3.1), động học nghịch và thuận (3.2–3.3), quy hoạch quỹ đạo (3.4), mô hình khớp và bộ điều khiển (3.5), và chuỗi thị giác máy tính (3.6). Cuối chương liệt kê giả thiết và hạn chế.

## 3.1 Cấu trúc robot Delta 3 bậc tự do

Robot Delta là cơ cấu song song (*parallel mechanism*) ba bậc tự do tịnh tiến, do Clavel đề xuất [1]. Cơ cấu gồm một đế cố định, ba khớp quay chủ động đặt trên đế, ba tay quay và ba cặp cẳng tay song song nối tới bàn di động. Ba khớp chủ động đặt tại ba đỉnh của tam giác đều, lệch nhau $120^\circ$ quanh trục $Oz$.

Mỗi nhánh gồm một tay quay dài $r_f$ và hai thanh song song dài $r_e$, cách nhau $w_p = 50\,\text{mm}$. Hai thanh cùng chiều dài và song song tạo thành hình bình hành phẳng. Hình bình hành giữ cạnh bàn di động song song với cạnh tương ứng của đế. Khi cả ba nhánh cùng ràng buộc như vậy, bàn di động bị khóa ba góc quay ($\alpha = \beta = \gamma = 0$) và chỉ còn ba bậc tự do tịnh tiến $(x, y, z)$. Đầu gắp nhờ đó luôn thẳng đứng, không cần thêm cổ tay.

Hai đầu mỗi thanh song song phải dùng khớp cầu (*ball joint*). Khớp bản lề một bậc tự do không cho thanh nghiêng ngang khi bàn di động lệch khỏi mặt phẳng nhánh. Điều kiện hình học là $|y_i| \le r_e$ với $y_i$ là độ lệch ngang so với mặt phẳng nhánh $i$ [`dong-hoc-delta.md`, mục 3.2].

Các tham số hình học chốt được trình bày ở Bảng 4.1 (chương 4). Từ $f$ và $e$ suy ra bán kính ngoại tiếp:

$$R_b = \frac{f}{\sqrt{3}} = 199{,}76\ \text{mm}, \qquad r_p = \frac{e}{\sqrt{3}} = 66{,}40\ \text{mm}, \qquad R = R_b - r_p = 133{,}37\ \text{mm} \tag{3.1}$$

Vùng làm việc là hình trụ $\varnothing 300 \times 150\,\text{mm}$ với $z \in [-425;\, -275]\,\text{mm}$ [`dong-hoc-delta.md`, mục 5.1].

## 3.2 Động học nghịch giải tích

**Bài toán.** Cho vị trí điểm tác động cuối $\mathbf{p} = [x, y, z]^T$, tìm ba góc khớp $\theta_i$. Quy ước: $\theta_i = 0$ khi tay quay nằm ngang hướng $+Ox_i$; $\theta_i > 0$ khi tay quay chúc xuống.

**Bước 1 — Chiếu về hệ địa phương.** Ràng buộc chiều dài cẳng tay là $\|\mathbf{p} - \mathbf{c}_i(\theta_i)\|^2 = r_e^2$, với tâm mặt cầu ảo $\mathbf{c}_i(\theta_i) = [(R + r_f\cos\theta_i)\cos\phi_i,\ (R + r_f\cos\theta_i)\sin\phi_i,\ -r_f\sin\theta_i]^T$. Chiếu $\mathbf{p}$ vào hệ địa phương nhánh $i$ bằng phép quay $\mathbf{R}_z^T(\phi_i)$:

$$x_i = x\cos\phi_i + y\sin\phi_i, \qquad y_i = -x\sin\phi_i + y\cos\phi_i, \qquad z_i = z \tag{3.2}$$

**Bước 2 — Phương trình lượng giác tuyến tính.** Khai triển và dùng $\cos^2 + \sin^2 = 1$ thu được:

$$E_i\cos\theta_i + F_i\sin\theta_i + G_i = 0 \tag{3.3}$$

$$E_i = -2r_f(x_i - R), \qquad F_i = 2r_f z_i, \qquad G_i = (x_i - R)^2 + y_i^2 + z_i^2 + r_f^2 - r_e^2 \tag{3.4}$$

**Bước 3 — Thế nửa góc.** Đặt $t_i = \tan(\theta_i/2)$, phương trình (3.3) trở thành bậc hai:

$$(G_i - E_i)\,t_i^2 + 2F_i\,t_i + (G_i + E_i) = 0 \tag{3.5}$$

Biệt thức rút gọn là $\Delta_i = E_i^2 + F_i^2 - G_i^2$. Điều kiện để điểm $\mathbf{p}$ nằm trong không gian khả đạt là $\Delta_i \ge 0$ với mọi $i$.

**Bước 4 — Chọn nhánh và dạng số ổn định.** Đề tài chọn nhánh khuỷu hướng ra ngoài (*elbow-out*) cho cả ba nhánh, tức $\cos\theta_i > 0$. Với dạng trực tiếp $t_i = (-F_i - \sqrt{\Delta_i})/(G_i - E_i)$, mẫu số tiến tới 0 khi $x_i \to R$ và $y_i^2 + z_i^2 \to r_e^2 - r_f^2$. Khi đó tử số là hiệu hai số gần bằng nhau, gây mất chữ số có nghĩa. Dùng định lý Viète để đổi sang dạng Citardauq:

$$t_i = \frac{-F_i - \sqrt{\Delta_i}}{G_i - E_i} \equiv \frac{G_i + E_i}{-F_i + \sqrt{\Delta_i}}, \qquad \theta_i = 2\arctan t_i \tag{3.6}$$

Trong vùng làm việc có $z < 0$, nên $F_i < 0$ và $-F_i + \sqrt{\Delta_i} \ge |F_i| > 0$. Mẫu số không bao giờ triệt tiêu, nên dạng (3.6) tránh được phép trừ gần bằng nhau. Các ký hiệu và đơn vị được tổng hợp ở Bảng 3.1.

**Bảng 3.1.** Ký hiệu và đơn vị trong động học nghịch.

| Ký hiệu | Ý nghĩa | Đơn vị |
| --- | --- | :---: |
| $\mathbf{p} = [x, y, z]^T$ | Vị trí điểm tác động cuối | mm |
| $\theta_i$ | Góc khớp chủ động, $i = 1, 2, 3$ | rad (hoặc $^\circ$) |
| $f$, $e$ | Cạnh tam giác đế cố định, cạnh tam giác bàn di động | mm |
| $r_f$, $r_e$ | Chiều dài tay quay, chiều dài cẳng tay | mm |
| $R$ | Hiệu bán kính $R_b - r_p$ | mm |
| $E_i$, $F_i$, $G_i$ | Hệ số trung gian (3.4) | mm² |
| $t_i$ | $\tan(\theta_i/2)$ | — |
| $\Delta_i$ | Biệt thức (điều kiện tồn tại nghiệm) | mm⁴ |

Lưu ý: mô hình tính bằng mm; các công thức trong báo cáo giữ đơn vị SI với tiền tố mm. Hồ sơ mô hình ghi rằng dạng trực tiếp làm sai số vòng kín "nhảy lên khoảng $10^{-10}$ mm" [`dong-hoc-delta.md`, mục 3.2]. Tuy nhiên, repo chưa có phép so sánh số hai dạng trên cùng một lưới. `[CẦN BỔ SUNG: sai số IK→FK của dạng trực tiếp và dạng Citardauq trên cùng lưới điểm]`.

## 3.3 Động học thuận

**Bài toán.** Cho ba góc khớp, tìm $\mathbf{p}$. Từ $\theta_i$ suy ra ba tâm mặt cầu $\mathbf{c}_i$, rồi $\mathbf{p}$ là giao điểm của ba mặt cầu bán kính $r_e$. Hai nghiệm đối xứng qua mặt phẳng chứa ba tâm. Mô hình chọn nghiệm nằm dưới đế ($z < 0$) [`dong-hoc-delta.md`, giả thiết 3].

Động học thuận là hệ phương trình phi tuyến. Yang và Xiao [3] giải bài này bằng phương pháp số. Đề tài dùng hai cách giải độc lập để kiểm chứng nhau.

**(a) Giải tích.** Trừ từng cặp phương trình mặt cầu để khử các số hạng bậc hai. Thu được hai mặt phẳng, từ đó biểu diễn $x = u_x + v_x z$ và $y = u_y + v_y z$. Thế vào phương trình mặt cầu thứ nhất được phương trình bậc hai $A_q z^2 + B_q z + C_q = 0$. Nghiệm vật lý là nghiệm nhỏ hơn:

$$z = \frac{-B_q - \sqrt{B_q^2 - 4A_qC_q}}{2A_q} \tag{3.7}$$

**(b) Newton–Raphson.** Đặt $F_i(\mathbf{p}) = \|\mathbf{p} - \mathbf{c}_i\|^2 - r_e^2$ và $\mathbf{F} = [F_1, F_2, F_3]^T$. Bước lặp là $\mathbf{p}_{k+1} = \mathbf{p}_k - \mathbf{J}_F(\mathbf{p}_k)^{-1}\mathbf{F}(\mathbf{p}_k)$, với hàng $i$ của $\mathbf{J}_F$ bằng $2(\mathbf{p} - \mathbf{c}_i)^T$.

**Kiểm chứng chéo IK ↔ FK.** Lưới đều gồm 1 859 điểm trong hình trụ $\varnothing 300 \times 150\,\text{mm}$ (11 mặt cắt $z$ × 169 điểm). Kết quả được tóm tắt ở Bảng 3.2.

**Bảng 3.2.** Kết quả kiểm chứng chéo trên 1 859 điểm lưới.

| Chỉ tiêu | Giá trị | Nguồn |
| --- | :---: | --- |
| Điểm có nghiệm IK hợp lệ | 1 859 / 1 859 (100 %) | `tom-tat-kiem-chung.json` |
| Sai số vòng kín cực đại, FK giải tích (mm) | $1{,}583 \times 10^{-13}$ | `tom-tat-kiem-chung.json` |
| Sai số vòng kín cực đại, FK Newton–Raphson (mm) | $1{,}836 \times 10^{-13}$ | `tom-tat-kiem-chung.json` |
| Độ lệch cực đại giữa hai bộ giải (mm) | $1{,}729 \times 10^{-13}$ | `tom-tat-kiem-chung.json` |
| Điểm Newton–Raphson không hội tụ | 0 / 1 859 | `dong-hoc-delta.md`, mục 6.4 |
| Số vòng lặp Newton–Raphson, trung bình / tối đa | 5,73 / 6 | `tom-tat-kiem-chung.json` |

Kiểm tra đại số bằng SymPy cho sai số đa thức bằng 0 [`dong-hoc-delta.md`, mục 3]. Các kết quả trên cho thấy cặp IK–FK nhất quán và nghiệm FK hội tụ trên toàn vùng làm việc. Chúng **không** chứng minh độ chính xác vật lý của robot. Độ chính xác vật lý được ước lượng bằng ngân sách sai số ở mục 4.4.

## 3.4 Quy hoạch quỹ đạo đa thức bậc 5

Mỗi đoạn chuyển động dùng đa thức bậc 5 chuẩn hóa theo thời gian $\tau = t/T \in [0, 1]$:

$$s(\tau) = 10\tau^3 - 15\tau^4 + 6\tau^5 \tag{3.8}$$

Đa thức (3.8) thỏa $s(0) = 0$, $s(1) = 1$, $\dot s(0) = \dot s(1) = 0$ (vận tốc bằng 0 tại hai đầu) và $\ddot s(0) = \ddot s(1) = 0$ (gia tốc bằng 0 tại hai đầu). Hai điều kiện sau bảo đảm robot dừng êm ở mỗi điểm mốc. Đỉnh vận tốc và gia tốc của đa thức chuẩn bằng $1{,}875\,\Delta/T$ và $10/\sqrt{3}\,\Delta/T^2 \approx 5{,}77\,\Delta/T^2$, với $\Delta$ là quãng đường đoạn.

Chu trình gồm ba đoạn `home → pick`, `pick → place`, `place → home`, tổng thời gian chuyển động $3T$. Quỹ đạo được nội suy trong không gian thao tác, sau đó mỗi mẫu được đổi sang góc khớp bằng động học nghịch (3.6) [`run.py`, lớp `JointReferenceInterpolator`]. Tại `pick` và `place` robot dừng một pha $t_{\text{dwell}} = 0{,}25\,\text{s}$ để kẹp và thả vật. Giá trị này là danh định, chọn trong dải $0{,}2$–$0{,}3\,\text{s}$ từ `tai-lieu/tong-quan.md`, mục 7.1; chưa có số đo thực nghiệm.

**Vì sao cần pha dừng.** Chỉ tiêu vọt lố (*overshoot*) và thời gian xác lập chỉ có nghĩa khi đo trong một cửa sổ robot đã tới đích. Bản chạy đầu (`2026-11-18-pid-quy-dao-bac5`) đo cửa sổ kéo sang đoạn kế tiếp. Kết quả ghi vọt lố $6{,}52\,\text{mm}$, lớn hơn cả sai số bám cực đại $1{,}158\,\text{mm}$ của cùng lần chạy. Đại lượng đó là khoảng cách robot **rời** đích, không phải vọt lố [`mo-phong/runs/2026-11-24-pid-v2-dung-nghi/KETQUA.md`, mục 1].

Bản v2 khắc phục bằng cách đo trong cửa sổ $[t_{\text{đến}},\ t_{\text{đến}} + t_{\text{dwell}}]$. Gọi $\hat{\mathbf{u}}$ là hướng tiếp cận từ điểm mốc trước tới đích, vọt lố được định nghĩa:

$$\text{OS} = \max\Big(0,\ \max_{t \in \text{dwell}} \big(\mathbf{p}(t) - \mathbf{p}_{\text{đích}}\big)\cdot\hat{\mathbf{u}}\Big) \tag{3.9}$$

Sai số cuối pha dừng cũng được đo, vì đây là đại lượng quyết định robot có kẹp đúng vật hay không.

## 3.5 Mô hình khớp và điều khiển

**Mô hình khớp.** Mỗi khớp chủ động được mô hình hóa là khối quán tính–nhớt:

$$J\,\ddot\theta + b\,\dot\theta = \tau \tag{3.10}$$

với $J = 0{,}01\,\text{kg·m}^2$, $b = 0{,}05\,\text{N·m·s/rad}$ là giá trị giả định trong `config.json`. Mô-men bị giới hạn $|\tau| \le 2{,}0\,\text{N·m}$ và tốc độ góc bị giới hạn $\omega_{\max} = 10\,\text{rad/s}$ như ràng buộc của mô hình.

**Bộ điều khiển PID và bù tiến.** Luật điều khiển là:

$$\tau = K_p\,e + K_i\int e\,dt + K_d\,\dot e_\omega + \underbrace{J\,\ddot\theta_{\text{ref}} + b\,\dot\theta_{\text{ref}}}_{\text{bù tiến (feed-forward)}} \tag{3.11}$$

Trong đó $e = \theta_{\text{ref}} - \theta$ và $\dot e_\omega = \omega_{\text{ref}} - \omega$. Hệ số là $K_p = 80$, $K_i = 5$, $K_d = 4$ (`config.json`). Khi mô-men chạm giới hạn, thành phần tích phân được đóng băng để tránh bão hòa tích phân (*anti-windup*). Phần bù tiến dùng mô hình (3.10) để tính mô-men cần thiết trên quỹ đạo tham chiếu.

**Lượng tử hóa encoder.** Phản hồi góc được lượng tử hóa theo bước $2\pi/4\,096 \approx 1{,}53\,\text{mrad}$ (`config.json`, `encoder_counts_per_rev = 4096`). Theo `KETQUA.md` (run v2, mục 6), chỉ tiêu sai số 1 mm hiện do độ phân giải encoder quyết định. Thí dụ với $T = 0{,}30\,\text{s}$, RMSE là $0{,}0813\,\text{mm}$ khi bật lượng tử hóa và $0{,}0001\,\text{mm}$ khi tắt.

**Vì sao cần bù tiến.** Ở $T = 0{,}50\,\text{s}$, PID thuần cho sai số bám cực đại $1{,}137\,\text{mm}$, vượt chỉ tiêu 1 mm. PID cộng bù tiến cho $0{,}186\,\text{mm}$ [`KETQUA.md`, mục 2]. Baseline PID có bù tiến tương tự được Castañeda và cộng sự [5] dùng khi so với ADRC thích nghi. Hai công trình ADRC [5], [6] không công bố số liệu PID định lượng trên quỹ đạo gắp–thả (chương 2).

**Bảng 3.3.** Tham số mô hình khớp và bộ điều khiển (`config.json`).

| Tham số | Ký hiệu | Giá trị | Đơn vị |
| --- | :---: | :---: | :---: |
| Mô-men quán tính khớp (giả định) | $J$ | 0,01 | kg·m² |
| Hệ số nhớt | $b$ | 0,05 | N·m·s/rad |
| Giới hạn mô-men | $\tau_{\max}$ | 2,0 | N·m |
| Giới hạn tốc độ góc | $\omega_{\max}$ | 10,0 | rad/s |
| Hệ số tỷ lệ / tích phân / vi phân | $K_p$ / $K_i$ / $K_d$ | 80 / 5 / 4 | N·m/rad; N·m/(rad·s); N·m·s/rad |
| Độ phân giải encoder | — | 4 096 | xung/vòng |
| Bước mô phỏng | $\Delta t$ | 1 | ms (`simulation.dt_s`) |

## 3.6 Thị giác máy tính

Chuỗi xử lý ảnh gồm bốn bước: chuyển không gian màu, phân ngưỡng, lọc contour, và trích đặc trưng hình học. Cách tiếp cận này là ngưỡng HSV kết hợp contour, không dùng học sâu [2], [7].

**Phân ngưỡng màu.** Ảnh BGR được đổi sang HSV. Ngưỡng ban đầu cho ba màu được cho ở Bảng 3.4. Các ngưỡng này lấy từ `mo-phong/runs/2026-11-18-thi-giac-hsv/KETQUA.md`, mục 1. Chúng được tinh chỉnh trên tập huấn luyện và validation gồm ảnh tổng hợp.

**Bảng 3.4.** Ngưỡng HSV ban đầu cho ba màu.

| Màu | Hue $H$ | Saturation $S \ge$ | Value $V \ge$ |
| --- | :---: | :---: | :---: |
| Đỏ | $[0, 10] \cup [170, 180]$ | 100 | 50 |
| Vàng | $[20, 40]$ | 100 | 50 |
| Xanh lá | $[100, 140]$ | 80 | 50 |

**Lọc contour và đặc trưng hình học.** Contour được lọc theo diện tích tương đối trong khoảng $[0{,}0002;\ 0{,}70]$. Bốn đặc trưng được tính cho mỗi vật, với $A$ là diện tích, $P$ là chu vi:

$$\text{circularity} = \frac{4\pi A}{P^2}, \qquad \text{extent} = \frac{A}{A_{\text{bbox}}}, \qquad \text{solidity} = \frac{A}{A_{\text{hull}}} \tag{3.12}$$

Số cạnh được xác định bằng `cv2.approxPolyDP` với $\varepsilon = 0{,}025\,P$. Phân bố góc tại các đỉnh phân biệt vuông (góc khoảng $90^\circ$) với tam giác (ba góc nhọn) [`KETQUA.md`, mục 1].

**Chuyển đổi pixel sang mm.** Ma trận homography được xác định từ bốn điểm mốc, giả định vùng làm việc $300 \times 200\,\text{mm}$. Đây là giả định của mô phỏng, chưa phải hiệu chuẩn trên bàn thật. `[CẦN BỔ SUNG: hiệu chuẩn homography trên bàn thí nghiệm, kèm sai số đo]`.

**Hạn chế của chuỗi thị giác.** Mọi số liệu thị giác hiện có là ảnh tổng hợp do nhóm tạo bằng OpenCV/NumPy. Repo chưa có vật mẫu thật. Ngưỡng cụ thể của các đặc trưng hình học (circularity, solidity, góc đỉnh) nằm trong mã, không được ghi trong tài liệu tóm tắt. `[CẦN BỔ SUNG: ngưỡng quyết định cho từng đặc trưng, lấy từ mã nguồn]`.

## 3.7 Giả thiết và hạn chế của chương 3

**Giả thiết:**

1. Các khâu là vật rắn tuyệt đối; độ võng đàn hồi không được mô hình hóa [`dong-hoc-delta.md`, giả thiết 1].
2. Hình học danh định và khe hở khớp bằng 0 trong mô hình; sai số chế tạo được xét riêng ở mục 4.4.
3. Ba nhánh chọn nghiệm khuỷu hướng ra ngoài; FK chọn nghiệm dưới đế.
4. Mô hình khớp tách rời: bỏ qua trọng lực, tương tác chéo giữa ba khớp, và ma sát Coulomb.
5. Pha dừng 0,25 s là giá trị danh định.
6. Ảnh thị giác là ảnh tổng hợp với điều kiện chiếu sáng giả định.

**Hạn chế:**

- Mô hình khớp không có trọng lực. Mô-men trọng lực được cộng thủ công ở mục 4.3 (Bảng 4.4); phần này không được mô phỏng.
- Quán tính $J = 0{,}01\,\text{kg·m}^2$ là giả định bảo thủ. Ước tính khối lượng thực cho $J_{\text{eq}} \approx 0{,}0066$–$0{,}0075\,\text{kg·m}^2$ [`thong-so-co-khi.md`, mục 2]. Hai mô hình chưa được thống nhất.
- Chưa có dữ liệu đo động cơ hay đo trễ thực tế để kiểm chứng mô hình khớp.
- Kết quả động học trong chương này đến từ kiểm chứng đại số và mô phỏng Monte Carlo trên máy tính, không phải đo trên khung robot thật.
