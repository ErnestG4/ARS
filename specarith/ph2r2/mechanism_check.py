"""R₂ §3, post-hoc mechanism diagnostic (descriptive; written after the read, on seen bins).

Hypothesis (for Will's confirmatory design): S_f = ∫ f̂(τ)|A(τ)|² dτ, A = the window's empirical Fourier sum of the zeros.
For τ < 1 the explicit formula makes A(τ) a sum over the prime powers in a log-window that narrows as the window
lengthens. Few terms means |A|² fluctuates less than GUE's (Gaussian) |A|². So the variance reduction should (i) scale
with f̂'s variance weight below τ = 1, (ii) grow with block length, and (iii) weaken with height (more primes at fixed τ).

This script checks (i) on the eight family members already read (results/members): the fraction of the GUE-weighted
variance ∫|f̂|²K² below |τ| = 1 (K(τ) = min(|τ|, 1), unit mean spacing), against the zeros' drift-removed bootstrap growth
at 10,000 levels (full bins). Paired comparison: within each u, the wider bump (more weight below τ = 1) should shrink more.

  python mechanism_check.py  ->  results/members/MECHANISM_CHECK.md
"""
import json
import os

import numpy as np

import r2prep as P

HERE = os.path.dirname(os.path.abspath(__file__))
R = {n: json.load(open(os.path.join(HERE, "results", "members", f"{n}.json"))) for n in P.BINS}
tau = np.linspace(-6, 6, 24001)
K = np.minimum(np.abs(tau), 1.0)
rows, mean_g = [], {}
for u, w in P.FAMILY:
    k = f"{u}_{w}"
    F2 = (2 * np.cos(2 * np.pi * tau * u)) ** 2 * np.exp(-(2 * np.pi * tau * w) ** 2)
    frac = float((F2 * K ** 2)[np.abs(tau) < 1].sum() / (F2 * K ** 2).sum())
    g = [R[n][k]["A1_growth_drift_removed"][-1] for n in P.BINS]
    mean_g[k] = float(np.mean(g))
    rows.append(f"| ({u}, {w}) | {frac:.3f} | {' / '.join(f'{x:.2f}' for x in g)} | {np.mean(g):.2f} |")
pairs = [(u, mean_g[f"{u}_0.3"], mean_g[f"{u}_0.15"]) for u in (0.5, 1.0, 1.5, 2.0)]
ok = sum(a < b for _, a, b in pairs)
out = ["# R₂ §3 mechanism diagnostic (post-hoc, descriptive)", "",
       "| member (u, w) | variance weight below τ = 1 | zeros drift-removed growth at 10⁴, R1–R5 | mean |",
       "|---|---|---|---|", *rows, "",
       f"Paired (same u; w = 0.3 vs 0.15): the wider bump shrinks more in {ok} of 4 pairs "
       f"({', '.join(f'u={u}: {a:.2f} vs {b:.2f}' for u, a, b in pairs)}); one-sided sign test p = {0.5 ** ok:.4f} if 4/4.",
       "No matched GUE baseline for the non-primary members (the dry-run surrogates exist for the primary only).", ""]
open(os.path.join(HERE, "results", "members", "MECHANISM_CHECK.md"), "w").write("\n".join(out))
print("\n".join(out))
