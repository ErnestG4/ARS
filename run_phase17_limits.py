"""
Phase 17 Tier 3 — recovery limits (minimal n_events sweep).

Sweeps n_events ∈ {200, 500, 1000, 2000, 5000} on the four classes that
matter for downstream Tier 4 application: poisson, wigner_gue,
uniform_jitter, periodic_q7.  3 seeds per cell.  Reports recovery
accuracy and CI coverage as a function of sample size.

Output:
  data/phase17_recovery_limits.parquet
  plots/49_phase17_recovery_curves.png
"""
import os, sys, time
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile
from field_generator import generate
from bulk_recovery import (
    recover_poisson_rate, recover_wigner_beta,
    recover_periodic_q, recover_uniform_jitter_sigma,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")

N_GRID = [200, 500, 1000, 2000, 5000]
N_SEEDS = 3
Q_MAX = 30


def main():
    t_start = time.time()
    rows = []
    print("=" * 110)
    print(f"Phase 17 Tier 3 — n_events sweep, {N_SEEDS} seeds × 4 classes × "
          f"{len(N_GRID)} sizes = {N_SEEDS * 4 * len(N_GRID)} runs")
    print("=" * 110)

    for n in N_GRID:
        for cls, params, truth_param, truth_value, recover_fn in [
            ('poisson', dict(rate=1.0), 'rate', 1.0,
                lambda t, j: (recover_poisson_rate(t)[0],
                                recover_poisson_rate(t)[1])),
            ('wigner_gue', {}, 'beta', 2.0,
                lambda t, j: (recover_wigner_beta(j)[0],
                                recover_wigner_beta(j)[1])),
            ('uniform_jitter', dict(sigma=0.10), 'sigma', 0.10,
                lambda t, j: (recover_uniform_jitter_sigma(j)[0],
                                recover_uniform_jitter_sigma(j)[1])),
            ('periodic_q7',  dict(q=7, jitter=0.05), 'q', 7,
                lambda t, j: (recover_periodic_q(j, q_max=30)[0],
                                recover_periodic_q(j, q_max=30)[1])),
        ]:
            for seed in range(N_SEEDS):
                cls_key = 'periodic' if cls == 'periodic_q7' else cls
                t = generate(cls_key, params, n_events=n, seed=seed)
                j = joint_q_profile(t, q_max=Q_MAX, min_events_per_q=30)
                est, (lo, hi) = recover_fn(t, j)
                covers = bool(lo <= truth_value <= hi)
                rel_err = abs(est - truth_value) / truth_value if truth_value else float('nan')
                rows.append(dict(cls=cls, n_events=n, seed=seed,
                                  truth=truth_value, estimate=est,
                                  ci_lo=lo, ci_hi=hi, covers=covers,
                                  rel_err=rel_err))
                mark = '✓' if covers else '✗'
                print(f"  n={n:>5}  {cls:<16}  truth={truth_value}  "
                      f"est={est:>8.3f}  CI=[{lo:>7.3f}, {hi:>7.3f}]  {mark}")

    df = pd.DataFrame(rows)
    df.to_parquet(os.path.join(DATA, "phase17_recovery_limits.parquet"))
    print(f"\n  → data/phase17_recovery_limits.parquet ({len(df)} rows)")

    # ─── Plot recovery curves ──────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    classes = [('poisson', 'rate λ=1.0', axes[0, 0]),
                ('wigner_gue', 'GUE β=2', axes[0, 1]),
                ('uniform_jitter', 'uniform σ=0.10', axes[1, 0]),
                ('periodic_q7', 'periodic q=7', axes[1, 1])]
    for cls, title, ax in classes:
        sub = df[df['cls'] == cls]
        if len(sub) == 0: continue
        # Aggregate over seeds at each n
        agg = sub.groupby('n_events').agg(
            est_med=('estimate', 'median'),
            est_lo=('estimate', lambda x: np.percentile(x, 25)),
            est_hi=('estimate', lambda x: np.percentile(x, 75)),
            coverage=('covers', 'mean'),
            rel_err=('rel_err', 'median'),
        ).reset_index()
        truth = float(sub['truth'].iloc[0])
        ax.plot(agg['n_events'], agg['est_med'], 'C0o-', lw=2, ms=7,
                label='median estimate')
        ax.fill_between(agg['n_events'], agg['est_lo'], agg['est_hi'],
                         color='C0', alpha=0.2, label='IQR over seeds')
        ax.axhline(truth, color='C3', ls='--', lw=1, label=f'truth = {truth}')
        ax.set_xscale('log')
        ax.set_xlabel('n_events'); ax.set_ylabel('estimate')
        ax.set_title(f"{title} — recovery vs n_events")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    fig.suptitle('Phase 17 Tier 3 — recovery accuracy as function of sample size')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOTS, "49_phase17_recovery_curves.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/49_phase17_recovery_curves.png")

    # ─── Per-class minimum n recommendation ────────────────────────────────
    print("\n" + "=" * 110)
    print("Per-class minimum n_events for ≥80% CI coverage:")
    print("=" * 110)
    for cls, _, _ in classes:
        sub = df[df['cls'] == cls]
        if len(sub) == 0: continue
        per_n = sub.groupby('n_events')['covers'].mean()
        passing_n = per_n[per_n >= 0.80]
        if len(passing_n) > 0:
            print(f"  {cls:<16}  min n_events = {int(passing_n.index.min()):>5}  "
                  f"(coverage = {passing_n.iloc[0]*100:.0f}%)")
        else:
            print(f"  {cls:<16}  fails at all tested n  "
                  f"(max coverage = {per_n.max()*100:.0f}% at n={int(per_n.idxmax())})")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == '__main__':
    main()
