#!/usr/bin/env python3
r"""Frank Reviews Your Side Hustle: a repeatable YouTube Short (1080x1920, 30 seconds = 15 bars at 120 BPM;
26 seconds = 13 bars for an older episode without "take").

Make an episode: edit the EPISODE block below, save, then run
    python video/make_short.py
or, with an episode file from the Short Studio page (tools/frank-short-studio.html):
    python video/make_short.py latest              (the newest episode file in your Downloads folder)
    python video/make_short.py path/to/episode-010.json
or stitch several finished Shorts into one widescreen video (see video/stitch.py):
    python video/make_short.py stitch          (the latest 5 posted episodes)
    python video/make_short.py stitch 3 8 9 10
or make a list Short of three episodes (see video/listshort.py), or the playbook (video/make_playbook.py):
    python video/make_short.py list free        python video/make_short.py playbook
or make a 10-second cheap-test cutdown of an episode (see video/cheaptest.py):
    python video/make_short.py cheaptest 11
Each episode gets its own folder next to this tool, e.g. with the tool in SideFrog\shorts-kit:
    SideFrog\episodes\011-mobile-car-wash\
        <name>.mp4            the Short (with its music loop and sound effects)
        <name>-cover.png      the frame to pick as the thumbnail in YouTube (at 2.0 seconds)
        <name>-verdict.png    the stamped verdict, for posts
        episode-011.json      the episode (moved out of Downloads, or saved from the EPISODE block)
        sidefrog-episode-011-package.txt   the YouTube package, if you saved one (moved out of Downloads)
    SideFrog\episode-log.csv  one row per episode, with columns for the YouTube link and views
<name> comes from the Short Studio's file name (e.g. sidefrog-011-short-mobile-car-wash), else frank-short-NNN.

The beats:
    0.0 - 3.0    the hook: "Can this actually make money?" over the idea in big type; Frank looks at
                 you, then makes his surprised "o".
                 Lines land on the beat (0.5, 1.0, 1.5 s); the "o" on the downbeat at 2.0 s; pick 2.5 s as the thumbnail.
    3.0 - 5.0    "Frank needs a sip for this one" (his real sip)
    5.0 - 14.0   Frank's three notes, 3 seconds each, with the face you choose for each
    14.0 - 18.0  the verdict, stamped onto Frank's memo, then Frank's scorecard under it, one item per
                 beat (16.0, 16.5, 17.0 s): easy to start?, first dollar in, the test costs
    18.0 - 22.0  the cheap test, with what it costs in the label ("The cheap test · about $40")
    22.0 - 26.0  Frank's take: Mark's own line of advice, in his words (the episode's "take"). This is
                 what shows a person's judgment behind every episode, not a template filled in by AI.
    26.0 - 30.0  the ask: "Would you try it? Yes or no." (one word to answer, so people do);
                 it ends on the opening frame, so it loops
    An episode without a "take" (an older file) skips that scene and runs 26 seconds, as before.
    The hook's question can change per episode ("question"): the Studio rotates through a few.
Rhythm: a code-made music loop at 120 BPM (keys, bass, hats, a kick from the verdict on); every
scene change, line, pop and the stamp land on a beat, text arrives with a little weight (it
overshoots and settles), and the last bar leads musically back into the first, so it loops cleanly.
Every text block shrinks to fit its space when it's long (and stays full size when it isn't).
The look is SideFrog "after hours": the site's colors on dark (ink background, cream text, avocado
numbers), with the memo card and Frank's disc light, so YouTube's and LinkedIn's white buttons and
captions read clearly. sidefrog.com sits in the masthead; the bottom fifth is left for YouTube.
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
    # Frank's scorecard, shown under the verdict (leave any of these out to skip it):
    "ease": "some_setup",                          # easy, some_setup or hard
    "first_dollar": "2 to 3 months",               # how soon a first sale could come, as a time
    "test_cost": "$0",                             # what the cheap test costs, as money
    # Frank's take: your own line of advice, in your words (not Frank's AI answer). Shown after the test.
    "take": "If the turtle people bite, sell a printable feeding guide first. No ice required.",
}
# Frank's faces:  0 surprised "o"   1 smile, looking left   2 heavy lids (unimpressed)
#                 3 puzzled          4 skeptical frown       12 looking at you
# The recurring question above the big topic on the hook screen (an episode can set its own "question")
HOOK_QUESTION = "Can this actually make money?"
VERDICTS = [["SURPRISINGLY,", "YES"], ["THIS COULD", "WORK"], ["CROWDED", "POND"],
            ["KEEP YOUR", "DAY JOB"], ["CAN'T HELP", "WITH THAT ONE"]]
FACES = {0, 1, 2, 3, 4, 12}
EASE = {"easy": "Easy", "some_setup": "Some setup", "hard": "Hard"}
ASK = ["Would you try it?", "Yes or no.", "Tell Frank in the comments."]   # easy to answer in one word

# ================================================================ layout and timing (no need to edit)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOLD = 0.6                                     # the finished hook holds 0.6 s longer: the thumbnail frame
BPM, BEAT, BAR = 120, 0.5, 2.0                 # everything lands on a beat; the Short is 13 bars long
W, H, FPS, DUR = 1080, 1920, 30, 26.0           # a whole number of bars, so the music loops without a jump
COVER_T = 2.5                                  # the second to pick as the thumbnail: the full hook and the "o"
# SideFrog "after hours": the site's own colors on dark, so YouTube's and LinkedIn's white controls
# and captions read clearly. The memo card and Frank's cream disc stay light: the bright focal points.
BG, TEXT, SUBTLE, LABEL, FROG = "#1F241F", "#FBF7EF", "#BEB49F", "#8DAA3F", "#8DAA3F"   # ink, paper, taupe, avocado
CARD, CARD_INK, CARD_MUTED, ACCENT, RULE, SHADOW = "#FFFDF9", "#1F241F", "#5A5A4A", "#A4501F", "#A89B84", "#121311"
ACCENT_ON_DARK = "#E08A55"                     # the burnt accent, lifted so it reads on the dark background
LEFT, TEXT_W = 90, 900                         # text column: left edge and width
TEXT_TOP = 300                                 # where each screen's text starts (under its label)
FRANK_SIZE, FRANK_Y = 504, 1050                # round Frank, centred, clear of YouTube's channel and title
TEXT_BOTTOM = FRANK_Y - FRANK_SIZE // 2 - 30   # text must end above Frank
NOTE_BOTTOM = FRANK_Y - FRANK_SIZE // 2 + 12   # a note's last line may reach Frank's head (three full-size lines fit)
SR = 44100
FRAMES = os.path.join(HERE, "frames")
EPISODES = os.path.join(os.path.dirname(ROOT), "episodes")   # SideFrog/episodes, beside the shorts-kit folder
LOG = os.path.join(os.path.dirname(ROOT), "episode-log.csv")
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
SIZES = [("round", 504), ("round", 240), ("cutout", 96)]   # the frame sizes the Short uses


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
    if e.get("ease") and e["ease"] not in EASE: problems.append(f"ease: use one of {list(EASE)} (or leave it out)")
    if e.get("test_cost") and "$" not in str(e["test_cost"]): problems.append("test_cost: write it as money, like \"$0\" or \"about $40\"")
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


def ease_back(x, s=1.4):                       # lands a touch past its spot and settles back: weight
    x = min(1, max(0, x)); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def land(t, beat, dur=0.25):
    """Progress of something that lands exactly on `beat` (seconds into the scene), arriving over `dur`."""
    return ease_back((t - (beat - dur)) / dur)


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
    d.text((LEFT, 250), text.upper(), font=font(30, 800, 14), fill=LABEL)


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
    # the recurring question (medium, the same every episode), then the topic, huge
    question = EPISODE.get("question") or HOOK_QUESTION
    qs = fit_lines(d, [question], 66, 40, TEXT_W, 80, weight=700, opsz=40)
    d.text((LEFT, TEXT_TOP + 4), question, font=font(qs, 700, 40), fill=TEXT)
    top = TEXT_TOP + 4 + int(qs * 1.45)
    lines = EPISODE["hook"]
    size = fit_lines(d, lines, 170, 84, TEXT_W, TEXT_BOTTOM - top)
    for k, line in enumerate(lines):          # one line per beat: 0.5, 1.0, 1.5 s
        p = land(t, BEAT * (k + 1))
        if t >= BEAT * (k + 1) - 0.25:
            d.text((LEFT, top + k * size * 1.03 + (1 - p) * 46), line, font=font(size), fill=TEXT)
    face = 12 if t < 2.0 else 0                # looking at you, then the surprised "o" on the downbeat
    round_frank(img, face, scale=1 + 0.05 * (1 - ease((t - 2.0) / 0.3)) if t >= 2.0 else 1.0)


def scene_sip(img, d, t):
    kicker(d, "One moment")
    d.text((LEFT, TEXT_TOP), "Frank needs a", font=font(96), fill=TEXT)
    d.text((LEFT, TEXT_TOP + 110), "sip for this one.", font=font(96), fill=TEXT)
    round_frank(img, sip_frame(t))


def scene_note(img, d, t, n):
    head, line, face = EPISODE["notes"][n]
    kicker(d, "Frank's notes")
    p0 = land(t, 0.15, 0.15)                   # the number lands with the downbeat
    d.text((LEFT - (1 - p0) * 70, TEXT_TOP - 10), f"{n + 1:02d}", font=font(170), fill=FROG)
    hs = fit_lines(d, [head], 92, 56, TEXT_W, 120)
    if t >= BEAT - 0.25:                       # the heading on the next beat
        p1 = land(t, BEAT)
        d.text((LEFT - (1 - p1) * 50, 480), head, font=font(hs), fill=TEXT)
    bs, body = fit_wrapped(d, line, 62, 44, TEXT_W, NOTE_BOTTOM - 600, line_gap=1.32, weight=500, opsz=20)
    if t >= 2 * BEAT - 0.25:                   # the line on the beat after
        p2 = land(t, 2 * BEAT)
        for k, l in enumerate(body):
            d.text((LEFT, 600 + k * bs * 1.32 + (1 - p2) * 30), l, font=font(bs, 500, 20), fill=TEXT)
    round_frank(img, face, scale=1 + 0.03 * (1 - ease(t / 0.3)))   # a small bump as the face changes


OVERSHOOT = 1.18                               # how much bigger the verdict lands before it settles
def scene_verdict(img, d, t):
    kicker(d, "The verdict")
    x, w = 70, 860                             # its right edge stays clear of YouTube's button column
    y = 380 + (1 - ease_back(t / 0.4, 1.0)) * 260   # the card slides up and settles
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
    d.rounded_rectangle((x + 14, y + 14, x + w + 14, y + h + 14), 40, fill=SHADOW)
    d.rounded_rectangle((x, y, x + w, y + h), 40, fill=CARD, outline=CARD_INK, width=5)
    d.text((x + 60, y + 60), "FROM:", font=lab, fill=ACCENT)
    d.text((x + 60 + d.textlength("FROM: ", font=lab), y + 56), "Frank", font=font(40, 400, 14), fill=CARD_MUTED)
    d.text((x + 60, y + 116), "RE:", font=lab, fill=ACCENT)
    d.text((x + 60 + d.textlength("RE: ", font=lab), y + 112 + (40 - rs) * 0.6), re_text, font=font(rs, 400, 14), fill=CARD_MUTED)
    d.rectangle((x + 60, y + 180, x + w - 60, y + 182), fill=RULE)
    st = (t - 0.78) / 0.22                      # the stamp lands exactly on the beat (1.0 s in)
    if st > 0:
        room = w - 60 - 280                     # from the verdict's left edge to just short of Frank
        size = fit_lines(d, EPISODE["verdict"], 100, 56, int(room / OVERSHOOT), 400)
        s = 1 + (OVERSHOOT - 1) * (1 - ease(st))
        for k, line in enumerate(EPISODE["verdict"]):
            d.text((x + 60, y + 230 + k * int(size * 0.98 * s)), line, font=font(int(size * s)), fill=CARD_INK)
    paste_center(img, frank(EPISODE["verdict_face"], 240, round_=True), x + w - 50 - 120, y + 320)
    for k, l in enumerate(reason):
        d.text((x + 60, y + 470 + k * rline), l, font=font(rf_size, 450, 18), fill=CARD_INK)
    scorecard(d, t, x, y + h + 50, w)


def score_items():
    """Frank's scorecard: (label, value) for each one the episode has."""
    cap = lambda v: str(v).strip()[:1].upper() + str(v).strip()[1:]
    items = [("Easy to start?", EASE.get(EPISODE.get("ease"), "")),
             ("First dollar in", cap(EPISODE.get("first_dollar", ""))),
             ("The test costs", cap(EPISODE.get("test_cost", "")))]
    return [(a, b) for a, b in items if b]


def scorecard(d, t, x, y, w):
    """Under the stamped verdict, one row per beat (2.0, 2.5, 3.0 s into the verdict): how easy it is
    to start, how soon a first dollar could come, and what the test costs. Rows stay above YouTube's
    bottom fifth; they get shorter (and the type smaller) when a long reason pushes the card down."""
    items = score_items()
    if not items: return
    row = min(104, (int(H * 0.8) - y) // len(items))
    label_w = 330
    size = min(fit_lines(d, [v], 64, 34, w - label_w, int(row * 0.8), weight=800) for _, v in items)
    for k, (label, value) in enumerate(items):
        when = 2.0 + k * BEAT
        if t < when - 0.2: continue
        p = land(t, when, 0.2)
        ry = y + k * row
        d.rectangle((x, ry, x + w, ry + 1), fill=RULE)
        dx = (1 - p) * 40
        d.text((x + dx, ry + row / 2 + 1), label.upper(), font=font(28, 800, 14), fill=SUBTLE, anchor="lm")
        color = TEXT
        if k == 0 and EPISODE.get("ease") == "easy": color = LABEL
        if k == 0 and EPISODE.get("ease") == "hard": color = ACCENT_ON_DARK
        d.text((x + label_w + dx, ry + row / 2), value, font=font(size), fill=color, anchor="lm")
    if t >= 2.0 + (len(items) - 1) * BEAT - 0.2:   # the closing rule arrives with the last row
        d.rectangle((x, y + len(items) * row, x + w, y + len(items) * row + 1), fill=RULE)


def scene_test(img, d, t):
    cost = str(EPISODE.get("test_cost", "")).strip()
    kicker(d, f"The cheap test · {cost}" if cost else "The cheap test")
    size, lines = fit_wrapped(d, EPISODE["cheap_test"], 84, 56, TEXT_W, TEXT_BOTTOM - TEXT_TOP, line_gap=1.19)
    for k, l in enumerate(lines):              # one line per beat, the first on the downbeat
        when = 0.15 + k * BEAT
        if t >= when - 0.15:
            p = land(t, when, 0.15 if k == 0 else 0.25)
            d.text((LEFT + (1 - p) * 50, TEXT_TOP + 10 + k * size * 1.19), l, font=font(size), fill=TEXT)
    round_frank(img, 12)


def scene_take(img, d, t):
    """Mark's own advice, in Frank's voice: a big avocado quote mark, then the line, one line per beat."""
    kicker(d, "Frank's take")
    d.text((LEFT - 6, TEXT_TOP - 40), "\u201c", font=font(200), fill=LABEL)
    top = TEXT_TOP + 110
    size, lines = fit_wrapped(d, EPISODE["take"].strip(), 80, 50, TEXT_W, TEXT_BOTTOM - top, line_gap=1.2)
    for k, l in enumerate(lines):
        when = 0.15 + k * BEAT
        if t >= when - 0.15:
            p = land(t, when, 0.15 if k == 0 else 0.25)
            d.text((LEFT + (1 - p) * 50, top + k * size * 1.2), l, font=font(size), fill=TEXT)
    round_frank(img, 1, scale=1 + 0.03 * (1 - ease(t / 0.3)))


def scene_ask(img, d, t):
    kicker(d, "Your turn")
    big = fit_lines(d, [ASK[0]], 100, 70, TEXT_W, 120)
    for k, (y, text, f) in enumerate(((TEXT_TOP, ASK[0], font(big)), (440, ASK[1], font(66, 500, 20)),
                                      (525, ASK[2], font(66, 500, 20)))):
        when = 0.15 + k * BEAT
        if t >= when - 0.15:
            p = land(t, when, 0.15 if k == 0 else 0.25)
            d.text((LEFT, y + (1 - p) * 34), text, font=f, fill=TEXT)
    round_frank(img, 12 if t < 2.0 else sip_frame(t - 2.0))


def note(n):
    return lambda img, d, t: scene_note(img, d, t, n)
def has_take():
    return bool(str(EPISODE.get("take", "")).strip())


def set_timeline():
    """30 seconds with Frank's take, 26 without (older episode files): whole bars either way."""
    global DUR, SCENES, ASK_T
    ASK_T = 26.0 if has_take() else 22.0
    DUR = ASK_T + 4.0
    SCENES = [(0.0, 3.0, scene_hook), (3.0, 5.0, scene_sip),            # every change lands on a beat
              (5.0, 8.0, note(0)), (8.0, 11.0, note(1)), (11.0, 14.0, note(2)),
              (14.0, 18.0, scene_verdict), (18.0, 22.0, scene_test)]
    if has_take():
        SCENES.append((22.0, 26.0, scene_take))
    SCENES.append((ASK_T, DUR, scene_ask))
set_timeline()


def render(t):
    img = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(img)
    # the masthead: logo Frank, sidefrog.com and the tagline, set in from the left so YouTube's back
    # arrow doesn't cover Frank; the address lives up here, where no overlay ever sits
    img.alpha_composite(frank(12, 96), (128, 98))
    d.text((236, 106), "sidefrog.com", font=font(50), fill=TEXT)
    d.text((238, 162), "For people who hate Mondays.", font=font(26, 600, 14), fill=SUBTLE)
    d.rectangle((LEFT, 214, W - LEFT, 217), fill=SUBTLE)
    for a, b, fn in SCENES:
        if a <= t < b:
            fn(img, d, t - a); break
    return img.convert("RGB")


# ================================================================ sound effects (no music)
# ---------------------------------------------------------------- the music: a loop made in code (nothing to license)
# Warm electric-piano chords, a round bass, brushed hats and a soft kick at 120 BPM. Chords run
# F maj7, D m7, Bb maj7, C7 every 4 bars; the final bar is always C7, which leads back into the
# opening F maj7, and anything still ringing at the end wraps around into the start: no seam.
CHORDS = [(174.61, 220.00, 261.63, 329.63), (146.83, 174.61, 220.00, 261.63),
          (116.54, 146.83, 174.61, 220.00), (130.81, 164.81, 196.00, 233.08)]
ROOTS = [87.31, 73.42, 58.27, 65.41]


def music(dur, levels, seed=3):
    """One bar per entry in `levels`: 0 = keys and bass, 1 = adds hats and a rim click, 2 = adds a kick."""
    n = int(dur * SR); out = np.zeros(n + 4 * SR); rng = np.random.default_rng(seed)
    def put(t0, sig, gain):
        i = int(t0 * SR); out[i:i + len(sig)] += sig * gain
    def release(sig, sec=0.08):               # every note fades out instead of stopping dead (no clicks)
        k = min(len(sig), int(sec * SR)); sig = sig.copy(); sig[-k:] *= np.linspace(1, 0, k); return sig
    def keys(freqs, sec):
        tt = np.arange(int(sec * SR)) / SR
        sig = sum(np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt) for f in freqs)
        return release(sig * np.minimum(1, tt / 0.008) * np.exp(-2.2 * tt) * (1 + 0.06 * np.sin(2 * np.pi * 5 * tt)))
    def bass(f, sec):
        tt = np.arange(int(sec * SR)) / SR
        sig = np.tanh(1.6 * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)))
        return release(sig * np.minimum(1, tt / 0.01) * np.exp(-3.0 * tt))
    def hat(sec=0.05):
        x = rng.standard_normal(int(sec * SR)); x = x - np.convolve(x, np.ones(6) / 6, mode="same")
        return x * np.exp(-np.arange(len(x)) / SR * 70)
    def kick():
        tt = np.arange(int(0.3 * SR)) / SR
        return np.sin(2 * np.pi * (45 * tt + 75 / 18 * (1 - np.exp(-18 * tt)))) * np.exp(-9 * tt)
    def rim():
        tt = np.arange(int(0.06 * SR)) / SR
        return (np.sin(2 * np.pi * 1700 * tt) + 0.6 * rng.standard_normal(len(tt))) * np.exp(-60 * tt)
    bars = len(levels)
    for b, lvl in enumerate(levels):
        c = 3 if b == bars - 1 else b % 4        # the last bar is always the C7 turnaround
        t0 = b * BAR
        put(t0, keys(CHORDS[c], 2.2), 0.10); put(t0 + 1.25, keys(CHORDS[c], 1.3), 0.06)       # beat 1 and the "and" of 3,
        put(t0, bass(ROOTS[c], 1.1), 0.30); put(t0 + 1.0, bass(ROOTS[c] * 1.5, 1.1), 0.22)     # ringing into the next bar
        if lvl >= 1:
            for e in range(8): put(t0 + e * 0.25, hat(), 0.05 if e % 2 else 0.08)
            for bt in (1, 3): put(t0 + bt * BEAT, rim(), 0.07)
        if lvl >= 2:
            for bt in (0, 2): put(t0 + bt * BEAT, kick(), 0.45)
    out[: 4 * SR] += out[n:n + 4 * SR]          # the tail wraps into the start
    return out[:n]


def sfx():
    """The music bed plus the sound effects, every one on a beat. Returns 16-bit samples."""
    n = int(DUR * SR); fx = np.zeros(n)
    rng = np.random.default_rng(7)
    def add(t0, sig, gain):
        i = int(t0 * SR); j = min(n, i + len(sig)); fx[i:j] += sig[: j - i] * gain
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
    for k in range(len(EPISODE["hook"])):                                   # a pop as each hook line lands
        add(BEAT * (k + 1) - 0.02, tone(523.25 * (1.12246 ** (2 * k)), 0.12, 30), 0.10)
    add(2.0, tone(880, 0.18, 18) + tone(1320, 0.18, 22) * 0.5, 0.09)        # Frank's "o", on the downbeat
    for t0 in (3.88, 4.2):                                                  # the sip
        add(t0, swell(noise(0.25, 6) - noise(0.25, 40), 1.5), 0.11)
    for k in range(3):                                                      # each note's number
        add(5.0 + k * 3 - 0.08, swell(noise(0.18, 20), 2), 0.08)
    add(14.25, env(noise(0.3, 12), 0.002, 18), 0.22)                        # the card lands
    thud = tone(70, 0.4, 9); slap = env(noise(0.08, 3), 0.001, 60) * 0.6
    thud[: len(slap)] += slap
    add(15.0, thud, 0.55)                                                   # the stamp, on the beat
    for k in range(len(score_items())):                                     # each scorecard item, a soft tick
        add(16.0 + k * BEAT - 0.01, tone(1046.5 * (1.12246 ** k), 0.08, 40), 0.05)
    add(18.0, tone(659.25, 0.15, 25), 0.07)                                 # the cheap test
    if has_take():
        add(22.0, tone(783.99, 0.18, 20) + tone(1174.66, 0.18, 24) * 0.4, 0.07)   # Frank's take
    add(ASK_T, tone(987.77, 0.25, 10) + tone(1479.98, 0.25, 12) * 0.4, 0.08)  # your turn
    levels = [0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2] + ([1, 1] if has_take() else []) + [0, 0]   # light, notes, verdict and test, take, light again
    mix = music(DUR, levels) * 0.55 + fx
    mix = mix / max(1e-9, np.abs(mix).max()) * 0.85
    return (mix * 32767).astype(np.int16)


# ================================================================ make the Short
def output_stem():
    """The video's file name: the episode's "filename" (from the Short Studio), or frank-short-NNN."""
    name = os.path.basename(str(EPISODE.get("filename", "")).strip())
    stem = name[:-4] if name.lower().endswith(".mp4") else name
    stem = "".join(c for c in stem if c.isalnum() or c in "-_")
    return stem or f"frank-short-{EPISODE['number']:03d}"


def episode_folder():
    """The episode's folder, e.g. episodes/011-mobile-car-wash: its number plus the idea."""
    import re as _re
    stem = output_stem()
    slug = _re.sub(r"^(sidefrog|frank)-short-|^sidefrog-\d+-short-", "", stem)
    if _re.fullmatch(r"\d+", slug) or not slug:
        slug = _re.sub(r"[^a-z0-9]+", "-", str(EPISODE.get("re", "")).lower()).strip("-")[:42] or "episode"
    return os.path.join(EPISODES, f"{EPISODE['number']:03d}-{slug}")


def file_episode(folder):
    """Move this episode's file and its YouTube package out of Downloads into its folder (or save the
    EPISODE block there), and add a row to episode-log.csv."""
    import json, glob, csv, datetime
    n = f"{EPISODE['number']:03d}"
    dest_json = os.path.join(folder, f"episode-{n}.json")
    if SOURCE_FILE and os.path.abspath(SOURCE_FILE) != os.path.abspath(dest_json):
        from_downloads = os.path.dirname(os.path.abspath(SOURCE_FILE)) == os.path.abspath(DOWNLOADS)
        try:                                   # tidy Downloads; leave files kept anywhere else where they are
            (shutil.move if from_downloads else shutil.copy2)(SOURCE_FILE, dest_json)
        except OSError:
            shutil.copy2(SOURCE_FILE, dest_json)
    elif not SOURCE_FILE:
        with open(dest_json, "w", encoding="utf-8") as f: json.dump(EPISODE, f, indent=2)
    packages = glob.glob(os.path.join(DOWNLOADS, f"sidefrog-episode-{n}-package*.txt"))
    if packages:
        newest = max(packages, key=os.path.getmtime)
        dest = os.path.join(folder, f"sidefrog-episode-{n}-package.txt")
        try: shutil.move(newest, dest)
        except OSError: shutil.copy2(newest, dest)
        print(f"Moved the YouTube package into the episode folder")
    header = ["Episode", "Idea", "Verdict", "File", "Made", "Posted", "YouTube link", "Views after a week"]
    rows = []
    if os.path.exists(LOG):
        with open(LOG, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))[1:]
    mine = [str(EPISODE["number"]), EPISODE.get("re", ""), " ".join(EPISODE["verdict"]).replace(", ", " ").title(),
            output_stem() + ".mp4", datetime.date.today().isoformat()]
    for r in rows:                          # re-rendering an episode updates its row, keeping what you typed
        if r and r[0] == mine[0]:
            r[:5] = mine; break
    else:
        rows.append(mine + ["", "", ""])
    rows.sort(key=lambda r: int(r[0]) if r and r[0].isdigit() else 0)
    try:
        with open(LOG, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows([header] + rows)
    except PermissionError:
        print(f"Couldn't update {LOG}: close it in Excel and run again to log this episode.")


def main():
    check_episode()
    set_timeline()
    if not has_take():
        print("No \"take\" in this episode: making the 26-second version. Add your own line of advice as \"take\" for the full one.")
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
        folder = episode_folder()
        os.makedirs(folder, exist_ok=True)
        base = os.path.join(folder, output_stem())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{work}/f%04d.png", "-i", wav,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "slow", "-c:a", "aac", "-b:a", "160k",
                        "-shortest", "-movflags", "+faststart", base + ".mp4"], check=True)
        render(COVER_T).save(base + "-cover.png")
        render(17.6).save(base + "-verdict.png")               # the stamped verdict and scorecard, settled
    finally:
        shutil.rmtree(work, ignore_errors=True)
    file_episode(folder)
    print(f"{base}.mp4 ({nframes} frames, {DUR:.1f}s)")
    print(f"Everything for this episode is in {folder}")
    print(f"Thumbnail: in YouTube, pick the frame at {COVER_T:.1f} seconds (see {os.path.basename(base)}-cover.png)")


def latest_episode_file():
    """The newest episode-*.json in Downloads (Chrome may have named it "episode-010 (1).json")."""
    import glob
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    files = glob.glob(os.path.join(downloads, "episode-*.json"))
    if not files:
        sys.exit(f"No episode files in {downloads}. Click 'Download episode file' in the Short Studio first.")
    newest = max(files, key=os.path.getmtime)
    print(f"Using {newest}")
    return newest


SOURCE_FILE = None          # the episode file this run used (moved into the episode's folder afterwards)


def load_episode(path):
    """Use an episode file (from the Short Studio page) instead of the EPISODE block."""
    import json
    if not os.path.exists(path):
        sys.exit(f"Can't find {path}. Try:  python video\\make_short.py latest   (uses the newest episode file in Downloads)")
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as err:
        sys.exit(f"Can't read the episode file {path}: {err}")
    data["notes"] = [tuple(n) for n in data.get("notes", [])]
    EPISODE.clear(); EPISODE.update(data)
    global SOURCE_FILE
    SOURCE_FILE = path


if __name__ == "__main__":
    if "--frames" in sys.argv:
        build_frames()
    elif len(sys.argv) > 1 and sys.argv[1].lower() == "cheaptest":
        import cheaptest                       # video/cheaptest.py: a 9-second cheap-test cutdown of an episode
        cheaptest.cheaptest(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1].lower() == "list":
        import listshort                       # video/listshort.py: three ideas in one 32-second Short
        listshort.listshort(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1].lower() == "playbook":
        import make_playbook                   # video/make_playbook.py: The Cheap Test Playbook, from your episodes
        make_playbook.playbook(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1].lower() == "stitch":
        import stitch                          # video/stitch.py: several Shorts in one widescreen video
        stitch.stitch(sys.argv[2:])
    else:
        args = sys.argv[1:]
        if "latest" in args:
            load_episode(latest_episode_file())
        else:
            files = [a for a in args if a.lower().endswith(".json")]
            if files:
                load_episode(files[0])
        main()
