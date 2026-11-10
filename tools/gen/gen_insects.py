#!/usr/bin/env python3
"""Render embroidered-looking insects at 240x240 for a GC9A01 round display.
Supersamples at 4x then downsamples for thread-like antialiasing."""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

S = 4                 # supersample
W = 240
N = W * S
OUT = "/home/claude/eye_pin_lowpower/insects"
os.makedirs(OUT, exist_ok=True)
random.seed(7)

# ----------------------------------------------------------------- utilities
def P(x, y):
    return (x * S, y * S)

def ellipse_pts(cx, cy, rx, ry, n=72, rot=0.0, a0=0.0, a1=2 * math.pi):
    pts = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return pts

def mask_of(draw_fn):
    m = Image.new("L", (N, N), 0)
    draw_fn(ImageDraw.Draw(m))
    return m

def poly_mask(pts):
    return mask_of(lambda d: d.polygon([P(*p) for p in pts], fill=255))

def ellipse_mask(cx, cy, rx, ry, rot=0.0):
    return poly_mask(ellipse_pts(cx, cy, rx, ry, 90, rot))

def satin(layer, mask, color, angle_deg, spacing=1.25, jitter=0.3, sheen=0.22,
          alpha=255, shadow=True, var=0.09):
    """Fill mask with parallel thread lines at angle_deg (satin stitch)."""
    bbox = mask.getbbox()
    if not bbox:
        return
    if shadow:
        sh = Image.new("RGBA", (N, N), (50, 30, 15, 90))
        layer.paste(sh, (int(0.6 * S), int(0.9 * S)), mask)
    st = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    R = math.hypot(bbox[2] - bbox[0], bbox[3] - bbox[1]) / 2 + 2 * S
    step = spacing * S
    n = int(2 * R / step) + 1
    for i in range(n):
        t = -R + i * step + random.uniform(-jitter, jitter) * S
        px, py = cx + nx * t, cy + ny * t
        v = 1 + random.uniform(-var, var) + sheen * math.cos(t / R * math.pi * 1.3 + 0.6)
        col = tuple(max(0, min(255, int(c * v))) for c in color)
        d.line([(px - dx * R, py - dy * R), (px + dx * R, py + dy * R)],
               fill=col + (alpha,), width=max(1, int(step * 0.9)))
    # per-thread highlight ridge
    hl = st.filter(ImageFilter.GaussianBlur(0.4 * S))
    st = Image.blend(st, hl, 0.25)
    layer.paste(st, (0, 0), ImageChops.multiply(mask, st.split()[3]))

def backstitch(layer, pts, color, width=1.1, dash=2.6, gap=0.7, closed=False, alpha=255):
    """Dashed line along a polyline: reads as back stitch / stem stitch."""
    d = ImageDraw.Draw(layer)
    if closed:
        pts = list(pts) + [pts[0]]
    # resample path to equal steps
    segs = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0:
            continue
        segs.append((x0, y0, x1, y1, L))
    total = sum(s[4] for s in segs)
    pos = 0.0
    on = True
    cur = 0.0
    def point_at(dist):
        acc = 0.0
        for x0, y0, x1, y1, L in segs:
            if acc + L >= dist:
                f = (dist - acc) / L
                return (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
            acc += L
        return segs[-1][2], segs[-1][3]
    while pos < total:
        seg_len = dash if on else gap
        end = min(total, pos + seg_len)
        if on:
            p0, p1 = point_at(pos), point_at(end)
            v = 1 + random.uniform(-0.1, 0.1)
            col = tuple(max(0, min(255, int(c * v))) for c in color)
            d.line([P(*p0), P(*p1)], fill=col + (alpha,), width=int(width * S))
        pos = end
        on = not on

def knot(layer, x, y, r, color):
    """French knot: dark base, lit top, tiny highlight."""
    d = ImageDraw.Draw(layer)
    dark = tuple(int(c * 0.55) for c in color)
    lite = tuple(min(255, int(c * 1.25)) for c in color)
    d.ellipse([P(x - r, y - r + 0.5), P(x + r, y + r + 0.5)], fill=dark + (255,))
    d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=color + (255,))
    d.ellipse([P(x - r * 0.45, y - r * 0.55), P(x + r * 0.25, y + r * 0.05)], fill=lite + (255,))
    d.ellipse([P(x - r * 0.3, y - r * 0.4), P(x - r * 0.05, y - r * 0.15)], fill=(255, 250, 240, 255))

def fuzz(layer, mask, color, count, length=2.2, width=0.9):
    """Short random stitches inside a mask (thorax fur, moth body)."""
    st = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    bb = mask.getbbox()
    for _ in range(count):
        x = random.uniform(bb[0], bb[2]) / S
        y = random.uniform(bb[1], bb[3]) / S
        a = random.uniform(0, math.pi)
        v = 1 + random.uniform(-0.2, 0.2)
        col = tuple(max(0, min(255, int(c * v))) for c in color)
        d.line([P(x - math.cos(a) * length / 2, y - math.sin(a) * length / 2),
                P(x + math.cos(a) * length / 2, y + math.sin(a) * length / 2)],
               fill=col + (255,), width=int(width * S))
    layer.paste(st, (0, 0), ImageChops.multiply(mask, st.split()[3]))

def mirror_pts(pts, cx=120):
    return [(2 * cx - x, y) for x, y in pts]

def new_layer():
    return Image.new("RGBA", (N, N), (0, 0, 0, 0))

# ----------------------------------------------------------------- fabric
def linen():
    rng = np.random.default_rng(3)
    base = np.array([226, 213, 188], dtype=float)
    rows = rng.normal(0, 5, (N, 1, 1))
    cols = rng.normal(0, 5, (1, N, 1))
    weave = (np.indices((N, N)).sum(axis=0) // (S * 1) % 2) * 3.0
    img = base + rows + cols + weave[..., None] + rng.normal(0, 2.5, (N, N, 1))
    yy, xx = np.mgrid[0:N, 0:N]
    r = np.hypot(xx - N / 2, yy - N / 2) / (N / 2)
    vign = 1 - 0.18 * np.clip(r, 0, 1) ** 2.2
    img = np.clip(img * vign[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(img, "RGB")

# ----------------------------------------------------------------- insects
def moth(flap=0.0, ant=0.0):
    """flap 0..1 (wings fold toward body), ant -1..1 (antenna sway)"""
    L = new_layer()
    cx, cy = 120, 122
    f = 1 - 0.28 * flap
    def wing(pts, side):
        return [(cx + side * (x) * f, cy + y) for x, y in pts]
    upper = [(4, -12), (26, -30), (50, -36), (60, -26), (56, -6), (40, 10), (18, 14), (5, 8)]
    lower = [(5, 6), (24, 12), (40, 26), (34, 46), (16, 50), (6, 36), (3, 18)]
    ochre, rust, cream, navy = (200, 150, 70), (168, 104, 74), (240, 226, 196), (44, 52, 92)
    for side in (-1, 1):
        lw = wing(lower, side)
        satin(L, poly_mask(lw), rust, 90 + side * 25, spacing=1.2)
        backstitch(L, lw, (110, 60, 40), closed=True)
        # scalloped band on lower wing
        band = [(cx + side * (x) * f, cy + y) for x, y in [(12, 30), (20, 34), (28, 38), (32, 44)]]
        backstitch(L, band, cream, width=1.0, dash=2.0, gap=1.0)
        uw = wing(upper, side)
        satin(L, poly_mask(uw), ochre, -20 * side + 90, spacing=1.2)
        backstitch(L, uw, (120, 80, 40), closed=True)
        # wing veins
        for vx, vy in [(50, -30), (56, -14), (44, 4)]:
            backstitch(L, [(cx + side * 8 * f, cy - 4), (cx + side * vx * f, cy + vy)],
                       (150, 100, 50), width=0.8, dash=2.0, gap=1.0)
        # eyespot
        ex, ey = cx + side * 36 * f, cy - 14
        satin(L, ellipse_mask(ex, ey, 8 * f, 8), navy, 45, spacing=1.0, shadow=False)
        satin(L, ellipse_mask(ex, ey, 4.5 * f, 4.5), cream, 0, spacing=1.0, shadow=False)
        knot(L, ex - side * 1.5 * f, ey - 1, 2.0, (60, 40, 30))
        # fringe dots along lower wing edge
        for i in range(4):
            knot(L, cx + side * (14 + i * 7) * f, cy + 48 - i * 3, 1.4, cream)
    # body
    body = ellipse_mask(cx, cy + 8, 7, 28)
    satin(L, body, (96, 66, 46), 0, spacing=1.1)
    fuzz(L, body, (140, 105, 75), 140, 2.0, 0.8)
    backstitch(L, ellipse_pts(cx, cy + 8, 7, 28), (60, 40, 30), closed=True)
    for i in range(5):
        backstitch(L, [(cx - 6, cy + i * 8), (cx + 6, cy + i * 8)], (60, 40, 30), width=0.8, dash=1.5, gap=0.8)
    # head + antennae (feathered)
    satin(L, ellipse_mask(cx, cy - 22, 6, 6), (80, 55, 40), 0, spacing=1.0)
    knot(L, cx - 3, cy - 23, 1.6, (20, 15, 15))
    knot(L, cx + 3, cy - 23, 1.6, (20, 15, 15))
    for side in (-1, 1):
        tip = (cx + side * (16 + 3 * ant * side), cy - 48 + 2 * ant * side)
        stem = [(cx + side * 2, cy - 27), (cx + side * 8, cy - 38), tip]
        backstitch(L, stem, (70, 45, 30), width=0.9, dash=2.0, gap=0.8)
        for k in range(7):
            t = (k + 1) / 8
            bx = cx + side * 2 + (tip[0] - cx - side * 2) * t
            by = cy - 27 + (tip[1] - cy + 27) * t
            backstitch(L, [(bx, by), (bx - side * 4 * (1 - t * 0.5), by - 2)], (90, 60, 40), width=0.6, dash=4, gap=0.1)
    return L

def beetle(leg=0.0, ant=0.0):
    L = new_layer()
    cx = 120
    green, dark, lime = (36, 128, 78), (18, 70, 52), (120, 190, 110)
    # legs first (under the body)
    for side in (-1, 1):
        for i, (hy, k) in enumerate([(104, -1), (124, 0), (146, 1)]):
            ph = leg * (1 if i == 1 else -0.5)
            pts = [(cx + side * 18, hy), (cx + side * (34 + 2 * ph), hy - 10 * k - 6 + 3 * ph),
                   (cx + side * (44 + 3 * ph), hy + 8 * k + 2)]
            backstitch(L, pts, (40, 30, 20), width=1.3, dash=2.4, gap=0.6)
            backstitch(L, [pts[2], (pts[2][0] + side * 4, pts[2][1] + 3)], (40, 30, 20), width=0.9, dash=4, gap=0.1)
    # elytra, two halves with different stitch angle so the sheen splits
    for side in (-1, 1):
        half = [(cx, 100)] + ellipse_pts(cx, 136, 27, 42, 40, 0, -math.pi / 2, math.pi / 2)[::side] + [(cx, 178)]
        if side == -1:
            half = mirror_pts(ellipse_pts(cx, 136, 27, 42, 40, 0, -math.pi / 2, math.pi / 2)) + [(cx, 178), (cx, 100)]
        m = poly_mask(half)
        satin(L, m, green, 90 + side * 28, spacing=1.15, sheen=0.35)
        backstitch(L, half, dark, closed=True)
        # pitted rows (knots)
        for row in range(5):
            for col in range(2):
                x = cx + side * (8 + col * 10)
                y = 112 + row * 13 + col * 4
                if math.hypot((x - cx) / 27, (y - 136) / 42) < 0.92:
                    knot(L, x, y, 1.5, lime)
    backstitch(L, [(cx, 100), (cx, 178)], dark, width=1.0)
    # pronotum + head
    pm = ellipse_mask(cx, 92, 21, 14)
    satin(L, pm, dark, 0, spacing=1.15, sheen=0.3)
    backstitch(L, ellipse_pts(cx, 92, 21, 14), (10, 40, 30), closed=True)
    knot(L, cx - 9, 90, 2.0, lime); knot(L, cx + 9, 90, 2.0, lime)
    hm = ellipse_mask(cx, 74, 11, 9)
    satin(L, hm, (14, 50, 40), 90, spacing=1.1)
    backstitch(L, ellipse_pts(cx, 74, 11, 9), (10, 30, 25), closed=True)
    knot(L, cx - 6, 72, 1.8, (230, 220, 200)); knot(L, cx + 6, 72, 1.8, (230, 220, 200))
    # clubbed antennae
    for side in (-1, 1):
        a = [(cx + side * 6, 68), (cx + side * (16 + 2 * ant * side), 58 - 2 * ant * side), (cx + side * (22 + 3 * ant * side), 54)]
        backstitch(L, a, (40, 30, 20), width=1.0, dash=2.0, gap=0.7)
        knot(L, a[-1][0], a[-1][1], 2.2, (60, 45, 30))
    return L

def bee(wing=0.0, ant=0.0):
    """wing 0..1 raises wings"""
    L = new_layer()
    cx = 120
    gold, black, cream = (214, 168, 56), (36, 30, 28), (240, 232, 215)
    # legs
    for side in (-1, 1):
        for hy, k in [(104, -1), (118, 0), (134, 1)]:
            pts = [(cx + side * 12, hy), (cx + side * 26, hy + 6 * k + 2), (cx + side * 34, hy + 12 * k + 12)]
            backstitch(L, pts, black, width=1.2, dash=2.2, gap=0.7)
    # wings (sparse translucent stitching + veins)
    for side in (-1, 1):
        rot = math.radians(side * (-38 + 22 * wing))
        wm = ellipse_mask(cx + side * 30, 96 - 8 * wing, 32, 13, rot)
        satin(L, wm, (250, 250, 255), 10 * side, spacing=2.6, alpha=120, shadow=False, sheen=0.0, var=0.04)
        pts = ellipse_pts(cx + side * 30, 96 - 8 * wing, 32, 13, 60, rot)
        backstitch(L, pts, (190, 190, 200), width=0.8, closed=True, dash=2.0, gap=1.2)
        for t in (0.35, 0.6):
            x0, y0 = cx + side * 6, 98 - 8 * wing
            x1, y1 = pts[int(len(pts) * t * 0.5)]
            backstitch(L, [(x0, y0), (x1, y1)], (190, 190, 200), width=0.7, dash=2.0, gap=1.2)
    # abdomen stripes
    ab = ellipse_mask(cx, 146, 23, 32)
    for i, y0 in enumerate(range(114, 180, 11)):
        band = mask_of(lambda d: d.rectangle([P(0, y0), P(240, y0 + 11)], fill=255))
        col = gold if i % 2 == 0 else black
        satin(L, ImageChops.multiply(ab, band), col, 0, spacing=1.15, sheen=0.3 if col == gold else 0.15)
    backstitch(L, ellipse_pts(cx, 146, 23, 32), (30, 25, 20), closed=True)
    knot(L, cx, 180, 1.6, black)  # stinger
    # thorax: fuzzy
    th = ellipse_mask(cx, 102, 18, 17)
    satin(L, th, (190, 150, 60), 0, spacing=1.3)
    fuzz(L, th, gold, 420, 2.6, 0.9)
    fuzz(L, th, (240, 205, 110), 120, 2.0, 0.7)
    backstitch(L, ellipse_pts(cx, 102, 18, 17), (120, 90, 40), closed=True, dash=1.8, gap=1.0)
    # head
    hm = ellipse_mask(cx, 78, 12, 11)
    satin(L, hm, black, 90, spacing=1.1)
    backstitch(L, ellipse_pts(cx, 78, 12, 11), (15, 12, 12), closed=True)
    knot(L, cx - 6, 76, 2.6, (110, 90, 80)); knot(L, cx + 6, 76, 2.6, (110, 90, 80))
    for side in (-1, 1):
        a = [(cx + side * 4, 69), (cx + side * (10 + 2 * ant * side), 60), (cx + side * (18 + 3 * ant * side), 56 + 2 * ant * side)]
        backstitch(L, a, black, width=0.9, dash=2.0, gap=0.7)
    return L

def dragonfly(tilt=0.0):
    L = new_layer()
    cx = 120
    teal, navy, ice = (40, 150, 150), (30, 60, 110), (248, 250, 255)
    # wings
    for side in (-1, 1):
        for (ang, wl, ww, oy) in [(-14, 58, 11, 0), (12, 54, 10, 10)]:
            rot = math.radians(side * (ang + 6 * tilt))
            wx = cx + side * (wl * 0.55) * math.cos(rot)
            wy = 96 + oy + (wl * 0.55) * math.sin(rot) * side
            wm = ellipse_mask(wx, wy, wl * 0.5, ww * 0.5, rot)
            satin(L, wm, ice, 90, spacing=2.8, alpha=110, shadow=False, sheen=0.0, var=0.03)
            pts = ellipse_pts(wx, wy, wl * 0.5, ww * 0.5, 80, rot)
            backstitch(L, pts, (170, 185, 200), width=0.8, closed=True, dash=2.0, gap=1.1)
            # lattice veins
            for t in range(1, 7):
                f = t / 7
                p0 = pts[int(len(pts) * (0.5 + f * 0.5)) % len(pts)]
                p1 = pts[int(len(pts) * (0.5 - f * 0.5)) % len(pts)]
                backstitch(L, [p0, p1], (175, 190, 205), width=0.6, dash=1.6, gap=1.0)
            backstitch(L, [(cx + side * 6, 96 + oy), pts[0]], (150, 170, 190), width=0.8, dash=2.0, gap=0.9)
    # body: segmented abdomen
    for i in range(9):
        y = 118 + i * 10
        r = 5.5 - i * 0.35
        col = teal if i % 2 == 0 else navy
        satin(L, ellipse_mask(cx, y, r, 5.6), col, 0, spacing=1.0, sheen=0.3)
        backstitch(L, ellipse_pts(cx, y, r, 5.6), (20, 40, 70), closed=True, dash=1.6, gap=0.9)
    # thorax + head
    tm = ellipse_mask(cx, 100, 9, 14)
    satin(L, tm, (30, 110, 120), 0, spacing=1.0, sheen=0.3)
    backstitch(L, ellipse_pts(cx, 100, 9, 14), (20, 40, 70), closed=True)
    hm = ellipse_mask(cx, 80, 9, 8)
    satin(L, hm, (30, 90, 110), 90, spacing=1.0)
    knot(L, cx - 5, 79, 3.2, (60, 170, 150)); knot(L, cx + 5, 79, 3.2, (60, 170, 150))
    # legs tucked
    for side in (-1, 1):
        for hy in (94, 102, 110):
            backstitch(L, [(cx + side * 8, hy), (cx + side * 16, hy - 4), (cx + side * 20, hy + 2)], (30, 40, 50), width=0.9, dash=1.8, gap=0.7)
    return L

def ladybug(leg=0.0, ant=0.0):
    L = new_layer()
    cx = 120
    red, black, cream = (196, 38, 38), (28, 24, 24), (240, 232, 215)
    for side in (-1, 1):
        for i, (hy, k) in enumerate([(108, -1), (128, 0), (150, 1)]):
            ph = leg * (1 if i == 1 else -0.6)
            pts = [(cx + side * 22, hy), (cx + side * (36 + 2 * ph), hy - 6 * k - 5 + 2 * ph), (cx + side * (44 + 3 * ph), hy + 8 * k + 4)]
            backstitch(L, pts, black, width=1.3, dash=2.3, gap=0.6)
    for side in (-1, 1):
        half = ellipse_pts(cx, 132, 31, 37, 40, 0, -math.pi / 2, math.pi / 2)
        if side == -1:
            half = mirror_pts(half)
        half = half + [(cx, 169), (cx, 95)]
        satin(L, poly_mask(half), red, 90 + side * 22, spacing=1.15, sheen=0.3)
        backstitch(L, half, (120, 20, 20), closed=True)
        for (sx, sy, sr) in [(13, 112, 5), (22, 134, 5.5), (10, 150, 5), (24, 158, 3.5)]:
            satin(L, ellipse_mask(cx + side * sx, sy, sr, sr), black, 45, spacing=1.0, shadow=False)
            backstitch(L, ellipse_pts(cx + side * sx, sy, sr, sr), (10, 8, 8), closed=True, dash=1.5, gap=0.8)
    backstitch(L, [(cx, 95), (cx, 169)], (60, 10, 10), width=1.0)
    # pronotum + head
    pm = ellipse_mask(cx, 94, 24, 11)
    satin(L, pm, black, 0, spacing=1.1, sheen=0.25)
    backstitch(L, ellipse_pts(cx, 94, 24, 11), (10, 8, 8), closed=True)
    satin(L, ellipse_mask(cx - 14, 92, 5, 4), cream, 20, spacing=1.0, shadow=False)
    satin(L, ellipse_mask(cx + 14, 92, 5, 4), cream, -20, spacing=1.0, shadow=False)
    hm = ellipse_mask(cx, 78, 11, 8)
    satin(L, hm, black, 90, spacing=1.1)
    backstitch(L, ellipse_pts(cx, 78, 11, 8), (10, 8, 8), closed=True)
    knot(L, cx - 5, 77, 1.9, cream); knot(L, cx + 5, 77, 1.9, cream)
    for side in (-1, 1):
        a = [(cx + side * 5, 71), (cx + side * (11 + 2 * ant * side), 64), (cx + side * (15 + 3 * ant * side), 60 + 2 * ant * side)]
        backstitch(L, a, black, width=0.9, dash=2.0, gap=0.7)
        knot(L, a[-1][0], a[-1][1], 1.5, black)
    return L

# ----------------------------------------------------------------- compose
FABRIC = linen()
CIRCLE = Image.new("L", (W, W), 0)
ImageDraw.Draw(CIRCLE).ellipse([0, 0, W - 1, W - 1], fill=255)

def compose(layer, rot_deg=0.0, scale=1.0):
    lay = layer
    if scale != 1.0:
        n2 = int(N * scale)
        lay = layer.resize((n2, n2), Image.LANCZOS)
        pad = Image.new("RGBA", (N, N), (0, 0, 0, 0))
        pad.paste(lay, ((N - n2) // 2, (N - n2) // 2))
        lay = pad
    if rot_deg:
        lay = lay.rotate(rot_deg, resample=Image.BICUBIC, center=(N / 2, N / 2))
    out = FABRIC.copy()
    out.paste(lay, (0, 0), lay)
    out = out.resize((W, W), Image.LANCZOS)
    black = Image.new("RGB", (W, W), (0, 0, 0))
    return Image.composite(out, black, CIRCLE)

INSECTS = {
    "moth":      lambda t: moth(flap=0.5 - 0.5 * math.cos(t * 2 * math.pi), ant=math.sin(t * 2 * math.pi)),
    "beetle":    lambda t: beetle(leg=math.sin(t * 2 * math.pi), ant=math.sin(t * 2 * math.pi + 1)),
    "bee":       lambda t: bee(wing=0.5 - 0.5 * math.cos(t * 2 * math.pi), ant=math.sin(t * 2 * math.pi)),
    "dragonfly": lambda t: dragonfly(tilt=math.sin(t * 2 * math.pi)),
    "ladybug":   lambda t: ladybug(leg=math.sin(t * 2 * math.pi), ant=math.sin(t * 2 * math.pi + 2)),
}

if __name__ == "__main__":
    stills = []
    gif_frames = []
    FR = 8  # frames per idle cycle
    for name, fn in INSECTS.items():
        random.seed(hash(name) & 0xffff)
        # resting still frame: what's shown 95% of the time
        still = compose(fn(0.0), rot_deg=random.uniform(-6, 6), scale=1.32)
        still.save(f"{OUT}/{name}.png")
        stills.append(still)
        # idle "stir": a short cycle of movement plus a few degrees of turn
        cyc = []
        base_rot = random.uniform(-6, 6)
        for i in range(FR):
            t = i / FR
            random.seed((hash(name) & 0xffff) + i)
            fr = compose(fn(t), rot_deg=base_rot + 4 * math.sin(t * 2 * math.pi), scale=1.32)
            fr.save(f"{OUT}/{name}_{i:02d}.png")
            cyc.append(fr)
        # hold still, stir, hold still
        gif_frames += [still] * 10 + cyc + [still] * 6
        # crossfade to next insect handled below
    # crossfades between stills (what the firmware does when it rotates the set)
    seq = []
    names = list(INSECTS.keys())
    k = 0
    for idx, name in enumerate(names):
        block = gif_frames[idx * (10 + FR + 6):(idx + 1) * (10 + FR + 6)]
        seq += block
        nxt = stills[(idx + 1) % len(stills)]
        for j in range(1, 6):
            seq.append(Image.blend(stills[idx], nxt, j / 6))
    seq[0].save(f"{OUT}/preview.gif", save_all=True, append_images=seq[1:], duration=110, loop=0)
    # contact sheet
    sheet = Image.new("RGB", (W * 5 + 60, W + 20), (20, 20, 20))
    for i, im in enumerate(stills):
        sheet.paste(im, (10 + i * (W + 10), 10))
    sheet.save(f"{OUT}/sheet.png")
    print("done")
