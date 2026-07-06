"""
Phase 17 Tier 2 — mixed-class recovery.

Generate mixed-class fields, run joint_q_profile, apply
recover_spectral_decomposition.  Verify each test case yields the
expected component structure (RF peaks + rep_int_q bands).

Output:
  data/phase17_mixed_recovery.parquet
  plots/48_phase17_mixed_recovery.png
"""
import os, sys, json, time
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile
from field_generator import generate_mixed
from bulk_recovery import (recover_spectral_decomposition,
                            recover_periodic_q)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
N_EVENTS = 1000
N_SEEDS = 3
Q_MAX = 30


TEST_CASES = [
    {
        'name': 'periodic_q7_plus_poisson',
        'description': 'Periodic q=7 + Poisson background, equal weight',
        'components': [
            dict(class_='periodic', params=dict(q=7, jitter=0.05), weight=0.5),
            dict(class_='poisson',  params=dict(rate=1.0),         weight=0.5),
        ],
        'expected_rf_peaks': [7],
        'expected_bands': ['poisson', 'br_artifact'],
    },
    {
        'name': 'periodic_q5_plus_q12',
        'description': 'Two periodic components q=5 and q=12',
        'components': [
            dict(class_='periodic', params=dict(q=5,  jitter=0.05), weight=0.5),
            dict(class_='periodic', params=dict(q=12, jitter=0.05), weight=0.5),
        ],
        'expected_rf_peaks': [5, 12],
        'expected_bands': ['br_artifact'],
    },
    {
        'name': 'gue_plus_uniform_jitter',
        'description': 'Wigner GUE + uniform-jitter superposition',
        'components': [
            dict(class_='wigner_gue',     params={},                  weight=0.5),
            dict(class_='uniform_jitter', params=dict(sigma=0.10),    weight=0.5),
        ],
        'expected_rf_peaks': [],
        'expected_bands': ['wigner', 'br_artifact'],
    },
    {
        'name': 'periodic_q8_low_snr',
        'description': 'Periodic q=8 + dominant Poisson (low SNR)',
        'components': [
            dict(class_='periodic', params=dict(q=8, jitter=0.05),  weight=0.2),
            dict(class_='poisson',  params=dict(rate=1.0),          weight=0.8),
        ],
        'expected_rf_peaks': [8],
        'expected_bands': ['poisson', 'br_artifact'],
    },
]


def main():
    t_start = time.time()
    rows = []
    print("=" * 110)
    print(f"Phase 17 Tier 2 — mixed-class recovery, {N_SEEDS} seeds × "
          f"{len(TEST_CASES)} cases at n={N_EVENTS}, q_max={Q_MAX}")
    print("=" * 110)

    for case in TEST_CASES:
        for seed in range(N_SEEDS):
            specs = [{'class': c['class_'], 'params': c['params'], 'weight': c['weight']}
                      for c in case['components']]
            t = generate_mixed(specs, n_events=N_EVENTS, seed=seed)
            j = joint_q_profile(t, q_max=Q_MAX, min_events_per_q=30)
            decomp = recover_spectral_decomposition(j)
            recovered_qs = sorted([p['q'] for p in decomp.get('rf_peaks', [])])
            recovered_bands = sorted(set(b['class_'] for b in decomp.get('bands', [])))
            expected_qs_match = set(case['expected_rf_peaks']).issubset(set(recovered_qs))
            expected_bands_match = set(case['expected_bands']).issubset(set(recovered_bands))
            print(f"  {case['name']:<32}  seed={seed}  "
                  f"recovered RF peaks={recovered_qs}  "
                  f"bands={recovered_bands}  "
                  f"qs_match={expected_qs_match}  bands_match={expected_bands_match}")
            rows.append(dict(
                case=case['name'], seed=seed,
                expected_rf_peaks=str(case['expected_rf_peaks']),
                recovered_rf_peaks=str(recovered_qs),
                expected_bands=str(case['expected_bands']),
                recovered_bands=str(recovered_bands),
                qs_match=expected_qs_match,
                bands_match=expected_bands_match,
                n_components=int(decomp.get('n_components', 0)),
            ))

    df = pd.DataFrame(rows)
    df.to_parquet(os.path.join(DATA, "phase17_mixed_recovery.parquet"))
    print(f"\n  → data/phase17_mixed_recovery.parquet ({len(df)} rows)")

    print("\n" + "=" * 110)
    print("Per-case summary (qs and bands recovered correctly across seeds)")
    print("=" * 110)
    for case in TEST_CASES:
        sub = df[df['case'] == case['name']]
        n = len(sub)
        qs_pct = sub['qs_match'].mean() * 100
        bands_pct = sub['bands_match'].mean() * 100
        print(f"  {case['name']:<32}  qs_match: {qs_pct:>5.1f}%  "
              f"bands_match: {bands_pct:>5.1f}%  ({n} seeds)")

    # ─── Plot per-case rf_amplitude_q + rep_int_q ──────────────────────────
    fig, axes = plt.subplots(len(TEST_CASES), 2, figsize=(13, 3.2 * len(TEST_CASES)))
    if len(TEST_CASES) == 1: axes = axes[None, :]
    for i, case in enumerate(TEST_CASES):
        # Re-run a single seed for plotting (fast)
        specs = [{'class': c['class_'], 'params': c['params'], 'weight': c['weight']}
                  for c in case['components']]
        t = generate_mixed(specs, n_events=N_EVENTS, seed=0)
        j = joint_q_profile(t, q_max=Q_MAX, min_events_per_q=30)
        well = j[~j['underpowered']]
        ax_rf = axes[i, 0]; ax_rep = axes[i, 1]
        ax_rf.plot(well['q'], well['rf_amplitude_q'], 'C0o-', lw=1, ms=4)
        for q_exp in case['expected_rf_peaks']:
            ax_rf.axvline(q_exp, color='C3', ls='--', lw=1, alpha=0.6)
        ax_rf.set_yscale('log')
        ax_rf.set_xlabel('q'); ax_rf.set_ylabel('|a_q|')
        ax_rf.set_title(f"{case['name']} — RF spectrum (red dashed = expected)", fontsize=9)
        ax_rf.grid(True, alpha=0.3)

        ax_rep.plot(well['q'], well['rep_int_q'], 'C2o-', lw=1, ms=4)
        ax_rep.axhline(0.10, color='gray', ls=':', lw=0.8)
        ax_rep.axhline(0.55, color='gray', ls=':', lw=0.8)
        ax_rep.set_xlabel('q'); ax_rep.set_ylabel('rep_int_q')
        ax_rep.set_ylim(-0.05, 1.0)
        ax_rep.set_title(f"{case['name']} — rep_int per q", fontsize=9)
        ax_rep.grid(True, alpha=0.3)
    fig.suptitle('Phase 17 Tier 2 — mixed-class joint_q_profile signatures')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOTS, "48_phase17_mixed_recovery.png"), dpi=120)
    plt.close(fig)
    print(f"\n  → plots/48_phase17_mixed_recovery.png")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == '__main__':
    main()
