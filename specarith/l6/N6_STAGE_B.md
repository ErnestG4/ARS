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

## Session 1, continued: G-b2, and what G-b1 costs as declared
**G-b2 at PMAX 10³ (official, spot): PASS; both wrong variants fail.**
- The first official run applied cs4lr's 1.1·10⁻⁹ as relative. `cs4lr_check` defines it as the largest absolute
  difference, and the gate declares the larger of that and the cutoff change.
- The code was corrected to 1.1·10⁻⁹ absolute, the stricter choice (3c16cc59). In that first run, at PMAX 3·10⁵ the
  extraction matched cs4lr to ≤ 7·10⁻¹³ and cs4fastc to ≤ 2·10⁻¹⁰.
- cs4lr cannot run at PMAX ≤ 1000 (its Fourier group above 1000 is empty), so the PMAX 10³ run compares cs4fastc
  only.

**G-b1 as declared is infeasible by direct quadrature** (`n6b_quadcheck.py`). Assembling the full CUE_N C(r) from
in-window Gauss–Legendre quadrature of the determinant ρ's gives these relative errors against stage (a)'s exact
Fredholm value:

| r | exact C(r) | 6 nodes | 8 | 10 | 12 |
|---|---|---|---|---|---|
| 4.125 | −1.95·10⁻² | 0.83 | 0.081 | 1.6·10⁻³ | 1.1·10⁻⁵ |
| 7.3 | 9.20·10⁻⁶ | −42 | 0.13 | 0.051 | 6.9·10⁻⁴ |
| 20 | −3.46·10⁻⁶ | 7.5 | −0.052 | −4.4·10⁻³ | −5.9·10⁻⁵ |
| 100 | −6.86·10⁻⁹ | 138 | 0.22 | −1.5·10⁻⁴ | −2.2·10⁻⁵ |

- **Why so many nodes:** the (a, b) pieces cancel heavily. C(100) is 7·10⁻⁹, while each piece is far larger. So 1%
  needs 10–12 nodes per coordinate.
- **The cost:** that is about 9·10⁴ jet evaluations per r (48,400 for the (3, 3) piece alone), roughly 1,600 core-h
  for the 60-point grid. **The scoping draft's "8 nodes per dimension" estimate was wrong for the same reason, and
  that applies to the ζ production run too.**

**What the derivation has to supply next (session 2), the separation.**
- For r ≫ 4, each kept term factorises into in-cluster phase factors, which are unit-scale and oscillatory, times
  cross factors, which are smooth in r and vary over the window only at relative order 4/r.
- Expanding the cross factors about the window centres in powers of (in-window offset)/r turns the 6-dimensional
  integral into in-cluster integrals (3-dimensional, computable once) times cross factors and their derivatives at
  the centres.
- Truncation is checked order by order against the exact answer.
- That makes C_long(r) cheap at every r. It is the critical path for both G-b1 and the ζ evaluation.

**A cheaper G-b1 variant, for Will to decide (not adopted):** compare the extraction with the determinant's full C,
period-averaged over 8 shifts, at identical quadrature nodes. The quadrature error then cancels in the comparison, so
4–6 nodes suffice, at a reduced r grid. That tests the phase filter at 3 + 3 without the separation, but not against
the exact Fredholm answer.

**G-b2 official result: PASS at both cutoffs; both wrong variants fail** (`cs4/results/n6b/GB2_P*.json`).
- PMAX 10³: max |extraction − cs4fastc| = 3.9·10⁻¹³.
- PMAX 3·10⁵: max |extraction − cs4lr| = 7.3·10⁻¹³, and against cs4fastc 2.0·10⁻¹⁰.
- Both are against the declared 1.1·10⁻⁹ absolute, on values of 6·10⁻⁵ to 0.05.
