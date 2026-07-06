"""
cross_substrate/fibonacci_lambda_run.py — Fibonacci Hamiltonian coupling-λ sweep.

Follow-up to the AM-vs-Fibonacci confluence test (am_confluence.py, §3(g)). That test
found AM-critical D_box≈0.513 overshoots BELOW the Fibonacci reference (0.628 at λ=2),
flagging a coupling-correspondence caveat: AM-critical is its self-dual λ=1, but the
Fibonacci ref was at *its* λ=2, and the Fibonacci D_box is itself coupling-dependent.

This sweeps the Sturmian/Fibonacci Hamiltonian coupling λ at α=golden and asks: does
some Fibonacci coupling's D_box reach AM-crit's ≈0.51? If yes → the two are the same
fractal class up to coupling-reparametrization (the gap was a coupling artifact); if the
Fibonacci D_box(λ) curve floors above 0.51 → genuinely distinct operator families.

  Fibonacci/Sturmian H_{golden,φ}: (Hψ)_n = ψ_{n+1} + ψ_{n-1} + λ·χ_{[1−α,1)}({nα+φ})ψ_n
    Cantor spectrum ∀λ>0; D_box → 1 as λ→0 (→ free Laplacian band), decreasing with λ.

METHODOLOGY FIX vs the banked reference: compute D_box at **N=50k — matched to the AM
confluence sweep** (the banked Fibonacci point was N=8000; box_dim is resolution-
sensitive). Includes an N-convergence check at λ=2 (N=8000/50k/100k) to test whether the
banked 0.628 is N-stable or whether the original AM-vs-Fib comparison carried an N-mismatch.
Instrument identical to am_confluence (same box_dim + poly_unfold + 8φ).

Modes:  --sweep [--workers 10]
Out:    coordinates/fibonacci-lambda.jsonl
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

from cross_substrate.axes import canonical_spacings, FAMILY_I, compute_family_II  # noqa: E402
from cross_substrate.sturmian_hamiltonian_run import (                            # noqa: E402
    sturmian_eigs, poly_unfold, box_dim)

COORD = os.path.join(_HERE, "coordinates")
GOLDEN = (np.sqrt(5.0) - 1.0) / 2.0
N_PHI = 8
PHIS = (np.arange(N_PHI) + 0.5) / N_PHI            # match am_confluence / sturmian-ham
N_BASE = 50_000                                    # matched to am_confluence sweep
# coupling grid: bracket the banked 0.628 (λ=2) and AM-crit 0.513; push high (D_box↓ with λ)
LAMBDAS = [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0]
N_CONV = {2.0: [8_000, 100_000]}                   # N-stability check at the reference coupling
AM_CRIT_DBOX = 0.5136                              # am-confluence λ=1, N=200k (the target)
FIB_REF_DBOX_N8K = 0.6279349210480618              # banked Fibonacci-golden (N=8000)


def _fingerprint(lam, n, phis=PHIS):
    perphi_s, dboxes, evs_unf = [], [], []
    for phi in phis:
        ev = sturmian_eigs(GOLDEN, float(phi), lam=lam, n=n)
        evs_unf.append(poly_unfold(ev))
        perphi_s.append(canonical_spacings(evs_unf[-1]))
        db = box_dim(ev)
        if db is not None:
            dboxes.append(db)
    pooled = np.concatenate(perphi_s)
    fI = {k: fn(pooled) for k, fn in FAMILY_I.items()}
    fII_list = [compute_family_II(u) for u in evs_unf]
    fII = {k: (float(np.mean([d[k] for d in fII_list
                              if isinstance(d.get(k), (int, float))]))
               if any(isinstance(d.get(k), (int, float)) for d in fII_list) else None)
           for k in fII_list[0]}
    d_box = float(np.mean(dboxes)) if dboxes else None
    return fI, fII, d_box, int(pooled.size)


def _task(arg):
    lam, n = arg
    fI, fII, d_box, npool = _fingerprint(lam, n)
    return (lam, n, fI, fII, d_box, npool)


def sweep(workers):
    tasks = [(lam, N_BASE) for lam in LAMBDAS]
    tasks += [(lam, n) for lam, ns in N_CONV.items() for n in ns if n != N_BASE]
    print(f"FIBONACCI Hamiltonian λ-sweep @ α=golden — {len(tasks)} cells, {workers} workers, "
          f"N={N_BASE} (matched to am_confluence), {N_PHI}φ")
    print(f"  target: AM-crit D_box={AM_CRIT_DBOX:.3f}; banked Fib ref (N=8k)={FIB_REF_DBOX_N8K:.3f}")
    print(f"{'λ':>5s} {'N':>7s} {'W1δ':>6s} {'ks_gue':>7s} {'q':>6s} {'D_box':>6s}  vs AM-crit(0.514)")
    recs = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_task, t) for t in tasks]
        results = [fu.result() for fu in as_completed(futs)]
    for lam, n, fI, fII, d_box, npool in sorted(results, key=lambda r: (r[0], r[1])):
        axes = {**fI, **fII, "IV.2_spectral_box_dim": d_box}
        d_gap = (d_box - AM_CRIT_DBOX) if d_box is not None else None
        recs.append({
            "substrate": "fibonacci-lambda",
            "cell_id": f"golden/lam{lam:g}/N{n}",
            "axes_computed": axes,
            "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim",
                                    "III.1_p2", "III.4_scalar_sum"],
            "extraction_method": f"Fibonacci/Sturmian Hamiltonian (α=golden, λ={lam:g}); "
                                 f"poly_unfold(deg12) Family I/II + box_dim D_box, {N_PHI}φ "
                                 f"[instrument-matched to am_confluence; N={n}]",
            "extraction_audit": {
                "alpha": float(GOLDEN), "alpha_class": "golden_quadratic",
                "lam": lam, "N": n, "n_phi": N_PHI, "n_pooled_spacings": npool,
                "D_box_minus_AMcrit": d_gap,
                "purpose": "coupling-correspondence sweep vs AM-confluence §3(g); "
                           "does Fibonacci D_box(λ) reach AM-crit 0.51?"},
            "source_artifact": "generated (deterministic eigensolve)",
            "computed_date": date.today().isoformat()})
        def f(v):
            return f"{v:.3f}" if isinstance(v, (int, float)) else "  -  "
        print(f"{lam:>5g} {n:>7d} {f(fI.get('I.1_w1_clock')):>6s} "
              f"{f(fI.get('I.5_ks_gue')):>7s} {f(fI.get('I.8_brody_q')):>6s} "
              f"{f(d_box):>6s}  Δ={f(d_gap)}")

    out = os.path.join(COORD, "fibonacci-lambda.jsonl")
    with open(out, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ wrote {os.path.relpath(out, _HERE)} ({len(recs)} cells)")
    print("[coupling-correspondence] does the Fibonacci D_box(λ) curve pass through "
          "AM-crit's 0.51? — flag, don't interpret.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.sweep:
        sweep(a.workers)
    else:
        ap.error("need --sweep")


if __name__ == "__main__":
    main()
