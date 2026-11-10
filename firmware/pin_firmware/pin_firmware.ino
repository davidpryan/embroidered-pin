/*
 * pin_firmware.ino — embroidered pin: plays stitched animations from a flat archive in flash.
 * Waveshare ESP32-S3-Touch-LCD-1.28 (GC9A01A 240x240, CST816S touch, QMI8658 IMU)
 *
 * The data partition (label "spiffs", 0x310000) holds a PINPAK01 archive built by the web
 * gallery (docs/index.html) or tools/build_pak.py:
 *   "PINPAK01" | uint32 count | count x { char name[32]; u32 frames; u32 flags(bit0=loop);
 *   u32 bg_off; u32 bg_len; u32 dlt_off; u32 dlt_len } | blobs
 * bg = optional 240x240 RGB565 ground; dlt = frames as deltas vs previous (tools/pack_delta.py).
 *
 * Behaviour: ground appears -> animation plays (~4 s) -> finished piece holds 1-3 min
 * (short 8-frame "stir" pieces replay every 20-60 s while holding) -> fade -> next.
 * Tap = next piece now.  Hold 1 s = replay this one.  No motion 60 s -> deep sleep.
 *
 * Built automatically by GitHub Actions (.github/workflows/build.yml); the hosted gallery flashes it.
 */

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <esp_bt.h>
#include <esp_sleep.h>
#include <driver/rtc_io.h>
#include <esp_partition.h>
#include <Arduino_GFX_Library.h>

#define PIN_LCD_SCLK 10
#define PIN_LCD_MOSI 11
#define PIN_LCD_MISO 12
#define PIN_LCD_CS    9
#define PIN_LCD_DC    8
#define PIN_LCD_RST  14
#define PIN_LCD_BL    2
#define PIN_I2C_SDA   6
#define PIN_I2C_SCL   7
#define PIN_IMU_INT1  4
#define PIN_TP_INT    5
#define PIN_BAT_ADC   1
#define PIN_BOOT_BTN  0

// ---- settings: defaults here, overridden by the 64-byte block in a PINPAK02 archive (set from the web page)
struct __attribute__((packed)) Settings {
  uint8_t  bl_normal, bl_dim, bl_boost, cpu_mhz;          // backlight 0-255; cpu 80/160
  uint16_t dim_after_s, sleep_after_s;                    // sleep 0 = never
  uint16_t hold_min_s, hold_max_s, loop_min_s, loop_max_s, gen_min_s, gen_max_s;
  uint16_t batt_low_mv;                                   // low-battery cutoff
  uint8_t  wom_mg, gen_step_ms, gen_share, touch_wake;    // wake threshold; generative frame interval; % of slots that may be generative; wake by touch
  uint8_t  batt_icon, reserved[37];
};
Settings S = {90, 20, 200, 80, 20, 60, 60, 180, 40, 90, 120, 300, 3450, 120, 60, 100, 0, 1, {0}};
#define BOOST_MS         4000
#define STIR_MIN_MS     20000UL
#define STIR_MAX_MS     60000UL
#define FRAME_MS           85
#define FADE_STEPS          8
#define SHUFFLE          true
#define BL_NORMAL (S.bl_normal)
#define BL_DIM    (S.bl_dim)
#define BL_BOOST  (S.bl_boost)
#define DIM_AFTER_MS   (S.dim_after_s * 1000UL)
#define SLEEP_AFTER_MS (S.sleep_after_s * 1000UL)
#define HOLD_MIN_MS (S.hold_min_s * 1000UL)
#define HOLD_MAX_MS (S.hold_max_s * 1000UL)
#define LOOP_MIN_MS (S.loop_min_s * 1000UL)
#define LOOP_MAX_MS (S.loop_max_s * 1000UL)
#define WOM_THRESHOLD_MG (S.wom_mg)
#define BATT_LOW_V (S.batt_low_mv / 1000.0f)

#define FRAME_PX    (240 * 240)
#define FRAME_BYTES (FRAME_PX * 2)
#define MAX_PIECES  64
#define REC_MAX     (256 * 1024)

#define QMI_ADDR 0x6B
#define QMI_WHO_AM_I 0x00
#define QMI_CTRL1 0x02
#define QMI_CTRL2 0x03
#define QMI_CTRL3 0x04
#define QMI_CTRL7 0x08
#define QMI_CTRL9 0x0A
#define QMI_CAL1_L 0x0B
#define QMI_CAL1_H 0x0C
#define QMI_STATUSINT 0x2D
#define QMI_STATUS1 0x2F
#define QMI_RESET 0x60

Arduino_DataBus *bus = new Arduino_ESP32SPI(PIN_LCD_DC, PIN_LCD_CS, PIN_LCD_SCLK, PIN_LCD_MOSI, PIN_LCD_MISO, FSPI);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, PIN_LCD_RST, 0, true);

uint16_t *frameBuf; uint8_t *recBuf;
#include "generative.h"
struct Piece { char name[32]; int frames; bool loop; bool gen; int genId; uint32_t bgOff, bgLen, dltOff, dltLen; };
const esp_partition_t *part;
Piece pieces[MAX_PIECES]; int nPieces = 0;
int order[MAX_PIECES]; int orderPos = 0;
int cur = 0; int frameIdx = 0; uint32_t dltPos = 0, dltEnd = 0, rec1Pos = 0, loopUntil = 0;
enum Phase { PLAYING, HOLDING, GENERATING } phase = PLAYING;
uint32_t genDeadline = 0;
#define GEN_MIN_MS (S.gen_min_s * 1000UL)   // minimum slot for a generative piece; it always finishes what it is making
#define GEN_MAX_MS (S.gen_max_s * 1000UL)
#define GEN_STEP_MS (S.gen_step_ms)
uint32_t nextFrameAt = 0, holdUntil = 0, pieceDeadline = 0, nextStir = 0, lastMotion = 0, boostUntil = 0;
uint8_t currentBL = 255;
RTC_DATA_ATTR int savedPiece = 0;
volatile bool motionFlag = false, touchFlag = false;
void IRAM_ATTR onMotion() { motionFlag = true; }
void IRAM_ATTR onTouch()  { touchFlag = true; }

void setBacklight(uint8_t d) { if (d != currentBL) { ledcWrite(PIN_LCD_BL, d); currentBL = d; } }
float batteryV() { uint32_t mv = 0; for (int i = 0; i < 8; i++) mv += analogReadMilliVolts(PIN_BAT_ADC); return mv / 8 * 3.0f / 1000.0f; }
void blit() { gfx->draw16bitRGBBitmap(0, 0, frameBuf, 240, 240); }

// ---------------- manifest / playlist ----------------
bool loadPak() {
  part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_SPIFFS, NULL);
  if (!part) return false;
  uint8_t hdr[12]; esp_partition_read(part, 0, hdr, 12);
  bool v2 = memcmp(hdr, "PINPAK02", 8) == 0;
  if (!v2 && memcmp(hdr, "PINPAK01", 8) != 0) return false;
  uint32_t count; memcpy(&count, hdr + 8, 4);
  if (count > MAX_PIECES) count = MAX_PIECES;
  uint32_t tableOff = 12;
  if (v2) { Settings tmp; esp_partition_read(part, 12, &tmp, sizeof tmp); if (tmp.cpu_mhz == 80 || tmp.cpu_mhz == 160) S = tmp; tableOff = 12 + sizeof(Settings); }
  for (uint32_t i = 0; i < count; i++) {
    uint8_t e[56]; esp_partition_read(part, tableOff + i * 56, e, 56);
    memcpy(pieces[i].name, e, 32); pieces[i].name[31] = 0;
    uint32_t v[6]; memcpy(v, e + 32, 24);
    pieces[i].frames = v[0]; pieces[i].loop = v[1] & 1; pieces[i].gen = v[1] & 2; pieces[i].genId = pieces[i].gen ? genIndex(pieces[i].name) : -1; pieces[i].bgOff = v[2]; pieces[i].bgLen = v[3]; pieces[i].dltOff = v[4]; pieces[i].dltLen = v[5];
  }
  nPieces = count;
  for (int i = 0; i < nPieces; i++) order[i] = i;
  if (SHUFFLE) for (int i = nPieces - 1; i > 0; i--) { int j = random(i + 1); int t = order[i]; order[i] = order[j]; order[j] = t; }
  return nPieces > 0;
}

// ---------------- frame decoding ----------------
void loadGround(int p) {
  if (pieces[p].bgLen == FRAME_BYTES) esp_partition_read(part, pieces[p].bgOff, frameBuf, FRAME_BYTES);
  else memset(frameBuf, 0, FRAME_BYTES);
}
bool nextDelta() {
  if (dltPos + 4 > dltEnd) return false;
  uint32_t len; esp_partition_read(part, dltPos, &len, 4); dltPos += 4;
  if (len > REC_MAX || dltPos + len > dltEnd) { dltPos = dltEnd; return false; }
  esp_partition_read(part, dltPos, recBuf, len); dltPos += len;
  uint32_t i = 0, px = 0;
  while (i < len && px < FRAME_PX) {
    uint8_t b = recBuf[i++]; uint8_t op = b >> 6; uint32_t n = (b & 63) + 1;
    if (op == 0) px += n;
    else if (op == 1) { uint16_t v = recBuf[i] | (recBuf[i + 1] << 8); i += 2; while (n-- && px < FRAME_PX) frameBuf[px++] = v; }
    else if (op == 2) { while (n-- && px < FRAME_PX) { frameBuf[px++] = recBuf[i] | (recBuf[i + 1] << 8); i += 2; } }
    else { n = (((b & 63) << 8) | recBuf[i++]) + 1; px += n; }
  }
  return true;
}
void startPiece(int p, bool fromGround, bool stir = false) {
  cur = p; savedPiece = p;
  if (!stir) pieceDeadline = 0;
  if (pieces[p].gen && pieces[p].genId >= 0) { genSlow = pieces[p].genId & 256; genInit(pieces[p].genId & 255); blit(); phase = GENERATING; genDeadline = millis() + random(GEN_MIN_MS, GEN_MAX_MS); nextFrameAt = millis(); return; }
  dltPos = pieces[p].dltOff; dltEnd = pieces[p].dltOff + pieces[p].dltLen;
  uint32_t len0 = 0; if (dltPos + 4 <= dltEnd) esp_partition_read(part, dltPos, &len0, 4);
  rec1Pos = dltPos + 4 + len0;
  if (fromGround) { loadGround(p); blit(); }
  frameIdx = 0; phase = PLAYING; nextFrameAt = millis();
  if (!stir) loopUntil = millis() + random(LOOP_MIN_MS, LOOP_MAX_MS);
}
void fadeOut() {
  for (int s = 1; s <= FADE_STEPS; s++) {
    for (int i = 0; i < FRAME_PX; i++) {
      uint16_t c = frameBuf[i];
      uint32_t r = (c >> 11) * (FADE_STEPS - 1) / FADE_STEPS, g = ((c >> 5) & 63) * (FADE_STEPS - 1) / FADE_STEPS, b = (c & 31) * (FADE_STEPS - 1) / FADE_STEPS;
      frameBuf[i] = (r << 11) | (g << 5) | b;
    }
    blit();
  }
}
int nextIndex() {
  for (int tries = 0; tries < nPieces; tries++) {
    orderPos = (orderPos + 1) % nPieces; int p = order[orderPos];
    if (pieces[p].gen && random(100) >= S.gen_share) continue;      // skip some generative slots to save battery
    return p;
  }
  orderPos = (orderPos + 1) % nPieces; return order[orderPos];
}

// ---------------- IMU / sleep ----------------
void imuWrite(uint8_t r, uint8_t v) { Wire.beginTransmission(QMI_ADDR); Wire.write(r); Wire.write(v); Wire.endTransmission(); }
uint8_t imuRead(uint8_t r) { Wire.beginTransmission(QMI_ADDR); Wire.write(r); Wire.endTransmission(false); Wire.requestFrom((uint8_t)QMI_ADDR, (uint8_t)1); return Wire.available() ? Wire.read() : 0; }
bool imuCmd(uint8_t c) {
  imuWrite(QMI_CTRL9, c); uint32_t t0 = millis();
  while (!(imuRead(QMI_STATUSINT) & 0x80)) { if (millis() - t0 > 200) return false; delay(1); }
  imuWrite(QMI_CTRL9, 0x00); t0 = millis();
  while (imuRead(QMI_STATUSINT) & 0x80) { if (millis() - t0 > 200) return false; delay(1); }
  return true;
}
bool imuSetupWoM() {
  if (imuRead(QMI_WHO_AM_I) != 0x05) return false;
  imuWrite(QMI_RESET, 0xB0); delay(20);
  imuWrite(QMI_CTRL1, 0x48); imuWrite(QMI_CTRL7, 0x00); imuWrite(QMI_CTRL2, 0x0D); imuWrite(QMI_CTRL3, 0x00);
  imuWrite(QMI_CAL1_L, WOM_THRESHOLD_MG); imuWrite(QMI_CAL1_H, 0x84);
  if (!imuCmd(0x08)) return false;
  imuWrite(QMI_CTRL7, 0x01); return true;
}
void imuClear() { (void)imuRead(QMI_STATUS1); }
void deepSleep(bool lowBatt) {
  setBacklight(0); gfx->displayOff(); imuClear();
  uint32_t t0 = millis();
  while (digitalRead(PIN_IMU_INT1) == HIGH && millis() - t0 < 500) { imuClear(); delay(10); }
  if (lowBatt) esp_sleep_enable_timer_wakeup(600ULL * 1000000ULL);
  else {
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_IMU_INT1, 1);                                  // motion
    if (S.touch_wake) { rtc_gpio_pullup_en((gpio_num_t)PIN_TP_INT); esp_sleep_enable_ext1_wakeup(1ULL << PIN_TP_INT, ESP_EXT1_WAKEUP_ALL_LOW); }   // touch (active low)
    else { rtc_gpio_pullup_en((gpio_num_t)PIN_BOOT_BTN); esp_sleep_enable_ext1_wakeup(1ULL << PIN_BOOT_BTN, ESP_EXT1_WAKEUP_ALL_LOW); }         // BOOT button
  }
  esp_deep_sleep_start();
}

// ---------------- setup / loop ----------------
void setup() {
  WiFi.mode(WIFI_OFF); btStop(); Serial.begin(115200);
  pinMode(PIN_IMU_INT1, INPUT); pinMode(PIN_TP_INT, INPUT_PULLUP); pinMode(PIN_BOOT_BTN, INPUT_PULLUP); analogReadResolution(12);
  frameBuf = (uint16_t *)ps_malloc(FRAME_BYTES); recBuf = (uint8_t *)ps_malloc(REC_MAX);
  if (!frameBuf || !recBuf) Serial.println("PSRAM alloc failed");
  ledcAttach(PIN_LCD_BL, 5000, 8); setBacklight(0);
  gfx->begin(40000000); gfx->fillScreen(RGB565_BLACK);
  float v = batteryV();
  if (v < BATT_LOW_V && v < 4.25f) { gfx->fillCircle(120, 120, 6, RGB565_RED); setBacklight(BL_DIM); delay(1200); deepSleep(true); }
  randomSeed(esp_random());
  bool ok = loadPak();
  setCpuFrequencyMhz(S.cpu_mhz == 160 ? 160 : 80);
  if (!ok) { gfx->setTextColor(RGB565_RED); gfx->setCursor(40, 110); gfx->print("No animation archive"); setBacklight(BL_NORMAL); while (true) delay(1000); }
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 400000); imuSetupWoM();
  attachInterrupt(digitalPinToInterrupt(PIN_IMU_INT1), onMotion, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_TP_INT), onTouch, FALLING);
  for (int i = 0; i < nPieces; i++) if (order[i] == savedPiece % nPieces) orderPos = i;
  startPiece(order[orderPos], true);
  if (S.batt_icon && v < 4.25f && v < 3.7f) {   // stitched battery glyph, bottom, for a moment
    int pct = constrain((int)((v - 3.4f) / 0.75f * 100), 0, 100);
    gfx->drawRoundRect(96, 200, 44, 18, 3, RGB565_WHITE); gfx->fillRect(140, 205, 4, 8, RGB565_WHITE);
    gfx->fillRect(99, 203, 38 * pct / 100, 12, pct < 25 ? RGB565_RED : RGB565_WHITE);
    setBacklight(BL_NORMAL); delay(1500); blit();
  }
  setBacklight(BL_NORMAL); lastMotion = millis();
}

void loop() {
  uint32_t now = millis();
  if (motionFlag) { motionFlag = false; lastMotion = now; imuClear(); }
  if (touchFlag) {
    touchFlag = false; lastMotion = now; boostUntil = now + BOOST_MS;
    uint32_t t0 = millis(); while (digitalRead(PIN_TP_INT) == LOW && millis() - t0 < 1500) delay(10);
    fadeOut();
    startPiece(millis() - t0 > 900 ? cur : nextIndex(), true);
  }
  uint32_t idle = now - lastMotion;
  if (now < boostUntil) setBacklight(BL_BOOST); else if (idle > DIM_AFTER_MS) setBacklight(BL_DIM); else setBacklight(BL_NORMAL);
  if (S.sleep_after_s && idle > SLEEP_AFTER_MS && phase != PLAYING) deepSleep(false);

  if (phase == GENERATING) {
    if (now >= genDeadline && (genCanSwitch() || now >= genDeadline + 180000UL)) { fadeOut(); startPiece(nextIndex(), true); }   // finish the composition first
    else if (now >= nextFrameAt) { genStep(); blit(); nextFrameAt = now + (genSlow ? GEN_STEP_MS * 4 : GEN_STEP_MS); }
  } else if (phase == PLAYING) {
    if (now >= nextFrameAt) {
      if (frameIdx < pieces[cur].frames && nextDelta()) { blit(); frameIdx++; nextFrameAt = now + FRAME_MS; }
      else if (pieces[cur].loop && now < loopUntil) {           // wrap: decode last->first record, then continue from frame 1
        if (nextDelta()) blit();
        dltPos = rec1Pos; frameIdx = 1; nextFrameAt = now + FRAME_MS;
      }
      else { phase = HOLDING; if (!pieceDeadline) pieceDeadline = now + (pieces[cur].loop ? 1500 : random(HOLD_MIN_MS, HOLD_MAX_MS)); holdUntil = pieceDeadline; nextStir = now + random(STIR_MIN_MS, STIR_MAX_MS); }
    }
  } else {
    if (now >= holdUntil) { fadeOut(); startPiece(nextIndex(), true); }
    else if (pieces[cur].frames <= 8 && now >= nextStir) startPiece(cur, true, true);   // insects stir again, deadline unchanged
  }
  static uint32_t lastBatt = 0;
  if (now - lastBatt > 10000) { lastBatt = now; float v = batteryV(); Serial.printf("BATT %.2f %s\n", v, v > 4.25f ? "USB" : "BAT"); if (v < BATT_LOW_V && v < 4.25f) deepSleep(true); }
  delay(phase == HOLDING ? 40 : 3);
}
