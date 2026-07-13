"""Dirichlet L-function family survey.

Katz-Sarnak predicts:
    real primitive Dirichlet characters → SYMPLECTIC family (Sp)
    complex characters                 → UNITARY family (U) ≃ GUE bulk

We enumerate all primitive Dirichlet characters of moduli q in a range,
classify each as real (order ≤ 2) or complex, compute many zeros via
PARI's lfunzeros, and run the analytical-passage-time NNS classifier.

The goal is to add a third universality-class data point (symplectic)
to the table that already has unitary (ζ, complex Dirichlet) and
orthogonal (elliptic curves) families.

Output:
    data/dirichlet_zeros.json
    data/dirichlet_results.json
    plots/22_dirichlet_family.png
"""
import os, sys, time, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))

from pll_bank import farey_rationals
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    _ks_pvalue,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cypari2
pari = cypari2.Pari()


DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
ZERO_HEIGHT = 200.0   # ~280 zeros per character at q ~ 50

# Configurable via env:  DIRICHLET_QMAX=150  python3 run_dirichlet_family.py
import os as _os
_qmax = int(_os.environ.get('DIRICHLET_QMAX', '80'))
Q_RANGE = list(range(3, _qmax))    # moduli to scan
SR = 44100.0; DUR = 300.0; FC_REF = 1.0; Q_MAX = 8
LOCK_CONFIRM_S = 20e-3; TONGUE_PREFAC = 0.05; TRANSIENT_S = 0.5


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


# ─── Enumerate primitive Dirichlet characters ────────────────────────────────
print(f"Enumerating primitive Dirichlet characters for q ∈ {Q_RANGE[0]}..{Q_RANGE[-1]}…",
      flush=True)
chars_to_use = []
for q in Q_RANGE:
    try:
        G = pari.znstar(q, 1)
        chars = pari.chargalois(G)   # Galois orbits of characters
    except Exception as e:
        continue
    for chi in chars:
        try:
            order = int(pari.charorder(G, chi))
            cond = int(pari('zncharconductor')(G, chi))
            if cond != q:               # only primitive characters
                continue
            if order == 1:
                continue                 # trivial character → ζ
            is_real = (order == 2)
            chars_to_use.append(dict(q=q, chi=chi, order=order, is_real=is_real,
                                       conductor=cond))
        except Exception:
            continue
print(f"  {len(chars_to_use)} primitive non-trivial characters", flush=True)
n_real = sum(1 for c in chars_to_use if c['is_real'])
n_complex = sum(1 for c in chars_to_use if not c['is_real'])
print(f"  real (predicted symplectic): {n_real}", flush=True)
print(f"  complex (predicted unitary): {n_complex}", flush=True)
print()


# ─── Compute zeros for each character ────────────────────────────────────────
print(f"Computing zeros up to height {ZERO_HEIGHT} per character…")
print(f"  {'#':>3}  {'q':>3}  {'order':>5}  {'class':>9}  {'#zeros':>6}  {'cpu_s':>6}",
      flush=True)
results_per_char = []
t0_total = time.perf_counter()
for i, c in enumerate(chars_to_use):
    t0 = time.perf_counter()
    try:
        G = pari.znstar(c['q'], 1)
        L = pari.lfuncreate([G, c['chi']])
        zeros = pari.lfunzeros(L, ZERO_HEIGHT)
        zeros = np.array([float(z) for z in zeros], dtype=np.float64)
    except Exception as e:
        print(f"  {i+1:>3}  {c['q']:>3}  {c['order']:>5}  ERR: {str(e)[:50]}", flush=True)
        continue
    if zeros.size < 30:
        # too few zeros for stable analysis — skip
        continue
    dt = time.perf_counter() - t0
    cls = 'real(Sp)' if c['is_real'] else 'cplx(U)'
    print(f"  {i+1:>3}  {c['q']:>3}  {c['order']:>5}  {cls:>9}  "
          f"{zeros.size:>6}  {dt:>6.1f}", flush=True)
    # Convert all PARI Gen objects to Python types before saving
    rec = dict(
        q=int(c['q']), order=int(c['order']),
        is_real=bool(c['is_real']), conductor=int(c['conductor']),
        chi=[int(x) for x in c['chi']],
        zeros=zeros.tolist(),
        n_zeros=int(zeros.size),
        cpu_s=float(dt),
    )
    results_per_char.append(rec)

print(f"\n  total compute: {(time.perf_counter()-t0_total)/60:.1f} min")
print(f"  characters analysed: {len(results_per_char)}", flush=True)


# Save zeros
with open(os.path.join(DATA, "dirichlet_zeros.json"), 'w') as f:
    json.dump(results_per_char, f)
print(f"  → data/dirichlet_zeros.json")
print()


# ─── Strip central zero if present (real chars at central point sometimes) ───
n_strip = 0
for c in results_per_char:
    if c['zeros'] and c['zeros'][0] < 1e-6:
        c['zeros'] = c['zeros'][1:]
        c['n_zeros'] -= 1
        n_strip += 1
if n_strip:
    print(f"  stripped central zero from {n_strip} characters")
    print()


# ─── Per-character classification ────────────────────────────────────────────
print("=" * 110)
print("Per-character NNS classification")
print("=" * 110)
print(f"  {'q':>3}  {'order':>5}  {'class':>9}  {'#zeros':>6}  {'#PLLs':>5}  "
      f"{'n_pool':>7}  {'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  {'gap':>6}  best",
      flush=True)
for c in results_per_char:
    z = np.array(c['zeros'], dtype=np.float64)
    pooled, info = analytical_nns(z)
    cl = classify(pooled)
    c['classification'] = cl
    c['_pooled'] = pooled
    cls = 'real(Sp)' if c['is_real'] else 'cplx(U)'
    if cl.get('best') == 'insufficient':
        print(f"  {c['q']:>3}  {c['order']:>5}  {cls:>9}  {c['n_zeros']:>6}  "
              f"{len(info):>5}  {cl['n']:>7}  insufficient", flush=True)
    else:
        print(f"  {c['q']:>3}  {c['order']:>5}  {cls:>9}  {c['n_zeros']:>6}  "
              f"{len(info):>5}  {cl['n']:>7}  "
              f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['best']}", flush=True)
print()


# ─── Aggregate ────────────────────────────────────────────────────────────────
print("=" * 110)
print("Aggregate by family symmetry class (Katz-Sarnak)")
print("=" * 110)
print(f"  {'group':<28}  {'n_chars':>7}  {'n_pool':>8}  {'KS_P':>5}  "
      f"{'KS_O':>5}  {'KS_U':>5}  {'gap':>6}  {'mass<0.3':>8}  best", flush=True)


def aggregate_pool(group):
    arrs = [c['_pooled'] for c in group
            if c.get('_pooled') is not None and c['_pooled'].size > 50]
    if not arrs: return None
    return np.concatenate(arrs)


groups = {
    'all primitive non-trivial':     results_per_char,
    'real characters (Sp predicted)': [c for c in results_per_char if c['is_real']],
    'complex characters (U predicted)': [c for c in results_per_char if not c['is_real']],
}
agg_results = {}
for name, group in groups.items():
    pooled = aggregate_pool(group)
    if pooled is None:
        print(f"  {name:<28}  insufficient")
        continue
    cl = classify(pooled)
    agg_results[name] = dict(cl=cl, pooled=pooled)
    print(f"  {name:<28}  {len(group):>7}  {cl['n']:>8}  "
          f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
          f"{cl['gap']:+6.3f}  {cl['mass03']:8.3f}  {cl['best']}", flush=True)
print()


# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200); bin_edges = np.linspace(0, 4, 41)
for ax, name in zip(axes, list(groups.keys())):
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
                  f"mass<0.3={cl['mass03']:.3f}", fontsize=8)
    ax.set_xlabel('s'); ax.grid(True, alpha=0.3)
axes[0].set_ylabel('P(s)')
axes[0].legend(fontsize=7, loc='upper right')
fig.suptitle("Dirichlet L-function family — Katz-Sarnak symplectic vs unitary test")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOTS, "22_dirichlet_family.png"), dpi=110)
plt.close(fig)
print(f"  → plots/22_dirichlet_family.png")


# ─── Save full results ────────────────────────────────────────────────────────
with open(os.path.join(DATA, "dirichlet_results.json"), 'w') as f:
    json.dump({
        'config': dict(zero_height=ZERO_HEIGHT, q_range=Q_RANGE,
                       fc_ref=FC_REF, q_max=Q_MAX),
        'aggregates': {k: v['cl'] for k, v in agg_results.items()},
        'per_character': [{k: v for k, v in c.items()
                            if k not in ('zeros', '_pooled', 'chi')}
                            for c in results_per_char],
    }, f, indent=2, default=str)
print(f"  → data/dirichlet_results.json")
