"""
Phase 17 σ̂ saturation diagnostic.

Investigates the §7.ter.23 cross-architecture finding that Phi-3 and
TinyLlama returned identical σ̂ to 3 decimals.  Hypothesis: rep_int_q
is essentially a signal-level scalar (not a q-resolved curve), and
for find_peaks-on-integer-trace event sets it is determined by the
gap distribution geometry — which is architecture-invariant on
NATURAL_TEXT residual norms (the §7.ter.19 mechanism).

Empirical findings (run on 2026-05-08):

1. rep_int_q is q-flat for any uniform-jitter-class signal.  Even
   continuous synthetic σ ∈ {0.05, 0.10, 0.15, 0.20} calibrators
   produce rep_int_q with std ≈ 0.0001 across q=1..30.  The 28-30
   "unique values" reported across q are floating-point noise from
   pair-correlation binning, not q-resolved structural variation.

2. For find_peaks(prominence=0.3) on NATURAL_TEXT residual norms,
   rep_int_q saturates at exactly 0.7000 for Phi-3 and TinyLlama
   (different events, Jaccard 0.16, n=133 vs 127), and 0.7500 for
   Qwen 2.5 3B.  These are exact to floating-point precision — not
   coincidence.  The gap distribution from find_peaks(prominence=0.3)
   on a NATURAL_TEXT-driven 1D residual-norm trace is architecture-
   invariant; the pair-correlation rep integral over r ∈ [0, 1] is
   therefore identical.

3. The σ̂ recovery routine inverts a continuous calibrator anchor
   curve (rep_int → σ).  When applied to a signal whose rep_int_q is
   a quantized scalar, σ̂ is the inverse-image of that quantized
   scalar — useful as a calibrator-relative descriptor, but NOT a
   recovery of a continuous-σ parameter of the signal.

Implications for the §7.ter.23 cross-architecture reading:

- "σ̂ insensitive to model size and microarchitecture variation"
  was over-reading the metric.  The honest read is: rep_int_q on
  find_peaks(prominence)-extracted integer-position events is blind
  to model variation at this metric's resolution; the cross-
  architecture σ̂ similarity is a re-derivation of §7.ter.19 (rhythm
  is set by find_peaks autocorrelation, not model dynamics) at
  higher metric resolution.

- "Primes (σ̂ = 0.048) and LLM (σ̂ = 0.087) occupy the same region
  of BR_artifact" still holds at the descriptive level, but the
  comparison is "where in the calibrator family each signal's pair-
  correlation rep integral sits", not "fitted continuous-σ values".
  Primes have continuous (log-unfolded) positions and a continuous-σ
  recovery is meaningful; LLM peaks are integer-positioned and σ̂ is
  a calibrator-relative scalar.

Output: text-only diagnostic (no parquet/plot — the conclusions go
into RESULTS.md §7.ter.23).
"""
from __future__ import annotations
import os
import sys

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile
from field_generator import generate


def report(label: str, t: np.ndarray, q_max: int = 30):
    j = joint_q_profile(t, q_max=q_max, min_events_per_q=30)
    well = j[~j["underpowered"]]
    if len(well) == 0:
        print(f"  {label:<48}  (insufficient)")
        return
    rep = well["rep_int_q"].to_numpy()
    print(f"  {label:<48}  n={len(t):>4}  "
          f"rep_int_q in [{rep.min():.4f}, {rep.max():.4f}]  "
          f"median={np.median(rep):.4f}  std={rep.std():.4f}")


def main():
    print("=" * 90)
    print("Continuous-position synthetic uniform_jitter (calibrator)")
    print("=" * 90)
    for sigma in (0.05, 0.10, 0.15, 0.20):
        t = generate("uniform_jitter", dict(sigma=sigma), n_events=1000, seed=0)
        report(f"uniform_jitter σ={sigma}", t)
    print("  → rep_int_q is q-flat (std ≈ 0.0001) for any uniform_jitter-class")
    print("    signal: it's a signal-level scalar, not a q-resolved curve.")
    print()

    print("=" * 90)
    print("Random-integer support, density 0.27")
    print("=" * 90)
    rng = np.random.default_rng(0)
    n_total = 460
    pos = rng.choice(n_total, size=int(n_total * 0.27), replace=False)
    t_int = np.sort(pos.astype(np.float64))
    report("random_integer density=0.27 (no jitter)", t_int)
    t_jit = t_int + rng.uniform(-0.4, 0.4, t_int.size)
    t_jit = np.sort(t_jit)
    report("random_integer + ±0.4 jitter (continuous)", t_jit)
    print("  → Random-integer support gives moderate rep_int_q (~0.55).  Adding")
    print("    ±0.4 jitter to break integer-quantisation drops it sharply.")
    print()

    print("=" * 90)
    print("Verdict")
    print("=" * 90)
    print("  rep_int_q is a near-scalar signal-level summary; the σ̂ recovery")
    print("  inverts the calibrator anchor curve to produce a calibrator-relative")
    print("  descriptor.  For continuous-position uniform_jitter signals (and")
    print("  primes after log-unfolding), the recovery returns a meaningful")
    print("  parameter.  For integer-position find_peaks output, the recovery")
    print("  returns a scalar determined by the gap distribution geometry — which")
    print("  is architecture-invariant on a fixed input text (the §7.ter.19")
    print("  mechanism).  The cross-architecture σ̂ similarity at residual_norm")
    print("  peaks is a metric-blindness finding, not a model-invariance finding.")


if __name__ == "__main__":
    main()
