#!/usr/bin/env python3
"""Ten more eyes: granny squares, quilting, and other yarn and fabric crafts.
usage: [EYES_OUT=eyes] python3 gen_eyes4.py [piece ...]   (exports the same files as gen_eyes2.py)"""
import math, random, sys
import gen_eyes2
from gen_eyes3 import *
from gen_eyes2 import _cache
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from gen_granny import square_rounds

gen_eyes2.BUILDS += ("granny", "log_cabin")
PINK, DARK = (214, 130, 150), (64, 58, 66)
ease = lambda u: 0.5 - 0.5 * math.cos(min(1.0, u) * math.pi)

# ------------------------------------------------------------------ 1 granny square, crocheted round by round
def granny(f, FR):
    if f == 0: random.seed(101); _cache["gs"] = (new_layer(), square_rounds(5, step=13, inner0=10, palette=[DARK, TEAL, SKY, CREAM, CREAM, OXBLOOD]), 0)
    L, ev, done = _cache["gs"]; target = int(len(ev) * ease((f + 1) / (FR * 0.8))); last = None
    while done < target: last = GG.run_event(L, ev[done]) or last; done += 1
    _cache["gs"] = (L, ev, done); F = L.copy()
    if done < len(ev):
        if last: hook(F, *last)
    else:
        g = min(1.0, (f - FR * 0.8 + 1) / 3); knot(F, 114, 113, 5.5 * g, WHITE)
        for k in range(7): yarn(F, petal((54 + 22 * k, 44), -math.pi / 2 + (k - 3) * 0.12, 13 * g + 1, 4.5), MUSTARD, 2.2)
    return F

# ------------------------------------------------------------------ 2 crocheted eye with a crocheted lid
def granny_blink(f, FR):
    if "gb" not in _cache:
        layers = []
        for pal in ([DARK, DARK, TEAL, SKY, CREAM, CREAM, MUSTARD], [PLUM, shade(PLUM, 1.25)] * 4):
            random.seed(102); T = new_layer()
            for e in circle_rounds(6, step=14, r0=11, palette=pal): GG.run_event(T, e)
            layers.append(T)
        _cache["gb"] = layers
    A, B = _cache["gb"]; L = A.copy(); u = f / FR; ph = TAU * u; random.seed(103)
    knot(L, 111 + 3 * math.sin(ph), 110, 6.0, WHITE)
    o = (0.5 + 0.5 * math.cos(ph)) ** 0.6; yl = 22 + 196 * (1 - o)
    edge = [(20 + 5 * i, yl + 16 * o * math.sin(math.pi * i / 40)) for i in range(41)]
    m = poly_mask([(20, 0), (220, 0)] + edge[::-1]); L.paste(B, (0, 0), ImageChops.multiply(m, B.split()[3]))
    vis = [q for q in edge if math.hypot(q[0] - 120, q[1] - 120) < 95]
    if len(vis) > 2:
        yarn(L, vis, shade(PLUM, 0.6), 3.4)
        for q in vis[3:-2:4]: yarn(L, petal(q, math.pi / 2, 10, 3.6), DARK, 1.8)
    return L

# ------------------------------------------------------------------ 3 trapunto: one cloth, padded and quilted
def puff(L, mask, k=0.5, r=7):
    a = ImageChops.multiply(ImageChops.invert(mask.filter(ImageFilter.GaussianBlur(r * S))), mask).point(lambda v: int(v * k))
    L.paste(Image.new("RGBA", (N, N), (60, 46, 30, 255)), (0, 0), a)

def trapunto(f, FR):
    L = new_layer(); random.seed(104); u = f / FR; ph = TAU * u; TH = (150, 136, 110)
    o = blink(u, [0.5], 0.1); c = (120 + 22 * math.sin(ph), 122)
    outside = lambda p: region(p[0], p[1], 120, 122, 112, 66, 56, 1, (0, 0), 0, 0) == "out" and math.hypot(p[0] - 120, p[1] - 120) < 114
    for k in range(-240, 481, 22):
        march(L, [(k, 0), (k + 240, 240)], TH, 4.5, 3, 1.5, 0, outside); march(L, [(k, 0), (k - 240, 240)], TH, 4.5, 3, 1.5, 0, outside)
    fu, fl = almond(120, 122, 104, 58, 48); up, lo = almond(120, 122, 104, 58 * o - 48 * (1 - o), 48); opening = poly_mask(up + lo[::-1])
    puff(L, poly_mask(fu + fl[::-1]), 0.5); puff(L, opening, 0.35)
    im = ImageChops.multiply(ellipse_mask(c[0], c[1], 36, 36), opening); puff(L, im, 0.6, 5)
    puff(L, ImageChops.multiply(ellipse_mask(c[0], c[1], 14, 14), opening), 0.9, 3)
    inside = lambda p: region(p[0], p[1], 120, 122, 104, 58, 48, o, (0, 0), 0, 0) == "sclera"
    march(L, ellipse_pts(c[0], c[1], 36, 36, 60), MUSTARD, 4.5, 2.5, 1.7, 0, inside); march(L, ellipse_pts(c[0], c[1], 14, 14, 30), TH, 3.5, 2.5, 1.5, 0, inside)
    for k in range(14):
        a = TAU * k / 14; march(L, [(c[0] + 18 * math.cos(a), c[1] + 18 * math.sin(a)), (c[0] + 32 * math.cos(a), c[1] + 32 * math.sin(a))], TH, 4, 2.5, 1.4, 0, inside)
    march(L, fu, TH, 4.5, 2.5, 1.7); march(L, lo, TH, 4.5, 2.5, 1.7); march(L, up, TH, 4.5, 2.5, 1.9)
    for k in range(9):
        t = 0.14 + 0.72 * k / 8; b = fu[int(t * 40)]; a = (t - 0.5) * 1.5
        march(L, [b, (b[0] + 17 * math.sin(a), b[1] - 17 * math.cos(a))], TH, 4.5, 2.5, 1.6)
    return L

# ------------------------------------------------------------------ 4 log cabin block, pieced strip by strip
def log_cabin(f, FR):
    if f == 0:
        strips = [((109, 109, 131, 131), SOOT, 0)]; x0, y0, x1, y1 = 109, 109, 131, 131; w = 13.5
        cols = [(SKY, TEAL), (TEAL, NAVY), (WHITE, CREAM), (CREAM, (212, 202, 180)), (MUSTARD, RUST), (PINK, OXBLOOD), (SAGE, PLUM)]
        for lt, dk in cols:
            strips.append(((x0, y0 - w, x1, y0), lt, 0)); y0 -= w
            strips.append(((x1, y0, x1 + w, y1), lt, 90)); x1 += w
            strips.append(((x0, y1, x1, y1 + w), dk, 0)); y1 += w
            strips.append(((x0 - w, y0, x0, y1), dk, 90)); x0 -= w
        _cache["lc"] = (new_layer(), strips, 0)
    L, strips, done = _cache["lc"]; target = int(len(strips) * ease((f + 1) / (FR * 0.8)))
    while done < target:
        (a, b, c, d_), col, ang = strips[done]; random.seed(105 + done)
        satin(L, poly_mask([(a, b), (c, b), (c, d_), (a, d_)]), col, ang, spacing=1.6, sheen=0.16, var=0.08, blur=0)
        march(L, [(a + 2, b + 2), (c - 2, b + 2), (c - 2, d_ - 2), (a + 2, d_ - 2), (a + 2, b + 2)], BONE if col != WHITE and col != CREAM else (170, 160, 140), 3.2, 2.4, 1.1)
        done += 1
    _cache["lc"] = (L, strips, done); F = L.copy()
    if 0 < done < len(strips):
        (a, b, c, d_), col, ang = strips[done - 1]; needle(F, (c - 2, d_ - 2) if ang == 0 else (a + 2, d_ - 2), (1, 0) if ang == 0 else (0, 1), BONE)
    elif done: knot(F, 115, 115, 4.5 * min(1.0, (f - FR * 0.8 + 1) / 3), WHITE)
    return F

# ------------------------------------------------------------------ 5 yo-yo quilt (Suffolk puffs)
def yoyo(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u; d = ImageDraw.Draw(L)
    o = blink(u, [0.5], 0.1); look = (22 * math.sin(ph), 0); outp = [SAGE, (214, 180, 150), (160, 124, 150), MUSTARD, RUST]
    for j in range(13):
        for i in range(12):
            x, y = 10 + 22 * i + (11 if j % 2 else 0), 6 + 19 * j
            if math.hypot(x - 120, y - 120) > 111: continue
            h = (i * 7 + j * 13) % 11; r = region(x, y, 120, 120, 106, 60, 50, o, look, 40, 15)
            col = {"out": outp[h % 5], "lid": (OXBLOOD, shade(OXBLOOD, 1.25))[h % 2], "sclera": (WHITE, CREAM)[h % 2], "pupil": SOOT, "iris": (TEAL, SKY)[h % 2]}[r]
            random.seed(106 + h + i + j * 12); satin(L, ellipse_mask(x, y, 10.6, 10.6), col, 30 * h, spacing=1.5, sheen=0.2, var=0.1, blur=0)
            for k in range(12):
                a = TAU * k / 12 + h; d.line([P(x + 2.6 * math.cos(a), y + 2.6 * math.sin(a)), P(x + 8.6 * math.cos(a + 0.25), y + 8.6 * math.sin(a + 0.25))], fill=shade(col, 0.68) + (255,), width=3)
            d.ellipse([P(x - 2.4, y - 2.4), P(x + 2.4, y + 2.4)], fill=shade(col, 0.35) + (255,))
    return L

# ------------------------------------------------------------------ 6 punch needle loops
def punch(f, FR):
    L = new_layer(); random.seed(107); u = f / FR; ph = TAU * u; d = ImageDraw.Draw(L)
    o = blink(u, [0.5], 0.09); look = (22 * math.sin(ph), 5 * math.sin(2 * ph)); R = lambda x, y: region(x, y, 120, 120, 98, 54, 44, o, look, 36, 14)
    for j in range(52):
        for i in range(46):
            x, y = 2 + 5.2 * i + (2.6 if j % 2 else 0), 2 + 4.6 * j; rr = math.hypot(x - 120, y - 120)
            if rr > 116: continue
            r = R(x, y); dx, dy = 1.0, 0.0
            if r == "out":
                col = RUST if rr > 103 else MUSTARD
                if rr > 103: dx, dy = -(y - 120) / rr, (x - 120) / rr
            elif any(R(x + ax, y + ay) == "out" for ax, ay in ((6, 0), (-6, 0), (0, 6), (0, -6))): col = OXBLOOD
            else:
                ex, ey = x - 120 - look[0], y - 120 - look[1]; dd = math.hypot(ex, ey) or 1
                col = {"lid": PLUM, "sclera": CREAM, "pupil": SOOT}.get(r) or (SKY if dd < 23 else TEAL)
                if r in ("iris", "pupil"): dx, dy = -ey / dd, ex / dd
            col = shade(col, 0.9 + 0.2 * random.random())
            a, b = (x - dx * 1.7, y - dy * 1.7), (x + dx * 1.7, y + dy * 1.7)
            d.line([P(a[0] + 0.4, a[1] + 0.8), P(b[0] + 0.4, b[1] + 0.8)], fill=shade(col, 0.5) + (255,), width=int(3.6 * S))
            d.line([P(*a), P(*b)], fill=col + (255,), width=int(3.0 * S))
            d.line([P(a[0], a[1] - 0.6), P(b[0], b[1] - 0.6)], fill=shade(col, 1.25) + (255,), width=int(1.0 * S))
    if o > 0.6: knot(L, 120 + look[0] - 9, 120 + look[1] - 10, 4.6, WHITE)
    return L

# ------------------------------------------------------------------ 7 needle felting: soft wool, no outlines
def soft(L, tex, vis, col, seed, r=2.6):
    T = felt(col, tex, seed); T.putalpha(ImageChops.multiply(vis.filter(ImageFilter.GaussianBlur(r * S)), T.split()[3])); L.alpha_composite(T)

def felted(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u
    o = blink(u, [0.5], 0.12); c = (120 + 20 * math.sin(ph), 124 + 4 * math.cos(ph))
    fu, fl = almond(120, 122, 104, 62, 50, p=0.6); full = poly_mask(fu + fl[::-1]); big = poly_mask(almond(120, 122, 112, 70, 58, p=0.6)[0] + almond(120, 122, 112, 70, 58, p=0.6)[1][::-1])
    up, lo = almond(120, 122, 104, 62 * o - 50 * (1 - o), 50, p=0.6); opening = poly_mask(up + lo[::-1])
    soft(L, big, full, PINK, 1); soft(L, big, opening, WHITE, 2)
    for r, col, sd in ((40, TEAL, 3), (27, SKY, 4), (14, SOOT, 5)):
        soft(L, ellipse_mask(c[0], c[1], r + 6, r + 6), ImageChops.multiply(ellipse_mask(c[0], c[1], r, r), opening), col, sd, 2.0)
    soft(L, ellipse_mask(c[0] - 9, c[1] - 10, 9, 9), ImageChops.multiply(ellipse_mask(c[0] - 9, c[1] - 10, 5, 5), opening), WHITE, 6, 1.2)
    for sx in (-1, 1):
        bm = ellipse_mask(120 + sx * 46, 46 - 4 * (1 - o), 30, 9, sx * 0.22); soft(L, ellipse_mask(120 + sx * 46, 46 - 4 * (1 - o), 36, 15, sx * 0.22), bm, MUSTARD, 7 + sx, 2.2)
    return L

# ------------------------------------------------------------------ 8 silk ribbon embroidery
def ribbon(L, pts, col, w):
    d = ImageDraw.Draw(L); pp = [P(*q) for q in pts]
    d.line([(x + 0.8 * S, y + 1.2 * S) for x, y in pp], fill=(0, 0, 0, 140), width=int(w * S), joint="curve")
    d.line(pp, fill=shade(col, 0.72) + (255,), width=int(w * S), joint="curve")
    d.line(pp, fill=col + (255,), width=int(w * S * 0.72), joint="curve")
    d.line([(x - 0.22 * w * S, y - 0.22 * w * S) for x, y in pp], fill=shade(col, 1.3) + (150,), width=max(1, int(w * S * 0.2)), joint="curve")

def ribbon_rose(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u
    up, lo = almond(120, 126, 102, 56, 46); random.seed(108)
    satin(L, poly_mask(up + lo[::-1]), WHITE, 10, spacing=1.6, sheen=0.12, var=0.05)
    for k in range(9):
        t = 0.12 + 0.76 * k / 8; b = up[int(t * 40)]; a = -math.pi / 2 + (t - 0.5) * 1.5 + 0.12 * math.sin(ph * 2 + k * 0.8)
        pt = petal(b, a, 26 + 4 * math.sin(math.pi * t), 6.5); col = (SKY, PLUM, PINK)[k % 3]
        random.seed(109 + k); satin(L, poly_mask(pt), col, math.degrees(a), spacing=1.4, sheen=0.4); ribbon(L, [b, (b[0] + 12 * math.cos(a), b[1] + 12 * math.sin(a))], shade(col, 0.8), 2.4)
    for k, t in enumerate((0.3, 0.5, 0.7)):
        b = lo[int(t * 40)]; pt = petal(b, math.pi / 2 + (t - 0.5) * 1.2, 20, 6); random.seed(120 + k); satin(L, poly_mask(pt), SAGE, 90, spacing=1.4, sheen=0.35)
    yarn(L, lo, GREEN, 2.6); yarn(L, up, GREEN, 3.4)
    rng = random.Random(110); th = 0.0; b = 9.0 / TAU; segs = []
    while 4 + b * th < 36: segs.append((th, rng.uniform(0.8, 1.25))); th += 0.85
    for i, (t0, v) in enumerate(segs):
        k = i / len(segs); col = shade(tuple(int(OXBLOOD[j] * (1 - k) + PINK[j] * k) for j in range(3)), v)
        ribbon(L, [(120 + (4 + b * (t0 + s)) * math.cos(t0 + s + ph), 126 + (4 + b * (t0 + s)) * math.sin(t0 + s + ph)) for s in (0, 0.25, 0.5, 0.75, 1.0)], col, 9.5)
    for a in (0, 2.1, 4.2): knot(L, 120 + 3 * math.cos(a + ph), 126 + 3 * math.sin(a + ph), 2.6, MUSTARD)
    return L

# ------------------------------------------------------------------ 9 Hardanger: kloster blocks and cut work
def hardanger(f, FR):
    L = new_layer(); random.seed(111); u = f / FR; ph = TAU * u; d = ImageDraw.Draw(L); HOLE = (46, 56, 76)
    o = blink(u, [0.5], 0.09); look = (12 * round(1.6 * math.sin(ph)), 0)
    R = lambda x, y: region(x, y, 120, 120, 102, 62, 62, o, look, 31, 7)
    for j in range(20):
        for i in range(20):
            x, y = 6 + 12 * i, 6 + 12 * j
            if math.hypot(x - 120, y - 120) > 110: continue
            r = R(x, y)
            if r == "out": continue
            vert = R(x, y - 12) == "out" or R(x, y + 12) == "out"; horz = R(x - 12, y) == "out" or R(x + 12, y) == "out"
            if vert or horz or r == "lid":
                for k in range(5):
                    t = -4.8 + 2.4 * k
                    if vert and not horz: stitch(L, (x + t, y - 5.2), (x + t, y + 5.2), WHITE, 2.0)
                    else: stitch(L, (x - 5.2, y + t), (x + 5.2, y + t), WHITE, 2.0)
            elif r in ("iris", "pupil"):
                d.rectangle([P(x - 5, y - 5), P(x + 5, y + 5)], fill=HOLE + (255,))
                for a, b in (((x - 6, y - 6), (x + 6, y - 6)), ((x - 6, y + 6), (x + 6, y + 6)), ((x - 6, y - 6), (x - 6, y + 6)), ((x + 6, y - 6), (x + 6, y + 6))): stitch(L, a, b, WHITE, 2.2)
                if r == "pupil" or (i + j) % 2 == 0:
                    stitch(L, (x - 5, y - 5), (x + 5, y + 5), WHITE, 0.9); stitch(L, (x - 5, y + 5), (x + 5, y - 5), WHITE, 0.9)
                if r == "pupil": knot(L, x, y, 2.8, WHITE)
            else:
                for a in range(4): stitch(L, (x, y), (x + 3.6 * math.cos(a * math.pi / 2 + math.pi / 4), y + 3.6 * math.sin(a * math.pi / 2 + math.pi / 4)), WHITE, 1.1)
    return L

# ------------------------------------------------------------------ 10 pom-pom on a string
def pompom(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u; d = ImageDraw.Draw(L)
    th = 0.2 * math.sin(ph); cx, cy = 120 + 170 * math.sin(th), -44 + 170 * math.cos(th); R = 78
    random.seed(112); yarn(L, [(120, -6), ((120 + cx) / 2, (cy - R) / 2), (cx, cy - R + 6)], MUSTARD, 3.0)
    rng = random.Random(113)
    for i in range(3000):
        r = (R + 6) * math.sqrt(rng.random()); a = rng.uniform(0, TAU); ln = rng.uniform(8, 15); da = rng.uniform(-0.5, 0.5) + 0.12 * math.sin(ph * 2 + i)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a); v = (1.08 - 0.42 * (r / R) ** 2) * rng.uniform(0.88, 1.08) * (1.06 if math.sin(a) < -0.3 else 0.96)
        d.line([P(x, y), P(x + ln * math.cos(a + da), y + ln * math.sin(a + da))], fill=shade(BONE, v) + (255,), width=int(1.5 * S))
    lag = 0.2 * math.sin(ph - 0.9); ix, iy = cx + 60 * (math.sin(lag) - math.sin(th)), cy + 2
    im = ellipse_mask(ix, iy, 31, 31); put_felt(L, felt(TEAL, im, 8), im); random.seed(114)
    blanket(L, ellipse_pts(ix, iy, 31, 31, 50)[:-1], shade(TEAL, 0.55), 5, 8, 1.4, ix, iy)
    px, py = ix + 10 * math.sin(lag * 3), iy + 5
    pm = ellipse_mask(px, py, 15, 15); put_felt(L, felt(SOOT, pm, 9), pm); knot(L, px - 6, py - 6, 4.0, WHITE)
    return L

PIECES4 = {
    "granny":       (granny,       64, 90, lambda: BLACK_BG, "eyes-crafts"),
    "granny_blink": (granny_blink, 40, 80, lambda: BLACK_BG, "eyes-crafts"),
    "trapunto":     (trapunto,     32, 80, lambda: bg_satin(81, (238, 230, 212), 90), "eyes-crafts"),
    "log_cabin":    (log_cabin,    40, 110, lambda: bg_linen(82), "eyes-crafts"),
    "yoyo":         (yoyo,         32, 90, lambda: bg_linen(83, (226, 216, 196)), "eyes-crafts"),
    "punch":        (punch,        32, 80, lambda: bg_linen(84), "eyes-crafts"),
    "felted":       (felted,       32, 80, lambda: bg_linen(85, (70, 96, 104)), "eyes-crafts"),
    "ribbon":       (ribbon_rose,  32, 80, lambda: bg_linen(86, (236, 230, 214)), "eyes-crafts"),
    "hardanger":    (hardanger,    32, 90, lambda: bg_linen(87, (150, 168, 190)), "eyes-crafts"),
    "pompom":       (pompom,       32, 80, lambda: BLACK_BG, "eyes-crafts"),
}
ALL.update(PIECES4)

if __name__ == "__main__": main(sys.argv[1:] or list(PIECES4))
