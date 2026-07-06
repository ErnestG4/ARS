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

## Cross-check DONE — Chialvo is a confirmed clustering-type member (and it corrects Track 1.1)
Re-read Chialvo (Track 1.1) on the clustering axis, torus vs chaos, in- AND out-of-sample:
- repulsion axis (rep_med): in-sample +0.296 but **flips to −0.067 out-of-sample** (does NOT generalize).
- clustering axis (CV of |Δpeak-amp|): in-sample **+0.196**, out-of-sample **+0.124** — SAME sign,
  consistent magnitude (mass<0.3: 0.148→0.230 in / 0.147→0.218 oos — both move up ~0.08). GENERALIZES.

So the SAME observable read on the repulsion axis fails out-of-sample but on the clustering axis
separates consistently. Chialvo is clustering-type (weak, +0.12-0.20) like Kaneko (strong, +25-37) —
taxonomy CONFIRMED with two members. **This corrects Track 1.1:** the original
`FAILED / NOT-SPECTRALLY-SEPARABLE` was AXIS-INCOMPLETE (only the repulsion/quadrant axis was tested);
the honest verdict is **`NOT-REPULSION-SEPARABLE` but CLUSTERING-AXIS-DETECTABLE (out-of-sample-consistent)**.
[[torus_transition_rigidity_vs_clustering]], [[ksgue_burst_substrate_relative]]-sibling; unifies with the SOC pair.

## Magnitude probe (within-Kaneko) — resolves the "Chialvo +0.12 vs Kaneko +37" question
`kaneko_gcm.py magnitude` (parallel). Question: does the clustering-axis separation magnitude track a
PHYSICAL variable, or is it an artifact?
- **(a) vary N at Δ=0.04:** CV-sep = 30.1 / 43.1 / 61.4 / 87.3 at N = 1000/2000/4000/8000 — scales as
  **√N** (8× N → 2.9× sep ≈ √8). So CV-based "magnitude" is a TRIVIAL N-scaling ARTIFACT (one cluster of
  N points → CV~√N). mass<τ-sep = 0.695/0.696/0.700/0.702 — **N-INVARIANT.** ⇒ use mass<τ, not CV, for
  cross-case magnitude.
- **(b) vary Δ (heterogeneity → transition sharpness) at N=2000:** mass<τ-sep tracks the R-JUMP
  (order-parameter discontinuity): Δ=0.02–0.10 → R-jump 0.88–0.82, mass-sep 0.59–0.72; **Δ=0.15 → R-jump
  collapses to 0.067 (no sync transition) and mass-sep collapses to 0.034.** The physical
  clustering-separation magnitude tracks the synchronization-transition STRENGTH.

**Resolution:** the "Chialvo +0.12 vs Kaneko +37" comparison was meaningless — different N, different
observable, CV-based (a √N artifact). The N-robust physical measure (mass<τ-sep) tracks the
order-parameter jump. Cross-substrate clustering magnitudes must be compared on mass<τ at matched N (or
N-normalized), never raw CV. [[capture_full_per_axis_sweep]]-sibling on the normalization axis.
