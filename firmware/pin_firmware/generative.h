// generative.h — ten procedural stitching patterns drawn live on the pin.
// Each has init() (new random parameters) and step() (adds a few stitches).
// Old thread slowly fades into the ground so the piece evolves forever.
#pragma once
#include <Arduino.h>
#include <math.h>

extern uint16_t *frameBuf;
#define GW 240
#define GH 240
#define GEN_COUNT 32
static const char *GEN_NAMES[GEN_COUNT] = {"gen_wander", "gen_spirograph", "gen_vine", "gen_lissajous", "gen_sashiko_drift",
                                           "gen_patchwork", "gen_mandala", "gen_flowfield", "gen_phyllotaxis", "gen_life_x", "gen_granny_square", "gen_granny_shapes",
                                           "gen_roses_cream", "gen_roses_black", "gen_daisies_cream", "gen_daisies_black", "gen_lavender_cream", "gen_lavender_black",
                                           "gen_blossom_cream", "gen_blossom_black", "gen_ferns_cream", "gen_ferns_black",
                                           "gen_asawa_lobes_cream", "gen_asawa_lobes_black", "gen_asawa_nested_cream", "gen_asawa_nested_black", "gen_asawa_tied_cream", "gen_asawa_tied_black",
                                           "gen_asawa_column_cream", "gen_asawa_column_black", "gen_asawa_loops_cream", "gen_asawa_loops_black"};

// ---------------- palette / colour helpers ----------------
static inline uint16_t C565(int r, int g, int b) { return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3); }
static inline void C888(uint16_t c, int &r, int &g, int &b) { r = (c >> 8) & 0xF8; g = (c >> 3) & 0xFC; b = (c << 3) & 0xF8; }
static uint16_t shade(uint16_t c, float f) { int r, g, b; C888(c, r, g, b); r = constrain(int(r * f), 0, 255); g = constrain(int(g * f), 0, 255); b = constrain(int(b * f), 0, 255); return C565(r, g, b); }
static uint16_t lerp565(uint16_t a, uint16_t b, int t) { int ar, ag, ab, br, bg, bb; C888(a, ar, ag, ab); C888(b, br, bg, bb); return C565(ar + (br - ar) * t / 256, ag + (bg - ag) * t / 256, ab + (bb - ab) * t / 256); }
static const uint16_t PAL[] = {C565(214, 168, 58), C565(124, 34, 42), C565(72, 132, 130), C565(236, 226, 204), C565(96, 58, 92), C565(178, 92, 52), C565(132, 150, 100)};
static const uint16_t CREAM = C565(238, 230, 210), INDIGO = C565(38, 52, 96), VERM = C565(196, 66, 44), SOOT = C565(30, 27, 29);
static uint16_t ground = 0, groundShadow = 0;
static inline bool inCircle(float x, float y, float r = 118) { float dx = x - 120, dy = y - 120; return dx * dx + dy * dy < r * r; }
static float frand() { return random(0, 10000) / 10000.0f; }
static float frandr(float a, float b) { return a + (b - a) * frand(); }

// ---------------- drawing primitives ----------------
static inline void px(int x, int y, uint16_t c) { if ((unsigned)x < GW && (unsigned)y < GH) frameBuf[y * GW + x] = c; }
static void disc(float cx, float cy, float r, uint16_t c) {
  int x0 = floorf(cx - r), x1 = ceilf(cx + r), y0 = floorf(cy - r), y1 = ceilf(cy + r); float r2 = r * r;
  for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) { float dx = x + 0.5f - cx, dy = y + 0.5f - cy; if (dx * dx + dy * dy <= r2) px(x, y, c); }
}
static void thick(float x0, float y0, float x1, float y1, float w, uint16_t c) {
  float dx = x1 - x0, dy = y1 - y0, L = sqrtf(dx * dx + dy * dy); int n = max(1, int(L / 0.6f));
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
  if (G.i > 3000 * G.n / 3) { fadeToGround(90); G.a = random(40, 100); G.b = random(7, 45); G.c = random(10, 70); G.i = 0; }
  else if (G.steps % 30 == 0) fadeToGround(4);
}
// ---- 2 vine: branching growth with leaves and knot flowers
static void initVine() { fillGround(C565(232, 224, 204), true); G.branches = 1; G.branchX[0] = 120 + frandr(-40, 40); G.branchY[0] = 236; G.branchA[0] = -1.57f + frandr(-0.3f, 0.3f); G.branchL[0] = 1; }
static void stepVine() {
  if (G.branches == 0 || G.steps % 400 == 399) { fadeToGround(60); G.branches = 1; G.branchX[0] = frandr(30, 210); G.branchY[0] = frandr(30, 210); G.branchA[0] = frandr(0, 6.28f); G.branchL[0] = 1; }
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
  } else { G.i++; G.e = 0; G.pcol = palRand(); G.f += frandr(-0.2f, 0.2f); if (ro > 110) { fadeToGround(120); G.i = 1; G.n = random(5, 9); } }
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
    if (r > 108) { fadeToGround(140); G.i = 0; G.a = 2.39996f + frandr(-0.03f, 0.03f); G.b = frandr(5.5f, 7.5f); G.col = random(0, 7); return; }
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
  if (GR.done) { if (++GR.holdSteps > 250) { fadeToGround(255); grannyNew(shapes); } return; }
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
    if (++FL.quiet > 120) { fadeToGround(255); floraInit(FL.kind * 2 + FL.dark); }
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
  if (AS.done) { if (++AS.hold > 220) { fadeToGround(255); asawaNew(AS.kind * 2 + AS.dark); } return; }
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

// ---------------- dispatch ----------------
static void genInit(int id) { G.id = id; G.steps = 0;
  switch (id) { case 0: initWander(); break; case 1: initSpiro(); break; case 2: initVine(); break; case 3: initLiss(); break; case 4: initSash(); drawSash(); break;
                case 5: initPatch(); break; case 6: initMand(); break; case 7: initFlow(); break; case 8: initPhyl(); break; case 9: initLife(); break; case 10: grannyNew(false); break; case 11: grannyNew(true); break; default: if (id >= 22) asawaNew(id - 22); else floraInit(id - 12); } }
static void genStep() {
  switch (G.id) { case 0: stepWander(); break; case 1: stepSpiro(); break; case 2: stepVine(); break; case 3: stepLiss(); break; case 4: stepSash(); break;
                  case 5: stepPatch(); break; case 6: stepMand(); break; case 7: stepFlow(); break; case 8: stepPhyl(); break; case 9: stepLife(); break; case 10: grannyStep(false); break; case 11: grannyStep(true); break; default: if (G.id >= 22) asawaStep(); else floraStep(); }
  G.steps++;
}
static int genIndex(const char *name) { for (int i = 0; i < GEN_COUNT; i++) if (strcmp(name, GEN_NAMES[i]) == 0) return i; return -1; }
