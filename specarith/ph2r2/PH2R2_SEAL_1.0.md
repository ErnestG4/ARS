# Phase 2, new part — ζ pair correlation with arithmetic lower-order terms (PH2R2_SEAL 1.0)

**Status: TEXT APPROVED (Will, 2026-10-09: "if it implements R1–R5 as decided, approve it"; CC checked R1–R5 against §§1–3 — implemented; two values the text names but does not fix — u_max (R4) and the bootstrap block lengths (R5) — are declared in the pre-read before any fresh zero is read). Decisions: twelfth round, `ph2/PH2_DECISIONS_2026-10-07.md`;
** Then code → pre-read (G0, primary test-function choice, power, reachability) →
dry run → seal JSON + seal commit → download/verify/decode fresh files → run. No fresh-height zero has been read
(files pinned before download: `FRESH_PLATT_PINS.md`, commit 697ddbb3; not yet downloaded).

## 1. What is tested, and its standing
**Source (R1): Conrey & Snaith 2007, Theorem 4.1** (Proc. LMS 94 (2007) 594; arXiv math/0509480 v2): the pair-correlation
sum Σ_{0<γ,γ′≤T} f(γ − γ′) with all arithmetic lower-order terms, error O(T^{1/2+ε}). **It rests on the L-functions ratios
conjecture (their Conjecture 2.1):** this phase tests a conjecture's lower-order prediction, not a theorem about ζ.
CS07 state it is Bogomolny–Keating's formula.

**Framing (R2): probable replication.** BK's formula was compared with Odlyzko's zeros before (Berry–Keating, SIAM Rev.
1999, Figs. 3 and 6: Σ² near t ≈ 2.7·10¹¹ and 3.7·10⁸, visual, near-perfect; `lit/BK99_ODLYZKO_COMPARISON.md`). The claim
this phase can make is an **independent quantitative replication**: a calibrated amplitude μ of the lower-order term with
a CI at five fresh heights, with sealed nulls and red paths.

## 2. Statistic and estimand
Raw zeros (no unfolding: CS07 is stated for raw γ). Per fresh bin (one Platt file, R1–R5): S_f = Σ f(γ − γ′) over ordered
pairs γ ≠ γ′ **both inside the file**, |γ − γ′| ≤ u_max (R4: declared u_max; the excluded fraction — pairs one of whose
members lies outside the file — reported). Prediction from CS07 Thm 4.1 by differencing its T-dependence over the
file's [t₀, t₁), with the within-file pair restriction applied identically to the prediction.
**Estimand μ:** S_f = RMT_f + μ·LOT_f (RMT_f: the theorem's leading, sine-kernel-density part; LOT_f: its arithmetic
lower-order part). μ = 1: the conjecture's prediction; μ = 0: leading order only.

**Test function (R3):** **one primary f**, chosen in the pre-read, before any fresh zero is read, from a small declared
family (Gaussian bumps f_{u,w}(x) = exp(−(x − u)²/2w²) + (x → −x), u and w in units of the local mean spacing; family
fixed in the pre-read code), as the member that maximises the predicted |LOT_f| / SD(S_f), with SD(S_f) from CUE_N
surrogates at the bin's size and density (theory + surrogates only). 2–3 other members reported descriptively. No sweeps.

## 3. Tolerances, resolvability and verdicts (R5)
- **CI on μ̂:** the wider of (a) the surrogate-calibrated CI (G0b) and (b) a moving-block bootstrap of the bin's own zero
  sequence over a declared block-length sweep (the widest used) — as Phase 2 A1.
- **Resolvable** iff the pre-read power to reject μ = 0 is ≥ 0.80 (per bin); otherwise NOT RESOLVABLE pre-data.
- **Resolution target:** half-width h = min(3 × predicted SD(μ̂), 0.5); reported achieved vs predicted.
- ~~**Achieved rule (as PH2 A6):** an achieved CI that cannot exclude μ = 0, or with half-width > 0.5, reads
  NOT RESOLVABLE (achieved) — never PASS/FAIL.~~ **Superseded by A2** (it judged where μ̂ landed, not precision).
- **G1:** PASS if 1 ∈ CI(μ̂), FAIL otherwise. **Power arm:** μ = 0 excluded.
- Per-bin results are the finding; a pooled μ̂ is descriptive.

## 4. Known answers and red paths (pre-read, before any fresh zero is read)
- **G0a:** CS07's arithmetic factors A(η), B(η) and the ζ-near-1 terms reproduced independently (1e-12); CS07 Thm 4.1 vs
  CS08 §5 (J*-form) vs BBLM v1 eqs. 11–12 numerically identical for a test f.
- **G0b:** CUE_N surrogates placed at each bin's density (μ_CUE computable exactly from the CUE two-point function; its
  N⁻⁴ term carries the 1/15 missing in BBLM v1 eq. 8): bias of μ̂ and coverage ≥ 95% of the §3 CI, including the
  bootstrap.
- **G0c:** per-bin power to reject μ = 0 (sets resolvability) and the target half-width.
- **Red paths (reachability computed pre-data; required only where power ≥ 0.80, as PH2 A8):** a wrong density
  (log(E/2πe)) in the prediction must FAIL; the LOT term with its sign flipped must FAIL; pair-structure-destroying
  shuffle (i.i.d. resampled spacings, rebuilt sequence) must change S_f (specificity witness that S_f reads pair
  correlations beyond the nearest neighbour).
- **Dry run:** full pipeline on CUE_N surrogate heights at full size, plus a witness that the (achieved) rule fires
  (expectations as amended by A2).

## 5. Data
Five fresh Platt files R1–R5 (`FRESH_PLATT_PINS.md`), downloaded by hand (human gate), md5-verified; decoded only after
the seal. The seen Phase 2 bins (A, B, P1–P6) under this statistic: descriptive only.

## Amendments
- **A1 (Will, 2026-10-09, before any fresh zero is read) — a declared descriptive output.** The CUE surrogates have no
  correlation beyond a block, but the zeros carry long-range arithmetic structure (the log p oscillations Phase 6
  measured) that slowly modulates local pair counts and can inflate the true variance of μ̂ beyond the surrogates'. The
  §3 bootstrap sweep (moving blocks of 100, 1,000 and 10,000 levels, the widest CI used) is the safeguard; unchanged. In
  the read, report per bin how the bootstrap SD of μ̂ grows with block length (100 → 1,000 → 10,000), beside the
  surrogates' ratio at the same block lengths. Still growing at 10,000 = the zeros' long-range arithmetic structure in
  the error bars: descriptive, linking R₂ to Phase 6; it changes no verdict.
- **A2 (Will, 2026-10-09, before any fresh zero is read) — the achieved rule judges precision only.** The v1 dry run
  showed every μ = 0 surrogate reading NOT RESOLVABLE (achieved) with tight CIs (half-widths 0.025–0.053) that exclude
  μ = 1: the v1 rule fired on "CI contains 0", which is the outcome "no arithmetic term", so the instrument could never
  FAIL Conrey–Snaith in favour of μ = 0. Replacement for §3's achieved rule:
  - **NOT RESOLVABLE (achieved)** iff the achieved CI contains **both** 0 and 1, or its half-width exceeds 0.5 (R5's
    ceiling) — a statement about precision only. (A CI containing both has half-width ≥ 0.5, so in practice the guard
    is the width ceiling; the "both" clause states its meaning.)
  - Otherwise **G1: PASS iff 1 ∈ CI, else FAIL.** Whether 0 ∈ CI is reported beside every verdict (descriptive).
  - Dry-run expectations: μ = 0 surrogate → FAIL; planted μ = 1 → PASS; a deliberately small sample → NOT RESOLVABLE
    (achieved), at both truths (witness), with a 1% control reading PASS (μ = 1) and FAIL (μ = 0).
  - Red paths are unaffected: their power is the probability that the reading excludes 1, i.e. FAIL under A2.
- **A3 (Will, 2026-10-09, before any fresh zero is read) — A1 reported three ways; drift removal declared.** The G0b
  surrogates showed R1's bootstrap SD of μ̂ doubling from 100- to 10,000-level blocks with no long-range structure
  present: the smooth density drifts across R1's height range (6.7·10⁶–8.8·10⁶), the per-level expected contribution
  drifts with it (+3.7% for the primary), and a moving-block bootstrap reads a deterministic trend as variance
  (`g0b_trend_check.py`: predicted 2.11, observed 2.03; R2–R5 drift < 0.5% and stay flat). The zeros share the drift.
  A1's growth (100 → 1,000 → 10,000, as SD ratio to the 100-level block) is therefore reported per bin:
  1. **raw**;
  2. **surrogate-relative:** raw ÷ the G0b surrogates' mean growth at the same block lengths (pinned in the seal JSON);
  3. **drift-removed:** the same bootstrap on c̃_i = c_i · e(t_c)/e(t_i), where c_i is level i's pair contribution and
     e(t) = 2∫₀^{U_MAX δ} f(r) ρ(t)(1 − sinc²(ρ(t) r)) dr is its expectation at height t under the sine kernel at the
     exact smooth density ρ = N̄′(t) (f at the bin's fixed δ; LOT omitted so the normalisation does not depend on μ).
     This is per-block normalisation by the exact smooth density, taken at level resolution
     (`r2run.drift_removed`). Pre-data check: on a synthetic R1-sized drifting series with i.i.d. noise, the raw growth
     is 1 → 2.91 → 8.90 and the drift-removed 1 → 0.98 → 0.92 (`checks/a3_drift_removal_check.py`).
  Only growth beyond (2) and (3) reads as the zeros' long-range arithmetic structure. Descriptive; never enters a CI or
  a verdict.
