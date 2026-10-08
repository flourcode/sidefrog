#!/usr/bin/env python3
r"""The cheap-test cutdown: a 10-second Short of just an episode's cheap test, built to loop.

    python video\make_short.py cheaptest          the newest episode folder
    python video\make_short.py cheaptest 11       episode 11

It reads the episode file in the episode's folder (SideFrog\episodes\011-mobile-car-wash\), so
there's nothing to write, and saves into that folder:
    <name>-cheap-test.mp4            the cutdown (with sound effects)
    <name>-cheap-test-cover.png      the frame to pick as its thumbnail (at 3.5 seconds)
    <name>-cheap-test-package.txt    title, description and captions for YouTube and the others
Post it a few days after the main episode, as a follow-up.

The 10 seconds (5 bars at 120 BPM, with the full Shorts' music): the topic and Frank's verdict tag
are on screen throughout; the cheap test lands line by line on the beat, holds for reading (to 9 s;
Frank sips), then fades out so the
last frame matches the first and it loops cleanly. Same "after hours" look as the full Shorts.
"""
import csv, glob, json, os, re, shutil, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_short as ms

# 10 s = 5 bars at 120 BPM, like the full Shorts: lines land on beats, the music loops cleanly
DUR, POP_START, POP_GAP, FADE_AT, COVER_T = 10.0, 0.5, 0.5, 9.0, 3.5
SIP_AT = 5.0
FRANK_SCALE, FRANK_Y = 0.85, 1120                  # a little smaller and lower than in the full Shorts,
TEXT_BOTTOM = FRANK_Y - int(ms.FRANK_SIZE * FRANK_SCALE / 2) - 30   # so the test gets more room (still above YouTube's band)
LABELS = {("SURPRISINGLY,", "YES"): "Surprisingly, yes", ("THIS COULD", "WORK"): "This could work",
          ("CROWDED", "POND"): "Crowded pond", ("KEEP YOUR", "DAY JOB"): "Keep your day job",
          ("CAN'T HELP", "WITH THAT ONE"): "Can't help"}
GOOD = {"Surprisingly, yes", "This could work"}


# ---------------------------------------------------------------- which episode
def find_episode(args):
    folders = [d for d in glob.glob(os.path.join(ms.EPISODES, "[0-9][0-9][0-9]-*")) if glob.glob(os.path.join(d, "episode-*.json"))]
    if not folders:
        sys.exit(f"No episode folders with an episode file in {ms.EPISODES}. Make the episode first.")
    nums = [int(a) for a in args if a.isdigit()]
    if nums:
        mine = [d for d in folders if os.path.basename(d).startswith(f"{nums[0]:03d}-")]
        if not mine:
            sys.exit(f"No episode folder for episode {nums[0]} in {ms.EPISODES}.")
        folder = max(mine, key=os.path.getmtime)
    else:
        folder = max(folders, key=os.path.getmtime)
    data = json.load(open(sorted(glob.glob(os.path.join(folder, "episode-*.json")))[-1], encoding="utf-8"))
    data["notes"] = [tuple(n) for n in data.get("notes", [])]
    ms.EPISODE.clear(); ms.EPISODE.update(data)
    if not str(ms.EPISODE.get("cheap_test", "")).strip():
        sys.exit("This episode has no cheap test to show.")
    return folder


# ---------------------------------------------------------------- the frame
def verdict_label():
    return LABELS.get(tuple(ms.EPISODE.get("verdict", [])), "")


def pill(d, x, y, label):
    f = ms.font(30, 800, 14); t = label.upper()
    w = d.textlength(t, font=f) + 44
    good = label in GOOD
    d.rounded_rectangle((x, y, x + w, y + 54), 27, fill=ms.FROG if good else None, outline=ms.FROG if good else ms.TEXT, width=3)
    d.text((x + 22, y + 11), t, font=f, fill=ms.BG if good else ms.TEXT)


def topic_line():
    hook = " ".join(ms.EPISODE.get("hook") or [ms.EPISODE.get("re", "")]).strip()
    return hook if hook.endswith("?") else hook + "?"


def layout(d):
    topic = topic_line()
    ts = ms.fit_lines(d, [topic], 96, 52, ms.TEXT_W, 120)
    top = ms.TEXT_TOP
    test_top = top + int(ts * 1.1) + (54 + 34 if verdict_label() else 20)
    size, lines = ms.fit_wrapped(d, ms.EPISODE["cheap_test"], 84, 46, ms.TEXT_W, TEXT_BOTTOM - test_top - 44, line_gap=1.19)
    return topic, ts, top, test_top, size, lines


def render(t):
    img = Image.new("RGBA", (ms.W, ms.H), ms.BG); d = ImageDraw.Draw(img)
    img.alpha_composite(ms.frank(12, 96), (128, 98))                       # the masthead, as in the full Shorts
    d.text((236, 106), "sidefrog.com", font=ms.font(50), fill=ms.TEXT)
    d.text((238, 162), "For people who hate Mondays.", font=ms.font(26, 600, 14), fill=ms.SUBTLE)
    d.rectangle((ms.LEFT, 214, ms.W - ms.LEFT, 217), fill=ms.SUBTLE)
    ms.kicker(d, f"The cheap test · No. {ms.EPISODE['number']:03d}")
    topic, ts, top, test_top, size, lines = layout(d)
    d.text((ms.LEFT, top), topic, font=ms.font(ts), fill=ms.TEXT)
    if verdict_label():
        pill(d, ms.LEFT, top + int(ts * 1.1) + 6, verdict_label())
    cost = str(ms.EPISODE.get("test_cost", "")).strip()
    d.text((ms.LEFT, test_top - 4), f"CHEAP TEST · {cost.upper()}:" if cost else "CHEAP TEST:", font=ms.font(30, 800, 14), fill=ms.LABEL)
    # the test pops in line by line, holds, then fades so the last frame matches the first
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    fade = 1.0 if t < FADE_AT else max(0.0, 1 - (t - FADE_AT) / (DUR - FADE_AT - 0.1))
    for k, line in enumerate(lines):
        p = ms.land(t, POP_START + k * POP_GAP)
        if t >= POP_START + k * POP_GAP - 0.25:
            ld.text((ms.LEFT, test_top + 44 + k * size * 1.19 + (1 - p) * 30), line, font=ms.font(size), fill=ms.TEXT)
    if fade < 1.0:
        layer.putalpha(layer.split()[-1].point(lambda v: int(v * fade)))
    img.alpha_composite(layer)
    face = ms.sip_frame(t - SIP_AT) if t >= SIP_AT else 12                # Frank looks at you, sips mid-way
    ms.paste_center(img, ms.frank(face, ms.FRANK_SIZE, round_=True), ms.W // 2, FRANK_Y, scale=FRANK_SCALE)
    return img.convert("RGB")


# ---------------------------------------------------------------- sound effects (no music)
def sfx(nlines):
    sr = ms.SR; n = int(DUR * sr); out = np.zeros(n); rng = np.random.default_rng(11)
    def add(t0, sig, gain):
        i = int(t0 * sr); j = min(n, i + len(sig)); out[i:j] += sig[: j - i] * gain
    def noise(sec, smooth):
        return np.convolve(rng.standard_normal(int(sec * sr)), np.ones(smooth) / smooth, mode="same")
    def tone(freq, sec, decay):
        tt = np.arange(int(sec * sr)) / sr
        return np.sin(2 * np.pi * freq * tt) * np.minimum(1, tt / 0.003) * np.exp(-decay * tt)
    swell = lambda s, p=1.0: s * np.sin(np.linspace(0, np.pi, len(s))) ** p
    add(0.15, swell(noise(0.3, 30)), 0.07)                                  # a soft whoosh
    for k in range(nlines):                                                 # a pop for each line
        add(POP_START + k * POP_GAP, tone(560 + k * 70, 0.12, 30), 0.11)
    for t0 in (SIP_AT + 0.88, SIP_AT + 1.2):                                # the sip
        add(t0, swell(noise(0.25, 6) - noise(0.25, 40), 1.5), 0.11)
    out = ms.music(DUR, [0, 1, 1, 1, 0]) * 0.55 + out        # the same music as the full Shorts, 5 bars
    out = out / max(1e-9, np.abs(out).max()) * 0.8
    return (out * 32767).astype(np.int16)


# ---------------------------------------------------------------- the package
def article(topic):
    last = re.sub(r"[^a-z]", "", topic.split()[-1].lower()) if topic.split() else ""
    if (last.endswith("s") and not last.endswith(("ss", "us", "is"))) or last.endswith("ing") or len(topic.split()) == 1:
        return topic
    return ("an " if topic[:1].lower() in "aeiou" else "a ") + topic


def youtube_link():
    if not os.path.exists(ms.LOG):
        return ""
    with open(ms.LOG, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("Episode") == str(ms.EPISODE["number"]) and r.get("YouTube link", "").strip():
                return r["YouTube link"].strip()
    return ""


def cost_words():
    """ "$40" from "about $40" (the test's cost, never earnings), "Free" for $0, else ""."""
    m = re.search(r"\$\s?([\d,]+)", str(ms.EPISODE.get("test_cost", "")))
    return "" if not m else ("Free" if m.group(1) == "0" else f"${m.group(1)}")


def package(stem):
    topic = ms.EPISODE.get("re", "this side hustle").strip()
    test, label, link = ms.EPISODE["cheap_test"].strip(), verdict_label(), youtube_link()
    full = f"Frank's full review: {link}" if link else "Frank's full review is on the channel."
    tags = f"#SideFrog #SideHustle #{re.sub(r'[^A-Za-z0-9]', '', topic.title())} #BusinessIdeas"
    tagged = lambda src: f"https://sidefrog.com/?utm_source={src}&utm_medium=social&utm_campaign=cheap-test-{ms.EPISODE['number']:03d}"
    return "\n\n".join([
        f"TITLE\nThinking About {article(topic)}? Try This Cheap Test First",
        f"OTHER TITLE\nThe Cheap Way to Test {article(topic)} Before You Spend Real Money"
        + (f"\nThe {cost_words()} Test Before You Start {article(topic)}" if cost_words() else ""),
        "DESCRIPTION\n" + "\n\n".join([
            f"Thinking about {article(topic).lower()}? Try this before you spend real money: {test}",
            (f"Frank's verdict on the idea: {label}. " if label else "") + full,
            f"Check your own idea free, no sign-up: {tagged('youtube')}", tags]),
        f"TIKTOK CAPTION\nThinking about {article(topic).lower()}? Do this first. {tags.lower()}",
        "INSTAGRAM REELS CAPTION\n" + "\n\n".join([f"Thinking about {article(topic).lower()}? Try this cheap test first:", test,
                                                    "Check your own idea free: link in bio.", tags.lower()]),
        f"THREADS POST\nBefore you spend money on {article(topic).lower()}: {test[0].lower() + test[1:]} Would you try it? {tagged('threads')}",
        f"THUMBNAIL\nIn YouTube, pick the frame at {COVER_T:.0f} seconds (see {stem}-cheap-test-cover.png).",
        f"FILENAME\n{stem}-cheap-test.mp4",
    ]) + "\n"


# ---------------------------------------------------------------- make it
def cheaptest(args):
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg isn't installed (on Windows: winget install ffmpeg, then open a new PowerShell).")
    folder = find_episode(args)
    words = len(ms.EPISODE["cheap_test"].split())
    if words > 32:
        print(f"Heads-up: this cheap test is {words} words, a lot to read in 6 seconds. It still fits on screen.")
    stem = ms.output_stem()
    work = tempfile.mkdtemp()
    try:
        d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        nlines = len(layout(d)[5])
        frames = int(DUR * ms.FPS)
        for k in range(frames):
            render(k / ms.FPS).save(f"{work}/f{k:04d}.png")
        wav = f"{work}/sfx.wav"
        with wave.open(wav, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(ms.SR); wf.writeframes(sfx(nlines).tobytes())
        out = os.path.join(folder, stem + "-cheap-test.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(ms.FPS), "-i", f"{work}/f%04d.png", "-i", wav,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "slow", "-c:a", "aac", "-b:a", "160k",
                        "-shortest", "-movflags", "+faststart", out], check=True)
        render(COVER_T).save(os.path.join(folder, stem + "-cheap-test-cover.png"))
        with open(os.path.join(folder, stem + "-cheap-test-package.txt"), "w", encoding="utf-8") as f:
            f.write(package(stem))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"{out} ({frames} frames, {DUR:.0f}s)")
    print(f"Cover and package are in {folder}. Post it a few days after the main episode.")


if __name__ == "__main__":
    cheaptest(sys.argv[1:])
