"""
Analytical passage-time NNS — bypass the chirp synthesis and PLL detector
entirely, compute the spacings of zero-passages through each PLL frequency
directly from the eigenvalue list.

For each PLL p:q at f_pll = fc_ref · p/q:
    1.  Eligible zeros: t_n in [f_pll, f_pll · (T+1)]   — pass through during recording
    2.  Dwell threshold: t_n ≥ N_lock · sr / (tongue_prefac × (2/(p+q))²)  for that PLL
    3.  Passage times t* = t_n/f_pll − 1
    4.  Spacings = diff(t*) — i.e., (t_{n+1}−t_n)/f_pll
    5.  Normalise per-PLL by mean spacing
    6.  Pool across PLLs

Compare this analytical NNS to the measured PLL-output NNS for ζ.  The
delta isolates what the chirp/PLL stack adds beyond the eigenvalue
selection function.

Inputs (from previous runs):
    ζ            — zeros_1000.npy
    GUE chirp t_k — recompute (semicircle-unfolded eigenvalues mapped
                    through ζ-empirical-CDF, same as in run_calibration.py)
    GOE chirp t_k — same
"""
import os, sys
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
N_EIG     = 1000
FC_REF    = 115.55
Q_MAX     = 8
PLOT_DIR  = os.path.join(THIS_DIR, "plots")
ZEROS_PATH = os.path.join(THIS_DIR, "zeros_1000.npy")

# PLL detection parameters (must match the actual run)
LOCK_CONFIRM_S = 20e-3
TONGUE_PREFAC  = 0.05

# Stripping the first 500 ms — same as the measurement
TRANSIENT_S = 0.500


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


def to_zeta_density(unfolded_uniform_in_0_N, zeta_sorted):
    N = len(zeta_sorted)
    return np.interp(unfolded_uniform_in_0_N,
                      np.linspace(0.5, N - 0.5, N),
                      np.asarray(zeta_sorted, dtype=np.float64))


def analytical_nns(t_n_array, fc_ref, q_max, dur_s, transient_s,
                    lock_confirm_s, tongue_prefac, min_events=10):
    """Per-PLL analytical passage-time NNS, normalised per-PLL and pooled."""
    pairs = farey_rationals(q_max)
    pooled = []
    info = []
    for p, q in pairs:
        f_pll = fc_ref * p / q
        if not (5.0 < f_pll < SR * 0.45): continue

        # Time-band: passage time t* = t_n/f_pll - 1 in [transient_s, dur_s]
        # ⇒ t_n in [(transient_s + 1)·f_pll, (dur_s + 1)·f_pll]
        elig = ((t_n_array >= (transient_s + 1.0) * f_pll) &
                (t_n_array <= (dur_s + 1.0) * f_pll))
        elig_t = np.sort(t_n_array[elig])

        # Tongue width: Δf = tongue_prefac · f_pll · (2/(p+q))²
        # Dwell duration: Δf · t_n / f_pll²  =  tongue_prefac · t_n · (2/(p+q))² / f_pll
        # Need dwell ≥ lock_confirm_s ⇒ t_n ≥ lock_confirm_s · f_pll / (tongue_prefac · (2/(p+q))²)
        threshold = lock_confirm_s * f_pll / (tongue_prefac * (2.0 / (p + q)) ** 2)
        qualifying = elig_t[elig_t >= threshold]
        if qualifying.size < min_events + 1:   # +1 because spacings = events − 1
            continue
        spacings = np.diff(qualifying) / f_pll
        if spacings.size == 0 or spacings.mean() <= 0:
            continue
        sp_norm = spacings / spacings.mean()
        pooled.append(sp_norm)
        info.append(dict(p=p, q=q, f_pll=f_pll, n_passages=int(qualifying.size)))
    pooled = np.concatenate(pooled) if pooled else np.zeros(0)
    return pooled, info


def ks_to(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    if n < 5: return float('nan'), float('nan')
    F_em = np.arange(1, n + 1) / n
    F_th = theory_cdf(s)
    ks = float(np.max(np.abs(F_em - F_th)))
    return ks, _ks_pvalue(ks, n)


# ── Build eigenvalue lists ────────────────────────────────────────────────────
print("Building eigenvalue lists …")
zeta = np.load(ZEROS_PATH)[:N_EIG].astype(np.float64)
zeta_sorted = np.sort(zeta)

gue_eigs   = gen_gue(N_EIG, seed=42)
goe_eigs   = gen_goe(N_EIG, seed=42)
gue_unf    = semicircle_cdf_unit(gue_eigs / 2.0) * N_EIG
goe_unf    = semicircle_cdf_unit(goe_eigs / 2.0) * N_EIG
# Two parameterisations of GUE/GOE chirp t_k to compare:
#   (i)   raw unfolded — uniform density on [0, N_EIG]
#   (ii)  ζ-density-mapped — same density profile as ζ
gue_t_uniform = gue_unf
goe_t_uniform = goe_unf
gue_t_zd = to_zeta_density(gue_unf, zeta_sorted)
goe_t_zd = to_zeta_density(goe_unf, zeta_sorted)

# Sanity: KS of plain unfolded eigenvalue spacings
def quick_ks(arr, theory_cdf):
    sp = np.diff(np.sort(arr)); sp /= sp.mean()
    return ks_to(sp, theory_cdf)[0]
print(f"  GUE unfolded eigenvalue NNS:  KS_GUE={quick_ks(gue_unf, nns_cdf_gue):.4f}  "
      f"KS_GOE={quick_ks(gue_unf, nns_cdf_goe):.4f}  KS_Poiss={quick_ks(gue_unf, nns_cdf_poisson):.4f}")
print(f"  GOE unfolded eigenvalue NNS:  KS_GUE={quick_ks(goe_unf, nns_cdf_gue):.4f}  "
      f"KS_GOE={quick_ks(goe_unf, nns_cdf_goe):.4f}  KS_Poiss={quick_ks(goe_unf, nns_cdf_poisson):.4f}")
print(f"  ζ raw NNS (1000 zeros):        KS_GUE={quick_ks(zeta, nns_cdf_gue):.4f}  "
      f"KS_GOE={quick_ks(zeta, nns_cdf_goe):.4f}  KS_Poiss={quick_ks(zeta, nns_cdf_poisson):.4f}")
print(f"      (note: ζ raw spacings include local density variation; not unfolded.)")
print()


# ── Compute analytical passage-time NNS for each ──────────────────────────────
print("=" * 90)
print(f"Analytical passage-time NNS @ fc_ref={FC_REF}, q_max={Q_MAX}, "
      f"dur={DUR}s, lock_confirm={LOCK_CONFIRM_S*1000:.0f}ms, transient={TRANSIENT_S*1000:.0f}ms")
print("=" * 90)
print(f"  {'signal':<24}  {'#PLL_qual':>9}  {'#pooled':>7}  {'KS_P':>5}  "
      f"{'KS_O':>5}  {'KS_U':>5}  {'KO−KU':>6}  best")
sigs = [
    ('ζ',                       zeta),
    ('GUE (unfolded uniform)',  gue_t_uniform),
    ('GOE (unfolded uniform)',  goe_t_uniform),
    ('GUE (ζ-density mapped)',  gue_t_zd),
    ('GOE (ζ-density mapped)',  goe_t_zd),
]
analytical_results = {}
for name, arr in sigs:
    pooled, info = analytical_nns(arr, FC_REF, Q_MAX, DUR, TRANSIENT_S,
                                    LOCK_CONFIRM_S, TONGUE_PREFAC)
    if pooled.size < 5:
        print(f"  {name:<24}  insufficient data")
        analytical_results[name] = None
        continue
    ks_p, p_p = ks_to(pooled, nns_cdf_poisson)
    ks_o, p_o = ks_to(pooled, nns_cdf_goe)
    ks_u, p_u = ks_to(pooled, nns_cdf_gue)
    delta = ks_o - ks_u
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    print(f"  {name:<24}  {len(info):9d}  {pooled.size:7d}  "
          f"{ks_p:5.3f}  {ks_o:5.3f}  {ks_u:5.3f}  {delta:+6.3f}  {best}")
    analytical_results[name] = dict(pooled=pooled, info=info,
                                      ks_p=ks_p, ks_o=ks_o, ks_u=ks_u, best=best)
print()


# ── Compare ζ analytical to ζ measured ────────────────────────────────────────
# Re-run the ζ measured NNS at the same cell using the cached chirp signal
# (same protocol as run_decisive.py).
print("=" * 90)
print("ζ — analytical-vs-measured comparison")
print("=" * 90)

import sys
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))

from pll_bank import pll_bank_gpu, PLLParams
from intermittency import extract_dwells
import cupy as cp

SIG_DIR = os.path.join(THIS_DIR, "signals_cache")
sig_zeta = np.load(os.path.join(SIG_DIR, "zeta_N1000_dur300.npy"))

pairs = farey_rationals(Q_MAX)
freqs, pairs_kept = [], []
for p, q in pairs:
    f = FC_REF * p / q
    if 5.0 < f < SR * 0.45:
        freqs.append(f); pairs_kept.append((p, q))
freqs = np.asarray(freqs, dtype=np.float32)
params = PLLParams(K_p=0.02, K_i=0.001, rho=0.95)
print(f"  Running PLL bank on cached ζ signal ({len(freqs)} PLLs) …")
import time
t0 = time.perf_counter()
lock_map, _ = pll_bank_gpu(sig_zeta, freqs, SR, params, return_phase_error=False)
print(f"  PLL bank: {time.perf_counter()-t0:.1f}s")

TRANSIENT_SAMPLES = int(round(SR * TRANSIENT_S))
def measured_nns(lock_map, sr, transient_n, min_events=10):
    pooled = []
    info = []
    N = lock_map.shape[1]
    for p in range(lock_map.shape[0]):
        s = lock_map[p, transient_n:]
        rec = extract_dwells(s)
        if rec.n_events < min_events: continue
        sp = np.diff(rec.lock_onsets)
        if sp.size == 0 or sp.mean() <= 0: continue
        sp_norm = sp / sp.mean()
        pooled.append(sp_norm)
        info.append(dict(pll_index=p, n_events=rec.n_events))
    pooled = np.concatenate(pooled) if pooled else np.zeros(0)
    return pooled, info

zeta_meas_pooled, zeta_meas_info = measured_nns(lock_map, SR, TRANSIENT_SAMPLES)
del lock_map; cp.get_default_memory_pool().free_all_blocks()

if zeta_meas_pooled.size > 5:
    ks_p, _ = ks_to(zeta_meas_pooled, nns_cdf_poisson)
    ks_o, _ = ks_to(zeta_meas_pooled, nns_cdf_goe)
    ks_u, _ = ks_to(zeta_meas_pooled, nns_cdf_gue)
    print(f"  ζ measured (PLL-detected): #PLLs={len(zeta_meas_info)}, n={zeta_meas_pooled.size}")
    print(f"    KS_P={ks_p:.3f}  KS_O={ks_o:.3f}  KS_U={ks_u:.3f}  KO−KU={ks_o-ks_u:+.3f}  "
          f"best={['Poiss','GOE','GUE'][np.argmin([ks_p, ks_o, ks_u])]}")

if 'ζ' in analytical_results and analytical_results['ζ'] is not None:
    a = analytical_results['ζ']
    print(f"  ζ analytical (passage times): #PLLs={len(a['info'])}, n={a['pooled'].size}")
    print(f"    KS_P={a['ks_p']:.3f}  KS_O={a['ks_o']:.3f}  KS_U={a['ks_u']:.3f}  "
          f"KO−KU={a['ks_o']-a['ks_u']:+.3f}  best={a['best']}")

    # Two-sample KS between analytical and measured ζ NNS
    s1 = np.sort(a['pooled']); s2 = np.sort(zeta_meas_pooled)
    n1, n2 = s1.size, s2.size
    pts = np.concatenate([s1, s2])
    cdf1 = np.searchsorted(s1, pts, side='right') / n1
    cdf2 = np.searchsorted(s2, pts, side='right') / n2
    ks_two = float(np.max(np.abs(cdf1 - cdf2)))
    p_two  = _ks_pvalue(ks_two, int(n1 * n2 / (n1 + n2)))
    print()
    print(f"  Two-sample KS (analytical vs measured ζ): KS={ks_two:.4f}, p={p_two:.4f}")
    if ks_two < 0.05:
        print(f"  → analytical and measured ζ NNS are STATISTICALLY THE SAME")
        print(f"    The PLL adds NEGLIGIBLE distortion; the metric is faithful.")
    elif ks_two < 0.10:
        print(f"  → small but real PLL contribution — instrument's signature is mild")
    else:
        print(f"  → analytical and measured DIFFER significantly — PLL adds substantial structure")
print()


# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey=True, sharex=True)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)

panels = [
    ('ζ analytical',          analytical_results.get('ζ'),                   axes[0, 0]),
    ('GUE analytical (uniform)', analytical_results.get('GUE (unfolded uniform)'), axes[0, 1]),
    ('GOE analytical (uniform)', analytical_results.get('GOE (unfolded uniform)'), axes[0, 2]),
    ('ζ measured (PLL)',      None,                                          axes[1, 0]),
    ('GUE analytical (ζ-density)', analytical_results.get('GUE (ζ-density mapped)'), axes[1, 1]),
    ('GOE analytical (ζ-density)', analytical_results.get('GOE (ζ-density mapped)'), axes[1, 2]),
]

# Stuff in measured ζ for the (1,0) panel
if zeta_meas_pooled.size > 5:
    panels[3] = ('ζ measured (PLL)', dict(pooled=zeta_meas_pooled,
                                            ks_p=ks_to(zeta_meas_pooled, nns_cdf_poisson)[0],
                                            ks_o=ks_to(zeta_meas_pooled, nns_cdf_goe)[0],
                                            ks_u=ks_to(zeta_meas_pooled, nns_cdf_gue)[0],
                                            best=['Poiss','GOE','GUE'][int(np.argmin([
                                                ks_to(zeta_meas_pooled, nns_cdf_poisson)[0],
                                                ks_to(zeta_meas_pooled, nns_cdf_goe)[0],
                                                ks_to(zeta_meas_pooled, nns_cdf_gue)[0]]))]),
                  axes[1, 0])

for title, r, ax in panels:
    if r is None:
        ax.set_title(f"{title}: no data"); continue
    pooled = r['pooled']
    if pooled.size == 0:
        ax.set_title(f"{title}: no data"); continue
    ax.hist(pooled, bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f'n={pooled.size}')
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.8, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    ax.set_title(f"{title}\nbest={r['best']}  KS_O={r['ks_o']:.3f}  "
                  f"KS_U={r['ks_u']:.3f}  Δ={r['ks_o']-r['ks_u']:+.3f}", fontsize=8)
    ax.grid(True, alpha=0.3)
axes[0, 0].legend(fontsize=7, loc='upper right')
axes[0, 0].set_ylabel('analytical')
axes[1, 0].set_ylabel('measured / ζ-density')
for ax in axes[-1]: ax.set_xlabel('normalised spacing s')
fig.suptitle(f"Analytical passage-time NNS vs measured ζ — q_max={Q_MAX}, fc_ref={FC_REF}, "
              f"transient={int(TRANSIENT_S*1000)}ms")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOT_DIR, "14_analytical_vs_measured.png"), dpi=110)
plt.close(fig)
print(f"  → plots/14_analytical_vs_measured.png")
