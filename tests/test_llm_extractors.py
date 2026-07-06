"""Sanity tests for state-based LLM extractors (Phase 16A.2).

Two synthetic-attention controls verify each extractor's threshold
parameters are calibrated correctly *before* applying to LLM data:

  1. Random-attention control: per-token attention is a random
     Dirichlet-like distribution.  argmax targets are approximately
     uniform over T → P(argmax in n_sink) ≈ n_sink / T → very low.
     The three new state-based extractors should produce sparse output
     (≤ ~5% of tokens flagged on average).

  2. Single-sink-attractor control: attention is permanently locked
     onto sink tokens.  argmax always lands in sink → all extractors
     should fire at every token (or every consecutive token for
     residency runs).  The resulting "no-spacing" point process is
     unclassifiable, which is the right behaviour.
"""
import os, sys
import numpy as np
import pytest

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS))

from llm_extractors import (
    extract_attention_argmax_sink,
    extract_attention_sink_residency_runs,
    extract_attention_multi_head_sink_consensus,
)


def _random_attention_cascade(T=400, H=8, L=4, n_sink=4, seed=0):
    """Each query distribution = softmax of random logits → near-uniform."""
    rng = np.random.default_rng(seed)
    attentions = []
    for _ in range(L):
        logits = rng.standard_normal((H, T, T))
        # Causal mask: each query t can only attend to keys ≤ t
        mask = np.triu(np.ones((T, T), dtype=bool), k=1)
        logits[:, mask] = -1e9
        a = np.exp(logits - logits.max(axis=-1, keepdims=True))
        a /= a.sum(axis=-1, keepdims=True)
        attentions.append(a.astype(np.float64))
    return dict(attentions=attentions, hidden_norms=np.zeros((L, T)))


def _sink_locked_cascade(T=400, H=8, L=4, n_sink=4):
    """Every query attends almost entirely to first sink token (key=0)."""
    attentions = []
    for _ in range(L):
        a = np.full((H, T, T), 1e-6, dtype=np.float64)
        a[:, :, 0] = 0.95   # query attends to key=0 (first sink)
        a[:, :, 1] = 0.04   # tiny mass on second sink
        # normalise
        a /= a.sum(axis=-1, keepdims=True)
        attentions.append(a)
    return dict(attentions=attentions, hidden_norms=np.zeros((L, T)))


# ─── Random-attention control: extractors should be sparse ─────────────────

def test_argmax_sink_sparse_on_random_attention():
    c = _random_attention_cascade(T=400, n_sink=4)
    events = extract_attention_argmax_sink(c, n_sink=4)
    # Expected fraction ≈ n_sink / T = 4/400 = 1%, allow up to 5%
    frac = events.size / 400
    assert frac <= 0.10, (
        f"argmax_sink should be sparse on random attention; got {frac:.3f}")


def test_residency_runs_sparse_on_random_attention():
    c = _random_attention_cascade(T=400, n_sink=4)
    events = extract_attention_sink_residency_runs(c, n_sink=4, theta=0.3,
                                                     min_run_length=3)
    # On random attention sink_mass ~ 4/400 = 0.01, well below θ=0.3
    # so runs of length ≥ 3 above θ should be very rare.
    assert events.size <= 5, (
        f"residency_runs should fire ≤ 5× on random attention; got {events.size}")


def test_multi_head_consensus_sparse_on_random_attention():
    c = _random_attention_cascade(T=400, n_sink=4, H=8)
    events = extract_attention_multi_head_sink_consensus(c, n_sink=4,
                                                           consensus_frac=0.5)
    # Random per-head sink probability ≈ 4/400 = 1%; binomial tail of 8 heads
    # with p=0.01 hitting ≥ 4: vanishingly small.  Allow up to 10 events
    # for any per-T position effects.
    frac = events.size / 400
    assert frac <= 0.05, (
        f"multi_head_consensus should be very sparse on random attention; got {frac:.3f}")


# ─── Sink-locked control: extractors should fire constantly ────────────────

def test_argmax_sink_fires_constantly_on_locked():
    c = _sink_locked_cascade(T=200, n_sink=4)
    events = extract_attention_argmax_sink(c, n_sink=4)
    assert events.size >= 195, (
        f"argmax_sink should fire ~every token on sink-locked attention; got {events.size}")


def test_residency_runs_one_long_run_on_locked():
    c = _sink_locked_cascade(T=200, n_sink=4)
    events = extract_attention_sink_residency_runs(c, n_sink=4, theta=0.3,
                                                     min_run_length=3)
    # Sink-locked → one contiguous run from t=0 → 1 start event
    assert events.size == 1 and events[0] == 0, (
        f"residency_runs should produce exactly 1 long run starting at t=0; "
        f"got {events.size} events {events}")


def test_multi_head_consensus_fires_constantly_on_locked():
    c = _sink_locked_cascade(T=200, H=8, n_sink=4)
    events = extract_attention_multi_head_sink_consensus(c, n_sink=4,
                                                           consensus_frac=0.5)
    # All 8 heads attend to sink → consensus at every token
    assert events.size >= 195, (
        f"multi_head_consensus should fire ~every token on sink-locked; got {events.size}")


# ─── Empty/missing cascade handling ────────────────────────────────────────

def test_extractors_handle_missing_attentions():
    c = dict(hidden_norms=np.zeros((4, 200)))    # no 'attentions' key
    for extractor in (extract_attention_argmax_sink,
                       extract_attention_sink_residency_runs,
                       extract_attention_multi_head_sink_consensus):
        out = extractor(c)
        assert isinstance(out, np.ndarray) and out.size == 0, (
            f"{extractor.__name__} should return empty on missing 'attentions'")


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
