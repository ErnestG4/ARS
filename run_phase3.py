"""
Task 2 — Phase 3 universality stats on three signals at two cells.

Cells:
    (q_max=16, K_p=0.20, fc_ref=115.55)   ← max signal-vs-null separation
    (q_max=16, K_p=0.02, fc_ref=115.55)   ← tongue boundary, most stable

Signals: ζ zeros, GUE-eigenvalue chirp, Poisson-FM null.

For each (signal, cell): compute aggregate-unfolded-pooled events then
NNS, pair correlation, number variance, spectral form factor.  Compare
NNS to analytical Poisson / GOE / GUE forms via KS distance, and report
which is the best fit.
"""
import os, sys, time
import numpy as np
import h5py

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from pll_bank import pll_bank_gpu, PLLParams, farey_rationals, GPU_NAME
from intermittency import extract_dwells, aggregate_unfolded_events
from universality import compute_nns, number_variance, spectral_form_factor, pair_correlation
import signal_gen
import cupy as cp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


SR  = 44100.0
DUR = 30.0
NZ  = 100
PLOT_DIR = os.path.join(THIS_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

CELLS = [
    dict(name="max-sep", q_max=16, K_p=0.20, fc_ref=115.55),
    dict(name="boundary", q_max=16, K_p=0.02, fc_ref=115.55),
]

print("Generating signals …")
signals = {
    'zeta':  signal_gen.make_zeta_signal(sr=SR, duration=DUR, n_zeros=NZ),
    'gue':   signal_gen.make_gue_eigenvalue_signal(sr=SR, duration=DUR, n_points=NZ, seed=42),
    'poiss': signal_gen.make_poisson_zeta_like(sr=SR, duration=DUR, n_points=NZ, seed=0),
}
for k, s in signals.items():
    print(f"  {k:8s}: RMS={np.sqrt(np.mean(s.astype(np.float64)**2)):.5f}")
print(f"GPU: {GPU_NAME}\n")


def run_pll_bank(signal, fc_ref, q_max, kp):
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
    lock_map, _ = pll_bank_gpu(signal, freqs, SR, params, return_phase_error=False)
    return lock_map, freqs, pairs_kept


def aggregate_events_for_cell(lock_map, sr):
    """Per-PLL onsets, unfolded by per-PLL mean spacing, pooled, then re-unfolded
    so the pooled-mean-spacing = 1.  This is the input format for universality."""
    onsets_all = []
    for p in range(lock_map.shape[0]):
        rec = extract_dwells(lock_map[p])
        onsets_all.append(rec.lock_onsets)
    pooled = aggregate_unfolded_events(onsets_all)
    if pooled.size < 5:
        return pooled, [r.size for r in onsets_all]
    spacings = np.diff(pooled)
    if spacings.size == 0 or spacings.mean() <= 0:
        return pooled, [r.size for r in onsets_all]
    return pooled / spacings.mean(), [r.size for r in onsets_all]


# ── Per-PLL Fano helper ───────────────────────────────────────────────────────
def per_pll_fano_at_L1(lock_map, sr):
    out = []
    N = lock_map.shape[1]
    for p in range(lock_map.shape[0]):
        rec = extract_dwells(lock_map[p])
        if rec.n_events < 5:
            continue
        sp = np.diff(rec.lock_onsets)
        ms = float(sp.mean()) if sp.size > 0 else 0.0
        if ms <= 0:
            continue
        T_int = max(1, int(round(ms)))
        nW = N // T_int
        if nW < 5:
            continue
        idx = rec.lock_onsets[rec.lock_onsets < nW * T_int] // T_int
        counts = np.bincount(idx, minlength=nW).astype(np.float64)
        m = counts.mean()
        if m > 0:
            out.append(float(counts.var(ddof=1) / m))
    return np.array(out)


# ── Run all (cell × signal) combinations ──────────────────────────────────────
all_results = {}
print(f"{'cell':>10s}  {'signal':>6s}  {'n_events':>8s}  {'NNS_KS_poiss':>12s}  "
      f"{'NNS_KS_GOE':>10s}  {'NNS_KS_GUE':>10s}  best   F_pp_mean±std")
for cell in CELLS:
    for sig_name, sig in signals.items():
        t0 = time.perf_counter()
        lock_map, freqs, pairs = run_pll_bank(sig, cell['fc_ref'], cell['q_max'], cell['K_p'])
        events, evt_per_pll = aggregate_events_for_cell(lock_map, SR)
        nns = compute_nns(events)
        nv  = number_variance(events, L_max=20.0, n_L=30)
        sff = spectral_form_factor(events, t_max=3.0, n_t=120)
        pc  = pair_correlation(events, r_max=4.0, n_bins=24)
        fpp = per_pll_fano_at_L1(lock_map, SR)
        del lock_map
        cp.get_default_memory_pool().free_all_blocks()
        dt = time.perf_counter() - t0
        all_results[(cell['name'], sig_name)] = dict(
            cell=cell, sig_name=sig_name,
            events=events, n_events=int(events.size),
            n_locking=int(np.sum(np.array(evt_per_pll) > 0)),
            nns=nns, nv=nv, sff=sff, pc=pc, fpp=fpp,
        )
        fpp_str = f"{fpp.mean():.2f}±{fpp.std(ddof=1):.2f}" if fpp.size > 1 else "n/a"
        print(f"  {cell['name']:>8s}  {sig_name:>6s}  {events.size:8d}  "
              f"{nns.ks_poisson:12.4f}  {nns.ks_goe:10.4f}  {nns.ks_gue:10.4f}  "
              f"{nns.best_fit:>5s}  {fpp_str}    [{dt:.1f}s]")
print()


# ── Headline NNS comparison ───────────────────────────────────────────────────
print("=" * 78)
print("NNS — KS distances and p-values for each (cell, signal)")
print("=" * 78)
print(f"  {'cell':>10s}  {'signal':>6s}  "
      f"{'KS_P':>8s} {'p_P':>5s}  {'KS_GOE':>7s} {'p_GOE':>5s}  "
      f"{'KS_GUE':>7s} {'p_GUE':>5s}  best")
for (cell_name, sig_name), r in all_results.items():
    n = r['nns']
    print(f"  {cell_name:>10s}  {sig_name:>6s}  "
          f"{n.ks_poisson:8.4f} {n.p_poisson:5.3f}  "
          f"{n.ks_goe:7.4f} {n.p_goe:5.3f}  "
          f"{n.ks_gue:7.4f} {n.p_gue:5.3f}   {n.best_fit}")
print()


# ── NNS plots: histogram + analytical curves ──────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey=True, sharex=True)
s_grid = np.linspace(0.01, 4.0, 200)
for ri, cell in enumerate(CELLS):
    for ci, sig_name in enumerate(['zeta', 'gue', 'poiss']):
        ax = axes[ri, ci]
        r = all_results[(cell['name'], sig_name)]
        s = r['nns'].spacings
        if s.size > 5:
            ax.hist(s, bins=40, range=(0, 4), density=True, alpha=0.5, color='C0',
                    label=f"empirical (n={s.size})")
        ax.plot(s_grid, np.exp(-s_grid), 'C1--', label='Poisson', lw=1)
        from universality import nns_goe, nns_gue
        ax.plot(s_grid, nns_goe(s_grid), 'C2-', label='GOE', lw=1)
        ax.plot(s_grid, nns_gue(s_grid), 'C3-', label='GUE', lw=1)
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 1.2)
        if ri == 0 and ci == 0:
            ax.legend(fontsize=7, loc='upper right')
        if ci == 0:
            ax.set_ylabel(f"{cell['name']}\nP(s)")
        if ri == 1:
            ax.set_xlabel("normalised spacing  s")
        ax.set_title(f"{sig_name}  (best={r['nns'].best_fit}, KS_GUE={r['nns'].ks_gue:.3f})", fontsize=9)
        ax.grid(True, alpha=0.3)
fig.suptitle(f"NNS @ q_max=16, fc_ref=115.55  —  rows: K_p=0.20 / K_p=0.02")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOT_DIR, "03_nns.png"), dpi=110)
plt.close(fig)


# ── Σ²(L) comparison ──────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
for ax, cell in zip(axes, CELLS):
    for sig_name in ['zeta', 'gue', 'poiss']:
        r = all_results[(cell['name'], sig_name)]
        nv = r['nv']
        if nv['L'].size > 0:
            ax.plot(nv['L'], nv['sigma2'], lw=2, label=sig_name)
    if nv['L'].size > 0:
        ax.plot(nv['L'], nv['poisson'], 'k--', lw=0.8, label='Poisson (=L)')
        ax.plot(nv['L'], nv['goe'], 'k:', lw=0.8, label='GOE')
        ax.plot(nv['L'], nv['gue'], 'k-.', lw=0.8, label='GUE')
    ax.set_xlabel('L (× mean spacing)')
    ax.set_title(cell['name'])
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
axes[0].set_ylabel('Σ²(L)')
fig.suptitle("Number variance Σ²(L)")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "04_number_variance.png"), dpi=110)
plt.close(fig)


# ── K(t) spectral form factor ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
for ax, cell in zip(axes, CELLS):
    for sig_name in ['zeta', 'gue', 'poiss']:
        r = all_results[(cell['name'], sig_name)]
        s = r['sff']
        if s['t'].size > 0:
            ax.plot(s['t'], s['K'], lw=1.5, label=sig_name, alpha=0.8)
    # GUE ramp-plateau
    t = np.linspace(0.01, 3.0, 200)
    ax.plot(t, np.minimum(t, 1.0), 'k--', lw=0.8, label='GUE ramp-plateau')
    ax.axhline(1, color='k', ls=':', lw=0.5)
    ax.set_xlabel('t')
    ax.set_title(cell['name'])
    ax.set_xlim(0, 3)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
axes[0].set_ylabel('K(t)')
fig.suptitle("Spectral form factor K(t)")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "05_spectral_form_factor.png"), dpi=110)
plt.close(fig)

print(f"plots saved to {PLOT_DIR}/")
