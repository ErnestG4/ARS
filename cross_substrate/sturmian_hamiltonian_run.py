"""
cross_substrate/sturmian_hamiltonian_run.py — Sturmian Hamiltonian operator α-sweep.

The capstone on the number-theoretic thread. The symbolic Sturmian WORD did NOT
stratify by Lagrange class (sturmian_run.py) — it's 3-distance-rigid. The prediction
was that the stratification is SPECTRAL. This tests it on the operator:

  discrete Schrödinger H_{α,φ}: (Hψ)_n = ψ_{n+1} + ψ_{n-1} + V_n ψ_n,
  V_n = λ · χ_{[1−α,1)}({nα + φ})   (Sturmian potential; α=golden ⇒ Fibonacci Hamiltonian)

Per (α, λ): φ-ensemble eigenvalues (tridiagonal) → polynomial-IDS unfold → pooled NNS
(Family I/II); spectral fractal dimension D_box of the eigenvalue set (Cantor-spectrum
discriminator, a Family-IV-lite axis). Sweep α across Lagrange classes; ask whether the
SPECTRUM stratifies where the word didn't. Flag, don't interpret.

Out: coordinates/sturmian-hamiltonian.jsonl.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date

import numpy as np
from scipy.linalg import eigvalsh_tridiagonal

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.axes import (                 # noqa: E402
    canonical_spacings, FAMILY_I, compute_family_II)

N = 8000
N_PHI = 8
PHIS = (np.arange(N_PHI) + 0.5) / N_PHI            # 8 offsets in [0,1)
LAM = 2.0                                          # Sturmian coupling (Cantor ∀λ>0)
COORD = os.path.join(_HERE, "coordinates")

_ALPHAS = [
    ("golden", (np.sqrt(5) - 1) / 2, "quadratic", "Fibonacci Hamiltonian"),
    ("silver", np.sqrt(2) - 1, "quadratic", "[0;2,2,…]"),
    ("bronze", (np.sqrt(13) - 3) / 2, "quadratic", "[0;3,3,…]"),
    ("sqrt3m1", np.sqrt(3) - 1, "quadratic", "[0;1,2,…] per-2"),
    ("e_minus_2", np.e - 2, "transcendental_diophantine", "bounded measure"),
    ("liouville", sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), "transcendental_liouville",
     "unbounded quotients"),
    ("rational_3_5", 0.6, "rational", "3/5 (periodic potential, control)"),
]


def sturmian_eigs(alpha, phi, lam=LAM, n=N):
    """Eigenvalues of the finite Sturmian Hamiltonian (tridiagonal, off-diag 1)."""
    frac = (np.arange(n) * alpha + phi) % 1.0
    V = lam * (frac >= 1.0 - alpha).astype(np.float64)        # χ_{[1−α,1)}
    return eigvalsh_tridiagonal(V, np.ones(n - 1))


def poly_unfold(eigs, deg=12):
    """Standard spectral unfolding: smooth integrated-density via polynomial fit to
    the eigenvalue staircase; unfolded position = N_smooth(E)."""
    e = np.sort(np.asarray(eigs, float))
    rank = np.arange(1, e.size + 1, dtype=np.float64)
    c = np.polyfit(e, rank, deg)
    return np.polyval(c, e)


def box_dim(eigs, n_sizes=12):
    """Box-counting dimension of the eigenvalue set (spectral support). Cantor < 1,
    full band ≈ 1 — discriminates the α-class spectral structure."""
    e = np.sort(np.asarray(eigs, float))
    span = float(e[-1] - e[0])
    if span <= 0:
        return None
    sizes = span / (2.0 ** np.arange(1, n_sizes + 1))
    counts = np.array([np.unique(np.floor((e - e[0]) / sz)).size for sz in sizes], float)
    m = counts > 1
    if m.sum() < 4:
        return None
    return float(-np.polyfit(np.log(sizes[m]), np.log(counts[m]), 1)[0])


def run():
    recs = []
    print(f"STURMIAN HAMILTONIAN α-sweep (N={N}, λ={LAM}, {N_PHI}φ) — does the SPECTRUM stratify?")
    print(f"{'α-name':12s} {'class':26s} {'W1δ':>6s} {'ks_gue':>7s} {'q':>5s} {'D_box':>6s}")
    for name, alpha, klass, desc in _ALPHAS:
        perphi_s, dboxes = [], []
        for phi in PHIS:
            ev = sturmian_eigs(alpha, float(phi))
            perphi_s.append(canonical_spacings(poly_unfold(ev)))
            db = box_dim(ev)
            if db is not None:
                dboxes.append(db)
        pooled = np.concatenate(perphi_s)
        fI = {k: fn(pooled) for k, fn in FAMILY_I.items()}
        fII_list = [compute_family_II(poly_unfold(sturmian_eigs(alpha, float(p)))) for p in PHIS]
        fII = {k: (float(np.mean([d[k] for d in fII_list if isinstance(d.get(k), (int, float))]))
                   if any(isinstance(d.get(k), (int, float)) for d in fII_list) else None)
               for k in fII_list[0]}
        d_box = float(np.mean(dboxes)) if dboxes else None
        axes = {**fI, **fII, "IV.2_spectral_box_dim": d_box}
        recs.append({"substrate": "sturmian-hamiltonian", "cell_id": f"{name}_{klass}_lam{LAM:g}",
                     "axes_computed": axes,
                     "non_applicable_axes": ["V.1_lyapunov"],
                     "extraction_method": f"tridiagonal eigs, Sturmian potential λ={LAM}; "
                                          f"polynomial-IDS unfold (deg 12), {N_PHI}φ pooled",
                     "extraction_audit": {"alpha": float(alpha), "lagrange_class": klass,
                                          "cf": desc, "N": N, "lam": LAM, "n_phi": N_PHI},
                     "source_artifact": "generated (deterministic eigensolve)",
                     "computed_date": date.today().isoformat()})
        def f(v):
            return f"{v:.3f}" if isinstance(v, float) else " - "
        print(f"{name:12s} {klass:26s} {f(fI.get('I.1_w1_clock')):>6s} "
              f"{f(fI.get('I.5_ks_gue')):>7s} {f(fI.get('I.8_brody_q')):>5s} {f(d_box):>6s}")

    with open(os.path.join(COORD, "sturmian-hamiltonian.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ wrote coordinates/sturmian-hamiltonian.jsonl ({len(recs)} cells)")
    print("[capstone] does the SPECTRUM stratify by Lagrange class (where the word did NOT)?")


if __name__ == "__main__":
    run()
