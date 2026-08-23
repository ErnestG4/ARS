"""THE INSTRUMENT'S TIMBRAL GRADIENT ACROSS ITS OWN RATIO RANGE.

COMMITTED GENERATOR of cross_substrate/brocot_ratio_sensitivity.json.
Prediction and verdict sealed here, before any output exists.

WHY THIS IS THE SYNTH-FACING MEASUREMENT
-----------------------------------------
`source/pull/Landscape.h` routes between timbre families by PARAMETER DISTANCE —
"a depth-weighted ratio histogram of the current patch vs each node" — and walks
waypoints with `PullIndex::morph`. That design assumes equal parameter distance
buys equal timbral change.

The saturation result says it does not: d(rigidity)/d(D_Q) is ~+5 at the
approximable end and ~+0.5 at the rigid end. But D_Q is not what the Landscape
moves along — it moves along RATIO. So the number the instrument needs is the
local gradient in RATIO space:

    g(alpha) = | u(alpha + delta) - u(alpha) | / delta

measured at the modulation index the instrument actually uses, over the ratio
range BROCOT-SPEC.md §1 names as the defining regime:

    "Modulators sit at NEAR-UNITY ratios ... slightly above (4/3 ~ 1.333,
     9/7 ~ 1.286, 14/11 ~ 1.273, 43/34 ~ 1.265) or slightly below (3/4 = 0.75,
     7/9 ~ 0.778, 11/14 ~ 0.786)."

So the sweep runs alpha in [0.70, 1.40] at I = 0.9, the spec's typical index —
NOT the I = 8 this programme had been measuring at.

WHAT A NON-UNIFORM GRADIENT WOULD MEAN FOR THE INSTRUMENT
----------------------------------------------------------
A morph that crosses a high-gradient region changes timbre fast and one crossing
a plateau barely changes at all, for the same distance travelled. That is
audible as a morph that lurches and then stalls — and it is a property of the
soundspace, not a bug in the interpolator, so it cannot be fixed by smoothing
the path. It can only be fixed by making the METRIC match the gradient.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ G1  The gradient is strongly NON-UNIFORM across the defining ratio range:    ║
║     the 90th percentile of g is at least 5x the 10th percentile.             ║
║ G2  It is structured, not noise: gradient near simple rationals (small        ║
║     denominator q <= 4) is HIGHER than in the noble/metallic neighbourhoods.  ║
║ G3  The unity ratio 1/1 sits in the highest gradient decile — it is the       ║
║     strongest resonance in the range.                                        ║
║                                                                              ║
║ G2 IS THE ONE THAT COULD FAIL HONESTLY. Near a simple rational the partials   ║
║ COINCIDE, which can make the spacing statistic degenerate rather than         ║
║ sensitive — a high gradient there might be the estimator destabilising, not   ║
║ the timbre moving. So the run also records how many partials survive at each  ║
║ alpha; a gradient spike coinciding with a partial-count collapse is reported  ║
║ as ESTIMATOR_UNSTABLE, never as sensitivity.                                  ║
║                                                                              ║
║ VERDICT LATTICE                                                              ║
║   NON_UNIFORM_STRUCTURED   G1 and G2 both hold, no instability confound       ║
║   NON_UNIFORM_UNSTRUCTURED G1 holds, G2 does not                              ║
║   UNIFORM                  G1 fails: parameter distance IS timbral distance,  ║
║                            and the Landscape's metric needs no correction     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                                 # noqa: E402
from phase3.partial_prediction import predict_partials                      # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded   # noqa: E402

I_MUSICAL = 0.9          # BROCOT-SPEC.md: "I ~ 0.9 typically"
LO, HI, N = 0.70, 1.40, 561
DELTA = 0.002            # a small ratio step, well inside a tree hop
MIN_PARTIALS = 20


def u_at(alpha):
    sp = predict_partials([1.0, float(alpha)], [I_MUSICAL, I_MUSICAL], f_carrier=220.0)
    if sp.freqs.size < MIN_PARTIALS:
        return None, sp.freqs.size
    val = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    return (None if val is None else float(val)), sp.freqs.size


def nearest_simple(alpha, max_q=4):
    """Denominator of the nearest rational with q <= max_q, and the distance."""
    best, bd = None, 1e9
    for q in range(1, max_q + 1):
        p = round(alpha * q)
        if p == 0:
            continue
        d = abs(alpha - p / q)
        if d < bd:
            best, bd = Fraction(p, q), d
    return best, bd


alphas = np.linspace(LO, HI, N)
grad, counts, uvals = [], [], []
for a in alphas:
    u0, n0 = u_at(a)
    u1, n1 = u_at(a + DELTA)
    counts.append(min(n0, n1))
    if u0 is None or u1 is None:
        grad.append(np.nan); uvals.append(np.nan)
    else:
        grad.append(abs(u1 - u0) / DELTA); uvals.append(u0)
grad = np.array(grad, float)
counts = np.array(counts)
ok = np.isfinite(grad)

p10, p50, p90 = np.nanpercentile(grad, [10, 50, 90])
ratio_90_10 = p90 / p10 if p10 > 0 else np.inf

# structure: near a simple rational vs not
dists = np.array([nearest_simple(a)[1] for a in alphas])
near = ok & (dists < 0.01)
far = ok & (dists > 0.05)
g_near, g_far = float(np.median(grad[near])), float(np.median(grad[far]))

# instability guard: does a gradient spike coincide with a partial-count collapse?
hi_grad = ok & (grad > p90)
median_count_all = float(np.median(counts[ok]))
median_count_spike = float(np.median(counts[hi_grad])) if hi_grad.any() else float("nan")
unstable = median_count_spike < 0.7 * median_count_all

# where does 1/1 sit?
i_unity = int(np.argmin(np.abs(alphas - 1.0)))
unity_pct = float((grad[ok] < grad[i_unity]).mean() * 100) if np.isfinite(grad[i_unity]) else np.nan

g1 = ratio_90_10 >= 5.0
g2 = g_near > g_far
g3 = np.isfinite(unity_pct) and unity_pct >= 90.0
verdict = ("NON_UNIFORM_STRUCTURED" if g1 and g2 and not unstable else
           "NON_UNIFORM_UNSTRUCTURED" if g1 else "UNIFORM")

print(f"ratio sweep [{LO}, {HI}], {N} points, delta={DELTA}, I={I_MUSICAL} "
      f"(BROCOT-SPEC typical)")
print(f"  alphas with a measurable gradient: {int(ok.sum())} of {N}")
print(f"  median partials: {median_count_all:.0f}\n")
print(f"gradient |du/d(ratio)|:  p10 {p10:.2f}   median {p50:.2f}   p90 {p90:.2f}")
print(f"G1  p90/p10 = {ratio_90_10:.1f}x   (>= 5 ?)  {'MET' if g1 else 'MISSED'}")
print(f"G2  median gradient near a simple rational (q<=4, d<0.01) = {g_near:.2f}")
print(f"    median gradient far from one (d>0.05)                = {g_far:.2f}   "
      f"{'MET' if g2 else 'MISSED'}")
print(f"G3  ratio 1/1 sits at the {unity_pct:.0f}th percentile of gradient   "
      f"{'MET' if g3 else 'MISSED'}")
print(f"\ninstability guard: median partials at gradient spikes {median_count_spike:.0f} "
      f"vs {median_count_all:.0f} overall -> "
      f"{'ESTIMATOR_UNSTABLE' if unstable else 'no partial-count collapse'}")

print("\nhighest-gradient ratios in the defining regime:")
order = np.argsort(np.where(ok, -grad, np.inf))[:10]
for i in order:
    fr, d = nearest_simple(alphas[i])
    print(f"    alpha {alphas[i]:.4f}  gradient {grad[i]:8.2f}  nearest simple {fr} "
          f"(dist {d:.4f})  partials {counts[i]}")

print(f"\nVERDICT: {verdict}")

with redpath("alphas with a measurable gradient", expect_min=int(0.8 * N)) as rp:
    rp.observed(int(ok.sum()))

json.dump(dict(I=I_MUSICAL, lo=LO, hi=HI, n=N, delta=DELTA,
               p10=float(p10), p50=float(p50), p90=float(p90),
               ratio_90_10=float(ratio_90_10),
               gradient_near_simple=g_near, gradient_far=g_far,
               unity_percentile=unity_pct,
               median_partials=median_count_all,
               median_partials_at_spikes=median_count_spike,
               estimator_unstable=bool(unstable),
               predictions=dict(G1=bool(g1), G2=bool(g2), G3=bool(g3)),
               verdict=verdict,
               alphas=alphas.tolist(), gradient=grad.tolist(),
               partial_counts=counts.tolist()),
          open(f"{HERE}/brocot_ratio_sensitivity.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_ratio_sensitivity.json")
