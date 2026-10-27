# RQ1-b Step 0: Chen et al.'s refined sector variance for a general quadratic field (round 93)

Time box: one session. No data are used in §§1–4. §5 (labelled post hoc) compares with the read data.

**Primary source.** Chen, Kim, Lichtman, Miller, Shubina, Sweitzer, Waxman, Winsor, Yang, "A Refined Conjecture for
the Variance of Gaussian Primes Across Sectors", Experimental Math. (2020), arXiv:1901.07386. Read from
`phase34d/lit/chen_refined_2019.pdf` (sha256 920b212b…9162) via its text extraction: eqs. (1.3)–(1.14), Theorem 1.1,
Conjecture 1.2, §9.2 (eqs. 9.13–9.27) and Appendix A. Everything stated about ℤ[i] below is from that source; every
statement about other fields is our generalisation and is marked.

## 1. Chen et al.'s statistic and formula (ℤ[i]; primary source)

- **Statistic:** ψ_{K,X}(θ) = Σ_𝔞 Φ(N𝔞/X)·Λ(𝔞)·F_K(θ_𝔞 − θ) over all nonzero ideals of ℤ[i] (prime powers included;
  inert primes at θ = 0; weights Λ = log N𝔭), with Var over θ (eq. 1.8). Their numerics (Appendix A) use Φ = 1_(0,1],
  f = 1_[−½,½], omit prime powers and (1 + i), and keep the inert primes p ≤ √X at θ = 0 with weight 2 log p.
- **Conjecture 1.2** (λ = log K / log X, Cf = cf for this f, C_Φ = 4π²∫Φ):
  - ½ < λ < 1: Var/(Cf X^{1−λ}) = C_Φ log X + Δ_Φ + O(X^{−ε}), with Δ_Φ = C′_Φ − π²Φ̃(½)²;
  - λ < ½: Var/(Cf X^{1−λ}) = C_Φ (2λ log X) − K_Φ + O(X^{−ε}), with
    K_Φ = C_Φ,ζ − C_Φ,L − A′_Φ + 2π²Φ̃(½)² + C_Φ(log(π²/4) + 2) (eq. 1.14).
  - In the Figure-1 normalisation, Var/(⟨ψ⟩ log X) = 1 + Δ_Φ/(C_Φ log X) above λ = ½ and 2λ − K_Φ/(C_Φ log X) below.
- **The three constants** (eqs. 9.25–9.27), integrals on Re β = ε′ (Appendix A uses ε′ = 0.1):
  - C_Φ,ζ = 2πi∫ Φ̃(½+β)Φ̃(½−β)·(ζ′/ζ(1−2β) + ζ′/ζ(1+2β)) dβ;
  - C_Φ,L = 2πi∫ Φ̃(½+β)Φ̃(½−β)·(L′/L(1+2β) + L′/L(1−2β)) dβ, with L = L(s, χ₋₄);
  - A′_Φ = −4πi∫ Φ̃(½+β)Φ̃(½−β)·Σ_{p≡3(4)} (p^{2+8β} + p² − 2p^{4β}) log p / (p^{2+8β} + p² − p^{4β} − p^{4+4β}) dβ.
- **Where log(π²/4) comes from** (§9.2, eqs. 9.15–9.16): the factor (π/2)^{2α}(X^{1−2λ})^α. The (π/2)^{2α} is the
  Γ-ratio of the family's functional equation, ξ_k(s) = π^{−(s+|2k|)}Γ(s+|2k|)L_k(s) (eq. 3.12), averaged over k with
  the window weights: π^{2α}Γ(½−α+2k)/Γ(½+α+2k) ≈ (π/2)^{2α} k^{−2α}.

## 2. The general quadratic field (our generalisation; UNVERIFIED as a whole)

Each field-dependent input of K_Φ, and what replaces it. The structure of the recipe (four integrals, the two
bifurcation points) is assumed to carry over; it has not been re-derived for a real-quadratic family.

| Input | ℤ[i] (Chen) | General F (ours) | Status |
|---|---|---|---|
| Γ-ratio constant (eq. 9.16) | log(π²/4) | log(4π²) − C_F, with C_F the RW conductor constant | derived below; reproduces Chen's ℤ[i] value |
| C_Φ,L | L(s, χ₋₄) | L(s, χ_F), χ_F the quadratic character of F: χ₋₄, χ₈, χ₋₃ | by analogy: ζ_F = ζ·L(s, χ_F) |
| A′_Φ | inert p ≡ 3 (4) | F's inert primes: p ≡ ±3 (8) for ℤ[√2], p ≡ 2 (3) for ℤ[ω] | by analogy: inert (p) is principal, λ^k((p)) = 1, same Euler factor |
| Ramified prime | (1 + i) omitted | (√2): λ^k = 1; (√−3): λ^k = (−1)^k | omitted, as Chen does; its size is not bounded here |
| C_Φ,ζ, C′_Φ, Φ̃(½) | — | field-independent | — |

**The Γ-ratio constant, derived.** Write the completed L-function's archimedean part at s = ½ + α and take the ratio
Γ(1−s)/Γ(s) for large character frequency k (θ ∈ [0, 1) normalisation):
- ℤ[i]: (√4)^s Γ_ℂ(s + 2|k|) ∝ π^{−s}Γ(s + 2|k|), ratio π^{2α}(2k)^{−2α} = (π²/4)^α k^{−2α} → log(π²/4). (Chen's value.)
- ℤ[√2]: (√8)^s Γ_ℝ(s + iν)Γ_ℝ(s − iν), ν = πk/log ε, ratio 8^{−α}π^{2α}(ν/2)^{−2α} = (log²ε/2)^α k^{−2α} →
  log(log²ε/2) = −0.946.
- ℤ[ω]: (√3)^s Γ_ℂ(s + 3|k|), ratio 3^{−α}(2π)^{2α}(3k)^{−2α} = (4π²/27)^α k^{−2α} → log(4π²/27) = 0.380.
- In each case the constant is log(4π²) − C_F with C_F = log(d_F·ν₁²) the RW conductor constant (16, 8π²/log²ε,
  27). The ℤ[i] − ℤ[√2] difference is log(π²/(2 log²ε)) = 1.8488 = ΔC, the collapse constant of round 92.

## 3. C_ω verified (round 93 item)

ℚ(ω), d = 3, six units. λ_k(𝔭) = (π/|π|)^{6k} is well defined on ideals (units are 6th roots of unity), with infinity
type 6k, so the completed L-function is (√3)^s Γ_ℂ(s + 3|k|) L(s, λ_k) and the analytic conductor at s = ½ is
≍ d·(3|k|)² = 27k² (the d·(wk/2)² rule with w = 6). So **C_ω = log 27 = 3.2958.**
- **Check against the primary source:** the same rule for ℤ[i] (w = 4) gives Γ_ℂ(s + 2|k|) and 16k², which is
  Chen's ξ_k(s) = π^{−(s+|2k|)}Γ(s+|2k|)L_k(s) (eq. 3.12) and RW's log 16.
- **Not checked against a published ℤ[ω] source** (none read). Status: derived; UNVERIFIED externally.

## 4. Numerical constants (Φ = 1_(0,1]; `rq1b_constants.py` → `results/RQ1B_CONSTANTS.json`)

Contour Re β = 0.1, composite Simpson on |t| ≤ 200 (step 0.05), tails beyond 200 bounded; inert primes below 10⁵
(the A′ sum converges like Σ log p / p²). Imaginary parts vanish to 10⁻¹³.

| Constant | ℤ[i] | ℤ[√2] | ℤ[ω] | tail bound |
|---|---|---|---|---|
| C_F (RW conductor constant) | log 16 = 2.773 | log(8π²/log²ε) = 4.621 | log 27 = 3.296 | — |
| Γ-ratio term log(4π²) − C_F | 0.903 (= log(π²/4), Chen's) | −0.946 | 0.380 | — |
| C_Φ,ζ (field-independent) | −33.954 | −33.954 | −33.954 | 0.10 |
| C_Φ,L | −7.032 | −12.809 | −13.632 | ≤ 0.11 |
| A′_Φ | −2.329 | −2.621 | −7.739 | ≤ 0.04 |
| **K_Φ / C_Φ** | **4.280** | **2.585** | **4.061** | ≲ 0.005 |
| Δ_Φ / C_Φ (field-independent) | −2 | −2 | −2 | — |

- The predicted field difference below λ = ½ is (K_ℤ[i] − K_ℤ[√2])/(C_Φ log X) = 1.695/log X. The conductor term
  alone gives ΔC/log X = 1.849/log X (round 92's flat offset); C_Φ,L and A′_Φ reduce it by 8%. Above λ = ½ the
  formula has no field dependence at all (Δ_Φ is field-independent).
- **Check of the constants on Chen's own statistic** (ℤ[i] at X = 10⁹, their Appendix-A statistic on our angles,
  `results/CHEN_TRANSCRIPTION_X1e9.json`; `results/RQ1B_COMPARE.json`): residual −0.037 to +0.021 for λ = 0.20–0.45,
  −0.019 to −0.004 for λ = 0.60–0.70, and up to −0.12 at λ = 0.50. Away from the bifurcation the constants reproduce
  the statistic they were derived for; at λ ≈ ½ the two-regime formula is not uniform.

## 5. Against the read data (post hoc)

**Post hoc.** `rq1b_compare.py` → `results/RQ1B_COMPARE.json`: the formula against the read data on the fine β grid of
the round-92 collapse run, λ = log K / log X, sealed-model SE. Zero parameters.

**The statistics differ.** Chen's ψ is Λ-weighted and includes inert primes at θ = 0; ours counts split ideals
unweighted. Nothing below corrects for that, so a residual mixes the formula's error with the statistic gap.

| β (λ at 10¹¹) | 10¹⁰: R_ℤ[√2] | 10¹⁰: R_ℤ[i] | 10¹⁰: D | 10¹¹: R_ℤ[√2] | 10¹¹: R_ℤ[i] | 10¹¹: D |
|---|---|---|---|---|---|---|
| 0.20–0.35 (0.18–0.31) | −0.6 to +0.4 SE | +0.2 to +1.3 SE | −1.1 to −0.1 SE | −0.5 to +0.5 SE | −0.3 to +1.4 SE | −1.3 to +0.5 SE |
| 0.40–0.50 (0.35–0.44) | +0.1 to +1.0 SE | +2.0 to +3.1 SE | −1.3 to −1.4 SE | −1.1 to +1.1 SE | +2.6 to +6.3 SE | −2.6 to −3.6 SE |
| 0.55 (0.48) | +4.0 SE | +3.9 SE | +0.3 SE | +5.9 SE | +7.3 SE | −0.6 SE |
| 0.60–0.70 (0.52–0.61) | −4.8 to −10.7 SE | −10.6 to −14.7 SE | +0.8 to +6.7 SE | −6.8 to −17.5 SE | −15.1 to −21.6 SE | +0.8 to +10.2 SE |

- **Rigidity range.** ℤ[√2] alone matches the formula within about 1 SE at both X. ℤ[i] sits above it (2–6 SE at
  β 0.40–0.50), so the predicted D, a flat 1.695/log X (0.074 at 10¹⁰, 0.067 at 10¹¹), is too large there:
  −1.3 to −3.6 SE.
- **λ > ½.** The formula predicts D = 0 and a plateau of 1 − 2/log X (0.913, 0.921). The data have D = +0.030 to
  +0.037 at λ ≈ 0.52 (+6.7 and +10.2 SE) and plateaus of 0.897 and 0.909. The plateau gap is at least partly the
  statistic (Chen's own ℤ[i] statistic at 10⁹ reads 0.899 against 0.9035).
- **At the bifurcation** (β ≈ 0.53–0.62, λ ≈ 0.46–0.54) the formula is not uniform, and the residuals are largest.

**Verdict on round 93's condition: not coherent.** The formula has the same flat-offset shape as the round-92
heuristic below λ = ½ (all its field dependence is a constant K_F) and none above. The data's D has a β-dependent shape
that peaks at the bifurcation, where the formula does not apply. A real comparison would need (i) Chen's statistic
computed on our archives (Λ-weights, inert primes at θ = 0), or a derivation for the unweighted split-only count, and
(ii) the four double contour integrals of their Conjecture 5.1 evaluated at finite X without the λ ≶ ½ split. Neither
is done here. **Per round 93: report and stop. No 10¹² full-curve seal is drafted.**

## 6. Fair check on Chen et al.'s own statistic (round 94; post hoc, zero parameters)

- **Statistic, exactly as their Appendix A:** log N𝔭 weights, inert primes q ≤ √X at θ = 0 (weight 2 log q, generated
  fresh), K = round(X^λ) equal bins, ddof-1 variance over X^{1−λ} log X, λ = 0.100–0.700 (`rq1b_chenstat.py`), both
  fields at the same X from the read archives (`results/CHENSTAT.json`; 1,822 s per field at 10¹¹ on spot).
- **Validated first:** ℤ[i] at 10⁹ reproduces the round-86 transcription to 3.6·10⁻¹⁰ relative and Chen's Figure 1
  within 0.0014 (tolerance 0.01).
- **Formula:** Conjecture 1.2 at finite X with all four constants (§4). The uniform evaluation of the four double
  contour integrals through λ = ½ (Conjecture 5.1 with the zero-sum residues) is **not done**. **The two analogy
  substitutions (L(s, χ_F) and F's inert primes in A′_Φ) remain UNVERIFIED.**
- **Criterion** (committed ded00c98 before the 10¹⁰ / 10¹¹ values were seen): coherent iff |residual| ≤ 2 SE for each
  field and for D at every λ ∈ [0.200, 0.400] at both X (SE model value·2/√K).

| | λ 0.200–0.400 at 10¹⁰ | λ 0.200–0.400 at 10¹¹ | λ 0.425–0.575 | λ ≥ 0.65 |
|---|---|---|---|---|
| ℤ[i] residual | −2.0 to +0.2 SE | −1.9 to +0.7 SE | to −44 SE | −3.6 to −2.4 SE (0.002 below) |
| ℤ[√2] residual | −3.3 to −1.0 SE | −8.2 to −0.4 SE | to −22 SE | −4.4 to −2.5 SE (0.002 below) |
| D residual | −2.4 to 0.0 SE | −4.6 to −0.4 SE | −11 to +19 SE | within ±1.4 SE |

- **Verdict: NOT COHERENT in the rigidity range** (`results/RQ1B_COMPARE2.json`). ℤ[i] fits; ℤ[√2] sits below the
  formula, increasingly with X, so the predicted field difference (1.695/log X) is too large. The misfit is in the
  field where the UNVERIFIED substitutions enter. **Per round 94: no 10¹² seal of this formula, and no P5.**
- **Descriptive:** around λ = ½ the data show D = +0.04 to +0.08 at λ 0.50–0.525, where the two-regime formula has
  no field dependence. Above λ = 0.65 both fields' Chen statistic levels at 1 − 2/log X to within 0.002 (0.911 and
  0.920), the field-independent Δ_Φ term: on Chen's weighted statistic the plateau is accounted for by their lower-order
  term. Our unweighted statistic's plateau (0.896, 0.908) is lower; no formula is derived for it.
