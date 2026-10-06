#!/usr/bin/env python3
"""YouTube channel banner for @SideFrogTV: 2560x1440. Everything essential sits in the
1546x423 center that phones show; desktops show the full-width middle strip (2560x423),
which adds two of Frank's verdicts; TVs show it all. Uses the Short's frames and font."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import make_short as ms

W, H = 2560, 1440
SAFE = (507, 508, 2053, 931)          # phones: the 1546x423 center
STRIP = (0, 508, 2560, 931)           # desktops: the full-width middle strip

def banner():
    img = Image.new("RGBA", (W, H), ms.PAPER); d = ImageDraw.Draw(img)
    # editorial rules framing the desktop strip
    d.rectangle((0, 532, W, 536), fill=ms.INK); d.rectangle((0, 902, W, 904), fill=ms.INK)
    # the safe center: round Frank looking at you, the name, what it is, the tagline
    ms.paste_center(img, ms.frank(12, 480, round_=True).resize((330, 330), Image.LANCZOS), 735, 719)
    x = 950
    d.text((x, 575), "FRANK REVIEWS YOUR SIDE HUSTLE", font=ms.font(34, 800, 14), fill=ms.DEEP)
    d.text((x, 615), "SideFrog", font=ms.font(176), fill=ms.INK)
    d.text((x, 805), "For people who hate Mondays.", font=ms.font(56, 500, 20), fill=ms.MUTED)
    # the desktop strip, outside the safe center: two of Frank's verdicts
    for cx, face, label in ((255, 0, "Surprisingly, yes"), (2305, 2, "Keep your day job")):
        ms.paste_center(img, ms.frank(face, 240, round_=True).resize((190, 190), Image.LANCZOS), cx, 690)
        f = ms.font(30, 800, 14); t = label.upper()
        d.text((cx - d.textlength(t, font=f) / 2, 800), t, font=f, fill=ms.INK)
    return img.convert("RGB")

if __name__ == "__main__":
    b = banner(); out = os.path.join(HERE, "sidefrog-youtube-banner.png"); b.save(out, optimize=True)
    # a check image: what phones, desktops and TVs each show
    chk = b.copy(); dd = ImageDraw.Draw(chk)
    dd.rectangle(STRIP, outline=(40, 110, 220), width=8); dd.rectangle(SAFE, outline=(220, 40, 40), width=8)
    chk.resize((1280, 720)).save(os.path.join(HERE, "banner-check.png"))
    print(out, os.path.getsize(out) // 1024, "KB")
