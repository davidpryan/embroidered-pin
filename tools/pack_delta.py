#!/usr/bin/env python3
"""Pack animation frames as RGB565 backgrounds + frame-to-frame deltas.

  python3 pack_delta.py <frames_dir> [<frames_dir> ...]

For every piece <name> in a dir:  <name>_bg.png (optional) and <name>_NN.png.
Writes data/<name>.bg  (raw 240x240 RGB565 LE, 115200 bytes; omitted if no bg png)
       data/<name>.dlt (all frames, concatenated; each frame = delta vs previous)
       data/manifest.txt  one line per piece: name frames

Delta stream per frame (ends when 57600 pixels covered):
  b = byte; op = b >> 6; n = (b & 63) + 1
  op 0: skip n pixels           op 1: repeat next uint16 n times
  op 2: n literal uint16s       op 3: long skip, n = ((b&63)<<8 | nextbyte) + 1
Each frame record is prefixed with its byte length as uint32 LE.
"""
import sys, os, glob, struct, re
import numpy as np
from PIL import Image

os.makedirs("data", exist_ok=True)
PX = 240 * 240

def to565(img):
    a = np.asarray(img.convert("RGB"), dtype=np.uint16)
    return (((a[..., 0] & 0xF8) << 8) | ((a[..., 1] & 0xFC) << 3) | (a[..., 2] >> 3)).reshape(-1)

def encode_delta(prev, cur):
    diff = prev != cur
    out = bytearray(); i = 0
    while i < PX:
        if not diff[i]:
            j = i
            while j < PX and not diff[j]: j += 1
            n = j - i
            while n > 0:
                k = min(n, 16384)
                if k <= 64: out.append((k - 1) & 63)
                else: out += bytes([0xC0 | ((k - 1) >> 8), (k - 1) & 0xFF])
                n -= k
            i = j
        else:
            # run of changed pixels: split into repeat runs and literal runs
            j = i
            while j < PX and diff[j]: j += 1
            seg = cur[i:j]; k = 0
            while k < len(seg):
                v = seg[k]; r = 1
                while k + r < len(seg) and seg[k + r] == v and r < 64: r += 1
                if r >= 3:
                    out.append(0x40 | (r - 1)); out += struct.pack("<H", int(v)); k += r
                else:
                    m = k
                    while m < len(seg) and m - k < 64:
                        # stop literal run when a repeat of >=3 starts
                        if m + 2 < len(seg) and seg[m] == seg[m + 1] == seg[m + 2]: break
                        m += 1
                    if m == k: m = k + 1
                    out.append(0x80 | (m - k - 1)); out += seg[k:m].astype("<u2").tobytes(); k = m
            i = j
    return bytes(out)

manifest = []
total = 0
import json
pieces = {}
SETMAP = {"linen": "linen", "granny": "granny", "granny2": "granny", "stitch": "stitch", "insects2": "insects", "loops": "loops", "bold": "bold", "wagara": "wagara"}
for d in sys.argv[1:]:
    names = sorted({re.sub(r"_\d\d\.png$", "", os.path.basename(p)) for p in glob.glob(os.path.join(d, "*_[0-9][0-9].png"))})
    for name in names:
        frames = sorted(glob.glob(os.path.join(d, f"{name}_[0-9][0-9].png")))
        bgp = os.path.join(d, f"{name}_bg.png")
        if os.path.exists(bgp):
            bg = to565(Image.open(bgp))
            open(f"data/{name}.bg", "wb").write(bg.astype("<u2").tobytes())
        else:
            bg = np.zeros(PX, dtype=np.uint16)
        prev = bg; blob = bytearray(); first = None
        for fp in frames:
            cur = to565(Image.open(fp))
            if first is None: first = cur
            rec = encode_delta(prev, cur)
            blob += struct.pack("<I", len(rec)) + rec
            prev = cur
        loop = os.path.exists(os.path.join(d, f"{name}.loop"))
        if loop:                                   # wrap record: last frame -> first frame
            rec = encode_delta(prev, first); blob += struct.pack("<I", len(rec)) + rec
        open(f"data/{name}.dlt", "wb").write(blob)
        sz = len(blob) + (PX * 2 if os.path.exists(bgp) else 0)
        total += sz
        manifest.append(f"{name} {len(frames)} {1 if loop else 0}")
        setname = SETMAP.get(os.path.basename(os.path.normpath(d)))
        sj = os.path.join(d, "sets.json")
        if setname is None and os.path.exists(sj): setname = json.load(open(sj)).get(name, os.path.basename(d))
        pieces[name] = {"bytes": sz, "frames": len(frames), "loop": loop, "set": setname or os.path.basename(d), "dir": d}
        print(f"{name:20s} {len(frames)} frames {'loop' if loop else '    '} {sz/1024:7.0f} KB")
open("data/manifest.txt", "w").write("\n".join(manifest) + "\n")
json.dump(pieces, open("data/pieces.json", "w"), indent=1)
print(f"\nTOTAL {total/1e6:.2f} MB  (partition 13.3 MB)")
