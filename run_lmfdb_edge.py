"""
Katz–Sarnak edge test on the LMFDB elliptic curve L-function family.

The Phase 6 bulk analysis (Section 7.ter.1) showed every curve classifies
as Wigner GUE in the bulk pair-correlation — as expected, since bulk PC
is family-independent.  Katz–Sarnak family symmetry shows up in the
EDGE behaviour: the distribution of the LOWEST few zeros (γ_1, γ_2, …)
and the spacings near the central point distinguish:

    root_number = +1  →  orthogonal-even  (SO_even):
        zeros AVOID s_min = 0 like GUE; first-zero distribution has
        specific edge form; no forced central zero.

    root_number = -1  →  orthogonal-odd   (SO_odd):
        zero forced at central point (γ = 0); first non-trivial zero is
        γ_1 > 0; expect the spacing γ_2 - γ_1 to be different from the
        +1 case because of the boundary effect.

This script:
    1. For each of the 87 curves, take the FIRST 10 and 20 zeros.
    2. Compute per-curve normalised spacings.
    3. Pool by root_number and run the same NNS classifier.
    4. Cross-test: how does the lowest-zero distribution itself differ?
"""
import os, sys, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    _ks_pvalue,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")


def ks_to(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    if n < 5: return float('nan'), float('nan')
    F_em = np.arange(1, n + 1) / n
    ks = float(np.max(np.abs(F_em - theory_cdf(s))))
    return ks, _ks_pvalue(ks, n)


def two_sample_ks(a, b):
    s1, s2 = np.sort(a), np.sort(b)
    n1, n2 = s1.size, s2.size
    if n1 < 5 or n2 < 5: return float('nan'), float('nan')
    pts = np.concatenate([s1, s2])
    cdf1 = np.searchsorted(s1, pts, side='right') / n1
    cdf2 = np.searchsorted(s2, pts, side='right') / n2
    ks = float(np.max(np.abs(cdf1 - cdf2)))
    p = _ks_pvalue(ks, int(n1 * n2 / (n1 + n2)))
    return ks, p


def classify(pooled):
    if pooled.size < 5: return dict(n=int(pooled.size), best='insufficient')
    ks_p, _ = ks_to(pooled, nns_cdf_poisson)
    ks_o, _ = ks_to(pooled, nns_cdf_goe)
    ks_u, _ = ks_to(pooled, nns_cdf_gue)
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=int(pooled.size), ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((pooled < 0.3).mean()), best=best)


print("Loading lmfdb_zeros.json …")
with open(os.path.join(DATA, "lmfdb_zeros.json")) as f:
    curves = json.load(f)
print(f"  {len(curves)} curves\n")

# For curves with root_number = -1 the functional equation forces a zero at
# the central point (γ = 0); PARI reports this as the first entry of
# lfunzeros.  We strip that central zero so γ_1 below means the first
# NON-TRIVIAL zero in all cases (apples-to-apples with root_number = +1).
print("  Stripping forced central zero for root_number = -1 curves …")
n_stripped = 0
for c in curves:
    if c['root_number'] == -1 and len(c['zeros']) > 0 and c['zeros'][0] < 1e-6:
        c['zeros'] = c['zeros'][1:]
        c['n_zeros'] = len(c['zeros'])
        n_stripped += 1
print(f"  stripped from {n_stripped} curves\n")

n_plus  = sum(1 for c in curves if c['root_number'] == +1)
n_minus = sum(1 for c in curves if c['root_number'] == -1)
print(f"  root_number = +1: {n_plus} curves")
print(f"  root_number = -1: {n_minus} curves\n")


# ─── 1.  Lowest-zero distribution (γ_1) ──────────────────────────────────────
# Conjecture: γ_1 distributions differ between orthogonal-even (SO_e, +1)
# and orthogonal-odd (SO_o, -1) families.
print("=" * 100)
print("1.  Lowest zero γ_1 by root_number")
print("=" * 100)
gamma1_plus  = np.array([c['zeros'][0] for c in curves if c['root_number'] == +1])
gamma1_minus = np.array([c['zeros'][0] for c in curves if c['root_number'] == -1])
print(f"  root_number = +1:  γ_1 mean = {gamma1_plus.mean():.3f},  "
      f"median = {np.median(gamma1_plus):.3f},  std = {gamma1_plus.std():.3f}")
print(f"  root_number = −1:  γ_1 mean = {gamma1_minus.mean():.3f},  "
      f"median = {np.median(gamma1_minus):.3f},  std = {gamma1_minus.std():.3f}")
ks_g1, p_g1 = two_sample_ks(gamma1_plus, gamma1_minus)
print(f"  two-sample KS(γ_1):  KS = {ks_g1:.3f},  p = {p_g1:.3f}")
# Normalise by per-curve "expected first zero" — use the curve's analytic
# conductor scaling: γ_1 ~ 2π / log(N).  Then dimensionless γ_1 should be
# comparable across curves.
def gamma1_normalised(c):
    N = c['conductor']
    return c['zeros'][0] * np.log(max(N, 2)) / (2.0 * np.pi)
g1n_plus  = np.array([gamma1_normalised(c) for c in curves if c['root_number'] == +1])
g1n_minus = np.array([gamma1_normalised(c) for c in curves if c['root_number'] == -1])
print(f"\n  γ_1 normalised by  log(N)/(2π):")
print(f"  root_number = +1:  mean = {g1n_plus.mean():.3f},  std = {g1n_plus.std():.3f}")
print(f"  root_number = −1:  mean = {g1n_minus.mean():.3f},  std = {g1n_minus.std():.3f}")
ks_g1n, p_g1n = two_sample_ks(g1n_plus, g1n_minus)
print(f"  two-sample KS(γ_1 normalised):  KS = {ks_g1n:.3f},  p = {p_g1n:.3f}")
print()


# ─── 2.  Edge spacings — first N zeros per curve ──────────────────────────────
def per_curve_low_spacings(c, N_zeros):
    z = np.array(c['zeros'][:N_zeros], dtype=np.float64)
    if z.size < 2: return np.zeros(0)
    sp = np.diff(z)
    if sp.mean() <= 0: return np.zeros(0)
    return sp / sp.mean()


print("=" * 100)
print("2.  Edge NNS — pooled normalised spacings of the FIRST N zeros, by root_number")
print("=" * 100)
print(f"  {'N_zeros':>7}  {'group':<22}  {'n_curves':>8}  {'n_pooled':>9}  "
      f"{'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  {'gap':>6}  {'mass<0.3':>8}  best")
edge_results = {}
for N_use in [10, 15, 20, 30, 50]:
    edge_results[N_use] = {}
    for rt_label, rt in [('root_number = +1', +1), ('root_number = -1', -1)]:
        spacings_pool = []
        for c in curves:
            if c['root_number'] != rt: continue
            sp = per_curve_low_spacings(c, N_use)
            if sp.size > 0: spacings_pool.append(sp)
        if not spacings_pool:
            continue
        pooled = np.concatenate(spacings_pool)
        cl = classify(pooled)
        edge_results[N_use][rt] = dict(pooled=pooled, **cl)
        print(f"  {N_use:>7}  {rt_label:<22}  {sum(1 for c in curves if c['root_number']==rt):>8}  "
              f"{cl['n']:>9}  {cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['mass03']:8.3f}  {cl['best']}")
    # cross-comparison
    if +1 in edge_results[N_use] and -1 in edge_results[N_use]:
        ks_pm, p_pm = two_sample_ks(edge_results[N_use][+1]['pooled'],
                                       edge_results[N_use][-1]['pooled'])
        print(f"  {N_use:>7}  two-sample KS(+1 vs −1):  KS = {ks_pm:.4f},  p = {p_pm:.4f}")
        print()


# ─── 3.  Orthogonal-edge specific test:  spacing γ_2 - γ_1 alone ──────────────
print("=" * 100)
print("3.  First spacing  γ_2 − γ_1  by root_number  (one number per curve)")
print("=" * 100)
def first_spacing(c, normalise=True):
    z = c['zeros']
    if len(z) < 2: return None
    s = z[1] - z[0]
    if not normalise: return s
    # Normalise by the "predicted local mean spacing" for this curve.
    # For an L-function of conductor N, mean zero spacing at height γ is
    # ~ 2π / (log(γ * sqrt(N) / (2π)) + log( … ) )  (rough).  Simpler:
    # just normalise by the curve's empirical mean of (γ_{k+1} - γ_k) for
    # k = 1..n_use - 1, using a healthy chunk of low zeros for stability.
    n_use = min(50, len(z))
    mean_local = float(np.diff(z[:n_use]).mean())
    return s / mean_local

s12_plus  = np.array([first_spacing(c) for c in curves if c['root_number'] == +1])
s12_minus = np.array([first_spacing(c) for c in curves if c['root_number'] == -1])
print(f"  root_number = +1:  s_norm(γ_2-γ_1) mean = {s12_plus.mean():.3f},  "
      f"median = {np.median(s12_plus):.3f},  std = {s12_plus.std():.3f}")
print(f"  root_number = −1:  s_norm(γ_2-γ_1) mean = {s12_minus.mean():.3f},  "
      f"median = {np.median(s12_minus):.3f},  std = {s12_minus.std():.3f}")
ks12, p12 = two_sample_ks(s12_plus, s12_minus)
print(f"  two-sample KS(γ_2-γ_1 normalised):  KS = {ks12:.3f},  p = {p12:.3f}")
# fraction of small spacings
print(f"  fraction with first spacing < 0.5 of local mean:")
print(f"    +1: {(s12_plus < 0.5).mean():.3f}")
print(f"    −1: {(s12_minus < 0.5).mean():.3f}")
print()


# ─── 4.  Plots ────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey='row', sharex='col')

# Top row: γ_1 distributions
for ax, (name, vals) in zip(axes[0],
                              [('γ_1 raw', (gamma1_plus, gamma1_minus)),
                               ('γ_1 / [log(N)/(2π)]', (g1n_plus, g1n_minus)),
                               ('γ_2 - γ_1 (normalised)', (s12_plus, s12_minus))]):
    a, b = vals
    bins = np.linspace(min(a.min(), b.min()), max(a.max(), b.max()), 18)
    ax.hist(a, bins=bins, alpha=0.55, color='C0', density=True, label=f'+1 (n={a.size})')
    ax.hist(b, bins=bins, alpha=0.55, color='C3', density=True, label=f'−1 (n={b.size})')
    ax.set_title(name, fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

# Bottom row: edge NNS (N=10, 20, 50)
s_grid = np.linspace(0.001, 4.0, 200); bin_edges = np.linspace(0, 4, 30)
for ax, N_use in zip(axes[1], [10, 20, 50]):
    for rt, color, label in [(+1, 'C0', '+1'), (-1, 'C3', '-1')]:
        if rt not in edge_results[N_use]: continue
        pooled = edge_results[N_use][rt]['pooled']
        ax.hist(pooled, bins=bin_edges, density=True, alpha=0.55, color=color,
                label=f"{label} (n={pooled.size}, KS_U={edge_results[N_use][rt]['ks_u']:.3f})")
    ax.plot(s_grid, nns_gue(s_grid),     'r-', lw=1.4, label='GUE')
    ax.plot(s_grid, nns_goe(s_grid),     'g-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_poisson(s_grid), 'k--', lw=0.8, label='Poisson')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.4)
    ax.set_title(f"Edge NNS, first {N_use} zeros / curve", fontsize=10)
    ax.set_xlabel('s')
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)

axes[0,0].set_ylabel('density')
axes[1,0].set_ylabel('density')
fig.suptitle("Katz–Sarnak edge test on LMFDB elliptic curve L-functions, conductor ≤ 99")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOTS, "19_lmfdb_edge.png"), dpi=110)
plt.close(fig)
print(f"  → plots/19_lmfdb_edge.png")


# ─── Save edge results ────────────────────────────────────────────────────────
out = dict(
    config=dict(N_zero_options=[10, 15, 20, 30, 50]),
    n_curves=len(curves),
    gamma1=dict(
        plus_one=dict(mean=float(gamma1_plus.mean()), median=float(np.median(gamma1_plus)),
                       std=float(gamma1_plus.std()), n=int(gamma1_plus.size)),
        minus_one=dict(mean=float(gamma1_minus.mean()), median=float(np.median(gamma1_minus)),
                        std=float(gamma1_minus.std()), n=int(gamma1_minus.size)),
        ks_two_sample=ks_g1, p_value=p_g1,
    ),
    gamma1_normalised=dict(
        plus_one=dict(mean=float(g1n_plus.mean()), std=float(g1n_plus.std())),
        minus_one=dict(mean=float(g1n_minus.mean()), std=float(g1n_minus.std())),
        ks_two_sample=ks_g1n, p_value=p_g1n,
    ),
    first_spacing_normalised=dict(
        plus_one=dict(mean=float(s12_plus.mean()), std=float(s12_plus.std()),
                       frac_below_0p5=float((s12_plus < 0.5).mean())),
        minus_one=dict(mean=float(s12_minus.mean()), std=float(s12_minus.std()),
                        frac_below_0p5=float((s12_minus < 0.5).mean())),
        ks_two_sample=ks12, p_value=p12,
    ),
    edge_NNS_by_N=dict([
        (str(N), {
            'plus_one': {k: v for k, v in edge_results[N].get(+1, {}).items() if k != 'pooled'},
            'minus_one': {k: v for k, v in edge_results[N].get(-1, {}).items() if k != 'pooled'},
        }) for N in [10, 15, 20, 30, 50]
    ]),
)
out_json = os.path.join(DATA, "lmfdb_edge_results.json")
with open(out_json, 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"  → {out_json}")
