# GEO1 Step 0: length spectrum of the modular surface and the Picard group (literature; no compute)

**Status (2026-10-27):** literature only; hand arithmetic only; nothing sealed or run. Of the 9 claims, 6 are VERIFIED in a primary text (some in corrected form). 3 primary sources could not be read: Sarnak 1982 JNT (the bot check blocked it), Sarnak–Wakayama 1999 Duke, and the EGM book. Their content is reported only through other primary papers and marked UNVERIFIED. The PDFs were read under `/tmp/claude-1000/geo1_lit/` and are not in the repo.

Conventions used below. Γ = PSL(2,ℤ). "Class" means a primitive hyperbolic Γ-conjugacy class, which is the same as an **oriented** primitive closed geodesic. t = |tr γ|. 𝒟 = {d > 0 : d ≡ 0,1 mod 4, d not a square}. h(d) = number of SL(2,ℤ)-classes (proper equivalence) of primitive forms [a,b,c] of discriminant d. ε_d = (t_d + u_d√d)/2, where (t_d,u_d) is the least positive solution of t² − d u² = 4.

---

## 1. Closed geodesics ↔ classes ↔ forms; ℓ = 2 arccosh(t/2) = 2 log ε_d

**Statement (Sarnak 2007, p. 224, verbatim summary):** "The primitive hyperbolic conjugacy classes are in 1-1 correspondence with classes of forms of discriminants d ∈ 𝒟. To each such d, there are h(d) = |F_d| such classes all of which have a common trace t_d and norm ε_d²."
- Each p gives an *oriented* primitive closed geodesic of length log N(p), with N(p) = [(t + √(t²−4))/2]² (p. 218).
- F_d is the set of classes of primitive forms of discriminant d under σ(Γ), i.e. SL(2,ℤ) substitutions (pp. 221–222, eqs. (25)–(26)).
- The bijection is n(p) = δ⁻¹ sgn(a+d)[b, d−a, −c] for p = (a b; c d) (eq. (27)), with inverse eq. (30).
- Automorphs: Aut_Γ(f) = {((t−bu)/2, au; −cu, (t+bu)/2) : t² − du² = 4}/±1 (eq. (31)).
- Units: η_d is the fundamental solution of t² − du² = ±4. If −4 is solvable then ε_d = η_d², otherwise ε_d = η_d (p. 223).

**Sources:**
- P. Sarnak, "Reciprocal geodesics", *Clay Math. Proc.* 7 (2007) 217–237. Read in full.
- Corroborated by M. Pollicott, *Bull. SMF* 114 (1986) 431–446, Prop. 4 (p. 443), stated there as "due to Sarnak": "one-to-one correspondence between closed geodesics … and equivalence classes of quadratic forms … length 2 log ε_d."
- ℓ ↔ trace: E. Bogomolny, "Quantum and arithmetical chaos", arXiv:nlin/0312061, eq. (58), "2 cosh(l_p/2) = |Tr M|".

**STATUS: VERIFIED** (Sarnak 2007, pp. 218, 221–224). log[(t+√(t²−4))/2] = arccosh(t/2), so ℓ = 2 arccosh(t/2) = 2 log ε_d.

**Notes and corrections:**
- **Which equivalence:** *proper* (SL(2,ℤ)) equivalence, with h(d) = |F_d|. Modern sources call this the narrow-sense class number h⁺ of the order of discriminant d. Hashimoto (arXiv:0807.0056v1, p. 1) says "class number of D in the narrow sense". That identification is standard but secondary here.
- It is **not** the wide class number: h⁺(d) = h(d) when N(η_d) = −1, and h⁺(d) = 2h(d) otherwise.
- **Orientation:** the bijection is with *oriented* geodesics. Time reversal p ↦ p⁻¹ corresponds to f ↦ −f (Sarnak 2007, (iii)). Mirror conjugation by w = diag(1,−1) corresponds to f ↦ [−a,b,−c] (iv). Improper substitution f ↦ [a,−b,c] corresponds to φ_A = mirror∘reversal (v).
- So improper (GL(2,ℤ)) equivalence does **not** correspond to "unoriented geodesic".
- Unoriented geodesics of discriminant d number (h(d) + r(d))/2, where r(d) = ν(d) (number of genera) if d ∈ 𝒟_R and 0 otherwise. *Derived here* from Sarnak 2007 eqs. (8), (41) and the orbit count of the involution f ↦ −f.
- "ε_d = fundamental solution of t² − du² = 4" is correct as phrased. It equals the fundamental unit only when N(η_d) = +1.
- The original 1982 source (JNT 15, 229–247) was **not read** (see claim 3). Peter (2002) cites it as "[Sarnak 1982], Corollary 1.5" for "lengths 2 log ε_d with multiplicities h(d)". That location is UNVERIFIED.

## 2. Multiplicity at trace t

**Correct statement:** g(t) = number of classes with trace t = Σ_{d ∈ 𝒟 : t_d = t} h(d). The condition is that (t,u) is the **fundamental** solution for d.

**Source:** M. Peter, "The correlation between multiplicities of closed geodesics on the modular surface", *Commun. Math. Phys.* 225 (2002) 171–189 (volume and pages from Hashimoto's reference list); arXiv:math/0104234.
- p. 4, eq. (2.1): "α(n) = (log n/n) Σ_{d: tr(ε_d)=n} h(d)", where g(n) = "number of closed geodesics … [of] primitive conjugacy classes with trace n".
- Equivalent to the Sarnak 2007 p. 224 summary ("common trace t_d").

**STATUS: VERIFIED** (Peter 2002 eq. (2.1); Sarnak 2007 p. 224).

**Correction to the PI's phrasing:** Σ h(d) over all d with t² − 4 = d u² (u ≥ 1) counts **all** hyperbolic classes of trace t, primitive and non-primitive. *Derived here:*
- Any hyperbolic p of trace t maps to (u, f), where u = gcd of the off-diagonal/difference entries and f is a primitive form of discriminant (t²−4)/u².
- Conversely, Sarnak's eq. (30) with (t,u) in place of (t_d,u_d) rebuilds p. Integrality holds because t ≡ bu mod 2.
- If (t,u) is not fundamental, then (t+u√d)/2 = ε_d^k with k ≥ 2, and the class is a k-th power.
- So: primitive count = sum restricted to fundamental (t,u); total count = unrestricted sum. h is h⁺ as in claim 1. d ranges over 𝒟; t² − 4 is never a square for t ≥ 3.
- Every t ≥ 3 occurs: (t,1) is fundamental for d = t² − 4, so g(t) ≥ h(t²−4) ≥ 1.

**Hand checks** (class numbers hand-derived from reduced forms or the order class-number formula; lengths from known logs, ≈):

| t | t²−4 | (d,u) pairs | fundamental? | h(d) | g(t) primitive | all classes | ℓ = 2 arccosh(t/2) |
|---|---|---|---|---|---|---|---|
| 3 | 5 | (5,1) | yes | h(5)=1 [1,1,−1] | 1 (RL) | 1 | 1.9248 |
| 4 | 12 | (12,1); u=2 gives d=3 ∉ 𝒟 | yes | h(12)=2 [1,2,−2],[−1,2,2] | 2 (R²L, RL²) | 2 | 2.6339 |
| 5 | 21 | (21,1) | yes | h(21)=2 (h_K=1, no unit of norm −1) | 2 (R³L, RL³) | 2 | 3.1336 |
| 6 | 32 | (32,1), (8,2); u=4 gives d=2 ∉ 𝒟 | both yes | h(32)=2, h(8)=1 | **3** (R⁴L, RL⁴; R²L²) | 3 | 3.5255 |
| 7 | 45 | (45,1), (5,3) | (5,3) **no**: (7+3√5)/2 = ε₅² | h(45)=2, h(5)=1 | 2 | 3 (incl. (RL)²) | 3.8497 = 2·ℓ(3) |

- t = 7 is the first trace where the PI's formula over-counts primitive classes.
- Oriented vs unoriented at t = 6: 3 oriented geodesics but 2 unoriented. R²L² is reciprocal (d = 8 ∈ 𝒟_R, ν = 1). {R⁴L, RL⁴} is a time-reversed pair, since 32 ∉ 𝒟_R.

## 3. Sarnak 1982: Σ_{ε_d ≤ x} h(d) ~ Li(x²)

**Statement (as given in a primary source I read):** Sarnak 2007, eqs. (43)–(45), p. 227:
- (43) Σ_{N(p) ≤ x², p ∈ Π} 1 = Σ_{d ∈ 𝒟, ε_d ≤ x} h(d).
- (44) [Luo–Sarnak 1995] Σ_{N(p) ≤ x} 1 = Li(x) + O(x^{7/10}).
- (45) Σ_{d ∈ 𝒟, ε_d ≤ x} h(d) ~ x²/(2 log x).

Here h is the SL(2,ℤ) class number, d ranges over all non-square discriminants (not only fundamental ones), and each class counts as an oriented geodesic.

**Source sought:** P. Sarnak, "Class numbers of indefinite binary quadratic forms", *J. Number Theory* 15 (1982) 229–247, doi:10.1016/0022-314X(82)90028-2.
- **Not read.** The ScienceDirect PDF sits behind a bot check, which I did not try to get around.
- Secondary reports agree:
  - Hashimoto (arXiv:0807.0056v1, withdrawn) eq. (1.2): Σ_{ε(D)<x} h(D) log ε(D) ~ x²/2, "equivalent to" (1.3) Σ h(D) ~ li(x²).
  - Pollicott 1986 §0 and Sarnak 1983 §1 describe it qualitatively: "h turned out to be about the size of the unit".

**STATUS:**
- **VERIFIED** for the asymptotic, in Sarnak 2007 (45), with remainder O(x^{7/5}) *derived here* from (43)+(44).
- **UNVERIFIED** for the exact 1982 statement (theorem number, error term).

**Notes:** Li(x²) ~ x²/(2 log x) at leading order. For finite-x work the Li form is the right one, because it is what the PGT gives. The PI's normalisation (ε_d ≤ x, h = SL(2,ℤ)/narrow, all discriminants) matches.

## 4. Mean multiplicity ⟨g(ℓ)⟩ ~ c e^{ℓ/2}/ℓ; c for PSL(2,ℤ)

**Statement:** ⟨g(l)⟩ ~ 2 e^{l/2}/l.
- Bogomolny, arXiv:nlin/0312061, pp. 69–70 (definition (59), then "⟨g(l)⟩ = 2e^{l/2}/l"), and p. 84, eq. (80): ⟨g(n)⟩ → n/ln n per integer trace n.
- J. Bolte, "Some studies on arithmetical chaos in classical and quantum mechanics", *Int. J. Mod. Phys. B* 7 (1993) 4451–4553, arXiv:chao-dyn/9305005:
  - §3.2: "⟨g(l)⟩ ∼ 2 e^{l/2}/l", eq. (multmodular).
  - §3.4: the same constant re-derived from the quaternion-order theorem with √D = 1/2, d₁ = d₂ = 1.
  - Bolte's general arithmetic-group formula c = 2^{3−n}(d₂/d₁)√D_{K/ℚ}(ℳ) is conditional on a stated "Hypothesis" about gaps in the trace set (§3.4). The modular group has no gaps, so c = 2 is unconditional there.

**Derived here** (from claims 1–3, unconditional):
- Π(x) := #{classes with t ≤ x} ~ x²/(2 log x) (Sarnak 2007 eq. (11), Theorem 2).
- Every integer t ≥ 3 is a trace, so the mean per trace is dΠ/dx. On the Li form this is exactly d/dx Li(x²) = x/log x.
- With t = 2 cosh(ℓ/2) ~ e^{ℓ/2} and log t ~ ℓ/2, this gives ⟨g⟩ ~ 2e^{ℓ/2}/ℓ.
- **c = 2 counts oriented classes**, which is what the PGT counts. For unoriented geodesics c → 1, because reciprocal classes are only ~(3/8)x of the ~x²/(2 log x) classes (Sarnak 2007 eq. (13)).

**Sources not read:**
- Bogomolny–Georgeot–Giannoni–Schmit, *PRL* 69 (1992) 1477 and *Phys. Rep.* 291 (1997) 219–324.
- Bolte–Steil–Steiner, *PRL* 69 (1992) 2188.
- They are cited by Bolte 1993 as the first observation.

**STATUS:**
- **VERIFIED** for c = 2 (Bolte 1993 §3.2 and §3.4; Bogomolny 2003 pp. 69–70), and derived here.
- **UNVERIFIED** for BGGS 1992/1997 and BSS 1992 themselves.

## 5. Series 1985 and the Gauss–Kuzmin law over closed geodesics

**Series' content:** C. Series, "The modular surface and continued fractions", *J. London Math. Soc.* (2) 31 (1985) 69–80. I read the full text through a text extraction of the PDF; the copy's host URL is now offline.
- Theorem A (p. 73): cutting sequences across the **Farey tessellation**, R^{n₀}xL^{n₁}…, give a lift γ with γ_∞ = [n₁,n₂,…] and −1/γ_{−∞} = [n₀,n₋₁,…].
- Theorem B (p. 75): the first-return map is the shift.
- Theorem C (p. 76): relation to the Gauss map T.
- §3.1: the Gauss measure is the measure induced by Liouville on the cross-section.
- §3.2: a periodic sequence n₁…n_{2r} gives the length 2 log λ.
- **Series 1985 contains no statement about the statistics of partial quotients over closed geodesics.**

**Gauss–Kuzmin over closed geodesics:** M. Pollicott, "Distribution of closed geodesics on the modular surface and quadratic irrationals", *Bull. SMF* 114 (1986) 431–446 (Numdam). Read in the scanned original.
- Theorem 1 (p. 441): closed geodesics, ordered by length, equidistribute with respect to the Riemann (Liouville) measure.
- Theorem 2 (Sarnak and Woo): π(t) ~ t/log t, where π(t) = #{γ : e^{l(γ)} ≤ t}.
- Prop. 3(i): (Σ_{e^{l(γ)}≤t} ω(γ))/π(t) ~ [6 log 2/π²] log t, where ω(γ) = 2n is the even period length.
- Prop. 3(ii): (Σ α_k(γ))/π(t) ~ [(6/π²) log((k+1)²/(k(k+2)))] log t, where α_k is the number of entries of the period [a₁,…,a_{2n}] equal to k.
- Prop. 5 (p. 445) gives the same for quadratic irrationals ordered by ε_d, with an extra factor 1/2. Theorem 3: those irrationals equidistribute to the Gauss measure.
- Pollicott's coding uses Series [18] (then "to appear"), Series 1980 [19] and Adler–Flatto. The method extends Bowen 1972 (compact case) via Mayer's transfer operator.

**Derived here:** dividing Prop. 3(ii) by 3(i) gives Σα_k/Σω → log₂((k+1)²/(k(k+2))) = −log₂(1 − 1/(k+1)²), which is the PI's Gauss–Kuzmin law.

**STATUS:**
- **VERIFIED** for the coding (Series 1985, Theorems A–C, §3.2).
- **VERIFIED** for the GK statement, but it belongs to **Pollicott 1986 Prop. 3(ii)/5(i), not Series 1985**.

**Notes for test design:**
- (a) The limit is a **pooled** digit frequency (ratio of sums over geodesics, which weights each geodesic by its period length). It is not an average of per-geodesic frequencies.
- (b) Digits are taken over the even-length period. An odd period is doubled; e.g. √2+1 = [2̄] gives R²L².
- (c) No rate of convergence is given.
- (d) Equidistribution in the modular-surface (non-compact) case is Pollicott's theorem. Bowen 1972 covers compact manifolds only.

## 6. The R²L² example

**Hand arithmetic** (R = (1 1; 0 1), L = (1 0; 1 1)):
- R² = (1 2; 0 1) and L² = (1 0; 2 1), so **R²L² = (5 2; 2 1)**, with trace 6 and det 1.
- Sarnak 2007 eq. (27) gives the form [b, d−a, −c] = [2,−4,−2] = 2·[1,−2,−1]. So δ = u = 2 and the primitive form [1,−2,−1] has discriminant 4 + 4 = **8**.
- Check: eq. (30) with (t,u) = (6,2) and [1,−2,−1] gives back (5 2; 2 1).
- t² − 8u² = 4 has no solution with u = 1 (12 is not a square), so **(6,2) is the fundamental solution for d = 8**. Hence R²L² is primitive, ε₈ = 3 + 2√2 = (1+√2)², and N(1+√2) = −1.
- **Answer: d = 8, u = 2, not d = 32.**
- The discriminant-32 classes (u = 1) are R⁴L = (5 4; 1 1), with form [4,−4,−1], and RL⁴ = (5 1; 4 1), with form [1,−4,−4]. They are inequivalent: [1,−4,−4] cannot represent −1 mod 8, while [4,−4,−1] does represent −1. So h(32) = 2, and the trace-6 total is 3.
- ℓ(R²L²) = 2 arccosh 3 = 4 log(1+√2) ≈ 3.5255.

**Note:** (3 2; 1 1), a guess in the delegation brief (not the PI's), is R²L with **trace 4** (d = 12), not 6.

**STATUS: hand arithmetic (derived here)**, using Sarnak 2007 eqs. (27) and (30). The general correspondence between cyclic R/L words and classes is standard; the primary text read for it is Series §3.2.

---

## 7. Picard group: complex lengths and multiplicities

**Statement:** P. Sarnak, "The arithmetic and geometry of some hyperbolic three manifolds", *Acta Math.* 151 (1983) 253–295. Read in the scan; key pages viewed as images.
- §4 assumes K_D has class number 1, which includes D = 1.
- 𝒟 = {m ∈ 𝒪_D : m ≡ x² mod 4 for some x, m not a perfect square}. h(d) = number of classes of primitive *binary quadratic* forms over 𝒪_D ("Dirichlet forms") under SL(2,𝒪_D), in the **narrow sense** (pp. 255, 277).
- Theorem 4.1 (pp. 280–281): primitive form classes with their fundamental automorphs (4.14) give a representative set for the primitive hyperbolic classes of Γ_D.
- Corollary 4.1 (p. 281): "norms … are the numbers ε_d² … with multiplicity h(d). … lengths … 2 log|ε_d| with multiplicity h(d) … rotations of the Poincaré maps … are 2 arg ε_d … multiplicity h(d)."
- Length and rotation depend only on d.
- Equivalently, the trace t ∈ ℤ[i] (defined up to sign) gives the eigenvalue λ with λ + λ⁻¹ = t and complex length 2 log λ = ℓ + iθ.

**Mean multiplicities for Picard:** J. Marklof, *Nonlinearity* 9 (1996) 517–536 (author PDF read).
- Distinct complex lengths: N^c(l) = (π/2)e^l + O(e^{(23/73+ε)l}), eq. (69).
- Distinct real lengths: N^r(l) = (π/4)e^l + e^{l/2} + O(·), eq. (70).
- ⟨g(l)⟩ ~ c e^l/l with c = (2^{2d−5}π/|D_a|^{1/2} − κ/4)⁻¹, eqs. (65)–(66), and κ = 0 for SL(2,𝒪_K). With d = 2 and D_a = −4 this gives **c = 4/π per real length**.
- *Derived here:* per complex length the constant is **2/π**, from N(l) ~ e^{2l}/(2l) and N^c.

**EGM book:** Elstrodt, Grunewald, Mennicke, *Groups Acting on Hyperbolic Space* (Springer 1998). **Not read.**

**STATUS:**
- **VERIFIED** for complex lengths and multiplicities h(d) (Sarnak 1983, Thm 4.1 and Cor 4.1).
- **VERIFIED** for the mean-multiplicity constants (Marklof 1996).
- **UNVERIFIED** for anything attributed to EGM.

**Corrections:**
- (a) The primary source for the multiplicity is binary **quadratic** forms over ℤ[i] (Sarnak 1983), **not binary Hermitian forms**. I found no primary text tying Hermitian forms to hyperbolic class multiplicities, so the "Hermitian forms" attribution is UNVERIFIED.
- (b) Sarnak's eq. (4.13) says the rotation is "2 arg(N(γ))" with N(γ) = r²e^{2iθ}. That conflicts with his Cor. 4.1 ("2 arg ε_d" = arg N(γ)) by a factor of 2. The geometrically correct holonomy for diag(re^{iθ}, r⁻¹e^{−iθ}) is 2θ = arg N(γ) = 2 arg ε_d (mod 2π), so (4.13) looks like a typo.
- (c) Lengths in H³ with ds² = (dx₁² + dx₂² + dy²)/y² are ℓ = log|N(γ)| = 2 log|λ|.
- (d) Marklof Lemma 3: a generic real length carries the traces s, s̄, −s, −s̄. So complex lengths come in conjugate pairs (θ, −θ).

## 8. Prime geodesic theorem for Bianchi groups (Sarnak 1983)

**Statement:**
- Theorem 5.1 (p. 282, image-verified): for finite-volume M = Γ\H³, "If λ₁ ≥ 5/9 then π(x) = Li(e^{2x}) + O(e^{γx}) as x → ∞ where γ is any number greater than 5/3."
  - π(x) = #{primitive closed geodesics with length ≤ x}.
  - "We distinguish between the two orientations" (eq. (5.1), p. 281).
  - Li(u) = ∫₂^u dt/log t.
- Theorem 3.1 (p. 255): λ₁ ≥ 3/4 on M_D (any D, Remark 5.2(iii)), so Theorem 5.1 applies.
- Consequences (p. 292, image-verified):
  - Σ_{d∈𝒟(e^{x/2})} h(d) = Li(e^{2x}) + O(e^{γx}), γ > 5/3.
  - Theorem 7.1: Σ_{d∈𝒟_x} h(d) = Li(x⁴) + O(x^γ), γ > 10/3, where 𝒟_x = {d : |ε_d| ≤ x}.
  - Theorem 7.2: (1/|𝒟_x|) Σ h(d) = Li(x⁴)/(c_k x²) + O(x^γ), γ > 4/3, using Theorem 6.1: |𝒟_x| = c_k x² + O(x^β), β > 4/3.
- Remark 5.2(ii): Gangolli–Warner had the weaker π(x) ~ e^{2x}/(2x).

**STATUS: VERIFIED** (Sarnak 1983, Theorems 5.1, 3.1, 7.1, 7.2, 6.1).

**Notes:**
- The exponent is in e^{2x} because the entropy in H³ is 2.
- Sarnak proves the PGT for one cusp and states that the multi-cusp case is similar.
- Corroborated by Marklof (1996) eq. (1): N(l) ~ Ei(τl), τ = n − 1.

## 9. Equidistribution of holonomy (Sarnak–Wakayama 1999)

**Sought:** P. Sarnak, M. Wakayama, "Equidistribution of holonomy about closed geodesics", *Duke Math. J.* 100 (1999) 1–57, doi:10.1215/S0012-7094-99-10001-9.
- **Not read**: the Project Euclid bot check and the mathdoc mirror (503) both failed.
- Secondary (Margulis–Mohammadi–Oh, arXiv:1404.5698 v5, p. 2): "When Γ is a lattice in a general rank one group G, Theorem 1.1 was proved by Sarnak and Wakayama; their method is based on the Selberg trace formula and produces an error term."
- Secondary (Kelmer, arXiv:0911.0329): holonomy classes equidistribute in K₀ ⊂ K with respect to Haar measure.

**Primary statement that covers the Picard group:** Margulis, Mohammadi, Oh, "Closed geodesics and holonomies for Kleinian manifolds", *GAFA* (2014), arXiv:1404.5698. The journal comes from the Springer DOI 10.1007/s00039-014-0299-y; volume and pages are unverified.
- Theorem 1.1: for Γ geometrically finite and Zariski dense, Σ_{C: ℓ(C) ≤ T} φ(h_C) ~ (e^{δT}/(δT)) ∫_M φ dm.
- Theorem 1.3 (G = PSL(2,ℂ)): #{[γ] primitive hyperbolic : |λ_γ| < T, θ₁ < Arg λ_γ < θ₂} ~ (θ₂ − θ₁) T^{2δ}/(2πδ log T) for 0 < θ₁ < θ₂ < π.
- For a lattice δ = 2, so the count is (θ₂ − θ₁) T⁴/(4π log T). Integrated over (0,π) this gives T⁴/(4 log T) = Li(T⁴), consistent with claim 8.

**STATUS:**
- **UNVERIFIED** for the exact Sarnak–Wakayama statement and error term.
- **VERIFIED** for the leading-order equidistribution (MMO Thm 1.3), with one caveat: MMO set up X = Γ\G/K for torsion-free Γ (§1). PSL(2,ℤ[i]) has torsion, so applying it to the Picard group goes through a finite-index torsion-free subgroup. That step is standard but not stated in the text.

**Notes:**
- Holonomy = 2 Arg λ mod 2π, so Arg λ uniform on (0,π) means holonomy uniform on the circle.
- Counting is with multiplicity h(d): all classes of one d share a single angle (claim 7).

---

## Summary table

| # | Claim | STATUS | Where (primary) | Correction |
|---|---|---|---|---|
| 1 | geodesics ↔ classes ↔ forms; ℓ = 2 arccosh(t/2) = 2 log ε_d | VERIFIED | Sarnak 2007 pp. 218, 221–224; Pollicott 1986 Prop. 4 | proper/SL(2,ℤ) classes (h⁺ of order); oriented geodesics; improper ≠ unoriented |
| 2 | g(t) = Σ h(d) over t²−4 = du² | VERIFIED in corrected form | Peter 2002 eq. (2.1); Sarnak 2007 p. 224 | restrict to (t,u) fundamental; unrestricted sum = all classes (first differs at t = 7) |
| 3 | Σ_{ε_d≤x} h(d) ~ Li(x²) | asymptotic VERIFIED (Sarnak 2007 (43)–(45)); 1982 text UNVERIFIED | Sarnak 2007 p. 227 | none; remainder O(x^{7/5}) derived |
| 4 | ⟨g⟩ ~ c e^{ℓ/2}/ℓ, c = ? | c = 2 VERIFIED + derived | Bolte 1993 §3.2/§3.4; Bogomolny 2003 pp. 69–70, (80) | c = 2 counts oriented classes (≈1 unoriented); BGGS/BSS PRLs and Phys. Rep. not read |
| 5 | Series 1985; GK law over closed geodesics | coding VERIFIED (Series Thm A–C); GK VERIFIED in **Pollicott 1986** Prop. 3(ii)/5(i) | Series pp. 73–78; Pollicott pp. 441, 445 | attribution: Pollicott, not Series; pooled frequency; no rate |
| 6 | R²L² example | hand arithmetic | Sarnak 2007 (27), (30) | d = 8, u = 2 (fundamental); d = 32 = R⁴L, RL⁴; (3 2; 1 1), a brief-side guess, has trace 4 |
| 7 | Picard complex lengths; forms | VERIFIED (Sarnak 1983 Thm 4.1, Cor. 4.1); EGM UNVERIFIED | Acta 151 pp. 277–281; Marklof 1996 (65)–(70) | quadratic (Dirichlet) forms over ℤ[i], not Hermitian; (4.13) factor-2 typo |
| 8 | PGT for Bianchi groups | VERIFIED | Sarnak 1983 Thm 5.1 (+3.1, 7.1, 7.2) | error O(e^{γx}), γ > 5/3, in length x; Li(e^{2x}) |
| 9 | Sarnak–Wakayama holonomy | UNVERIFIED (not read); leading order VERIFIED via MMO Thm 1.3 | MMO arXiv:1404.5698 pp. 2–3 | torsion-free caveat; angle depends only on d |

## Candidate sealable predictions

Statements found in primary texts, ordered by how directly they can be tested on an exact length spectrum (no compute done):

1. **Correlations of multiplicities (rigorous, parameter-free).**
   - Source: Peter 2002, Theorem (p. 2), **VERIFIED**. Define α(n) = g(n) log n/n and α̃ = α − 1. Then γ(r) := lim_N (1/N) Σ_{2<n≤N} α̃(n) α̃(n+r) exists for every r ≥ 0.
   - Value: γ(r) + 1 = ∏_p (1 + Σ_{b≥1} A_r(p^b)), with explicit local factors.
   - Odd p: A_r(p) = (p·Σ_{n mod p} ((n²−4)((n+r)²−4) / p) − 1)/(p²−1)², and piecewise formulas for A_r(p^b).
   - p = 2: A_r(2) = ±1/9, A_r(4), A_r(8) = 0, A_r(16), A_r(32) = 0, A_r(2^b) for b ≥ 6.
   - First stated heuristically by Bogomolny–Leyvraz–Schmit, *CMP* 176 (1996) 577–617, via Hardy–Littlewood. That paper was not read; its content is restated in Bogomolny 2003 §4.2–4.3, pp. 86–89.
   - r = 0 gives the **variance of the normalised multiplicity**, i.e. the asymptotic relative spread σ_g/⟨g⟩ = √γ(0). *Derived here* to match Bolte 1993 §3.6's numerical finding that σ_g(l) ~ const·e^{l/2}/l.
   - **No rate of convergence is given**, so a seal needs a tolerance justified separately (e.g. a block-SE estimate).
2. **k-point correlations (rigorous).** Hashimoto, arXiv:1202.2603, Theorem 1.1, **VERIFIED** (statement read; the constants in his Thm 3.1 were not transcribed).
   - For any congruence subgroup Γ ⊂ SL(2,ℤ): Σ_{3≤t<x} m_Γ(t+r₁)…m_Γ(t+r_k) ~ c^{(k)}_Γ(r) li_k(x^{k+1}), with li_k(x) = ∫₂^x (log t)^{−k} dt.
   - *Derived consistency:* c^{(2)}_{SL(2,ℤ)}(r) = 3(γ(r) + 1), because li₂(x³) ~ (1/3)∫ u²/log²u du.
   - Lukianov (*Forum Math.* 19, 2007) and Rudnick (*AHP* 6, 2005) are cited there; not read, so UNVERIFIED.
3. **Mean multiplicity with finite-length form.**
   - Because every integer t ≥ 3 is a trace, ⟨g(t)⟩ = d/dt Li(t²) = t/log t exactly at the main-term level. This equals 2e^{ℓ/2}/ℓ only at leading order (derived here from Sarnak 2007 (43)–(45)).
   - Error control: cumulatively, Σ_{t≤x} g(t) = Li(ε(x)²) + O(x^{7/5}), with ε(x) = (x + √(x²−4))/2 and (44) from Luo–Sarnak 1995 (cited in Sarnak 2007; LS95 itself not read).
   - This is a "can it fail" calibration rather than a discovery test.
4. **Limit distribution of α exists** (Peter 2002 §3, Cor. 4.2: α ∈ D^q for all q ≥ 1, and limit-periodic functions have limit distributions). **VERIFIED** as existence only.
   - No explicit distribution is given. Its moments M(α^k) are the r = 0 constants of item 2.
5. **Continued-fraction digit statistics over closed geodesics** (Pollicott 1986 Prop. 3, 5; **VERIFIED**).
   - Mean even period length ~ (6 log 2/π²) ℓ.
   - Pooled digit frequency → −log₂(1 − 1/(k+1)²).
   - Leading order only, no rate.
6. **Picard group** (VERIFIED statements; leading order only):
   - Σ_{|ε_d|≤x} h(d) = Li(x⁴) + O(x^γ), γ > 10/3 (Sarnak 1983 Thm 7.1).
   - Distinct complex and real lengths, Marklof (69)–(70) (both with an explicit O(e^{(23/73+ε)l}) remainder). The real-length count carries a second-order term e^{l/2}.
   - Mean multiplicity 4/π per real length (Marklof (66)) and 2/π per complex length (derived here).
   - Uniform Arg λ, MMO Thm 1.3 (no rate in the read statement). Sarnak–Wakayama's error term is UNVERIFIED.
7. **Correlations among rotation angles:** **none found.**
   - The only structural facts found:
     - (a) The angle is a function of d alone, so all h(d) classes share it (Sarnak 1983 Cor. 4.1).
     - (b) Complex lengths come in conjugate pairs ±θ at a generic real length (Marklof Lemma 3).
   - No quantitative prediction for pair correlations or fluctuations of holonomy angles was found in the texts read.
8. **PGT remainder size:** heuristic only.
   - Bolte 1993 §3.6 expects |Q_R(l)| = e^{l/2}ω(l), with ω a power or log; this rests on numerical evidence for the Artin billiard and octagon groups and on Berry's non-rigorous theory.
   - The proven bound in Sarnak 2007 (44) is O(x^{7/10}) in N.
   - Not sealable as a constant.

**Sources read (primary):** Sarnak 2007 (Clay 7); Sarnak 1983 (Acta 151); Pollicott 1986 (Bull. SMF 114); Series 1985 (JLMS 31); Peter 2001/2002 (arXiv:math/0104234); Hashimoto 2012 (arXiv:1202.2603); Margulis–Mohammadi–Oh (arXiv:1404.5698 v5); Marklof 1996 (Nonlinearity 9); Bolte 1993 (arXiv:chao-dyn/9305005 TeX); Bogomolny 2003 (arXiv:nlin/0312061).

**Not read (UNVERIFIED wherever used):** Sarnak 1982 (JNT 15); Sarnak 1985 (JNT 21); Sarnak–Wakayama 1999 (Duke 100); EGM 1998; BGGS PRL 1992 and Phys. Rep. 1997; BSS PRL 1992; BLS CMP 1996; Luo–Sarnak 1994 and 1995; Lukianov 2007; Rudnick 2005.
