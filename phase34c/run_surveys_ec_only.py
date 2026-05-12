"""
phase34c/run_surveys_ec_only.py — re-run only the EC L panels after
the γ=0 unfolding-fix in zeros_loaders.py / unfolding.py.

ζ and Dirichlet panels are not affected by the bug (no γ=0 entries
in their data); we keep their surveys.json results unchanged and
re-write only the ec-* keys.
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

from run_surveys import ec_panels
from survey_engine import run_panel, Q_MAX, Q_MAX_ROBUST

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34c_results'


def main() -> None:
    out_path = OUT_DIR / 'surveys.json'
    with open(out_path) as f:
        existing = json.load(f)

    # Remove old (NaN-contaminated) EC L panels
    new_panels = {k: v for k, v in existing.get('panels', {}).items()
                  if not k.startswith('ec-')}

    for label, unfolded, beta in ec_panels(q_max=Q_MAX):
        new_panels[label] = run_panel(unfolded, label, beta_right=beta,
                                        q_max=Q_MAX)

    for label, unfolded, beta in ec_panels(q_max=Q_MAX_ROBUST):
        new_panels[label] = run_panel(unfolded, label, beta_right=beta,
                                        q_max=Q_MAX_ROBUST)

    existing['panels'] = new_panels
    with open(out_path, 'w') as f:
        json.dump(existing, f, indent=2, default=str)
    print(f"\n→ {out_path} (EC L panels re-written)")


if __name__ == '__main__':
    main()
