#!/usr/bin/env python3
"""Fifty more on-theme pieces in seven families. Build pieces sew live; loop pieces cycle."""
import math, random, os
from PIL import Image, ImageDraw, ImageChops
from gen_insects2 import P, S, N, W, shade, knot, ellipse_pts, ellipse_mask, poly_mask, rect_mask, new_layer, satin, backstitch, sm, leaf, daisy
from gen_stitch import stitch, loop as thread_loop, needle, resample
from gen_granny import yarn, post, hook, square_rounds, circle_rounds, MUSTARD, OXBLOOD, TEAL, CREAM, SOOT, PLUM, RUST, SAGE, PALETTE
from gen_linen import bg_linen, bg_satin, bg_aida, BLACK_BG, compose_bg, path_events, cross
from gen_wagara import dashes, fill, inside, INDIGO, VERM, INDIGO_L, bg_indigo, bg_cream
from gen_bold import bigknot, rot
import gen_linen, gen_granny2 as G2

OUT = "/home/claude/eye_pin_lowpower/fifty"
os.makedirs(OUT, exist_ok=True)
gen_linen.OUT = OUT
TAU = 2 * math.pi
BONE, CHAR = (236, 226, 204), (112, 104, 112)
ORANGE, LEAF, BROWN, SNOW = (214, 112, 40), (96, 134, 72), (92, 62, 40), (246, 244, 240)

def fn_ev(f, endpt=(120, 120), col=CREAM): return ("fn", f, endpt, col)
def satin_ev(poly, col, ang, sp=1.5, clip=120):
    m = ImageChops.multiply(poly_mask(poly), ellipse_mask(120, 120, clip, clip))
    return fn_ev(lambda L, m=m: satin(L, m, col, ang, spacing=sp, sheen=0.25), poly[0], col)
def outline_ev(poly, col, w=1.4, step=5.0): return path_events(poly + [poly[0]], col, w, step)
def run_ev(pts, col, w=1.5, dash=4.0, gap=2.5):
    ev = []; at, total = resample(pts); pos = 0
    while pos < total: ev.append(("stitch", at(pos), at(min(total, pos + dash)), col, w)); pos += dash + gap
    return ev

# =================================================================== A. sashiko (indigo)
def seigaiha_indigo():
    ev = []; R = 34
    for ri, cy in enumerate(range(0, 262, R // 2)):
        off = 0 if ri % 2 == 0 else R
        for cx in range(-R + off, 264 + R, 2 * R):
            if math.hypot(cx - 120, cy - 120) > 120 + R: continue
            ev.append(("fillpoly", ellipse_pts(cx, cy, R, R, 40), (34, 46, 86)))
            for k, r in enumerate((R - 3, R - 12, R - 21)):
                ev += dashes(ellipse_pts(cx, cy, r, r, 30, 0, math.pi, TAU), CREAM if k else VERM, 2.6, 6, 2.5)
    return ev

def asanoha_indigo():
    ev = []; a = 44.0; h = a * math.sqrt(3) / 2
    for fam in range(3):
        ang = math.radians(60 * fam); dx, dy = math.cos(ang), math.sin(ang)
        for k in range(-6, 7):
            px, py = (120, 120 + k * h) if fam == 0 else (120 + k * a, 120)
            seg = G2.chord(px, py, dx, dy, 118)
            if seg: ev += dashes([seg[0], seg[1]], CREAM, 2.6, 7, 3)
    for j in range(-4, 5):
        for i in range(-7, 7):
            p = lambda ii, jj: (120 + a * (ii + jj / 2), 120 + jj * h)
            for tri in ([p(i, j), p(i + 1, j), p(i, j + 1)], [p(i + 1, j), p(i, j + 1), p(i + 1, j + 1)]):
                gx = sum(q[0] for q in tri) / 3; gy = sum(q[1] for q in tri) / 3
                if inside(gx, gy, 110):
                    for v in tri: ev.append(("stitch", (gx, gy), v, VERM, 2.2))
    return ev

def kaki_no_hana():
    ev = []; c = 40
    for k in range(-3, 4):
        ev += dashes([(120 + k * c, -10), (120 + k * c, 250)], CREAM, 2.4, 7, 3); ev += dashes([(-10, 120 + k * c), (250, 120 + k * c)], CREAM, 2.4, 7, 3)
    for i in range(-3, 3):
        for j in range(-3, 3):
            cx, cy = 120 + i * c + c / 2, 120 + j * c + c / 2
            if not inside(cx, cy, 108): continue
            for (dx, dy) in ((1, 0), (0, 1)):
                ev.append(("stitch", (cx - dx * 14, cy - dy * 14), (cx + dx * 14, cy + dy * 14), VERM, 2.6))
            for (ox, oy) in ((-8, -8), (8, -8), (8, 8), (-8, 8)): ev.append(("stitch", (cx + ox * 0.5, cy + oy * 0.5), (cx + ox * 1.3, cy + oy * 1.3), CREAM, 2.0))
    return ev

def juji_tsunagi():
    ev = []; c = 30
    for i in range(-5, 5):
        for j in range(-5, 5):
            if (i + j) % 2: continue
            cx, cy = 120 + i * c + c / 2, 120 + j * c + c / 2
            if not inside(cx, cy, 112): continue
            col = CREAM if (i // 2 + j // 2) % 2 == 0 else VERM
            ev.append(("stitch", (cx - c / 2 + 2, cy), (cx + c / 2 - 2, cy), col, 3.0)); ev.append(("stitch", (cx, cy - c / 2 + 2), (cx, cy + c / 2 - 2), col, 3.0))
    return ev

def fundo():
    ev = []; r = 40; s = r * 2
    cs = []
    for i in range(-3, 4):
        for j in range(-3, 4): cs += [(120 + i * s, 120 + j * s), (120 + i * s + r, 120 + j * s + r)]
    cs = [c for c in cs if math.hypot(c[0] - 120, c[1] - 120) < 118 + r]
    for (cx, cy) in cs:
        for k in range(4):
            a0 = math.radians(90 * k + 45 - 40); a1 = math.radians(90 * k + 45 + 40)
            arc = ellipse_pts(cx + r * 1.3 * math.cos(math.radians(90 * k + 45)), cy + r * 1.3 * math.sin(math.radians(90 * k + 45)), r * 0.95, r * 0.95, 20, 0, a0 + math.pi, a1 + math.pi)
            ev += dashes(arc, CREAM, 2.6, 6, 2.5)
    for (cx, cy) in cs:
        if inside(cx, cy, 108): ev.append(("knot", cx, cy, 3.0, VERM))
    return ev

def nowaki():
    ev = []
    for row, cy in enumerate(range(260, -40, -34)):
        for cx in range(-20 + (row % 2) * 34, 280, 68):
            if math.hypot(cx - 120, cy - 120) > 170: continue
            for k, r in enumerate((30, 22, 14)):
                ev += dashes(ellipse_pts(cx, cy, r, r, 24, 0, math.radians(200), math.radians(340)), CREAM if k != 1 else VERM, 2.4, 6, 2.5)
    return ev

# =================================================================== B. cross-stitch motifs (aida)
MOTIFS = {
    "skull_x": (["....WWWWWWW....", "..WWWWWWWWWWW..", ".WWWWWWWWWWWWW.", ".WWWWWWWWWWWWW.", "WWWWWWWWWWWWWWW", "WWSSSWWWWWSSSWW", "WSSSSSWWWSSSSSW", "WSSSSSWWWSSSSSW", "WWSSSWWRWWSSSWW", ".WWWWWRRRWWWWW.", ".WWWWWWRWWWWWW.", "..WWWWWWWWWWW..", "...WSWSWSWSW...", "...WWWWWWWWW...", "....SWSWSWS...."], {"W": BONE, "S": SOOT, "R": OXBLOOD}, bg_indigo),
    "pumpkin_x": ([".......G.......", "......GG.......", "....OOOOOOO....", "..OOOOOOOOOOO..", ".OOOOOOOOOOOOO.", ".OOSSOOOOOSSOO.", "OOOSSSOOOSSSOOO", "OOOOOOOSOOOOOOO", "OOOOOOSSSOOOOOO", "OOSOOOOOOOOOSOO", "OOSSOOOOOOOSSOO", ".OOSSSSSSSSSOO.", ".OOOOSSSSSOOOO.", "..OOOOOOOOOOO..", "....OOOOOOO...."], {"O": ORANGE, "S": SOOT, "G": LEAF}, bg_aida),
    "cat_x": (["..S.........S..", "..SS.......SS..", "..SSS.....SSS..", "..SSSSSSSSSSS..", "..SSSSSSSSSSS..", "..SMSSSSSSSMS..", "..SSSSSSSSSSS..", "..SSSSSRSSSSS..", "...SSSSSSSSS...", "....SSSSSSS....", "...SSSSSSSSS...", "..SSSSSSSSSSS..", "..SSSSSSSSSSS..", "..SSS.SSS.SSS..", "..SSS.SSS.SSSS."], {"S": SOOT, "M": MUSTARD, "R": OXBLOOD}, bg_aida),
    "moth_x": (["...S.......S...", "....S.....S....", ".....S...S.....", "PPP...SSS...PPP", "PPPPP.SSS.PPPPP", "PPPPPPSSSPPPPPP", "PPCPPPSSSPPPCPP", "PPPPPPSSSPPPPPP", ".PPPPPSSSPPPPP.", "..PPPPSSSPPPP..", "...PPPSSSPPP...", "....PPSSSPP....", ".....PPSPP.....", "......PSP......", ".......P......."], {"P": PLUM, "S": SOOT, "C": CREAM}, bg_aida),
    "teapot_x": (["......TTT......", ".....TTTTT.....", "...TTTTTTTTT...", "..TTTTTTTTTTT..", "T.TTTTTTTTTTT.T", "TTTTTTTTTTTTTTT", "T.TTTRRTTTTTT.T", "T.TTTRRTTTTTT.T", "T.TTTTTTTTTTT.T", "TT.TTTTTTTTT.TT", "...TTTTTTTTT...", "....TTTTTTT....", ".....TTTTT.....", "....TTTTTTT....", "...TTTTTTTTT..."], {"T": TEAL, "R": OXBLOOD}, bg_aida),
    "acorn_x": (["......B........", ".....BB........", "....BBBBBBB....", "...BBBBBBBBB...", "..BBBBBBBBBBB..", "..BBBBBBBBBBB..", "..BBBBBBBBBBB..", "...MMMMMMMMM...", "...MMMMMMMMM...", "...MMMMMMMMM...", "....MMMMMMM....", "....MMMMMMM....", ".....MMMMM.....", "......MMM......", ".......M......."], {"B": BROWN, "M": MUSTARD}, bg_aida),
    "snowflake_x": ([".......W.......", "...W...W...W...", "....W..W..W....", ".....W.W.W.....", "..W...WWW...W..", "...WW.WWW.WW...", "....WWWWWWW....", "WWWWWWWWWWWWWWW", "....WWWWWWW....", "...WW.WWW.WW...", "..W...WWW...W..", ".....W.W.W.....", "....W..W..W....", "...W...W...W...", ".......W......."], {"W": SNOW}, bg_indigo),
    "bee_x": (["....W.....W....", "...WWW...WWW...", "...WWWW.WWWW...", "....WWWWWWW....", ".....SSSSS.....", "....SSSSSSS....", "...MMMMMMMMM...", "...MMMMMMMMM...", "...SSSSSSSSS...", "...MMMMMMMMM...", "...SSSSSSSSS...", "....MMMMMMM....", ".....SSSSS.....", "......SSS......", ".......S......."], {"W": CREAM, "S": SOOT, "M": MUSTARD}, bg_aida),
}
def motif(name):
    rows, cols, _ = MOTIFS[name]; ev = []; c = 13; ox = 120 - c * len(rows[0]) / 2; oy = 120 - c * len(rows) / 2
    for ch in cols:
        for j, row in enumerate(rows):
            cells = [i for i, x in enumerate(row) if x == ch]
            for i in cells: ev.append(("stitch", (ox + i * c + 1.5, oy + j * c + c - 1.5), (ox + i * c + c - 1.5, oy + j * c + 1.5), cols[ch], 2.6))
            for i in reversed(cells): ev.append(("stitch", (ox + i * c + 1.5, oy + j * c + 1.5), (ox + i * c + c - 1.5, oy + j * c + c - 1.5), cols[ch], 2.6))
    return ev

# =================================================================== C. granny family
def granny_sunburst():
    ev = circle_rounds(3, step=16, r0=12, palette=[MUSTARD, OXBLOOD, TEAL, CREAM])
    ev += square_rounds(2, step=16, inner0=66, palette=[PLUM, PLUM, SAGE], start_col=0)[1:]
    return ev
def granny_stripes():
    ev = []
    for row, y in enumerate(range(-6, 250, 18)):
        col = PALETTE[row % len(PALETTE)]
        for x in range(-10, 260, 12):
            if inside(x, y + 8, 124):
                for o in (-3.6, 0, 3.6): ev.append(("yarn", post((x, y + 16), (x + o, y)), col, 3.0))
    return ev
def granny_triangle():
    ev = [("ring", (120, 132), 8, MUSTARD)]
    for n in range(1, 5):
        col = PALETTE[n % len(PALETTE)]; Ri = 12 + 22 * (n - 1); Ro = Ri + 20
        for side in range(3):
            a0 = math.radians(-90 + 120 * side); a1 = math.radians(-90 + 120 * (side + 1))
            pi0 = (120 + Ri * math.cos(a0), 132 + Ri * math.sin(a0)); pi1 = (120 + Ri * math.cos(a1), 132 + Ri * math.sin(a1))
            po0 = (120 + Ro * math.cos(a0), 132 + Ro * math.sin(a0)); po1 = (120 + Ro * math.cos(a1), 132 + Ro * math.sin(a1))
            per = n + 1
            for k in range(per):
                t = (k + 0.5) / per
                base = (pi0[0] + (pi1[0] - pi0[0]) * t, pi0[1] + (pi1[1] - pi0[1]) * t)
                top = (po0[0] + (po1[0] - po0[0]) * t, po0[1] + (po1[1] - po0[1]) * t)
                dx, dy = po1[0] - po0[0], po1[1] - po0[1]; ln = math.hypot(dx, dy); dx, dy = dx / ln, dy / ln
                for o in (-3.6, 0, 3.6): ev.append(("yarn", post(base, (top[0] + dx * o, top[1] + dy * o)), col, 3.0))
            ev.append(("yarn", [po1, (120 + (Ro + 5) * math.cos(a1), 132 + (Ro + 5) * math.sin(a1)), po1], col, 2.4))
    return ev
def granny_heart():
    ev = []
    for n, (s, col) in enumerate(((2.0, MUSTARD), (3.4, OXBLOOD), (4.8, TEAL), (6.2, CREAM))):
        hp = G2.heart_pts(120, 118, s, 60); inner = G2.heart_pts(120, 118, s - 1.2 if n else 0.6, 60)
        for k in range(0, 60, 2 if n else 4):
            for o in (-1, 0, 1):
                kk = (k + o) % 60
                ev.append(("yarn", post(inner[k], hp[kk]), col, 3.0))
    return ev
def granny_flower():
    ev = []
    for k in range(8):
        a = TAU * k / 8; pts = ellipse_pts(120 + 22 * math.cos(a), 120 + 22 * math.sin(a), 16, 9, 20, a)
        ev.append(("yarn", pts + [pts[0]], OXBLOOD, 4.5))
    ev.append(("fn", lambda L: bigknot(L, 120, 120, 12, MUSTARD), (120, 120), MUSTARD))
    ev += circle_rounds(2, step=16, r0=44, palette=[SAGE, SAGE, TEAL])[1:]
    ev += square_rounds(1, step=16, inner0=78, palette=[PLUM, PLUM])[1:]
    return ev
def granny_ripple_round():
    ev = []
    for n in range(1, 7):
        col = PALETTE[n % len(PALETTE)]; r = 10 + n * 17
        pts = [(120 + (r + (7 if k % 2 else -7)) * math.cos(TAU * k / 24), 120 + (r + (7 if k % 2 else -7)) * math.sin(TAU * k / 24)) for k in range(25)]
        for a, b in zip(pts, pts[1:]): ev.append(("yarn", [a, b], col, 4.4))
    return ev

# =================================================================== D. Burton
def burton_tree():
    ev = []
    def branch(x, y, ang, ln, w, depth):
        nonlocal ev
        if depth == 0 or ln < 6: return
        ex, ey = x + ln * math.cos(ang), y + ln * math.sin(ang)
        pts = sm([(x, y), (x + ln * 0.5 * math.cos(ang + 0.5), y + ln * 0.5 * math.sin(ang + 0.5)), (ex, ey)], 1)
        ev.append(("yarn", pts, SOOT, w))
        branch(ex, ey, ang - 0.5 - random.uniform(0, 0.4), ln * 0.74, w * 0.68, depth - 1)
        branch(ex, ey, ang + 0.4 + random.uniform(0, 0.4), ln * 0.7, w * 0.68, depth - 1)
    ev.append(("fn", lambda L: satin(L, ellipse_mask(168, 58, 26, 26), MUSTARD, 30, spacing=1.5, sheen=0.3), (168, 58), MUSTARD))
    branch(120, 240, -math.pi / 2 + 0.12, 84, 12, 6)
    return ev
def swirl_hill():
    ev = []
    hill = [(0, 240), (0, 160)] + sm([(0, 160), (60, 120), (120, 104), (170, 110), (210, 140), (240, 170)], 2) + [(240, 240)]
    ev.append(satin_ev(hill, (84, 76, 84), 80))
    ev += run_ev(hill[2:-1], CREAM, 1.6, 4, 3)
    sp = []; th = 0
    while th < TAU * 3.2: r = 4 + 9 * th / TAU; sp.append((176 + r * math.cos(th), 92 - r * math.sin(th))); th += 0.25
    for i in range(0, len(sp) - 2, 2): ev.append(("yarn", sp[i:i + 3], (84, 76, 84), 6.5))
    for x in range(10, 110, 16):
        y = 160 - (x / 110) * 50 + 2
        ev.append(("stitch", (x, y - 16 + random.uniform(-3, 3)), (x + random.uniform(-2, 2), y), CREAM, 2.0))
    ev.append(("fn", lambda L: satin(L, ImageChops.subtract(ellipse_mask(60, 56, 30, 30), ellipse_mask(72, 48, 28, 28)), CREAM, 40, spacing=1.5), (60, 56), CREAM))
    return ev
def lantern():
    ev = []
    body = [(32, 130)] + ellipse_pts(120, 128, 90, 74, 48, 0, math.pi, TAU)[::-1] + [(208, 130)] + ellipse_pts(120, 132, 90, 70, 48, 0, 0, math.pi)[::-1]
    ev.append(satin_ev(body, ORANGE, 90, 1.6))
    for k in range(-2, 3): ev += run_ev(ellipse_pts(120 + k * 10, 130, 72 - abs(k) * 14, 72, 40, 0, -math.pi / 2, math.pi / 2), (170, 80, 30), 1.6, 4, 3)
    ev.append(satin_ev([(108, 58), (134, 54), (138, 76), (112, 78)], LEAF, 70, 1.4))
    for tri in ([(70, 100), (100, 100), (84, 124)], [(140, 100), (170, 100), (156, 124)]): ev.append(satin_ev(tri, SOOT, 45, 1.3)); ev += outline_ev(tri, (30, 20, 20), 1.0)
    smile = sm([(66, 150), (84, 172), (110, 180), (140, 178), (164, 166), (178, 146)], 2); mouth = smile + [(170, 160), (150, 168), (120, 170), (90, 164), (74, 154)]
    ev.append(satin_ev(mouth, SOOT, 0, 1.3))
    for k in range(0, len(smile) - 1, 3): ev.append(("stitch", (smile[k][0] - 4, smile[k][1] - 10), (smile[k][0] + 4, smile[k][1] + 6), CREAM, 2.0))
    return ev
def crooked_house():
    ev = []
    walls = [(70, 236), (78, 120), (150, 112), (166, 236)]; roof = [(60, 128), (120, 50), (180, 116)]
    ev.append(satin_ev(walls, PLUM, 88, 1.5)); ev += outline_ev(walls, SOOT, 1.6)
    ev.append(satin_ev(roof, SOOT, 20, 1.4)); ev += outline_ev(roof, (70, 60, 64), 1.4)
    for (x, y, w, h) in ((90, 140, 18, 24), (124, 136, 18, 24), (92, 180, 18, 22), (126, 178, 18, 22)):
        q = [(x, y), (x + w, y - 2), (x + w + 2, y + h), (x + 1, y + h + 2)]
        ev.append(satin_ev(q, MUSTARD, 0, 1.2)); ev += outline_ev(q, SOOT, 1.2)
        ev.append(("stitch", (x + w / 2, y), (x + w / 2, y + h), SOOT, 1.0)); ev.append(("stitch", (x, y + h / 2), (x + w, y + h / 2), SOOT, 1.0))
    door = [(110, 236), (112, 206), (130, 204), (134, 236)]; ev.append(satin_ev(door, OXBLOOD, 90, 1.2)); ev += outline_ev(door, SOOT, 1.2)
    chim = [(140, 90), (152, 86), (156, 112), (146, 114)]; ev.append(satin_ev(chim, OXBLOOD, 0, 1.2))
    ev.append(("fn", lambda L: satin(L, ImageChops.subtract(ellipse_mask(52, 60, 26, 26), ellipse_mask(64, 52, 24, 24)), MUSTARD, 40, spacing=1.5), (52, 60), MUSTARD))
    for k in range(3): ev.append(("knot", 152 + k * 6, 76 - k * 12, 3 + k, (150, 150, 150)))
    return ev
def ragdoll():
    ev = []; skin = (168, 176, 160)
    ev.append(satin_ev(ellipse_pts(120, 78, 34, 36, 40), skin, 90, 1.5)); ev += outline_ev(ellipse_pts(120, 78, 34, 36, 40), SOOT, 1.2)
    body = [(96, 112), (144, 112), (156, 200), (84, 200)]; ev.append(satin_ev(body, OXBLOOD, 0, 1.5)); ev += outline_ev(body, SOOT, 1.2)
    for s in (-1, 1):
        arm = [(120 + s * 30, 116), (120 + s * 56, 170), (120 + s * 44, 176), (120 + s * 24, 128)]; ev.append(satin_ev(arm, skin, 60 * s, 1.4)); ev += outline_ev(arm, SOOT, 1.2)
        leg = [(120 + s * 10, 198), (120 + s * 28, 198), (120 + s * 26, 238), (120 + s * 8, 238)]; ev.append(satin_ev(leg, (60, 56, 60), 90, 1.4))
        for yy in range(204, 236, 8): ev.append(("stitch", (120 + s * 9, yy), (120 + s * 27, yy), CREAM, 1.6))
    for s in (-1, 1): ev.append(("stitch", (120 + s * 18, 66), (120 + s * 8, 78), SOOT, 2.0)); ev.append(("stitch", (120 + s * 8, 66), (120 + s * 18, 78), SOOT, 2.0))
    smile = sm([(100, 94), (110, 102), (120, 104), (130, 102), (140, 94)], 1); ev += path_events(smile, SOOT, 1.6, 4)
    for p in smile[::3]: ev.append(("stitch", (p[0], p[1] - 5), (p[0], p[1] + 5), SOOT, 1.4))
    ev.append(("fn", lambda L: satin(L, poly_mask([(84, 120), (104, 118), (106, 140), (86, 142)]), TEAL, 40, spacing=1.3), (94, 130), TEAL))
    ev += run_ev([(84, 120), (104, 118), (106, 140), (86, 142), (84, 120)], CREAM, 1.3, 3, 2)
    for k in range(5): ev.append(("stitch", (120 - 20 + k * 10, 50 - abs(k - 2) * 6), (120 - 18 + k * 10, 36 - abs(k - 2) * 6), OXBLOOD, 2.2))
    return ev
def cat_on_moon():
    ev = []
    moon = ImageChops.subtract(ellipse_mask(112, 128, 80, 80), ellipse_mask(146, 108, 70, 70))
    ev.append(fn_ev(lambda L: satin(L, moon, MUSTARD, 35, spacing=1.6, sheen=0.3), (112, 128), MUSTARD))
    ev += run_ev(ellipse_pts(112, 128, 81, 81, 60, 0, math.radians(100), math.radians(400)), SOOT, 1.6, 5, 3)
    cat = sm([(72, 168), (80, 150), (86, 136), (92, 118), (98, 110), (96, 100), (104, 108), (114, 108), (122, 100), (120, 112), (124, 130), (118, 150), (108, 164), (90, 172)], 1)
    ev.append(satin_ev(cat, SOOT, 80, 1.4)); ev += outline_ev(cat, (60, 54, 56), 1.2)
    tail = sm([(108, 164), (130, 176), (150, 170), (156, 150)], 2); ev.append(("yarn", tail, SOOT, 5.0))
    ev.append(("knot", 104, 118, 1.8, MUSTARD)); ev.append(("knot", 114, 118, 1.8, MUSTARD))
    for (sx, sy) in ((180, 60), (200, 120), (176, 190), (50, 50)): ev.append(("knot", sx, sy, 2.2, CREAM))
    return ev
def skeleton_key():
    ev = []
    bow = ImageChops.subtract(ellipse_mask(120, 72, 34, 30), ellipse_mask(120, 72, 18, 15))
    ev.append(fn_ev(lambda L: satin(L, bow, (150, 130, 80), 30, spacing=1.5, sheen=0.35), (120, 42), MUSTARD))
    ev += run_ev(ellipse_pts(120, 72, 35, 31, 48), SOOT, 1.4, 4, 3); ev += run_ev(ellipse_pts(120, 72, 17, 14, 32), SOOT, 1.2, 3, 2.5)
    for k in range(4):
        a = TAU * k / 4; ev.append(("fn", (lambda a=a: lambda L: satin(L, ellipse_mask(120 + 30 * math.cos(a), 72 + 26 * math.sin(a), 7, 7), (150, 130, 80), 0, spacing=1.3, sheen=0.3))(), (120, 72), MUSTARD))
    shaft = [(112, 100), (128, 100), (126, 214), (114, 214)]; ev.append(satin_ev(shaft, (150, 130, 80), 90, 1.5)); ev += outline_ev(shaft, SOOT, 1.2)
    for (y, w) in ((170, 30), (190, 22), (208, 26)):
        bit = [(126, y), (126 + w, y), (126 + w, y + 10), (126, y + 10)]; ev.append(satin_ev(bit, (150, 130, 80), 0, 1.3)); ev += outline_ev(bit, SOOT, 1.1)
    ev.append(("fn", lambda L: yarn(L, sm([(120, 42), (100, 28), (80, 36), (70, 56)], 2), OXBLOOD, 2.6), (70, 56), OXBLOOD))
    return ev
def crow():
    ev = []
    ev.append(("yarn", sm([(0, 190), (50, 182), (100, 186), (150, 178), (200, 184), (240, 176)], 2), BROWN, 5.0))
    body = sm([(84, 170), (92, 134), (106, 112), (128, 100), (150, 104), (160, 120), (156, 146), (170, 176), (140, 166), (118, 176), (100, 178)], 2)
    ev.append(satin_ev(body, SOOT, 70, 1.4)); ev += outline_ev(body, (60, 54, 56), 1.2)
    head = ellipse_pts(150, 94, 18, 15, 30, math.radians(-15)); ev.append(satin_ev(head, SOOT, 0, 1.3))
    ev.append(satin_ev([(166, 92), (190, 98), (166, 102)], (120, 110, 90), 0, 1.2))
    ev.append(("knot", 156, 90, 2.4, CREAM)); ev.append(("knot", 156, 90, 1.2, SOOT))
    for k in range(4): ev.append(("stitch", (96 + k * 10, 140 + k * 6), (84 + k * 10, 160 + k * 4), (90, 84, 88), 1.6))
    for lx in (112, 132): ev.append(("stitch", (lx, 176), (lx + 2, 186), (120, 110, 90), 1.6)); ev.append(("stitch", (lx - 4, 186), (lx + 8, 186), (120, 110, 90), 1.4))
    ev.append(fn_ev(lambda L: satin(L, ImageChops.subtract(ellipse_mask(56, 60, 26, 26), ellipse_mask(68, 52, 24, 24)), BONE, 40, spacing=1.5), (56, 60), CREAM))
    return ev

# =================================================================== E. quilt blocks
def q_grid(n, size=160):
    c = size / n; o = 120 - size / 2
    return lambda i, j: (o + i * c, o + j * c), c
def log_cabin():
    ev = []; x0, y0, x1, y1 = 60, 60, 180, 180
    ev.append(satin_ev([(104, 104), (136, 104), (136, 136), (104, 136)], OXBLOOD, 45, 1.4))
    cols = [CREAM, SAGE, MUSTARD, TEAL, PLUM, RUST, CREAM, SAGE]
    w = 14; L_, T, R, B = 104, 104, 136, 136; k = 0
    for ring in range(3):
        for side in range(4):
            col = cols[k % len(cols)]; k += 1
            if side == 0: poly = [(L_, T - w), (R, T - w), (R, T), (L_, T)]; T -= w
            elif side == 1: poly = [(R, T), (R + w, T), (R + w, B), (R, B)]; R += w
            elif side == 2: poly = [(L_, B), (R, B), (R, B + w), (L_, B + w)]; B += w
            else: poly = [(L_ - w, T), (L_, T), (L_, B), (L_ - w, B)]; L_ -= w
            ev.append(satin_ev(poly, col, 0 if side % 2 else 90, 1.4)); ev += run_ev(poly + [poly[0]], SOOT, 1.0, 3, 2.5)
    return ev
def pinwheel():
    ev = []; g, c = q_grid(2, 150)
    for (i, j, r) in ((0, 0, 0), (1, 0, 1), (1, 1, 2), (0, 1, 3)):
        p = g(i, j); sq = [p, (p[0] + c, p[1]), (p[0] + c, p[1] + c), (p[0], p[1] + c)]
        t1 = [sq[r % 4], sq[(r + 1) % 4], sq[(r + 2) % 4]]; t2 = [sq[(r + 2) % 4], sq[(r + 3) % 4], sq[r % 4]]
        ev.append(satin_ev(t1, OXBLOOD, 45 + 90 * r, 1.5)); ev.append(satin_ev(t2, CREAM, -45 + 90 * r, 1.5)); ev += run_ev(sq + [sq[0]], SOOT, 1.0, 3, 2.5); ev += run_ev([t1[0], t1[2]], SOOT, 1.0, 3, 2.5)
    return ev
def flying_geese():
    ev = []
    for row, y in enumerate(range(30, 200, 40)):
        x0 = 40
        for k in range(2):
            x = x0 + k * 80; goose = [(x, y + 40), (x + 40, y), (x + 80, y + 40)]
            ev.append(satin_ev(goose, [TEAL, PLUM, MUSTARD, OXBLOOD][row % 4], 90, 1.5))
            ev.append(satin_ev([(x, y), (x + 40, y), (x, y + 40)], CREAM, 45, 1.5)); ev.append(satin_ev([(x + 40, y), (x + 80, y), (x + 80, y + 40)], CREAM, -45, 1.5))
            ev += run_ev(goose + [goose[0]], SOOT, 1.0, 3, 2.5)
    return ev
def nine_patch():
    ev = []; g, c = q_grid(3, 156)
    for i in range(3):
        for j in range(3):
            p = g(i, j); sq = [p, (p[0] + c, p[1]), (p[0] + c, p[1] + c), (p[0], p[1] + c)]
            ev.append(satin_ev(sq, PLUM if (i + j) % 2 == 0 else MUSTARD, 45 if (i + j) % 2 else -45, 1.5)); ev += run_ev(sq + [sq[0]], CREAM, 1.2, 3, 2.5)
    return ev
def ohio_star():
    ev = []; g, c = q_grid(3, 156)
    for i in range(3):
        for j in range(3):
            p = g(i, j); sq = [p, (p[0] + c, p[1]), (p[0] + c, p[1] + c), (p[0], p[1] + c)]; m = (p[0] + c / 2, p[1] + c / 2)
            if (i + j) % 2 == 1:
                tris = [[sq[0], sq[1], m], [sq[1], sq[2], m], [sq[2], sq[3], m], [sq[3], sq[0], m]]
                for t, tri in enumerate(tris): ev.append(satin_ev(tri, TEAL if t % 2 == ((i + j) // 2) % 2 else CREAM, 45 * t, 1.4))
                for tri in tris: ev += run_ev([tri[0], m], SOOT, 1.0, 3, 2.5)
            else: ev.append(satin_ev(sq, OXBLOOD if i == 1 else CREAM, 45, 1.5))
            ev += run_ev(sq + [sq[0]], SOOT, 1.0, 3, 2.5)
    return ev
def dresden_plate():
    ev = []
    for k in range(12):
        a0 = TAU * k / 12; a1 = TAU * (k + 1) / 12; am = (a0 + a1) / 2
        blade = [(120 + 26 * math.cos(a0 + 0.1), 120 + 26 * math.sin(a0 + 0.1)), (120 + 96 * math.cos(a0 + 0.04), 120 + 96 * math.sin(a0 + 0.04)),
                 (120 + 108 * math.cos(am), 120 + 108 * math.sin(am)), (120 + 96 * math.cos(a1 - 0.04), 120 + 96 * math.sin(a1 - 0.04)), (120 + 26 * math.cos(a1 - 0.1), 120 + 26 * math.sin(a1 - 0.1))]
        ev.append(satin_ev(blade, PALETTE[k % len(PALETTE)], math.degrees(am), 1.5)); ev += run_ev(blade + [blade[0]], SOOT, 1.0, 3, 2.5)
    ev.append(fn_ev(lambda L: satin(L, ellipse_mask(120, 120, 26, 26), MUSTARD, 30, spacing=1.4), (120, 120), MUSTARD)); ev += run_ev(ellipse_pts(120, 120, 26, 26, 40), SOOT, 1.0, 3, 2.5)
    return ev
def hexie_flower():
    ev = []; R = 30; w = math.sqrt(3) * R
    cells = [(120, 120)] + [(120 + w * math.cos(TAU * k / 6 + math.pi / 6), 120 + w * math.sin(TAU * k / 6 + math.pi / 6)) for k in range(6)]
    cells += [(120 + 2 * w * math.cos(TAU * k / 6 + math.pi / 6), 120 + 2 * w * math.sin(TAU * k / 6 + math.pi / 6)) for k in range(6)]
    cells += [(120 + w * math.sqrt(3) * math.cos(TAU * k / 6), 120 + w * math.sqrt(3) * math.sin(TAU * k / 6)) for k in range(6)]
    for n, (cx, cy) in enumerate(cells):
        hexp = [(cx + (R - 1.5) * math.cos(math.radians(60 * k + 30)), cy + (R - 1.5) * math.sin(math.radians(60 * k + 30))) for k in range(6)]
        col = MUSTARD if n == 0 else (OXBLOOD if n < 7 else (SAGE if n < 13 else TEAL))
        ev.append(satin_ev(hexp, col, 30 * n, 1.5)); ev += run_ev(hexp + [hexp[0]], CREAM, 1.2, 3, 2.5)
    return ev
def bear_paw():
    ev = []; g, c = q_grid(4, 160)
    for (qi, qj) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        ox, oy = qi * 2, qj * 2; big = g(ox + (1 - qi), oy + (1 - qj))
        sq = [big, (big[0] + c, big[1]), (big[0] + c, big[1] + c), (big[0], big[1] + c)]; ev.append(satin_ev(sq, OXBLOOD, 45, 1.5)); ev += run_ev(sq + [sq[0]], SOOT, 1.0, 3, 2.5)
        for (ti, tj) in ((ox + qi, oy), (ox + qi, oy + 1), (ox, oy + qj), (ox + 1, oy + qj)):
            if (ti, tj) == (ox + (1 - qi), oy + (1 - qj)): continue
            p = g(ti, tj); s2 = [p, (p[0] + c, p[1]), (p[0] + c, p[1] + c), (p[0], p[1] + c)]
            ev.append(satin_ev([s2[0], s2[2], s2[3]] if qi == qj else [s2[1], s2[3], s2[0]], OXBLOOD, 45, 1.4)); ev.append(satin_ev([s2[0], s2[1], s2[2]] if qi == qj else [s2[1], s2[2], s2[3]], CREAM, -45, 1.4))
            ev += run_ev(s2 + [s2[0]], SOOT, 1.0, 3, 2.5)
    return ev

# =================================================================== F. embroidery florals
def lazy_daisy_ring():
    ev = []
    for k in range(8):
        a = TAU * k / 8; cx, cy = 120 + 72 * math.cos(a), 120 + 72 * math.sin(a); col = [CREAM, (236, 160, 170), MUSTARD, (190, 170, 220)][k % 4]
        for p in range(6):
            pa = TAU * p / 6 + a; pts = ellipse_pts(cx + 9 * math.cos(pa), cy + 9 * math.sin(pa), 9, 3.6, 16, pa)
            ev.append(fn_ev((lambda pts=pts, col=col: lambda L: thread_loop(L, pts, col, 1.6))(), (cx, cy), col))
        for p in range(5): ev.append(("knot", cx + 2 * math.cos(TAU * p / 5), cy + 2 * math.sin(TAU * p / 5), 1.6, MUSTARD if col != MUSTARD else OXBLOOD))
        for p in range(2):
            la = a + math.pi / 8 + p * math.pi; ev.append(fn_ev((lambda cx=cx, cy=cy, la=la: lambda L: leaf(L, cx + 12 * math.cos(la), cy + 12 * math.sin(la), cx + 26 * math.cos(la), cy + 26 * math.sin(la), 4, SAGE))(), (cx, cy), SAGE))
    ev.append(fn_ev(lambda L: bigknot(L, 120, 120, 14, OXBLOOD), (120, 120), OXBLOOD))
    return ev
def satin_rose():
    ev = []; th = 0.0
    while th < TAU * 4:
        r = 6 + 16 * th / TAU; a0, a1 = th, th + 0.5
        petal = [(120 + r * math.cos(a0), 120 + r * math.sin(a0)), (120 + (r + 12) * math.cos(a0 + 0.1), 120 + (r + 12) * math.sin(a0 + 0.1)), (120 + (r + 14) * math.cos(a1), 120 + (r + 14) * math.sin(a1)), (120 + (r + 2) * math.cos(a1 + 0.05), 120 + (r + 2) * math.sin(a1 + 0.05))]
        col = shade(OXBLOOD, 0.8 + 0.5 * (th / (TAU * 4)))
        ev.append(satin_ev(petal, col, math.degrees(th) + 90, 1.3)); th += 0.5
    for k in range(5):
        a = TAU * k / 5 + 0.3; ev.append(fn_ev((lambda a=a: lambda L: leaf(L, 120 + 70 * math.cos(a), 120 + 70 * math.sin(a), 120 + 104 * math.cos(a + 0.15), 120 + 104 * math.sin(a + 0.15), 9, SAGE))(), (120, 120), SAGE))
    return ev
def feather_vine():
    ev = []
    stem = sm([(120, 236), (110, 190), (126, 150), (112, 110), (124, 70), (118, 20)], 2); at, total = resample(stem); pos = 0; side = 1
    while pos + 9 < total:
        a = at(pos); b = at(pos + 9); dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) or 1; nx, ny = -dy / ln, dx / ln
        ev.append(("stitch", a, (b[0] + nx * 12 * side, b[1] + ny * 12 * side), SAGE, 1.8)); ev.append(("stitch", (b[0] + nx * 12 * side, b[1] + ny * 12 * side), (b[0] + nx * 22 * side + dx / ln * 6, b[1] + ny * 22 * side + dy / ln * 6), SAGE, 1.6))
        if int(pos / 9) % 4 == 1: ev.append(("knot", b[0] + nx * 26 * side, b[1] + ny * 26 * side, 3.2, [OXBLOOD, MUSTARD, TEAL][int(pos / 36) % 3]))
        pos += 9; side = -side
    return ev
def chain_heart():
    ev = []
    for n, (s, col) in enumerate(((5.8, OXBLOOD), (4.6, MUSTARD), (3.4, TEAL), (2.2, PLUM), (1.1, CREAM))):
        hp = G2.heart_pts(120, 118, s, 90); at, total = resample(hp + [hp[0]]); pos = 0
        while pos < total:
            a = at(pos); b = at(min(total, pos + 6)); ang = math.atan2(b[1] - a[1], b[0] - a[0]); pts = ellipse_pts((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 3.2, 2.0, 12, ang)
            ev.append(fn_ev((lambda pts=pts, col=col: lambda L: thread_loop(L, pts, col, 1.4))(), b, col)); pos += 6
    return ev
def knot_cloud():
    ev = []; random.seed(8)
    cloud = sm([(40, 140), (60, 100), (96, 84), (130, 78), (166, 92), (196, 118), (200, 150), (176, 168), (120, 174), (70, 168), (44, 160)], 2); m = poly_mask(cloud)
    pts = [(x + random.uniform(-2, 2), y + random.uniform(-2, 2)) for y in range(70, 180, 7) for x in range(30, 210, 7)]
    pts = [p for p in pts if 0 <= p[0] < 240 and 0 <= p[1] < 240 and m.getpixel((int(p[0] * S), int(p[1] * S))) > 0]
    pts.sort(key=lambda p: p[0] + p[1] * 0.3)
    for (x, y) in pts: ev.append(("knot", x, y, 3.4, random.choice([CREAM, CREAM, (236, 160, 170), (190, 170, 220)])))
    for (rx, ry) in ((60, 196), (120, 206), (180, 196)):
        for k in range(3): ev.append(("stitch", (rx - 6 + k * 6, ry + k * 8), (rx - 8 + k * 6, ry + 12 + k * 8), TEAL, 1.6))
    return ev
def herringbone_bands():
    ev = []
    for row, y in enumerate(range(20, 230, 30)):
        col = PALETTE[row % len(PALETTE)]; side = 1; x = 10
        while x < 236:
            if inside(x, y + 10, 116): ev.append(("stitch", (x, y + 10 - 9 * side), (x + 14, y + 10 + 9 * side), col, 2.2))
            x += 12; side = -side
    return ev
def bullion_roses():
    ev = []
    for (cx, cy, r, col) in ((80, 90, 28, OXBLOOD), (150, 76, 20, (236, 160, 170)), (160, 150, 30, RUST), (84, 162, 22, PLUM)):
        th = 0
        while th < TAU * 2.2:
            rr = 4 + r * th / (TAU * 2.2); a, b = (cx + rr * math.cos(th), cy + rr * math.sin(th)), (cx + (rr + 2) * math.cos(th + 0.6), cy + (rr + 2) * math.sin(th + 0.6))
            ev.append(("yarn", [a, ((a[0] + b[0]) / 2 + 1.5, (a[1] + b[1]) / 2 - 1.5), b], shade(col, 0.85 + 0.3 * th / (TAU * 2.2)), 3.4)); th += 0.6
        for k in range(3): a = TAU * k / 3 + 0.4; ev.append(fn_ev((lambda a=a, cx=cx, cy=cy, r=r: lambda L: leaf(L, cx + r * math.cos(a), cy + r * math.sin(a), cx + (r + 16) * math.cos(a), cy + (r + 16) * math.sin(a), 5, SAGE))(), (cx, cy), SAGE))
    return ev
def wheat():
    ev = []
    for (bx, lean) in ((70, -0.25), (120, 0.0), (170, 0.22)):
        stem = sm([(bx, 236), (bx + lean * 40, 170), (bx + lean * 90, 100)], 1); ev.append(("yarn", stem, (160, 130, 70), 2.4))
        tip = stem[-1]; d = (tip[0] - stem[-2][0], tip[1] - stem[-2][1]); ln = math.hypot(*d); dx, dy = d[0] / ln, d[1] / ln; nx, ny = -dy, dx
        for k in range(8):
            p = (tip[0] - dx * k * 7, tip[1] - dy * k * 7)
            for s in (-1, 1): ev.append(("stitch", p, (p[0] + nx * 10 * s + dx * 10, p[1] + ny * 10 * s + dy * 10), MUSTARD, 2.6))
            ev.append(("stitch", p, (p[0] + dx * 12, p[1] + dy * 12), (180, 150, 80), 1.2))
    return ev

# =================================================================== G. loops
def lantern_swing(f, FR=24):
    L = new_layer(); ph = TAU * f / FR; th = math.radians(14) * math.sin(ph)
    ax, ay = 120, -4; ln = 70; hx, hy = ax + ln * math.sin(th), ay + ln * math.cos(th)
    yarn(L, [(ax, ay), (hx, hy)], BROWN, 3.0)
    body = rot([(hx - 30, hy), (hx + 30, hy), (hx + 36, hy + 70), (hx - 36, hy + 70)], hx, hy, th)
    satin(L, poly_mask(body), ORANGE, 90 + math.degrees(th), spacing=1.5, sheen=0.3); yarn(L, body + [body[0]], SOOT, 3.0)
    top = rot([(hx - 24, hy - 10), (hx + 24, hy - 10), (hx + 30, hy), (hx - 30, hy)], hx, hy, th); satin(L, poly_mask(top), SOOT, 0, spacing=1.3)
    for (ex, ey) in ((-14, 22), (14, 22)): p = rot([(hx + ex, hy + ey)], hx, hy, th)[0]; satin(L, poly_mask([(p[0] - 8, p[1] + 8), (p[0] + 8, p[1] + 8), (p[0], p[1] - 8)]), SOOT, 45, spacing=1.2)
    sm_ = rot(sm([(hx - 20, hy + 44), (hx - 8, hy + 54), (hx + 8, hy + 54), (hx + 20, hy + 44)], 1), hx, hy, th); yarn(L, sm_, SOOT, 4.0)
    glow = 0.7 + 0.3 * math.sin(ph * 3); p = rot([(hx, hy + 30)], hx, hy, th)[0]; bigknot(L, p[0], p[1], 5 * glow, (250, 220, 120))
    return L
def pinwheel_spin(f, FR=24):
    L = new_layer(); ph = TAU * f / FR / 4   # quarter turn per loop = seamless (4-fold symmetry)
    for k in range(4):
        a = ph + TAU * k / 4
        blade = rot([(120, 120), (120 + 90, 120), (120 + 90, 120 - 50)], 120, 120, a)
        satin(L, poly_mask(blade), [OXBLOOD, CREAM, TEAL, MUSTARD][k], math.degrees(a) + 30, spacing=1.5, sheen=0.3); yarn(L, blade + [blade[0]], SOOT, 2.0)
    bigknot(L, 120, 120, 9, SOOT)
    yarn(L, [(120, 128), (120, 240)], BROWN, 4.0)
    return L
def bats_circle(f, FR=24):
    L = new_layer(); ph = TAU * f / FR; random.seed(2)
    satin(L, ellipse_mask(120, 120, 56, 56), MUSTARD, 30, spacing=1.5, sheen=0.3); yarn(L, ellipse_pts(120, 120, 57, 57, 60), (170, 130, 50), 2.0)
    for i in range(5):
        a = ph + TAU * i / 5; r = 92 + 6 * math.sin(ph * 2 + i); bx, by = 120 + r * math.cos(a), 120 + r * math.sin(a)
        wings, body = gen_linen.bat_poly(bx, by, 0.55, 0.5 + 0.5 * math.sin(ph * 5 + i))
        wings = rot(wings, bx, by, a + math.pi / 2); body = rot(body, bx, by, a + math.pi / 2)
        satin(L, poly_mask(wings), SOOT, 0, spacing=1.2, blur=0); satin(L, poly_mask(body), SOOT, 90, spacing=1.2, blur=0)
    return L
def snow_knots(f, FR=24):
    L = new_layer(); ph = f / FR; random.seed(5)
    for i in range(40):
        x0 = random.uniform(0, 240); sp = random.uniform(0.6, 1.4); r = random.uniform(1.6, 3.4); drift = random.uniform(-8, 8)
        y = ((random.uniform(0, 1) + ph * sp) % 1.0) * 260 - 10; x = x0 + drift * math.sin(ph * TAU + i)
        if inside(x, y, 118): knot(L, x, y, r, SNOW)
    hill = [(0, 240), (0, 196)] + sm([(0, 196), (60, 184), (120, 190), (180, 180), (240, 190)], 2) + [(240, 240)]
    satin(L, poly_mask(hill), SNOW, 0, spacing=1.6, sheen=0.1)
    yarn(L, sm([(150, 186), (154, 150), (146, 120)], 1), BROWN, 4.0); yarn(L, [(154, 150), (170, 134)], BROWN, 2.6); yarn(L, [(150, 136), (136, 124)], BROWN, 2.6)
    return L
def candle_flicker(f, FR=24):
    L = new_layer(); ph = TAU * f / FR
    satin(L, poly_mask([(96, 236), (144, 236), (140, 110), (100, 110)]), CREAM, 90, spacing=1.5, sheen=0.3); yarn(L, [(96, 236), (100, 110), (140, 110), (144, 236)], SOOT, 2.0)
    for (x, y) in ((104, 130), (134, 150), (108, 170)): yarn(L, sm([(x, 112), (x - 2, y), (x + 3, y + 10)], 1), (220, 210, 190), 3.0)
    yarn(L, [(120, 110), (120, 96)], SOOT, 2.0)
    fl = 1 + 0.18 * math.sin(ph * 3) + 0.1 * math.sin(ph * 5 + 1); lean = 5 * math.sin(ph * 2)
    flame = sm([(120, 96), (108 + lean, 76), (112 + lean * 1.5, 52 * fl + 44 * (1 - fl)), (120 + lean * 2, 36 * fl + 50 * (1 - fl)), (128 + lean * 1.5, 52 * fl + 44 * (1 - fl)), (132 + lean, 76)], 2)
    satin(L, poly_mask(flame), ORANGE, 90, spacing=1.3, sheen=0.3, blur=0)
    inner = sm([(120, 94), (114 + lean, 80), (118 + lean * 1.5, 62), (120 + lean * 2, 56), (122 + lean * 1.5, 62), (126 + lean, 80)], 2); satin(L, poly_mask(inner), (250, 230, 150), 90, spacing=1.2, shadow=False, blur=0)
    yarn(L, flame + [flame[0]], OXBLOOD, 1.6)
    return L
def thread_wiggle(f, FR=24):
    L = new_layer(); ph = TAU * f / FR; random.seed(9)
    for k, col in enumerate((OXBLOOD, MUSTARD, TEAL)):
        pts = [(x, 120 + (k - 1) * 40 + 18 * math.sin(x / 30 + ph + k) + 8 * math.sin(x / 11 - ph * 2 + k)) for x in range(-10, 251, 6)]
        yarn(L, pts, col, 3.6)
    needle(L, (232, 120 + 18 * math.sin(232 / 30 + ph + 1) + 8 * math.sin(232 / 11 - ph * 2 + 1)), (1, 0), MUSTARD)
    return L

# =================================================================== registry
BUILDS = [
    # name, fn, bg, tool, frames, set
    ("seigaiha_indigo", seigaiha_indigo, lambda: bg_indigo(50), "needle", 36, "sashiko"), ("asanoha_indigo", asanoha_indigo, lambda: bg_indigo(51), "needle", 36, "sashiko"),
    ("kaki_no_hana", kaki_no_hana, lambda: bg_indigo(52), "needle", 36, "sashiko"), ("juji_tsunagi", juji_tsunagi, lambda: bg_indigo(53), "needle", 36, "sashiko"),
    ("fundo", fundo, lambda: bg_indigo(54), "needle", 36, "sashiko"), ("nowaki", nowaki, lambda: bg_indigo(55), "needle", 36, "sashiko"),
] + [(n, (lambda n=n: motif(n)), (lambda n=n: MOTIFS[n][2](60 + i)), "needle", 36, "cross-stitch") for i, n in enumerate(MOTIFS)] + [
    ("granny_sunburst", granny_sunburst, lambda: BLACK_BG, "hook", 36, "granny"), ("granny_stripes", granny_stripes, lambda: BLACK_BG, "hook", 36, "granny"),
    ("granny_triangle", granny_triangle, lambda: BLACK_BG, "hook", 36, "granny"), ("granny_heart", granny_heart, lambda: BLACK_BG, "hook", 36, "granny"),
    ("granny_flower", granny_flower, lambda: BLACK_BG, "hook", 36, "granny"), ("granny_ripple_round", granny_ripple_round, lambda: BLACK_BG, "hook", 36, "granny"),
    ("burton_tree", burton_tree, lambda: bg_satin(70, (242, 236, 222), 60), "needle", 36, "burton"), ("swirl_hill", swirl_hill, lambda: BLACK_BG, "needle", 36, "burton"),
    ("lantern", lantern, lambda: BLACK_BG, "needle", 36, "burton"), ("crooked_house", crooked_house, lambda: BLACK_BG, "needle", 36, "burton"),
    ("ragdoll", ragdoll, lambda: bg_linen(71), "needle", 36, "burton"), ("cat_on_moon", cat_on_moon, lambda: BLACK_BG, "needle", 36, "burton"),
    ("skeleton_key", skeleton_key, lambda: bg_linen(72), "needle", 36, "burton"), ("crow", crow, lambda: bg_satin(73), "needle", 36, "burton"),
    ("log_cabin", log_cabin, lambda: bg_linen(80), "needle", 36, "quilt"), ("pinwheel", pinwheel, lambda: bg_linen(81), "needle", 36, "quilt"),
    ("flying_geese", flying_geese, lambda: bg_linen(82), "needle", 36, "quilt"), ("nine_patch", nine_patch, lambda: bg_linen(83), "needle", 36, "quilt"),
    ("ohio_star", ohio_star, lambda: bg_linen(84), "needle", 36, "quilt"), ("dresden_plate", dresden_plate, lambda: bg_linen(85), "needle", 36, "quilt"),
    ("hexie_flower", hexie_flower, lambda: bg_linen(86), "needle", 36, "quilt"), ("bear_paw", bear_paw, lambda: bg_linen(87), "needle", 36, "quilt"),
    ("lazy_daisy_ring", lazy_daisy_ring, lambda: bg_linen(90), "needle", 36, "floral"), ("satin_rose", satin_rose, lambda: bg_linen(91), "needle", 36, "floral"),
    ("feather_vine", feather_vine, lambda: bg_linen(92), "needle", 36, "floral"), ("chain_heart", chain_heart, lambda: bg_linen(93), "needle", 36, "floral"),
    ("knot_cloud", knot_cloud, lambda: bg_satin(94), "needle", 36, "floral"), ("herringbone_bands", herringbone_bands, lambda: bg_linen(95), "needle", 36, "floral"),
    ("bullion_roses", bullion_roses, lambda: bg_linen(96), "needle", 36, "floral"), ("wheat", wheat, lambda: bg_linen(97), "needle", 36, "floral"),
]
LOOPS = [("lantern_swing", lantern_swing, lambda: BLACK_BG, "burton"), ("pinwheel_spin", pinwheel_spin, lambda: bg_linen(98), "quilt"), ("bats_circle", bats_circle, lambda: bg_satin(101, (242, 236, 222), 60), "burton"),
         ("snow_knots", snow_knots, lambda: bg_indigo(99), "floral"), ("candle_flicker", candle_flicker, lambda: BLACK_BG, "burton"), ("thread_wiggle", thread_wiggle, lambda: bg_linen(100), "floral")]

if __name__ == "__main__":
    import json
    sets = {}
    done = []
    for i, (name, fn, bgf, tool, FR, st) in enumerate(BUILDS):
        random.seed(500 + i); gen_linen.FRAMES = FR
        fr = gen_linen.render_events(name, fn(), bgf(), tool); done.append((name, fr)); sets[name] = st; print(name)
    for name, fn, bgf, st in LOOPS:
        bg = bgf(); gen_linen.export_bg(name, bg); fr = []
        for f in range(24):
            random.seed(1000); img = compose_bg(fn(f), bg); img.save(f"{OUT}/{name}_{f:02d}.png"); fr.append(img)
        open(f"{OUT}/{name}.loop", "w").write("1\n"); done.append((name, fr)); sets[name] = st; print(name)
    json.dump(sets, open(f"{OUT}/sets.json", "w"))
    cols = 10; rows = math.ceil(len(done) / cols)
    sheet = Image.new("RGB", (cols * 130 + 10, rows * 130 + 10), (40, 40, 40))
    for i, (name, fr) in enumerate(done): sheet.paste(fr[-1].resize((120, 120), Image.LANCZOS), (10 + (i % cols) * 130, 10 + (i // cols) * 130))
    sheet.save(f"{OUT}/sheet_fifty.png"); print("done", len(done))
