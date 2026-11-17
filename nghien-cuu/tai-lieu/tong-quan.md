# Tổng quan tài liệu nghiên cứu: Mô phỏng robot Delta phân loại sản phẩm bằng camera

**Ngày tổng hợp:** 2026-11-18  
**Đối chiếu với đề cương:** `nghien-cuu/de-tai.md` (Mục tiêu: sai số vị trí $\le 1\text{ mm}$ trên vùng làm việc $\varnothing 300 \times 150\text{ mm}$; chu kỳ gắp–thả (pick-and-place) $\le 1,5\text{ s}$, độ vọt lố (overshoot) $\le 5\,\%$; độ chính xác phân loại camera $\ge 90\,\%$ trên $\ge 100$ mẫu).

---

## 1. Phạm vi tổng quan

Tổng quan này tổng hợp **8 công trình khoa học** trong `references.bib`, trải dài trong giai đoạn **1988–2024** (36 năm), bao gồm:
- **Giai đoạn nền tảng (1988–1998):** 2 công trình gốc về cấu trúc cơ khí song song (parallel mechanism) và hiệu chuẩn động học (kinematic calibration) của robot Delta (`Clavel1988Delta`, `Vischer1998Kinematic`).
- **Giai đoạn điều khiển nâng cao (2015–2020):** 2 bài báo tạp chí quốc tế về điều khiển kháng nhiễu chủ động (Active Disturbance Rejection Control — ADRC) cho bài toán bám quỹ đạo (trajectory tracking) tốc độ cao (`Castaneda2015Robust`, `Liu2020LADRC`).
- **Giai đoạn tích hợp thị giác và giải pháp chi phí thấp (2023–2024):** 4 công trình gần đây về giải số động học thuận (`Yang2024FKNumerical`) và hệ thống robot Delta chi phí thấp tích hợp thị giác máy tính (computer vision) để gắp–phân loại vật trên băng tải (`PhuongHoai2023LowCostDelta`, `Vo2023DeltaPhanLoai`, `Elassal2024LowCost`), trong đó có 2 công trình của nhóm tác giả tại Việt Nam (`PhuongHoai2023LowCostDelta`, `Vo2023DeltaPhanLoai`).

**Nguồn xuất bản và mức độ kiểm chứng:**
- **7/8 tài liệu** đã được xác thực mã định danh số (DOI) qua cơ sở dữ liệu Crossref, đăng trên các tạp chí và hội nghị uy tín (*IEEE Transactions on Control Systems Technology*, *Robotica*, *Mathematical Problems in Engineering*, *e-Prime*, *FME Transactions*, *International Journal of Electrical and Computer Engineering — IJECE*, và kỷ yếu hội nghị IEEE *ICAIDT*).
- **1/8 tài liệu** (`Clavel1988Delta`) là bài hội nghị lịch sử (*Proc. 18th Int. Symp. Industrial Robots*, 1988), chưa tìm thấy DOI trên Crossref và đang ở trạng thái `[CẦN KIỂM CHỨNG]` từ kỷ yếu gốc.
- **Giới hạn dữ liệu đầu vào:** Toàn bộ 8 ghi chú hiện tại được trích xuất từ metadata và tóm tắt (abstract) qua OpenAlex/Crossref; riêng `Vischer1998Kinematic` và `Clavel1988Delta` chưa có cả nội dung abstract. Do đó, mọi phân tích dưới đây tách biệt nghiêm ngặt giữa **dữ kiện từ notes** và **(nhận định của người tổng hợp)**.

---

## 2. Bản đồ phương pháp

Thay vì liệt kê theo thứ tự thời gian, 8 công trình được phân thành **3 nhóm phương pháp** tương ứng với 3 bài toán cốt lõi của đề tài (Động học — Điều khiển quỹ đạo — Tích hợp thị giác máy tính):

### Nhóm 1: Mô hình hình học, hiệu chuẩn và giải số động học (Kinematics & Calibration)
- **Đại diện:** `Clavel1988Delta` (1988), `Vischer1998Kinematic` (1998), `Yang2024FKNumerical` (2024).
- **Ý tưởng cốt lõi:**
  - Thiết lập cấu trúc 3 chuỗi động học song song đối xứng với các khớp quay chủ động (actuated revolute joints) gắn trên đế cố định và cơ cấu hình bình hành (parallelogram linkage) giữ cho bàn di động (moving platform) chỉ có 3 bậc tự do (degrees of freedom — DOF) tịnh tiến $x$–$y$–$z$ (`Clavel1988Delta`).
  - Xử lý sai số hình học do chế tạo/lắp ráp (chiều dài khâu, vị trí khớp đế) thông qua mô hình hiệu chuẩn động học để giảm sai số vị trí điểm cuối (`Vischer1998Kinematic`).
  - Giải bài toán động học thuận (forward kinematics — FK) bằng phương pháp số (numerical method) kết hợp ràng buộc nghiệm trong MATLAB để tìm nghiệm duy nhất, đồng thời dùng mô phỏng Monte Carlo để xác định không gian làm việc (workspace) (`Yang2024FKNumerical`).
- **Ưu điểm:** Đặt nền móng toán học cho việc xác định vùng làm việc và ánh xạ giữa không gian khớp $(\theta_1, \theta_2, \theta_3)$ với không gian thao tác $(x, y, z)$. Phương pháp số + Monte Carlo trong `Yang2024FKNumerical` dễ lập trình trên MATLAB/Python và trực quan hoá được biên vùng làm việc.
- **Hạn chế:** Bài toán FK của robot song song là hệ phương trình phi tuyến đa nghiệm, khó rút gọn tường minh (`Yang2024FKNumerical`). Trong các tóm tắt của `Vischer1998Kinematic` và `Yang2024FKNumerical`, chưa có con số định lượng về sai số vị trí (tính bằng $\text{mm}$) hay thời gian hội tụ của thuật toán số.

### Nhóm 2: Điều khiển bám quỹ đạo kháng nhiễu dựa trên động lực học (Dynamic Trajectory Tracking Control)
- **Đại diện:** `Castaneda2015Robust` (2015), `Liu2020LADRC` (2020).
- **Ý tưởng cốt lõi:**
  - Xem các bất định của mô hình động lực học (uncertain dynamics), lực ma sát và tác động qua lại giữa các nhánh song song (coupling) là "nhiễu tổng hợp" (total disturbance) và dùng bộ quan sát trạng thái mở rộng (Extended State Observer — ESO) để ước lượng rồi bù trừ theo thời gian thực.
  - `Castaneda2015Robust` đề xuất bộ điều khiển ADRC thích nghi chỉ dựa trên đầu ra (output-based adaptive ADRC), không cần cảm biến đo vận tốc khớp, kết hợp thuật toán bình phương tối thiểu trung bình (Least Mean Squares — LMS) để xấp xỉ phi tham số thành phần bất định; đối chứng trực tiếp với bộ điều khiển tỉ lệ – tích phân – vi phân có bù tiến (PID with feed-forward) và ADRC thường trên cả mô phỏng (quỹ đạo nhanh gấp 5 lần) và thực nghiệm.
  - `Liu2020LADRC` xây dựng mô hình động lực học và dùng ADRC tuyến tính (Linear ADRC — LADRC) để giải ghép (decoupling) giữa 3 khớp chủ động khi bám quỹ đạo đường cong số 8 xoắn ốc trong không gian 3D.
- **Ưu điểm:** Đạt độ bền vững (robustness) cao trước nhiễu nội/ngoại và sự thay đổi tải trọng ở tốc độ cao mà không đòi hỏi mô hình động lực học chính xác tuyệt đối (`Castaneda2015Robust`, `Liu2020LADRC`).
- **Hạn chế:** Cấu trúc toán học phức tạp (phải dẫn giải động lực học hệ song song, thiết kế bộ quan sát ESO và chứng minh ổn định hệ kín), vượt quá yêu cầu cơ bản của sinh viên năm 2 nếu triển khai từ đầu (nhận định của người tổng hợp). Cả hai bài đều không nêu con số sai số bám hay độ vọt lố cụ thể trong phần abstract (`Castaneda2015Robust`, `Liu2020LADRC`).

### Nhóm 3: Hệ thống tích hợp thị giác máy tính cổ điển và robot Delta chi phí thấp (Vision-Guided Low-Cost Pick-and-Place)
- **Đại diện:** `PhuongHoai2023LowCostDelta` (2023), `Vo2023DeltaPhanLoai` (2023), `Elassal2024LowCost` (2024).
- **Ý tưởng cốt lõi:**
  - Sử dụng kiến trúc xử lý phân tán chi phí thấp: máy tính nhúng (Raspberry Pi 4 trong `Vo2023DeltaPhanLoai`, Raspberry Pi trong `Elassal2024LowCost`) hoặc máy tính xử lý ảnh kết hợp với vi điều khiển (Arduino Uno/Arduino trong `PhuongHoai2023LowCostDelta`, `Vo2023DeltaPhanLoai`, `Elassal2024LowCost`) để tính động học nghịch (inverse kinematics — IK) và phát xung điều khiển động cơ.
  - Xử lý ảnh cổ điển không dùng học sâu (deep learning): chuyển đổi không gian màu BGR sang HSV và phân ngưỡng (thresholding) để phân loại 3 màu đỏ, vàng, xanh lá (`Vo2023DeltaPhanLoai`); lọc theo dải màu kết hợp đường bao (contour / bounding box) để trích xuất tọa độ thực của vật (`Elassal2024LowCost`); hoặc xác định đồng thời tọa độ 3D và kích thước vật để điều chỉnh độ mở tay kẹp (`PhuongHoai2023LowCostDelta`).
  - Giảm giá thành phần cứng bằng động cơ servo DC (`Vo2023DeltaPhanLoai`) hoặc động cơ bước (stepper motor) kết hợp gia công cắt laser và in 3D thay cho phay CNC (`PhuongHoai2023LowCostDelta`).
- **Ưu điểm:** Kiến trúc đơn giản, chi phí thấp, thuật toán thị giác HSV/contour nhẹ và phù hợp tuyệt đối với giới hạn "không dùng học sâu" trong đề cương (`Vo2023DeltaPhanLoai`, `Elassal2024LowCost`).
- **Hạn chế:** Sử dụng điều khiển vị trí mức cơ bản trên Arduino (không xét động lực học hay bộ điều khiển bám quỹ đạo nâng cao); tốc độ thực thi còn hạn chế (1,8 s/vật trong `Vo2023DeltaPhanLoai`); thiếu báo cáo định lượng đầy đủ về sai số vị trí (mm) và độ vọt lố (%) trong abstract (`PhuongHoai2023LowCostDelta`, `Elassal2024LowCost`, `Vo2023DeltaPhanLoai`).

---

## 3. Bảng so sánh tổng hợp

*Lưu ý: Bảng dưới đây chỉ sử dụng dữ kiện có trong 8 ghi chú tài liệu (`notes/*.md`). Mọi thông số không xuất hiện trong abstract/metadata được ghi rõ là "Không nêu (trong abstract)". Đơn vị chuẩn SI.*

| Tài liệu (Khoá BibTeX) | Nhóm phương pháp | Thuật toán Động học / Điều khiển / Thị giác | Điều kiện thí nghiệm (Mô phỏng / Phần cứng) | Chỉ tiêu đánh giá | Kết quả định lượng / định tính (từ notes) | Trạng thái & Hạn chế dữ liệu |
| --- | --- | --- | --- | --- | --- | --- |
| `Clavel1988Delta` (1988) | Nhóm 1 (Động học & Cơ cấu) | Cơ cấu song song 3 DOF tịnh tiến, khớp chủ động trên đế cố định | Thiết kế cơ khí gốc (không nêu chi tiết trong note) | Không nêu | Không nêu (chưa có bản gốc) | `[CẦN KIỂM CHỨNG]` Không có DOI trên Crossref; cần đối chiếu kỷ yếu ISIR 1988 |
| `Vischer1998Kinematic` (1998) | Nhóm 1 (Hiệu chuẩn động học) | Hiệu chuẩn sai số hình học (chiều dài khâu, vị trí khớp đế) | Robot Delta thực (chi tiết không nêu do thiếu abstract) | Sai số vị trí điểm cuối | Không nêu (OpenAlex không có abstract) | `[CẦN KIỂM CHỨNG]` Cần đọc toàn văn để lấy mô hình sai số và số liệu (mm) |
| `Castaneda2015Robust` (2015) | Nhóm 2 (Điều khiển quỹ đạo) | Output-based Adaptive ADRC + LMS thích nghi; so với PID + feed-forward và ADRC thường | Thực nghiệm trên Delta thật + Mô phỏng (quỹ đạo nhanh gấp 5 lần) | Sai số bám quỹ đạo | Định tính: tốt hơn PID + feed-forward và ADRC không thích nghi ở cả thực nghiệm và mô phỏng tốc độ gấp 5 lần. Số liệu: không nêu (trong abstract) | `[CẦN KIỂM CHỨNG]` Cần đọc toàn văn để lấy thông số robot, sai số bám (mm) và overshoot (%) |
| `Liu2020LADRC` (2020) | Nhóm 2 (Điều khiển quỹ đạo) | Mô hình động lực học + LADRC giải ghép (decoupling) 3 khớp bằng ESO | Chỉ mô phỏng (quỹ đạo số 8 xoắn ốc trong không gian, có nhiễu nội/ngoại) | Sai số bám quỹ đạo, tính bền vững | Định tính: "quick and precise", "strong robustness". Số liệu: không nêu (trong abstract) | `[CẦN KIỂM CHỨNG]` Chỉ mô phỏng; cần đọc toàn văn để lấy sai số bám và thông số quỹ đạo |
| `Yang2024FKNumerical` (2024) | Nhóm 1 (Động học & Vùng làm việc) | Động học thuận (FK) bằng phương pháp số + ràng buộc nghiệm; Monte Carlo tìm vùng làm việc | Mô hình 3 DOF; chỉ mô phỏng trên MATLAB (không có đo đạc thực nghiệm) | Vùng làm việc, tính duy nhất của nghiệm FK | Định tính: mô hình hợp lý qua so sánh tham số vùng chuyển động. Số liệu: không nêu (trong abstract) | Không có điều khiển quỹ đạo; thiếu thông số kích thước khâu và sai số hội tụ trong abstract |
| `Elassal2024LowCost` (2024) | Nhóm 3 (Hệ thống gắp–đặt + Vision) | Lọc dải màu + contour (bounding box); tính IK trên Arduino | Thực nghiệm: Raspberry Pi (master) + Arduino (slave) + động cơ + giác hút ("hydraulic system" với cốc hút) | Độ chính xác gắp–đặt trên băng tải | Định tính: "proved the effectiveness and accuracy". Số liệu: không nêu (trong abstract) | `[CẦN KIỂM CHỨNG]` Thuật ngữ "hydraulic system" cho giác hút trong abstract chưa rõ; thiếu toàn bộ số liệu định lượng |
| `PhuongHoai2023LowCostDelta` (2023) | Nhóm 3 (Hệ thống gắp–đặt + Vision) | Thị giác xác định tọa độ 3D + kích thước vật; mở kẹp theo kích thước | Thực nghiệm: Động cơ bước + Arduino Uno + khung cắt laser & in 3D | Sai số tọa độ gắp vật kích thước bất kỳ | Định tính: "small error", "works correctly". Số liệu: không nêu (trong abstract) | `[CẦN KIỂM CHỨNG]` Thứ tự/tên tác giả trên Crossref chưa khớp chuẩn tên Việt; thiếu số liệu sai số (mm) và chu kỳ (s) |
| `Vo2023DeltaPhanLoai` (2023) | Nhóm 3 (Hệ thống phân loại + Vision) | Chuyển ảnh BGR $\to$ HSV, phân ngưỡng (threshold) 3 màu | Thực nghiệm: 3 servo DC + Arduino + Raspberry Pi 4 + camera trên băng tải | Độ chính xác phân loại (%); thời gian trung bình/vật (s) | **100 %** (màu đỏ, vàng); **97,5 %** (màu xanh lá); thời gian trung bình **1,8 s/vật** | `[CẦN KIỂM CHỨNG]` Tổng số mẫu thử ($N$) và điều kiện chiếu sáng không nêu trong abstract |

---

## 4. Xu hướng nghiên cứu

Từ 8 công trình trải dài từ năm 1988 đến 2024, có thể rút ra **4 xu hướng rõ rệt**:

1. **Dịch chuyển từ cơ cấu công nghiệp đắt tiền sang nguyên mẫu chi phí thấp (low-cost prototyping) tích hợp xử lý ảnh nhúng (2023–2024):**  
   Trong khi các công trình đầu tiên tập trung vào kết cấu chuẩn công nghiệp (`Clavel1988Delta`, `Vischer1998Kinematic`), cả 3 công trình thực nghiệm gần nhất (`PhuongHoai2023LowCostDelta`, `Vo2023DeltaPhanLoai`, `Elassal2024LowCost`) đều hướng tới giảm giá thành bằng cách dùng in 3D, cắt laser, động cơ bước hoặc servo DC phổ thông, và kết hợp cặp xử lý Raspberry Pi (thị giác) + Arduino (điều khiển khớp).
2. **Ưu tiên thuật toán thị giác máy tính cổ điển (HSV, Contour) cho bài toán phân loại sản phẩm đơn giản trên phần cứng giới hạn (2023–2024):**  
   Dù học sâu rất phát triển, trong bài toán gắp–phân loại sản phẩm có đặc trưng màu sắc/hình khối rõ ràng trên băng tải, các nghiên cứu năm 2023–2024 vẫn chọn lọc ngưỡng không gian màu HSV (`Vo2023DeltaPhanLoai`) và bao hình contour/bounding box (`Elassal2024LowCost`) hoặc đo kích thước hình học (`PhuongHoai2023LowCostDelta`). Cách tiếp cận này giúp chạy thời gian thực trên Raspberry Pi 4 mà không cần GPU, đạt độ chính xác tới 97,5–100 % với 3 màu cơ bản (`Vo2023DeltaPhanLoai`) (nhận định của người tổng hợp).
3. **Ứng dụng giải số (Numerical Methods) và mô phỏng Monte Carlo trên MATLAB để giải quyết bài toán động học thuận và vùng làm việc (2024):**  
   Thay vì giải hệ phương trình phi tuyến phức tạp bằng đại số thuần tuý, xu hướng gần đây dùng công cụ tính toán số để tìm nghiệm FK có ràng buộc và quét đám mây điểm Monte Carlo nhằm trực quan hoá không gian làm việc 3D (`Yang2024FKNumerical`).
4. **Sử dụng điều khiển kháng nhiễu chủ động (ADRC/LADRC) có bù phi tuyến/giải ghép khi yêu cầu bám quỹ đạo tốc độ cao (2015–2020):**  
   Khi robot Delta vận hành ở tốc độ cao hoặc theo quỹ đạo phức tạp (như đường số 8 xoắn ốc hoặc tăng tốc gấp 5 lần), bộ điều khiển PID kinh điển bộc lộ hạn chế trước nhiễu khớp ghép và bất định động lực học; các tác giả chuyển sang dùng bộ quan sát ESO trong ADRC thích nghi (`Castaneda2015Robust`) hoặc LADRC giải ghép (`Liu2020LADRC`).

---

## 5. Mâu thuẫn và điểm chưa thống nhất

Khi đối chiếu chéo các tài liệu với nhau và với đề cương (`de-tai.md`), có **3 điểm mâu thuẫn / chưa thống nhất** cần lưu ý:

1. **Mâu thuẫn giữa độ phức tạp của lý thuyết điều khiển (Nhóm 2) và thực tế triển khai hệ thống phân loại (Nhóm 3):**  
   - *Hiện tượng:* `Castaneda2015Robust` và `Liu2020LADRC` khẳng định cần mô hình động lực học và bộ điều khiển ADRC/LADRC phức tạp để bám quỹ đạo chính xác (tốt hơn PID + feed-forward). Ngược lại, `Elassal2024LowCost`, `PhuongHoai2023LowCostDelta` và `Vo2023DeltaPhanLoai` chỉ tính động học nghịch (IK) thuần tuý trên vi điều khiển 8-bit Arduino Uno (thậm chí dùng động cơ bước vòng hở trong `PhuongHoai2023LowCostDelta`) mà vẫn báo cáo hệ thống hoạt động tốt ("effective and accurate", "small error", 97,5–100 %).  
   - *Nguyên nhân (nhận định của người tổng hợp):* Sự khác biệt nằm ở **chế độ vận hành và chỉ tiêu đo**. Nhóm 2 xét bài toán bám quỹ đạo liên tục tốc độ rất cao (high-speed continuous trajectory tracking) với lực quán tính và tương tác khớp lớn; trong khi Nhóm 3 vận hành ở tốc độ trung bình/thấp (chu kỳ 1,8 s/vật trong `Vo2023DeltaPhanLoai`) và chủ yếu quan tâm đến độ chính xác điểm đầu–điểm cuối (point-to-point pick-and-place) khi gắp vật nhẹ.
2. **Chưa thống nhất về lựa chọn cơ cấu dẫn động trong phân khúc chi phí thấp:**  
   - *Hiện tượng:* Cùng giải bài toán robot Delta giá rẻ gắn camera của nhóm tác giả Việt Nam năm 2023, `PhuongHoai2023LowCostDelta` chọn **động cơ bước (stepper motor)**, trong khi `Vo2023DeltaPhanLoai` chọn **động cơ servo DC (DC servo)**.  
   - *Nguyên nhân (nhận định của người tổng hợp):* Động cơ bước rẻ và dễ điều khiển góc bằng xung mà không cần bộ điều khiển vòng kín phức tạp, nhưng dễ trượt bước và giới hạn tốc độ (`PhuongHoai2023LowCostDelta`). Động cơ servo DC có phản hồi vị trí vòng kín và đáp ứng động học tốt hơn, phù hợp khi cần đảm bảo tốc độ gắp trên băng tải (`Vo2023DeltaPhanLoai`).
3. **Chênh lệch về chỉ tiêu thời gian chu kỳ gắp–thả (1,5 s trong đề cương so với 1,8 s trong thực nghiệm):**  
   - *Hiện tượng:* Đề cương `de-tai.md` đặt mục tiêu thời gian chu kỳ pick-place $\le 1,5\text{ s}$, trong khi tiền lệ thực nghiệm gần nhất (`Vo2023DeltaPhanLoai`) ghi nhận thời gian phân loại trung bình là **1,8 s/vật**.  
   - *Nguyên nhân (nhận định của người tổng hợp):* Các bài báo chưa có **định nghĩa thống nhất về "thời gian chu kỳ"**. Con số $1,8\text{ s/vật}$ trong `Vo2023DeltaPhanLoai` trên hệ thống thực nghiệm nhiều khả năng bao gồm cả thời gian chụp/xử lý ảnh trên Raspberry Pi 4, truyền thông nối tiếp sang Arduino, thời gian đóng/ngắt cơ cấu chấp hành cuối (end-effector) và di chuyển cơ khí có giới hạn công suất của servo DC giá rẻ. Trong khi đó, chu kỳ trong mô phỏng MATLAB/Simulink của đề cương thường chỉ tính **thời gian chuyển động theo quỹ đạo gắp–thả** (ví dụ: từ vị trí chờ $\to$ điểm gắp $\to$ điểm thả $\to$ vị trí chờ) với tham số vận tốc/gia tốc đặt trước.

---

## 6. Khoảng trống nghiên cứu

Dựa trên 8 tài liệu đã khảo sát, có **4 khoảng trống nghiên cứu** rõ rệt mà đề tài sinh viên năm 2 có thể khai thác:

- **Khoảng trống 1 — Thiếu kiểm chứng chéo định lượng giữa Động học thuận (FK) và Động học nghịch (IK) trên toàn vùng làm việc:**  
  - *Điều chưa ai làm (trong các bài đã đọc):* `Yang2024FKNumerical` giải FK bằng phương pháp số và vẽ vùng làm việc bằng Monte Carlo nhưng không công bố sai số định lượng (mm) hay đối chiếu vòng kín $\text{FK}(\text{IK}(x,y,z)) - (x,y,z)$.  
  - *Vì sao đáng làm:* Robot song song rất nhạy với kỳ dị (singularity) và đa nghiệm; nếu không kiểm chứng vòng kín $\text{IK} \leftrightarrow \text{FK}$, sai số công thức hoặc chọn nhầm nhánh nghiệm sẽ làm hỏng toàn bộ khâu điều khiển quỹ đạo phía sau (nhận định của người tổng hợp).  
  - *Đề tài này làm được tới đâu:* Xây dựng script Python (`sympy`/`numpy`) và MATLAB kiểm chứng vòng kín $\text{IK} \leftrightarrow \text{FK}$ (dùng giải tích kết hợp Newton–Raphson) trên hàng nghìn điểm lưới thuộc không gian làm việc tham chiếu $\varnothing 300 \times 150\text{ mm}$, báo cáo sai số cực đại và sai số căn quân phương (RMSE).
- **Khoảng trống 2 — Thiếu bộ số liệu chuẩn (Benchmark) cho bộ điều khiển kinh điển (PID / PID + bù tiến) trên kịch bản quỹ đạo gắp–thả tiêu chuẩn:**  
  - *Điều chưa ai làm (trong các bài đã đọc):* Các bài điều khiển (`Castaneda2015Robust`, `Liu2020LADRC`) tập trung vào thuật toán phức tạp (ADRC thích nghi, LADRC) trên quỹ đạo toán học (như đường số 8 xoắn ốc), còn các bài ứng dụng (`Vo2023DeltaPhanLoai`, `Elassal2024LowCost`) lại bỏ qua phân tích đáp ứng quá độ (độ vọt lố, thời gian xác lập, sai số bám).  
  - *Vì sao đáng làm:* Trước khi dùng các bộ điều khiển phức tạp hoặc chế tạo mạch thực, người thiết kế cần biết một bộ điều khiển đơn giản (PID hoặc PID + feed-forward) đạt được độ vọt lố bao nhiêu phần trăm và chu kỳ bao nhiêu giây trên quỹ đạo pick-and-place thực tế (nhận định của người tổng hợp).  
  - *Đề tài này làm được tới đâu:* Thiết kế quỹ đạo gắp–thả mượt (ví dụ: đa thức bậc 3/bậc 5 hoặc vận tốc hình thang) trong MATLAB/Simulink và định lượng rõ thời gian chu kỳ, độ vọt lố ($\le 5\,\%$) và sai số xác lập ($\le 1\text{ mm}$) của bộ điều khiển PID và PID + bù tiến.
- **Khoảng trống 3 — Thiếu báo cáo thống kê đầy đủ (ma trận nhầm lẫn, cỡ mẫu $\ge 100$, phân tích cả màu sắc lẫn hình dạng) trong bài toán thị giác cổ điển cho Delta:**  
  - *Điều chưa ai làm (trong các bài đã đọc):* `Vo2023DeltaPhanLoai` chỉ phân loại 3 màu (chưa xét hình dạng) và trong abstract không nêu cỡ mẫu hay ma trận nhầm lẫn (confusion matrix); `Elassal2024LowCost` và `PhuongHoai2023LowCostDelta` hoàn toàn không có số liệu phần trăm chính xác hay sai số tọa độ trong abstract.  
  - *Vì sao đáng làm:* Độ chính xác $100\,\%$ hay $97,5\,\%$ nếu chỉ thử trên cỡ mẫu nhỏ sẽ thiếu ý nghĩa thống kê và không cho biết cặp màu/hình nào dễ bị nhầm lẫn nhất (nhận định của người tổng hợp).  
  - *Đề tài này làm được tới đâu:* Đánh giá thuật toán phân ngưỡng HSV + hình học contour (OpenCV) trên tập dữ liệu $\ge 100$ mẫu (kết hợp cả màu sắc và hình dạng cơ bản như tròn, vuông, tam giác), xuất ma trận nhầm lẫn và sai số tâm vật quy đổi sang hệ tọa độ robot (mm).
- **Khoảng trống 4 — Thiếu một quy trình mô phỏng tích hợp đầu–cuối (End-to-End Simulation Pipeline) có khả năng tái lập cho bài toán phân loại bằng robot Delta:**  
  - *Điều chưa ai làm (trong các bài đã đọc):* Các bài báo hiện tách rời giữa mô phỏng động học/điều khiển (`Yang2024FKNumerical`, `Liu2020LADRC`) và lắp ráp phần cứng thử nghiệm trực tiếp (`Vo2023DeltaPhanLoai`, `Elassal2024LowCost`, `PhuongHoai2023LowCostDelta`).  
  - *Vì sao đáng làm:* Với điều kiện sinh viên năm 2 chưa có kinh phí chế tạo cơ khí chính xác, một pipeline mô phỏng nối liền từ đầu ra tọa độ/nhãn của OpenCV $\to$ quy hoạch quỹ đạo gắp–thả $\to$ động học nghịch $\to$ điều khiển khớp sẽ kiểm chứng trọn vẹn tính khả thi của toàn hệ thống trước khi ra bản vẽ CAD và danh mục linh kiện (BOM) (nhận định của người tổng hợp).  
  - *Đề tài này làm được tới đâu:* Thực hiện đúng Bước 4 của đề cương (`de-tai.md`): truyền dữ liệu tọa độ + loại sản phẩm từ Python/OpenCV sang mô phỏng quỹ đạo và điều khiển trên MATLAB/Simulink (hoặc Python thống nhất) để chạy kịch bản phân loại hoàn chỉnh.

---

## 7. Đánh giá chuyên sâu 4 yêu cầu của đề tài & Đề xuất phương án thực hiện

### 7.1. Trả lời 4 câu hỏi trọng tâm đối chiếu với đề cương (`de-tai.md`)

#### (1) Tính khả thi của 3 mục tiêu trong đề cương — Đánh giá thẳng chỉ tiêu chu kỳ $\le 1,5\text{ s}$ so với mốc $1,8\text{ s}$ của Vo & Le (2023)
- **Mục tiêu 1 (Sai số vị trí điểm cuối $\le 1\text{ mm}$ trên vùng làm việc $\varnothing 300 \times 150\text{ mm}$):** **Rất khả thi trong mô phỏng.** Trong môi trường mô phỏng không có rơ-le cơ khí (backlash) hay biến dạng nhiệt như bài toán thực tế của `Vischer1998Kinematic`, sai số vị trí điểm cuối chỉ phụ thuộc vào: (a) sai số hội tụ của thuật toán giải động học thuận/nghịch (có thể đạt $< 10^{-6}\text{ mm}$ bằng số) và (b) sai số xác lập / sai số bám của bộ điều khiển ở cuối quỹ đạo (hoàn toàn điều chỉnh được $< 1\text{ mm}$ qua hệ số khuếch đại điều khiển và thời gian dừng ở hai đầu quỹ đạo) (nhận định của người tổng hợp). Tuy nhiên, để mục tiêu $\le 1\text{ mm}$ có ý nghĩa kỹ thuật chứ không tầm thường (trivial), đề tài nên bổ sung **khảo sát độ nhạy sai số hình học** (cộng nhiễu giả lập $\pm 0,1\text{ mm}$ đến $\pm 0,5\text{ mm}$ vào chiều dài khâu theo tinh thần `Vischer1998Kinematic`) hoặc tính sai số quy đổi từ độ phân giải điểm ảnh camera (pixel-to-mm error) + sai số bám động lực học.
- **Mục tiêu 2 (Thời gian chu kỳ pick-place $\le 1,5\text{ s}$ và overshoot $\le 5\,\%$):** **Cần làm rõ định nghĩa chu kỳ; khuyến nghị giữ mốc $1,8\text{ s}$ của `Vo2023DeltaPhanLoai` làm mốc đối sánh thực nghiệm (baseline) và tách chỉ tiêu thành 2 mức: Chu kỳ chuyển động thuần tuý $\le 1,5\text{ s}$ và Chu kỳ toàn hệ thống $\le 1,8\text{–}2,0\text{ s}$.**  
  - *Lý do và bằng chứng:* Trong `Vo2023DeltaPhanLoai`, thời gian phân loại trung bình trên phần cứng thực tế (servo DC + Arduino + Raspberry Pi 4) là **$1,8\text{ s/vật}$**. Nếu sinh viên năm 2 làm **mô phỏng toán học**, việc đặt thời gian chạy quỹ đạo $T_{\text{traj}} \le 1,5\text{ s}$ là dễ dàng về mặt con số (chỉ cần tăng vận tốc/gia tốc đặt của quỹ đạo đa thức như cách `Castaneda2015Robust` tăng tốc quỹ đạo mô phỏng gấp 5 lần). Nhưng nếu ép chu kỳ xuống $\le 1,5\text{ s}$ một cách tuỳ tiện mà **không ràng buộc mô-men/vận tốc cực đại của động cơ thực tế** (ví dụ động cơ servo DC phổ thông hoặc động cơ bước như trong `Vo2023DeltaPhanLoai`, `PhuongHoai2023LowCostDelta`), kết quả mô phỏng sẽ phi thực tế và gây vọt lố lớn ($> 5\,\%$). Hơn nữa, một chu kỳ phân loại thực tế gồm:
    $$T_{\text{total}} = t_{\text{vision}} + t_{\text{move\_to\_pick}} + t_{\text{grip}} + t_{\text{move\_to\_place}} + t_{\text{release}} + t_{\text{return}}$$
  - *Khuyến nghị cụ thể (nhận định của người tổng hợp):* Không nên xoá bỏ con số $1,5\text{ s}$ nếu đề cương đã duyệt, nhưng phải quy định minh bạch trong báo cáo:
    1. **Chỉ tiêu chuyển động cơ học thuần tuý (Pure Kinematic/Dynamic Motion Cycle):** $\le 1,5\text{ s}$ (gồm thời gian di chuyển gắp và thả trong mô phỏng với giới hạn vận tốc góc khớp phù hợp linh kiện trong BOM).
    2. **Chỉ tiêu toàn chu trình phân loại (Full Sorting Cycle — tính cả thời gian xử lý ảnh OpenCV $\approx 0,05\text{–}0,15\text{ s}$ và trễ đóng/nhả đầu hút/kẹp $\approx 0,2\text{–}0,3\text{ s}$):** nới thành **$\le 1,8\text{–}2,0\text{ s}$**, lấy đúng con số **$1,8\text{ s/vật}$ của `Vo2023DeltaPhanLoai` làm mốc chuẩn thực nghiệm (benchmark)** để chứng minh mô hình mô phỏng có tính thực tiễn sát với phần cứng chi phí thấp tại Việt Nam.
- **Mục tiêu 3 (Phân loại bằng camera đạt độ chính xác $\ge 90\,\%$ trên $\ge 100$ mẫu):** **Hoàn toàn khả thi.** Bằng chứng là `Vo2023DeltaPhanLoai` dùng ngưỡng màu HSV trên Raspberry Pi 4 đã đạt **97,5 % – 100 %** trên 3 màu. Với mô phỏng/thí nghiệm ảo trên tập $\ge 100$ ảnh mẫu (có thêm biến thiên độ sáng/nhiễu nhẹ và phân biệt 2–3 hình dạng bằng contour như `Elassal2024LowCost`), ngưỡng $\ge 90\,\%$ là vừa sức và có tính thuyết phục cao.

#### (2) Chọn cách tiếp cận động học: Giải tích (Geometric/Vector Loop) so với Phương pháp số (Newton–Raphson)
- **So sánh hai hướng tiếp cận cho Động học nghịch (IK) và Động học thuận (FK):**

| Tiêu chí | Hướng Giải tích (Geometric / Vector Loop Closure — theo nền tảng `Clavel1988Delta`) | Hướng Giải số (Numerical / Newton–Raphson — theo hướng `Yang2024FKNumerical`) |
| --- | --- | --- |
| **Động học nghịch (IK): $(x,y,z) \to (\theta_1,\theta_2,\theta_3)$** | Mỗi nhánh độc lập đưa về phương trình lượng giác cổ điển $E_i \cos\theta_i + F_i \sin\theta_i + G_i = 0$; giải tường minh bằng phép thế $t_i = \tan(\theta_i/2)$. Tốc độ tính toán cực nhanh, chính xác tuyệt đối, phát hiện ngay điểm ngoài vùng làm việc khi biệt thức $\Delta < 0$. | Không cần thiết vì nghiệm giải tích tường minh của IK Delta rất gọn; dùng lặp số cho IK vừa chậm vừa có nguy cơ hội tụ nhầm nhánh nghiệm (khuỷu tay quay vào trong/ra ngoài). |
| **Động học thuận (FK): $(\theta_1,\theta_2,\theta_3) \to (x,y,z)$** | Là giao điểm của 3 mặt cầu (trilateration). Có thể giải giải tích bằng khử đại số đưa về phương trình bậc 2 một ẩn, nhưng biểu thức dài, dễ nhầm dấu hoặc suy biến khi 3 tâm cầu nằm trên mặt phẳng đặc biệt (nhận định của người tổng hợp). | Thiết lập hệ 3 phương trình phi tuyến $f_i(x,y,z) = 0$ và lặp Newton–Raphson với ma trận Jacobian; kết hợp ràng buộc nghiệm ($z < 0$) như `Yang2024FKNumerical`. Rất dễ lập trình bằng `sympy`/`numpy`/MATLAB, dùng trực tiếp được ma trận Jacobian cho phân tích kỳ dị. |

- **Khuyến nghị lựa chọn (nhận định của người tổng hợp):**
  - **Trục chính (Primary Method) để điều khiển và chạy thời gian thực:** Dùng **Giải tích hình học / khép kín vector (Geometric / Vector-loop analytical method)** cho **Động học nghịch (IK)** (để tính góc khớp từ quỹ đạo $(x(t), y(t), z(t))$ tương tự cách các bài `Elassal2024LowCost`, `Vo2023DeltaPhanLoai` nạp lên vi điều khiển) kết hợp với phương pháp **Giao điểm 3 mặt cầu (Analytical Trilateration)** cho **Động học thuận (FK)**.
  - **Công cụ kiểm chứng chéo (Cross-validation Method) và quét vùng làm việc:** Dùng **Phương pháp số Newton–Raphson + Monte Carlo** (theo `Yang2024FKNumerical`) cho **Động học thuận (FK)**. Cụ thể: lấy nghiệm FK bằng Newton–Raphson đối chiếu với nghiệm FK giải tích và kiểm tra vòng kín $\|(x,y,z) - \text{FK}_{\text{NR}}(\text{IK}_{\text{analytical}}(x,y,z))\|_2 \le 10^{-6}\text{ mm}$ trên toàn bộ đám mây điểm Monte Carlo. Cách làm này giải quyết triệt để rủi ro số 1 trong đề cương (`de-tai.md`, mục 8) và tạo điểm nhấn học thuật vượt lên trên `Yang2024FKNumerical`.

#### (3) Mức độ điều khiển hợp lý: PID + Bù tiến (Feed-forward) so với ADRC/LADRC và giới hạn khi chỉ dùng PID
- **Đánh giá tính công bằng của PID + Feed-forward trong phạm vi đề tài:**  
  Trong `Castaneda2015Robust`, chính các tác giả đã sử dụng **PID có bù tiến (PID with feed-forward)** làm **bộ điều khiển chuẩn đối sánh (baseline)** khi thử nghiệm thực tế và mô phỏng trước khi chứng minh ưu thế của Adaptive ADRC. Tương tự, `Liu2020LADRC` giải bài toán bám quỹ đạo ở tốc độ cao với mô hình động lực học đầy đủ. Tuy nhiên, đề cương (`de-tai.md`, mục 4) đã giới hạn rõ: *"Trọng tâm động học (kinematics); động lực học chỉ ở mức cơ bản... Robot không chịu tải lớn, giả thiết khâu nhẹ"*. Do đó, với sinh viên năm 2 trong 12 tuần, việc thiết kế **PID + bù tiến vận tốc/gia tốc (hoặc bù trọng lực/quán tính rút gọn)** trên mô hình động lực học khớp độc lập (có nhiễu tương tác giả lập) là **hoàn toàn hợp lý, vừa sức và đủ công bằng** để làm baseline học thuật mà không cần cài đặt Adaptive ADRC + LMS (`Castaneda2015Robust`) hay LADRC giải ghép (`Liu2020LADRC`) (nhận định của người tổng hợp).
- **Nếu đề tài chỉ dùng PID kinh điển (hoặc thêm Feed-forward cơ bản), báo cáo bắt buộc phải nêu rõ 4 giới hạn sau:**
  1. *Giả thiết tách khớp (Decoupled joints assumption):* Bộ điều khiển PID đơn biến (SISO) cho từng khớp bỏ qua thành phần tương tác động lực học phi tuyến (Coriolis, ly tâm và ma trận quán tính phụ thuộc cấu hình) giữa 3 nhánh song song mà `Liu2020LADRC` đã chỉ ra.
  2. *Giới hạn ở tốc độ cao và khi thay đổi tải:* Như `Castaneda2015Robust` đã chứng minh khi tăng tốc quỹ đạo gấp 5 lần, PID cố định hệ số sẽ tăng sai số bám và độ vọt lố khi gia tốc lớn hoặc khi khối lượng vật gắp thay đổi.
  3. *Yêu cầu đo/ước lượng đạo hàm:* Khâu vi phân (D) trong PID nhạy cảm với nhiễu đo lường, trong khi phương pháp của `Castaneda2015Robust` dùng bộ quan sát thích nghi chỉ dựa trên đầu ra vị trí.
  4. *Phạm vi áp dụng:* Khẳng định rõ PID / PID + Feed-forward đáp ứng tốt chỉ tiêu $\text{overshoot} \le 5\,\%$ và chu kỳ $1,5\text{–}1,8\text{ s}$ vì robot hoạt động ở chế độ gắp–thả vật nhẹ (light-payload pick-and-place) như `Vo2023DeltaPhanLoai`, `Elassal2024LowCost`, chứ không phải gia công hay bám quỹ đạo xoắn ốc siêu tốc như `Liu2020LADRC`.

#### (4) Rủi ro về số liệu: Các mục đang thiếu số trong bảng so sánh và cần đọc toàn văn
Hiện tại, **7/8 tài liệu** trong `bang-so-sanh.md` thiếu số liệu định lượng do mới chỉ khai thác được phần abstract/metadata (chỉ duy nhất `Vo2023DeltaPhanLoai` có số liệu độ chính xác 100 % / 97,5 % và chu kỳ 1,8 s/vật ngay trong abstract). Đây là **rủi ro lớn nhất khi viết báo cáo và bảo vệ** nếu sinh viên trích dẫn mà không có con số cụ thể. Các mục bắt buộc phải đọc toàn văn (full-text) gồm:

1. **`Vo2023DeltaPhanLoai` (Ưu tiên số 1 — Mở toàn văn ngay, tạp chí IJECE là Open Access):**
   - *Thiếu:* Kích thước hình học các khâu của robot Delta ($R, r, L, l$), kích thước vùng làm việc, tổng số mẫu thử nghiệm ($N$) cho mỗi màu, định nghĩa chính xác của thời gian "1,8 s/vật", và sai số vị trí gắp–thả (mm).
2. **`PhuongHoai2023LowCostDelta` (Ưu tiên số 2 — FME Transactions là Open Access):**
   - *Thiếu:* Con số cụ thể của "small error" (sai số tọa độ $x, y, z$ bằng bao nhiêu $\text{mm}$?), kích thước khâu, thời gian chu kỳ gắp của hệ dùng động cơ bước, và **trang bìa bài báo** để sửa lỗi `[CẦN KIỂM CHỨNG]` về thứ tự Họ/Tên tác giả Việt Nam trong `references.bib`.
3. **`Elassal2024LowCost` (Ưu tiên số 3 — e-Prime trên ScienceDirect là Open Access):**
   - *Thiếu:* Độ chính xác nhận dạng màu/contour (%), sai số vị trí gắp (mm), thời gian chu kỳ (s), và kiểm chứng lại cụm từ "hydraulic system" cho giác hút chân không trong abstract.
4. **`Yang2024FKNumerical` (Ưu tiên số 4):**
   - *Thiếu:* Bộ thông số hình học của robot Delta 3 DOF dùng trong mô phỏng MATLAB, kích thước vùng làm việc Monte Carlo ($\text{mm}$), và sai số hội tụ của thuật toán giải số FK.
5. **`Castaneda2015Robust` & `Liu2020LADRC` (Ưu tiên số 5):**
   - *Thiếu:* Bảng chỉ số sai số bám (ISE/ITAE/RMSE tính bằng $\text{mm}$ hoặc $\text{deg}$) và độ vọt lố (%) của bộ điều khiển PID + feed-forward so với ADRC/LADRC để lấy làm con số tham chiếu cho Chương Điều khiển.
6. **`Clavel1988Delta` & `Vischer1998Kinematic` (Ưu tiên số 6):**
   - *Thiếu:* Kiểm chứng thông tin xuất bản gốc của `Clavel1988Delta` (`[CẦN KIỂM CHỨNG]`) và độ lớn sai số vị trí trước/sau hiệu chuẩn (mm) trong `Vischer1998Kinematic`.

---

### 7.2. Đề xuất 3 phương án triển khai cho đề tài (dành cho sinh viên năm 2 — 12 tuần)

| Phương án | Nội dung kỹ thuật cốt lõi | Độ khó & Thời gian | Thiết bị / Công cụ | Rủi ro chính & Đánh giá |
| --- | --- | --- | --- | --- |
| **Phương án 1: Tiêu chuẩn — Bám sát đề cương, tối ưu tính tái lập (KHUYẾN NGHỊ CHỌN)** | - **Động học:** IK giải tích + FK giải tích & kiểm chứng chéo bằng FK Newton–Raphson + Monte Carlo vùng làm việc $\varnothing 300 \times 150\text{ mm}$ (`Yang2024FKNumerical`).<br>- **Quỹ đạo & Điều khiển:** Quỹ đạo đa thức bậc 5 (quintic polynomial) pick-and-place; so sánh **PID** và **PID + Feed-forward** (lấy cảm hứng baseline từ `Castaneda2015Robust`) trên mô hình động lực học khớp rút gọn có nhiễu.<br>- **Thị giác:** OpenCV lọc ngưỡng HSV + Contour (`Vo2023DeltaPhanLoai`, `Elassal2024LowCost`) phân loại 3 màu $\times$ 3 hình dạng trên $\ge 120$ ảnh mẫu.<br>- **Tích hợp & Thiết kế:** Nối pipeline Python $\leftrightarrow$ MATLAB/Simulink + Bản vẽ CAD & BOM chi phí thấp (`PhuongHoai2023LowCostDelta`). | **Vừa sức** (Đúng 12 tuần theo kế hoạch đề cương). | Máy tính cá nhân (Python `sympy`, `numpy`, `opencv-python` + MATLAB/Simulink + SolidWorks). Kinh phí phần cứng: 0 đ (chỉ thiết kế CAD + BOM). | - *Rủi ro:* Giao tiếp Python – MATLAB/Simulink gây trễ tiến độ tuần 9.<br>- *Giảm thiểu:* Xuất file dữ liệu trung gian (`.csv`/`.json`) từ OpenCV sang Simulink, đồng thời có script mô phỏng hoàn chỉnh chạy 100 % trên Python để đảm bảo tái lập. |
| **Phương án 2: Nâng cao về Điều khiển & Độ nhạy sai số (Thiên về mô hình toán)** | Như Phương án 1, nhưng **bổ sung**:<br>- Thiết kế thêm bộ điều khiển **LADRC bậc hai** (theo hướng `Liu2020LADRC`) để so sánh trực tiếp 3 bộ điều khiển: PID vs PID + Feed-forward vs LADRC trên cùng quỹ đạo gắp–thả.<br>- Mô phỏng **sai số hình học chế tạo** ($\pm 0,2\text{ mm}$ chiều dài khâu theo `Vischer1998Kinematic`) để chứng minh khi nào sai số điểm cuối vượt ngưỡng $1\text{ mm}$. | **Khá cao** với sinh viên năm 2 (Dễ lố thời gian ở tuần 5–6). | Python + MATLAB/Simulink. | - *Rủi ro:* Mất quá nhiều thời gian chỉnh tham số bộ quan sát ESO của LADRC làm ảnh hưởng phần tích hợp camera và vẽ CAD.<br>- *Chỉ chọn khi:* Sinh viên có nền tảng toán và điều khiển tự động tốt. |
| **Phương án 3: Kết hợp Mô phỏng + Thí nghiệm phần cứng một phần (Hardware-in-the-loop thu nhỏ)** | Giữ phần Động học và Mô phỏng điều khiển ở mức cơ bản (chỉ PID), dành thời gian gắn **1 camera USB thực tế** chụp các vật mẫu thật trên bàn (3 màu, 2–3 hình dạng) xử lý qua OpenCV và gửi góc khớp IK qua cổng Serial tới **1 mạch Arduino Uno** (theo kiến trúc `Vo2023DeltaPhanLoai`, `Elassal2024LowCost`) để đo thời gian xử lý thực tế (chưa cần dựng khung cơ khí Delta hoàn chỉnh). | **Trung bình – Cao** (Phụ thuộc kỹ năng phần cứng). | Máy tính + Webcam USB + Arduino Uno (chi phí $< 500.000\text{ VNĐ}$). | - *Rủi ro:* Nhiễu ánh sáng thực tế làm giảm độ chính xác HSV nếu không có hộp chụp cố định; phân tán thời gian viết báo cáo.<br>- *Điểm cộng:* Có số liệu thời gian trễ thực tế của camera + Arduino để cộng vào chu kỳ mô phỏng. |

---

## 8. Cần bổ sung (Dành cho `literature` thực hiện ở bước tiếp theo)

Để hoàn thiện cơ sở dữ liệu tài liệu trước khi bước sang tuần 3–4 (Mô hình hoá động học) và viết báo cáo, đề nghị agent `literature` bổ sung các nội dung sau:

1. **Tải và trích xuất số liệu toàn văn (Full-text Extraction) cho 3 bài Open Access sát đề tài nhất:**
   - `Vo2023DeltaPhanLoai` (*IJECE*, 2023, DOI: `10.11591/ijece.v13i3.pp2669-2676`): lấy bảng kích thước khâu Delta, cỡ mẫu thử nghiệm, sai số vị trí (nếu có) và cách tính chu kỳ $1,8\text{ s/vật}$.
   - `PhuongHoai2023LowCostDelta` (*FME Transactions*, 2023, DOI: `10.5937/fme2301099p`): lấy số liệu sai số tọa độ ("small error" cụ thể là bao nhiêu $\text{mm}$), thông số cơ khí và **kiểm chứng lại tên tác giả trên PDF gốc** để xóa nhãn `[CẦN KIỂM CHỨNG]` (dự kiến tên chuẩn là Lê Hoài Phương, Võ Duy Công, Thái Thị Ngọc Hiệp hoặc tương đương).
   - `Elassal2024LowCost` (*e-Prime*, 2024, DOI: `10.1016/j.prime.2024.100518`): lấy thông số hình học, độ chính xác nhận dạng contour/màu, sai số gắp–đặt và làm rõ cơ cấu giác hút chân không.
2. **Bổ sung 1–2 tài liệu chuẩn về dẫn giải phương trình Động học thuận/nghịch giải tích và Quy hoạch quỹ đạo pick-and-place cho robot Delta:**
   - Trong 8 bài hiện tại, `Clavel1988Delta` chưa có bản gốc và `Yang2024FKNumerical` chỉ tóm tắt hướng giải số FK. Cần tìm thêm **1 bài báo hoặc chương sách có DOI kiểm chứng được** trình bày tường minh hệ phương trình động học nghịch/thuận giải tích (giao 3 mặt cầu) và quy hoạch quỹ đạo gắp–thả (ví dụ quỹ đạo đa thức hoặc hình thang cho Delta) để làm tài liệu tham chiếu trực tiếp cho các công thức toán trong `nghien-cuu/mo-hinh/`.
3. **Bổ sung tài liệu trong nước (nếu truy cập được):**
   - Tìm thêm 1–2 bài báo khoa học tiếng Việt (ví dụ từ *Tạp chí Khoa học và Công nghệ — ĐH Điện lực*, *Tạp chí Cơ khí Việt Nam*, hoặc hội nghị *VCCA* / *Hội nghị Cơ điện tử toàn quốc VCM*) về mô phỏng động học/điều khiển robot Delta để tăng tính gắn kết với bối cảnh nghiên cứu trong nước.
4. **Giải quyết dứt điểm các mục `[CẦN KIỂM CHỨNG]` trong `references.bib`:**
   - Xác minh thông tin thư mục đầy đủ của `Clavel1988Delta` hoặc thay thế/bổ sung bằng một bài báo tổng quan/động học Delta có DOI hợp lệ trên Crossref.
