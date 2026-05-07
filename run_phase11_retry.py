"""
Phase 11 retry — Mistral 7B (int4) and TinyLlama 1.1B (fp16) to fill
the model-family matrix.  Phi-3-mini fails to load in transformers 5.x
due to a rope_scaling schema mismatch; substituted with TinyLlama
(Llama architecture, 1.1B) for a third distinct architecture.

Mistral-7B-v0.1 in fp16 OOMs at seq_len=2048 with output_attentions=True
(32 layers × 32 heads × 2048² × fp16 ≈ 8 GB just for attention matrices,
plus 14 GB weights → exceeds 24 GB).  Loading with int4 quantization
brings memory to ~5 GB weights + attention overhead < 12 GB total — fits.

Output:
    data/phase11_model_family.json   (merged with existing Qwen entries)
    plots/38_phase11_models.png      (regenerated from merged data)
"""
import os, sys, json, time, gc
import numpy as np

# Allow expandable allocator to reduce fragmentation between model loads.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from llm_cascade import (extract_cascade, get_event_times,
                          STRUCTURED_TEXT, NATURAL_TEXT, RANDOM_TEXT)
from arithmetic_toolkit import full_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
EXISTING_JSON = os.path.join(DATA, "phase11_model_family.json")

STIMULI = {"structured": STRUCTURED_TEXT, "natural": NATURAL_TEXT, "random": RANDOM_TEXT}
EXTRACTION_METHODS = [
    ("residual_norm_peaks",  dict(prom=0.3)),
    ("surprisal_cumulative", dict(prom=0.3)),
]

# Models to (re-)run.  Qwen 2.5 3B already in JSON — skip if present.
RETRY_MODELS = [
    ("TinyLlama/TinyLlama-1.1B-Chat-v1.0", None,    1024),
    ("mistralai/Mistral-7B-v0.1",          "int4",  1024),
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
                quantization=res.get('quantization'),
                seq_len=res.get('seq_len'),
                mean_surprisal=res.get('mean_surprisal'),
                std_surprisal=res.get('std_surprisal'))


def main():
    serial = json.load(open(EXISTING_JSON)) if os.path.exists(EXISTING_JSON) else {}

    for model_name, quant, max_seq_len in RETRY_MODELS:
        m_short = model_name.split('/')[-1]
        # Wipe failed entries from the previous run, keep good ones
        if m_short in serial:
            for stim, methods in serial[m_short].items():
                for method, res in list(methods.items()):
                    if isinstance(res, dict) and 'error' in res:
                        methods.pop(method, None)
                # remove empty stim entries
            serial[m_short] = {s: v for s, v in serial[m_short].items() if v}
        serial.setdefault(m_short, {})

        print("=" * 110)
        print(f"  MODEL = {model_name}   quant={quant}   seq_len={max_seq_len}")
        print("=" * 110)
        for stim_name, text in STIMULI.items():
            print(f"\n  -- stimulus = {stim_name}  --")
            t0 = time.time()
            try:
                cascade = extract_cascade(text, model_name=model_name,
                                            quantization=quant,
                                            max_seq_len=max_seq_len)
            except Exception as e:
                print(f"    extract_cascade failed: {type(e).__name__}: {str(e)[:200]}")
                serial[m_short].setdefault(stim_name, {})['_load'] = dict(
                    error=f"{type(e).__name__}: {str(e)[:200]}")
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
                    serial[m_short].setdefault(stim_name, {})[method] = dict(
                        error='insufficient', n_events=int(events.size))
                    continue
                res = full_analysis(events,
                                     label=f"{model_name}|{stim_name}|{method}",
                                     q_max=8, ramanujan_q_max=200)
                res['model_name'] = model_name
                res['stimulus'] = stim_name
                res['extraction_method'] = method
                res['quantization'] = quant
                res['seq_len'] = cascade['seq_len']
                res['mean_surprisal'] = float(np.mean(cascade['surprisal']))
                res['std_surprisal']  = float(np.std(cascade['surprisal']))
                serial[m_short].setdefault(stim_name, {})[method] = _trim(res)
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

    with open(EXISTING_JSON, 'w') as fp:
        json.dump(serial, fp, indent=2, default=str)
    print(f"\n  → data/phase11_model_family.json  (merged)")

    # ─── Comparison table (residual_norm_peaks) ─────────────────────────────
    print("\n" + "=" * 130)
    print("Phase 11 model-family fingerprint matrix  (residual_norm_peaks)")
    print("=" * 130)
    keys = ['n_ev', 'KS_GUE', 'mass<.3', 'F(T=1)', 'F(T=5)', 'rep_int', 'top_q']
    header = (f"  {'model':<38}  {'stim':<10}  {'best':<7}  " +
              "  ".join(f"{k:>9}" for k in keys))
    print(header); print("  " + "-" * (len(header) - 2))
    for m_short in serial:
        for stim in STIMULI:
            res = serial[m_short].get(stim, {}).get('residual_norm_peaks')
            if not res or 'error' in res:
                err = (res or {}).get('error', 'missing')
                print(f"  {m_short[:36]:<38}  {stim:<10}  err: {str(err)[:50]}")
                continue
            fp_vec = res['fingerprint_vector']
            best = res['primary_nns']['best']
            print(f"  {m_short[:36]:<38}  {stim:<10}  {best:<7}  "
                  f"{res['n_events']:>9}  "
                  f"{fp_vec[0]:>9.3f}  {fp_vec[3]:>9.3f}  "
                  f"{fp_vec[4]:>9.3f}  {fp_vec[5]:>9.3f}  "
                  f"{fp_vec[6]:>9.3f}  {int(fp_vec[7]):>9d}")

    print(f"\nPhase 11 model-family fingerprint matrix  (surprisal_cumulative)")
    print("  " + "-" * 130)
    print(header); print("  " + "-" * (len(header) - 2))
    for m_short in serial:
        for stim in STIMULI:
            res = serial[m_short].get(stim, {}).get('surprisal_cumulative')
            if not res or 'error' in res:
                err = (res or {}).get('error', 'missing')
                print(f"  {m_short[:36]:<38}  {stim:<10}  err: {str(err)[:50]}")
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
    for m_short in serial:
        for stim in STIMULI:
            for method, _ in EXTRACTION_METHODS:
                res = serial[m_short].get(stim, {}).get(method)
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
        ax.set_title("Phase 11: model-family fingerprint matrix")
        fig.colorbar(im, ax=ax, label='normalised across rows')
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "38_phase11_models.png"), dpi=120)
        plt.close(fig)
        print(f"  → plots/38_phase11_models.png")


if __name__ == '__main__':
    main()
