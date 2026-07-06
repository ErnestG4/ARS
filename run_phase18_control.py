"""
Phase 18 control validation — apply the surrogate panel to two synthetic
inputs whose ground-truth class is known:

  1. Poisson process (BL by construction).
  2. Wigner-GUE eigenvalue spacings (TR by construction).

Expected behavior under the higher-order falsification protocol:

  Poisson input  (BL):
    - phase_randomized_iei    → BL (preserves exp-IEI second-order
                                     structure that gives BL)
    - hawkes_matched          → BL (low branching ratio fitted →
                                     near-Poisson surrogate)
    - cumulant_matched        → BL (preserves first three IEI cumulants)

  Wigner-GUE input  (TR):
    - phase_randomized_iei    → TR (preserves IEI variance ≈ 0.45 which
                                     drives the TR classification)
    - hawkes_matched          → BL (Hawkes fit on a non-clustered
                                     sequence yields near-Poisson →
                                     classification flips to BL.  This
                                     is the discriminating surrogate.)
    - cumulant_matched        → TR (preserves marginal moments of the
                                     Wigner IEI distribution)

The Wigner control mirrors the arithmetic-finding pattern in Tier 3 (TR
input → IEI-preserving surrogates catch, hawkes flips to BL).  This
confirms that the arithmetic findings' surrogate response in Tier 3 is
the same as the surrogate response on a synthetic ground-truth Wigner
input — i.e., the catches reflect the joint-plane classifier's IEI-
marginal sensitivity, not finding artifacthood.
"""
from __future__ import annotations
import os, sys, time
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from signal_gen import make_beta_ensemble_eigenvalues
from surrogates import (
    phase_randomized_iei_events,
    hawkes_matched_events,
    cumulant_matched_events,
)


N_EVENTS = 4000
Q_MAX = 30
MIN_EVENTS = 30
N_SEEDS = 3


def primary_quadrant(events):
    if events.size < MIN_EVENTS:
        return 'underpowered', float('nan'), float('nan')
    j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return 'underpowered', float('nan'), float('nan')
    counts = well['quadrant'].value_counts()
    return (str(counts.idxmax()),
            float(well['rep_int_q'].median()),
            float(well['ks_gue_q'].median()))


SURROGATES = [
    ('phase_randomized_iei', phase_randomized_iei_events),
    ('hawkes_matched',       hawkes_matched_events),
    ('cumulant_matched',     cumulant_matched_events),
]


def gen_poisson(seed):
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.exponential(1.0, size=N_EVENTS))


def gen_wigner(seed):
    return make_beta_ensemble_eigenvalues(N_EVENTS, 2, seed)


def main():
    rows = []
    print("=" * 90)
    print("Phase 18 control validation — surrogates on Poisson and Wigner-GUE")
    print("=" * 90)
    for label, gen, expected in [
            ('poisson_iid',     gen_poisson, 'BL'),
            ('wigner_gue_n4k',  gen_wigner,  'TR'),
            ]:
        for seed in range(N_SEEDS):
            t = gen(seed)
            orig_q, orig_rep, orig_ks = primary_quadrant(t)
            print(f"\n  {label} seed={seed}  ORIGINAL  rep={orig_rep:.3f}  "
                  f"ks={orig_ks:.3f}  → {orig_q}  (expected {expected})")
            for name, fn in SURROGATES:
                rng = np.random.default_rng(seed * 1000 + abs(hash(name)) % 50000)
                surr = fn(t, rng=rng)
                surr_q, surr_rep, surr_ks = primary_quadrant(surr)
                catch = (surr_q == orig_q)
                rows.append(dict(
                    input=label, seed=seed, surrogate=name,
                    orig_quadrant=orig_q, orig_rep=orig_rep, orig_ks=orig_ks,
                    surr_quadrant=surr_q, surr_rep=surr_rep, surr_ks=surr_ks,
                    catch=catch))
                tag = 'CATCH' if catch else 'flip '
                print(f"    {name:<22}  surr rep={surr_rep:.3f}  ks={surr_ks:.3f}"
                      f"  → {surr_q:<12}  {tag}")
    df = pd.DataFrame(rows)
    out = os.path.join(THIS_DIR, 'data', 'phase18_control_validation.parquet')
    df.to_parquet(out)
    print(f"\n  → {out}  ({len(df)} rows)")

    # Summary
    print("\nSummary (catch fractions across {} seeds):".format(N_SEEDS))
    summary = (df.groupby(['input', 'surrogate'])
                 .agg(catch_rate=('catch', 'mean'))
                 .reset_index())
    print(summary.pivot(index='input', columns='surrogate',
                          values='catch_rate'))


if __name__ == '__main__':
    main()
