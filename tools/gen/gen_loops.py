#!/usr/bin/env python3
"""Ten seamless 32-frame loops for the pin. Writes <name>_bg.png, <name>_NN.png and a
<name>.loop marker so pack_delta.py adds a wrap record and the firmware loops them."""
import math, random, os
from PIL import Image, ImageDraw, ImageChops
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, ellipse_mask, poly_mask, rect_mask, new_layer, satin, backstitch, sm
from gen_stitch import stitch, loop as thread_loop, needle, resample
from gen_granny import yarn, post, hook, MUSTARD, OXBLOOD, TEAL, CREAM, SOOT, PLUM, RUST, SAGE, PALETTE
from gen_linen import bg_linen, bg_satin, BLACK_BG, compose_bg, export_bg
import gen_granny2 as G2

OUT = "/home/claude/eye_pin_lowpower/loops"
os.makedirs(OUT, exist_ok=True)
FRAMES = 32
CHAR, BONE = (112, 104, 112), (236, 226, 204)
TAU = 2 * math.pi

def rot(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]

# 1 ---------------------------------------------------------------- swinging spider
def swinging_spider(f):
    L = new_layer(); ph = TAU * f / FRAMES
    web = (222, 216, 200)
    for k in range(5):                                   # static web corner, top-left
        a = math.radians(-20 + k * 28); yarn(L, [(0, 0), (130 * math.cos(a), 130 * math.sin(a))], web, 1.8)
    for r in (30, 52, 74, 96):
        pts = [(r * math.cos(math.radians(-20 + t * 112 / 20)) , r * math.sin(math.radians(-20 + t * 112 / 20))) for t in range(21)]
        yarn(L, [(x, y - 2 * math.sin(t * 0.9)) for t, (x, y) in enumerate(pts)], web, 1.5)
    th = math.radians(22) * math.sin(ph); L_ = 108
    ax, ay = 150, 0
    sx, sy = ax + L_ * math.sin(th), ay + L_ * math.cos(th)
    yarn(L, [(ax, ay), ((ax + sx) / 2 + 2 * math.sin(ph), (ay + sy) / 2), (sx, sy)], web, 1.8)
    knot(L, sx, sy + 12, 13, (58, 52, 56)); knot(L, sx, sy - 5, 8, (58, 52, 56))
    swing = -0.35 * math.cos(ph)                         # legs trail the motion
    for s in (-1, 1):
        for (ex, ey) in ((30, -18), (36, -4), (34, 12), (26, 26)):
            a0 = (sx + s * 8, sy + 4); mid = (sx + s * ex * 0.6, sy + ey * 0.4 + 2); end = (sx + s * ex, sy + ey + 4)
            mid = rot([mid], sx, sy, swing * s)[0]; end = rot([end], sx, sy, swing * s)[0]
            yarn(L, [a0, mid, end], (58, 52, 56), 2.2)
    knot(L, sx - 3.5, sy - 7, 1.8, OXBLOOD); knot(L, sx + 3.5, sy - 7, 1.8, OXBLOOD)
    return L

# 2 ---------------------------------------------------------------- bunting
def bunting(f):
    L = new_layer(); ph = TAU * f / FRAMES
    pts = [(x, 62 + 22 * math.sin(x / 240 * math.pi) + 3 * math.sin(ph)) for x in range(-10, 251, 10)]
    yarn(L, pts, (90, 70, 56), 2.2)
    cols = [MUSTARD, OXBLOOD, TEAL, CREAM, PLUM, RUST, SAGE]
    for i, x in enumerate(range(18, 240, 30)):
        y = 62 + 22 * math.sin(x / 240 * math.pi) + 3 * math.sin(ph)
        sw = math.radians(9) * math.sin(ph + i * 0.7)
        tri = rot([(x - 13, y + 2), (x + 13, y + 2), (x, y + 40)], x, y + 2, sw)
        col = cols[i % len(cols)]
        satin(L, poly_mask(tri), col, 90 + math.degrees(sw), spacing=1.4, sheen=0.3)
        inner = rot([(x - 7, y + 10), (x + 7, y + 10), (x, y + 30)], x, y + 2, sw)
        satin(L, poly_mask(inner), cols[(i + 3) % len(cols)], math.degrees(sw), spacing=1.3, sheen=0.3, shadow=False)
        knot(L, *rot([(x, y + 18)], x, y + 2, sw)[0], 2.4, cols[(i + 5) % len(cols)])
        yarn(L, tri + [tri[0]], shade(col, 0.6), 1.6)
    return L

# 3 ---------------------------------------------------------------- spool
def spool(f):
    L = new_layer(); ph = TAU * f / FRAMES
    cx, cy = 104, 128
    wood = (170, 128, 84)
    satin(L, ellipse_mask(cx, cy - 42, 34, 9), wood, 0, spacing=1.3, sheen=0.3)
    satin(L, ellipse_mask(cx, cy + 42, 34, 9), wood, 0, spacing=1.3, sheen=0.3)
    satin(L, rect_mask(cx - 34, cy - 42, cx + 34, cy + 42) if False else poly_mask([(cx - 34, cy - 42), (cx + 34, cy - 42), (cx + 34, cy + 42), (cx - 34, cy + 42)]), shade(wood, 0.75), 90, spacing=1.3, sheen=0.1, shadow=False)
    # wound thread: diagonal stripes sliding = rotation
    body = poly_mask([(cx - 30, cy - 34), (cx + 30, cy - 34), (cx + 30, cy + 34), (cx - 30, cy + 34)])
    satin(L, body, MUSTARD, 90, spacing=1.2, sheen=0.35)
    stripes = new_layer(); d = ImageDraw.Draw(stripes)
    period = 12; off = (ph / TAU) * period
    for k in range(-8, 10):
        y0 = cy - 34 + k * period + off
        d.line([P(cx - 30, y0 + 4), P(cx + 30, y0 - 4)], fill=shade(MUSTARD, 0.72) + (200,), width=int(1.6 * S))
    L.paste(stripes, (0, 0), ImageChops.multiply(body, stripes.split()[3]))
    satin(L, ellipse_mask(cx, cy - 42, 34, 9), wood, 0, spacing=1.3, sheen=0.3)
    # thread travelling off the spool in a moving wave to a needle on the right
    pts = [(cx + 30 + t, cy - 30 - t * 0.35 + 6 * math.sin(t / 14 - ph)) for t in range(0, 100, 4)]
    yarn(L, pts, MUSTARD, 2.0)
    needle(L, pts[-1], (1, -0.35), MUSTARD)
    return L

# 4 ---------------------------------------------------------------- rolling yarn
def rolling_yarn(f):
    L = new_layer(); ph = TAU * f / FRAMES; random.seed(44)
    cx, cy, R = 96, 128, 46
    for ang_base, n in ((20, 14), (75, 14), (130, 12)):
        for i in range(n):
            ang = math.radians(ang_base + random.uniform(-6, 6)) + ph; dx, dy = math.cos(ang), math.sin(ang)
            off = random.uniform(-R * 0.9, R * 0.9)
            seg = G2.chord(cx - dy * off, cy + dx * off, dx, dy, R - 1.5, cx, cy)
            if seg: yarn(L, [seg[0], ((seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2), seg[1]], shade((172, 54, 60), random.uniform(0.85, 1.15)), 3.2)
    sh = ellipse_mask(cx, cy, R, R); dark = new_layer(); d = ImageDraw.Draw(dark)
    d.ellipse([P(cx - R, cy - R), P(cx + R, cy + R)], fill=(0, 0, 0, 70)); d.ellipse([P(cx - R * 0.9, cy - R * 1.05), P(cx + R * 0.7, cy + R * 0.55)], fill=(0, 0, 0, 0))
    L.paste(dark, (0, 0), ImageChops.multiply(sh, dark.split()[3]))
    tail = [(cx + R - 2 + t, cy + 30 - 14 * math.sin(t / 16 + ph) * (t / 110)) for t in range(0, 120, 4)]
    yarn(L, tail, (172, 54, 60), 3.0)
    yarn(L, [(0, cy + R + 2), (240, cy + R + 2)], (90, 76, 70), 2.0)     # floor line
    return L

# 5 ---------------------------------------------------------------- rotating spiral
def rotating_spiral(f):
    L = new_layer(); ph = TAU * f / FRAMES
    b = 11.5 / TAU
    for col, off in ((CHAR, 0.0), (BONE, math.pi)):
        pts = []; th = 0.0
        while True:
            r = 2 + b * (th + off)
            if r > 118: break
            pts.append((120 + r * math.cos(th + ph), 120 + r * math.sin(th + ph))); th += 6.0 / max(r, 4)
        for i in range(0, len(pts) - 1, 2): yarn(L, pts[i:i + 3], col, 5.2)
    return L

# 6 ---------------------------------------------------------------- moon pendulum
def moon_pendulum(f):
    L = new_layer(); ph = TAU * f / FRAMES; random.seed(9)
    for i, (sx, sy, sr) in enumerate([(40, 70, 2.0), (66, 40, 1.5), (190, 50, 2.2), (206, 96, 1.5), (176, 160, 1.8), (60, 170, 1.4)]):
        tw = 0.65 + 0.35 * math.sin(ph * 2 + i * 1.7)
        knot(L, sx, sy, sr * tw, shade(MUSTARD, 0.7 + 0.5 * tw))
        if sr > 1.9:
            for (ax, ay) in ((1, 0), (0, 1)): stitch(L, (sx - ax * 4 * tw, sy - ay * 4 * tw), (sx + ax * 4 * tw, sy + ay * 4 * tw), shade(MUSTARD, 0.9), 0.9)
    th = math.radians(12) * math.sin(ph); ax, ay = 120, -4; L_ = 118
    mx, my = ax + L_ * math.sin(th), ay + L_ * math.cos(th)
    yarn(L, [(ax, ay), (mx, my - 36)], (90, 70, 56), 1.8)
    r = 44
    full = ellipse_mask(mx, my, r, r); cut = ellipse_mask(mx + 26, my - 8, r * 0.86, r * 0.86)
    moon = ImageChops.subtract(full, cut)
    seam = poly_mask(rot([(0, my - 6), (240, my + 10), (240, -50), (0, -50)], mx, my, th))
    satin(L, ImageChops.multiply(moon, seam), MUSTARD, 35 + math.degrees(th), spacing=1.5, sheen=0.3)
    satin(L, ImageChops.subtract(moon, seam), CREAM, -30 + math.degrees(th), spacing=1.5, sheen=0.25)
    out = ellipse_pts(mx, my, r + 1, r + 1, 60, 0, math.radians(100), math.radians(400))
    at, total = resample(out)
    for k in range(26):
        t = total * k / 26; a = at(t); bb = at(min(total, t + 2)); dx, dy = bb[0] - a[0], bb[1] - a[1]; ln = math.hypot(dx, dy) or 1; nx, ny = -dy / ln, dx / ln
        stitch(L, (a[0] + nx * 2.5 - dx / ln * 1.5, a[1] + ny * 2.5 - dy / ln * 1.5), (a[0] - nx * 2.5 + dx / ln * 1.5, a[1] - ny * 2.5 + dy / ln * 1.5), (96, 74, 60), 1.3)
    return L

# 7 ---------------------------------------------------------------- mandala turn
def mandala_turn(f):
    L = new_layer(); ph = TAU * f / FRAMES
    cx, cy = 120, 120; step = 13; r0 = 11
    pal = [MUSTARD, OXBLOOD, TEAL, CREAM, RUST, PLUM, SAGE, MUSTARD]
    yarn(L, ellipse_pts(cx, cy, r0 * 0.6, r0 * 0.6, 24), pal[0], 3.0)
    for n in range(1, 8):
        col = pal[n % len(pal)]; ri = r0 + step * (n - 1); ro = ri + step - 2
        count = 6 + 5 * n
        turn = (ph / TAU) * (TAU / count) * (1 if n % 2 else -1)      # each ring advances exactly one cluster per loop
        for k in range(count):
            a = TAU * k / count - math.pi / 2 + turn
            base = (cx + ri * math.cos(a), cy + ri * math.sin(a))
            for off in (-0.045, 0, 0.045):
                aa = a + off * (12 / n); yarn(L, post(base, (cx + ro * math.cos(aa), cy + ro * math.sin(aa))), col, 3.0)
            a_next = TAU * (k + 1) / count - math.pi / 2 + turn; mid = (a + a_next) / 2
            yarn(L, [(cx + ro * math.cos(a + 0.045 * 12 / n), cy + ro * math.sin(a + 0.045 * 12 / n)), (cx + (ro + 1.5) * math.cos(mid), cy + (ro + 1.5) * math.sin(mid)),
                     (cx + ro * math.cos(a_next - 0.045 * 12 / n), cy + ro * math.sin(a_next - 0.045 * 12 / n))], col, 2.4)
    return L

# 8 ---------------------------------------------------------------- marching stitch
def marching_stitch(f):
    L = new_layer(); ph = f / FRAMES
    def march(pts, col, dash, gap, w, phase, closed=True):
        at, total = resample(pts + ([pts[0]] if closed else [])); period = dash + gap
        pos = -period + phase * period
        while pos < total:
            a = max(0, pos); b = min(total, pos + dash)
            if b > a: stitch(L, at(a), at(b), col, w)
            pos += period
    march(ellipse_pts(120, 120, 112, 112, 120), OXBLOOD, 7, 4, 2.0, ph)
    march(ellipse_pts(120, 120, 100, 100, 120), TEAL, 5, 4, 1.6, 1 - ph)
    march(G2.heart_pts(120, 116, 3.6), OXBLOOD, 6, 3.5, 2.0, ph)
    march(G2.heart_pts(120, 116, 2.6), MUSTARD, 4, 3, 1.5, 1 - ph)
    march(G2.heart_pts(120, 116, 1.6), TEAL, 4, 3, 1.5, ph)
    knot(L, 120, 118, 3.5, OXBLOOD)
    return L

# 9 ---------------------------------------------------------------- waving ripple
def waving_ripple(f):
    L = new_layer(); ph = TAU * f / FRAMES
    period, amp = 52, 15
    cols = [MUSTARD, CREAM, OXBLOOD, TEAL, CREAM, PLUM, SAGE, CREAM]
    for row, y in enumerate(range(-30, 262, 9)):
        col = cols[row % len(cols)]
        pts = [(x, y + amp * (1 if (x // (period // 2)) % 2 else -1) + 7 * math.sin(x / 38 + ph - row * 0.25)) for x in range(-26, 270, period // 2)]
        yarn(L, pts, col, 4.6)
    return L

# 10 --------------------------------------------------------------- bobbing buttons
def bobbing_buttons(f):
    L = new_layer(); ph = TAU * f / FRAMES; random.seed(77)
    spots = [(60, 70, 15, MUSTARD), (120, 58, 12, OXBLOOD), (178, 74, 16, TEAL), (48, 128, 11, PLUM), (120, 120, 20, CREAM), (190, 132, 12, RUST),
             (66, 184, 14, SAGE), (126, 186, 11, OXBLOOD), (178, 186, 15, MUSTARD)]
    for i, (x, y0, r, col) in enumerate(spots):
        y = y0 + 5 * math.sin(ph + i * 0.8); tilt = math.radians(10) * math.sin(ph + i * 0.8 + 1.2)
        thr = [SOOT, CREAM, MUSTARD, TEAL][i % 4] if col != [SOOT, CREAM, MUSTARD, TEAL][i % 4] else OXBLOOD
        satin(L, ellipse_mask(x, y, r, r), col, random.uniform(0, 180), spacing=1.3, sheen=0.35)
        satin(L, ellipse_mask(x, y, r * 0.78, r * 0.78), shade(col, 0.85), random.uniform(0, 180), spacing=1.3, sheen=0.3)
        yarn(L, ellipse_pts(x, y, r * 0.78, r * 0.78, 28), shade(col, 1.25) if sum(col) < 400 else shade(col, 0.7), 1.4)
        hs = r * 0.26; hr = r * 0.11 + 0.8
        holes = rot([(x - hs, y - hs), (x + hs, y - hs), (x + hs, y + hs), (x - hs, y + hs)], x, y, tilt)
        d = ImageDraw.Draw(L)
        for (hx, hy) in holes: d.ellipse([P(hx - hr, hy - hr), P(hx + hr, hy + hr)], fill=(8, 8, 10, 255))
        yarn(L, [holes[0], holes[2]], thr, 1.9); yarn(L, [holes[1], holes[3]], thr, 1.9)
    return L

PIECES = [
    ("swinging_spider", swinging_spider, lambda: BLACK_BG),
    ("bunting", bunting, lambda: bg_linen(21)),
    ("spool", spool, lambda: bg_satin(22)),
    ("rolling_yarn", rolling_yarn, lambda: BLACK_BG),
    ("rotating_spiral", rotating_spiral, lambda: BLACK_BG),
    ("moon_pendulum", moon_pendulum, lambda: bg_satin(23, (242, 236, 222), 60)),
    ("mandala_turn", mandala_turn, lambda: BLACK_BG),
    ("marching_stitch", marching_stitch, lambda: bg_linen(24)),
    ("waving_ripple", waving_ripple, lambda: BLACK_BG),
    ("bobbing_buttons", bobbing_buttons, lambda: bg_satin(25)),
]

if __name__ == "__main__":
    import gen_linen; gen_linen.OUT = OUT
    all_frames = []
    for name, fn, bgf in PIECES:
        bg = bgf(); gen_linen.export_bg(name, bg)
        frames = []
        for f in range(FRAMES):
            random.seed(1000)
            img = compose_bg(fn(f), bg); img.save(f"{OUT}/{name}_{f:02d}.png"); frames.append(img)
        open(f"{OUT}/{name}.loop", "w").write("1\n")
        all_frames.append((name, frames)); print(name)
    seq = []
    for name, fr in all_frames: seq += fr * 2
    seq[0].save(f"{OUT}/preview_loops.gif", save_all=True, append_images=seq[1:], duration=85, loop=0)
    sheet = Image.new("RGB", (W * 5 + 60, W * 4 + 50), (40, 40, 40))
    for i, (name, fr) in enumerate(all_frames):
        col = i % 5; rowb = (i // 5) * 2
        sheet.paste(fr[0], (10 + col * (W + 10), 10 + rowb * (W + 10)))
        sheet.paste(fr[FRAMES // 4], (10 + col * (W + 10), 10 + (rowb + 1) * (W + 10)))
    sheet.save(f"{OUT}/sheet_loops.png")
    print("done")
