"""Second-order statistics across all collected L-function families.

NNS (one-point spacing) gave Wigner GUE for ζ, ECs, and both Dirichlet
classes, with edge-only differentiation.  This run compares
second-order statistics — pair correlation R₂(r) and number variance
Σ²(L) — which contain richer information about long-range correlations.

For each family, take the unfolded zeros (or their analytical-passage-time
events), apply universality.pair_correlation and universality.number_variance,
plot vs analytical Wigner GUE and Poisson references.

Output:
    data/second_order_results.json
    plots/26_second_order.png
"""
import os, sys, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from pll_bank import farey_rationals
from universality import (
    pair_correlation, number_variance, spectral_form_factor,
    nns_poisson, nns_goe, nns_gue,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")


def unfolded_spacings_zeta(zeros):
    """Riemann-von Mangoldt density unfolding."""
    z = np.asarray(zeros, dtype=np.float64)
    N_smooth = (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8
    return N_smooth   # already approximately unit-mean spacing


def unfolded_spacings_lfunction(zeros, conductor):
    """Approximate unfolding by log(C)/(2π) density.

    For an L-function of analytic conductor C, the local density of zeros
    near height γ is ~ log(C γ / (2π)) / (2π).  Use this to convert raw
    γ_n to an unfolded variable with unit local mean spacing.
    """
    z = np.asarray(zeros, dtype=np.float64)
    z = z[z > 0]
    if z.size < 2: return np.zeros(0)
    # Cumulative count smooth function: integrate the density.
    # N(γ) ≈ (γ/(2π)) (log(C γ / (2π e)))
    # Use γ_smooth = γ / (2π) * (log(C γ /(2π)) - 1)  as unfolded.
    arg = np.maximum(conductor * z / (2*np.pi), 1.0)
    return (z / (2*np.pi)) * (np.log(arg) - 1.0)


# ─── Build event lists for each family ────────────────────────────────────────
print("Loading data sources …")
events_by_family = {}

# 1. ζ low (first 100k from zeros6)
zeros6 = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"))
events_by_family['ζ low (heights 14-75k)'] = unfolded_spacings_zeta(zeros6[:100000])

# 2. ζ high
events_by_family['ζ high (heights ~1.1M)'] = unfolded_spacings_zeta(zeros6[1900000:2000000])

# 3. Elliptic-curve L-functions (LMFDB), aggregate of all curves' unfolded zeros
print("  loading LMFDB curves …")
with open(os.path.join(DATA, "lmfdb_zeros.json")) as f:
    lmfdb = json.load(f)
agg_lmfdb = []
for c in lmfdb:
    z = np.array(c['zeros'])
    if c['root_number'] == -1 and z[0] < 1e-6:
        z = z[1:]
    if z.size < 50: continue
    u = unfolded_spacings_lfunction(z, c['conductor'])
    agg_lmfdb.append(u - u.min())
# Stagger them so they don't overlap (each family member's events shift to
# be apart from the next).
offset = 0
shifted = []
for u in agg_lmfdb:
    shifted.append(u + offset)
    offset = u.max() + 100   # gap between curves
events_by_family['LMFDB ECs (Sp+U mix)'] = agg_lmfdb   # list of per-curve unfolded

# 4. Dirichlet (real, predicted Sp)
print("  loading Dirichlet …")
with open(os.path.join(DATA, "dirichlet_zeros.json")) as f:
    dirichlet = json.load(f)
agg_real = []
agg_cplx = []
for c in dirichlet:
    z = np.array(c['zeros'])
    if z.size < 50: continue
    u = unfolded_spacings_lfunction(z, c['conductor'])
    if u.size < 2: continue
    if c['is_real']: agg_real.append(u - u.min())
    else:            agg_cplx.append(u - u.min())

events_by_family['Dirichlet real (Sp)']     = agg_real      # list of per-curve unfolded
events_by_family['Dirichlet complex (U)']   = agg_cplx

# 5. Earthquakes (for null contrast in physical signal)
print("  loading earthquakes …")
import csv
with open(os.path.join(DATA, "usgs_M45_5yr.csv")) as f:
    reader = csv.reader(f)
    header = next(reader)
    i_t = header.index('time')
    from datetime import datetime
    eq_times = []
    for row in reader:
        try:
            t = datetime.fromisoformat(row[i_t].replace('Z', '+00:00')).timestamp()
            eq_times.append(t)
        except Exception:
            continue
eq_times = np.sort(np.array(eq_times))
mean_dt = np.diff(eq_times).mean()
events_by_family['Earthquakes M≥4.5 (5yr)'] = (eq_times - eq_times[0]) / mean_dt

# Print sizes — handle both single-array and list-of-arrays cases
print()
for k, v in events_by_family.items():
    if isinstance(v, list):
        total = sum(u.size for u in v)
        print(f"  {k:<32}: {len(v)} systems, {total} total events")
    else:
        print(f"  {k:<32}: n_events = {v.size}")
print()


# ─── Compute Σ²(L) and R₂(r) for each ────────────────────────────────────────
print("=" * 90)
print("Number variance Σ²(L)")
print("=" * 90)
print(f"  {'family':<32}  {'L=2':>5}  {'L=5':>5}  {'L=10':>5}  {'L=20':>5}  "
      f"vs Poisson(L)/GUE(L)")
sigma2_results = {}
L_vals_target = [2.0, 5.0, 10.0, 20.0]
for name, evt in events_by_family.items():
    if isinstance(evt, list):
        # Per-curve Σ²(L), then average across curves
        per_curve = []
        for u in evt:
            if u.size < 100: continue
            r = number_variance(u, L_max=25.0, n_L=20)
            per_curve.append(r['sigma2'])
        if not per_curve:
            print(f"  {name:<32}  insufficient")
            continue
        L = number_variance(evt[0], L_max=25.0, n_L=20)['L']
        s2_arr = np.array(per_curve)   # (n_curves, n_L)
        s2_mean = np.nanmean(s2_arr, axis=0)
        res = {'L': L, 'sigma2': s2_mean,
               'poisson': L,
               'goe':  (1/np.pi**2) * (np.log(np.maximum(2*np.pi*L, 1.0)) + 0.5772 + 1.0),
               'gue':  (2/np.pi**2) * (np.log(np.maximum(2*np.pi*L, 1.0)) + 0.5772 + 1.0 - np.pi**2/8)}
    elif evt.size < 200:
        print(f"  {name:<32}  insufficient")
        continue
    else:
        res = number_variance(evt, L_max=25.0, n_L=20)
    sigma2_results[name] = dict(L=res['L'].tolist(), sigma2=res['sigma2'].tolist(),
                                  poisson=res['poisson'].tolist(),
                                  goe=res['goe'].tolist(), gue=res['gue'].tolist())
    samples = []
    for L_t in L_vals_target:
        idx = int(np.argmin(np.abs(res['L'] - L_t)))
        s = res['sigma2'][idx]
        samples.append(f"{s:5.2f}" if not np.isnan(s) else "  nan")
    poisson_at = " ".join(f"{res['poisson'][int(np.argmin(np.abs(res['L']-L)))]:.1f}" for L in L_vals_target)
    gue_at = " ".join(f"{res['gue'][int(np.argmin(np.abs(res['L']-L)))]:.2f}" for L in L_vals_target)
    print(f"  {name:<32}  " + "  ".join(samples) + f"   (Poisson: {poisson_at}; GUE: {gue_at})")
print()


# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 7))
panels = list(events_by_family.keys())[:6]
for ax, name in zip(axes.flat, panels):
    if name not in sigma2_results:
        ax.set_title(f"{name}: insufficient", fontsize=8); continue
    r = sigma2_results[name]
    L = np.array(r['L'])
    s2 = np.array(r['sigma2'])
    poi = np.array(r['poisson'])
    gue = np.array(r['gue'])
    goe = np.array(r['goe'])
    ax.plot(L, s2, 'C0o-', lw=2, label='empirical', markersize=4)
    ax.plot(L, poi, 'g--', lw=1, label='Poisson (=L)')
    ax.plot(L, goe, 'C2-', lw=1, label='GOE')
    ax.plot(L, gue, 'r-',  lw=1.5, label='GUE')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('L'); ax.set_ylabel('Σ²(L)')
    ax.set_title(name, fontsize=8)
    ax.grid(True, alpha=0.3, which='both')
axes[0, 0].legend(fontsize=7, loc='lower right')
fig.suptitle("Number variance Σ²(L) — log-growth = Wigner / linear = Poisson")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOTS, "26_second_order.png"), dpi=110)
plt.close(fig)
print(f"  → plots/26_second_order.png")


with open(os.path.join(DATA, "second_order_results.json"), 'w') as f:
    json.dump({'sigma2_by_family': sigma2_results,
                'event_counts': {k: (sum(u.size for u in v) if isinstance(v, list) else int(v.size))
                                  for k, v in events_by_family.items()}},
                f, indent=2, default=str)
print(f"  → data/second_order_results.json")
