#!/usr/bin/env python3
"""Build SideFrog's content pages: the Break Room guides, About, What it costs,
plus sitemap.xml, robots.txt and llms.txt.

Run from the site folder:  python3 make_pages.py
Edit the copy in PAGES below, never the built index.html files.

Voice (from the QuotaBird handoff): the coffee test, stop at the point, no
"X isn't Y. It's Z", no paired punchlines, no counted setups, contractions,
no em or en dashes, second person in guides, Mark's "I" only on About and
What it costs. One office aside per page.
The frog is Frank. About introduces him in one line ("He reads every idea that comes in and tells you what he thinks."); otherwise he never gets a biography, an explanation of the pun, or "Frank the Frog." He's just Frank.
Each guide gets its own Frank line as its label, so the bit doesn't turn into a tic.
"""
import html
import urllib.parse
import re
import json
import pathlib

BASE_URL = "https://sidefrog.com"      # change if the site lives elsewhere
CHECKED = "October 3, 2026"            # "last checked" date shown on every guide
CHECKED_ISO = "2026-10-03"
UPDATED = "October 2026"
HOME_UPDATED = "2026-10-03"           # the tool page's lastmod in sitemap.xml; bump when it changes              # shown in the colophon on every page
ROOT = pathlib.Path(__file__).parent

# ---- Frank, inline, so he can sip (frank.js picks when) ----------------------------




def frank_round_html(mood="smirk", look="you"):
    """Round Frank in a circle, matching Mark's portrait (About). Sips like the others."""
    return (f'<span class="frank-portrait" aria-hidden="true">'
            f'<span class="frank is-round can-sip" data-mood="{mood}" data-look="{look}"></span></span>')


def og_image(p):
    """A page's share card address with its version code; pages without a card (the 404) use the home card."""
    slug = slug_of(p)
    if (ROOT / "og" / f"{slug}.jpg").exists():
        return f"{BASE_URL}/og/{slug}.jpg?v={fingerprint('og/' + slug + '.jpg')}"
    return f"{BASE_URL}/og/home.jpg?v={fingerprint('og/home.jpg')}"


def frank_svg(cls, mood="smirk", look="you"):
    """Frank, from the sprite (see build_frank_sprite.py). The name is kept so callers don't change."""
    return f'<span class="frog frank {cls} can-sip" data-mood="{mood}" data-look="{look}" aria-hidden="true"></span>'


# Fonts: Google Fonts for now. Self-hosting (make_fonts.py, fonts/) is faster on phones but needs the
# live security policy to allow font-src 'self'; it didn't take effect on Amplify, so it's switched off.
# To switch it back on: confirm the live content-security-policy header includes font-src 'self', set
# SELF_HOST_FONTS = True, put the @font-face rules back at the top of styles.css, and rebuild.
SELF_HOST_FONTS = False
GOOGLE_FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Source+Serif+4:ital,wght@1,400&display=swap" rel="stylesheet">'
FONT_FILES = dict(l.split() for l in (ROOT / "fonts" / "fonts.txt").read_text().splitlines() if l.strip())
FONT = (f'<link rel="preload" href="/fonts/{FONT_FILES["bricolage"]}" as="font" type="font/woff2" crossorigin>'
        if SELF_HOST_FONTS else GOOGLE_FONTS)

NAV_TEMPLATE = '''<nav class="site-nav" aria-label="Sections"><a href="/break-room/"{br}>Break Room</a><a href="/side-kit/"{sk}>Side Kit</a></nav>'''


def site_nav(path):
    """Masthead links; the current section gets aria-current so it's marked."""
    cur = ' aria-current="page"'
    return NAV_TEMPLATE.format(
        br=cur if path.startswith('/break-room/') else '',
        bi=cur if path.startswith('/break-room/build/') else '',
        ab=cur if path.startswith('/about/') else '',
        sk=cur if path.startswith('/side-kit/') else '')


HEADER = '''<header class="site-header">
    <a class="wordmark" href="/">''' + frank_svg("wordmark-frog") + '''<span class="wordmark-words"><span class="wordmark-name">SideFrog</span><span class="wordmark-tag">For people who hate Mondays.</span></span></a>
    {NAV}
  </header>'''

FOOTER = '''<footer class="site-footer">
    <p class="footer-tag">For people who hate Mondays.</p>
    <p class="footer-aside">Made for coffee breaks. Your manager remains uninformed.</p>
    <nav class="footer-nav" aria-label="More from SideFrog"><a href="/break-room/">Break Room</a><span class="dot" aria-hidden="true">·</span><a href="/side-kit/">Side Kit</a><span class="dot" aria-hidden="true">·</span><a href="/break-room/build/vibe-coding-101/">Build it</a><span class="dot" aria-hidden="true">·</span><a href="/what-it-costs/">What it costs</a><span class="dot" aria-hidden="true">·</span><a href="/about/">About</a><span class="dot" aria-hidden="true">·</span><a href="/about/#help">Get help</a><span class="dot" aria-hidden="true">·</span><a href="https://www.youtube.com/@SideFrogTV">YouTube</a></nav>
    <p class="fine-print"><span class="label">The fine print</span>Frank’s verdict is a quick AI read using Gemini 3.5 Flash-Lite, not market research. .com names are checked live at the registry. “Open” means no registry record was found, but premium or reserved names can still be unavailable, so confirm before you buy. Not legal, financial, or trademark advice. Your idea goes to Google’s Gemini to write the verdict; SideFrog itself doesn’t store what you type.</p>
    <p class="colophon"><span class="label">Colophon</span>SideFrog is made by <a href="/about/">Mark Flournoy</a> in California. Vibe coded with Claude over a weekend for about $20. So yeah, <a href="/break-room/build/vibe-coding-101/">you can probably build your thing too</a>. Set in Bricolage Grotesque. Printed on the internet. Updated ''' + UPDATED + '''.</p>
  </footer>'''

CALENDLY = "https://calendly.com/markflournoy/vibe-code?utm_source=sidefrog&amp;utm_medium="
LINKEDIN = "https://www.linkedin.com/in/markflournoy/"

# Viewing from your desktop (file://): folder links open their index.html. Does nothing on the live site.
LOCAL_LINKS = '<script src="/local-links.js" defer></script>'

CTA = '''<div class="cta-box">
      <p><strong>Got an idea?</strong> SideFrog gives you a straight verdict, who'd pay, a first test to run and names with an open .com, in about ten seconds.</p>
      <a class="plate-btn" href="/">Check your idea</a>
      <p class="help-line">Want help building it? Mark helps people vibe code their first site with AI. <a href="{cal}" target="_blank" rel="noopener">Pick a time with Mark</a> or <a href="{li}" target="_blank" rel="noopener">message him on LinkedIn</a>.</p>
    </div>'''


def page_html(p):
    """Wrap one page's body in the shared shell."""
    url = BASE_URL + p["path"]
    title = html.escape(p["title"])
    desc = html.escape(p["description"])
    crumbs = ""
    if p.get("section"):
        crumbs = f'<p class="crumbs"><a href="/break-room/">Break Room</a> / {html.escape(p["section"])}</p>'
    take = ""
    if p.get("take"):
        label = p.get("take_label", "A note from Frank")
        take = f'''<div class="take">
      {'<img class="take-photo" src="/mark-portrait.jpg" alt="Mark" width="68" height="68">' if p.get("take_photo") else frank_svg("take-frog", p.get("frank_mood", "smirk"))}
      <div><p class="take-label">{label}</p><blockquote>{p["take"]}</blockquote></div>
    </div>'''
    faq_html, ld = "", []
    if p.get("faq"):
        items = "".join(f"<h3>{html.escape(q)}</h3><p>{a}</p>" for q, a in p["faq"])
        faq_html = f'<section class="faq"><h2>Questions people ask</h2>{items}</section>'
        ld.append({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in p["faq"]],
        })
    if p.get("article"):
        ld.append({
            "@context": "https://schema.org", "@type": "Article", "headline": p["h1"],
            "description": p["description"], "dateModified": p.get("updated", CHECKED_ISO), "url": url,
            "author": {"@type": "Person", "name": "Mark Flournoy", "url": BASE_URL + "/about/"},
            "publisher": {"@type": "Organization", "name": "SideFrog", "url": BASE_URL + "/"},
        })
    if p.get("section"):
        ld.append({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "SideFrog", "item": BASE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": "Break Room", "item": BASE_URL + "/break-room/"},
                {"@type": "ListItem", "position": 3, "name": p["h1"], "item": url},
            ],
        })
    ld += p.get("extra_ld", [])
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    sources = ""
    if p.get("sources"):
        lis = "".join(f'<li><a href="{u}" rel="noopener">{html.escape(t)}</a></li>' for t, u in p["sources"])
        sources = f'<section class="sources"><h2>Sources</h2><p>Last checked {CHECKED}.</p><ul>{lis}</ul></section>'
    related = ""
    if p.get("related"):
        rows = "".join(f'<li><a class="row" href="{PAGES[k]["path"]}"><span class="row-main">{html.escape(PAGES[k]["h1"])}</span><span class="row-cue" aria-hidden="true">Read</span></a></li>' for k in p["related"])
        related = f'<section class="related"><h2>Read next</h2><ul class="rows">{rows}</ul></section>'
    slug = p["path"].strip("/").split("/")[-1] or "home"
    cta = CTA.format(cal=CALENDLY + slug, li=LINKEDIN) if p.get("cta", True) else ""
    if p.get("help_box"):
        cta = HELP_BOX.format(cal=CALENDLY + slug) + "\n      " + cta
    editorial = bool(p.get("article") or p.get("contents"))
    if p.get("article"):
        # the editorial guide: label, headline, one-line description, byline; a ruled side rail
        if p.get("numbered"):
            steps_html, titles = editorial_steps(pull_lines(p["body"]))
        else:
            steps_html, titles = pull_lines(p["body"]), []
        byline = " · ".join(([f"{len(titles)} steps"] if titles else []) + [f"{read_minutes(p)} min read", f"Updated {UPDATED}"])
        note = ""
        if p.get("take"):
            note = (f'<aside class="ed-rail-piece ed-note-piece"><div class="ed-frank-note">{frank_svg("take-frog", p.get("frank_mood", "smirk"))}'
                    f'<div><p class="ed-kicker">{p.get("take_label", "A note from Frank")}</p><blockquote>{p["take"]}</blockquote></div></div></aside>')
        toc = ""
        if titles:
            toc = ('<aside class="ed-rail-piece ed-toc-piece"><p class="ed-kicker">In this guide</p><ol class="ed-mini">'
                   + "".join(f'<li><span><a href="#step-{i}">{t}</a></span></li>' for i, t in enumerate(titles, 1)) + "</ol></aside>")
        read_next = ""
        if p.get("related"):
            read_next = ('<aside class="ed-rail-piece ed-related-piece"><p class="ed-kicker">Read next</p><ol class="ed-mini">'
                         + "".join(f'<li><span><a href="{PAGES[k]["path"]}">{html.escape(PAGES[k]["h1"])}</a>'
                                   f'<small>{html.escape(PAGES[k].get("blurb", ""))}</small></span></li>' for k in p["related"]) + "</ol></aside>")
        main_html = f'''<main class="ed ed-article">
    <header class="ed-mast">
      <p class="ed-kicker"><a href="/break-room/">The Break Room</a> · {html.escape(p.get("section", ""))}</p>
      <h1 class="ed-title">{html.escape(p["h1"])}</h1>
      <p class="ed-dek">{html.escape(p.get("blurb", p["description"]))}</p>
      <p class="ed-byline">{byline}</p>
    </header>
    <div class="ed-grid">
      {note}
      <article class="ed-body prose">
        {steps_html}
        {guide_share(p)}
        {cta}
        {faq_html}
        {sources}
      </article>
      {toc}
      {read_next}
    </div>
  </main>'''
    elif p.get("contents"):
        main_html = f'''<main class="ed">
    <header class="ed-mast">
      <p class="ed-kicker">{p.get("kicker_html", "The Break Room")}</p>
      <h1 class="ed-title">{html.escape(p["h1"])}</h1>
      <p class="ed-dek">{html.escape(p.get("dek", ""))}</p>
    </header>
    {p["body"]}
  </main>'''
    else:
        main_html = f'''<main>
    {crumbs}
    {'<img class="who-photo" src="/mark-portrait.jpg" alt="Mark Flournoy" width="120" height="120">' if p.get("portrait") else ""}
    {f'<p class="eyebrow">{html.escape(p["eyebrow"])}</p>' if p.get("eyebrow") else ""}
    <h1>{html.escape(p["h1"])}</h1>
    {f'<p class="dek">{html.escape(p["dek"])}</p>' if p.get("dek") else ""}
    {take}
    <div class="prose">
      {number_steps(p["body"]) if p.get("numbered") else p["body"]}
    {guide_share(p)}
      {cta}
      {faq_html}
      {related}
      {sources}
    </div>
  </main>'''
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{url}">
  <meta property="og:site_name" content="SideFrog">
  <meta property="og:image" content="{og_image(p)}">
  <meta property="og:image:width" content="2400">
  <meta property="og:image:height" content="1260">
  <meta property="og:image:alt" content="SideFrog: {html.escape(p['h1'])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{og_image(p)}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="{"article" if p.get("article") else "website"}">
  <meta property="og:url" content="{url}">
  <meta name="theme-color" content="#FBF7EF">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="ard" type="application/json" href="/ard.json">
  {FONT}
  <link rel="stylesheet" href="/styles.css">
  {ld_html}
</head>
<body class="page{' ed-page' if editorial else ''}">
  {HEADER.replace("{NAV}", site_nav(p["path"]))}

  {main_html}

  {FOOTER}
  <script src="/analytics.js" defer></script>
  <script src="/frank.js" defer></script>
  {"".join(f'<script src="{s}" defer></script>' for s in p.get("scripts", []))}{'<p class="sr-only" id="kit-announce" aria-live="polite"></p>' if p.get("scripts") else ""}
  {LOCAL_LINKS}
</body>
</html>
'''


def relative(doc, path):
    """Root-relative links and assets become relative to this page, so the
    site works opened straight from disk as well as on the live domain."""
    depth = len([x for x in path.strip("/").split("/") if x])
    prefix = "../" * depth
    for attr in ("href", "src"):
        doc = doc.replace(f'{attr}="/', f'{attr}="{prefix}')
    return doc


def slug_of(p):
    return p["path"].strip("/").split("/")[-1] or "home"


def editorial_steps(body):
    """Numbered guides as editorial steps: a big number, the step heading, the text, a rule between steps.
    Returns the HTML and the step titles (for the In this guide list)."""
    parts = re.split(r"<h2>(.*?)</h2>", body, flags=re.S)
    out, titles = [parts[0]], []
    for i in range(1, len(parts), 2):
        n = len(titles) + 1
        titles.append(parts[i])
        out.append(f'<section class="ed-step" id="step-{n}"><div class="ed-step-num" aria-hidden="true">{n:02d}</div>'
                   f'<h2>{parts[i]}</h2><div class="ed-step-body">{parts[i + 1]}</div></section>')
    return "".join(out), titles


def pull_lines(body):
    """The one-line asides become italic pull lines."""
    return re.sub(r'<p class="aside">', '<p class="ed-pull">', body)


def number_steps(body):
    """Office-manual numbering for sequential guides: 1., 2., 3. on each step heading."""
    n = 0
    def num(m):
        nonlocal n
        n += 1
        return f'<h2><span class="step">{n}.</span> '
    return re.sub(r"<h2>", num, body)


import hashlib

ASSET_RE = re.compile(r'(href|src)="(/|(?:\.\./)*)((?:styles\.css|app\.js|frank\.js|analytics\.js|local-links\.js|side-kit\.js|site\.webmanifest|favicon[^"?]*|apple-touch-icon\.png|mark(?:-mono)?\.jpg|frogs/[^"?]+))(?:\?v=[0-9a-f]+)?"')
_fingerprints = {}


def fingerprint(asset):
    """First 8 characters of the file's SHA-1: changes whenever the file does."""
    if asset not in _fingerprints:
        f = ROOT / asset
        _fingerprints[asset] = hashlib.sha1(f.read_bytes()).hexdigest()[:8] if f.exists() else None
    return _fingerprints[asset]


def stamp(doc):
    """styles.css -> styles.css?v=3f9a1c2e, so browsers fetch a file again only when it changed."""
    def sub(m):
        v = fingerprint(m.group(3))
        return f'{m.group(1)}="{m.group(2)}{m.group(3)}' + (f'?v={v}"' if v else '"')
    return ASSET_RE.sub(sub, doc)


def guide_share(p):
    """'Share this guide: LinkedIn · Copy link' at the end of every guide. Plain links, no tracking scripts."""
    if not p.get("article"):
        return ""
    url = BASE_URL + p["path"]
    li = "https://www.linkedin.com/sharing/share-offsite/?url=" + urllib.parse.quote(url, safe="")
    return (f'<p class="share-row guide-share"><span class="label-caps">Share this guide</span>'
            f'<a href="{li}" target="_blank" rel="noopener">LinkedIn</a><span class="dot" aria-hidden="true">\u00b7</span>'
            f'<button type="button" class="text-btn" data-copy-link="{url}">Copy link</button></p>')


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&")


def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


SBA = ("SBA: Choose your business name", "https://www.sba.gov/business-guide/launch/choose-your-business-name-register")
PORKBUN = ("Porkbun: products and free features", "https://porkbun.com/affiliate")
DOMAINOFFER = ("DomainOffer: .com prices across registrars", "https://domainoffer.net/tld/com/hover")
PEW = ("Pew Research Center: Do people click on links in Google AI summaries?", "https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/")
KWP = ("DYNO Mapper: using Google Keyword Planner", "https://dynomapper.com/blog/search-engine-optimization/how-to-use-googles-keyword-planner-like-a-pro/")

PAGES = {}

# ---------------------------------------------------------------- Guide 3
PAGES["test"] = dict(
    numbered=True,
    take_label="Let me be Frank",
    path="/break-room/start/test-an-idea-in-a-week/", section="Start", article=True,
    title="How to Test a Side Hustle Idea in a Week (Before You Buy Anything) | SideFrog",
    h1="Test a side hustle idea in a week",
    description="A cheap, one-week way to find out if strangers will pay for your side hustle idea, before you buy a domain, a logo or anything else.",
    take="Before you buy anything, find out if a stranger will hand over an email address or a deposit. Friends saying \u201cthat's a great idea\u201d doesn't count. You can find out in a week for about the price of a domain, or for free.",
    body='''
      <h2>Decide what \u201cyes\u201d looks like before you start</h2>
      <p>Write down two numbers before you run anything: the result that would make you keep going, and the result that would make you stop. Twenty sign-ups from strangers, three people willing to pay a deposit, five businesses that agree to a call. Pick your own. The point is to decide before you see the results, because afterwards every number looks encouraging.</p>
      <p>If you've run your idea through SideFrog, the \u201cCheap test\u201d line is a good starting point for the test.</p>

      <h2>Pick the test that fits the idea</h2>
      ''' + table(["If you're selling", "The cheapest real test"], [
        ["A service (bookkeeping, dog walking, tutoring)", "Offer it to five people this week at a real price. Do the work by hand."],
        ["A physical product", "A page with a pre-order or a waitlist. Don't make anything until people sign up."],
        ["Something digital (a template, a course, an app)", "A one-page sign-up with the price on it. Build it only after people ask for it."],
        ["Something local", "A post in the neighborhood group or a flyer on the coffee shop board, with a way to sign up."],
      ]) + '''

      <h2>Talk to ten people who'd actually pay</h2>
      <p>Not friends, not family, not coworkers. Find people who have the problem today: in a subreddit, a Facebook group, a trade forum, at the shop counter. Ask how they handle the problem now, what they've tried and what they've paid for. Skip \u201cWould you use this?\u201d because almost everyone says yes to be nice.</p>
      <p class="aside">Your coworkers are not a focus group. They also said the reorg was a great idea.</p>
      <p>SideFrog's \u201cTalk to ten buyers\u201d prompt, under every answer, writes the message and the questions for you.</p>

      <h2>Put up one page</h2>
      <p>A headline that says what it is, a sentence on who it's for, the price, and one button. That's the whole page. The button can open a free Google Form that collects an email address. SideFrog's \u201cBuild the page\u201d prompt gives Claude or ChatGPT everything it needs to write it as a single file you can put online.</p>
      <p>No logo, no business cards and no company paperwork yet. None of that tells you whether anyone wants it.</p>

      <h2>Send people to it</h2>
      <p>Share the page in the places you found in the last step, with a plain note: you're testing an idea and would value a look. Count three things: how many people visited, how many signed up, and how many replied with a question. Questions are a good sign; they mean someone is picturing themselves buying.</p>

      <h2>Read the result honestly</h2>
      <p>Compare what happened with the numbers you wrote down at the start. If you cleared the bar, keep going. If you missed it badly, that's a cheap answer, and SideFrog's alternative ideas are a decent place to look next. If you landed in between, change one thing (the price, the headline or who you're asking) and run it once more. Then decide.</p>
''',
    faq=[
        ("What if someone steals my idea?", "It's very unlikely that a stranger will drop everything to build your idea. The bigger risk is spending months on something nobody wants. Talking to people early is how you avoid that."),
        ("Should I spend money on ads for the test?", "Not at first. Free places where your buyers already gather tell you more, because people there can reply and ask questions. Small ads can come later, once you know what to say."),
        ("How long should I keep testing before I give up?", "Run the test once, change one thing and run it again. If two honest tries miss the number you set at the start, that's your answer for this version of the idea."),
    ],
    related=["search", "competition", "domain"],
    sources=[],
)

# ---------------------------------------------------------------- Guide 4
PAGES["search"] = dict(
    take_label="Frankly",
    path="/break-room/start/is-anyone-searching-for-this/", section="Start", article=True,
    title="Is Anyone Searching for Your Idea? Check Demand With Free Tools | SideFrog",
    h1="Is anyone searching for this?",
    description="How to check whether people search for what you want to sell, using Google autocomplete, Google Trends and the free Keyword Planner.",
    take="You don't need a paid tool to find out if people are looking for what you want to sell. Start typing it into Google and read what it finishes for you. If nobody's searching, you'll be paying to find every customer yourself.",
    body='''
      <h2>Start with Google's own suggestions</h2>
      <p>Open a private browser window, go to Google and type your idea slowly. Watch what autocomplete offers. Then search, and read the \u201cPeople also ask\u201d box and the related searches at the bottom of the page.</p>
      <p>This tells you the words buyers actually use, which are often different from yours. You might call it \u201cmeal prep for pet turtles.\u201d They type \u201cbest food for red eared slider.\u201d</p>
      <p class="aside">Autocomplete is the most honest market research you'll ever get. Nobody types a search to impress their boss.</p>

      <h2>Check the trend</h2>
      <p>Google Trends (trends.google.com) shows interest over time on a scale of 0 to 100, where 100 is the busiest point for that search. It won't give you a count, but it answers three useful questions: is interest growing, is it fading, and is it seasonal? Holiday ideas spike in November. Pool cleaning dies in January.</p>

      <h2>Get a rough number</h2>
      <p>Google's Keyword Planner is free inside a Google Ads account, and you don't have to run ads to use it. When the setup screens push you toward a campaign, look for the option to create an account without one. Google may ask for billing details along the way.</p>
      <p>Without ad spend it shows ranges like 100 to 1K or 1K to 10K searches a month instead of exact numbers. For deciding whether an idea has legs, a range is plenty.</p>

      <h2>Search where your buyers shop</h2>
      <p>A product idea lives or dies on Etsy, Amazon or the app stores more than on Google. Each one has its own search bar with its own suggestions. Type your idea there too. If a marketplace suggests it before you finish typing, people are looking.</p>

      <h2>How much search is enough?</h2>
      <p>Less than you'd think. A side hustle doesn't need millions of searches. A few hundred people a month searching for something specific and ready to buy (\u201cturtle food subscription\u201d) can be worth more than thousands searching for something vague (\u201cturtle facts\u201d).</p>
      <p>Look for searches with buying words in them: price, near me, best, for (a specific person), service, hire, subscription. Those are people with a wallet out.</p>
''',
    faq=[
        ("What if there's no search for my idea at all?", "It can mean the idea is new, or that people describe the problem differently. Try the words a customer would use for the problem rather than your solution. If those get no search either, plan on finding every customer yourself, through outreach or communities."),
        ("Are paid keyword tools worth it?", "Not for testing a side hustle. Google's suggestions, Google Trends, the free Keyword Planner and the free tools from companies like Ahrefs cover what you need to decide whether an idea has legs."),
        ("How accurate are these numbers?", "They're estimates, and the free Keyword Planner shows ranges on purpose. Use them to compare ideas and spot trends, not to forecast sales."),
    ],
    related=["competition", "test", "ai"],
    sources=[KWP],
)

# ---------------------------------------------------------------- Guide 5
PAGES["competition"] = dict(
    numbered=True,
    take_label="Just being Frank here",
    path="/break-room/start/size-up-the-competition/", section="Start", article=True,
    title="Who's Already Doing It? Size Up the Competition in an Hour | SideFrog",
    h1="Who's already doing it?",
    description="A one-hour way to find your competitors, read what their customers complain about and spot the opening for a small side hustle.",
    take="Somebody's probably already doing it, and that's mostly good news, because it means people pay for it. Spend an hour reading their bad reviews. That's where you'll find the customers they're letting down.",
    body='''
      <h2>Make a list of ten</h2>
      <p>Search the words you found in <a href="/break-room/start/is-anyone-searching-for-this/">Is anyone searching for this?</a> and write down who shows up. Check Google, Etsy or Amazon if it's a product, the app stores if it's an app, and Google Maps if it's local. A simple spreadsheet is enough:</p>
      ''' + table(["Column", "What to write"], [
        ["Name and link", "Where you found them"],
        ["Price", "What they charge, and how (one-time, monthly, per hour)"],
        ["Who it's for", "In their own words, from their homepage"],
        ["Reviews", "How many, and the average rating"],
      ]) + '''

      <h3>No competition is the warning sign</h3>
      <p>If you can't find anyone doing it, it usually means nobody's figured out how to make money at it yet. A crowded market only becomes a problem when you can't say who you're for.</p>

      <h2>Read the one- to three-star reviews</h2>
      <p>Go to Amazon, Etsy, Google Maps or the app store, whichever fits, and read the unhappy reviews of your top few competitors. Copy the complaints that come up again and again: too slow, too expensive, too complicated, nobody answers the phone. Those complaints are your selling points.</p>
      <p class="aside">Reading bad reviews is like reading the company engagement survey. Same complaints, every year.</p>
      <p>SideFrog's \u201cRead their bad reviews\u201d prompt will group the complaints for you if you paste them into Claude or ChatGPT.</p>

      <h2>Check what people pay</h2>
      <p>Note the cheapest price, the most expensive and where most of them land. If you plan to be cheaper than everyone, have a reason, because the cheapest option attracts the customers who leave fastest.</p>

      <h2>Look where people complain out loud</h2>
      <p>Search Reddit and Facebook groups for the competitor's name plus \u201calternative\u201d or \u201ctoo expensive.\u201d People who are actively looking for something else are your easiest first customers.</p>

      <h2>Find your opening</h2>
      <p>Usually it's one of three things: a smaller group of buyers the big players ignore, one problem they handle badly, or a simpler version for people who don't need everything. Write it as one sentence: \u201cFor [who], who are tired of [problem].\u201d If you can't fill in the blanks, keep reading reviews.</p>
''',
    faq=[
        ("What if a big company already does this?", "Big companies serve big groups of customers. A side hustle can win by serving a small group better, faster or more personally. Look for the customers they don't bother with."),
        ("Can I compete on price?", "You can, but it's the easiest advantage to lose. Someone can always go lower. A specific group of buyers or a problem you solve better holds up longer."),
        ("What if they copy me?", "Most won't notice a small new business. If they do, it usually means you found something real, and you'll know your customers better than they do."),
    ],
    related=["test", "search", "ai"],
    sources=[],
)

# ---------------------------------------------------------------- Guide 1
PAGES["name"] = dict(
    take_label="I'll be Frank",
    path="/break-room/name/check-if-a-business-name-is-taken/", section="Name", article=True,
    title="How to Check if a Business Name Is Taken (Domain, State, Trademark) | SideFrog",
    h1="How to check if a business name is taken",
    description="Where business names get registered, and how to check the domain, your state's business records, DBA filings and federal trademarks in about fifteen minutes.",
    take="A name can be free in your state and still belong to someone else. Check the .com, your state's business records and the federal trademark database before you order the mugs. It takes about fifteen minutes.",
    body='''
      <h2>Where a name can be taken</h2>
      <p>There isn't one master list. A name can be claimed in four different places, and each one covers something different:</p>
      ''' + table(["Where", "What it covers", "Where you check"], [
        ["Domain", "Your web address", "SideFrog, or any registrar's search"],
        ["State business records", "LLCs and corporations registered in one state", "Your Secretary of State's business search"],
        ["DBA (\u201cdoing business as\u201d)", "A trade name, filed with your state, county or city", "Depends on the state; the business search page usually says"],
        ["Federal trademark", "A name for a kind of goods or services, nationwide", "The USPTO's trademark search"],
      ]) + '''
      <p class="aside">Fifteen minutes. Shorter than the meeting about the meeting.</p>

      <h2>Check it in this order</h2>
      <ol>
        <li><strong>The domain.</strong> It's the fastest no. Type the name into SideFrog with your idea and it checks the .com live.</li>
        <li><strong>Your state's business search.</strong> Search \u201c[your state] secretary of state business search.\u201d Look for exact matches and names that differ only by a word like \u201cCo.\u201d or \u201cLLC.\u201d</li>
        <li><strong>DBA records.</strong> Some states keep these with the state, others with the county or city. Your state's business search page usually says where.</li>
        <li><strong>The federal trademark search.</strong> Search the USPTO's trademark database for your name and close spellings. Pay attention to names used for the same kind of business as yours.</li>
      </ol>

      <h2>The one to take seriously</h2>
      <p>A similar name in the same line of business is the kind of \u201ctaken\u201d that can cost you later. \u201cShellbite\u201d for turtle food and \u201cShellbite\u201d for a seafood restaurant are a different situation from two turtle food companies with the same name. If you find something close in your field, that's a question for a trademark attorney, not SideFrog.</p>

      <h2>What \u201cavailable\u201d means at each step</h2>
      <p>When your state says a name is available, it means no other company registered in that state has that exact name. It doesn't give you rights anywhere else, and it doesn't clear a trademark. An open .com only means nobody owns that address today.</p>

      <h2>If it's taken</h2>
      <p>Small changes often fix a domain problem: a second word, a different ending, dropping \u201cthe.\u201d They don't fix a trademark conflict in your line of business. If you're stuck, run the idea through SideFrog again; every answer comes with names whose .com is open right now.</p>
''',
    faq=[
        ("Does registering with my state protect the name everywhere?", "No. A state registration covers that state's business records. Nationwide protection for a brand name comes from a federal trademark, which is a separate process."),
        ("What if the name is close but not the same?", "Close names matter most when the businesses are similar. If you find a near match in your line of work, a trademark attorney can tell you whether it's a problem."),
        ("Can two businesses have the same DBA?", "Often, yes. Several businesses in one state can use the same trade name, which is why a DBA alone doesn't protect a name."),
    ],
    related=["domain", "test"],
    sources=[SBA],
)

# ---------------------------------------------------------------- Guide 2
PAGES["domain"] = dict(
    take_label="A note from Frank",
    path="/break-room/name/how-to-buy-a-domain/", section="Name", article=True,
    title="How to Buy a Domain Name (and Skip the Upsells) | SideFrog",
    h1="How to buy a domain",
    description="Where to buy a .com, what it should cost, which checkout add-ons to skip, and what to do with the domain once you have it.",
    take="Buy the .com for one year, say no to everything else at checkout, and make sure privacy is on. We point people to Porkbun because privacy is free there and the checkout doesn't fight you. We don't make anything from saying so.",
    body='''
      <h2>Should you buy it yet?</h2>
      <p>A domain is cheap, so it's tempting to grab it the moment you like a name. If SideFrog just told you to keep your day job, it can wait a week while you <a href="/break-room/start/test-an-idea-in-a-week/">test the idea</a>. If the name might disappear, $15 or so is a fair price for not worrying about it.</p>

      <h2>What a .com usually costs</h2>
      <p>A price tracker that compares registrars put the average .com at about $15 a year in May 2026. The number to look at is the renewal price, not the first year. Some registrars make year one cheap and year two expensive, so find the renewal line before you pay.</p>

      <h2>Where we'd buy it</h2>
      <p>Porkbun. WHOIS privacy is free there, so your name and address stay out of the public record without an extra charge, and so are SSL certificates, email forwarding and URL forwarding. The renewal price is easy to find. We don't get paid by Porkbun or any registrar. If that changes, this page will say so.</p>
      <p>Any registrar that shows you the renewal price up front and includes privacy is fine. SideFrog's own domains are on Amazon Route 53 because the site already runs on AWS. If you're not on AWS, Porkbun is simpler.</p>

      <h2>The checkout, step by step</h2>
      <ol>
        <li>Search for the exact name you want.</li>
        <li>Add the .com to your cart and find the renewal price.</li>
        <li>Make sure WHOIS privacy is on.</li>
        <li>Turn on auto-renew, so the domain doesn't lapse while you're busy.</li>
        <li>Turn on two-factor login for the account.</li>
        <li>Make sure the account is in your name, not your nephew's or your web designer's.</li>
      </ol>

      <h2>What you can skip for now</h2>
      <p class="aside">Decline the add-ons the way you'd decline an 8 a.m. \u201cquick sync.\u201d</p>
      <ul>
        <li><strong>Hosting.</strong> You don't need it to own the name, and a test page can live somewhere free.</li>
        <li><strong>Paid email.</strong> Free email forwarding sends hello@ your domain to the inbox you already have. Pay for a mailbox when you're emailing customers every day.</li>
        <li><strong>Other extensions</strong> (.net, .co, .shop) to \u201cprotect your brand.\u201d Buy them later if the business takes off.</li>
        <li><strong>Paid SSL.</strong> Free certificates do the same job for a small site.</li>
      </ul>

      <h2>Now point it somewhere</h2>
      <p>A domain on its own shows nothing. Point it at your one-page test site, or forward it to a link-in-bio page or a Google Form while you test. Set up hello@ forwarding the same day, so the first email from a customer doesn't bounce.</p>
''',
    faq=[
        ("Is .co or .io okay instead of .com?", "They work, but people type .com by habit, so some of your visitors will end up somewhere else. If the .com is taken, a slightly different name with an open .com is usually the better trade."),
        ("Should I buy more than one year?", "Not yet. One year with auto-renew on is enough while you find out whether the idea works."),
        ("Can I move the domain to another registrar later?", "Yes. Domains can be transferred between registrars, usually for the price of a year's renewal, which gets added to your registration."),
        ("What's a premium domain, and why is it $2,000?", "Some short or popular names are priced by the registry or held by investors. They can look open in a basic check. If the price at checkout is far above normal, pick another name."),
    ],
    related=["name", "test"],
    sources=[PORKBUN, DOMAINOFFER],
)

# ---------------------------------------------------------------- Guide 6
PAGES["ai"] = dict(
    take_label="Frank's take",
    path="/break-room/launch/getting-found-by-ai-answers/", section="Launch", article=True,
    title="Getting Found When People Ask AI Instead of Google | SideFrog",
    h1="Getting found when people ask AI instead of Google",
    description="What zero-click searches and AI answers mean for a small business, and plain steps to become the name an AI summary mentions.",
    take="A lot of people now get their answer from an AI summary and never click anything. For a small business, ranking first matters less than being the name the answer mentions. Write plain answers to the exact questions your buyers ask, and put them where the AI tools are reading.",
    body='''
      <h2>What changed</h2>
      <p>Pew Research Center looked at the Google searches of 900 U.S. adults in March 2025. When Google showed an AI summary, people clicked a regular search result in 8% of visits. Without a summary, they clicked in 15%. They clicked a source inside the summary in 1% of visits.</p>
      <p>Questions and longer searches got AI summaries far more often: 60% of searches that started with who, what, when or why produced one. These numbers are from March 2025, and AI answers have spread since, so treat them as a snapshot.</p>

      <h2>What it means for a side hustle</h2>
      <p>General questions (\u201chow often should I feed a turtle\u201d) send fewer people to websites now, because the answer appears right there. Searches from people ready to buy (\u201cturtle food subscription\u201d) still send clicks, and those are the visitors you want anyway. The goal is to be named in the answer for the first kind and clicked for the second.</p>

      <h2>Answer the questions yourself</h2>
      <p>Take the questions from <a href="/break-room/start/is-anyone-searching-for-this/">Is anyone searching for this?</a> (the \u201cPeople also ask\u201d box is the list) and answer each one on your site in two or three plain sentences. Say who it's for, what it costs and where you are. Put each question in its own heading. SideFrog's \u201cAnswer the questions\u201d prompt drafts these for you.</p>

      <h2>Be where the answers come from</h2>
      <p>In Pew's data, the sites cited most often in AI summaries and in regular results were Wikipedia, YouTube and Reddit. For a side hustle, that points to two things you can do: a short YouTube video that answers one question well, and honest, helpful posts in the subreddits your buyers read. If you're local, keep your Google Business Profile complete and ask happy customers for reviews.</p>
      <p class="aside">Nobody reads the deck after the all-hands. They remember who got mentioned.</p>

      <h2>Make your site easy for machines to read</h2>
      <ul>
        <li>A page title that says what you do and for whom.</li>
        <li>One sentence near the top that says the same thing in plain words.</li>
        <li>Your FAQ marked up as FAQ structured data, matching the visible text.</li>
        <li>An llms.txt file that lists your pages with a one-line description each. It's a young convention, not something Google has said it uses, but it's cheap to add.</li>
      </ul>

      <h2>Check yourself once a month</h2>
      <p>Ask ChatGPT, Claude, Gemini and Perplexity the question a buyer would ask, like \u201cwho delivers turtle food near Sacramento\u201d or \u201cbest turtle food subscription.\u201d Write down whether you show up, and who does. The ones who show up are doing something you can learn from.</p>
''',
    faq=[
        ("Is SEO still worth doing for a side hustle?", "Yes. The basics that help Google (clear titles, plain answers, pages people find useful) are the same things that get you mentioned in AI answers."),
        ("Should I pay for an \u201cAEO\u201d service?", "Not while you're testing an idea. Answering your buyers' questions clearly on your own site and showing up where they ask is most of the work, and you can do it yourself."),
        ("Should I block AI crawlers?", "If you want AI tools to mention you, they need to be able to read your site. Blocking them is a choice some publishers make, but it works against a small business trying to get found."),
        ("Does this matter if I only sell on Etsy?", "Less, because buyers search inside Etsy. A simple site with your FAQ still helps people who ask an AI tool before they shop."),
    ],
    related=["search", "competition", "test"],
    sources=[PEW],
)

# ---------------------------------------------------------------- About
PAGES["about"] = dict(
    path="/about/", title="About SideFrog: Made by Mark | SideFrog", eyebrow="About SideFrog",
    h1="SideFrog helps you decide which ideas are worth testing out.",
    description="SideFrog is a free side hustle idea checker built by Mark Flournoy, who retired early from Amazon and learned to build sites one cheap idea at a time.",
    cta=False,
    body='''
      <span class="who who-frank">''' + frank_round_html() + '''</span>
      <p>Frank is the frog. Type in an idea and he gives you a straight answer in seconds.</p>
      <p>Behind Frank, Google's Gemini reads your idea and works out who would pay for it, what to watch out for, a cheap test you can run this week, and the signs that tell you to keep going or rethink it. While that runs, SideFrog checks about 20 possible business names against the .com registry, live, and shows you only the ones you can still register.</p>
      <p>Frank likes ideas you can test cheaply and ideas people will actually pay for. He's skeptical of passive income promises and of anything that needs investors or a team before it can make its first sale.</p>
      <p><a class="plate-btn" href="/">Check an idea with Frank</a></p>

      <h2>The person behind Frank</h2>
      <span class="who who-mark"><span class="who-circle"><img src="/mark-portrait.jpg" alt="Mark Flournoy" width="120" height="120"></span></span>
      <p>I'm Mark. I retired early from Amazon at 56 and started building things, mostly small websites for ideas I wanted to try.</p>
      <p>When I started, I didn't know how to build a website. I learned how to buy a domain, set up hosting and form an LLC as I went. Now I can usually get an idea online in a day. I use Claude to think ideas through and write the code, and Gemini runs most of the AI work on the sites because it costs less.</p>
      <p>SideFrog is the checklist I use before I put money into an idea, turned into something you can use too. Most of my ideas cost about $16 for the domain and very little to run. Here's <a href="/what-it-costs/">what it actually costs me</a>.</p>
      <p>I also mentor salespeople and build sales tools at <a href="https://quotabird.com/">QuotaBird</a>. I recently moved to California after 15 years in Northern Virginia.</p>
      <p>Nothing on SideFrog pays me. If that ever changes, the page with the link will say so.</p>

      <h2>Who it's for</h2>
      <p>SideFrog is for people who hate Mondays. More specifically, people with office jobs who have an idea, or a few, and want to know whether one is worth trying. You don't have to quit your job to find out. Most of the tests Frank suggests fit into evenings and weekends.</p>

      <h2>What happens to your idea</h2>
      <p>Your idea goes to Google's Gemini to write the verdict. SideFrog doesn't store what you type.</p>
      <p>The verdict is an AI's quick read, not market research. The guides in the <a href="/break-room/">Break Room</a> show you how to check it yourself.</p>

      <h2 id="help">Want help?</h2>
      <p>If you've got an idea and want help turning it into a real site, I help people vibe code their first one with AI: the domain, the page, getting it online. Pick a time on my calendar and tell me what you're working on, or send me a message on LinkedIn if that's easier.</p>
      <p><a class="plate-btn" href="https://calendly.com/markflournoy/vibe-code?utm_source=sidefrog&amp;utm_medium=about" target="_blank" rel="noopener">Pick a time with Mark</a></p>
      <p><a class="text-btn" href="https://www.linkedin.com/in/markflournoy/" target="_blank" rel="noopener">Message me on LinkedIn</a></p>
''',
    extra_ld=[{"@context": "https://schema.org", "@type": "Person", "name": "Mark Flournoy",
               "url": BASE_URL + "/about/", "sameAs": ["https://www.linkedin.com/in/markflournoy/"]}],
)

# ---------------------------------------------------------------- What it costs
PAGES["costs"] = dict(
    path="/what-it-costs/", title="How to Keep Costs Low When You Test a Business Idea | SideFrog",
    h1="Here's how to keep development costs low",
    description="How to test a side hustle idea for about $16: a domain, cheap hosting and cheap AI, with the real monthly bills behind SideFrog.",
    take="Most ideas cost about $16 to try. That's the domain. Everything else is free or close to it, and the bills below are the real ones behind SideFrog.",
    cta=True,
    body='''
      <h2>The short version</h2>
      <p>A new idea costs a domain and an afternoon. Everything behind SideFrog and Mark's other sites costs about $48 a month, and the part that's really for the sites is closer to $8, for Amplify and Gemini. Claude, Google Workspace and Calendly would be there even without the side projects.</p>

      <h2>What SideFrog runs on, and what it costs</h2>
      <p>These are Mark's real bills as of October 2026.</p>
      ''' + table(["What", "What it does", "What it costs"], [
        ["Route 53", "Domains", "$16 a year per .com"],
        ["AWS Amplify", "Hosts the sites, deploys from GitHub, free SSL certificates", "About $4 a month"],
        ["Gemini Flash Lite", "The AI behind most tools, with tight prompts", "About $4 a month"],
        ["AWS Lambda", "Runs the small bits of code behind the tools", "Next to nothing; it only runs when someone uses a tool"],
        ["Claude Pro", "Thinking ideas through and writing the code", "$20 a month, spread across everything Mark builds"],
        ["Google Workspace", "Email on his own domains", "$8 a month"],
        ["Calendly and Google Meet", "Mentoring calls", "$12 a month"],
        ["GitHub", "Where the code lives", "Free"],
        ["Google Analytics, Search Console, Keyword Planner, Ahrefs' free tools", "Seeing who comes and what they searched", "Free"],
        ["Notepad", "Where most of the HTML gets edited", "Free"],
        ["Surface Pro", "The laptop it all happens on", "$1,000, once"],
      ]) + '''

      <h2>What a test site actually needs</h2>
      <p>A domain, one page, a way to collect an email address, and a way to see whether anyone came. Everything else can wait until somebody wants what you're selling.</p>

      <h2>If you're not technical</h2>
      <p>You don't need any of this setup. The same test works with a domain from Porkbun, a one-page site written by SideFrog's “Build the page” prompt (or any simple page builder), and a free Google Form for sign-ups. Same idea, much less setup.</p>

      <h2>What you can skip at first</h2>
      <p>Email marketing software, a logo, ads, and a separate company for each idea. Start paying for those once an idea has customers, not before.</p>
''',
)

# ---------------------------------------------------------------- Build it yourself
GITHUB_SECRETS = ("GitHub: Keeping secrets out of public repositories", "https://github.blog/news-insights/product-news/keeping-secrets-out-of-public-repositories/")
OWASP_LLM = ("Coralogix: OWASP Top 10 for LLM Applications (2025)", "https://coralogix.com/ai-blog/owasp-top-10-for-llm-applications/")

HELP_BOX = '''<div class="help-box">
      <p class="help-box-label">When to get real help</p>
      <p>Some things are worth paying a professional for, even on a side project:</p>
      <ul>
        <li>Taking payments. Use a hosted checkout like Stripe's so card numbers never touch your code.</li>
        <li>Health, financial or other sensitive personal information.</li>
        <li>Logins and passwords. Use a sign-in service instead of building your own.</li>
        <li>Anything aimed at kids.</li>
        <li>Real customers depending on it every day.</li>
      </ul>
      <p>That's where you stop being cheap. If you want a second pair of eyes before you get there, <a href="{cal}" target="_blank" rel="noopener">pick a time with Mark</a> or <a href="https://www.linkedin.com/in/markflournoy/" target="_blank" rel="noopener">message him on LinkedIn</a>.</p>
    </div>'''

PAGES["vibe"] = dict(
    path="/break-room/build/vibe-coding-101/", section="Build it yourself", article=True, numbered=True,
    take_label="Frank has notes",
    title="Vibe Coding 101: Vibe a Site Tonight | SideFrog",
    h1="Vibe coding 101: vibe a site tonight",
    dek="A plain-English guide to getting your weird idea onto the internet before you talk yourself out of it.",
    description="A plain-English guide to getting your weird idea onto the internet before you talk yourself out of it. Eight steps for people who don't code, using AI tools like Claude, ChatGPT or Gemini.",
    take="You don't need to learn to code to build a first version. You need to describe one small thing clearly, change one thing at a time, and save your work when it works. Keep the first version embarrassingly small.",
    body='''
      <p>Vibe coding means describing what you want in plain English and letting an AI tool write the code. It's how SideFrog was built: Claude, Notepad, GitHub and a $16 domain, by someone whose last job was sales. This guide is the version of that process we'd hand a friend.</p>

      <h2>Write the one-sentence version</h2>
      <p>Before you open any AI tool, write one sentence: who it's for, and the one thing it does for them. \u201cA page where dog owners in my building can book a walk for tomorrow.\u201d If you can't write the sentence, the AI can't build it either. It will build something, just not your thing.</p>

      <h2>Brief it like a new contractor</h2>
      <p>The AI is fast and knows nothing about your business. Tell it who uses the page, what they see, what happens when they click, and what it should not do. Paste in real wording and real examples. A good first brief is a few paragraphs, not a few words.</p>
      <p>Then give it your point of view, because if you don't, it fills in the most average one. Say what you believe about the work, how it should feel, a look you like (an old diner menu, a 1970s travel poster, a brand you admire) and one detail only someone in your business would think of. Stripe's head of design, Katie Dill, calls the generic alternative \u201czombie UI\u201d: pages that work but could belong to anyone.</p>
      <p class="aside">Brief it like the contractor who started this morning. Skip the acronyms, and don't assume it read last quarter's deck.</p>

      <h2>Ask for the smallest thing that works</h2>
      <p>Ask for one page in one file, with no logins, no database and no accounts. You can add those later if anyone uses it. SideFrog's \u201cBuild the page\u201d prompt, under every answer, is a ready-made brief for exactly this kind of first version.</p>

      <h2>Change one thing at a time</h2>
      <p>Ask for one change, open the page, check that it worked, then ask for the next. When something breaks, copy the exact error message and paste it back in. \u201cIt doesn't work\u201d gets you guesses; the error message gets you a fix.</p>

      <h2>Use it like a customer before you call it done</h2>
      <p>AI makes things look finished very fast, often before they are. When it works, open it on your phone from a link, the way a customer would, and try to do the one thing it's for without explaining anything to yourself. Does it solve the problem? Where did you hesitate?</p>
      <p>Then ask the AI to critique its own work: \u201cLook at this as a skeptical customer. List the five things that feel generic, confusing or unfinished.\u201d Fix the best few, and go one detail further than you think anyone will notice. SideFrog's \u201cBuild the page\u201d prompt asks for this pass automatically.</p>

      <h2>Save your work when it works</h2>
      <p>GitHub is a free place to keep your files with every version saved. Each save point is called a commit. Make one every time something works, and you can always get back to the last good version when a change goes sideways. It's the undo button you'll wish you had the first time the AI \u201cimproves\u201d something that was fine.</p>

      <h2>Write a handoff before the chat runs out</h2>
      <p>Long chats get slower, start forgetting decisions you made an hour ago, and eventually hit a limit. When that happens mid-project, the next chat starts from zero. A handoff file fixes that: a short note, saved as <code>HANDOFF.md</code> next to your code, that tells a brand-new chat what the project is, what's done and what's next. SideFrog is built this way, one session at a time.</p>
      <p>Write one at the end of every working session, and any time the AI starts repeating old mistakes or forgetting what you agreed. Don't wait for the limit message. Ask for it like this:</p>
      <blockquote class="script">We're wrapping up this session. Write a HANDOFF.md I can paste into a new chat so it can pick up exactly where we left off. Include: what the project is and who it's for, in two sentences; how it's built (files, tools, hosting, where the code lives); what's done and working; what we're in the middle of and the exact next step; decisions we made and why, including anything we tried and dropped; known bugs and loose ends; and the file names, web addresses and setting names I'll need. Never include secret keys or passwords. Keep it short and plain, written for someone who has never seen this chat.</blockquote>
      <p>Save it with your code and commit it, so it lives next to the work it describes. Then start the next chat like this, with the handoff and your current files attached:</p>
      <blockquote class="script">Here's the handoff from my last session and my current files. Read them, tell me in three lines what you understand the project to be and what's next, and wait for me to confirm before changing anything.</blockquote>
      <p>That last line matters. It catches misunderstandings before they turn into changes you have to undo. Update the same file at the end of each session rather than starting a new one.</p>

      <h2>Put it online</h2>
      <p>A simple page can live for free or close to it on hosts like GitHub Pages, Netlify or AWS Amplify (what SideFrog uses), pointed at your domain. Before you share the link with anyone, read <a href="/break-room/build/before-you-put-it-online/">Before you put it on the internet</a>. It's an hour of boring work that saves you from the expensive kind of surprise.</p>
''',
    faq=[
        ("Do I need to learn to code first?", "No. It helps to learn a little as you go, like reading an error message or knowing which file does what, and the AI will explain anything you ask about. Start building and learn what the project needs."),
        ("Which AI tool should I use?", "Any of the big ones can write a first version. Claude, ChatGPT and Gemini all work in a chat window. Tools like Cursor or Claude Code work directly on your files once you're comfortable. Pick one and stick with it for the first project."),
        ("What if it breaks something that used to work?", "Go back to your last commit on GitHub, then ask for the change again in a smaller step. This is the main reason to save often."),
        ("What do I do when I hit the chat limit?", "Start a new chat and paste in your HANDOFF.md and your current files, then ask the AI to tell you what it understands before it changes anything. If you didn't write a handoff in time, paste your files and describe where you were in a few sentences, and write the handoff at the end of this new session."),
        ("Why does my AI-built site look like every other site?", "Because the AI gives you the most likely answer when you don't give it yours. Tell it what you believe about the work, how it should feel, a look you like and one detail only your business would think of, then have it critique the result as a skeptical customer."),
        ("Is code written by AI safe to put online?", "It can be, but don't assume it. AI tools will happily put a secret key where anyone can read it. The next guide covers what to check before you share the link."),
    ],
    related=["secure", "scale", "costs"],
    sources=[],
)

PAGES["secure"] = dict(
    path="/break-room/build/before-you-put-it-online/", section="Build it yourself", article=True,
    take_label="Frank would like a word",
    help_box=True,
    title="Before You Put It on the Internet: Security for First-Time Builders | SideFrog",
    h1="Before you put it on the internet",
    description="The security and cost basics to check before you share a vibe-coded site: secret keys, spending limits, rate limits, user input, privacy and backups.",
    take="Claude can write the code. It can also leave the front door unlocked and not mention it. Before you share the link, spend an hour on the boring stuff below.",
    body='''
      <p>Most of this takes minutes once you know to look. We'll use SideFrog itself as the example, since everything here was checked on this site.</p>
      <p class="aside">You are now the IT department. Unfortunately, nobody approved the headcount.</p>

      <h2>Keep secret keys off the page</h2>
      <p>If your site uses an AI model, a map or a payment service, it has a secret key. Anything in your page's code can be read by anyone who visits, so a key in the page is a public key. Put the call behind a small server function instead, like an AWS Lambda, a Netlify Function or a Cloudflare Worker, and keep the key in that function's settings. SideFrog's Gemini key lives in its Lambda's settings and never reaches the browser.</p>
      <p>Keep keys out of GitHub too. GitHub blocks pushes that contain recognized keys to public repositories by default, and it found over a million leaked secrets on public repositories in the first eight weeks of 2024 alone. If a key ever leaks, delete it and make a new one. Hiding the file afterwards doesn't help.</p>

      <h2>Put a lid on the bill</h2>
      <p>Set a budget alert the day you open a cloud or AI account, so you get an email before a mistake becomes expensive. If your provider lets you set a hard spending limit, set one. Then limit how often one visitor can use the expensive part: SideFrog allows six checks a minute and forty an hour from the same visitor, which is plenty for people and useless for a script.</p>

      <h2>Don't trust what people type</h2>
      <p>Check the length and shape of anything someone types before you use it. If it goes to an AI model, assume someone will try to talk the model into misbehaving. The security group OWASP lists this, called prompt injection, as the top risk for AI apps, and it warns that the hidden instructions you give the model can leak too. Don't put anything in those instructions you'd mind seeing on Reddit, and don't give the model the power to do anything you couldn't undo.</p>

      <h2>Collect less</h2>
      <p>Data you never store can't leak, and you never have to protect it. Skip accounts until you need them, don't log what people type, and make sure your privacy promise matches what the code actually does. SideFrog sends ideas to Gemini to write the answer and stores nothing, so that's what the fine print says.</p>

      <h2>Turn on the free protections</h2>
      <ul>
        <li>Two-factor login on GitHub, your host, your registrar and your AI account.</li>
        <li>HTTPS, which most hosts now turn on for you.</li>
        <li>Security headers, a few lines of host settings that tell browsers to refuse common tricks. Ask your AI tool to write them for your host, then test that the site still works.</li>
        <li>Automatic update alerts for the libraries you use, like GitHub's Dependabot.</li>
      </ul>

      <h2>Keep a way back</h2>
      <p>Your GitHub history is your backup for the code. If the site stores anything people give you, back that up separately and try restoring it once. Turn on auto-renew for your domain, because losing it is the most common way a small site disappears.</p>
''',
    faq=[
        ("My site is tiny. Does any of this matter?", "The bill doesn't care how small the site is. A leaked AI key or an unlimited endpoint can run up charges in an afternoon, and bots find new sites within days."),
        ("How do I know if my key is in my page?", "Open your site, right-click and choose View Page Source, then search for the first few characters of your key. If it's there, everyone can see it. Ask your AI tool to move the call into a server function."),
        ("Do I need a privacy policy?", "If you collect anything about people, including analytics, a short plain-English page saying what you collect and why is the honest minimum. Some laws require more; that's a question for a lawyer if you collect much."),
        ("Can I just ask the AI to make it secure?", "Ask, but check. Have it walk you through this list item by item for your actual site, and test each change yourself."),
    ],
    related=["scale", "vibe", "costs"],
    sources=[GITHUB_SECRETS, OWASP_LLM],
)

PAGES["scale"] = dict(
    path="/break-room/build/six-users-now-what/", section="Build it yourself", article=True,
    take_label="Frank ran the numbers",
    help_box=True,
    title="Six People Use It. Now What? Scaling a Side Project Sensibly | SideFrog",
    h1="Six people use it. Now what?",
    description="What to watch, what to fix and what to ignore when a small vibe-coded project gets its first real users, without rebuilding everything too early.",
    take="Congratulations on the six users. Don't rebuild anything yet. Watch for errors, watch the bill, and let real problems tell you what to fix next.",
    body='''
      <p>The internet is full of advice for running sites with millions of users. You have six, and that's the right number to be thinking about.</p>
      <p class="aside">Six users is not a reason to read about Kubernetes. Please step away from the architecture diagrams.</p>

      <h2>Know when it breaks</h2>
      <p>Set up a free uptime check that emails you if the site goes down, and turn on error alerts from your host or server function. Most small sites don't fail dramatically. Something quietly stops working and nobody tells you, so the goal is to hear about it before your users do.</p>

      <h2>Watch the bill weekly</h2>
      <p>For most AI-powered side projects, the AI calls are the biggest cost. Look at your spending once a week while it's new. If one feature costs more than the rest combined, that's the thing to look at, usually with a shorter prompt, a cheaper model or saving answers you've already paid for. SideFrog runs on about $8 a month for the site itself; <a href="/what-it-costs/">here's the breakdown</a>.</p>

      <h2>Count what matters</h2>
      <p>Free analytics tell you which pages people visit and what they click. Pick the one or two numbers that tell you the idea is working, like sign-ups or completed checks, and ignore the rest for now.</p>

      <h2>Add pieces only when you need them</h2>
      <ul>
        <li><strong>A database,</strong> when the site has to remember something between visits.</li>
        <li><strong>Logins,</strong> when people need their own stuff. Use a sign-in service rather than building it.</li>
        <li><strong>Payments,</strong> when someone wants to pay. Use a hosted checkout.</li>
        <li><strong>More servers,</strong> when your host's own charts say you're running out. On serverless hosting, that's rarely your problem first.</li>
      </ul>

      <h2>Know when to stop vibe coding</h2>
      <p>Vibe coding is great for getting to the first real users. When real money, sensitive data or a lot of customers depend on the site, it's time for someone who does this for a living to look it over.</p>
''',
    faq=[
        ("When does a side project need a real server?", "Usually much later than you think. Serverless functions and static hosting handle thousands of visitors a day without you managing anything. Move when your host tells you you're hitting limits, not before."),
        ("What should I do if it suddenly gets popular?", "Check your bill and your rate limits first, then your error alerts. A sudden spike is often a bot, not a fan club."),
        ("Should I rewrite it properly now that it works?", "Not until something specific hurts. Rewrites eat months. Fix the part that's actually causing trouble."),
    ],
    related=["secure", "vibe", "costs"],
    sources=[],
)


# ---------------------------------------------------------------- Sell it
PAGES["customers"] = dict(
    path="/break-room/sell/first-ten-customers/", section="Sell it", article=True, numbered=True,
    take_label="Frank, off the record",
    title="How to Get Your First 10 Customers for a Side Hustle | SideFrog",
    h1="How to get your first 10 customers",
    description="A plain, honest way to find the first ten paying customers for a side hustle: start with people you know, send short messages, ask clearly, follow up and do the work by hand.",
    take="Your first ten customers will come from messages you send one at a time, mostly to people who already know you or know someone with the problem. Ask plainly, follow up, and do the work by hand for now.",
    body='''
      <p>Almost nobody's first ten customers come from a launch post or an ad. They come from a spreadsheet, a few dozen messages and some follow-up. That's good news if you have a day job, because it fits in coffee breaks.</p>

      <h2>Write down 30 names</h2>
      <p>Former coworkers, neighbors, people from church or the gym, LinkedIn connections, the group chat. You're not going to sell to all of them. You're going to ask them two things: do they have this problem, and do they know someone who does. Most early customers are one introduction away from you.</p>

      <h2>Know exactly who you're looking for</h2>
      <p>\u201cSmall businesses\u201d is too vague to find anyone. \u201cRestaurant owners in my town whose website still lists last year's menu\u201d is a person you could walk in and meet. If you've done <a href="/break-room/start/size-up-the-competition/">Who's already doing it?</a>, you already have this sentence. Then list where those people actually are: a Facebook group, a trade association, a subreddit, a street.</p>
      <p>Describe them by what they believe and what they won't put up with, which tells you more than their income or age. \u201cOwners who refuse to pay an agency $500 to change their hours\u201d is a sharper description than \u201cbusinesses with money.\u201d Use the words they'd use; people notice when something was written by someone who gets it.</p>

      <h2>Send a short, honest message</h2>
      <p>Say who you are, what you're testing, who it's for, and what you're asking for. Keep it short enough to read on a phone. Something like this, in your own words:</p>
      <blockquote class="script">Hi Dana, I'm starting a small side business doing website tune-ups for local restaurants: menus, hours, photos, the stuff that goes stale. I'm taking on my first five clients at a lower price in exchange for honest feedback. Would that be useful for you, or do you know a restaurant owner who'd want it?</blockquote>
      <p>Being upfront that it's new and that you want feedback usually makes people more willing to help. A founding-customer price is fine as long as it's real and you tell them what it'll be later.</p>

      <h2>Follow up, then follow up once more</h2>
      <p>Most people who don't reply are just busy. Send one friendly follow-up a few days later, and one more a week after that. After that, let it go and move on to the next name.</p>
      <p class="aside">If you've ever chased a coworker for a signature on a form, you already have the follow-up skills.</p>

      <h2>Ask for the sale</h2>
      <p>When someone's interested, tell them the price and the next step in plain words. \u201cIt's $150 for the first month. I can start Monday. Want me to send the details?\u201d Then stop talking. If they say no, ask what would have made it a yes, and use the answer to fix the offer.</p>

      <h2>Do the work by hand</h2>
      <p>Deliver the first customers' work yourself, personally, even if you plan to automate it later. You'll learn what they actually care about, which is rarely what you guessed, and you'll get the kind of results that make people tell their friends.</p>
      <p>Before you start, tell them what the first week or two will look like, including the awkward part: the messy first cleanup, the photos that need a second round, the month before results show. When you've said it first, the customer reads it as expected.</p>

      <h2>Turn each customer into the next one</h2>
      <p>After you've delivered, ask three things: \u201cWould you tell me honestly how it went?\u201d, \u201cWhat almost stopped you from buying?\u201d and \u201cDo you know anyone else who'd want this?\u201d The middle answer is the worry your page should answer for the next customer. If they're happy, ask whether you can quote them on your page, using their real words and only with their permission. Keep everyone in one simple spreadsheet: name, how you know them, when you messaged, what they said, and the next step.</p>

      <p>Mark spent his career in sales and mentors salespeople now. If you're stuck on what to say, <a href="https://calendly.com/markflournoy/vibe-code?utm_source=sidefrog&amp;utm_medium=first-ten-customers" target="_blank" rel="noopener">pick a time with him</a>.</p>
''',
    faq=[
        ("Is it okay to sell to friends and family?", "Yes, as long as you're honest about what it is and they'd actually use it. Even better is asking them who they know, since a friend's introduction gets you a stranger's honest answer."),
        ("What if nobody replies?", "Look at your message and your list before you look at the idea. Is the message short, specific and easy to answer? Are you writing to people who really have the problem? Change one thing and send ten more."),
        ("Should I use social media instead?", "Use it to find people and to show your work. Most first sales still happen in a direct conversation, so follow a good post with a message."),
        ("Do I need a website first?", "No, but one simple page helps people take you seriously and gives them something to forward. SideFrog's \u201cBuild the page\u201d prompt makes one quickly; see <a href=\"/break-room/start/test-an-idea-in-a-week/\">Test a side hustle idea in a week</a>."),
        ("What should I charge?", "A real price, close to what you'd charge later, with an honest founding discount if you want one. Free work teaches you less, because people don't tell you the truth about things they didn't pay for. The full walkthrough is in <a href=\"/break-room/sell/what-to-charge/\">What should I charge?</a>"),
    ],
    related=["price", "test", "competition"],
    sources=[],
)


PAGES["price"] = dict(
    path="/break-room/sell/what-to-charge/", section="Sell it", article=True, numbered=True,
    take_label="Frank\u2019s two cents",
    title="What Should I Charge? Pricing a Side Hustle Without Guessing | SideFrog",
    h1="What should I charge?",
    description="A plain way to price a side hustle: check the going rate, work out the lowest price that covers your costs and time, think about what it's worth to the customer, and say the number without apologizing.",
    take="Charge a real price from the start. Check what others charge, make sure the number covers your costs and your time, and say it out loud without apologizing. You can always offer a founding discount, but raising a price you started too low is a much harder conversation.",
    body='''
      <p>Most first-time sellers pick a number that feels polite, which usually means too low. This takes about an hour and gets you a number you can say with a straight face.</p>
      <p class="aside">If you've ever padded a project estimate for your boss, you already understand margin.</p>

      <h2>Find the going rate</h2>
      <p>Look at the list you made in <a href="/break-room/start/size-up-the-competition/">Who's already doing it?</a> and write down what each one charges and how: per job, per hour or per month. Search \u201c[your service] rates [your town]\u201d and ask two or three people who already do this work what's normal. You're looking for a range, from the cheap end to the expensive end.</p>

      <h2>Work out your floor</h2>
      <p>Your floor is the lowest price that's worth your time. Add up what each job costs you (supplies, software, mileage, marketplace and payment fees), then add your hours times the hourly rate you'd actually accept for giving up an evening. Remember that part of what you earn goes to taxes; an accountant can tell you how much to set aside. Don't go below the floor, even for a first customer.</p>

      <h2>Think about what it's worth to them</h2>
      <p>Then look at it from the customer's side: what does the work get them? A restaurant with the wrong hours on its website loses dinner orders every night it stays wrong, so fixing it is worth more to the owner than the three hours it takes you. Price somewhere between your floor and the value you deliver, leaning toward value once you have proof it works.</p>

      <h2>Pick a structure people can understand</h2>
      <p>One clear price beats a menu of options when you're starting. Per job works for one-off work like a website fix or an estate sale. Monthly works for anything ongoing like bookkeeping or dog walking, and it's steadier for you. Hourly is easy to explain but caps what you can earn and makes customers watch the clock, so use it only when the work really can't be predicted.</p>
      <p>How you describe the offer changes what people compare it to. Call it \u201cyour menu, hours and photos kept right all year\u201d and the $175 gets weighed against the dinner orders they lose when those are wrong, instead of against someone else's price.</p>

      <h2>Say the price plainly</h2>
      <p>State the number, what it includes and the next step, then stop. \u201cIt's $175 a month for menu, hours and photo updates. I can start Monday.\u201d No \u201cif that's okay\u201d and no discount before anyone asks. A common rule of thumb: if every single person says yes immediately, you're probably too cheap. If nobody does, check whether you're talking to the right customers before you drop the price.</p>

      <h2>Be honest about founding prices</h2>
      <p>A lower price for your first few customers in exchange for feedback is fair, as long as you tell them up front what the regular price will be and when it starts. Raise prices for new customers first. For existing ones, give real notice and say why.</p>

      <h2 class="unnumbered">An example, with made-up numbers</h2>
      <p>Here's how the math might look for website tune-ups for local restaurants. Your numbers will be different; the point is the order you work them out in.</p>
      ''' + table(["Step", "Example"], [
        ["Hours per restaurant per month", "3"],
        ["The hourly rate you'd accept", "$40, so $120"],
        ["Software and costs per restaurant", "$10"],
        ["Your floor", "$130 a month"],
        ["Going rate you found locally", "$150 to $300 a month"],
        ["Your regular price", "$175 a month"],
        ["Founding price for the first five", "$140 a month, going to $175 after three months"],
      ]) + '''
''',
    faq=[
        ("Should I charge by the hour?", "Only when the work is truly unpredictable. A set price per job or per month is easier for customers to say yes to, and it rewards you for getting faster."),
        ("What if someone says it's too expensive?", "Ask what they were expecting and what they'd compare it to. Sometimes they're the wrong customer. Sometimes you need a smaller version of the offer at a lower price, rather than the same offer for less."),
        ("Should I put my prices on my website?", "For simple services, yes. It saves everyone time and filters out people who were never going to buy. For custom work, a \u201cstarting at\u201d price works well."),
        ("Should I offer a free trial?", "Rarely for a service. People don't tell you the truth about things they didn't pay for. A small paid first job or a founding price teaches you more."),
        ("Should I run discounts?", "Sparingly, and with clear limits. Discounting all the time teaches people to wait for the next one. A founding price for your first few customers, or a sale with a real start and end date, is fine. Keep your main offer at its regular price."),
        ("Should I offer a guarantee?", "If you can stand behind one, yes, and make it specific: what's covered, what isn't, and what happens if they're unhappy. Specific terms show you've thought it through and intend to honor it."),
        ("How often should I raise prices?", "Look at it whenever you're too busy to take new customers, or once or twice a year. Raise for new customers first and give existing ones notice."),
    ],
    related=["customers", "competition", "test"],
    sources=[],
)


# ---------------------------------------------------------------- Make the leap
COBRA_SSA = ("Social Security Administration: COBRA continuation coverage basics", "https://secure.ssa.gov/poms.nsf/lnx/0411080001")
HCGOV_JOB = ("HealthCare.gov: If you lose job-based health insurance", "https://www.healthcare.gov/what-if-i-am-losing-job-based-insurance/")

PAGES["leap"] = dict(
    path="/break-room/leap/before-you-leap/", section="Make the leap", article=True, numbered=True,
    take_label="Frank, speaking as a friend",
    title="Before You Leap: A Safety Net for Leaving Your 9-to-5 | SideFrog",
    h1="Before you leap",
    description="What to line up before you quit a steady job for a side hustle: a cash cushion, what your job quietly pays for, proof the business works, the people it affects, a checkpoint, and leaving on good terms.",
    take="Don't quit on a good week. Build a cushion, find out what your job quietly pays for, let the side hustle prove itself while you still have a paycheck, and leave in a way that lets you walk back in if you need to.",
    body='''
      <p>Leaving a steady job for your own thing is a perfectly good plan, as long as there's a net under it. This is general guidance, not financial advice; a fee-only financial planner can look at your actual numbers.</p>

      <h2>Build the safety net first</h2>
      <p>Add up what you actually spend in a month: housing, food, insurance, debt payments, and the subscriptions you forgot you had. Then multiply. Six months of expenses is a common rule of thumb for a cushion, and many people aim for more when they're leaving a paycheck on purpose, because new businesses usually take longer to pay than their owners expect. Keep it somewhere boring and easy to reach.</p>

      <h2>Price out what your job quietly pays for</h2>
      <p>In the US, health insurance is the big one. You generally have two routes. COBRA lets you keep your employer's plan, usually for up to 18 months, but you pay the whole premium yourself, up to 102% of what the plan costs, which surprises a lot of people. Or you can buy a plan on HealthCare.gov: leaving a job, even quitting, opens a special window to enroll, and you have 60 days after your coverage ends, or can apply up to 60 days before.</p>
      <p>Then list the rest: retirement matching, life and disability insurance, your phone, your laptop, paid training. Add whatever you'll keep paying for to the monthly number from step 1.</p>

      <h2>Let the side hustle prove itself first</h2>
      <p>Pick a \u201cleap number\u201d before you get excited, and write it down. For example: the side hustle covers half your monthly expenses for three months in a row, with more customers lined up. While you still have a paycheck, every month it earns is a month your cushion doesn't have to cover. <a href="/break-room/sell/first-ten-customers/">How to get your first 10 customers</a> and <a href="/break-room/sell/what-to-charge/">What should I charge?</a> are the guides for getting there.</p>

      <h2>Talk to the people it affects</h2>
      <p>A partner, family, anyone who counts on your income. Show them the real numbers, the cushion and the plan, and agree ahead of time on what happens if it's harder than expected. It's also worth an hour with someone who has made the jump themselves; they'll ask the questions you haven't thought of yet.</p>

      <h2>Decide your checkpoint before you jump</h2>
      <p>Write down a date and a number: \u201cIf the business isn't paying $X a month by [date], I start looking for a job.\u201d Share it with the people from step 4. Deciding it now, while you're calm, makes going back part of the plan instead of a decision you have to make on a bad week.</p>

      <h2>Leave well</h2>
      <p>Give the notice your role expects, write a real handoff, thank the people who helped you, and keep your references and contacts warm. Plenty of people go back to a job after running their own thing, sometimes to the same company, and you want that door open.</p>
      <p class="aside">Your exit interview is not the moment to finally share your thoughts on the reorg.</p>
      <p>If you signed anything about competing, inventions or confidentiality, have a lawyer read it before you give notice.</p>
      <p>To put all six steps on paper, print the <a href="/side-kit/leap-worksheet/">Leap Worksheet</a>.</p>
''',
    faq=[
        ("How much money do I really need saved?", "It depends on what you spend, what your health coverage will cost and how quickly the business can pay you. Six months of expenses is a common place to start. A fee-only financial planner can work it out with your actual numbers."),
        ("Should I quit before the side hustle makes any money?", "The safer path is to let it earn first while you're employed. If the business truly can't start until you're full time, plan for a bigger cushion and a firmer checkpoint."),
        ("Can I go part-time instead of quitting?", "It's worth asking. Some employers will agree to reduced hours or a contract arrangement, which keeps some income and sometimes benefits while you build. Check your company's policies first."),
        ("What if it doesn't work out?", "Then your checkpoint does its job: you start looking for work with new skills and a real story to tell. Leaving on good terms makes that much easier."),
    ],
    related=["customers", "price", "test"],
    sources=[COBRA_SSA, HCGOV_JOB],
)


# ---------------------------------------------------------------- Test a big idea small
ASTHO_COTTAGE = ("ASTHO: Do cottage foods really come from a cottage?", "https://www.astho.org/communications/blog/do-cottage-foods-really-come-from-a-cottage/")
NALC_COTTAGE = ("National Agricultural Law Center: Cottage food laws by state", "https://nationalaglawcenter.org/center-projects/cottage-food-laws/")

PAGES["bigsmall"] = dict(
    path="/break-room/start/test-a-big-idea-small/", section="Start", article=True, numbered=True,
    take_label="Frank, between sips",
    title="Test a Big Idea Small: Try a Food Truck or Shop Before You Buy One | SideFrog",
    h1="Test a big idea small",
    description="How to test a food truck, shop or other in-person business before you buy anything big: shrink it to one Saturday, check what your health department requires, rent before you buy, sell where the crowd already is, and count everything.",
    take="Don't buy the truck yet. Sell fifty tacos at someone else's event first, and if people line up, do it again. Start pricing trucks once the line gets long.",
    body='''
      <p>Some ideas can't be tested with a web page. A taco truck, a bakery, a vintage shop or a coffee cart lives or dies on whether people buy the actual thing, in person, at your price. You can find that out for a few hundred dollars before you spend tens of thousands.</p>
      <p class="aside">Think of it as a pilot program. You've sat through enough of those to know how they work.</p>

      <h2>Shrink the dream to one Saturday</h2>
      <p>\u201cTaco truck empire\u201d becomes \u201cone table at one event, selling three kinds of tacos.\u201d Keep the part people would actually come for and drop everything else: the truck, the logo, the second location. If the small version doesn't sell, the big version wouldn't have either, and you found out cheaply.</p>

      <h2>Find out what your city requires before you cook for strangers</h2>
      <p>Call or visit your local health department first. Selling food to the public usually needs a permit, and one-day events often have their own temporary food permit. Every state also has home-kitchen rules (often called cottage food laws), but they vary widely and usually cover only low-risk foods that don't need refrigeration, like baked goods and jams. Foods with meat or dairy, tacos included, almost always need a licensed kitchen. Ask the health department what applies to your exact food; they answer this question every day.</p>

      <h2>Rent before you buy</h2>
      <p>Many towns have shared commercial kitchens you can rent by the hour, and some restaurants rent out their kitchen on days they're closed. Rent or borrow the equipment, too: a tent, a griddle, coolers, a card reader. Your costs for the test should be a booth fee, ingredients and a few hours of kitchen time, not a down payment.</p>

      <h2>Sell where the crowd already is</h2>
      <p>Don't try to build a crowd for your first test. Go where hungry people already gather: a farmers market, a brewery without a kitchen, a school fundraiser, a friend's party, an office that orders lunch for its team. Catering one office lunch is an especially clean test, because you know the order size and get paid up front.</p>

      <h2>Take pre-orders or deposits</h2>
      <p>Before you cook for an event, ask people to order ahead: taco boxes for pickup, a holiday batch of tamales, a catering deposit. Money paid before the food exists is the strongest proof you can get, and it means you don't guess how much to make.</p>

      <h2>Count everything</h2>
      <p>Write down how many you sold, how fast you sold out (if you did), what each plate cost you to make, what people asked for that you didn't have, and who came back for seconds. Decide before the event what a good day looks like, like the \u201cKeep going if\u201d line SideFrog gives with every answer, and compare.</p>

      <h2>Do it again before you scale</h2>
      <p>One good day can be luck, so look for three good days at different events before you call it a pattern. Once you have that and you know your numbers, a used trailer or a regular market spot is a much smaller leap than a new truck, and <a href="/break-room/leap/before-you-leap/">Before you leap</a> covers the rest.</p>
''',
    faq=[
        ("Can I sell food I make at home?", "Sometimes. Every state has home-kitchen rules, but they usually cover only low-risk foods like baked goods and jams, often with limits on where and how much you sell. Anything with meat or dairy usually needs a licensed kitchen. Your local health department can tell you exactly what applies."),
        ("Do I need insurance for a pop-up?", "Many markets and events require vendors to carry liability insurance and will tell you how much. Ask the organizer before you sign up, and check whether short-term event coverage is available."),
        ("What if my idea isn't food?", "The same approach works: a market stall, a pop-up in a friend's shop, a few items on consignment, or pre-orders before you buy inventory. Sell a small batch before you stock a store."),
        ("How much does a food truck cost?", "Enough that you should know your numbers first. Prices vary a lot by size, age and city rules, so get quotes once your test days tell you what you'd actually sell. Leasing or a regular market spot are cheaper ways to grow first."),
    ],
    related=["test", "price", "leap"],
    sources=[ASTHO_COTTAGE, NALC_COTTAGE],
)


# ---------------------------------------------------------------- Where to get honest feedback
REDSHIP_RULES = ("Redship: The complete guide to Reddit self-promotion rules (2026)", "https://redship.io/blog/reddit-self-promotion-rules")

PAGES["feedback"] = dict(
    path="/break-room/start/where-to-get-feedback/", section="Start", article=True, numbered=True,
    take_label="Frank, at the water cooler",
    title="Where to Get Honest Feedback on Your Side Hustle Idea | SideFrog",
    h1="Where to get honest feedback",
    description="Where to ask for honest feedback on a side hustle idea: go where your buyers already talk, not where other founders hang out, read the rules, ask instead of pitching, and count what you hear.",
    take="Ask the people who'd pay. Other founders will happily critique your idea, but they aren't your customers. Go where your buyers already talk, ask a real question, and count the answers.",
    body='''
      <p>Lists of \u201csubreddits to promote your startup\u201d are everywhere, and most of them are communities of other builders. That's useful if you're making an app and want another builder's opinion. It doesn't tell you whether anyone will buy your tacos.</p>
      <p class="aside">Posting a taco idea in a software forum is the office equivalent of asking IT to plan the potluck.</p>

      <h2>Decide whose opinion counts</h2>
      <p>Write down who would actually pay. Your SideFrog result should already give you a good starting point. Feedback from those people matters more than upvotes from everyone else, because they're the ones whose answer should change what you do next.</p>

      <h2>Find where your buyers already talk</h2>
      <p>Go to them instead of asking them to come to you:</p>
      <ul>
        <li><strong>Local services and food:</strong> neighborhood Facebook groups, Nextdoor, your city's subreddit, farmers markets and local events.</li>
        <li><strong>Corporate skills:</strong> LinkedIn, industry groups and people you've worked with.</li>
        <li><strong>Crafts and products:</strong> hobby groups, forums and marketplaces where people already buy and trade that kind of thing.</li>
        <li><strong>Creators:</strong> the audience you already have, even if it's small.</li>
      </ul>
      <p>Don't assume promotion is welcome; read the rules first. A useful question will usually teach you more than an ad anyway.</p>

      <h2>If your idea is an app, try builder communities too</h2>
      <p>For software, other builders can be useful early testers. Places worth checking include:</p>
      <ul>
        <li><strong>r/SideProject</strong> and <strong>r/sideprojects:</strong> sharing side projects and how you built them.</li>
        <li><strong>r/IMadeThis</strong> and <strong>r/buildinpublic:</strong> showing work in progress.</li>
        <li><strong>r/alphaandbetausers:</strong> finding early testers.</li>
        <li><strong>r/webapps:</strong> web apps specifically.</li>
      </ul>
      <p>Use their feedback to improve the product, and don't confuse it with proof that customers will pay.</p>

      <h2>Read the rules before you post</h2>
      <p>Every community has its own rules, they vary widely and they change. Some allow sharing anytime, some have a weekly thread, and some don't allow self-promotion at all. Read the sidebar or group rules before posting, and better yet, spend some time reading and helping other people before you show up with your thing.</p>

      <h2>Ask, don't pitch</h2>
      <p>Start with the problem. Instead of \u201cI built an app that does X. Check it out,\u201d try \u201cHow are you handling X today?\u201d Describe what you're thinking about in a sentence or two, and leave the link out unless the rules allow it or someone asks. End with one question that's easy to answer. The Side Kit has a <a href="/side-kit/#feedback-post">prompt that writes the post</a> from the community's rules.</p>

      <h2>Count what you hear</h2>
      <p>Keep a simple tally:</p>
      <ul>
        <li>How many people replied?</li>
        <li>How many actually have the problem?</li>
        <li>What do they use today?</li>
        <li>Did anyone ask how much it costs?</li>
        <li>Did anyone offer to try it or buy it?</li>
      </ul>
      <p>Then compare it with the \u201cKeep going if\u201d and \u201cRethink it if\u201d lines SideFrog gave you. Twenty upvotes from other founders and no interest from buyers means rethink.</p>
''',
    faq=[
        ("Can I post my idea in r/startups or r/Entrepreneur?", "Check the current rules first. Larger business communities often restrict self-promotion, require particular post formats or put promotional content in designated threads."),
        ("Should I post a link to my landing page?", "Only where the rules allow it. If you're trying to learn rather than promote, asking about the problem usually gets better information than leading with your link."),
        ("What about sites that list new apps?", "Directories and launch sites can bring traffic and early users, which is useful. Traffic is different from evidence that someone will pay, though, so talk to potential buyers too."),
        ("How many responses is enough?", "There's no magic number; you're looking for a pattern. Ten detailed answers from people who actually have the problem can tell you more than hundreds of anonymous upvotes."),
    ],
    related=["customers", "test", "competition"],
    sources=[REDSHIP_RULES],
)


# ---------------------------------------------------------------- Side Kit
def kit_prompt(pid, title, get, watch, text):
    """One copyable prompt: what you'll get, what to watch out for, the prompt, a copy button."""
    return (f'<section class="kit-prompt" id="{pid}"><h3>{html.escape(title)}</h3>'
            f'<p class="kit-meta"><span class="label">You\u2019ll get</span>{get}</p>'
            f'<p class="kit-meta"><span class="label">Watch out</span>{watch}</p>'
            f'<blockquote class="script">{html.escape(text)}</blockquote>'
            f'<button type="button" class="kit-copy" data-copy="{pid}">Copy prompt</button></section>')


SIDE_KIT_BODY = (
    '<p>Copy a prompt, paste it into ChatGPT, Claude or Gemini, and fill in the parts in [brackets]. They\u2019re in the order you\u2019ll probably need them. Any AI can be confidently wrong, especially about local rules and money, so check anything that matters with a real person or an official source.</p>'
    '<h2>Test it</h2>'
    + kit_prompt("pressure-test", "Pressure-test the idea",
        "an honest read on who would pay and why it might not work.",
        "AI tends to be encouraging. The prompt asks it to argue against you on purpose.",
        "Here's my side hustle idea: [your idea]. Act like a skeptical friend who wants me to succeed. Tell me who would pay for this, how often, and what they use or pay for today instead. Then give me the strongest reasons it might not work, and the cheapest way to find out within a week. Don't be encouraging for its own sake.")
    + kit_prompt("small-test", "Plan a small real-world test",
        "a one-day test plan: where to sell, what to make, a small budget and what to ask your city.",
        'AI can be wrong about local permits. Confirm with your health department or city. See <a href="/break-room/start/test-a-big-idea-small/">Test a big idea small</a>.',
        "I want to test [your idea] in person before I buy anything big. I live in [your city or area]. Help me plan one small test: where people who'd buy this already gather, what I should offer and how much to make, what I should ask my local health department or city before I sell, a simple budget for the day, and what result would tell me it's worth doing again. Assume I don't own any equipment yet.")
    + '<h2>Money</h2>'
    + kit_prompt("costs", "Startup costs and break-even",
        "a list of costs as ranges, and how much you'd need to sell each month to cover them.",
        "These are estimates, not quotes and not financial advice. Get real prices before you spend anything.",
        "Help me estimate what it would cost to start [your idea], both one-time costs and monthly costs. Ask me questions before you guess. List each cost as a range and mark the ones you're least sure about. Then show how many [sales, customers or units] a month I'd need at [your price] to cover the monthly costs and pay myself [amount] a month.")
    + kit_prompt("price", "Price it",
        "a regular price, an honest founding price, and the reasoning behind both.",
        'Check it against real competitor prices. See <a href="/break-room/sell/what-to-charge/">What should I charge?</a>',
        "Help me set a price for [what you sell]. Competitors charge: [paste prices you found]. My costs per [job or item] are about [amount], and it takes me about [hours]. Suggest a regular price, a founding price for my first five customers with the date it ends, and a one-line way to describe the offer that makes the value clear. Explain your reasoning briefly.")
    + '<h2>Sell it</h2>'
    + kit_prompt("first-ten", "Write to your first ten customers",
        "a short, honest message to send, and questions that get real answers.",
        "Send it to people one at a time, not as a mass email.",
        "I'm testing [your idea] for [who it's for]. Write a short, honest message I can send to people I know, asking whether they have this problem or know someone who does. Make it clear it's new and I'm looking for feedback, keep it readable on a phone, and don't make it sound like a sales pitch. Then give me five questions to ask people who reply, about how they handle this today and what they've tried or paid for.")
    + kit_prompt("feedback-post", "Write a feedback post that won't get removed",
        "a short post for one community that asks a real question instead of pitching.",
        'Read the community\u2019s rules yourself, too. See <a href="/break-room/start/where-to-get-feedback/">Where to get honest feedback</a>.',
        "I want honest feedback on my side hustle idea from people who might actually pay for it. The idea: [your idea, in a sentence]. I'm posting in: [the group or subreddit], and here are its rules: [paste the rules]. Write a short post that follows those rules exactly. Open with a real question about how people handle [the problem] today, describe my idea in one or two sentences, leave out links unless the rules allow them, and skip hype and fake urgency. End with one specific question that's easy to answer. Then give me three follow-up questions for people who reply, and tell me which kind of answer would mean the idea is worth pursuing.")
    + kit_prompt("reviews", "Read your competitors' bad reviews",
        "the complaints grouped into themes, and the opening they point to.",
        "Use real reviews you copied yourself; don't ask the AI to invent them.",
        "Below are one- to three-star reviews of businesses like the one I want to start: [your idea]. Group the complaints into themes, count how often each comes up, quote one short example for each, and tell me which complaint looks like the best opening for a small new business. Reviews: [paste them here]")
    + '<h2>Build it</h2>'
    + kit_prompt("page", "Build a one-page site",
        "a finished one-page site with a point of view, after the AI asks you five quick questions.",
        "Never let it invent reviews, numbers or credentials. For a version filled in from your idea, run it through SideFrog and use \u201cBuild the page\u201d under the answer.",
        'Design and build a one-page landing page for my business, as a single complete HTML file.\n\nABOUT THE BUSINESS\n- What it is: [your business, in one sentence]\n- Who it\'s for and what they pay: [who pays, and roughly how much]\n- Name: [your business name, or "help me pick one"]\n\nBEFORE YOU BUILD\nAsk me these in one short message, then wait for my answers:\n1. The name (or confirm the one above), and the exact price.\n2. What I believe about this work that others in my field don\'t.\n3. How it should feel, in a few words, and a place, era or brand whose look I like.\n4. The worry that almost stops people from buying, and any real proof I have that answers it (a customer\'s words I\'m allowed to use, a before-and-after, a guarantee).\n5. The link people should land on when they tap the button (a Google Form is fine).\nIf I answer "you choose" to any of these, make a confident, specific choice that fits this business and tell me what you chose.\n\nTHE ONE JOB\nThe page has one job: get the right person to tap one button. Everything on it should help that. Anything that doesn\'t, leave out.\n\nWHAT IT CONTAINS, IN ORDER\n1. A first screen that works on a phone without scrolling: the name, a headline that says plainly what this is and who it\'s for, one supporting sentence, the price, and the button.\n2. A concrete picture of what the customer actually gets, or what happens first, in three short steps or one short paragraph. Specific beats impressive.\n3. The worry, answered directly with my real proof, just above the same button again.\n4. A quiet footer: the name, a way to reach me, and any fine print this business needs.\nNo navigation menu, no feature grid, no wall of FAQs.\n\nHOW IT SHOULD LOOK AND FEEL\n- Design it from this business, not from a template. Someone in this trade should recognize it as theirs.\n- Premium craft: a confident type scale, generous spacing, and a restrained palette taken from the business and the feel I described. You may load one or two Google Fonts.\n- One simple visual drawn in inline SVG or CSS that belongs to this business. No stock photos, icon sets, emoji or gradient hero.\n- Calm, purposeful motion: sections ease in as they scroll into view, and the button responds to a tap. Respect prefers-reduced-motion, and never make anyone wait to read.\n- Mobile first, easy to read on a small phone, good contrast, visible keyboard focus.\n\nHOW IT SHOULD WORK\n- One self-contained file (HTML, CSS and a little JavaScript), no frameworks or build step, fast on a phone.\n- Both buttons open my link in a new tab. If I haven\'t given one, put a clearly marked placeholder at the top of the script.\n- Include a page title, a description and social-sharing tags.\n\nHONESTY\nPlain, specific words, no hype. Never invent testimonials, reviews, customer counts, statistics, credentials or awards. Where proof is missing, leave a clearly marked spot for it.\n\nBEFORE YOU SHOW ME\n1. Read the page as a skeptical customer on a phone, then as a demanding designer. List the five weakest things and fix them.\n2. Ask what\'s on the page because it could be, not because it should be, and remove it.\n3. Give me the finished file, tell me exactly where to paste my link, and explain in two sentences how to put it online for free.')
    + kit_prompt("handoff", "Write the handoff before the chat runs out",
        "a HANDOFF.md that lets a new chat pick up exactly where you left off.",
        'Never include secret keys or passwords. See <a href="/break-room/build/vibe-coding-101/">Vibe coding 101</a>.',
        "We're wrapping up this session. Write a HANDOFF.md I can paste into a new chat so it can pick up exactly where we left off. Include: what the project is and who it's for, in two sentences; how it's built (files, tools, hosting, where the code lives); what's done and working; what we're in the middle of and the exact next step; decisions we made and why, including anything we tried and dropped; known bugs and loose ends; and the file names, web addresses and setting names I'll need. Never include secret keys or passwords. Keep it short and plain, written for someone who has never seen this chat.")
    + '<h2>Leap</h2>'
    + kit_prompt("partner", "Talk it through with your partner",
        "the questions they're likely to ask, and honest answers built from your real numbers.",
        "This is for a conversation, not a pitch. Bring the real numbers, including the scary ones.",
        "I'm thinking about [your plan, e.g. going part-time to build my side business]. Help me prepare to talk it through with [my partner or family]. List the questions they're likely to ask about money, time and risk. Using my real numbers below, help me write honest answers, including what I don't know yet. Suggest a checkpoint date and a number we could agree on for deciding whether to keep going. Don't turn it into a sales pitch. My numbers: [monthly expenses, savings, what the side business earns now]")
    + kit_prompt("leave-well", "Leave well",
        "a notice timeline, a handoff outline for your replacement, and a gracious resignation note.",
        'Check your employment paperwork and company policy first, and never share confidential company information. See <a href="/break-room/leap/before-you-leap/">Before you leap</a>.',
        "Help me plan leaving my job on good terms. My role: [your role]. Help me with: a sensible timeline for giving notice, an outline for a handoff document my replacement could use, a short and gracious resignation note with nothing negative about the company, and a list of people to thank and keep in touch with.")
    + '<h2>Frank for your next meeting</h2>'
    + '<p>Three video-call backgrounds, 1920 by 1080, for Zoom, Teams or Google Meet. Download one and set it as your virtual background: in Zoom, Settings, Backgrounds and effects, then the plus button; in Teams, Video effects, More video effects, Add new; in Google Meet, Apply visual effects, then upload. If the words look backwards to you, that\u2019s only your own mirrored preview; everyone else sees them the right way round.</p>'
    + '<div class="bg-grid">'
    + "".join(f'<figure class="bg-item"><img src="/side-kit/backgrounds/frank-{n}-preview.jpg" alt="{alt}" width="640" height="360" loading="lazy">'
              f'<figcaption><span>{label}</span><a href="/side-kit/backgrounds/frank-{n}.png" download>Download</a></figcaption></figure>'
              for n, label, alt in (("email", "Could have been an email", "A memo from Frank reading: RE this meeting, could have been an email, with Frank sipping coffee in the corner"),
                                    ("desk", "The desk", "The SideFrog masthead with Frank sipping coffee in the corner"),
                                    ("after-hours", "After hours", "The SideFrog masthead on a dark background with Frank sipping coffee in the corner")))
    + '</div>'
    + '<h2>The Leap Worksheet</h2>'
    + '<p>One printable page that turns Frank\u2019s advice into paperwork: your monthly number, your safety net, your leap number, your checkpoint, your first test and your first 30 names. Print it, fill it in, and stick it somewhere you\u2019ll see it. <a href="/side-kit/leap-worksheet/">Open the Leap Worksheet</a>.</p>'
)

PAGES["kit"] = dict(
    path="/side-kit/", title="The Side Kit: Ten AI Prompts for Starting a Side Hustle | SideFrog",
    h1="The Side Kit",
    description="Ten copyable AI prompts for testing, pricing, selling and building a side hustle, in the order you'll need them, plus a printable Leap Worksheet. Free, honest, no hype.",
    take="Ten prompts, in the order you'll need them. Fill in the brackets, paste them into whatever AI you use, and double-check anything that involves money or the law.",
    take_label="From Frank's desk",
    scripts=["/side-kit.js"],
    body=SIDE_KIT_BODY,
)


# ---------------------------------------------------------------- Leap Worksheet (printable)
def ws_line(label, hint=""):
    h = f'<span class="ws-hint">{hint}</span>' if hint else ""
    return f'<div class="ws-line"><span class="ws-label">{label}</span><span class="ws-blank"></span>{h}</div>'


WORKSHEET_BODY = (
    '<p class="ws-intro no-print">Print it, fill it in with a pen, and stick it on the fridge. It\u2019s the advice from <a href="/break-room/leap/before-you-leap/">Before you leap</a>, turned into paperwork. General guidance, not financial advice.</p>'
    '<p class="no-print ws-actions"><button type="button" class="kit-copy" data-print>Print the worksheet</button> <a class="text-btn" href="/side-kit/leap-worksheet.pdf" download>Download the PDF</a></p>'
    '<div class="worksheet">'
    '<p class="ws-form-title">Form SF-1 \u00b7 The Leap Worksheet</p>'
    '<section class="ws-part"><h2>1. My monthly number</h2>'
    + ws_line("What I actually spend in a month: $", "housing, food, insurance, debt payments, subscriptions")
    + '</section><section class="ws-part"><h2>2. What my job quietly pays for</h2>'
    + ws_line("Health insurance on my own, per month: $", "COBRA or a HealthCare.gov plan")
    + ws_line("Other things I\u2019ll start paying for (retirement match, phone, laptop): $")
    + ws_line("My real monthly number (1 + 2): $")
    + '</section><section class="ws-part"><h2>3. My safety net</h2>'
    + ws_line("Months of cushion I want:", "six is a common rule of thumb")
    + ws_line("Months \u00d7 my real monthly number = $")
    + ws_line("Saved so far: $")
    + '</section><section class="ws-part"><h2>4. My leap number</h2>'
    + ws_line("The side hustle earns $", "per month")
    + ws_line("for this many months in a row:")
    + '</section><section class="ws-part"><h2>5. My checkpoint</h2>'
    + ws_line("If the business isn\u2019t paying $", "per month")
    + ws_line("by this date:", "I start looking for a job")
    + ws_line("Agreed with:")
    + '</section><section class="ws-part"><h2>6. My first test</h2>'
    + ws_line("What I\u2019ll sell:")
    + ws_line("Where and when:")
    + ws_line("A good sign would be:")
    + '</section><section class="ws-part ws-names"><h2>7. My first 30 names</h2>'
    + '<ol class="ws-names-list">' + "".join('<li><span class="ws-blank"></span></li>' for _ in range(30)) + '</ol>'
    + '</section><section class="ws-part ws-sign">'
    + ws_line("Signed:") + ws_line("Date:")
    + '<p class="ws-reviewed">Reviewed by Frank.</p>'
    + '</section></div>'
)

PAGES["worksheet"] = dict(
    path="/side-kit/leap-worksheet/", title="The Leap Worksheet: A Printable Plan for Leaving Your 9-to-5 | SideFrog",
    h1="The Leap Worksheet",
    description="A free one-page printable worksheet for leaving a steady job for a side hustle: your monthly number, safety net, leap number, checkpoint, first test and first 30 names.",
    cta=False, scripts=["/side-kit.js"],
    body=WORKSHEET_BODY,
)


# ---------------------------------------------------------------- 404 (not in the sitemap)
NOT_FOUND = dict(
    path="/404.html", title="Page not found | SideFrog", h1="Frank can't find that page", frank_mood="oops",
    description="This page doesn't exist on SideFrog.", cta=False,
    body='''
      <p>It may have moved, or the link had a typo. Frank checked the break room and the supply closet. Nothing.</p>
      <ul class="rows">
        <li><a class="row" href="/"><span class="row-main">Check a side hustle idea</span><span class="row-cue" aria-hidden="true">Go</span></a></li>
        <li><a class="row" href="/break-room/"><span class="row-main">Browse the Break Room guides</span><span class="row-cue" aria-hidden="true">Go</span></a></li>
      </ul>
''',
)


# ---------------------------------------------------------------- Break Room hub
GROUPS = [("Build it yourself", ["vibe", "secure", "scale"]), ("Start here", ["test", "bigsmall", "search", "competition", "feedback"]), ("Name it", ["name", "domain"]), ("Sell it", ["customers", "price"]), ("Get found", ["ai"]), ("Make the leap", ["leap"])]


SKILL_MD = """---
name: test-a-side-hustle-idea
description: Help someone decide whether a side hustle idea is worth testing, and design a cheap one-week test, using SideFrog's method. Use when someone asks whether their business or side hustle idea is any good, or how to test one before spending money.
---

# Test a side hustle idea

SideFrog's method for finding out, in about a week and for about the price of a domain, whether strangers will pay for an idea. From https://sidefrog.com/break-room/start/test-an-idea-in-a-week/

## Before anything is bought

Find out whether a stranger will hand over an email address or a deposit. Friends saying it's a great idea doesn't count.

## The steps

1. **Decide what "yes" looks like first.** Write down two numbers before running anything: the result that means keep going, and the result that means stop (for example: twenty sign-ups from strangers, three deposits, five businesses agreeing to a call). Decide before seeing results, because afterwards every number looks encouraging.
2. **Pick the cheapest real test for the kind of idea.**
   - A service: offer it to five people this week at a real price, and do the work by hand.
   - A physical product: a page with a pre-order or a waitlist. Make nothing until people sign up.
   - Something digital: a one-page sign-up with the price on it. Build only after people ask for it.
   - Something local: a post in the neighborhood group or a flyer on a coffee shop board, with a way to sign up.
3. **Talk to ten people who would actually pay.** Not friends, family or coworkers. Find people who have the problem today and ask how they handle it now, what they've tried and what they've paid for. Don't ask "Would you use this?"; almost everyone says yes to be nice.
4. **Put up one page.** A headline that says what it is, a sentence on who it's for, the price, and one button (a free form that collects an email address is enough). No logo, business cards or company paperwork yet.
5. **Send people to it** in the places found in step 3, with a plain note. Count visits, sign-ups and replies with a question. Questions are a good sign.
6. **Read the result honestly** against the numbers from step 1. Cleared the bar: keep going. Missed badly: that's a cheap answer. In between: change one thing (price, headline or audience), run it once more, then decide.

## How to help

- Be direct about whether the idea looks crowded, risky or promising, and say why in a sentence or two.
- Suggest the single cheapest test that would teach the person the most, with the yes and no numbers to set.
- Don't recommend quitting a job to try an idea. Don't invent statistics. This is general information, not legal, tax or financial advice.
- For a quick verdict, likely buyers and business names with an open .com, the person can use the free checker at https://sidefrog.com/ (no sign-up; ideas aren't stored).

## More from SideFrog

- Is anyone searching for this? https://sidefrog.com/break-room/start/is-anyone-searching-for-this/
- Who's already doing it? https://sidefrog.com/break-room/start/size-up-the-competition/
- What should I charge? https://sidefrog.com/break-room/sell/what-to-charge/
- How to get your first 10 customers: https://sidefrog.com/break-room/sell/first-ten-customers/
"""


# ---------------------------------------------------------------- Stuff I Like
STUFF_BOOKS = [('The Little Red Book of Selling', 'Jeffrey Gitomer', "If you've never sold anything, start here. Short, blunt and easy to finish."), ('Fanatical Prospecting', 'Jeb Blount', 'Finding customers is the part most side hustles skip. This makes it a habit.'), ('Getting to Yes', 'Roger Fisher, William Ury and Bruce Patton', 'For your first price conversation, without turning it into a hostage situation.'), ('How to Say It', 'Rosalie Maggio', "Good when you know what you mean but can't find the words. Handy for that first cold email."), ('The Bezos Blueprint', 'Carmine Gallo', 'Why Amazon writes things down before building them. Writing the one-page version of your idea first works the same way.'), ('Atomic Habits', 'James Clear', 'A side hustle is mostly small, boring things done every evening.'), ('Meditations', 'Marcus Aurelius', 'For the week nobody signs up.')]
STUFF_PODCASTS = [('The Side Hustle Show', 'Nick Loper', 'Real people describing what they started and what it earns. The closest thing to a SideFrog podcast.'), ('Freakonomics Radio', 'Stephen J. Dubner', "Incentives explain why people buy, or don't."), ('Hidden Brain', 'Shankar Vedantam', 'People are weird. Worth remembering before you guess what customers want.'), ('Marketplace', 'American Public Media', 'Twenty-some minutes and you know enough about the economy to sound less surprised.'), ('Pivot', 'Kara Swisher and Scott Galloway', 'Tech and business news, and two people disagreeing about it.'), ('Stuff You Should Know', 'Josh Clark and Chuck Bryant', 'A good break from thinking about your idea.')]
STUFF_SKIP = [('A business course', "It can't tell you whether strangers will pay. A one-week test can."), ('A custom logo', "Your first customers won't ask who designed it."), ('Business cards', "Nobody you're testing with needs one."), ('Ads', 'Wait until you know what to say. Free places where your buyers already talk teach you that.'), ('A second AI subscription', 'One is plenty to start.'), ('A company for each idea', 'Talk to an accountant once money starts coming in, not before.')]


def stuff_body():
    """Mark's short list, in the editorial style: numbered sections, two ruled columns on wider screens."""
    def items(rows):
        return "".join(f'<li><span class="ed-item-title">{html.escape(t)}</span>'
                       + (f'<span class="ed-by">{html.escape(a)}</span>' if a else "")
                       + f'<span class="ed-item-dek">{html.escape(w)}</span></li>' for t, a, w in rows)
    secs = [("Books worth a few evenings", STUFF_BOOKS), ("Podcasts I fall asleep to", STUFF_PODCASTS),
            ("What you don't need yet", [(t, "", w) for t, w in STUFF_SKIP])]
    out = [f'''<div class="ed-frank-note ed-intro-note">{frank_svg("take-frog", "smirk")}
      <div><p class="ed-kicker">A note from Frank</p><blockquote>Reading about businesses is fine. Testing one is better. Pick one book, then go run a test.</blockquote></div></div>''']
    for n, (label, rows) in enumerate(secs, 1):
        out.append(f'<section class="ed-section"><div class="ed-sec-head"><span class="ed-num">{n:02d}</span>'
                   f'<h2 class="ed-kicker">{html.escape(label)}</h2></div><ul class="ed-items">{items(rows)}</ul></section>')
    out.append('<p class="ed-fine">Nobody paid to be here. If a link ever pays me, I\'ll say so next to the link.</p>')
    return "\n".join(out)


PAGES["stuff"] = dict(
    path="/stuff-i-like/", title="Stuff I Like: Books and Podcasts for Starting Something on the Side | SideFrog",
    h1="Stuff I Like", contents=True, kicker_html='<a href="/break-room/">The Break Room</a> · Behind SideFrog',
    dek="Books and podcasts I've actually read and listened to while figuring this out. I haven't tried everything, so if you've found something better, tell me.",
    description="The books and podcasts Mark Flournoy actually uses while testing side hustle ideas, plus the things you don't need to buy yet.",
    body=stuff_body(),
)


# One line per guide, for the Break Room contents page, under each headline and in "Read next".
# Plain and short (about 10 to 15 words); the longer "description" stays for search results.
BLURBS = {
    "vibe": "Get your idea onto the internet tonight with AI tools, no coding required.",
    "secure": "The security and cost checks to run before you share a site you built with AI.",
    "scale": "What to watch, fix and ignore when your first real users show up.",
    "test": "Find out whether strangers will pay before you buy a domain or a logo.",
    "bigsmall": "Shrink a food truck or shop idea down to one Saturday before you spend big.",
    "search": "Use free Google tools to see whether people already look for what you sell.",
    "competition": "Spend an hour on your competitors and find the gap their customers complain about.",
    "feedback": "Ask where your buyers already talk, and count what they actually tell you.",
    "name": "Check registrations, the .com and social handles before you fall for a name.",
    "domain": "Where to buy a .com, what it should cost and which add-ons to skip.",
    "customers": "A plain, honest way to find the first ten people who pay you.",
    "price": "Check the going rate, work out your floor and pick a price you can explain.",
    "ai": "How to show up when people ask ChatGPT or Google's AI instead of searching.",
    "leap": "The savings cushion and health cover to line up before you quit a steady job.",
    "costs": "What it really costs to test an idea, with the bills behind SideFrog.",
    "about": "Who's behind Frank, and what happens to the ideas you type in.",
    "stuff": "The books and podcasts I'd hand a friend, and what you don't need to buy yet.",
}
for _k, _b in BLURBS.items():
    PAGES[_k]["blurb"] = _b
PAGES["about"]["list_title"] = "About SideFrog"     # its headline is a sentence; the contents page wants a name


def read_minutes(p):
    """Reading time from the page's own words, at about 220 a minute."""
    words = len(strip_tags(p.get("body", "") + " " + p.get("take", "")).split())
    words += sum(len(strip_tags(q + " " + a).split()) for q, a in p.get("faq", []))
    return max(2, -(-words // 220))


# Frank on YouTube: newest first. Adding an episode is one line (title as on YouTube, its link).
YOUTUBE_CHANNEL = "https://www.youtube.com/@SideFrogTV"
YOUTUBE_SHORTS = [
    ("Vending machine route: worth it?", "https://www.youtube.com/shorts/uKP8Myic1Ts"),
    ("Automated YouTube channel: worth it?", "https://www.youtube.com/shorts/DAPpYNnV5t8"),
    ("Is TikTok dropshipping still worth it in 2026?", "https://www.youtube.com/shorts/M5FvtyyS9yQ"),
]


def youtube_rail():
    """The Break Room rail: Frank's latest Shorts (no spoilers: the verdict is the payoff)."""
    items = "".join(f'<li><span><a href="{url}">{html.escape(title)}</a><small>Watch Frank’s verdict · 25 seconds</small></span></li>'
                    for title, url in YOUTUBE_SHORTS[:3])
    return (f'''<section class="ed-youtube">
          <p class="ed-kicker">Frank on YouTube</p>
          <p>Frank reviews a side hustle in under 30 seconds.</p>
          <ol class="ed-mini">{items}</ol>
          <p class="ed-more"><a href="{YOUTUBE_CHANNEL}">All episodes on @SideFrogTV</a></p>
        </section>''')


def hub_body():
    """The Break Room as a contents page: numbered sections, numbered guides with a one-line
    description and reading time, and a ruled side rail."""
    groups = GROUPS + [("Behind SideFrog", ["costs", "stuff", "about"])]
    secs = []
    for s, (label, keys) in enumerate(groups, 1):
        items = "".join(
            f'<li><a href="{PAGES[k]["path"]}"><span class="n">{n:02d}</span>'
            f'<span class="ed-item-title">{html.escape(PAGES[k].get("list_title", PAGES[k]["h1"]))}</span>'
            f'<span class="ed-item-dek">{html.escape(PAGES[k].get("blurb", ""))}</span>'
            f'<span class="ed-meta">{read_minutes(PAGES[k])} min read</span></a></li>'
            for n, k in enumerate(keys, 1))
        secs.append(f'<section class="ed-section"><div class="ed-sec-head"><span class="ed-num">{s:02d}</span>'
                    f'<h2 class="ed-kicker">{html.escape(label)}</h2></div><ol class="ed-list">{items}</ol></section>')
    starts = "".join(f'<li><span><a href="{PAGES[k]["path"]}">{html.escape(PAGES[k]["h1"])}</a>'
                     f'<small>{read_minutes(PAGES[k])} min read</small></span></li>' for k in ("test", "competition", "price"))
    return f'''<div class="ed-grid">
      <div class="ed-main">{"".join(secs)}</div>
      <aside class="ed-rail">
        <section><p class="ed-kicker">New here? Start with</p><ol class="ed-mini">{starts}</ol></section>
        {youtube_rail()}
        <section class="ed-check">
          <span class="frank-portrait"><span class="frank is-round can-sip" data-mood="smirk" data-look="you"></span></span>
          <p class="ed-kicker">Got an idea?</p>
          <p>Frank gives you a straight verdict, who'd pay and a cheap first test in seconds.</p>
          <a class="plate-btn" href="/">Check an idea</a>
        </section>
      </aside>
    </div>'''


PAGES["hub"] = dict(
    path="/break-room/", title="The Break Room: Guides for Testing a Side Hustle Idea | SideFrog",
    h1="Short guides for coffee breaks.", contents=True,
    dek=f"{sum(len(k) for _, k in GROUPS)} plain guides for testing an idea before you spend real money on it.",
    description="Short, plain guides for testing a side hustle idea: demand, competition, naming, domains and getting found by Google and AI answers.",
    body=hub_body(),
)


def main():
    for key, p in PAGES.items():
        out = ROOT / p["path"].strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(stamp(relative(page_html(p), p["path"])), encoding="utf-8")
        print("built", p["path"])

    # lastmod = when a page's content last changed (its "updated" field), not
    # when the site was rebuilt. Bump a page's "updated" when you edit its copy.
    urls = [("/", HOME_UPDATED)] + [(p["path"], p.get("updated", CHECKED_ISO)) for p in PAGES.values()]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{BASE_URL}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
        + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")

    lines = ["# SideFrog", "",
             "> SideFrog: free advice from a frog with no stake in your idea. A free side hustle idea checker: type an idea and get a straight verdict, who would pay, a first test to run, related searches and business names with an open .com, checked live. Built by Mark Flournoy. SideFrog doesn't store the ideas people type.", "",
             "## Tool", f"- [Check an idea]({BASE_URL}/): the idea checker", "",
             "## Guides"]
    for label, keys in GROUPS:
        for k in keys:
            lines.append(f"- [{PAGES[k]['h1']}]({BASE_URL}{PAGES[k]['path']}): {PAGES[k]['description']}")
    lines += ["", "## About", f"- [About SideFrog]({BASE_URL}/about/): {PAGES['about']['description']}",
              f"- [What it costs]({BASE_URL}/what-it-costs/): {PAGES['costs']['description']}", ""]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    print("built sitemap.xml, robots.txt, llms.txt")

    # 404 page: served for any address that doesn't exist, at any depth, so its
    # links stay root-relative (/styles.css) instead of being made relative.
    nf = page_html(NOT_FOUND).replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n  <meta name="theme-color"')
    nf = nf.replace("<h1>", frank_svg("nf-frog", "oops") + "<h1>", 1)      # Frank's error face, above the headline
    (ROOT / "404.html").write_text(stamp(nf), encoding="utf-8")

    # Amplify rewrites and redirects: /about -> /about/ (301) for every page,
    # then anything that doesn't exist -> /404.html with a real 404 status.
    # www always goes to the bare domain (first, so it wins before anything else):
    # the home page, then any path, keeping the path.
    host = BASE_URL.split("://", 1)[1]
    rules = [{"source": f"https://www.{host}", "target": f"https://{host}", "status": "301", "condition": None},
             {"source": f"https://www.{host}/<*>", "target": f"https://{host}/<*>", "status": "301", "condition": None}]
    rules += [{"source": p["path"].rstrip("/"), "target": p["path"], "status": "301", "condition": None}
              for p in PAGES.values()]
    rules.append({"source": "/verdict", "target": "/verdict/", "status": "301", "condition": None})   # shared verdict links
    # /.well-known/ is skipped by zip deploys, so serve the AI-discovery manifest from the root there
    rules += [{"source": f"/.well-known/{n}", "target": f"/{n}", "status": "200", "condition": None}
              for n in ("ard.json", "ai-catalog.json")]
    rules.append({"source": "/<*>", "target": "/404.html", "status": "404", "condition": None})
    (ROOT / "amplify-redirects.json").write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")
    print(f"built 404.html and amplify-redirects.json ({len(rules)} rules)")

    # Agentic Resource Discovery manifest (AI Catalog spec 1.0): the envelope is exactly
    # specVersion, host and entries. Entries are resources agents can use, not web pages
    # (those stay findable through llms.txt and the sitemap). SideFrog publishes one agent
    # skill: its method for deciding whether an idea is worth testing and designing a cheap
    # test. The idea-check API is deliberately not advertised to agents (it costs money per call).
    host = BASE_URL.split("://", 1)[1]
    updated = CHECKED_ISO + "T00:00:00Z"
    skill_path = "/skills/test-a-side-hustle-idea/SKILL.md"
    (ROOT / skill_path.strip("/")).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / skill_path.strip("/")).write_text(SKILL_MD, encoding="utf-8")
    manifest = {
        "specVersion": "1.0",
        "host": {"displayName": "SideFrog", "identifier": f"did:web:{host}", "documentationUrl": BASE_URL + "/about/"},
        "entries": [{
            "identifier": f"urn:air:{host}:skill:test-a-side-hustle-idea",
            "displayName": "Test a side hustle idea",
            "type": 'text/markdown; profile="urn:air:agent-skills"',
            "url": BASE_URL + skill_path,
            "description": "Help someone decide whether a side hustle idea is worth testing, then design a cheap one-week test: set the yes and no numbers first, pick the cheapest real test, talk to ten likely buyers, put up one page, and read the result honestly.",
            "tags": ["side hustle", "small business", "idea validation", "customer discovery"],
            "updatedAt": updated,
        }],
    }
    # Written to the site root: Amplify's zip deploys skip dot-folders like .well-known.
    # amplify-redirects.json rewrites /.well-known/ard.json and /.well-known/ai-catalog.json
    # to these files (status 200), so tools that only look there still find them.
    for name in ("ard.json", "ai-catalog.json"):
        (ROOT / name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("built ard.json and ai-catalog.json (served at /.well-known/ too, via rewrites)")

    # The tool page (index.html) is hand-written, but its footer comes from the
    # same template, and its asset links get the same fingerprints.
    idx = ROOT / "index.html"
    doc = idx.read_text(encoding="utf-8")
    doc = re.sub(r'<footer class="site-footer">.*?</footer>', lambda _: relative(FOOTER, "/"), doc, count=1, flags=re.S)
    # the home page preloads the same self-hosted Bricolage (no Google Fonts)
    google_re = r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">'
    preload_re = r'<link rel="preload" href="fonts/bricolage\.[0-9a-f]+\.woff2" as="font" type="font/woff2" crossorigin>'
    if SELF_HOST_FONTS:
        doc = re.sub(google_re, lambda _: f'<link rel="preload" href="fonts/{FONT_FILES["bricolage"]}" as="font" type="font/woff2" crossorigin>', doc)
        doc = re.sub(r'(<link rel="preload" href=")fonts/bricolage\.[0-9a-f]+\.woff2', lambda mm: f'{mm.group(1)}fonts/{FONT_FILES["bricolage"]}', doc)
    else:
        doc = re.sub(preload_re, lambda _: GOOGLE_FONTS.replace('><', '>\n  <'), doc)
    v = fingerprint("og/home.jpg")
    doc = re.sub(r'(content="https://[^"]+/og/home\.jpg)(?:\?v=[0-9a-f]+)?"', lambda mm: f'{mm.group(1)}?v={v}"', doc)
    doc = doc.replace('og:image:width" content="1200"', 'og:image:width" content="2400"').replace('og:image:height" content="630"', 'og:image:height" content="1260"')
    idx.write_text(stamp(doc), encoding="utf-8")
    print("updated index.html (footer, asset fingerprints)")

    # Shared verdict links go to /verdict/#v=... : the same page, but with its own share card.
    # The idea lives after the # (never sent anywhere), so link previews can't show the real
    # verdict; this card says "Frank's verdict is in" instead of the home card's sample verdict.
    vdoc = stamp(doc)
    vdoc = re.sub(r'(\s(?:href|src)=")(?!https?:|/|#|mailto:|data:|tel:|\.\./)', r'\1../', vdoc)   # one folder down
    vt = "Frank's verdict is in | SideFrog"
    vd = "Someone shared Frank's verdict on their side hustle idea. Tap to see what he thought, then check your own idea for free."
    vimg = f"{BASE_URL}/og/verdict.jpg?v={fingerprint('og/verdict.jpg')}"
    vdoc = re.sub(r"<title>.*?</title>", f"<title>{html.escape(vt)}</title>", vdoc, count=1)
    vdoc = re.sub(r'(<meta name="description" content=")[^"]*', lambda mm: mm.group(1) + html.escape(vd), vdoc, count=1)
    vdoc = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda mm: mm.group(1) + html.escape(vt), vdoc, count=1)
    vdoc = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda mm: mm.group(1) + html.escape(vd), vdoc, count=1)
    vdoc = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda mm: mm.group(1) + f"{BASE_URL}/verdict/", vdoc, count=1)
    vdoc = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*', lambda mm: mm.group(1) + vimg, vdoc)
    vdoc = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda mm: mm.group(1) + "Frank's verdict is in. Tap to see what he thought of this idea.", vdoc, count=1)
    vdoc = vdoc.replace('<link rel="canonical" href="https://sidefrog.com/">', '<link rel="canonical" href="https://sidefrog.com/">\n  <meta name="robots" content="noindex, follow">', 1)
    (ROOT / "verdict").mkdir(exist_ok=True)
    (ROOT / "verdict" / "index.html").write_text(vdoc, encoding="utf-8")
    print("wrote verdict/index.html (shared verdicts: same page, its own share card)")


if __name__ == "__main__":
    main()
