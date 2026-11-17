---
description: Nạp tài liệu do Gemini/AI khác tổng hợp vào repo, kiểm chứng DOI rồi mới ghi
agent: literature
subagent: true
---

Nạp tài liệu từ hộp thư: $ARGUMENTS

Mặc định đọc mọi file `.md` trong `nghien-cuu/tai-lieu/inbox/` (bỏ qua thư mục con).

Với **từng tài liệu** trong đó:

1. **Kiểm chứng trước, ghi sau.** Trích DOI, gọi `webfetch` tới
   `https://api.crossref.org/works/<DOI>`. So khớp 4 trường: tên bài, tác giả đầu,
   năm, venue. Lệch → đánh dấu `[SAI/NGHI VẤN]`, không đưa vào `references.bib`.
2. Không có DOI → tìm lại bằng Crossref `query.bibliographic` hoặc OpenAlex
   `search`. Không tìm ra → ghi `[CẦN KIỂM CHỨNG]`.
3. **Phát hiện bịa:** nếu DOI không tồn tại, hoặc tên bài không khớp, ghi rõ vào
   `nghien-cuu/tai-lieu/kiem-chung.md` mục "Tài liệu bị loại" kèm lý do. Tuyệt đối
   không âm thầm bỏ qua.
4. Tài liệu hợp lệ → tạo note `notes/<TacGia><Nam>-<slug>.md` theo cấu trúc chuẩn.
5. Cập nhật `bang-so-sanh.md` và `references.bib` (khoá `TacGiaNamTuKhoa`).
6. Chuyển file đã xử lý sang `inbox/da-xu-ly/` (giữ nguyên nội dung gốc để truy vết).

Cuối cùng trả về bảng:

| Tài liệu | DOI | Kết quả kiểm chứng | Đã ghi vào |
| --- | --- | --- | --- |

và tổng: bao nhiêu hợp lệ / bao nhiêu bị loại / bao nhiêu cần kiểm chứng tay.
