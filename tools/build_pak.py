#!/usr/bin/env python3
"""Build a PINPAK01 archive (what the firmware reads from the data partition) from docs/data.
Same format the web gallery builds in the browser.

  python3 tools/build_pak.py --only shippo,kikko,big_bat --out mypin.bin
  python3 tools/build_pak.py --exclude waving_ripple --out mypin.bin
Then:  esptool.py --chip esp32s3 -p PORT write_flash 0x310000 mypin.bin
"""
import sys, os, json, struct
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "docs", "data")
PART = 0xCF0000
args = sys.argv[1:]
def opt(k, d=None): return args[args.index(k) + 1] if k in args else d
only = set(opt("--only", "").split(",")) - {""}; excl = set(opt("--exclude", "").split(",")) - {""}
pieces = json.load(open(os.path.join(HERE, "..", "docs", "pieces.json")))
names = [n for n in pieces if (not only or n in only) and n not in excl]

def build(names):
    entries = []; blobs = bytearray(); base = 12 + 56 * len(names)
    for n in names:
        bgp, dlp = os.path.join(DATA, n + ".bg"), os.path.join(DATA, n + ".dlt")
        bg = open(bgp, "rb").read() if os.path.exists(bgp) else b""
        dl = open(dlp, "rb").read()
        bg_off = base + len(blobs); blobs += bg
        dl_off = base + len(blobs); blobs += dl
        entries.append(struct.pack("<32sIIIIII", n.encode()[:31].ljust(32, b"\0"), pieces[n]["frames"], 1 if pieces[n]["loop"] else 0, bg_off, len(bg), dl_off, len(dl)))
    return b"PINPAK01" + struct.pack("<I", len(names)) + b"".join(entries) + bytes(blobs)

if __name__ == "__main__":
    pak = build(names)
    if len(pak) > PART: sys.exit(f"{len(pak)/1e6:.1f} MB exceeds the {PART/1e6:.1f} MB partition — exclude some pieces")
    out = opt("--out", "pin_archive.bin"); open(out, "wb").write(pak)
    print(f"{len(names)} pieces, {len(pak)/1e6:.2f} MB -> {out}")
