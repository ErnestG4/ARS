"""
Phase 10 — LLM cascade fingerprint matrix.

Runs Qwen 2.5 3B at three quantization levels (fp16, int8, int4) on
three stimulus texts (structured / natural / random) and three event-
extraction methods.  For each (model × quant × text × method) cell,
runs `arithmetic_toolkit.full_analysis` and saves the fingerprint
vector.

Output:
    data/phase10_llm_fingerprints.json
    plots/37_phase10_llm.png    (heatmap matrix)

Three questions:
  Q1.  Do quantization levels of the same model produce different
       universality classes?
  Q2.  Does stimulus structure (mathematical / natural / random)
       affect the fingerprint?
  Q3.  Do quant and stimulus vary independently or are they confounded?
"""
import os, sys, json, time, gc
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from llm_cascade import extract_cascade, get_event_times, get_default_texts
from arithmetic_toolkit import full_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
MODEL = "Qwen/Qwen2.5-3B"
QUANTIZATIONS = [None, "int8", "int4"]
EXTRACTION_METHODS = [
    ("surprisal_threshold",  dict(k=1.0)),
    ("surprisal_cumulative", dict(prom=0.3)),
    ("residual_norm_peaks",  dict(prom=0.3)),
]
MAX_SEQ_LEN = 2048


def _trim(res):
    """Drop bulky internals before JSON-encoding the fingerprint."""
    if 'error' in res: return res
    return dict(label=res['label'], n_events=res['n_events'],
                primary_nns=res['primary_nns'],
                fingerprint_vector=res['fingerprint_vector'],
                fingerprint_keys=res.get('fingerprint_keys'),
                fano_summary={k: res['fano_curve'].get(k)
                               for k in ('F_at_1', 'F_at_5', 'F_at_20',
                                         'mean_sp', 'duration')},
                ramanujan_summary={k: res['ramanujan'].get(k)
                                    for k in ('peak_q', 'top10_q', 'top10_amplitudes',
                                              'mode')},
                pair_correlation_summary={k: res['pair_correlation'].get(k)
                                           for k in ('R2_at_0_1', 'R2_at_0_5',
                                                     'R2_at_1', 'repulsion_integral')},
                sb_split_summary=res['sb_split'],
                padic_summary=dict(dominant_prime=res['padic_profile']['dominant_prime'],
                                    best_by_prime=res['padic_profile']['best_by_prime']),
                extraction_method=res.get('extraction_method'),
                model_name=res.get('model_name'),
                quantization=res.get('quantization'),
                seq_len=res.get('seq_len'),
                mean_surprisal=res.get('mean_surprisal'),
                std_surprisal=res.get('std_surprisal'))


def main():
    texts = get_default_texts()
    print(f"Stimulus token-length estimates (chars):")
    for k, v in texts.items():
        print(f"  {k}: {len(v)} chars")
    print()

    results = {}
    for quant in QUANTIZATIONS:
        quant_label = quant if quant else "fp16"
        print("=" * 100)
        print(f"  MODEL = {MODEL}    QUANT = {quant_label}")
        print("=" * 100)
        for stim_name, text in texts.items():
            print(f"\n  -- stimulus = {stim_name}  --")
            t0 = time.time()
            try:
                cascade = extract_cascade(text, model_name=MODEL,
                                            quantization=quant,
                                            max_seq_len=MAX_SEQ_LEN)
            except Exception as e:
                print(f"    extract_cascade failed: {e}")
                results[(quant_label, stim_name, '_load')] = dict(error=str(e))
                continue
            print(f"    n_tokens = {cascade['seq_len']}, "
                  f"mean surprisal = {np.mean(cascade['surprisal']):.3f}, "
                  f"std = {np.std(cascade['surprisal']):.3f}, "
                  f"⏱ {time.time() - t0:.1f}s")

            for method, kw in EXTRACTION_METHODS:
                events = get_event_times(cascade, method=method, **kw)
                if events.size < 20:
                    print(f"    [{method}]  insufficient events ({events.size})")
                    results[(quant_label, stim_name, method)] = dict(
                        error='insufficient', n_events=int(events.size))
                    continue
                res = full_analysis(events,
                                     label=f"{quant_label}|{stim_name}|{method}",
                                     q_max=8, ramanujan_q_max=200)
                res['extraction_method'] = method
                res['model_name'] = MODEL
                res['quantization'] = quant_label
                res['seq_len'] = cascade['seq_len']
                res['mean_surprisal'] = float(np.mean(cascade['surprisal']))
                res['std_surprisal']  = float(np.std(cascade['surprisal']))
                results[(quant_label, stim_name, method)] = res
                p = res['primary_nns']
                pc = res['pair_correlation']
                fan = res['fano_curve']
                print(f"    [{method:<22}]  n={res['n_events']:>4}  "
                      f"best={p['best']:<7}  KS_GUE={p['ks_u']:.3f}  "
                      f"mass<.3={p['mass03']:.3f}  "
                      f"F(T=5)={fan.get('F_at_5', float('nan')):.2f}  "
                      f"rep_int={pc.get('repulsion_integral', 0):.3f}")

            del cascade
            gc.collect()
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:
                pass

    # ─── Save JSON ────────────────────────────────────────────────────────────
    serial = {}
    for (q, s, m), v in results.items():
        serial.setdefault(q, {}).setdefault(s, {})[m] = _trim(v) if 'error' not in v else v
    with open(os.path.join(DATA, "phase10_llm_fingerprints.json"), 'w') as fp:
        json.dump(serial, fp, indent=2, default=str)
    print(f"\n  → data/phase10_llm_fingerprints.json")

    # ─── Comparison table ─────────────────────────────────────────────────────
    print("\n" + "=" * 130)
    print("Phase 10 fingerprint matrix")
    print("=" * 130)
    method_focus = "surprisal_cumulative"
    keys = ['KS_GUE', 'mass<0.3', 'F(T=1)', 'F(T=5)', 'rep_int', 'top_q']
    header = (f"  {'quant':<6}  {'stimulus':<10}  {'best':<7}  "
              f"{'n_ev':>5}  " + "  ".join(f"{k:>9}" for k in keys))
    print(f"  Showing extraction = {method_focus}")
    print(header); print("  " + "-" * (len(header) - 2))
    for q_label in [q if q else "fp16" for q in QUANTIZATIONS]:
        for stim_name in get_default_texts():
            res = results.get((q_label, stim_name, method_focus))
            if not res or 'error' in res:
                err = (res or {}).get('error', '?')
                print(f"  {q_label:<6}  {stim_name:<10}  err: {err}")
                continue
            fp_vec = res['fingerprint_vector']
            best = res['primary_nns']['best']
            cells = (f"{fp_vec[0]:>9.3f}  {fp_vec[3]:>9.3f}  "
                     f"{fp_vec[4]:>9.3f}  {fp_vec[5]:>9.3f}  "
                     f"{fp_vec[6]:>9.3f}  {int(fp_vec[7]):>9d}")
            print(f"  {q_label:<6}  {stim_name:<10}  {best:<7}  "
                  f"{res['n_events']:>5}  {cells}")

    # ─── Plot ────────────────────────────────────────────────────────────────
    rows = []
    for q_label in [q if q else "fp16" for q in QUANTIZATIONS]:
        for stim in get_default_texts():
            for method, _ in EXTRACTION_METHODS:
                key = (q_label, stim, method)
                res = results.get(key)
                if res and 'fingerprint_vector' in res:
                    rows.append((f"{q_label}|{stim}|{method}",
                                  res['fingerprint_vector']))
    if rows:
        labels = [r[0] for r in rows]
        M = np.array([r[1] for r in rows])
        keys_full = ['KS_GUE', 'KS_GOE', 'KS_P', 'mass<.3',
                     'F(1)', 'F(5)', 'rep_int', 'top_q', 'sb_KS', 'p_dom']
        col_min = np.nanmin(M, axis=0); col_max = np.nanmax(M, axis=0)
        rng = np.where(col_max > col_min, col_max - col_min, 1.0)
        Mn = (M - col_min) / rng
        fig, ax = plt.subplots(figsize=(12, 0.3 * len(labels) + 2))
        im = ax.imshow(Mn, aspect='auto', cmap='RdBu_r', vmin=0, vmax=1)
        ax.set_xticks(range(len(keys_full)), labels=keys_full,
                      rotation=45, ha='right')
        ax.set_yticks(range(len(labels)), labels=labels, fontsize=7)
        for i in range(len(labels)):
            for j in range(len(keys_full)):
                v = M[i, j]; vn = Mn[i, j]
                ax.text(j, i, f"{v:.2f}", ha='center', va='center',
                        fontsize=6,
                        color='white' if abs(vn - 0.5) > 0.32 else 'black')
        ax.set_title("Phase 10: Qwen 2.5 3B  ×  3 quant levels  ×  3 stimuli  ×  3 extraction methods")
        fig.colorbar(im, ax=ax, label='normalised across rows')
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "37_phase10_llm.png"), dpi=120)
        plt.close(fig)
        print(f"  → plots/37_phase10_llm.png")


if __name__ == '__main__':
    main()
