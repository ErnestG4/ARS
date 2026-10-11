# Conrey–Snaith (2008): erratum in the 4-point local factor A*, and one parenthesis

J. B. Conrey and N. C. Snaith, "Correlations of eigenvalues and Riemann zeros", Commun. Number Theory Phys. 2(3),
477–536 (2008), doi:10.4310/CNTP.2008.v2.n3.a1; arXiv:0803.2795 (v1 only).

This note collects two existing records: the transcription note in `cs4lib.py` (header of the ζ section) and the
journal check (`../MORNING_2026-10-10.md`, 14:30). It adds nothing new. The published PDF is not committed; its
sha256 (decd4a26…) is recorded in `../ph2/lit/NEXT_ORDER_LIT.md`.

## 1. A*'s local factor (erratum)
- **Printed:** both arXiv v1 and the journal print the local factor of A*, in the zeta 4-point correlation, as
  p^{−Σ}(1 + T₁ + T₂). It appears in eq. (5.40) in §5.6 and again in eq. (5.45) in §5.7.
- **Derived:** evaluating A*'s definition from the ratios conjecture,
  Π_p Z_p(B⁻, A⁻; A, B) ∫₀¹ 𝒜_{p,θ}(B⁻, A⁻; A, B) dθ, by residues at w = 0, u₁, u₂ gives **p^{−Σ}(1 − T₁ − T₂)**.
  - Res₀ = p^{−Σ}.
  - p^{Σ}·Res_{u_k} = −T_k exactly.
  - T₁ and T₂ are the same fractions as printed.
- **Why the printed form cannot be right:** it does not tend to 1 as p → ∞, so it is not an Euler factor. The
  derived form does tend to 1.
- **Numerical check:** `check_zeta.py` Z3, results in `results/check_zeta.json`.
  - The corrected factor equals its defining θ-integral to 1.2e-14 (worst case).
  - The printed form misses it by at least 1.57. This is the red path.
- **Status:** the journal version prints the same form. Under the twentieth-round rule
  (`../ph2/PH2_DECISIONS_2026-10-07.md`), it is therefore recorded as an erratum, not as an arXiv typo corrected in the
  journal.

## 2. B₄'s parenthesis (typo, partly corrected in the journal)
- **The error:** B₄'s parenthesis is misplaced in the §5.6 copy, in both arXiv v1 and the journal.
- **The fix:** the journal's §5.7 copy, eq. (5.49), has it right. arXiv v1 has the error in both copies.
- **Our reading:** the one in the journal's §5.7 (`cs4lib.py`, `B4`).

## 3. Effect on results
None. `cs4lib.py` used the derived forms from the start. The U(N) gates (`GS_UNITARY_RESULTS.md`) and the ζ checks
Z1–Z4 pass with them. The Stage 2 prediction (`GS_ZETA_RESULTS.md`, tag `ph2s-stage2-prediction`) is computed with
them.
