# Phase 6 literature: explicit formulas (exact normalisations)

Compiled 2026-10-07 for Phase 6 ("prime spectroscopy": the spectrum
S(τ) = Σ_{γ>0} w(γ) e^{iτγ} over raw zero heights). Every formula below is quoted from a source I
opened. The status tags are **PRIMARY-READ** (I read the original or the textbook itself),
**SECONDARY-READ** (I read a later paper that quotes or reproves the result) and **UNVERIFIED**
(I did not open it). Downloaded PDFs and sources are in `~/specarith_lit_cache/`, outside the repository,
and their sha256 hashes are listed in §8. Nothing in this directory is a copyrighted PDF.

Also, the adopted identity (§7) was **checked numerically to 30 significant digits** against actual zeros
of ζ(s) and of L(s, χ₋₄). The script and its output are in §9.

---

## 1. Landau 1911: Σ_{0<γ≤T} x^ρ

**Citation.** E. Landau, "Über die Nullstellen der Zetafunktion", *Math. Ann.* **71** (1912), 548–564.
The paper is signed "Göttingen, den 1. Juli 1911" (p. 564). The GDZ volume record gives the year as 1912. I did not
resolve a DOI. The page range was checked against the scan: first page 548, last page 564.
Ford–Zaharescu cite "(1911), 548–568", but **568 is wrong**. Durkan–Hughes–Pearce-Crump cite
"71(4):548–564, 1912", which is correct.

**Access.** GDZ Göttingen, METS `https://gdz.sub.uni-goettingen.de/mets/PPN235181684_0071.mets.xml`,
article LOG_0057, PDF `https://gdz.sub.uni-goettingen.de/download/pdf/PPN235181684_0071/LOG_0057.pdf`
(the page scans have no text layer, so I read the images). **PRIMARY-READ.**

**Landau's notation (important).** p. 548: "ρ = γ + βi". In Landau, **β is the imaginary part and γ is the real
part**, which is the reverse of the modern convention. Footnote **, p. 548: "x^ρ bedeutet e^{ρ log x} bei reellem
Logarithmus."

**Quoted statement (p. 553, "Satz 1").**
> Satz 1: *Es ist bei festem x > 1*
> Σ_{0<β≤T} x^ρ = { −(T/2π) log p + O(log T)  für x = p^m ;  O(log T)  für x ≠ p^m }.

> Satz 2 (p. 553): *Wenn 1 < x₀ < x₁ und das Intervall x₀ ≤ x ≤ x₁ von den p^m frei ist, so ist für
> x₀ ≤ x ≤ x₁ gleichmäßig* Σ_{0<β≤T} x^ρ = O(log T).

**Conventions and assumptions.**
- The statement is for the full **x^ρ**, not x^{iγ}, and sums over zeros with imaginary part in (0, T]. It is **unconditional**:
  there is no RH in the statement or in §1 (p. 553), and the zeros are all non-real zeros of ζ.
- The main term is written as "(T/2π) log p" for x = p^m, which is −(T/2π)Λ(x) in modern notation (Λ(x) = 0 for
  non-integer x).
- Under RH, x^ρ = x^{1/2} x^{iγ} with γ = Im ρ in modern notation. So Σ_{0<γ≤T} e^{iτγ} = −(T/2π) Λ(e^τ) e^{−τ/2} + O(log T)
  for fixed e^τ > 1. This gives a negative spike of height (T/2π)·Λ(n)/√n at τ = log n. This is my one-line
  consequence and is not quoted from Landau.
- p. 564 (end of paper): in terms of the zeros ±α of ξ (α = real ordinate under RH), Landau notes that
  Σ_α cos(αy)/α "divergiert für y = 0, m log p, −m log p und konvergiert für alle anderen reellen y". His closing remark is
  "Ich habe aber keine Ahnung, worin derselbe [Zusammenhang] besteht."

**Discrepancy with the from-memory form.** The form "Σ_{0<γ≤T} x^ρ = −(T/2π)Λ(x) + O(log T)" is correct in content.
Landau states it as a two-case formula with log p, and the summation variable is called β.

---

## 2. Gonek's uniform version

**Citation.** S. M. Gonek, "An explicit formula of Landau and its applications to the theory of the zeta-function",
in *A tribute to Emil Grosswald: number theory and related analysis*, Contemp. Math. **143**, AMS, Providence RI
(1993), 395–413. There is an earlier announcement: S. M. Gonek, "A formula of Landau and mean values of ζ(s)", in *Topics in
analytic number theory* (Austin 1982), Univ. Texas Press (1985), 92–97.

**Access.** I did not find an open copy of Gonek's paper, so the **primary source is UNVERIFIED**. **SECONDARY-READ** from two
independent sources:
- (a) B. Durkan, C. Hughes, A. Pearce-Crump, "Generalisations of the Landau–Gonek theorem and applications to mean
  values of zeta", arXiv:2601.18025v1 (25 Jan 2026), Theorem 2 and Corollary 2.1, p. 1–2.
  `https://arxiv.org/pdf/2601.18025`
- (b) K. Ford, A. Zaharescu, "On the distribution of imaginary parts of zeros of the Riemann zeta function",
  *J. reine angew. Math.* 579 (2005) 145–158 (from the arXiv journal-ref), arXiv:math/0405459v2, eq. (1.1) and Lemma 1 (3.1),
  p. 1 and p. 7.
  `https://arxiv.org/pdf/math/0405459`

**Quoted, (a) Theorem 2 ("Gonek, 1985" in their attribution).** Uniformly for X, T > 1,
$$\sum_{0<\gamma\le T} X^{\rho} = -\frac{T}{2\pi}\Lambda(X) + O\big(X\log(2XT)\log\log(3X)\big)
+ O\Big(\log X\,\min\big(T, \tfrac{X}{\langle X\rangle}\big)\Big) + O\Big(\log(2T)\,\min\big(T, \tfrac{1}{\log X}\big)\Big),$$
where ⟨X⟩ is the distance from X to the closest prime power other than X. The authors add (p. 2): "When we restrict X to
be an integer, Gonek also notes that the last two error terms are subsumed by the first two error terms."

**Quoted, (a) Corollary 2.1 ("Gonek, 1993"; uses ρ → 1−ρ).** Uniformly for X > 1, T > 1,
$$\sum_{0<\gamma\le T} X^{-\rho} = -\frac{T}{2\pi}\frac{\Lambda(X)}{X} + O(\log(2XT)\log\log(3X))
+ O\Big(\log X\min\big(\tfrac{T}{X},\tfrac{1}{\langle X\rangle}\big)\Big) + O\Big(\log(2T)\min\big(\tfrac{T}{X},\tfrac{1}{X\log X}\big)\Big).$$

**Quoted, (b) Lemma 1, a sharper main term near a prime power.** Let x, T > 1 and let n_x be the prime power nearest to x. Then
$$\sum_{0<\gamma\le T} x^{\rho} = -\frac{\Lambda(n_x)}{2\pi}\,\frac{e^{iT\log(x/n_x)}-1}{i\log(x/n_x)}
+ O\Big(x\log^2(2xT) + \frac{\log 2T}{\log x}\Big),$$
"where if x = n_x the first term is −TΛ(n_x)/2π". Ford–Zaharescu describe it as "a uniform version of a theorem of
Landau … the proof is nearly identical to the proof of Theorem 1 of Gonek ([5], §3)".

**Use for Phase 6.** Lemma 1 of (b) is the sharp-cutoff (w = 1_{(0,T]}) line shape. Under RH, with x = e^τ, the spike at τ = log n
has the Dirichlet-kernel profile (e^{iTν} − 1)/(iν), ν = τ − log n, multiplied by −Λ(n)/(2π) and by x^{−1/2} once x^ρ is converted to
e^{iτγ}. The error terms are **O(·) only and carry no explicit constants**, so they cannot serve as a floating-point bar. For the
exact bar, use §3 and §7 with a smooth window.

**Discrepancy.** The year of Gonek's theorem is attributed as 1985 or 1993 in different places. The Contemp. Math. 143 paper is 1993.

---

## 3. Weil / Guinand–Weil explicit formula for ζ(s), exact normalisation

### 3a. Modern form used here (PRIMARY-READ of the research papers that state it)

**Citations.**
- E. Carneiro, V. Chandee, M. B. Milinovich, "Bounding S(t) and S₁(t) on the Riemann hypothesis",
  *Math. Ann.* **356** (2013) 939–968, arXiv:1309.1526, **Lemma 5** (pp. 6–7 of the arXiv PDF).
  `https://arxiv.org/pdf/1309.1526`
- E. Carneiro, V. Chandee, M. B. Milinovich, "A note on the zeros of zeta and L-functions", *Math. Z.* **281**
  (2015), arXiv:1503.00955, **Lemma 4** (read in the LaTeX source `https://arxiv.org/e-print/1503.00955`).
  Proof: "This is [GG, Lemma 1]. For a similar formula, see [IK, Equation (25.10)]."
  [GG] = Goldston–Gonek; [IK] = Iwaniec–Kowalski, *Analytic Number Theory*, AMS Colloq. Publ. 53 (2004).

**Quoted (1503.00955, Lemma 4; unconditional).** Let h(s) be analytic in the strip |Im s| ≤ ½ + ε for some ε > 0, and
assume |h(s)| ≪ (1+|s|)^{−(1+δ)} for some δ > 0 when |Re s| → ∞. Then
$$\sum_\rho h\Big(\frac{\rho-\frac12}{i}\Big) = h\Big(\frac{1}{2i}\Big)+h\Big(-\frac{1}{2i}\Big)
+\frac1\pi\int_{-\infty}^{\infty} h(u)\,\mathrm{Re}\,\frac{\Gamma_{\mathbb R}'}{\Gamma_{\mathbb R}}\big(\tfrac12+iu\big)\,du
-\frac{1}{2\pi}\sum_{n=2}^\infty\frac{\Lambda(n)}{\sqrt n}\Big\{\hat h\Big(\frac{\log n}{2\pi}\Big)+\hat h\Big(-\frac{\log n}{2\pi}\Big)\Big\},$$
where "the sum on the left-hand side runs over the nontrivial zeros ρ of ζ(s)", Γ_ℝ(s) = π^{−s/2}Γ(s/2), and
$\hat F(\xi)=\int F(x)e^{-2\pi i x\xi}dx$ (the convention stated in the same paper).

**Quoted (1309.1526, Lemma 5).** Assume RH, with the same strip and decay conditions. "Let h(w) be real-valued for real w, and set
ĥ(x) = ∫ h(w) e^{−2πixw} dw. Then"
$$\sum_\rho h(\gamma) = h\Big(\frac{1}{2i}\Big)+h\Big(-\frac{1}{2i}\Big)-\frac{1}{2\pi}\hat h(0)\log\pi
+\frac{1}{2\pi}\int_{-\infty}^\infty h(u)\,\mathrm{Re}\,\frac{\Gamma'}{\Gamma}\Big(\frac14+\frac{iu}{2}\Big)du
-\frac{1}{2\pi}\sum_{n=2}^\infty\frac{\Lambda(n)}{\sqrt n}\Big(\hat h\Big(\frac{\log n}{2\pi}\Big)+\hat h\Big(-\frac{\log n}{2\pi}\Big)\Big).$$
Proof note: "follows from [16, Theorem 5.12] [= Iwaniec–Kowalski]. It can be stated unconditionally by replacing h(γ)
with h((ρ−1/2)/i)."

The two papers agree. Since Γ_ℝ'/Γ_ℝ(½+iu) = −½ log π + ½ ψ(¼ + iu/2), the term
(1/π)∫h Re(Γ_ℝ'/Γ_ℝ) equals −(1/2π)ĥ(0) log π + (1/2π)∫h Re ψ(¼+iu/2). This is my algebra; it is exact.

**Conventions.**
- **Zeros summed:** all nontrivial zeros, γ of both signs, with multiplicity. Under RH the argument is γ; without RH it is (ρ−½)/i.
- **Fourier transform:** ĥ(ξ) = ∫h(x)e^{−2πixξ}dx. h need **not** be even. The prime sum carries both ĥ(+log n/2π)
  and ĥ(−log n/2π).
- **Sign:** the prime-power term enters with a **minus** sign.
- **Real-valuedness:** 1309.1526 assumes h real on ℝ, and 1503.00955 Lemma 4 does not. The identity is linear in h, so it holds
  for complex h (e.g. w(r)e^{iτr}). This is confirmed numerically in §9 to 1e−29.

### 3b. Translation to the g-convention (my algebra, exact)

Define g(u) = (1/2π)∫h(r)e^{−iru}dr, so that h(r) = ∫g(u)e^{iru}du. Then ĥ(ξ) = 2π g(2πξ), so (1/2π)ĥ(±log n/2π) = g(±log n)
and (1/2π)ĥ(0) = g(0). The formula becomes
$$\sum_\rho h(\gamma)=h(\tfrac i2)+h(-\tfrac i2)-g(0)\log\pi+\frac1{2\pi}\int_{-\infty}^\infty h(r)\,\mathrm{Re}\,\psi\big(\tfrac14+\tfrac{ir}2\big)dr-\sum_{n\ge2}\frac{\Lambda(n)}{\sqrt n}\big[g(\log n)+g(-\log n)\big].$$

**Comparison with the from-memory form.**
- Every factor matches: h(i/2)+h(−i/2), −g(0) log π, (1/2π)∫h Re ψ(¼+ir/2) dr, and −2Σ Λ(n)/√n g(log n).
- **One caveat:** "−2Σ Λ(n)/√n g(log n)" is valid **only for even h**, since g is then even. For the Phase 6 test function
  h(r) = w(r)e^{iτr}, which is not even, the term must be written −Σ Λ(n)/√n [g(log n) + g(−log n)].
- The conditions on h are those quoted above: analytic in |Im| ≤ ½+ε, with decay (1+|s|)^{−1−δ} in the strip.

### 3c. Textbook form: Montgomery–Vaughan Theorem 12.13 ("Weil") (PRIMARY-READ)

H. L. Montgomery, R. C. Vaughan, *Multiplicative Number Theory I. Classical Theory*, CUP (2007),
doi:10.1017/CBO9780511618314. Chapter 12, **Theorem 12.13, p. 410**, from the author-hosted chapter PDF
`https://personal.science.psu.edu/rcv4/personal/Publications/MNTI/16.0_pp_397_418_Explicit_formulae.pdf`.

> Let F(x) be measurable with ∫e^{(½+δ₀)2π|x|}|F(x)|dx < ∞ (12.20) and ∫e^{(½+δ₀)2π|x|}|dF(x)| < ∞ (12.21), with
> F(x) = ½(F(x−)+F(x+)) and F(x)+F(−x) = 2F(0)+O(|x|). Put Φ(s) = ∫F(x)e^{−(s−½)2πx}dx. Let χ be a primitive
> character modulo q. Then
> $$\lim_{T\to\infty}\sum_{|\gamma|\le T}\Phi(\rho)=E_0(\chi)(\Phi(0)+\Phi(1))+\frac1{2\pi}\Big(\log\frac q\pi+\frac{\Gamma'}{\Gamma}(1/4+\kappa/2)\Big)F(0)
> -\frac1{2\pi}\sum_{n=1}^\infty\frac{\Lambda(n)}{n^{1/2}}\Big(\chi(n)F\big(\tfrac{-1}{2\pi}\log n\big)+\bar\chi(n)F\big(\tfrac1{2\pi}\log n\big)\Big)
> +\int_0^\infty\frac{e^{-(1+2\kappa)\pi x}}{1-e^{-4\pi x}}\big(2F(0)-F(x)-F(-x)\big)dx\quad(12.22)$$
> E₀(χ) = 1 if χ = χ₀, else 0; κ = 0 if χ(−1) = 1, κ = 1 if χ(−1) = −1.

(The PDF text extraction dropped the overline on the second χ. Its placement is inferred from the Fourier dictionary below and
agrees with §4. It is irrelevant for real χ.) Dictionary: Φ(½+iγ) = ∫F(x)e^{−2πiγx}dx, so with h(γ) := Φ(½+iγ) we have
**F(x) = ĥ(−x)** in the ĥ-convention of §3a. Then F(−log n/2π) = ĥ(log n/2π), consistent with §3a and §4. The Γ-term appears here in Weil's
"F(0) + ∫(2F(0)−F(x)−F(−x))…" form rather than as ∫h Re ψ. I did not check that equivalence separately. It is implied
by the numerically verified §3a/§4, which use the same zeros.

MV Notes §12.3 (p. 417): "Theorem 12.13 is a special case of the main result of Weil (1952) …". Weil's paper is A. Weil,
"Sur les 'formules explicites' de la théorie des nombres premiers", Comm. Sém. Math. Univ. Lund [Medd. Lunds Univ. Mat.
Sem.], Tome Supplémentaire (1952), 252–265. **UNVERIFIED (not opened).**

### 3d. Not opened

- Rudnick & Sarnak, "Zeros of principal L-functions and random matrix theory", *Duke Math. J.* **81** (1996) 269–322:
  **UNVERIFIED**, no open copy found. M. Das's survey (arXiv:2002.00595) was opened but does not state the formula.
- Iwaniec–Kowalski Thm 5.12 / eq. (25.10): **UNVERIFIED** (book not opened). Both CCM papers and CMQR cite it as the source.

---

## 4. Explicit formula for a primitive Dirichlet character (χ₋₄)

**Citation.** E. Carneiro, M. B. Milinovich, E. Quesada-Herrera, A. P. Ramos, "Fourier optimization, the least quadratic
non-residue, and the least prime in an arithmetic progression", arXiv:2404.08380 (revision source dated 2025-08-11),
**Lemma 9 ("Guinand-Weil explicit formula")**, §"Explicit formula and auxiliary lemmas". I read the LaTeX source
`https://arxiv.org/e-print/2404.08380`. **PRIMARY-READ** (as a research-paper statement; they say it follows by "modifying the
proof of [IK, Theorem 5.12]; see for instance [CarFinder, Lemma 5]").

**Quoted.** Let h(s) be analytic in the strip |Im s| ≤ ½+ε for some ε > 0, and assume |h(s)| ≪ (1+|s|)^{−(1+δ)} for some
δ > 0 when |Re s| → ∞. Let χ be a primitive Dirichlet character modulo q. Then
$$\sum_{\rho_\chi}h\Big(\frac{\rho_\chi-\frac12}{i}\Big)=\hat h(0)\frac{\log(q/\pi)}{2\pi}+\frac1{2\pi}\int_{-\infty}^\infty h(u)\,\mathrm{Re}\frac{\Gamma'}{\Gamma}\Big(\frac{2-\chi(-1)}4+\frac{iu}2\Big)du
-\frac1{2\pi}\sum_{n\ge2}\frac{\Lambda(n)}{\sqrt n}\Big\{\chi(n)\hat h\Big(\frac{\log n}{2\pi}\Big)+\overline{\chi(n)}\,\hat h\Big(-\frac{\log n}{2\pi}\Big)\Big\},$$
"where the sum on the left-hand side runs over the non-trivial zeros ρ_χ of L(s,χ)". The Fourier transform is the same
ĥ(ξ) = ∫h e^{−2πixξ}.

**Cross-check.** CCM 2015 (arXiv:1503.00955) §"Extension to general L-functions", eq. (Exp_Form_L), has the same structure:
r(π){h(1/2i)+h(−1/2i)} + (1/π)∫h(u) Re (L'/L)(½+iu, π_∞) du − (1/2π)Σ n^{−½}{Λ_π(n)ĥ(log n/2π) + Λ_π̃(n)ĥ(−log n/2π)} − [μ_j corrections].
With L(s,π_∞) = N^{s/2}Γ_ℝ(s+μ), N = q, μ = a, this gives (L'/L)(½+iu) = ½log(q/π) + ½ψ(¼+a/2+iu/2), which reproduces
the formula above (my algebra). There, −L'/L(s,π) = ΣΛ_π(n)n^{−s}, so Λ_π(n) = χ(n)Λ(n).

**Ingredients, read off.**
- **Γ-factor parity:** the argument is (2−χ(−1))/4 + iu/2 = ¼ + a/2 + iu/2, with a = 0 (even) or a = 1 (odd).
  **For χ₋₄ (odd): ψ(¾ + iu/2).**
- **Conductor term:** + ĥ(0) log(q/π)/(2π) = + g(0) log(q/π). For ζ (q = 1) this is −g(0) log π, as in §3.
- **Pole/trivial terms:** **none.** L(s,χ) for primitive χ mod q > 1 has no pole, so there is no h(±i/2) term. The trivial zeros are absorbed
  in the Γ-integral, and the left side sums nontrivial zeros only. (The μ_j-correction terms in CCM 2015 vanish since Re μ = a ≥ 0.)
- **Prime weights:** χ(n)Λ(n)/√n at +log n and conj(χ(n))Λ(n)/√n at −log n. In the g-convention:
  −Σ Λ(n)/√n [χ(n) g(log n) + χ̄(n) g(−log n)]. For even h this becomes −Σ Λ(n)/√n (χ(n)+χ̄(n)) g(log n), which is the form in
  Hughes–Rudnick (2.1). **For real χ (χ₋₄): weights χ(n)Λ(n)/√n on both sides**, χ₋₄(p^k) = χ₋₄(p)^k, χ₋₄(2) = 0.
- **Sign consequence for χ₋₄:** the spike at τ = log n has sign **−χ(n)**. It is negative at p ≡ 1 (mod 4) (5, 13, …),
  positive at p ≡ 3 (mod 4) (3, 7, 11, …), absent at powers of 2, and negative at 9 = 3². This is confirmed in the §9 output.
- **Zero symmetry:** for real χ the zeros are symmetric γ ↔ −γ. For complex χ the zeros with γ < 0 are conjugates of zeros
  of L(s, χ̄) (CMQR, proof of Lemma 10, quoting MV).

**Discrepancy found: do not use Hughes–Rudnick (2.1) as printed.** C. P. Hughes, Z. Rudnick, "Linear statistics of
low-lying zeros of L-functions", *Q. J. Math.* 54 (2003), arXiv:math/0208230, eq. (2.1). I read the LaTeX source.
- They print G_χ(r) = Γ'/Γ(½ + a(χ) + ir) + Γ'/Γ(½ + a(χ) − ir) − ½ log π, with the integrand (1/2π)h(r)(log q + G_χ(r)), and
  a strip condition "−c ≤ Im r ≤ 1+c".
- This is a typo. It gives zero density (1/2π)(log q + 2 log|r|), whereas the correct density is (1/2π) log(q|r|/2π) (see §5).
- The correct Γ-term is (1/2π)∫h(r)[log(q/π) + ½ψ(¼+a/2+ir/2) + ½ψ(¼+a/2−ir/2)] dr. Their g-convention and prime term
  are fine for even h.

---

## 5. Smooth counting functions N(T) and N(T, χ)

**Primary textbook source.** Montgomery–Vaughan (2007), Chapter 14, author-hosted PDF
`https://personal.science.psu.edu/rcv4/personal/Publications/MNTI/18.0_pp_452_462_Zeros.pdf`. **PRIMARY-READ.**

**ζ: MV Theorem 14.1, eq. (14.2), p. 452.** N(T) counts zeros with 0 < β < 1, 0 < γ < T, using the half-sum
(N(T+)+N(T−))/2 at an ordinate. S(t) = (1/π) arg ζ(½+it) (14.1). For T > 0,
$$N(T)=\frac1\pi\arg\Gamma(1/4+iT/2)-\frac{T}{2\pi}\log\pi+S(T)+1.\qquad(14.2)$$
This is θ(T)/π + 1 + S(T) with θ(T) = arg Γ(¼+iT/2) − (T/2)log π, as in the from-memory form.

**MV Corollary 14.2, p. 453.** For T ≥ 2,
N(T) = (T/2π) log(T/2π) − T/2π + 7/8 + S(T) + O(1/T). This matches the from-memory form.

**Cross-source.** Berry–Keating 1999 (§6) eq. (2.3), p. 239:
⟨N(t)⟩ ≡ θ(t)/π + 1 = (1/π)[arg Γ(¼ + ½it) − ½ t log π] + 1 = (t/2π) log(t/2πe) + 7/8 + O(1/t). They cite Titchmarsh 1986 [11].

**Numerical note (mine, not quoted).** θ(T)/π + 1 − [(T/2π)log(T/2π) − T/2π + 7/8] = 6.6315e−4, 6.6315e−5, 6.6315e−6 at T = 10, 100, 1000.
So the O(1/T) term is ≈ 1/(48πT) = 0.0066315/T. mpmath's `siegeltheta(T)` equals Im log Γ(¼+iT/2) − (T/2)log π
to working precision (0 difference at 30 digits). Use `mpmath.loggamma` (continuous branch, arg Γ(¼) = 0 at T = 0).

**Dirichlet: MV Theorem 14.5, pp. 454–455.** Let χ be primitive mod q > 1. N(T,χ) counts zeros with 0 < β < 1, 0 ≤ γ ≤ T,
and "any zeros with γ = 0 or γ = T should be counted with weight 1/2". S(T,χ) = (1/π) arg L(½+iT,χ) (14.5). Then
$$N(T,\chi)=\frac1\pi\arg\Gamma(1/4+\kappa/2+iT/2)+\frac T{2\pi}\log\frac q\pi+S(T,\chi)-S(0,\chi),$$
with κ = 0 or 1 according as χ(−1) = 1 or −1. MV add: "the number of zeros of L(s,χ) with −T ≤ γ ≤ 0 is N(T, χ̄)".

**MV Corollary 14.6, p. 455.** For T > 0,
N(T,χ) = (T/2π) log(qT/2π) − T/2π + S(T,χ) − S(0,χ) − χ(−1)/8 + O(1/(T+1)).
For χ₋₄ (odd) the constant is **+1/8**. For ζ it is 7/8 = 1 − 1/8, where the "1" comes from the pole. The same 1/(48πT) correction
appears numerically for κ = 1, q = 4.

**Numerical consistency (§9).** For χ₋₄ I found 81 zeros with 0 < γ < 143.63. MV 14.5 gives a smooth part of 80.49 there.
This is consistent: the difference is S(T,χ) − S(0,χ), well inside |·| < 1. For ζ, 50 zeros below 144 agree with `mpmath.nzeros`.

**Not opened.** Titchmarsh (2nd ed., rev. Heath-Brown, 1986) §9.3 and Edwards (1974) §6.6 are **UNVERIFIED**. MV
and Berry–Keating replace them.

---

## 6. The sign relative to Gutzwiller ("sign puzzle")

**(a) Berry & Keating.** M. V. Berry, J. P. Keating, "The Riemann zeros and eigenvalue asymptotics", *SIAM Review*
**41** (1999) 236–266, doi:10.1137/S0036144598347497. Author-hosted PDF
`https://michaelberryphysics.wordpress.com/wp-content/uploads/2013/06/berry307.pdf`. **PRIMARY-READ.**

- **Eq. (2.6), p. 240:**
  N^fl(t) = −(1/π) Im Σ_p log{1 − exp(−it log p)/√p} = **−(1/π)** Σ_p Σ_{m≥1} exp(−½ m log p) sin{tm log p} / m.
  They describe it as "the divergent but formally exact expression" obtained by substituting the Euler product into (2.4).
- **Gutzwiller, eq. (2.9), p. 241:**
  N^fl(E) ∼ **(1/π)** Σ_p Σ_{m≥1} sin{mS_p(E)/ℏ − ½πmμ_p} / (m √|det(M_p^m − I)|).
- **Density form, eqs. (2.16)–(2.18), p. 243:** d^fl(E) = (1/πℏ) Σ_j A_j cos{S_j(E)/ℏ}, with A_j ∼ T_j/(m√|det(M_j − I)|) (2.17).
  "For the Riemann zeros … µ_j = 0, **A_j = −log p / p^{m/2} = −(T_j/m) exp{−½T_j}** (2.18), and is an identity rather than an
  asymptotic approximation."
- **The sign passage, p. 243:**
  > "There are two discordant features of the analogy [1] … Second, the negative sign in (2.6) indicates that when the Maslov
  > phases πmµ_p/2 are reinstated in (2.13) their value should be π for all orbits, but this is hard to understand because if
  > the index is π for a given orbit it should be 2π for the same orbit traversed twice."
- **§6 item f, p. 260:**
  > "The Maslov phases associated with the orbits are also peculiar: they are all π. The result appears paradoxical in view
  > of the relation between these phases and the winding numbers of the stable and unstable manifolds associated with
  > periodic orbits [22], but finds an explanation in a scheme of Connes [62]."
  [62] = A. Connes, *C. R. Acad. Sci. Paris* 323 (1996) 1231–1236. Also on p. 260: "We have no explanation of property f."

**(b) Connes.** A. Connes, "Trace formula in noncommutative geometry and the zeros of the Riemann zeta function",
arXiv:math/9811068 (Nov 1998). The journal version, which I believe is *Selecta Math. (N.S.)* 5 (1999) 29–106, is not given on the arXiv page
and is **unverified**. I read the LaTeX source of the arXiv version. **PRIMARY-READ (arXiv version).**

- **Eq. (6) (Gutzwiller, after Berry [B]):** N_osc(E) ≃ (1/π) Σ_{γ_p} Σ_m (1/m) · 1/(2 sh(mλ_p/2)) · sin(S_pm(E)).
- **Eq. (7):** N_osc(E) ≃ **(−1/π)** Σ_p Σ_m (1/m)(1/p^{m/2}) sin(m E log p).
- **The sign passage:**
  > "However there are two important mismatches (cf. [B]) between the two formulas (6) and (7). The first one is the overall
  > *minus sign* in front of formula (7), the second one is that though 2 sh(mλ_p/2) ∼ p^{m/2} when m → ∞, we do not have an
  > equality for finite values of m."
- **Resolution proposed (introduction):**
  > "The minus sign which was problematic in the above discussion admits here a beautiful resolution since the analogue of
  > the Polya-Hilbert space is given … by the cohomology group H¹_et(Σ̄, Q_ℓ) (2) which appears with an overall minus sign
  > in the Lefchetz formula (3) … (C) The Polya-Hilbert space H should appear from its negative ⊖H. In other words, the
  > spectral interpretation of the zeros of the Riemann zeta function should be as an absorption spectrum rather than as an
  > emission spectrum."
  The abstract reads "We give a spectral interpretation of the critical zeros of the Riemann zeta function as an absorption
  spectrum". [B] = M. V. Berry, "Riemann's zeta function: a model for quantum chaos?", in *Quantum Chaos and Statistical
  Nuclear Physics*, Lecture Notes in Phys. 263 (1986). That paper is **UNVERIFIED (not opened)** and is the original locus of the remark.

**Consistency with §3 (my algebra).**
- Write the prime term of §3b as −Σ Λ(n)/√n [g(log n)+g(−log n)] = ∫h(r)[−(1/π)Σ_n Λ(n)/√n cos(r log n)] dr.
- So the oscillatory zero density on the full line is d_osc(r) = −(1/π)Σ_n Λ(n) n^{−½} cos(r log n). This is exactly
  Berry–Keating (2.16)+(2.18) with ℏ = 1 and Λ(p^m) = log p.
- In Gutzwiller form (A_j > 0, µ = 0) a periodic orbit would give a **positive** peak of S(τ) at τ = period. The Riemann zeros give a
  **negative** peak at τ = log p^m. This is the sign puzzle.

---

## 7. Conventions to adopt: one exact identity for S(τ)

**Setting.**
- Let w be a real entire window that is real on ℝ, decays on horizontal lines in the strip |Im r| ≤ ½+ε, and is effectively
  supported on r > 0.
- Canonical choice: the **Gaussian** w(r) = exp(−(r−T₀)²/(2σ²)) with T₀ ≫ σ.
- Let ŵ(ξ) = ∫w(x)e^{−2πixξ}dx. Define
  $$S(\tau)=\sum_{\gamma_k>0} w(\gamma_k)e^{i\tau\gamma_k}$$
  over positive ordinates (raw heights, with multiplicity) of ζ, or of L(s, χ) for real primitive χ mod q.

**Step 1 (test function).** Take h_τ(r) := w(r) e^{iτr}. It is analytic in the strip, and |h_τ(x+iy)| = w-decay × e^{−τy} is bounded
in |y| ≤ ½+ε. So the hypotheses of §3a/§4 hold. The function is complex-valued, and linearity covers that (verified in §9).

**Step 2 (left side).** Assume RH/GRH for the zeros used (for the tabulated zeros this is a numerically verified fact up to their height).
The zeros come in ±γ pairs for ζ and for real χ. So
$$\sum_\rho h_\tau(\gamma)=S(\tau)+M(\tau),\qquad M(\tau):=\sum_{\gamma_k>0}w(-\gamma_k)e^{-i\tau\gamma_k}$$
M is the "mirror" term. For the Gaussian, |M| ≤ Σ e^{−(γ_k+T₀)²/2σ²}, which is negligible but **exactly computable from the same zeros**.
Keep it in the identity rather than drop it.

**Step 3 (Fourier pieces).** ĥ_τ(ξ) = ŵ(ξ − τ/2π). In the g-convention, g_τ(u) := (1/2π)∫h_τ(r)e^{−iru}dr = (1/2π)ŵ((u−τ)/2π).
For the Gaussian (closed form, my algebra; consistent with §9):
$$g_\tau(u)=\frac{\sigma}{\sqrt{2\pi}}\;e^{-\sigma^2(u-\tau)^2/2}\;e^{-i(u-\tau)T_0}.$$

**Step 4 (the identity).** Substitute into §3a (ζ: q = 1, a = 0, χ ≡ 1, pole terms present) or §4 (primitive χ mod q > 1,
a = (1−χ(−1))/2, no pole terms):
$$\boxed{\;S(\tau)= -M(\tau)\;+\;\delta_{q,1}\big[h_\tau(\tfrac i2)+h_\tau(-\tfrac i2)\big]\;+\;g_\tau(0)\log\frac q\pi\;+\;\frac1{2\pi}\int_{-\infty}^{\infty}w(u)e^{i\tau u}\,\mathrm{Re}\,\psi\Big(\frac14+\frac a2+\frac{iu}2\Big)du\;-\;\sum_{n\ge2}\frac{\Lambda(n)}{\sqrt n}\Big[\chi(n)\,g_\tau(\log n)+\overline{\chi(n)}\,g_\tau(-\log n)\Big]\;}$$
- h_τ(±i/2) = w(±i/2) e^{∓τ/2}, where w(±i/2) means the analytic continuation of w (for the Gaussian, exp(−(±i/2 − T₀)²/2σ²)).
- For ζ: log(q/π) = −log π.
- For χ₋₄: q = 4, a = 1 (ψ(¾ + iu/2)), and χ(n)Λ(n) is real.

**Reading the identity.**
- **Prime spikes.** −Λ(n)χ(n)/√n · g_τ(log n) is a Gaussian line of width 1/σ in τ, centred at **τ = log n**, with peak value
  **−(σ/√(2π)) χ(n)Λ(n)/√n**. It carries the phase factor **e^{i(τ−log n)T₀}**, so only the modulus or the phase-demodulated value
  is a pure "negative spike" off the peak.
  - The peak height matches Landau (§1) with T → ∫w = σ√(2π): −(∫w/2π) Λ(n)/√n.
  - The g_τ(−log n) "mirror spikes" sit at τ = −log n, outside [0.5, 4.5]. Their tails are ∝ e^{−σ²(τ+log n)²/2}.
- **Smooth (Γ) term.** This is a smooth window transform at frequency τ. It decays like ŵ at τ (≈ e^{−σ²τ²/2} for the Gaussian).
  With T₀ = 60, σ = 6 it is 0.09 at τ = 0.5, 1.5e−3 at log 2, and below 1e−14 for τ ≥ log 4 (§9 column "gammaterm"). It is
  **not** negligible at the low end of [0.5, 4.5] unless σ is large, so keep it.
- **Equivalence check (my algebra).** For ζ, (1/2π)[Re ψ(¼+iu/2) − log π] = θ'(u)/π, with θ the Riemann–Siegel theta
  (d/du Im log Γ(¼+iu/2) = ½ Re ψ(¼+iu/2)). So the conductor and Γ terms together equal (1/π)∫h_τ(u) θ'(u) du = ∫h_τ dN_smooth,
  consistent with MV (14.2). For χ, the same holds with MV Thm 14.5.

**Steps I am not certain of (flagged).**
1. Extending the CCM Lemma 5 hypothesis "h real-valued on ℝ" to complex h by linearity. It is fine in principle, CCM 2015 Lemma 4
   drops the condition, and §9 confirms it to 1e−29. Still, it is an inference and not a quoted statement.
2. The form of §3a/§4 without RH uses h((ρ−½)/i). Using h(γ) presumes the zeros used lie on the line. For tabulated zeros this is
   the numerically established situation; it is not a theorem.
3. With non-Gaussian windows (e.g. a compactly supported taper), w is not entire, so §3/§4 do not apply verbatim. One then needs
   the Weil-class version (MV Thm 12.13 hypotheses on F = ĥ(−·), conditions (12.20)–(12.21)), or a window with analytic
   continuation to the strip. The Gaussian, or any entire window decaying in the strip, avoids this.
4. Iwaniec–Kowalski Thm 5.12, Rudnick–Sarnak and Weil 1952 were **not opened**. The identity rests on CCM 2013/2015, CMQR, MV
   12.13/14.x and the numerical check.

---

## 8. Source files (outside the repo, `~/specarith_lit_cache/`) and sha256

| file | sha256 |
|---|---|
| landau/landau1911_LOG_0057.pdf (GDZ scan, Math. Ann. 71) | 92841e7262f65efb0bdaa774bf0dc56f621a608cc92b4fab858973bcf78a4cf7 |
| math_0405459.pdf (Ford–Zaharescu) | 694ba24ada3b9b206bf082cff6a088917691532b3df885932c1ecfd188d36e66 |
| 2601.18025.pdf (Durkan–Hughes–Pearce-Crump) | 9b29bb43ec55817d095f5d5ee013a8011c6f493b21e0ea78897ed2b54c442ac1 |
| 1110_ccm_bounding.pdf (= arXiv:1309.1526, CCM 2013; misnamed file) | 6ad94674038e6a619ec1eaebecf83672374d56de8370a970797d7f47a77f8c16 |
| src_1503/src.gz (arXiv:1503.00955 LaTeX, CCM 2015) | 6702759b468be67dd4f7fed6b390722a2a23b0c86bb1bd5c8da597456617fb4b |
| src_2404/src.gz (arXiv:2404.08380 LaTeX tarball, CMQR) | b2491b11ddf5153d0433043ff098d648e7ae5357c10c452a40ef1ee135ed0254 |
| src_hr/hr.src (arXiv:math/0208230 LaTeX, Hughes–Rudnick) | ccc0b83a9dedf15f712c12907d818f439a6c54bb74a8f60bcaccdc79006ea65e |
| mv/mv_ch12_explicit.pdf (MV Ch. 12) | 51d6d04a6a6d8ef32c08ecd0cb38e0a4e94f36be1c205a960e12f2b0b16974ee |
| mv/mv_ch14_zeros.pdf (MV Ch. 14) | f44acc37b5fcc90a0fd2a882d5440d51eba40c56011d877c0ddb0a974d1e865e |
| berry307.pdf (Berry–Keating SIAM Rev.; re-downloaded, identical hash) | 26baa1c22dabb428bfa6f0535eb9c8431774f18b5f294dd11c62d7f4abd71cf1 |
| src_connes/src.gz (arXiv:math/9811068 LaTeX, Connes) | 0e1a9d4acac8fd9eff70f24aed3a895c5d3af4352d0b54ca2a0629d82dd2e931 |

(The cache directory is shared with other sessions. Other files in it were not used here.)

---

## 9. Numerical verification of §7 (generator and output)

The generator was run with mpmath 1.3.0 at 30 digits, with `/home/combust/fmexplorer/bin/python3`. The full file
`verify_ef.py` has sha256 fa2a27303c034f25fbbcd93a2bd3750adfd0dacccb76b48a76ca80b888b25d18. A copy with the same hash is
kept outside the repo at `~/specarith_lit_cache/ef_agent/verify_ef.py`. The listing below is that file with the docstring and the print/main block
condensed into a comment.
- Window: Gaussian with T₀ = 60, σ = 6.
- Zeros: all zeros with 0 < γ ≤ 144 and their mirrors. For ζ these come from `mpmath.zetazero`. For χ₋₄ they are the sign changes of
  the real completed function (4/π)^{(s+1)/2}Γ((s+1)/2)L(s,χ₋₄) on the critical line, refined to 45 digits.
- Prime sum: n ≤ 3000.
- Columns: LHS = Σ_{all zeros} h_τ(γ); RHS = §3a / §4.

ζ (50 zeros ≤ 144; `mpmath.nzeros(144)` = 50):
```
tau        LHS(re)              LHS(im)              RHS(re)              RHS(im)            |diff|      gammaterm   primeterm(re)
0.5        -0.317475377309507   -0.558458936942184   -0.317475377309507   -0.558458936942184    3.28e-30     0.0918   -0.334617
0.693147    -1.22827852605308  -0.0576336269272348    -1.22827852605308  -0.0576336269272348    4.97e-30    0.00147    -1.22767
1.09861     -1.56842428869383   -0.154040453541329    -1.56842428869383   -0.154040453541329    5.36e-30    3.19e-9    -1.56842
1.60944      -2.0036752491807  -0.0154978929108426     -2.0036752491807  -0.0154978929108426    8.81e-30   5.14e-20    -2.00368
3.0           2.3146072734895     1.84887805674361      2.3146072734895     1.84887805674361    2.99e-29   4.31e-23     2.31461
4.5         -2.37730629106352    -1.03216619605781    -2.37730629106352    -1.03216619605781    4.19e-29   2.04e-23    -2.37731
```
χ₋₄ (81 zeros ≤ 144; first zeros 6.0209489047, 10.2437703042, 12.9880980123, 16.3426071046):
```
tau        LHS(re)              LHS(im)              RHS(re)              RHS(im)            |diff|      gammaterm   primeterm(re)
0.5        0.0223240344621172  -0.0931841782884557   0.0223240344621172  -0.0931841782884557    1.95e-30     0.0918  -0.000503901
0.693147   0.0535497487471505   0.0555599245587766   0.0535497487471505   0.0555599245587766    8.65e-30    0.00147   0.0545812
1.09861      1.50693692527376  -0.0109029844390103     1.50693692527376  -0.0109029844390103    6.94e-30    3.19e-9     1.50694
1.60944     -1.65883237331732   -0.234001019207742    -1.65883237331732   -0.234001019207742    1.69e-29   5.14e-20    -1.65883
1.94591      1.91713191426775  -0.0939657525237013     1.91713191426775  -0.0939657525237013     2.1e-29   1.05e-23     1.91713
4.5         -3.04213790251428    -1.60265938703803    -3.04213790251428    -1.60265938703803    2.52e-29   2.33e-25    -3.04214
```
All 12 τ values (0.5, log 2, 1, log 3, log 4, log 5, 2.5, log 7, log 8, log 9, 3, 4.5) agree to ≤ 4.7e−29 in both
cases. The rows above are excerpts, and no separate log file was kept. Before refinement to 45 digits,
χ₋₄ zeros from bracketing alone gave |diff| ≈ 1e−10. That is a zero-accuracy floor and not a formula error.
- The χ₋₄ spikes have sign −χ(n): +1.51 at log 3, −1.66 at log 5, +1.92 at log 7, and nothing at log 2.
- The ζ spike at log 2 is −1.23, against −(σ/√(2π))·log 2/√2 = −1.173 for the isolated line. The remainder is overlap from the log 3
  line at separation 0.405, where the width is 1/σ = 0.167.

Generator (`verify_ef.py`; usage `python3 -I verify_ef.py T0 sigma {zeta|chi4}`):
```python
import sys
import mpmath as mp

mp.mp.dps = 30
T0 = mp.mpf(sys.argv[1]) if len(sys.argv) > 1 else mp.mpf(60)
SIG = mp.mpf(sys.argv[2]) if len(sys.argv) > 2 else mp.mpf(6)
TAUS = [mp.mpf('0.5'), mp.log(2), mp.mpf(1), mp.log(3), mp.log(4), mp.log(5), mp.mpf('2.5'),
        mp.log(7), mp.log(8), mp.log(9), mp.mpf('3.0'), mp.mpf('4.5')]
NMAX = 3000

def w(r):        return mp.exp(-(r - T0) ** 2 / (2 * SIG ** 2))
def h(r, tau):   return w(r) * mp.exp(1j * tau * r)
def hhat(xi, tau):   # hhat(xi) = int h(x) exp(-2 pi i x xi) dx, closed form for the Gaussian
    nu = 2 * mp.pi * xi - tau
    return SIG * mp.sqrt(2 * mp.pi) * mp.exp(-SIG ** 2 * nu ** 2 / 2) * mp.exp(-1j * nu * T0)

def mangoldt(n):
    for p in range(2, n + 1):
        if n % p == 0:
            m = n
            while m % p == 0: m //= p
            return mp.log(p) if m == 1 else mp.mpf(0)
    return mp.mpf(0)
LAM = {n: mangoldt(n) for n in range(2, NMAX + 1)}

def gamma_integral(tau, shift):   # (1/2pi) int h(u) Re psi(shift + iu/2) du
    f = lambda u: h(u, tau) * mp.re(mp.digamma(shift + 1j * u / 2))
    return mp.quad(f, mp.linspace(T0 - 14 * SIG, T0 + 14 * SIG, 113)) / (2 * mp.pi)

def rhs(tau, chi, q, shift, pole):
    tot = mp.mpc(0)
    if pole: tot += h(1j / 2, tau) + h(-1j / 2, tau)
    tot += mp.log(mp.mpf(q) / mp.pi) / (2 * mp.pi) * hhat(0, tau)
    g = gamma_integral(tau, shift); tot += g
    pr = mp.mpc(0)
    for n, L in LAM.items():
        c = chi(n)
        if L == 0 or c == 0: continue
        x = mp.log(n) / (2 * mp.pi)
        pr += L / mp.sqrt(n) * (c * hhat(x, tau) + mp.conj(c) * hhat(-x, tau))
    tot -= pr / (2 * mp.pi)
    return tot, g, -pr / (2 * mp.pi)

def lhs(tau, gp, gn): return mp.fsum(h(g, tau) for g in gp) + mp.fsum(h(g, tau) for g in gn)

def zeta_zeros(tmax):
    out, n = [], 1
    while True:
        g = mp.im(mp.zetazero(n))
        if g > tmax: return out
        out.append(g); n += 1

def chi4(n): return [0, 1, 0, -1][n % 4]

def L4_zeros(tmax, step=mp.mpf('0.05')):
    def Z(t):   # completed L(s, chi_-4); real on the critical line (root number 1)
        s = mp.mpf('0.5') + 1j * t
        v = (4 / mp.pi) ** ((s + 1) / 2) * mp.gamma((s + 1) / 2) * mp.dirichlet(s, [0, 1, 0, -1])
        return mp.re(v), mp.im(v)
    zs, t = [], mp.mpf('0.01'); prev = Z(t)[0]; maxim = 0
    while t < tmax:
        t2 = t + step; cur, im = Z(t2)
        maxim = max(maxim, abs(im) / (abs(cur) + 1e-300))
        if prev * cur < 0:
            r0 = mp.findroot(lambda x: Z(x)[0], (t, t2), solver='anderson')
            with mp.workdps(mp.mp.dps + 15):
                r1 = mp.findroot(lambda x: Z(x)[0], (r0, r0 + mp.mpf('1e-12')), solver='secant',
                                 tol=mp.mpf(10) ** (-2 * mp.mp.dps))
            zs.append(+r1)
        prev, t = cur, t2
    return zs, maxim
# main: zeta -> chi=1, q=1, shift=1/4, pole=True ; chi4 -> chi=chi4, q=4, shift=3/4, pole=False;
# gp = zeros in (0, T0+14 sigma], gn = [-g for g in gp]; print LHS, RHS, |diff| for each tau in TAUS.
```
