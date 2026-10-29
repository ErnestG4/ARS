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

### 1.1 Printed lines, by version (added 2026-10-14; review response item 3, before any outreach)
**Versions.** arXiv 0803.2795 has **one** version: v1, 19 Mar 2008 (no comment, no journal-ref; /abs/0803.2795v2 and
v3 return 404, and the arXiv API lists v1 only). The journal version is CNTP 2(3) 477–536 (2008). No later version
exists to fix either erratum, and no corrigendum was found (CNTP issue page not reachable; Snaith's publication list,
the Bristol research portal and the authors' later "In support of n-correlation" (arXiv:1212.5537, CMP 2014) show
none; MathSciNet not checked — a negative search, not proof). The v1 source fetched on 2026-10-14 is byte-identical
to the copy the transcription used (`~/specarith_lit_cache/ph2_next_order/src_0803.2795`, gzip sha256 4f627757…cb3;
`n_correlation_10.tex` sha256 2a883ed0…009).

**A* (this section), arXiv v1, §5.6, source lines 2729–2734** (the §5.7 copy, lines 2781–2786, is identical):
```
A^*(a_1,a_2,b_1,b_2)=\prod_p\frac{Z_p(\{a_1,a_2\},\{b_1,b_2\})Z_p(\{-a_1,-a_2\},\{-b_1,-b_2\})}
{Z_p(\{a_1,a_2\},\{-a_1,-a_2\})Z_p(\{b_1,b_2\},\{-b_1,-b_2\})}\\
&&  \nonumber \qquad \times p^{-a_1-a_2-b_1-b_2} \bigg( 1+\frac
{z_p(1-a_1-b_1)z_p(1-a_2-b_1)z_p(b_2-b_1)}{z_p(1)z_p(-a_1-b_1)z_p(-a_2-b_1)z_p(1+b_2-b_1)}   \\
&& \qquad \qquad  \nonumber +\frac {z_p(1-a_1-b_2)z_p(1-a_2-b_2)z_p(b_1-b_2)}
{ z_p(1)z_p(-a_1-b_2)z_p(-a_2-b_2)z_p(1+b_1-b_2)} \bigg).
```
**A*, journal** (PDF sha256 decd4a26…; text extracted with pypdf, superscripts flattened inline):
- eq. (5.40), §5.6, printed p. 532: "× p−a1−a2−b1−b2 ( 1+ zp(1 − a1 − b1)zp(1 − a2 − b1)zp(b2 − b1) / zp(1)zp(−a1 − b1)
  zp(−a2 − b1)zp(1 +b2 − b1) + zp(1 − a1 − b2)zp(1 − a2 − b2)zp(b1 − b2) / zp(1)zp(−a1 − b2)zp(−a2 − b2)zp(1 +b1 − b2) )";
- eq. (5.45), §5.7, printed p. 533: the same "( 1+ … + … )".
Both versions print 1 + T₁ + T₂ in both copies.

**J₁₃'s prime-sum sign (§4)**, arXiv v1 source line 2701:
```
J^*_{\zeta,t}(\{a\},\{b_1,b_2,b_3\})=-\sum_p\frac{z_p(1+a+b_1)z_p(1+a+b_2)z_p(1+a+b_3)\log^4p }{p^{3+3a+b_1+b_2+b_3}}\\
```
journal eq. (5.36), printed p. 531: "J∗ ζ,t({a},{b1,b2,b3}) = − ∑ p zp(1 +a + b1)zp(1 +a + b2)zp(1 +a + b3) log4 p /
p3+3a+b1+b2+b3 + W1(a, b1;b2,b3)+ W1(a, b2;b1,b3)+ W1(a, b3;b1,b2)" (the minus is U+2212). Both versions print −Σ_p.

**B₄ (§2)**: v1 source lines 2767 (§5.6) and 2818 (§5.7) both have `p^{1 + a_2 + b_1})-1)(`; the journal's §5.6
copy (p. 533) has "(p1+a2+b1 ) − 1)", its §5.7 copy (p. 534) "(p1+a2+b1 − 1)".

## 2. B₄'s parenthesis (typo, partly corrected in the journal)
> **Correction (2026-10-14):** "eq. (5.49)" below is probably B₃'s number, not B₄'s. In the extracted journal text the
> tag (5.49) closes B₃ and B₄ follows untagged before C's (5.50), on printed p. 534. To be confirmed on the printed
> page before this file is quoted to the authors; the substance (journal §5.7 copy correct) is unaffected.

- **The error:** B₄'s parenthesis is misplaced in the §5.6 copy, in both arXiv v1 and the journal.
- **The fix:** the journal's §5.7 copy, eq. (5.49), has it right. arXiv v1 has the error in both copies.
- **Our reading:** the one in the journal's §5.7 (`cs4lib.py`, `B4`).

## 3. Effect on results (§1–§2)
None. `cs4lib.py` used the derived forms from the start. The U(N) gates (`GS_UNITARY_RESULTS.md`) and the ζ checks
Z1–Z4 pass with them. The Stage 2 prediction (`GS_ZETA_RESULTS.md`, tag `ph2s-stage2-prediction`) is computed with
them.

*(Release v2026.10.11 carried §1–§3 above. §4 was added on 2026-10-11, after the release; release v2026.10.12 carries it, with §4.1 based on the full recompute.)*

## 4. The sign of J*({a},{b₁,b₂,b₃})'s prime-sum term (erratum; found 2026-10-11, after the release)

### 4.0 The printed text, by version (checked 2026-10-29)
- **Versions.** arXiv:0803.2795 has a single version, **v1** (19 Mar 2008, 31 KB; arXiv abstract page, checked
  2026-10-29). The only other version is the journal: Commun. Number Theory Phys. 2(3) (2008) 477–536.
- **arXiv v1**, e-print `n_correlation_10.tex` (sha256 of the e-print 4f627757…dacb3, cached in
  `~/specarith_lit_cache/ph2_next_order/src_0803.2795`), **line 2701**, verbatim:
  `J^*_{\zeta,t}(\{a\},\{b_1,b_2,b_3\})=-\sum_p\frac{z_p(1+a+b_1)z_p(1+a+b_2)z_p(1+a+b_3)\log^4p }{p^{3+3a+b_1+b_2+b_3}}\\`
  followed by `+ W_1(a,b_1;b_2,b_3)+W_1(a,b_2;b_1,b_3)+W_1(a,b_3;b_1,b_2)`.
- **Journal**, eq. **(5.36)**, printed **p. 531** (PDF sha256 decd4a26…7745, page 55 of 60). The text layer extracts as:
  `J∗ζ,t({a},{b1,b2,b3}) = − ∑p zp(1 +a + b1)zp(1 +a + b2)zp(1 +a + b3) log4 p / p3+3a+b1+b2+b3
  + W1(a, b1;b2,b3)+ W1(a, b2;b1,b3)+ W1(a, b3;b1,b2),(5.36)`.
- **Does any version fix it? No.** Both versions print the minus sign, and no later arXiv version exists. Not checked:
  whether the journal issued a separate correction notice.
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

### 4.1 Effect on Stage 2: recomputed; no sealed value moves by more than 1.2e-9
- **The error was in the prediction code.** Unlike §1, where `cs4lib` used the derived form from the start, `cs4lib` and
  `cs4fast` transcribed J₁₃ as printed. That code computed the sealed Stage 2 prediction (tag `ph2s-stage2-prediction`).
- **Recomputed (Will, 2026-10-12).** The full sealed pipeline was rerun with the corrected sign
  (`run_gs_zeta_fix4_spot.sh`, `results/gs_zeta_fix4/`).
  - Heights, grids, prime cutoff and code are the same as sealed apart from the fix.
  - ρ₃ was reused, because the n = 3 terms contain no J₁₃.
  - All 256 tasks exited 0, and positivity holds at every rung and height.
  - The comparison with the sealed values is `compare_fix4.py` (`results/compare_fix4.json`). Will set a budget of
    10⁻³ before the run: within it, the PASS stands; beyond it, the sealed prediction was wrong and the findings
    would say so.

  | quantity | sealed | recomputed | largest change |
  |---|---|---|---|
  | ĝ_B, five F2 files | 0.6703, 0.6656, 0.6646, 0.6829, 0.7201 | same | ≤ 3.4e-10 |
  | pooled prediction (weights C) | 0.6830255987 | 0.6830255986 | 1.4e-10 |
  | v_B at every rung (relative) | — | — | ≤ 1.2e-9 |
  | v at every rung (relative) | — | — | ≤ 4.4e-10 |
  | ρ₁ at every rung | — | — | ≤ 7.6e-10 |
  | z_pool of the read | −0.2156 | −0.2156 | — |

  **Within budget by six orders. The Stage 2 PASS stands.**
- **Why the change is so small: exact integrals vs the pipeline.**
  - In Stage 2's two-pair geometry (x₁,₂ = ∓d₁/2, x₃,₄ = r ∓ d₂/2), every term of the correction
    Δρ₄ = (2/ℓ⁴)·Σ_{8 J₁₃ terms} S₁₃ carries an r-phase p^{±i(2 + k₁ + k₂)r_t}, with k ≥ 0. This follows from
    expanding z_p(1 + x) = Σ_k p^{−k(1+x)}.
  - So Δρ₄ has no constant part (Bohr mean 0, so c∞ is unchanged), and its lowest frequency is 2·log 2·2π/ℓ ≥ 0.39 per
    spacing for ℓ ≤ 22.1.
  - Against Stage 2's windows exp(−πr²/2b²), b ≥ 100, and their 3b-shifted copies, the exact integrals are suppressed
    to ≲ √2·b·sup|Δρ₄|·e^{−ω²b²/2π} ≈ e^{−240}.
  - The pipeline's changes of ~1e-9 are therefore not this effect. They are attributed to the numerical floor of its
    grids and of the NUFFT long-range sums. Its own accuracy diagnostics (pair overlaps 1e-8, Fourier tails ~5e-6) sit
    at or above this level. This attribution was not tested separately.
- **The earlier partial check stands** (`check_s13_stage2.py`, `results/check_s13_stage2.json`).
  - Settings: three F2 heights; in-pair offsets (0.5, 0.5), (0.2, 0.9) and (1.2, 0.4); r ≤ 2000 on Δr = 0.05;
    p ≤ 10⁴.
  - sup|Δρ₄| ≤ 1.24e-4.
  - The mean over r ∈ [100, 2000] is ≤ 2.4e-8.
  - The b = 100 window integral is ≤ 2.7e-19.
- **Therefore unchanged:** Stage 2's v(b), v_B(b), g, the ĝ_B prediction (0.6830 pooled), ρ₁(b), the PASS read, and
  the L4 comparison (CS08's −0.031 to −0.034 at b = 100).
- **L3's C(r):** the RMS of the assembled C(r) on [4.7·10⁴, 4.8·10⁴] moves by +1.5e-6 to +5.4e-6 across the five
  heights, about 1e-4 of its value. At ℓ = 16.50 it goes from 0.052643 to 0.052648. The pointwise bound is ≤ 2.8e-4,
  and L3's statement is unchanged.
- **Not unchanged:** anything that evaluates ρ₄ unwindowed at short range. This affects route (a)'s spacing law,
  which had not been tagged when the error was found. No released number does this.
