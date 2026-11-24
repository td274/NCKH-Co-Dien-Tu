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
| `nghien-cuu/cong-cu/` | Script tiện ích (kiểm tra hạn mức API, ...) | `nckh` |

## Môi trường máy (quan trọng — đừng đoán đường dẫn)

| Công cụ | Đường dẫn | Ghi chú |
| --- | --- | --- |
| Python 3.12.10 | `D:\Python312\python.exe` | `python` trần trên PATH là **stub Microsoft Store**, gọi vào sẽ báo lỗi. Luôn dùng đường dẫn đầy đủ. Đã cài: numpy, scipy, sympy, matplotlib, opencv-python (cv2), pyserial, pandas |
| MATLAB | `D:\matlb\bin\matlab.exe` | Gọi `& "D:\matlb\bin\matlab.exe" -batch "lệnh"` |
| Arduino IDE | `%LOCALAPPDATA%\Programs\Arduino IDE` | Nạp firmware; chưa có PlatformIO |
| Git | `%LOCALAPPDATA%\GitHubDesktop\app-3.6.4\resources\app\git\cmd\git.exe` | Git nhúng của GitHub Desktop |
| Repo | `D:\NCKH-Co-Dien-Tu` | Ổ C gần đầy, mọi dữ liệu lớn để ở D |

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
- `tong-hop` — tổng hợp notes thành tổng quan, xu hướng, khoảng trống (model mạnh)
- `co-khi` — thiết kế cơ khí: kích thước, dung sai, BOM, bản vẽ sơ đồ
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
| `/tong-hop` | Tổng hợp notes thành tổng quan + khoảng trống (Argon) |
| `/thiet-ke` | Thiết kế cơ khí + dung sai + BOM + bản vẽ |
| `/mo-hinh <hệ/ký hiệu>` | Dẫn giải mô hình toán |
| `/mo-phong <kịch bản>` | Viết và chạy mô phỏng |
| `/phan-bien <file/mục>` | Phản biện trước khi nộp |
| `/bao-cao <mục>` | Viết một mục báo cáo |
| `/nhat-ky <việc đã làm>` | Ghi nhật ký hôm nay |
| `/han-muc` | Kiểm tra hạn mức các API đã kết nối (Go, Mistral, Google) |
| `/nap-tai-lieu` | Nạp tài liệu từ `tai-lieu/inbox/` (Gemini web) + kiểm chứng DOI |

## Dùng model mạnh (Argon/Gemini) để tổng hợp tài liệu

Có 2 đường, chọn theo nhu cầu:

**A. Khép kín trong OpenCode (mặc định, khuyến nghị).** Argon đã có trong gói
`opencode-go` nên không cần API key:
1. `/khao-sat <chủ đề>` — agent `literature` (model rẻ) tìm bài qua OpenAlex/Crossref,
   kiểm chứng DOI, ghi note từng bài.
2. `/tong-hop` — agent `tong-hop` (**Argon**) đọc notes, viết `tai-lieu/tong-quan.md`:
   bản đồ phương pháp, xu hướng, mâu thuẫn, khoảng trống, hướng khả thi.

**B. Dùng Gemini web (AI Pro) khi cần model mạnh hơn hoặc hết hạn mức Go.**
1. Dán prompt trong `nghien-cuu/tai-lieu/inbox/PROMPT-GEMINI.md` vào Gemini web.
2. Lưu câu trả lời thành `nghien-cuu/tai-lieu/inbox/<ngày>-<chủ-đề>.md`.
3. Chạy `/nap-tai-lieu` — agent kiểm chứng từng DOI bằng Crossref rồi mới ghi vào repo.

**Không bao giờ** dán kết quả AI thẳng vào báo cáo: mọi trích dẫn phải qua Crossref.
Lưu ý: gói AI Pro **không kèm API key**; muốn gọi Gemini bằng API riêng phải tạo key ở
Google AI Studio (hạn mức miễn phí riêng, tính tiền riêng), rồi `/connect` provider Google.

## Ngân sách token (quan trọng với sinh viên)

- Việc nặng suy luận (mô hình, phản biện) dùng model mạnh; việc đọc/tóm tắt/format
  dùng model rẻ — đã cấu hình sẵn theo từng agent.
- Không chạy 5 subagent song song cho một việc nhỏ.
- Tóm tắt paper **một lần** rồi lưu file; đừng bắt agent đọc lại PDF gốc nhiều lần.

### Gói Go tính bằng tiền, không phải token

Hạn mức là một khoản **đô-la** dùng chung: 5 giờ = 20 %, tuần = 50 % (reset 07:00 thứ Hai),
tháng = 100 %. Mỗi model có hạn mức tháng riêng nhưng quy đổi theo *phần trăm*, nên đổi
model chỉ đổi tốc độ tiêu, không "thoát" hạn mức. Kiểm tra bằng `/han-muc`.

Chi phí thật bị chi phối bởi **token cache đọc** (mỗi lượt gửi lại toàn bộ ngữ cảnh), nên
model có cache đọc rẻ quan trọng hơn model có giá token thấp:

| Model | Hạn mức/tháng | Cache đọc $/1M | Token cache / 1 % hạn mức |
| --- | --- | --- | --- |
| `deepseek-v4.1-flash` | $100 | 0,003 | **333 M** |
| `glm-5.3-flash` | $60 | 0,03 | 20 M |
| `claude-haiku-5-5` | $15 | 0,01 | 15 M |
| `deepseek-v4-pro` | $15 | 0,022 | 7 M |
| `gemini-4-argon` | $30 | 0,10 | 3 M |
| `kimi-k2.7-code` | $60 | 0,19 | 3 M |
| `qwen3.8-max` | $15 | 0,25 | 1 M |

Phân công hiện tại (đã tối ưu, tiết kiệm ~68 % so với cấu hình đầu):

| Agent | Model | Lý do |
| --- | --- | --- |
| `simulation` | `deepseek-v4.1-flash` | chạy nhiều lượt → cache đọc rẻ nhất |
| `firmware` | `deepseek-v4.1-flash` | việc code, không cần model đắt |
| `reviewer` | `glm-5.3-flash` | cần phán đoán, hạn mức $60 |
| `modeling`, `tong-hop`, `co-khi` | `gemini-4-argon` | phần khó nhất, giữ chất lượng |
| `literature`, `writer` | `claude-haiku-5-5` | đọc/tóm tắt/format |
| `nckh` | `deepseek-v4-pro` | điều phối, ngữ cảnh ngắn |

Quy tắc vận hành để không đốt hạn mức:

- Phiên quá ~50 lượt thì mở phiên mới; ghi kết quả ra file, phiên sau đọc file tóm tắt.
- Không `read` nguyên file lớn (`dong-hoc-delta.md` 56 KB, `tong-quan.md` 45 KB,
  `sai-so-ik-fk.csv` 682 KB) — dùng `grep`, `offset`/`limit`, hoặc in 10 dòng cuối.
- Đừng dán log dài vào ngữ cảnh.
- Việc nặng nên chạy ngay sau khi tháng reset, không chạy sát trần hạn mức.
