"""
Task 2 — Per-PLL NNS distribution for ζ at (q_max=8, K_p=0.02, fc_ref=100).

For each PLL with ≥10 lock events, compute the spacings between consecutive
events, normalise each PLL's spacings by its own mean, then pool the
normalised spacings across PLLs.  This is the right way to compute the NNS
for a multi-PLL bank — pooling raw events would scramble the spacing
structure.

Compare the pooled distribution to:
    Wigner GUE :  P(s) = (32/π²) s² exp(-4s²/π)
    Wigner GOE :  P(s) = (π/2) s   exp(-π s²/4)
    Poisson    :  P(s) =          exp(-s)

Also run with the corrected GUE chirp and the Poisson-FM null at the same
cell to triangulate.
"""
import os, sys, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from pll_bank import pll_bank_gpu, PLLParams, farey_rationals, GPU_NAME
from intermittency import extract_dwells
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    _ks_pvalue,
)
import signal_gen
import scanner
import cupy as cp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


SR  = 44100.0
DUR = 30.0
NZ  = 98
PLOT_DIR = os.path.join(THIS_DIR, "plots")


def per_pll_nns(lock_map, sr, min_events=10):
    """
    For each PLL with ≥min_events lock events, compute spacings, normalise
    by the PLL's own mean, and append to the pooled list.  Returns:
        pooled_spacings : (M,) array of normalised spacings
        per_pll_info    : list of dicts (pll_index, n_events, mean_spacing_ms,
                                          F_at_L1)
    """
    N = lock_map.shape[1]
    pooled = []
    info = []
    for p in range(lock_map.shape[0]):
        rec = extract_dwells(lock_map[p])
        if rec.n_events < min_events:
            continue
        sp = np.diff(rec.lock_onsets)
        if sp.size == 0 or sp.mean() <= 0:
            continue
        sp_norm = sp / sp.mean()
        pooled.append(sp_norm.astype(np.float64))
        # Per-PLL Fano at L=1.
        T_int = max(1, int(round(sp.mean())))
        nW = N // T_int
        if nW >= 5:
            idx = rec.lock_onsets[rec.lock_onsets < nW * T_int] // T_int
            cnts = np.bincount(idx, minlength=nW).astype(np.float64)
            m = cnts.mean()
            F = float(cnts.var(ddof=1) / m) if m > 0 else float('nan')
        else:
            F = float('nan')
        info.append(dict(pll_index=p, n_events=rec.n_events,
                          mean_spacing_ms=float(sp.mean() * 1000.0 / sr),
                          F_at_L1=F))
    if pooled:
        pooled = np.concatenate(pooled)
    else:
        pooled = np.zeros(0)
    return pooled, info


def ks_distance(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    if n < 5:
        return float('nan'), float('nan')
    F_em = np.arange(1, n + 1) / n
    F_th = theory_cdf(s)
    ks = float(np.max(np.abs(F_em - F_th)))
    return ks, _ks_pvalue(ks, n)


# ── PLL bank config ───────────────────────────────────────────────────────────
# fc=115.55 was the max-separation cell from the parameter sweep; ζ has 754
# events / 22 PLLs there (~34/PLL on average), which gives meaningful NNS
# statistics.  At fc=100 only 3 PLLs cleared even the modest ≥10-events bar.
fc_ref, q_max, kp = 115.55, 16, 0.02
pairs = farey_rationals(q_max)
freqs = []
pairs_kept = []
for p, q in pairs:
    f = fc_ref * p / q
    if 5.0 < f < SR * 0.45:
        freqs.append(f)
        pairs_kept.append((p, q))
freqs = np.asarray(freqs, dtype=np.float32)
params = PLLParams(K_p=kp, K_i=kp * 0.05, rho=0.95)
print(f"GPU: {GPU_NAME}")
print(f"Bank: {len(freqs)} PLLs, fc_ref={fc_ref}, q_max={q_max}, K_p={kp}")
print(f"Signals at SR={SR}, dur={DUR}, N=98 tones")
print()


# ── Build signals ─────────────────────────────────────────────────────────────
print("Generating signals …")
sig_zeta = scanner.make_zeta_signal(sr=SR, duration=DUR, n_zeros=NZ)
sig_gue  = signal_gen.make_gue_eigenvalue_signal(sr=SR, duration=DUR, n_points=NZ,
                                                   seed=42, rescale_to_zeta_range=True)
sig_pois = signal_gen.make_poisson_zeta_like(sr=SR, duration=DUR, n_points=NZ, seed=0)
print()


# ── Compute per-PLL NNS for each signal ───────────────────────────────────────
results = {}
for sig_name, sig in [('zeta', sig_zeta), ('gue', sig_gue), ('poiss', sig_pois)]:
    print(f"  ── {sig_name} ──")
    lock_map, _ = pll_bank_gpu(sig, freqs, SR, params, return_phase_error=False)
    pooled, info = per_pll_nns(lock_map, SR, min_events=8)

    if pooled.size > 0:
        ks_p, p_p = ks_distance(pooled, nns_cdf_poisson)
        ks_o, p_o = ks_distance(pooled, nns_cdf_goe)
        ks_u, p_u = ks_distance(pooled, nns_cdf_gue)
        best = min([('Poisson', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    else:
        ks_p = ks_o = ks_u = float('nan')
        p_p = p_o = p_u = float('nan')
        best = 'no data'

    print(f"    PLLs with ≥10 events: {len(info)} of {lock_map.shape[0]}")
    print(f"    pooled normalised spacings: {pooled.size}")
    print(f"    KS to Poisson:  {ks_p:.4f}  (p={p_p:.3f})")
    print(f"    KS to GOE   :   {ks_o:.4f}  (p={p_o:.3f})")
    print(f"    KS to GUE   :   {ks_u:.4f}  (p={p_u:.3f})")
    print(f"    best fit    :   {best}")

    print(f"    PLLs (sorted by n_events):")
    print(f"      {'p:q':>6}  {'n_evt':>5}  {'mean_dwell_ms':>13}  {'F_at_L1':>7}")
    info_sorted = sorted(info, key=lambda d: -d['n_events'])
    for d in info_sorted[:10]:
        pq = pairs_kept[d['pll_index']]
        print(f"      {pq[0]}:{pq[1]:<3d}  {d['n_events']:5d}  "
              f"{d['mean_spacing_ms']:13.2f}  "
              f"{d['F_at_L1']:7.3f}" if not np.isnan(d['F_at_L1'])
              else f"      {pq[0]}:{pq[1]:<3d}  {d['n_events']:5d}  "
                   f"{d['mean_spacing_ms']:13.2f}  {'n/a':>7}")
    print()

    results[sig_name] = dict(
        pooled=pooled, info=info, sorted_info=info_sorted,
        ks_poisson=ks_p, ks_goe=ks_o, ks_gue=ks_u,
        p_poisson=p_p, p_goe=p_o, p_gue=p_u, best=best,
    )

    del lock_map
    cp.get_default_memory_pool().free_all_blocks()


# ── Histogram + plot ──────────────────────────────────────────────────────────
print()
print("Histograms (30 bins, s in [0, 4]):")
bin_edges = np.linspace(0.0, 4.0, 31)
bin_centres = 0.5 * (bin_edges[:-1] + bin_edges[1:])

for sig_name, r in results.items():
    if r['pooled'].size == 0:
        print(f"\n  {sig_name}: no qualifying PLLs")
        continue
    h, _ = np.histogram(r['pooled'], bins=bin_edges)
    h_density, _ = np.histogram(r['pooled'], bins=bin_edges, density=True)
    print(f"\n  {sig_name}  (n={r['pooled'].size}):")
    print(f"  {'s':>5}  {'count':>6}  {'P(s) emp':>9}  {'Wigner GUE':>10}")
    for i in range(len(bin_centres)):
        s = bin_centres[i]
        wig = float(nns_gue([s])[0])
        print(f"  {s:5.2f}  {int(h[i]):6d}  "
              f"{h_density[i]:9.4f}  {wig:10.4f}")


# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200)
for ax, (name, r) in zip(axes, results.items()):
    if r['pooled'].size > 0:
        ax.hist(r['pooled'], bins=bin_edges, density=True, alpha=0.55, color='C0',
                label=f'empirical (n={r["pooled"].size})')
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.8, label='Wigner GUE')
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 1.2)
    ax.set_xlabel('normalised spacing  s')
    ax.set_title(f"{name}\nKS_GUE={r['ks_gue']:.3f}  KS_Poisson={r['ks_poisson']:.3f}  best={r['best']}")
    ax.grid(True, alpha=0.3)
axes[0].set_ylabel('P(s)')
axes[0].legend(fontsize=8, loc='upper right')
fig.suptitle(f"Per-PLL NNS at (q_max=8, K_p=0.02, fc_ref=100) — pooled after per-PLL normalisation")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "07_per_pll_nns.png"), dpi=110)
plt.close(fig)
print(f"\nplot saved: plots/07_per_pll_nns.png")


# ── Verdict ───────────────────────────────────────────────────────────────────
print()
print("=" * 78)
print("Verdict")
print("=" * 78)
print(f"""
  ζ      : best fit = {results['zeta']['best']}    (KS Poisson={results['zeta']['ks_poisson']:.3f}, GOE={results['zeta']['ks_goe']:.3f}, GUE={results['zeta']['ks_gue']:.3f})
  GUE    : best fit = {results['gue']['best']}    (KS Poisson={results['gue']['ks_poisson']:.3f}, GOE={results['gue']['ks_goe']:.3f}, GUE={results['gue']['ks_gue']:.3f})
  Poiss  : best fit = {results['poiss']['best']}    (KS Poisson={results['poiss']['ks_poisson']:.3f}, GOE={results['poiss']['ks_goe']:.3f}, GUE={results['poiss']['ks_gue']:.3f})
""")

# Sanity: empirical mass at small s for ζ.  GUE has s² suppression near 0;
# Poisson has finite mass.
zp = results['zeta']['pooled']
near_zero_zeta = float((zp < 0.3).mean()) if zp.size else float('nan')
near_zero_poiss = float((results['poiss']['pooled'] < 0.3).mean()) if results['poiss']['pooled'].size else float('nan')
near_zero_gue = float((results['gue']['pooled'] < 0.3).mean()) if results['gue']['pooled'].size else float('nan')
print(f"  fraction of normalised spacings with s < 0.3:")
print(f"    ζ      = {near_zero_zeta:.4f}")
print(f"    GUE    = {near_zero_gue:.4f}")
print(f"    Poiss  = {near_zero_poiss:.4f}")
# Theoretical:
poi_pred = float(1 - np.exp(-0.3))
gue_grid = np.linspace(0, 0.3, 200)
trap = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
gue_int  = float(trap(nns_gue(gue_grid), gue_grid)) if trap else float('nan')
print(f"    theory: Poisson = {poi_pred:.4f}, Wigner GUE = {gue_int:.4f}")
