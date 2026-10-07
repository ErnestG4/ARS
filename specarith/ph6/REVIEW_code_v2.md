# Phase 6 code review v2: verification of the REVIEW_code_v1 fixes (3992fd2, fe55747)

Reviewer: independent agent (second pass), 2026-10-07. Read against `PH6_SEAL_6.0.md` (the authority),
`REVIEW_code_v1.md` and `PH6_PROPOSED_AMENDMENTS.md` (A1–A11). Code: `ph6lib.py`, `preread.py`, `gates.py`, `rulings.py`,
`chi4_zeros.py`, `classes.py` at fe55747, plus the `git show 3992fd2` diff. Pre-read outputs read: `preread_out_v2/`
(tables, `rhs_*.npz` tolerance arrays) and `results/preread/` (bands, design table, known answers).

What I did not touch: no Odlyzko zeros, no Maass CSV, no χ₋₄ zero file. No gate statistic was computed, and I did not
run `gates.py run` or `preread.py tables`. The checks below are of four kinds:
- RHS-only float64 vs mpmath comparisons at 40 digits (30 digits for G1);
- PARI number theory, for the class-sum tail;
- unit tests of `rulings.py` and `t3_verdict` on constructed theorem readouts (c = a_n, or the ideal picket c = log 2 at
  2^k) with the pre-read bands;
- reading the pre-read tolerance arrays.

Scripts are in the session scratchpad (`v2_chk_dir.py`, `v2_chk_selberg.py`, `v2_chk_tail.py`, `v2_chk_rulings.py`),
outside the repo.

Severity uses the v1 scale:
- **BLOCKER**: a gate verdict would be wrong.
- **MAJOR**: wrong or not as sealed, but caught elsewhere or only conservative.
- **MINOR**: clarity, robustness, or an unsealed choice.

**Summary: 0 new BLOCKER, 1 new MAJOR, 12 new MINOR.**
- All v1 code-vs-seal items are fixed or moved to an amendment for Will.
- The derived float bounds are genuine upper bounds at every point I tested, with a margin of at least 250×.
- They do not swamp the bar, except at G2. There the Γ-term rounding bound is 52–82% of ε. That is conservative and
  changes no red path.
- Every reachability key that gates.py evaluates is declared by preread.py with an identical string.
- The new MAJOR, N1, is a sign error: the tolerance uses a signed τ, and the local grid that m5 added at G0-s reaches
  τ < 0. At G0-s (40, 3) this makes ε **negative** at two grid points. Those points pass unconditionally, and no red
  path can fire there.

---

## 1. Status of the first-review items

| item | status | verification / residual |
|---|---|---|
| **B1** M applied to every weight vector | **FIXED (PROPOSED A3, pending Will)** | `t3_verdict` sets M_w = M ∩ supp(a) (`ph6lib.py:426`). The NOT RESOLVABLE short-circuit runs only when M_w ⊄ R. Under ζ weights M_w = M, so behaviour is unchanged. Under zero weights M_w = ∅ and the short-circuit was already skipped, so that is unchanged too. Tested on constructed readouts with the pre-read bands: χ₋₄ truth vs χ₋₄ → PASS; ζ truth vs χ₋₄ → FAIL; G0 and G0-c truth vs ζ → PASS; G2 truth → PASS; the swapped truths → FAIL. `design()` uses the same M_w. See N6 for a fragile margin in the G2 cross-read. |
| **B2** missing √2 in the design numbers and §7 | **NOT FIXED: legitimate (seal arithmetic, A4/A5 for Will)** | The empirical bands give G0 29/34, G0-c 24/34 (inside [22, 30]) and G2 15/28 with 9 ∉ R (`results/preread/design_table.json`). `rulings.g2_layer_b` already implements A4 option (a) (9 reported NOT RESOLVABLE, not scored); see N5. |
| **M1** null known answer | **FIXED as a report; the criterion is A5 for Will** | `known_answers` "literal" is the sealed §7 formula: Σw² = ∫ρ̄w² with the target's density, × log n/τ_H with the literal τ_H = log(T₀/2π), / norm², and every n within 20% on mean\|c\|². The `min(·, 1)` cap is inactive, because log 90 < τ_H at every configuration. "LS" divides by `d["pred"]²`, and `pred` is exactly `predicted_s` saved by `nulls()`. Results: literal FAIL at G0, G0-c and G2 (median 1.36–1.41); LS median 0.96–1.00. Residual: `nulls()` still writes the old `known_answer_20pct` verdict, tested on s (N7). |
| **M2** ⟨r̃⟩ check | **FIXED-WITH-DEFECT (minor)** | It is now implemented against arsrh PHASE1_FINDINGS W = 10,000 [0.5952, 0.6065], and passes (0.5998–0.5999). That band is a single-draw 95% band for 10⁴-level windows. The code compares a mean over 100 draws of ~10⁵ levels each (SE ~10⁻⁴) to it, so the test only catches gross errors (N8). |
| **M3** RP5 and RP11 cannot fire | **NOT FIXED: legitimate (A1/A6 for Will)** | The v2 pre-read confirms RP5 INAPPLICABLE (1.9e-10 / 1.5e-10). RP11 is not yet computed (N9). |
| **M4** ε_rhs | **FIXED (wording is A7)** | The derived bounds hold everywhere I tested (§2). Minor gaps: N2, N3, N10. |
| **M5** ε_float and summation | **FIXED-WITH-DEFECT** | fsum is on the gate paths: `zero_sums(exact=True)` S and M, `maass_sector_sum`, and the picket LHS (`gates.py:236–237`). The ε_float formula matches §5.1 (2⁻⁵¹ w(\|τE\|+1), mirror weights added, which is conservative; fsum term 2·2⁻⁵³Σw). Defect: the code uses τ, not \|τ\| (N1). |
| **M6** Layer B rulings | **FIXED (PROPOSED A9/A10)** | `rulings.py` is wired into G0, G0-c, G2, G3/G3-c and G4. All rulings behave correctly on constructed inputs. Three divergences from the sealed text are listed in N5. |
| **M7** reachability fails open | **FIXED, apart from RP17/RP4** | `Reach.status` raises on a missing key. The key strings match exactly (list in §3). RP17 never goes through `Reach`, and RP4's status is fetched but ignored (N4). G2's keys exist only when `tables` runs with the χ₋₄ file, and `preread_out_v2` lacks them (N9). |
| m1 RP15 at u = 0 | **FIXED** | `psi_asymptotic` = log(max(\|u\|, 2)/2). It is the same function on the same u-grid (`arange(T₀−13σ, T₀+13σ, 0.025)`) in `preread.py:113–114`, `gates.py:102–103` and the dry run. Pinning it in the JSON is A10. |
| m2 RP8 term set | **NOT FIXED in code: legitimate (pinned in A10 text)** | preread (removed term) and gates (RHS − prime + 2ψ₁/4π) are consistent. |
| m3 RP9 | **NOT FIXED: legitimate (A10 text)** | preread and gates are consistent. |
| m4 RP7 h(i/2), RP12 | **FIXED / A10 text** | The swapped even LHS now includes h(i/2). The RP7 reach still uses RHS_even − RHS_odd (without the 10⁻¹⁶ h(i/2)) and ε_even for both sectors. That is harmless (ratio 2.4·10⁶). |
| m5 G0-s grid | **FIXED, but it introduced N1** | — |
| m6 cutoffs and tails | **FIXED-WITH-DEFECT (minor)** | Prime sum to 10⁴, with a dyadic tail. The Selberg tail's justification is invalid for non-maximal orders, although the inequality holds numerically. Both tails stop at a finite t and n with no remainder term. See N3 and N10. |
| m7 δ_eff | **FIXED** | `eps_data_zero` and G1 use δ + 2⁻⁵³·max E. |
| m8 chi4 merge | **FIXED (recipe text is A8)** | `merge()` asserts \|N − N̄(20000)\| < 2 (N̄ = MV 14.5 smooth part, which I checked: N̄(γ₁ = 6.0209) = 0.455) and min gap > 10⁻⁸. Caveat in N11. |
| m9 pre-read omissions | **MOSTLY FIXED** | G4 tolerances, RP12 reach and RP4 (by construction) are present. The RP17 "reach ratio" is written to `design_table.json` but not consumed (N4). The G4 tolerance code is never exercised in the dry run (N12). |
| m10 null constants | **NOT FIXED: legitimate (A10 text)** | — |
| m11 gamma_term estimate | **FIXED** | `fb` was added. At G0 the float Γ value is 1.4e-14 against a bound of 1.0e-6. |
| m12 τ_H / RP16 wording | **N/A for code** | `known_answers` uses the literal τ_H and labels it. The wording is for Will. |
| m13 RP3 marginal | **NOT FIXED: optional (A11)** | v2 ratios 2.06 (G0) and 2.39 (G0-c). |

---

## 2. Derived float bounds vs mpmath (RHS only)

| config | τ points (incl. local grid, negative τ at G0-s) | max \|float − mp\| | `err` bound | max diff/err | ε at those τ | err/ε |
|---|---|---|---|---|---|---|
| G0 | 9 | 4.7e-9 (at log 29) | 1.0e-6 – 2.2e-6 | 2.4e-3 | 4.8e-5 – 4.2e-4 | ≤ 2% (low τ ≤ 5%) |
| G0-c | 9 | 5.9e-10 | 1.1e-7 – 2.3e-7 | 2.8e-3 | 1.4e-5 – 1.3e-4 | ≤ 1% |
| G0-s (10, 4) | 9 | 3.7e-15 | 1.2e-12 – 6.0e-12 | 6.9e-4 | 8.0e-10 – 2.0e-8 | ≤ 0.2% |
| G0-s (40, 3) | 9 | 2.3e-14 | 1.3e-12 – 9.4e-12 | 3.9e-3 | **−8.1e-10** – 8.0e-8 | — (N1) |
| G2 | 9 | 3.3e-10 | 6.3e-8 – 1.3e-7 | 2.7e-3 | ≈1.5e-7 – 5.2e-7 (density estimate, no zeros) | **52–82%** (N2) |
| G1 even | 5 | 9.0e-14 | 1.6e-10 | 5.4e-4 | 2.4e-7 – 1.7e-6 | < 0.1% |
| G1 odd | 5 | 4.2e-14 | 1.3e-10 | 3.2e-4 | 3.1e-7 – 2.2e-6 | < 0.1% |

All bounds are genuine upper bounds at the tested points, with a margin of at least 250×. The mpmath RHS used the same
float T₀ and σ, the exact log n, the Γ integral by `mp.quad` at G0-s, the class weights from `classes.pari_counts`, and
the Selberg integrals by `mp.quad`.

**selberg_tail_bound.** The quantity being bounded is C(t)·log ε₁ = Σ_{f|ℓ} h⁺(df²)·[r¹:r_f¹]·log ε₁.
- This equals Σ_{f|ℓ} 2h(df²)R(df²) = √d·Σ_{f|ℓ} f·L(1, χ_{df²}). I checked the first equality against
  `classes.pari_counts` at every t ≤ 30, both kinds.
- The docstring derives "≤ √D(log D + 1)" from "h log ε = √D L(1,χ), L ≤ log D + 1". For ℓ > 1 that derivation is
  invalid: the divisor sum makes the ratio to √D·L(1,χ_d) as large as Σ_{f|ℓ} ψ(f)/ℓ, which is 2 at ℓ = 2, 3.3 at ℓ = 6
  and 4.2 at ℓ = 12.
- The inequality itself holds numerically: PARI, t ≤ 1500, max ratio 0.26 (hyperbolic, t = 610, ℓ = 12) and 0.34
  (glide, t = 840). The code also applies an extra ×2, mislabelled "hyperbolic and glide both bounded" (the loop already
  covers both kinds), so the effective margin is ≥ 6×.
- A provable replacement: for any non-principal χ mod k, |L(1,χ)| ≤ log k + 2. Hence C(t) log ε₁ ≤ √D·(σ(L_t)/L_t)·(log D + 2),
  with L_t the largest integer such that L_t² | D (ℓ | L_t).
- Practically irrelevant: the tail is ~10⁻⁴¹ at G1.

---

## 3. Fail-closed reachability: key strings

Keys that `gates.py` evaluates, with the declaring line in `preread.py`. **No mismatch.**

| gate | key | declared at |
|---|---|---|
| G0, G0c | `{G0,G0c}:RP1_drop_k>=2`, `:RP2_flip_prime_sign`, `:RP3_shift_100delta` | `preread.py:105–108` |
| G0 | `G0:RP4_plant_log6` | `:186` (looked up at `gates.py:136`, result ignored) |
| G0s_a/b/c | `:RP13_drop_gamma`, `:RP14_drop_pole`, `:RP15_asymptotic_psi`, `:RP16_drop_mirror(upper bound)` | `:110–119` |
| G1 | `G1_even:` / `G1_odd:` `RP5_elliptic_x2`, `RP6_drop_R`, `RP9_wrong_discriminant`; `G1_even:RP8_drop_scattering`; `G1:RP7_swap_parity` | `:139–149` |
| G2 | `G2:RP10_chi_equiv_1`, `G2:RP11_wrong_parity_a0` | `:166–168` (**only if CHI4_ZEROS is given**) |
| G4 | `G4_confusable:RP12_brief_v1_bc`, `G4_incommensurate:RP12_brief_v1_bc` | `:184` |
| G0c | RP17 | **not routed through Reach** (N4) |

`preread_out_v2/preread_tables.json` contains every key above except G2's. A sealed run against it stops with
FileNotFoundError on `rhs_G2.npz`, or with the KeyError (fail closed, as intended).

`preread.py` computes no gate statistic. It uses zero and Maass positions only in non-oscillatory sums (ε_data, ε_float,
Σw(−γ)) and in z[29999] / z[−1]. Its nulls are synthetic. `known` and `design` read only band and null files.

---

## 4. NEW findings

### MAJOR

**N1. The tolerance uses a signed τ. On the G0-s local grids τ < 0, so ε goes negative (fail-open).**
Locations: `ph6lib.py:523` (`eps_data_zero`: `taus * ws.sum()`), `ph6lib.py:534` (`eps_float_zero`: `taus * (ws*E).sum()`),
`ph6lib.py:207–210` (`prime_sum_dirichlet` fbound: `(ln + tc)`, and the amplitude of the +log n line only),
`gates.py:63–75` (no positivity check).

What happens:
- Since m5, G0-s uses the §4 local grids: τ = log n + (j/2)/σ, j = −6…6. At σ = 3, log 2 − 1 = −0.307. At σ = 4,
  log 2 − 0.75 = −0.057.
- `preread_out_v2/rhs_G0s_b.npz` gives **ε = −8.06·10⁻¹⁰ at τ = −0.3069**, from ε_data = −4.0e-10 and ε_float = −1.1e-14.
  ε_float is also negative at τ = −0.140.
- At G0-s (10, 4), τ = −0.057: ε = 8.0e-10. With \|τ\| it would be ≈ 1.2e-9 at the same point.

Consequences:
- Where ε < 0, `|LHS − RHS|/ε < 0`. That grid point passes Layer A unconditionally, and no red path can fire there.
- Where 0 < τ is small, or τ < 0 with ε still positive, ε is under-estimated. This is a small false-FAIL risk.
- §5.1's own text writes ε_data with "τ·w(γ_k)" (signed), so the code follows the letter of the seal. The seal's ε_float
  writes |τγ_k|. Evidently the seal assumed τ ≥ 0.5.
- Not a BLOCKER: only 2 of 5,158 points at G0-s (40, 3) are blind, and the identity is tested at all the others.

Fix:
- Use `np.abs(taus)` in `eps_data_zero` and `eps_float_zero`, and in the inline G1/G4 formulas for uniformity.
- In the prime fbound, use `(ln + |τ|)` and add the |g(−log n)| amplitude. That line dominates at τ < 0.
- Assert `np.all(eps > 0)` in `preread.save` and in `gates.layer_a` and `red_path`.
- Wording for Will (with A7): §5.1 should read |τ|. §4 should state whether local-grid points with τ < 0.5 belong to
  G0-s's identity grid. They do by the letter of §4, and the identity holds there.

### MINOR

**N2. At G2 the Γ-term rounding bound dominates ε.**
Location: `ph6lib.py:177–179`.
- At σ = 1176.5 the true Γ term is ≈ 0. The float value is ≤ 6·10⁻¹⁴. Its "bound" is 6.3e-8 – 1.3e-7, which is 52–82% of
  ε (density estimate of ε_data + ε_float, no zeros read).
- Two terms drive it: N·2⁻⁵³·Σ\|f\| over ~1.2·10⁵ trapezoid nodes, and 4u·\|τu\| with \|u\| up to 2.5·10⁴.
- This is conservative and changes no red path (RP10 is huge, RP11 is INAPPLICABLE regardless). It makes G2's Layer A bar
  ~2–5× looser than data + float alone.
- Elsewhere the effect is small: G0 ≤ 5%, G0-c ≤ 1%.

Fix: for σ ≥ 100, bound the Γ term analytically (|Γ term| ≤ (σ/√2π)e^{−σ²τ²/2}·max|ψ| plus a w(0)-scale edge term)
instead of integrating roundoff. Or tighten the per-term factor 4u to 2u and use a pairwise-summation bound.

**N3. `selberg_tail_bound` (`ph6lib.py:273–287`).**
- The justification is invalid for non-maximal orders (§2). The inequality holds numerically.
- The ×2 is mislabelled.
- The sums stop at t < 5000 and n ≤ 2·10⁵, with no remainder bound. The omitted part is ≲ e^{−2600} at G1.

Fix: use the provable per-t factor (σ(L_t)/L_t)(log D + 2) without the extra ×2. Add a one-line analytic remainder, or
assert that g underflows at t = 5000.

**N4. RP17 is not routed through `Reach` (`gates.py:139–141`), and RP4's status is ignored (`gates.py:136`).**
- `design()` writes `RP17_reach_ratio` = max|a_ζ − a_χ|/B = 10.46. Nothing reads it.

Fix: write a `G0c:RP17_read_vs_chi4` reachability entry in preread (from the band, as `design()` computes it). Look it up
through `Reach`, and make RP4 honour an INAPPLICABLE status like every other red path.

**N5. Rulings vs seal §8: three undeclared divergences.** None makes a gate PASS where the seal says FAIL, given the
sealed bands.
- (a) `g0c_layer_b` (`rulings.py:32–41`) calls `g0_layer_b`, so G0-c's Layer B also requires "vs χ₋₄ FAIL". In the seal
  that is RP17, a red path, not part of Layer B. A non-firing RP17 would therefore be reported twice.
- (b) `null_gate` for G3-c (`gates.py:205`, `216`) has two departures from the seal:
  - It counts NOT RESOLVABLE as a rejection. The seal's G3-c row says "T3 = FAIL in 100%". This has no effect while
    M ⊆ R at G0-c's band, which is deterministic (margins ≥ 1.26).
  - It also requires the Poisson family to pass. The seal's G3-c row names only held-out GUE. The code is stricter
    than sealed.
- (c) `g2_layer_b` (`rulings.py:54–61`) scores a named sign arm only when n ∈ R. This silently implements A4 option (a)
  (9 is not scored) before Will has chosen. A9's list of fixed interpretations does not mention it.

Fix: list (a)–(c) in A9, or align the code with the sealed text. Mark (c) "PROPOSED A4(a)" in code.

**N6. G2's required "vs ζ FAIL" rests on a 1.4% margin.**
- At the G2 band, |a₄|/2B₄ = **1.014**. If 4 dropped out of R_ζ, the cross-read would be NOT RESOLVABLE, and
  `g2_layer_b` would FAIL G2.
- With the sealed seeds the band is fixed, so the sealed run is safe. It is not robust to any band change, for example
  A4(b) at T = 4·10⁴, or any change to the null construction.

Fix: `design()` should also report each cross-reading's M_w ⊆ R with margins: G0 vs χ₋₄, G0-c vs χ₋₄, G2 vs ζ. A3 should
state whether a cross-reading that is NOT RESOLVABLE satisfies "required FAIL".

**N7. `preread.nulls` (`preread.py:211–245`) has two problems.**
- There is no guard `n_gue, n_poi ≤ 100`. With 200 draws, the held-out seeds 1100–1199 and 2100–2199 would enter the
  calibration band.
- It still emits `known_answer_20pct` on s with ±20%. That is the old unsealed criterion, and it reads "PASS".

Fix: assert ≤ 100, and drop or rename the field (the verdicts live in `known`).

**N8. The ⟨r̃⟩ check (`preread.py:271`, `305`) compares the 100-draw mean to a single-draw W = 10⁴ band.**
Fix: compare per draw (at least 95% of draws inside), or use a matched-size band.

**N9. The v2 pre-read is incomplete for the sealed run.**
- `preread_out_v2` has no `rhs_G2.npz` and no `G2:RP10/RP11` (it was run without CHI4_ZEROS).
- `main_run` reads tables and bands from one PRE_DIR. The bands are in `results/preread/`, the v2 tables in
  `preread_out_v2/`.
- The seal JSON must pin the pre-read outputs (tables, `rhs_*.npz`, `nulls_*.npz`), not only code. `check_seal` checks
  only what `seal["files"]` lists.

**N10. RHS bound gaps.** None is material: the measured margin is at least 250×.
- The Dirichlet tails (`ph6lib.py:214`, `219`) and fbound count only the g(+log n) half of each line.
- The conductor and pole rounding is covered only by `add_round`'s 8u.
- The G1 class and prime float error is an ad hoc 8u·Σ|term| (`preread.py:135`), not derived.
- The G4 `e_rhs` omits the kλ rounding, which is covered by its 16u factor.

**N11. chi4 count check.**
- \|N − N̄\| < 2 cannot detect a single missed zero when |S(20000)| < 1, which is typical.
- The contingency [20000, 40000] cannot be merged or accuracy-checked by the current code: `plan()`, `merge()`,
  `accuracy()` and `preread.configs` all hard-wire 20000.

Fix: add an independent integer check N(T) = θ(T)/π + (1/π)arg L(½+iT, χ₋₄) at T and at the chunk edges. Parametrise T_MAX
before A4(b) can be used.

**N12. The dry run does not exercise the sealed G4 code paths.**
- It builds its picket tolerance inline with the old `1e-12·max(1, |RHS|)` (`gates.py:231–232`), so the sealed G4
  tolerance code (`preread.py:176–181`) is never run against a picket LHS before the seal.
- The dry-run pickets read NOT RESOLVABLE (10⁴-level synthetic), so the PASS branches of `g4_confusable` and
  `g4_incommensurate` are untested there. I unit-tested them on constructed ideal readouts with the G0 band: both PASS,
  and c = −log 2 or the ζ truth FAIL as they should.

Fix: move the G4 tolerance into one `ph6lib` function used by both preread and the dry run.

**N13. Consistency asserts.**
- `gates.py:89` and `:157` use atol = 10⁻⁹·max|RHS|. At G0-s that is ~1.7e-9, which exceeds ε_min (8e-10).
- `maass_gate` scores Layer A against the recomputed RHS, while `zeta_like_gate` uses the pre-read RHS.

Fix: use atol ≤ 10⁻³·min ε, and one convention for which RHS is scored.

---

## 5. What was confirmed correct (in addition to the v1 list)

- **fsum.** `_fsum_rows` evaluates Σw·cos and Σw·sin per row with `math.fsum`. M uses phase −τE with weights w(−E).
  `maass_sector_sum` and the picket LHS also use fsum. Null draws and Layer-B readouts stay on BLAS, which is acceptable
  because they are statistical.
- **ε_float** = 2⁻⁵¹(τΣ(w⁺+w⁻)E + Σ(w⁺+w⁻)) + 2·2⁻⁵³Σ(w⁺+w⁻). This covers per-term phase rounding (u|τE|), window and
  cos/product evaluation (~5.5u per unit weight in total, absorbed by the phase term's 3u|τE| slack when |τ| ≳ 0.1), and
  the correctly rounded fsum result. It is conditional on N1.
- **Red-path constructions.** RP1 (rhs + P_nonprime), RP2 (rhs + 2P), RP3 (shifted LHS), RP8 and RP9 match their
  pre-read reach terms term for term. So do RP10 (χ ≡ 1 prime sum) and RP12 ((e^{τ/2} − 1)|RHS|).
- **Rulings on constructed known answers.**
  - G0, G0-c and G2 truth → PASS.
  - Swapped truth → FAIL.
  - G2 truth vs ζ → FAIL with POSITION, SIGN and WEIGHT.
  - Ideal confusable picket → PASS (c = log 2 at 2^k, silent at 3, 5, 7, T3 vs ζ FAIL with WEIGHT/SIGN).
  - Ideal incommensurate picket → PASS.
- **G3 allowance.** `binom.ppf(0.99, 100, 0.01)` = 4 exceedances. Poisson uses its own band; the ζ cross-read uses the
  GUE band; the positive control adds `templ @ a_ζ`.
- **chi4 smooth count.** N̄(T) = arg Γ(¾ + iT/2)/π + (T/2π) log(4/π), with no +1. This is consistent with N(T) = θ_χ(T)/π + S(T)
  and with `ph6lib.nbar_chi`.
