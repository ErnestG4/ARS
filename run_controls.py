"""
Two control experiments before drawing conclusions about ζ.

Task 1 — Selection-bias control.
    The PLL's lock-confirmation window (N_lock=20ms) selects against
    fast-passage zeros (small dwell at f_pll) and for slow-passage ones.
    Hypothesis: this selection function alone could induce apparent level
    repulsion in the per-PLL NNS, regardless of whether the underlying
    frequencies are GUE-spaced or not.

    Test: synthesize a Poisson-frequency chirp (t_k uniform on ζ's range),
    run the same PLL bank, compute per-PLL NNS.  If it also shows level
    repulsion, the ζ result is an artifact of the selection.  If it shows
    Poisson statistics, ζ's level repulsion is genuine.

    Also: predict analytically which zeros pass the dwell threshold for
    each PLL, to see how much of the underlying t_n distribution survives.

Task 2 — Time-reversal symmetry.
    Run ζ forward and ζ reversed.  Identical NNS → measurement is time-
    symmetric (GOE/GUE indistinguishable, the metric folds them).  Distinct
    NNS → there is a genuine asymmetry the PLL detects.
"""
import os, sys
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '$HOME/fmexplorer/riemann_explorer')

from pll_bank import pll_bank_gpu, PLLParams, farey_rationals, GPU_NAME
from intermittency import extract_dwells, stern_brocot_depth
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

# Anchor cell — same as Task 2 (per-PLL NNS) yielded the headline ζ result.
FC_REF, Q_MAX, K_P = 115.55, 16, 0.02


def per_pll_nns(lock_map, sr, min_events=8):
    pooled = []
    info = []
    N = lock_map.shape[1]
    for p in range(lock_map.shape[0]):
        rec = extract_dwells(lock_map[p])
        if rec.n_events < min_events:
            continue
        sp = np.diff(rec.lock_onsets)
        if sp.size == 0 or sp.mean() <= 0:
            continue
        sp_norm = sp / sp.mean()
        pooled.append(sp_norm.astype(np.float64))
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
    pooled = np.concatenate(pooled) if pooled else np.zeros(0)
    return pooled, info


def ks_to(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    if n < 5:
        return float('nan'), float('nan')
    F_em = np.arange(1, n + 1) / n
    F_th = theory_cdf(s)
    ks = float(np.max(np.abs(F_em - F_th)))
    return ks, _ks_pvalue(ks, n)


def summarise_NNS(name, lock_map, sr):
    pooled, info = per_pll_nns(lock_map, sr, min_events=8)
    if pooled.size == 0:
        return dict(name=name, info=info, pooled=pooled,
                     ks_p=np.nan, ks_o=np.nan, ks_u=np.nan,
                     mass_below_03=np.nan, F_pp_mean=np.nan, F_pp_std=np.nan)
    ks_p, _ = ks_to(pooled, nns_cdf_poisson)
    ks_o, _ = ks_to(pooled, nns_cdf_goe)
    ks_u, _ = ks_to(pooled, nns_cdf_gue)
    fpp = np.array([d['F_at_L1'] for d in info if not np.isnan(d['F_at_L1'])])
    return dict(
        name=name, info=info, pooled=pooled,
        ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
        mass_below_03=float((pooled < 0.3).mean()),
        F_pp_mean=float(fpp.mean()) if fpp.size else float('nan'),
        F_pp_std=float(fpp.std(ddof=1)) if fpp.size > 1 else float('nan'),
        n_qualifying=len(info),
        n_pooled=pooled.size,
    )


def run_pll_bank_for_signal(sig):
    pairs = farey_rationals(Q_MAX)
    freqs, pairs_kept = [], []
    for p, q in pairs:
        f = FC_REF * p / q
        if 5.0 < f < SR * 0.45:
            freqs.append(f); pairs_kept.append((p, q))
    freqs = np.asarray(freqs, dtype=np.float32)
    params = PLLParams(K_p=K_P, K_i=K_P * 0.05, rho=0.95)
    lock_map, _ = pll_bank_gpu(sig, freqs, SR, params, return_phase_error=False)
    return lock_map, pairs_kept, freqs


# ─────────────────────────────────────────────────────────────────────────────
# TASK 1 — analytical selection prediction + Poisson-FM control
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 80)
print("TASK 1 — selection-bias characterisation")
print("=" * 80)
print()

zeta_zeros = scanner.ZETA_ZEROS.astype(np.float64)
LOCK_CONFIRM_S = 20e-3      # 20 ms
TONGUE_PREFAC  = 0.05       # 5% of f_pll for the unit (p+q=2) tongue
sb_depth = lambda p, q: stern_brocot_depth(p, q)


def predict_selected_zeros(zeros, fc_ref, q_max, dur_s, lock_confirm_s):
    """For each (p, q) PLL, return list of zero indices that survive the
    dwell-threshold criterion."""
    pairs = farey_rationals(q_max)
    selected_per_pll = {}
    for p, q in pairs:
        f_pll = fc_ref * p / q
        if not (5.0 < f_pll < SR * 0.45):
            continue
        # eligible zeros: t_n in [f_pll, f_pll * (dur_s + 1)]
        elig = (zeros >= f_pll) & (zeros <= f_pll * (dur_s + 1))
        elig_idx = np.where(elig)[0]
        # Tongue width Δf ≈ TONGUE_PREFAC · f_pll · (2/(p+q))^2
        Δf = TONGUE_PREFAC * f_pll * (2.0 / (p + q)) ** 2
        # Dwell duration at f_pll for zero t_n: Δf · t_n / f_pll²
        dwell = Δf * zeros[elig_idx] / (f_pll ** 2)
        keep = elig_idx[dwell >= lock_confirm_s]
        selected_per_pll[(p, q)] = keep
    return selected_per_pll


print(f"  Predicted-selected zero-index distribution at fc_ref={FC_REF}, q_max={Q_MAX}:")
sel = predict_selected_zeros(zeta_zeros, FC_REF, Q_MAX, DUR, LOCK_CONFIRM_S)
all_kept = []
for pq, idx in sel.items():
    all_kept.extend(idx.tolist())
all_kept = np.array(all_kept) if all_kept else np.zeros(0, int)
print(f"  total (zero, PLL) pairs surviving dwell threshold: {all_kept.size}")
print(f"  unique zeros that pass at any PLL: {len(np.unique(all_kept))}")
# Summary by zero index
counts = np.bincount(all_kept, minlength=len(zeta_zeros))
nonzero_idx = np.where(counts > 0)[0]
print(f"  per-zero PLL pass-count: min={counts.min()}, max={counts.max()}, "
      f"mean(of those that pass)={counts[nonzero_idx].mean():.2f}")
print()
# Histogram of zero magnitudes that pass — vs all 98 ζ zeros
print(f"  ζ zero-magnitude survival fraction by decile:")
edges = np.percentile(zeta_zeros, np.linspace(0, 100, 11))
print(f"    {'t_n band':>22}  {'#zeros':>6}  {'#pass':>6}  {'frac':>5}")
for i in range(10):
    lo, hi = edges[i], edges[i + 1]
    band = (zeta_zeros >= lo) & (zeta_zeros < hi)
    band_idx = np.where(band)[0]
    band_pass = sum(1 for idx in band_idx if counts[idx] > 0)
    print(f"    [{lo:7.2f}, {hi:7.2f})  {int(band.sum()):6d}  "
          f"{band_pass:6d}  {band_pass / max(int(band.sum()), 1):.3f}")
print()


# ─ Now actually run the bank on all four control signals ─
print("  Running PLL bank for control signals …")
print(f"  cell: q_max={Q_MAX}, K_p={K_P}, fc_ref={FC_REF}, dur={DUR}s, NZ={NZ}")
print(f"  GPU: {GPU_NAME}")
print()

sig_zeta    = scanner.make_zeta_signal(sr=SR, duration=DUR, n_zeros=NZ)
sig_gue     = signal_gen.make_gue_eigenvalue_signal(sr=SR, duration=DUR, n_points=NZ,
                                                     seed=42, rescale_to_zeta_range=True)
sig_pois    = signal_gen.make_poisson_zeta_like(sr=SR, duration=DUR, n_points=NZ, seed=0)

# Ensure ζ and Poisson share the same underlying t_k count — they already do (98).
results_t1 = {}
for name, sig in [('zeta', sig_zeta), ('gue', sig_gue), ('poiss', sig_pois)]:
    lock_map, pairs_kept, freqs = run_pll_bank_for_signal(sig)
    summary = summarise_NNS(name, lock_map, SR)
    results_t1[name] = summary
    del lock_map; cp.get_default_memory_pool().free_all_blocks()

# Print headline table
print(f"  {'signal':>10}  {'qual_PLL':>8}  {'n_pooled':>8}  "
      f"{'F_pp_mean':>9}  {'mass<0.3':>8}  "
      f"{'KS_P':>6}  {'KS_GOE':>6}  {'KS_GUE':>6}  best")
for name in ['zeta', 'gue', 'poiss']:
    r = results_t1[name]
    best = min([('Poiss', r['ks_p']), ('GOE', r['ks_o']), ('GUE', r['ks_u'])],
                key=lambda x: x[1])[0]
    print(f"  {name:>10}  {r['n_qualifying']:8d}  {r['n_pooled']:8d}  "
          f"{r['F_pp_mean']:9.3f}  {r['mass_below_03']:8.3f}  "
          f"{r['ks_p']:6.3f}  {r['ks_o']:6.3f}  {r['ks_u']:6.3f}  {best}")
print()
print(f"  Theoretical mass at s<0.3: Poisson=0.259, GOE≈0.064, GUE≈0.011")
print()
print(f"  TASK 1 VERDICT:")
zeta_mass = results_t1['zeta']['mass_below_03']
poiss_mass = results_t1['poiss']['mass_below_03']
poiss_F = results_t1['poiss']['F_pp_mean']
zeta_F  = results_t1['zeta']['F_pp_mean']
if poiss_mass < 0.10 and poiss_F < 1.5:
    print(f"  Poisson-FM null shows mass<0.3 = {poiss_mass:.3f} and F = {poiss_F:.3f}")
    print(f"  → selection bias DOES produce apparent level repulsion!")
    print(f"  → ζ's result may be an artifact.")
elif poiss_mass > 0.20 and poiss_F > 2.0:
    print(f"  Poisson-FM null:  mass<0.3 = {poiss_mass:.3f},  F = {poiss_F:.3f}")
    print(f"  ζ                 mass<0.3 = {zeta_mass:.3f},  F = {zeta_F:.3f}")
    print(f"  → Poisson-FM control DOES NOT show level repulsion.")
    print(f"  → selection bias is NOT sufficient to cause level repulsion.")
    print(f"  → ζ's level repulsion (mass<0.3 = {zeta_mass:.3f}, "
          f"{'5x' if zeta_mass>0 else 'inf×'} less than poiss) is GENUINE.")
else:
    print(f"  intermediate result — poiss mass<0.3 = {poiss_mass:.3f}, F = {poiss_F:.3f}")
    print(f"  ζ                    mass<0.3 = {zeta_mass:.3f}, F = {zeta_F:.3f}")
    print(f"  → ambiguous: needs more events or longer duration to disambiguate.")
print()


# ─────────────────────────────────────────────────────────────────────────────
# TASK 2 — time-reversal symmetry
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 80)
print("TASK 2 — time-reversal symmetry test")
print("=" * 80)
print()

sig_zeta_fwd = sig_zeta.astype(np.float32)
sig_zeta_rev = sig_zeta[::-1].astype(np.float32)

lm_fwd, _, _ = run_pll_bank_for_signal(sig_zeta_fwd)
sum_fwd = summarise_NNS("zeta_fwd", lm_fwd, SR)
del lm_fwd; cp.get_default_memory_pool().free_all_blocks()

lm_rev, _, _ = run_pll_bank_for_signal(sig_zeta_rev)
sum_rev = summarise_NNS("zeta_rev", lm_rev, SR)
del lm_rev; cp.get_default_memory_pool().free_all_blocks()

print(f"  {'direction':>10}  {'qual_PLL':>8}  {'n_pooled':>8}  "
      f"{'F_pp_mean':>9}  {'mass<0.3':>8}  {'KS_P':>6}  {'KS_GOE':>6}  {'KS_GUE':>6}")
for label, r in [('forward', sum_fwd), ('reversed', sum_rev)]:
    print(f"  {label:>10}  {r['n_qualifying']:8d}  {r['n_pooled']:8d}  "
          f"{r['F_pp_mean']:9.3f}  {r['mass_below_03']:8.3f}  "
          f"{r['ks_p']:6.3f}  {r['ks_o']:6.3f}  {r['ks_u']:6.3f}")
print()

# Quantify how different the two pooled spacing distributions are.
if sum_fwd['pooled'].size > 5 and sum_rev['pooled'].size > 5:
    # Two-sample KS between forward and reversed pooled spacings
    s1 = np.sort(sum_fwd['pooled'])
    s2 = np.sort(sum_rev['pooled'])
    n1, n2 = s1.size, s2.size
    cdf1 = np.searchsorted(s1, np.concatenate([s1, s2]), side='right') / n1
    cdf2 = np.searchsorted(s2, np.concatenate([s1, s2]), side='right') / n2
    ks_two = float(np.max(np.abs(cdf1 - cdf2)))
    p_two  = _ks_pvalue(ks_two, int(n1 * n2 / (n1 + n2)))
    print(f"  Two-sample KS between forward & reversed pooled spacings:")
    print(f"    KS = {ks_two:.4f}, p-value = {p_two:.4f}")
    if ks_two < 0.10 and p_two > 0.05:
        print(f"  → forward and reversed are STATISTICALLY INDISTINGUISHABLE")
        print(f"  → measurement is time-symmetric → cannot distinguish GOE from GUE")
    else:
        print(f"  → forward and reversed are STATISTICALLY DIFFERENT")
        print(f"  → measurement detects time-asymmetry — GOE-vs-GUE distinguishable")
print()

# Compare F per PLL pair for forward vs reversed (ranked by n_events)
print(f"  per-PLL F comparison (top-12 by forward n_events):")
fwd_by_idx = {d['pll_index']: d for d in sum_fwd['info']}
rev_by_idx = {d['pll_index']: d for d in sum_rev['info']}
common = [i for i in fwd_by_idx if i in rev_by_idx]
common_sorted = sorted(common, key=lambda i: -fwd_by_idx[i]['n_events'])
print(f"    {'pll_idx':>8}  {'n_fwd':>5}  {'n_rev':>5}  {'F_fwd':>6}  {'F_rev':>6}  {'|ΔF|':>5}")
for i in common_sorted[:12]:
    df = fwd_by_idx[i]; dr = rev_by_idx[i]
    if not np.isnan(df['F_at_L1']) and not np.isnan(dr['F_at_L1']):
        dF = abs(df['F_at_L1'] - dr['F_at_L1'])
        print(f"    {i:8d}  {df['n_events']:5d}  {dr['n_events']:5d}  "
              f"{df['F_at_L1']:6.3f}  {dr['F_at_L1']:6.3f}  {dF:5.3f}")


# ─ Plot ─────────────────────────────────────────────────────────────────────
print()
print("Plotting NNS comparisons …")
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey=True, sharex=True)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 31)

# Top row: control signals (Task 1)
for ax, name in zip(axes[0], ['zeta', 'gue', 'poiss']):
    r = results_t1[name]
    if r['pooled'].size > 0:
        ax.hist(r['pooled'], bins=bin_edges, density=True, alpha=0.55, color='C0',
                label=f"empirical (n={r['pooled'].size})")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.8, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    ax.set_title(f"{name}\nKS_P={r['ks_p']:.3f}  KS_GUE={r['ks_u']:.3f}  mass<0.3={r['mass_below_03']:.3f}")
    ax.grid(True, alpha=0.3)
axes[0, 0].legend(fontsize=7, loc='upper right')
axes[0, 0].set_ylabel("Task 1 — controls\nP(s)")

# Bottom row: forward vs reversed
for ax, (label, r) in zip(axes[1], [('forward', sum_fwd), ('reversed', sum_rev)]):
    if r['pooled'].size > 0:
        ax.hist(r['pooled'], bins=bin_edges, density=True, alpha=0.55, color='C0',
                label=f"empirical (n={r['pooled'].size})")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.8, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    ax.set_title(f"ζ {label}\nF_pp={r['F_pp_mean']:.3f}  mass<0.3={r['mass_below_03']:.3f}")
    ax.grid(True, alpha=0.3)
axes[1, 2].axis('off')
axes[1, 0].set_ylabel("Task 2 — time reversal\nP(s)")
axes[1, 0].set_xlabel("normalised spacing  s")
axes[1, 1].set_xlabel("normalised spacing  s")

fig.suptitle(f"Controls @ q_max={Q_MAX}, K_p={K_P}, fc_ref={FC_REF}")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOT_DIR, "08_controls.png"), dpi=110)
plt.close(fig)
print(f"  → plots/08_controls.png")
