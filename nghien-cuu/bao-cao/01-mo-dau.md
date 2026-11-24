# Chương 1. Mở đầu

> Bản nháp do AI soạn từ dữ liệu trong repo. Sinh viên phải kiểm chứng số liệu và trích dẫn trước khi nộp.

## 1.1 Đặt vấn đề

Trong dây chuyền thực phẩm, linh kiện điện tử và bao bì, sản phẩm phải được phân loại theo màu sắc hoặc hình dạng trước khi đóng gói. Phân loại thủ công chậm và dễ sai khi băng tải chạy nhanh. Kết hợp camera với cơ cấu gắp cho phép tự động hóa khâu gắp–phân loại.

Robot song song kiểu Delta (Delta parallel robot) là lựa chọn phổ biến cho bài toán gắp–đặt. Bài báo gốc về robot Delta nhấn mạnh tốc độ cao nhờ hình học song song [1]. Cơ cấu gồm ba chuỗi động học song song. Các khớp quay chủ động đặt trên đế cố định, còn bàn công tác chuyển động tịnh tiến theo ba trục x, y, z [1]. Lập luận về độ cứng kết cấu của cơ cấu song song so với cơ cấu nối tiếp cần nguồn định lượng: [CẦN BỔ SUNG: nguồn so sánh độ cứng kết cấu robot song song và nối tiếp].

Tiền lệ gần nhất là hệ Delta phân loại vật theo màu bằng xử lý ảnh trong không gian HSV. Vo và Le (2023) báo cáo thời gian phân loại trung bình 1,8 s/vật [2]. Con số này là mốc đối chiếu thực nghiệm của đề tài.

Chế tạo robot Delta hoàn chỉnh tốn kém. Sinh viên thường mô phỏng động học mà chưa đo trễ thực của chuỗi camera đến vi điều khiển. Khi lắp thật, chu kỳ có thể vượt xa thiết kế. Đề tài hướng tới thu hẹp khoảng cách giữa mô phỏng và phần cứng trước khi đầu tư cơ khí.

Đề tài được thực hiện tại Khoa Cơ điện tử, Trường Đại học Điện lực, trong 12 tuần. Phạm vi được chọn để phù hợp năng lực sinh viên năm 2: không dùng học sâu, không gia công cơ khí chính xác.

## 1.2 Mục tiêu

Mục tiêu tổng quát là xây dựng mô hình toán, mô phỏng và một nguyên mẫu thí nghiệm một phần cho bài toán phân loại sản phẩm bằng camera. Nguyên mẫu gồm webcam và Arduino, chưa có khung cơ khí Delta. Kết quả làm cơ sở cho thiết kế phần cứng hoàn chỉnh.

Đề tài đặt ba mục tiêu đo được:

1. Dẫn giải và kiểm chứng chéo động học nghịch (inverse kinematics — IK) và động học thuận (forward kinematics — FK) của robot Delta ba bậc tự do. Sai số vòng kín cực đại không vượt 1 mm trên không gian làm việc tham chiếu Ø300 × 150 mm.
2. Thiết kế quỹ đạo gắp–thả bậc 5 kết hợp bộ điều khiển tỉ lệ–tích phân–vi phân (PID) và bù tiến (feed-forward). Chu kỳ chuyển động 3 đoạn 0,96 s (T = 0,32 s) cộng hai pha dừng 0,25 s, độ vọt lố (overshoot) không vượt 5 %. Chu kỳ toàn hệ thống không vượt 1,8 s khi cộng trễ thực đo được.
3. Xây dựng module phân loại trên vật thật bằng webcam. Độ chính xác đạt ít nhất 90 % trên ít nhất 120 vật mẫu gồm 3 màu và 3 hình dạng. Kết quả có ma trận nhầm lẫn và trễ xử lý ảnh đo thực tế.

## 1.3 Câu hỏi nghiên cứu

Đề tài trả lời hai câu hỏi:

- **Câu hỏi 1:** Mô hình động học thuận và nghịch của robot Delta ba bậc tự do đạt sai số nào khi kiểm chứng chéo trên toàn vùng làm việc?
- **Câu hỏi 2:** Trễ thực tế của chuỗi camera → OpenCV → Arduino chiếm bao nhiêu trong chu kỳ phân loại? Chu kỳ tổng có đạt mốc 1,8 s/vật đã công bố không?

## 1.4 Đối tượng, phạm vi và giới hạn

**Đối tượng nghiên cứu** là robot Delta ba bậc tự do tịnh tiến x–y–z, không có bậc quay đầu gắp. Hệ thống thị giác dùng webcam USB đặt cố định trên cao. Vật mẫu gồm 3 màu và 3 hình dạng (tròn, vuông, tam giác).

**Phạm vi** theo phương án 3 của đề cương: mô phỏng kết hợp thí nghiệm phần cứng một phần (hardware-in-the-loop thu nhỏ). Các nội dung cụ thể gồm:

- Động học là trọng tâm. Động lực học chỉ xét ở mức cơ bản.
- Điều khiển dừng ở PID. Không dùng ADRC hay LADRC.
- Nhận dạng màu và hình bằng ngưỡng HSV và contour trong OpenCV. Không dùng học sâu.
- Arduino Uno nhận góc khớp qua cổng Serial và xuất PWM. Chi phí phần cứng dự kiến dưới 500.000 VNĐ.

**Giới hạn** gồm các nội dung không thực hiện:

- Không dựng khung cơ khí Delta hoàn chỉnh. Phần cơ khí dừng ở bản vẽ CAD và danh mục linh kiện (BOM).
- Không gia công cơ khí chính xác.
- Không hiệu chuẩn động học trên robot thật.
- Không điều khiển bám quỹ đạo tốc độ cao.

**Tình trạng thực hiện tại thời điểm báo cáo.** Nhóm chưa hoàn thành hai hạng mục phụ thuộc
phần cứng vì hạn chế ngân sách, không phải vì thiếu phương pháp. Cụ thể:

- **Đã hoàn thành:** động học và kiểm chứng chéo IK↔FK trên 1.859 điểm; khảo sát độ nhạy
  dung sai bằng Monte Carlo; mô phỏng quỹ đạo bậc 5 với PID và bù tiến; phần mềm điều khiển
  nhúng (biên dịch đạt, chưa nạp bo mạch); pipeline thị giác HSV trên ảnh tổng hợp; bản vẽ
  chế tạo 2D và danh mục vật tư.
- **Chưa thực hiện:** đo trễ truyền thông Serial trên phần cứng thật (hiện chỉ có dry-run);
  thu và phân loại ≥ 120 vật mẫu thật; hiệu chuẩn động học trên khung thật.
- **Thay thế tạm thời:** bản vẽ chế tạo 2D kèm dung sai và BOM thay cho mô hình CAD 3D.
  Bản vẽ này đủ để đặt gia công và lắp ráp; mô hình 3D là bước bổ sung, không làm thay đổi
  kết luận của báo cáo.

Giả thiết tách khớp (decoupled joints) được áp dụng khi dùng PID đơn biến cho từng khớp. Giả thiết này làm bỏ qua tương tác động lực học giữa các nhánh song song. Báo cáo nêu rõ giả thiết này khi kết luận.

## 1.5 Đóng góp dự kiến

Đề tài dự kiến có ba đóng góp:

1. **Kiểm chứng chéo định lượng IK↔FK trên toàn vùng làm việc.** Nghiệm IK giải tích được đối chiếu với FK bằng phương pháp Newton–Raphson trên lưới điểm dày trong Ø300 × 150 mm. Báo cáo sai số cực đại và sai số căn quân phương (root mean square error — RMSE).
2. **Chỉ tiêu dung sai chế tạo suy ra từ mô phỏng độ nhạy.** Chiều dài khâu được cộng sai lệch ±0,2 mm. Báo cáo phân bố sai số điểm cuối gồm giá trị cực đại và phân vị 95 %, đối chiếu với ngưỡng 1 mm. Từ đó đề xuất dung sai chế tạo cho khâu.
3. **Pipeline mô phỏng đầu–cuối tái lập được.** Pipeline nối đầu ra tọa độ và nhãn của OpenCV với quy hoạch quỹ đạo, IK và điều khiển khớp. Mỗi lần chạy lưu tham số, phiên bản thư viện và seed để chạy lại được.

## 1.6 Bố cục báo cáo

Chương 2 tổng quan 8 công trình liên quan theo ba nhóm phương pháp. Chương 2 cũng nêu bốn khoảng trống dẫn đến đề tài. Chương 3 trình bày mô hình động học, giả thiết và thuật toán. Chương 4 mô tả thiết kế phần cứng, firmware và cấu hình mô phỏng. Chương 5 trình bày kết quả và thảo luận so với chỉ tiêu đề cương và tiền lệ. Chương 6 nêu kết luận và hướng phát triển. Danh mục tài liệu tham khảo theo chuẩn IEEE đặt cuối Chương 2 và đánh số thống nhất cho toàn báo cáo.
