# GHICHU — khác biệt giữa mô phỏng và phần cứng thật

Mục đích: khi ghép trễ đo được vào chu kỳ điều khiển tổng (Phương án 3), phải phân
biệt rõ các thành phần trễ — mô hình mô phỏng thường bỏ qua chúng.

## 1. Trễ truyền Serial (đo bằng script này)

- Ở **115200 baud**, 1 byte ≈ 87 µs. Lệnh `J,0.0,0.0,0.0\n` ≈ 14 byte → ~1.2 ms
  chỉ riêng thời gian truyền đi; trả lời `A,12345678\n` ≈ 11 byte → ~1.0 ms về.
- Cộng trễ xử lý + trễ đệm USB-serial (CH340/FTDI): tổng **vòng ~1–3 ms** là hợp lý.
- Trễ này **biến động** (do OS scheduling, đệm), nên báo P95/P99 chứ không chỉ mean.
- Nếu mô phỏng giả định "truyền tức thời", cần cộng thêm ~1–3 ms mỗi vòng.

## 2. Trễ cơ khí servo (KHÔNG nằm trong `A,<micros>`)

- `A,<micros>` là lúc nhận xong lệnh; **servo chưa tới vị trí**.
- Servo hobby điển hình: tốc độ ~0.10–0.20 s/60° → **100–200 ms** để quét hành trình.
- Đây là trễ lớn nhất hệ; mô phỏng động học phải có khâu bậc nhất/quán tính servo.
- Cần đo riêng: phát lệnh bước rồi quan sát (camera/encoder) thời gian tới góc.

## 3. Lượng tử hoá góc & xung

- Servo library xuất xung rời rạc (độ phân giải ~0.5–1 µs tuỳ timer AVR), ứng với
  ~0.03–0.06° cho xung 500–2500 µs. Mô phỏng dùng float liên tục → sai lệch nhỏ.
- Bản thân servo có **deadband** (vùng chết) vài µs: lệnh quá nhỏ sẽ không dịch.
- Không có phản hồi vị trí: `currentDeg` trong firmware là **vị trí đặt**, không phải
  vị trí thực. Mô phỏng có "đo vị trí" là lý tưởng hoá.

## 4. Tần số cập nhật thực tế

- Servo refresh 50 Hz (20 ms/khung) do phần cứng. Dù gửi lệnh nhanh hơn, servo chỉ
  cập nhật mỗi 20 ms → **chu kỳ điều khiển hiệu quả ≤ 50 Hz**.
- Vòng `loop()` không delay, chạy rất nhanh (~µs), nhưng bị chặn bởi tốc độ Serial
  và cơ chế 50 Hz của servo.

## 5. Nguồn & nhiễu (chỉ có trên thật)

- Servo kéo dòng xung (hàng trăm mA–A): nguồn chung với UNO dễ sụt áp → brown-out
  reset. Mô phỏng không mô tả.
- Điện áp thấp làm servo giật, chậm, hoặc mất xung.
- Dây tín hiệu dài gần dây động cơ → nhiễu, sai lệch xung.

## Tóm tắt để ghép chu kỳ tổng

| Thành phần trễ | Độ lớn điển hình | Có trong mô phỏng? |
| --- | --- | --- |
| Truyền + xử lý Serial (vòng) | 1–3 ms | thường bỏ qua |
| Cơ khí servo (quét góc) | 100–200 ms | thường bỏ qua / khâu lý tưởng |
| Lượng tử hoá xung + deadband | < 0.1° | bỏ qua |
| Chu kỳ refresh servo | 20 ms (50 Hz) | thường bỏ qua |

→ Khi đối chiếu mô phỏng với thực nghiệm, phải thêm khâu trễ vận tải + quán tính
servo, và chỉ so sánh khi đã đồng bộ chu kỳ lấy mẫu.
