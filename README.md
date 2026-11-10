# Embroidered Pin

A wearable pin built on the Waveshare ESP32-S3-Touch-LCD-1.28 (1.28" round display, touch, IMU, LiPo) that plays
stitched-looking animations: embroidered insects, live sashiko and cross-stitch, granny squares, Tim Burton
patchwork, Japanese wagara, and more — 122 pre-rendered pieces plus 32 **generative** patterns that are
computed on the pin itself (`firmware/pin_firmware/generative.h`) and never repeat: wandering seams, spirographs,
growing vines, drifting sashiko, a Voronoi patchwork, flow-field stitches, phyllotaxis knots, cross-stitch Life,
two that crochet a fresh granny square or shape every few minutes, and ten growing-floral beds (roses, daisies, lavender, blossom branches, ferns — each on cream and on black), and ten Ruth Asawa–inspired looped-wire forms — stacked lobes, nested spheres, tied-wire stars, hourglass columns, crocheted loop vessels — crocheted ring by ring in colored string on cream or white wire on black. Ten more use core generative techniques (reaction-diffusion, Truchet tiles, flocking, DLA, circle packing, recursive subdivision, noise contours, a Clifford attractor, a harmonograph, Molnár's disordered squares), and fifteen `_slow` variants run continuously at a quarter speed, dissolving and regrowing instead of holding. A generative piece always finishes what it is making before the pin moves on. Generative pieces cost no flash.

**Gallery + flasher:** https://davidpryan.github.io/embroidered-pin/

Open it in Chrome or Edge, click the pieces you want, watch the memory bar, plug in a pin
(hold BOOT, tap RESET, release BOOT), click **Flash selection to pin**. Nothing to install.
The firmware is compiled by GitHub Actions on every push and served from the same page.

## Layout
| path | what |
|---|---|
| `firmware/pin_firmware/` | Arduino sketch + partition table. Reads a flat `PINPAK01` archive from the data partition. |
| `docs/` | the GitHub Pages site: gallery, thumbnails, packed animation data (`data/*.bg`, `data/*.dlt`), `pieces.json` |
| `tools/gen/` | the Python generators that render every animation (PIL, 4× supersampled) |
| `tools/pack_delta.py` | PNG frames → `.bg` ground + `.dlt` frame deltas |
| `tools/build_pak.py` | command-line archive builder (same format the page builds in-browser) |

## Flash budget
The data partition is 13.3 MB. Build-style pieces cost 150–800 KB each; full-screen seamless loops
(ripple, spiral, mandala) cost 2–3 MB. The page refuses to build past the limit.

## Controls on the pin
tap = next piece · hold 1 s = replay · move = wake · still 60 s = deep sleep (IMU wake-on-motion)

## Adding animations
Write a generator (see `tools/gen/gen_bold.py` for the simplest), render frames to a folder,
`python3 tools/pack_delta.py <folder>` from a scratch dir, copy the resulting `.bg/.dlt` into `docs/data/`,
add the piece to `docs/pieces.json`, add 128px `thumbs/<name>.png|gif`, push. Actions redeploys the page.

## Manual flashing
```
python3 tools/build_pak.py --only shippo,kikko,big_bat --out mypin.bin
esptool.py --chip esp32s3 -p PORT -b 921600 write_flash 0x0 merged.bin 0x310000 mypin.bin
```
(`merged.bin` is at `<pages-url>/firmware/merged.bin` after the first Actions run.)
