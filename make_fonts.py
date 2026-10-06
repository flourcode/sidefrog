#!/usr/bin/env python3
"""Self-hosted fonts: trims Bricolage Grotesque and Source Serif 4 Italic to what SideFrog uses
and writes them as WOFF2 with fingerprinted names, then points styles.css at them.
Serving fonts from sidefrog.com (instead of Google Fonts) takes two connections and a
render-blocking stylesheet off the critical path on phones.
Sources go in fonts/src/ (Bricolage.ttf: the variable Bricolage Grotesque; SourceSerif4-Italic.ttf).
Needs fonttools and brotli. Run before make_pages.py."""
import glob, hashlib, io, os, re
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "fonts", "src")
# Google Fonts' "latin" set (Basic Latin, Latin-1 with its accents, common punctuation, euro, trademark,
# minus) plus the arrows SideFrog uses. Covers everything on the site and what people type.
UNICODES = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2190-2199,U+2212,U+2215,U+FEFF,U+FFFD"
FONTS = [
    # (source file, output name, axis limits)
    ("Bricolage.ttf", "bricolage", {"wdth": 100, "wght": (400, 800), "opsz": (12, 96)}),
    ("SourceSerif4-Italic.ttf", "serif-italic", {"wght": 400, "opsz": 20}),
]

def build(src, name, limits):
    font = instancer.instantiateVariableFont(TTFont(os.path.join(SRC, src)), limits)
    tmp = io.BytesIO(); font.save(tmp); tmp.seek(0); font = TTFont(tmp)   # reopen before trimming (avoids a fonttools quirk)
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]; opts.name_IDs = ["*"]
    opts.hinting = False                      # phones and modern screens don't need hinting; it's a third of the file
    sub = subset.Subsetter(opts); sub.populate(unicodes=subset.parse_unicodes(UNICODES)); sub.subset(font)
    buf = io.BytesIO(); font.flavor = "woff2"; font.save(buf); data = buf.getvalue()
    out = f"{name}.{hashlib.sha1(data).hexdigest()[:8]}.woff2"
    for old in glob.glob(os.path.join(ROOT, "fonts", f"{name}.*.woff2")): os.remove(old)
    open(os.path.join(ROOT, "fonts", out), "wb").write(data)
    print(f"fonts/{out}: {len(data) // 1024} KB")
    return out

names = {name: build(src, name, lim) for src, name, lim in FONTS}
css_path = os.path.join(ROOT, "styles.css"); css = open(css_path, encoding="utf-8").read()
for name, out in names.items():
    css = re.sub(rf'url\("fonts/{name}\.[0-9a-f]+\.woff2"\)', f'url("fonts/{out}")', css)
open(css_path, "w", encoding="utf-8").write(css)
open(os.path.join(ROOT, "fonts", "fonts.txt"), "w").write("\n".join(f"{k} {v}" for k, v in names.items()) + "\n")
