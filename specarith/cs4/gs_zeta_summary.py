"""Summary of the Stage 2 ζ prediction (gs_zeta.py merge output): v(b) and g per height, the assembly's pieces, the
precision checks (|Im| noise bound on v, Fourier tail, imaginary residues, the ℓ-oscillating long-range part dropped by
the split), positivity, ρ₃ smoothness near the diagonal, and the log b behaviour (descriptive; twenty-first round: no
functional form).

  python gs_zeta_summary.py RESULTS_DIR      (RESULTS_DIR holds gs_zeta_L*.json and L*/rho3/c*.npy)
"""
import glob
import json
import math
import os
import sys

import numpy as np

import gs_zeta as Z

G_GUE = 0.9606180215687513          # gs_unitary.py, sine kernel, direct (GS_UNITARY_RESULTS.md)


def rho3_smoothness(d):
    """Second differences of ρ₃(0, a, e) along e on the GL grid, relative to the local scale: a rough check that the
    near-diagonal (a ≈ e) values carry no precision spikes. Returns the max |Δ²| / max|ρ₃| over the grid, in and away from
    the band |a − e| < 0.2."""
    rows = np.concatenate([np.load(f) for f in sorted(glob.glob(os.path.join(d, "rho3", "c*.npy")))])
    a, _, e, _ = Z.i3_nodes()
    R = np.zeros((Z.NA, Z.NE))
    R[rows[:, 0].astype(int), rows[:, 1].astype(int)] = rows[:, 2]
    # second divided differences along e (non-uniform GL nodes)
    e0, e1, e2 = e[:-2], e[1:-1], e[2:]
    d2 = 2 * (R[:, :-2] / ((e0 - e1) * (e0 - e2)) + R[:, 1:-1] / ((e1 - e0) * (e1 - e2)) + R[:, 2:] / ((e2 - e0) * (e2 - e1)))
    near = np.abs(a[:, None] - e1[None, :]) < 0.2
    scale = np.abs(R).max()
    return dict(max_d2_near=float(np.abs(d2[near]).max() / scale), max_d2_far=float(np.abs(d2[~near]).max() / scale),
                min_rho3=float(R.min()), max_rho3=float(R.max()))


def main(rd):
    out = {}
    for f in sorted(glob.glob(os.path.join(rd, "gs_zeta_L*.json")), key=lambda s: float(s.split("_L")[1][:-5])):
        r = json.load(open(f))
        ell = r["ell"]
        v = {int(b): x for b, x in r["v"].items()}
        bs = sorted(v)
        lb = np.log(bs)
        dv_dlogb = [(v[bs[k + 1]] - v[bs[k]]) / (lb[k + 1] - lb[k]) for k in range(len(bs) - 1)]
        noise = {int(b): x for b, x in r["v_noise_bound"].items()}
        osc = {p: max(abs(o) for o in q["osc_long"]) for p, q in r["osc_check"].items()}
        sm = rho3_smoothness(os.path.join(rd, f"L{ell}"))
        out[ell] = dict(v=v, g=r["g"], g_over_gGUE=r["g"] / G_GUE, positivity=r["positivity"],
                        dv_dlogb=dv_dlogb, max_rel_noise=max(noise[b] / v[b] for b in bs),
                        max_fourier_tail=r["max_fourier_tail"], max_imag=r["max_imag"],
                        rho3_max_imag=r["rho3_max_imag"], n_pairs=r["n_pairs"], osc_max_abs=osc,
                        I2=r["I2"], I3={int(b): x for b, x in r["I3"].items()},
                        I4_short={int(b): x for b, x in r["I4_short"].items()},
                        I4_long={int(b): x for b, x in r["I4_long"].items()}, rho3=sm)
        print(f"ℓ = {ell}:  " + "  ".join(f"v({b}) {v[b]:.6f}" for b in bs)
              + f"   g {r['g']:.4f}  g/g_GUE {r['g'] / G_GUE:.4f}  positivity {'PASS' if r['positivity'] else 'FAIL'}")
        print("   dv/dlog b per rung: " + "  ".join(f"{x:+.5f}" for x in dv_dlogb)
              + f"   max rel |Im| noise {out[ell]['max_rel_noise']:.1e}  tail {r['max_fourier_tail']:.1e}"
              + f"  max imag {r['max_imag']:.1e}  ρ₃ imag {r['rho3_max_imag']:.1e}  pairs {r['n_pairs']}")
        print("   osc part (dropped) max |·| per pair: " + "  ".join(f"{p}: {x:.1e}" for p, x in osc.items())
              + "   ρ₃ Δ² near/far diag %.2e / %.2e, ρ₃ range [%.4f, %.4f]"
              % (sm["max_d2_near"], sm["max_d2_far"], sm["min_rho3"], sm["max_rho3"]))
    json.dump(out, open(os.path.join(rd, "gs_zeta_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
