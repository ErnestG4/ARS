"""B1 + B2 — brocot re-run on the FULL population with the unbounded axis primary.
COMMITTED GENERATOR of overnight_2026_08_22/b1_b2_results.json.
Scored against overnight_2026_08_22/SEALED_CRITERIA.md (committed 82e408e, before this file).
"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
R = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, R); sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from phase3.partial_prediction import predict_partials                      # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded   # noqa: E402
from scipy import stats                                                     # noqa: E402

src = json.load(open(f"{R}/cross_substrate/brocot_perAlpha.json"))
DEPTH = src["depth"]
MAXQ = {"golden": 1, "silver": 2, "bronze": 3, "metallic4": 4, "metallic5": 5,
        "e_minus_2": 99, "ln2": 99, "pi_minus_3": 99, "liouville": 99}
METALLIC = ["golden", "silver", "bronze", "metallic4", "metallic5"]

rows = []
for r in src["rows"]:
    sp = predict_partials([1.0, r["alpha"]], [DEPTH, DEPTH], f_carrier=220.0)
    if sp.freqs.size < 20:
        continue
    u = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    if u is None:
        continue
    rows.append(dict(cls=r["cls"], D=r["D"], u=float(u)))
print(f"full population: {len(rows)} alpha, NO selection\n")
rng = np.random.default_rng(20260822)

# ---- B1: per-class ordering, metallic classes, full population -------------
def b1(classes):
    med = {c: float(np.median([r["u"] for r in rows if r["cls"] == c])) for c in classes}
    xs = np.array([MAXQ[c] for c in classes], float)
    ys = np.array([med[c] for c in classes], float)
    rho = float(stats.spearmanr(xs, ys)[0])
    boots = []
    for _ in range(2000):
        m = [float(np.median(rng.choice([r["u"] for r in rows if r["cls"] == c],
                                        size=sum(1 for r in rows if r["cls"] == c))))
             for c in classes]
        boots.append(stats.spearmanr(xs, m)[0])
    b = np.asarray([x for x in boots if np.isfinite(x)])
    lo, hi = np.percentile(b, [2.5, 97.5])
    return med, rho, float(lo), float(hi)

med5, rho5, lo5, hi5 = b1(METALLIC)
print("B1 — per-class median unbounded q (metallic classes, full population):")
for c in METALLIC:
    print(f"    {c:11s} maxq={MAXQ[c]}  median {med5[c]:+.4f}")
print(f"  rho(maxq, median q) = {rho5:+.3f}   95% CI [{lo5:+.3f}, {hi5:+.3f}]")
b1_pass = bool(rho5 <= -0.60 and not (lo5 <= 0 <= hi5))
print(f"  SEALED: survives iff rho <= -0.60 AND CI excludes 0  ->  "
      f"{'SURVIVES' if b1_pass else 'DOES NOT SURVIVE'}")
med9, rho9, lo9, hi9 = b1(list(MAXQ))
print(f"  (secondary, reported not scored: 9-class rho = {rho9:+.3f} "
      f"[{lo9:+.3f}, {hi9:+.3f}])\n")

# ---- B2: terciles of the PREDICTOR, never the outcome ----------------------
D = np.array([r["D"] for r in rows]); U = np.array([r["u"] for r in rows])
q1, q2 = np.percentile(D, [100/3, 200/3])
top = D >= q2
rho_top = float(stats.spearmanr(D[top], U[top])[0])
bt = [stats.spearmanr(D[top][i], U[top][i])[0]
      for i in (rng.integers(0, top.sum(), top.sum()) for _ in range(2000))]
bt = np.asarray([x for x in bt if np.isfinite(x)])
lo_t, hi_t = np.percentile(bt, [2.5, 97.5])
print(f"B2 — split on D_Q terciles (selection on the PREDICTOR, never the outcome):")
print(f"  full-population rho(D_Q, u) = {stats.spearmanr(D,U)[0]:+.3f}  (n={len(rows)})")
print(f"  TOP-D_Q tercile rho = {rho_top:+.3f}  95% CI [{lo_t:+.3f}, {hi_t:+.3f}]  n={int(top.sum())}")
b2_pass = bool(rho_top < 0 and hi_t < 0)
print(f"  SEALED: reversal is real iff NEGATIVE and CI excludes 0  ->  "
      f"{'REVERSAL SURVIVES' if b2_pass else 'REVERSAL DOES NOT SURVIVE — subgroup result stays retired'}")

json.dump(dict(n=len(rows), B1=dict(medians_metallic=med5, rho=rho5, ci=[lo5,hi5],
                                    passes=b1_pass, secondary_9class=[rho9,lo9,hi9]),
               B2=dict(rho_top_tercile=rho_top, ci=[lo_t,hi_t], n_top=int(top.sum()),
                       rho_full=float(stats.spearmanr(D,U)[0]), passes=b2_pass)),
          open(f"{R}/overnight_2026_08_22/b1_b2_results.json", "w"), indent=1)
