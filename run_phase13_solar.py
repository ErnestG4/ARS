"""
Phase 13 — Solar flare catalog analysis.

Apply arithmetic_toolkit.full_analysis to the GOES X-ray flare catalog
(Plutino 2024, 1986-04-04 → 2023-04-30, 358,885 flares).  The point
process is `tstart` converted to seconds-since-first-event.

Six stratifications:
  - all_flares             (n ≈ 359k)
  - C_and_above            (cat ∈ {C, M, X})
  - M_and_above            (cat ∈ {M, X})
  - X_only                 (cat == X)
  - solar_max              (years near cycle peak)
  - solar_min              (years near cycle trough)

Then a targeted Ramanujan-Fourier resonance scan on M+X intervals to
compare with Planat's 2009 amplitude-spectrum result on the same dataset
(or its predecessor): Planat used f(n) = Δt_n through the RF transform
and identified dominant resonance orders.  Our toolkit reproduces that
formulation when invoked with ``ramanujan_fourier(t_k, normalize=True)``,
which internally takes np.diff and unit-mean-normalises before the RF
transform.

Output:
    data/solar_flare_results.json
    plots/40_solar_flares.png
"""
import os, sys, json, time
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import full_analysis, ramanujan_fourier, fano_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
CSV = os.path.join(DATA, "solar_flares_plutino_1986_2023.csv")

print(f"Loading {CSV} …")
t0 = time.time()
df = pd.read_csv(CSV)
df['tstart'] = pd.to_datetime(df['tstart'], errors='coerce')
df = df.dropna(subset=['tstart']).sort_values('tstart').reset_index(drop=True)
t_origin = df['tstart'].iloc[0]
df['t_sec'] = (df['tstart'] - t_origin).dt.total_seconds()
df['year'] = df['tstart'].dt.year
print(f"  loaded {len(df):,} flares spanning "
      f"{df['tstart'].min()} → {df['tstart'].max()}  "
      f"({(df['tstart'].max() - df['tstart'].min()).days / 365.25:.2f} yr)  "
      f"⏱ {time.time() - t0:.1f}s\n")

# ─── Six stratifications ──────────────────────────────────────────────────────

YEARS_MAX = {1989, 1990, 1991,
             2000, 2001, 2002,
             2011, 2012, 2013,
             2022, 2023}
YEARS_MIN = {1986, 1987,
             1996, 1997,
             2007, 2008, 2009,
             2019, 2020}

strata = {
    'all_flares':     df,
    'C_and_above':    df[df['cat'].isin(['C', 'M', 'X'])],
    'M_and_above':    df[df['cat'].isin(['M', 'X'])],
    'X_only':         df[df['cat'] == 'X'],
    'solar_max':      df[df['year'].isin(YEARS_MAX)],
    'solar_min':      df[df['year'].isin(YEARS_MIN)],
}

print("=" * 130)
print("Phase 13 — solar-flare fingerprint matrix")
print("=" * 130)
print(f"  {'stratum':<14}  {'n':>7}  {'best':<7}  "
      f"{'KS_GUE':>7}  {'KS_GOE':>7}  {'KS_P':>7}  "
      f"{'mass<.3':>7}  {'F(T=1)':>7}  {'F(T=5)':>7}  "
      f"{'rep_int':>7}  {'top_q':>7}  {'mean_dt':>10}")
print("  " + "-" * 128)

results = {}
for name, sub in strata.items():
    t_k = sub['t_sec'].to_numpy()
    if t_k.size < 50:
        print(f"  {name:<14}  {t_k.size:>7}  insufficient")
        results[name] = dict(label=name, n_events=int(t_k.size),
                              error='insufficient')
        continue
    res = full_analysis(t_k, label=name, q_max=8, ramanujan_q_max=200)
    results[name] = res
    p = res['primary_nns']; pc = res['pair_correlation']; fan = res['fano_curve']
    fp = res['fingerprint_vector']
    mean_dt = float(np.diff(t_k).mean()) if t_k.size > 1 else float('nan')
    print(f"  {name:<14}  {res['n_events']:>7}  {p['best']:<7}  "
          f"{p['ks_u']:>7.3f}  {p['ks_o']:>7.3f}  {p['ks_p']:>7.3f}  "
          f"{p['mass03']:>7.3f}  "
          f"{fan.get('F_at_1', float('nan')):>7.3f}  "
          f"{fan.get('F_at_5', float('nan')):>7.3f}  "
          f"{pc.get('repulsion_integral', 0):>7.3f}  "
          f"{int(fp[7]):>7d}  {mean_dt/3600:>8.2f} h")


# ─── Ramanujan-Fourier resonance scan on M+X (Planat-style) ──────────────────

print("\n" + "=" * 110)
print("Ramanujan-Fourier resonance scan on M+X inter-flare intervals "
      "(Planat 2009 comparison)")
print("=" * 110)

mx_t = strata['M_and_above']['t_sec'].to_numpy()
mx_intervals_sec = np.diff(mx_t)
mx_intervals_days = mx_intervals_sec / 86400.0
print(f"  M+X events: n = {mx_t.size:,}, intervals: n = {mx_intervals_sec.size:,}")
print(f"  inter-flare interval stats:  mean = {mx_intervals_days.mean():.3f} d, "
      f"median = {np.median(mx_intervals_days):.3f} d, "
      f"std = {mx_intervals_days.std():.3f} d")

# Planat formulation: RF on f(n) = unit-mean-normalised intervals (normalize=True)
rf_planat = ramanujan_fourier(mx_t, q_max=200, normalize=True)
print(f"\n  RF mode = {rf_planat.get('mode')} (Planat 2009 formulation)")
print(f"  Top 10 resonance orders by |a_q|:")
for q, amp in zip(rf_planat['top10_q'], rf_planat['top10_amplitudes']):
    print(f"    q = {q:>3}   |a_q| = {amp:.4f}")
print(f"  peak_q = {rf_planat['peak_q']}")

# Indicator-function variant — period detection on event-count grid
rf_indicator = ramanujan_fourier(mx_t, q_max=200, normalize=False,
                                   n_bins=int(mx_t[-1] / 86400) + 1)
print(f"\n  RF mode = {rf_indicator.get('mode')} (indicator function on day grid)")
print(f"  Top 10 q values by |a_q|:  {rf_indicator['top10_q']}")
print(f"  peak_q = {rf_indicator['peak_q']}  "
      f"(units: 1 q ≈ 1 day, so q = 27 ≈ Carrington rotation, q ≈ 365 → year, etc.)")


# ─── Solar-cycle Fano comparison on M+X subsets ──────────────────────────────

print("\n" + "=" * 110)
print("Fano F(T) curve: solar_max(M+X)  vs  solar_min(M+X)")
print("=" * 110)

mx_max = df[df['cat'].isin(['M', 'X']) & df['year'].isin(YEARS_MAX)]['t_sec'].to_numpy()
mx_min = df[df['cat'].isin(['M', 'X']) & df['year'].isin(YEARS_MIN)]['t_sec'].to_numpy()
print(f"  solar_max M+X:  n = {mx_max.size:,}")
print(f"  solar_min M+X:  n = {mx_min.size:,}")

fano_max = fano_curve(mx_max, n_scales=30) if mx_max.size >= 50 else None
fano_min = fano_curve(mx_min, n_scales=30) if mx_min.size >= 50 else None
nns_max = full_analysis(mx_max, label='solar_max M+X', q_max=8) if mx_max.size >= 50 else None
nns_min = full_analysis(mx_min, label='solar_min M+X', q_max=8) if mx_min.size >= 50 else None

if fano_max and fano_min:
    print(f"\n  {'window':<14}  {'best':<7}  {'KS_GUE':>7}  {'mass<.3':>7}  "
          f"{'F(T=1)':>7}  {'F(T=5)':>7}  {'F(T=20)':>7}")
    for label, fan, full in [('solar_max', fano_max, nns_max), ('solar_min', fano_min, nns_min)]:
        p = full['primary_nns']
        print(f"  {label:<14}  {p['best']:<7}  {p['ks_u']:>7.3f}  {p['mass03']:>7.3f}  "
              f"{fan['F_at_1']:>7.3f}  {fan['F_at_5']:>7.3f}  {fan['F_at_20']:>7.3f}")


# ─── Save JSON ────────────────────────────────────────────────────────────────

def _trim(res):
    if 'error' in res: return res
    return dict(label=res['label'], n_events=res['n_events'],
                primary_nns=res['primary_nns'],
                fingerprint_vector=res['fingerprint_vector'],
                fano_summary={k: res['fano_curve'].get(k)
                               for k in ('F_at_1', 'F_at_5', 'F_at_20',
                                         'mean_sp', 'duration')},
                ramanujan_summary={k: res['ramanujan'].get(k)
                                    for k in ('peak_q', 'top10_q',
                                              'top10_amplitudes', 'mode')},
                pair_correlation_summary={k: res['pair_correlation'].get(k)
                                           for k in ('R2_at_0_1', 'R2_at_0_5',
                                                     'R2_at_1', 'repulsion_integral')},
                sb_split_summary=res['sb_split'],
                padic_summary=dict(dominant_prime=res['padic_profile']['dominant_prime'],
                                    best_by_prime=res['padic_profile']['best_by_prime']))

out = dict(strata={k: _trim(v) for k, v in results.items()},
           rf_planat={'top10_q': rf_planat['top10_q'],
                       'top10_amplitudes': rf_planat['top10_amplitudes'],
                       'peak_q': rf_planat['peak_q'],
                       'mode': rf_planat.get('mode')},
           rf_indicator={'top10_q': rf_indicator['top10_q'],
                          'top10_amplitudes': rf_indicator['top10_amplitudes'],
                          'peak_q': rf_indicator['peak_q'],
                          'mode': rf_indicator.get('mode'),
                          'n_bins': rf_indicator.get('n_bins')},
           solar_cycle_comparison=dict(
               solar_max=dict(n=int(mx_max.size),
                               fano=fano_max,
                               primary=nns_max['primary_nns'] if nns_max else None) if fano_max else None,
               solar_min=dict(n=int(mx_min.size),
                               fano=fano_min,
                               primary=nns_min['primary_nns'] if nns_min else None) if fano_min else None,
           ))

with open(os.path.join(DATA, "solar_flare_results.json"), 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"\n  → data/solar_flare_results.json")


# ─── Plot ────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

# Panel 1 — fingerprint heatmap
ax = axes[0, 0]
keys_full = ['KS_GUE', 'KS_GOE', 'KS_P', 'mass<.3',
             'F(1)', 'F(5)', 'rep_int', 'top_q', 'sb_KS', 'p_dom']
labels = [k for k, v in results.items() if 'fingerprint_vector' in v]
M = np.array([results[k]['fingerprint_vector'] for k in labels])
col_min = np.nanmin(M, axis=0); col_max = np.nanmax(M, axis=0)
rng = np.where(col_max > col_min, col_max - col_min, 1.0)
Mn = (M - col_min) / rng
im = ax.imshow(Mn, aspect='auto', cmap='RdBu_r', vmin=0, vmax=1)
ax.set_xticks(range(len(keys_full)), labels=keys_full, rotation=45, ha='right', fontsize=8)
ax.set_yticks(range(len(labels)), labels=labels, fontsize=9)
for i in range(len(labels)):
    for j in range(len(keys_full)):
        v = M[i, j]; vn = Mn[i, j]
        ax.text(j, i, f"{v:.2f}", ha='center', va='center', fontsize=7,
                color='white' if abs(vn - 0.5) > 0.32 else 'black')
ax.set_title('Phase 13: solar-flare fingerprint matrix')

# Panel 2 — Ramanujan amplitudes M+X
ax = axes[0, 1]
amps_planat = np.asarray(rf_planat['amplitudes'])
amps_ind = np.asarray(rf_indicator['amplitudes'])
qs = np.arange(1, len(amps_planat) + 1)
ax.plot(qs, np.abs(amps_planat), 'C0-', lw=1, alpha=0.7,
        label=f"Planat-mode (top q={rf_planat['peak_q']})")
ax.plot(qs, np.abs(amps_ind), 'C1-', lw=1, alpha=0.7,
        label=f"indicator-mode  (top q={rf_indicator['peak_q']})")
for q in rf_planat['top10_q'][:5]:
    ax.axvline(q, color='C0', ls=':', lw=0.8, alpha=0.5)
ax.set_xlabel('q')
ax.set_ylabel('|a_q|')
ax.set_title('M+X inter-flare RF spectrum (Planat 2009 comparison)')
ax.set_yscale('log')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Panel 3 — Fano curve solar_max vs solar_min on M+X
ax = axes[1, 0]
if fano_max and fano_min:
    ax.plot(np.array(fano_max['T_in_mean_sp']), fano_max['F'], 'C3o-',
            lw=2, ms=5, label=f"solar_max M+X  n={mx_max.size}")
    ax.plot(np.array(fano_min['T_in_mean_sp']), fano_min['F'], 'C0s-',
            lw=2, ms=5, label=f"solar_min M+X  n={mx_min.size}")
    ax.axhline(1.0, color='gray', ls='--', lw=0.8, label='Poisson F=1')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('T (units of mean spacing)')
    ax.set_ylabel('Fano factor F(T)')
    ax.set_title('Solar-cycle Fano comparison on M+X')
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=9)

# Panel 4 — KS_GUE bars per stratum
ax = axes[1, 1]
xs = []
ks_u_vals = []
mass03_vals = []
for k, v in results.items():
    if 'fingerprint_vector' in v:
        xs.append(k)
        ks_u_vals.append(v['fingerprint_vector'][0])
        mass03_vals.append(v['fingerprint_vector'][3])
xs_pos = np.arange(len(xs))
w = 0.4
ax.bar(xs_pos - w/2, ks_u_vals, width=w, color='C2', label='KS_GUE')
ax.bar(xs_pos + w/2, mass03_vals, width=w, color='C1', label='mass<0.3')
ax.set_xticks(xs_pos, labels=xs, rotation=30, ha='right', fontsize=8)
ax.set_ylabel('value')
ax.set_title('Per-stratum KS_GUE / mass<0.3')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=9)

fig.suptitle('Phase 13 — Solar X-ray flare statistics (1986-2023, GOES Plutino catalog)')
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "40_solar_flares.png"), dpi=120)
plt.close(fig)
print(f"  → plots/40_solar_flares.png")
