"""Post-process lmfdb_zeros.json — run analytical NNS classifier per curve
and aggregate by root number / rank."""
import os, sys, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from pll_bank import farey_rationals
from universality import nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue
from universality import nns_poisson, nns_goe, nns_gue
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SR = 44100.0; DUR = 300.0; FC_REF = 1.0; Q_MAX = 8
LOCK_CONFIRM_S = 20e-3; TONGUE_PREFAC = 0.05; TRANSIENT_S = 0.5
PLOT_DIR = os.path.join(THIS_DIR, "plots")
DATA_DIR = os.path.join(THIS_DIR, "data")


def analytical_nns(t_n_array, fc_ref=FC_REF, q_max=Q_MAX, dur_s=DUR,
                    transient_s=TRANSIENT_S, lock_confirm_s=LOCK_CONFIRM_S,
                    tongue_prefac=TONGUE_PREFAC, sr=SR, min_events=10):
    pairs = farey_rationals(q_max)
    pooled = []
    info = []
    for p, q in pairs:
        f_pll = fc_ref * p / q
        if f_pll <= 0.5: continue
        elig = ((t_n_array >= (transient_s + 1.0) * f_pll) &
                (t_n_array <= (dur_s + 1.0) * f_pll))
        elig_t = np.sort(t_n_array[elig])
        threshold = lock_confirm_s * f_pll / (tongue_prefac * (2.0 / (p + q)) ** 2)
        qualifying = elig_t[elig_t >= threshold]
        if qualifying.size < min_events + 1: continue
        sp = np.diff(qualifying) / f_pll
        if sp.size == 0 or sp.mean() <= 0: continue
        pooled.append(sp / sp.mean())
        info.append((p, q, int(qualifying.size)))
    return (np.concatenate(pooled) if pooled else np.zeros(0)), info


def classify(pooled):
    if pooled.size < 50:
        return dict(n=int(pooled.size), best='insufficient')
    s = np.sort(pooled); n = s.size
    F_em = np.arange(1, n + 1) / n
    ks_p = float(np.max(np.abs(F_em - nns_cdf_poisson(s))))
    ks_o = float(np.max(np.abs(F_em - nns_cdf_goe(s))))
    ks_u = float(np.max(np.abs(F_em - nns_cdf_gue(s))))
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=n, ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((pooled < 0.3).mean()), best=best)


print("Loading lmfdb_zeros.json …")
with open(os.path.join(DATA_DIR, "lmfdb_zeros.json")) as f:
    curves = json.load(f)
print(f"  {len(curves)} curves")
print()


# ─── Per-curve classification ───
print("=" * 110)
print("Per-curve NNS classification")
print("=" * 110)
print(f"  {'label':<10}  {'cond':>4}  {'rank':>4}  {'rt#':>3}  {'n_z':>5}  "
      f"{'#PLLs':>5}  {'n_pool':>7}  {'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  "
      f"{'gap':>6}  best")
per_curve = []
for c in curves:
    zeros = np.array(c['zeros'], dtype=np.float64)
    pooled, info = analytical_nns(zeros)
    cl = classify(pooled)
    per_curve.append(dict(label=c['label'], conductor=c['conductor'],
                            rank=c['rank'], root_number=c['root_number'],
                            n_zeros=c['n_zeros'], n_plls=len(info),
                            pooled=pooled, **cl))
    if cl.get('best') == 'insufficient':
        print(f"  {c['label']:<10}  {c['conductor']:>4}  {c['rank']:>4}  "
              f"{c['root_number']:>+3}  {c['n_zeros']:>5}  insufficient")
    else:
        print(f"  {c['label']:<10}  {c['conductor']:>4}  {c['rank']:>4}  "
              f"{c['root_number']:>+3}  {c['n_zeros']:>5}  {len(info):>5}  "
              f"{cl['n']:>7}  {cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['best']}")
print()


# ─── Aggregate ───
print("=" * 110)
print("Aggregate by root_number / rank — Katz–Sarnak family signature")
print("=" * 110)
print(f"  {'group':<24}  {'n_curves':>8}  {'n_pooled':>9}  "
      f"{'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  "
      f"{'gap':>6}  {'mass<0.3':>8}  best")
groups = {
    'all curves':       per_curve,
    'root_number = +1': [r for r in per_curve if r['root_number'] == +1],
    'root_number = -1': [r for r in per_curve if r['root_number'] == -1],
    'rank = 0':         [r for r in per_curve if r['rank'] == 0],
    'rank ≥ 1':         [r for r in per_curve if r['rank'] >= 1],
}
agg = {}
for name, group in groups.items():
    arrs = [r['pooled'] for r in group if r['pooled'].size > 50]
    if not arrs:
        print(f"  {name:<24}  insufficient"); continue
    pooled = np.concatenate(arrs)
    cl = classify(pooled)
    agg[name] = cl
    print(f"  {name:<24}  {len(group):>8}  {cl['n']:>9}  "
          f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
          f"{cl['gap']:+6.3f}  {cl['mass03']:8.3f}  {cl['best']}")
print()


# ─── Best-fit class counts per group ───
print("=" * 110)
print("Per-curve best-fit distribution (within each group)")
print("=" * 110)
print(f"  {'group':<24}  {'#GUE':>4}  {'#GOE':>4}  {'#Poiss':>6}  {'mean gap':>9}")
for name, group in groups.items():
    valid = [r for r in group if r['best'] in ('GUE', 'GOE', 'Poiss')]
    if not valid: continue
    n_gue = sum(1 for r in valid if r['best'] == 'GUE')
    n_goe = sum(1 for r in valid if r['best'] == 'GOE')
    n_poi = sum(1 for r in valid if r['best'] == 'Poiss')
    mean_gap = float(np.mean([r['gap'] for r in valid]))
    print(f"  {name:<24}  {n_gue:>4}  {n_goe:>4}  {n_poi:>6}  {mean_gap:+9.4f}")
print()


# ─── Plot ───
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200); bin_edges = np.linspace(0, 4, 41)
group_to_plot = ['all curves', 'root_number = +1', 'root_number = -1']
for ax, name in zip(axes, group_to_plot):
    arrs = [r['pooled'] for r in groups[name] if r['pooled'].size > 50]
    if not arrs: ax.set_title(f"{name}: no data"); continue
    pooled = np.concatenate(arrs)
    ax.hist(pooled, bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={pooled.size}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    cl = agg[name]
    ax.set_title(f"{name}\nbest={cl['best']}, gap={cl['gap']:+.3f}, "
                  f"mass<0.3={cl['mass03']:.3f}", fontsize=9)
    ax.set_xlabel('normalised spacing s')
    ax.grid(True, alpha=0.3)
axes[0].set_ylabel('P(s)')
axes[0].legend(fontsize=7, loc='upper right')
fig.suptitle("LMFDB elliptic curve L-functions, conductor ≤ 99 — Katz–Sarnak family symmetry test")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "17_lmfdb_family.png"), dpi=110)
plt.close(fig)
print(f"  → plots/17_lmfdb_family.png")


# ─── Save full results JSON ───
out = dict(
    config=dict(fc_ref=FC_REF, q_max=Q_MAX, dur=DUR, transient_s=TRANSIENT_S),
    n_curves=len(curves),
    aggregates=agg,
    per_curve=[{k: v for k, v in r.items() if k != 'pooled'}
                for r in per_curve],
)
out_json = os.path.join(DATA_DIR, "lmfdb_results.json")
with open(out_json, 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"  → {out_json}")
