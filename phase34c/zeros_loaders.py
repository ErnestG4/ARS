"""
phase34c/zeros_loaders.py — loaders for the three spectral-coordinate
substrates: ζ zeros (Odlyzko), Dirichlet L-zeros, EC L-zeros.

ζ zeros are pure float arrays of γ values.  Dirichlet and EC L zeros
come with substrate metadata (character type, root number, rank,
conductor) used by the substrate-specific windowing per the
PHASE34C_BRIEF.md structural-null audit.

Cache paths
-----------
data/odlyzko_zeros1.txt        — first 10⁵ ζ zeros
data/odlyzko_zeros6.txt        — first 2·10⁶ ζ zeros (extends to γ ~ 10⁶)
data/dirichlet_zeros.json      — 630 primitive Dirichlet characters, 136k zeros
data/lmfdb_zeros.json          — 87 elliptic curves, 168k zeros
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
DATA_DIR = Path(ROOT_DIR) / 'data'

# ─── ζ zeros (Odlyzko) ───────────────────────────────────────────────────────

def load_zeta_zeros(file: str = 'odlyzko_zeros6.txt') -> np.ndarray:
    """Return float64 array of γ values (positive imaginary parts of the
    non-trivial Riemann zeros)."""
    path = DATA_DIR / file
    return np.loadtxt(path, dtype=np.float64)


def zeta_height_band(zeros: np.ndarray,
                       lo: float, hi: float) -> np.ndarray:
    """Return zeros γ ∈ [lo, hi)."""
    return zeros[(zeros >= lo) & (zeros < hi)]


# ─── Dirichlet L-zeros (project's §7.ter.3 cache) ────────────────────────────

def load_dirichlet() -> list[dict]:
    """Return the project's 630-character Dirichlet zero list (primitive
    non-principal characters, q ≤ 149).  Each entry has keys:
        q, order, is_real, conductor, chi, zeros, n_zeros, cpu_s.
    """
    with open(DATA_DIR / 'dirichlet_zeros.json') as f:
        return json.load(f)


def dirichlet_by_character_type(entries: list[dict],
                                  is_real: bool) -> list[dict]:
    """Filter Dirichlet entries by character type.

    is_real=True  → 92 real characters (Legendre-symbol-type),
                   symmetry class Sp(2N).
    is_real=False → 538 complex characters, symmetry class U(N).
    """
    return [e for e in entries if bool(e['is_real']) == bool(is_real)]


def dirichlet_pooled_zeros(entries: list[dict]) -> np.ndarray:
    """Concatenate raw γ values across all entries.  Pooling without
    per-character unfolding; analytic-conductor unfolding is applied
    by `unfolding.dirichlet_unfold` before downstream RF / p-adic
    analyses.
    """
    return np.sort(np.concatenate([np.asarray(e['zeros'])
                                     for e in entries]).astype(np.float64))


# ─── EC L-zeros (LMFDB) ──────────────────────────────────────────────────────

def load_ec_curves() -> list[dict]:
    """Return the project's 87-curve EC L-function zero list.  Each entry:
        label, klass, conductor, rank, ainvs, root_number, zeros, n_zeros.
    """
    with open(DATA_DIR / 'lmfdb_zeros.json') as f:
        return json.load(f)


def ec_by_root_number(entries: list[dict], root: int) -> list[dict]:
    """Filter EC L entries by root number ∈ {+1, −1}.

    +1 → SO(even) symmetry class (70 curves in the project cohort,
         mostly rank 0)
    −1 → SO(odd)  symmetry class (17 curves, mostly rank 1)
    """
    return [e for e in entries if int(e['root_number']) == int(root)]


def ec_pooled_zeros(entries: list[dict]) -> np.ndarray:
    """Concatenate raw γ values across curves.  Per-curve conductor
    unfolding is applied by `unfolding.ec_unfold` before downstream
    analyses.

    Filters γ ≤ 1e-6 (the analytic-rank zero at γ=0 for rank > 0
    curves, which would make log(γ) = −∞ in the unfolding).
    """
    arr = np.concatenate([np.asarray(e['zeros']) for e in entries]).astype(np.float64)
    arr = arr[arr > 1e-6]
    return np.sort(arr)


# ─── Sanity ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    zeta = load_zeta_zeros('odlyzko_zeros1.txt')
    print(f"ζ Odlyzko first 100K: {zeta.size} zeros, "
          f"γ range [{zeta.min():.2f}, {zeta.max():.2f}]")
    zeta_full = load_zeta_zeros('odlyzko_zeros6.txt')
    print(f"ζ Odlyzko full 2M: {zeta_full.size} zeros, "
          f"γ range [{zeta_full.min():.2f}, {zeta_full.max():.2f}]")

    d = load_dirichlet()
    real = dirichlet_by_character_type(d, is_real=True)
    comp = dirichlet_by_character_type(d, is_real=False)
    print(f"Dirichlet: real={len(real)} chars ({sum(x['n_zeros'] for x in real)} zeros), "
          f"complex={len(comp)} chars ({sum(x['n_zeros'] for x in comp)} zeros)")

    e = load_ec_curves()
    plus = ec_by_root_number(e, +1)
    minus = ec_by_root_number(e, -1)
    print(f"EC L: root+1={len(plus)} curves ({sum(x['n_zeros'] for x in plus)} zeros), "
          f"root-1={len(minus)} curves ({sum(x['n_zeros'] for x in minus)} zeros)")
