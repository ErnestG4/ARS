# GEO1 Step 1 plan: build and gates (committed before any run; Will's go 2026-10-30)

Brief: `../ph2/PH2_DECISIONS_2026-10-07.md` ("GEO1 opened", 2026-10-27). Step 0: `GEO1_STEP0.md`. Price:
`GEO1_STEP1_PRICE.md` (corrected below). Code: `geo1.py` (routes), `geo1_analyze.py` (gates, witness). Gates are known-
answer checks, not a sealed prediction; nothing here carries a verdict on new mathematics.

## 1. What is computed
Hyperbolic conjugacy classes of SL(2,ℤ) by trace t ≥ 3 (oriented closed geodesics of the modular surface, length
ℓ = 2 arccosh(t/2)); g_all(t) all classes, g_prim(t) primitive classes (Step 0 claim 2: the multiplicity is the sum
over fundamental (t, u)).

| route | range | what | independence |
|---|---|---|---|
| words | t ≤ T_w = 3·10⁴ | reduced positive matrices → R/L run vectors (the regular CF digits of the cutting sequence) → classes, primitive classes, pooled digit histogram over primitive classes | exact integers; no class numbers |
| pari | t ≤ T_m = 10⁶ | g_all(t) = Σ_u h⁺(d), h⁺ = h·(2 if N(ε_d) = +1 else 1), h from `quadclassunit`, N from `quadunitnorm` (PARI 2.17.2); g_prim by removing powers | class numbers; GRH-conditional beyond the words range |
| forms | t ≤ 40 | positive matrices → primitive forms → least reduced form of the Gauss ρ-cycle | exact integers; neither words nor PARI |

## 2. Range and cost (corrected price)
- **Correction to `GEO1_STEP1_PRICE.md`:** the explicit route's benchmark loop costs ≈ 0.39·t² steps per trace (so
  0.13·T³ in all, not T³/24); the production loop walks only d ≤ t/2 and b ≥ d, ≈ 0.071·t² steps per trace, ≈ T³/42.
- words, T_w = 3·10⁴: model Σ_t 0.071·t²·1.2 ns × 2.3 (spot) ≈ 0.5 spot core-h; one process, numba threads, 10
  cost-balanced groups; cost checks after groups 1, 3, 5, 8; stop above 1.25×.
- pari, T_m = 10⁶: ≈ 1.3·10⁶ (t, u) pairs × ≈ 4 ms (spot: `quadclassunit` 2.5–5.0 ms at d ≈ 10⁸–10¹²; `quadunitnorm`
  and `factor` negligible) ≈ 1.5 spot core-h; 100 chunks, 20 processes; first-chunk cost check.
- forms: seconds. Total ≈ 2 spot core-h; spot load checked before launch (ARSv2 shares it).

## 3. Gates (tolerances fixed here, before any run)
- **G1 (class counts).** For every t ≤ T_w: words all = PARI g_all and words primitive = PARI g_prim, exactly; for every
  t ≤ 40: forms = both. **Red path:** the wide sum Σ_u h(d) (no narrow factor) must differ from the words count at
  ≥ 1 t (it does at t = 6 by hand: 1 + 1 against 3), so G1 can fail.
- **G2 (R²L²).** At t = 6 the classes are exactly R⁴L, RL⁴, R²L² (run vectors [4,1], [1,4], [2,2]); the R²L² matrix
  (5 2; 2 1) has u = 2, d = 8; g_all(6) = h⁺(32) + h⁺(8) = 2 + 1 = 3 (Step 0 §6).
- **G3 (Sarnak / prime geodesic theorem).** Π(T) = Σ_{3 ≤ t ≤ T} g_prim(t) against Li(x²), x = ε(T) = (T + √(T² − 4))/2.
  Tolerance |Π/Li − 1| ≤ x^(−3/5)·ln(x²) at T = 10⁴, 10⁵ and 10⁶ (0.073, 0.023, 0.0069): the proven remainder
  O(x^{7/5}) (Step 0 §3, Sarnak 2007 (44) via Luo–Sarnak) with its constant set to 1. **Red path:** the wide sum must
  fail at T = 10⁶ (it under-counts every d whose fundamental unit has norm +1).
- **G4 (Gauss–Kuzmin over closed geodesics, Pollicott 1986).** Pooled digit frequencies over the primitive classes
  with t ≤ T_w against P(k) = −log₂(1 − 1/(k + 1)²), k ≤ 64, and P(> 64) = log₂(1 + 1/65): total variation ≤ 0.05.
  Basis: no rate is known (Step 0 §5); a finite-ℓ correction of order 1/ℓ ≈ 5% (ℓ ≈ 20.6 at t = 3·10⁴) on the leading
  bin is ≈ 0.02; the nearest wrong law (geometric run lengths) is at TV ≈ 0.2.
- **Witness that must fail.** Random cyclic L/R words of matched letter length (per sampled t, the mean letter length
  of its primitive classes; seeded 20261030; 300 t, ≤ 1,000 words each, ≤ 2·10⁷ letters): their run lengths must fail
  G4 (TV from Gauss–Kuzmin > 0.10) and be geometric (TV from 2^−k ≤ 0.02).

All of G1–G4, both red paths and the witness must hold. `geo1_analyze.py` runs twice in separate processes and the
outputs are compared with `cmp`; timings go to sidecar files only (TOOLKIT §9.F). A smoke run on t ≤ 200 / forms
t ≤ 40 / list t = 6 checks the code before the production run; it is a code check on the small-t seen range.

## 4. Outputs (Step 1)
`results/words_3e4.npz`, `results/pari_1e6.npz` (+ per-(t, u, d, h, N) rows), `results/forms_40.json`,
`results/list_t6.json`, `results/GATES.json`, hashes. Step 2 (descriptive: length spectrum with multiplicities,
multiplicity growth against t/log t, the partial-quotient histogram, mean period against (6 log 2/π²)·ℓ) follows the
gates, on Will's word.

## 5. Run log
- 2026-10-30 12:12 PDT, launch 1: stopped at import (spot's `specarith` env has cypari2 but no numba). Fixed by an
  optional numba import and a two-env launcher (4ab4b551). An import test wrote two scratch
  files to spot's /tmp; removed at once and logged (spot rule: ~/tmp/claude only).
- 2026-10-30 12:15 PDT, launch 2: the words route **stopped by its cost check, 1.667× the model after group 1 of 10**
  (the check is armed once the finished work models ≥ 60 s). Nothing else ran (no pari chunk started; no output read).
  The model (0.071·t² steps per trace × 1.2 ns × 2.3) under-prices the production loop on spot with 20 threads. At the
  measured rate the words route is ≈ 0.85 spot core-h instead of 0.5; the pari route is unaffected. Relaunch waits on
  Will.
- 2026-10-30, launch 3 (Will: "Yes please go ahead"): words model coefficient 0.071 → 0.12 per t² (the measured
  1.667×), stop line 1.25× of the new figure; pari unchanged. Total ≈ 2.4 spot core-h.
