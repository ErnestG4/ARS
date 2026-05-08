"""
Phase 15 Tier 5 — Cross-domain joint_q_profile.

Apply joint_q_profile + joint_quadrant_diagnostic to every signal
class currently characterised by ARS, populate cross-signal table
with primary quadrant + BR_artifact / BR_novel fractions.

Signals re-run (subsampled to n=2000 where larger):
  - ζ first 2000 zeros (already cached as phase15_zeta_joint.parquet)
  - ζ heights ~10⁶ (last 2000 from zeros6)
  - LMFDB EC L-functions (pooled normalised inter-zero spacings)
  - Dirichlet L-functions (pooled normalised)
  - Primes ≤ 10⁶ (subsampled to 2000)
  - Twin primes ≤ 10⁷ (subsampled to 2000)
  - Adamatzky fungal spike pool (re-detected, ~1500 events)
  - USGS earthquakes M ≥ 4.5 (subsampled to 2000)
  - LLM residual-norm peaks pool (Qwen 2.5 3B fp16 natural stim)
  - Solar X-ray flares M+ (subsampled to 2000)
  - Binance BTCUSDT trades (subsampled to 2000)
  - Uniform-jitter=0.10 control (already in calibrator pool)

Output:
  data/phase15_cross_signal_joint.parquet
  plots/43_phase15_cross_signal_quadrants.png
"""
import os, sys, json, time, glob
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
N_TARGET = 2000
Q_MAX = 200
MIN_EVENTS = 30


def _subsample(t, n=N_TARGET):
    """Take every kth event to reach ~n total."""
    if t.size <= n: return t
    step = t.size // n
    return t[::step][:n]


def load_zeta_low():
    z = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"), max_rows=N_TARGET)
    return (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8


def load_zeta_high():
    """Last N_TARGET zeros from zeros6 (heights near 1.1M)."""
    full = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"))
    z = full[-N_TARGET:]
    return (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8


def _unfold_lfunc(zeros, conductor):
    z = np.asarray(zeros, dtype=np.float64)
    z = z[z > 0]
    if z.size < 2: return np.zeros(0)
    arg = np.maximum(conductor * z / (2*np.pi), 1.0)
    return (z / (2*np.pi)) * (np.log(arg) - 1.0)


def load_lmfdb_pool():
    p = os.path.join(DATA, "lmfdb_zeros.json")
    if not os.path.exists(p): return None
    curves = json.load(open(p))
    pool = []
    for c in curves:
        u = _unfold_lfunc(np.array(c.get('zeros', [])), c['conductor'])
        sp = np.diff(u)
        if sp.size and sp.mean() > 0:
            pool.append(sp / sp.mean())
    if not pool: return None
    return np.cumsum(np.concatenate(pool))[:N_TARGET * 5]   # cap


def load_dirichlet_pool():
    p = os.path.join(DATA, "dirichlet_zeros.json")
    if not os.path.exists(p): return None
    chars = json.load(open(p))
    pool = []
    for c in chars:
        u = _unfold_lfunc(np.array(c.get('zeros', [])), c['conductor'])
        sp = np.diff(u)
        if sp.size and sp.mean() > 0:
            pool.append(sp / sp.mean())
    if not pool: return None
    return np.cumsum(np.concatenate(pool))[:N_TARGET * 5]


def load_primes(N=10**6):
    sieve = np.ones(N + 1, dtype=bool); sieve[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if sieve[p]: sieve[p*p::p] = False
    primes = np.where(sieve)[0].astype(np.float64)
    unfolded = primes / np.log(np.maximum(primes, 2.0))
    return _subsample(unfolded)


def load_twin_primes(N=10**7):
    sieve = np.ones(N + 1, dtype=bool); sieve[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if sieve[p]: sieve[p*p::p] = False
    primes = np.where(sieve)[0]
    diffs = np.diff(primes)
    twins = primes[:-1][diffs == 2].astype(np.float64)
    unfolded = twins / np.log(np.maximum(twins, 2.0))
    return _subsample(unfolded)


def load_earthquakes():
    p = os.path.join(DATA, "usgs_M45_5yr.csv")
    if not os.path.exists(p): return None
    df = pd.read_csv(p, low_memory=False)
    times = pd.to_datetime(df['time'], utc=True, errors='coerce').dropna()
    secs = times.astype('int64').to_numpy() / 1e9
    secs = np.sort(secs)
    diffs = np.diff(secs); diffs = diffs[diffs > 0]
    if diffs.size == 0: return None
    return _subsample(np.cumsum(diffs / diffs.mean()))


def load_solar_M_plus():
    p = os.path.join(DATA, "solar_flares_plutino_1986_2023.csv")
    if not os.path.exists(p): return None
    df = pd.read_csv(p, low_memory=False)
    df['tstart'] = pd.to_datetime(df['tstart'], errors='coerce')
    df = df.dropna(subset=['tstart']).sort_values('tstart').reset_index(drop=True)
    df = df[df['cat'].isin(['M', 'X'])]
    if len(df) < 100: return None
    t_origin = df['tstart'].iloc[0]
    secs = (df['tstart'] - t_origin).dt.total_seconds().to_numpy()
    diffs = np.diff(secs); diffs = diffs[diffs > 0]
    return _subsample(np.cumsum(diffs / diffs.mean()))


def load_binance(day_files=None):
    if day_files is None:
        day_files = sorted(glob.glob(os.path.join(
            DATA, "binance/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2024-01-*.csv")))[:1]
    if not day_files: return None
    df = pd.read_csv(day_files[0],
                      names=['id','price','qty','quoteQty','time','isBM','isBest'],
                      header=None, dtype={'time': np.int64})
    secs = df['time'].to_numpy() / 1000.0
    secs = np.sort(secs)
    return _subsample(secs - secs[0])


def load_fungal_pool():
    """Re-detect spikes; pool normalised inter-spike intervals."""
    sys.path.insert(0, THIS_DIR)
    try:
        from run_fungal_nns import (load_fungal_csv, detect_spikes,
                                    THRESHOLDS, TARGET_LO, TARGET_HI, FUNGI_ROOT)
    except Exception:
        return None
    files = sorted(p for p in glob.glob(
        os.path.join(FUNGI_ROOT, '**', '*.csv'), recursive=True)
                    if 'Zone.Identifier' not in p)
    pool = []
    for f in files:
        try:
            df = load_fungal_csv(f)
        except Exception:
            continue
        t_arr = df.index.to_numpy()
        for ch in df.columns:
            v = df[ch].to_numpy(dtype=np.float64)
            chosen = None
            for thr in sorted(THRESHOLDS, reverse=True):
                sp = detect_spikes(t_arr, v, threshold_std=thr)
                if TARGET_LO <= sp.size <= TARGET_HI:
                    chosen = sp; break
                if chosen is None or abs(sp.size - 60) < abs(chosen.size - 60):
                    chosen = sp
            if chosen is not None and chosen.size >= 20:
                isi = np.diff(np.sort(chosen))
                if isi.size and isi.mean() > 0:
                    pool.append(isi / isi.mean())
    if not pool: return None
    return _subsample(np.cumsum(np.concatenate(pool)))


SIGNALS = [
    ('zeta_first_2000',   load_zeta_low),
    ('zeta_high_~1M',     load_zeta_high),
    ('lmfdb_EC_pool',     load_lmfdb_pool),
    ('dirichlet_pool',    load_dirichlet_pool),
    ('primes_le_10^6',    load_primes),
    ('twin_primes_le_10^7', load_twin_primes),
    ('fungal_pool',       load_fungal_pool),
    ('earthquakes_M45',   load_earthquakes),
    ('solar_flares_MX',   load_solar_M_plus),
    ('binance_BTCUSDT_d1', load_binance),
]


def main():
    t_start = time.time()
    print("=" * 110)
    print("Phase 15 Tier 5 — joint_q_profile across cross-domain signals")
    print("=" * 110)
    rows = []
    for name, loader in SIGNALS:
        t0 = time.time()
        try:
            t_k = loader()
        except Exception as e:
            print(f"  {name:<24} loader failed: {type(e).__name__}: {e}")
            continue
        if t_k is None or t_k.size < 100:
            print(f"  {name:<24} insufficient data (n={t_k.size if t_k is not None else 'None'})")
            continue
        n = t_k.size
        df = joint_q_profile(t_k, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
        df = joint_quadrant_diagnostic(df)
        df['signal_class'] = name
        rows.append(df)
        well = df[~df['underpowered']]
        primary = well['quadrant'].mode().iloc[0] if len(well) else 'underpowered'
        primary_pct = (well['quadrant'] == primary).mean() if len(well) else 0
        br_a = (well['quadrant'] == 'BR_artifact').mean() if len(well) else 0
        br_n = (well['quadrant'] == 'BR_novel').mean() if len(well) else 0
        elapsed = time.time() - t0
        print(f"  {name:<24} n={n:>6}  "
              f"rep_int={well['rep_int_q'].median():.3f}  "
              f"KS_GUE={well['ks_gue_q'].median():.3f}  "
              f"primary={primary:<14} ({primary_pct*100:>4.1f}%)  "
              f"BR_a={br_a*100:>4.1f}%  BR_novel={br_n*100:>4.1f}%  ⏱ {elapsed:.0f}s")

    if rows:
        pooled = pd.concat(rows, ignore_index=True)
        pooled.to_parquet(os.path.join(DATA, "phase15_cross_signal_joint.parquet"))
        print(f"\n  → data/phase15_cross_signal_joint.parquet ({len(pooled)} rows)")

        # Bar chart of quadrant occupancy fractions per signal
        well_pool = pooled[~pooled['underpowered']]
        fracs = (well_pool.groupby('signal_class')['quadrant']
                  .value_counts(normalize=True).unstack(fill_value=0))
        # Order quadrants for the bar chart
        order = [c for c in ['BL', 'TR', 'TL', 'BR_artifact', 'BR_novel', 'ambiguous']
                  if c in fracs.columns]
        fracs = fracs[order]
        fracs = fracs.loc[[s for s, _ in SIGNALS if s in fracs.index]]

        fig, ax = plt.subplots(figsize=(11, 6))
        bottom = np.zeros(len(fracs))
        colors = {'BL': '#7d7d7d', 'TR': '#1f77b4', 'TL': '#ff7f0e',
                   'BR_artifact': '#d62728', 'BR_novel': '#9467bd',
                   'ambiguous': '#bbbbbb'}
        for q in fracs.columns:
            ax.bar(fracs.index, fracs[q], bottom=bottom, label=q,
                   color=colors.get(q, '#aaaaaa'))
            bottom += fracs[q]
        ax.set_ylabel('quadrant occupancy fraction (well-powered q-bands)')
        ax.set_xticks(range(len(fracs.index)))
        ax.set_xticklabels(fracs.index, rotation=30, ha='right', fontsize=9)
        ax.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize=8)
        ax.set_title('Phase 15 Tier 5 — cross-signal joint-q quadrant occupancy')
        ax.set_ylim(0, 1.0)
        ax.grid(True, axis='y', alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "43_phase15_cross_signal_quadrants.png"), dpi=120)
        plt.close(fig)
        print(f"  → plots/43_phase15_cross_signal_quadrants.png")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == '__main__':
    main()
