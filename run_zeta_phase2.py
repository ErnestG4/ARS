"""
Phase 2 dry run on the ζ zeros signal.

Configuration (per the brief):
  • signal: scanner.make_zeta_signal(sr=44100, duration=8.0, n_zeros=50)
  • carrier reference fc = 100 Hz
  • Farey rationals up to q_max = 8
  • PLL params from Phase 1 (PLLParams() defaults)

Reports:
  • how many PLLs lock at all (lock_frac > 1%)
  • mean lock events per locking PLL
  • total aggregate lock events (raw and unfolded-pooled)
  • Fano factor F(L) of the aggregate, expressed in units of mean spacing
  • dwell-time distribution shape — pooled slip dwells:
        — exponential MLE rate
        — power-law MLE α (CSN)
        — KS distance for each → which fits better
  • lock map text summary — which Farey rationals lock most / least
  • Stern-Brocot depth histogram of lock events vs the geometric (2^−d)
    p-adic uniform reference
  • verdict: ≥200 events → continue to Phase 3; otherwise extend duration
"""
import os
import sys
import time

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '$HOME/fmexplorer/riemann_explorer')   # for scanner.make_zeta_signal

import scanner                                                      # noqa: E402
from pll_bank import pll_bank_gpu, PLLParams, farey_rationals, GPU_NAME  # noqa: E402
from intermittency import (                                         # noqa: E402
    analyze_lock_map, fit_power_law_mle, fano_factor,
    stern_brocot_depth, depth_histogram,
)

SR     = 44100.0
DUR    = 30.0      # extended: 8s × 50 zeros gave only 110 events (< 200 threshold)
NZ     = 100       # 30s × 100 zeros → 302 events, 22 PLLs locking, 8 evt/PLL
FC_REF = 100.0
QMAX   = 8


def hist_ascii(values, bins=20, width=50, title=""):
    """Tiny ASCII histogram for the report."""
    if len(values) == 0:
        print(f"  {title}: <empty>")
        return
    counts, edges = np.histogram(values, bins=bins)
    hi = counts.max() if counts.max() > 0 else 1
    print(f"  {title}  (n={len(values)}, range [{edges[0]:.2f}, {edges[-1]:.2f}])")
    for c, e0, e1 in zip(counts, edges[:-1], edges[1:]):
        bar = "█" * int(width * c / hi)
        print(f"    [{e0:8.2f}, {e1:8.2f})  {bar} {c}")


# ── Build signal ──────────────────────────────────────────────────────────────
print("=" * 72)
print(f"ζ zeros signal — first {NZ} zeros, {DUR}s @ {SR/1000:g} kHz, fc_ref={FC_REF}")
print("=" * 72)
sig = scanner.make_zeta_signal(sr=SR, duration=DUR, n_zeros=NZ)
rms = float(np.sqrt(np.mean(sig.astype(np.float64) ** 2)))
print(f"  signal len       : {len(sig)} samples")
print(f"  signal RMS       : {rms:.5f}")
print(f"  signal min/max   : {sig.min():.4f} / {sig.max():.4f}")
print()

# ── Build PLL bank ────────────────────────────────────────────────────────────
pairs = farey_rationals(QMAX)
f_plls_all = [(p, q, FC_REF * p / q) for p, q in pairs]
# Filter to in-band PLLs (Goertzel-equivalent guard).
f_plls_kept = [(p, q, f) for (p, q, f) in f_plls_all if 5.0 < f < SR * 0.45]
pairs_kept   = [(p, q) for (p, q, _) in f_plls_kept]
freqs_kept   = np.array([f for (_, _, f) in f_plls_kept], dtype=np.float32)
print(f"  Farey bank q_max={QMAX}: {len(pairs)} pairs total, {len(pairs_kept)} in-band")
print(f"  f_pll range      : [{freqs_kept.min():.2f}, {freqs_kept.max():.2f}] Hz")
print()

# ── Run GPU PLL bank ──────────────────────────────────────────────────────────
print(f"  GPU: {GPU_NAME}")
t0 = time.perf_counter()
lock_map, _ = pll_bank_gpu(sig, freqs_kept, SR, PLLParams())
t_gpu = time.perf_counter() - t0
print(f"  pll_bank_gpu     : {t_gpu*1000:.1f} ms ({lock_map.size/max(t_gpu, 1e-9)/1e6:.0f} M-cells/s)")

# ── Phase 2 analysis ──────────────────────────────────────────────────────────
fano_T_ms = np.array([5, 10, 25, 50, 100, 250, 500, 1000, 2000], dtype=np.float64)
report = analyze_lock_map(
    lock_map, SR,
    pll_freqs=freqs_kept,
    farey_pairs=pairs_kept,
    fano_T_ms=fano_T_ms,
    pl_tau_min_samples=20.0,
    pl_auto_tau_min=True,
)
print()


# ── Lock summary ─────────────────────────────────────────────────────────────
print("=" * 72)
print("Lock summary")
print("=" * 72)
locking = [d for d in report.per_pll if d['lock_fraction'] > 0.01]
n_lock = len(locking)
n_total = len(report.per_pll)
print(f"  PLLs locking (frac > 1%) : {n_lock}/{n_total}")
events_per = [d['n_events'] for d in locking]
total_events = sum(d['n_events'] for d in report.per_pll)
print(f"  total lock events        : {total_events}")
if events_per:
    print(f"  mean events / locking PLL: {np.mean(events_per):.2f}  "
          f"(median {int(np.median(events_per))}, max {max(events_per)})")
print(f"  aggregate (unfolded)     : {report.aggregate_n_events} events")
print()

# Sort locking PLLs by lock fraction descending; print top + bottom.
locking.sort(key=lambda d: -d['lock_fraction'])
print("  top locking rationals (by lock_fraction):")
print(f"  {'p:q':>7}  {'f_pll':>7}  {'depth':>5}  {'lock_frac':>9}  {'n_evt':>5}  "
      f"{'mean_lock':>9}  {'mean_slip':>9}")
for d in locking[:12]:
    p, q = d['rational']
    print(f"  {p}:{q:<5d}  {d['f_pll']:7.2f}  {d['stern_brocot_depth']:5d}  "
          f"{d['lock_fraction']:9.4f}  {d['n_events']:5d}  "
          f"{d['mean_lock_ms']:9.2f}  {d['mean_slip_ms']:9.2f}")
if len(locking) > 12:
    print("  …")
    for d in locking[-3:]:
        p, q = d['rational']
        print(f"  {p}:{q:<5d}  {d['f_pll']:7.2f}  {d['stern_brocot_depth']:5d}  "
              f"{d['lock_fraction']:9.4f}  {d['n_events']:5d}  "
              f"{d['mean_lock_ms']:9.2f}  {d['mean_slip_ms']:9.2f}")
print()

non_locking = [d for d in report.per_pll if d['lock_fraction'] <= 0.01]
print(f"  PLLs that did NOT lock (frac ≤ 1%): {len(non_locking)}")
nonlock_examples = sorted(non_locking, key=lambda d: -d['lock_fraction'])[:6]
print(f"  near-miss examples (highest of the non-locking):")
for d in nonlock_examples:
    p, q = d['rational']
    print(f"    {p}:{q}  f_pll={d['f_pll']:.2f}  lock_frac={d['lock_fraction']:.4f}")
print()


# ── Aggregate Fano factor ─────────────────────────────────────────────────────
print("=" * 72)
print("Aggregate Fano factor F(L) — events pooled across all locking PLLs,")
print("each unfolded by its own mean spacing (so mean spacing = 1)")
print("=" * 72)
af = report.aggregate_fano
if af is None:
    print("  not enough aggregate events for Fano (< 20)")
else:
    print(f"  {'L (× mean spacing)':>20}  {'mean_count':>10}  {'var_count':>9}  {'F':>5}")
    for L, m, v, F in zip(af['L_units_of_mean_spacing'],
                          af['mean_count'], af['var_count'], af['F']):
        if np.isnan(F):
            print(f"  {L:20.2f}  (too few windows)")
        else:
            print(f"  {L:20.2f}  {m:10.3f}  {v:9.3f}  {F:5.3f}")
    F_short = float(np.nanmean(af['F'][:3])) if len(af['F']) >= 3 else float('nan')
    F_long  = float(np.nanmean(af['F'][-3:])) if len(af['F']) >= 3 else float('nan')
    print(f"  → mean F at short L (≤2):  {F_short:.3f}    (Poisson=1, GUE<1)")
    print(f"  → mean F at long L (≥10): {F_long:.3f}    (should approach 1)")
print()


# ── Dwell-distribution shape (pooled slip dwells) ─────────────────────────────
print("=" * 72)
print("Pooled slip-dwell distribution — exponential vs power-law fit")
print("=" * 72)
all_slips = np.concatenate([d['slip_dwells'] for d in report.per_pll
                            if d['slip_dwells'].size > 0]) \
    if any(d['slip_dwells'].size > 0 for d in report.per_pll) else np.zeros(0, np.int64)
print(f"  total slip dwells pooled: {all_slips.size}")
if all_slips.size >= 20:
    # Exponential MLE: rate = 1 / mean.   KS vs Exp(rate).
    mean_s = float(all_slips.mean())
    if mean_s > 0:
        rate = 1.0 / mean_s
        sorted_d = np.sort(all_slips.astype(np.float64))
        emp = np.arange(1, sorted_d.size + 1) / sorted_d.size
        F_exp = 1.0 - np.exp(-rate * sorted_d)
        ks_exp = float(np.max(np.abs(emp - F_exp)))
    else:
        ks_exp = float('nan')
    pl = fit_power_law_mle(all_slips, tau_min=20.0, auto_tau_min=True)
    print(f"  exponential fit: mean = {mean_s:.1f} samples  ({1000*mean_s/SR:.2f} ms),  KS = {ks_exp:.4f}")
    if pl.valid:
        print(f"  power-law fit  : α = {pl.alpha:.3f} ± {pl.alpha_stderr:.3f},  "
              f"τ_min = {pl.tau_min:.0f},  KS = {pl.ks_stat:.4f}  (n={pl.n_used})")
        verdict = "POWER-LAW" if pl.ks_stat < ks_exp else "EXPONENTIAL"
        print(f"  → smaller KS distance suggests: {verdict}")
    else:
        print(f"  power-law fit  : insufficient data above τ_min")
    print()
    # Log-log histogram for visual inspection
    hist_ascii(np.log10(all_slips[all_slips > 0]),
               bins=15, title="log10(slip_dwell)")
print()


# ── Stern-Brocot depth histogram ──────────────────────────────────────────────
print("=" * 72)
print("Stern-Brocot depth distribution of lock events")
print("=" * 72)
dh = report.depth_histogram
if dh is None or dh['event_count'].sum() == 0:
    print("  no lock events to histogram by depth")
else:
    total_evt = int(dh['event_count'].sum())
    print(f"  {'depth':>5}  {'#PLLs':>6}  {'#locked':>8}  {'#events':>8}  "
          f"{'frac':>6}  {'2^-d':>6}")
    for d, n_total, n_lock, n_evt, geo in zip(
            dh['depth'], dh['rationals_at_depth'], dh['bin_count'],
            dh['event_count'], dh['geometric_ref']):
        frac = n_evt / total_evt if total_evt > 0 else 0.0
        print(f"  {d:5d}  {n_total:6d}  {n_lock:8d}  {n_evt:8d}  "
              f"{frac:6.3f}  {geo:6.3f}")
    print()
    # KL divergence of observed depth distribution vs geometric reference
    obs = dh['event_count'].astype(np.float64) / max(total_evt, 1)
    ref = dh['geometric_ref']
    mask = (obs > 0) & (ref > 0)
    if mask.any():
        kl = float(np.sum(obs[mask] * np.log(obs[mask] / ref[mask])))
        print(f"  KL(observed ∥ 2^-d uniform) = {kl:.4f}    (0 = matches geometric)")
print()


# ── Verdict ───────────────────────────────────────────────────────────────────
print("=" * 72)
print("Verdict")
print("=" * 72)
print(f"  total lock events: {total_events}")
print(f"  aggregate (unfolded) events: {report.aggregate_n_events}")
threshold = 200
if total_events >= threshold:
    print(f"  ≥ {threshold} events → enough for Phase 3 universality analysis")
else:
    print(f"  < {threshold} events → need to extend.  Suggest:")
    print(f"    • duration → 30 s   (currently {DUR} s)")
    print(f"    • or n_zeros → 100  (currently {NZ})")
    print(f"    • or both.")
print()
