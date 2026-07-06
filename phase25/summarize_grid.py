"""
phase25/summarize_grid.py — pretty-print summary tables from the
Phase 25 fit-quality and survival outputs.  Generates the markdown
tables that go into PHASE25_FINDINGS.md.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase25_results'

N_LAGS_GRID = [1, 4, 8]
BIN_MS_GRID = [5.0, 10.0, 20.0, 40.0]
VARIANTS = ['canonical', 'unconstrained']


def fit_quality_table() -> str:
    """Render the fit-quality grid as a markdown table.

    Columns: n_lags, bin_ms, variant, verdict, dev_med,
             units_pass / total, sur/real spike ratio.
    Plus extras pulled from per-cell fit parquets: hist_l2_med,
    hist_min_med, hist_max_med, stim_l2_med.
    """
    g_path = OUT_DIR / 'fit_quality_grid.parquet'
    if not g_path.exists():
        return "(fit_quality_grid.parquet not present — run stage=fit first)"
    g = pd.read_parquet(g_path)

    rows = []
    for _, r in g.iterrows():
        tag = f"nlags{int(r['n_lags'])}__bin{int(r['bin_ms'])}ms__{r['variant']}"
        fp = OUT_DIR / f"fits__{tag}.parquet"
        if fp.exists():
            df = pd.read_parquet(fp)
            hist_l2 = df['history_kernel_l2'].median()
            hist_min = df['history_kernel_min'].median()
            hist_max = df['history_kernel_max'].median()
            stim_l2 = df['stim_kernel_l2'].median()
        else:
            hist_l2 = hist_min = hist_max = stim_l2 = float('nan')
        rows.append(dict(
            n_lags=int(r['n_lags']), bin_ms=int(r['bin_ms']),
            variant=r['variant'], verdict=r['verdict'],
            dev_med=float(r['dev_med']),
            units_pass=f"{int(r['n_units_pass'])}/{int(r['n_units_total'])}",
            sur_real=float(r['sur_total_spikes']) / max(int(r['real_total_spikes']), 1),
            hist_l2_med=float(hist_l2), hist_min_med=float(hist_min),
            hist_max_med=float(hist_max), stim_l2_med=float(stim_l2),
        ))

    g2 = pd.DataFrame(rows).sort_values(['variant', 'bin_ms', 'n_lags'])
    lines = []
    lines.append("| n_lags | bin (ms) | variant | verdict | dev_med | units_pass | sur/real | hist_l2 | hist_min | hist_max | stim_l2 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in g2.iterrows():
        lines.append(
            f"| {r['n_lags']} | {r['bin_ms']} | {r['variant']} | "
            f"{r['verdict']} | {r['dev_med']:+.4f} | {r['units_pass']} | "
            f"{r['sur_real']:.2f} | {r['hist_l2_med']:.3f} | "
            f"{r['hist_min_med']:+.3f} | {r['hist_max_med']:+.3f} | "
            f"{r['stim_l2_med']:.3f} |"
        )
    return "\n".join(lines)


def survival_table() -> str:
    """Render the survival outcomes for cells that PASSed fit-quality."""
    g_path = OUT_DIR / 'fit_quality_grid.parquet'
    if not g_path.exists():
        return "(no survival data — stage 2 not run)"
    g = pd.read_parquet(g_path)
    pass_cells = g[g['verdict'] == 'FIT-PROPER']
    if not len(pass_cells):
        return "(no cells were FIT-PROPER — H_PassD verdict: FIT-CEILING)"

    rows = []
    for _, r in pass_cells.iterrows():
        tag = f"nlags{int(r['n_lags'])}__bin{int(r['bin_ms'])}ms__{r['variant']}"
        sp = OUT_DIR / f"survival__{tag}.parquet"
        if not sp.exists():
            rows.append(dict(n_lags=int(r['n_lags']), bin_ms=int(r['bin_ms']),
                              variant=r['variant'],
                              survives_rep="(no data)",
                              survives_quad="-", survives_both="-",
                              verdict="(stage 2 not run)"))
            continue
        sdf = pd.read_parquet(sp)
        n_q = len(sdf)
        n_rep = int(sdf['survives_rep'].sum())
        n_quad = int(sdf['survives_quad'].sum())
        n_both = int(sdf['survives_both'].sum())
        if n_both >= 1:
            verdict = "EXTEND (strict)"
        elif n_rep >= 1:
            verdict = "EXTEND (rep only)"
        else:
            verdict = "CHARACTERIZE-AND-CLOSE"
        rows.append(dict(n_lags=int(r['n_lags']), bin_ms=int(r['bin_ms']),
                          variant=r['variant'],
                          survives_rep=f"{n_rep}/{n_q}",
                          survives_quad=f"{n_quad}/{n_q}",
                          survives_both=f"{n_both}/{n_q}",
                          verdict=verdict))

    lines = []
    lines.append("| n_lags | bin (ms) | variant | rep>p95 | quad-diff | both-strict | verdict |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| {r['n_lags']} | {r['bin_ms']} | {r['variant']} | "
            f"{r['survives_rep']} | {r['survives_quad']} | "
            f"{r['survives_both']} | {r['verdict']} |"
        )
    return "\n".join(lines)


def aggregate_verdict() -> dict:
    """Compute the Phase 25 H_PassD primary verdict and stim-mis-routing
    secondary verdict.
    """
    g_path = OUT_DIR / 'fit_quality_grid.parquet'
    if not g_path.exists():
        return dict(primary='UNKNOWN', secondary='UNKNOWN',
                      reason='fit_quality_grid.parquet absent')
    g = pd.read_parquet(g_path)
    pass_cells = g[g['verdict'] == 'FIT-PROPER']

    # Primary: H_PassD verdict.
    if not len(pass_cells):
        primary = 'FIT-CEILING'
        primary_detail = ("no (n_lags, bin_ms, variant) cell was "
                            "FIT-PROPER; coupled-GLM surrogates cannot "
                            "be fit faithfully on this data with the "
                            "methodologies tested")
    else:
        extend_strict = False
        extend_rep_only = False
        char_close = False
        details = []
        for _, r in pass_cells.iterrows():
            tag = f"nlags{int(r['n_lags'])}__bin{int(r['bin_ms'])}ms__{r['variant']}"
            sp = OUT_DIR / f"survival__{tag}.parquet"
            if not sp.exists():
                continue
            sdf = pd.read_parquet(sp)
            n_both = int(sdf['survives_both'].sum())
            n_rep = int(sdf['survives_rep'].sum())
            if n_both >= 1:
                extend_strict = True
                details.append(f"{tag}: EXTEND-strict ({n_both}/30 both)")
            elif n_rep >= 1:
                extend_rep_only = True
                details.append(f"{tag}: EXTEND-rep ({n_rep}/30 rep)")
            else:
                char_close = True
                details.append(f"{tag}: CHARACTERIZE-AND-CLOSE")
        if extend_strict:
            primary = 'EXTEND'
        elif extend_rep_only:
            primary = 'EXTEND-SOFT'
        elif char_close:
            primary = 'CHARACTERIZE-AND-CLOSE'
        else:
            primary = 'FIT-CEILING'
        primary_detail = "; ".join(details)

    # Secondary: stim-mis-routing diagnostic.  CONFIRMED if multi-frame
    # STA collapses unconstrained runaway at any n_lags > 1 cell (i.e.,
    # unconstrained verdict transitions from DEGENERATE-RUNAWAY at
    # n_lags=1 to non-runaway at n_lags>1 at the same bin_ms).
    secondary = 'UNDETERMINED'
    sec_detail = []
    for bw in BIN_MS_GRID:
        cells_bw = g[(g['bin_ms'] == bw) & (g['variant'] == 'unconstrained')]
        verdicts_by_nlags = {int(r['n_lags']): r['verdict']
                              for _, r in cells_bw.iterrows()}
        v1 = verdicts_by_nlags.get(1, '?')
        v4 = verdicts_by_nlags.get(4, '?')
        v8 = verdicts_by_nlags.get(8, '?')
        sec_detail.append(
            f"bin={int(bw)}ms unconstrained: nlags1={v1}, nlags4={v4}, nlags8={v8}"
        )
    runaway_at_nlags1 = any(
        g[(g['n_lags'] == 1) & (g['variant'] == 'unconstrained')]['verdict']
        == 'FIT-PATHOLOGICAL-BY-CONSTRAINT')
    runaway_at_nlags8 = any(
        g[(g['n_lags'] == 8) & (g['variant'] == 'unconstrained')]['verdict']
        == 'FIT-PATHOLOGICAL-BY-CONSTRAINT')
    if runaway_at_nlags1 and not runaway_at_nlags8:
        secondary = 'CONFIRMED'
    elif runaway_at_nlags1 and runaway_at_nlags8:
        secondary = 'FALSIFIED'

    return dict(primary=primary, primary_detail=primary_detail,
                  secondary=secondary, secondary_detail=sec_detail)


def main():
    print("=== Fit-quality grid ===\n")
    print(fit_quality_table())
    print("\n=== Survival (PASS cells) ===\n")
    print(survival_table())
    print("\n=== Aggregate verdicts ===\n")
    verdict = aggregate_verdict()
    print(json.dumps(verdict, indent=2))
    # Persist:
    with open(OUT_DIR / 'aggregate_verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)


if __name__ == '__main__':
    main()
