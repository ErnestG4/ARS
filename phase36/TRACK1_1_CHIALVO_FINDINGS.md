# Track 1.1 — Chialvo Map Calibrator · Findings

**Phase 36, 2026-05-31.** Gated on Track 0 PASS. Config-justification:
`TRACK1_1_CHIALVO_CONFIG_JUSTIFICATION.md`. Status vocabulary {DETECTED-AT-LOCUS, NFP-CONFIRMED,
SENSITIVITY-BOUNDED, FAILED}.

## Verdict: `FAILED — NOT-SPECTRALLY-SEPARABLE` (refined; banked, not discarded)

The Chialvo torus→chaos transition is **not robustly legible on the ARS spectral/quadrant
fingerprint (`joint_q_profile`) via any tested event observable.** This is a bounded negative about
the event-extracted *spectral* instrument for this transition class — NOT total instrument blindness,
and NOT a defect of the map (the dynamics are clean and the loci are exactly located).

## What the route is (dynamics — clean, ground-truth)
Chialvo (1995) 2-D map, fixed (b=0.45, k=0.06), sweep recovery-decay `a`: smooth 2-torus (λ₁≈0,
a≈0.89) → Arnold-tongue mode-locking windows (λ₁<0, a≈0.925–0.95) → chaos (λ₁≈+0.054, a≈0.965+). NS
onset analytic (det J(fixed pt)=1, complex pair, k_NS=0.0303); breakdown via λ₁=0 Benettin. λ₁ signs
reproduce textbook torus-breakdown. **The calibrator's ground truth is sound.**

## Why it fails on the spectral instrument — the observable investigation
Events fed to `joint_q_profile` must produce a *spacing distribution* that changes across the
transition. Tested observables (torus a=0.89 vs chaos a=0.97, in-sample slice b=0.45,k=0.06):

| event observable | torus | chaos | separates on quadrant/rep_med? |
|---|---|---|---|
| median-upcrossing of x (zoo default) | BR_artifact, rep 0.85, CV 0.019 | BR_artifact, rep 0.85, CV 0.024 | **no — clock both** |
| y-upcrossing intervals | BR_artifact, rep 0.85 | BR_artifact, rep 0.85 | **no — clock both** |
| IEI \|Δx\| (zoo logistic mode) | BL, rep 0.000, CV 1.73 | BL, rep 0.000, CV 2.28 | **no — both BL** (CV differs, quadrant-blind) |
| **\|Δ peak-amplitude\|** (envelope reading) | BL/ambiguous, rep 0.046 | TR, rep 0.342 | **in-sample YES (BL→TR)** |

**Root cause:** the fast x-oscillation period is regime-stable, so spike-*timing* observables
(median/y-upcrossing) read clock-like in every regime — the torus-breakdown lives in the *slow
quasiperiodic modulation / amplitude*, which timing discards. The interval SET only changes
combinatorially: **2 distinct upcrossing-interval values (torus) → 3 (chaos)** — a real but
*combinatorial* signature (cardinality of the interval set), exactly the kind a *spectral/repulsion*
instrument (`joint_q_profile`) is not built to read. So timing is NOT signal-free; its signal is
combinatorial, not spectral.

## The circularity guard — why \|Δpeak-amp\| does NOT rescue it
\|Δpeak-amp\| (the event-amplitude reading) separated torus from chaos IN-SAMPLE (BL→TR, rep_med
0.046→0.342). But choosing an observable *because* it separates validates the search, not the
instrument. **Out-of-sample check** (held-out slice b=0.35, k=0.08, λ₁ independently marking
regimes, NOT used in selection):
- torus a=0.88 → rep_med **0.340**, quad TR
- chaos a=0.99 → rep_med **0.272**, quad TR
- separation chaos−torus = **−0.067** (in-sample was **+0.296** — opposite sign, both TR).

The same dynamical type (torus, λ₁≈0) reads **BL in one slice, TR in another** ⇒ the \|Δpeak-amp\|
fingerprint tracks the map's *parameters*, not torus-vs-chaos. **The in-sample separation was
slice-specific, not a transition-class readout.** Without the out-of-sample test this would have
banked as a false `DETECTED`. The guard converted a would-be false positive into an honest negative.

## NFP / sensitivity / q_max (recorded; secondary given the verdict)
- No quadrant flip on the canonical (timing) observable across the whole swept route (all
  BR_artifact); stationary torus & chaos both stay BR_artifact. The naive sub-quadrant monotonicity
  metric is degenerate here (rep_med saturated ≈0.85 with ties → Spearman ill-defined), so the
  swept-vs-stationary sub-quadrant comparison is not interpretable on this observable — consistent
  with "timing carries no spectral transition signal."
- q_max guard: detection verdict identical at q_max 25 and 50 (q_max-robust).

## Two banked implications
1. **Engine/observable boundary for the spectral ARS instrument:** for a transition whose signal is
   carried by a continuous *amplitude/envelope* modulation (not by event timing or by a
   parameter-stable amplitude-spacing law), event-extraction + `joint_q_profile` does not give a
   robust, regime-typed readout. The fingerprint of even a fixed dynamical type is parameter-dependent.
2. **Convergence with Track 4 (independently found):** \|Δpeak-amp\| is the event-*amplitude* reading
   — the middle rung between pure timing (fails) and a full continuous envelope front-end (F1/Track 4).
   Its out-of-sample failure means even amplitude-aware *event* extraction loses this transition class.
   This is a **calibrator-side instance of Track 4's premise** (the transition living in a continuous
   modulation the event front-end discards) and *sharpens* Track 4's motivation: for this transition
   class the continuous arm is the principled tool, not a luxury. [[capture_full_per_axis_sweep]],
   [[discriminant_exact_question_check]], [[observable_binding_clarifies]].

## Strict-gate consequence
Chialvo did NOT reach DETECTED-AT-LOCUS → **Track 1.4 (Kaneko GCM) is gated OFF**: Kaneko is another
torus-breakdown map read by the same event-extracted spectral instrument, so it would most likely
reconfirm the same negative; building it now would not test a new hypothesis. Queued as a *lower*-value
"does the negative generalize across torus-breakdown maps?" option. The highest-value redirect is
**Track 4** (continuous front-end), which this negative directly motivates and which is independent
(gated only on Track 0, passed). Track 3.1 (pvc-11 torus-breakdown read) is **deferred**: its premise
was a Track-1-calibrated lens, which does not exist — applying an uncalibrated event-spectral
torus-breakdown reading to real data would be premature.
