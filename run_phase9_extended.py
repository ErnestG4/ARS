"""
Phase 9 extended — apply arithmetic_toolkit.full_analysis to:

  - GUE eigenvalues (N=2000) — calibrator for the GUE class
  - ζ zeros low (first 100k from zeros6, RvM-unfolded)
  - ζ zeros high (last 100k from zeros6 ≈ heights 1.1M)
  - LMFDB EC L-functions (pooled normalised inter-zero spacings)
  - Dirichlet L-functions (pooled normalised inter-zero spacings)
  - Primes ≤ 10⁵, 10⁶, 10⁷ (logarithmic-unfold) — convergence study

Run with q_max=16 in the p-adic and SB-split engines (vs default q_max=8)
to give the p-adic profile non-trivial p ∈ {11, 13} separation.

Output:
    data/phase9_extended_fingerprints.json
    plots/32_phase9_extended.png
"""
import os, sys, json, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import full_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
Q_MAX = 16


# ─── Generators / loaders ────────────────────────────────────────────────────

def gen_gue_unfolded(N=2000, seed=42):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
    H = (A + A.conj().T) / 2 / np.sqrt(2)
    eigs = np.sort(np.linalg.eigvalsh(H))
    R = 2 * np.sqrt(N)
    x = np.clip(eigs / R, -1, 1)
    cdf = (x * np.sqrt(1 - x**2) + np.arcsin(x)) / np.pi + 0.5
    return cdf * N


def load_zeta_band(start, n=100_000):
    z6 = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"),
                    skiprows=start, max_rows=n)
    return (z6 / (2*np.pi)) * np.log(np.maximum(z6 / (2*np.pi*np.e), 1.0)) + 7/8


def load_lmfdb_pool():
    """Pool normalised inter-zero spacings across all LMFDB EC curves."""
    with open(os.path.join(DATA, "lmfdb_zeros.json")) as f:
        curves = json.load(f)
    pool = []
    for c in curves:
        z = np.asarray(c['zeros'], dtype=np.float64)
        z = z[z > 0]
        if z.size < 50: continue
        cond = c['conductor']
        u = (z / (2*np.pi)) * (np.log(np.maximum(cond * z / (2*np.pi), 1.0)) - 1.0)
        sp = np.diff(u)
        sp = sp[sp > 0]
        if sp.size and sp.mean() > 0:
            pool.append(sp / sp.mean())
    if not pool: return np.zeros(0)
    return np.cumsum(np.concatenate(pool))


def load_dirichlet_pool():
    with open(os.path.join(DATA, "dirichlet_zeros.json")) as f:
        chars = json.load(f)
    pool = []
    for c in chars:
        z = np.asarray(c['zeros'], dtype=np.float64)
        z = z[z > 0]
        if z.size < 50: continue
        cond = c['conductor']
        u = (z / (2*np.pi)) * (np.log(np.maximum(cond * z / (2*np.pi), 1.0)) - 1.0)
        sp = np.diff(u)
        sp = sp[sp > 0]
        if sp.size and sp.mean() > 0:
            pool.append(sp / sp.mean())
    if not pool: return np.zeros(0)
    return np.cumsum(np.concatenate(pool))


def primes_unfolded(N):
    sieve = np.ones(N + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if sieve[p]:
            sieve[p*p::p] = False
    primes = np.where(sieve)[0].astype(np.float64)
    return primes / np.log(np.maximum(primes, 2.0))


# ─── Run ──────────────────────────────────────────────────────────────────────

DATASETS = [
    ('GUE eigenvalues (N=2000)',  lambda: gen_gue_unfolded()),
    ('ζ low (first 100k zeros)',  lambda: load_zeta_band(start=0, n=100_000)),
    ('ζ high (heights ~1.1M)',    lambda: load_zeta_band(start=1_900_000, n=100_000)),
    ('LMFDB EC L-functions',      load_lmfdb_pool),
    ('Dirichlet L (q ≤ 149)',     load_dirichlet_pool),
    ('Primes ≤ 10⁵',              lambda: primes_unfolded(10**5)),
    ('Primes ≤ 10⁶',              lambda: primes_unfolded(10**6)),
    ('Primes ≤ 10⁷',              lambda: primes_unfolded(10**7)),
]


print("=" * 130)
print(f"Phase 9 extended — full_analysis with q_max={Q_MAX}")
print("=" * 130)

results = {}
t0_outer = time.time()
for label, loader in DATASETS:
    print(f"\n[{label}]")
    t0 = time.time()
    try:
        t_k = loader()
    except Exception as e:
        print(f"  loader failed: {e}")
        results[label] = dict(label=label, error=str(e))
        continue
    if t_k.size < 20:
        print(f"  insufficient ({t_k.size})")
        results[label] = dict(label=label, n_events=int(t_k.size), error='insufficient')
        continue
    print(f"  loaded n={t_k.size:,}  span={t_k[-1]-t_k[0]:.1f}  "
          f"mean_sp={float(np.diff(t_k).mean()):.4f}")
    res = full_analysis(t_k, label=label, q_max=Q_MAX)
    results[label] = res
    p = res['primary_nns']; f = res['fano_curve']; pc = res['pair_correlation']
    pa = res['padic_profile']; sbs = res['sb_split']; r = res['ramanujan']
    print(f"  best={p['best']:<7}  KS_GUE={p['ks_u']:.3f}  KS_GOE={p['ks_o']:.3f}  "
          f"KS_P={p['ks_p']:.3f}  mass<0.3={p['mass03']:.3f}")
    print(f"  F(T=1)={f.get('F_at_1', float('nan')):.3f}  "
          f"F(T=5)={f.get('F_at_5', float('nan')):.3f}  "
          f"rep_int={pc.get('repulsion_integral', 0):.3f}  "
          f"R₂(0.1)={pc.get('R2_at_0_1', 0):.3f}")
    print(f"  top10 Ramanujan q: {r.get('top10_q', [])[:5]}…  peak_q={r.get('peak_q', 0)}")
    print(f"  SB symmetry_ks={sbs.get('symmetry_ks', float('nan')):.4f}  "
          f"p={sbs.get('symmetry_p', float('nan')):.3f}")
    bp = pa.get('best_by_prime', {})
    pad_str = ", ".join(f"p={pp}: {b.get('ks_min', 1):.3f}" for pp, b in bp.items())
    print(f"  p-adic dominant prime={pa.get('dominant_prime', 0)}    {pad_str}")
    print(f"  ⏱ {time.time() - t0:.1f}s")

print(f"\nTotal elapsed: {time.time() - t0_outer:.1f}s")


# ─── Comparison table ────────────────────────────────────────────────────────

print("\n" + "=" * 140)
print("Extended periodic table — fingerprint vectors @ q_max=" + str(Q_MAX))
print("=" * 140)
keys = ['KS_GUE', 'KS_GOE', 'KS_Poiss', 'mass<0.3',
        'F(T=1)', 'F(T=5)', 'rep_int',
        'top_ram_q', 'sb_KS', 'p_dom']
header = f"  {'signal':<28}  {'best':<7}  " + " ".join(f"{k:>9}" for k in keys)
print(header)
print("  " + "-" * (len(header) - 2))
for label, _ in DATASETS:
    res = results.get(label, {})
    if 'error' in res:
        print(f"  {label:<28}  {res['error']}")
        continue
    fp = res['fingerprint_vector']
    best = res['primary_nns']['best']
    cells = []
    for k, v in zip(keys, fp):
        if k.startswith('top_ram_q') or k == 'p_dom':
            cells.append(f"{int(v):>9d}")
        else:
            cells.append(f"{v:>9.3f}")
    print(f"  {label:<28}  {best:<7}  " + " ".join(cells))


# ─── Save JSON ────────────────────────────────────────────────────────────────

def _trim(res):
    if 'error' in res: return res
    out = dict(label=res['label'], n_events=res['n_events'],
               primary_nns=res['primary_nns'],
               fingerprint_vector=res['fingerprint_vector'],
               fingerprint_keys=res['fingerprint_keys'],
               fano_summary={k: res['fano_curve'].get(k)
                             for k in ('F_at_1', 'F_at_5', 'F_at_20',
                                       'mean_sp', 'duration')},
               ramanujan_summary={k: res['ramanujan'].get(k)
                                  for k in ('peak_q', 'top10_q', 'top10_amplitudes')},
               pair_correlation_summary={k: res['pair_correlation'].get(k)
                                         for k in ('R2_at_0_1', 'R2_at_0_5',
                                                   'R2_at_1', 'repulsion_integral')},
               sb_split_summary=res['sb_split'],
               padic_summary=dict(dominant_prime=res['padic_profile']['dominant_prime'],
                                  best_by_prime=res['padic_profile']['best_by_prime']))
    return out


with open(os.path.join(DATA, "phase9_extended_fingerprints.json"), 'w') as fp:
    json.dump({l: _trim(results[l]) for l, _ in DATASETS}, fp, indent=2, default=str)
print(f"\n  → data/phase9_extended_fingerprints.json")


# ─── Plot ────────────────────────────────────────────────────────────────────

labels = []
fp_matrix = []
for label, _ in DATASETS:
    r = results.get(label)
    if r and 'fingerprint_vector' in r:
        labels.append(label); fp_matrix.append(r['fingerprint_vector'])

if fp_matrix:
    M = np.asarray(fp_matrix)
    col_min = np.nanmin(M, axis=0); col_max = np.nanmax(M, axis=0)
    rng = np.where(col_max > col_min, col_max - col_min, 1.0)
    M_n = (M - col_min) / rng

    fig, ax = plt.subplots(figsize=(13, 0.55 * len(labels) + 2))
    im = ax.imshow(M_n, aspect='auto', cmap='RdBu_r', vmin=0, vmax=1)
    ax.set_xticks(range(len(keys)), labels=keys, rotation=45, ha='right')
    ax.set_yticks(range(len(labels)), labels=labels, fontsize=9)
    for i in range(len(labels)):
        for j in range(len(keys)):
            ax.text(j, i, f"{M[i, j]:.2f}", ha='center', va='center',
                    fontsize=7,
                    color='white' if abs(M_n[i, j] - 0.5) > 0.32 else 'black')
    ax.set_title(f"Extended periodic table of point processes — q_max={Q_MAX}")
    fig.colorbar(im, ax=ax, label='normalised across signals')
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "32_phase9_extended.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/32_phase9_extended.png")
