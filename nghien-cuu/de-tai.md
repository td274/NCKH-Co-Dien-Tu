# Đề cương nghiên cứu khoa học

## 1. Thông tin chung

| | |
| --- | --- |
| Tên đề tài (VI) | Nghiên cứu và mô phỏng robot Delta cho ứng dụng phân loại sản phẩm bằng camera |
| Tên đề tài (EN) | Study and simulation of a Delta robot for camera-based product sorting |
| Sinh viên thực hiện | ... |
| Lớp / Khoa | ... (Khoa Cơ điện tử — ĐH Điện lực) |
| Giảng viên hướng dẫn | ... |
| Thời gian thực hiện | 12 tuần |

## 2. Đặt vấn đề

- **Hiện tượng / nhu cầu thực tiễn:** trong dây chuyền phân loại (thực phẩm, linh kiện
  điện tử, bao bì), robot Delta là lựa chọn phổ biến nhờ tốc độ cao và độ chính xác
  vị trí tốt. Việc phân loại thủ công chậm và dễ sai; kết hợp robot Delta với camera
  cho phép tự động hoá khâu gắp–phân loại.
- **Vì sao chọn đề tài:** chi phí chế tạo robot Delta thật cao, nên trước khi đầu tư
  phần cứng cần một **mô hình mô phỏng** kiểm chứng động học, quỹ đạo và chiến lược
  phân loại. Đây là bài toán trọn vẹn cho sinh viên năm 2: động học song song, điều
  khiển quỹ đạo và xử lý ảnh ở mức vừa sức.
- **Câu hỏi nghiên cứu:** (1) mô hình động học thuận/nghịch của robot Delta 3 bậc tự do
  có thể kiểm chứng được trong không gian làm việc đến mức sai số nào? (2) kết hợp
  nhận dạng màu/hình bằng camera với quỹ đạo gắp–thả có đạt chỉ tiêu chu kỳ và độ
  chính xác đặt ra trong mô phỏng không?

## 3. Mục tiêu

**Tổng quát:** xây dựng mô hình toán và mô phỏng robot Delta 3 bậc tự do dùng cho
phân loại sản phẩm theo tín hiệu camera, làm cơ sở thiết kế phần cứng sau này.

**Cụ thể (đo được):**
1. Dẫn giải và kiểm chứng động học nghịch/thuận Delta; sai số vị trí điểm cuối trong
   mô phỏng ≤ 1 mm trên không gian làm việc tham chiếu Ø300 × 150 mm.
2. Thiết kế quỹ đạo gắp–thả (đa thức bậc 5) và bộ điều khiển vị trí; mô phỏng đạt
   **chu kỳ chuyển động thuần ≤ 1,5 s** và **chu kỳ toàn hệ thống (gồm xử lý ảnh +
   đóng/nhả đầu gắp) ≤ 1,8 s**, lấy mốc **1,8 s/vật của Vo & Le 2023** làm chuẩn đối
   sánh; overshoot ≤ 5 %.
3. Xây dựng module phân loại bằng camera (màu sắc/hình dạng đơn giản) đạt độ chính
   xác ≥ 90 % trên tập mẫu ≥ 100 vật trong mô phỏng/thí nghiệm ảo.

## 4. Phạm vi và giới hạn

- **Đối tượng:** robot Delta 3 bậc tự do (chuyển động tịnh tiến x–y–z), không quay đầu
  gắp (bỏ bậc tự do quay Rz).
- **Trọng tâm động học (kinematics); động lực học chỉ ở mức cơ bản** (bỏ qua nếu vượt
  thời gian). Robot không chịu tải lớn, giả thiết khâu nhẹ.
- **Camera:** nhận dạng màu/hình đơn giản (ngưỡng màu, contour), **không dùng học sâu**.
- **Phần cứng ở mức thiết kế** (mô hình CAD, sơ đồ, danh mục linh kiện) + nguyên mẫu
  thu nhỏ chỉ nếu còn thời gian và kinh phí. Ưu tiên mô phỏng.

## 5. Phương pháp

| Bước | Việc làm | Công cụ | Đầu ra kiểm chứng được |
| --- | --- | --- | --- |
| 1 | Mô hình hoá động học nghịch/thuận | giấy + Python (sympy) | Hệ phương trình + kiểm tra đơn vị, vùng làm việc |
| 2 | Mô phỏng quỹ đạo + điều khiển | MATLAB/Simulink | Đồ thị sai số, thời gian chu kỳ, overshoot |
| 3 | Mô phỏng phân loại bằng camera | Python/OpenCV (ảnh mẫu) | Ma trận nhầm lẫn, độ chính xác % |
| 4 | Tích hợp nhận dạng → quỹ đạo gắp–thả | MATLAB + Python | Kịch bản mô phỏng phân loại hoàn chỉnh |
| 5 | Thiết kế cơ khí | SolidWorks/Fusion (tuỳ có) | CAD + bản vẽ + BOM |

## 6. Sản phẩm dự kiến

- Mô hình toán động học Delta + bộ điều khiển quỹ đạo (có script kiểm chứng).
- Bộ mô phỏng (MATLAB/Simulink + Python/OpenCV) chạy lại được.
- Bản thiết kế cơ khí + danh mục linh kiện (BOM).
- Báo cáo + slide bảo vệ.

## 7. Kế hoạch theo tuần

| Tuần | Nội dung | Đầu ra | Trạng thái |
| --- | --- | --- | --- |
| 1–2 | Khảo sát tài liệu (delta, động học song song, phân loại ảnh) | `tai-lieu/` notes + bảng so sánh + `tong-quan.md` | |
| 3–4 | Động học nghịch/thuận + kiểm chứng sympy | `mo-hinh/` + script | |
| 5–6 | Mô phỏng quỹ đạo + điều khiển trên MATLAB | `mo-phong/runs/` + KETQUA | |
| 7–8 | Module phân loại camera (OpenCV) | `mo-phong/` (ảnh) + độ chính xác | |
| 9 | Tích hợp nhận dạng → gắp–thả | kịch bản mô phỏng hoàn chỉnh | |
| 10 | Thiết kế CAD + BOM | bản vẽ + danh mục | |
| 11 | Phản biện + chỉnh sửa | `/phan-bien` đạt | |
| 12 | Viết báo cáo + slide | `bao-cao/` | |

## 8. Rủi ro và phương án dự phòng

| Rủi ro | Khả năng | Ảnh hưởng | Dự phòng |
| --- | --- | --- | --- |
| Động học thuận Delta không có nghiệm tường minh | Cao | Khó kiểm chứng vòng kín | Dùng nghiệm số (Newton–Raphson) + so với nghịch |
| Tích hợp camera → quỹ đạo phức tạp hơn dự kiến | Trung bình | Trễ tiến độ tuần 7–9 | Thu hẹp: phân loại theo màu 2–3 lớp trước, thêm hình sau |
| MATLAB mất nhiều thời gian học Simulink | Trung bình | Trễ tiến độ | Làm trước bằng Python, chuyển Simulink khi đủ |
| Phần cứng nguyên mẫu không kịp kinh phí | Trung bình | Giảm phạm vi thực nghiệm | Đề tài vẫn hoàn chỉnh ở mức mô phỏng + thiết kế |

## 9. Tài liệu tham khảo

*(Trống — sẽ bổ sung qua `/khao-sat`. Mọi mục phải có DOI/URL kiểm chứng được, tra
Crossref trước khi ghi vào `references.bib`. Không bịa.)*
