"""
Why do the GUE/GOE chirps saturate the PLL while ζ doesn't?

Apply the SAME quadrature-mix-and-LP front-end the PLL uses, then look at
the narrowband instantaneous power |I_lp(t) + j Q_lp(t)|² across the 300 s
recording.  Compare to the PLL's power_floor = 0.03 · signal_RMS².

If the GUE/GOE chirps sit ABOVE the floor most of the time → continuous-
lock saturation (the PLL is locked nearly always, only counting brief slip
events).  If ζ sits below the floor most of the time, popping above only at
sharp peaks → discrete-event regime, which is what gives clean lock onsets.

This tells us which fix to take next:
    1.  Sustained-amplitude story  → raise power floor or use peak-detector
    2.  Different envelope shape   → modify chirp synthesis directly
"""
import os, sys, time
import numpy as np
from scipy.signal import lfilter

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '$HOME/fmexplorer/riemann_explorer')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


SR        = 44100.0
FC_REF    = 115.55
BW_FRAC   = 0.05
POWER_FLOOR_FRAC = 0.03    # PLLParams default
PLOT_DIR  = os.path.join(THIS_DIR, "plots")
SIG_DIR   = os.path.join(THIS_DIR, "signals_cache")


def narrowband_power(sig, fc, sr, bw_frac=BW_FRAC):
    """Quadrature mix at fc, 1-pole IIR LP at fc*bw_frac, return |I_lp+jQ_lp|²."""
    n = np.arange(len(sig), dtype=np.float64)
    omega = 2.0 * np.pi * fc / sr
    cos_n = np.cos(omega * n)
    sin_n = np.sin(omega * n)
    I = sig.astype(np.float64) * cos_n
    Q = -sig.astype(np.float64) * sin_n
    # IIR LP: y[k] = (1-α)y[k-1] + α x[k]   →  b = [α], a = [1, -(1-α)]
    fc_lp = max(fc * bw_frac, 1.0)
    alpha = 1.0 - np.exp(-2.0 * np.pi * fc_lp / sr)
    b = [alpha]
    a = [1.0, -(1.0 - alpha)]
    I_lp = lfilter(b, a, I)
    Q_lp = lfilter(b, a, Q)
    return I_lp * I_lp + Q_lp * Q_lp


def load_signal(name):
    path = os.path.join(SIG_DIR, name)
    return np.load(path)


def above_threshold_runs(power, threshold, min_run_samples=1):
    """Return (lengths_above, lengths_below) — durations of above/below intervals."""
    above = power >= threshold
    if above.size == 0:
        return np.zeros(0, int), np.zeros(0, int)
    d = np.diff(above.astype(np.int8))
    boundaries = np.concatenate([[0], np.where(d != 0)[0] + 1, [above.size]])
    runs = np.diff(boundaries)
    states = above[boundaries[:-1]].astype(bool)
    return runs[states], runs[~states]


# ── Load signals ──────────────────────────────────────────────────────────────
print("Loading cached chirps …")
sig_zeta = load_signal("zeta_N1000_dur300.npy")
sig_gue  = load_signal("gue1000_N1000_dur300.npy")
sig_goe  = load_signal("goe1000_N1000_dur300.npy")

for name, s in [('ζ', sig_zeta), ('GUE', sig_gue), ('GOE', sig_goe)]:
    rms = float(np.sqrt(np.mean(s.astype(np.float64) ** 2)))
    print(f"  {name:4s}: len={len(s)}, RMS={rms:.5e}")
print()


# ── Compute narrowband envelopes ──────────────────────────────────────────────
print(f"Computing narrowband power at fc={FC_REF} (BW={BW_FRAC*FC_REF:.2f} Hz)…")
envelopes = {}
power_floors = {}
for name, sig in [('ζ', sig_zeta), ('GUE', sig_gue), ('GOE', sig_goe)]:
    t0 = time.perf_counter()
    p = narrowband_power(sig, FC_REF, SR)
    rms2 = float(np.mean(sig.astype(np.float64) ** 2))
    floor = POWER_FLOOR_FRAC * rms2
    envelopes[name] = p
    power_floors[name] = floor
    print(f"  {name}: env mean={p.mean():.4e}, median={np.median(p):.4e}, "
          f"max={p.max():.4e}, floor={floor:.4e}, computed in {time.perf_counter()-t0:.1f}s")
print()


# ── Statistics vs PLL power_floor ─────────────────────────────────────────────
print("=" * 80)
print(f"Narrowband-power statistics relative to PLL power_floor = {POWER_FLOOR_FRAC} × RMS²")
print("=" * 80)
print(f"  {'signal':<6}  {'mean/floor':>10}  {'med/floor':>9}  {'max/floor':>9}  "
      f"{'%above':>7}  {'P95/floor':>10}  {'P99/floor':>10}")
for name in ['ζ', 'GUE', 'GOE']:
    p = envelopes[name]; floor = power_floors[name]
    above_frac = float((p >= floor).mean())
    p95 = float(np.percentile(p, 95))
    p99 = float(np.percentile(p, 99))
    print(f"  {name:<6}  {p.mean()/floor:10.3f}  {np.median(p)/floor:9.3f}  "
          f"{p.max()/floor:9.3f}  {above_frac*100:6.2f}%  "
          f"{p95/floor:10.3f}  {p99/floor:10.3f}")
print()


# ── Above/below threshold dwell distributions ─────────────────────────────────
print("=" * 80)
print("Run-length statistics for above-floor / below-floor intervals (in ms)")
print("=" * 80)
print(f"  {'signal':<6}  {'#above':>6}  {'mean_above_ms':>13}  {'median_above_ms':>15}  "
      f"{'#below':>6}  {'mean_below_ms':>13}  {'median_below_ms':>15}")
for name in ['ζ', 'GUE', 'GOE']:
    p = envelopes[name]; floor = power_floors[name]
    above, below = above_threshold_runs(p, floor)
    if above.size > 0:
        ma = above.mean() * 1000.0 / SR
        med_a = np.median(above) * 1000.0 / SR
    else:
        ma = med_a = float('nan')
    if below.size > 0:
        mb = below.mean() * 1000.0 / SR
        med_b = np.median(below) * 1000.0 / SR
    else:
        mb = med_b = float('nan')
    print(f"  {name:<6}  {above.size:6d}  {ma:13.2f}  {med_a:15.2f}  "
          f"{below.size:6d}  {mb:13.2f}  {med_b:15.2f}")
print()


# ── Plot envelopes ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(13, 8), sharex=True)
T_total = len(sig_zeta) / SR
N_plot = 6000
ds = max(1, len(sig_zeta) // N_plot)
t_axis = np.arange(0, len(sig_zeta), ds) / SR

for ax, name in zip(axes, ['ζ', 'GUE', 'GOE']):
    p = envelopes[name][::ds]
    floor = power_floors[name]
    ax.semilogy(t_axis, p, color='C0', lw=0.6, alpha=0.85, label='|I_lp+jQ_lp|²')
    ax.axhline(floor, color='red', ls='--', lw=1.0, label=f'power_floor = 0.03·RMS² = {floor:.2e}')
    ax.axhline(np.median(envelopes[name]), color='gray', ls=':', lw=0.8, label='median')
    ax.set_ylabel(f'{name}\nnarrowband power')
    ax.legend(loc='upper right', fontsize=7)
    ax.grid(True, alpha=0.3, which='both')
axes[-1].set_xlabel('time (s)')
fig.suptitle(f"Narrowband power at fc={FC_REF} Hz over 300 s "
              f"— ζ vs density-matched GUE / GOE chirps")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOT_DIR, "11_envelope_timeseries.png"), dpi=110)
plt.close(fig)
print(f"  → plots/11_envelope_timeseries.png")


# Power distribution histogram (log-x)
fig, ax = plt.subplots(figsize=(11, 4.5))
for name, color in [('ζ', 'C0'), ('GUE', 'C1'), ('GOE', 'C2')]:
    p = envelopes[name]
    floor = power_floors[name]
    p_norm = p / floor
    p_norm = p_norm[p_norm > 1e-10]   # drop very-near-zero values for log axis
    ax.hist(np.log10(p_norm), bins=200, alpha=0.45, density=True,
            label=f"{name} (frac>floor = {(p>=floor).mean():.3f})", color=color)
ax.axvline(0.0, color='red', ls='--', lw=1.0, label='power = floor')
ax.set_xlabel("log10(narrowband_power / power_floor)")
ax.set_ylabel("density")
ax.set_title("Distribution of narrowband power, normalised to PLL power_floor")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "12_envelope_histogram.png"), dpi=110)
plt.close(fig)
print(f"  → plots/12_envelope_histogram.png")


# ── Verdict ───────────────────────────────────────────────────────────────────
print()
print("=" * 80)
print("Diagnosis")
print("=" * 80)
zeta_above = float((envelopes['ζ'] >= power_floors['ζ']).mean())
gue_above  = float((envelopes['GUE'] >= power_floors['GUE']).mean())
goe_above  = float((envelopes['GOE'] >= power_floors['GOE']).mean())
print(f"  fraction of time above power_floor:")
print(f"    ζ   = {zeta_above*100:5.2f}%")
print(f"    GUE = {gue_above*100:5.2f}%")
print(f"    GOE = {goe_above*100:5.2f}%")
print()

if gue_above > 0.5 and zeta_above < 0.15:
    print("  → DIAGNOSIS CONFIRMED: GUE/GOE chirps sit above the PLL's power_floor")
    print(f"    {gue_above:.0%} of the time vs ζ at {zeta_above:.0%} — continuous-lock regime.")
    print(f"    The detector is saturated for the random-matrix chirps; the few events")
    print(f"    we see are slip-recovery transitions, not zero-passage events.")
    print()
    print(f"  Two fixes available:")
    print(f"    A.  Raise PLL power_floor_frac from 0.03 to ~{POWER_FLOOR_FRAC * gue_above / zeta_above * 0.5:.3f}")
    print(f"        so that GUE chirp drops below the floor most of the time too.")
    print(f"        This recreates ζ's 'sparse peaks above floor' regime for the calibration.")
    print(f"    B.  Replace lock-onset detection with peak detection: count upward")
    print(f"        crossings of the envelope through some threshold instead of PLL")
    print(f"        lock state.  Robust to continuous-lock saturation by construction.")
elif zeta_above > 0.5:
    print("  → ζ also runs hot — surprising; reconsider PLL config.")
else:
    print("  → No clear separation; revisit hypotheses.")
