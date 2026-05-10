"""
phase22a/h2_survival.py — H2 surrogate-survival verdicts.

For each (recording, surrogate, q_max), compare the real-data ARS
classification (h2_population_classifications) against the surrogate
distribution (h2_surrogate_classifications) at every q-band.

A q-band is recorded as "structure survives" when the real rep_int_q is
above the surrogate distribution's 95th percentile (i.e. the real value
is more repulsive than 19/20 surrogate replicates) AND the real
quadrant differs from the surrogate-modal quadrant at that q.  The
two-criterion conjunction protects against modal-flips driven by
surrogate noise alone.

Per the brief:
  - Cell-shuffle and the appropriate stimulus/state-drive surrogate
    are both required for H2 acceptance.
  - Survival need only happen at ≥ 1 order, on ≥ 1 of {spontaneous,
    evoked} subsets.

Outputs:
  data/phase22a_results/h2_survival_per_qband.parquet
  data/phase22a_results/h2_survival_summary.parquet
  Stdout: subset-level verdicts.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
REAL_PATH = OUT_DIR / 'h2_population_classifications.parquet'
SURR_PATH = OUT_DIR / 'h2_surrogate_classifications.parquet'

# Required-conjunction surrogate sets per subset (from the brief)
REQUIRED_SURROGATES = {
    'spontaneous':    {'cell_shuffle', 'state_modulated'},
    'gratings':       {'cell_shuffle'},   # no LN-evoked for static gratings
    'gratings_movie': {'cell_shuffle', 'ln_evoked'},
    'natural_movie':  {'cell_shuffle', 'ln_evoked'},
    'noise_movie':    {'cell_shuffle', 'ln_evoked'},
}

PCT_HI = 95.0
PCT_LO = 5.0


def _to_numpy(seq) -> np.ndarray:
    """Coerce a parquet list-column entry (list / np.ndarray / None) to
    a float ndarray."""
    if seq is None: return np.array([])
    arr = np.asarray(seq, dtype=object)
    return np.array([np.nan if v is None else float(v) for v in arr],
                     dtype=np.float64)


def survival_per_qband(real: pd.DataFrame, surr: pd.DataFrame) -> pd.DataFrame:
    """Per (recording, surrogate, q_max, q-band) survival flags."""
    out = []
    for q_max, real_q in real.groupby('q_max', sort=False):
        sub_surr = surr[surr['q_max'] == q_max]
        for _, real_row in real_q.iterrows():
            rec = real_row['recording']
            if 'rep_int_per_q' not in real_row:
                continue
            real_rep = _to_numpy(real_row.get('rep_int_per_q'))
            real_quad = real_row.get('quadrants_per_q')
            if real_quad is None: real_quad = []
            else: real_quad = list(real_quad)
            for surrogate_kind, sg in sub_surr[sub_surr['recording'] == rec].groupby('surrogate'):
                # Stack surrogate rep_int per q across seeds → (n_seeds, q_max)
                stacks = []
                quad_rows = []
                for _, sr in sg.iterrows():
                    s_rep = _to_numpy(sr.get('rep_int_per_q'))
                    stacks.append(s_rep)
                    sr_quad = sr.get('quadrants_per_q')
                    quad_rows.append(list(sr_quad) if sr_quad is not None else [])
                if not stacks: continue
                # Pad to same length
                Q = max(real_rep.size, max(s.size for s in stacks))
                def _pad(a, q):
                    out = np.full(q, np.nan)
                    out[:a.size] = a
                    return out
                real_pad = _pad(real_rep, Q)
                arr = np.stack([_pad(s, Q) for s in stacks])  # (n_seeds, Q)
                pct_hi = np.nanpercentile(arr, PCT_HI, axis=0)
                pct_lo = np.nanpercentile(arr, PCT_LO, axis=0)
                from collections import Counter
                quad_modal = []
                for qi in range(Q):
                    items = [row[qi] if qi < len(row) else None for row in quad_rows]
                    items = [x for x in items if x is not None]
                    if items:
                        quad_modal.append(Counter(items).most_common(1)[0][0])
                    else:
                        quad_modal.append(None)
                # Per-q-band flags
                for qi in range(Q):
                    real_q_quad = (real_quad[qi] if qi < len(real_quad) else None)
                    surv_rep = (not np.isnan(real_pad[qi])
                                 and not np.isnan(pct_hi[qi])
                                 and real_pad[qi] > pct_hi[qi])
                    quad_diff = (real_q_quad is not None
                                  and quad_modal[qi] is not None
                                  and real_q_quad != quad_modal[qi])
                    out.append(dict(
                        recording=rec, q_max=int(q_max), surrogate=surrogate_kind,
                        q=qi + 1,
                        real_rep_int=float(real_pad[qi]),
                        surr_rep_int_p95=float(pct_hi[qi]),
                        surr_rep_int_p5=float(pct_lo[qi]),
                        real_quadrant=real_q_quad,
                        surr_modal_quadrant=quad_modal[qi],
                        survives_rep=bool(surv_rep),
                        survives_quad=bool(quad_diff),
                        survives_both=bool(surv_rep and quad_diff),
                    ))
    return pd.DataFrame(out)


def survival_summary(per_q: pd.DataFrame, real: pd.DataFrame) -> pd.DataFrame:
    """Roll up per-q survival into per (recording, surrogate, q_max)
    counts and a final per-recording verdict (does the required
    conjunction of surrogates pass at ≥ 1 q-band?)."""
    if per_q.empty: return pd.DataFrame()
    rows = []
    for (rec, q_max), g in per_q.groupby(['recording', 'q_max'], sort=False):
        rec_subset = real[(real['recording'] == rec) &
                            (real['q_max'] == q_max)]['subset'].iloc[0]
        per_sur = {}
        for sur_kind, sg in g.groupby('surrogate'):
            n_total = int(len(sg))
            n_rep = int(sg['survives_rep'].sum())
            n_quad = int(sg['survives_quad'].sum())
            n_both = int(sg['survives_both'].sum())
            per_sur[sur_kind] = dict(n_total=n_total, n_rep=n_rep,
                                      n_quad=n_quad, n_both=n_both)
            rows.append(dict(
                recording=rec, subset=rec_subset, q_max=q_max,
                surrogate=sur_kind,
                n_q_total=n_total, n_q_rep_survives=n_rep,
                n_q_quad_diff=n_quad, n_q_both=n_both,
                survives_at_any_q=(n_both > 0),
            ))
        # Required-conjunction verdict
        req = REQUIRED_SURROGATES.get(rec_subset, set())
        passes = []
        for r in req:
            if r in per_sur and per_sur[r]['n_both'] > 0:
                passes.append(r)
        rows.append(dict(
            recording=rec, subset=rec_subset, q_max=q_max,
            surrogate='REQUIRED_CONJUNCTION',
            n_q_total=int(g.shape[0]),
            n_q_rep_survives=int(g['survives_rep'].sum()),
            n_q_quad_diff=int(g['survives_quad'].sum()),
            n_q_both=len(passes),
            survives_at_any_q=(set(passes) >= req and req != set()),
        ))
    return pd.DataFrame(rows)


def main():
    print("=" * 72)
    print("Phase 22a H2 — surrogate-survival verdicts")
    print("=" * 72)
    real = pd.read_parquet(REAL_PATH)
    surr = pd.read_parquet(SURR_PATH)
    print(f"  real rows: {len(real)}, surrogate rows: {len(surr)}")

    per_q = survival_per_qband(real, surr)
    summary = survival_summary(per_q, real)

    per_q.to_parquet(OUT_DIR / 'h2_survival_per_qband.parquet', index=False)
    summary.to_parquet(OUT_DIR / 'h2_survival_summary.parquet', index=False)
    print(f"  → {OUT_DIR}/h2_survival_per_qband.parquet  ({len(per_q)} rows)")
    print(f"  → {OUT_DIR}/h2_survival_summary.parquet  ({len(summary)} rows)")

    print()
    print("Verdict by recording & q_max:")
    pivot = summary[summary['surrogate'] == 'REQUIRED_CONJUNCTION'].copy()
    if len(pivot):
        for _, r in pivot.iterrows():
            flag = "✓" if r['survives_at_any_q'] else "·"
            print(f"  {flag}  {r['recording']:32s}  subset={r['subset']:18s}  "
                  f"q_max={int(r['q_max']):3d}  passes={int(r['n_q_both'])}/required")

    print()
    print("Per-subset H2 verdict (≥ 1 recording w/ required conjunction passing):")
    for subset in ['spontaneous', 'gratings', 'gratings_movie',
                   'natural_movie', 'noise_movie']:
        sub = pivot[pivot['subset'] == subset]
        if not len(sub): continue
        any_pass = bool(sub['survives_at_any_q'].any())
        n_pass = int(sub['survives_at_any_q'].sum())
        print(f"  {subset:18s}  {n_pass}/{len(sub)} (recording, q_max) pass  →  "
              f"H2 {'PASS' if any_pass else 'NULL'}")


if __name__ == '__main__':
    main()
