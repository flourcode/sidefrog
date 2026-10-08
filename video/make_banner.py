#!/usr/bin/env python3
"""YouTube channel banner for @SideFrogTV: Mark's approved draft (video/art/banner-draft.png),
rebuilt for YouTube's crops and set in the Shorts' exact "after hours" colors.

YouTube shows a 2560x1440 banner three ways: phones show only the 1546x423 center, desktops the
full-width middle strip (2560x423), TVs all of it. So:
  - the main scene (Frank at his desk, the notepad, the "Ideas welcome" note) is scaled into the
    phone-safe center, with the draft's text erased and re-set in Bricolage, crisp and on-palette;
  - the plant and filing cabinet (cut off by the draft's right edge) sit flush against the banner's
    right edge, so their cut side disappears; desktops and TVs show them;
  - the background becomes exact ink (#1F241F), with the desk line running the full width."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import make_short as ms

W, H = 2560, 1440
SAFE = (507, 508, 2053, 931)          # phones: the 1546x423 center
STRIP = (0, 508, 2560, 931)           # desktops: the full-width middle strip
DRAFT = os.path.join(HERE, "art", "banner-draft.png")
S = 0.72                              # draft -> banner scale (the scene fits the phone-safe height)
OX, OY = 560 - 125 * S, 520 - 132 * S # draft (125, 132) lands at (560, 520)
INK = np.array([0x1F, 0x24, 0x1F])


def on_ink(a, bg):
    """The draft's background (and anything within a hair of it) becomes exact ink."""
    near = np.abs(a[..., :3].astype(int) - bg).sum(-1) < 24
    a[near, :3] = INK
    return a


def text_rows(fg, x0, x1, y0, y1):
    """The ink rows of the draft's text between y0 and y1 (columns x0..x1), as (top, bottom) bands."""
    r = np.nonzero(fg[y0:y1, x0:x1].any(1))[0] + y0
    bands, start = [], r[0]
    for p, q in zip(r, r[1:]):
        if q - p > 4: bands.append((start, p)); start = q
    bands.append((start, r[-1]))
    return bands


def put_text(d, text, font, x, top, fill):
    """Draw text so its letters' top edge lands exactly at `top` (not its line box)."""
    bb = d.textbbox((0, 0), text, font=font)
    d.text((x - bb[0], top - bb[1]), text, font=font, fill=fill)


def banner():
    import cv2
    src = np.asarray(Image.open(DRAFT).convert("RGBA")).copy()
    bg = np.median(np.concatenate([src[:40, :40, :3].reshape(-1, 3), src[-40:, :40, :3].reshape(-1, 3)]), 0).astype(int)
    fg = np.abs(src[..., :3].astype(int) - bg).sum(-1) > 40

    # the sticky note: its own outline (the cream card, plus a little for its edge), so nothing behind it comes along
    cream = (src[..., :3].min(-1) > 200)
    cream[:, :1650] = False; cream[380:] = False
    n, lab, stats, _ = cv2.connectedComponentsWithStats(cream.astype(np.uint8))
    biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    hull = cv2.convexHull(np.argwhere(lab == biggest)[:, ::-1].astype(np.int32))
    note = np.zeros(cream.shape, np.uint8); cv2.fillPoly(note, [hull], 1)
    note = cv2.dilate(note, np.ones((5, 5), np.uint8)).astype(bool)

    # the plant and filing cabinet: everything right of x 1745 except the note (cut cleanly at the note's edge)
    side = src.copy(); side[note] = [*bg, 255]
    side = side[190:646, 1745:1983]
    scene = src.copy()
    scene[200:462, 100:1262] = [*bg, 255]            # "SideFrog" (to the end of the g)
    scene[455:592, 100:1205] = [*bg, 255]            # the tagline and the label
    keep = scene.copy()
    scene[120:700, 1745:1983] = [*bg, 255]           # the plant and cabinet move to the banner's edge
    scene[note] = keep[note]                         # ...but the note stays with Frank
    scene[640:700, 1240:1983] = [*bg, 255]           # the draft's desk line right of the notepad (redrawn full width)
    scene = on_ink(scene, bg); side = on_ink(side, bg)

    img = Image.new("RGBA", (W, H), (*INK, 255)); d = ImageDraw.Draw(img)
    sc = Image.fromarray(scene).resize((int(1983 * S), int(793 * S)), Image.LANCZOS)
    img.alpha_composite(sc, (int(OX), int(OY)))
    desk_y = int(OY + 633 * S)
    sd = Image.fromarray(side); sd = sd.resize((int(sd.width * S * 1.05), int(sd.height * S * 1.05)), Image.LANCZOS)
    img.alpha_composite(sd, (W - sd.width, desk_y + 4 - sd.height))   # flush right: the cut edge is the banner's edge
    pad0, pad1 = int(OX + 955 * S), int(OX + 1252 * S)                 # the notepad sits on top of the desk line
    d.rectangle((0, desk_y, pad0, desk_y + 6), fill=ms.TEXT)            # the desk, full width
    d.rectangle((pad1, desk_y, W, desk_y + 6), fill=ms.TEXT)

    # the text, re-set in Bricolage where the draft's letters were, in the exact cream and avocado
    (w_top, w_bot), (t_top, t_bot) = text_rows(fg, 100, 1100, 200, 540)[:2]      # "SideFrog" caps, then the tagline
    l_top = text_rows(fg, 100, 1100, 540, 592)[0][0]                             # the label
    x = 560
    word = ms.fit_lines(d, ["SideFrog"], 300, 120, int((1258 - 125) * S), 400)
    put_text(d, "SideFrog", ms.font(word), x - 4, OY + w_top * S, ms.TEXT)
    tag = ms.fit_lines(d, ["For people who hate Mondays."], 80, 30, int((1180 - 125) * S), 200, weight=700, opsz=40)
    put_text(d, "For people who hate Mondays.", ms.font(tag, 700, 40), x, OY + t_top * S, ms.TEXT)
    label, track = "FRANK REVIEWS YOUR SIDE HUSTLE.", 0.16
    want = (1005 - 129) * S                                             # the label's width in the draft
    def label_width(f): return sum(d.textlength(ch, font=f) + f.size * track for ch in label) - f.size * track
    size = 40
    while size > 12 and label_width(ms.font(size, 800, 14)) > want: size -= 1
    f = ms.font(size, 800, 14)
    bb = d.textbbox((0, 0), "F", font=f); cx = x + 3
    for ch in label:                                                    # letter-spaced, like the draft
        d.text((cx, OY + l_top * S - bb[1]), ch, font=f, fill=ms.LABEL)
        cx += d.textlength(ch, font=f) + f.size * track
    return img.convert("RGB")


if __name__ == "__main__":
    b = banner(); out = os.path.join(HERE, "sidefrog-youtube-banner.png"); b.save(out, optimize=True)
    chk = b.copy(); cd = ImageDraw.Draw(chk)
    cd.rectangle(STRIP, outline=(40, 110, 220), width=8); cd.rectangle(SAFE, outline=(220, 40, 40), width=8)
    chk.resize((1280, 720)).save(os.path.join(HERE, "banner-check.png"))
    print(out, os.path.getsize(out) // 1024, "KB")
