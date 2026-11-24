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
| Phương án triển khai | **Phương án 3 — mô phỏng + thí nghiệm phần cứng một phần (hardware-in-the-loop thu nhỏ)** |

## 2. Đặt vấn đề

- **Hiện tượng / nhu cầu thực tiễn:** trong dây chuyền phân loại (thực phẩm, linh kiện
  điện tử, bao bì), robot Delta là lựa chọn phổ biến nhờ tốc độ cao và độ chính xác
  vị trí tốt. Việc phân loại thủ công chậm và dễ sai; kết hợp robot Delta với camera
  cho phép tự động hoá khâu gắp–phân loại.
- **Vì sao chọn đề tài:** chế tạo robot Delta hoàn chỉnh tốn kém, nên bước đi hợp lý là
  **mô phỏng động học + đo trễ thực tế của chuỗi thị giác → vi điều khiển** trước khi
  đầu tư cơ khí. Đây là điểm yếu phổ biến của các đồ án sinh viên: mô phỏng đẹp nhưng
  không biết trễ thực bao nhiêu, nên khi lắp thật thì chu kỳ vượt xa thiết kế.
- **Câu hỏi nghiên cứu:** (1) mô hình động học thuận/nghịch của robot Delta 3 bậc tự do
  đạt sai số nào khi kiểm chứng chéo trên toàn vùng làm việc? (2) trễ thực tế của chuỗi
  camera → OpenCV → Arduino chiếm bao nhiêu trong chu kỳ phân loại, và chu kỳ tổng có
  đạt mốc 1,8 s/vật đã công bố không?

## 3. Mục tiêu

**Tổng quát:** xây dựng mô hình toán, mô phỏng và một nguyên mẫu thí nghiệm một phần
(webcam + Arduino, chưa có khung cơ khí Delta) cho bài toán phân loại sản phẩm bằng
camera, làm cơ sở thiết kế phần cứng hoàn chỉnh.

**Cụ thể (đo được):**
1. Dẫn giải và kiểm chứng chéo động học nghịch (IK) ↔ thuận (FK) của Delta 3 bậc tự do;
   sai số vòng kín cực đại ≤ 1 mm trên không gian làm việc tham chiếu Ø300 × 150 mm,
   báo cáo max error và RMSE trên ≥ 1000 điểm lưới. **Bổ sung khảo sát độ nhạy:** khi
   chiều dài khâu sai lệch ±0,2 mm (sai số chế tạo), báo cáo phân bố sai số điểm cuối
   (max, phân vị 95 %) và đối chiếu với ngưỡng 1 mm.
2. Thiết kế quỹ đạo gắp–thả (đa thức bậc 5) + PID/feed-forward; mô phỏng đạt **chu kỳ
   chuyển động 3 đoạn 0,96 s** (T = 0,32 s, kèm 2 pha dừng 0,25 s để kẹp/thả → chu kỳ
   1,46 s), overshoot ≤ 5 %; **chu kỳ toàn hệ thống ≤ 1,8 s** khi cộng trễ camera +
   truyền thông (mốc đối chiếu: 1,8 s/vật của Vo & Le 2023). Điểm vận hành chốt:
   τ = 1,14 N·m (đã gồm trọng lực), ω = 7,25 rad/s, hệ số an toàn mô-men 2,23.
3. Xây dựng module phân loại trên **vật thật** (webcam, 3 màu × 3 hình dạng) đạt độ
   chính xác ≥ 90 % trên ≥ 120 vật mẫu, có ma trận nhầm lẫn; đo và báo cáo trễ xử lý
   ảnh thực tế.

## 4. Phạm vi và giới hạn

- **Đối tượng:** robot Delta 3 bậc tự do tịnh tiến (x–y–z), không có bậc quay đầu gắp.
- **Động học là trọng tâm**; động lực học chỉ ở mức cơ bản, điều khiển dừng ở **PID**
  (không ADRC/LADRC), có nêu rõ giả thiết tách khớp khi báo cáo.
- **Phần cứng làm tới mức hardware-in-the-loop:** webcam USB + Arduino Uno nhận góc khớp
  qua Serial và xuất PWM; **không dựng khung cơ khí Delta hoàn chỉnh** — phần cơ khí
  dừng ở bản vẽ CAD + BOM.
- **Camera:** nhận dạng màu/hình bằng ngưỡng HSV + contour (OpenCV), **không học sâu**.
- **Không thực hiện:** gia công cơ khí chính xác, hiệu chuẩn động học trên robot thật,
  điều khiển bám quỹ đạo tốc độ cao.

### Phần cứng tối thiểu (dự kiến < 500.000 VNĐ)

| Thiết bị | Thông số tối thiểu | Dùng để |
| --- | --- | --- |
| Webcam USB | ≥ 720p, 30 fps, đặt cố định trên cao | Chụp vật trên mặt bàn |
| Arduino Uno (hoặc tương đương) | Có UART/USB Serial | Nhận góc khớp, xuất PWM, đo trễ |
| Hộp chụp / đèn | Giấy trắng mờ + 1 đèn LED | Giảm nhiễu ánh sáng cho HSV |
| Vật mẫu | ≥ 120 vật: 3 màu × 3 hình (tròn/vuông/tam giác) | Tập kiểm thử phân loại |

## 5. Phương pháp

| Bước | Việc làm | Công cụ | Đầu ra kiểm chứng được |
| --- | --- | --- | --- |
| 1 | Động học nghịch giải tích (vector loop) | giấy + Python (sympy) | Công thức θᵢ(x,y,z) + kiểm tra đơn vị |
| 2 | Động học thuận + kiểm chứng chéo Newton–Raphson, quét Monte Carlo | Python/MATLAB | Bảng sai số vòng kín IK↔FK (max, RMSE) |
| 3 | Quỹ đạo gắp–thả bậc 5 + PID/feed-forward, mô phỏng có pha dừng | Python (scipy) | Đồ thị sai số bám, overshoot thật, bảng quét chu kỳ |
| 4 | Thị giác trên vật thật: HSV + contour | Python/OpenCV + webcam | Ma trận nhầm lẫn, độ chính xác %, trễ xử lý |
| 5 | Truyền góc khớp qua Serial, đo trễ vòng | Python ↔ Arduino | Số đo trễ (ms) theo từng công đoạn |
| 6 | Ghép chu kỳ tổng + thiết kế CAD/BOM | Python (pandas) + CAD | Bảng phân rã chu kỳ, bản vẽ, BOM |

## 6. Sản phẩm dự kiến

- Mô hình toán IK/FK + script kiểm chứng chéo (kèm bảng sai số).
- Bộ mô phỏng quỹ đạo + PID chạy lại được (MATLAB/Simulink hoặc Python).
- Module thị giác chạy thật với webcam + tập dữ liệu ≥ 120 vật và ma trận nhầm lẫn.
- Firmware Arduino nhận góc khớp + số đo trễ thực tế của chuỗi thị giác → vi điều khiển.
- Bản vẽ CAD + BOM cho khung Delta hoàn chỉnh (để phát triển tiếp).
- Báo cáo + slide bảo vệ.

## 7. Kế hoạch theo tuần

| Tuần | Nội dung | Đầu ra | Trạng thái |
| --- | --- | --- | --- |
| 1–2 | Khảo sát tài liệu + chốt thông số hình học tham chiếu | `tong-quan.md`, bảng tham số | ✅ xong |
| 3–4 | Động học nghịch/thuận + kiểm chứng chéo | `mo-hinh/` + script + bảng sai số | |
| 5–6 | Quỹ đạo bậc 5 + PID trên MATLAB | `mo-phong/runs/` + KETQUA | |
| 7 | Dựng bàn thí nghiệm: webcam, hộp chụp, vật mẫu | ảnh mẫu + quy trình chụp | |
| 8 | Thị giác HSV + contour trên vật thật | ma trận nhầm lẫn + trễ xử lý | |
| 9 | Arduino: nhận góc khớp qua Serial, xuất PWM, đo trễ | `firmware/` + số đo trễ | |
| 10 | Ghép chu kỳ tổng, so với mốc 1,8 s | bảng phân rã chu kỳ | |
| 11 | CAD + BOM + phản biện | bản vẽ + `/phan-bien` đạt | |
| 12 | Báo cáo + slide | `bao-cao/` | |

## 8. Rủi ro và phương án dự phòng

| Rủi ro | Khả năng | Ảnh hưởng | Dự phòng |
| --- | --- | --- | --- |
| Ánh sáng thay đổi làm HSV sai, độ chính xác tụt | Cao | Mục tiêu 3 không đạt | Hộp chụp + đèn cố định; hiệu chỉnh ngưỡng theo từng buổi; ghi điều kiện chiếu sáng |
| Động học thuận Delta đa nghiệm, chọn sai nhánh | Cao | Sai số vòng kín lớn giả tạo | Ràng buộc nhánh (z < 0, khớp quay đúng chiều) + so với Newton–Raphson |
| Không mua được Arduino/webcam đúng hạn | Trung bình | Trễ tuần 7–9 | Dùng webcam laptop + mô phỏng Serial ảo; xin mượn phòng lab |
| Trễ Serial/PWM lớn hơn dự kiến | Trung bình | Chu kỳ vượt 1,8 s | Đo tách từng công đoạn, tối ưu gói tin; báo cáo trung thực thay vì che |
| Thời gian viết báo cáo bị ép | Trung bình | Chất lượng báo cáo | Ghi nhật ký hàng tuần, viết kết quả ngay sau mỗi mốc |

## 9. Tài liệu tham khảo

Xem `nghien-cuu/tai-lieu/references.bib` (8 mục, 7 DOI đã kiểm chứng Crossref;
`Clavel1988Delta` không có DOI — `[CẦN KIỂM CHỨNG]` từ kỷ yếu gốc).
