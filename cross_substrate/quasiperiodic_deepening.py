"""
cross_substrate/quasiperiodic_deepening.py — deepen Job 1 for the two operators that joined the family.

Job 1 found gaah (ρ=−0.72) and ext_harper (ρ=−0.70) stratify by approximability at λ≈1 (D_box, N=50k,
coarse grid). This deepens that: (a) a FINE coupling grid around λ=1 to pin where the stratification
peaks and its shape, and (b) N-CONVERGENCE (N=50k→100k) of D_box at the critical coupling to confirm the
stratification is robust, not a finite-N artifact (the AM/Liouville-style check). 9 Lagrange classes.

Reuses Job 1's validated operator eigensolves + box_dim. Out: coordinates/quasiperiodic-deepening.jsonl
+ figure P_qpo_deepening.png. Run: --run [--workers 10].
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

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.axes import canonical_spacings, FAMILY_I                      # noqa: E402
from cross_substrate.sturmian_hamiltonian_run import box_dim, poly_unfold          # noqa: E402
from cross_substrate.quasiperiodic_operators import OPERATORS, CLASSES, N_PHI, PHIS  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
OPS = ["gaah", "ext_harper"]               # the two that joined the family
FINE_COUPLINGS = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4]
N_CONV = [50_000, 100_000]                  # N-convergence at the critical coupling
CRIT_LAM = 1.0


def _f(v):
    return None if v is None or not (isinstance(v, (int, float)) and np.isfinite(v)) else float(v)


def _fp(opname, lam, theta, n):
    fn = OPERATORS[opname]
    perphi_s, dboxes = [], []
    for phi in PHIS:
        ev = fn(lam, float(phi), theta, n=n)
        perphi_s.append(canonical_spacings(poly_unfold(ev)))
        db = box_dim(ev)
        if db is not None:
            dboxes.append(db)
    pooled = np.concatenate(perphi_s)
    return {"IV.2_spectral_box_dim": _f(float(np.mean(dboxes))) if dboxes else None,
            "I.8_brody_q": _f(FAMILY_I["I.8_brody_q"](pooled))}


def _task(arg):
    kind, opname, cls, alpha, lam, n = arg
    fp = _fp(opname, lam, alpha, n)
    return (kind, opname, cls, lam, n, fp)


def run(workers):
    tasks = [("fine", op, c, a, lam, 50_000) for op in OPS for c, a, mu in CLASSES for lam in FINE_COUPLINGS]
    tasks += [("nconv", op, c, a, CRIT_LAM, n) for op in OPS for c, a, mu in CLASSES for n in N_CONV]
    print(f"QPO DEEPENING — {len(tasks)} cells (gaah/ext_harper: fine λ-grid @50k + N-conv @λ=1), {workers}w")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_task, tasks))
    recs = []
    fine = {}   # op -> lam -> {cls: D_box}
    nconv = {}  # op -> n -> {cls: D_box}
    clsidx = [c for c, *_ in CLASSES]
    for kind, op, cls, lam, n, fp in res:
        recs.append({"substrate": f"qpo-{op}", "cell_id": f"{op}/{cls}/lam{lam:g}/N{n}/{kind}",
                     "operator": op, "lagrange_class": cls, "coupling": lam, "N": n, "kind": kind,
                     "axes_computed": fp,
                     "extraction_audit": {"irrationality_measure": dict((c, mu) for c, _, mu in CLASSES)[cls]},
                     "source_artifact": "generated (tridiagonal/banded eigensolve)",
                     "computed_date": date.today().isoformat()})
        if kind == "fine":
            fine.setdefault(op, {}).setdefault(lam, {})[cls] = fp["IV.2_spectral_box_dim"]
        else:
            nconv.setdefault(op, {}).setdefault(n, {})[cls] = fp["IV.2_spectral_box_dim"]
    with open(os.path.join(COORD, "quasiperiodic-deepening.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")

    from scipy import stats
    rank = np.arange(len(CLASSES))
    def _rho_spread(d):
        vals = [d.get(c) for c in clsidx]
        valid = [(r, v) for r, v in zip(rank, vals) if isinstance(v, float)]
        if len(valid) < 5:
            return None, None
        rho = stats.spearmanr([a for a, _ in valid], [b for _, b in valid])[0]
        spread = max(b for _, b in valid) - min(b for _, b in valid)
        return rho, spread

    print("\n(a) FINE coupling grid — ρ(rank,D_box) & spread per λ (where does stratification peak?):")
    for op in OPS:
        print(f"  {op}:")
        for lam in FINE_COUPLINGS:
            rho, sp = _rho_spread(fine[op][lam])
            print(f"    λ={lam:>4g}  ρ={rho:+.3f}  spread={sp:.3f}" if rho is not None else f"    λ={lam:g} (n<5)")
    print("\n(b) N-CONVERGENCE @λ=1 — ρ(rank,D_box) & golden/Liouville D_box at N=50k vs 100k:")
    for op in OPS:
        for n in N_CONV:
            rho, sp = _rho_spread(nconv[op][n])
            g = nconv[op][n].get("golden"); l = nconv[op][n].get("liouville")
            print(f"  {op:11s} N={n:>7d}  ρ={rho:+.3f}  golden={g:.3f} liouville={l:.3f} (spread {sp:.3f})")
    print(f"\n→ {len(recs)} cells in {(time.perf_counter()-t0)/60:.1f} min. ρ stable across N ⇒ "
          "stratification is N-robust (not finite-N artifact). Flag, don't interpret.")
    _figure(fine)


def _figure(fine):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cmap = plt.cm.viridis(np.linspace(0, 1, len(CLASSES)))
    clsnames = [c for c, *_ in CLASSES]
    fig, axes = plt.subplots(1, len(OPS), figsize=(6 * len(OPS), 5), sharey=True)
    for ax, op in zip(axes, OPS):
        for i, cn in enumerate(clsnames):
            ys = [fine[op][lam].get(cn) for lam in FINE_COUPLINGS]
            ax.plot(FINE_COUPLINGS, [y if isinstance(y, float) else np.nan for y in ys], "o-",
                    color=cmap[i], ms=4, label=cn)
        ax.axvline(1.0, ls=":", color="0.5"); ax.set_title(op); ax.set_xlabel("coupling λ (fine)")
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("D_box (IV.2)"); axes[-1].legend(fontsize=6, ncol=2)
    fig.suptitle("QPO deepening: D_box vs fine coupling by Lagrange class (stratification peaks near λ=1)")
    p = os.path.join(_HERE, "figures", "P_qpo_deepening.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
