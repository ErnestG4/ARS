"""
phase34b/liouville_events.py — Liouville function L(n) sign-change
positions for Phase 34b.

λ(n) = (-1)^Ω(n), where Ω is the number-of-prime-factors function with
multiplicity.  L(n) = Σ_{k=1}^n λ(k) is the Liouville summatory.

Unlike μ, λ is non-zero on every integer, so L changes value by ±1 at
every n.  Sign-changes of L are therefore "random-walk-like" crossings
of zero, modulated by the arithmetic structure of λ.

Pólya's conjecture (1919) — that L(n) < 0 for all n ≥ 2 — was falsified
by Haselgrove (1958).  Tanaka (1980) located the smallest counterexample
at n = 906,150,257.  Phase 34b's N_MAX must include this counterexample
for any meaningful sign-change analysis; the existing project sieve at
N=10⁷ (data/mertens_liouville_results.json) found a single sign-change
(the initial L(2)=0 → L(3)=-1 transition with L(1)=+1) and then no
crossings until the counterexample.

This module sieves λ via the project's existing smallest-prime-factor
recurrence (the µ-style sieve, but using λ(n) = -λ(n // p) with no
zero case).  For N ≤ 10⁹ this fits comfortably in memory.  For N > 10⁹
a segmented variant would be required (out of scope for Phase 34b's
back-to-back session).

Caches to data/phase34b_results/liouville_signchanges_N{N_MAX}.npz.
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

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34b_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def lambda_sieve(N: int, chunk: int = 10**7) -> np.ndarray:
    """Compute λ(n) for n = 1..N via fully-vectorised Ω-sieve.

    λ(n) = (-1)^Ω(n), where Ω is the number of prime factors with
    multiplicity.  We compute Ω by:

      1. Sieve primes up to √N (tiny, in-memory).
      2. For each small prime p ≤ √N and each power pᵏ ≤ N:
         omega[pᵏ::pᵏ] += 1  and  small_part[pᵏ::pᵏ] *= p
         (small_part accumulates the small-prime part of each n.)
      3. Each n has at most ONE prime factor > √N (since two such would
         exceed N).  After processing all small primes, n / small_part[n]
         is either 1 or that single large prime.  Add 1 to omega for
         n / small_part[n] > 1.  Done in chunks to bound memory.

    Returns int8 array of length N+1 with λ at index n; λ(0) = 0,
    λ(1) = +1.

    Memory: ~1 GB omega int8 + ~4 GB small_part int32 for N=10⁹.
    Runtime: ~30-90s for N=10⁹.
    """
    print(f"[liouville_events] vectorised Ω-sieve up to N = {N}…")
    t0 = time.perf_counter()
    sqrt_N = int(np.sqrt(N))

    # Step 1 — primes ≤ √N
    is_prime = np.ones(sqrt_N + 1, dtype=bool)
    is_prime[:2] = False
    for p in range(2, int(np.sqrt(sqrt_N)) + 1):
        if is_prime[p]:
            is_prime[p * p::p] = False
    small_primes = np.flatnonzero(is_prime).tolist()
    print(f"  small_primes (≤ √N = {sqrt_N}): {len(small_primes)} primes")

    # Step 2 — slice-add omega and slice-mul small_part for each small p^k
    omega = np.zeros(N + 1, dtype=np.int8)
    small_part = np.ones(N + 1, dtype=np.int32)
    for p in small_primes:
        pk = p
        while pk <= N:
            omega[pk::pk] += 1
            small_part[pk::pk] *= p
            if pk > N // p:    # avoid overflow on pk * p
                break
            pk *= p
    print(f"  small-prime slice phase done in {time.perf_counter() - t0:.1f}s")

    # Step 3 — large-prime residue check in chunks
    t1 = time.perf_counter()
    n_chunks = (N + chunk) // chunk
    for c in range(n_chunks):
        a = c * chunk
        b = min((c + 1) * chunk, N + 1)
        if a >= b:
            break
        idx = np.arange(a, b, dtype=np.int64)
        sp_ck = small_part[a:b].astype(np.int64)
        residue = idx // sp_ck
        omega[a:b] += (residue > 1).astype(np.int8)
    print(f"  large-prime residue phase done in "
          f"{time.perf_counter() - t1:.1f}s")

    # Free small_part before allocating λ (memory-tight at N=10⁹).
    del small_part

    # λ(n) = (-1)^Ω(n).  λ(0) = 0 (n=0 not used); λ(1) = 1.
    omega_max = int(omega.max())
    lam = np.where(omega & 1, np.int8(-1), np.int8(1))
    lam[0] = 0
    del omega
    print(f"[liouville_events] λ sieve total: "
          f"{time.perf_counter() - t0:.1f}s; |Ω| max = {omega_max}")
    return lam


def sign_change_positions(L: np.ndarray) -> np.ndarray:
    """Same convention as Mertens: skip zeros, find transitions in
    sign(L[1:]) with zero values skipped."""
    s = np.sign(L[1:])
    nz_mask = s != 0
    s_nz = s[nz_mask]
    nz_idx = np.where(nz_mask)[0]
    flips = np.where(np.diff(s_nz) != 0)[0]
    return nz_idx[flips + 1] + 1


def zero_positions(L: np.ndarray) -> np.ndarray:
    """Integer n where L(n) = 0.  More numerous than strict sign-changes."""
    return (np.where(L[1:] == 0)[0] + 1).astype(np.int64)


def load_or_compute(N_MAX: int = 10**9,
                     cache_path: Path | None = None,
                     force: bool = False) -> dict:
    """Compute λ + L sign-changes and zeros; cache.

    Returns dict with:
        n_max, signchanges (np.int64), zero_positions (np.int64),
        L_at_decades (list[int]).
    """
    if cache_path is None:
        cache_path = OUT_DIR / f'liouville_signchanges_N{N_MAX}.npz'
    if cache_path.exists() and not force:
        d = np.load(cache_path, allow_pickle=False)
        return dict(
            n_max=int(d['n_max']),
            signchanges=d['signchanges'].astype(np.int64),
            zero_positions=d['zero_positions'].astype(np.int64),
            L_at_decades=d['L_at_decades'].tolist(),
        )

    print(f"[liouville_events] === N_MAX = {N_MAX} ===")
    lam = lambda_sieve(N_MAX)
    print(f"[liouville_events] streaming cumsum + sign-change detection…")
    t0 = time.perf_counter()
    # Stream L = cumsum(λ) in chunks; record sign-change positions and
    # zero positions without materialising the full L int64 array (8 GB
    # at N=10⁹).  Decade values L(10^k) are recorded as we pass them.
    sc_list: list[int] = []
    zs_list: list[int] = []
    L_sum = np.int64(0)
    prev_sign = np.int8(0)
    CHUNK = 10 ** 7
    decades_target = [10 ** k for k in range(1, int(np.log10(N_MAX)) + 1)]
    decades_value: dict[int, int] = {}
    L_max = 0
    L_min = 0
    for a in range(1, N_MAX + 1, CHUNK):
        b = min(a + CHUNK, N_MAX + 1)
        L_chunk = (lam[a:b].astype(np.int64).cumsum()) + L_sum
        L_sum = int(L_chunk[-1])
        for d in decades_target:
            if a <= d < b:
                decades_value[d] = int(L_chunk[d - a])
        # Sign-change detection with running prev_sign across chunk seam
        signs = np.sign(L_chunk).astype(np.int8)
        # Process within-chunk: skip zeros, detect transitions
        all_signs = np.concatenate(([prev_sign], signs)) if prev_sign != 0 \
            else signs
        nz_mask = all_signs != 0
        if nz_mask.any():
            s_nz = all_signs[nz_mask]
            nz_idx_local = np.flatnonzero(nz_mask)
            flips = np.flatnonzero(np.diff(s_nz) != 0)
            # Map flip indices back to absolute positions
            #   prev_sign included → offset is -1 from absolute (a + i - 1)
            offset = -1 if (prev_sign != 0) else 0
            for fi in flips:
                local = int(nz_idx_local[fi + 1])  # post-flip position in concat
                abs_pos = a + local + offset
                if abs_pos >= 1:
                    sc_list.append(abs_pos)
        # Zero positions in chunk
        zero_local = np.flatnonzero(signs == 0)
        if zero_local.size:
            for z in zero_local.tolist():
                zs_list.append(a + int(z))
        # Update prev_sign with the last nonzero sign of this chunk
        last_nz = signs[signs != 0]
        if last_nz.size:
            prev_sign = np.int8(last_nz[-1])
        L_max = max(L_max, int(L_chunk.max()))
        L_min = min(L_min, int(L_chunk.min()))
        del L_chunk, signs, all_signs
    sc = np.asarray(sc_list, dtype=np.int64)
    zs = np.asarray(zs_list, dtype=np.int64)
    print(f"  done in {time.perf_counter() - t0:.1f}s; "
          f"|L| range = [{L_min}, {L_max}]")
    decades = [decades_value.get(d, None) for d in decades_target]
    print(f"[liouville_events] {sc.size} sign-changes and {zs.size} zeros in "
          f"[1, {N_MAX}]")
    print(f"[liouville_events] L at decades 10^1..10^{len(decades)}: {decades}")
    if sc.size > 0:
        print(f"[liouville_events] first 10 sign-changes: "
              f"{sc[:min(10, sc.size)].tolist()}")
        if sc.size > 10:
            print(f"[liouville_events] last 5 sign-changes: "
                  f"{sc[-5:].tolist()}")
    if zs.size > 0:
        print(f"[liouville_events] first 10 zeros: "
              f"{zs[:min(10, zs.size)].tolist()}")

    np.savez_compressed(cache_path,
                         n_max=np.array(N_MAX, dtype=np.int64),
                         signchanges=sc,
                         zero_positions=zs,
                         L_at_decades=np.array(decades, dtype=np.int64))
    print(f"[liouville_events] cached → {cache_path}")
    return dict(n_max=int(N_MAX), signchanges=sc, zero_positions=zs,
                 L_at_decades=decades)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--N', type=int, default=10**9)
    p.add_argument('--force', action='store_true')
    args = p.parse_args()
    load_or_compute(args.N, force=args.force)
