# n = 6, stage (a): the exact U(N) block variance of corrected (B) (round 74; DATA-FREE; committed before running)

**What.** The exact CUE_N (N = 10⁵) prediction of the block variance W_B(G) of corrected (B)'s estimator, with no
ratios machinery and no Monte Carlo. It is compared with the L6 long CUE baseline at G = 300, 1,000, 3,000 and 10,000.
This is the §4.3 check of the scoping draft, run first and on its own (round 74 (a)).

## Method (`n6a_trace.py`)
- **The process.** CUE_N in unfolded units is determinantal, with K(x, y) = sin π(x − y) / (N sin(π(x − y)/N)).
- **The generating function.** For windows A = [0, 4) and B = [r, r + 4), the joint generating function of the counts
  is the Fredholm determinant F(z, w) = det(I − K g):
  - g = 1 − z on A∖B, 1 − w on B∖A, and 1 − zw on A∩B;
  - discretised with Gauss–Legendre, 24 nodes per window (Bornemann).
- **The factorial moments.** f_ab = ∂_z^a ∂_w^b F at (1, 1), from the Taylor coefficients of F(1 + s, 1 + t) on
  |s| = |t| = 0.75 (a 16 × 16 DFT).
  - For disjoint windows (r ≥ 4), the connected part F − F_A F_B = F_A F_B·expm1(X) is computed directly. Here X is the
    Schur-complement log-determinant, summed as Σ log1p(−λ), so nothing cancels at long range.
- **The covariance.** C(r) = Cov(ψ(n_A), ψ(n_B)), where ψ(n) = (n − m)³ − 3σ²(n − m) is the influence function of the
  k₃ estimator, written in the falling-factorial basis.
- **The estimator's target.** b2_est places window starts on a grid of step Δ = L/NU = 1/8. Its segment bootstrap and
  the round-73 global-mean estimator both target, in κ₃ units,

  **W_B(G) = Δ·[C(0) + 2·Σ_{k ≥ 1} (1 − kΔ/G)·C(kΔ)].**

  C is computed at every kΔ up to 10⁴ (80,001 points). In μ units W is divided by each file's Δκ₃².

## Checks (`n6a_trace.py check`; must pass before the run is read)
- The single-window moments must give mean 4 to 10⁻¹⁰, and κ₃ equal to the sine-kernel value in the tagged corrected
  (B) prediction (0.0037028835622) to 10⁻⁸.
- **Convergence:** at r ∈ {0, 0.5, 2, 3.875, 4, 4.125, 7.3, 100, 5000}, C changes by ≤ 10⁻¹¹ when going from 24 to 36
  nodes per window, and from ρ = 0.75 to ρ = 0.5.
  - Because the long-range C is tiny, that tolerance bounds W's numerical error at about 3·10⁻⁶ relative.
  - A local run passes. Disjoint windows converge to 10⁻¹⁴–10⁻¹⁸. At r ≥ 5000 the remaining ~10⁻¹³ is noise on a C of
    the same size, and contributes < 10⁻⁷ of W.

## Comparison with the L6 long baseline (declared)
- **Measured, in κ₃ units (W × Δκ₃²):**
  - **G = 300 and 1,000:** the per-sequence segment bootstrap (`results/base/stats`), multiplied by n_s/(n_s − 1),
    with n_s = 10⁵/G segments. That is the explicit correction for the bootstrap's centring.
  - **G = 3,000 and 10,000:** the round-73 global-mean estimator (`results/r73`).
  - Both are reported at every G.
- **z = (measured − predicted)/SE_measured,** per file. The files are the same CUE sequences with different Δκ₃ and
  bootstrap draws, so they are not independent.
- **Agrees:** |z| ≤ 3 at every G and file, on the primary estimator for that G.
- **Known small-G caveat:** at G = 300 the round-73 block estimator runs 8–11% high (§ round 73), so it is not the
  primary there.

Outputs: `results/n6a/N6A_CHECK.json`, `results/n6a/C_*.npz` (kept on spot), `results/n6a/N6A_SUMMARY.json`.
