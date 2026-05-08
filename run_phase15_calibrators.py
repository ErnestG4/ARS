"""
Phase 15 Tier 2 — Calibrator scatter validation for the RF/NNS joint view.

Run `joint_q_profile` across 9 calibrator signals × 5 seeds each at
n_points=2000.  Pool the per-q rows into a long-form DataFrame with a
`signal_class` column.  Plot a 9-panel scatter (RF amplitude vs rep_int)
plus a 10th panel of median trajectories.  Apply k-nearest-neighbours
classification on per-q points to test discriminative power.

Acceptance:
  1. Visual separability across at least four classes.
  2. Quadrant assignment consistent with theoretical expectation
     (Poisson bottom-left, GUE top-right, periodic top-left, uniform-
     jitter bottom-right).
  3. KNN classifier per-q accuracy > 65% on held-out seeds.

Output:
  data/phase15_calibrator_joint.parquet
  data/phase15_seeds.json
  plots/42_phase15_joint_scatter.png
"""
import os, sys, json, time
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile
from signal_gen import (
    make_beta_ensemble_eigenvalues,
    make_uniform_jitter,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
N_POINTS = 2000
N_SEEDS = 5
Q_MAX = 200
MIN_EVENTS = 30


def gen_poisson(n, seed):
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.exponential(1.0, size=n))


def gen_periodic_jitter(n, period, jitter, seed):
    rng = np.random.default_rng(seed)
    t = np.arange(1, n + 1, dtype=np.float64) * period \
        + jitter * rng.standard_normal(n)
    return np.sort(t)


def gen_mixed_periodic(n, periods, weights, jitter, seed):
    """Mix multiple periodic-with-jitter components plus some Poisson noise."""
    rng = np.random.default_rng(seed)
    streams = []
    for p, w in zip(periods, weights):
        n_p = int(n * w)
        t = np.arange(1, n_p + 1, dtype=np.float64) * p \
            + jitter * rng.standard_normal(n_p)
        streams.append(t)
    bg = np.cumsum(rng.exponential(periods[0], size=int(n * 0.3)))
    streams.append(bg)
    out = np.sort(np.concatenate(streams))
    return out[:n]


def load_zeta(n=2000):
    z = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"), max_rows=n)
    return (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8


CALIBRATORS = [
    ('poisson',          lambda seed: gen_poisson(N_POINTS, seed)),
    ('beta=1_GOE',       lambda seed: make_beta_ensemble_eigenvalues(N_POINTS, 1, seed)),
    ('beta=2_GUE',       lambda seed: make_beta_ensemble_eigenvalues(N_POINTS, 2, seed)),
    ('beta=4_GSE',       lambda seed: make_beta_ensemble_eigenvalues(N_POINTS, 4, seed)),
    ('periodic_q7',      lambda seed: gen_periodic_jitter(N_POINTS, 7.0, 0.05, seed)),
    ('periodic_q12',     lambda seed: gen_periodic_jitter(N_POINTS, 12.0, 0.05, seed)),
    ('mixed_q7_q12',     lambda seed: gen_mixed_periodic(N_POINTS, [7.0, 12.0], [0.4, 0.4], 0.05, seed)),
    ('uniform_jitter_0.10', lambda seed: make_uniform_jitter(N_POINTS, 0.10, seed)),
    ('zeta_first_2000',  lambda seed: load_zeta(N_POINTS)),  # deterministic
]


def main():
    t_start = time.time()
    seeds_log = {}
    rows = []
    print("=" * 110)
    print(f"Phase 15 Tier 2 — joint_q_profile across {len(CALIBRATORS)} classes "
          f"× {N_SEEDS} seeds, n={N_POINTS}, q_max={Q_MAX}")
    print("=" * 110)

    for class_name, gen in CALIBRATORS:
        seeds_log[class_name] = list(range(N_SEEDS))
        for seed in range(N_SEEDS):
            t0 = time.time()
            try:
                t_k = gen(seed)
            except Exception as e:
                print(f"  {class_name} seed={seed}: gen failed: {e}")
                continue
            df = joint_q_profile(t_k, q_max=Q_MAX,
                                  min_events_per_q=MIN_EVENTS)
            df['signal_class'] = class_name
            df['seed'] = seed
            rows.append(df)
            elapsed = time.time() - t0
            print(f"  {class_name:<22} seed={seed}  n_events_q median={int(df['n_events_q'].median()):>7,}  "
                  f"rep_int median={df.loc[~df['underpowered'], 'rep_int_q'].median():.3f}  "
                  f"KS_GUE median={df.loc[~df['underpowered'], 'ks_gue_q'].median():.3f}  ⏱ {elapsed:.0f}s")
            if class_name == 'zeta_first_2000':
                # deterministic; one seed is enough
                break

    pooled = pd.concat(rows, ignore_index=True)
    pooled.to_parquet(os.path.join(DATA, "phase15_calibrator_joint.parquet"))
    print(f"\n  → data/phase15_calibrator_joint.parquet "
          f"({len(pooled)} rows)")

    with open(os.path.join(DATA, "phase15_seeds.json"), 'w') as f:
        json.dump(dict(seeds=seeds_log, n_points=N_POINTS, q_max=Q_MAX,
                        min_events=MIN_EVENTS), f, indent=2)
    print(f"  → data/phase15_seeds.json")

    # ─── KNN discriminative power test ───────────────────────────────────────
    print("\n" + "=" * 110)
    print("KNN per-q discriminative power test")
    print("=" * 110)
    from sklearn.neighbors import KNeighborsClassifier
    well = pooled[~pooled['underpowered']].copy()
    feat_cols = ['rf_amplitude_q', 'rep_int_q', 'ks_gue_q', 'mass_lt_0_3_q',
                  'F_T5_q']
    well = well.dropna(subset=feat_cols)
    # Train on seeds {0, 1, 2}; test on {3, 4} per class.
    train = well[well['seed'].isin([0, 1, 2])]
    test  = well[well['seed'].isin([3, 4])]
    if len(train) > 50 and len(test) > 20:
        clf = KNeighborsClassifier(n_neighbors=5)
        clf.fit(train[feat_cols].values, train['signal_class'].values)
        acc = clf.score(test[feat_cols].values, test['signal_class'].values)
        print(f"  KNN (k=5) per-q classification accuracy: {acc:.3f}")
        n_classes = len(test['signal_class'].unique())
        print(f"  N classes in test: {n_classes}, chance level: {1/n_classes:.3f}")
        if acc > 0.65:
            print(f"  ✓ DISCRIMINATIVE: accuracy {acc:.2f} > 0.65 threshold")
        else:
            print(f"  ✗ NOT DISCRIMINATIVE: accuracy {acc:.2f} ≤ 0.65")
    else:
        acc = None
        print(f"  insufficient data for KNN (train={len(train)}, test={len(test)})")

    # ─── Plot ────────────────────────────────────────────────────────────────
    classes = list(set(c[0] for c in CALIBRATORS))
    fig, axes = plt.subplots(3, 3, figsize=(14, 12))
    axes = axes.flatten()
    # Use Poisson medians as the quadrant origin
    poi = pooled[pooled['signal_class'] == 'poisson']
    poi_well = poi[~poi['underpowered']]
    qx = poi_well['rf_amplitude_q'].median()
    qy = poi_well['rep_int_q'].median()
    color_map = {c[0]: f'C{i % 10}' for i, c in enumerate(CALIBRATORS)}

    for ax_i, (class_name, _) in enumerate(CALIBRATORS):
        ax = axes[ax_i]
        sub = pooled[pooled['signal_class'] == class_name]
        well_sub = sub[~sub['underpowered']]
        und_sub  = sub[sub['underpowered']]
        size_well = (np.log10(np.clip(well_sub['n_events_q'], 1, None)) + 1) * 8
        ax.scatter(well_sub['rf_amplitude_q'], well_sub['rep_int_q'],
                    s=size_well, c=color_map[class_name], alpha=0.5,
                    edgecolors='none')
        ax.scatter(und_sub['rf_amplitude_q'], und_sub['rep_int_q'],
                    s=10, c=color_map[class_name], alpha=0.15,
                    edgecolors='none')
        ax.axvline(qx, color='gray', ls=':', lw=0.8)
        ax.axhline(qy, color='gray', ls=':', lw=0.8)
        ax.set_xscale('log')
        ax.set_xlabel('rf_amplitude_q')
        ax.set_ylabel('rep_int_q')
        ax.set_title(class_name, fontsize=9)
        ax.grid(True, alpha=0.2)
        ax.set_xlim(1e-4, 2)
        ax.set_ylim(-0.05, 1.0)

    fig.suptitle('Phase 15 Tier 2 — joint_q_profile calibrator scatter '
                  '(quadrant lines = Poisson medians)')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOTS, "42_phase15_joint_scatter.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/42_phase15_joint_scatter.png")

    # ─── Median-trajectory overlay (10th panel) ──────────────────────────────
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    for class_name, _ in CALIBRATORS:
        sub = pooled[pooled['signal_class'] == class_name]
        well_sub = sub[~sub['underpowered']]
        if len(well_sub) < 10: continue
        # Median (rf, rep_int) over all q for this class, plus median path by q
        med_x = well_sub.groupby('q')['rf_amplitude_q'].median()
        med_y = well_sub.groupby('q')['rep_int_q'].median()
        ax.scatter(med_x.values, med_y.values, s=14,
                    c=color_map[class_name], alpha=0.6,
                    edgecolors='none', label=class_name)
        # Mark median centroid
        cx, cy = med_x.median(), med_y.median()
        ax.scatter([cx], [cy], s=140, marker='*', c=color_map[class_name],
                    edgecolors='black', linewidth=1, zorder=5)
    ax.axvline(qx, color='gray', ls=':', lw=0.8)
    ax.axhline(qy, color='gray', ls=':', lw=0.8)
    ax.set_xscale('log')
    ax.set_xlabel('rf_amplitude_q (median over seeds)')
    ax.set_ylabel('rep_int_q (median over seeds)')
    ax.set_title('Phase 15 Tier 2 — median trajectories per signal class')
    ax.set_xlim(1e-4, 2)
    ax.set_ylim(-0.05, 1.0)
    ax.legend(fontsize=8, loc='best')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "42b_phase15_median_trajectories.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/42b_phase15_median_trajectories.png")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == '__main__':
    main()
