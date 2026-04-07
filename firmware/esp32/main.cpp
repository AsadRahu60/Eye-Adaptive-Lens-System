/**
 * Eye Adaptive Lens System — ESP32-S3 Firmware
 * ==============================================
 * Main entry point (PlatformIO / Arduino-framework).
 *
 * Architecture
 * ────────────
 *  ┌─────────────┐   BLE (NUS)    ┌─────────────────┐
 *  │  Host (Pi)  │◄──────────────►│   ESP32-S3      │
 *  └─────────────┘                │  ┌───────────┐  │
 *                                 │  │ Sensor    │  │
 *                                 │  │ VL53L0X   │  │ (distance)
 *                                 │  │ BH1750    │  │ (lux)
 *                                 │  │ MPU6050   │  │ (IMU / yaw)
 *                                 │  └───────────┘  │
 *                                 │  ┌───────────┐  │
 *                                 │  │ LC Shutter│  │ (LEDC PWM)
 *                                 │  │ L-eye     │  │
 *                                 │  │ R-eye     │  │
 *                                 │  └───────────┘  │
 *                                 └─────────────────┘
 *
 * BLE Protocol
 * ────────────
 *  Device name : EyeLens-S3
 *  Service     : Nordic UART Service (6E400001-...)
 *  TX char     : 6E400003-... → sensor JSON packets sent to host
 *  RX char     : 6E400002-... ← commands received from host
 *
 *  Sensor packet (JSON, sent every TELEMETRY_INTERVAL_MS):
 *    {"ts":<ms>,"dist_cm":<f>,"lux":<f>,"yaw_deg":<f>}
 *
 *  Commands (ASCII, received from host):
 *    SET SHUTTER L <duty_pct>   — set left-eye LC shutter duty (0–100)
 *    SET SHUTTER R <duty_pct>   — set right-eye LC shutter duty (0–100)
 *    SET PERIOD <ms>            — set LC oscillation period in ms
 *    STATUS                     — respond with current state JSON
 *
 * Hardware Pins (ESP32-S3 DevKit, adjust for your board)
 * ───────────────────────────────────────────────────────
 *   I2C SDA      → GPIO 8
 *   I2C SCL      → GPIO 9
 *   LC Left PWM  → GPIO 4   (LEDC channel 0)
 *   LC Right PWM → GPIO 5   (LEDC channel 1)
 *   Status LED   → GPIO 2   (built-in LED on most DevKit boards)
 *
 * Dependencies (install via Arduino Library Manager or platformio.ini)
 * ────────────────────────────────────────────────────────────────────
 *   ESP32 BLE Arduino (built-in with esp32 Arduino core ≥ 3.0)
 *   ArduinoJson ≥ 7.x     (bblanchon/ArduinoJson)
 *   Adafruit_VL53L0X      (adafruit/Adafruit_VL53L0X)    — ToF distance
 *   BH1750                (claws/BH1750)                  — ambient light
 *   Adafruit MPU6050      (adafruit/Adafruit_MPU6050)     — IMU
 *
 * NOTE: If sensors are not wired, MOCK_SENSORS=1 enables simulated data.
 *
 * @file    main.cpp
 * @version 0.2.0-S1
 * @stage   S1 Research & Development
 */

// ─── Build-time options ───────────────────────────────────────────────────────
#ifndef MOCK_SENSORS
  #define MOCK_SENSORS 1   // Set to 0 when real sensor hardware is attached
#endif

// ─── Includes ─────────────────────────────────────────────────────────────────
#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <esp_task_wdt.h>   // Watchdog timer

#if !MOCK_SENSORS
  #include <Adafruit_VL53L0X.h>
  #include <BH1750.h>
  #include <Adafruit_MPU6050.h>
  #include <Adafruit_Sensor.h>
#endif

// ─── Constants ────────────────────────────────────────────────────────────────

// BLE Nordic UART Service UUIDs (standard NUS)
#define NUS_SERVICE_UUID        "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define NUS_RX_CHARACTERISTIC   "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define NUS_TX_CHARACTERISTIC   "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
#define DEVICE_NAME             "EyeLens-S3"

// GPIO
#define PIN_SDA           8
#define PIN_SCL           9
#define PIN_LC_LEFT       4
#define PIN_LC_RIGHT      5
#define PIN_STATUS_LED    2

// LC LEDC config
#define LEDC_FREQ_HZ      50     // 50 Hz LC drive (20 ms period)
#define LEDC_RESOLUTION   8      // 8-bit duty (0–255)
#define LEDC_CH_LEFT      0
#define LEDC_CH_RIGHT     1

// Timing
#define TELEMETRY_INTERVAL_MS   500   // Send a sensor packet every 500 ms
#define WATCHDOG_TIMEOUT_S      10    // Reset if loop stalls for 10 s

// Safety clamp: maximum allowed LC shutter duty (%)
#define MAX_SHUTTER_DUTY_PCT    80.0f

// ─── Globals ──────────────────────────────────────────────────────────────────

// BLE
BLEServer          *pServer        = nullptr;
BLECharacteristic  *pTxChar        = nullptr;
volatile bool       bleConnected   = false;

// Shutter state
float shutterDutyL   = 0.0f;    // % (0–100)
float shutterDutyR   = 0.0f;
uint32_t lcPeriodMs  = 30000;   // oscillation period (from host policy)

// Telemetry timestamp
uint32_t lastTelemetryMs = 0;

// Reconnect / advertising restart flag
volatile bool doStartAdv = false;

#if !MOCK_SENSORS
  Adafruit_VL53L0X tof;
  BH1750           lightSensor;
  Adafruit_MPU6050 mpu;
#endif

// ─── Sensor reading structure ─────────────────────────────────────────────────

struct SensorPacket {
  float dist_cm;
  float lux;
  float yaw_deg;
};

// ─── Utility: map duty % to 8-bit LEDC value ──────────────────────────────────

static uint8_t dutyPctToLedc(float pct) {
  pct = constrain(pct, 0.0f, 100.0f);
  return static_cast<uint8_t>(pct / 100.0f * 255.0f);
}

// ─── LC Shutter control ───────────────────────────────────────────────────────

void shutterInit() {
  ledcSetup(LEDC_CH_LEFT,  LEDC_FREQ_HZ, LEDC_RESOLUTION);
  ledcSetup(LEDC_CH_RIGHT, LEDC_FREQ_HZ, LEDC_RESOLUTION);
  ledcAttachPin(PIN_LC_LEFT,  LEDC_CH_LEFT);
  ledcAttachPin(PIN_LC_RIGHT, LEDC_CH_RIGHT);
  ledcWrite(LEDC_CH_LEFT,  0);
  ledcWrite(LEDC_CH_RIGHT, 0);
  Serial.println("[shutter] LEDC channels initialised");
}

void shutterSet(float dutyL, float dutyR) {
  // Hard safety clamp — never exceed MAX_SHUTTER_DUTY_PCT
  dutyL = constrain(dutyL, 0.0f, MAX_SHUTTER_DUTY_PCT);
  dutyR = constrain(dutyR, 0.0f, MAX_SHUTTER_DUTY_PCT);
  shutterDutyL = dutyL;
  shutterDutyR = dutyR;
  ledcWrite(LEDC_CH_LEFT,  dutyPctToLedc(dutyL));
  ledcWrite(LEDC_CH_RIGHT, dutyPctToLedc(dutyR));
  Serial.printf("[shutter] L=%.1f%% R=%.1f%%\n", dutyL, dutyR);
}

// ─── Sensor reading ───────────────────────────────────────────────────────────

#if MOCK_SENSORS
SensorPacket readSensors() {
  // Deterministic mock values for CI/bench testing without hardware
  SensorPacket p;
  uint32_t t = millis();
  p.dist_cm  = 60.0f + 30.0f * sinf(t * 0.001f);
  p.lux      = 200.0f + 100.0f * cosf(t * 0.0007f);
  p.yaw_deg  = 15.0f * sinf(t * 0.0003f);
  return p;
}
#else
SensorPacket readSensors() {
  SensorPacket p = {80.0f, 200.0f, 0.0f};  // safe defaults

  // ── VL53L0X ToF distance ────────────────────────────────────────────────────
  VL53L0X_RangingMeasurementData_t measure;
  tof.rangingTest(&measure, false);
  if (measure.RangeStatus != 4) {   // 4 = phase failure / out of range
    p.dist_cm = measure.RangeMilliMeter / 10.0f;
  }

  // ── BH1750 ambient light ────────────────────────────────────────────────────
  float lux = lightSensor.readLightLevel();
  if (lux >= 0) {
    p.lux = lux;
  }

  // ── MPU6050 yaw (Z-axis gyro integration — replace with DMP for accuracy) ───
  // TODO: Replace simple gyro read with full DMP quaternion fusion when
  //       Adafruit_MPU6050 DMP support is confirmed for ESP32-S3.
  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);
  // Simple approximation: use gyro.gyro.z as instantaneous yaw rate
  // A proper implementation should integrate or use a complementary filter.
  p.yaw_deg = gyro.gyro.z * (180.0f / M_PI);  // rad/s → deg (approx)

  return p;
}
#endif  // MOCK_SENSORS

// ─── BLE TX: send sensor packet ───────────────────────────────────────────────

void sendTelemetry(const SensorPacket &pkt) {
  if (!bleConnected || pTxChar == nullptr) return;

  StaticJsonDocument<128> doc;
  doc["ts"]       = millis();
  doc["dist_cm"]  = serialized(String(pkt.dist_cm,  1));
  doc["lux"]      = serialized(String(pkt.lux,      1));
  doc["yaw_deg"]  = serialized(String(pkt.yaw_deg,  1));

  char buf[128];
  size_t len = serializeJson(doc, buf, sizeof(buf));
  buf[len++] = '\n';   // newline delimiter for host-side line parsing

  pTxChar->setValue(reinterpret_cast<uint8_t*>(buf), len);
  pTxChar->notify();
}

// ─── BLE RX: parse incoming command from host ─────────────────────────────────

void handleCommand(const String &cmd) {
  Serial.printf("[cmd] received: %s\n", cmd.c_str());

  if (cmd.startsWith("SET SHUTTER L ")) {
    float duty = cmd.substring(14).toFloat();
    shutterSet(duty, shutterDutyR);

  } else if (cmd.startsWith("SET SHUTTER R ")) {
    float duty = cmd.substring(14).toFloat();
    shutterSet(shutterDutyL, duty);

  } else if (cmd.startsWith("SET PERIOD ")) {
    uint32_t period = static_cast<uint32_t>(cmd.substring(11).toInt());
    if (period > 0) {
      lcPeriodMs = period;
      Serial.printf("[cmd] LC period set to %u ms\n", lcPeriodMs);
    }

  } else if (cmd == "STATUS") {
    if (pTxChar) {
      StaticJsonDocument<128> doc;
      doc["shutter_L"]  = shutterDutyL;
      doc["shutter_R"]  = shutterDutyR;
      doc["period_ms"]  = lcPeriodMs;
      doc["connected"]  = bleConnected;
      doc["mock"]       = (bool)MOCK_SENSORS;
      char buf[128];
      size_t len = serializeJson(doc, buf, sizeof(buf));
      pTxChar->setValue(reinterpret_cast<uint8_t*>(buf), len);
      pTxChar->notify();
    }

  } else {
    Serial.printf("[cmd] unknown command: %s\n", cmd.c_str());
  }
}

// ─── BLE Callbacks ────────────────────────────────────────────────────────────

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *pSrv) override {
    bleConnected = true;
    digitalWrite(PIN_STATUS_LED, HIGH);
    Serial.println("[BLE] client connected");
  }

  void onDisconnect(BLEServer *pSrv) override {
    bleConnected = false;
    digitalWrite(PIN_STATUS_LED, LOW);
    Serial.println("[BLE] client disconnected — restarting advertising");
    doStartAdv = true;  // handled safely in loop()
  }
};

class RxCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pChar) override {
    String value = pChar->getValue().c_str();
    value.trim();
    if (value.length() > 0) {
      handleCommand(value);
    }
  }
};

// ─── BLE initialisation ───────────────────────────────────────────────────────

void bleInit() {
  BLEDevice::init(DEVICE_NAME);
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());

  BLEService *pService = pServer->createService(NUS_SERVICE_UUID);

  // RX characteristic (host → device)
  BLECharacteristic *pRxChar = pService->createCharacteristic(
    NUS_RX_CHARACTERISTIC,
    BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
  );
  pRxChar->setCallbacks(new RxCallbacks());

  // TX characteristic (device → host, notify)
  pTxChar = pService->createCharacteristic(
    NUS_TX_CHARACTERISTIC,
    BLECharacteristic::PROPERTY_NOTIFY
  );
  pTxChar->addDescriptor(new BLE2902());

  pService->start();

  BLEAdvertising *pAdv = BLEDevice::getAdvertising();
  pAdv->addServiceUUID(NUS_SERVICE_UUID);
  pAdv->setScanResponse(true);
  pAdv->setMinPreferred(0x06);
  BLEDevice::startAdvertising();

  Serial.printf("[BLE] advertising as '%s'\n", DEVICE_NAME);
}

// ─── Sensor hardware initialisation ──────────────────────────────────────────

void sensorsInit() {
#if MOCK_SENSORS
  Serial.println("[sensors] MOCK mode — no hardware required");
#else
  Wire.begin(PIN_SDA, PIN_SCL);

  // VL53L0X
  if (!tof.begin()) {
    Serial.println("[sensors] ERROR: VL53L0X not found — check wiring");
  } else {
    tof.startRangeContinuous();
    Serial.println("[sensors] VL53L0X OK");
  }

  // BH1750
  if (!lightSensor.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("[sensors] ERROR: BH1750 not found");
  } else {
    Serial.println("[sensors] BH1750 OK");
  }

  // MPU6050
  if (!mpu.begin()) {
    Serial.println("[sensors] ERROR: MPU6050 not found");
  } else {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("[sensors] MPU6050 OK");
  }
#endif
}

// ─── Arduino setup / loop ─────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("\n[boot] Eye Adaptive Lens System v0.2.0-S1");

  // Status LED
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_STATUS_LED, LOW);

  // Hardware watchdog — reset if loop() stalls
  esp_task_wdt_init(WATCHDOG_TIMEOUT_S, true);
  esp_task_wdt_add(nullptr);

  shutterInit();
  sensorsInit();
  bleInit();

  Serial.println("[boot] ready");
}

void loop() {
  // Pet the watchdog
  esp_task_wdt_reset();

  // Restart BLE advertising after disconnect (must be called from loop, not callback)
  if (doStartAdv) {
    doStartAdv = false;
    BLEDevice::startAdvertising();
  }

  // Send telemetry at fixed interval
  uint32_t now = millis();
  if (now - lastTelemetryMs >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryMs = now;
    SensorPacket pkt = readSensors();
    sendTelemetry(pkt);

    // Also print to Serial for bench debugging
    Serial.printf("[tel] dist=%.1fcm lux=%.1f yaw=%.1fdeg shL=%.0f%% shR=%.0f%%\n",
                  pkt.dist_cm, pkt.lux, pkt.yaw_deg, shutterDutyL, shutterDutyR);
  }

  delay(10);  // yield to FreeRTOS BLE stack
}
