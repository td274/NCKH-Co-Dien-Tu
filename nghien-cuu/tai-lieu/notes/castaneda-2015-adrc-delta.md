# Castañeda, Luviano-Juárez & Chairez (2015) — Robust trajectory tracking of a Delta robot through adaptive ADRC

**Loại tài liệu:** bài báo tạp chí (IEEE TCST) — đã kiểm chứng DOI qua Crossref.
**Lưu ý năm:** Crossref ghi 2015 (vol. 23, no. 4); OpenAlex hiển thị 2014 do ngày xuất bản online. Dùng 2015 theo số tạp chí.

## Trích dẫn (IEEE)
[3] L. A. Castañeda, A. Luviano-Juárez, and I. Chairez, "Robust trajectory tracking of a Delta robot through adaptive active disturbance rejection control," *IEEE Trans. Control Syst. Technol.*, vol. 23, no. 4, pp. 1387–1398, 2015, doi: 10.1109/TCST.2014.2367313.

## Bài toán
Bám quỹ đạo của Delta với mô hình động lực học không chắc chắn (uncertain dynamics).

## Phương pháp
- ADRC thích nghi đầu ra (output-based), không cần đo vận tốc khớp.
- Bộ quan sát–nhận dạng đồng thời; thành phần không chắc chắn xấp xỉ phi tham số bằng LMS thích nghi.

## Phần cứng / thí nghiệm
Thực nghiệm trên robot Delta thật (tên cụ thể của phần cứng và thông số không có trong abstract — `[CẦN KIỂM CHỨNG]` qua toàn văn). Có mô phỏng quỹ đạo nhanh gấp 5 lần.

## Kết quả định lượng
Theo abstract, tốt hơn PID có bù tiến và ADRC không thích nghi trong thực nghiệm; trên mô phỏng với quỹ đạo nhanh gấp 5 lần, bộ thích nghi vẫn tốt hơn PID. **Không có số liệu sai số cụ thể trong abstract** — không suy diễn con số.

## Hạn chế / giả thiết
Điều khiển nâng cao (ADRC thích nghi) có thể vượt phạm vi sinh viên năm 2; cần độ phức tạp tính toán và kiến thức điều khiển. Phụ thuộc mô hình tham chiếu.

## Liên quan đề tài
Tham chiếu cho bước 2 (điều khiển quỹ đạo). Đề tài có thể dùng PID/feed-forward làm baseline và so sánh với ADRC đơn giản hơn — đây là phương án dự phòng thực tế hơn.
