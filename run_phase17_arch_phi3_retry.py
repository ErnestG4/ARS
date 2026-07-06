"""
Phase 17 Tier 4 follow-up — Phi-3 retry.

The original cross-architecture run hit
  KeyError: 'type'
in the cached Phi-3 remote modeling code (rope_scaling["type"] vs the
new "rope_type" key in transformers 5.8).  Fix: load Phi-3 with
trust_remote_code=False so transformers' in-tree Phi3ForCausalLM
(updated for the new rope_scaling format) is used instead of the
out-of-date HF-cached remote code.

Pipeline matches the other three architectures: NATURAL_TEXT →
extract_cascade (preloaded model, fp16, eager attn) →
extract_residual_norm_peaks → joint_q_profile → recover_uniform_jitter_sigma.

Includes synthetic uniform σ=0.10 and σ=0.15 controls as a session-
level estimator-sanity check.

Output:
  - Phi-3 row appended to data/phase17_arch_invariance.parquet
  - plots/49c_phase17_arch_invariance.png re-rendered with 4 rows
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
from field_generator import generate
from bulk_recovery import recover_uniform_jitter_sigma

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
N_TARGET = 1000
Q_MAX = 30
MIN_EVENTS = 30


def run_synthetic_control(sigma: float, seed: int = 0) -> dict:
    t = generate("uniform_jitter", dict(sigma=sigma),
                 n_events=N_TARGET, seed=seed)
    j = joint_q_profile(t, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    sigma_hat, (lo, hi), flagged = recover_uniform_jitter_sigma(j)
    return dict(label=f"synthetic_uniform_{sigma}", family="synthetic_control",
                truth=sigma, sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                ci_width=hi - lo, flagged=bool(flagged), n=int(len(t)),
                n_params=np.nan, model_name=None)


def run_phi3() -> dict:
    """Forward Phi-3-mini-4k-instruct with trust_remote_code=False to
    avoid the cached remote modeling code that reads rope_scaling['type']."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from llm_cascade import extract_cascade, NATURAL_TEXT
    from llm_extractors import extract_residual_norm_peaks

    model_name = "microsoft/Phi-3-mini-4k-instruct"
    print(f"  Phi-3-mini-4k-instruct          loading (trust_remote_code=False)...",
          flush=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="cuda",
        trust_remote_code=False,
        attn_implementation="eager",
    )
    cascade = extract_cascade(NATURAL_TEXT,
                              model_name=model_name,
                              max_seq_len=1024,
                              compute_attention=False,
                              preloaded_model=model,
                              preloaded_tokenizer=tok)
    events = extract_residual_norm_peaks(cascade)

    # free model after extraction
    del model, tok, cascade
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

    j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    sigma_hat, (lo, hi), flagged = recover_uniform_jitter_sigma(j)
    elapsed = time.time() - t0
    print(f"  Phi-3-mini-4k-instruct          n={len(events):>4}  "
          f"σ̂={sigma_hat:.3f}  CI=[{lo:.3f}, {hi:.3f}]  "
          f"flagged={flagged}  ⏱ {elapsed:.0f}s")
    return dict(label="Phi-3-mini-4k-instruct",
                model_name=model_name, family="Phi",
                n_params=3.8e9, n=int(len(events)),
                sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                ci_width=hi - lo, flagged=bool(flagged))


def render_panel(df: pd.DataFrame) -> str:
    """Render the four-row forest plot with primes-LLM cluster shading +
    cross-architecture CI common-overlap shading."""
    syn = df[df["family"] == "synthetic_control"].copy()
    arc = df[df["family"] != "synthetic_control"].copy().sort_values("n_params")
    plot_df = pd.concat([syn, arc], ignore_index=True)

    ys = np.arange(len(plot_df))
    sigmas = plot_df["sigma_hat"].to_numpy()
    los = plot_df["ci_lo"].to_numpy()
    his = plot_df["ci_hi"].to_numpy()
    family_colors = {
        "synthetic_control": "#2ca02c",
        "Qwen": "#9467bd",
        "Llama": "#8c564b",
        "Mistral": "#d62728",
        "Phi": "#1f77b4",
    }
    colors = [family_colors.get(f, "#777") for f in plot_df["family"]]

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    # Tier 4 primes-LLM cluster region
    ax.axvspan(0.04, 0.09, color="#e0d5f5", alpha=0.5, zorder=0,
               label="Tier 4 primes-LLM cluster [0.04, 0.09]")

    # Architecture-CI common-overlap region (across all arch rows)
    if len(arc) >= 2:
        arch_lo = float(arc["ci_lo"].max())
        arch_hi = float(arc["ci_hi"].min())
        if arch_lo < arch_hi:
            ax.axvspan(arch_lo, arch_hi, ymin=0.5, ymax=0.95,
                       color="#9467bd", alpha=0.15, zorder=0,
                       label=f"arch CI common overlap [{arch_lo:.3f}, {arch_hi:.3f}]")
    else:
        arch_lo = arch_hi = float("nan")

    ax.errorbar(sigmas, ys, xerr=[sigmas - los, his - sigmas],
                fmt="none", ecolor="gray", capsize=4, lw=1.2)
    for y, (sig, c) in enumerate(zip(sigmas, colors)):
        ax.scatter([sig], [y], c=c, s=130, zorder=3,
                   edgecolors="black", linewidths=1)

    for y, r in plot_df.iterrows():
        if pd.notna(r.get("truth")):
            ax.scatter([r["truth"]], [y], marker="|", c="black",
                       s=300, lw=2, zorder=4)

    ax.set_yticks(ys)
    ax.set_yticklabels(plot_df["label"], fontsize=10)
    ax.set_xlabel("σ̂  (uniform_jitter parameter)")
    ax.set_xlim(-0.03, 0.30)
    ax.axvline(0.0, color="gray", ls=":", lw=0.8)
    ax.grid(True, axis="x", alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    spread = float(arc["sigma_hat"].max() - arc["sigma_hat"].min())
    ax.set_title(f"Phase 17 Tier 4 follow-up — cross-architecture σ̂  "
                 f"(point spread {spread:.3f}; CI common overlap "
                 f"[{arch_lo:.3f}, {arch_hi:.3f}])")
    fig.tight_layout()
    out = os.path.join(PLOTS, "49c_phase17_arch_invariance.png")
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def main():
    t_start = time.time()
    print("=" * 90)
    print("Phase 17 Tier 4 follow-up — Phi-3 retry")
    print("=" * 90)

    # ─── (1) Synthetic controls ─────────────────────────────────────────────
    print("\n[1] Synthetic uniform_jitter controls")
    new_rows = []
    for sigma in (0.10, 0.15):
        c = run_synthetic_control(sigma, seed=0)
        err = abs(c["sigma_hat"] - c["truth"])
        mark = "✓" if err <= 0.02 else "✗"
        print(f"  σ={c['truth']}  σ̂={c['sigma_hat']:.3f}  "
              f"CI=[{c['ci_lo']:.3f}, {c['ci_hi']:.3f}]  "
              f"|err|={err:.3f}  {mark}")
        if err > 0.02:
            print("\n  ✗ Synthetic control failed — estimator drifted.  "
                  "Aborting Phi-3 run.")
            return

    print("\n  ✓ Synthetic controls within ±0.02 of truth — estimator OK.")

    # ─── (2) Phi-3 forward pass ─────────────────────────────────────────────
    print("\n[2] Phi-3 forward pass (residual_norm_peaks, NATURAL_TEXT)")
    try:
        phi3_row = run_phi3()
    except Exception as e:
        print(f"  Phi-3 failed: {type(e).__name__}: {e}")
        import traceback; traceback.print_exc()
        return

    # ─── (3) Append to existing parquet ─────────────────────────────────────
    parquet = os.path.join(DATA, "phase17_arch_invariance.parquet")
    existing = pd.read_parquet(parquet)
    keep = existing[existing["label"] != "Phi-3-mini-4k-instruct"].copy()
    merged = pd.concat([keep, pd.DataFrame([phi3_row])], ignore_index=True)
    merged.to_parquet(parquet)
    print(f"\n  → {parquet} ({len(merged)} rows)")

    # ─── (4) Re-render forest plot ──────────────────────────────────────────
    out = render_panel(merged)
    print(f"  → {out}")

    # ─── (5) Verdict ────────────────────────────────────────────────────────
    arc = merged[merged["family"] != "synthetic_control"].copy()
    arc_los = arc["ci_lo"].to_numpy()
    arc_his = arc["ci_hi"].to_numpy()
    arc_sigmas = arc["sigma_hat"].to_numpy()
    common_lo = float(arc_los.max())
    common_hi = float(arc_his.min())
    spread = float(arc_sigmas.max() - arc_sigmas.min())
    print("\n" + "=" * 90)
    print("FOUR-ARCHITECTURE PANEL")
    print("=" * 90)
    for _, r in arc.sort_values("n_params").iterrows():
        in_cluster = "in [0.04, 0.09]" if 0.04 <= r["sigma_hat"] <= 0.09 else "outside"
        print(f"  {r['label']:<28}  σ̂={r['sigma_hat']:.3f}  "
              f"CI=[{r['ci_lo']:.3f}, {r['ci_hi']:.3f}]  ({in_cluster})")
    print(f"\n  point-estimate spread (max - min): {spread:.3f}")
    if common_lo < common_hi:
        print(f"  CI common overlap: [{common_lo:.3f}, {common_hi:.3f}]  "
              f"(width {common_hi - common_lo:.3f})")
    else:
        print(f"  No CI common overlap across all four architectures.")

    # Verdict mapping per spec
    cluster_lo, cluster_hi = 0.04, 0.131
    phi3_sig = float(phi3_row["sigma_hat"])
    phi3_lo = float(phi3_row["ci_lo"])
    phi3_hi = float(phi3_row["ci_hi"])
    if cluster_lo <= phi3_sig <= cluster_hi:
        # Inside the existing cluster CI union — strengthen
        print(f"\n  Verdict: Phi-3 σ̂ ({phi3_sig:.3f}) inside "
              f"[{cluster_lo:.3f}, {cluster_hi:.3f}] (existing-CI union) — "
              f"architecture-consistency extends to four architectures; "
              f"§7.ter.23 reading strengthened.")
    else:
        print(f"\n  Verdict: Phi-3 σ̂ ({phi3_sig:.3f}) OUTSIDE "
              f"[{cluster_lo:.3f}, {cluster_hi:.3f}] — architectural outlier; "
              f"document and bound the generalisation claim.")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
