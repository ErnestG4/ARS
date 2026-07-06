"""
Phase 14 — Binance BTCUSDT trade timing.

Apply arithmetic_toolkit.full_analysis to the millisecond-resolution
trade-timestamp point process from Binance spot BTCUSDT, 2024-01-01
through 2024-01-07 (~12M trades).

Three stratifications:
  1. full week pooled    (subsampled to ~1.2M = every 10th trade)
  2. buyer-maker split   (col 5 == True / False) — microstructure asymmetry
  3. per-day             (Mon..Sun) — day-of-week effect

The buyer-maker / seller-maker split is the headline: aggressive buys
hitting the ask vs aggressive sells hitting the bid.  If the two sides
have different universality classes that's a real microstructure
finding — one side regularly spaced (algorithmic, level-repelling),
the other clustered (reactive, super-Poisson).

Output:
    data/binance_results.json
    plots/41_binance.png
"""
import os, sys, json, time, glob
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import full_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
TRADES_DIR = os.path.join(DATA, "binance/spot/daily/trades/BTCUSDT")
SUBSAMPLE = 10  # keep every 10th trade

print(f"Loading Binance BTCUSDT 7-day trade dump from {TRADES_DIR} …")
files = sorted(glob.glob(os.path.join(TRADES_DIR, "BTCUSDT-trades-*.csv")))
print(f"  found {len(files)} daily files")

# Columns: id, price, qty, quoteQty, time, isBuyerMaker, isBestMatch
COL_NAMES = ['trade_id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch']
DTYPES = {'trade_id': np.int64, 'price': np.float64,
          'qty': np.float64, 'quoteQty': np.float64,
          'time': np.int64, 'isBuyerMaker': str, 'isBestMatch': str}

t0_load = time.time()
day_frames = []
for f in files:
    print(f"  reading {os.path.basename(f)} …")
    df = pd.read_csv(f, names=COL_NAMES, dtype=DTYPES, header=None)
    df['isBuyerMaker'] = (df['isBuyerMaker'] == 'True')
    day_frames.append(df)
df_all = pd.concat(day_frames, ignore_index=True)
del day_frames
df_all = df_all.sort_values('time').reset_index(drop=True)
df_all['t_sec'] = (df_all['time'] - df_all['time'].iloc[0]) / 1000.0
df_all['day'] = pd.to_datetime(df_all['time'], unit='ms', utc=True).dt.day
print(f"  loaded {len(df_all):,} trades, "
      f"span {df_all['t_sec'].iloc[-1] / 86400:.2f} days, "
      f"⏱ {time.time() - t0_load:.1f}s\n")


def _subsample(t, k=SUBSAMPLE):
    return t[::k] if t.size > 1000 else t


# 1. Full pooled
t_full = _subsample(df_all['t_sec'].to_numpy())

# 2. Buyer-maker split.
#    Binance: isBuyerMaker = True  → trade was a SELLER taker
#       (aggressive sell hit the bid; the buyer was passive on the book).
#    isBuyerMaker = False → BUYER taker (aggressive buy hit the ask).
t_seller_taker = _subsample(df_all.loc[df_all['isBuyerMaker'], 't_sec'].to_numpy())
t_buyer_taker  = _subsample(df_all.loc[~df_all['isBuyerMaker'], 't_sec'].to_numpy())

# 3. Per-day
day_streams = {}
for d in sorted(df_all['day'].unique()):
    day_t = df_all.loc[df_all['day'] == d, 't_sec'].to_numpy()
    day_streams[f'day_{int(d):02d}'] = _subsample(day_t)

strata = {
    'full_week_pooled':            t_full,
    'seller_taker (isBM=True)':    t_seller_taker,
    'buyer_taker  (isBM=False)':   t_buyer_taker,
    **day_streams,
}

print("=" * 130)
print(f"Phase 14 — Binance BTCUSDT fingerprint matrix  (subsample = every {SUBSAMPLE}th)")
print("=" * 130)
print(f"  {'stratum':<28}  {'n':>9}  {'best':<7}  "
      f"{'KS_GUE':>7}  {'KS_GOE':>7}  {'KS_P':>7}  "
      f"{'mass<.3':>7}  {'F(T=1)':>7}  {'F(T=5)':>7}  "
      f"{'rep_int':>7}  {'mean_dt_ms':>10}")
print("  " + "-" * 128)

results = {}
for name, t_k in strata.items():
    if t_k.size < 50:
        print(f"  {name:<28}  {t_k.size:>9}  insufficient")
        results[name] = dict(label=name, n_events=int(t_k.size), error='insufficient')
        continue
    t0_run = time.time()
    res = full_analysis(t_k, label=name, q_max=8, ramanujan_q_max=200,
                        pair_r_max=5.0, pair_n_bins=50)
    p = res['primary_nns']; pc = res['pair_correlation']; fan = res['fano_curve']
    fp = res['fingerprint_vector']
    mean_dt = float(np.diff(t_k).mean()) * 1000  # back to ms
    print(f"  {name:<28}  {res['n_events']:>9,}  {p['best']:<7}  "
          f"{p['ks_u']:>7.3f}  {p['ks_o']:>7.3f}  {p['ks_p']:>7.3f}  "
          f"{p['mass03']:>7.3f}  "
          f"{fan.get('F_at_1', float('nan')):>7.3f}  "
          f"{fan.get('F_at_5', float('nan')):>7.3f}  "
          f"{pc.get('repulsion_integral', 0):>7.3f}  "
          f"{mean_dt:>9.1f}    [⏱ {time.time() - t0_run:.1f}s]")
    results[name] = res


def _trim(res):
    if 'error' in res: return res
    return dict(label=res['label'], n_events=res['n_events'],
                primary_nns=res['primary_nns'],
                fingerprint_vector=res['fingerprint_vector'],
                fano_summary={k: res['fano_curve'].get(k)
                              for k in ('F_at_1', 'F_at_5', 'F_at_20',
                                        'mean_sp', 'duration')},
                ramanujan_summary={k: res['ramanujan'].get(k)
                                   for k in ('peak_q', 'top10_q',
                                             'top10_amplitudes', 'mode')},
                pair_correlation_summary={k: res['pair_correlation'].get(k)
                                          for k in ('R2_at_0_1', 'R2_at_0_5',
                                                    'R2_at_1', 'repulsion_integral')},
                sb_split_summary=res['sb_split'],
                padic_summary=dict(dominant_prime=res['padic_profile']['dominant_prime'],
                                   best_by_prime=res['padic_profile']['best_by_prime']))

with open(os.path.join(DATA, "binance_results.json"), 'w') as f:
    json.dump({k: _trim(v) for k, v in results.items()}, f,
              indent=2, default=str)
print(f"\n  → data/binance_results.json")


# ─── Plot ────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
keys = ['KS_GUE', 'KS_GOE', 'KS_P', 'mass<.3', 'F(1)', 'F(5)', 'rep_int',
        'top_q', 'sb_KS', 'p_dom']
labels = [k for k, v in results.items() if 'fingerprint_vector' in v]
M = np.array([results[k]['fingerprint_vector'] for k in labels])
col_min = np.nanmin(M, axis=0); col_max = np.nanmax(M, axis=0)
rng = np.where(col_max > col_min, col_max - col_min, 1.0)
Mn = (M - col_min) / rng
im = ax.imshow(Mn, aspect='auto', cmap='RdBu_r', vmin=0, vmax=1)
ax.set_xticks(range(len(keys)), labels=keys, rotation=45, ha='right', fontsize=8)
ax.set_yticks(range(len(labels)), labels=labels, fontsize=8)
for i in range(len(labels)):
    for j in range(len(keys)):
        v = M[i, j]; vn = Mn[i, j]
        ax.text(j, i, f"{v:.2f}", ha='center', va='center', fontsize=6,
                color='white' if abs(vn - 0.5) > 0.32 else 'black')
ax.set_title('Phase 14: Binance BTCUSDT fingerprint matrix')

ax = axes[1]
xs_pos = np.arange(len(labels))
ks_u = [results[k]['fingerprint_vector'][0] for k in labels]
mass03 = [results[k]['fingerprint_vector'][3] for k in labels]
fan5 = [results[k]['fingerprint_vector'][5] for k in labels]
w = 0.27
ax.bar(xs_pos - w, ks_u, width=w, color='C0', label='KS_GUE')
ax.bar(xs_pos + 0,  mass03, width=w, color='C1', label='mass<0.3')
ax.bar(xs_pos + w, fan5, width=w, color='C2', label='F(T=5)')
ax.set_xticks(xs_pos, labels=labels, rotation=30, ha='right', fontsize=7)
ax.set_ylabel('value')
ax.set_title('Per-stratum scalars')
ax.grid(True, alpha=0.3); ax.legend(fontsize=8)

fig.suptitle('Phase 14 — Binance spot BTCUSDT trade timing, 2024-01-01..07')
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "41_binance.png"), dpi=120)
plt.close(fig)
print(f"  → plots/41_binance.png")
