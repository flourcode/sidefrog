"use strict";

// Shared Lambda Function URL (the same Lambda also serves the Idea Sifter).
const CHECK_API_URL = "https://4s7uc7iyyeh7p4sknfpo6agllq0ahdff.lambda-url.us-east-1.on.aws/";

const CONFIG = {
  timeoutMs: 40000,
  minLength: 3,
  maxLength: 500,
  maxNames: 6, // show at most this many open .com names
  // Plain, non-affiliate links.
  // Porkbun, no affiliate. Check that ?q= pre-fills their search; if not, it still lands on Porkbun's search page.
  registrarUrl: (domain) => `https://porkbun.com/checkout/search?q=${encodeURIComponent(domain)}`,
  searchUrl: (q) => `https://www.google.com/search?q=${encodeURIComponent(q)}`,
};

const VERDICT_LABEL = {
  great: "Surprisingly, yes",
  worth_a_shot: "This could work",
  crowded: "Crowded pond",
  nah: "Keep your day job",
  cant_help: "Can't help with that one",
};

// The coffee frog's face for each verdict (faces live in the inline SVG; the
// body is frogs/coffee.svg). The verdict itself is the live caption text.
const VERDICT_FACE = { great: "yeah", worth_a_shot: "smirk", crowded: "meh", nah: "nah", cant_help: "sad" };

const $ = (sel) => document.querySelector(sel);

function el(tag, attrs = {}, text) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null) continue;
    if (k === "className") node.className = v;
    else node.setAttribute(k, v);
  }
  if (text !== undefined) node.textContent = text;
  return node;
}

// A full-width action row: text on the left, a short cue on the right.
// Used for names (Register ↗), searches (↗) and alternative ideas (Check).
function row(tag, attrs, mainNodes, cue) {
  const node = el(tag, { ...attrs, className: "row" });
  const main = el("span", { className: "row-main" });
  main.append(...mainNodes);
  node.append(main, el("span", { className: "row-cue", "aria-hidden": "true" }, cue));
  return node;
}
const NEW_TAB = " (opens in a new tab)";

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ---------------------------------------------------------------------------
// Ask the Lambda (one request: Gemini plus live .com checks)
// ---------------------------------------------------------------------------

async function ask(idea) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), CONFIG.timeoutMs);
  try {
    // text/plain keeps this a "simple" CORS request (no preflight). The Lambda parses it as JSON.
    const res = await fetch(CHECK_API_URL, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=UTF-8" },
      body: JSON.stringify({ kind: "idea", idea }),
      signal: ctrl.signal,
    });
    let data = null;
    try { data = await res.json(); } catch { /* handled below */ }
    if (!res.ok || !data?.idea) {
      const msg = typeof data?.error === "string" && data.error.length < 200 ? data.error : null;
      return { error: msg || "Something went wrong. Try again." };
    }
    return { report: data.idea };
  } catch (err) {
    return { error: err?.name === "AbortError" ? "That took too long. Try again." : "Couldn't connect. Check your connection and try again." };
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------------------
// Run a check
// ---------------------------------------------------------------------------

// Analytics (analytics.js). Categories only: never the idea text.
const track = (name, params) => { if (window.sfTrack) window.sfTrack(name, params); };

let runId = 0;
let lastIdea = "";
let justChecked = false; // after a result, the next click into the box selects it so typing replaces it

async function check(raw) {
  const input = $("#idea-input");
  let idea = String(raw || "").replace(/\s+/g, " ").trim();
  // Empty box: coach instead of checking the example. Frank asks for their own idea,
  // the cursor goes into the box (the keyboard opens on phones), and a small link
  // offers the example for anyone who just wants to see it work.
  if (!idea) {
    showError("Your turn. Type your own idea above, even a half-baked one.", { offerExample: true });
    input.removeAttribute("aria-invalid");
    input.focus();
    track("empty_nudge");
    return;
  }
  const error = $("#idea-error");
  error.hidden = true;
  input.removeAttribute("aria-invalid");
  if (idea.length < CONFIG.minLength) return showError("Type an idea first. Half-baked is fine.");
  if (idea.length > CONFIG.maxLength) return showError(`Keep it under ${CONFIG.maxLength} characters. One line is plenty.`);

  const id = ++runId;
  lastIdea = idea;
  setBusy(true);
  setStatus("Frank's sipping on it…");
  startThinking(idea);
  const step = setTimeout(() => {
    if (id !== runId) return;
    setStatus("Circling back on the .com names…");
    thinkingNote("Circling back on the .com names…");
  }, 4500);

  const { report, error: err } = await ask(idea);
  clearTimeout(step);
  if (id !== runId) return;
  setBusy(false);
  setStatus("");
  stopThinking(Boolean(err));
  if (err) { track("check_error"); return showError(err); }
  track("check", { verdict: report.verdict });
  render(report);
  justChecked = true;
}

// Progress for screen readers. Sighted people see Frank thinking in the card.
function setStatus(text) {
  $("#status-text").textContent = text;
}

// While a check runs, the card already on screen (the example on a first check,
// the last answer after that) shows the new idea and Frank sipping on a loop.
let thinkingCard = null;
let savedTitle = "";                 // the tab title before a check, restored if it fails
let savedMemo = "";
function memoRow(label, text) {
  const row = el("span", { className: "memo-row" });
  row.append(el("span", { className: "re" }, label), document.createTextNode(text));
  return row;
}
function startThinking(idea) {
  const result = $("#result");
  const example = $("#example");
  const card = !result.hidden ? result : example && !example.hidden ? example : null;
  if (!card) return;
  thinkingCard = card;
  const memo = card.querySelector(".you-wrote");
  savedMemo = memo.innerHTML;
  memo.replaceChildren(memoRow("FROM: ", "Frank"), memoRow("RE: ", idea));
  card.querySelector(".loading-note").textContent = "";
  card.classList.add("is-loading");
  savedTitle = document.title;
  document.title = "Sipping on it\u2026 \u00b7 SideFrog";   // for people who switched tabs while Frank thinks
  fitVerdict();
  const top = card.getBoundingClientRect().top;
  if (top < 0 || top > window.innerHeight * 0.65) {
    card.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "center" });
  }
}
function thinkingNote(text) {
  if (thinkingCard) thinkingCard.querySelector(".loading-note").textContent = text;
}
function stopThinking(failed) {
  if (!thinkingCard) return;
  thinkingCard.classList.remove("is-loading");
  if (failed) {
    thinkingCard.querySelector(".you-wrote").innerHTML = savedMemo;  // put the card back as it was
    document.title = savedTitle;
  }
  thinkingCard = null;
}

function showError(msg, opts = {}) {
  const e = $("#idea-error");
  $("#idea-error-text").textContent = msg;
  $("#try-example").hidden = !opts.offerExample;
  e.hidden = false;
  $("#idea-input").setAttribute("aria-invalid", "true");
}

function setBusy(on) {
  const btn = $("#idea-btn");
  btn.disabled = on;
  btn.textContent = on ? "Checking…" : "Check it";
}

// ---------------------------------------------------------------------------
// Render the answer card
// ---------------------------------------------------------------------------

function render(r) {
  const card = $("#result");
  card.dataset.verdict = r.verdict;

  const wrote = $("#you-wrote");
  // Memo header: from Frank (the frog; no explanation), re: your idea
  wrote.replaceChildren(memoRow("FROM: ", "Frank"), memoRow("RE: ", lastIdea));
  $("#verdict").replaceChildren(el("span", { className: "verdict-text" }, VERDICT_LABEL[r.verdict] || "Here's the read"));
  // The tab shows the verdict (never the idea, so nothing typed lands in browser history)
  document.title = `${VERDICT_LABEL[r.verdict] || "Here's the read"} \u00b7 SideFrog`;
  $("#mascot").dataset.mood = VERDICT_FACE[r.verdict] || "smirk";
  const sticker = $("#sticker");
  sticker.classList.remove("is-sipping");
  void sticker.getBoundingClientRect(); // restart the sip for every new answer
  if (!reducedMotion()) sticker.classList.add("is-sipping");
  $("#reason").textContent = r.verdictReason || "";

  // Quick facts: the sharper version, who pays, the first move
  const facts = $("#facts");
  facts.replaceChildren();
  // "Watch out for" is skipped when Frank finds nothing worth flagging, to keep the card short
  const watchOut = r.watchOut && !/^nothing obvious/i.test(r.watchOut.trim()) ? r.watchOut : "";
  for (const [label, value] of [["Sharper version", r.sharpenedIdea], ["Who pays", r.whoPays], ["Try this first", r.firstMove],
                                ["Good sign", r.goodSign], ["Watch out for", watchOut]]) {
    if (!value) continue;
    const row = el("div");
    row.append(el("dt", {}, label), el("dd", {}, value));
    facts.append(row);
  }

  renderYours(r.yourName);
  renderNames(Array.isArray(r.names) ? r.names : [], r.verdict);
  $("#names-title").textContent = r.yourName ? "Other names with an open .com" : "Names with an open .com";

  // Related searches: open Google so people can see the competition themselves
  const kws = r.verdict === "cant_help" || !Array.isArray(r.keywords) ? [] : r.keywords;
  $("#keywords").replaceChildren(...kws.map((k) => {
    const li = el("li");
    li.append(row("a", { href: CONFIG.searchUrl(k), target: "_blank", rel: "noopener", "aria-label": `Search Google for ${k}${NEW_TAB}` },
      [document.createTextNode(k)], "↗"));
    return li;
  }));
  $("#keywords-part").hidden = kws.length === 0;

  // Other ideas: one click checks the next one
  const alts = Array.isArray(r.alternatives) ? r.alternatives : [];
  $("#alts").replaceChildren(...alts.map((text) => {
    const li = el("li");
    const btn = row("button", { type: "button", "aria-label": `Check this idea: ${text}` }, [document.createTextNode(text)], "Check");
    btn.addEventListener("click", () => tryIdea(text));
    li.append(btn);
    return li;
  }));
  $("#alts-title").textContent = r.verdict === "cant_help" ? "Ideas we can help with" : "Try one of these instead";
  $("#alts-part").hidden = alts.length === 0;

  renderKit(r);

  card.hidden = false;
  const example = $("#example");
  if (example) example.hidden = true;   // the real answer replaces the example
  fitVerdict();
  const heading = $("#verdict");
  card.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });
  heading.focus({ preventScroll: true });
}

// The name the person typed or mentioned, checked live: always shown, open or not.
function renderYours(y) {
  const part = $("#yours-part");
  const box = $("#yours");
  box.replaceChildren();
  part.hidden = !y;
  if (!y) return;

  const pillText = {
    likely_available: "Looks open",
    taken: y.registeredYear ? `Taken since ${y.registeredYear}` : "Taken",
    unknown: "Couldn't check right now",
  }[y.status] || "Couldn't check right now";

  box.append(
    el("span", { className: "name-word" }, y.name),
    el("span", { className: "sr-only" }, ", "),
    el("span", { className: "name-domain" }, y.domain),
    el("span", { className: "sr-only" }, ", "),
    el("span", { className: "pill", "data-status": y.status }, pillText),
    el("span", { className: "sr-only" }, ", "),
  );
  if (y.status === "likely_available") {
    box.append(el("a", { href: CONFIG.registrarUrl(y.domain), target: "_blank", rel: "noopener", "aria-label": `Register ${y.domain}${NEW_TAB}` }, "Register it ↗"));
  } else if (y.status === "taken") {
    box.append(el("a", { href: `https://${y.domain}`, target: "_blank", rel: "noopener nofollow", "aria-label": `See who has ${y.domain}${NEW_TAB}` }, "See who has it ↗"));
  } else {
    box.append(el("a", { href: CONFIG.registrarUrl(y.domain), target: "_blank", rel: "noopener", "aria-label": `Look up ${y.domain}${NEW_TAB}` }, "Look it up ↗"));
  }

  const takenHint = y.status === "taken" ? " The open names below are close alternatives." : "";
  $("#yours-note").textContent = `${y.comment || ""}${takenHint}`.trim();
}

// The verdict always stays on one line, the frog's one-liner. CSS sets the
// largest size; this shrinks it only when the line would overflow its space.
function fitVerdict() {
  for (const h of document.querySelectorAll(".result:not([hidden]) .verdict")) fitOne(h);
}

function fitOne(h) {
  const text = h.firstElementChild;
  if (!text) return;
  h.style.fontSize = "";                       // start from the CSS maximum
  const avail = h.clientWidth;
  const need = text.offsetWidth;
  if (!avail || !need) return;                 // not laid out yet
  if (need > avail) {
    const max = parseFloat(getComputedStyle(h).fontSize);
    let size = Math.max(14, Math.floor(max * (avail / need)));
    h.style.fontSize = `${size}px`;
    // Letter widths don't scale perfectly; nudge down until it really fits.
    for (let i = 0; i < 12 && size > 14 && text.offsetWidth > h.clientWidth; i++) {
      size -= 1;
      h.style.fontSize = `${size}px`;
    }
  }
}

// Re-fit when the card changes width (rotation, resizing) and once the web font arrives.
if ("ResizeObserver" in window) {
  let lastWidth = 0;
  new ResizeObserver((entries) => {
    const w = Math.round(entries[0].contentRect.width);
    if (w !== lastWidth) { lastWidth = w; fitVerdict(); }
  }).observe(document.querySelector("main") || document.body);
} else {
  window.addEventListener("resize", fitVerdict);
}
if (document.fonts?.ready) document.fonts.ready.then(fitVerdict);

// ---- Take it further: ready-made prompts to paste into your own AI ---------------
// Built in the browser from the answer you just got. Nothing is sent anywhere again.

const GUIDES = {
  test: { href: "break-room/start/test-an-idea-in-a-week/", title: "Test a side hustle idea in a week" },
  competition: { href: "break-room/start/size-up-the-competition/", title: "Who's already doing it?" },
  leap: { href: "break-room/leap/before-you-leap/", title: "Before you leap" },
};
const READ_NEXT = { great: "leap", worth_a_shot: "test", crowded: "competition", nah: "test" };   // "Surprisingly, yes" is when people are most tempted to quit on the spot
const KIT_FOR = {
  great: ["page", "buyers", "faq"],
  worth_a_shot: ["page", "buyers", "faq"],
  crowded: ["reviews", "buyers", "page"],
  nah: ["buyers"],
  cant_help: [],
};

function kitPrompts(r) {
  const idea = r.sharpenedIdea || lastIdea;
  const who = r.whoPays || "[who you think will pay]";
  const open = (Array.isArray(r.names) ? r.names : []).find((n) => n.status === "likely_available");
  const nameLine = r.yourName && r.yourName.status === "likely_available"
    ? `${r.yourName.name} (${r.yourName.domain})`
    : open ? `${open.name} (${open.domain})` : "[your business name]";
  const searches = Array.isArray(r.keywords) && r.keywords.length ? r.keywords.map((k) => `"${k}"`).join(", ") : "[a few searches your buyers would type]";
  return {
    page: {
      name: "Build the page",
      text: `Build me a one-page landing page as a single HTML file (HTML, CSS and a little JavaScript, no frameworks, under 40KB).

The business: ${idea}
Who it's for and who pays: ${who}
The name: ${nameLine}
The price: [your price, or "early access"]

What makes it mine (fill these in; they're what keep it from looking like every other site):
- What I believe about this work: [e.g. "restaurant owners shouldn't need a web developer to change their hours"]
- How it should feel, in a few words: [e.g. "warm, local, no-nonsense"]
- A place, era or brand whose look I like: [e.g. "an old diner menu" or "1970s travel posters"]
- One detail only someone in this business would think of: [e.g. "today's hours at the top, because that's what customers check"]
- The worry that almost stops people buying: [e.g. "I'll have to learn some new system" or "you'll disappear after the first month"]

The page needs:
- A headline that says what it is in plain words
- One short paragraph on who it's for and the problem it solves
- The price
- A short, direct answer to that worry, right above the button, with real evidence if I have it: a before-and-after, a real customer's words used with permission, or a specific guarantee
- One button that opens this sign-up form: [paste your Google Form link]

Rules:
- Mobile first and easy to read on a small phone
- Plain, specific language. No hype words.
- Don't invent testimonials, reviews, customer counts or statistics.
- One page only, with no navigation menu.
- Skip the generic startup template look: no gradient hero, no stock icons, no emoji. Pick fonts and colors that fit how it should feel.

When you're done:
1. Look at the page the way a skeptical customer would, list the five things that make it feel generic or unfinished, and fix them.
2. Tell me in two sentences how to put it online for free.`,
    },
    buyers: {
      name: "Talk to ten buyers",
      text: `I'm testing a side business idea before I spend money on it.

The idea: ${idea}
Who I think pays: ${who}

Help me talk to ten real potential buyers this week:
1. List specific places where these people already gather, online and offline, where it's normal to ask questions.
2. Write a short, honest message I can send or post asking for 15 minutes of their time. Make it clear I'm not selling anything yet.
3. Give me five questions about how they handle this problem today and what they've already tried or paid for. Avoid questions like "Would you use this?" that invite polite answers.
4. Tell me which answers would mean the idea is worth pursuing, and which would mean I should stop.`,
    },
    reviews: {
      name: "Read their bad reviews",
      text: `I'm sizing up the competition for this idea: ${idea}

Below I'll paste one- to three-star reviews of competing products or services. Please:
1. Group the complaints into themes and count how often each one comes up.
2. Quote one short example for each theme.
3. Tell me which complaint looks like the best opening for a small, new business, and why.
4. Suggest one sentence I could use to describe my offer to the people who wrote these reviews.

Searches I've been using: ${searches}

Reviews:
[paste the reviews here]`,
    },
    faq: {
      name: "Answer the questions",
      text: `I'm writing an FAQ page for this business: ${idea}
Who it's for: ${who}

1. List the ten questions a likely buyer would type into Google or ask an AI assistant before buying something like this. Use their words, not industry words. Start from these searches: ${searches}
2. Answer each one in two or three plain sentences. Be specific about who it's for, what it costs ([your price]) and where it's available ([your area, or "online"]).
3. Don't make claims you can't back up. Leave a blank wherever you'd need a fact from me.
4. Format the result as HTML with each question as an h3, plus FAQPage structured data (JSON-LD) that matches the visible text exactly.`,
    },
  };
}

function copyText(text, btn) {
  const done = () => {
    btn.textContent = "Copied";
    const live = document.getElementById("announce");
    if (live) live.textContent = "Prompt copied. Paste it into Claude, ChatGPT or Gemini.";
    setTimeout(() => { btn.textContent = "Copy prompt"; }, 2200);
  };
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(done, () => { btn.textContent = "Select the text above to copy"; });
  } else {
    btn.textContent = "Select the text above to copy";
  }
}

function renderKit(r) {
  const part = $("#kit-part");
  const list = $("#kit");
  const keys = KIT_FOR[r.verdict] || [];
  const prompts = kitPrompts(r);
  list.replaceChildren(...keys.map((k) => {
    const p = prompts[k];
    const li = el("li");
    const details = el("details", { className: "kit-item" });
    const summary = el("summary", { className: "row" });
    summary.append(el("span", { className: "row-main" }, p.name), el("span", { className: "row-cue", "aria-hidden": "true" }, "Show"));
    const pre = el("pre", { className: "kit-text", tabIndex: 0 }, p.text);
    const btn = el("button", { type: "button", className: "kit-copy" }, "Copy prompt");
    btn.addEventListener("click", () => { copyText(p.text, btn); track("prompt_copy", { prompt: k }); });
    details.append(summary, pre, btn);
    li.append(details);
    return li;
  }));
  part.hidden = keys.length === 0;
  // Mark's help offer only follows a promising verdict. After "Keep your day job"
  // or "Crowded pond" the free guide below is the next step, not a sales pitch.
  const help = part.querySelector(".help-note");
  if (help) help.hidden = !(r.verdict === "great" || r.verdict === "worth_a_shot");
  const next = GUIDES[READ_NEXT[r.verdict]];
  const read = $("#read-next");
  read.replaceChildren();
  if (next) read.append("Read next: ", el("a", { href: next.href }, next.title));
}

// Only names the registry shows as open are listed. If none are open, say so
// plainly; if the registry couldn't be reached, show a few names marked as unchecked.
function renderNames(names, verdict) {
  const part = $("#names-part");
  const list = $("#names");
  const note = $("#names-note");
  list.replaceChildren();
  note.textContent = "";
  if (verdict === "cant_help" || names.length === 0) { part.hidden = true; return; }
  part.hidden = false;

  const open = names.filter((n) => n.status === "likely_available");
  const unknown = names.filter((n) => n.status === "unknown");
  const shown = (open.length ? open : unknown).slice(0, CONFIG.maxNames);

  // Frank doesn't sell a domain for an idea he just told you not to pursue:
  // on "Keep your day job" the names are shown for reference, with no registrar link.
  const buyable = verdict !== "nah";
  for (const n of shown) {
    const li = el("li", { "data-status": n.status });
    const parts = [el("span", { className: "name-word" }, n.name), el("span", { className: "name-domain" }, n.domain)];
    if (buyable) {
      const action = open.length ? "Register" : "Look it up";
      li.append(row("a",
        { href: CONFIG.registrarUrl(n.domain), target: "_blank", rel: "noopener", "aria-label": `${action} ${n.domain}${NEW_TAB}` },
        parts, `${action} ↗`));
    } else {
      const plain = el("div", { className: "row row-static" });
      const main = el("span", { className: "row-main" });
      main.append(...parts);
      plain.append(main);
      li.append(plain);
    }
    list.append(li);
  }

  if (!open.length && !unknown.length) {
    note.textContent = names.length === 1
      ? "The name we came up with already has its .com taken. Check it again for a fresh batch."
      : `All ${names.length} names we came up with already have their .com taken. Check it again for a fresh batch.`;
  } else if (!open.length) {
    note.textContent = "Couldn't reach the .com registry just now, so these aren't checked yet.";
  } else {
    const taken = names.filter((n) => n.status === "taken").length;
    const takenText = taken ? `; ${taken} ${taken === 1 ? "was" : "were"} taken` : "";
    const nameCount = `${names.length} ${names.length === 1 ? "name" : "names"}`;
    const these = open.length === 1 ? "This one was" : "These were";
    note.textContent = buyable
      ? `We came up with ${nameCount} and checked each .com live${takenText}. ${these} open when we checked. ${open.length === 1 ? "If it sticks" : "If one sticks"}, confirm it at the registrar before you get attached.`
      : `I wouldn't buy anything yet. ${these} open when we checked, if you want to keep one in mind.`;
  }
}

// Empty the box and put the cursor in it, ready for the next idea.
function newIdea({ scroll = false } = {}) {
  const input = $("#idea-input");
  input.value = "";
  autosize(input);
  syncClear();
  justChecked = false;
  $("#idea-error").hidden = true;
  input.removeAttribute("aria-invalid");
  if (scroll) window.scrollTo({ top: 0, behavior: reducedMotion() ? "auto" : "smooth" });
  input.focus({ preventScroll: scroll });
}

function syncClear() {
  $("#idea-clear").hidden = $("#idea-input").value.trim() === "";
}

function tryIdea(text) {
  const input = $("#idea-input");
  input.value = text;
  autosize(input);
  syncClear();
  window.scrollTo({ top: 0, behavior: reducedMotion() ? "auto" : "smooth" });
  check(text);
}

// The grey examples the empty box rotates through: realistic side hustles with
// the odd weird one, so people see any idea is fair game.
const EXAMPLES = [
  "taco truck empire",
  "website tune-ups for local restaurants",
  "travel planning for busy families",
  "estate sale flipping on weekends",
  "LinkedIn coaching for executives",
  "cruise broker",
  "candles that smell like the office",
];

function autosize(textarea) {
  textarea.style.height = "auto";
  // While empty, size to the LONGEST example, so the box never jumps as they
  // rotate and no example is ever cut off on a narrow screen.
  if (!textarea.value) {
    let h = 0;
    for (const ex of EXAMPLES.map((x) => "e.g. " + x).concat(textarea.placeholder || [])) {
      textarea.value = ex;
      h = Math.max(h, textarea.scrollHeight);
    }
    textarea.value = "";
    textarea.style.height = `${h}px`;
    return;
  }
  textarea.style.height = `${textarea.scrollHeight}px`;
}

// Rotate the grey example every few seconds, but hold still while someone is in
// the box or has typed, while the tab is in the background, and for reduced motion.
// The grey text reads "e.g. taco truck empire" so it's clearly an example.
const EG = "e.g. ";
const currentExample = (input) => input.placeholder.replace(/^e\.g\.\s*/i, "").trim() || EXAMPLES[0];

function rotateExamples(input) {
  if (reducedMotion()) return;
  let i = Math.max(0, EXAMPLES.indexOf(currentExample(input)));
  setInterval(() => {
    if (document.hidden || input.value || document.activeElement === input) return;
    i = (i + 1) % EXAMPLES.length;
    input.placeholder = EG + EXAMPLES[i];
  }, 3500);
}

// ---------------------------------------------------------------------------
// Wire up
// ---------------------------------------------------------------------------

function init() {
  const input = $("#idea-input");
  $("#idea-form").addEventListener("submit", (e) => {
    e.preventDefault();
    check(input.value);
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { // Enter checks; Shift+Enter adds a line
      e.preventDefault();
      check(input.value);
    } else if (e.key === "Escape" && input.value) { // Escape clears the box
      e.preventDefault();
      newIdea();
    }
  });
  // After a result, clicking or tabbing into the box selects the old idea,
  // so just typing replaces it. No need to backspace.
  const selectIfStale = () => {
    if (justChecked && input.value.trim() === lastIdea) input.select();
  };
  input.addEventListener("focus", selectIfStale);
  input.addEventListener("click", selectIfStale);
  $("#idea-clear").addEventListener("click", () => newIdea());
  $("#again").addEventListener("click", () => newIdea({ scroll: true }));

  fitVerdict();   // the example answer is on screen from the start
  // Size the idea box now, again once the web font is in, and when the width changes
  autosize(input);
  rotateExamples(input);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => autosize(input));
  let lastBoxWidth = input.clientWidth;
  window.addEventListener("resize", () => {
    if (input.clientWidth !== lastBoxWidth) { lastBoxWidth = input.clientWidth; autosize(input); }
  });

  input.addEventListener("input", () => {
    justChecked = false;
    syncClear();
    autosize(input);
    if (!$("#idea-error").hidden) $("#idea-error").hidden = true;
    input.removeAttribute("aria-invalid");
  });
  // "or check the example": runs whichever example is showing, typed into the box
  $("#try-example").addEventListener("click", () => {
    const ex = currentExample(input);
    input.value = ex;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    track("example_check");
    check(ex);
  });
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();
