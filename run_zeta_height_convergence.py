"""ζ-zero height-dependent GUE convergence.

The Phase 5 result showed KS_GUE improves at higher zero heights (0.017
at low heights → 0.012 at heights ≈ 1.1M).  This run quantifies the
convergence by binning Odlyzko's 2M-zero file into ~20 height buckets
and computing analytical NNS in each.

The conjecture predicts KS_GUE → 0 as t → ∞ (asymptotic universality).
A clean monotone decrease across height bins is the empirical signature.

Output:
    data/zeta_height_convergence.json
    plots/24_zeta_height_convergence.png
"""
import os, sys, json, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from pll_bank import farey_rationals
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
ZEROS_PATH = os.path.join(DATA, "odlyzko_zeros6.txt")

# Use direct unfolded NNS (Riemann–von Mangoldt density) — bypasses the
# per-PLL framework so we can isolate the height-dependence cleanly.

def vonMangoldt_density(t):
    """Approximate density of ζ zeros at height t (unfolded scale)."""
    return np.log(np.maximum(t / (2 * np.pi), 1.0)) / (2.0 * np.pi)


def unfolded_spacings(zeros):
    """Apply the Riemann–von Mangoldt density to get unit-mean spacings."""
    z = np.asarray(zeros, dtype=np.float64)
    # Cumulative count function N(t) ≈ (t/2π)·log(t/2πe) + 7/8
    N_smooth = (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8
    sp = np.diff(N_smooth)   # already approximately unit mean
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0: return np.zeros(0)
    return sp / sp.mean()


def classify(spacings):
    if spacings.size < 50: return dict(n=int(spacings.size), best='insufficient')
    s = np.sort(spacings); n = s.size
    F_em = np.arange(1, n + 1) / n
    ks_p = float(np.max(np.abs(F_em - nns_cdf_poisson(s))))
    ks_o = float(np.max(np.abs(F_em - nns_cdf_goe(s))))
    ks_u = float(np.max(np.abs(F_em - nns_cdf_gue(s))))
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=n, ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((spacings < 0.3).mean()), best=best)


print(f"Loading {ZEROS_PATH}…")
zeros = np.loadtxt(ZEROS_PATH)
print(f"  {zeros.size} zeros loaded; height range [{zeros[0]:.1f}, {zeros[-1]:.1f}]")
print()


# ─── Bin by index (each bin contains 100k zeros) ─────────────────────────────
print("=" * 100)
print("ζ-zero NNS convergence — 100k zeros per height-bin (unfolded by Riemann-von Mangoldt)")
print("=" * 100)
print(f"  {'idx_lo':>10}  {'idx_hi':>10}  {'t_lo':>9}  {'t_hi':>9}  "
      f"{'n_pool':>7}  {'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  {'gap':>6}  best")

BIN_SIZE = 100_000
results = []
for start in range(0, zeros.size, BIN_SIZE):
    end = min(start + BIN_SIZE, zeros.size)
    if end - start < 1000: continue
    chunk = zeros[start:end]
    sp = unfolded_spacings(chunk)
    cl = classify(sp)
    rec = dict(idx_lo=int(start), idx_hi=int(end),
                t_lo=float(chunk[0]), t_hi=float(chunk[-1]), **cl)
    results.append(rec)
    if cl.get('best') == 'insufficient':
        print(f"  {start:>10}  {end:>10}  {chunk[0]:>9.1f}  {chunk[-1]:>9.1f}  "
              f"insufficient")
    else:
        print(f"  {start:>10}  {end:>10}  {chunk[0]:>9.1f}  {chunk[-1]:>9.1f}  "
              f"{cl['n']:>7}  {cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  "
              f"{cl['ks_u']:5.3f}  {cl['gap']:+6.3f}  {cl['best']}", flush=True)
print()


# ─── Plot KS_GUE vs height ────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

valid = [r for r in results if r.get('best') != 'insufficient']
heights = [(r['t_lo'] + r['t_hi']) / 2 for r in valid]
ks_u = [r['ks_u'] for r in valid]
ks_o = [r['ks_o'] for r in valid]
ks_p = [r['ks_p'] for r in valid]
gaps = [r['gap'] for r in valid]

ax = axes[0]
ax.semilogx(heights, ks_u, 'r.-', label='KS to Wigner GUE', lw=1.5)
ax.semilogx(heights, ks_o, 'C2.-', label='KS to GOE', lw=1.0)
ax.semilogx(heights, ks_p, 'g.--', label='KS to Poisson', lw=1.0)
ax.axhline(0.022, color='gray', ls=':', lw=0.5, label='calibrator threshold')
ax.set_xlabel('zero height (mean of bin)')
ax.set_ylabel('KS distance')
ax.set_title("KS distance to RMT references vs zero height")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, which='both')

ax = axes[1]
ax.semilogx(heights, gaps, 'k.-', lw=1.5)
ax.axhline(0, color='gray', ls=':')
ax.axhline(0.05, color='r', ls=':', label='decisive threshold')
ax.set_xlabel('zero height (mean of bin)')
ax.set_ylabel('KS_GOE − KS_GUE  (positive = GUE wins)')
ax.set_title("Family symmetry decisiveness vs height")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, which='both')

fig.suptitle(f"ζ height-dependent NNS convergence — Odlyzko zeros6 ({len(valid)} bins of 100k zeros)")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOTS, "24_zeta_height_convergence.png"), dpi=110)
plt.close(fig)
print(f"  → plots/24_zeta_height_convergence.png")


# Save
with open(os.path.join(DATA, "zeta_height_convergence.json"), 'w') as f:
    json.dump({'bin_size': BIN_SIZE, 'bins': results}, f, indent=2, default=str)
print(f"  → data/zeta_height_convergence.json")

# Summary
ks_u_arr = np.array(ks_u)
print()
print(f"  Summary: KS_GUE across {len(valid)} bins")
print(f"    bin 1 (lowest heights):  KS_GUE = {ks_u_arr[0]:.4f}")
print(f"    bin {len(valid)} (highest heights): KS_GUE = {ks_u_arr[-1]:.4f}")
print(f"    monotone decrease? {bool(np.all(np.diff(ks_u_arr) <= 0.001))}")
print(f"    mean KS_GUE: {ks_u_arr.mean():.4f}")
