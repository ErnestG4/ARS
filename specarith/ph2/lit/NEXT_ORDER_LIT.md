# Next-order (beyond O(N_eff⁻²)) corrections to the ζ-zero nearest-neighbour spacing: literature check

Agent report, 2026-10-07. Not yet reviewed. This is a literature task only. No zero data were touched and
nothing was computed numerically. Every statement below comes from the arXiv LaTeX source and/or PDF named
beside it, which were downloaded into
`/tmp/claude-1000/-home-combust-fmexplorer-criticality-tool/6a37af9b-2be6-47a4-9e3c-79e1e7734393/scratchpad/lit_next_order/`
(scratch, wiped on reboot; sha256 values are in §5). Equation numbers and page numbers are those of the
**arXiv version stated**, checked against text extracted from the PDF. Where a number was only counted from
the LaTeX source, this is said. Items marked **[agent remark]** are my own algebra or reasoning. They are not
source material and are labelled wherever they occur.

Status key: **PRIMARY-READ** means the relevant sections of the full text were opened. **ABSTRACT/SECONDARY**
means only an abstract, a search snippet or a citing paper was seen. **UNVERIFIED** means the item could not
be opened.

Conventions used throughout: ρ̄ = (1/2π) log(E/2π). N ≡ N_eff = log(E/2π)/√(12Λ) = πρ̄/√(3Λ), with
Λ = 1.5731510713… and Q = 2.3158463849… (BFM 2017 p. 14). Then **N⁻⁴ = 9Λ²/(π⁴ρ̄⁴)**, so an O(ρ̄⁻⁴) term and
an O(N⁻⁴) term are the same order. s is the spacing unfolded to unit mean.

---

## 1. Answer

**No.** None of the sources checked publishes a theory-fixed O(N_eff⁻⁴) (equivalently O(ρ̄⁻⁴)) term for
the nearest-neighbour spacing density p(0;s), or for the gap probability E(0;s), of the Riemann zeros.
No ζ-specific O(N⁻⁴) spacing curve has been computed numerically or compared with Odlyzko, Platt or LMFDB
zeros. Here is what does exist:

- **To O(N⁻³) the ζ spacing is theory-fixed** (no fitted parameters). It is conditional on the
  Bogomolny–Keating (BK) pair correlation and on BBLM's "kernel-change" conjecture. The source is BFM 2017
  eqs. (4.3)–(4.6): K_RZ = K + L_RZ N⁻² + O(N⁻⁴), with L_RZ(x,y) = π(x−y) sin(πᾱ(x−y))/6 and ᾱ = 2α−1. The
  remainder is explicitly O(N⁻⁴), and the O(N⁻⁴) kernel term is never written down.
- **For CUE_N alone**, the O(N⁻⁴) spacing term p₂ has **no published closed form or operator formula**.
  Forrester–Shen 2025 (arXiv 2505.09865v2, Remark 2.1.4) say that they "have yet to find evidence for a
  generalisation of (2.8)" at this order. They do publish its exact small-s power series (eq. (2.6), through
  s⁹). They also give a closed form for the CUE **two-point** O(N⁻⁴) term (eq. (2.20)). The exact finite-N
  characterisations (Toeplitz/Fredholm determinant, and the σPVI τ-function in FM 2015 eqs. (3.11)–(3.13)) let
  one compute the CUE p₂ numerically.
- **On the ζ side**, the ratios-conjecture n-point correlations of Conrey–Snaith 2008 (CNTP 2, 477; arXiv
  0803.2795, Theorem 9 and §5 for n ≤ 4), and the BK 2013 averaged-determinant recipe (arXiv 1307.6012,
  eqs. (25), (27), (28)), contain "all of the lower order terms" of every n-point function, with no free
  parameters. They are therefore the only routes to a ζ-specific p₂ that does not rest on a
  kernel hypothesis. **Nobody has carried out that computation.** Conrey–Snaith 2007 (§9) and 2008 (§1) both
  name it explicitly as a future or "anticipated application". The **pair correlation** is the only quantity
  written out with lower-order terms, and even its O(ρ̄⁻⁴) Taylor coefficient is not printed in any source
  read. Every source stops at "+O(ρ̄⁻⁴)": BBLM eq. (16), FM15 (2.3), BFM (4.1), Bogomolny 2007.
- The only published multi-height test that goes past N⁻² is **Nishigaki 2025** (arXiv 2507.10193; PTEP
  2026, 023A02). It concerns the **gap ratio**, not p(0;s). There the CUE O(N⁻²) term cancels, so the ζ
  deviation scales as N_e⁻³. The fit of the mean gap ratio over six heights is 0.1896·N_e^{−3.081}, which is
  fitted and not theory-fixed. The ζ coefficient function P⁽³⁾_RZ,r is not derived.

Rigour status: the CUE_N statements are theorems. One exception is FS25 Prop. 2.1, which is proved by
reduction to an identity checked with computer algebra. Everything ζ-specific beyond Montgomery and
Rudnick–Sarnak (leading order, restricted support) is conjectural or heuristic: BK uses the Hardy–Littlewood
conjecture, CS uses the ratios conjecture, and BBLM and BFM use the kernel-change hypothesis.

---

## 2. Per source

### 2.1 Forrester & Mays 2015 ("FM15")
- **Citation.** P. J. Forrester, A. Mays, "Finite-size corrections in random matrix theory and Odlyzko's
  dataset for the Riemann zeros", Proc. R. Soc. A 471 (2015) 20150436; arXiv:1506.06531 **v3** (LaTeX
  `ForresterMays2015_RZd.tex` and PDF). **PRIMARY-READ.**
- **Contains.**
  - Eq. (2.3), p. 5: the BBLM expansion of the ζ two-point function, which ends at "+O(1/ρ̄⁴)".
  - Eqs. (2.4)–(2.6): the α-rescaled form, N_eff, and s ↦ αs.
  - Eq. (3.11): the exact finite-N CUE spacing, p^N(0;s;ξ) = ξ⁻¹ d²/ds² det(I − ξK_s^N).
  - Eqs. (3.12)–(3.13), p. 9: the **exact finite-N τ-function**, det(I − ξK_s^N) = exp(−∫₀^{πs/N} U(cot φ;ξ)dφ),
    with U satisfying the σ̃PVI equation (3.13) and v₄ = N.
  - Eqs. (3.14)–(3.18) and Prop. 3.1: the O(N⁻²) term through a linear 2nd-order ODE for σ⁽¹⁾. The kernel
    expansion is quoted only "+O(1/N⁴)" (LaTeX line 345).
  - p. 19: the numerical check "for 20 values of N between 100 and 138 we extrapolate the limiting value …
    and the next-to-leading order correction".
- **Does not contain.** Any term beyond p₁, whether for ζ or for CUE. The conclusion (p. 20) claims only
  consistency with the hypothesis that the ζ corrections "coincide with the O(1/N²) correction terms for the
  corresponding quantities of the eigenvalues of random unitary matrices". There is no N⁻⁴ discussion.
- **Use for p₂.** The σPVI system (3.12)–(3.13) holds for every N. A large-N expansion carried to second
  order would characterise the CUE p₂, but FM15 do not do this.

### 2.2 Bornemann, Forrester & Mays 2017 ("BFM")
- **Citation.** F. Bornemann, P. J. Forrester, A. Mays, "Finite size effects for spacing distributions in
  random matrix theory: circular ensembles and Riemann zeros", Stud. Appl. Math. 138 (2017) 401–437
  (DOI 10.1111/sapm.12160); arXiv:1608.04638 **v4** (LaTeX `BFM_21Feb.tex` and PDF). **PRIMARY-READ.**
- **Contains.**
  - Eqs. (1.9)–(1.13), pp. 3–4: the CUE kernel expansion K^N = K + N⁻² L + O(N⁻⁴), with L = (π(x−y)/6) sin π(x−y).
    The determinant expansion det(I−K_s^N) = det(I−K_s) + N⁻² Ω(K_s):L_s + O(N⁻⁴) is given **to first order
    only**.
  - Lemma 2.1 (p. 6), the "folklore" lemma: first order in h only.
  - Prop. 2.1: p^CUE(s;z) = p₂(s;z) + N⁻² r₂(s;z) + O(N⁻⁴). (In BFM, p₂ and r₂ name the leading term and the
    first correction. They are not this report's p₂.)
  - Eq. (4.1), p. 13: the BBLM ζ R₂ expansion through ρ̄⁻³, "+O(ρ̄⁻⁴)".
  - §4.3, eqs. (4.3)–(4.6), pp. 16–17: interior rescaling, quoted. "K_RZ^N(x,y) = K(x,y) + L(x,y)N⁻² + M(x,y)N⁻³ +
    O(N⁻⁴)" (4.3); "μ(s) = η π²s² cos(πs)/6, η = Q/(Λ√(3Λ))"; L_RZ (4.4); "ᾱ = 1 + ηN⁻¹ = … = 2α−1" (4.5);
    "K_RZ^N(x,y) = K(x,y) + L_RZ(x,y)N⁻² + O(N⁻⁴)" (4.6). Footnote 5: "[BBLM06, Eq. (28)] contains a
    miscalculation by claiming that ᾱ would be the same as α." The authors' stated purpose is "to improve
    systematically the CUE_N fit … from O(N⁻³) to O(N⁻⁴)". In other words, the method gives the ζ spacing
    **to O(N⁻³) inclusive**, with the error at O(N⁻⁴).
  - p. 17: one height only (Odlyzko, 1,041,719,075 zeros from index 10²³ + 985,531,550; N = 11.2975909009…).
- **The sampling passage** (§1.2 "A note on sampling sizes of empirical data", p. 6), quoted:
  > "In this paper we discuss finite size effects up to an error O(N⁻⁴), with N in the Odlyzko data set of
  > Riemann zeros being effectively N ≈ 10. … pushing the sampling error to the same order of magnitude as the
  > remaining finite size error thus requires a sampling size of M = N⁸ ≈ 10⁸. This was actually the choice
  > for our simulations and is well matched by the Odlyzko data set of a little more than 10⁹ ≈ 10⁸·N zeros.
  > However, observing structure also in the O(N⁻⁴) remainder term would hence require to increase the
  > sampling size by at least two to four orders of magnitude."

  **Correction to the brief's paraphrase.** The ≈10⁸·N zeros at N ≈ 10 bring the *sampling error* down to the
  size of the O(N⁻⁴) remainder. *Resolving structure in* the O(N⁻⁴) term would need 10²–10⁴ times more data,
  which is about 10¹¹–10¹³ zeros at N ≈ 11. **[agent remark]** By the same M ∝ N⁸ logic (error ∝ M^{-1/2}
  set against N⁻⁴), at N_eff 2.3–5.1 the N⁻⁴ term is larger by a factor (11.3/N)⁴ ≈ 24–580 than at N = 11.3.
  This is why low heights can see it with far fewer zeros.
- **Does not contain.** Any O(N⁻⁴) kernel term for ζ, or any O(N⁻⁴) spacing term for CUE or for ζ. Remark 5.9
  (p. 27, COE/CSE) is the only "future study" remark, and it concerns Painlevé theory, not higher orders.

### 2.3 Forrester & Shen 2025 ("FS25"): the CUE O(N⁻⁴) spacing term
- **Citation.** P. J. Forrester, B.-J. Shen, "Finite size corrections in the bulk for circular β ensembles",
  arXiv:2505.09865 **v2** (LaTeX `BulkN.tex` and PDF). Published in **Forum Math. Sigma 14 (2026) e105**
  (Crossref metadata checked; the journal text itself was not read). **PRIMARY-READ (arXiv v2).**
- **Contains.**
  - (1.12)–(1.14): every bulk-scaled CUE n-point function and the gap generating function have asymptotic
    expansions in powers of 1/N² **to all orders**, which follows from the kernel being even in N.
  - **(1.15), p. 4:** the exact small-s expansion of 𝓔_N^CUE((0,2πs/N);ξ) with its **full N-dependence**,
    through O(s¹²). For example, the s⁶ coefficient is −(1−1/N²)(2−3/N²)ξ²π⁴/1350.
  - **(2.4)–(2.6), p. 7:** small-s series of 𝓟₀, 𝓟₁ and **𝓟₂** (the O(N⁻⁴) term of the spacing generating
    function; ξ = 1 gives p(0;s)):
    > 𝓟₂(s;ξ) = −π⁴s⁴/15 + π⁶s⁶/45 − π⁶ξs⁷/450 − 2π⁸s⁸/675 + 44π⁸ξs⁹/70875 + O(s¹⁰)  (2.6)
  - **Prop. 2.1, (2.8)–(2.9), p. 8:** 𝓟₁ = −(1/12) d²/ds² (s² 𝓟₀) and 𝓔₁ = −(1/12) s² 𝓔₀''. Proved through
    σ-PV, with the final identity "checked … with the help of computer algebra".
  - **Remark 2.1.4, p. 9**, quoted: "in relation to 𝓟^bulk_{2,β=2}(s;ξ) in (4.3b), we have yet to find
    evidence for a generalisation of (2.8) using as data the power series in (2.4) and (2.6)." For the
    two-point function they give
    > ρ^bulk_{(2),2,β=2}(s,0) = −((πs)²/60) d²/ds² ( s² ρ^bulk_{(2),0,β=2}(s,0) )  (2.20)

    and they add that this, "as a candidate for linking the O(N⁻⁴) term for the spacing generating function
    to its limiting form, … is incompatible with the ξ-dependent terms in (2.4) and (2.6)."
  - Appendix B: leading small-s coefficient of each ξ^k with exact N-dependence (B.1), and its N⁻⁴ part
    (R1w). They note that "if there were to be an analogue … at this order, the highest power derivative must
    be four."
  - §3.3: for β = 1 and 4 the structure function (a two-point quantity) has differential identities at both
    N⁻² and N⁻⁴ (X6). These are not spacing results.
  - §4 end (p. 25): for even β, writing out the N⁻⁴ two-point term explicitly "would be an arduous task".
- **Does not contain.** A closed, operator or Painlevé form of the CUE p₂(s). It has no ζ data. Its only ζ
  link is Remark 2.1.2 (O(N⁻²), FM15 Fig. 10).
- **[agent remark]** Expanding (2.20): ρ_{(2),2} = −(πs)² sin²(πs)/15. Together with (1.11) this means that
  K^N = K + N⁻²L + N⁻⁴L₂ + O(N⁻⁶) with L₂(x,y) = 7π³(x−y)³ sin π(x−y)/360, which follows from the series
  x/sin x = 1 + x²/6 + 7x⁴/360 + ….
  **BBLM arXiv v1 eq. (8) (p. 3) prints the R₂ N⁻⁴ term as −((πs)²/N⁴) sin²(πs). The factor 1/15 is missing.**
  This conflicts with FS25 (2.20). Whether the journal version corrects it is UNVERIFIED.

### 2.4 Nishigaki 2025
- **Citation.** S. M. Nishigaki, "Distributions of consecutive level spacings of circular unitary ensemble
  and their ratio: finite-size corrections and Riemann ζ zeros", arXiv:2507.10193 **v1** (LaTeX `DCLS_CUE.tex`
  and PDF). Published in **PTEP 2026(2) 023A02** (Crossref; journal text not read). **PRIMARY-READ (v1).**
- **Contains.**
  - §4.3: P_nn(t) (min of left and right neighbour) of CUE_N = P⁽⁰⁾ + N⁻²P⁽²⁾ + O(N⁻⁴), computed numerically
    from the Tracy–Widom PDE system.
  - §4.4: the CUE gap-ratio law has P⁽²⁾_r ≡ 0, so N⁴(P_r − P_r⁽⁰⁾) converges (Fig. 3). This "enables direct
    access to the next-to-leading correction P⁽⁴⁾_r(t), which captures the O(N⁻⁴) contribution of the kernel".
    The term is obtained numerically only.
  - §5.2: for ζ, P_RZ,r = P⁽⁰⁾_r + N_e⁻³ P⁽³⁾_RZ,r + O(N_e⁻⁴), as an anticipated form. Data are at three heights
    (Fig. 5). The mean gap ratio at six heights is fitted as **0.1896 N_e^{−3.081}** (Fig. 6). This is a fit;
    no theoretical P⁽³⁾_RZ,r curve is drawn. Footnote (§5.2) restates the BFM interior-rescaled K_RZ with
    "+O(N_e⁻⁴)".
- **Does not contain.** A ζ O(N⁻⁴) term, or a closed-form CUE O(N⁻⁴) term for any statistic.

### 2.5 L-functions ratios conjecture
**(a) Conrey, Farmer, Zirnbauer 2008 ("CFZ").** "Autocorrelation of ratios of L-functions", Commun. Number
Theory Phys. 2 (2008) 593–636 (Crossref); arXiv:0711.0718 **v3** (LaTeX `ratios2h.tex` and PDF).
**PRIMARY-READ.**
- **Contains.** The general recipe (§5.1). §5.2 "Moments of ratios of ζ(s)" gives the conjectured main terms
  for (1/T)∫ ∏ζ(s+α_k)∏ζ(1−s−α_ℓ)/∏ζ(s+γ_q)∏ζ(1−s+δ_r) dt with an arithmetic factor A_ζ (an Euler product, with
  no free parameters), valid up to O(T^{1/2+ε}). §7.2 gives a conjecture for the mean square of ζ'/ζ "which is
  more precise than the Goldston–Gonek–Montgomery formula, in that it contains some lower order terms".
- **Does not contain.** Any zero-correlation function with lower-order terms, or any spacing statistic. The
  source has a commented-out note "% Lower order terms in PC / % derivation of correlations from moments of
  ratios" (LaTeX ≈ line 2048), so this was left out.

**(b) Conrey & Snaith 2007 ("CS07").** "Applications of the L-functions ratios conjectures", Proc. London Math.
Soc. (3) **94** (2007) 594–646. Crossref gives vol. 94(3); the arXiv journal-ref says 93. arXiv:math/0509480
**v2** (LaTeX `new_ratiosI.tex` and PDF). **PRIMARY-READ.**
- **Contains.**
  - **Theorem 4.1 (§4 "Pair-correlation", p. 20)**: assuming Conjecture 2.1 (the ζ ratios conjecture), the
    full pair-correlation sum Σ_{γ,γ'≤T} f(γ−γ') with all arithmetic lower-order terms, error O(T^{1/2+ε}).
    The arithmetic functions are A(η) = ∏_p (1−p^{−1−η})(1−2/p+p^{−1−η})/(1−1/p)² and
    B(η) = Σ_p (log p/(p^{1+η}−1))². p. 21: "We believe that this formula, originally found by Bogomolny and
    Keating, is very accurate, indeed, down to a square root error term. It includes all of the lower order
    terms…".
  - **§9 Conclusion, p. 57**, quoted: "Precise evaluations of n-level correlations might be combined to obtain
    the secondary terms in the nearest neighbour spacing distribution for the zeros of the Riemann zeta
    function."
- **Does not contain.** The n ≥ 3 correlations, any spacing computation, or an explicit ρ̄-expansion of the
  pair correlation.

**(c) Conrey & Snaith 2008 ("CS08"), added because it is the n-point source.** "Correlations of eigenvalues
and Riemann zeros", Commun. Number Theory Phys. 2 (2008) 477–536 (Crossref); arXiv:0803.2795 **v1** (LaTeX
and PDF). **PRIMARY-READ.**
- **Contains.**
  - **Theorem 9 (p. 33)**: assuming the ratios conjecture (their Conjecture 1), the general **n-correlation**
    sum Σ_{γ₁≠…≠γ_n≤T} f(γ₁,…,γ_n), with every lower-order term, error O(T^{1/2+ε}).
  - §5 (pp. 34ff.): written out explicitly for **n = 2, 3, 4** for ζ (pair: J*_ζ,t(a;b) = (ζ'/ζ)'(1+a+b) − B(a+b)
    + e^{−ℓ(a+b)}ζ(1+a+b)ζ(1−a−b)A(a+b), with ℓ = log(t/2π); triple: Q(x,y), B₁; quadruple: A*, B₂, B₃, B₄).
  - §1, p. 2: "Assuming the ratios conjecture we prove a formula which explicitly gives all of the lower order
    terms in any order correlation." Also, §1, p. 3, quoted: "**An anticipated application of this current work is to the
    determination of the lower order terms in the nearest neighbor spacing for zeta-zeros.**"
- **Does not contain.** The spacing calculation itself, any 1/ρ̄ expansion, or any numerics.
- **Free parameters.** None. Every constant is a prime sum, an Euler product, or a value or derivative of ζ
  near 1.

**(d) Conrey & Snaith, "In support of n-correlation"**, Commun. Math. Phys. (2014); arXiv:1212.5537 v2
(LaTeX, abstract and introduction only). This paper is about leading-order n-correlation for test functions of
restricted support. It has no lower-order spacing content and is not relevant.

**(e) Conrey & Snaith, "Triple correlation of the Riemann zeros"**, J. Théor. Nombres Bordeaux (2008);
arXiv:math/0610495. **ABSTRACT/SECONDARY only.** Per search snippets, it gives all lower-order terms of the
triple correlation under the ratios conjecture. CS08 says that it extends this paper.

**Has anyone done the spacing computation from (b)/(c)?** None was found. I screened the Semantic Scholar
citation list of CS08 (43 entries, 2008–2026) by title only. No entry concerns the ζ nearest-neighbour
spacing with lower-order terms. FM15 is the only spacing paper among them, and it does not use CS08.

### 2.6 Bogomolny & Keating
- **BK I, Nonlinearity 8 (1995) 1115–1131** (3- and 4-point). **UNVERIFIED (not opened).** BK II (p. 4)
  describes it as computing R₃ and R₄ "explicitly and shown to coincide with the corresponding RMT formulae",
  which is a leading-order statement.
- **BK II, "Random matrix theory and the Riemann zeros II: n-point correlations", Nonlinearity 9 (1996) 911**
  (HP Labs tech report HPL-BRIMS-96-13, a scanned, OCR'd PDF). **PRIMARY-READ (tech-report version).** p. 4:
  "we calculate the leading order asymptotics as E→∞ of the general term"; §4 Comments, p. 24: "term-by-term
  asymptotically identical for all n … we have concentrated solely on the universal statistical regime. The
  nonuniversal correlations could easily be investigated …". **There are no lower-order terms.**
- **BK PRL 77 (1996) 1472–1475** (two-point function with lower-order terms). **UNVERIFIED.** The APS site
  served a bot challenge. The formula is reproduced in BBLM v1 eqs. (11)–(12), in CS07 Theorem 4.1 (which
  states that the two agree) and in BK 2013 eq. (50) and (58) (see lit/bblm_bk.md §2.2). It is a two-point
  result only.
- **BK 2013a, "A method for calculating spectral statistics based on random-matrix universality with an
  application to the three-point correlations of the Riemann zeros"**, J. Phys. A 46 (2013) 305203.
  **Note: the arXiv id is 1307.6012, not 1307.6010 as the brief has it.** arXiv v1 (LaTeX and PDF).
  **PRIMARY-READ.**
  - **Contains.** A general heuristic recipe for **all** n-point functions. Eq. (27), p. 9: kernel
    K(E_i,E_j) = sin(π(N̄(E_i,p*)−N̄(E_j,p*)))/(π(E_i−E_j)), where N̄ includes the oscillatory prime terms with
    p < p*. Eq. (28): R_n = ⟨⟨det K(E+e_i,E+e_j)⟩⟩_ΔE, averaged over the window, with prime phases treated as
    independent uniform phases. "Eq. (28) together with (27) and (25) are our main formulae … this assumption
    permits us to calculate all low order terms for correlation functions of Riemann zeros." The paper derives
    the two-point and three-point functions explicitly (§§5–6; summary in §7) and says that the result agrees
    with Conrey–Snaith's triple correlation.
  - **Does not contain.** The n ≥ 4 correlations, any spacing statistic, or any 1/ρ̄ expansion beyond what
    BBLM used.
  - **[agent remark]** Because E(0;s) = Σ_n ((−1)ⁿ/n!) ∫R_n and eq. (28) is linear in each R_n, the recipe
    formally gives E(0;s) = ⟨⟨det(I − K_{E,s})⟩⟩. That is a phase-average of Fredholm determinants with the
    p*-truncated kernel. BK do not state this, and the divergent-sum regularisation (their eq. (39),
    ∏_{p<p*}(1−p⁻¹)/(1−p^{−1−s}) → sζ(1+s), valid under 1 ≪ ln p* ≪ 1/|s|, eq. (36)) is done on averaged expressions. Whether it can be carried out
    inside a determinant is UNVERIFIED. This route would be heuristic and free of parameters, but **nobody has
    done it.**
- **BK 2013b, "Two-point correlation function for Dirichlet L-functions"**, J. Phys. A 46 (2013) 095202;
  arXiv:1307.6010 v1 (LaTeX and PDF). **PRIMARY-READ (abstract and scan).** It covers the two-point function
  only, and the finite-E corrections differ from ζ "by certain finite products of primes which divide the
  modulus". There is no spacing content. It is not relevant here.

### 2.7 BBLM 2006 and Bogomolny 2007 (re-checked only for next-order content)
- **BBLM**, J. Phys. A 39 (2006) 10743; arXiv:math/0602270 **v1** (LaTeX `bblm.tex` and PDF). **PRIMARY-READ
  (v1).** The journal version, which is longer and has an appendix, is **UNVERIFIED** (see lit/bblm_bk.md §1).
  - Eq. (16), p. 5: R₂ through ρ̄⁻³, "+O(ρ̄⁻⁴)".
  - Eq. (23): p^{CUE_N} = p₀ + N⁻²p₁ + O(N⁻⁴). The text says "The expansion (23) is difficult to derive
    analytically", so p₁ was done numerically from Toeplitz eqs. (21)–(22).
  - Conclusion, p. 7: the method rests on two conjectures, the BK two-point formula and "that to leading order
    deviations from random matrix predictions reduce to a change of the kernel".
  - It says nothing about O(N⁻⁴) for ζ. Eq. (8) has the coefficient problem noted in §2.3.
  - Per BFM p. 17, the journal appendix checks the kernel conjecture against the three-point function **at
    O(N⁻³)**. UNVERIFIED by me.
- **Bogomolny 2007**, "Riemann zeta function and quantum chaos", Prog. Theor. Phys. Suppl. 166 (2007) 19–44;
  arXiv:0708.4223 v1 (LaTeX). **PRIMARY-READ (§§7–8).** It restates BBLM.
  - §8, quoted: "There is still some structure visible which might be attributed to the O(N_eff⁻⁴)
    correction", at E = 2.504×10¹⁵ and N_eff = 7.7376. At 1.307×10²² the residual is "structureless". No
    formula is given.
  - **[agent remark, algebra]** Its kernel eq. (deltak), k₁ = (πε/6N²) sin(παε) with
    α = 1 + δ/(β ln(E/2π)), carries the same α-for-ᾱ slip that BFM footnote 5 flags in BBLM eq. (28).
    Matching the ε² cos(πε) coefficient requires ᾱ = 1 + 2δ/(β ln(E/2π)).
- **Bogomolny, Les Houches lectures "Quantum and arithmetical chaos"**, arXiv:nlin/0312061 v1 (LaTeX, searched
  only). It predates BBLM and has no finite-size spacing correction.

### 2.8 Search for 2015–2026 work beyond N⁻²
Method: arXiv API phrase searches; WebSearch and Exa queries; Semantic Scholar citation lists (retrieved
2026-10-07, screened by title) for BBLM (36 citing), FM15 (22), BFM17 (32), CS08 (43), BK13a (10),
Nishigaki 2025 (2) and FS25 (0 returned). **Google Scholar was not accessed (UNVERIFIED)**; Semantic Scholar
was used instead.

Results:
- No paper computes the ζ p(0;s) beyond N_eff⁻² or compares an O(N⁻⁴) ζ prediction with zeros.
- The papers that go furthest are FS25 (CUE p₂ small-s series, no closed form) and Nishigaki 2025 (CUE gap
  ratio at N⁻⁴, numerical; ζ gap ratio at N_e⁻³, fitted).
- **Zenodo record 19268721** (D. Alarcón, "Gap ratio statistics of Riemann zeros…", 2026-03-28, not
  peer-reviewed). **ABSTRACT/SECONDARY only** (WebFetch summary). It is reported to fit ⟨r⟩ = a + b/log²T with
  fitted coefficients, so it is not theory-fixed. It is also at odds with Nishigaki's N_e⁻³ scaling. It is
  not a candidate.
- Titles screened and judged irrelevant to spacing at next order: "Power spectra and autocovariances of level
  spacings beyond the Dyson conjecture" (2301.09441), "Power spectra of Dyson's circular ensembles"
  (2408.15571), and the Forrester-group edge-expansion papers (1903.08823, 1812.07750, 2008.13124,
  2205.05257). Also "On the Berry–Keating Operator" (2606.24405; abstract only, a review of H_BK). None was
  read in full; this is a title or abstract judgement only.

---

## 3. Candidate sources for a theory-fixed p₂ (none gives it ready-made)

| # | Source | Object it gives | What it would take to get p₂(s) | Free parameters | Status |
|---|---|---|---|---|---|
| 1 | **CUE_N exact finite-N**: Toeplitz det (BBLM v1 eqs. (21)–(22)); Fredholm det(I−K_s^N) (FM15 (3.11), BFM (1.7)); σPVI τ-function (FM15 (3.12)–(3.13)) | the CUE_N spacing for any N, exactly | Numerical: Richardson-extrapolate N⁴[p^N − p₀ − N⁻²p₁] over N, or expand the σPVI system to second order. Validate against FS25 (2.6) (small-s series of 𝓟₂ through s⁹) and FS25 (1.15). **Gives CUE's own p₂, not ζ's.** | none | theorem |
| 2 | **CUE kernel to O(N⁻⁴)** [agent remark]: K^N = K + N⁻²L + N⁻⁴L₂, L₂ = 7π³(x−y)³ sin π(x−y)/360; second-order determinant expansion det(I−K−hL−h²L₂) = det(I−K)[1 − h tr(RL) + h²(½(tr RL)² − ½ tr(RLRL) − tr(RL₂))] + O(h³), R = (I−K_s)⁻¹, h = N⁻² | the CUE p₂ as an operator formula, p₂ = d²/ds² of the h² bracket times det(I−K_s) | Bornemann-type quadrature. Cross-check with row 1 and FS25 (2.6). **Not in any source read.** BFM Lemma 2.1 is first order only, so this is my extension of it and is unverified. | none | agent derivation |
| 3 | **CS08 Theorem 9 + §5** (ratios conjecture) | ζ n-point correlations with all lower-order terms, explicit for n ≤ 4 | Expand each R_n to O(ρ̄⁻⁴) in unfolded variables. Truncating the inclusion–exclusion series for E(0;s) needs all n (n ≤ 4 explicit; general n only as a contour-integral formula). This is a heavy analytic and numerical project. **Never done.** CS07 §9 and CS08 §1 name it as future work. | none (prime sums, Euler products, ζ near 1) | conditional on the ratios conjecture |
| 4 | **BK 2013a eqs. (25), (27), (28)** | heuristic recipe for all R_n (averaged determinant, random-phase prime kernel) | As in row 3, or formally ⟨⟨det(I−K)⟩⟩ (agent remark, §2.6). The regularisation inside a determinant is unverified. **Never done.** | none | heuristic (HL / universality) |
| 5 | **Kernel hypothesis extended to O(N⁻⁴)** (BBLM / BFM logic carried one order further) [agent remark] | if the ζ correlations stay determinantal with a translation-invariant even kernel to O(N⁻⁴), then K_RZ(s) = ±√(1 − R₂(s)) is fixed by the BK/CS07 pair correlation expanded to O(ρ̄⁻⁴), and p₂^RZ follows from row 2's operator formula with L→L_RZ and L₂→ the (parameter-free) O(N⁻⁴) kernel so determined | (i) the O(ρ̄⁻⁴) coefficient of R₂, which no source read prints (all stop at "+O(ρ̄⁻⁴)") but which follows by Taylor expansion of BBLM (11)–(12) / CS07 Thm 4.1 (it involves γ₀…γ₃, c₁ and the ε⁴ coefficient of the Euler product); (ii) the operator formula. **The hypothesis is untested at O(N⁻⁴).** BBLM checked it only against R₃ at O(N⁻³). In BK13 the n-point functions are averages of determinants, and at second order an average of products need not equal the product of averages. Theory-fixed if the hypothesis holds. | none | conjecture beyond published support |

A remark on rows 1 and 2 versus 3–5. A "CUE_{N_eff} p₂" (rows 1 and 2, with N = N_eff) is **not** the ζ
O(ρ̄⁻⁴) term. Already at O(N⁻²) the ζ and CUE coefficients match only through the choice of N_eff. At O(N⁻³)
ζ has a term that CUE lacks (the Q term, handled by ᾱ). At O(N⁻⁴) the ζ pair-correlation coefficient
involves new arithmetic constants (higher Stieltjes constants, c₁, …). There is no reason for these to
reproduce the CUE value −(πs)² sin²(πs)/15 at N = N_eff **[agent remark]**. So "BFM + CUE p₂ at N_eff" is one
specific, parameter-free model. It is not *the* ζ prediction.

---

## 4. Discrepancies and corrections found

1. The brief cites BK 2013 "three-point" as arXiv 1307.6010. **It is arXiv:1307.6012.** 1307.6010 is the
   Dirichlet two-point paper.
2. The brief's BFM paraphrase. ≈10⁸·N zeros at N ≈ 10 bring the *sampling error* down to the O(N⁻⁴)
   *remainder*. *Seeing structure* in the O(N⁻⁴) term needs "at least two to four orders of magnitude" more
   data (BFM §1.2, p. 6).
3. BBLM arXiv v1 eq. (8): the CUE R₂ term at N⁻⁴ is printed as −(πs)²sin²(πs)/N⁴. FS25 (2.20), and the
   x/sin x series, give −(πs)²sin²(πs)/(15N⁴) [agent check]. Journal version UNVERIFIED.
4. Bogomolny 2007 §8 repeats the α-for-ᾱ slip that BFM footnote 5 flags in BBLM (28) [agent algebra].
5. CS07 volume: Crossref gives **94**(3) 594–646. The arXiv journal-ref says 93.
6. Journal versions newer than the brief: FS25 is in Forum Math. Sigma 14 (2026) e105, and Nishigaki 2025 is
   in PTEP 2026(2) 023A02 (Crossref). Neither journal text was read.

---

## 5. Files read (sha256)

All files are in `…/scratchpad/lit_next_order/`. A `src_*` file is the arXiv e-print (gzip or tar.gz). The
.tex rows are the files extracted from it. PDFs were read through pypdf text extraction, run in a scratch venv
with `python -I` from a separate scripts directory.

| File | Item | sha256 |
|---|---|---|
| 1506.06531.pdf | FM15 v3 | 900567ea40f28af5e8f5268840d4a96ce32382c08de5c235c64de4a4a6016fda |
| src_1506.06531 | FM15 v3 e-print | e93620f8f6556b43f257aaf8fb36725df5426f2a76520b4bf9282a2571c68f6b |
| x_fm15/ForresterMays2015_RZd.tex | FM15 LaTeX | 0542f62449938cfe7f8dca38cdc38c74ef8db7287a4b9faf286aaf7311812ea6 |
| 1608.04638.pdf | BFM v4 | 41cccd7a0ffb09955eba83651691338d3fad8daeb4e4aacc6c5dbb4b20fda66d |
| src_1608.04638 | BFM v4 e-print | 81581a95ccd3e1892583f2bd3164ae3b44b76bf6d17d11e4303fef41539dabd0 |
| x_bfm17/BFM_21Feb.tex | BFM LaTeX | 86d6b429816eb271e3882906e3c4eed2cf5149ee41933337a39d3584a61a26ee |
| 2505.09865.pdf | Forrester–Shen v2 | 360f9e7fae0c09b86c7cc62273c7bfba24e409cd44e6457258c5d1a492b1a512 |
| src_2505.09865 | FS25 v2 e-print | f08d5e499c664c7750c261e2361cc817ce6d73f3b0241cbe676c33b81fec0f16 |
| x_fs25/BulkN.tex | FS25 LaTeX | 3cf7340a86cee90e44ae085b1a1065d07309191e892416fba4dc49962d335821 |
| 2507.10193.pdf | Nishigaki v1 | d9d11a658a9c23d442450f6e367f4dc925bb639df95230ba45439ae4108e0222 |
| src_2507.10193 | Nishigaki e-print | 9ff431667de0228da3f4ad822d9b7cdd0bf6002e6533e3a202b7ba329c6ba64a |
| x_nish25/DCLS_CUE.tex | Nishigaki LaTeX | 4d967f936b75d719c49420494dc3df6825480be5238eca3ec69c67122c6826bb |
| 0711.0718.pdf | CFZ v3 | d65cf4b2791fbbbe0e4a6ed15b416a90fe4c93116ed273ee8717e8eadd9a6efc |
| src_0711.0718 | CFZ e-print | 334896a1d66f8323a5821d879b9632d3ea661227f9af23f1c582f5c73d5823b2 |
| cfz08.tex | CFZ LaTeX | a81ebe84d7b468ba7752960edf0a22f06ad9318934ff6e45f9b13377f8677cf0 |
| math_0509480.pdf | CS07 v2 | 2deeeb0ff78b51835f2e59f7fcf2c0a8343f4cc65ff1aeb611ac12268ff42ac3 |
| src_math_0509480 | CS07 e-print | 69222df52053d3b6a1e9ddbefa944eac0c6bcba9b94a30d7345be335d0616afc |
| cs07.tex | CS07 LaTeX | f1447009462754b556267867c6d6ec9495dc6f3759b3b7f885498ad1fa3e8487 |
| 0803.2795.pdf | CS08 v1 | 026111915ff8663daa9069f7cb556cbfc7f0f54038ff0e17031fbdafa098419c |
| src_0803.2795 | CS08 e-print | 4f6277574c51b24ef510611a55669af2ee09544f7330c3cc4d9ba47764fdacb3 |
| cs08_ncorr.tex | CS08 LaTeX | 2a883ed0dc102028eda3c52961b73140eb637ddb92b9f554eded96cd26ab3009 |
| src_1212.5537 | CS14 v2 e-print | f2909d4ad3db52db46b1641bab8afa25ec15d90c569bd2715e89ba159bf7625e |
| cs14_support.tex | CS14 LaTeX (intro only) | da3f01da00898a803ed9cf4ed8654d3f8664779ceaa2d268f587cf8e565d4340 |
| 1307.6012.pdf | BK 2013a v1 (3-pt) | 6017dafbeb190f21a0a03bb1f04b05afe2909d9a84d5eca24de8c60e5c84960e |
| src_1307.6012 | BK 2013a e-print | 7192ed09888bc72fd9372610d2dd580fdb24b7824422888f6525f3f31b80a1ff |
| bk13_3pt.tex | BK 2013a LaTeX | 4a526eaf49343380317f56fa96f413cc834469a0eee50d0cf22b290232ad522f |
| 1307.6010.pdf | BK 2013b v1 (Dirichlet) | bed4651db1ade0106596ef550eb991ed3816837df4de82c92da28371dd205e66 |
| src_1307.6010 | BK 2013b e-print | d0dc511ac105651b348a3c4cd06ba14751bb6128237c162c7a9e1d0e8eebe84e |
| bk13_dir.tex | BK 2013b LaTeX | e92a5a39dc162218ae483de15a30b3d49bfdcac4a0d9542d9b873b9602cdf1aa |
| bk96_nonlinII_hpl.pdf | BK II (HPL-BRIMS-96-13 scan) | 94c4285fe95d37a9af14b5cc1f2bbffd0a0551ae87cb339305a5c8a01df03a1e |
| math_0602270.pdf | BBLM v1 | 38baa479453564421afb5d2e51e2676e93b7d4c3b6173d3b956bc5482e33ccea |
| src_math_0602270 | BBLM e-print | b395fedd493366c54ee4f0997854b3d426e712684c95e0a0e1f1dacccdbe427d |
| x_bblm/bblm.tex | BBLM LaTeX | 52902e9b94e841cc700ae498180f645980d2ab8ec283dbbdd5068ac714a71dd1 |
| src_0708.4223 | Bogomolny 2007 v1 e-print | 0f5f10260c8495d725f8bddf6826e3e9d045462ced2110f0266201d4d0fb5b09 |
| x_bog07/zeta.tex | Bogomolny 2007 LaTeX | f35ddb819fc884fb32e5edabf290d5e8d376060f239428c35c757df698e3d8bd |
| src_nlin_0312061 | Bogomolny Les Houches v1 e-print | 63aa34f7647ae45f126e7d62b560c65b313b7df8611056d5998287b51d7692f8 |
| x_bog03/houches.tex | Les Houches LaTeX (searched only) | 459c8792857d8ab29b278399b7e4cdcc543398acad42470d64ac9c385fcd060e |

The PDF hashes of 1307.6010, 1307.6012, 2505.09865 and 2507.10193 match those recorded in lit/bblm_bk.md
(earlier download), so these are the same files.

**Not opened (UNVERIFIED):** BK PRL 77 (1996) 1472 (APS bot wall); BK I, Nonlinearity 8 (1995) 1115; BBLM
journal version and appendix (IOP); CS "Triple correlation" (math/0610495, abstract only); the journal
versions of FS25 and Nishigaki; Nishigaki 2024 PTEP 081A01 (the earlier mean-gap-ratio table); Google Scholar
citation lists.
