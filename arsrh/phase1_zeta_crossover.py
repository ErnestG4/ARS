"""
arsrh/phase1_zeta_crossover.py — ARS-RH Phase 1: zeta height crossover under the
deterministic-noise discipline.

Prereg: arsrh/PHASE1_PREREG_SEALED.json. §0 anti-claim BINDING (instrument-resolution measurement;
NOT evidence about zeta or RH).

The deterministic-noise null is BLOCKING and is the whole point: zeta has no measurement noise, so
the only legitimate "error bar" on <r~> in a window is the finite-window SAMPLING SPREAD of <r~>
over a stationary GUE spectrum of the same window W. Built from the Dumitriu-Edelman beta=2 Hermite
TRIDIAGONAL ensemble (exact GUE eigenvalue statistics, O(W^2) via eigh_tridiagonal, no dense eig /
no GPU): diag ~ N(0,2) [= sqrt(2)*randn, the correct DE normalization], off-diag_i ~ chi_{2(n-i)};
central flat window so the raw ratio is unbiased. SWEEP W to map the jitter floor sd(W) ~ c/sqrt(W)
— that map IS the Skewes "what scale would be needed" answer.

Immunity test (assumption-light, no fit): is each height's zeta <r~> INSIDE the matched-window GUE
<r~> percentile band? A 1/log fit is reported only if the points already sit outside it.

Run:  $HOME/fmexplorer/bin/python3 arsrh/phase1_zeta_crossover.py
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
from scipy.linalg import eigh_tridiagonal

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260724)
from rtilde_refs import LARGE_N as _RT   # Atas et al. 2013 Table I, large N (2026-10-08, 6.1 D4)
GUE_RTILDE = _RT["GUE"]      # 0.5996; was the surmise 0.60266 (mislabelled "Atas") when PHASE1 was banked — see erratum
POISSON_RTILDE = _RT["Poisson"]


def mean_rtilde(points_sorted):
    s = np.diff(np.sort(points_sorted))
    s = s[s > 0]
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(r.mean())


def gue_window_rtilde(W):
    """<r~> over W GUE levels: central flat window of a size-5W DE beta=2 Hermite tridiagonal."""
    n = 5 * W
    d = math.sqrt(2.0) * RNG.standard_normal(n)
    b = np.sqrt(RNG.chisquare(2 * np.arange(n - 1, 0, -1)))
    ev = eigh_tridiagonal(d, b, eigvals_only=True, select="i",
                          select_range=(2 * W, 3 * W - 1))   # central W eigenvalues only (fast)
    return mean_rtilde(np.sort(ev))


def gue_null(W, n_real):
    return np.array([gue_window_rtilde(W) for _ in range(n_real)])


def unfold_zeta(t):
    """Riemann-von Mangoldt smooth counting -> unit-mean unfolded process (removes density gradient)."""
    tt = t / (2 * math.pi)
    N = tt * np.log(tt) - tt + 7.0 / 8.0
    return N - N[0]


def main():
    print("Loading zeta zeros (first ~2M, heights 14..1.13e6) ...", flush=True)
    z = np.loadtxt(os.path.join(_ROOT, "data", "odlyzko_zeros6.txt"))
    print(f"  loaded {z.size:,} zeros, height [{z.min():.1f}, {z.max():.3g}]\n", flush=True)

    sweep = [(2000, 80), (5000, 60), (10000, 40)]
    out = {"anti_claim": "instrument-resolution measurement; NOT evidence about zeta or RH",
           "reference_GUE_rtilde": GUE_RTILDE, "by_W": []}
    delta_pred = 1e-3          # sealed predicted finite-height correction scale

    for W, n_real in sweep:
        # height blocks spanning gamma ~1e2..1e6 (indices into the contiguous zero list)
        starts = [0, 40_000, 200_000, 700_000, z.size - W - 1]
        null = gue_null(W, n_real)
        nmean, nsd = float(null.mean()), float(null.std())
        p_lo, p_hi = (float(x) for x in np.percentile(null, [2.5, 97.5]))
        zr = []
        for s in starts:
            blk = z[s:s + W]
            gmid = float(blk[W // 2])
            rt = mean_rtilde(unfold_zeta(blk))
            zr.append({"gamma_mid": gmid, "inv_log": 1.0 / math.log(gmid / (2 * math.pi)),
                       "zeta_rtilde": rt, "dev_vs_GUE": rt - GUE_RTILDE,
                       "inside_95_GUE_null": bool(p_lo <= rt <= p_hi),
                       "percentile_in_null": float((null < rt).mean())})
        spread = max(r["zeta_rtilde"] for r in zr) - min(r["zeta_rtilde"] for r in zr)
        all_inside = all(r["inside_95_GUE_null"] for r in zr)
        c = nsd * math.sqrt(W)                          # jitter ~ c/sqrt(W)
        W_needed = (c / delta_pred) ** 2
        out["by_W"].append({"W": W, "n_real": n_real, "null_mean": nmean, "null_sd": nsd,
                            "null_band95": [p_lo, p_hi], "zeta": zr,
                            "zeta_spread_across_heights": spread,
                            "all_heights_inside_null_band": all_inside,
                            "jitter_const_c": c, "W_needed_to_resolve_1e-3": W_needed})
        print(f"W={W:>6,} (n_real={n_real}): GUE null mean={nmean:.5f} sd={nsd:.5f} "
              f"band95=[{p_lo:.5f},{p_hi:.5f}]", flush=True)
        for r in zr:
            flag = "" if r["inside_95_GUE_null"] else "  <-- OUTSIDE band"
            print(f"    gamma~{r['gamma_mid']:>10.3g}  1/log={r['inv_log']:.3f}  "
                  f"zeta<r~>={r['zeta_rtilde']:.5f}  dev={r['dev_vs_GUE']:+.5f}{flag}", flush=True)
        print(f"    spread {spread:.5f} vs sd {nsd:.5f}; all inside band: {all_inside}; "
              f"W to resolve 1e-3 ~ {W_needed:.2e} zeros/window\n", flush=True)

    any_out = any(not w["all_heights_inside_null_band"] for w in out["by_W"])
    biggest_W = out["by_W"][-1]
    out["resolvable_anywhere"] = bool(any_out)
    out["VERDICT"] = ("RESOLVABLE — some height exits the matched-window GUE band; a genuine "
                      "crossover to pursue frame-agnostic" if any_out else
                      "NOT RESOLVABLE above the finite-window GUE jitter floor at heights <=1.1e6 and "
                      "W<=1e4. Every zeta <r~> sits inside the matched-window GUE 95%% band at every "
                      "W. The floor sd(W) falls as ~1/sqrt(W) but at the largest reachable W=%d it is "
                      "%.4f — still ~%.0fx the sealed ~1e-3 finite-height correction; resolving that "
                      "needs W >~ %.1e zeros/window (%s the %.1e available). The honest deliverable is "
                      "the non-resolvability plus this required scale — the Skewes/Odlyzko-te-Riele "
                      "posture, quantified." % (biggest_W["W"], biggest_W["null_sd"],
                       biggest_W["null_sd"] / delta_pred, biggest_W["W_needed_to_resolve_1e-3"],
                       ">>" if biggest_W["W_needed_to_resolve_1e-3"] > z.size else "<", float(z.size)))
    print("VERDICT:", out["VERDICT"])
    json.dump(out, open(os.path.join(HERE, "phase1_zeta_crossover_measured.json"), "w"),
              indent=2, default=str)
    print("\nwrote phase1_zeta_crossover_measured.json")


if __name__ == "__main__":
    main()
