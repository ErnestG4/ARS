# Phase 6 code review v1: ph6lib.py, preread.py, classes.py, chi4_zeros.py (plus gates.py where it consumes them)

Reviewer: independent agent, 2026-10-07. Read against `PH6_SEAL_6.0.md` (the authority), `PH6_DECISIONS_2026-10-07.md`,
EF §3/§4/§5/§7/§9, SB §1.3–§1.5/§2/§3/§5, XP §5. Code state: ph6lib.py at 324041f; preread.py, classes.py, chi4_zeros.py and
gates.py at 1f9d3f4. Pre-read outputs read: `results/preread/tables.log`, `results/dry_run_pilot.json`,
`PH6_PROPOSED_AMENDMENTS.md`, the 02:32 NOTES line.

No data file was opened by me: no Odlyzko zeros, no Maass CSV, no χ₋₄ zeros. No gate statistic was computed. The checks
under "Numerical checks" use the RHS only, printed EF §9 numbers, mpmath, or **synthetic** null spectra at a non-gate
configuration. The scripts are in the session scratchpad (`chk1.py`–`chk6.py`), outside the repo.

Severity: **BLOCKER** = a gate verdict would be wrong. **MAJOR** = wrong or not as sealed, but caught by the exact bar, a
red path or the pre-read, or wrong only in the conservative direction. **MINOR** = clarity, robustness, or an unsealed
choice that must be written down.

Counts: **2 BLOCKER, 7 MAJOR, 13 MINOR.**

---

## BLOCKER

### B1. `t3_verdict` returns NOT RESOLVABLE for every reading against χ₋₄ weights, the exact truth included
`ph6lib.py:356–359`; it propagates to `gates.py:110–111`, `gates.py:124` (RP17) and `preread.py:259–262` (design table).

- R excludes n with a_n = 0 (correct: §6.2 requires |a_n| ≥ 2B_n). Under χ₋₄, a_2 = a_4 = 0, so 2, 4 ∉ R.
- Then `not set(M) <= Rset and np.any(a != 0)` is always true, with M = {2,3,4,5,7}. The function returns
  "NOT RESOLVABLE" before it evaluates any arm.
- Checked directly: `t3_verdict(c=a_chi4, a=a_chi4, B=1e-3)` gives `('NOT RESOLVABLE', {R: [3, 5, 7, 9, …]})`.
  `t3_verdict(c=a_zeta, a=a_chi4, …)` also gives NOT RESOLVABLE.

Consequences for the sealed gates:
- **G2 Layer B** "vs χ weights: PASS, incl. SILENCE at 2…64 and SIGN at 3, 5, 7, 9" cannot be obtained.
- **G0 Layer B** "vs χ₋₄ weights: FAIL" comes out NOT RESOLVABLE.
- **RP17** (`gates.py:124`: FIRED iff `v_other[0] == "FAIL"`) reports DID_NOT_FIRE on the true ζ spectrum, so G0-c's red
  path is recorded as broken.
- `design()` writes `contains_M = False` for G2 whatever the band.

Why this is wrong: seal §6.3 introduces M for the T3 rule "applied to candidates in 6.1", which are read against ζ weights.
§6.2 itself counts G2's R over the 28 prime powers with χ ≠ 0 ("22/28 … 3, 5, 7, 9 all in R"), so the seal never
intended 2 and 4 to be required under χ₋₄. The code applies M to every weight vector.

Fix (needs a seal amendment or a line in the seal JSON):
- Define the minimum set per weight vector: M_w = M ∩ {n : a_n ≠ 0}, which is {3, 5, 7} for χ₋₄. Alternatively, apply the
  NOT RESOLVABLE rule only to ζ-weight (candidate) readings and report the arms directly for the χ₋₄ readings.
- State for G0 "vs χ₋₄: FAIL" and RP17 which outcome counts as the required failure. Under M_w, G0-c read against χ₋₄
  FAILs through SILENCE at 2, 4, 8, … (c_n = a_n^ζ ≠ 0 there) and through SIGN at 5, 13, …. That is the natural reading.

### B2. The seal's design numbers and its §7 null known answer omit the least-squares projection factor (Var c_n = √2 × the pointwise variance). G0-c's sealed |R| ∈ [22, 30] then fails, and G2 loses the log 9 sign arm
This is a seal arithmetic error, not a code bug. The code (`preread.py:227–247`, `predicted_s`) computes the right
quantity, but it departs from the sealed formula without saying so (see M1).

Derivation:
- The joint-LS coefficient of an isolated line, on the sealed 13-point local grid, is
  ĉ_n ≈ (∫ a* r dτ)/(∫|a|² dτ) with template a = e^{−σ²(τ−x)²/2}e^{i(τ−x)T₀}.
- The null r(τ) has covariance Var·e^{−σ²Δ²/4}e^{iΔT₀}, the transform of w².
- Hence Var ĉ = Var r(x) · ∬e^{−σ²[(s²+t²)/2+(s−t)²/4]} / (√π/σ)² = **√2 · Var r(x)**. The factor is independent of σ.
- The code's discrete version gives s_code/s_seal = 1.18904 at every n and every configuration (2^{1/4} = 1.18921).

Monte Carlo on synthetic nulls (E_hi = 6000, σ = 352.9, 100 GUE + 100 Poisson draws, seeds 91000+/92000+; no real data):

| null | mean\|c_n\|²/(code prediction), median [range] | mean\|c_n\|²/(seal §7 formula), median [range] |
|---|---|---|
| GUE | 0.993 [0.75, 1.23] | **1.446** [1.15, 1.94] |
| Poisson | 1.000 [0.79, 1.30] | **1.470** [1.16, 1.99] |

The overnight G0-c/G2 null runs agree: NOTES 02:32 reports GUE s/pred 0.90–1.15 against the code's prediction.

Resolvable sets: R = {prime powers : |a_n| ≥ 2B_n}, B_n = s_n√ln(8900). The seal's numbers are reproduced exactly by the
pointwise formula and change as follows with the correct one:

| configuration | seal design (pointwise) | with the LS factor | sealed requirement affected |
|---|---|---|---|
| G0 | 29/34, not {16, 27, 32, 64, 81} | **28/34**, also not 49 | none (G0 has no size bar) |
| G0-c (E_hi ≈ 25755) | 26/34 | **21/34**, also not 71, 73, 79, 83, 89 | **§8b: \|R\| ∈ [22, 30], so G0-c FAILs** |
| G2 | 22/28, "3, 5, 7, 9 all in R" | **14/28, 9 ∉ R** (also not 53, 59, 61, 67, 71, 73, 79) | **§8 G2 "SIGN at 9 (−)" cannot be scored. This was Will's stated reason for T = 2·10⁴ (decision Q1)** |
| 3·10⁴-level candidate | 26/34 | 21/34 | §12 Q2 and the ≥ 3·10⁴ minimum rest on 26/34 |
| 10⁴-level candidate | 10/34 | 7/34 | — |

M ⊆ R still holds at G0 and G0-c (2, 3, 4, 5, 7 stay in). The empirical bands decide the final sets (s/pred scatters
±10–15% per n), but the expected G0-c count is 21 ± 1.

Why BLOCKER: as sealed, G0-c would most likely FAIL its |R| bar. The cause is the design table's missing √2, not the
instrument. Per §8b that would force an amendment of the ≥ 3·10⁴ minimum for the wrong reason. Separately, G2's log 9 sign
arm, the reason G2 was set at 2·10⁴, would silently drop out of R.

Fix: report this to Will before the seal commit, as §8b/§9.5 intend.
- Amend §6.2's design values and §7's known-answer formula to include the factor √2, i.e. use P·Cov·Pᴴ as the code does.
- Re-derive the G0-c window [22, 30] (≈ [17, 25] around 21) or keep it and accept the consequence.
- Decide whether G2 needs a larger T or whether the log 9 arm becomes descriptive. From `predicted_s`, 2B₉/|a₉| is
  1.13 at T = 2·10⁴, 1.01 at 2.5·10⁴, 0.92 at 3·10⁴ (9 ∈ R, |R| = 23/28, but only 8% margin against band noise) and
  0.80 at 4·10⁴.

---

## MAJOR

### M1. The null known-answer test differs from seal §7 in three unsealed ways
`preread.py:210–218`.

1. **Different prediction.** The code uses the LS-propagated √(P Cov Pᴴ). §7 seals "Σw²·(log n/τ_H)/(σ/√2π)²" (GUE) and
   "Σw²/(σ/√2π)²" (Poisson), the pointwise variance. As B2 shows, the sealed formula fails by a factor 1.45.
2. **Looser criterion.** The code tests |s/pred − 1| ≤ 0.2 on s = √(mean|c|²). §7 says "mean |c_n|² … within 20%". 20% on s
   is [0.64, 1.44] on |c|². By the code's own criterion the overnight runs PASS (s/pred 0.90–1.15). On |c|² that range
   is 0.81–1.32, which would FAIL a 20% bar.
3. **Unachievable as written.** With 100 calibration draws, mean|c_n|² of a complex Gaussian has sd ≈ 10% per n. Requiring
   all 89 n within ±20% fails by sampling noise alone: in my MC, with the correct prediction, 94% of n fell inside, so
   ~5 n fall outside per run. The seal does not say whether the 20% applies per n, to the median, or pooled.

Fix by amendment: prediction = P·Cov·Pᴴ (as coded). Criterion = a per-n band from the Gamma(100, 1/100) law with
Bonferroni over 89 (≈ [0.67, 1.38] on |c|²), or the median over n within ±10%. Record which statistic (|c|² or s) is tested.

### M2. The ⟨r̃⟩ known answer is not implemented, and the sealed reference value 0.6027 is the wrong number for a large GUE
`preread.py:183–187` computes `rtilde` and reports `rtilde_mean`, but nothing compares it to a band.

- Seal §7: "unfolded GUE ⟨r̃⟩ within the arsrh Phase-1 tridiagonal band of 0.6027".
- 0.60266 is the Atas–Bohigas–Roux–Vivo 3×3 surmise value (`arsrh/phase1_zeta_crossover.py:36`). Large-N GUE is ≈ 0.5996.
- My checks: `gue_unfolded(5000)` gives 0.5997 ± 0.0005, raw tridiagonal centre 0.6003 ± 0.0012, dense 600×600 GUE centre
  0.5952 ± 0.0017. The overnight NOTES give 0.5998/0.5996.
- arsrh's "band" is a percentile band of matched-size tridiagonal draws (`phase1_zeta_crossover.py:98`), not a band around
  0.6027. A ±0.001 band about 0.6027 would reject a correct GUE null at G0 size, where the per-draw sd is ~0.0008.

Fix: write the reference (0.5996, or the matched-size tridiagonal 95% band computed with the arsrh recipe) and the
pass rule into the seal JSON, and implement the check in `nulls()`.

### M3. Two sealed red paths cannot fire at their gate's window: RP5 (G1) and RP11 (G2)
`preread.py:137` and `preread.py:165–166`.

- **RP5 (G1).** Already found by the pre-read (ratio ≈ 2·10⁻¹⁰) and addressed by proposed amendment A1. I concur.
  Mechanism: the elliptic kernels 1/cosh(πr) and cosh(πr/3)/cosh(πr) live at |r| ≲ 2, where w ≈ e^{−36}. The seal's
  claim (round 3) that "the exact bar will check the elliptic weights itself" is false at G1's window.
- **RP11 (G2), the same defect class, not yet flagged.** At σ = 1176.5 the Γ term is ∝ e^{−σ²τ²/2} < 10⁻³⁰⁰ for τ ≥ 0.5
  (seal §3, §6.1). So ψ(¼+iu/2) and ψ(¾+iu/2) give the same RHS to float noise. `R0["gamma"] − R["gamma"]` is pure
  roundoff (~10⁻¹¹ against ε ~ 10⁻⁸). The reachability will say INAPPLICABLE, so the Γ-parity (a) is never tested
  for χ₋₄. Only G0-s exercises the Γ code path, and only with a = 0.

Fix: add a G2-s (small-window χ₋₄ identity, e.g. (T₀, σ) = (10, 4), (12, 4), on the χ₋₄ zeros already computed from 0)
with RP11, RP13, RP15-analogue and RP10, parallel to A1.

### M4. ε_rhs is not what the seal declares, and the substitute is not an upper bound on what it claims
`preread.py:94, 133, 158`; `ph6lib.py:185–198`.

- Seal §5.1: ε_rhs = "mpmath quadrature error estimates (dps 30) + prime-sum tail + class-sum tail". The code evaluates the
  whole RHS in float64 numpy and adds an unsealed `1e-12·max(1, |RHS|)`.
- Measured against mpmath (40 digits) on the local grids of n = 2, 3, 29, 90: the float64 prime-sum error is 4.8·10⁻⁹ at
  G0 (relative 4.6·10⁻¹²), against an allowance of 1.1·10⁻⁹. At G2 it is 3.4·10⁻¹⁰ against 3.0·10⁻¹⁰. The dominant
  cause is ulp(log n)·T₀ in the line phase.
- Not verdict-changing at the sealed configurations: ε_data ≥ 1.4·10⁻⁵ at G0/G0-c, and at G2 ε_float ≈ 5·10⁻⁹–4·10⁻⁸
  covers it. But the term is mislabelled, and it is the only RHS-float allowance in the tolerance.

Fix: either evaluate the line phases with an extended-precision log n (mpmath, as the seal says) or replace the 1e-12 with a
derived bound such as 2⁻⁵¹·(T₀·max|log n| + 1)·Σ_n|line_n|. Record the choice in the JSON.

### M5. ε_float departs from the sealed formula and method
`ph6lib.py:457–465` (bound) and `ph6lib.py:79–96` (summation).

- **Seal:** Σ w(|τγ|+1)·2⁻⁵¹ plus a summation term, with compensated summation (`math.fsum`).
- **Code:** 2⁻⁵²·(τΣwE + Σw·(log₂n + 4)), with the LHS summed by a BLAS complex matmul (`@`), not fsum.
- The phase part is therefore **half** the sealed value. For BLAS accumulation, the log₂n summation factor is not a proven
  bound; the worst case is ~(n/k)·u with k accumulator lanes.
- At G2, ε_float is likely the dominant term (δ_χ from p38 vs p57 is presumably ≲ 10⁻²⁵), so the code's G2 bar is ~2×
  tighter than the sealed one. The risk is a false FAIL, not a false PASS.
- The 2⁻⁵² bound covers the float64 rounding of the zero and the τ·γ product with no slack; only the ×2 safety factor
  remains.

Fix: use 2⁻⁵¹ as sealed, plus either fsum (as sealed) or an n·u summation bound for BLAS. Or amend the seal to the coded
form.

### M6. The composite Layer B gate criteria have no verdict logic
`gates.py:107–127`, `202–229`. Not one of the four files under review, but it is where `t3_verdict` is consumed, and it
will be hashed.

- **G0.** "vs ζ PASS **and** vs χ₋₄ FAIL" are recorded (`verdict_own`, `verdict_other`) but never combined into a gate
  PASS/FAIL.
- **G2.** The specific requirements (SILENCE at 2, 4, 8, 16, 32, 64; SIGN at 3+, 5−, 7+, 9−; vs ζ FAIL) are not checked.
- **G4 confusable.** The code records `position_fires_at`, `silent_at_3_5_7` and `vs_zeta`, but no verdict. Seal §8 says
  "T3 vs ζ = FAIL with WEIGHT/SIGN attribution". `t3_verdict` will also list POSITION at 3, 5, 7, 9, … (c = 0 there, n ∈ R),
  so it must be specified whether the attribution must *equal* or *contain* {WEIGHT, SIGN}. "c = +log 2 each" has no
  tolerance.
- **G4 incommensurate.** "silent at all n ≤ 90" (vs_zero) and "T3 vs ζ = FAIL (POSITION absent)" are not turned into a
  verdict either.

Fix: write each gate's Layer B pass rule as code (a rulings module) and pin it in the JSON before the run.

### M7. Reachability lookups fail open
`gates.py:80, 142, 149`: `reach.get(key, {}).get("status", "REACHABLE")`.

- A missing or mis-keyed reachability entry is treated as REACHABLE. A red path that cannot fire then reports DID_NOT_FIRE,
  which reads as a broken red path. It should be INAPPLICABLE, or the run should halt.
- This already happened in the dry run: RP14 and RP16 reported DID_NOT_FIRE at the pilot (60, 6) because `reach = {}`.
- At the sealed run the risk is G2's RP10/RP11 keys if `tables` ran without the χ₋₄ file.
- RP4, RP12 and RP17 have no reachability entries at all (preread computes none; see m9).

Fix: raise on a missing key, and compute (or explicitly declare by construction) reachability for RP4, RP12 and RP17.

---

## MINOR

- **m1. RP15 is singular at u = 0 at G0-s (10, 4).** `preread.py:113–116`, `gates.py:90–94`. "Replace Re ψ(¼+iu/2) by log(u/2)":
  the code uses log(|u|/2) on a 0.05 grid that passes within 2·10⁻¹² of u = 0, and w(0) = 0.044 there. The removed term's
  size depends on the grid: |Δ| at τ = 0.5 is 0.0032 (step 0.05) vs 0.0108 (step 0.05 shifted by ½ step) vs 0.0093
  (step 0.01). Preread and gates use the same grid, so they are mutually consistent, and the path is reachable (5.6·10⁵).
  But the red path's definition is unsealed. Pin it, e.g. log(|u|/2) with an endpoint-aware rule or the u-grid itself.
- **m2. RP8's term set is unsealed.** `preread.py:140`, `gates.py:151–153`. "Drop the scattering terms" is implemented as
  {2ΣΛ(n)/n·g(2 log n), −(2/4π)∫hψ(1+ir)}. Other readings exist: the φ′/φ form, (1/4π)∫hφ′/φ + h(0)/2; or the full even-only
  difference including the g(0) parity constant (log(π⁴/2)/4 vs −log 8/4, ≈ 0.07 at τ = 0.5). All are reachable. Pin one.
- **m3. RP9 swaps the whole weight Σh⁺·idx·log ε₁ of the t²+4 field.** `preread.py:143`, `gates.py:154`. The seal says
  "class counts". Pin it.
- **m4. RP7 and RP12 constructions.** RP7 (`gates.py:148`): the swapped "even" LHS lacks h(i/2) (4·10⁻¹⁶; harmless).
  RP12 (`gates.py:214`) is implemented as e^{τ/2}·LHS. Pin both in the JSON.
- **m5. G0-s grid and data scope.** `preread.py:92`. G0-s uses only the 0.001-step grid. Seal §4 defines the identity grid
  as that grid plus the local grids of every line centre. Harmless at σ ≤ 10, but not as sealed. Also unsealed: whether
  the G0-s LHS is truncated at T₀ + 8.5σ. ε_trunc assumes it is; the code passes all 10⁵ zeros. Both choices are harmless.
- **m6. Prime-sum cutoffs differ from the seal.** `ph6lib.py:164–165, 181`. The cutoff is "13 widths" (n_max = 100 at G0,
  2321 at σ = 4), not the sealed "n ≤ 10⁴". The bound beyond n_tail is the heuristic `norm·e^{−312.5}·10`; the true tail is
  ~10⁻¹³⁰, so this is harmless. The Selberg ε has no class-sum (t > 30) or prime-sum (n > 10⁴) tail term, although §5.1
  lists both. Both are < 10⁻⁴⁰ (g at u ≥ 6.87 vs τ ≤ 4.5: e^{−σ²·2.37²/2}). Add them or amend.
- **m7. δ_χ ignores float64 rounding of the PARI zeros.** `preread.py:155`, `gates.py:241`. The zeros are read as `float(x)`,
  a representation error up to 1.8·10⁻¹² at γ ≈ 2·10⁴, which is ≫ δ_χ. This is covered only because ε_float's 2⁻⁵²·τ·E
  term bounds it (exactly). State δ_eff = max(δ_χ, 2⁻⁵³E_hi) in ε_data.
- **m8. chi4_zeros fail-open and recipe drift.** `chi4_zeros.py:58–81`. The count check vs MV 14.5 (seal §9.1 "within
  |S| < 2") is printed, not asserted. Deduplication at 10⁻²⁰ is not followed by a min-gap assertion, so a missed duplicate
  would double a zero. Seal §1 names one call, `lfunzeros(lfuncreate(-4), 20000)`, while the code makes 20 interval calls
  [a, b]. Record that in the JSON; assert counts and min-gap.
- **m9. The pre-read omits steps the seal lists.** `preread.py` has no G4 tolerances (§9.3 lists G4) and no reachability
  for RP4, RP12, RP17 (§8a says "every red path").
- **m10. Null construction free choices.** `ph6lib.py:408–438`: t_min = 7; upper margin 1.02·E_hi + 50; the first null
  level is pinned exactly at t_min; n_mat = ⌈n/0.8⌉ + 10; the clip in the semicircle CDF. All are harmless (w(7) ≤ e⁻³⁶),
  but they are unsealed. List them in the JSON.
- **m11. gamma_term's halving estimate is not an upper bound when the true value is ~0.** `ph6lib.py:155–157`. At G0 the
  value (pure roundoff) is 2.1·10⁻¹⁰ and the estimate 1.6·10⁻¹⁰. This is negligible against ε ≥ 10⁻⁵, but the label
  "error estimate" overstates it.
- **m12. Two wording issues.** §7's τ_H = log(T₀/2π) should be log(qT₀/2π) for χ₋₄. (The code's GUE prediction avoids τ_H,
  because the density cancels, which is correct.) And RP16's REACHABLE status rests on an upper bound only; A2 already
  says so.
- **m13. RP3 is structurally marginal.** The first-order ratio is ≈ 25·(Λ(n)/√n)/(2πρ̄), independent of σ: 2.1 at G0 and
  2.4 at G0-c. This is because ε_data is a worst-case sum over the whole window mass. It is correct as computed, but a
  shift of 1000δ would make RP3 a clear test.

---

## preread.py computes no gate statistic: line-by-line check

- `tables`: zeros are used only in
  - `eps_data_zero` (Σw, Σ|w′| over ±γ: non-oscillatory),
  - `eps_float_zero` (Σw·E, Σw),
  - `z[29999]` and `z[-1]` (configuration rule),
  - RP16 Σw(−γ) (non-oscillatory).
- Maass levels are used only in `wsum`, `wp` and Σw·r (`preread.py:128–131`). χ₋₄ zeros are used only in ε_data/ε_float.
- Every RHS, reachability and design quantity is a function of cfg, Λ, χ, class numbers and integrals. **No S(τ), C(τ) or
  c_n is formed from ζ, χ₋₄ or Maass data.**
- `nulls`/`_one_draw` use only synthetic levels; `design` uses only bands.
- Closest approaches, all legitimate:
  - RP3's estimate uses |RHS|, not the LHS.
  - RP16 uses the upper bound instead of the true |M(τ)|.
  - E_hi = γ_N reads one position.

gates.py's `main_dry` reads only the disclosed pilot's 50 zeros ≤ 144 at (60, 6) (EF §9, seal §11), plus synthetic spectra.

## Checked and found correct

- **`rhs_dirichlet` against the EF §7 box.**
  - Pole h(±i/2) = w(±i/2)e^{∓τ/2}, for q = 1 only.
  - Conductor g_τ(0)·log(q/π).
  - Γ term (1/2π)∫w e^{iτu} Re ψ(¼ + a/2 + iu/2).
  - Prime lines with both g_τ(+log n) and g_τ(−log n) and a minus sign.
  - g_τ(u) = (σ/√2π)e^{−σ²(u−τ)²/2}e^{−i(u−τ)T₀}.
  - Reproduces the printed EF §9 RHS at (60, 6) to ≤ 5.9·10⁻¹⁴ (ζ) and ≤ 1.3·10⁻¹⁴ (χ₋₄) at τ = 0.5, log 2, log 3, 4.5.
  - `gamma_term` at (10, 4) agrees with mpmath to 1.2·10⁻¹⁶.
- **`g_maass`.** It equals (1/2π)∫[w(r)+w(−r)]cos(τr)e^{−iru}dr: direct mpmath quadrature agrees to ≤ 4·10⁻¹⁶ on O(1)
  values. h(i/2) = [w(i/2)+w(−i/2)]cosh(τ/2) is real, matches mpmath, and is added on the even LHS only.
- **`rhs_selberg` against SB §1.4 and BS07 (2.39) at N = 1, term by term.**
  - Identity 1/24 per sector.
  - (E2+E3)/2, with E2 = (1/8)∫h/cosh and E3 = (1/(3√3))∫h cosh(πr/3)/cosh. The prefactors were re-derived from (2.40):
    |r¹| = 4, 6; arccos 0, ½; symmetrisation.
  - +H/2; ±R/2 (+ even, − odd).
  - g(0)·log(π⁴/2)/4 (even) and −g(0)·log 8/4 (odd), re-derived from C_{χ,ε} = 2/0.
  - −(1/4π)∫h[ψ(½+ir) + 2ψ(1+ir)] even and −(1/4π)∫hψ(½+ir) odd. Real parts suffice since h is even.
  - 2ΣΛ(n)/n·g(2 log n) on even only ({χ}₀ = 2, {χ}₁ = 0).
  - All integrals are full-line trapezoid (2× the half-line) with strip half-width ½. Aliasing is e^{−π/0.01}.
- **Class weights.** `lsum_h/2 = Σ_f h⁺(df²)·[r¹:r_f¹]·log ε₁` and `lsum_g = Σ_f h⁺·[r¹:r_f¹]·log ε₁` are exactly the W(D)
  coefficient of SB §1.4 / BS07 (2.40). So `hyp` = Σ_{t≥3}W(t²−4) = H/2 and `gl` = Σ_{t≥1}W(t²+4) = R/2. The hyperbolic
  factor 2 (BS07 Lemma 2.10) and the glide factor 1 (N(T₀) = ε₁ at t = 1) are consistent with G1-pre's CF cross-check.
  h⁺ = qfbclassno·(2 if N(ε) = +1) is cross-checked against the Gauss cycle counts by G1-pre. The CF enumeration's pruning
  is sound: (NQ)₀₀ ≥ N₀₀.
- **Readout.** The template phase e^{i(τ−log n)T₀} matches g_τ(log n)/norm, so c_n = a_n = −χ(n)Λ(n)/√n on true zeros. The
  dry-run picket gives c = +log 2 with imaginary part 10⁻¹⁴. The a_n signs: χ₋₄ 3 (+), 5 (−), 7 (+), 9 (−).
- **Band and arms.** B_n = s_n√ln(89/α) (len(ns) = 89, α = 0.01). R = prime powers with |a_n| ≥ 2B_n. The four arms are as
  in §6.2. SILENCE covers non-prime-powers and every n with a_n = 0.
- **GUE null.** The Dumitriu–Edelman normalisation is identical to arsrh (diag √2·N(0,1), off-diag √χ²_{2(n−k)}).
  - The semicircle radius √(8n) is correct for it: second moment/(2n) = 1.0002 and max|λ|/√(8n) = 1.0008 at n = 4000.
  - The unfolding CDF ½ + (x√(1−x²) + arcsin x)/π is correct. The central 80% is taken.
  - The N̄⁻¹ map has N̄ monotone on t ≥ 7 for both targets.
- **`nbar_zeta`, `nbar_chi`.** They agree with mpmath θ/π + 1 and with MV 14.5's (1/π)arg Γ(¾+iT/2) + (T/2π)log(4/π) to
  ≤ 4·10⁻¹⁵, continuous branch included. The count at 143.63 (80.49) matches EF §5.
- **GUE pointwise variance.** (τ/2π)σ√π with the density cancelling (ρ̄·σ√π·τ/(2πρ̄)) is right for τ < τ_H at every
  configuration, and the MC confirms it: median ratio 0.993 to the code's propagated prediction. Only the seal's omission of
  the LS factor (B2) is wrong.
- **Tolerance pieces.**
  - ε_data includes the mirror zeros' contribution, with the correct |w′(−γ)|.
  - ε_trunc = 2ρ·σ√(π/2)·erfc(8.5/√2) is the correct ∫_{E_hi}^∞ w, ≈ 6·10⁻¹³ at G0.
  - The G1 Maass density E_hi/6 + 1 is conservative per sector.
  - δ = 3·10⁻⁹ (ζ) and 5·10⁻⁹ (Maass) are as sealed.
- **Picket.** The Poisson-summation RHS (λ/2π)Σ_k e^{ikθ}σ√(2π)e^{−σ²ν²/2}e^{iνT₀} was re-derived. The two-sided picket sum
  over span 40σ is correct.
- **Red-path reachability terms that match §8.** RP1 (non-prime prime powers), RP2 (2P), RP5 (+elliptic), RP6 (±R/2),
  RP7 (RHS_even − RHS_odd), RP10 (prime sum χ ≡ 1 − χ₋₄), RP13 (Γ), RP14 (pole), RP16 (upper bound).
