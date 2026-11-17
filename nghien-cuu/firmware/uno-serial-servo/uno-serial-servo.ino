// ============================================================================
//  uno-serial-servo.ino — firmware điều khiển 3 servo qua giao thức Serial
// ----------------------------------------------------------------------------
//  Mục đích: nhận góc khớp qua Serial và trả A,<micros> ngay khi nhận xong dòng,
//  để đo trễ vòng (round-trip latency) thực tế — phục vụ Phương án 3.
//
//  Giao thức (mỗi lệnh một dòng, kết thúc '\n'):
//    J,<t1>,<t2>,<t3>  -> A,<micros>   đặt góc 3 khớp (độ, cho phép âm)
//    H                 -> A,<micros>   về vị trí home
//    P                 -> P,<micros>   ping
//    S                 -> S,<trạng thái>
//
//  An toàn:
//    - Mọi góc bị CLAMP vào giới hạn từng khớp (config.h) trước khi xuất xung.
//    - Khởi động: attach xung trung tính rồi quét từ từ về home (không giật).
//    - Dừng khẩn cấp ESTOP_PIN active-low: servo về trung tính, từ chối J/H.
//    - Không dùng delay(): đọc Serial không blocking, quét home bằng millis().
//
//  Chân nối dây: xem config.h. Xung servo 500–2500 µs @ 50 Hz.
// ============================================================================

#include <Servo.h>
#include "config.h"

// ------------------------------ Đối tượng -----------------------------------
Servo servo[NUM_SERVOS];

const uint8_t SERVO_PIN[NUM_SERVOS]  = { SERVO1_PIN, SERVO2_PIN, SERVO3_PIN };
const float   JOINT_MIN[NUM_SERVOS]  = { JOINT1_MIN_DEG, JOINT2_MIN_DEG, JOINT3_MIN_DEG };
const float   JOINT_MAX[NUM_SERVOS]  = { JOINT1_MAX_DEG, JOINT2_MAX_DEG, JOINT3_MAX_DEG };
const float   HOME_DEG[NUM_SERVOS]   = { HOME1_DEG, HOME2_DEG, HOME3_DEG };

// Trạng thái góc: currentDeg là góc đang xuất xung hiện tại, targetDeg là đích.
float currentDeg[NUM_SERVOS];
float targetDeg[NUM_SERVOS];

// Bộ đệm nhận dòng lệnh.
char    rxBuf[SERIAL_RX_BUF];
uint8_t rxLen = 0;

// Trạng thái an toàn.
bool          homing       = false;   // đang quét về home lúc khởi động
bool          estopLatched = false;   // đã áp dừng khẩn cấp (tránh gọi lặp)
unsigned long lastHomeStepMs = 0;

// ------------------------------ Tiện ích ------------------------------------
static inline float clampf(float v, float lo, float hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

// Xuất xung cho một servo từ góc (độ), có CLAMP giới hạn khớp.
static void writeServo(uint8_t idx, float angleDeg) {
  float a = clampf(angleDeg, JOINT_MIN[idx], JOINT_MAX[idx]);
  float frac = (a - SERVO_MIN_DEG) / (SERVO_MAX_DEG - SERVO_MIN_DEG);
  long us = (long)(SERVO_MIN_US + frac * (SERVO_MAX_US - SERVO_MIN_US));
  us = constrain(us, (long)SERVO_MIN_US, (long)SERVO_MAX_US);
  servo[idx].writeMicroseconds((int)us);
}

// Quét currentDeg -> targetDeg một bước (chỉ dùng lúc homing, không giật).
static bool stepHoming() {
  bool allDone = true;
  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    float d = targetDeg[i] - currentDeg[i];
    if (d >  HOME_STEP_DEG)      { currentDeg[i] += HOME_STEP_DEG; allDone = false; }
    else if (d < -HOME_STEP_DEG) { currentDeg[i] -= HOME_STEP_DEG; allDone = false; }
    else                         { currentDeg[i]  = targetDeg[i]; }
    writeServo(i, currentDeg[i]);
  }
  return allDone;
}

// ------------------------------ Phân tích lệnh -------------------------------
// Parse "J,t1,t2,t3" -> 3 góc. Trả false nếu sai cú pháp / thiếu số.
static bool parseAngles(const char* s, float out[NUM_SERVOS]) {
  char buf[SERIAL_RX_BUF];
  strncpy(buf, s, SERIAL_RX_BUF - 1);
  buf[SERIAL_RX_BUF - 1] = '\0';

  char* tok = strtok(buf, ",");         // bỏ "J"
  if (tok == NULL) return false;

  uint8_t n = 0;
  while ((tok = strtok(NULL, ",")) != NULL && n < NUM_SERVOS) {
    out[n++] = atof(tok);
  }
  return (n == NUM_SERVOS);
}

// In trạng thái (lệnh S).
static void printStatus(unsigned long nowMicros) {
  Serial.print(F("S,v=" FIRMWARE_VERSION ",uptime_ms="));
  Serial.print(millis());
  Serial.print(F(",homing="));
  Serial.print(homing ? 1 : 0);
  Serial.print(F(",estop="));
  Serial.print(digitalRead(ESTOP_PIN) == ESTOP_ACTIVE_LEVEL ? 1 : 0);
  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    Serial.print(F(",a"));
    Serial.print(i + 1);
    Serial.print(F("="));
    Serial.print(currentDeg[i], 1);
    Serial.print(F("/"));
    Serial.print(targetDeg[i], 1);
    Serial.print(F("["));
    Serial.print(JOINT_MIN[i], 1);
    Serial.print(F(".."));
    Serial.print(JOINT_MAX[i], 1);
    Serial.print(F("]"));
  }
  Serial.println();
}

// Xử lý một dòng lệnh đã nhận đủ. nowMicros = micros() ngay thời điểm nhận xong.
static void handleCommand(const char* cmd, unsigned long nowMicros) {
  switch (cmd[0]) {
    case 'J': case 'j': {
      if (eStopActive()) { Serial.println(F("E,ESTOP")); return; }
      float t[NUM_SERVOS];
      if (!parseAngles(cmd, t)) { Serial.println(F("E,SYNTAX")); return; }
      homing = false;  // hủy quét home nếu đang dở
      for (uint8_t i = 0; i < NUM_SERVOS; i++) {
        targetDeg[i]  = clampf(t[i], JOINT_MIN[i], JOINT_MAX[i]);
        currentDeg[i] = targetDeg[i];
        writeServo(i, targetDeg[i]);
      }
      Serial.print(F("A,")); Serial.println(nowMicros);
      break;
    }
    case 'H': case 'h': {
      if (eStopActive()) { Serial.println(F("E,ESTOP")); return; }
      homing = false;
      for (uint8_t i = 0; i < NUM_SERVOS; i++) {
        targetDeg[i]  = HOME_DEG[i];
        currentDeg[i] = targetDeg[i];
        writeServo(i, targetDeg[i]);
      }
      Serial.print(F("A,")); Serial.println(nowMicros);
      break;
    }
    case 'P': case 'p': {
      Serial.print(F("P,")); Serial.println(nowMicros);
      break;
    }
    case 'S': case 's': {
      printStatus(nowMicros);
      break;
    }
    default:
      Serial.println(F("E,UNKNOWN"));
      break;
  }
}

// Đọc Serial không blocking, tách dòng rồi xử lý ngay.
static void processSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (rxLen > 0) {                 // bỏ qua dòng rỗng (để \r\n không kích 2 lần)
        rxBuf[rxLen] = '\0';
        handleCommand(rxBuf, micros());
        rxLen = 0;
      }
    } else if (rxLen < SERIAL_RX_BUF - 1) {
      rxBuf[rxLen++] = c;
    } else {
      rxLen = 0;                       // tràn bộ đệm: bỏ dòng này
    }
  }
}

// ------------------------------ An toàn: dừng khẩn cấp -----------------------
// Nếu chân ESTOP tích cực -> servo về trung tính và chặn lệnh J/H.
static bool eStopActive() {
  return (digitalRead(ESTOP_PIN) == ESTOP_ACTIVE_LEVEL);
}

static void applyEStop() {
  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    servo[i].writeMicroseconds(SERVO_NEUTRAL_US);
  }
  currentDeg[0] = currentDeg[1] = currentDeg[2] = 0.0f;
  targetDeg[0] = targetDeg[1] = targetDeg[2] = 0.0f;
  homing = false;
}

// ------------------------------ setup / loop --------------------------------
void setup() {
  Serial.begin(SERIAL_BAUD);
  pinMode(ESTOP_PIN, INPUT_PULLUP);

  // Attach ở xung trung tính (1500 µs = 0°) để tránh giật lúc cấp nguồn.
  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    servo[i].attach(SERVO_PIN[i], SERVO_MIN_US, SERVO_MAX_US);
    servo[i].writeMicroseconds(SERVO_NEUTRAL_US);
    currentDeg[i] = 0.0f;
    targetDeg[i] = HOME_DEG[i];
  }

  // Bắt đầu quét từ từ về home.
  homing = true;
  lastHomeStepMs = millis();

  Serial.print(F("OK uno-serial-servo v" FIRMWARE_VERSION));
  Serial.println();
}

void loop() {
  processSerial();

  // Quét home (không delay, chỉ bước khi đủ chu kỳ).
  if (homing && !eStopActive()) {
    if (millis() - lastHomeStepMs >= HOME_STEP_MS) {
      lastHomeStepMs = millis();
      if (stepHoming()) homing = false;
    }
  }

  // Dừng khẩn cấp: một lần khi chuyển sang trạng thái dừng thì kéo servo về trung
  // tính và giữ. Khi chân ESTOP nhả ra, cho phép điều khiển lại (servo vẫn đứng
  // trung tính cho tới khi có lệnh J/H kế tiếp).
  if (eStopActive()) {
    if (!estopLatched) { applyEStop(); estopLatched = true; }
  } else {
    estopLatched = false;
  }
}
