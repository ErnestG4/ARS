# Track 1.4 — Kaneko GCM · Configuration Justification & Pre-Registration

**Authored before execution.** Phase 36, 2026-05-31. Reopened deliberately (was gated off after
Chialvo) to run as a GENUINE generalization test, not a reconfirmation. The test must be able to come
back POSITIVE, or it isn't testing generalization.

## What Chialvo's negative was, and the reconfirmation trap
Chialvo `NOT-SPECTRALLY-SEPARABLE`: its torus→chaos transition lived in TEMPORAL AMPLITUDE MODULATION
of a single 2-D element; spike-TIMING observables were clock-like in every regime, so the
spacing/repulsion (spectral) axis was blind (only a combinatorial 2→3 interval-cardinality signature
persisted). **Reading Kaneko via a temporal/mean-field/single-element timing observable would fail by
the IDENTICAL mechanism** — banking "negative again" without learning whether the negative is class-wide
or just Chialvo-in-higher-D. That observable is the trap; it is NOT the headline test.

## What makes Kaneko a positive-capable test (the pre-registration)
Kaneko GCM has what Chialvo lacked: HIGH DIMENSIONALITY → a SPATIAL CONFIGURATION of N oscillators on
the circle. The GCM collective transition (quasiperiodic torus → collective/turbulent chaos) is a
CLUSTERING ↔ DESYNCHRONIZATION transition — which changes the SPACING STATISTICS of the snapshot
configuration. Clustering vs repulsion vs Poisson spacing IS the spectral axis the arm reads.

- **Observable (headline):** SNAPSHOT SPATIAL NNS — at a fixed time (post-transient), sort the N phases
  on S¹, take circular gaps (incl. wrap-around), renormalise to unit mean, feed `joint_q_profile`
  (rep_int / rf), average the fingerprint over several stationary-regime snapshots. This is a GENUINELY
  DIFFERENT observable from Chialvo's (spatial configuration, not temporal amplitude), where the
  transition could land in the separation.
- **System:** globally-coupled circle maps, mean-field (Kuramoto-style) coupling for O(N)/step:
  θ_i' = θ_i + Ω + (K/2π)sin(2πθ_i) + ε·R·sin(2π(ψ−θ_i))  mod 1,  R e^{i2πψ}=(1/N)Σ e^{i2πθ_j}.
  Local circle-map nonlinearity K, global coupling ε. Sweep ε (coupling) across the
  desynchronized→clustered transition at fixed K.
- **Independent regime marker (the λ₁ analogue):** the synchronization order parameter R (R≈0
  desynchronised / R≈1 clustered) + the largest Lyapunov where tractable. R marks the regimes
  independently of the ARS readout (non-circular).

## Pre-registered verdicts (BOTH must be reachable)
- **POSITIVE** = the snapshot-NNS fingerprint (rep_med / quadrant) SEPARATES the desynchronised regime
  from the clustered/turbulent regime (a quadrant flip or a clear rep_med shift), AND the separation
  survives an OUT-OF-SAMPLE check (different N_osc and/or K, regimes marked independently by R — the
  Chialvo discipline). ⇒ torus-breakdown CAN be spectral-visible with the right (spatial-configuration)
  observable ⇒ **Chialvo's negative was OBSERVABLE-SPECIFIC, not class-wide.** The continuous/spatial
  arm reads it.
- **NEGATIVE** = the snapshot-NNS is statistically the same across regimes (transition invisible even to
  the spatial-configuration spacing). ⇒ the negative is **CLASS-WIDE**: even high-D spatial structure
  does not make torus-breakdown spectrally legible. Distinct from — and more informative than —
  "re-ran Chialvo."

## Feasibility pre-check (run FIRST — gates the instrument run)
Before the instrument: confirm the snapshot DISTRIBUTION actually changes across the transition (CV /
clustering of the snapshot gaps differs between R≈0 and R≈1), so the test CAN come back positive. If the
snapshot is statistically identical across regimes (e.g. always ~uniform), the observable cannot see it
by construction — bank that honestly (and note the observable can't test it) rather than running a
foregone negative. This is the "could it plausibly be positive?" gate the test requires.

## Instrument config
`joint_q_profile` q_max=25, min_events_per_q matched to the calibrator zoo; N_osc large enough that one
snapshot gives ≥ a few hundred gaps (N_osc ~ 2000–4000), fingerprint averaged over ≥10 post-transient
snapshots. Circular spacings (S¹ topology) — wrap-around gap included. Engine attribution (rep_int NNS
vs rf RF) recorded. STRICT: out-of-sample required before any POSITIVE is banked.

## Out of scope
Forced-HH + BGKM (ODE) remain deferred. No real data. This is a calibrator generalization test only.
