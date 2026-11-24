# Chương 6. Kết luận và hướng phát triển

## 6.1 Đối chiếu với mục tiêu

Đề cương đặt ba mục tiêu đo được (`nghien-cuu/de-tai.md` mục 3). Bảng 6.1 đối chiếu từng mục tiêu với kết quả ở chương 5.

**Bảng 6.1.** Đối chiếu mục tiêu của đề cương với kết quả

| Mục tiêu | Chỉ tiêu trong đề cương | Kết quả | Trạng thái |
| --- | --- | --- | --- |
| 1. Động học và độ nhạy | Sai số vòng kín IK↔FK ≤ 1 mm trên ≥ 1.000 điểm; khảo sát ±0,2 mm báo cáo max và P95 | 1.859 điểm; sai số cực đại 1,583 × 10⁻¹³ mm; ±0,2 mm cho P95 0,402 mm (4 khâu) và max 0,689 mm | **Đạt** theo định nghĩa đo của đề cương; ngân sách worst-case của phương án chọn (GT2) là 1,048 mm, vượt 1 mm |
| 2. Quỹ đạo, chu kỳ | Chu kỳ 3 đoạn 0,96 s; overshoot ≤ 5 %; chu kỳ toàn hệ thống ≤ 1,8 s | T = 0,32 s, 3T = 0,96 s; overshoot 0,134 % (PID) và 0 % (PID+FF); tổng danh định 1,506 s | **Đạt trong mô phỏng**; chưa xác nhận trên phần cứng (trễ Serial và servo chưa đo) |
| 3. Phân loại trên vật thật | ≥ 90 % trên ≥ 120 vật thật, có ma trận nhầm lẫn, đo trễ xử lý ảnh | 97,33 % trên 75 vật tổng hợp (seed 999); 0 vật thật; trễ xử lý 3,41 ms trung bình | **Chưa đạt** (chưa có vật thật) |

*Nguồn: các bảng 5.1–5.8 và các file kết quả tương ứng.*

Đề tài đạt mục tiêu 1 và đạt mục tiêu 2 trong phạm vi mô phỏng. Mục tiêu 3 chưa đạt, vì mọi số phân loại đo trên ảnh tổng hợp và chưa có vật thật. Không thể viết rằng đề tài đạt cả ba mục tiêu.

Với mục tiêu 1, con số 1,583 × 10⁻¹³ mm chứng minh cặp IK và FK nhất quán về toán học, không phải độ chính xác của robot. Độ chính xác vật lý chỉ được ước lượng qua khảo sát dung sai. Theo khảo sát này, chỉ tiêu 1 mm đạt theo thống kê nhưng không đạt theo worst-case.

Với mục tiêu 2, chu kỳ 1,506 s là tổng danh định. Thành phần truyền Serial là dry-run. Cần phân biệt hai cấu hình: thiết kế dùng **stepper vòng kín + đai GT2**, sai lệch vị trí là sai số bám (đã nằm trong ngân sách 0,612 mm) chứ không phải trễ cộng thêm; còn **mô hình HIL dùng servo hobby** có thời gian quay 110° khoảng 0,18–0,37 s, nếu lấy cấu hình đó làm chu kỳ thì tổng thành 1,69–1,88 s. Vì vậy HIL dùng để đo trễ truyền thông, không dùng để đánh giá chu kỳ của thiết kế.

## 6.2 Đóng góp của đề tài

Đề tài có ba đóng góp trong phạm vi đã thực hiện.

1. **Kiểm chứng chéo IK↔FK định lượng trên toàn vùng làm việc.** Lưới 1.859 điểm trong hình trụ Ø300 × 150 mm cho 0 điểm Newton–Raphson không hội tụ, κ(Ĵ) ≤ 1,981 và góc truyền lực nhỏ nhất 39,00°. Các bài đã đọc ở chương 2 chưa báo cáo kiểm chứng này.
2. **Chỉ tiêu dung sai suy từ độ nhạy.** Monte Carlo cho P95 và max theo hai cấp dung sai. Cận trên giải tích 1,123 mm (4 khâu, ±0,2 mm) và 0,780 mm (dung sai phân cấp) được đặt cạnh nhau. Kết quả cho thấy chỉ tiêu 1 mm đạt theo thống kê và không đạt theo worst-case.
3. **Pipeline mô phỏng tái lập được, cùng một metric đo sai đã được phát hiện và sửa.** Mỗi lần chạy có cấu hình, dữ liệu thô và script sinh hình. Metric overshoot cũ báo 4,35 %, vì cửa sổ đo vượt sang đoạn kế tiếp. Metric đã sửa cho 0,134 % với PID thuần và 0 % với PID+FF. Phát hiện này cho thấy cần định nghĩa đo trước khi đọc số liệu.

## 6.3 Hạn chế

Ba hạn chế quyết định phạm vi kết luận.

- **Chưa có vật thật.** Mục 5.5 đo trên ảnh do nhóm tự sinh. Tập test có 75 vật, nên khoảng tin cậy 95 % là 90,8–99,3 %.
- **Chưa có trễ đo trên phần cứng.** Chu kỳ là giá trị danh định, và ngân sách 1,8 s chưa được kiểm chứng ở cấp hệ thống.
- **Mô phỏng còn đơn giản.** Mô hình khớp bỏ trọng lực và tương tác giữa các khớp. Hệ số J = 0,01 kg·m² là giả định.

## 6.4 Hướng phát triển

Các việc tiếp theo được sắp theo mức ảnh hưởng đến kết luận.

1. **Chụp ≥ 120 vật thật** (3 màu × 3 hình) trong hộp chụp cố định, lập ma trận nhầm lẫn và độ chính xác. Đây là điều kiện để đạt mục tiêu 3. Nếu sửa pipeline sau khi thấy kết quả, phải đánh giá trên seed mới, không dùng lại seed 999.
2. **Đo trễ Serial thật** bằng `do-tre-serial.py` với ít nhất 500 mẫu, và đo thời gian bám của stepper vòng kín (và trễ servo nếu triển khai cấu hình HIL). Sau đó cập nhật Bảng 5.6.
3. **Đo độ giãn đai GT2.** Giá trị 0,100 mm hiện là giả thiết và là thành phần lớn nhất của ngân sách sau hiệu chuẩn.
4. **Hiệu chuẩn gốc bằng 9 điểm** để kiểm chứng lệch gốc 0,03° và sai số 0,105 mm.
5. **Thêm trọng lực và ma sát** vào mô phỏng, rồi đối chiếu J = 0,01 kg·m² với ước tính 0,0066–0,0075 kg·m².
6. **Quét T mịn** với bước 0,005 s quanh 0,22–0,24 s, để chốt biên ω_max = 10 rad/s.
7. **Cải thiện phân loại hình dạng** cho lỗi tròn → vuông, bằng Hu moments hoặc template matching. Đánh giá trên seed mới theo nguyên tắc ở mục 1.

Đề tài sẽ đạt mục tiêu 3 khi có ≥ 120 vật thật và độ chính xác ≥ 90 % trên tập đó. Cho đến khi có dữ liệu này, mọi kết luận về phân loại chỉ áp dụng cho ảnh tổng hợp.
