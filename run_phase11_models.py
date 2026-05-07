"""
Phase 11 — Model-family fingerprint swap.

Same stimulus, same extraction, different LLM architectures.  Tests
whether the universal Wigner GUE fingerprint of residual-norm peaks
(found in Phase 10 on Qwen 2.5 3B) is an architectural signature or
a property specific to that one model.

Models (3B-7B, all open):
    Qwen/Qwen2.5-3B          - 3.0B,  Qwen architecture, base
    microsoft/Phi-3-mini-4k-instruct  - 3.8B, Phi-3 architecture, instruct
    mistralai/Mistral-7B-v0.1   - 7.2B, Mistral architecture, base

Stimulus: NATURAL_TEXT (middle of the surprisal gradient).
Extraction: residual_norm_peaks (canonical from Phase 10).
Extra extraction for cross-check: surprisal_cumulative.

Output:
    data/phase11_model_family.json
    plots/38_phase11_models.png
"""
import os, sys, json, time, gc
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from llm_cascade import extract_cascade, get_event_times, NATURAL_TEXT, STRUCTURED_TEXT, RANDOM_TEXT
from arithmetic_toolkit import full_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
MAX_SEQ_LEN = 2048

MODELS = [
    "Qwen/Qwen2.5-3B",
    "microsoft/Phi-3-mini-4k-instruct",
    "mistralai/Mistral-7B-v0.1",
]
STIMULI = {"structured": STRUCTURED_TEXT,
           "natural":     NATURAL_TEXT,
           "random":      RANDOM_TEXT}
EXTRACTION_METHODS = [
    ("residual_norm_peaks",  dict(prom=0.3)),
    ("surprisal_cumulative", dict(prom=0.3)),
]


def _trim(res):
    if 'error' in res: return res
    return dict(label=res['label'], n_events=res['n_events'],
                primary_nns=res['primary_nns'],
                fingerprint_vector=res['fingerprint_vector'],
                fano_summary={k: res['fano_curve'].get(k)
                               for k in ('F_at_1', 'F_at_5', 'F_at_20',
                                         'mean_sp', 'duration')},
                ramanujan_summary={k: res['ramanujan'].get(k)
                                    for k in ('peak_q', 'top10_q', 'mode')},
                pair_correlation_summary={k: res['pair_correlation'].get(k)
                                           for k in ('R2_at_0_1', 'R2_at_1',
                                                     'repulsion_integral')},
                model=res.get('model_name'),
                stimulus=res.get('stimulus'),
                extraction_method=res.get('extraction_method'),
                seq_len=res.get('seq_len'),
                mean_surprisal=res.get('mean_surprisal'),
                std_surprisal=res.get('std_surprisal'))


def main():
    results = {}
    for model_name in MODELS:
        print("=" * 110)
        print(f"  MODEL = {model_name}")
        print("=" * 110)
        for stim_name, text in STIMULI.items():
            print(f"\n  -- stimulus = {stim_name}  --")
            t0 = time.time()
            try:
                cascade = extract_cascade(text, model_name=model_name,
                                            quantization=None,
                                            max_seq_len=MAX_SEQ_LEN)
            except Exception as e:
                print(f"    extract_cascade failed: {type(e).__name__}: {e}")
                results[(model_name, stim_name, '_load')] = dict(error=str(e))
                gc.collect()
                try:
                    import torch; torch.cuda.empty_cache()
                except Exception: pass
                continue

            print(f"    n_tokens={cascade['seq_len']}  "
                  f"surprisal mean={np.mean(cascade['surprisal']):.3f} "
                  f"std={np.std(cascade['surprisal']):.3f}  "
                  f"⏱ {time.time() - t0:.1f}s")

            for method, kw in EXTRACTION_METHODS:
                events = get_event_times(cascade, method=method, **kw)
                if events.size < 20:
                    print(f"    [{method}]  insufficient events ({events.size})")
                    results[(model_name, stim_name, method)] = dict(
                        error='insufficient', n_events=int(events.size))
                    continue
                res = full_analysis(events,
                                     label=f"{model_name}|{stim_name}|{method}",
                                     q_max=8, ramanujan_q_max=200)
                res['model_name'] = model_name
                res['stimulus'] = stim_name
                res['extraction_method'] = method
                res['seq_len'] = cascade['seq_len']
                res['mean_surprisal'] = float(np.mean(cascade['surprisal']))
                res['std_surprisal']  = float(np.std(cascade['surprisal']))
                results[(model_name, stim_name, method)] = res
                p = res['primary_nns']; pc = res['pair_correlation']; fan = res['fano_curve']
                print(f"    [{method:<22}]  n={res['n_events']:>4}  "
                      f"best={p['best']:<7}  KS_GUE={p['ks_u']:.3f}  "
                      f"mass<.3={p['mass03']:.3f}  "
                      f"F(T=5)={fan.get('F_at_5', float('nan')):.2f}  "
                      f"rep_int={pc.get('repulsion_integral', 0):.3f}")

            del cascade
            gc.collect()
            try:
                import torch; torch.cuda.empty_cache()
            except Exception: pass

    # ─── Save JSON ───────────────────────────────────────────────────────────
    serial = {}
    for (mdl, stim, method), v in results.items():
        m_short = mdl.split('/')[-1]
        serial.setdefault(m_short, {}).setdefault(stim, {})[method] = (
            _trim(v) if 'error' not in v else v)
    with open(os.path.join(DATA, "phase11_model_family.json"), 'w') as fp:
        json.dump(serial, fp, indent=2, default=str)
    print(f"\n  → data/phase11_model_family.json")

    # ─── Comparison table ───────────────────────────────────────────────────
    print("\n" + "=" * 130)
    print("Phase 11 model-family fingerprint matrix  (extraction = residual_norm_peaks)")
    print("=" * 130)
    keys = ['n_ev', 'KS_GUE', 'mass<.3', 'F(T=1)', 'F(T=5)', 'rep_int', 'top_q']
    header = (f"  {'model':<38}  {'stim':<10}  {'best':<7}  " +
              "  ".join(f"{k:>9}" for k in keys))
    print(header); print("  " + "-" * (len(header) - 2))
    for mdl in MODELS:
        m_short = mdl.split('/')[-1]
        for stim in STIMULI:
            res = results.get((mdl, stim, 'residual_norm_peaks'))
            if not res or 'error' in res:
                err = (res or {}).get('error', '?')
                print(f"  {m_short[:36]:<38}  {stim:<10}  err: {err}")
                continue
            fp_vec = res['fingerprint_vector']
            best = res['primary_nns']['best']
            print(f"  {m_short[:36]:<38}  {stim:<10}  {best:<7}  "
                  f"{res['n_events']:>9}  "
                  f"{fp_vec[0]:>9.3f}  {fp_vec[3]:>9.3f}  "
                  f"{fp_vec[4]:>9.3f}  {fp_vec[5]:>9.3f}  "
                  f"{fp_vec[6]:>9.3f}  {int(fp_vec[7]):>9d}")

    print(f"\n  Phase 11 model-family fingerprint matrix  (extraction = surprisal_cumulative)")
    print("  " + "-" * 110)
    print(header); print("  " + "-" * (len(header) - 2))
    for mdl in MODELS:
        m_short = mdl.split('/')[-1]
        for stim in STIMULI:
            res = results.get((mdl, stim, 'surprisal_cumulative'))
            if not res or 'error' in res:
                err = (res or {}).get('error', '?')
                print(f"  {m_short[:36]:<38}  {stim:<10}  err: {err}")
                continue
            fp_vec = res['fingerprint_vector']
            best = res['primary_nns']['best']
            print(f"  {m_short[:36]:<38}  {stim:<10}  {best:<7}  "
                  f"{res['n_events']:>9}  "
                  f"{fp_vec[0]:>9.3f}  {fp_vec[3]:>9.3f}  "
                  f"{fp_vec[4]:>9.3f}  {fp_vec[5]:>9.3f}  "
                  f"{fp_vec[6]:>9.3f}  {int(fp_vec[7]):>9d}")

    # ─── Plot ────────────────────────────────────────────────────────────────
    rows = []
    for mdl in MODELS:
        m_short = mdl.split('/')[-1]
        for stim in STIMULI:
            for method, _ in EXTRACTION_METHODS:
                key = (mdl, stim, method)
                res = results.get(key)
                if res and 'fingerprint_vector' in res:
                    rows.append((f"{m_short[:24]}|{stim[:6]}|{method[:9]}",
                                  res['fingerprint_vector']))
    if rows:
        labels = [r[0] for r in rows]
        M = np.array([r[1] for r in rows])
        keys_full = ['KS_GUE', 'KS_GOE', 'KS_P', 'mass<.3',
                     'F(1)', 'F(5)', 'rep_int', 'top_q', 'sb_KS', 'p_dom']
        col_min = np.nanmin(M, axis=0); col_max = np.nanmax(M, axis=0)
        rng = np.where(col_max > col_min, col_max - col_min, 1.0)
        Mn = (M - col_min) / rng
        fig, ax = plt.subplots(figsize=(13, 0.32 * len(labels) + 2))
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
        ax.set_title("Phase 11: Qwen 2.5 3B  /  Phi-3 mini 4k  /  Mistral 7B v0.1  ×  3 stim  ×  2 extractions")
        fig.colorbar(im, ax=ax, label='normalised across rows')
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "38_phase11_models.png"), dpi=120)
        plt.close(fig)
        print(f"  → plots/38_phase11_models.png")


if __name__ == '__main__':
    main()
