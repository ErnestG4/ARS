"""IS THE D_Q-RIGIDITY RELATION WITHIN-CLASS OR BETWEEN-CLASS?

COMMITTED GENERATOR of cross_substrate/brocot_within_between.json.
Predictions and verdict lattice sealed here, before any output exists.

WHY THIS FOLLOWS DIRECTLY FROM THE ATTENUATION RESULT
------------------------------------------------------
`brocot_attenuation.json` established that the attenuation is SUBSTANTIVE: the
slope collapses from +4.48 to +1.16 with a CI excluding zero, beyond anything
predictor-range restriction can explain, and the top tercile is not class-skewed.

But the within-class slopes it measured inside the top tercile disagree in SIGN:

    bronze +1.61   e_minus_2 -1.07   golden -1.79
    ln2    +3.98   metallic4 +3.78   silver -0.37     (median +0.62)

Six classes, three signs each way. That is not what a within-class dose-response
looks like. It raises the question the attenuation test did not ask: is the
STRONG FULL-POPULATION relation (slope +4.48, rho +0.658) itself a BETWEEN-class
effect — classes sitting at different D_Q with different rigidity — rather than a
relation any individual class exhibits?

This repo has the rule already: WITHIN-SUBSTRATE BEFORE POOLED, because pooled
comparisons manufacture Simpson's. The rule was applied to substrates and not, so
far, to this population's own classes.

THE DECOMPOSITION
-----------------
By the law of total covariance, over classes g:

    Cov(D, u) = E_g[Cov(D, u | g)]  +  Cov_g(E[D|g], E[u|g])
                \___ WITHIN ____/      \____ BETWEEN _____/

If the between term carries the covariance, the relation is a statement about
where classes sit in D_Q — real, but not a dose-response, and the "saturation"
found in the attenuation test would then describe the SPACING OF CLASSES rather
than a curve any class traverses.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ W1  Within-class slopes disagree in sign across the FULL population too:     ║
║     at least 2 classes positive and at least 2 negative.                     ║
║ W2  The BETWEEN component carries most of the covariance:                    ║
║     |Cov_between| > |Cov_within|.                                            ║
║ W3  The median within-class slope is under 25% of the pooled slope.          ║
║ W4  Verdict: BETWEEN_CLASS_DOMINATED.                                        ║
║                                                                              ║
║ CONSEQUENCE, STATED IN ADVANCE so it is not a post-hoc rescue:               ║
║   If W4 holds, the SUBSTANTIVE attenuation verdict is RE-SCOPED, not          ║
║   withdrawn. "The relation saturates as approximability runs out" would then  ║
║   be a claim about how CLASSES are positioned in D_Q, not about a curve any   ║
║   single class traverses — and the attenuation artifact would say the class   ║
║   POSITIONS bunch toward the rigid end. Both readings are findings; they are  ║
║   different findings, and the banked wording must match the one measured.     ║
║                                                                              ║
║ `generic` is the one class expected to carry real within-class D_Q range, so  ║
║ it is reported separately: it is the only arm where a within-class            ║
║ dose-response COULD be seen at all, and an arm that cannot fire is            ║
║ INAPPLICABLE rather than evidence of absence.                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                                 # noqa: E402
from phase3.partial_prediction import predict_partials                      # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded   # noqa: E402

SRC = json.load(open(f"{HERE}/brocot_perAlpha.json"))
ATT = json.load(open(f"{HERE}/brocot_attenuation.json"))
DEPTH = SRC["depth"]
MIN_N = 8

data = []
for r in SRC["rows"]:
    if r.get("D") is None:
        continue
    sp = predict_partials([1.0, r["alpha"]], [DEPTH, DEPTH], f_carrier=220.0)
    if sp.freqs.size < 20:
        continue
    u = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    if u is None:
        continue
    data.append((float(r["D"]), float(u), r["cls"]))

D = np.array([d for d, _, _ in data])
U = np.array([u for _, u, _ in data])
CLS = np.array([c for _, _, c in data])
pooled_slope = float(np.polyfit(D, U, 1)[0])
assert abs(pooled_slope - ATT["full"]["slope"]) < 1e-9, "population mismatch vs attenuation run"

# ── within-class fits ───────────────────────────────────────────────────────
within = {}
for c in sorted(set(CLS)):
    m = CLS == c
    if m.sum() < MIN_N:
        within[c] = dict(n=int(m.sum()), status="INAPPLICABLE_TOO_FEW")
        continue
    if np.ptp(D[m]) == 0:
        within[c] = dict(n=int(m.sum()), status="INAPPLICABLE_NO_D_RANGE",
                         note="every member shares one D_Q; a slope is undefined")
        continue
    within[c] = dict(n=int(m.sum()), status="MEASURED",
                     sd_D=float(D[m].std(ddof=1)), sd_u=float(U[m].std(ddof=1)),
                     slope=float(np.polyfit(D[m], U[m], 1)[0]),
                     pearson=float(stats.pearsonr(D[m], U[m])[0]))

meas = {c: v for c, v in within.items() if v["status"] == "MEASURED"}
slopes = [v["slope"] for v in meas.values()]
pos = [c for c, v in meas.items() if v["slope"] > 0]
neg = [c for c, v in meas.items() if v["slope"] < 0]

# ── covariance decomposition (law of total covariance) ─────────────────────
n = D.size
cov_total = float(((D - D.mean()) * (U - U.mean())).sum() / (n - 1))
cov_within = 0.0
for c in set(CLS):
    m = CLS == c
    if m.sum() < 2:
        continue
    cov_within += ((D[m] - D[m].mean()) * (U[m] - U[m].mean())).sum()
cov_within /= (n - 1)
gm_D = np.array([D[CLS == c].mean() for c in sorted(set(CLS))])
gm_U = np.array([U[CLS == c].mean() for c in sorted(set(CLS))])
gn = np.array([(CLS == c).sum() for c in sorted(set(CLS))], float)
cov_between = float((gn * (gm_D - D.mean()) * (gm_U - U.mean())).sum() / (n - 1))
between_slope = float(np.polyfit(gm_D, gm_U, 1)[0])

median_within = float(np.median(slopes)) if slopes else float("nan")

w1 = len(pos) >= 2 and len(neg) >= 2
w2 = abs(cov_between) > abs(cov_within)
w3 = abs(median_within) < 0.25 * abs(pooled_slope)
verdict = ("BETWEEN_CLASS_DOMINATED" if w2 and w3
           else "WITHIN_CLASS_PRESENT" if not w2
           else "MIXED")

print(f"n = {n}   pooled slope = {pooled_slope:+.4f}   "
      f"(matches attenuation run {ATT['full']['slope']:+.4f})\n")
print(f"{'class':12s} {'n':>4s} {'SD(D_Q)':>9s} {'slope':>10s} {'pearson':>8s}  status")
for c in sorted(within):
    v = within[c]
    if v["status"] != "MEASURED":
        print(f"  {c:10s} {v['n']:>4d} {'—':>9s} {'—':>10s} {'—':>8s}  {v['status']}")
    else:
        print(f"  {c:10s} {v['n']:>4d} {v['sd_D']:>9.4f} {v['slope']:>10.4f} "
              f"{v['pearson']:>8.3f}  MEASURED")

print(f"\nW1  sign disagreement: {len(pos)} positive {sorted(pos)}, "
      f"{len(neg)} negative {sorted(neg)}   {'MET' if w1 else 'MISSED'}")
print(f"W2  Cov total {cov_total:+.5f} = within {cov_within:+.5f} + between "
      f"{cov_between:+.5f}")
print(f"    between share of |cov| = "
      f"{abs(cov_between) / (abs(cov_between) + abs(cov_within)):.3f}   "
      f"{'MET' if w2 else 'MISSED'}")
print(f"W3  median within-class slope {median_within:+.4f} vs pooled "
      f"{pooled_slope:+.4f}  ({abs(median_within) / abs(pooled_slope):.2f} of it)   "
      f"{'MET' if w3 else 'MISSED'}")
print(f"    between-class slope (class means) = {between_slope:+.4f}")
gen = within.get("generic", {})
print(f"\ngeneric (the only class with real within-class D_Q range): {gen}")

print(f"\nVERDICT: {verdict}")
if verdict == "BETWEEN_CLASS_DOMINATED":
    print("  RE-SCOPING, per the sealed consequence clause: the SUBSTANTIVE")
    print("  attenuation stands as measured, but it describes how CLASSES are")
    print("  POSITIONED in D_Q, not a dose-response any single class traverses.")

with redpath("classes with a measurable within-class slope", expect_min=2) as rp:
    rp.observed(len(meas))

json.dump(dict(n=n, pooled_slope=pooled_slope, within=within,
               positive=sorted(pos), negative=sorted(neg),
               cov_total=cov_total, cov_within=cov_within, cov_between=cov_between,
               between_share=abs(cov_between) / (abs(cov_between) + abs(cov_within)),
               between_slope=between_slope, median_within_slope=median_within,
               predictions=dict(W1=bool(w1), W2=bool(w2), W3=bool(w3)),
               verdict=verdict),
          open(f"{HERE}/brocot_within_between.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_within_between.json")
