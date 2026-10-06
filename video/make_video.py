#!/usr/bin/env python3
"""Render a short SideFrog video for LinkedIn (1080x1350, 4:5, 30 fps, 9.6 s): "the meeting".
A calendar memo for meeting 1 of 6, "Meanwhile...", then a real check of "taco truck empire"
on the site, Frank's verdict with its cheap test, and an open .com (with a cash register).
It opens and closes on the same end card (SideFrog.com), so it loops seamlessly and its first
frame makes a good default thumbnail; the end card is also saved as sidefrog-demo-thumbnail.png.

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
FPS, SECONDS = 30, 9.6
INTRO = 0.8                          # opens on the end card, which slides away: first frame = last frame, so it loops
LEAD = INTRO                         # the page timeline starts once the opening card has lifted
W, H, SCALE = 432, 540, 2.5        # phone layout; 432x540 CSS pixels at 2.5x = 1080x1350 video

SCENE = {
    "memo_from": "Your calendar",
    "memo_re": "Q3 alignment sync",
    "memo_big": "Meeting 1 of 6",
    "memo_line": "Agenda: TBD.",
    "meanwhile": "Meanwhile\u2026",
    "idea": "taco truck empire",
    "thinking": "This is a coffee break, not Shark Tank.",
    "verdict": "This could work",
    "reason": "One location is a business, an empire is just a logistical migraine.",
    "facts": [("Cheap test", "Rent commercial kitchen hours and book a spot at a weekend market or local event.", "fact-lead"),
              ("Keep going if", "you sell out your entire inventory before the market closes", "fact-signal"),
              ("Rethink it if", "you sell fewer than 30 tacos in a four-hour market", "fact-signal")],
    "name": ("TacoRoute", "tacoroute.com"),
    "url": "SideFrog.com",
    "tagline": "For people who hate Mondays.",
    "small": "Half-baked is fine. Your idea isn\u2019t saved.",
}

# Timing on the page timeline (seconds after the opening card has lifted, i.e. after INTRO)
T_MEMO_IN, T_MEANWHILE, T_MEMO_OUT = 0.0, 0.9, 1.55   # the calendar memo
T_TYPE, T_TYPED = 1.75, 2.45                            # typing the idea
T_PRESS = 2.6                                           # button press
T_SCROLL0, T_SCROLL1 = 2.75, 3.25                       # page scrolls to Frank's card
T_ANSWER = 4.0                                          # verdict stamps in
T_NAMES0, T_NAMES1 = 5.4, 5.85                          # scroll down to the open name
T_KACHING = 5.95                                        # the name lights up
T_END = 6.6                                             # end card

SCENE_JS = r"""
(() => {
  const S = __SCENE__;
  const $ = (q) => document.querySelector(q);
  const clamp = (x) => Math.max(0, Math.min(1, x));
  const ease = (x) => { x = clamp(x); return x < .5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3) / 2; };
  const back = (x) => { x = clamp(x); const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };

  // --- the real page, set up for filming
  document.documentElement.style.scrollBehavior = "auto";
  document.body.style.overflow = "hidden";
  const hdr = $(".site-header");
  hdr.style.cssText += ";position:sticky;top:0;z-index:20;background:var(--paper)";
  let sib = $("#example").nextElementSibling;
  while (sib) { sib.style.display = "none"; sib = sib.nextElementSibling; }
  document.querySelector("footer")?.style.setProperty("display", "none");
  const btn = $("#idea-btn"), ta = $("#idea-input");
  const cs = getComputedStyle(ta);
  const typed = document.createElement("div");
  typed.className = ta.className;
  typed.style.cssText = `min-height:${cs.height};font:${cs.font};letter-spacing:${cs.letterSpacing};line-height:${cs.lineHeight};padding:${cs.padding};color:var(--ink)`;
  ta.replaceWith(typed);
  const st = document.createElement("style");
  st.textContent = `.vid-caret{display:inline-block;width:3px;height:1.05em;background:var(--ink);vertical-align:-0.12em;margin-left:2px}
    .vid-memo{position:fixed;inset:0;z-index:40;background:var(--paper);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 26px}
    .vid-memo .result{width:100%;max-width:400px;margin:0;padding:26px 26px 24px}
    .vid-memo .you-wrote{font-size:20px;line-height:1.45}
    .vid-memo .verdict{font-size:44px;line-height:1;margin-top:14px;white-space:nowrap}
    .vid-memo .reason{font-size:22px;color:var(--muted);margin-top:10px}
    .vid-meanwhile{margin-top:34px;font-size:40px;font-weight:800;letter-spacing:-0.035em;color:var(--ink)}
    .vid-names{margin-top:1.2rem;padding-top:1rem;border-top:1px solid var(--rule)}
    .vid-names h3{margin:0 0 .6rem}
    .vid-names .row{transition:none}
    .end-inner{text-align:center;padding:0 28px}
    .end-frog .frank-portrait{float:none;width:200px;height:200px;margin:0 auto 18px}
    .end-url{font-size:52px;font-weight:800;letter-spacing:-0.035em;margin:0;color:var(--ink)}
    .end-tag{font-size:21px;line-height:1.35;margin:12px auto 0;max-width:22ch;color:var(--muted)}
    .end-small{font-size:15px;font-weight:600;margin:22px 0 0;color:var(--deep)}`;
  document.head.append(st);

  // --- Frank's card: this answer, thinking first
  const ex = $("#example");
  ex.querySelector(".example-tag")?.remove();
  ex.querySelector(".example-foot")?.remove();
  ex.setAttribute("data-verdict", "worth_a_shot");
  ex.querySelector(".you-wrote").innerHTML = `<span class="memo-row"><span class="re">FROM: </span>Frank</span><span class="memo-row"><span class="re">RE: </span>${S.idea}</span>`;
  ex.querySelector(".verdict:not(.loading-verdict) .verdict-text").textContent = S.verdict;
  ex.querySelector(".reason").textContent = S.reason;
  ex.querySelector(".loading-note").textContent = S.thinking;
  const dl = document.createElement("dl"); dl.className = "facts";
  S.facts.forEach(([k, v, role]) => dl.insertAdjacentHTML("beforeend", `<div class="${role}"><dt>${k}</dt><dd>${v}</dd></div>`));
  ex.append(dl);
  const facts = [...dl.children];
  const names = document.createElement("div"); names.className = "vid-names part";
  names.innerHTML = `<h3>Names with an open .com</h3><ul class="rows"><li><a class="row"><span class="row-main"><span class="name-word">${S.name[0]}</span><span class="name-domain">${S.name[1]}</span></span><span class="row-cue">Register \u2197</span></a></li></ul>`;
  ex.append(names);
  const nameRow = names.querySelector(".row");
  const frog = ex.querySelector(".frank");
  frog.setAttribute("data-mood", "smirk");
  // the timeline sets Frank's frames itself, so no random idle sips sneak into a frame
  document.querySelectorAll(".can-sip").forEach((f) => f.classList.remove("can-sip"));

  // --- the calendar memo, in the same memo style as Frank's card
  const memo = document.createElement("div"); memo.className = "vid-memo";
  memo.innerHTML = `<section class="result"><div class="card-head" style="display:block">
      <p class="you-wrote"><span class="memo-row"><span class="re">FROM: </span>${S.memo_from}</span><span class="memo-row"><span class="re">RE: </span>${S.memo_re}</span></p>
      <p class="verdict"><span class="verdict-text">${S.memo_big}</span></p>
      <p class="reason">${S.memo_line}</p></div></section>
    <p class="vid-meanwhile">${S.meanwhile}</p>`;
  document.body.append(memo);
  const memoCard = memo.querySelector(".result"), meanwhile = memo.querySelector(".vid-meanwhile");

  // --- the end card
  const end = document.createElement("div");
  end.innerHTML = `<div class="end-inner"><div class="end-frog"><span class="frank-portrait"><span class="frank is-round" data-mood="smirk" data-look="you"></span></span></div>
      <p class="end-url">${S.url}</p><p class="end-tag">${S.tagline}</p><p class="end-small">${S.small}</p></div>`;
  end.style.cssText = "position:fixed;inset:0;background:var(--paper);display:flex;align-items:center;justify-content:center;z-index:50;";
  document.body.append(end);
  const endParts = [...end.querySelectorAll(".end-inner > *")];

  const cardTarget = () => Math.max(0, ex.getBoundingClientRect().top + window.scrollY - hdr.offsetHeight - 14);
  const namesTarget = () => Math.max(0, nameRow.getBoundingClientRect().bottom + window.scrollY - window.innerHeight + 26);
  let t1 = null, t2 = null;

  const inner = (t) => {
    // the memo drops in, "Meanwhile..." appears, then the memo lifts away
    const mi = back((t - __T_MEMO_IN__) / 0.4);
    memoCard.style.transform = `translateY(${(1 - mi) * -40}px)`; memoCard.style.opacity = clamp((t - __T_MEMO_IN__) / 0.15);
    const mw = ease((t - __T_MEANWHILE__) / 0.3); meanwhile.style.opacity = mw; meanwhile.style.transform = `translateY(${(1 - mw) * 10}px)`;
    memo.style.transform = `translateY(${-ease((t - __T_MEMO_OUT__) / 0.35) * 100}%)`;
    // typing, then the button
    const n = Math.round(clamp((t - __T_TYPE__) / (__T_TYPED__ - __T_TYPE__)) * S.idea.length);
    const caretOn = t < __T_PRESS__ && t > __T_MEMO_OUT__ + 0.2 && (t < __T_TYPED__ || Math.floor(t * 2.4) % 2 === 0);
    typed.innerHTML = S.idea.slice(0, n) + (caretOn ? '<span class="vid-caret"></span>' : "");
    const press = t >= __T_PRESS__ && t < __T_PRESS__ + 0.16;
    btn.style.transform = press ? "translate(4px,4px)" : ""; btn.style.boxShadow = press ? "0 0 0 var(--ink)" : "";
    // Frank's card rises in, thinking (with the Shark Tank line) until the answer stamps in
    const cp = ease((t - __T_PRESS__ - 0.1) / 0.45);
    ex.style.opacity = cp; ex.style.transform = `translateY(${(1 - cp) * 40}px)`;
    const loading = t < __T_ANSWER__;
    ex.classList.toggle("is-loading", loading);
    // while he thinks, Frank sips the card's way (eyes on the verdict): lift, sip over the mug, lower
    const ms = (t - __T_PRESS__) * 1000 - 250;
    const cyc = ms % 2000;
    const sipFrame = loading && ms > 0 ? (cyc < 200 ? 5 : cyc < 1150 ? 6 : cyc < 1350 ? 5 : null) : null;
    if (sipFrame === null) frog.style.removeProperty("--frame"); else frog.style.setProperty("--frame", sipFrame);
    if (t1 === null) t1 = cardTarget();
    let y = t1 * ease((t - __T_SCROLL0__) / (__T_SCROLL1__ - __T_SCROLL0__));
    if (!loading) { if (t2 === null) t2 = Math.max(t1, namesTarget()); y += (t2 - t1) * ease((t - __T_NAMES0__) / (__T_NAMES1__ - __T_NAMES0__)); }
    window.scrollTo(0, y);
    const since = loading ? (t - __T_PRESS__) * 1000 + 700 : (t - __T_ANSWER__) * 1000;
    for (const a of document.getAnimations({ subtree: true })) { a.pause(); a.currentTime = Math.max(0, since); }
    // the verdict stamps in; the cheap test and its pass/fail pair follow
    const v = ex.querySelector(".verdict:not(.loading-verdict)");
    if (!loading) {
      const s2 = back((t - __T_ANSWER__) / 0.3);
      v.style.transform = `scale(${1.35 - 0.35 * s2})`; v.style.transformOrigin = "left center"; v.style.opacity = clamp((t - __T_ANSWER__) / 0.1);
      const r = ex.querySelector(".reason"); const rp = ease((t - __T_ANSWER__ - 0.25) / 0.3); r.style.opacity = rp;
      facts.forEach((f, i) => { const fp = ease((t - __T_ANSWER__ - 0.5 - i * 0.22) / 0.3); f.style.opacity = fp; f.style.transform = `translateY(${(1 - fp) * 10}px)`; });
      const np = ease((t - __T_ANSWER__ - 1.1) / 0.3); names.style.opacity = np;
    } else { names.style.opacity = 0; }
    // ka-ching: the open name lights up
    const k = clamp((t - __T_KACHING__) / 0.12);
    nameRow.style.background = k > 0 ? `color-mix(in srgb, var(--frog) ${Math.round(28 * k)}%, var(--surface))` : "";
    nameRow.style.transform = k > 0 && k < 1 ? "scale(1.03)" : "";
    // the end card slides back up
    const ep = ease((t - __T_END__) / 0.45);
    end.style.transform = `translateY(${(1 - ep) * 100}%)`;
    endParts.forEach((p, i) => { const q = ease((t - __T_END__ - 0.2 - i * 0.1) / 0.35); p.style.opacity = q; p.style.transform = `translateY(${(1 - q) * 14}px)`; });
  };
  // Opens on the finished end card (so it loops), which lifts away to the calendar memo.
  window.scene = (t) => {
    inner(Math.max(0, t - __LEAD__));
    if (t < __INTRO__) {
      const x = ease((t - (__INTRO__ - 0.4)) / 0.4);
      end.style.transform = `translateY(${-x * 100}%)`;
      endParts.forEach((p) => { p.style.opacity = 1; p.style.transform = "none"; });
    }
  };
})();
"""


def build_js():
    import json
    sys.path.insert(0, str(ROOT))
    scene = dict(SCENE)
    js = SCENE_JS.replace("__SCENE__", json.dumps(scene))
    for k, v in {"__T_MEMO_IN__": T_MEMO_IN, "__T_MEANWHILE__": T_MEANWHILE, "__T_MEMO_OUT__": T_MEMO_OUT,
                 "__T_TYPE__": T_TYPE, "__T_TYPED__": T_TYPED, "__T_PRESS__": T_PRESS,
                 "__T_SCROLL0__": T_SCROLL0, "__T_SCROLL1__": T_SCROLL1, "__T_ANSWER__": T_ANSWER,
                 "__T_NAMES0__": T_NAMES0, "__T_NAMES1__": T_NAMES1, "__T_KACHING__": T_KACHING,
                 "__T_END__": T_END, "__INTRO__": INTRO, "__LEAD__": LEAD}.items():
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
    """Office sounds only, no music: a whoosh as the opening card lifts, a paper thump as the
    memo lands and a softer whoosh as it lifts away, key clicks, the button, a quiet sip while
    Frank drinks, a rubber stamp on the verdict, a cash register when an open .com shows up,
    and a whoosh as the end card slides up."""
    sr = 44100
    n = int(sr * SECONDS)
    out = np.zeros(n)
    rng = np.random.default_rng(7)

    def add(t0, sig, gain, shift=True):
        i = int((t0 + (LEAD if shift else 0)) * sr)
        j = min(n, i + len(sig))
        if i < n:
            out[i:j] += sig[: j - i] * gain

    def env(length, attack=0.002, decay=0.05):
        t = np.arange(int(length * sr)) / sr
        return np.minimum(1, t / attack) * np.exp(-t / decay)

    def noise(length, smooth):
        x = rng.standard_normal(int(length * sr))
        return np.convolve(x, np.ones(smooth) / smooth, "same")

    # the opening card lifting away
    w = noise(0.4, 30); add(INTRO - 0.4, w * np.sin(np.linspace(0, np.pi, len(w))), 0.05, shift=False)
    # the memo landing: a soft paper thump
    t = np.arange(int(0.18 * sr)) / sr
    add(T_MEMO_IN + 0.08, (np.sin(2 * np.pi * 70 * t) * 0.6 + noise(0.18, 12)[: len(t)] * 0.5) * env(0.18, decay=0.04), 0.35)
    # the memo lifting away: a short, soft paper whoosh
    w = noise(0.3, 40); add(T_MEMO_OUT, w * np.sin(np.linspace(0, np.pi, len(w))) ** 2, 0.06)
    # keyboard clicks, slightly uneven like real typing
    keys = len(SCENE["idea"])
    for k in range(keys):
        t0 = T_TYPE + (T_TYPED - T_TYPE) * (k + 0.5) / keys + rng.uniform(-0.012, 0.012)
        click = noise(0.025, 3) * env(0.025, decay=0.005)
        add(t0, click, 0.16)
    # the button
    t = np.arange(int(0.05 * sr)) / sr
    add(T_PRESS, np.sin(2 * np.pi * 1300 * t) * env(0.05, decay=0.01), 0.22)
    # Frank's sip: two short, airy slurps while the mug is at his mouth
    for k, t0 in enumerate((T_PRESS + 0.62, T_PRESS + 0.98)):
        L = 0.26; t = np.arange(int(L * sr)) / sr
        air = noise(L, 6)[: len(t)] - noise(L, 40)[: len(t)]           # breathy, band-limited
        shape = np.sin(np.pi * np.clip(t / L, 0, 1)) ** 1.5
        add(t0, air * shape * (1 + 0.5 * np.sin(2 * np.pi * 9 * t)), 0.10 if k == 0 else 0.07)
    # the rubber stamp: a low thud with a little paper slap
    t = np.arange(int(0.22 * sr)) / sr
    thud = np.sin(2 * np.pi * (95 - 45 * t) * t) * env(0.22, decay=0.06)
    slap = noise(0.22, 4)[: len(t)] * env(0.22, decay=0.012)
    add(T_ANSWER, thud * 0.8 + slap * 0.5, 0.55)
    # the cash register: a drawer clunk, then the bell
    t = np.arange(int(0.12 * sr)) / sr
    add(T_KACHING - 0.05, (np.sin(2 * np.pi * 140 * t) * 0.5 + noise(0.12, 6)[: len(t)] * 0.6) * env(0.12, decay=0.03), 0.3)
    t = np.arange(int(1.1 * sr)) / sr
    bell = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((2093, 1.0), (2637, 0.6), (3136, 0.35), (4186, 0.2))) * env(1.1, attack=0.002, decay=0.28)
    add(T_KACHING + 0.04, bell, 0.16)
    # the end card sliding back up
    w = noise(0.45, 30); add(T_END, w * np.sin(np.linspace(0, np.pi, len(w))), 0.05)
    out = out / max(1e-9, np.abs(out).max()) * 0.8
    out[: int(0.02 * sr)] *= np.linspace(0, 1, int(0.02 * sr))   # no click at the very start of the loop
    fade = int(0.12 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(path), "wb") as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(sr)
        wv.writeframes((out * 32767).astype(np.int16).tobytes())


def remux_audio():
    """Rebuild just the soundtrack and put it into the existing video (the picture is unchanged)."""
    import tempfile
    work = pathlib.Path(tempfile.mkdtemp(prefix="sidefrog-audio-"))
    wav = work / "sound.wav"; soundtrack(wav)
    mp4 = OUT / "sidefrog-demo.mp4"; tmp = work / "out.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(tmp)], check=True)
    shutil.copy(tmp, mp4); shutil.rmtree(work)
    print(f"{mp4} (new soundtrack)")


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
    if "--audio-only" in sys.argv:
        remux_audio()
    else:
        main()
