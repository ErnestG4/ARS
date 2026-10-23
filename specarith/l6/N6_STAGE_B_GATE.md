# n = 6, stage (b): the long-range extraction and its gate (round 74; gate committed BEFORE any derivation)

**Task (round 74 (b)):** derive the long-range non-oscillating part of the connected correlation for 3 + 3 clusters,
the n = 6 counterpart of `cs4/cs4lr.py`'s 2 + 2 extraction, in the form the ratios construction gives it.
- **Time box:** 3 sessions. Session 1 is 2026-10-22, the one that commits this gate.
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
