# RQ1 — real-quadratic prime angles in ℤ[√2]: Step 0 (round 85; no compute)

Arc RQ1, time box two sessions; session 1 starts 2026-10-25. The cost model and first-wave rule
(`../l6/N6-2_PLAN.md` §10) apply.

## 1. Phase 34d: what it computed (repository record: `../../PHASE34D_FINDINGS.md`, `../../phase34d/`)
**Substrates and generation.**
- **Prime ideals and angles:** Gaussian prime ideals in ℤ[i] (θ ∈ [0, π/2)) and Eisenstein prime ideals in ℤ[ω]
  (θ ∈ [0, π/3)).
- **Generation:** Cornacchia plus Tonelli–Shanks, at X up to 10⁸.
- **Counting:** one angle per prime ideal; a split p gives θ and L − θ.

**Readouts.**
- **Step 3: σ²(K, X)/(N/K) against β = log K/log N,** compared with Rudnick–Waxman's min(1, 2β). The estimator is
  RW's sliding-window variance, discretised on 5,000 (2,000 in the bootstrap) window centres.
- **Step 4: ARS bulk readouts** (NNS classification, RF spike test) against CUE/Poisson. These are not RW
  statistics.

**Results as recorded.**
- **Gaussian: "RW_SHAPE_CONFIRMED".**
  - Rigidity regime: within 1σ on every cell, e.g. X = 10⁷, K = 30, β = 0.268: 0.626 ± 0.242 against 0.535.
  - Saturation regime: a deficit that closes as X grows, e.g. β = 0.65: 0.857 / 0.923 / 0.984 ± 0.025 at
    X = 10⁶ / 10⁷ / 10⁸. This was read as consistent with Chen et al.'s 1/log X NLO.
- **Eisenstein: "first measurement",** reaching 1.000 ± 0.022 at β = 0.65, X = 10⁸.
- **Step 4:** both substrates BL-bulk in 20/20 subsample seeds.

**Did it test Rudnick–Waxman?** Descriptively, yes: Conjecture 1.2's shape was compared on ℤ[i] at X ≤ 10⁸. It was
not a sealed test: no pre-registered tolerance, no seal, no double read.

**A defect found in this review (Step 0; not previously recorded).**
- **What the reported numbers are.** The σ²/(N/K) values in the X-rate table, including every number quoted above,
  are means over 50 random half-samples (`phase34d/run_amendments.py`: `rng.choice(N_full, N_full/2, replace=False)`),
  not the full-sample statistic.
- **Why that biases them.** Random halving is a thinning. For a p-thinning,
  Var_thin = p²·Var + p(1 − p)·E N, so ratio_thin = p·ratio + (1 − p). At p = ½ that is
  ratio_half = (ratio_full + 1)/2. The reported ratios are pulled halfway toward 1, the Poisson value and RW's
  saturation value.
  - The headline "0.984 ± 0.025 within 1σ of 1" corresponds to a full-sample ratio near 0.97.
  - 0.857 corresponds to ≈ 0.71.
  - In the rigidity regime, thinning pulls the readings away from RW's 2β toward 1.
- **Why the error bars are wrong too.** The ± is the spread of half-samples, not the sampling uncertainty of the
  full-sample statistic.
- **Consequence:** Phase 34d's "within 1σ of the RW asymptote" verdicts are not established as stated. Its
  qualitative X-trend survives the bias.
- **Also:** its statistic was never shown stable across X (TOOLKIT §9.E) before the comparison was read.
- Recorded here for Will. Phase 34d's files are not edited.

## 2. Literature (primary source, or UNVERIFIED)
- **Rudnick & Waxman, "Angles of Gaussian primes",** Isr. J. Math. 232 (2019), 159–199; arXiv:1705.07498.
  - **Verified:** arXiv abstract page; full text from the cached copy `phase34d/lit/rudnick_waxman_2019.txt` (the
    Isr. J. Math. layout).
  - **Definitions** (eq. 1.2): N_{K,x}(θ) = #{𝔭 prime, N𝔭 ≤ x, θ_𝔭 ∈ I_K(θ)}, with I_K(θ) of length π/(2K) in
    [0, π/2).
    - Var(N_{K,x}) = ∫₀^{π/2} |N_{K,x} − ⟨N_{K,x}⟩|² dθ/(π/2), a continuous average over the window centre.
    - N = #{𝔭 : N𝔭 ≤ x} counts all prime ideals: inert ones, at θ = 0, and (1 + i) included.
  - **Conjecture 1.2, verbatim:** "For 1 ≪ K ≪ N^{1−o(1)}, Var(N_{K,x}) ∼ (N/K)·min(1, 2 log K / log N)."
  - **Published numerics: Figure 1 only.** It plots Var/E against β = log K/log N for x ≈ 10⁸, with the curve
    min(1, 2β). There is no table, so the published values exist only as plotted points (§5, gate 3).
  - Also stated: Proposition 2.2 (the trivial regime x = o(K): Var ∼ N/K), and a function-field analogue proved.
- **Chen, Kim, Lichtman, Miller, Shubina, Sweitzer, Waxman, Winsor, Yang, "A Refined Conjecture for the Variance of
  Gaussian Primes Across Sectors",** Experimental Math. (2020); arXiv:1901.07386.
  - **Verified:** arXiv abstract page and the cached text.
  - **Content:** a ratios-conjecture derivation with a power-saving error term and a second bifurcation point.
  - **Its statistic is not RW's:** the smoothed, von Mangoldt-weighted ψ_{K,X} with test functions Φ, f.
  - **Numerics:** Figure 1 only (X = 10⁹, Mathematica code in Appendix A). No table.
  - **Not transcribed here:** its lower-order constants (C_Φ,ζ, C_Φ,L, …), which are in §§5–9.
- **Hecke, "Eine neue Art von Zetafunktionen und ihre Beziehungen zur Verteilung der Primzahlen",** Math. Z. 1 (1918)
  357–376 and Math. Z. 6 (1920) 11–51.
  - **Citation verified** via secondary reference lists.
  - **UNVERIFIED (no primary text read):** that Part II proves equidistribution of real-quadratic prime-ideal angles
    log|π/π′| mod 2 log ε via Grössencharaktere. That is the standard attribution.
- **Real-quadratic analogues:**
  - **Baier & Roy, "A note on the distribution of prime ideals in real quadratic fields",** arXiv:2307.03513 (a search
    result lists Funct. Approx. Comment. Math. 71(2), 2024; that journal reference is UNVERIFIED).
    - The abstract (verified) says it carries Harman–Kumchev–Lewis's imaginary-quadratic results over to real
      quadratic fields.
    - Its statements on angles and sectors are UNVERIFIED (full text not read).
  - **Huang, Liu & Rudnick, "Gaussian primes in almost all narrow sectors",** arXiv:1903.04005.
    - Metadata verified.
    - A search snippet says it also treats real quadratic fields with a unit of norm −1 and narrow class number one,
      which fits ℤ[√2]. UNVERIFIED (the abstract page does not say so).
  - **No sector-variance conjecture or result for real quadratic fields was found.** By the round-85 standard, RQ1
    has no published target. Its prediction is the structural analogue derived below.

## 3. Derivation for ℤ[√2] (K = ℚ(√2), O_K = ℤ[√2], h = 1, ε = 1 + √2, N(ε) = −1)
**The angle is well defined.** For π = a + b√2 ≠ 0 with conjugate π′ = a − b√2, put
θ(π) = log|π/π′| / (2 log ε) mod 1.
- Every unit is u = ±ε^n. Since εε′ = N(ε) = −1, ε′ = −ε⁻¹, so u′ = ±(−1)^n ε^{−n}.
- Hence |u/u′| = ε^{2n}, and θ(uπ) = θ(π) + n ≡ θ(π) mod 1.
- So θ is a function of the principal ideal (π). With h = 1, it is a function of every ideal.

**Special cases.**
- θ(π′) = −θ(π): the two primes above a split p sit at θ and −θ.
- An inert p (p ≡ ±3 mod 8) has 𝔭 = (p), so θ = 0.
- The ramified (√2) has |√2/(−√2)| = 1, so θ = 0.
- **The inert-prime witness:** inclusion of inert primes puts a spike at θ = 0.

**The characters.** λ^k(𝔞) := e^{2πikθ(𝔞)} = |π/π′|^{iπk/log ε}.
- This is a unitary Grössencharakter of K with trivial finite modulus and infinity type
  x ↦ |x₁|^{iν_k}|x₂|^{−iν_k}, where ν_k = πk/log ε ≈ 3.564·k.
- It is well defined by the unit computation above (|ε^n|^{iν}|ε′^n|^{−iν} = ε^{2niν} = e^{2πikn} = 1).

**Its L-function.**
- L(s, λ^k) = Σ_𝔞 λ^k(𝔞) N𝔞^{−s}, with gamma factor Γ_ℝ(s + iν_k)Γ_ℝ(s − iν_k).
- Since 𝔭 ↦ 𝔭′ sends λ^k to λ^{−k}, the Dirichlet coefficients are real: 2cos 2πkθ_𝔭 at split p. So
  L(s, λ^k) = L(s, λ^{−k}).
- The Gaussian case has the same structure.

**Analytic conductor.** At s = ½ it is q(λ^k) ≍ d_K·(|ν_k| + 3)² = 8·(πk/log ε)²(1 + o(1)). So
log q(λ^k) = 2 log k + log(8π²/log²ε) + o(1).
- The growth rate is k², exactly as for the Gaussian characters (𝔭/𝔭̄)^{2k}, whose conductor is ≍ 4·(2k)².
- Only the constant differs: log(8π²/log²ε) ≈ 4.62 here (corrected after 599683f2, which had 4.32: an arithmetic slip), against log 16 ≈ 2.77 for ℤ[i].

**The leading-order sector variance (reviewer's heuristic: derived, not refuted, at the level of RW's heuristic).**
- **Setting it up:**
  - With windows of width 1/K in θ ∈ [0, 1), Parseval gives Var = Σ_{k≠0} |Î_K(k)|²·|S_k|², where
    Î_K(k) = sin(πk/K)/(πk) and S_k = Σ_{N𝔭 ≤ X} λ^k(𝔭).
  - The window weights confine the sum to |k| ≲ K.
- **RW's heuristic for |S_k|²** (§5 of their paper, via the explicit formula and a random-matrix model for the zeros
  of L(s, λ^k)) gives |S_k|² ≈ N·min(1, log q(λ^k)/log X).
  - Its inputs are the conductor growth, which sets the matrix size, unitary-type bulk statistics (their Prop. 5.3:
    U, USp and SO agree at leading order), and the prime ideal theorem.
  - **For ℤ[√2] all three inputs carry over:** log q(λ^k) ≈ 2 log k, and N ∼ X/log X counting both ideals above each
    split p.
- **The result:** summing over |k| ≲ K gives
  **Var ∼ (N/K)·min(1, 2 log K / log N)**,
  the same functional form, with the crossover at K ≈ √N. Will's reviewer's heuristic is therefore derivable in the
  same sense as RW's Conjecture 1.2: conditional on RW's RMT model, not proved.
- **Differences from ℤ[i], all below leading order:**
  - the conductor constant (4.62 against 2.77) shifts the crossover in log K by O(1), i.e. an O(1/log N) relative
    change near β = ½;
  - unit group ±ε^ℤ is infinite and torsion is order 2, against order 4 for ℤ[i] (that enters only through the angle
    normalisation);
  - the round's generator excludes inert and ramified primes, where RW include them; their effect is O(√X) points at
    θ = 0.

**Lower-order terms: not derived in Step 0.**
- Chen et al.'s ratios-conjecture route would carry over in principle. Its constants depend on the field (d_K = 8,
  ν_k = πk/log ε, the Euler factors at 2 and at the inert primes) and on the statistic (theirs is smoothed and
  ψ-weighted, RW's and ours sharp and unweighted).
- The adaptation is a derivation in its own right.
- **Without it, the prediction is definite only at leading order. The finite-X corrections are O(1/log X), measured
  on ℤ[i] as ≈ 30% (X = 10⁶) down to ≈ 3% (X = 10⁸) at β = 0.65 (Phase 34d's numbers after undoing its thinning bias).**

**What this means for a verdict (Will's call at the seal).**
- **What exists:** a definite leading-order formula.
- **What does not:** a derived finite-X correction.
- **The available verdicts:**
  - (a) RQ1 exploratory, a gallery with no verdict;
  - (b) a verdict on the leading-order shape only, with a tolerance wide enough for an O(1/log X) correction, and a
    rate check across both X values (the §9.E stability requirement) in place of a fitted correction;
  - (c) first derive the lower-order terms (not costed).

## 4. Phase 34d lesson carried into RQ1
- **No subsample bootstraps.** Error bars come from the X-stability check and from the gates' known answers.
- **Every ratio uses the full-sample statistic,** computed exactly. N(θ) is piecewise constant, so ∫N(θ)²dθ is summed
  over the 2N window breakpoints, with no grid.
