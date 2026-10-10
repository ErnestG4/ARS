"""Diagnostic (not a gate): does the long-range Gaussian-weighted integral of the non-oscillating connected ζ function
converge in the prime cutoff? One in-pair node (d₁ = d₂ = 0.5), t = 4.12e8, b ∈ {100, 300}:
  I(b) = ∫_{|r| ≥ r_c} (W⋆W)(r)·(1 − χ(r))·C_non(r) dr / b,  (W⋆W)(r) = (b/√2)exp(−πr²/(2b²)), unit spacing,
χ a smooth cut (1 for r ≤ 10, cos² fall to 0 at r = 20); C_non even in r, so 2∫ over r > 0. Trapezoid, Δr = 0.5 and 0.25
(aliasing check). Prime cutoffs 1e4, 3e4, 1e5.

  python diag_pmax.py  ->  results/diag_pmax.json
"""
import json
import math
import os

import numpy as np

import cs4fastc as FC

HERE = os.path.dirname(os.path.abspath(__file__))


def chi(r):
    out = np.where(r <= 10, 1.0, 0.0)
    m = (r > 10) & (r < 20)
    out[m] = np.cos(0.5 * math.pi * (r[m] - 10) / 10) ** 2
    return out


def integral(model, b, dr):
    rmax = 6 * b / math.sqrt(math.pi)
    r = np.arange(10.0, rmax + dr, dr)
    ww = (b / math.sqrt(2)) * np.exp(-math.pi * r ** 2 / (2 * b * b))
    _, non = model.connected(0.5, 0.5, r, nonosc_only=True)
    f = ww * (1 - chi(r)) * non.real
    return float(2 * np.sum(f) * dr / b)


def main(pm, out):
    """One prime cutoff per process (v2, 2026-10-10: v1 looped all cutoffs in one process locally and was running at
    pmax 1e5 when the local machine froze). Run on spot with CS4_CHUNK sized to the prime count."""
    res = []
    Z = FC.FastZetaCached(4.12e8, pmax=pm)
    for b in (100, 300):
        for dr in (0.5, 0.25):
            v = integral(Z, b, dr)
            res.append(dict(pmax=pm, b=b, dr=dr, I=v))
            print(pm, b, dr, "%.10e" % v, flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, f"diag_pmax_{pm}.json"), "w"), indent=1)


if __name__ == "__main__":
    import sys
    main(int(sys.argv[1]), sys.argv[2])
