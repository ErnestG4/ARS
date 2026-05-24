"""
cross_substrate/lambda_star_nconv.py — N-confirmation of the discriminating λ* cells.

The λ*(class) map (lambda_star_classes.py) flagged the unbounded-CF cells N-preliminary
(N=50k). The qualitative verdict (continuous approximability stratification; NOT a step at
CF-boundedness) is N-robust — e at λ*=3.74 vs Liouville 10.24 has no plausible N-wobble
closing that gap — but the specific λ* of the load-bearing cells should be confirmed.

Liouville is already N-confirmed (liouville_nconv.py: λ*≈10.7 @ N=100k). This confirms the
two remaining decisive unbounded-CF cells, **e** (the discriminator, 50k λ*=3.74) and **π**
(50k λ*=7.64), at N=100k. Reports λ*(N) drift; flags any cell that moves notably.

Dict-based returns (no positional index mapping — the 50k-sweep crash lesson). Same
instrument (box_dim + poly_unfold, 8φ). Out: coordinates/lambda-star-nconv.jsonl.
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
N = 100_000

# decisive unbounded-CF cells: value, μ, banked 50k λ*, Fibonacci λ-grid bracketing the crossing
CELLS = {
    "e_minus_2":  {"val": np.e - 2.0,  "mu": 2.0,  "lam_star_50k": 3.74,
                   "fib_lams": [3.0, 3.5, 4.0, 5.0]},
    "pi_minus_3": {"val": np.pi - 3.0, "mu": 7.10, "lam_star_50k": 7.64,
                   "fib_lams": [6.0, 8.0, 10.0]},
}


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
    return {"fI": fI, "fII": fII, "d_box": (float(np.mean(dboxes)) if dboxes else None),
            "npool": int(pooled.size)}


def _task(arg):
    kind, cls, val, lam = arg
    if kind == "am":
        fp = _fingerprint(lambda phi: am_eigs(lam, N, phi, val))
    else:
        fp = _fingerprint(lambda phi: sturmian_eigs(val, phi, lam=lam, n=N))
    return {"kind": kind, "cls": cls, "lam": lam, **fp}


def _crossing(lams, dbs, target):
    order = sorted(range(len(lams)), key=lambda i: lams[i])
    lams = [lams[i] for i in order]; dbs = [dbs[i] for i in order]
    for i in range(len(lams) - 1):
        d0, d1 = dbs[i], dbs[i + 1]
        if (d0 - target) * (d1 - target) <= 0 and d0 != d1:
            return lams[i] + (target - d0) * (lams[i + 1] - lams[i]) / (d1 - d0)
    return None


def run(workers):
    tasks = []
    for cls, c in CELLS.items():
        tasks.append(("am", cls, c["val"], 1.0))
        tasks += [("fib", cls, c["val"], lam) for lam in c["fib_lams"]]
    print(f"λ* N-CONFIRMATION (e, π) @ N={N} — {len(tasks)} cells, {workers} workers, {N_PHI}φ")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_task, t) for t in tasks]
        res = [fu.result() for fu in as_completed(futs)]

    recs = []
    print(f"\n{'class':11s} {'μ':>5s} {'AM-crit':>8s} {'λ*(50k)':>8s} {'λ*(100k)':>9s} {'drift':>7s}")
    for cls, c in CELLS.items():
        am = next(r for r in res if r["kind"] == "am" and r["cls"] == cls)
        fibs = sorted([r for r in res if r["kind"] == "fib" and r["cls"] == cls],
                      key=lambda r: r["lam"])
        ad = am["d_box"]
        recs.append(_rec(am, cls, c))
        for r in fibs:
            recs.append(_rec(r, cls, c))
        lam_star = _crossing([r["lam"] for r in fibs], [r["d_box"] for r in fibs], ad)
        drift = (lam_star - c["lam_star_50k"]) if lam_star else None
        flag = ""
        if drift is not None and abs(drift) > 0.5:
            flag = "  <-- NOTABLE DRIFT"
        ls = f"{lam_star:.2f}" if lam_star else "none"
        ds = f"{drift:+.2f}" if drift is not None else "  -"
        print(f"{cls:11s} {c['mu']:>5.2f} {ad:>8.3f} {c['lam_star_50k']:>8.2f} "
              f"{ls:>9s} {ds:>7s}{flag}")

    with open(os.path.join(COORD, "lambda-star-nconv.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ wrote lambda-star-nconv.jsonl ({len(recs)} cells)")
    print("[N-confirm] e and π λ* at N=100k vs N=50k; >0.5 drift flagged. Liouville already "
          "N-confirmed (λ*≈10.7 @100k, liouville_nconv.py).")


def _rec(r, cls, c):
    return {"substrate": "lambda-star-nconv",
            "cell_id": f"{r['kind']}/{cls}/lam{r['lam']:g}/N{N}",
            "axes_computed": {**r["fI"], **r["fII"], "IV.2_spectral_box_dim": r["d_box"]},
            "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim"],
            "extraction_method": f"{'AM-critical(λ=1)' if r['kind']=='am' else 'Fibonacci'} "
                                 f"class={cls}, λ={r['lam']:g}; box_dim+poly_unfold(deg12), "
                                 f"{N_PHI}φ, N={N} [unbounded-CF N-confirmation]",
            "extraction_audit": {"operator": r["kind"], "lagrange_class": cls,
                                 "cf_bounded": False, "irrationality_measure": c["mu"],
                                 "theta_or_alpha": float(c["val"]), "lam": r["lam"], "N": N,
                                 "n_phi": N_PHI, "lam_star_50k_ref": c["lam_star_50k"]},
            "source_artifact": "generated (deterministic eigensolve)",
            "computed_date": date.today().isoformat()}


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
