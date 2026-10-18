# Diagnostic D — results (round 55; EXPLORATORY, NO VERDICT)

Design `DIAG_D_DESIGN.md` (d2506082), code `diag_d.py` (f562b793), run on spot (ph6c) 2026-10-18 10:18–10:38 PDT;
tables in `results/diag_d/` (`DIAG_D.json`, per-file scale tables, the CUE null). D3 in `DIAG_D_THEORY.md` (616344b3).
Nothing here changes route (a)'s, (A)'s or (B)'s sealed verdict.

## Declared reading (D1, D2)
| F5 file | D1 k₃: zeros | τ (CUE null 1–99%) | stand-in | D2 k₂: zeros | stand-in |
|---|---|---|---|---|---|
| zeros_36146000.dat | none | −0.107 (−0.303, +0.107) | none | none | none |
| zeros_244046000.dat | none | −0.132 (−0.245, +0.091) | none | none | none |
| zeros_2377646000.dat | none | −0.031 (−0.347, +0.070) | none | none | none |
| zeros_10643246000.dat | none | −0.025 (−0.329, +0.078) | none | none | none |

Every F5 file reads **none** for both k₃ and k₂: the between-sub-block variance stays inside each file's CUE null at
every scale from ½ the file down to 100 windows, with no trend. By the declared reading this points away from slow
arithmetic fluctuation and toward the model terms or a pipeline defect. D3's estimate predicted exactly this: the
near-resonant prime terms give per-file offsets of 2–7·10⁻⁵ in k₃, about 100× below what the read needs.

## Pipeline checks
- **Halves** (μ̂ with the sealed b_f and Δκ₃,f): 0.538 ± 0.019 / 0.553 ± 0.018; 0.603 ± 0.023 / 0.589 ± 0.022;
  1.287 ± 0.044 / 1.223 ± 0.047; 0.865 ± 0.040 / 0.917 ± 0.039. Each file's two halves agree; the between-file
  differences are carried by whole files.
- **Zero-count completeness:** all twelve zero files (F5, F4, F3) have |count − θ count| ≤ 1.5 (largest −1.49). The
  four stand-ins differ by about −99, by construction (they hold n_f − 100 spacings).

## Post-hoc finding: the window grid is phase-locked to the zeros (`diag_d_phase.py`, `results/diag_d/PHASE.json`)
Not in the design; found while reading D's tables, and reported as such.
- **Observation.** k₂ at L = 3 differs between files far beyond its SE (≈ 0.001), including between files at the same
  height: at ℓ ≈ 19.75 it is 0.494 (F4), 0.389 (F3) and 0.369 (F5); over all twelve files it ranges from 0.337 to 0.503.
  Every CUE sequence and stand-in gives 0.457–0.458.
- **Mechanism (hypothesis, then checked).** In unfolded coordinates the zeros sit near a lattice:
  x_k = N̄(γ_k) − N̄(t₀) ≈ N(t₀) + k − ½ − N̄(t₀) − S(γ_k), and S(t) has a standard deviation of only about 0.4 at these
  heights. (B)'s windows have integer length 3 and start at x = 0, so in each file they see the lattice at one fixed
  phase φ = frac(N(t₀) − N̄(t₀)). How often a zero jitters across a window edge, and so the count cumulants, depend on φ.
  The CUE calibration rotates every matrix at random and so averages over φ; it cannot see this.
- **Check.** Across the twelve zero files, with φ from each Platt header's N(t₀) and exact θ:
  **corr(k₂, cos 2πφ) = −0.990** and **corr(k₃, cos 2πφ) = −0.882**. Files whose lattice sits mid-cell (φ ≈ 0.54–0.59)
  have k₂ ≈ 0.49–0.50 and k₃ ≈ −0.004; files with φ near 0 have k₂ ≈ 0.34–0.39 and k₃ ≈ −0.009 to −0.018.
- **What follows (reasoning; no verdict changes).**
  - (B)'s sealed estimator is not stationary on the zeros: with a grid anchored at N̄(t₀) it measures the count
    cumulants at one lattice phase per file, whereas the prediction (from translation-invariant correlation functions)
    is the phase average. The CUE calibration, being phase-averaged, could not detect this. The between-file
    heterogeneity (χ² 282.7 on 3) is what this produces: a per-file constant set by φ.
  - Within the sealed attribution ("observable-specific model terms or estimator"), this points to the **estimator**.
    D3's exact-resonance check (Δκ₃ reproduced to 3%) and D1's "none" both point away from the model terms.
  - Route (a) and (A) use spacings, which do not depend on where windows start; they are unaffected.
- **Not done (Will's call).** A phase-averaged k₃ (windows averaged over origins) on the F5 data would be post-hoc on
  seen data and is not computed here. A corrected (B) would need its own pre-registration, a calibration that
  reproduces the lattice locking (or an estimator that averages over the grid phase), and fresh data.
