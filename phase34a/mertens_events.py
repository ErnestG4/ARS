"""
phase34a/mertens_events.py — Mertens sign-change positions for Phase 34a.

Sieves μ(n) up to N_MAX, builds M(n) = Σ_{k=1}^n μ(k), and records the
integer positions n where sign(M(n)) ≠ sign(M(n-1)) (skipping M=0
intervals via the same convention used in run_mertens_liouville.py).

The sign-change positions form a sparse integer point process on
[1, N_MAX].  This is the raw input to every Phase 34a analysis
(stationarity, NNS, RF, p-adic v4).

Caches to data/phase34a_results/mertens_signchanges_NMAX.npz.

Phase 34a in-scope: N_MAX = 10^7 (matches the historical computation
used at §7.bis / §7.ter.4 in the project; in the 10^3-10^4 event-count
range the brief identifies).  Out of scope: computing new M(n) values
beyond published tables.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34a_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def mu_sieve(N: int) -> np.ndarray:
    """Compute μ(n) for n = 1..N via smallest-prime-factor sieve.

    Returns int8 array of length N+1 with μ at index n.
    """
    smallest_p = np.zeros(N + 1, dtype=np.int32)
    for p in range(2, int(np.sqrt(N)) + 1):
        if smallest_p[p] == 0:
            smallest_p[p::p] = np.where(smallest_p[p::p] == 0,
                                         p, smallest_p[p::p])
    for p in range(int(np.sqrt(N)) + 1, N + 1):
        if smallest_p[p] == 0:
            smallest_p[p] = p
    mu = np.zeros(N + 1, dtype=np.int8)
    mu[1] = 1
    for n in range(2, N + 1):
        p = smallest_p[n]
        m = n // p
        mu[n] = 0 if (m % p == 0) else -mu[m]
    return mu


def sign_change_positions(M: np.ndarray) -> np.ndarray:
    """Return integer n where sign(M(n)) ≠ sign(M(n-1)), zeros skipped.

    Matches the convention used in run_mertens_liouville.py.  Input M
    is the cumulative array M[0]=0, M[n]=Σ_{k=1..n} μ(k).
    """
    s = np.sign(M[1:])
    nonzero = s != 0
    s_nz = s[nonzero]
    nz_idx = np.where(nonzero)[0]      # 0-based into M[1:]
    flips = np.where(np.diff(s_nz) != 0)[0]
    return nz_idx[flips + 1] + 1       # actual n


def load_or_compute(N_MAX: int = 10**7,
                     cache_path: Path | None = None,
                     force: bool = False) -> dict:
    """Return dict with keys:
        n_max, mu_sum_check (M at decades), M_values (M[1..N_MAX] -
        not cached, only on regen), signchanges (np.int64 array of
        integer positions).
    """
    if cache_path is None:
        cache_path = OUT_DIR / f'mertens_signchanges_N{N_MAX}.npz'
    if cache_path.exists() and not force:
        d = np.load(cache_path, allow_pickle=False)
        return dict(
            n_max=int(d['n_max']),
            signchanges=d['signchanges'].astype(np.int64),
            M_at_decades=d['M_at_decades'].tolist(),
        )

    print(f"[mertens_events] sieving μ to N = {N_MAX:.0e}…")
    t0 = time.perf_counter()
    mu = mu_sieve(N_MAX)
    M = np.cumsum(mu.astype(np.int64))
    sc = sign_change_positions(M).astype(np.int64)
    decades = [int(M[10 ** k]) for k in range(1, int(np.log10(N_MAX)) + 1)]
    elapsed = time.perf_counter() - t0
    print(f"[mertens_events] done in {elapsed:.1f}s — "
          f"{sc.size} sign changes in [1, {N_MAX}]")
    print(f"[mertens_events] M at decades 10^1..10^{len(decades)}: {decades}")

    np.savez_compressed(cache_path,
                         n_max=np.array(N_MAX, dtype=np.int64),
                         signchanges=sc,
                         M_at_decades=np.array(decades, dtype=np.int64))
    print(f"[mertens_events] cached → {cache_path}")
    return dict(n_max=int(N_MAX), signchanges=sc, M_at_decades=decades)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--N', type=int, default=10**7)
    p.add_argument('--force', action='store_true')
    args = p.parse_args()
    out = load_or_compute(args.N, force=args.force)
    print(f"\nLoaded {out['signchanges'].size} sign changes; first 10: "
          f"{out['signchanges'][:10].tolist()}")
    print(f"Last 5: {out['signchanges'][-5:].tolist()}")
