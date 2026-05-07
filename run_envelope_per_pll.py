"""
Per-PLL envelope diagnosis — same front-end as the PLL, but only the
amplitude part (skip phase tracking).  Compute |I_lp+jQ_lp|² at every
Farey ratio in the q_max=8 bank, count above-floor peaks, and identify
which PLLs (and at what t-band) the GUE/GOE chirps differ from ζ.

This pinpoints the actual mechanism behind the 4-vs-28 qualifying-PLL gap.
"""
import os, sys, time
import numpy as np
from scipy.signal import lfilter

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from pll_bank import farey_rationals
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


SR        = 44100.0
FC_REF    = 115.55
Q_MAX     = 8
BW_FRAC   = 0.05
POWER_FLOOR_FRAC = 0.03
PLOT_DIR  = os.path.join(THIS_DIR, "plots")
SIG_DIR   = os.path.join(THIS_DIR, "signals_cache")

# Lock-confirm window — same as PLL (20 ms)
N_LOCK_SAMPLES = int(round(SR * 20e-3))


def narrowband_power(sig, fc, sr, bw_frac=BW_FRAC):
    n = np.arange(len(sig), dtype=np.float64)
    omega = 2.0 * np.pi * fc / sr
    cos_n = np.cos(omega * n)
    sin_n = np.sin(omega * n)
    I = sig.astype(np.float64) * cos_n
    Q = -sig.astype(np.float64) * sin_n
    fc_lp = max(fc * bw_frac, 1.0)
    alpha = 1.0 - np.exp(-2.0 * np.pi * fc_lp / sr)
    b = [alpha]; a = [1.0, -(1.0 - alpha)]
    I_lp = lfilter(b, a, I)
    Q_lp = lfilter(b, a, Q)
    return I_lp * I_lp + Q_lp * Q_lp


def above_run_stats(p, threshold):
    """Counts of above-runs and below-runs and their durations.  Filtered
    to runs ≥ N_LOCK_SAMPLES — only those would actually trigger the PLL."""
    above = p >= threshold
    if above.size == 0: return 0, 0, 0.0, 0.0
    d = np.diff(above.astype(np.int8))
    boundaries = np.concatenate([[0], np.where(d != 0)[0] + 1, [above.size]])
    runs = np.diff(boundaries)
    states = above[boundaries[:-1]].astype(bool)
    above_runs = runs[states]
    below_runs = runs[~states]
    # PLL lock-confirm filter: only runs ≥ 20 ms count as triggers
    pll_triggers = int((above_runs >= N_LOCK_SAMPLES).sum())
    return (int(above_runs.size), int(below_runs.size),
            float(above_runs.mean() * 1000.0 / SR) if above_runs.size else 0.0,
            float(above.mean()),
            pll_triggers)


# ── Build the bank of frequencies the PLL bank used ───────────────────────────
pairs = farey_rationals(Q_MAX)
freqs_pq = []
for p, q in pairs:
    f = FC_REF * p / q
    if 5.0 < f < SR * 0.45:
        freqs_pq.append((f, p, q))
freqs_pq.sort()
print(f"Bank: {len(freqs_pq)} PLLs spanning {freqs_pq[0][0]:.2f}–{freqs_pq[-1][0]:.2f} Hz")
print()


# ── Load signals ──────────────────────────────────────────────────────────────
signals = {}
for name, fname in [('ζ', 'zeta_N1000_dur300.npy'),
                     ('GUE', 'gue1000_N1000_dur300.npy'),
                     ('GOE', 'goe1000_N1000_dur300.npy')]:
    s = np.load(os.path.join(SIG_DIR, fname))
    rms2 = float(np.mean(s.astype(np.float64) ** 2))
    signals[name] = (s, rms2, POWER_FLOOR_FRAC * rms2)
    print(f"  {name:4s}: RMS²={rms2:.4e}, floor={POWER_FLOOR_FRAC*rms2:.4e}")
print()


# ── Sweep frequencies, collect per-PLL above-floor stats ──────────────────────
# Memory-conscious: process one frequency at a time per signal.
print("=" * 92)
print("Per-frequency above-floor analysis (lock-confirm filter applied: runs must be ≥ 20 ms)")
print("=" * 92)
print(f"  {'p:q':>6}  {'fc':>7}  {'ζ #peaks':>8}  {'ζ #PLL':>7}  "
      f"{'GUE #peaks':>10}  {'GUE #PLL':>9}  {'GOE #peaks':>10}  {'GOE #PLL':>9}")
results = []
for f_pll, p, q in freqs_pq:
    row = {'p': p, 'q': q, 'f_pll': f_pll}
    for name, (sig, rms2, floor) in signals.items():
        p_env = narrowband_power(sig, f_pll, SR)
        n_above_runs, _, mean_above_ms, frac_above, n_triggers = above_run_stats(p_env, floor)
        row[f'{name}_n_above'] = n_above_runs
        row[f'{name}_n_triggers'] = n_triggers
        row[f'{name}_mean_above_ms'] = mean_above_ms
        row[f'{name}_frac_above'] = frac_above
    results.append(row)
    print(f"  {p}:{q:<3d}  {f_pll:7.2f}  "
          f"{row['ζ_n_above']:8d}  {row['ζ_n_triggers']:7d}  "
          f"{row['GUE_n_above']:10d}  {row['GUE_n_triggers']:9d}  "
          f"{row['GOE_n_above']:10d}  {row['GOE_n_triggers']:9d}")
print()


# ── Aggregate ────────────────────────────────────────────────────────────────
print("=" * 92)
print("Bank totals — runs above floor (raw) and ≥20-ms-confirmed triggers")
print("=" * 92)
for name in ['ζ', 'GUE', 'GOE']:
    total_runs = sum(r[f'{name}_n_above'] for r in results)
    total_trig = sum(r[f'{name}_n_triggers'] for r in results)
    plls_with_10p = sum(1 for r in results if r[f'{name}_n_triggers'] >= 10)
    print(f"  {name}: total above-floor runs = {total_runs:6d}, "
          f"≥20-ms triggers = {total_trig:6d}, "
          f"PLLs with ≥10 triggers = {plls_with_10p}")
print()


# ── Plot per-PLL counts ───────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 4.5))
xs = [f'{r["p"]}:{r["q"]}' for r in results]
x_pos = np.arange(len(xs))
w = 0.27
ax.bar(x_pos - w, [r['ζ_n_triggers'] for r in results],   w, label='ζ',   color='C0')
ax.bar(x_pos,     [r['GUE_n_triggers'] for r in results], w, label='GUE', color='C1')
ax.bar(x_pos + w, [r['GOE_n_triggers'] for r in results], w, label='GOE', color='C2')
ax.axhline(10, color='red', ls='--', lw=1.0, label='qualifying threshold (10)')
ax.set_xticks(x_pos)
ax.set_xticklabels(xs, rotation=90, fontsize=7)
ax.set_ylabel('# above-floor runs ≥ 20 ms')
ax.set_xlabel('PLL p:q')
ax.set_title(f"Per-PLL above-floor trigger count — fc_ref={FC_REF}, "
              f"floor=0.03·RMS², lock_confirm=20 ms")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis='y')
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "13_envelope_per_pll.png"), dpi=110)
plt.close(fig)
print(f"  → plots/13_envelope_per_pll.png")
