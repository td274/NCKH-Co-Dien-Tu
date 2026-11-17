// ============================================================================
//  config.h — thông số phần cứng & giao thức cho firmware "uno-serial-servo"
// ----------------------------------------------------------------------------
//  Mọi hằng số đều ghi rõ nguồn:
//    [DATASHEET]  : lấy từ datasheet / tài liệu chính thức
//    [GIẢ ĐỊNH]   : chưa đo trên phần cứng thật — PHẢI chốt lại trước khi chạy
// ============================================================================
#pragma once

// ------------------------------ Phiên bản ----------------------------------
#define FIRMWARE_VERSION "1.0.0"

// ------------------------------ Giao thức -----------------------------------
// Mỗi lệnh một dòng, kết thúc bằng '\n' (LF). Baud 115200, 8N1.
//   J,<t1>,<t2>,<t3>  -> A,<micros>   (đặt 3 góc khớp, độ, cho phép âm)
//   H                 -> A,<micros>   (về vị trí home)
//   P                 -> P,<micros>   (ping)
//   S                 -> S,<trạng thái>
#define SERIAL_BAUD       115200UL
// [DATASHEET] CH340/ATmega16U2 hỗ trợ 115200 8N1; chọn 115200 để giảm trễ truyền
//   (mỗi byte ~87 µs). Giảm xuống 57600 nếu nhiễu gây lỗi khung.

// ------------------------------ Chân kết nối --------------------------------
// Arduino UNO R3 (ATmega328P). Ba chân PWM — thư viện Servo.h dùng Timer1 cho
// tất cả kênh nên các chân không xung đột timer.
#define SERVO1_PIN        9     // [GIẢ ĐỊNH] khớp 1 (base)  — nối dây tín hiệu servo 1
#define SERVO2_PIN        10    // [GIẢ ĐỊNH] khớp 2 (vai)   — nối dây tín hiệu servo 2
#define SERVO3_PIN        11    // [GIẢ ĐỊNH] khớp 3 (khuỷu) — nối dây tín hiệu servo 3

// Chân dừng khẩn cấp (tùy chọn). Active-LOW: nối công tắc thường đóng (NC) xuống
// GND; khi hở mạch (pin đọc LOW) là dừng khẩn cấp. Nội trở kéo lên bật sẵn.
#define ESTOP_PIN         2     // INT0, INPUT_PULLUP
#define ESTOP_ACTIVE_LEVEL LOW  // mức logic = dừng khẩn cấp

// ------------------------------ Xung servo (PWM) ----------------------------
// [DATASHEET/quy ước servo hobby] Khung 20 ms (50 Hz), xung 500–2500 µs quét hết
// hành trình. Trung tính 1500 µs. Với phần lớn servo 180°:
//   500 µs -> -90°, 1500 µs -> 0°, 2500 µs -> +90°.
#define SERVO_FRAME_US    20000UL  // 20 ms = 50 Hz
#define SERVO_MIN_US      500      // xung ngắn nhất
#define SERVO_MAX_US      2500     // xung dài nhất
#define SERVO_NEUTRAL_US  1500     // (MIN+MAX)/2 = vị trí trung tính 0°
// [GIẢ ĐỊNH] Cặp góc cực trị tương ứng với 500/2500 µs. Một số servo thực tế chỉ
// chạy tuyến tính trong 1000–2000 µs; CẦN hiệu chỉnh từng servo bằng lệnh quét.
#define SERVO_MIN_DEG     -90.0f
#define SERVO_MAX_DEG     +90.0f

// ------------------------------ Giới hạn hành trình --------------------------
// [GIẢ ĐỊNH] Giới hạn cơ khí an toàn từng khớp (độ). Mọi lệnh J đều bị CLAMP vào
// khoảng này TRƯỚC khi xuất xung. Chốt lại theo bản vẽ cơ khí / đo tay trước khi
// gắn tải.
#define JOINT1_MIN_DEG    -30.0f
#define JOINT1_MAX_DEG    +80.0f
#define JOINT2_MIN_DEG    -30.0f
#define JOINT2_MAX_DEG    +80.0f
#define JOINT3_MIN_DEG    -30.0f
#define JOINT3_MAX_DEG    +80.0f

// ------------------------------ Vị trí home ---------------------------------
// [GIẢ ĐỊNH] Vị trí an toàn khi khởi động / lệnh H. 0° = xung trung tính 1500 µs.
#define HOME1_DEG         0.0f
#define HOME2_DEG         0.0f
#define HOME3_DEG         0.0f

// ------------------------------ An toàn khởi động ----------------------------
// Khi cấp nguồn, servo được attach ở xung trung tính rồi QUÉT TỪ TỪ về home để
// tránh giật. Tham số quét:
#define HOME_STEP_DEG     1.0f    // độ / bước quét
#define HOME_STEP_MS      20UL    // chu kỳ một bước (không dùng delay(), dùng millis)
// Lưu ý: bước quét ~1°/20 ms tức ~50 °/s; chậm để an toàn, điều chỉnh khi đã chốt
// tải trọng.

// ------------------------------ Khác ----------------------------------------
#define NUM_SERVOS        3
#define SERIAL_RX_BUF     64      // độ dài tối đa một dòng lệnh (đủ "J,-90,-90,-90")
