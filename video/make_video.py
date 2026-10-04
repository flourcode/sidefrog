#!/usr/bin/env python3
"""Render a short SideFrog demo video for LinkedIn (1080x1350, 4:5, 30 fps, 10 s). It opens and
closes on the same end card (SideFrog.com), so it loops seamlessly and its first frame makes
a good default thumbnail; the end card is also saved as sidefrog-demo-thumbnail.png.

    pip install playwright numpy && python3 -m playwright install chromium   (ffmpeg on PATH)
    python3 video/make_video.py [path/to/Bricolage.ttf]

It loads the real home page (index.html, styles.css, Frank's layers) at phone width,
blocks the page's own scripts, and drives everything from one function of time,
scene(t): the headline, typing an idea, pressing the button, Frank's sip (the site's
own CSS animation, seeked frame by frame), the verdict and an end card. Every frame
is deterministic. A quiet soundtrack (key ticks, a click, a stamp, a chime) is
synthesized with numpy, since LinkedIn plays videos muted until tapped and the words
on screen carry the message anyway.

Edit the copy in SCENE below and run it again.
"""
import asyncio
import pathlib
import shutil
import subprocess
import sys
import wave

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "video"
FPS, SECONDS = 30, 10.0
INTRO = 1.0                          # opens on the end card, which slides away: first frame = last frame, so it loops
LEAD = INTRO - 0.35                  # the page timeline starts while the card is still lifting, so there's no dead air
W, H, SCALE = 432, 540, 2.5        # phone layout; 432x540 CSS pixels at 2.5x = 1080x1350 video

SCENE = {
    "idea": "taco truck empire",
    "verdict": "This could work",
    "reason": "Real demand, but trucks are expensive. Prove the tacos first.",
    "facts": [("Try this first", "Sell 50 tacos at one weekend market."),
              ("Good sign", "You sell out before 1pm.")],
    "url": "SideFrog.com",
    "tagline": "Free advice from a frog with no stake in your idea.",
    "small": "Free. No sign-up. Your idea isn\u2019t saved.",
}

# Timing (seconds)
T_TYPE, T_TYPED = 1.25, 2.75        # typing the idea
T_PRESS = 2.95                       # button press
T_SCROLL0, T_SCROLL1 = 3.15, 3.85    # page scrolls to Frank's card
T_ANSWER = 5.35                      # verdict lands
T_END = 7.25                         # end card

SCENE_JS = r"""
(() => {
  const S = __SCENE__;
  const $ = (q) => document.querySelector(q);
  const clamp = (x) => Math.max(0, Math.min(1, x));
  const ease = (x) => { x = clamp(x); return x < .5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3) / 2; };
  const back = (x) => { x = clamp(x); const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };

  // --- one-time setup on the real page ---
  document.documentElement.style.scrollBehavior = "auto";
  document.body.style.overflow = "hidden";
  // keep the masthead pinned, and show nothing after Frank's card
  const hdr = $(".site-header");
  hdr.style.cssText += ";position:sticky;top:0;z-index:20;background:var(--paper)";
  let sib = $("#example").nextElementSibling;
  while (sib) { sib.style.display = "none"; sib = sib.nextElementSibling; }
  document.querySelector("footer")?.style.setProperty("display", "none");
  const h1 = $("main h1");
  h1.innerHTML = h1.textContent.trim().split(/\s+/).map(w => `<span class="w" style="display:inline-block">${w}</span>`).join(" ");
  const words = [...h1.querySelectorAll(".w")];
  const lede = $(".lede"), plate = $(".plate"), btn = $("#idea-btn");
  const ta = $("#idea-input");
  ta.setAttribute("placeholder", "");
  const caret = document.createElement("style");
  caret.textContent = `.plate-input{caret-color:transparent} .vid-caret{display:inline-block;width:3px;height:1.05em;background:var(--ink);vertical-align:-0.12em;margin-left:2px}`;
  document.head.append(caret);
  // a div that looks like the textarea, so the caret can sit after the text
  const typed = document.createElement("div");
  typed.className = ta.className;
  const cs = getComputedStyle(ta);
  typed.style.cssText = `min-height:${cs.height};font:${cs.font};letter-spacing:${cs.letterSpacing};line-height:${cs.lineHeight};padding:${cs.padding};color:var(--ink)`;
  ta.replaceWith(typed);
  const ex = $("#example");
  ex.querySelector(".example-tag")?.remove();
  ex.querySelector(".example-foot")?.remove();
  ex.querySelector(".you-wrote").innerHTML = `<span class="memo-row"><span class="re">FROM: </span>Frank</span><span class="memo-row"><span class="re">RE: </span>${S.idea}</span>`;
  ex.querySelector(".verdict:not(.loading-verdict) .verdict-text").textContent = S.verdict;
  ex.querySelector(".reason").textContent = S.reason;
  const dl = document.createElement("dl"); dl.className = "facts"; dl.style.marginTop = "1rem";
  S.facts.forEach(([k, v]) => { dl.insertAdjacentHTML("beforeend", `<div class="fact"><dt>${k}</dt><dd>${v}</dd></div>`); });
  ex.append(dl);
  const facts = [...dl.children];
  const frog = ex.querySelector(".sticker-frog") || ex.querySelector(".frog");
  // the example card only carries the faces the site needs; add the smirk ("This could work")
  if (!frog.querySelector(".face-smirk")) {
    const mug = frog.querySelector(".mug");
    mug.insertAdjacentHTML("beforebegin", S.smirk);
  }
  // the end card
  const end = document.createElement("div");
  end.innerHTML = `<div class="end-inner">
      <div class="end-frog">${frog.outerHTML}</div>
      <p class="end-url">${S.url}</p>
      <p class="end-tag">${S.tagline}</p>
      <p class="end-small">${S.small}</p></div>`;
  end.style.cssText = "position:fixed;inset:0;background:var(--paper);display:flex;align-items:center;justify-content:center;z-index:50;";
  const st = document.createElement("style");
  st.textContent = `.end-inner{text-align:center;padding:0 28px}
    .end-frog svg{width:190px;height:auto;display:block;margin:0 auto 18px}
    .end-url{font-size:52px;font-weight:800;letter-spacing:-0.035em;margin:0;color:var(--ink)}
    .end-tag{font-size:21px;line-height:1.35;margin:12px auto 0;max-width:22ch;color:var(--muted)}
    .end-small{font-size:15px;font-weight:600;margin:22px 0 0;color:var(--deep)}
    .end-inner > *{will-change:transform,opacity}`;
  document.head.append(st);
  document.body.append(end);
  const endFrog = end.querySelector("svg"); endFrog.setAttribute("data-mood", "smirk");
  const endParts = [...end.querySelectorAll(".end-inner > *")];
  const scrollTarget = () => Math.max(0, ex.getBoundingClientRect().top + window.scrollY - hdr.offsetHeight - 18);
  let target = null;

  const inner = (t) => {
    // headline: words rise in, one after another
    words.forEach((w, i) => { const p = ease((t - 0.05 - i * 0.07) / 0.45); w.style.opacity = p; w.style.transform = `translateY(${(1 - p) * 26}px)`; });
    const lp = ease((t - 0.6) / 0.4); lede.style.opacity = lp; lede.style.transform = `translateY(${(1 - lp) * 12}px)`;
    const pp = ease((t - 0.75) / 0.45); plate.style.opacity = pp; plate.style.transform = `translateY(${(1 - pp) * 18}px)`;
    // typing, then the caret blinks while waiting
    const n = Math.round(clamp((t - __T_TYPE__) / (__T_TYPED__ - __T_TYPE__)) * S.idea.length);
    const caretOn = t < __T_PRESS__ && (t < __T_TYPED__ || Math.floor(t * 2.4) % 2 === 0) && t > 1.0;
    typed.innerHTML = S.idea.slice(0, n) + (caretOn ? '<span class="vid-caret"></span>' : "");
    // button press
    const press = t >= __T_PRESS__ && t < __T_PRESS__ + 0.16;
    btn.style.transform = press ? "translate(4px,4px)" : "";
    btn.style.boxShadow = press ? "0 0 0 var(--ink)" : "";
    // the card appears only after the button press, rising in as the page scrolls
    const cp = ease((t - __T_PRESS__ - 0.1) / 0.5);
    ex.style.opacity = cp; ex.style.transform = `translateY(${(1 - cp) * 40}px)`;
    // card: thinking until the answer lands
    const loading = t < __T_ANSWER__;
    ex.classList.toggle("is-loading", loading);
    frog.setAttribute("data-mood", loading ? "smirk" : "smirk");
    // scroll to the card
    if (target === null) target = scrollTarget();
    window.scrollTo(0, target * ease((t - __T_SCROLL0__) / (__T_SCROLL1__ - __T_SCROLL0__)));
    // Frank's real sip animation, seeked to this moment
    // (thinking sip loops from the press; after the answer, the site's 1.5 s landing sip plays from the answer)
    const since = loading ? (t - __T_PRESS__) * 1000 + 700 : (t - __T_ANSWER__) * 1000;
    for (const a of document.getAnimations({ subtree: true })) { a.pause(); a.currentTime = Math.max(0, since); }
    // verdict stamps in, then the facts
    const v = ex.querySelector(".verdict:not(.loading-verdict)");
    if (!loading) {
      const s = back((t - __T_ANSWER__) / 0.32);
      v.style.transform = `scale(${1.35 - 0.35 * s})`; v.style.transformOrigin = "left center"; v.style.opacity = clamp((t - __T_ANSWER__) / 0.12);
      const r = ex.querySelector(".reason"); const rp = ease((t - __T_ANSWER__ - 0.3) / 0.35); r.style.opacity = rp; r.style.transform = `translateY(${(1 - rp) * 10}px)`;
      facts.forEach((f, i) => { const fp = ease((t - __T_ANSWER__ - 0.65 - i * 0.28) / 0.35); f.style.opacity = fp; f.style.transform = `translateY(${(1 - fp) * 10}px)`; });
    }
    // end card slides up
    const ep = ease((t - __T_END__) / 0.5);
    end.style.transform = `translateY(${(1 - ep) * 100}%)`;
    endParts.forEach((p, i) => { const q = ease((t - __T_END__ - 0.25 - i * 0.12) / 0.4); p.style.opacity = q; p.style.transform = `translateY(${(1 - q) * 14}px)`; });
  };
  // Intro: the video opens on the finished end card (so it starts as it ends and loops),
  // holds a beat, then the card slides up and away to reveal the page.
  window.scene = (t) => {
    inner(Math.max(0, t - __LEAD__));
    if (t < __INTRO__) {
      const x = ease((t - (__INTRO__ - 0.45)) / 0.45);
      end.style.transform = `translateY(${-x * 100}%)`;
      endParts.forEach((p) => { p.style.opacity = 1; p.style.transform = "none"; });
    }
  };
})();
"""


def build_js():
    import json
    sys.path.insert(0, str(ROOT))
    import make_pages                      # Frank's faces live in the build script
    scene = dict(SCENE, smirk=make_pages.FACES["smirk"])
    js = SCENE_JS.replace("__SCENE__", json.dumps(scene))
    for k, v in {"__T_TYPE__": T_TYPE, "__T_TYPED__": T_TYPED, "__T_PRESS__": T_PRESS,
                 "__T_SCROLL0__": T_SCROLL0, "__T_SCROLL1__": T_SCROLL1,
                 "__T_ANSWER__": T_ANSWER, "__T_END__": T_END, "__INTRO__": INTRO, "__LEAD__": LEAD}.items():
        js = js.replace(k, str(v))
    return js


async def render_frames(frames_dir, font_file=None):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        # the page's own scripts would rotate examples and trigger idle sips: block them
        await page.route("**/*.js*", lambda r: r.abort())
        if font_file:
            data = pathlib.Path(font_file).read_bytes()
            await page.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css",
                body="@font-face{font-family:'Bricolage Grotesque';src:url(https://fonts.gstatic.com/b.ttf);font-weight:200 800}"))
            await page.route("https://fonts.gstatic.com/**", lambda r: r.fulfill(status=200, content_type="font/ttf", body=data))
        await page.goto((ROOT / "index.html").as_uri())
        await page.evaluate("document.fonts.ready")
        await page.evaluate(build_js())
        # let every Frank layer (including the end card's copy) load before frame one
        await page.evaluate("scene(0)")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(600)
        total = int(FPS * SECONDS)
        for i in range(total):
            await page.evaluate(f"scene({i / FPS})")
            await page.screenshot(path=str(frames_dir / f"f{i:04d}.png"))
        await browser.close()
    return total


def soundtrack(path):
    sr = 44100
    n = int(sr * SECONDS)
    out = np.zeros(n)
    rng = np.random.default_rng(7)

    def add(t0, sig, gain, shift=True):
        i = int((t0 + (LEAD if shift else 0)) * sr)
        j = min(n, i + len(sig))
        out[i:j] += sig[: j - i] * gain

    def env(length, attack=0.002, decay=0.05):
        t = np.arange(int(length * sr)) / sr
        return np.minimum(1, t / attack) * np.exp(-t / decay)

    # the opening card lifting away
    noise = rng.standard_normal(int(0.45 * sr))
    add(INTRO - 0.45, np.convolve(noise, np.ones(30) / 30, "same") * np.sin(np.linspace(0, np.pi, len(noise))), 0.06, shift=False)
    # soft key ticks while typing
    keys = len(SCENE["idea"])
    for k in range(keys):
        t0 = T_TYPE + (T_TYPED - T_TYPE) * (k + 0.5) / keys
        noise = rng.standard_normal(int(0.03 * sr))
        add(t0, np.convolve(noise, np.ones(6) / 6, "same") * env(0.03, decay=0.008), 0.06)
    # button click
    t = np.arange(int(0.06 * sr)) / sr
    add(T_PRESS, np.sin(2 * np.pi * 1400 * t) * env(0.06, decay=0.012), 0.25)
    # a soft "sip" whoosh while Frank thinks
    noise = rng.standard_normal(int(0.9 * sr))
    whoosh = np.convolve(noise, np.ones(40) / 40, "same") * np.sin(np.linspace(0, np.pi, len(noise)))
    add(T_PRESS + 1.25, whoosh, 0.08)
    # verdict stamp: a low thump
    t = np.arange(int(0.25 * sr)) / sr
    add(T_ANSWER, np.sin(2 * np.pi * (90 - 40 * t) * t) * env(0.25, decay=0.07), 0.5)
    # end chime: two warm notes
    for f0, dt in ((660, 0.0), (880, 0.14)):
        t = np.arange(int(1.2 * sr)) / sr
        tone = (np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * 2 * f0 * t)) * env(1.2, attack=0.005, decay=0.35)
        add(T_END + 0.35 + dt, tone, 0.12)
    out = out / max(1e-9, np.abs(out).max()) * 0.7
    fade = int(0.3 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


def main():
    font = sys.argv[1] if len(sys.argv) > 1 else None
    import tempfile
    work = pathlib.Path(tempfile.mkdtemp(prefix="sidefrog-video-"))   # frames on local disk, not the output folder
    frames = work / "frames"
    frames.mkdir()
    total = asyncio.run(render_frames(frames, font))
    wav = work / "sound.wav"
    soundtrack(wav)
    mp4 = OUT / "sidefrog-demo.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%04d.png"),
                    "-i", str(wav), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(mp4)], check=True)
    shutil.copy(frames / f"f{total - 1:04d}.png", OUT / "sidefrog-demo-thumbnail.png")   # the end card, for a custom thumbnail
    shutil.rmtree(work)
    print(f"{mp4} ({total} frames, {SECONDS:.0f}s)")


if __name__ == "__main__":
    main()
