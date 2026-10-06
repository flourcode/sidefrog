#!/usr/bin/env python3
"""Builds SideFrog's icons from round Frank looking at you (frank_art.py):
favicon-16/32 and favicon.ico (16, 32, 48) as the round avatar; icon-192/512 the same;
apple-touch-icon.png (180) and icon-maskable-512.png as full squares, because iOS and
Android round the corners themselves (the maskable one keeps him inside the safe zone).
Needs cairosvg and Pillow."""
import io, os, cairosvg
from PIL import Image
import frank_art as fa
ROOT = os.path.dirname(os.path.abspath(__file__))
YOU = fa.FRAME["you"]

def render(svg, size):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size))).convert("RGBA")

def save(im, name): im.save(os.path.join(ROOT, name)); print(f"  {name:24} {im.size[0]}x{im.size[1]}")

avatar = fa.round_svg(YOU, bg="cream", uid="icon")                       # circle, transparent corners
for size, name in ((32, "favicon-32.png"), (192, "icon-192.png"), (512, "icon-512.png")):
    save(render(avatar, size), name)
# at 16px the whole pose turns to mush: crop in on his face (eyes and smile), still round
face = fa.round_svg(YOU, bg="cream", uid="face", zoom=0.62, lift=0.36)
save(render(face, 16), "favicon-16.png")
# favicon.ico: the face crop at 16, the full avatar at 32 and 48
ico16, ico32, ico48 = render(face, 16), render(avatar, 32), render(avatar, 48)
ico48.save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)], append_images=[ico16, ico32])
print("  favicon.ico              16 (face), 32, 48")
square = fa.round_svg(YOU, bg="cream", uid="sq", shape="square")
save(render(square, 180).convert("RGB"), "apple-touch-icon.png")
maskable = fa.round_svg(YOU, bg="cream", uid="mk", shape="square", zoom=1.25)
save(render(maskable, 512).convert("RGB"), "icon-maskable-512.png")
