"""
Phase 12 — Planat hypothesis test.

Test: is there an optimal human-perturbation rate that produces *cleaner*
Wigner GUE statistics in the LLM residual stream than either pure
uninterrupted generation or heavily-perturbed back-and-forth?

Prediction (from everything in Phases 10-11): KS_GUE follows a
U-shaped curve in perturbation rate.  Minimum (cleanest GUE) at some
non-trivial rate; degraded at both ends.

Procedure:
  1. Load Qwen 2.5 3B (canonical model from Phase 10/11).
  2. For each perturbation rate r in {0, 4, 9, 19, 39} splices per
     ~2000 tokens:
       - Start with a seed prompt.
       - Loop: generate N tokens, splice a perturbation phrase + topic,
         repeat until target total length reached.
       - Capture the full text.
       - extract_cascade on the full text → residual_norm_peaks events
         → full_analysis fingerprint.
  3. Compare KS_GUE, F(T=5), rep_int across perturbation rates.

If the prediction holds — KS_GUE lower at some intermediate rate than
at the endpoints, with rep_int held at ≥ 0.900 — that is empirical
confirmation of the Planat 2026 conjecture in an instrument whose
mathematical scaffolding traces back to Planat's own 2002 results on
Farey sequences and PLL phase locking.

Output:
    data/phase12_planat.json
    plots/39_phase12_planat.png
"""
import os, sys, json, time, gc
import numpy as np

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from llm_cascade import extract_cascade, get_event_times
from arithmetic_toolkit import full_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
MODEL = "Qwen/Qwen2.5-3B"
TARGET_TOKENS = 2048
SEED_PROMPT = (
    "The following is a long-form exploration of the relationship between "
    "mathematics and physics.  We will move through several themes — "
    "symmetry, randomness, structure — examining each carefully.\n\n"
    "First, let us begin with the Riemann zeta function and its zeros."
)

# Each splice is one "redirection" — the cumulative count divides
# the total budget into blocks.
PERTURBATION_RATES = [0, 4, 9, 19, 39]

PERTURB_PHRASES = [
    "Actually, let me redirect — ",
    "Hold on, I want to ask about something else.  ",
    "Wait, can you explain ",
    "Let me change topics.  Discuss ",
    "Okay but what about ",
    "Setting that aside, tell me about ",
    "Pause — what is ",
    "Different question: ",
    "Now I'm curious about ",
    "Switching gears: ",
]

PERTURB_TOPICS = [
    "the role of cellular automata in modern computer science",
    "how protein folding relates to optimization landscapes",
    "the historical development of group theory",
    "why the periodic table has the structure it does",
    "the connection between thermodynamics and information theory",
    "the geometry of three-dimensional knots",
    "the algorithmic complexity of factoring large integers",
    "how birds navigate using magnetoreception",
    "the role of symmetry breaking in particle physics",
    "the philosophy of mathematical Platonism",
    "the relationship between music theory and number theory",
    "the structure of the standard model Lagrangian",
    "how the brain represents grid cells in spatial memory",
    "the mathematical foundations of topology",
    "the chemistry of catalysis at metal surfaces",
]


def _build_text_with_splices(model, tokenizer, n_splices,
                             target_tokens=TARGET_TOKENS,
                             seed_prompt=SEED_PROMPT,
                             temperature=0.7, top_p=0.9, seed=42):
    """Generate a long sequence with `n_splices` interruptions evenly
    spaced through the target length.

    Returns the full text plus a list of (token_position, splice_phrase)
    annotations for diagnostic purposes.
    """
    import torch
    rng = np.random.default_rng(seed)

    # Token budget per chunk
    n_blocks = n_splices + 1
    tokens_per_block = max(50, target_tokens // n_blocks)

    accumulated = seed_prompt
    splice_log = []

    for block_i in range(n_blocks):
        # tokenize current text and count tokens
        ids = tokenizer(accumulated, return_tensors="pt").to(model.device)
        cur_len = ids["input_ids"].shape[1]
        if cur_len >= target_tokens:
            break

        budget_this_block = min(tokens_per_block,
                                 target_tokens - cur_len)
        with torch.no_grad():
            out = model.generate(
                **ids,
                max_new_tokens=budget_this_block,
                min_new_tokens=budget_this_block,   # force length, no EOS exit
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_text = tokenizer.decode(out[0][cur_len:], skip_special_tokens=True)
        accumulated += new_text

        # Splice if not the last block
        if block_i < n_blocks - 1:
            phrase = rng.choice(PERTURB_PHRASES)
            topic = rng.choice(PERTURB_TOPICS)
            splice = f"\n\n{phrase}{topic}?\n\n"
            splice_log.append(dict(block=block_i,
                                   token_pos=cur_len + budget_this_block,
                                   text=splice.strip()))
            accumulated += splice

    return accumulated, splice_log


def main():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"Loading {MODEL}...")
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
    print()

    results = {}
    print("=" * 110)
    print(f"  Phase 12 — generating {TARGET_TOKENS}-token sequences at "
          f"perturbation rates {PERTURBATION_RATES}")
    print("=" * 110)

    for n_splices in PERTURBATION_RATES:
        rate_label = f"r={n_splices}"
        print(f"\n[{rate_label}]  generating with {n_splices} splices...")
        t0 = time.time()
        text, splice_log = _build_text_with_splices(model, tokenizer, n_splices)
        n_tokens_full = len(tokenizer(text, return_tensors="pt")["input_ids"][0])
        print(f"  generated text: {n_tokens_full} tokens, "
              f"{n_splices} splices, ⏱ {time.time() - t0:.1f}s")
        print(f"  first 200 chars: {text[:200].replace(chr(10), ' / ')}…")

        # Free generation outputs; reuse the already-loaded model for cascade
        # extraction (avoids OOM from holding two copies of a multi-GB model).
        gc.collect(); torch.cuda.empty_cache()
        cascade = extract_cascade(text, model_name=MODEL,
                                   max_seq_len=min(n_tokens_full, 4096),
                                   preloaded_model=model,
                                   preloaded_tokenizer=tokenizer,
                                   compute_attention=False)
        print(f"  cascade: seq_len={cascade['seq_len']}, "
              f"surprisal mean={np.mean(cascade['surprisal']):.3f} "
              f"std={np.std(cascade['surprisal']):.3f}")

        # residual_norm_peaks → full_analysis
        events = get_event_times(cascade, method='residual_norm_peaks',
                                  prom=0.3)
        if events.size < 20:
            print(f"  insufficient events ({events.size})")
            results[rate_label] = dict(n_splices=n_splices, n_events=int(events.size),
                                        error='insufficient')
            del cascade; gc.collect(); torch.cuda.empty_cache()
            continue
        res = full_analysis(events, label=rate_label, q_max=8,
                             ramanujan_q_max=200)
        res['n_splices'] = n_splices
        res['perturbation_rate_per_kt'] = n_splices / (n_tokens_full / 1000.0)
        res['n_tokens_full'] = int(n_tokens_full)
        res['mean_surprisal'] = float(np.mean(cascade['surprisal']))
        res['std_surprisal'] = float(np.std(cascade['surprisal']))
        res['splice_log'] = splice_log
        results[rate_label] = res

        p = res['primary_nns']; pc = res['pair_correlation']; fan = res['fano_curve']
        print(f"  fingerprint:  best={p['best']}  KS_GUE={p['ks_u']:.4f}  "
              f"mass<.3={p['mass03']:.3f}  F(T=5)={fan.get('F_at_5', float('nan')):.3f}  "
              f"rep_int={pc.get('repulsion_integral', 0):.3f}  "
              f"n_events={res['n_events']}")

        del cascade
        gc.collect(); torch.cuda.empty_cache()

    # ─── Build comparison ─────────────────────────────────────────────────────
    print("\n" + "=" * 110)
    print("Phase 12 — perturbation-rate sweep on Qwen 2.5 3B  (residual_norm_peaks)")
    print("=" * 110)
    print(f"  {'rate':<8}  {'rate/kt':>8}  {'n_ev':>5}  {'best':<7}  "
          f"{'KS_GUE':>7}  {'KS_GOE':>7}  {'mass<.3':>7}  "
          f"{'F(T=1)':>7}  {'F(T=5)':>7}  {'rep_int':>7}")
    print("  " + "-" * 100)
    rate_values, ks_values, rep_values, fano5_values = [], [], [], []
    for rate_label, res in results.items():
        if 'error' in res:
            print(f"  {rate_label:<8}  {res['error']}")
            continue
        p = res['primary_nns']; pc = res['pair_correlation']; fan = res['fano_curve']
        print(f"  {rate_label:<8}  "
              f"{res['perturbation_rate_per_kt']:>8.2f}  "
              f"{res['n_events']:>5}  "
              f"{p['best']:<7}  "
              f"{p['ks_u']:>7.4f}  {p['ks_o']:>7.4f}  {p['mass03']:>7.3f}  "
              f"{fan.get('F_at_1', float('nan')):>7.3f}  "
              f"{fan.get('F_at_5', float('nan')):>7.3f}  "
              f"{pc.get('repulsion_integral', 0):>7.3f}")
        rate_values.append(res['n_splices'])
        ks_values.append(p['ks_u'])
        rep_values.append(pc.get('repulsion_integral', 0))
        fano5_values.append(fan.get('F_at_5', float('nan')))

    # ─── Acceptance check ────────────────────────────────────────────────────
    print("\n" + "=" * 110)
    print("PLANAT HYPOTHESIS CHECK")
    print("=" * 110)
    if len(rate_values) == len(PERTURBATION_RATES):
        ks_arr = np.array(ks_values); rep_arr = np.array(rep_values)
        idx_min = int(np.argmin(ks_arr))
        ks_baseline = ks_arr[0]   # r = 0 (no perturbation)
        ks_optimal = ks_arr[idx_min]
        ks_high    = ks_arr[-1]   # heaviest perturbation
        print(f"  KS_GUE @ r=0 (no perturbation):  {ks_baseline:.4f}")
        print(f"  KS_GUE @ r={rate_values[idx_min]} (minimum):       {ks_optimal:.4f}  "
              f"(Δ from baseline: {ks_optimal - ks_baseline:+.4f})")
        print(f"  KS_GUE @ r={rate_values[-1]} (max perturbation): {ks_high:.4f}  "
              f"(Δ from baseline: {ks_high - ks_baseline:+.4f})")
        print(f"  rep_int across rates: {[f'{r:.3f}' for r in rep_arr]}")
        if 0 < idx_min < len(ks_arr) - 1 and ks_optimal < ks_baseline - 0.02 and ks_optimal < ks_high - 0.02:
            print("\n  ✓ PLANAT PREDICTION SUPPORTED")
            print(f"    Optimal perturbation rate r={rate_values[idx_min]} produces cleaner GUE")
            print(f"    than either uninterrupted (r=0) or heavily-perturbed (r={rate_values[-1]}).")
        else:
            print("\n  ✗ PLANAT PREDICTION NOT CLEARLY SUPPORTED")
            print(f"    Either KS_GUE is monotone in r (idx_min={idx_min}, "
                  f"either endpoint), or the trough is not deep enough.")

    # ─── Save JSON ───────────────────────────────────────────────────────────
    def _trim(res):
        if 'error' in res: return res
        return dict(label=res['label'], n_events=res['n_events'],
                    n_splices=res['n_splices'],
                    perturbation_rate_per_kt=res['perturbation_rate_per_kt'],
                    n_tokens_full=res['n_tokens_full'],
                    mean_surprisal=res['mean_surprisal'],
                    std_surprisal=res['std_surprisal'],
                    primary_nns=res['primary_nns'],
                    fingerprint_vector=res['fingerprint_vector'],
                    fano_summary={k: res['fano_curve'].get(k)
                                   for k in ('F_at_1', 'F_at_5', 'F_at_20',
                                             'mean_sp', 'duration')},
                    pair_correlation_summary={k: res['pair_correlation'].get(k)
                                               for k in ('R2_at_0_1', 'R2_at_1',
                                                         'repulsion_integral')},
                    ramanujan_summary={k: res['ramanujan'].get(k)
                                        for k in ('peak_q', 'top10_q', 'mode')},
                    splice_log=res.get('splice_log'))
    with open(os.path.join(DATA, "phase12_planat.json"), 'w') as f:
        json.dump({k: _trim(v) for k, v in results.items()}, f,
                  indent=2, default=str)
    print(f"\n  → data/phase12_planat.json")

    # ─── Plot ────────────────────────────────────────────────────────────────
    if rate_values:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        ax = axes[0]
        ax.plot(rate_values, ks_values, 'C0o-', lw=2, ms=8,
                label='KS_GUE (lower = closer to Wigner)')
        ax.set_xlabel('# perturbation splices in 2048-token window')
        ax.set_ylabel('KS_GUE')
        ax.set_title('Planat hypothesis: KS_GUE vs perturbation rate')
        ax.grid(True, alpha=0.3); ax.legend(fontsize=9)

        ax = axes[1]
        ax.plot(rate_values, rep_values, 'C2o-', lw=2, ms=8,
                label='repulsion integral')
        ax.plot(rate_values, fano5_values, 'C1s-', lw=2, ms=8,
                label='F(T=5)')
        ax.axhline(1.0, color='gray', ls='--', lw=0.8, label='Poisson F=1')
        ax.set_xlabel('# perturbation splices')
        ax.set_ylabel('value')
        ax.set_title('Companion fingerprint metrics')
        ax.grid(True, alpha=0.3); ax.legend(fontsize=9)
        fig.suptitle(f"Phase 12: Qwen 2.5 3B, residual_norm_peaks, {TARGET_TOKENS}-token windows")
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "39_phase12_planat.png"), dpi=120)
        plt.close(fig)
        print(f"  → plots/39_phase12_planat.png")


if __name__ == '__main__':
    main()
