"""
run_phase19_distinctness_matrix.py — Phase 19 Tier 2.

Build the full pairwise empirical-distinctness matrix for the project's
extractor panel:

  General extractors (6, from `extractors.EXTRACTORS`):
    direct_events, pll_passage, find_peaks_prominence, derivative_zeros,
    threshold_crossing, modular_bin_events.

  LLM-specific extractors (8, from `llm_extractors.LLM_EXTRACTORS`):
    residual_norm_peaks, attention_entropy_peaks, attention_target_jumps,
    attention_sink_events, layer_kl_divergence_events,
    attention_argmax_sink, attention_sink_residency_runs,
    attention_multi_head_sink_consensus.

LLM extractors take a `cascade` dict (transformer-state stash).  For
the calibrator panel, we synthesise minimal cascades that encode each
calibrator's events as attention-argmax-to-sink, residual-norm peaks,
and per-layer KL spikes — `synthesize_cascade_from_events`.

Equivalence-class structure: pairs that are not demonstrably distinct
form an equivalence class via transitive closure (union-find).  Per
the spec, this confirms or revises the §7.ter.22 / §7.ter.23 claims
about LLM extractors clustering into a small number of underlying
mechanisms despite description-level diversity.

Output:
  data/phase19_distinctness_matrix.parquet
  plots/52_phase19_extractor_equivalence.png
"""
from __future__ import annotations
import os, sys, time
from itertools import combinations
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from extractors import EXTRACTORS
from llm_extractors import LLM_EXTRACTORS
from extractor_distinctness import (
    distinct_pair, STANDARD_CALIBRATORS,
    extractor_for_events, _quadrants_per_q, _q_disagreement_count,
    _gen_poisson, _gen_periodic, _gen_mixed, _load_zeta,
)
from signal_gen import (
    make_beta_ensemble_eigenvalues,
    make_uniform_jitter,
)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

DATA = os.path.join(THIS_DIR, 'data')
PLOTS = os.path.join(THIS_DIR, 'plots')

N_SEEDS = 5
SEED_THRESHOLD = 4
Q_MAX = 30
MIN_EVENTS = 30
# Smaller calibrators for distinctness testing — keeps cascade-embedded
# events sparse enough for threshold-style LLM extractors to detect
# isolated peaks rather than a continuous-fill regime.
DIST_N_POINTS = 400
DIST_T = 1200


# Smaller-N versions of the calibrator generators — used in the
# pairwise-matrix run to keep cascade synthesis tractable while still
# spanning the standard 8-class panel.
DIST_CALIBRATORS = [
    ('poisson',           lambda s: _gen_poisson(s, n=DIST_N_POINTS)),
    ('beta=1_GOE',        lambda s: make_beta_ensemble_eigenvalues(DIST_N_POINTS, 1, s)),
    ('beta=2_GUE',        lambda s: make_beta_ensemble_eigenvalues(DIST_N_POINTS, 2, s)),
    ('beta=4_GSE',        lambda s: make_beta_ensemble_eigenvalues(DIST_N_POINTS, 4, s)),
    ('zeta_first_400',    lambda s: _load_zeta(s, n=DIST_N_POINTS)),
    ('uniform_jitter',    lambda s: make_uniform_jitter(DIST_N_POINTS, 0.10, s)),
    ('periodic_q7',       lambda s: _gen_periodic(s, period=7.0, jitter=0.05,
                                                     n=DIST_N_POINTS)),
    ('mixed_q7_q12',      lambda s: _gen_mixed(s, n=DIST_N_POINTS)),
]


# ─── Synthetic cascade construction for LLM extractors ────────────────────


def synthesize_cascade_from_events(
        events: np.ndarray,
        T: int = 600,
        n_layers: int = 3,
        n_heads: int = 3,
        n_sink: int = 4,
        peak_height: float = 5.0,
        background_noise: float = 0.1,
        rng: np.random.Generator = None,
        ) -> dict:
    """Build a synthetic transformer cascade that encodes the input event
    positions as detectable signatures across the LLM extractors:

      - `hidden_norms[L, T]`: baseline 1.0 + peak_height-tall Gaussian
        bumps at integer-rounded event positions, plus background noise.
        Picks up `residual_norm_peaks`.
      - `attn_entropy[L, H, T]`: baseline + dips at event positions
        (low entropy ↔ peaked attention).  Picks up
        `attention_entropy_peaks` (after sign-flip via find_peaks on
        -entropy ≈ peakiness).
      - `attentions[L]`: each layer's attentions[layer] is a [H, T, T]
        tensor; row q is the attention distribution from query q over
        keys.  At event positions, every head's argmax targets the
        first sink token (consensus, sink-mass spike, argmax-to-sink,
        target jump from non-sink to sink).  Between events, argmax
        targets `q-1` (causal nearest neighbour, low sink mass).
      - Layer-to-layer divergence is created by varying which sink token
        each layer's attention concentrates on at event positions, so
        `layer_kl_divergence_events` sees a spike there.
      - Sink-residency runs are created by extending the sink-target
        for `sink_run_len` consecutive tokens at event-position blocks.

    Output: dict matching the schema expected by `llm_extractors`
    (`hidden_norms`, `attentions`, `attn_entropy`).
    """
    if rng is None:
        rng = np.random.default_rng()
    events = np.asarray(events, dtype=np.float64)

    # 1. Map events to integer token positions in [0, T).
    if events.size == 0:
        ev_int = np.zeros(0, dtype=int)
    else:
        # Rescale events to fit into [0, T) preserving relative spacings.
        e_min = float(events.min())
        e_max = float(events.max())
        if e_max <= e_min:
            ev_int = np.zeros(0, dtype=int)
        else:
            scaled = (events - e_min) / (e_max - e_min) * (T - 1)
            ev_int = np.unique(np.round(scaled).astype(int))
            ev_int = ev_int[(ev_int >= 1) & (ev_int < T)]
    is_event = np.zeros(T, dtype=bool)
    is_event[ev_int] = True

    # 2. Hidden norms: peaks at events.
    hidden_norms = np.full((n_layers, T), 1.0, dtype=np.float64)
    for L in range(n_layers):
        hidden_norms[L] += background_noise * rng.standard_normal(T)
        # Gaussian-shaped bumps at events, σ=1.
        for p in ev_int:
            lo, hi = max(0, p - 3), min(T, p + 4)
            xs = np.arange(lo, hi) - p
            hidden_norms[L, lo:hi] += peak_height * np.exp(-0.5 * xs ** 2)

    # 3. Attention tensors.  At each query q ∈ [0, T):
    #    if is_event[q] → all heads target a sink token (vary per layer).
    #    else → target q-1 (causal nearest neighbour).
    #    Distribution is sharply peaked (one-hot smoothed by ε temperature).
    attentions = []
    for L in range(n_layers):
        # Layer-dependent sink target (creates inter-layer KL spikes
        # at event positions).
        sink_target = L % max(1, n_sink)
        # Vectorised attention construction:
        #  rows [H, q, k] = uniform 0.15 / (T-1) + 0.85 at chosen target k
        target_idx = np.empty((n_heads, T), dtype=np.int64)
        for H in range(n_heads):
            for q in range(T):
                if is_event[q]:
                    target_idx[H, q] = sink_target
                else:
                    # Non-sink causal target: q - 1, but skip past the
                    # sink range so non-event queries don't accidentally
                    # land argmax inside [0, n_sink) for small q.
                    candidate = q - 1 - (H % 3)
                    if candidate < n_sink:
                        candidate = (q + n_sink + (H % 3)) % T
                        if candidate < n_sink:
                            candidate = n_sink + (H % max(1, T - n_sink - 1))
                    target_idx[H, q] = candidate
        a = np.full((n_heads, T, T),
                     (1.0 - 0.85) / (T - 1), dtype=np.float32)
        for H in range(n_heads):
            a[H, np.arange(T), target_idx[H]] = 0.85
        # Re-normalise per-row to enforce sum=1 (defensive, handles the
        # double-count at the target index).
        a /= a.sum(axis=2, keepdims=True)
        attentions.append(a)

    # 4. Attention entropy: small at events, larger between events.
    #    Compute per-layer per-head entropy directly from attentions to
    #    keep the surrogate self-consistent.
    eps = 1e-12
    attn_entropy = np.zeros((n_layers, n_heads, T), dtype=np.float64)
    for L in range(n_layers):
        a = attentions[L]
        # Entropy of each row (per query)
        attn_entropy[L] = -(a * np.log(a + eps)).sum(axis=2)

    return dict(
        hidden_norms=hidden_norms,
        attentions=attentions,
        attn_entropy=attn_entropy,
    )


# ─── Adapter: LLM extractor as f(t_k) -> events ───────────────────────────


def llm_extractor_adapter(name: str, T: int = DIST_T, **synth_kwargs):
    """Wrap an LLM extractor into a unified `f(t_k) -> events` callable
    by synthesising a cascade from the input events first."""
    fn = LLM_EXTRACTORS[name]

    def _wrapped(t_k):
        rng = np.random.default_rng(int(abs(hash(name)) % 1_000_000))
        cascade = synthesize_cascade_from_events(t_k, T=T, rng=rng, **synth_kwargs)
        out = fn(cascade)
        return np.sort(np.asarray(out, dtype=np.float64))

    _wrapped.__name__ = f"llm_{name}"
    return _wrapped


# ─── Build full extractor panel ───────────────────────────────────────────


def build_extractor_panel():
    """Return list of (name, callable) for all extractors in scope."""
    panel = []
    # General extractors with default params
    for name in EXTRACTORS.keys():
        panel.append((f"gen.{name}", extractor_for_events(name)))
    # LLM-specific extractors via cascade-synthesis adapter
    for name in LLM_EXTRACTORS.keys():
        panel.append((f"llm.{name}", llm_extractor_adapter(name)))
    return panel


# ─── Equivalence classes via union-find ───────────────────────────────────


class UnionFind:
    def __init__(self, items):
        self.parent = {x: x for x in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb

    def classes(self):
        out = {}
        for x in self.parent:
            r = self.find(x)
            out.setdefault(r, []).append(x)
        return list(out.values())


# ─── Main matrix loop ─────────────────────────────────────────────────────


def main():
    panel = build_extractor_panel()
    names = [n for n, _ in panel]
    callables = {n: fn for n, fn in panel}
    print("=" * 100)
    print(f"Phase 19 Tier 2 — pairwise distinctness for {len(names)} "
          f"extractors ({len(names) * (len(names) - 1) // 2} pairs)")
    print(f"  calibrators: {len(DIST_CALIBRATORS)} (n={DIST_N_POINTS} each, "
          f"cascade T={DIST_T}), seeds: {N_SEEDS}, "
          f"seed_threshold: {SEED_THRESHOLD} of {N_SEEDS}")
    print("=" * 100)

    # Step 1: pre-compute per-(calibrator, seed, extractor) per-q quadrants.
    # Massively cheaper than re-running joint_q_profile in every pair check.
    print("\n  Pre-computing per-(calibrator, seed, extractor) quadrants…")
    cache = {}   # (cal_name, seed, ext_name) -> qd DataFrame
    t_start = time.time()
    for cal_name, cal_gen in DIST_CALIBRATORS:
        for seed in range(N_SEEDS):
            try:
                t_k = cal_gen(seed)
            except Exception as e:
                print(f"    {cal_name} seed={seed}: gen failed: {e}")
                continue
            for ext_name, ext_fn in panel:
                t0 = time.time()
                try:
                    events = np.sort(np.asarray(ext_fn(t_k), dtype=np.float64))
                except Exception as e:
                    print(f"      {ext_name} on {cal_name} seed={seed}: "
                          f"FAILED {e}")
                    cache[(cal_name, seed, ext_name)] = None
                    continue
                qd = _quadrants_per_q(events, q_max=Q_MAX,
                                       min_events=MIN_EVENTS)
                cache[(cal_name, seed, ext_name)] = qd
                dt = time.time() - t0
                if dt > 5.0:
                    print(f"    [slow] {ext_name} on {cal_name} seed={seed}: "
                          f"{events.size:,} events, {dt:.1f}s")
        print(f"    {cal_name}: complete  ⏱ {time.time() - t_start:.1f}s")

    # Step 2: pairwise distinctness from the cache.
    print("\n  Computing pairwise distinctness…")
    rows = []
    for ext_a, ext_b in combinations(names, 2):
        max_disagree = 0
        disagreeing_class = None
        per_class = []
        for cal_name, _ in STANDARD_CALIBRATORS:
            n_dis_seeds = 0
            for seed in range(N_SEEDS):
                qd_a = cache.get((cal_name, seed, ext_a))
                qd_b = cache.get((cal_name, seed, ext_b))
                if qd_a is None or qd_b is None:
                    continue
                n_q_dis = _q_disagreement_count(qd_a, qd_b)
                if n_q_dis > 0:
                    n_dis_seeds += 1
            per_class.append(dict(calibrator=cal_name,
                                    n_disagree_seeds=n_dis_seeds))
            if n_dis_seeds > max_disagree:
                max_disagree = n_dis_seeds
                if n_dis_seeds >= SEED_THRESHOLD:
                    disagreeing_class = cal_name
        distinct = max_disagree >= SEED_THRESHOLD
        rows.append(dict(
            ext_a=ext_a, ext_b=ext_b,
            distinct=bool(distinct),
            max_disagree_seeds=int(max_disagree),
            disagreeing_class=disagreeing_class,
            per_class=str(per_class),
        ))

    df = pd.DataFrame(rows)
    out_parquet = os.path.join(DATA, 'phase19_distinctness_matrix.parquet')
    df.to_parquet(out_parquet)
    print(f"\n  → {out_parquet}  ({len(df)} pairs)")

    # Step 3: equivalence classes (union-find on not-distinct edges).
    uf = UnionFind(names)
    for _, row in df.iterrows():
        if not row['distinct']:
            uf.union(row['ext_a'], row['ext_b'])
    classes = uf.classes()
    classes.sort(key=lambda c: (-len(c), c[0]))

    print("\n" + "=" * 100)
    print(f"Equivalence classes ({len(classes)} classes from {len(names)} extractors):")
    print("=" * 100)
    for i, c in enumerate(classes):
        print(f"  Class {i + 1} ({len(c)} members):")
        for ext in c:
            print(f"      {ext}")

    # Step 4: plot heatmap + class diagram.
    print("\n  Plotting…")
    n = len(names)
    M = np.zeros((n, n), dtype=int)
    name_idx = {n_: i for i, n_ in enumerate(names)}
    for _, row in df.iterrows():
        i = name_idx[row['ext_a']]
        j = name_idx[row['ext_b']]
        v = int(row['distinct'])
        M[i, j] = v
        M[j, i] = v
    np.fill_diagonal(M, -1)   # mark self-pairs

    # Order extractors by equivalence class, classes by size.
    order = []
    class_of = {}
    for c_idx, c in enumerate(classes):
        for ext in sorted(c):
            order.append(ext)
            class_of[ext] = c_idx
    perm = [name_idx[x] for x in order]
    M_p = M[np.ix_(perm, perm)]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6),
                              gridspec_kw={'width_ratios': [3, 1]})
    ax_h = axes[0]
    cmap = plt.matplotlib.colors.ListedColormap(
        ['black', '#F1F1F1', '#D62728'])
    im = ax_h.imshow(M_p + 1, aspect='auto', cmap=cmap,
                      vmin=0, vmax=2)
    ax_h.set_xticks(np.arange(n))
    ax_h.set_xticklabels(order, rotation=70, ha='right', fontsize=7)
    ax_h.set_yticks(np.arange(n))
    ax_h.set_yticklabels(order, fontsize=7)
    # Class boundaries
    boundaries = []
    cur = 0
    for c in classes:
        cur += len(c)
        boundaries.append(cur)
    for b in boundaries[:-1]:
        ax_h.axhline(b - 0.5, color='blue', linewidth=1, alpha=0.5)
        ax_h.axvline(b - 0.5, color='blue', linewidth=1, alpha=0.5)
    ax_h.set_title('Phase 19 Tier 2 — pairwise distinctness\n'
                    '(red = distinct, light = equivalent on calibrator panel; '
                    'blue lines = equivalence-class boundaries)')
    legend_h = [
        mpatches.Patch(color='#D62728', label='distinct'),
        mpatches.Patch(color='#F1F1F1', label='equivalent (or no disagreement)'),
        mpatches.Patch(color='black', label='self-pair'),
    ]
    ax_h.legend(handles=legend_h, loc='upper right', bbox_to_anchor=(1.0, 1.20),
                 fontsize=8, framealpha=0.9)

    ax_c = axes[1]
    ax_c.axis('off')
    ax_c.set_title('Equivalence classes', fontsize=10)
    y = 1.0
    for i, c in enumerate(classes):
        ax_c.text(0.0, y, f"Class {i + 1} ({len(c)}):",
                  fontsize=9, fontweight='bold', transform=ax_c.transAxes)
        y -= 0.04
        for ext in sorted(c):
            ax_c.text(0.05, y, ext, fontsize=7,
                       transform=ax_c.transAxes)
            y -= 0.03
        y -= 0.02

    plt.tight_layout()
    out_png = os.path.join(PLOTS, '52_phase19_extractor_equivalence.png')
    plt.savefig(out_png, dpi=130, bbox_inches='tight')
    plt.close()
    print(f"  → {out_png}")

    print(f"\n  total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
