#!/usr/bin/env python3
"""Ten more embroidered eyes, each in a different needlework tradition.
usage: [EYES_OUT=eyes] python3 gen_eyes2.py [piece ...]
Exports eye_<name>_bg.png + eye_<name>_NN.png (+ .loop marker) for pack_delta.py, 128px thumbs/ and sets.json, for all twenty eyes."""
import math, random, sys, os, json
from multiprocessing import Pool
from gen_eyes import *
from gen_eyes import OUT
from PIL import Image, ImageDraw, ImageChops
from gen_insects2 import fuzz
from gen_stitch import stitch, needle, loop as thread_loop
from gen_granny import hook, circle_rounds
import gen_granny as GG
from gen_linen import bg_aida

RED, GOLD, THREAD, INDIGO = (176, 30, 40), (206, 166, 72), (238, 234, 222), (30, 44, 92)

def region(x, y, cx, cy, w, hu, hl, o, look, ir, pr):
    t = (x - cx + w) / (2 * w)
    if not 0 < t < 1: return "out"
    k = math.sin(math.pi * t) ** 0.75
    if y > cy + hl * k or y < cy - hu * k: return "out"
    if y < cy - (hu * o - hl * (1 - o)) * k: return "lid"
    d = math.hypot(x - cx - look[0], y - cy - look[1])
    return "pupil" if d < pr else "iris" if d < ir else "sclera"

def march(L, pts, col, dash=7, gap=4, w=1.9, off=0.0, keep=None):
    """Running stitch whose dashes travel along the path."""
    at, tot = resample(pts); per = dash + gap; pos = (off % per) - per
    while pos < tot:
        a, b = max(0, pos), min(tot, pos + dash)
        if b - a > 1.5:
            p, q = at(a), at(b)
            if keep is None or keep(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)): stitch(L, p, q, col, w)
        pos += per

def chain(L, pts, col, ln=8, wd=2.8, w=1.3, off=0.0):
    at, tot = resample(pts); st = ln * 0.85; pos = (off % st) - st
    while pos < tot:
        a, b = at(max(0, pos)), at(min(tot, pos + ln)); d = math.hypot(b[0] - a[0], b[1] - a[1])
        if d > 3: thread_loop(L, petal(a, math.atan2(b[1] - a[1], b[0] - a[0]), d * 1.1, wd, 10), col, w)
        pos += st

def felt(col, mask, seed):
    T = new_layer(); T.paste(col + (255,), (0, 0, N, N), mask); random.seed(seed)
    fuzz(T, mask, col, 2600, length=3.0, width=0.5, var=0.16, alpha=130)
    return T

def put_felt(L, T, mask):
    L.paste(Image.new("RGBA", (N, N), (0, 0, 0, 120)), (int(1.0 * S), int(1.6 * S)), mask); L.paste(T, (0, 0), mask)

def blanket(L, pts, col, depth=6, step=9, w=1.6, cx=120, cy=120):
    at, tot = resample(pts + [pts[0]]); n = max(3, int(tot / step)); prev = None
    for i in range(n + 1):
        p = at(tot * i / n); q = at(min(tot, tot * i / n + 0.5)); r = at(max(0, tot * i / n - 0.5))
        dx, dy = q[0] - r[0], q[1] - r[1]; m = math.hypot(dx, dy) or 1; nx, ny = -dy / m, dx / m
        if nx * (cx - p[0]) + ny * (cy - p[1]) < 0: nx, ny = -nx, -ny
        stitch(L, p, (p[0] + nx * depth, p[1] + ny * depth), col, w)
        if prev: stitch(L, prev, p, col, w)
        prev = p

# ------------------------------------------------------------------ 1 counted cross-stitch on aida
def cross_stitch(f, FR):
    L = new_layer(); random.seed(31); u = f / FR; ph = TAU * u
    o = blink(u, [0.5], 0.08); look = (8 * round(2.2 * math.sin(ph)), 0)
    R = lambda x, y: region(x, y, 124, 124, 92, 46, 38, o, look, 30, 12)
    def X(x, y, col):
        stitch(L, (x - 3, y + 3), (x + 3, y - 3), col, 1.9); stitch(L, (x - 3, y - 3), (x + 3, y + 3), col, 1.9)
    for gy in range(30):
        for gx in range(30):
            x, y = 4 + 8 * gx, 4 + 8 * gy; rr = math.hypot(x - 120, y - 120)
            if rr > 113: continue
            r = R(x, y)
            if r == "out":
                if 99 < rr < 108 and (gx + gy) % 2 == 0: X(x, y, (OXBLOOD, MUSTARD)[(gx + gy // 2 + int(u * 8)) % 2])
                if R(x, y + 8) != "out" and gx % 3 == 1 and y < 124: X(x, y - 8, SOOT); X(x, y, SOOT)   # lashes
                continue
            edge = any(R(x + ax, y + ay) == "out" for ax, ay in ((8, 0), (-8, 0), (0, 8), (0, -8)))
            if edge or (r == "lid" and R(x, y + 8) not in ("lid", "out")): X(x, y, SOOT); continue
            d = math.hypot(x - 124 - look[0], y - 124)
            col = {"lid": PLUM, "sclera": WHITE, "pupil": INK}.get(r) or (MUSTARD if d < 19 else TEAL if d < 25 else shade(TEAL, 0.62))
            if r == "pupil" and (x - 124 - look[0], y - 124) == (-8, -8): col = WHITE
            X(x, y, col)
    return L

# ------------------------------------------------------------------ 2 sashiko on indigo
def sashiko(f, FR):
    L = new_layer(); random.seed(32); u = f / FR; ph = TAU * u
    o = blink(u, [0.0], 0.1); look = (16 * math.sin(ph), 0); off = u * 22
    outer = lambda p: region(p[0], p[1], 120, 120, 110, 64 * o + 6, 54, 1, (0, 0), 0, 0) == "out" and math.hypot(p[0] - 120, p[1] - 120) < 113
    for j, y in enumerate(range(22, 222, 13)):
        march(L, [(4, y), (236, y)], THREAD, 7, 4, 1.8, off * (1 if j % 2 else -1) + j * 3, outer)
    for s, d in ((1.0, 1), (0.84, -1)):
        up, lo = almond(120, 120, 100 * s, (56 * o - 46 * (1 - o)) * s + (1 - s) * 30 * (1 - o), 46 * s)
        march(L, up + lo[::-1] + [up[0]], THREAD, 7, 4, 2.0, off * d)
    inner = lambda p: region(p[0], p[1], 120, 120, 80, 43, 35, o, (0, 0), 0, 0) == "sclera"
    c = (120 + look[0], 120)
    for r, col, d in ((33, THREAD, 1), (24, (222, 98, 62), -1), (15, THREAD, 1)):
        march(L, ellipse_pts(c[0], c[1], r, r, 60), col, 6, 3.5, 2.0, off * d, inner)
    if inner(c):
        stitch(L, (c[0] - 6, c[1]), (c[0] + 6, c[1]), THREAD, 2.2); stitch(L, (c[0], c[1] - 6), (c[0], c[1] + 6), THREAD, 2.2)
    return L

# ------------------------------------------------------------------ 3 blackwork: the pattern stays on the weave, the eye moves over it
def blackwork(f, FR):
    L = new_layer(); random.seed(33); u = f / FR; ph = TAU * u
    o = blink(u, [0.5], 0.09); cx, cy = 120 + 24 * math.sin(ph), 122
    fu, fl = almond(120, 120, 100, 54, 42); full = poly_mask(fu + fl[::-1])
    up, lo = almond(120, 120, 100, 54 * o - 42 * (1 - o), 42); opening = poly_mask(up + lo[::-1])
    irm, pum = ellipse_mask(cx, cy, 38, 38), ellipse_mask(cx, cy, 15, 15)
    ink = SOOT + (255,); wl = max(2, int(0.7 * S))
    A = new_layer(); d = ImageDraw.Draw(A)                     # octagon-and-star diaper
    for k in range(0, 241, 8):
        d.line([P(k, 0), P(k, 240)], fill=ink, width=wl); d.line([P(0, k), P(240, k)], fill=ink, width=wl)
    for k in range(-240, 481, 16):
        d.line([P(k, 0), P(k + 240, 240)], fill=ink, width=wl); d.line([P(k, 0), P(k - 240, 240)], fill=ink, width=wl)
    B = new_layer(); d = ImageDraw.Draw(B)                     # seeded crosses
    for j, y in enumerate(range(6, 240, 9)):
        for x in range(6 + (j % 2) * 6, 240, 12):
            d.line([P(x - 2.2, y), P(x + 2.2, y)], fill=ink, width=wl); d.line([P(x, y - 2.2), P(x, y + 2.2)], fill=ink, width=wl)
    C = new_layer(); d = ImageDraw.Draw(C)                     # hatch for the lid
    for k in range(-240, 481, 5): d.line([P(k, 0), P(k + 240, 240)], fill=ink, width=wl)
    for k in range(-240, 481, 15): d.line([P(k, 0), P(k - 240, 240)], fill=ink, width=wl)
    iris_m = ImageChops.multiply(irm, opening)
    for T, m in ((B, ImageChops.subtract(opening, irm)), (A, ImageChops.subtract(iris_m, pum)), (C, ImageChops.subtract(full, opening))):
        L.paste(T, (0, 0), ImageChops.multiply(m, T.split()[3]))
    T = new_layer(); satin(T, pum, SOOT, 20, spacing=1.3, sheen=0.2, shadow=False); L.paste(T, (0, 0), ImageChops.multiply(opening, T.split()[3]))
    T = new_layer(); backstitch(T, ellipse_pts(cx, cy, 38, 38, 60), SOOT, width=2.2, dash=5, gap=1)
    for k in range(8): knot(T, cx + 27 * math.cos(TAU * k / 8), cy + 27 * math.sin(TAU * k / 8), 2.6, MUSTARD)
    knot(T, cx - 6, cy - 6, 2.4, WHITE); L.paste(T, (0, 0), ImageChops.multiply(opening, T.split()[3]))
    backstitch(L, fu, SOOT, width=1.6, dash=4, gap=1.2); backstitch(L, lo, SOOT, width=2.4, dash=6, gap=1); backstitch(L, up, SOOT, width=3.0, dash=6, gap=1)
    for k in range(9):
        t = 0.14 + 0.72 * k / 8; b = fu[int(t * 40)]; a = (t - 0.5) * 1.5
        stitch(L, b, (b[0] + 15 * math.sin(a), b[1] - 15 * math.cos(a)), SOOT, 1.6)
        knot(L, b[0] + 18 * math.sin(a), b[1] - 18 * math.cos(a), 1.9, MUSTARD)
    return L

# ------------------------------------------------------------------ 4 redwork: one red thread, sewn as you watch
_cache = {}
def redwork_paths():
    up, lo = almond(120, 128, 94, 50, 38); paths = [up, lo[::-1], ellipse_pts(120, 126, 33, 33, 48)]
    paths += [[(120 + r0 * math.cos(a), 126 + r0 * math.sin(a)), (120 + 29 * math.cos(a), 126 + 29 * math.sin(a))]
              for a, r0 in ((TAU * k / 18, 17 + 4 * (k % 2)) for k in range(18))]
    sp = []; th = 0.0
    while th < TAU * 3.2: r = 13 - 13 * th / (TAU * 3.2); sp.append((120 + r * math.cos(th), 126 + r * math.sin(th))); th += 0.3
    paths.append(sp)
    paths.append(almond(120, 122, 100, 66, 0)[0][5:36])
    paths.append([(36 + i * 8.4, 50 + 0.04 * (i - 6) ** 2 - 12 * math.sin(math.pi * i / 20)) for i in range(21)])
    for k in range(9):
        t = 0.12 + 0.76 * k / 8; b = up[int(t * 40)]; a = (t - 0.5) * 1.6; ln = 13 + 6 * math.sin(math.pi * t)
        paths.append([b, (b[0] + ln * 0.5 * math.sin(a) * 0.8, b[1] - ln * 0.55 * math.cos(a)), (b[0] + ln * math.sin(a), b[1] - ln * math.cos(a))])
    for k in range(5):
        t = 0.25 + 0.5 * k / 4; b = lo[int(t * 40)]; a = (t - 0.5) * 1.2
        paths.append([b, (b[0] + 8 * math.sin(a), b[1] + 8 * math.cos(a))])
    for sx, sy in ((38, 176), (198, 182), (120, 204)):
        for a in (0, TAU / 6, TAU / 3): paths.append([(sx - 7 * math.cos(a), sy - 7 * math.sin(a)), (sx + 7 * math.cos(a), sy + 7 * math.sin(a))])
    st = []
    for p in paths:
        at, tot = resample(p); pos = 0.0
        while pos < tot - 0.5: st.append((at(pos), at(min(tot, pos + 5.5)))); pos += 6.3
    return st

def redwork(f, FR):
    if f == 0: _cache["red"] = (new_layer(), redwork_paths(), 0); random.seed(34)
    L, st, done = _cache["red"]; u = min(1.0, (f + 1) / (FR * 0.8)); target = int(len(st) * (0.5 - 0.5 * math.cos(u * math.pi)))
    while done < target: stitch(L, st[done][0], st[done][1], RED, 1.8); done += 1
    _cache["red"] = (L, st, done); F = L.copy()
    if 0 < done < len(st): a, b = st[done - 1]; needle(F, b, (b[0] - a[0], b[1] - a[1]), RED)
    elif done: knot(F, 109, 115, 4.0 * min(1, (f - FR * 0.8) / 3 + 0.4), WHITE)
    return F

# ------------------------------------------------------------------ 5 goldwork on black velvet
def goldwork(f, FR):
    L = new_layer(); random.seed(35); u = f / FR; ph = TAU * u
    for k in range(32):
        a = TAU * k / 32; r0, r1 = (88, 112) if k % 2 else (94, 106)
        b = 0.62 + 0.75 * max(0, math.sin(ph - k * TAU * 2 / 32)) ** 3
        e = lambda r: (120 + r * math.cos(a), 120 + r * 0.92 * math.sin(a))
        if abs(math.sin(a)) > 0.34 or k % 2: yarn(L, [e(r0), e(r1)], shade(GOLD, b), 2.6)
    d = ImageDraw.Draw(L)
    for k in range(14):
        a = TAU * k / 14 + 0.22; x, y = 120 + 80 * math.cos(a), 120 + 66 * math.sin(a)
        if abs(y - 120) < 34: continue
        b = 0.7 + 0.8 * max(0, math.sin(ph * 2 + k * 2.4)) ** 4
        d.ellipse([P(x - 5.2, y - 4.4), P(x + 6.2, y + 6.6)], fill=(0, 0, 0, 160))
        d.ellipse([P(x - 5.6, y - 5.6), P(x + 5.6, y + 5.6)], fill=shade(GOLD, b * 0.8) + (255,))
        d.ellipse([P(x - 4.6, y - 5.0), P(x + 3.8, y + 3.4)], fill=shade(GOLD, b) + (255,))
        d.ellipse([P(x - 1.2, y - 1.2), P(x + 1.2, y + 1.2)], fill=INK + (255,))
        stitch(L, (x, y), (x + 5.4 * math.cos(a), y + 5.4 * math.sin(a)), OXBLOOD, 1.0)
    o = blink(u, [0.5], 0.08); c = (120 + 18 * math.sin(ph), 120)
    def inner(E):
        satin(E, ellipse_mask(c[0], c[1], 30, 30), (18, 112, 96), 360 * u, spacing=1.3, sheen=0.55, shadow=False, var=0.2)
        for k in range(20): knot(E, c[0] + 30 * math.cos(TAU * k / 20), c[1] + 30 * math.sin(TAU * k / 20), 2.5, GOLD)
        ImageDraw.Draw(E).ellipse([P(c[0] - 12, c[1] - 12), P(c[0] + 12, c[1] + 12)], fill=INK + (255,))
        knot(E, c[0] - 9, c[1] - 10, 4.2, WHITE)
    up, lo = eye(L, 120, 120, 78, 42, 34, o, scl=(196, 198, 206), line=GOLD, lw=5.6, inner=inner)
    for crv in (up, lo):                                      # couching stitches over the gold cord
        for i in range(3, 38, 3):
            p, q = crv[i - 1], crv[i + 1]; dx, dy = q[0] - p[0], q[1] - p[1]; m = math.hypot(dx, dy) or 1
            x, y = crv[i]; stitch(L, (x - dy / m * 2.6, y + dx / m * 2.6), (x + dy / m * 2.6, y - dx / m * 2.6), OXBLOOD, 0.9)
    return L

# ------------------------------------------------------------------ 6 crewel chain stitch
def chain_eye(f, FR):
    L = new_layer(); random.seed(36); u = f / FR; ph = TAU * u; off = u * 6.8 * 3
    up, lo = almond(120, 124, 100, 56, 46)
    T = new_layer(); satin(T, poly_mask(up + lo[::-1]), WHITE, 10, spacing=1.6, sheen=0.12, shadow=False, var=0.05); L.paste(T, (0, 0), T)
    c = (120 + 12 * math.sin(ph), 124 + 2 * math.sin(2 * ph))
    for r, col, d in ((38, RUST, 1), (30, MUSTARD, -1), (22, TEAL, 1), (14, SKY, -1)):
        chain(L, ellipse_pts(c[0], c[1], r, r, 48), col, 8, 3.0, 1.5, off * d)
    bigknot(L, c[0], c[1], 8, SOOT); knot(L, c[0] - 3, c[1] - 3, 2.4, WHITE)
    iu, il = almond(120, 124, 91, 48, 38)
    chain(L, iu + il[::-1] + [iu[0]], PLUM, 8, 2.8, 1.4, -off)
    chain(L, up + lo[::-1] + [up[0]], OXBLOOD, 9, 3.2, 1.6, off)
    for k in range(7):
        t = 0.14 + 0.72 * k / 6; b = up[int(t * 40)]; a = (t - 0.5) * 1.5 + 0.16 * math.sin(ph + k * 0.9)
        pts = [(b[0] + s * math.sin(a + 0.5 * (s / 26) ** 2 * (1 if t > 0.5 else -1)), b[1] - s * math.cos(a + 0.5 * (s / 26) ** 2)) for s in range(0, 27, 3)]
        chain(L, pts, SAGE, 7, 2.4, 1.3); knot(L, pts[-1][0], pts[-1][1], 3.0, MUSTARD)
    return L

# ------------------------------------------------------------------ 7 French-knot pointillism
def knots(f, FR):
    L = new_layer(); random.seed(37); u = f / FR; ph = TAU * u
    o = blink(u, [0.75], 0.09); look = (24 * math.sin(ph), 6 * math.sin(ph * 2))
    for j in range(30):
        for i in range(27):
            x, y = 3 + 9 * i + (4.5 if j % 2 else 0), 6 + 7.8 * j
            if math.hypot(x - 120, y - 120) > 112: continue
            r = region(x, y, 120, 120, 98, 54, 44, o, look, 35, 14); h = (i * 7 + j * 13) % 11
            if r == "out":
                if h == 0: knot(L, x, y, 1.4 + 1.3 * max(0, math.sin(ph * 2 + i + j * 1.7)), BONE)
                continue
            d = math.hypot(x - 120 - look[0], y - 120 - look[1])
            col = {"lid": PLUM, "sclera": BONE, "pupil": (58, 52, 60)}.get(r) or (MUSTARD if d < 23 else TEAL if d < 30 else shade(TEAL, 0.62))
            knot(L, x, y, 3.9, shade(col, 0.9 + 0.02 * h))
    if o > 0.55: knot(L, 120 + look[0] - 10, 120 + look[1] - 11, 5.0, WHITE)
    return L

# ------------------------------------------------------------------ 8 felt applique with blanket stitch
def applique(f, FR):
    L = new_layer(); u = f / FR; ph = TAU * u
    o = 1 - 0.92 * (1 - blink(u, [0.5], 0.11)); c = (120 + 16 * math.sin(ph), 126 + 4 * math.cos(ph))
    fu, fl = almond(120, 122, 102, 62, 50, p=0.62); fullp = fu + fl[::-1]; full = poly_mask(fullp)
    up, lo = almond(120, 122, 102, 62 * o - 50 * (1 - o), 50, p=0.62); opening = poly_mask(up + lo[::-1])
    put_felt(L, felt(WHITE, full, 1), full)
    E = new_layer(); im = ellipse_mask(c[0], c[1], 37, 37); put_felt(E, felt(TEAL, im, 2), im); random.seed(38)
    blanket(E, ellipse_pts(c[0], c[1], 37, 37, 60)[:-1], MUSTARD, 7, 9, 1.7, c[0], c[1])
    pm = ellipse_mask(c[0], c[1], 16, 16); put_felt(E, felt(SOOT, pm, 3), pm)
    march(E, ellipse_pts(c[0], c[1], 12, 12, 30), BONE, 3.5, 3, 1.3); knot(E, c[0] - 6, c[1] - 7, 3.6, WHITE)
    L.paste(E, (0, 0), ImageChops.multiply(opening, E.split()[3]))
    lidm = ImageChops.subtract(full, opening); put_felt(L, felt(OXBLOOD, full, 4), lidm); random.seed(39)
    if o < 0.9:
        march(L, [(q[0], q[1] - 5) for q in up[4:37]], MUSTARD, 5, 4, 1.6)
        if o < 0.45:
            for x, y in ((92, 92), (150, 98)): stitch(L, (x - 5, y - 5), (x + 5, y + 5), BONE, 1.8); stitch(L, (x - 5, y + 5), (x + 5, y - 5), BONE, 1.8)
    blanket(L, fullp, SOOT, 7, 10, 1.9, 120, 122)
    for k in range(6):
        t = 0.16 + 0.68 * k / 5; b = fu[int(t * 40)]; a = (t - 0.5) * 1.5
        yarn(L, [b, (b[0] + 17 * math.sin(a), b[1] - 17 * math.cos(a))], SOOT, 3.2)
    return L

# ------------------------------------------------------------------ 9 crochet: an amigurumi eye worked in the round
def crochet(f, FR):
    pal = [(64, 58, 66), (64, 58, 66), TEAL, SKY, CREAM, CREAM, OXBLOOD]
    if f == 0: _cache["cro"] = (new_layer(), circle_rounds(6, step=14, r0=11, palette=pal), 0); random.seed(40)
    L, ev, done = _cache["cro"]; u = min(1.0, (f + 1) / (FR * 0.8)); target = int(len(ev) * (0.5 - 0.5 * math.cos(u * math.pi))); last = None
    while done < target: last = GG.run_event(L, ev[done]) or last; done += 1
    _cache["cro"] = (L, ev, done); F = L.copy()
    if done < len(ev):
        if last: hook(F, *last)
    else:
        g = min(1.0, (f - FR * 0.8 + 1) / 3); knot(F, 111, 110, 6.5 * g, WHITE)
        for k in range(9):
            a = -math.pi / 2 + (k - 4) * 0.2; b = (120 + 95 * math.cos(a), 120 + 95 * math.sin(a))
            yarn(F, petal(b, a, 15 * g + 1, 4.5), CREAM, 2.2)
    return F

# ------------------------------------------------------------------ 10 string art: thread wound between pins
def string_art(f, FR):
    L = new_layer(); random.seed(41); u = f / FR; ph = TAU * u; d = ImageDraw.Draw(L)
    n = 56; up, lo = almond(120, 120, 108, 66, 66, n)
    def at(c, t):
        t = max(0.0, min(1.0, t)) * n; i = min(n - 1, int(t)); fr = t - i
        return (c[i][0] + (c[i + 1][0] - c[i][0]) * fr, c[i][1] + (c[i + 1][1] - c[i][1]) * fr)
    s = 0.3 + 0.08 * math.sin(ph)
    for col, sg in ((MUSTARD, 1), (OXBLOOD, -1)):
        for i in range(n + 1):
            t = i / n; t2 = t + sg * s
            if 0 <= t2 <= 1: d.line([P(*up[i]), P(*at(lo, t2))], fill=shade(col, 1 + random.uniform(-0.15, 0.2)) + (235,), width=3)
    d.ellipse([P(120 - 47, 120 - 47), P(120 + 47, 120 + 47)], fill=(12, 10, 10, 255))
    R = 45; m = 64
    for col, dl, rt in ((TEAL, math.pi * (0.66 + 0.2 * math.sin(ph)), ph / m * 0), (SKY, math.pi * (0.42 + 0.14 * math.sin(ph + 1.2)), TAU / m / 2)):
        for i in range(m):
            a = TAU * i / m + rt
            d.line([P(120 + R * math.cos(a), 120 + R * math.sin(a)), P(120 + R * math.cos(a + dl), 120 + R * math.sin(a + dl))],
                   fill=shade(col, 1 + random.uniform(-0.15, 0.2)) + (235,), width=3)
    for i in range(0, m, 2): knot(L, 120 + R * math.cos(TAU * i / m), 120 + R * math.sin(TAU * i / m), 1.5, (200, 204, 210))
    for c in (up, lo):
        for i in range(0, n + 1, 2): knot(L, c[i][0], c[i][1], 1.7, (200, 204, 210))
    bigknot(L, 120, 120, 5 + 1.5 * math.sin(ph), MUSTARD)
    return L

PIECES2 = {
    "cross_stitch": (cross_stitch, 32, 90, lambda: bg_aida(51)),
    "sashiko":      (sashiko,      32, 80, lambda: bg_linen(52, INDIGO)),
    "blackwork":    (blackwork,    32, 80, lambda: bg_linen(53, (236, 230, 214))),
    "redwork":      (redwork,      60, 90, lambda: bg_linen(54, (238, 232, 216))),
    "goldwork":     (goldwork,     32, 80, lambda: BLACK_BG),
    "chain_eye":    (chain_eye,    32, 80, lambda: bg_linen(55)),
    "knots":        (knots,        32, 80, lambda: BLACK_BG),
    "applique":     (applique,     32, 80, lambda: bg_linen(56, (150, 164, 122))),
    "crochet":      (crochet,      64, 90, lambda: BLACK_BG),
    "string_art":   (string_art,   32, 80, lambda: BLACK_BG),
}

CIRCLE = Image.new("L", (W, W), 0); ImageDraw.Draw(CIRCLE).ellipse([0, 0, W - 1, W - 1], fill=255)
BUILDS = ("redwork", "crochet")                        # sewn once and held; everything else loops
def out_name(key): return "eye_" + key.replace("_eye", "")

ALL = {k: v + ("eyes",) for k, v in PIECES.items()}; ALL.update({k: v + ("eyes-crafts",) for k, v in PIECES2.items()})

def render(key):
    fn, FR, dur, bgf, _ = ALL[key]; bg = bgf(); name = out_name(key)
    Image.composite(bg.resize((W, W), Image.LANCZOS), Image.new("RGB", (W, W), (0, 0, 0)), CIRCLE).save(f"{OUT}/{name}_bg.png")
    frames = [compose_bg(fn(f, FR), bg) for f in range(FR)]
    for f, im in enumerate(frames): im.save(f"{OUT}/{name}_{f:02d}.png")
    if key not in BUILDS: open(f"{OUT}/{name}.loop", "w").write("1\n")
    th = [im.resize((128, 128), Image.LANCZOS) for im in frames]
    (th[-1] if key in BUILDS else th[FR // 4]).save(f"{OUT}/thumbs/{name}.png")
    th[0].save(f"{OUT}/thumbs/{name}.gif", save_all=True, append_images=th[1:] + ([th[-1]] * 12 if key in BUILDS else []), duration=dur, loop=0)
    return name

def main(keys):
    os.makedirs(f"{OUT}/thumbs", exist_ok=True)
    with Pool(min(8, len(keys))) as pool: names = pool.map(render, keys)
    sj = f"{OUT}/sets.json"; sets = json.load(open(sj)) if os.path.exists(sj) else {}
    sets.update({out_name(k): ALL[k][4] for k in keys}); json.dump(sets, open(sj, "w"), indent=1)
    print("done", names)

if __name__ == "__main__": main(sys.argv[1:] or list(ALL))
