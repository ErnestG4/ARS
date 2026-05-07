"""
Decisive run — 1000 ζ zeros × 300 s, q_max=8, K_p=0.02, fc_ref=115.55,
PLL onset transient stripped from each PLL's output.

Goals:
    1. Resolve the GOE/GUE distinction in the per-PLL NNS by getting
       enough events (~3000 pooled spacings expected).
    2. Repeat the time-reversal test on the transient-stripped output.
       If the forward/reversed asymmetry shrinks, the previous asymmetry
       was driven by IIR settling.  If it persists, the asymmetry is
       genuine in the chirp dynamics.

Acceptance:
    KS_GOE − KS_GUE > 0.05 (or vice versa)  →  decisive separation
    Otherwise  →  instrument resolution is the limiting factor.
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
import cupy as cp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ── Config ────────────────────────────────────────────────────────────────────
SR        = 44100.0
DUR       = 300.0
NZ        = 1000
FC_REF    = 115.55
Q_MAX     = 8
K_P       = 0.02
TRANSIENT_MS = 500.0      # strip from each PLL's lock_map before stats

ZEROS_PATH = os.path.join(THIS_DIR, "zeros_1000.npy")
PLOT_DIR   = os.path.join(THIS_DIR, "plots")


# ── Build signal ──────────────────────────────────────────────────────────────
print(f"Loading {NZ} ζ zeros …")
zeros = np.load(ZEROS_PATH).astype(np.float64)
assert len(zeros) >= NZ, f"only have {len(zeros)} zeros, need {NZ}"
zeros = zeros[:NZ]
print(f"  range: [{zeros.min():.2f}, {zeros.max():.2f}]")
print()


def make_zeta_chirp(zeros, sr, dur):
    N = int(sr * dur)
    t = np.arange(1, N + 1, dtype=np.float64) / sr
    log_t = np.log(t + 1.0)
    sig = np.zeros(N, dtype=np.float64)
    for tn in zeros:
        sig += np.cos(tn * log_t) / np.sqrt(tn)
    return (sig / max(len(zeros), 1)).astype(np.float32)


print(f"Synthesising {DUR}s chirp at {SR/1000:g} kHz with {NZ} zeros …")
t0 = time.perf_counter()
sig_fwd = make_zeta_chirp(zeros, SR, DUR)
print(f"  signal: {len(sig_fwd)} samples, "
      f"RMS={float(np.sqrt(np.mean(sig_fwd.astype(np.float64)**2))):.5f}, "
      f"build {time.perf_counter()-t0:.1f}s")
sig_rev = sig_fwd[::-1].astype(np.float32)
print()


# ── PLL bank ──────────────────────────────────────────────────────────────────
pairs = farey_rationals(Q_MAX)
freqs, pairs_kept = [], []
for p, q in pairs:
    f = FC_REF * p / q
    if 5.0 < f < SR * 0.45:
        freqs.append(f)
        pairs_kept.append((p, q))
freqs = np.asarray(freqs, dtype=np.float32)
print(f"Bank: {len(freqs)} PLLs, fc_ref={FC_REF}, q_max={Q_MAX}, K_p={K_P}")
print(f"GPU: {GPU_NAME}")
print()


def run_bank(sig):
    params = PLLParams(K_p=K_P, K_i=K_P * 0.05, rho=0.95)
    t0 = time.perf_counter()
    lock_map, _ = pll_bank_gpu(sig, freqs, SR, params, return_phase_error=False)
    print(f"  bank run: {time.perf_counter()-t0:.1f}s")
    return lock_map


# ── Per-PLL stats with transient stripping ────────────────────────────────────
TRANSIENT_SAMPLES = int(round(SR * TRANSIENT_MS * 0.001))


def per_pll_stats(lock_map, sr, transient_n, min_events=10):
    """Strip first `transient_n` samples; for each PLL with ≥min_events
    events in the remaining window, normalise spacings by per-PLL mean and
    pool.  Also compute per-PLL Fano F."""
    pooled_spacings = []
    info = []
    N = lock_map.shape[1]
    Nused = N - transient_n
    if Nused <= 0:
        return np.zeros(0), info
    for p in range(lock_map.shape[0]):
        # Apply transient strip on the lock_map row.
        s = lock_map[p, transient_n:]
        rec = extract_dwells(s)
        if rec.n_events < min_events:
            continue
        sp = np.diff(rec.lock_onsets)
        if sp.size == 0 or sp.mean() <= 0:
            continue
        sp_norm = sp / sp.mean()
        pooled_spacings.append(sp_norm.astype(np.float64))
        # Fano at L=1 in this PLL's mean-spacing units.
        T_int = max(1, int(round(sp.mean())))
        nW = Nused // T_int
        F = float('nan')
        if nW >= 5:
            idx = rec.lock_onsets[rec.lock_onsets < nW * T_int] // T_int
            cnts = np.bincount(idx, minlength=nW).astype(np.float64)
            m = cnts.mean()
            if m > 0:
                F = float(cnts.var(ddof=1) / m)
        info.append(dict(
            pll_index=p,
            n_events=rec.n_events,
            mean_spacing_ms=float(sp.mean() * 1000.0 / sr),
            F_at_L1=F,
        ))
    pooled = np.concatenate(pooled_spacings) if pooled_spacings else np.zeros(0)
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


def summarise(name, lock_map):
    pooled, info = per_pll_stats(lock_map, SR, TRANSIENT_SAMPLES, min_events=10)
    if pooled.size == 0:
        return None
    ks_p, p_p = ks_to(pooled, nns_cdf_poisson)
    ks_o, p_o = ks_to(pooled, nns_cdf_goe)
    ks_u, p_u = ks_to(pooled, nns_cdf_gue)
    F_arr = np.array([d['F_at_L1'] for d in info if not np.isnan(d['F_at_L1'])])
    return dict(
        name=name, pooled=pooled, info=info,
        ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
        p_p=p_p, p_o=p_o, p_u=p_u,
        F_pp_mean=float(F_arr.mean()) if F_arr.size else float('nan'),
        F_pp_std=float(F_arr.std(ddof=1)) if F_arr.size > 1 else float('nan'),
        n_qualifying=len(info), n_pooled=pooled.size,
        mass_below_03=float((pooled < 0.3).mean()),
        best=min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0],
    )


# ── Run ───────────────────────────────────────────────────────────────────────
print("=" * 80)
print(f"FORWARD (transient-stripped: first {TRANSIENT_MS} ms = {TRANSIENT_SAMPLES} samples)")
print("=" * 80)
lm_fwd = run_bank(sig_fwd)
sum_fwd = summarise("ζ forward", lm_fwd)
del lm_fwd
cp.get_default_memory_pool().free_all_blocks()

print("=" * 80)
print(f"REVERSED (signal[::-1])")
print("=" * 80)
lm_rev = run_bank(sig_rev)
sum_rev = summarise("ζ reversed", lm_rev)
del lm_rev
cp.get_default_memory_pool().free_all_blocks()


# ── Report ────────────────────────────────────────────────────────────────────
print()
print("=" * 80)
print("Per-PLL NNS — FORWARD vs REVERSED  (transient-stripped)")
print("=" * 80)
print(f"  {'metric':<22}  {'forward':>10}  {'reversed':>10}")
for label, key in [
    ("qualifying PLLs",       'n_qualifying'),
    ("pooled spacings",       'n_pooled'),
    ("F per PLL (mean)",      'F_pp_mean'),
    ("F per PLL (std)",       'F_pp_std'),
    ("mass at s < 0.3",       'mass_below_03'),
    ("KS to Poisson",         'ks_p'),
    ("KS to GOE",             'ks_o'),
    ("KS to GUE",             'ks_u'),
    ("p-value Poisson",       'p_p'),
    ("p-value GOE",           'p_o'),
    ("p-value GUE",           'p_u'),
]:
    fv = sum_fwd[key] if sum_fwd is not None else float('nan')
    rv = sum_rev[key] if sum_rev is not None else float('nan')
    print(f"  {label:<22}  {fv:>10.4f}  {rv:>10.4f}")
print(f"  {'best fit':<22}  {sum_fwd['best']:>10}  {sum_rev['best']:>10}")
print()


# ── GOE-vs-GUE separation ──
print("=" * 80)
print("GOE vs GUE separation")
print("=" * 80)
for label, s in [('forward', sum_fwd), ('reversed', sum_rev)]:
    if s is None: continue
    delta = s['ks_o'] - s['ks_u']   # +ve → GUE fits better; -ve → GOE
    sign = "GUE wins" if delta > 0 else "GOE wins"
    decisive = abs(delta) > 0.05
    flag = "DECISIVE" if decisive else "NOT decisive"
    print(f"  {label}: KS_GOE − KS_GUE = {delta:+.4f}   "
          f"({sign}, {flag})")
print()


# ── Two-sample KS forward vs reversed ──
if sum_fwd is not None and sum_rev is not None and sum_fwd['pooled'].size > 5 and sum_rev['pooled'].size > 5:
    s1 = np.sort(sum_fwd['pooled'])
    s2 = np.sort(sum_rev['pooled'])
    n1, n2 = s1.size, s2.size
    pts = np.concatenate([s1, s2])
    cdf1 = np.searchsorted(s1, pts, side='right') / n1
    cdf2 = np.searchsorted(s2, pts, side='right') / n2
    ks_two = float(np.max(np.abs(cdf1 - cdf2)))
    p_two  = _ks_pvalue(ks_two, int(n1 * n2 / (n1 + n2)))
    print(f"  two-sample KS forward vs reversed:  KS = {ks_two:.4f}, p = {p_two:.4f}")
    if ks_two > 0.10 and p_two < 0.05:
        print(f"  → forward and reversed are DIFFERENT — genuine time-asymmetry")
    elif ks_two < 0.05:
        print(f"  → forward and reversed are EQUIVALENT — measurement is time-symmetric")
    else:
        print(f"  → ambiguous — borderline asymmetry")
print()


# ── Top-event PLL table ──
print("=" * 80)
print("Top 10 forward-locking PLLs (by event count)")
print("=" * 80)
print(f"  {'p:q':>6}  {'n_evt_fwd':>9}  {'n_evt_rev':>9}  {'F_fwd':>6}  {'F_rev':>6}  {'mean_dwell_ms':>13}")
fwd_by_idx = {d['pll_index']: d for d in sum_fwd['info']} if sum_fwd else {}
rev_by_idx = {d['pll_index']: d for d in sum_rev['info']} if sum_rev else {}
fwd_sorted = sorted(sum_fwd['info'], key=lambda d: -d['n_events']) if sum_fwd else []
for d in fwd_sorted[:10]:
    pq = pairs_kept[d['pll_index']]
    rev_d = rev_by_idx.get(d['pll_index'])
    n_rev = rev_d['n_events'] if rev_d else 0
    F_rev = rev_d['F_at_L1'] if rev_d else float('nan')
    print(f"  {pq[0]}:{pq[1]:<3d}  {d['n_events']:9d}  {n_rev:9d}  "
          f"{d['F_at_L1']:6.3f}  {F_rev:6.3f}  {d['mean_spacing_ms']:13.2f}")
print()


# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)
for ax, (label, s) in zip(axes, [('forward', sum_fwd), ('reversed', sum_rev)]):
    if s is None or s['pooled'].size == 0:
        ax.set_title(f"{label} — no data")
        continue
    ax.hist(s['pooled'], bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"empirical (n={s['pooled'].size})")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.8, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    ax.set_xlabel("normalised spacing  s")
    ax.set_title(f"{label}\nbest={s['best']}  KS_GOE={s['ks_o']:.3f}  "
                  f"KS_GUE={s['ks_u']:.3f}  mass<0.3={s['mass_below_03']:.3f}")
    ax.grid(True, alpha=0.3)
axes[0].legend(fontsize=8, loc='upper right')
axes[0].set_ylabel("P(s)")
fig.suptitle(f"Decisive run — {NZ} zeros × {DUR}s, transient stripped {TRANSIENT_MS}ms")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "09_decisive.png"), dpi=110)
plt.close(fig)
print(f"  → plots/09_decisive.png")


# ── Verdict ───────────────────────────────────────────────────────────────────
print()
print("=" * 80)
print("VERDICT")
print("=" * 80)
if sum_fwd is None:
    print("  insufficient data — abort.")
else:
    delta_fwd = sum_fwd['ks_o'] - sum_fwd['ks_u']
    if abs(delta_fwd) > 0.05:
        winner = "GUE" if delta_fwd > 0 else "GOE"
        print(f"  forward NNS: KS_GOE − KS_GUE = {delta_fwd:+.4f}   →   {winner} wins decisively")
    else:
        print(f"  forward NNS: KS_GOE − KS_GUE = {delta_fwd:+.4f}   →   "
              f"NOT decisive at this n={sum_fwd['n_pooled']}")
    print(f"  forward F per PLL = {sum_fwd['F_pp_mean']:.3f} ± {sum_fwd['F_pp_std']:.3f}  "
          f"(< 1 → level repulsion)")
    print(f"  forward mass<0.3 = {sum_fwd['mass_below_03']:.4f}  "
          f"(theoretical: Poisson 0.259, GOE 0.064, GUE 0.011)")
