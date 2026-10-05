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
  // Empty box: a quiet nudge. The cursor stays in the box (the keyboard opens on
  // phones), the box gives a small shake, and one short line asks for an idea.
  // The rotating examples are inspiration only; they're never checked.
  if (!idea) {
    showError("Give me something to work with.", { hint: true });
    input.removeAttribute("aria-invalid");
    input.focus();
    const plate = $(".plate");
    if (!reducedMotion()) { plate.classList.remove("shake"); void plate.offsetWidth; plate.classList.add("shake"); }
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
  thinkingNote("This is a coffee break, not Shark Tank.");   // the joke while Frank sips; replaced if it runs long
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
  checksThisVisit += 1;
  // from_shared: this check started on a shared verdict (the sharing loop: someone got a verdict, then tried their own)
  const fromShared = location.pathname.startsWith("/verdict") || location.hash.startsWith("#v=");
  track("check", { verdict: report.verdict, check_number: checksThisVisit, from_shared: fromShared ? "yes" : "no" });
  if (checksThisVisit === 2) track("second_check", { verdict: report.verdict });
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
let savedTitle = "";
let checksThisVisit = 0;      // analytics: 1st, 2nd, 3rd check in this visit (a 2nd check means it was fun)
let shownReport = null;       // the answer on screen, for the share card                 // the tab title before a check, restored if it fails
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
  if (window.frankLoop) window.frankLoop(card.querySelector(".frank"));
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
  if (window.frankStop) window.frankStop(thinkingCard.querySelector(".frank"));
  if (failed) {
    thinkingCard.querySelector(".you-wrote").innerHTML = savedMemo;  // put the card back as it was
    document.title = savedTitle;
  }
  thinkingCard = null;
}

function showError(msg, opts = {}) {
  const e = $("#idea-error");
  $("#idea-error-text").textContent = msg;
  e.classList.toggle("is-hint", Boolean(opts.hint));   // a quiet nudge: no Frank, no red
  e.hidden = false;
  keepMessageInView();
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
  // RE is a memo subject line: Frank's 3-6 word summary, or the idea trimmed to one line (CSS) if there isn't one
  const subject = (r.subject || "").trim() || lastIdea;
  const reRow = memoRow("RE: ", subject);
  if (subject !== lastIdea) reRow.title = lastIdea;              // the full idea on hover
  wrote.replaceChildren(memoRow("FROM: ", "Frank"), reRow);
  $("#verdict").replaceChildren(el("span", { className: "verdict-text" }, VERDICT_LABEL[r.verdict] || "Here's the read"));
  // The tab shows the verdict (never the idea, so nothing typed lands in browser history)
  document.title = `${VERDICT_LABEL[r.verdict] || "Here's the read"} \u00b7 SideFrog`;
  $("#mascot").dataset.mood = VERDICT_FACE[r.verdict] || "smirk";
  shownReport = { ...r, idea: lastIdea, re: subject };
  warmShareCard();
  $("#share-row").hidden = r.verdict === "cant_help";
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
  // The cheap test leads, then its pass/fail pair (when to keep going, when to rethink),
  // then context. An older Lambda without rethinkIf just skips that row.
  for (const [label, value, role] of [["Cheap test", r.firstMove, "fact-lead"],
                                      ["Keep going if", r.goodSign, "fact-signal"], ["Rethink it if", r.rethinkIf, "fact-signal"],
                                      ["Watch out for", watchOut, "fact-minor"],
                                      ["Who pays", r.whoPays, "fact-minor"], ["Sharper version", r.sharpenedIdea, "fact-minor"]]) {
    if (!value) continue;
    const row = el("div", { className: role });
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

// ---- Hand it to your AI: ready-made prompts to paste into your own AI ---------------
// Built in the browser from the answer you just got. Nothing is sent anywhere again.

const GUIDES = {
  test: { href: "break-room/start/test-an-idea-in-a-week/", title: "Test a side hustle idea in a week" },
  competition: { href: "break-room/start/size-up-the-competition/", title: "Who's already doing it?" },
  leap: { href: "break-room/leap/before-you-leap/", title: "Before you leap" },
  feedback: { href: "break-room/start/where-to-get-feedback/", title: "Where to get honest feedback" },
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
      text: `Design and build a one-page landing page for my business, as a single complete HTML file.

ABOUT THE BUSINESS
- What it is: ${idea}
- Who it's for and what they pay: ${who}
- Name: ${nameLine}

BEFORE YOU BUILD
Ask me these in one short message, then wait for my answers:
1. The name (or confirm the one above), and the exact price.
2. What I believe about this work that others in my field don't.
3. How it should feel, in a few words, and a place, era or brand whose look I like.
4. The worry that almost stops people from buying, and any real proof I have that answers it (a customer's words I'm allowed to use, a before-and-after, a guarantee).
5. The link people should land on when they tap the button (a Google Form is fine).
If I answer "you choose" to any of these, make a confident, specific choice that fits this business and tell me what you chose.

THE ONE JOB
The page has one job: get the right person to tap one button. Everything on it should help that. Anything that doesn't, leave out.

WHAT IT CONTAINS, IN ORDER
1. A first screen that works on a phone without scrolling: the name, a headline that says plainly what this is and who it's for, one supporting sentence, the price, and the button.
2. A concrete picture of what the customer actually gets, or what happens first, in three short steps or one short paragraph. Specific beats impressive.
3. The worry, answered directly with my real proof, just above the same button again.
4. A quiet footer: the name, a way to reach me, and any fine print this business needs.
No navigation menu, no feature grid, no wall of FAQs.

HOW IT SHOULD LOOK AND FEEL
- Design it from this business, not from a template. Someone in this trade should recognize it as theirs.
- Premium craft: a confident type scale, generous spacing, and a restrained palette taken from the business and the feel I described. You may load one or two Google Fonts.
- One simple visual drawn in inline SVG or CSS that belongs to this business. No stock photos, icon sets, emoji or gradient hero.
- Calm, purposeful motion: sections ease in as they scroll into view, and the button responds to a tap. Respect prefers-reduced-motion, and never make anyone wait to read.
- Mobile first, easy to read on a small phone, good contrast, visible keyboard focus.

HOW IT SHOULD WORK
- One self-contained file (HTML, CSS and a little JavaScript), no frameworks or build step, fast on a phone.
- Both buttons open my link in a new tab. If I haven't given one, put a clearly marked placeholder at the top of the script.
- Include a page title, a description and social-sharing tags.

HONESTY
Plain, specific words, no hype. Never invent testimonials, reviews, customer counts, statistics, credentials or awards. Where proof is missing, leave a clearly marked spot for it.

BEFORE YOU SHOW ME
1. Read the page as a skeptical customer on a phone, then as a demanding designer. List the five weakest things and fix them.
2. Ask what's on the page because it could be, not because it should be, and remove it.
3. Give me the finished file, tell me exactly where to paste my link, and explain in two sentences how to put it online for free.`,
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
  // when the cheap test is about asking people online, point to the feedback guide
  const asksOnline = /\b(reddit|subreddit|r\/|facebook|nextdoor|linkedin|forum|community|group|post (it|them|a|an|in|on))\b/i.test(r.firstMove || "");
  const next = GUIDES[asksOnline && r.verdict !== "nah" ? "feedback" : READ_NEXT[r.verdict]];
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
  list.hidden = shown.length === 0;   // no empty list (and no stray bullet) when nothing is open
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
      ? "The name we came up with already has its .com taken. Check it again for a fresh batch, or add a name of your own to the idea."
      : `All ${names.length} names we came up with already have their .com taken. Check it again for a fresh batch, or add a name of your own to the idea.`;
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
  "interview coaching",
  "taco truck empire",
  "YouTube influencer",
  "yard sale flipping",
  "fractional sales help",
  "dog walking business",
  "passive-aggressive mugs",
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

// Frank's message lives inside the idea box. If it isn't fully visible (a phone keyboard
// takes about half the screen), bring the whole box up so it sits just below the top.
function keepMessageInView() {
  const check = () => {
    const box = $(".plate"), msg = $("#idea-error");
    if (!box || !msg || msg.hidden) return;
    const vv = window.visualViewport;
    const top = vv ? vv.offsetTop : 0, height = vv ? vv.height : window.innerHeight;
    const r = msg.getBoundingClientRect();
    if (r.top >= top + 8 && r.bottom <= top + height - 8) return;
    window.scrollBy({ top: box.getBoundingClientRect().top - top - 10, behavior: reducedMotion() ? "auto" : "smooth" });
  };
  requestAnimationFrame(check);
  setTimeout(check, 350);   // again once a phone keyboard has finished opening
}

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
// Share Frank's verdict: a 1080x1350 image drawn in the browser from the answer on
// screen. Nothing is sent anywhere; the visitor decides whether to share it.
// ---------------------------------------------------------------------------

const SHARE = { w: 1080, h: 1350, pad: 72, paper: "#FBF7EF", card: "#FFFDF9", ink: "#1F241F",
  muted: "#5A5A4A", rule: "#A89B84", accent: "#A4501F", font: '"Bricolage Grotesque", system-ui, sans-serif' };

// Frank for the share card: his face's frame, cut from the same sprite the page shows.
const FRANK_FRAME = { yeah: 0, smirk: 1, think: 1, meh: 2, nah: 2, sad: 3, oops: 4, you: 12 };
// two sprites: the cutout (the masthead logo) and the round one (the share card's Frank);
// each loads once, so requests at the same time all wait for the same load
const frankSprites = {};
function loadFrankSprite(round) {
  const key = round ? "round" : "cutout";
  if (!frankSprites[key]) {
    const css = round ? getComputedStyle(document.documentElement).getPropertyValue("--frank-round")
                      : getComputedStyle($("#mascot")).backgroundImage;
    // a url() inside a CSS variable is relative to the stylesheet, not this page (which can be /verdict/)
    const sheet = document.querySelector('link[rel="stylesheet"][href*="styles.css"]');
    const url = new URL(css.trim().replace(/^url\(["']?|["']?\)$/g, ""), sheet ? sheet.href : location.href).href;
    frankSprites[key] = new Promise((ok, fail) => {
      const img = new Image();
      img.onload = () => ok(img);
      img.onerror = () => { delete frankSprites[key]; fail(new Error("Frank's sprite didn't load")); };
      img.src = url;
    });
  }
  return frankSprites[key];
}
async function frankImage(mood, round = false) {
  const sprite = await loadFrankSprite(round);
  const size = sprite.naturalHeight, f = FRANK_FRAME[mood] ?? 1;
  const c = document.createElement("canvas"); c.width = c.height = size;
  c.getContext("2d").drawImage(sprite, f * size, 0, size, size, 0, 0, size, size);
  return c;
}

function wrapLines(ctx, text, maxWidth, maxLines) {
  const words = String(text).split(/\s+/).filter(Boolean), lines = [];
  let line = "";
  for (const w of words) {
    const test = line ? `${line} ${w}` : w;
    if (ctx.measureText(test).width <= maxWidth || !line) line = test;
    else { lines.push(line); line = w; }
  }
  if (line) lines.push(line);
  if (lines.length > maxLines) {
    const kept = lines.slice(0, maxLines);
    let last = kept[maxLines - 1];
    while (ctx.measureText(last + "\u2026").width > maxWidth && last.includes(" ")) last = last.slice(0, last.lastIndexOf(" "));
    kept[maxLines - 1] = last.replace(/[,.;:]$/, "") + "\u2026";
    return kept;
  }
  return lines;
}

// Start loading Frank's two pictures for the share card as soon as there's a verdict,
// so they're ready by the time someone taps Share.
function warmShareCard() {
  try { loadFrankSprite(true).catch(() => {}); loadFrankSprite(false).catch(() => {}); } catch { /* the share retries */ }
}

// Waits for a promise, but never longer than ms: then it settles with the fallback instead.
// The share card never hangs on a slow font or image; it draws with whatever has arrived.
function withTimeout(promise, ms, fallback) {
  return Promise.race([promise, new Promise((ok) => setTimeout(() => ok(fallback), ms))]);
}

async function drawShareCard(r) {
  const S = SHARE, c = document.createElement("canvas");
  c.width = S.w; c.height = S.h;
  const ctx = c.getContext("2d");
  const font = (weight, size) => { ctx.font = `${weight} ${size}px ${S.font}`; };
  const spacing = (px) => { if ("letterSpacing" in ctx) ctx.letterSpacing = `${px}px`; };
  try { await withTimeout(Promise.all([document.fonts.load(`800 100px ${S.font}`), document.fonts.load(`400 40px ${S.font}`)]), 3000); } catch {}
  const mood = VERDICT_FACE[r.verdict] || "smirk";
  let bigFrank = null, smallFrank = null;
  // each Frank loads on his own: if one ever fails, the card still gets the other
  const [big, small] = await Promise.allSettled([
    withTimeout(frankImage(mood, true), 10000, null),     // null: not here yet
    withTimeout(frankImage("you"), 10000, null),
  ]);
  if (big.status === "fulfilled") bigFrank = big.value;
  if (small.status === "fulfilled") smallFrank = small.value;
  // No card without Frank: if either picture is missing, stop here and let the person try again
  if (!bigFrank || !smallFrank) throw new Error("no-frank");

  ctx.fillStyle = S.paper; ctx.fillRect(0, 0, S.w, S.h);
  // masthead: Frank, the wordmark, a rule
  const L = S.pad, R = S.w - S.pad;
  if (smallFrank) ctx.drawImage(smallFrank, L - 4, 50, 90, 90);
  font(800, 48); spacing(-1.5); ctx.fillStyle = S.ink; ctx.textBaseline = "alphabetic";
  ctx.fillText("SideFrog", L + (smallFrank ? 98 : 0), 118);
  ctx.fillRect(L, 164, R - L, 3);

  // the memo card: measure first, then draw
  const cardX = L, cardW = R - L, inPad = 56, inL = cardX + inPad, inW = cardW - inPad * 2;
  // Frank sits beside the verdict with his eyes level with its first line (like the answer card)
  const frankW = 236, frankH = 236, frankEyes = 0.29;     // his eyes are ~29% down the round frame
  const memoW = inW, vW = inW - frankW - 26;
  font(800, 30); spacing(3);
  const reLabelW = ctx.measureText("RE: ").width;
  font(400, 34); spacing(0);
  const reLines = wrapLines(ctx, r.re || r.idea, memoW - reLabelW - 10, 2);
  // the verdict in the column beside Frank: the biggest size from 108 down to 84 that fits in two lines
  const verdictText = (VERDICT_LABEL[r.verdict] || "Here's the read").toUpperCase();
  let vSize = 84;
  for (let s = 108; s >= 84; s -= 4) {
    font(800, s); spacing(-s / 27);
    const lines = wrapLines(ctx, verdictText, vW, 3);
    if (lines.length <= 2 && lines.every((l) => ctx.measureText(l).width <= vW)) { vSize = s; break; }
  }
  font(800, vSize); spacing(-vSize / 27);
  const verdictLines = wrapLines(ctx, verdictText, vW, 3);
  const vLine = Math.round(vSize * 0.94);
  font(400, 42); spacing(0);
  const reasonLines = wrapLines(ctx, r.verdictReason || "", inW, 6);
  // lay out once at the top to get the height, then center the card and the URL below the masthead
  const layout = (cardY) => {
    const memoTop = cardY + 78, memoBottom = memoTop + 52 + (reLines.length - 1) * 46 + 18;
    const verdictTop = memoBottom + 40;
    const eyeLine = verdictTop + vSize * 0.46;                       // the middle of the verdict's first line
    const frankY = Math.max(memoBottom + 12, eyeLine - frankH * frankEyes);
    const reasonTop = Math.max(verdictTop + verdictLines.length * vLine, frankY + frankH) + 26;
    const cardH = reasonTop + reasonLines.length * 58 - cardY + 50;
    return { cardY, memoTop, memoBottom, verdictTop, frankY, reasonTop, cardH };
  };
  const first = layout(0), blockH = first.cardH + 14 + 96 + 54, room = S.h - 200 - 70;
  const { cardY, memoTop, memoBottom, verdictTop, frankY, reasonTop, cardH } = layout(200 + Math.max(20, (room - blockH) / 2));

  // hard offset shadow, then the card
  const rr = (x, y, w, h, rad) => { ctx.beginPath(); ctx.moveTo(x + rad, y); ctx.arcTo(x + w, y, x + w, y + h, rad); ctx.arcTo(x + w, y + h, x, y + h, rad); ctx.arcTo(x, y + h, x, y, rad); ctx.arcTo(x, y, x + w, y, rad); ctx.closePath(); };
  ctx.fillStyle = S.ink; rr(cardX + 14, cardY + 14, cardW, cardH, 34); ctx.fill();
  ctx.fillStyle = S.card; rr(cardX, cardY, cardW, cardH, 34); ctx.fill();
  ctx.lineWidth = 4; ctx.strokeStyle = S.ink; ctx.stroke();

  // FROM / RE
  font(800, 30); spacing(3); ctx.fillStyle = S.accent; ctx.fillText("FROM:", inL, memoTop);
  const fromW = ctx.measureText("FROM: ").width;
  font(400, 34); spacing(0); ctx.fillStyle = S.muted; ctx.fillText("Frank", inL + fromW, memoTop);
  font(800, 30); spacing(3); ctx.fillStyle = S.accent; ctx.fillText("RE:", inL, memoTop + 52);
  font(400, 34); spacing(0); ctx.fillStyle = S.muted;
  reLines.forEach((line, i) => ctx.fillText(line, inL + reLabelW, memoTop + 52 + i * 46));
  ctx.fillStyle = S.rule; ctx.fillRect(inL, memoBottom, memoW, 2);
  if (bigFrank) {
    // round Frank, like his profile picture: a cream circle with his verdict face
    const fx = cardX + cardW - inPad - frankW + 18, fy = frankY;
    ctx.save(); ctx.beginPath(); ctx.arc(fx + frankW / 2, fy + frankH / 2, frankW / 2, 0, Math.PI * 2); ctx.closePath();
    ctx.fillStyle = "#ECE3D1"; ctx.fill(); ctx.clip();
    ctx.drawImage(bigFrank, fx, fy, frankW, frankH); ctx.restore();
  }

  // the verdict, then the reason
  font(800, vSize); spacing(-vSize / 27); ctx.fillStyle = S.ink;
  verdictLines.forEach((line, i) => ctx.fillText(line, inL, verdictTop + Math.round(vSize * 0.82) + i * vLine));
  font(400, 42); spacing(0); ctx.fillStyle = S.ink;
  reasonLines.forEach((line, i) => ctx.fillText(line, inL, reasonTop + 40 + i * 58));

  // under the card: where to get your own
  const footY = cardY + cardH + 14 + 96;
  font(800, 64); spacing(-2); ctx.fillStyle = S.ink; ctx.fillText("sidefrog.com", L, footY);
  font(400, 34); spacing(0); ctx.fillStyle = S.muted;
  ctx.fillText("Free advice from a frog with no stake in your idea.", L, footY + 54);
  return c;
}

async function shareVerdict() {
  const r = shownReport, btn = $("#share-verdict");
  if (!r) return;
  const label = "Share Frank\u2019s verdict";
  btn.textContent = "Making the card\u2026"; btn.disabled = true;
  // safety net: if anything still stalls, the button comes back instead of hanging
  const stuck = setTimeout(() => { btn.textContent = label; btn.disabled = false; setStatus("That took too long. Try again."); }, 15000);
  try {
    const canvas = await drawShareCard(r);
    const blob = await new Promise((ok) => canvas.toBlob(ok, "image/png"));
    const file = new File([blob], "frank-verdict.png", { type: "image/png" });
    // The share sheet only on phones and tablets: on desktop it can open behind the window or not at all
    const touch = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;
    clearTimeout(stuck);
    if (touch && navigator.canShare && navigator.canShare({ files: [file] })) {
      try {
        await navigator.share({ files: [file], title: "Frank's verdict", text: `Frank's verdict on my idea: ${verdictLink(r)}` });
        track("share", { verdict: r.verdict, method: "share_sheet" });
      } catch (e) { if (e.name !== "AbortError") throw e; }
    } else {
      const url = URL.createObjectURL(blob);
      const a = Object.assign(document.createElement("a"), { href: url, download: "frank-verdict.png" });
      document.body.append(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 4000);
      track("share", { verdict: r.verdict, method: "download" });
      btn.textContent = "Saved. Post it anywhere.";
      setStatus("Frank's verdict was saved as an image.");
      btn.disabled = false;
      setTimeout(() => { btn.textContent = label; }, 2500);
      return;
    }
  } catch (e) {
    setStatus(e && e.message === "no-frank" ? "Frank's picture didn't load, so there's no card yet. Try again in a moment."
                                            : "Couldn't make the image. Try again.");
  }
  clearTimeout(stuck);
  btn.textContent = label; btn.disabled = false;
}

// ---------------------------------------------------------------------------
// Shared verdict links: sidefrog.com/#v=... carries the idea, verdict, reason and
// cheap test inside the link itself. The part after # is never sent to the server
// and never stored; opening the link shows that exact card, with no new check.
// ---------------------------------------------------------------------------

const b64urlEncode = (s) => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const b64urlDecode = (s) => decodeURIComponent(escape(atob(s.replace(/-/g, "+").replace(/_/g, "/"))));

function verdictLink(r) {
  const data = { i: String(r.re || r.idea || "").slice(0, 160), v: r.verdict, r: String(r.verdictReason || "").slice(0, 300),
                 t: String(r.firstMove || "").slice(0, 220) };
  // /verdict/ is the same page with its own link preview ("Frank's verdict is in"), so the
  // preview never shows the home card's sample verdict as if it were this one
  const base = location.protocol === "file:" ? "https://sidefrog.com/verdict/" : `${location.origin}/verdict/`;
  return `${base}#v=${b64urlEncode(JSON.stringify(data))}`;
}

function readSharedVerdict() {
  const m = location.hash.match(/^#v=([A-Za-z0-9_-]+)$/);
  if (!m) return null;
  try {
    const d = JSON.parse(b64urlDecode(m[1]));
    if (!d || !VERDICT_LABEL[d.v] || d.v === "cant_help" || typeof d.i !== "string" || typeof d.r !== "string") return null;
    return { idea: d.i.slice(0, 160), verdict: d.v, reason: d.r.slice(0, 300), test: typeof d.t === "string" ? d.t.slice(0, 220) : "" };
  } catch { return null; }
}

// Show a shared verdict in the example card's place: same memo, marked "Shared".
function showSharedVerdict() {
  const s = readSharedVerdict();
  if (!s) return;
  history.replaceState(null, "", location.pathname + location.search);   // keep the address clean
  const card = $("#example");
  card.dataset.verdict = s.verdict;
  card.setAttribute("aria-label", "A shared answer from Frank");
  const memo = card.querySelector(".you-wrote");
  memo.replaceChildren();
  const row = (label, text, tag) => {
    const r = el("span", { className: "memo-row" });
    r.append(el("span", { className: "re" }, label), text);
    if (tag) { r.append(" "); r.append(el("span", { className: "example-tag" }, tag)); }
    return r;
  };
  memo.append(row("FROM: ", "Frank"), row("RE: ", s.idea, "Shared"));
  card.querySelector(".verdict:not(.loading-verdict) .verdict-text").textContent = VERDICT_LABEL[s.verdict];
  card.querySelector(".reason").textContent = s.reason;
  const frog = card.querySelector(".sticker .frank");
  if (frog) frog.dataset.mood = VERDICT_FACE[s.verdict] || "smirk";
  const foot = card.querySelector(".example-foot");
  foot.replaceChildren();
  if (s.test) {
    const t = el("span", { className: "shared-test" });
    t.append(el("span", { className: "label-caps" }, "Cheap test"), s.test);
    foot.append(t);
  }
  const go = el("button", { type: "button", className: "text-btn shared-go" }, "Check your own idea");
  go.addEventListener("click", () => {
    const box = $(".plate");
    box.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });
    setTimeout(() => $("#idea-input").focus({ preventScroll: true }), reducedMotion() ? 0 : 450);
  });
  foot.append(go);
  card.classList.add("is-shared");
  track("shared_view", { verdict: s.verdict });
  // they came for this card: bring it into view
  requestAnimationFrame(() => card.scrollIntoView({ behavior: "auto", block: "center" }));
}

async function copyVerdictLink() {
  const r = shownReport, btn = $("#copy-verdict-link");
  if (!r) return;
  const link = verdictLink(r);
  try { await navigator.clipboard.writeText(link); }
  catch { window.prompt("Copy this link:", link); }
  track("share", { verdict: r.verdict, method: "copy_link" });
  btn.textContent = "Link copied";
  setStatus("Link copied. Paste it anywhere.");
  setTimeout(() => { btn.textContent = "Copy link"; }, 2200);
}

// ---------------------------------------------------------------------------
// Wire up
// ---------------------------------------------------------------------------

function init() {
  const input = $("#idea-input");
  $("#share-verdict").addEventListener("click", shareVerdict);
  $("#copy-verdict-link").addEventListener("click", copyVerdictLink);
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

  showSharedVerdict();   // a shared link (#v=...) shows that card in the example's place
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
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();
