# uno-serial-servo — firmware đo trễ vòng Serial (Phương án 3)

Firmware Arduino UNO nhận góc 3 khớp qua Serial và trả `A,<micros>` ngay khi nhận
xong dòng lệnh, dùng để **đo trễ vòng (round-trip latency) thực tế** giữa máy tính
và vi điều khiển.

> ⚠️ **Số đo trễ chỉ có nghĩa khi cắm board thật.** Khi chưa cắm, dùng
> `--dry-run` để kiểm tra script (số liệu là giả lập).

---

## 1. Sơ đồ nối dây (bảng chân)

| Arduino UNO | Nối tới | Ghi chú |
| --- | --- | --- |
| GND | GND servo + GND nguồn | Mass chung bắt buộc |
| 5V | (không cấp cho servo tải nặng) | Servo nên dùng nguồn riêng 5–6 V |
| D9  | Tín hiệu servo 1 (khớp base) | `SERVO1_PIN` |
| D10 | Tín hiệu servo 2 (khớp vai) | `SERVO2_PIN` |
| D11 | Tín hiệu servo 3 (khớp khuỷu) | `SERVO3_PIN` |
| D2  | Công tắc dừng khẩn cấp (NC → GND) | `ESTOP_PIN`, active-LOW |

Thứ tự chân (D9/D10/D11 → khớp 1/2/3) là **giả định**, chốt lại theo cơ cấu thật.

**Xung servo:** khung 20 ms (50 Hz), xung 500–2500 µs. Trung tính 1500 µs = 0°.
Ánh xạ: `xung = 500 + (góc + 90)/180 × 2000` µs.

---

## 2. Giao thức Serial (115200, 8N1)

Mỗi lệnh một dòng, kết thúc `\n`:

| Gửi | Nhận | Ý nghĩa |
| --- | --- | --- |
| `J,<t1>,<t2>,<t3>` | `A,<micros>` | Đặt 3 góc khớp (độ, cho phép âm), trả lời ngay |
| `H` | `A,<micros>` | Về vị trí home |
| `P` | `P,<micros>` | Ping |
| `S` | `S,v=...,uptime_ms=...,a1=...` | Trạng thái |
| (lệnh lỗi) | `E,SYNTAX` / `E,UNKNOWN` / `E,ESTOP` | Báo lỗi |

`<micros>` là `micros()` của Arduino tại thời điểm **nhận đủ dòng** (không phải
thời điểm servo chuyển động xong). Trễ cơ khí servo tính riêng (xem GHICHU.md).

Giới hạn hành trình: mỗi khớp mặc định `[-30°, +80°]` (CLAMP trước khi xuất xung).

---

## 3. Cách nạp firmware (arduino-cli v1.5.1)

```powershell
$CLI = "C:\Users\Admin\AppData\Local\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"

# Biên dịch (đã xác nhận BUILD XANH):
& $CLI compile --fqbn arduino:avr:uno "D:\NCKH-Co-Dien-Tu\nghien-cuu\firmware\uno-serial-servo"

# Nạp khi cắm board (thay COM5 bằng cổng thật):
& $CLI upload -p COM5 --fqbn arduino:avr:uno "D:\NCKH-Co-Dien-Tu\nghien-cuu\firmware\uno-serial-servo"
```

Kết quả compile hiện tại: **7958 bytes (24%) flash, 386 bytes (18%) RAM** — thành công.

Nếu chưa có core (máy khác):
```powershell
& $CLI core install arduino:avr
```

---

## 4. Cách chạy đo trễ

```powershell
# Đo thật (cần cắm board):
D:\Python312\python.exe do-tre-serial.py --port COM5 --n 200

# Tự dò cổng (ưu tiên CH340):
D:\Python312\python.exe do-tre-serial.py --n 200

# Dry-run — KHÔNG cần board, chỉ kiểm tra script (số liệu GIẢ LẬP):
D:\Python312\python.exe do-tre-serial.py --dry-run --n 200
```

Kết quả ghi vào `ket-qua/`: CSV (`latency-<real|dryrun>-<ts>.csv`) và histogram
300 dpi (`histogram-*.png`). Báo cáo: trung bình, trung vị, P95, P99, max (ms).

---

## 5. Điểm cần chốt trên phần cứng thật

1. Ánh xạ chân → khớp (D9/D10/D11 hiện là giả định).
2. Cặp xung–góc thực của từng servo (một số servo chỉ tuyến tính 1000–2000 µs).
3. Giới hạn cơ khí `[-30°, +80°]` theo bản vẽ, tránh kẹt cơ khí.
4. Nguồn servo riêng; nếu nguồn chung với UNO dễ sụt áp → reset.
