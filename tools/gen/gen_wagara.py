#!/usr/bin/env python3
"""Ten traditional Japanese textile patterns (wagara), large-scale, indigo + cream, sewn live."""
import math, random, os
from PIL import Image, ImageDraw, ImageChops
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, ellipse_mask, poly_mask, new_layer, satin, backstitch, sm
from gen_stitch import stitch, needle, resample
from gen_granny import yarn
from gen_linen import bg_linen, compose_bg
import gen_linen, gen_granny2 as G2

OUT = "/home/claude/eye_pin_lowpower/wagara"
os.makedirs(OUT, exist_ok=True)
gen_linen.OUT = OUT; gen_linen.FRAMES = 36
INDIGO, CREAM, VERM, INDIGO_L = (38, 52, 96), (238, 230, 210), (196, 66, 44), (74, 96, 150)
TAU = 2 * math.pi
def inside(x, y, R=118): return math.hypot(x - 120, y - 120) < R
def bg_indigo(seed): return bg_linen(seed, (34, 46, 86))
def bg_cream(seed): return bg_linen(seed, (236, 228, 208))

def dashes(pts, col, w=2.6, dash=7, gap=3, closed=False, clip=118):
    ev = []; at, total = resample(pts + ([pts[0]] if closed else [])); pos = 0
    while pos < total:
        a, b = at(pos), at(min(total, pos + dash))
        if inside(*a, clip) or inside(*b, clip): ev.append(("stitch", a, b, col, w))
        pos += dash + gap
    return ev

def fill(poly, col, ang, sp=1.6, clip=119):
    m = ImageChops.multiply(poly_mask(poly), ellipse_mask(120, 120, clip, clip))
    return ("fn", (lambda m=m, col=col, ang=ang, sp=sp: lambda L: satin(L, m, col, ang, spacing=sp, sheen=0.22))(), poly[0], col)

# 1 shippō — interlocking circles
def shippo():
    ev = []; r = 40; s = r * math.sqrt(2)
    centers = []
    for i in range(-3, 4):
        for j in range(-3, 4):
            centers += [(120 + i * s, 120 + j * s), (120 + i * s + s / 2, 120 + j * s + s / 2)]
    centers = [c for c in centers if math.hypot(c[0] - 120, c[1] - 120) < 118 + r]
    centers.sort(key=lambda c: math.hypot(c[0] - 120, c[1] - 120))
    for (cx, cy) in centers: ev += dashes(ellipse_pts(cx, cy, r, r, 64), CREAM, 2.8, 7, 3, closed=True)
    for (cx, cy) in centers:
        if inside(cx, cy, 110): ev.append(("knot", cx, cy, 3.2, VERM))
    return ev

# 2 kikkō — tortoiseshell hexagons
def kikko():
    ev = []; R = 36; w = math.sqrt(3) * R
    cells = []
    for j in range(-4, 5):
        for i in range(-4, 5):
            cx = 120 + i * w + (j % 2) * w / 2; cy = 120 + j * 1.5 * R
            if math.hypot(cx - 120, cy - 120) < 118 + R: cells.append((cx, cy))
    cells.sort(key=lambda c: math.hypot(c[0] - 120, c[1] - 120))
    for (cx, cy) in cells:
        hexp = [(cx + R * math.cos(math.radians(60 * k + 30)), cy + R * math.sin(math.radians(60 * k + 30))) for k in range(6)]
        ev += dashes(hexp, CREAM, 3.0, 8, 3, closed=True)
    for (cx, cy) in cells:
        if inside(cx, cy, 108):
            for k in range(3):
                a = math.radians(60 * k)
                ev.append(("stitch", (cx - 9 * math.cos(a), cy - 9 * math.sin(a)), (cx + 9 * math.cos(a), cy + 9 * math.sin(a)), VERM, 2.4))
    return ev

# 3 yagasuri — arrow feathers
def yagasuri():
    ev = []; cw = 40; fh = 44
    for ci, x0 in enumerate(range(-20, 260, cw)):
        if not (inside(x0 + cw / 2, 120, 118 + cw)): continue
        flip = ci % 2
        for y0 in range(-40 + (ci % 2) * fh // 2, 280, fh):
            # left and right feather halves of one fletching
            for side in (-1, 1):
                xa = x0 + cw / 2; xb = xa + side * cw / 2
                poly = [(xa, y0), (xb, y0 - 18), (xb, y0 + fh - 18 - 8), (xa, y0 + fh - 8)] if not flip else [(xa, y0 + fh - 8), (xb, y0 + fh - 18 - 8 + 36), (xb, y0 - 18 + 36), (xa, y0)]
                if any(inside(px, py, 119) for px, py in poly): ev.append(fill(poly, INDIGO if side == 1 else INDIGO_L, 90 + side * 35))
        ev += dashes([(x0 + cw / 2, -10), (x0 + cw / 2, 250)], CREAM, 2.2, 9, 3)
    return ev

# 4 ichimatsu — checkerboard
def ichimatsu():
    ev = []; c = 40
    for i in range(-4, 4):
        for j in range(-4, 4):
            if (i + j) % 2: continue
            x, y = 120 + i * c, 120 + j * c
            if inside(x + c / 2, y + c / 2, 118 + c): ev.append(fill([(x, y), (x + c, y), (x + c, y + c), (x, y + c)], INDIGO, 45 if i % 2 else -45))
    for k in range(-3, 4):
        ev += dashes([(120 + k * c, -10), (120 + k * c, 250)], CREAM, 2.0, 8, 3); ev += dashes([(-10, 120 + k * c), (250, 120 + k * c)], CREAM, 2.0, 8, 3)
    return ev

# 5 uroko — scales (triangles)
def uroko():
    ev = []; s = 52; h = s * math.sqrt(3) / 2
    for j in range(-4, 5):
        y = 120 + j * h
        for i in range(-5, 6):
            x = 120 + i * s + (j % 2) * s / 2
            tri = [(x, y + h / 2), (x + s / 2, y - h / 2), (x + s, y + h / 2)]
            if any(inside(px, py, 119) for px, py in tri): ev.append(fill(tri, INDIGO, 90))
    for j in range(-4, 6): ev += dashes([(-10, 120 + j * h + h / 2), (250, 120 + j * h + h / 2)], CREAM, 2.0, 8, 3)
    for sgn in (1, -1):
        for k in range(-6, 7):
            seg = G2.chord(120 + k * s + (s / 2 if sgn < 0 else 0), 120, 0.5 * sgn, math.sqrt(3) / 2, 118)
            if seg: ev += dashes([seg[0], seg[1]], CREAM, 2.0, 8, 3)
    return ev

# 6 kagome — basket lattice
def kagome():
    ev = []; sp = 46
    for fam in range(3):
        a = math.radians(60 * fam); dx, dy = math.cos(a), math.sin(a); nx, ny = -dy, dx
        for k in range(-4, 5):
            for off in (-5, 5):
                px, py = 120 + nx * (k * sp + off), 120 + ny * (k * sp + off)
                seg = G2.chord(px, py, dx, dy, 118)
                if seg: ev += dashes([seg[0], seg[1]], CREAM, 3.2, 10, 3)
    return ev

# 7 hishi / hanabishi — diamonds within diamonds
def hishi():
    ev = []; dw, dh = 60, 84
    for j in range(-3, 4):
        for i in range(-3, 4):
            cx = 120 + i * dw + (j % 2) * dw / 2; cy = 120 + j * dh / 2
            if not inside(cx, cy, 118 + 30): continue
            outer = [(cx, cy - dh / 2), (cx + dw / 2, cy), (cx, cy + dh / 2), (cx - dw / 2, cy)]
            ev += dashes(outer, CREAM, 2.8, 8, 3, closed=True)
            if inside(cx, cy, 112):
                inner = [(cx, cy - dh / 4), (cx + dw / 4, cy), (cx, cy + dh / 4), (cx - dw / 4, cy)]
                ev.append(fill(inner, VERM, 0, 1.4))
                ev += dashes(inner, CREAM, 2.0, 6, 3, closed=True)
    return ev

# 8 tatewaku — rising steam
def tatewaku():
    ev = []; sp = 48; amp = 11
    for k in range(-3, 4):
        x0 = 120 + k * sp
        for sgn in (1, -1):
            pts = [(x0 + sgn * (sp / 4 + amp * math.sin(y / 60 * math.pi)), y) for y in range(-20, 262, 6)]
            ev += dashes(pts, CREAM, 3.0, 8, 3)
    for k in range(-3, 4):
        x0 = 120 + k * sp
        for y in range(30, 240, 120):
            if inside(x0, y, 108): ev.append(("knot", x0, y, 4.5, VERM))
    return ev

# 9 kanoko shibori — fawn spots
def kanoko():
    ev = []; sp = 36
    pts = []
    for j in range(-4, 5):
        for i in range(-4, 5):
            x = 120 + i * sp + (j % 2) * sp / 2; y = 120 + j * sp * 0.87
            if inside(x, y, 112): pts.append((x, y))
    pts.sort(key=lambda p: math.hypot(p[0] - 120, p[1] - 120))
    for (x, y) in pts:
        ring = ImageChops.subtract(ellipse_mask(x, y, 12, 12), ellipse_mask(x, y, 5.5, 5.5))
        ev.append(("fn", (lambda ring=ring: lambda L: satin(L, ring, CREAM, random.uniform(0, 180), spacing=1.4, sheen=0.2, shadow=False, var=0.12))(), (x, y), CREAM))
        ev.append(("fn", (lambda x=x, y=y: lambda L: backstitch(L, ellipse_pts(x, y, 12.5, 12.5, 30), (210, 200, 180), width=0.9, dash=1.6, gap=1.4, closed=True))(), (x, y), CREAM))
    return ev

# 10 higaki — cypress-fence herringbone
def higaki():
    ev = []; cw = 44; sh = 16
    for ci, x0 in enumerate(range(-24, 264, cw)):
        slant = 1 if ci % 2 == 0 else -1
        for y0 in range(-60, 280, sh * 2):
            poly = [(x0, y0), (x0 + cw, y0 + slant * cw * 0.5), (x0 + cw, y0 + slant * cw * 0.5 + sh), (x0, y0 + sh)]
            if any(inside(px, py, 119) for px, py in poly): ev.append(fill(poly, INDIGO if (y0 // (sh * 2)) % 2 else INDIGO_L, 90 + slant * 27))
        ev += dashes([(x0, -10), (x0, 250)], CREAM, 2.0, 8, 3)
    return ev

PIECES = [("shippo", shippo, bg_indigo, "needle"), ("kikko", kikko, bg_indigo, "needle"), ("yagasuri", yagasuri, bg_cream, "needle"),
          ("ichimatsu", ichimatsu, bg_cream, "needle"), ("uroko", uroko, bg_cream, "needle"), ("kagome", kagome, bg_indigo, "needle"),
          ("hishi", hishi, bg_indigo, "needle"), ("tatewaku", tatewaku, bg_indigo, "needle"), ("kanoko", kanoko, bg_indigo, "needle"), ("higaki", higaki, bg_cream, "needle")]

if __name__ == "__main__":
    out = []
    for i, (name, fn, bgf, tool) in enumerate(PIECES):
        random.seed(400 + i); out.append((name, gen_linen.render_events(name, fn(), bgf(40 + i), tool))); print(name)
    seq = []
    for i, (name, fr) in enumerate(out):
        seq += fr + [fr[-1]] * 10; nxt = out[(i + 1) % len(out)][1][0]; seq += [Image.blend(fr[-1], nxt, j / 5) for j in range(1, 5)]
    seq[0].save(f"{OUT}/preview_wagara.gif", save_all=True, append_images=seq[1:], duration=90, loop=0)
    sheet = Image.new("RGB", (W * 5 + 60, W * 2 + 30 + 90), (40, 40, 40))
    for i, (name, fr) in enumerate(out):
        sheet.paste(fr[-1], (10 + (i % 5) * (W + 10), 10 + (i // 5) * (W + 10)))
        sheet.paste(fr[-1].resize((70, 70), Image.LANCZOS), (10 + i * 80, W * 2 + 35))
    sheet.save(f"{OUT}/sheet_wagara.png"); print("done")
