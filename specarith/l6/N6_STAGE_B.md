# n = 6, stage (b): the 3 + 3 long-range extraction (the derivation, as it goes)

Gates: `N6_STAGE_B_GATE.md` (G-b1 U(N), G-b2 reduction, G-b3 brute force; the wrong variants must fail all three).
Time box: 3 sessions from the start of the derivation (round 75). **Session 1: 2026-10-22.**

## Session 1 (2026-10-22): the extraction is a phase filter
**The observation.** In the ratios construction (`cs4/ratios_t5.py`, `Model.ratio_jet`), each term of J(A; B) is
labelled by subsets S of A and T of B with |S| = |T|. Its x-dependence carries an explicit e^{−L(ΣS + ΣT)}.
- A carries the values i x_p (p ∈ P), and B carries −i x_m (m ∈ M). So the phase is Φ = i·Σ_k c_k x_k, with
  c_k = +1 for the points of P in S, −1 for the points of M in T, and 0 otherwise.
- The rest of the term (Z-ratio factors, and 𝒜_ζ for ζ) depends on the points only through smooth functions of their
  differences.
- **Shifting the second cluster by r multiplies a term by e^{−iL·r_t·Σ_{k∈B} c_k}.** So the term is non-oscillating
  in r iff Σ_{k ∈ cluster B} c_k = 0.
- The multilinear-jet derivative that gives J preserves each term's phase. So selecting terms by this rule is exact at
  every order. It involves no asymptotic expansion and no new transcription.
- It is the rule `cs4fastc.connected` applies to CS08's closed-form pieces for 2 + 2 (a piece oscillates iff
  c₃ + c₄ ≠ 0), lifted to the ratios definition for any cluster sizes (a, b).

**The extracted object.**
- K_ab(x_A, x_B) = ρ_{a+b}^{non-osc}(x_A ∪ x_B) − ρ_a(x_A)·ρ_b(x_B), in unit-spacing densities.
- For corrected (B), C_long(r) = Σ_{a,b = 1..3} c_a c_b ∫_{A^a × B^b} K_ab, with c_a the falling-factorial
  coefficients of ψ (`N6_STAGE_A.md`). The (3, 3) term is the new n = 6 piece. The lower (a, b) use the same code.
- Code: `cs4/n6b_extract.py` (`FilteredModel.rho_f`, `K_ab`).

**First gate result, a local smoke run (G-b2 at PMAX 10³).**
- The extraction's own (2, 2) instance against `cs4fastc.connected(nonosc_only=True)` at ℓ = 15.75 and 21.75, two
  pairs of in-pair offsets, and r = 20, 50, 100, 300, 1000.
- Agreement is to 10⁻¹⁴–4·10⁻¹³ absolute, against values of 2.5·10⁻⁵ to 0.05. The declared precision is 1.1·10⁻⁹
  relative.
- Both wrong variants fail: the sign-reversed extraction, and the (1, 1) reduction in its place.
- **The term is large in the ζ regime:** the 2 + 2 non-oscillating ρ₄ᶜ is 0.025–0.05 at r = 50–1000. So G-b2 has
  resolution there. The official run adds `cs4lr` itself on its grid and PMAX 3·10⁵ (on spot).

**Still open in session 1:**
- G-b1 needs U(N) at large N with r up to 1000. The jets' cancellations at large L are to be checked against the
  determinant first. If they need a moderate N, the known answer is recomputed at the same N with stage (a)'s
  Fredholm code.
- G-b3 needs stage (c)'s n = 6 U(N) pointwise gate to pass first.
- The bond-order definitions of the wrong variants for C(r): (i) the (1, 1) term only; (ii) the (2, 2) contribution
  with its sign reversed.
