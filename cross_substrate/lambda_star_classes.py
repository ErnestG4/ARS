"""
cross_substrate/lambda_star_classes.py — λ*(class): step or continuum? (new arc)

§3(h) found the AM↔Fibonacci matching coupling λ* is α-invariant ~3.4 within the metallic
means (quadratics) and jumps to ~10.7 for Liouville. This maps λ*(class) across a richer
α-set to resolve WHAT λ* tracks:
  (a) STEP at CF-boundedness — λ* is a discrete bounded-vs-unbounded-CF signature (two
      universality classes among irrationals, divided at CF-boundedness); OR
  (b) CONTINUOUS with irrationality measure μ — single class, λ* a smooth function of μ;
      the metallic-mean cluster and Liouville become endpoints of a continuum.

Critical discriminator: **e** (μ=2 like the quadratics, but UNBOUNDED CF like Liouville).
  (a) predicts e high (~10, unbounded group); (b) predicts e low (~3.4, μ=2 group).
Plus higher metallic means [0;4,4̄],[0;5,5̄] (bounded CF, μ=2, larger quotients) test whether
λ* creeps up with quotient MAGNITUDE within bounded-CF — a third model.

Per class: AM-critical D_box (λ=1, self-dual) + Fibonacci-α D_box(λ) curve → crossing λ*.
Same instrument as theta_class_correspondence / liouville_nconv (box_dim+poly_unfold, 8φ, N=50k).
L_iter discipline: unbounded-CF classes (e,ln2,π,Liouville) get an N-convergence flag — the
N=50k λ* is preliminary for those pending a spot N-check at the decisive cell (e).

Out: coordinates/lambda-star-classes.jsonl, figure P10.  Run: --run [--workers 10]
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
N = 50_000
LAM_GRID = [1.0, 2.0, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0]
AM_CRIT_LAM = 1.0

# (name, value, cf_bounded, irrationality_measure μ, max_quotient, description)
CLASSES = [
    ("golden",    (np.sqrt(5) - 1) / 2,          True,  2.0,  1,  "[0;1,1,…] metallic"),
    ("silver",    np.sqrt(2) - 1,                 True,  2.0,  2,  "[0;2,2,…] metallic"),
    ("bronze",    (np.sqrt(13) - 3) / 2,          True,  2.0,  3,  "[0;3,3,…] metallic"),
    ("metallic4", np.sqrt(5) - 2,                 True,  2.0,  4,  "[0;4,4,…] √5−2"),
    ("metallic5", (np.sqrt(29) - 5) / 2,          True,  2.0,  5,  "[0;5,5,…]"),
    ("e_minus_2", np.e - 2,                        False, 2.0,  99, "e−2: μ=2 but UNBOUNDED CF (discriminator)"),
    ("ln2",       np.log(2),                       False, 3.57, 99, "ln2: μ≈3.57, unbounded CF"),
    ("pi_minus_3", np.pi - 3,                      False, 7.10, 99, "π−3: μ≲7.10, unbounded CF"),
    ("liouville", sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), False, 1e9, 99,
                  "Σ10^−k!: μ=∞, unbounded CF"),
]


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
    kind, name, val, lam = arg
    if kind == "am":
        out = _fingerprint(lambda phi: am_eigs(lam, N, phi, val))
    else:
        out = _fingerprint(lambda phi: sturmian_eigs(val, phi, lam=lam, n=N))
    return (kind, name, lam, *out)


def _crossing(lams, dbs, target):
    for i in range(len(lams) - 1):
        d0, d1 = dbs[i], dbs[i + 1]
        if (d0 - target) * (d1 - target) <= 0 and d0 != d1:
            return lams[i] + (target - d0) * (lams[i + 1] - lams[i]) / (d1 - d0)
    return None


def run(workers):
    tasks = [("am", n, v, AM_CRIT_LAM) for n, v, *_ in CLASSES]
    tasks += [("fib", n, v, lam) for n, v, *_ in CLASSES for lam in LAM_GRID]
    print(f"λ*(class) — {len(tasks)} cells, {workers} workers, N={N}, {N_PHI}φ")
    print("  resolve: does λ* STEP at CF-boundedness or scale CONTINUOUSLY with μ? (e is the discriminator)")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_task, t) for t in tasks]
        res = [fu.result() for fu in as_completed(futs)]
    am = {r[1]: r for r in res if r[0] == "am"}
    fib = {}
    for r in res:
        if r[0] == "fib":
            fib.setdefault(r[1], []).append(r)
    for c in fib:
        fib[c].sort(key=lambda r: r[2])

    recs, summary = [], []
    print(f"\n{'class':11s} {'CF':>9s} {'μ':>5s} {'AM-crit':>8s} {'λ*':>6s}")
    for name, val, bounded, mu, maxq, desc in CLASSES:
        # task tuple = (kind, name, lam, fI, fII, d_box, npool) → idx 3,4,5,6
        ad = am[name][5]
        recs.append(_rec("am", name, AM_CRIT_LAM, am[name][3], am[name][4], am[name][5], am[name][6],
                         bounded, mu, maxq, desc))
        lams = [r[2] for r in fib[name]]
        dbs = [r[5] for r in fib[name]]
        for r in fib[name]:
            recs.append(_rec("fib", name, r[2], r[3], r[4], r[5], r[6], bounded, mu, maxq, desc))
        lam_star = _crossing(lams, dbs, ad)
        summary.append((name, bounded, mu, ad, lam_star))
        flag = "" if bounded else " *N-prelim"
        cfs = "bounded" if bounded else "UNbounded"
        mus = "∞" if mu > 1e8 else f"{mu:.2f}"
        print(f"{name:11s} {cfs:>9s} {mus:>5s} {ad:>8.3f} "
              f"{(f'{lam_star:.2f}' if lam_star else 'none>16'):>6s}{flag}")

    with open(os.path.join(COORD, "lambda-star-classes.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ wrote lambda-star-classes.jsonl ({len(recs)} cells) in {(time.perf_counter()-t0)/60:.1f} min")
    print("[step-vs-continuum] e (μ=2, UNbounded CF): λ*≈3.4 ⇒ tracks μ/algebraicity; "
          "λ*≈10 ⇒ steps at CF-boundedness. Flag, don't interpret.")
    _figure(summary)


def _rec(kind, name, lam, fI, fII, d_box, npool, bounded, mu, maxq, desc):
    return {"substrate": "lambda-star-classes",
            "cell_id": f"{kind}/{name}/lam{lam:g}/N{N}",
            "axes_computed": {**fI, **fII, "IV.2_spectral_box_dim": d_box},
            "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim"],
            "extraction_method": f"{'AM-critical(λ=1)' if kind=='am' else 'Fibonacci'} class={name}, "
                                 f"λ={lam:g}; box_dim+poly_unfold(deg12), {N_PHI}φ, N={N}",
            "extraction_audit": {"operator": kind, "lagrange_class": name, "cf": desc,
                                 "cf_bounded": bounded, "irrationality_measure": mu,
                                 "max_quotient": maxq, "theta_or_alpha": float(_aval(name)),
                                 "lam": lam, "N": N, "n_phi": N_PHI,
                                 "N_converged": (kind == "am" or bounded)},
            "source_artifact": "generated (deterministic eigensolve)",
            "computed_date": date.today().isoformat()}


def _aval(name):
    return next(v for n, v, *_ in CLASSES if n == name)


def _figure(summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    XCAP = 9.0  # plot μ=∞ (Liouville) at a capped x with an ∞ tick
    for name, bounded, mu, ad, lam_star in summary:
        if lam_star is None:
            continue
        x = XCAP if mu > 1e8 else mu
        face = ("#1f77b4" if bounded else "white")
        ax.scatter([x], [lam_star], s=170, marker=("o" if bounded else "^"),
                   facecolor=face, edgecolor=("k" if bounded else "#d62728"), lw=1.6, zorder=5)
        lbl = name + ("" if mu < 1e8 else " (μ=∞)")
        ax.annotate(lbl, (x, lam_star), fontsize=7, xytext=(6, 3), textcoords="offset points")
    ax.axhspan(3.3, 3.5, color="0.88", zorder=0)
    ax.annotate("metallic-mean band λ*≈3.4", (2.0, 3.4), fontsize=8, color="0.4",
                xytext=(0, 6), textcoords="offset points")
    ax.set_xticks([2, 3, 4, 5, 6, 7, XCAP])
    ax.set_xticklabels(["2", "3", "4", "5", "6", "7", "∞"])
    ax.set_xlabel("irrationality measure μ  (Liouville at ∞)")
    ax.set_ylabel("matching coupling λ*")
    ax.set_title("P10 λ*(class): step at CF-boundedness or continuous with μ?\n"
                 "● bounded-CF (quadratics)   ▲ unbounded-CF (transcendentals); e at μ=2 is the discriminator")
    ax.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P10_lambda_star_classes.png")
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
