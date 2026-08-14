"""Pre-step P3 micro-deliverable: bank a citable GUE pair-correlation SHAPE
tolerance anchor.

Attribution-slot audit (memory: filing_discipline_attribution_slot): the GUE
R₂ analytic FORM is owned by universality.py (pair_correlation docstring +
R2_gue), and the Σ² asymptotic by universality.py number_variance docstring —
but NO repo file owned a g(s)-shape TOLERANCE.  arsrh/phase3_sigma2.py:76-78
seals `gue_relerr_max < 0.25` in the Σ² slot; citing that in the R₂ slot would
be an attribution-slot violation.  Hence this anchor.

Derivation: β=2 GUE (dense Hermitian, off-diagonal E|H_jk|²=1 → semicircle
support [−2√N, 2√N]), unfolded by the EXACT semicircle CDF (theory-fixed, not
fit — same discipline as the Weyl analytic unfold, sessionK/maass_analysis.py),
bulk-trimmed 5% per edge, pooled over seeds to a sample size matched in order
to the 100k-zero Odlyzko window.  Empirical g via bridge/observer_b.pcf_1d
(border-corrected) against g(s) = 1 − (sin πs/πs)².

Banked tolerance: tol = max(0.02, 2·max_{s∈[0.25,5]}|ĝ_pooled − g_analytic|).
The 0.02 floor keeps the anchor from under-covering if the ensemble happens to
land unusually close to the analytic curve.
"""

import json
import sys
import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/bridge")
from observer_b import pcf_1d  # noqa: E402

N = 4096
SEEDS = list(range(700, 724))          # 24 seeds → ~88k bulk levels pooled
TRIM = 0.05                            # bulk trim per edge
S_LO, S_HI = 0.25, 5.0                 # assessed window (matches G-A2)
BINS = np.arange(0.0, 25.0 + 1e-9, 0.05)


def gue_levels(n, seed):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    H = (X + X.conj().T) / 2.0
    return np.linalg.eigvalsh(H)


def semicircle_unfold(lam, n):
    """DIM=1, theory-fixed unfold: u = n·F_sc(λ), F_sc the exact semicircle CDF
    on [−2√n, 2√n].  One transition on this path (tripwire 1)."""
    y = np.clip(lam / (2.0 * np.sqrt(n)), -1.0, 1.0)
    F = 0.5 + (y * np.sqrt(1.0 - y**2) + np.arcsin(y)) / np.pi
    return n * F


def main():
    pooled = []
    for s in SEEDS:
        lam = gue_levels(N, s)
        u = np.sort(semicircle_unfold(lam, N))
        k = int(TRIM * len(u))
        pooled.append(u[k:-k])
        print(f"  seed {s}: {len(u)-2*k} bulk levels", flush=True)
    # pcf per seed (each seed is one stationary unit-rate segment), averaged —
    # pooling raw levels across seeds would splice unrelated processes.
    gs = []
    for u in pooled:
        c, g = pcf_1d(u, BINS)
        gs.append(g)
    centers = c
    g_pool = np.mean(gs, axis=0)
    sinc = np.where(centers > 0, np.sin(np.pi*centers)/(np.pi*centers + 1e-300), 1.0)
    g_ana = 1.0 - sinc**2
    m = (centers >= S_LO) & (centers <= S_HI)
    dev = g_pool[m] - g_ana[m]
    tol = max(0.02, 2.0 * float(np.abs(dev).max()))
    out = dict(N=N, n_seeds=len(SEEDS), n_levels_pooled=int(sum(len(u) for u in pooled)),
               window=[S_LO, S_HI], bin_width=0.05,
               max_abs_dev=float(np.abs(dev).max()),
               rms_dev=float(np.sqrt((dev**2).mean())),
               TOLERANCE_G_A2=tol,
               derivation="tol = max(0.02, 2*max|g_pooled - g_analytic|) on window",
               analytic_form_owner="universality.py pair_correlation (R2_gue)",
               centers=centers[m].tolist(), g_pooled=g_pool[m].tolist())
    with open("/home/combust/fmexplorer/criticality_tool/bridge/gue_pcf_anchor.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"ANCHOR BANKED: max|dev|={out['max_abs_dev']:.4f} rms={out['rms_dev']:.4f} "
          f"→ TOLERANCE_G_A2={tol:.4f}  ({out['n_levels_pooled']} pooled levels)")


if __name__ == "__main__":
    main()
