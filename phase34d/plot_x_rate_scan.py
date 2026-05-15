"""
phase34d/plot_x_rate_scan.py — visualize the X-rate scan: σ²/(N/K) vs β
at three X values, plus deficit(X) vs 1/log X with the Chen 2019 NLO
prediction line.

Outputs:
  plots/phase34d_x_rate_scan.png  — main figure (saturation curves at 3 X)
  plots/phase34d_x_rate_deficit.png  — deficit vs 1/log X with fit
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
PLOT_DIR = Path(ROOT_DIR) / 'plots'
PLOT_DIR.mkdir(parents=True, exist_ok=True)
DATA = Path(ROOT_DIR) / 'data' / 'phase34d_results' / 'x_rate_scan.json'


def main():
    with open(DATA) as f:
        d = json.load(f)
    recs = d['records']
    fits = d['fits']

    # ─── Figure 1: σ²/(N/K) vs β at three X values, both substrates ──────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    betas = np.linspace(0, 1, 400)
    rw = np.minimum(1.0, 2.0 * betas)

    color_map = {
        1_000_000: 'lightblue',
        10_000_000: 'cornflowerblue',
        100_000_000: 'darkblue',
    }

    for ax, sub in zip(axes, ('gaussian', 'eisenstein')):
        ax.plot(betas, rw, 'k-', label='RW Conj 1.2: min(1, 2β)', lw=2)
        ax.axhline(1.0, color='gray', ls=':', alpha=0.5, lw=0.8)
        ax.axvline(0.5, color='gray', ls=':', alpha=0.5, lw=0.8)
        for X in (1_000_000, 10_000_000, 100_000_000):
            sub_recs = [r for r in recs if r['substrate'] == sub and r['X'] == X]
            if not sub_recs:
                continue
            xs = [r['beta_mean'] for r in sub_recs]
            ys = [r['ratio_mean'] for r in sub_recs]
            yerr = [2.0 * r['ratio_std'] for r in sub_recs]
            ax.errorbar(xs, ys, yerr=yerr, fmt='o',
                        color=color_map[X], markersize=7,
                        capsize=3, elinewidth=1.0,
                        markeredgecolor='black', markeredgewidth=0.4,
                        label=f"X=10^{int(np.log10(X))}  (2σ)",
                        zorder=5)
        ax.set_xlabel(r"$\beta = \log K / \log N$", fontsize=11)
        ax.set_title(f"{sub.title()} primes — three-X scan", fontsize=11)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.2)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower right', fontsize=8.5, framealpha=0.95)
    axes[0].set_ylabel(r"$\sigma^2(K, X) / (N/K)$", fontsize=11)

    out1 = PLOT_DIR / 'phase34d_x_rate_scan.png'
    plt.suptitle("Phase 34d X-rate scan — σ²(K, X)/(N/K) at X ∈ {10⁶, 10⁷, 10⁸}\n"
                 "Convergence toward RW asymptote as X grows tests finite-X correction vs substrate departure",
                 fontsize=10)
    plt.tight_layout()
    plt.savefig(out1, dpi=130)
    plt.close()
    print(f"→ wrote {out1}")

    # ─── Figure 2: deficit vs 1/log X at fixed β, with linear fit ───────
    saturation_betas = [0.55, 0.65, 0.75, 0.85, 0.95]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    color_beta = plt.cm.plasma(np.linspace(0.1, 0.9, len(saturation_betas)))

    for ax, sub in zip(axes, ('gaussian', 'eisenstein')):
        for i, b_t in enumerate(saturation_betas):
            sub_recs = sorted(
                [r for r in recs if r['substrate'] == sub
                 and abs(r['beta_target'] - b_t) < 1e-9],
                key=lambda r: r['log_X'])
            if len(sub_recs) < 2:
                continue
            inv_log_X = [1.0 / r['log_X'] for r in sub_recs]
            deficits = [r['deficit'] for r in sub_recs]
            errs = [r['ratio_std'] for r in sub_recs]
            ax.errorbar(inv_log_X, deficits, yerr=errs, fmt='o-',
                        color=color_beta[i], markersize=7,
                        capsize=3, elinewidth=1.0,
                        label=f"β={b_t}")
            # Fit line
            for f in fits:
                if (f['substrate'] == sub and
                        abs(f['beta_target'] - b_t) < 1e-9):
                    a, b = f['a_over_logX'], f['b_offset']
                    xx = np.array([0, max(inv_log_X) * 1.1])
                    yy = a * xx + b
                    ax.plot(xx, yy, '--', color=color_beta[i], alpha=0.5, lw=1.0)
                    break
        ax.axhline(0, color='gray', ls=':', alpha=0.6, lw=0.8)
        ax.set_xlabel(r"$1 / \log X$", fontsize=11)
        ax.set_title(f"{sub.title()} primes — saturation regime deficit vs 1/log X", fontsize=11)
        ax.set_xlim(0, None)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=8.5, framealpha=0.95)
    axes[0].set_ylabel(r"deficit := RW $-$ empirical $\sigma^2/(N/K)$", fontsize=11)

    out2 = PLOT_DIR / 'phase34d_x_rate_deficit.png'
    plt.suptitle("Phase 34d X-rate deficit — Chen 2019 NLO predicts deficit $\\propto 1/\\log X$ "
                 "in saturation regime\n"
                 "Linear fit deficit $= a/\\log X + b$: $b \\approx 0$ → finite-X correction; "
                 "$b > 0$ → residual substrate departure",
                 fontsize=10)
    plt.tight_layout()
    plt.savefig(out2, dpi=130)
    plt.close()
    print(f"→ wrote {out2}")


if __name__ == '__main__':
    main()
