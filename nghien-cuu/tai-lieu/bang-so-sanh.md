# Bảng so sánh tài liệu — Robot Delta phân loại bằng camera

Ngày cập nhật: 2026-11-18. Nguồn kiểm chứng: Crossref (DOI), OpenAlex (abstract). Chỉ tiêu theo đề cương: sai số ≤ 1 mm, chu kỳ ≤ 1,5 s, overshoot ≤ 5 %, độ chính xác phân loại ≥ 90 %.

## Bảng tổng hợp

| Tài liệu | Phương pháp | Phần cứng | Chỉ tiêu đo | Kết quả (theo abstract) | Hạn chế |
| --- | --- | --- | --- | --- | --- |
| Clavel 1988 [1] — *nền tảng* | Cấu trúc Delta song song 3 DOF | — (thiết kế gốc) | — | Chưa xác minh (không có DOI) | `[CẦN KIỂM CHỨNG]` nguồn gốc |
| Vischer & Clavel 1998 [2] — *nền tảng* | Hiệu chuẩn động học (sai số hình học) | Robot Delta thực | Sai số vị trí (chưa rõ) | Không có abstract | Cần toàn văn |
| Castañeda 2015 [3] | ADRC thích nghi đầu ra + LMS | Delta thực + mô phỏng | Bám quỹ đạo, so PID/ADRC | Tốt hơn PID (định tính); không có số | Điều khiển nâng cao; chưa rõ số |
| Liu 2020 [4] | LADRC giải ghép 3 khớp | Chỉ mô phỏng | Bám quỹ đạo số 8 | "quick and precise" (định tính) | Không có số; không có phần cứng |
| Yang & Xiao 2024 [5] | Động học thuận bằng số + Monte Carlo vùng làm việc | Mô hình 3 DOF; MATLAB | Vùng làm việc, tính duy nhất nghiệm | Định tính: mô hình hợp lý | Không có số sai số; không điều khiển |
| Elassal 2024 [6] | Nhận dạng màu + contour; IK trên Arduino | Raspberry Pi + Arduino; động cơ; hút chân không | Độ chính xác gắp (chưa rõ) | "effective and accurate" (chưa có số) | Thiếu số liệu; cần toàn văn |
| Phuong Hoai 2023 [7] | Thị giác 3D (tọa độ + kích thước) | Động cơ bước; Arduino Uno; in 3D | Sai số tọa độ (định tính) | "small error" (không có số) | Động cơ bước; chưa định lượng; cần kiểm chứng tác giả |
| Vo & Le 2023 [8] | Ngưỡng HSV, 3 màu | 3 servo DC; Arduino; Raspberry Pi 4; camera băng tải | Độ chính xác phân loại; thời gian/vật | 100 % (đỏ, vàng); 97,5 % (xanh); 1,8 s/vật | Chỉ 3 màu; cỡ mẫu chưa rõ; chu kỳ > 1,5 s |

## So sánh theo chỉ tiêu đề tài

| Chỉ tiêu | Tiền lệ gần nhất | Đề tài cần |
| --- | --- | --- |
| Sai số vị trí ≤ 1 mm | Chưa có số trong các bài đã đọc | Tự tạo bộ kiểm chứng (Python/sympy) |
| Chu kỳ ≤ 1,5 s | 1,8 s/vật [8] | Định nghĩa rõ chu kỳ, đo trong mô phỏng |
| Overshoot ≤ 5 % | Không có số | Đo từ đáp ứng bước |
| Phân loại ≥ 90 % (≥ 100 mẫu) | 97,5–100 % trên 3 màu [8] | Ma trận nhầm lẫn trên ≥ 100 vật |

## Khoảng trống nghiên cứu

- Các bài thực nghiệm (Elassal 2024 [6], Vo & Le 2023 [8], Phuong Hoai 2023 [7]) **không công bố sai số định lượng đầy đủ** (sai số vị trí, số mẫu, chu kỳ theo định nghĩa thống nhất); đề tài có thể đặt chỉ tiêu đo được và báo cáo ma trận nhầm lẫn.
- Phần lớn bài điều khiển Delta (Castañeda [3], Liu [4]) dùng ADRC/thích nghi phức tạp; **chưa thấy so sánh PID/feed-forward đơn giản trên cùng kịch bản pick-and-place** — đề tài có thể làm baseline này trong mô phỏng.
- Chưa tìm thấy bài nào kết nối **liền mạch** động học nghịch đã kiểm chứng với mô phỏng quỹ đạo gắp–thả và nhận dạng camera trong cùng một bộ chỉ tiêu; đây là đóng góp khả thi của đề tài.
- Động học thuận Delta (Yang [5]) mới chỉ có mô phỏng vùng làm việc; **chưa có kiểm chứng sai số giữa nghiệm thuận–nghịch** trong bài nào đã đọc — đề tài có thể thực hiện bước này bằng nghiệm số (Newton–Raphson) theo rủi ro đã nêu.
- Bối cảnh phân loại bằng HSV/ngưỡng (đúng phạm vi không học sâu) còn ít bài tiếng Việt có số liệu đầy đủ; tiềm năng đóng góp ở mức sinh viên.

## Ghi chú nguồn

- Không tìm được bài tiếng Việt trong Tạp chí Khoa học ĐH Điện lực qua `webfetch` trong lượt này; cần bổ sung nếu có thời gian.
- Các bài trong bảng đều là bài báo khoa học/hội nghị. Không có blog hay luận văn được dùng làm nền tảng học thuật.
- Mục `[CẦN KIỂM CHỨNG]`: Clavel 1988 (DOI), tác giả FME 2023, và số liệu toàn văn của các bài chỉ có abstract.
