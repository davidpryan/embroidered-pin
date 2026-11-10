#!/usr/bin/env python3
"""Ten bold pieces that read from across a room: one big motif, high contrast, fat thread."""
import math, random, os
from PIL import Image, ImageDraw, ImageChops
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, ellipse_mask, poly_mask, new_layer, satin, backstitch, sm
from gen_stitch import stitch, needle, resample
from gen_granny import yarn, post, hook, MUSTARD, OXBLOOD, TEAL, CREAM, SOOT, PLUM, RUST, SAGE
from gen_linen import bg_linen, bg_satin, BLACK_BG, compose_bg
import gen_linen, gen_granny2 as G2

OUT = "/home/claude/eye_pin_lowpower/bold"
os.makedirs(OUT, exist_ok=True)
gen_linen.OUT = OUT
TAU = 2 * math.pi
BONE = (236, 226, 204)

def bigknot(L, x, y, r, col):
    """Oversized French knot: layered rings so it reads as wound thread."""
    d = ImageDraw.Draw(L)
    d.ellipse([P(x - r, y - r + 1.5), P(x + r, y + r + 1.5)], fill=(0, 0, 0, 160))
    for k, f in enumerate((1.0, 0.78, 0.55, 0.32)):
        c = shade(col, 0.75 + 0.18 * k); rr = r * f
        d.ellipse([P(x - rr, y - rr), P(x + rr, y + rr)], fill=c + (255,))
        d.arc([P(x - rr, y - rr), P(x + rr, y + rr)], 200, 330, fill=shade(col, 1.3) + (200,), width=max(1, int(r * 0.12 * S)))

def rot(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]

# ------------------------------------------------------------------ builds (needle/hook events)
def big_x():
    ev = []
    for a, b in (((44, 44), (196, 196)), ((196, 44), (44, 196))):
        at, total = resample([a, b]); pos = 0
        while pos < total: ev.append(("yarn", [at(pos), at(min(total, pos + 12))], OXBLOOD, 9.0)); pos += 11
    for (x, y) in ((44, 44), (196, 196), (196, 44), (44, 196)): ev.append(("fn", (lambda x=x, y=y: lambda L: bigknot(L, x, y, 9, OXBLOOD))(), (x, y), OXBLOOD))
    return ev

def big_granny():
    from gen_granny import square_rounds
    ev = [("ring", (120, 120), 14, MUSTARD)]
    # two fat rounds, hand-placed so each cluster is huge
    for n, (hi, ho, col, per) in enumerate(((22, 56, OXBLOOD, 2), (58, 94, TEAL, 3))):
        hs = hi
        for side in range(4):
            a = math.radians(90 * side); ca, sa = math.cos(a), math.sin(a)
            def T(x, y, ca=ca, sa=sa): return (120 + x * ca - y * sa, 120 + x * sa + y * ca)
            xs = [-hs + 2 * hs * (k + 0.5) / per for k in range(per)]
            for k, x in enumerate(xs):
                base = T(x, -hi + 2)
                for o in (-9, 0, 9): ev.append(("yarn", post(base, T(x + o, -ho), 1.5), col, 7.0))
                if k < per - 1: ev.append(("yarn", [T(x + 9, -ho), T((x + xs[k + 1]) / 2, -ho - 3), T(xs[k + 1] - 9, -ho)], col, 5.0))
            a2 = math.radians(90 * (side + 1)); ca2, sa2 = math.cos(a2), math.sin(a2)
            ev.append(("yarn", [T(xs[-1] + 9, -ho), T(ho + 4, -ho - 4), (120 + (xs[0] - 9) * ca2 - (-ho) * sa2, 120 + (xs[0] - 9) * sa2 + (-ho) * ca2)], col, 5.0))
    return ev

def big_toadstool():
    ev = []
    stem = sm([(86, 232), (92, 150), (148, 150), (154, 232)], 2)
    ev.append(("fn", lambda L: satin(L, poly_mask(stem), (226, 214, 190), 90, spacing=1.6, sheen=0.25), (120, 190), CREAM))
    ev.append(("fn", lambda L: yarn(L, stem + [stem[0]], SOOT, 3.0), (120, 232), SOOT))
    cap = [(10, 150)] + ellipse_pts(120, 142, 112, 96, 48, 0, math.pi, TAU) + [(230, 150)]
    ev.append(("fn", lambda L: satin(L, poly_mask(cap), OXBLOOD, 85, spacing=1.6, sheen=0.3), (120, 50), OXBLOOD))
    ev.append(("fn", lambda L: yarn(L, cap + [cap[0]], SOOT, 3.5), (230, 150), SOOT))
    for (sx, sy, sr) in ((62, 106, 16), (122, 70, 20), (182, 104, 14), (96, 132, 9), (156, 134, 10)):
        ev.append(("fn", (lambda sx=sx, sy=sy, sr=sr: lambda L: (satin(L, ellipse_mask(sx, sy, sr, sr), BONE, 45, spacing=1.4, shadow=False), yarn(L, ellipse_pts(sx, sy, sr, sr, 30), shade(BONE, 0.8), 2.0)))(), (sx, sy), CREAM))
    return ev

def big_star():
    ev = []
    pts = []
    for i in range(10):
        r = 104 if i % 2 == 0 else 44; a = -math.pi / 2 + i * math.pi / 5
        pts.append((120 + r * math.cos(a), 124 + r * math.sin(a)))
    at, total = resample(pts + [pts[0]]); pos = 0
    while pos < total: ev.append(("yarn", [at(pos), at(min(total, pos + 12))], MUSTARD, 8.0)); pos += 11
    ev.append(("fn", lambda L: bigknot(L, 120, 124, 16, OXBLOOD), (120, 124), OXBLOOD))
    return ev

def big_spiral_build():
    ev = []; b = 14 / TAU; th = 0.5
    while True:
        r = 4 + b * th
        if r > 112: break
        pts = []
        for k in range(3):
            rr = 4 + b * (th + k * 0.18); pts.append((120 + rr * math.cos(th + k * 0.18), 120 + rr * math.sin(th + k * 0.18)))
        ev.append(("yarn", pts, BONE, 7.5)); th += 0.36
    return ev

def big_granny_bg(): return BLACK_BG

# ------------------------------------------------------------------ loops (draw fns)
def big_button(f, FR=16):
    L = new_layer(); ph = TAU * f / FR; random.seed(3)
    tilt = math.radians(6) * math.sin(ph); cx, cy, r = 120, 120, 104
    satin(L, ellipse_mask(cx, cy, r, r), BONE, 20 + math.degrees(tilt) * 0, spacing=1.6, sheen=0.35)
    satin(L, ellipse_mask(cx, cy, r - 16, r - 16), (222, 210, 184), 110, spacing=1.6, sheen=0.3)
    yarn(L, ellipse_pts(cx, cy, r - 16, r - 16, 60), (196, 182, 156), 2.4)
    hs = 30; holes = rot([(cx - hs, cy - hs), (cx + hs, cy - hs), (cx + hs, cy + hs), (cx - hs, cy + hs)], cx, cy, tilt)
    d = ImageDraw.Draw(L)
    for (hx, hy) in holes: d.ellipse([P(hx - 11, hy - 11), P(hx + 11, hy + 11)], fill=(14, 12, 12, 255))
    yarn(L, [holes[0], holes[2]], OXBLOOD, 9.0); yarn(L, [holes[1], holes[3]], OXBLOOD, 9.0)
    return L

def big_heart(f, FR=16):
    L = new_layer(); ph = TAU * f / FR
    pulse = 1.0 + 0.06 * max(0.0, math.sin(ph)) ** 2 + 0.03 * max(0.0, math.sin(ph * 2 + 0.6)) ** 4
    hp = G2.heart_pts(120, 118, 6.2 * pulse)
    yarn(L, hp + [hp[0]], OXBLOOD, 11.0)
    yarn(L, G2.heart_pts(120, 118, 3.6 * pulse) + [G2.heart_pts(120, 118, 3.6 * pulse)[0]], MUSTARD, 6.0)
    bigknot(L, 120, 122, 12, TEAL)
    return L

def big_moon(f, FR=16):
    L = new_layer(); ph = TAU * f / FR
    cx, cy, r = 112, 122, 94
    full = ellipse_mask(cx, cy, r, r); cut = ellipse_mask(cx + 54, cy - 18, r * 0.9, r * 0.9)
    moon = ImageChops.subtract(full, cut)
    satin(L, moon, MUSTARD, 35, spacing=1.6, sheen=0.3)
    out = ellipse_pts(cx, cy, r + 2, r + 2, 80, 0, math.radians(95), math.radians(400))
    yarn(L, out, SOOT, 3.0)
    for i, (sx, sy, sr) in enumerate([(186, 70, 9), (206, 140, 6), (176, 196, 7)]):
        tw = 0.7 + 0.3 * math.sin(ph + i * 2.1)
        for a in (0, math.pi / 2): yarn(L, [(sx - sr * tw * math.cos(a), sy - sr * tw * math.sin(a)), (sx + sr * tw * math.cos(a), sy + sr * tw * math.sin(a))], BONE, 3.5)
        bigknot(L, sx, sy, 4 * tw, BONE)
    return L

def big_bat(f, FR=16):
    L = new_layer(); ph = TAU * f / FR
    flap = 0.5 + 0.5 * math.sin(ph)
    wings, body = gen_linen.bat_poly(120, 118, 2.2, flap)
    satin(L, poly_mask(wings), SOOT, 0, spacing=1.4, sheen=0.12, blur=0)
    satin(L, poly_mask(body), SOOT, 90, spacing=1.4, sheen=0.12, blur=0)
    yarn(L, wings + [wings[0]], (70, 62, 64), 2.6)
    bigknot(L, 120 - 4, 118 - 15, 4, OXBLOOD); bigknot(L, 120 + 4, 118 - 15, 4, OXBLOOD)
    return L

def big_spider(f, FR=16):
    L = new_layer(); ph = TAU * f / FR
    yarn(L, [(120, -4), (120, 70 + 10 * math.sin(ph))], BONE, 3.0)
    sy = 70 + 10 * math.sin(ph); sx = 120
    bigknot(L, sx, sy + 46, 38, SOOT); bigknot(L, sx, sy + 2, 22, SOOT)
    bend = 0.25 * math.sin(ph)
    for s in (-1, 1):
        for (ex, ey) in ((78, -40), (92, -8), (88, 30), (70, 66)):
            a0 = (sx + s * 20, sy + 30); mid = rot([(sx + s * ex * 0.55, sy + 20 + ey * 0.4)], sx, sy + 30, bend * s)[0]; end = rot([(sx + s * ex, sy + 30 + ey)], sx, sy + 30, bend * s)[0]
            yarn(L, [a0, mid, end], SOOT, 6.0)
    bigknot(L, sx - 8, sy - 2, 5, OXBLOOD); bigknot(L, sx + 8, sy - 2, 5, OXBLOOD)
    return L

def big_ring_march(f, FR=16):
    L = new_layer(); ph = f / FR
    at, total = resample(ellipse_pts(120, 120, 100, 100, 160) + [ellipse_pts(120, 120, 100, 100, 160)[0]])
    period = 44; pos = -period + ph * period
    while pos < total:
        a = max(0, pos); b = min(total, pos + 26)
        if b > a: yarn(L, [at(a), at((a + b) / 2), at(b)], BONE, 9.0)
        pos += period
    bigknot(L, 120, 120, 30, OXBLOOD)
    return L

if __name__ == "__main__":
    pieces = []
    builds = [("big_x", big_x, lambda: bg_linen(31), "needle", 24), ("big_granny", big_granny, big_granny_bg, "hook", 24),
              ("big_toadstool", big_toadstool, lambda: bg_satin(32), "needle", 24), ("big_star", big_star, lambda: BLACK_BG, "needle", 24),
              ("big_spiral", big_spiral_build, lambda: BLACK_BG, "needle", 24)]
    for i, (name, fn, bgf, tool, FR) in enumerate(builds):
        random.seed(300 + i); gen_linen.FRAMES = FR
        pieces.append((name, gen_linen.render_events(name, fn(), bgf(), tool))); print(name)
    loops = [("big_button", big_button, lambda: BLACK_BG), ("big_heart", big_heart, lambda: bg_linen(33)), ("big_moon", big_moon, lambda: BLACK_BG),
             ("big_bat", big_bat, lambda: bg_satin(34, (242, 236, 222), 60)), ("big_spider", big_spider, lambda: bg_linen(35)), ("big_ring", big_ring_march, lambda: BLACK_BG)]
    for name, fn, bgf in loops:
        bg = bgf(); gen_linen.export_bg(name, bg); frames = []
        for f in range(16):
            img = compose_bg(fn(f), bg); img.save(f"{OUT}/{name}_{f:02d}.png"); frames.append(img)
        open(f"{OUT}/{name}.loop", "w").write("1\n"); pieces.append((name, frames)); print(name)
    seq = []
    for name, fr in pieces: seq += fr + [fr[-1]] * 6 if len(fr) > 16 else fr * 3
    seq[0].save(f"{OUT}/preview_bold.gif", save_all=True, append_images=seq[1:], duration=100, loop=0)
    # sheet: finished/mid state, shown at actual-ish size AND shrunk to simulate distance
    sheet = Image.new("RGB", (W * 6 + 70, W * 2 + 30 + 90), (40, 40, 40))
    for i, (name, fr) in enumerate(pieces[:11]):
        col = i % 6; rowb = i // 6
        im = fr[-1] if len(fr) > 16 else fr[4]
        sheet.paste(im, (10 + col * (W + 10), 10 + rowb * (W + 10)))
    for i, (name, fr) in enumerate(pieces):
        im = (fr[-1] if len(fr) > 16 else fr[4]).resize((70, 70), Image.LANCZOS)
        sheet.paste(im, (10 + i * 80, W * 2 + 35))
    sheet.save(f"{OUT}/sheet_bold.png")
    print("done")
