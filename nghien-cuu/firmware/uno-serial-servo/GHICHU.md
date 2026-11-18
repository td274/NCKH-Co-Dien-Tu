# GHICHU — khác biệt giữa mô hình mô phỏng và firmware thật

Phạm vi: firmware `uno-serial-servo` đo **trễ vòng (round-trip latency)** bằng cách
gửi `J,t1,t2,t3\n` rồi chờ dòng trả lời `A,<micros>\n`. Con số `<micros>` là
`micros()` của Arduino **tại thời điểm nhận đủ dòng lệnh**, KHÔNG phải thời điểm
servo chuyển động xong. Vì vậy có nhiều khâu trễ mà mô phỏng thường bỏ qua — ghi rõ
ở đây để khi so với `nghien-cuu/mo-phong/` không kết luận sai.

> Quy ước đánh dấu nguồn số: `[TÍNH]` = tự tính từ thông số; `[DATASHEET]` = lấy từ
> datasheet; `[ƯỚC LƯỢNG]` = chưa đo, cần đo thực nghiệm để chốt.

---

## 1. Ngân sách trễ vòng (bảng ước lượng)

| Khâu | Giá trị ước lượng | Nguồn |
| --- | --- | --- |
| Truyền lệnh `J,...\n` (17–20 byte) qua UART | 1.5–1.7 ms | `[TÍNH]` |
| Truyền đáp `A,<micros>\n` (8–13 byte) | 0.7–1.1 ms | `[TÍNH]` |
| Đệm + polling USB↔UART (chip CH340) | 1–4 ms | `[ƯỚC LƯỢNG]` |
| Lịch trình OS + driver serial Windows + Python `readline` | 1–15 ms (đuôi dài) | `[ƯỚC LƯỢNG]` |
| **Tổng trễ vòng đo bằng script** | **~3–20 ms, trung bình ~5 ms** | `[ƯỚC LƯỢNG]` |
| Trễ cơ khí servo (KHÔNG nằm trong phép đo trên) | 100–200 ms / 60° | `[DATASHEET]` |

Kết luận quan trọng: **trễ vòng Serial (vài ms) nhỏ hơn trễ cơ khí servo (trăm ms)
khoảng 1–2 bậc.** Trong mô phỏng điều khiển, khâu trễ đáng kể là servo, không phải
đường truyền.

---

## 2. Trễ Serial @ 115200 baud (cách tính)

UART 8N1 = 10 bit cho mỗi byte (1 start + 8 data + 1 stop):

```
t_byte = 10 bit / 115200 baud = 86.8 µs/byte
```

- Lệnh dài nhất `J,-30.0,-30.0,-30.0\n` = 20 byte → `20 × 86.8 µs ≈ 1.74 ms`.
- Đáp `A,<micros>\n`: `micros()` tối đa 10 chữ số → 13 byte → `≈ 1.13 ms`.

Tổng **thời gian trên dây UART ≈ 2.2–2.9 ms**. Nhưng phép đo thật qua USB–CH340
còn cộng thêm:

- **Đệm USB**: CH340 trao đổi theo gói bulk; driver gom byte rồi mới đẩy — thêm
  1–4 ms và gây jitter theo chu kỳ polling.
- **OS + Python**: Windows scheduler (time-slice ~1–15 ms), thư viện `pyserial`
  đọc qua lớp buffer. Đuôi phân bố (P99) thường vài chục ms do bị trễ lịch.

Mô phỏng thường mô hình trễ đường truyền là hằng số hoặc bằng 0 → thực tế là một
**phân bố** (mean ~5 ms, P99 có thể 15–30 ms). Dùng P95/P99 của script để so, không
dùng riêng mean.

---

## 3. Trễ cơ khí servo (100–200 ms)

Servo hobby thông dụng:

| Loại | Tốc độ | Nguồn |
| --- | --- | --- |
| SG90 (9g, nhựa) | 0.10–0.12 s/60° | `[DATASHEET]` |
| MG995 (kim loại) | 0.17–0.20 s/60° | `[DATASHEET]` |
| MG996R (kim loại) | 0.13–0.17 s/60° | `[DATASHEET]` |

→ Đổi góc 60° mất **100–200 ms**; đổi từ −30° lên +80° (110°) mất ~0.18–0.37 s.
Firmware trả `A,<micros>` **ngay khi nhận lệnh**, chưa chờ servo đạt vị trí, nên
trễ cơ khí này nằm NGOÀI phép đo Serial. Muốn so với mô phỏng động học phải cộng
thêm khâu này (mô phỏng nên có khối trễ/slew-rate cho servo).

Cách đo chốt số: gắn encoder (hoặc quay phim + chấm điểm) lên trục servo, đo thời
gian từ cạnh lên của lệnh `J` tới khi góc đạt 95 % giá trị đích.

---

## 4. Lượng tử hoá góc

`writeMicroseconds()` chỉ nhận số **nguyên µs**; dải 500–2500 µs = 2000 µs quét 180°:

```
1 µs  = 180° / 2000 = 0.09°   →  góc bị làm tròn tới bội của ~0.09°
```

Ngoài ra servo còn có **vùng chết (deadband)** ~5–8 µs ≈ 0.5–0.7°: lệnh thay đổi
nhỏ hơn deadband có thể không làm servo nhúc nhích. Mô phỏng dùng `float` liên tục
→ không có bước lượng tử này (sai khác < 0.1°, thường bỏ qua được trừ khi điều
khiển vị trí tinh).

---

## 5. Jitter của `micros()`

- Độ phân giải `micros()` trên ATmega328P @16 MHz là **4 µs** (Timer0 tick 64 µs,
  nội suy bằng TCNT0), nên giá trị nhảy theo bước 4 µs.
- Có sai số ±4 µs do đọc TCNT0 đúng lúc timer sắp tràn.
- Tràn (overflow) sau 2³² µs ≈ **71.6 phút**; nếu chạy lâu, cột `arduino_micros`
  trong CSV sẽ quấn về 0. Script đo trễ bằng `perf_counter_ns()` độc lập nên bản
  thân phép đo không bị ảnh hưởng.
- Thạch anh gốm của board clone sai tần ~±30 ppm → vài µs trôi mỗi giây (không đáng
  kể cho phép đo trễ ms).

---

## 6. Cảnh báo: servo rẻ giật khi đổi góc lớn

- Lệnh `J` trong firmware đặt `targetDeg = currentDeg = góc mới` rồi xuất xung **tức
  thì** (không ramp). Servo rẻ không có mạch giảm tốc độ bên trong sẽ **giật mạnh**,
  rung, có thể kéo sụt nguồn chung.
- Riêng lúc khởi động, firmware **có** quét từ từ về home (`HOME_STEP_DEG 1°` mỗi
  `20 ms` = 50°/s) → an toàn. Lệnh `J` thì không có bước ramp này.
- Khuyến nghị khi kiểm thử: gửi chuỗi góc trung gian, hoặc thêm ramp trong firmware;
  không nhảy −30°→+80° trong một lệnh.

Mô phỏng giả định servo đạt góc tức thời / lý tưởng → thực tế có quá độ (overshoot),
dao động và giật ở servo rẻ; chỉ nên so **trạng thái xác lập**, không so quá độ.

---

## 7. Danh sách cần đo thực nghiệm để đối chiếu mô phỏng

1. Phân bố trễ vòng thật (chạy `do-tre-serial.py --port COM<x> --n 500`) → lấy mean/P95/P99.
2. Trễ cơ khí từng servo (encoder/phim) → đưa vào mô phỏng làm khâu trễ/slew.
3. Đặc tuyến xung–góc thật từng servo (một số servo chỉ tuyến tính 1000–2000 µs).
4. Deadband thật (bước góc nhỏ nhất servo phản hồi).
5. Kiểm tra giật khi đổi góc lớn → quyết định có cần ramp trong lệnh `J` hay không.
