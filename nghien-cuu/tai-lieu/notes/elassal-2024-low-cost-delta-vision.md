# Elassal, Abdelaal, Osama & Elhnidy (2024) — Low-cost parallel delta robot for pick-and-place with vision

**Loại tài liệu:** bài báo tạp chí (*e-Prime – Advances in Electrical Engineering, Electronics and Energy*) — đã kiểm chứng DOI qua Crossref (vol. 8, art. 100518).

## Trích dẫn (IEEE)
[6] A. Elassal, M. Abdelaal, M. Osama, and H. Elhnidy, "Low-cost parallel delta robot for a pick-and-place application with the support of the vision system," *e-Prime*, vol. 8, Art. no. 100518, 2024, doi: 10.1016/j.prime.2024.100518.

## Bài toán
Robot Delta giá rẻ gắp–đặt sản phẩm trên băng tải, có hệ thống thị giác.

## Phương pháp
- Thị giác: nhận dạng theo **dải màu**, bao contour (bounding box), gửi tọa độ thực về vi điều khiển.
- Điều khiển: Raspberry Pi (xử lý ảnh) + Arduino (động học nghịch, điều khiển động cơ).

## Phần cứng / thí nghiệm
Raspberry Pi (master), Arduino (slave), động cơ và cơ cấu hút chân không (abstract mô tả "hydraulic system" với cốc hút — `[CẦN KIỂM CHỨNG]` vì cách diễn đạt chưa rõ).

## Kết quả định lượng
Abstract: "proved the effectiveness and accuracy" nhưng **không có con số**. `[CẦN KIỂM CHỨNG]` qua toàn văn.

## Hạn chế / giả thiết
Chưa rõ số mẫu thử, chu kỳ gắp và sai số; phần cơ khí/điện mô tả chưa đủ chi tiết.

## Liên quan đề tài
Rất gần với đề tài: cùng kiến trúc "nhận dạng màu/contour + động học nghịch + gắp–đặt". Đề tài khác ở chỗ là **mô phỏng trước**, với chỉ tiêu định lượng (chu kỳ ≤ 1,5 s, độ chính xác ≥ 90 %).
