"""
Calibration controls — does the instrument distinguish GOE from GUE?

Three signals, each 300 s × 1000-eigenvalue chirp at fc_ref=115.55, q_max=8,
K_p=0.02, with the first 500 ms of each PLL stripped to remove IIR settling:

    A.  ζ            — first 1000 Riemann zero heights (loaded from cache)
    B.  GUE chirp    — eigenvalues of N=1000 Hermitian random matrix,
                        semicircle-unfolded at R=2
    C.  GOE chirp    — eigenvalues of N=1000 real-symmetric random matrix,
                        semicircle-unfolded at R=2

Each is run forward and reversed; we report the standard table (qualifying
PLLs, pooled spacings, F per PLL, mass<0.3, KS to Poisson/GOE/GUE,
KS_GOE − KS_GUE) plus the fwd-vs-rev two-sample KS and matched per-PLL F
comparisons.

Verdict matrix:
    GUE→GUE  GOE→GOE  →  instrument has GUE/GOE resolution; ζ→GOE means
                          ζ genuinely deviates from GUE (interesting result).
    GUE→GOE  GOE→GOE  →  instrument folds GUE onto GOE (GOE-projection
                          confirmed); ζ→GOE is consistent with GUE conjecture.
    GUE→Poisson GOE→Poisson → still broken.
"""
import os, sys, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))

from pll_bank import pll_bank_gpu, PLLParams, farey_rationals, GPU_NAME
from intermittency import extract_dwells
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    _ks_pvalue,
)
import cupy as cp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


SR        = 44100.0
DUR       = 300.0
N_EIG     = 1000
FC_REF    = 115.55
Q_MAX     = 8
K_P       = 0.02
TRANSIENT_MS = 500.0
TRANSIENT_SAMPLES = int(round(SR * TRANSIENT_MS * 0.001))

ZEROS_PATH = os.path.join(THIS_DIR, "zeros_1000.npy")
PLOT_DIR   = os.path.join(THIS_DIR, "plots")
SIG_DIR    = os.path.join(THIS_DIR, "signals_cache")
os.makedirs(SIG_DIR, exist_ok=True)


# ── Random matrix eigenvalue generators (semicircle-unfolded, R=2) ────────────
def semicircle_cdf_unit(x):
    x = np.clip(x, -1.0, 1.0)
    return 0.5 + (x * np.sqrt(1.0 - x * x) + np.arcsin(x)) / np.pi


def gue_eigenvalues(N, seed):
    rng = np.random.default_rng(seed)
    A = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * N)
    return np.sort(np.linalg.eigvalsh(H).real)


def goe_eigenvalues(N, seed):
    """Real-symmetric Gaussian: A_ij ~ N(0,1), H = (A+A^T)/√(2N).
    Bulk semicircle on [-2, 2], same as GUE (just real-valued)."""
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((N, N))
    H = (A + A.T) / np.sqrt(2 * N)
    return np.sort(np.linalg.eigvalsh(H))


def unfold_R2(eigs):
    return semicircle_cdf_unit(eigs / 2.0) * len(eigs)


def ks_between(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    if n < 5: return float('nan')
    F_em = np.arange(1, n + 1) / n
    F_th = theory_cdf(s)
    return float(np.max(np.abs(F_em - F_th)))


# ── Build / verify eigenvalue sets ────────────────────────────────────────────
print(f"=" * 80)
print(f"Eigenvalue sets — N={N_EIG}, semicircle CDF unfolded at R=2")
print(f"=" * 80)

# ζ zero heights — load from cache.
zeta = np.load(ZEROS_PATH)[:N_EIG].astype(np.float64)

# GUE
gue_raw = gue_eigenvalues(N_EIG, seed=42)
gue_unfolded = unfold_R2(gue_raw)
sp_g = np.diff(gue_unfolded); sp_g /= sp_g.mean()
ks_gue_to_gue = ks_between(sp_g, nns_cdf_gue)
ks_gue_to_goe = ks_between(sp_g, nns_cdf_goe)
ks_gue_to_poi = ks_between(sp_g, nns_cdf_poisson)

# GOE
goe_raw = goe_eigenvalues(N_EIG, seed=42)
goe_unfolded = unfold_R2(goe_raw)
sp_o = np.diff(goe_unfolded); sp_o /= sp_o.mean()
ks_goe_to_goe = ks_between(sp_o, nns_cdf_goe)
ks_goe_to_gue = ks_between(sp_o, nns_cdf_gue)
ks_goe_to_poi = ks_between(sp_o, nns_cdf_poisson)

print(f"  GUE matrix eigenvalues: span [{gue_raw.min():.3f}, {gue_raw.max():.3f}]")
print(f"    KS to Wigner GUE = {ks_gue_to_gue:.4f}   (target < 0.05)")
print(f"    KS to Wigner GOE = {ks_gue_to_goe:.4f}   (control)")
print(f"    KS to Poisson    = {ks_gue_to_poi:.4f}")
print(f"  GOE matrix eigenvalues: span [{goe_raw.min():.3f}, {goe_raw.max():.3f}]")
print(f"    KS to Wigner GOE = {ks_goe_to_goe:.4f}   (target < 0.05)")
print(f"    KS to Wigner GUE = {ks_goe_to_gue:.4f}   (control)")
print(f"    KS to Poisson    = {ks_goe_to_poi:.4f}")
print()
assert ks_gue_to_gue < 0.06, f"GUE generator broken: KS={ks_gue_to_gue}"
assert ks_goe_to_goe < 0.06, f"GOE generator broken: KS={ks_goe_to_goe}"

# Map GUE/GOE eigenvalues through the inverse empirical CDF of ζ zeros so they
# inherit ζ's INCREASING density profile (sparse at low t, dense at high t)
# while keeping their local Wigner spacing structure.  Without this step,
# uniform-density chirps run the PLL into continuous-lock saturation and the
# detector can't see the level statistics at all.
def to_zeta_density(unfolded_uniform_in_0_N, zeta_sorted):
    """Map values uniform on [0, N] to ζ-density-distributed values via
    F_ζ^(-1)."""
    N = len(zeta_sorted)
    return np.interp(unfolded_uniform_in_0_N,
                      np.linspace(0.5, N - 0.5, N),
                      np.asarray(zeta_sorted, dtype=np.float64))

zeta_sorted = np.sort(zeta)
gue_t_k = to_zeta_density(gue_unfolded, zeta_sorted)
goe_t_k = to_zeta_density(goe_unfolded, zeta_sorted)
print(f"  ζ-density-matched mapping (range matches ζ exactly):")
print(f"    GUE t_k: [{gue_t_k.min():.3f}, {gue_t_k.max():.3f}]")
print(f"    GOE t_k: [{goe_t_k.min():.3f}, {goe_t_k.max():.3f}]")
# After non-linear remapping, normalised spacings need to be evaluated locally
# (per-PLL).  Globally they will follow the ζ density, not Wigner directly.
# The local NNS structure is preserved for spacings small compared to the
# variation of the density gradient — which holds within a single PLL's band.
sp_g_re = np.diff(gue_t_k); sp_g_re /= sp_g_re.mean()
sp_o_re = np.diff(goe_t_k); sp_o_re /= sp_o_re.mean()
print(f"  global spacing KS (NOT directly comparable post-remap, but for ref):")
print(f"    GUE: KS_to_GUE={ks_between(sp_g_re, nns_cdf_gue):.4f}, "
      f"KS_to_Poiss={ks_between(sp_g_re, nns_cdf_poisson):.4f}")
print(f"    GOE: KS_to_GOE={ks_between(sp_o_re, nns_cdf_goe):.4f}, "
      f"KS_to_Poiss={ks_between(sp_o_re, nns_cdf_poisson):.4f}")
print()


# ── Synthesise chirps ─────────────────────────────────────────────────────────
def make_chirp_cached(t_k, name):
    cache = os.path.join(SIG_DIR, f"{name}_N{N_EIG}_dur{int(DUR)}.npy")
    if os.path.exists(cache):
        sig = np.load(cache)
        print(f"  {name}: loaded cached signal ({len(sig)} samples)")
        return sig
    print(f"  {name}: synthesising {DUR}s × {len(t_k)} tones …")
    t0 = time.perf_counter()
    N = int(SR * DUR)
    t = np.arange(1, N + 1, dtype=np.float64) / SR
    log_t = np.log(t + 1.0)
    sig = np.zeros(N, dtype=np.float64)
    for tk in t_k:
        sig += np.cos(tk * log_t) / np.sqrt(tk)
    sig = (sig / max(len(t_k), 1)).astype(np.float32)
    print(f"  {name}: built in {time.perf_counter()-t0:.1f}s, RMS={float(np.sqrt(np.mean(sig.astype(np.float64)**2))):.5f}")
    np.save(cache, sig)
    return sig


print("Synthesising chirp signals (cached)…")
sig_zeta = make_chirp_cached(zeta,    "zeta")
sig_gue  = make_chirp_cached(gue_t_k, "gue1000")
sig_goe  = make_chirp_cached(goe_t_k, "goe1000")
print()


# ── PLL bank infrastructure ───────────────────────────────────────────────────
pairs = farey_rationals(Q_MAX)
freqs, pairs_kept = [], []
for p, q in pairs:
    f = FC_REF * p / q
    if 5.0 < f < SR * 0.45:
        freqs.append(f); pairs_kept.append((p, q))
freqs = np.asarray(freqs, dtype=np.float32)
print(f"Bank: {len(freqs)} PLLs, fc_ref={FC_REF}, q_max={Q_MAX}, K_p={K_P}")
print(f"GPU: {GPU_NAME}")
print()


def run_bank(sig):
    params = PLLParams(K_p=K_P, K_i=K_P * 0.05, rho=0.95)
    t0 = time.perf_counter()
    lock_map, _ = pll_bank_gpu(sig, freqs, SR, params, return_phase_error=False)
    print(f"  bank: {time.perf_counter()-t0:.1f}s")
    return lock_map


def per_pll_stats(lock_map, sr, transient_n, min_events=10):
    pooled = []
    info = []
    N = lock_map.shape[1]
    Nused = N - transient_n
    if Nused <= 0:
        return np.zeros(0), info
    for p in range(lock_map.shape[0]):
        s = lock_map[p, transient_n:]
        rec = extract_dwells(s)
        if rec.n_events < min_events: continue
        sp = np.diff(rec.lock_onsets)
        if sp.size == 0 or sp.mean() <= 0: continue
        sp_norm = sp / sp.mean()
        pooled.append(sp_norm.astype(np.float64))
        T_int = max(1, int(round(sp.mean())))
        nW = Nused // T_int
        F = float('nan')
        if nW >= 5:
            idx = rec.lock_onsets[rec.lock_onsets < nW * T_int] // T_int
            cnts = np.bincount(idx, minlength=nW).astype(np.float64)
            m = cnts.mean()
            if m > 0: F = float(cnts.var(ddof=1) / m)
        info.append(dict(
            pll_index=p, n_events=rec.n_events,
            mean_spacing_ms=float(sp.mean() * 1000.0 / sr),
            F_at_L1=F,
        ))
    return (np.concatenate(pooled) if pooled else np.zeros(0)), info


def summarise(name, lock_map):
    pooled, info = per_pll_stats(lock_map, SR, TRANSIENT_SAMPLES, min_events=10)
    if pooled.size == 0:
        return dict(name=name, n_qualifying=0, n_pooled=0)
    F_arr = np.array([d['F_at_L1'] for d in info if not np.isnan(d['F_at_L1'])])
    s = np.sort(pooled); n = s.size
    F_em = np.arange(1, n + 1) / n
    ks_p = float(np.max(np.abs(F_em - nns_cdf_poisson(s))))
    ks_o = float(np.max(np.abs(F_em - nns_cdf_goe(s))))
    ks_u = float(np.max(np.abs(F_em - nns_cdf_gue(s))))
    return dict(
        name=name, pooled=pooled, info=info,
        ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
        F_pp_mean=float(F_arr.mean()) if F_arr.size else float('nan'),
        F_pp_std=float(F_arr.std(ddof=1)) if F_arr.size > 1 else float('nan'),
        n_qualifying=len(info), n_pooled=pooled.size,
        mass_below_03=float((pooled < 0.3).mean()),
        best=min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0],
    )


# ── Run all 6 (3 signals × forward/reversed) ──────────────────────────────────
results = {}
for sig_name, sig in [('ζ', sig_zeta), ('GUE', sig_gue), ('GOE', sig_goe)]:
    print(f"── {sig_name} forward ──")
    lm = run_bank(sig)
    results[(sig_name, 'fwd')] = summarise(f"{sig_name} fwd", lm)
    del lm; cp.get_default_memory_pool().free_all_blocks()
    print(f"── {sig_name} reversed ──")
    lm = run_bank(sig[::-1].astype(np.float32))
    results[(sig_name, 'rev')] = summarise(f"{sig_name} rev", lm)
    del lm; cp.get_default_memory_pool().free_all_blocks()


# ── Master table ──────────────────────────────────────────────────────────────
print()
print("=" * 80)
print(f"Master table — q_max={Q_MAX}, K_p={K_P}, fc_ref={FC_REF}, "
      f"transient strip = {TRANSIENT_MS} ms, N_EIG={N_EIG}")
print("=" * 80)
print(f"  {'signal':<8}  {'dir':>3}  {'qual':>4}  {'pooled':>6}  "
      f"{'F_pp':>5}  {'std':>5}  {'<0.3':>5}  "
      f"{'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  {'KO−KU':>6}  best")
for sig_name in ['ζ', 'GUE', 'GOE']:
    for d in ['fwd', 'rev']:
        r = results[(sig_name, d)]
        if r.get('pooled') is None or len(r.get('pooled', [])) == 0:
            print(f"  {sig_name:<8}  {d:>3}  no qualifying PLLs")
            continue
        delta = r['ks_o'] - r['ks_u']
        print(f"  {sig_name:<8}  {d:>3}  {r['n_qualifying']:4d}  {r['n_pooled']:6d}  "
              f"{r['F_pp_mean']:5.3f}  {r['F_pp_std']:5.3f}  {r['mass_below_03']:5.3f}  "
              f"{r['ks_p']:5.3f}  {r['ks_o']:5.3f}  {r['ks_u']:5.3f}  {delta:+6.3f}  {r['best']}")
print()
print("  Theoretical references for mass at s<0.3:  Poisson 0.259, GOE 0.064, GUE 0.011")
print()


# ── Forward vs reversed two-sample KS for each signal ─────────────────────────
print("=" * 80)
print("Forward vs reversed two-sample KS (transient-stripped)")
print("=" * 80)
print(f"  {'signal':<8}  {'KS_two':>7}  {'p-value':>8}   interpretation")
for sig_name in ['ζ', 'GUE', 'GOE']:
    f = results[(sig_name, 'fwd')]; r = results[(sig_name, 'rev')]
    if f.get('pooled') is None or r.get('pooled') is None: continue
    s1 = np.sort(f['pooled']); s2 = np.sort(r['pooled'])
    n1, n2 = s1.size, s2.size
    if n1 < 5 or n2 < 5: continue
    pts = np.concatenate([s1, s2])
    cdf1 = np.searchsorted(s1, pts, side='right') / n1
    cdf2 = np.searchsorted(s2, pts, side='right') / n2
    ks_two = float(np.max(np.abs(cdf1 - cdf2)))
    p_two  = _ks_pvalue(ks_two, int(n1 * n2 / (n1 + n2)))
    interp = ("DIFFERENT (asymmetric)" if (ks_two > 0.10 and p_two < 0.05)
              else "EQUIVALENT (symmetric)" if ks_two < 0.05
              else "borderline")
    print(f"  {sig_name:<8}  {ks_two:7.4f}  {p_two:8.4f}   {interp}")
print()


# ── Verdict ───────────────────────────────────────────────────────────────────
print("=" * 80)
print("VERDICT — what does the instrument see?")
print("=" * 80)
gue_fwd = results[('GUE', 'fwd')]; goe_fwd = results[('GOE', 'fwd')]
zeta_fwd = results[('ζ', 'fwd')]
gue_best, goe_best = gue_fwd.get('best'), goe_fwd.get('best')
zeta_best = zeta_fwd.get('best')
gue_delta = (gue_fwd['ks_o'] - gue_fwd['ks_u']) if gue_fwd.get('pooled') is not None else 0
goe_delta = (goe_fwd['ks_o'] - goe_fwd['ks_u']) if goe_fwd.get('pooled') is not None else 0

print(f"  ζ forward best fit:    {zeta_best}   (KS_GOE−KS_GUE = "
      f"{zeta_fwd['ks_o']-zeta_fwd['ks_u']:+.4f})")
print(f"  GUE chirp best fit:    {gue_best}   (KS_GOE−KS_GUE = {gue_delta:+.4f})")
print(f"  GOE chirp best fit:    {goe_best}   (KS_GOE−KS_GUE = {goe_delta:+.4f})")
print()

# Decision logic
DECISIVE = 0.05
gue_decisive_GUE = (gue_delta > DECISIVE)   # GOE worse than GUE → GUE wins
gue_decisive_GOE = (gue_delta < -DECISIVE)
goe_decisive_GOE = (goe_delta < -DECISIVE)
goe_decisive_GUE = (goe_delta > DECISIVE)
gue_poiss = (gue_best == 'Poiss')
goe_poiss = (goe_best == 'Poiss')

if gue_poiss or goe_poiss:
    print(f"  → at least one calibration chirp falls back to Poisson best-fit.")
    print(f"    Generator/instrument issue — investigate before drawing conclusions.")
elif gue_decisive_GUE and goe_decisive_GOE:
    print(f"  → instrument distinguishes GOE from GUE.")
    print(f"    ζ landing at GOE means ζ deviates from the GUE conjecture under")
    print(f"    this measurement — surprising result, warrants careful follow-up.")
elif (gue_decisive_GOE or gue_best == 'GOE') and goe_decisive_GOE:
    print(f"  → instrument folds GUE onto GOE (GOE-projection confirmed).")
    print(f"    ζ landing at GOE is consistent with the GUE conjecture; we have")
    print(f"    a Poisson-vs-(GOE/GUE) detector but not a GUE-vs-GOE detector.")
else:
    print(f"  → ambiguous calibration.  Consider larger N or different detector.")
print()


# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey=True, sharex=True)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)
for col, sig_name in enumerate(['ζ', 'GUE', 'GOE']):
    for row, d in enumerate(['fwd', 'rev']):
        ax = axes[row, col]
        r = results[(sig_name, d)]
        if r.get('pooled') is None or r['pooled'].size == 0:
            ax.set_title(f"{sig_name} {d}: no data"); continue
        ax.hist(r['pooled'], bins=bin_edges, density=True, alpha=0.55, color='C0',
                label=f"empirical (n={r['pooled'].size})")
        ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
        ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
        ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.8, label='Wigner GUE')
        ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
        delta = r['ks_o'] - r['ks_u']
        ax.set_title(f"{sig_name} {d}\nbest={r['best']}  KS_O−KS_U={delta:+.3f}",
                      fontsize=9)
        ax.grid(True, alpha=0.3)
axes[0, 0].legend(fontsize=7, loc='upper right')
axes[0, 0].set_ylabel('forward')
axes[1, 0].set_ylabel('reversed')
axes[1, 0].set_xlabel('s'); axes[1, 1].set_xlabel('s'); axes[1, 2].set_xlabel('s')
fig.suptitle(f"Calibration controls — {N_EIG} eigenvalues × {DUR}s, transient {TRANSIENT_MS}ms")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "10_calibration.png"), dpi=110)
plt.close(fig)
print(f"  → plots/10_calibration.png")
