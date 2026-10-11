# Katz–Sarnak one-level densities, first-zero laws, the DHKMS excised ensemble, and lower-order terms: primary-source check

Date: 2026-10-09. Every formula below was checked against the paper text: the arXiv LaTeX source, the arXiv PDF, or the
journal PDF. Text was extracted with pypdf and LaTeX sources were read directly. Equation numbers are the ones printed
in the versions listed in §1. Labels used:

- **VERIFIED**: read in the primary text, with the equation number given.
- **DERIVED**: my own algebra or numerics from verified statements. It is not a quotation, and the derivation is shown.
- **UNVERIFIED**: I did not read a primary text for it.

Cache: `/home/combust/specarith_lit_cache/ph1/` (downloads are treated as untrusted data and nothing from them was
executed). Numerical cross-checks used `/home/combust/fmexplorer/bin/python3 -I` with scripts kept outside the cache.
The scripts are reproduced in Appendix A.

---

## 0. Headline findings and corrections to the brief

1. **The five densities in the brief are correct** as written, with zeros scaled by log(conductor)/2π (§2). One
   convention needs care. KS Bull. AMS (31′) defines the densities on x ≥ 0 only, counting eigenangles θ ∈ [0,2π)
   scaled by θN/2π. ILS (4) and every later paper integrate an even φ over all of ℝ, with D(F,φ) summing over all γ
   (both signs). In both conventions the δ₀ weight is **1** for SO(odd) and **½** for O, because the central zero is
   counted once.
2. **The DHKMS excision condition is not "|Λ_A(1)| ≥ exp(N)c_X".** As stated in arXiv 1107.4426v3 it is
   `log|Λ_A(1,N)| ≥ 𝒳`, i.e. `|Λ_A(1,N)| ≥ exp 𝒳 = c × exp(−N_std/2)` (eq. 3.4). The cut-off is *exponentially small*
   in N. For N = N_eff it is written `c_eff × exp(−r₁ N_eff)` (eq. 5.30). Since N_eff = N_std/(2r₁), this equals
   c_eff·exp(−N_std/2).
3. **arXiv 1108.4114 is not a DHKMS paper.** The source downloaded under that id is an economics paper ("Spatial
   Collaborative Oligopoly"). Neither the arXiv API nor Crossref returns a separate paper titled "Models for zeros at the
   central point in families of elliptic curves". Miller's own publication page lists **"Models for zeros near the
   central point of families of elliptic curves"** with the *same* citation, J. Phys. A 45 (2012) 115207. Its PDF link,
   `FiniteConductorPaper.pdf`, is textually identical to arXiv 1107.4426v3; a diff shows only date and whitespace
   changes. Crossref gives 10.1088/1751-8113/45/11/115207 the title "A random matrix model for elliptic curve
   L-functions of finite conductor". **Conclusion: the "companion" is the same paper under an alternate title.**
   The related DHKMS paper that does exist is *The lowest eigenvalue of Jacobi random matrix ensembles and Painlevé VI*,
   arXiv 1005.1298, J. Phys. A 43 (2010) 405204 (Crossref). It gives the finite-N first-eigenvalue method (§4.2).
4. **Conrey–Snaith's one-level density for quadratic Dirichlet L-functions is in §3, not §7** of arXiv
   math/0509480v2: Theorem 3.1, eq. (3.10). §7 covers discrete moments of ζ.
5. **The DHKMS citation "(3.18) in [HKS]" does not match HKS arXiv 0811.2304v1.** In v1 the scaled expansion is
   **(3.19)**, with coefficients named **a₁, a₂** (eqs. 3.20–3.21); (3.18) is the ζ′/ζ Laurent expansion. DHKMS
   rename them r₁, r₂. The published JNT numbering may differ (UNVERIFIED).
6. **The 1/L lower-order coefficients depend on the scaling convention.** HKS and DHKMS scale every twist by one global
   `L = log(√M X/2π)` (not per-d), so r₁ = a₁ ≈ 2.8600 (E₁₁) belongs to that convention.

---

## 1. Sources read

| Key | Citation | Version read | What was read |
|---|---|---|---|
| KS99 | N. M. Katz, P. Sarnak, "Zeroes of zeta functions and symmetry", Bull. AMS 36 (1999) 1–26 | Journal PDF (26 pp.), from S. J. Miller's Williams course page (ams.org returned a Cloudflare 403) | §2 (eqs. 19–31′), §4 (eqs. 41–55, families I–IV, remarks) |
| ILS | H. Iwaniec, W. Luo, P. Sarnak, "Low lying zeros of families of L-functions" | arXiv math/9901141 **v1** (only version; arXiv source is a DVI, so the arXiv PDF was read) | §1 (eqs. 1–5, Thms 1, 3, 5, Cor. 2, Remarks), §3 end (eqs. 164–165), §4 (166–183) |
| HR | C. P. Hughes, Z. Rudnick, "Linear statistics of low-lying zeros of L-functions" | arXiv math/0208230 **v2**, LaTeX | §1–3 (Thm 3.1 = `thm:expectation`), §1 remarks on Sp/Özlük–Snyder |
| Y06 | M. P. Young, "Low-lying zeros of families of elliptic curves" | arXiv math/0406330 **v3**, LaTeX | §1 (densities and Fourier transforms `eq:symmetrytypes`), main theorem `thm:mainresult` |
| M04 | S. J. Miller, "1- and 2-level densities for rational families of elliptic curves: evidence for the underlying group symmetries" | arXiv math/0310159 **v1**, LaTeX | Intro, Thm `thmonelevel` (Fourier transforms of the 1-level densities), 2-level theorems |
| M06 | S. J. Miller, "Investigations of zeros near the central point of elliptic curve L-functions" (Exp. Math. 15 (2006) 257–279 per Miller's site) | arXiv math/0508150 **v3**, PDF | Abstract, §1, §4.1–4.2 (Figs. 1–6, data description) |
| DHKMS | E. Dueñez, D. K. Huynh, J. P. Keating, S. J. Miller, N. C. Snaith, "A random matrix model for elliptic curve L-functions of finite conductor", J. Phys. A 45 (2012) 115207 (Crossref) | arXiv 1107.4426 **v3**: LaTeX and PDF; also Miller-site PDF (same text) | Whole paper: §1 Thms 1.1–1.3, §2–§6 |
| DHKMS2 | Same authors, "The lowest eigenvalue of Jacobi random matrix ensembles and Painlevé VI", J. Phys. A 43 (2010) 405204 (Crossref) | arXiv 1005.1298 **v2**, PDF | Abstract, §1, §2 (eqs. 2.1–2.12), §3 heads |
| HKS | D. K. Huynh, J. P. Keating, N. C. Snaith, "Lower order terms for the one-level density of elliptic curve L-functions", J. Number Theory 129 (2009) 2883–2902 (Crossref) | arXiv 0811.2304 **v1**, PDF and LaTeX | Conj. 2.1, Thms 2.2–2.3 (eq. 2.52), §3 (eqs. 3.8–3.26), §4 |
| CS07 | J. B. Conrey, N. C. Snaith, "Applications of the L-functions ratios conjectures" | arXiv math/0509480 **v2**, PDF | §2.2 (Conj. 2.6, Thm 2.7), §3 (Thms 3.1, 3.2, eqs. 3.10–3.17) |
| M07s | S. J. Miller, "A symplectic test of the L-functions ratios conjecture" | arXiv 0704.0927 **v5**, PDF | Abstract, Thms 1.1–1.2, eqs. 1.3–1.6 |
| M07h | S. J. Miller, "Lower order terms in the 1-level density for families of holomorphic cuspidal newforms" | arXiv 0704.0924 **v4**, PDF | Abstract, §1 summary (eqs. 1.18–1.20), Thm 1.1 head, Thm 3.4 (eqs. 3.11–3.14) |
| B10r | F. Bornemann, "On the numerical evaluation of distributions in random matrix theory: a review" | arXiv 0904.1581 **v5**, PDF | §2.4–2.6 (Bessel kernel, PIII), §5 (E±, eqs. 5.1–5.9), App. A.1 (eq. A.8), Tables 7–8 |
| B10f | F. Bornemann, "On the numerical evaluation of Fredholm determinants" | arXiv 0804.2543 **v2**, PDF | Abstract, sine-kernel Ritz–Galerkin passage (cites KS book p. 411) |

**Not read (UNVERIFIED wherever used):**

- N. M. Katz and P. Sarnak, *Random Matrices, Frobenius Eigenvalues, and Monodromy* (AMS Colloq. Publ. 45, 1999). I
  found no legitimate open copy and only cite it at second hand.
- Özlük–Snyder.
- Rubinstein's thesis and his Duke 2001 paper.
- Marshall's hard-gap paper (DHKMS ref. [45]).
- Huynh–Miller–Morrison (DHKMS ref. "HMM").
- Bogomolny–Bohigas–Leboeuf–Monastra 2006.
- Conrey–Keating–Rubinstein–Snaith (CKRS02/06).
- Forrester–Witte.
- Kowalski–Michel and VanderKam.
- The published journal versions of ILS (Publ. IHÉS 91 (2000) 55–131, citation per brief, not checked) and of HKS.
  Their equation numbers may differ from the arXiv versions.

---

## 2. One-level densities: definitions, normalisation and conventions

### 2.1 Katz–Sarnak, Bull. AMS 1999 (VERIFIED)

Random-matrix side, §2:

- G(N) is realised as unitary matrices with eigenvalues e^{iθ_j}, ordered 0 ≤ θ₁ ≤ … ≤ θ_N < 2π (eq. 19).
- ν_k(G(N))[a,b] = Haar{A : θ_k(A)N/2π ∈ [a,b]} (eq. 27).
- Δ(A)[a,b] = #{θ(A) : (θ(A)N)/2π ∈ [a,b]} (eq. 28), with W(G(N)) = ∫Δ(A)dA (eq. 29).
- lim W(G(N))[a,b] = ∫_a^b w(G)(x)dx (eq. 31), where (eq. 31′):

> w(G)(x) = 1 if G = U or SU; 1 − sin 2πx/2πx if G = Sp; 1 + sin 2πx/2πx if G = SO(even); δ₀ + 1 − sin 2πx/2πx if G = SO(odd).

- Note: N here is the number of eigenvalues, i.e. the matrix size. For SO(2N) the scaling is θ·2N/2π = θN/π, which is
  the convention M06 and DHKMS use. **KS99 (31′) lists no density for O.**
- KS99 p. 10 (VERIFIED quote): "ν₁(SO(odd)) = δ₀, and it turns out that ν₂(SO(odd)) = ν₁(Sp). Note that Sp is unique
  in having the density of ν₁ vanish (in fact to second order) at s = 0."
- KS99 p. 9: "the measures ν_k(G) may be expressed in terms of Fredholm determinants ([K-S1]), and this allows for their
  numerical calculation." (K-S1 is the book; its formulas are UNVERIFIED.)

Number-field side, §4:

- Zeros are written ½ + iγ_f, ordered … ≤ γ_f^{(−1)} ≤ 0 ≤ γ_f^{(1)} ≤ … (eq. 51), and scaled as γ_f^{(j)} log c_f / 2π
  (eq. 52).
- ν_j(X,F) is defined in (53). Δ(f,φ) = Σ_{γ_f} φ(γ_f log c_f/2π) (eq. 54), and
  W(X,F,φ) = (1/#F_X) Σ_{c_f ≤ X} Δ(f,φ) (eq. 55).
- The conjecture is W(X,F,φ) → ∫_{−∞}^{∞} φ(x)w(F)(x)dx. Here c_f is the conductor.
- §4 assumes RH ("for the rest of this section we assume RH for all L(s,f)'s").

### 2.2 Iwaniec–Luo–Sarnak (VERIFIED, arXiv v1)

- Eq. (1): ρ_F = ½ + iγ_F.
- Eq. (2): D(F,φ) = Σ_{γ_F} φ(γ_F (log c_F)/2π), for φ ∈ S(ℝ) **even** with compactly supported φ̂, where
  φ̂(ξ) = ∫φ(x)e^{−2πixξ}dx.
- Eq. (3): the average (1/M_x(F)) Σ_{c_F ≤ x} D(F,φ).
- Conductors are c_f = k² for the weight-aspect family F_K and for F_sym² (where c_{sym²f} = k²), and c_f = N for the
  level-aspect family F_N with N prime. These are plain conductors, not analytic conductors with (2π)⁻² factors.
- Eq. (4), verbatim:

> W(SO(even))(x)dx = (1 + sin 2πx/2πx)dx, W(SO(odd))(x)dx = δ₀(x) + (1 − sin 2πx/2πx)dx, W(O)(x)dx = ½δ₀ + dx,
> W(Sp)(x)dx = (1 − sin 2πx/2πx)dx. Here δ₀ is the unit point measure at 0.

- Eq. (5) is the Density Conjecture: lim (1/M_x) Σ D(F,φ) = ∫_{−∞}^{∞} φ(x)W(G(F))(x)dx for all compactly supported φ̂.
- ILS (4) lists **no U**. The U density is in KS99 (31′), Y06 and M04.
- Consistency check (DERIVED): ½W(SO(even)) + ½W(SO(odd)) = 1 + ½δ₀ = W(O).

### 2.3 Fourier-side forms (VERIFIED in Y06 and M04)

Y06, eq. `eq:symmetrytypes`, with f̂(y) = ∫f(x)e(−xy)dx:

- Ŵ(U) = δ₀
- Ŵ(Sp) = δ₀ − ½η
- Ŵ(O) = ½ + δ₀
- Ŵ(SO(even)) = δ₀ + ½η
- Ŵ(SO(odd)) = 1 + δ₀ − ½η

Here η(t) = 1 for |t| < 1, ½ at |t| = 1, and 0 for |t| > 1. M04 (Thm `thmonelevel`) gives the same with I(u) = 1_{[−1,1]}.

Consequence (stated in Y06, M04 and ILS Remark B): **O, SO(even) and SO(odd) are indistinguishable by the one-level
density unless supp φ̂ extends beyond [−1,1].** ILS Remark (B) says the Ŵ for Sp, SO(even) and SO(odd) "all have
discontinuities at ξ = ±1".

### 2.4 Summary table

All of these are VERIFIED against ILS (4) and KS99 (31′), plus Y06 for U and O.

| Symmetry | W(x), integrated against even φ over ℝ | Ŵ(u) | δ₀ weight | Primary location |
|---|---|---|---|---|
| U | 1 | δ(u) | 0 | KS99 (31′); Y06; M04 |
| USp | 1 − sin(2πx)/(2πx) | δ(u) − ½η(u) | 0 | KS99 (31′); ILS (4); Y06 |
| SO(even) | 1 + sin(2πx)/(2πx) | δ(u) + ½η(u) | 0 | KS99 (31′); ILS (4); Y06 |
| SO(odd) | 1 − sin(2πx)/(2πx) + δ₀(x) | δ(u) − ½η(u) + 1 | 1 | KS99 (31′); ILS (4); Y06 |
| O | 1 + ½δ₀(x) | δ(u) + ½ | ½ | ILS (4); Y06 (not in KS99 (31′)) |

Scaling: x = γ·log(c_f)/(2π), giving unit mean spacing. KS99 and ILS use the conductor c_f. HR uses log q/2π. Y06 uses
log X/2π with X ≈ N_E. M06 uses log C_t/2π. CS07 and M07s use log X/2π, and log(d/π)/2π in CS07 (3.13). **HKS and
DHKMS use γ·L/π with L = log(√M X/2π).** That equals γ·log(M X²/4π²)/(2π): the same unit-density scaling, written
through one global X.

### 2.5 What is proved, for which family, on what support

All entries below are VERIFIED except where marked.

| Family | Symmetry | Support of φ̂ | Hypotheses | Source |
|---|---|---|---|---|
| All non-principal χ mod prime q | U | [−2,2] | **None.** HR: "we don't assume GRH since we allow the γ to be complex". Error O(1/log q) | HR Thm 3.1 (`thm:expectation`), §3 |
| Quadratic Dirichlet L(s,χ_d) | Sp | (−2,2) | RH (KS99 §4) | KS99 I(b), citing [K-S2] and Özlük–Snyder. HR quotes the Özlük–Snyder form, with weight e^{−πd²/D²} and GRH. Özlük–Snyder itself UNVERIFIED |
| Quadratic Dirichlet, even fundamental d ≤ X | Sp, with lower-order terms | (−σ,σ) ⊂ (−1,1) | RH used in parts (M07s Lemma 2.1); not fully audited | M07s Thm 1.2 |
| Weight k ≤ K, level 1, ε = +1 (k ≡ 0 mod 4) or ε = −1 (k ≡ 2 mod 4) | SO(even) / SO(odd) | (−2,2) | GRH | ILS Thm 1 |
| Fixed weight k, prime level N → ∞, H_k^± | SO(even) / SO(odd) | (−2,2) | GRH; unconditional for (−1,1) (Remark B) | ILS Thm 1 |
| Same, weight 2, N prime | SO(even) / SO(odd) | (−2,2) | RH | KS99 III(b), citing ILS |
| Level 1, all even k, weighted by h(k/K)·L(1,sym²f)⁻¹ | O | (−2,2) | Uses approximation D_k of (20); stated "unconditionally" (ILS p. 7) | ILS Thm 3 |
| Same | O | (−7/3, 7/3) | Hypothesis 4 (exponential sums over primes) | ILS Thm 5 |
| sym² f, f level 1 | Sp | (−4/3, 4/3) | GRH | ILS Thm 1; KS99 IV(b) |
| GL₂ form twisted by quadratic χ (e.g. Δ⊗χ, E⊗χ), split by sign | SO(even) / SO(odd) | (−1,1) | RH | KS99 II(b), citing [K-S2] (UNVERIFIED primary) |
| All E: y² = x³ + ax + b, a,b > 0, smooth weight, a ≍ X^{1/3}, b ≍ X^{1/2} | "O inasmuch as detectable within (−1,1)" | (−7/9, 7/9) | GRH | Y06 `thm:mainresult`: D ∼ [φ̂(0) + ½φ(0)]·W_X |
| One-parameter families of rank r over ℚ(T) (rational surfaces) | Orthogonal, plus r central zeros | σ₁ < min(½, 2/(3m)) (1-level) | GRH; ABC if Δ(T) has an irreducible factor of degree ≥ 4 | M04 "Rational Surfaces Density Theorem" |

---

## 3. First-zero (lowest-zero) distributions

### 3.1 What the primary texts state

- **KS99** (VERIFIED):
  - The scaling-limit measures ν_k(G) exist (eq. 30) and are expressible as Fredholm determinants ([K-S1]; the explicit
    formulas are UNVERIFIED because the book was not read).
  - ν₁(SO(odd)) = δ₀ and ν₂(SO(odd)) = ν₁(Sp).
  - Figure 5 plots ν₁ for U, Sp and SO(even).
  - Published mean values: "the mean value of γ_χ log q_χ/2π should be the mean of ν₁(Sp) which is 0.7827…" (§4 I(d)).
  - The SO(even) data in Figs. 8 and 10 are "renormalized to have mean 0.3214" (the ν₁(SO(even)) mean).
  - The SO(odd) data in Figs. 9 and 11 are "renormalized to have mean 0.7827" (ν₂(SO(odd)) = ν₁(Sp)).
  - Data from Rubinstein: quadratic L(s,χ_d), 10¹² < |d| < 10¹² + 200000, 7243 d's, with raw mean first zero 0.8268.
    Twists of Δ: 350000 < |d| < 650000, raw means 0.2926 (even) and 0.7186 (odd).
  - Remark: "the convergence to the limit is at a speed of 1/log q and moreover there is a term of one sign which shifts
    the answer by this amount… the approach is from above."
- **M06** (VERIFIED) cites "pages 412–415 of [KaSa2]", which is the book: as N → ∞ the mean first normalised eigenangle
  is "approximately 0.321" for SO(even) and "approximately 0.782" for SO(odd) (second eigenangle). Finite-N simulations,
  Figs. 1–2:
  - SO(4), 23,040 matrices: mean .357, sd .302.
  - SO(6), 23,040 matrices: mean .325, sd .284.
  - SO(7), 322,560 matrices: first eigenangle above 1, mean .879.

  The captions give the same number for mean and median (".357 … Median = .357", ".325 … .325", ".879 … .879"), which
  looks like a caption error in the source. The SO(2N) normalisation is θ_j N/π. The finite-N mean *decreases* towards
  0.321 as N grows.
- **B10r** (VERIFIED) gives the computable machinery:
  - K±_sin(x,y) = ½(K_sin(x,y) ± K_sin(x,−y)) (eq. 5.3).
  - E±(k;s) = ((−1)^k/k!) d^k/dz^k det(I − zK±_sin on L²(−s/2,s/2))|_{z=1} (eq. 5.6).
  - E₂(k;s) = Σ_j E₊(j;s)E₋(k−j;s) for GUE (eq. 5.7), and E₁(0;s) = E₊(0;s) for GOE (eq. 5.8a).
  - Hard edge: E₂^{(hard)}(k;(0,s),±½) = E∓(k; 2√s/π) (eq. A.8), linking the even/odd sine kernels to the Bessel kernel
    with α = ∓½. That kernel has a Painlevé III (Jimbo–Miwa–Okamoto σ-form) representation (eqs. 2.42–2.43, after
    Tracy–Widom 1994b).
  - Nyström/Gauss–Legendre quadrature gives exponential convergence for analytic kernels (B10f). The method and Matlab
    toolbox are in B10r §9 and App. A.
  - Tables 7–8 give spacing moments for GOE and GUE (e.g. GUE p₂(0;s) variance 0.1799938776; GOE p₁(0;s) variance
    0.2855306557).
- **DHKMS2** (VERIFIED, finite N, including non-integer N):
  - The eigenphase joint density of SO(2N), SO(2N+1) and USp(2N) is a Jacobi ensemble,
    C ∏ w(cos φ_j) ∏ (cos φ_k − cos φ_j)² with w = (1 − cos φ)^α (1 + cos φ)^β (eqs. 2.4–2.5).
  - Parameters: "α = β = 0 corresponds to SO(2N), α = 1 and β = 0 corresponds to SO(2N+1), and α = β = 1 to USp(2N)".
  - The first-eigenphase density is ν_N^{(α,β)}(φ) = −dE_N^{(α,β)}(φ)/dφ (eq. 2.6), where E is the probability of no
    eigenphase in [0,φ].
  - E is computed as an Okamoto τ-function of Painlevé VI. They use the Forrester–Witte auxiliary Hamiltonian h(t)
    (eq. 3.1ff, with t = 1 + cos φ (2.11) up to scaling), in two ways: (i) a numerical ODE solve from initial conditions
    near t = 1, obtained from the Selberg–Aomoto integral; (ii) a power series about t = 0 (SAGE). MATLAB and SAGE code
    are in the appendices.
  - DHKMS used this for the non-integer N curves in their Fig. 4 (N_eff = 2.14, N_std = 12.26).

### 3.2 Per symmetry type: what gives the first-zero law

| Type | Scaling-limit first-zero law | Finite N | Published numbers |
|---|---|---|---|
| U | Gap probability det(I − K_sine on (0,t)) = E₂(0;t), the GUE bulk gap (DERIVED from B10r 5.7 and the one-sided KS ν₁ convention) | Not treated in DHKMS2 (U(N) is not a Jacobi ensemble in this sense) | Fig. 5 of KS99 (plot only). Mean 0.5899969 (DERIVED, App. A) |
| SO(even) | E(t) = det(I − K₊ on L²(0,t)) with K₊(x,y) = S(x−y) + S(x+y), S(x) = sin πx/πx. Equals E₊(0;2t) = E₁(0;2t) (GOE gap, B10r 5.8a) and the hard-edge Bessel α = −½ (B10r A.8, PIII) | Jacobi α = β = 0, PVI (DHKMS2) | Mean 0.3214 (KS99 captions), ≈ 0.321 (M06). DERIVED: 0.321383 |
| SO(odd) | ν₁ = δ₀. The first non-central zero follows ν₂(SO(odd)) = ν₁(Sp) | Jacobi α = 1, β = 0 for the N free eigenphases (DHKMS2) | 0.7827 (KS99), ≈ 0.782 (M06) |
| USp | E(t) = det(I − K₋ on L²(0,t)) with K₋ = S(x−y) − S(x+y). Equals E₋(0;2t), the hard-edge Bessel α = +½ | Jacobi α = β = 1 (DHKMS2) | Mean 0.7827… (KS99). DERIVED: 0.782716 |
| O | A Haar mixture of the two cosets: ½·SO(even) law + ½·(atom at 0 / SO(odd)) (DERIVED from the O = ½SO(even) + ½SO(odd) structure; book UNVERIFIED) | — | — |

**Status of the kernel identifications in the table:**

- **DERIVED** from B10r's E± and the one-level densities (the diagonal of K± is 1 ± sin(2πx)/(2πx)).
- **Numerically VERIFIED** against the published constants. My Nyström evaluation (App. A) gives:
  - SO(even) mean 0.321383, compared with KS99 "0.3214", M06 "≈0.321", and GOE ⟨s²⟩/4 = 1.2855306557/4 = 0.3213827
    from B10r Table 7.
  - USp mean 0.782716, compared with KS99 "0.7827…".
  - B10r's two A.1.3 cross-check values reproduced to 15 digits (0.861142170583287 and 0.524976779218592).
- The exact kernel statements in the KS book were **not** read (UNVERIFIED).
- Also derived: the SO(even) first-zero density is 2 at 0 (no repulsion), and the USp density vanishes at 0 (second-order
  zero, as KS99 states).

**Tables:** I found no table of the ν₁(G) densities in the papers read. KS99 gives plots and means only. B10r gives
GOE/GUE/GSE spacing tables, which cover SO(even) via E₁(0;s) = E₊(0;s), and a toolbox to compute any of these to about
15 digits.

---

## 4. The DHKMS excised orthogonal ensemble (arXiv 1107.4426v3; VERIFIED unless marked)

### 4.1 Model definition

- Characteristic polynomial: Λ_A(e^{iθ},N) := det(I − e^{iθ}A^{−1}) = ∏_{k=1}^N (1 − e^{i(θ−θ_k)})(1 − e^{i(θ+θ_k)}),
  for A ∈ SO(2N) (eq. 1.1).
- **Excised ensemble:** T_𝒳 = {A ∈ SO(2N) : log|Λ_A(1,N)| ≥ 𝒳} (Thm 1.1), i.e. |Λ_A(1,N)| ≥ exp 𝒳 = c × exp(−N_std/2)
  (eq. 3.4). Haar measure is renormalised by C_𝒳, defined by 1 = C_𝒳 ∫ H(log Λ_A(1,N) − 𝒳) ∏(cos θ_j − cos θ_k)² dθ
  (eq. 6.12; P(N,r,θ) is defined in eq. 6.33).
- **Motivation** is the Waldspurger / Kohnen–Zagier discreteness, L_E(½,χ_d) = κ_E c_E(|d|)²/d^{1/2} (eq. 2.7). So
  rank-0 curves have L_E(½,χ_d) ≥ κ_E/d^{1/2} (eq. 3.3). Values are discretised on the scale 1/√d, which on the matrix
  side is exp(−N_std/2) with N_std ∼ log d.
- **Theorem 1.1:**
  R₁^{T_𝒳}(θ₁) = (C_𝒳/2πi) ∫_{c−i∞}^{c+i∞} 2^{Nr} (exp(−r𝒳)/r) R₁^{J_N}(θ₁; r−½, −½) dr.
  Here R₁^{J_N} is the one-level density of a Jacobi ensemble with weight
  w^{(α,β)}(cos θ) = (1 − cos θ)^{α+½}(1 + cos θ)^{β+½}, α = r − ½, β = −½.
  Note that this exponent convention differs from DHKMS2 (2.5).
- **Theorem 1.2 (eq. 1.4):** the closed form, with Selberg-integral Γ-products and P(N,r,θ) built from Jacobi
  polynomials (eq. `PNrtheta`).
- **Theorem 1.3 (eq. 1.5):** R₁^{T_𝒳}(θ) = 0 for d(θ,𝒳) < 0, and
  R₁^{SO(2N)}(θ) + C_𝒳 Σ_k b_k(θ) exp((k+½)𝒳) for d ≥ 0, where **d(θ,𝒳) = (2N−1) log 2 + log(1 − cos θ) − 𝒳**.
  - This gives a **hard gap** {θ > 0 : d < 0}, exponentially small in N when −𝒳 ∝ N, followed by "soft repulsion … on a
    much larger scale".
  - "In the limit 𝒳 → −∞, θ fixed, R₁^{T_𝒳}(θ) → R₁^{SO(2N)}(θ)."
  - DHKMS footnote: Marshall later gave "a rigorous theory for this hard gap" (UNVERIFIED).
- SO(2N) finite-N one-level density: R₁(s) = (2N−1)/2π + sin((2N−1)s)/(2π sin s) (eq. 4.5).
- Its scaled expansion (eq. 4.6), DERIVED-verified by Taylor expansion:
  (π/N)R₁(πy/N) = 1 + sin 2πy/2πy − (1 + cos 2πy)/(2N) − πy sin 2πy/(6N²) + O(N⁻³).

### 4.2 Parameter-fixing recipe (family F_E⁺(X): even quadratic twists of E, prime conductor M)

1. **Conductor and sign.** The twist L_E(s,χ_d) has conductor M d² and sign χ_d(−M)ω(E) (eq. 2.6). The family keeps
   sign +1 and 0 < d ≤ X.
2. **Standard size.** Equating the eigenvalue density N/π with the zero density (1/π)log(√M d/2π) gives N_std ∼ log d
   (§3). Concretely, **N_std = L = log(√M X/2π)** (eqs. 4.3, 4.9). For E₁₁ with X = 400,000, N_std ≈ 12.26; the
   simulations used N_std = 12.
3. **Effective size (BBLM-style).** Match the 1/L term of the ratios-conjecture expansion (eq. 4.2 = HKS (3.19)) to the
   1/N term of (4.6). This gives **N_eff = L/(2r₁)** (eq. 4.7), where r₁ is HKS's a₁ (eq. 3.20, below). For E₁₁,
   **r₁ ≈ 2.8600** (eq. 4.8, "find numerically"), so N_eff ≈ 2.14 (eq. 4.10). Simulations used SO(4), i.e. N_eff = 2.
   r₂ is not given numerically.
4. **Cut-off from CKRS.**
   - Moments: M_E(X,s) ∼ a_s(E)M_O(N,s) (eq. 5.2), with M_O(N,s) = 2^{2Ns} ∏_{j=1}^N Γ(N+j−1)Γ(s+j−½)/(Γ(j−½)Γ(s+j+N−1))
     (eq. 5.6). The arithmetic factor a_s(E) is in eq. 5.4; for d > 0 use the "+" sign in L_M(±ω(E)/M^{1/2}).
   - Small-x density: P_O(N,x) ∼ x^{−½}h(N) (eq. 5.8), with h(N) = Res_{s=−½}M_O(N,s) (eq. 5.9) and
     h(N) ∼ 2^{−7/8}G(½)π^{−¼}N^{3/8} (eq. 5.10).
   - Ansatz P_E(d,x) ∼ a_{−½}(E)P_O(log d, x) (eq. 5.13).
   - The effective discretisation is δ·κ_E/√d. **δ is fitted to Rubinstein's CKRS06 count of vanishing twists:**
     (8/3)·2^{−7/8}G(½)π^{−¼}δ^{½} ≈ 0.2834620 for E = 11A (eq. 5.20), which gives δ ≈ 0.185116 (5.21).
   - κ_E = 6.346046521 and a_{−½}(E) = 0.732728078 (5.22), so δκ_E = 1.17475 (5.23).
   - **This cut-off is not fixed by theory: δ is calibrated on the count of central vanishings in the same family.**
5. **Map the cut-off to matrix size by matching probability *densities*.**
   - N = N_std: c_std = a_{−½}⁻²(E)·δκ_E ≈ **2.188** (eqs. 5.25–5.26). Cut-off |Λ_A(1,12)| ≥ 2.188e^{−6} = 0.005424
     (Fig. 10 caption).
   - N = N_eff: c_eff = a_{−½}⁻²(E)(2r₁)^{−3/4}δκ_E ≈ **0.5916**, applied as c_eff × exp(−r₁N_eff) (eqs. 5.30–5.31).
   - Matching *probabilities* instead gives c = a²δκ ≈ 0.6307 (5.28) for N_std and (2r₁)^{3/4}a²δκ ≈ 2.3328 (5.32) for
     N_eff. **Both are rejected by the data**, because the CDF-error minimum sits at the density-matched values.
   - DERIVED check: all of these numbers are reproduced from the quoted constants to the printed precision (App. A,
     `dhkms_numbers.py`).

### 4.3 Data compared

- Rubinstein's lcalc: lowest zero of even quadratic twists L_{E₁₁}(s,χ_d), with E₁₁ = [0,−1,1,0,0], i.e.
  y² + y = x³ − x², M = 11.
- §4 states 0 < d ≤ X = 400,000 over "fundamental discriminants". §5.2 onward uses **prime** fundamental discriminants
  and rank-0 (non-vanishing) twists.
- Mean first zero 0.4081.
- N_std run: 3×10⁶ SO(24) matrices with the cut-off, first-eigenvalue mean 0.365. Matched only after mean-rescaling by
  0.4081/0.365 = 1.118.
- N_eff run: 3×10⁶ SO(4) matrices, mean 0.4234, no rescaling.
- One-level density (§5.4): 9.12×10⁶ SO(24) matrices (rescaled) and 9.8×10⁶ SO(4) matrices. The N_std excised model
  tracks the zero data "over a wide range". The N_eff model agrees only "up to the first unit mean spacing".
- The N_eff one-level-density run uses the cut-off 0.5916·exp(−N_std/2) = 0.001466 (Fig. 10 caption and §5.4 text).
  The first-zero figure for the same model (Fig. 8) instead writes 0.5916 × exp(−r₁N_eff) with N_eff = 2, which would
  be e^{−5.72}·0.5916 ≈ 0.00194. **Internal inconsistency in the paper.** Fig. 10 and §5.4 state exp(−6) explicitly;
  which value produced Fig. 8 is not determinable from the text.
- Consistency test of Thms 1.2–1.3 against 200,000 simulated SO(4) matrices with cut-off |Λ_A(1,N)| ≥ 0.1: Fig. 13.
- Figure map (arXiv v3 PDF):
  - Fig. 1: SO(24) vs excised SO(24) at e^𝒳 ≈ 0.005.
  - Fig. 2: Miller's data.
  - Fig. 3: finite-N SO(4/6/8) first eigenvalue.
  - Fig. 4: N_eff vs N_std vs data.
  - Figs. 5–7: N_std excised model.
  - Figs. 8–9: N_eff excised model.
  - Figs. 10–12: one-level density.

### 4.4 Predicted behaviour

- **Hard gap** at the origin: R₁ = 0 where 1 − cos θ < e^𝒳·2^{−(2N−1)}.
- **Soft repulsion** extending far beyond the gap.
- Recovery of SO(2N) as 𝒳 → −∞ (or N → ∞ with −𝒳 ∝ N).
- DHKMS (§1): their larger data sets "indicate a hard gap containing no zeros", whereas Miller's original data showed
  only soft repulsion.

### 4.5 Miller's original observation (M06, arXiv math/0508150v3; VERIFIED)

- Zeros are normalised as γ_{E,1} log C_t/2π, where C_t is the conductor. Zeros come from Rubinstein's lcalc, with a
  contour-integral check that all zeros in a region were found. Data were posted at
  `http://www.math.brown.edu/~sjmiller/repulsion` (not fetched).
- Curves [a₁,…,a₆] with a₁ ∈ [0,10] and the other aᵢ ∈ [−10,10], reduced to minimal models.
- **Rank 0:**
  - 750 curves with log(cond) ∈ [3.2, 12.6]: median 1.00, mean 1.04, sd .32 (Fig. 3).
  - 750 curves with log(cond) ∈ [12.6, 14.9]: median .85, mean .88, sd .27 (Fig. 4).
  - Two-sample t ≈ 10.5.
- **Rank 2:**
  - 665 curves with log(cond) ∈ [10, 10.3125]: median 2.29, mean 2.30 (Fig. 5).
  - 665 curves with log(cond) ∈ [16, 16.5]: median 1.81, mean 1.82 (Fig. 6).
- Abstract findings: repulsion "increases with r"; it "decreases markedly as the conductors increase"; "we conjecture
  that the r family zeros do not repel in the limit"; and spacings between adjacent normalised zeros are statistically
  independent of the repulsion ("the effect of the repulsion is simply to shift all zeros by approximately the same
  amount").
- M06 is also the source of the SO(2N) finite-N first-eigenangle means quoted in §3.1.

---

## 5. Lower-order (finite-conductor) terms with theory-fixed coefficients

| Family | Statement | Status | Location |
|---|---|---|---|
| Quadratic Dirichlet L(s,χ_d), real even χ_d (Sp) | Full one-level density to O(X^{1/2+ε}): S₁(f) = (1/2π)∫f(t)Σ_d[log(d/π) + ½Γ′/Γ(¼ + it/2) + ½Γ′/Γ(¼ − it/2) + 2(ζ′/ζ(1+2it) + A′_D(it;it) − (d/π)^{−it}(Γ(¼ − it/2)/Γ(¼ + it/2))ζ(1−2it)A_D(−it;it))]dt. A_D is in (3.11), A′_D(r;r) = Σ_p log p/((p+1)(p^{1+2r} − 1)) (3.12). Scaled version (3.14); limit (3.16) = 1 − sin 2πτ/2πτ | **Conjectural** (ratios conjecture, Conj. 2.6) | CS07 **Thm 3.1, eq. (3.10)** (§3, not §7) |
| Same, even fundamental d ≤ X | (1.3)–(1.6): ratios prediction with log X/2π scaling. **Proved** to agree up to O(X^{−(1−σ)/2+ε}) for supp ĝ ⊂ (−σ,σ) ⊂ (−1,1). For {8d}, agreement up to O(X^{−1/2} + X^{−(1−3σ/2)+ε} + X^{−3(1−σ)/4+ε}), i.e. O(X^{−1/2+ε}) when σ < 1/3 | Theorem (number-theory side) | M07s Thm 1.2; Thm 1.1 = CS07 rewritten |
| Twists L_Δ(s,χ_d) of Ramanujan Δ (SO(even)) | Analogue of (3.10) with Γ′/Γ(6 ± it), ζ′/ζ, L′_Δ(sym²)/L_Δ(sym²), B′_Δ | Conjectural | CS07 Thm 3.2, eq. (3.17) |
| Even quadratic twists of E, prime conductor M (SO(even)) | Full density **(2.52)** to O(X^{1/2+ε}), with Y_E (2.35), A_E (2.36), A¹_E (2.40). Scaled: (1/X*)Σ g(γ_d L/π) = ∫g(τ)(1 + sin 2πτ/2πτ − a₁(1 + cos 2πτ)/L − a₂ πτ sin 2πτ/L² + O(L⁻³))dτ **(3.19)**, with **a₁ = 1 + 2γ − A¹_E(0,0) − L′_E(sym²,1)/L_E(sym²,1)** (3.20) and a₂ in (3.21) (involves γ, γ₁, B′(0), B″(0), L′_E(sym²,1)/L_E(sym²,1), L″_E(sym²,1)/L_E(sym²,1), plus a term written "4γL′(1)/L(1)") | Conjectural (ratios). Theory-fixed coefficients. The HKS data test (E₁₁, d < 40,000 and < 400,000) matches **except** near t = 0, where the data repel: "they do not capture the behaviour of zeros in the important region very close to the critical point" | HKS Thm 2.3, (3.19)–(3.22) |
| Same, E₁₁ | r₁ (= a₁) ≈ 2.8600 numerically; r₂ not given | Numerical evaluation of the HKS constant | DHKMS (4.2), (4.8) |
| Weight-k, prime-level newforms (O / SO±), harmonic weights ζ(2)/L(1,sym²f) | Prime-sum part S(F) = φ(0)/2 + 2(−γ_{ST;0} + γ_{ST;2} − γ_{ST;Ã} + γ_PNT)φ̂(0)/log R + O(log⁻³R) for σ < 4/3. γ_PNT ≈ −1.33258 and the Sato–Tate combination sums to 0 (3.14). The non-conductor lower-order term is −1.33258·2φ̂(0)/log R (1.18) | Theorem (stated as Theorem 3.4; hypotheses not audited) | M07h Thm 3.4, (3.11)–(3.14), (1.18) |
| One-parameter elliptic families (CM / torsion / rank) | Family-dependent 1/log R terms: −2.124, −2.201, −2.347, −1.921, −2.042 (times 2φ̂(0)/log R) for y² = x³ + B(6T+1)^κ (1.19); −2.703 for y² = x³ − 3x + 12T (1.20); S_Ã contribution −.11 vs .63 for the rank-1 / rank-0 CM pair (§5.2) | Numerically evaluated prime sums | M07h §1, §5 |
| Unitary Dirichlet family | Error O(1/log q) only; no explicit 1/log q constant in the theorem | Theorem | HR Thm 3.1 |

Notes:

- (i) CS07 (3.14) and M07s (1.3) scale by log X/2π, a global X. CS07 (3.13) and (3.16) use log(d/π)/2π. HKS and DHKMS
  use L = log(√M X/2π) and γL/π. **The 1/L coefficients (a₁, a₂, r₁) are tied to the scaling actually used and to the
  per-family X-averaging, including the Euler–Maclaurin step (3.13) of HKS.**
- (ii) None of these lower-order formulas produces the near-origin repulsion. That is the stated motivation for the
  excision (HKS §3 end and §4; DHKMS §4).

---

## 6. Items marked UNVERIFIED

- Explicit Fredholm-determinant kernels and tables in the KS book (only cited at second hand: KS99 p. 9, M06
  pp. 412–415 citation, B10f p. 411 citation).
- Özlük–Snyder's theorem statement and hypotheses (only quoted via KS99 and HR).
- KS [K-S2] (Bull/announcement) for the quadratic-twist families I(b) and II(b).
- Rubinstein's n-level results.
- Marshall's hard-gap theory.
- Huynh–Miller–Morrison's proof of the HKS lower-order terms (DHKMS's summary says they were "proved in [HMM]").
- BBLM06 N_eff for ζ.
- CKRS06 Conjecture 5.1 and Rubinstein's vanishing counts.
- Published-journal equation numbering for ILS, HKS, CS07, M06 and DHKMS (only arXiv numbering checked, except KS99,
  which was read in journal form).
- The value of r₂ for E₁₁ (never published in the papers read).

---

## 7. sha256 of every file read (in `/home/combust/specarith_lit_cache/ph1/`)

| File | sha256 | Content |
|---|---|---|
| KS_BullAMS1999.pdf | 4f99e2242e7a63d65b81078bd7318be6ee57613f9b71e568532949a7e01b7a77 | KS99 journal PDF |
| ILS_9901141.pdf | 5072c63324c329250f70c4ef4e2648a0e8ff465d6b9c241c3d3646d4c6759997 | ILS arXiv v1 PDF |
| src_math_9901141 | bc482333fe91d3d36c6f487b22cfc1627f32053568f83ad92772ce71bce2861a | ILS arXiv source (gzipped DVI; not read) |
| pdf_1107.4426v3.pdf | 28de6f6b78e5ba861223d2da90110cc027e795f600bf66e333629d915da1d1b0 | DHKMS v3 PDF |
| src_1107.4426 | 4283e5ddb17336c95d0af49e4ecc6d9a3f48bed3c7760b703c1cf6457dcfff0a | DHKMS source tarball |
| x_1107/FiniteConductorPaper.tex | 6a2a17c24c342f68537d84757a2f57cc8e25a8b116ee44967811db57b54a66e4 | DHKMS LaTeX |
| Miller_site_FiniteConductorPaper.pdf | c71d144ecbe13012d6ea4066e88157b8b75762ac9093d87ba87f64ff61aba3bd | Miller-site PDF of DHKMS (= v3 text) |
| src_1108.4114 | aaaad7fbb190e58765c33d6e17c29fb63fc5b111d826700c6403f983a37e40f3 | **Unrelated paper** (oligopoly) |
| x_1108/SpatialCollaborativeOligopoly20110820v1.tex | 4fcbbd5a46ee76a91289334288414036fcb00d9fcd8a23344ea9fe6b5807b2bc | Title only read |
| pdf_1005.1298v2.pdf | 358ee0d0d69776ba5432edaeef4dae4c1f1222cf200bc55b959f96d609e7e4fe | DHKMS2 PDF |
| 1005.1298_src | a18e75337d4739748eacc2d7f893061d69ad75cf8ec360b96307ee01e6682d8b | DHKMS2 source tarball |
| x_1005/PainlevePaperArxiv2010_09_02.tex | 869932134a7096eb616f01b21b9517424f1f58ee37b2461bb2055c9cd5325c85 | DHKMS2 LaTeX (extracted; PDF used) |
| pdf_math_0508150v3.pdf | f4443c8f286fd019bc58cd68bb94822ff2cccb864743a5d045a47e7d61205a5b | M06 PDF |
| src_math_0508150 | 79e91d8c8e7c00f025d263aea8633804e916d071cf50c7536f82abc0831d636f | M06 source tarball |
| x_0508150/ECnumerics04arxiv.tex | 3f6d073c923d5aff74c5a5a9af13829a7f482236e771fce83a1b4009e51fd3f9 | M06 LaTeX (extracted; PDF used) |
| pdf_0811.2304v1.pdf | c78cb601f47b6836b77d848387d1b6e42c8cee9f67eed97bb39be94175c33397 | HKS PDF |
| src_0811.2304 | 3159664f3010cbf6a410041d0791e6bad164d112848c2fdb8ac6071646964854 | HKS source tarball |
| x_0811/oneleveldensity2.tex | e7d5f1bc3a8c3979aff64f9ae37bc9eb264baa7f1afcbdc245baa1cadc81a7f8 | HKS LaTeX |
| pdf_math_0509480v2.pdf | 2deeeb0ff78b51835f2e59f7fcf2c0a8343f4cc65ff1aeb611ac12268ff42ac3 | CS07 PDF |
| src_math_0509480 | 69222df52053d3b6a1e9ddbefa944eac0c6bcba9b94a30d7345be335d0616afc | CS07 source (gz) |
| CS07_new_ratiosI.tex | f1447009462754b556267867c6d6ec9495dc6f3759b3b7f885498ad1fa3e8487 | CS07 LaTeX (extracted; PDF used) |
| pdf_0704.0927v5.pdf | bf64b7ca2b285030136298cd789f7f0d5d59ddee974e26eafcbb0c346c9b0fc2 | M07s PDF |
| src_0704.0927 | ffedf878e597be4d1c45e49166cf0a4ff8d0a2e1a7b63768055259a01f10c37c | M07s source (gz) |
| Miller_SymplecticTest.tex | bc4555c0040ba8b1b2a7b3ca0357da3f7bf46f37cc53bf0b0ba0056d8a9f60d6 | M07s LaTeX (extracted; PDF used) |
| pdf_0704.0924v4.pdf | bc437f7cc6944e5ba4c2c545918e3f72b4621289d748071ebd7f009ee93c9bbf | M07h PDF |
| src_0704.0924 | 7787e13daeaaab6ddc7ddcfa18f7bd2fcf2c97c79356eb49fc9c893dd704b0eb | M07h source (gz) |
| Miller_LowerTerms80.tex | 38a7493a25cf0823fbdc03cc3e8ae206307a5f40e66edb3367832957e8f8c53c | M07h LaTeX (extracted; PDF used) |
| src_math_0208230 | ccc0b83a9dedf15f712c12907d818f439a6c54bb74a8f60bcaccdc79006ea65e | HR source (gz) |
| HR_zeros_Dirichlet_L.tex | 2c29355bc8b18a20985ec69a3aab420f94ebb5aeed04b54a8db305020e77db2c | HR LaTeX |
| src_math_0406330 | 9324a54a0efa8e96bb28db5075276b6ad62380e898e3e704fafc045ebcaa3b91 | Y06 source (gz) |
| Young_eczeros.tex | 60cabcbb9ee238ee60e5f908ea6babdb1cd2d3607be16c884580eaed4b6791d9 | Y06 LaTeX (read via an LF-normalised copy, Young_lf.tex) |
| src_math_0310159 | 6214c81eb64537b438176cc17bdb439f01068d01a1a0b966ef57396991fd7c06 | M04 source (gz) |
| Miller04_rds.tex | 7640a96a834fedff48aa089e539c654a618e08987f58ae15c5a310dc84b010bd | M04 LaTeX (read via an LF-normalised copy, Miller04_rds_lf.tex) |
| pdf_0904.1581v5.pdf | 15e0102133a0d87466fbc86379d8f7add912c97f9b60f63007e0218604142770 | B10r PDF |
| src_0904.1581 | da743a190b912ffe789d7c54e319b992669a3608d8be38caa4f0052cafb245b2 | B10r source tarball |
| x_0904/article.tex | d5397e091675da5dbb1bc55237d608afcc2f4558493997014fc38aad3650856f | B10r LaTeX (extracted; PDF used) |
| pdf_0804.2543v2.pdf | 0652a97dcc57ec8727dbef4f60d14cb22c7b428b8551e3ecf67464803bde798a | B10f PDF |
| src_0804.2543 | a6a8e44ae720b19e37706ba9fca2d2de60a4b3df8a6772e62fad794a88bb9bc0 | B10f source tarball |
| x_0804/article.tex | 6466c5da08820b6de4827d9988a09c0afc5763627428677b1801c6df4ad9dc15 | B10f LaTeX (extracted; PDF used) |

---

## Appendix A. Numerical cross-checks (DERIVED)

These were run with `/home/combust/fmexplorer/bin/python3 -I` from the session scratchpad. Neither script reads any
downloaded file.

**A.1 `firstzero.py`.** Nyström method (48-point Gauss–Legendre) for det(I − K± on L²(0,t)), with
K±(x,y) = S(x−y) ± S(x+y) and S = sinc. The mean is ∫₀⁶ E(t)dt (400-point Gauss–Legendre; E(6) < 10⁻³⁴).

```
SO(even): K=S(x-y)+S(x+y): mean first scaled eigenvalue = 0.321383
USp / SO(odd) 2nd: K=S(x-y)-S(x+y): mean first scaled eigenvalue = 0.782716
first-zero density near 0: SO(even) -> 2.0000 ; USp -> 1.5e-07 (vanishes)
Bornemann check E+(1; 2sqrt6/pi) = 0.8611421705832869  (paper: 0.861142170583288)
Bornemann check E-(1; 2sqrt6/pi) = 0.524976779218592   (paper: 0.524976779218593)
```

**A.2 `unitary_first.py`.** det(I − K_sine on (0,t)) gives a U first-eigenangle mean of 0.5899969388. This equals
(1 + Var_GUE)/2 with Var_GUE = 0.1799938776 from B10r Table 8. SO(even) equals ⟨s²⟩_GOE/4 = 0.3213827 from B10r Table 7.

**A.3 `dhkms_numbers.py`.** Re-derives the DHKMS constants:

```
Barnes G(1/2) = 0.6032442812        (paper ~0.603244)
delta = 0.1851157                    (5.21: 0.185116)
delta*kappa = 1.1747528              (5.23: 1.17475)
c_std = 2.1880628                    (5.26: 2.188)
prob-matching c = 0.6307120          (5.28: 0.6307)
N_std = L = 12.2602904               (4.9: 12.26)
N_eff = 2.1434074                    (4.10: 2.14)
c_eff = 0.5915790                    (5.31: 0.5916)
prob-matching c_eff = 2.3328034      (5.32: 2.3328)
2.188 e^-6 = 0.0054235 ; 0.5916 e^-6 = 0.0014664   (Fig. 10 caption: 0.005424, 0.001466)
```

The script sources (the core of `firstzero.py`) are reproduced below so these numbers have a generator once the
scratchpad is gone:

```python
import numpy as np
S = np.sinc                                   # sin(pi x)/(pi x)
def gap(t, sign, m=48):                       # det(I - K_sign on L2(0,t))
    x, w = np.polynomial.legendre.leggauss(m); x = 0.5*t*(x+1); w = 0.5*t*w
    X, Y = np.meshgrid(x, x, indexing='ij'); K = S(X-Y) + sign*S(X+Y)
    sw = np.sqrt(w); return np.linalg.det(np.eye(m) - sw[:,None]*K*sw[None,:])
ts, ws = np.polynomial.legendre.leggauss(400); T = 6.0; ts = 0.5*T*(ts+1); ws = 0.5*T*ws
mean = lambda sg: float(np.sum(ws*np.array([gap(t, sg) for t in ts])))
# mean(+1) -> 0.321383 (SO(even)); mean(-1) -> 0.782716 (USp = 2nd zero of SO(odd))
```
