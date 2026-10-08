#!/usr/bin/env python3
r"""The Cheap Test Playbook: builds the book from your episodes and saved ideas.

    python video\make_short.py playbook            build the book (Frank fills in anything missing)
    python video\make_short.py playbook final      the version to sell (stops only if a page is still incomplete)
    python video\make_short.py playbook offline    build from what's saved, without asking Frank for anything

Where the pages come from (one page per idea):
    SideFrog\episodes\NNN-idea\episode-NNN.json    every episode you've made, if it has Frank's full answer
    SideFrog\playbook\ideas\*.json                 ideas you haven't filmed: the Studio's "Save for the
                                                   playbook" button (they're moved out of Downloads for you)
    SideFrog\playbook\part-1.txt                   the "how to test anything" chapter, in your words
                                                   (made with a starting draft the first time; edit it freely)

What it writes, in SideFrog\playbook\:
    the-cheap-test-playbook.html    open it in Chrome and print to PDF (Letter, margins: none,
                                    background graphics: on) if the PDF below wasn't made
    the-cheap-test-playbook.pdf     made automatically when Playwright is installed
                                    (pip install playwright, then: python -m playwright install chromium)

Nothing to write: for any page that's missing pieces (older episodes, ideas with no take), it asks
Frank's service (the same one the site uses) for that page: Frank's full answer, your take drafted in
your voice, who the idea is best for, and what going past the test costs. A published episode keeps
its real verdict, reason and cheap test; a take you wrote yourself in the Studio always wins over a
drafted one. Answers are saved into the episode or idea file, so each idea is asked about once.
It waits about 11 seconds between requests (the service allows 6 a minute and 40 an hour); with more
than 40 new pages, run it again an hour later and it picks up where it stopped.
Frank's parts are labeled as his AI-assisted read, there are no earnings claims, and the only dollar
figures are what things cost.
"""
import glob, html, json, os, re, shutil, sys, time, urllib.request, urllib.error
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_short as ms

SIDEFROG = os.path.dirname(ms.ROOT)
BOOK = os.path.join(SIDEFROG, "playbook")
IDEAS = os.path.join(BOOK, "ideas")
API = os.environ.get("SIDEFROG_API", "https://4s7uc7iyyeh7p4sknfpo6agllq0ahdff.lambda-url.us-east-1.on.aws/")   # Frank's service
TITLE = "The Cheap Test Playbook"
SUBTITLE = "Side hustles, and the cheapest way to test each one before you spend real money"
AUTHOR = "Mark Flournoy, with Frank"

VERDICT = {"great": ("Surprisingly, yes", 0), "worth_a_shot": ("This could work", 1), "crowded": ("Crowded pond", 2),
           "nah": ("Keep your day job", 2), "cant_help": ("Can't help", 3)}
FROM_LINES = {("SURPRISINGLY,", "YES"): "great", ("THIS COULD", "WORK"): "worth_a_shot", ("CROWDED", "POND"): "crowded",
              ("KEEP YOUR", "DAY JOB"): "nah", ("CAN'T HELP", "WITH THAT ONE"): "cant_help"}
EASE = {"easy": "Easy", "some_setup": "Some setup", "hard": "Hard"}
CATEGORIES = ["Local services", "Selling things", "Skills from home", "Other ideas", "Ones Frank says to skip"]

PART_1_DRAFT = """## How to use this book
Every idea in here gets the same page. At the top is Frank's verdict and why. Under it: how hard it is to start, how soon a first dollar could come in, and what the test costs. Then the test itself, and the result that tells you to keep going or to stop. At the bottom is what I'd actually do.

Frank's verdicts come from SideFrog, which uses Google's Gemini to read each idea. They're a quick, honest read, not market research. The takes at the bottom of each page are mine.

Nothing in here promises income. The only dollar figures are what each test costs you.

## Frank's rules for testing
1. Spend under $100 before your first sale. If the test costs more than that, find a smaller test.
2. Sell it before you build it. A deposit, a pre-order or a booked first job tells you more than any survey.
3. Write down your numbers first. Decide what counts as a yes and what counts as a no before you start, so you can't talk yourself into it later.
4. Give it three weekends. That's long enough to learn something and short enough that you won't mind stopping.
5. Keep a log. One line per weekend: what you did, what it cost and what happened. There's a page for it at the back.
6. A no is a useful answer. You found out for the price of a few weekends instead of a year and your savings.
"""


# ---------------------------------------------------------------- the entries
def _first(*vals):
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def from_episode(e, source):
    """One playbook entry from an episode or idea file. Frank's answer can be under "frank" (saved by the
    Studio) and/or "playbook" (asked for by this tool); what the episode itself says always wins."""
    f = {**(e.get("playbook") or {}), **{k: v for k, v in (e.get("frank") or {}).items() if v}}
    pb = e.get("playbook") or {}
    verdict = FROM_LINES.get(tuple(e.get("verdict", [])), f.get("verdict", "worth_a_shot"))
    return dict(idea=_first(e.get("re"), f.get("subject")), verdict=verdict, category=_first(e.get("category"), pb.get("category")),
                best_for=_first(pb.get("bestFor")), after_test=_first(pb.get("costAfterTest")),
                reason=_first(e.get("reason"), f.get("verdictReason")), test=_first(e.get("cheap_test"), f.get("firstMove")),
                ease=_first(e.get("ease"), f.get("easyToStart")), first_dollar=_first(e.get("first_dollar"), f.get("firstDollar")),
                test_cost=_first(e.get("test_cost"), f.get("testCost")), who_pays=_first(f.get("whoPays")),
                keep_going=_first(f.get("goodSign")), rethink=_first(f.get("rethinkIf")),
                catch=_first(f.get("watchOut")), sharper=_first(f.get("sharpenedIdea")), take=_first(e.get("take"), pb.get("take")),
                episode=e.get("number"), source=source, sample=bool(e.get("sample")))


NEEDED = ("take", "best_for", "after_test", "who_pays", "keep_going", "rethink", "catch", "ease", "first_dollar", "test_cost", "category")


def complete(x):
    return all(x.get(k) for k in NEEDED)


def ask_frank(e):
    """Frank's service, "playbook" request: the whole page, keeping what's already decided."""
    known = {"verdict": FROM_LINES.get(tuple(e.get("verdict", [])), ""), "reason": e.get("reason", ""), "test": e.get("cheap_test", "")}
    body = json.dumps({"kind": "playbook", "idea": e.get("re") or (e.get("frank") or {}).get("subject", ""), "known": known}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={"Content-Type": "text/plain;charset=UTF-8",
                                                                          "User-Agent": "SideFrog playbook builder"})
    with urllib.request.urlopen(req, timeout=40) as res:
        return json.loads(res.read().decode("utf-8"))["playbook"]


_last_call = [0.0]
def fill_from_frank(path, e):
    """Ask once, save the answer into the file. Returns True if the file was updated."""
    for attempt in range(3):
        wait = 11 - (time.time() - _last_call[0])
        if wait > 0: time.sleep(wait)
        _last_call[0] = time.time()
        try:
            e["playbook"] = ask_frank(e)
            with open(path, "w", encoding="utf-8") as f: json.dump(e, f, indent=2)
            return True
        except urllib.error.HTTPError as err:
            if err.code in (429, 503) and attempt < 2:
                print("  Frank's service is busy: waiting a minute"); time.sleep(60); continue
            if err.code == 429:
                raise RuntimeError("hourly limit")
            print(f"  Frank's service answered {err.code}: skipping this one for now")
            return False
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as err:
            print(f"  Couldn't reach Frank's service ({err.__class__.__name__}): skipping this one for now")
            return False
    return False


def load_entries(ask=True):
    """Episodes first, then saved ideas; the same idea twice keeps the later one. With ask, any page
    that's missing pieces is filled in by Frank's service (and saved, so it's asked once)."""
    entries, files = {}, []
    for path in sorted(glob.glob(os.path.join(ms.EPISODES, "[0-9][0-9][0-9]-*", "episode-*.json"))):
        files.append((path, "episode"))
    for path in sorted(glob.glob(os.path.join(IDEAS, "*.json"))):
        files.append((path, "idea"))
    todo = []
    for path, kind in files:
        try:
            e = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            print(f"Skipping {path}: it isn't a readable {kind} file.")
            continue
        x = from_episode(e, path)
        if not x["idea"]:
            continue
        if ask and not complete(x) and not e.get("sample"):
            todo.append((path, e))
        entries[x["idea"].lower()] = x
    if todo:
        print(f"Asking Frank to fill in {len(todo)} page{'s' if len(todo) != 1 else ''} (about {len(todo) * 11 // 60 + 1} min)...")
        for k, (path, e) in enumerate(todo, 1):
            print(f"  {k}/{len(todo)}  {e.get('re') or path}")
            try:
                if fill_from_frank(path, e):
                    x = from_episode(e, path); entries[x["idea"].lower()] = x
            except RuntimeError:
                print("Frank's service has hit its hourly limit. The book is built with what's done; run this again in an hour for the rest.")
                break
    out = list(entries.values())
    for x in out:                                       # Frank's "Keep your day job" ideas go in the skip chapter
        if x["verdict"] in ("nah", "cant_help"): x["category"] = "Ones Frank says to skip"
        elif x["category"] not in CATEGORIES: x["category"] = "Other ideas"
    out.sort(key=lambda x: (CATEGORIES.index(x["category"]), x["idea"].lower()))
    return out


def collect_downloads():
    """Move "Save for the playbook" files out of Downloads into playbook\\ideas."""
    os.makedirs(IDEAS, exist_ok=True)
    for p in glob.glob(os.path.join(ms.DOWNLOADS, "playbook-idea-*.json")):
        dest = os.path.join(IDEAS, re.sub(r" \(\d+\)", "", os.path.basename(p)))
        try: shutil.move(p, dest)
        except OSError: shutil.copy2(p, dest)
        print(f"Added {os.path.basename(dest)} to the playbook")


# ---------------------------------------------------------------- the pages
_posted = None
def posted_episodes():
    """Episode numbers with a YouTube link in episode-log.csv (only those pages point to YouTube)."""
    global _posted
    if _posted is None:
        import csv
        _posted = set()
        if os.path.exists(ms.LOG):
            with open(ms.LOG, newline="", encoding="utf-8-sig") as f:
                _posted = {int(r["Episode"]) for r in csv.DictReader(f) if r.get("Episode", "").isdigit() and r.get("YouTube link", "").strip()}
    return _posted


def esc(s):
    return html.escape(str(s or ""))


def frank_img(face):
    return Path(ms.frame_path("round", 504, face)).as_uri()


def page(body, n, cls="", draft=False):
    foot = f'<footer><span>{esc(TITLE)}</span><span>{"DRAFT · " if draft else ""}sidefrog.com</span><span>{n}</span></footer>' if n else ""
    return f'<section class="page {cls}">{body}{foot}</section>'


def cover(draft):
    return page(f'''
      <div class="cover-top"><p class="kicker">SideFrog · For people who hate Mondays</p></div>
      <h1>{esc(TITLE)}</h1>
      <p class="cover-sub">{esc(SUBTITLE)}</p>
      <img class="cover-frank" src="{frank_img(12)}" alt="">
      <p class="cover-by">{esc(AUTHOR)}</p>
      {'<p class="draft-mark">Draft</p>' if draft else ''}''', 0, "cover")


rows_extra = []        # (section heading, index of its page) for the contents


def part_one(text, start):
    """part-1.txt to pages: "## " starts a section; a line of three dashes (---) starts a new page."""
    rows_extra.clear()
    blocks, cur = [], None
    for line in text.splitlines():
        if line.strip() == "---":                      # a line of three dashes starts a new page
            if blocks: blocks[-1]["break"] = True
        elif line.startswith("## "):
            cur = {"h": line[3:].strip(), "lines": []}; blocks.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    pages = []
    for k, b in enumerate(blocks):
        paras, items, buf = [], [], []
        def flush():
            if buf: paras.append(f"<p>{esc(' '.join(buf))}</p>"); buf.clear()
        for line in b["lines"]:
            m = re.match(r"\s*(\d+)\.\s+(.*)", line)
            if m:
                flush(); head, _, rest = m.group(2).partition(". ")
                items.append(f'<li><span class="n">{m.group(1)}</span><p><b>{esc(head)}.</b> {esc(rest)}</p></li>')
            elif line.strip(): buf.append(line.strip())
            else: flush()
        flush()
        body = "".join(paras) + (f'<ol class="rules">{"".join(items)}</ol>' if items else "")
        section = f'<h2>{esc(b["h"])}</h2>{body}'
        if pages and not blocks[k - 1].get("break"):
            h, prev = pages[-1]; pages[-1] = (h, prev + f'<div class="gap"></div>{section}')
            rows_extra.append((b["h"], len(pages) - 1))
        else:
            pages.append((b["h"], f'<p class="kicker">Part 1 · How to test anything</p>{section}'))
            rows_extra.append((b["h"], len(pages) - 1))
    return pages


def idea_page(x, n, number):
    label, face = VERDICT.get(x["verdict"], VERDICT["worth_a_shot"])
    score = [("Easy to start?", EASE.get(x["ease"], "")), ("First dollar in", x["first_dollar"]), ("The test costs", x["test_cost"]),
             ("Past the test", x.get("after_test", ""))]
    score = "".join(f'<div><dt>{a}</dt><dd>{esc(b[:1].upper() + b[1:])}</dd></div>' for a, b in score if b)
    cap = lambda t: t[:1].upper() + t[1:]
    pair = "".join(f'<div><dt>{a}</dt><dd>{esc(cap(b))}</dd></div>' for a, b in (("Keep going if", x["keep_going"]), ("Rethink it if", x["rethink"])) if b)
    minor = "".join(f'<div><dt>{a}</dt><dd>{esc(cap(b))}</dd></div>' for a, b in
                    (("Who pays", x["who_pays"]), ("The catch", x["catch"]), ("The sharper version", x["sharper"])) if b)
    if x["take"]:
        take = f'<div class="take"><p class="kicker">Mark’s take</p><p>{esc(x["take"])}</p></div>'
    else:
        take = '<div class="take missing"><p class="kicker">Mark’s take</p><p>Still to come: Frank’s service couldn’t be reached for this page. Run the build again.</p></div>'
    ep = f' · Episode {x["episode"]:03d} on YouTube' if x.get("episode") in posted_episodes() else ""
    sample = '<p class="sample">Sample text: Frank’s answer for this idea wasn’t saved, so parts of this page are placeholders.</p>' if x.get("sample") else ""
    return page(f'''
      <p class="kicker">No. {number:02d} · {esc(x["category"])}{ep}</p>
      <div class="head">
        <div><h2>{esc(x["idea"])}</h2><p class="verdict v-{x["verdict"]}">{esc(label)}</p></div>
        <img class="frank" src="{frank_img(face)}" alt="">
      </div>
      <p class="lede">{esc(x["reason"])}</p>
      {f'<p class="bestfor"><b>Best for</b> someone who {esc(re.sub(r"^someone who ", "", x["best_for"], flags=re.I))}.</p>' if x.get("best_for") else ''}
      {f'<dl class="score">{score}</dl>' if score else ''}
      <div class="test"><p class="kicker">The cheap test{(" · " + esc(x["test_cost"])) if x["test_cost"] else ""}</p><p>{esc(x["test"])}</p></div>
      {f'<dl class="pair">{pair}</dl>' if pair else ''}
      {f'<dl class="minor">{minor}</dl>' if minor else ''}
      {take}{sample}
      <p class="fine">Frank’s verdict is an AI-assisted read from SideFrog, not market research or a promise of income.</p>''', n, "idea",
      draft=not x["take"])


def contents(rows, n):
    items, last = [], None
    for title, cat, pg in rows:
        if cat != last:
            items.append(f'<li class="cat">{esc(cat)}</li>'); last = cat
        items.append(f'<li><span>{esc(title)}</span><span class="dots"></span><span>{pg}</span></li>')
    return page(f'<p class="kicker">Contents</p><h2>What’s inside</h2><ol class="toc">{"".join(items)}</ol>', n)


def test_log(n):
    rows = "".join("<tr>" + "<td></td>" * 5 + "</tr>" for _ in range(14))
    return page(f'''<p class="kicker">Part 3 · Worksheets</p><h2>Test log</h2>
      <p>One line per weekend. Write your yes and no numbers at the top before you start.</p>
      <p class="fill">The idea: <span></span></p>
      <p class="fill half">Keep going if: <span></span></p><p class="fill half">Rethink it if: <span></span></p>
      <table class="log"><thead><tr><th>Date</th><th>What I did</th><th>What it cost</th><th>What happened</th><th>Next</th></tr></thead><tbody>{rows}</tbody></table>''', n)


CSS = """
@page { size: Letter; margin: 0; }
@font-face { font-family: "Bricolage"; src: url("FONT"); font-weight: 200 800; }
:root { --ink:#1F241F; --paper:#FBF7EF; --card:#FFFDF9; --muted:#5A5A4A; --deep:#4A5C34; --frog:#8DAA3F; --accent:#A4501F; --rule:#A89B84; --line:#E2D8C6; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #ddd; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font: 11.5pt/1.45 "Bricolage", system-ui, sans-serif; color: var(--ink); }
.page { position: relative; width: 8.5in; height: 11in; padding: 0.75in 0.8in 0.9in; background: var(--card); overflow: hidden;
        margin: 0 auto 0.3in; page-break-after: always; break-after: page; }
@media print { body { background: none; } .page { margin: 0; } }
footer { position: absolute; left: 0.8in; right: 0.8in; bottom: 0.45in; display: flex; justify-content: space-between;
         border-top: 1px solid var(--line); padding-top: 0.08in; font-size: 8.5pt; color: var(--muted); letter-spacing: 0.02em; }
.kicker { margin: 0 0 0.08in; font-size: 8.5pt; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase; color: var(--deep); }
h1 { font-size: 48pt; line-height: 0.98; letter-spacing: -0.035em; margin: 0.9in 0 0.2in; font-weight: 800; }
h2 { font-size: 32pt; line-height: 1.02; letter-spacing: -0.03em; margin: 0 0 0.14in; font-weight: 800; }
p { margin: 0 0 0.12in; }
.cover { background: var(--paper); }
.cover-sub { font-size: 16pt; line-height: 1.3; max-width: 5.4in; color: var(--muted); }
.cover-frank { display: block; width: 3.6in; margin: 0.55in auto 0; }
.cover-by { position: absolute; left: 0.8in; bottom: 0.7in; font-size: 13pt; font-weight: 700; margin: 0; }
.draft-mark, .sample { color: var(--accent); font-weight: 800; }
.draft-mark { position: absolute; right: 0.8in; bottom: 0.7in; margin: 0; letter-spacing: 0.14em; text-transform: uppercase; font-size: 10pt; }
.rules { list-style: none; padding: 0; margin: 0.2in 0 0; }
.gap { height: 0.3in; }
.rules li { display: grid; grid-template-columns: 0.5in 1fr; padding: 0.12in 0; border-top: 1px solid var(--line); }
.rules .n { font-size: 22pt; font-weight: 800; color: var(--frog); line-height: 1; }
.rules p { margin: 0; }
.toc { list-style: none; padding: 0; margin: 0.15in 0 0; }
.toc li { display: flex; gap: 0.08in; padding: 0.035in 0; }
.toc li.cat { margin-top: 0.14in; font-size: 8.5pt; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: var(--deep); }
.toc .dots { flex: 1; border-bottom: 1px dotted var(--rule); transform: translateY(-0.06in); }
.idea .head { display: grid; grid-template-columns: 1fr 1.7in; gap: 0.2in; align-items: start; }
.idea .frank { width: 1.7in; }
.verdict { display: inline-block; margin: 0.02in 0 0; padding: 0.04in 0.14in; border: 1.5px solid var(--ink); border-radius: 99px;
           font-size: 10pt; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
.v-great, .v-worth_a_shot { background: var(--frog); border-color: var(--frog); }
.v-nah { border-color: var(--accent); color: var(--accent); }
.lede { font-size: 16pt; line-height: 1.38; margin: 0.16in 0 0.24in; }
dl { margin: 0; } dt { font-size: 8pt; font-weight: 800; letter-spacing: 0.11em; text-transform: uppercase; color: var(--muted); }
dd { margin: 0.03in 0 0; }
.bestfor { margin: -0.1in 0 0.2in; font-size: 11.5pt; color: var(--muted); } .bestfor b { color: var(--deep); }
.score { display: grid; grid-template-columns: repeat(auto-fit, minmax(0, 1fr)); border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); margin-bottom: 0.2in; }
.score div { padding: 0.12in 0.16in 0.14in; } .score div:first-child { padding-left: 0; }
.score div + div { border-left: 1px solid var(--rule); } .score dd { font-size: 13pt; font-weight: 800; line-height: 1.2; }
.test { border-left: 4px solid var(--frog); padding: 0.02in 0 0.02in 0.18in; margin-bottom: 0.26in; }
.test p:last-child { font-size: 15pt; line-height: 1.38; font-weight: 500; margin: 0; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 0.2in; margin-bottom: 0.18in; } .pair dd { font-size: 13.5pt; }
.minor { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.2in; padding-top: 0.14in; border-top: 1px solid var(--line); }
.minor dd { font-size: 11pt; color: var(--muted); }
.take { position: absolute; left: 0.8in; right: 0.8in; bottom: 1.25in; display: block; padding: 0.18in 0.24in; background: var(--paper); border: 2px solid var(--ink); border-radius: 14px; box-shadow: 4px 4px 0 var(--ink); }
.take p:last-child { margin: 0; font-size: 13pt; line-height: 1.38; font-weight: 600; }
.take.missing { display: block; background: none; border: 2px dashed var(--accent); box-shadow: none; }
.take.missing p:last-child { color: var(--accent); font-weight: 500; }
.sample { position: absolute; left: 0.8in; right: 0.8in; bottom: 0.95in; margin: 0; font-size: 8.5pt; }
.fine { position: absolute; left: 0.8in; right: 0.8in; bottom: 0.72in; margin: 0; font-size: 8pt; color: var(--muted); }
.fill { display: flex; gap: 0.1in; align-items: end; margin: 0.12in 0; font-weight: 700; }
.fill span { flex: 1; border-bottom: 1px solid var(--rule); height: 0.22in; }
.fill.half { display: inline-flex; width: 48%; margin-right: 3%; } .fill.half + .fill.half { margin-right: 0; }
.log { width: 100%; border-collapse: collapse; margin-top: 0.2in; font-size: 9pt; }
.log th { text-align: left; padding: 0.06in; border-bottom: 2px solid var(--ink); font-weight: 800; }
.log td { height: 0.42in; border-bottom: 1px solid var(--line); }
.log td + td, .log th + th { border-left: 1px solid var(--line); }
"""


def build(final=False, ask=True):
    collect_downloads()
    entries = load_entries(ask)
    if not entries:
        sys.exit("No playbook pages yet. In the Short Studio, ask Frank about an idea, write your take, and click "
                 "\"Save for the playbook\" (or make an episode with the new Studio). Then run this again.")
    missing = [x["idea"] for x in entries if not x["take"]]
    if final and missing:
        sys.exit("These pages are still missing a take (Frank's service couldn't be reached for them). Run it again "
                 "in a few minutes:\n  - " + "\n  - ".join(missing))
    draft = bool(missing)
    os.makedirs(BOOK, exist_ok=True)
    part1_path = os.path.join(BOOK, "part-1.txt")
    if not os.path.exists(part1_path):
        with open(part1_path, "w", encoding="utf-8") as f: f.write(PART_1_DRAFT)
        print(f"Wrote a starting draft of Part 1 to {part1_path} (change it any time; the next build uses your version).")
    part1 = part_one(open(part1_path, encoding="utf-8").read(), 3)

    # page numbers: cover (unnumbered), contents = 2, Part 1, the ideas, the worksheet
    n = 3
    p1_pages = []
    for h, body in part1:
        p1_pages.append((h, body, n)); n += 1
    idea_pages = []
    for k, x in enumerate(entries, 1):
        idea_pages.append((x, n, k)); n += 1
    log_n = n
    rows = [(h, "Part 1 · How to test anything", p1_pages[i][2]) for h, i in rows_extra]
    rows += [(x["idea"], f"Part 2 · {x['category']}", pg) for x, pg, _ in idea_pages]
    rows += [("Test log", "Part 3 · Worksheets", log_n)]
    pages = [cover(draft), contents(rows, 2)] + [page(b, pg) for _, b, pg in p1_pages] \
            + [idea_page(x, pg, k) for x, pg, k in idea_pages] + [test_log(log_n)]
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(TITLE)}</title>'
           f'<style>{CSS.replace("FONT", Path(ms.FONT).as_uri())}</style></head><body>{"".join(pages)}</body></html>')
    out_html = os.path.join(BOOK, "the-cheap-test-playbook.html")
    with open(out_html, "w", encoding="utf-8") as f: f.write(doc)
    out_pdf = out_html[:-5] + ".pdf"
    made_pdf = to_pdf(out_html, out_pdf)
    print(f"{len(entries)} idea pages, {log_n} pages in all" + (" (DRAFT: some pages are incomplete)" if draft else ""))
    for idea in missing: print(f"  still incomplete: {idea}")
    print(f"Book: {out_pdf if made_pdf else out_html}")
    if not made_pdf:
        print("To make the PDF: open the .html in Chrome, Print, Save as PDF, Paper: Letter, Margins: None, "
              "Background graphics: on. (Or pip install playwright and python -m playwright install chromium.)")
    return out_pdf if made_pdf else out_html


def to_pdf(src, dest):
    """Print the book with Chromium through Playwright, and warn about any page whose text overflows."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page()
            pg.goto(Path(src).as_uri()); pg.wait_for_timeout(300)
            over = pg.evaluate("""() => [...document.querySelectorAll('.page')].map((p, i) => { if (p.classList.contains('cover')) return 0;
                const take = p.querySelector('.take'); const kids = [...p.children].filter(c => !['FOOTER'].includes(c.tagName)
                  && !c.classList.contains('take') && !c.classList.contains('fine') && !c.classList.contains('sample'));
                const bottom = Math.max(0, ...kids.map(c => c.getBoundingClientRect().bottom));
                const limit = take ? take.getBoundingClientRect().top - 8 : p.getBoundingClientRect().bottom - 80;
                return bottom > limit ? i + 1 : 0; }).filter(Boolean)""")
            if over:
                print(f"Heads-up: too much text on page(s) {', '.join(map(str, over))}: shorten those answers a little.")
            pg.pdf(path=dest, format="Letter", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            b.close()
        return True
    except Exception as err:                       # no Chromium installed, etc.: the HTML still works
        print(f"(Couldn't make the PDF automatically: {err.__class__.__name__}.)")
        return False


def playbook(args):
    build(final=any(a.lower() == "final" for a in args), ask=not any(a.lower() == "offline" for a in args))


if __name__ == "__main__":
    playbook(sys.argv[1:])
