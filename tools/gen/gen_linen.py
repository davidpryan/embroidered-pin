#!/usr/bin/env python3
"""Ten pieces, several on off-white embroidered grounds (linen / cream satin / aida).
Exports <name>_bg.png (static ground) + <name>_NN.png frames for delta packaging."""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, ellipse_mask, poly_mask, rect_mask, new_layer, satin, backstitch, sm, leaf, daisy
from gen_stitch import stitch, loop, needle, resample
from gen_granny import yarn, post, hook, square_rounds, MUSTARD, OXBLOOD, TEAL, CREAM, SOOT, PLUM, RUST, SAGE, PALETTE
import gen_granny2 as G2

OUT = "/home/claude/eye_pin_lowpower/linen"
os.makedirs(OUT, exist_ok=True)
FRAMES = 48
LINEN = (232, 224, 204)
CIRCLE = Image.new("L", (W, W), 0); ImageDraw.Draw(CIRCLE).ellipse([0, 0, W - 1, W - 1], fill=255)

# ------------------------------------------------------------------ grounds
def bg_linen(seed=3, base=LINEN):
    rng = np.random.default_rng(seed)
    b = np.array(base, dtype=float)
    rows = rng.normal(0, 4.5, (N, 1, 1)); cols = rng.normal(0, 4.5, (1, N, 1))
    weave = ((np.indices((N, N)).sum(axis=0) // S) % 2) * 2.5
    img = b + rows + cols + weave[..., None] + rng.normal(0, 2, (N, N, 1))
    yy, xx = np.mgrid[0:N, 0:N]; r = np.hypot(xx - N / 2, yy - N / 2) / (N / 2)
    img *= (1 - 0.10 * np.clip(r, 0, 1) ** 2.5)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")

def bg_satin(seed=4, col=(240, 234, 218), angle=90):
    random.seed(seed)
    base = Image.new("RGB", (N, N), (222, 214, 196))
    L = new_layer()
    satin(L, ellipse_mask(120, 120, 124, 124), col, angle, spacing=1.6, sheen=0.18, shadow=False, var=0.05)
    base.paste(L, (0, 0), L)
    return base

def bg_aida(seed=5):
    img = bg_linen(seed, (236, 229, 210))
    d = ImageDraw.Draw(img)
    for k in range(0, 240, 8):
        d.line([P(k, 0), P(k, 240)], fill=(214, 205, 184), width=max(1, S // 2))
        d.line([P(0, k), P(240, k)], fill=(214, 205, 184), width=max(1, S // 2))
    for x in range(0, 240, 8):
        for y in range(0, 240, 8):
            d.ellipse([P(x - 0.8, y - 0.8), P(x + 0.8, y + 0.8)], fill=(206, 196, 174))
    return img

BLACK_BG = Image.new("RGB", (N, N), (12, 10, 10))

def compose_bg(layer, bg):
    out = bg.copy(); out.paste(layer, (0, 0), layer)
    out = out.resize((W, W), Image.LANCZOS)
    return Image.composite(out, Image.new("RGB", (W, W), (0, 0, 0)), CIRCLE)

def export_bg(name, bg):
    img = bg.resize((W, W), Image.LANCZOS)
    Image.composite(img, Image.new("RGB", (W, W), (0, 0, 0)), CIRCLE).save(f"{OUT}/{name}_bg.png")

# ------------------------------------------------------------------ event helpers
def path_events(pts, col, w=1.3, step=7.0):
    at, total = resample(pts); ev = []; pos = 0.0
    while pos < total:
        a, b = at(pos), at(min(total, pos + step))
        ev.append(("stitch", a, b, col, w)); pos += step * 0.92
    return ev

def cross(x, y, c, col, w=1.5):
    return [("stitch", (x + 1, y + c - 1), (x + c - 1, y + 1), col, w), ("stitch", (x + 1, y + 1), (x + c - 1, y + c - 1), col, w)]

def run_event(L, e):
    if e[0] == "fn":
        _, fn, endpt, col = e; fn(L); return endpt, (1, 0), col
    return G2.run_event(L, e)

def render_events(name, ev, bg, tool="needle"):
    L = new_layer(); done = 0; last = None; frames = []
    export_bg(name, bg)
    for f in range(FRAMES):
        t = (f + 1) / FRAMES; t = 0.5 - 0.5 * math.cos(t * math.pi)
        target = int(len(ev) * t)
        while done < target:
            r = run_event(L, ev[done]); done += 1
            if r: last = r
        fl = L.copy()
        if f < FRAMES - 1 and last: (hook if tool == "hook" else needle)(fl, *last)
        img = compose_bg(fl, bg); img.save(f"{OUT}/{name}_{f:02d}.png"); frames.append(img)
    return frames

def render_draw(name, fn, bg):
    export_bg(name, bg); frames = []
    for f in range(FRAMES):
        img = compose_bg(fn(f), bg); img.save(f"{OUT}/{name}_{f:02d}.png"); frames.append(img)
    return frames

# ------------------------------------------------------------------ pieces
def piece_sampler():
    ev = []; c = 8
    # border of crosses around a 22x22-cell square
    x0 = y0 = 120 - 11 * c
    cells = [(x0 + i * c, y0) for i in range(22)] + [(x0 + 21 * c, y0 + j * c) for j in range(1, 22)] + \
            [(x0 + i * c, y0 + 21 * c) for i in range(20, -1, -1)] + [(x0, y0 + j * c) for j in range(20, 0, -1)]
    for i, (x, y) in enumerate(cells): ev += cross(x, y, c, OXBLOOD if i % 7 else MUSTARD)
    # house
    H = ["....R....", "...RRR...", "..RRRRR..", ".RRRRRRR.", "..MMMMM..", "..MTMTM..", "..MMMMM..", "..MMSMM..", "..MMSMM.."]
    cols = {"R": OXBLOOD, "M": MUSTARD, "T": TEAL, "S": SOOT}
    for j, row in enumerate(H):
        for i, ch in enumerate(row):
            if ch != ".": ev += cross(120 - 4.5 * c + i * c, 96 + j * c, c, cols[ch])
    # trees either side
    T = ["..G..", ".GGG.", "GGGGG", ".GGG.", "GGGGG", "..S..", "..S.."]
    for tx in (120 - 11 * c, 120 + 6 * c):
        for j, row in enumerate(T):
            for i, ch in enumerate(row):
                if ch != ".": ev += cross(tx + i * c, 112 + j * c, c, SAGE if ch == "G" else SOOT)
    # row of hearts above
    for hx in range(120 - 8 * c, 120 + 8 * c, 4 * c):
        for (i, j) in [(0, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (1, 3)]:
            ev += cross(hx + i * c, 56 + j * c, c, OXBLOOD)
    # flowers below
    for fx in range(120 - 9 * c, 120 + 9 * c, 3 * c):
        ev += cross(fx, 176, c, MUSTARD); ev += cross(fx - c, 176, c, OXBLOOD); ev += cross(fx + c, 176, c, OXBLOOD)
        ev += cross(fx, 168, c, OXBLOOD); ev += cross(fx, 184, c, SAGE)
    return ev

def piece_redwork_bird():
    ev = []
    body = ellipse_pts(116, 126, 36, 22, 60, math.radians(-14), math.radians(20), math.radians(340))
    ev += path_events(body, OXBLOOD, 1.4)
    head = ellipse_pts(152, 100, 14, 13, 40, 0, math.radians(120), math.radians(400))
    ev += path_events(head, OXBLOOD, 1.4)
    ev += path_events([(165, 98), (178, 102), (165, 106)], OXBLOOD, 1.3)                 # beak
    ev.append(("knot", 156, 96, 2.2, OXBLOOD))                                            # eye
    ev += path_events(sm([(84, 118), (60, 136), (54, 152), (72, 142), (84, 134)], 1), OXBLOOD, 1.4)   # tail
    ev += path_events([(60, 136), (78, 136)], OXBLOOD, 1.0); ev += path_events([(56, 146), (76, 141)], OXBLOOD, 1.0)
    wing = sm([(104, 112), (120, 104), (140, 112), (138, 128), (120, 136), (104, 128)], 2)
    ev += path_events(wing + [wing[0]], OXBLOOD, 1.2)
    for k in range(3): ev += path_events([(108 + k * 10, 130 - k * 2), (122 + k * 8, 118 - k * 3)], OXBLOOD, 0.9)   # feathers
    for lx in (112, 128): ev += path_events([(lx, 146), (lx + 2, 162), (lx - 6, 166)], OXBLOOD, 1.2); ev += path_events([(lx + 2, 162), (lx + 8, 166)], OXBLOOD, 1.0)
    branch = sm([(20, 176), (60, 168), (100, 166), (140, 170), (180, 164), (220, 160)], 2)
    ev += path_events(branch, OXBLOOD, 1.6)
    for (bx, by, d) in [(52, 170, -1), (90, 167, 1), (150, 168, -1), (190, 163, 1)]:
        lf = ellipse_pts(bx + 6, by + d * 9, 9, 4, 20, math.radians(-50 * d))
        ev += path_events(lf + [lf[0]], OXBLOOD, 1.1); ev += path_events([(bx, by), (bx + 6, by + d * 9)], OXBLOOD, 0.9)
    return ev

def piece_blackwork():
    ev = []; sp = 22
    for sgn in (1, -1):
        for k in range(-7, 8):
            dx, dy = math.sqrt(0.5), sgn * math.sqrt(0.5)
            px, py = 120 + k * sp * math.sqrt(2) * dx * (1 if sgn == 1 else 1), 120 - k * sp * math.sqrt(2) * dy
            seg = G2.chord(px, py, dx, dy, 118)
            if seg: ev += path_events([seg[0], seg[1]], SOOT, 1.1, 6.0)
    # inner motif in each diamond: a small plus + four dots
    for i in range(-6, 7):
        for j in range(-6, 7):
            if (i + j) % 2: continue
            cx, cy = 120 + i * sp, 120 + j * sp
            if math.hypot(cx - 120, cy - 120) > 104: continue
            ev.append(("stitch", (cx - 5, cy), (cx + 5, cy), SOOT, 1.0)); ev.append(("stitch", (cx, cy - 5), (cx, cy + 5), SOOT, 1.0))
            for (ox, oy) in ((-5, -5), (5, -5), (5, 5), (-5, 5)): ev.append(("knot", cx + ox * 0.9, cy + oy * 0.9, 1.0, SOOT))
    return ev

def piece_hitomezashi():
    ev = []; sp = 11; n = 22; x0 = y0 = 120 - sp * n / 2
    rows = [random.randint(0, 1) for _ in range(n + 1)]; cols = [random.randint(0, 1) for _ in range(n + 1)]
    for j in range(n + 1):
        y = y0 + j * sp
        for i in range(n):
            if (i + rows[j]) % 2 == 0:
                x = x0 + i * sp
                if math.hypot(x + sp / 2 - 120, y - 120) < 112: ev.append(("stitch", (x + 1, y), (x + sp - 1, y), TEAL, 1.7))
    for i in range(n + 1):
        x = x0 + i * sp
        for j in range(n):
            if (j + cols[i]) % 2 == 0:
                y = y0 + j * sp
                if math.hypot(x - 120, y + sp / 2 - 120) < 112: ev.append(("stitch", (x, y + 1), (x, y + sp - 1), OXBLOOD, 1.7))
    return ev

def piece_toadstool():
    ev = []
    def satin_ev(mask, col, ang, sp=1.4, endpt=(120, 120)):
        return ("fn", lambda L: satin(L, mask, col, ang, spacing=sp, sheen=0.25), endpt, col)
    # grass first
    for gx in range(30, 215, 9):
        h = random.uniform(8, 22); ev.append(("stitch", (gx, 196), (gx + random.uniform(-4, 4), 196 - h), SAGE, 1.6))
    # stems
    big = sm([(100, 190), (104, 130), (134, 130), (140, 190)], 2); small = sm([(56, 192), (58, 162), (74, 162), (78, 192)], 1)
    for m, pts in ((poly_mask(big), big), (poly_mask(small), small)):
        ev.append(satin_ev(m, (222, 210, 182), 90, 1.4, pts[0])); ev += path_events(pts + [pts[0]], SOOT, 1.0)
    ev.append(("fn", lambda L: satin(L, ellipse_mask(120, 134, 22, 6), (196, 180, 150), 0, spacing=1.3), (142, 134), SOOT))    # ring
    # caps
    cap = [(52, 136)] + ellipse_pts(120, 132, 70, 56, 40, 0, math.pi, 2 * math.pi) + [(188, 136)]
    ev.append(satin_ev(poly_mask(cap), OXBLOOD, 80, 1.5, (120, 76)))
    ev += path_events(cap + [cap[0]], SOOT, 1.2)
    for (sx, sy, sr) in [(84, 112, 7), (118, 92, 9), (150, 108, 6), (102, 128, 4), (138, 128, 5), (168, 128, 3.5), (70, 128, 3.5)]:
        ev.append(("fn", (lambda sx=sx, sy=sy, sr=sr: lambda L: satin(L, ellipse_mask(sx, sy, sr, sr), CREAM, 45, spacing=1.1, shadow=False))(), (sx, sy), CREAM))
        for k in range(5): ev.append(("knot", sx + sr * 0.55 * math.cos(k * 1.26), sy + sr * 0.55 * math.sin(k * 1.26), 1.1, (250, 246, 236)))
    cap2 = [(40, 166)] + ellipse_pts(67, 164, 32, 26, 24, 0, math.pi, 2 * math.pi) + [(94, 166)]
    ev.append(satin_ev(poly_mask(cap2), MUSTARD, 70, 1.4, (67, 140))); ev += path_events(cap2 + [cap2[0]], SOOT, 1.1)
    for (sx, sy, sr) in [(56, 152, 4), (72, 146, 4.5), (82, 158, 3)]:
        ev.append(("fn", (lambda sx=sx, sy=sy, sr=sr: lambda L: satin(L, ellipse_mask(sx, sy, sr, sr), CREAM, 45, spacing=1.1, shadow=False))(), (sx, sy), CREAM))
    for k in range(6): ev.append(("stitch", (120 + (k - 2.5) * 10, 136), (120 + (k - 2.5) * 12, 150), (120, 60, 50), 1.0))   # gills
    return ev

def bat_poly(cx, cy, s, flap):
    top = [(0, -3), (6, -9), (14, -15), (26, -18), (38, -14), (48, -6), (52, 0)]
    bot = [(46, 5), (40, -1), (32, 8), (24, 1), (16, 9), (8, 3), (0, 9)]
    k = 1 - 0.55 * flap
    pts = []
    for side in (1, -1):
        seq = (top + bot) if side == 1 else (top + bot)[::-1]
        pts += [(cx + side * x * s, cy + (y * k if x > 4 else y) * s - (12 * flap * s if x > 30 else 0)) for x, y in seq]
    body = [(cx, cy + 10 * s), (cx - 3.5 * s, cy + 2 * s), (cx - 3.5 * s, cy - 6 * s), (cx - 5 * s, cy - 12 * s), (cx - 1.5 * s, cy - 8 * s),
            (cx + 1.5 * s, cy - 8 * s), (cx + 5 * s, cy - 12 * s), (cx + 3.5 * s, cy - 6 * s), (cx + 3.5 * s, cy + 2 * s)]
    return pts, body

def draw_bats(frame):
    L = new_layer(); random.seed(12)
    satin(L, ellipse_mask(150, 72, 28, 28), MUSTARD, 30, spacing=1.4, sheen=0.3)
    backstitch(L, ellipse_pts(150, 72, 28, 28), (180, 136, 50), closed=True, width=0.9, dash=2.2, gap=1.0)
    for i in range(6):
        ph = frame / FRAMES * 2 * math.pi
        bx = (40 + i * 34 + frame * (2.2 + 0.4 * i)) % 300 - 30
        by = 90 + 40 * math.sin(ph * (0.5 + 0.1 * i) + i) + i * 8
        flap = 0.5 + 0.5 * math.sin(ph * 6 + i * 2)
        s = 0.5 + 0.12 * i
        wings, body = bat_poly(bx, by, s, flap)
        satin(L, poly_mask(wings), SOOT, 0, spacing=1.2, sheen=0.1, blur=0)
        satin(L, poly_mask(body), SOOT, 90, spacing=1.2, sheen=0.1, blur=0)
        backstitch(L, wings, (70, 62, 64), closed=True, width=0.8, dash=2.0, gap=0.9)
        knot(L, bx - 1.6 * s, by - 7 * s, 0.9 * s, OXBLOOD); knot(L, bx + 1.6 * s, by - 7 * s, 0.9 * s, OXBLOOD)
    # ground: a bare branch silhouette
    br = sm([(0, 214), (40, 206), (80, 210), (120, 200), (160, 206), (200, 196), (240, 200)], 2)
    yarn(L, br, (60, 44, 40), 3.0)
    return L

def piece_wreath_heart():
    ev = []
    cx, cy, r = 120, 120, 92
    for (a0, a1, flip) in ((110, 250, -1), (70, -70, 1)):
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / 40)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / 40))) for i in range(41)]
        ev += path_events(pts, (90, 110, 70), 1.2, 8)
        for i in range(14):
            t = (i + 0.5) / 14; a = math.radians(a0 + (a1 - a0) * t)
            bx, by = cx + r * math.cos(a), cy + r * math.sin(a)
            tx_, ty_ = -math.sin(a) * flip, math.cos(a) * flip
            side = 1 if i % 2 == 0 else -1
            dx = tx_ * 0.7 + math.cos(a) * side * 0.7; dy = ty_ * 0.7 + math.sin(a) * side * 0.7; dn = math.hypot(dx, dy)
            col = [SAGE, (150, 168, 112), (100, 122, 76)][i % 3]
            ev.append(("fn", (lambda bx=bx, by=by, dx=dx, dy=dy, dn=dn, col=col: lambda L: leaf(L, bx, by, bx + dx / dn * 12, by + dy / dn * 12, 4.0, col))(), (bx, by), col))
    for a_deg in (140, 200):
        for sgn in (1, -1):
            a = math.radians(a_deg); x = cx + sgn * r * math.cos(a); y = cy + r * math.sin(a)
            ev.append(("fn", (lambda x=x, y=y: lambda L: daisy(L, x, y, 10, rot=random.uniform(0, 1)))(), (x, y), CREAM))
    ev.append(("fn", lambda L: daisy(L, 120, 120 + r, 12, petals=12), (120, 212), CREAM))
    # French-knot heart in the centre, filled in a spiral from the outside in
    hp = G2.heart_pts(120, 116, 3.2); hm = poly_mask(hp)
    pts = []
    for yy in range(70, 170, 6):
        for xx in range(70, 170, 6):
            jx, jy = xx + random.uniform(-1.5, 1.5), yy + random.uniform(-1.5, 1.5)
            if 0 <= jx < 240 and 0 <= jy < 240 and hm.getpixel((int(jx * S), int(jy * S))) > 0: pts.append((jx, jy))
    pts.sort(key=lambda p: -math.hypot(p[0] - 120, p[1] - 118))
    for (x, y) in pts: ev.append(("knot", x, y, 3.0, OXBLOOD if random.random() < 0.85 else RUST))
    return ev

def piece_granny_on_linen():
    ev = square_rounds(3, step=14, inner0=10, palette=[PLUM, MUSTARD, TEAL, OXBLOOD], skew=random.uniform(-5, 5))
    # blanket-stitch it down onto the linen
    h = 10 + 14 * 2 + 12 + 3
    corners = [(120 - h, 120 - h), (120 + h, 120 - h), (120 + h, 120 + h), (120 - h, 120 + h)]
    at, total = resample(corners + [corners[0]]); pos = 0
    while pos < total:
        a = at(pos); b = at(min(total, pos + 7))
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) or 1; nx, ny = -dy / ln, dx / ln
        ev.append(("stitch", a, b, SOOT, 1.4)); ev.append(("stitch", a, (a[0] - nx * 6, a[1] - ny * 6), SOOT, 1.4)); pos += 7
    return ev

def piece_patches():
    ev = []
    scraps = [(sm([(44, 60), (120, 50), (126, 118), (50, 126)], 1), OXBLOOD, 30), (sm([(130, 70), (200, 64), (206, 136), (136, 140)], 1), TEAL, -40),
              (sm([(60, 134), (128, 128), (134, 196), (66, 200)], 1), MUSTARD, 70), (sm([(142, 148), (196, 142), (190, 198), (148, 204)], 1), PLUM, 10)]
    for pts, col, ang in scraps:
        ev.append(("fn", (lambda pts=pts, col=col, ang=ang: lambda L: satin(L, poly_mask(pts), col, ang, spacing=1.5, sheen=0.28))(), pts[0], col))
        thread = CREAM if col != MUSTARD else SOOT
        at, total = resample(pts + [pts[0]]); pos = 0
        while pos < total: ev.append(("stitch", at(pos), at(min(total, pos + 4)), thread, 1.5)); pos += 6.5
        # a few decorative crosses in the middle of each scrap
        cx = sum(p[0] for p in pts) / 4; cy = sum(p[1] for p in pts) / 4
        for (ox, oy) in ((-10, -10), (10, -10), (0, 0), (-10, 10), (10, 10)): ev += cross(cx + ox - 4, cy + oy - 4, 8, thread, 1.4)
    return ev

def draw_dandelion(frame):
    L = new_layer(); random.seed(31)
    t = frame / (FRAMES - 1)
    stem = sm([(96, 230), (100, 190), (108, 150), (112, 118)], 2)
    yarn(L, stem, (74, 86, 56), 2.2)
    yarn(L, [(100, 190), (84, 176), (70, 178)], (74, 86, 56), 1.6)    # leaf stalk
    satin(L, poly_mask(sm([(70, 178), (62, 168), (48, 170), (44, 182), (56, 190), (70, 184)], 1)), SAGE, 20, spacing=1.3)
    cx, cy = 112, 112
    knot(L, cx, cy, 4, (120, 112, 84))
    nseeds = 26
    for i in range(nseeds):
        a = 2 * math.pi * i / nseeds + 0.1
        release = (i * 7 % nseeds) / nseeds * 0.75 if (i * 7 % nseeds) < nseeds * 0.6 else 9.0   # ~40% never let go
        if t < release:
            ex, ey = cx + 30 * math.cos(a), cy + 30 * math.sin(a)
            stitch(L, (cx, cy), (ex, ey), (150, 140, 110), 0.8)
        else:
            u = (t - release) / max(0.001, 1 - release)
            ex = cx + 30 * math.cos(a) + 120 * u + 10 * math.sin(u * 9 + i)
            ey = cy + 30 * math.sin(a) - 90 * u + 8 * math.cos(u * 7 + i)
            if ex > 250 or ey < -10: continue
            stitch(L, (ex, ey + 6), (ex - 2, ey + 14), (150, 140, 110), 0.8)
        for k in range(5):
            pa = a + (k - 2) * 0.28 + (0 if t < release else 0.6)
            stitch(L, (ex, ey), (ex + 7 * math.cos(pa), ey + 7 * math.sin(pa)), (128, 118, 100), 0.7)
            knot(L, ex + 7 * math.cos(pa), ey + 7 * math.sin(pa), 0.7, (96, 88, 82))
    return L

if __name__ == "__main__":
    pieces = []
    jobs = [
        ("sampler", lambda: render_events("sampler", piece_sampler(), bg_aida())),
        ("redwork_bird", lambda: render_events("redwork_bird", piece_redwork_bird(), bg_linen(7))),
        ("blackwork", lambda: render_events("blackwork", piece_blackwork(), bg_satin(8))),
        ("hitomezashi", lambda: render_events("hitomezashi", piece_hitomezashi(), bg_linen(9))),
        ("toadstool", lambda: render_events("toadstool", piece_toadstool(), bg_linen(10))),
        ("bats", lambda: render_draw("bats", draw_bats, bg_satin(11, (242, 236, 222), 60))),
        ("wreath_heart", lambda: render_events("wreath_heart", piece_wreath_heart(), bg_linen(12))),
        ("granny_on_linen", lambda: render_events("granny_on_linen", piece_granny_on_linen(), bg_linen(13), tool="hook")),
        ("patches", lambda: render_events("patches", piece_patches(), bg_satin(14))),
        ("dandelion", lambda: render_draw("dandelion", draw_dandelion, bg_linen(15))),
    ]
    for i, (name, job) in enumerate(jobs):
        random.seed(200 + i); pieces.append((name, job())); print(name)
    seq = []
    for i, (name, fr) in enumerate(pieces):
        seq += fr + [fr[-1]] * 12
        nxt = pieces[(i + 1) % len(pieces)][1][0]
        seq += [Image.blend(fr[-1], nxt, j / 6) for j in range(1, 6)]
    seq[0].save(f"{OUT}/preview_linen.gif", save_all=True, append_images=seq[1:], duration=90, loop=0)
    sheet = Image.new("RGB", (W * 5 + 60, W * 4 + 50), (40, 40, 40))
    for i, (name, fr) in enumerate(pieces):
        col = i % 5; rowb = (i // 5) * 2
        sheet.paste(fr[FRAMES // 2], (10 + col * (W + 10), 10 + rowb * (W + 10)))
        sheet.paste(fr[-1], (10 + col * (W + 10), 10 + (rowb + 1) * (W + 10)))
    sheet.save(f"{OUT}/sheet_linen.png")
    print("done")
