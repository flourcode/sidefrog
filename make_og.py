#!/usr/bin/env python3
"""Render SideFrog's share cards (1200x630, for Facebook, LinkedIn, X, iMessage, Slack).

    pip install playwright && python3 -m playwright install chromium
    python3 make_og.py

Writes og/home.jpg and one og/<slug>.jpg per page in make_pages.PAGES (plus the
printable side-kit/leap-worksheet.pdf), using the
site's own font, colours and Frank. Titles come from make_pages.py, so rerun this
after changing a page title. Then rerun make_pages.py (it links each page's card).
"""
import asyncio
import html
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
import make_pages  # noqa: E402

FONT_URL = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&display=swap"
FROGS = (ROOT / "frogs").as_uri()

INK, PAPER, CARD, RULE, ACCENT = "#1F241F", "#FBF7EF", "#FFFDF9", "#A89B84", "#A4501F"


import frank_art
_uid = [0]


def frank(mood="smirk", look="right"):
    """The masthead logo: cutout Frank looking at you, like the site's logo."""
    return frank_art.cutout(frank_art.FRAME["you"])


def round_frank(mood="you", bg="cream"):
    """Round Frank for share cards and backgrounds (identity and sharing)."""
    _uid[0] += 1
    return frank_art.round_svg(frank_art.FRAME.get(mood, 12), bg=bg, uid=f"og{_uid[0]}")


BASE_CSS = f"""
* {{ box-sizing: border-box; margin: 0; }}
html, body {{ width: 1200px; height: 630px; }}
body {{ background: {PAPER}; color: {INK}; font-family: "Bricolage Grotesque", system-ui, sans-serif; position: relative; overflow: hidden; }}
.frame {{ position: absolute; inset: 36px; border-top: 3px solid {INK}; }}
.brand {{ position: absolute; left: 64px; top: 62px; display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 34px; letter-spacing: -0.03em; }}
.brand svg {{ width: 62px; }}
.tagline {{ position: absolute; right: 64px; top: 66px; text-align: right; font-size: 20px; line-height: 1.3; color: #5A5A4A; }}
.url {{ position: absolute; left: 64px; bottom: 54px; font-size: 24px; font-weight: 700; color: {INK}; }}
"""


def home_card():
    return f"""<!doctype html><html><head><meta charset="utf-8"><link href="{FONT_URL}" rel="stylesheet"><style>{BASE_CSS}
h1 {{ position: absolute; left: 64px; top: 150px; width: 560px; font-size: 64px; line-height: 1.02; letter-spacing: -0.04em; font-weight: 800; }}
.lede {{ position: absolute; left: 64px; top: 400px; width: 540px; font-size: 27px; line-height: 1.35; color: #5A5A4A; }}
.card {{ position: absolute; right: 56px; top: 150px; width: 500px; background: {CARD}; border: 3px solid {INK}; border-radius: 22px; box-shadow: 8px 8px 0 {INK}; padding: 26px 28px 28px; }}
.memo {{ font-size: 20px; line-height: 1.5; color: #5A5A4A; width: 300px; border-bottom: 1.5px solid {RULE}; padding-bottom: 8px; }}
.memo b {{ color: {ACCENT}; letter-spacing: 0.08em; }}
.memo {{ width: auto; }}
.vrow {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; margin-top: 24px; }}
.verdict {{ margin: 0; font-size: 46px; font-weight: 800; letter-spacing: -0.035em; line-height: 1; text-transform: uppercase; }}
.vrow svg {{ flex: none; width: 124px; height: 124px; margin-top: -14px; }}   /* his eyes level with the verdict's first line */
.reason {{ margin-top: 16px; font-size: 22px; line-height: 1.4; }}
</style></head><body>
<div class="frame"></div>
<div class="brand">{frank()}SideFrog</div>
<div class="tagline">For people who<br>hate Mondays.</div>
<h1>Thinking about making the leap from your 9-to-5?</h1>
<p class="lede">Type an idea. Find out if it has legs.</p>
<div class="card">
  <p class="memo"><b>FROM:</b> Frank<br><b>RE:</b> meal prep for pet turtles</p>
  <div class="vrow"><p class="verdict">Keep your<br>day job</p>{round_frank("meh", "cream")}</div>
  <p class="reason">Niche is far too small, and perishable logistics will eat your margin.</p>
</div>
<div class="url">sidefrog.com</div>
</body></html>"""


def page_card(p):
    path = p["path"]
    if p.get("take"):
        label = p.get("take_label", "A note from Frank")
    elif path.startswith("/side-kit/"):
        label = "The Side Kit"
    elif path == "/about/":
        label = "Made by Mark"
    elif path == "/verdict/":
        label = "Shared with you"
    elif path == "/stuff-i-like/":
        label = "Behind SideFrog"
    else:
        label = "The Break Room"
    if path.startswith("/break-room/"):
        where = "From the Break Room. Short guides for coffee breaks."
    elif path.startswith("/side-kit/"):
        where = "From the Side Kit. Prompts and a printable worksheet."
    elif path == "/verdict/":
        where = "Free idea checks. No sign-up."
    else:
        where = "Made by Mark Flournoy. Free, no sign-up."
    title = html.escape(p["h1"])
    size = 74 if len(p["h1"]) <= 28 else 62 if len(p["h1"]) <= 44 else 54
    return f"""<!doctype html><html><head><meta charset="utf-8"><link href="{FONT_URL}" rel="stylesheet"><style>{BASE_CSS}
.label {{ position: absolute; left: 64px; top: 168px; font-size: 22px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #4A5C34; }}
h1 {{ position: absolute; left: 64px; top: 210px; width: 720px; font-size: {size}px; line-height: 1.04; letter-spacing: -0.04em; font-weight: 800; text-wrap: balance; }}
.big {{ position: absolute; right: 70px; bottom: 60px; width: 330px; }}
.big svg {{ display: block; width: 100%; height: auto; }}
.dek {{ position: absolute; left: 64px; top: 380px; width: 680px; font-size: 27px; line-height: 1.35; color: #5A5A4A; margin: 0; }}
.where {{ position: absolute; left: 64px; bottom: 96px; font-size: 22px; color: #5A5A4A; }}
</style></head><body>
<div class="frame"></div>
<div class="brand">{frank()}SideFrog</div>
<div class="tagline">For people who<br>hate Mondays.</div>
<p class="label">{html.escape(label)}</p>
<h1>{title}</h1>{f'<p class="dek">{html.escape(p["dek"])}</p>' if p.get("dek") else ""}
<p class="where">{html.escape(where)}</p>
<div class="big">{round_frank("you", "cream")}</div>
<div class="url">sidefrog.com</div>
</body></html>"""


def background(kind):
    """1920x1080 video-call backgrounds. The middle stays clear: that's where the person sits."""
    dark = kind == "after-hours"
    bg, ink, muted = (INK, PAPER, "#C9C2B2") if dark else (PAPER, INK, "#5A5A4A")
    if kind == "email":
        body = f"""<div class="memo"><p class="row"><b>FROM:</b> Frank</p><p class="row"><b>RE:</b> this meeting</p>
            <p class="v">COULD HAVE BEEN<br>AN EMAIL</p></div>
          <div class="frog-big left">{round_frank("meh", "sage")}</div>
          <p class="url right">sidefrog.com</p>"""
    else:
        body = f"""<div class="mast">{frank()}<span>SideFrog</span></div><div class="mast-rule"></div>
          <div class="frog-big right">{round_frank("you", "cream" if dark else "sage")}</div>
          <p class="tag left">For people who<br>hate Mondays.</p>
          <p class="url left2">sidefrog.com</p>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><link href="{FONT_URL}" rel="stylesheet"><style>
* {{ box-sizing: border-box; margin: 0; }}
html, body {{ width: 1920px; height: 1080px; }}
body {{ background: {bg}; color: {ink}; font-family: "Bricolage Grotesque", system-ui, sans-serif; position: relative; overflow: hidden; }}
.memo {{ position: absolute; right: 110px; top: 110px; width: 640px; background: {CARD}; color: {INK}; border: 4px solid {INK}; border-radius: 30px; box-shadow: 14px 14px 0 {INK}; padding: 40px 44px 44px; }}
.memo .row {{ font-size: 30px; line-height: 1.5; color: #5A5A4A; }}
.memo .row b {{ color: {ACCENT}; letter-spacing: 0.08em; }}
.memo .v {{ margin-top: 22px; padding-top: 22px; border-top: 2px solid {RULE}; font-size: 62px; white-space: nowrap; font-weight: 800; line-height: 0.98; letter-spacing: -0.035em; }}
.frog-big {{ position: absolute; bottom: 90px; width: 400px; }}
.frog-big.left {{ left: 90px; }} .frog-big.right {{ right: 110px; }}
.frog-big svg {{ display: block; width: 100%; height: auto; }}
.mast {{ position: absolute; left: 110px; top: 86px; display: flex; align-items: center; gap: 18px; font-weight: 800; font-size: 52px; letter-spacing: -0.03em; }}
.mast svg {{ width: 92px; }}
.mast-rule {{ position: absolute; left: 110px; right: 110px; top: 196px; height: 4px; background: {ink}; }}
.tag {{ position: absolute; left: 110px; bottom: 150px; font-size: 32px; line-height: 1.35; color: {muted}; }}
.url {{ position: absolute; font-size: 44px; font-weight: 800; letter-spacing: -0.03em; }}
.url.right {{ right: 110px; bottom: 70px; }} .url.left2 {{ left: 110px; bottom: 80px; }}
</style></head><body>{body}</body></html>"""


def slug(path):
    return path.strip("/").split("/")[-1] or "home"


async def main(font_file=None):
    from playwright.async_api import async_playwright
    out = ROOT / "og"
    out.mkdir(exist_ok=True)
    jobs = [("home", home_card())] + [(slug(p["path"]), page_card(p)) for p in make_pages.PAGES.values()]
    # shared verdict links (/verdict/#v=...): no sample verdict, since the preview can't know the real one
    jobs.append(("verdict", page_card(dict(path="/verdict/", h1="Frank's verdict is in",
                                           dek="Tap to see what he thought of this idea, then check your own."))))
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        # Rendered at 2x (2400x1260, the same 1.91:1 shape) so text stays crisp after
        # LinkedIn and others shrink and re-compress it, and on high-resolution screens.
        page = await browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=2)
        if font_file:  # offline: serve the font from disk instead of Google
            data = pathlib.Path(font_file).read_bytes()
            await page.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css",
                body="@font-face{font-family:'Bricolage Grotesque';src:url(https://fonts.gstatic.com/b.ttf);font-weight:200 800}"))
            await page.route("https://fonts.gstatic.com/**", lambda r: r.fulfill(status=200, content_type="font/ttf", body=data))
        tmp = ROOT / "og" / "_card.html"
        for name, doc in jobs:
            tmp.write_text(doc, encoding="utf-8")
            await page.goto(tmp.as_uri())
            await page.evaluate("document.fonts.ready")
            await page.wait_for_timeout(150)
            png = await page.screenshot(type="png")
            from PIL import Image
            import io
            Image.open(io.BytesIO(png)).convert("RGB").save(out / f"{name}.jpg", quality=90, subsampling=0, optimize=True, progressive=True)   # 4:4:4 keeps small coloured text sharp
            print("og/" + name + ".jpg")
        # Video-call backgrounds (1920x1080) and small previews for the Side Kit
        bgdir = ROOT / "side-kit" / "backgrounds"
        bgdir.mkdir(parents=True, exist_ok=True)
        bgpage = await browser.new_page(viewport={"width": 1920, "height": 1080})
        if font_file:
            await bgpage.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css",
                body="@font-face{font-family:'Bricolage Grotesque';src:url(https://fonts.gstatic.com/b.ttf);font-weight:200 800}"))
            await bgpage.route("https://fonts.gstatic.com/**", lambda r: r.fulfill(status=200, content_type="font/ttf", body=data))
        from PIL import Image
        import io
        for name in ("email", "desk", "after-hours"):
            tmp.write_text(background(name), encoding="utf-8")
            await bgpage.goto(tmp.as_uri())
            await bgpage.evaluate("document.fonts.ready")
            await bgpage.wait_for_timeout(150)
            png = await bgpage.screenshot(type="png")
            im = Image.open(io.BytesIO(png)).convert("RGB")
            im.save(bgdir / f"frank-{name}.png", optimize=True)
            im.resize((640, 360), Image.LANCZOS).save(bgdir / f"frank-{name}-preview.jpg", quality=84, optimize=True)
            print(f"side-kit/backgrounds/frank-{name}.png")
        tmp.unlink()

        # The Leap Worksheet as a PDF, printed with the page's own print styles
        ws = ROOT / "side-kit" / "leap-worksheet" / "index.html"
        if ws.exists():
            await page.goto(ws.as_uri())
            await page.evaluate("document.fonts.ready")
            await page.emulate_media(media="print")
            await page.pdf(path=str(ROOT / "side-kit" / "leap-worksheet.pdf"), format="Letter", print_background=False,
                           margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"})
            print("side-kit/leap-worksheet.pdf")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else None))
