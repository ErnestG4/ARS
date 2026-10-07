# Phase 2 primary sources: BBLM N_eff, Bogomolny–Keating pair correlation, finite-N CUE spacing

Agent report, 2026-10-07. Not yet reviewed. All formulas below are quoted from the source named
beside them (arXiv LaTeX source or PDF that was actually opened). Equation and page numbers refer to the
**arXiv version stated**, not the journal pagination, unless said otherwise. Downloads are in
`~/specarith_lit_cache/ph2/` (outside the repo; sha256 values are in the Appendix). No zeta-zero data were
touched. Two small checks were run: a prime sum for Λ and Q, and sine-kernel / CUE_N determinants. They are
labelled **[agent check]**, are not source material, and their scripts are listed in the Appendix.

Access-status key: PRIMARY-READ = full text opened (arXiv version named). SECONDARY-READ = only a citing
source or an abstract was opened. UNVERIFIED = could not be opened.

---

## 0. Verdict on the brief's statements

| Brief statement | Verdict |
|---|---|
| "N_eff = log(E/2π)/√(12Λ)" | **CONFIRMED** verbatim (BBLM arXiv v1 eq. (19)). Equivalent form: N_eff = πρ̄/√(3Λ), with ρ̄ = (1/2π)log(E/2π). |
| "Λ ≈ 1.5731" | **CONFIRMED to the 4 decimals quoted.** BBLM print "Λ = 1.57314…", but that **5th decimal is wrong**. The correct value is **Λ = 1.5731510713…** (BFM 2017 give 1.57315 10713 24955…, Nishigaki 2025 gives 1.573151071…, and [agent check] gives 1.5731510713261). The effect on N_eff is a relative 3.5×10⁻⁶, which is negligible. Quote it as Λ = 1.573151… and not as "1.57314". |
| "spacing distribution … matches CUE with effective size N_eff" | **CONFIRMED, with two conditions.** (i) What is *derived* is a match of the **two-point function at O(ρ̄⁻²)**. That the nearest-neighbour spacing matches is an **extra conjecture**: the correction is assumed to be a change of kernel only. (ii) The spacing prediction also uses a rescaling **s → αs** of the correction term, with α = 1 + C/log(E/2π) and C = Q/Λ. N_eff alone gives the O(N⁻²) term. α is needed to handle the O(N⁻³) term. |
| "BK (1995–96) derived zero correlations, including the lower-order corrections, from the Hardy–Littlewood prime-pair conjecture" | **PARTLY WRONG.** The 1995 and 1996 *Nonlinearity* papers (I: 3- and 4-point; II: n-point) show that the correlations are **asymptotically** equal to GUE. Their abstracts say "asymptotically equivalent", and BK 2013b describes them as using a *smoothed* HL conjecture. The formula **with lower-order terms** is the two-point function of **Bogomolny–Keating, PRL 77 (1996) 1472**. That paper was not readable here. The derivation of the formula from the full HL conjecture is given explicitly in Bogomolny's Les Houches lectures (nlin/0312061, eq. (57)), which were read. |

---

## 1. Bogomolny, Bohigas, Leboeuf, Monastra (2006) — "BBLM"

- **Citation.** E. Bogomolny, O. Bohigas, P. Leboeuf, A. G. Monastra, "On the spacing distribution of the
  Riemann zeros: corrections to the asymptotic result", *J. Phys. A: Math. Gen.* **39** (2006) 10743–10754,
  DOI 10.1088/0305-4470/39/34/010; arXiv:math/0602270 (**v1 only**, 13 Feb 2006).
- **URLs accessed.** https://arxiv.org/pdf/math/0602270, https://arxiv.org/e-print/math/0602270 (LaTeX
  `bblm.tex`), https://export.arxiv.org/abs/math/0602270, Crossref metadata.
- **Access status.** **PRIMARY-READ (arXiv v1, 9 pp.)**. The **journal version is UNVERIFIED**: IOP
  returned an error or captcha, and HAL hal-00118511 links to arXiv only. **The journal version is longer
  than arXiv v1**: it has 12 pages against 9, it has an appendix, and it has at least 28 equations.
  BFM 2017 cite "[BBLM06, Eq. (28)]", "the appendix of [BBLM06]" and "[BBLM06, p. 10748]", none of which
  are in arXiv v1 (v1 ends at eq. (24) and has no appendix). The journal abstract on IOP seems to call the
  constant **β** ("β = 1.573 14…", as summarised by a fetch tool, not verified). Bogomolny 2007 also uses β
  for it (see §1.8).

### 1.1 Effective size and Λ (arXiv v1, p. 5)
Quoted from the source (eq. (19)):

> "To leading order in 1/ρ̄ the two–point correlation function of the Riemann zeros coincides with that of
> eigenvalues of random CUE_N matrices of effective dimension N = N_eff, where
> **N_eff = πρ̄/√(3Λ) = (1/√(12Λ)) log(E/2π)**, (19)
> where **Λ ≡ γ₀² + 2γ₁ + c₀ = 1.57314…**"

and (p. 5): "N_eff = (12Λ)^{-1/2} N₀ = 0.230158 N₀", with N₀ = log(E/2π) (eq. (2), p. 2; it equates the
zero density to the CUE_N eigenvalue density, following Keating–Snaith).

**Definition of the pieces** (p. 4; these displays are unnumbered):
- γ_n are the Stieltjes constants, from ζ(1+x) = 1/x + Σ_{n≥0} ((−1)ⁿ/n!) γ_n xⁿ. So γ₀ is the Euler
  constant.
- c_n = ((−1)ⁿ/(2n)!) Σ_p (log p)^{2(n+1)} Σ_{r≥1} (r−1) r^{2n} / p^r. In particular
  **c₀ = Σ_p log²p Σ_r (r−1)p^{−r} = Σ_p log²p/(p−1)²**. The closed form is written out by BFM 2017
  (§4.1) and by Bogomolny 2007 eq. (7.11).
- **Q = Σ_p log³p/(p−1)²** (p. 4). **C = Q/(γ₀²+2γ₁+c₀) = 1.4720…** (p. 5).

**Numerical values, with sources:**

| Constant | BBLM v1 | BFM 2017 (arXiv v4, p. 14) | Nishigaki 2025 (p. 12) | [agent check] |
|---|---|---|---|---|
| Λ | 1.57314… | **1.57315 10713 24955…** | 1.573151071… | 1.5731510713261 |
| Q | (not given) | 2.31584 63849 58803… | 2.315846384… | 2.3158463850 |
| C = Q/Λ | 1.4720… | (not given) | (not given) | 1.4721068 |
| (12Λ)^{−1/2} | 0.230158 | (not given) | (not given) | 0.2301570 (0.2301578 with Λ = 1.57314) |

Both BBLM digits strings come out slightly low: "1.57314" should be 1.57315…, and "1.4720" should be
1.4721…. BBLM's 0.230158 is consistent with the low Λ. Bogomolny 2007 repeats the low values ("≈ 1.57314",
"δ ≈ 2.3157", eq. (7.11)). BFM obtained their digits by Euler–Maclaurin for γ_n and "the method of
[Ma09, p. 2]" for the prime sums (footnote, p. 14). [agent check] Λ = γ₀² + 2γ₁ + c₀ with
γ₀² + 2γ₁ = 0.18754623284 (mpmath) and c₀ = 1.3856048385. The prime sum was taken exactly to 2×10⁸ and the
tail was estimated as ∫ f(x)/log x dx; the tail is 1.0×10⁻⁷ for c₀ and 2.0×10⁻⁶ for Q. This agrees with BFM
to about 10⁻¹² (Λ) and 3×10⁻¹¹ (Q).

### 1.2 What is matched: the two-point function (arXiv v1, pp. 3–5)
CUE_N side (eq. (4) p. 3, eq. (7) p. 3, eq. (8) p. 3):
> K(x,y) = sin(π(x−y)) / (N sin(π(x−y)/N)) = K₀(x−y) + N⁻² K₁(x−y) + O(N⁻⁴), with K₀(s) = sin(πs)/(πs),
> K₁(s) = (πs/6) sin(πs) (eqs. (4)–(6)).
> R₂^{(CUE_N)}(s) = 1 − (sin(πs)/(N sin(πs/N)))² (7)
> = 1 − sin²(πs)/(π²s²) − (1/(3N²)) sin²(πs) − ((πs)²/N⁴) sin²(πs) + O(N⁻⁶). (8)

Zeros side, expanded from the BK formula (eq. (16) p. 5):
> **R₂(s) = 1 − sin²(πs)/(π²s²) − ((γ₀² + 2γ₁ + c₀)/(π²ρ̄²)) sin²(πs) − (Q/(2π²ρ̄³)) s sin(2πs) + O(ρ̄⁻⁴)** (16)

with ρ̄ = (1/2π) log(E/2π) (eq. (10) p. 4) and unfolding R₂(s) = ρ̄⁻² r₂(s/ρ̄) (eq. (13) p. 4).
Rescaled form (eqs. (17)–(18), p. 5):
> R₂(s) = 1 − sin²(πs)/(π²s²) − (Λ/(π²ρ̄²)) sin²(παs) + O(ρ̄⁻⁴), (17)
> α = 1 + Q/(2πρ̄ Λ) = 1 + C/log(E/2π). (18)

Equating the O(N⁻²) term of (8) with the O(ρ̄⁻²) term of (16) gives (19). **The matching is done on the
two-point function to O(ρ̄⁻²).** The O(ρ̄⁻³) term is absorbed by the rescaling s → αs (eq. (20)).

### 1.3 How the spacing prediction is built (arXiv v1, pp. 6–7)
- CUE_N spacing (eqs. (21)–(22), p. 6):
  > p^{(CUE_N)}(s) = d²E(s)/ds² (21),
  > **E(s) = det[ δ_jk − sin(πs(j−k)/N) / (π(j−k)) ], 1 ≤ j,k ≤ N** (22)
  >
  > The diagonal entries are understood as δ_jj − s/N. This is the N×N Toeplitz determinant for "no
  > eigenvalue in an arc of length 2πs/N".
- Expansion (eq. (23), p. 6): p^{(CUE_N)}(s) = p₀(s) + N⁻² p₁(s) + O(N⁻⁴). The text says: "The expansion
  (23) is difficult to derive analytically. We have therefore computed numerically … p₁(s) = N²[p^{(CUE_N)}(s)
  − p₀(s)] for increasing values of N." **So BBLM obtained p₁ by numerical extrapolation in N.** The
  values of N used are not stated in v1.
- Prediction (eq. (24), p. 7): **δp(s) = N_eff⁻² p₁(αs) + O(N_eff⁻⁴)**, where p(s) = p₀(s) + δp(s).
- The extra assumption (p. 6, citing Andreev–Altshuler and Nishigaki): "to leading order … deviations from
  standard random matrix theory … are reduced to a change of the kernel only … the correction term is the
  same as for CUE_N matrices with an effective matrix size." The conclusion (p. 8) names two conjectures:
  the BK two-point formula, and "to leading order deviations from random matrix predictions reduce to a
  change of the kernel".

The statistic is **p(s), the spacing between consecutive zeros**. BBLM call it the "nearest–neighbour
spacing distribution", which is the RMT usage. **Naming trap:** BFM 2017 and Nishigaki 2025 use "nearest
neighbour spacing" p_nn for **min(left gap, right gap)**, and call BBLM's statistic the "0-th next
neighbour spacing" p(0;s).

### 1.4 Data heights and the numbers BBLM report
- Fig. 1 and Fig. 2: "a billion zeros located in a window near **E = 2.5041178×10¹⁵**". The text on p. 2
  places this "around the 10¹⁶-th zero". Values: N₀ = 33.6188, **N_eff = 7.7376, α = 1.0438** (p. 7).
- Fig. 3: "one billion zeros located on a window around **E = 1.30664344×10²²**". Values: N₀ = 49.0864,
  **N_eff = 11.2976, α = 1.0300** (p. 7).
- **So the height is ≈1.3×10²² and the zero index is ≈10²³.** FM 2015 and BFM 2017 give the exact
  start: zero number 10²³ + 985,531,550 at E = 13066434408793621120027.3961465854. The data source cited
  is Odlyzko, "The 10²²-nd zero of the Riemann zeta function", Contemp. Math. 290 (2001) 139–144. In that
  title, "10²²-nd" refers to the **index** of the zero in an earlier data set. It is not this height.
- [agent check] With the true Λ: N_eff(2.5041178e15) = 7.73761 and N_eff(1.30664344e22) = 11.29759. Both
  agree with BBLM to the digits printed. α = 1.043788 and 1.029990.

### 1.5 Stated validity and remaining discrepancy (p. 7)
- At 2.5×10¹⁵: "The agreement is quite good … There is still some structure visible, which might be
  attributed to the O(N_eff⁻⁴) correction."
- At 1.3×10²²: "Now the agreement is clearly improved. The difference between the prediction (24) and the
  numerical results … shows a structureless remain."
- Without the α rescaling (dashed curve in Fig. 2) the fit is visibly worse.
- Fig. 1(b): plain N = N₀ gives the right shape of correction, but "its amplitude is clearly too small (by a
  factor of order 20)". This is consistent with (N₀/N_eff)² = 12Λ ≈ 18.9.
- No quantitative goodness-of-fit statistic is given. All comparisons are graphical.

### 1.6 Errata found in other sources
- **α versus ᾱ.** BFM 2017 (arXiv v4 p. 17, footnote to eq. (4.5)) say: "[BBLM06, Eq. (28)] contains a
  miscalculation by claiming that ᾱ would be the same as α."
  - If the O(N⁻³) term is put into the **kernel** ("interior rescaling"), the correction becomes
    (π(x−y)/6) sin(πᾱ(x−y)) with **ᾱ = 1 + Q/(πΛρ̄) = 1 + 2Q/(Λ log(E/2π)) = 2α − 1** (eq. (4.5)).
  - The α of eq. (18) applies only to the "exterior" rescaling of the R₂ correction term.
  - [agent check, algebra] Matching −2K₀μN⁻³ to the Q term of (16) gives μ(s) = η π²s² cos(πs)/6 with
    η = Q/(Λ√(3Λ)), and ᾱ − 1 = η/N_eff = 2(α − 1). **BFM are right.**
  - BBLM's own spacing recipe (24) applies α to p₁ directly ("exterior"). That is a heuristic. BFM report
    that for p(0;s) there is "no difference visible between interior and exterior rescaling" (p. 18,
    footnote).
- Bogomolny 2007 (§1.8) writes the kernel correction as k₁(ε) = (πε/(6N_eff²)) sin(παε) with the
  *exterior* α (eqs. (8.5)–(8.6)). That is the same factor-2 slip in print.

### 1.7 Bogomolny–Keating two-point formula as BBLM quote it (p. 4, eqs. (9), (11), (12))
See §2. BBLM's eqs. (11)–(12) agree with the Les Houches eq. (57) and with BK 2013 eqs. (50) and (58).

### 1.8 Bogomolny (2007), Prog. Theor. Phys. Suppl. 166, 19–44 (arXiv:0708.4223v1) — PRIMARY-READ
This is a restatement of BBLM with the constant called **β** (eqs. (7.10)–(7.11), p. 11):
> R₂(ε) = 1 − sin²(πε)/(π²ε²) − (β/(π²d̄²)) sin²(πε) − (δ/(2π²d̄³)) ε sin(2πε) + O(d̄⁻⁴), (7.10)
> β = γ₀² + 2γ₁ + Σ_p ln²p/(p−1)² ≈ 1.57314, δ = Σ_p ln³p/(p−1)² ≈ 2.3157. (7.11)

N_eff = πd̄(E)/√(3β) ≈ ln(E/2π)/√(12β) (eq. (8.6), p. 14). The same two heights are used, with the same
N_eff and α.

---

## 2. Bogomolny–Keating: pair correlation with arithmetic corrections

### 2.1 Sources and access
| Source | Status |
|---|---|
| E. B. Bogomolny, J. P. Keating, "Random matrix theory and the Riemann zeros I: three- and four-point correlations", *Nonlinearity* **8** (1995) 1115–1131, DOI 10.1088/0951-7715/8/6/013 | **SECONDARY-READ (abstract only**, via IOP page fetch). Abstract: "we demonstrate that the 3-point and 4-point zero correlation functions are **asymptotically** equivalent to the corresponding GUE results. Our method centres around a Hardy-Littlewood conjecture…" Not on arXiv. |
| E. B. Bogomolny, J. P. Keating, "… II: n-point correlations", *Nonlinearity* **9** (1996) 911–935, DOI 10.1088/0951-7715/9/4/006 | **SECONDARY-READ (abstract only)**: "for all n the n-point correlation function of the zeros is equivalent to the corresponding GUE result **in the appropriate asymptotic limit**." Not on arXiv. |
| E. B. Bogomolny, J. P. Keating, "Gutzwiller's trace formula and spectral statistics: beyond the diagonal approximation", *PRL* **77** (1996) 1472–1475, DOI 10.1103/PhysRevLett.77.1472 | **UNVERIFIED** (paywalled). Only the abstract was read; it does not state the formula. This is the original source of the formula with lower-order terms, according to BBLM ref. [bk], BK 2013a,b, FM 2015 and BFM 2017. |
| E. Bogomolny, "Quantum and arithmetical chaos", Les Houches lectures 2003, arXiv:nlin/0312061v1 | **PRIMARY-READ** (cached at `~/specarith_lit_cache/nlin_0312061.pdf`). |
| E. Bogomolny, J. P. Keating, "A method for calculating spectral statistics based on random-matrix universality with an application to the three-point correlations of the Riemann zeros", *J. Phys. A* **46** (2013) 305203, arXiv:1307.6012v1 | **PRIMARY-READ** (LaTeX + PDF). |
| E. Bogomolny, J. P. Keating, "Two-point correlation function for Dirichlet L-functions", *J. Phys. A* **46** (2013) 095202 (journal ref from memory, **not verified**), arXiv:1307.6010v1 | **PRIMARY-READ** (LaTeX + PDF). |
| E. Bogomolny, "Spectral statistics and periodic orbits", Varenna 1999 proceedings (2000) pp. 333–369 | **UNVERIFIED** (not opened). Cited as holding the detailed HL derivation. |

**Who derived what, quoted from BK 2013b (arXiv:1307.6010v1, p. 1–2):**
> "In [Keating 1993] a smooth version of this conjecture was used to demonstrate that the two-point
> correlation function … in the universal limit coincides with … GUE … In [BK Nonlinearity 1995/96], using
> the same smoothed form of the Hardy-Littlewood conjecture, it was shown that all correlation functions of
> the Riemann zeros agree with the corresponding GUE/CUE results. A more precise expression for the
> two-point correlation function … was obtained in [BK PRL 1996] using another method which is equivalent
> to the full Hardy-Littlewood conjecture (details of the calculations can be found in [Varenna])."

BK 2013a (1307.6012v1 p. 10) words it differently: "It was calculated in [BK PRL] by using the explicit form
of the Hardy-Littlewood conjecture concerning the distribution of prime pairs." BK 2013a also states that
the same formula follows from the ratios conjecture (Conrey–Snaith), and from their own RMT-universality
method.

### 2.2 The formula (quoted)
**Les Houches, nlin/0312061v1, §2.2, eq. (57), p. 61, restated in the Summary on p. 62:**
> R₂(ε) = d̄²(E) + R₂^{(diag)}(ε) + R₂^{(off)}(ε),
> R₂^{(diag)}(ε) = −(1/4π²) ∂²/∂ε² ln[ |ζ(1+iε)|² Φ^{(diag)}(ε) ],
> **R₂^{(off)}(ε) = (1/4π²) |ζ(1+iε)|² e^{2πi d̄ ε} Φ^{(off)}(ε) + c.c.** (57)
> Φ^{(diag)}(ε) = exp( 2 Σ_p Σ_{m≥1} ((1−m)/(m² p^m)) cos(mε ln p) ),
> **Φ^{(off)}(ε) = Π_p ( 1 − (1 − p^{iε})² / (p−1)² )**, Φ^{(off)}(0) = 1,
> with 2πd̄ = ln(E/2π).

Unfolding is R₂^{(unfolded)}(ε) = d̄⁻² R₂(ε/d̄) (p. 62). The HL input (eqs. (54)–(55), pp. 58–60) is
α(r) = C₂ Π_{p|r, p>2} (p−1)/(p−2) for even r, with **C₂ = 2Π_{p>2}(1 − 1/(p−1)²) ≈ 1.32032**.
**Typo in the source:** p. 58 says "for even r α(r)=0 and for odd r it can be represented as…". This is
reversed. The Summary on p. 62 correctly says "with even r".

**The same formula appears in:**
- BBLM eqs. (9), (11) and (12) (arXiv v1 p. 4). The diagonal part is written as
  −(1/4π²)∂²_ε[log|ζ(1+iε)|² + 2Σ_pΣ_{r≥1} ((1−r)/(r²p^r)) cos(εr log p)].
- BK 2013a (1307.6012v1) eq. (50), p. 12, with the diagonal part in closed form:
  > R₂^{diag}(ε) = −(1/4π²)∂²_ε ln|ζ(1+iε)|² − (1/4π²) Σ_p ln²p [ 1/(p^{1+iε}−1)² + 1/(p^{1−iε}−1)² ] (50)
  
  and eq. (58), p. 13: R₂^{osc}(ε) = (1/4π²) e^{2πi d̄(E) ε} |ζ(1+iε)|² Π_p(1 − (1−p^{iε})²/(p−1)²) + c.c.
  [agent check, algebra] The two diagonal forms are identical, because Σ_{r≥2}(r−1)x^r = x²/(1−x)².
  **Sign-convention caution:** BK 2013a eq. (43) writes the connected part as R₂^c ≡ +⟨⟨K²⟩⟩ while
  eq. (40) subtracts it. The final formulas (50) and (58) are the same as the others.
- BK 2013b (1307.6010v1) eqs. (1)–(6), pp. 1–3: the same formula, with d̄(E) = (1/2π)ln(E/2π) and the
  definition R₂(ε) = ⟨d(E−ε/2) d(E+ε/2)⟩ (eq. (3)). It adds: "The assumed (optimistic) precision of these
  formulas is O(E^{−1/2}) and they agree very well with numerical calculations of Odlyzko."

### 2.3 Leading lower-order corrections, stated explicitly
Source: BBLM eq. (16) (arXiv v1 p. 5). The same expression is BFM 2017 eq. (4.1) and FM 2015 eq. (2.3).
With L ≡ log(E/2π) and ρ̄ = L/(2π):

> R₂(s) = 1 − sin²(πs)/(π²s²) − (Λ/(π²ρ̄²)) sin²(πs) − (Q/(2π²ρ̄³)) s sin(2πs) + O(ρ̄⁻⁴)

The O(1/L²) term is −(Λ/(π²ρ̄²)) sin²(πs) = **−(4Λ/L²) sin²(πs)**. The O(1/L³) term is
−(Q/(2π²ρ̄³)) s sin(2πs) = **−(4πQ/L³) s sin(2πs)**. The conversion to L is arithmetic done here
[agent check]. Λ = γ₀² + 2γ₁ + Σ_p log²p/(p−1)² and Q = Σ_p log³p/(p−1)².

Intermediate expansions behind it (BBLM p. 4, eqs. (14)–(15)):
- r₂^{diag}(ε) = −1/(2π²ε²) − Λ/(2π²) + O(ε²)
- r₂^{off}(ε) = (1/4π²)[1/ε² + Λ + iQε + O(ε²)] e^{2πiρ̄ε} + c.c.

They use Φ^{off}(ε) = 1 + c₀ε² + iQε³ + O(ε⁴). [agent check] Re-assembling (14)+(15) under eq. (13)
reproduces (16).

**Range of validity (FM 2015, arXiv v3, p. 6):** the expanded form (2.4) (the α-rescaled form) agrees with
Odlyzko's R₂ data "for distances up to approximately one and a half times the average spacing … as the
distances increase, there is a systematic discrepancy". The **full** BK formula (not expanded), by
contrast, matches "for all distances displayed" (Les Houches Figs. 12–17 and Bogomolny 2007 Figs. 3–5:
2×10⁸ zeros near the 10²³-rd zero, residual histogram consistent with statistical noise). **For the
two-point function, a replication should use the full BK formula and not its 1/L expansion beyond s ≈ 1.5.**

---

## 3. Later numerical tests of the BBLM N_eff prediction

| Work | Status | Heights | Statistic | Key numbers / result |
|---|---|---|---|---|
| **BBLM 2006** (above) | PRIMARY-READ (arXiv v1) | E = 2.5041178×10¹⁵ and 1.30664344×10²², 10⁹ zeros each | consecutive spacing p(s), with exterior α | N_eff = 7.7376 and 11.2976; α = 1.0438 and 1.0300. Structure remains at 10¹⁵; "structureless remain" at 10²². Graphical only. |
| **P. J. Forrester, A. Mays**, "Finite size corrections in random matrix theory and Odlyzko's data set for the Riemann zeros", *Proc. R. Soc. A* **471** (2015) 20150436; arXiv:1506.06531**v3** | PRIMARY-READ (LaTeX + PDF) | one height: zero number 10²³ + 985,531,550, E = 1.30664344×10²² (p. 3) | R₂ (Fig. 2), p(0;s) with thinning ξ = 1 and 0.6 (Figs. 9–10) | p₁ characterised by a σ-PV/linear ODE (Prop. 3.1; eqs. (3.14)–(3.18), pp. 10–11), checked against extrapolation over **20 values of N between 100 and 138**. "accurate agreement with the Riemann zero data both for ξ = 1 and … ξ = 0.6, for all displayed values of s", using (2.5) N = log(E/2π)/√(12Λ) and (2.6) s ↦ αs. R₂ in expanded form agrees only up to about 1.5 mean spacings. **Caution:** their eq. (1.1) states ρ̄ = (1/2π)log(E/(2πe)) + O(log E/E). That is N̄(E)/E, not dN̄/dE = (1/2π)log(E/2π). Their §2 says the BBLM expansion uses "the leading term in (1.1)", and the Fig. 9 caption says zeros are "scaled by the leading term in (1.1)". The text cannot settle which density they actually unfolded with. |
| **F. Bornemann, P. J. Forrester, A. Mays**, "Finite size effects for spacing distributions in random matrix theory: circular ensembles and Riemann zeros", *Stud. Appl. Math.* **138** (2017) 401–437; arXiv:1608.04638**v4** | PRIMARY-READ (LaTeX + PDF) | one height, 1,041,719,075 zeros from index 10²³ + 985,531,550 (p. 17) | p(1;s) (next-but-one), minimum distance from a random origin, p_nn = min(left, right); ξ = 1 and 0.6 | Precise values (p. 18): **ρ̄ = 7.81235 22019 1727…, N = 11.29759 09009 547…, α = 1.02999 00807 6719…, ᾱ = 1.05998 01615 3438…**. Introduces interior rescaling L → L_RZ (eqs. (4.3)–(4.6)). Shows "excellent agreement up to the leading correction term with (interior) rescaling". p(0;s) is not re-plotted because "no difference [is] visible between interior and exterior rescaling". Gives the Λ and Q digits quoted in §1.1. Sampling note (p. 6): N ≈ 10 and ≈10⁸·N zeros are needed to resolve O(N⁻⁴). |
| **S. M. Nishigaki**, "Distributions of consecutive level spacings of circular unitary ensemble and their ratio: finite-size corrections and Riemann ζ zeros", arXiv:2507.10193v1 (2025; PTEP template, journal ref not verified) | PRIMARY-READ (LaTeX + PDF) | **several heights**: 10⁸ zeros from n = 1.037×10¹¹ (LMFDB); ≈10⁹ from n = 1.305×10¹⁶ and 1.000×10²³ (Odlyzko). Mean gap ratio also at n = 10⁸, 10⁹, 10¹⁰ | joint law of two consecutive spacings; gap ratio r | **N_e = 5.13383486853, 7.73844996441, 11.2975909009** (p. 13). Kernel eq. (41), N_e eq. (42), Λ = 1.573151071…. Finds that the CUE_N gap-ratio correction is **O(N⁻⁴)**: the O(N⁻²) part cancels. For zeta zeros the gap-ratio deviation therefore scales as N_e⁻³. A fit over six heights gives **0.1896 N_e^{−3.081}** for the mean of r̃ = min(r, 1/r) (Fig. 6), with sine-kernel E[r̃] = 0.5997504209…. The joint consecutive-spacing law at 10²³ agrees with CUE_{N_e} at O(N_e⁻²). |
| **P. J. Forrester, B.-J. Shen**, "Finite size corrections in the bulk for circular β ensembles", arXiv:2505.09865**v2** (2025) | PRIMARY-READ (LaTeX + PDF) | no new zeta data | CUE spacing generating function | **Prop. 2.1, eq. (2.8), p. 7:** 𝒫₁(s;ξ) = −(1/12) d²/ds² ( s² 𝒫₀(s;ξ) ). Equivalent form (2.9): ℰ₁ = −(1/12) s² ℰ₀''. Two-point analogue (2.7): ρ₍₂₎,₁ = −(1/12)(s²ρ₍₂₎,₀)''. The proof reduces it to an identity that is checked by computer algebra. Remark 2.1.2 links this to the Riemann-zero correction plots (FM15 Fig. 10). |
| Bogomolny 2007, PTPS 166 | PRIMARY-READ | the same two heights as BBLM | p(s) | No new heights. A restatement of BBLM. |

**Not found:** a published test of the N_eff **spacing** correction p₁ at more than two heights. BBLM used
two heights; FM15 and BFM17 used one. The only multi-height test found (Nishigaki 2025) is of the gap
ratio, where the O(N_e⁻²) term vanishes, so it tests the N⁻³ (ᾱ) structure rather than N_eff at O(N⁻²).
"Bornemann's finite-size work" (BFM17 above) covers the CUE side and the 10²³ data only.

---

## 4. Computing the CUE(N) spacing distribution exactly at finite N

**Convention used throughout:** eigen-angles θ are unfolded as x = Nθ/(2π), so the mean spacing is 1
(FM15 p. 5, BFM17 §3.1). p(0;s) is the consecutive spacing.

**(a) Exact at integer N: an N×N Toeplitz determinant (BBLM eqs. (21)–(22), p. 6).**
- E_N(0;s) = det[δ_jk − sin(πs(j−k)/N)/(π(j−k))]_{j,k=1..N}, with diagonal entries 1 − s/N.
- p_N(0;s) = E_N''(s).

**(b) Exact at integer N: a Fredholm determinant with the finite-N kernel (BFM17 eqs. (1.7)–(1.8), p. 3;
FM15 eq. (3.11)).**
- p^{U(N)}(0;s) = d²/ds² det(I − K_s^N), where K^N(x,y) = sin π(x−y) / (N sin(π(x−y)/N)) on (0,s).
- Generating function for all k: E^{CUE}(s;z) = det(I − z K_s^N) (BFM17 eq. (3.7)), and
  p(s;z) = z⁻² d²/ds² E(s;z) (eq. (3.3)). Equivalently
  p(n;s) = d²/ds² Σ_{j≤n}(n−j+1) E(j;s) (eq. (3.4)), and
  E(k;s) = ((−1)^k/k!) ∂_z^k det(I − zK)|_{z=1} (Bornemann 2010 review eq. (4.19), sine-kernel case).
- [agent check] (a) and (b) agree to about 10⁻¹⁵ at s = 1 for N = 8, 12 and 30.

**(c) Numerical method for (b), recommended: Bornemann's Nyström/Gauss–Legendre determinant.**
- Source: F. Bornemann, "On the numerical evaluation of Fredholm determinants", *Math. Comp.* **79** (2010)
  871–915, arXiv:0804.2543v2, PRIMARY-READ. Eq. (1.5), p. 3:
  > d_Q(z) = det( δ_ij + z w_i^{1/2} K(x_i,x_j) w_j^{1/2} )_{i,j=1}^m
- Convergence: Theorem 6.2 (p. 22) gives |d_Q(z) − d(z)| ≤ 4ρ^{−ν}/(1−ρ^{−1}) Φ(|z|(b−a)‖K‖_{L∞(E_ρ×E_ρ)})
  for analytic kernels. This is exponential in the number of quadrature nodes.
- Review: F. Bornemann, "On the numerical evaluation of distributions in random matrix theory: a review",
  *Markov Process. Related Fields* **16** (2010) 803–866, arXiv:0904.1581v5, PRIMARY-READ.
  - Eq. (1.2): E₂(0;s) = det(I − K_sin↾L²(0,s)).
  - Eq. (2.6): p_β(k;s) = d²/ds² Σ_{j=0}^k (k+1−j) E_β(j;s).
  - **Table 8, p. 48: p₂(0;s) has mean 1 and variance 0.17999 38776.** This is a known-answer check.
  - s-derivatives are taken by Chebyshev expansion, and z-derivatives by contour integration (BFM17 p. 8).

**(d) Leading correction p₁ = r₂(0;s), with no extrapolation in N.**
- Operator form (BFM17 eqs. (1.10)–(1.13), p. 4):
  > K^N = K + N⁻² L + O(N⁻⁴), L(x,y) = (π(x−y)/6) sin π(x−y)
  > det(I − K_s^N) = det(I − K_s) + N⁻² Ω + O(N⁻⁴), Ω = −det(I − K_s) tr((I − K_s)⁻¹ L_s)
  > **r₂(0;s) = d²/ds² Ω**
- Closed form (Forrester–Shen 2025 Prop. 2.1, eq. (2.8)): **p₁(s) = −(1/12) d²/ds² (s² p₀(s))**.
  Equivalently E₁(s) = −(1/12) s² E₀''(s).
- Painlevé alternative (FM15 Prop. 3.1, eqs. (3.3)–(3.5), (3.15)–(3.18)):
  - ℰ₀ = exp ∫₀^{πs} σ⁽⁰⁾(t)/t dt, where σ⁽⁰⁾ solves the σ-PV equation
    (tσ'')² + 4(tσ'−σ)(tσ'−σ+σ'²) = 0 with σ⁽⁰⁾ ~ −(ξ/π)t − (ξ²/π²)t².
  - σ⁽¹⁾ solves a linear second-order ODE with σ⁽¹⁾ ~ −(t⁴ξ²/(9π²) + t⁵ 5ξ³/(36π³)).
  - The finite-N τ-function (FM15 eqs. (3.12)–(3.13)) is σ̃PVI with v₁ = v₂ = v₃ = 0, v₄ = N.
  - FM15 warn that a generic ODE solver applied to σ-PV for ξ < 1 "diverges to a spurious pole". They used
    a nested power-series method.

**Known-answer anchors** (BFM17 Appendix, p. 28–29, Matlab output quoted):
- det(I − K_s) at s = 1 = **0.170217421379185**
- Ω at s = 1 = **−0.075241982465122**

In the Matlab code `sinc(pi*(x-y))` must mean sin(π(x−y))/(π(x−y)), which is the toolbox convention. The
number confirms this. [agent check] Gauss–Legendre Nyström with m = 40 reproduces both values to 15 digits.
−12Ω(1) = 0.90290379 equals p₀(1) from finite differences (0.90290348, with h² error). That is a
consistency check of the Forrester–Shen relation against the BFM operator formula.

**Recommendation for the replication.**
1. p₀: compute it by (c).
2. p₁: compute it **both** from Forrester–Shen (2.8) and from the BFM Ω formula, and check that the two
   agree. Doing this replaces BBLM's extrapolation in N.
3. Finite-N CUE: use (a) or (b) directly at integer N. CUE_N is not defined at non-integer N.
4. The prediction at height E: use p₀(s) + N_eff⁻² p₁(αs). Or, following BFM, use the interior rescaling
   L → L_RZ with ᾱ = 2α − 1. **The choice between α and ᾱ must be pinned before any data are read.**

---

## Open issues
1. **The journal version of BBLM is unread.** It has 12 pages against 9 in arXiv v1, and contains an
   appendix with a three-point check and an eq. (28) that BFM say is wrong. It may also change the
   constant's name to β and other wording. Getting it needs institutional access to J. Phys. A 39 10743.
2. **BK PRL 77 (1996) 1472 is unread**, so the exact form and conventions of the original two-point formula
   are known only from three restatements by the same authors (Les Houches 2003, BK 2013a, BK 2013b) and
   from BBLM. These all agree with one another. The Varenna 2000 lectures, which hold the HL derivation
   details, were not opened either.
3. **The Λ digits.** BBLM and Bogomolny 2007 print 1.57314. Three independent determinations give
   1.5731510713…, which is low by 1.1×10⁻⁵ relative to the printed value. C is printed as 1.4720 against
   1.47211 computed. Any pre-registration should cite BFM 2017 for the digits.
4. **α versus ᾱ.** The rescaling recipe is a heuristic at O(N⁻³). BBLM (arXiv v1 and Bogomolny 2007)
   use α in the spacing recipe. BFM show that the kernel-consistent value is ᾱ = 2α − 1, and that the
   choice is invisible for p(0;s) at 10²³. Phase 2 should pre-register one of them, or both as separate
   arms.
5. **Unfolding density.** BBLM, BFM, Nishigaki and BK use ρ̄ = (1/2π)log(E/2π). FM15 eq. (1.1) prints
   log(E/(2πe)). A 1/L mis-scaling (≈2% at 10²²) would be larger than the whole N_eff⁻² effect
   (≈0.8%), so the unfolding convention must be pinned and checked against ⟨s⟩ = 1.
6. **Multi-height tests of the O(N⁻²) spacing correction.** Only BBLM's two heights were found. Nishigaki's
   multi-height test is of the gap ratio, which is blind at O(N⁻²). A new multi-height test would be
   new work; the brief should not say one already exists.
7. **What BBLM extrapolated over is not stated.** BBLM do not give the range of N used to extrapolate p₁.
   FM15 used N = 100–138, 20 values. This does not matter if the closed form (Forrester–Shen) is used.
8. **Rigour status.** Forrester–Shen Prop. 2.1 is proved by reduction to an identity checked with computer
   algebra. BK's two-point formula is heuristic: it rests on the HL conjecture, or equally on the ratios
   conjecture. The extension from R₂ to all correlations, and so to p(s), is a further conjecture
   ("change of kernel only").
9. **Not checked:** journal references for Nishigaki 2025 and for BK 2013b (the J. Phys. A 46 095202
   above is from memory). The [Ma09] method BFM used for the prime sums was not opened.

---

## Appendix: provenance

**sha256 of the cached files read** (all under `~/specarith_lit_cache/`; not in the repo):
```
38baa479453564421afb5d2e51e2676e93b7d4c3b6173d3b956bc5482e33ccea  ph2/math_0602270.pdf      (BBLM arXiv v1)
52902e9b94e841cc700ae498180f645980d2ab8ec283dbbdd5068ac714a71dd1  ph2/src_0602270/bblm.tex  (BBLM v1 LaTeX)
030adc71bc55b35a2ebe8773f08f5932f7fa4c24a3d09e7b4e9da32401ddf750  nlin_0312061.pdf          (Les Houches v1)
6017dafbeb190f21a0a03bb1f04b05afe2909d9a84d5eca24de8c60e5c84960e  ph2/1307.6012.pdf         (BK 2013a v1)
bed4651db1ade0106596ef550eb991ed3816837df4de82c92da28371dd205e66  ph2/1307.6010.pdf         (BK 2013b v1)
900567ea40f28af5e8f5268840d4a96ce32382c08de5c235c64de4a4a6016fda  ph2/1506.06531v3.pdf      (FM 2015)
41cccd7a0ffb09955eba83651691338d3fad8daeb4e4aacc6c5dbb4b20fda66d  ph2/1608.04638v4.pdf      (BFM 2017)
360f9e7fae0c09b86c7cc62273c7bfba24e409cd44e6457258c5d1a492b1a512  ph2/2505.09865v2.pdf      (Forrester-Shen 2025)
d9d11a658a9c23d442450f6e367f4dc925bb639df95230ba45439ae4108e0222  ph2/2507.10193.pdf         (Nishigaki 2025 v1)
ab20ca02c4eed0d22f86927f707774d1a68b7d65a8bad01e08a42b1383e3d8bb  ph2/0708.4223.pdf          (Bogomolny 2007)
15e0102133a0d87466fbc86379d8f7add912c97f9b60f63007e0218604142770  ph2/0904.1581.pdf          (Bornemann review v5)
0652a97dcc57ec8727dbef4f60d14cb22c7b428b8551e3ecf67464803bde798a  ph2/0804.2543.pdf          (Bornemann Fredholm v2)
```
LaTeX sources were extracted next to them (`src_0602270/`, `src_bk2013/`, `src_fm15/`, `src_bfm17/`,
`src_2505/`, `src_2507/`).

**[agent check] scripts.** These are kept at `~/specarith_lit_cache/ph2/checks/` (outside the repo, not
committed). They use the venv python and no zeta-zero data.
- `lam2.py`: Λ and Q by a numpy sieve to 2×10⁸, plus a tail integral ∫_X^∞ f(x)/log x dx (mpmath, 25
  digits). γ₀ and γ₁ come from mpmath. Output: Λ = 1.573151071326132, Q = 2.315846384982841,
  C = 1.472106797, N_eff(1.30664344e22) = 11.29759090, α = 1.02999008.
- `kcheck.py`: a Gauss–Legendre Nyström (m = 40) check of the BFM17 Appendix values. It also compares the
  BBLM Toeplitz determinant (22) with the finite-N Fredholm determinant, and checks the Forrester–Shen
  relation at s = 1.

**URLs accessed:**
- arxiv.org/pdf and e-print for math/0602270, 1307.6012, 1307.6010, 1506.06531v3, 1608.04638v4,
  2505.09865v2, 2507.10193, 0708.4223, 0804.2543, 0904.1581
- export.arxiv.org abs and API pages
- api.crossref.org/works/10.1088/0305-4470/39/34/010
- journals.aps.org/prl/abstract/10.1103/PhysRevLett.77.1472 (abstract only)
- iopscience.iop.org/article/10.1088/0951-7715/8/6/013 and 10.1088/0951-7715/9/4/006 (abstracts only)
- iopscience.iop.org/article/10.1088/0305-4470/39/34/010 (error page)
- api.archives-ouvertes.fr (HAL record hal-00118511: no file)
