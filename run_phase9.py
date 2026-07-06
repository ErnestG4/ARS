"""
Phase 9 — Periodic table of point processes.

Run arithmetic_toolkit.full_analysis on six reference signals and produce
a side-by-side fingerprint table.

Signals:
    1. ζ zeros (first 2000 from Odlyzko zeros6, RvM-unfolded)
    2. GOE eigenvalues (N=2000, semicircle-unfolded)
    3. Poisson uniform (2000 events from exp(1) intervals)
    4. Fungal spikes (pooled normalised, Adamatzky data)
    5. USGS earthquakes M ≥ 4.5 (5-year catalog)
    6. Primes ≤ 10⁶ (sieve)

Output:
    data/phase9_fingerprints.json
    plots/31_phase9_table.png
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


# ─── 1. ζ zeros (first 2000) — RvM-unfolded ──────────────────────────────────

def load_zeta_unfolded(n_zeros=2000):
    z6_path = os.path.join(DATA, "odlyzko_zeros6.txt")
    if os.path.exists(z6_path):
        zeros = np.loadtxt(z6_path, max_rows=n_zeros)
    else:
        zeros = np.load(os.path.join(THIS_DIR, "zeros_2000.npy"))
        zeros = zeros[:n_zeros]
    z = np.asarray(zeros, dtype=np.float64)
    # Riemann-von Mangoldt smooth count: N(γ) ≈ (γ/(2π)) ln(γ/(2πe)) + 7/8
    return (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8


# ─── 2. GOE eigenvalues (N=2000) — semicircle-unfolded ───────────────────────

def gen_goe_unfolded(N=2000, seed=42):
    rng = np.random.default_rng(seed)
    M = rng.standard_normal((N, N)) / np.sqrt(2)
    M = (M + M.T) / np.sqrt(2)
    eigs = np.sort(np.linalg.eigvalsh(M))
    R = 2 * np.sqrt(N)
    x = np.clip(eigs / R, -1, 1)
    cdf = (x * np.sqrt(1 - x**2) + np.arcsin(x)) / np.pi + 0.5
    return cdf * N


# ─── 3. Poisson uniform ──────────────────────────────────────────────────────

def gen_poisson_unfolded(N=2000, seed=43):
    rng = np.random.default_rng(seed)
    intervals = rng.exponential(1.0, size=N)
    return np.cumsum(intervals)


# ─── 4. Fungal spikes (pooled) ───────────────────────────────────────────────

def load_fungal_pool(target_n=2000):
    """Re-detect fungal spikes; pool normalised intervals across all units."""
    sys.path.insert(0, THIS_DIR)
    from run_fungal_nns import (load_fungal_csv, detect_spikes,
                                THRESHOLDS, TARGET_LO, TARGET_HI, FUNGI_ROOT)
    import glob
    from pathlib import Path
    files = sorted(p for p in glob.glob(os.path.join(FUNGI_ROOT, '**', '*.csv'),
                                         recursive=True)
                    if 'Zone.Identifier' not in p)
    pool = []
    print(f"  re-detecting fungal spikes from {len(files)} CSVs …")
    for f in files:
        try:
            df = load_fungal_csv(f)
        except Exception:
            continue
        t_arr = df.index.to_numpy()
        for ch in df.columns:
            v = df[ch].to_numpy(dtype=np.float64)
            chosen = None
            for thr in sorted(THRESHOLDS, reverse=True):
                sp = detect_spikes(t_arr, v, threshold_std=thr)
                if TARGET_LO <= sp.size <= TARGET_HI:
                    chosen = sp; break
                if chosen is None or abs(sp.size - 60) < abs(chosen.size - 60):
                    chosen = sp
            if chosen is not None and chosen.size >= 20:
                isi = np.diff(np.sort(chosen))
                if isi.size and isi.mean() > 0:
                    pool.append(isi / isi.mean())
    if not pool:
        return np.zeros(0)
    norm_intervals = np.concatenate(pool)
    print(f"  pooled {norm_intervals.size} normalised inter-spike intervals")
    return np.cumsum(norm_intervals)


# ─── 5. USGS earthquakes ─────────────────────────────────────────────────────

def load_earthquakes_unfolded():
    csv = os.path.join(DATA, "usgs_M45_5yr.csv")
    if not os.path.exists(csv):
        return np.zeros(0)
    df = pd.read_csv(csv, low_memory=False)
    t_col = 'time' if 'time' in df.columns else df.columns[0]
    times = pd.to_datetime(df[t_col], utc=True, errors='coerce').dropna()
    secs = times.astype('int64').to_numpy() / 1e9
    secs = np.sort(secs)
    diffs = np.diff(secs)
    diffs = diffs[diffs > 0]
    if diffs.size == 0: return np.zeros(0)
    return np.cumsum(diffs / diffs.mean())


# ─── 6. Primes ≤ 10⁶ ─────────────────────────────────────────────────────────

def primes_unfolded(N=10**6):
    """Primes ≤ N as raw t_k.  Unfolding uses Cramér: π(t) ≈ t/log t,
       so unfolded position is N_smooth(p) = li(p) ≈ p/log(p)."""
    sieve = np.ones(N + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if sieve[p]:
            sieve[p*p::p] = False
    primes = np.where(sieve)[0].astype(np.float64)
    # Logarithmic unfolding so mean spacing = 1
    return primes / np.log(np.maximum(primes, 2.0))


# ─── Run all signals ──────────────────────────────────────────────────────────

DATASETS = [
    ('ζ zeros (first 2000)',    load_zeta_unfolded,           dict()),
    ('GOE eigenvalues (N=2000)', gen_goe_unfolded,            dict()),
    ('Poisson uniform',         gen_poisson_unfolded,         dict()),
    ('Fungal spikes (pooled)',  load_fungal_pool,             dict()),
    ('USGS earthquakes M≥4.5',  load_earthquakes_unfolded,    dict()),
    ('Primes ≤ 10⁶',            primes_unfolded,              dict()),
]


print("=" * 110)
print("Phase 9 — periodic table of point processes via arithmetic_toolkit")
print("=" * 110)

t0_outer = time.time()
results = {}
for label, loader, kwargs in DATASETS:
    print(f"\n[{label}]")
    t0 = time.time()
    try:
        t_k = loader(**kwargs)
    except Exception as e:
        print(f"  loader failed: {e}")
        results[label] = dict(label=label, error=str(e))
        continue
    if t_k.size < 20:
        print(f"  insufficient events ({t_k.size}) — skipping")
        results[label] = dict(label=label, n_events=int(t_k.size),
                              error='insufficient')
        continue
    print(f"  loaded n={t_k.size}, span={t_k[-1]-t_k[0]:.1f}, "
          f"mean_sp={float(np.diff(t_k).mean()):.4f}")
    res = full_analysis(t_k, label=label)
    results[label] = res
    p = res['primary_nns']
    f = res['fano_curve']
    pc = res['pair_correlation']
    r = res['ramanujan']
    s = res['sb_split']
    pa = res['padic_profile']
    print(f"  n={res['n_events']:,}  best={p['best']}  "
          f"KS_GUE={p['ks_u']:.3f}  KS_GOE={p['ks_o']:.3f}  KS_P={p['ks_p']:.3f}  "
          f"mass<0.3={p['mass03']:.3f}")
    print(f"  F(T=1)={f.get('F_at_1', float('nan')):.3f}  "
          f"F(T=5)={f.get('F_at_5', float('nan')):.3f}  "
          f"F(T=20)={f.get('F_at_20', float('nan')):.3f}")
    print(f"  R₂(0.1)={pc.get('R2_at_0_1', float('nan')):.3f}  "
          f"R₂(1.0)={pc.get('R2_at_1', float('nan')):.3f}  "
          f"repulsion_integral={pc.get('repulsion_integral', float('nan')):.3f}")
    print(f"  top10 Ramanujan q: {r.get('top10_q', [])[:5]}…  peak_q={r.get('peak_q', 0)}")
    print(f"  SB symmetry_ks={s.get('symmetry_ks', float('nan')):.3f}  "
          f"p={s.get('symmetry_p', float('nan')):.3f}")
    print(f"  p-adic dominant prime={pa.get('dominant_prime', 0)}  "
          f"per-prime KS_min: " +
          ", ".join(f"p={p_}: {bp.get('ks_min', 1):.2f}"
                     for p_, bp in (pa.get('best_by_prime') or {}).items()))
    print(f"  ⏱ {time.time() - t0:.1f}s")

print(f"\nTotal elapsed: {time.time() - t0_outer:.1f}s")


# ─── Comparison table ────────────────────────────────────────────────────────

print("\n" + "=" * 130)
print("Periodic table of point processes — fingerprint vectors")
print("=" * 130)
keys = ['KS_GUE', 'KS_GOE', 'KS_Poiss', 'mass<0.3',
        'F(T=1)', 'F(T=5)', 'rep_int',
        'top_ram_q', 'sb_KS', 'p_dom']
header = f"  {'signal':<26}  {'best':<7}  " + " ".join(f"{k:>9}" for k in keys)
print(header)
print("  " + "-" * (len(header) - 2))
for label, _, _ in DATASETS:
    res = results.get(label, {})
    if 'error' in res:
        print(f"  {label:<26}  {res['error']}")
        continue
    fp = res['fingerprint_vector']
    best = res['primary_nns']['best']
    cells = []
    for k, v in zip(keys, fp):
        if k.startswith('top_ram_q') or k == 'p_dom':
            cells.append(f"{int(v):>9d}")
        else:
            cells.append(f"{v:>9.3f}")
    print(f"  {label:<26}  {best:<7}  " + " ".join(cells))


# ─── Save JSON ────────────────────────────────────────────────────────────────

def _trim(res):
    """Drop bulky arrays before JSON — keep summary scalars + fingerprint."""
    if 'error' in res: return res
    out = dict(label=res['label'], n_events=res['n_events'],
               primary_nns=res['primary_nns'],
               fingerprint_vector=res['fingerprint_vector'],
               fingerprint_keys=res['fingerprint_keys'])
    out['fano_summary'] = {k: res['fano_curve'].get(k)
                            for k in ('F_at_1', 'F_at_5', 'F_at_20',
                                      'mean_sp', 'duration')}
    out['ramanujan_summary'] = {k: res['ramanujan'].get(k)
                                 for k in ('peak_q', 'top10_q',
                                           'top10_amplitudes', 'a0')}
    out['pair_correlation_summary'] = {k: res['pair_correlation'].get(k)
                                        for k in ('R2_at_0_1', 'R2_at_0_5',
                                                  'R2_at_1', 'repulsion_integral')}
    out['sb_split_summary'] = res['sb_split']
    out['padic_summary'] = dict(dominant_prime=res['padic_profile']['dominant_prime'],
                                 best_by_prime=res['padic_profile']['best_by_prime'])
    return out


with open(os.path.join(DATA, "phase9_fingerprints.json"), 'w') as fp:
    json.dump({label: _trim(results[label]) for label, _, _ in DATASETS},
              fp, indent=2, default=str)
print(f"\n  → data/phase9_fingerprints.json")


# ─── Plot: fingerprint heatmap ────────────────────────────────────────────────

labels = []
fp_matrix = []
for label, _, _ in DATASETS:
    res = results.get(label)
    if res and 'fingerprint_vector' in res:
        labels.append(label)
        fp_matrix.append(res['fingerprint_vector'])

if fp_matrix:
    fp_arr = np.asarray(fp_matrix)
    # Normalise each column (across signals) for visual comparison
    col_min = np.nanmin(fp_arr, axis=0)
    col_max = np.nanmax(fp_arr, axis=0)
    rng = np.where(col_max > col_min, col_max - col_min, 1.0)
    fp_norm = (fp_arr - col_min) / rng

    fig, ax = plt.subplots(figsize=(11, 5))
    im = ax.imshow(fp_norm, aspect='auto', cmap='RdBu_r',
                   vmin=0, vmax=1)
    ax.set_xticks(range(len(keys)), labels=keys, rotation=45, ha='right')
    ax.set_yticks(range(len(labels)), labels=labels)
    for i in range(len(labels)):
        for j in range(len(keys)):
            ax.text(j, i, f"{fp_arr[i, j]:.2f}",
                    ha='center', va='center',
                    fontsize=7,
                    color='white' if abs(fp_norm[i, j] - 0.5) > 0.3 else 'black')
    ax.set_title("Periodic table of point processes — fingerprint vectors")
    fig.colorbar(im, ax=ax, label='normalised across signals')
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "31_phase9_table.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/31_phase9_table.png")
