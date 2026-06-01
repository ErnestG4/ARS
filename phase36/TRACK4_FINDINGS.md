# Track 4 — Continuous Front-End Feasibility · Findings

**Phase 36, 2026-05-31.** Calibrator-only, falsification-gated. Config:
`TRACK4_CONFIG_JUSTIFICATION.md`. Ground truth: analytic Almost-Mathieu operator (golden θ, N=2584),
metal (λ<1, AC/transport) vs insulator (λ>1, pure-point/localized), transition at λ=1.
Driver: `phase36/track4_frontend.py`; raw: `track4_frontend_results.json`.

## Headline
**Neither F1 nor F2 is PROMOTABLE to a validated continuous arm — but for different, informative
reasons, and the continuous front-end demonstrably CARRIES the transition that event-extraction
(Track 1.1 Chialvo) lost.** §7.ter.19 reaffirmed with *positive, mechanism-named* evidence; the
result maps exactly what a continuous arm would need.

## The φ(t) bridge is sound (pre-check)
Wavepacket return amplitude φ(t)=⟨e₀|e^{−iHt}|e₀⟩ shows the textbook transport signature:
|φ| late/early ratio = 0.080 (λ=0.5 metal, decays) → 0.438 (λ=0.95) → 0.990 (λ=1.5 insulator,
recurs). Monotone metal→critical→insulator. So the continuous front-end's raw signal carries the
metal-insulator distinction directly.

## F1 — Hilbert instantaneous-phase → rotation-number stream  →  `CARRIES-TRANSITION / α-CONFOUND-UNRESOLVABLE`
Pipeline: φ(t) → Re → band-pass → Hilbert → unwrapped phase → 2π-crossing intervals → unit-mean → NNS.
- **Transition location (pinned α=0, default band 0.05–0.30 Hz, T=2000):** W1δ MONOTONE across λ —
  0.097 (λ0.5) → 0.034 (0.85) → 0.013 (0.95) → 0.004 (1.05) → 0.001 (1.25) → 0.001 (λ1.5). Metal
  phase-crossings are structured; insulator phase advance is clock-regular (W1δ→floor). A clean,
  monotone, transition-bracketing signal — exactly what event-extraction could NOT produce on the
  related Chialvo torus-breakdown.
- **Band knob-robustness (pinned α=0):** 4 bands, separation insul−metal = −0.096, −0.091, −0.091,
  −0.033 — all same sign (metal > insul). Band-robust. ✓
- **α CONFOUND sweep (the decisive catch):** separation is NOT α-robust at N=2584 —
  α=0.00: −0.096, α=0.13: **+0.002**, α=0.27: **−0.003**, α=0.41: −0.112. At α∈{0.13,0.27} the metal
  W1δ collapses to floor and the separation vanishes. This is the inherited phase-knob confound
  (α = the operator phase φ, the SAME d.o.f. that is φ-noisy at N=2584 — the α-ensemble that made
  the 35b sub-quadrant branch UNRESOLVED).
- **Why it can't be factored out (the load-bearing blocker):** the protocol says pin α in the
  high-N-stable regime (N≳5×10⁴, where the α-spread collapses) for the headline. **But F1 needs the
  return amplitude φ(t), which needs eigenVECTORS (weights |v_k[0]|²) — O(N²) memory (~20 GB at
  N=5×10⁴).** So F1 is structurally capped at moderate N (a few thousand), exactly where α-noise is
  present. Unlike the eigenvalue-only spacing leg, F1 cannot escape the substrate's phase-noise by
  going to high N. The α-instability is *consistent with* the substrate's known phase-noise, but F1
  cannot reach the regime that would confirm it ⇒ promotion BLOCKED by an unresolvable confound
  (not refuted; not promotable).
- **Resolution path (queued):** compute the site-0 spectral weights |v_k[0]|² as Gauss-quadrature
  weights via an O(N) Lanczos / continued-fraction method (not the full O(N²) eigenvector matrix),
  which would let φ(t) — and hence the α-sweep — reach N≳5×10⁴ and cleanly attribute the α-instability.

## F2 — spectral-measure (KDE-DOS) → IDS-unfold  →  `SEPARATES_ROBUST_BUT_NO_FLOOR`
Estimate DOS by Gaussian KDE on the eigenvalues; unfold eigenvalues through the smoothed cumulative
DOS; read W1δ. Knob: KDE bandwidth h.
- **Separation:** insul−metal W1δ = +0.337, +0.365, +0.369, +0.344 across h ∈ {0.25,0.5,1,2}×Silverman
  — robustly positive (insulator more structured), knob-robust. ✓
- **But NO floor:** metal W1δ = 0.48 / 0.60 / 0.76 / 1.00 (rising with h) — nowhere near the banked
  rotation-number floor (≈0.005). The smoothed density does NOT capture the fine IDS, so unfolding
  leaves O(0.5) residual fluctuation even in the AC/metal regime.
- **Conclusion:** a smoothed-spectral-density continuous front-end SEPARATES the regimes robustly in
  the correct direction, but does NOT inherit the banked validation — the metal→floor is load-bearing
  on the **exact rotation-number IDS**, not on "a spectral measure." F2's inheritance is partial
  (direction yes, floor no). NOT promoted (strict criterion requires floor recovery).

## What this buys the program (both outcomes are wins)
1. **§7.ter.19 reaffirmed with positive evidence**, and the knob that breaks each front-end is named:
   F2 — the estimator smoothing loses the floor; F1 — the eigenvector-O(N²) wall prevents factoring
   out the α phase-confound.
2. **The continuous arm is the right TOOL for this transition class, but not in turnkey form.** F1 at
   pinned α gives the monotone λ-signal that event-extraction (Chialvo) could not — corroborating the
   Track-1.1 convergence (transition lives in continuous modulation). The continuous arm needs (a) the
   *exact* IDS, not a smoothed density (F2 lesson), and (b) an O(N) spectral-weight method to escape the
   α-confound at high N (F1 lesson). Both are concrete, queued engineering steps — not open-ended.
3. **No promotion to real continuous data** (the gate did not pass) — §7.ter.19 holds; Track-3-style
   continuous substrates remain out until a front-end passes the gate.

Status tags: F1 `CARRIES_TRANSITION_α-CONFOUND-UNRESOLVABLE_AT_REACHABLE_N`;
F2 `SEPARATES_ROBUST_BUT_NO_FLOOR`. [[sweep_inherited_knob_independently]],
[[gate_certifies_half_say_so]], cross-refs Track 1.1 convergence.
