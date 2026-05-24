"""
cross_substrate/liouville_nconv.py — Liouville N-convergence disambiguator (§3(h) open).

The θ-class sweep found the AM↔Fibonacci confluence generalizes across the quadratics but
left Liouville ambiguous: at N=50k, AM-crit-Liouville D_box=0.491 vs Fibonacci-Liouville
floor 0.530 (no crossing in the λ≤8 grid). Liouville's unbounded CF quotients make box_dim
finite-N-fragile (fine spectral structure tied to its huge approximation denominators), so the
"no crossing" could be either:
  (A) bounded-CF-only correspondence — Liouville is genuinely outside the universality class;
  (B) N-limited — N=50k under-resolves Liouville; higher N reveals a crossing.

Disambiguator: push BOTH legs at θ/α=Liouville to higher N. Does AM-crit-Liouville D_box
converge? Does the Fibonacci-Liouville curve drop with N and/or extended λ toward it?
L_iter discipline (Phase-35): Liouville may show convergence pathology analogous to AM's
sup-side at large N — report D_box(N), flag if it does not cleanly converge; do not assume.

Instrument identical to theta_class_correspondence (box_dim + poly_unfold, 8φ).
Out: coordinates/liouville-nconv.jsonl.  Run:  --run [--workers 10]
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
LIOUVILLE = sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720))
# banked N=50k anchors (from am-confluence-theta / fibonacci-lambda-theta)
AM_50K = 0.491
FIB_50K = {6.0: 0.565, 8.0: 0.530}   # from the θ-sweep Liouville curve

# AM-crit (λ=1) at higher N; Fibonacci λ=8 N-stability + extended-λ floor probe
AM_TASKS = [("am", 1.0, N) for N in (100_000, 200_000)]
FIB_TASKS = ([("fib", 8.0, N) for N in (100_000, 200_000)] +
             [("fib", lam, 100_000) for lam in (6.0, 10.0, 12.0, 16.0)])


def _fingerprint(eigfn):
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
    kind, lam, n = arg
    t0 = time.perf_counter()
    if kind == "am":
        fI, fII, d_box, npool = _fingerprint(lambda phi: am_eigs(lam, n, phi, LIOUVILLE))
    else:
        fI, fII, d_box, npool = _fingerprint(lambda phi: sturmian_eigs(LIOUVILLE, phi, lam=lam, n=n))
    return (kind, lam, n, fI, fII, d_box, npool, time.perf_counter() - t0)


def run(workers):
    tasks = AM_TASKS + FIB_TASKS
    print(f"LIOUVILLE N-CONVERGENCE — {len(tasks)} cells, {workers} workers, {N_PHI}φ")
    print(f"  anchors @N=50k: AM-crit={AM_50K}, Fib(λ=8)={FIB_50K[8.0]}; does higher N cross?")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_task, t) for t in tasks]
        res = [fu.result() for fu in as_completed(futs)]

    recs = []
    am = sorted([r for r in res if r[0] == "am"], key=lambda r: r[2])
    fib = sorted([r for r in res if r[0] == "fib"], key=lambda r: (r[1], r[2]))

    print("\nAM-critical-Liouville (λ=1) — D_box(N):")
    print(f"  N=  50000: D_box={AM_50K:.3f}  (banked)")
    for _, lam, n, fI, fII, d_box, npool, dt in am:
        print(f"  N={n:>7d}: D_box={d_box:.3f}  ({dt:.0f}s)")
        recs.append(_rec("am", lam, n, fI, fII, d_box, npool))
    am_hiN = am[-1][5] if am else AM_50K

    print("\nFibonacci-Liouville — D_box(λ, N)   (target = AM-crit-Liouville converged):")
    for _, lam, n, fI, fII, d_box, npool, dt in fib:
        anchor = f"  [50k:{FIB_50K[lam]:.3f}]" if (n == 100_000 and lam in FIB_50K) else ""
        gap = d_box - am_hiN
        print(f"  λ={lam:>4g} N={n:>7d}: D_box={d_box:.3f}  Δvs-AMhiN={gap:+.3f}{anchor}  ({dt:.0f}s)")
        recs.append(_rec("fib", lam, n, fI, fII, d_box, npool))

    out = os.path.join(COORD, "liouville-nconv.jsonl")
    with open(out, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ wrote {os.path.relpath(out, _HERE)} ({len(recs)} cells)")
    print("[Liouville disambiguator] (A) bounded-CF-only if Fib floors above converged AM-crit; "
          "(B) N-limited if higher N drops Fib to a crossing. Flag, don't interpret.")


def _rec(kind, lam, n, fI, fII, d_box, npool):
    label = "AM-critical-Liouville (λ=1)" if kind == "am" else "Fibonacci-Liouville"
    return {"substrate": "liouville-nconv",
            "cell_id": f"{'am' if kind=='am' else 'fib'}/liouville/lam{lam:g}/N{n}",
            "axes_computed": {**fI, **fII, "IV.2_spectral_box_dim": d_box},
            "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim"],
            "extraction_method": f"{label}; box_dim + poly_unfold(deg12), {N_PHI}φ, N={n} "
                                 f"[Liouville N-convergence disambiguator, §3(h)]",
            "extraction_audit": {"operator": kind, "lagrange_class": "liouville",
                                 "theta_or_alpha": float(LIOUVILLE), "lam": lam, "N": n,
                                 "n_phi": N_PHI, "n_pooled_spacings": npool},
            "source_artifact": "generated (deterministic eigensolve)",
            "computed_date": date.today().isoformat()}


def figure():
    """P9 — Liouville confluence: full Fibonacci-Liouville D_box(λ) curve (θ-sweep λ≤8 @50k +
    extended λ @100k) vs the N-converged AM-crit-Liouville line; crossing at λ*≈10.7."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # Fibonacci-Liouville short arm (λ≤8, N=50k) from the θ-class sweep
    short = {}
    for l in open(os.path.join(COORD, "fibonacci-lambda-theta.jsonl")):
        r = json.loads(l)
        if r["extraction_audit"]["lagrange_class"] == "liouville":
            short[r["extraction_audit"]["lam"]] = r["axes_computed"]["IV.2_spectral_box_dim"]
    # extended arm (λ≥6, N=100k) + AM-crit from this run
    ext, am_crit = {}, None
    for l in open(os.path.join(COORD, "liouville-nconv.jsonl")):
        r = json.loads(l)
        a = r["extraction_audit"]
        if a["operator"] == "fib" and a["N"] == 100_000:
            ext[a["lam"]] = r["axes_computed"]["IV.2_spectral_box_dim"]
        if a["operator"] == "am" and a["N"] == 200_000:
            am_crit = r["axes_computed"]["IV.2_spectral_box_dim"]
    curve = dict(sorted({**short, **ext}.items()))
    lams, dbs = list(curve.keys()), list(curve.values())

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(lams, dbs, "^-", color="#1f77b4", lw=1.4, ms=7, label="Fibonacci α=Liouville  D_box(λ)")
    ax.axhline(am_crit, ls="--", color="#d62728", lw=1.3)
    ax.annotate(f"AM-critical-Liouville D_box={am_crit:.3f}\n(N-converged 50k–200k)",
                (11.5, am_crit), color="#d62728", fontsize=8, xytext=(0, 5),
                textcoords="offset points")
    ax.scatter([10.7], [am_crit], s=200, marker="*", color="#d62728", edgecolor="k", zorder=6)
    ax.annotate("λ*≈10.7", (10.7, am_crit), fontsize=9, color="#d62728",
                xytext=(6, -16), textcoords="offset points")
    # context: quadratic matching coupling band
    ax.axvspan(3.3, 3.5, color="0.85", alpha=0.6)
    ax.annotate("metallic-mean λ*≈3.4", (3.4, max(dbs)), fontsize=8, color="0.4",
                rotation=90, xytext=(-13, -90), textcoords="offset points")
    ax.set_xlabel("Fibonacci coupling λ")
    ax.set_ylabel("D_box (IV.2)")
    ax.set_title("P9 Liouville confluence — Fibonacci-Liouville reaches AM-critical at λ*≈10.7\n"
                 "(vs α-invariant λ*≈3.4 for the metallic means: matching coupling stratifies by class)")
    ax.legend(fontsize=9); ax.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P9_liouville_nconv.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--figure", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    elif a.figure:
        figure()
    else:
        ap.error("need --run or --figure")


if __name__ == "__main__":
    main()
