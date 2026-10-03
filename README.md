# SideFrog

**Start here: [`HOUSE_RULES.md`](HOUSE_RULES.md).** It's SideFrog's point of view and standards on one page (voice, Frank, look, trust, UX, definition of done). Paste it at the start of any AI session working on the site, so the AI builds to SideFrog's standards instead of its own defaults. This README is the technical reference behind it.


A casual, 10-second gut check for side hustle ideas. The kind of tool someone opens on a break, tries three or four ideas in, and comes back to next week.

Type an idea, get one answer card:

- **A verdict:** Surprisingly, yes / This could work / Crowded pond / Keep your day job, or (for illegal or harmful ideas only) Can't help with that one, with a one-line reason. The frog mascot on the card changes its face to match and does one little hop when the answer lands (skipped for people who prefer reduced motion).
- **The sharper version** of the idea, **who pays**, and **what to try first** this week.
- **Names with an open .com.** Gemini suggests 12 brandable names, and the Lambda checks every .com live at the registry in the same request. Only open ones are shown, with a Register link. Near-duplicates (MeowLens and MewLens, Purrshot and Purrshots) are dropped before checking, and the prompt rules out dropped-vowel spellings like "KittnArt".
- **The name you picked.** If the idea mentions a name ("…call it SideFrog.com", "I'd call it Purrshot"), it's checked first and always shown, whether it's open, taken (with the year it was registered) or couldn't be checked, along with a one-line take on the name. A typed domain is read straight from the text, so the exact ending is checked (.com, .app and others in the IANA directory; "Node.js" doesn't count). A name without a domain is picked out by Gemini and checked as .com. Suggestions too close to their name are dropped.
- **See what's already out there:** 5 related search phrases, each a link to Google results, so people can size up the competition themselves.
- **Try one of these instead:** 3 other ideas on the same interest. One click checks the next one.

Weak or vague ideas are never a dead end. The AI reshapes them into the nearest workable version and says why.

Starting a new idea is one move: after a result, clicking into the box selects the old idea so typing replaces it. **Clear** (or Escape) empties it, and **Check another idea** at the bottom of the card jumps back up with an empty box.

**About the name:** the product is SideFrog, and since the move to its own Lambda function the code and settings say so too (`lambda/index.mjs`, `GEMINI_MODEL`). The project folder is still called `namercheck/`, which doesn't matter to anyone.

**The mascot is Frank, the coffee frog** (licensed sticker art, vectorized). He's drawn in layers: `frogs/coffee-body.svg` (body, with the chest behind the mug redrawn), inline SVG faces (one per mood plus the sip face), `frogs/coffee-mug.svg` and `frogs/coffee-mug-tilt.svg`, and an arm that shows during sips. See The sip and The tilted mug below.

| Verdict | Face |
|---|---|
| Surprisingly, yes | happy closed eyes, big laugh |
| This could work | open eyes, easy half-smile |
| Crowded pond | wide eyes, flat mouth |
| Keep your day job | open eyes, one skeptical raised brow, frown |
| Can't help with that one | worried, with a tear |

Two more faces cover the rest of the page: **thinking** (eyes up, wavy mouth, while the AI works) and **oops** (errors).

**The sip:** Frank is layered: his arm (behind the body, 80px of green plus a 10px outline, matched to his other arm), his body (`frogs/coffee-body.svg`, with the chest behind the mug redrawn), his faces, and the mug. During a sip the arm grows out from his shoulder so the elbow shows out to the side, holds while he drinks, and folds away as the mug comes down. A front-of-body forearm was tried and retired: it looked detached and the wrong size. Every sip (loading loop 3.2s, landing 1.5s, idle 2.6s) follows the same arc: a small dip before the lift, the lift, the tilt deepening slightly while he drinks, then the mug comes down with a soft settle. His eyes close as the mug reaches his mouth. Reduced motion: no sip.

**Where he looks:** his pupils are their own layer, aimed with `look-left` / `look-right` so he always looks at what he's reacting to. In the header he glances right at "SideFrog". On the answer card he sits to the right of the text and glances left at it, with the mug on that side, as if sipping while he reads your idea. He isn't mirrored, which keeps the artwork as drawn. To change where he looks, swap the class; to add a face, add a mood in the inline SVG plus one CSS line.

The verdict itself is the card's headline (Bricolage Grotesque 800, uppercase), with the frog beside it. The frog is a transparent cut-out with no sticker border, so he sits directly on whatever background he's on, light or dark. He sips and settles on each new answer. `frogs/favicon.svg` is a self-contained copy used for the browser tab, since favicons can't load other files. `sidefrog-stickers.zip` has every coffee-frog face looking left and right (Surprisingly, yes has closed eyes, so it comes once) as SVG and 1024px PNG.

## Content pages (the Break Room)

Built by `make_pages.py` from the copy inside it. **Edit the copy there, then run `python3 make_pages.py`. Never edit the built `index.html` files under `break-room/`, `about/` or `what-it-costs/`.** The script also writes `sitemap.xml`, `robots.txt` and `llms.txt`.

| URL | Page |
|---|---|
| /break-room/ | The hub |
| /break-room/start/test-an-idea-in-a-week/ | Test a side hustle idea in a week |
| /break-room/start/is-anyone-searching-for-this/ | Is anyone searching for this? |
| /break-room/start/size-up-the-competition/ | Who's already doing it? |
| /break-room/name/check-if-a-business-name-is-taken/ | How to check if a business name is taken |
| /break-room/name/how-to-buy-a-domain/ | How to buy a domain |
| /break-room/launch/getting-found-by-ai-answers/ | Getting found when people ask AI instead of Google |
| /break-room/sell/first-ten-customers/ | How to get your first 10 customers (7 numbered steps: 30 names, a specific customer, a short honest message with an example to adapt, follow up twice, ask for the sale, do the work by hand, turn each customer into the next; "Frank, off the record"; one line offering Mark's time, since sales is his field) |
| /break-room/sell/what-to-charge/ | What should I charge? (6 numbered steps: going rate, your floor, value to the customer, a simple structure, say it plainly, honest founding prices; then an unnumbered worked example with made-up numbers; "Frank’s two cents"). Taxes get one line pointing to an accountant, nothing more. |
| /break-room/leap/before-you-leap/ | Before you leap (6 numbered steps: build the safety net, price out what your job quietly pays for (COBRA vs HealthCare.gov, sourced), let the side hustle prove itself with a "leap number", talk to the people it affects, decide your checkpoint, leave well; "Frank, speaking as a friend"). General guidance with one "not financial advice" line pointing to a fee-only planner; one line on having employment paperwork read by a lawyer. First in the home guide list, and "Read next" after a Surprisingly, yes verdict. |
| /break-room/build/vibe-coding-101/ | Vibe coding 101: build the ugly first version (8 numbered steps: one sentence, brief it with a point of view, smallest thing that works, one change at a time, use it like a customer, save your work, write a handoff before the chat runs out (with copyable prompts to write HANDOFF.md and to start the next chat from it), put it online; "Frank has notes") |
| /break-room/build/before-you-put-it-online/ | Before you put it on the internet: keys, spending limits, rate limits, user input and prompt injection, collecting less, free protections, backups ("Frank would like a word"; help box) |
| /break-room/build/six-users-now-what/ | Six people use it. Now what? Error alerts, the weekly bill, what to count, adding pieces only when needed, when to stop vibe coding ("Frank ran the numbers"; help box) |
| /break-room/start/test-a-big-idea-small/ | Test a big idea small (7 numbered steps for food trucks, shops and other in-person businesses: shrink it to one Saturday, check your health department first (cottage food rules, sourced), rent before you buy, sell where the crowd already is, pre-orders, count everything, repeat before you scale; "Frank, between sips") |
| /side-kit/ | The Side Kit: ten copyable prompts by stage (Test it, Money, Sell it, Build it, Leap), each with "You'll get" and "Watch out", copy buttons via `side-kit.js` ("From Frank's desk") |
| /side-kit/leap-worksheet/ | The Leap Worksheet ("Form SF-1"): a printable form (monthly number, what the job pays for, safety net, leap number, checkpoint, first test, 30 names, signed, "Reviewed by Frank."). Print button and `side-kit/leap-worksheet.pdf` (one Letter page, made by `make_og.py` from the print styles) |
| /about/ | About SideFrog (Mark, first person) |
| /what-it-costs/ | What it costs me to test an idea (Mark's real bills; its card is labeled "My usual costs" with Mark's photo, since Mark is the one talking) |

Every guide opens with a note from Frank (each guide has its own Frank line), uses one office aside, ends with a "Check your idea" box, a visible FAQ (with matching FAQPage structured data), Read next rows and dated sources. Voice rules are at the top of `make_pages.py`. SideFrog stays out of legal and tax advice; those guides are parked on purpose.

**The idea box's grey example rotates** every 3.5 seconds through realistic side hustles with the odd weird one, so people see any idea is fair game: website tune-ups for local restaurants, travel planning for busy families, estate sale flipping on weekends, LinkedIn coaching for executives, cruise broker, candles that smell like the office (`EXAMPLES` in `app.js`). It holds still while someone is in the box or has typed, while the tab is in the background, and for reduced motion. The box is sized to the longest example, so its height never jumps as they rotate. The grey text is `#66614F` (6.1:1, readable but clearly not typed text). None of the examples is the example answer card's idea (pet turtles), so a live answer never contradicts the card beside it.

**Clicking Check it with an empty box** checks whichever example is showing at that moment, instead of an error. It moves into the box as real text, Clear appears, and clicking the box selects it so typing replaces it. A one-letter entry still gets "Type an idea first. Half-baked is fine."

**"Or try:" chips:** bookkeeping for side hustlers (an office skill you already have), home tech help for boomers (an ordinary problem people pay to make go away), candles that smell like the office (yes, dumb ideas are allowed). The label stays plain.

**Frank thinks in the answer card:** while a check runs, the card already on screen (the example on a first check, the last answer after that) shows "FROM: Frank / RE: your new idea", the headline "SIPPING ON IT…" and Frank sipping on a loop; after 4.5 seconds a note adds "Circling back on the .com names…". On desktop that's the right-hand column beside the input; on phones it's the card under the input, scrolled into view if needed. The answer replaces it as before, and a failed check puts the card back exactly as it was. The old separate loading Frank under the input is gone; its messages are still announced to screen readers through a visually hidden live region.

**Google's "unusual traffic" page:** the "See what's already out there" links are ordinary Google searches. Google shows its robot check when it sees many searches from one network in a short time (VPNs, office networks, or a development laptop running lots of test searches). It's tied to the visitor's network, not the link, and clicking "I'm not a robot" clears it. Most visitors won't see it.

**The tilted mug:** each Frank carries the original mug (`frogs/coffee-mug.svg`) and a tilted one (`frogs/coffee-mug-tilt.svg`): the original artwork edited and retraced with Frank's own settings, so the rim and coffee flatten into a thin oval and a soft band shows the underside, with no extra inked line. The tilted mug fades in on top during the fast part of the lift while the original stays solid underneath, so nothing is ever see-through (checked at every 1% of all three sips in Chromium). It stays loaded but invisible between sips so it never pops in late.

**Frank sips now and then:** `frank.js` (about 1KB) picks one on-screen Frank every 9 to 23 seconds and he takes a 2.6-second sip: the header Frank, the example-answer Frank, the answer Frank (after his landing sip) and the Frank on each guide's note card. One at a time, only when he's visible (IntersectionObserver), never in a background tab, never with reduced motion. The loading Frank keeps his own sip loop and isn't picked. The animation is CSS transforms inside Frank's own box, so nothing on the page moves. Every Frank is the same inline markup (body, faces, arm, mug layer), which also means guide pages no longer load the 18KB favicon for their Franks.

**Viewing it on your desktop before launch:** unzip the site anywhere and double-click `index.html`. Every path is relative, so styles, the frog and all links work straight from disk, and a small script makes folder links open their `index.html` when you're browsing files (it does nothing on the live site). The guides, About, What it costs and the example answer all work this way.

The live idea check is the one thing that won't work from disk as-is. A page opened from disk has no web address, so the browser reports its origin as "null", and the Lambda Function URL only answers the sites listed in its CORS settings. While you're developing, either add `*` to Allow origins in the Function URL's CORS settings and put it back to your real domains before launch, or add your Amplify preview address to that list and test there. Until then, a check from disk shows the "couldn't reach" message rather than an answer.

**Help links:** people who want help are pointed to Mark's Calendly (`calendly.com/markflournoy/vibe-code`, tagged `utm_source=sidefrog` and the page they came from) or his LinkedIn. They appear as plain links under the prompt kit on positive answers, as a line in every guide's "Check your idea" box, as "Get help" in every footer, and as a Want help? section on About (`/about/#help`), which is the only place it gets a filled button.

**Layout note:** the two-column desktop layout (headline and input left, example answer right) applies to the tool page only (`body:not(.page) main`). Article pages carry `class="page"` and keep one 46rem reading column, with the header and footer at the same width so everything shares one left edge.

**UX notes from the design references:** kept what helps the person using the site: value before any ask (the example answer), specific labels, feedback on every action (Copy is also announced to screen readers), emphasis by difference with one filled button per screen, 44px targets and clear focus states. Left out on purpose: fake social proof, urgency and other conversion tricks that work against the visitor.

## Editorial details (warm mid-century editorial brutalism)

- **Grid:** on desktop the example answer card's top edge lines up with the idea box, two columns starting on one line (`"form example"` in the grid areas), instead of floating centred.
- **Manual-style numbering:** guides that are real sequences carry `numbered=True` in `make_pages.py`, which numbers their step headings (1., 2., 3. in burnt orange). A heading that isn't a step (like a worked example) uses `<h2 class="unnumbered">` and is skipped. Test an idea in a week (6 steps) and Who's already doing it? (5 steps; its "No competition is the warning sign" note sits inside step 1). Guides that aren't sequences stay unnumbered.
- **Colophon:** every footer ends like the back page of a manual, in Mark's voice (see The footer below). The date is `UPDATED` in `make_pages.py`, and the build applies it everywhere.
- **Left alone on purpose:** more colours, textures or halftones, thicker borders or bigger shadows, and decorative office ephemera (stamps, punch holes, fake form fields). The memo header, price box and small caps labels are enough paper.

The idea box sizes itself to the grey example while empty (on load, once the font loads, and on resize), so the example is never cut off at any width.

## Build it yourself

A Break Room section for office people getting a small idea online safely: make it, don't expose yourself, don't overbuild it. It uses SideFrog itself as the worked example (the Gemini key lives in the Lambda, six checks a minute and forty an hour per visitor, the stored-nothing privacy promise, $8 a month). The security and scaling guides end with a "When to get real help" box (payments, sensitive data, logins, kids, real customers depending on it: "That's where you stop being cheap.") with Mark's Calendly and LinkedIn. That's the one place on the guides where Mark's help is offered by name, after the free advice rather than instead of it. The colophon's "you can probably build your thing too" links to Vibe coding 101.

## Against "zombie UI" (from Katie Dill's talk, Stripe)

- **Point of view in the user's prompt:** the "Build the page" prompt asks for what you believe about the work, how it should feel, a look you like and one detail only someone in your business would think of; it rules out the generic startup template look (gradient hero, stock icons, emoji) and ends with a skeptical-customer critique pass ("list the five things that feel generic or unfinished, and fix them").
- **Standards encoded for the machine:** `HOUSE_RULES.md`.
- **Done is not the same as good:** Vibe coding 101 has a step for it ("Use it like a customer before you call it done") and a FAQ on why AI-built sites look alike.
- **A detail that shows care:** the browser tab reads "Sipping on it… · SideFrog" while Frank thinks and then the verdict ("Keep your day job · SideFrog"), so people who switched tabs see the answer landed. It shows only the verdict, never the idea, so nothing typed lands in browser history; a failed check puts back whatever the tab said before.

## Selling advice taken from a premium-brands talk (and what was left out)

From a talk on how premium e-commerce brands justify their prices, four plain ideas were kept and folded into existing pages:
- **Describe the buyer by what they believe and won't put up with**, not income (first customers, step 2), and ask every customer "What almost stopped you from buying?" (step 7), because that's the worry the page should answer.
- **Name the awkward first week before it happens** (first customers, step 6), so customers read it as expected.
- **Contain discounts and package the offer** (pricing: how the offer is described changes what people compare it to; FAQs on discounts with clear limits and on specific guarantees).
- **Proof answers one specific worry with real evidence**, so the "Build the page" prompt asks for the worry and puts a direct answer above the button: a before-and-after, a real customer's words with permission, or a specific guarantee. Invented testimonials stay banned.

Left out on purpose: income-based targeting, ad-agency tactics, subscription lock-in, an unsourced promotions-per-year figure, and the pitch. None of it fits SideFrog's readers or trust rules.

## Two answer fields borrowed from the old Sifter

The Lambda returns two more short lines, both shown in the answer's facts list after "Try this first":
- **`goodSign` ("Good sign")**: the countable result from this week's test that says the idea is working, e.g. "3 shops say yes to a paid second month". It does step 1 of "Test an idea in a week" (decide what yes looks like) for the reader.
- **`watchOut` ("Watch out for")**: the single thing most likely to sink it (a big free competitor, insurance or liability, platform rules, personal data, payments, a slow first test), stated without legal, tax or financial advice. When the model says "Nothing obvious", the row is skipped.

The prompt also has the Sifter's "not a clone" rule: when similar things exist, the sharpened idea must be narrower, simpler or aimed at a different buyer. Both fields are in the response schema, cleared for "can't help", capped at 160 and 180 characters, and add about 40 tokens to a typical 400-token answer (limit 1,024), so Flash-Lite isn't strained. Deliberately not borrowed: keyword demand guesses (guesses dressed as data), named communities for first customers (the model invents subreddits), scores, stack fit and weekend build plans. The site and Lambda can be deployed in either order: an older Lambda just means the two rows don't appear.

## Trust rules in the answer

- **Names are verdict-aware.** On SURPRISINGLY, YES, THIS COULD WORK and CROWDED POND, open names link to Porkbun ("Register ↗") with a calm note: "These were open when we checked. If one sticks, confirm it at the registrar before you get attached." On KEEP YOUR DAY JOB they show for reference only, with no registrar link, and Frank says "I wouldn't buy anything yet." No urgency language anywhere.
- **Mark's help offer only follows a promising verdict** (SURPRISINGLY, YES and THIS COULD WORK). After KEEP YOUR DAY JOB or CROWDED POND, the next step is the free guide in "Read next", not a pitch.
- **Privacy wording is precise.** The promise under the button says "Your idea isn't saved"; the fine print says the idea goes to Google's Gemini to write the verdict and SideFrog itself doesn't store what you type. That's accurate: the Lambda writes nothing to its logs (no `console.log` of requests), and analytics never sends typed text. Keep it that way: if you ever add logging to the Lambda, don't log the idea, or change this copy.

## Security headers

`customHttp.yml` sends, on every response: `Strict-Transport-Security` (https only, a year), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, a `Permissions-Policy` that turns off camera, microphone, location, payment and USB, and a strict `Content-Security-Policy`: scripts, styles and requests only from the site itself, Google Fonts, the SideFrog Lambda URL and (when on) Google Analytics; no inline scripts, no framing. Tested under enforcement with the full flow (fonts, Frank, a check, the prompt kit, a guide, analytics switched on) with zero violations. Because inline scripts are blocked, the desktop-viewing helper lives in `local-links.js`. **If you add an outside service (a new API, an embed, another analytics tool), add its address to the policy in `customHttp.yml` or the browser will block it.** The Lambda's per-IP rate limits are the first line against abuse; add AWS WAF or tighter throttling if traffic grows.

## Structured data and the sitemap

The tool page has `WebApplication` data (free, by Mark); guides have `Article`, `FAQPage` (matching the visible FAQ) and `BreadcrumbList` (SideFrog › Break Room › guide); About has `Person`. Sitemap `lastmod` comes from each page's `updated` field in `make_pages.py` (default: the guides' last-checked date) and `HOME_UPDATED` for the tool page, so rebuilding the site doesn't claim every page changed. Bump a page's `updated` when you edit its copy.

## The stylesheet

Each Frank animation is defined once (the final versions); retired parts (the separate loading Frank, the front forearm) and rules fully overridden later were removed in a cleanup that was verified two ways: every sip animation (idle, thinking, landing) is identical before and after, and home, a guide, About and a full answer render pixel-identical on desktop and phone.

## Updating the site (cache busting)

**The routine: edit, run `python3 make_pages.py`, zip, deploy.** Always run the build before deploying, even if you only touched `styles.css`, `app.js`, `frank.js`, `analytics.js` or an image. The build stamps every reference to those files with a fingerprint of their contents (`styles.css?v=b4c6dbb4`). Change a file and its fingerprint changes, so returning visitors' browsers fetch the new version; unchanged files keep coming from cache. It stamps the tool page (`index.html`) as well as the generated pages.

`customHttp.yml` sets the matching caching: HTML is always revalidated (`no-cache`), so a deploy shows up on the next visit; stamped CSS, JS, SVG, PNG and `mark.jpg` are cached for a year. Share cards, `favicon.ico`, the manifest, `sitemap.xml`, `robots.txt` and `llms.txt` get short lifetimes because apps request them by fixed name. With Git-based Amplify deploys the file is picked up from the repo root; with manual zip deploys, paste the same YAML into Amplify > Hosting > Custom headers. It's the same approach as QuotaBird.

## The footer

One template in `make_pages.py` (`FOOTER`) for every page, including the tool page: the build swaps it into `index.html`, so the two can't drift. It has the tagline, links separated by middle dots (Break Room, What it costs, About, Get help), THE FINE PRINT (what the verdict and the .com check are, not legal, financial or trademark advice, nothing you type is saved), and the COLOPHON in Mark's voice, ending "Updated October 2026" from `UPDATED`.

## Amplify rewrites and redirects

`make_pages.py` writes `amplify-redirects.json` on every build: first, a 301 from `https://www.sidefrog.com` (and any path under it) to the same path on `https://sidefrog.com`, so www always ends up on the bare domain; then a 301 from each page's address without the trailing slash to the one with it (`/about` to `/about/`), then a last catch-all that serves `404.html` with a real 404 status for any address that doesn't exist. New pages get their redirect automatically.

To install: Amplify console, your app, **Hosting > Rewrites and redirects > Manage redirects**, open the JSON editor, replace everything with the contents of `amplify-redirects.json`, and save. If the list had Amplify's default single-page-app rule (the long `</^[^.]+$|...>` pattern that sends everything to `index.html`), it must go: it would turn every missing page into the home page. Rerun the paste whenever you add a page. For the www rules to apply, `www.sidefrog.com` has to reach the app: in **Domain management**, make sure the `www` subdomain is listed for `sidefrog.com` (Amplify adds it by default). Amplify handles https itself. The www rules come from `BASE_URL` in `make_pages.py`, so they follow the domain if it ever changes.

`404.html` ("Frank can't find that page") is built from the same template, with root links (`/styles.css`) because it's served at whatever address was mistyped, `noindex` so search engines skip it, and links back to the tool and the Break Room. It's not in the sitemap.

**Text flows around Frank:** the guide note cards ("Frank has notes" and the rest), the What it costs card and Frank's introduction on About float Frank (or Mark's round portrait) top left with `shape-outside`, so the text wraps beside him and returns to full width underneath, like the About portrait. The answer card keeps its own layout so the verdict stays on one line.

## For the non-technical dreamer

The taco-truck reader is served by: "taco truck empire" leading the rotating examples; a rule in Frank's prompt that physical and local businesses get a small real-world first test (pop-up, market stall, catering one lunch, pre-orders, renting kitchen time) instead of a website, and that empires get sharpened to the first truck or stall; the "Test a big idea small" guide; the Side Kit (linked in the masthead, the footer and under the answer's prompt kit); and the Leap Worksheet (linked from the kit and from Before you leap). The masthead is BREAK ROOM · SIDE KIT · BUILD IT · ABOUT (Build it hides under 360px and About under 400px; both are a tap away). Deliberately not built: accounts, saved progress, a course or a community.

## Sharing, icons and analytics

**Share cards (`og/`):** 1200x630 JPGs (50 to 76KB each), one for the home page and one per Break Room page, wired with Open Graph and `twitter:card` tags (absolute URLs on `https://sidefrog.com`, which social sites require). The home card shows the question and a real answer card (FROM: Frank, RE: meal prep for pet turtles, KEEP YOUR DAY JOB); each guide card shows its title under that guide's Frank line. They're rendered from HTML with the site's own font, colours and Frank by `make_og.py`. Rerun it after changing a page title (`pip install playwright`, `python3 -m playwright install chromium`, `python3 make_og.py`), then `python3 make_pages.py`. After launch, check a link in LinkedIn's Post Inspector and Facebook's Sharing Debugger; both cache cards, and those tools refresh them.

**Icons:** `apple-touch-icon.png` (180, on cream, since iOS fills transparency with black), `favicon-16.png`, `favicon-32.png`, `favicon.ico` (16/32/48) and `frogs/favicon.svg` use a tight crop on Frank's face so he reads at tab size; `icon-192.png`, `icon-512.png` and `icon-maskable-512.png` (Frank inside the safe zone so Android can crop to any shape) are listed in `site.webmanifest`.

**Analytics (`analytics.js`):** paste your GA4 measurement ID into `GA_ID` at the top. That's the only edit. Until then it does nothing, and it only ever runs on the addresses in `LIVE_HOSTS` (sidefrog.com and www), never from your desktop. It sends page views plus: `check` (with the verdict type), `check_error`, `example_check` (an empty-box click), `prompt_copy` (which prompt), and `help_click`, `register_click`, `search_click`, `quotabird_click` for links that leave the site. It never sends the idea someone typed. In GA, under Admin > Data streams > Enhanced measurement, turn off "Outbound clicks", since those record full link addresses and the Google search links contain search phrases. If you add GA, consider a short privacy page saying so; the price box's "We don't save your idea" stays true.

**Before going live:**
- `BASE_URL` in `make_pages.py` is `https://sidefrog.com`. Change it if the site lives on another domain, then rebuild (it's used in canonical tags, the sitemap and llms.txt).
- `mark-mono.jpg` is Mark's photo as a small round portrait in warm sepia (240x240 for sharp screens, 10KB): shadows in the ink colour, highlights in a warm paper a shade deeper than the page so the circle reads without a border. On About it floats at the top beside the headline with the text wrapping around the circle (`shape-outside: circle()`), as on QuotaBird; the What it costs card uses it too. To redo it from a new photo: crop square, convert to greyscale, map shadows to `#1F241F` and highlights to `#ECE3D1`.
- Check that `https://porkbun.com/checkout/search?q=example.com` opens Porkbun's search with the domain filled in. If it doesn't, it still lands on their search page; adjust `registrarUrl` in `app.js` if you find the right pattern.
- Amplify rewrites and redirects: paste `amplify-redirects.json` (see below).
- Submit `sitemap.xml` in Google Search Console.

## Take it further (the prompt kit)

Under every answer, ready-made prompts to paste into your own Claude, ChatGPT or Gemini, built in the browser from the answer itself (nothing is sent anywhere again). Shown by verdict: Surprisingly, yes and This could work get Build the page, Talk to ten buyers and Answer the questions; Crowded pond gets Read their bad reviews first; Keep your day job gets Talk to ten buyers only; Can't help gets none. Each prompt opens in place with a Copy button, and a "Read next" link points to the matching guide. Prompt text lives in `kitPrompts()` in `app.js`. Every prompt tells the AI not to invent testimonials, reviews or statistics.

Registrar links now go to Porkbun (no affiliate), the registrar the guides recommend.

## Design system

**Style:** a mid-century palette with soft neo-brutalism: flat colour, ink outlines, hard offset shadows, and no gradients, glows, textures or halftones. Cohesion comes from applying those rules everywhere (cards, buttons, chips, the price box), not from adding a new style label.

**UI rules (checked in real Chromium on a 360px phone and on desktop):**
- **Rows:** one component for every list of actions in the answer (open names, searches, alternative ideas). Full width, text on the left, a cue on the right: "Register ↗" (registrar), "↗" (Google), or "Check" (runs that idea). Long text wraps inside the row instead of breaking a pill shape. Rows sitting side by side share a height.
- **Pills** only for short, single-line things: the example ideas under the input, which are one swipeable row on phones.
- **Touch targets:** every tappable thing is at least 44px tall (verified automatically).
- **Hover:** effects only apply on devices that really hover, so taps on phones don't leave a "stuck" lifted state. Taps get a small press instead.
- **Links that open a new tab** show "↗" and tell screen readers "(opens in a new tab)".
- **One outline language:** ink outlines on every interactive or framed element (cards, buttons, rows, chips, the price box). Hard offset shadows only on the idea box, the answer card and the main buttons.

**First screen = instant value:** on page load an **example answer** ("RE: meal prep for pet turtles. KEEP YOUR DAY JOB", with the frog and an EXAMPLE tag) is already showing. First-time visitors see what they'll get before typing. A real check replaces it.

- **Phones:** a tight hero (one-line lede, compact masthead, a single swipeable row of example ideas) puts the example verdict on the first screen. Measured in real Chromium: about 730px on a 390x844 iPhone, about 727px on a 360x740 Android.
- **Desktop (1000px and up):** a two-column hero, with the headline and input on the left and the example answer on the right. The verdict sits at about 380px on 1280x800.
- **Above the fold** there's one dry joke ("not Shark Tank"). The lede is just "Type an idea. Get a straight verdict in about ten seconds."

**Direction:** a coffee-break accomplice for corporate folks sneaking in ten minutes of side-hustle daydreaming. It's responsible adult meets tiny act of rebellion: warm, light, retro-smart, and trustworthy enough for white-collar professionals. It's deliberately about 10–15% less polished than a fintech app. Not startup-bro, not fintech, not wellness, not "AI platform".

**Palette: "Avocado Kitchen"** (vintage mid-century mod; tokens at the top of `styles.css`). Use it roughly as 60% toasted white and cream, 25% coffee black and rules, 10% avocado and olive, and 5% orange, rust and mustard. Colour lands where the meaning is: the frog, the button and the verdict.

| Token | Name | Hex | Use |
|---|---|---|---|
| `--paper` | Toasted White | `#FBF7EF` | page |
| `--surface` | Warm White | `#FFFDF9` | cards, the idea box (a shade lighter than the page) |
| `--ink` | Coffee Black | `#1F241F` | text, outlines, hard shadows |
| `--muted` | Taupe Ink | `#5A5A4A` | supporting text (5.8:1) |
| `--rule` | Olive Gray | `#A89B84` | rules, decorative |
| `--frog` | Avocado | `#8DAA3F` | Frank; never text |
| `--lime` | Warm avocado | `#97AE43` | the main button fill (ink text 6.35:1), hover `#A6BC52`; never text |
| `--deep` | Forest Olive | `#4A5C34` | labels (6.0:1) |
| `--accent-text` | Deep Burnt | `#A4501F` | "RE:" and small warm accents (4.6:1) |
| `--blue` | Atomic Teal | `#2F6F73` | links and focus rings (5.4:1) |

**Old Mustard** `#D2B24C` is reserved for small highlights; it's never text.

**Verdict colour:** every verdict headline is ink (`--ink`), like the page headline: black type does the heavy lifting and colour is punctuation. Frank's face carries the mood (skeptical, grinning, flat), so there's no per-verdict colour or status tag. Burnt orange stays on small accents like `RE:`; mustard is not used for text.

**Type:** Bricolage Grotesque throughout, loaded as one variable font. Weights by role:

| Role | Weight |
|---|---|
| Hero | 800, tight tracking |
| Headings | 700 |
| Buttons and the typed idea | 700 |
| Verdict | 800, uppercase, the biggest type on the card |
| Labels | 600 |
| Small helper text | 450–500 |
| Body | 400 |

Verdict captions are 800 uppercase.

**Components:**
- **Idea box:** the emotional centre, and deliberately not form-like: a light surface with a 2px ink outline, a 6px hard offset shadow, and large bold ink text with no ruled line. While you type, the whole box lifts and its outline turns deep green, so keyboard users still see focus.
- **Primary buttons** ("Check it", "Check another idea"): lime with an ink outline and a hard shadow. They lift on hover and press in on click. "Check it" is a size up, since it's the main action on the site.
- **Chips:** off-white pills that turn lime-tinted, ink-outlined and lift on hover. They read as "tap me, try something random".
- **Mobile first** (most visitors): on phones the frog sits on top of the verdict at the right, glancing down-left at it, and the verdict gets the full width. From 600px wide he moves beside it. The verdict is always one line, the frog's one-liner. CSS sets the largest size, and `fitVerdict()` in `app.js` shrinks it only when the line would overflow, re-fitting on rotation and once the web font loads. Checked in real Chromium at 360px, 390px and 1280px for every verdict: "CAN'T HELP WITH THAT ONE", the longest, lands at about 22px on a 360px phone. "9-to-5?" never splits across lines. On phones "Clear" sits beside the full-width "Check it".
- **Answer card:** the verdict is the star. "KEEP YOUR DAY JOB" is the card's headline (Bricolage 800, uppercase), with the reason right under it and a memo-style "RE: your idea" line above. The frog sits beside it at character size, looking left at the verdict and delivering it. Build personality through the verdicts, not extra decoration.
- **Masthead links:** BREAK ROOM · BUILD IT · ABOUT in small caps where the price box used to be (About hides under 400px; it's in the footer). The current section is underlined in burnt orange.
- **The promise:** "Free. No sign-up. Your idea isn't saved." in deep green under the Check it button, where people decide.
- **Motion:** small and physical: lifts, presses, the frog's hop, and the loading bob. All of it turns off for people who prefer reduced motion. Focus rings are a 3px blue outline.

**Frank:** the frog is Frank. Each guide opens with its own Frank line ("Let me be Frank", "Frankly", "Just being Frank here", "I'll be Frank", "A note from Frank", "Frank's take"), the answer card's memo header reads "FROM: Frank" over "RE: your idea", and the loading line is "Frank's sipping on it…". About introduces him in one line ("The frog is Frank. He reads every idea that comes in and tells you what he thinks.") beside a small sipping Frank, without explaining the pun. Otherwise Frank never gets a biography, an explanation or "Frank the Frog"; readers work out the rest. Keep him to those spots, and don't repeat a Frank line on two guides.

**Voice:** deadpan corporate absurdity. SideFrog is side-hustle validation for people who are still technically on the clock. The humour sounds like it escaped from a meeting: dry, restrained and workplace-aware, about one line per spot, never a punchline on every surface. The site itself stays polished. The frog is the one character who says what the user is thinking.

| Spot | Copy |
|---|---|
| Masthead | BREAK ROOM · BUILD IT · ABOUT (small caps links; replaced the price box) |
| Promise | "Free. No sign-up. Your idea isn't saved." under the Check it button |
| Hero | "Thinking about making the leap from your 9-to-5?" |
| Lede | "Type an idea. Get a straight verdict in about ten seconds." |
| Hint | "Half-baked is fine. This is a coffee break, not Shark Tank." |
| Empty box | "Type an idea first. Half-baked is fine." |
| Chips | "Or try:" with bookkeeping for side hustlers, home tech help for boomers, and candles that smell like the office |
| Loading | Frank thinks in the answer card: "SIPPING ON IT…", then "Circling back on the .com names…" |
| Answer card | opens like a memo: "RE: meal prep for pet turtles" |
| Footer | "Made for coffee breaks. Your manager remains uninformed." |
| Too many checks | "That's a lot of ideas for one coffee break." |

**Verdicts:** SURPRISINGLY, YES / THIS COULD WORK / CROWDED POND / KEEP YOUR DAY JOB. Dry headlines rather than bro slang. Gemini writes the reason as a plain, useful explanation under the headline, with an office reference only if it lands naturally, often none and never more than one. For example: "Niche is far too small, and perishable logistics will eat your margin before your first status meeting." It's never mean about the person or their idea.

**The rule:** useful first, mildly disgruntled corporate employee second, frog third. That works out to about one dry jab per section: the header badge, the lede, the hint, the chips, loading, the card's RE: line (plus at most one in the reason), and the footer. Everything else is straight language, including the card's section headings.

Deliberately left out, to stay on the right side of parody: decorative underlines, stamped verdicts, ruled-paper backgrounds and "INTERNAL USE ONLY" labels. If a visual joke is ever wanted, a tiny [DRAFT] or memo treatment is the most this voice can take.

Avoid "unlock your potential", "AI-powered" and startup clichés.

No login, no database, no saved history, no build step. Nothing typed is stored.

## Files

```text
/
  index.html        Page
  styles.css        Styles (light and dark)
  app.js            One request, render the card (no storage)
  frogs/            coffee-body.svg, coffee-mug.svg (the frog, in two layers) and favicon.svg
  make_og.py        Renders the share cards in og/ (needs Playwright)
  analytics.js      GA4: paste your ID in one place
  make_pages.py     Builds the Break Room guides, About, What it costs, sitemap.xml, robots.txt, llms.txt
  break-room/ about/ what-it-costs/   Built pages (don't edit by hand)
  README.md
  lambda/
    index.mjs       The whole SideFrog Lambda: Gemini + live .com checks, one file, no npm packages
  sidefrog-lambda.zip   lambda/index.mjs, ready to upload
```

| Deployment | Files |
|---|---|
| AWS Amplify | `sidefrog-site.zip` (the whole site) |
| AWS Lambda | `sidefrog-lambda.zip`, on its own function called `sidefrog` |

## The SideFrog Lambda

SideFrog has its own Lambda function, `sidefrog`, at `https://4s7uc7iyyeh7p4sknfpo6agllq0ahdff.lambda-url.us-east-1.on.aws/` (set as `CHECK_API_URL` at the top of `app.js`, and in the `connect-src` part of the Content-Security-Policy in `customHttp.yml`; change both if the URL ever changes). It's one file, `index.mjs`, that answers one request, `POST { "kind": "idea", "idea": "..." }`, plus a `GET` health check. The Idea Sifter code, the two-tool router and the `lambda.handler` alias that lived here when SideFrog shared the Sifter's function are gone.

### Setting up the function (once)

1. **Runtime** Node.js 20 or later. **Handler** `index.handler`.
2. **Timeout** 30 seconds (Gemini can take up to 20, the .com checks up to 6). **Memory** 256 MB is plenty.
3. **Code:** Code, Upload from, .zip file, pick `sidefrog-lambda.zip`.
4. **Function URL:** auth type NONE. Under CORS: allowed origins `https://sidefrog.com` and `https://www.sidefrog.com` (add your Amplify preview address while testing, or `*` to test from your desktop, then take it back out), allowed methods `GET` and `POST`, allowed headers `content-type`. Leave `SEND_CORS_HEADERS` unset so AWS sends the CORS headers and the code doesn't duplicate them.
5. **Environment variables:** at least `GEMINI_API_KEY` (table below).

Quick test (the first should say `"ready": true`):

```sh
curl -s "https://4s7uc7iyyeh7p4sknfpo6agllq0ahdff.lambda-url.us-east-1.on.aws/"
curl -s -X POST "https://4s7uc7iyyeh7p4sknfpo6agllq0ahdff.lambda-url.us-east-1.on.aws/" \
  -H "content-type: application/json" \
  -d '{"kind":"idea","idea":"meal prep for traveling sales reps"}'
```

### Environment variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | **Required.** |
| `GEMINI_MODEL` | Default `gemini-3.5-flash-lite`. (The old name `NAMERCHECK_GEMINI_MODEL` still works.) |
| `GEMINI_TIMEOUT_MS` | Default 20000. |
| `AI_RATE_LIMIT_PER_MINUTE`, `AI_RATE_LIMIT_PER_HOUR` | Per-visitor (IP) limits, defaults 6 and 40, per warm instance. Enough for someone testing a handful of ideas. |
| `ALLOWED_ORIGINS` | Optional, recommended once live: `https://sidefrog.com,https://www.sidefrog.com`. Requests from other sites get a 403. Default `*` so you can test from anywhere. |
| `BOT_USER_AGENT`, `SITE_URL` | User-Agent sent to the .com registry. |
| `SEND_CORS_HEADERS` | Leave unset (AWS handles CORS). Set `true` only if you turn CORS off on the Function URL. |

## API

`POST { "kind": "idea", "idea": "meal prep for traveling sales reps" }` returns:

```json
{
  "idea": {
    "verdict": "crowded",
    "verdictReason": "People want it, but meal kits are everywhere.",
    "sharpenedIdea": "Frozen meal packs for reps who live in hotels.",
    "whoPays": "Field sales reps, about $80 a week.",
    "firstMove": "Post a sign-up page in two sales subreddits.",
    "keywords": ["healthy meals for travel", "meal prep delivery for one"],
    "alternatives": ["...", "...", "..."],
    "names": [{ "name": "Roadfed", "domain": "roadfed.com", "status": "likely_available" }],
    "yourName": { "name": "SideFrog", "domain": "sidefrog.com", "status": "taken", "registeredYear": 2019, "comment": "Short, friendly, and the frog gives you a mascot." }
  },
  "model": "gemini-3.5-flash-lite"
}
```

`verdict` is one of `great`, `worth_a_shot`, `crowded`, `nah`, `cant_help`. `yourName` is `null` when the idea doesn't mention a name. (The `yourName` values above are illustrative, not a real lookup.)

Each name's `status` is one of:
- `likely_available`: the registry has no record
- `taken`
- `unknown`: timed out or couldn't be checked

Errors come back as `{ "error": "..." }` with a user-readable message (400, 413, 422, 429, 502, 503, 504).

## How it stays fast

- **One request per check.** The Lambda starts loading the .com registry details while Gemini thinks. It then checks all 12 .coms in parallel, with a 6-second cap, so a slow lookup becomes `unknown` instead of holding up the answer.
- **A short reply.** Gemini returns a short JSON reply (capped at 1,024 tokens) shaped by an enforced schema. There's no `temperature`, because it's deprecated for Gemini 3.5+. Flash-Lite's default minimal thinking is used.
- **A small page.** About 21KB in total, with no storage and no other API calls.

## Honesty rules

- **The AI never decides availability.** Only a registry "not found" makes a name show as open. Anything unclear is `unknown`, and those names are only shown, marked "couldn't check", when the registry couldn't be reached at all.
- **"Open" means likely available.** Premium or reserved names can look the same, and the footer says so.
- **The verdict is labelled** as an AI's quick read, not market research or legal advice.
- **Weak ideas get reshaped, not refused.** Only clearly illegal or harmful ideas get `cant_help`, with no names or keywords and three legitimate alternatives.
- **Model output is parsed, type-checked and length-capped** on the server, and rendered with `textContent` only.
- **Outbound requests are allowlisted:** HTTPS only, to Google's Gemini API, IANA, and the RDAP server from the IANA bootstrap file. Redirects are re-checked.

## Hardening for public traffic

Origin checks only stop other websites; scripts can still call the URL directly. The in-memory rate limits reset with each Lambda instance. For real protection:

- **Reserved concurrency:** set it on the shared function (for example 10–20).
- **Google Cloud budget alert:** set one on the project behind the Gemini key.
- **AWS WAF:** add a rate-based rule if traffic grows.
