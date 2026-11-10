#!/usr/bin/env python3
"""'Midnight garden' embroidered insects for a 240x240 round display.
Black ground, crescent moon, laurel + daisy wreath (optional), thick satin thread.
Renders at 4x and downsamples."""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

S = 4
W = 240
N = W * S
OUT = "/home/claude/eye_pin_lowpower/insects2"
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ helpers
def P(x, y): return (x * S, y * S)

def ellipse_pts(cx, cy, rx, ry, n=72, rot=0.0, a0=0.0, a1=2 * math.pi):
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out

def poly_mask(pts):
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).polygon([P(*p) for p in pts], fill=255)
    return m

def ellipse_mask(cx, cy, rx, ry, rot=0.0): return poly_mask(ellipse_pts(cx, cy, rx, ry, 90, rot))
def rect_mask(x0, y0, x1, y1):
    m = Image.new("L", (N, N), 0); ImageDraw.Draw(m).rectangle([P(x0, y0), P(x1, y1)], fill=255); return m
def new_layer(): return Image.new("RGBA", (N, N), (0, 0, 0, 0))
def shade(c, v): return tuple(max(0, min(255, int(ch * v))) for ch in c)

def satin(layer, mask, color, angle_deg, spacing=1.45, jitter=0.3, sheen=0.28,
          alpha=255, shadow=True, var=0.1, blur=0.45):
    """Satin stitch: parallel thread lines through a mask, cropped for speed."""
    bb = mask.getbbox()
    if not bb: return
    m = 3 * S
    x0, y0 = max(0, bb[0] - m), max(0, bb[1] - m)
    x1, y1 = min(N, bb[2] + m), min(N, bb[3] + m)
    sub = mask.crop((x0, y0, x1, y1)); w, h = sub.size
    if shadow:
        layer.paste(Image.new("RGBA", (w, h), (0, 0, 0, 150)), (x0 + int(0.8 * S), y0 + int(1.1 * S)), sub)
    st = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    a = math.radians(angle_deg); dx, dy = math.cos(a), math.sin(a); nx, ny = -dy, dx
    cx, cy = w / 2, h / 2; R = math.hypot(w, h) / 2 + 2
    step = spacing * S; n = int(2 * R / step) + 1
    for i in range(n):
        t = -R + i * step + random.uniform(-jitter, jitter) * S
        px, py = cx + nx * t, cy + ny * t
        v = 1 + random.uniform(-var, var) + sheen * math.cos(t / R * math.pi * 1.4 + 0.5)
        d.line([(px - dx * R, py - dy * R), (px + dx * R, py + dy * R)],
               fill=shade(color, v) + (alpha,), width=max(1, int(step * 0.92)))
    if blur:
        st = Image.blend(st, st.filter(ImageFilter.GaussianBlur(blur * S)), 0.3)
    layer.paste(st, (x0, y0), ImageChops.multiply(sub, st.split()[3]))

def fuzz(layer, mask, color, count, length=2.4, width=1.0, var=0.22, alpha=255):
    bb = mask.getbbox()
    if not bb: return
    x0, y0, x1, y1 = bb; w, h = x1 - x0, y1 - y0
    st = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    for _ in range(count):
        x = random.uniform(0, w); y = random.uniform(0, h); a = random.uniform(0, math.pi)
        d.line([(x - math.cos(a) * length * S / 2, y - math.sin(a) * length * S / 2),
                (x + math.cos(a) * length * S / 2, y + math.sin(a) * length * S / 2)],
               fill=shade(color, 1 + random.uniform(-var, var)) + (alpha,), width=int(width * S))
    layer.paste(st, (x0, y0), ImageChops.multiply(mask.crop(bb), st.split()[3]))

def backstitch(layer, pts, color, width=1.2, dash=2.6, gap=0.8, closed=False, alpha=255):
    d = ImageDraw.Draw(layer)
    pts = list(pts) + ([pts[0]] if closed else [])
    segs = [(a[0], a[1], b[0], b[1], math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts, pts[1:])]
    segs = [s for s in segs if s[4] > 0]
    if not segs: return
    total = sum(s[4] for s in segs)
    def at(dist):
        acc = 0
        for x0, y0, x1, y1, L in segs:
            if acc + L >= dist:
                f = (dist - acc) / L; return (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
            acc += L
        return segs[-1][2], segs[-1][3]
    pos, on = 0.0, True
    while pos < total:
        end = min(total, pos + (dash if on else gap))
        if on:
            d.line([P(*at(pos)), P(*at(end))], fill=shade(color, 1 + random.uniform(-0.1, 0.1)) + (alpha,), width=int(width * S))
        pos, on = end, not on

def knot(layer, x, y, r, color):
    d = ImageDraw.Draw(layer)
    d.ellipse([P(x - r, y - r + 0.6), P(x + r, y + r + 0.6)], fill=(0, 0, 0, 170))
    d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=shade(color, 0.7) + (255,))
    d.ellipse([P(x - r * 0.8, y - r * 0.8), P(x + r * 0.8, y + r * 0.8)], fill=color + (255,))
    d.ellipse([P(x - r * 0.5, y - r * 0.6), P(x + r * 0.15, y - r * 0.05)], fill=shade(color, 1.3) + (255,))
    d.ellipse([P(x - r * 0.35, y - r * 0.45), P(x - r * 0.1, y - r * 0.2)], fill=(255, 250, 240, 230))

def sm(pts, it=2):
    """Chaikin corner-cutting for organic closed outlines."""
    for _ in range(it):
        out = []
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        pts = out
    return pts

def mirror(pts, cx=120): return [(2 * cx - x, y) for x, y in pts]

# ------------------------------------------------------------------ decor
SAGE, SAGE_D, SAGE_L = (118, 142, 84), (84, 106, 60), (160, 178, 112)
CREAM, GOLD, GOLD_D = (246, 240, 222), (224, 182, 74), (176, 132, 44)

def leaf(L, bx, by, tx, ty, wid, color=SAGE):
    ax, ay = tx - bx, ty - by; ln = math.hypot(ax, ay) or 1
    nx, ny = -ay / ln, ax / ln
    left, right = [], []
    for i in range(13):
        s = i / 12; off = wid * math.sin(math.pi * s) ** 0.9
        px, py = bx + ax * s, by + ay * s
        left.append((px + nx * off, py + ny * off)); right.append((px - nx * off, py - ny * off))
    poly = left + right[::-1]
    ang = math.degrees(math.atan2(ay, ax)) + 50
    satin(L, poly_mask(poly), color, ang, spacing=1.3, sheen=0.3)
    backstitch(L, [(bx, by), (tx, ty)], shade(color, 0.6), width=0.7, dash=1.8, gap=0.8)

def vine_arc(L, cx, cy, r, a0, a1, n_leaves=9, flip=1, leaf_len=11, leaf_w=3.4):
    """Leaves along an arc from angle a0 to a1 (degrees, y-down), alternating sides."""
    pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / 40)),
            cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / 40))) for i in range(41)]
    backstitch(L, pts, SAGE_D, width=1.1, dash=3.0, gap=0.9)
    for i in range(n_leaves):
        t = (i + 0.5) / n_leaves
        a = math.radians(a0 + (a1 - a0) * t)
        bx, by = cx + r * math.cos(a), cy + r * math.sin(a)
        # tangent direction of growth, tilted outward/inward alternately
        tx_, ty_ = -math.sin(a) * flip, math.cos(a) * flip
        side = 1 if i % 2 == 0 else -1
        ox, oy = math.cos(a) * side, math.sin(a) * side
        dx = tx_ * 0.75 + ox * 0.65; dy = ty_ * 0.75 + oy * 0.65
        dn = math.hypot(dx, dy)
        col = [SAGE, SAGE_L, SAGE_D][i % 3]
        leaf(L, bx, by, bx + dx / dn * leaf_len, by + dy / dn * leaf_len, leaf_w, col)

def daisy(L, x, y, r=9, petals=11, rot=0.0):
    for i in range(petals):
        a = rot + 2 * math.pi * i / petals
        px, py = x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62
        satin(L, ellipse_mask(px, py, r * 0.42, r * 0.17, a), CREAM, math.degrees(a) + 90, spacing=1.2, sheen=0.2, var=0.06)
    for i in range(6):
        a = 2 * math.pi * i / 6
        knot(L, x + math.cos(a) * r * 0.16, y + math.sin(a) * r * 0.16, r * 0.12, GOLD)
    knot(L, x, y, r * 0.13, GOLD)

def bud(L, x, y, a, size=5):
    tx, ty = x + math.cos(a) * size, y + math.sin(a) * size
    satin(L, ellipse_mask(x, y, size * 0.7, size * 0.42, a), CREAM, math.degrees(a) + 90, spacing=1.2, sheen=0.2)
    backstitch(L, [(x - math.cos(a) * 6, y - math.sin(a) * 6), (x, y)], SAGE_D, width=0.9, dash=4, gap=0.1)

def moon(L, x, y, r=12):
    m = ellipse_mask(x, y, r, r)
    cut = ellipse_mask(x + r * 0.55, y - r * 0.2, r * 0.92, r * 0.92)
    m = ImageChops.subtract(m, cut)
    satin(L, m, GOLD, 35, spacing=1.3, sheen=0.35)
    pts = ellipse_pts(x, y, r, r, 60)
    backstitch(L, pts, GOLD_D, width=0.8, dash=2.0, gap=0.8, closed=True, alpha=200)

def star(L, x, y, s=3.0, col=GOLD):
    backstitch(L, [(x - s, y), (x + s, y)], col, width=0.8, dash=10, gap=0.1)
    backstitch(L, [(x, y - s), (x, y + s)], col, width=0.8, dash=10, gap=0.1)
    backstitch(L, [(x - s * 0.5, y - s * 0.5), (x + s * 0.5, y + s * 0.5)], shade(col, 1.15), width=0.6, dash=10, gap=0.1)
    backstitch(L, [(x - s * 0.5, y + s * 0.5), (x + s * 0.5, y - s * 0.5)], shade(col, 1.15), width=0.6, dash=10, gap=0.1)
    knot(L, x, y, 0.9, (255, 240, 200))

def wreath_layer(seed, florals=True):
    random.seed(seed)
    L = new_layer()
    cx, cy = 120, 120
    # sky
    moon(L, 120, 40, 15)
    for (sx, sy, ss) in [(96, 30, 2.6), (146, 28, 2.2), (82, 52, 1.8), (160, 50, 2.6), (120, 62, 1.6)]:
        star(L, sx, sy, ss)
    for (sx, sy) in [(70, 40), (172, 38), (104, 48), (140, 56), (60, 70), (184, 66)]:
        knot(L, sx, sy, 0.9, (255, 236, 190))
    if not florals:
        # plain variant: just a sparse ring of tiny stars at the rim so it isn't bare
        for i in range(10):
            a = math.radians(100 + i * 160 / 9)
            for sgn in (1, -1):
                knot(L, 120 + sgn * 102 * math.cos(a) * -1, 120 + 102 * math.sin(a), 0.8, (255, 236, 190))
        return L
    r = 97
    # two arcs climbing from bottom to the moon on each side
    vine_arc(L, cx, cy, r, 112, 230, n_leaves=16, flip=-1, leaf_len=13, leaf_w=4.3)     # left (y-down angles)
    vine_arc(L, cx, cy, r, 68, -50, n_leaves=16, flip=1, leaf_len=13, leaf_w=4.3)       # right
    # second inner sprig on each side for density
    vine_arc(L, cx, cy, r - 12, 130, 212, n_leaves=9, flip=-1, leaf_len=10, leaf_w=3.2)
    vine_arc(L, cx, cy, r - 12, 50, -32, n_leaves=9, flip=1, leaf_len=10, leaf_w=3.2)
    # daisies
    for a_deg in (128, 172, 215):
        a = math.radians(a_deg)
        daisy(L, cx + r * math.cos(a), cy + r * math.sin(a), 9.5, rot=random.uniform(0, 1))
        daisy(L, cx - r * math.cos(a), cy + r * math.sin(a), 9.5, rot=random.uniform(0, 1))
    daisy(L, 120, 120 + r + 1, 11, petals=12)
    # buds near vine tips and between daisies
    for (a_deg, rr) in ((236, r - 2), (150, r - 15), (196, r - 15)):
        a = math.radians(a_deg)
        bud(L, cx + rr * math.cos(a), cy + rr * math.sin(a), a - 0.6)
        bud(L, cx - rr * math.cos(a), cy + rr * math.sin(a), math.pi - a + 0.6)
    # bottom sprigs flanking the big daisy
    for sgn in (-1, 1):
        leaf(L, 120 + sgn * 14, 214, 120 + sgn * 26, 206, 3.2, SAGE_L)
        leaf(L, 120 + sgn * 10, 216, 120 + sgn * 20, 222, 2.6, SAGE_D)
    return L

# ------------------------------------------------------------------ insects
def luna_moth(flap=0.0, ant=0.0):
    L = new_layer(); cx, cy = 120, 118
    f = 1 - 0.26 * flap
    pale, pale_d, plum, cream = (186, 206, 150), (140, 165, 108), (120, 76, 88), (244, 240, 220)
    upper = [(3, -16), (14, -31), (36, -41), (60, -38), (68, -27), (62, -12), (48, 0), (28, 7), (10, 7)]
    lower = [(4, 2), (20, 7), (36, 14), (46, 28), (42, 44), (34, 54), (28, 62), (25, 74), (21, 86), (17, 74), (14, 58), (9, 42), (3, 24)]
    lead = [(3, -16), (14, -31), (36, -41), (60, -38), (68, -27), (62, -30), (38, -34), (16, -25), (5, -12)]
    def w(pts, side): return sm([(cx + side * x * f, cy + y) for x, y in pts])
    for side in (-1, 1):
        lw = w(lower, side)
        satin(L, poly_mask(lw), pale_d, 90 + side * 30, spacing=1.45)
        backstitch(L, lw, (90, 110, 70), closed=True, width=1.0)
        # tail ribbing
        for k in range(3):
            backstitch(L, [(cx + side * (14 + k * 6) * f, cy + 30 + k * 6), (cx + side * (24 + k * 2) * f, cy + 62 + k * 6)], pale, width=0.8, dash=2.0, gap=1.0)
        uw = w(upper, side)
        satin(L, poly_mask(uw), pale, 95 - side * 20, spacing=1.45)
        backstitch(L, uw, (110, 130, 85), closed=True, width=1.0)
        satin(L, poly_mask(w(lead, side)), plum, 20 * side, spacing=1.3, shadow=False)
        # veins
        for vx, vy in [(60, -34), (66, -20), (56, -4)]:
            backstitch(L, [(cx + side * 10 * f, cy - 8), (cx + side * vx * f, cy + vy)], (130, 150, 100), width=0.8, dash=2.2, gap=1.1)
        # eyespots: upper + lower, crescent style
        for (ex, ey, er) in [(40, -20, 6.5), (22, 30, 5.5)]:
            X, Y = cx + side * ex * f, cy + ey
            satin(L, ellipse_mask(X, Y, er * f, er), (150, 110, 100), 45, spacing=1.1, shadow=False)
            satin(L, ellipse_mask(X, Y, er * 0.6 * f, er * 0.6), cream, 0, spacing=1.0, shadow=False)
            c = ImageChops.subtract(ellipse_mask(X, Y, er * 0.6 * f, er * 0.6), ellipse_mask(X + side * 1.5 * f, Y - 1, er * 0.6 * f, er * 0.6))
            satin(L, c, plum, 0, spacing=1.0, shadow=False)
    body = ellipse_mask(cx, cy + 10, 6.5, 24)
    satin(L, body, (236, 236, 224), 0, spacing=1.2)
    fuzz(L, body, (250, 250, 240), 160, 2.2, 0.8)
    satin(L, ellipse_mask(cx, cy - 18, 6, 6), (230, 228, 210), 0, spacing=1.1)
    knot(L, cx - 3, cy - 19, 1.6, (40, 30, 30)); knot(L, cx + 3, cy - 19, 1.6, (40, 30, 30))
    for side in (-1, 1):
        tip = (cx + side * (18 + 3 * ant * side), cy - 46 + 2 * ant * side)
        base = (cx + side * 2, cy - 23)
        backstitch(L, [base, (cx + side * 9, cy - 36), tip], (130, 120, 70), width=0.9, dash=2.0, gap=0.8)
        for k in range(8):
            t = (k + 1) / 9
            bx, by = base[0] + (tip[0] - base[0]) * t, base[1] + (tip[1] - base[1]) * t
            ln = 5 * (1 - t * 0.6)
            backstitch(L, [(bx - side * ln, by - 2), (bx + side * ln * 0.6, by - 1)], (150, 140, 85), width=0.6, dash=12, gap=0.1)
    return L

def bumblebee(wing=0.0, ant=0.0):
    L = new_layer(); cx = 120
    brown, gold, blk, parch = (92, 62, 36), (222, 172, 58), (40, 32, 28), (238, 226, 196)
    for side in (-1, 1):
        for hy, k in [(108, -1), (124, 0), (142, 1)]:
            pts = [(cx + side * 14, hy), (cx + side * 30, hy + 7 * k + 1), (cx + side * 40, hy + 12 * k + 12)]
            backstitch(L, pts, blk, width=1.4, dash=2.4, gap=0.7)
    for side in (-1, 1):
        rot = math.radians(side * (-40 + 24 * wing))
        wx, wy = cx + side * 36, 100 - 10 * wing
        wm = ellipse_mask(wx, wy, 38, 14, rot)
        satin(L, wm, parch, 6 * side, spacing=2.4, alpha=150, shadow=False, sheen=0.1, var=0.05)
        pts = ellipse_pts(wx, wy, 38, 14, 70, rot)
        backstitch(L, pts, (190, 170, 120), width=0.9, closed=True, dash=2.2, gap=1.0)
        for t in (0.22, 0.4, 0.58):
            x1, y1 = pts[int(len(pts) * t * 0.5)]
            backstitch(L, [(cx + side * 8, 102 - 10 * wing), (x1, y1)], (190, 170, 120), width=0.7, dash=2.0, gap=1.1)
        # small hind wing
        hm = ellipse_mask(cx + side * 24, 118 - 6 * wing, 20, 8, math.radians(side * (-28 + 18 * wing)))
        satin(L, hm, parch, 6 * side, spacing=2.4, alpha=130, shadow=False, sheen=0.1, var=0.05)
        backstitch(L, ellipse_pts(cx + side * 24, 118 - 6 * wing, 20, 8, 50, math.radians(side * (-28 + 18 * wing))), (190, 170, 120), width=0.8, closed=True, dash=2.2, gap=1.0)
    ab = ellipse_mask(cx, 150, 25, 34)
    bands = [(116, 128, gold), (128, 142, brown), (142, 156, gold), (156, 170, brown), (170, 186, parch)]
    for y0, y1, col in bands:
        m = ImageChops.multiply(ab, rect_mask(0, y0, 240, y1))
        satin(L, m, col, 0, spacing=1.5, sheen=0.3)
        fuzz(L, m, shade(col, 1.15), 160, 2.4, 0.9, alpha=200)
    backstitch(L, ellipse_pts(cx, 150, 25, 34), (50, 35, 25), closed=True, width=1.0)
    th = ellipse_mask(cx, 104, 20, 19)
    satin(L, th, brown, 0, spacing=1.4)
    fuzz(L, th, (120, 85, 50), 300, 2.6, 1.0)
    fuzz(L, ImageChops.multiply(th, rect_mask(0, 84, 240, 98)), gold, 220, 2.4, 0.9)
    backstitch(L, ellipse_pts(cx, 104, 20, 19), (60, 40, 25), closed=True, dash=1.8, gap=1.0)
    hm = ellipse_mask(cx, 78, 12, 11)
    satin(L, hm, blk, 90, spacing=1.3)
    fuzz(L, hm, (70, 58, 50), 90, 2.0, 0.8)
    knot(L, cx - 6, 76, 2.8, (90, 75, 65)); knot(L, cx + 6, 76, 2.8, (90, 75, 65))
    for side in (-1, 1):
        a = [(cx + side * 4, 69), (cx + side * (11 + 2 * ant * side), 59), (cx + side * (20 + 3 * ant * side), 54 + 2 * ant * side)]
        backstitch(L, a, blk, width=1.0, dash=2.0, gap=0.7)
    return L

def ladybird(leg=0.0, ant=0.0):
    L = new_layer(); cx = 120
    red, red_d, blk, cream = (200, 44, 40), (140, 24, 24), (30, 26, 26), (242, 236, 220)
    for side in (-1, 1):
        for i, (hy, k) in enumerate([(106, -1), (128, 0), (150, 1)]):
            ph = leg * (1 if i == 1 else -0.6)
            pts = [(cx + side * 26, hy), (cx + side * (42 + 2 * ph), hy - 7 * k - 5 + 2 * ph), (cx + side * (50 + 3 * ph), hy + 8 * k + 5)]
            backstitch(L, pts, blk, width=1.5, dash=2.4, gap=0.6)
            knot(L, pts[-1][0], pts[-1][1], 1.2, blk)
    for side in (-1, 1):
        half = ellipse_pts(cx, 134, 36, 42, 40, 0, -math.pi / 2, math.pi / 2)
        if side == -1: half = mirror(half)
        half = half + [(cx, 176), (cx, 92)]
        satin(L, poly_mask(half), red, 90 + side * 24, spacing=1.5, sheen=0.34)
        backstitch(L, half, red_d, closed=True, width=1.1)
        for (sx, sy, sr) in [(14, 110, 6), (26, 132, 6.5), (11, 150, 6), (27, 160, 4.5)]:
            satin(L, ellipse_mask(cx + side * sx, sy, sr, sr), blk, 45, spacing=1.1, shadow=False)
            backstitch(L, ellipse_pts(cx + side * sx, sy, sr, sr), (12, 10, 10), closed=True, dash=1.6, gap=0.8)
    backstitch(L, [(cx, 92), (cx, 176)], (70, 10, 10), width=1.1)
    pm = ellipse_mask(cx, 92, 28, 12)
    satin(L, pm, blk, 0, spacing=1.3, sheen=0.3)
    backstitch(L, ellipse_pts(cx, 92, 28, 12), (12, 10, 10), closed=True)
    satin(L, ellipse_mask(cx - 17, 90, 6, 4.5), cream, 20, spacing=1.0, shadow=False)
    satin(L, ellipse_mask(cx + 17, 90, 6, 4.5), cream, -20, spacing=1.0, shadow=False)
    hm = ellipse_mask(cx, 74, 12, 9)
    satin(L, hm, blk, 90, spacing=1.2)
    knot(L, cx - 5, 73, 2.0, cream); knot(L, cx + 5, 73, 2.0, cream)
    for side in (-1, 1):
        a = [(cx + side * 5, 67), (cx + side * (12 + 2 * ant * side), 59), (cx + side * (17 + 3 * ant * side), 54 + 2 * ant * side)]
        backstitch(L, a, blk, width=1.0, dash=2.0, gap=0.7)
        knot(L, a[-1][0], a[-1][1], 1.6, blk)
    return L

def tiger_moth(flap=0.0, ant=0.0):
    L = new_layer(); cx, cy = 120, 122
    f = 1 - 0.26 * flap
    ochre, ochre_d, rust, cream, choc = (206, 152, 72), (160, 110, 50), (182, 104, 62), (244, 228, 192), (88, 58, 36)
    upper = [(3, -14), (18, -30), (44, -38), (66, -34), (70, -22), (62, -8), (46, 6), (24, 12), (6, 8)]
    lower = [(4, 4), (24, 10), (42, 22), (44, 40), (34, 52), (18, 54), (6, 44), (3, 22)]
    def w(pts, side): return sm([(cx + side * x * f, cy + y) for x, y in pts])
    for side in (-1, 1):
        lw = w(lower, side)
        satin(L, poly_mask(lw), rust, 90 + side * 30, spacing=1.45)
        backstitch(L, lw, (120, 60, 40), closed=True, width=1.0)
        for (sx, sy) in [(20, 30), (32, 42)]:
            knot(L, cx + side * sx * f, cy + sy, 2.6, choc)
        uw = w(upper, side)
        satin(L, poly_mask(uw), ochre, 95 - side * 22, spacing=1.45)
        backstitch(L, uw, choc, closed=True, width=1.0)
        # cream chevrons across upper wing
        for k, (x0, y0, x1, y1) in enumerate([(14, -22, 40, -6), (24, -32, 56, -14), (40, -37, 64, -26)]):
            pts = [(cx + side * x0 * f, cy + y0), (cx + side * (x0 + x1) / 2 * f, cy + (y0 + y1) / 2 - 4), (cx + side * x1 * f, cy + y1)]
            backstitch(L, pts, cream, width=1.5, dash=2.6, gap=0.9)
            backstitch(L, [(p[0], p[1] + 3) for p in pts], ochre_d, width=0.8, dash=2.0, gap=1.0)
        X, Y = cx + side * 50 * f, cy - 18
        satin(L, ellipse_mask(X, Y, 5 * f, 5), choc, 0, spacing=1.0, shadow=False)
        knot(L, X - side * 1 * f, Y - 1, 1.6, cream)
    body = ellipse_mask(cx, cy + 10, 7, 26)
    for i, y0 in enumerate(range(-16, 36, 7)):
        m = ImageChops.multiply(body, rect_mask(0, cy + y0, 240, cy + y0 + 7))
        satin(L, m, choc if i % 2 else ochre_d, 0, spacing=1.2)
    fuzz(L, body, (170, 120, 70), 120, 2.0, 0.8, alpha=160)
    satin(L, ellipse_mask(cx, cy - 20, 6, 6), choc, 0, spacing=1.1)
    knot(L, cx - 3, cy - 21, 1.6, (20, 15, 15)); knot(L, cx + 3, cy - 21, 1.6, (20, 15, 15))
    for side in (-1, 1):
        tip = (cx + side * (17 + 3 * ant * side), cy - 48 + 2 * ant * side); base = (cx + side * 2, cy - 25)
        backstitch(L, [base, (cx + side * 8, cy - 37), tip], choc, width=0.9, dash=2.0, gap=0.8)
        for k in range(7):
            t = (k + 1) / 8; bx, by = base[0] + (tip[0] - base[0]) * t, base[1] + (tip[1] - base[1]) * t
            backstitch(L, [(bx - side * 4 * (1 - t * 0.5), by - 2), (bx, by)], (120, 85, 50), width=0.6, dash=12, gap=0.1)
    return L

def dragonfly(tilt=0.0):
    L = new_layer(); cx = 120
    teal, sage, gauze, vein = (56, 150, 140), (122, 150, 96), (226, 232, 214), (160, 176, 140)
    for side in (-1, 1):
        for (ang, wl, ww, oy) in [(-12, 64, 13, 0), (14, 60, 12, 12)]:
            rot = math.radians(side * (ang + 6 * tilt))
            wx = cx + side * (wl * 0.54) * math.cos(rot); wy = 98 + oy + (wl * 0.54) * math.sin(rot) * side
            wm = ellipse_mask(wx, wy, wl * 0.5, ww * 0.5, rot)
            satin(L, wm, gauze, 90, spacing=2.6, alpha=120, shadow=False, sheen=0.0, var=0.04)
            pts = ellipse_pts(wx, wy, wl * 0.5, ww * 0.5, 80, rot)
            backstitch(L, pts, vein, width=0.9, closed=True, dash=2.2, gap=1.0)
            for t in range(1, 8):
                fr = t / 8
                p0 = pts[int(len(pts) * (0.5 + fr * 0.5)) % len(pts)]; p1 = pts[int(len(pts) * (0.5 - fr * 0.5)) % len(pts)]
                backstitch(L, [p0, p1], vein, width=0.6, dash=1.6, gap=1.1)
            backstitch(L, [(cx + side * 6, 98 + oy), pts[0]], vein, width=0.9, dash=2.0, gap=0.9)
    for i in range(10):
        y = 120 + i * 10; r = 6 - i * 0.38
        col = teal if i % 2 == 0 else sage
        satin(L, ellipse_mask(cx, y, r, 5.6), col, 0, spacing=1.1, sheen=0.32)
        backstitch(L, ellipse_pts(cx, y, r, 5.6), (30, 60, 60), closed=True, dash=1.6, gap=0.9)
    tm = ellipse_mask(cx, 100, 10, 15)
    satin(L, tm, (40, 120, 115), 0, spacing=1.2, sheen=0.3)
    backstitch(L, ellipse_pts(cx, 100, 10, 15), (30, 60, 60), closed=True)
    satin(L, ellipse_mask(cx, 80, 10, 9), (40, 100, 110), 90, spacing=1.1)
    knot(L, cx - 5.5, 79, 3.6, (90, 190, 170)); knot(L, cx + 5.5, 79, 3.6, (90, 190, 170))
    for side in (-1, 1):
        for hy in (94, 102, 110):
            backstitch(L, [(cx + side * 9, hy), (cx + side * 18, hy - 4), (cx + side * 22, hy + 2)], (30, 45, 50), width=0.9, dash=1.8, gap=0.7)
    return L

# ------------------------------------------------------------------ compose
def velvet():
    rng = np.random.default_rng(5)
    base = np.array([16, 14, 14], dtype=float)
    rows = rng.normal(0, 2.2, (N, 1, 1)); cols = rng.normal(0, 2.2, (1, N, 1))
    img = base + rows + cols + rng.normal(0, 1.5, (N, N, 1))
    yy, xx = np.mgrid[0:N, 0:N]
    r = np.hypot(xx - N / 2, yy - N / 2) / (N / 2)
    img = img + (10 * (1 - np.clip(r, 0, 1)) ** 1.5)[..., None]  # faint centre glow
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")

FABRIC = velvet()
CIRCLE = Image.new("L", (W, W), 0); ImageDraw.Draw(CIRCLE).ellipse([0, 0, W - 1, W - 1], fill=255)

def transform(layer, rot_deg=0.0, scale=1.0, dy=0):
    lay = layer
    if scale != 1.0:
        n2 = int(N * scale); lay = layer.resize((n2, n2), Image.LANCZOS)
        pad = new_layer(); pad.paste(lay, ((N - n2) // 2, (N - n2) // 2 + int(dy * S))); lay = pad
    elif dy:
        pad = new_layer(); pad.paste(lay, (0, int(dy * S))); lay = pad
    if rot_deg:
        lay = lay.rotate(rot_deg, resample=Image.BICUBIC, center=(N / 2, N / 2))
    return lay

def compose(decor, insect):
    out = FABRIC.copy()
    out.paste(decor, (0, 0), decor)
    out.paste(insect, (0, 0), insect)
    out = out.resize((W, W), Image.LANCZOS)
    return Image.composite(out, Image.new("RGB", (W, W), (0, 0, 0)), CIRCLE)

INSECTS = {
    "luna_moth":  (lambda t: luna_moth(flap=0.5 - 0.5 * math.cos(t * 2 * math.pi), ant=math.sin(t * 2 * math.pi)), 0.92, 1.22),
    "bumblebee":  (lambda t: bumblebee(wing=0.5 - 0.5 * math.cos(t * 2 * math.pi), ant=math.sin(t * 2 * math.pi)), 0.96, 1.25),
    "ladybird":   (lambda t: ladybird(leg=math.sin(t * 2 * math.pi), ant=math.sin(t * 2 * math.pi + 2)), 0.92, 1.2),
    "tiger_moth": (lambda t: tiger_moth(flap=0.5 - 0.5 * math.cos(t * 2 * math.pi), ant=math.sin(t * 2 * math.pi)), 0.92, 1.22),
    "dragonfly":  (lambda t: dragonfly(tilt=math.sin(t * 2 * math.pi)), 0.9, 1.15),
}

if __name__ == "__main__":
    FR = 8
    decor = {"floral": wreath_layer(11, True), "plain": wreath_layer(12, False)}
    stills = {"floral": [], "plain": []}
    seq = {"floral": [], "plain": []}
    for name, (fn, sc_f, sc_p) in INSECTS.items():
        seed = hash(name) & 0xffff
        for variant, sc in (("floral", sc_f), ("plain", sc_p)):
            random.seed(seed)
            base_rot = random.uniform(-5, 5)
            dy = 8 if variant == "floral" else 0       # sit a touch low under the moon
            still = compose(decor[variant], transform(fn(0.0), base_rot, sc, dy))
            still.save(f"{OUT}/{name}_{variant}.png")
            stills[variant].append(still)
            cyc = []
            for i in range(FR):
                random.seed(seed + i + 1)
                t = i / FR
                fr = compose(decor[variant], transform(fn(t), base_rot + 4 * math.sin(t * 2 * math.pi), sc, dy))
                fr.save(f"{OUT}/{name}_{variant}_{i:02d}.png")
                cyc.append(fr)
            seq[variant].append((still, cyc))
    for variant in ("floral", "plain"):
        frames = []
        items = seq[variant]
        for idx, (still, cyc) in enumerate(items):
            frames += [still] * 10 + cyc + [still] * 6
            nxt = items[(idx + 1) % len(items)][0]
            frames += [Image.blend(still, nxt, j / 6) for j in range(1, 6)]
        frames[0].save(f"{OUT}/preview_{variant}.gif", save_all=True, append_images=frames[1:], duration=110, loop=0)
        sheet = Image.new("RGB", (W * 5 + 60, W + 20), (40, 40, 40))
        for i, im in enumerate(stills[variant]):
            sheet.paste(im, (10 + i * (W + 10), 10))
        sheet.save(f"{OUT}/sheet_{variant}.png")
    print("done")
