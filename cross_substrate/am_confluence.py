"""
cross_substrate/am_confluence.py — AM λ-sweep confluence test at golden θ.

Tests the operator-IS-substrate framing's strongest concrete prediction: does the
Almost-Mathieu operator's fingerprint TRAJECTORY (λ-sweep at golden θ, through
criticality λ=1) pass through the Fibonacci Hamiltonian's fingerprint?

  AM_{λ,θ,φ}: (Hψ)_n = ψ_{n+1} + ψ_{n-1} + 2λcos(2π(θn+φ))ψ_n,   θ = golden.
    λ<1 sub-critical   → absolutely-continuous (band) spectrum     → D_box ≈ 1
    λ=1 critical       → singular-continuous zero-measure Cantor   → D_box < 1
    λ>1 super-critical → pure-point (localized) spectrum

Reference = the Fibonacci Hamiltonian (= Sturmian-Ham @ golden), Cantor ∀λ>0,
D_box≈0.628, q≈0, W1δ≈1.79 (coordinates/sturmian-hamiltonian.jsonl).

INSTRUMENT-MATCHED to Fibonacci so the comparison is apples-to-apples:
  • D_box via box_dim on RAW eigenvalues — instrument-independent; the PRIMARY
    confluence axis (Family IV), the one Fibonacci is placed on.
  • Family I/II via the SAME poly_unfold (deg-12 polynomial IDS) Fibonacci used.
This deliberately does NOT use the rotnum matched leg (am.jsonl). Its Family-I
values therefore compare to sturmian-hamiltonian.jsonl, NOT to am.jsonl; D_box is
the axis that crosses both legs. Direct eigensolve + poly-IDS → cheap, no O(N·L)
rotnum unfold.

The relevant "convergence" near criticality is FINITE-N (the Cantor structure is an
N→∞ limit): λ=1.0 run at several N; the trajectory shape is banked regardless of
whether any single N fully resolves the Cantor set (Phase-35 critical-λ lesson —
bank what you get, characterize where it bends).

Modes:  --hedge | --probe | --sweep [--workers 10]
Out:    coordinates/am-confluence.jsonl
"""
from __future__ import annotations

import os
# pin threads BEFORE numpy import (LAPACK oversubscription guard under ProcessPool)
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

from unfold_rotnum import am_eigs, GOLDEN                              # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I, compute_family_II  # noqa: E402
# instrument identity with the Fibonacci reference: SAME box_dim, SAME poly_unfold
from cross_substrate.sturmian_hamiltonian_run import box_dim, poly_unfold          # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
WORK = os.path.join(COORD, "am_work")

N_PHI = 8                                          # match Fibonacci reference (8 φ)
PHIS = (np.arange(N_PHI) + 0.5) / N_PHI            # match Fibonacci offsets
N_BASE = 50_000                                    # sweep baseline (brief)
# dense around criticality where the trajectory shape matters most (brief)
LAMBDAS = [0.5, 0.7, 0.9, 0.95, 0.99, 1.0, 1.01, 1.05, 1.1, 1.3, 1.5]
# finite-N convergence at / near criticality (Cantor is an N→∞ limit)
N_CONV = {1.0: [50_000, 100_000, 200_000], 0.99: [100_000], 1.01: [100_000]}
FIB_DBOX = 0.6279349210480618                      # Fibonacci-golden reference D_box


def _regime(lam):
    return "sub_AC" if lam < 1.0 else "critical" if lam == 1.0 else "sup_PP"


def _fingerprint(lam, n, phis=PHIS):
    """Instrument-matched fingerprint of AM(λ, golden, N=n): Family I/II via
    poly_unfold, D_box via box_dim on raw eigenvalues. Pooled over φ exactly as
    sturmian_hamiltonian_run.run() does."""
    perphi_s, dboxes, evs_unf = [], [], []
    for phi in phis:
        ev = am_eigs(lam, n, float(phi), GOLDEN)
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


# ── hedge: D_box on already-banked AM-sub-golden eigenvalues ──────────────────
def hedge():
    print("HEDGE — D_box on banked AM-sub-golden eigenvalues vs Fibonacci-golden 0.628")
    print("(sub-AC band spectrum should give D_box≈1: 'obviously-doesn't-match')")
    for stem in ("eig_sub_N100k", "eig_sub_N125k"):
        dbs = []
        for i in range(16):                        # banked at 16 φ
            f = os.path.join(WORK, f"{stem}_phi{i}.npy")
            if not os.path.exists(f):
                continue
            db = box_dim(np.load(f))
            if db is not None:
                dbs.append(db)
        if dbs:
            print(f"  {stem:18s}: D_box = {np.mean(dbs):.4f} "
                  f"(±{np.std(dbs):.4f}, n={len(dbs)}φ)   vs Fib 0.628")
    print("→ if AM-sub D_box≈1 and Fib=0.628, the two-point contrast 'doesn't match' "
          "as predicted (AC band vs Cantor); the sweep is the real test.")


# ── probe: eigensolve timing across N (single λ near criticality) ─────────────
def probe():
    print("PROBE — eigensolve+fingerprint wall per φ at golden θ, λ=1.0 (1 thread):")
    for n in (50_000, 100_000, 200_000, 500_000):
        t0 = time.perf_counter()
        ev = am_eigs(1.0, n, float(PHIS[0]), GOLDEN)
        t_eig = time.perf_counter() - t0
        t1 = time.perf_counter()
        _ = box_dim(ev); _ = canonical_spacings(poly_unfold(ev))
        t_post = time.perf_counter() - t1
        print(f"  N={n:>7d}: eig {t_eig:6.2f}s + post {t_post:5.2f}s "
              f"= {t_eig + t_post:6.2f}s/φ  → {(t_eig+t_post)*N_PHI:6.1f}s/cell ({N_PHI}φ)")


# ── sweep: the confluence trajectory ──────────────────────────────────────────
def _sweep_task(arg):
    lam, n = arg
    t0 = time.perf_counter()
    fI, fII, d_box, npool = _fingerprint(lam, n)
    return (lam, n, fI, fII, d_box, npool, time.perf_counter() - t0)


def sweep(workers):
    tasks = [(lam, N_BASE) for lam in LAMBDAS]
    tasks += [(lam, n) for lam, ns in N_CONV.items() for n in ns if n != N_BASE]
    print(f"AM CONFLUENCE λ-sweep @ golden θ — {len(tasks)} cells, {workers} workers, "
          f"instrument-matched to Fibonacci (box_dim + poly_unfold, {N_PHI}φ)")
    print(f"{'λ':>5s} {'N':>7s} {'regime':>9s} {'W1δ':>6s} {'ks_gue':>7s} "
          f"{'q':>6s} {'D_box':>6s}  vs Fib(0.628)")
    recs = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_sweep_task, t) for t in tasks]
        results = [fu.result() for fu in as_completed(futs)]
    for lam, n, fI, fII, d_box, npool, dt in sorted(results, key=lambda r: (r[0], r[1])):
        axes = {**fI, **fII, "IV.2_spectral_box_dim": d_box}
        d_gap = (d_box - FIB_DBOX) if d_box is not None else None
        recs.append({
            "substrate": "am-confluence",
            "cell_id": f"golden/lam{lam:g}/N{n}",
            "axes_computed": axes,
            "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim",
                                    "III.1_p2", "III.4_scalar_sum"],
            "extraction_method": f"AM tridiagonal eigs (θ=golden); poly_unfold(deg12) "
                                 f"Family I/II + box_dim D_box, {N_PHI}φ pooled "
                                 f"[INSTRUMENT-MATCHED to Fibonacci, NOT rotnum/am.jsonl]",
            "extraction_audit": {
                "lam": lam, "theta": float(GOLDEN), "theta_class": "golden",
                "N": n, "n_phi": N_PHI, "regime": _regime(lam),
                "n_pooled_spacings": npool,
                "D_box_minus_Fib": d_gap,
                "instrument": "poly_unfold+box_dim (Fibonacci-matched); compares to "
                              "sturmian-hamiltonian.jsonl, not am.jsonl",
                "finite_N_note": ("criticality: Cantor is an N→∞ limit; D_box at finite N "
                                  "under-resolves the set" if lam == 1.0 else None)},
            "source_artifact": "generated (deterministic eigensolve)",
            "computed_date": date.today().isoformat()})
        def f(v):
            return f"{v:.3f}" if isinstance(v, (int, float)) else "  -  "
        print(f"{lam:>5g} {n:>7d} {_regime(lam):>9s} {f(fI.get('I.1_w1_clock')):>6s} "
              f"{f(fI.get('I.5_ks_gue')):>7s} {f(fI.get('I.8_brody_q')):>6s} "
              f"{f(d_box):>6s}  Δ={f(d_gap)}")

    # also (re-)bank the Fibonacci-golden reference as the fixed comparison point,
    # tagged so it's findable alongside the trajectory
    out = os.path.join(COORD, "am-confluence.jsonl")
    with open(out, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ wrote {os.path.relpath(out, _HERE)} ({len(recs)} cells)")
    print("[confluence] does AM's trajectory pass through Fibonacci-golden's "
          "fingerprint (D_box≈0.628, q≈0) at λ=1.0? — flag, don't interpret.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hedge", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.hedge:
        hedge()
    elif a.probe:
        probe()
    elif a.sweep:
        sweep(a.workers)
    else:
        ap.error("need --hedge / --probe / --sweep")


if __name__ == "__main__":
    main()
