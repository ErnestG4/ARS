# Conrey–Snaith (2008): two errata in the 4-point correlation (A*'s local factor; the sign of J₁₃'s prime sum), and one parenthesis

J. B. Conrey and N. C. Snaith, "Correlations of eigenvalues and Riemann zeros", Commun. Number Theory Phys. 2(3),
477–536 (2008), doi:10.4310/CNTP.2008.v2.n3.a1; arXiv:0803.2795 (v1 only).

§1–§3 collect two existing records: the transcription note in `cs4lib.py` (header of the ζ section) and the
journal check (`../MORNING_2026-10-10.md`, 14:30). §4 is new (2026-10-11). The published PDF is not committed; its
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

## 3. Effect on results (§1–§2)
None. `cs4lib.py` used the derived forms from the start. The U(N) gates (`GS_UNITARY_RESULTS.md`) and the ζ checks
Z1–Z4 pass with them. The Stage 2 prediction (`GS_ZETA_RESULTS.md`, tag `ph2s-stage2-prediction`) is computed with
them.

*(Release v2026.10.11 carried §1–§3 above. §4 was added on 2026-10-11, after the release.)*

## 4. The sign of J*({a},{b₁,b₂,b₃})'s prime-sum term (erratum; found 2026-10-11, after the release)
- **Printed:** CS08 writes the quadruple-correlation piece as
  J*_{ζ,t}({a},{b₁,b₂,b₃}) = **−**Σ_p z_p(1+a+b₁)z_p(1+a+b₂)z_p(1+a+b₃) log⁴p / p^{3+3a+b₁+b₂+b₃} + W₁(…) + W₁(…) + W₁(…).
  This is arXiv v1 (source line 2701) and the journal's eq. (5.36), checked in the published PDF (sha256 decd4a26…).
  `cs4lib.py`, `cs4fast.py` and `cs4ref.py` transcribed it as printed.
- **Derived:** the term is **+**Σ_p. The check is `check_ratios_j.py` (results in `results/check_ratios_j.json`).
  - It builds J*(A;B) from CS08's own definition: the mixed first derivatives of the ratios-conjecture expression
    ℛ_{ζ,t}(A,B;C,D) at C = A, D = B. The identity holds prime by prime, so p ≤ 7 tests every arithmetic factor; ζ is
    exact on both sides.
  - **J₁₁, J₁₂, J₂₂** match the transcription to ≤ 3.5e-16 relative. This also confirms §1's derived A* and §2's
    reading of B₄ independently.
  - **J₁₃** misses by exactly −2 × (the prime-sum term). The miss is the same at ℓ = 14.76 and 21.19, so it does not
    depend on ℓ, and it vanishes when no primes are included. With the sign flipped, J₁₃ matches to ≤ 3.5e-15.
    The printed sign misses by 0.4–10%: this is the red path.
- **Why the printed sign cannot be right:** CS08's n-correlation counts distinct zeros (its Theorem "mainzeta":
  γ₁ ≠ … ≠ γ_n). R₄ is therefore a density and must vanish at coincidence, as R₂ and R₃ do.
  - With the printed sign, ρ₄^ζ(0, y, a, b) → a non-zero constant as y → 0, and the constant is negative
    (−9.2e-5 at ℓ = 14.76, (a, b) = (0.45, 0.9)). Its ratio to the sine kernel diverges like y⁻².
  - With the corrected sign the ratio settles: 0.05–0.59 over three configurations and two heights.
- **How it was found:** route (a)'s spacing-law integrator (`route_a_zeta.py`) evaluates ρ₄ with all four points inside
  a gap s ≤ 1.8. A fast-vs-30-digit point check showed negative ρ₄ at the nodes nearest coincidence, and the
  coincidence probe followed from that.
  - The earlier checks Z1–Z4 could not see it. A sign error in a real, permutation-symmetric, decaying term passes the
    realness and symmetry test, and the summand-decay test checks magnitudes only.
  - The U(N) gates do not involve the arithmetic factors.
- **Status:** the journal prints the same sign, so under the twentieth-round rule this is recorded as an erratum.
- **Fixed:** in `cs4lib.Zeta.S13`, `cs4fast.FastZeta.S13` (inherited by `cs4fastc` and `cs4lr`) and
  `cs4ref.ZetaRef.S13`. `cs4split.Zetap` inherits `cs4lib`'s.

### 4.1 Effect on Stage 2: none on any windowed quantity, by construction and checked
- **Why there can be none:** in Stage 2's two-pair geometry (x₁,₂ = ∓d₁/2, x₃,₄ = r ∓ d₂/2), every term of the
  correction Δρ₄ = (2/ℓ⁴)·Σ_{8 J₁₃ terms} S₁₃ carries an r-phase p^{±i(2 + k₁ + k₂)r_t}, with k ≥ 0. This follows from
  expanding z_p(1 + x) = Σ_k p^{−k(1+x)}.
  - So Δρ₄ has no constant part: its Bohr mean is 0, and c∞ is unchanged.
  - Its lowest frequency is 2·log 2·2π/ℓ ≥ 0.39 per spacing for ℓ ≤ 22.1.
  - Against Stage 2's windows exp(−πr²/2b²), b ≥ 100, and their 3b-shifted copies, it integrates to
    ≲ √2·b·sup|Δρ₄|·e^{−ω²b²/2π} ≈ e^{−240}.
  - The production grids alias nothing back to low frequency at any size that matters: an alias needs m·log p ≈ 2ℓk
    with a coefficient ~p^{−m−1}.
- **Checked numerically:** `check_s13_stage2.py`, results in `results/check_s13_stage2.json`. Settings: the F2 heights
  ℓ = 15.75, 17.25 and 21.75; in-pair offsets (d₁, d₂) = (0.5, 0.5), (0.2, 0.9) and (1.2, 0.4); r ≤ 2000 on Δr = 0.05;
  p ≤ 10⁴.
  - sup|Δρ₄| ≤ 1.24e-4, with RMS 0.6–2.5e-5.
  - The mean over r ∈ [100, 2000] is ≤ 2.4e-8, at most 1e-3 of the RMS. This is consistent with 0 for a finite average
    of an almost-periodic sum.
  - The b = 100 window integral is ≤ 2.7e-19, i.e. rounding, against v_B(100) ≈ 0.075.
  - PASS.
- **Therefore unchanged:** Stage 2's v(b), v_B(b), g, ĝ_B prediction (0.6830 pooled), ρ₁(b), the PASS read, and the
  L4 comparison (CS08's −0.031 to −0.034 at b = 100). The pointwise C(r) of L3 changes by at most
  sup|Δρ₄|·(∫|F|)² ≈ 1.24e-4 × 1.50² = 2.8e-4, about 0.5% of its RMS of 0.053, and by about 0.1% at the RMS of Δρ₄.
  L3's statement (C(r) almost periodic, RMS constant out to 4.8·10⁴) is unchanged.
- **Not unchanged:** anything that evaluates ρ₄ unwindowed at short range. This affects route (a)'s spacing law,
  which had not been tagged when the error was found. No released number does this.
