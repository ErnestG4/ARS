"""
Phase 2 acceptance tests for intermittency.py.

  Test A — RLE round-trip: hand-rolled binary series → expected dwells.
  Test B — Power-law recovery: synthetic dwells from inverse-CDF
           sampling at α=2.0, τ_min=10 → MLE recovers within ±0.1.
  Test C — Exponential rejection: synthetic exponential dwells → KS test
           rejects power-law fit (p < 0.05).
  Test D — Fano factor on Poisson process: F ≈ 1 across T.
  Test E — Sanity on Phase-1 PLL bank output (FM signal).
  Test F — Sanity on white noise.
"""
import math
import os
import sys

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

from intermittency import (  # noqa: E402
    extract_dwells, fit_power_law_mle, fano_factor,
    aggregate_unfolded_events, analyze_lock_map,
)
from pll_bank import pll_bank_gpu, PLLParams, farey_rationals  # noqa: E402


SR = 44100.0


# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test A — extract_dwells RLE round-trip")
print("=" * 72)
# 0,0,1,1,1,0,0,1,1,0,0,0,1
# slip runs: 2 (at start), 2 (middle), 3 (later)
# lock runs: 3 (first), 2 (middle), 1 (trailing)
# onsets at indices 2, 7, 12; offsets at 5, 9
s = np.array([0,0,1,1,1,0,0,1,1,0,0,0,1], dtype=np.uint8)
rec = extract_dwells(s)
print(f"  series:           {list(map(int, s))}")
print(f"  lock_dwells:      {list(rec.lock_dwells)}  (expected [3, 2, 1])")
print(f"  slip_dwells:      {list(rec.slip_dwells)}  (expected [2, 2, 3])")
print(f"  lock_onsets:      {list(rec.lock_onsets)}  (expected [2, 7, 12])")
print(f"  lock_offsets:     {list(rec.lock_offsets)} (expected [5, 9])")
print(f"  lock_fraction:    {rec.lock_fraction:.4f}    (expected 0.4615)")
assert list(rec.lock_dwells) == [3, 2, 1]
assert list(rec.slip_dwells) == [2, 2, 3]
assert list(rec.lock_onsets) == [2, 7, 12]
assert list(rec.lock_offsets) == [5, 9]
assert abs(rec.lock_fraction - 6/13) < 1e-6
print("  PASS")
print()


# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test B — power-law MLE recovers α=2.0 from synthetic samples (±0.1)")
print("=" * 72)
# Inverse-CDF sampling of continuous power law, then `floor` to integers.
# (`floor`, not `ceil`: a continuous sample in [k, k+1) maps to the integer
# bin k, which matches the discrete distribution P(τ=k) ≈ ∫_k^{k+1} p(x) dx.
# `ceil` would shift values in (τ_min, τ_min+1) to τ_min+1, giving an empty
# τ_min bin and biasing the MLE toward smaller α.)
def sample_power_law(n, alpha, tau_min, rng):
    U = rng.random(n)
    return np.floor(tau_min * (1 - U) ** (-1.0 / (alpha - 1.0))).astype(np.int64)

rng = np.random.default_rng(42)
for alpha_true in [1.7, 2.0, 2.5, 3.0]:
    samples = sample_power_law(20000, alpha_true, tau_min=10.0, rng=rng)
    fit = fit_power_law_mle(samples, tau_min=10.0, auto_tau_min=False)
    err = abs(fit.alpha - alpha_true)
    print(f"  α_true={alpha_true:.2f}  n_used={fit.n_used:6d}  "
          f"α_hat={fit.alpha:.4f} ± {fit.alpha_stderr:.4f}  "
          f"|err|={err:.4f}  KS={fit.ks_stat:.4f}  p={fit.ks_pvalue:.3f}")
    assert err < 0.1, f"FAIL: α recovery error {err:.3f} > 0.1"
print("  PASS")
print()


# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test C — KS rejects power-law fit on exponential dwells")
print("=" * 72)
# Exponential samples with mean = 50.  Truncate at τ_min = 10.
n_trials = 5
rejected = 0
for trial in range(n_trials):
    rng = np.random.default_rng(100 + trial)
    samp = np.ceil(rng.exponential(scale=50.0, size=20000)).astype(np.int64)
    fit = fit_power_law_mle(samp, tau_min=10.0, auto_tau_min=False)
    if fit.ks_pvalue < 0.05:
        rejected += 1
    print(f"  trial {trial}: α_hat={fit.alpha:.3f}  KS={fit.ks_stat:.4f}  "
          f"p={fit.ks_pvalue:.4e}  {'reject power-law' if fit.ks_pvalue<0.05 else 'fail to reject'}")
print(f"  → {rejected}/{n_trials} trials reject power-law at p<0.05")
assert rejected == n_trials, "FAIL: KS did not reject power-law on exponential dwells"
print("  PASS")
print()


# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test D — Fano factor on a Poisson process: F ≈ 1 across T")
print("=" * 72)
rng = np.random.default_rng(7)
total = int(SR * 4)                # 4 sec
rate = 50.0 / SR                   # 50 events/sec mean
# Poisson process via sampling inter-arrival times from Exp(rate).
gaps = rng.exponential(scale=1.0/rate, size=int(2.5 * rate * total))
events = np.cumsum(gaps).astype(np.int64)
events = events[events < total]
print(f"  generated {events.size} events over {total/SR:.1f}s "
      f"(rate ≈ {events.size/(total/SR):.1f}/s)")
T_ms = np.array([10, 25, 50, 100, 250, 500])
fano = fano_factor(events, total, (T_ms * SR * 0.001).astype(np.int64))
print(f"  {'T (ms)':>8}  {'mean_count':>10}  {'var_count':>9}  {'F':>5}")
for T, m, v, F in zip(T_ms, fano['mean_count'], fano['var_count'], fano['F']):
    print(f"  {T:8.1f}  {m:10.3f}  {v:9.3f}  {F:5.3f}")
F_mean = float(np.nanmean(fano['F']))
print(f"  mean F across T = {F_mean:.3f}   (expect ≈ 1.0)")
assert 0.85 < F_mean < 1.15, f"FAIL: Fano factor {F_mean:.3f} not near 1.0"
print("  PASS")
print()


# ──────────────────────────────────────────────────────────────────────────────
# Build a simple deterministic process to demonstrate sub-Poisson F.
print("=" * 72)
print("Test D2 — Fano factor on regular (deterministic) point process")
print("=" * 72)
events_reg = np.arange(0, total, int(SR / 50)).astype(np.int64)   # 50 Hz exactly
fano_reg = fano_factor(events_reg, total, (T_ms * SR * 0.001).astype(np.int64))
print(f"  generated {events_reg.size} events at exactly 50 Hz")
print(f"  {'T (ms)':>8}  {'mean':>8}  {'var':>8}  {'F':>5}")
for T, m, v, F in zip(T_ms, fano_reg['mean_count'], fano_reg['var_count'], fano_reg['F']):
    print(f"  {T:8.1f}  {m:8.3f}  {v:8.3f}  {F:5.3f}")
print("  (expect F ≈ 0 for windows containing an integer number of events;")
print("   small F when window is many events long — strongly sub-Poisson)")
F_reg_mean = float(np.nanmean(fano_reg['F']))
assert F_reg_mean < 0.5, f"FAIL: F={F_reg_mean:.3f} too high for regular process"
print("  PASS")
print()


# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test E — Phase-1 PLL bank output for FM(fc=220, fm=165, β=3)")
print("=" * 72)


def make_fm(fc, fm, beta, sr=SR, dur=4.0, amp=1.0):
    t = np.arange(int(sr * dur), dtype=np.float64) / sr
    return (amp * np.cos(2*np.pi*fc*t + beta*np.sin(2*np.pi*fm*t))).astype(np.float32)


fc = 220.0
pairs = farey_rationals(8)
f_plls = np.array([fc * p / q for p, q in pairs if 5.0 < fc * p / q < SR * 0.45],
                  dtype=np.float32)
sig = make_fm(220.0, 165.0, 3.0)
lock_map, _ = pll_bank_gpu(sig, f_plls, SR, PLLParams())
print(f"  bank: {f_plls.size} PLLs, {sig.size} samples")

report = analyze_lock_map(lock_map, SR, pll_freqs=f_plls,
                          fano_T_ms=np.array([5, 25, 100, 500]))
print()
print(f"  per-PLL summary (lock_frac > 0.5 only):")
print(f"  {'p:q':>6}  {'f_pll':>6}  {'lock_frac':>9}  {'n_evt':>5}  "
      f"{'mean_lock':>9}  {'mean_slip':>9}  {'F(5ms)':>7}  {'F(100ms)':>8}  {'slip-α':>7}")
for d, (p, q) in zip(report.per_pll, pairs):
    if d['lock_fraction'] < 0.5:
        continue
    mlock = d['mean_lock_ms']
    mslip = d['mean_slip_ms']
    F = d['fano']['F']
    sa = d['slip_powerlaw'].alpha if d['slip_powerlaw'].valid else float('nan')
    print(f"  {p}:{q:<3d}  {d['f_pll']:6.1f}  {d['lock_fraction']:9.4f}  "
          f"{d['n_events']:5d}  {mlock:9.3f}  {mslip:9.3f}  "
          f"{F[0]:7.3f}  {F[2]:8.3f}  {sa:7.3f}")
print()
print(f"  aggregate (unfolded, pooled) events: {report.aggregate_n_events}")
print()


# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test F — white noise sanity")
print("=" * 72)
rng = np.random.default_rng(0)
sig_n = (rng.standard_normal(int(SR * 4)) * 0.5).astype(np.float32)
lock_n, _ = pll_bank_gpu(sig_n, f_plls, SR, PLLParams())
report_n = analyze_lock_map(lock_n, SR, pll_freqs=f_plls,
                            fano_T_ms=np.array([5, 25, 100, 500]))
locked_plls = sum(1 for d in report_n.per_pll if d['lock_fraction'] > 0.05)
total_events = sum(d['n_events'] for d in report_n.per_pll)
print(f"  PLLs with lock_frac > 0.05: {locked_plls} / {len(report_n.per_pll)}")
print(f"  total lock events across bank: {total_events}")
print(f"  aggregate unfolded events: {report_n.aggregate_n_events}")
assert locked_plls == 0 and total_events == 0, (
    f"FAIL: noise should produce no locks; got {locked_plls} PLLs / {total_events} events")
print("  PASS — noise produces no locks (clean baseline)")
print()


print("=" * 72)
print("PHASE 2 INTERMITTENCY ACCEPTANCE TESTS PASSED")
print("=" * 72)
