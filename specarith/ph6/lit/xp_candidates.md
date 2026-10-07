# Phase 6 literature: xp-type candidate Hamiltonians (primary-source check)

Compiled 2026-10-07 by CC for Will, as input to the Phase 6 (H = xp) pre-registration. Every quotation below was taken
from a source that was opened in this session. The local copies are under `~/specarith_lit_cache/` (outside the repo,
not committed). Equation numbers refer to the version stated. Text marked **[CC check]** is CC's own derivation or
numerical check, not a quotation.

Access status key:
- **PRIMARY-READ**: the paper itself was read, either the journal version or the arXiv version named.
- **SECONDARY-READ**: only a later source describing the paper was read.
- **ABSTRACT-READ**: only the arXiv abstract was read.
- **UNVERIFIED**: not opened.

Short answers to the questions in the brief:

| Question | Answer |
|---|---|
| "1 against 7/8" (BK 1999) | **Verified, with a gloss.** The bare phase-space area gives the constant **+1**, eq. (8). BK then add a *guessed* Maslov term **−1/8**, which gives 7/8, eq. (9). Both numbers are in the paper. |
| Interval dilation boundary condition and spectrum | **Verified.** Endres & Steiner (2010), eqs. (149)–(150), give exactly √b ψ(b) ∝ √a ψ(a) and k_n = 2π(n + c)/ln(b/a). This agrees with decision 4's corrected boundary condition. The brief v1 form ψ(L) = e^{iθ}ψ(l) is not the self-adjoint one. |
| Sierra–Rodríguez-Laguna x(p + ℓ_p²/p) | The spectrum is computable to any height with no zeta input. It contains **only the smooth part; there are no fluctuations.** Whether it gives 7/8 depends on a phase ϑ. The 2011 paper picks ϑ = π/4. The 2019 review picks a different ϑ and says the 7/8 "is missing". [CC check]: with the 2011 choice the constant term tends to −1/8, so it equals 7/8 only modulo 1 (one level is lost at low energy). |
| BBM eigenfunctions | **Hurwitz zeta, ψ_z(x) = −ζ(z, x+1).** The boundary condition ψ(0) = 0 *is* ζ(z) = 0, so the spectrum is defined by the zeros. That makes a test against the zeros circular. |
| Independent finite-basis discretisation of BBM | **None found** (searches listed under item 4). Decision 7 therefore gives **INAPPLICABLE**. |

---

## 1. Berry & Keating (1999), two papers

### 1a. "H = xp and the Riemann zeros"

- **Citation.** M. V. Berry & J. P. Keating, in *Supersymmetry and Trace Formulae: Chaos and Disorder*, eds. I. V. Lerner,
  J. P. Keating, D. E. Khmelnitskii, NATO ASI Series B vol. 370 (Kluwer Academic / Plenum, New York, 1999), pp. 355–367.
  DOI 10.1007/978-1-4615-4875-1_19 (from Crossref).
- **URL accessed.** https://michaelberryphysics.wordpress.com/wp-content/uploads/2013/06/berry306.pdf (Berry's own
  publication list, item 306). It is a scan of the printed chapter with page footers 355–366; the text was transcribed by
  eye from the page images.
- **Status.** PRIMARY-READ (published version, scanned).

**Phase-space cutoff and counting function (§2, p. 357).**
> "The simplest regularization is to truncate x and p by extending the Planck cell with sides l_x, l_p and area
> h = l_x l_p as in figure 1, so that A becomes the finite area indicated, which depends on ħ. [...] We cannot justify
> the regularization procedure [...]"

So the cutoff is x ≥ l_x, p ≥ l_p with **l_x l_p = h = 2πħ**. Later (p. 359): "Henceforth we set l_x = l_p = √(2π),
i.e. ħ = 1."

Eq. (8), p. 357:

  N(E) = (1/h)[ E ∫_{l_x}^{E/l_p} dx/x − l_p (E/l_p − l_x) ] + … = (E/h)(log(E/h) − 1) + 1 + …

**Constant term and the Maslov correction (pp. 357–358), verbatim.**
> "The constant (sub-leading) term should be modified by the Maslov phase. To guess this, we note that for a closed
> phase-space contour which turns by −2π, the extra term in the counting function is +1/2 (cf. the harmonic oscillator
> with frequency ω, for which N(E) = Int(E/ħω + 1/2)). For (1) the turn is +π/2, so the extra term should be −1/8.
> Choosing units such that ħ = 1, (equivalent to replacing E by ħE), we now obtain
>
> (9) N(E) = (E/2π)(log(E/2π) − 1) + 7/8 + …
>
> This is precisely the asymptotic form of the smoothed counting function for the Riemann zeros, namely
> (10) N_sm(E) = θ(E)/π + 1, where (11) θ(E) = −(E/2) log π + Im log Γ(1/4 + iE/2), correct to terms that do not vanish
> as E→∞. This is unlikely to be a coincidence."

**Verdict on the brief.** "1 against 7/8" is correct for the *bare area count*, eq. (8). It should be recorded together
with the fact that BK's own eq. (9) claims 7/8 through a guessed Maslov term ("To guess this"). Later sources treat that
step as unproven:
- Endres & Steiner 2010 (item 5), p. 8: "there is actually no rigorous argument for the choice of the Maslov index
  (correction)". They note that it implies a non-integer Maslov index μ = −1/2.
- Connes 1999 (item 6), p. 50, calls BK's computation "coincidental": "the two rectangles are eliminated for no reason,
  which changes appropriately the sign of the term in E".

**Time-reversal symmetry (p. 357).**
> "In addition, xp does not possess time-reversal symmetry, because it is not invariant under p→−p; more fundamentally,
> reversal of velocity ẋ for fixed x does not lead to retracing of the orbit, for the simple reason that ẋ is tied to x
> and so cannot be reversed independently. Furthermore, dynamics generated by xp is semiclassically exact."

The required property is item c on p. 356: "The Riemann dynamics does not have time-reversal symmetry. This is because
the statistics of the E_n are locally those of the gaussian unitary ensemble [...]".

**Sign of the oscillatory term (property f, p. 356).**
> "The Maslov phases associated with the orbits are also peculiar: they are all π. This follows from the negative signs
> of the terms in the von Mangoldt formula. The result appears paradoxical [...] but finds an explanation in the scheme
> of Connes."

**Other definitions in the paper.**
- Eq. (12), p. 358: H = ½(xp + px) = −iħ(x d/dx + ½). Eq. (14): ψ_E(x) = A/x^{1/2 − iE/ħ}.
- Eqs. (16)–(17), p. 359: x and p eigenfunctions are time-reverses of one another, with phase exp{±iθ(E/ħ)}.
- §4, p. 360: "It would be desirable to replace the semiclassical regularization of xp [...] with a quantum boundary
  condition that would generate a discrete spectrum in a natural way. We do not know how to do this".
- Eq. (25), p. 361: the integer-dilation superposition Σ_m ψ_E(mx) ∝ ζ(½ − iE). BK reject it: "we see no reason to impose
  this requirement [...] Even worse, putting E = E_n in (25) destroys the 'eigenfunction' by making it vanish for all x."
- Eq. (29), p. 362: the "quantum exchange" superposition gives 2cos θ(E) = 0, the first Riemann–Siegel term. BK show it
  has complex zeros, so (p. 363) "the vanishing of (29) is not a boundary condition corresponding to a hermitian
  operator."
- Eq. (32), p. 363: a combined condition ∝ Z(E) = 0. BK: "These conditions do generate the Riemann zeros, but we see no
  way to interpret either of them geometrically."
- Eqs. (34)–(39), §5: a Gauss-map condition. Numerically it "does not vanish at the Riemann zeros (figure 4)".

**What can be computed.** BK define no operator with a discrete spectrum.
- Eq. (9) is a smooth counting law only. Its "levels" are the solutions of N(E_n) = n (or n − ½): a smooth staircase,
  with **no fluctuations**.
- Eqs. (25) and (32) are the zeta function itself (ζ(½ − iE), Z(E)). They are **DEFINED BY THE ZEROS, so circular**.
- Eq. (29), cos θ(E) = 0, is a smooth zero set (first Riemann–Siegel term). It is computable to any height and does not
  use the zeros. BK show it is not a Hermitian spectrum: there are zeros off the line, and on-line zeros near
  s = ½ ± 0.82i that are not Riemann zeros.

### 1b. "The Riemann zeros and eigenvalue asymptotics"

- **Citation.** M. V. Berry & J. P. Keating, SIAM Review 41 (1999) 236–266, DOI 10.1137/S0036144598347497.
- **URL accessed.** https://michaelberryphysics.wordpress.com/wp-content/uploads/2013/06/berry307.pdf (published
  typeset text, Berry list item 307).
- **Status.** PRIMARY-READ.

Eq. (2.3), p. 239:

  ⟨N(t)⟩ ≡ θ(t)/π + 1 = (1/π)[arg Γ(¼ + ½it) − ½ t log π] + 1 = (t/2π) log(t/2πe) + 7/8 + O(1/t)

**Sign of the oscillatory term relative to Gutzwiller.**
- Riemann, eq. (2.6), p. 240: N_fl(t) = **−**(1/π) Σ_p Σ_m exp(−½ m log p) m⁻¹ sin{t m log p}.
- Gutzwiller, eq. (2.13), p. 242: N_fl(E) ∼ **+**(1/π) Σ_p Σ_m exp(−½ m λ_p T_p) m⁻¹ sin{m S_p(E)/ħ − ½ π m μ_p}.

p. 243:
> "the negative sign in (2.6) indicates that when the Maslov phases πmμ_p/2 are reinstated in (2.13) their value should
> be π for all orbits, but this is hard to understand because if the index is π for a given orbit it should be 2π for the
> same orbit traversed twice."

Eq. (2.18), p. 243, is written in that sign convention: "For the Riemann zeros [...] µ_j = 0, A_j = −log p / p^{m/2}".

**Time reversal (p. 242).**
> "the dynamics does not possess time-reversal symmetry. If it did, degeneracy of actions between each orbit and its
> time-reversed partner would lead to their contributing coherently to N(t), so that for most orbits [...] the prefactor
> in (2.6) would be 2/π rather than 1/π."

**XP regularisation (§6, p. 261).**
> "The result (unaltered by representing the Planck cell by a rectangle instead of a square) is that ⟨N(E)⟩ is precisely
> the asymptotics of the smoothed counting function for the Riemann zeros (last member of (2.3)), including the term 7/8,
> with t replaced by the energy E."

The Maslov correction is described here as "α/4π, where α is the angle turned through along the orbit". Eq. (6.3),
p. 261: H = ½(XP + PX) = −i(X d/dX + ½). p. 262: "The major problem remaining is to find boundary conditions that would
convert XP into a well-defined hermitean operator with discrete eigenvalues."

**What can be computed.** Same as 1a: a smooth law only. The SIAM paper defines no discrete operator.

---

## 2. Sierra & Townsend (2008), "Landau levels and Riemann zeros"

- **Citation.** G. Sierra & P. K. Townsend, Phys. Rev. Lett. 101 (2008) 110201, DOI 10.1103/PhysRevLett.101.110201,
  arXiv:0805.4079.
- **Version read.** arXiv **v2** (22 Sep 2008), LaTeX source and PDF. It was posted after publication and is assumed,
  not checked, to match the PRL text.
- **URL.** https://arxiv.org/abs/0805.4079.
- **Status.** PRIMARY-READ (arXiv v2).

**Hamiltonian.**
- Lagrangian, eq. (5), p. 2: L = (μ/2)(ẋ² + ẏ²) − (eB/c) ẏ x − eλ xy. This is a charge −e of mass μ in a uniform field B
  (Landau gauge A = Bx dy), with electric potential φ = −λxy.
- Hamiltonian, eq. (11), p. 2: **H = (1/2μ)[p̂_x² + (p̂_y + ħx/ℓ²)²] + eλ xy**, with ℓ² = ħc/eB (eq. 8) and
  p̂ = −iħ∂.
- Normal-mode frequencies, eq. (6): ω_c = (eB/μc) cosh ϑ and ω_h = i(eB/μc) sinh ϑ, with sinh 2ϑ = 2λμc²/(eB²). In the
  limit ω_c ≫ |ω_h| (eq. 7), ω_h ≈ iλc/B.
- After a unitary transformation (eq. 12, ħ = ℓ = 1): H_c = (ω_c/2)(p̂² + q²) and **H_h = (|ω_h|/2)(QP̂ + P̂Q)**.
- Lowest-Landau-level Lagrangian, eq. (8): L_LLL = p ẋ − |ω_h| xp, with p = ħy/ℓ². Quote: "This LLL model is the
  (unregularized) one-dimensional H = xp model."

**Regularisation and spectrum.**
- Box, eq. (9): |x| < L, |y| < L. This "implies for the LLL model a restriction on the phase space equivalent to that
  proposed by Connes".
- Semiclassical count, eq. (10), p. 2: N_sc(E) = (E/2π) log(L²/2πℓ²) − (E/2π) log(E/2π) + E/2π. The smooth Riemann term
  enters with a **negative** sign ("Connes [...] interpret[s] it as representing spectral lines missing from the
  continuum").
- Eigenfunctions, eqs. (14)–(16): confluent hypergeometric functions M(¼ + iE/2, ½, (x − iy)²/2ℓ²) (even) and the
  corresponding ¾, 3/2 functions (odd).
- Boundary identification (x, L) ~ (L, x), eq. (20), p. 3: ψ^η_E(x, L) = e^{iLx/ℓ² + iπ(η−1)/4} ψ^η_E(L, x). For the even
  sector this leads to the *asymptotic* condition, eqs. (21)–(22):

  **e^{2iθ(E)} (L²/2πℓ²)^{−iE} = 1**, hence eq. (23): **[ (E/2π) log(L²/2πℓ²) + 1 ] − N̄(E) = N_E** (an integer)

  The paper: "If the first term on the left hand side is interpreted as the regularization of the infinite number of
  states in a continuum, then we see that N̄(E) has the Connes interpretation as a count of states missing from this
  continuum." The odd sector gives "the phase of the odd Dirichlet L-functions".
- Fluctuations: absent. "As it stands, a counting of states in the model does not yield the full 'counting' formula for
  the Riemann zeros because the 'fluctuation term' is missing". Higher Landau levels are *speculated* to supply it
  (eqs. 24–29, semiclassical only).

**What can be computed.** A finite list, given L/ℓ: solve 2θ(E) − E log(L²/2πℓ²) = 2πN_E (eq. 22).
- Inputs are the Riemann–Siegel θ (a Gamma function) and L/ℓ. **No zeta zeros are used.**
- The count is bounded by |E| ≤ L²/ℓ² (stated on p. 2). It is an *absorption* count: continuum minus N̄. The levels are
  smooth (no fluctuations), so the model can serve as a smooth-only (Weyl-only) null, not as a candidate.
- The condition is derived from large-L asymptotic forms (eq. 17). It is not an exact eigenvalue problem; an exact
  computation would need the full 2D problem in the box, which the paper does not set up.

---

## 3. Sierra & Rodríguez-Laguna (2011), "The H = xp model revisited and the Riemann zeros"

- **Citation.** G. Sierra & J. Rodríguez-Laguna, Phys. Rev. Lett. 106 (2011) 200201, DOI 10.1103/PhysRevLett.106.200201,
  arXiv:1102.5356.
- **Version read.** arXiv **v1** (25 Feb 2011; the only arXiv version), LaTeX source and PDF. It predates PRL
  publication (May 2011), and the PRL text was **not** compared (paywalled). See Open issue 2.
- **Status.** PRIMARY-READ (arXiv v1).

**Hamiltonian.**
- Classical, eq. (3), p. 2: **H_cl = x (p + ℓ_p²/p), x ≥ ℓ_x, p ∈ ℝ**. The period, eq. (6), is
  T_E = cosh⁻¹(E/2h) → log(E/h), where "h ≡ ℓ_x ℓ_p should not still be identified with Planck's constant 2πħ".
- Quantum, eq. (8): Ĥ = x^{1/2}(p̂ + ℓ_p²/p̂)x^{1/2}, with ⟨x|p̂⁻¹|y⟩ = −(i/ħ)θ(y − x) (eq. 9).
- Action, eq. (10): Ĥψ(x) = −i x^{1/2}[ħ d/dx{x^{1/2}ψ} + ℓ_p² ∫_{ℓ_x}^∞ (dy/ħ) θ(y − x) y^{1/2} ψ(y)].
- Boundary condition, eq. (11), p. 2 (non-local): **ħ ℓ_x^{1/2} e^{iϑ} ψ(ℓ_x) + ℓ_p ∫_{ℓ_x}^∞ dx x^{1/2} ψ(x) = 0**,
  with ϑ ∈ [0, 2π). The deficiency indices are n₊ = n₋ = 1 (p. 3), so the self-adjoint extensions are U(1).
- Eigenfunctions, eq. (12): ψ_E(x) = x^{iE/2ħ} K_{½ − iE/2ħ}(ℓ_p x/ħ).
- **Quantisation condition, eq. (14), p. 3:**
  **Ξ_Ĥ(E) ≡ e^{−iϑ/2} K_{½ + iE/2ħ}(h/ħ) + e^{iϑ/2} K_{½ − iE/2ħ}(h/ħ) = 0.**
- Asymptotics, eqs. (15)–(16), as printed in v1:

  Ξ_Ĥ ≃ (4πħ/h)^{1/2} e^{−πE/4ħ} cos((E/2ħ) log(E/2he) − ϑ/2), which vanishes at
  (E/2πħ) log(E/2he) − ϑ/2π = n + ½.

  **[CC check]** The large-order asymptotics of K, and the 2019 review's eq. (5.16) (below), give log(E/(h e)), not
  log(E/(2he)). The numerics below confirm there is no (E/2π) log 2 drift, so the "2he" is a typo in arXiv v1.

**Parameters and the 7/8 question (p. 3).**
> "If h = 2πħ and ϑ = 5π/4, one recovers the semiclassical estimates for N(E) given in eqs. (2) and (7). [...] a better
> estimate of the average position of the Riemann zeros is obtained equating N(E) to a half integer n + ½, rather than an
> integer, which in view of eq.(16) yields ϑ = π/4."

The L-function generalisation, eq. (24), is E/ħ = t, h = 2πħ/q and ϑ = (π/4)(3 − 2a_χ − 2ε_χ). Note that eq. (2) of this
paper attributes the 7/8 to "a Maslov phase" (citing BK).

**Fluctuations.** None. The spectrum is the smooth count only. The paper (p. 4): "To achieve this goal one has of course
to find the quantum origin of the fluctuations of the Riemann zeros." Its Fig. 3 compares Ξ_Ĥ with Pólya's fake ξ*,
whose zeros are also real and smooth (eqs. 18–19).

**Later statement by Sierra (Symmetry 2019, review below).** The 2019 review flips the sign of the boundary condition
(eq. 5.10: ħ e^{iϑ} √U(ℓ_x) ψ(ℓ_x) = ℓ_p ∫ √V ψ). Its eigenvalue equation (5.14) is e^{iϑ}K_{½−iE/2ħ} − K_{½+iE/2ħ} = 0,
so ϑ₂₀₁₉ = ϑ₂₀₁₁ + π. The review **chooses ϑ = π** "Considering that the Riemann zeros form pairs [...] and that s = ½ is
not a zero". It then states (p. 10):

  eq. (5.16): cos((E/2ħ) log(E/ℓ_xℓ_p e)) = 0, and eq. (5.17): n(E) ≃ (E/2πħ)(log(E/ℓ_xℓ_p) − 1) − ½ + O(E⁻¹)

and, p. 10: "In both cases, the constant 7/8 in Riemann's formula (2.3) is missing." In the review's eq. (7.19) the
model becomes ξ_H(t) ≡ K_{½+it/2}(2π) + K_{½−it/2}(2π) = 0.

**[CC check: numerical levels.]** Script: `~/specarith_lit_cache/cc_check_srl_levels.py` (mpmath, 30 digits).
- Method: for real E and h, K_{½−iE/2}(h) is the complex conjugate of K_{½+iE/2}(h). So eq. (14) becomes
  2 arg K_{½+iE/2}(h) = ϑ + π (mod 2π). The script tracks the continuous phase on a grid with ΔE = 0.01 and finds the
  crossings. Settings: h = 2π, ħ = 1, E ≤ 200.
- Measured constant: c = (n − ½) − (E_n/2π)(log(E_n/2π) − 1).

| ϑ (2011 convention) | First levels | c at n = 5 / 20 / 40 / 60 / 78 | Reading |
|---|---|---|---|
| π/4 (the 2011 choice) | 19.150, 24.532, 29.020, 33.045, 36.769 | 0.013 / −0.063 / −0.086 / −0.095 / −0.100 | tends to **−1/8 ≡ 7/8 − 1** |
| 0 (= the 2019 choice, ϑ₂₀₁₉ = π) | 18.652, 24.084, 28.602, 32.648, 36.388 | 0.120 / 0.054 / 0.035 / 0.026 / 0.022 | tends to **0** |

- The Riemann smooth positions (θ(t)/π + 1 = n − ½) are 14.518, 20.654, 25.492, 29.739, 33.624, 37.257. With ϑ = π/4 the
  model's n-th level tracks Riemann smooth position n + 1: the model has no level near the first zero, 14.13.
- So the 2011 choice reproduces 7/8 **only modulo 1**: the exact count is one level short. The 2019 choice gives
  constant 0 in this midpoint convention. Sierra's "−½" is the same thing written for a zero-based index n. Neither
  choice gives 7/8 as an absolute constant.
- The spectrum with ϑ ∉ {0, π} (2011 convention) is not symmetric under E → −E (p. 3: "If ϑ ≠ π, all the eigenenergies
  are non vanishing and form time conjugate pairs {E_n, −E_n}"). The paper's own text is ambiguous here; this needs
  care if the sign of E matters.

**What can be computed.** Any number of levels, by root-finding the Bessel-K phase.
- Parameters: h = ℓ_xℓ_p (= 2πħ for ζ, 2πħ/q for L-functions) and ϑ.
- **No zeta zeros are used.** The output is a smooth, crystal-like spectrum. This is a calibrator, or a smooth-only null
  for G-gates, not a candidate that could carry log p structure.

### 3b. Sierra, "The Riemann zeros as spectrum and the Riemann hypothesis"

- **Citation.** G. Sierra, Symmetry 11 (2019) 494, DOI 10.3390/sym11040494, arXiv:1601.01797.
- **Version read.** arXiv **v4** (16 Apr 2019; LaTeX source and PDF). Equation numbers below are from the v4 PDF.
- **Status.** PRIMARY-READ (arXiv v4).

Concrete xp-type Hamiltonians defined in the review or in the papers it cites:

1. **H_BK = ½(xp̂ + p̂x)** on L²(0,∞), eqs. (3.1)–(3.2). It is essentially self-adjoint with a continuous spectrum ℝ.
   Quote: "The normal order quantization of xp does not exhibit any trace of the Riemann zeros."
2. **General U, V family**, eqs. (5.5)–(5.8): H = U(x)p + ℓ_p² V(x)/p, quantised as √U p̂ √U + ℓ_p² √V p̂⁻¹ √V. The
   boundary condition is (5.10). It covers:
   - **H_I = x(p + ℓ_p²/p)**, x ≥ ℓ_x (item 3 above). Eigenvalue equation (5.14).
   - **H_II = (x + ℓ_x²/x)(p + ℓ_p²/p)**, x ≥ 0 (Berry–Keating 2011, below). Count (5.18):
     n(t) ≃ (t/2π)(log(t/2π) − 1) − (8π/t) log(t/2π) + …
   - Source for the family: arXiv:1110.3203 (Sierra, J. Phys. A 45 (2012) 055209; ABSTRACT-READ). Quote: H_I corresponds
     to a flat spacetime, and its spectrum approaches the Riemann zeros "in average".
3. **Massive Dirac fermion in a Rindler wedge** (§7, eqs. (7.1)–(7.19)). It reproduces H_I with m = ℓ_p. Setting
   mℓ_x = 2π and ϑ = π gives ξ_H(t) above. Computable, smooth only.
4. **Massless Dirac fermion with δ-mirrors** (§10–12; original paper arXiv:1404.4252, J. Phys. A 47 (2014) 325204,
   ABSTRACT-READ).
   - Definition: H = diag(−i(ρ∂_ρ + ½), +i(ρ∂_ρ + ½)), eq. (10.5), on ∪ I_n, with I_n = (ℓ_n, ℓ_{n+1}).
   - Matching: χ(ℓ_n⁻) = L(ϱ_n)χ(ℓ_n⁺), eqs. (10.6) and (10.8), with boundary phase −ie^{iϑ}χ₋(ℓ₁⁺) = χ₊(ℓ₁⁺).
   - Choice: **ℓ_n = n^{1/2}, ϱ_n = μ(n)/n^{1/2}**, eq. (11.4).
   - Result, eq. (11.11), heuristic: "If ζ(½ ± iE_n) = 0 and e^{2i(ϑ+θ(E_n))} = 1 ⟺ H_ϑ χ_{E_n} = E_n χ_{E_n}". The
     "rigorous" version, eq. (12.33), is ϑ = −(θ(E) + (π/2) sign Z′(E)).
   - Quote, p. 26: "this spectral realization of the zeros requires the fine tuning of the parameter of ϑ in terms of the
     phase of the zeta function [...] This realization is different from the Pólya–Hilbert conjecture of a single
     Hamiltonian encompassing all the Riemann zeros at once."
   - p. 28: "if ϑ does not satisfy Eq.(12.33), then the norm of the state will diverge badly and so the zero E will be
     missing in the spectrum. [...] if E is not a zero, we expect that the state will belong generically to the
     continuum." The spectrum is a continuum (bands) with zeros only as tuned bound states.
   - **FLAG: the discrete part is DEFINED by the zeros (one ϑ per zero, set from θ(E_n)), so testing it against the zeros
     is circular.** A finite truncation to mirrors n ≤ N is buildable from §10–12, but the paper's discrete levels need
     the zeros as input.
5. **Modified-prime variants** (§14, eqs. (14.3)–(14.9)): ϱ_n = μ*(n)/n^{1/2} from a sequence q_n with the same ζ zeros.
   Same circularity.

Other Sierra xp papers (ABSTRACT-READ only, from arXiv abstracts retrieved 2026-10-07):
- **math-ph/0702034** (Nucl. Phys. B 776 (2007) 327). xp plus a non-local interaction set by two potentials. A Jost
  function has "resonances [that] converge asymptotically toward the average position of the Riemann zeros". A
  dilation superposition gives a Jost function "whose real part vanishes at the Riemann zeros".
- **0712.0705** (New J. Phys. 10 (2008) 033016). xp with boundary wave functions: "a continuum spectrum with discrete
  bound states embedded in it". The boundary functions "giving rise to the Riemann zeros, are found using the
  Riemann-Siegel formula of the zeta function". Zeta enters the construction (likely circular; not checked).

### 3c. Berry & Keating (2011), "A compact hamiltonian with the same asymptotic mean spectral density as the Riemann zeros"

- **Citation.** M. V. Berry & J. P. Keating, J. Phys. A 44 (2011) 285203, DOI 10.1088/1751-8113/44/28/285203.
- **URL.** https://michaelberryphysics.wordpress.com/wp-content/uploads/2013/07/berry440.pdf (published version).
- **Status.** PRIMARY-READ.

**Definitions.**
- Hamiltonian, eq. (1.3): **H = (x + 1/x)(p + 1/p)**. Scaling, eq. (1.2): x′ = l_x x, p′ = l_p p, η = ħ/(l_x l_p) (1.5).
- Ordering, eq. (2.1): H = √(x + 1/x)(p + 1/p)√(x + 1/x).
- Reduced to the ODE χ″ = (h/η² + ig/η)χ, eqs. (2.8)–(2.9), with h(x) = 1 − E²x²/(4(1 + x²)²) and
  g(x) = E(1 − x²)/(2(1 + x²)²).
- Hermiticity boundary condition, eq. (2.22): **∂_xφ(0)/φ(0) = (1/η) exp(iα)**. The derivation makes it non-local.
- Semiclassical rule, eq. (1.6): A(E_n) ≈ E_n(log E_n − 1) = 2π(n + ½)η.
- Identification, eq. (5.3): E = t/2π, η = 1/2π. The choice is α = 0 (§5: α = π is excluded because it gives E = 0).
- Count, eq. (5.7): N_{t,α=0}(t) = (t/2π)(log(t/2π) − 1) − (8π/t) log(t/2π) + …, against Riemann's eq. (5.6) with + 7/8.
  **No 7/8.**

Quote (§6):
> "we are not claiming that our hamiltonian (1.3) has an immediate connection with the Riemann zeta function [...] For
> (1.3), there is a single primitive periodic orbit for each energy E [...] This absence of connection with the primes is
> shared by all variants of xp".

**What can be computed.** Levels by shooting, eq. (3.3): C₊(E) = 0, with "x ⩽ 30" sufficient. **No zeta input.** Smooth
spectrum only. The paper itself predicts no log p structure (one primitive orbit per energy).

### 3d. Two further computable xp discretisations found while searching for item 4

**Bolte, Egger & Keppeler, "The Berry–Keating operator on a lattice".**
- Citation: J. Phys. A 50 (2017) 105201, DOI 10.1088/1751-8121/aa5844, arXiv:1610.06472. Version read: arXiv v2,
  PRIMARY-READ.
- Construction: Weyl quantisation of the symbol h(x, ξ) = (ξ² − x²)/2 (xp rotated, eq. 2.5), periodised on a torus,
  eq. (2.8).
- Operator, eq. (2.16): an **N×N Hermitian difference operator**:
  (op_N(h)ψ)_l = (ℓ_ξ²/24)ψ_l + (ℓ_ξ²/4π²) Σ_m ((−1)^m/m²)(ψ_{l+m} + ψ_{l−m}) − ½(lℓ_x/N)²ψ_l, with 2πħN = ℓ_ξℓ_x
  (eq. 2.14).
- Finite-sum form used for diagonalisation: eq. (5.1). Matrix elements: eq. (B.11). Numerics in the paper: N up to
  2000, with ℓ_x = ℓ_ξ = √(2πN).
- A logarithmic density, d̄(E) = (1/π) log(E/2π), eq. (4.16), appears only when the torus size is tied to E
  (eq. 4.13), and it is twice BK's. Quote (p. 16): "our analysis clearly demonstrates the limitations of modelling the
  Riemann zeros with the eigenvalues of an operator that is a quantisation (of an established nature) of H(q, p) = qp."
- **Computable and uses no zeta input.** This is a genuine finite-basis xp candidate (not BBM).

**Srednicki, "The Berry–Keating Hamiltonian and the local Riemann hypothesis".**
- Citation: J. Phys. A 44 (2011) 305202, arXiv:1104.1850. Version read: arXiv v3, PRIMARY-READ.
- In the harmonic-oscillator basis, H_BK = (1/2i)(â†â† − ââ) (eq. 25). Matrix elements, eqs. (26)–(27):
  ⟨k|H_BK|k′⟩ = b*_{k′+1}δ_{k,k′+1} + b_{k′}δ_{k,k′−1}, with **b_k = −(i/2)[(2k + δ)(2k + δ − 1)]^{1/2}**
  (a tridiagonal matrix).
- Eq. (24): the truncation to oscillator levels n < N has eigenvalues equal to the zeros of the modified gamma factor
  Γ_{∞,N}(½ + iE) (the "local Riemann hypothesis"). These are **not** Riemann zeros.
- **Computable finite xp matrix with an exactly known spectrum.** Possibly useful as a known-answer fixture for the
  pipeline. It is not a Riemann candidate.

---

## 4. Bender, Brody & Müller (2017) and all disputes found

### 4a. The paper

- **Citation.** C. M. Bender, D. C. Brody, M. P. Müller, "Hamiltonian for the zeros of the Riemann zeta function",
  Phys. Rev. Lett. 118 (2017) 130201, DOI 10.1103/PhysRevLett.118.130201, arXiv:1608.03679.
- **Version read.** arXiv **v4** (6 Mar 2017; source file "LW15132_Brody.tex", the PRL manuscript code). The published
  text was not compared.
- **Status.** PRIMARY-READ.

**Operator, eq. (1), p. 1:**

  **Ĥ = (1 − e^{−ip̂})⁻¹ (x̂p̂ + p̂x̂) (1 − e^{−ip̂})**, with ħ = 1 and p̂ = −i∂_x on ℝ⁺.

- Eq. (2): Δ̂f(x) = f(x) − f(x − 1).
- Eq. (3): Δ̂⁻¹ = (ip̂)⁻¹ Σ_n B_n (−ip̂)^n/n!, Borel-summed, "with boundary at infinity".
- Classical limit: "H = 2xp when x̂ and p̂ commute".

**Eigenfunctions and how the boundary condition becomes ζ(z) = 0 (p. 2), verbatim.**
> "The solutions to the eigenvalue differential equation Ĥψ = Eψ are given in terms of the Hurwitz zeta function
> ψ_z(x) = −ζ(z, x+1) on the positive half line ℝ⁺ (the negative sign is our convention), with eigenvalues i(2z−1)."
>
> "Next, we impose the boundary condition that ψ_z(0) = 0 [...] Because −ψ_z(0) = ζ(z) is the Riemann zeta function, the
> boundary condition that we have used implies that z must belong to the discrete set of zeros of ζ(z)."
>
> "the eigenvalues E_n = i(2z_n − 1) are discrete and z_n = ½(1 − iE_n) are the nontrivial zeros of the Riemann zeta
> function. The Riemann hypothesis is valid if and only if these eigenvalues are real."

- The trivial zeros are excluded because their eigenstates grow as x^{2n+1} (p. 2).
- Metric: η̂ = sin²(½p̂). With ρ̂ = Δ̂ the paper obtains ĥ^BK = x̂p̂ + p̂x̂, and the quantisation condition becomes
  lim_{x→0}[φ_z^BK(x) − ζ(z, x−1)] = 0 (p. 3).
- Biorthogonality, eq. (6): ⟨ψ̃_m|ψ_n⟩ = ∫₀^∞ dx x^{−1+i(E_n−Ē_m)/2}.
- Domain left open (p. 4): "Identifying the domain of Ĥ remains a difficult and open problem."
- Footnote [rX]: a one-parameter family Δ_ε = ε⁻¹(1 − e^{−iεp̂}), with eigenstates ∝ −ζ(z, 1 + x/ε). This is a
  continuous deformation, not a discretisation.

**What can be computed.** In the paper, the eigenvalue condition **is** ζ(z) = 0, imposed through the boundary value of a
Hurwitz zeta function. **FLAG: the spectrum is DEFINED BY THE ZETA ZEROS. Computing "BBM levels" means computing zeta
zeros, so a test against the zeros is circular** (decision 7).

### 4b. Disputes, replies and follow-ups found

1. **Bellissard, "Comment on 'Hamiltonian for the zeros of the Riemann zeta function'".** arXiv:1704.02644v1
   (9 Apr 2017). PRIMARY-READ (arXiv). No published PRL Comment was found: a Crossref title search was negative, and
   Crossref has no relation metadata on the BBM DOI. Core objections, verbatim:
   - Problem 1 (p. 1–2): "in the present case p̂ admits n₊ = 1, n₋ = 0, so that p̂ has no selfadjoint extension. Hence the
     argument proposed in the paper cannot be used." Also, on the translation S: "if restricted to ℋ = L²(0,+∞) it is
     not [unitary]. It is only a partial isometry."
   - Problem 2 (p. 2): "the wave function ψ_z is not an eigenvector for Re z = 1/2". On the weighted-space cure: "The
     constant term on the r.h.s. changes the eigenvalue problem and does not give the line Re z = 1/2 anymore."
   - Conclusion: "As attractive this idea looks, it does not hold when checking the analysis part of the problem."
2. **Bender, Brody & Müller, "Comment on 'Comment on "Hamiltonian for the zeros of the Riemann zeta function"'"**
   (the reply). arXiv:1705.06767v1 (18 May 2017). PRIMARY-READ. Core points, verbatim:
   - "nowhere in [2] is it claimed to have shown that the eigenvalues of Ĥ are real".
   - "the selfadjointness of p̂ is never postulated or used".
   - "whether or not ζ(z, x+1) is an element of L²(0,+∞) with respect to the Lebesgue measure is not a relevant question
     to ask in the context of pseudo-Hermitian operators".
   - "the remarks of [1] do not invalidate the arguments of [2]".
3. **M. P. Müller, "A note on 'Hamiltonian for the zeros of the Riemann zeta function'".** arXiv:1704.04705v2
   (27 Sep 2017). PRIMARY-READ.
   - Builds a rigorous variant R = Xp + pX with X := Σ x Δ (Σ = fractional-sum operator), on a space of functions (not a
     Hilbert space).
   - Theorem 11: the eigenvalues with f(0) = 0 are exactly {0} ∪ {i(2s_n − 1) : s_n a nontrivial zero}.
   - Concedes: "the above does not give us any additional information about the spectrum of R, and we have mostly omitted
     the discussion of how one might equip the linear space with the structure of a Banach or Hilbert space."
   - Again the spectrum is defined by ζ(s) = 0.
4. **Bender & Brody, "Asymptotic analysis on a pseudo-Hermitian Riemann-zeta Hamiltonian".** J. Phys. A 51 (2018)
   135203, DOI 10.1088/1751-8121/aab068, arXiv:1710.04411v2. PRIMARY-READ (abstract and introduction).
   - WKB asymptotics of the eigenfunctions. The momentum-space formulation is "a challenging open problem".
   - Contains no numerics or truncation.
5. **F. I. Moxley III, "A Schrödinger equation for solving the Bender–Brody–Müller conjecture".** AIP Conf. Proc. 1905
   (2017) 030024. **UNVERIFIED** (not opened). Secondary description in Liu 2026 (item 7): Moxley "observed that a formal
   state redefinition conjugates the BBM eigenvalue equation to a dilation equation". A preprint seems to exist at
   preprints.org 201712.0149 (not opened).
6. **E. Yakaboylu, "Hamiltonian for the Hilbert–Pólya conjecture".** J. Phys. A 57 (2024) 235204, arXiv:2309.00405v6.
   PRIMARY-READ (abstract and introduction).
   - A different similarity-transformed BK operator with a Dirichlet boundary condition. Its eigenfunctions "vanish at
     the origin by the nontrivial zeros of the Riemann zeta function".
   - Cites BBM as satisfying only "stage (I)". **Same circularity** (eigenvalues defined by the zeros).
7. **Kejun Liu, "Metric completion of the Bender–Brody–Müller Hamiltonian: dilation spectrum and missing eigenstates".**
   arXiv:2607.19067v1 (21 Jul 2026). PRIMARY-READ (abstract, introduction, references).
   - The L²-based completion under BBM's metric η̂ = sin²(p̂/2) is unitarily equivalent to L²(ℝ₊), and its free
     realisation is the dilation generator with "purely absolutely continuous spectrum ℝ".
   - Quote: "the original BBM boundary-condition/eigenfunction mechanism cannot produce point-spectrum Riemann-zero
     states in this L²-based metric completion".
   - Liu's survey of prior work (p. 1) lists exactly items 1, 2, 4, 5 and 6 above.
8. **Bishop, Aiken & Singleton, "Modified commutation relationships from the Berry–Keating program".** arXiv:1810.03976v3
   (journal reference not checked). PRIMARY-READ (abstract).
   - "we assume the validity of a version of the Bender–Brody–Müller variant [...] this larger family generalizes the
     Bender–Brody–Müller approach". It assumes BBM; it does not test or discretise it.
9. **Das & Kalauni, "Supersymmetry and the Riemann zeros on the critical line".** Phys. Lett. B 791 (2019) 265,
   arXiv:1810.02204v3. PRIMARY-READ (abstract).
   - The energy eigenvalues "correspond to the Riemann zeta function", and the zeros "arise naturally from the vanishing
     ground state energy condition". Zeta is built in, so it is circular in the same sense.

### 4c. CRUCIAL question: an independent finite-basis discretisation of BBM?

**None found.** No paper read or surfaced gives a finite-matrix truncation of the BBM operator whose eigenvalues are
computed without solving ζ = 0. What exists instead:
- discretisations of **xp** (Bolte–Egger–Keppeler 2017; Srednicki 2011, items 3d);
- rigorous or asymptotic analyses of BBM (Müller 2017; Bender–Brody 2018; Liu 2026);
- generalisations that assume BBM (Bishop et al.);
- Connes's remark that his absorption construction "yields an explicit construction of a large matrix whose spectrum
  approaches the zeros of zeta as Λ → ∞" (Connes 1999, arXiv p. 49). That matrix is Connes's, not BBM's, and is an
  absorption-picture construction.

Searches run on 2026-10-07:
- Web (extended): "reply to comment Bellissard 'Hamiltonian for the zeros of the Riemann zeta function' Bender Brody
  Müller".
- Web (extended): "Bender Brody Müller Hamiltonian Riemann zeros numerical diagonalization finite matrix truncation
  eigenvalues".
- Web (extended): "'Bender' 'Brody' 'Müller' Riemann Hamiltonian follow-up critique arXiv 2018 2019 2020 pseudo-Hermitian
  xp Hurwitz zeta eigenfunctions".
- Web (extended): "'Bender-Brody-Müller' OR 'Bender–Brody–Müller' Riemann operator numerically computed eigenvalues
  discretization".
- Web: "'Domain and Eigenvalues of the Bender-Brody-Müller Hamiltonian'". This is an academia.edu item, HTTP 403, not
  opened, author unknown (see Open issues).
- arXiv API: ti:"pseudo-Hermitian Riemann"; abs:"Bender-Brody-M" OR abs:"Bender, Brody"; au:Kalauni AND au:Das;
  au:Moxley AND ti:Riemann (no arXiv hits).
- Crossref: title search for a published Comment (negative); the BBM DOI record shows 91 citations and empty relation
  metadata.

Limits: the ~91 citing works were **not** enumerated one by one; only the works surfaced by the searches above were
checked. A citing-articles sweep (Google Scholar / INSPIRE) is the remaining way to raise confidence. Under decision 7,
the current state gives **BBM = INAPPLICABLE**.

---

## 5. Dilation operator on a finite interval

**Primary result found: Endres & Steiner (2010).**
- Citation: S. Endres & F. Steiner, "The Berry–Keating operator on L²(ℝ_>, dx) and on compact quantum graphs with general
  self-adjoint realizations", J. Phys. A 43 (2010) 095204, DOI 10.1088/1751-8113/43/9/095204, arXiv:0912.3183.
- Version read: arXiv v5. Status: PRIMARY-READ.
- Operator, eq. (4), p. 4: H_BK = ½(xp + px) = −iħ(x d/dx + ½). The eigenvalue λ = ħk, with s := −½ + ik (eq. 7).
- On the half-line it is essentially self-adjoint ("both deficiency indices are equal to zero"), with continuous spectrum.

**Single edge I = [a, b], Example 16.2, p. 29, verbatim (eqs. 148–150):**
> "For a single edge I = [a,b] (one-dimensional quantum billiard) [...] with S(A,B) =: e^{−2πic} (148) to
> ψ(a) = S(A,B) √(b/a) ψ(b) = √(b/a) e^{−2πic} ψ(b) with c ∈ [0,1). (149)
> The eigenvalue spectrum is given by
> k_n = (2π / ln(b/a)) (n + c) with c ∈ [0,1) and n ∈ ℤ. (150)"

In the brief's notation (l = a, L = b, θ = −2πc), eq. (149) is √l ψ(l) = e^{−2πic}√L ψ(L), i.e.
**√L ψ(L) = e^{iθ}√l ψ(l)**. Eq. (150) is **E log(L/l) = θ + 2πn**, equally spaced with spacing 2π/log(L/l). This
**verifies decision 4's corrected boundary condition and the picket-fence (G4) spectrum.**

**[CC check]** The brief v1 form ψ(L) = e^{iθ}ψ(l) cannot hold for real E. With ψ = x^{−1/2+iE}, it would need
|L^{−1/2}| = |l^{−1/2}|. So the √ weights are required, as decision 4 says.

Related statements in the same paper:
- Theorem 15.5 (p. 27), Weyl's law on any compact graph: N(k) ∼ (L/π) k, with L = Σ l_i (eq. 135) the total length. It
  is linear, not k log k.
- Theorem 15.6 (p. 28), "No-go theorem": "Neither H_BK nor H²_BK yields as eigenvalues the nontrivial Riemann zeros if
  these are self-adjoint realizations on any compact graph."
- Example 16.3 (p. 33): on [1, b], the periodic orbits have lengths n ln b, all repetitions of one primitive orbit of
  length T = ln b, and S(A, B) = e^{−2πic} = e^{−iπμ/2}. This is the "one spike family at its own period" of G4.

**Template from Bonneau, Faraut & Valent (2001).**
- Citation: "Self-adjoint extensions of operators and the teaching of quantum mechanics", Am. J. Phys. 69 (2001) 322,
  DOI 10.1119/1.1328351, arXiv:quant-ph/0103153. Version read: arXiv v1. Status: PRIMARY-READ.
- They treat the **momentum** operator, not the dilation operator. §5.3, eqs. (14)–(15), p. 8:
  D_θ = {ψ ∈ D_max(0,L), ψ(L) = e^{iθ}ψ(0)}, P_θφ_n = (2πħ/L)ν φ_n, with ν = n + θ/2π.
- **[CC check]** The dilation result maps onto this one under u = log x with φ(u) = e^{u/2}ψ(e^u), which is unitary from
  L²([l, L], dx) to L²([log l, log L], du). The √x weight in the boundary condition is the Jacobian. The same map appears
  in the Sierra review as eq. (13.1): ψ(ρ) = e^{x/2}ψ(e^x).

**Twamley & Milburn, "The quantum Mellin transform".**
- Citation: New J. Phys. 8 (2006) 328, arXiv:quant-ph/0702107. PRIMARY-READ (searched).
- They cite the finite-interval *momentum* case (their refs 11, 12) but do **not** give the interval-dilation spectrum.
  Not needed.

---

## 6. Connes (1999), background only

- **Citation.** A. Connes, "Trace formula in noncommutative geometry and the zeros of the Riemann zeta function", Selecta
  Math. (N.S.) 5 (1999) 29–106, DOI 10.1007/s000290050042, arXiv:math/9811068.
- **Version read.** arXiv v1 (10 Nov 1998). The Selecta pagination was not compared; page numbers below are arXiv pages.
- **Status.** PRIMARY-READ (arXiv).

Connes opens (p. 2): "The spectral interpretation of the zeros of zeta will be as an absorption spectrum, i.e. as missing
spectral lines." The reason is the sign.
- Gutzwiller (his eq. 6, p. 6) has N_osc ≃ **+**(1/π) Σ_γ Σ_m (1/m) [2 sh(mλ_p/2)]⁻¹ sin(S_pm(E)).
- The Euler product gives (eq. 7) N_osc ≃ **−**(1/π) Σ_p Σ_m (1/m) p^{−m/2} sin(mE log p).
- "two important mismatches [...] The first one is the overall minus sign in front of formula (7)".
- In the function-field case the zeros live on H¹, "which appears with an overall minus sign in the Lefchetz formula".
  Hence (p. 8): "(C) The Polya-Hilbert space H should appear from its negative ⊖H. In other words, the spectral
  interpretation of the zeros of the Riemann zeta function should be as an absorption spectrum rather than as an emission
  spectrum".
- His xp count with cutoffs |q|, |p| ≤ Λ (eqs. 35–43, pp. 47–48) gives 2E/2π log Λ − (E/2π)(log(E/2π) − 1). There, "the
  overall term ⟨N(E)⟩ [...] appears with a minus sign".
- p. 50: "the computation of [BK] is actually coincidental [...] What [BK] had not taken into account is that the
  spectral interpretation of [Co] is as an absorption spectrum rather than an emission spectrum."

Relevance to Phase 6: an "absorption" candidate (Connes, Sierra–Townsend, the continuum part of Sierra 2014) predicts
log p structure with the **opposite sign** to an emission spectrum. A G-gate sign arm separates the two. Srednicki's
PRL 107 (2011) 100201 (arXiv:1105.2342, ABSTRACT-READ) offers a different resolution: a class-C "nonclassical two-valued
degree of freedom" with "a phase factor of −1".

---

## Summary: what each candidate gives as a list of levels

| Candidate | Levels computable without the zeros? | Finite list? | Fluctuations? | Notes |
|---|---|---|---|---|
| BK 1999 cell count (eq. 9) | yes (smooth law) | n/a | none | constant +1 (area) or 7/8 (guessed Maslov) |
| Interval dilation (ES eq. 150) | yes, exact | any n | none: exact picket fence | G4 calibrator; spacing 2π/log(L/l) |
| Sierra–Townsend LLL (eq. 22) | yes (θ only) | yes, bounded by L²/ℓ² | none | absorption sign; asymptotic condition |
| Sierra–RL x(p + ℓ_p²/p) (eq. 14) | yes (Bessel K) | any number | none | the ϑ choice sets the constant: −1/8 (2011) or 0 (2019) [CC check] |
| BK 2011 (x + 1/x)(p + 1/p) | yes (ODE shooting) | any number | none | no 7/8; one primitive orbit per energy |
| Bolte–Egger–Keppeler lattice | yes (N×N matrix) | N levels | not studied in the paper | finite-basis xp; log density only with E-linked torus |
| Srednicki truncation | yes (tridiagonal matrix) | N/2 | n/a | eigenvalues = local-RH zeros, not Riemann zeros |
| Sierra 2014/2019 Dirac mirrors | **no**: discrete levels need ϑ tuned per zero | — | — | **CIRCULAR** |
| BBM 2017 (and Müller 2017, Yakaboylu 2024, Das–Kalauni) | **no**: the eigencondition is ζ(z) = 0 | — | — | **CIRCULAR**; no independent discretisation found, so INAPPLICABLE |

---

## Open issues

1. **The brief's "1 against 7/8" needs one more clause.** BK's own eq. (9) claims 7/8, through a *guessed* Maslov term
   −1/8 that later work (Endres–Steiner; Connes) calls unjustified or coincidental. Suggested wording: "the bare
   cell-count constant is 1; BK's heuristic Maslov correction gives 7/8 (eqs. 8–9)".
2. **PRL versus arXiv.** S-RL (arXiv v1, Feb 2011) predates the PRL by about 3 months, and the PRL text was not compared.
   Two items in v1 should be checked against the published version before the Phase 6 seal cites equation numbers: the
   "log(E/2he)" typo in eqs. (15)–(16), and the ϑ = π/4 statement. Sierra–Townsend v2 and BBM v4 are probably final
   but were also not compared.
3. **Conflicting ϑ choices in S-RL (2011) and Sierra (2019).** With the 2011 choice the constant is −1/8 [CC check],
   i.e. 7/8 − 1, missing the first level. With the 2019 choice it is 0 (index-convention form "−½"). If S-RL is used as a
   calibrator, pre-register ϑ and the counting convention. Also re-run `cc_check_srl_levels.py` at higher E (the
   constant converges slowly, roughly as 1/E) before treating −1/8 as established.
4. **Is BBM INAPPLICABLE?** No independent finite-basis discretisation was found, but the ~91 citing works were not swept
   one by one. Two items are unread:
   - the academia.edu item "Domain and Eigenvalues of the Bender-Brody-Müller Hamiltonian" (HTTP 403, author unknown);
   - Moxley, AIP Conf. Proc. 1905, 030024 (2017).

   An INSPIRE or Google Scholar citing-articles sweep would close this.
5. **BK 1999 (book chapter) was read from a scan.** Equation numbers and quotes were transcribed from page images, not
   from extractable text.
6. **The Sierra–Townsend levels come from an asymptotic boundary condition.** Eq. (22) follows from the large-L forms
   (17), so it is not an exact finite spectrum. A 2D box computation would be new work, and decision 7's spirit ("do not
   invent post hoc") arguably applies.
7. **Connes was read in the arXiv version only.** Selecta page numbers are not given.
8. **Out of scope here, still open from the brief.** Landau's 1911 formula (G0 sign and weight) and the desymmetrised
   Selberg formula (G1) were not fetched in this pass.
