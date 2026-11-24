# Kiểm tra hạn mức (quota) API

Mỗi nhà cung cấp tính hạn mức một kiểu, nên không có một con số chung. Ghi lại đây để
không phải mò lại.

| Nhà cung cấp | Tính bằng | Xem ở đâu | Đọc được bằng API? |
| --- | --- | --- | --- |
| OpenCode Go | **tiền** (không phải token) | console + endpoint `/usage` | **Có** |
| Mistral | request/phút, token/phút | console + header phản hồi | Một phần |
| Google Gemini | request/ngày, token/phút | AI Studio | Không (chỉ biết qua lỗi 429) |

## Cách nhanh nhất

```powershell
D:\Python312\python.exe nghien-cuu\cong-cu\kiem-tra-han-muc.py
```

Hoặc gõ `/han-muc` trong OpenCode.

Tùy chọn:

| Tham số | Việc |
| --- | --- |
| `--chi-go` | chỉ kiểm tra OpenCode Go |
| `--json` | xuất JSON (để script khác đọc) |
| `--mistral-model <id>` | đo rate-limit bằng model khác (mặc định `mistral-small-2603`) |

Script đọc khóa trong cơ sở dữ liệu cục bộ của OpenCode
(`~/.local/share/opencode/opencode.db`), không in khóa ra màn hình.

## OpenCode Go

**Cách hiểu quan trọng:** gói Go có **một hạn mức chung tính bằng đô-la**, không phải
token. Mỗi model có một hạn mức tháng riêng, nhưng cách quy đổi là *phần trăm*:

> Tiêu $1,50 trên model có hạn mức $15 = dùng 10 % hạn mức tháng.

Nên đổi model không "thoát" được hạn mức — chỉ là đổi tốc độ tiêu.

Ba mốc:

| Mốc | Bằng | Reset |
| --- | --- | --- |
| 5 giờ | 20 % hạn mức tháng | trượt, tính từ lần dùng đầu |
| Tuần | 50 % hạn mức tháng | **07:00 thứ Hai** (00:00 UTC) |
| Tháng | 100 % | theo chu kỳ thanh toán |

Đọc trực tiếp:

```powershell
curl.exe https://opencode.ai/inference/go/v1/usage -H "Authorization: Bearer <khóa Go>"
```

Kết quả có `rolling` / `weekly` / `monthly`, mỗi mục gồm `status` (`ok` hoặc
`rate-limited`), `percent`, `resetsAt`.

Xem hạn mức **theo từng model** và giá token:

```powershell
curl.exe https://opencode.ai/inference/go/v1/models -H "Authorization: Bearer <khóa Go>"
```

Trong JSON: `go.monthly_usage.go` là hạn mức đô-la của model đó trong gói Go;
`cost.text.input.price` và `cost.text.output.price` là giá mỗi 1 triệu token.

Giao diện: <https://opencode.ai/console/go> — tab **Limits** có bảng hạn mức từng model
và ước lượng số request cho mỗi mốc.

## Mistral

Không có endpoint trả về "còn bao nhiêu hạn mức tháng". Chỉ đọc được **rate-limit tức
thời** qua header của mỗi phản hồi:

```
x-ratelimit-limit-tokens-minute
x-ratelimit-remaining-tokens-minute
x-ratelimit-limit-req-minute
x-ratelimit-remaining-req-minute
```

Rate-limit **khác nhau theo từng model** — đo bằng đúng model mình sẽ dùng, đừng lấy số
của model này suy ra model khác. Ví dụ đã đo trên khóa hiện tại:

| Model | Token/phút | Request/phút |
| --- | --- | --- |
| `mistral-small-2603` | 500.000 | 1.000 |
| `deepseek-v4-1-flash-1017` | 10.000.000 | 1.333 |
| `mistral-large-latest` | 15.000.000 | 2.000 |

Số dư và lịch sử chi tiêu: <https://console.mistral.ai/usage>.

Mistral là **tài khoản trả phí riêng**, không nằm trong $10 của gói Go.

## Google Gemini

Không có API đọc hạn mức. Cách duy nhất là gửi một request nhỏ:

- `200` → còn hạn mức
- `429` → hết hạn mức (free tier), phải chờ reset theo ngày

Script tự chọn một model text còn hiệu lực (bản `-latest` hoặc phiên bản cao nhất) rồi
thử 1 token. Đừng ghi cứng tên model: model cũ vẫn nằm trong danh sách nhưng đã bị gỡ
với người dùng mới, gọi vào sẽ trả 404.

Xem hạn mức và khóa: <https://aistudio.google.com/apikey>.

## Cái gì ăn hạn mức nhanh nhất

Theo số liệu thực tế của đề tài (đọc từ cơ sở dữ liệu OpenCode):

1. **Token cache đọc** — phiên càng dài, mỗi lượt agent gửi lại càng nhiều ngữ cảnh.
   Một agent mô phỏng đã tạo ra 26 triệu token cache đọc, chiếm phần lớn chi phí.
   Cách giảm: chia phiên ngắn, giao việc cho subagent (ngữ cảnh mới), lưu kết quả ra
   file thay vì đọc lại file lớn.
2. **Model đắt** — `gemini-4-argon` $2/$10 mỗi 1M token, `qwen3.8-max` $2/$6 nhưng hạn
   mức tháng chỉ $15, nên rất dễ chạm trần.
3. **Suy luận (reasoning)** — tính như token ra, có thể gấp nhiều lần token trả lời.

## Ghi chú

- Con số "token đã dùng" trong giao diện **không** phải hạn mức. Hạn mức Go là tiền.
- Khi bị chặn: chờ mốc reset, bật **Extra Usage** (trừ credit), hoặc dùng model miễn phí.
- Giá và hạn mức thay đổi theo thời gian — luôn lấy từ endpoint, đừng chép số cũ trong
  tài liệu này.
