# Phase 34f-cohomological-H Findings — ARS Sato-Tate engine validated against the BCGNT-2025 *proven* target

**Status:** COMPLETE. Verdict **`COHOMOLOGICAL_H_METHODOLOGY_VALIDATED_AT_FINITE_P`**. First calibration of the integrated ARS Sato-Tate instrument against a *mathematically proven theorem* (Boxer–Calegari–Gee–Newton–Thorne 2025) rather than an empirical/conditional anchor. Brief: `PHASE34F_COHOMOLOGICAL_H_BRIEF.md` (committed b1361d8, three-way `(cm,bc)` stratification). Data + results: `data/phase34f_cohh/` (gitignored).

## Frame

BCGNT 2025 proves Ramanujan + Sato-Tate **unconditionally** for cohomological (regular-algebraic parallel-weight) Bianchi modular forms over CM fields; non-CM stratum → semicircular (2/π)√(1−x²)dx. This makes Cremona's `bianchi-data` newform corpus a *proven*-Sato-Tate dataset → calibrate the ARS H-side engine against a proven target. **Scope (load-bearing):** instrument validation, NOT discovery, NOT a test of BCGNT; does **NOT** advance the §D.4 Q(√−3) three-coordinate Δ-closer (still 34f-E-Δ-Maass-blocked). Distinct substrate from 34f-G/E-Δ (Bianchi-Maass).

## §3 Data — RESOLVED in-environment

`JohnCremona/bianchi-data` GitHub `newforms/` consolidated catalogs (NOT LMFDB/lmfdb=website; NOT bianchi-progs=program; NOT the reCAPTCHA/rate-limited LMFDB API). Two GitHub-raw files, format documented in `newforms/schema.txt`. Parsed **40,030 Q(i) + 42,343 Q(√−3) forms, 0 malformed** across 57 MB. `cm`/`bc` inline → three-way stratification keyed at source, zero derivation.

## §6 Engine pre-validation — PASS

Multi-seed (K=50, n=4000): true-measure reject_rate 0.020 ≈ α (p-values Uniform under H₀ ⇒ sampler↔CDF exact), wrong-measure (uniform) reject_rate 1.000. **Harness bug caught & fixed (§7.ter.57-class):** the initial single-draw `KS p>0.05` gate false-failed (p=0.029 is a benign draw — under H₀ the KS p is Uniform(0,1)); replaced with the statistically-correct multi-seed rejection-rate criterion. Engine validated *before* touching real data.

## §4 Decode gate — RESOLVED:idealnorm (both fields), empirically

`[AP]` is positionally prime-ideal-indexed; the ordering is the §D.0b residue. Resolved against known truth, not assumed — three corroborating criteria, both fields:

| field | ordering | bc=1 conj-eq | genuine control | RP-within (BCGNT Thm A) |
|---|---|---|---|---|
| Q(i)    | **idealnorm** | **1.0000** | 0.042 | **1.00000** |
| Q(i)    | ratprime      | 0.547 | 0.029 | 0.932 ✗ |
| Q(√−3)  | **idealnorm** | **1.0000** | 0.047 | **1.00000** |
| Q(√−3)  | ratprime      | 0.486 | 0.033 | 0.932 ✗ |

bc=1 base-change conjugate signature recovered **exactly** (a(𝔭)=a(𝔭̄)=classical aₚ); genuine-non-CM negative control ≈0.04 (signature is real, not adjacency artifact); BCGNT-proven Ramanujan bound **exactly** satisfied under idealnorm on ~82k real forms, decisively broken (0.932) under ratprime. The §D.0b silent-corruption surface is closed **empirically** (§7.ter.55 instrument-validation on real known-truth). Harness refinement caught en route: the gate must test the signature on the `bc=1`-good-prime subset (the brief's §4 spec), not all `bc≠0` incl. twists.

## Substantive — per-stratum per-field (finite-P framed)

**Discipline (§7.ter.57 / Phase-34d finite-X):** at pooled n = 10⁵–10⁷ a KS p-value →0 for any infinitesimal finite-P deviation and is **uninformative**; the verdict uses the KS *statistic* (effect size) + a Chen-2019 finite-P scan (does the deviation shrink as the prime bound grows = the NLO correction tail?). The initial `p>0.01` flag was the same wrong-instrument class as §6 and was discarded.

| field:stratum | n | KS_full | finite-P scan (1e3→1e6) | verdict |
|---|---|---|---|---|
| Q(i):C genuine-non-CM | 7,701,850 | 0.0217 | 0.0242→0.0217 ↓ | `SATO_TATE_VALIDATED_AT_FINITE_P_WITH_CORRECTION` |
| Q(i):B base-change-non-CM | 249,860 | 0.0189 | 0.0236→0.0190 ↓ | `..._VALIDATED_AT_FINITE_P_WITH_CORRECTION` |
| Q(i):A CM | 7,506 | 0.2557 | ≈0.26 (flat, huge) | `SATO_TATE_CM_NON_SEMICIRCULAR_AS_EXPECTED_DESCRIPTIVE_ONLY` |
| Q(√−3):C genuine-non-CM | 8,078,006 | 0.0232 | 0.0257→0.0233 ↓ | `..._VALIDATED_AT_FINITE_P_WITH_CORRECTION` |
| Q(√−3):B base-change-non-CM | 290,621 | 0.0197 | 0.0241→0.0199 ↓ | `..._VALIDATED_AT_FINITE_P_WITH_CORRECTION` |
| Q(√−3):A CM | 4,543 | 0.2647 | ≈0.26 (flat, huge) | `SATO_TATE_CM_NON_SEMICIRCULAR_AS_EXPECTED_DESCRIPTIVE_ONLY` |

- **C (headline):** the ARS Sato-Tate engine recovers BCGNT's **Bianchi** semicircular on the genuine-non-CM stratum to ~2% KS, deviation shrinking with prime bound (Chen-2019 NLO) — on 7.7M/8.1M eigenvalues across both fields.
- **B:** independently consistent via the **classical** GL(2)/ℚ Sato-Tate (Newton–Thorne) — a *different* proven theorem; reported separately, never pooled with C (false-positive-equivalence discipline, §7.ter.49).
- **A:** the negative control — CM correctly non-semicircular (engine discriminates); the §5 CM Hecke-character target measure was not pre-pinned ⇒ `_DESCRIPTIVE_ONLY`.

## Verdict map (asymmetric — proven-theorem-calibration tier, METHODS §1)

- **Cell:** `COHOMOLOGICAL_H_METHODOLOGY_VALIDATED_AT_FINITE_P` — instrument validated against a proven theorem; **not** a discovery, **not** a substantive convergence claim, **does not touch the Q(√−3) Δ-closer**.
- **Forward:** 34f-G-H / 34f-E-H Maass Sato-Tate engine inherits earned validation (`CONVENTION_PROPAGATED_FROM_34e` → engine validated on a proven Bianchi target). Does NOT change 34f-G/E-Δ `DATA_ACQUISITION_BLOCKED` or the §D.4 closer status.

## Methodology

No new numbered generalisation — faithful application of §7.ter.55 (validate the instrument on known truth: §4 decode vs bc=1 classical signature + BCGNT Thm A on 82k forms; §6 engine vs exact semicircular) and §7.ter.57 (a fitted/threshold criterion is not an absolute when the instrument/regime is the issue — caught **twice**: the §6 single-draw p-threshold and the §7 large-n p-criterion; both replaced with the statistically-correct instrument). Canonical sharpening of §7.ter.57: **at pooled n ≳ 10⁵ a KS p-value is not the instrument; the KS statistic + finite-P (Chen-2019 NLO) scan is** — the Phase-34d finite-X discipline transposed to Sato-Tate finite-P.

## Outputs

```
PHASE34F_COHOMOLOGICAL_H_BRIEF.md (committed b1361d8)
phase34f_cohh/bianchi_data_loader.py   — fetch/parse/decode/stratify
phase34f_cohh/run_cohh.py              — §6 + §4 gates + substantive
phase34f_cohh/fetch_bmf_lmfdb.py       — demoted; optional LMFDB cross-check
data/phase34f_cohh/{newforms.1.1-100000,newforms.3.1-150000} [gitignored, 57 MB]
data/phase34f_cohh/{checkpoint_gate,st_results}.json [gitignored]
```
