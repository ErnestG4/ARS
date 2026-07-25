"""
arsrh/phase1_density_check.py — the check the unfold falsifier COULDN'T do (reviewer).

"raw == unfolded exactly" proves r~ is unfold-INVARIANT on zeta, so the unfold test had ZERO power
to detect a density confound (unfolding is a no-op on r~). The low-gamma <r~> deviation (+1.2e-2)
scaling to ~0 at high gamma is degenerate between (a) a true finite-height crossover and (b) a raw
local-density-gradient bias that r~ sees THROUGH the unfold-invariance. The uniform-density
Dumitriu-Edelman null could not break this — it had no gradient.

Break it with a MATCHED-DENSITY null: GUE local fluctuations placed on the SAME smooth density
backbone as each zeta window (via the Riemann-von Mangoldt counting), then r~. If the matched-density
GUE null reproduces the deviation, it is the density gradient; if it stays at GUE 0.603, the zeta
deviation is real beyond density.

Run:  $HOME/fmexplorer/bin/python3 arsrh/phase1_density_check.py
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
from scipy.linalg import eigh_tridiagonal

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260725)


def mean_rtilde(x):
    s = np.diff(np.sort(x)); s = s[s > 0]
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(r.mean())


def gue_unit_levels(W):
    """GUE central flat window (unit-mean spacing), from DE beta=2 tridiagonal."""
    n = 5 * W
    d = math.sqrt(2.0) * RNG.standard_normal(n)
    b = np.sqrt(RNG.chisquare(2 * np.arange(n - 1, 0, -1)))
    ev = np.sort(eigh_tridiagonal(d, b, eigvals_only=True, select="i",
                                  select_range=(2 * W, 3 * W - 1)))
    s = np.diff(ev)
    u = np.concatenate([[0.0], np.cumsum(s / s.mean())])   # unit-mean-spacing levels
    return u


def rvm_N(t):
    tt = t / (2 * math.pi)
    return tt * np.log(tt) - tt + 7.0 / 8.0


# one global monotone R-vM grid for inversion, reused (np.interp is fast)
_GRID = np.linspace(10.0, 1.4e6, 3_000_000)
_NGRID = rvm_N(_GRID)


def rvm_inv(Nval):
    return np.interp(Nval, _NGRID, _GRID)


def matched_density_null(t_lo, W, n_real=30):
    """GUE fluctuations on the zeta window's R-vM density backbone -> <r~> distribution."""
    N0 = rvm_N(t_lo)
    out = []
    for _ in range(n_real):
        u = gue_unit_levels(W)                     # unit-density GUE levels
        tj = rvm_inv(N0 + u)                        # impose zeta density
        out.append(mean_rtilde(tj))
    return np.array(out)


def main():
    z = np.sort(np.loadtxt(os.path.join(_ROOT, "data", "odlyzko_zeros6.txt")))
    W = 2000
    starts = [0, z.size - W - 1]  # low-gamma (steep gradient) + high-gamma (flat, control)
    print("MATCHED-DENSITY null vs uniform-density null vs zeta (W=2000):")
    print("  break the density/crossover degeneracy the unfold test could not.\n")
    print(f"  {'gamma_mid':>11s} {'zeta <r~>':>10s} {'matched-dens GUE':>18s} {'uniform GUE':>13s} "
          f"{'zeta-matched':>13s}")
    # uniform-density GUE reference (flat), for contrast
    uni = np.array([mean_rtilde(gue_unit_levels(W)) for _ in range(30)])
    uni_m, uni_s = uni.mean(), uni.std()
    rows = []
    for s in starts:
        blk = z[s:s + W]
        gmid = float(blk[W // 2]); t_lo = float(blk[0])
        zr = mean_rtilde(blk)
        md = matched_density_null(t_lo, W, n_real=30)
        md_m, md_s = float(md.mean()), float(md.std())
        excess = zr - md_m
        rows.append({"gamma_mid": gmid, "zeta_rtilde": zr, "matched_density_null_mean": md_m,
                     "matched_density_null_sd": md_s, "uniform_null_mean": float(uni_m),
                     "zeta_minus_matched": excess,
                     "excess_over_matched_sd": excess / md_s if md_s else float("inf")})
        print(f"  {gmid:>11.3g} {zr:>10.5f} {md_m:>10.5f}±{md_s:.4f} {uni_m:>13.5f} "
              f"{excess:>+13.5f}")

    # verdict: does the matched-density null reproduce the low-gamma inflation?
    lowg = rows[0]
    density_explains = abs(lowg["matched_density_null_mean"] - lowg["zeta_rtilde"]) < 2 * lowg["matched_density_null_sd"]
    residual_real = any(r["excess_over_matched_sd"] > 2 for r in rows)
    out = {"anti_claim": "instrument-resolution / confound-isolation; NOT about RH",
           "uniform_null_mean": float(uni_m), "uniform_null_sd": float(uni_s), "rows": rows,
           "low_gamma_density_explains_deviation": bool(density_explains),
           "residual_beyond_density_at_any_height": bool(residual_real),
           "verdict": ("DENSITY-DOMINATED: the matched-density GUE null reproduces the zeta <r~> "
                       "inflation at low gamma (within its sd), so most/all of the +1.2e-2 was the raw "
                       "local density gradient r~ sees through unfold-invariance, NOT a finite-height "
                       "crossover. Phase 1's 'crossover' is (largely) a density artifact — the unfold "
                       "falsifier could not have caught it." if density_explains and not residual_real
                       else "REAL RESIDUAL: zeta <r~> exceeds the matched-density GUE null beyond its "
                       "sd at some height(s), so there is a genuine finite-height component BEYOND the "
                       "density gradient. The crossover survives the density confound (partly).")}
    print(f"\n  low-gamma: matched-density null {lowg['matched_density_null_mean']:.5f} vs zeta "
          f"{lowg['zeta_rtilde']:.5f} -> density {'EXPLAINS' if density_explains else 'does NOT explain'} it")
    print(f"  VERDICT: {out['verdict']}")
    json.dump(out, open(os.path.join(HERE, "phase1_density_check_measured.json"), "w"),
              indent=2, default=str)
    print("\n  wrote phase1_density_check_measured.json")


if __name__ == "__main__":
    main()
