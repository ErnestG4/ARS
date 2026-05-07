"""Extend each LMFDB curve's zero list to a deeper height.

Phase 6 used 87 curves at height 200 (≈ 280 zeros each).  This re-runs PARI's
`lfunzeros` to height 1000 (≈ 1400 zeros/curve) for the same curve set,
giving a 5× richer dataset for both bulk and edge analysis.

Output:
    data/lmfdb_zeros_h1000.json      — extended zero list
    data/lmfdb_extend_results.json   — classification per curve + aggregate
    plots/20_lmfdb_extend.png
"""
import os, sys, time, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from pll_bank import farey_rationals
from universality import nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue
from universality import nns_poisson, nns_goe, nns_gue, _ks_pvalue
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cypari2

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
ZERO_HEIGHT = 1000.0
SR = 44100.0; DUR = 300.0; FC_REF = 1.0; Q_MAX = 8
LOCK_CONFIRM_S = 20e-3; TONGUE_PREFAC = 0.05; TRANSIENT_S = 0.5

pari = cypari2.Pari()


def analytical_nns(t_n_array):
    pairs = farey_rationals(Q_MAX)
    pooled, info = [], []
    for p, q in pairs:
        f_pll = FC_REF * p / q
        if f_pll <= 0.5: continue
        elig = ((t_n_array >= (TRANSIENT_S + 1.0) * f_pll) &
                (t_n_array <= (DUR + 1.0) * f_pll))
        elig_t = np.sort(t_n_array[elig])
        threshold = LOCK_CONFIRM_S * f_pll / (TONGUE_PREFAC * (2.0 / (p + q)) ** 2)
        qual = elig_t[elig_t >= threshold]
        if qual.size < 11: continue
        sp = np.diff(qual) / f_pll
        if sp.size == 0 or sp.mean() <= 0: continue
        pooled.append(sp / sp.mean())
        info.append((p, q, int(qual.size)))
    return (np.concatenate(pooled) if pooled else np.zeros(0)), info


def classify(pooled):
    if pooled.size < 50: return dict(n=int(pooled.size), best='insufficient')
    s = np.sort(pooled); n = s.size
    F_em = np.arange(1, n + 1) / n
    ks_p = float(np.max(np.abs(F_em - nns_cdf_poisson(s))))
    ks_o = float(np.max(np.abs(F_em - nns_cdf_goe(s))))
    ks_u = float(np.max(np.abs(F_em - nns_cdf_gue(s))))
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=n, ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((pooled < 0.3).mean()), best=best)


print(f"Loading curves from previous LMFDB run …")
with open(os.path.join(DATA, "lmfdb_zeros.json")) as f:
    base = json.load(f)
print(f"  {len(base)} curves; recomputing zeros to height {ZERO_HEIGHT}\n")
print(f"  {'#':>3}  {'label':<10}  {'cond':>4}  {'rt#':>3}  {'#zeros':>6}  {'cpu_s':>7}",
      flush=True)

extended = []
t_total0 = time.perf_counter()
for i, c in enumerate(base):
    t0 = time.perf_counter()
    try:
        E = pari.ellinit(c['ainvs'])
        L = pari.lfuncreate(E)
        zeros = pari.lfunzeros(L, ZERO_HEIGHT)
        zeros = np.array([float(z) for z in zeros], dtype=np.float64)
    except Exception as e:
        print(f"  {i+1:>3}  {c['label']:<10}  {c['conductor']:>4}  "
              f"{c['root_number']:>+3}  ERR: {str(e)[:40]}", flush=True)
        continue
    dt = time.perf_counter() - t0
    print(f"  {i+1:>3}  {c['label']:<10}  {c['conductor']:>4}  "
          f"{c['root_number']:>+3}  {zeros.size:>6}  {dt:>7.1f}", flush=True)
    extended.append(dict(c, zeros=zeros.tolist(), n_zeros=int(zeros.size)))

print(f"\n  Total: {(time.perf_counter()-t_total0)/60:.1f} min  "
      f"({len(extended)}/{len(base)} curves)")

with open(os.path.join(DATA, "lmfdb_zeros_h1000.json"), 'w') as f:
    json.dump(extended, f)
print(f"  → data/lmfdb_zeros_h1000.json")

# Strip central zero for root_number=-1
print(f"\n  Stripping central zero for root_number=-1 curves …")
n_strip = 0
for c in extended:
    if c['root_number'] == -1 and c['zeros'][0] < 1e-6:
        c['zeros'] = c['zeros'][1:]; c['n_zeros'] -= 1; n_strip += 1
print(f"  stripped {n_strip}")

# Run analytical NNS per curve
print(f"\n  Per-curve classification …")
print(f"  {'label':<10}  {'cond':>4}  {'rt#':>3}  {'n_z':>5}  {'#PLLs':>5}  "
      f"{'n_pool':>7}  {'KS_GUE':>6}  {'gap':>6}  best", flush=True)
per_curve = []
for c in extended:
    z = np.array(c['zeros'], dtype=np.float64)
    pooled, info = analytical_nns(z)
    cl = classify(pooled)
    rec = dict(label=c['label'], conductor=c['conductor'],
                rank=c['rank'], root_number=c['root_number'],
                n_zeros=c['n_zeros'], n_plls=len(info),
                pooled=pooled, **cl)
    per_curve.append(rec)
    print(f"  {c['label']:<10}  {c['conductor']:>4}  {c['root_number']:>+3}  "
          f"{c['n_zeros']:>5}  {len(info):>5}  {cl['n']:>7}  "
          f"{cl.get('ks_u', float('nan')):6.3f}  {cl.get('gap', float('nan')):+6.3f}  "
          f"{cl['best']}", flush=True)


# Aggregate
def agg(group):
    arrs = [r['pooled'] for r in group if r['pooled'].size > 50]
    if not arrs: return None
    pooled = np.concatenate(arrs)
    return classify(pooled), pooled

groups = {
    'all curves':       per_curve,
    'root_number = +1': [r for r in per_curve if r['root_number'] == +1],
    'root_number = -1': [r for r in per_curve if r['root_number'] == -1],
}
print(f"\n  Aggregate by root number")
print(f"  {'group':<24}  {'n_curves':>8}  {'n_pool':>8}  {'KS_P':>5}  "
      f"{'KS_O':>5}  {'KS_U':>5}  {'gap':>6}  best")
agg_results = {}
for name, group in groups.items():
    res = agg(group)
    if res is None: continue
    cl, pooled = res
    agg_results[name] = dict(cl=cl, pooled=pooled)
    print(f"  {name:<24}  {len(group):>8}  {cl['n']:>8}  "
          f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
          f"{cl['gap']:+6.3f}  {cl['best']}", flush=True)

# Plot
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200); bin_edges = np.linspace(0, 4, 41)
for ax, name in zip(axes, ['all curves', 'root_number = +1', 'root_number = -1']):
    if name not in agg_results: ax.set_title(f"{name}: empty"); continue
    pooled = agg_results[name]['pooled']
    cl = agg_results[name]['cl']
    ax.hist(pooled, bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={cl['n']}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    ax.set_title(f"{name}\nbest={cl['best']}, gap={cl['gap']:+.3f}, "
                  f"mass<0.3={cl['mass03']:.3f}", fontsize=9)
    ax.set_xlabel('s')
    ax.grid(True, alpha=0.3)
axes[0].set_ylabel('P(s)')
axes[0].legend(fontsize=7, loc='upper right')
fig.suptitle(f"LMFDB extended (zeros to height {int(ZERO_HEIGHT)})")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOTS, "20_lmfdb_extend.png"), dpi=110)
plt.close(fig)
print(f"  → plots/20_lmfdb_extend.png")

with open(os.path.join(DATA, "lmfdb_extend_results.json"), 'w') as f:
    json.dump({
        'config': dict(zero_height=ZERO_HEIGHT, fc_ref=FC_REF, q_max=Q_MAX),
        'aggregates': {k: v['cl'] for k, v in agg_results.items()},
        'per_curve': [{k: v for k, v in r.items() if k != 'pooled'}
                       for r in per_curve],
    }, f, indent=2, default=str)
print(f"  → data/lmfdb_extend_results.json")
