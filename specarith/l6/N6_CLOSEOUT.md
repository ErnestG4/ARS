# n = 6 arc: close-out (round 79; session 3 of 3)

**The stop (Will, round 79, verbatim):** "an exact CS n = 6 prediction of corrected (B)'s block variance requires a ζ
extraction that retains beat terms; not available; arc stopped at the time box."
- Not funded (round 79): the full stage (c) run (~700 core-h) and G-b1 by brute force (~10³ core-h). Without a ζ
  extraction, neither feeds a prediction.
- A post-hoc qualification of what "beat terms" refers to came in during close-out (§3.2). It bears on the wording of
  the stop, not on the decision to stop. The wording is Will's call.

Records: `N6_STAGE_A.md`, `N6_STAGE_B.md`, `N6_STAGE_B_GATE.md`, `N6_STAGE_C.md`, `N6_STAGE_C_BOUND.md`; the decision
log is `../ph2/PH2_DECISIONS_2026-10-07.md`, rounds 74–79.

## 1. What stands
- **The deficit.** The zeros' block variance for corrected (B), against the exact U(N) value, is R(G) = 0.315, 0.209,
  0.183 and 0.157 at G = 300, 1,000, 3,000 and 10,000 (`N6_STAGE_A.md`). That is up to a five-fold deficit.
- **Its origin is arithmetic and long-range.** The exact U(N) block variance is flat in G to 0.05%, and CUE's
  covariance is gone by r ≈ 10. So the zeros' fall with G is entirely the zeros' own long-range arithmetic structure.
  The rounds 72–73 CUE "fall" was estimator bias.
- **Predicting it from the ratios conjecture at 6-point order needs a new analytic tool.** §2–§5 record why.

## 2. The exact four-term covariance form (stage (b), S2.1)
For disjoint windows (r ≥ 4), with ψ(X) = X³ − 3σ²X the influence function of the κ₃ estimator:

  **C(r) = κ₃₃ + 9κ₂₁κ₁₂ + 9κ₁₁κ₂₂ + 6κ₁₁³**

- κ_{a,b} are the joint count cumulants: κ_{a,b} = Σ S(a, i)S(b, j)·κ^{[i,j]}, with S the Stirling numbers of the
  second kind.
- κ^{[i,j]} = ∫_{A^i×B^j} T_{i+j} are the factorial cumulants, i.e. integrals of the Ursell (connected) functions.
- The σ² terms cancel exactly, which is ψ's influence-function property. T₆ enters only through κ^{[3,3]}, with
  coefficient 1.
- **Fredholm verification** (U(N), N = 10⁵, against stage (a)'s determinant C(r); κ^{[i,j]} from cyclic traces with
  the product Gauss–Legendre rule, 16 nodes):

  | r | relative agreement |
  |---|---|
  | 4.125 | 6·10⁻¹¹ |
  | 7.3 | 3·10⁻⁸ |
  | 20 | 4·10⁻⁸ |
  | 100 | 3·10⁻⁶ |
  | 1000 | 8·10⁻¹⁴ absolute, inside stage (a)'s 10⁻¹¹ floor |

- **What the form does not remove:** U(N)'s cancellation sits inside κ₃₃. At r = 100, κ₃₃ = −4.7·10⁻⁹ while
  κ^{[3,3]} = −2.75·10⁻⁴ and κ^{[1,1]} = −8.1·10⁻⁵, four to five orders. That is the determinantal rigidity, and why
  G-b1 needs ~12 nodes per coordinate.

## 3. The beat-term finding (stage (b), G-b3; round 77) and its close-out qualification
### 3.1 As recorded in round 77
G-b3 compared the (3, 3) piece at ζ PMAX 10³, at identical in-window nodes, on two sides. The brute side was the
unfiltered construction. The extraction side was the phase filter's non-oscillating class. Both were averaged over 15
triangular shifts, a two-period average that removes pure integer-frequency carriers exactly. The gap, brute minus
extraction, was 1–30% of the piece at r ≤ 500:
- ℓ = 15.75: 31%, 8%, 6% and 2.5% at r = 100, 173, 300 and 500;
- ℓ = 21.75: 1.0% and 1.6% at r = 173 and 500.

G-b3 FAILED as declared, and both wrong variants failed, so the gate had power. Round 77 attributed the gap to beat
terms: slow components from products of primes near e^ℓ mixing with the carrier. Hence "no phase-filter extraction
can work for ζ at this order."

### 3.2 Close-out qualification (post-hoc, descriptive; r = 100, lowest corrected (B) file only)
The averaging run (§4) stores every shift separately, so the content behind the gap can be resolved at r = 100. It
does not look like near-DC beats.
- **What the class-1 content is.**
  - Across the 15 shifts it advances by −0.885 rad per 1/8 step, at all 8 heights. That is a frequency of
    −1.127 cycles per unit: the carrier (−1) plus an offset of −0.127 cycles per unit, i.e. log n/ℓ with log n ≈ 2.0
    (n ≈ 7, small primes).
  - A beat from n ≈ e^ℓ would sit near 0 cycles per unit.
- **The across-file rotation agrees independently.** Across the file the class-1 value rotates by 0.27 rad. A beat
  with log n ≈ ℓ would rotate 1.75 rad; 0.27 rad matches log n ≈ 2–3.
- **So most of the gap is leakage, not beats.** The two-period triangular average passes about 1% of a component at
  1.13 cycles per unit, and this component has amplitude ~10–16. That leakage makes up most of the class-1 gap.
  - A descriptive fit separates the two: a polynomial envelope times e^{2πifs} with f free, plus a constant and a linear
    term. It attributes ~93% of the class-1 gap to the 1.13-cycle component (−0.26 of −0.28). It leaves a near-DC part
    of −0.015 to −0.021, which also does not rotate like an e^ℓ beat.
  - The class-1 fit leaves 0.3–0.4% of the rms.
  - Class 2 behaves the same way: −2.09 cycles per unit, with 3–9% of the rms left.
  - Class 3 is not resolved: the fit hits the scan edge with 47–49% left. It carries ~1% of the gap.
  - Caveat: a 1.75-unit window cannot separate true DC from frequencies |f| ≲ 0.3, so "near-DC" here is that whole band.
  - Generator: `../cs4/n6b_lavg_shiftfit.py` → `../cs4/results/n6b/lavg_r100/SHIFTFIT_100.0.json`.
- **Consequence.**
  - What G-b3 measured is the content that a two-period average passes. The block estimator's Bartlett sum at
    G ≥ 300 on the 1/8 grid suppresses a 1.13-cycle component far more strongly.
  - **At this point, therefore, the 31% gap overstates what the estimator sees of classes k ≠ 0 by roughly an order of
    magnitude.** By the fit, the near-DC part is ~0.5% of the piece, against the 8% TRI residual summed over classes in
    this file.
  - The round-77 attribution to prime products near e^ℓ is not supported here.
- **What is not established:**
  - other r, the higher height (ℓ = 21.75) and the other G-b3 points;
  - whether the phase filter would pass a gate built on the estimator's own kernel;
  - the fit is model-dependent.
- **What would settle it:** re-evaluating the G-b3 points with the estimator's own kernel (Fejér at G on the 1/8 grid)
  in place of the two-period average. That is not run; it is offered to Will (§8). The r = 300 per-shift data from §4
  will allow the same reading at a second r at no cost.

## 4. The averaging result (stage (b), S2.2; `../cs4/n6b_lavg.py`)
**Declared before running:** the file average multiplies class k's beat by S(r, k), the dephasing of a beat with
log n ≈ kℓ across the file. For the lowest file (zeros_46646000, ℓ 15.8202–15.8643):
- S(100, k = 1) = 0.878;
- S(300, k = 1) = 0.190.

For the two highest files S stays ≈ 1 up to r ~ 10³–10⁴. Read per class: |file average| / weighted rms over ℓ,
beside S.

**r = 100** (8 stratified heights × 15 shifts, all 120 tasks; `n6b_lavg.py summary` with CASES restricted to r = 100, run locally on the fetched task files → `../cs4/results/n6b/lavg_r100/LAVG_r100.json`):

| class | |file avg| / rms | S_pred |
|---|---|---|
| ±1 | 0.996 | 0.879 |
| ±2 | 0.826 | 0.567 |
| ±3 | 0.940 | 0.192 |

- **The summed beat** (classes k ≠ 0) is −0.547 to −0.571 across the file. Its file average is −0.562, with
  rms over ℓ 0.562.
- **Reading against the prediction: the prediction FAILS.** The class contents dephase far less than S predicts, at
  every k. File-averaging within the lowest file removes essentially none of the period-averaged class content at
  r = 100.
- **Diagnosis:** §3.2. The prediction's premise was that class k after the period average is dominated by beats with
  log n ≈ kℓ. That premise is false at this point. The dominant content carries small-prime offsets (log n ≈ 2–3),
  which rotate slowly with ℓ.
- **What this means for the averaging question.** Within the lowest file, the content G-b3 measured is fixed-height
  content, not averaged away.
  - Whether the estimator-visible near-DC part averages out is not answered here. It is ~7% of the class-1 content by
    the fit, and it too does not rotate like an e^ℓ beat.

**r = 300** (16 heights): running on spot; recorded here when it lands.

## 5. The stage (c) pilot: convergence and size record (round 78; `N6_STAGE_C.md`)
- **Quantity:** the arithmetic part (ζ − U) of the fully connected T₆, at r = 6, ζ ℓ = 15.75, PMAX 10².
- **Witnesses and criteria, declared before running:**
  - **Null:** U(N) through the exact determinant against the construction, |residual| ≤ 4·10⁻⁷ at 8 and 10 nodes.
  - **Witness:** a planted ρ₆ × (1 + 10⁻⁸) must fire and be recovered within 10%.
  - **Convergence:** |X₈ − X₁₀| ≤ 0.2|X₁₀| + 4·10⁻⁷ for the envelope E and the class-summed ΔI.
- **Status:** running on spot (616 tasks; 102 of the 379 ζ 10-node chunks done after 4.4 h).
- **Cost against the estimate:** it runs ~5× slower per process than the local timing behind the "~85 core-h" estimate,
  sharing the box with §4. Projected finish ~2026-10-24 evening.
- Recorded here as a convergence and size record when it lands. No full run follows (round 79).

## 6. The in-window repeated-node defect, caught before any result (round 78)
- **The defect.** The pilot as first committed integrated T₆ with the distinct-node rule inherited from round 77: sorted
  distinct node tuples × 3!. That rule equals the product Gauss–Legendre rule only for integrands that vanish at
  in-cluster coincidence. ρ_m and ρ₆ − ρ₃ρ₃ do; T₆ does not (T₂(x, x) = −1 for the sine process).
- **Measured** (U(N), r = 6, ∫T₆):

  | rule | 6 nodes | 8 | 10 | 12 |
  |---|---|---|---|---|
  | distinct-node rule (no convergence) | +1.5·10⁻³ | −2.4·10⁻³ | −7.5·10⁻³ | −5.4·10⁻³ |
  | product rule (24-node reference −0.0952269) | −0.0461 | −0.0934 | −0.09520 | −0.0952267 |

- **Caught** ~8 minutes after launch, before any task file was written. Stopped by explicit PIDs.
- **Corrected before any result was read.** The fix is the product rule folded onto sorted node multisets, with weights
  (3!/Π mult!)·Π w.
  - Every subset ρ with a repeated node is set to exactly 0.
  - That is exact because ρ_m ∝ d² at coincidence, verified for the ζ model on the mpmath path first:
    ρ₂ = 3.0230·10⁻⁴, 3.0230·10⁻⁶ and 3.0230·10⁻⁸ at d = 10⁻², 10⁻³ and 10⁻⁴.
- **Checked:**
  - the folded rule equals the trace formula to ~10⁻¹¹;
  - construction against determinant: 2·10⁻¹⁶ and 7.7·10⁻¹⁵;
  - the planted witness is recovered exactly.
- **Unaffected:** rounds 76–77, G-b3 and the algebra check, because their integrands vanish at coincidence.

## 7. Other records from the arc
- **Round-77 stage (c) bound: NOT ESTABLISHED.** It was unconverged at 6 nodes (E₈/E₆ = 0.12), and it bounded the whole
  (3, 3) piece by mistake instead of the declared connected term. Redefined in round 78 (§5).
- **G-b2 PASS** (round 76): the 3 + 3 reduction reproduces the validated cs4lr 2 + 2 term.
- **G-b1 (i), the algebra check, PASS:** the phase filter is exact for U(N) at 3 + 3, to ≤ 2.4·10⁻⁵.
- **Sibling check** (round 77): Stage 2's dropped ℓ-oscillating part was computed (one pair) and carried. No other
  banked result uses the phase filter as exact.
  - §3.2's reading suggests checking the same question at 2 + 2: was Stage 2's period-averaged diagnostic also mostly
    leakage? Not run.
- **S2.3:**
  - the U(N) cross-factor expansion separates (Taylor in window/r);
  - ζ's does not, under exact prime phases;
  - direct full-function evaluation on the 1/8 grid is unaffordable for ζ (10⁵–10⁶ core-h per configuration).

## 8. Open
- **L7, the spectral route** (`../OPEN_LEADS.md` L7): a sketch only.
- **Offered to Will, not run:** the estimator-kernel version of G-b3 (§3.2), which would settle whether the phase
  filter is what the estimator needs at 3 + 3.
  - **Rough size:** two G-b3 points (ℓ = 15.75, r = 100; ℓ = 21.75, r = 173) with a ±4-unit shift window at 1/8 in place
    of ±7/8, about 4× G-b3's per-point cost, ~100 core-h on spot.
  - If the phase filter passed it, the G-b3 obstacle as worded in the stop would not stand. The full prediction would
    still need G-b1 and the remaining n = 6 machinery.
