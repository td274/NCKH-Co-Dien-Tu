# Hộp thư tài liệu

Nơi bạn dán kết quả tổng hợp từ **Gemini web**, ChatGPT, hoặc bất kỳ AI nào khác.
Agent `literature` sẽ đọc file ở đây, **kiểm chứng DOI qua Crossref**, rồi mới ghi vào
`references.bib`.

## Cách dùng (3 bước)

1. Copy prompt trong `PROMPT-GEMINI.md`, dán vào Gemini web kèm chủ đề của bạn.
2. Lưu câu trả lời vào một file mới: `inbox/<ngày>-<chủ-đề>.md`
   (ví dụ `2026-11-18-pid-dong-co-dc.md`).
3. Chạy `/nap-tai-lieu` — agent kiểm chứng và nạp vào repo.

Sau khi xử lý, file gốc được chuyển sang `inbox/da-xu-ly/`.

## Vì sao phải kiểm chứng

AI trên web hay tạo ra tài liệu **trông rất thật nhưng không tồn tại** (DOI sai, tác
giả đúng nhưng bài không có, số trang bịa). Nếu tin ngay, bạn sẽ nộp báo cáo có
citation ảo — lỗi nặng nhất trong NCKH. Bước kiểm chứng bằng Crossref là bắt buộc.

## Quy ước file

- Mỗi file một chủ đề, Markdown thuần.
- Không cần đúng định dạng BibTeX — cứ dán nguyên văn câu trả lời, agent tự chuẩn hoá.
- Nếu biết DOI thì càng tốt; không có DOI thì agent sẽ tự tra.
