# NCKH Cơ điện tử — quy ước dự án

Repo này là không gian làm **nghiên cứu khoa học (NCKH) ngành cơ điện tử**, dùng cho
sinh viên năm 2 (Trường Đại học Điện lực) và mọi đề tài sau này: cánh tay robot,
điều khiển động cơ, hệ thống nhúng, đo lường — tự động hoá, robot di động, v.v.

## Cấu trúc thư mục

| Thư mục | Nội dung | Ai ghi |
| --- | --- | --- |
| `nghien-cuu/de-tai.md` | Đề cương: vấn đề, mục tiêu, phương pháp, kế hoạch | `nckh` |
| `nghien-cuu/tai-lieu/` | Ghi chú đọc paper, `references.bib`, bảng so sánh | `literature` |
| `nghien-cuu/tai-lieu/inbox/` | Kết quả tổng hợp từ Gemini web — **phải kiểm chứng DOI** trước khi dùng | người dùng dán vào |
| `nghien-cuu/mo-hinh/` | Dẫn giải toán, động học/động lực học, hàm truyền, bộ điều khiển | `modeling` |
| `nghien-cuu/mo-phong/` | Script mô phỏng, cấu hình, kết quả từng lần chạy | `simulation` |
| `nghien-cuu/firmware/` | Code nhúng (Arduino/ESP32/STM32), PlatformIO | `firmware` |
| `nghien-cuu/du-lieu/` | Dữ liệu đo thực nghiệm (CSV), calibration | `simulation` |
| `nghien-cuu/bao-cao/` | Báo cáo, slide, hình vẽ xuất bản | `writer` |
| `nghien-cuu/nhat-ky/` | Nhật ký theo ngày `YYYY-MM-DD.md` | `nckh` |

## Quy tắc bắt buộc

1. **Không bịa tài liệu.** Mọi trích dẫn phải có DOI hoặc URL kiểm chứng được; tra
   Crossref trước khi đưa vào `references.bib` (xem skill `trich-dan-ieee`).
   Không chắc thì ghi `[CẦN KIỂM CHỨNG]` thay vì bịa.
2. **Ghi nhật ký mỗi phiên làm việc**: đã làm gì, kết quả, việc tiếp theo, lỗi gặp phải.
3. **Tái lập được**: mỗi lần mô phỏng lưu `config.json` (tham số, phiên bản thư viện,
   seed) và dữ liệu thô. Hình trong báo cáo phải sinh lại được từ script.
4. **Đơn vị SI** trong mọi công thức và bảng; ghi rõ đơn vị ở tiêu đề cột.
5. **Tiếng Việt** là ngôn ngữ làm việc và viết báo cáo; thuật ngữ chuyên ngành giữ
   tiếng Anh trong ngoặc khi cần (ví dụ: *động học nghịch (inverse kinematics)*).
6. **Không tự ý sửa** kết quả cũ trong `du-lieu/` hay `mo-phong/runs/`; muốn làm lại
   thì tạo lần chạy mới.
7. Kết quả do AI tạo ra là **bản nháp**: sinh viên phải tự kiểm chứng công thức, số liệu
   và kết luận trước khi đưa vào báo cáo nộp.

## Cách điều phối

Agent chính là `nckh`. Nó **không tự làm hết** mà giao việc cho subagent chuyên trách,
rồi tổng hợp:

- `literature` — tìm & tóm tắt paper, lập bảng so sánh, quản lý `references.bib`
- `modeling` — dẫn giải toán, thiết kế bộ điều khiển
- `simulation` — viết/chạy mô phỏng, xử lý số liệu, vẽ đồ thị
- `firmware` — code nhúng và build
- `reviewer` — phản biện, soi lỗi logic, citation ảo, tính tái lập
- `writer` — viết báo cáo/slide theo văn phong khoa học

Quy tắc chuyển giao: mỗi subagent **ghi kết quả ra file** trong thư mục của mình và
trả về một bản tóm tắt ngắn. Agent sau đọc file, không cần đọc lại toàn bộ ngữ cảnh —
đây là cách tiết kiệm token quan trọng nhất.

## Lệnh nhanh

| Lệnh | Việc |
| --- | --- |
| `/de-cuong <chủ đề>` | Lập đề cương NCKH |
| `/khao-sat <chủ đề>` | Khảo sát tài liệu, lập bảng so sánh |
| `/mo-hinh <hệ/ký hiệu>` | Dẫn giải mô hình toán |
| `/mo-phong <kịch bản>` | Viết và chạy mô phỏng |
| `/phan-bien <file/mục>` | Phản biện trước khi nộp |
| `/bao-cao <mục>` | Viết một mục báo cáo |
| `/nhat-ky <việc đã làm>` | Ghi nhật ký hôm nay |
| `/nap-tai-lieu` | Nạp tài liệu từ `tai-lieu/inbox/` (Gemini web) + kiểm chứng DOI |

## Phối hợp với Gemini web (Google AI Pro)

Tài khoản Google AI Pro dùng Argon/Hydrogen **trên web Gemini**, không tự động nối vào
repo. Quy trình phối hợp:

1. Dán prompt trong `nghien-cuu/tai-lieu/inbox/PROMPT-GEMINI.md` vào Gemini web.
2. Lưu câu trả lời thành `nghien-cuu/tai-lieu/inbox/<ngày>-<chủ-đề>.md`.
3. Chạy `/nap-tai-lieu` — agent kiểm chứng từng DOI bằng Crossref rồi mới ghi vào repo.

Không bao giờ dán kết quả AI thẳng vào báo cáo: mọi trích dẫn phải qua bước kiểm chứng.
Lưu ý: gói AI Pro **không kèm API key**; muốn OpenCode gọi Gemini trực tiếp thì phải tạo
API key riêng ở Google AI Studio (có hạn mức miễn phí, tính tiền riêng).

## Ngân sách token (quan trọng với sinh viên)

- Việc nặng suy luận (mô hình, phản biện) dùng model mạnh; việc đọc/tóm tắt/format
  dùng model rẻ — đã cấu hình sẵn theo từng agent.
- Không chạy 5 subagent song song cho một việc nhỏ.
- Tóm tắt paper **một lần** rồi lưu file; đừng bắt agent đọc lại PDF gốc nhiều lần.
- Muốn giảm chi phí: đổi `model` của `modeling` trong `.opencode/agents/modeling.md`
  từ `gemini-4-argon` sang `qwen3.8-max` hoặc `deepseek-v4-pro`.
