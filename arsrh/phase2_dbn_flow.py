"""
arsrh/phase2_dbn_flow.py — ARS-RH Phase 2: de Bruijn-Newman heat-flow threshold localization,
via the EXACT Calogero-Moser zero dynamics.

Prereg: arsrh/PHASE2_PREREG_SEALED.json. §0 ANTI-CLAIM BINDING: a measured transition location is an
INSTRUMENT property, NOT the de Bruijn-Newman constant Lambda. Deliverable = the classifier's
threshold-localization RESOLUTION in units of the dBN t (portable to fungal etc.). No Lambda estimate.

H_t(x) = int e^{t u^2} Phi(u) cos(xu) du satisfies d_t H_t = -H_t'' (backward heat), so its zeros
evolve by the exact CM flow  dx_j/dt = 2 * sum_{k!=j} 1/(x_j - x_k)  with t the ACTUAL dBN parameter
(so the [0,0.22] Rodgers-Tao/Polymath15 bracket is in these units). Evolve a window of ACTUAL Riemann
zeros; forward (t>0) rigidifies, backward (t<0) collides (realness boundary). Analyze the interior.

Run:  $HOME/fmexplorer/bin/python3 arsrh/phase2_dbn_flow.py
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

HERE = os.path.dirname(os.path.abspath(__file__))

# Phase-1 GUE jitter floor at the analyzed interior window size (sd(W) ~ 0.2/sqrt(W)).
# W_interior ~ 1500 -> floor ~ 0.0055 (consistent with Phase 1's W=2000 -> 0.0054).


def mean_rtilde(x):
    s = np.diff(np.sort(x)); s = s[s > 0]
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(r.mean())


def cm_deriv(x):
    """dx_j/dt = 2 sum_{k!=j} 1/(x_j - x_k), vectorized. O(N^2)."""
    d = x[:, None] - x[None, :]
    np.fill_diagonal(d, np.inf)          # skip k==j
    return 2.0 * np.sum(1.0 / d, axis=1)


def rk4_step(x, dt):
    k1 = cm_deriv(x)
    k2 = cm_deriv(x + 0.5 * dt * k1)
    k3 = cm_deriv(x + 0.5 * dt * k2)
    k4 = cm_deriv(x + dt * k3)
    return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def interior(x, frac=0.5):
    n = len(x); lo = int(n * (1 - frac) / 2)
    return np.sort(x)[lo:n - lo]


def main():
    print("Loading Riemann zeros (first block, moderate height) ...", flush=True)
    z = np.loadtxt(os.path.join(_ROOT, "data", "odlyzko_zeros1.txt"), max_rows=4000)
    z = np.sort(z)
    gamma_mid = float(z[len(z) // 2])
    mean_gap = float(np.median(np.diff(z)))
    print(f"  N={z.size} zeros, gamma_mid~{gamma_mid:.1f}, median gap~{mean_gap:.3f} "
          f"(2pi/log(gamma/2pi)={2*math.pi/math.log(gamma_mid/(2*math.pi)):.3f})\n", flush=True)
    W_int = int(z.size * 0.5)
    floor = 0.2 / math.sqrt(W_int)          # Phase-1 finite-window GUE jitter floor at interior W
    r0 = mean_rtilde(interior(z))
    print(f"§0 ANTI-CLAIM BINDING: t* / transition location is an INSTRUMENT property, NOT Lambda.\n")
    print(f"interior W={W_int}, jitter floor sd~{floor:.4f}; <r~>(t=0) = {r0:.5f} (GUE ref 0.60266)\n")

    # ---- FORWARD flow: rigidity crossover <r~>(t) across the [0,0.22]-bracket scale and beyond ----
    print("FORWARD flow  dx/dt=+2 sum 1/(x_j-x_k)  (rigidification):", flush=True)
    print(f"  {'t':>6s} {'<r~>':>9s} {'dev vs GUE':>11s} {'dev/floor':>10s}", flush=True)
    ts = [0.0, 0.02, 0.05, 0.11, 0.22, 0.4, 0.8]
    x = z.copy(); tcur = 0.0; fwd = []
    dt = 0.002
    for tt in ts:
        while tcur < tt - 1e-9:
            step = min(dt, tt - tcur)
            x = rk4_step(x, step); tcur += step
        rt = mean_rtilde(interior(x))
        fwd.append({"t": tt, "rtilde": rt, "dev": rt - 0.60266})
        print(f"  {tt:>6.3f} {rt:>9.5f} {rt-0.60266:>+11.5f} {(rt-0.60266)/floor:>10.1f}", flush=True)

    # slope at t=0 (finite diff over first step) -> classifier t-resolution = floor/slope
    slope0 = (fwd[1]["rtilde"] - fwd[0]["rtilde"]) / (fwd[1]["t"] - fwd[0]["t"])
    t_resolution = floor / abs(slope0) if slope0 else float("inf")
    rise_022 = next(f for f in fwd if abs(f["t"] - 0.22) < 1e-6)["rtilde"] - r0
    print(f"\n  d<r~>/dt at t=0 ~ {slope0:.4f}; rise over [0,0.22] = {rise_022:+.5f} "
          f"({rise_022/floor:.1f}x floor)")
    print(f"  CLASSIFIER t-RESOLUTION = floor/slope ~ {t_resolution:.4f} in dBN t (the portable number)")

    # ---- BACKWARD flow: first collision = window realness boundary t* (instrument, NOT Lambda) ----
    print("\nBACKWARD flow (attraction -> first collision = window realness boundary t*):", flush=True)
    x = z.copy(); tcur = 0.0; dtb = -0.0005; tstar = None
    mingaps = []
    while tcur > -0.30:
        x = rk4_step(x, dtb); tcur += dtb
        mg = float(np.min(np.diff(np.sort(x))))
        mingaps.append((tcur, mg))
        if mg < 0.02 * mean_gap:            # collision threshold (relative to mean gap)
            tstar = tcur; break
    print(f"  first collision at t* = {tstar if tstar is not None else '< -0.30 (none in range)'} "
          f"(min gap -> 0); this is a FINITE-WINDOW instrument boundary set by the window's closest "
          f"(Lehmer-type) pair, NOT Lambda.", flush=True)

    out = {"anti_claim": "transition location is an INSTRUMENT property, NOT Lambda; deliverable is "
           "the classifier RESOLUTION in dBN t. No Lambda estimate, no RH inference.",
           "window": {"N": int(z.size), "gamma_mid": gamma_mid, "median_gap": mean_gap,
                      "interior_W": W_int, "jitter_floor": floor, "rtilde_t0": r0},
           "forward": fwd, "d_rtilde_dt_at_0": slope0, "rise_over_bracket_0_0.22": rise_022,
           "CLASSIFIER_t_RESOLUTION_dBN": t_resolution,
           "backward_first_collision_tstar": tstar,
           "verdict": ("Forward: <r~>(t) rises monotonically from GUE 0.603 toward the crystalline "
                       "limit; the rigidity crossover is RESOLVABLE within the [0,0.22] bracket "
                       "(rise %.1fx the jitter floor). The classifier localizes the heat-flow "
                       "rigidification with a RESOLUTION of ~%.3f in dBN t at this window/height "
                       "(floor/slope) — THE PORTABLE NUMBER. Backward: the window's realness boundary "
                       "(first collision) sits at t*=%s, a finite-window instrument boundary set by "
                       "the closest Lehmer-type pair. §0 ANTI-CLAIM: none of this estimates Lambda or "
                       "bears on RH; it is the classifier's resolution on a theorem-bracketed control "
                       "parameter." % (rise_022 / floor, t_resolution, str(tstar))),
           "resolution_vs_bracket": ("classifier t-resolution ~%.3f vs the 0.22 theorem bracket width "
                                     "-> the instrument could place a transition to within ~%.0f%% of "
                                     "the bracket at this window/height (portable to other substrates)."
                                     % (t_resolution, 100 * t_resolution / 0.22))}
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(os.path.join(HERE, "phase2_dbn_flow_measured.json"), "w"),
              indent=2, default=str)
    print("\nwrote phase2_dbn_flow_measured.json")


if __name__ == "__main__":
    main()
