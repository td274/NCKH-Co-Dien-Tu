# Vo & Le (2023) — Thiết kế và phát triển hệ robot Delta phân loại vật bằng xử lý ảnh

**Loại tài liệu:** bài báo tạp chí (*IJECE*) — đã kiểm chứng DOI qua Crossref. **Tác giả Việt Nam.**

## Trích dẫn (IEEE)
[8] D. C. Vo and H. P. Le, "Design and development of a delta robot system to classify objects using image processing," *Int. J. Electr. Comput. Eng. (IJECE)*, vol. 13, no. 3, pp. 2669–2676, 2023, doi: 10.11591/ijece.v13i3.pp2669-2676.

## Bài toán
Robot Delta gắp vật trên băng tải và phân loại theo màu bằng camera trên băng tải.

## Phương pháp
- Ảnh BGR → chuyển sang **HSV**; áp ngưỡng (threshold) để nhận màu.
- Robot đặt vật theo kết quả nhận dạng.

## Phần cứng / thí nghiệm
Delta dẫn động bằng **3 servo DC**; Arduino điều khiển động cơ; **Raspberry Pi 4** xử lý ảnh; camera trên băng tải.

## Kết quả định lượng (theo abstract)
- Độ chính xác phân loại: **100 %** (đỏ, vàng); **97,5 %** (xanh lá).
- Thời gian phân loại trung bình: **1,8 s/vật**.
- `[CẦN KIỂM CHỨNG]` số lượng mẫu thử và điều kiện chiếu sáng — không có trong abstract.

## Hạn chế / giả thiết
Chỉ phân loại 3 màu; không có học sâu (đúng phạm vi đề tài); thời gian 1,8 s vượt chỉ tiêu chu kỳ ≤ 1,5 s của đề tài (dù tính chu kỳ khác nhau — cần định nghĩa rõ); cỡ mẫu chưa rõ.

## Liên quan đề tài
Đây là **tiền lệ trực tiếp nhất** cho mục tiêu 3 (camera ≥ 90 %) và mục tiêu 2 (chu kỳ). Đề tài có thể dùng cùng phương pháp HSV/ngưỡng và mở rộng: ≥ 100 mẫu, báo cáo ma trận nhầm lẫn, đo chu kỳ theo định nghĩa chuẩn.
