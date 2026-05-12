"""
phase34c/run_prepilot.py — pre-pilot adequacy check per substrate.

Verifies that the right structural null (Dumitriu–Edelman β-tridiagonal
RMT surrogate, unfolded, bulk-only at 85% retention) reproduces the
substrate's bulk NNS-engine verdict on its own surrogates.  Per the
PHASE34C_BRIEF.md structural-null audit, failure of this check is a
*calibrator-zoo / sample-size diagnostic at the relevant N*, not a
substrate rejection.

Per (substrate × stratum):
  - sample one right-null surrogate at the substrate's matched N
  - feed unfolded eigenvalues through ars_classify.classify
  - expected verdict: TR (Wigner-class) at the appropriate β
  - if verdict drifts, the failure mode is named in the brief:
    calibrator-zoo extension or N adjustment, not "the substrate
    survey is invalid"

Output: data/phase34c_results/prepilot.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from rmt_sampler import sample_rmt_unfolded
from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34c_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Matched-N targets for the brief's primary panels.  Values are chosen
# to (a) overlap with the substrate panel size in the next sub-question,
# (b) fit comfortably in memory (N ≤ 10⁴ takes < 1 s per sample under
# Dumitriu–Edelman).
PANELS = [
    ('zeta-bulk',          2.0, 5000),
    ('zeta-mid-height',    2.0, 5000),
    ('dirichlet-real',     4.0, 2000),
    ('dirichlet-complex',  2.0, 5000),
    ('ec-root-plus',       1.0, 5000),
    ('ec-root-minus',      1.0, 2000),
]
N_SEEDS = 3   # cheap; want modal-verdict robustness


def main() -> dict:
    print("=" * 72)
    print("Phase 34c pre-pilot adequacy: RMT right-null self-classify")
    print("=" * 72)
    print(f"  Q_MAX={Q_MAX}, MIN_EVENTS_PER_Q={MIN_EVENTS_PER_Q}, "
          f"N_SEEDS={N_SEEDS}")
    out: dict = {'panels': []}
    for panel, beta, N in PANELS:
        print(f"\n[panel={panel}  β={beta}  N={N}]")
        primaries = []
        rep_meds = []
        ks_meds = []
        for s in range(N_SEEDS):
            rng = np.random.default_rng(s)
            t0 = time.perf_counter()
            unfolded = sample_rmt_unfolded(N, beta, rng=rng)
            unfolded = unfolded[~np.isnan(unfolded)]
            t1 = time.perf_counter()
            r = classify(unfolded, q_max=Q_MAX,
                          min_events_per_q=MIN_EVENTS_PER_Q,
                          return_full=False)
            t2 = time.perf_counter()
            primaries.append(r['primary'])
            rep_meds.append(r['rep_med'])
            ks_meds.append(r['ks_gue_med'])
            print(f"  seed={s}: sample={t1 - t0:.2f}s classify={t2 - t1:.2f}s "
                  f"→ primary={r['primary']}  rep_med={r['rep_med']:.3f}  "
                  f"ks_gue_med={r['ks_gue_med']:.3f}")
        from collections import Counter
        modal = Counter(primaries).most_common(1)[0][0]
        # Acceptance: modal should be 'TR' (Wigner-class).  GUE/Sp/SO bulk
        # at q_max=30 with sample size ≥ 2000 should classify as TR
        # robustly; if not, the calibrator zoo at this N has a gap.
        ok = (modal == 'TR')
        flag = '✓' if ok else '✗'
        print(f"  {flag}  modal primary across {N_SEEDS} seeds: {modal} "
              f"(expected TR Wigner-class)")
        out['panels'].append({
            'panel': panel, 'beta': float(beta), 'N': int(N),
            'primaries': primaries,
            'rep_meds': [float(x) for x in rep_meds],
            'ks_meds': [float(x) for x in ks_meds],
            'modal': modal,
            'accepted_as_wigner_TR': bool(ok),
        })

    n_pass = sum(1 for p in out['panels'] if p['accepted_as_wigner_TR'])
    n_tot = len(out['panels'])
    print(f"\nPre-pilot adequacy: {n_pass}/{n_tot} panels classify as Wigner TR.")
    if n_pass < n_tot:
        print("  Per brief: failure → calibrator-zoo / sample-size diagnostic, "
              "not substrate rejection.")
    out['n_pass'] = n_pass
    out['n_total'] = n_tot
    out_path = OUT_DIR / 'prepilot.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\n  → {out_path}")
    return out


if __name__ == '__main__':
    main()
