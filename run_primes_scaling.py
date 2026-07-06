"""
Fano F(T=5) scaling for primes and twin primes — Cramér / Hardy-Littlewood
convergence to Poisson visualized.

Sieves once up to N_MAX (= 10⁸), slices progressively, and for each cut-off
N computes the multiscale Fano factor F(T) of the logarithmically-unfolded
prime-position sequence.  Same for twin primes (using the lower member of
each twin-prime pair as the event time).

Output:
    data/primes_scaling.json
    plots/33_primes_scaling.png
"""
import os, sys, json, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import fano_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")

N_MAX = 10**8
CUTS  = [10**4, 10**5, 10**6, 10**7, 10**8]


def sieve(N):
    s = np.ones(N + 1, dtype=bool)
    s[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if s[p]:
            s[p*p::p] = False
    return s


def primes_unfolded(p_arr):
    """Logarithmic unfolding so mean spacing → 1 asymptotically."""
    return p_arr.astype(np.float64) / np.log(np.maximum(p_arr.astype(np.float64), 2.0))


def twin_pairs_lower(p_arr):
    """Lower member of each twin-prime pair (p, p+2)."""
    diffs = np.diff(p_arr)
    mask = diffs == 2
    return p_arr[:-1][mask]


def fano_scaling_row(t_k, label):
    """Compute F(T=1), F(T=5), F(T=20) for the unfolded events."""
    if t_k.size < 50:
        return dict(label=label, n=int(t_k.size), F1=np.nan, F5=np.nan, F20=np.nan)
    res = fano_curve(t_k, n_scales=30)
    return dict(label=label, n=int(t_k.size),
                F1=res.get('F_at_1', np.nan),
                F5=res.get('F_at_5', np.nan),
                F20=res.get('F_at_20', np.nan),
                mean_sp=res.get('mean_sp', np.nan),
                duration=res.get('duration', np.nan))


# ─── Sieve once ───────────────────────────────────────────────────────────────

print(f"Sieving primes up to N = {N_MAX:,} …")
t0 = time.time()
s = sieve(N_MAX)
all_primes = np.where(s)[0]
print(f"  π({N_MAX:,}) = {all_primes.size:,}   sieve time {time.time()-t0:.1f}s")

print("\n" + "=" * 90)
print(f"  {'N':<12}  {'π(N)':>10}  {'F(T=1)':>7}  {'F(T=5)':>7}  {'F(T=20)':>7}  signal")
print("=" * 90)

results = []
for N in CUTS:
    p = all_primes[all_primes <= N]
    if p.size < 50: continue
    u = primes_unfolded(p)
    row = fano_scaling_row(u, f"primes_N{N}")
    row['N'] = N
    row['kind'] = 'primes'
    results.append(row)
    print(f"  primes ≤ 10^{int(np.log10(N))}  {p.size:>10,}  "
          f"{row['F1']:>7.3f}  {row['F5']:>7.3f}  {row['F20']:>7.3f}  primes")

    tp = twin_pairs_lower(p)
    if tp.size >= 50:
        u_tp = primes_unfolded(tp)
        row_tp = fano_scaling_row(u_tp, f"twin_N{N}")
        row_tp['N'] = N
        row_tp['kind'] = 'twin_primes'
        results.append(row_tp)
        print(f"  twin   ≤ 10^{int(np.log10(N))}  {tp.size:>10,}  "
              f"{row_tp['F1']:>7.3f}  {row_tp['F5']:>7.3f}  {row_tp['F20']:>7.3f}  twin primes")

print(f"\n  total time {time.time()-t0:.1f}s")


# ─── Save JSON ────────────────────────────────────────────────────────────────

with open(os.path.join(DATA, "primes_scaling.json"), 'w') as f:
    json.dump({'N_max': N_MAX, 'rows': results}, f, indent=2, default=str)
print(f"  → data/primes_scaling.json")


# ─── Plot ────────────────────────────────────────────────────────────────────

primes_rows = [r for r in results if r['kind'] == 'primes']
twin_rows   = [r for r in results if r['kind'] == 'twin_primes']

fig, ax = plt.subplots(figsize=(8, 5.5))
xs_p = [int(np.log10(r['N'])) for r in primes_rows]
xs_t = [int(np.log10(r['N'])) for r in twin_rows]

for col, lbl, fn in [('C0', 'F(T=1)', 'F1'), ('C1', 'F(T=5)', 'F5'), ('C2', 'F(T=20)', 'F20')]:
    ax.plot(xs_p, [r[fn] for r in primes_rows], 'o-', color=col,
            lw=2, ms=7, label=f'primes  {lbl}')
    if twin_rows:
        ax.plot(xs_t, [r[fn] for r in twin_rows], 's--', color=col,
                lw=1.5, ms=6, alpha=0.7, label=f'twins  {lbl}')

ax.axhline(1.0, color='g', ls=':', lw=1.5, label='Poisson F = 1')
ax.set_xlabel('log₁₀(N)')
ax.set_ylabel('Fano factor F(T)')
ax.set_title("Cramér / Hardy-Littlewood: primes & twin primes Fano factor → Poisson with N")
ax.set_xticks(xs_p)
ax.legend(fontsize=8, loc='lower right', ncol=2)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "33_primes_scaling.png"), dpi=120)
plt.close(fig)
print(f"  → plots/33_primes_scaling.png")
