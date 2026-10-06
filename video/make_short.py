#!/usr/bin/env python3
"""Frank Reviews Your Side Hustle: a repeatable YouTube Short (1080x1920, 25.6 seconds).

Make an episode: edit the EPISODE block below, save, then run
    python video/make_short.py
It writes, in the video folder:
    frank-short-NNN.mp4          the Short (with sound effects)
    frank-short-NNN-cover.png    the frame to pick as the thumbnail in YouTube (at 2.0 seconds)
    frank-short-NNN-verdict.png  the stamped verdict, for posts

The beats:
    0.0 - 3.0    the hook: the idea in big type; Frank looks at you, then makes his surprised "o".
                 The finished hook holds from about 1.6 to 3.0 s: that's the thumbnail frame.
    3.0 - 5.0    "Frank needs a sip for this one" (his real sip)
    5.0 - 14.0   Frank's three notes, 3 seconds each, with the face you choose for each
    14.0 - 18.0  the verdict, stamped onto Frank's memo
    18.0 - 22.0  the cheap test
    22.0 - 25.6  the ask (comment your idea); it ends on the opening frame, so it loops
Every text block shrinks to fit its space when it's long (and stays full size when it isn't).
Text stays out of the bottom fifth and the right edge, where YouTube puts the title and buttons.

Needs: Python with Pillow and numpy (pip install pillow numpy), and ffmpeg (winget install ffmpeg).
Frank comes from the pre-rendered images in video/frames/; the font from fonts/src/Bricolage.ttf.
If Frank's art ever changes:  python video/make_short.py --frames   (re-renders video/frames/;
that one also needs cairosvg and the project's frogs/ folder).
"""
import os, subprocess, sys, tempfile, shutil, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ================================================================ THE EPISODE: edit this block
EPISODE = {
    "number": 1,                                   # the episode number (shown on screen, used in file names)
    "hook": ["Meal kits", "for pet", "turtles?"],  # the idea, 1 to 4 short lines
    "notes": [                                     # three notes: (heading, one line, Frank's face)
        ("Who pays?", "People who own turtles. It's not a long line.", 2),
        ("The shipping", "Fresh greens on ice cost more to ship than to grow.", 4),
        ("The repeat order", "A turtle eats a little, for a very long time. Small, slow subscription.", 2),
    ],
    "re": "Meal kits for pet turtles",             # the memo's RE line
    "verdict": ["KEEP YOUR", "DAY JOB"],           # one of the five verdicts, as two lines (see VERDICTS)
    "verdict_face": 2,                             # Frank's face on the verdict card
    "reason": "Niche is far too small, and perishable logistics will eat your margin.",
    "cheap_test": "Before you buy a single cooler, ask two turtle-owner groups what they feed them now.",
}
# Frank's faces:  0 surprised "o"   1 smile, looking left   2 heavy lids (unimpressed)
#                 3 puzzled          4 skeptical frown       12 looking at you
VERDICTS = [["SURPRISINGLY,", "YES"], ["THIS COULD", "WORK"], ["CROWDED", "POND"],
            ["KEEP YOUR", "DAY JOB"], ["CAN'T HELP", "WITH THAT ONE"]]
FACES = {0, 1, 2, 3, 4, 12}

# ================================================================ layout and timing (no need to edit)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOLD = 0.6                                     # the finished hook holds 0.6 s longer: the thumbnail frame
W, H, FPS, DUR = 1080, 1920, 30, 25.0 + HOLD
COVER_T = 2.0                                  # the second to pick as the thumbnail
PAPER, CARD, INK, MUTED, DEEP, FROG, ACCENT, RULE = "#FBF7EF", "#FFFDF9", "#1F241F", "#5A5A4A", "#4A5C34", "#8DAA3F", "#A4501F", "#A89B84"
LEFT, TEXT_W = 90, 900                         # text column: left edge and width
TEXT_TOP = 300                                 # where each screen's text starts (under its label)
FRANK_SIZE, FRANK_Y = 480, 1130                # round Frank, centred
TEXT_BOTTOM = FRANK_Y - FRANK_SIZE // 2 - 30   # text must end above Frank
NOTE_BOTTOM = FRANK_Y - FRANK_SIZE // 2 + 12   # a note's last line may reach Frank's head (three full-size lines fit)
SR = 44100
FRAMES = os.path.join(HERE, "frames")
SIZES = [("round", 480), ("round", 240), ("cutout", 96)]   # the frame sizes the Short uses


def find_font():
    for p in (os.path.join(ROOT, "fonts", "src", "Bricolage.ttf"), os.path.expanduser("~/.fonts/Bricolage.ttf")):
        if os.path.exists(p):
            return p
    sys.exit("Can't find Bricolage.ttf: it should be at fonts/src/Bricolage.ttf in the project folder.")
FONT = find_font()
_fonts = {}
def font(size, weight=800, opsz=None):
    key = (size, weight, opsz)
    if key not in _fonts:
        f = ImageFont.truetype(FONT, size)
        f.set_variation_by_axes([opsz or (96 if size >= 60 else 14), weight, 100])
        _fonts[key] = f
    return _fonts[key]


def check_episode():
    """Catch mistakes in the EPISODE block with a plain message, before rendering anything."""
    e, problems = EPISODE, []
    if not 1 <= len(e["hook"]) <= 4: problems.append("hook: use 1 to 4 short lines")
    if len(e["notes"]) != 3: problems.append("notes: there must be exactly three")
    for n, note in enumerate(e["notes"], 1):
        if len(note) != 3: problems.append(f"note {n}: needs (heading, line, face)")
        elif note[2] not in FACES: problems.append(f"note {n}: face {note[2]} isn't one of {sorted(FACES)}")
    if e["verdict"] not in VERDICTS: problems.append(f"verdict: {e['verdict']} isn't one of {VERDICTS}")
    if e["verdict_face"] not in FACES: problems.append(f"verdict_face: {e['verdict_face']} isn't one of {sorted(FACES)}")
    for k in ("re", "reason", "cheap_test"):
        if not str(e.get(k, "")).strip(): problems.append(f"{k}: is empty")
    missing = [p for kind, size in SIZES for p in [frame_path(kind, size, 12)] if not os.path.exists(p)]
    if missing: problems.append("video/frames/ is missing Frank's images (unzip the full source again)")
    if problems:
        sys.exit("Fix the EPISODE block first:\n  - " + "\n  - ".join(problems))


# ================================================================ Frank, from pre-rendered frames
def frame_path(kind, size, i):
    return os.path.join(FRAMES, f"{kind}-{size}-{i:02d}.png")


def build_frames():
    """Re-render Frank's 13 frames at the Short's sizes from the approved art (needs cairosvg and frogs/)."""
    import cairosvg
    sys.path.insert(0, ROOT)
    import frank_art as fa
    os.makedirs(FRAMES, exist_ok=True)
    for kind, size in SIZES:
        for i in range(13):
            svg = fa.round_svg(i, "cream", uid=f"s{i}") if kind == "round" else fa.cutout(i)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=frame_path(kind, size, i), output_width=size, output_height=size)
    print(f"video/frames/: {13 * len(SIZES)} images")


_frank = {}
def frank(i, size, round_=False):
    key = (i, size, round_)
    if key not in _frank:
        _frank[key] = Image.open(frame_path("round" if round_ else "cutout", size, i)).convert("RGBA")
    return _frank[key]


def paste_center(img, im, cx, cy, scale=1.0):
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def round_frank(img, face, scale=1.0):
    paste_center(img, frank(face, FRANK_SIZE, round_=True), W // 2, FRANK_Y, scale=scale)


# ================================================================ text helpers
def ease(x):                                   # ease-out: fast start, gentle stop
    x = min(1, max(0, x)); return 1 - (1 - x) ** 3


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


_fit = {}
def fit_lines(d, lines, biggest, smallest, width, height, line_gap=1.03, weight=800, opsz=None):
    """The largest size (biggest down to smallest) at which these fixed lines fit width and height."""
    key = ("lines", tuple(lines), biggest, smallest, width, height, weight)
    if key not in _fit:
        size = smallest
        for sz in range(biggest, smallest - 1, -2):
            f = font(sz, weight, opsz)
            if all(d.textlength(l, font=f) <= width for l in lines) and len(lines) * sz * line_gap <= height:
                size = sz; break
        _fit[key] = size
    return _fit[key]


def fit_wrapped(d, text, biggest, smallest, width, height, line_gap=1.2, weight=800, opsz=None):
    """The largest size at which this text, wrapped to width, fits height. Returns (size, lines)."""
    key = ("wrap", text, biggest, smallest, width, height, weight)
    if key not in _fit:
        best = None
        for sz in range(biggest, smallest - 1, -2):
            f = font(sz, weight, opsz)
            lines = wrap(d, text, f, width)
            if len(lines) * sz * line_gap <= height and all(d.textlength(l, font=f) <= width for l in lines):
                best = (sz, lines); break
        _fit[key] = best or (smallest, wrap(d, text, font(smallest, weight, opsz), width))
    return _fit[key]


def kicker(d, text):
    d.text((LEFT, 250), text.upper(), font=font(30, 800, 14), fill=DEEP)


# ================================================================ the scenes
SIP = [(12, 0.25), (10, 0.12), (9, 0.12), (8, 0.14), (7, 0.7), (8, 0.14), (9, 0.12), (10, 0.12), (12, 0.29)]
def sip_frame(t):                              # Frank's sip, frame by frame (eyes on you)
    acc = 0
    for f, dur in SIP:
        acc += dur
        if t < acc: return f
    return 12


def scene_hook(img, d, t):
    kicker(d, f"Frank reviews your side hustle · No. {EPISODE['number']:03d}")
    lines = EPISODE["hook"]
    size = fit_lines(d, lines, 170, 84, TEXT_W, TEXT_BOTTOM - 330)
    for k, line in enumerate(lines):
        p = ease((t - 0.12 - k * 0.32) / 0.25)
        if p > 0:
            d.text((LEFT, 330 + k * size * 1.03 + (1 - p) * 40), line, font=font(size), fill=INK)
    face = 12 if t < 1.35 else 0               # looking at you, then the surprised "o"
    round_frank(img, face, scale=1.04 if 1.35 <= t < 1.6 else 1.0)


def scene_sip(img, d, t):
    kicker(d, "One moment")
    d.text((LEFT, TEXT_TOP), "Frank needs a", font=font(96), fill=INK)
    d.text((LEFT, TEXT_TOP + 110), "sip for this one.", font=font(96), fill=INK)
    round_frank(img, sip_frame(t))


def scene_note(img, d, t, n):
    head, line, face = EPISODE["notes"][n]
    p = ease(t / 0.3)
    kicker(d, "Frank's notes")
    slide = (1 - p) * 60
    d.text((LEFT - slide, TEXT_TOP), f"{n + 1:02d}", font=font(200), fill=FROG)
    hs = fit_lines(d, [head], 92, 56, TEXT_W, 120)
    d.text((LEFT - slide, 520), head, font=font(hs), fill=INK)
    bs, body = fit_wrapped(d, line, 62, 44, TEXT_W, NOTE_BOTTOM - 650, line_gap=1.32, weight=500, opsz=20)
    for k, l in enumerate(body):
        d.text((LEFT, 650 + k * bs * 1.32), l, font=font(bs, 500, 20), fill=INK)
    round_frank(img, face)


OVERSHOOT = 1.18                               # how much bigger the verdict lands before it settles
def scene_verdict(img, d, t):
    kicker(d, "The verdict")
    x, w = 70, 940
    y = 380 + (1 - ease(t / 0.35)) * 260       # the card slides up
    inner = w - 120
    lab = font(34, 800, 14)
    re_w = inner - d.textlength("RE: ", font=lab)
    rs = fit_lines(d, [EPISODE["re"]], 40, 30, re_w, 60, weight=400, opsz=14)
    re_text = EPISODE["re"]
    while d.textlength(re_text, font=font(rs, 400, 14)) > re_w and " " in re_text:   # still too long: trim with "…"
        re_text = re_text.rsplit(" ", 1)[0].rstrip(",;:") + "…"
        if d.textlength(re_text, font=font(rs, 400, 14)) <= re_w: break
        re_text = re_text[:-1]
    rf_size, reason = fit_wrapped(d, EPISODE["reason"], 52, 40, inner, 400, line_gap=1.27, weight=450, opsz=18)
    rline = int(rf_size * 1.27)
    h = 470 + len(reason) * rline + 70
    d.rounded_rectangle((x + 14, y + 14, x + w + 14, y + h + 14), 40, fill=INK)
    d.rounded_rectangle((x, y, x + w, y + h), 40, fill=CARD, outline=INK, width=5)
    d.text((x + 60, y + 60), "FROM:", font=lab, fill=ACCENT)
    d.text((x + 60 + d.textlength("FROM: ", font=lab), y + 56), "Frank", font=font(40, 400, 14), fill=MUTED)
    d.text((x + 60, y + 116), "RE:", font=lab, fill=ACCENT)
    d.text((x + 60 + d.textlength("RE: ", font=lab), y + 112 + (40 - rs) * 0.6), re_text, font=font(rs, 400, 14), fill=MUTED)
    d.rectangle((x + 60, y + 180, x + w - 60, y + 182), fill=RULE)
    st = (t - 0.75) / 0.22                      # the stamp: the verdict lands big and settles
    if st > 0:
        room = w - 60 - 280                     # from the verdict's left edge to just short of Frank
        size = fit_lines(d, EPISODE["verdict"], 100, 56, int(room / OVERSHOOT), 400)
        s = 1 + (OVERSHOOT - 1) * (1 - ease(st))
        for k, line in enumerate(EPISODE["verdict"]):
            d.text((x + 60, y + 230 + k * int(size * 0.98 * s)), line, font=font(int(size * s)), fill=INK)
    paste_center(img, frank(EPISODE["verdict_face"], 240, round_=True), x + w - 50 - 120, y + 320)
    for k, l in enumerate(reason):
        d.text((x + 60, y + 470 + k * rline), l, font=font(rf_size, 450, 18), fill=INK)


def scene_test(img, d, t):
    p = ease(t / 0.3)
    kicker(d, "The cheap test")
    size, lines = fit_wrapped(d, EPISODE["cheap_test"], 84, 56, TEXT_W, TEXT_BOTTOM - TEXT_TOP, line_gap=1.19)
    for k, l in enumerate(lines):
        d.text((LEFT + (1 - p) * 50, TEXT_TOP + 10 + k * size * 1.19), l, font=font(size), fill=INK)
    round_frank(img, 12)


def scene_ask(img, d, t):
    kicker(d, "Your turn")
    d.text((LEFT, TEXT_TOP), "Got a worse idea?", font=font(100), fill=INK)
    d.text((LEFT, 440), "Comment it.", font=font(66, 500, 20), fill=INK)
    d.text((LEFT, 525), "Frank reviews one next.", font=font(66, 500, 20), fill=INK)
    round_frank(img, 12 if t < 1.6 else sip_frame(t - 1.6))


def note(n):
    return lambda img, d, t: scene_note(img, d, t, n)
SCENES = [(0.0, 2.4 + HOLD, scene_hook), (2.4 + HOLD, 4.4 + HOLD, scene_sip),
          (4.4 + HOLD, 7.4 + HOLD, note(0)), (7.4 + HOLD, 10.4 + HOLD, note(1)), (10.4 + HOLD, 13.4 + HOLD, note(2)),
          (13.4 + HOLD, 17.4 + HOLD, scene_verdict), (17.4 + HOLD, 21.4 + HOLD, scene_test), (21.4 + HOLD, DUR, scene_ask)]


def render(t):
    img = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    img.alpha_composite(frank(12, 96), (78, 96))            # the masthead: logo Frank, SideFrog, a rule
    d.text((184, 128), "SideFrog", font=font(52), fill=INK)
    d.rectangle((LEFT, 214, W - LEFT, 217), fill=INK)
    for a, b, fn in SCENES:
        if a <= t < b:
            fn(img, d, t - a); break
    url, tag = font(64), font(32, 600, 14)                  # always on screen, above YouTube's title band
    d.text(((W - d.textlength("sidefrog.com", font=url)) / 2, 1405), "sidefrog.com", font=url, fill=DEEP)
    d.text(((W - d.textlength("For people who hate Mondays.", font=tag)) / 2, 1488), "For people who hate Mondays.", font=tag, fill=MUTED)
    return img.convert("RGB")


# ================================================================ sound effects (no music)
def sfx():
    n = int(DUR * SR); out = np.zeros(n)
    rng = np.random.default_rng(7)
    def add(t0, sig, gain):
        i = int(t0 * SR); j = min(n, i + len(sig)); out[i:j] += sig[: j - i] * gain
    def noise(sec, smooth):
        return np.convolve(rng.standard_normal(int(sec * SR)), np.ones(smooth) / smooth, mode="same")
    def env(sig, attack=0.005, decay=6.0):
        tt = np.arange(len(sig)) / SR
        return sig * np.minimum(1, tt / attack) * np.exp(-decay * tt)
    def tone(freq, sec, decay=8.0):
        tt = np.arange(int(sec * SR)) / SR
        return env(np.sin(2 * np.pi * freq * tt), 0.003, decay)
    def swell(sig, power=1.0):
        return sig * np.sin(np.linspace(0, np.pi, len(sig))) ** power
    add(0.0, swell(noise(0.35, 30)), 0.08)                                  # whoosh in
    for k in range(len(EPISODE["hook"])):                                   # a pop for each hook line
        add(0.12 + k * 0.32, tone(520 + k * 90, 0.12, 30), 0.12)
    add(1.35, tone(880, 0.18, 18) + tone(1320, 0.18, 22) * 0.5, 0.1)        # Frank's "o"
    for t0 in (3.28 + HOLD, 3.6 + HOLD):                                    # the sip
        add(t0, swell(noise(0.25, 6) - noise(0.25, 40), 1.5), 0.12)
    for k in range(3):                                                      # each note slides in
        add(4.4 + HOLD + k * 3, swell(noise(0.22, 20), 2), 0.09)
    add(13.7 + HOLD, env(noise(0.3, 12), 0.002, 18), 0.25)                  # the card lands
    thud = tone(70, 0.4, 9); slap = env(noise(0.08, 3), 0.001, 60) * 0.6
    thud[: len(slap)] += slap
    add(14.37 + HOLD, thud, 0.55)                                           # the stamp
    add(17.4 + HOLD, tone(660, 0.15, 25), 0.08)                             # the cheap test
    add(21.4 + HOLD, tone(988, 0.25, 10) + tone(1480, 0.25, 12) * 0.4, 0.1) # your turn
    out = out / max(1e-9, np.abs(out).max()) * 0.85
    return (out * 32767).astype(np.int16)


# ================================================================ make the Short
def main():
    check_episode()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg isn't installed (on Windows: winget install ffmpeg, then open a new PowerShell).")
    work = tempfile.mkdtemp()
    try:
        nframes = int(DUR * FPS)
        for k in range(nframes):
            render(k / FPS).save(f"{work}/f{k:04d}.png")
        wav = f"{work}/sfx.wav"
        with wave.open(wav, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(sfx().tobytes())
        base = os.path.join(HERE, f"frank-short-{EPISODE['number']:03d}")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{work}/f%04d.png", "-i", wav,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "slow", "-c:a", "aac", "-b:a", "160k",
                        "-shortest", "-movflags", "+faststart", base + ".mp4"], check=True)
        render(COVER_T).save(base + "-cover.png")
        render(13.4 + HOLD + 1.6).save(base + "-verdict.png")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"{base}.mp4 ({nframes} frames, {DUR:.1f}s)")
    print(f"Thumbnail: in YouTube, pick the frame at {COVER_T:.1f} seconds (see {os.path.basename(base)}-cover.png)")


if __name__ == "__main__":
    build_frames() if "--frames" in sys.argv else main()
