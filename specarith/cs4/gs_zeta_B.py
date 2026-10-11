"""Stage 2 ζ prediction for estimator B (twenty-fourth round): E[v̂_B(b)] = v(b)(1 − ρ₁(b)) = v(b) − Cov(3b)/b, with
  Cov(R)/b = (1/√2) ∫_ℝ exp(−π(r − R)²/2b²) C(r) dr,
C assembled exactly as v(b) is (gs_zeta.py merge weights): short range = stored c_short × χ; long range = stored c_non
× (1 − χ) on r = 5 … 48000.5, continued by gs_zeta_ext.py's c_non_ext on r > 48000.5 (to 6.0005·10⁴). The ℓ-oscillating
long-range part is dropped as in v(b) (amendment 7; its lag-1 counterpart: diag_osc_lag1.py).
Every lag used lies inside the grid to 5σ of its Gaussian (s = b/√π); b = 10⁴ lag 1 needs 5.82·10⁴.

Checks:
- **Overlap.** On [47000, 48000.5] the extension's c_non_ext must reproduce the stored c_non, per pair and assembled.
- **Recheck.** Lag 0 on the combined grid must reproduce the stored I₄ (short + long).

  python gs_zeta_B.py RESULTS_DIR      (RESULTS_DIR = results/gs_zeta) -> RESULTS_DIR/gs_zeta_B_summary.json
"""
import json
import math
import os
import sys

import numpy as np

import gs_unitary as G
import gs_zeta as Z
import gs_zeta_ext as E

ELLS = ("15.7502", "16.4972", "17.2491", "19.5003", "21.75")
G_GUE_B_FILE = os.path.join("results", "gs_unitary_lag1", "gs_unitary_lag1.json")


def assemble(rd, ell):
    rs, rl, re = Z.short_grid(), Z.long_grid(), E.ext_grid()
    cs_, cl_ = G.chi(rs), 1 - G.chi(rl)
    Cs, Cl, Ce = np.zeros(len(rs)), np.zeros(len(rl)), np.zeros(len(re))
    ov_l = (rl >= re[0])
    ov_e = (re <= rl[-1])
    assert np.allclose(rl[ov_l], re[ov_e]), "extension is not on the production lattice"
    worst_pair, imag, tail = 0.0, 0.0, 0.0
    for (i, j) in Z.PAIRS:
        z = np.load(os.path.join(rd, f"L{ell}", "pairs", f"p{i:02d}_{j:02d}.npz"))
        x = np.load(os.path.join(rd, f"L{ell}", "ext", f"p{i:02d}_{j:02d}.npz"))
        wgt = 4 * Z.DW[i] * Z.FD[i] * Z.DW[j] * Z.FD[j] * (1 if i == j else 2)
        Cs += wgt * cs_ * z["c_short"]
        Cl += wgt * cl_ * z["c_non"]
        Ce += wgt * x["c_non_ext"]                       # 1 − χ = 1 here
        d = np.abs(z["c_non"][ov_l] - x["c_non_ext"][ov_e]).max() / max(np.abs(z["c_non"][ov_l]).max(), 1e-300)
        worst_pair = max(worst_pair, float(d))
        imag, tail = max(imag, float(x["imag_max"])), max(tail, float(x["tail"]))
    ov = dict(worst_pair_rel=worst_pair, assembled_abs=float(np.abs(Cl[ov_l] - Ce[ov_e]).max()),
              assembled_rms=float(np.sqrt(np.mean(Cl[ov_l] ** 2))), ext_imag_max=imag, ext_fourier_tail=tail)
    r_long = np.concatenate([rl, re[~ov_e]])
    C_long = np.concatenate([Cl, Ce[~ov_e]])
    return rs, Cs, r_long, C_long, ov


def cov_over_b(rs, Cs, r_long, C_long, b, R):
    g = lambda x: np.exp(-math.pi * x ** 2 / (2 * b * b))
    return (Z.DR_S * np.sum((g(rs - R) + g(rs + R)) * Cs) + Z.DR_L * np.sum((g(r_long - R) + g(r_long + R)) * C_long)) / math.sqrt(2)


def main(rd):
    out = {}
    gue = json.load(open(G_GUE_B_FILE))
    for ell in ELLS:
        res = json.load(open(os.path.join(rd, f"gs_zeta_L{ell}.json")))
        v = {int(b): x for b, x in res["v"].items()}
        rs, Cs, r_long, C_long, ov = assemble(rd, ell)
        rmax = r_long[-1]
        row = dict(overlap=ov, rungs={})
        for b in Z.LADDER:
            s = b / math.sqrt(math.pi)
            assert 3 * b + 5 * s <= rmax, (b, rmax)
            i4 = math.sqrt(2) * cov_over_b(rs, Cs, r_long, C_long, b, 0.0)
            recheck = i4 - (res["I4_short"][str(b)] + res["I4_long"][str(b)])
            c1 = cov_over_b(rs, Cs, r_long, C_long, b, 3.0 * b)
            row["rungs"][b] = dict(v=v[b], cov1_over_b=c1, rho1=c1 / v[b], vB=v[b] - c1, i4_recheck=recheck)
        vB = {b: row["rungs"][b]["vB"] for b in Z.LADDER}
        row["g_B"] = math.sqrt(vB[10_000] / vB[100])
        row["g"] = res["g"]
        row["positivity_B"] = all(x > 0 for x in vB.values())
        row["g_B_over_gGUE_B"] = row["g_B"] / gue["g_B"]
        out[ell] = row
        print("ℓ=%-8s overlap: pair rel %.1e, assembled %.1e (rms %.2e) | ρ₁: %s | g %.4f → g_B %.4f (g_B/g_GUE,B %.3f) "
              "positivity %s | recheck ≤ %.0e"
              % (ell, ov["worst_pair_rel"], ov["assembled_abs"], ov["assembled_rms"],
                 " ".join("%+.4f" % row["rungs"][b]["rho1"] for b in Z.LADDER), row["g"], row["g_B"],
                 row["g_B_over_gGUE_B"], "PASS" if row["positivity_B"] else "FAIL",
                 max(abs(row["rungs"][b]["i4_recheck"]) for b in Z.LADDER)), flush=True)
    out["gue_B"] = dict(g_B=gue["g_B"], rho1={b: gue["rows"][str(b)]["rho1"] for b in Z.LADDER})
    json.dump(out, open(os.path.join(rd, "gs_zeta_B_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
