# n = 6, stage (c): bounding the arithmetic n = 6 short-range correction (round 74; method committed BEFORE computing)

**Task (round 74 (c)):** before any full computation, bound the arithmetic n = 6 contribution to corrected (B)'s block
variance from short range (r < R₀ = 20, overlapping windows included). The bound is computed at a low prime cutoff.
If it is below the test's resolution, the term is carried as a bounded systematic and not computed in full.

## The quantity
- ΔC₆(r) is the part of C_ζ(r) − C_sine(r) that comes only from the arithmetic part of ρ₆: the 3 + 3 cross-connected
  term for r ≥ 4, and the 6-point terms with overlapping windows for r < 4. Everything through ρ₅ is computable with
  existing code and is not part of this bound.
- Its effect on the block variance: ΔW₆ = Δ·[ΔC₆(0) + 2·Σ_{0 < kΔ < R₀} ΔC₆(kΔ)]. For G ≥ 300 the Bartlett weights are
  ≥ 0.93 below R₀, so ΔW₆ hardly depends on G, and the sum is bounded by the sum of |ΔC₆|.

## Method
1. **The n = 6 ratios construction:** `cs4/ratios_t5.py`'s jet construction, with 6 variables.
2. **Its U(N) pointwise gate** (the `ratios_t5 ugate` check at n = 6): R₆ for U(N) by this construction against
   det[S(x_i − x_j)] at N = 10 and 50, at random and near-coincident configurations. It must agree to the ugate's
   tolerance before any ζ value is read.
3. **ζ at a low prime cutoff:** ρ₆^ζ − ρ₆^sine at the heights of the eventual test (ℓ ≈ 15.75 and 21.75, the extremes),
   at PMAX = 10², 3·10² and 10³.
   - It is evaluated on a coarse in-window grid: Gauss–Legendre with 4 nodes per coordinate, 3 + 3 coordinates.
   - At r ∈ {0, 1, 2, 3, 4, 6, 10, 20}.
4. **The bound:** B₆ = Δ·Σ |ψ-weighted in-window integral of the arithmetic ρ₆ part| over the r grid, interpolated
   piecewise-linearly in r. It carries a safety factor of 2 for the coarse quadrature, justified only if B₆ changes by
   less than 2× from 3 to 4 nodes per coordinate, which is checked. It also takes the largest |B₆| over the three
   cutoffs, as a stand-in for the cutoff tail.
   - Prime sums converge slowly. So the bound is stated as conditional on the cutoff trend: its change from PMAX 3·10²
     to 10³ is reported. If that change exceeds 30% of B₆, the bound is reported as not yet established.

## Resolution it is compared with (from the scoping clarification)
- The test reads R(G) = W_ζ(G)/W_CUE(G), about 0.16–0.31. Its pooled precision is about 3% of R at G = 10⁴ over five
  files (CUE floor).
- **The term is negligible if B₆ ≤ ⅓ of that,** i.e. B₆/W_CUE(G) ≤ 0.01·R(G) at every G. Then it is carried as a
  bounded systematic, ±B₆.
- Otherwise it must be computed in full, which is about 10³–5·10³ core-h (scoping §3), and that is Will's call.

## Cost
- Each ρ₆ evaluation costs about 50–150 core-s at PMAX 10³ (scoping §3). Far less at 10².
- 4⁶/72 ≈ 60 distinct configurations × 8 r × 2 heights × 3 cutoffs ≈ 3·10³ evaluations, about 10–100 core-h. That
  needs spot.
- **Under round 74 this runs only as the bound,** after the n = 6 U(N) pointwise gate (step 2) passes.

Outputs: `N6_STAGE_C.md` (result), `results/n6c/`. Code: `cs4/ratios_t6.py` (the n = 6 construction and its U(N)
gate) and `n6c_bound.py`.
