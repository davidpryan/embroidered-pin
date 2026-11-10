#!/usr/bin/env python3
"""Animated stitching patterns for a 240x240 round display.
A needle sews each pattern live; every frame adds a few stitches.
Reuses the thread renderer from gen_insects2."""
import math, random, os
from PIL import Image, ImageDraw
import gen_insects2 as G
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, new_layer, FABRIC, CIRCLE

OUT = "/home/claude/eye_pin_lowpower/stitch"
os.makedirs(OUT, exist_ok=True)
FRAMES = 48

CREAM, GOLD, RUST, SAGE, INDIGO_T = (238, 234, 222), (226, 184, 80), (186, 96, 60), (128, 152, 96), (120, 150, 200)
RED, RED_D, PINK, LEAF, LEAF_L = (196, 44, 48), (130, 22, 30), (236, 150, 160), (96, 134, 72), (150, 184, 110)

# ------------------------------------------------------------------ stitch primitives
def stitch(L, p0, p1, col, w=1.35):
    d = ImageDraw.Draw(L)
    r = w * S / 2
    for (a, b, c, ww) in [((p0[0] + 0.45, p0[1] + 0.7), (p1[0] + 0.45, p1[1] + 0.7), (0, 0, 0, 150), w),
                          (p0, p1, shade(col, 1 + random.uniform(-0.07, 0.07)) + (255,), w)]:
        d.line([P(*a), P(*b)], fill=c, width=int(ww * S))
        for q in (a, b):
            x, y = P(*q); d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    # thread sheen
    d.line([P(p0[0] - 0.15, p0[1] - 0.3), P(p1[0] - 0.15, p1[1] - 0.3)], fill=shade(col, 1.3) + (120,), width=max(1, int(w * S * 0.3)))

def loop(L, pts, col, w=1.2):
    """Closed thread loop (chain stitch / lazy daisy petal)."""
    d = ImageDraw.Draw(L)
    sh = [P(x + 0.45, y + 0.7) for x, y in pts] + [P(pts[0][0] + 0.45, pts[0][1] + 0.7)]
    d.line(sh, fill=(0, 0, 0, 150), width=int(w * S), joint="curve")
    pp = [P(*q) for q in pts] + [P(*pts[0])]
    d.line(pp, fill=shade(col, 1 + random.uniform(-0.06, 0.06)) + (255,), width=int(w * S), joint="curve")
    d.line([(x - 0.15 * S, y - 0.3 * S) for x, y in pp], fill=shade(col, 1.3) + (110,), width=max(1, int(w * S * 0.3)), joint="curve")

def fill_circle(L, x, y, r, col=(16, 14, 14, 255)):
    ImageDraw.Draw(L).ellipse([P(x - r, y - r), P(x + r, y + r)], fill=col)

def resample(pts):
    segs = [(a[0], a[1], b[0], b[1], math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts, pts[1:])]
    segs = [s for s in segs if s[4] > 0]
    total = sum(s[4] for s in segs)
    def at(dist):
        acc = 0
        for x0, y0, x1, y1, L_ in segs:
            if acc + L_ >= dist:
                f = (dist - acc) / L_; return (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
            acc += L_
        return (segs[-1][2], segs[-1][3]) if segs else (0, 0)
    return at, total

def running(pts, col, dash=3.4, gap=1.5, w=1.35):
    """Yield stitch events along a polyline."""
    at, total = resample(pts)
    pos = 0.0
    ev = []
    while pos < total:
        a, b = at(pos), at(min(total, pos + dash))
        ev.append(("stitch", a, b, col, w))
        pos += dash + gap
    return ev

def circle_clip_line(px, py, dx, dy, R=117, cx=120, cy=120):
    """Segment of infinite line through (px,py) dir (dx,dy) inside circle, or None."""
    fx, fy = px - cx, py - cy
    a = dx * dx + dy * dy; b = 2 * (fx * dx + fy * dy); c = fx * fx + fy * fy - R * R
    disc = b * b - 4 * a * c
    if disc <= 0: return None
    s = math.sqrt(disc); t0, t1 = (-b - s) / (2 * a), (-b + s) / (2 * a)
    return (px + dx * t0, py + dy * t0), (px + dx * t1, py + dy * t1)

def inside(x, y, R=116): return math.hypot(x - 120, y - 120) < R

# ------------------------------------------------------------------ patterns -> event lists
def seigaiha():
    ev = []
    R = 24
    rows = list(range(14, 262, 12))
    for ri, cy in enumerate(rows):
        off = 0 if ri % 2 == 0 else R
        for cx in range(-R + off, 264 + R, 2 * R):
            if math.hypot(cx - 120, cy - 120) > 120 + R: continue
            ev.append(("fill", cx, cy, R))
            for k, r in enumerate((R - 2, R - 8.5, R - 15, R - 21)):
                col = GOLD if k == 3 else CREAM
                ev += running(ellipse_pts(cx, cy, r, r, 28, 0, math.pi, 2 * math.pi), col, 3.2, 1.3, 1.25)
    return ev

def asanoha():
    ev = []
    a = 30.0; h = a * math.sqrt(3) / 2
    # three families of long lines through the lattice p(i,j) = (120 + a(i + j/2), 120 + j*h)
    for fam in range(3):
        ang = math.radians(60 * fam); dx, dy = math.cos(ang), math.sin(ang)
        for k in range(-9, 10):
            px, py = (120, 120 + k * h) if fam == 0 else (120 + k * a, 120)
            seg = circle_clip_line(px, py, dx, dy)
            if seg: ev += running([seg[0], seg[1]], CREAM, 3.8, 1.6, 1.25)
    # centroid-to-vertex stitches for each triangle (the hemp leaf)
    for j in range(-6, 7):
        for i in range(-10, 10):
            p = lambda ii, jj: (120 + a * (ii + jj / 2), 120 + jj * h)
            for tri in ([p(i, j), p(i + 1, j), p(i, j + 1)], [p(i + 1, j), p(i, j + 1), p(i + 1, j + 1)]):
                gx = sum(q[0] for q in tri) / 3; gy = sum(q[1] for q in tri) / 3
                if not inside(gx, gy, 112): continue
                for v in tri:
                    ev.append(("stitch", (gx, gy), v, GOLD, 1.15))
    return ev

ROSE = [
    "...............",
    ".....DDRR......",
    "....DRRRRR.....",
    "...DRRPPRRD....",
    "...RRPPYPRR....",
    "...RRPYYYPRD...",
    "...DRRPYPRR....",
    "....DRRPRRD....",
    ".....DRRD......",
    "......GL.G.....",
    ".....GLG.LG....",
    "....GL.G.GLG...",
    ".....G.GG..G...",
    ".......G.......",
    "...............",
]
def cross_stitch():
    ev = []
    c = 8.6; ox, oy = 120 - c * 7.5, 120 - c * 7.5
    cols = {"R": RED, "D": RED_D, "P": PINK, "Y": GOLD, "G": LEAF, "L": LEAF_L}
    # faint aida grid first (a few quick guide stitches look like the fabric weave)
    for k in range(16):
        ev.append(("grid", ox + k * c, oy, ox + k * c, oy + 15 * c))
        ev.append(("grid", ox, oy + k * c, ox + 15 * c, oy + k * c))
    for ch in "DRPYGL":                      # real cross-stitch goes colour by colour
        for j, row in enumerate(ROSE):
            cells = [i for i, x in enumerate(row) if x == ch]
            if not cells: continue
            for i in cells:                  # first pass: /// left to right
                x, y = ox + i * c, oy + j * c
                ev.append(("stitch", (x + 1, y + c - 1), (x + c - 1, y + 1), cols[ch], 1.5))
            for i in reversed(cells):        # return pass: \\\ right to left
                x, y = ox + i * c, oy + j * c
                ev.append(("stitch", (x + 1, y + 1), (x + c - 1, y + c - 1), cols[ch], 1.5))
    return ev

def chain_spiral():
    ev = []
    b = 9.0 / (2 * math.pi); th = 0.8; link = 6.2
    stops = [RUST, GOLD, CREAM, SAGE, INDIGO_T, RUST]
    def colour(t):
        t = (t % 1) * (len(stops) - 1); i = int(t); f = t - i
        return tuple(int(stops[i][k] * (1 - f) + stops[i + 1][k] * f) for k in range(3))
    while True:
        r = 3 + b * th
        if r > 110: break
        x, y = 120 + r * math.cos(th), 120 + r * math.sin(th)
        dth = link / max(r, 1); nx, ny = 120 + (3 + b * (th + dth)) * math.cos(th + dth), 120 + (3 + b * (th + dth)) * math.sin(th + dth)
        ang = math.atan2(ny - y, nx - x)
        mx, my = (x + nx) / 2, (y + ny) / 2
        pts = ellipse_pts(mx, my, link / 2, 2.0, 14, ang)
        ev.append(("loop", pts, colour(th / (2 * math.pi) / 6), 1.15))
        th += dth
    # finish with a knot at the centre
    ev.append(("knot", 120, 120, 2.2, GOLD))
    return ev

def rim_daisies():
    ev = []
    R0, R1, n = 112, 101, 40
    for k in range(n + 1):                   # blanket stitch around the rim
        a0 = math.radians(-90 + 360 * k / n); a1 = math.radians(-90 + 360 * (k + 1) / n)
        p_out = (120 + R0 * math.cos(a0), 120 + R0 * math.sin(a0))
        p_in = (120 + R1 * math.cos(a0), 120 + R1 * math.sin(a0))
        p_next = (120 + R0 * math.cos(a1), 120 + R0 * math.sin(a1))
        ev.append(("stitch", p_out, p_in, GOLD, 1.3))
        if k < n: ev.append(("stitch", p_out, p_next, GOLD, 1.3))
    def daisy(cx, cy, petals, plen, pw, col, knot_col, leafy=True):
        out = []
        for i in range(petals):
            a = 2 * math.pi * i / petals - math.pi / 2
            mx, my = cx + math.cos(a) * plen / 2, cy + math.sin(a) * plen / 2
            out.append(("loop", ellipse_pts(mx, my, plen / 2, pw, 16, a), col, 1.2))
        if leafy:
            for i in range(petals):
                a = 2 * math.pi * (i + 0.5) / petals - math.pi / 2
                out.append(("stitch", (cx + math.cos(a) * plen * 0.55, cy + math.sin(a) * plen * 0.55),
                            (cx + math.cos(a) * plen * 1.05, cy + math.sin(a) * plen * 1.05), SAGE, 1.1))
        for i in range(5):
            a = 2 * math.pi * i / 5
            out.append(("knot", cx + math.cos(a) * 1.6, cy + math.sin(a) * 1.6, 1.3, knot_col))
        out.append(("knot", cx, cy, 1.4, knot_col))
        return out
    for i in range(8):
        a = 2 * math.pi * i / 8 - math.pi / 2
        ev += daisy(120 + 66 * math.cos(a), 120 + 66 * math.sin(a), 6, 13, 3.0, CREAM if i % 2 == 0 else PINK, GOLD)
    for i in range(8):                       # small seed stitches between the ring flowers
        a = 2 * math.pi * (i + 0.5) / 8 - math.pi / 2
        for r in (56, 64, 72):
            ev.append(("stitch", (120 + r * math.cos(a) - 1.5, 120 + r * math.sin(a)), (120 + r * math.cos(a) + 1.5, 120 + r * math.sin(a)), GOLD, 1.0))
    ev += daisy(120, 120, 10, 22, 4.2, CREAM, RUST)
    return ev

PATTERNS = {
    "seigaiha_waves": seigaiha,
    "asanoha_lattice": asanoha,
    "cross_stitch_rose": cross_stitch,
    "chain_spiral": chain_spiral,
    "rim_daisies": rim_daisies,
}

# ------------------------------------------------------------------ event execution
def run_event(L, e):
    """Draw one event; return (needle position, direction, thread colour)."""
    k = e[0]
    if k == "stitch":
        _, a, b, col, w = e; stitch(L, a, b, col, w)
        return b, (b[0] - a[0], b[1] - a[1]), col
    if k == "loop":
        _, pts, col, w = e; loop(L, pts, col, w)
        return pts[len(pts) // 2], (pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]), col
    if k == "knot":
        _, x, y, r, col = e; knot(L, x, y, r, col); return (x, y), (1, 0), col
    if k == "fill":
        _, x, y, r = e; fill_circle(L, x, y, r); return None
    if k == "grid":
        _, x0, y0, x1, y1 = e
        ImageDraw.Draw(L).line([P(x0, y0), P(x1, y1)], fill=(60, 56, 52, 120), width=max(1, S // 2))
        return None
    return None

def needle(L, pos, dirv, col):
    """Silver needle ahead of the last stitch, thread trailing back to it."""
    if pos is None: return
    d = ImageDraw.Draw(L)
    dx, dy = dirv; ln = math.hypot(dx, dy) or 1; dx, dy = dx / ln, dy / ln
    ex, ey = pos[0] + dx * 3, pos[1] + dy * 3          # eye end, just past the stitch
    tx, ty = ex + dx * 16, ey + dy * 16                # tip
    # thread from stitch end up through the eye
    d.line([P(*pos), P(pos[0] + dx * 1.5 - dy * 2.5, pos[1] + dy * 1.5 + dx * 2.5), P(ex, ey)], fill=col + (255,), width=int(1.1 * S), joint="curve")
    d.line([P(ex + 0.4, ey + 0.8), P(tx + 0.4, ty + 0.8)], fill=(0, 0, 0, 170), width=int(1.6 * S))
    d.line([P(ex, ey), P(tx, ty)], fill=(196, 200, 206, 255), width=int(1.5 * S))
    d.line([P(ex, ey), P(tx, ty)], fill=(240, 242, 246, 255), width=int(0.5 * S))
    nx, ny = -dy, dx
    d.ellipse([P(ex - 1.2, ey - 1.2), P(ex + 1.2, ey + 1.2)], outline=(150, 154, 160, 255), width=int(0.5 * S))

FLAT = Image.new("RGB", (N, N), (12, 10, 10))
def compose(layer):
    out = FLAT.copy(); out.paste(layer, (0, 0), layer)
    out = out.resize((W, W), Image.LANCZOS)
    return Image.composite(out, Image.new("RGB", (W, W), (0, 0, 0)), CIRCLE)

if __name__ == "__main__":
    gif = []
    stills = []
    for name, make in PATTERNS.items():
        random.seed(hash(name) & 0xffff)
        ev = make()
        L = new_layer()
        done = 0; last = None
        frames = []
        for f in range(FRAMES):
            # ease-in-out so the sewing starts slow and finishes slow
            t = (f + 1) / FRAMES; t = 0.5 - 0.5 * math.cos(t * math.pi)
            target = int(len(ev) * t)
            while done < target:
                r = run_event(L, ev[done]); done += 1
                if r: last = r
            frame_layer = L.copy()
            if f < FRAMES - 1 and last: needle(frame_layer, *last)
            img = compose(frame_layer)
            img.save(f"{OUT}/{name}_{f:02d}.png")
            frames.append(img)
        stills.append(frames[-1])
        gif += frames + [frames[-1]] * 14
        print(name, len(ev), "stitches")
    # crossfade between the finished pieces when the loop wraps
    seq = []
    per = FRAMES + 14
    for i in range(len(stills)):
        seq += gif[i * per:(i + 1) * per]
        nxt = stills[(i + 1) % len(stills)]
        seq += [Image.blend(stills[i], nxt, j / 6) for j in range(1, 6)]
    seq[0].save(f"{OUT}/preview_stitch.gif", save_all=True, append_images=seq[1:], duration=90, loop=0)
    sheet = Image.new("RGB", (W * 5 + 60, W + 20), (40, 40, 40))
    for i, im in enumerate(stills): sheet.paste(im, (10 + i * (W + 10), 10))
    sheet.save(f"{OUT}/sheet_stitch.png")
    # mid-sew contact sheet so the needle is visible
    mid = Image.new("RGB", (W * 5 + 60, W + 20), (40, 40, 40))
    for i, name in enumerate(PATTERNS):
        mid.paste(Image.open(f"{OUT}/{name}_{FRAMES // 2:02d}.png"), (10 + i * (W + 10), 10))
    mid.save(f"{OUT}/sheet_midsew.png")
    print("done")
