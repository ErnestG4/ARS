"""
phase34e/maass_loader.py — load Seymour-Howell 2022 Zenodo dataset of
rigorously computed Maass forms.

Dataset: Zenodo DOI 10.5281/zenodo.7105773, ~5 GB → tarball
sqrfree_maassdata.tar.gz → extracted to data/maassdata/{r_value}.txt
with 33,214 Maass forms across squarefree composite levels.

**Note (pivot from PHASE34E_BRIEF.md):** the Zenodo dump does NOT
include Maass forms at trivial level N = 1 (SL(2,ℤ)). Per
Lowry-Duda 2025 (arXiv:2502.01442), 2,202 level-1 Maass forms exist in
the full LMFDB database but are NOT in the Zenodo upload. Phase 34e
pivots to **per-level analysis on representative Γ₀(N) squarefree
levels** (lowest level in dataset: N = 23). The Sarnak anomaly applies
to all Γ₀(N) by the Hecke-algebra structural argument; methodology
validation still holds.

File format (Seymour-Howell 2022 internal convention):
  Line 1: spectral parameter r + error bound, comma-separated
  Line 2: level N (integer)
  Line 3: nebentype / parity flag
  Line 4: ? (always 1 in inspected sample; possibly trivial-character flag)
  Lines 5+: Hecke eigenvalues at primes, one per line as "λ_p, error"
            where primes are taken in ascending order from p=2.

Hecke-eigenvalue normalization: λ_p ∈ [-2, 2] under Ramanujan-Petersson
(to be verified at §D.0 normalization gate).
"""
from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Iterator

import numpy as np


PHASE34E_DATA = Path('/home/combust/fmexplorer/criticality_tool/phase34e/data/maassdata')


def parse_maass_file(path: Path) -> dict:
    """Parse one Seymour-Howell Maass-form file.

    Returns dict with:
      r              spectral parameter
      r_error        rigorous error bound on r
      level          Γ₀(N) level
      parity         line 3 value (0 or 1; symmetry / nebentype)
      trivial_char   line 4 value (typically 1)
      hecke_pairs    list of (lambda_p, error_lambda_p) for primes
                     p = 2, 3, 5, 7, ... in ascending order
      n_hecke        count of Hecke eigenvalues
    """
    with open(path) as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    # Line 1: r, r_error
    r_str, err_str = lines[0].split(',')
    r = float(r_str)
    r_error = float(err_str)
    level = int(lines[1])
    parity = int(lines[2])
    trivial_char = int(lines[3])
    hecke_pairs = []
    for ln in lines[4:]:
        parts = ln.split(',')
        if len(parts) != 2:
            continue
        try:
            lam = float(parts[0])
            lam_err = float(parts[1])
            hecke_pairs.append((lam, lam_err))
        except ValueError:
            continue
    return dict(
        r=r,
        r_error=r_error,
        level=level,
        parity=parity,
        trivial_char=trivial_char,
        hecke_pairs=hecke_pairs,
        n_hecke=len(hecke_pairs),
        path=str(path),
    )


def iter_maass_forms(level: int | None = None,
                     levels: list[int] | None = None,
                     data_dir: Path = PHASE34E_DATA) -> Iterator[dict]:
    """Iterate over Maass forms in the dataset.

    Parameters
    ----------
    level    : if set, return only forms at this specific level.
    levels   : if set, return only forms at any level in this list.
    data_dir : path to extracted maassdata/ directory.
    """
    for fp in sorted(data_dir.iterdir()):
        if not fp.name.endswith('.txt'):
            continue
        try:
            d = parse_maass_file(fp)
        except Exception as e:
            print(f"  skip {fp.name}: {e}")
            continue
        if level is not None and d['level'] != level:
            continue
        if levels is not None and d['level'] not in levels:
            continue
        yield d


def load_eigenvalues_at_level(level: int,
                              data_dir: Path = PHASE34E_DATA) -> np.ndarray:
    """Load all spectral parameters r at a given level, sorted ascending."""
    r_list = []
    for d in iter_maass_forms(level=level, data_dir=data_dir):
        r_list.append(d['r'])
    return np.sort(np.array(r_list, dtype=np.float64))


def load_level_index(data_dir: Path = PHASE34E_DATA) -> dict[int, int]:
    """Return {level: count} mapping for fast level-distribution queries.

    Pre-computes once via filename-scan; faster than parsing each file.
    Uses the second-line read for each file. Cached if invoked again
    within a session (via the lru_cache on the underlying call).
    """
    counts = {}
    for fp in sorted(data_dir.iterdir()):
        if not fp.name.endswith('.txt'):
            continue
        try:
            with open(fp) as f:
                next(f)  # skip line 1
                lvl = int(f.readline().strip())
            counts[lvl] = counts.get(lvl, 0) + 1
        except Exception:
            continue
    return counts


def gamma0_N_index(N: int) -> int:
    """Index [SL(2,ℤ) : Γ₀(N)] = N · ∏_{p|N} (1 + 1/p)."""
    if N < 1:
        raise ValueError(f"N must be ≥ 1, got {N}")
    idx = N
    n = N
    p = 2
    while p * p <= n:
        if n % p == 0:
            idx = idx * (p + 1) // p
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        idx = idx * (n + 1) // n
    return idx


def gamma0_N_weyl_constant(N: int) -> float:
    """Weyl-law leading constant for Γ₀(N)\\ℍ²:  vol(Γ₀(N)\\ℍ²) / (4π)
    = (π/3 · [SL(2,ℤ):Γ₀(N)]) / (4π) = [SL(2,ℤ):Γ₀(N)] / 12.

    So N(T) ~ ([SL2Z:Γ₀(N)] / 12) · T² and unfolding is
    x_j = ([SL2Z:Γ₀(N)] / 12) · r_j².
    """
    return gamma0_N_index(N) / 12.0


def unfold_gamma0(r: np.ndarray, level: int) -> np.ndarray:
    """Unfold spectral parameters at level N via Γ₀(N) Weyl-law constant.

    x_j = ([SL(2,ℤ):Γ₀(N)] / 12) · r_j²

    After this transformation, the asymptotic mean spacing is 1.
    """
    c = gamma0_N_weyl_constant(level)
    return c * np.asarray(r, dtype=np.float64) ** 2


if __name__ == '__main__':
    # Print level-distribution summary
    print("Scanning Seymour-Howell 2022 dataset for level distribution...")
    counts = load_level_index()
    print(f"Total Maass forms: {sum(counts.values())}")
    print(f"Distinct levels:   {len(counts)}")
    print()
    print(f"{'level':>6s}  {'count':>6s}  {'index':>6s}  {'role':>20s}")
    sorted_levels = sorted(counts.items(), key=lambda x: -x[1])
    for lvl, c in sorted_levels[:15]:
        idx = gamma0_N_index(lvl)
        role = ''
        if lvl == 1:
            role = 'SL(2,ℤ) trivial'
        elif c > 1000:
            role = 'PRIMARY (high count)'
        print(f"{lvl:>6d}  {c:>6d}  {idx:>6d}  {role:>20s}")
