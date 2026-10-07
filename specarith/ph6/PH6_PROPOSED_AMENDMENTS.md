# Phase 6 — proposed amendments to PH6_SEAL_6.0.md (for Will; none applied)

Written overnight 2026-10-07 from the pre-read (seal §9). The seal text says the red-path reachability result is
reported to Will before the seal commit; this file is that report's decision part. Nothing below is in force until
Will approves it and it is appended to the seal's Amendments section.

## A1. G1-s — small-window Maass identity (tests the elliptic weights)

**Finding.** At G1's sealed window (T₀ = 49.38, σ = 5.81) the elliptic terms (1/8)∫h/cosh(πr) and
(1/(3√3))∫h cosh(πr/3)/cosh(πr) are ~e⁻³⁶: the test function is negligible near r = 0, where those kernels live. RP5
("elliptic weights ×2") is therefore INAPPLICABLE in both sectors (max |removed term|/2ε ≈ 1e-10;
`results/preread/preread_tables.json`). G1 as sealed cannot test the very weights Will's failure ladder (round 3)
names first. This is the same situation G0-s fixed for ζ's smooth terms.

**Proposal.** Add G1-s: the per-sector Maass identity (seal §5, unchanged formulas and tolerance construction) at two
fixed windows, Layer A only, with RP5–RP9 and their reachability rule:

| window (T₀, σ) | upper edge T₀ + 8.5σ (list complete to 98.765) | max \|elliptic term\| | RP5 reach ratio (estimate) |
|---|---|---|---|
| (12, 4) | 46.0 | 4.0·10⁻³ | ≈ 2·10³ per sector |
| (20, 5) | 62.5 | 1.2·10⁻⁴ | ≈ 3·10¹ per sector |

(Estimate from the RHS and a density-based ε; the sealed ε would be computed by preread.py exactly as for G1.) Both
windows also put weight on the lowest forms (r₁ = 9.53 odd, 13.78 even), so they exercise the region Session K found
GOE-like in the odd sector — irrelevant to an exact identity, but noted.

**Cost.** Minutes. No new data.

## A2. Wording: RP16 (drop the mirror term) is marginal

RP16 is reachable only at G0-s window (10, 4), and there only by its upper bound (Σ w(−γ) gives 2.2× the threshold).
The actual |M(τ)| is not computed before the gate run (it is part of the LHS). If at the run it falls below 2ε, the seal
already says RP16 is reported INAPPLICABLE. No change proposed; flagged so it is not a surprise.

---

The amendments below come from the independent code review (`REVIEW_code_v1.md`, 2026-10-07 ~02:35) and the null
calibration draws. Empirical numbers are from `results/preread/` (bands = 100 calibration draws per family; no gate
statistic). Code already implementing a proposal is marked "PROPOSED" in the source and is reverted if Will declines.

## A3. Minimum set over the weight vector's support (review B1) — BLOCKER as sealed

**Finding.** §6.3 applies M = {2,3,4,5,7} to every weight vector. Under χ₋₄ weights a₂ = a₄ = 0, so 2 and 4 can never be
in R and every χ₋₄ reading is NOT RESOLVABLE — the exact χ₋₄ truth included. G2's "vs χ weights: PASS" is unreachable;
G0's "vs χ₋₄: FAIL" and RP17 come out NOT RESOLVABLE instead of FAIL.
**Proposal.** M_w = M ∩ {n : a_n ≠ 0} (= {3, 5, 7} under χ₋₄; unchanged {2,3,4,5,7} under ζ, so candidates are
unaffected). "Required FAIL" of a cross-reading means T3 = FAIL under M_w. **Code: implemented (ph6lib.t3_verdict).**
Check: χ₋₄ truth vs χ₋₄ weights → PASS; ζ truth vs χ₋₄ weights → FAIL (WEIGHT, SIGN at p ≡ 3 mod 4; SILENCE at 2^k).

## A4. The design table's missing √2, and what it does to G0-c and G2 (review B2)

**Finding.** The joint least-squares fit on the sealed 13-point grid gives Var c_n = √2 × the pointwise variance (σ-free;
review derivation, confirmed by the calibration draws: mean|c_n|²/pointwise ≈ 1.41). The seal's §6.2 design numbers
used the pointwise variance.
**Empirical resolvable sets from the calibration bands** (`results/preread/design_table.json`):

| config | seal design | review (LS-corrected theory) | **empirical (bands)** | sealed requirement |
|---|---|---|---|---|
| G0-c (3·10⁴ zeros) | 26/34 | ~21/34 | **24/34**, M ⊆ R | \|R\| ∈ [22, 30] → **met** |
| G2 (T = 2·10⁴) | 22/28, 9 ∈ R | 14/28, 9 ∉ R | **15/28, 9 ∉ R** | SIGN at 9 (−) → **cannot be scored** |
| G0 | 29/34 | 28/34 | (G0 draws pending) | none |

**Decisions for Will.**
1. G0-c: the sealed window holds empirically (24). Keep [22, 30] as sealed (proposed), or re-centre it on the corrected
   design (~21) — not needed now.
2. G2 height: (a) keep T = 2·10⁴ and report SIGN at 9 as NOT RESOLVABLE (the other three named sign arms 3, 5, 7 are in R);
   or (b) raise G2 to T = 4·10⁴ (review: 2B₉/|a₉| = 0.80 there, 9 ∈ R with ~20% margin). **χ₋₄ zeros on [20000, 40000]
   are being computed overnight as a contingency**, so (b) costs no waiting.
3. §6.2's design values are replaced by the empirical ones in the seal JSON (they come from the sealed band rule).

## A5. Null known answer (review M1) — FAILS as sealed, for reasons that are not about the nulls

**Finding.** §7 seals "mean |c_n|² within 20% of the form-factor prediction" for every n, with the pointwise formula.
- Literal (sealed) evaluation: **FAIL** at G0-c and G2 (median ratio 1.41 GUE / 1.41 Poisson at G0-c, 1.20 / 1.39 at
  G2; 45–86 of 89 n outside 20%) — the √2 of A4.
- With the least-squares-propagated prediction P·Cov·Pᴴ (as `preread.predicted_s` computes): median ratio 0.998–1.008,
  range 0.74–1.33, and 2–4 of 89 n outside ±20% — the sampling noise of 100 draws (~10% per n on |c|²), so a per-n 20%
  bar fails by chance alone.
**Proposal.** Prediction = P·Cov·Pᴴ. Criterion: (i) the median over n of mean|c_n|²/pred² within ±10%, and (ii) at most
5% of the n outside the Bonferroni band of the Gamma(100, 1/100) law for a mean of 100 |complex Gaussian|² (≈ [0.67, 1.38]).
Empirically all four (config, family) pairs pass both. (The ⟨r̃⟩ check passes as sealed: 0.5998 / 0.5996 inside the
arsrh band [0.5952, 0.6065]; the "0.6027" in §7's wording is the 3×3 surmise value and should read "the arsrh Phase-1
band" only — review M2.)

## A6. G2-s — small-window χ₋₄ identity (review M3; parallel to A1)

**Finding.** RP11 (Γ parity a = 0 vs a = 1) cannot fire at G2: at σ = 1176.5 the Γ term is below 10⁻³⁰⁰ for τ ≥ 0.5, so
the χ₋₄ Γ factor ψ(¾ + iu/2) is never tested. Only G0-s exercises the Γ path, and only with a = 0.
**Proposal.** G2-s: the χ₋₄ identity at fixed small windows (e.g. (10, 4) and (40, 3)) on the χ₋₄ zeros already computed
from 0, Layer A only, with RP10 (χ ≡ 1), RP11 (a = 0), RP13 (drop Γ). Reachability computed by the pre-read rule.

## A7. ε_rhs wording (review M4)

§5.1 says "mpmath quadrature error estimates (dps 30)". The code evaluates the RHS in float64 (trapezoid with step
halving; closed-form lines) with a DERIVED float64 rounding bound (phase and Gaussian rounding of each prime line,
trapezoid rounding, addition rounding) plus the tails. It reproduces the 30-digit pilot identity to ≤ 6·10⁻¹⁴ (bound
1.2·10⁻¹¹ there), and the review's 40-digit spot checks (4.8·10⁻⁹ at G0) sit inside the new bound. Proposal: replace the
sentence with this description. (mpmath quadrature over a 26σ window with ~10⁵ oscillations is not practical at G0.)

## A8. χ₋₄ zeros recipe (review m8)

§1 names one call `lfunzeros(lfuncreate(-4), 20000)`; the zeros were produced as 20 interval calls [a, b] at
realprecision 38 through GP strings (cypari2's library calls are 64-bit whatever realprecision says), merged with
boundary de-duplication, a count assertion against MV Thm 14.5 (|S| < 2) and a minimum-gap assertion; precision checked
at realprecision 57 on [0, 1000] and [19900, 20000] (narrowed from [19000, 20000] for cost). Proposal: record this recipe.

## A9. Layer B rulings as code (review M6)

§8's Layer B requirements become the functions in `rulings.py` (G0, G0-c, G2, G3, G4 confusable/incommensurate).
Interpretations fixed there: a cross-reading's "required FAIL" = T3 FAIL under A3; G4 confusable's "WEIGHT/SIGN
attribution" = the failed arms CONTAIN WEIGHT or SIGN (POSITION at 3, 5, 7 may also be listed, since those n are in R
with c = 0); "c = +log 2 each" = |c_n − log 2| ≤ B_n at every power of 2 ≤ 64. **Code: implemented.**

## A10. Pinned red-path definitions (review m1–m4, m10)

To be written into `seals/PH6_SEAL_6.0.json`: RP15 replacement = log(max(|u|, 2)/2) (ph6lib.psi_asymptotic); RP8 drops
{2ΣΛ(n)/n·g(2 log n), −(2/4π)∫hψ(1+ir)}; RP9 uses the whole class weight Σh⁺·idx·log ε₁ of the t²+4 discriminants in
place of t²−4; RP7 reads each sector's identity on the other sector's levels (h(i/2) added where the even identity has
it); RP12 multiplies the picket sum by e^{τ/2} (eigenvalues E_n − i/2); null construction constants (t_min = 7, upper
margin 1.02·E_hi + 50, central 80%, n_mat = ⌈n/0.8⌉ + 10, seeds 1000–1199 / 2000–2199, held-out 1100–1199 / 2100–2199).

## A11. Optional: RP3 at 1000δ (review m13)

RP3 (data shifted by 100δ) is reachable but only ~2× (structurally, independent of σ). 1000δ would make it a clear test
(~20×). Optional; the sealed 100δ works.

## Reachability summary (all from the RHS / positions only; no gate statistic)

| gate | red path | max ratio | status |
|---|---|---|---|
| G0 | RP1 drop k ≥ 2 | 2.4·10⁶ | REACHABLE |
| G0 | RP2 flip prime sign | 1.4·10⁷ | REACHABLE |
| G0 | RP3 data + 100δ (first-order estimate) | 2.1 | REACHABLE (modest) |
| G0-s (10,4) | RP13 Γ / RP14 pole / RP15 asym. ψ / RP16 mirror (upper bound) | 7.6·10⁷ / 1.5·10⁷ / 5.6·10⁵ / 2.2 | all REACHABLE |
| G0-s (40,3) | RP13 / RP14 / RP15 / RP16 | 5.6·10⁷ / 2·10⁻³¹ / 4.9·10² / 9·10⁻⁶⁴ | R / INAPPL. / R / INAPPL. |
| G0-s (150,10) | RP13 / RP14 / RP15 / RP16 | 7.4·10² / 2·10⁻⁴² / 3·10⁻⁴ / 4·10⁻⁵² | R / INAPPL. / INAPPL. / INAPPL. |
| G0-c | RP1 / RP2 / RP3 | 2.7·10⁶ / 1.5·10⁷ / 2.4 | REACHABLE |
| G1-even | RP5 / RP6 / RP8 / RP9 | 2·10⁻¹⁰ / 1.2·10⁶ / 1.4·10⁶ / 9.6·10⁵ | INAPPL. / R / R / R |
| G1-odd | RP5 / RP6 / RP9 | 1.5·10⁻¹⁰ / 9.4·10⁵ / 7.4·10⁵ | INAPPL. / R / R |
| G1 | RP7 swap parity | 2.4·10⁶ | REACHABLE |
| G2 | RP10, RP11 | pending (χ₋₄ zeros) | |
