"""
phase34c/run_surveys.py — orchestrator for ζ + Dirichlet + EC L surveys.

Runs the per-substrate panels per the PHASE34C_BRIEF.md substrate-
specific windowing:

  ζ zeros:
    - low-height bulk (first 10⁴ zeros, heights up to ~10⁴)
    - mid-height window (zeros at heights 10⁵ → 1.1·10⁶)
  Dirichlet:
    - real-character pool (Sp class)
    - complex-character pool (U class)
  EC L:
    - root-number +1 stratum (SO(even))
    - root-number −1 stratum (SO(odd))
    - q_max=20 robustness panel on both strata

Each panel runs the consolidated survey_engine.run_panel pipeline:
stationarity → NNS → within-window stability → RF/p-adic vs Poisson
(wrong null) → RF/p-adic vs RMT (right null).

Output: data/phase34c_results/surveys.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from zeros_loaders import (load_zeta_zeros, load_dirichlet, load_ec_curves,
                             dirichlet_by_character_type, ec_by_root_number)
from unfolding import (zeta_unfold, dirichlet_unfold, ec_unfold,
                         pool_unfolded)
from survey_engine import run_panel, Q_MAX, Q_MAX_ROBUST

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34c_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def zeta_panels() -> list[tuple[str, np.ndarray, float]]:
    """Two ζ height windows per the substrate-specific windowing.

    Low-height bulk: first 10⁴ zeros (heights ~14 to ~7,500).
    Mid-height: zeros at indices [10⁵, 2·10⁵] (heights ~75,000 to
    ~150,000) — a tight log-decade window per the brief's [10^k,
    10^(k+1)] specification.  N=10⁵ events here, decimated to
    N_MAX_SURVEY=5K events in the RF surveys.
    """
    full = load_zeta_zeros('odlyzko_zeros6.txt')
    low_g = full[:10_000]
    mid_g = full[100_000:200_000]
    return [
        ('zeta-low-height-bulk', zeta_unfold(low_g), 2.0),
        ('zeta-mid-height-1e5-to-2e5', zeta_unfold(mid_g), 2.0),
    ]


def dirichlet_panels() -> list[tuple[str, np.ndarray, float]]:
    d = load_dirichlet()
    real = dirichlet_by_character_type(d, is_real=True)
    comp = dirichlet_by_character_type(d, is_real=False)
    real_unf = pool_unfolded([(e['conductor'], np.asarray(e['zeros']))
                                  for e in real], substrate='dirichlet')
    comp_unf = pool_unfolded([(e['conductor'], np.asarray(e['zeros']))
                                  for e in comp], substrate='dirichlet')
    return [
        ('dirichlet-real-Sp', real_unf, 4.0),
        ('dirichlet-complex-U', comp_unf, 2.0),
    ]


def ec_panels(q_max: int = Q_MAX) -> list[tuple[str, np.ndarray, float]]:
    e = load_ec_curves()
    plus = ec_by_root_number(e, +1)
    minus = ec_by_root_number(e, -1)
    plus_unf = pool_unfolded([(c['conductor'], np.asarray(c['zeros']))
                                 for c in plus], substrate='ec')
    minus_unf = pool_unfolded([(c['conductor'], np.asarray(c['zeros']))
                                  for c in minus], substrate='ec')
    suffix = f"_qmax{q_max}" if q_max != Q_MAX else ""
    return [
        (f'ec-root-plus-SO-even{suffix}', plus_unf, 1.0),
        (f'ec-root-minus-SO-odd{suffix}', minus_unf, 1.0),
    ]


def main() -> dict:
    print("=" * 72)
    print("Phase 34c Surveys — ζ + Dirichlet + EC L")
    print("=" * 72)
    out: dict = {'panels': {}}

    for label, unfolded, beta in zeta_panels():
        out['panels'][label] = run_panel(unfolded, label, beta_right=beta,
                                            q_max=Q_MAX)

    for label, unfolded, beta in dirichlet_panels():
        out['panels'][label] = run_panel(unfolded, label, beta_right=beta,
                                            q_max=Q_MAX)

    # EC L primary at q_max=30
    for label, unfolded, beta in ec_panels(q_max=Q_MAX):
        out['panels'][label] = run_panel(unfolded, label, beta_right=beta,
                                            q_max=Q_MAX)

    # EC L robustness at q_max=20
    for label, unfolded, beta in ec_panels(q_max=Q_MAX_ROBUST):
        out['panels'][label] = run_panel(unfolded, label, beta_right=beta,
                                            q_max=Q_MAX_ROBUST)

    out_path = OUT_DIR / 'surveys.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n→ {out_path}")
    return out


if __name__ == '__main__':
    main()
