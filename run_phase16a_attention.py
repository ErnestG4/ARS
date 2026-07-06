"""
Phase 16A — LLM attention extractor invariance.

Run five attention-based extractors on a single cached LLM cascade
(Qwen 2.5 3B fp16, natural stimulus, attentions kept).  For each
extractor produce a t_k point process, run joint_q_profile +
joint_quadrant_diagnostic, record primary quadrant.

Three branches per spec:
  (i) all extractors → BR_artifact: LLM is genuinely uniform-jitter
      under multiple independent extraction methods.  Soften §7.ter.19.
  (ii) at least one by-construction extractor → TR/BL/TL: find_peaks
       artifact reading from §7.ter.19 confirmed.
  (iii) by-construction split: multiple structurally distinct extractor
        families exist.  Most informative outcome.

Output:
  data/phase16a_attention_matrix.parquet
  plots/45_phase16a_attention_quadrants.png
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
MAX_SEQ_LEN = 1024   # smaller than Phase 11 (2048) to fit attention storage
Q_MAX = 50
MIN_EVENTS = 30


def main():
    t_start = time.time()
    print(f"Loading {MODEL} fp16 + natural stimulus, max_seq_len={MAX_SEQ_LEN}…")
    t0 = time.time()
    cascade = extract_cascade(NATURAL_TEXT, model_name=MODEL,
                                max_seq_len=MAX_SEQ_LEN,
                                compute_attention=True,
                                keep_attention=True)
    print(f"  seq_len={cascade['seq_len']}  "
          f"attentions kept: {len(cascade.get('attentions', []))} layers  "
          f"⏱ {time.time() - t0:.1f}s")

    rows = []
    print("\n" + "=" * 110)
    print(f"Phase 16A — LLM attention extractor matrix at q_max={Q_MAX}")
    print("=" * 110)
    print(f"  {'extractor':<32}  {'n_events':>8}  {'primary':<14}  "
          f"{'rep_int':>7}  {'KS_GUE':>7}  ⏱")
    print("  " + "-" * 90)

    # Per-extractor kwargs — calibrated to produce ≥50 events at seq_len=404.
    # Lowered k for sink/KL events to capture enough of the upper tail.
    extractor_kwargs = {
        'attention_sink_events':       dict(k=0.3, window=20),
        'layer_kl_divergence_events':  dict(k=0.3, window=20),
        'attention_target_jumps':      dict(delta_tokens=8),
    }

    for ext_name in LLM_EXTRACTORS:
        t_e = time.time()
        try:
            kw = extractor_kwargs.get(ext_name, {})
            t_k = extract_llm(cascade, ext_name, **kw)
        except Exception as e:
            print(f"  {ext_name:<32}  EXTRACT FAILED: {type(e).__name__}: {e}")
            rows.append(dict(extractor=ext_name, error=str(e)))
            continue
        if t_k is None or t_k.size < 50:
            print(f"  {ext_name:<32}  {t_k.size if t_k is not None else 0:>8}  "
                  f"insufficient events")
            rows.append(dict(extractor=ext_name,
                              n_events=int(t_k.size if t_k is not None else 0),
                              primary='underpowered',
                              error='insufficient'))
            continue
        df = joint_q_profile(t_k, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
        df = joint_quadrant_diagnostic(df)
        well = df[~df['underpowered']]
        if len(well) == 0:
            primary, primary_pct = 'underpowered', 0.0
            rep_med = ks_med = np.nan
            br_a = br_n = tl = tr = bl = np.nan
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
        elapsed = time.time() - t_e
        rows.append(dict(extractor=ext_name, n_events=int(t_k.size),
                          primary=primary, primary_pct=primary_pct,
                          rep_int_med=rep_med, ks_gue_med=ks_med,
                          br_a_pct=br_a, br_n_pct=br_n,
                          tl_pct=tl, tr_pct=tr, bl_pct=bl,
                          elapsed_s=elapsed))
        print(f"  {ext_name:<32}  {t_k.size:>8}  {primary:<14}  "
              f"{rep_med:>7.3f}  {ks_med:>7.3f}  ({primary_pct*100:>4.1f}%)  ⏱ {elapsed:.0f}s")

    df_pool = pd.DataFrame(rows)
    df_pool.to_parquet(os.path.join(DATA, "phase16a_attention_matrix.parquet"))
    print(f"\n  → data/phase16a_attention_matrix.parquet")

    # ─── Verdict ────────────────────────────────────────────────────────────
    print("\n" + "=" * 110)
    print("VERDICT")
    print("=" * 110)

    by_construction = ['attention_target_jumps', 'attention_sink_events',
                        'layer_kl_divergence_events']
    bc_results = df_pool[df_pool['extractor'].isin(by_construction)]
    bc_quadrants = bc_results['primary'].dropna().tolist()

    valid = df_pool.dropna(subset=['primary'])
    print(f"  Control extractors:")
    for _, r in valid[~valid['extractor'].isin(by_construction)].iterrows():
        print(f"    {r['extractor']:<32}  → {r['primary']}")
    print(f"  By-construction extractors:")
    for _, r in valid[valid['extractor'].isin(by_construction)].iterrows():
        print(f"    {r['extractor']:<32}  → {r['primary']}")

    n_br_a = sum(1 for q in bc_quadrants if q == 'BR_artifact')
    n_other = sum(1 for q in bc_quadrants if q != 'BR_artifact'
                                              and q != 'underpowered')

    print()
    if n_br_a == len(bc_quadrants) and n_br_a > 0:
        print("  → Branch (i): ALL by-construction extractors classify LLM as BR_artifact.")
        print("    Soften §7.ter.19 reading: BR_artifact regime is invariant across")
        print("    extractor families; the find_peaks extractor reproduces this")
        print("    classification but does not solely produce it.  Substantive update.")
    elif n_other > 0 and n_br_a > 0:
        print("  → Branch (iii): by-construction extractors SPLIT.")
        print(f"    {n_br_a} → BR_artifact, {n_other} → other quadrants.")
        print("    Most informative outcome.  Different extractor families read")
        print("    different attention properties; class identification is")
        print("    extractor-conditional.")
    elif n_other > 0:
        print("  → Branch (ii): by-construction extractors classify LLM as NOT-BR_artifact.")
        print("    The find_peaks reading from §7.ter.19 stands; the LLM peak")
        print("    process is extractor-induced uniform-jitter, not an underlying")
        print("    property.  §7.ter.19 reading reinforced.")
    else:
        print("  → Underpowered: by-construction extractors did not produce")
        print("    enough events for classification.  Tighten thresholds and rerun.")

    # ─── Plot ───────────────────────────────────────────────────────────────
    valid_plot = df_pool.dropna(subset=['primary']).copy()
    if len(valid_plot) > 0:
        valid_plot['is_bc'] = valid_plot['extractor'].isin(by_construction)
        fig, ax = plt.subplots(figsize=(11, 5))
        # Stacked-bar of quadrant occupancy fractions per extractor
        cols = ['bl_pct', 'tr_pct', 'tl_pct', 'br_a_pct', 'br_n_pct']
        col_labels = ['BL', 'TR', 'TL', 'BR_artifact', 'BR_novel']
        colors = ['#7d7d7d', '#1f77b4', '#ff7f0e', '#d62728', '#9467bd']
        bottom = np.zeros(len(valid_plot))
        for c, lbl, col in zip(cols, col_labels, colors):
            vals = valid_plot[c].fillna(0).to_numpy()
            ax.bar(valid_plot['extractor'], vals, bottom=bottom,
                   label=lbl, color=col)
            bottom += vals
        ax.set_xticks(range(len(valid_plot)))
        ax.set_xticklabels(valid_plot['extractor'], rotation=30, ha='right',
                            fontsize=9)
        # mark by-construction extractors
        for i, is_bc in enumerate(valid_plot['is_bc']):
            if is_bc:
                ax.text(i, -0.05, '↑ by-construction', ha='center', va='top',
                        fontsize=7, color='black')
        ax.set_ylabel('quadrant occupancy fraction')
        ax.set_ylim(-0.1, 1.05)
        ax.set_title('Phase 16A — LLM attention extractor quadrant occupancy '
                      f'(Qwen 2.5 3B fp16, seq_len={cascade["seq_len"]})')
        ax.legend(fontsize=8, loc='upper right', bbox_to_anchor=(1, 1))
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "45_phase16a_attention_quadrants.png"), dpi=120)
        plt.close(fig)
        print(f"\n  → plots/45_phase16a_attention_quadrants.png")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == '__main__':
    main()
