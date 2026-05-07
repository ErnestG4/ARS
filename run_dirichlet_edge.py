"""Katz-Sarnak edge test on Dirichlet L-functions.

Bulk pair-correlation gave the same Wigner GUE shape for both real and
complex characters (run_dirichlet_family.py).  Family symmetry shows up
at the edge.  For real Dirichlet characters (symplectic family Sp), the
prediction is:
    γ_1 distribution differs from unitary (complex characters).
    Specifically, Sp has a "central-zero" effect when the character is
    associated with a quadratic discriminant whose L-value at s=½ has
    specific behaviour.

This script runs the analogue of run_lmfdb_edge.py but on Dirichlet
characters: γ_1 raw, γ_1 normalised by analytic conductor scaling,
γ_2 - γ_1 first spacing.

Output:
    data/dirichlet_edge_results.json
    plots/25_dirichlet_edge.png
"""
import os, sys, json
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from universality import nns_poisson, nns_goe, nns_gue, _ks_pvalue

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")


def two_sample_ks(a, b):
    s1, s2 = np.sort(a), np.sort(b)
    n1, n2 = s1.size, s2.size
    if n1 < 5 or n2 < 5: return float('nan'), float('nan')
    pts = np.concatenate([s1, s2])
    cdf1 = np.searchsorted(s1, pts, side='right') / n1
    cdf2 = np.searchsorted(s2, pts, side='right') / n2
    ks = float(np.max(np.abs(cdf1 - cdf2)))
    p = _ks_pvalue(ks, int(n1 * n2 / (n1 + n2)))
    return ks, p


print("Loading dirichlet_zeros.json …")
with open(os.path.join(DATA, "dirichlet_zeros.json")) as f:
    chars = json.load(f)
print(f"  {len(chars)} characters")

# Strip central zero if present (some characters have functional-equation
# forced zero at γ=0 — happens for characters whose L-value at s=½ vanishes,
# rare but check anyway).
n_strip = 0
for c in chars:
    if c['zeros'] and c['zeros'][0] < 1e-6:
        c['zeros'] = c['zeros'][1:]
        c['n_zeros'] -= 1
        n_strip += 1
print(f"  central zero stripped from {n_strip} characters\n")

real_chars    = [c for c in chars if c['is_real']]
complex_chars = [c for c in chars if not c['is_real']]
print(f"  real chars (Sp predicted): {len(real_chars)}")
print(f"  complex chars (U predicted): {len(complex_chars)}\n")


# ─── γ_1 distributions ────────────────────────────────────────────────────────
print("=" * 90)
print("1.  Lowest zero γ_1 by character class")
print("=" * 90)
g1_real = np.array([c['zeros'][0] for c in real_chars if c['zeros']])
g1_cplx = np.array([c['zeros'][0] for c in complex_chars if c['zeros']])
print(f"  real    : γ_1 mean = {g1_real.mean():.3f},  median = {np.median(g1_real):.3f},  "
      f"std = {g1_real.std():.3f},  n = {g1_real.size}")
print(f"  complex : γ_1 mean = {g1_cplx.mean():.3f},  median = {np.median(g1_cplx):.3f},  "
      f"std = {g1_cplx.std():.3f},  n = {g1_cplx.size}")
ks_g1, p_g1 = two_sample_ks(g1_real, g1_cplx)
print(f"  two-sample KS(γ_1 raw):  KS = {ks_g1:.3f},  p = {p_g1:.3f}")
print()


# γ_1 normalised by log(q) / (2π)
def gamma1_norm(c):
    return c['zeros'][0] * np.log(c['conductor']) / (2 * np.pi) if c['zeros'] else None

g1n_real = np.array([gamma1_norm(c) for c in real_chars if gamma1_norm(c) is not None])
g1n_cplx = np.array([gamma1_norm(c) for c in complex_chars if gamma1_norm(c) is not None])
print(f"  γ_1 normalised by log(q)/(2π):")
print(f"  real    :  mean = {g1n_real.mean():.3f},  std = {g1n_real.std():.3f}")
print(f"  complex :  mean = {g1n_cplx.mean():.3f},  std = {g1n_cplx.std():.3f}")
ks_g1n, p_g1n = two_sample_ks(g1n_real, g1n_cplx)
print(f"  two-sample KS(γ_1 normalised):  KS = {ks_g1n:.3f},  p = {p_g1n:.3f}")
print()


# ─── First spacing γ_2 - γ_1 ──────────────────────────────────────────────────
print("=" * 90)
print("2.  First spacing γ_2 − γ_1, normalised by per-character mean spacing of first 50")
print("=" * 90)
def first_sp(c):
    z = c['zeros']
    if len(z) < 50: return None
    s12 = z[1] - z[0]
    mean_local = float(np.diff(z[:50]).mean())
    return s12 / mean_local

s12_real = np.array([first_sp(c) for c in real_chars if first_sp(c) is not None])
s12_cplx = np.array([first_sp(c) for c in complex_chars if first_sp(c) is not None])
print(f"  real    :  mean = {s12_real.mean():.3f},  std = {s12_real.std():.3f},  n = {s12_real.size}")
print(f"  complex :  mean = {s12_cplx.mean():.3f},  std = {s12_cplx.std():.3f},  n = {s12_cplx.size}")
ks12, p12 = two_sample_ks(s12_real, s12_cplx)
print(f"  two-sample KS:  {ks12:.3f}, p = {p12:.3f}")
print()


# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

# γ_1 raw
ax = axes[0]
bins = np.linspace(min(g1_real.min(), g1_cplx.min()),
                    max(g1_real.max(), g1_cplx.max()), 22)
ax.hist(g1_real, bins=bins, alpha=0.55, color='C0', density=True,
        label=f'real (Sp pred), n={g1_real.size}')
ax.hist(g1_cplx, bins=bins, alpha=0.55, color='C3', density=True,
        label=f'complex (U pred), n={g1_cplx.size}')
ax.set_title(f'γ_1 raw\nKS = {ks_g1:.3f}, p = {p_g1:.3f}', fontsize=10)
ax.set_xlabel('γ_1')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# γ_1 normalised
ax = axes[1]
bins = np.linspace(min(g1n_real.min(), g1n_cplx.min()),
                    max(g1n_real.max(), g1n_cplx.max()), 22)
ax.hist(g1n_real, bins=bins, alpha=0.55, color='C0', density=True,
        label='real (Sp)')
ax.hist(g1n_cplx, bins=bins, alpha=0.55, color='C3', density=True,
        label='complex (U)')
ax.set_title(f'γ_1 · log(q)/(2π)\nKS = {ks_g1n:.3f}, p = {p_g1n:.3f}', fontsize=10)
ax.set_xlabel('normalised γ_1')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# γ_2 - γ_1 spacing
ax = axes[2]
if s12_real.size > 5 and s12_cplx.size > 5:
    bins = np.linspace(min(s12_real.min(), s12_cplx.min()),
                        max(s12_real.max(), s12_cplx.max()), 22)
    ax.hist(s12_real, bins=bins, alpha=0.55, color='C0', density=True,
            label='real (Sp)')
    ax.hist(s12_cplx, bins=bins, alpha=0.55, color='C3', density=True,
            label='complex (U)')
ax.set_title(f'γ_2 - γ_1 (norm)\nKS = {ks12:.3f}, p = {p12:.3f}', fontsize=10)
ax.set_xlabel('normalised first spacing')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

fig.suptitle("Dirichlet L-function edge — Sp vs U Katz-Sarnak family signature")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOTS, "25_dirichlet_edge.png"), dpi=110)
plt.close(fig)
print(f"  → plots/25_dirichlet_edge.png")


# Save
out = dict(
    n_real=int(len(real_chars)),
    n_complex=int(len(complex_chars)),
    gamma1_raw=dict(
        real=dict(mean=float(g1_real.mean()), std=float(g1_real.std()), n=int(g1_real.size)),
        complex=dict(mean=float(g1_cplx.mean()), std=float(g1_cplx.std()), n=int(g1_cplx.size)),
        ks_two=float(ks_g1), p=float(p_g1),
    ),
    gamma1_normalised=dict(
        real=dict(mean=float(g1n_real.mean()), std=float(g1n_real.std())),
        complex=dict(mean=float(g1n_cplx.mean()), std=float(g1n_cplx.std())),
        ks_two=float(ks_g1n), p=float(p_g1n),
    ),
    first_spacing=dict(
        real=dict(mean=float(s12_real.mean()), std=float(s12_real.std()), n=int(s12_real.size)),
        complex=dict(mean=float(s12_cplx.mean()), std=float(s12_cplx.std()), n=int(s12_cplx.size)),
        ks_two=float(ks12), p=float(p12),
    ),
)
with open(os.path.join(DATA, "dirichlet_edge_results.json"), 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"  → data/dirichlet_edge_results.json")
