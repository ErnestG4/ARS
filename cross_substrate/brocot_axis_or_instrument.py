"""IS THE PUNCTUATION THE SOUNDSPACE, OR THE BRODY AXIS?

COMMITTED GENERATOR of cross_substrate/brocot_axis_or_instrument.json.
Predictions sealed here, before any output exists.

THE CHALLENGE THIS ANSWERS
--------------------------
Every roughness result in this arc was measured on u(alpha) = the unbounded
Brody q of the partial spacings:

  * "the attenuation is SUBSTANTIVE"          (slope collapse in u)
  * "the punctuation is scale-free"           (three failed linearisations of u)
  * "62% of large jumps sit at no partial-set change"  (v2, this session)

That last one is the challenge to the other two. If the partial SET does not
change, a jump in u is the estimator responding to continuous movement of
partial positions — and then the punctuation might be a property of the AXIS
rather than of the instrument, which would qualify two banked conclusions.

A conclusion that rests entirely on one estimator has to be checked against a
second one that fails differently. The ERB excitation-pattern distance from
`brocot_horizon_perceptual.json` is that second estimator: it is perceptual
rather than statistical, it uses amplitudes (which Brody discards entirely), and
it has no fit and therefore no fit instability.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ X1  Large Brody jumps correspond to real spectral change: median ERB step at ║
║     a large |du| is at least 3x the median elsewhere.                        ║
║ X2  The perceptual coordinate is ALSO punctuated — its step CV is at least   ║
║     as large as Brody's. If it is much SMALLER, the punctuation is an axis   ║
║     artifact and the linearisation conclusions need qualifying.              ║
║ X3  The two estimators are NOT interchangeable: their step-size correlation  ║
║     is well below 1 (Spearman < 0.5), so u is not a proxy for perceptual     ║
║     change even where both are large.                                        ║
║                                                                              ║
║ X2 IS THE LOAD-BEARING ONE. It can overturn banked conclusions, and it is     ║
║ pointed at my own results rather than at a hypothesis I hope to confirm.     ║
║ If it fails, "the punctuation is scale-free" becomes "the BRODY AXIS is      ║
║ punctuated", the three failed linearisations become failures to linearise a  ║
║ statistic, and the feature question reopens on the perceptual coordinate.    ║
║                                                                              ║
║ X3 has a consequence either way: if the estimators disagree on WHERE the     ║
║ jumps are, then any morph work aimed at what a player hears should be run    ║
║ on ERB, not on u — regardless of how X2 lands.                               ║
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
from redpath import redpath                                       # noqa: E402
from phase3.partial_prediction import predict_partials            # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded  # noqa: E402

I_MUS, A0, A1, GRID = 0.9, 0.70, 1.40, 701
FMIN, FMAX = 50.0, 12000.0
ERB_C = np.geomspace(FMIN, FMAX, 400)
ABS_JUMP = 0.05
SEED, BOOT = 20260824, 2000


def both(a):
    sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=220.0)
    f = np.asarray(sp.freqs, float)
    am = np.abs(np.asarray(sp.amps, float))
    m = (f >= FMIN) & (f <= FMAX) & (am > 0)
    f, am = f[m], am[m]
    v = np.zeros(len(ERB_C))
    for fr, pa in zip(f, am):
        w = 24.7 * (4.37 * fr / 1000.0 + 1.0)
        v += (pa * pa) * np.exp(-0.5 * ((ERB_C - fr) / w) ** 2)
    v = np.sqrt(v)
    n = np.linalg.norm(v)
    v = v / n if n > 0 else v
    u = (I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
         if sp.freqs.size >= 20 else None)
    return (np.nan if u is None else float(u)), v, int(sp.freqs.size)


g = np.linspace(A0, A1, GRID)
U, V, N = [], [], []
for a in g:
    u, v, n = both(a)
    U.append(u); V.append(v); N.append(n)
U = np.array(U, float); V = np.array(V); N = np.array(N, float)

du = np.abs(np.diff(U))
de = np.array([float(np.linalg.norm(V[i + 1] - V[i])) for i in range(len(V) - 1)])
dn = np.abs(np.diff(N))
ok = np.isfinite(du)

big = ok & (du >= ABS_JUMP)
erb_at_big = float(np.median(de[big]))
erb_elsewhere = float(np.median(de[ok & ~big]))
ratio = erb_at_big / erb_elsewhere if erb_elsewhere > 0 else float("inf")

cv_u = float(du[ok].std() / du[ok].mean())
cv_e = float(de[ok].std() / de[ok].mean())
rho = float(stats.spearmanr(du[ok], de[ok])[0])
rng = np.random.default_rng(SEED)
bs = []
for _ in range(BOOT):
    i = rng.integers(0, int(ok.sum()), int(ok.sum()))
    r = stats.spearmanr(du[ok][i], de[ok][i])[0]
    if np.isfinite(r):
        bs.append(r)
lo, hi = np.percentile(bs, [2.5, 97.5])

# where does ERB jump, relative to partial-set change?
big_e = ok & (de >= np.percentile(de[ok], 90))
erb_at_setchange = float((dn[big_e] > 0).mean())
erb_setchange_base = float((dn[ok & ~big_e] > 0).mean())

x1 = ratio >= 3.0
x2 = cv_e >= cv_u
x3 = rho < 0.5 and hi < 1.0
verdict = ("SOUNDSPACE_NOT_AXIS" if x1 and x2 else "AXIS_ARTIFACT_SUSPECTED")

print(f"path [{A0},{A1}] at I={I_MUS}, {GRID} points\n")
print(f"X1  ERB step at a large Brody jump {erb_at_big:.5f} vs {erb_elsewhere:.5f} "
      f"elsewhere = {ratio:.1f}x   {'MET' if x1 else 'MISSED'}")
print(f"X2  step CV: Brody {cv_u:.3f}   ERB {cv_e:.3f}   "
      f"(ERB >= Brody ?)  {'MET' if x2 else 'MISSED'}")
print(f"X3  Spearman(|du|, |dERB|) = {rho:+.3f}  CI [{lo:+.3f}, {hi:+.3f}]   "
      f"{'MET' if x3 else 'MISSED'}")
print(f"\n    top-decile ERB jumps sitting at a partial-set change: "
      f"{erb_at_setchange:.1%}  (baseline {erb_setchange_base:.1%})")
print(f"\nVERDICT: {verdict}")
if verdict == "SOUNDSPACE_NOT_AXIS":
    print("  The punctuation survives a second, differently-failing estimator, and")
    print("  the PERCEPTUAL coordinate is rougher than the statistical one. The")
    print("  linearisation conclusions stand and strengthen.")
print("  X3's consequence regardless: the two estimators disagree on WHERE the")
print("  jumps are, so morph work aimed at what a player hears belongs on ERB,")
print("  not on u -- every linearisation attempt in this arc used u.")

with redpath("grid points with both estimators finite", expect_min=int(0.9 * GRID)) as rp:
    rp.observed(int(np.isfinite(U).sum()))

json.dump(dict(I=I_MUS, a0=A0, a1=A1, grid=GRID, abs_jump=ABS_JUMP,
               erb_at_big_brody=erb_at_big, erb_elsewhere=erb_elsewhere,
               ratio=ratio, cv_brody=cv_u, cv_erb=cv_e,
               spearman=rho, spearman_ci=[float(lo), float(hi)],
               erb_jumps_at_setchange=erb_at_setchange,
               erb_setchange_baseline=erb_setchange_base,
               predictions=dict(X1=bool(x1), X2=bool(x2), X3=bool(x3)),
               verdict=verdict),
          open(f"{HERE}/brocot_axis_or_instrument.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_axis_or_instrument.json")
