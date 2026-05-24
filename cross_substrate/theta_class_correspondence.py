"""
cross_substrate/theta_class_correspondence.py — does AM-θ ↔ Fibonacci-α generalize?

The golden confluence is confirmed (§3(g): AM-critical-golden ↔ Fibonacci-golden at λ≈3.46).
This asks whether the correspondence generalizes across the Lagrange classes: for each class,
does the AM-CRITICAL fingerprint (AM at its self-dual λ=1 — θ-independent by Aubry-André) at
θ=class coincide with the Fibonacci-α fingerprint at α=class, at some matched Fibonacci coupling?

  classes: golden (control), silver [0;2,2,…], bronze [0;3,3,…], liouville (unbounded quotients).

Two outputs, both flag-don't-interpret:
  (1) Does AM-critical D_box STRATIFY by θ-class? (parallel to the AM-sup-θ Brody stratification)
  (2) Does each Fibonacci-α D_box(λ) curve REACH its AM-critical-θ value? If every class matches
      at its own coupling → AM and Fibonacci are the same operator family up to parameterization
      (strongest operator-IS-substrate state). If golden-only → golden is special.

Instrument identical to am_confluence / fibonacci_lambda (box_dim on raw eigs + poly_unfold, 8φ,
N=50k). Cheap: tridiagonal eigensolves only.

Out: coordinates/am-confluence-theta.jsonl (AM-crit per class),
     coordinates/fibonacci-lambda-theta.jsonl (Fib λ-curve per class), figure P8.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase35a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from unfold_rotnum import am_eigs                                                  # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I, compute_family_II   # noqa: E402
from cross_substrate.sturmian_hamiltonian_run import sturmian_eigs, poly_unfold, box_dim  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
N_PHI = 8
PHIS = (np.arange(N_PHI) + 0.5) / N_PHI
N = 50_000

# Lagrange classes — values consistent with am_reextract / sturmian_hamiltonian_run
CLASSES = {
    "golden": ((np.sqrt(5.0) - 1.0) / 2.0, "quadratic [0;1,1,…]"),
    "silver": (np.sqrt(2.0) - 1.0, "quadratic [0;2,2,…]"),
    "bronze": ((np.sqrt(13.0) - 3.0) / 2.0, "quadratic [0;3,3,…]"),
    "liouville": (sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), "transcendental, unbounded"),
}
FIB_LAMBDAS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0]
AM_CRIT_LAM = 1.0   # self-dual critical coupling (θ-independent)


def _fingerprint(eigfn):
    """eigfn(phi) -> eigenvalues. Pooled-φ Family I + per-φ Family II + mean D_box."""
    perphi_s, dboxes, evs_unf = [], [], []
    for phi in PHIS:
        ev = eigfn(float(phi))
        evs_unf.append(poly_unfold(ev))
        perphi_s.append(canonical_spacings(evs_unf[-1]))
        db = box_dim(ev)
        if db is not None:
            dboxes.append(db)
    pooled = np.concatenate(perphi_s)
    fI = {k: fn(pooled) for k, fn in FAMILY_I.items()}
    fII_list = [compute_family_II(u) for u in evs_unf]
    fII = {k: (float(np.mean([d[k] for d in fII_list if isinstance(d.get(k), (int, float))]))
               if any(isinstance(d.get(k), (int, float)) for d in fII_list) else None)
           for k in fII_list[0]}
    return fI, fII, (float(np.mean(dboxes)) if dboxes else None), int(pooled.size)


def _task(arg):
    kind, cls, alpha, lam = arg
    if kind == "am":
        fI, fII, d_box, npool = _fingerprint(lambda phi: am_eigs(lam, N, phi, alpha))
    else:
        fI, fII, d_box, npool = _fingerprint(lambda phi: sturmian_eigs(alpha, phi, lam=lam, n=N))
    return (kind, cls, alpha, lam, fI, fII, d_box, npool)


def run(workers):
    tasks = [("am", c, v, AM_CRIT_LAM) for c, (v, _) in CLASSES.items()]
    tasks += [("fib", c, v, lam) for c, (v, _) in CLASSES.items() for lam in FIB_LAMBDAS]
    print(f"θ-CLASS CORRESPONDENCE — {len(tasks)} cells, {workers} workers, N={N}, {N_PHI}φ")
    print("  AM-critical (λ=1, self-dual) vs Fibonacci-α D_box(λ), per Lagrange class")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_task, t) for t in tasks]
        res = [fu.result() for fu in as_completed(futs)]

    am = {r[1]: r for r in res if r[0] == "am"}
    fib = {}
    for r in res:
        if r[0] == "fib":
            fib.setdefault(r[1], []).append(r)
    for c in fib:
        fib[c].sort(key=lambda r: r[3])

    # report + crossing per class
    print(f"\n{'class':10s} {'AM-crit D_box':>13s}  Fibonacci D_box(λ) → crossing λ*")
    am_recs, fib_recs, summary = [], [], []
    for c, (alpha, desc) in CLASSES.items():
        _, _, _, _, afI, afII, ad, an = am[c]
        am_recs.append(_rec("am-confluence-theta", f"{c}/lam1.0/N{N}", {**afI, **afII,
                       "IV.2_spectral_box_dim": ad}, alpha, c, 1.0, desc,
                       "AM-critical (self-dual λ=1)"))
        lams = [r[3] for r in fib[c]]
        dbs = [r[6] for r in fib[c]]
        for r in fib[c]:
            fib_recs.append(_rec("fibonacci-lambda-theta", f"{c}/lam{r[3]:g}/N{N}",
                            {**r[4], **r[5], "IV.2_spectral_box_dim": r[6]},
                            alpha, c, r[3], desc, "Fibonacci/Sturmian-Ham"))
        lam_star = _crossing(lams, dbs, ad)
        summary.append((c, ad, lam_star))
        cross = f"{lam_star:.2f}" if lam_star else "NO CROSS in grid"
        print(f"{c:10s} {ad:>13.3f}  range[{min(dbs):.3f},{max(dbs):.3f}] → λ*={cross}")

    _write("am-confluence-theta.jsonl", am_recs)
    _write("fibonacci-lambda-theta.jsonl", fib_recs)
    print(f"\n→ wrote am-confluence-theta.jsonl ({len(am_recs)}) + "
          f"fibonacci-lambda-theta.jsonl ({len(fib_recs)})")
    print("[θ-correspondence] does AM-crit D_box stratify by class, and does each "
          "Fibonacci-α curve reach its AM-crit value? — flag, don't interpret.")
    _figure(am, fib, summary)


def _crossing(lams, dbs, target):
    """First λ where the (monotone-ish decreasing) D_box(λ) crosses target."""
    for i in range(len(lams) - 1):
        d0, d1 = dbs[i], dbs[i + 1]
        if (d0 - target) * (d1 - target) <= 0 and d0 != d1:
            return lams[i] + (target - d0) * (lams[i + 1] - lams[i]) / (d1 - d0)
    return None


def _rec(substrate, cid, axes, alpha, cls, lam, desc, method):
    return {"substrate": substrate, "cell_id": cid, "axes_computed": axes,
            "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim",
                                    "III.1_p2", "III.4_scalar_sum"],
            "extraction_method": f"{method} (class={cls}, λ={lam:g}); box_dim + poly_unfold(deg12), "
                                 f"{N_PHI}φ, N={N} [instrument-matched to am_confluence]",
            "extraction_audit": {"alpha_or_theta": float(alpha), "lagrange_class": cls,
                                 "cf": desc, "lam": lam, "N": N, "n_phi": N_PHI},
            "source_artifact": "generated (deterministic eigensolve)",
            "computed_date": date.today().isoformat()}


def _write(name, recs):
    with open(os.path.join(COORD, name), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")


def _figure(am, fib, summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIGDIR = os.path.join(_HERE, "figures")
    cmap = {"golden": "#d4af37", "silver": "#9aa0a6", "bronze": "#9c6b30", "liouville": "#1f77b4"}
    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    for c in CLASSES:
        lams = [r[3] for r in fib[c]]
        dbs = [r[6] for r in fib[c]]
        ad = am[c][6]
        ax.plot(lams, dbs, "^-", color=cmap[c], lw=1.3, ms=6, label=f"Fib α={c}")
        ax.axhline(ad, ls="--", color=cmap[c], lw=0.9, alpha=0.7)
        lam_star = next((s[2] for s in summary if s[0] == c), None)
        if lam_star:
            ax.scatter([lam_star], [ad], s=150, marker="*", color=cmap[c],
                       edgecolor="k", zorder=6)
    ax.set_xlabel("Fibonacci coupling λ")
    ax.set_ylabel("D_box (IV.2)")
    ax.set_title("P8 θ-class correspondence — Fibonacci-α D_box(λ) vs AM-critical-θ (dashed)\n"
                 "★ = Fibonacci reaches the AM-crit value of its class")
    ax.legend(fontsize=8, ncol=2); ax.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "P8_theta_class_correspondence.png")
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
