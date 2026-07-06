"""
Phase 17 Tier 4 follow-up — Cross-architecture σ̂ recovery.

Tests whether the σ̂ ≈ 0.065 from Tier 4 (Qwen 2.5 3B,
residual_norm_peaks, natural stimulus) is architecture-invariant
across autoregressive transformers.  Extends the same matched-panel
test that established BR_artifact-classification invariance in
Phase 11 / §7.ter.18 to the σ̂-resolution introduced by Phase 17.

Panel (Phase 11 cached models — substitutes for the originally
specified Llama 3.2 3B Instruct + Mistral 7B v0.3, which are not
locally cached and require HF auth):
  - Qwen2.5-3B               (3B, fp16)
  - Phi-3-mini-4k-instruct   (3.8B, fp16)
  - Mistral-7B-v0.1          (7B, fp16)

Pipeline per architecture:
  NATURAL_TEXT → extract_cascade(model_name, fp16, eager attn)
              → extract_residual_norm_peaks
              → joint_q_profile (q_max=30)
              → recover_uniform_jitter_sigma → σ̂ ± 95% CI

Sanity controls (run first, priority): synthetic uniform_jitter
σ ∈ {0.10, 0.15} to verify the estimator is unchanged from Tier 4
calibrator results.

Output:
  data/phase17_arch_invariance.parquet
  plots/49c_phase17_arch_invariance.png
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

ARCH_PANEL = [
    # (display name, hf model_name, parameters, family)
    ("Qwen2.5-3B",                "Qwen/Qwen2.5-3B",                3.0e9, "Qwen"),
    ("Phi-3-mini-4k-instruct",    "microsoft/Phi-3-mini-4k-instruct", 3.8e9, "Phi"),
    ("Mistral-7B-v0.1",           "mistralai/Mistral-7B-v0.1",      7.0e9, "Mistral"),
]


# ─── Sanity controls ─────────────────────────────────────────────────────────

def run_synthetic_control(sigma: float, seed: int = 0) -> dict:
    t = generate("uniform_jitter", dict(sigma=sigma),
                 n_events=N_TARGET, seed=seed)
    j = joint_q_profile(t, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    sigma_hat, (lo, hi), flagged = recover_uniform_jitter_sigma(j)
    return dict(label=f"synthetic_uniform_{sigma}", family="synthetic_control",
                truth=sigma, sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                ci_width=hi - lo, flagged=bool(flagged), n=int(len(t)))


# ─── Per-architecture σ̂ recovery ─────────────────────────────────────────────

def run_architecture(display_name: str, model_name: str, params: float,
                     family: str) -> dict:
    """Forward NATURAL_TEXT through the model, extract residual_norm_peaks,
    run joint_q_profile + σ̂ recovery, return one row.  Frees model+CUDA
    memory after each call."""
    from llm_cascade import extract_cascade, NATURAL_TEXT
    from llm_extractors import extract_residual_norm_peaks

    print(f"\n  {display_name:<30}  loading...", flush=True)
    t0 = time.time()
    cascade = extract_cascade(NATURAL_TEXT, model_name=model_name,
                              max_seq_len=1024, compute_attention=False)
    t_load = time.time() - t0
    events = extract_residual_norm_peaks(cascade)

    # free GPU memory before next architecture loads
    del cascade
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass
    gc.collect()

    if events is None or len(events) < 50:
        print(f"  {display_name:<30}  insufficient events (n="
              f"{0 if events is None else len(events)})")
        return dict(label=display_name, model_name=model_name, family=family,
                    n_params=params, n=0,
                    sigma_hat=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                    ci_width=np.nan, flagged=True, error="insufficient")

    j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    sigma_hat, (lo, hi), flagged = recover_uniform_jitter_sigma(j)
    elapsed = time.time() - t0
    print(f"  {display_name:<30}  n={len(events):>4}  "
          f"σ̂={sigma_hat:.3f}  CI=[{lo:.3f}, {hi:.3f}]  "
          f"flagged={flagged}  ⏱ {elapsed:.0f}s (load+forward {t_load:.0f}s)")
    return dict(label=display_name, model_name=model_name, family=family,
                n_params=params, n=int(len(events)),
                sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                ci_width=hi - lo, flagged=bool(flagged))


# ─── Verdict ─────────────────────────────────────────────────────────────────

def derive_verdict(arch_rows: list[dict]) -> str:
    sigmas = [r["sigma_hat"] for r in arch_rows
              if r["sigma_hat"] is not None and not np.isnan(r["sigma_hat"])]
    if len(sigmas) < 2:
        return "insufficient_data"
    spread = max(sigmas) - min(sigmas)
    # pairwise distances
    pairs = [(i, j, abs(sigmas[i] - sigmas[j]))
             for i in range(len(sigmas)) for j in range(i + 1, len(sigmas))]
    within = sum(1 for *_, d in pairs if d <= 0.02)
    n_pairs = len(pairs)

    if spread <= 0.02:
        return "architecture_invariant"
    elif within == n_pairs - 1 and spread >= 0.05:
        return "partial_invariance"
    elif spread > 0.05:
        return "spread_exceeds_threshold"
    else:
        return "intermediate_spread"


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    t_start = time.time()
    print("=" * 100)
    print("Phase 17 Tier 4 follow-up — cross-architecture σ̂ recovery")
    print("=" * 100)

    rows = []

    # ─── (1) PRIORITY: synthetic controls first ──────────────────────────────
    print("\n[1] Synthetic uniform_jitter controls (sanity check the estimator")
    print("    is unchanged from Tier 4 calibrator)")
    for sigma in (0.10, 0.15):
        c = run_synthetic_control(sigma, seed=0)
        err = abs(c["sigma_hat"] - c["truth"])
        mark = "✓" if err <= 0.02 else "✗"
        print(f"  σ={c['truth']}  σ̂={c['sigma_hat']:.3f}  "
              f"CI=[{c['ci_lo']:.3f}, {c['ci_hi']:.3f}]  |err|={err:.3f}  {mark}")
        rows.append(c)

    sanity_pass = all(
        abs(r["sigma_hat"] - r["truth"]) <= 0.02
        for r in rows if r.get("family") == "synthetic_control"
    )
    if not sanity_pass:
        print("\n  ✗ Synthetic controls failed — estimator changed since Tier 4.")
        print("    Aborting before architecture sweep.  Save what we have.")
        df = pd.DataFrame(rows)
        df.to_parquet(os.path.join(DATA, "phase17_arch_invariance.parquet"))
        return

    print("\n  ✓ Synthetic controls within ±0.02 of truth — estimator OK.")

    # ─── (2) Architecture sweep ──────────────────────────────────────────────
    print("\n[2] Architecture sweep — residual_norm_peaks on NATURAL_TEXT")
    arch_rows = []
    for display_name, model_name, params, family in ARCH_PANEL:
        try:
            r = run_architecture(display_name, model_name, params, family)
        except Exception as e:
            print(f"  {display_name:<30}  failed: {type(e).__name__}: {e}")
            r = dict(label=display_name, model_name=model_name, family=family,
                     n_params=params, n=0, sigma_hat=np.nan, ci_lo=np.nan,
                     ci_hi=np.nan, ci_width=np.nan, flagged=True,
                     error=f"{type(e).__name__}: {e}")
        arch_rows.append(r)
        rows.append(r)
        # free CUDA between architectures
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        gc.collect()

    # ─── (3) Save parquet ────────────────────────────────────────────────────
    df = pd.DataFrame(rows)
    df.to_parquet(os.path.join(DATA, "phase17_arch_invariance.parquet"))
    print(f"\n  → data/phase17_arch_invariance.parquet ({len(df)} rows)")

    # ─── (4) Verdict ─────────────────────────────────────────────────────────
    verdict = derive_verdict(arch_rows)
    print("\n" + "=" * 100)
    print("VERDICT")
    print("=" * 100)
    valid = [r for r in arch_rows
             if r.get("sigma_hat") is not None and not np.isnan(r["sigma_hat"])]
    if valid:
        sigmas = [r["sigma_hat"] for r in valid]
        spread = max(sigmas) - min(sigmas)
        print(f"  σ̂ values: " +
              ", ".join(f"{r['label']}={r['sigma_hat']:.3f}" for r in valid))
        print(f"  Spread (max - min): {spread:.3f}")

    verdict_text = {
        "architecture_invariant": (
            "Architecture-invariant.  All three σ̂ within ±0.02 of each "
            "other.  The primes-LLM σ̂ coincidence (Tier 4 §7.ter.23) holds "
            "for autoregressive transformers as a class."),
        "partial_invariance": (
            "Partial invariance — two of three σ̂ within ±0.02; one outlier "
            "≥ 0.05 from the cluster.  Document the outlier; do not retract "
            "the cluster reading."),
        "spread_exceeds_threshold": (
            "Spread > 0.05 across architectures.  The Qwen σ̂ ≈ 0.065 is "
            "model-specific or training-corpus-specific.  The primes-LLM "
            "coincidence is bounded to the architectures where it holds."),
        "intermediate_spread": (
            "Intermediate spread (0.02 < spread ≤ 0.05).  Neither tight "
            "invariance nor a clear outlier — soft architecture-dependence."),
        "insufficient_data": (
            "Insufficient data — fewer than 2 architectures returned a σ̂."),
    }[verdict]
    print(f"  → {verdict}: {verdict_text}")

    # ─── (5) Forest plot ─────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))

    plot_rows = [r for r in rows
                 if r.get("sigma_hat") is not None and not np.isnan(r["sigma_hat"])]
    # Order: synthetic controls first, then architectures by parameter count
    syn = [r for r in plot_rows if r.get("family") == "synthetic_control"]
    arc = sorted([r for r in plot_rows if r.get("family") != "synthetic_control"],
                 key=lambda r: r.get("n_params", 0))
    plot_rows = syn + arc

    ys = np.arange(len(plot_rows))
    sigmas = np.array([r["sigma_hat"] for r in plot_rows])
    los = np.array([r["ci_lo"] for r in plot_rows])
    his = np.array([r["ci_hi"] for r in plot_rows])
    family_colors = {
        "synthetic_control": "#2ca02c",
        "Qwen": "#9467bd",
        "Phi": "#1f77b4",
        "Mistral": "#d62728",
    }
    colors = [family_colors.get(r.get("family"), "#777777") for r in plot_rows]

    ax.errorbar(sigmas, ys, xerr=[sigmas - los, his - sigmas],
                fmt="none", ecolor="gray", capsize=4, lw=1.2)
    for y, (sig, c, r) in enumerate(zip(sigmas, colors, plot_rows)):
        ax.scatter([sig], [y], c=c, s=110, zorder=3,
                   edgecolors="black", linewidths=1)

    # Truth markers for synthetic controls
    for y, r in enumerate(plot_rows):
        if r.get("truth") is not None:
            ax.scatter([r["truth"]], [y], marker="|", c="black",
                       s=300, lw=2, zorder=4)

    # Reference shading: Tier 4 primes-LLM cluster region [0.04, 0.09]
    ax.axvspan(0.04, 0.09, color="#e0d5f5", alpha=0.5, zorder=0,
               label="Tier 4 primes-LLM cluster [0.04, 0.09]")

    ax.set_yticks(ys)
    ax.set_yticklabels([r["label"] for r in plot_rows], fontsize=9)
    ax.set_xlabel("σ̂  (uniform_jitter parameter)")
    ax.set_xlim(-0.03, 0.30)
    ax.axvline(0.0, color="gray", ls=":", lw=0.8)
    ax.grid(True, axis="x", alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(f"Phase 17 Tier 4 follow-up — cross-architecture σ̂ "
                 f"(verdict: {verdict})")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "49c_phase17_arch_invariance.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/49c_phase17_arch_invariance.png")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
