# Scope (Will, eleventh round (ii)): a ζ-specific next-order spacing law from Conrey–Snaith — before committing

**Goal.** A parameter-free prediction of the ζ nearest-neighbour law p(s; E) at height E with the arithmetic lower-order
terms, from Conrey & Snaith's n-correlation theorem (CS08 Theorem 9, ratios conjecture), to be sealed and tested on fresh
heights. Nobody has done it (CS07 §9 and CS08 §1 name it as anticipated future work; `lit/NEXT_ORDER_LIT.md` §2.5).

## 1. Feasibility: how many n-point functions are needed
E(0; s) = Σ_n ((−1)ⁿ/n!) ∫_{[0,s]ⁿ} R_n, p(s) = E″(s). The series converges fast on the sealed window s ≤ 2 (A2).
Leading order (sine kernel; Gauss–Legendre m = 60, exact Fredholm determinant vs partial sums):

| s | |E − Σ_{n≤2}| | n ≤ 3 | n ≤ 4 | n ≤ 5 |
|---|---|---|---|---|
| 1.0 | 2·10⁻³ | 4·10⁻⁷ | 9·10⁻¹³ | 3·10⁻¹⁷ |
| 1.5 | 4·10⁻² | 1·10⁻⁴ | 1·10⁻⁸ | 1·10⁻¹⁴ |
| 2.0 | 2·10⁻¹ | 5·10⁻³ | **5·10⁻⁶** | 1·10⁻¹⁰ |
| 2.5 | 6·10⁻¹ | 5·10⁻² | 3·10⁻⁴ | 1·10⁻⁷ |

So on s ≤ 2 the spacing law needs the correlations only **through n = 4** (truncation ≤ 5·10⁻⁶ in E, far below the
~10⁻⁴ resolution of a Phase-2-sized bin; the lower-order corrections to R₅ multiply integrals already ≤ 10⁻¹⁰·ρ̄⁻²).
CS08 §5 writes n = 2, 3, 4 out explicitly for ζ — the inputs exist in print. This is the main reason the project is
tractable, and it rests on the window Will adopted in A2.

## 2. Work plan
1. **Transcribe CS08 §5 (n = 2, 3, 4) and the arithmetic factors** (A(η), B(η), Q, B₁, A*, B₂–B₄: Euler products / prime
   sums; ζ, ζ′/ζ near 1) into code; independent re-derivation of n = 2 from CS07 Thm 4.1 as a cross-check.
2. **Built-in known answer (the strongest G0 available):** CS08 also states the same structure for **U(N) eigenvalue
   correlations** (§ "Eigenvalue correlations"). Implemented with the same code, it must reproduce the exact CUE_N
   n-correlations (determinants of sin(πd)/(N sin(πd/N))) and, through §1's series, our exact CUE_N gap probabilities
   (ph2lib Fredholm, G0b-verified) to ≤ 10⁻⁸ — before any ζ number is computed.
3. **Densities and integrals.** The R_n at height E are local densities (the theorems are for sums over 0 < γ ≤ T;
   differentiate in T, or difference over a bin). n-fold integrals over [0, s]ⁿ for n ≤ 4 by tensor Gauss–Legendre
   (m ≈ 20–30 per axis: ≤ 10⁶ points) with the integrands' contour/residue structure handled analytically where CS give
   it in closed form.
4. **Output:** p(s; E) at each fresh bin's heights (full formula at height E — no 1/ρ̄ expansion needed, so no new
   truncation choice); and, descriptively, its 1/ρ̄ expansion to read off the O(ρ̄⁻⁴) coefficient.
5. **Seal and test:** estimand as Phase 2 (κ-type, or the amplitude of the lower-order part as in the R₂ draft), on its
   own fresh Platt heights (not R1–R5, which the R₂ phase will have read: e.g. L = 15, 17, 19, 21, pinned when this model
   is sealed). The seen Phase 2 bins: descriptive only.

## 3. Risks and limits
- **Conjectural input:** the ratios conjecture (CS08 Thm 9 is conditional). The test is of "ratios conjecture +
  CS08 + n ≤ 4 truncation", stated as such.
- **Transcription risk** in CS08 §5's n = 3, 4 formulas (long, many factors): mitigated by step 2 (the U(N) analogue must
  match exact CUE_N) and by CS's own consistency checks (their n = 3 agrees with BK 2013a's triple correlation, per
  BK 2013a §7).
- **Numerical cancellation:** the lower-order parts are 1/ρ̄² ≈ 4–19% corrections built from differences of near-equal
  terms near poles (ζ(1 + a + b) at a + b → 0); evaluate in mpmath where needed, verify by step 2.
- **s > 2:** not covered without n = 5 (CS08 Thm 9 general n, not written out); the sealed window makes it unnecessary.

## 4. Effort (estimate, for planning only)
Transcription + U(N) known answer (steps 1–2): the bulk — roughly 2–3 focused sessions. Integrals and p(s; E) (step 3):
1 session. Seal text, pre-read, fresh-height download (by hand), run: as Phase 2 (≈ 1–2 sessions). CPU: modest (n ≤ 4
integrals on a grid of s and E; spot not essential).

## 5. Recommendation
Commit to it after the R₂ phase is sealed (the R₂ phase exercises CS07/CS08's two-point machinery first — step 1's n = 2
part — so its G0 de-risks this one). Decision points for Will: (i) go/no-go; (ii) whether the estimand is κ-type or the
lower-order amplitude; (iii) fresh heights for this phase distinct from R1–R5.
