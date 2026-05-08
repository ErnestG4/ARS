"""
Phase 17 σ̂ extractor × architecture matrix — Mistral 7B addon.

The original matrix run OOM'd on Mistral 7B due to GPU fragmentation
left over from the prior three model loads.  Standalone fresh-process
run to fill in the Mistral row.
"""
from __future__ import annotations
import gc
import os
import sys
import time

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile
from bulk_recovery import recover_uniform_jitter_sigma

DATA = os.path.join(THIS_DIR, "data")
N_TARGET = 1000
Q_MAX = 30
MIN_EVENTS = 30
MAX_SEQ_LEN = 1024

EXTRACTOR_PANEL = [
    ("residual_norm_peaks",                "find_peaks"),
    ("attention_entropy_peaks",            "find_peaks"),
    ("layer_kl_divergence_events",         "threshold_crossing"),
    ("attention_target_jumps",             "by_construction"),
    ("attention_sink_events",              "by_construction"),
    ("attention_argmax_sink",              "by_construction"),
    ("attention_multi_head_sink_consensus","by_construction"),
]


def main():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from llm_cascade import extract_cascade, NATURAL_TEXT
    from llm_extractors import LLM_EXTRACTORS

    display = "Mistral-7B-v0.1"
    model_name = "mistralai/Mistral-7B-v0.1"
    print(f"Loading {display}...")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="cuda",
        trust_remote_code=True,
        attn_implementation="eager",
    )
    cascade = extract_cascade(NATURAL_TEXT,
                              model_name=model_name,
                              max_seq_len=MAX_SEQ_LEN,
                              compute_attention=True,
                              keep_attention=True,
                              preloaded_model=model,
                              preloaded_tokenizer=tok)
    print(f"  forward done ({time.time() - t0:.0f}s)")

    rows = []
    for ext_name, ext_family in EXTRACTOR_PANEL:
        try:
            extractor_fn = LLM_EXTRACTORS[ext_name]
            events = extractor_fn(cascade)
        except Exception as e:
            print(f"  {ext_name:<40}  failed: {type(e).__name__}: {e}")
            rows.append(dict(label=display, arch=display, arch_family=display,
                             n_params=7.0e9, extractor=ext_name,
                             extractor_family=ext_family, n=0,
                             sigma_hat=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                             ci_width=np.nan, flagged=True,
                             rep_int_q_median=np.nan,
                             error=f"{type(e).__name__}: {e}"))
            continue

        if events is None or len(events) < 50:
            print(f"  {ext_name:<40}  underpowered (n="
                  f"{0 if events is None else len(events)})")
            rows.append(dict(label=display, arch=display, arch_family=display,
                             n_params=7.0e9, extractor=ext_name,
                             extractor_family=ext_family,
                             n=int(0 if events is None else len(events)),
                             sigma_hat=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                             ci_width=np.nan, flagged=True,
                             rep_int_q_median=np.nan,
                             error="underpowered"))
            continue

        j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
        sigma_hat, (lo, hi), flagged = recover_uniform_jitter_sigma(j)
        well = j[~j["underpowered"]]
        rep_med = float(well["rep_int_q"].median()) if len(well) else float("nan")
        print(f"  {ext_name:<40}  n={len(events):>4}  "
              f"σ̂={sigma_hat:.3f}  CI=[{lo:.3f},{hi:.3f}]  "
              f"rep_int_q.med={rep_med:.4f}  flagged={flagged}")
        rows.append(dict(label=display, arch=display, arch_family=display,
                         n_params=7.0e9, extractor=ext_name,
                         extractor_family=ext_family, n=int(len(events)),
                         sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                         ci_width=hi - lo, flagged=bool(flagged),
                         rep_int_q_median=rep_med))

    del model, tok, cascade
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

    parquet = os.path.join(DATA, "phase17_extractor_arch_sigma.parquet")
    existing = pd.read_parquet(parquet)
    keep = existing[existing["arch"] != display].copy()
    merged = pd.concat([keep, pd.DataFrame(rows)], ignore_index=True)
    merged.to_parquet(parquet)
    print(f"\n  → {parquet} ({len(merged)} rows)")


if __name__ == "__main__":
    main()
