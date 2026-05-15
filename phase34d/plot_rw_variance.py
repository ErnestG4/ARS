"""
phase34d/plot_rw_variance.py — produce a plot of σ²(K, X)/(N/K) vs
β = log K / log N, alongside the RW Conjecture 1.2 min(1, 2β) curve.

This is the empirical version of Rudnick-Waxman 2019 Figure 1.

Outputs:
  plots/phase34d_rw_variance.png
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
DATA = Path(ROOT_DIR) / 'data' / 'phase34d_results' / 'rw_variance_direct.json'


def main():
    with open(DATA) as f:
        d = json.load(f)
    recs = d['records']

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    # Plot RW conjecture: min(1, 2β)
    betas = np.linspace(0, 1, 400)
    rw = np.minimum(1.0, 2.0 * betas)
    ax.plot(betas, rw, 'k-', label='RW Conjecture 1.2: min(1, 2β)', lw=2)

    # Markers for each substrate × X
    colors = {
        ('gaussian',    100_000):    'lightblue',
        ('gaussian',  1_000_000):    'cornflowerblue',
        ('gaussian', 10_000_000):    'darkblue',
        ('eisenstein',    100_000):  'lightcoral',
        ('eisenstein',  1_000_000):  'tomato',
        ('eisenstein', 10_000_000):  'darkred',
    }
    markers = {'gaussian': 'o', 'eisenstein': 's'}

    for sub in ('gaussian', 'eisenstein'):
        for X in (100_000, 1_000_000, 10_000_000):
            xs = [r['beta_logK_over_logN'] for r in recs
                  if r['substrate'] == sub and r['X'] == X]
            ys = [r['ratio_emp_over_NoverK'] for r in recs
                  if r['substrate'] == sub and r['X'] == X]
            if not xs:
                continue
            ax.scatter(xs, ys, c=colors[(sub, X)],
                       marker=markers[sub], s=90,
                       label=f"{sub} X=10^{int(np.log10(X))}",
                       edgecolors='black', linewidths=0.6, zorder=5)

    ax.set_xlabel(r"$\beta = \log K / \log N$", fontsize=12)
    ax.set_ylabel(r"$\sigma^2(K, X) / (N/K)$", fontsize=12)
    ax.set_title("Phase 34d Step 3 — direct Rudnick-Waxman variance check\n"
                 "(Empirical reproduction of RW 2019 Figure 1)", fontsize=12)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.2)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=9, framealpha=0.95)
    ax.axhline(1.0, color='gray', ls=':', alpha=0.5, lw=0.8)
    ax.axvline(0.5, color='gray', ls=':', alpha=0.5, lw=0.8)

    out = PLOT_DIR / 'phase34d_rw_variance.png'
    plt.tight_layout()
    plt.savefig(out, dpi=130)
    plt.close()
    print(f"→ wrote {out}")


if __name__ == '__main__':
    main()
