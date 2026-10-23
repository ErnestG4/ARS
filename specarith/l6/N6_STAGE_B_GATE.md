# n = 6, stage (b): the long-range extraction and its gate (round 74; gate committed BEFORE any derivation)

**Task (round 74 (b)):** derive the long-range non-oscillating part of the connected correlation for 3 + 3 clusters,
the n = 6 counterpart of `cs4/cs4lr.py`'s 2 + 2 extraction, in the form the ratios construction gives it.
- **Time box:** 3 sessions, counted from the start of the derivation, not from the gate commit (round 75).
- If the gate below has not passed by the end of session 3, the work stops and is reported to Will.

## What is extracted
For corrected (B), C(r) = Cov(ψ(n_A), ψ(n_B)), with A = [0, 4), B = [r, r + 4) and ψ the k₃ influence function
(stage (a), `N6_STAGE_A.md`). For r ≥ 4 it expands in the cross-connected parts of ρ₂ … ρ₆ with points in both windows.
The extraction is a formula C_long^ext(r) for r ≥ R₀ = 20. It keeps:
- every cross-connected term through n = 6 (one-, two- and three-bond);
- for each term, only the pieces whose e^{iL(·)} phases cancel between the clusters, so that r enters only through
  smooth factors.

That formula is then evaluated for U(N), with CS08's U(N) building blocks (L = N), to be gated, and later for ζ (L = ℓ).

## The gate (U(N); declared now)
**Known answer.** Stage (a)'s exact CUE_N C(kΔ), Δ = 1/8, reduced to its non-oscillating part by the one-period average
C̄(r) = mean of C over the 8 grid points in [r − ½, r + ½). The average removes e^{±2πir} carriers, up to O(r⁻³).

**The gate passes iff all three hold:**
1. **Pointwise:** |C_long^ext(r) − C̄(r)| ≤ max(0.01·|C̄(r)|, 10⁻¹¹) at every r on a log grid of 60 points in
   [20, 1000]. The 10⁻¹¹ floor is stage (a)'s verified per-point numerical tolerance; above it, stage (a)'s C is exact.
2. **Integrated:** the long-range contribution to the block variance,
   W_long(G) = 2Δ·Σ_{kΔ ≥ R₀} (1 − kΔ/G)·C(kΔ), from the extraction agrees with the exact one within the L6 long
   baseline's SE of W(G), at G = 300, 1,000, 3,000 and 10,000.
3. **Power (red path, TOOLKIT §9.D):** the same comparison must FAIL criterion 1 for two deliberately wrong variants,
   declared now:
   - (i) the one-bond term alone;
   - (ii) the two-bond term with its sign reversed.

   If either wrong variant passes, the gate is uninformative at that r range, and that is reported instead of a
   pass.

**If stage (a)'s exact long-range C̄ is below the 10⁻¹¹ floor over most of [20, 1000],** criterion 1 is reported as
"unresolvable at that r". The gate then rests on the r range where C̄ is resolvable, which must include at least
[20, 100], and on criterion 3. A gate that cannot fail is not a pass.

## Outputs
`N6_STAGE_B.md` (the derivation, as it goes), `n6b_extract.py`, `results/n6b/GATE.json`. Nothing for ζ is evaluated
before the gate passes and Will has seen it (round 74).

## Amendment (round 75; before any derivation): two gates with ζ-regime resolution
The U(N) gate above stays, as **G-b1**. Two more are added. **All three must pass.**
- **G-b2, reduction.** The extraction is written for general cluster sizes (a, b). The cumulant relations take it from
  3 + 3 down to a = b = 2, which removes the extra point in each cluster: the same construction, evaluated with
  clusters of two. That reduced 2 + 2 term is the gated object.
  - **Wording clarified before any derivation** (2026-10-22): the earlier phrase "one point integrated out of each
    cluster against the window" was not well defined. The gated object is the extraction's own 2 + 2 instance.
  - It must reproduce the validated `cs4/cs4lr.py` 2 + 2 long-range term (`LongRangeZeta`, the non-oscillating part
    used in Stage 2) at the same heights and r, within that term's precision.
  - "Its precision": the larger of the evaluator's validated agreement with `cs4fastc` (worst 1.1·10⁻⁹,
    `GS_ZETA_RESULTS.md` §2) and the prime-cutoff change from 3·10⁵ to 10⁶ in `results/gs_zeta_cutB`, at each r.
  - Heights ℓ = 15.75 and 21.75 (F2's extremes), at r ∈ {20, 50, 100, 300, 1000}.
- **G-b3, brute-force spot check.** At a prime cutoff of 10³, the full n = 6 quadrature of the 3 + 3 cross-connected
  term is computed, using the n = 6 ratios construction of stage (c) after its U(N) pointwise gate passes.
  - It covers 4–6 configurations with r ∈ [100, 500], declared now: r = 100, 173, 300 and 500 at ℓ = 15.75, plus r = 173
    and 500 at ℓ = 21.75.
  - It is compared with the extraction evaluated at the same cutoff.
  - Agreement: within the brute-force quadrature's own error, estimated by 4 against 6 Gauss–Legendre nodes per
    coordinate, or 1% of the brute-force value if that is larger.
- **Power:** the two deliberately wrong variants (one-bond only; two-bond with reversed sign) must fail all three
  gates, G-b1, G-b2 and G-b3. A variant that passes any gate makes that gate uninformative, and that is reported as
  such.
