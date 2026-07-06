"""
Phase 16 Tier 1 — Boundary-extractor invariance matrix.

For each (signal, extractor) cell, run extractor → joint_q_profile →
joint_quadrant_diagnostic, record primary quadrant + occupancy fractions.
Diagonal = direct_events (ground truth); off-diagonal cells encode
"extractor X reads signal Y as quadrant Z."

Output:
  data/phase16_invariance_matrix.parquet
  plots/44_phase16_invariance_heatmap.png
"""
import os, sys, json, time
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from extractors import EXTRACTORS, extract
from signal_gen import (
    make_beta_ensemble_eigenvalues, make_uniform_jitter,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
N_TARGET = 1000   # smaller than Phase 15 (2000) to keep matrix runtime manageable
Q_MAX = 50         # truncated from 200 — quadrant signature settles by q=50
MIN_EVENTS = 30


def _poisson(seed=0): rng = np.random.default_rng(seed); return np.cumsum(rng.exponential(1.0, size=N_TARGET))
def _gue(seed=0):     return make_beta_ensemble_eigenvalues(N_TARGET, 2, seed)
def _periodic_q7(seed=0):
    rng = np.random.default_rng(seed)
    return np.sort(np.arange(1, N_TARGET + 1, dtype=np.float64) * 7.0
                    + 0.05 * rng.standard_normal(N_TARGET))
def _ujit(seed=0):    return make_uniform_jitter(N_TARGET, 0.10, seed)
def _zeta_low():
    z = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"), max_rows=N_TARGET)
    return (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8

def _primes(N=10**6):
    sieve = np.ones(N + 1, dtype=bool); sieve[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if sieve[p]: sieve[p*p::p] = False
    primes = np.where(sieve)[0].astype(np.float64)
    unfolded = primes / np.log(np.maximum(primes, 2.0))
    step = unfolded.size // N_TARGET
    return unfolded[::max(1, step)][:N_TARGET]

def _twin_primes(N=10**7):
    sieve = np.ones(N + 1, dtype=bool); sieve[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if sieve[p]: sieve[p*p::p] = False
    primes = np.where(sieve)[0]
    diffs = np.diff(primes)
    twins = primes[:-1][diffs == 2].astype(np.float64)
    unfolded = twins / np.log(np.maximum(twins, 2.0))
    step = unfolded.size // N_TARGET
    return unfolded[::max(1, step)][:N_TARGET]


def _lmfdb_pool():
    p = os.path.join(DATA, "lmfdb_zeros.json")
    if not os.path.exists(p): return None
    curves = json.load(open(p))
    pool = []
    for c in curves:
        z = np.asarray(c.get('zeros', []), dtype=np.float64)
        z = z[z > 0]
        if z.size < 2: continue
        cond = c['conductor']
        arg = np.maximum(cond * z / (2*np.pi), 1.0)
        u = (z / (2*np.pi)) * (np.log(arg) - 1.0)
        sp = np.diff(u)
        if sp.size and sp.mean() > 0:
            pool.append(sp / sp.mean())
    if not pool: return None
    return np.cumsum(np.concatenate(pool))[:N_TARGET]


SIGNALS = [
    ('zeta_first',      _zeta_low,        'TR'),
    ('beta=2_GUE',      lambda: _gue(0),  'TR'),
    ('poisson',         lambda: _poisson(0), 'BL'),
    ('periodic_q7',     lambda: _periodic_q7(0), 'TL'),
    ('uniform_jitter',  lambda: _ujit(0), 'BR_artifact'),
    ('primes_le_10^6',  _primes,          'BR_artifact'),
    ('twin_primes',     _twin_primes,     'BR_artifact'),
    ('lmfdb_EC_pool',   _lmfdb_pool,      'TR'),
]

EXTRACTORS_LIST = list(EXTRACTORS.keys())


def main():
    t_start = time.time()
    print("=" * 110)
    print(f"Phase 16 Tier 1 — invariance matrix at n={N_TARGET}, q_max={Q_MAX}")
    print(f"  signals: {len(SIGNALS)}, extractors: {len(EXTRACTORS_LIST)}")
    print(f"  total cells: {len(SIGNALS) * len(EXTRACTORS_LIST)}")
    print("=" * 110)

    rows = []
    for sig_name, gen, expected_quad in SIGNALS:
        try:
            t_k = gen()
        except Exception as e:
            print(f"  {sig_name:<20} loader failed: {e}")
            continue
        if t_k is None or t_k.size < 100:
            print(f"  {sig_name:<20} insufficient data")
            continue
        for ext_name in EXTRACTORS_LIST:
            t0 = time.time()
            try:
                t_out = extract(t_k, ext_name)
            except Exception as e:
                print(f"  {sig_name:<20} {ext_name:<24} extractor failed: {e}")
                continue
            if t_out is None or t_out.size < 100:
                print(f"  {sig_name:<20} {ext_name:<24} too few events: {t_out.size if t_out is not None else 'None'}")
                rows.append(dict(signal=sig_name, expected=expected_quad,
                                  extractor=ext_name, n_out=int(t_out.size if t_out is not None else 0),
                                  primary_quadrant='underpowered',
                                  primary_pct=0.0,
                                  rep_int_med=np.nan,
                                  ks_gue_med=np.nan,
                                  br_a_pct=np.nan, br_n_pct=np.nan,
                                  tl_pct=np.nan, tr_pct=np.nan, bl_pct=np.nan,
                                  elapsed_s=time.time() - t0))
                continue
            # joint_q_profile + quadrant
            df = joint_q_profile(t_out, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
            df = joint_quadrant_diagnostic(df)
            well = df[~df['underpowered']]
            if len(well) == 0:
                primary, primary_pct = 'underpowered', 0.0
                rep_med = ks_med = np.nan
                br_a = br_n = tl = tr = bl = np.nan
            else:
                vc = well['quadrant'].value_counts(normalize=True)
                primary = vc.idxmax()
                primary_pct = float(vc.max())
                rep_med = float(well['rep_int_q'].median())
                ks_med = float(well['ks_gue_q'].median())
                br_a = float(vc.get('BR_artifact', 0.0))
                br_n = float(vc.get('BR_novel', 0.0))
                tl = float(vc.get('TL', 0.0))
                tr = float(vc.get('TR', 0.0))
                bl = float(vc.get('BL', 0.0))
            elapsed = time.time() - t0
            rows.append(dict(signal=sig_name, expected=expected_quad,
                              extractor=ext_name,
                              n_out=int(t_out.size),
                              primary_quadrant=primary,
                              primary_pct=primary_pct,
                              rep_int_med=rep_med,
                              ks_gue_med=ks_med,
                              br_a_pct=br_a, br_n_pct=br_n,
                              tl_pct=tl, tr_pct=tr, bl_pct=bl,
                              elapsed_s=elapsed))
            mark = '✓' if primary == expected_quad else (
                '~' if (primary.startswith('BR') and expected_quad.startswith('BR'))
                       or (primary == 'TL' and expected_quad == 'TL')
                else '✗')
            print(f"  {sig_name:<20} {ext_name:<24} n_out={t_out.size:>5}  "
                  f"primary={primary:<14} ({primary_pct*100:>4.1f}%)  "
                  f"rep_int={rep_med:.3f}  KS_GUE={ks_med:.3f}  "
                  f"expected={expected_quad:<14}  {mark}  ⏱ {elapsed:.0f}s")

    df_pool = pd.DataFrame(rows)
    df_pool.to_parquet(os.path.join(DATA, "phase16_invariance_matrix.parquet"))
    print(f"\n  → data/phase16_invariance_matrix.parquet ({len(df_pool)} rows)")

    # ─── Heatmap visualization ──────────────────────────────────────────────
    sig_order = [s[0] for s in SIGNALS]
    ext_order = EXTRACTORS_LIST
    M = pd.pivot_table(df_pool, index='signal', columns='extractor',
                        values='primary_quadrant', aggfunc='first')
    # Reorder
    M = M.reindex(index=sig_order, columns=ext_order)

    # Encode quadrants as integers for the heatmap
    quad_to_int = {'BL': 0, 'TR': 1, 'TL': 2, 'BR_artifact': 3,
                    'BR_novel': 4, 'ambiguous': 5, 'underpowered': 6}
    M_int = M.replace(quad_to_int).astype(float)
    fig, ax = plt.subplots(figsize=(11, 7))
    im = ax.imshow(M_int.to_numpy(), aspect='auto', cmap='tab10', vmin=0, vmax=9)
    ax.set_xticks(range(len(ext_order)), labels=ext_order, rotation=30, ha='right')
    ax.set_yticks(range(len(sig_order)), labels=sig_order)
    for i, sig in enumerate(sig_order):
        for j, ext in enumerate(ext_order):
            v = M.iloc[i, j] if pd.notna(M.iloc[i, j]) else '-'
            ax.text(j, i, str(v).replace('BR_artifact', 'BR_a'),
                    ha='center', va='center', fontsize=7,
                    color='white')
    # mark expected quadrant per row
    for i, (sig, _, exp) in enumerate(SIGNALS):
        ax.text(-0.5, i, f'expect: {exp}', ha='right', va='center',
                 fontsize=7, color='gray')
    ax.set_title('Phase 16 Tier 1 — invariance matrix (signal × extractor → primary quadrant)')
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "44_phase16_invariance_heatmap.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/44_phase16_invariance_heatmap.png")

    # ─── Acceptance check ──────────────────────────────────────────────────
    print("\n" + "=" * 110)
    print("ACCEPTANCE CHECK")
    print("=" * 110)
    for sig, gen, exp in SIGNALS:
        sub = df_pool[df_pool['signal'] == sig]
        match_count = (sub['primary_quadrant'] == exp).sum()
        # for periodic, accept BR_artifact + TL spike pattern
        if exp == 'TL':
            match_count = ((sub['primary_quadrant'] == 'BR_artifact') |
                            (sub['primary_quadrant'] == 'TL')).sum()
        n = len(sub)
        print(f"  {sig:<20} expected {exp:<14}: matched on {match_count}/{n} extractors")

    # Per-extractor consistency: how often does each extractor land on expected?
    print("\n  Per-extractor agreement with expected ground-truth quadrant:")
    for ext in EXTRACTORS_LIST:
        sub = df_pool[df_pool['extractor'] == ext]
        # for periodic, accept BR_artifact + TL spike pattern
        match = 0
        for _, row in sub.iterrows():
            if row['primary_quadrant'] == row['expected']:
                match += 1
            elif row['expected'] == 'TL' and row['primary_quadrant'] in {'BR_artifact', 'TL'}:
                match += 1
        print(f"    {ext:<24} {match}/{len(sub)}")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == '__main__':
    main()
