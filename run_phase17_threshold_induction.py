"""
Phase 17 falsification test for the three "out-of-domain" extractors
in finding (E).

The Phase 16 Tier 1 induction-on-Poisson paradigm: if an extractor's
filter mechanism produces TR/Wigner-class readings when fed a Poisson
input that has no underlying level repulsion, the readings on real
LLM signals are extractor-induced rather than substantively read off
the LLM internals.

Mechanisms tested:

  layer_kl_divergence_events / attention_sink_events:
    Both apply moving-mean + k·σ → up-crossings to a 1D positive
    signal (KL-summed-over-layer-pairs / sink-mass time series).
    Falsification: feed an iid positive signal (Poisson and
    exponential noise), apply the SAME threshold logic, look at
    rep_int_q on the resulting events.

  attention_target_jumps:
    By-construction: events at positions where |Δargmax| ≥ 16 between
    consecutive query positions.  Falsification: random argmax
    sequence (iid uniform-over-T), apply the same |Δ| ≥ 16 condition.

Three control inputs per mechanism, 5 seeds each.  If Poisson-input
rep_int_q lands at ≈ 0.34 for layer_kl / sink_events, the LLM cells'
0.34 readings are mechanism-induced.

Output:
  data/phase17_threshold_induction.parquet
"""
from __future__ import annotations
import os, sys
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic

DATA = os.path.join(THIS_DIR, "data")
T = 1024            # match LLM forward-pass length
WINDOW = 50         # extractor's moving-window
K = 1.0             # extractor's threshold multiplier
DELTA_TOKENS = 16   # target_jumps condition
N_SEEDS = 5
Q_MAX = 30
MIN_EVENTS = 30


def _moving_mean_std(x, window=50):
    """Replicate llm_extractors._moving_mean_std behaviour."""
    n = x.size
    mu = np.zeros(n); sd = np.zeros(n)
    for i in range(n):
        a = max(0, i - window // 2); b = min(n, i + window // 2 + 1)
        mu[i] = x[a:b].mean()
        sd[i] = x[a:b].std() + 1e-12
    return mu, sd


def threshold_upcross_events(signal: np.ndarray, k: float = K,
                              window: int = WINDOW) -> np.ndarray:
    """Replicates layer_kl_divergence_events / attention_sink_events
    threshold mechanism."""
    if signal.size < window + 5: return np.zeros(0)
    mu, sd = _moving_mean_std(signal, window=window)
    above = signal > (mu + k * sd)
    if above.sum() < 2: return np.zeros(0)
    transitions = np.diff(above.astype(np.int8))
    upcross = np.where(transitions == 1)[0] + 1
    return upcross.astype(np.float64)


def argmax_jump_events(argmax_seq: np.ndarray,
                       delta: int = DELTA_TOKENS) -> np.ndarray:
    """Replicates attention_target_jumps mechanism."""
    diffs = np.abs(np.diff(argmax_seq))
    jumps = np.where(diffs >= delta)[0] + 1
    return jumps.astype(np.float64)


def measure(events: np.ndarray, signal_label: str, mechanism: str,
            n_input: int) -> dict:
    if events.size < MIN_EVENTS:
        return dict(signal=signal_label, mechanism=mechanism,
                    n_input=n_input, n_events=int(events.size),
                    rep_int_q_median=np.nan, primary_quadrant=None,
                    quadrant_pct=np.nan, underpowered=True)
    j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    well = j[~j["underpowered"]]
    rep_med = float(well["rep_int_q"].median()) if len(well) else float("nan")
    qd = joint_quadrant_diagnostic(j)
    # qd is a DataFrame with per-q quadrant assignment
    well_q = qd[~qd["underpowered"]] if "underpowered" in qd.columns else qd
    if len(well_q):
        counts = well_q["quadrant"].value_counts()
        primary = str(counts.idxmax())
        pct = float(counts.iloc[0] / counts.sum())
    else:
        primary, pct = "ambiguous", float("nan")
    return dict(signal=signal_label, mechanism=mechanism,
                n_input=n_input, n_events=int(events.size),
                rep_int_q_median=rep_med, primary_quadrant=primary,
                quadrant_pct=pct, underpowered=False)


def main():
    rows = []

    # ─── 1. Threshold-upcrossing mechanism (layer_kl / sink_events) ─────────
    print("=" * 80)
    print("Threshold up-crossing mechanism (layer_kl / sink_events)")
    print("=" * 80)
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        # (a) iid exponential — heavy-tail positive Poisson-process step magnitudes
        sig_exp = rng.exponential(1.0, size=T)
        ev = threshold_upcross_events(sig_exp)
        rows.append(measure(ev, "iid_exponential", "threshold_upcross", T) | dict(seed=seed))
        # (b) iid Poisson counts — discrete positive signal
        sig_pois = rng.poisson(1.0, size=T).astype(float)
        ev = threshold_upcross_events(sig_pois)
        rows.append(measure(ev, "iid_poisson", "threshold_upcross", T) | dict(seed=seed))
        # (c) uniform iid — flat positive signal
        sig_uni = rng.uniform(0.0, 1.0, size=T)
        ev = threshold_upcross_events(sig_uni)
        rows.append(measure(ev, "iid_uniform", "threshold_upcross", T) | dict(seed=seed))

    # ─── 2. Argmax-jump mechanism (target_jumps) ────────────────────────────
    print("\n" + "=" * 80)
    print("Argmax-jump mechanism (target_jumps)")
    print("=" * 80)
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        # (a) iid uniform argmax — random target each query
        argmax_seq = rng.integers(0, T, size=T)
        ev = argmax_jump_events(argmax_seq)
        rows.append(measure(ev, "iid_uniform_argmax", "argmax_jump", T) | dict(seed=seed))
        # (b) sticky argmax — change with low probability per step (autocorrelated)
        argmax_seq = np.zeros(T, dtype=int)
        argmax_seq[0] = rng.integers(0, T)
        for i in range(1, T):
            if rng.random() < 0.1:
                argmax_seq[i] = rng.integers(0, T)
            else:
                argmax_seq[i] = argmax_seq[i - 1]
        ev = argmax_jump_events(argmax_seq)
        rows.append(measure(ev, "sticky_argmax_p=0.1", "argmax_jump", T) | dict(seed=seed))

    df = pd.DataFrame(rows)
    out_parquet = os.path.join(DATA, "phase17_threshold_induction.parquet")
    df.to_parquet(out_parquet)

    # ─── 3. Aggregate report ────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("Per-(signal, mechanism) median rep_int_q across seeds")
    print("=" * 80)
    valid = df[~df["underpowered"]].copy()
    if len(valid):
        agg = (valid.groupby(["signal", "mechanism"])
               .agg(rep_int_q_median=("rep_int_q_median", "median"),
                    rep_int_q_min=("rep_int_q_median", "min"),
                    rep_int_q_max=("rep_int_q_median", "max"),
                    n_events_median=("n_events", "median"),
                    primary_quadrant=("primary_quadrant",
                                       lambda x: x.value_counts().index[0]),
                    n_seeds=("seed", "count"))
               .reset_index())
        for _, r in agg.iterrows():
            print(f"  {r['signal']:<25}  {r['mechanism']:<22}  "
                  f"rep_int_q.med = {r['rep_int_q_median']:.4f} "
                  f"[{r['rep_int_q_min']:.4f}, {r['rep_int_q_max']:.4f}]  "
                  f"n_ev≈{int(r['n_events_median'])}  "
                  f"quadrant={r['primary_quadrant']}  "
                  f"({int(r['n_seeds'])} seeds)")

    print()
    print("=" * 80)
    print("Underpowered cells")
    print("=" * 80)
    up = df[df["underpowered"]]
    if len(up):
        print(up.groupby(["signal", "mechanism"]).size())
    else:
        print("  (none)")

    print()
    print("=" * 80)
    print("Comparison to LLM-cell rep_int_q values from finding (E)")
    print("=" * 80)
    print("  layer_kl_divergence_events   Phi-3=0.340  TinyLlama=0.342  →  if iid_*"
          "rep_int_q.med ≈ 0.34, threshold mechanism induces this on Poisson-"
          "structured input.")
    print("  attention_target_jumps       Qwen=0.700  Phi-3=0.350  →  if "
          "iid_uniform_argmax rep_int_q ≈ 0.35, the by-construction filter")
    print("                              induces TR-like readings.")
    print(f"\n  → {out_parquet}")


if __name__ == "__main__":
    main()
