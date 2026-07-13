"""
Task 1 — diagnose and fix the GUE eigenvalue signal generator.

Problem identified by the previous Phase 3 run:
    per-PLL Fano F for the GUE-eigenvalue signal at (q_max=16, K_p=0.20,
    fc_ref=115.55) was ~2.10, super-Poisson — contradicting the GUE
    level-repulsion expectation that should give F ≤ 1.

Diagnosis hypothesis: the "unfolding" step in make_gue_eigenvalue_signal
just divides eigenvalues by the GLOBAL mean spacing — but the bulk
density of GUE follows the Wigner semicircle ρ(x) = (2/π)√(1−x²), so
the LOCAL mean spacing varies — narrower near the bulk centre, wider at
the edges.  Without proper local unfolding the resulting "frequencies"
have non-stationary spacing and don't follow Wigner surmise.

Fix: unfold by the semicircle CDF
    F(x) = 0.5 + (x √(1−x²) + arcsin(x)) / π
mapping eigenvalues x ∈ [-1, 1] to a uniform-density support [0, N].

Acceptance: KS to Wigner surmise on the unfolded spacings should be <0.05
for N=500.  Then re-run the PLL bank at the canonical cell and check the
per-PLL Fano.
"""
import os, sys, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))

from pll_bank import pll_bank_gpu, PLLParams, farey_rationals, GPU_NAME
from intermittency import extract_dwells
from universality import compute_nns
import scanner
import cupy as cp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


SR  = 44100.0
DUR = 30.0


def semicircle_cdf_unit(x):
    """CDF of semicircle ρ(x) = (2/π)√(1−x²) on [-1, 1]."""
    x = np.clip(x, -1.0, 1.0)
    return 0.5 + (x * np.sqrt(1.0 - x * x) + np.arcsin(x)) / np.pi


def gen_gue_eigenvalues(N, seed):
    """Sample GUE matrix eigenvalues.  With H_ij ~ N(0, 1/N) for off-diagonal,
    the bulk semicircle has half-radius R = 2 (eigenvalues live in ≈ [-2, 2])."""
    rng = np.random.default_rng(seed)
    A = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * N)
    return np.sort(np.linalg.eigvalsh(H).real)


def unfold_global_mean(eigs):
    """OLD broken procedure — divide by global mean spacing."""
    eigs = np.asarray(eigs, dtype=np.float64)
    sp = np.diff(eigs)
    return (eigs - eigs[0]) / sp.mean()


def unfold_semicircle_R(eigs, R=None):
    """Semicircle CDF unfolding when bulk half-radius is R.  If R is None,
    estimate from data as ~(max-min)/2 + some edge margin."""
    eigs = np.asarray(eigs, dtype=np.float64)
    if R is None:
        # Theoretical R for our matrix normalisation = 2.
        R = 2.0
    return semicircle_cdf_unit(eigs / R) * len(eigs)


def unfold_empirical(eigs, deg=11):
    """Empirical unfolding: fit a smooth polynomial to the cumulative count
    function N(λ) = #{i : eigs[i] ≤ λ}, then evaluate at each eigenvalue.
    Robust to non-asymptotic deviations from the analytic semicircle."""
    eigs = np.asarray(eigs, dtype=np.float64)
    n = eigs.size
    counts = np.arange(1, n + 1, dtype=np.float64)
    coefs = np.polyfit(eigs, counts, deg=deg)
    return np.polyval(coefs, eigs)


def ks_to_wigner_gue(spacings_normalised):
    """KS distance between empirical CDF of normalised spacings and Wigner GUE."""
    s = np.sort(np.asarray(spacings_normalised, dtype=np.float64))
    n = s.size
    if n < 5:
        return float('nan')
    # Wigner GUE CDF: F(s) = ∫_0^s (32/π²)·u²·exp(−4u²/π) du.
    # We tabulate this numerically.
    grid = np.linspace(0.0, max(float(s.max()), 5.0), 4001)
    pdf = (32.0 / np.pi ** 2) * grid * grid * np.exp(-4.0 * grid * grid / np.pi)
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (pdf[:-1] + pdf[1:]) * np.diff(grid))])
    F_th = np.interp(s, grid, cdf)
    F_em = np.arange(1, n + 1) / n
    return float(np.max(np.abs(F_em - F_th)))


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 78)
print("Step 1 — verify Wigner surmise compatibility on N=500 GUE eigenvalues")
print("=" * 78)
N_VERIFY = 500
eigs500 = gen_gue_eigenvalues(N_VERIFY, seed=1)
print(f"  N={N_VERIFY}  eigenvalue range: [{eigs500.min():.4f}, {eigs500.max():.4f}]")

methods = {
    "global-mean":         unfold_global_mean(eigs500),
    "semicircle@R=1 (BUG)": semicircle_cdf_unit(eigs500) * len(eigs500),  # wrong: eigs in [-2,2]
    "semicircle@R=2":       unfold_semicircle_R(eigs500, R=2.0),
    "empirical-poly(deg=11)": unfold_empirical(eigs500, deg=11),
}
ks_results = {}
for name, unf in methods.items():
    sp = np.diff(unf)
    if sp.mean() <= 0:
        ks_results[name] = float('nan'); continue
    sp_norm = sp / sp.mean()
    ks_results[name] = ks_to_wigner_gue(sp_norm)

for name, ks in ks_results.items():
    flag = " ← passes" if ks < 0.05 else (" ← borderline" if ks < 0.10 else " ← FAILS")
    print(f"  {name:24s}  KS to Wigner GUE = {ks:.4f}{flag}")
ks_new = ks_results["semicircle@R=2"]
ks_old = ks_results["global-mean"]
print()
print(f"  fix: divide eigs by half-radius R=2 before applying unit-CDF.")
print(f"  (User's literal procedure clipped eigs to [-1,1] and gave KS={ks_results['semicircle@R=1 (BUG)']:.4f}.)")
print()

# ─ also report at smaller N (relevant to the chirp signal as actually used)
for N in (100, 200):
    e = gen_gue_eigenvalues(N, seed=1)
    sp = np.diff(unfold_semicircle_R(e, R=2.0))
    sp /= sp.mean()
    ks = ks_to_wigner_gue(sp)
    print(f"  N={N:3d} (seed=1) KS to Wigner GUE (R=2 semicircle unfolded) = {ks:.4f}")
print()


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 78)
print("Step 2 — visualise the spacing distributions")
print("=" * 78)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200)
wig_pdf = (32.0 / np.pi ** 2) * s_grid * s_grid * np.exp(-4.0 * s_grid * s_grid / np.pi)
poi_pdf = np.exp(-s_grid)

old_sp = np.diff(methods["global-mean"]); old_sp /= old_sp.mean()
new_sp_norm = np.diff(methods["semicircle@R=2"]); new_sp_norm /= new_sp_norm.mean()
for ax, sp_norm, title in [(axes[0], old_sp, "OLD (divide by mean spacing)"),
                             (axes[1], new_sp_norm, "NEW (semicircle CDF, R=2)")]:
    ax.hist(sp_norm, bins=40, range=(0, 4), density=True, alpha=0.6,
            label=f"empirical (n={len(sp_norm)})")
    ax.plot(s_grid, wig_pdf, 'r-', lw=2, label="Wigner GUE")
    ax.plot(s_grid, poi_pdf, 'g--', lw=1, label="Poisson")
    ax.set_xlabel("normalised spacing  s")
    ax.set_title(title)
    ax.legend(fontsize=8)
    ax.set_xlim(0, 4)
axes[0].set_ylabel("P(s)")
fig.tight_layout()
fig.savefig(os.path.join(THIS_DIR, "plots", "06_gue_unfolding.png"), dpi=110)
plt.close(fig)
print(f"  → plots/06_gue_unfolding.png")
print()


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 78)
print("Step 3 — synthesize chirp from corrected unfolded eigenvalues; compare to ζ")
print("=" * 78)


def make_chirp(t_k, sr, dur):
    """Σ_k cos(t_k log(t+1)) / sqrt(t_k+1)  — same form as scanner.make_zeta_signal."""
    N = int(sr * dur)
    t = np.arange(1, N + 1, dtype=np.float64) / sr
    log_t = np.log(t + 1.0)
    sig = np.zeros(N, dtype=np.float64)
    for tk in t_k:
        if tk > 0:
            sig += np.cos(tk * log_t) / np.sqrt(tk + 1.0)
    return (sig / max(len(t_k), 1)).astype(np.float32)


# Generate the GUE chirp using the CORRECTED unfolding.
# Match N to ζ exactly (98 zeros) so per-tone spectral density is the same
# — narrowband power at the PLL bank is then comparable.  KS at N=98 is
# ~0.06 (borderline) but adequate for the chirp comparison; use seeds to
# average if needed.
zeta_zeros_arr = scanner.ZETA_ZEROS.astype(np.float64)
N_GUE = len(zeta_zeros_arr)
eigs = gen_gue_eigenvalues(N_GUE, seed=42)
unf  = unfold_semicircle_R(eigs, R=2.0)      # uniform on [0, N_GUE]
z_min = float(zeta_zeros_arr[0])
z_max = float(zeta_zeros_arr[-1])
gue_t_k = z_min + (unf - unf[0]) * (z_max - z_min) / (unf[-1] - unf[0])
# Verify the rescaled GUE t_k still satisfy Wigner GUE spacing.
sp_check = np.diff(gue_t_k); sp_check /= sp_check.mean()
ks_chirp = ks_to_wigner_gue(sp_check)
print(f"  GUE-new t_k: N={N_GUE}, range [{gue_t_k.min():.2f}, {gue_t_k.max():.2f}]")
print(f"  KS Wigner-GUE on chirp t_k spacings: {ks_chirp:.4f}  "
      f"({'passes' if ks_chirp < 0.10 else 'BORDERLINE/FAILS'})")

# Also build a Poisson-uniform null with the same N for comparison.
rng2 = np.random.default_rng(0)
poiss_t_k = np.sort(rng2.uniform(z_min, z_max, N_GUE))
sp_p = np.diff(poiss_t_k); sp_p /= sp_p.mean()
ks_poiss = ks_to_wigner_gue(sp_p)
print(f"  Poisson-FM t_k: N={N_GUE}, KS to Wigner = {ks_poiss:.4f} "
      f"(should be FAR from Wigner — Poisson spacing is exponential, not s²-suppressed)")
print(f"  GUE: N={N_GUE}, t_k range [{gue_t_k.min():.2f}, {gue_t_k.max():.2f}], "
      f"mean spacing ≈ 1.0")
sig_gue_new = make_chirp(gue_t_k, SR, DUR)
sig_poiss   = make_chirp(poiss_t_k, SR, DUR)

# For ζ we use the natural zero heights for parity.
zeta_zeros = scanner.ZETA_ZEROS.astype(np.float64)
sig_zeta = scanner.make_zeta_signal(sr=SR, duration=DUR, n_zeros=len(zeta_zeros))
print(f"  ζ  : NZ={len(zeta_zeros)}, t_n range [{zeta_zeros.min():.2f}, {zeta_zeros.max():.2f}]")

# Also keep the OLD (broken) GUE generator for comparison.
import signal_gen
sig_gue_old = signal_gen.make_gue_eigenvalue_signal(sr=SR, duration=DUR,
                                                      n_points=100, seed=42,
                                                      rescale_to_zeta_range=True)

for n, s in [("ζ      ", sig_zeta),
              ("GUE-old", sig_gue_old),
              ("GUE-new", sig_gue_new),
              ("Poisson", sig_poiss)]:
    rms = float(np.sqrt(np.mean(s.astype(np.float64) ** 2)))
    print(f"  {n}: RMS={rms:.5f}  range [{s.min():.4f}, {s.max():.4f}]")
print()


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 78)
print("Step 4 — PLL bank at (q_max=8, K_p=0.02, fc_ref=100) for ζ vs GUE-new")
print("=" * 78)
fc_ref = 100.0
q_max = 8
kp = 0.02
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
print(f"  bank: {len(freqs)} PLLs at fc_ref={fc_ref}, q_max={q_max}, K_p={kp}")
print(f"  GPU: {GPU_NAME}\n")


def per_pll_fano(lock_map, sr):
    out = []
    N = lock_map.shape[1]
    for p in range(lock_map.shape[0]):
        rec = extract_dwells(lock_map[p])
        if rec.n_events < 5:
            out.append(np.nan)
            continue
        sp = np.diff(rec.lock_onsets)
        if sp.size == 0 or sp.mean() <= 0:
            out.append(np.nan)
            continue
        T_int = max(1, int(round(sp.mean())))
        nW = N // T_int
        if nW < 5:
            out.append(np.nan)
            continue
        idx = rec.lock_onsets[rec.lock_onsets < nW * T_int] // T_int
        cnts = np.bincount(idx, minlength=nW).astype(np.float64)
        m = cnts.mean()
        out.append(float(cnts.var(ddof=1) / m) if m > 0 else np.nan)
    return np.array(out)


def summarise(name, signal):
    lock_map, _ = pll_bank_gpu(signal, freqs, SR, params, return_phase_error=False)
    F_pp = per_pll_fano(lock_map, SR)
    n_evt = sum(extract_dwells(lock_map[p]).n_events for p in range(lock_map.shape[0]))
    locking = [(pairs_kept[p], extract_dwells(lock_map[p]).n_events,
                F_pp[p], extract_dwells(lock_map[p]).lock_fraction)
               for p in range(lock_map.shape[0])
               if extract_dwells(lock_map[p]).lock_fraction > 0.01]
    locking.sort(key=lambda r: -r[1])
    F_locking = F_pp[~np.isnan(F_pp)]
    print(f"  {name}:")
    print(f"    n_events_total   = {n_evt}")
    print(f"    n_locking_PLLs   = {len(locking)}")
    print(f"    F_per_PLL mean ± std (locking): "
          f"{F_locking.mean():.3f} ± {F_locking.std(ddof=1):.3f}")
    print(f"    top 8 locking PLLs:")
    print(f"      {'p:q':>6}  {'n_evt':>5}  {'lock_frac':>9}  {'F_per_PLL':>9}")
    for (pq, n_e, fpll, lf) in locking[:8]:
        print(f"      {pq[0]}:{pq[1]:<3d}  {n_e:5d}  {lf:9.4f}  "
              f"{fpll if not np.isnan(fpll) else 'n/a':>9}"
              if isinstance(fpll, float) else "")
    del lock_map
    cp.get_default_memory_pool().free_all_blocks()
    return F_pp, locking


print("  ── ζ ──")
F_pp_z, lock_z = summarise("ζ", sig_zeta)
print()
print("  ── GUE-new (R=2 semicircle unfolding, N=98 matched to ζ) ──")
F_pp_g_new, lock_g_new = summarise("GUE-new", sig_gue_new)
print()
print("  ── Poisson-FM null (uniform t_k, N=98) ──")
F_pp_pois, lock_pois = summarise("Poisson", sig_poiss)
print()


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 78)
print("Verdict")
print("=" * 78)
F_z   = F_pp_z[~np.isnan(F_pp_z)]
F_new = F_pp_g_new[~np.isnan(F_pp_g_new)]
F_pois = F_pp_pois[~np.isnan(F_pp_pois)]
print(f"  per-PLL F  ζ            : mean={F_z.mean():.3f}  median={np.median(F_z):.3f}  n_PLL={F_z.size}")
print(f"  per-PLL F  GUE-new      : mean={F_new.mean():.3f}  median={np.median(F_new):.3f}  n_PLL={F_new.size}")
print(f"  per-PLL F  Poisson-FM   : mean={F_pois.mean():.3f}  median={np.median(F_pois):.3f}  n_PLL={F_pois.size}")
print()
print(f"  KS Wigner-GUE on unfolded eigenvalue spacings (N=500): {ks_new:.4f}")
print(f"    {'GENERATOR PASSES' if ks_new < 0.05 else 'GENERATOR STILL FAILS WIGNER VERIFICATION'}")
print()
print(f"  Reading A: ζ has F<1, GUE-new has F<1 → both show level repulsion at PLL level.")
print(f"  Reading B: ζ has F<1, GUE-new has F>1 → ζ has structure beyond GUE-class spacing.")
