"""
p-adic engine validation — financial settlement-cycle test.

The Phase-9 limitation note (RESULTS.md §7.ter.8) records that the p-adic
engine sees no signal on the L-function arithmetic block: bulk Wigner GUE
universality smooths over per-prime asymmetry there.  The engine is
*expected* to fire on signals with calendar / settlement-cycle structure,
where weekly = 7, monthly ≈ 30 = 2·3·5, quarterly ≈ 91 = 7·13.

This script does two things:

  1. If `data/financial_settlements.csv` exists (a single column of
     timestamps in seconds or ISO-8601), runs `full_analysis` on the
     timestamps and reports per-prime KS_min.

  2. Otherwise, generates four synthetic settlement-style signals with
     known structure and runs the same analysis as a sanity-check:

       (a) pure weekly periodic + jitter        → expected: peak_q = 7,
                                                   p = 7 KS_min low
       (b) pure monthly periodic + jitter       → expected: peak_q ≈ 30,
                                                   p ∈ {2,3,5} KS_min low
       (c) mixed weekly+monthly+quarterly       → expected: multi-prime
                                                   activation
       (d) Poisson background with injected     → expected: p = 7 KS_min
           weekly settlements (signal+noise)      *worse* than others
                                                   (asymmetry diagnostic)

Output:
    data/padic_finance_results.json
    plots/34_padic_finance.png   (if synthetic, per-prime KS panels)
"""
import os, sys, json, time
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
Q_MAX = 16
SPAN_DAYS = 1825   # 5 years


def gen_periodic(period_days, jitter_days, span=SPAN_DAYS, seed=0):
    """Periodic events with Gaussian jitter, returned as days since t=0."""
    rng = np.random.default_rng(seed)
    n = int(span / period_days)
    base = (np.arange(1, n + 1) * period_days)
    events = base + rng.normal(0, jitter_days, size=n)
    return np.sort(events[(events > 0) & (events < span)])


def gen_poisson_with_injection(rate_per_day, period_days, jitter_days,
                                span=SPAN_DAYS, seed=1):
    """Poisson background + injected periodic component (signal in noise)."""
    rng = np.random.default_rng(seed)
    n_bg = rng.poisson(rate_per_day * span)
    bg = np.sort(rng.uniform(0, span, size=n_bg))
    inj = gen_periodic(period_days, jitter_days, span=span, seed=seed + 100)
    return np.sort(np.concatenate([bg, inj]))


def normalize_to_unit_mean(t):
    sp = np.diff(t)
    if sp.size == 0 or sp.mean() <= 0: return np.zeros(0)
    return np.cumsum(sp / sp.mean())


# ─── Real data path (if available) ────────────────────────────────────────────

real_csv = os.path.join(DATA, "financial_settlements.csv")
if os.path.exists(real_csv):
    print(f"Found real data: {real_csv}")
    df = pd.read_csv(real_csv, low_memory=False)
    col = df.columns[0]
    try:
        t = pd.to_datetime(df[col], utc=True, errors='coerce').dropna()
        secs = t.astype('int64').to_numpy() / 1e9
    except Exception:
        secs = pd.to_numeric(df[col], errors='coerce').dropna().to_numpy()
    secs = np.sort(secs)
    diffs = np.diff(secs)
    diffs = diffs[diffs > 0]
    if diffs.size < 50:
        print("  too few events — falling through to synthetic demo")
        t_input = None
    else:
        t_input = np.cumsum(diffs / diffs.mean())
        print(f"  loaded {secs.size:,} events, mean Δt = {diffs.mean()/86400:.2f} days")
else:
    t_input = None
    print(f"(no real data at {real_csv} — running synthetic demo)")

print()


# ─── Synthetic suite ─────────────────────────────────────────────────────────

print("=" * 110)
print(f"Synthetic settlement-cycle p-adic engine validation (q_max={Q_MAX})")
print("=" * 110)

cases = [
    ('(a) weekly periodic',
        gen_periodic(period_days=7,  jitter_days=0.5)),
    ('(b) monthly periodic',
        gen_periodic(period_days=30, jitter_days=2)),
    ('(c) quarterly periodic',
        gen_periodic(period_days=91, jitter_days=4)),
    ('(d) mixed (W+M+Q)',
        np.sort(np.concatenate([
            gen_periodic(7,  0.5, seed=1),
            gen_periodic(30, 2.0, seed=2),
            gen_periodic(91, 4.0, seed=3)]))),
    ('(e) Poisson + weekly injection',
        gen_poisson_with_injection(rate_per_day=0.5, period_days=7,
                                     jitter_days=0.5)),
    ('(f) Poisson background only',
        np.sort(np.random.default_rng(99).uniform(0, SPAN_DAYS,
                                                    size=int(SPAN_DAYS * 0.6)))),
]

results = {}
for label, raw in cases:
    if raw.size < 50:
        print(f"  {label}: insufficient ({raw.size})")
        continue
    t_unit = normalize_to_unit_mean(raw)
    res = full_analysis(t_unit, label=label, q_max=Q_MAX)
    results[label] = res
    p = res['primary_nns']
    pa = res['padic_profile']
    r = res['ramanujan']
    bp = pa.get('best_by_prime', {})
    print(f"\n[{label}]  n={res['n_events']:,}  best={p['best']}  "
          f"KS_GUE={p['ks_u']:.3f}  mass<0.3={p['mass03']:.3f}")
    print(f"   peak_q={r.get('peak_q', 0)}   "
          f"top10_q={r.get('top10_q', [])[:5]}…")
    print("   p-adic KS_min by prime:  " +
          "  ".join(f"p={pp}: {b.get('ks_min', 1):.3f}" for pp, b in bp.items()))


# ─── Real-data path ──────────────────────────────────────────────────────────

if t_input is not None:
    res_real = full_analysis(t_input, label='real_settlements', q_max=Q_MAX)
    results['real_settlements'] = res_real
    p = res_real['primary_nns']; pa = res_real['padic_profile']
    bp = pa.get('best_by_prime', {})
    print("\n" + "=" * 110)
    print("REAL settlement data")
    print("=" * 110)
    print(f"  n={res_real['n_events']:,}  best={p['best']}  "
          f"KS_GUE={p['ks_u']:.3f}  mass<0.3={p['mass03']:.3f}")
    print(f"  peak_q={res_real['ramanujan'].get('peak_q', 0)}")
    print("  p-adic KS_min by prime:  " +
          "  ".join(f"p={pp}: {b.get('ks_min', 1):.3f}" for pp, b in bp.items()))


# ─── Save JSON ────────────────────────────────────────────────────────────────

def _trim(res):
    return dict(label=res.get('label', '?'),
                n_events=res.get('n_events', 0),
                primary_nns=res.get('primary_nns', {}),
                fingerprint_vector=res.get('fingerprint_vector', []),
                padic_summary={'dominant_prime': res['padic_profile']['dominant_prime'],
                                'best_by_prime': res['padic_profile']['best_by_prime']},
                ramanujan_summary={'peak_q': res['ramanujan']['peak_q'],
                                    'top10_q': res['ramanujan']['top10_q']})


with open(os.path.join(DATA, "padic_finance_results.json"), 'w') as f:
    json.dump({k: _trim(v) for k, v in results.items()}, f, indent=2, default=str)
print(f"\n  → data/padic_finance_results.json")


# ─── Plot per-prime KS profile ────────────────────────────────────────────────

primes = (2, 3, 5, 7, 11, 13)
fig, ax = plt.subplots(figsize=(11, 5.5))
for label, res in results.items():
    bp = res['padic_profile']['best_by_prime']
    y = [bp.get(p, {}).get('ks_min', np.nan) for p in primes]
    ax.plot(primes, y, 'o-', lw=1.7, ms=7, label=label)
ax.set_xlabel('prime p (p-adic engine selector)')
ax.set_ylabel('KS_min  (lower = closer to a Wigner reference)')
ax.set_xticks(primes)
ax.set_title("p-adic engine: per-prime KS_min on settlement-cycle synthetics")
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8, loc='best')
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "34_padic_finance.png"), dpi=120)
plt.close(fig)
print(f"  → plots/34_padic_finance.png")
