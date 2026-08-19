"""Stage 2: use the within-class scatter as SIGNAL, not noise.
COMMITTED GENERATOR of cross_substrate/brocot_perAlpha.json.

Stage 1 (brocot_within_class.py) found within-class spread ~= between-class
spread and rho CIs that touch zero, so "q tracks the LAGRANGE CLASS" is not
supported.  But it also pointed at why, and the why is a better experiment.

A Lagrange class is defined by the CF TAIL, i.e. by ASYMPTOTIC approximability.
The brocot substrate is a sideband lattice k1*1 + k2*alpha with |k| bounded by
the FM index -- so what it can possibly resolve is near-resonance at SMALL
denominators, which is fixed by the FIRST few CF terms and is exactly what
prepending terms changes.  Stage 1's "noise" is therefore not noise at all: it
is variation in the quantity the instrument actually responds to, and the class
label is simply the wrong x-axis.

So: measure approximability PER ALPHA at the scale the instrument probes, and
correlate against that instead.  n goes from 9 hand-picked class
representatives to ~250 alphas, and the x-axis becomes a measured property of
each alpha rather than a position in a hardcoded list.

  D_Q(alpha) = min_{1<=q<=Q} q * ||q*alpha||      (classic Markov-type; SMALL
               = strongly near-resonant = well approximated at reachable q)
  Q = 2 * depth, matched to the reachable sideband orders rather than assumed.

PREDICTION, COMMITTED BEFORE THE RUN: q correlates with D_Q at n~250 more
tightly than the class-mean correlation of stage 1 (|rho| > 0.5 with a CI clear
of zero).  If it does NOT, then the substrate does not track approximability at
any resolution and the original finding is an artifact of representative choice
alone -- which is the outcome that would close brocot rather than redirect it.
"""
import json, os, sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (os.path.expandvars("$HOME/fmexplorer/brocot"), _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)
from phase3.partial_prediction import predict_partials              # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q      # noqa: E402
from brocot_within_class import CLASSES, prepend_cf, DEPTH, F_CARRIER  # noqa: E402
from scipy import stats                                              # noqa: E402

Q_MAX = int(2 * DEPTH)          # matched to reachable sideband order, not assumed
N_PER_CLASS = 24
N_GENERIC = 40


def approx_D(alpha, Q=Q_MAX):
    """min_{1<=q<=Q} q*||q*alpha||  -- small = strongly near-resonant."""
    q = np.arange(1, Q + 1, dtype=float)
    r = np.abs(q * alpha - np.round(q * alpha))
    return float(np.min(q * r))


def cf_terms(alpha, m=8):
    x, out = float(alpha), []
    for _ in range(m):
        x = x - np.floor(x)
        if x < 1e-12:
            break
        x = 1.0 / x
        out.append(int(np.floor(x)))
    return out


def q_of(alpha):
    sp = predict_partials([1.0, float(alpha)], [DEPTH, DEPTH], f_carrier=F_CARRIER)
    if sp.freqs.size < 20:
        return None
    return I8_brody_q(canonical_spacings(np.sort(sp.freqs)))


def main():
    rng = np.random.default_rng(20260819)
    rows = []
    for name, alpha, mu, maxq in CLASSES:
        for i in range(N_PER_CLASS):
            a = alpha if i == 0 else prepend_cf(
                alpha, [int(v) for v in rng.integers(1, 6, size=int(rng.integers(1, 4)))])
            qv = q_of(a)
            if qv is not None:
                cf = cf_terms(a)
                rows.append(dict(alpha=float(a), cls=name, mu=mu, q=qv,
                                 D=approx_D(a), max_cf8=max(cf) if cf else 0,
                                 banked_rep=bool(i == 0)))
        print(f"  {name:12s} done ({sum(r['cls']==name for r in rows)} alphas)", flush=True)
    for _ in range(N_GENERIC):                      # coverage outside the 9 classes
        a = float(rng.random())
        qv = q_of(a)
        if qv is not None:
            cf = cf_terms(a)
            rows.append(dict(alpha=a, cls="generic", mu=None, q=qv, D=approx_D(a),
                             max_cf8=max(cf) if cf else 0, banked_rep=False))
    print(f"  generic done -> total n = {len(rows)}")

    q = np.array([r["q"] for r in rows]); D = np.array([r["D"] for r in rows])
    M = np.array([r["max_cf8"] for r in rows], float)
    out = dict(n=len(rows), Q_MAX=Q_MAX, depth=DEPTH, rows=rows, corr={})
    print(f"\n{'x-axis':28s} {'rho(x,q)':>10s} {'95% CI':>22s}")
    for xn, xv, sgn in (("D_Q (small=resonant)", D, "+"), ("max CF term (first 8)", M, "-")):
        r = float(stats.spearmanr(xv, q)[0])
        bs = [stats.spearmanr(xv[i], q[i])[0]
              for i in (rng.integers(0, len(q), len(q)) for _ in range(2000))]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out["corr"][xn] = dict(rho=r, ci95=[float(lo), float(hi)],
                               expected_sign=sgn, n=len(q))
        print(f"{xn:28s} {r:>+10.3f}   [{lo:+.3f}, {hi:+.3f}]")
    json.dump(out, open(f"{_HERE}/brocot_perAlpha.json", "w"), indent=1)


if __name__ == "__main__":
    main()
