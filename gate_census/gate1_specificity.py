"""GATE ENUMERATION #1 — arithmetic_toolkit._classify (93 dependent files).

Sharp question: is there a NAMED SET of things this gate should not fire on, and
was that set ever measured?

Read: the only refusal is n < 5 ('insufficient'). There is no goodness-of-fit
threshold and no 'none of the above' branch -- `best = min(...)` over exactly
three surmises. So its specificity against a NON-MEMBER distribution is not
merely unmeasured, it is structurally ZERO: every input with n >= 5 is assigned
one of Poisson/GOE/GUE. Measuring what it says on things that are none of them.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/combust/fmexplorer/criticality_tool')
from arithmetic_toolkit import _classify

rng = np.random.default_rng(4)
N = 2000
cases = {
    "PERFECT CLOCK (all spacings equal)":      np.ones(N),
    "UNIFORM spacings U(0,2)":                 rng.uniform(0, 2, N),
    "LOGNORMAL spacings (heavy tail)":         (lambda x: x / x.mean())(rng.lognormal(0, 1.2, N)),
    "BIMODAL (half 0.2, half 1.8)":            np.concatenate([np.full(N//2, .2), np.full(N//2, 1.8)]),
    "CLUSTERED (Neyman-Scott-ish)":            (lambda x: x / x.mean())(rng.exponential(1, N) * rng.choice([0.05, 3.0], N, p=[.7, .3])),
    "CONSTANT 0.5 + tiny noise":               0.5 + rng.normal(0, 1e-6, N),
    "--- genuine members, for contrast ---":   None,
    "true Poisson (exponential)":              (lambda x: x / x.mean())(rng.exponential(1, N)),
}
print("WHAT DOES THE 93-FILE CLASSIFIER SAY ABOUT THINGS THAT ARE NONE OF ITS THREE CLASSES?")
print(f"{'input':42s} {'verdict':>10s} {'ks_p':>7s} {'ks_o':>7s} {'ks_u':>7s}  best-fit quality")
n_labelled = 0
for name, sp in cases.items():
    if sp is None:
        print(f"{name:42s}"); continue
    sp = np.asarray(sp, float); sp = sp / sp.mean()
    c = _classify(sp)
    best_ks = min(c['ks_p'], c['ks_o'], c['ks_u'])
    # KS critical value at alpha=0.01 for n=2000 is ~1.63/sqrt(n)
    crit = 1.63 / np.sqrt(len(sp))
    flag = "FITS" if best_ks < crit else f"REJECTED by KS (D={best_ks:.3f} > {crit:.3f})"
    if c['best'] != 'insufficient':
        n_labelled += 1
    print(f"{name:42s} {c['best']:>10s} {c['ks_p']:7.3f} {c['ks_o']:7.3f} {c['ks_u']:7.3f}  {flag}")
print(f"\n  {n_labelled}/{sum(1 for v in cases.values() if v is not None)} inputs received a CLASS LABEL,")
print("  including every non-member. The gate has no way to say 'none of these'.")
