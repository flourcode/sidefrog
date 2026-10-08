"""Titles for multi-idea videos (compilations, countdowns, list Shorts) that only claim what the
episodes themselves show: their verdicts, what each test costs, how easy each is to start.
Never earnings. Strongest true claim first."""
import re

GOOD = {"Surprisingly, yes", "This could work"}
SKIP = {"Keep your day job", "Crowded pond"}


def cost_value(text):
    """$ figure from "about $40", "under $100", "$0", "Free"; None when there isn't one."""
    t = str(text or "")
    if re.fullmatch(r"\s*free\s*", t, re.I):
        return 0
    m = re.search(r"\$\s?([\d,]+)", t)
    return int(m.group(1).replace(",", "")) if m else None


def cost_claim(eps):
    """"for $0" / "for Under $100" / "for Under $500" when every test in the set fits; else ""."""
    costs = [cost_value(e.get("test_cost")) for e in eps]
    if not costs or any(c is None for c in costs):
        return ""
    top = max(costs)
    return "for $0" if top == 0 else "for Under $100" if top < 100 else "for Under $500" if top < 500 else ""


def checked_titles(eps, countdown=False):
    n = len(eps)
    verdicts = [e.get("verdict", "") for e in eps]
    titles = []
    cost = cost_claim(eps)
    if cost:
        titles.append(f"{n} Side Hustles You Can Test {cost}")
    if verdicts and all(v in GOOD for v in verdicts):
        titles.append(f"{n} Side Hustles Frank Would Actually Try")
    if verdicts and all(v in SKIP for v in verdicts):
        titles.append(f"{n} Popular Side Hustles Frank Isn't Sold On")
    if eps and all(e.get("ease") == "easy" for e in eps):
        titles.append(f"{n} Side Hustles That Are Easy to Start")
    if countdown:
        titles.append(f"{n} Side Hustles, Ranked Worst to Best")
    titles += [f"Can You Actually Make Money With These {n} Side Hustles?", f"{n} Popular Side Hustles, Honestly Reviewed"]
    return list(dict.fromkeys(titles))


def boring_note():
    return '(Add "Boring" before "Side Hustles" only when the set really is plain, practical work.)'
