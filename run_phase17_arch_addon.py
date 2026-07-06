"""
Phase 17 Tier 4 follow-up — third-architecture addon.

Phi-3-mini-4k-instruct hit a transformers/rope_scaling KeyError on
the initial cross-architecture run.  This addon runs the third
architecture as TinyLlama-1.1B-Chat-v1.0 (Llama-architecture, Phase 11
cached) and merges into the existing parquet.
"""
from __future__ import annotations
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
Q_MAX = 30
MIN_EVENTS = 30


def run_one(display_name: str, model_name: str, n_params: float,
            family: str) -> dict:
    from llm_cascade import extract_cascade, NATURAL_TEXT
    from llm_extractors import extract_residual_norm_peaks
    print(f"  {display_name:<30}  loading...", flush=True)
    t0 = time.time()
    cascade = extract_cascade(NATURAL_TEXT, model_name=model_name,
                              max_seq_len=1024, compute_attention=False)
    events = extract_residual_norm_peaks(cascade)
    j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    sigma_hat, (lo, hi), flagged = recover_uniform_jitter_sigma(j)
    print(f"  {display_name:<30}  n={len(events):>4}  "
          f"σ̂={sigma_hat:.3f}  CI=[{lo:.3f}, {hi:.3f}]  "
          f"flagged={flagged}  ⏱ {time.time() - t0:.0f}s")
    return dict(label=display_name, model_name=model_name, family=family,
                n_params=n_params, n=int(len(events)),
                sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                ci_width=hi - lo, flagged=bool(flagged))


def main():
    new_row = run_one("TinyLlama-1.1B-Chat",
                      "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                      1.1e9, "Llama")
    existing = pd.read_parquet(os.path.join(DATA, "phase17_arch_invariance.parquet"))
    # Drop any prior row for this label / drop the failed Phi-3 row
    keep = existing[~existing["label"].isin(
        ["TinyLlama-1.1B-Chat", "Phi-3-mini-4k-instruct"])]
    merged = pd.concat([keep, pd.DataFrame([new_row])], ignore_index=True)
    merged.to_parquet(os.path.join(DATA, "phase17_arch_invariance.parquet"))
    print(f"\n  → data/phase17_arch_invariance.parquet ({len(merged)} rows)")


if __name__ == "__main__":
    main()
