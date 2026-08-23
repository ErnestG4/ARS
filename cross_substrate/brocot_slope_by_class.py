"""DOES A CLASS'S POSITION IN D_Q PREDICT ITS OWN DOSE-RESPONSE SLOPE?

COMMITTED GENERATOR of cross_substrate/brocot_slope_by_class.json.
Prediction and verdict sealed here, before any output exists.

THE TWO FINDINGS THIS TESTS FOR UNITY
--------------------------------------
1. ATTENUATION (brocot_attenuation.json): pooled slope collapses from +4.48 to
   +1.16 in the top-D_Q tercile — the relation flattens toward the RIGID end,
   substantively, beyond range restriction.
2. CLASS SPLIT (brocot_within_between.json): within-class slopes split into
   strong (liouville +8.63, pi_minus_3 +7.86, generic +4.94) and flat
   (golden +0.31, e_minus_2 +0.28, ln2 +0.81, metallic4 -0.81).

These may be ONE phenomenon. In this population larger D_Q means harder to
approximate — golden, the least approximable number, sits at D_Q = 0.382 — so
the top tercile IS the rigid end. If the flat classes are the ones sitting there,
then "the relation flattens toward the rigid end" and "some classes have no
dose-response" are the same statement read across two different cuts.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTION                                                             ║
║                                                                              ║
║ S1  rho(class-mean D_Q, within-class slope) is NEGATIVE across the 10         ║
║     classes: classes sitting at the rigid end have flatter slopes.           ║
║ S2  It survives controlling for POWER. A class with little internal D_Q       ║
║     spread has an unreliable slope, so the association must not be explained  ║
║     by SD(D_Q) within class: the partial rho controlling for within-class     ║
║     SD(D_Q) stays negative.                                                   ║
║                                                                              ║
║ S2 IS THE ARM THAT MATTERS. Without it, "rigid classes have flat slopes"      ║
║ could just be "rigid classes are narrow, so their slopes are noise centred    ║
║ on zero" — a power artifact wearing a finding's clothes. The repo has paid    ║
║ for that shape before.                                                       ║
║                                                                              ║
║ VERDICT LATTICE                                                              ║
║   UNIFIED             S1 and S2 both hold                                    ║
║   POWER_CONFOUNDED    S1 holds, S2 does not                                  ║
║   NOT_UNIFIED         S1 does not hold                                       ║
║                                                                              ║
║ n = 10 classes. That is a SMALL sample for a correlation and the CI will be   ║
║ wide; the verdict is reported with it, and a wide CI is stated as a bound,    ║
║ never as a null.                                                             ║
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
WB = json.load(open(f"{HERE}/brocot_within_between.json"))
DEPTH = SRC["depth"]
SEED, BOOT = 20260823, 4000

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

classes = sorted(set(CLS))
mean_D, slope, sd_D, ns = [], [], [], []
for c in classes:
    m = CLS == c
    mean_D.append(D[m].mean())
    slope.append(float(np.polyfit(D[m], U[m], 1)[0]))
    sd_D.append(float(D[m].std(ddof=1)))
    ns.append(int(m.sum()))
mean_D, slope, sd_D = np.array(mean_D), np.array(slope), np.array(sd_D)

# cross-check against the banked within/between run
for i, c in enumerate(classes):
    banked = WB["within"].get(c, {})
    if banked.get("status") == "MEASURED":
        assert abs(banked["slope"] - slope[i]) < 1e-9, f"slope mismatch for {c}"

rho_s1 = float(stats.spearmanr(mean_D, slope)[0])

# partial Spearman controlling for within-class SD(D_Q), via ranks + residuals
def partial_rho(x, y, z):
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return float(stats.pearsonr(ex, ey)[0])


rho_s2 = partial_rho(mean_D, slope, sd_D)

rng = np.random.default_rng(SEED)
b1, b2 = [], []
k = len(classes)
for _ in range(BOOT):
    idx = rng.integers(0, k, k)
    if len(set(idx.tolist())) < 4:
        continue
    try:
        b1.append(stats.spearmanr(mean_D[idx], slope[idx])[0])
        b2.append(partial_rho(mean_D[idx], slope[idx], sd_D[idx]))
    except Exception:                                             # noqa: BLE001
        continue
b1 = np.asarray([v for v in b1 if np.isfinite(v)])
b2 = np.asarray([v for v in b2 if np.isfinite(v)])
lo1, hi1 = np.percentile(b1, [2.5, 97.5])
lo2, hi2 = np.percentile(b2, [2.5, 97.5])

s1 = rho_s1 < 0 and hi1 < 0
s2 = rho_s2 < 0 and hi2 < 0
verdict = ("UNIFIED" if s1 and s2 else
           "POWER_CONFOUNDED" if s1 and not s2 else "NOT_UNIFIED")

print(f"{'class':12s} {'n':>4s} {'mean D_Q':>9s} {'SD(D_Q)':>9s} {'slope':>10s}")
for i, c in enumerate(classes):
    print(f"  {c:10s} {ns[i]:>4d} {mean_D[i]:>9.4f} {sd_D[i]:>9.4f} {slope[i]:>10.4f}")

print(f"\nS1  rho(class-mean D_Q, within-class slope) = {rho_s1:+.3f}   "
      f"95% CI [{lo1:+.3f}, {hi1:+.3f}]   {'MET' if s1 else 'MISSED'}")
print(f"S2  partial rho controlling for within-class SD(D_Q) = {rho_s2:+.3f}   "
      f"95% CI [{lo2:+.3f}, {hi2:+.3f}]   {'MET' if s2 else 'MISSED'}")
print(f"    (n = {k} classes — a small sample; the CI is the bound, and a wide "
      f"one is not a null)")
print(f"\nVERDICT: {verdict}")

with redpath("classes contributing a slope", expect_min=8) as rp:
    rp.observed(k)

json.dump(dict(classes=classes, n=ns, mean_D=mean_D.tolist(), sd_D=sd_D.tolist(),
               slope=slope.tolist(), rho_position_vs_slope=rho_s1, ci_s1=[lo1, hi1],
               partial_rho_controlling_power=rho_s2, ci_s2=[lo2, hi2],
               predictions=dict(S1=bool(s1), S2=bool(s2)), verdict=verdict,
               seed=SEED, n_boot=BOOT),
          open(f"{HERE}/brocot_slope_by_class.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_slope_by_class.json")
