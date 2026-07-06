"""
phase34d/run_amendments.py — robustness amendments to the Phase 34d pre-pilot
in response to the post-commit critical read (2026-05-14).

Three additions:
  1. Bootstrap σ²(K, X) — resample with replacement from the angle array
     and recompute σ²/(N/K) over n_boot bootstrap samples per cell.  Gives
     error bars on the Step 3 ratios so "0.872 vs RW asymptote 1.0" carries
     a ± and we can say whether the 13% gap is finite-X correction or
     within statistical noise.
  2. Eisenstein at all K values matching the Gaussian scan (now feasible
     with the Cornacchia speed-up): X = 10⁷ with K ∈ {30, 100, 300, 1000,
     3000, 10000} so the Eisenstein shape-confirmation has parity with
     Gaussian (was: single point at K=10⁴).
  3. Seed-replicate NNS classification — 20 sub-samples (80% of angles
     per seed) for both Gaussian X=10⁶ and Eisenstein X=10⁶, recording
     the full distribution of (primary, rep_med, ks_gue_med).  Tests
     whether the Gaussian TR vs Eisenstein BL bulk-classification
     difference is stable or boundary-noise per §7.ter.22 metric-saturation
     discipline.

Outputs:
  data/phase34d_results/rw_variance_bootstrap.json
  data/phase34d_results/nns_seed_replicates.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34c'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34a'))

from gaussian_primes import gaussian_prime_angles
from eisenstein_primes import eisenstein_prime_angles
from run_rw_variance_direct import variance_in_arcs
from ars_classify import classify

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34d_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ───────────────────────── bootstrap σ²(K, X) ──────────────────────────


def bootstrap_variance(angles: np.ndarray,
                       K: int,
                       sector_length: float,
                       n_boot: int = 100,
                       n_grid: int = 2000,
                       rng: np.random.Generator | None = None) -> dict:
    """Bootstrap σ²(K, X)/(N/K) by half-sample partitioning.

    Strategy: partition the N angles into two random halves of size N/2.
    Compute σ²(K, X) on each half, scaled to N total via
    σ²_half × (N_full / N_half) — no, that doesn't work since σ² scales
    nonlinearly in N. Better strategy: take ⌊N · 0.5⌋ random angles
    (sub-sample without replacement, like Phase 22b 7-seed convention)
    n_boot times, compute σ²/(N/K) on each subsample, return mean ± std.

    The subsample's N is smaller (so β = log K / log N_sub differs slightly
    from full-N β), but the ratio σ²/(N/K) at fixed K is what RW predicts
    to follow min(1, 2β) — so we report the ratio at each subsample's β
    and aggregate.
    """
    if rng is None:
        rng = np.random.default_rng(0)
    N_full = len(angles)
    N_sub = N_full // 2
    ratios = np.empty(n_boot)
    sigma2s = np.empty(n_boot)
    betas = np.empty(n_boot)
    for s in range(n_boot):
        idx = rng.choice(N_full, size=N_sub, replace=False)
        sub = np.sort(angles[idx])
        sigma2 = variance_in_arcs(sub, K, sector_length, n_grid=n_grid)
        sigma2s[s] = sigma2
        ratios[s] = sigma2 / (N_sub / K)
        betas[s] = np.log(K) / np.log(N_sub)
    return dict(
        K=int(K),
        N_full=int(N_full),
        N_sub=int(N_sub),
        n_boot=int(n_boot),
        beta_mean=float(np.mean(betas)),
        ratio_mean=float(np.mean(ratios)),
        ratio_std=float(np.std(ratios)),
        ratio_p5=float(np.percentile(ratios, 5)),
        ratio_p95=float(np.percentile(ratios, 95)),
        sigma2_mean=float(np.mean(sigma2s)),
        sigma2_std=float(np.std(sigma2s)),
    )


def run_bootstrap_variance():
    print("=" * 78)
    print("Phase 34d amendment 1+2 — bootstrap σ²(K, X) and Eisenstein parity scan")
    print("=" * 78)
    records = []
    for substrate, gen, sector in [
        ('gaussian',   lambda X: gaussian_prime_angles(X, both_ideals=True),  np.pi / 2),
        ('eisenstein', lambda X: eisenstein_prime_angles(X, both_factors=True), np.pi / 3),
    ]:
        for X in (1_000_000, 10_000_000):
            t0 = time.time()
            angles = gen(X)
            N = len(angles)
            print(f"  [{substrate}] X = {X:.0e}, N = {N}, gen = {time.time()-t0:.1f}s")
            # Match Step 3 K scan for X=10⁶ and X=10⁷
            if X == 1_000_000:
                K_list = [10, 30, 100, 300, 1000]
            else:
                K_list = [30, 100, 300, 1000, 3000, 10000]
            for K in K_list:
                rng = np.random.default_rng(hash((substrate, X, K)) % 2**32)
                rec = bootstrap_variance(angles, K, sector,
                                          n_boot=50, n_grid=2000, rng=rng)
                rec['substrate'] = substrate
                rec['X'] = X
                # RW prediction at the average beta
                rec['rw_pred'] = float(min(1.0, 2.0 * rec['beta_mean']))
                rec['within_error_of_RW'] = bool(
                    abs(rec['ratio_mean'] - rec['rw_pred']) <
                    2.0 * rec['ratio_std']
                )
                records.append(rec)
                z = (rec['rw_pred'] - rec['ratio_mean']) / max(rec['ratio_std'], 1e-9)
                print(f"    K={K:>6d}  β={rec['beta_mean']:.3f}  "
                      f"ratio = {rec['ratio_mean']:.3f} ± {rec['ratio_std']:.3f}  "
                      f"RW = {rec['rw_pred']:.3f}  (RW − emp)/σ = {z:+.2f}")
    out = OUT_DIR / 'rw_variance_bootstrap.json'
    with open(out, 'w') as f:
        json.dump({
            'phase': '34d amendment',
            'method': '50-bootstrap half-sample partitions, σ²(K, X) recomputed',
            'records': records,
        }, f, indent=2)
    print(f"\n→ wrote {out}")
    return records


# ───────────────────────── seed-replicate NNS ──────────────────────────


def seed_replicate_nns(angles: np.ndarray, sector_length: float,
                       n_seeds: int = 20,
                       subsample_frac: float = 0.8,
                       q_max: int = 30) -> dict:
    """Run joint_q_profile (deployed classifier) on n_seeds subsamples.

    Each seed takes a different random subsample of subsample_frac * N
    angles (without replacement), unfolds via Hecke uniform density,
    and runs classify(). Records primary, rep_med, ks_gue_med per seed.
    """
    N_full = len(angles)
    N_sub = int(N_full * subsample_frac)
    primaries = []
    rep_meds = []
    ks_gues = []
    for s in range(n_seeds):
        rng = np.random.default_rng(s)
        idx = rng.choice(N_full, size=N_sub, replace=False)
        sub = np.sort(angles[idx])
        unfolded = sub * (N_sub / sector_length)
        r = classify(unfolded.astype(np.float64), q_max=q_max,
                      min_events_per_q=30, return_full=False)
        primaries.append(r['primary'])
        rep_meds.append(float(r['rep_med']))
        ks_gues.append(float(r['ks_gue_med']))
        if s == 0 or s == n_seeds - 1 or (s + 1) % 5 == 0:
            print(f"    seed {s:>2d}: primary={r['primary']}  "
                  f"rep_med={r['rep_med']:.3f}  ks_gue_med={r['ks_gue_med']:.3f}")
    # Tally
    from collections import Counter
    primary_counts = dict(Counter(primaries))
    return dict(
        n_seeds=int(n_seeds),
        subsample_frac=float(subsample_frac),
        N_sub=int(N_sub),
        primaries=primaries,
        primary_counts=primary_counts,
        rep_med_mean=float(np.mean(rep_meds)),
        rep_med_std=float(np.std(rep_meds)),
        rep_med_min=float(np.min(rep_meds)),
        rep_med_max=float(np.max(rep_meds)),
        ks_gue_mean=float(np.mean(ks_gues)),
        ks_gue_std=float(np.std(ks_gues)),
        rep_meds=rep_meds,
        ks_gues=ks_gues,
    )


def run_seed_replicate_nns():
    print()
    print("=" * 78)
    print("Phase 34d amendment 3 — seed-replicate NNS classification")
    print("=" * 78)
    records = {}
    for substrate, gen, sector in [
        ('gaussian',   lambda X: gaussian_prime_angles(X, both_ideals=True),  np.pi / 2),
        ('eisenstein', lambda X: eisenstein_prime_angles(X, both_factors=True), np.pi / 3),
    ]:
        X = 1_000_000
        print(f"\n[{substrate}] X = {X}")
        angles = gen(X)
        rec = seed_replicate_nns(angles, sector_length=sector,
                                  n_seeds=20, subsample_frac=0.8)
        rec['substrate'] = substrate
        rec['X'] = X
        rec['N_full'] = int(len(angles))
        records[f'{substrate}_X{X:.0e}'] = rec
        print(f"  → primary classifications across 20 seeds: {rec['primary_counts']}")
        print(f"  → rep_med = {rec['rep_med_mean']:.3f} ± {rec['rep_med_std']:.3f}  "
              f"[min {rec['rep_med_min']:.3f}, max {rec['rep_med_max']:.3f}]")
        print(f"  → ks_gue_med = {rec['ks_gue_mean']:.3f} ± {rec['ks_gue_std']:.3f}")
    out = OUT_DIR / 'nns_seed_replicates.json'
    with open(out, 'w') as f:
        json.dump({'phase': '34d amendment', 'records': records}, f, indent=2)
    print(f"\n→ wrote {out}")
    return records


# ───────────────────────────── main ─────────────────────────────


def main():
    bootstrap_recs = run_bootstrap_variance()
    nns_recs = run_seed_replicate_nns()

    # Summary discrimination on TR/BL boundary question
    print()
    print("=" * 78)
    print("Discrimination: Gaussian TR vs Eisenstein BL — real or boundary noise?")
    print("=" * 78)
    g = nns_recs['gaussian_X1e+06']
    e = nns_recs['eisenstein_X1e+06']
    # Are the rep_med distributions separated?
    g_mean, g_std = g['rep_med_mean'], g['rep_med_std']
    e_mean, e_std = e['rep_med_mean'], e['rep_med_std']
    # Welch-style separation
    sep = (g_mean - e_mean) / np.sqrt(g_std**2 + e_std**2)
    print(f"  Gaussian X=10⁶ rep_med: {g_mean:.3f} ± {g_std:.3f}  ({g['primary_counts']})")
    print(f"  Eisenstein X=10⁶ rep_med: {e_mean:.3f} ± {e_std:.3f}  ({e['primary_counts']})")
    print(f"  Welch-style separation: {sep:.2f} σ")
    if abs(sep) >= 2.0 and not (set(g['primary_counts'].keys()) &
                                  set(e['primary_counts'].keys())):
        verdict = "REAL_BULK_DIVERGENCE — substrates separable at the bulk-statistic level"
    elif set(g['primary_counts'].keys()) & set(e['primary_counts'].keys()):
        verdict = "BOUNDARY_ARTIFACT — primary class overlaps across seeds; discrete classifier overclaims on continuous metric"
    else:
        verdict = "AMBIGUOUS — separated rep_med but primary class differs; intermediate"
    print(f"\n  VERDICT: {verdict}")


if __name__ == '__main__':
    main()
