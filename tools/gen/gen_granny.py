#!/usr/bin/env python3
"""Patchwork / Tim Burton / granny-square set for the 240x240 round pin.
4 related granny-square pieces + 2 standalone pieces, each 48 animated frames.
Shared palette: mustard, oxblood, dusty teal, cream, soot black."""
import math, random, os
from PIL import Image, ImageDraw, ImageChops
import gen_insects2 as G
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, ellipse_mask, poly_mask, rect_mask, new_layer, satin, backstitch, sm
from gen_stitch import stitch, loop, needle, compose, resample

OUT = "/home/claude/eye_pin_lowpower/granny"
os.makedirs(OUT, exist_ok=True)
FRAMES = 48

MUSTARD, OXBLOOD, TEAL, CREAM, SOOT = (214, 168, 58), (124, 34, 42), (72, 132, 130), (236, 226, 204), (30, 27, 29)
PLUM, RUST, SAGE = (96, 58, 92), (178, 92, 52), (132, 150, 100)
PALETTE = [MUSTARD, OXBLOOD, TEAL, CREAM, PLUM, RUST, SAGE]

# ------------------------------------------------------------------ yarn
def yarn(L, pts, col, w=3.0):
    """Chunky 2-ply yarn stroke along a polyline."""
    d = ImageDraw.Draw(L)
    pp = [P(*q) for q in pts]
    if len(pp) < 2: return
    d.line([(x + 0.7 * S, y + 1.0 * S) for x, y in pp], fill=(0, 0, 0, 170), width=int(w * S), joint="curve")
    d.line(pp, fill=shade(col, 0.8) + (255,), width=int(w * S), joint="curve")
    d.line(pp, fill=col + (255,), width=max(1, int(w * S * 0.68)), joint="curve")
    for q in (pp[0], pp[-1]):
        r = w * S / 2; d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=shade(col, 0.8) + (255,))
        r2 = r * 0.68; d.ellipse([q[0] - r2, q[1] - r2, q[0] + r2, q[1] + r2], fill=col + (255,))
    at, total = resample(pts)
    pos = 0.0
    while pos < total:                                   # ply twist ticks
        a, b = at(pos), at(min(total, pos + 0.8))
        dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1; dx, dy = dx / n, dy / n; nx, ny = -dy, dx
        m = at(min(total, pos + 0.4))
        d.line([P(m[0] + nx * w * 0.33 - dx * w * 0.25, m[1] + ny * w * 0.33 - dy * w * 0.25),
                P(m[0] - nx * w * 0.33 + dx * w * 0.25, m[1] - ny * w * 0.33 + dy * w * 0.25)],
               fill=shade(col, 0.62) + (150,), width=max(1, int(0.55 * S)))
        pos += w * 0.7
    d.line([(x - 0.35 * S, y - 0.55 * S) for x, y in pp], fill=shade(col, 1.35) + (85,), width=max(1, int(w * S * 0.22)), joint="curve")

def post(base, top, wobble=0.0):
    """Double-crochet post: slightly S-curved stroke base->top with a yarn-over bar."""
    mx, my = (base[0] + top[0]) / 2, (base[1] + top[1]) / 2
    dx, dy = top[0] - base[0], top[1] - base[1]; n = math.hypot(dx, dy) or 1; nx, ny = -dy / n, dx / n
    k = 0.9 + wobble
    return [base, (mx + nx * k, my + ny * k), top]

def hook(L, pos, dirv, col):
    """Crochet hook: silver shaft with a curled tip, yarn looped over it."""
    if pos is None: return
    d = ImageDraw.Draw(L)
    dx, dy = dirv; n = math.hypot(dx, dy) or 1; dx, dy = dx / n, dy / n; nx, ny = -dy, dx
    ex, ey = pos[0] + dx * 2, pos[1] + dy * 2
    tx, ty = ex + dx * 18, ey + dy * 18
    d.line([P(ex + 0.5, ey + 0.9), P(tx + 0.5, ty + 0.9)], fill=(0, 0, 0, 170), width=int(2.2 * S))
    d.line([P(ex, ey), P(tx, ty)], fill=(190, 194, 200, 255), width=int(2.0 * S))
    d.line([P(ex, ey), P(tx, ty)], fill=(238, 240, 244, 255), width=int(0.6 * S))
    # curled tip
    d.arc([P(ex - 2.6, ey - 2.6), P(ex + 2.6, ey + 2.6)], start=0, end=270, fill=(190, 194, 200, 255), width=int(1.6 * S))
    # yarn over the hook
    d.line([P(pos[0], pos[1]), P(ex + nx * 3.5, ey + ny * 3.5), P(ex + dx * 2 - nx * 1.5, ey + dy * 2 - ny * 1.5)], fill=col + (255,), width=int(2.4 * S), joint="curve")

# ------------------------------------------------------------------ granny geometry
def square_rounds(rounds, step=13, inner0=10, palette=PALETTE, wobble=0.0, skew=0.0, cx=120, cy=120, post_len=None, start_col=0):
    """Event list for a classic granny square built round by round."""
    ev = [("ring", (cx, cy), inner0 * 0.55, palette[start_col % len(palette)])]
    for n in range(1, rounds + 1):
        col = palette[(start_col + n) % len(palette)]
        hi = inner0 + step * (n - 1); ho = hi + (post_len or step - 2)
        per_side = max(2, int(round(2 * hi / 11.5)))
        for side in range(4):
            a = math.radians(90 * side + skew)
            ca, sa = math.cos(a), math.sin(a)
            def T(x, y): return (cx + x * ca - y * sa, cy + x * sa + y * ca)
            for k in range(per_side):
                x = -hi + 2 * hi * (k + 0.5) / per_side
                jx = random.uniform(-wobble, wobble); jl = random.uniform(-wobble, wobble)
                base = T(x + jx, -hi + 1)
                tops = [T(x + jx + o, -ho - jl) for o in (-3.6, 0, 3.6)]
                for t in tops: ev.append(("yarn", post(base, t, wobble * 0.5), col, 3.0))
                if k < per_side - 1:                    # ch-1 between side clusters
                    nx_ = -hi + 2 * hi * (k + 1.5) / per_side
                    ev.append(("yarn", [T(x + 3.6, -ho - jl), T((x + nx_) / 2, -ho - 1.5), T(nx_ - 3.6, -ho)], col, 2.4))
            # corner chain-2 arc from this side's last cluster to next side's first
            x_last = -hi + 2 * hi * (per_side - 0.5) / per_side
            p1 = T(x_last + 3.6, -ho); c = T(ho + 1.5, -ho - 1.5)
            a2 = math.radians(90 * (side + 1) + skew); ca2, sa2 = math.cos(a2), math.sin(a2)
            x_first = -hi + 2 * hi * 0.5 / per_side
            p2 = (cx + (x_first - 3.6) * ca2 - (-ho) * sa2, cy + (x_first - 3.6) * sa2 + (-ho) * ca2)
            ev.append(("yarn", [p1, c, p2], col, 2.4))
    return ev

def circle_rounds(rounds, step=13, r0=11, palette=PALETTE, cx=120, cy=120, start_col=0):
    ev = [("ring", (cx, cy), r0 * 0.6, palette[start_col % len(palette)])]
    for n in range(1, rounds + 1):
        col = palette[(start_col + n) % len(palette)]
        ri = r0 + step * (n - 1); ro = ri + step - 2
        count = 6 + 5 * n
        for k in range(count):
            a = 2 * math.pi * k / count - math.pi / 2
            base = (cx + ri * math.cos(a), cy + ri * math.sin(a))
            for off in (-0.045, 0, 0.045):
                aa = a + off * (12 / n)
                ev.append(("yarn", post(base, (cx + ro * math.cos(aa), cy + ro * math.sin(aa))), col, 3.0))
            a_next = 2 * math.pi * (k + 1) / count - math.pi / 2
            mid = (a + a_next) / 2
            ev.append(("yarn", [(cx + ro * math.cos(a + 0.045 * 12 / n), cy + ro * math.sin(a + 0.045 * 12 / n)),
                                (cx + (ro + 1.5) * math.cos(mid), cy + (ro + 1.5) * math.sin(mid)),
                                (cx + ro * math.cos(a_next - 0.045 * 12 / n), cy + ro * math.sin(a_next - 0.045 * 12 / n))], col, 2.4))
    return ev

# ------------------------------------------------------------------ pieces
def piece_granny_classic():
    return square_rounds(5, palette=[MUSTARD, OXBLOOD, TEAL, CREAM, PLUM, MUSTARD], skew=random.uniform(-4, 4))

def piece_granny_mandala():
    return circle_rounds(7, palette=[MUSTARD, OXBLOOD, TEAL, CREAM, RUST, PLUM, SAGE, MUSTARD])

def piece_granny_burton():
    # black & bone stripes, every stitch a little drunk, a loose tail curling off the corner
    ev = square_rounds(5, palette=[(78, 72, 78), CREAM, (78, 72, 78), CREAM, (78, 72, 78), CREAM], wobble=1.6, skew=random.uniform(6, 10), post_len=12)
    tail = [(120 + 66, 120 - 70), (120 + 78, 120 - 84), (120 + 70, 120 - 98), (120 + 86, 120 - 104)]
    ev.append(("yarn", sm(tail + tail[::-1], 1)[:8], CREAM, 2.4))
    return ev

def piece_granny_patchwork():
    ev = []
    cell = 62; pal = PALETTE[:]
    order = [(1, 1), (0, 1), (1, 0), (2, 1), (1, 2), (0, 0), (2, 2), (0, 2), (2, 0)]
    for (i, j) in order:
        cx, cy = 120 + (i - 1) * cell, 120 + (j - 1) * cell
        if math.hypot(cx - 120, cy - 120) > 150: continue
        random.shuffle(pal)
        ev += square_rounds(2, step=10, inner0=7, palette=pal[:3] + [pal[3]], cx=cx, cy=cy, post_len=8, skew=random.uniform(-2, 2))
    # whipstitch the squares together along the grid lines
    for g in (-1, 1):
        for t in range(-96, 97, 7):
            x = 120 + g * cell / 2
            ev.append(("stitch", (x - 2.5, 120 + t - 2), (x + 2.5, 120 + t + 2), CREAM, 1.4))
            ev.append(("stitch", (120 + t - 2, x - 2.5), (120 + t + 2, x + 2.5), CREAM, 1.4))
    return ev

def draw_patched_moon(frame):
    """Standalone: crescent sewn from three scraps, bare branch, twinkling stars."""
    L = new_layer()
    random.seed(99)
    cx, cy, r = 120, 110, 62
    full = ellipse_mask(cx, cy, r, r)
    cut = ellipse_mask(cx + 34, cy - 10, r * 0.86, r * 0.86)
    moon = ImageChops.subtract(full, cut)
    # three scraps split by two wavy seams
    seam1 = sm([(0, 60), (80, 70), (120, 85), (160, 95), (240, 100), (240, 0), (0, 0)], 2)
    seam2 = sm([(0, 125), (60, 135), (110, 150), (170, 160), (240, 165), (240, 0), (0, 0)], 2)
    m1 = ImageChops.multiply(moon, poly_mask(seam1))
    m2 = ImageChops.multiply(moon, ImageChops.subtract(poly_mask(seam2), poly_mask(seam1)))
    m3 = ImageChops.subtract(moon, poly_mask(seam2))
    satin(L, m1, MUSTARD, 35, spacing=1.5, sheen=0.3)
    satin(L, m2, CREAM, -30, spacing=1.5, sheen=0.25)
    # checked scrap: cream base with thin oxblood lines
    satin(L, m3, (226, 208, 170), 90, spacing=1.5, sheen=0.2)
    chk = new_layer(); d = ImageDraw.Draw(chk)
    for k in range(0, 240, 8):
        d.line([P(k, 0), P(k, 240)], fill=OXBLOOD + (140,), width=int(0.8 * S)); d.line([P(0, k), P(240, k)], fill=OXBLOOD + (140,), width=int(0.8 * S))
    L.paste(chk, (0, 0), ImageChops.multiply(m3, chk.split()[3]))
    # branch (always there)
    br = sm([(30, 230), (48, 196), (60, 168), (80, 150), (96, 138), (120, 130)], 2)
    yarn(L, br, (70, 48, 34), 3.2)
    yarn(L, [(60, 168), (52, 150), (40, 140)], (70, 48, 34), 2.2)
    yarn(L, [(80, 150), (84, 128), (78, 116)], (70, 48, 34), 2.0)
    yarn(L, [(96, 138), (108, 118)], (70, 48, 34), 1.6)
    # seams get whipstitched over frames 0..30; crescent outline whipstitched 0..30 too
    prog = min(1.0, frame / 30.0)
    def whip(path_pts, n, col, prog):
        at, total = resample(path_pts)
        for k in range(int(n * prog)):
            t = total * (k + 0.5) / n
            a = at(t); b = at(min(total, t + 2.5))
            dx, dy = b[0] - a[0], b[1] - a[1]; nn = math.hypot(dx, dy) or 1; nx, ny = -dy / nn, dx / nn
            stitch(L, (a[0] + nx * 4 - dx / nn * 2, a[1] + ny * 4 - dy / nn * 2), (a[0] - nx * 4 + dx / nn * 2, a[1] - ny * 4 + dy / nn * 2), col, 1.5)
    # visible parts of the seams: clip to moon by only placing stitches whose midpoint is inside moon
    for seam, n in ((seam1[:len(seam1) // 2], 22), (seam2[:len(seam2) // 2], 24)):
        pts = [p for p in seam if moon.getpixel(P(*p)) > 0] if False else seam
        at, total = resample(pts)
        k_total = n; placed = 0
        for k in range(k_total):
            t = total * (k + 0.5) / k_total; a = at(t)
            if moon.getpixel((int(a[0] * S), int(a[1] * S))) == 0: continue
            if placed >= int(n * prog): break
            b = at(min(total, t + 2.5)); dx, dy = b[0] - a[0], b[1] - a[1]; nn = math.hypot(dx, dy) or 1; nx, ny = -dy / nn, dx / nn
            stitch(L, (a[0] + nx * 4 - dx / nn * 2, a[1] + ny * 4 - dy / nn * 2), (a[0] - nx * 4 + dx / nn * 2, a[1] - ny * 4 + dy / nn * 2), SOOT, 1.5)
            placed += 1
    outline = ellipse_pts(cx, cy, r + 1, r + 1, 80, 0, math.radians(100), math.radians(100 + 300))
    whip(outline, 48, SOOT, prog)
    # stars: twinkle after the sewing is done
    stars = [(44, 60, 2.2), (70, 36, 1.6), (176, 44, 2.4), (200, 86, 1.6), (186, 150, 2.0), (150, 196, 1.6), (62, 100, 1.4), (210, 120, 1.3)]
    for i, (sx, sy, sr) in enumerate(stars):
        tw = 0.6 + 0.4 * math.sin(frame * 0.6 + i * 1.7)
        if frame < 30: tw = 0.75
        knot(L, sx, sy, sr * tw, shade(CREAM, 0.6 + 0.5 * tw))
        if sr > 2.0:
            for (ax, ay) in ((1, 0), (0, 1)):
                stitch(L, (sx - ax * 4.5 * tw, sy - ay * 4.5 * tw), (sx + ax * 4.5 * tw, sy + ay * 4.5 * tw), shade(MUSTARD, 0.7 + 0.4 * tw), 0.9)
    return L

def draw_button(frame):
    """Standalone: a mismatched button on a frayed scrap. One thread snaps, the button
    drops and tilts, then the needle sews it back on."""
    L = new_layer()
    random.seed(7)
    # frayed scrap of cream check
    scrap = sm([(42, 58), (196, 48), (206, 190), (54, 198)], 2)
    m = poly_mask(scrap)
    satin(L, m, (222, 206, 172), 90, spacing=1.5, sheen=0.2)
    chk = new_layer(); d = ImageDraw.Draw(chk)
    for k in range(30, 220, 11):
        d.line([P(k, 0), P(k, 240)], fill=TEAL + (120,), width=int(1.0 * S)); d.line([P(0, k), P(240, k)], fill=TEAL + (120,), width=int(1.0 * S))
    L.paste(chk, (0, 0), ImageChops.multiply(m, chk.split()[3]))
    at, total = resample(scrap + [scrap[0]])
    for k in range(70):                                          # fray
        a = at(total * k / 70); b = at(total * (k + 0.2) / 70)
        dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1; nx, ny = -dy / n, dx / n
        stitch(L, a, (a[0] + nx * random.uniform(2, 5), a[1] + ny * random.uniform(2, 5)), (200, 185, 150), 0.8)
    # running stitch holding the scrap down
    inner = sm([(54, 70), (184, 61), (194, 178), (66, 186)], 2)
    atI, totI = resample(inner + [inner[0]])
    pos = 0
    while pos < totI:
        stitch(L, atI(pos), atI(min(totI, pos + 4)), OXBLOOD, 1.4); pos += 6.5

    # timeline: 0-10 intact, 10-14 thread snaps, 14-22 button drops/tilts, 22-26 hold, 26-44 re-sew, 44-48 settled
    if frame < 10: snapped, drop, tilt, resew = False, 0.0, 0.0, 0.0
    elif frame < 14: snapped, drop, tilt, resew = True, 0.0, 0.0, 0.0
    elif frame < 22:
        t = (frame - 14) / 8; e = 1 - (1 - t) ** 3; snapped, drop, tilt, resew = True, 6 * e, -14 * e, 0.0
    elif frame < 26: snapped, drop, tilt, resew = True, 6.0, -14.0, 0.0
    elif frame < 44:
        t = (frame - 26) / 18; snapped, drop, tilt, resew = True, 6 * (1 - t), -14 * (1 - t), t
    else: snapped, drop, tilt, resew = False, 0.0, 0.0, 1.0

    bx, by, br = 120, 118 + drop, 34
    rot = math.radians(tilt)
    # button body: soot with a worn rim, 4 holes
    satin(L, ellipse_mask(bx, by, br, br), (104, 96, 100), 20, spacing=1.3, sheen=0.4)
    satin(L, ellipse_mask(bx, by, br - 5, br - 5), (50, 46, 50), 110, spacing=1.3, sheen=0.45)
    backstitch(L, ellipse_pts(bx, by, br - 5, br - 5), (70, 64, 66), width=0.9, dash=2.0, gap=1.2, closed=True)
    holes = []
    for (hx, hy) in ((-8, -8), (8, -8), (8, 8), (-8, 8)):
        x = bx + hx * math.cos(rot) - hy * math.sin(rot); y = by + hx * math.sin(rot) + hy * math.cos(rot)
        holes.append((x, y))
        ImageDraw.Draw(L).ellipse([P(x - 3, y - 3), P(x + 3, y + 3)], fill=(8, 8, 10, 255))
    # the two cross threads (teal, clashing on purpose). Thread A: holes 0-2, thread B: holes 1-3
    thrA = [holes[0], holes[2]]; thrB = [holes[1], holes[3]]
    yarn(L, thrB, TEAL, 2.6)
    if not snapped:
        yarn(L, thrA, MUSTARD if frame >= 44 else TEAL, 2.6)
    else:
        # broken ends curling out of holes 0 and 2
        h0, h2 = holes[0], holes[2]
        yarn(L, sm([h0, (h0[0] - 6, h0[1] - 10), (h0[0] - 14, h0[1] - 8)], 1)[:6], TEAL, 2.4)
        yarn(L, sm([h2, (h2[0] + 8, h2[1] + 6), (h2[0] + 10, h2[1] + 14)], 1)[:6], TEAL, 2.4)
        if resew > 0:
            # new thread: this time mustard (even more mismatched), drawn progressively hole0->hole2 then a second pass
            a, b = holes[0], holes[2]
            seg = min(1.0, resew * 1.3)
            yarn(L, [a, (a[0] + (b[0] - a[0]) * seg, a[1] + (b[1] - a[1]) * seg)], MUSTARD, 2.6)
            if resew > 0.75:
                s2 = (resew - 0.75) / 0.25
                yarn(L, [b, (b[0] + (a[0] - b[0]) * s2 + 1.5, b[1] + (a[1] - b[1]) * s2 - 1.0)], MUSTARD, 2.6)
            if resew < 1.0:
                tip = (a[0] + (b[0] - a[0]) * seg, a[1] + (b[1] - a[1]) * seg)
                needle(L, tip, (b[0] - a[0], b[1] - a[1]), MUSTARD)
    # a tiny second button, clearly from a different set
    satin(L, ellipse_mask(172, 158, 9, 9), OXBLOOD, 40, spacing=1.2, sheen=0.4)
    for (hx, hy) in ((-2.5, 0), (2.5, 0)):
        ImageDraw.Draw(L).ellipse([P(172 + hx - 1.2, 158 + hy - 1.2), P(172 + hx + 1.2, 158 + hy + 1.2)], fill=(8, 8, 10, 255))
    stitch(L, (169.5, 158), (174.5, 158), CREAM, 1.3)
    return L

# ------------------------------------------------------------------ event runner (granny pieces)
def run_event(L, e):
    k = e[0]
    if k == "yarn":
        _, pts, col, w = e; yarn(L, pts, col, w); return pts[-1], (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]), col
    if k == "ring":
        _, (x, y), r, col = e; yarn(L, ellipse_pts(x, y, r, r, 24), col, 3.0); return (x + r, y), (0, -1), col
    if k == "stitch":
        _, a, b, col, w = e; stitch(L, a, b, col, w); return b, (b[0] - a[0], b[1] - a[1]), col
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
        if f < FRAMES - 1 and last:
            (hook if tool == "hook" else needle)(fl, *last)
        img = compose(fl); img.save(f"{OUT}/{name}_{f:02d}.png"); frames.append(img)
    return frames

def render_draw(name, fn):
    frames = []
    for f in range(FRAMES):
        img = compose(fn(f)); img.save(f"{OUT}/{name}_{f:02d}.png"); frames.append(img)
    return frames

if __name__ == "__main__":
    pieces = []
    random.seed(1); pieces.append(("granny_classic", render_events("granny_classic", piece_granny_classic())))
    random.seed(2); pieces.append(("granny_mandala", render_events("granny_mandala", piece_granny_mandala())))
    random.seed(3); pieces.append(("granny_burton", render_events("granny_burton", piece_granny_burton())))
    random.seed(4); pieces.append(("granny_patchwork", render_events("granny_patchwork", piece_granny_patchwork(), tool="mixed")))
    pieces.append(("patched_moon", render_draw("patched_moon", draw_patched_moon)))
    pieces.append(("button", render_draw("button", draw_button)))
    seq = []
    for i, (name, fr) in enumerate(pieces):
        seq += fr + [fr[-1]] * 12
        nxt = pieces[(i + 1) % len(pieces)][1][0]
        seq += [Image.blend(fr[-1], nxt, j / 6) for j in range(1, 6)]
    seq[0].save(f"{OUT}/preview_granny.gif", save_all=True, append_images=seq[1:], duration=90, loop=0)
    sheet = Image.new("RGB", (W * 6 + 70, W * 2 + 30), (40, 40, 40))
    for i, (name, fr) in enumerate(pieces):
        sheet.paste(fr[FRAMES // 2], (10 + i * (W + 10), 10))
        sheet.paste(fr[-1], (10 + i * (W + 10), W + 20))
    sheet.save(f"{OUT}/sheet_granny.png")
    print("done")
