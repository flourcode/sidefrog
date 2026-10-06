#!/usr/bin/env python3
"""Frank's profile pictures and the looping round sip video, from frank_art.py.
Writes frank-profile/: round Frank looking at you on cream, sage and ink (SVG and 800px PNG),
frank-sip-round.mp4 (1080x1080, two sips, opens on him looking at you) and a 480px GIF.
Needs cairosvg, Pillow and ffmpeg. Not part of the site."""
import io, os, shutil, subprocess, tempfile, cairosvg
from PIL import Image
import frank_art as fa
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, "frank-profile")
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
YOU = fa.FRAME["you"]
for bg in ("cream", "sage", "ink"):
    s = fa.round_svg(YOU, bg, uid=f"p-{bg}")
    open(os.path.join(OUT, f"frank-profile-{bg}.svg"), "w").write(s)
    open(os.path.join(OUT, f"frank-profile-{bg}.png"), "wb").write(cairosvg.svg2png(bytestring=s.encode(), output_width=800, output_height=800))
FPS, SIZE, CIRCLE = 30, 1080, 960
frames = {}
for i in set(fa.SIP_YOU):
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=fa.round_svg(i, "cream", uid=f"v{i}").encode(), output_width=CIRCLE, output_height=CIRCLE))).convert("RGBA")
    c = Image.new("RGBA", (SIZE, SIZE), (251, 247, 239, 255)); c.alpha_composite(im, ((SIZE - CIRCLE) // 2, (SIZE - CIRCLE) // 2))
    frames[i] = c.convert("RGB")
hold = {12: 1400, 10: 140, 9: 150, 8: 170, 7: 850}
seq = []
for loop in range(2):
    for n, i in enumerate(fa.SIP_YOU):
        ms = 1200 if (i == 12 and n == len(fa.SIP_YOU) - 1) else hold.get(i, 160)
        seq += [i] * max(1, round(ms / 1000 * FPS))
work = tempfile.mkdtemp()
for n, i in enumerate(seq): frames[i].save(f"{work}/f{n:04d}.png")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{work}/f%04d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "18", "-preset", "slow", "-movflags", "+faststart", os.path.join(OUT, "frank-sip-round.mp4")], check=True)
g = [frames[i].resize((480, 480), Image.LANCZOS) for i in seq[: len(seq) // 2]]
g[0].save(os.path.join(OUT, "frank-sip-round.gif"), save_all=True, append_images=g[1:], duration=int(1000 / FPS), loop=0, optimize=True)
shutil.rmtree(work)
print(f"frank-profile/: 3 profile pictures, a {len(seq) / FPS:.1f}s video and a GIF")
