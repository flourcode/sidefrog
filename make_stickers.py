#!/usr/bin/env python3
"""Frank's sticker pack, from the approved frames (frank_art.py): die-cut, a white border and a
faint rim so they show on white too, transparent background, 1024px. Writes frank-stickers/ and
sidefrog-stickers.zip. Needs cairosvg, Pillow, numpy and scipy."""
import io, os, zipfile, cairosvg, numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, binary_fill_holes
import frank_art as fa
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "frank-stickers")
STICKERS = [("looking-at-you", 12), ("this-could-work", 1), ("surprisingly-yes", 0), ("crowded-pond", 2),
            ("cant-help", 3), ("error", 4), ("glance-right", 11), ("sipping", 7)]
SIZE, ART, BORDER, RIM = 1024, 900, 26, 3

def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r

os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
for name, i in STICKERS:
    art = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=fa.cutout(i).encode(), output_width=ART, output_height=ART))).convert("RGBA")
    a = np.array(art.split()[-1]) > 20
    ys, xs = np.nonzero(a)
    art = art.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    pad = BORDER + RIM + 4
    canvas = np.zeros((a.shape[0] + 2 * pad, a.shape[1] + 2 * pad), bool); canvas[pad:-pad, pad:-pad] = a
    white = binary_dilation(binary_fill_holes(canvas), disk(BORDER))
    rim = binary_dilation(white, disk(RIM))
    st = Image.new("RGBA", (canvas.shape[1], canvas.shape[0]), (0, 0, 0, 0))
    st.paste(Image.new("RGBA", st.size, (217, 210, 195, 255)), (0, 0), Image.fromarray((rim * 255).astype(np.uint8)))
    st.paste(Image.new("RGBA", st.size, (255, 255, 255, 255)), (0, 0), Image.fromarray((white * 255).astype(np.uint8)))
    st.alpha_composite(art, (pad, pad))
    st.thumbnail((SIZE, SIZE), Image.LANCZOS)
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0)); out.alpha_composite(st, ((SIZE - st.width) // 2, (SIZE - st.height) // 2))
    out.save(os.path.join(OUT, f"frank-{name}.png"))
with zipfile.ZipFile(os.path.join(ROOT, "sidefrog-stickers.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(OUT)): z.write(os.path.join(OUT, f), f)
print(f"{len(STICKERS)} stickers in frank-stickers/ and sidefrog-stickers.zip")
