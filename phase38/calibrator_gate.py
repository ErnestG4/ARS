"""
Phase 38 calibrator gate — BLOCKING pre-flight for the reliability ledger.

Structural-null audit (PHASE38_RELIABILITY_LEDGER_BRIEF.md):

  NULL      A cell with NO stable per-cell axis: each window's events replaced by a
            rate-matched Poisson draw at that window's own event count. Split-half
            rho MUST return ~0. Any positive rho is estimator-side leakage and the
            ledger would be measuring the pipeline, not the cells.

  POSITIVE  A synthetic per-cell axis of known reliability rho_true. The estimator
            must recover rho_true within CI. (synthetic_validate_fitters)

Arms, to localise leakage if the null fails:

  A  3 surrogates, seeds re-derived as default_rng(seed + 98765) inside the window
     loop -- EXACTLY as phase32b/per_cell_decomposition.py:173 does it. Because
     win_dur is constant within a session, the surrogate triple is a deterministic
     function of n alone: two cells with equal event counts get byte-identical
     surrogates, and z becomes a deterministic function of (real_p7, n).
  B  3 surrogates, independent per (cell, window). Isolates arm A's shared-seed bug.
  C  100 surrogates, independent per (cell, window). The Phase 38 repair.
  D  analytic positive control, no padic: z_w = sqrt(a)*axis + sqrt(1-a)*noise.

If A leaks and B does not, the banked z_w values inherit a rate-driven correlation
and rho(p7 @ 3 surr) measured in TOOLKIT §9 is itself an OVERESTIMATE.

Run:  /home/combust/fmexplorer/bin/python3 phase38/calibrator_gate.py
"""

import itertools
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)

from arithmetic_toolkit import padic_amplitude_v4  # noqa: E402

Q_MAX = 200
N_WINDOWS = 5
WIN_DUR = 600.5 / N_WINDOWS  # nmo concatenated duration per session / n_windows
SHARED_SEED_BASE = 98765     # phase32b constant
OUT = Path(ROOT_DIR) / "data" / "phase38_results"
OUT.mkdir(parents=True, exist_ok=True)


def p7(events):
    return float(padic_amplitude_v4(events, q_max=Q_MAX)["per_prime"][7]["normalised_per_q"])


# ---- surrogate p7 caches --------------------------------------------------
_shared_cache = {}


def shared_surrogate_p7(n, n_seeds=3):
    """Arm A: the as-implemented surrogate. Depends ONLY on n."""
    if (n, n_seeds) not in _shared_cache:
        vals = []
        for seed in range(n_seeds):
            rng = np.random.default_rng(seed + SHARED_SEED_BASE)
            vals.append(p7(np.sort(rng.uniform(0, WIN_DUR, size=n))))
        _shared_cache[(n, n_seeds)] = np.asarray(vals)
    return _shared_cache[(n, n_seeds)]


def independent_surrogate_p7(n, n_seeds, rng):
    return np.asarray([p7(np.sort(rng.uniform(0, WIN_DUR, size=n))) for _ in range(n_seeds)])


def z_of(real, sur):
    return (real - sur.mean()) / max(sur.std(), 1e-6)


# ---- reliability ----------------------------------------------------------
def rho5(M):
    """Spearman-Brown reliability of the 5-window mean, rank-robust."""
    k = M.shape[1]
    pr = [spearmanr(M[:, i], M[:, j]).statistic for i, j in itertools.combinations(range(k), 2)]
    rb = float(np.mean(pr))
    return (k * rb / (1 + (k - 1) * rb)) if rb > 0 else float("nan"), rb


def split_half_ci(M, n_boot=2000, seed=7):
    odd, even = M[:, ::2].mean(1), M[:, 1::2].mean(1)
    r = spearmanr(odd, even).statistic
    rng = np.random.default_rng(seed)
    bs = [spearmanr(odd[i], even[i]).statistic
          for i in (rng.integers(0, len(odd), len(odd)) for _ in range(n_boot))]
    return r, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def _worker(task):
    """One null cell: 5 windows of rate-matched Poisson, z under arms A/B/C."""
    idx, ns = task
    rng = np.random.default_rng(1_000_000 + idx)
    zA, zB, zC = [], [], []
    for n in ns:
        real = p7(np.sort(rng.uniform(0, WIN_DUR, size=n)))   # the NULL cell's own draw
        zA.append(z_of(real, shared_surrogate_p7(n, 3)))
        zB.append(z_of(real, independent_surrogate_p7(n, 3, rng)))
        zC.append(z_of(real, independent_surrogate_p7(n, 100, rng)))
    return zA, zB, zC


def main():
    df = pd.read_parquet(Path(ROOT_DIR) / "data/phase32b_results/per_cell_decomposition_merged.parquet")
    d = df[(df.p7_status == "OK") & (df.p7_n_windows_used == 5)]
    N = d[[f"n_w{i}" for i in range(5)]].values.astype(int)
    print(f"null cohort: {len(N)} cells x 5 windows (event counts taken from the real cells)")

    from multiprocessing import Pool
    with Pool(10) as pool:
        res = pool.map(_worker, list(enumerate(N)), chunksize=8)

    arms = {"A_3surr_shared_seed (as-implemented)": np.array([r[0] for r in res]),
            "B_3surr_independent": np.array([r[1] for r in res]),
            "C_100surr_independent": np.array([r[2] for r in res])}

    report = {}
    print("\n=== NULL calibrator: rho MUST be ~0 (no per-cell axis exists) ===")
    for nm, M in arms.items():
        rk, rb = rho5(M)
        r, lo, hi = split_half_ci(M)
        leak = not (lo <= 0 <= hi)
        report[nm] = dict(rho5=None if rk != rk else rk, mean_pair_r=rb,
                          split_half=r, ci=[lo, hi], leaks=bool(leak))
        flag = "*** LEAKS ***" if leak else "clean"
        print(f"  {nm:38s} rho5={rk if rk==rk else float('nan'):+.4f}  "
              f"split-half={r:+.4f} [{lo:+.4f},{hi:+.4f}]  {flag}")

    print("\n=== POSITIVE control (arm D): recover known rho ===")
    rng = np.random.default_rng(11)
    dpos = {}
    for a in (0.05, 0.10, 0.20, 0.40):
        axis = rng.normal(size=len(N))
        M = np.sqrt(a) * axis[:, None] + np.sqrt(1 - a) * rng.normal(size=(len(N), 5))
        rk, _ = rho5(M)
        expect = 5 * a / (1 + 4 * a)
        ok = abs(rk - expect) < 0.08
        dpos[f"a={a}"] = dict(rho5_measured=rk, rho5_expected=expect, ok=bool(ok))
        print(f"   r1_true={a:.2f}  expected rho5={expect:.4f}  measured={rk:.4f}  "
              f"{'OK' if ok else '*** FAIL ***'}")

    gate_pass = (not report["B_3surr_independent"]["leaks"]
                 and not report["C_100surr_independent"]["leaks"]
                 and all(v["ok"] for v in dpos.values()))
    out = dict(null_arms=report, positive_control=dpos, gate_pass=bool(gate_pass),
               note="Arm A is the as-implemented estimator; leakage there indicts the banked z_w.")
    (OUT / "calibrator_validation.json").write_text(json.dumps(out, indent=2))
    print(f"\nGATE: {'PASS' if gate_pass else 'FAIL'}   -> data/phase38_results/calibrator_validation.json")
    if report["A_3surr_shared_seed (as-implemented)"]["leaks"]:
        print("ARM A LEAKS: the banked phase32b z_w carry estimator-side correlation "
              "through shared, n-determined surrogates. rho(p7 @ 3 surr) is an OVERESTIMATE.")


if __name__ == "__main__":
    main()
