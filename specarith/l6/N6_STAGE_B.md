# n = 6, stage (b): the 3 + 3 long-range extraction (the derivation, as it goes)

Gates: `N6_STAGE_B_GATE.md` (G-b1 U(N), G-b2 reduction, G-b3 brute force; the wrong variants must fail all three).
Time box: 3 sessions from the start of the derivation (round 75). **Session 1: 2026-10-22.**

## Session 1 (2026-10-22): the extraction is a phase filter
**The observation.** In the ratios construction (`cs4/ratios_t5.py`, `Model.ratio_jet`), each term of J(A; B) is
labelled by subsets S of A and T of B with |S| = |T|. Its x-dependence carries an explicit e^{−L(ΣS + ΣT)}.
- A carries the values i x_p (p ∈ P), and B carries −i x_m (m ∈ M). So the phase is Φ = i·Σ_k c_k x_k, with
  c_k = +1 for the points of P in S, −1 for the points of M in T, and 0 otherwise.
- The rest of the term (Z-ratio factors, and 𝒜_ζ for ζ) depends on the points only through smooth functions of their
  differences.
- **Shifting the second cluster by r multiplies a term by e^{−iL·r_t·Σ_{k∈B} c_k}.** So the term is non-oscillating
  in r iff Σ_{k ∈ cluster B} c_k = 0.
- The multilinear-jet derivative that gives J preserves each term's phase. So selecting terms by this rule is exact at
  every order. It involves no asymptotic expansion and no new transcription.
- It is the rule `cs4fastc.connected` applies to CS08's closed-form pieces for 2 + 2 (a piece oscillates iff
  c₃ + c₄ ≠ 0), lifted to the ratios definition for any cluster sizes (a, b).

**The extracted object.**
- K_ab(x_A, x_B) = ρ_{a+b}^{non-osc}(x_A ∪ x_B) − ρ_a(x_A)·ρ_b(x_B), in unit-spacing densities.
- For corrected (B), C_long(r) = Σ_{a,b = 1..3} c_a c_b ∫_{A^a × B^b} K_ab, with c_a the falling-factorial
  coefficients of ψ (`N6_STAGE_A.md`). The (3, 3) term is the new n = 6 piece. The lower (a, b) use the same code.
- Code: `cs4/n6b_extract.py` (`FilteredModel.rho_f`, `K_ab`).

**First gate result, a local smoke run (G-b2 at PMAX 10³).**
- The extraction's own (2, 2) instance against `cs4fastc.connected(nonosc_only=True)` at ℓ = 15.75 and 21.75, two
  pairs of in-pair offsets, and r = 20, 50, 100, 300, 1000.
- Agreement is to 10⁻¹⁴–4·10⁻¹³ absolute, against values of 2.5·10⁻⁵ to 0.05. The declared precision is 1.1·10⁻⁹
  relative.
- Both wrong variants fail: the sign-reversed extraction, and the (1, 1) reduction in its place.
- **The term is large in the ζ regime:** the 2 + 2 non-oscillating ρ₄ᶜ is 0.025–0.05 at r = 50–1000. So G-b2 has
  resolution there. The official run adds `cs4lr` itself on its grid and PMAX 3·10⁵ (on spot).

**Still open in session 1:**
- G-b1 needs U(N) at large N with r up to 1000. The jets' cancellations at large L are to be checked against the
  determinant first. If they need a moderate N, the known answer is recomputed at the same N with stage (a)'s
  Fredholm code.
- G-b3 needs stage (c)'s n = 6 U(N) pointwise gate to pass first.
- The bond-order definitions of the wrong variants for C(r): (i) the (1, 1) term only; (ii) the (2, 2) contribution
  with its sign reversed.

## Session 1, continued: G-b2, and what G-b1 costs as declared
**G-b2 at PMAX 10³ (official, spot): PASS; both wrong variants fail.**
- The first official run applied cs4lr's 1.1·10⁻⁹ as relative. `cs4lr_check` defines it as the largest absolute
  difference, and the gate declares the larger of that and the cutoff change.
- The code was corrected to 1.1·10⁻⁹ absolute, the stricter choice (3c16cc59). In that first run, at PMAX 3·10⁵ the
  extraction matched cs4lr to ≤ 7·10⁻¹³ and cs4fastc to ≤ 2·10⁻¹⁰.
- cs4lr cannot run at PMAX ≤ 1000 (its Fourier group above 1000 is empty), so the PMAX 10³ run compares cs4fastc
  only.

**G-b1 as declared is infeasible by direct quadrature** (`n6b_quadcheck.py`). Assembling the full CUE_N C(r) from
in-window Gauss–Legendre quadrature of the determinant ρ's gives these relative errors against stage (a)'s exact
Fredholm value:

| r | exact C(r) | 6 nodes | 8 | 10 | 12 |
|---|---|---|---|---|---|
| 4.125 | −1.95·10⁻² | 0.83 | 0.081 | 1.6·10⁻³ | 1.1·10⁻⁵ |
| 7.3 | 9.20·10⁻⁶ | −42 | 0.13 | 0.051 | 6.9·10⁻⁴ |
| 20 | −3.46·10⁻⁶ | 7.5 | −0.052 | −4.4·10⁻³ | −5.9·10⁻⁵ |
| 100 | −6.86·10⁻⁹ | 138 | 0.22 | −1.5·10⁻⁴ | −2.2·10⁻⁵ |

- **Why so many nodes:** the (a, b) pieces cancel heavily. C(100) is 7·10⁻⁹, while each piece is far larger. So 1%
  needs 10–12 nodes per coordinate.
- **The cost:** that is about 9·10⁴ jet evaluations per r (48,400 for the (3, 3) piece alone), roughly 1,600 core-h
  for the 60-point grid. **The scoping draft's "8 nodes per dimension" estimate was wrong for the same reason, and
  that applies to the ζ production run too.**

**What the derivation has to supply next (session 2), the separation.**
- For r ≫ 4, each kept term factorises into in-cluster phase factors, which are unit-scale and oscillatory, times
  cross factors, which are smooth in r and vary over the window only at relative order 4/r.
- Expanding the cross factors about the window centres in powers of (in-window offset)/r turns the 6-dimensional
  integral into in-cluster integrals (3-dimensional, computable once) times cross factors and their derivatives at
  the centres.
- Truncation is checked order by order against the exact answer.
- That makes C_long(r) cheap at every r. It is the critical path for both G-b1 and the ζ evaluation.

**A cheaper G-b1 variant, for Will to decide (not adopted):** compare the extraction with the determinant's full C,
period-averaged over 8 shifts, at identical quadrature nodes. The quadrature error then cancels in the comparison, so
4–6 nodes suffice, at a reduced r grid. That tests the phase filter at 3 + 3 without the separation, but not against
the exact Fredholm answer.

**G-b2 official result: PASS at both cutoffs; both wrong variants fail** (`cs4/results/n6b/GB2_P*.json`).
- PMAX 10³: max |extraction − cs4fastc| = 3.9·10⁻¹³.
- PMAX 3·10⁵: max |extraction − cs4lr| = 7.3·10⁻¹³, and against cs4fastc 2.0·10⁻¹⁰.
- Both are against the declared 1.1·10⁻⁹ absolute, on values of 6·10⁻⁵ to 0.05.

**Round 76:** G-b2 PASS accepted. The relative/absolute tolerance coding error in the first official run is recorded
here and in 3c16cc59, corrected to the declared absolute criterion. **Session 1 of 3 is used.**

**Cost update (round 76; detail in the scoping draft §7).**
- 1% on the total C(r) needs 10–12 nodes per coordinate, because the pieces cancel. A single (3, 3) piece needs ≥ 8
  nodes for 0.2%: 4 and 6 nodes underestimate it by 71% and 26%.
- At 12 nodes that is ~8.9·10⁴ configurations per r. Brute force is ruled out at any useful cutoff: ~6·10⁴ core-h
  per height at PMAX 10³.
- The session-2 separation is the only route to the ζ prediction.
- G-b3 stays feasible (~15–25 core-h), because it compares at identical nodes.
- The committed 4-node (c) bound will likely come back "not established". A 6-node variant with an 8-node spot check
  would cost ~130 core-h; that is for Will to choose.

## G-b1 (i): the algebra check (not G-b1)
**First run (2c22dd0b, `cs4/results/n6b/ALGEBRA_CHECK.json`): FAIL as declared.**
- It passes at r = 100 and 300 (every piece within 10⁻⁴). It fails at r = 20 and 50.
- **Diagnosis:** every (a, b) piece is off by the same factor, determinant over extraction = 1.00130 at r = 20,
  1.00020 at 50 and 1.00005 at 100.
  - The check averaged the determinant over the triangular two-period kernel, but compared it with the unaveraged
    extraction.
  - That average multiplies a non-oscillating 1/r² term by 1 + 3σ²/r², with σ² = 0.164. This predicts 1.00123,
    1.00020 and 1.000049, which is the observed factor to 6% of the effect at r = 20 and better beyond.
  - **The defect is in the comparison, not the extraction.**
- **Post-hoc rerun (`algebra2`):** the same nodes and criterion, with both sides averaged over the same 15 shifts.
  Labelled as a post-hoc correction of the comparison.

## G-b3 (round 75 gate; implementation declared 2026-10-23, before running)
- **Cases:** the (3, 3) cross-connected term at ζ PMAX 10³, at the six declared (ℓ, r): (15.75; 100, 173, 300, 500)
  and (21.75; 173, 500).
- **Sides:** brute = the unfiltered construction's ρ₆ − ρ₃ρ₃; extraction = the phase-filtered non-oscillating part
  − ρ₃ρ₃.
- **Treatment:** identical in-window nodes (4 per coordinate), and both sides averaged over the same 15 triangular
  shifts.
- **Tolerance:** 1% of |brute|. The declared tolerance is the larger of the quadrature error and 1%; 1% alone is
  stricter, and the quadrature cancels at identical nodes.
- **Wrong variants:** the sign-reversed extraction, and the (1, 1) piece in place of (3, 3), must fail.
- **Guard:** every ζ configuration goes through `ratios_t6.guard`. The nodes are ≥ 1 apart, so the double path is used
  throughout.

## Results (spot; both finished before the local reboot of 2026-10-23)
**G-b1 (i), algebra check (not G-b1), post-hoc rerun with both sides averaged: PASS** (`cs4/results/n6b/ALGEBRA_CHECK2.json`).
- Every (a, b) piece agrees with the exact determinant to ≤ 2.4·10⁻⁵ at r = 20, ≤ 6.7·10⁻⁶ at 50, ≤ 1.8·10⁻⁶ at 100 and
  ≤ 2·10⁻⁷ at 300, against a criterion of 10⁻⁴.
- **The phase filter is exact for U(N) at 3 + 3.**

**G-b3: FAIL as declared; both wrong variants fail (the gate has power)** (`cs4/results/n6b/GB3.json`; 9,332 s on 28
processes). The (3, 3) piece at ζ PMAX 10³, at identical nodes, with both sides averaged identically:

| ℓ | r | brute | extraction | brute − extraction | relative |
|---|---|---|---|---|---|
| 15.75 | 100 | 1.229 | 1.616 | −0.387 | 0.31 |
| 15.75 | 173 | −1.655 | −1.516 | −0.140 | 0.08 |
| 15.75 | 300 | 10.06 | 9.416 | +0.643 | 0.06 |
| 15.75 | 500 | 19.61 | 19.13 | +0.487 | 0.025 |
| 21.75 | 173 | −8.075 | −8.157 | +0.082 | 0.010 |
| 21.75 | 500 | 14.02 | 13.80 | +0.221 | 0.016 |

**Diagnosis (descriptive; consistent with a known mechanism, not yet proven).**
- The missing part does not decay with r: its absolute size is 0.08–0.64. It is larger at the lower height.
- That is the signature of **beat terms.**
  - A piece in an r-oscillating phase class (e^{2πikr}, k ≠ 0) also carries arithmetic factors p^{±i r_t}, with
    frequencies log p / ℓ per unit spacing.
  - Where the summed prime frequencies come within ~½ of k, which needs products of primes p·q·… ≈ e^{kℓ}, the piece has
    near-DC content in r. That content survives the period average, and the block-variance estimator's Bartlett sum
    sees it as well.
  - This is the mechanism Stage 2 recorded for its dropped "ℓ-oscillating long-range part" (`cs4/GS_ZETA_RESULTS.md`
    §3): up to 0.9% of v at 2 + 2, larger at low heights.
  - At 3 + 3 there are more Euler factors in each term, so more prime products can reach e^ℓ. At ℓ = 15.75,
    e^ℓ = 6.9·10⁶ < 10⁹ (three primes ≤ 10³); at ℓ = 21.75, e^ℓ = 2.8·10⁹.
- **G-b2 passed because it tested agreement with Stage 2's own definition,** which drops the same beat terms. G-b3
  compares against the brute-force value, which keeps them.

**Consequence.** The phase filter ("non-oscillating class") is the wrong object for ζ at 3 + 3. What the estimator sees
is the low-frequency content of C(r), beats included. A correct extraction has to keep the near-DC beat components of
the oscillating classes. In practice that means a per-prime frequency decomposition, as `cs4lr` does with its NUFFT for
prime sums, or the full function evaluated on the estimator's 1/8 grid. Either is a session-2 design question,
alongside the separation. **Decision to Will.**

## Round 77
- **G-b3 FAIL is recorded, attributed to beat terms:** slow components from products of primes near e^ℓ, mixing with
  the carrier. The gap table is above.
- **Beat-term finding, recorded either way:** at ζ PMAX 10³, beat terms carry 1–30% of the 3 + 3 long-range (3, 3)
  piece at r ≤ 500. They are larger at the lower height (ℓ = 15.75: 2.5–31%; ℓ = 21.75: 1.0–1.6%).
- **The fix (Will):** evaluate the full function, all phase classes, on the estimator's 1/8-unit r grid. That is made
  affordable by the session-2 cross-factor expansion.
  - In the expansion, only smooth envelopes are expanded in window/r.
  - The carrier and the prime phases are carried exactly and are never treated as slow.
  - The expansion must pass G-b3 (brute force at cutoff 10³) and G-b1 before any ζ prediction.
- **Time box:** unchanged, 1 of 3 sessions used.
- **For session 2, noted:**
  - Stage 2's prediction is the file-averaged one (G_S_DESIGN amendment 7). Its beat terms moved with ℓ and averaged
    out across a file: from up to 9·10⁻³ of v at one ℓ to (1.3 ± 5.3)·10⁻⁴ file-averaged.
  - G-b3 compares at fixed ℓ. Whether the 3 + 3 beat terms also average out over an F-file's ℓ range is a separate
    question. The full-function evaluation answers it, if run at stratified ℓ across a file, as `diag_osc_lavg.py`
    did.

## Sibling check (round 77)
**Stage 2's dropped ℓ-oscillating part was computed, not assumed, and carried as an accepted precision item:**
- **Computed.**
  - In production it was evaluated for two node pairs per height. That check turned out to be aliased on the
    Δr = 0.5 grid.
  - It was redone on a Δr = 0.1 grid for pair (5, 5).
  - It was then file-averaged at 64 stratified ℓ across the lowest-height F2 file: (0.9 ± 0.6)·10⁻⁴,
    (0.9 ± 2.3)·10⁻⁴ and (1.3 ± 5.3)·10⁻⁴ of v at b = 10³, 3·10³ and 10⁴ (`cs4/GS_ZETA_RESULTS.md` §3,
    `diag_osc_lavg.py`).
  - The lag-1 term was checked the same way (`diag_osc_lag1.py`).
- **Carried.** In `ph2s2/PH2S_SEAL_2.0.md` §2 (precision): "the dropped oscillating lag term is (2.0 ± 8.9)·10⁻⁴ of v;
  it misses the 10⁻³ standard, accepted in the twenty-fifth round as ~6·10⁻⁴ in g against a per-file SE of ~0.04".
  The prediction is defined as file-averaged (G_S_DESIGN amendment 7, approved in round 23).
- **Caveats:**
  - The file-averaged evaluation covered the heaviest pair at the lowest-height file only. Other pairs and heights
    were argued smaller ("smaller weights"; "higher heights are smaller at fixed ℓ"), not computed.
  - The "≤ 0.9%" figure is the single-ℓ, single-pair maximum (9·10⁻³ of v). The file-averaged value is ~100× smaller.

**Every use of the phase filter as exact** (`nonosc_only=True`; repository-wide search):
- `cs4/gs_zeta.py`: the Stage 2 prediction.
- `cs4/gs_zeta_ext.py`: the ρ₁ extension, Stage 2 estimator B.
- `cs4/gs_zeta_cutB.py`: Stage 2's prime-cutoff check.
- `cs4/diag_pmax.py`: Stage 2's cutoff diagnostic.
- `cs4/cs4lr_check.py`: evaluator validation.
- `cs4/n6b_extract.py`: this work.
- `cs4fastc.py` and `cs4lr.py` define it.

**No other banked result uses it.** Route (a), (A), (B), corrected (B), R₂, Stage 1 and Phase 6 do not. The only banked
result resting on the filter is Stage 2's prediction, and there the dropped part was computed (one pair) and carried.

## Session 2 (started 2026-10-23, round 78; session 2 of 3)
Round 78: "Use the full-function expansion with exact phases, evaluate at several heights per file (to answer the
averaging question), and use G-b1 and G-b3 as the gates."

### S2.1: C(r) in joint count cumulants (derivation; checked for U(N), not a gate)
For disjoint windows, with X = n_A − m, Y = n_B − m, ψ(X) = X³ − 3σ²X and E[ψ] = κ₃, expanding E[X³Y³],
E[X³Y] and E[XY³] in joint cumulants (set partitions with no singletons) gives

  **C(r) = κ₃₃ + 9κ₂₁κ₁₂ + 9κ₁₁κ₂₂ + 6κ₁₁³.**

- **The σ² terms cancel exactly.** That is ψ's influence-function property.
- **The joint count cumulants** are κ_{a,b} = Σ_{i ≤ a, j ≤ b} S(a, i)S(b, j)·κ^{[i,j]}, with S the Stirling numbers of
  the second kind.
- **The factorial cumulants are connected:** κ^{[i,j]} = ∫_{A^i×B^j} T_{i+j}, where T is the Ursell function.
- **T₆ enters only through κ^{[3,3]},** with coefficient 1. That is the stage (c) quantity.

**Check against stage (a)'s Fredholm C(r)** (U(N), N = 10⁵; κ^{[i,j]} from the cyclic-trace formula with the product
Gauss–Legendre rule):
- **Exact:** the agreement is 6·10⁻¹¹ (r = 4.125), 3·10⁻⁸ (7.3), 4·10⁻⁸ (20) and 3·10⁻⁶ (100) relative at 16 nodes. At
  r = 1000 the gap is 8·10⁻¹⁴ absolute, inside stage (a)'s 10⁻¹¹ floor.
- **The cancellation is not removed.** It sits inside κ₃₃: at r = 100, κ₃₃ = −4.7·10⁻⁹, while κ^{[3,3]} = −2.75·10⁻⁴
  and κ^{[1,1]} = −8.1·10⁻⁵. That is four to five orders, the determinantal rigidity of U(N).
- **Node counts:** the relative error of C is 0.5% at 10 nodes and ≤ 6·10⁻⁵ at 12 for r ≤ 100. So **G-b1 still needs
  about 12 nodes per coordinate.**
- **For ζ, the quantity to predict is far larger.** The zeros halve W, which implies an arithmetic ΔC of order 10⁻⁴ at
  r ~ 10²–10³. It is not a 10⁻⁹ residue, so the ζ evaluation does not inherit U(N)'s cancellation requirement. That
  will be quantified, not assumed.
- **Quadrature lesson** (from stage (c), round 78): integrals of T's need the product rule with the in-cluster
  diagonal. The distinct-node rule is valid only for integrands that vanish at coincidence.

### S2.2: the averaging question (declared before running; descriptive)
- **Kinematics.** A beat whose product of primes has log n ≈ kℓ carries the phase 2πr(k − log n/ℓ). Across a file it
  moves at 2πrk/ℓ per unit ℓ.
- **The four corrected (B) files** have Δℓ = 0.044, 8.2·10⁻³, 8.9·10⁻⁴ and 2.0·10⁻⁴ (ℓ̄ = 15.84, 17.53, 19.75,
  21.25).
- **Prediction stated now:** the file-average dephasing factor for k = 1 is

  | file | S at r = 100 | 300 | 1000 | 10000 |
  |---|---|---|---|---|
  | zeros_46646000 | 0.878 | 0.190 | 0.073 | 0.007 |
  | zeros_256646000 | 0.996 | 0.968 | 0.680 | 0.061 |
  | zeros_2365046000 | 1.000 | 1.000 | 0.997 | 0.699 |
  | zeros_10630646000 | 1.000 | 1.000 | 1.000 | 0.986 |

  **So file-averaging cannot remove 3 + 3 beats in the two highest files at any r that matters.** Unlike Stage 2's
  F2 15.75 file, those files are too narrow in ℓ. Beats have to be predicted at fixed ℓ there.
- **Numerical test** (`cs4/n6b_lavg.py`):
  - The (3, 3) piece by phase class at ζ PMAX 10³, with G-b3's treatment: 4 nodes (distinct-node rule, valid here) and
    the 15 triangular shifts.
  - It runs at stratified ℓ across the lowest file: 8 heights at r = 100 and 16 at r = 300, with weights ∝ ℓe^ℓ.
  - Reported per class k ≠ 0: |file average| / (weighted rms over ℓ), beside S(r, |k|).
  - 360 tasks, ~145 core-h. It runs on spot at 20 processes, beside the stage (c) pilot.

### S2.3 onwards (to be declared before computing)
- The separated evaluation, with exact phases, of the factorial cumulants on the estimator's 1/8 grid.
- G-b1 against Fredholm at ~12 nodes.
- G-b3 on the separated evaluator.

### S2.3: the cross-factor expansion with exact phases. What separates, what does not (derivation notes)
**U(N) separates.**
- A cross factor depends on the in-window offsets only through r + δ, with δ = v − u ∈ [−4, 4].
- For U(N), z(i2π(r + δ)/N) is smooth on the scale r. Its Taylor series in δ about the window centres converges like
  (4/r)^m.
- δ^m splits into powers of u and v. So each (S, T) term becomes in-cluster integrals (3-dimensional, with the exact
  in-window carriers e^{2πi c·u}) times derivatives of the cross factors at r.
- The order is set by U(N)'s cancellation inside κ₃₃ (S2.1): about 10⁻⁷ relative at r = 100 needs m ≈ 5; about 10⁻⁶ at
  r = 20 needs m ≈ 9.

**ζ does not separate by that expansion.**
- A cross factor such as ζ(1 ± i(2π/ℓ)(r + δ)), or 𝒜's local factors, carries in-window phases n^{∓iδ·2π/ℓ}. Across the
  window δ·(2π/ℓ)·log n reaches ~1.6·log n rad: more than 1 rad from n ≈ 2, and ~25 rad for n ≈ e^ℓ.
- Those are exactly the prime phases round 77 says must be carried exactly, never treated as slow.
- Carried exactly, each cross factor is a Dirichlet or prime sum of separable plane waves. A term holds up to 9 cross
  factors and 𝒜's θ-coupling, so the separated form is a multi-index sum over products of primes. **Those products are
  the beat terms.**
- So the round-77 plan, "expand only the smooth envelopes, carry the phases", does not reduce the in-window work for ζ.
  It moves it into sums over prime products.

**The direct alternative is unaffordable.**
- The direct alternative is the full function on the 1/8 grid, configuration by configuration (cs4lr-style, r on the
  grid).
- **Measured at good batching** (local): U(N) ρ₆ costs ~0.3–0.4 s per (configuration, r); ζ ρ₆ ~6–7 s at PMAX 10² and
  ~60–90 s at 10³.
- A single configuration on the 1/8 grid to r = 10⁴ (8·10⁴ points) is ~7 core-h for U(N) and 10⁵–10⁶ core-h for ζ.
  Times ≥ 3·10³ configurations, that is far beyond reach. cs4lr's NUFFT only helps the prime sums, not the n = 6 jets
  algebra over the grid.

**The candidate that remains (not designed in detail; a theory step):** a spectral formulation.
- **Why it fits:** on the 1/8 grid the Bartlett sum is W(G) = ∫dΩ K(Ω) F_G(Ω), with F_G the Fejér kernel (period
  2π/Δ). Carriers at k ≤ 3 cycles per unit are below the grid's Nyquist frequency of 4. So the estimator sees only
  C's near-DC spectral content, K(Ω) for |Ω| ≲ 2π/G: the non-oscillating part plus exactly the beats.
- **Where it could come from:** for a fixed in-window configuration, the r-dependence is a function on the torus of
  prime angles θ_p = r_t·log p (times the carriers), sampled along a line.
- **Why it could be tractable:** where that function is an Euler product, its Fourier modes factorise over primes.
  The near-DC modes are the prime products with log n ≈ kℓ, which can be enumerated with their amplitudes.
- **What it needs:** handling ζ(1 + it) on Re s = 1, where its Euler product does not converge absolutely; the jets'
  derivatives; and the in-window integral of each kept mode (exact plane waves).
- **It is new analysis,** not bookkeeping. Its cost cannot be estimated until it is designed.

**Consequence for the gates and the time box (session 2 of 3).**
- **G-b1 (U(N)) is reachable.** Either by the U(N) separation above (new code), or by brute force at about 12 nodes
  with the S2.1 cumulant form on a sparse r grid. The brute-force cost: the product-rule multisets at 12 nodes are 364
  per cluster, so ~1.3·10⁵ configurations per r and ~15–20 core-h per r on spot. A 60-point grid is ~10³ core-h, less
  with a GPU port of the jets (CuPy is available on the local 4090).
- **G-b3 needs a ζ extraction to test.** The only candidate is the spectral formulation, which does not exist yet.
  Evaluating the full function directly at G-b3's identical nodes would make G-b3 compare a computation with itself,
  so it could not fail.
- **By the end of session 3,** G-b1 can plausibly pass. G-b3 passing requires the spectral method to be designed,
  implemented and validated within one session. **I do not expect that.** This is flagged now, not at the deadline.
