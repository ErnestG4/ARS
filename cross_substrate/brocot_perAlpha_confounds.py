"""Confound audit for brocot_perAlpha's rho(D_Q, q) = +0.699.
COMMITTED GENERATOR of cross_substrate/brocot_perAlpha_confounds.json.

Two ways that correlation could be real-looking and mean nothing:

  C1  PARTIAL-COUNT.  Near-resonance means k1 + k2*alpha ~ 0 for small k, so
      strongly-approximable alpha have COLLIDING sidebands and fewer DISTINCT
      partials.  If n tracks D_Q, then q may be tracking sample size (a fit
      property) rather than approximability (a substrate property).  Stage 1
      saw n in 343-345 across all nine classes, which is reassuring but was
      never checked against the generic alphas or measured as a correlation.

  C2  THE BRODY RAIL.  I8_brody_q is bounded to [0,1] and stage 1 returned
      EXACTLY 1.000 for four of nine banked representatives -- railed values.
      A rank correlation computed over a pile of ties at a bound can be driven
      entirely by which side of the rail things fall on.  The repo already
      carries an unbounded estimator (I8_brody_q_unbounded) precisely for this,
      so the test is to re-run the correlation through it.

A confound that survives either check does not merely weaken the result, it
replaces it: C1 would make this a statement about collision counts and C2 a
statement about a fitter's boundary.
"""
import json, os, sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.expandvars("$HOME/fmexplorer/brocot"), os.path.dirname(_HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)
from phase3.partial_prediction import predict_partials                        # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q, I8_brody_q_unbounded  # noqa: E402
from brocot_within_class import DEPTH, F_CARRIER                              # noqa: E402
from scipy import stats                                                       # noqa: E402

src = json.load(open(f"{_HERE}/brocot_perAlpha.json"))
rows = src["rows"]
rng = np.random.default_rng(7)


def ci(x, y, n_boot=2000):
    x, y = np.asarray(x, float), np.asarray(y, float)
    r = float(stats.spearmanr(x, y)[0])
    bs = [stats.spearmanr(x[i], y[i])[0]
          for i in (rng.integers(0, len(x), len(x)) for _ in range(n_boot))]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return r, float(lo), float(hi)


out = {"n": len(rows)}
n_part, q_unb = [], []
for r in rows:
    sp = predict_partials([1.0, r["alpha"]], [DEPTH, DEPTH], f_carrier=F_CARRIER)
    n_part.append(int(sp.freqs.size))
    q_unb.append(I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs))))
n_part = np.array(n_part, float)
q = np.array([r["q"] for r in rows], float)
D = np.array([r["D"] for r in rows], float)
q_unb = np.array([v if v is not None else np.nan for v in q_unb], float)

print("C1 -- PARTIAL COUNT")
print(f"  n_partials range {int(n_part.min())}-{int(n_part.max())}  sd {n_part.std():.2f}")
r1 = ci(D, n_part); r2 = ci(n_part, q)
print(f"  rho(D_Q, n_partials) = {r1[0]:+.3f}  [{r1[1]:+.3f}, {r1[2]:+.3f}]")
print(f"  rho(n_partials, q)   = {r2[0]:+.3f}  [{r2[1]:+.3f}, {r2[2]:+.3f}]")
out["C1"] = dict(n_range=[int(n_part.min()), int(n_part.max())], n_sd=float(n_part.std()),
                 rho_D_n=r1, rho_n_q=r2)

print("\nC2 -- BRODY RAIL")
railed = int(np.sum(q >= 0.999))
print(f"  bounded q at the rail (>=0.999): {railed}/{len(q)} = {railed/len(q):.1%}")
m = np.isfinite(q_unb)
r3 = ci(D[m], q_unb[m])
print(f"  rho(D_Q, q) bounded    = {ci(D, q)[0]:+.3f}   (deployed, from stage 2)")
print(f"  rho(D_Q, q) UNBOUNDED  = {r3[0]:+.3f}  [{r3[1]:+.3f}, {r3[2]:+.3f}]   n={int(m.sum())}")
print(f"  unbounded q range {np.nanmin(q_unb):+.3f} to {np.nanmax(q_unb):+.3f}")
out["C2"] = dict(railed_frac=railed / len(q), rho_unbounded=r3,
                 q_unb_range=[float(np.nanmin(q_unb)), float(np.nanmax(q_unb))])

# partial correlation of D and q controlling for n, via rank residuals
rk = lambda v: stats.rankdata(v)
res = lambda a, b: rk(a) - np.polyval(np.polyfit(rk(b), rk(a), 1), rk(b))
r4 = ci(res(D, n_part), res(q, n_part))
print(f"\n  PARTIAL rho(D_Q, q | n_partials) = {r4[0]:+.3f}  [{r4[1]:+.3f}, {r4[2]:+.3f}]")
out["partial_rho_controlling_n"] = r4
surv = bool(r4[1] > 0 and r3[1] > 0)
out["verdict"] = ("SURVIVES_BOTH" if surv else "CONFOUNDED")
print(f"\n  VERDICT: {out['verdict']}")
json.dump(out, open(f"{_HERE}/brocot_perAlpha_confounds.json", "w"), indent=1)
