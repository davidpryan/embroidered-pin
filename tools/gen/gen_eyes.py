#!/usr/bin/env python3
"""Ten embroidered, animated eyes for the 240x240 round pin, built on the embroidered-pin generators.
Set one: the gallery's own look (satin, 2-ply yarn, French knots). Render with gen_eyes2.py, which exports both sets."""
import math, random, os, sys

GEN = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("EYES_OUT", "eyes")
sys.path.insert(0, GEN)
_mk = os.makedirs; os.makedirs = lambda *a, **k: None      # the generators create their own output dirs on import
from PIL import Image, ImageDraw, ImageChops
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, ellipse_mask, poly_mask, new_layer, satin, backstitch
from gen_stitch import resample
from gen_granny import yarn, MUSTARD, OXBLOOD, TEAL, CREAM, SOOT, PLUM, RUST, SAGE
from gen_linen import bg_linen, bg_satin, BLACK_BG, compose_bg
from gen_bold import bigknot, rot, BONE
os.makedirs = _mk
os.makedirs(OUT, exist_ok=True)

TAU = 2 * math.pi
INK = (14, 12, 12)
NAVY, SKY, WHITE = (36, 60, 128), (104, 166, 204), (246, 242, 232)

# ------------------------------------------------------------------ eye helpers
def almond(cx, cy, w, hu, hl, n=40, tilt=0.0, p=0.75):
    """Upper and lower lid curves, corner to corner."""
    c, s = math.cos(tilt), math.sin(tilt); up, lo = [], []
    for i in range(n + 1):
        t = i / n; x = -w + 2 * w * t; k = math.sin(math.pi * t) ** p
        up.append((cx + x * c + hu * k * s, cy + x * s - hu * k * c))
        lo.append((cx + x * c - hl * k * s, cy + x * s + hl * k * c))
    return up, lo

def blink(u, centers, dur=0.07):
    o = 1.0
    for c in centers:
        d = abs(((u - c + 0.5) % 1) - 0.5)
        if d < dur: o = min(o, (d / dur) ** 1.5)
    return o

def fixed_satin(L, mask, tex_mask, col, ang, **kw):
    """Satin whose thread texture stays put while the visible mask moves."""
    T = new_layer(); satin(T, tex_mask, col, ang, shadow=False, **kw)
    L.paste(T, (0, 0), ImageChops.multiply(mask, T.split()[3]))

def iris(E, x, y, r, col, pupil=0.42, seed=1, col2=None, slit=None, glint=True):
    """Long-and-short radial stitches, a backstitched limbal ring, pupil, French-knot glint."""
    rng = random.Random(seed); d = ImageDraw.Draw(E)
    d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=shade(col, 0.5) + (255,))
    n = max(24, int(r * 2.4))
    for i in range(n):
        a = TAU * i / n + rng.uniform(-0.04, 0.04)
        r0, r1 = r * rng.uniform(0.2, 0.5), r * rng.uniform(0.88, 1.0)
        d.line([P(x + r0 * math.cos(a), y + r0 * math.sin(a)), P(x + r1 * math.cos(a), y + r1 * math.sin(a))],
               fill=shade(col, 1 + rng.uniform(-0.2, 0.25)) + (255,), width=max(1, int(min(1.5, r * 0.07) * S)))
    if col2:
        for i in range(n // 2):
            a = TAU * i / (n // 2) + rng.uniform(-0.08, 0.08)
            r0, r1 = r * pupil * 0.8, r * rng.uniform(0.5, 0.72)
            d.line([P(x + r0 * math.cos(a), y + r0 * math.sin(a)), P(x + r1 * math.cos(a), y + r1 * math.sin(a))],
                   fill=shade(col2, 1 + rng.uniform(-0.15, 0.2)) + (255,), width=max(1, int(min(1.5, r * 0.07) * S)))
    backstitch(E, ellipse_pts(x, y, r - 0.6, r - 0.6, 48), shade(col, 0.42), width=max(1.0, r * 0.07), dash=4.0, gap=0.5)
    pr = r * pupil
    if slit is None: d.ellipse([P(x - pr, y - pr), P(x + pr, y + pr)], fill=INK + (255,))
    else: d.polygon([P(*q) for q in almond(x, y, r * 0.86, pr * slit, pr * slit, 24, math.pi / 2, 0.9)[0]
                     + almond(x, y, r * 0.86, pr * slit, pr * slit, 24, math.pi / 2, 0.9)[1][::-1]], fill=INK + (255,))
    if glint: knot(E, x - r * 0.33, y - r * 0.36, max(1.6, r * 0.14), BONE)

def eye(L, cx, cy, w, hu, hl, o=1.0, look=(0, 0), ir=None, icol=TEAL, icol2=None, scl=BONE, line=SOOT, lw=4.0,
        lashes=0, lash_len=14, lash_col=None, lash_w=2.2, lid=None, lid_ang=80, tilt=0.0, pupil=0.42, slit=None,
        seed=1, lower=True, inner=None):
    """One stitched eye. o = openness 0..1. inner(E) replaces the iris if given."""
    ir = ir or hu * 0.92
    fu, fl = almond(cx, cy, w, hu, hl, tilt=tilt); full = poly_mask(fu + fl[::-1])
    up, lo = almond(cx, cy, w, hu * o - hl * (1 - o), hl, tilt=tilt); opening = poly_mask(up + lo[::-1])
    E = new_layer()
    satin(E, full, scl, 8, spacing=1.5, sheen=0.16, shadow=False, var=0.06)
    if inner: inner(E)
    else: iris(E, cx + look[0], cy + look[1], ir, icol, pupil, seed, icol2, slit)
    L.paste(E, (0, 0), opening)
    if lid:
        fixed_satin(L, ImageChops.subtract(full, opening), full, lid, lid_ang, spacing=1.5, sheen=0.3)
        yarn(L, fu, line, lw * 0.55)
    if lower: yarn(L, lo, line, lw * 0.6)
    yarn(L, up, line, lw)
    lc = lash_col or line; c, s = math.cos(tilt), math.sin(tilt)
    for k in range(lashes):
        t = 0.14 + 0.72 * k / max(1, lashes - 1); b = up[int(t * (len(up) - 1))]
        a = (t - 0.5) * 1.5; ln = lash_len * (0.7 + 0.3 * math.sin(math.pi * t))
        dx, dy = math.sin(a), -math.cos(a) * (2 * o - 1 if o < 0.75 else 1) if o < 0.75 else -math.cos(a)
        dx, dy = dx * c - dy * s, dx * s + dy * c
        yarn(L, [b, (b[0] + dx * ln * 0.55, b[1] + dy * ln * 0.5), (b[0] + dx * ln, b[1] + dy * ln)], lc, lash_w)
    return up, lo

def teardrop(x, y, r, n=28):
    return [(x + r * math.sin(a) * math.sin(a / 2) ** 1.6, y - r * 1.5 * math.cos(a)) for a in (TAU * i / n for i in range(n))]

def petal(b, ang, ln, wd, n=14):
    """Lazy-daisy loop from base b."""
    dx, dy = math.cos(ang), math.sin(ang); out = []
    for i in range(n + 1):
        u = TAU * i / n; al = (1 - math.cos(u)) / 2 * ln; sd = math.sin(u) * wd * (0.35 + 0.65 * (1 - math.cos(u)) / 2)
        out.append((b[0] + dx * al - dy * sd, b[1] + dy * al + dx * sd))
    return out

# ------------------------------------------------------------------ the ten
def watcher(f, FR):
    L = new_layer(); random.seed(11); u = f / FR; ph = TAU * u
    o = blink(u, [0.5]); look = (27 * math.sin(ph), 3 * math.sin(2 * ph) + 2)
    yarn(L, [(40 + i * 8, 62 - 22 * math.sin(math.pi * i / 20) - 3 * (1 - o)) for i in range(21)], MUSTARD, 5.0)
    eye(L, 120, 128, 98, 50, 38, o, look, 40, TEAL, MUSTARD, BONE, BONE, 5.0, lashes=9, lash_len=17, lash_w=2.6, seed=2)
    return L

def nazar(f, FR):
    L = new_layer(); random.seed(12); u = f / FR; ph = TAU * u
    for k in range(18):
        a = TAU * k / 18; tw = 0.75 + 0.25 * math.sin(ph * 2 + k * TAU / 3)
        bigknot(L, 120 + 106 * math.cos(a), 120 + 106 * math.sin(a), 4.6 * tw, MUSTARD if k % 2 else OXBLOOD)
    satin(L, ellipse_mask(120, 120, 92, 92), NAVY, 360 * u, spacing=1.6, sheen=0.3)
    satin(L, ellipse_mask(120, 120, 66, 66), WHITE, -360 * u + 40, spacing=1.6, sheen=0.2, shadow=False)
    satin(L, ellipse_mask(120, 120, 45, 45), SKY, 360 * u + 90, spacing=1.5, sheen=0.3, shadow=False)
    pr = 22 + 5 * math.sin(ph * 2)
    satin(L, ellipse_mask(120, 120, pr, pr), SOOT, 30, spacing=1.4, sheen=0.15, shadow=False)
    for r, c, w_ in ((92, shade(NAVY, 0.6), 3.0), (66, shade(WHITE, 0.82), 2.2), (45, shade(SKY, 0.65), 2.2), (pr, INK, 2.0)):
        yarn(L, ellipse_pts(120, 120, r, r, 72), c, w_)
    knot(L, 120 - pr * 0.4, 120 - pr * 0.4, 4.2, BONE)
    return L

def cat(f, FR):
    L = new_layer(); random.seed(13); u = f / FR; ph = TAU * u
    sl = 0.16 + 0.42 * (0.5 - 0.5 * math.cos(ph)) ** 2
    o = blink(u, [0.0], 0.09); look = (10 * math.sin(ph), 0)
    eye(L, 120, 120, 104, 60, 52, o, look, 62, MUSTARD, SAGE, shade(BONE, 0.8), BONE, 5.0, tilt=-0.13, pupil=0.9,
        slit=sl, seed=5)
    for sx in (-1, 1):                                   # whisker-ish tick marks at the corners
        yarn(L, [(120 + sx * 100, 120 - sx * 13 - 2), (120 + sx * 113, 120 - sx * 15 - 8)], BONE, 3.0)
    return L

def sleepy(f, FR):
    L = new_layer(); random.seed(14); u = f / FR
    if u < 0.7: o = 0.78 - 0.7 * (u / 0.7) ** 1.6
    elif u < 0.78: o = 0.08 + 0.87 * ((u - 0.7) / 0.08)
    else: o = 0.95 - 0.17 * ((u - 0.78) / 0.22)
    eye(L, 120, 124, 100, 58, 36, o, (0, 8 + 10 * (1 - o)), 42, RUST, MUSTARD, WHITE, SOOT, 5.0, lashes=8, lash_len=18,
        lash_w=2.8, lid=PLUM, seed=7)
    for k in range(3):                                    # drifting z's as cross-stitched ticks
        v = (u + k / 3) % 1; x, y, s_ = 176 + 22 * v, 70 - 46 * v, 5 + 5 * v
        if o < 0.6 and v < 0.9:
            yarn(L, [(x - s_, y - s_), (x + s_, y - s_), (x - s_, y + s_), (x + s_, y + s_)], OXBLOOD, 2.2)
    return L

def button_eye(f, FR):
    L = new_layer(); random.seed(15); u = f / FR; ph = TAU * u
    up, lo = almond(120, 120, 102, 62, 54)
    T = new_layer(); satin(T, poly_mask(up + lo[::-1]), WHITE, 12, spacing=1.6, sheen=0.14, var=0.05); L.paste(T, (0, 0), T)
    backstitch(L, up + lo[::-1], SOOT, width=3.2, dash=9, gap=4, closed=True)
    for k in range(7):                                    # ragdoll lashes: straight stitches that twitch
        t = 0.16 + 0.68 * k / 6; b = up[int(t * 40)]; a = (t - 0.5) * 1.5 + 0.12 * math.sin(ph * 2 + k)
        yarn(L, [b, (b[0] + 20 * math.sin(a), b[1] - 20 * math.cos(a))], SOOT, 3.0)
    bx, by, r = 120 + 9 * math.sin(ph), 122 + 3 * math.sin(2 * ph), 40
    sw = 0.5 * math.sin(ph + 0.6)                         # dangling thread
    tail = [(bx + 6, by + 10), (bx + 14 + 14 * sw, by + 44), (bx + 4 + 30 * sw, by + 72), (bx + 16 + 44 * sw, by + 96)]
    at, tot = resample(tail); yarn(L, [at(tot * i / 14) for i in range(15)], OXBLOOD, 2.6)
    satin(L, ellipse_mask(bx, by, r, r), SOOT, 25, spacing=1.5, sheen=0.5, var=0.2)
    yarn(L, ellipse_pts(bx, by, r - 9, r - 9, 48), (70, 64, 68), 2.2)
    yarn(L, ellipse_pts(bx, by, r, r, 60), INK, 2.6)
    hs = 12; holes = rot([(bx - hs, by - hs), (bx + hs, by - hs), (bx + hs, by + hs), (bx - hs, by + hs)], bx, by, TAU / 4 * u)
    d = ImageDraw.Draw(L)
    for hx, hy in holes: d.ellipse([P(hx - 4.6, hy - 4.6), P(hx + 4.6, hy + 4.6)], fill=WHITE + (255,))
    yarn(L, [holes[0], holes[2]], OXBLOOD, 4.2); yarn(L, [holes[1], holes[3]], OXBLOOD, 4.2)
    return L

def all_seeing(f, FR):
    L = new_layer(); random.seed(16); u = f / FR; ph = TAU * u
    tri = [(120, 30), (36, 180), (204, 180)]; c = (120, 132)
    for k in range(24):                                   # marching running-stitch rays
        a = TAU * k / 24 + TAU / 48; dx, dy = math.cos(a), math.sin(a); per = 20
        pos = 30 + ((u * 2 + (k % 2) * 0.5) % 1) * per - per
        while pos < 118:
            a0, a1 = max(30, pos), min(118, pos + 11)
            p0 = (c[0] + dx * a0, c[1] + dy * a0); p1 = (c[0] + dx * a1, c[1] + dy * a1)
            if a1 - a0 > 2 and math.hypot(p1[0] - 120, p1[1] - 120) < 116:
                yarn(L, [p0, p1], BONE if k % 2 else MUSTARD, 2.4)
            pos += per
    ImageDraw.Draw(L).polygon([P(*q) for q in tri], fill=(12, 10, 10, 255))
    at, tot = resample(tri + [tri[0]]); pos = 0
    while pos < tot: yarn(L, [at(pos), at(min(tot, pos + 12))], MUSTARD, 6.5); pos += 11
    for q in tri: bigknot(L, q[0], q[1], 7, OXBLOOD)
    o = blink(u, [0.25, 0.75], 0.08)
    eye(L, 120, 136, 46, 25, 20, o, (8 * math.sin(ph), 0), 19, TEAL, None, BONE, MUSTARD, 3.6, seed=3)
    return L

def lash_sun(f, FR):
    L = new_layer(); random.seed(17); u = f / FR; ph = TAU * u
    n = 22
    for k in range(n):
        a = TAU * k / n; b = (120 + 76 * math.cos(a), 122 + 50 * math.sin(a))
        ln = 26 + 9 * math.sin(ph * 2 - k * TAU * 3 / n); col = (PLUM, MUSTARD)[k % 2]
        pt = petal(b, a, ln, 7.5); yarn(L, pt, col, 2.6)
        tip = (b[0] + math.cos(a) * ln, b[1] + math.sin(a) * ln)
        yarn(L, [tip, (tip[0] + math.cos(a) * 4, tip[1] + math.sin(a) * 4)], shade(col, 0.7), 2.0)
    o = blink(u, [0.40, 0.56], 0.065)
    eye(L, 120, 122, 66, 37, 31, o, (0, 2), 28, SAGE, MUSTARD, WHITE, SOOT, 4.4, lid=RUST, seed=9)
    return L

def hypno(f, FR):
    L = new_layer(); random.seed(18); u = f / FR; ph = TAU * u
    def inner(E):
        ImageDraw.Draw(E).rectangle([0, 0, N, N], fill=SOOT + (255,))
        for col, off in ((BONE, 0.0), (OXBLOOD, math.pi)):
            b = 26 / TAU; th = 0.0; pts = []
            while 6 + b * th < 124:
                rr = 6 + b * th; pts.append((120 + rr * math.cos(th + off - ph), 120 + rr * math.sin(th + off - ph))); th += 0.16
            yarn(E, pts, col, 5.6)
        bigknot(E, 120, 120, 13 + 3 * math.sin(ph * 2), TEAL)
    eye(L, 120, 120, 110, 74, 74, 1.0, lw=5.5, line=BONE, inner=inner, lashes=11, lash_len=15, lash_w=2.6)
    return L

def weeping(f, FR):
    L = new_layer(); random.seed(19); u = f / FR; ph = TAU * u
    o = 0.36 + 0.1 * math.sin(ph)
    yarn(L, [(46 + i * 7.4, 58 + 0.05 * (i - 4) ** 2 - 6 * math.sin(math.pi * i / 20)) for i in range(21)], SOOT, 4.6)
    for k, (tx, ty, sp) in enumerate(((84, 124, 0.0), (120, 132, 0.37), (158, 123, 0.7))):
        backstitch(L, [(tx, ty + 4), (tx - 2, ty + 50), (tx + 1, ty + 104)], SKY, width=1.6, dash=4, gap=4)
        for j in range(2):
            v = (u + sp + j / 2) % 1; r = 7.5 * min(1, v / 0.18) * min(1, (1 - v) / 0.15)
            y = ty + 10 + 84 * v ** 1.5; x = tx - 2 * math.sin(v * 3)
            if r > 1.2:
                satin(L, poly_mask(teardrop(x, y, r)), TEAL, 75, spacing=1.3, sheen=0.3)
                yarn(L, teardrop(x, y, r) + [teardrop(x, y, r)[0]], shade(TEAL, 0.6), 1.5)
                knot(L, x - r * 0.25, y + r * 0.2, max(1.2, r * 0.26), WHITE)
    eye(L, 120, 100, 92, 46, 32, o, (0, 13), 36, TEAL, SKY, WHITE, SOOT, 5.0, lashes=8, lash_len=15, lash_w=2.6,
        lid=OXBLOOD, seed=4)
    return L

def many(f, FR):
    L = new_layer(); random.seed(20); u = f / FR; ph = TAU * u
    cols = [(MUSTARD, RUST), (TEAL, SKY), (OXBLOOD, RUST), (SAGE, MUSTARD), (PLUM, SKY), (RUST, MUSTARD), (SKY, WHITE)]
    spots = [(120, 120, 0.0)] + [(120 + 72 * math.cos(TAU * k / 6 + 0.5), 120 + 70 * math.sin(TAU * k / 6 + 0.5), 0.0) for k in range(6)]
    for k, (x, y, _) in enumerate(spots):
        o = blink(u, [(k * 0.31 + 0.1) % 1, (k * 0.31 + 0.1 + (0.5 if k % 2 else 0.2)) % 1], 0.07)
        look = (7 * math.cos(ph + 0.3 * k), 3 * math.sin(ph + 0.3 * k))
        sc = 1.25 if k == 0 else 1.0
        eye(L, x, y, 31 * sc, 17 * sc, 14 * sc, o, look, 14 * sc, cols[k][0], cols[k][1], BONE, BONE, 2.8, tilt=(0 if k == 0 else 0.25 * math.sin(k * 2.1)),
            lashes=5 if k % 2 == 0 else 0, lash_len=8, lash_w=1.6, seed=k + 20)
    return L

PIECES = {
    "watcher":    (watcher,    32, 80, lambda: BLACK_BG),
    "nazar":      (nazar,      40, 80, lambda: bg_linen(41)),
    "cat":        (cat,        36, 80, lambda: BLACK_BG),
    "sleepy":     (sleepy,     48, 90, lambda: bg_satin(42)),
    "button_eye": (button_eye, 32, 80, lambda: bg_satin(43, (240, 232, 214), 60)),
    "all_seeing": (all_seeing, 32, 80, lambda: BLACK_BG),
    "lash_sun":   (lash_sun,   32, 80, lambda: bg_linen(44)),
    "hypno":      (hypno,      32, 70, lambda: BLACK_BG),
    "weeping":    (weeping,    36, 80, lambda: bg_linen(45, (226, 222, 210))),
    "many":       (many,       40, 80, lambda: BLACK_BG),
}
