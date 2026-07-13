"""
Phase 4 — cross-signal application of the analytical passage-time NNS.

The instrument is calibrated (§6 of RESULTS.md):
    GUE eigenvalues → Wigner GUE NNS  (KS_GUE = 0.022)
    GOE eigenvalues → Wigner GOE NNS  (KS_GOE = 0.021)
    ζ zeros        → Wigner GUE NNS  (KS_GUE = 0.034)

Now apply it to other arithmetic objects.

Signals tested:
    1.  ζ first 1000 zeros            — anchor (Wigner GUE)
    2.  ζ zeros 1001–2000             — same theory, different region
    3.  Primes (first N)              — what universality class do prime
                                         positions show?
    4.  Squarefree integers (first N) — Möbius support
    5.  Random uniform                — Poisson null
    6.  GUE eigenvalues (uniform unfolded)  — calibration anchor (Wigner GUE)
    7.  GOE eigenvalues (uniform unfolded)  — calibration anchor (Wigner GOE)

Per-PLL passage-time NNS at the calibrated cell (q_max=8, fc_ref=115.55,
dur=300 s, lock_confirm=20 ms, transient=500 ms).
"""
import os, sys, time
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


SR        = 44100.0
DUR       = 300.0
FC_REF    = 115.55
Q_MAX     = 8
LOCK_CONFIRM_S = 20e-3
TONGUE_PREFAC  = 0.05
TRANSIENT_S    = 0.500
PLOT_DIR  = os.path.join(THIS_DIR, "plots")


def analytical_nns(t_n_array, fc_ref, q_max, dur_s, transient_s,
                    lock_confirm_s, tongue_prefac, min_events=10):
    pairs = farey_rationals(q_max)
    pooled = []
    info = []
    for p, q in pairs:
        f_pll = fc_ref * p / q
        if not (5.0 < f_pll < SR * 0.45): continue
        elig = ((t_n_array >= (transient_s + 1.0) * f_pll) &
                (t_n_array <= (dur_s + 1.0) * f_pll))
        elig_t = np.sort(t_n_array[elig])
        threshold = lock_confirm_s * f_pll / (tongue_prefac * (2.0 / (p + q)) ** 2)
        qualifying = elig_t[elig_t >= threshold]
        if qualifying.size < min_events + 1: continue
        spacings = np.diff(qualifying) / f_pll
        if spacings.size == 0 or spacings.mean() <= 0: continue
        pooled.append(spacings / spacings.mean())
        info.append(dict(p=p, q=q, f_pll=f_pll, n_passages=int(qualifying.size)))
    pooled = np.concatenate(pooled) if pooled else np.zeros(0)
    return pooled, info


def ks_to(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    if n < 5: return float('nan'), float('nan')
    F_em = np.arange(1, n + 1) / n
    return float(np.max(np.abs(F_em - theory_cdf(s)))), n


def classify(pooled):
    ks_p, _ = ks_to(pooled, nns_cdf_poisson)
    ks_o, _ = ks_to(pooled, nns_cdf_goe)
    ks_u, _ = ks_to(pooled, nns_cdf_gue)
    n = pooled.size
    pv_p = _ks_pvalue(ks_p, n) if not np.isnan(ks_p) else float('nan')
    pv_o = _ks_pvalue(ks_o, n) if not np.isnan(ks_o) else float('nan')
    pv_u = _ks_pvalue(ks_u, n) if not np.isnan(ks_u) else float('nan')
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    mass03 = float((pooled < 0.3).mean()) if pooled.size else float('nan')
    return dict(ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                  pv_p=pv_p, pv_o=pv_o, pv_u=pv_u,
                  best=best, mass03=mass03, n=n,
                  gap=ks_o - ks_u)


# ── Build all signal lists ────────────────────────────────────────────────────
print("Building signal lists …")
signals = {}

# 1+2. ζ zeros
ZEROS_PATH = os.path.join(THIS_DIR, "zeros_1000.npy")
ZEROS_2000 = os.path.join(THIS_DIR, "zeros_2000.npy")
zeta_1000 = np.load(ZEROS_PATH).astype(np.float64)
signals['ζ_zeros[1..1000]'] = zeta_1000
print(f"  ζ_zeros[1..1000]: range [{zeta_1000.min():.2f}, {zeta_1000.max():.2f}]")

if os.path.exists(ZEROS_2000):
    zeta_2000 = np.load(ZEROS_2000).astype(np.float64)
    signals['ζ_zeros[1001..2000]'] = zeta_2000[1000:2000]
    signals['ζ_zeros[1..2000]'] = zeta_2000
    print(f"  ζ_zeros[1001..2000]: range [{zeta_2000[1000]:.2f}, {zeta_2000[1999]:.2f}]")
    print(f"  ζ_zeros[1..2000]:   range [{zeta_2000[0]:.2f}, {zeta_2000[1999]:.2f}]")
else:
    print(f"  zeros_2000.npy not yet ready, skipping")

# 3. Primes (first N) via sieve
def primes_up_to(N):
    sieve = np.ones(N + 1, dtype=bool); sieve[0] = sieve[1] = False
    for i in range(2, int(np.sqrt(N)) + 1):
        if sieve[i]: sieve[i*i::i] = False
    return np.where(sieve)[0]

primes_n = primes_up_to(20000)
signals['primes[first 1000]'] = primes_n[:1000].astype(np.float64)
signals['primes[first 2000]'] = primes_n[:2000].astype(np.float64)
print(f"  primes[first 1000]: range [{primes_n[0]}, {primes_n[999]}]")
print(f"  primes[first 2000]: range [{primes_n[0]}, {primes_n[1999]}]")

# 4. Squarefree integers (μ ≠ 0)
def squarefree_up_to(N):
    sf = np.ones(N + 1, dtype=bool); sf[0] = False
    for p in primes_up_to(int(np.sqrt(N)) + 1):
        sf[p * p :: p * p] = False
    return np.where(sf)[0]

sf = squarefree_up_to(2500)
signals['squarefree[first 1000]'] = sf[:1000].astype(np.float64)
print(f"  squarefree[first 1000]: range [{sf[0]}, {sf[999]}]")

# 5. Random uniform (Poisson null) in same range as ζ first 1000
rng = np.random.default_rng(0)
poisson_uniform = np.sort(rng.uniform(zeta_1000.min(), zeta_1000.max(), 1000))
signals['poisson_uniform[ζ-range]'] = poisson_uniform
print(f"  poisson_uniform: range [{poisson_uniform.min():.2f}, {poisson_uniform.max():.2f}]")

# 6+7. GUE/GOE eigenvalues (uniform-unfolded, R=2 semicircle)
def semicircle_cdf_unit(x):
    x = np.clip(x, -1.0, 1.0)
    return 0.5 + (x * np.sqrt(1.0 - x * x) + np.arcsin(x)) / np.pi

def gen_gue(N, seed):
    rng = np.random.default_rng(seed)
    A = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * N)
    return np.sort(np.linalg.eigvalsh(H).real)

def gen_goe(N, seed):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((N, N))
    H = (A + A.T) / np.sqrt(2 * N)
    return np.sort(np.linalg.eigvalsh(H))

gue_eigs = gen_gue(1000, 42); gue_unf = semicircle_cdf_unit(gue_eigs / 2.0) * 1000
goe_eigs = gen_goe(1000, 42); goe_unf = semicircle_cdf_unit(goe_eigs / 2.0) * 1000
signals['GUE_eigs[unfolded uniform]'] = gue_unf
signals['GOE_eigs[unfolded uniform]'] = goe_unf
print(f"  GUE_unfolded: range [{gue_unf.min():.2f}, {gue_unf.max():.2f}]")
print(f"  GOE_unfolded: range [{goe_unf.min():.2f}, {goe_unf.max():.2f}]")
print()


# ── Compute analytical NNS for each ───────────────────────────────────────────
print("=" * 100)
print(f"Phase 4 — analytical passage-time NNS @ fc_ref={FC_REF}, q_max={Q_MAX}, "
      f"dur={DUR}s, transient={int(TRANSIENT_S*1000)}ms")
print("=" * 100)
print(f"  {'signal':<28}  {'#PLLs':>5}  {'n':>6}  {'KS_P':>5}  {'KS_O':>5}  "
      f"{'KS_U':>5}  {'gap':>6}  {'mass<0.3':>8}  best")

results = {}
for name, t_k in signals.items():
    pooled, info = analytical_nns(t_k, FC_REF, Q_MAX, DUR, TRANSIENT_S,
                                    LOCK_CONFIRM_S, TONGUE_PREFAC)
    if pooled.size < 50:
        print(f"  {name:<28}  insufficient data (n={pooled.size})")
        results[name] = None
        continue
    cl = classify(pooled)
    results[name] = dict(pooled=pooled, info=info, **cl)
    print(f"  {name:<28}  {len(info):5d}  {cl['n']:6d}  "
          f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
          f"{cl['gap']:+6.3f}  {cl['mass03']:8.3f}  {cl['best']}")
print()
print("  Theoretical mass<0.3:  Poisson 0.259, GOE 0.064, GUE 0.011")
print("  gap = KS_GOE − KS_GUE.  +ve → GUE wins, −ve → GOE wins.  |gap| > 0.05 = decisive.")
print()


# ── Classification verdict ────────────────────────────────────────────────────
print("=" * 100)
print("Classification verdict per signal")
print("=" * 100)
for name, r in results.items():
    if r is None: continue
    decisiveness = "decisive" if abs(r['gap']) > 0.05 else "borderline"
    print(f"  {name:<28}  best={r['best']:<6}  gap={r['gap']:+6.3f} ({decisiveness}),  "
          f"KS_min={min(r['ks_p'], r['ks_o'], r['ks_u']):.3f},  n={r['n']}")
print()


# ── Plot ──────────────────────────────────────────────────────────────────────
n_sigs = sum(1 for r in results.values() if r is not None)
ncols = 3
nrows = (n_sigs + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols, figsize=(13, 3.2 * nrows), sharey=True, sharex=True)
axes = np.array(axes).reshape(-1)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)
i = 0
for name, r in results.items():
    if r is None: continue
    ax = axes[i]; i += 1
    pooled = r['pooled']
    ax.hist(pooled, bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={pooled.size}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.8, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.4)
    ax.set_title(f"{name}\nbest={r['best']}, gap={r['gap']:+.3f}, mass<0.3={r['mass03']:.3f}",
                  fontsize=9)
    ax.grid(True, alpha=0.3)
for j in range(i, len(axes)): axes[j].axis('off')
axes[0].legend(fontsize=7, loc='upper right')
fig.suptitle(f"Phase 4 cross-signal NNS — analytical passage-time, "
              f"q_max={Q_MAX}, fc_ref={FC_REF}")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOT_DIR, "15_phase4_classification.png"), dpi=110)
plt.close(fig)
print(f"  → plots/15_phase4_classification.png")


# ── Pickle results for the writeup ────────────────────────────────────────────
import pickle
out_pkl = os.path.join(THIS_DIR, "phase4_results.pkl")
with open(out_pkl, 'wb') as f:
    pickle.dump({'results': {k: {kk: vv for kk, vv in r.items() if kk not in ('pooled', 'info')}
                              for k, r in results.items() if r is not None},
                  'config': dict(fc_ref=FC_REF, q_max=Q_MAX, dur=DUR, transient_s=TRANSIENT_S,
                                  lock_confirm_s=LOCK_CONFIRM_S, tongue_prefac=TONGUE_PREFAC)},
                 f)
print(f"  → {out_pkl}")
