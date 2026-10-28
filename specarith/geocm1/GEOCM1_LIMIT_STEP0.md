<!-- Provenance: Step 0 for "GEO-CM1, the limit" (Will, 2026-10-28). Drafted by a literature agent; filed unedited below.
Spot-checked by the main session against the agent's downloaded copy of Cvitanović–Gunaratne–Vinson, Nonlinearity 3
(1990): Table 1 (p.878) lists |δ| for [ā] a = 1…10, including δ_9 = −174.5198 ± 2·10⁻⁴ and δ_4 = −24.620 347 98 with
an uncertainty printed as "7 × 10⁻⁸" (OCR-garbled exponent; read as 10⁻⁸); the text (p.876) reads "δ_p for p = a1a2…n
with a large continued fraction entry n grows as a power of n. According to [1, 9, 16] [eq. (9)] … could perhaps be
turned into a systematic asymptotic expansion"; p.879 uses "δ_a ≈ a³ for large a". Both CONFIRMED. The Graczyk–Świątek
and Epstein–Yampolsky items were not re-checked. §5 fits are the agent's computation (post hoc, descriptive). -->

# GEO-CM1 limit, Step 0: large-a asymptotic of δ_a along [0; a, a, …]

Downloads (untrusted data, read only): `/tmp/claude-1000/-home-combust-fmexplorer-criticality-tool--claude-worktrees-ph6-xp/a91f0f2e-c26b-4e53-81dc-2feedac9a4b5/scratchpad/lit_cm2/` (dLOP preprint, CGV 1990, Lanford–Yampolsky 1108.2801, Epstein–Yampolsky IMS 2001/4).

## Short answer
The exponent is known in the physics literature, though as a heuristic. The constant and the corrections are not published anywhere I could find. The stated law is δ_a ∝ a³, which means h_a → 3/2 and f(a) → 3/2. I found no source that argues for any other limit. There is a rigorous one-sided bound (Graczyk–Świątek). There is also a rigorous framework that could give the full asymptotic, the a = ∞ "universal parabolic map", but nobody has carried that computation out. A limit near 1.7 is ruled out by theory, not by data alone (INFERENCE, see §4).

## 1. Who wrote dLOP
- R. de la Llave, A. Olvera, N. P. Petrov, "Universal scalings of universal scaling exponents", mp_arc 07-104. VERIFIED from the title page of Petrov's copy (combination_022007.pdf, p.1).
- The citation J. Phys. A 40 (2007) F427 is UNVERIFIED: I did not see the journal page.
- dLOP Table 1 (p.5) lists δ for [(1^k 2)^∞] and [(1^k 3)^∞], with δ_3 = 13.760284 (k = 0). VERIFIED.
- dLOP's subject is the concatenation law δ_AB ≈ δ_A δ_B (eqs. 2–4). VERIFIED. It says nothing about large a.

## 2. The key physics source: Cvitanović, Gunaratne, Vinson, Nonlinearity 3 (1990) 873–885
- **Table 1 (p.878)** gives δ_1 … δ_10 for [ā]. VERIFIED. The note added in proof says δ_1–δ_8 come from A. Eriksson, Chalmers preprint 1990.
  - δ_9 = −174.5198 ± 2·10⁻⁴. This fills your missing a = 9.
  - δ_4 = −24.62034798, δ_5 = −40.386913, δ_6 = −62.140406, δ_7 = −90.99597, δ_8 = −128.08011, δ_10 = −231.439 ± 2·10⁻³.
  - All of your values agree with these to the digits you quote. VERIFIED by comparison.
- **Eq. (9), p.876** (VERIFIED):
  - "δ_p for p = a1a2…n with a large continued fraction entry n grows as a power of n. According to [1, 9, 16], lim δ_p ∝ n³."
  - The paper adds that this "follows from methods akin to those used in describing intermittency [17] and could perhaps be turned into a systematic asymptotic expansion."
  - It gives no prefactor and no correction terms. It cites Jensen–Bak–Bohr (1983/84), Cvitanović–Shraiman–Söderberg (1985), Kaneko (1982/83) and Pomeau–Manneville. I did not read those for this specific claim, so their part is SECONDARY.
- **p.879**: "δ_a ≈ a³ for large a" is used to sum the tail of a cycle expansion. VERIFIED.
- **p.881**: a "phase transition" at τ = −1/3 is attributed to the power-law tails δ_…n ≈ n³. VERIFIED.

## 3. Rigorous and mathematical side
- **Graczyk & Świątek, "Critical circle maps near bifurcation", CMP 176 (1996) 227–260 (arXiv math/9201283).** Read through a web-fetch summary of the ar5iv HTML, not proof-read.
  - Prop. 4 (§3.1): harmonic scalings h_n = |J_n|/|J| ≥ K₁/(n³+1), uniformly.
  - The matching upper bound h_n ≤ K₂/(n³+1) holds only if their Prop. 2 holds.
  - Theorem B: 1/3 ≤ HD < 1.
  - Status: VERIFIED-via-summary.
- **Epstein & Yampolsky, "A universal parabolic map", Stony Brook IMS preprint 2001/4 (ETDS).**
  - p.2: there is a renormalization fixed point f_* that "should be thought of as having the rotation number represented by an infinite continued fraction, each entry of which equals ∞". VERIFIED.
  - Thm 3.1 (p.10): ι is continuous in the weak topology. VERIFIED.
  - Thm 3.2(c) (p.12): if a_i → ∞, then R^n_cyl f → f_*. VERIFIED.
  - So the [N̄] fixed points converge to f_* as N → ∞. INFERENCE, from continuity of ι.
  - Thm 3.2(d): P contracts only inside the codimension-one set Par_[∞]. The transverse, unstable eigenvalue is never computed. VERIFIED.
  - Thm 2.2 (p.8), near-parabolic Douady coordinates: θ(g) = 1/α(g) + o(1). VERIFIED.
  - Cor. 2.6 (p.9): the parabolic point of P_σ(f) is simple, so the tangency is quadratic. VERIFIED.
- **Lanford & Yampolsky, arXiv 1108.2801, p.1**: says the parabolic renormalization fixed point for critical circle maps "permits both a numerical and an analytic study". VERIFIED. They cite Lanford, "The zero rotation number fixed point" (manuscript), whose content is UNVERIFIED. The paper itself treats the quadratic (Inou–Shishikura) case only.

## 4. What links δ_a to the q⁻³ cusp law (INFERENCE)
- The fixed point for [N̄] sits near f_*, which has a simple parabolic point. Perturbing transversally by ε gives α ≈ c√ε. Thm 2.2 then gives N ≈ 1/α, so dN/dε ∝ ε^(−3/2) ∝ N³.
- That makes the unstable eigenvalue δ_N ≈ C·N³. C is a universal constant fixed by f_*, but nobody has computed it.
- α is analytic in √ε, so I expect corrections as powers of 1/N, with no log N. This is not proven.
- The scaling holds because the tangency is quadratic (Cor. 2.6), not because the critical point is cubic. That is the same mechanism as the 1/n tongue widths ∝ n⁻³ at K = 1.
- If the per-level harmonic scalings in Graczyk–Świątek can be identified with the ratios that define δ, their uniform lower bound gives |δ_N| ≲ N³/K₁. That excludes 2h → 3.4 (h → 1.7). The matching lower bound on δ_N is conditional.

## 5. What the full table (with δ_9) says (my computation)
- δ_a/λ_a³ = 0.669, 0.483, 0.382, 0.324, 0.289, 0.266, 0.250, 0.239, 0.231, 0.225 for a = 1…10. It is still falling at a = 10.
- Local h, adding the new pairs: (8,9) = 1.349, (9,10) = 1.369.
- **Fitting δ/λ³ = C + c₁/a + c₂/a² + … on a ≥ 3…6:**
  - C = 0.187–0.188, stable whether the expansion is in λ or in a.
  - The relative corrections are large: about 0.83/a + 13/a² − 20/a³.
  - This model reproduces the data exactly. It predicts h = 1.385, 1.455, 1.487, 1.495 at a = 10.5, 20.5, 50.5, 100.5, so h approaches 1.5 from below at O(1/a).
- **Free-exponent fits** (ln δ = ln C + p ln λ + b/a [+ c/a²]) give p = 2.96–3.17, i.e. h∞ = 1.48–1.58.
- **Polynomial extrapolation of h in 1/a** gives 1.43–1.60, depending on the fit window and order. Data up to a = 10 cannot separate 1.5 from about 1.58.
- f(a) = 3/2 + ln C/(2 ln λ_a) + … ≈ 1.5 − 0.84/ln λ_a. It converges only logarithmically, so extrapolating f in 1/a is misleading, as you suspected.

## 6. Evidence against h → 1.5
- I found no source that proposes a different limit.
- The weak points are these:
  - The n³ law in CGV is heuristic, and so is its link to the eigenvalue.
  - The rigorous bound covers one side only, and its link to δ is my inference.
  - No log-correction analysis exists for the circle-map case.
  - At a ≤ 10 the corrections are 20–30%. That is the most likely source of your "≈1.7" form.

## Who would know
- **Exact asymptotic and constant C:** M. Yampolsky (Toronto); D. Gaidashev (Uppsala, computer-assisted renormalization); N. Goncharuk.
- **Lanford's manuscript:** whoever holds Lanford's unpublished notes. Lanford himself has died.
- **Physics side:** P. Cvitanović. A. Eriksson computed δ_1–δ_8.
- **Near-parabolic expansions:** M. Shishikura, A. Chéritat, X. Buff.
- **Large-a numerics:** R. de la Llave and N. Petrov, who have the code.
