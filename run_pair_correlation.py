"""Pair correlation R₂(r) cross-family comparison.

Companion to run_second_order.py.  Uses the same per-family unfolded
event lists, computes R₂(r), and plots vs Wigner GUE / Poisson references.

R₂(r) is more sensitive than Σ²(L) to short-range correlations (the
characteristic GUE "level repulsion" dip near r → 0 is particularly
diagnostic).

Output:
    data/pair_correlation_results.json
    plots/27_pair_correlation.png
"""
import os, sys, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from universality import pair_correlation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")


def unfolded_zeta(zeros):
    z = np.asarray(zeros, dtype=np.float64)
    return (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8


def unfolded_lfunc(zeros, conductor):
    z = np.asarray(zeros, dtype=np.float64)
    z = z[z > 0]
    if z.size < 2: return np.zeros(0)
    arg = np.maximum(conductor * z / (2*np.pi), 1.0)
    return (z / (2*np.pi)) * (np.log(arg) - 1.0)


# Load
print("Loading data sources …")
zeros6 = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"))
families = {
    'ζ low (heights 14-75k)':     unfolded_zeta(zeros6[:100000]),
    'ζ high (heights ~1.1M)':     unfolded_zeta(zeros6[1900000:2000000]),
}

with open(os.path.join(DATA, "lmfdb_zeros.json")) as f:
    lmfdb = json.load(f)
families['LMFDB ECs'] = [unfolded_lfunc(np.array(c['zeros'])[1:] if c['root_number']==-1 and c['zeros'][0]<1e-6
                                          else np.array(c['zeros']),
                                          c['conductor']) for c in lmfdb if c['n_zeros'] >= 50]

with open(os.path.join(DATA, "dirichlet_zeros.json")) as f:
    dirichlet = json.load(f)
real_unf = []
cplx_unf = []
for c in dirichlet:
    z = np.array(c['zeros'])
    if z.size < 50: continue
    u = unfolded_lfunc(z, c['conductor'])
    if u.size < 2: continue
    if c['is_real']: real_unf.append(u)
    else:            cplx_unf.append(u)
families['Dirichlet real (Sp)']    = real_unf
families['Dirichlet complex (U)']  = cplx_unf

# Earthquakes
import csv
from datetime import datetime
with open(os.path.join(DATA, "usgs_M45_5yr.csv")) as f:
    reader = csv.reader(f)
    header = next(reader); i_t = header.index('time')
    eq_t = []
    for row in reader:
        try:
            eq_t.append(datetime.fromisoformat(row[i_t].replace('Z', '+00:00')).timestamp())
        except Exception:
            continue
eq_t = np.sort(np.array(eq_t))
mean_dt = float(np.diff(eq_t).mean())
families['Earthquakes M≥4.5'] = (eq_t - eq_t[0]) / mean_dt

print()
for k, v in families.items():
    if isinstance(v, list):
        print(f"  {k:<32}: {len(v)} systems, {sum(u.size for u in v)} total")
    else:
        print(f"  {k:<32}: {v.size} events")
print()


# Compute R₂(r) with reasonable r_max for short-range structure
print("=" * 80)
print("Pair correlation R₂(r)  (lower = more level repulsion; GUE has dip at r→0)")
print("=" * 80)
r_targets = [0.1, 0.3, 0.5, 1.0, 2.0]
results = {}
print(f"  {'family':<32}  {'r=0.1':>5}  {'r=0.3':>5}  {'r=0.5':>5}  {'r=1.0':>5}  {'r=2.0':>5}")
for name, evt in families.items():
    if isinstance(evt, list):
        # Per-system R₂(r), then average
        per_sys = []
        for u in evt:
            if u.size < 50: continue
            r = pair_correlation(u, r_max=4.0, n_bins=30)
            per_sys.append(r['R2'])
        if not per_sys:
            print(f"  {name:<32}  insufficient")
            continue
        R2 = np.nanmean(np.array(per_sys), axis=0)
        r_arr = pair_correlation(evt[0], r_max=4.0, n_bins=30)['r']
    else:
        if evt.size < 200:
            print(f"  {name:<32}  insufficient")
            continue
        r = pair_correlation(evt, r_max=4.0, n_bins=30)
        R2 = r['R2']; r_arr = r['r']

    # GUE reference: 1 - sinc²(πr)
    sinc = np.where(r_arr > 0, np.sin(np.pi*r_arr) / (np.pi*r_arr + 1e-12), 1.0)
    R2_gue = 1 - sinc**2
    results[name] = dict(r=r_arr.tolist(), R2=R2.tolist(), R2_gue=R2_gue.tolist())
    samples = []
    for rt in r_targets:
        idx = int(np.argmin(np.abs(r_arr - rt)))
        samples.append(f"{R2[idx]:5.3f}")
    print(f"  {name:<32}  " + "  ".join(samples))
print()
print("  Reference R₂_GUE: at r=0.1: 0.033, r=0.3: 0.27, r=0.5: 0.59, r=1.0: 1.00, r=2.0: 1.00")
print("  Reference R₂_Poisson:  flat 1.00 everywhere")
print()


# Plot
fig, axes = plt.subplots(2, 3, figsize=(13, 7))
panels = list(families.keys())[:6]
for ax, name in zip(axes.flat, panels):
    if name not in results:
        ax.set_title(f"{name}: insufficient", fontsize=8); continue
    r_arr = np.array(results[name]['r'])
    R2 = np.array(results[name]['R2'])
    R2_gue = np.array(results[name]['R2_gue'])
    ax.plot(r_arr, R2, 'C0o-', lw=1.5, label='empirical', markersize=4)
    ax.plot(r_arr, R2_gue, 'r-', lw=1.4, label='GUE: 1−sinc²(πr)')
    ax.axhline(1.0, color='g', ls='--', lw=1, label='Poisson')
    ax.set_xlim(0, 4); ax.set_ylim(-0.1, 1.4)
    ax.set_xlabel('r'); ax.set_ylabel('R₂(r)')
    ax.set_title(name, fontsize=9)
    ax.grid(True, alpha=0.3)
axes[0,0].legend(fontsize=7, loc='lower right')
fig.suptitle("Pair correlation R₂(r) — GUE has characteristic dip near r = 0")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOTS, "27_pair_correlation.png"), dpi=110)
plt.close(fig)
print(f"  → plots/27_pair_correlation.png")

with open(os.path.join(DATA, "pair_correlation_results.json"), 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"  → data/pair_correlation_results.json")
