# Track 1.4 — Kaneko GCM Generalization Test · Findings

**Phase 36, 2026-05-31.** Pre-registration: `TRACK1_4_KANEKO_CONFIG_JUSTIFICATION.md`. Reopened
deliberately as a POSITIVE-CAPABLE generalization test of the Chialvo `NOT-SPECTRALLY-SEPARABLE`
negative (must be able to come back positive, or it isn't testing generalization).

## Verdict (two-sided — the informative outcome): `REPULSION-AXIS-BLIND_CLASS-WIDE / CLUSTERING-AXIS-SEPARATES_OOS`

The test came back BOTH ways on DIFFERENT axes, which resolves the generalization question precisely:
1. **The repulsion/quadrant axis (`joint_q_profile` rep_int — the torus-breakdown lens that Chialvo
   used) is BLIND to this transition class even with the high-D spatial observable.** ⇒ Chialvo's
   repulsion-axis negative is **CLASS-WIDE**, not Chialvo-specific.
2. **But the transition IS spectrally legible on the CLUSTERING axis (CV / mass<τ, Poisson↔super-Poisson),
   robustly out-of-sample.** ⇒ "spectrally invisible" was **AXIS-SPECIFIC**; the right ARS readout sees it.

## System & feasibility (test can be positive — confirmed first)
Mean-field coupled circle maps (Kuramoto-style, O(N)/step): θ_i' = θ_i + Ω_i + (K/2π)sin(2πθ_i) +
ε·R·sin(2π(ψ−θ_i)), heterogeneous Ω_i. Sweep coupling ε; sync order parameter R (independent regime
marker). Feasibility pre-check (gates the run): snapshot gap-CV swings 1.18 (desync, R≈0.11) → 54
(clustered, R≈0.99) — the snapshot distribution CHANGES enormously ⇒ the test CAN be positive. Headline
observable = SNAPSHOT spatial NNS (sorted phases on S¹ → circular gaps → instrument), the high-D
structure Chialvo lacked; NOT temporal timing (the reconfirmation trap, avoided).

## Result (both axes, in- and out-of-sample)
| ε | R (in-sample) | rep_med (repulsion) | CV (clustering) || R (oos) | rep_med (oos) | CV (oos) |
|---|---|---|---|---|---|---|---|
| 0.00 | 0.111 | 0.0 BL | 1.16 || 0.152 | 0.0 BL | 1.55 |
| 0.03 | 0.727 | 0.0 BL | 2.98 || 0.485 | 0.0 BL | 2.55 |
| 0.08 | 0.976 | 0.0 BL | 50.70 || 0.972 | 0.0 BL | 36.93 |
| 0.20 | 0.994 | 0.0 BL | 54.15 || 0.990 | 0.0 BL | 38.26 |

- **Repulsion axis** rep_med: **0.0, BL throughout** the transition, BOTH samples — separation 0.0. Blind.
- **Clustering axis** CV: separation desync→clustered **+36.95 in-sample, +25.89 out-of-sample**
  (mass<0.3: 0.30→0.9997). Robust out-of-sample. Separates.

## Why (the mechanism, unifying with banked work)
The torus-breakdown/collective transition is a **CLUSTERING transition** (Poisson→super-clustered as
oscillators synchronize), NOT a level-*repulsion* transition. Both the desync (≈Poisson, CV~1.2) and
clustered (CV~50) configurations are LOW-repulsion ⇒ rep_med stays at the BL/low-repulsion floor in
both ⇒ the repulsion axis cannot separate them. This is EXACTLY the banked SOC-pair finding: one-sided
fitters and the rep_int/repulsion axis are blind to super-Poisson clustering; clustering is legible
only on ks_poisson / mass<τ / CV. The Kaneko collective transition is the same kind of object.

## Phase-36 unifying taxonomy (the synthesis this test earns)
"Quasiperiodicity↔chaos / torus-breakdown" transitions are NOT one ARS-class — they split by which axis
reads them:
- **RIGIDITY-type** — AM metal-insulator (Track 4): metal→clock-rigid W1δ FLOOR vs insulator→Poisson.
  Read by the **repulsion/rigidity axis** (W1δ / rep_int). That is why F2's IDS-unfold W1δ separated and
  why the floor was spectral rigidity.
- **CLUSTERING-type** — Chialvo (Track 1.1) & Kaneko (Track 1.4): Poisson→super-clustered. **Blind to the
  repulsion axis** (Chialvo: even in timing; Kaneko: even in the high-D spatial snapshot — CLASS-WIDE),
  **legible on the clustering axis** (mass<τ/CV — Kaneko, out-of-sample-validated).

So the repulsion/quadrant axis (the pillar-1 GUE↔Poisson-poles lens) reads rigidity-type torus
transitions, not clustering-type ones. The instrument is not blind to clustering-type transitions — it
reads them on the clustering axis. The earlier Chialvo `NOT-SPECTRALLY-SEPARABLE` is refined to
`NOT-REPULSION-SEPARABLE` (the repulsion axis specifically; the clustering axis was never tested on
Chialvo's temporal observable — a queued cross-check).

## Generalization verdict
The negative GENERALIZES on the repulsion axis (class-wide: temporal AND spatial, Chialvo AND Kaneko)
AND is BROKEN on the clustering axis (Kaneko, out-of-sample). Both halves informative — this was a
genuine generalization test, not a reconfirmation. The test came back positive where it could
(clustering axis), proving it was capable of it.

Queued cross-check (well-specified): re-read Chialvo on the clustering axis (mass<τ/CV of its
amplitude/spatial observable) to confirm the rigidity/clustering taxonomy holds there too.
[[ksgue_burst_substrate_relative]]-sibling on the one-sided-fitter axis; unifies with the SOC pair.
