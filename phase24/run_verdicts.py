"""
phase24/run_verdicts.py — Phase 24 Full verdict + findings doc generator.

Reads all phase24 result parquets and writes:
  - data/phase24_results/PHASE24_FULL_FINDINGS.md
  - Phase 22a findings update note
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase24_results'
FINDINGS = OUT_DIR / 'PHASE24_FULL_FINDINGS.md'

PVC11_REF = {
    ('osi', 'ks_gue_med'): +0.720,
    ('osi', 'rep_med'): -0.324,
    ('dsi', 'ks_gue_med'): +0.223,
    ('dsi', 'rep_med'): -0.060,
    ('f1_f0_pref', 'rep_med'): +0.388,
    ('f1_f0_pref', 'ks_gue_med'): -0.093,
}


def _safe(p):
    return pd.read_parquet(p) if p.exists() else None


def main():
    cv = _safe(OUT_DIR / 'per_session_h1_crossval.parquet')
    overall = _safe(OUT_DIR / 'h1_meta_overall.parquet')
    by_cre = _safe(OUT_DIR / 'h1_meta_by_cre.parquet')
    by_rate = _safe(OUT_DIR / 'h1_meta_by_rate_quartile.parquet')
    h2_pop = _safe(OUT_DIR / 'per_session_h2_population.parquet')
    h2_surv = _safe(OUT_DIR / 'per_session_h2_survival.parquet')
    rate_matched = _safe(OUT_DIR / 'rate_matched_configs.parquet')

    L = []
    p = L.append

    p("# Phase 24 (Full) Findings — multi-session Allen Visual Coding awake-mouse-V1 replication")
    p("")
    p("Multi-session replication of Phase 22a's H1 + H2 findings on the")
    p("Allen Brain Observatory Visual Coding Neuropixels brain_observatory_1.1")
    p("session set, picking up where the Phase 24 triage left off.")
    p("")

    if cv is not None:
        p(f"## Sessions analysed")
        p("")
        n_sess = cv['session_id'].nunique()
        cre_counts = cv.drop_duplicates('session_id')['cre_line'].value_counts()
        p(f"  - Total sessions: **{n_sess}**")
        p(f"  - Cre line distribution: {dict(cre_counts)}")
        p("")

    # ─── H1 verdict ──
    if overall is not None and len(overall):
        p("## H1 — multi-session OSI ↔ ks_gue_med headline")
        p("")
        p("Per-session Spearman partial correlations of {ks_gue_med, rep_med}")
        p("vs {OSI, DSI, F1/F0} controlling for mean firing rate, then")
        p("Fisher-Z meta-analysis (fixed and random effect).")
        p("")
        p("| descriptor | ARS metric | n_sess | meta-fixed ρ | meta-random ρ | I² | pvc-11 ref | sign |")
        p("|---|---|---|---|---|---|---|---|")
        for _, r in overall.iterrows():
            key = (r['descriptor'], r['ars_metric'])
            pvc = PVC11_REF.get(key, float('nan'))
            sign_match = ('match' if (r['fixed_rho'] * pvc) > 0
                            else 'flip' if (r['fixed_rho'] * pvc) < 0 else '~0')
            p(f"| {r['descriptor']} | {r['ars_metric']} | {int(r['n_studies'])} | "
              f"{r['fixed_rho']:+.3f} | {r['random_rho']:+.3f} | {r['I2']:.0f}% | "
              f"{pvc:+.3f} | {sign_match} |")
        p("")
        # H1 verdict logic
        head = overall[(overall['descriptor'] == 'osi')
                         & (overall['ars_metric'] == 'ks_gue_med')]
        if len(head):
            r = head.iloc[0]
            pvc = PVC11_REF[('osi', 'ks_gue_med')]
            if (r['fixed_rho'] > 0
                  and abs(r['fixed_rho']) >= 0.5 * abs(pvc)
                  and r['n_studies'] >= 6):
                p("**H1 verdict: LOCKED** — meta-fixed OSI ↔ ks_gue_med "
                  "across all sessions is positive at substantive magnitude "
                  "(Allen meta-fix ρ above 50% of pvc-11). Cross-species "
                  "cross-state replication of the H1 headline.")
            elif r['fixed_rho'] > 0 and r['n_studies'] >= 4:
                p("**H1 verdict: MODIFIED** — meta-fixed positive but "
                  "attenuated or heterogeneous; flag as substrate-modulated.")
            else:
                p("**H1 verdict: NOT REPLICATED** at fixed-effect across "
                  "sessions.")
        p("")

    # DSI replication check
    if overall is not None:
        dsi = overall[(overall['descriptor'] == 'dsi')
                        & (overall['ars_metric'] == 'ks_gue_med')]
        if len(dsi):
            r = dsi.iloc[0]
            pvc = PVC11_REF[('dsi', 'ks_gue_med')]
            p("## DSI status")
            p("")
            verdict = ('REPLICATED — Allen meta-fix exceeds pvc-11 reference; '
                         'add as cross-validated finding.'
                         if r['fixed_rho'] > pvc and r['fixed_rho'] > 0.30
                         else 'REPLICATED-with-attenuation' if r['fixed_rho'] > 0
                         else 'NOT REPLICATED')
            p(f"**DSI ↔ ks_gue_med:** Allen meta-fix ρ = {r['fixed_rho']:+.3f} "
              f"(pvc-11 ref +0.223). **{verdict}**")
            p("")

    # F1/F0 sign-flip status
    if by_cre is not None:
        f1f0 = overall[(overall['descriptor'] == 'f1_f0_pref')
                         & (overall['ars_metric'] == 'rep_med')]
        if len(f1f0):
            r = f1f0.iloc[0]
            f1f0_cre = by_cre[(by_cre['descriptor'] == 'f1_f0_pref')
                                  & (by_cre['ars_metric'] == 'rep_med')]
            p("## F1/F0 sign-flip status")
            p("")
            p(f"Overall meta-fix F1/F0 ↔ rep_med = {r['fixed_rho']:+.3f}")
            p(f"(triage was −0.222; pvc-11 ref +0.388).")
            p(f"")
            p(f"Per-Cre-line breakdown:")
            p("")
            p("| Cre line | n_sess | meta-fix ρ | random ρ | I² |")
            p("|---|---|---|---|---|")
            for _, cr in f1f0_cre.iterrows():
                p(f"| {cr['cre_line']} | {int(cr['n_sessions'])} | "
                  f"{cr['fixed_rho']:+.3f} | {cr['random_rho']:+.3f} | "
                  f"{cr['I2']:.0f}% |")
            p("")
            # Verdict logic
            signs = f1f0_cre['fixed_rho'].values
            if r['fixed_rho'] < -0.1 and (signs < 0).all():
                p("**F1/F0 verdict: SUBSTRATE-SYSTEMATIC** — opposite-sign "
                  "to pvc-11 across all Cre lines and overall meta. "
                  "Substantive substrate difference: mouse and macaque V1 "
                  "have opposite F1/F0 ↔ rep_med relationships.")
            elif abs(r['fixed_rho']) < 0.1:
                p("**F1/F0 verdict: SESSION-NOISE** — overall meta near zero.")
            elif (signs < 0).any() and (signs > 0).any():
                p("**F1/F0 verdict: CRE-LINE-SPECIFIC** — sign varies across "
                  "Cre lines.")
            else:
                p("**F1/F0 verdict: AMBIGUOUS** — needs further investigation.")
            p("")

    # Rate-quartile breakdown
    if by_rate is not None:
        p("## H1 by per-session firing-rate quartile")
        p("")
        head = by_rate[(by_rate['descriptor'] == 'osi')
                         & (by_rate['ars_metric'] == 'ks_gue_med')]
        if len(head):
            p("OSI ↔ ks_gue_med per per-session-firing-rate quartile:")
            p("")
            p("| quartile | n_sess | meta-fix ρ | random ρ | I² |")
            p("|---|---|---|---|---|")
            for _, r in head.iterrows():
                p(f"| {r['rate_quartile']} | {int(r['n_sessions'])} | "
                  f"{r['fixed_rho']:+.3f} | {r['random_rho']:+.3f} | "
                  f"{r['I2']:.0f}% |")
            p("")

    # H2 verdict
    if h2_surv is not None and len(h2_surv):
        p("## H2 — multi-session population-event verdict")
        p("")
        p("Per-session H2 surrogate-survival verdicts at default (k=5, w=5ms)")
        p("and rate-matched (per-session k, w) configurations.  Required-")
        p("conjunction means ALL surrogates for that session pass strict")
        p("survival at ≥ 1 q-band.")
        p("")
        for cfg in ('default', 'rate_matched'):
            p(f"### {cfg} config")
            p("")
            p("| condition | sessions | PASS (all surrogates) |")
            p("|---|---|---|")
            sub = h2_surv[h2_surv['config'] == cfg]
            for cond in ('natural_movie_one', 'drifting_pooled', 'spontaneous'):
                ssub = sub[sub['condition'] == cond]
                if not len(ssub): continue
                per_sess = ssub.groupby('session_id')['survives_at_any_q'].all()
                n_pass = int(per_sess.sum())
                n_total = len(per_sess)
                p(f"| {cond} | {n_total} | **{n_pass} / {n_total}** |")
            p("")
        # H2 verdict logic
        nmo_def = h2_surv[(h2_surv['config'] == 'default')
                              & (h2_surv['condition'] == 'natural_movie_one')]
        nmo_rm = h2_surv[(h2_surv['config'] == 'rate_matched')
                              & (h2_surv['condition'] == 'natural_movie_one')]
        if len(nmo_def) and len(nmo_rm):
            n_def_pass = int(nmo_def.groupby('session_id')['survives_at_any_q'].all().sum())
            n_def_total = nmo_def['session_id'].nunique()
            n_rm_pass = int(nmo_rm.groupby('session_id')['survives_at_any_q'].all().sum())
            n_rm_total = nmo_rm['session_id'].nunique()
            p(f"**H2 natural_movie_one: default {n_def_pass}/{n_def_total} PASS, "
              f"rate-matched {n_rm_pass}/{n_rm_total} PASS.**")
            p("")
            if n_rm_pass >= n_rm_total / 2 and n_def_pass < n_def_total / 2:
                p("**H2 verdict: SUBSTRATE-RATE-REGIME-CONFIRMED.**  Triage "
                  "hypothesis confirmed: pvc-11 (k=5, w=5ms) defaults probe "
                  "Allen at the wrong event-rate regime.  At the rate-matched "
                  "interface configuration, the H2 finding holds across "
                  "Allen mouse V1.  The Phase 22a H2 claim is substrate-"
                  "general at appropriately-configured interfaces.")
            elif n_rm_pass < n_rm_total / 2:
                p("**H2 verdict: PVC-11-SPECIFIC.**  Even at rate-matched "
                  "configurations, Allen H2 NULL across most sessions.  The "
                  "Phase 22a H2 finding is bounded to anesthetised macaque V1 "
                  "or some specific stimulus-substrate combination.")
            else:
                p("**H2 verdict: MIXED.**  Heterogeneous across sessions; "
                  "not cleanly substrate-general or substrate-specific.")
            p("")

    out = FINDINGS
    out.write_text('\n'.join(L))
    print(f"  → {out}  ({len(L)} lines)")


if __name__ == '__main__':
    main()
