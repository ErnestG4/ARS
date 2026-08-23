"""B2's OPEN QUESTION — is the D_Q–rigidity attenuation SUBSTANTIVE or INSTRUMENTAL?

COMMITTED GENERATOR of cross_substrate/brocot_attenuation.json.
Predictions and verdict lattice are sealed in this docstring, before any output exists.

THE QUESTION, as B2 left it (overnight_2026_08_22/RESULTS_B1_B2.md)
-------------------------------------------------------------------
    "ATTENUATION WITHOUT REVERSAL. The D_Q–rigidity relation weakens substantially
     toward the rigid end — rho = 0.362 in the top-D_Q tercile against 0.658
     overall, roughly halved — direction preserved."
    "Open, noted and not pursued: whether the attenuation is SUBSTANTIVE (the
     relation genuinely saturates as approximability runs out) or INSTRUMENTAL
     (less dynamic range in q up there)."

WHY THIS IS DECIDABLE, AND WHY B2's OWN DESIGN IS WHAT MAKES IT SO
-------------------------------------------------------------------
B2 split on TERCILES OF THE PREDICTOR D_Q — deliberately, "never the outcome".
That choice, made to avoid manufacturing a correlation, also hands us the test:

    Under restriction on X, the OLS SLOPE beta(u|D) is unbiased, while the
    CORRELATION r attenuates by a known amount that depends only on how much
    X-variance was removed.

So correlation and slope come apart, and which one moves says which story is true:

  * r falls, slope HOLDS      -> the relation is the same line, measured over a
                                 shorter stretch of x. INSTRUMENTAL.
  * r falls AND slope falls   -> the line itself is flatter up there. SUBSTANTIVE.

The quantitative form: given the full-population Pearson r and the SD ratio
u = SD(D_top)/SD(D_full), pure X-restriction predicts

    r_pred = r_full * u / sqrt(r_full^2 * u^2 + 1 - r_full^2)

Observed r_top materially BELOW r_pred is attenuation beyond what removing
X-variance can account for.

A THIRD ARM, BECAUSE THE SEALED DICHOTOMY MAY BE FALSE
-------------------------------------------------------
"Substantive or instrumental" presumes those exhaust it. They do not. The
population is nine approximability CLASSES plus generics, and D_Q is close to a
class property — so the top-D_Q tercile may be dominated by a few classes whose q
spread is intrinsically narrow. Then the attenuation would be COMPOSITIONAL: not a
saturating relation and not a measurement limit, but a different mix of classes.
That is the pooled-vs-within defect this repo has recorded before, and a
two-option question cannot return it.

So: the within-class slope is measured too. If beta holds within class while the
pooled beta falls, the attenuation is compositional.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — committed with this generator, before any output         ║
║                                                                              ║
║ A1  The SD of D_Q in the top tercile is much smaller than in the full         ║
║     population: u = SD(D_top)/SD(D_full) < 0.5. (If u is near 1 the whole     ║
║     range-restriction account is inapplicable and the arm is INAPPLICABLE,    ║
║     not passed.)                                                             ║
║ A2  Pure X-restriction ALREADY predicts most of the observed drop:            ║
║     r_pred lands within 0.15 of the observed r_top.                          ║
║ A3  The OLS slope does NOT collapse: beta_top is within a factor of 2 of      ║
║     beta_full, and the bootstrap CI on (beta_top - beta_full) covers 0.       ║
║ A4  Therefore the headline verdict is INSTRUMENTAL.                           ║
║ A5  The compositional arm is LIVE but not decisive: the top tercile is        ║
║     class-skewed (top class >= 30% of the tercile), yet the within-class      ║
║     slope does not differ from the pooled slope beyond its CI.                ║
║                                                                              ║
║ A4 is the one I most expect to be wrong, and the informative failure is       ║
║ COMPOSITIONAL rather than SUBSTANTIVE — D_Q is so nearly a class label that   ║
║ a tercile split is close to a class split.                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

VERDICT LATTICE, fixed here rather than after seeing the numbers:

  INSTRUMENTAL   A3 holds (slope CI covers 0) AND A2 holds (r_pred within 0.15)
  SUBSTANTIVE    slope CI EXCLUDES 0 in the shrinking direction AND observed
                 r_top is below r_pred by more than 0.15
  COMPOSITIONAL  pooled slope falls but the WITHIN-CLASS slope does not
  INDETERMINATE  anything else, with the reason named and the power stated

POWER IS REPORTED IN BOTH DIRECTIONS. A CI on the slope difference that covers 0
means "no detected difference", never "no difference"; the half-width is printed
so a null is read as the bound it is.
"""
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from redpath import redpath   # noqa: E402

SRC = json.load(open(f"{HERE}/brocot_perAlpha.json"))
B1B2 = json.load(open(f"{ROOT}/overnight_2026_08_22/b1_b2_results.json"))
SEED = 20260823
BOOT = 4000

rows = [r for r in SRC["rows"] if r.get("D") is not None and r.get("q") is not None]
# The outcome is the UNBOUNDED axis B1/B2 used, recomputed the same way.
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from phase3.partial_prediction import predict_partials                      # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded   # noqa: E402

DEPTH = SRC["depth"]
data = []
for r in rows:
    sp = predict_partials([1.0, r["alpha"]], [DEPTH, DEPTH], f_carrier=220.0)
    if sp.freqs.size < 20:
        continue
    u = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    if u is None:
        continue
    data.append((float(r["D"]), float(u), r["cls"]))

D = np.array([d for d, _u, _c in data])
U = np.array([u for _d, u, _c in data])
CLS = np.array([c for _d, _u, c in data])
n = D.size

# sanity: this must reproduce B2's banked numbers or we are analysing a different set
rho_full = float(stats.spearmanr(D, U)[0])
banked_full = B1B2["B2"]["rho_full"]
assert abs(rho_full - banked_full) < 1e-9, (
    f"population mismatch: rho_full {rho_full} vs banked {banked_full}")

q1, q2 = np.percentile(D, [100 / 3, 200 / 3])
terciles = {"bottom": D < q1, "middle": (D >= q1) & (D < q2), "top": D >= q2}


def ols(x, y):
    return float(np.polyfit(x, y, 1)[0])


def summarise(mask):
    x, y = D[mask], U[mask]
    return dict(n=int(mask.sum()), sd_D=float(x.std(ddof=1)), sd_u=float(y.std(ddof=1)),
                pearson=float(stats.pearsonr(x, y)[0]),
                spearman=float(stats.spearmanr(x, y)[0]),
                slope=ols(x, y))


per_tercile = {k: summarise(m) for k, m in terciles.items()}
full = summarise(np.ones(n, bool))

# ── A1 / A2: does pure X-restriction account for the drop? ──────────────────
u_ratio = per_tercile["top"]["sd_D"] / full["sd_D"]
rf = full["pearson"]
r_pred = rf * u_ratio / np.sqrt(rf ** 2 * u_ratio ** 2 + 1 - rf ** 2)
r_obs = per_tercile["top"]["pearson"]
a1 = u_ratio < 0.5
a2 = abs(r_pred - r_obs) <= 0.15

# ── A3: does the SLOPE move? bootstrap the DIFFERENCE, resampling the whole
# population so the nesting of top-inside-full is respected ─────────────────
rng = np.random.default_rng(SEED)
diffs = []
for _ in range(BOOT):
    idx = rng.integers(0, n, n)
    d, uu = D[idx], U[idx]
    b, c = np.percentile(d, [100 / 3, 200 / 3])
    t = d >= c
    if t.sum() < 10 or np.ptp(d[t]) == 0:
        continue
    diffs.append(ols(d[t], uu[t]) - ols(d, uu))
diffs = np.asarray(diffs)
d_lo, d_hi = np.percentile(diffs, [2.5, 97.5])
slope_diff = per_tercile["top"]["slope"] - full["slope"]
a3 = (d_lo <= 0 <= d_hi) and abs(per_tercile["top"]["slope"]) <= 2 * abs(full["slope"])

# ── the compositional arm: within-class slope in the top tercile ────────────
top_mask = terciles["top"]
comp = {}
for c in sorted(set(CLS[top_mask])):
    m = top_mask & (CLS == c)
    if m.sum() >= 8 and np.ptp(D[m]) > 0:
        comp[c] = dict(n=int(m.sum()), slope=ols(D[m], U[m]),
                       pearson=float(stats.pearsonr(D[m], U[m])[0]))
class_counts = {c: int((CLS[top_mask] == c).sum()) for c in sorted(set(CLS[top_mask]))}
top_share = max(class_counts.values()) / top_mask.sum() if class_counts else 0.0
within_slopes = [v["slope"] for v in comp.values()]
within_median = float(np.median(within_slopes)) if within_slopes else float("nan")
a5 = top_share >= 0.30

# ── verdict ────────────────────────────────────────────────────────────────
pooled_slope_fell = (d_hi < 0) if full["slope"] > 0 else (d_lo > 0)
within_holds = (bool(within_slopes)
                and abs(within_median - full["slope"]) <= abs(slope_diff))
if a3 and a2:
    verdict = "INSTRUMENTAL"
elif pooled_slope_fell and abs(r_pred - r_obs) > 0.15:
    verdict = "SUBSTANTIVE"
elif pooled_slope_fell and within_holds:
    verdict = "COMPOSITIONAL"
else:
    verdict = "INDETERMINATE"

print(f"population: n={n}   rho_full={rho_full:+.3f} (matches banked {banked_full:+.3f})\n")
print(f"{'tercile':8s} {'n':>4s} {'SD(D_Q)':>9s} {'SD(u)':>9s} {'pearson':>8s} "
      f"{'spearman':>9s} {'slope':>10s}")
for k in ("bottom", "middle", "top"):
    t = per_tercile[k]
    print(f"  {k:6s} {t['n']:>4d} {t['sd_D']:>9.4f} {t['sd_u']:>9.4f} "
          f"{t['pearson']:>8.3f} {t['spearman']:>9.3f} {t['slope']:>10.4f}")
t = full
print(f"  {'FULL':6s} {t['n']:>4d} {t['sd_D']:>9.4f} {t['sd_u']:>9.4f} "
      f"{t['pearson']:>8.3f} {t['spearman']:>9.3f} {t['slope']:>10.4f}")

print(f"\nA1  SD ratio u = {u_ratio:.3f}   (< 0.5 ?)  {'MET' if a1 else 'MISSED'}")
print(f"A2  r predicted by pure X-restriction = {r_pred:+.3f}, observed = {r_obs:+.3f}, "
      f"|diff| = {abs(r_pred - r_obs):.3f}   (<= 0.15 ?)  {'MET' if a2 else 'MISSED'}")
print(f"A3  slope full = {full['slope']:+.4f}, top = {per_tercile['top']['slope']:+.4f}, "
      f"diff = {slope_diff:+.4f}")
print(f"    bootstrap 95% CI on the difference: [{d_lo:+.4f}, {d_hi:+.4f}]  "
      f"half-width {abs(d_hi - d_lo) / 2:.4f}   {'MET' if a3 else 'MISSED'}")
print(f"    POWER: a slope difference smaller than {abs(d_hi - d_lo) / 2:.4f} is NOT "
      f"detectable here; a covering CI is a bound, not an absence")
print(f"A5  top-tercile class mix: {class_counts}")
print(f"    largest class share = {top_share:.2f}   (>= 0.30 ?)  {'MET' if a5 else 'MISSED'}")
print(f"    within-class slopes in the top tercile: "
      f"{ {k: round(v['slope'], 4) for k, v in comp.items()} }")
print(f"    median within-class slope = {within_median:+.4f} vs pooled full "
      f"{full['slope']:+.4f}")

print(f"\nVERDICT: {verdict}")

# NON-VACUITY: the terciles must actually partition, and the compositional arm
# must have had classes to look at. An arm with nothing in it is INAPPLICABLE.
with redpath("terciles containing data", expect_min=3) as rp:
    rp.observed(sum(1 for m in terciles.values() if m.sum() > 0))
with redpath("classes with enough top-tercile members to fit a slope", expect_min=1) as rp:
    rp.observed(len(comp))

json.dump(dict(n=n, rho_full=rho_full, full=full, per_tercile=per_tercile,
               sd_ratio=u_ratio, r_pred=r_pred, r_obs=r_obs,
               slope_diff=slope_diff, slope_diff_ci=[d_lo, d_hi],
               top_class_counts=class_counts, top_class_share=top_share,
               within_class=comp, within_median_slope=within_median,
               predictions=dict(A1=bool(a1), A2=bool(a2), A3=bool(a3), A5=bool(a5)),
               verdict=verdict, seed=SEED, n_boot=BOOT),
          open(f"{HERE}/brocot_attenuation.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_attenuation.json")
