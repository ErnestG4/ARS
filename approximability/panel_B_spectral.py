"""
approximability/panel_B_spectral.py — Panel B, Face 1 (SPECTRAL, primary; inherits Panel A).

Object: Σ²(L) of the UNFOLDED spectrum of the α-Schrödinger (Sturm) Hamiltonian at large coupling. Panel A said
C=dim·lnλ is K-governed: metallics (K=a) finite/rigid Cantor; e (K=∞) → dim→1 → spectrum FILLS → Σ²(L)→Poisson-like.
So on the certified Σ²(L) probe (clean-room gate PASSED, L≤30, deg≈14–20):
  PREDICTION — metallics & π: LOW Σ² (rigid Cantor);  e: HIGHER Σ², drifting toward Poisson (Σ²~L) as depth grows.

PRE-REGISTRATION (per reviewer point 2): e's CF is closed-form (Euler [2;1,2,1,1,4,1,1,6,…]), so its drift is
computable in advance. We register e's expected Σ² ORDERING (highest, → Poisson) and check the grid is DEEP ENOUGH
that e actually separates from the metallics. If e does NOT separate at the deepest affordable n, the honest output is
"insufficient depth", NOT a verdict. π's accessible depth is limited by its early large quotients (a₃=15, a₄... ,292),
so π may land as "insufficient depth" — reported honestly, not forced.

READ-ONLY. Run: PYTHONPATH=$HOME/fmexplorer/riemann_explorer $HOME/fmexplorer/bin/python3 \
                  approximability/panel_B_spectral.py
"""
import os, sys, json
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
import numpy as np
import mpmath as mp
from cross_substrate.sturmian_hamiltonian_run import sturmian_eigs
from cross_substrate.longrange_discriminator import unfold_empirical
from cross_substrate.axes import II1_sigma2_at_L

mp.mp.dps = 120
OUT = os.path.dirname(os.path.abspath(__file__))
L_GRID = [2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0]   # certified range (L≤30)
LAM = 16.0
UDEG = 16
PHI = 0.1234


def cf_digits(x, n):
    a = []; y = mp.mpf(x)
    for _ in range(n):
        ai = int(mp.floor(y)); a.append(ai); f = y - ai
        if f == 0: break
        y = 1 / f
    return a


def K_finite(digits):
    d = [a for a in digits if a > 0]
    return float(np.exp(np.mean(np.log(d))))


def spectral_sigma2(alpha, n, seeds=(0.1234, 0.31, 0.53)):
    """Σ²(L) of the unfolded α-Hamiltonian spectrum, averaged over phase φ (reduces phason noise)."""
    curves = []
    for phi in seeds:
        e = np.sort(np.asarray(sturmian_eigs(alpha, phi, lam=LAM, n=n), float))
        k = int(len(e) * 0.12); e = e[k:len(e) - k]          # bulk trim
        u = np.sort(unfold_empirical(e, UDEG))
        curves.append([II1_sigma2_at_L(u, L) for L in L_GRID])
    C = np.array(curves, float)
    return C.mean(0), C.std(0) / np.sqrt(len(seeds))


ALPHAS = [
    ("golden", (np.sqrt(5) - 1) / 2, 1.0),
    ("silver", np.sqrt(2) - 1,       2.0),
    ("bronze", (np.sqrt(13) - 3) / 2, 3.0),
    ("pi",     float(mp.pi) - 3,     None),
    ("e",      float(mp.e) - 2,      None),
]

if __name__ == "__main__":
    print("=" * 86)
    print(f"PANEL B — FACE 1 (spectral) — Σ²(L) of the α-Hamiltonian spectrum, λ={LAM:g}, unfold deg={UDEG}")
    print("=" * 86)

    # depth certificate: accessible n and the finite-depth K each α's spectrum actually sees
    N = 4200
    pid = cf_digits(mp.pi, 40); ed = cf_digits(mp.e, 60)
    print(f"\n[depth] n={N} sites resolve α to ~1/n ⇒ CF terms with q≲{N}. Finite-depth K each spectrum SEES:")
    print(f"   golden/silver/bronze: K=1/2/3 exactly (periodic, any depth).")
    print(f"   π first terms {pid[:6]} → the 15 (a₃) and 292 (a₅, q=33102≫{N}) inflate shallow K; "
          f"K over q≲{N} ≈ {K_finite(pid[:4]):.2f} (NOT yet settled to K₀=2.685).")
    print(f"   e first terms {ed[:8]} → K over q≲{N} ≈ {K_finite(ed[:14]):.2f}, climbing (2,4,6,… spine).")

    # ---- PRE-REGISTER e (and metallic baseline) BEFORE reading π ----
    print(f"\n[pre-register] expected ordering: e HIGHEST Σ² (dim→1, filling); metallics LOW; π conditional.")
    res = {}
    for name, a, K in ALPHAS:
        if name == "pi":
            continue
        m, se = spectral_sigma2(a, N)
        res[name] = (m, se)
    gold = res["golden"][0]; ev = res["e"][0]
    sep = ev[-1] - gold[-1]                       # e vs golden at L=30
    sep_se = np.hypot(res["e"][1][-1], res["golden"][1][-1])
    print(f"   Σ²(L=30): golden={gold[-1]:.3f}  silver={res['silver'][0][-1]:.3f}  "
          f"bronze={res['bronze'][0][-1]:.3f}  e={ev[-1]:.3f}")
    depth_ok = sep > 3 * sep_se and sep > 0.05
    print(f"   e−golden separation at L=30 = {sep:+.3f} (±{sep_se:.3f}); "
          f"{'DEPTH SUFFICIENT — e separates ✓' if depth_ok else 'INSUFFICIENT DEPTH — e does not separate at n=%d' % N}")

    # ---- now read π ----
    print(f"\n[test] π:")
    pm, pse = spectral_sigma2(float(mp.pi) - 3, N)
    res["pi"] = (pm, pse)
    print(f"   {'L':>4s} " + " ".join(f"{int(L)}".rjust(7) for L in L_GRID))
    for name in ("golden", "silver", "bronze", "pi", "e"):
        m = res[name][0]
        print(f"   {name:>6s} " + " ".join(f"{v:.3f}".rjust(7) for v in m))

    # π placement: distance to the metallic band vs to e, at L=30
    metband = np.array([res[k][0][-1] for k in ("golden", "silver", "bronze")])
    d_met = abs(pm[-1] - metband.mean()); d_e = abs(pm[-1] - ev[-1])
    print(f"\n   π Σ²(L=30)={pm[-1]:.3f}: |π−metallic_mean|={d_met:.3f}  |π−e|={d_e:.3f}  "
          f"metallic band=[{metband.min():.3f},{metband.max():.3f}]")
    if not depth_ok:
        verdict = "INSUFFICIENT DEPTH (e control did not separate) — no π verdict"
    elif d_met < d_e and metband.min() - 0.05 <= pm[-1] <= metband.max() + 0.05:
        verdict = "π reads METALLIC-LIKE (finite family) — consistent with liminf K(π)<∞ [conditional]"
    elif d_e < d_met:
        verdict = "π reads e-LIKE (drifting) — would CONTRADICT the finite-K placement (audit!)"
    else:
        verdict = "π AMBIGUOUS (between bands) — likely shallow-depth (π's 15/292 not yet averaged out)"
    print(f"\n   VERDICT (Face 1, conditional on depth): {verdict}")

    with open(os.path.join(OUT, "panel_B_spectral.json"), "w") as fh:
        json.dump({"L_grid": L_GRID, "lam": LAM, "n_sites": N, "unfold_deg": UDEG,
                   "sigma2": {k: res[k][0].tolist() for k in res},
                   "sigma2_se": {k: res[k][1].tolist() for k in res},
                   "e_minus_golden_sep_L30": float(sep), "depth_sufficient": bool(depth_ok),
                   "verdict": verdict}, fh, indent=2)
    print("\n   wrote approximability/panel_B_spectral.json — DONE.")
