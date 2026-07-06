"""
p-adic engine v3 acceptance test — per-band Wigner-fit table.

The v2 redesign (pure-p-power filter + pooling) failed because pooling
across each disjoint per-prime subset still washes out the prime-base
asymmetry — the pooled NNS converges to the same shape regardless of
the prime selector.

v3 keeps the pure-p-power filter but stops pooling.  It classifies
each Farey rational (a, q) individually and reports a (p, q_p) table
of *median* per-band KS scores at q_max = 64 (so each prime p ≤ 7
gets at least two q_p values to compare).

Acceptance criterion (per user spec):
    On Poisson + period-7 injection, median KS_GUE at the (p=7, q=7)
    cell should be visibly elevated relative to the (p=2, q=2..64)
    cells that see only the Poisson background.

Output:
    data/padic_v3_results.json
    plots/35_padic_v3.png
"""
import os, sys, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import padic_per_band
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
SPAN_DAYS = 1825
Q_MAX = 64
PRIMES = (2, 3, 5, 7, 11, 13)


def gen_periodic(period_days, jitter_days, span=SPAN_DAYS, seed=0):
    rng = np.random.default_rng(seed)
    n = int(span / period_days)
    base = (np.arange(1, n + 1) * period_days)
    events = base + rng.normal(0, jitter_days, size=n)
    return np.sort(events[(events > 0) & (events < span)])


def gen_poisson(rate_per_day, span=SPAN_DAYS, seed=1):
    rng = np.random.default_rng(seed)
    n = rng.poisson(rate_per_day * span)
    return np.sort(rng.uniform(0, span, size=n))


def gen_poisson_plus_periodic(rate_per_day, period_days, jitter_days,
                                span=SPAN_DAYS, seed=2):
    bg = gen_poisson(rate_per_day, span, seed)
    inj = gen_periodic(period_days, jitter_days, span, seed=seed + 100)
    return np.sort(np.concatenate([bg, inj]))


# ─── Acceptance suite ────────────────────────────────────────────────────────

cases = [
    ('Poisson background only',                  gen_poisson(rate_per_day=0.5)),
    ('Poisson + period-7 inject (acceptance)',   gen_poisson_plus_periodic(0.5, 7, 0.5)),
    ('Poisson + period-3 inject (control)',      gen_poisson_plus_periodic(0.5, 3, 0.2)),
    ('Poisson + period-5 inject (control)',      gen_poisson_plus_periodic(0.5, 5, 0.3)),
    ('Pure weekly periodic',                      gen_periodic(7, 0.5)),
]

results = {}
for label, t in cases:
    if t.size < 50:
        print(f"  {label}: insufficient ({t.size})")
        continue
    print("\n" + "=" * 110)
    print(f"  {label}   n_events={t.size}")
    print("=" * 110)
    res = padic_per_band(t, primes=PRIMES, q_max=Q_MAX, fc_ref=1.0)
    table = res['per_band_table']
    results[label] = res

    # Print per-prime per-q table
    print(f"  {'p':>3}  {'q':>3}  {'n_bands':>7}  {'med_n':>5}  "
          f"{'med_KS_P':>8}  {'med_KS_O':>8}  {'med_KS_U':>8}  "
          f"{'med_m<.3':>8}")
    for p, rows in table.items():
        for r in rows:
            mark = "  ⬅ q=p" if r['q'] == p else ""
            print(f"  {p:>3}  {r['q']:>3}  {r['n_bands']:>7}  "
                  f"{r['median_n']:>5}  "
                  f"{r['median_ks_p']:>8.3f}  "
                  f"{r['median_ks_o']:>8.3f}  "
                  f"{r['median_ks_u']:>8.3f}  "
                  f"{r['median_mass03']:>8.3f}{mark}")


# ─── Acceptance check ────────────────────────────────────────────────────────

print("\n" + "=" * 110)
print("ACCEPTANCE CHECK")
print("=" * 110)
acc = results.get('Poisson + period-7 inject (acceptance)')
if acc:
    table = acc['per_band_table']

    def median_ksu_at(p_target, q_target):
        rows = table.get(p_target, [])
        for r in rows:
            if r['q'] == q_target: return r['median_ks_u']
        return None

    p7q7 = median_ksu_at(7, 7)
    p2q2 = median_ksu_at(2, 2)
    p2q4 = median_ksu_at(2, 4)
    p2q8 = median_ksu_at(2, 8)
    p2q16 = median_ksu_at(2, 16)
    p2q32 = median_ksu_at(2, 32)
    p2q64 = median_ksu_at(2, 64)

    p2_baseline = np.nanmedian([x for x in [p2q2, p2q4, p2q8, p2q16, p2q32, p2q64]
                                  if x is not None])
    print(f"\n  Poisson + period-7 injection:")
    print(f"    median KS_GUE @ (p=7, q=7):     {p7q7}")
    print(f"    median KS_GUE @ (p=2, q=2..64): {p2_baseline:.4f}  (across q in 2,4,8,16,32,64)")
    if p7q7 is not None and p2_baseline is not None:
        ratio = p7q7 / p2_baseline if p2_baseline > 0 else float('inf')
        diff = p7q7 - p2_baseline
        print(f"    elevation: KS_GUE(p=7,q=7) − KS_GUE(p=2 baseline) = {diff:+.4f}  "
              f"(ratio = {ratio:.2f}×)")
        if diff > 0.05:
            print(f"\n  ✓ ACCEPTANCE PASSED  (KS_GUE@p7q7 elevated by {diff:+.3f} over p=2 baseline)")
        else:
            print(f"\n  ✗ ACCEPTANCE FAILED  (KS_GUE@p7q7 not elevated over p=2 baseline)")


# ─── Save JSON ───────────────────────────────────────────────────────────────

def _trim(res):
    """Drop the per-band detail; keep cell summaries."""
    out = {}
    for p, rows in res['per_band_table'].items():
        out[p] = [{k: v for k, v in r.items() if k != 'bands'} for r in rows]
    return dict(per_band_table=out, q_max=res['q_max'],
                filter_mode=res['filter_mode'])


with open(os.path.join(DATA, "padic_v3_results.json"), 'w') as f:
    json.dump({k: _trim(v) for k, v in results.items()}, f, indent=2, default=str)
print(f"\n  → data/padic_v3_results.json")


# ─── Plot heatmap ────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, len(results), figsize=(4 * len(results), 5),
                         sharey=True)
if len(results) == 1: axes = [axes]
for ax, (label, res) in zip(axes, results.items()):
    table = res['per_band_table']
    # Build (p, q) grid of median_ks_u
    rows_p = sorted(table.keys())
    qs = sorted({r['q'] for rows in table.values() for r in rows})
    grid = np.full((len(rows_p), len(qs)), np.nan)
    for i, p in enumerate(rows_p):
        for r in table[p]:
            j = qs.index(r['q'])
            grid[i, j] = r['median_ks_u']
    im = ax.imshow(grid, aspect='auto', cmap='RdBu_r',
                   vmin=0, vmax=max(0.5, np.nanmax(grid)))
    ax.set_xticks(range(len(qs)), labels=qs, fontsize=7)
    ax.set_yticks(range(len(rows_p)), labels=[f"p={p}" for p in rows_p], fontsize=8)
    for i in range(len(rows_p)):
        for j in range(len(qs)):
            v = grid[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha='center', va='center',
                        fontsize=7,
                        color='white' if v > 0.3 else 'black')
    ax.set_title(label[:34], fontsize=9)
    ax.set_xlabel("q (pure-power of p)")
fig.suptitle(f"p-adic v3: median KS_GUE per (p, q_p) cell, q_max = {Q_MAX}",
             fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "35_padic_v3.png"), dpi=120)
plt.close(fig)
print(f"  → plots/35_padic_v3.png")
