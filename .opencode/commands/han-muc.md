---
description: Kiểm tra hạn mức (quota) của các API đã kết nối
agent: nckh
---

Chạy script kiểm tra hạn mức:

```
D:\Python312\python.exe nghien-cuu\cong-cu\kiem-tra-han-muc.py
```

Rồi báo lại cho người dùng, bằng tiếng Việt, theo đúng số liệu script in ra:

1. **OpenCode Go** — phần trăm của 3 mốc (5 giờ / tuần / tháng), mốc nào đang chặn, và
   giờ reset **đổi sang giờ Việt Nam**. Nhắc rằng Go tính bằng tiền chứ không phải token.
   Nếu tháng đã > 80 %, cảnh báo rằng mốc chặn thật sự là tháng.
2. **Mistral** — rate-limit token/phút và request/phút của model vừa đo (mặc định
   `mistral-small-2603`). Ghi rõ rate-limit khác nhau theo model.
3. **Google Gemini** — khóa còn dùng được không, model nào được chọn để thử, và kết quả
   200/429.

Quy tắc:
- Không tự đổi model của agent hay sửa cấu hình khi chưa hỏi.
- Nếu script báo lỗi mạng, chạy lại một lần; vẫn lỗi thì báo nguyên văn thông báo.
- Không in khóa API ra màn hình.
