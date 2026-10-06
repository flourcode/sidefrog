# SideFrog

**Tagline:** "Free advice from a frog with no stake in your idea." (home page title, its search and share descriptions, `llms.txt`; not under the logo).

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
| /break-room/start/where-to-get-feedback/ | Where to get honest feedback (6 numbered steps: decide whose opinion counts, find where your buyers already talk, builder communities if it's an app (r/SideProject, r/sideprojects, r/IMadeThis, r/buildinpublic, r/alphaandbetausers, r/webapps, described by purpose only), read the rules first, ask don't pitch, count what you hear; "Frank, at the water cooler"). Written in response to a "40 subreddits to promote your startup" list, which was all builder communities and an ad for a directory; the guide's point is that builders aren't buyers. Rules are deliberately not listed per subreddit because they change; it says to read each sidebar. The answer card's "Read next" points here when the cheap test mentions a subreddit, Facebook, Nextdoor, LinkedIn, a forum, a group or posting somewhere (not for Keep your day job). The Side Kit's "Write a feedback post that won't get removed" prompt (#feedback-post) goes with it. |
| /break-room/sell/first-ten-customers/ | How to get your first 10 customers (7 numbered steps: 30 names, a specific customer, a short honest message with an example to adapt, follow up twice, ask for the sale, do the work by hand, turn each customer into the next; "Frank, off the record"; one line offering Mark's time, since sales is his field) |
| /break-room/sell/what-to-charge/ | What should I charge? (6 numbered steps: going rate, your floor, value to the customer, a simple structure, say it plainly, honest founding prices; then an unnumbered worked example with made-up numbers; "Frank’s two cents"). Taxes get one line pointing to an accountant, nothing more. |
| /break-room/leap/before-you-leap/ | Before you leap (6 numbered steps: build the safety net, price out what your job quietly pays for (COBRA vs HealthCare.gov, sourced), let the side hustle prove itself with a "leap number", talk to the people it affects, decide your checkpoint, leave well; "Frank, speaking as a friend"). General guidance with one "not financial advice" line pointing to a fee-only planner; one line on having employment paperwork read by a lawyer. First in the home guide list, and "Read next" after a Surprisingly, yes verdict. |
| /break-room/build/vibe-coding-101/ | Vibe coding 101: vibe a site tonight, with the dek "A plain-English guide to getting your weird idea onto the internet before you talk yourself out of it." (8 numbered steps: one sentence, brief it with a point of view, smallest thing that works, one change at a time, use it like a customer, save your work, write a handoff before the chat runs out (with copyable prompts to write HANDOFF.md and to start the next chat from it), put it online; "Frank has notes") |
| /break-room/build/before-you-put-it-online/ | Before you put it on the internet: keys, spending limits, rate limits, user input and prompt injection, collecting less, free protections, backups ("Frank would like a word"; help box) |
| /break-room/build/six-users-now-what/ | Six people use it. Now what? Error alerts, the weekly bill, what to count, adding pieces only when needed, when to stop vibe coding ("Frank ran the numbers"; help box) |
| /break-room/start/test-a-big-idea-small/ | Test a big idea small (7 numbered steps for food trucks, shops and other in-person businesses: shrink it to one Saturday, check your health department first (cottage food rules, sourced), rent before you buy, sell where the crowd already is, pre-orders, count everything, repeat before you scale; "Frank, between sips") |
| /side-kit/ | The Side Kit: ten copyable prompts by stage (Test it, Money, Sell it, Build it, Leap), each with "You'll get" and "Watch out", copy buttons via `side-kit.js` ("From Frank's desk") |
| /side-kit/leap-worksheet/ | The Leap Worksheet ("Form SF-1"): a printable form (monthly number, what the job pays for, safety net, leap number, checkpoint, first test, 30 names, signed, "Reviewed by Frank."). Print button and `side-kit/leap-worksheet.pdf` (one Letter page, made by `make_og.py` from the print styles) |
| /about/ | About SideFrog (Mark, first person) |
| /what-it-costs/ | What it costs me to test an idea (Mark's real bills; its card is labeled "My usual costs" with Mark's photo, since Mark is the one talking) |

Every guide opens with a note from Frank (each guide has its own Frank line), uses one office aside, ends with a "Check your idea" box, a visible FAQ (with matching FAQPage structured data), Read next rows and dated sources. Voice rules are at the top of `make_pages.py`. SideFrog stays out of legal and tax advice; those guides are parked on purpose.

**The idea box's grey example rotates** every 3.5 seconds through realistic side hustles with the odd weird one, so people see any idea is fair game: website tune-ups for local restaurants, travel planning for busy families, estate sale flipping on weekends, LinkedIn coaching for executives, cruise broker, candles that smell like the office (`EXAMPLES` in `app.js`). It holds still while someone is in the box or has typed, while the tab is in the background, and for reduced motion. The box is sized to the longest example, so its height never jumps as they rotate. The grey text is `#66614F` (6.1:1, readable but clearly not typed text). None of the examples is the example answer card's idea (pet turtles), so a live answer never contradicts the card beside it.

**An empty click gets a quiet nudge.** The rotating grey examples ("e.g. taco truck empire") are inspiration only and are never checked. Clicking "Check my idea" with an empty box sends nothing: the cursor stays in the box (the keyboard opens on phones), the box gives a small shake (none with reduced motion), and the status line under the button reads "Give me something to work with." in deep green, with no Frank and no red. Typing brings the promise back. Real errors (the AI is busy, a timeout) still show Frank in red in the same spot. Analytics event: `empty_nudge`.

**No "Or try" chips:** they duplicated the rotating examples and pushed the example answer below the first screen on phones, so they were removed.

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

**The box and the example card, simplified:** the box label is just "YOUR IDEA" (no "and a name, if you have one"; people who type a name in their idea still get it checked as an exact .com). The example card ends with one plain line instead of a feature list: "Every answer gives you a cheap first test, who might pay, and what to watch out for. If the idea survives, we'll help with names too." The rest is discovered after a check.

## The idea box on phones

The box is built to keep the example answer on the first screen and Frank's messages visible above the phone keyboard: a one-line typing area on phones (1.3rem; the rotating examples are short enough to fit on one line at 360px and up: interview coaching, taco truck empire, YouTube influencer, yard sale flipping, fractional sales help, dog walking business, passive-aggressive mugs, chosen to cover selling what you know, the quit-the-office fantasy, the creator fantasy, hobby to money, corporate skills without corporate life, a simple tangible escape, and permission for weird ideas), tighter hero spacing, and a single **status line under the button inside the box**. It normally shows the promise ("Half-baked is fine. Your idea isn't saved."); a one-line nudge ("Give me something to work with.") takes its place on an empty click, and Frank's message on an error. "This is a coffee break, not Shark Tank." lives in Frank's thinking state instead: it's the note under "SIPPING ON IT…" while he works, replaced by "Circling back on the .com names…" if the check runs past 4.5 seconds. If the message isn't fully visible (the keyboard takes about half a phone screen), the page scrolls the box to just below the top so the input and the whole message fit above the keyboard. Measured with Safari's bars showing: the example verdict ends at about 600px on a 393x659 iPhone 14 Pro view (it was 744), and the input plus message fit above the keyboard on iPhone 14 Pro, iPhone SE and a 360px Android.

## Frank (the 2026 art)

Frank is traced, not drawn: every frame comes from Mark's approved reference art (a sip sprite sheet and an expression sheet), converted to vectors exactly, recolored from lime to avocado (#8DAA3F with matching highlight and shadow greens), and aligned to each other by image registration so he never jumps between frames. The 13 source frames live in `frogs/src/` in name order (kept out of the site zip): five faces, sip frames 2 to 8, then the straight-ahead resting frame (`frank-13-forward.svg`, frame 12). New frames go at the end with the next number, and `build_frank_sprite.py` updates the stylesheet's frame count.

| Frame | Face | Used for |
|---|---|---|
| 0 | small "o", surprised | Surprisingly, yes (`yeah`) |
| 1 | smile, eyes left (the sip's first frame) | This could work (`smirk`), the header, guide notes, About |
| 2 | heavy lids, flat mouth | Crowded pond (`meh`) and Keep your day job (`nah`) |
| 3 | puzzled, mouth to the side | Can't help (`sad`) |
| 4 | skeptical brow, frown | Error (`oops`) and the 404 page |
| 5-11 | the sip | the animation |
| 12 | relaxed, looking straight at you | the logo, guide notes, Side Kit, About |

**Round Frank (identity and sharing):** `frank_art.py` turns any frame into a cutout or a round version. The circle is calculated once across all 13 frames (`frogs/round.json`): the whole head inside with breathing room above the bumps, the mug and hand in frame at rest and mid-sip, and the bottom of the circle in his green body. For that, the round version gives him a longer torso: below each frame's bottom row it adds flat avocado with his outline and arm crease continued straight down (measured once into `frogs/round.json`), so nothing from the mug or the drawing's shading can streak into it. Round Frank is used on the About page (matching Mark's portrait, and he sips: `build_frank_sprite.py` also makes `frogs/frank-round.<hash>.webp`, exposed to CSS and JS as `--frank-round`), the share cards and meeting backgrounds (`make_og.py`), the share-your-verdict image (his verdict face in a cream circle), and the profile pictures and video in `frank-profile/` (not part of the site). Beside text on the site (logo, notes, the answer card) he stays a cutout.

**Icons, stickers and the demo video:** `python3 make_icons.py` builds the favicons (16px is a face crop so his eyes read in a browser tab; 32 and 48 are the full round avatar), `favicon.ico`, the app icons (`icon-192/512.png` round), and the full-square `apple-touch-icon.png` and `icon-maskable-512.png` (the phone rounds those itself; the maskable one keeps him inside the safe zone). `python3 make_stickers.py` builds the sticker pack: eight die-cut 1024px PNGs in `frank-stickers/` and `sidefrog-stickers.zip` (not part of the site). `video/make_video.py` sets Frank's frames from its own timeline (his card sip while he thinks) and ends on round Frank.

**Pupils:** Frank ships with his pupils exactly as traced; `frogs/src/` is a copy of `frogs/src-traced/`. A 75% version was tried and rejected. `frank_pupils.py` can still produce smaller pupils (it paints each pupil out inside the eye's white and draws a smaller oval that keeps the gaze), but it isn't part of the build.

**RE is a memo subject line:** the Lambda (3.1.0) returns `subject`, a 3 to 6 word summary of the idea, and the answer card, share image and shared links use it for RE (the full idea shows on hover and still goes into the AI prompts). Without one, RE is the idea trimmed to one line. On wider screens Frank starts at the verdict row (not the top of the card), with `--frank-lift` putting his eyes level with the verdict, so a long RE can't push the verdict out of his gaze.

**The share-your-verdict image** is 1080×1080 (square, so LinkedIn, Instagram, X, iMessage and Slack all show it whole), with the tagline under the SideFrog logo; it picks the largest of three size steps that fits, so long reasons shrink a little instead of overflowing. It follows the same rule as the answer card: the memo header runs full width, the verdict sits in a column beside round Frank (the biggest size from 108 to 84px that fits in two lines), and Frank's eyes (about 29% down his round frame) are level with the verdict's first line.

**About page:** opens with "SideFrog helps you decide which ideas are worth testing out." Frank comes first (150px round, on the left) with what's behind him: Gemini's analysis plus the live .com check of about 20 names, then a Check an idea button. Then "The person behind Frank" with Mark's photo (120px on the right), "Who it's for", "What happens to your idea" and "Want help?". Portraits have no captions, so the text wraps around the circles. Mark's photo is `mark-portrait.jpg`, a warm ink-to-cream two-tone of the original `mark-mono.jpg` (kept in the source, not deployed), used on About and What it costs.

**Shared verdict links** go to `/verdict/#v=...`. `make_pages.py` writes `verdict/index.html` as a copy of the home page with its own title, description and share card (`og/verdict.jpg`: "Frank's verdict is in", no sample verdict), marked noindex with the home page as canonical. The verdict stays after the `#`, so it's never sent to a server and link previews can't show it; this card makes the preview an invitation instead of the home card's sample verdict ("Keep your day job"), which looked like the shared verdict. Old `/#v=` links still work.

**The editorial system (the Break Room and its guides):** borrowed from Monocle's grammar, not its look. Small uppercase labels (`.ed-kicker`), big avocado numbers, thin rules instead of cards, an italic serif (Source Serif 4, from Google Fonts) only for one-line descriptions and pull lines, and a ruled side rail from 900px. The Break Room (`contents=True`) is a contents page: numbered sections, numbered guides with a one-line description (`BLURBS` in make_pages.py, about 10 to 15 words; the longer `description` stays for search) and a reading time (`read_minutes`, about 220 words a minute). Every guide (`article=True`) gets a label, headline, one-line description and byline; numbered guides get big step numbers and an "In this guide" list; the rail holds Frank's note and "Read next". Phones get one column, with Frank's note right after the headline. A "Frank's week" panel of verdict counts is designed but waits for real counts.

**Stuff I Like** (`/stuff-i-like/`, in the Break Room's Behind SideFrog section): Mark's books and podcasts and "What you don't need yet", from `STUFF_BOOKS`, `STUFF_PODCASTS` and `STUFF_SKIP` in make_pages.py. Only things Mark has actually read or listened to; no paid links (if one ever pays, it says so next to the link).

**Analytics events** (GA4, only on sidefrog.com, never the idea text): `check` (verdict, check_number, from_shared: "yes" when the check started on a shared verdict), `second_check`, `check_error`, `empty_nudge`, `share` (method), `shared_view`, `prompt_copy` (prompt), `guide_share` (method), `help_click` (via), `register_click`, `search_click`, `quotabird_click`, `check_cta_click` (from: the page whose Check an idea button was clicked; the logo doesn't count) and `kit_download` (item: the Side Kit file). Register as event-scoped custom dimensions: verdict, check_number, from_shared, method, prompt, via, from, item.

**Content-aware gaze:** every Frank has `data-look`. **you** (the logo, guide notes, the Side Kit, About, the 404 page): he rests looking straight at the reader on frame 12, traced from the relaxed straight-ahead reference, and sips 10 → 9 → 8 → 7 → 8 → 9 → 10, glancing right at his text while he drinks, then looks back at you. **left** (the example and answer cards): he rests on his verdict face, looking at the verdict, and sips 5 → 6 → 5. **right** (the error nudge): the error face, which looks right at the message. `make_pages.frank_svg(cls, mood, look)` defaults to `you`; index.html sets it by hand. Known gap: the Can't help face looks up and right, away from the card's text; a left-looking version would need new reference art.

`python3 build_frank_sprite.py` renders them into one 320px-per-frame strip, `frogs/frank-sprite.<hash>.webp` (about 160KB), and writes that name into `styles.css`. On the page Frank is `<span class="frog frank …" data-mood="…">`; CSS shows the frame for his mood (`--frame`), so setting a verdict is still one attribute. `frank.js` steps `--frame` through 5 to 11 for a sip and lets his face come back: about 3 seconds after a page loads (the biggest Frank on screen), then at random every 9 to 23 seconds (one Frank at a time, only on screen, not in background tabs, never with reduced motion), and on a loop while an answer loads (`frankLoop`/`frankStop`, called from `app.js`). The share card cuts his frame from the same sprite. Every asset now uses this Frank; the previous drawing and its animation CSS are gone.

## Share Frank's verdict

Under every verdict (except "Can't help"), a quiet "Share Frank's verdict" text link makes a 1080x1350 image in the site's style: the masthead, a memo card (FROM: Frank, RE: the idea, Frank with that verdict's face), the verdict in big caps (fitted to one line from 108px down to 84px when it can), the reason, then "sidefrog.com" and the tagline, centered below the masthead. It's drawn on a canvas in the visitor's browser from the answer on screen, with Frank's body, face and mug layers combined into one SVG; nothing is sent to the server, so "Your idea isn't saved" stays true. On phones it opens the share sheet (LinkedIn, Messages and so on); elsewhere it downloads `frank-verdict.png` and the link says "Saved. Post it anywhere." Long ideas trim to two lines and long reasons to six, with an ellipsis. It's also the fastest way to make "Frank's bad idea of the week" posts.

**Shared verdict links:** "Copy link" sits beside "Share Frank's verdict", and the share sheet includes the link with the image. The link is `sidefrog.com/#v=...`: the idea (160 characters), verdict, reason and cheap test, as base64url JSON after the `#`. Browsers never send that part to the server, so it's never in Amplify's logs and nothing is stored. Opening one shows that exact card in the example card's place, marked SHARED, with Frank's face for the verdict (borrowed from the answer card's Frank if the example card lacks it), the cheap test and a "Check your own idea" button that takes you to the box; there's no new Gemini call, so shared links cost nothing. The address is cleaned afterwards, a `shared_view` event is recorded (verdict only), and `analytics.js` sets `page_location` without the `#`. Invalid or tampered links just show the normal example; text is always inserted as text, never HTML.

**Guide share links:** every Break Room guide ends with "Share this guide: LinkedIn · Copy link" (LinkedIn's share page, plus a copy button handled in `local-links.js`); both are counted as `guide_share` with the method.

**Video-call backgrounds (Side Kit, "Frank for your next meeting"):** three 1920x1080 PNGs (about 70KB each) in `side-kit/backgrounds/`, with 640x360 previews: "Could have been an email" (a memo from Frank, RE: this meeting), "The desk" and "After hours" (dark). The middle stays clear for the person. Rendered by `make_og.py`. Frank's art is licensed sticker art: confirm the license allows people to download and use it before relying on this section. The PNGs are cached for a year, so give a changed design a new file name.

**Analytics for the funnel:** every `check` event carries `check_number` (1st, 2nd, 3rd check in a visit), a separate `second_check` event fires on the second (the "this is fun" signal), and `share` records the verdict and `method` (`share_sheet`, `download` or `copy_link`); `shared_view` counts visits from shared links, and `guide_share` counts guide shares. None of them include the idea. To see `check_number` and `method` in GA reports, register them once under Admin > Custom definitions > Create custom dimension (event scope).

## The answer's facts, in decision order

After the verdict and its reason, the card leads with the test and its pass/fail pair, prompted by r/SideProject feedback ("make the cheap test the main output, with a pass/fail signal and what result would change the recommendation"): **Cheap test** (full width, larger type, a 4px avocado rule), then **Keep going if** (`goodSign`) and **Rethink it if** (`rethinkIf`) side by side on desktop, stacked on phones. Both are written by Gemini to finish their label's sentence, so they start lowercase ("Keep going if you sell out before the market closes"). Then **Watch out for**, **Who pays** and **Sharper version**, smaller and muted, as context. The verdict stays the headline and the names stay visible: they're the hook and the fun for a casual audience. An older Lambda without `rethinkIf` just leaves that row out. The prompts section below is called "Hand it to your AI".

## Names with an open .com

Gemini can't know which .coms are free, so the Lambda improves the odds instead of guessing: it asks for **20 names** (7 to 14 letters; a trade word plus an unexpected second word, a short phrase run together, or a coined word; no obvious pairs like "taco truck" or anything + "hub"), and checks all 20 .coms at once, so 20 take about as long as 12. Every name must pass the say-it-once test (hear it once, spell it, and it hints at the business; real words combined freshly over made-up spellings like Cilantroro), avoid accidental readings when run together (Scutefood reads as "S cute food"), and come back best first, which is the order the site shows the open ones in. **If every one is taken**, it makes one small extra call for 12 fresh names (it's told which were taken; names only, 300-token cap, 8-second timeout) and checks those too. That retry only runs when nothing came back open, when the registry actually answered (no point retrying a registry outage), and when the request is under 14 seconds old; the site's "Circling back on the .com names…" note covers the wait. If still nothing is open, the message suggests checking again or adding a name of your own to the idea (which is checked as an exact .com), and the empty list is hidden.

## Two answer fields borrowed from the old Sifter

The Lambda returns two more short lines, both shown in the answer's facts list after "Cheap test":
- **`goodSign` ("Good sign")**: the countable result from this week's test that says the idea is working, e.g. "3 shops say yes to a paid second month". It does step 1 of "Test an idea in a week" (decide what yes looks like) for the reader.
- **`watchOut` ("Watch out for")**: the single thing most likely to sink it (a big free competitor, insurance or liability, platform rules, personal data, payments, a slow first test), stated without legal, tax or financial advice. When the model says "Nothing obvious", the row is skipped.

The prompt also has the Sifter's "not a clone" rule: when similar things exist, the sharpened idea must be narrower, simpler or aimed at a different buyer. Both fields are in the response schema, cleared for "can't help", capped at 160 and 180 characters, and add about 40 tokens to a typical 400-token answer (limit 1,024), so Flash-Lite isn't strained. Deliberately not borrowed: keyword demand guesses (guesses dressed as data), named communities for first customers (the model invents subreddits), scores, stack fit and weekend build plans. The site and Lambda can be deployed in either order: an older Lambda just means the two rows don't appear.

## The "Build the page" prompt

Built in the visitor's browser from Frank's answer (it never goes to Gemini, so its length costs nothing), and mirrored with [brackets] in the Side Kit. It follows Steve Jobs' design questions: it states the page's one job (get the right person to tap one button) and says to leave out anything that doesn't help it; it asks the user five short questions before building (name and price, what they believe, the feel and a look they like, the worry plus any real proof, the link) and makes confident choices on "you choose", because most people won't fill in blanks before pasting; it fixes the structure (a first screen that works on a phone without scrolling with name, plain headline, price and button; what you actually get; the worry answered with real proof above the button again; a quiet footer; no menu, feature grid or FAQ wall); it sets a craft standard (designed from the business, confident type scale, generous spacing, one or two Google Fonts, a restrained palette from the business, one simple inline SVG or CSS visual, calm scroll motion that respects reduced motion); it says it should just work (both buttons open the link, a marked placeholder if there isn't one, title, description and sharing tags); it keeps the honesty rules (now including credentials and awards); and it ends with two passes: fix the five weakest things as a skeptical customer and a demanding designer, then remove whatever is there "because it could be, not because it should be". The old 40KB limit is gone.

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

## Two zips

- **`sidefrog-site.zip`** is for Amplify: only the files the website serves (pages, styles, scripts, images, sitemap, robots, llms.txt, the AI catalog). Nothing internal is public.
- **`sidefrog-source.zip`** is the whole project for GitHub: the site plus `customHttp.yml`, `amplify-redirects.json`, the build scripts, the docs, the Lambda source and the video script.

`customHttp.yml` and `amplify-redirects.json` are not uploaded with the site on manual deploys; paste their contents into the Amplify console (Hosting > Custom headers, and Hosting > Rewrites and redirects). To confirm the headers are live: Chrome DevTools > Network > reload > the page's first row > Response Headers should show `cache-control: no-cache` and `content-security-policy`.

## Updating the site (cache busting)

**The routine: edit, run `python3 make_pages.py`, zip, deploy.** Always run the build before deploying, even if you only touched `styles.css`, `app.js`, `frank.js`, `analytics.js` or an image. The build stamps every reference to those files with a fingerprint of their contents (`styles.css?v=b4c6dbb4`). Change a file and its fingerprint changes, so returning visitors' browsers fetch the new version; unchanged files keep coming from cache. It stamps the tool page (`index.html`) as well as the generated pages.

`customHttp.yml` sets the matching caching: HTML is always revalidated (`no-cache`), so a deploy shows up on the next visit; stamped CSS, JS, SVG, PNG and `mark.jpg` are cached for a year. Share cards, `favicon.ico`, the manifest, `sitemap.xml`, `robots.txt` and `llms.txt` get short lifetimes because apps request them by fixed name. With Git-based Amplify deploys the file is picked up from the repo root; with manual zip deploys, paste the same YAML into Amplify > Hosting > Custom headers. It's the same approach as QuotaBird.

## The footer

One template in `make_pages.py` (`FOOTER`) for every page, including the tool page: the build swaps it into `index.html`, so the two can't drift. It has the tagline, links separated by middle dots (Break Room, What it costs, About, Get help), THE FINE PRINT (what the verdict and the .com check are, not legal, financial or trademark advice, nothing you type is saved), and the COLOPHON in Mark's voice, ending "Updated October 2026" from `UPDATED`.

## Amplify rewrites and redirects

`make_pages.py` writes `amplify-redirects.json` on every build: first, a 301 from `https://www.sidefrog.com` (and any path under it) to the same path on `https://sidefrog.com`, so www always ends up on the bare domain; then a 301 from each page's address without the trailing slash to the one with it (`/about` to `/about/`), then a last catch-all that serves `404.html` with a real 404 status for any address that doesn't exist. New pages get their redirect automatically.

To install: Amplify console, your app, **Hosting > Rewrites and redirects > Manage redirects**, open the JSON editor, replace everything with the contents of `amplify-redirects.json`, and save. If the list had Amplify's default single-page-app rule (the long `</^[^.]+$|...>` pattern that sends everything to `index.html`), it must go: it would turn every missing page into the home page. Rerun the paste whenever you add a page. For the www rules to apply, `www.sidefrog.com` has to reach the app: in **Domain management**, make sure the `www` subdomain is listed for `sidefrog.com` (Amplify adds it by default). Amplify handles https itself. The www rules come from `BASE_URL` in `make_pages.py`, so they follow the domain if it ever changes.

`404.html` ("Frank can't find that page") is built from the same template, with root links (`/styles.css`) because it's served at whatever address was mistyped, `noindex` so search engines skip it, and links back to the tool and the Break Room. It's not in the sitemap.

**Text flows around Frank:** the guide note cards ("Frank has notes" and the rest), the What it costs card and Frank's introduction on About float Frank (or Mark's round portrait) top left, so the text wraps beside him and returns to full width underneath. Mark's round portrait uses `shape-outside: circle()` so the text curves around it. Frank deliberately doesn't: his right edge is nearly straight (head 78 to 91% of his width, shoulder 99%), so a traced outline moved text by only a few pixels and, with the gap removed, crowded him. Tested and dropped; keep the even gap. Frank is also never cropped into a circle: the circle is for the human. The answer card keeps its own layout so the verdict stays on one line.

## For the non-technical dreamer

The taco-truck reader is served by: "taco truck empire" leading the rotating examples; a rule in Frank's prompt that physical and local businesses get a small real-world first test (pop-up, market stall, catering one lunch, pre-orders, renting kitchen time) instead of a website, and that empires get sharpened to the first truck or stall; the "Test a big idea small" guide; the Side Kit (linked in the masthead, the footer and under the answer's prompt kit); and the Leap Worksheet (linked from the kit and from Before you leap). The masthead is just BREAK ROOM · SIDE KIT at every size, and its links never wrap; Build it, What it costs, About and Get help are in the footer. Deliberately not built: accounts, saved progress, a course or a community.


## Demo video (`video/`)

`video/make_video.py` renders `video/sidefrog-demo.mp4`, "the meeting": 9.6 seconds, 1080x1350 (4:5), 30 fps, about 900KB, opening and closing on the same SideFrog.com end card so it loops and the default thumbnail shows the URL (also saved as `video/sidefrog-demo-thumbnail.png`). A calendar memo in Frank's memo style ("FROM: Your calendar / RE: Q3 alignment sync / MEETING 1 OF 6 / Agenda: TBD."), then "Meanwhile...", then the real site: "taco truck empire" typed into YOUR IDEA, "Check my idea", Frank sipping over "This is a coffee break, not Shark Tank.", THIS COULD WORK stamped in with the cheap test and its keep-going and rethink lines, and a scroll to TacoRoute.com lighting up.The soundtrack is office sounds only, no music: whooshes as the cards move, a paper thump, key clicks, the button, Frank's sip, a rubber stamp on the verdict and a cash register for the open .com...", dips under the stamp and the cash register, and fades out over the end card; on top, a paper thump, keyboard clicks, a button click, a rubber stamp on the verdict and a cash register on the open .com. It doesn't sample or imitate any existing song. `python3 video/make_video.py --audio-only` rebuilds just the soundtrack into the existing video. Suggested caption: "If you like piña coladas but hate meetings, plan your escape with sidefrog.com". The answer is Mark's real taco truck result except the "Rethink it if" line, which is written in the prompt's style. Change the copy in `SCENE` or the `T_*` timings at the top and rerun (`python3 video/make_video.py`; needs Playwright, numpy and ffmpeg). The earlier one-idea demo was replaced.

## Sharing, icons and analytics

**Share cards (`og/`):** 2400x1260 JPGs (rendered at 2x, quality 90 with 4:4:4 colour so small text stays sharp; about 200KB each), linked with a `?v=` version code from their contents so LinkedIn and others fetch a changed card instead of a cached one (run `make_og.py` before `make_pages.py` so the codes match) with the tagline "Free advice from a frog with no stake in your idea" in the top corner (it replaced the retired price box), a label (the page's Frank line, "The Side Kit" or "Made by Mark") and a footer line that fits the kind of page; (50 to 76KB each), one for the home page and one per Break Room page, wired with Open Graph and `twitter:card` tags (absolute URLs on `https://sidefrog.com`, which social sites require). The home card shows the question and a real answer card (FROM: Frank, RE: meal prep for pet turtles, KEEP YOUR DAY JOB); each guide card shows its title under that guide's Frank line. They're rendered from HTML with the site's own font, colours and Frank by `make_og.py`. Rerun it after changing a page title (`pip install playwright`, `python3 -m playwright install chromium`, `python3 make_og.py`), then `python3 make_pages.py`. After launch, check a link in LinkedIn's Post Inspector and Facebook's Sharing Debugger; both cache cards, and those tools refresh them.

**Icons:** `apple-touch-icon.png` (180, on cream, since iOS fills transparency with black), `favicon-16.png`, `favicon-32.png`, `favicon.ico` (16/32/48) and `frogs/favicon.svg` use a tight crop on Frank's face so he reads at tab size; `icon-192.png`, `icon-512.png` and `icon-maskable-512.png` (Frank inside the safe zone so Android can crop to any shape) are listed in `site.webmanifest`.

**Analytics (`analytics.js`):** on, with GA4 measurement ID `G-MZ6BMZ84Y2` in `GA_ID` at the top. It only ever runs on the addresses in `LIVE_HOSTS` (sidefrog.com and www), never from your desktop. It sends page views plus: `check` (with the verdict type and `check_number`), `second_check`, `share` (verdict and method), `check_error`, `example_check` (an empty-box click), `prompt_copy` (which prompt), and `help_click`, `register_click`, `search_click`, `quotabird_click` for links that leave the site. It never sends the idea someone typed. In GA, under Admin > Data streams > Enhanced measurement, turn off "Outbound clicks", since those record full link addresses and the Google search links contain search phrases. If you add GA, consider a short privacy page saying so; the price box's "We don't save your idea" stays true.

**Before going live:**
- `BASE_URL` in `make_pages.py` is `https://sidefrog.com`. Change it if the site lives on another domain, then rebuild (it's used in canonical tags, the sitemap and llms.txt).
- `mark-mono.jpg` is Mark's photo as a small round portrait in warm sepia (240x240 for sharp screens, 10KB): shadows in the ink colour, highlights in a warm paper a shade deeper than the page so the circle reads without a border. On About it floats at the top beside the headline with the text wrapping around the circle (`shape-outside: circle()`), as on QuotaBird; the What it costs card uses it too. To redo it from a new photo: crop square, convert to greyscale, map shadows to `#1F241F` and highlights to `#ECE3D1`.
- Check that `https://porkbun.com/checkout/search?q=example.com` opens Porkbun's search with the domain filled in. If it doesn't, it still lands on their search page; adjust `registrarUrl` in `app.js` if you find the right pattern.
- Amplify rewrites and redirects: paste `amplify-redirects.json` (see below).
- Submit `sitemap.xml` in Google Search Console.

## Hand it to your AI (the prompt kit)

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
- **Masthead links:** BREAK ROOM · SIDE KIT in small caps where the price box used to be, at every screen size, set never to wrap. The current section is underlined in burnt orange. Everything else (Build it, What it costs, About, Get help) is in the footer.
- **The promise:** "Half-baked is fine. Your idea isn't saved." in deep green under the Check it button, where people decide.
- **Motion:** small and physical: lifts, presses, the frog's hop, and the loading bob. All of it turns off for people who prefer reduced motion. Focus rings are a 3px blue outline.

**Frank:** the frog is Frank. Each guide opens with its own Frank line ("Let me be Frank", "Frankly", "Just being Frank here", "I'll be Frank", "A note from Frank", "Frank's take"), the answer card's memo header reads "FROM: Frank" over "RE: your idea", and the loading line is "Frank's sipping on it…". About introduces him in one line ("The frog is Frank. He reads every idea that comes in and tells you what he thinks.") beside a small sipping Frank, without explaining the pun. Otherwise Frank never gets a biography, an explanation or "Frank the Frog"; readers work out the rest. Keep him to those spots, and don't repeat a Frank line on two guides.

**Voice:** deadpan corporate absurdity. SideFrog is side-hustle validation for people who are still technically on the clock. The humour sounds like it escaped from a meeting: dry, restrained and workplace-aware, about one line per spot, never a punchline on every surface. The site itself stays polished. The frog is the one character who says what the user is thinking.

| Spot | Copy |
|---|---|
| Masthead | BREAK ROOM · SIDE KIT (small caps links that never wrap; replaced the price box) |
| Promise | "Half-baked is fine. Your idea isn't saved." under the Check it button |
| Hero | "Thinking about making the leap from your 9-to-5?" |
| Lede | "Type an idea. Get a straight verdict in about ten seconds." |
| Hint | "Half-baked is fine. This is a coffee break, not Shark Tank." |
| Empty box | "Type an idea first. Half-baked is fine." |
| Examples | Rotating grey "e.g." examples in the box; no chips |
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

## AI Catalog (ARD)
`ai-catalog.json` and `ard.json` (identical, at the site root; Amplify rewrites serve them at `/.well-known/` too) follow the AI Catalog spec 1.0: exactly `specVersion` ("1.0"), `host` (SideFrog, `did:web:sidefrog.com`) and `entries`. Entries are resources agents can use, not web pages, so SideFrog lists one agent skill, `/skills/test-a-side-hustle-idea/SKILL.md` (type `text/markdown; profile="urn:air:agent-skills"`): its method for deciding whether an idea is worth testing and designing a cheap one-week test, from the "Test a side hustle idea in a week" guide. Pages stay findable through `llms.txt` and the sitemap. The idea-check API is deliberately not listed (it costs money per call). Built by `make_pages.py` (`SKILL_MD` holds the skill text). Check it with the `ardkit-ai` package: `validate_manifest(json.load(open("ai-catalog.json")))` returns `[]` when it conforms.


## Fonts and mobile speed
Fonts load from **Google Fonts** (Bricolage Grotesque and Source Serif 4 Italic), linked in every page's head (`FONT` in make_pages.py; index.html is kept in step on each build). Google Analytics loads after the page has loaded (`analytics.js`), so its script doesn't compete with the page on slow phones; events queue until it arrives.

Self-hosting the fonts is built and switched off (`SELF_HOST_FONTS = False`): `make_fonts.py` trims both fonts into fingerprinted WOFF2 files in `fonts/`, and `fonts/self-hosted-font-face.css` holds the matching `@font-face` rules. It removes Google's render-blocking stylesheet and two connections on phones, but it needs the live security policy to include `font-src 'self'`. In October 2026 the updated policy was saved in Amplify but the live site kept sending the old one, so browsers blocked the files and showed system fonts. To switch it on: confirm in the browser (Network tab, the page's response headers) that the live `content-security-policy` includes `font-src 'self'`; then set `SELF_HOST_FONTS = True`, paste the rules from `fonts/self-hosted-font-face.css` at the top of `styles.css`, rebuild, add `fonts` to the site zip, and deploy.


## Frank Reviews Your Side Hustle (YouTube Shorts)
`video/make_short.py` renders a 1080x1920, 25.6-second Short from the `EPISODE` block at the top of the file: the hook (1 to 4 lines), three notes (heading, line, Frank's face), the RE line, the verdict (one of five, as two lines), Frank's face on the verdict card, the reason and the cheap test. Beats: hook (0-3.0s, the finished hook holds 1.6-3.0s as the thumbnail frame), sip, three notes (3s each), the stamped verdict, the cheap test, the ask; it ends on the opening frame so it loops. Every text block sizes itself to its space (full size when it fits, smaller when long); an overlong RE is trimmed with "…". The episode block is checked first, with plain-English errors. Frank's faces are the traced originals (pre-rendered in `video/frames/`; `--frames` regenerates them with cairosvg); the font is `fonts/src/Bricolage.ttf`. Needs Python with Pillow and NumPy, and ffmpeg. Outputs `frank-short-NNN.mp4`, `-cover.png` (pick the frame at 2.0s as the YouTube thumbnail) and `-verdict.png`. `sidefrog-shorts-kit.zip` holds just the script, frames and font.

## Frank on YouTube (@SideFrogTV)
The Break Room's rail lists the latest Shorts (up to three, newest first) from `YOUTUBE_SHORTS` in make_pages.py, with a link to the channel; the footer links to the channel on every page. They're plain links, not embedded players: no security-policy change, no extra scripts slowing phones, no YouTube cookies. The cards say "Watch Frank's verdict" rather than giving it away. Clicks send `youtube_click` (video: the Short's id, or "channel"). To add an episode, put a line at the top of `YOUTUBE_SHORTS` (its title as on YouTube, its link) and rebuild. Build a full videos page at around 8 to 10 episodes.
