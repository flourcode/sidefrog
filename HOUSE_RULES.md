# SideFrog house rules

Paste this file at the start of any AI session that works on SideFrog. It's the point of view; the README has the technical detail. If a request conflicts with these rules, say so instead of quietly following the request.

## What SideFrog is

A free side hustle idea checker for burned-out office workers, plus the Break Room: short guides for testing, naming, selling and building a small idea. It's made by Mark Flournoy (retired early from Amazon, mentors salespeople, also runs QuotaBird). The site should feel like a 1970s office manual that somehow became interactive: warm, plainspoken, useful first, funny second. The mascot is Frank, a frog with a coffee mug.

The point of view, in one line: Frank is comfortable telling you not to spend money.

The tagline: "Free advice from a frog with no stake in your idea." It leads the home page title, its search and share descriptions, and `llms.txt`; use it in social bios too. It lives in those places, not under the logo.

## Voice

- Useful first, mildly disgruntled employee second, frog third. About one dry office aside per page, never explained.
- The coffee test: would Mark say it to one person over coffee? If it reads like website copy, rewrite it.
- Second person in guides ("you"). Mark's "I" only on About and What it costs.
- Contractions always. No em or en dashes anywhere.
- Banned patterns: "X isn't Y. It's Z." reversals, paired punchlines, "X, not Y." lines, counted setups with bold lead-ins ("three things..."), quotable closing lines that restate or sell, literary metaphors, the same device used twice.
- Banned words: leverage (verb), navigate, robust, seamless, crucial, ensure, unlock, empower, landscape, journey, delve.
- Facts that change (prices, laws, tools, studies) get a source link and a "last checked" date. Examples with invented numbers are labelled as made up.
- No legal, tax or financial advice. Point to an accountant, lawyer or trademark attorney in one plain line.

## Frank

- He's Frank. Never "Frank the Frog," never a biography, never an explanation of the pun. About introduces him in one line and that's it.
- He appears as: the memo header ("FROM: Frank / RE: your idea"), each guide's note card with its own Frank line (no line used twice), and the sip animation.
- Frank lines in use: Let me be Frank · Frankly · Just being Frank here · I'll be Frank · A note from Frank · Frank's take · Frank has notes · Frank would like a word · Frank ran the numbers · Frank, off the record · Frank's two cents · Frank, speaking as a friend · Frank, between sips · From Frank's desk · Frank, at the water cooler.
- Frank is never cropped into a circle or avatar; the round crop is for Mark, the human. Wherever Frank (or Mark's portrait) sits beside text, the text flows around him, the way the About portrait works (text curves around Mark's circle; Frank keeps an even gap, since his outline is nearly straight): he floats top left and the lines wrap back to full width below. Not a fixed column beside him. The one exception is the answer card, whose layout keeps the verdict headline on one line.
- His face carries the verdict's mood. Don't add status colours or tags to do that job.

## Look

- Warm mid-century editorial brutalism: toasted paper, ink, avocado, burnt orange. Black type does the heavy lifting; colour is punctuation.
- Tokens: page `#FBF7EF`, cards `#FFFDF9`, ink `#1F241F`, muted `#5A5A4A`, rules `#A89B84`, Frank `#8DAA3F`, button `#97AE43`, deep green labels `#4A5C34`, burnt orange accents `#A4501F`, links teal `#2F6F73`. All verdict headlines are ink.
- One typeface: Bricolage Grotesque. Small caps labels, hairline rules, ink outlines, hard offset shadows. The masthead has two small caps section links (Break Room, Side Kit), never more, so they fit on one line on any phone; the "Price: free" box was retired to give that space to navigation, and its promise moved under the Check it button.
- One filled button per screen. Rows over boxes. One left edge.
- Tips, asides, prompts and example messages in the guides all use the same plain 3px vertical rule in the rule colour (`#A89B84`), no box, no rounded corners, no coloured edge. Asides are muted grey; prompts and messages people copy stay full ink.
- Mark's photo: `mark-mono.jpg`, a small round portrait in warm sepia (the site's ink colour for shadows, a warm paper a shade deeper than the page for highlights, so the circle reads without a border). On About it sits at the top beside the headline with the text wrapping around the circle, as on QuotaBird; the What it costs card uses the same image. Never full colour, never a rectangle, never a heavy border.
- Tried and dropped, don't bring back: per-verdict colours, halftones and grain, gradients and glows, a front-of-body forearm on Frank, a separate loading Frank, a second typeface, a colour headshot, a rectangular portrait mid-page, decorative office ephemera (stamps, punch holes, fake form fields).

## Trust

- No affiliate links. Porkbun is the registrar we point to, and the domain guide says SideFrog's own domains are on Route 53.
- Never urgency, fake proof, fake reviews or invented numbers. No "grab it fast."
- Verdict-aware: on "Keep your day job" there are no registrar links and no help offer; Mark's help offer only follows a promising verdict.
- Sharing is the visitor's choice and happens in their browser: the share card is drawn client-side and nothing is stored. Shared verdict links carry the idea, verdict, reason and cheap test after the # (sidefrog.com/#v=...), which browsers never send to the server; opening one shows that exact card with no new check, and analytics records the page without the #. Never add server-side saving of ideas or public result pages without changing the privacy copy and asking first.
- Privacy copy must match the code: the idea goes to Gemini to write the verdict; SideFrog doesn't store it; analytics never sends typed text. If logging is ever added, the copy changes too.

## UX

- Show value before any ask (the example answer is on screen from the start).
- The answer card follows the decision path: verdict, why, then a cheap test (the lead) with its pass/fail pair (keep going if, rethink it if), then context (watch out for, who pays, sharper version). Names stay visible: they're part of the fun. Emphasis comes from type size and the vertical rule, not tinted boxes.
- The tool asks for the visitor's own idea: "YOUR IDEA", "Check my idea", grey examples marked "e.g." that rotate as inspiration and are never checked. An empty click gets a quiet nudge ("Give me something to work with.", a small shake, the cursor kept in the box), not an error. No example chips or "try the example" links.
- Feedback about the idea box appears inside the box (the status line under the button), never below it where a phone keyboard would hide it.
- Every action gets feedback. Mobile first from 320px, nothing sideways, 44px touch targets.
- Respect reduced motion everywhere. Readable contrast (WCAG AA) in light and dark.
- No inline scripts or inline event handlers (the Content-Security-Policy blocks them).

## Definition of done

Built isn't the finish line. Before something ships:

1. Use it like a visitor would, on a phone and on a desktop. Does it solve the problem? Where did you hesitate?
2. Read every new line against the voice rules above.
3. Run `python3 make_pages.py` (pages, sitemap, fingerprints, footer), and `python3 make_og.py` if a title changed.
4. Check every internal link works and nothing scrolls sideways.
5. Go one detail further than anyone will notice. People feel the care even when they can't name it.

## Frank's art
- Frank is traced from Mark's approved reference art, never hand-drawn or redrawn by AI. New poses or faces start as a generated sheet in the same style, approved by Mark, then traced.
- Avocado green (#8DAA3F family), not lime. No teardrop, ever. No heavy-lidded "jaded" lids.
- Verdict faces: Surprisingly, yes = surprised "o"; This could work = the sip's first frame (smile); Crowded pond and Keep your day job = heavy lids, flat mouth; Can't help = puzzled; Error and 404 = skeptical frown.
- Frank's gaze (data-look): where he's talking or greeting (logo, guide notes, Side Kit, About, 404) he looks straight at the reader and glances at his text only while sipping; on the answer and example cards he looks at the verdict. Every sip starts and ends on his resting gaze. Any new placement sets data-look.
- Round Frank for identity and sharing (About, share cards, the share-your-verdict image, backgrounds, profile pictures, video); cutout Frank beside text on the site. Both come from frank_art.py, never drawn by hand.
- Frank's pupils stay exactly as traced (100%); smaller pupils were tried and rejected.
- RE on the answer card is a short memo subject line from Frank, never a wrapped paragraph; Frank sits level with the verdict.
- Plainspoken copy with no AI hallmarks: no punchy three-part lists, no "Maybe X. Maybe Y." fragments, no colon setups, no clever closing lines. Short, plain sentences in Mark's voice.
- Portraits that text wraps around have no captions (captions turn them into blocks).
- Shared verdict links use /verdict/#v=...: the verdict stays after the #, and the link preview is the neutral "Frank's verdict is in" card, never a sample verdict.
- Editorial pages: labels, numbers and thin rules instead of cards; the italic serif only for one-line descriptions and pull lines. Every new guide gets a one-line description in BLURBS.
- No made-up numbers anywhere, including joke statistics. "Frank's week" shows only real verdict counts.
- Text next to Frank flows around his outline (shape-outside), never in a block beside him: the traced polygon for cutout Frank, a circle for round Frank.
- Brand tagline: "For people who hate Mondays." (share cards, footer signature, About, video end card, social bios). Never explain it. "Free advice from a frog with no stake in your idea." stays where a reader needs to know what SideFrog is: page titles, search descriptions, the share-your-verdict image. Avoid "I hate Mondays" on merchandise (Garfield's line).
- In the Shorts, Frank's faces are the traced originals on every screen; no moved-pupil variants.
