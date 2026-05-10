"""
phase23/run_phase23_writeup.py — orchestrator that synthesises the
Phase 23 findings + comparison-vs-Phase-21 document from parquet
outputs.  Writes:

  data/phase23_results/PHASE23_FINDINGS.md
  data/phase23_results/PHASE23_VS_PHASE21.md
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


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase23_results'
PHASE21_DIR = Path(ROOT_DIR) / 'data'
FINDINGS = OUT_DIR / 'PHASE23_FINDINGS.md'
COMPARISON = OUT_DIR / 'PHASE23_VS_PHASE21.md'

QPO_WINDOW_S = (45.0, 47.0)
TARGET_QPO_HZ = 909.0


def load_safe(p: Path) -> pd.DataFrame | None:
    return pd.read_parquet(p) if p.exists() else None


def main():
    real_traj = load_safe(OUT_DIR / 'phase23_targeted_classification.parquet')
    surr_traj = load_safe(OUT_DIR / 'phase23_targeted_surrogate_classification.parquet')
    qpo_cmp = load_safe(OUT_DIR / 'phase23_targeted_qpo_comparison.parquet')
    p21_qpo = load_safe(PHASE21_DIR / 'phase21_qpo_comparison.parquet')

    lines = []
    p = lines.append

    p("# Phase 23 Findings — targeted 909 Hz QPO replication on GRB 230307A")
    p("")
    p("Time-slice adjustment from GRB_NEXT_STEPS.md applied:")
    p("  - sub-window: 100 ms (down from 2.0 s in Phase 21 Tier 3)")
    p("  - q_max: 50 (up from 30 in Phase 21 Tier 3)")
    p("  - analysis window: [-5, +60] s post-trigger")
    p("  - target QPO: 909 Hz (Chen et al. 2025), claim window 45–47 s")
    p("")

    if real_traj is not None and surr_traj is not None:
        n_real_total = len(real_traj)
        n_real_well = int((real_traj['primary'] != 'underpowered').sum())
        n_surr_seeds = surr_traj['label'].nunique()
        n_surr_per_seed = len(surr_traj) // max(n_surr_seeds, 1)
        p(f"## Trajectory size")
        p("")
        p(f"- real sub-windows: {n_real_total} total, {n_real_well} well-powered")
        p(f"- surrogate seeds: {n_surr_seeds}, sub-windows per seed: ~{n_surr_per_seed}")
        p("")

    if qpo_cmp is not None and len(qpo_cmp):
        real = qpo_cmp[qpo_cmp['label'] == 'real']
        surr = qpo_cmp[qpo_cmp['label'].str.startswith('surr_')]
        real_in = real[real['in_qpo_window']]
        real_out = real[~real['in_qpo_window']]
        surr_in = surr[surr['in_qpo_window']]
        surr_out = surr[~surr['in_qpo_window']]

        p("## Sub-window counts at the 909 Hz q-band (well-powered, q in [2, q_max])")
        p("")
        p("| condition                    | sub-windows |")
        p("|------------------------------|-------------|")
        p(f"| real, inside QPO window      | {len(real_in)} |")
        p(f"| real, outside QPO window     | {len(real_out)} |")
        p(f"| surrogate, inside QPO window | {len(surr_in)} |")
        p(f"| surrogate, outside QPO window | {len(surr_out)} |")
        p("")

        p("## Per-condition signature at the 909 Hz q-band")
        p("")
        p("| condition       | n   | median rep_int_at_qpo_q | median rf_amp_at_qpo_q | quadrants |")
        p("|-----------------|-----|------------------------|------------------------|-----------|")

        def _row(label, df):
            if not len(df):
                return f"| {label} | 0 | – | – | – |"
            return (f"| {label} | {len(df)} | "
                    f"{df['rep_int_at_qpo_q'].median():.3f} | "
                    f"{df['rf_amp_at_qpo_q'].median():.4f} | "
                    f"{dict(df['quadrant_at_qpo_q'].value_counts())} |")

        p(_row('real, inside ', real_in))
        p(_row('real, outside', real_out))
        p(_row('surr, inside ', surr_in))
        p(_row('surr, outside', surr_out))
        p("")

        # Verdict
        if len(real_in) and len(surr_in):
            real_med_in = float(real_in['rep_int_at_qpo_q'].median())
            real_med_out = (float(real_out['rep_int_at_qpo_q'].median())
                              if len(real_out) else float('nan'))
            surr_med_in = float(surr_in['rep_int_at_qpo_q'].median())
            surr_med_out = (float(surr_out['rep_int_at_qpo_q'].median())
                              if len(surr_out) else float('nan'))
            real_delta = real_med_in - real_med_out
            surr_delta = surr_med_in - surr_med_out
            p("## Verdict")
            p("")
            p(f"- real    inside − outside delta: {real_delta:+.3f}")
            p(f"- surr    inside − outside delta: {surr_delta:+.3f}")
            p("")
            if abs(real_delta) > 0.05 and abs(real_delta - surr_delta) > 0.05:
                if real_delta > surr_delta:
                    p("**PASS** — real shows a larger inside-vs-outside delta")
                    p("at the 909 Hz q-band than the lightcurve-modulated")
                    p("Poisson surrogate.  Signature beyond the rate envelope.")
                else:
                    p("**PASS-INVERTED** — real shows a smaller delta than")
                    p("surrogate; structure is suppressed in the QPO claim")
                    p("window relative to the lightcurve baseline.")
            elif abs(real_delta) > 0.05:
                p("**SOFT PASS** — real shows an inside-vs-outside delta")
                p("at the 909 Hz q-band but the lightcurve-modulated Poisson")
                p("surrogate reproduces it.  The signature is fully accounted")
                p("for by the empirical rate envelope; no QPO claim survives.")
            else:
                p("**FAIL (substantive)** — real shows no meaningful")
                p("inside-vs-outside delta at the 909 Hz q-band.  The")
                p("time-slice adjustment is methodologically applied but the")
                p("targeted Chen 2025 909 Hz QPO claim does not register in")
                p("the framework's classification at any q-band coverage")
                p("we can reach with this dataset.")
            p("")

    p("## Time-slice-adjustment effect on the underlying constraint")
    p("")
    p("Phase 21 GRB_NEXT_STEPS identified two intertwined limits:")
    p("  - q_max=30 left published QPO frequencies just outside the")
    p("    framework's q-coverage (q_target ~31 for 909 Hz at typical")
    p("    prompt-window event rates).")
    p("  - 2.0 s sub-windows captured at most 1 sub-window inside the")
    p("    2 s Chen 2025 claim window — no temporal trajectory inside.")
    p("")
    p("Phase 23 fixes both: q_max=50 gives ~2.5× margin (q_target ~19.5")
    p("at 17 K events/s in the QPO window) and 100 ms sub-windows give")
    p("20 sub-windows inside the 2 s claim window.  The framework's")
    p("classification can now in principle register a transient at")
    p("909 Hz timescale; whether one is actually present is the verdict")
    p("above.")
    p("")

    out = FINDINGS
    out.write_text('\n'.join(lines))
    print(f"  → {out}  ({len(lines)} lines)")

    # ─── comparison vs Phase 21 ──
    cmp_lines = []
    pp = cmp_lines.append
    pp("# Phase 23 vs Phase 21 — comparison")
    pp("")
    pp("## What Phase 21 found (per GRB_NEXT_STEPS.md)")
    pp("")
    pp("- Quadrant classification did not shift during published QPO windows on")
    pp("  any of the four events. All four classified uniformly as BL throughout")
    pp("  prompt and surrounding windows.")
    pp("- Lightcurve-modulated Poisson surrogate reproduced the empirical")
    pp("  classification on every event (12/12 reproductions across 3 seeds × 4")
    pp("  events).")
    pp("- MGF positive control was partial: 836 Hz mode in GRB 200415A produced")
    pp("  an elevated RF-amplitude at q=74 (predicted q=70.5) on a full-prompt-")
    pp("  window scan at q_max=300; higher-frequency modes did not.")
    pp("- Identified blocking issue: q_max=30 + 2.0 s sub-windows left the")
    pp("  909 Hz published claim for GRB 230307A just outside the framework's")
    pp("  q-coverage with no temporal-trajectory resolution inside the 2 s claim")
    pp("  window.")
    pp("")
    pp("## What Phase 23 changed")
    pp("")
    pp("- Sub-window: **2.0 s → 100 ms** (20× finer)")
    pp("- q_max:      **30 → 50** (~2.5× margin on q_target for 909 Hz)")
    pp("- Analysis target: **GRB 230307A specifically**, in [-5, +60] s window")
    pp("- Surrogate floor unchanged: lightcurve-modulated Poisson, 5 seeds")
    pp("  (up from 3 in Phase 21)")
    pp("")
    if qpo_cmp is not None and len(qpo_cmp):
        real = qpo_cmp[qpo_cmp['label'] == 'real']
        surr = qpo_cmp[qpo_cmp['label'].str.startswith('surr_')]
        real_in = real[real['in_qpo_window']]
        surr_in = surr[surr['in_qpo_window']]
        pp("## What Phase 23 finds")
        pp("")
        if len(real_in):
            real_med_in = float(real_in['rep_int_at_qpo_q'].median())
            surr_med_in = float(surr_in['rep_int_at_qpo_q'].median()) if len(surr_in) else float('nan')
            pp(f"- {len(real_in)} sub-windows inside the 45–47 s QPO claim window are")
            pp(f"  well-powered and have q_target in [2, 50].")
            pp(f"- median rep_int_q at the 909 Hz q-band, real:    {real_med_in:.3f}")
            pp(f"- median rep_int_q at the 909 Hz q-band, surr:    {surr_med_in:.3f}")
        pp("")
    pp("## Comparison logic")
    pp("")
    pp("Phase 21 was blocked at the q-resolution / sub-window-resolution wall.")
    pp("Phase 23 lifts both limits.  The verdict in PHASE23_FINDINGS.md")
    pp("therefore tells us:")
    pp("")
    pp("  - **PASS:** the time-slice adjustment was the operative blocker.  ARS")
    pp("    classifies the QPO window distinctly from the lightcurve baseline at")
    pp("    the 909 Hz q-band when the resolution is matched to the claim.  This")
    pp("    is a positive ARS-replicates-published-QPO finding.")
    pp("  - **SOFT PASS:** the time-slice adjustment surfaces a real inside-vs-")
    pp("    outside delta in the data, but the lightcurve-modulated Poisson")
    pp("    surrogate reproduces it.  The deltas are rate-envelope-driven, not")
    pp("    QPO-driven.  Phase 21's lightcurve-floor null still wins; the time-")
    pp("    slice adjustment changes nothing for the QPO claim.")
    pp("  - **FAIL:** the time-slice adjustment applies cleanly but the framework")
    pp("    detects no signature at the published 909 Hz q-band.  The")
    pp("    methodological ceiling identified in Phase 21 was not the operative")
    pp("    blocker; ARS at any reachable q/sub-window resolution does not")
    pp("    register the published claim on this event.  Either (a) ARS is the")
    pp("    wrong instrument for this signal, or (b) the published claim is not")
    pp("    a real signal.  Phase 23 itself doesn't discriminate between these.")
    pp("")
    cmp_out = COMPARISON
    cmp_out.write_text('\n'.join(cmp_lines))
    print(f"  → {cmp_out}  ({len(cmp_lines)} lines)")


if __name__ == '__main__':
    main()
