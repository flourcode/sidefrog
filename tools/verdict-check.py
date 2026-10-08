#!/usr/bin/env python3
r"""Is Frank too harsh? Asks Frank's service about a set of ideas and shows each verdict next to what
a fair answer looks like, plus the overall mix. Run it after deploying a new Lambda:

    python tools\verdict-check.py

It waits about 11 seconds between ideas (the service allows 6 a minute), so 16 ideas take about
3 minutes. Nothing is saved; it only prints.
"""
import json, sys, time, urllib.request, urllib.error
from collections import Counter

API = "https://4s7uc7iyyeh7p4sknfpo6agllq0ahdff.lambda-url.us-east-1.on.aws/"
LABEL = {"great": "Surprisingly, yes", "worth_a_shot": "This could work", "crowded": "Crowded pond",
         "nah": "Keep your day job", "cant_help": "Can't help"}
# (idea, verdicts that would be fair)
IDEAS = [
    ("dog walking on Rover", {"great"}),
    ("house cleaning on weekends", {"great"}),
    ("lawn mowing in my neighborhood", {"great"}),
    ("pet sitting", {"great"}),
    ("tutoring high school math", {"great", "worth_a_shot"}),
    ("mobile car detailing", {"great", "worth_a_shot"}),
    ("handyman jobs on TaskRabbit", {"great", "worth_a_shot"}),
    ("reselling thrift finds on eBay", {"great", "worth_a_shot"}),
    ("bookkeeping for small businesses", {"great", "worth_a_shot"}),
    ("notary loan signing agent", {"worth_a_shot"}),
    ("renting out party tables and chairs", {"great", "worth_a_shot"}),
    ("selling home-baked cookies", {"worth_a_shot"}),
    ("dropshipping phone cases", {"crowded"}),
    ("generic print-on-demand t-shirts", {"crowded"}),
    ("faceless AI YouTube channel", {"crowded", "nah"}),
    ("meal kits for pet turtles", {"nah"}),
]


def ask(idea):
    req = urllib.request.Request(API, data=json.dumps({"kind": "idea", "idea": idea}).encode(), method="POST",
                                 headers={"Content-Type": "text/plain;charset=UTF-8", "User-Agent": "SideFrog verdict check"})
    with urllib.request.urlopen(req, timeout=40) as res:
        return json.loads(res.read().decode("utf-8"))["idea"]


def main():
    mix, fair = Counter(), 0
    for k, (idea, ok) in enumerate(IDEAS):
        if k: time.sleep(11)
        try:
            r = ask(idea)
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as err:
            print(f"  {idea:42s} couldn't ask ({err})"); continue
        v = r.get("verdict", "?"); mix[v] += 1; good = v in ok; fair += good
        print(f"{'  ok' if good else '  ??'}  {idea:42s} {LABEL.get(v, v):18s} {r.get('verdictReason', '')[:90]}")
    print("\nThe mix:", ", ".join(f"{LABEL[v]} {n}" for v, n in mix.most_common()))
    print(f"Fair verdicts: {fair} of {len(IDEAS)}. Lines marked ?? are worth a look; one or two is normal (it's an AI's read).")


if __name__ == "__main__":
    main()
