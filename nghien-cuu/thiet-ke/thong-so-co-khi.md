# Thông số Thiết kế Cơ khí, Dung sai Chế tạo và Phương án Gia công Robot Delta 3-DOF

**Đề tài:** Nghiên cứu và mô phỏng robot Delta cho ứng dụng phân loại sản phẩm bằng camera  
**Nguồn số liệu truy nguyên:**
- Mô hình động học & vùng làm việc: `nghien-cuu/mo-hinh/dong-hoc-delta.md`, `nghien-cuu/mo-hinh/ket-qua/tom-tat-kiem-chung.json`
- Khảo sát độ nhạy sai số hình học (Monte Carlo & OAT): `nghien-cuu/mo-hinh/ket-qua/tom-tat-do-nhay.json`
- Động lực học & yêu cầu mô-men/vận tốc: `nghien-cuu/mo-phong/runs/2026-11-18-pid-quy-dao-bac5/output/metrics.json` và `config.json`
- Giới hạn hành trình khớp trong phần cứng nhúng: `nghien-cuu/firmware/uno-serial-servo/config.h`

---

## 1. Bảng kích thước hình học và kết cấu chính

Toàn bộ kích thước động học được giữ nguyên 100 % từ kết quả kiểm chứng chéo $\text{IK} \leftrightarrow \text{FK}$ trên $1\,859$ điểm lưới (đạt độ bao phủ $100\,\%$ hình trụ $\varnothing 300 \times 150\text{ mm}$, số điều kiện Jacobian chuẩn hóa $\kappa(\hat{J}) \in [1,013;\ 1,981]$, góc truyền lực nhỏ nhất $\gamma_{\min} = 39,00^\circ \ge 25^\circ$).

| Hạng mục / Tham số | Ký hiệu | Giá trị thiết kế (mm / deg) | Giá trị chuẩn SI | Giải thích & Ràng buộc kết cấu |
| --- | :---: | :---: | :---: | --- |
| Cạnh tam giác đều đế cố định | $f$ | $346,00\text{ mm}$ | $0,3460\text{ m}$ | Khoảng cách tâm 3 khớp quay chủ động $A_1, A_2, A_3$ đặt tại 3 đỉnh tam giác đều. |
| Bán kính ngoại tiếp khớp đế cố định | $R_b = f/\sqrt{3}$ | $199,76\text{ mm}$ ($\approx 199,8\text{ mm}$) | $0,1998\text{ m}$ | Khoảng cách từ tâm $O(0,0,0)$ tới trục quay của mỗi khớp chủ động $A_i$. |
| Cạnh tam giác đều bàn di động | $e$ | $115,00\text{ mm}$ | $0,1150\text{ m}$ | Khoảng cách tâm 3 cụm khớp cầu $P_1, P_2, P_3$ trên bàn di động (moving platform). |
| Bán kính ngoại tiếp bàn di động | $r_p = e/\sqrt{3}$ | $66,40\text{ mm}$ ($\approx 66,4\text{ mm}$) | $0,0664\text{ m}$ | Khoảng cách từ tâm bàn di động $P$ tới đường tâm cụm khớp cầu nhánh $i$. |
| Hiệu bán kính hình học quy đổi | $R = R_b - r_p$ | $133,37\text{ mm}$ | $0,1334\text{ m}$ | Tham số trực tiếp trong phương trình mặt cầu ảo $\mathbf{c}_i(\theta_i)$. |
| Chiều dài tay quay chủ động (*upper arm*) | $r_f$ | $200,00\text{ mm}$ | $0,2000\text{ m}$ | Khoảng cách tâm trục khớp đế $A_i$ đến đường tâm trục khớp khuỷu $B_i$. |
| Chiều dài cẳng tay song song (*lower arm*) | $r_e$ | $400,00\text{ mm}$ | $0,4000\text{ m}$ | Khoảng cách tâm–tâm giữa 2 đầu khớp cầu (rod-end) trên mỗi thanh truyền ($r_e / r_f = 2,0$). |
| Khoảng cách ngang 2 thanh trong 1 cặp cẳng | $w_p$ | $50,00\text{ mm}$ | $0,0500\text{ m}$ | Bề rộng cơ cấu hình bình hành tại khuỷu $B_i$ và bàn di động $P_i$, chống xoắn quanh trục $Oz$. |
| Đường kính × Chiều cao vùng làm việc | $D_{\text{ws}} \times H_{\text{ws}}$ | $\varnothing 300,0 \times 150,0\text{ mm}$ | $\varnothing 0,30 \times 0,15\text{ m}$ | Không gian thao tác hình trụ chuẩn theo mục tiêu đề cương (`de-tai.md`). |
| Dải cao độ vùng làm việc (theo trục $Oz$) | $[z_{\min}, z_{\max}]$ | $[-425,0;\ -275,0]\text{ mm}$ | $[-0,425;\ -0,275]\text{ m}$ | Tâm vùng làm việc đặt tại $\mathbf{p}_0 = (0, 0, -350,0)\text{ mm}$ ($\theta_{i,0} = +20,66^\circ$). |
| Dải góc khớp thực tế / Giới hạn phần mềm | $[\theta_{\min}, \theta_{\max}]$ | $[-27,05^\circ, +77,30^\circ]$ / $[-30^\circ, +80^\circ]$ | $[-0,472, +1,349]\text{ rad}$ | Dải góc quét trong $\varnothing 300 \times 150\text{ mm}$ nằm lọt trong giới hạn kẹp của `config.h` (`-30.0f` đến `+80.0f`). |
| Khoảng hở phía trên mặt phẳng khớp đế | $h_{\text{top}}$ | $\ge 115,0\text{ mm}$ | $\ge 0,1150\text{ m}$ | Khi tay quay ngóc lên cực đại $\theta = -30^\circ$, khuỷu $B_i$ nhô cao $+r_f \sin 30^\circ = +100,0\text{ mm}$ so với mặt $z=0$; cộng $15\text{ mm}$ dự trữ an toàn. |
| Chiều cao mặt phẳng khớp đế so với mặt bàn | $H_{\text{base}}$ | $550,0\text{ mm}$ | $0,5500\text{ m}$ | Tính từ mặt bàn thí nghiệm ($z_{\text{table}} = -550\text{ mm}$) lên mặt phẳng chứa 3 trục khớp $A_i$ ($z = 0$). |
| Khoảng hở làm việc dưới bàn di động | $h_{\text{clear}}$ | $125,0 \div 275,0\text{ mm}$ | $0,125 \div 0,275\text{ m}$ | Tại đáy vùng làm việc ($z_{\min} = -425\text{ mm}$), còn $550 - 425 = 125\text{ mm}$ để lắp giác hút/nam châm ($45\text{ mm}$), chiều cao vật mẫu ($30\text{ mm}$) và mặt băng tải/khay phân loại ($50\text{ mm}$). |
| Tổng chiều cao 3 trụ đứng khung máy | $H_{\text{frame}}$ | $600,0\text{ mm}$ | $0,6000\text{ m}$ | Dùng 3 thanh nhôm định hình $40 \times 40\text{ mm}$ dài $600\text{ mm}$ đặt ngoài bán kính quét của tay quay ($R_{\text{trụ}} = 280\text{ mm}$). |

---

## 2. Lựa chọn vật liệu từng chi tiết (Dẫn giải từ bài toán động lực học & mô-men)

Trong mô phỏng điều khiển quỹ đạo đa thức bậc 5 (`nghien-cuu/mo-phong/runs/2026-11-18-pid-quy-dao-bac5/config.json` và `output/metrics.json`), mô-men quán tính quy đổi về mỗi trục khớp chủ động được giả định là $J_{\text{eq}} = 0,01\text{ kg}\cdot\text{m}^2$, sinh ra mô-men cực đại:
- **Ở chu kỳ chuẩn $T_{\text{cycle}} = 1,5\text{ s}$:** $\tau_{\max} = 0,457\text{ N}\cdot\text{m}$ (với bộ điều khiển `PID_can_bang`), vận tốc góc đỉnh $\omega_{\max} = 4,66\text{ rad/s}$.
- **Ở chu kỳ giới hạn $T_{\text{cycle}} = 0,696\text{ s}$:** $\tau_{\max} = 1,636\text{ N}\cdot\text{m}$, vận tốc góc đỉnh $\omega_{\max} = 9,99\text{ rad/s}$.

Mô-men quán tính quy đổi về trục khớp thứ $i$ của robot Delta được xấp xỉ bởi:
$$J_{\text{eq},i} \approx J_{\text{rotor}} + J_{\text{tay\_quay}} + \left( m_{\text{khuỷu}} + \frac{2}{3} m_{\text{cẳng}} + \frac{1}{3} (m_{\text{bàn}} + m_{\text{tải}}) \right) r_f^2$$
Vì $r_f = 0,200\text{ m}$ ($r_f^2 = 0,04\text{ m}^2$), **cứ mỗi $100\text{ g}$ khối lượng tăng thêm ở bàn di động hoặc khớp khuỷu sẽ làm tăng mô-men cản tĩnh thêm $\Delta \tau_g = m g r_f \approx 0,1 \times 9,81 \times 0,2 = 0,196\text{ N}\cdot\text{m}$** (tương đương $43\,\%$ tổng mô-men $\tau_{\max} = 0,457\text{ N}\cdot\text{m}$ ở chu kỳ $1,5\text{ s}$). Do đó, nguyên tắc chọn vật liệu là: **Đế cố định phải nặng và cứng vững tuyệt đối; các khâu chuyển động ($r_f, r_e, e$) phải nhẹ nhất có thể nhưng đủ độ cứng chống võng.**

| Chi tiết cơ khí | Vật liệu lựa chọn | Khối lượng ước tính | Lý do kỹ thuật (Liên hệ tới $\tau$, độ cứng và giả thiết vật rắn) |
| --- | --- | :---: | --- |
| **1. Tấm đế cố định ($f = 346\text{ mm}$) & Gối đỡ ổ trục $A_i$** | **Nhôm hợp kim 6061-T6** dày $10\text{ mm}$ (hoặc thép tấm CT3/S45C cắt laser dày $8\text{ mm}$ cho bản tiết kiệm) | $\sim 2,8\text{ kg}$ (Nhôm) / $\sim 6,2\text{ kg}$ (Thép) | Khâu đứng yên ($\dot{\theta} = 0$) nên khối lượng không làm tăng $\tau$. Cần mô-đun đàn hồi cao ($E = 69\text{ GPa}$ với nhôm 6061) để không bị rung hoặc biến dạng nhiệt, giữ cứng vị trí 3 ổ trục $A_1, A_2, A_3$ vốn có độ nhạy sai số lớn nhất ($3,40\text{ mm/mm}$). |
| **2. Khung trụ đỡ & Giằng chân đế** | **Nhôm định hình $40 \times 40\text{ mm}$** (3 trụ đứng $600\text{ mm}$ + 6 thanh giằng ngang) kèm ke góc đúc | $\sim 4,5\text{ kg}$ | Hạ thấp trọng tâm hệ thống, triệt tiêu rung động khung khi 3 tay quay đảo chiều gia tốc ở chu kỳ $1,5\text{ s}$. Dễ căn chỉnh độ phẳng mặt đế bằng chân tăng chỉnh. |
| **3. Tay quay chủ động ($r_f = 200\text{ mm}$)** | **Nhôm hợp kim 6061-T6** dày $6\text{ mm}$ phay hạ bậc tạo tiết diện chữ I / khoét lỗ giảm tải (hoặc hộp nhôm định hình $20 \times 20\text{ mm}$) | $\sim 110\text{ g} / \text{tay}$ | Chịu toàn bộ mô-men uốn $\tau_{\max} = 0,457 \div 1,636\text{ N}\cdot\text{m}$ và lực dọc từ hộp số động cơ. Không dùng nhựa in 3D PLA cho phần thân tay quay vì PLA bị biến dạng từ biến (creep) và xoắn đàn hồi dưới tải động, gây sai lệch góc $\theta_i$. |
| **4. Thanh cẳng tay song song ($r_e = 400\text{ mm}$, 6 thanh)** | **Ống sợi carbon rỗng** $\varnothing 8 \times \varnothing 6\text{ mm}$ (hoặc ống nhôm 6061 $\varnothing 8 \times 1\text{ mm}$ cho phương án giá rẻ) kết hợp 2 đầu nối ren nhôm/in 3D | $\sim 18\text{ g} / \text{thanh}$ ($36\text{ g} / \text{cặp}$) | Trong cơ cấu hình bình hành Delta, thanh $r_e$ chỉ chịu **kéo – nén dọc trục thuần túy**, không chịu uốn. Ống carbon có tỷ số độ cứng/khối lượng cao nhất, giảm khối lượng quy đổi về khuỷu tay, đảm bảo giả thiết vật rắn tuyệt đối (độ võng $< 0,05\text{ mm}$ theo Mục 2 `dong-hoc-delta.md`). |
| **5. Bàn di động ($e = 115\text{ mm}$)** | **Nhựa in 3D PLA+ hoặc PETG** (độ đặc infill $40\,\%$ dạng tổ ong *gyroid*, thành dày $2,4\text{ mm}$) hoặc tấm nhôm 6061 dày $4\text{ mm}$ khoét rỗng | $\sim 45\text{ g}$ | Nằm ở xa trục quay nhất (cánh tay đòn $r_f = 200\text{ mm}$). Dùng PLA+ giúp giảm khối lượng bàn di động xuống $< 50\text{ g}$, giảm trực tiếp $\tau_{\max}$ và giữ mô-men quán tính tổng mỗi nhánh $J_{\text{eq}} \approx 0,0048\text{ kg}\cdot\text{m}^2 < 0,01\text{ kg}\cdot\text{m}^2$ (nằm trong giới hạn an toàn của mô phỏng). |

> **Kiểm chứng tổng mô-men quán tính quy đổi $J_{\text{eq}}$:**  
> Với $m_{\text{tay\_quay}} = 0,11\text{ kg}$ ($J_{\text{tay\_quay}} = \frac{1}{3} m r_f^2 \approx 0,00147\text{ kg}\cdot\text{m}^2$), $m_{\text{khuỷu}} = 0,035\text{ kg}$, $m_{\text{cặp\_cẳng}} = 0,036\text{ kg}$, $m_{\text{bàn+tải}} = 0,045 + 0,030 = 0,075\text{ kg}$, mô-men quán tính cơ khí quy đổi về trục khớp là:
> $$J_{\text{mech}} = 0,00147 + \left(0,035 + \frac{2}{3}\cdot 0,036 + \frac{1}{3}\cdot 0,075\right) \times 0,200^2 = 0,00147 + 0,084 \times 0,04 = 0,00483\text{ kg}\cdot\text{m}^2$$
> Cộng thêm quán tính rotor động cơ + hộp giảm tốc quy đổi ($\sim 0,002 \div 0,004\text{ kg}\cdot\text{m}^2$), tổng $J_{\text{eq}} \approx 0,007 \div 0,009\text{ kg}\cdot\text{m}^2 \le 0,01\text{ kg}\cdot\text{m}^2$ đúng như tham số `J_kg_m2: 0.01` trong `config.json`.

---

## 3. Thiết kế kiểu khớp và nguyên lý cơ cấu hình bình hành

### 3.1. Ba khớp quay chủ động tại đế cố định ($A_1, A_2, A_3$)
- **Kết cấu:** Mỗi khớp chủ động $A_i$ sử dụng **1 trục thép tôi mài $\varnothing 8\text{ mm}$ (dung sai $g6$)** được đỡ ở **cả hai đầu** bằng **2 ổ bi cầu rãnh sâu 688ZZ ($\varnothing 8 \times \varnothing 16 \times 5\text{ mm}$) hoặc 608ZZ ($\varnothing 8 \times \varnothing 22 \times 7\text{ mm}$)** lắp trong hai tai gối đỡ liền khối trên tấm đế.
- **Lý do không gắn trực tiếp tay quay lên trục động cơ (Cantilever mount):** Trục ra của động cơ bước/servo nhỏ hoặc hộp số hành tinh nếu lắp công-xôn một bên sẽ bị uốn dưới tác dụng của lực dọc thanh truyền $r_e$ khi bàn di động di chuyển lệch tâm ($y_i \ne 0$), gây đảo trục và làm sai lệch cao độ khớp đế $\Delta z_{A,i}$. Việc dùng gối đỡ 2 ổ bi hai đầu (straddle mounting) với khoảng cách hai ổ bi $L_{\text{bearing}} = 36\text{ mm}$ giúp triệt tiêu hoàn toàn độ đảo góc của mặt phẳng quay $O x_i z_i$.

### 3.2. Mười hai khớp cầu trên 6 thanh cẳng tay ($B_{i,1}, B_{i,2}$ và $P_{i,1}, P_{i,2}$)
- **Kết cấu:** Mỗi nhánh $i \in \{1, 2, 3\}$ gồm **2 thanh cẳng tay song song** dài $r_e = 400\text{ mm}$, cách nhau $w_p = 50\text{ mm}$. Hai đầu mỗi thanh gắn **khớp cầu mắt trâu (Rod-end spherical bearing) cỡ M5 (mã SI5T/K, lỗ bi $\varnothing 5\text{ mm}$)** hoặc khớp cầu có lò xo kéo khử độ rơ (anti-backlash spring preload). Tổng cộng toàn robot có $3 \text{ nhánh} \times 2 \text{ thanh/nhánh} \times 2 \text{ đầu/thanh} = 12$ khớp cầu.
- **Giải thích cơ học vì sao bắt buộc dùng khớp cầu để giữ cơ cấu hình bình hành:**
  1. **Tạo chuyển động không gian 3 chiều ($x, y, z$):** Tay quay chủ động $A_i B_i$ chỉ quay trong mặt phẳng thẳng đứng cố định $O x_i z_i$ ($y_i = 0$). Để bàn di động $P$ có thể dịch chuyển ngang ra ngoài mặt phẳng nhánh ($y_i \ne 0$, với $|y_i| \le 150\text{ mm} < r_e = 400\text{ mm}$ theo điều kiện (10) trong `dong-hoc-delta.md`), cặp thanh cẳng tay phải vừa quay quanh trục khuỷu $B_i$ (trong mặt phẳng đứng), vừa nghiêng ngang một góc $\alpha_i = \arcsin(y_i / r_e)$ (tới $\pm 22^\circ$ trong vùng làm việc $\varnothing 300\text{ mm}$). Khớp bản lề 1 bậc tự do không thể thực hiện chuyển động nghiêng ngang này.
  2. **Khóa 3 bậc tự do quay ($\alpha = \beta = \gamma = 0$) của bàn di động:** Ở mỗi nhánh $i$, hai thanh cẳng tay có chiều dài bằng nhau ($r_{e,i1} = r_{e,i2} = 400\text{ mm}$) nối với trục khuỷu $B_i$ và cạnh bàn di động $P_i$ (cùng có bề rộng $w_p = 50\text{ mm}$) tạo thành một **hình bình hành phẳng luôn có 2 cạnh đáy song song với nhau** ($\overrightarrow{B_{i,1} B_{i,2}} \parallel \overrightarrow{P_{i,1} P_{i,2}}$). Vì trục khuỷu $\overrightarrow{B_{i,1} B_{i,2}}$ luôn nằm ngang (song song với mặt phẳng đế $Oxy$), nên cạnh tương ứng trên bàn di động cũng bắt buộc phải nằm ngang.
  3. **Hợp nhất ràng buộc từ 3 nhánh lệch nhau $120^\circ$:** Khi cả 3 nhánh ($0^\circ, 120^\circ, 240^\circ$) đồng thời ép 3 cạnh của tam giác bàn di động $P_1 P_2 P_3$ song song với 3 trục khớp đế $A_1, A_2, A_3$, bàn di động bị **khóa cứng hoàn toàn cả 3 góc quay Roll – Pitch – Yaw** ($\alpha = \beta = \gamma = 0$). Nhờ đó, bàn di động chỉ còn đúng **3 bậc tự do tịnh tiến thuần túy $(x, y, z)$**, giữ cho đầu gắp luôn thẳng đứng vuông góc với mặt bàn phân loại mà không cần thêm cơ cấu truyền động cổ tay.
  4. **Kiểm tra giới hạn góc mở khớp cầu:** Theo `tom-tat-kiem-chung.json`, góc truyền lực nhỏ nhất trên toàn vùng làm việc là $\gamma_{\min} = 39,00^\circ$, tức góc lệch ngang tối đa của khớp cầu là $90^\circ - 39,00^\circ = 51,0^\circ$ ở biên cực trị, và trong vùng làm việc thường xuyên $\le 35^\circ$. Để tránh cấn vỏ khớp cầu mắt trâu tiêu chuẩn (vốn chỉ mở được $\pm 15^\circ \div \pm 20^\circ$ nếu lắp trục vuông góc), **trục bu-lông đi qua lỗ bi cầu tại khuỷu $B_i$ và bàn di động $P_i$ phải bố trí song song với trục khớp chủ động $O y_i$** (hướng tiếp tuyến), kèm đệm vát (cone spacer) hai bên viên bi cầu để góc quay trong mặt phẳng nhánh đạt $360^\circ$ tự do và góc nghiêng ngang chỉ cần $\pm 22^\circ$ (nằm gọn trong giới hạn $\pm 30^\circ$ của rod-end có đệm vát).

---

## 4. Bảng dung sai chế tạo từng chi tiết (Truy nguyên trực tiếp từ Khảo sát Độ nhạy)

Từ kết quả mô phỏng Monte Carlo ($170\,100$ mẫu đánh giá trong `nghien-cuu/mo-hinh/ket-qua/tom-tat-do-nhay.json` và Bảng 6.5c trong `dong-hoc-delta.md`), khi dung sai chế tạo ở mức $\pm 0,5\text{ mm}$, tỷ lệ vùng làm việc đạt yêu cầu $\text{P95} \le 1,0\text{ mm}$ sụt giảm thảm hại xuống chỉ còn **$31,57\,\%$** (và **$0,00\,\%$** nếu tính cả sai lệch khớp đế $\pm 0,5\text{ mm}$, với sai số cực đại vọt lên **$2,410\text{ mm}$**). Ngược lại, khi kiểm soát dung sai trong phạm vi **$\le \pm 0,2\text{ mm}$**, **$100,00\,\%$ vùng làm việc** đạt sai số $\le 1,0\text{ mm}$ ($\text{P95} = 0,514\text{ mm}$, $\text{Max} = 0,795\text{ mm}$), để dành $0,486\text{ mm}$ dự trữ cho sai số bám động lực học của bộ điều khiển PID (trong `metrics.json`, `PID+FF_can_bang` có sai số bám quỹ đạo $\max = 0,075\text{ mm}$, tại điểm gắp $0,344\text{ mm}$, tại điểm thả $0,652\text{ mm}$).

Bảng dưới đây quy định dung sai chế tạo cho từng chi tiết, xếp theo thứ tự độ nhạy từ cao xuống thấp:

| TT | Chi tiết & Kích thước kiểm soát | Giá trị danh nghĩa | Dung sai cho phép | Cấp chính xác / Lắp ghép ISO | Lý do kỹ thuật (Dẫn chiếu định lượng từ `tom-tat-do-nhay.json`) |
| :-: | --- | :---: | :---: | :---: | --- |
| **1** | **Vị trí tâm 3 ổ trục khớp đế $A_1, A_2, A_3$** (Bán kính hướng kính $R_b$ và độ đồng phẳng cao độ $z_A$) | $R_b = 199,76\text{ mm}$<br>$z_A = 0,00\text{ mm}$ | **$\pm 0,05\text{ mm}$** | Gia công CNC 1 lần gá; lỗ ổ bi $\varnothing 16\text{H7}$ | **Nhạy số 1 (Hệ số khuếch đại xấu nhất $= 3,40\text{ mm/mm}$, trung bình $= 2,57\text{ mm/mm}$):** Ở mức nhiễu $\pm 0,2\text{ mm}$, riêng sai lệch vị trí khớp đế ($\Delta R_b, \Delta z_A$) đã gây ra $\text{P95} = 0,312\text{ mm}$ và $\text{Max} = 0,515\text{ mm}$. Do đó phải siết dung sai vị trí tâm ổ trục trên đế cố định xuống $\pm 0,05\text{ mm}$ để giới hạn sai số thành phần này $< 0,17\text{ mm}$. |
| **2** | **Chiều dài tâm–tâm thanh cẳng tay bị động ($r_e$)** và **độ đồng đều giữa 6 thanh** | $r_e = 400,00\text{ mm}$ | **$\pm 0,10\text{ mm}$** (tuyệt đối)<br>**$\le 0,05\text{ mm}$** (chênh lệch trong cùng 1 cặp) | Dưỡng gá (Jig) 2 chốt $\varnothing 5\text{g6}$ | **Nhạy số 2 — Nhạy nhất trong các khâu động (Hệ số khuếch đại xấu nhất $= 2,52\text{ mm/mm}$, nhạy hơn gấp đôi $r_f$):** Ở mức $\pm 0,2\text{ mm}$, riêng $r_e$ gây $\text{P95} = 0,291\text{ mm}$ và $\text{Max} = 0,434\text{ mm}$ vì $\Delta r_e$ thay đổi trực tiếp bán kính mặt cầu giao nhau. Đặc biệt, nếu 2 thanh trong cùng 1 cặp lệch nhau $> 0,1\text{ mm}$, hình bình hành bị méo làm bàn di động nghiêng góc $\Delta \alpha \approx 0,1/50\text{ rad} = 0,11^\circ$. |
| **3** | **Chiều dài tay quay chủ động ($r_f$)** (Khoảng cách tâm trục $A_i$ đến tâm trục khuỷu $B_i$) | $r_f = 200,00\text{ mm}$ | **$\pm 0,10\text{ mm}$** | Khoảng cách tâm CNC; lỗ trục $\varnothing 8\text{H7}$ | **Nhạy số 3 (Hệ số khuếch đại xấu nhất $= 1,16\text{ mm/mm}$, trung bình $= 0,62\text{ mm/mm}$):** Nhạy bằng một nửa so với $r_e$ (ở $\pm 0,2\text{ mm}$ gây $\text{P95} = 0,145\text{ mm}$, $\text{Max} = 0,212\text{ mm}$). Phay/cắt CNC với dung sai $\pm 0,10\text{ mm}$ là hoàn toàn khả thi và giữ sai số thành phần $< 0,12\text{ mm}$. |
| **4** | **Khoảng cách cạnh tam giác đế cố định ($f$) & Góc chia $120^\circ$ giữa 3 nhánh** | $f = 346,00\text{ mm}$<br>$\phi_i = 0^\circ, 120^\circ, 240^\circ$ | **$\pm 0,10\text{ mm}$**<br>**$\pm 0,03^\circ$** | Cắt/phay CNC tọa độ phẳng $Oxy$ | **Nhạy số 4 (Hệ số khuếch đại xấu nhất $= 0,97\text{ mm/mm}$, trung bình $= 0,81\text{ mm/mm}$):** Nhờ phép chia hình học $R_b = f/\sqrt{3}$, sai số $\Delta f$ được giảm đi $\sqrt{3} \approx 1,732$ lần (ở $\pm 0,2\text{ mm}$ gây $\text{P95} = 0,131\text{ mm}$, $\text{Max} = 0,181\text{ mm}$). Vì tấm đế đã gia công CNC để đạt dung sai $\pm 0,05\text{ mm}$ cho $R_b$, kích thước $f$ tự động đạt $\le \pm 0,10\text{ mm}$. |
| **5** | **Kích thước tam giác bàn di động ($e$)** (Bán kính ngoại tiếp $r_p = 66,40\text{ mm}$) | $e = 115,00\text{ mm}$ | **$\pm 0,15\text{ mm}$** | In 3D PLA+ hiệu chuẩn bước E-steps + doa lỗ chốt $\varnothing 5\text{H7}$ | **Nhạy số 5 — Ít nhạy nhất (Hệ số khuếch đại xấu nhất $= 0,97\text{ mm/mm}$, $\text{P95} = 0,128\text{ mm}$, $\text{Max} = 0,180\text{ mm}$ ở $\pm 0,2\text{ mm}$):** Sai số $\Delta e$ cũng được chia giảm $\sqrt{3}$ lần trong hiệu bán kính $R = (f - e)/\sqrt{3}$. Do đó cho phép nới dung sai lên $\pm 0,15\text{ mm}$, phù hợp với khả năng của máy in 3D FDM phổ thông sau khi bù co ngót. |
| **6** | **Khoảng cách ngang giữa 2 khớp cầu trong 1 cặp bình hành ($w_p$)** tại khuỷu $B_i$ và bàn $P_i$ | $w_p = 50,00\text{ mm}$ | **$\pm 0,05\text{ mm}$** (đồng bộ giữa $B_i$ và $P_i$) | Cắt ống đệm (spacer) trên máy tiện hoặc dùng thước cặp điện tử | Đảm bảo 2 cạnh đáy của hình bình hành bằng nhau tuyệt đối ($w_{p,\text{khuỷu}} = w_{p,\text{bàn}}$). Nếu lệch $\Delta w_p$, hai thanh $r_e$ không còn song song, gây kẹt khớp cầu khi góc nghiêng ngang $\alpha_i$ lớn ở biên vùng làm việc ($r = 150\text{ mm}$). |
| **7** | **Khe hở dọc trục của khớp cầu (Rod-end radial/axial clearance) & ổ bi trục chính** | $0,00\text{ mm}$ | **$\le 0,03\text{ mm}$** | Ổ bi 688ZZ/608ZZ cấp ABEC-3 trở lên; Rod-end có lò xo kéo khử rơ | Theo Mục 2 và 6.6 `dong-hoc-delta.md`, độ rơ khớp cầu cộng trực tiếp vào $\Delta r_e$ (khuếch đại $2,52\text{ lần}$). Gắn 1 lò xo kéo nhẹ song song giữa 2 thanh cẳng tay của mỗi nhánh giúp luôn ép bi cầu về một phía thành ổ, triệt tiêu khe hở đảo chiều (backlash). |
| **8** | **Độ rơ góc (Backlash) của bộ truyền động tại trục khớp $A_i$** | $0,00\text{ arcmin}$ | **$\le 5\text{ arcmin}$** ($\le 1,45 \times 10^{-3}\text{ rad}$)<br>*(Hoặc $\approx 0$ với đai GT2 căng đai)* | Hộp số chính xác cao $\le 5\text{ arcmin}$ hoặc **Đai răng GT2 bản $10\text{ mm}$ có cơ cấu căng đai** | Cánh tay đòn $r_f = 200\text{ mm}$ phóng đại mọi độ rơ góc $\delta \theta_b$ tại trục khớp thành sai số điểm cuối $e_{\text{backlash}} \approx r_f \delta \theta_b$. Nếu dùng hộp số phổ thông $15\text{ arcmin}$ ($4,36 \times 10^{-3}\text{ rad}$), riêng backlash đã chiếm **$0,873\text{ mm}$**, làm vỡ ngân sách sai số $\le 1,0\text{ mm}$ (xem chi tiết Mục 5). |

---

## 5. Ngân sách Sai số Tổng hợp (Total Error Budget) và Đánh giá Độ rơ Hộp số (Backlash)

Trong Mục 4, mô phỏng Monte Carlo (`tom-tat-do-nhay.json`) mới chỉ xét **sai số hình học tĩnh của các khâu cơ khí** ($f, e, r_f, r_e, R_b, z_A$). Trên robot thực tế, sai số vị trí điểm tác động cuối là tổng hợp của **4 nguồn sai số vật lý**:

### 5.1. Định lượng từng thành phần sai số quy đổi về điểm cuối ($r_f = 200\text{ mm}$)

1. **Sai số chế tạo & lắp ráp cơ khí ($e_{\text{mech}}$):**
   - Từ `tom-tat-do-nhay.json` ở mức dung sai $\pm 0,2\text{ mm}$ (4 khâu $f, e, r_f, r_e$): phân vị 95 % đạt **$\text{P95} = 0,402\text{ mm}$**, cực đại trường hợp xấu nhất **$\text{Max} = 0,689\text{ mm}$** (nếu cộng cả lệch khớp đế $\pm 0,2\text{ mm}$ thì $\text{P95} = 0,514\text{ mm}, \text{Max} = 0,795\text{ mm}$; khi gia công đế CNC liền khối $\pm 0,05\text{ mm}$ và cẳng tay trên đồ gá $\pm 0,10\text{ mm}$ theo Bảng Mục 4, sai số cơ khí cực đại giới hạn ở $\text{Max}_{\text{tk}} \approx 0,520\text{ mm}$, $\text{P95}_{\text{tk}} \approx 0,340\text{ mm}$).
2. **Độ rơ góc của bộ truyền động (Gearbox / Transmission Backlash — $e_{\text{backlash}}$):**
   - Góc rơ $\delta \theta_b$ tại trục khớp chủ động $A_i$ làm đầu mút khuỷu tay $B_i$ dịch chuyển một cung tròn:
     $$e_{\text{backlash}} \approx r_f \cdot \delta \theta_b, \qquad \text{với } r_f = 200\text{ mm}, \quad 1\text{ arcmin} = \frac{1}{60} \times \frac{\pi}{180} = 2,9089 \times 10^{-4}\text{ rad}$$
   - *(Ghi chú từ ma trận Jacobian Mục 4.2 `dong-hoc-delta.md`: $\delta \mathbf{p} = J \delta \boldsymbol{\theta} = \hat{J} (r_f \delta \boldsymbol{\theta})$; tại tâm vùng làm việc $\|J\|_2 \approx 1,116 r_f$, nên công thức $r_f \delta \theta_b$ là mức cơ sở trực tiếp tại đầu khuỷu tay)*. Quy đổi cụ thể cho các mức truyền động:
     - **Mức $15\text{ arcmin}$ (Hộp số hành tinh phổ thông 1 cấp):** $\delta \theta_b = 4,363 \times 10^{-3}\text{ rad} \implies e_{\text{backlash}} = 200 \times 4,363 \times 10^{-3} = \mathbf{0,873\text{ mm}}$.
     - **Mức $10\text{ arcmin}$ (Hộp số hành tinh cấp trung bình):** $\delta \theta_b = 2,909 \times 10^{-3}\text{ rad} \implies e_{\text{backlash}} = 200 \times 2,909 \times 10^{-3} = \mathbf{0,582\text{ mm}}$.
     - **Mức $5\text{ arcmin}$ (Hộp số hành tinh chính xác cao):** $\delta \theta_b = 1,454 \times 10^{-3}\text{ rad} \implies e_{\text{backlash}} = 200 \times 1,454 \times 10^{-3} = \mathbf{0,291\text{ mm}}$.
     - **Truyền đai răng GT2 tỷ số $5:1$ (Puly $16\text{T} \to 80\text{T}$, bản rộng $10\text{ mm}$, có con lăn căng đai):** Khe hở chết hình học $\approx 0\text{ arcmin}$. Dưới mô-men tĩnh tại điểm dừng gắp–thả ($\ddot{\theta} = 0$, chỉ còn tải trọng lực tĩnh $\tau_g \approx 0,12\text{ N}\cdot\text{m}$ trên bán kính puly bị động $R_{80\text{T}} = 25,46\text{ mm}$, lực vòng $F = 4,7\text{ N}$), độ giãn đàn hồi vi sai của dây đai GT2 lõi sợi thủy tinh (`[CẦN KIỂM CHỨNG]`) gây lệch góc tương đương $\delta \theta_{\text{belt, tĩnh}} \approx 0,5 \times 10^{-3}\text{ rad} \approx 1,7\text{ arcmin} \implies \mathbf{e_{\text{belt, tĩnh}} \approx 0,100\text{ mm}}$ (và ở đỉnh gia tốc $\tau_{\max} = 0,457\text{ N}\cdot\text{m}$, độ giãn động tức thời $\approx 0,20\text{ mm}$ nhưng tự phục hồi về $0,10\text{ mm}$ khi dừng hẳn tại điểm gắp/thả).
     - **Truyền trực tiếp (Direct-drive, tỷ số $1:1$ qua khớp nối đĩa đàn hồi zero-backlash):** $e_{\text{backlash}} \approx \mathbf{0,020\text{ mm}}$ (nhưng độ phân giải encoder giảm 5 lần và đòi hỏi động cơ nặng/đắt hơn).
3. **Độ phân giải lượng tử hóa của Encoder ($e_{\text{enc}}$):**
   - Với Encoder $1\,000\text{ PPR}$ giải mã Quadrature $4\times$ ($4\,000\text{ xung/vòng}$) đặt ở trục động cơ trước bộ truyền tỷ số $i = 5:1$:
     $$N_{\text{khớp}} = 4\,000 \times 5 = 20\,000\text{ xung/vòng} \implies \delta \theta_{\text{enc}} = \frac{2\pi}{20\,000} = 3,1416 \times 10^{-4}\text{ rad}\ (0,018^\circ)$$
   - Sai số lượng tử hóa toàn bước ($1\text{ count}$) quy đổi ra điểm cuối:
     $$e_{\text{enc}} = r_f \cdot \delta \theta_{\text{enc}} = 200 \times 3,1416 \times 10^{-4} = \mathbf{0,063\text{ mm}} \quad (\text{hoặc } \pm 0,031\text{ mm với } \pm 0,5\text{ count})$$
   - *(Lưu ý: Nếu dùng phương án Truyền trực tiếp $1:1$ với encoder $4\,000\text{ cpr}$, bước lượng tử vọt lên $e_{\text{enc, 1:1}} = 0,314\text{ mm}$).*
4. **Sai số hiệu chuẩn gốc khớp Home ($e_{\text{home}}$):**
   - Hệ số nhạy góc gốc tại tay quay: $\frac{\partial s}{\partial \theta_0} = r_f \frac{\pi}{180^\circ} = 200 \times 0,017453 = \mathbf{3,491\text{ mm/deg}}$.
   - **Khi căn gốc cơ khí thủ công bằng ke vuông / thước đo cao ($\delta \theta_{\text{home}} = \pm 0,10^\circ$):**
     $$e_{\text{home, cơ}} = 3,491 \times 0,10 = \mathbf{0,349\text{ mm}}$$
   - **Khi áp dụng thêm bước hiệu chuẩn phần mềm chạm 9 điểm chuẩn (Mục 4B `README.md`, đưa sai lệch gốc dư về $\delta \theta_{\text{home}} \le \pm 0,03^\circ$):**
     $$e_{\text{home, cal}} = 3,491 \times 0,03 = \mathbf{0,105\text{ mm}}$$

---

### 5.2. Phương pháp cộng dồn sai số và Bảng Ngân sách Sai số Tổng hợp

Chúng ta đánh giá đồng thời theo **2 quy tắc cộng sai số chuẩn trong thiết kế máy chính xác**:
- **Cộng tuyến tính trường hợp xấu nhất (Worst-Case Linear Sum):**
  $$e_{\text{total, Linear}} = e_{\text{mech, Max}} + e_{\text{backlash}} + e_{\text{enc}} + e_{\text{home}}$$
  *Ý nghĩa:* Giả định cực đoan rằng tại cùng một điểm không gian, cả 18 kích thước cơ khí đều lệch ở biên xấu nhất ($0,689\text{ mm}$), đồng thời hộp số rơ hết biên độ theo đúng hướng đó, encoder lệch tròn 1 xung và gốc khớp lệch $0,1^\circ$ cùng chiều. Đây là cận trên tuyệt đối (xác suất xảy ra đồng thời $< 10^{-5}$).
- **Cộng căn tổng bình phương (RSS — Root Sum Square) & Cộng Hỗn hợp Bán bảo thủ (Hybrid RSS + Deterministic Backlash):**
  - **RSS thuần (mức tin cậy 95 %):** Vì sai số chế tạo các khâu ($e_{\text{mech, P95}} = 0,402\text{ mm}$), sai số đặt gốc, bước lượng tử encoder và hướng tải trên 3 nhánh là các biến ngẫu nhiên độc lập, tổng sai số phân vị 95 % được tính bằng:
    $$e_{\text{total, RSS}} = \sqrt{e_{\text{mech, P95}}^2 + e_{\text{backlash}}^2 + e_{\text{enc}}^2 + e_{\text{home}}^2}$$
  - **Hỗn hợp Bán bảo thủ (Hybrid = Backlash tuyến tính + RSS ngẫu nhiên):** Vì độ rơ hộp số ($e_{\text{backlash}}$) là sai số hệ thống phi tuyến luôn xuất hiện mỗi khi đảo chiều chuyển động, cách tính an toàn và thực tế nhất trong cơ điện tử là **cộng thẳng $e_{\text{backlash}}$ với căn bậc hai tổng bình phương (RSS) của các thành phần ngẫu nhiên**:
    $$e_{\text{total, Hybrid}} = e_{\text{backlash}} + \sqrt{e_{\text{mech, P95}}^2 + e_{\text{enc}}^2 + e_{\text{home}}^2}$$

#### Bảng tổng hợp Ngân sách Sai số (Đơn vị: mm) — Chỉ tiêu mục tiêu: $\le 1,000\text{ mm}$

| Kịch bản truyền động & Mức Backlash | (1) Dung sai chế tạo $\pm 0,2\text{ mm}$<br>$\text{P95} / \text{Max}$ | (2) Backlash / Đàn hồi truyền động<br>$e_{\text{backlash}}$ | (3) Độ phân giải Encoder<br>$e_{\text{enc}}$ | (4) Lệch gốc khớp $0,1^\circ$ (sau Calib $0,03^\circ$)<br>$e_{\text{home}}$ | **Tổng RSS (P95)**<br>*(Kèm giá trị sau Calib gốc)* | **Tổng Hybrid (Backlash + RSS)**<br>*(Kèm giá trị sau Calib)* | **Tổng Tuyến tính (Max xấu nhất)**<br>*(Kèm giá trị sau Calib)* | Kết luận đối chiếu ngưỡng $\le 1,00\text{ mm}$ |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **1. Hộp số hành tinh phổ thông ($15\text{ arcmin}$)** | $0,402$ / $0,689$ | **$0,873$** | $0,063$ | $0,349$<br>*(0,105)* | **$1,024\text{ mm}$**<br>*(0,969 mm)* | **$1,409\text{ mm}$**<br>*(1,293 mm)* | **$1,974\text{ mm}$**<br>*(1,730 mm)* | ❌ **LOẠI BỎ:** Vượt ngưỡng $1,0\text{ mm}$ ở cả 3 cách tính (riêng backlash đã chiếm $87,3\,\%$ ngân sách). |
| **2. Hộp số hành tinh trung bình ($10\text{ arcmin}$)** | $0,402$ / $0,689$ | **$0,582$** | $0,063$ | $0,349$<br>*(0,105)* | **$0,791\text{ mm}$**<br>*(0,718 mm)* | **$1,118\text{ mm}$**<br>*(1,002 mm)* | **$1,683\text{ mm}$**<br>*(1,439 mm)* | ❌ **KHÔNG ĐẠT:** Vượt ngưỡng theo cả Cộng tuyến tính ($1,683\text{ mm}$) và Hybrid ($1,118\text{ mm}$). |
| **3. Hộp số hành tinh chính xác cao ($\le 5\text{ arcmin}$)** | $0,402$ / $0,689$ | **$0,291$** | $0,063$ | $0,349$<br>*(0,105)* | **$0,610\text{ mm}$**<br>*(0,511 mm)* | **$0,827\text{ mm}$**<br>*(0,711 mm)* | **$1,392\text{ mm}$**<br>*(1,148 mm; nếu siết đế CNC: **0,979 mm**)* | ⚠️ **ĐẠT KỸ THUẬT** (RSS $= 0,610\text{ mm}$, Hybrid $= 0,827\text{ mm} \le 1,0\text{ mm}$), nhưng **chi phí hộp số rất đắt**. |
| **4. Truyền đai răng GT2 $5:1$ bản $10\text{ mm}$ có căng đai (PHƯƠNG ÁN CHỌN)** | $0,402$ / $0,689$ | **$0,100$**<br>*(đàn hồi tĩnh; backlash $\approx 0$)* | $0,063$ | $0,349$<br>*(0,105)* | **$0,545\text{ mm}$**<br>*(0,432 mm)* | **$0,636\text{ mm}$**<br>*(0,520 mm)* | **$1,201\text{ mm}$**<br>*(Sau Calib gốc $0,03^\circ$: **0,957 mm**)* | ✅ **ĐẠT TỐI ƯU:** Đạt $\le 1,0\text{ mm}$ ở cả RSS ($0,545\text{ mm}$), Hybrid ($0,636\text{ mm}$) và Tuyến tính sau Calib ($0,957\text{ mm}$), chi phí thấp. |
| **5. Truyền trực tiếp Direct-Drive $1:1$ (Stepper vòng kín NEMA 23)** | $0,402$ / $0,689$ | **$0,020$**<br>*(khớp nối đĩa)* | **$0,314$**<br>*(không qua $5:1$)* | $0,349$<br>*(0,105)* | **$0,618\text{ mm}$**<br>*(0,521 mm)* | **$0,641\text{ mm}$**<br>*(0,541 mm)* | **$1,372\text{ mm}$**<br>*(Sau Calib gốc: **1,128 mm**)* | ⚠️ Hết backlash nhưng mất lợi thế nhân độ phân giải encoder ($e_{\text{enc}}$ tăng 5 lần lên $0,314\text{ mm}$) và động cơ nặng/nóng. |

### 5.3. Kết luận rút ra từ Ngân sách Sai số để điều chỉnh Thiết kế Truyền động
1. **Phát hiện quan trọng:** Hộp giảm tốc hành tinh phổ thông ($10 \div 15\text{ arcmin}$) hoàn toàn **không sử dụng được** cho robot Delta có $r_f = 200\text{ mm}$ khi mục tiêu sai số là $\le 1,0\text{ mm}$, vì riêng khe hở bánh răng đã gây lệch $0,582 \div 0,873\text{ mm}$.
2. **Chốt phương án truyền động chuẩn:** Chuyển từ hộp số hành tinh phổ thông sang **Bộ truyền Đai răng GT2 bản rộng $10\text{ mm}$ tỷ số truyền $i = 5:1$ (Puly chủ động $16\text{ răng}$ kéo Puly bị động $80\text{ răng}$ gắn liền trục khớp $\varnothing 8\text{g6}$, có rãnh trượt + con lăn căng đai khử rơ)** kết hợp **Động cơ bước vòng kín (Closed-loop Stepper) có Encoder $1\,000\text{ PPR}$**.
   - Phương án này giúp triệt tiêu khe hở chết (dead-zone backlash $\approx 0$), giữ nguyên hệ số nhân mô-men $5\times$ ($\tau_{\text{ra}} \approx 2,48\text{ N}\cdot\text{m}$, $k_{\text{sf}} = 5,42$) và hệ số chia nhỏ bước encoder $5\times$ ($e_{\text{enc}} = 0,063\text{ mm}$), đưa tổng sai số toàn hệ thống về **$0,545\text{ mm}$ (RSS)**, **$0,636\text{ mm}$ (Hybrid)** và **$0,957\text{ mm}$ (Cộng tuyến tính xấu nhất sau khi hiệu chuẩn gốc khớp $\le 0,03^\circ$)** — đảm bảo đạt chỉ tiêu $\le 1,0\text{ mm}$.

---

## 6. Phương án gia công và đồ gá chế tạo (Manufacturing & Jig Plan)

Để đạt được bảng dung sai ở Mục 4 trong điều kiện xưởng cơ khí sinh viên / dịch vụ gia công bên ngoài tại Việt Nam với chi phí thấp nhất, quy trình công nghệ được chốt như sau:

1. **Tấm đế cố định ($f = 346\text{ mm}$) — Gia công CNC liền khối, tuyệt đối không khoan/bắt vít tay rời rạc:**
   - **Lý do:** Nếu dùng 3 gối đỡ rời bắt lên khung nhôm định hình bằng thước dây/thước cặp, sai số lắp đặt vị trí khớp đế ($\Delta R_b, \Delta z_A$) thường lên tới $\pm 0,5 \div 1,0\text{ mm}$. Với hệ số khuếch đại $3,40\text{ mm/mm}$, riêng lỗi này sẽ gây sai số điểm cuối $1,7 \div 3,4\text{ mm}$ (phá vỡ hoàn toàn mục tiêu $\le 1,0\text{ mm}$).
   - **Giải pháp:** Đặt phay CNC (hoặc cắt Laser Fiber trên tấm thép/nhôm phẳng) **một tấm đế nguyên tấm duy nhất** hình lục giác vát góc (ngoại tiếp đường tròn $\varnothing 500\text{ mm}$). Toàn bộ các lỗ định vị (chốt định vị $\varnothing 6\text{H7}$) cho 3 cụm gối đỡ ổ trục $A_1, A_2, A_3$ được gia công trong **cùng một lần gá đặt phôi** trên máy CNC, đảm bảo dung sai khoảng cách tâm $\le \pm 0,03\text{ mm}$ và góc lệch $120^\circ \pm 0,01^\circ$.
2. **Đồ gá (Jig) lắp ráp và khóa chiều dài 6 thanh cẳng tay ($r_e = 400,00 \pm 0,10\text{ mm}$):**
   - **Cấu tạo đồ gá:** Dùng một thanh nhôm định hình phẳng hoặc tấm thép cắt CNC có đóng sẵn **2 chốt trụ thép tôi $\varnothing 5,00\text{ mm}$ ($g6$) cách nhau đúng $400,00\text{ mm}$** (kiểm tra bằng thước cặp điện tử có độ phân giải $0,01\text{ mm}$).
   - **Quy trình lắp:** Cắt 6 đoạn ống carbon $\varnothing 8 \times \varnothing 6\text{ mm}$ dài $350\text{ mm}$ (dung sai cắt thô $\pm 0,5\text{ mm}$ không ảnh hưởng). Dán keo Epoxy 2 thành phần (hoặc vặn đầu ren trái – phải M5) nối với 2 mắt trâu SI5T/K, sau đó **cắm ngay 2 đầu mắt trâu vào 2 chốt trên đồ gá**, siết đai ốc hãm M5 và chờ keo đóng rắn hoàn toàn trên đồ gá. Cách này đảm bảo cả 6 thanh có khoảng cách tâm $r_e$ giống hệt nhau với độ lệch tương đối $\le 0,03\text{ mm}$ mà không phụ thuộc vào sai số cắt ống carbon.
3. **Ba tay quay chủ động ($r_f = 200,00 \pm 0,10\text{ mm}$):**
   - Gia công phay CNC từ nhôm tấm 6061-T6 dày $6\text{ mm}$ (hoặc cắt Laser kim loại tấm + doa lại 2 lỗ đầu mút bằng mũi doa $\varnothing 8\text{H7}$ và $\varnothing 5\text{H7}$ trên máy khoan bàn). Khi lắp ghép, có thể kẹp chồng cả 3 tay quay lại với nhau và doa thông 2 lỗ cùng lúc để đảm bảo $r_{f,1} = r_{f,2} = r_{f,3}$ đồng đều tuyệt đối.
4. **Bàn di động ($e = 115,00 \pm 0,15\text{ mm}$):**
   - In 3D bằng nhựa PLA+ trên máy in FDM đã hiệu chuẩn (in thử khối chuẩn $100 \times 100\text{ mm}$ để bù hệ số co ngót `XY scaling factor` trong phần mềm cắt lớp). Các lỗ xuyên chốt khớp cầu $\varnothing 5\text{ mm}$ được thiết kế nhỏ hơn danh nghĩa ($4,8\text{ mm}$) rồi dùng mũi khoan/doa $\varnothing 5,0\text{ mm}$ doa nguội sau khi in, kết hợp luồn thanh ren/chốt thép thông suốt chiều rộng $w_p = 50,00\text{ mm}$.
