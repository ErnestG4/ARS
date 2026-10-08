# Phase 6.1 — candidates: seal text (PH6_SEAL 6.1)

**Status: TEXT APPROVED (Will, 2026-10-08: "approved IF the text implements D1–D6 as summarized"; CC checked each of
D1–D6 against §§1–5 — implemented as summarized; one addition flagged to Will: §5's "ambiguous ⇒ NOT RESOLVABLE" when
⟨r̃⟩ lies in more than one class band).** Decisions: `PH6_DECISIONS_2026-10-07.md` § 6.1 decisions. Then: code → pre-read (known answers on zeros and nulls; candidate construction
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
- **A1 (Will, 2026-10-08, second round): C3b INAPPLICABLE.** BEK §5 (eqs. 5.2–5.3) reads each matrix size N only near
  one energy E(N) = π√(2N) − 2π; the paper defines no single spectrum, and stitching levels from different N would be a
  new construction.
- **A2 (Will): C3a at N = 6·10⁴** (3·10⁴ positive levels; BEK Lemma 1 makes the spectrum symmetric). Option (b), counting
  both signs, rejected: the mirror half adds no independent information. **Convergence (§2 for C3a):** agreement of the
  low-|E| levels of the N = 3·10⁴ and N = 6·10⁴ runs where both are valid. *Operationalised by CC before the comparison
  was computed (flagged to Will):* the lowest 10% of the N = 3·10⁴ run's positive levels (1,500 levels) are compared
  level by level with the N = 6·10⁴ run; converged iff max |ΔE| ≤ 10⁻³ local mean spacings (as §2). **Fallback (c):** if
  this fails, C3a reads NOT RESOLVABLE (not converged).
- **A3 (Will): PA-6.1-1 adopted with a change to T2.**
  - **T4** (replaces §5's band rule): nearest class by |⟨r̃⟩ − band mean| / band SD over the matched-size Poisson, GOE,
    GUE, GSE bands; assigned iff the nearest is separated from the second-nearest by ≥ 3 SD units, else "ambiguous"
    (NOT RESOLVABLE); integrable crystals INAPPLICABLE (unchanged). Known answers (pre-read): zeros → GUE (8.5 vs 40.0 SD
    units); 800/800 band draws → their own class.
  - **T2** (replaces §4's PASS rule): PASS iff |⟨r̃⟩_cand − ⟨r̃⟩_zeros| ≤ 3·√(SD_cand² + SD_zeros²), both SDs by
    moving-block bootstrap over the T1-matched height ranges; the matched-size GUE band is reported descriptively.
    Reason: at these heights the zeros' own ⟨r̃⟩ (0.6129) is 8.5 SD above the GUE band, so the rule as written failed the
    zeros' known answer (`results/preread61/redpaths61.json`).
- **A4 (Will, 2026-10-08, pre-seal confirmations):**
  - **T1 states what it tests:** the mean density **and** zeros-level rigidity of the counting function, including its
    global offset (the 7/8 constant to ±τ₁ = 0.02, τ₁ calibrated on the zeros' block SD 4.6·10⁻⁴). A spectrum with the
    right mean density but generic random-matrix fluctuations of N(t) (e.g. a random global offset) can FAIL T1 — by
    design. T1's density/slope component (|slope of δ_n on log t_n| ≤ τ₁) is reported separately, descriptively, for
    attribution.
  - **Crystal criterion** ⟨r̃⟩ ≥ 0.9 (integrable crystal ⇒ T2 FAIL, T4 INAPPLICABLE): accepted.
  - **T4 addition:** if ⟨r̃⟩ < 0.9 and it lies more than **15 SD** from every band mean → "intermediate, no standard
    class" (T4 NOT RESOLVABLE). The margin keeps the zeros (8.5 SD from GUE) classified.
  - **T2 bootstrap:** moving blocks of {30, 100, 300} ratios, the widest SD used (for the candidate and for the zeros
    separately), 2,000 replicates.
  - **Candidates are read at their res2 level lists.**
- **Open lead (Will; descriptive, listed together, not merged):** the low-height ⟨r̃⟩ excess (0.6129 over the first
  3·10⁴ zeros, falling with height) and Phase 2's κ̂ > 1 — `specarith/OPEN_LEADS.md`.
