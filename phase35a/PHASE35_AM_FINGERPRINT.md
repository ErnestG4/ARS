# PHASE 35 — Almost-Mathieu Substrate Fingerprint (cross-substrate-comparison feature record)

**Status:** fingerprint feature inventory, cut 2026-05-21 pre-compaction.
**Framing (Will, 2026-05-21):** AM is no longer a substrate-of-interest for utility
extraction. It is one substrate to be *fingerprinted*; the utility is the fingerprint
and its comparison to other substrates (operators mapping Farey rationals / arithmetic
patterns → statistical distributions). **The reframe inverts signal/noise:** the
L-underconvergence pathology, N-scaling, θ-class sensitivity, and Fibonacci-N resonance
— treated as instrument problems through rev-5.2 — ARE the fingerprint.

**Purpose of this file:** capture the AM signature numbers + their semantic context
NOW, while the full conditions-and-meaning mapping is in-conversation, before compaction.
Format is a starting inventory; reshape to the cross-substrate comparison schema once
that schema is defined (the pivot). Source commits cited per feature.

---

## 0. Readout definition (what the fingerprint is OF)

- **Operator:** almost-Mathieu / Harper, tridiagonal: diagonal 2λcos(2π(θn+φ)), off-diag 1.
- **Arithmetic parameter:** θ (frequency). Default golden mean (√5−1)/2; continued-fraction /
  Farey structure of θ is the arithmetic input. One alt measured: silver mean √2−1 (C1).
- **Readout leg:** ratio-free rotation-number IDS unfold (`unfold_rotnum`, structurally
  ref-N-free, `unfold_rotnum.py:156-157`). Convergence parameter L_iter.
- **Statistic:** W1δ = E|s−1| (Wasserstein-1 of unfolded NNS to the unit clock). Clock=0,
  Poisson(=2/e)≈0.736.
- **Ensemble:** α-ensemble over φ∈[0,0.5) (deterministic, period-0.5 in φ — §7.ter.48).
  Two reductions used so far: mean_φ(W1δ), spread_φ = ptp_φ(W1δ). **Per-φ pattern shape
  itself is unextracted signal — see §6.**

---

## 1. Spectral-type contrast across the λ=1 critical point (the primary AM signature)

AM has a proven AC/PP transition at λ=1 (Avila–Jitomirskaya). The W1δ response:

| Regime | λ | L-converged W1δ (substrate) | character |
|---|---|---|---|
| Subcritical (AC) | 0.5 | ≈0.00013 (N=100k, bh22pfzoa) | near-clock |
| Subcritical (AC), near-crit | 0.995 | small, δ-dependent (~0.016 @N=100k L1.6e6) | near-clock+residual |
| Supercritical (PP) | 1.5 | mean≈0.30 (N=50k) / 0.44 (N=70k) / 0.50 (N=100k) | NOT at Poisson 0.736 |
| Critical | 1.0 | NOT MEASURED (held; T1/T2-core/§3-(A)) | — |

**Fingerprint note:** the supercritical (localized/PP) L-converged W1δ mean is well BELOW the
Poisson limit (0.30–0.50 vs 0.736) at these finite N — the finite-N localized-phase NNS is
not pure-Poisson. This sub-Poisson localized value is itself a substrate feature.

---

## 2. L-convergence law (resolution-interaction signature — monotone-N-growing)

The L=1e5 → L-converged growth of the supercritical (δ=0.5, λ=1.5) W1δ SPREAD, vs matrix
size N. **Monotone super-linear** (the headline structural finding, rev-5.2 §10):

| N | stored spread @L=1e5 | substrate spread (L-conv) | growth factor | source |
|---|---|---|---|---|
| 50000 | 0.123 | 0.115 (L=2.56e7) | **0.93×** | box6iq1j4 |
| 70000 | 0.0766 | 0.382 (L=2.56e7) | **4.99×** | b0haqgof3/Test2 |
| 100000 | 0.00715 | 0.847 (L=6.4e6, conv) | **118.5×** | d069ec8 |

- L-transition concentrated at L=1e5→1.6e6 where it occurs; asymptotes (~10%) past 1.6e6.
- At N=50k there is essentially NO L-transition (L=1e5 already substrate).
- **Sub-side L-decay rate (α) is L-range-dependent** (Test 3, 7a66ff6): N=70k α drops
  1.25 (L=1e5→1.6e6) → 0.50 (L=1.6e6→6.4e6); N=125k holds α≈1.0. Sub-side substrate
  unreachable at feasible L for N=70k/125k (still 41–47× substrate at L=6.4e6).
- **Mechanism (open):** why does the L=1e5 artifact suppress sup_spread super-linearly
  with N? Candidate: matrix-dimension-dependent Birkhoff/rotation-number convergence rate.
  Slate-4 territory.

**Fingerprint discriminator:** the *shape* of growth-factor-vs-N (here super-linear) is a
substrate × readout-leg signature. Other substrates under the same leg will have their own.

---

## 3. θ-class (Diophantine) sensitivity — the Farey-relevant axis (C1, 9020c24)

How the L=1e5 W1δ spread changes between Diophantine classes (golden vs silver mean),
at N=70k, δ=0.5, L=1e5:

| leg | golden spread | silver spread | silver/golden |
|---|---|---|---|
| sub (λ=0.5) | 2.68e-05 | 9.52e-05 | **3.55×** (θ-class-sensitive) |
| sup (λ=1.5) | 0.0766 | 0.0989 | **1.29×** (θ-class-universal within ~30%) |

**Fingerprint discriminator (directly Farey-germane):** AC-leg statistic is sensitive to
the *specific* Diophantine class (continued-fraction approximant structure); PP-leg is
θ-class-universal. **Severely undersampled axis** — only 2 θ-values at 1 cell, 1 L.
This is the most fingerprint-relevant gap (see §7).

---

## 4. Number-theoretic resonance — Fibonacci/commensurate-N (C2, aa33e44)

Contamination ratio at N=F₂₄=46368 (Fibonacci-commensurate) vs {N=43k, N=50k} bracket,
δ=0.5, both legs:

| leg | F₂₄ anomaly vs bracket | terminal |
|---|---|---|
| sub (λ=0.5) | **+89%** | COMMENSURATE_ANOMALY |
| sup (λ=1.5) | +20% | NO_ANOMALY |

**Fingerprint discriminator:** AC leg shows a commensurate-N (Fibonacci, i.e. golden-θ
convergent-denominator) resonance; PP leg does not. Likely SEPARATE mechanism from the
monotone-N L-pathology (rev-5.2 §10: pattern is monotone, not resonance-spiked at
F₂₅/F₂₆ — though those specific N's unmeasured). Directly relevant to "operators matching
Farey rationals": the commensurate-N resonance IS a Farey-structure response.

---

## 5. N-scaling of contamination ratio (Test 1, aa33e44)

Ratio = per-φ-shift-ptp / L=1e5-spread, vs N, δ=0.5:

- sub: α ≈ 2.46 (log-log ratio-vs-N)
- sup: α ≈ 2.99

**Caveat (rev-5.2):** this is RATIO-scaling, NOT magnitude-scaling. Misleading about
substrate magnitude (overturned at N=100k by direct measurement: ratio-α predicted nothing
like the 118× magnitude). Keep as a ratio-axis feature, not a magnitude predictor.

---

## 6. φ-response pattern shape — UNEXTRACTED SIGNAL (available in existing rawtables)

We have per-φ W1δ values (16 φ) stored in: `sub_phi_resolved_L_rawtable.json`,
`sup_phi_resolved_L_rawtable.json`, `test1_flipN_phi_rawtable.json`, `test2/tier2_*_rawtable.json`.
We have only ever used scalar reductions (mean_φ, ptp_φ). The **deterministic period-0.5
φ-pattern's SHAPE** (harmonic content / symmetry / cross-cell pattern correlation) is rich
unused signal and is likely a strong fingerprint discriminator. **Recommended sweep
analysis (analysis-only, no compute):** FFT/harmonic decomposition of the per-φ W1δ pattern
per cell; cross-cell pattern-correlation; whether sub and sup legs share φ-pattern phase.

---

## 7. Fingerprint gaps (new measurement; the pivot's call, mostly the program proper)

- **θ-sweep across Diophantine classes (HIGHEST fingerprint value, Farey-direct).** C1 is
  2 θ-points. A fingerprint comparison wants the θ-response characterized — e.g. noble
  numbers, metallic means, generic Diophantine, near-Liouville. New compute; arguably IS
  the cross-substrate program for AM, not a pre-pivot item.
- **Fibonacci/Farey-N resonance map** — characterize the commensurate-N resonance across
  F_k, and whether it appears for other θ's convergent denominators.
- **Critical-slice (λ=1) NNS** — held under §3-(A)/T-matrix; the actual critical fingerprint.
- **Full NNS distribution (not just W1δ)** — W1δ is a lossy scalar projection. For
  fingerprinting, the distribution shape may be the richer object; requires re-running
  eigensolves to extract spacings (expensive).

---

## 8. Demoted to "one readout among many" (was the verdict machinery)

The Step-1 verdict apparatus (no-FP / sensitivity / transition_diagnostic / §C floor) is,
under the fingerprint reframe, **one particular scalar reduction + threshold over the
W1δ response surface.** Its retraction status (no-FP retracted 2/3 cells f7ae4e9/d069ec8,
N=50k surviving 928c0a4; sensitivity polarity-inversion STEP1_SENSITIVITY_POLARITY_INVERSION)
is about utility-extraction, NOT about the fingerprint. The fingerprint is the response
surface; the verdict was one question asked of it. **For cross-substrate work, carry the
response surface (§§1–6), not the verdict terminals.**

---

## 9. Source-commit index (for re-derivation post-compaction)

- aa33e44 Test 1 flip-N φ + C2 Fibonacci (α-scaling, commensurate resonance)
- 9020c24 C1 θ-robustness (silver vs golden)
- e53154a Test 2 sup L-extend N=70k (substrate 0.382, growth 4.99×)
- d027967 Sensitivity Tier 1 (per-cell criterion ratios)
- 928c0a4 Tier 2 sup N=50k (substrate 0.115, growth 0.93×)
- f7ae4e9 Step-1 verdict math Tier 1 N=70k (flip)
- d069ec8 Tier 2 sup N=100k (substrate 0.847, growth 118.5×)
- 7a66ff6 Test 3 sub L-extend N=70k/125k (α L-range-dependence)
- decision record: memory `phase35_am_arc_design.md` (full chronology)
- brief: rev-5.2 (in Will's messages; not in repo)
