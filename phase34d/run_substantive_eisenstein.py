"""
phase34d/run_substantive_eisenstein.py — Phase 34d-E substantive run.

Mirrors run_prepilot_ars.py but on Eisenstein prime angles (Z[ω],
fundamental sector [0, π/3)). Per Phase 34d brief §C deep-layer
two-layer cross-phase, this is the first-measurement against the
implicit Rudnick-Waxman analog for Q(ω) (no published dedicated paper
per LIT_SUMMARY.md §6).

The substantive question: does the Eisenstein angle substrate
- land NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_HECKE (matches Gaussian
  surface layer)?
- show CONSTANT_LEVEL_DIVERGENT from Gaussian (different prefactor,
  same min-shape: confirmatory of structural analog)?
- show FUNCTIONAL_FORM_DIVERGENT from Gaussian (different scaling
  exponent or curve shape: substantively novel)?

Gates from Phase 34d-G must pass before this is interpreted.

Outputs
-------
data/phase34d_results/eisenstein_substantive_ars.json
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
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34c'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34a'))

from eisenstein_primes import eisenstein_prime_angles
from run_prepilot_ars import run_panel

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34d_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    n_seeds = 200

    panels = {}

    print("Generating Eisenstein prime angles at X = 10⁶ ...")
    eis_angles = eisenstein_prime_angles(1_000_000, both_factors=True)
    panels['eisenstein_X1e6'] = run_panel('eisenstein_X1e6', eis_angles,
                                          sector_length=np.pi / 3,
                                          n_seeds=n_seeds)

    out_path = OUT_DIR / 'eisenstein_substantive_ars.json'
    with open(out_path, 'w') as f:
        json.dump({
            'phase': '34d-E',
            'step': 'substantive run / ARS readout on Eisenstein angles',
            'panels': panels,
        }, f, indent=2)
    print(f"\n→ wrote Eisenstein substantive results to {out_path}")


if __name__ == '__main__':
    main()
