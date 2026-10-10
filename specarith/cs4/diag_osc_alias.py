"""Diagnostic: is gs_zeta's osc check (the ℓ-oscillating long-range part dropped by the split) aliased?

The long grid has Δr = 0.5. Two-pair oscillating pieces carry e^{∓2πi(x₃ + x₄ − x₁ − x₂)} = e^{∓4πir} (two cycles per
mean spacing), which sample to exactly 1 at Δr = 0.5: the trapezoid sees them as non-oscillating. On a Δr = 0.1 grid
(aliasing only at ±10 cycles per spacing) the same integrals should be ≈ 0 if G_S_DESIGN §3's claim holds.

For one node pair at one height, on r ∈ [5, R_MAX] with Δr = 0.1: the osc part's long-range integral against
(1 − χ)·exp(−πr²/2b²) for b = 100, 300 (R_MAX = 4.8·300), from (i) the full fine grid and (ii) its Δr = 0.5 subsample;
also the non-oscillating part the same two ways (should agree: its bandwidth is < 2 cycles per spacing).

  python diag_osc_alias.py ELL I J OUT
"""
import json
import math
import os
import sys

import numpy as np

import gs_unitary as G
import gs_zeta as Z

BS = (100, 300)


def main(ell, i, j, out):
    import cs4lr as LR
    lr = LR.LongRangeZeta(Z.tval(ell), pmax=Z.PMAX)
    n = int(round((4.8 * max(BS) - Z.R_LO) / 0.1)) + 1
    n += n % 2
    r = Z.R_LO + 0.1 * np.arange(n)
    o, nn = lr.connected(Z.DN[i], Z.DN[j], r)
    cl = 1 - G.chi(r)
    sub = slice(None, None, 5)                       # Δr = 0.5 subsample, the production grid's points
    res = dict(ell=ell, i=i, j=j, d1=Z.DN[i], d2=Z.DN[j])
    for name, f in (("osc", o.real), ("non", nn.real)):
        for b in BS:
            g = cl * Z.gb(r, b) * f
            res[f"{name}_fine_b{b}"] = float(2 * 0.1 * np.sum(g))
            res[f"{name}_coarse_b{b}"] = float(2 * 0.5 * np.sum(g[sub]))
    # spectrum of the osc part on the fine grid: where its power sits (cycles per mean spacing)
    w = np.hanning(n)
    sp = np.abs(np.fft.rfft(o.real * w))
    fr = np.fft.rfftfreq(n, 0.1)
    top = np.argsort(sp)[::-1][:8]
    res["osc_peak_freqs"] = sorted(float(fr[k]) for k in top)
    print(json.dumps(res), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, f"alias_L{ell}_{i}_{j}.json"), "w"), indent=1)


if __name__ == "__main__":
    main(float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
