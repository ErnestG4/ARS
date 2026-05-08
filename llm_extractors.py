"""
llm_extractors.py — Attention-based LLM extractors for Phase 16A.

Operate on a stored cascade dict (from llm_cascade.extract_cascade with
keep_attention=True).  All extractors output sorted t_k_out (np.float64
array) — token positions where the relevant event occurs.

Six extractors:

    residual_norm_peaks     — find_peaks on per-token residual norm
                              (Phase 10/11 control; expected BR_artifact)
    attention_entropy_peaks — find_peaks on per-token attention entropy
                              (alternate continuous signal)
    attention_target_jumps  — events where argmax-attention target jumps
                              by ≥ Δ tokens between consecutive query positions
                              (by-construction discrete events)
    attention_sink_events   — events where attention mass on the first
                              N_sink tokens (BOS / system) exceeds
                              moving-mean + k·σ
                              (by-construction)
    layer_kl_divergence_events — events where KL(att[L] || att[L+1])
                              exceeds moving-mean + k·σ summed over layers
                              (by-construction; needs full attention tensor)
    per_turn_attention_focus — one event per generated turn marking the
                              centroid token of attention
                              (multi-turn only; by-construction)
"""
from __future__ import annotations
import numpy as np
from typing import Optional


def _moving_mean_std(x, window=50):
    """Sliding-window mean and std (centered, edge-clamped)."""
    x = np.asarray(x, dtype=np.float64)
    if x.size <= window:
        return np.full_like(x, x.mean()), np.full_like(x, x.std() + 1e-9)
    pad = window // 2
    xp = np.pad(x, pad, mode='edge')
    cumsum = np.cumsum(xp)
    cumsq = np.cumsum(xp * xp)
    n = window
    mean = (cumsum[n:n + x.size] - cumsum[:x.size]) / n
    sq = (cumsq[n:n + x.size] - cumsq[:x.size]) / n
    std = np.sqrt(np.maximum(sq - mean * mean, 1e-18))
    return mean, std


def extract_residual_norm_peaks(cascade: dict, prominence: float = 0.3) -> np.ndarray:
    """Phase 10/11 control: find_peaks on final-layer residual norm."""
    from scipy.signal import find_peaks
    norms = np.asarray(cascade['hidden_norms'], dtype=np.float64)[-1, 1:]
    if norms.size < 5: return np.zeros(0)
    peaks, _ = find_peaks(norms, prominence=prominence)
    return peaks.astype(np.float64)


def extract_attention_entropy_peaks(cascade: dict, prominence: float = 0.3) -> np.ndarray:
    """Find peaks on per-token mean attention entropy (averaged over
    layers and heads)."""
    from scipy.signal import find_peaks
    if 'attn_entropy' not in cascade or cascade['attn_entropy'].size == 0:
        return np.zeros(0)
    ent = np.asarray(cascade['attn_entropy'], dtype=np.float64)
    # Shape: [n_layers, n_heads, T] — average over layers & heads
    mean_ent = ent.reshape(-1, ent.shape[-1]).mean(axis=0)
    if mean_ent.size < 5: return np.zeros(0)
    peaks, _ = find_peaks(mean_ent, prominence=prominence * mean_ent.std())
    return peaks.astype(np.float64)


def extract_attention_target_jumps(cascade: dict, delta_tokens: int = 16,
                                    layer: int = -1) -> np.ndarray:
    """Events at query positions where the argmax-attention target jumps
    by ≥ delta_tokens between consecutive queries.  By-construction discrete.

    Requires `attentions` to be present (kept via keep_attention=True).
    """
    if 'attentions' not in cascade or not cascade['attentions']:
        return np.zeros(0)
    a = cascade['attentions'][layer]      # [heads, T, T] for the chosen layer
    if a.ndim != 3: return np.zeros(0)
    # For each query position, mean-over-heads attention distribution
    a_mean = a.mean(axis=0)                # [T, T]
    targets = a_mean.argmax(axis=1)        # [T]
    diffs = np.abs(np.diff(targets))
    jumps = np.where(diffs >= delta_tokens)[0] + 1
    return jumps.astype(np.float64)


def extract_attention_sink_events(cascade: dict, n_sink: int = 4,
                                   k: float = 1.0,
                                   layer: int = -1,
                                   window: int = 50) -> np.ndarray:
    """Events where attention mass on first n_sink tokens exceeds
    moving-mean + k·σ.  Captures attention-sink dynamics."""
    if 'attentions' not in cascade or not cascade['attentions']:
        return np.zeros(0)
    a = cascade['attentions'][layer]      # [heads, T, T]
    if a.ndim != 3 or a.shape[-1] <= n_sink: return np.zeros(0)
    a_mean = a.mean(axis=0)                # [T, T] — query × key
    sink_mass = a_mean[:, :n_sink].sum(axis=1)   # [T]
    if sink_mass.size < window + 5: return np.zeros(0)
    mu, sd = _moving_mean_std(sink_mass, window=window)
    above = sink_mass > (mu + k * sd)
    if above.sum() < 2: return np.zeros(0)
    transitions = np.diff(above.astype(np.int8))
    upcross = np.where(transitions == 1)[0] + 1
    return upcross.astype(np.float64)


def extract_attention_argmax_sink(cascade: dict, n_sink: int = 4,
                                   layer: int = -1) -> np.ndarray:
    """Events at token positions where argmax-attention target IS a sink
    (BOS / system) token.  Categorical event detection — no continuous-
    signal threshold, no autocorrelated trace.  Distinct from
    threshold_crossing on continuous signals."""
    if 'attentions' not in cascade or not cascade['attentions']:
        return np.zeros(0)
    a = cascade['attentions'][layer]
    if a.ndim != 3 or a.shape[-1] <= n_sink:
        return np.zeros(0)
    a_mean = a.mean(axis=0)                    # [T, T] query × key
    targets = a_mean.argmax(axis=1)            # [T]
    is_sink = targets < n_sink
    events = np.where(is_sink)[0]
    return events.astype(np.float64)


def extract_attention_sink_residency_runs(cascade: dict, n_sink: int = 4,
                                           theta: float = 0.3,
                                           min_run_length: int = 3,
                                           layer: int = -1) -> np.ndarray:
    """Events at the **start** of contiguous runs where attention mass
    on sink tokens ≥ θ for ≥ min_run_length consecutive tokens.
    Run-onset detection — duration-conditional, distinct from
    point-threshold upcrossings."""
    if 'attentions' not in cascade or not cascade['attentions']:
        return np.zeros(0)
    a = cascade['attentions'][layer]
    if a.ndim != 3 or a.shape[-1] <= n_sink:
        return np.zeros(0)
    a_mean = a.mean(axis=0)
    sink_mass = a_mean[:, :n_sink].sum(axis=1)
    above = sink_mass >= theta
    if above.sum() < min_run_length:
        return np.zeros(0)
    # Identify run boundaries
    diff = np.diff(np.concatenate([[False], above, [False]]).astype(np.int8))
    starts = np.where(diff == 1)[0]
    ends   = np.where(diff == -1)[0]
    long_runs = (ends - starts) >= min_run_length
    return starts[long_runs].astype(np.float64)


def extract_attention_multi_head_sink_consensus(cascade: dict,
                                                  n_sink: int = 4,
                                                  consensus_frac: float = 0.5,
                                                  layer: int = -1) -> np.ndarray:
    """Events at positions where ≥ ⌈H·consensus_frac⌉ of the H attention
    heads concentrate argmax on sink tokens simultaneously.  Multi-head
    consensus — operates on per-head distribution, not aggregated trace."""
    if 'attentions' not in cascade or not cascade['attentions']:
        return np.zeros(0)
    a = cascade['attentions'][layer]            # [heads, T, T]
    if a.ndim != 3 or a.shape[-1] <= n_sink:
        return np.zeros(0)
    H = a.shape[0]
    M = int(np.ceil(consensus_frac * H))
    targets = a.argmax(axis=2)                  # [heads, T]
    sink_per_head = targets < n_sink            # [heads, T]
    consensus_count = sink_per_head.sum(axis=0) # [T]
    is_consensus = consensus_count >= M
    return np.where(is_consensus)[0].astype(np.float64)


def extract_layer_kl_divergence_events(cascade: dict, k: float = 1.0,
                                        window: int = 50) -> np.ndarray:
    """Events where summed KL divergence between consecutive layers'
    per-query attention distributions exceeds moving-mean + k·σ.
    By-construction discrete."""
    if 'attentions' not in cascade or len(cascade['attentions']) < 2:
        return np.zeros(0)
    atts = cascade['attentions']
    # Shape per layer: [heads, T, T]
    L = len(atts)
    T = atts[0].shape[-1]
    kl_per_t = np.zeros(T, dtype=np.float64)
    eps = 1e-9
    for l in range(L - 1):
        a1 = atts[l].mean(axis=0)         # [T, T]
        a2 = atts[l + 1].mean(axis=0)
        # Per-query KL: Σ a1 log(a1 / a2)
        kl = np.sum(a1 * (np.log(a1 + eps) - np.log(a2 + eps)), axis=1)  # [T]
        kl_per_t += np.maximum(kl, 0)
    if kl_per_t.size < window + 5: return np.zeros(0)
    mu, sd = _moving_mean_std(kl_per_t, window=window)
    above = kl_per_t > (mu + k * sd)
    if above.sum() < 2: return np.zeros(0)
    transitions = np.diff(above.astype(np.int8))
    upcross = np.where(transitions == 1)[0] + 1
    return upcross.astype(np.float64)


# ─── Registry ────────────────────────────────────────────────────────────────

LLM_EXTRACTORS = {
    'residual_norm_peaks':                   extract_residual_norm_peaks,
    'attention_entropy_peaks':               extract_attention_entropy_peaks,
    'attention_target_jumps':                extract_attention_target_jumps,
    'attention_sink_events':                 extract_attention_sink_events,
    'layer_kl_divergence_events':            extract_layer_kl_divergence_events,
    'attention_argmax_sink':                 extract_attention_argmax_sink,
    'attention_sink_residency_runs':         extract_attention_sink_residency_runs,
    'attention_multi_head_sink_consensus':   extract_attention_multi_head_sink_consensus,
}


def extract_llm(cascade, name: str, **kwargs):
    if name not in LLM_EXTRACTORS:
        raise ValueError(f"unknown LLM extractor: {name!r}")
    out = LLM_EXTRACTORS[name](cascade, **kwargs)
    return np.sort(np.asarray(out, dtype=np.float64))


__all__ = list(LLM_EXTRACTORS.keys()) + ['extract_llm', 'LLM_EXTRACTORS']
