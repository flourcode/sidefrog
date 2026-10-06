#!/usr/bin/env python3
"""Builds Frank's sprite: the approved frames in frogs/src/ in name order (5 verdict faces, sip frames 2-8,
then the straight-ahead resting frame),
rendered at 320px with a transparent background into one horizontal strip, saved as
frogs/frank-sprite.<hash>.webp, and the stylesheet pointed at it. Run after changing any frame.
Needs cairosvg and Pillow."""
import glob, hashlib, io, os, re, cairosvg
from PIL import Image
ROOT=os.path.dirname(os.path.abspath(__file__)); SIZE=320
files=sorted(glob.glob(os.path.join(ROOT,"frogs","src","frank-*.svg")))
strip=Image.new("RGBA",(SIZE*len(files),SIZE),(0,0,0,0))
for i,f in enumerate(files):
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=f, output_width=SIZE, output_height=SIZE))).convert("RGBA")
    strip.paste(im,(i*SIZE,0),im)
buf=io.BytesIO(); strip.save(buf,"WEBP",lossless=False,quality=92,method=6,alpha_quality=100)
digest=hashlib.sha1(buf.getvalue()).hexdigest()[:8]
for old in glob.glob(os.path.join(ROOT,"frogs","frank-sprite.*.webp")): os.remove(old)
name=f"frank-sprite.{digest}.webp"
open(os.path.join(ROOT,"frogs",name),"wb").write(buf.getvalue())
css_path=os.path.join(ROOT,"styles.css"); css=open(css_path).read()
css=re.sub(r'url\("frogs/frank-sprite\.[0-9a-f]+\.webp"\)', f'url("frogs/{name}")', css)
n=len(files)
css=re.sub(r'background-size: \d+% 100%; background-position: calc\(var\(--frame, 1\) \* 100% / \d+\) 0;',
           f'background-size: {n*100}% 100%; background-position: calc(var(--frame, 1) * 100% / {n-1}) 0;', css)
open(css_path,"w").write(css)
print(f"frogs/{name}: {len(files)} frames at {SIZE}px, {len(buf.getvalue())//1024} KB")

# The round sprite: the same frames in the calculated circle (frank_art.py), transparent around him,
# so CSS gives the circle its colour. Used for round Frank on the site (About) and the share card.
import sys
sys.path.insert(0, ROOT)
import frank_art
rstrip=Image.new("RGBA",(SIZE*len(files),SIZE),(0,0,0,0))
for i in range(len(files)):
    svg=frank_art.round_svg(i, bg=None, uid=f"r{i}")
    im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=SIZE, output_height=SIZE))).convert("RGBA")
    rstrip.paste(im,(i*SIZE,0),im)
rbuf=io.BytesIO(); rstrip.save(rbuf,"WEBP",lossless=False,quality=92,method=6,alpha_quality=100)
rname=f"frank-round.{hashlib.sha1(rbuf.getvalue()).hexdigest()[:8]}.webp"
for old in glob.glob(os.path.join(ROOT,"frogs","frank-round.*.webp")): os.remove(old)
open(os.path.join(ROOT,"frogs",rname),"wb").write(rbuf.getvalue())
css=open(css_path).read()
css=re.sub(r'url\("frogs/frank-round\.[0-9a-f]+\.webp"\)', f'url("frogs/{rname}")', css)
open(css_path,"w").write(css)
print(f"frogs/{rname}: round, {len(rbuf.getvalue())//1024} KB")
