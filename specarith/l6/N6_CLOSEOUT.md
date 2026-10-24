# n = 6 arc: close-out (rounds 79–80; session 3 of 3)

**The stop: pending the round-80 settling test (§3.3).** Round 80 fixed both readings in advance:
- **PASS at both points** → "paused at the time box; extraction viable under the estimator's kernel; resumption is a
  new arc, Will's call".
- **FAIL at either** → "extraction inadequate under the estimator's own kernel", with the slow-content share at each
  point.

Not funded either way (rounds 79–80): the full stage (c) run (~700 core-h) and G-b1 by brute force (~10³ core-h).

**Struck in round 80.** Two statements are withdrawn:
- round 79's stop wording, "an exact CS n = 6 prediction of corrected (B)'s block variance requires a ζ extraction that
  retains beat terms; not available; arc stopped at the time box";
- round 77's inference, "no phase-filter extraction can work for ζ at this order".

Both were asserted before the averaging test (§4) and the shift-resolved reading (§3.2). That reading shows the G-b3
gap is carried mainly by a near-carrier leak through G-b3's two-period average, not by beat terms.

Records: `N6_STAGE_A.md`, `N6_STAGE_B.md`, `N6_STAGE_B_GATE.md`, `N6_STAGE_C.md`, `N6_STAGE_C_BOUND.md`; the decision
log is `../ph2/PH2_DECISIONS_2026-10-07.md`, rounds 74–80.

## 1. What stands
- **The deficit.** The zeros' block variance for corrected (B), against the exact U(N) value, is R(G) = 0.315, 0.209,
  0.183 and 0.157 at G = 300, 1,000, 3,000 and 10,000 (`N6_STAGE_A.md`). That is up to a five-fold deficit.
- **Its origin is arithmetic and long-range.** The exact U(N) block variance is flat in G to 0.05%, and CUE's
  covariance is gone by r ≈ 10. So the zeros' fall with G is entirely the zeros' own long-range arithmetic structure.
  The rounds 72–73 CUE "fall" was estimator bias.
- **Predicting it from the ratios conjecture at 6-point order is not done.** §2–§6 record how far the arc got and why
  it stopped.

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

## 3. The G-b3 gap: a near-carrier leak through the two-period average (round 80 rewrite)
### 3.1 The sealed gate (round 77; stays as sealed)
**What G-b3 compared.** The (3, 3) piece at ζ PMAX 10³, at identical in-window nodes, on two sides:
- **brute:** the unfiltered construction;
- **extraction:** the phase filter's non-oscillating class.

Both sides were averaged over 15 triangular shifts. That is a two-period average, which removes pure integer-frequency
carriers exactly.

**The gap,** brute minus extraction:
- ℓ = 15.75: 31%, 8%, 6% and 2.5% of the piece at r = 100, 173, 300 and 500;
- ℓ = 21.75: 1.0% and 1.6% at r = 173 and 500.

**G-b3 FAILED as declared.** Both wrong variants failed, so the gate had power. That FAIL stands.

**Superseded:**
- round 77 attributed the gap to beat terms (slow components from products of primes near e^ℓ mixing with the
  carrier);
- round 77 inferred that no phase-filter extraction can work for ζ at this order.

Both are struck (header; round 80).

### 3.2 What carries the class-1 gap (post-hoc, descriptive; lowest corrected (B) file, r = 100 and 300)
**Main carrier: a near-carrier leak.**
- **The component.** The class-1 content that passes G-b3's two-period average is dominated by a component at about
  1.04–1.13 cycles per unit: the carrier plus a small-prime offset of log n/ℓ, with log n ≈ 0.6–2.
  - −1.127 at r = 100;
  - −1.03 to −1.05 at r = 300.
- **How it was read.** The averaging run (§4) stores all 15 shifts at each height, so the phase advance per 1/8 step
  gives the frequency directly. A fit of a polynomial envelope × e^{2πifs}, plus a constant and linear part, leaves
  0.3–0.9% of the rms.
- **The leak.** The two-period triangular average passes ~10⁻² (r = 100) to ~10⁻³ (r = 300) of this component. Its
  amplitude is ~10–16, so the leak makes up most of the gap:

  | | r = 100 | r = 300 |
  |---|---|---|
  | leak, share of the class-1 gap | ~93% | ~80% |
  | leak, value | −0.26 of −0.28 | −0.29 to −0.37 of −0.35 to −0.46 |

**The slow remainder is not e^ℓ-like either.**
- **Size:** the near-DC part (|f| ≲ 0.3; a 1.75-unit window cannot resolve finer) is −0.015 to −0.021 per class at
  r = 100 and −0.06 to −0.085 at r = 300. That is ~7% and ~20% of the class-1 gap.
- **Rotation:** across the file it rotates no faster than the leak component, which turns 0.27 rad (r = 100) and
  ~0.2 rad (r = 300). An e^ℓ beat would rotate 1.75 and ~4.6 rad.

**Classes 2 and 3.**
- Class 2 behaves like class 1: −2.09 cycles per unit at r = 100 and −2.2 at r = 300, with 3–20% of the rms left by the
  fit.
- Class 3 is small (≤ 1% of the gap) and only partly resolved.

**Generators:** `../cs4/n6b_lavg_shiftfit.py` → `../cs4/results/n6b/lavg_r100/SHIFTFIT_100.0.json` and
`../cs4/results/n6b/lavg/SHIFTFIT_300.0.json`.

**What this does and does not establish.** The block estimator's own kernel suppresses a ~1.1-cycle component far
more strongly than G-b3's average does. So G-b3's gap overstates the slow content: ~10× at r = 100 and ~5× at r = 300
in this file. Whether the phase filter passes under the estimator's own kernel is the settling test (§3.3). The fit is
model-dependent, and ℓ = 21.75 and r ≥ 500 are not resolved.

### 3.3 The settling test (round 80; POST-HOC; declared and committed before computing; `../cs4/n6b_settle.py`)
**The kernel, derived from the estimator code (`../cs4/b2_est.py`).**
- **The window starts.** They are u_q + jL, with u_q = qL/NU, q < NU = 32 and L* = 4. Every start lies on the grid
  kΔ, Δ = 1/8.
- **Segments.** A window belongs to the segment holding its start. Each offset puts exactly G/L windows in a segment.
- **Linearisation.** Linearising the offset-averaged k-statistic gives k̄₃ − κ₃ = (1/NU) Σ_q (1/n_q) Σ_j ψ(d_qj). So
  W(G) = G·Var(segment mean) = Δ Σ_k c_k C(kΔ), where c_k are the lag counts of the enumerated starts divided by
  M = G/Δ.
- **Check.** Enumerated from the code's start rule, c_k equals the Bartlett weights 1 (k = 0) and 2(1 − k/M) to
  2·10⁻¹⁶, at all four G.
- **Not modelled:** the k-statistic's nonlinear O(1/n) terms and the bootstrap's centring (stage (a)'s n_s/(n_s − 1)).
  These are the same as in stage (a).

**Known answer: PASS (run locally before any ζ point;** `../cs4/results/n6b/settle/KERNEL.json`**).** The kernel
applied to stage (a)'s exact U(N) C(kΔ) (all 80,001 points) reproduces stage (a)'s W_B at relative 0–2.2·10⁻¹⁶. The
criterion was 10⁻⁹:

| G | W_B |
|---|---|
| 300 | 0.211190771786 |
| 1,000 | 0.211117034265 |
| 3,000 | 0.211095915943 |
| 10,000 | 0.211088507392 |

Stage (a) was itself checked against the L6 long CUE baseline: AGREES, max |z| 2.14.

**Point evaluation.**
- **The partition.** The kernel is global (r ∈ [0, G)). A point value is one member of an exact partition of it:
  τ(x) = cos²(π/2·β(|x|/h)), with β the smootherstep 6t⁵ − 15t⁴ + 10t³ and h = 5. It satisfies Σ_j τ(r − jh) = 1, so
  W = Σ_j Δ Σ_k c_k τ(kΔ − jh) C(kΔ) exactly.
- **The local kernel.** At r₀ it is w(r) = c(r)·τ(r − r₀) on r = r₀ + kΔ, |k| ≤ 39 (79 points), normalised to Σw = 1,
  with c at G = 10,000.
- **Transfer (predicted, from the weights):**
  - |T| ≤ 5.4·10⁻⁵ anywhere in [0.9, 1.2] cycles per unit: −3.6·10⁻⁶ at 1.04 and 7.8·10⁻⁶ at 1.13;
  - ≤ 1.5·10⁻⁷ in [1.9, 2.4];
  - 0.980 at 0.02 and 0.882 at 0.05.
  - For comparison, G-b3's two-period average passes ~10⁻²–10⁻³ near 1.1.

**Quantity, points and tolerance (G-b3's, unchanged).**
- **Quantity:** the (3, 3) piece at ζ PMAX 10³, ℓ = 15.75, 4 in-window nodes.
  - brute = Σ classes (ρ₆ − ρ₃ρ₃);
  - extraction = class 0 − ρ₃ρ₃;
  - both under w.
- **Points:** r₀ = 100 and 300.
- **Tolerance:** |brute − extraction| ≤ 0.01·|brute|.

**Witnesses (on the real per-point values, in `summary`).**
- **Tone.** Plant 16·e^{±2πi·1.04(r − r₀)} in classes ±1, where 16 is the largest measured class-1 amplitude. The
  change in brute − extraction must:
  - match the predicted 2·16·T(1.04) within 1%;
  - stay ≤ 10% of the tolerance (a near-carrier leak cannot decide the reading).
- **Slow.** Plant A_s·cos(2π·0.02(r − r₀)) in classes ±1, with |A_s| = 3 × tolerance and the sign of the measured gap.
  The change must match A_s·T(0.02) within 1%, and the planted reading must FAIL (the test can see slow content).
- **WITNESS_OK** iff all four hold at both points.

**Synthetic check of the code path (local, not a gate).**
- A class-1 tone of amplitude 16 at 1.13 cycles per unit, plus a slow part of −0.002 per class, reads PASS: share
  −0.3%, leak 1.1·10⁻⁴.
- The same with −0.05 per class reads FAIL: share −9.1%.
- The witnesses matched their predictions in both cases.

**Reading.**
- **PASS** iff the known answer holds, WITNESS_OK, and both points are within tolerance.
- **FAIL** iff the known answer holds, WITNESS_OK, and either point is outside tolerance. The slow-content share
  (brute − extraction)/brute is reported at each point.
- **VOID** otherwise.

**Cost and run.** 158 point tasks, measured at ~0.7 core-h each on spot (the averaging run's tasks are the same
computation): ~110 core-h. Launcher `../cs4/run_n6b_settle_spot.sh`; outputs `../cs4/results/n6b/settle/`.

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

- **The summed class content k ≠ 0** ("beat" in LAVG.json) is −0.547 to −0.571 across the file. Its file average is −0.562, with
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

**r = 300** (16 stratified heights × 15 shifts, all 240 tasks; spot summary under its own status 0 →
`../cs4/results/n6b/lavg/LAVG.json`):

| class | |file avg| / rms | S_pred |
|---|---|---|
| ±1 | 0.996 | 0.190 |
| ±2 | 0.605 | 0.167 |
| ±3 | 0.888 | 0.132 |

- **The summed class content k ≠ 0** is −0.69 to −0.91 across the file, with file average −0.846 and rms over ℓ 0.849. The full
  (3, 3) piece runs from −0.84 to −6.54 across the same file.
- **Reading against the prediction: FAILS again, more widely.** S predicted a five-fold suppression of class 1; there
  is none.
- **Diagnosis:** as at r = 100 (§3.2). The period-averaged class content is dominated by carriers offset by
  small-prime frequencies (−1.04 cycles per unit for class 1), which barely rotate across the file.

**Answer to the averaging question, for the content G-b3 measured:** within the lowest corrected (B) file it does not
average out, at r = 100 or 300. The two highest files are narrower in ℓ, so the same holds there a fortiori. That leaves
the near-DC part of the class content, the part the estimator sees. Here it is 7% (r = 100) to 20% (r = 300) of the
period-averaged gap, and it does not average out across the lowest file either.

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
- **Superseded by round 80:** the offer below is now the settling test (§3.3).
- **Offered to Will, not run:** the estimator-kernel version of G-b3 (§3.2), which would settle whether the phase
  filter is what the estimator needs at 3 + 3.
  - **Rough size:** two G-b3 points (ℓ = 15.75, r = 100; ℓ = 21.75, r = 173) with a ±4-unit shift window at 1/8 in place
    of ±7/8, about 4× G-b3's per-point cost, ~100 core-h on spot.
  - If the phase filter passed it, the G-b3 obstacle as worded in the stop would not stand. The full prediction would
    still need G-b1 and the remaining n = 6 machinery.
