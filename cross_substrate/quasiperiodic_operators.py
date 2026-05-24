"""
cross_substrate/quasiperiodic_operators.py — does approximability stratification hold across the
BROADER quasi-periodic-operator family? (extends the AM↔Fibonacci↔brocot headline)

The "approximability stratification transcends operator family" result rests on 3 substrates. This
adds more 1-D quasi-periodic operators, each a simple (validated-instrument) eigensolve:

  maryland  : V_n = λ·tan(π(θn+φ))                         (exactly-solvable, unbounded potential)
  gaah      : V_n = 2λcos(2π(θn+φ)) / (1 − b·cos(2π(θn+φ)))  (generalized AAH, b=0.5; mobility edge)
  mosaic    : V_n = 2λcos(2π(θn+φ)) on every κ-th site (κ=2), 0 else  (mosaic-AM)
  ext_harper: AM + next-nearest-neighbour hopping λ'        (extended-Harper; pentadiagonal, eig_banded)

Per (operator, θ-class, coupling): eigensolve at N=50k × 8φ → box_dim (IV.2) + Family I (Brody q / I.5 /
W1δ via poly_unfold). Same 9 Lagrange θ-classes as AM/Fibonacci/brocot. Headline per operator:
ρ(approximability-rank, Brody q) at strong coupling — does q FALL with approximability (golden→Liouville)
like the established substrates? Reuses validated box_dim + poly_unfold + canonical_spacings; new potentials only.

Out: coordinates/quasiperiodic-operators.jsonl + figure P_qpo_approx.png. Run: --probe | --sweep [--workers 10].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np
from scipy.linalg import eigvalsh_tridiagonal, eig_banded

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.axes import canonical_spacings, FAMILY_I, compute_family_II  # noqa: E402
from cross_substrate.sturmian_hamiltonian_run import box_dim, poly_unfold          # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
N = 50_000
N_PHI = 8
PHIS = (np.arange(N_PHI) + 0.5) / N_PHI
COUPLINGS = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
# 9 Lagrange classes (same as AM/Fibonacci/brocot λ*), approximability-ordered golden→Liouville
CLASSES = [
    ("golden", (np.sqrt(5) - 1) / 2, 2.0), ("silver", np.sqrt(2) - 1, 2.0),
    ("bronze", (np.sqrt(13) - 3) / 2, 2.0), ("metallic4", np.sqrt(5) - 2, 2.0),
    ("metallic5", (np.sqrt(29) - 5) / 2, 2.0), ("e_minus_2", np.e - 2, 2.0),
    ("ln2", np.log(2), 3.57), ("pi_minus_3", np.pi - 3, 7.10),
    ("liouville", sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), 1e9),
]


def _frac(theta, phi, n=N):
    return (theta * np.arange(n) + phi) % 1.0


def maryland_eigs(lam, phi, theta, n=N):
    fr = _frac(theta, phi, n)
    fr = np.where(np.abs(fr - 0.5) < 1e-9, 0.5 + 1e-9, fr)   # dodge tan singularity (measure zero)
    return eigvalsh_tridiagonal(lam * np.tan(np.pi * fr), np.ones(n - 1))


def gaah_eigs(lam, phi, theta, n=N, b=0.5):
    c = np.cos(2 * np.pi * (theta * np.arange(n) + phi))
    return eigvalsh_tridiagonal(2 * lam * c / (1 - b * c), np.ones(n - 1))


def mosaic_eigs(lam, phi, theta, n=N, kappa=2):
    nn = np.arange(n)
    V = np.where(nn % kappa == 0, 2 * lam * np.cos(2 * np.pi * (theta * nn + phi)), 0.0)
    return eigvalsh_tridiagonal(V, np.ones(n - 1))


def ext_harper_eigs(lam, phi, theta, n=N, lam2=0.5):
    """AM + NNN hopping λ2 → pentadiagonal symmetric; eigenvalues via eig_banded."""
    V = 2 * lam * np.cos(2 * np.pi * (theta * np.arange(n) + phi))
    ab = np.zeros((3, n))      # banded (upper): row0=2nd diag, row1=1st diag, row2=main
    ab[2] = V
    ab[1, 1:] = 1.0
    ab[0, 2:] = lam2
    return eig_banded(ab, lower=False, eigvals_only=True)


OPERATORS = {"maryland": maryland_eigs, "gaah": gaah_eigs,
             "mosaic": mosaic_eigs, "ext_harper": ext_harper_eigs}


def _f(v):
    return None if v is None or not (isinstance(v, (int, float)) and np.isfinite(v)) else float(v)


def _fingerprint(eigfn, lam, theta):
    perphi_s, dboxes, evs_unf = [], [], []
    for phi in PHIS:
        ev = eigfn(lam, float(phi), theta)
        evs_unf.append(poly_unfold(ev))
        perphi_s.append(canonical_spacings(evs_unf[-1]))
        db = box_dim(ev)
        if db is not None:
            dboxes.append(db)
    pooled = np.concatenate(perphi_s)
    fI = {k: _f(fn(pooled)) for k, fn in FAMILY_I.items()}
    d_box = _f(float(np.mean(dboxes))) if dboxes else None
    return {**fI, "IV.2_spectral_box_dim": d_box}


def _task(arg):
    opname, cls, alpha, mu, lam = arg
    fp = _fingerprint(OPERATORS[opname], lam, alpha)
    return (opname, cls, mu, lam, fp)


def sweep(workers):
    tasks = [(op, c, a, mu, lam) for op in OPERATORS for c, a, mu in CLASSES for lam in COUPLINGS]
    print(f"QUASI-PERIODIC OPERATORS — {len(tasks)} cells ({len(OPERATORS)} ops × {len(CLASSES)} classes "
          f"× {len(COUPLINGS)} couplings), N={N}, {N_PHI}φ, {workers} workers")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_task, tasks))
    recs = []
    by = {}
    for opname, cls, mu, lam, fp in res:
        recs.append({"substrate": f"qpo-{opname}", "cell_id": f"{opname}/{cls}/lam{lam:g}",
                     "operator": opname, "lagrange_class": cls, "coupling": lam,
                     "axes_computed": fp,
                     "extraction_audit": {"irrationality_measure": mu, "N": N, "n_phi": N_PHI},
                     "source_artifact": "generated (tridiagonal/banded eigensolve)",
                     "computed_date": date.today().isoformat()})
        by.setdefault(opname, {}).setdefault(lam, []).append((cls, mu, fp))
    with open(os.path.join(COORD, "quasiperiodic-operators.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")

    # per-operator stratification test: D_box (the SC-spectrum discriminator) at the coupling with
    # MAX class-spread (strong coupling localizes → washes out; the fractal/critical regime is where
    # θ-class shows). ρ(approximability-rank, D_box); ρ<0 ⇒ Diophantine high / approximable low (joins family).
    from scipy import stats
    clsidx = [c for c, *_ in CLASSES]
    rank = np.arange(len(CLASSES))
    print(f"\n{'operator':11s} {'λ*':>4s} {'spread':>6s} {'ρ(rank,Dbox)':>12s}  D_box by class (golden→Liouville)")
    for op in OPERATORS:
        best = (None, -1.0, None, None)   # lam, spread, rho, ds
        for lam in COUPLINGS:
            pts = sorted(by[op][lam], key=lambda t: clsidx.index(t[0]))
            ds = [fp.get("IV.2_spectral_box_dim") for _, _, fp in pts]
            valid = [(r, d) for r, d in zip(rank, ds) if isinstance(d, float)]
            if len(valid) < 5:
                continue
            spread = max(d for _, d in valid) - min(d for _, d in valid)
            if spread > best[1]:
                rho = stats.spearmanr([a for a, _ in valid], [b for _, b in valid])[0]
                best = (lam, spread, rho, ds)
        lam, spread, rho, ds = best
        dstr = " ".join(f"{d:.2f}" if isinstance(d, float) else " - " for d in (ds or []))
        rs = f"{rho:+.3f}" if rho is not None else "  n/a"
        print(f"{op:11s} {lam if lam else '-':>4} {spread:>6.3f} {rs:>12s}  {dstr}")
    print(f"\n→ {len(recs)} cells banked in {(time.perf_counter()-t0)/60:.1f} min. "
          "ρ<0 at the critical coupling (Diophantine high D_box, Liouville low) ⇒ operator joins the "
          "approximability-stratification family. (maryland = always-PP control: λ-invariant, expected flat.)")
    _figure(by)


def _figure(by):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(OPERATORS), figsize=(4.2 * len(OPERATORS), 4.6), sharey=True)
    cmap = plt.cm.viridis(np.linspace(0, 1, len(CLASSES)))
    clsnames = [c for c, *_ in CLASSES]
    for ax, op in zip(axes, OPERATORS):
        for i, cn in enumerate(clsnames):
            qs = []
            for lam in COUPLINGS:
                pt = [fp for c, _, fp in by[op][lam] if c == cn]
                qs.append(pt[0].get("IV.2_spectral_box_dim") if pt else None)
            ax.plot(COUPLINGS, [q if isinstance(q, float) else np.nan for q in qs], "o-",
                    color=cmap[i], ms=3, label=cn)
        ax.set_title(op); ax.set_xlabel("coupling λ"); ax.grid(alpha=0.2)
    axes[0].set_ylabel("D_box (IV.2)")
    axes[-1].legend(fontsize=5, ncol=2)
    fig.suptitle("Quasi-periodic operators: Brody q vs coupling by Lagrange class "
                 "(stratification ⇒ D_box-spread by approximability at critical λ)")
    p = os.path.join(_HERE, "figures", "P_qpo_approx.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def probe(workers):
    print("PROBE — one cell per operator (golden vs Liouville @ λ=3), sanity + class-separation:")
    for op, fn in OPERATORS.items():
        gd = _fingerprint(fn, 3.0, (np.sqrt(5) - 1) / 2)
        li = _fingerprint(fn, 3.0, sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)))
        print(f"  {op:11s} golden: q={_f(gd['I.8_brody_q'])} D_box={_f(gd['IV.2_spectral_box_dim'])} | "
              f"liouville: q={_f(li['I.8_brody_q'])} D_box={_f(li['IV.2_spectral_box_dim'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.probe:
        probe(a.workers)
    elif a.sweep:
        sweep(a.workers)
    else:
        ap.error("need --probe or --sweep")


if __name__ == "__main__":
    main()
