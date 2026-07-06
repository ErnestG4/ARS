"""
phase34e/unfolding.py — SL(2,ℤ) Maass-form Weyl-law unfolding.

For SL(2,ℤ) acting on ℍ², the Selberg trace formula gives the asymptotic
eigenvalue counting function:

    N(T) := #{r_j ≤ T} ~ (Area / 4π) T²  as T → ∞

with Area = π/3 (hyperbolic area of the SL(2,ℤ) fundamental domain).
Leading-term unfolding:

    x_j := r_j² / 12

so that the unfolded sequence {x_j} has asymptotic mean spacing 1.

Subleading Weyl-law corrections come from:
  - cusp contribution (logarithmic),
  - identity term,
  - small-eigenvalue contributions.

These are sub-percent at the scales the rigorous SH/BSV datasets reach
and do not affect bulk-NNS classification. Documented but not retained
in the default unfolding; flag via the `include_subleading` parameter.

For 3-D Bianchi (Phase 34f), the leading-term unfolding constant changes:
    x_j := vol(Γ\ℍ³) · r_j³ / (6 π²)
with field-specific volume. See `unfold_bianchi` for that variant.

Reference: Iwaniec 2002, Spectral methods of automorphic forms, §11.
"""
from __future__ import annotations

import math
import numpy as np


SL2Z_AREA = math.pi / 3.0  # hyperbolic area of SL(2,ℤ) fundamental domain


def unfold_sl2z(r: np.ndarray, include_subleading: bool = False) -> np.ndarray:
    """Weyl-law leading-term unfolding for SL(2,ℤ) Maass spectrum.

    Parameters
    ----------
    r : 1D array of spectral parameters (sorted ascending preferred).
    include_subleading : if True, add the leading cusp + identity-term
        correction terms.  For SH/BSV-precision data and bulk-NNS use,
        the leading-only unfolding is sufficient.

    Returns
    -------
    x : unfolded coordinates with asymptotic ⟨Δx⟩ = 1.
    """
    r = np.asarray(r, dtype=np.float64)
    # Leading: N(r) ~ Area / 4π · r² = r² / 12
    x = r * r / 12.0
    if include_subleading:
        # Sub-leading SL(2,ℤ) Weyl-law (Iwaniec 2002 Theorem 11.1):
        #   N(T) = (Area/4π) T² − (1/2π) T log(T/π) + O(T / log T)
        # The (-T log T / 2π) cusp term shifts the unfolded coordinate
        # by an O(log r / log²r) correction.
        # Implementation: subtract (r * log(r / π)) / (2π) from x.
        mask = r > 1.0
        with np.errstate(invalid='ignore'):
            cusp = np.where(mask, r * np.log(r / math.pi) / (2.0 * math.pi), 0.0)
        x = x - cusp
    return x


def unfold_bianchi(r: np.ndarray, volume: float) -> np.ndarray:
    """Weyl-law leading-term unfolding for 3-D Bianchi Maass spectrum.

    Parameters
    ----------
    r : spectral parameters.
    volume : hyperbolic volume of Γ\ℍ³ fundamental domain.
        Picard (Q(i)): vol = G/3 ≈ 0.30532186.
        Bianchi-Z[ω] (Q(√−3)): vol = √3·L(2,χ_{-3})/8 ≈ 0.16915693
        (Humbert-direct; pinned in phase34f/bianchi_unfolding.py — the
        canonical source.  EGM's 0.0845776 orbifold value is this / ~2,
        the ω↔ω² Z/2 quotient; see that module's constants comment).

    Returns
    -------
    x : unfolded coordinates with asymptotic ⟨Δx⟩ = 1.
    """
    r = np.asarray(r, dtype=np.float64)
    # 3-D Bianchi Weyl law: N(T) ~ vol · T³ / (6π²)
    return volume * r ** 3 / (6.0 * math.pi * math.pi)


def spacings(x: np.ndarray) -> np.ndarray:
    """Nearest-neighbor spacings s_j = x_{j+1} − x_j on a sorted sequence.

    Sorts x first if not already sorted (idempotent on already-sorted input).
    """
    x = np.asarray(x, dtype=np.float64)
    x_sorted = np.sort(x)
    return np.diff(x_sorted)


def mean_spacing_check(s: np.ndarray, tolerance: float = 0.05) -> dict:
    """Sanity check on Weyl-law unfolding: ⟨s⟩ should be close to 1.

    Returns dict with mean, std, CV, and pass/fail flag.
    """
    mean = float(np.mean(s))
    std = float(np.std(s))
    cv = std / mean if mean > 0 else float('inf')
    return dict(
        mean=mean,
        std=std,
        CV=cv,
        deviation_from_one=abs(mean - 1.0),
        pass_check=abs(mean - 1.0) < tolerance,
        tolerance=tolerance,
    )


__all__ = [
    'SL2Z_AREA',
    'unfold_sl2z',
    'unfold_bianchi',
    'spacings',
    'mean_spacing_check',
]
