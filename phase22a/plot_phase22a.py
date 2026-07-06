"""
phase22a/plot_phase22a.py — diagnostic plots for the Phase 22a writeup.

  fig 1  per-unit primary quadrant counts × recording (H1)
  fig 2  ARS rep_med vs OSI partial-corr scatter (H1 cross-validation)
  fig 3  cross-stimulus consistency Sankey-style transitions (H1 (C))
  fig 4  population-event freq band coverage per recording × q_max (H2)
  fig 5  real vs surrogate rep_int_q overlay per (recording, surrogate)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
PLOT_DIR = Path(ROOT_DIR) / 'plots' / 'phase22a'
PLOT_DIR.mkdir(parents=True, exist_ok=True)

QUAD_COLORS = {
    'BL': '#2ca02c', 'TR': '#1f77b4', 'TL': '#ff7f0e',
    'BR_artifact': '#d62728', 'BR_novel': '#9467bd',
    'ambiguous': '#888', 'underpowered': '#ccc',
}


def fig1_h1_quadrants():
    df = pd.read_parquet(OUT_DIR / 'h1_classifications.parquet')
    cnt = df.groupby('recording')['primary'].value_counts().unstack(fill_value=0)
    rec_order = sorted(cnt.index)
    cnt = cnt.loc[rec_order]
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = np.zeros(len(rec_order))
    for q in cnt.columns:
        col = QUAD_COLORS.get(q, '#888')
        ax.bar(range(len(rec_order)), cnt[q].values, bottom=bottom,
                color=col, label=q, edgecolor='white', linewidth=0.5)
        bottom += cnt[q].values
    ax.set_xticks(range(len(rec_order)))
    ax.set_xticklabels(rec_order, rotation=45, ha='right')
    ax.set_ylabel('# units')
    ax.set_title('Phase 22a H1 — per-unit ARS modal quadrant by recording')
    ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    p = PLOT_DIR / 'fig1_h1_quadrants.png'
    plt.savefig(p, dpi=120); plt.close()
    print(f"  → {p}")


def fig2_h1_xv_scatter():
    ars = pd.read_parquet(OUT_DIR / 'h1_classifications.parquet')
    func = pd.read_parquet(OUT_DIR / 'h1_functional.parquet')
    j = ars.merge(func, on=['recording', 'unit_idx', 'subset', 'monkey',
                              'unit_id'])
    if 'osi' not in j: return
    sub = j.dropna(subset=['osi', 'ks_gue_med', 'mean_rate'])
    if not len(sub): return
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    sc = axes[0].scatter(sub['ks_gue_med'], sub['osi'],
                          c=np.log10(sub['mean_rate'] + 0.1),
                          cmap='viridis', s=15, alpha=0.7)
    axes[0].set_xlabel('ARS ks_gue_med (per-unit pooled)')
    axes[0].set_ylabel('OSI')
    axes[0].set_title(f'OSI vs ks_gue_med  n={len(sub)}\n'
                       'colored by log mean firing rate')
    plt.colorbar(sc, ax=axes[0], label='log10(rate + 0.1)')

    if 'f1_f0_pref' in j:
        sub2 = j.dropna(subset=['f1_f0_pref', 'rep_med', 'mean_rate'])
        if len(sub2):
            sc = axes[1].scatter(sub2['rep_med'], sub2['f1_f0_pref'],
                                  c=np.log10(sub2['mean_rate'] + 0.1),
                                  cmap='viridis', s=15, alpha=0.7)
            axes[1].set_xlabel('ARS rep_med (per-unit pooled)')
            axes[1].set_ylabel('F1/F0')
            axes[1].axhline(1.0, color='gray', ls='--', lw=1)
            axes[1].set_title(f'F1/F0 vs rep_med  n={len(sub2)}')
            plt.colorbar(sc, ax=axes[1], label='log10(rate + 0.1)')

    if 'dsi' in j:
        sub3 = j.dropna(subset=['dsi', 'ks_gue_med'])
        if len(sub3):
            axes[2].scatter(sub3['ks_gue_med'], sub3['dsi'], s=15, alpha=0.6)
            axes[2].set_xlabel('ARS ks_gue_med')
            axes[2].set_ylabel('DSI')
            axes[2].set_title(f'DSI vs ks_gue_med  n={len(sub3)}')

    fig.suptitle('Phase 22a H1 (B) — ARS metrics vs functional descriptors',
                  fontsize=11)
    plt.tight_layout()
    p = PLOT_DIR / 'fig2_h1_xv_scatter.png'
    plt.savefig(p, dpi=120); plt.close()
    print(f"  → {p}")


def fig3_cross_stim():
    p_in = OUT_DIR / 'h1_crossval_perunit.parquet'
    if not p_in.exists(): return
    cc = pd.read_parquet(p_in)
    if not len(cc): return
    triple = cc[cc['n_movies_present'] == 3]
    if not len(triple): return
    cnt = triple.groupby(['primary_gratings_movie',
                            'primary_natural_movie',
                            'primary_noise_movie']).size().reset_index(name='n')
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(cnt)),
            cnt['n'].values, color='steelblue', edgecolor='white')
    labels = [f"{r['primary_gratings_movie']}→\n"
              f"{r['primary_natural_movie']}→\n"
              f"{r['primary_noise_movie']}"
              for _, r in cnt.iterrows()]
    ax.set_xticks(range(len(cnt)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel('# units')
    ax.set_title('Phase 22a H1 (C) — quadrant transitions across 3 matched-unit movies\n'
                  '(monkey1 + monkey2 pooled)')
    plt.tight_layout()
    out = PLOT_DIR / 'fig3_cross_stim_transitions.png'
    plt.savefig(out, dpi=120); plt.close()
    print(f"  → {out}")


def fig4_h2_coverage():
    cov = pd.read_parquet(OUT_DIR / 'h2_coverage.parquet')
    if not len(cov): return
    fig, ax = plt.subplots(figsize=(11, 5))
    for q_max, marker, color in [(30, 'o', 'steelblue'), (100, 's', 'firebrick')]:
        sub = cov[cov['q_max'] == q_max].sort_values('recording')
        for i, (_, r) in enumerate(sub.iterrows()):
            ax.plot([r['freq_band_lo_hz'], r['freq_band_hi_hz']],
                     [i, i], color=color, marker=marker, lw=2, ms=4,
                     label=f'q_max={q_max}' if i == 0 else None)
    ax.set_xscale('log')
    ax.axvspan(0.5, 3.0, alpha=0.18, color='gold',
                label='V1 anesthetised Up/Down (0.5–3 Hz)')
    ax.axvspan(15, 30, alpha=0.10, color='green', label='Beta (15–30 Hz)')
    ax.axvspan(30, 80, alpha=0.10, color='magenta', label='Gamma (30–80 Hz)')
    sub30 = cov[cov['q_max'] == 30].sort_values('recording')
    ax.set_yticks(range(len(sub30)))
    ax.set_yticklabels(sub30['recording'].values, fontsize=9)
    ax.set_xlabel('Frequency probed by q-band (Hz, log scale)')
    ax.set_title('Phase 22a H2 — population-event q-band time-frequency coverage')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='lower right', fontsize=8)
    ax.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()
    out = PLOT_DIR / 'fig4_h2_coverage.png'
    plt.savefig(out, dpi=120); plt.close()
    print(f"  → {out}")


def fig5_h2_surrogate_overlay():
    p_real = OUT_DIR / 'h2_population_classifications.parquet'
    p_surr = OUT_DIR / 'h2_surrogate_classifications.parquet'
    if not (p_real.exists() and p_surr.exists()): return
    real = pd.read_parquet(p_real)
    surr = pd.read_parquet(p_surr)
    # Pick q_max=30 view for clarity
    real30 = real[real['q_max'] == 30]
    surr30 = surr[surr['q_max'] == 30]
    rec_subset = real30['recording'].unique()[:6]   # first 6 for the panel
    fig, axes = plt.subplots(2, 3, figsize=(14, 7), sharey=True)
    for i, rec in enumerate(rec_subset):
        ax = axes[i // 3, i % 3]
        rr = real30[real30['recording'] == rec]
        if not len(rr): continue
        rep_in = rr.iloc[0]['rep_int_per_q']
        if rep_in is None: continue
        real_rep = np.array(list(rep_in), dtype=float)
        x = np.arange(1, len(real_rep) + 1)
        ax.plot(x, real_rep, 'k-', lw=2.0, label='real')
        for kind, color in [('rate_matched_poisson', '#888'),
                             ('cell_shuffle', 'tab:orange'),
                             ('state_modulated', 'tab:green'),
                             ('ln_evoked', 'tab:purple')]:
            sg = surr30[(surr30['recording'] == rec) &
                          (surr30['surrogate'] == kind)]
            if not len(sg): continue
            arrs = []
            for _, sr in sg.iterrows():
                src = sr['rep_int_per_q']
                if src is None: continue
                arr = np.array(list(src), dtype=float)
                if arr.size == real_rep.size: arrs.append(arr)
            if not arrs: continue
            stack = np.stack(arrs)
            ax.fill_between(x,
                              np.nanpercentile(stack, 5, axis=0),
                              np.nanpercentile(stack, 95, axis=0),
                              alpha=0.25, color=color, label=kind)
            ax.plot(x, np.nanmean(stack, axis=0), color=color, lw=1.0,
                     ls='--', alpha=0.8)
        ax.set_title(f'{rec}', fontsize=9)
        ax.set_xlabel('q-band'); ax.set_ylabel('rep_int_q')
        ax.legend(fontsize=7, loc='upper right')
        ax.set_ylim(0, 1)
    fig.suptitle('Phase 22a H2 — real vs surrogate rep_int_q (q_max=30, '
                  'surrogate band = 5–95% across seeds)')
    plt.tight_layout()
    out = PLOT_DIR / 'fig5_h2_surrogate_overlay.png'
    plt.savefig(out, dpi=120); plt.close()
    print(f"  → {out}")


def main():
    print("Phase 22a plots:")
    fig1_h1_quadrants()
    fig2_h1_xv_scatter()
    fig3_cross_stim()
    if (OUT_DIR / 'h2_coverage.parquet').exists():
        fig4_h2_coverage()
    if (OUT_DIR / 'h2_surrogate_classifications.parquet').exists():
        fig5_h2_surrogate_overlay()


if __name__ == '__main__':
    main()
