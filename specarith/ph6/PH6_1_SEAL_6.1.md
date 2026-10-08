# Phase 6.1 — candidates: seal text (PH6_SEAL 6.1)

**Status: TEXT with Will's decisions D1–D6 applied (2026-10-08, `PH6_DECISIONS_2026-10-07.md` § 6.1 decisions);
awaiting Will's approval of the text.** Then: code → pre-read (known answers on zeros and nulls; candidate construction
and convergence — levels computed, not read by T1–T4) → seal JSON + seal commit → read candidates. Any later change is
appended under Amendments.

Inherits from PH6_SEAL_6.0 (unchanged): the instrument (Layer A, Layer B readout), the configuration rule (§3:
≥ 3·10⁴ levels, else NOT RESOLVABLE), **T3's verdict rule (§6.3)** and INAPPLICABLE for circular candidates.

## 1. Candidates and declared variants
Definitions are primary-read (`ph6/lit/xp_candidates.md`); every parameter below is declared, none fitted.

| id | construction (source, equation) | declared variants |
|---|---|---|
| C1a, C1b | Sierra–Rodríguez-Laguna H_I = x(p + ℓ_p²/p): roots of 2 arg K_{½+iE/2}(h) = ϑ + π (S-RL 2011 eq. 14; ħ = 1, h = 2π) | **D1: both** — C1a ϑ = π/4 (2011 choice; constant −1/8), C1b ϑ₂₀₁₁ = 0 ≡ ϑ₂₀₁₉ = π (2019 choice; constant 0). A verdict for each. |
| C2 | Berry–Keating 2011 H_II = (x + 1/x)(p + 1/p): shooting C₊(E) = 0 (BK11 eq. 3.3; η = 1/2π, α = 0, E = t/2π, eq. 5.3) | one |
| C3a, C3b | Bolte–Egger–Keppeler lattice op_N(h) (BEK17 eq. 2.16 / 5.1; ℓ_x = ℓ_ξ = √(2πN)) | **D2:** C3a N = 3·10⁴ (primary variant); C3b the E-linked torus (BEK eq. 4.13) at N = 3·10⁴ (declared secondary variant) |
| C4 | Sierra–Townsend LLL: 2θ(E) − E log(L²/2πℓ²) = 2πn (ST08 eq. 22) | L/ℓ declared so that ≥ 3·10⁴ levels lie below the bound |L²/ℓ²| |
| — | Bender–Brody–Müller 2017; Sierra δ-mirror Dirac (2014/2019) | **INAPPLICABLE** (levels defined by the zeros; 6.0 §6.3) |
| fixture | Srednicki truncation (tridiagonal; eigenvalues = zeros of Γ_{∞,N}(½ + iE)) | pipeline known answer; not a candidate |

## 2. Convergence
Each candidate at two resolutions (basis/grid/tolerance and its refinement): the read window's levels agree to
≤ 10⁻³ mean spacings (max over the window), else NOT RESOLVABLE (not converged). C3's spectrum is defined at the
declared N: its check is the eigensolver's residual (≤ 10⁻¹⁰ relative), and N is reported.

## 3. T1 — smooth count (fixes the energy scale before T3)
Declared rescaling from each paper's identification (never fitted). δ_n = (n − ½) − N̄(E_n), N̄ = θ(E)/π + 1 (contains
the 7/8). Statistics over the read window: δ̄ (mean) and the slope of δ_n against log E_n.
**Tolerance (D3):** τ₁ = max(5 × SD_blocks, 0.02), SD_blocks = the block-to-block SD of δ̄ for the zeros at the same
level count (G0-c's 3·10⁴ zeros); τ₁′ for the slope by the same rule. PASS if |δ̄| ≤ τ₁ and |slope| ≤ τ₁′, else FAIL
with attribution (constant / slope). Known answers: zeros PASS; C1a/C1b read their own constants.

## 4. T2 — local statistics (one witness)
⟨r̃⟩ primary; NNS, Σ², Δ₃ descriptive. References (D4, D5):
- **GUE:** band from GUE draws at the candidate's level count (Dumitriu–Edelman β = 2, central window, as ARS-RH
  Phase 1), labelled by the large-N value 0.5996 (Atas et al. 2013; `rtilde_refs.py`);
- **the zeros at matched height:** ⟨r̃⟩ of the zeros over the T1-matched height range, CI by moving-block bootstrap.
PASS if ⟨r̃⟩ lies in both bands; FAIL otherwise (reported per reference). Integrable crystals (⟨r̃⟩ → 1) FAIL.

## 5. T4 — symmetry class (D6)
Nearest class by ⟨r̃⟩ using **matched-size bands** from Poisson, GOE, GUE, GSE draws (labels: large-N constants,
`rtilde_refs.py`); the class is assigned only if ⟨r̃⟩ lies inside exactly one band, else "ambiguous" (reported as NOT
RESOLVABLE). **INAPPLICABLE for integrable crystals** (smooth/picket spectra: C1, C2, C4 as expected; decided by T2's
crystal criterion before T4 is read). NNS-KS (`sessionK/nns_stats.classify_nns`) and Σ² + Δ₃
(`sessionK/nns_stats.classify`) reported descriptively. Known answers: zeros → β = 2; GOE/GSE/Poisson draws at 3·10⁴
levels → their own classes (red paths).

## 6. Verdicts
Per candidate (and declared variant): the 4-tuple (T1, T2, T3, T4) ∈ {PASS, FAIL, NOT RESOLVABLE, INAPPLICABLE}. No
"Riemann Hamiltonian" language unless all four PASS, and then only "candidate passes the instrument".

## 7. Pre-read (before the seal commit; no candidate read by T1–T4)
1. Known answers: the zeros (G0-c set) through T1, T2, T4 → PASS, PASS, β = 2; τ₁ computed; the Srednicki fixture's
   eigenvalues equal the zeros of Γ_{∞,N}(½ + iE) to tolerance.
2. Matched-size bands (GUE for T2; Poisson/GOE/GUE/GSE for T4) at 3·10⁴ levels; red paths: GOE/GSE/Poisson draws
   classified as themselves; a picket fence → INAPPLICABLE (crystal) for T4, FAIL for T2.
3. Candidate construction + convergence; levels stored and hashed, not read by T1–T4.
4. Seal JSON: code hashes, candidate level files' hashes, τ₁, bands, variants.

## Amendments
(none)
