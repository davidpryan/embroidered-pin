#!/usr/bin/env python3
"""Twenty more embroidered eyes: ten in the gallery's own look, ten in other needlework traditions.
usage: [EYES_OUT=eyes] python3 gen_eyes3.py [piece ...]   (exports the same files as gen_eyes2.py)"""
import math, random, sys
from gen_eyes2 import *
from gen_eyes2 import _cache
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from gen_granny2 import heart_pts

FOLK_RED, GREEN, SILVER, BRASS = (200, 44, 56), (60, 150, 90), (214, 214, 222), (176, 140, 60)
def disc(r=116): return ellipse_mask(120, 120, r, r)

# ================================================================== ten in the gallery's look
def wink(f, FR):
    L = new_layer(); random.seed(61); u = f / FR; ph = TAU * u
    ol = blink(u, [0.25], 0.07); orr = min(blink(u, [0.25], 0.07), blink(u, [0.68], 0.16) ** 0.6)
    look = (6 * math.sin(ph), 1)
    for x, o, sx in ((70, ol, -1), (170, orr, 1)):
        yarn(L, [(x - 36 + i * 7.2, 78 + 5 * (1 - o) - 9 * math.sin(math.pi * i / 10) + sx * (i - 5) * 0.8) for i in range(11)], SOOT, 4.4)
        eye(L, x, 122, 42, 25, 19, o, look, 18, TEAL, MUSTARD, WHITE, SOOT, 3.8, lashes=5, lash_len=10, lash_w=2.0, lid=PLUM, seed=3)
    yarn(L, [(96 + i * 6, 178 + 7 * math.sin(math.pi * i / 8) * (1.4 - orr * 0.6)) for i in range(9)], OXBLOOD, 3.6)
    return L

def moon_eye(f, FR):
    L = new_layer(); random.seed(62); u = f / FR; ph = TAU * u
    for k in range(9):
        a = TAU * k / 9 + 0.3; tw = 0.6 + 0.4 * math.sin(ph * 2 + k * 2.2); x, y = 120 + 104 * math.cos(a), 120 + 104 * math.sin(a)
        for b in (0, math.pi / 2): yarn(L, [(x - 6 * tw * math.cos(b), y - 6 * tw * math.sin(b)), (x + 6 * tw * math.cos(b), y + 6 * tw * math.sin(b))], BONE, 2.2)
    satin(L, ellipse_mask(120, 120, 86, 86), MUSTARD, 35, spacing=1.6, sheen=0.3)
    for cx, cy, r in ((74, 84, 11), (168, 170, 14), (160, 70, 7), (84, 172, 6)): yarn(L, ellipse_pts(cx, cy, r, r, 30, 0, 0.6, 4.2), shade(MUSTARD, 0.7), 2.2)
    yarn(L, ellipse_pts(120, 120, 87, 87, 80), shade(MUSTARD, 0.6), 2.6)
    o = blink(u, [0.5], 0.14)
    eye(L, 120, 122, 60, 33, 27, o, (13 * math.sin(ph), 2), 25, TEAL, None, BONE, SOOT, 4.2, lid=shade(MUSTARD, 0.78), lid_ang=35, seed=4)
    return L

def heart_eye(f, FR):
    L = new_layer(); random.seed(63); u = f / FR; ph = TAU * u
    pulse = 1.0 + 0.22 * max(0.0, math.sin(ph * 2)) ** 2; c = (120 + 8 * math.sin(ph), 124)
    def inner(E):
        iris(E, c[0], c[1], 42, SKY, 0.05, 6, WHITE, glint=False)
        hp = heart_pts(c[0], c[1] - 2, 1.05 * pulse); satin(E, poly_mask(hp), FOLK_RED, 90, spacing=1.3, sheen=0.35, shadow=False)
        yarn(E, hp + [hp[0]], OXBLOOD, 1.8); knot(E, c[0] - 8 * pulse, c[1] - 9 * pulse, 3.0, WHITE)
    eye(L, 120, 122, 100, 56, 44, blink(u, [0.0], 0.07), line=SOOT, lw=5.0, scl=WHITE, inner=inner, lashes=9, lash_len=17, lash_w=2.6, lid=(214, 130, 150))
    for k in range(3):
        v = (u + k / 3) % 1; s = 0.45 * min(1, v * 4) * min(1, (1 - v) * 3)
        if s > 0.08: hp = heart_pts(40 + 70 * k + 8 * math.sin(v * 5 + k), 214 - 40 * v, s); yarn(L, hp + [hp[0]], FOLK_RED, 2.0)
    return L

def keyhole(f, FR):
    L = new_layer(); random.seed(64); u = f / FR; ph = TAU * u
    if "key" not in _cache:
        hole = ImageChops.lighter(ellipse_mask(120, 96, 38, 38), poly_mask([(106, 118), (134, 118), (152, 196), (88, 196)]))
        P_ = new_layer(); random.seed(64); satin(P_, ImageChops.subtract(disc(119), hole), BRASS, 62, spacing=1.6, sheen=0.4, shadow=False, var=0.08)
        _cache["key"] = (hole, P_)
    hole, plate = _cache["key"]
    y = 98 + 62 * (0.5 - 0.5 * math.cos(ph)) ** 2; x = 120 + 9 * math.sin(ph * 2) * (1 - (y - 98) / 80)
    E = new_layer(); eye(E, x, y, 31, 19, 15, blink(u, [0.25, 0.8], 0.06), (5 * math.sin(ph * 3), 0), 14, TEAL, MUSTARD, BONE, BONE, 3.0, seed=5)
    L.paste(E, (0, 0), ImageChops.multiply(hole, E.split()[3])); L.paste(plate, (0, 0), plate)
    yarn(L, ellipse_pts(120, 96, 38, 38, 60, 0, 1.95, 1.19 + TAU), shade(BRASS, 0.5), 3.2)
    yarn(L, [(106, 126), (88, 196), (152, 196), (134, 126)], shade(BRASS, 0.5), 3.2)
    for sx, sy in ((48, 60), (192, 60), (48, 180), (192, 180)):
        bigknot(L, sx, sy, 7, shade(BRASS, 1.25)); yarn(L, [(sx - 4, sy - 3), (sx + 4, sy + 3)], shade(BRASS, 0.5), 1.6)
    return L

def peacock(f, FR):
    L = new_layer(); random.seed(65); u = f / FR; ph = TAU * u; sway = 5 * math.sin(ph)
    yarn(L, [(120 + sway * (1 - t) * 0, 236 - t * 100) for t in (0, 0.5, 1)], BONE, 3.0)
    for k in range(46):
        a = -math.pi / 2 + (k - 22.5) * 0.125 + 0.05 * math.sin(ph + k * 0.5); r1 = 104 + 8 * math.sin(k * 1.7)
        yarn(L, [(120 + 40 * math.cos(a), 130 + 46 * math.sin(a)), (120 + sway * 0.5 + r1 * 0.75 * math.cos(a), 130 + r1 * 0.75 * math.sin(a) + 2), (120 + sway + r1 * math.cos(a), 130 + r1 * math.sin(a) + 6)],
             (SAGE, TEAL, GREEN)[k % 3], 1.8)
    sh = 25 * math.sin(ph)
    for cx, cy, rx, ry, col, ang in ((120, 112, 56, 70, SAGE, 80), (120, 118, 44, 54, MUSTARD, 100), (120, 124, 33, 39, (30, 150, 160), 60), (120, 130, 20, 23, NAVY, 120)):
        satin(L, ellipse_mask(cx, cy, rx, ry), col, ang + sh, spacing=1.5, sheen=0.4, shadow=(col == SAGE))
        yarn(L, ellipse_pts(cx, cy, rx, ry, 60), shade(col, 0.6), 1.8)
    knot(L, 113, 123, 4.0, BONE)
    return L

def hamsa(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u
    if "hamsa" not in _cache:
        m = ellipse_mask(120, 150, 54, 50)
        for x, top in ((90, 66), (120, 48), (150, 66)):
            m = ImageChops.lighter(m, poly_mask([(x - 13, 150), (x - 13, top + 13)] + ellipse_pts(x, top + 13, 13, 13, 20, 0, math.pi, TAU) + [(x + 13, top + 13), (x + 13, 150)]))
        for sx in (-1, 1): m = ImageChops.lighter(m, ellipse_mask(120 + sx * 58, 132, 15, 36, sx * 0.75))
        H = new_layer(); random.seed(66); satin(H, m, TEAL, 90, spacing=1.6, sheen=0.3)
        edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(13)), m); H.paste(shade(TEAL, 0.5) + (255,), (0, 0, N, N), edge)
        _cache["hamsa"] = H
    L.paste(_cache["hamsa"], (0, 0), _cache["hamsa"]); random.seed(67)
    for i, (x, top) in enumerate(((90, 66), (120, 48), (150, 66))):
        backstitch(L, [(x, top + 16), (x, 108)], BONE, width=1.6, dash=4, gap=3)
        bigknot(L, x, top + 12, 4.4 * (0.75 + 0.25 * math.sin(ph * 2 + i * 2.1)), MUSTARD)
    for k in range(11):
        a = math.pi * k / 10; knot(L, 120 + 46 * math.cos(a), 156 + 40 * math.sin(a), 2.2, BONE)
    eye(L, 120, 150, 36, 22, 17, blink(u, [0.5], 0.1), (7 * math.sin(ph), 0), 16, OXBLOOD, MUSTARD, BONE, SOOT, 3.4, lid=shade(TEAL, 0.8), seed=6)
    return L

def sun_eye(f, FR):
    L = new_layer(); random.seed(68); u = f / FR; ph = TAU * u
    for k in range(12):
        a = TAU * k / 12 + TAU / 6 * u; r1 = 112 if k % 2 == 0 else 96; hw = 0.21
        tri = [(120 + 60 * math.cos(a - hw), 120 + 60 * math.sin(a - hw)), (120 + r1 * math.cos(a), 120 + r1 * math.sin(a)), (120 + 60 * math.cos(a + hw), 120 + 60 * math.sin(a + hw))]
        random.seed(68 + k % 2); satin(L, poly_mask(tri), (MUSTARD, RUST)[k % 2], math.degrees(a), spacing=1.5, sheen=0.3)
    random.seed(70); satin(L, ellipse_mask(120, 120, 62, 62), MUSTARD, 20, spacing=1.6, sheen=0.3)
    yarn(L, ellipse_pts(120, 120, 62, 62, 70), shade(MUSTARD, 0.6), 2.6)
    eye(L, 120, 120, 46, 27, 22, blink(u, [0.5], 0.09), (9 * math.sin(ph), 0), 20, TEAL, None, BONE, SOOT, 3.8, lid=RUST, seed=7)
    return L

def daisy_eye(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u; cx, cy = 120 + 7 * math.sin(ph), 104
    random.seed(71); yarn(L, [(120, 238), (120 + 3 * math.sin(ph), 190), (cx, cy + 40)], SAGE, 5.0)
    for sx in (-1, 1):
        lp = petal((120 + 2 * math.sin(ph), 196), -math.pi / 2 + sx * 0.9, 40, 9); satin(L, poly_mask(lp), SAGE, 60 * sx, spacing=1.5, sheen=0.25)
    for k in range(12):
        a = TAU * k / 12 + 0.05 * math.sin(ph * 2 + k * 1.3); random.seed(72 + k)
        satin(L, ellipse_mask(cx + 62 * math.cos(a), cy + 62 * math.sin(a), 30, 12.5, a), BONE, math.degrees(a), spacing=1.5, sheen=0.22)
        yarn(L, [(cx + 36 * math.cos(a), cy + 36 * math.sin(a)), (cx + 84 * math.cos(a), cy + 84 * math.sin(a))], shade(BONE, 0.78), 1.4)
    random.seed(90); satin(L, ellipse_mask(cx, cy, 38, 38), MUSTARD, 30, spacing=1.5, sheen=0.3)
    for k in range(16): knot(L, cx + 33 * math.cos(TAU * k / 16), cy + 33 * math.sin(TAU * k / 16), 2.4, RUST)
    eye(L, cx, cy, 29, 18, 15, blink(u, [0.3, 0.42], 0.05), (5 * math.sin(ph * 2), 0), 13, TEAL, None, BONE, SOOT, 3.0, seed=8)
    return L

def clock_eye(f, FR):
    L = new_layer(); random.seed(73); u = f / FR
    def inner(E):
        backstitch(E, ellipse_pts(120, 120, 47, 47, 60), SOOT, width=2.6, dash=6, gap=1)
        for k in range(12):
            a = TAU * k / 12 - math.pi / 2; q = (120 + 39 * math.cos(a), 120 + 39 * math.sin(a))
            if k % 3 == 0: bigknot(E, q[0], q[1], 3.6, OXBLOOD)
            else: knot(E, q[0], q[1], 2.0, SOOT)
        for a, ln, w_, col in ((-math.pi / 2 - 1.05, 22, 4.0, SOOT), (-math.pi / 2 + 1.05, 32, 3.2, SOOT), (TAU * f / FR - math.pi / 2, 36, 1.8, OXBLOOD)):
            yarn(E, [(120, 120), (120 + ln * math.cos(a), 120 + ln * math.sin(a))], col, w_)
        bigknot(E, 120, 120, 5, MUSTARD)
    eye(L, 120, 120, 104, 62, 56, blink(u, [0.5], 0.08), line=SOOT, lw=5.0, scl=WHITE, inner=inner, lashes=9, lash_len=15, lash_w=2.6, lid=PLUM)
    return L

def googly(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u
    for i, x in enumerate((70, 170)):
        random.seed(74 + i); y = 124 + 3 * math.sin(ph * 2 + i)
        satin(L, ellipse_mask(x, y, 44, 44), WHITE, 15, spacing=1.6, sheen=0.14, var=0.05)
        th = math.pi / 2 + 1.5 * math.sin(ph + i * 0.7) * (1 if i == 0 else -1); px, py = x + 21 * math.cos(th), y + 21 * math.sin(th)
        satin(L, ellipse_mask(px, py, 21, 21), SOOT, 40, spacing=1.4, sheen=0.3, shadow=False); knot(L, px - 7, py - 8, 4.2, WHITE)
        yarn(L, ellipse_pts(x, y, 44, 44, 60), SOOT, 4.4)
        yarn(L, [(x - 30, 62 - 6 * math.sin(ph * 2 + i * 2)), (x, 54 - 8 * math.sin(ph * 2 + i * 2)), (x + 30, 62 - 6 * math.sin(ph * 2 + i * 2))], OXBLOOD, 5.0)
    return L

# ================================================================== ten more crafts
def kantha(f, FR):
    L = new_layer(); random.seed(81); u = f / FR; ph = TAU * u
    cols = [OXBLOOD, TEAL, MUSTARD, NAVY, RUST, SAGE]; keep = lambda p: math.hypot(p[0] - 120, p[1] - 120) < 113
    for k in range(13):
        s = (0.5 + 0.13 * k) * (1 + 0.035 * math.sin(ph - k * 0.7)); up, lo = almond(120, 120, 74 * s, 42 * s, 36 * s)
        march(L, up + lo[::-1] + [up[0]], cols[k % 6], 6.5, 4, 1.9, (u * 21) * (1 if k % 2 else -1), keep)
    c = (120 + 6 * math.sin(ph), 120)
    for r, col in ((24, NAVY), (17, TEAL), (10, NAVY)): march(L, ellipse_pts(c[0], c[1], r, r, 40), col, 5, 3, 2.0, u * 16)
    bigknot(L, c[0], c[1], 5, OXBLOOD)
    return L

def bargello(f, FR):
    L = new_layer(); random.seed(82); u = f / FR; ph = TAU * u
    o = blink(u, [0.5], 0.09); look = (20 * math.sin(ph), 0); shift = u * 36
    pal = {"out": (OXBLOOD, RUST, MUSTARD), "sclera": (WHITE, CREAM, (212, 202, 180)), "iris": (TEAL, SKY, NAVY),
           "pupil": (INK, SOOT, (62, 56, 64)), "lid": (PLUM, shade(PLUM, 1.35), shade(PLUM, 0.7))}
    for i in range(48):
        x = 2.5 + 5 * i; z = 10 * abs(((i / 8) % 2) - 1)
        for j in range(-4, 22):
            y0 = 12 * j + z + shift - 12; ym = y0 + 5.5
            if math.hypot(x - 120, ym - 120) > 117: continue
            r = region(x, ym, 120, 122, 100, 54, 44, o, look, 34, 14)
            stitch(L, (x, y0), (x, y0 + 10.6), pal[r][j % 3], 3.9)
    return L

def sequins(f, FR):
    L = new_layer(); random.seed(83); u = f / FR; ph = TAU * u; d = ImageDraw.Draw(L)
    o = blink(u, [0.75], 0.09); look = (22 * math.sin(ph), 4 * math.sin(2 * ph))
    for j in range(27):
        for i in range(22):
            x, y = 5 + 11 * i + (5.5 if j % 2 else 0), 10 + 8.4 * j
            r = region(x, y, 120, 120, 100, 56, 46, o, look, 36, 14)
            if r == "out": continue
            dd = math.hypot(x - 120 - look[0], y - 120 - look[1])
            col = {"lid": PLUM, "sclera": SILVER, "pupil": (44, 40, 50)}.get(r) or (GOLD if dd < 23 else TEAL)
            b = 0.82 + 0.55 * max(0, math.sin(ph - (x + y) * 0.035)) ** 8
            d.ellipse([P(x - 6.2, y - 5.2), P(x + 7.2, y + 7.6)], fill=(0, 0, 0, 130))
            d.ellipse([P(x - 6.6, y - 6.6), P(x + 6.6, y + 6.6)], fill=shade(col, b * 0.72) + (255,))
            d.ellipse([P(x - 5.6, y - 6.0), P(x + 4.8, y + 4.4)], fill=shade(col, b) + (255,))
            d.ellipse([P(x - 1.1, y - 1.1), P(x + 1.1, y + 1.1)], fill=INK + (255,))
            d.line([P(x, y), P(x, y - 6.4)], fill=shade(col, 0.5) + (255,), width=2)
    fu, fl = almond(120, 120, 104, 60, 50); yarn(L, fu, GOLD, 3.4); yarn(L, fl, GOLD, 3.4)
    return L

def quilt(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u
    o = blink(u, [0.5], 0.1); look = (24 * math.sin(ph), 0); outp = [SAGE, MUSTARD, RUST, (150, 110, 140), TEAL]
    for gy in range(8):
        for gx in range(8):
            x0, y0 = gx * 30, gy * 30; a, b, c, d_ = (x0, y0), (x0 + 30, y0), (x0 + 30, y0 + 30), (x0, y0 + 30)
            tris = ((a, b, c), (a, c, d_)) if (gx + gy) % 2 else ((a, b, d_), (b, c, d_))
            for t, tri in enumerate(tris):
                mx, my = sum(q[0] for q in tri) / 3, sum(q[1] for q in tri) / 3
                if math.hypot(mx - 120, my - 120) > 132: continue
                h = (gx * 7 + gy * 13 + t * 5) % 11; r = region(mx, my, 120, 120, 112, 64, 54, o, look, 42, 15)
                dd = math.hypot(mx - 120 - look[0], my - 120)
                col = {"out": outp[h % 5], "lid": (OXBLOOD, shade(OXBLOOD, 1.25))[h % 2], "sclera": (WHITE, CREAM)[h % 2], "pupil": SOOT}.get(r) or ((SKY, TEAL)[h % 2] if dd < 30 else NAVY)
                random.seed(h + gx + gy * 8); satin(L, poly_mask(tri), col, 45 * (h % 4), spacing=1.6, sheen=0.14, shadow=False, var=0.08, blur=0)
    random.seed(84)
    for k in range(0, 241, 30):
        march(L, [(k + 1.5, 0), (k + 1.5, 240)], BONE, 4, 3, 1.2); march(L, [(0, k + 1.5), (240, k + 1.5)], BONE, 4, 3, 1.2)
    return L

def eyelet(f, FR):
    L = new_layer(); random.seed(85); u = f / FR; ph = TAU * u; HOLE = (58, 78, 108); d = ImageDraw.Draw(L)
    up, lo = almond(120, 122, 100, 56, 46)
    satin(L, poly_mask(up + lo[::-1]), WHITE, 12, spacing=1.6, sheen=0.14, var=0.05)
    def hole(x, y, r):
        d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=HOLE + (255,)); yarn(L, ellipse_pts(x, y, r + 0.8, r + 0.8, 26), WHITE, 2.2)
    for crv, sg in ((up, -1), (lo, 1)):                        # scalloped buttonhole edge
        for i in range(2, 39, 4):
            p, q = crv[i - 2], crv[i + 2]; mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2; dx, dy = q[0] - p[0], q[1] - p[1]; m = math.hypot(dx, dy) or 1
            bul = 5 + 1.5 * math.sin(ph * 2 + i * 0.5)
            yarn(L, [p, (mx - dy / m * bul * sg, my + dx / m * bul * sg), q], WHITE, 2.6)
    c = (120 + 14 * math.sin(ph), 122)
    for k in range(10):
        a = TAU * k / 10 + TAU / 10 * u; hole(c[0] + 29 * math.cos(a), c[1] + 29 * math.sin(a), 5)
    hole(c[0], c[1], 13 + 3 * math.sin(ph * 2))
    for k in range(7):
        t = 0.14 + 0.72 * k / 6; b = up[int(t * 40)]; a = (t - 0.5) * 1.5; e = (b[0] + 16 * math.sin(a), b[1] - 16 * math.cos(a))
        yarn(L, [(b[0] + 6 * math.sin(a), b[1] - 6 * math.cos(a)), e], WHITE, 2.2); hole(e[0] + 4 * math.sin(a), e[1] - 4 * math.cos(a), 3.2)
    return L

def darned(f, FR):
    L = new_layer(); random.seed(86); u = f / FR; ph = TAU * u
    o = blink(u, [0.5], 0.1); look = (16 * math.sin(ph), 0)
    for j in range(25):
        for i in range(25):
            x, y = 24 + 8 * i, 24 + 8 * j
            if math.hypot(x - 120, y - 120) > 94: continue
            r = region(x, y, 120, 120, 78, 42, 34, o, look, 26, 10)
            col = {"out": RUST, "lid": MUSTARD, "sclera": WHITE, "iris": TEAL, "pupil": INK}[r]
            hz = lambda: stitch(L, (x - 4.6, y), (x + 4.6, y), col, 3.4); vt = lambda: stitch(L, (x, y - 4.6), (x, y + 4.6), CREAM, 3.0)
            (vt(), hz()) if (i + j) % 2 == 0 else (hz(), vt())
    march(L, ellipse_pts(120, 120, 103, 103, 80), MUSTARD, 7, 5, 2.2, u * 24)
    return L

def wheel(f, FR):
    L = new_layer(); random.seed(87); u = f / FR; ph = TAU * u
    up, lo = almond(120, 122, 102, 58, 48)
    satin(L, poly_mask(up + lo[::-1]), WHITE, 10, spacing=1.6, sheen=0.12, var=0.05)
    yarn(L, lo, OXBLOOD, 3.0); yarn(L, up, OXBLOOD, 4.6)
    for k in range(8):
        t = 0.14 + 0.72 * k / 7; b = up[int(t * 40)]; a = (t - 0.5) * 1.5
        yarn(L, [b, (b[0] + 16 * math.sin(a), b[1] - 16 * math.cos(a))], OXBLOOD, 2.6)
    n = 9; R = 42
    for k in range(n): yarn(L, [(120, 122), (120 + R * math.cos(TAU * k / n), 122 + R * math.sin(TAU * k / n))], shade(TEAL, 0.55), 2.0)
    rmax = 7 + 32 * (0.5 - 0.5 * math.cos(ph)); th = 0.0; pts = []; b = 5.2 / TAU
    while 4 + b * th < rmax:
        r = 4 + b * th + 1.3 * math.cos(th * n / 2); pts.append((120 + r * math.cos(th), 122 + r * math.sin(th))); th += 0.12
    cut = next((i for i, q in enumerate(pts) if math.hypot(q[0] - 120, q[1] - 122) > 17), len(pts))
    if cut > 1: yarn(L, pts[:cut + 1], MUSTARD, 3.6)
    if len(pts) - cut > 1: yarn(L, pts[cut:], TEAL, 3.6)
    if len(pts) > 2 and math.sin(ph) > 0: needle(L, pts[-1], (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]), TEAL)
    bigknot(L, 120, 122, 4.5, SOOT)
    return L

def folk(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u; cols = [FOLK_RED, MUSTARD, SKY, GREEN]
    for k in range(12):
        a = TAU * k / 12 - math.pi / 2; big = k % 2 == 0; ln = (46 if big else 30) + 5 * math.sin(ph * 2 + k * math.pi / 2)
        b = (120 + (62 if abs(math.cos(a)) > 0.5 else 44) * math.cos(a), 120 + 44 * math.sin(a) * (1.0 if abs(math.cos(a)) < 0.5 else 1.0))
        pt = petal(b, a, ln, 15 if big else 9); col = cols[(k // 2) % 4] if big else GREEN
        random.seed(88 + k); satin(L, poly_mask(pt), col, math.degrees(a) + 90, spacing=1.4, sheen=0.3)
        yarn(L, [b, (b[0] + ln * 0.8 * math.cos(a), b[1] + ln * 0.8 * math.sin(a))], shade(col, 0.6), 1.8)
        if big: knot(L, b[0] + (ln + 6) * math.cos(a), b[1] + (ln + 6) * math.sin(a), 3.0, BONE)
    random.seed(110)
    eye(L, 120, 120, 58, 34, 28, blink(u, [0.5], 0.09), (10 * math.sin(ph), 0), 25, SKY, MUSTARD, BONE, BONE, 4.0, lid=FOLK_RED, seed=9)
    return L

def lace(f, FR):
    L = new_layer(); random.seed(89); u = f / FR; ph = TAU * u; c = (120, 120)
    R = lambda x, y: region(x, y, 120, 120, 102, 58, 58, 1, (0, 0), 0, 0)
    for k in range(28):                                       # bars from the iris out to the edge
        a = TAU * k / 28; r = 44
        while R(c[0] + (r + 2) * math.cos(a), c[1] + (r + 2) * math.sin(a)) != "out" and r < 110: r += 2
        if r > 48: stitch(L, (c[0] + 42 * math.cos(a), c[1] + 42 * math.sin(a)), (c[0] + r * math.cos(a), c[1] + r * math.sin(a)), BONE, 1.0)
    up, lo = almond(120, 120, 102, 58, 58)
    chain(L, up + lo[::-1] + [up[0]], BONE, 7, 2.6, 1.2, u * 6)
    for crv, sg in ((up, -1), (lo, 1)):
        for i in range(3, 38, 3):
            p, q = crv[i - 1], crv[i + 1]; a = math.atan2(q[1] - p[1], q[0] - p[0]) + sg * math.pi / 2 * (1 if sg > 0 else 1)
            thread_loop(L, petal(crv[i], a if sg > 0 else a, 8 + 2.5 * math.sin(ph * 2 - i * 0.6), 4.2, 10), BONE, 1.1)
    for r, n, ln, wd, d in ((8, 8, 15, 5.5, 1), (26, 14, 14, 5, -1)):
        for k in range(n):
            a = TAU * k / n + d * TAU / n * u; thread_loop(L, petal((c[0] + r * math.cos(a), c[1] + r * math.sin(a)), a, ln, wd, 10), BONE, 1.2)
    chain(L, ellipse_pts(120, 120, 25, 25, 40), BONE, 6, 2.2, 1.1, -u * 5.1 * 2)
    chain(L, ellipse_pts(120, 120, 42, 42, 50), BONE, 7, 2.6, 1.2, u * 6 * 2)
    bigknot(L, 120, 120, 5, BONE)
    return L

def mola(f, FR):
    L = new_layer(); random.seed(91); u = f / FR; ph = TAU * u; D = disc(117)
    cols = [OXBLOOD, MUSTARD, TEAL, FOLK_RED, NAVY, BONE]; keep = lambda p: math.hypot(p[0] - 120, p[1] - 120) < 113
    for k in range(6):
        s = (1.8 - 0.26 * k) * (1 + 0.05 * math.sin(ph - k * 0.9)); up, lo = almond(120, 120, 62 * s, 38 * s, 32 * s)
        m = ImageChops.multiply(poly_mask(up + lo[::-1]), D)
        L.paste(Image.new("RGBA", (N, N), (0, 0, 0, 130)), (int(1.0 * S), int(1.5 * S)), m); L.paste(cols[k] + (255,), (0, 0, N, N), m)
        s2 = s - 0.07; iu, il = almond(120, 120, 62 * s2, 38 * s2, 32 * s2)
        march(L, iu + il[::-1] + [iu[0]], (BONE if k != 5 else SOOT), 3.2, 2.6, 1.2, 0, keep)
    c = (120 + 7 * math.sin(ph), 120)
    ImageDraw.Draw(L).ellipse([P(c[0] - 13, c[1] - 13), P(c[0] + 13, c[1] + 13)], fill=SOOT + (255,))
    march(L, ellipse_pts(c[0], c[1], 9.5, 9.5, 24), MUSTARD, 3, 2.4, 1.2); knot(L, c[0] - 4, c[1] - 5, 2.8, WHITE)
    return L

PIECES3 = {
    "wink":      (wink,      40, 80, lambda: bg_linen(61), "eyes"),
    "moon":      (moon_eye,  40, 80, lambda: BLACK_BG, "eyes"),
    "heart":     (heart_eye, 32, 80, lambda: bg_satin(62), "eyes"),
    "keyhole":   (keyhole,   40, 80, lambda: BLACK_BG, "eyes"),
    "peacock":   (peacock,   32, 80, lambda: BLACK_BG, "eyes"),
    "hamsa":     (hamsa,     32, 80, lambda: bg_linen(63), "eyes"),
    "sun":       (sun_eye,   32, 80, lambda: BLACK_BG, "eyes"),
    "daisy":     (daisy_eye, 32, 80, lambda: BLACK_BG, "eyes"),
    "clock":     (clock_eye, 32, 90, lambda: bg_satin(64, (240, 232, 214), 60), "eyes"),
    "googly":    (googly,    32, 80, lambda: bg_linen(65, (150, 164, 122)), "eyes"),
    "kantha":    (kantha,    32, 80, lambda: bg_linen(66, (238, 232, 216)), "eyes-crafts"),
    "bargello":  (bargello,  32, 80, lambda: bg_linen(67), "eyes-crafts"),
    "sequins":   (sequins,   32, 80, lambda: BLACK_BG, "eyes-crafts"),
    "quilt":     (quilt,     32, 90, lambda: bg_linen(68), "eyes-crafts"),
    "eyelet":    (eyelet,    32, 80, lambda: bg_linen(69, (168, 190, 212)), "eyes-crafts"),
    "darned":    (darned,    32, 80, lambda: bg_linen(70, (58, 78, 126)), "eyes-crafts"),
    "wheel":     (wheel,     40, 80, lambda: bg_linen(71), "eyes-crafts"),
    "folk":      (folk,      32, 80, lambda: BLACK_BG, "eyes-crafts"),
    "lace":      (lace,      32, 80, lambda: BLACK_BG, "eyes-crafts"),
    "mola":      (mola,      32, 80, lambda: BLACK_BG, "eyes-crafts"),
}
ALL.update(PIECES3)

if __name__ == "__main__": main(sys.argv[1:] or list(PIECES3))
