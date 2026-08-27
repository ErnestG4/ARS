"""STAGE B SCORING: score the sealed predictions against listener responses.

Reads cross_substrate/stageb_trials/responses.csv and the key, and scores B1-B4
exactly as `brocot_stageb_protocol` sealed them. Runs only when data exists; with
an empty sheet it says so and stops rather than reporting a null.

THREE THINGS IT REFUSES TO DO
-------------------------------
  1. SCORE A MERGE NULL THAT HAS NOT CLEARED ITS GATE. B1 is an inclusion
     criterion: a listener below 90% on the beat arm is not hearing the
     stimulus, so their merge trials say nothing about merges. The gate is
     evaluated first and the merge arms are not reported at all if it fails.
  2. REPORT A NULL WITHOUT ITS POWER. A single informed listener can show a
     difference IS audible far more cheaply than that one is NOT. So every
     merge rate carries a 95% upper bound, and a null whose upper bound sits
     above its own bar is reported UNDERPOWERED rather than as a pass -- the
     asymmetry is enforced here rather than left to the reader.
  3. MOVE A BAR. B2 <= 45%, B3 >= 60%, B1 >= 90%, chance 33.3%, all read from
     the sealed artifact rather than restated here, so an edit to the protocol
     cannot silently disagree with the scorer.
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

PROTO = json.load(open(os.path.join(HERE, "brocot_stageb_protocol.json")))
TRIALS = os.path.join(HERE, "stageb_trials")
KEY = json.load(open(os.path.join(TRIALS, "KEY_do_not_open.json")))["key"]
CHANCE = PROTO["chance"]
GATE, B2_BAR, B3_BAR = PROTO["gate_pct"], PROTO["b2_bar"], PROTO["b3_bar"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


rows = {}
path = os.path.join(TRIALS, "responses.csv")
if os.path.exists(path):
    for r in csv.DictReader(open(path)):
        v = (r.get("odd") or "").strip()
        if v in ("1", "2", "3"):
            rows[int(r["trial"])] = int(v)

if not rows:
    print("STAGE B SCORING\n")
    print(f"  responses.csv holds no answers yet ({len(KEY)} trials built).")
    print("  Listen to cross_substrate/stageb_trials/trial_NNNN.wav and write")
    print("  1, 2 or 3 in the `odd` column, then re-run this.")
    print("\n  Partial data is fine and expected — every rate below is reported")
    print("  with its n and a 95% interval, and the gate is checked first.")
    print("\nVERDICT: NO_DATA")
    sys.exit(0)

bykey = {k["trial"]: k for k in KEY}
arms = {}
for t, resp in rows.items():
    k = bykey.get(t)
    if not k:
        continue
    a = arms.setdefault(k["arm"], {}).setdefault(k["ratio"], [0, 0])
    a[1] += 1
    a[0] += (resp == k["odd"])

beat = arms.get("merge" if False else "beat", {})
bk = sum(v[0] for v in beat.values())
bn = sum(v[1] for v in beat.values())
b1 = bk / bn if bn else 0.0
lo, hi = wilson(bk, bn)

print("STAGE B SCORING\n")
print(f"  chance {CHANCE:.1%}   gate {GATE:.0%}   "
      f"B2 <= {B2_BAR:.0%}   B3 >= {B3_BAR:.0%}   (all read from the seal)\n")
print(f"B1 GATE — beat arm: {bk}/{bn} = {b1:.1%}  "
      f"[{lo:.1%}, {hi:.1%}]   {'PASS' if b1 >= GATE else 'FAIL'}")

if bn == 0:
    print("\n  No beat trials answered. The gate is unevaluated, so the merge")
    print("  arm is not scored.\n\nVERDICT: GATE_UNEVALUATED")
    sys.exit(0)
if b1 < GATE:
    print(f"\n  The gate did not clear. A listener below {GATE:.0%} on a")
    print("  squarely-audible arm is not hearing the stimulus, so their merge")
    print("  trials say nothing about merges and are NOT reported.")
    print("\n  This is an inclusion criterion declared before data, not a")
    print("  post-hoc exclusion. If the gate fails repeatedly, suspect the")
    print("  playback chain before the ears: check level, and that the 3-8 Hz")
    print("  beat is audible on the beat stimuli played alone.")
    print("\nVERDICT: GATE_NOT_CLEARED")
    sys.exit(0)

merge = arms.get("merge", {})
print(f"\nB2/B3 — merge arm, {sum(v[1] for v in merge.values())} trials\n")
print(f"{'ratio':>7s} {'correct':>9s} {'rate':>7s} {'95% CI':>16s}   reading")
uni_k = uni_n = 0
non_k = non_n = 0
above = 0
for ratio, (k, n) in sorted(merge.items(), key=lambda x: -x[1][1]):
    r = k / n if n else 0.0
    l, h = wilson(k, n)
    if ratio == "1":
        uni_k, uni_n = k, n
        read = "B3: the one masking says is heard"
    else:
        non_k += k
        non_n += n
        read = ("above bar" if r > B2_BAR else
                "UNDERPOWERED" if h > B2_BAR else "at chance")
        above += r > B2_BAR
    print(f"{ratio:>7s} {k:>4d}/{n:<4d} {r:>6.1%} [{l:>5.1%},{h:>5.1%}]   {read}")

if non_n:
    r = non_k / non_n
    l, h = wilson(non_k, non_n)
    ok = r <= B2_BAR
    powered = h <= B2_BAR
    print(f"\nB2 non-unison pooled: {non_k}/{non_n} = {r:.1%} [{l:.1%}, {h:.1%}]"
          f"   {'MET' if ok and powered else 'UNDERPOWERED' if ok else 'MISSED'}")
    if ok and not powered:
        need = math.ceil(0.25 * (1.96 / (B2_BAR - CHANCE)) ** 2)
        print(f"   the point estimate is under the bar but the interval is not:"
              f" a null needs\n   roughly {need} trials to separate {CHANCE:.1%}"
              f" from {B2_BAR:.0%}. Reported as underpowered,\n   not as a pass.")
if uni_n:
    r = uni_k / uni_n
    l, h = wilson(uni_k, uni_n)
    print(f"B3 unison 1/1:        {uni_k}/{uni_n} = {r:.1%} [{l:.1%}, {h:.1%}]"
          f"   {'MET' if r >= B3_BAR else 'MISSED'}")
    if r < B3_BAR and h >= B3_BAR:
        print("   underpowered rather than refuted — the interval still covers "
              "the bar")

print(f"\nB4 sigma: {above} merge ratio(s) above {B2_BAR:.0%} "
      f"(1 implies sigma ~ ERB, 3 implies ~ERB/2.5)")
print("   audible-horizon-calibration and suggest-reachability-filter both")
print("   re-adjudicate against this number.")

json.dump(dict(n_answered=len(rows), gate=dict(k=bk, n=bn, rate=b1,
                                               passed=bool(b1 >= GATE)),
               merge={r: dict(k=v[0], n=v[1]) for r, v in merge.items()},
               b4_count_above_bar=above),
          open(f"{HERE}/brocot_stageb_score.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_stageb_score.json")
