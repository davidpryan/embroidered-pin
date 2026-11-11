// generative.h — ten procedural stitching patterns drawn live on the pin.
// Each has init() (new random parameters) and step() (adds a few stitches).
// Old thread slowly fades into the ground so the piece evolves forever.
#pragma once
#include <Arduino.h>
#include <math.h>

extern uint16_t *frameBuf;
#define GW 240
#define GH 240
#define GEN_COUNT 70
static const char *GEN_NAMES[GEN_COUNT] = {"gen_wander", "gen_spirograph", "gen_vine", "gen_lissajous", "gen_sashiko_drift",
                                           "gen_patchwork", "gen_mandala", "gen_flowfield", "gen_phyllotaxis", "gen_life_x", "gen_granny_square", "gen_granny_shapes",
                                           "gen_roses_cream", "gen_roses_black", "gen_daisies_cream", "gen_daisies_black", "gen_lavender_cream", "gen_lavender_black",
                                           "gen_blossom_cream", "gen_blossom_black", "gen_ferns_cream", "gen_ferns_black",
                                           "gen_asawa_lobes_cream", "gen_asawa_lobes_black", "gen_asawa_nested_cream", "gen_asawa_nested_black", "gen_asawa_tied_cream", "gen_asawa_tied_black",
                                           "gen_asawa_column_cream", "gen_asawa_column_black", "gen_asawa_loops_cream", "gen_asawa_loops_black",
                                           "gen_turing", "gen_truchet", "gen_flock", "gen_dla", "gen_packing", "gen_subdivide", "gen_contours", "gen_attractor", "gen_harmonograph", "gen_molnar",
                                           "touch_seam", "touch_satin", "touch_bloom", "touch_ripple", "touch_knots", "touch_flock", "touch_crystal", "touch_vine", "touch_web", "touch_granny",
                                           "touch_rose", "touch_asawa", "touch_mend", "touch_buttons", "touch_kaleido", "touch_string", "touch_contours", "touch_shibori", "touch_life", "touch_truchet",
                                           "gen_seigaiha", "gen_asanoha", "gen_shippo", "gen_kikko", "gen_hitomezashi", "gen_kagome", "gen_yagasuri", "gen_kanoko"};
#define REACTIVE_LAST 61
#define REACTIVE_FIRST 42

// ---------------- palette / colour helpers ----------------
static inline uint16_t C565(int r, int g, int b) { return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3); }
static inline void C888(uint16_t c, int &r, int &g, int &b) { r = (c >> 8) & 0xF8; g = (c >> 3) & 0xFC; b = (c << 3) & 0xF8; }
static uint16_t shade(uint16_t c, float f) { int r, g, b; C888(c, r, g, b); r = constrain(int(r * f), 0, 255); g = constrain(int(g * f), 0, 255); b = constrain(int(b * f), 0, 255); return C565(r, g, b); }
static uint16_t lerp565(uint16_t a, uint16_t b, int t) { int ar, ag, ab, br, bg, bb; C888(a, ar, ag, ab); C888(b, br, bg, bb); return C565(ar + (br - ar) * t / 256, ag + (bg - ag) * t / 256, ab + (bb - ab) * t / 256); }
static const uint16_t PAL[] = {C565(214, 168, 58), C565(124, 34, 42), C565(72, 132, 130), C565(236, 226, 204), C565(96, 58, 92), C565(178, 92, 52), C565(132, 150, 100)};
static const uint16_t CREAM = C565(238, 230, 210), INDIGO = C565(38, 52, 96), INDIGO_L = C565(74, 96, 150), VERM = C565(196, 66, 44), SOOT = C565(30, 27, 29);
static uint16_t ground = 0, groundShadow = 0;
static inline bool inCircle(float x, float y, float r = 118) { float dx = x - 120, dy = y - 120; return dx * dx + dy * dy < r * r; }
static float frand() { return random(0, 10000) / 10000.0f; }
static float frandr(float a, float b) { return a + (b - a) * frand(); }

// ---------------- drawing primitives ----------------
static inline void px(int x, int y, uint16_t c) { if ((unsigned)x < GW && (unsigned)y < GH) frameBuf[y * GW + x] = c; }
static void disc(float cx, float cy, float r, uint16_t c) {
  if (!(r > 0 && r < 200) || !(fabsf(cx) < 1000) || !(fabsf(cy) < 1000)) return;
  int x0 = floorf(cx - r), x1 = ceilf(cx + r), y0 = floorf(cy - r), y1 = ceilf(cy + r); float r2 = r * r;
  for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) { float dx = x + 0.5f - cx, dy = y + 0.5f - cy; if (dx * dx + dy * dy <= r2) px(x, y, c); }
}
static void thick(float x0, float y0, float x1, float y1, float w, uint16_t c) {
  float dx = x1 - x0, dy = y1 - y0, L = sqrtf(dx * dx + dy * dy); if (!(L < 600)) return; int n = max(1, int(L / 0.6f));
  for (int i = 0; i <= n; i++) { float t = (float)i / n; disc(x0 + dx * t, y0 + dy * t, w * 0.5f, c); }
}
// a thread: shadow, body, highlight ridge
static void stitch(float x0, float y0, float x1, float y1, float w, uint16_t c) {
  thick(x0 + 0.6f, y0 + 0.9f, x1 + 0.6f, y1 + 0.9f, w, groundShadow);
  thick(x0, y0, x1, y1, w, shade(c, 0.82f));
  thick(x0, y0, x1, y1, w * 0.6f, c);
  if (w >= 2.2f) thick(x0 - 0.3f, y0 - 0.5f, x1 - 0.3f, y1 - 0.5f, w * 0.25f, shade(c, 1.3f));
}
static void knot(float x, float y, float r, uint16_t c) {
  disc(x, y + 1, r, groundShadow); disc(x, y, r, shade(c, 0.7f)); disc(x, y, r * 0.78f, c); disc(x - r * 0.3f, y - r * 0.35f, r * 0.3f, shade(c, 1.35f));
}
static void dashes(float x0, float y0, float x1, float y1, float dash, float gap, float w, uint16_t c) {
  float dx = x1 - x0, dy = y1 - y0, L = sqrtf(dx * dx + dy * dy); if (L < 0.5f) return; dx /= L; dy /= L;
  for (float p = 0; p < L; p += dash + gap) { float e = min(L, p + dash); if (inCircle(x0 + dx * p, y0 + dy * p)) stitch(x0 + dx * p, y0 + dy * p, x0 + dx * e, y0 + dy * e, w, c); }
}
static void fillGround(uint16_t col, bool linen) {
  ground = col; groundShadow = shade(col, 0.6f);
  int r, g, b; C888(col, r, g, b);
  for (int y = 0; y < GH; y++) {
    int rowN = linen ? (int)((y * 2654435761u) >> 29) - 4 : 0;
    for (int x = 0; x < GW; x++) {
      int n = linen ? rowN + (int)(((x * 2246822519u) ^ (y * 3266489917u)) >> 29) - 4 : 0;
      frameBuf[y * GW + x] = inCircle(x, y, 121) ? C565(constrain(r + n, 0, 255), constrain(g + n, 0, 255), constrain(b + n, 0, 255)) : 0;
    }
  }
}
static void fadeToGround(int amount) { for (int i = 0; i < GW * GH; i++) if (frameBuf[i] != ground) frameBuf[i] = lerp565(frameBuf[i], ground, amount); }

// ---------------- generator state ----------------
struct Gen {
  int id = 0; int steps = 0;
  float a, b, c, d, e, f, x, y, ang, hue;          // free parameters
  int i, n, col; uint16_t pcol;
  uint8_t cells[32 * 32]; uint8_t cells2[32 * 32];
  float px_[64], py_[64], pvx[64], pvy[64]; uint16_t pc[64];
  float branchX[40], branchY[40], branchA[40], branchL[40]; int branches;
};
static Gen G;
static bool genComplete = false;   // composition finished: hold (or, in slow mode, dissolve and begin again)
static bool genEvolving = false;   // never 'finishes' — may be switched away from at any time
static bool genSlow = false;
static bool genFlow = false;       // flow mode: sew slowly, tap = fresh composition, finished = advance to the next piece
static int  slowFade = 0;
static uint16_t palRand() { return PAL[random(0, 7)]; }

// ---- 0 wandering seam: a running stitch with momentum, re-entering with a new colour
static void initWander() { uint16_t g = random(2) ? SOOT : C565(232, 224, 204); fillGround(g, g != SOOT); G.x = 120; G.y = 120; G.ang = frandr(0, 6.28f); G.pcol = palRand(); G.a = frandr(0.1f, 0.35f); }
static void stepWander() {
  for (int k = 0; k < 3; k++) {
    G.ang += frandr(-G.a, G.a);
    float nx = G.x + cosf(G.ang) * 6, ny = G.y + sinf(G.ang) * 6;
    if (!inCircle(nx, ny, 112)) { G.ang = atan2f(120 - G.y, 120 - G.x) + frandr(-0.8f, 0.8f); G.pcol = palRand(); G.x = 120 + cosf(G.ang + 3.14f) * 100; G.y = 120 + sinf(G.ang + 3.14f) * 100; continue; }
    stitch(G.x, G.y, nx - cosf(G.ang) * 1.6f, ny - sinf(G.ang) * 1.6f, 2.4f, G.pcol);
    G.x = nx; G.y = ny;
  }
  if (G.steps % 40 == 39) fadeToGround(10);
}
// ---- 1 spirograph: hypotrochoid satin, new gears each pass
static void initSpiro() { fillGround(SOOT, false); G.a = random(40, 100); G.b = random(7, 45); G.c = random(10, 70); G.hue = 0; G.pcol = palRand(); G.i = 0; G.n = random(2, 7); }
static void stepSpiro() {
  float k = (G.a - G.b) / G.b;
  for (int s = 0; s < 6; s++) {
    float t0 = G.i * 0.05f, t1 = t0 + 0.05f;
    float x0 = 120 + (G.a - G.b) * cosf(t0) + G.c * cosf(k * t0), y0 = 120 + (G.a - G.b) * sinf(t0) - G.c * sinf(k * t0);
    float x1 = 120 + (G.a - G.b) * cosf(t1) + G.c * cosf(k * t1), y1 = 120 + (G.a - G.b) * sinf(t1) - G.c * sinf(k * t1);
    if (inCircle(x0, y0) && inCircle(x1, y1)) stitch(x0, y0, x1, y1, 2.6f, G.pcol);
    G.i++;
    if (G.i % 500 == 0) G.pcol = palRand();
  }
  if (G.i > 1000 * G.n) genComplete = true;
}
// ---- 2 vine: branching growth with leaves and knot flowers
static void initVine() { fillGround(C565(232, 224, 204), true); G.branches = 1; float x = 120 + frandr(-40, 40); G.branchX[0] = x; G.branchY[0] = 120 + sqrtf(108 * 108 - (x - 120) * (x - 120)) - 3; G.branchA[0] = -1.57f + frandr(-0.3f, 0.3f); G.branchL[0] = 1; }
static void stepVine() {
  if (G.branches == 0) { genComplete = true; return; }
  for (int bi = 0; bi < G.branches; bi++) {
    float &x = G.branchX[bi], &y = G.branchY[bi], &a = G.branchA[bi];
    a += frandr(-0.35f, 0.35f);
    float nx = x + cosf(a) * 4, ny = y + sinf(a) * 4;
    if (!inCircle(nx, ny, 110)) { G.branchX[bi] = G.branchX[G.branches - 1]; G.branchY[bi] = G.branchY[G.branches - 1]; G.branchA[bi] = G.branchA[G.branches - 1]; G.branches--; bi--; continue; }
    stitch(x, y, nx, ny, 2.6f, C565(86, 110, 64));
    x = nx; y = ny;
    if (frand() < 0.12f) {   // leaf: a short fat satin stroke to one side
      float la = a + (random(2) ? 1.1f : -1.1f); for (int l = 0; l < 4; l++) stitch(x + cosf(la) * 2 + cosf(a) * l, y + sinf(la) * 2 + sinf(a) * l, x + cosf(la) * (10 - fabsf(l - 1.5f) * 2), y + sinf(la) * (10 - fabsf(l - 1.5f) * 2), 1.6f, C565(132, 150, 100));
    }
    if (frand() < 0.04f) { uint16_t fc = palRand(); for (int p = 0; p < 6; p++) knot(x + cosf(p * 1.05f) * 4, y + sinf(p * 1.05f) * 4, 2.2f, fc); knot(x, y, 2.0f, C565(214, 168, 58)); }
    if (frand() < 0.05f && G.branches < 40) { G.branchX[G.branches] = x; G.branchY[G.branches] = y; G.branchA[G.branches] = a + frandr(-1.2f, 1.2f); G.branches++; }
  }
}
// ---- 3 lissajous chain stitch with drifting frequencies
static void initLiss() { fillGround(C565(232, 224, 204), true); G.a = random(1, 5); G.b = random(1, 5); G.c = 0; G.d = frandr(0, 3.14f); G.i = 0; G.pcol = palRand(); }
static void stepLiss() {
  for (int s = 0; s < 4; s++) {
    float t = G.i * 0.045f, t1 = t + 0.045f;
    float ax = G.a + G.c * 0.001f, bx = G.b;
    float x0 = 120 + 84 * sinf(ax * t + G.d), y0 = 120 + 84 * sinf(bx * t), x1 = 120 + 84 * sinf(ax * t1 + G.d), y1 = 120 + 84 * sinf(bx * t1);
    // chain stitch: small loop along the segment
    float mx = (x0 + x1) / 2, my = (y0 + y1) / 2, ang = atan2f(y1 - y0, x1 - x0);
    for (int k = 0; k < 10; k++) { float u = k * 0.628f, v = u + 0.628f; stitch(mx + cosf(ang) * 2.2f * cosf(u) - sinf(ang) * 1.3f * sinf(u), my + sinf(ang) * 2.2f * cosf(u) + cosf(ang) * 1.3f * sinf(u), mx + cosf(ang) * 2.2f * cosf(v) - sinf(ang) * 1.3f * sinf(v), my + sinf(ang) * 2.2f * cosf(v) + cosf(ang) * 1.3f * sinf(v), 1.3f, G.pcol); }
    G.i++; G.c += 1;
  }
  if (G.steps % 12 == 0) fadeToGround(9);
  if (G.i % 700 == 0) { G.pcol = palRand(); if (frand() < 0.5f) G.b = random(1, 6); else G.a = random(1, 6); }
}
// ---- 4 sashiko drift: hitomezashi grid whose rows/cols keep flipping
static void initSash() { fillGround(INDIGO, true); for (int i = 0; i < 64; i++) G.cells[i] = random(2); G.i = 0; }
static void drawSash() {
  const int sp = 12, n = 20; float o = 120 - sp * n / 2.0f;
  for (int j = 0; j <= n; j++) for (int i = 0; i < n; i++) if ((i + G.cells[j]) % 2 == 0) { float x = o + i * sp, y = o + j * sp; if (inCircle(x + sp / 2, y, 112)) stitch(x + 1.5f, y, x + sp - 1.5f, y, 2.0f, CREAM); }
  for (int i = 0; i <= n; i++) for (int j = 0; j < n; j++) if ((j + G.cells[32 + i]) % 2 == 0) { float x = o + i * sp, y = o + j * sp; if (inCircle(x, y + sp / 2, 112)) stitch(x, y + 1.5f, x, y + sp - 1.5f, 2.0f, VERM); }
}
static void stepSash() { if (G.steps % 12 == 0) { G.cells[random(0, 21) + (random(2) ? 32 : 0)] ^= 1; fillGround(INDIGO, true); drawSash(); } }
// ---- 5 drifting patchwork: Voronoi scraps whose seeds wander, seams stitched
static void initPatch() { G.n = random(6, 11); for (int i = 0; i < G.n; i++) { G.px_[i] = frandr(30, 210); G.py_[i] = frandr(30, 210); G.pvx[i] = frandr(-0.5f, 0.5f); G.pvy[i] = frandr(-0.5f, 0.5f); G.pc[i] = PAL[i % 7]; } ground = SOOT; groundShadow = 0; }
static void stepPatch() {
  if (G.steps % 8) return;
  for (int i = 0; i < G.n; i++) { G.px_[i] += G.pvx[i]; G.py_[i] += G.pvy[i]; if (G.px_[i] < 30 || G.px_[i] > 210) G.pvx[i] = -G.pvx[i]; if (G.py_[i] < 30 || G.py_[i] > 210) G.pvy[i] = -G.pvy[i]; }
  for (int y = 0; y < GH; y++) for (int x = 0; x < GW; x++) {
    if (!inCircle(x, y, 121)) { frameBuf[y * GW + x] = 0; continue; }
    float best = 1e9, second = 1e9; int bi = 0;
    for (int i = 0; i < G.n; i++) { float dx = x - G.px_[i], dy = y - G.py_[i], d = dx * dx + dy * dy; if (d < best) { second = best; best = d; bi = i; } else if (d < second) second = d; }
    float edge = sqrtf(second) - sqrtf(best);
    // satin texture: stripes at a per-cell angle; seams as cream running stitch
    float ang = bi * 0.7f; float s = x * cosf(ang) + y * sinf(ang); int stripe = ((int)floorf(s / 1.5f)) & 1;
    uint16_t c = stripe ? G.pc[bi] : shade(G.pc[bi], 0.82f);
    if (edge < 1.4f) c = shade(SOOT, 1.2f); else if (edge < 4.0f && ((int)(x + y) / 6) % 2 == 0) c = CREAM;
    frameBuf[y * GW + x] = c;
  }
}
// ---- 6 generative mandala: rounds of clusters, random counts and colours, outward then reset
static void initMand() { fillGround(SOOT, false); G.i = 1; G.n = random(5, 9); G.pcol = palRand(); G.f = frandr(0, 6.28f); G.e = 0; }
static void stepMand() {
  float ri = 10 + 13 * (G.i - 1), ro = ri + 11; int count = G.n + 5 * G.i;
  int k = (int)G.e;
  if (k < count) {
    float a = 6.2832f * k / count - 1.57f + G.f;
    for (int o = -1; o <= 1; o++) { float aa = a + o * 0.05f * (12.0f / G.i); stitch(120 + ri * cosf(a), 120 + ri * sinf(a), 120 + ro * cosf(aa), 120 + ro * sinf(aa), 2.6f, G.pcol); }
    G.e += 1;
  } else { G.i++; G.e = 0; G.pcol = palRand(); G.f += frandr(-0.2f, 0.2f); if (ro > 110) genComplete = true; }
}
// ---- 7 flow field: short stitches following slowly rotating value noise
static float vnoise(float x, float y) {
  int xi = floorf(x), yi = floorf(y); float fx = x - xi, fy = y - yi;
  auto h = [](int a, int b) { uint32_t v = a * 374761393u + b * 668265263u; v = (v ^ (v >> 13)) * 1274126177u; return (v & 0xFFFF) / 65535.0f; };
  float a = h(xi, yi), b = h(xi + 1, yi), c = h(xi, yi + 1), d = h(xi + 1, yi + 1); fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
  return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy;
}
static void initFlow() { fillGround(C565(232, 224, 204), true); G.a = frandr(0, 100); G.b = frandr(0, 100); G.c = 0; G.pcol = palRand(); }
static void stepFlow() {
  for (int k = 0; k < 6; k++) {
    float x = frandr(10, 230), y = frandr(10, 230); if (!inCircle(x, y, 112)) continue;
    float ang = vnoise(x / 60 + G.a, y / 60 + G.b) * 12.56f + G.c;
    stitch(x, y, x + cosf(ang) * 9, y + sinf(ang) * 9, 1.8f, G.pcol);
  }
  G.c += 0.004f;
  if (G.steps % 20 == 0) fadeToGround(5);
  if (G.steps % 300 == 299) G.pcol = palRand();
}
// ---- 8 phyllotaxis: golden-angle knots growing outward, angle slightly off each cycle
static void initPhyl() { uint16_t g = random(2) ? SOOT : C565(232, 224, 204); fillGround(g, g != SOOT); G.i = 0; G.a = 2.39996f + frandr(-0.03f, 0.03f); G.b = frandr(5.5f, 7.5f); G.col = random(0, 7); }
static void stepPhyl() {
  for (int k = 0; k < 2; k++) {
    float r = G.b * sqrtf((float)G.i), a = G.i * G.a;
    if (r > 108) { genComplete = true; return; }
    knot(120 + r * cosf(a), 120 + r * sinf(a), 2.2f + r / 60, PAL[(G.col + G.i / 40) % 7]); G.i++;
  }
}
// ---- 9 life in cross-stitch: cellular automaton on aida, each live cell a cross
static void initLife() { fillGround(C565(236, 229, 210), true); G.n = 0; for (int i = 0; i < 24 * 24; i++) G.cells[i] = frand() < 0.3f; }
static void stepLife() {
  if (G.steps % 10) return;
  const int N = 24; const float c = 9.5f, o = 120 - c * N / 2;
  fillGround(C565(236, 229, 210), true);
  for (int j = 0; j < N; j++) for (int i = 0; i < N; i++) {
    int cnt = 0; for (int dj = -1; dj <= 1; dj++) for (int di = -1; di <= 1; di++) if (di || dj) cnt += G.cells[((j + dj + N) % N) * N + (i + di + N) % N];
    G.cells2[j * N + i] = G.cells[j * N + i] ? (cnt == 2 || cnt == 3) : (cnt == 3);
    if (G.cells[j * N + i]) { float x = o + i * c, y = o + j * c; if (inCircle(x + c / 2, y + c / 2, 112)) { uint16_t col = PAL[(i / 6 + j / 6) % 7]; stitch(x + 1.5f, y + c - 1.5f, x + c - 1.5f, y + 1.5f, 1.8f, col); stitch(x + 1.5f, y + 1.5f, x + c - 1.5f, y + c - 1.5f, 1.8f, col); } }
  }
  int alive = 0; for (int i = 0; i < N * N; i++) { G.cells[i] = G.cells2[i]; alive += G.cells[i]; }
  if (alive < 12 || G.steps % 1200 == 0) for (int i = 0; i < N * N; i++) G.cells[i] = frand() < 0.3f;
}


// ---- 10/11 generative granny: crochet a fresh square (or triangle/hexagon/circle) each time
struct Granny { int sides, rounds, n, s, k, p, holdSteps; float step, inner0, skew, wobble; uint16_t pal[8]; bool done; } GR;
static void yarnSeg(float x0, float y0, float x1, float y1, float w, uint16_t c) {
  stitch(x0, y0, x1, y1, w, c);
  float dx = x1 - x0, dy = y1 - y0, L = sqrtf(dx * dx + dy * dy); if (L < 1) return; dx /= L; dy /= L;
  for (float t = w * 0.6f; t < L; t += w * 0.75f) thick(x0 + dx * t - dy * w * 0.3f - dx * w * 0.2f, y0 + dy * t + dx * w * 0.3f - dy * w * 0.2f, x0 + dx * t + dy * w * 0.3f + dx * w * 0.2f, y0 + dy * t - dx * w * 0.3f + dy * w * 0.2f, 0.7f, shade(c, 0.62f));
}
static void post(float bx, float by, float tx, float ty, uint16_t c) {
  float mx = (bx + tx) / 2, my = (by + ty) / 2, dx = tx - bx, dy = ty - by, L = sqrtf(dx * dx + dy * dy) + 0.01f; float nx = -dy / L, ny = dx / L;
  yarnSeg(bx, by, mx + nx * 0.9f, my + ny * 0.9f, 3.0f, c); yarnSeg(mx + nx * 0.9f, my + ny * 0.9f, tx, ty, 3.0f, c);
}
static void grannyNew(bool shapes) {
  fillGround(SOOT, false);
  GR.sides = shapes ? (int[]){3, 4, 6, 0}[random(0, 4)] : 4;
  GR.rounds = GR.sides == 3 ? random(3, 5) : (GR.sides == 0 ? random(5, 8) : random(4, 6));
  GR.step = GR.sides == 0 ? 13 : (GR.sides == 3 ? 20 : 13); GR.inner0 = GR.sides == 3 ? 12 : 10;
  GR.skew = frandr(-0.12f, 0.12f); GR.wobble = shapes ? frandr(0, 1.2f) : 0;
  int start = random(0, 7); for (int i = 0; i < 8; i++) GR.pal[i] = PAL[(start + i * (1 + random(0, 2))) % 7];
  if (frand() < 0.3f) GR.pal[GR.rounds] = CREAM;   // cream border round, sometimes
  GR.n = 1; GR.s = 0; GR.k = 0; GR.p = 0; GR.done = false; GR.holdSteps = 0;
  // centre ring
  for (int i = 0; i < 16; i++) { float a0 = i * 0.3927f, a1 = a0 + 0.3927f; yarnSeg(120 + 7 * cosf(a0), 120 + 7 * sinf(a0), 120 + 7 * cosf(a1), 120 + 7 * sinf(a1), 3.0f, GR.pal[0]); }
}
static void T(float x, float y, float rot, float &ox, float &oy) { ox = 120 + x * cosf(rot) - y * sinf(rot); oy = 120 + x * sinf(rot) + y * cosf(rot); }
static void grannyStep(bool shapes) {
  if (GR.done) { genComplete = true; return; }
  uint16_t col = GR.pal[GR.n % 8];
  if (GR.sides == 0) {   // circular rounds
    float ri = GR.inner0 + GR.step * (GR.n - 1), ro = ri + GR.step - 2; int count = 6 + 5 * GR.n;
    float a = 6.2832f * GR.k / count - 1.5708f + GR.skew;
    if (GR.p < 3) { float aa = a + (GR.p - 1) * 0.045f * (12.0f / GR.n); post(120 + ri * cosf(a), 120 + ri * sinf(a), 120 + ro * cosf(aa), 120 + ro * sinf(aa), col); GR.p++; }
    else { float an = 6.2832f * (GR.k + 1) / count - 1.5708f + GR.skew, m = (a + an) / 2, o = 0.045f * 12.0f / GR.n;
           yarnSeg(120 + ro * cosf(a + o), 120 + ro * sinf(a + o), 120 + (ro + 1.5f) * cosf(m), 120 + (ro + 1.5f) * sinf(m), 2.4f, col); yarnSeg(120 + (ro + 1.5f) * cosf(m), 120 + (ro + 1.5f) * sinf(m), 120 + ro * cosf(an - o), 120 + ro * sinf(an - o), 2.4f, col);
           GR.p = 0; if (++GR.k >= count) { GR.k = 0; if (++GR.n > GR.rounds) GR.done = true; } }
    return;
  }
  float half = 3.14159f / GR.sides, hi = GR.inner0 + GR.step * (GR.n - 1), ho = hi + GR.step - 2, hs = hi * tanf(half);
  int per = max(1, (int)roundf(2 * hs / 11.5f)); float rot = 6.2832f * GR.s / GR.sides + GR.skew;
  float x = -hs + 2 * hs * (GR.k + 0.5f) / per + frandr(-GR.wobble, GR.wobble) * 0.3f;
  float bx, by, tx, ty;
  if (GR.p < 3) { T(x, -hi + 1, rot, bx, by); T(x + (GR.p - 1) * 3.6f, -ho - frandr(0, GR.wobble), rot, tx, ty); post(bx, by, tx, ty, col); GR.p++; return; }
  if (GR.k < per - 1) {   // chain-1 to the next cluster on this side
    float xn = -hs + 2 * hs * (GR.k + 1.5f) / per; float ax, ay, mx, my, cx, cy;
    T(x + 3.6f, -ho, rot, ax, ay); T((x + xn) / 2, -ho - 1.5f, rot, mx, my); T(xn - 3.6f, -ho, rot, cx, cy);
    yarnSeg(ax, ay, mx, my, 2.4f, col); yarnSeg(mx, my, cx, cy, 2.4f, col);
  } else {                // corner chain-2 to the next side
    float rot2 = 6.2832f * (GR.s + 1) / GR.sides + GR.skew, xf = -hs + 2 * hs * 0.5f / per; float ax, ay, cx, cy;
    T(x + 3.6f, -ho, rot, ax, ay); T(xf - 3.6f, -ho, rot2, cx, cy);
    float cr = ho / cosf(half) + 1.5f, ac = rot + half - 1.5708f; float mx = 120 + cr * cosf(ac), my = 120 + cr * sinf(ac);
    yarnSeg(ax, ay, mx, my, 2.4f, col); yarnSeg(mx, my, cx, cy, 2.4f, col);
  }
  GR.p = 0;
  if (++GR.k >= per) { GR.k = 0; if (++GR.s >= GR.sides) { GR.s = 0; if (++GR.n > GR.rounds) GR.done = true; } }
}


// ---- 12..21 growing florals: stems climb and branch, flowers bloom petal by petal, then the bed fades and regrows
struct Tip { float x, y, a; int age; bool alive; };
struct Flower { float x, y, size, rot; int type, stage; uint16_t col; bool alive; };
struct Flora { int kind; bool dark; Tip tips[20]; int ntips; Flower fl[48]; int nfl; int quiet; uint16_t stem, leaf; } FL;
static const uint16_t FLOWER_COLS[] = {C565(196, 60, 72), C565(236, 150, 160), C565(214, 168, 58), C565(238, 230, 210), C565(150, 110, 190), C565(200, 90, 120), C565(72, 132, 170)};
static void addTip(float x, float y, float a) { if (FL.ntips < 20) { FL.tips[FL.ntips++] = {x, y, a, 0, true}; } }
static void addGroundTip(float x) { float dy = sqrtf(fmaxf(0.0f, 110.0f * 110.0f - (x - 120) * (x - 120))); addTip(x, 120 + dy - 2, -1.5708f + frandr(-0.4f, 0.4f)); }
static void addFlower(float x, float y, int type, float size, uint16_t col) { if (FL.nfl < 48) FL.fl[FL.nfl++] = {x, y, size, frandr(0, 6.28f), type, 0, col, true}; }
static void leafStroke(float x, float y, float a, float len, float w, uint16_t c) {
  for (int l = 0; l < 4; l++) { float t = l / 3.0f, half = w * sinf(t * 3.14159f) + 0.3f, px = x + cosf(a) * len * t, py = y + sinf(a) * len * t; stitch(px - sinf(a) * half, py + cosf(a) * half, px + sinf(a) * half, py - cosf(a) * half, 1.5f, c); }
  stitch(x, y, x + cosf(a) * len, y + sinf(a) * len, 0.9f, shade(c, 0.6f));
}
static void floraInit(int k) {
  FL.kind = k / 2; FL.dark = k & 1;
  uint16_t g = FL.dark ? SOOT : C565(232, 224, 204); fillGround(g, !FL.dark);
  FL.stem = FL.dark ? C565(120, 150, 96) : C565(86, 110, 64); FL.leaf = FL.dark ? C565(150, 180, 110) : C565(126, 150, 92);
  FL.ntips = 0; FL.nfl = 0; FL.quiet = 0;
  int n = FL.kind == 4 ? 3 : random(2, 5);
  for (int i = 0; i < n; i++) { if (FL.kind == 3) addTip(frandr(60, 180), frandr(60, 180), frandr(-0.6f, 0.6f) + (random(2) ? 0 : 3.14f)); else addGroundTip(frandr(40, 200)); }
}
// one flower stage; returns false when finished
static bool bloom(Flower &f) {
  float x = f.x, y = f.y, s = f.size;
  switch (f.type) {
    case 0: { // rose: yarn spiral, 14 stages
      float th0 = f.stage * 0.55f, th1 = th0 + 0.55f, r0 = 1 + s * th0 / 7.7f, r1 = 1 + s * th1 / 7.7f;
      stitch(x + r0 * cosf(th0 + f.rot), y + r0 * sinf(th0 + f.rot), x + r1 * cosf(th1 + f.rot), y + r1 * sinf(th1 + f.rot), 2.8f, shade(f.col, 0.75f + 0.5f * f.stage / 14.0f));
      return ++f.stage < 14; }
    case 1: { // daisy: 8 lazy-daisy petals then knot centre
      if (f.stage < 8) { float a = f.rot + f.stage * 0.785f; for (int k = 0; k < 8; k++) { float u = k * 0.785f, v = u + 0.785f, px = x + cosf(a) * s * 0.55f, py = y + sinf(a) * s * 0.55f;
          stitch(px + cosf(a) * s * 0.5f * cosf(u) - sinf(a) * s * 0.2f * sinf(u), py + sinf(a) * s * 0.5f * cosf(u) + cosf(a) * s * 0.2f * sinf(u), px + cosf(a) * s * 0.5f * cosf(v) - sinf(a) * s * 0.2f * sinf(v), py + sinf(a) * s * 0.5f * cosf(v) + cosf(a) * s * 0.2f * sinf(v), 1.5f, f.col); } }
      else for (int k = 0; k < 5; k++) knot(x + cosf(k * 1.26f) * 1.6f, y + sinf(k * 1.26f) * 1.6f, 1.5f, C565(214, 168, 58));
      return ++f.stage < 9; }
    case 2: { // lavender: knots climbing a short spike
      float a = f.rot; float px = x + cosf(a) * f.stage * 2.6f, py = y + sinf(a) * f.stage * 2.6f;
      knot(px - sinf(a) * 2.2f, py + cosf(a) * 2.2f, 2.0f, f.col); knot(px + sinf(a) * 2.2f, py - cosf(a) * 2.2f, 2.0f, shade(f.col, 1.15f)); if (f.stage % 2) knot(px, py, 1.6f, shade(f.col, 0.85f));
      return ++f.stage < (int)(s / 2.6f); }
    case 3: { // blossom: 5 satin petals then centre
      if (f.stage < 5) { float a = f.rot + f.stage * 1.2566f; for (int l = 0; l < 5; l++) { float t = 0.25f + 0.75f * l / 4.0f, half = s * 0.28f * sinf((l + 1) / 6.0f * 3.14f); float px = x + cosf(a) * s * t, py = y + sinf(a) * s * t; stitch(px - sinf(a) * half, py + cosf(a) * half, px + sinf(a) * half, py - cosf(a) * half, 1.6f, l == 0 ? shade(f.col, 0.85f) : f.col); } }
      else for (int k = 0; k < 6; k++) knot(x + cosf(k * 1.05f) * 1.8f, y + sinf(k * 1.05f) * 1.8f, 1.3f, C565(214, 168, 58));
      return ++f.stage < 6; }
  }
  return false;
}
static void floraStep() {
  int alive = 0;
  for (int i = 0; i < FL.ntips; i++) {
    Tip &t = FL.tips[i]; if (!t.alive) continue; alive++;
    float up = FL.kind == 3 ? 0.0f : -1.5708f;                       // blossom branches wander sideways
    float turn = FL.kind == 4 ? 0.09f : frandr(-0.3f, 0.3f);           // ferns curl steadily
    if (FL.kind != 3 && FL.kind != 4) t.a += turn + (up - t.a) * 0.06f; else if (FL.kind == 3) t.a += frandr(-0.25f, 0.25f); else t.a += turn * (t.age < 40 ? 1 : 0.2f) + frandr(-0.05f, 0.05f);
    float nx = t.x + cosf(t.a) * 3.2f, ny = t.y + sinf(t.a) * 3.2f;
    if (!inCircle(nx, ny, 112) || t.age > (FL.kind == 4 ? 90 : 140)) { t.alive = false; if (t.age > 8 && (FL.kind == 0 || FL.kind == 1 || FL.kind == 3)) addFlower(t.x, t.y, FL.kind, frandr(7, 13), FLOWER_COLS[random(0, 7)]); continue; }
    stitch(t.x, t.y, nx, ny, FL.kind == 3 ? 3.0f : 2.2f, FL.kind == 3 ? C565(92, 62, 40) : FL.stem);
    t.x = nx; t.y = ny; t.age++;
    if (FL.kind == 4) { if (t.age % 3 == 0) { float side = (t.age / 3) % 2 ? 1.1f : -1.1f; leafStroke(t.x, t.y, t.a + side, 6 + 10 * (1 - t.age / 90.0f), 1.6f, FL.leaf); } }
    else if (frand() < 0.10f) leafStroke(t.x, t.y, t.a + (random(2) ? 0.9f : -0.9f), frandr(7, 12), 2.2f, FL.leaf);
    if (FL.kind == 2 && t.age > 20 && frand() < 0.04f) { addFlower(t.x, t.y, 2, frandr(14, 28), FLOWER_COLS[4 + random(0, 2)]); t.alive = false; }
    if (FL.kind == 3 && frand() < 0.08f) addFlower(t.x + frandr(-6, 6), t.y + frandr(-6, 6), 3, frandr(6, 10), FLOWER_COLS[random(2) ? 1 : 5]);
    if ((FL.kind == 0 || FL.kind == 1) && t.age > 15 && frand() < 0.03f) addFlower(t.x, t.y, FL.kind, frandr(6, 12), FLOWER_COLS[random(0, 7)]);
    if (frand() < (FL.kind == 3 ? 0.05f : 0.03f) && FL.ntips < 20) addTip(t.x, t.y, t.a + frandr(-1.0f, 1.0f));
  }
  int blooming = 0;
  for (int i = 0; i < FL.nfl; i++) if (FL.fl[i].alive) { blooming++; if (!bloom(FL.fl[i])) FL.fl[i].alive = false; if (blooming >= 3) break; }
  if (alive == 0 && blooming == 0) {
    if (++FL.quiet > 40) genComplete = true;
    else if (FL.quiet == 1 && FL.ntips < 20 && frand() < 0.7f) { FL.quiet = 0; if (FL.kind == 3) addTip(frandr(60, 180), frandr(60, 180), frandr(-0.6f, 0.6f)); else addGroundTip(frandr(40, 200)); }
  }
}


// ---- 22..31 Asawa wire forms: looped-wire lattices crocheted ring by ring, forms within forms, tied-wire stars
struct Lobe { float c, r, s; };
struct Form { Lobe lobes[6]; int nl; float y0, y1, squash; int meridians; uint16_t col; float w; };
struct Asawa { int kind; bool dark; Form forms[5]; int nf, f; float y, lastY; int hold; bool done;
               float bx[160], by[160], ba[160], bl[160]; int nb, bdepth, bcur, bnext; uint16_t wire; } AS;
static float profileR(const Form &F, float y) { float r = 0; for (int i = 0; i < F.nl; i++) { float d = (y - F.lobes[i].c) / F.lobes[i].s; r += F.lobes[i].r * expf(-d * d); } return r; }
static uint16_t asawaCol(int i) { return AS.dark ? (i == 0 ? C565(246, 246, 242) : C565(214, 214, 208)) : PAL[(i * 2 + 1) % 7]; }
static float wireW(float w) { return AS.dark ? w * 1.35f : w; }
static void ringAt(const Form &F, float y, float scale, uint16_t col, float w) {
  float R = profileR(F, y) * scale; if (R < 1.5f) return; float rz = R * F.squash;
  for (int k = 0; k < 28; k++) { float a0 = k * 0.2244f, a1 = a0 + 0.2244f; stitch(120 + R * cosf(a0), y + rz * sinf(a0), 120 + R * cosf(a1), y + rz * sinf(a1), wireW(w), k < 14 ? shade(col, 0.82f) : col); }
}
static void meridians(const Form &F, float ya, float yb, float scale, uint16_t col, float w) {
  float Ra = profileR(F, ya) * scale, Rb = profileR(F, yb) * scale;
  for (int m = 0; m < F.meridians; m++) { float a = 6.2832f * m / F.meridians; bool back = sinf(a) < 0;
    stitch(120 + Ra * cosf(a), ya + Ra * F.squash * sinf(a), 120 + Rb * cosf(a), yb + Rb * F.squash * sinf(a), wireW(w), back ? shade(col, 0.76f) : col); }
}
static void asawaNew(int k) {
  AS.kind = k / 2; AS.dark = k & 1; uint16_t g = AS.dark ? SOOT : C565(232, 224, 204); fillGround(g, !AS.dark);
  AS.nf = 0; AS.f = 0; AS.hold = 0; AS.done = false; AS.nb = 0;
  auto addForm = [](int nl, float yTop, float yBot, float rMin, float rMax, float squash, int mer, uint16_t col, float w) {
    Form &F = AS.forms[AS.nf++]; F.nl = nl; F.y0 = yTop; F.y1 = yBot; F.squash = squash; F.meridians = mer; F.col = col; F.w = w;
    for (int i = 0; i < nl; i++) { F.lobes[i].c = yTop + (yBot - yTop) * (i + 0.5f) / nl; F.lobes[i].r = frandr(rMin, rMax); F.lobes[i].s = (yBot - yTop) / nl * frandr(0.42f, 0.55f); } };
  switch (AS.kind) {
    case 0: { int nl = random(2, 5); addForm(nl, 26, 226, 34, 62, 0.26f, random(14, 22), asawaCol(0), 1.3f);          // stacked lobes with an inner form in each lobe
              Form &O = AS.forms[0]; for (int i = 0; i < nl && AS.nf < 5; i++) { Form &I = AS.forms[AS.nf++]; I = O; I.nl = 1; I.lobes[0] = O.lobes[i]; I.lobes[0].r *= frandr(0.42f, 0.55f); I.lobes[0].s *= 0.7f; I.y0 = I.lobes[0].c - I.lobes[0].s * 1.8f; I.y1 = I.lobes[0].c + I.lobes[0].s * 1.8f; I.col = asawaCol(1 + i); I.meridians = 10; I.w = 1.1f; } break; }
    case 1: { int n = random(3, 5); for (int i = 0; i < n; i++) { float sc = 1 - i * (0.8f / n); addForm(1, 120 - 100 * sc, 120 + 100 * sc, 92 * sc, 98 * sc, 0.3f, 18 - i * 2, asawaCol(i), 1.3f - i * 0.1f); AS.forms[i].lobes[0].s = 100 * sc * 0.62f; } break; }   // nested spheres
    case 3: { addForm(random(4, 7), 14, 232, 16, 34, 0.24f, random(10, 14), asawaCol(0), 1.2f); break; }                 // hourglass column
    case 4: { addForm(random(1, 3), 30, 222, 46, 72, 0.28f, random(12, 16), asawaCol(0), 1.3f); break; }                 // loop vessel
    default: {                                                                                                             // tied wire: dichotomous branching star
      AS.wire = AS.dark ? C565(246, 246, 242) : PAL[random(0, 7)]; int spokes = random(5, 9); AS.bdepth = random(4, 6); AS.nb = 0; AS.bcur = 0;
      for (int i = 0; i < spokes; i++) { AS.bx[AS.nb] = 120; AS.by[AS.nb] = 120; AS.ba[AS.nb] = 6.2832f * i / spokes + frandr(-0.1f, 0.1f); AS.bl[AS.nb] = frandr(30, 42); AS.nb++; }
      AS.bnext = AS.nb; AS.f = 0; break; }
  }
  AS.y = AS.forms[0].y0; AS.lastY = AS.y;
  if (AS.kind != 2) stitch(120, 0, 120, AS.forms[0].y0, 1.1f, asawaCol(0));   // hanging wire
}
static void asawaStep() {
  if (AS.done) { genComplete = true; return; }
  if (AS.kind == 2) {   // grow one generation of branches per few steps
    if (AS.bcur >= AS.bnext) { if (AS.f >= AS.bdepth || AS.nb >= 150) { AS.done = true; return; } AS.f++; AS.bcur = AS.bnext; AS.bnext = AS.nb; }
    // draw one branch, then spawn its children
    int i = AS.bcur++; float ex = AS.bx[i] + cosf(AS.ba[i]) * AS.bl[i], ey = AS.by[i] + sinf(AS.ba[i]) * AS.bl[i];
    if (!inCircle(ex, ey, 114)) return;
    stitch(AS.bx[i], AS.by[i], ex, ey, wireW(1.7f - AS.f * 0.14f), AS.wire); knot(ex, ey, 1.4f, shade(AS.wire, 0.85f));
    int kids = frand() < 0.75f ? 2 : 3;
    for (int k = 0; k < kids && AS.nb < 160; k++) { AS.bx[AS.nb] = ex; AS.by[AS.nb] = ey; AS.ba[AS.nb] = AS.ba[i] + (k - (kids - 1) / 2.0f) * frandr(0.45f, 0.7f); AS.bl[AS.nb] = AS.bl[i] * frandr(0.62f, 0.78f); AS.nb++; }
    return;
  }
  Form &F = AS.forms[AS.f]; float sc = 1;
  if (AS.kind == 4) {      // explicit crocheted loops instead of a lattice
    float R = profileR(F, AS.y), rz = R * F.squash; int M = max(6, (int)(R / 5));
    for (int m = 0; m < M; m++) { float a = 6.2832f * (m + ((int)(AS.y / 8) % 2) * 0.5f) / M; float cx = 120 + R * cosf(a), cy = AS.y + rz * sinf(a); uint16_t c = sinf(a) < 0 ? shade(F.col, 0.72f) : F.col;
      for (int k = 0; k < 8; k++) { float u = k * 0.785f, v = u + 0.785f; stitch(cx + 3.4f * cosf(u) * cosf(a) * 0.6f - 0 , cy + 4.2f * sinf(u), cx + 3.4f * cosf(v) * cosf(a) * 0.6f, cy + 4.2f * sinf(v), wireW(1.3f), c); } }
    AS.y += 7;
  } else {
    ringAt(F, AS.y, sc, F.col, F.w); if (AS.y > F.y0) meridians(F, AS.lastY, AS.y, sc, F.col, F.w * 0.9f); AS.lastY = AS.y; AS.y += 8;
  }
  if (AS.y > F.y1) { AS.f++; if (AS.f >= AS.nf) AS.done = true; else { AS.y = AS.forms[AS.f].y0; AS.lastY = AS.y; } }
}


// ---- 32..41 core generative techniques, stitched
static uint16_t randGround() { uint16_t g = random(2) ? SOOT : C565(232, 224, 204); fillGround(g, g != SOOT); return g; }
static uint16_t threadFor(uint16_t g) { return g == SOOT ? (random(3) ? palRand() : CREAM) : palRand(); }

// 32 reaction-diffusion (Gray-Scott) on a 60x60 grid, high-V cells become knots
struct RD { float U[3600], V[3600]; float f, k; uint16_t col; } RDs;
static void initTuring() { uint16_t g = randGround(); RDs.col = threadFor(g); RDs.f = frandr(0.030f, 0.055f); RDs.k = frandr(0.059f, 0.064f);
  for (int i = 0; i < 3600; i++) { RDs.U[i] = 1; RDs.V[i] = 0; } for (int n = 0; n < 12; n++) { int cx = random(10, 50), cy = random(10, 50); for (int y = -2; y <= 2; y++) for (int x = -2; x <= 2; x++) RDs.V[(cy + y) * 60 + cx + x] = 1; } }
static void stepTuring() {
  for (int it = 0; it < 6; it++) {
    static float nU[3600], nV[3600];
    for (int y = 0; y < 60; y++) for (int x = 0; x < 60; x++) { int i = y * 60 + x; int l = y * 60 + (x + 59) % 60, r = y * 60 + (x + 1) % 60, u = ((y + 59) % 60) * 60 + x, d = ((y + 1) % 60) * 60 + x;
      float lu = RDs.U[l] + RDs.U[r] + RDs.U[u] + RDs.U[d] - 4 * RDs.U[i], lv = RDs.V[l] + RDs.V[r] + RDs.V[u] + RDs.V[d] - 4 * RDs.V[i]; float uvv = RDs.U[i] * RDs.V[i] * RDs.V[i];
      nU[i] = constrain(RDs.U[i] + 0.19f * lu - uvv + RDs.f * (1 - RDs.U[i]), 0.0f, 1.0f); nV[i] = constrain(RDs.V[i] + 0.09f * lv + uvv - (RDs.f + RDs.k) * RDs.V[i], 0.0f, 1.0f); }
    memcpy(RDs.U, nU, sizeof nU); memcpy(RDs.V, nV, sizeof nV);
  }
  if (G.steps % 3) return;
  fillGround(ground, ground != SOOT);
  for (int y = 0; y < 60; y++) for (int x = 0; x < 60; x++) { float v = RDs.V[y * 60 + x]; float px_ = x * 4 + 2, py_ = y * 4 + 2; if (v > 0.25f && inCircle(px_, py_, 114)) knot(px_, py_, 1.2f + v * 2.2f, shade(RDs.col, 0.8f + v * 0.5f)); }
  if (G.steps > 700) genComplete = true;
}
// 33 Truchet tiles: quarter-arc tiles, random flips rippling through
static uint8_t TR[64];
static void drawTruchetTile(int i, int j, uint16_t col) { const float c = 30; float x = i * c, y = j * c; bool f = TR[j * 8 + i];
  for (int k = 0; k < 10; k++) { float a0 = k * 0.157f, a1 = a0 + 0.157f; float cx0 = f ? x : x + c, cy0 = y, cx1 = f ? x + c : x, cy1 = y + c; float s0 = f ? 0 : 1.5708f, s1 = f ? 3.1416f : 4.7124f;
    stitch(cx0 + c / 2 * cosf(s0 + a0), cy0 + c / 2 * sinf(s0 + a0), cx0 + c / 2 * cosf(s0 + a1), cy0 + c / 2 * sinf(s0 + a1), 2.4f, col);
    stitch(cx1 + c / 2 * cosf(s1 + a0), cy1 + c / 2 * sinf(s1 + a0), cx1 + c / 2 * cosf(s1 + a1), cy1 + c / 2 * sinf(s1 + a1), 2.4f, col); } }
static void initTruchet() { uint16_t g = randGround(); G.pcol = threadFor(g); for (int i = 0; i < 64; i++) TR[i] = random(2); for (int j = 0; j < 8; j++) for (int i = 0; i < 8; i++) drawTruchetTile(i, j, G.pcol); }
static void stepTruchet() { if (G.steps % 6) return; int i = random(0, 8), j = random(0, 8); TR[j * 8 + i] ^= 1;
  // redraw the tile's square with ground then arcs (neighbours' arcs end at tile edges so nothing else is disturbed)
  for (int y = j * 30; y < j * 30 + 30; y++) for (int x = i * 30; x < i * 30 + 30; x++) if (inCircle(x, y, 121)) frameBuf[y * GW + x] = ground;
  drawTruchetTile(i, j, G.pcol); if (G.steps % 600 == 0) G.pcol = threadFor(ground); }
// 34 flocking: boids leave thread trails
struct Boid { float x, y, vx, vy; uint16_t c; } BD[26];
static void initFlock() { uint16_t g = randGround(); for (auto &b : BD) { b.x = frandr(60, 180); b.y = frandr(60, 180); float a = frandr(0, 6.28f); b.vx = cosf(a) * 2; b.vy = sinf(a) * 2; b.c = threadFor(g); } }
static void stepFlock() {
  for (auto &b : BD) { float cx = 0, cy = 0, ax = 0, ay = 0, sx = 0, sy = 0; int n = 0;
    for (auto &o : BD) { if (&o == &b) continue; float dx = o.x - b.x, dy = o.y - b.y, d2 = dx * dx + dy * dy; if (d2 < 1600) { cx += o.x; cy += o.y; ax += o.vx; ay += o.vy; n++; if (d2 < 120) { sx -= dx; sy -= dy; } } }
    if (n) { b.vx += ((cx / n - b.x) * 0.004f + (ax / n - b.vx) * 0.05f + sx * 0.03f); b.vy += ((cy / n - b.y) * 0.004f + (ay / n - b.vy) * 0.05f + sy * 0.03f); }
    float dx = 120 - b.x, dy = 120 - b.y, d = sqrtf(dx * dx + dy * dy); if (d > 90) { b.vx += dx / d * 0.12f; b.vy += dy / d * 0.12f; }
    float sp = sqrtf(b.vx * b.vx + b.vy * b.vy); if (sp > 2.4f) { b.vx *= 2.4f / sp; b.vy *= 2.4f / sp; } if (sp < 1.2f) { b.vx *= 1.3f; b.vy *= 1.3f; }
    float nx = b.x + b.vx, ny = b.y + b.vy; if (inCircle(nx, ny, 112)) stitch(b.x, b.y, nx, ny, 1.6f, b.c); b.x = nx; b.y = ny; }
  if (G.steps % 6 == 0) fadeToGround(7);
}
// 35 diffusion-limited aggregation: walkers stick to a growing crystal of knots
static uint8_t OCC[GW * GH / 8];
static inline bool occ(int x, int y) { return (unsigned)x < GW && (unsigned)y < GH && (OCC[(y * GW + x) >> 3] >> (x & 7)) & 1; }
static inline void setOcc(int x, int y) { OCC[(y * GW + x) >> 3] |= 1 << (x & 7); }
static void initDLA() { uint16_t g = randGround(); G.pcol = threadFor(g); memset(OCC, 0, sizeof OCC); int seeds = random(1, 4); G.a = 6; for (int i = 0; i < seeds; i++) { int x = 120 + random(-30, 31), y = 120 + random(-30, 31); setOcc(x, y); knot(x, y, 2.2f, G.pcol); G.a = max(G.a, sqrtf((x - 120.f) * (x - 120.f) + (y - 120.f) * (y - 120.f)) + 6); } G.i = 0; }
static void stepDLA() {
  for (int w = 0; w < 10; w++) { float a = frandr(0, 6.28f), sr = min(108.0f, G.a + 4); int x = 120 + sr * cosf(a), y = 120 + sr * sinf(a);
    for (int t = 0; t < 2500; t++) { x += random(-1, 2); y += random(-1, 2); if (!inCircle(x, y, min(110.0f, G.a + 14))) { a = frandr(0, 6.28f); x = 120 + sr * cosf(a); y = 120 + sr * sinf(a); }
      if (occ(x + 1, y) || occ(x - 1, y) || occ(x, y + 1) || occ(x, y - 1)) { setOcc(x, y); float d = sqrtf((x - 120.f) * (x - 120.f) + (y - 120.f) * (y - 120.f)); knot(x, y, 1.6f + (d > 60 ? 0.6f : 0), shade(G.pcol, 0.75f + d / 200)); G.a = max(G.a, d + 6); G.i++; break; } } }
  if (G.i > 2200 || G.a > 112) genComplete = true;
}
// 36 circle packing: stitched rings packed until the disc is full
struct Circ { float x, y, r; } CP[140]; static int ncp;
static void initPack() { uint16_t g = randGround(); ncp = 0; G.col = random(0, 7); }
static void stepPack() {
  for (int tries = 0; tries < 40 && ncp < 140; tries++) { float a = frandr(0, 6.28f), rr = sqrtf(frand()) * 106; float x = 120 + rr * cosf(a), y = 120 + rr * sinf(a); float r = 110 - rr;
    for (int i = 0; i < ncp; i++) { float d = sqrtf((x - CP[i].x) * (x - CP[i].x) + (y - CP[i].y) * (y - CP[i].y)) - CP[i].r; r = min(r, d); }
    if (r < 3.5f) continue; r = min(r, frandr(10, 34)) - 1.2f; CP[ncp++] = {x, y, r};
    uint16_t c = PAL[(G.col + ncp) % 7]; int segs = max(10, (int)(r * 1.3f));
    for (int k = 0; k < segs; k++) { float a0 = 6.2832f * k / segs, a1 = a0 + 6.2832f / segs; stitch(x + r * cosf(a0), y + r * sinf(a0), x + r * cosf(a1), y + r * sinf(a1), r > 14 ? 2.6f : 1.8f, c); }
    if (r > 9) for (int k = 0; k < segs / 2; k++) { float a0 = 6.2832f * k / (segs / 2), a1 = a0 + 6.2832f / (segs / 2); stitch(x + r * 0.55f * cosf(a0), y + r * 0.55f * sinf(a0), x + r * 0.55f * cosf(a1), y + r * 0.55f * sinf(a1), 1.6f, shade(c, 0.8f)); }
    if (r <= 9) knot(x, y, r * 0.45f, shade(c, 1.1f));
    break; }
  if (ncp >= 140 || G.steps > 600) genComplete = true;
}
// 37 recursive subdivision: a quilt that keeps re-splitting itself
struct Rect { float x, y, w, h; } RQ[40]; static int nrq;
static void drawRect(const Rect &R, uint16_t c) { float ang = random(2) ? 45 : 135; float ca = cosf(ang * 0.01745f), sa = sinf(ang * 0.01745f);
  for (int y = R.y; y < R.y + R.h; y++) for (int x = R.x; x < R.x + R.w; x++) if (inCircle(x, y, 118)) { float sdist = x * ca + y * sa; int stripe = ((int)floorf(sdist / 1.6f)) & 1; px(x, y, stripe ? c : shade(c, 0.84f)); }
  float x1 = R.x + R.w, y1 = R.y + R.h; dashes(R.x, R.y, x1, R.y, 4, 2.5f, 1.4f, CREAM); dashes(x1, R.y, x1, y1, 4, 2.5f, 1.4f, CREAM); dashes(x1, y1, R.x, y1, 4, 2.5f, 1.4f, CREAM); dashes(R.x, y1, R.x, R.y, 4, 2.5f, 1.4f, CREAM); }
static void initSub() { fillGround(SOOT, false); nrq = 1; RQ[0] = {0, 0, 240, 240}; drawRect(RQ[0], palRand()); }
static void stepSub() { if (G.steps % 14) return;
  if (nrq >= 36) { genComplete = true; return; }
  int i = random(0, nrq); Rect R = RQ[i]; if (R.w < 40 && R.h < 40) return; bool vert = R.w > R.h ? true : (R.h > R.w ? false : random(2)); float t = frandr(0.35f, 0.65f);
  Rect A = R, B = R; if (vert) { A.w = R.w * t; B.x = R.x + A.w; B.w = R.w - A.w; } else { A.h = R.h * t; B.y = R.y + A.h; B.h = R.h - A.h; }
  RQ[i] = A; RQ[nrq++] = B; drawRect(A, palRand()); drawRect(B, palRand()); }
// 38 noise contours: marching-squares topography that slowly drifts
static void initContours() { uint16_t g = randGround(); G.pcol = threadFor(g); G.a = frandr(0, 50); G.b = frandr(0, 50); G.c = 0; }
static void stepContours() { if (G.steps % 4) return;
  fillGround(ground, ground != SOOT); const int N = 40; const float cs = 240.0f / N; static float F[41 * 41];
  for (int j = 0; j <= N; j++) for (int i = 0; i <= N; i++) F[j * 41 + i] = vnoise(i * cs / 70 + G.a, j * cs / 70 + G.b + G.c) + 0.5f * vnoise(i * cs / 30 + G.a * 2, j * cs / 30 + G.b);
  for (int lv = 0; lv < 7; lv++) { float iso = 0.25f + lv * 0.17f; uint16_t c = lv % 2 ? G.pcol : shade(G.pcol, 0.8f);
    for (int j = 0; j < N; j++) for (int i = 0; i < N; i++) { float a = F[j * 41 + i], b = F[j * 41 + i + 1], cc = F[(j + 1) * 41 + i + 1], d = F[(j + 1) * 41 + i]; int code = (a > iso) | (b > iso) << 1 | (cc > iso) << 2 | (d > iso) << 3; if (code == 0 || code == 15) continue;
      float x0 = i * cs, y0 = j * cs; auto lerp = [&](float p, float q) { return (iso - p) / (q - p + 1e-6f); };
      float ex[4][2] = {{x0 + cs * lerp(a, b), y0}, {x0 + cs, y0 + cs * lerp(b, cc)}, {x0 + cs * lerp(d, cc), y0 + cs}, {x0, y0 + cs * lerp(a, d)}};
      static const int8_t tbl[16][4] = {{-1},{3,0,-1},{0,1,-1},{3,1,-1},{1,2,-1},{3,0,1,2},{0,2,-1},{3,2,-1},{2,3,-1},{2,0,-1},{0,1,2,3},{2,1,-1},{1,3,-1},{1,0,-1},{0,3,-1},{-1}};
      for (int e = 0; e < 4 && tbl[code][e] >= 0; e += 2) { int p = tbl[code][e], q = tbl[code][e + 1]; if (inCircle(ex[p][0], ex[p][1], 114) && inCircle(ex[q][0], ex[q][1], 114)) stitch(ex[p][0], ex[p][1], ex[q][0], ex[q][1], 1.7f, c); } } }
  G.c += 0.012f; if (G.steps % 600 == 599) { G.pcol = threadFor(ground); } }
// 39 strange attractor (Clifford): points accumulate as knots, parameters re-rolled when it goes stale
static void initAttr() { uint16_t g = randGround(); G.pcol = threadFor(g);
  for (int tries = 0; tries < 40; tries++) {
    G.a = (random(2) ? 1 : -1) * frandr(1.3f, 2.0f); G.b = (random(2) ? 1 : -1) * frandr(1.3f, 2.0f); G.c = (random(2) ? 1 : -1) * frandr(0.6f, 1.9f); G.d = (random(2) ? 1 : -1) * frandr(0.6f, 1.9f);
    float x = 0.1f, y = 0.1f, mnx = 9, mxx = -9, mny = 9, mxy = -9;
    for (int i = 0; i < 400; i++) { float nx = sinf(G.a * y) + G.c * cosf(G.a * x), ny = sinf(G.b * x) + G.d * cosf(G.b * y); x = nx; y = ny; if (i > 50) { mnx = min(mnx, x); mxx = max(mxx, x); mny = min(mny, y); mxy = max(mxy, y); } }
    if (mxx - mnx > 1.2f && mxy - mny > 1.2f) break;                 // spread out = a real attractor, not a fixed point or short cycle
  }
  G.x = 0.1f; G.y = 0.1f; G.i = 0; }
static void stepAttr() {
  for (int k = 0; k < 40; k++) { float nx = sinf(G.a * G.y) + G.c * cosf(G.a * G.x), ny = sinf(G.b * G.x) + G.d * cosf(G.b * G.y); G.x = nx; G.y = ny;
    float px_ = 120 + nx * 42, py_ = 120 + ny * 42; if (inCircle(px_, py_, 112) && G.i > 20) knot(px_, py_, 1.3f, shade(G.pcol, 0.8f + 0.4f * frand())); G.i++; }
  if (G.steps > 450) genComplete = true;
}
// 40 harmonograph: two damped pendulums trace a single thread
static float HF[4], HP[4];
static void initHarm() { uint16_t g = randGround(); G.pcol = threadFor(g);
  int base = random(1, 4); HF[0] = base; HF[1] = base * (random(2) ? 2 : 3) + frandr(-0.02f, 0.02f); HF[2] = random(1, 4) + frandr(-0.02f, 0.02f); HF[3] = HF[2] * (random(2) ? 2 : 1.5f) + frandr(-0.02f, 0.02f);
  for (int i = 0; i < 4; i++) HP[i] = frandr(0, 6.28f);
  G.e = frandr(0.00035f, 0.0008f); G.i = 0; G.x = G.y = 0; }
static void stepHarm() {
  for (int k = 0; k < 8; k++) { float t = G.i * 0.03f, damp = expf(-G.e * G.i);
    float x = 120 + damp * (62 * sinf(HF[0] * t + HP[0]) + 40 * sinf(HF[1] * t + HP[1])), y = 120 + damp * (62 * sinf(HF[2] * t + HP[2]) + 40 * sinf(HF[3] * t + HP[3]));
    if (G.i > 0 && inCircle(x, y, 114) && inCircle(G.x, G.y, 114)) stitch(G.x, G.y, x, y, 1.5f, shade(G.pcol, 0.7f + 0.6f * damp)); G.x = x; G.y = y; G.i++; }
  if (expf(-G.e * G.i) < 0.08f) genComplete = true;
}
// 41 Molnár's (Dés)Ordres: a grid of nested squares, disorder creeping in then resetting
static void initMolnar() { uint16_t g = randGround(); G.pcol = threadFor(g); G.a = 0; }
static void stepMolnar() { if (G.steps % 5) return;
  fillGround(ground, ground != SOOT); const int n = 5; const float cell = 44, o = 120 - cell * n / 2;
  for (int j = 0; j < n; j++) for (int i = 0; i < n; i++) { float cx = o + (i + 0.5f) * cell, cy = o + (j + 0.5f) * cell; uint32_t h = (i * 73856093u) ^ (j * 19349663u) ^ (uint32_t)(G.steps / 5 * 2654435761u);
    for (int k = 0; k < 4; k++) { float hs = cell * (0.46f - k * 0.1f); float jit = G.a * (((h >> (k * 5)) & 31) / 31.0f - 0.5f); float rot = jit * 0.6f, dx = jit * 5, dy = (((h >> (k * 3 + 7)) & 15) / 15.0f - 0.5f) * G.a * 5; float cr = cosf(rot), sr = sinf(rot);
      float px_[4], py_[4]; for (int v = 0; v < 4; v++) { float sx = (v == 1 || v == 2) ? hs : -hs, sy = v >= 2 ? hs : -hs; px_[v] = cx + dx + sx * cr - sy * sr; py_[v] = cy + dy + sx * sr + sy * cr; }
      for (int v = 0; v < 4; v++) if (inCircle(px_[v], py_[v], 116)) stitch(px_[v], py_[v], px_[(v + 1) % 4], py_[(v + 1) % 4], 1.6f, G.pcol); } }
  G.a += 0.02f; if (G.a > 1.6f) { G.a = 0; G.pcol = threadFor(ground); } }


// ================= 42..61 reactive generators: the finger is the needle =================
static uint16_t MUSTARD_C() { return C565(214, 168, 58); }
struct TouchState { bool down; float x, y, lx, ly, dx, dy; int ev; uint32_t downSteps; float path[2]; } TS;   // ev: 0 down 1 move 2 up, -1 none
static bool genIsReactive() { return G.id >= REACTIVE_FIRST && G.id <= REACTIVE_LAST; }
static void genTouch(int type, int x, int y) {
  if (type == 0) { TS.down = true; TS.x = TS.lx = x; TS.y = TS.ly = y; TS.dx = TS.dy = 0; TS.downSteps = 0; }
  else if (type == 1) { TS.lx = TS.x; TS.ly = TS.y; TS.x = x; TS.y = y; TS.dx = TS.x - TS.lx; TS.dy = TS.y - TS.ly; }
  else { TS.down = false; }
  TS.ev = type;
}
static inline bool fresh(int type) { bool r = TS.ev == type; return r; }
static void consumeTouch() { if (TS.ev == 2 || TS.ev == 0) TS.ev = -1; else if (TS.ev == 1) TS.ev = -1; }

// 42 seam: drag sews a running stitch; lifts end the seam; old seams fade
static void initTSeam() { uint16_t g = randGround(); G.pcol = threadFor(g); G.a = 0; }
static void stepTSeam() {
  if (TS.down && TS.ev == 1) { float L = sqrtf(TS.dx * TS.dx + TS.dy * TS.dy); G.a += L;
    if (G.a > 3.5f) { G.a = 0; float ux = TS.dx / (L + 0.01f), uy = TS.dy / (L + 0.01f); stitch(TS.x - ux * 5, TS.y - uy * 5, TS.x, TS.y, 2.4f, G.pcol); } }
  if (TS.ev == 2) G.pcol = threadFor(ground);
  if (G.steps % 50 == 49) fadeToGround(6); consumeTouch(); }
// 43 satin brush: drag paints a fat satin stroke, tap changes colour
static void initTSatin() { uint16_t g = randGround(); G.pcol = threadFor(g); G.b = 7; }
static void stepTSatin() {
  if (TS.down) { float L = sqrtf(TS.dx * TS.dx + TS.dy * TS.dy); if (L > 0.5f) { float nx = -TS.dy / L, ny = TS.dx / L; for (float t = 0; t <= L; t += 1.2f) { float px_ = TS.lx + TS.dx * t / L, py_ = TS.ly + TS.dy * t / L; stitch(px_ + nx * G.b, py_ + ny * G.b, px_ - nx * G.b, py_ - ny * G.b, 1.4f, shade(G.pcol, 0.85f + 0.3f * frand())); } } }
  if (TS.ev == 0) { TS.downSteps = 0; } if (TS.down) TS.downSteps++;
  if (TS.ev == 2 && TS.downSteps < 6) G.pcol = threadFor(ground);          // a quick tap = next colour
  consumeTouch(); }
// 44 bloom: tap plants a flower that blooms petal by petal
static void initTBloom() { uint16_t g = randGround(); FL.dark = g == SOOT; FL.nfl = 0; FL.leaf = FL.dark ? C565(150, 180, 110) : C565(126, 150, 92); }
static void stepTBloom() {
  if (TS.ev == 0) { if (FL.nfl >= 48) FL.nfl = 0; addFlower(TS.x, TS.y, random(0, 4) == 2 ? 3 : random(0, 4), frandr(9, 16), FLOWER_COLS[random(0, 7)]);
    for (int k = 0; k < 2; k++) { float a = frandr(0, 6.28f); leafStroke(TS.x + cosf(a) * 6, TS.y + sinf(a) * 6, a, frandr(8, 14), 2.4f, FL.leaf); } }
  int blooming = 0; for (int i = 0; i < FL.nfl; i++) if (FL.fl[i].alive) { blooming++; if (!bloom(FL.fl[i])) FL.fl[i].alive = false; if (blooming >= 2) break; }
  consumeTouch(); }
// 45 ripple: tap drops a stone; stitched rings expand
struct Rip { float x, y, r; bool on; } RP[3];
static void initTRipple() { uint16_t g = randGround(); G.pcol = threadFor(g); for (auto &r : RP) r.on = false; }
static void stepTRipple() {
  if (TS.ev == 0) { bool placed = false; for (auto &r : RP) if (!r.on) { r = {TS.x, TS.y, 4, true}; placed = true; break; } if (!placed) RP[0] = {TS.x, TS.y, 4, true}; }
  if (G.steps % 2 == 0) for (auto &r : RP) if (r.on) { int segs = 16 + (int)r.r / 3; for (int k = 0; k < segs; k += 2) { float a0 = 6.2832f * k / segs, a1 = a0 + 6.2832f / segs; float x0 = r.x + r.r * cosf(a0), y0 = r.y + r.r * sinf(a0), x1 = r.x + r.r * cosf(a1), y1 = r.y + r.r * sinf(a1); if (inCircle(x0, y0, 114) && inCircle(x1, y1, 114)) stitch(x0, y0, x1, y1, 1.8f, shade(G.pcol, 1.0f - r.r / 300)); } r.r += 7; if (r.r > 120) r.on = false; }
  if (G.steps % 2 == 1) fadeToGround(22); consumeTouch(); }
// 46 knots: drag drops French knots, denser when you move slowly
static void initTKnots() { uint16_t g = randGround(); G.pcol = threadFor(g); G.a = 0; }
static void stepTKnots() {
  if (TS.down) { float L = sqrtf(TS.dx * TS.dx + TS.dy * TS.dy); G.a += max(1.0f, L); if (G.a > 7) { G.a = 0; knot(TS.x + frandr(-2, 2), TS.y + frandr(-2, 2), frandr(2.2f, 4.2f), L < 2 ? shade(G.pcol, 1.2f) : G.pcol); } }
  if (TS.ev == 2) G.pcol = threadFor(ground); consumeTouch(); }
// 47 flock: the boids flee your finger and regroup when you lift
static void initTFlock() { initFlock(); }
static void stepTFlock() {
  if (TS.down) for (auto &b : BD) { float dx = b.x - TS.x, dy = b.y - TS.y, d2 = dx * dx + dy * dy + 1; if (d2 < 3600) { b.vx += dx / d2 * 40; b.vy += dy / d2 * 40; } }
  stepFlock(); consumeTouch(); }
// 48 crystal: tap seeds a DLA crystal where you touch
static void initTCrystal() { uint16_t g = randGround(); G.pcol = threadFor(g); memset(OCC, 0, sizeof OCC); G.a = 0; G.i = 0; }
static void stepTCrystal() {
  if (TS.ev == 0) { setOcc(TS.x, TS.y); knot(TS.x, TS.y, 2.6f, G.pcol); G.a = max(G.a, sqrtf((TS.x - 120) * (TS.x - 120) + (TS.y - 120) * (TS.y - 120)) + 8); }
  if (G.a > 0) { float sr = min(106.0f, G.a + 6); for (int w = 0; w < 16; w++) { float a = frandr(0, 6.28f); int x = 120 + sr * cosf(a), y = 120 + sr * sinf(a);
      for (int t = 0; t < 2500; t++) { x += random(-1, 2); y += random(-1, 2); if (!inCircle(x, y, min(110.0f, G.a + 16))) { a = frandr(0, 6.28f); x = 120 + sr * cosf(a); y = 120 + sr * sinf(a); }
        if (occ(x + 1, y) || occ(x - 1, y) || occ(x, y + 1) || occ(x, y - 1)) { setOcc(x, y); knot(x, y, 1.7f, shade(G.pcol, 0.75f + frand() * 0.5f)); G.a = max(G.a, sqrtf((x - 120.f) * (x - 120.f) + (y - 120.f) * (y - 120.f)) + 8); G.i++; break; } } } }
  consumeTouch(); }
// 49 vine: a vine sprouts from wherever you touch and climbs
static void initTVine() { fillGround(C565(232, 224, 204), true); G.branches = 0; }
static void stepTVine() {
  if (TS.ev == 0 && G.branches < 38) { G.branchX[G.branches] = TS.x; G.branchY[G.branches] = TS.y; G.branchA[G.branches] = -1.57f + frandr(-0.5f, 0.5f); G.branchL[G.branches] = 1; G.branches++; }
  for (int bi = 0; bi < G.branches; bi++) {
    float &x = G.branchX[bi], &y = G.branchY[bi], &a = G.branchA[bi]; a += frandr(-0.3f, 0.3f) + (-1.57f - a) * 0.05f;
    float nx = x + cosf(a) * 3, ny = y + sinf(a) * 3; if (!inCircle(nx, ny, 110)) { G.branchX[bi] = G.branchX[G.branches - 1]; G.branchY[bi] = G.branchY[G.branches - 1]; G.branchA[bi] = G.branchA[G.branches - 1]; G.branches--; bi--; continue; }
    stitch(x, y, nx, ny, 2.4f, C565(86, 110, 64)); x = nx; y = ny;
    if (frand() < 0.1f) leafStroke(x, y, a + (random(2) ? 1 : -1), frandr(7, 11), 2.2f, C565(132, 150, 100));
    if (frand() < 0.025f) { uint16_t fc = FLOWER_COLS[random(0, 7)]; for (int p = 0; p < 6; p++) knot(x + cosf(p * 1.05f) * 4, y + sinf(p * 1.05f) * 4, 2.2f, fc); knot(x, y, 2, C565(214, 168, 58)); }
    if (frand() < 0.03f && G.branches < 38) { G.branchX[G.branches] = x; G.branchY[G.branches] = y; G.branchA[G.branches] = a + frandr(-1, 1); G.branchL[G.branches] = 1; G.branches++; } }
  consumeTouch(); }
// 50 web: each tap pins a thread anchor and ties it to the nearest three
static void initTWeb() { uint16_t g = randGround(); G.pcol = threadFor(g); G.n = 0; }
static void stepTWeb() {
  if (TS.ev == 0 && G.n < 64) { int best[3] = {-1, -1, -1}; float bd[3] = {1e9, 1e9, 1e9};
    for (int i = 0; i < G.n; i++) { float d = (G.px_[i] - TS.x) * (G.px_[i] - TS.x) + (G.py_[i] - TS.y) * (G.py_[i] - TS.y); for (int k = 0; k < 3; k++) if (d < bd[k]) { for (int m = 2; m > k; m--) { bd[m] = bd[m - 1]; best[m] = best[m - 1]; } bd[k] = d; best[k] = i; break; } }
    for (int k = 0; k < 3; k++) if (best[k] >= 0) { float ax = G.px_[best[k]], ay = G.py_[best[k]]; dashes(ax, ay, TS.x, TS.y, 5, 2.5f, 1.6f, G.pcol); }
    G.px_[G.n] = TS.x; G.py_[G.n] = TS.y; G.n++; knot(TS.x, TS.y, 3.2f, shade(G.pcol, 1.2f)); }
  consumeTouch(); }
// 51 granny: every tap crochets a small granny square there
static void initTGranny() { fillGround(SOOT, false); G.n = 0; }
static void stepTGranny() {
  if (TS.ev == 0) { int start = random(0, 7); float cx = TS.x, cy = TS.y, skew = frandr(-0.3f, 0.3f);
    for (int i = 0; i < 12; i++) { float a0 = i * 0.5236f, a1 = a0 + 0.5236f; yarnSeg(cx + 5 * cosf(a0), cy + 5 * sinf(a0), cx + 5 * cosf(a1), cy + 5 * sinf(a1), 2.6f, PAL[start % 7]); }
    for (int n = 1; n <= 2; n++) { uint16_t col = PAL[(start + n) % 7]; float hi = 7 + 12 * (n - 1), ho = hi + 10; int per = n;
      for (int side = 0; side < 4; side++) { float rot = 1.5708f * side + skew;
        for (int k = 0; k < per; k++) { float x = -hi + 2 * hi * (k + 0.5f) / per; float bx, by, tx, ty;
          for (int o = -1; o <= 1; o++) { bx = cx + x * cosf(rot) - (-hi + 1) * sinf(rot); by = cy + x * sinf(rot) + (-hi + 1) * cosf(rot); tx = cx + (x + o * 3.2f) * cosf(rot) - (-ho) * sinf(rot); ty = cy + (x + o * 3.2f) * sinf(rot) + (-ho) * cosf(rot); post(bx, by, tx, ty, col); } }
        float cr = ho * 1.4142f + 1.5f, ac = rot + 0.7854f - 1.5708f; yarnSeg(cx + ho * cosf(rot - 1.5708f) * 0 + (hi) * cosf(rot) - (-ho) * sinf(rot), cy + (hi) * sinf(rot) + (-ho) * cosf(rot), cx + cr * cosf(ac), cy + cr * sinf(ac), 2.2f, col); } } }
  consumeTouch(); }
// 52 rose: hold to grow a spiral rose; the longer you hold, the bigger
static void initTRose() { uint16_t g = randGround(); G.pcol = threadFor(g); G.a = 0; }
static void stepTRose() {
  if (TS.ev == 0) { G.a = 0; G.pcol = FLOWER_COLS[random(0, 7)]; G.x = TS.x; G.y = TS.y; }
  if (TS.down && G.a < 6.2832f * 3.5f) { float th0 = G.a, th1 = G.a + 0.45f, r0 = 1 + 2.4f * th0, r1 = 1 + 2.4f * th1; stitch(G.x + r0 * cosf(th0), G.y + r0 * sinf(th0), G.x + r1 * cosf(th1), G.y + r1 * sinf(th1), 2.8f, shade(G.pcol, 0.7f + 0.5f * th1 / 22)); G.a = th1; }
  if (TS.ev == 2 && G.a > 2) for (int k = 0; k < 3; k++) { float a = frandr(0, 6.28f), r = 1 + 2.4f * G.a; leafStroke(G.x + cosf(a) * r, G.y + sinf(a) * r, a, 12, 3, C565(96, 134, 72)); }
  consumeTouch(); }
// 53 asawa: drag up and down the centre line to sculpt a lobed form, lift to crochet it
static void initTAsawa() { AS.dark = random(2); uint16_t g = AS.dark ? SOOT : C565(232, 224, 204); fillGround(g, !AS.dark); for (int i = 0; i < 28; i++) G.px_[i] = 0; G.n = 0; G.i = -1; }
static void stepTAsawa() {
  if (TS.down) { int row = constrain((int)(TS.y / 8.6f), 0, 27); float r = fabsf(TS.x - 120); G.px_[row] = max(G.px_[row], min(r, 108.0f)); for (int k = 1; k <= 2; k++) { if (row - k >= 0) G.px_[row - k] = max(G.px_[row - k], G.px_[row] * (1 - 0.25f * k)); if (row + k < 28) G.px_[row + k] = max(G.px_[row + k], G.px_[row] * (1 - 0.25f * k)); }
    // live guide: faint ring where the finger is
    float R = G.px_[row]; for (int k = 0; k < 20; k++) { float a0 = k * 0.314f, a1 = a0 + 0.314f; stitch(120 + R * cosf(a0), row * 8.6f + 4 + R * 0.28f * sinf(a0), 120 + R * cosf(a1), row * 8.6f + 4 + R * 0.28f * sinf(a1), 1.0f, shade(ground, AS.dark ? 2.5f : 0.8f)); } }
  if (TS.ev == 2) { fillGround(ground, !AS.dark); G.i = 0; G.n = 0; }
  if (G.i >= 0 && G.i < 28) {   // crochet the sculpted profile ring by ring
    uint16_t col = asawaCol(0); float y = G.i * 8.6f + 4, R = G.px_[G.i], yp = (G.i - 1) * 8.6f + 4, Rp = G.i ? G.px_[G.i - 1] : 0;
    if (G.i == 0) stitch(120, 0, 120, y, 1.1f, col);
    if (R > 2) { for (int k = 0; k < 28; k++) { float a0 = k * 0.2244f, a1 = a0 + 0.2244f; stitch(120 + R * cosf(a0), y + R * 0.28f * sinf(a0), 120 + R * cosf(a1), y + R * 0.28f * sinf(a1), wireW(1.3f), k < 14 ? shade(col, 0.8f) : col); }
      for (int m = 0; m < 16; m++) { float a = 6.2832f * m / 16; stitch(120 + Rp * cosf(a), yp + Rp * 0.28f * sinf(a), 120 + R * cosf(a), y + R * 0.28f * sinf(a), wireW(1.1f), sinf(a) < 0 ? shade(col, 0.75f) : col); } }
    G.i++; }
  consumeTouch(); }
// 54 mend: tap tears the cloth; it darns itself shut
static void initTMend() { fillGround(C565(96, 58, 92), true); G.n = 0; }
static void stepTMend() {
  if (TS.ev == 0 && G.n < 8) { float a = frandr(0, 3.14f), L = frandr(18, 34); G.px_[G.n] = TS.x; G.py_[G.n] = TS.y; G.pvx[G.n] = a; G.pvy[G.n] = L; G.pc[G.n] = 0; G.n++;
    for (int k = -4; k < 4; k++) { float t0 = k * L / 8, t1 = t0 + L / 8; thick(TS.x + cosf(a) * t0 + frandr(-2, 2), TS.y + sinf(a) * t0, TS.x + cosf(a) * t1 + frandr(-2, 2), TS.y + sinf(a) * t1, 5, C565(10, 8, 10)); } }
  for (int i = 0; i < G.n; i++) if (G.pc[i] < 60) { float a = G.pvx[i], L = G.pvy[i]; int k = G.pc[i]; float nx = -sinf(a), ny = cosf(a);
    if (k < 24) { float t = -L / 2 - 6 + k * (L + 12) / 24; stitch(G.px_[i] + cosf(a) * t + nx * 7, G.py_[i] + sinf(a) * t + ny * 7, G.px_[i] + cosf(a) * t - nx * 7, G.py_[i] + sinf(a) * t - ny * 7, 2.0f, MUSTARD_C()); }
    else { int j = k - 24; float u = -7 + j * 14 / 36.0f; stitch(G.px_[i] - cosf(a) * (L / 2 + 6) + nx * u, G.py_[i] - sinf(a) * (L / 2 + 6) + ny * u, G.px_[i] + cosf(a) * (L / 2 + 6) + nx * u, G.py_[i] + sinf(a) * (L / 2 + 6) + ny * u, 1.6f, (j & 1) ? C565(72, 132, 130) : C565(236, 226, 204)); }
    G.pc[i]++; break; }
  consumeTouch(); }
// 55 buttons: tap sews on a button; drag sews a thread between the last two
static void initTButtons() { uint16_t g = randGround(); G.n = 0; }
static void stepTButtons() {
  if (TS.ev == 0) { float r = frandr(7, 16); uint16_t c = PAL[random(0, 7)]; int segs = (int)(r * 1.6f);
    for (int k = 0; k < segs; k++) { float a0 = 6.2832f * k / segs, a1 = a0 + 6.2832f / segs; stitch(TS.x + r * cosf(a0), TS.y + r * sinf(a0), TS.x + r * cosf(a1), TS.y + r * sinf(a1), 2.4f, c); }
    disc(TS.x, TS.y, r * 0.78f, shade(c, 0.9f)); disc(TS.x, TS.y, r * 0.78f, c); float hs = r * 0.26f, hr = r * 0.11f + 0.8f; uint16_t thr = random(2) ? SOOT : CREAM; if (c == SOOT) thr = CREAM;
    disc(TS.x - hs, TS.y - hs, hr, C565(8, 8, 10)); disc(TS.x + hs, TS.y - hs, hr, C565(8, 8, 10)); disc(TS.x + hs, TS.y + hs, hr, C565(8, 8, 10)); disc(TS.x - hs, TS.y + hs, hr, C565(8, 8, 10));
    stitch(TS.x - hs, TS.y - hs, TS.x + hs, TS.y + hs, 1.8f, thr); stitch(TS.x + hs, TS.y - hs, TS.x - hs, TS.y + hs, 1.8f, thr);
    if (G.n > 0) dashes(G.px_[(G.n - 1) % 64], G.py_[(G.n - 1) % 64], TS.x, TS.y, 4, 3, 1.3f, thr); G.px_[G.n % 64] = TS.x; G.py_[G.n % 64] = TS.y; G.n++; }
  consumeTouch(); }
// 56 kaleido: everything you draw is mirrored six-fold
static void initTKaleido() { uint16_t g = randGround(); G.pcol = threadFor(g); }
static void stepTKaleido() {
  if (TS.down && TS.ev == 1) { for (int k = 0; k < 6; k++) { float a = k * 1.0472f, ca = cosf(a), sa = sinf(a);
      for (int m = 0; m < 2; m++) { float lx = TS.lx - 120, ly = (m ? -1 : 1) * (TS.ly - 120), x = TS.x - 120, y = (m ? -1 : 1) * (TS.y - 120);
        stitch(120 + lx * ca - ly * sa, 120 + lx * sa + ly * ca, 120 + x * ca - y * sa, 120 + x * sa + y * ca, 2.2f, G.pcol); } } }
  if (TS.ev == 2) G.pcol = threadFor(ground); consumeTouch(); }
// 57 string art: tap near the rim to add a pin; threads run between the pins
static void initTString() { uint16_t g = randGround(); G.pcol = threadFor(g); G.n = 0; for (int k = 0; k < 36; k++) knot(120 + 110 * cosf(k * 0.1745f), 120 + 110 * sinf(k * 0.1745f), 1.6f, shade(ground, ground == SOOT ? 2.2f : 0.8f)); }
static void stepTString() {
  if (TS.ev == 0 && G.n < 64) { float a = atan2f(TS.y - 120, TS.x - 120); float x = 120 + 110 * cosf(a), y = 120 + 110 * sinf(a); knot(x, y, 2.6f, G.pcol);
    for (int i = max(0, G.n - 6); i < G.n; i++) stitch(G.px_[i], G.py_[i], x, y, 1.3f, shade(G.pcol, 0.8f + 0.3f * frand())); G.px_[G.n] = x; G.py_[G.n] = y; G.n++; if (G.n % 8 == 0) G.pcol = threadFor(ground); }
  consumeTouch(); }
// 58 contours: press to raise a hill in the noise field; the contours flow around it
static float BUMPX[6], BUMPY[6], BUMPH[6]; static int nbump;
static void initTContours() { initContours(); nbump = 0; }
static void stepTContours() {
  if (TS.ev == 0) { BUMPX[nbump % 6] = TS.x; BUMPY[nbump % 6] = TS.y; BUMPH[nbump % 6] = 0.1f; nbump++; }
  if (TS.down) BUMPH[(nbump - 1) % 6] = min(1.2f, BUMPH[(nbump - 1) % 6] + 0.03f);
  if (G.steps % 4 == 0) {
    fillGround(ground, ground != SOOT); const int N = 40; const float cs = 6; static float F[41 * 41];
    for (int j = 0; j <= N; j++) for (int i = 0; i <= N; i++) { float v = vnoise(i * cs / 70 + G.a, j * cs / 70 + G.b + G.c); for (int b = 0; b < min(nbump, 6); b++) { float dx = i * cs - BUMPX[b], dy = j * cs - BUMPY[b]; v += BUMPH[b] * expf(-(dx * dx + dy * dy) / 1400); } F[j * 41 + i] = v; }
    for (int lv = 0; lv < 9; lv++) { float iso = 0.2f + lv * 0.16f; uint16_t c = lv % 2 ? G.pcol : shade(G.pcol, 0.8f);
      for (int j = 0; j < N; j++) for (int i = 0; i < N; i++) { float a = F[j * 41 + i], b = F[j * 41 + i + 1], cc = F[(j + 1) * 41 + i + 1], d = F[(j + 1) * 41 + i]; int code = (a > iso) | (b > iso) << 1 | (cc > iso) << 2 | (d > iso) << 3; if (code == 0 || code == 15) continue;
        float x0 = i * cs, y0 = j * cs; auto lerp = [&](float p, float q) { return (iso - p) / (q - p + 1e-6f); };
        float ex[4][2] = {{x0 + cs * lerp(a, b), y0}, {x0 + cs, y0 + cs * lerp(b, cc)}, {x0 + cs * lerp(d, cc), y0 + cs}, {x0, y0 + cs * lerp(a, d)}};
        static const int8_t tbl[16][4] = {{-1},{3,0,-1},{0,1,-1},{3,1,-1},{1,2,-1},{3,0,1,2},{0,2,-1},{3,2,-1},{2,3,-1},{2,0,-1},{0,1,2,3},{2,1,-1},{1,3,-1},{1,0,-1},{0,3,-1},{-1}};
        for (int e = 0; e < 4 && tbl[code][e] >= 0; e += 2) { int p = tbl[code][e], q = tbl[code][e + 1]; if (inCircle(ex[p][0], ex[p][1], 114) && inCircle(ex[q][0], ex[q][1], 114)) stitch(ex[p][0], ex[p][1], ex[q][0], ex[q][1], 1.7f, c); } } }
    G.c += 0.006f; }
  consumeTouch(); }
// 59 shibori: hold to let dye bleed out in stitched rings from the finger
static void initTShibori() { fillGround(INDIGO, true); G.a = 0; }
static void stepTShibori() {
  if (TS.ev == 0) { G.a = 3; G.x = TS.x; G.y = TS.y; }
  if (TS.down && G.a < 70) { int segs = 10 + (int)G.a / 2; for (int k = 0; k < segs; k++) { float a0 = 6.2832f * k / segs + frandr(-0.1f, 0.1f), r = G.a + frandr(-1.5f, 1.5f); float x = G.x + r * cosf(a0), y = G.y + r * sinf(a0); if (inCircle(x, y, 114) && frand() < 0.8f) stitch(x, y, x + cosf(a0) * 3, y + sinf(a0) * 3, 1.5f, shade(CREAM, 0.85f + 0.15f * frand())); } G.a += 2.2f; }
  consumeTouch(); }
// 60 life: paint live cells with your finger; the automaton carries on
static void initTLife() { initLife(); }
static void stepTLife() {
  if (TS.down) { const int N = 24; const float c = 9.5f, o = 120 - c * N / 2; int i = (int)((TS.x - o) / c), j = (int)((TS.y - o) / c); if (i >= 0 && i < N && j >= 0 && j < N) { G.cells[j * N + i] = 1; if (i + 1 < N) G.cells[j * N + i + 1] = 1; if (j + 1 < N) G.cells[(j + 1) * N + i] = 1; } }
  stepLife(); consumeTouch(); }
// 61 truchet: tap a tile to flip it
static void initTTruchet() { initTruchet(); if (ground == SOOT) { G.pcol = CREAM; for (int j = 0; j < 8; j++) for (int i = 0; i < 8; i++) drawTruchetTile(i, j, G.pcol); } }
static void stepTTruchet() {
  if (TS.ev == 0) { int i = constrain((int)(TS.x / 30), 0, 7), j = constrain((int)(TS.y / 30), 0, 7); TR[j * 8 + i] ^= 1;
    for (int y = j * 30; y < j * 30 + 30; y++) for (int x = i * 30; x < i * 30 + 30; x++) if (inCircle(x, y, 121)) frameBuf[y * GW + x] = ground; drawTruchetTile(i, j, G.pcol); }
  consumeTouch(); }


// ================= 62..69 generative wagara: a fresh randomised traditional pattern each time, sewn in order =================
struct Wag { float sc, rot, p1; int i, j, n, phase; uint16_t a, b; bool darkG; } WG;
static void wagGround() { WG.darkG = random(3) != 0; if (WG.darkG) { fillGround(INDIGO, true); WG.a = CREAM; WG.b = random(2) ? VERM : C565(214, 168, 58); } else { fillGround(C565(236, 228, 208), true); WG.a = INDIGO; WG.b = random(2) ? VERM : INDIGO_L; } }
static void dashArc(float cx, float cy, float r, float a0, float a1, uint16_t col, float w = 2.4f) { int n = max(4, (int)((a1 - a0) * r / 7)); for (int k = 0; k < n; k++) { float t0 = a0 + (a1 - a0) * k / n, t1 = t0 + (a1 - a0) * 0.68f / n; float x0 = cx + r * cosf(t0), y0 = cy + r * sinf(t0), x1 = cx + r * cosf(t1), y1 = cy + r * sinf(t1); if (inCircle(x0, y0, 117) && inCircle(x1, y1, 117)) stitch(x0, y0, x1, y1, w, col); } }
static void fillQuad(float *xs, float *ys, uint16_t col, float ang) {   // scanline fill of a convex quad with satin stripes
  float ymin = min(min(ys[0], ys[1]), min(ys[2], ys[3])), ymax = max(max(ys[0], ys[1]), max(ys[2], ys[3])); float ca = cosf(ang), sa = sinf(ang);
  for (int y = max(0, (int)ymin); y <= min(239, (int)ymax); y++) { float xl = 1e9, xr = -1e9;
    for (int e = 0; e < 4; e++) { float x0 = xs[e], y0 = ys[e], x1 = xs[(e + 1) % 4], y1 = ys[(e + 1) % 4]; if ((y0 <= y && y1 > y) || (y1 <= y && y0 > y)) { float x = x0 + (y - y0) * (x1 - x0) / (y1 - y0); xl = min(xl, x); xr = max(xr, x); } }
    for (int x = max(0, (int)xl); x <= min(239, (int)xr); x++) if (inCircle(x, y, 118)) { int st = ((int)floorf((x * ca + y * sa) / 1.6f)) & 1; px(x, y, st ? col : shade(col, 0.84f)); } }
}
// walk the square ring `ring` (8*ring cells, or 1 for ring 0): k -> (gi, gj); returns false when k is past the ring
static bool ringCell(int ring, int k, int &gi, int &gj) {
  if (ring == 0) { gi = gj = 0; return k == 0; } int per = 8 * ring; if (k >= per) return false; int side = 2 * ring;
  int e = k / side, t = k % side;
  if (e == 0) { gi = -ring + t; gj = -ring; } else if (e == 1) { gi = ring; gj = -ring + t; } else if (e == 2) { gi = ring - t; gj = ring; } else { gi = -ring; gj = ring - t; }
  return true;
}
// 62 seigaiha: scallops row by row
static void initSeig() { wagGround(); WG.sc = frandr(26, 46); WG.j = 0; WG.i = 0; }
static void stepSeig() {
  float R = WG.sc; int rows = (int)(260 / (R / 2)) + 1; if (WG.j > rows) { genComplete = true; return; }
  float cy = WG.j * R / 2 - 4, cx = -R + (WG.j % 2 ? R : 0) + WG.i * 2 * R;
  if (cx > 264 + R) { WG.j++; WG.i = 0; return; }
  if (sqrtf((cx - 120) * (cx - 120) + (cy - 120) * (cy - 120)) < 120 + R) {
    disc(cx, cy, R, ground); dashArc(cx, cy, R - 3, 3.1416f, 6.2832f, WG.a); dashArc(cx, cy, R * 0.62f, 3.1416f, 6.2832f, WG.a); dashArc(cx, cy, R * 0.3f, 3.1416f, 6.2832f, WG.b); }
  WG.i++;
}
// 63 asanoha: three line families then the hemp-leaf spokes
static void initAsa() { wagGround(); WG.sc = frandr(34, 58); WG.rot = frandr(0, 1.0f); WG.phase = 0; WG.i = -8; WG.j = 0; }
static void stepAsa() {
  float a = WG.sc, h = a * 0.866f;
  if (WG.phase < 3) { float ang = WG.rot + 1.0472f * WG.phase; float dx = cosf(ang), dy = sinf(ang), nx = -dy, ny = dx; float off = WG.i * (WG.phase == 0 ? h : a * 0.866f);
    float px0 = 120 + nx * off, py0 = 120 + ny * off; float fx = px0 - 120, fy = py0 - 120; float bq = 2 * (fx * dx + fy * dy), cq = fx * fx + fy * fy - 118 * 118, disc_ = bq * bq - 4 * cq;
    if (disc_ > 0) { float sq = sqrtf(disc_); float t0 = (-bq - sq) / 2, t1 = (-bq + sq) / 2; for (float t = t0; t < t1; t += 10) { float e = min(t1, t + 6.5f); stitch(px0 + dx * t, py0 + dy * t, px0 + dx * e, py0 + dy * e, 2.4f, WG.a); } }
    if (++WG.i > 8) { WG.i = -8; WG.phase++; } return; }
  // spokes: iterate triangles of the lattice
  int i = WG.i, j = WG.j; if (j > 6) { genComplete = true; return; }
  float ca = cosf(WG.rot), sa = sinf(WG.rot);
  auto P_ = [&](float ii, float jj, float &x, float &y) { float lx = a * (ii + jj / 2), ly = jj * h; x = 120 + lx * ca - ly * sa; y = 120 + lx * sa + ly * ca; };
  for (int tri = 0; tri < 2; tri++) { float xs[3], ys[3]; if (tri == 0) { P_(i, j, xs[0], ys[0]); P_(i + 1, j, xs[1], ys[1]); P_(i, j + 1, xs[2], ys[2]); } else { P_(i + 1, j, xs[0], ys[0]); P_(i, j + 1, xs[1], ys[1]); P_(i + 1, j + 1, xs[2], ys[2]); }
    float gx = (xs[0] + xs[1] + xs[2]) / 3, gy = (ys[0] + ys[1] + ys[2]) / 3; if (inCircle(gx, gy, 112)) for (int v = 0; v < 3; v++) stitch(gx, gy, xs[v], ys[v], 2.0f, WG.b); }
  if (++WG.i > 8) { WG.i = -9; WG.j++; }
}
// 64 shippō: interlocking circles from the centre out
static void initShip() { wagGround(); WG.sc = frandr(30, 52); WG.i = 0; WG.j = 0; WG.phase = 0; }
static void stepShip() {
  float r = WG.sc, s_ = r * 1.41421f; int gi, gj;
  if (!ringCell(WG.j, WG.i, gi, gj)) { WG.j++; WG.i = 0; if (WG.j > 4) genComplete = true; return; }
  for (int which = 0; which < 2; which++) { float cx = 120 + gi * s_ + (which ? s_ / 2 : 0), cy = 120 + gj * s_ + (which ? s_ / 2 : 0);
    if (sqrtf((cx - 120) * (cx - 120) + (cy - 120) * (cy - 120)) < 118 + r) { dashArc(cx, cy, r, 0, 6.2832f, WG.a, 2.6f); if (inCircle(cx, cy, 108)) knot(cx, cy, 3.0f, WG.b); } }
  WG.i++;
}
// 65 kikkō: hexagons, then a small red motif in each
static void initKik() { wagGround(); WG.sc = frandr(24, 44); WG.i = -5; WG.j = -5; WG.phase = 0; }
static void stepKik() {
  float R = WG.sc, w = 1.732f * R; if (WG.j > 5) { if (WG.phase == 0) { WG.phase = 1; WG.i = -5; WG.j = -5; return; } genComplete = true; return; }
  float cx = 120 + WG.i * w + (WG.j & 1 ? w / 2 : 0), cy = 120 + WG.j * 1.5f * R;
  if (sqrtf((cx - 120) * (cx - 120) + (cy - 120) * (cy - 120)) < 118 + R) {
    if (WG.phase == 0) { for (int k = 0; k < 6; k++) { float a0 = 1.0472f * k + 0.5236f, a1 = a0 + 1.0472f; float x0 = cx + R * cosf(a0), y0 = cy + R * sinf(a0), x1 = cx + R * cosf(a1), y1 = cy + R * sinf(a1); dashes(x0, y0, x1, y1, 7, 3, 2.6f, WG.a); } }
    else if (inCircle(cx, cy, 108)) for (int k = 0; k < 3; k++) { float a = 1.0472f * k; stitch(cx - R * 0.28f * cosf(a), cy - R * 0.28f * sinf(a), cx + R * 0.28f * cosf(a), cy + R * 0.28f * sinf(a), 2.2f, WG.b); } }
  if (++WG.i > 5) { WG.i = -5; WG.j++; }
}
// 66 hitomezashi: rows of alternating dashes, then columns; the maze appears
static void initHito() { wagGround(); WG.sc = frandr(9, 15); WG.n = (int)(240 / WG.sc) + 1; for (int i = 0; i < 64; i++) G.cells[i] = random(2); WG.i = 0; WG.phase = 0; }
static void stepHito() {
  float sp = WG.sc; int n = min(WG.n, 30); float o = 120 - sp * n / 2;
  if (WG.i > n) { if (WG.phase == 0) { WG.phase = 1; WG.i = 0; return; } genComplete = true; return; }
  for (int k = 0; k < n; k++) { if ((k + G.cells[(WG.phase * 32 + WG.i) & 63]) % 2) continue;
    if (WG.phase == 0) { float x = o + k * sp, y = o + WG.i * sp; if (inCircle(x + sp / 2, y, 114)) stitch(x + 1.5f, y, x + sp - 1.5f, y, 2.2f, WG.a); }
    else { float x = o + WG.i * sp, y = o + k * sp; if (inCircle(x, y + sp / 2, 114)) stitch(x, y + 1.5f, x, y + sp - 1.5f, 2.2f, WG.b); } }
  WG.i++;
}
// 67 kagome: three families of paired lines
static void initKag() { wagGround(); WG.sc = frandr(34, 60); WG.rot = frandr(0, 1.0f); WG.phase = 0; WG.i = -4; }
static void stepKag() {
  if (WG.phase >= 3) { genComplete = true; return; }
  float ang = WG.rot + 1.0472f * WG.phase; float dx = cosf(ang), dy = sinf(ang), nx = -dy, ny = dx;
  for (int o = -1; o <= 1; o += 2) { float off = WG.i * WG.sc + o * 5; float px0 = 120 + nx * off, py0 = 120 + ny * off; float fx = px0 - 120, fy = py0 - 120; float bq = 2 * (fx * dx + fy * dy), cq = fx * fx + fy * fy - 118 * 118, disc_ = bq * bq - 4 * cq;
    if (disc_ > 0) { float sq = sqrtf(disc_); float t0 = (-bq - sq) / 2, t1 = (-bq + sq) / 2; for (float t = t0; t < t1; t += 13) { float e = min(t1, t + 10); stitch(px0 + dx * t, py0 + dy * t, px0 + dx * e, py0 + dy * e, 3.0f, WG.a); } } }
  if (++WG.i > 4) { WG.i = -4; WG.phase++; }
}
// 68 yagasuri: arrow-feather columns, one fletching at a time
static void initYag() { WG.darkG = false; fillGround(C565(236, 228, 208), true); WG.a = INDIGO; WG.b = random(2) ? INDIGO_L : VERM; WG.sc = frandr(30, 50); WG.i = 0; WG.j = -2; }
static void stepYag() {
  float cw = WG.sc, fh = cw * 1.1f; int cols = (int)(240 / cw) + 2; if (WG.i >= cols) { genComplete = true; return; }
  float x0 = -cw + WG.i * cw, y0 = -fh + WG.j * fh + ((WG.i % 2) ? fh / 2 : 0); bool flip = WG.i % 2;
  for (int side = -1; side <= 1; side += 2) { float xa = x0 + cw / 2, xb = xa + side * cw / 2; float xs[4], ys[4];
    if (!flip) { xs[0] = xa; ys[0] = y0; xs[1] = xb; ys[1] = y0 - fh * 0.4f; xs[2] = xb; ys[2] = y0 + fh * 0.42f; xs[3] = xa; ys[3] = y0 + fh * 0.82f; }
    else { xs[0] = xa; ys[0] = y0 + fh * 0.82f; xs[1] = xb; ys[1] = y0 + fh * 1.22f; xs[2] = xb; ys[2] = y0 + fh * 0.4f; xs[3] = xa; ys[3] = y0; }
    fillQuad(xs, ys, side == 1 ? WG.a : WG.b, 1.5708f + side * 0.6f); }
  dashes(x0 + cw / 2, y0 - 2, x0 + cw / 2, y0 + fh, 8, 3, 2.0f, CREAM);
  if (++WG.j * fh > 260) { WG.j = -2; WG.i++; }
}
// 69 kanoko shibori: rings of dye, from the centre out
static void initKan() { wagGround(); if (!WG.darkG) { fillGround(INDIGO, true); WG.darkG = true; WG.a = CREAM; } WG.sc = frandr(26, 40); WG.i = 0; WG.j = 0; }
static void stepKan() {
  float sp = WG.sc; int gi, gj;
  if (!ringCell(WG.j, WG.i, gi, gj)) { WG.j++; WG.i = 0; if (WG.j > 5) genComplete = true; return; }
  WG.i++;
  float x = 120 + gi * sp + (gj & 1 ? sp / 2 : 0), y = 120 + gj * sp * 0.87f; if (!inCircle(x, y, 110)) return;
  float r = sp * 0.33f; for (int q = 0; q < 14; q++) { float a0 = 0.4488f * q + frandr(-0.1f, 0.1f), a1 = a0 + 0.3f; stitch(x + r * cosf(a0), y + r * sinf(a0), x + r * cosf(a1), y + r * sinf(a1), 3.2f, shade(WG.a, 0.85f + 0.2f * frand())); }
  knot(x, y, r * 0.25f, shade(WG.a, 0.8f));
}

// ---------------- dispatch ----------------
static const bool GEN_EVOLVING[GEN_COUNT] = {true, false, false, true, true, true, false, true, false, true, false, false,
                                            false, false, false, false, false, false, false, false, false, false,
                                            false, false, false, false, false, false, false, false, false, false,
                                            false, true, true, false, false, false, true, false, false, true,
                                            true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true,
                                            false, false, false, false, false, false, false, false};
static void genInit(int id) { G.id = id; G.steps = 0; genComplete = false; genEvolving = GEN_EVOLVING[id]; slowFade = 0; TS.down = false; TS.ev = -1;
  switch (id) { case 0: initWander(); break; case 1: initSpiro(); break; case 2: initVine(); break; case 3: initLiss(); break; case 4: initSash(); drawSash(); break;
                case 5: initPatch(); break; case 6: initMand(); break; case 7: initFlow(); break; case 8: initPhyl(); break; case 9: initLife(); break; case 10: grannyNew(false); break; case 11: grannyNew(true); break; case 32: initTuring(); break; case 33: initTruchet(); break; case 34: initFlock(); break; case 35: initDLA(); break; case 36: initPack(); break;
                case 37: initSub(); break; case 38: initContours(); break; case 39: initAttr(); break; case 40: initHarm(); break; case 41: initMolnar(); break;
                case 42: initTSeam(); break; case 43: initTSatin(); break; case 44: initTBloom(); break; case 45: initTRipple(); break; case 46: initTKnots(); break;
                case 47: initTFlock(); break; case 48: initTCrystal(); break; case 49: initTVine(); break; case 50: initTWeb(); break; case 51: initTGranny(); break;
                case 52: initTRose(); break; case 53: initTAsawa(); break; case 54: initTMend(); break; case 55: initTButtons(); break; case 56: initTKaleido(); break;
                case 57: initTString(); break; case 58: initTContours(); break; case 59: initTShibori(); break; case 60: initTLife(); break; case 61: initTTruchet(); break;
                case 62: initSeig(); break; case 63: initAsa(); break; case 64: initShip(); break; case 65: initKik(); break; case 66: initHito(); break; case 67: initKag(); break; case 68: initYag(); break; case 69: initKan(); break;
                default: if (id >= 22) asawaNew(id - 22); else floraInit(id - 12); } }
static void genStep() {
  if (genComplete) {
    if (!genSlow) return;                                   // hold the finished piece until the slot ends
    if (++slowFade % 3 == 0) fadeToGround(5);               // slow mode: dissolve gently, then begin a new one
    if (slowFade > 240) { int id = G.id; genInit(id); }
    return;
  }
  switch (G.id) { case 0: stepWander(); break; case 1: stepSpiro(); break; case 2: stepVine(); break; case 3: stepLiss(); break; case 4: stepSash(); break;
                  case 5: stepPatch(); break; case 6: stepMand(); break; case 7: stepFlow(); break; case 8: stepPhyl(); break; case 9: stepLife(); break; case 10: grannyStep(false); break; case 11: grannyStep(true); break; case 32: stepTuring(); break; case 33: stepTruchet(); break; case 34: stepFlock(); break; case 35: stepDLA(); break; case 36: stepPack(); break;
                  case 37: stepSub(); break; case 38: stepContours(); break; case 39: stepAttr(); break; case 40: stepHarm(); break; case 41: stepMolnar(); break;
                  case 42: stepTSeam(); break; case 43: stepTSatin(); break; case 44: stepTBloom(); break; case 45: stepTRipple(); break; case 46: stepTKnots(); break;
                  case 47: stepTFlock(); break; case 48: stepTCrystal(); break; case 49: stepTVine(); break; case 50: stepTWeb(); break; case 51: stepTGranny(); break;
                  case 52: stepTRose(); break; case 53: stepTAsawa(); break; case 54: stepTMend(); break; case 55: stepTButtons(); break; case 56: stepTKaleido(); break;
                  case 57: stepTString(); break; case 58: stepTContours(); break; case 59: stepTShibori(); break; case 60: stepTLife(); break; case 61: stepTTruchet(); break;
                  case 62: stepSeig(); break; case 63: stepAsa(); break; case 64: stepShip(); break; case 65: stepKik(); break; case 66: stepHito(); break; case 67: stepKag(); break; case 68: stepYag(); break; case 69: stepKan(); break;
                  default: if (G.id >= 22) asawaStep(); else floraStep(); }
  G.steps++;
}
// "gen_x" -> id; "gen_x_slow" -> id with slow flag (bit 8)
static int genIndex(const char *name) {
  char base[32]; strncpy(base, name, 31); base[31] = 0; int n = strlen(base);
  bool slow = n > 5 && strcmp(base + n - 5, "_slow") == 0; bool flow = n > 5 && strcmp(base + n - 5, "_flow") == 0; if (slow || flow) base[n - 5] = 0;
  for (int i = 0; i < GEN_COUNT; i++) if (strcmp(base, GEN_NAMES[i]) == 0) return i | (slow ? 256 : 0) | (flow ? 512 : 0);
  return -1;
}
static bool genCanSwitch() { return genComplete || genEvolving || genSlow; }
