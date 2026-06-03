"""Mertens M(x) and Liouville L(x) running-sum zero crossings.

Two classical arithmetic functions, both partial sums of multiplicative
sign sequences (μ and λ).  The locations where M(x) and L(x) change
sign form arithmetic point processes whose level statistics are not
predicted by any standard random matrix theory result — this is novel
empirical data.

Computed up to x = 10^7 via sieve.

  M(x) = Σ_{n ≤ x} μ(n)         — Mertens function (Möbius partial sum)
  L(x) = Σ_{n ≤ x} λ(n)         — Liouville function partial sum

Both are integer-valued at integer x and the "zero crossings" we record
are integers x where M(x) (or L(x)) changes sign relative to its previous
value.  That gives us a sequence of integers; we apply the same analytical
NNS classifier as for the L-function families.

Output:
    data/mertens_liouville_results.json
    plots/21_mertens_liouville.png
"""
import os, sys, time, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '$HOME/fmexplorer/riemann_explorer')

from pll_bank import farey_rationals
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    _ks_pvalue,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


N_MAX = 10**7
DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")


# ─── Sieve μ(n) and λ(n) up to N_MAX ──────────────────────────────────────────
print(f"Sieving μ and λ up to N = {N_MAX:.0e}…")
t0 = time.perf_counter()


def mu_lambda_sieve(N):
    """Compute μ(n) and λ(n) for n = 1..N via sieve."""
    smallest_p = np.zeros(N + 1, dtype=np.int32)
    for p in range(2, int(np.sqrt(N)) + 1):
        if smallest_p[p] == 0:
            smallest_p[p::p] = np.where(smallest_p[p::p] == 0, p, smallest_p[p::p])
    for p in range(int(np.sqrt(N)) + 1, N + 1):
        if smallest_p[p] == 0: smallest_p[p] = p
    mu  = np.zeros(N + 1, dtype=np.int8)
    lam = np.zeros(N + 1, dtype=np.int8)
    mu[1] = 1; lam[1] = 1
    for n in range(2, N + 1):
        p = smallest_p[n]; m = n // p
        # μ(n)
        if m % p == 0: mu[n] = 0          # squareful
        else:          mu[n] = -mu[m]
        # λ(n) = (-1)^Ω(n) — same recurrence but no squarefree filter
        lam[n] = -lam[m]
    return mu, lam


mu, lam = mu_lambda_sieve(N_MAX)
print(f"  done in {time.perf_counter()-t0:.1f}s")
print(f"  Σ μ(n)/n verification (should approach 0): "
      f"Σ_{{n≤1000}} μ(n) = {mu[:1001].sum()}, "
      f"Σ_{{n≤10000}} μ(n) = {mu[:10001].sum()}, "
      f"Σ_{{n≤100000}} μ(n) = {mu[:100001].sum()}")
print()


# ─── Compute M(x), L(x) and zero-crossing positions ───────────────────────────
M = np.cumsum(mu.astype(np.int64))     # M(0) = 0, M(N) = Σ_{n=1..N} μ(n)
L = np.cumsum(lam.astype(np.int64))


def find_sign_changes(seq):
    """Return integer x values where seq[x-1] and seq[x] have opposite signs."""
    s = np.sign(seq[1:])    # consider M(1) onwards
    nonzero_mask = s != 0
    s_nz = s[nonzero_mask]
    nz_idx = np.where(nonzero_mask)[0]   # indices into seq[1:] (0-based)
    changes = np.where(np.diff(s_nz) != 0)[0]
    return nz_idx[changes + 1] + 1       # actual x values where sign changed


M_zeros = find_sign_changes(M)
L_zeros = find_sign_changes(L)
print(f"  M(x) sign changes for x ≤ {N_MAX:.0e}: {M_zeros.size}")
print(f"  L(x) sign changes for x ≤ {N_MAX:.0e}: {L_zeros.size}")
print(f"  M(x) range: [{M[1:].min()}, {M[1:].max()}]")
print(f"  L(x) range: [{L[1:].min()}, {L[1:].max()}]")
print()


# ─── Pólya conjecture failure region for L (well-known: starts ~906,150,257) ──
# We only see up to 10^7 here so we won't see the failure point itself, but the
# direction of L should be measurable.
print(f"  L(10^4) = {L[10000]}, L(10^5) = {L[100000]}, "
      f"L(10^6) = {L[1000000]}, L(10^7) = {L[N_MAX]}")
print(f"  M(10^4) = {M[10000]}, M(10^5) = {M[100000]}, "
      f"M(10^6) = {M[1000000]}, M(10^7) = {M[N_MAX]}")
print()


# ─── Analytical NNS on the zero-crossing positions ────────────────────────────
SR = 44100.0; DUR = 300.0; Q_MAX = 8
LOCK_CONFIRM_S = 20e-3; TONGUE_PREFAC = 0.05; TRANSIENT_S = 0.5


def analytical_nns(t_n_array, fc_ref):
    pairs = farey_rationals(Q_MAX)
    pooled, info = [], []
    for p, q in pairs:
        f_pll = fc_ref * p / q
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
    return dict(n=n, ks_p=ks_p, ks_o=ks_o, ks_u=ks_u, gap=ks_o - ks_u,
                mass03=float((pooled < 0.3).mean()), best=best)


# Use multiple fc_refs since these are huge integer ranges
print("=" * 100)
print("Mertens / Liouville sign-change positions: analytical passage-time NNS")
print("=" * 100)
print(f"  {'signal':<22}  {'fc_ref':>9}  {'#PLLs':>5}  {'n_pool':>7}  "
      f"{'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  {'gap':>6}  best")
results = []
for sig_name, t_n in [('Mertens M(x) sign-x', M_zeros.astype(np.float64)),
                       ('Liouville L(x) sign-x', L_zeros.astype(np.float64))]:
    # Pick fc_ref so the bands cover the data
    median_x = float(np.median(t_n))
    fc_ref = median_x / 100.0   # so the 1:1 PLL has events spread over recording
    pooled, info = analytical_nns(t_n, fc_ref)
    cl = classify(pooled)
    results.append(dict(name=sig_name, fc_ref=fc_ref, t_n=t_n, **cl))
    if cl.get('best') == 'insufficient':
        print(f"  {sig_name:<22}  {fc_ref:9.1f}  {len(info):>5}  {cl['n']:>7}  "
              f"insufficient")
    else:
        print(f"  {sig_name:<22}  {fc_ref:9.1f}  {len(info):>5}  {cl['n']:>7}  "
              f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['best']}")


# ─── Direct NNS (without per-PLL framework) for comparison ────────────────────
print()
print("=" * 100)
print("Direct NNS of sign-change spacings (normalised by mean)")
print("=" * 100)
print(f"  {'signal':<22}  {'n':>6}  {'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  "
      f"{'gap':>6}  {'mass<0.3':>8}  best")

def direct_nns(events):
    e = np.sort(np.asarray(events, dtype=np.float64))
    sp = np.diff(e)
    if sp.size == 0 or sp.mean() <= 0: return np.zeros(0)
    return sp / sp.mean()

direct_results = []
for sig_name, evt in [('Mertens M(x)', M_zeros), ('Liouville L(x)', L_zeros)]:
    sp = direct_nns(evt)
    cl = classify(sp)
    direct_results.append(dict(name=sig_name, **cl, spacings=sp))
    if cl.get('best') == 'insufficient':
        n_evt = evt.size
        note = '(Pólya: L(x) ≤ 0 for almost all x ≤ 906,150,257; '\
               f'we see {n_evt} sign-changes, < 50 spacings)' \
               if 'Liouville' in sig_name else \
               f'(only {cl["n"]} spacings, need ≥ 50)'
        print(f"  {sig_name:<22}  {cl['n']:>6}  insufficient  {note}")
    else:
        print(f"  {sig_name:<22}  {cl['n']:>6}  {cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  "
              f"{cl['ks_u']:5.3f}  {cl['gap']:+6.3f}  {cl['mass03']:8.3f}  {cl['best']}")
print()


# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex='col')
s_grid = np.linspace(0.001, 4.0, 200); bin_edges = np.linspace(0, 4, 41)

# Top row: M(x) and L(x) trajectories + sign-change density
xs_show = np.arange(1, N_MAX + 1)[::1000]
M_show  = M[1:N_MAX+1:1000]
L_show  = L[1:N_MAX+1:1000]
axes[0,0].plot(xs_show, M_show, lw=0.5, color='C0')
axes[0,0].axhline(0, color='k', lw=0.3)
axes[0,0].set_title(f"M(x) for x ≤ {N_MAX:.0e},  {M_zeros.size} sign changes")
axes[0,0].set_xlabel('x'); axes[0,0].set_ylabel('M(x)')
axes[0,1].plot(xs_show, L_show, lw=0.5, color='C3')
axes[0,1].axhline(0, color='k', lw=0.3)
axes[0,1].set_title(f"L(x) for x ≤ {N_MAX:.0e},  {L_zeros.size} sign changes")
axes[0,1].set_xlabel('x'); axes[0,1].set_ylabel('L(x)')

axes[0,2].hist(np.log10(np.diff(M_zeros)), bins=40, alpha=0.6, color='C0',
                label=f'M ({M_zeros.size-1} gaps)', density=True)
axes[0,2].hist(np.log10(np.diff(L_zeros)), bins=40, alpha=0.6, color='C3',
                label=f'L ({L_zeros.size-1} gaps)', density=True)
axes[0,2].set_xlabel('log10(gap between sign changes)')
axes[0,2].set_title('gap-size distribution')
axes[0,2].legend(fontsize=8)
axes[0,2].grid(True, alpha=0.3)

# Bottom row: NNS histograms (direct)
for ax, r in zip(axes[1, :2], direct_results):
    if r.get('best') == 'insufficient':
        ax.set_title(f"{r['name']} direct NNS\n(insufficient sign changes)", fontsize=9)
        ax.text(0.5, 0.5, '<insufficient data>', ha='center', va='center',
                transform=ax.transAxes, fontsize=10, color='gray')
        continue
    ax.hist(r['spacings'], bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={r['n']}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.2, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.4)
    ax.set_title(f"{r['name']} direct NNS\nbest={r['best']}, KS_P={r['ks_p']:.3f}, "
                  f"KS_GUE={r['ks_u']:.3f}", fontsize=9)
    ax.set_xlabel('normalised spacing s')
    ax.grid(True, alpha=0.3)
axes[1, 2].axis('off')
axes[1, 0].set_ylabel('P(s)')
axes[1, 0].legend(fontsize=7, loc='upper right')
fig.suptitle(f"Mertens M(x) and Liouville L(x) sign-change statistics (x ≤ 10^7)")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOTS, "21_mertens_liouville.png"), dpi=110)
plt.close(fig)
print(f"  → plots/21_mertens_liouville.png")

# Save results
with open(os.path.join(DATA, "mertens_liouville_results.json"), 'w') as f:
    json.dump({
        'N_max': N_MAX,
        'mertens': {
            'n_sign_changes': int(M_zeros.size),
            'M_at_decades': [int(M[10**k]) for k in range(1, 8)],
            'analytical_nns': {k: v for k, v in results[0].items() if k != 't_n'},
            'direct_nns': {k: v for k, v in direct_results[0].items() if k != 'spacings'},
        },
        'liouville': {
            'n_sign_changes': int(L_zeros.size),
            'L_at_decades': [int(L[10**k]) for k in range(1, 8)],
            'analytical_nns': {k: v for k, v in results[1].items() if k != 't_n'},
            'direct_nns': {k: v for k, v in direct_results[1].items() if k != 'spacings'},
        },
    }, f, indent=2, default=str)
print(f"  → data/mertens_liouville_results.json")
