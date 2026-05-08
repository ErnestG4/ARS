"""
Phase 13 Tier 3A — Layer-depth sweep.

Diagnostic for the §7.ter.19 reinterpretation: is the near-uniform
residual-norm-peak structure present at every layer, or does it emerge
at a specific depth?

  - Present at layer 1 (post-embedding) → extraction-pipeline artifact
    operating on the natural autocorrelation rhythm of the token-norm
    signal.  Architecturally trivial, no internal-dynamics content.
  - Emerges at depth → computation-driven; the residual stream must
    accumulate something that produces the uniform-spacing fingerprint.
  - Sharp transition at a specific layer → that layer is doing the
    relevant work.
  - Degrades at final layers → read-out / unembedding effect, not
    representation.

Procedure: load Qwen 2.5 3B fp16 once.  Forward-pass the natural
stimulus with output_hidden_states=True.  For each layer ∈ {0..36},
extract residual-norm peaks at that layer, run full_analysis,
record fingerprint.

Output:
    data/phase13_layer_sweep.json
    plots/41_phase13_layer_sweep.png
"""
import os, sys, json, time, gc
import numpy as np

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from llm_cascade import NATURAL_TEXT
from arithmetic_toolkit import full_analysis
from scipy.signal import find_peaks
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
MODEL = "Qwen/Qwen2.5-3B"


def main():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"Loading {MODEL} fp16 …")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map="cuda",
        attn_implementation="eager", trust_remote_code=True,
    )
    model.eval()
    print(f"  loaded in {time.time() - t0:.1f}s")

    inputs = tokenizer(NATURAL_TEXT, return_tensors="pt",
                        truncation=True, max_length=2048).to(model.device)
    print(f"  seq_len = {inputs['input_ids'].shape[1]}")

    with torch.no_grad():
        out = model(inputs['input_ids'], output_hidden_states=True)

    # hidden_states is a tuple of (n_layers + 1) tensors
    # hidden_states[0] = embedding output (layer 0)
    # hidden_states[i] = output of decoder layer i, i ∈ {1..n_layers}
    hidden_states = out.hidden_states
    n_layers = len(hidden_states)
    print(f"  n_layers (incl. embedding) = {n_layers}")

    # Compute per-layer residual-norm trace
    norms_by_layer = []
    for i, h in enumerate(hidden_states):
        n = h[0].norm(dim=-1).float().cpu().numpy()  # [seq_len]
        norms_by_layer.append(n)
    norms_by_layer = np.stack(norms_by_layer)  # [n_layers, seq_len]
    del out, hidden_states
    gc.collect(); torch.cuda.empty_cache()
    print(f"  norms collected: shape = {norms_by_layer.shape}")

    # ─── Run fingerprint per layer ──────────────────────────────────────────
    print("\n" + "=" * 110)
    print("Per-layer residual-norm-peak fingerprint")
    print("=" * 110)
    print(f"  {'layer':>5}  {'n_ev':>5}  {'best':<7}  "
          f"{'KS_GUE':>7}  {'KS_GOE':>7}  {'mass<.3':>7}  "
          f"{'F(T=5)':>7}  {'rep_int':>7}  {'mean_norm':>10}")
    print("  " + "-" * 100)

    rows = []
    for i in range(n_layers):
        norms_i = norms_by_layer[i, 1:]  # drop first token (no surprisal anchor)
        peaks, _ = find_peaks(norms_i, prominence=0.3)
        if peaks.size < 2:
            peaks, _ = find_peaks(norms_i, prominence=max(0.05,
                                                           norms_i.std() * 0.1))
        events = peaks.astype(np.float64)
        if events.size < 20:
            print(f"  {i:>5}  {events.size:>5}  insufficient")
            rows.append(dict(layer=i, n_events=int(events.size),
                              error='insufficient'))
            continue
        res = full_analysis(events, label=f"layer_{i}", q_max=8,
                             ramanujan_q_max=200)
        if 'error' in res:
            rows.append(dict(layer=i, **res))
            continue
        p = res['primary_nns']; pc = res['pair_correlation']; fan = res['fano_curve']
        rows.append(dict(
            layer=i,
            n_events=res['n_events'],
            ks_u=p['ks_u'], ks_o=p['ks_o'], ks_p=p['ks_p'],
            mass03=p['mass03'],
            F_at_5=fan.get('F_at_5'),
            rep_int=pc.get('repulsion_integral', 0),
            best=p['best'],
            mean_norm=float(norms_i.mean())))
        print(f"  {i:>5}  {res['n_events']:>5}  {p['best']:<7}  "
              f"{p['ks_u']:>7.3f}  {p['ks_o']:>7.3f}  {p['mass03']:>7.3f}  "
              f"{fan.get('F_at_5', float('nan')):>7.3f}  "
              f"{pc.get('repulsion_integral', 0):>7.3f}  "
              f"{norms_i.mean():>10.2f}")

    # ─── Save ───────────────────────────────────────────────────────────────
    out_dict = dict(model=MODEL, n_layers=n_layers, stimulus='natural',
                     seq_len=int(inputs['input_ids'].shape[1]),
                     prominence=0.3,
                     per_layer=rows,
                     mean_norm_per_layer=norms_by_layer.mean(axis=1).tolist())
    with open(os.path.join(DATA, "phase13_layer_sweep.json"), 'w') as f:
        json.dump(out_dict, f, indent=2, default=str)
    print(f"\n  → data/phase13_layer_sweep.json")

    # ─── Plot ───────────────────────────────────────────────────────────────
    valid = [r for r in rows if 'ks_u' in r]
    if valid:
        layers_arr = np.array([r['layer'] for r in valid])
        ks_u = np.array([r['ks_u'] for r in valid])
        mass = np.array([r['mass03'] for r in valid])
        f5   = np.array([r['F_at_5'] for r in valid])
        ri   = np.array([r['rep_int'] for r in valid])
        n_ev = np.array([r['n_events'] for r in valid])

        fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

        ax = axes[0, 0]
        ax.plot(layers_arr, ks_u, 'C0o-', lw=1.5, ms=5)
        ax.axhline(0.21, color='C3', ls='--', lw=1, label='LLM Phase 10/11 mean (0.21)')
        ax.axhline(0.105, color='C2', ls=':', lw=1, label='β=8 (0.105)')
        ax.axhline(0.022, color='gray', ls=':', lw=1, label='calibrator (0.022)')
        ax.set_ylabel('KS_GUE')
        ax.set_title('KS to Wigner GUE per layer')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        ax = axes[0, 1]
        ax.plot(layers_arr, mass, 'C1o-', lw=1.5, ms=5)
        ax.axhline(0.0, color='C3', ls='--', lw=1, label='LLM Phase 10/11 (0.000)')
        ax.axhline(0.10, color='gray', ls=':', lw=1, label='Wigner GUE baseline (~0.10)')
        ax.axhline(0.26, color='gray', ls=':', lw=1, label='Poisson (0.26)')
        ax.set_ylabel('mass<0.3')
        ax.set_title('Short-spacing mass per layer')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        ax = axes[1, 0]
        ax.plot(layers_arr, f5, 'C2o-', lw=1.5, ms=5)
        ax.axhline(0.13, color='C3', ls='--', lw=1, label='LLM Phase 10/11 mean (0.13)')
        ax.axhline(1.0, color='gray', ls=':', lw=1, label='Poisson F=1')
        ax.set_xlabel('layer index (0 = embedding)')
        ax.set_ylabel('F(T=5)')
        ax.set_title('Fano factor F(T=5) per layer')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        ax = axes[1, 1]
        ax.plot(layers_arr, ri, 'C3o-', lw=1.5, ms=5)
        ax.axhline(0.900, color='C3', ls='--', lw=1, label='uniform-saturation (0.900)')
        ax.axhline(0.50, color='C0', ls=':', lw=1, label='Wigner GUE (~0.50)')
        ax.axhline(0.0, color='gray', ls=':', lw=1, label='Poisson (0.0)')
        ax.set_xlabel('layer index (0 = embedding)')
        ax.set_ylabel('repulsion integral')
        ax.set_title('Pair-correlation repulsion integral per layer')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        fig.suptitle(f'Phase 13 Tier 3A — Qwen 2.5 3B layer-depth sweep '
                     f'(natural stimulus, n_layers={n_layers})')
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "41_phase13_layer_sweep.png"), dpi=120)
        plt.close(fig)
        print(f"  → plots/41_phase13_layer_sweep.png")

    # ─── Diagnostic summary ─────────────────────────────────────────────────
    if valid:
        print("\n" + "=" * 110)
        print("DIAGNOSTIC")
        print("=" * 110)
        layer_0 = next((r for r in valid if r['layer'] == 0), None)
        layer_final = valid[-1]
        if layer_0:
            print(f"  Layer 0 (embedding):  rep_int={layer_0['rep_int']:.3f}  "
                  f"mass<.3={layer_0['mass03']:.3f}  F(T=5)={layer_0['F_at_5']:.3f}")
        print(f"  Layer {layer_final['layer']} (final): rep_int={layer_final['rep_int']:.3f}  "
              f"mass<.3={layer_final['mass03']:.3f}  F(T=5)={layer_final['F_at_5']:.3f}")
        ri_arr = ri
        if ri_arr.size > 5:
            early = ri_arr[:max(2, len(ri_arr)//8)].mean()
            late  = ri_arr[-max(2, len(ri_arr)//8):].mean()
            shift = late - early
            print(f"\n  rep_int shift early→late: {early:.3f} → {late:.3f}  Δ={shift:+.3f}")
            if abs(shift) < 0.05 and ri_arr.min() > 0.7:
                print(f"  → Near-uniform fingerprint is **present at all layers**.")
                print(f"    Conclusion: extraction-pipeline-on-token-rhythm artifact, ")
                print(f"    NOT computation-driven internal dynamics.")
            elif shift > 0.1:
                print(f"  → rep_int rises with depth — the uniform-spacing structure ")
                print(f"    ACCUMULATES with layers.  Computation-driven.")
            elif shift < -0.1:
                print(f"  → rep_int decreases with depth.  Layer 0 has more uniform ")
                print(f"    structure that is partially erased by computation.")
            else:
                print(f"  → Modest shift; pattern not strongly directional.")


if __name__ == '__main__':
    main()
