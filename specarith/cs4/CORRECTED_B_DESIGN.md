# Corrected (B) — the third cumulant of the count with an offset-averaged estimator (round 57; DATA-FREE PREP)

**Status:** committed before any computation for it (round 57). Sealing waits for Will's review; the read waits for the
seal's Bitcoin attestation. Background: (B)'s sealed FAIL is attributed to its phase-locked window grid
(`ROUTE_A_FINDINGS.md` §9, `DIAG_D_RESULTS.md`); engine gate G1b requires a windowed statistic with L ≤ 3 to average
over the grid phase.

## 1. Estimator (offset-averaged k₃)
For a sequence with unfolded positions x (zeros: x = N̄(γ) − N̄(t₀), exact θ, as the sealed read; CUE_1000: x = Nθ/2π
per matrix), window length L and NU = 32 offsets u_k = kL/NU, k = 0…31:
- counts c_j(u_k) in windows [u_k + jL, u_k + (j + 1)L) lying entirely inside the data (zeros: inside [0, x_last];
  CUE: inside each matrix's [0, N), matrices concatenated);
- k₃(u_k) = the k-statistic of those counts; **k̄₃ = mean over k of k₃(u_k)**;
- μ̂_f = (k̄₃ − κ₃^sine(L))/Δκ₃,f(L), with the data-free prediction at file f's zero-weighted mean height.

## 2. Choice of L (data-free power rule; this section is the rule)
- **Grid:** L ∈ {1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0}.
- **Metric:** M(L) = 1/SE_pool(L), SE_pool(L) = (Σ_f w_f² SD_f(L)²)^½, where SD_f(L) is the standard deviation of μ̂_f(L)
  over R = 100 CUE_1000 replicates at file f's pre-data size, and w_f ∝ n_f.
- **Geometry:** F3's five files (heights and n_f), as the round-50 rule used; F6 is not pinned yet (its feasibility is
  in `../ph2r2/FRESH_SET_F6_FEASIBILITY.md`). The metric compares L at fixed geometry.
- **Signal:** Δκ₃,f(L) and κ₃^sine(L) from `followup_k3.py` (FastZeta, primes ≤ 3·10⁵, triangle order 48, order 32 as
  the quadrature check), at the F3 heights; L = 0.5–3 exist in `results/followup_k3.json` (a01bf8d0), and L = 4, 5, 6
  are computed with the same code.
- **∂μ*/∂μ = 1** in the metric (κ₃ is exactly linear in μ, and averaging over offsets does not change the estimator's
  expectation for a stationary sequence). It is measured at the chosen L in the calibration (§4).
- **Eligibility:** an L whose Δκ₃ quadrature error (order 48 vs 32) exceeds 1% of |Δκ₃| at any file is ineligible.
- **L\*** = the eligible grid value with the largest M(L); an exact tie goes to the smaller L.
- **Inputs are CUE replicates and data-free predictions only.** No zero is read. F5's post-hoc phase-averaged result at
  L = 3 (`DIAG_D_RESULTS.md`) is not an input; L = 3 is one grid value like the others.
- Recorded: M(L), SE_pool(L), SD_f(L), Δκ₃,f(L) and the quadrature errors at every L.
- **CUE replicates:** char GPU (cbe.py Killip–Nenciu sampler), seeds [20261018, 57, i, rep] (disjoint from every earlier
  use); per replicate and file, for every L and offset, the window count sums Σd, Σd², Σd³ and the window number (d =
  count − round(L)), so k̄₃ is computed exactly without storing positions.

## 3. Prediction at F6 (after L\* and Will's F6 geometry)
F6 pinned (`FRESH_SET_F6.md`, gap rule) before the prediction. Δκ₃(L\*) at the F6 heights with route (a)'s checks
(prime cutoff 3·10⁵ → 10⁶, quadrature order, file average) and the round-52 gates (TAGGABLE, cutoff convergence,
cross-machine recompute, selftests); tagged and OpenTimestamps-stamped.

## 4. Calibration from scratch (not the phase-locked floor)
- R = 200 CUE_1000 replicates per F6 file at its pre-data size, through the §1 estimator: bias b_f, SD_f (the SE floor),
  the block length for a joint segment bootstrap over all offsets (shortest segment length whose SE_boot/SD geometric
  mean over files is ≥ 0.95), and the false-FAIL rate at μ = 1 and power at μ = 0 under route (a)'s rule (bias
  subtracted, SE_f = max(SD_f, SE_boot) widened by SD_f/√R, all files but one within 3·SE_f, band 2·SE_pool + δμ_sys).
- ∂μ*/∂μ at L\*: the CUE_N known-answer slope through the §1 estimator, under round 53's rule (SE(slope) ≤ 0.005; divide
  out only if |slope − 1| > 2·SE; its SE in δμ_sys either way).
- G1b red path: on a jittered lattice x_k = k + 0.3·N(0, 1), the §1 estimator must stay within SE across grid origins,
  and the single-offset estimator must not (witness).
- Nothing from the sealed (B)'s calibration (`followup_calib_B_declared.json`) is reused.

## 5. Order
§2 rule (this commit) → §2 computation and L\* → Will reviews F6 geometry → F6 pinned → §3 prediction, gates, tag,
stamp → §4 calibration → seal drafts to Will → seal, stamp, attestation → download → two reads, compare.
