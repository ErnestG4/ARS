"""
p-adic engine v4 acceptance test — Ramanujan-Fourier-amplitude based.

Side-steps the band-invariance pathology that killed v1-v3: detection
happens in the RF spectrum (which is sensitive to *which integers*
events align with) rather than in PLL passage NNS (which is invariant
under linear time scaling for stationary signals).

Acceptance criterion: on Poisson + period-7 injection, normalized
p_amplitude(7) should be visibly higher than p_amplitude(2,3,5,11,13);
ratio p_amplitude(7) / mean(p_amplitude(2,3,5,11,13)) should be » 1
for the period-7 case and ≈ 1 for pure Poisson background.

Output:
    data/padic_v4_results.json
    plots/36_padic_v4.png
"""
import os, sys, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import padic_amplitude_v4
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
SPAN_DAYS = 1825
Q_MAX = 200
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


# ─── Suite ───────────────────────────────────────────────────────────────────

cases = [
    ('Poisson background only',                gen_poisson(0.5)),
    ('Poisson + period-3 inject',              gen_poisson_plus_periodic(0.5, 3, 0.2)),
    ('Poisson + period-5 inject',              gen_poisson_plus_periodic(0.5, 5, 0.3)),
    ('Poisson + period-7 inject (acceptance)', gen_poisson_plus_periodic(0.5, 7, 0.5)),
    ('Poisson + period-11 inject',             gen_poisson_plus_periodic(0.5, 11, 0.5)),
    ('Poisson + period-13 inject',             gen_poisson_plus_periodic(0.5, 13, 0.5)),
    ('Pure weekly periodic',                    gen_periodic(7, 0.5)),
]

results = {}
print("=" * 130)
print(f"  p-adic v4 (RF-amplitude based) acceptance suite, q_max={Q_MAX}")
print("=" * 130)
print("  ── Metric 1: SUM-normalised (per spec) — sum |a_q| over q∈{p,p²,…} / total power")
print(f"  {'signal':<46}  " + "  ".join(f"p={p:>2}".rjust(8) for p in PRIMES) +
      "    dom    ratio7/mean(others)")
for label, t in cases:
    if t.size < 50:
        print(f"  {label:<46}: insufficient ({t.size})")
        continue
    res = padic_amplitude_v4(t, primes=PRIMES, q_max=Q_MAX)
    results[label] = res
    pp = res['per_prime']
    cells = "  ".join(f"{pp[p]['normalised']:>8.3f}" for p in PRIMES)
    others = [pp[p]['normalised'] for p in PRIMES if p != 7]
    mean_others = float(np.mean(others))
    ratio = pp[7]['normalised'] / mean_others if mean_others > 0 else float('inf')
    dom = res.get('dominant_prime', 0)
    print(f"  {label:<46}  {cells}    p={dom:<2}    {ratio:>6.2f}×")

print("\n  ── Metric 2: PER-Q-POWER-normalised — mean |a_q| over q∈{p,p²,…} / global mean")
print(f"  {'signal':<46}  " + "  ".join(f"p={p:>2}".rjust(8) for p in PRIMES) +
      "    dom    ratio7/mean(others)")
for label, t in cases:
    res = results.get(label)
    if not res: continue
    pp = res['per_prime']
    cells = "  ".join(f"{pp[p]['normalised_per_q']:>8.3f}" for p in PRIMES)
    others = [pp[p]['normalised_per_q'] for p in PRIMES if p != 7]
    mean_others = float(np.mean(others))
    ratio = pp[7]['normalised_per_q'] / mean_others if mean_others > 0 else float('inf')
    dom = res.get('dominant_prime_per_q', 0)
    print(f"  {label:<46}  {cells}    p={dom:<2}    {ratio:>6.2f}×")


# ─── Acceptance check ────────────────────────────────────────────────────────

print("\n" + "=" * 110)
print("ACCEPTANCE CHECK")
print("=" * 110)

target = results.get('Poisson + period-7 inject (acceptance)')
control = results.get('Poisson background only')

if target and control:
    pp_t = target['per_prime']; pp_c = control['per_prime']

    def _ratios(res, key):
        pp = res['per_prime']
        a7 = pp[7][key]
        others = float(np.mean([pp[p][key] for p in PRIMES if p != 7]))
        return a7, others, (a7 / others if others > 0 else float('inf'))

    for metric, key, dom_key in [
        ('sum-normalised  (per spec)', 'normalised', 'dominant_prime'),
        ('per-q-power-normalised', 'normalised_per_q', 'dominant_prime_per_q'),
    ]:
        a7_t, oth_t, ratio_t = _ratios(target, key)
        a7_c, oth_c, ratio_c = _ratios(control, key)
        print(f"\n  Metric: {metric}")
        print(f"  {'target (Poisson + period-7 inject)':<40}: "
              f"p=7 = {a7_t:.4f},  others mean = {oth_t:.4f},  "
              f"ratio = {ratio_t:.2f}×,  dom = p={target[dom_key]}")
        print(f"  {'control (Poisson background only)':<40}: "
              f"p=7 = {a7_c:.4f},  others mean = {oth_c:.4f},  "
              f"ratio = {ratio_c:.2f}×,  dom = p={control[dom_key]}")
        if ratio_t > 1.5 and target[dom_key] == 7 and ratio_c < 1.5:
            print(f"  ✓ ACCEPTANCE PASSED on this metric "
                  f"(target ratio {ratio_t:.2f}× > 1.5, dom=7, control {ratio_c:.2f}× < 1.5)")
        else:
            print(f"  ✗ ACCEPTANCE FAILED on this metric "
                  f"(target ratio {ratio_t:.2f}×, dom=p={target[dom_key]}, control {ratio_c:.2f}×)")


# ─── Save JSON ───────────────────────────────────────────────────────────────

def _trim(res):
    return dict(per_prime={int(p): {k: v for k, v in d.items()}
                           for p, d in res['per_prime'].items()},
                total_power=res['total_power'],
                q_max=res['q_max'],
                dominant_prime=res['dominant_prime'])


with open(os.path.join(DATA, "padic_v4_results.json"), 'w') as f:
    json.dump({k: _trim(v) for k, v in results.items()}, f, indent=2, default=str)
print(f"\n  → data/padic_v4_results.json")


# ─── Plot ────────────────────────────────────────────────────────────────────

labels = list(results.keys())
M = np.array([[results[lbl]['per_prime'][p]['normalised'] for p in PRIMES]
              for lbl in labels])

fig, ax = plt.subplots(figsize=(11, 0.55 * len(labels) + 2))
im = ax.imshow(M, aspect='auto', cmap='YlOrRd', vmin=0, vmax=M.max())
ax.set_xticks(range(len(PRIMES)),
              labels=[f"p={p}" for p in PRIMES])
ax.set_yticks(range(len(labels)), labels=labels, fontsize=9)
for i in range(len(labels)):
    for j in range(len(PRIMES)):
        ax.text(j, i, f"{M[i, j]:.3f}", ha='center', va='center',
                fontsize=8,
                color='white' if M[i, j] > 0.4 * M.max() else 'black')
ax.set_title(f"p-adic v4 (RF-amplitude based) — normalised power per prime, q_max={Q_MAX}")
fig.colorbar(im, ax=ax, label='normalised |a_q| amplitude')
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "36_padic_v4.png"), dpi=120)
plt.close(fig)
print(f"  → plots/36_padic_v4.png")
