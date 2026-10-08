#!/usr/bin/env python3
r"""Frank's list: three ideas in one 32-second Short, built from episodes you've already made.

    python video\make_short.py list              the 3 newest episodes
    python video\make_short.py list free         3 whose cheap test costs $0
    python video\make_short.py list cheap        3 whose test costs under $100
    python video\make_short.py list yes          3 Frank said yes or "this could work" to
    python video\make_short.py list easy         3 that are easy to start
    python video\make_short.py list 11 21 23     these three episodes

The title is the strongest claim the three episodes actually back up ("3 Side Hustles You Can Test for
$0", "3 Side Hustles Frank Would Actually Try"), never earnings. The full episodes are the follow-ups:
the package links each one when the log has its YouTube link.

The beats (16 bars at 120 BPM, so it loops cleanly):
    0 - 4     the title, one line per beat; Frank looks at you, then the surprised "o"
    4 - 12    idea 1: number, idea, verdict stamp (on the beat), test cost and ease, the cheap test
    12 - 20   idea 2
    20 - 28   idea 3
    28 - 32   "Which one would you try? Tell Frank in the comments."
Writes SideFrog\lists\<date>-<title>\ with the video, a cover (pick 2.5 s in YouTube) and a package.
"""
import csv, datetime, glob, json, os, re, shutil, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_short as ms
import claims

DUR, ITEM, HOOK = 32.0, 8.0, 4.0
ITEM_FRANK_Y = 1330                    # Frank on the idea screens: 60% size, still above YouTube's bottom fifth
ITEM_BOTTOM = ITEM_FRANK_Y - int(ms.FRANK_SIZE * 0.6) // 2 - 40
ASK_T = HOOK + 3 * ITEM
LISTS = os.path.join(os.path.dirname(ms.ROOT), "lists")
LABELS = {("SURPRISINGLY,", "YES"): ("Surprisingly, yes", 0), ("THIS COULD", "WORK"): ("This could work", 1),
          ("CROWDED", "POND"): ("Crowded pond", 2), ("KEEP YOUR", "DAY JOB"): ("Keep your day job", 2),
          ("CAN'T HELP", "WITH THAT ONE"): ("Can't help", 3)}
CRITERIA = {"free": lambda e: claims.cost_value(e["test_cost"]) == 0,
            "cheap": lambda e: (claims.cost_value(e["test_cost"]) or 10 ** 9) < 100 or claims.cost_value(e["test_cost"]) == 0,
            "yes": lambda e: e["verdict"] in claims.GOOD,
            "easy": lambda e: e["ease"] == "easy"}


# ---------------------------------------------------------------- the three ideas
def posted_links():
    links = {}
    if os.path.exists(ms.LOG):
        with open(ms.LOG, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r.get("Episode", "").isdigit() and r.get("YouTube link", "").strip():
                    links[int(r["Episode"])] = r["YouTube link"].strip()
    return links


def all_episodes():
    eps = {}
    for path in glob.glob(os.path.join(ms.EPISODES, "[0-9][0-9][0-9]-*", "episode-*.json")):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        pb = d.get("playbook") or {}
        label, face = LABELS.get(tuple(d.get("verdict", [])), ("", 12))
        if not label or not d.get("cheap_test"):
            continue
        eps[int(d.get("number", 0))] = dict(number=int(d.get("number", 0)), idea=d.get("re", ""), verdict=label, face=face,
                                            test=d["cheap_test"], test_cost=d.get("test_cost") or pb.get("testCost", ""),
                                            ease=d.get("ease") or pb.get("easyToStart", ""))
    return eps


def pick(args):
    eps = all_episodes()
    if not eps:
        sys.exit(f"No episodes in {ms.EPISODES} yet.")
    nums = [int(a) for a in args if a.isdigit()]
    if nums:
        missing = [n for n in nums if n not in eps]
        if missing:
            sys.exit(f"No episode file for: {', '.join(map(str, missing))}")
        chosen = [eps[n] for n in nums]
    else:
        crit = next((a.lower() for a in args if a.lower() in CRITERIA), None)
        pool = [e for e in eps.values() if not crit or CRITERIA[crit](e)]
        links = posted_links()                       # posted episodes first, newest first
        pool.sort(key=lambda e: (e["number"] in links, e["number"]), reverse=True)
        chosen = pool[:3]
        if len(chosen) < 3:
            sys.exit(f"Only {len(chosen)} episode(s) fit \"{crit}\". Make a few more, or name three episode numbers.")
    if len(chosen) != 3:
        sys.exit("A list Short has exactly three ideas.")
    return chosen


# ---------------------------------------------------------------- drawing
def masthead(img, d):
    img.alpha_composite(ms.frank(12, 96), (128, 98))
    d.text((236, 106), "sidefrog.com", font=ms.font(50), fill=ms.TEXT)
    d.text((238, 162), "For people who hate Mondays.", font=ms.font(26, 600, 14), fill=ms.SUBTLE)
    d.rectangle((ms.LEFT, 214, ms.W - ms.LEFT, 217), fill=ms.SUBTLE)


def pill(d, x, y, label, size=40, s=1.0):
    f = ms.font(int(size * s), 800, 14); t = label.upper()
    w = d.textlength(t, font=f) + size * 1.2 * s; h = size * 1.75 * s
    good, nah = label in claims.GOOD, label == "Keep your day job"
    color = ms.ACCENT_ON_DARK if nah else ms.TEXT
    d.rounded_rectangle((x, y, x + w, y + h), int(h / 2), fill=ms.FROG if good else None, outline=ms.FROG if good else color, width=4)
    d.text((x + size * 0.6 * s, y + size * 0.33 * s), t, font=f, fill=ms.BG if good else color)


def scene_title(img, d, t, title):
    ms.kicker(d, "Frank's list")
    words, lines, cur = title.split(), [], ""
    f = ms.font(120)
    for w in words:                                  # wrap, then size to fit
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) > ms.TEXT_W and cur: lines.append(cur); cur = w
        else: cur = test
    lines.append(cur)
    size = ms.fit_lines(d, lines, 120, 64, ms.TEXT_W, ms.TEXT_BOTTOM - ms.TEXT_TOP)
    for k, line in enumerate(lines):
        when = ms.BEAT * (k + 1)
        if t >= when - 0.25:
            p = ms.land(t, when)
            d.text((ms.LEFT, ms.TEXT_TOP + k * size * 1.03 + (1 - p) * 46), line, font=ms.font(size), fill=ms.TEXT)
    face = 12 if t < 2.0 else 0
    ms.round_frank(img, face, scale=1 + 0.05 * (1 - ms.ease((t - 2.0) / 0.3)) if t >= 2.0 else 1.0)


def scene_item(img, d, t, e, k):
    ms.kicker(d, f"Frank's list · {k + 1} of 3")
    p0 = ms.land(t, 0.15, 0.15)
    d.text((ms.LEFT - (1 - p0) * 70, ms.TEXT_TOP - 10), f"{k + 1:02d}", font=ms.font(150), fill=ms.FROG)
    y = ms.TEXT_TOP + 165
    hs, head = ms.fit_wrapped(d, e["idea"], 86, 54, ms.TEXT_W, 190, line_gap=1.05)
    if t >= ms.BEAT - 0.25:                          # the idea, on the next beat
        p1 = ms.land(t, ms.BEAT)
        for j, l in enumerate(head):
            d.text((ms.LEFT - (1 - p1) * 50, y + j * hs * 1.05), l, font=ms.font(hs), fill=ms.TEXT)
    y += int(len(head) * hs * 1.05) + 22
    st = (t - 1.28) / 0.22                           # the verdict stamps on the beat (1.5 s in)
    if st > 0:
        pill(d, ms.LEFT, y, e["verdict"], 40, 1 + 0.18 * (1 - ms.ease(st)))
    y += 92
    bits = [b for b in (f"Test costs {e['test_cost']}" if e["test_cost"] else "",
                        {"easy": "Easy to start", "some_setup": "Some setup", "hard": "Hard to start"}.get(e["ease"], "")) if b]
    if bits and t >= 2.25:
        p2 = ms.land(t, 2.5)
        d.text((ms.LEFT, y + (1 - p2) * 24), " · ".join(bits), font=ms.font(40, 700, 24), fill=ms.LABEL)
    y += 64
    if t >= 2.75:
        p3 = ms.land(t, 3.0)
        ts, tl = ms.fit_wrapped(d, e["test"], 54, 38, ms.TEXT_W, ITEM_BOTTOM - y, line_gap=1.28, weight=500, opsz=20)
        for j, l in enumerate(tl):
            d.text((ms.LEFT, y + j * ts * 1.28 + (1 - p3) * 24), l, font=ms.font(ts, 500, 20), fill=ms.TEXT)
    face = 12 if t < 1.5 else e["face"]               # smaller and lower here, so the cheap test has room
    bump = 1 + 0.04 * (1 - ms.ease((t - 1.5) / 0.3)) if t >= 1.5 else 1.0
    ms.paste_center(img, ms.frank(face, ms.FRANK_SIZE, round_=True), ms.W // 2, ITEM_FRANK_Y, scale=0.6 * bump)


def scene_ask(img, d, t):
    ms.kicker(d, "Your turn")
    big = ms.fit_lines(d, ["Which one would you try?"], 96, 60, ms.TEXT_W, 120)
    for k, (y, text, f) in enumerate(((ms.TEXT_TOP, "Which one would you try?", ms.font(big)),
                                      (440, "Tell Frank in the comments.", ms.font(62, 500, 20)),
                                      (520, "Full reviews on the channel.", ms.font(62, 500, 20)))):
        when = 0.15 + k * ms.BEAT
        if t >= when - 0.15:
            p = ms.land(t, when, 0.15 if k == 0 else 0.25)
            d.text((ms.LEFT, y + (1 - p) * 34), text, font=f, fill=ms.TEXT)
    ms.round_frank(img, 12 if t < 2.0 else ms.sip_frame(t - 2.0))


def render(t, eps, title):
    img = Image.new("RGBA", (ms.W, ms.H), ms.BG); d = ImageDraw.Draw(img)
    masthead(img, d)
    if t < HOOK: scene_title(img, d, t, title)
    elif t < ASK_T:
        k = int((t - HOOK) // ITEM); scene_item(img, d, t - HOOK - k * ITEM, eps[k], k)
    else: scene_ask(img, d, t - ASK_T)
    return img.convert("RGB")


def sound(title_lines):
    n = int(DUR * ms.SR); fx = np.zeros(n); rng = np.random.default_rng(5)
    def add(t0, sig, gain):
        i = int(t0 * ms.SR); j = min(n, i + len(sig)); fx[i:j] += sig[: j - i] * gain
    def tone(freq, sec, decay=8.0):
        tt = np.arange(int(sec * ms.SR)) / ms.SR
        return np.sin(2 * np.pi * freq * tt) * np.minimum(1, tt / 0.003) * np.exp(-decay * tt)
    def whoosh(sec=0.18):
        x = np.convolve(rng.standard_normal(int(sec * ms.SR)), np.ones(20) / 20, mode="same")
        return x * np.sin(np.linspace(0, np.pi, len(x))) ** 2
    for k in range(title_lines):
        add(ms.BEAT * (k + 1) - 0.02, tone(523.25 * (1.12246 ** (2 * k)), 0.12, 30), 0.10)
    add(2.0, tone(880, 0.18, 18) + tone(1320, 0.18, 22) * 0.5, 0.09)
    for k in range(3):
        t0 = HOOK + k * ITEM
        add(t0 - 0.08, whoosh(), 0.08)
        thud = tone(70, 0.4, 9); add(t0 + 1.5, thud, 0.5)                      # the verdict stamp
        add(t0 + 2.5, tone(1046.5, 0.08, 40), 0.05)
    add(ASK_T, tone(987.77, 0.25, 10) + tone(1479.98, 0.25, 12) * 0.4, 0.08)
    levels = [0, 0] + [1, 1, 2, 2] * 3 + [0, 0]
    mix = ms.music(DUR, levels) * 0.55 + fx
    mix = mix / max(1e-9, np.abs(mix).max()) * 0.85
    return (mix * 32767).astype(np.int16)


# ---------------------------------------------------------------- the package
def package(eps, titles, stem):
    links = posted_links()
    lines = [f"{k + 1}. {e['idea']}: {e['verdict']}." + (f" Test costs {e['test_cost']}." if e["test_cost"] else "")
             + (f" Full review: {links[e['number']]}" if e["number"] in links else "") for k, e in enumerate(eps)]
    tagged = lambda src: f"https://sidefrog.com/?utm_source={src}&utm_medium=social&utm_campaign=list-{datetime.date.today().isoformat()}"
    desc = [f"Frank's list: {titles[0]}.", "\n".join(lines),
            "Which one would you try? Tell Frank in the comments.",
            f"Check your own idea free, no sign-up: {tagged('youtube')}",
            "Everybody tells you what a side hustle could make. SideFrog tells you whether it's worth doing.",
            "#SideFrog #SideHustle #SideHustleIdeas #BusinessIdeas"]
    tags = ["side hustle", "side hustle ideas", "cheap side hustles", "business ideas", "SideFrog"] + [e["idea"].lower() for e in eps]
    return "\n\n".join([f"TITLE\n{titles[0]}", "OTHER TITLE OPTIONS\n" + "\n".join(titles[1:]) + "\n" + claims.boring_note(),
                        "DESCRIPTION\n" + "\n\n".join(desc), "TAGS\n" + ", ".join(dict.fromkeys(tags)),
                        f"PINNED COMMENT\nWhich of these three would you actually try? If you've done one of them, tell Frank how it went.",
                        f"TIKTOK CAPTION\n{titles[0]}. Which one would you try? #sidehustle #sidehustleideas #sidefrog",
                        "INSTAGRAM REELS CAPTION\n" + "\n\n".join([titles[0] + ".", "\n".join(l.split(" Full review")[0] for l in lines),
                                                                   "Which one would you try? Check your own idea free: link in bio.", "#sidehustle #sidehustleideas #sidefrog"]),
                        f"THUMBNAIL\nIn YouTube, pick the frame at 2.5 seconds (see {stem}-cover.png).", f"FILENAME\n{stem}.mp4"]) + "\n"


def listshort(args):
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg isn't installed (on Windows: winget install ffmpeg, then open a new PowerShell).")
    eps = pick(args)
    titles = claims.checked_titles(eps)
    title = titles[0]
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50]
    stem = f"sidefrog-list-{slug}"
    out_dir = os.path.join(LISTS, f"{datetime.date.today().isoformat()}-{slug}")
    os.makedirs(out_dir, exist_ok=True)
    work = tempfile.mkdtemp()
    try:
        d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        title_lines = 0
        f = ms.font(120); cur = ""
        for w in title.split():
            test = (cur + " " + w).strip()
            if d.textlength(test, font=f) > ms.TEXT_W and cur: title_lines += 1; cur = w
            else: cur = test
        title_lines += 1
        for k in range(int(DUR * ms.FPS)):
            render(k / ms.FPS, eps, title).save(f"{work}/f{k:04d}.png")
        wav = f"{work}/a.wav"
        with wave.open(wav, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(ms.SR); wf.writeframes(sound(title_lines).tobytes())
        base = os.path.join(out_dir, stem)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(ms.FPS), "-i", f"{work}/f%04d.png", "-i", wav,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "slow", "-c:a", "aac", "-b:a", "160k",
                        "-shortest", "-movflags", "+faststart", base + ".mp4"], check=True)
        render(2.5, eps, title).save(base + "-cover.png")
        with open(base + "-package.txt", "w", encoding="utf-8") as fh:
            fh.write(package(eps, titles, stem))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"{base}.mp4 ({DUR:.0f}s): {title}")
    print(f"Cover and package are in {out_dir}")


if __name__ == "__main__":
    listshort(sys.argv[1:])
