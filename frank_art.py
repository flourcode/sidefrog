"""Frank, from the approved frames in frogs/src/ (traced from Mark's reference art; never redrawn).

Two ways to show him:
  cutout(i)          Frank as drawn, for the site beside text (logo, notes, the answer card).
  round_svg(i, bg)   Frank in a circle, for identity and sharing (About, share cards, profile
                     pictures, backgrounds, video).

The circle is calculated once across all frames (frogs/round.json): the whole head inside
with breathing room above the bumps, the mug and hand in frame at rest and mid-sip, and the
bottom of the circle in his green body. For that, the round version stretches a thin strip of
his body from just below the mug straight down (a longer torso). Nothing else changes.
"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
FILES = sorted(glob.glob(os.path.join(ROOT, "frogs", "src", "frank-*.svg")))
ROUND = json.load(open(os.path.join(ROOT, "frogs", "round.json")))
SIZE = ROUND["size"]

# sprite frame for each mood; 12 is relaxed and looking straight at you
FRAME = {"yeah": 0, "smirk": 1, "think": 1, "meh": 2, "nah": 2, "sad": 3, "oops": 4, "you": 12}
SIP_YOU = [12, 10, 9, 8, 7, 8, 9, 10, 12]          # glance at the text, sip, back to you

BACKGROUNDS = {"cream": "#ECE3D1", "sage": "#D9DFC6", "ink": "#2A302A"}


def _clean(s):
    """Drop embedded provenance metadata (its namespace isn't declared once the frame is inlined)."""
    return re.sub(r'<metadata>.*?</metadata>', "", s, flags=re.S)


def _inner(i):
    s = _clean(open(FILES[i]).read())
    return re.sub(r'^\s*<svg[^>]*>|</svg>\s*$', "", s.strip())


def cutout(i):
    """The frame as drawn (square, transparent background)."""
    return _clean(open(FILES[i]).read())


def _extended(i, uid):
    """The frame with a longer torso: below its bottom row, flat avocado with his outline and any
    crease lines continued straight down (measured once into frogs/round.json). Flat shapes, so
    nothing from the mug and none of the drawing's shading can streak into the extension."""
    name = os.path.basename(FILES[i])
    e = ROUND["ext"][name]
    y = e["y"] - 0.6                                  # tuck under the drawing's last row
    colour = {"green": "#8DAA3F", "ink": "#121311"}
    rects = "".join(f'<rect x="{x0:.2f}" y="{y:.2f}" width="{x1 - x0:.2f}" height="800" fill="{colour[k]}"/>'
                    for k, x0, x1 in e["segs"])
    return f"{_inner(i)}{rects}"


def round_svg(i, bg="cream", uid=None, px=None, shape="circle", zoom=1.0, lift=0.0):
    """Frank in his calculated circle. bg: a name from BACKGROUNDS, a colour, or None for no fill.
    shape="square" fills the whole square instead (app icons, which the phone masks itself);
    zoom > 1 shows more room around him (zoom 1.25 keeps him inside a maskable icon's safe zone);
    zoom < 1 with lift (a fraction of the radius, upward) crops in on his face for tiny icons."""
    uid = uid or f"frank-round-{i}"
    cx, cy, r = ROUND["cx"], ROUND["cy"] - ROUND["r"] * lift, ROUND["r"] * zoom
    fill = BACKGROUNDS.get(bg, bg)
    size = f' width="{px}" height="{px}"' if px else ""
    back = f'<rect x="{cx - r:.2f}" y="{cy - r:.2f}" width="{2 * r:.2f}" height="{2 * r:.2f}" fill="{fill}"/>' if fill else ""
    clip = (f'<defs><clipPath id="{uid}-circle"><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/></clipPath></defs>'
            f'<g clip-path="url(#{uid}-circle)">') if shape == "circle" else "<g>"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx - r:.2f} {cy - r:.2f} {2 * r:.2f} {2 * r:.2f}"{size}>'
            f'{clip}{back}{_extended(i, uid)}</g></svg>')
