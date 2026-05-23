"""
cross_substrate/am_reextract.py — Phase 1: AM matched re-extraction (parallel, hardened).

Phase 35 banked only the W1δ reduction, not eigenvalues/spacings. This recovers
AM into the landscape on the matched object-(a) leg. Three stages:

  A (eigensolve, ~min parallel): am_eigs per (cell,φ) → checkpoint
     coordinates/am_work/eig_{cell}_phi{i}.npy. The reusable raw object.
  B (unfold @ converged L, ~hours): O(N·L) Sturm unfold per (cell,φ) →
     checkpoint coordinates/am_work/unf_{cell}_phi{i}.npy. The expensive stage;
     48 independent tasks, parallel across local workers.
  agg: pool φ-ensemble positions per cell → matched Family I/II → coordinates/am.jsonl.

HARDENING: every task persists its own .npy before any post-processing; tasks
skip if their checkpoint exists (resumable / analyze-only re-run). Threads pinned
to 1 so the ProcessPool isn't oversubscribed by LAPACK.

Run:  ... --probe | --stage A | --stage B [--Lcap L] | --agg   [--workers 18]
"""
from __future__ import annotations

import os
# pin threads BEFORE numpy import (hardened-run pattern)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase35a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from unfold_rotnum import am_eigs, unfold_rotnum, GOLDEN  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
WORK = os.path.join(COORD, "am_work")
os.makedirs(WORK, exist_ok=True)

N_PHI = 16
PHIS = np.arange(N_PHI) / (2 * N_PHI)            # 16 pts in [0,0.5), spacing 1/32
THETA = GOLDEN
CELLS = [
    # core 6 (Night-1 brief §3, load-bearing rev-5.2.1). VI.1 α = banked Phase-35 loglog_alpha_mean.
    {"name": "sup_N50k", "N": 50000, "lam": 1.5, "delta": 0.5, "L": 25_600_000, "alpha": -0.0068, "converged": True},
    {"name": "sup_N70k", "N": 70000, "lam": 1.5, "delta": 0.5, "L": 25_600_000, "alpha": -0.0025, "converged": True},
    {"name": "sup_N100k", "N": 100000, "lam": 1.5, "delta": 0.5, "L": 6_400_000, "alpha": -0.0094, "converged": True},
    {"name": "sub_N70k", "N": 70000, "lam": 0.5, "delta": 0.5, "L": 6_400_000, "alpha": None, "converged": False},
    {"name": "sub_N100k", "N": 100000, "lam": 0.5, "delta": 0.5, "L": 1_600_000, "alpha": None, "converged": True},
    {"name": "sub_N125k", "N": 125000, "lam": 0.5, "delta": 0.5, "L": 6_400_000, "alpha": None, "converged": False},
]
# VI.2 N-scaling β across the 3 sup cells (converged sup spreads, Phase 35 banked)
SUP_N_SCALING = {"N": [50000, 70000, 100000], "spread": [0.1151, 0.3816, 0.847]}
CMAP = {c["name"]: c for c in CELLS}


def _eig_f(name, i):
    return os.path.join(WORK, f"eig_{name}_phi{i}.npy")


def _unf_f(name, i, L):
    return os.path.join(WORK, f"unf_{name}_phi{i}_L{L}.npy")


# ── module-level tasks (picklable for ProcessPool) ───────────────────────────
def _eig_task(arg):
    name, i = arg
    c = CMAP[name]
    f = _eig_f(name, i)
    if os.path.exists(f):
        return (name, i, "skip", 0.0)
    t0 = time.perf_counter()
    e = am_eigs(c["lam"], c["N"], float(PHIS[i]), THETA)
    np.save(f, e)
    return (name, i, "ok", time.perf_counter() - t0)


def _unfold_task(arg):
    name, i, Lcap = arg
    c = CMAP[name]
    L = min(c["L"], Lcap) if Lcap else c["L"]
    f = _unf_f(name, i, L)
    if os.path.exists(f):
        return (name, i, "skip", 0.0)
    e = np.load(_eig_f(name, i))
    t0 = time.perf_counter()
    unf = unfold_rotnum(e, c["lam"], THETA, L, phis=(float(PHIS[i]),))
    np.save(f, unf)
    return (name, i, "ok", time.perf_counter() - t0)


def _run_pool(tasks, fn, workers, label):
    print(f"[{label}] {len(tasks)} tasks, {workers} workers")
    t0 = time.perf_counter()
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(fn, t) for t in tasks]
        for fu in as_completed(futs):
            name, i, st, dt = fu.result()
            done += 1
            if st == "ok":
                print(f"  [{label}] {done}/{len(tasks)} {name} φ{i} {dt:.0f}s", flush=True)
    print(f"[{label}] complete in {(time.perf_counter()-t0)/60:.1f} min")


def stage_A(workers):
    _run_pool([(c["name"], i) for c in CELLS for i in range(N_PHI)],
              _eig_task, workers, "A")


def stage_B(workers, Lcap=None):
    tasks = [(c["name"], i, Lcap) for c in CELLS for i in range(N_PHI)]
    missing = [(n, i) for (n, i, _) in tasks if not os.path.exists(_eig_f(n, i))]
    if missing:
        raise SystemExit(f"Stage A incomplete: {len(missing)} eigfiles missing. Run --stage A.")
    _run_pool(tasks, _unfold_task, workers, "B")


def aggregate(Lcap=None):
    from cross_substrate.axes import (compute_family_I, compute_family_II,
                                       VI2_N_scaling_beta, canonical_spacings,
                                       I1_w1_clock)
    import datetime
    beta = VI2_N_scaling_beta(SUP_N_SCALING["N"], SUP_N_SCALING["spread"])  # VI.2 (substrate-level)
    recs = []
    for c in CELLS:
        L = min(c["L"], Lcap) if Lcap else c["L"]
        files = [_unf_f(c["name"], i, L) for i in range(N_PHI)]
        if not all(os.path.exists(f) for f in files):
            print(f"  agg: {c['name']} L={L} incomplete, skipping")
            continue
        # φ-ensemble aggregation — PER-φ then average. NEVER concatenate positions
        # across φ and re-diff (that interleaves 16 separately-unfolded spectra =
        # a superposition with spurious near-Poisson statistics). Family I on pooled
        # per-φ SPACINGS; Family II per-φ then mean. (W1δ reproduces Phase 35 per-φ.)
        from cross_substrate.axes import FAMILY_I
        perphi_pos = [np.asarray(np.load(f), float) for f in files]
        perphi_s = [canonical_spacings(p) for p in perphi_pos]
        pooled_s = np.concatenate(perphi_s)
        fI = {name: fn(pooled_s) for name, fn in FAMILY_I.items()}
        fII_list = [compute_family_II(p) for p in perphi_pos]
        def _avg(key):
            vals = [d[key] for d in fII_list if isinstance(d.get(key), (int, float))]
            return float(np.mean(vals)) if vals else None
        fII = {k: _avg(k) for k in fII_list[0]}
        axes = {**fI, **fII}
        axes["VI.1_L_iter_alpha"] = c.get("alpha")       # banked Phase-35 loglog_alpha
        axes["VI.2_N_scaling_beta"] = beta["beta"] if (beta and c["lam"] > 1) else None
        # per-φ W1δ spread (the Phase-35 fingerprint quantity) + non-degeneracy
        perphi_w1 = [I1_w1_clock(s) for s in perphi_s]
        perphi_w1 = [v for v in perphi_w1 if v is not None]
        w1_spread = float(np.ptp(perphi_w1)) if perphi_w1 else None
        frac_zero = float(np.mean(pooled_s <= 0))
        positions = pooled_s  # for n_positions audit below
        recs.append({
            "substrate": "AM", "cell_id": f"{c['name']}/lam{c['lam']}/Lconv{L}",
            "axes_computed": axes,
            "applicable_axes_not_yet_computed": [],
            "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim",
                                    "III.1_p2", "III.4_scalar_sum"],  # no RF run in Phase 35
            "extraction_method": f"unfold_rotnum @ L={L}, {N_PHI}φ pooled, θ=golden (matched object-a)",
            "extraction_audit": {"N": c["N"], "lam": c["lam"], "delta": c["delta"],
                                 "L_target": L, "L_converged": c.get("converged"),
                                 "n_phi": N_PHI, "n_pooled_spacings": int(positions.size),
                                 "perphi_W1d_spread": w1_spread,
                                 "agg_method": "per-φ then mean (Family II); pooled per-φ "
                                               "spacings (Family I); NOT position-concat",
                                 "frac_zero_spacings": round(frac_zero, 4),
                                 "VI2_beta_detail": beta if c["lam"] > 1 else None},
            "source_artifact": "coordinates/am_work/ (eig+unf checkpoints, permanent bank)",
            "computed_date": datetime.date.today().isoformat()})
        def _fm(v):
            return f"{v:.3f}" if isinstance(v, (int, float)) else str(v)
        print(f"  agg {c['name']} L={L}: {positions.size} pos  "
              f"W1δ={_fm(fI['I.1_w1_clock'])} ks_gue={_fm(fI['I.5_ks_gue'])} "
              f"brody={_fm(fI['I.8_brody_q'])} BRρ={_fm(fI['I.9_berry_robnik_rho'])}")
    if recs:
        with open(os.path.join(COORD, "am.jsonl"), "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        print(f"  → wrote coordinates/am.jsonl ({len(recs)} cells)")


def probe():
    print("AM PHASE-1 COST PROBE")
    for c in CELLS:
        t0 = time.perf_counter(); e = am_eigs(c["lam"], c["N"], 0.0, THETA)
        te = time.perf_counter() - t0
        t1 = time.perf_counter(); unfold_rotnum(e, c["lam"], THETA, 200_000, (0.0,))
        tu = (time.perf_counter() - t1) * (c["L"] / 200_000)
        print(f"  {c['name']}: eig {te:.0f}s/φ, unfold proj {tu/60:.0f}min/φ "
              f"(L={c['L']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--stage", choices=["A", "B"])
    ap.add_argument("--agg", action="store_true")
    ap.add_argument("--Lcap", type=int, default=None)
    ap.add_argument("--workers", type=int, default=18)
    a = ap.parse_args()
    if a.probe:
        probe()
    elif a.stage == "A":
        stage_A(a.workers)
    elif a.stage == "B":
        stage_B(a.workers, a.Lcap)
    elif a.agg:
        aggregate(a.Lcap)
    else:
        ap.error("need --probe / --stage A / --stage B / --agg")


if __name__ == "__main__":
    main()
