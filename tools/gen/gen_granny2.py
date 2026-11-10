#!/usr/bin/env python3
"""Ten more patchwork / Burton / granny pieces, 48 frames each."""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, ellipse_mask, poly_mask, rect_mask, new_layer, satin, backstitch, sm
from gen_stitch import stitch, loop, needle, compose, resample
from gen_granny import yarn, post, hook, MUSTARD, OXBLOOD, TEAL, CREAM, SOOT, PLUM, RUST, SAGE, PALETTE

OUT = "/home/claude/eye_pin_lowpower/granny2"
os.makedirs(OUT, exist_ok=True)
FRAMES = 48
CHAR, BONE = (112, 104, 112), (236, 226, 204)

# ------------------------------------------------------------------ generic helpers
def circle_mask(r=120): return ellipse_mask(120, 120, r, r)

def chord(px, py, dx, dy, R, cx=120, cy=120):
    fx, fy = px - cx, py - cy
    a = dx * dx + dy * dy; b = 2 * (fx * dx + fy * dy); c = fx * fx + fy * fy - R * R
    disc = b * b - 4 * a * c
    if disc <= 0: return None
    s = math.sqrt(disc); t0, t1 = (-b - s) / (2 * a), (-b + s) / (2 * a)
    return (px + dx * t0, py + dy * t0), (px + dx * t1, py + dy * t1)

def clip_poly(poly, px, py, nx, ny):
    """Keep the side of line (through p, normal n) where dot >= 0."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da = (a[0] - px) * nx + (a[1] - py) * ny; db = (b[0] - px) * nx + (b[1] - py) * ny
        if da >= 0: out.append(a)
        if (da >= 0) != (db >= 0):
            t = da / (da - db); out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out

def poly_rounds(sides, rounds, step=13, inner0=10, palette=PALETTE, cx=120, cy=120, skew=0.0, wobble=0.0):
    """Granny polygon (hexagon etc.) built round by round, as yarn events."""
    ev = [("ring", (cx, cy), inner0 * 0.55, palette[0])]
    half = math.pi / sides
    for n in range(1, rounds + 1):
        col = palette[n % len(palette)]
        hi = inner0 + step * (n - 1); ho = hi + step - 2
        hs = hi * math.tan(half)
        per = max(1, int(round(2 * hs / 11.5)))
        for side in range(sides):
            a = math.radians(360 / sides * side + skew); ca, sa = math.cos(a), math.sin(a)
            def T(x, y, ca=ca, sa=sa): return (cx + x * ca - y * sa, cy + x * sa + y * ca)
            xs = [-hs + 2 * hs * (k + 0.5) / per for k in range(per)]
            for k, x in enumerate(xs):
                jx = random.uniform(-wobble, wobble)
                base = T(x + jx, -hi + 1)
                for o in (-3.6, 0, 3.6): ev.append(("yarn", post(base, T(x + jx + o, -ho)), col, 3.0))
                if k < per - 1:
                    ev.append(("yarn", [T(x + 3.6, -ho), T((x + xs[k + 1]) / 2, -ho - 1.5), T(xs[k + 1] - 3.6, -ho)], col, 2.4))
            a2 = math.radians(360 / sides * (side + 1) + skew); ca2, sa2 = math.cos(a2), math.sin(a2)
            p1 = T(xs[-1] + 3.6, -ho)
            cr = ho / math.cos(half) + 1.5; ang_c = a + half - math.pi / 2
            c = (cx + cr * math.cos(ang_c), cy + cr * math.sin(ang_c))
            p2 = (cx + (xs[0] - 3.6) * ca2 - (-ho) * sa2, cy + (xs[0] - 3.6) * sa2 + (-ho) * ca2)
            ev.append(("yarn", [p1, c, p2], col, 2.4))
    return ev

# ------------------------------------------------------------------ event pieces
def piece_hexagon():
    return poly_rounds(6, 6, palette=[MUSTARD, PLUM, TEAL, CREAM, OXBLOOD, SAGE, MUSTARD], skew=random.uniform(-6, 6))

def piece_burton_spiral():
    ev = []
    b = 11.5 / (2 * math.pi)
    for which, col, off in ((0, CHAR, 0.0), (1, BONE, math.pi)):
        th = 0.3; pts = []
        while True:
            r = 2 + b * (th + off) + 0.8 * math.sin(th * 3.1)
            if r > 116: break
            pts.append((120 + r * math.cos(th), 120 + r * math.sin(th)))
            th += 7.0 / max(r, 4)
        # interleave the two spirals so they grow together
        for i in range(0, len(pts) - 1, 2):
            ev.append((which, ("yarn", pts[i:i + 3], col, 5.2)))
    ev.sort(key=lambda e: 0)  # stable
    # merge alternately by progress
    a = [e[1] for e in ev if e[0] == 0]; bb = [e[1] for e in ev if e[0] == 1]
    out = []
    for i in range(max(len(a), len(bb))):
        if i < len(a): out.append(a[i])
        if i < len(bb): out.append(bb[i])
    return out

def piece_ragdoll_seam():
    ev = [("satin", circle_mask(121), (166, 172, 158), 90, 1.6)]
    seam = sm([(26, 104), (56, 124), (92, 138), (128, 136), (164, 128), (196, 112), (214, 96)], 2)
    ev.append(("path", seam, SOOT, 2.4))
    at, total = resample(seam)
    n = int(total / 14)
    for k in range(n):
        t = total * (k + 0.5) / n; p = at(t); q = at(min(total, t + 1))
        dx, dy = q[0] - p[0], q[1] - p[1]; L_ = math.hypot(dx, dy) or 1; dx, dy = dx / L_, dy / L_; nx, ny = -dy, dx
        col = [OXBLOOD, OXBLOOD, OXBLOOD, MUSTARD, OXBLOOD, TEAL][k % 6]
        w = random.uniform(-2, 2); s = random.uniform(9, 12)
        ev.append(("stitch", (p[0] - dx * 5 + nx * s + w, p[1] - dy * 5 + ny * s), (p[0] + dx * 5 - nx * s, p[1] + dy * 5 - ny * s + w), col, 2.6))
        ev.append(("stitch", (p[0] + dx * 5 + nx * s, p[1] + dy * 5 + ny * s + w), (p[0] - dx * 5 - nx * s + w, p[1] - dy * 5 - ny * s), col, 2.6))
    # a small patch sewn over a worn spot
    patch = sm([(60, 150), (104, 146), (108, 190), (64, 196)], 1)
    ev.append(("satin", poly_mask(patch), OXBLOOD, 40, 1.5))
    at2, tot2 = resample(patch + [patch[0]]); pos = 0
    while pos < tot2:
        ev.append(("stitch", at2(pos), at2(min(tot2, pos + 3.5)), CREAM, 1.4)); pos += 6
    return ev

def piece_crazy_quilt():
    ev = []
    cells = [[(-10, -10), (250, -10), (250, 250), (-10, 250)]]
    seams = []
    for depth in range(3):
        nxt = []
        for poly in cells:
            cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
            ang = random.uniform(0, math.pi); nx, ny = math.cos(ang), math.sin(ang)
            px, py = cx + random.uniform(-15, 15), cy + random.uniform(-15, 15)
            A = clip_poly(poly, px, py, nx, ny); B = clip_poly(poly, px, py, -nx, -ny)
            if len(A) >= 3 and len(B) >= 3:
                nxt += [A, B]; seams.append((px, py, -ny, nx))
            else: nxt.append(poly)
        cells = nxt
    pal = [MUSTARD, OXBLOOD, TEAL, CREAM, PLUM, RUST, SAGE, (196, 186, 160)]
    random.shuffle(pal)
    circ = circle_mask(121)
    for i, poly in enumerate(cells):
        ev.append(("satin", ImageChops.multiply(poly_mask(poly), circ), pal[i % len(pal)], random.uniform(0, 180), 1.5))
    # herringbone embroidery along every seam
    for (px, py, dx, dy) in seams:
        seg = chord(px, py, dx, dy, 118)
        if not seg: continue
        at, total = resample([seg[0], seg[1]]); pos = 0; side = 1
        col = random.choice([CREAM, SOOT, MUSTARD])
        while pos + 7 < total:
            a = at(pos); b = at(pos + 7)
            nx, ny = -dy, dx
            ev.append(("stitch", (a[0] + nx * 4 * side, a[1] + ny * 4 * side), (b[0] - nx * 4 * side, b[1] - ny * 4 * side), col, 1.3))
            pos += 7; side = -side
    return ev

def piece_darning():
    ev = [("satin", circle_mask(121), PLUM, 0, 1.9)]
    hole = sm([(78, 96), (120, 82), (160, 100), (168, 138), (134, 162), (90, 156), (72, 124)], 2)
    ev.append(("fillpoly", hole, (10, 8, 10)))
    xs = list(range(68, 176, 5)); ys = list(range(78, 170, 5))
    for i, x in enumerate(xs):                       # warp
        ev.append(("yarn", [(x + random.uniform(-0.5, 0.5), 74), (x, 172)], MUSTARD if i % 4 else RUST, 2.2))
    for j, y in enumerate(ys):                       # weft, woven over/under
        ev.append(("yarn", [(64, y), (180, y + random.uniform(-0.5, 0.5))], TEAL if j % 5 else CREAM, 2.2))
        overs = [("yarn", [(x, y - 2.6), (x, y + 2.6)], MUSTARD if i % 4 else RUST, 2.2) for i, x in enumerate(xs) if (i + j) % 2 == 0]
        ev.append(("multi", overs))
    return ev

def piece_spiderweb():
    ev = []
    cx, cy = 120, 120; spokes = 9; web = (214, 208, 192)
    for k in range(spokes):
        a = 2 * math.pi * k / spokes - math.pi / 2 + random.uniform(-0.08, 0.08)
        ev.append(("yarn", [(cx, cy), (cx + 124 * math.cos(a), cy + 124 * math.sin(a))], web, 1.5))
    r = 10
    angles = [2 * math.pi * k / spokes - math.pi / 2 for k in range(spokes)]
    k = 0
    while r < 118:
        a0 = angles[k % spokes]; a1 = angles[(k + 1) % spokes]
        r1 = r + 9.5 / spokes
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0)); p1 = (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1))
        mid = (a0 + a1) / 2 if k % spokes != spokes - 1 else a0 + math.pi / spokes
        sag = (r + r1) / 2 - 2.5 - r * 0.03
        ev.append(("yarn", [p0, (cx + sag * math.cos(mid), cy + sag * math.sin(mid)), p1], web, 1.4))
        r = r1; k += 1
    # spider dropping on a thread
    ev.append(("yarn", [(168, 0), (168, 60)], web, 1.2))
    ev.append(("knot", 168, 66, 5.5, SOOT)); ev.append(("knot", 168, 56, 3.5, SOOT))
    for s in (-1, 1):
        for (ex, ey) in ((16, -10), (18, -2), (17, 7), (13, 14)):
            ev.append(("yarn", [(168 + s * 4, 64), (168 + s * ex * 0.6, 64 + ey * 0.5), (168 + s * ex, 66 + ey)], SOOT, 1.4))
    ev.append(("knot", 166, 54, 1.0, OXBLOOD)); ev.append(("knot", 170, 54, 1.0, OXBLOOD))
    return ev

def piece_button_jar():
    ev = []
    placed = []
    tries = 0
    while len(placed) < 15 and tries < 4000:
        tries += 1
        r = random.uniform(7, 17); x = random.uniform(30, 210); y = random.uniform(30, 210)
        if math.hypot(x - 120, y - 120) + r > 112: continue
        if any(math.hypot(x - px, y - py) < r + pr + 3 for px, py, pr in placed): continue
        placed.append((x, y, r))
    for (x, y, r) in placed:
        col = random.choice([MUSTARD, OXBLOOD, TEAL, CREAM, PLUM, RUST, SAGE, CHAR, (200, 190, 170)])
        thr = random.choice([c for c in [MUSTARD, OXBLOOD, TEAL, CREAM, SOOT] if c != col])
        four = r > 10 and random.random() < 0.7
        ev.append(("satin", ellipse_mask(x, y, r, r), col, random.uniform(0, 180), 1.3))
        ev.append(("satin", ellipse_mask(x, y, r * 0.78, r * 0.78), shade(col, 0.85), random.uniform(0, 180), 1.3))
        ev.append(("ring", (x, y), r * 0.78, shade(col, 1.25) if sum(col) < 400 else shade(col, 0.7)))
        hr = r * 0.11 + 0.8
        if four:
            hs = r * 0.26
            holes = [(x - hs, y - hs), (x + hs, y - hs), (x + hs, y + hs), (x - hs, y + hs)]
            ev.append(("holes", holes, hr))
            if random.random() < 0.5:
                ev.append(("yarn", [holes[0], holes[2]], thr, 2.0)); ev.append(("yarn", [holes[1], holes[3]], thr, 2.0))
            else:
                ev.append(("yarn", [holes[0], holes[1]], thr, 2.0)); ev.append(("yarn", [holes[3], holes[2]], thr, 2.0))
        else:
            hs = r * 0.3
            holes = [(x - hs, y), (x + hs, y)]
            ev.append(("holes", holes, hr))
            ev.append(("yarn", [holes[0], holes[1]], thr, 2.0))
            if random.random() < 0.5: ev.append(("yarn", [(holes[0][0], holes[0][1] + 1.5), (holes[1][0], holes[1][1] - 1.5)], thr, 1.8))
    return ev

def piece_ripple():
    ev = []
    period, amp = 52, 15
    cols = [MUSTARD, CREAM, OXBLOOD, TEAL, CREAM, PLUM, SAGE, CREAM]
    row = 0
    for y in range(-30, 262, 8):
        col = cols[row % len(cols)]; row += 1
        pts = [(x, y + amp * (1 if (x // (period // 2)) % 2 else -1)) for x in range(-26, 270, period // 2)]
        # straight zig segments, drawn one by one left->right
        for a, b in zip(pts, pts[1:]):
            ev.append(("yarn", [a, b], col, 4.6))
    return ev

# ------------------------------------------------------------------ draw-based pieces
def draw_yarn_ball(frame):
    L = new_layer(); random.seed(21)
    t = frame / (FRAMES - 1)
    cx, cy = 104, 128; R = 48 - 10 * t
    # wound strands: three wrap directions, chords across the ball
    for ang_base, n in ((20, 14), (75, 14), (130, 12)):
        for i in range(n):
            ang = math.radians(ang_base + random.uniform(-6, 6)); dx, dy = math.cos(ang), math.sin(ang)
            off = random.uniform(-R * 0.9, R * 0.9)
            seg = chord(cx - dy * off, cy + dx * off, dx, dy, R - 1.5, cx, cy)
            if seg: yarn(L, [seg[0], ((seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2), seg[1]], shade(OXBLOOD, random.uniform(0.85, 1.15)), 3.2)
    # ball shading
    sh = ellipse_mask(cx, cy, R, R)
    dark = new_layer(); d = ImageDraw.Draw(dark)
    d.ellipse([P(cx - R, cy - R), P(cx + R, cy + R)], fill=(0, 0, 0, 110))
    d.ellipse([P(cx - R * 0.9, cy - R * 1.05), P(cx + R * 0.7, cy + R * 0.55)], fill=(0, 0, 0, 0))
    L.paste(dark, (0, 0), ImageChops.multiply(sh, dark.split()[3]))
    # the unwinding tail: a wandering path, revealed with time
    tail = sm([(cx + R - 2, cy - 6), (cx + R + 14, cy - 20), (190, 96), (206, 130), (184, 160), (150, 176), (128, 196), (150, 214), (180, 206), (196, 186)], 2)
    at, total = resample(tail)
    reveal = total * (0.08 + 0.92 * t)
    pts = [at(s) for s in np.linspace(0, reveal, max(2, int(reveal / 3)))]
    yarn(L, pts, OXBLOOD, 3.0)
    if frame < FRAMES - 1:
        p = pts[-1]; q = pts[-2]
        hook(L, p, (p[0] - q[0], p[1] - q[1]), OXBLOOD)
    return L

def heart_pts(cx, cy, s, n=80):
    out = []
    for i in range(n):
        th = 2 * math.pi * i / n
        x = 16 * math.sin(th) ** 3; y = -(13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th))
        out.append((cx + x * s, cy + y * s + 2 * s))
    return out

def draw_patched_heart(frame):
    L = new_layer(); random.seed(5)
    pulse = 1.0
    if frame >= 30:
        ph = (frame - 30) / 18 * 2 * math.pi * 2
        pulse = 1.0 + 0.05 * max(0, math.sin(ph)) ** 2
    s = 4.6 * pulse
    hp = heart_pts(120, 118, s)
    hm = poly_mask(hp)
    # zigzag seam splitting it into two scraps, slightly off-centre (lopsided, Burton)
    zz = [(124 + (8 if i % 2 else -8) * (s / 4.6), -20 + i * 14) for i in range(22)]
    left = poly_mask(zz + [(-20, 300), (-20, -20)])
    satin(L, ImageChops.multiply(hm, left), OXBLOOD, 30, spacing=1.5, sheen=0.3)
    right_m = ImageChops.subtract(hm, left)
    satin(L, right_m, (176, 170, 150), -40, spacing=1.5, sheen=0.25)
    chk = new_layer(); d = ImageDraw.Draw(chk)
    for k in range(0, 240, 9):
        d.line([P(k, 0), P(k, 240)], fill=TEAL + (130,), width=int(0.9 * S)); d.line([P(0, k), P(240, k)], fill=TEAL + (130,), width=int(0.9 * S))
    L.paste(chk, (0, 0), ImageChops.multiply(right_m, chk.split()[3]))
    # progressive: seam cross-stitches (0-20), whip outline (14-30)
    prog_seam = min(1.0, frame / 20); prog_out = max(0.0, min(1.0, (frame - 12) / 18))
    inside = [p for p in zz if 0 <= p[0] < 240 and 0 <= p[1] < 240 and hm.getpixel((int(p[0] * S), int(p[1] * S))) > 0]
    for i, p in enumerate(inside[:int(len(inside) * prog_seam)]):
        stitch(L, (p[0] - 5, p[1] - 4), (p[0] + 5, p[1] + 4), SOOT, 2.0); stitch(L, (p[0] - 5, p[1] + 4), (p[0] + 5, p[1] - 4), SOOT, 2.0)
    seam_line = [p for p in zz if -10 < p[1] < 250]
    for a, b in zip(inside, inside[1:]):
        backstitch(L, [a, b], SOOT, width=0.9, dash=2.0, gap=1.0)
    at, total = resample(hp + [hp[0]])
    n = 56
    for k in range(int(n * prog_out)):
        t = total * k / n; a = at(t); b = at(min(total, t + 2))
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) or 1; nx, ny = -dy / ln, dx / ln
        stitch(L, (a[0] + nx * 3.5 - dx / ln * 2, a[1] + ny * 3.5 - dy / ln * 2), (a[0] - nx * 3.5 + dx / ln * 2, a[1] - ny * 3.5 + dy / ln * 2), CREAM, 1.6)
    # a little square patch on the left lobe
    patch = sm([(84, 92), (104, 88), (108, 108), (86, 112)], 1)
    satin(L, poly_mask(patch), MUSTARD, 60, spacing=1.4, sheen=0.3)
    at2, t2 = resample(patch + [patch[0]]); pos = 0
    while pos < t2: stitch(L, at2(pos), at2(min(t2, pos + 3)), SOOT, 1.2); pos += 5
    return L

# ------------------------------------------------------------------ runner
def run_event(L, e):
    k = e[0]
    if k == "yarn":
        _, pts, col, w = e; yarn(L, pts, col, w); return pts[-1], (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]), col
    if k == "ring":
        _, (x, y), r, col = e; yarn(L, ellipse_pts(x, y, r, r, 28), col, 1.6 if r > 8 else 3.0); return (x + r, y), (0, -1), col
    if k == "stitch":
        _, a, b, col, w = e; stitch(L, a, b, col, w); return b, (b[0] - a[0], b[1] - a[1]), col
    if k == "satin":
        _, m, col, ang, sp = e; satin(L, m, col, ang, spacing=sp, sheen=0.25); return None
    if k == "path":
        _, pts, col, w = e; backstitch(L, pts, col, width=w, dash=3.0, gap=1.2); return pts[-1], (1, 0), col
    if k == "fillpoly":
        _, pts, col = e; ImageDraw.Draw(L).polygon([P(*p) for p in pts], fill=col + (255,)); return None
    if k == "knot":
        _, x, y, r, col = e; knot(L, x, y, r, col); return (x, y), (1, 0), col
    if k == "holes":
        _, holes, hr = e; d = ImageDraw.Draw(L)
        for (x, y) in holes: d.ellipse([P(x - hr, y - hr), P(x + hr, y + hr)], fill=(8, 8, 10, 255))
        return None
    if k == "multi":
        last = None
        for sub in e[1]:
            r = run_event(L, sub)
            if r: last = r
        return last
    return None

def render_events(name, ev, tool="hook"):
    L = new_layer(); done = 0; last = None; frames = []
    for f in range(FRAMES):
        t = (f + 1) / FRAMES; t = 0.5 - 0.5 * math.cos(t * math.pi)
        target = int(len(ev) * t)
        while done < target:
            r = run_event(L, ev[done]); done += 1
            if r: last = r
        fl = L.copy()
        if f < FRAMES - 1 and last: (hook if tool == "hook" else needle)(fl, *last)
        img = compose(fl); img.save(f"{OUT}/{name}_{f:02d}.png"); frames.append(img)
    return frames

def render_draw(name, fn):
    frames = []
    for f in range(FRAMES):
        img = compose(fn(f)); img.save(f"{OUT}/{name}_{f:02d}.png"); frames.append(img)
    return frames

if __name__ == "__main__":
    pieces = []
    for seed, (name, fn, tool) in enumerate([
        ("granny_hexagon", piece_hexagon, "hook"),
        ("burton_spiral", piece_burton_spiral, "hook"),
        ("ragdoll_seam", piece_ragdoll_seam, "needle"),
        ("crazy_quilt", piece_crazy_quilt, "needle"),
        ("darning_patch", piece_darning, "needle"),
        ("spiderweb", piece_spiderweb, "hook"),
        ("button_jar", piece_button_jar, "needle"),
        ("ripple_blanket", piece_ripple, "hook"),
    ]):
        random.seed(100 + seed)
        pieces.append((name, render_events(name, fn(), tool))); print(name)
    pieces.append(("yarn_ball", render_draw("yarn_ball", draw_yarn_ball))); print("yarn_ball")
    pieces.append(("patched_heart", render_draw("patched_heart", draw_patched_heart))); print("patched_heart")
    seq = []
    for i, (name, fr) in enumerate(pieces):
        seq += fr + [fr[-1]] * 12
        nxt = pieces[(i + 1) % len(pieces)][1][0]
        seq += [Image.blend(fr[-1], nxt, j / 6) for j in range(1, 6)]
    seq[0].save(f"{OUT}/preview_granny2.gif", save_all=True, append_images=seq[1:], duration=90, loop=0)
    sheet = Image.new("RGB", (W * 5 + 60, W * 4 + 50), (40, 40, 40))
    for i, (name, fr) in enumerate(pieces):
        col = i % 5; rowb = (i // 5) * 2
        sheet.paste(fr[FRAMES // 2], (10 + col * (W + 10), 10 + rowb * (W + 10)))
        sheet.paste(fr[-1], (10 + col * (W + 10), 10 + (rowb + 1) * (W + 10)))
    sheet.save(f"{OUT}/sheet_granny2.png")
    print("done")
