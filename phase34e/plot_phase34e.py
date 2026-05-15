"""
phase34e/plot_phase34e.py — visualizations for Phase 34e.

Produces:
  plots/phase34e_nns_per_level.png — bulk NNS rep_med per level, 20-seed
                                       distribution boxes
  plots/phase34e_berry_robnik_per_level.png — fitted ρ per level
  plots/phase34e_sato_tate_per_level.png — Hecke-eigenvalue histograms
                                             vs semicircular
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
DATA = Path(ROOT_DIR) / 'data' / 'phase34e_results'
PLOT_DIR = Path(ROOT_DIR) / 'plots'
PLOT_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_LEVELS = [91, 95, 85, 77, 93, 87]


def plot_nns_per_level():
    p = DATA / 'nns_classification.json'
    if not p.exists():
        print(f"skip NNS plot — {p} missing")
        return
    with open(p) as f:
        d = json.load(f)

    fig, ax = plt.subplots(1, 1, figsize=(9, 5.5))
    levels = []
    box_data = []
    labels = []
    for lvl in PRIMARY_LEVELS:
        r = d['results'].get(f'level_{lvl}')
        if r is None:
            continue
        rep_meds = r['seed_replicate']['rep_meds']
        levels.append(lvl)
        box_data.append(rep_meds)
        labels.append(f"Γ₀({lvl})\nN={r['N_eigenvalues']}")

    # TR/BL boundary at rep_med ~ 0.1; mark zones
    ax.axhspan(0.0, 0.1, color='lightcoral', alpha=0.20, label='BL (Poisson-leaning)')
    ax.axhspan(0.1, 0.6, color='lightblue', alpha=0.20, label='TR (Wigner-Dyson)')
    bp = ax.boxplot(box_data, tick_labels=labels, patch_artist=True,
                     widths=0.6)
    for box in bp['boxes']:
        box.set_facecolor('steelblue')
        box.set_alpha(0.7)
    ax.set_ylabel("rep_med (NNS quadrant continuous metric)", fontsize=11)
    ax.set_title("Phase 34e Test 1 — bulk NNS rep_med per Γ₀(N) level\n"
                 "(20-seed 80%-subsample distribution; BL classification = Sarnak anomaly)",
                 fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    out = PLOT_DIR / 'phase34e_nns_per_level.png'
    plt.savefig(out, dpi=130)
    plt.close()
    print(f"→ wrote {out}")


def plot_berry_robnik():
    p = DATA / 'berry_robnik.json'
    if not p.exists():
        print(f"skip BR plot — {p} missing")
        return
    with open(p) as f:
        d = json.load(f)
    fig, ax = plt.subplots(1, 1, figsize=(9, 5.5))
    xs = []
    rhos = []
    sigmas = []
    labels = []
    for lvl in PRIMARY_LEVELS:
        r = d['results'].get(f'level_{lvl}')
        if r is None:
            continue
        xs.append(lvl)
        rhos.append(r['bootstrap_rho_mean'])
        sigmas.append(r['bootstrap_rho_std'])
        labels.append(f"Γ₀({lvl})")
    ax.axhline(0.0, color='red', ls='--', alpha=0.5, label='ρ=0 (Poisson)')
    ax.axhline(1.0, color='blue', ls='--', alpha=0.5, label='ρ=1 (GOE)')
    ax.axhline(0.5, color='gray', ls=':', alpha=0.5, lw=0.8)
    ax.errorbar(range(len(xs)), rhos, yerr=sigmas, fmt='o',
                color='black', markersize=8, capsize=4, elinewidth=1.2)
    ax.set_xticks(range(len(xs)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Berry-Robnik ρ", fontsize=11)
    ax.set_title("Phase 34e Test 2 — Berry-Robnik ρ per level\n"
                 "(bootstrap 1σ error bars; Sarnak anomaly: ρ<<1, Poisson-dominant)",
                 fontsize=11)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    out = PLOT_DIR / 'phase34e_berry_robnik_per_level.png'
    plt.savefig(out, dpi=130)
    plt.close()
    print(f"→ wrote {out}")


def plot_sato_tate():
    p = DATA / 'sato_tate.json'
    if not p.exists():
        print(f"skip ST plot — {p} missing")
        return
    with open(p) as f:
        d = json.load(f)
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    axes = axes.flatten()
    for i, lvl in enumerate(PRIMARY_LEVELS):
        ax = axes[i]
        r = d['results'].get(f'level_{lvl}')
        if r is None:
            continue
        hist = r['histogram']
        bc = np.array(hist['bin_centers'])
        emp = np.array(hist['empirical_density'])
        pred = np.array(hist['predicted_density'])
        ax.bar(bc, emp, width=0.15, alpha=0.6, label='empirical', color='steelblue')
        ax.plot(bc, pred, 'r-', lw=2, label='semicircular μ_∞')
        ax.set_title(f"Γ₀({lvl})  KS_p={r['ks_test']['ks_p_value']:.2e}\n"
                     f"N_λ={r['n_hecke_eigenvalues']}", fontsize=10)
        ax.set_xlabel("λ_p (Ramanujan-Petersson)")
        ax.set_xlim(-2.2, 2.2)
        ax.grid(True, alpha=0.3)
        if i == 0:
            ax.legend(loc='upper right', fontsize=8)
    plt.suptitle("Phase 34e Test 3 — Hecke-eigenvalue Sato-Tate distribution per level\n"
                 "(methodology calibration; semicircular SU(2)-Sato-Tate is right null)",
                 fontsize=11)
    plt.tight_layout()
    out = PLOT_DIR / 'phase34e_sato_tate_per_level.png'
    plt.savefig(out, dpi=130)
    plt.close()
    print(f"→ wrote {out}")


def main():
    plot_nns_per_level()
    plot_berry_robnik()
    plot_sato_tate()


if __name__ == '__main__':
    main()
