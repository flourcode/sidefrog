#!/usr/bin/env python3
r"""Stitch several Shorts into one widescreen video for YouTube ("Frank reviews 5 side hustles").

    python video\make_short.py stitch              the latest 5 posted episodes (rows in
                                                   episode-log.csv that have a YouTube link)
    python video\make_short.py stitch 3 8 9 10     these episode numbers, in this order
    python video\make_short.py stitch countdown            a countdown: the same episodes, ordered worst
    python video\make_short.py stitch countdown 3 8 9 10   verdict to best, numbered #5 down to #1

The countdown: the intro says "#1 is the one Frank would actually try" (or, when none of them got a
good verdict, "#1 is the least bad of the lot", so the promise is always true). The lineup hides the
ideas still to come, so nobody can skip ahead, and each verdict appears when it's stamped.

Why widescreen: YouTube treats vertical videos up to 3 minutes as Shorts, so a vertical compilation
would just be another Short. A 16:9 video is a regular video. Each Short plays in the middle, with
side panels: the lineup of ideas and verdicts on the left (the current one highlighted), sidefrog.com
on the right (no second Frank, and no rules around the Short: on the dark background it blends in). A 3-second intro card opens it. Each Short is trimmed just
before its ending question, except the last, so it moves along.

Optional: your voice on the intro. Record 10 to 20 seconds on your phone ("I had Frank look at five
side hustles people keep recommending..."), save it as SideFrog\voice-intro.m4a (or .mp3 or .wav), and
the next stitch plays it over the intro card, which stays up as long as you talk. Afterwards the file
moves into that compilation's folder, so it's never reused by accident. No file: the usual silent
3-second intro, and nothing stops. You can also name a file:  ... stitch countdown my-intro.m4a

It uses the posted video in each episode's folder (SideFrog\episodes\NNN-idea\), and writes, in
SideFrog\compilations\<date>-frank-reviews-N\:
    the video, its YouTube package (title, description with chapters, tags) and a thumbnail.
Needs Python with Pillow and numpy, ffmpeg, and the frames and font the Short builder uses.
"""
import csv, datetime, glob, json, os, re, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_short as ms

W, H, FPS = 1920, 1080, 30
SH_W, SH_X = 608, (1920 - 608) // 2                 # the Short, scaled to the full height, centered
INTRO = 3.0
COMP = os.path.join(os.path.dirname(ms.ROOT), "compilations")
LABELS = {("SURPRISINGLY,", "YES"): "Surprisingly, yes", ("THIS COULD", "WORK"): "This could work",
          ("CROWDED", "POND"): "Crowded pond", ("KEEP YOUR", "DAY JOB"): "Keep your day job",
          ("CAN'T HELP", "WITH THAT ONE"): "Can't help"}
GOOD = {"Surprisingly, yes", "This could work"}
RANK = {"Can't help": 0, "Keep your day job": 1, "Crowded pond": 2, "This could work": 3, "Surprisingly, yes": 4}
EASE_RANK = {"hard": 0, "some_setup": 1, "easy": 2}


def countdown_order(eps):
    """Worst verdict first, best last; between equal verdicts, the easier one to start comes later."""
    return sorted(eps, key=lambda e: (RANK.get(e["verdict"], 1), EASE_RANK.get(e.get("ease"), 1)))


def countdown_tease(eps):
    return ("#1 is the one Frank would actually try." if eps[-1]["verdict"] in GOOD
            else "#1 is the least bad of the lot.")


# ---------------------------------------------------------------- which episodes
def episode_dirs():
    """{number: newest folder for that number that has a video}"""
    found = {}
    for d in glob.glob(os.path.join(ms.EPISODES, "[0-9][0-9][0-9]-*")):
        m = re.match(r"(\d+)-", os.path.basename(d))
        vids = [v for v in glob.glob(os.path.join(d, "*.mp4"))]
        if not m or not vids:
            continue
        n = int(m.group(1))
        if n not in found or os.path.getmtime(d) > os.path.getmtime(found[n]):
            found[n] = d
    return found


def posted_numbers():
    """Episode numbers with a YouTube link in the log, oldest first."""
    if not os.path.exists(ms.LOG):
        return []
    with open(ms.LOG, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    nums = [int(r["Episode"]) for r in rows if r.get("Episode", "").isdigit() and r.get("YouTube link", "").strip()]
    return sorted(set(nums))


def pick(args):
    dirs = episode_dirs()
    if not dirs:
        sys.exit(f"No episode folders with videos in {ms.EPISODES}.")
    asked = [int(a) for a in args if a.isdigit()]
    if asked:
        missing = [n for n in asked if n not in dirs]
        if missing:
            sys.exit(f"No episode folder with a video for: {', '.join(map(str, missing))} (looked in {ms.EPISODES}).")
        nums = asked
    else:
        posted = [n for n in posted_numbers() if n in dirs]
        nums = (posted or sorted(dirs))[-5:]
        if not posted:
            print("No YouTube links in episode-log.csv yet: using the 5 newest episode folders.")
    if len(nums) < 2:
        sys.exit("A stitch needs at least 2 episodes.")
    eps = []
    for n in nums:
        d = dirs[n]
        js = sorted(glob.glob(os.path.join(d, "episode-*.json")))
        data = json.load(open(js[0], encoding="utf-8")) if js else {}
        vids = sorted(glob.glob(os.path.join(d, "*.mp4")), key=os.path.getmtime)
        eps.append(dict(number=n, folder=d, video=vids[-1],
                        idea=data.get("re") or os.path.basename(d).split("-", 1)[1].replace("-", " ").title(),
                        verdict=LABELS.get(tuple(data.get("verdict", [])), ""), ease=data.get("ease", ""),
                        test_cost=data.get("test_cost", "") or (data.get("playbook") or {}).get("testCost", "")))
    return eps


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def stamp_time(path):
    """When the verdict lands in the Short (the lineup shows its tag from then on)."""
    d = duration(path)
    return 15.0 if d > 25.8 else 14.97 if d > 25.3 else 14.37      # 26 s (on the beat), 25.6 s, 25 s formats


def cut_point(path, last):
    """Each Short is trimmed just before its ending question (22.0 s in the current
    format, 21.4 s in the earlier 25-second one), except the last. In the beat-synced 26-second
    format, 22.0 s is a bar line, so the music cuts cleanly too."""
    d = duration(path)
    if last:
        return d
    return 26.0 if d > 29 else 22.0 if d > 25.3 else 21.4     # 30 s (with Frank's take), 26 s, 25 s


# ---------------------------------------------------------------- the panels
def tag(d, x, y, label, size=22):
    f = ms.font(size, 800, 14); t = label.upper()
    w = d.textlength(t, font=f) + size * 1.1
    good = label in GOOD
    d.rounded_rectangle((x, y, x + w, y + size * 1.7), size, fill=ms.FROG if good else None, outline=ms.TEXT if not good else ms.FROG, width=2)
    d.text((x + size * 0.55, y + size * 0.3), t, font=f, fill=ms.BG if good else ms.TEXT)
    return w


def lineup(d, eps, current, x, y, width, reveal=False, countdown=False):
    d.text((x, y), "FRANK COUNTS DOWN" if countdown else "FRANK REVIEWS", font=ms.font(26, 800, 14), fill=ms.LABEL)
    d.text((x, y + 36), f"{len(eps)} side hustles", font=ms.font(52), fill=ms.TEXT)
    y += 130
    for k, e in enumerate(eps):
        on = k == current
        col = ms.TEXT if (on or current is None) else ms.SUBTLE
        if on:
            d.rectangle((x - 22, y - 6, x - 14, y + 74), fill=ms.FROG)
        num = f"#{len(eps) - k}" if countdown else f"{k + 1:02d}"
        d.text((x, y), num, font=ms.font(30, 800, 14), fill=ms.FROG if on or current is None else ms.SUBTLE)
        if countdown and current is not None and k > current:      # no skipping ahead
            d.text((x + 56, y), "Still to come", font=ms.font(30, 500, 24), fill=ms.SUBTLE)
            y += 104
            continue
        size = ms.fit_lines(d, [e["idea"]], 34, 22, width - 56, 60, weight=700, opsz=24)
        d.text((x + 56, y), e["idea"], font=ms.font(size, 700, 24), fill=col)
        if e["verdict"] and (current is None or k < current or (k == current and reveal)):   # no spoilers
            tag(d, x + 56, y + 46, e["verdict"], 16)
        y += 104


def brand_panel(img, d, x0, x1):
    # no Frank here: the Short in the middle already has him
    cx = (x0 + x1) // 2
    for text, f, fill, y in (("sidefrog.com", ms.font(50), ms.TEXT, 450), ("For people who hate Mondays.", ms.font(26, 600, 14), ms.SUBTLE, 516),
                             ("Check your own idea free.", ms.font(28, 700, 24), ms.LABEL, 590)):
        d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


def panel(eps, current, reveal=False, countdown=False):
    img = Image.new("RGBA", (W, H), ms.BG); d = ImageDraw.Draw(img)
    lineup(d, eps, current, 90, 150, SH_X - 130, reveal, countdown)
    brand_panel(img, d, SH_X + SH_W, W)
    return img.convert("RGB")


def intro_card(eps, countdown=False):
    img = Image.new("RGBA", (W, H), ms.BG); d = ImageDraw.Draw(img)
    if countdown:                                       # no list: that would give #1 away
        d.text((140, 190), "FRANK COUNTS DOWN", font=ms.font(30, 800, 14), fill=ms.LABEL)
        d.text((132, 235), f"{len(eps)} side hustles,", font=ms.font(132), fill=ms.TEXT)
        d.text((132, 380), "worst to best.", font=ms.font(132), fill=ms.TEXT)
        tease = countdown_tease(eps)
        ts = ms.fit_lines(d, [tease], 60, 36, 1050, 80, weight=700, opsz=40)
        d.text((136, 580), tease, font=ms.font(ts, 700, 40), fill=ms.LABEL)
        fr = ms.frank(12, 504, round_=True)               # looking at you
        img.alpha_composite(fr, (W - fr.width - 150, 300))
        f = ms.font(40); d.text((W - 150 - fr.width / 2 - d.textlength("sidefrog.com", font=f) / 2, 840), "sidefrog.com", font=f, fill=ms.TEXT)
        return img.convert("RGB")
    d.text((140, 150), "FRANK REVIEWS YOUR SIDE HUSTLE", font=ms.font(30, 800, 14), fill=ms.LABEL)
    d.text((132, 195), f"{len(eps)} side hustles.", font=ms.font(132), fill=ms.TEXT)
    d.text((136, 355), "Which ones can actually make money?", font=ms.font(54, 700, 40), fill=ms.TEXT)
    y = 470
    for k, e in enumerate(eps):
        d.text((140, y), f"{k + 1:02d}", font=ms.font(34, 800, 14), fill=ms.FROG)
        d.text((205, y - 2), e["idea"], font=ms.font(40, 600, 24), fill=ms.TEXT)
        y += 62
    fr = ms.frank(0, 504, round_=True)                  # the surprised "o"
    img.alpha_composite(fr, (W - fr.width - 150, 300))
    f = ms.font(40); d.text((W - 150 - fr.width / 2 - d.textlength("sidefrog.com", font=f) / 2, 840), "sidefrog.com", font=f, fill=ms.TEXT)
    return img.convert("RGB")


# ---------------------------------------------------------------- build
def run(cmd):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + cmd, check=True)


VOICE_EXT = (".m4a", ".mp3", ".wav", ".aac")


def find_voice(args):
    """The optional voice intro: a file named on the command line, else SideFrog\voice-intro.*"""
    named = [a for a in args if a.lower().endswith(VOICE_EXT)]
    if named:
        if not os.path.exists(named[0]):
            print(f"Couldn't find {named[0]}: making the intro without your voice.")
            return None
        return named[0]
    for ext in VOICE_EXT:
        p = os.path.join(os.path.dirname(ms.ROOT), "voice-intro" + ext)
        if os.path.exists(p):
            return p
    return None


def stitch(args):
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg isn't installed (on Windows: winget install ffmpeg, then open a new PowerShell).")
    countdown = any(a.lower() == "countdown" for a in args)
    voice = find_voice(args)
    eps = pick([a for a in args if a.lower() != "countdown" and not a.lower().endswith(VOICE_EXT)])
    if countdown:
        eps = countdown_order(eps)
    stamp = datetime.date.today().isoformat()
    kind = "countdown" if countdown else "reviews"
    out_dir = os.path.join(COMP, f"{stamp}-frank-{kind}-{len(eps)}")
    os.makedirs(out_dir, exist_ok=True)
    work = tempfile.mkdtemp()
    try:
        segs, starts, t = [], [], 0.0
        intro_png = os.path.join(work, "intro.png"); intro_card(eps, countdown).save(intro_png)
        seg = os.path.join(work, "seg00.mp4")
        intro = INTRO
        if voice:                                 # your voice over the intro card, which stays up while you talk
            try:
                intro = max(INTRO, round(duration(voice) + 0.6, 2))
                run(["-loop", "1", "-framerate", str(FPS), "-i", intro_png, "-i", voice,
                     "-filter_complex", "[1:a]aresample=44100,aformat=channel_layouts=stereo,afade=t=in:d=0.05,apad[a]",
                     "-map", "0:v", "-map", "[a]", "-t", f"{intro:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
                     "-c:a", "aac", "-b:a", "160k", seg])
                print(f"Voice intro: {os.path.basename(voice)} ({intro:.1f} s)")
            except (subprocess.CalledProcessError, ValueError):
                print(f"Couldn't use {voice} (is it an audio file?): making the intro without your voice.")
                voice, intro = None, INTRO
        if not voice:
            run(["-loop", "1", "-framerate", str(FPS), "-i", intro_png, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                 "-t", str(INTRO), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-shortest", seg])
        segs.append(seg); t += intro
        for k, e in enumerate(eps):
            last = k == len(eps) - 1
            cut = cut_point(e["video"], last)
            p = os.path.join(work, f"panel{k}.png"); panel(eps, k, countdown=countdown).save(p)
            p2 = os.path.join(work, f"panel{k}b.png"); panel(eps, k, reveal=True, countdown=countdown).save(p2)
            at = stamp_time(e["video"])
            seg = os.path.join(work, f"seg{k + 1:02d}.mp4")
            run(["-loop", "1", "-framerate", str(FPS), "-i", p, "-i", e["video"], "-loop", "1", "-framerate", str(FPS), "-i", p2,
                 "-filter_complex", f"[0:v][2:v]overlay=0:0:enable='gte(t,{at})'[bg];"
                                    f"[1:v]scale={SH_W}:{H},fps={FPS}[s];[bg][s]overlay={SH_X}:0:shortest=1,format=yuv420p[v];"
                                    f"[1:a]aresample=44100,aformat=channel_layouts=stereo[a]",
                 "-map", "[v]", "-map", "[a]", "-t", f"{cut:.2f}", "-c:v", "libx264", "-r", str(FPS), "-crf", "20", "-preset", "medium",
                 "-c:a", "aac", "-b:a", "160k", seg])
            segs.append(seg); starts.append(t); t += cut
        lst = os.path.join(work, "list.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{s}'\n" for s in segs)
        name = f"sidefrog-frank-{kind}-{len(eps)}-side-hustles-{stamp}"
        out = os.path.join(out_dir, name + ".mp4")
        run(["-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
             "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
        intro_card(eps, countdown).save(os.path.join(out_dir, name + "-thumbnail.png"))
        with open(os.path.join(out_dir, name + "-package.txt"), "w", encoding="utf-8") as f:
            f.write(package(eps, starts, name, countdown))
        if voice:                                 # file it with this compilation so it isn't reused next time
            dest = os.path.join(out_dir, "voice-intro" + os.path.splitext(voice)[1].lower())
            try: shutil.move(voice, dest)
            except OSError: shutil.copy2(voice, dest)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"{out} ({t:.0f} seconds, {len(eps)} episodes)")
    if not voice:
        print("Optional: save a short voice intro as SideFrog\\voice-intro.m4a and the next compilation opens with it.")
    print(f"YouTube package and thumbnail are in {out_dir}")


NAMES = {"depop": "Depop", "etsy": "Etsy", "ebay": "eBay", "amazon": "Amazon", "airbnb": "Airbnb", "youtube": "YouTube",
         "tiktok": "TikTok", "instagram": "Instagram", "facebook": "Facebook", "linkedin": "LinkedIn", "uber": "Uber",
         "doordash": "DoorDash", "shopify": "Shopify", "kdp": "KDP", "fba": "FBA", "ai": "AI", "christmas": "Christmas"}


def lower(idea):
    """Sentence-case an idea for running text, keeping brand names: "Depop clothing resale shop"."""
    return " ".join(NAMES.get(re.sub(r"[^a-z]", "", w.lower()), w.lower()) for w in idea.split())


def package(eps, starts, name, countdown=False):
    def stamp(s):
        s = int(s); return f"{s // 60}:{s % 60:02d}"
    n = len(eps)
    good = [e for e in eps if e["verdict"] in GOOD]
    # YouTube ignores chapters unless the first is at 0:00 and each runs 10 seconds or more, so the
    # 3-second intro belongs to the first chapter
    chapters = [f"{stamp(0 if k == 0 else s)} {'#' + str(n - k) + ' ' if countdown else ''}{e['idea']}: {e['verdict'] or 'Frank takes a look'}"
                for k, (e, s) in enumerate(zip(eps, starts))]
    ideas = ", ".join(lower(e["idea"]) for e in eps[:-1]) + f" and {lower(eps[-1]['idea'])}"
    desc = [f"Can you actually make money with any of these? Frank reviews {n} side hustles: {ideas}.",
            (f"{['None', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight'][len(good)] if len(good) < 9 else len(good)} of them might be worth a weekend. " if good else "") + "Each one ends with a cheap way to test it yourself before you spend real money.",
            "\n".join(chapters),
            "Check your own idea free, no sign-up: https://sidefrog.com/?utm_source=youtube&utm_medium=video&utm_campaign=compilation",
            "Which one would you try? Tell Frank in the comments.", "#SideFrog #SideHustle #BusinessIdeas"]
    if countdown:
        abc = sorted(eps, key=lambda e: e["idea"].lower())          # alphabetical, so the list doesn't give #1 away
        ideas = ", ".join(lower(e["idea"]) for e in abc[:-1]) + f" and {lower(abc[-1]['idea'])}"
        desc[0] = f"Frank counts down {n} side hustles, worst to best: {ideas}. {countdown_tease(eps).replace('#1', 'Number one')}"
    tags = ["side hustle", "side hustle ideas", "side hustles that make money", "business ideas", "small business ideas",
            "extra income", "SideFrog"] + [e["idea"].lower() for e in eps]
    import claims                                  # only claims the episodes back up (costs, verdicts, ease)
    titles = claims.checked_titles(eps, countdown)
    if countdown:                                  # a countdown's title says it's ranked
        strong = [t + ", Ranked" for t in titles if any(k in t for k in ("You Can Test", "Easy to Start", "Would Actually Try"))]
        titles = list(dict.fromkeys(strong + [t for t in titles if "Ranked" in t] + titles))
    return "\n\n".join([
        f"TITLE\n{titles[0]}",
        "OTHER TITLE OPTIONS\n" + "\n".join(titles[1:]) + "\n" + claims.boring_note(),
        "DESCRIPTION\n" + "\n\n".join(desc),
        "TAGS\n" + ", ".join(dict.fromkeys(tags)),
        "THUMBNAIL\nUpload the -thumbnail.png in this folder (YouTube lets regular videos have a custom thumbnail).",
        f"FILENAME\n{name}.mp4",
    ]) + "\n"


if __name__ == "__main__":
    stitch(sys.argv[1:])
