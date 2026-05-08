"""
Phase 17 σ̂ extractor × architecture matrix — diagnostic for the
metric-saturation finding (D, §7.ter.23).

Hypothesis (the predictive test):
  - find_peaks-family extractors (residual_norm_peaks,
    attention_entropy_peaks): σ̂ should saturate per architecture
    (metric-blind regime — gap distribution geometry dominates).
  - threshold-crossing (layer_kl_divergence_events): predicted to
    behave similarly — moving-mean+k·σ threshold induces a
    density-determined event set.
  - by-construction discrete (attention_target_jumps, _sink_events,
    _argmax_sink, _multi_head_sink_consensus): events triggered by
    architecture-specific attention conditions; σ̂ should vary
    meaningfully across architectures if the recovery is reading
    real model differences.

If the prediction holds (find_peaks σ̂ collapses across arches,
by-construction σ̂ varies across arches), §7.ter.19's
"find_peaks-is-doing-the-work" mechanism is confirmed at σ̂
resolution and the metric-saturation interpretation of finding (D)
is empirically validated.

If by-construction σ̂ ALSO collapses, the input-text autocorrelation
dominates regardless of extraction mechanism — a stronger version
of §7.ter.19.

Skips `attention_sink_residency_runs` per Phase 16A.2's underpowered
flag.

Output:
  data/phase17_extractor_arch_sigma.parquet
  plots/49d_phase17_extractor_arch_heatmap.png
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
MAX_SEQ_LEN = 1024

# Architecture panel — same as Phase 17 Tier 4 follow-up.  Phi-3 needs
# trust_remote_code=False to bypass the cached remote modeling code's
# rope_scaling['type'] KeyError.
ARCH_PANEL = [
    ("Qwen2.5-3B",                "Qwen/Qwen2.5-3B",                     True,  3.0e9),
    ("Phi-3-mini-4k-instruct",    "microsoft/Phi-3-mini-4k-instruct",    False, 3.8e9),
    ("TinyLlama-1.1B-Chat",       "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  True,  1.1e9),
    ("Mistral-7B-v0.1",           "mistralai/Mistral-7B-v0.1",           True,  7.0e9),
]

# Categorisation of the 7 extractors per the saturation hypothesis.
# residency_runs intentionally skipped (Phase 16A.2 underpowered).
EXTRACTOR_PANEL = [
    # (name, family)
    ("residual_norm_peaks",                "find_peaks"),
    ("attention_entropy_peaks",            "find_peaks"),
    ("layer_kl_divergence_events",         "threshold_crossing"),
    ("attention_target_jumps",             "by_construction"),
    ("attention_sink_events",              "by_construction"),
    ("attention_argmax_sink",              "by_construction"),
    ("attention_multi_head_sink_consensus","by_construction"),
]


def run_synthetic_control(sigma: float, seed: int = 0) -> dict:
    t = generate("uniform_jitter", dict(sigma=sigma),
                 n_events=N_TARGET, seed=seed)
    j = joint_q_profile(t, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    sigma_hat, (lo, hi), flagged = recover_uniform_jitter_sigma(j)
    well = j[~j["underpowered"]]
    rep_med = float(well["rep_int_q"].median()) if len(well) else float("nan")
    return dict(label=f"synthetic_uniform_{sigma}", arch="synthetic",
                arch_family="synthetic", n_params=np.nan,
                extractor=f"σ={sigma}", extractor_family="synthetic_control",
                truth=sigma, n=int(len(t)),
                sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                ci_width=hi - lo, flagged=bool(flagged),
                rep_int_q_median=rep_med)


def run_architecture_extractors(display: str, model_name: str,
                                trust_remote: bool, n_params: float):
    """One forward pass per architecture with compute_attention=True;
    apply all extractors to the same cascade.  Returns list of rows."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from llm_cascade import extract_cascade, NATURAL_TEXT
    from llm_extractors import LLM_EXTRACTORS

    print(f"\n  {display:<28}  loading "
          f"(trust_remote_code={trust_remote})...", flush=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=trust_remote)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="cuda",
        trust_remote_code=trust_remote,
        attn_implementation="eager",
    )
    cascade = extract_cascade(NATURAL_TEXT,
                              model_name=model_name,
                              max_seq_len=MAX_SEQ_LEN,
                              compute_attention=True,
                              keep_attention=True,
                              preloaded_model=model,
                              preloaded_tokenizer=tok)
    t_forward = time.time() - t0
    print(f"  {display:<28}  forward done ({t_forward:.0f}s)")

    rows = []
    for ext_name, ext_family in EXTRACTOR_PANEL:
        try:
            extractor_fn = LLM_EXTRACTORS[ext_name]
            events = extractor_fn(cascade)
        except Exception as e:
            print(f"    {ext_name:<40}  failed: {type(e).__name__}: {e}")
            rows.append(dict(label=display, arch=display, arch_family=ext_family,
                             n_params=n_params, extractor=ext_name,
                             extractor_family=ext_family, n=0,
                             sigma_hat=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                             ci_width=np.nan, flagged=True,
                             rep_int_q_median=np.nan,
                             error=f"{type(e).__name__}: {e}"))
            continue

        if events is None or len(events) < 50:
            print(f"    {ext_name:<40}  underpowered (n="
                  f"{0 if events is None else len(events)})")
            rows.append(dict(label=display, arch=display, arch_family=ext_family,
                             n_params=n_params, extractor=ext_name,
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
        print(f"    {ext_name:<40}  n={len(events):>4}  "
              f"σ̂={sigma_hat:.3f}  CI=[{lo:.3f},{hi:.3f}]  "
              f"rep_int_q.med={rep_med:.4f}")
        rows.append(dict(label=display, arch=display, arch_family=display,
                         n_params=n_params, extractor=ext_name,
                         extractor_family=ext_family, n=int(len(events)),
                         sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                         ci_width=hi - lo, flagged=bool(flagged),
                         rep_int_q_median=rep_med))

    # free CUDA after this architecture
    del model, tok, cascade
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()
    elapsed = time.time() - t0
    print(f"  {display:<28}  arch total {elapsed:.0f}s")
    return rows


def render_heatmap(df: pd.DataFrame, out_path: str):
    arc = df[df["extractor_family"] != "synthetic_control"].copy()
    archs = list(arc["arch"].unique())
    extractors = [e for e, _ in EXTRACTOR_PANEL]
    families = {e: f for e, f in EXTRACTOR_PANEL}

    M_sigma = np.full((len(archs), len(extractors)), np.nan)
    M_n = np.zeros((len(archs), len(extractors)), dtype=int)
    for i, a in enumerate(archs):
        for k, e in enumerate(extractors):
            row = arc[(arc["arch"] == a) & (arc["extractor"] == e)]
            if len(row):
                M_sigma[i, k] = row["sigma_hat"].iloc[0]
                M_n[i, k] = int(row["n"].iloc[0])

    fig, axes = plt.subplots(1, 2, figsize=(15, 5),
                             gridspec_kw={"width_ratios": [3, 1]})
    ax = axes[0]
    im = ax.imshow(M_sigma, aspect="auto", cmap="viridis",
                   vmin=0.0, vmax=0.20)
    ax.set_xticks(range(len(extractors)))
    ax.set_xticklabels(extractors, rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(len(archs)))
    ax.set_yticklabels(archs, fontsize=10)
    for i in range(len(archs)):
        for k in range(len(extractors)):
            v = M_sigma[i, k]
            if np.isnan(v):
                txt = "—"
                color = "white"
            else:
                txt = f"{v:.3f}\nn={M_n[i,k]}"
                color = "white" if v < 0.10 else "black"
            ax.text(k, i, txt, ha="center", va="center",
                    fontsize=8, color=color)
    fam_lines = {}
    for k, e in enumerate(extractors):
        fam_lines.setdefault(families[e], []).append(k)
    ax.set_xlabel("extractor")
    ax.set_title("σ̂ per (architecture × extractor) — "
                 "rows: arch, cols: extractor (grouped by family)")
    fig.colorbar(im, ax=ax, label="σ̂")

    # Per-extractor σ̂ spread across architectures
    ax2 = axes[1]
    fam_color = {"find_peaks": "#1f77b4",
                 "threshold_crossing": "#9467bd",
                 "by_construction": "#d62728"}
    spreads = []
    for e in extractors:
        col = arc[arc["extractor"] == e]["sigma_hat"].dropna()
        spreads.append(col.max() - col.min() if len(col) >= 2 else np.nan)
    colors = [fam_color[families[e]] for e in extractors]
    ax2.barh(range(len(extractors)), spreads, color=colors)
    ax2.set_yticks(range(len(extractors)))
    ax2.set_yticklabels(extractors, fontsize=8)
    ax2.set_xlabel("σ̂ spread (max − min) across archs")
    ax2.axvline(0.02, color="gray", ls=":", lw=1,
                label="≤ 0.02: model-intrinsic threshold")
    ax2.axvline(0.05, color="gray", ls="-", lw=1,
                label="> 0.05: extractor-conditional threshold")
    ax2.legend(fontsize=7, loc="lower right")
    ax2.set_title("Per-extractor σ̂ spread")
    # Family-coloured legend
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=c, label=f) for f, c in fam_color.items()]
    ax2.legend(handles=handles, loc="lower right", fontsize=7)

    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main():
    t_start = time.time()
    print("=" * 90)
    print("Phase 17 σ̂ extractor × architecture matrix")
    print("=" * 90)

    rows = []

    # ─── (1) Synthetic controls ─────────────────────────────────────────────
    print("\n[1] Synthetic uniform_jitter controls")
    for sigma in (0.10, 0.15):
        c = run_synthetic_control(sigma, seed=0)
        err = abs(c["sigma_hat"] - c["truth"])
        mark = "✓" if err <= 0.02 else "✗"
        print(f"  σ={c['truth']}  σ̂={c['sigma_hat']:.3f}  "
              f"CI=[{c['ci_lo']:.3f}, {c['ci_hi']:.3f}]  "
              f"|err|={err:.3f}  {mark}")
        rows.append(c)
        if err > 0.02:
            print("  ✗ control failed — abort")
            return
    print("  ✓ Synthetic controls within ±0.02 of truth — estimator OK.")

    # ─── (2) Per-architecture extractor sweep ───────────────────────────────
    print("\n[2] Architecture × extractor sweep")
    for display, mn, trc, params in ARCH_PANEL:
        try:
            arch_rows = run_architecture_extractors(display, mn, trc, params)
            rows.extend(arch_rows)
        except Exception as e:
            print(f"  {display:<28}  arch failed: {type(e).__name__}: {e}")
            import traceback; traceback.print_exc()

    # ─── (3) Save parquet ───────────────────────────────────────────────────
    df = pd.DataFrame(rows)
    parquet_path = os.path.join(DATA, "phase17_extractor_arch_sigma.parquet")
    df.to_parquet(parquet_path)
    print(f"\n  → {parquet_path} ({len(df)} rows)")

    # ─── (4) Per-extractor analysis ─────────────────────────────────────────
    arc = df[df["extractor_family"] != "synthetic_control"].copy()
    print("\n" + "=" * 90)
    print("Per-extractor σ̂ across architectures (arch-side spread)")
    print("=" * 90)
    print(f"  {'extractor':<40}  {'family':<22}  spread     verdict")
    extractors = [e for e, _ in EXTRACTOR_PANEL]
    families = {e: f for e, f in EXTRACTOR_PANEL}
    summary = []
    for e in extractors:
        col = arc[arc["extractor"] == e]
        valid = col.dropna(subset=["sigma_hat"])
        if len(valid) < 2:
            print(f"  {e:<40}  {families[e]:<22}  {'(insufficient)':>10}")
            summary.append(dict(extractor=e, family=families[e],
                                spread=np.nan, n_valid=len(valid)))
            continue
        spread = float(valid["sigma_hat"].max() - valid["sigma_hat"].min())
        if spread <= 0.02:
            verdict = "saturated (≤ 0.02)"
        elif spread <= 0.05:
            verdict = "intermediate"
        else:
            verdict = "discriminative (> 0.05)"
        print(f"  {e:<40}  {families[e]:<22}  {spread:.4f}     {verdict}")
        summary.append(dict(extractor=e, family=families[e],
                            spread=spread, n_valid=len(valid)))

    # Family-level verdict
    print("\n" + "=" * 90)
    print("Family-level diagnostic")
    print("=" * 90)
    summary_df = pd.DataFrame(summary).dropna(subset=["spread"])
    by_family = summary_df.groupby("family")["spread"].agg(
        ["mean", "max", "count"])
    print(by_family)

    # ─── (5) Heatmap ────────────────────────────────────────────────────────
    out_plot = os.path.join(PLOTS, "49d_phase17_extractor_arch_heatmap.png")
    render_heatmap(df, out_plot)
    print(f"\n  → {out_plot}")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
