# Literature check: variance of block pair statistics of zeta zeros vs GUE/CUE

Date: 2026-10-10. Scope: the published literature only (arXiv, journal pages, author PDFs). No project files were read.

**Question.** Let S_f = Σ_{i≠j} f(x_i − x_j) be computed over a block of b consecutive unfolded zeros, with f a smooth bump a few mean spacings wide. What is known about Var(S_f) across blocks, and how it scales with b (about 10² to 10⁴), compared with the sine-kernel (GUE/CUE) prediction?

**Access legend.** [FULL] means I read the full text (arXiv PDF converted to text, or an OCR'd author PDF). [ABS] means I saw only the abstract or metadata. [NOT ACCESSED] means I saw the paper only through secondary citations. Equation and section numbers are given only for papers marked [FULL].

---

## 0. Bottom line

- **No published paper was found that computes or measures the variance across blocks of a pair statistic Σ_{i≠j} f(γ_i − γ_j) for zeta zeros. None was found on its dependence on block length, and none compares it with GUE/CUE.** The same holds for the empirical pair correlation function and the empirical form factor of zeta zeros.
- **The sine-kernel/CUE side is well covered.** Aguirre–Soshnikov–Sumpter (2021) give a CLT for the microscopic CUE pair statistic. The variance is proportional to N, with an explicit coefficient depending only on f. Earlier work: Soshnikov (1998) on the empirical spacing distribution, Braun–Haake (2015) on the CUE variance of the smoothed correlator, and Prange (1997) heuristically.
- **For zeta, the fluctuation results that exist are for linear statistics only.** These are:
  - Fujii's CLTs;
  - Hughes–Rudnick (mock-Gaussian);
  - Rodgers;
  - Bourgade;
  - Bourgade–Kuan;
  - Maples–Rodgers;
  - Kargin;
  - Berry's number variance.
- **Two zeta results come closest to a pair-type second-order quantity.** Both concern mean correlations, not block-to-block variance of a pair sum:
  - The long-range spacing autocovariances c_k found by Odlyzko (1987). Bohigas–Leboeuf–Sánchez (2001) explained them with a parameter-free prime-sum formula (their Eq. 3.1) and compared it with Odlyzko's data.
  - Rodgers' rigorous mixed moments of mesoscopic linear statistics (2014, Thm 7.6). These cover only band-limited test functions and windows of n = o(log T) zeros.
- **Most direct theory-fixed route:** the Conrey–Snaith (2008) ratios-conjecture formulas for the zeta 2-, 3- and 4-point correlations. They are written out explicitly for n = 2, 3, 4 in their §5.2, §5.4 and §5.6. Inserted into the standard identity Var(S_f) = (4-point + 3-point + 2-point terms) − (mean)², they give a fixed prediction for a given f, block geometry and height. The Bogomolny–Keating (2013) recipe is an alternative way to reach the same higher correlations.
- **No paper found does this computation.**

---

## 1. Fluctuations / self-averaging of pair statistics and the empirical form factor

### 1.1 Prange, "The spectral form factor is not self-averaging"
- Citation: R. E. Prange, Phys. Rev. Lett. 78, 2280 (1997); arXiv:chao-dyn/9606010. [FULL]
- Setup:
  - Two-level function C(x) averaged over an energy window W (Eq. 1); form factor k(t) its Fourier transform (Eqs. 2–3).
  - With a Gaussian window, k(t) = |Σ_a F_a e^{2πi E_a t/Δ}|² (Eq. 4).
- Key claims, quoted:
  - "Insofar as the phases of the individual terms in the sum Eq.(4) are indeed independent random variables, one may show that the distribution of values of y = k(t) is ρ(y) = e^{−y}. (5) This result is independent of the form of F_a and of W, as long as there are many terms … i.e. as long as w ≫ 1." Here w = W/Δ is the number of levels.
  - For smaller t: "ρ(k(t)) = (1/k_E(t)) e^{−k(t)/k_E(t)}, (6) where k_E(t) is the ensemble average form factor."
  - "Increasing W does not change the distribution, but it does make k(t) vary more rapidly."
  - "smearing the time t by an amount τ is like averaging over a number τW/Δ independent choices from the distribution ρ(k(t)). Thus the 'noise' in the smeared function k_τ(t) is reduced by a factor √(1/wτ)."
  - On zeta, p. 1: "the Riemann zeta function … can probably be studied effectively, especially in view of the large database of zeroes obtained by Odlyzko".
  - On zeta, p. 4: "For other systems, particularly the Riemann zeta function, it is likely possible [to confirm or discredit the theoretical predictions of k(t) for t ∼ 1]."
  - On linear transforms: "Certain often used linear transforms of k(t) are self-averaging … Σ²(L) and Δ₃(L)."
- (a) Quantity: the empirical form factor of a single spectrum.
- (b) Type: pair/quadratic.
- (c) Window-size prediction: yes, heuristic. The unsmoothed k(t) has an O(1) relative spread at every W. With smoothing over a width τ in t, the relative noise is about (wτ)^{-1/2}.
  - My inference (not in Prange): a pair statistic with a smooth f of width about one spacing equals ∫ f̂(t) k(t) dt with f̂ of width O(1). In Prange's picture its relative noise is therefore O(b^{-1/2}), i.e. Var(S_f) ∝ b for a random-phase/GUE-like spectrum.
- (d) Zeta data: no. It is only argued that zeta "is likely" an exception, because its non-universal corrections are large.
- (e) Parameter-free formula: only the exponential law and the (wτ)^{-1/2} scaling. There is no arithmetic correction to the noise.

### 1.2 Braun & Haake, "Self-averaging characteristics of spectral fluctuations"
- Citation: P. Braun, F. Haake, J. Phys. A 48, 135101 (2015); arXiv:1410.5299. [FULL]
- Setting: kicked top versus CUE. They compute the CUE variance of the smoothed two-point correlator from an average of eight spectral determinants (a four-point quantity). Covariance in Appendix VIII A, Eq. (14).
- Variance results:
  - Correlator smoothed by an imaginary part η: Var_CUE(Re C(e+iη, δ)) ∼ (1/(2Nη))(…) (Eq. 10). For δ = 0 the text gives "∝ 1/(Nη)". With η ∝ N^{−α}, the variance is "∝ N^{−1+α}, small indeed and suggesting self-averaging".
  - First primitive R^{(1)}(e): explicit large-N form in Eq. (12): "Var_CUE R^{(1)}(e) ∼ 1/N [ … ]". Also: "The scaling with N, Var_CUE R^{(1)}(e) ∼ 1/N, is manifest in the figure."
  - Abstract: the raw form factor and correlator "are not self-averaging. Only suitable smoothing turns them into useful characteristics."
- (a) Quantity: the smoothed two-point correlator and its primitives.
- (b) Type: pair.
- (c) Scaling: yes, 1/N in CUE.
- (d) Zeta data: no; the paper does not mention zeta. Its comparison system is a kicked top.
- (e) Formula: yes for CUE (Eqs. 10, 12, 14).

### 1.3 Aguirre, Soshnikov, Sumpter, "Pair dependent linear statistics for CβE" — the CUE baseline
- Citation: A. Aguirre, A. Soshnikov, J. Sumpter, Random Matrices: Theory Appl. 10(4), 2150035 (2021); arXiv:1912.07110. [FULL]
- Statistic: S_N = Σ_{1≤i≠j≤N} f(L_N(θ_i−θ_j)). The microscopic case L_N = N is the one motivated by Montgomery.
- Theorem 2.5 (β = 2, L_N = N, f ∈ C_c^∞ even):
  - (S_N − E S_N) N^{−1/2} → Gaussian with variance
    (1/π)∫|f̂(t)|² min(|t|,1)² dt − (1/π)∫∫_{|s−t|≤1, |s|∨|t|≥1} f̂(t)f̂(s)(1−|s−t|) ds dt − (1/π)∫∫_{0≤s,t≤1, s+t>1} f̂(s)f̂(t)(s+t−1) ds dt   (Eq. 2.6).
  - Fourier convention: f̂(t) = (2π)^{−1/2}∫ f(x)e^{−itx}dx (Eq. 2.4). Nθ has mean spacing 2π, so rescale f accordingly for unit-spacing unfolding.
- Exact finite-N variance for β = 2: Proposition 4.1 of this paper, reproduced as Eq. (2.1) of Aguirre–Soshnikov, arXiv:2004.01345 [FULL]:
  Var S_N(f) = 4Σ_{1≤s≤N−1} s²|f̂(s)|² + 4(N²−N)Σ_{s≥N}|f̂(s)|² − (two off-diagonal terms).
- Mean: Remark 2.2, Eq. (2.3): E S_N = f̂(0)N² − f(0)N + Σ_k f̂(k) min(|k|,N).
- The introduction links the statistic to Soshnikov's CLT for the empirical nearest-neighbour spacing distribution: "(#{j: τ_j ≤ s} − E#…) N^{−1/2} converges … to a Gaussian random process". Ref: A. Soshnikov, "Level spacings distribution for large random matrices: Gaussian fluctuations", Ann. Math. 148 (1998) 573–617 [NOT ACCESSED beyond this citation].
- (a) Quantity: exactly the user's statistic, for CUE over the full circle.
- (b) Type: pair.
- (c) Scaling: yes. Var ∝ N, with the constant given by Eq. 2.6.
- (d) Zeta data: none.
- (e) Formula: yes, parameter-free in f.
- Caveat: N is the full CUE circle, which is periodic with no edges. A block of b zeros is a window of a stationary process, so boundary terms can differ. I found no paper that treats the sine-process window version explicitly.

### 1.4 Other RMT form-factor fluctuation literature (context; not zeta)
- H. Kunz, "The probability distribution of the spectral form factor in random matrix theory", J. Phys. A 32, 2171 (1999). [NOT ACCESSED]
- E. Brézin, S. Hikami, "Spectral form factor in a random matrix theory", PRE 55, 4067 (1997); arXiv:cond-mat/9608116. [ABS] It treats the mean S(τ) at finite N.
- G. Cipolloni, L. Erdős, D. Schröder, "On the spectral form factor for random matrices", arXiv:2109.06712. [ABS] It covers Wigner matrices.
- A. Altland et al., "Statistics of the random matrix spectral form factor", Phys. Rev. Research 7, 033138 (2025); arXiv:2503.21386. [ABS] It covers non-Gaussian corrections, D^{−1} expansion. None of these four mentions zeta, as far as the abstracts show.

### 1.5 Zeta-specific: window invariance of a smoothed density autocorrelation (Lu–Sridhar)
- Citation: W. T. Lu, S. Sridhar, "Correlations among the Riemann zeros: Invariance, resurgence, prophecy and self-duality", arXiv:nlin/0405058 (2004). [Read only through a summarising fetch of the HTML; treat quotes as approximate.]
- Statistic: the autocorrelation of the fluctuating part of a Gaussian-smoothed density, in raw (un-unfolded) units at long lags. Windows were 10⁴ zeros near 10¹², 10²¹ and 10²², plus 5 windows in the first 10⁵ zeros.
- Claim: "The spectral auto-correlation is invariant w.r.t. the averaging window." The 5 low windows "collapse to the same curve" with relative difference "less than 0.1%".
- (a) Quantity: a mean long-range pair quantity dominated by deterministic arithmetic "resurgence" peaks at lags equal to low zeros.
- (b) Type: pair.
- (c) Window-size scaling of the fluctuations: none. No GUE comparison of the fluctuations.
- (d) Zeta data: yes.
- (e) Formula for the variance: no.

### 1.6 Zeta-specific: long-range spacing autocovariances (the closest pair-type second-order data)
- **Odlyzko (1987)**: A. M. Odlyzko, "On the distribution of spacings between zeros of the zeta function", Math. Comp. 48, 273–308 (1987). [FULL, OCR]
  - Definition, §2 Eq. (2.28): c_k(N,M) = (1/M)Σ_{n=N+1}^{N+M}(δ_n−1)(δ_{n+k}−1).
  - Dyson's GUE guess, Eq. (2.29): c_k ≈ −1/(2π²k²).
  - Observed: "Since the variance of the δ_n is around 1/6, random independent δ_n would give values of c_k around (6√10⁵)^{−1} ≈ 0.00053. The values in Table 5 are typically much larger than that, and therefore statistically significant."
  - The "spectrum of the δ_n" (Figs. 13–14), computed over 98,303 zeros at N = 10¹², shows sharp lines: "The peaks of f(x) occur near x = 2(log N)/log q, where q is a prime power". The text is OCR-garbled here; see the original.
  - Moments of the spacing statistics in blocks of 10⁵ zeros at several heights are compared with GUE (Tables 1–4). There is no variance-versus-block-length study.
- **Bohigas, Leboeuf & Sánchez (2001)**: O. Bohigas, P. Leboeuf, M. J. Sánchez, "Spectral spacing correlations for chaotic and disordered systems", Found. Phys. 31, 489 (2001); arXiv:nlin/0012049. [FULL]
  - Spacing autocovariances "can be viewed as a discretized two point correlation function".
  - For zeta, Eq. (3.1): C(n) = (2/π²)Σ_{p,r} sin²(πrτ_p)/(r²p^r) · cos(2πnrτ_p), with τ_p = log p/log(t/2π).
  - "In Figs. 2 and 3 the theoretical prediction (3.1) is compared with numerical values ('data') computed by Odlyzko. The agreement is good, although some small deviations remain. Important differences with respect to the RMT result are observed already at n ≈ 3."
  - For 50 < n < 500: "a dominant small positive correlation 'punctuated' by large peaks of anti-correlation".
- (a) Quantity: the mean covariance of spacings at lag k. This is a mean pair-type statistic.
  - My inference: Σ_k (b−|k|) Cov(g_n, g_{n+k}) is exactly the block variance of a spacing-sum statistic Σ_n g(δ_n). So these covariances are the ingredient for the block variance of a nearest-neighbour statistic. Neither paper forms that sum or treats a general g or f.
- (b) Type: pair-type.
- (c) Block-length prediction: not stated.
- (d) Zeta data: yes (Odlyzko).
- (e) Formula: Eq. (3.1) is parameter-free, but only for c_k of the raw spacings. It is a diagonal-approximation semiclassical result.

### 1.7 Forrester & Mays; Bogomolny–Bohigas–Leboeuf–Monastra (mean corrections, effective N)
- **Bogomolny, Bohigas, Leboeuf, Monastra (2006)**: E. Bogomolny, O. Bohigas, P. Leboeuf, A. G. Monastra, J. Phys. A 39, 10743 (2006); arXiv:math/0602270. [ABS]
  - Leading finite-height deviations of the spacing distribution equal those of CUE with N_eff = log(E/2π)/√(12Λ), Λ = 1.57314….
- **Forrester & Mays (2015)**: P. J. Forrester, A. Mays, "Finite size corrections in random matrix theory and Odlyzko's data set for the Riemann zeros", Proc. R. Soc. A 471 (2015); arXiv:1506.06531. [FULL intro and §2]
  - Empirical two-point function from Odlyzko's 10⁹ zeros near 10²³, compared with the Bogomolny–Keating two-point formula: "Very good agreement is found for distances up to approximately one and a half times the average spacing between zeros, after which systematic deviation is observed."
  - On higher correlations: "While higher order correlations cannot be measured empirically from the Riemann zeros data, this hypothesis [CUE(N_eff) corrections persist to all orders] becomes predictive…"
- Both treat mean statistics only; no fluctuation or block-length study.
  - My note: N_eff is only about 10 at 10²³, so the CUE(N_eff) device is a microscopic-correction model. It cannot represent correlations across blocks of 10²–10⁴ zeros.

### 1.8 Coram & Diaconis (2003)
- Citation: M. Coram, P. Diaconis, "New tests of the correspondence between unitary eigenvalues and the zeros of Riemann's zeta function", J. Phys. A 36, 2883–2906 (2003). [NOT ACCESSED: the PDF was unreachable.]
- Secondary descriptions:
  - Forrester–Mays: they "used the random unitary matrix model to predict the functional form of the covariance between the number of eigenvalues in overlapping intervals of equal size".
  - Bourgade (2010): their Odlyzko-data tests "suggested that the correlation structure … should appear when counting the zeros".
- On those descriptions: linear (counting) statistics; matched against CUE blocks; data comparison yes. I cannot confirm whether any pair statistic was tested.

---

## 2. Higher correlations with arithmetic lower-order terms

### 2.1 Bogomolny & Keating, RMT and the Riemann zeros I and II
- **Paper I**: "Random matrix theory and the Riemann zeros I: three- and four-point correlations", Nonlinearity 8, 1115–1131 (1995); doi:10.1088/0951-7715/8/6/013. [ABS only]
  - Abstract: "the 3-point and 4-point zero correlation functions are asymptotically equivalent to the corresponding GUE results", via the explicit formula plus the Hardy–Littlewood conjecture.
- **Paper II**: "… II: n-point correlations", Nonlinearity 9, 911–935 (1996). [ABS only]
  - Abstract: "for all n the n-point correlation function of the zeros is equivalent to the corresponding GUE result in the appropriate asymptotic limit".
- I could not check whether paper I writes out arithmetic lower-order 4-point terms in usable form.
  - Conrey–Snaith (2008, intro) say of Bogomolny–Keating: "They gave full details for the lower order terms for the 2-point correlation … whereas for three and higher correlations, they outlined several methods which lead to these lower order terms."
- No fluctuation or variance content is indicated in either abstract.

### 2.2 Bogomolny & Keating (2013)
- Citation: "A method for calculating spectral statistics based on random-matrix universality with an application to the three-point correlations of the Riemann zeros", J. Phys. A 46, 305203 (2013); arXiv:1307.6012. [FULL]
- Recipe (§IV, summarised in §VII):
  - Kernel K(E_i,E_j) = sin(π(N̄(E_i,p*) − N̄(E_j,p*)))/(π(E_i−E_j)) (Eq. 27). N̄ includes the oscillatory contributions of primes p < p* (Eqs. 25, 86).
  - Correlations R_n = ⟨⟨det K(E+e_i, E+e_j)⟩⟩_ΔE (Eqs. 28, 87).
  - Window conditions "1 ≪ p* ≪ ΔE ≪ E" (Eq. 30). The phases E ln p are treated as independent uniform random phases (Eqs. 34, 88).
  - Divergent prime products are regularised by ∏_{p<p*}(1−p^{−1})/(1−p^{−1−s}) → sζ(1+s) (Eqs. 39, 89).
- Explicit results: two-point (Eqs. 90–92) and three-point (Eqs. 93–95). The authors say both their method and Conrey–Snaith's "are general, permit to calculate, in principle, all correlation functions".
- The 4-point function is NOT written out, and there is no variance or fluctuation content.
- (a) Quantity: mean n-point functions.
- (b) Type: correlations (pair and higher).
- (c) Window-size prediction: none.
- (d) Zeta data: none in this paper, which defers to Forrester–Mays etc.
- (e) Formula: yes, a parameter-free recipe for any n.
  - My inference: the model is "determinantal given the small-prime phases, with the phases random". A block variance would therefore split into a within-block determinantal part plus a between-block part from prime-phase modulation of the local density. This is an inference from the model's structure, not a published result.

### 2.3 Conrey & Snaith, "Correlations of eigenvalues and Riemann zeros"
- Citation: J. B. Conrey, N. C. Snaith, Commun. Number Theory Phys. 2(3), 477–536 (2008); arXiv:0803.2795. [FULL]
- Assumptions: RH and the Conrey–Farmer–Zirnbauer ratios conjecture.
- Main theorem (Theorem 9, Eq. 163; Corollary 2, Eq. 166): for translation-invariant f,
  Σ_{0<γ_1≠…≠γ_n≤T} f(γ_1,…,γ_n) = (1/T)∫_0^T (2π)^{−n}∫_{[−T,T]^n} Σ_{K+L+M={1..n}} J*_{ζ,t}(−iz_K+it; iz_L−it; iz_M−it) f(z) dz dt + O(T^{1/2+ε}).
- Test-function conditions (Eq. 154):
  - f holomorphic for |Im x_j| < 2;
  - translation-invariant;
  - f(0,x_2,…,x_n) ≪ 1/(1+|x_2|²+…+|x_n|²).
  - Consequence: a sharp block indicator is not admissible; a smooth window (e.g. Gaussian or holomorphic) is.
- **Explicit n = 2, 3, 4 for zeta, answering item 2 directly: yes.** §5 opens: "we explicitly write out all of the terms in our expressions for n-correlations for RMT eigenvalues and for ζ-zeros for 2 ≤ n ≤ 4". The ζ forms use the approximation χ'/χ ≈ −log(t/2π) = −ℓ (Eqs. 107, 162).
  - Pair, §5.2: J*_{ζ,t}(a;b) = (ζ'/ζ)'(1+a+b) − B(a+b) + e^{−ℓ(a+b)}ζ(1+a+b)ζ(1−a−b)A(a+b) (Eq. 178), with A, B as in Eqs. 179–180. Then R_{ζ,t,2} = ℓ² + J*(iu;−iv) + J*(−iu;iv) (Eq. 181), which they "conjecture". Equivalently J* = P_1 + P_2 (Eqs. 182–184).
  - Triple, §5.4: Eqs. 191–192 plus B_1 (Eq. 213).
  - Quadruple, §5.6, "We conjecture that R_{ζ,t,4}(u,v,w,y) = ℓ⁴ + ℓ²(…12 two-point J*…) + ℓ(…24 three-point J*…) + (8 terms J*({a},{b_1,b_2,b_3}) and conjugates) + (6 terms J*({a_1,a_2},{b_1,b_2}))" (Eq. 201). The new building blocks:
    - J*({a},{b_1,b_2,b_3}) (Eq. 202), with W_1 and B_2 (Eqs. 203–204);
    - J*({a_1,a_2},{b_1,b_2}) (Eq. 205), with A* (Eq. 206), W, B_3, C, B_4 (Eqs. 207–209);
    - auxiliary functions collected in §5.7 (Eqs. 210ff).
  - Some ingredients (Z_ζ, Z_ζ†, P_3) are defined earlier in the paper. I did not check every definition for completeness.
- Fluctuations: the paper does not use these formulas for any variance or fluctuation question. Its stated application is "lower order terms in the nearest neighbor spacing".
- (a) Quantity: mean n-point correlations (t-averaged) with all arithmetic lower-order terms.
- (b) Type: n-point.
- (c) Window-size prediction: none stated.
- (d) Zeta data: none in this paper.
- (e) Formula: yes, conditional on RH and the ratios conjecture. In principle it can be evaluated for any admissible f, but the 4-point evaluation involves 4-fold integrals of prime sums and products. See §6 for the variance assembly.

### 2.4 Conrey & Snaith, triple correlation
- Citation: "Triple correlation of the Riemann zeros", J. Théor. Nombres Bordeaux 20, 61–106 (2008); arXiv:math/0610495. [NOT ACCESSED; cited by CS 2008 and BK 2013]

### 2.5 Has anyone used 4-point correlations to compute the variance of a pair statistic for zeta zeros?
- **Not found.** Searches combining "four-point/quadruple correlation", "variance", "pair statistic/pair correlation" and "Riemann/zeta" returned nothing of the kind.
- The only rigorous related result is Rodgers (2014), Thm 7.6 (§3.3 below). It covers mixed moments of band-limited mesoscopic linear statistics, which formally include the second moment of a band-limited pair statistic. It does not cover a compactly supported f or b ≫ log T.

---

## 3. Mesoscopic fluctuations and CLTs for zeta zeros (all linear unless stated)

### 3.1 Fujii (via secondary sources)
- Citation: A. Fujii, "On the zeros of Dirichlet L-functions I", Trans. AMS 196 (1974) 225–235. [NOT ACCESSED; statements as quoted in Rodgers 2014 and Hughes–Rudnick 2002]
- Mesoscopic (Rodgers Thm 1.1): Δ = N(t+2πn/log T) − N(t), with n → ∞ and n = o(log T). Then Var Δ ∼ (1/π²) log n, and the CLT holds.
- Macroscopic (Rodgers Thm 1.6): log T ≲ n(T) ≲ T gives Var(S(t+2πn/log T) − S(t)) ∼ (1/π²) log log T.
- Hughes–Rudnick (2002) quote Fujii's version for h → ∞, h ≪ T: "σ² is replaced by σ² = (1/π²)(log log T − log|ζ(1+ih)|)".
- (b) Type: linear (counting).
- (c) Window-size prediction: yes, with an explicit arithmetic dependence through ζ(1+ih).
- (e) Formula: yes, for counts only.

### 3.2 Hughes & Rudnick, "Linear statistics for zeros of Riemann's zeta function"
- Citation: C. P. Hughes, Z. Rudnick, C. R. Acad. Sci. Paris 335, 667–670 (2002); arXiv:math/0208220. [FULL]
- Theorem 1.1: N_f(τ) = Σ_j f((log T/2π)(γ_j−τ)) with supp f̂ ⊆ (−2a/m, 2a/m), averaged over a window H = T^a. The first m moments are Gaussian, with σ_f² = ∫ min(|u|,1) f̂(u)² du (Eq. 1). This is mock-Gaussian behaviour.
- (b) Type: linear only, microscopic scale.
- (c) Window-size prediction: no; the window enters only through which moments are Gaussian.
- (d) Zeta data: no.
- (e) Formula: yes, but only for band-limited f.
- RMT analogue: C. P. Hughes, Z. Rudnick, "Mock-Gaussian behaviour for linear statistics of classical compact groups", J. Phys. A 36, 2919 (2003). [NOT ACCESSED]

### 3.3 Rodgers, "A central limit theorem for the zeroes of the zeta function"
- Citation: B. Rodgers, Int. J. Number Theory 10, 483–511 (2014); arXiv:1205.0303. [FULL]
- Theorem 1.2: for compactly supported η of bounded variation with divergent ∫|x||η̂|², Var(Σ_γ η((log T/2πn)(γ−t))) ∼ ∫_{−n}^{n}|x||η̂(x)|² dx, plus a CLT. This holds in the mesoscopic regime n = o(log T).
- Theorem 1.3 covers the convergent-variance case.
- Appendix §7:
  - Theorem 7.1 (Rudnick–Sarnak, support |x_1|+…+|x_k| < 2).
  - Theorem 7.6: for wave-packet statistics Δ_ℓ = Σ r(ξ_i/n(T)) e(α_ℓ ξ_i), with |α_1|+…+|α_k| ≤ A < 2, mixed central moments agree with the sine process up to o(1) terms. The paper says this gives "covariance statements for translated linear statistics separated by mesoscopic distances".
- (b) Type: linear. Thm 7.6 gives products of linear statistics, so formally it covers band-limited quadratic statistics.
  - My inference: a pair sum with f̂ supported in |α| < 1/2 has a second moment that is a k = 4 product with Σ|α| < 2.
- (c) Window-size prediction: yes for linear statistics (the log n growth). For pair statistics, only through this inference, and only for n = o(log T).
- (d) Zeta data: no.
- (e) Formula: yes for linear statistics.

### 3.4 Maples & Rodgers
- Citation: K. Maples, B. Rodgers, "Bootstrapped zero density estimates and a central limit theorem for the zeros of the zeta function", Int. J. Number Theory 11, 2087–2107 (2015); arXiv:1404.3080. [ABS]
- Content: an unconditional CLT for linear statistics with growing variance. Linear only.

### 3.5 Bourgade, "Mesoscopic fluctuations of the zeta zeros"
- Citation: P. Bourgade, Probab. Theory Relat. Fields 148 (2010); arXiv:0902.1757. [FULL]
- Content: a multidimensional Selberg CLT for log ζ at mesoscopically separated points (Thm 1.1, covariance 1 ∧ c_{i,j}, Eq. 1.6). Corollary 1.3 covers correlated counting fluctuations.
- "This confirms numerical experiments by Coram and Diaconis [1], who after making extensive tests (based on data by Odlyzko) suggested that the correlation structure … should appear when counting the zeros".
- (b) Type: linear (counts / log ζ).
- (c) Window-size dependence: yes, through log-scale separations.
- (d) Zeta data: indirect, via Coram–Diaconis.

### 3.6 Bourgade & Kuan, "Strong Szegő asymptotics and zeros of the zeta function"
- Citation: P. Bourgade, J. Kuan, Comm. Pure Appl. Math. 67, 1028–1044 (2014); arXiv:1203.5328. [ABS]
- Content: linear statistics converge to a Gaussian field with H^{1/2} covariance. Linear only.

### 3.7 Kargin
- "On fluctuations of Riemann's zeta zeros", Probab. Theory Relat. Fields 157, 575–604 (2013); arXiv:1203.5309. [ABS] Gaussian fluctuations of individual zeros about their predicted locations; bivariate Gaussian for pairs at logarithmic separation.
- "Statistical properties of zeta functions' zeros", Probab. Surveys 11, 121–160 (2014); arXiv:1302.1452 [survey; skimmed].
- Linear/positional quantities only.

**Linear versus pair, explicitly:** every CLT and fluctuation result for zeta zeros listed in §3 is for linear statistics. The only exception is the formal reach of Rodgers' Thm 7.6 (band-limited, n = o(log T)). No published CLT or variance formula for zeta pair statistics was found.

---

## 4. Berry: number variance and saturation; Bogomolny–Keating beyond the diagonal approximation

### 4.1 Berry, "Semiclassical formula for the number variance of the Riemann zeros"
- Citation: M. V. Berry, Nonlinearity 1, 399–407 (1988). Author PDF berry175. [FULL, OCR]
- V(L;x) is expressed through the form factor (Eqs. 8–9). With the diagonal approximation for short "orbits" (primes) plus the GUE form factor for long ones (Eq. 15), he gets Eq. (19).
- GUE behaviour holds for L ≪ L_max = ln(E/2π)/(2π ln 2). Beyond that there are "quasirandom oscillations about the mean value π^{−2}(ln ln(E/2π) + 1.4009)" (abstract; Eq. 23).
- Compared with Odlyzko's 10⁵ zeros at x = 10¹² (E = 2.677×10¹¹): L_max = 5.62; longest oscillation wavelength ΔL = 35.31; asymptotic mean 0.4659. Verdict: agreement "to within the limits of graphical precision".
- Here x-averaging is "asymptotic averaging … over a range Δx satisfying 1 ≪ Δx ≪ x".
- (a) Quantity: the mean number variance at a given height.
- (b) Type: the variance of a linear statistic. Through Eq. 9 it is an integral of the mean form factor.
- (c) Window-size prediction: yes in L (saturation), but for counts only. There is nothing on block-to-block fluctuations of V or of any pair statistic.
- (d) Zeta data: yes.
- (e) Formula: yes, parameter-free for V(L).
- Scale note (arithmetic from Berry's numbers): blocks of b ≥ 10² zeros are far beyond L_max ≈ 6 at E ≈ 10¹¹, i.e. in Berry's non-universal regime for counts.

### 4.2 Berry, "Semiclassical theory of spectral rigidity"
- Citation: M. V. Berry, Proc. R. Soc. A 400, 229–251 (1985).
- Status: [NOT READ: the author PDF berry140 is an image scan with no text layer, and no renderer was available.] I cannot say whether it discusses form-factor noise.

### 4.3 Bogomolny & Keating, PRL 1996
- Citation: E. B. Bogomolny, J. P. Keating, "Gutzwiller's trace formula and spectral statistics: beyond the diagonal approximation", Phys. Rev. Lett. 77, 1472–1475 (1996). [NOT ACCESSED: APS 403]
- Secondary sources (CS 2008 and BK 2013 intros) describe it as deriving the arithmetic lower-order terms in the mean two-point function and comparing with Odlyzko's data.
- Prange (1997) comments on its ensemble-free derivation: "The 'noise' in the Bogomolny-Keating formulation thus presents a deep question". Nothing I could access indicates that BK treated fluctuations of pair statistics.

### 4.4 Berry & Keating, SIAM Review (1999)
- Citation: M. V. Berry, J. P. Keating, "The Riemann zeros and eigenvalue asymptotics", SIAM Review 41, 236–266 (1999). [NOT READ: scanned PDF, no text layer.]

### 4.5 Lugar, Milinovich, Quesada-Herrera
- Citation: "On the number variance of zeta zeros and a conjecture of Berry", arXiv:2211.14918 (Mathematika). [ABS]
- Content: proves Berry's conjecture in the non-universal regime, assuming RH and auxiliary hypotheses. Linear statistic; mean variance only.

---

## 5. Montgomery's F(α) as an empirical / fluctuating quantity
- **Definition**, as in Odlyzko (1987) Eqs. (1.1)–(1.3) [FULL] and Aguirre–Soshnikov–Sumpter's introduction [FULL]:
  - F(α,T) = 2π(T log T)^{−1} Σ_{0<γ,γ'≤T} T^{iα(γ−γ')} w(γ−γ'), with w(u) = 4/(4+u²).
  - Theorem (on RH): F = (1+o(1))T^{−2α}log T + α + o(1) for 0 ≤ α ≤ 1.
  - Conjecture: F = 1 + o(1) for α ≥ 1.
  - Montgomery's 1973 paper itself was not opened.
- **Rodgers (2013)**, "Macroscopic pair correlation of the Riemann zeroes for smooth test functions", Q. J. Math. 64, 1197–1219; arXiv:1203.3275. [ABS] On RH, the Bogomolny–Keating pair measure matches the true pair correlation, to a very small error, for sufficiently smooth (band-limited) test functions. This concerns the mean.
- **Not found:** any paper treating F(α), or a windowed or local version, as a random quantity over windows of height, with its variance or distribution. This holds for both α < 1 (prime-determined) and α > 1.
- The nearest material:
  - Prange's general statements (§1.1). An empirical form factor from w levels at fixed t ≳ 1 has an exponential distribution, independent of w. Smoothing over τ reduces the relative noise as (wτ)^{−1/2}. For t < 1 the distribution is (1/k_E)e^{−k/k_E}.
  - Odlyzko's (1987) "spectrum of the δ_n" and exponential sums Σ e^{iγ_n y} over 4×10⁴ zeros (Fig. 15), which peak at y ≈ log p^m.
- The Goldston–Montgomery equivalence (pair correlation ⟺ variance of primes in short intervals) concerns mean quantities [NOT ACCESSED; cited in several sources].
- (c) Window-size prediction for zeta specifically: none found.

---

## 6. Summary and most direct routes to a theory-fixed prediction

**Has the block-length dependence of Var(S_f) for zeta zeros, relative to GUE, been described before?** As far as this search found: **no.** Some pieces exist partially:

1. **GUE/CUE side (done).**
   - Aguirre–Soshnikov–Sumpter 2021, Thm 2.5 / Eq. 2.6: Var ∝ N, explicit constant. Exact finite-N formula in Prop 4.1 (= Aguirre–Soshnikov Eq. 2.1).
   - Soshnikov 1998: empirical spacing distribution, N^{−1/2} Gaussian fluctuations.
   - Braun–Haake 2015: CUE variance of the smoothed correlator ∼ 1/N.
   - Prange 1997: heuristic (wτ)^{−1/2}.
2. **Zeta, mean pair-type second-order structure with data.**
   - Odlyzko 1987: long-range spacing autocovariances, far above the independent-noise level, with prime-power spectral lines.
   - Bohigas–Leboeuf–Sánchez 2001, Eq. 3.1: parameter-free prime-sum formula for these autocovariances, checked against Odlyzko.
   - These are the ingredients of a block variance for spacing-based statistics, but nobody has assembled them into Var vs b.
3. **Zeta, fluctuation theory exists for linear statistics only.** Fujii; Hughes–Rudnick; Rodgers; Maples–Rodgers; Bourgade; Bourgade–Kuan; Berry's number variance with saturation beyond L_max ≈ ln(E/2π)/(2π ln 2).
   - The user's b = 10²–10⁴ spans raw height h = 2πb/log(T/2π) ≫ 1 at any practical height. That is outside Rodgers' mesoscopic regime (n = o(log T)) and inside the regime where Fujii's linear variance carries −log|ζ(1+ih)| and Berry's V(L) has saturated. No pair-statistic analogue of either has been published.

**Most direct published routes to a theory-fixed prediction (none yet executed in the literature):**

- **(A) Conrey–Snaith 2008 n = 2, 3, 4 formulas.** Theorem 9 / Corollary 2, explicit in §5.2 (Eqs. 178–184), §5.4 (Eqs. 191–192, 213) and §5.6 (Eqs. 201–209), with auxiliary functions in §5.7.
  - Use the standard expansion of E[S_f²] for a smoothly windowed pair sum. Write W(·) for a smooth block window; translation invariance is restored by averaging the window position over t. Then E[S_f²] = 4-distinct-zero term (R_4) + 3-distinct terms (R_3, from one shared index, 4 ways) + 2-distinct terms (R_2, from both indices shared, 2 ways). Subtract (E S_f)² from R_2.
  - This assembly is standard combinatorics. It is my description, not a formula from the paper.
  - Conditional on RH and the ratios conjecture. Requires test functions holomorphic in |Im| < 2 (Eq. 154), so use a smooth window, not a sharp block. Error O(T^{1/2+ε}).
  - This is the only published source I found with the explicit arithmetic 4-point function of zeta zeros.
- **(B) Bogomolny–Keating 2013 recipe**, extended to n = 4 (Eqs. 27–30, 34, 39 / 85–89).
  - Determinantal kernel with a small-prime-modulated density, averaged over independent prime phases. The authors state the method yields all n. Only n = 2, 3 are written out.
  - Its structure (determinantal conditional on prime phases) may make a within-block versus between-block decomposition of Var(S_f) natural; that is my inference, not theirs.
- **(C) Diagonal-approximation semiclassics** in the style of Berry 1988 / Bohigas–Leboeuf–Sánchez 2001.
  - Quickest to evaluate, and validated against Odlyzko data for V(L) and c_k. But it is an approximation: it is diagonal in prime pairs, and the 4-point off-diagonal terms are exactly what Bogomolny–Keating and Conrey–Snaith add.
- **Baseline for comparison:** Aguirre–Soshnikov–Sumpter Eq. 2.6, or the finite-N Prop 4.1. Mind the 2π spacing convention and CUE periodic-versus-window edge effects.

---

## Sources (URLs used)
- Prange 1997 — https://arxiv.org/abs/chao-dyn/9606010
- Braun & Haake 2015 — https://arxiv.org/abs/1410.5299
- Aguirre, Soshnikov, Sumpter 2021 — https://arxiv.org/abs/1912.07110
- Aguirre & Soshnikov 2020 — https://arxiv.org/abs/2004.01345
- Bogomolny & Keating 2013 — https://arxiv.org/abs/1307.6012
- Conrey & Snaith 2008 (CNTP) — https://arxiv.org/abs/0803.2795 ; journal: https://www.doi.org/10.4310/CNTP.2008.V2.N3.A1
- Bogomolny & Keating 1995 (I) — https://iopscience.iop.org/article/10.1088/0951-7715/8/6/013 (abstract only)
- Bogomolny & Keating 1996 (II) — https://iopscience.iop.org/article/10.1088/0951-7715/9/4/006 (abstract only)
- Rodgers 2014 CLT — https://arxiv.org/abs/1205.0303
- Rodgers 2013 macroscopic pair correlation — https://arxiv.org/abs/1203.3275
- Maples & Rodgers 2015 — https://arxiv.org/abs/1404.3080
- Hughes & Rudnick 2002 — https://arxiv.org/abs/math/0208220
- Bourgade 2010 — https://arxiv.org/abs/0902.1757
- Bourgade & Kuan 2014 — https://arxiv.org/abs/1203.5328
- Kargin 2013 — https://arxiv.org/abs/1203.5309 ; Kargin 2014 survey — https://arxiv.org/abs/1302.1452
- Berry 1988 — https://michaelberryphysics.files.wordpress.com/2013/07/berry175.pdf
- Berry publications list — https://michaelberryphysics.wordpress.com/publications/
- Odlyzko 1987 — https://www.physics.rutgers.edu/grad/682/papers/zeta.pdf
- Bohigas, Leboeuf, Sánchez 2001 — https://arxiv.org/abs/nlin/0012049
- Bogomolny, Bohigas, Leboeuf, Monastra 2006 — https://arxiv.org/abs/math/0602270
- Forrester & Mays 2015 — https://arxiv.org/abs/1506.06531
- Lu & Sridhar 2004 — https://arxiv.org/abs/nlin/0405058
- Lugar, Milinovich, Quesada-Herrera — https://arxiv.org/abs/2211.14918
- Brézin & Hikami 1997 — https://arxiv.org/abs/cond-mat/9608116
- Cipolloni, Erdős, Schröder — https://arxiv.org/abs/2109.06712
- Altland et al. 2025 — https://arxiv.org/abs/2503.21386
- Arias de Reyna & Rodgers (GUE-hypothesis equivalences, mean statistics only) — https://arxiv.org/abs/2311.13441
