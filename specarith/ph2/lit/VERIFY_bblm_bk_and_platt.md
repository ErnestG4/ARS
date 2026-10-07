# Independent check of `bblm_bk.md` against primary sources, and Platt / LMFDB height scoping

Verification agent, 2026-10-07. Will asked for this ("check these against the primary sources before anything is
sealed"). It is not yet reviewed. Every source was re-opened for this check. arXiv PDFs and LaTeX were
**re-fetched from arXiv** into `~/specarith_lit_cache/ph2/verify2/` (outside the repo) and hashed. The first agent's
cache was used only for sha256 comparison. No zeta-zero statistic was computed. Two zero files were sampled by HTTP
byte-range, ≤ 50 zeros each, to confirm the format.

Verdict key. **VERIFIED**: I re-opened the source and the claim matches it. **CORRECTED**: the claim is wrong or
needs qualifying, and the correction is given. **UNVERIFIED**: I could not open the source.

Page and equation numbers refer to the arXiv PDF named, as paginated by pypdf. Equation numbers were read from the
PDF text and cross-checked against the order of `\label`s in the LaTeX source.

---

## 0. Summary

| # | Claim in `bblm_bk.md` | Verdict |
|---|---|---|
| A1a | N_eff = log(E/2π)/√(12Λ) is BBLM eq. (19) | **VERIFIED** (arXiv v1 p. 5) |
| A1b | Λ ≡ γ₀² + 2γ₁ + c₀, with c₀ = Σ_p log²p/(p−1)² | **VERIFIED** (p. 4 unnumbered displays, p. 5 eq. (19)) |
| A1c | BBLM print Λ = 1.57314… | **VERIFIED** as printed (abstract p. 1 and p. 5). The printed value is low by 1.1×10⁻⁵ (A2). |
| A1d | Eq. (16): R₂ to O(ρ̄⁻³) with Q | **VERIFIED**. The expansion (14)+(15) → (16) was also re-derived by hand. |
| A1e | Eqs. (21)–(24) spacing recipe; α = 1 + C/log(E/2π), C = Q/Λ | **VERIFIED** (pp. 5–7) |
| A1f | Data heights: E = 2.5041178×10¹⁵ and 1.30664344×10²², 10⁹ zeros each | **VERIFIED** (pp. 2, 5, 7) |
| A1g | BBLM's scale convention | **VERIFIED, with a point for Will** (§A1.6): BBLM's stated prediction (24) *includes* the exterior α. "N_eff alone" is BBLM's dashed comparison curve, not their prediction. |
| A2 | Λ = 1.5731510713 24955…, Q = 2.3158463849 58803… | **VERIFIED independently** by a different method; agrees with BFM to all 16 printed digits (difference 2×10⁻¹⁶). BBLM's 1.57314 and C = 1.4720 are low. |
| A3a | BFM footnote: BBLM "[Eq. (28)] contains a miscalculation …"; ᾱ = 2α − 1 | **VERIFIED** (BFM arXiv v4 p. 17, footnote 5, eq. (4.5)). The algebra was re-derived and checked numerically. |
| A3b | BFM's secondary model: K_RZ = K + L_RZ N⁻², L_RZ = π(x−y) sin(πᾱ(x−y))/6 | **VERIFIED** (eqs. (4.3)–(4.6), pp. 16–17) |
| A3c | BFM values ρ̄ = 7.81235 22019 1727…, N = 11.29759 09009 547…, α = 1.02999 00807 6719…, ᾱ = 1.05998 01615 3438… | **VERIFIED** (p. 18). All four were reproduced to every printed digit from the first-zero height. |
| A3d | BFM numerical method: p = d²/ds² det(I − K_s^N), K^N = sin πx/(N sin(πx/N)); Nyström / Gauss–Legendre | **VERIFIED** (eqs. (1.7)–(1.13) pp. 3–4; §2.2 pp. 7–8; Appendix). The Appendix values were reproduced to 15 digits. BBLM (22) equals the BFM Fredholm determinant to 10⁻¹⁵. |
| A4a | The pair correlation with arithmetic lower-order terms is BK PRL 77 (1996) 1472 | **Attribution VERIFIED** (BBLM, FM15, BFM and BK 2013a/b all cite the PRL for it). **Content UNVERIFIED**: the PRL full text is closed, it is not on arXiv, and the HAL record is a notice with no file. The PRL **abstract** was obtained this time. It describes generic chaotic systems and does not mention the Riemann zeros (§A4). |
| A4b | The Nonlinearity 1995/1996 papers give asymptotic GUE agreement only | **VERIFIED from abstracts** (OpenAlex). Full text UNVERIFIED: IOP lists the papers as "bronze OA", but the PDF is behind a JavaScript challenge. |
| A4c | The first agent "read the PRL abstract" | **CORRECTED**: the cached `prl77_1472.html` is a Cloudflare challenge page and contains no abstract. |
| A5 | BFM's "nearest neighbour spacing" means min(left gap, right gap) | **VERIFIED** (BFM p. 5 and §3.5 p. 12; Nishigaki §4). **Qualification:** FM15 uses "nearest neighbour spacing" for the *consecutive* spacing p(0;s), as BBLM do. So the trap applies to BFM and Nishigaki, not to FM15. |
| A6 | FM15 eq. (1.1) prints ρ̄ = (1/2π)log(E/(2πe)) + O(log E/E) and calls it a density | **VERIFIED** (FM15 arXiv v3 p. 1). It is printed as "the density", but it is N(E)/E (A6). Will's θ(E)/π + 1 unfolding agrees with BBLM's ρ̄ to O(E⁻²). |
| B | Platt / LMFDB heights | LMFDB serves **all 103,800,788,359 zeros with 0 < γ ≤ 30,610,046,000** (log(E/2π) up to **22.31**). They are rigorous (±2⁻¹⁰², completeness by Turing's method), contiguous, and downloadable at any height with md5 checksums (CC BY-SA 4.0). This continuously fills **log(E/2π) ∈ [12.1, 22.3]**, which no Odlyzko table covers. Nothing public was found in **24.5 < log(E/2π) < 44.6**. Platt–Trudgian 2021 (RH to 3×10¹²) did **not** store zeros. See the Part B table. |

**Corrections to `PH2_DECISIONS_2026-10-07.md`, item 3** (heights). The public Odlyzko tables span log(E/2π) from
**0.81** (the first zero) to **46.83** (zero #10²²+1). "About 9" is the *top* of `zeros1` (9.39); `zeros6` reaches
12.10. The three high tables hold **only 10⁴ zeros each**, at log(E/2π) = 24.48, 44.58 and 46.83. At log(E/2π) ≲ 9.4,
N_eff ≲ 2.2 and N_eff⁻² ≳ 0.21. Whether a 1/N_eff² expansion means anything there is a design question for Will. I
flag it and do not judge it.

---

## Part A — load-bearing claims

### A1. BBLM, arXiv:math/0602270 **v1** (the only arXiv version; 9 pp.)

Re-fetched: PDF sha256 `38baa479…ccea`, identical to the first agent's copy. `bblm.tex` sha256 `52902e9b…1dd1`,
identical. arXiv metadata: v1 only, "9 pages, 3 figures", journal-ref J. Phys. A 39 (2006) 10743–10754.
**The journal version is UNVERIFIED**: IOP returns an error page. OpenAlex lists HAL hal-00118511 and arXiv as the
only OA copies, and both are v1.

**A1.1 N_eff, eq. (19), p. 5. VERIFIED.** From the LaTeX, `\label{neff}`:
> "To leading order in 1/ρ̄ the two–point correlation function of the Riemann zeros coincides with that of
> eigenvalues of random CUE_N matrices of effective dimension N = N_eff, where
> N_eff = πρ̄/√(3Λ) = (1/√(12Λ)) log(E/2π), (19)
> where Λ ≡ γ₀² + 2γ₁ + c₀ = 1.57314…"

The abstract (p. 1) repeats it: "N_eff = log(E/2π)/√(12Λ), where Λ = 1.57314… is a well defined constant". p. 5
gives "N_eff = (12Λ)^{-1/2} N₀ = 0.230158 N₀".

**A1.2 Definition of Λ, pp. 4–5. VERIFIED.** The unnumbered displays on p. 4 are:
ζ(1+x) = 1/x + Σ_n ((−1)ⁿ/n!) γ_n xⁿ ("γ_i are the Stieljes constants" [sic]);
c_n = ((−1)ⁿ/(2n)!) Σ_p (log p)^{2(n+1)} Σ_{r≥1} (r−1) r^{2n}/p^r;
Π_p[1 − (1−p^{iε})²/(p−1)²] = 1 + c₀ε² + iQε³ + O(ε⁴), with Q = Σ_p log³p/(p−1)².
Since Σ_{r≥1}(r−1)p^{−r} = 1/(p−1)², c₀ = Σ_p log²p/(p−1)². I checked this by expanding the product to O(ε³).
Note that BBLM never print c₀ = Σ log²p/(p−1)² in closed form. The closed form is BFM's (p. 14) and Bogomolny 2007's.
That identity is exact.

**A1.3 Eq. (16), p. 5. VERIFIED.** `\label{r2r1}`:
> R₂(s) = 1 − sin²(πs)/(π²s²) − ((γ₀²+2γ₁+c₀)/(π²ρ̄²)) sin²(πs) − (Q/(2π²ρ̄³)) s sin(2πs) + O(ρ̄⁻⁴) (16)

with ρ̄ = (1/2π)log(E/2π) (eq. (10), p. 4) and R₂(s) = ρ̄⁻² r₂(s/ρ̄) (eq. (13), p. 4). I re-derived (16) by hand
from (14)–(15):
- log|ζ(1+iε)|² = −2 log ε + (γ₀²+2γ₁)ε² + …, so r₂^diag = −1/(2π²ε²) − Λ/(2π²) + O(ε²), which is eq. (14).
- Inserting (15) and unfolding gives the three correction terms of (16) exactly, signs included.

**A1.4 Eqs. (17)–(18), p. 5. VERIFIED.** (17) R₂ = 1 − sin²(πs)/(π²s²) − (Λ/(π²ρ̄²)) sin²(παs) + O(ρ̄⁻⁴), and
> α = 1 + Q/(2πρ̄(γ₀²+2γ₁+c₀)) = 1 + C/log(E/2π) (18), "C = Q/(γ₀²+2γ₁+c₀) = 1.4720…"

Check: sin²(παs) = sin²(πs) + (α−1)πs sin(2πs) + O((α−1)²). This reproduces the Q term of (16) iff
α − 1 = Q/(2πρ̄Λ). ✓.

**A1.5 Eqs. (20)–(24), pp. 5–7. VERIFIED.**
- (20) "s → αs" is stated as rule ii): "The next-to-leading order is obtained by rescaling the variable s in the
  first correction term according to s → αs".
- (21) p^(CUE_N)(s) = d²E(s)/ds².
- (22) E(s) = det[δ_jk − sin(πs(j−k)/N)/(π(j−k))], 1 ≤ j,k ≤ N (p. 6).
- (23) p^(CUE_N)(s) = p₀(s) + N⁻²p₁(s) + O(N⁻⁴). BBLM: "We have therefore computed numerically … p₁(s) = N²[p^(CUE_N)(s)
  − p₀(s)] for increasing values of N". The values of N are not stated, as the first agent said.
- (24), p. 7: δp(s) = N_eff⁻² p₁(αs) + O(N_eff⁻⁴).

**A1.6 Heights and BBLM's scale convention. VERIFIED.** Heights:
- Fig. 1 caption (p. 2): "a window near E = 2.5041178×10¹⁵". The text says "a billion zeros around the 10¹⁶-th zero".
- p. 7: "N_eff = 7.7376 (instead of N₀ = 33.6188), and α = 1.0438".
- p. 7: "one billion zeros located on a window around E = 1.30664344×10²², which corresponds to N_eff = 11.2976
  (instead of N₀ = 49.0864) and α = 1.0300".

I recomputed these with the true Λ: 7.737610 / 1.043788 and 11.297591 / 1.029990. Both agree with the printed digits.
BBLM's own Λ gives 7.737637 and 11.297631, which round to the same values. N₀ = 49.08646 is printed *truncated* as
49.0864. This is cosmetic.

**BBLM's convention, stated exactly (this is what Will's "primary model" should pin):**
1. **Unfolding:** s is in units of the mean spacing 1/ρ̄, with ρ̄ = (1/2π) log(E/2π) (eq. (10); "s is the unfolded
   distance between zeros (i.e. the mean spacing is set to one)", p. 1). How BBLM unfolded the *data* (local or
   global window) is not stated in v1.
2. **Size:** N_eff from (19), with Λ.
3. **Scale:** an *exterior* rescaling of the correction term only. p₀(s) is left unscaled, and only the argument of
   p₁ is multiplied by α from (18): **p(s) = p₀(s) + N_eff⁻² p₁(αs)**, eq. (24).

BFM give this convention the name "exterior rescaling" (BFM §4.2 p. 15). They confirm that for R₂ it is correct to
O(N⁻⁴), with the same α:
> "α = 1 + Q/(2πΛρ̄) = 1 + Q/(Λ log(E/2π)) = 1 + Q/(Λ√(12Λ)) N⁻¹" (BFM p. 15, unnumbered)

**Point for Will.** His decision 4a says "primary model: BBLM's leading correction (N_eff alone), with BBLM's own
scale convention". In BBLM, "N_eff alone" (p₀ + N_eff⁻² p₁(s), with no α) is the **dashed comparison curve** of
Figs. 2–3: "For comparison, we have plotted as a dashed curve the theoretical formula (24) without the rescaling of the
variable s" (p. 7). BBLM's *prediction* is (24) **with** α. Both variants are BBLM's own and both use BBLM's α, so
neither mixes slots. But "N_eff alone" and "BBLM's own scale convention" name two different curves, and the
pre-registration has to say which one, or carry both as arms.

**A1.7 Erratum provenance.** BFM's "[BBLM06, Eq. (28)]" and "[BBLM06, p. 10748]" refer to the **journal** version.
arXiv v1 ends at eq. (24) and has no appendix. So arXiv v1 **contains no α/ᾱ error**: its (24) uses α in the
exterior sense, which BFM accept as correct for exterior rescaling. The error BFM flag concerns the kernel statement
in the journal appendix, which is UNVERIFIED (not opened).

Bogomolny 2007 (arXiv:0708.4223v1, re-fetched; LaTeX `zeta.tex`, label `deltak`) shows the same slip *inside one
display*:
> k₁(ε) = ε (β/(2π d̄²)) sin(πε) + ε² (δ/(2π d̄³)) cos(πε) = (πε/(6N_eff²)) sin(παε), α = 1 + δ/(β ln(E/2π))

**Check:**
- The first equality, with δ ≡ Q and β ≡ Λ, equals BFM's L·N⁻² + μ·N⁻³ term for term. I checked this:
  μN⁻³ = Q s² cos(πs)/(2π d̄³).
- Expanding the second equality gives only half of the cos term. It needs ᾱ − 1 = 2(α − 1).
- So Bogomolny 2007 is internally inconsistent by exactly the factor BFM identify. This independently corroborates
  BFM's footnote.

### A2. Λ and Q recomputed. VERIFIED (BFM digits); BBLM digits CORRECTED

The method is deliberately different from the first agent's sieve. Script:
`~/specarith_lit_cache/ph2/verify2/checks/lam_verify.py`, mpmath at 40 digits.
- γ₀ = 0.5772156649015328606…, γ₁ = −0.0728158454836767248… (`mp.stieltjes(1)`), so γ₀² + 2γ₁ = 0.18754623284036522…
- c₀ and Q are computed with no tail estimate. Primes ≤ 100 are summed explicitly, and the rest use the exact identity
  log²p/(p−1)² = log²p Σ_{r≥2}(r−1)p^{−r}, i.e. c₀ = Σ_r (r−1) P″(r) and Q = −Σ_r (r−1) P‴(r), where P is the prime
  zeta function (`mp.primezeta`) with the small primes removed. The r-series converge like 100^{−r}.
- Cross-check: a direct sieve to 10⁷ with a PNT tail integral. It agrees to ~10⁻¹¹.

| Constant | This check | BFM 2017 (v4 p. 14) | BBLM v1 | Status |
|---|---|---|---|---|
| c₀ | 1.385604838484590002682… | — | — | — |
| **Λ** | **1.573151071324955227…** | 1.57315 10713 24955… | 1.57314… (p. 1, p. 5) | BFM VERIFIED (Δ = 2.3×10⁻¹⁶). BBLM low by 1.107×10⁻⁵. |
| **Q** | **2.315846384958803289…** | 2.31584 63849 58803… | (not given) | BFM VERIFIED (Δ = 2.9×10⁻¹⁶) |
| C = Q/Λ | 1.472106797097578… | — | 1.4720… (p. 5) | BBLM low (1.4721…) |
| (12Λ)^{−1/2} | 0.2301569860708… | — | 0.230158 (p. 5) | BBLM's value follows from its low Λ |
| δ (Bogomolny 2007 name for Q) | 2.3158464 | — | Bog07: "≈ 2.3157" | Bog07 low |

The first agent's numbers (Λ = 1.573151071326132, Q = 2.315846384982841) are right to ~10⁻¹² and ~2×10⁻¹¹. The residual
there comes from their tail estimate. **Cite BFM 2017 for the digits**, as Will decided. This confirms Will's item 1:
N_eff moves by 3.5×10⁻⁶ relative, which is negligible.

### A3. Bornemann–Forrester–Mays 2017, arXiv:1608.04638 **v4** (latest; 22 Feb 2017; "31 pages … Corrected typos")

Re-fetched PDF sha256 `41cccd7a…a66d`, identical to the first agent's v4. Source `BFM_21Feb.tex`.

**A3.1 Footnote. VERIFIED.** p. 17, footnote 5, attached to eq. (4.5):
> "Note that [5, Eq. (28)] contains a miscalculation by claiming that ᾱ would be the same as α."

([5] = BBLM06, J. Phys. A 39 (2006) 10743.)

**A3.2 BFM's own convention for the higher-order (secondary) model. VERIFIED.** §4.3 "Interior rescaling of the
leading correction terms", pp. 16–17:
- (4.3), p. 16: K_RZ^N(x,y) = K(x,y) + L(x,y)N⁻² + M(x,y)N⁻³ + O(N⁻⁴), with M(x,y) = μ(x−y).
- Unnumbered, p. 17: "Matching with (4.1) gives, cf. the first equality in [5, Eq. (28)], μ(s) = η π²s² cos(πs)/6,
  η = Q/(Λ√(3Λ))".
- (4.4): **L_RZ(x,y) = π(x−y) sin(πᾱ(x−y))/6**. "which expands as L_RZ = L + M N⁻¹ + O(N⁻²)". *Only the sine's
  argument is rescaled. The prefactor π(x−y) is not.*
- (4.5): **ᾱ = 1 + ηN⁻¹ = 1 + Q/(πΛρ̄) = 1 + 2Q/(Λ log(E/2π)) = 2α − 1.**
- (4.6): **K_RZ^N(x,y) = K(x,y) + L_RZ(x,y)N⁻² + O(N⁻⁴)**. The recipe: "simply replace the leading correction kernel
  L by its interior rescaling L_RZ".
- Here N is BFM's N = (1/√(12Λ)) log(E/2π) (p. 14, unnumbered), i.e. the same N_eff. ρ̄ = log(E/2π)/(2π) (p. 14,
  unnumbered, under (4.1)).
- The statistic's correction is then computed as Ω(K_s) : (L_RZ)_s in place of L_s, from (1.11)–(1.13).

So the secondary model is **fully specified inside BFM**: kernel (4.6) with (4.4), scale ᾱ from (4.5), and N from p. 14.
No BBLM quantity enters except the matching that BFM themselves redo. That satisfies Will's 4a rule.

**My algebra check.** −2K₀·L_RZ·N⁻² = −(1/(3N²)) sin(πs) sin(πᾱs). Matching it to the exterior form
−(1/(3N²)) sin²(παs) at first order in (α−1) requires ᾱ − 1 = 2(α − 1). Numerically (`det_verify.py`), with ε = 10⁻⁶:
- max|exterior − interior| / ε = 3×10⁻⁵ when ᾱ = 1 + 2ε (second-order residual);
- the same quantity is 1.44 when ᾱ = α, i.e. a first-order mismatch.

BFM's footnote is right.

**A3.3 BFM quoted values. VERIFIED** (p. 18, §4.4). The data set is "1 041 719 075 consecutive zeros starting with zero
number 10²³ + 985 531 550", and the first has height 13 066 434 408 793 621 120 027.39614 65854… (pp. 17–18).
> ρ̄ = 7.81235 22019 1727…, N = 11.29759 09009 547…, α = 1.02999 00807 6719…, ᾱ = 1.05998 01615 3438…

Recomputed from that first height with my Λ and Q: ρ̄ = 7.812352201917277, N = 11.29759090095475,
α = 1.029990080767193, ᾱ = 1.059980161534386. **All printed digits match.**

**A3.4 Numerical method for finite-N CUE spacing. VERIFIED.**
- (1.7), p. 3: p^{U(N)}(0;s) = d²/ds² det(I − K_s^N).
- (1.8): K^N(x,y) = sin π(x−y)/(N sin(π(x−y)/N)), "the integral operator on (0,s)".
- (1.9)–(1.10), pp. 3–4: K^N = K + N⁻²L + O(N⁻⁴), L(x,y) = (π(x−y)/6) sin π(x−y).
- (1.11)–(1.13), p. 4: det(I − K_s^N) = det(I − K_s) + N⁻² Ω(K_s):L_s + O(N⁻⁴), with
  Ω(K_s):L_s = −det(I − K_s) tr((I − K_s)⁻¹L_s), and r₂(0;s) = d²/ds² Ω(K_s):L_s.
- §2.2, pp. 7–8: Nyström matrix K_w = (K(x_j,x_k)w_k), Gauss–Legendre, exponential convergence for analytic kernels.
  "The numerical derivatives with respect to the s and z variables … are computed … based on Chebyshev expansions with
  respect to s and contour integration with respect to z" (p. 8).
- Appendix (pp. 28–29, Matlab): det(I − K_s)|_{s=1} = **0.170217421379185** and Ω|_{s=1} = **−0.075241982465122**,
  "good to about 15 digits".

Reproduced by `det_verify.py` (symmetric Nyström, Gauss–Legendre, m = 20 and 40): 0.170217421379185 and
−0.075241982465122 (m = 40). Also, BBLM's Toeplitz (22) and BFM's Fredholm (1.7)/(1.8) agree to <10⁻¹⁵ at s = 1 for
N = 5, 8, 12.

The first agent's description of the method (§4 of `bblm_bk.md`) is VERIFIED. Their Forrester–Shen closed form was
not in scope here and was not re-checked.

### A4. Bogomolny–Keating: which paper has the arithmetic lower-order terms

**arXiv search.** The API for au:Bogomolny AND au:Keating returns only 1307.6010, 1307.6012 and nlin/0010045. Bogomolny's
1994–98 arXiv items are chao-dyn/9409004, 9509019 and 9604001, and cond-mat/9801171. A title search for "diagonal
approximation" with "Gutzwiller" returns nothing. **The PRL is not on arXiv.** HAL in2p3-00000969 is
`submitType: notice` with no file. APS returns 403. Semantic Scholar and OpenAlex mark it closed.

**PRL abstract** (obtained via OpenAlex this time):
> "We calculate the 2-point spectral correlation function for classically chaotic systems in the semiclassical limit
> using Gutzwiller's trace formula. The off-diagonal contributions from pairs of nonidentical periodic orbits are
> evaluated by relating them to the diagonal terms. The behavior we find is similar to that recently discovered to
> hold for disordered systems using nonperturbative supersymmetric methods. Our analysis generalizes immediately to
> include parametric statistics and higher-order correlations and to the study of the semiclassical distribution of
> matrix elements."

The abstract does not mention the Riemann zeros. **Whether the PRL prints the explicit Riemann formula is
UNVERIFIED.** The attribution of that formula to the PRL rests on later papers:
- BBLM bib `[bk]` = the PRL. Text, p. 4: "An heuristic formula for the two-point correlation function for these zeros
  was obtained by Bogomolny and Keating in Ref. [bk] using the Hardy-Littlewood conjecture … (for more details see
  [Varenna, LesHouches])."
- BK 2013b (arXiv:1307.6010v1, re-fetched, sha256 equals cache) §1: "A more precise expression for the two-point
  correlation function of the Riemann zeta function zeros was obtained in [keating = the PRL] using another method which
  is equivalent to the full Hardy-Littlewood conjecture (details of the calculations can be found in [varenna])." The
  same paragraph says the Nonlinearity papers used "the same smoothed form of the Hardy-Littlewood conjecture".
- BK 2013a (1307.6012v1, sha256 equals cache), §"Two-point correlation function of Riemann zeros": "It was calculated in
  [PRL] by using the explicit form of the Hardy-Littlewood conjecture". The two 2013 papers describe the PRL's method
  slightly differently. The PRL abstract supports "relating off-diagonal to diagonal terms", i.e. the 2013b wording.
- FM15 and BFM cite `BK96b` = the PRL for it (BFM p. 14: "Bogomonly [sic] and Keating [BK96b] had earlier given an
  analytic expression for the pair correlation").
- **Caveat.** Bogomolny's Les Houches lectures (nlin/0312061v1, re-fetched, sha256 equals cache) derive the formula
  themselves (§"Beyond the Diagonal Approximation", eq. (57), p. 61; HL input eqs. (54)–(55), p. 58). There he cites
  the PRL only for "dynamical systems": "We shall discuss here this type of computation on the example of the Riemann
  zeta function … (for the latter see [KeatingBogomolny = PRL] and [Bogomolny2])".
- The first agent's p. 58 typo ("for even r α(r) = 0 and for odd r …", reversed) is **VERIFIED** in the PDF.

**Nonlinearity papers** (abstracts via OpenAlex; full text UNVERIFIED):
- I (Nonlinearity 8 (1995) 1115): "we demonstrate that the 3-point and 4-point zero correlation functions are
  asymptotically equivalent to the corresponding GUE results. Our method centres around a Hardy-Littlewood
  conjecture … The calculation generalises a previous study of 2-point correlations".
- II (Nonlinearity 9 (1996) 911): "for all n the n-point correlation function of the zeros is equivalent to the
  corresponding GUE result in the appropriate asymptotic limit."

These match the first agent's report. One small bibliographic slip: BBLM's bib gives Nonlinearity 9 as "(1995)". It
is 1996 (Crossref).

**Bottom line for Will's item 2.** Citing the PRL is what every later source by the same authors does, so it is the
right citation. The *formula itself* should be quoted from a readable restatement (BBLM eqs. (9)–(12); Les Houches
eq. (57); BK 2013a eqs. (50), (58)), with the PRL as the attribution. **Practical tip:** IOP marks both Nonlinearity
papers as free ("bronze OA"). Will can probably download them in a browser; only scripted access is blocked. The PRL
needs institutional access.

### A5. "Nearest neighbour spacing" naming. VERIFIED, with a qualification

- BFM p. 5 (§1.1): "the statistic for the nearest neighbor spacing, that is, the minimum of the spacing distance
  between left and right neighbours".
- BFM §3.5, p. 12: "at each eigenvalue one measures the smallest of the spacings to the eigenvalue immediately to the
  left, and the spacing immediately to the right". p_nn is defined in (3.26)–(3.30), using the kernel
  K^nn = K(x,y) − K(x,0)K(0,y) on (−s,s).
- BFM call the consecutive spacing "the 0-th next neighbour spacing" (footnote, p. 18). The k-th next neighbour of
  x_j is "item x_{j+k+1}" (footnote, p. 2).
- Nishigaki 2507.10193v1 (PDF sha256 equals cache; source `DCLS_CUE.tex`): "the nearest neighbor spacing
  t = min(|a₁|, a₂)".
- **Qualification:** FM15 (arXiv v3) uses the BBLM sense. Fig. 9 caption (p. 20): "Comparison of Riemann zero nearest
  neighbour spacing (where each zero is scaled by the leading term in (1.1)) …". That figure is p(0;s). So "nearest
  neighbour" means consecutive in BBLM and FM15, and min(left, right) in BFM and Nishigaki.

### A6. FM15 eq. (1.1). VERIFIED (as printed); interpretation confirmed

FM15 arXiv:1506.06531 **v3** (latest; re-fetched PDF sha256 `900567ea…6fda`, identical). Comment: "Version 3
corrected the scaling on the spacing distribution and some typos". p. 1:
> "… at position 1/2 + iE along the critical line, and with E ≫ 1, the density (ρ̄ say) is given by [55, pg. 280]
> ρ̄ = (1/2π) log(E/(2πe)) + O(log E / E). (1.1)"

([55] = Whittaker & Watson.)

**It is printed and named as a density. Its form is that of N(E)/E**, the mean density over (0, E):
- N(E) = (E/2π) log(E/2πe) + 7/8 + S(E) + O(1/E), and S(E) = O(log E). So N(E)/E = (1/2π)log(E/2πe) + O(log E/E),
  which is exactly (1.1) including its error term.
- The local density is dN̄/dE = (1/2π) log(E/2π).
- FM15 then use "ρ̄ given by the leading term in (1.1)" for the BK expansion (p. 5), and "rescale the data by (1.1)"
  (p. 6). On p. 19 they say "we have used the scalings (2.5) and (2.6) from [8]" (= BBLM), with (2.5)
  N = log(E/2π)/√(12Λ) (p. 6).
- The text cannot settle which density they actually used on the data. The first agent was right about that.

Will's 4b reading is right in substance. The more precise statement is that log(E/2πe) is the form of N(E)/E rather
than of N(E). His choice, unfolding by θ(E)/π + 1, is consistent with BBLM's convention:
d/dE[θ(E)/π] = (1/2π) log(E/2π) + O(E⁻²). So the exact count and BBLM's ρ̄ agree as local densities to O(E⁻²), while
avoiding the ~1/log(E/2π) global-offset trap.

---

## Part B — additional public, hashable heights

### B1. LMFDB / Platt zeta zeros

**What is served** (quoted from the LMFDB pages, fetched 2026-10-07):
- Completeness page: "This database contains the 103,800,788,359 zeros of the Riemann zeta function ζ(s) with
  imaginary part in the interval (0, 30 610 046 000], all of which have real part 1/2. Data computed by David Platt."
- Source page: "The imaginary part of each zero is stored with an absolute precision of ±2^−102. The completeness of
  the list was verified using a rigorous version of Turing's method." Raw data: https://beta.lmfdb.org/data/riemann-zeta-zeros/.
- Reliability page: "The results have been checked to a separate list of zeros independently computed by Jan Büthe to
  an accuracy of ±2^-64 (this comparison found 108 minor discrepancies, each of which was resolved in favor of the data
  presented here)."
- **Citation.** The LMFDB pages cite MR:3315519 = Platt, "Computing π(x) analytically", Math. Comp. **84** (2015)
  1521–1535 (Crossref), for the algorithm. The paper that actually describes *this* zero set is
  **D. J. Platt, "Isolating some non-trivial zeros of zeta", Math. Comp. 86 (2017) 2449–2467,
  doi:10.1090/mcom/3198**. Its abstract (OpenAlex): "…isolate the non-trivial zeros of zeta with imaginary part
  ≤ 30,610,046,000 to an absolute precision of ±2^−102. In the process, we provide an independent verification of the
  Riemann Hypothesis to this height." Platt–Trudgian 2021 cite it as the source of the database (`\bibitem{Platt}`).
  Cite both papers plus the LMFDB.
- **Platt–Trudgian**, "The Riemann hypothesis is true up to 3·10¹²", Bull. LMS **53** (2021) 792–797,
  doi:10.1112/blms.12460, arXiv:2004.09765v1. **No zeros above 3.06×10¹⁰ were stored.** From the arXiv source:
  "A key motivation of [Platt 2017] was to generate a database of rigorously isolated zeroes to high precision, but to
  do so here would have added to the run time and, in any case, we had nowhere to store that many zeroes. … we merely
  counted it and moved on."

**Access mechanics:**
1. **Web text API.** `https://www.lmfdb.org/zeros/zeta/list?N=<index>&limit=<k>` (or `t=<height>`). From LMFDB source
   `lmfdb/zeros/zeta/zetazeros.py` (GitHub `main`, sha256 `75b3f598…`):
   - the output is plain text "`n γ`" with 31 + ⌊log₁₀γ⌋ + 1 significant digits;
   - `limit` may be up to **100,000** ("Too many zeros" above that);
   - `download=yes` gives an attachment.
   - Worked via WebFetch: `N=10000000000&limit=5` returned "10000000000 3293531632.3971367042089917031338769677068 …".
   - **reCAPTCHA-walled to curl** (confirmed). It is hashable, but the text depends on the server's formatting code.
     Pin the server code version, or prefer route 2.
2. **Bulk binary files** (recommended for hashing). `https://beta.lmfdb.org/data/riemann-zeta-zeros/zeros_<t0>.dat`.
   - **14,580 files, ≈1.29 TB in total**, all dated 2016-06-01 (static).
   - From t₀ = 446,000 on, each file spans 2.1×10⁶ in t. That is 1,000 blocks of t-length 2,100, holding ≈7.4×10⁶
     zeros at the top height. Size per file is 57 KB to 92 MB.
   - **`md5.txt` publishes an md5 for every file** (14,580 lines; my copy has sha256 `6ca3534a…8521`).
   - HTTP `Accept-Ranges: bytes` and `ETag` are present.
   - Access is behind a trivial JavaScript gate that sets the cookie `human=1`. curl with `-b human=1` works; this is
     what a browser does.
   - **Format** (documented by `lmfdb/zeros/zeta/platt_zeros.py`, J. Bober):
     - 8-byte uint64 holding the number of blocks;
     - then per block a 32-byte header `ddQQ` = (t₀, t₁, N(t₀), N(t₁));
     - then N(t₁) − N(t₀) records of 13 bytes (`QIB`, little-endian). These are *cumulative* integer deltas, so
       γ = t₀ + Z·2⁻¹⁰¹.
3. **Format confirmed on a sample** (byte-range 0–689 of two files, ≤ 50 zeros decoded each; `checks/platt_head.py`):
   - `zeros_14.dat`: header (14.0, 5000.0, 0, 4520), first zero 14.13472514173469379045725198356… ✓.
   - `zeros_30607946000.dat`: header (30607946000.0, 30607948100.0, 103793332900, 103793340354), i.e. 7,454 zeros in
     the first 2,100-wide block; zero #103,793,332,901 = 30607946000.43979868008487584315….
   - In both files, Hardy's Z(t) changes sign across the first two decoded values (±10⁻⁶).
   - N(t₀) agrees with θ(t₀)/π + 1 to within 1, as it must.

**Can a contiguous block of ≥10⁴ consecutive zeros be had at arbitrary height? Yes, for heights up to 3.0610046×10¹⁰.**
- Route 1 gives it in one request (limit ≤ 10⁵), or 10 requests for 10⁶.
- Route 2 gives one ≤92 MB file of ~7×10⁶ consecutive zeros, md5-checkable against the publisher's list.
- **Near 10⁸ and 10¹⁰: yes. Near 10¹²: no LMFDB data.** Only Odlyzko's 10⁴ zeros near 2.68×10¹¹ exist publicly.
- Nishigaki 2025 already used "10⁸ zeros from n = 1.037×10¹¹ (LMFDB)". My computed N_eff at the LMFDB top, 5.134,
  matches their N_e = 5.13383…, so a published anchor exists at that height.

**Reproducible hash recipe:** download the whole file → check its md5 against `md5.txt` → record sha256 → (optionally)
pin the byte range of the blocks used, located by walking the block headers, which are themselves in the hashed file.
This meets Will's "public, hashable source".

**Terms.** LMFDB data license: "licensed under the Creative Commons Attribution-ShareAlike 4.0 International License
(CC-BY-SA)" (beta.lmfdb.org/license). LMFDB asks users to "use more efficient access options rather than scraping the
website directly, and to rate limit". Use the bulk files, not thousands of `list` calls. Citation form:
lmfdb.org/citation.

### B2. Odlyzko public tables (https://www-users.cse.umn.edu/~odlyzko/zeta_tables/)

Six static text files, Last-Modified 1999-02-17 for the high tables. No checksums are published; hash them yourself.
Headers were read by byte-range (≤6 zeros each):
- `zeros1`: the first 100,000 zeros, "accurate to within 3*10^(-9)".
- `zeros6`: the first 2,001,052 zeros, "accurate to within 4*10^(-9)".
- `zeros2`: the first 100 zeros to over 1,000 decimals.
- `zeros3`: zeros #10¹²+1 … 10¹²+10⁴, given as γ − 267653395647. "Values are guaranteed to be accurate only to within
  10^(-8)." 180,287 bytes.
- `zeros4`: #10²¹+1 … +10⁴, γ − 144176897509546973000. "Values are not guaranteed, and are probably accurate to within
  10^(-6)." 160,319 bytes.
- `zeros5`: #10²²+1 … +10⁴, γ − 1370919909931995300000. Same caveat. 170,318 bytes.

There are no stated terms of use. The ≈10⁹–10¹⁰-zero sets at 10²⁰ and 10²³ (BBLM, FM15, BFM, Nishigaki) were
*provided privately* (BFM acknowledgements: "We are grateful to A. Odlyzko for providing us with the Riemann zero data
set") and are **not public**. The `~odlyzko/unpublished/` page holds manuscripts only, no data.

### B3. Other candidates checked

- **Gourdon 2004** ("The 10¹³ first zeros … and zeros computation at very large height", PDF re-fetched, sha256
  `b1868b1c…4025`). It computed "two billion zeros" at heights up to the 10²⁴-th zero (p. 1, p. 26). The paper contains
  **no data release**, and no public copy was found. Not usable.
- **Bober–Hiary zetacalc** (github.com/jwbober/zetacalc): *code*, not a zero list. A self-computed list could be made
  hashable with pinned code, but that is a new computation, not a public source. Not assessed.
- **arXiv:2512.09960** (Orellana Real, math.GM, "Valley Scanner", zeros "up to heights near 1e20", Zenodo
  10.5281/zenodo.17566257). Zeros are located from minima of |Z| with no completeness verification by Turing's method.
  **Not recommended** as a source for spacing statistics, because missed close pairs would bias exactly the small-s
  region. The datasets themselves were not opened.

### B4. Heights table

L = log(E/2π), N_eff = L/√(12Λ), α = 1 + (Q/Λ)/L, ᾱ = 2α − 1. E for index n comes from the smooth count θ(E)/π + 1 = n
(`checks/heights.py`; no zero data used).

| Source | Zeros available | E (first/representative) | L = log(E/2π) | N_eff | N_eff⁻² | α | ᾱ | Rigorous? | Public / hashable |
|---|---|---|---|---|---|---|---|---|---|
| LMFDB/Platt, low end | contiguous from #1 | 14.13 | 0.81 | 0.19 | 28.7 | — | — | yes (±2⁻¹⁰²) | yes (md5 + CC BY-SA) |
| Odlyzko `zeros1` top / LMFDB | #10⁵ | 7.49×10⁴ | 9.39 | 2.16 | 0.214 | 1.157 | 1.314 | Odl: 3×10⁻⁹ stated; LMFDB: yes | yes |
| Odlyzko `zeros6` top / LMFDB | #2,001,052 | 1.13×10⁶ | 12.10 | 2.79 | 0.129 | 1.122 | 1.243 | as above | yes |
| **LMFDB only** | #10⁷ | 4.99×10⁶ | 13.59 | 3.13 | 0.102 | 1.108 | 1.217 | yes | yes |
| **LMFDB only** | #10⁸ | 4.27×10⁷ | 15.73 | 3.62 | 0.076 | 1.094 | 1.187 | yes | yes |
| **LMFDB only** | #10⁹ | 3.72×10⁸ | 17.90 | 4.12 | 0.059 | 1.082 | 1.165 | yes | yes |
| **LMFDB only** | #10¹⁰ | 3.29×10⁹ | 20.08 | 4.62 | 0.047 | 1.073 | 1.147 | yes | yes |
| **LMFDB top** | up to #103,800,788,359 | 3.061×10¹⁰ | **22.31** | 5.13 | 0.038 | 1.066 | 1.132 | yes | yes |
| Odlyzko `zeros3` | 10⁴ from #10¹²+1 | 2.677×10¹¹ | 24.48 | 5.63 | 0.032 | 1.060 | 1.120 | ±10⁻⁸ stated | yes (no published checksum) |
| Platt–Trudgian RH limit | **none stored** | 3×10¹² | 26.89 | 6.19 | — | — | — | — | **no** |
| BBLM window (Odlyzko) | 10⁹, private | 2.504×10¹⁵ | 33.62 | 7.74 | 0.017 | 1.044 | 1.088 | — | **no** |
| Odlyzko `zeros4` | 10⁴ from #10²¹+1 | 1.442×10²⁰ | 44.58 | 10.26 | 0.0095 | 1.033 | 1.066 | "not guaranteed", ~10⁻⁶ | yes (no checksum) |
| Odlyzko `zeros5` | 10⁴ from #10²²+1 | 1.371×10²¹ | 46.83 | 10.78 | 0.0086 | 1.031 | 1.063 | "not guaranteed", ~10⁻⁶ | yes (no checksum) |
| Odlyzko 10²³ set (BBLM/FM15/BFM) | ~10⁹, private | 1.307×10²² | 49.09 | 11.30 | 0.0078 | 1.030 | 1.060 | — | **no** |

**What Platt adds.** Rigorous, arbitrarily large contiguous samples at **any L in [≈9, 22.31]**. Large samples (≥10⁸
zeros) are possible from L ≈ 16 up. The public record then has a **gap 24.5 < L < 44.6** that nothing public fills.
Above L = 22.3, the public samples are 10⁴ zeros each at three heights.

---

## Provenance

Everything is under `~/specarith_lit_cache/ph2/verify2/` (outside the repo, not committed).

**sha256 of what was fetched or read:**
```
38baa479453564421afb5d2e51e2676e93b7d4c3b6173d3b956bc5482e33ccea  bblm_v1.pdf          (= first agent's math_0602270.pdf)
52902e9b94e841cc700ae498180f645980d2ab8ec283dbbdd5068ac714a71dd1  s_bblm/bblm.tex      (= first agent's)
41cccd7a0ffb09955eba83651691338d3fad8daeb4e4aacc6c5dbb4b20fda66d  bfm17_latest.pdf     (v4; = first agent's)
86d6b429816eb271e3882906e3c4eed2cf5149ee41933337a39d3584a61a26ee  s_bfm/BFM_21Feb.tex
900567ea40f28af5e8f5268840d4a96ce32382c08de5c235c64de4a4a6016fda  fm15_latest.pdf      (v3; = first agent's)
0542f62449938cfe7f8dca38cdc38c74ef8db7287a4b9faf286aaf7311812ea6  s_fm/ForresterMays2015_RZd.tex
7192ed09888bc72fd9372610d2dd580fdb24b7824422888f6525f3f31b80a1ff  bk13a.src            (= cached 1307.6012.src)
d0dc511ac105651b348a3c4cd06ba14751bb6128237c162c7a9e1d0e8eebe84e  bk13b.src            (= cached 1307.6010.src)
030adc71bc55b35a2ebe8773f08f5932f7fa4c24a3d09e7b4e9da32401ddf750  lh.pdf               (Les Houches v1; = cached)
0f5f10260c8495d725f8bddf6826e3e9d045462ced2110f0266201d4d0fb5b09  b07.src              (Bogomolny 2007)
d9d11a658a9c23d442450f6e367f4dc925bb639df95230ba45439ae4108e0222  nish.pdf             (Nishigaki v1; = cached)
c4f13cdfca711d2bf90a097147be2a094ff175b0b161647359e174633fd8bf86  pt21.src             (Platt–Trudgian v1)
b1868b1c3f8d8661cb59c58ab6ceffc687dc6dce4d18d35b69117c84f60d4025  gourdon/g04.pdf
6ca3534a1e967f593a93428e6479eac0992c446a105da3eeb0b7a64121808521  platt/md5.txt        (LMFDB bulk checksums)
fe44da14f1012476e6fba7fcff92500a99ed9bd3697ef9352dce2b5935cacdc3  platt/platt_zeros.py (LMFDB reader)
75b3f5983a94b57d9c31fa895d54d9c04545a75d493b1cc30f5a9c1b46c8edac  platt/zetazeros.py   (LMFDB route code)
86c057102133db4d40cc5f989386e9ca55ee0679fa24967336992187a73cae68  platt/head_14.bin            (bytes 0–689)
647e2016ef845abd5d08de6a86358d6f52e59520229f0f1bb043455b6fd37b5a  platt/head_30607946000.bin   (bytes 0–689)
```
- Every sha256 in `bblm_bk.md` that I re-fetched (BBLM PDF and tex, BFM, FM15, Les Houches, Nishigaki, BK 2013a/b
  sources) matches.
- **`prl77_1472.html` in the first agent's cache is a Cloudflare challenge page, not an abstract.**

**Scripts** (`verify2/checks/`, venv python, `-I`):
- `lam_verify.py`: Λ, Q, C by the prime-zeta series plus a sieve cross-check; N_eff, α, ᾱ at the BBLM/BFM heights.
- `det_verify.py`: BFM Appendix known answers, BBLM (22) vs Fredholm K^N, and the interior/exterior first-order check.
- `platt_head.py`: decodes ≤50 zeros from a byte-range head, checks the header, θ/π + 1, and Z(t) sign changes.
- `heights.py`: the B4 table.

**Not opened (UNVERIFIED):**
- the BBLM journal version (and so its eq. (28) and appendix);
- BK PRL 77 (1996) 1472 full text;
- BK Nonlinearity 8 and 9 full texts (abstracts only);
- Bogomolny's Varenna 2000 lectures;
- Platt 2017 full text (abstract only; the AMS lists a bronze-OA PDF that was not fetched);
- the Zenodo data of arXiv:2512.09960.
