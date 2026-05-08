"""
Phase 16A.2 — State-occupancy extractor verification.

Apply the three new state-based attention extractors plus the four
Phase 16A controls to a Qwen 2.5 3B fp16 forward pass on the natural
stimulus.  Verdict map:

  A — all 3 new state extractors → TR → upgrade §7.ter.22 state-vs-change
      framing to confirmed finding
  B — 1-2 produce TR, 1-2 produce other → state-based readings are
      heterogeneous; document variation
  C — 0 of 3 produce TR → original attention_sink_events TR was
      threshold-extraction-induced; collapse the state/change distinction

Output:
  data/phase16a2_state_matrix.parquet
  plots/46_phase16a2_state_extractors.png
"""
import os, sys, json, time, gc
import numpy as np
import pandas as pd

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from llm_cascade import extract_cascade, NATURAL_TEXT
from llm_extractors import LLM_EXTRACTORS, extract_llm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
MODEL = "Qwen/Qwen2.5-3B"
MAX_SEQ_LEN = 1024
Q_MAX = 50
MIN_EVENTS = 30


# Same per-extractor calibration as Phase 16A, plus defaults for new ones.
EXTRACTOR_KWARGS = {
    'attention_sink_events':                 dict(k=0.3, window=20),
    'layer_kl_divergence_events':            dict(k=0.3, window=20),
    'attention_target_jumps':                dict(delta_tokens=8),
    # New state-based extractors keep their defaults (calibrated via tests):
    'attention_argmax_sink':                 dict(n_sink=4),
    'attention_sink_residency_runs':         dict(n_sink=4, theta=0.3,
                                                   min_run_length=3),
    'attention_multi_head_sink_consensus':   dict(n_sink=4, consensus_frac=0.5),
}

# Order: change-based controls first, then state-based extractors
EXTRACTOR_ORDER = [
    # Phase 16A change-based controls
    ('residual_norm_peaks',                  'change'),
    ('attention_entropy_peaks',              'change'),
    ('attention_target_jumps',               'change'),
    ('layer_kl_divergence_events',           'change'),
    # Phase 16A state-based (original threshold-style)
    ('attention_sink_events',                'state_threshold'),
    # NEW state-based extractors
    ('attention_argmax_sink',                'state_categorical'),
    ('attention_sink_residency_runs',        'state_run'),
    ('attention_multi_head_sink_consensus',  'state_consensus'),
]


def main():
    t_start = time.time()
    print(f"Loading {MODEL} fp16 + natural stimulus, max_seq_len={MAX_SEQ_LEN}…")
    t0 = time.time()
    cascade = extract_cascade(NATURAL_TEXT, model_name=MODEL,
                                max_seq_len=MAX_SEQ_LEN,
                                compute_attention=True,
                                keep_attention=True)
    print(f"  seq_len={cascade['seq_len']}  "
          f"attentions: {len(cascade.get('attentions', []))} layers  "
          f"⏱ {time.time() - t0:.1f}s\n")

    rows = []
    print("=" * 110)
    print(f"Phase 16A.2 — state-occupancy extractor verification at q_max={Q_MAX}")
    print("=" * 110)
    print(f"  {'extractor':<38}  {'family':<18}  {'n_events':>5}  "
          f"{'primary':<14}  {'rep_int':>7}  {'KS_GUE':>7}")
    print("  " + "-" * 105)

    for ext_name, family in EXTRACTOR_ORDER:
        kw = EXTRACTOR_KWARGS.get(ext_name, {})
        try:
            t_k = extract_llm(cascade, ext_name, **kw)
        except Exception as e:
            print(f"  {ext_name:<38}  {family:<18}  EXTRACT FAILED: {e}")
            continue
        if t_k is None or t_k.size < 30:
            print(f"  {ext_name:<38}  {family:<18}  "
                  f"{t_k.size if t_k is not None else 0:>5}  insufficient")
            rows.append(dict(extractor=ext_name, family=family,
                              n_events=int(t_k.size if t_k is not None else 0),
                              primary='underpowered'))
            continue
        df = joint_q_profile(t_k, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
        df = joint_quadrant_diagnostic(df)
        well = df[~df['underpowered']]
        if len(well) == 0:
            primary = 'underpowered'; rep_med = ks_med = np.nan
            br_a = br_n = tl = tr = bl = np.nan; primary_pct = 0.0
        else:
            vc = well['quadrant'].value_counts(normalize=True)
            primary = vc.idxmax()
            primary_pct = float(vc.max())
            rep_med = float(well['rep_int_q'].median())
            ks_med = float(well['ks_gue_q'].median())
            br_a = float(vc.get('BR_artifact', 0.0))
            br_n = float(vc.get('BR_novel', 0.0))
            tl = float(vc.get('TL', 0.0))
            tr = float(vc.get('TR', 0.0))
            bl = float(vc.get('BL', 0.0))
        rows.append(dict(extractor=ext_name, family=family,
                          n_events=int(t_k.size),
                          primary=primary, primary_pct=primary_pct,
                          rep_int_med=rep_med, ks_gue_med=ks_med,
                          br_a_pct=br_a, br_n_pct=br_n,
                          tl_pct=tl, tr_pct=tr, bl_pct=bl))
        print(f"  {ext_name:<38}  {family:<18}  {t_k.size:>5}  {primary:<14}  "
              f"{rep_med:>7.3f}  {ks_med:>7.3f}")

    df_pool = pd.DataFrame(rows)
    df_pool.to_parquet(os.path.join(DATA, "phase16a2_state_matrix.parquet"))
    print(f"\n  → data/phase16a2_state_matrix.parquet")

    # ─── Verdict ────────────────────────────────────────────────────────────
    print("\n" + "=" * 110)
    print("VERDICT — three new state-based extractors")
    print("=" * 110)
    new_ext = ['attention_argmax_sink', 'attention_sink_residency_runs',
                'attention_multi_head_sink_consensus']
    new_results = df_pool[df_pool['extractor'].isin(new_ext)]
    n_tr = (new_results['primary'] == 'TR').sum()
    n_other = ((new_results['primary'] != 'TR') &
                (new_results['primary'] != 'underpowered')).sum()
    n_uncalibrated = (new_results['primary'] == 'underpowered').sum()

    # Compare each new extractor's rep_int and KS_GUE to the original
    # attention_sink_events benchmark
    orig_row = df_pool[df_pool['extractor'] == 'attention_sink_events']
    if len(orig_row):
        orig_rep = float(orig_row['rep_int_med'].iloc[0])
        orig_ks  = float(orig_row['ks_gue_med'].iloc[0])
        print(f"  Original attention_sink_events benchmark: "
              f"primary={orig_row['primary'].iloc[0]}, rep_int={orig_rep:.3f}, KS_GUE={orig_ks:.3f}")
        print(f"\n  New state-based extractors:")
        for _, r in new_results.iterrows():
            agree_rep = abs(r['rep_int_med'] - orig_rep) < 0.10 if pd.notna(r['rep_int_med']) else False
            agree_ks = abs(r['ks_gue_med'] - orig_ks) < 0.10 if pd.notna(r['ks_gue_med']) else False
            print(f"    {r['extractor']:<38}  primary={r['primary']:<14}  "
                  f"rep_int={r['rep_int_med']:.3f}  KS_GUE={r['ks_gue_med']:.3f}  "
                  f"(Δrep={'✓' if agree_rep else '✗'}, ΔKS={'✓' if agree_ks else '✗'})")

    print(f"\n  Of {len(new_ext)} new state-based extractors:")
    print(f"    → TR:           {n_tr}")
    print(f"    → other:        {n_other}")
    print(f"    → underpowered: {n_uncalibrated}")
    print()
    if n_tr == 3:
        print("  ✓ VERDICT A — Principled state-based finding.")
        print("    All three new state-based extractors classify the LLM as TR.")
        print("    State-based attention dynamics meets the ≥4-distinct-mechanism")
        print("    principled criterion.  §7.ter.22 state-vs-change framing")
        print("    upgraded to confirmed finding.")
        verdict = 'A'
    elif n_tr >= 1 and n_other >= 1:
        print("  ⚠ VERDICT B — Provisional remains provisional.")
        print(f"    {n_tr} new state-based extractor(s) give TR; {n_other} give other.")
        print("    State-based attention dynamics has structurally heterogeneous")
        print("    readings depending on which state-property is extracted.")
        print("    Document the variation; do not claim a single class for state-based.")
        verdict = 'B'
    elif n_tr == 0 and n_other > 0:
        print("  ✗ VERDICT C — Original attention_sink_events TR was extractor artifact.")
        print(f"    0 of {len(new_ext)} new extractors produce TR.")
        print("    The threshold-style attention_sink_events reading was likely")
        print("    the threshold-extraction-induced artifact identified in Phase 16")
        print("    Tier 1.  State-vs-change framing in §7.ter.22 collapses;")
        print("    LLM result reduces to 'all attention extractors → BR_artifact.'")
        verdict = 'C'
    else:
        print("  ! UNCALIBRATED — too many new extractors underpowered for verdict.")
        verdict = 'uncalibrated'

    # ─── Plot ───────────────────────────────────────────────────────────────
    valid = df_pool.dropna(subset=['primary']).copy()
    if len(valid) > 0:
        # Stacked bar of quadrant occupancy fractions per extractor
        cols = ['bl_pct', 'tr_pct', 'tl_pct', 'br_a_pct', 'br_n_pct']
        col_labels = ['BL', 'TR', 'TL', 'BR_artifact', 'BR_novel']
        colors = ['#7d7d7d', '#1f77b4', '#ff7f0e', '#d62728', '#9467bd']
        fig, ax = plt.subplots(figsize=(13, 6))
        bottom = np.zeros(len(valid))
        for c, lbl, col in zip(cols, col_labels, colors):
            vals = valid[c].fillna(0).to_numpy()
            ax.bar(valid['extractor'], vals, bottom=bottom,
                   label=lbl, color=col)
            bottom += vals
        ax.set_xticks(range(len(valid)))
        ax.set_xticklabels(valid['extractor'], rotation=30, ha='right',
                            fontsize=8)
        # Annotate family beneath x-tick labels
        for i, fam in enumerate(valid['family']):
            ax.text(i, -0.08, fam, ha='center', va='top', fontsize=7,
                     color='gray')
        ax.set_ylabel('quadrant occupancy fraction')
        ax.set_ylim(-0.15, 1.05)
        ax.set_title(f'Phase 16A.2 — state-occupancy extractor verification '
                      f'on Qwen 2.5 3B (verdict: {verdict})')
        ax.legend(fontsize=8, loc='upper right')
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "46_phase16a2_state_extractors.png"), dpi=120)
        plt.close(fig)
        print(f"\n  → plots/46_phase16a2_state_extractors.png")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")
    return verdict


if __name__ == '__main__':
    main()
