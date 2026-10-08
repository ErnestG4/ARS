# Phase 2, item 1 — ζ spacings against CUE(N_eff) per height (PH2_SEAL 2.1)

**Status: SEALED 2026-10-07 (Will's GO, ninth round): seals/PH2_SEAL_2.1.json, amendments A1–A8 below. Text approved (fifth round) with amendment A1 (CI robustness), written into §5–§6 below.
The seal is not complete:** code → pre-read (configs, CUE known answers, estimator calibration incl. bootstrap coverage,
tolerances, resolution targets, red-path reachability, data acquisition verified by md5/sha256) → dry run → seal JSON +
seal commit → run. No Phase-2 zero data read. Any later change is appended under Amendments, never edited in.

Sources: programme brief Phase 2; `PH2_DECISIONS_2026-10-07.md` (three rounds; they win); `lit/bblm_bk.md`,
`lit/VERIFY_bblm_bk_and_platt.md` (primary-source checks). Design numbers below are pre-data arithmetic.

---

## 1. What is tested
BBLM (2006): the nearest-neighbour **consecutive-spacing** distribution of ζ zeros at height E is that of CUE(N_eff),
N_eff = log(E/2π)/√(12Λ), Λ = 1.5731510713… (BFM 2017; BBLM print 1.57314). To O(N⁻²):
p_N(s) = p₀(s) + N⁻² p₁(s), p₁ = −(1/12)(s²p₀)″ (Forrester–Shen 2025, eq. 2.8; = BFM's operator form).

**Two arms, never mixed (Will, 4a):**
- **PRIMARY — "N_eff alone"** (BBLM's convention: p₀ + N_eff⁻² p₁, no rescaling of the correction).
- **SECONDARY — BFM higher-order:** kernel K + L_RZ N⁻², L_RZ = π(x−y) sin(πᾱ(x−y))/6, ᾱ = 2α − 1, α = 1 + C/log(E/2π),
  C = Q/Λ = 1.47211 (BFM eqs. 4.3–4.6, their scale convention). BBLM eq. 24 with BBLM's α is NOT used for the secondary
  (BFM footnote 5: BBLM's journal eq. 28 mis-sets ᾱ = α).

**Primary statistic (one witness): the consecutive-spacing distribution p(s).** ⟨r̃⟩ is NOT used as a test: its CUE_N
correction is O(N⁻⁴) (the O(N⁻²) term cancels; Nishigaki 2025), so it is blind to N_eff. ⟨r̃⟩, F(α), Σ², Δ₃ are reported
descriptively only (Task B: one witness).

## 2. Unfolding (Will, 4b)
x_k = N̄(γ_k) = θ(γ_k)/π + 1, the exact Riemann–Siegel θ (mpmath at the precision the height needs; the high tables are
stored as offsets from a base, so θ is evaluated at base + offset with ≥ 40 digits). Spacings s_k = x_{k+1} − x_k.
Check: mean spacing within its sampling band of 1 in every bin.

## 3. Height bins and data (declared before any Phase-2 zero is read)
Sealed bins need N_eff ≥ 2 (log(E/2π) ≥ 8.7); lower heights are descriptive only (Will, decision 2). **Justification,
from the pre-read (G0c):** the next-order term — the measured O(N⁻⁴) remainder of p₀ + p₁N⁻² against the exact CUE_N law,
and the SECONDARY-minus-PRIMARY shift — is reported as a function of N; the seal text records its size at N = 2 and
below (N_eff = 0.19 at the first zero, 1.17 at γ = 10³, where the leading correction alone exceeds 70%).

| bin | source | log(E/2π) | N_eff | zeros | design rel sd(N̂) |
|---|---|---|---|---|---|
| A | Odlyzko zeros6 (hashed) | 9.4–10.5 | 2.16–2.42 | ~3·10⁵ | ~0.7% |
| B | Odlyzko zeros6 | 11.0–12.1 | 2.53–2.79 | ~5·10⁵ | ~0.5% |
| P1…P6 | Platt/LMFDB, one bulk file each, md5 from the site's md5.txt | ≈ 13, 15, 17, 19, 21, 22.3 | 2.99–5.13 | ~7·10⁶ each | 0.2–0.5% |
| H1 | Odlyzko zeros3 (# 10¹²+) | 24.48 | 5.63 | 10⁴ | ~17% |
| H2, H3 | Odlyzko zeros4, zeros5 | 44.58, 46.83 | 10.26, 10.78 | 10⁴ each | ~60% |
Platt files (Will, decision 4): the file per height (≈ 13, 15, 17, 19, 21, 22.3) is chosen from the site's file index
by height only — the file whose start height is the largest ≤ E = 2π·e^L — and its md5 (from the site's md5.txt,
fetched 2026-10-07, sha256 6ca3534a…8521, 14,580 entries) is **written here before the file is downloaded**; the download
is verified against it. Gap log(E/2π) 24.5–44.6: no public data — stated as a limit.

| bin | target L | file | height range | md5 (pinned before download) |
|---|---|---|---|---|
| P1 | 13 | zeros_2546000.dat | [2,546,000, 4,646,000) | 5642999b13dc52270064a055b1b6b15f |
| P2 | 15 | zeros_19346000.dat | [19,346,000, 21,446,000) | 24dedbc917f3a006690026dd7cda930b |
| P3 | 17 | zeros_151646000.dat | [151,646,000, 153,746,000) | 242ca86d1691d1a93623b2f8ce2cbf33 |
| P4 | 19 | zeros_1119746000.dat | [1,119,746,000, 1,121,846,000) | 8d01c4c244daf4751f3c251de53008af |
| P5 | 21 | zeros_8284946000.dat | [8,284,946,000, 8,287,046,000) | 8adc69731784c1958ca60d67686e98b4 |
| P6 | 22.3 | zeros_30404246000.dat | [30,404,246,000, 30,406,346,000) | 95f2c89b2b4572e5529cd25a79e9def8 |

Each file spans a height width of 2.1·10⁶ (≈ 4.3–7.5·10⁶ zeros). In P1 N_eff varies 2.99 → 3.13 across the file, so the
estimand is the **ratio κ = N/N_eff**, fitted with each spacing's own local N_eff(E_k) (§4); the same estimator is used in
every bin (in the high bins the variation is negligible).
(Design sd from the Fisher information of N in p₀ + p₁N⁻² with a Wigner-surmise p₀, independent spacings: optimistic;
the calibration in §5 gives the real one.)

## 4. Estimand and per-bin arms
Per bin: **κ̂** = maximum-likelihood κ in the model family evaluated at N_k = κ·N_eff(E_k) for each spacing (PRIMARY:
p₀ + p₁N_k⁻²; SECONDARY: BFM higher-order with ᾱ(E_k) by its own formula), with a CI from the calibrated estimator (§5).
N_eff ∈ CI(N̂) below means κ = 1 ∈ CI(κ̂); "N = ∞" means κ = ∞ (1/κ² = 0).
- **G1 (match):** N_eff ∈ CI(N̂). PRIMARY: CI widened by the truncation allowance (§6). SECONDARY: statistical CI only —
  the sharp test (Will, decision 3). PASS / FAIL / NOT RESOLVABLE.
- **Power arm (Will):** N = ∞ (sine kernel) excluded — the CI of 1/N̂² excludes 0.
- **Resolution arm (Will, decision 5):** per-bin target half-width **h_bin = min(3 × the pre-read's predicted SD of
  N̂/N_eff, 0.20)**, sealed from the pre-read — ±20% is the floor target (never looser); "pinned at h_bin" ⇔
  CI(N̂) ⊂ (1 ± h_bin)·N_eff, and "pinned at ±20%" is reported separately. The achieved interval is always reported.
- **PRIMARY NOT RESOLVABLE rule (Will, decision 3):** in a bin where the widened PRIMARY tolerance either cannot exclude
  N = ∞ or is wider than the ±20% floor (the resolution arm meaningless), the PRIMARY verdict there is NOT RESOLVABLE —
  decided from the pre-read, before data.
- Per-bin results are the finding; a pooled N̂/N_eff trend is descriptive.

## 5. G0 — known answers, all run before any Phase-2 zero is read
- **G0a constants:** Λ, Q, C recomputed (exact prime-zeta series) = BFM's digits; BBLM's (E, N_eff, α) at 2.5·10¹⁵ and
  1.3·10²² and BFM p. 18's (N, α, ᾱ) reproduced.
- **G0b CUE_N exact vs draws:** spacing distribution from det(I − K^N) (Bornemann Gauss–Legendre) = Monte Carlo CUE draws
  (Haar unitary, integer N ∈ {3, 5, 8, 11}) within MC error; BFM's two appendix values reproduced to 1e-12.
- **G0c expansion accuracy:** p₀ + p₁N⁻² vs exact det(I − K^N) at integer N: the O(N⁻⁴) remainder measured; it sets the
  primary model's truncation allowance (§6) at each bin's N_eff.
- **G0d estimator known answer (the whole chain):** CUE_N eigenphases at integer N (blocks concatenated, matched bin
  sizes) mapped onto ζ's density by N̄⁻¹ and unfolded back with the exact θ → κ̂ must recover κ with calibrated bias and
  CI coverage (≥ 95% nominal). Without this, a residual cannot be read (calibrator-bias lesson). **A1 (Will): G0d also
  validates the moving-block bootstrap's coverage on the same CUE surrogates, for every declared block length.**

## 6. Tolerance (G1)
- **Statistical CI** of κ̂ (both arms) = **the WIDER of** (a) the CUE-calibrated CI from G0d's sampling distribution at
  the bin's size and (b) **(A1, Will) a moving-block bootstrap CI of the bin's own spacings**, block lengths declared
  pre-data: L_b ∈ {10, 30, 100} × ⌈N_eff⌉ levels (the widest of the three is used). Reason (Will): concatenated CUE_N
  blocks impose a within-block sum constraint and zero between-block correlation that the zero sequence does not share,
  so a CUE-calibrated CI alone may be too narrow for the zeros.
- **PRIMARY only — truncation allowance (Will, decision 3; the primary is a leading-order law):** the shift in fitted N
  between the PRIMARY family and (i) the exact CUE_N law (G0c) and (ii) the SECONDARY family at that height, computed
  pre-data from theory only, added to the CI half-width. At 0.2–0.5% statistical precision the terms "N_eff alone" omits
  (α − 1 = C/log(E/2π) ≈ 6–15% on the correction's argument) are visible; without the allowance the leading-order law
  would FAIL on known higher-order mathematics, not on the zeros.
- **SECONDARY: statistical CI only** — the higher-order model is tested sharply.

## 7. Red paths (each must fail where reachable; reachability computed pre-data)
- **RP-misprint (Will):** unfold with the log(E/2πe) density form (FM15 eq. 1.1 as printed) — a ~1/log(E/2π) scale
  error (2% at the top, ~10% in bin A), larger than the effect. G1 must FAIL (mean-spacing check and N̂).
- **RP-Λ (Will) — declared UNREACHABLE:** BBLM's printed Λ = 1.57314 moves N_eff by ~3.5 ppm, far below every bin's
  resolution. Listed as INAPPLICABLE at every bin, as Phase 6 listed its unreachable red paths.
- **RP-mix:** secondary arm with BBLM's α in place of ᾱ (the wrong-slot error 4a forbids) — must be distinguishable
  where reachable (reachability per bin; probably only in P-bins).
- **RP-N∞:** the power arm itself (sine kernel) — must be rejected where resolvable.
- **RP-shuffle:** spacings drawn i.i.d. from the bin's own empirical distribution (destroys nothing in p(s)) — must NOT
  change N̂ (a specificity witness that the estimator reads p(s) only).

## 8. Outputs
PH2_FINDINGS.md: per-bin table (N_eff, N̂ ± CI, G1, power, resolution, secondary), G0 table, red paths; figure of N̂/N_eff
vs log(E/2π) with CIs; the 24.5–44.6 gap marked. The arithmetic leg (programme Phase 2 "new part": singular-series terms
for the residual) is a separate later item.

## 9. Decisions (Will, fourth round; `PH2_DECISIONS_2026-10-07.md`)
1. Primary statistic p(s); ⟨r̃⟩/Σ²/F(α)/Δ₃ descriptive, one witness.
2. Sealed bins N_eff ≥ 2, cutoff justified from the pre-read's next-order estimate; lower bins descriptive.
3. Truncation allowance for the PRIMARY only; PRIMARY NOT RESOLVABLE where the widened tolerance cannot reject N = ∞ or
   exceeds the ±20% floor; SECONDARY statistical only.
4. Platt heights ≈ 13, 15, 17, 19, 21, 22.3, one file each, md5 in the seal before download.
5. Per-bin resolution target sealed from the pre-read (3 × predicted SD of N̂/N_eff), ±20% floor; achieved intervals
   always reported.

## Amendments
- **A1 (Will, 2026-10-07, at approval):** CI robustness by a moving-block bootstrap of each bin's spacings (L_b ∈ {10, 30,
  100} × ⌈N_eff⌉); G1 uses the wider of the CUE-calibrated and bootstrap CIs; G0d validates bootstrap coverage on CUE
  surrogates. Written into §5 (G0d) and §6.
- **A2 = PA1 (Will, 2026-10-07, sixth round):** κ̂ (§4, both arms, every bin) is the conditional maximum-likelihood
  estimate on the window s ≤ S_C = 2.0, the model normalised over the window; the c-range is where the model is a
  density on the whole window. Reason: the first-order family turns negative at s ≈ 2.2–3 at the sealed heights, and the
  full-range MLE is pinned by the largest spacing (CUE known answer: κ̂ = 1.40 at true κ = 1). Windows 1.8 and 2.2 are
  reported descriptively (sensitivity), never as verdicts.
- **A3 = PA2 (Will):** §6 PRIMARY allowance = the **larger** of |δ_i| (exact CUE_N) and |δ_ii| (SECONDARY) at the bin's
  lowest-N_eff edge. Rationale (Will): the two shifts measure the distance to two ALTERNATIVE references for the truth
  (ζ = CUE(N_eff) vs ζ = BFM higher-order); only one can hold, so the allowance covers the larger, not their sum.
  Sum-based PRIMARY verdicts for bins A and B are reported descriptively.
- **A4 = PA3 (Will):** the allowance at a bin's real N_eff uses the BFM kernel sin(πd)/(N sin(πd/N)) at real N (its
  analytic continuation; CUE_N itself is defined at integer N), cross-checked against the integer-N values (G0c).
- **A5 = PA4 (Will):** beta.lmfdb.org serves a JavaScript human gate to scripted clients; the six Platt files were
  downloaded by hand by Will and verified against the md5s pinned in §3 (all six OK, 2026-10-07).
- **A6 = PA5 + refinement (Will, 2026-10-07, seventh round):** (i) the SECONDARY uses §4's NOT RESOLVABLE rule on its
  statistical CI (no allowance): NOT RESOLVABLE where it cannot exclude N = ∞ or is wider than ±20%, decided pre-data
  from the predicted spread. (ii) Red-path checks that cannot fire in a bin read INAPPLICABLE. (iii) Post-data, any arm
  whose ACHIEVED CI (PRIMARY: widened) cannot exclude N = ∞ or has half-width > 0.20 reads "NOT RESOLVABLE (achieved)"
  — flagged, never PASS/FAIL — and its dependent red-path checks read INAPPLICABLE (achieved). Predicted and achieved
  half-widths are reported per bin and arm.
- **A7 = PA6 (Will, 2026-10-07, eighth round):** the PRIMARY's h_bin resolution arm is INAPPLICABLE pre-data in every
  bin (the predicted widened half-width exceeds h_bin everywhere: primary resolution is bounded by its own theoretical
  truncation). Reported for the PRIMARY: the ±20% floor arm and the achieved interval. Statistical resolution is carried
  by the SECONDARY's h_bin arm (unchanged).
- **A8 = PA7 (Will):** a red-path check is REQUIRED to fail only where its pre-read power is ≥ 0.80; below that its
  outcome is reported descriptively, not scored. RP-mix: required in A (0.84), B (0.94), P1 (0.93); descriptive in P2
  (0.59) and wherever lower. Checks whose arm is NOT RESOLVABLE remain INAPPLICABLE (A6).
