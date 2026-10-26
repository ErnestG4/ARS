# Post-hoc cross-check against Chen et al. (round 86; tolerances committed before any comparison is computed)

**Target.** Chen, Kim, Lichtman, Miller, Shubina, Sweitzer, Waxman, Winsor, Yang, arXiv:1901.07386 (Experimental
Math. 2020), Appendix A. It is a Mathematica program that, at X = 10⁹, outputs Var(ψ_{K,X})/(⟨ψ_{K,X}⟩ log X) for
λ = 0.100, 0.125, …, 0.700. What it computes:
- **Angles:** of ℤ[i] primes of norm ≤ X, in [0, π/2). Both ideals above each p ≡ 1 mod 4, at arctan(a/b) and
  arctan(b/a). Inert p ≡ 3 mod 4 with p ≤ √X sit at 0. (1 + i) and prime powers are omitted.
- **Weights:** log N𝔭 (2 log p for the inert primes).
- **Binning:** K = Round[X^λ] equal bins on [0, π/2), by `HistogramList`.
- **Statistic:** Mathematica's `Variance` of the K bin weights (denominator K − 1), divided by X^{1−λ}·log X.
- **Source PDF:** `phase34d/lit/chen_refined_2019.pdf`, sha256 920b212b…9162.

**Primary check (as ordered: their code, version-pinned, on our ℤ[i] angle set at X = 10⁹).**
- **Tolerance:** |theirs − ours| ≤ 10⁻⁶ relative at every λ, where "ours" is our Python transcription
  (`chen_appendixA.py`) on the same angle set. Both are double precision on identical inputs.
- **STATUS: BLOCKED.** No Mathematica or Wolfram Engine is installed locally or on spot. The free Wolfram Engine needs
  a Wolfram ID to activate a licence, and that is Will's account action. Nothing is run as "their code" until then.

**Secondary check: their Figure 1.**
- **The figure:** a raster image (799 × 865 px JPEG), not vector paths. Its 25 points are located from the dark-pixel
  clusters, calibrated on the gridlines.
- **Precision:** about ±0.002 in both coordinates (≈ ±0.3 px; dot diameter ≈ 14 px).
- **Tolerance:** |transcription − figure| ≤ 0.01 at every one of the 25 λ, at X = 10⁹.
- **What it tests:** our transcription of their code against their published output. The primary check would test
  the transcription against the code itself.
