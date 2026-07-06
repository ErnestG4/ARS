# Phase 34f-cohomological-H Findings — ARS Sato-Tate engine validated against the BCGNT-2025 *proven* target

**Status:** COMPLETE — **AMENDED 2026-05-16** (Will's floor-anchoring catch; the original `COHOMOLOGICAL_H_METHODOLOGY_VALIDATED_AT_FINITE_P` headline is **RETRACTED** as overclaimed). Corrected verdict: **`COHOMOLOGICAL_H_SATO_TATE_CONSISTENT_TO_FINITE_PRIME_DEPTH_DISCREPANCY`** — the ARS Sato-Tate engine is consistent with the BCGNT-2025-proven semicircular up to the **effective-Sato-Tate finite-prime-depth discrepancy**, which decreases monotonically with per-form prime depth (to ~1.4–3× the n-floor on the depth-sufficient subpopulation) but is **corpus-depth-limited to a ~12–78× n-floor residual on the bulk** (per-form depth ≈100 primes). Not engine/decode (§6/§4 independently validated). First calibration of the integrated ARS Sato-Tate instrument against a *mathematically proven theorem* (Boxer–Calegari–Gee–Newton–Thorne 2025). Brief: `PHASE34F_COHOMOLOGICAL_H_BRIEF.md` (b1361d8). Data: `data/phase34f_cohh/` (gitignored). See **AMENDMENT** (§ below) for why the original was wrong.

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

## AMENDMENT (2026-05-16) — the original substantive verdict was overclaimed

**Will's catch (load-bearing).** The KS-statistic floor for n iid draws vs the true CDF is E[Dₙ] ≈ 0.8687/√n. At n≈2000 (the NNS-calibrator regime) that is ≈0.019 — which is why KS≈0.02 reads as "calibrator quality" everywhere in the NNS work. At n≈10⁷ the floor is ≈3×10⁻⁴. So the original headline KS≈0.022 at n=7.7M is **~70× the perfect-sample floor — a large deviation in effect-size terms, not a small one.** I excluded p-values for being sample-size-regime-dependent and then read the KS *statistic* in the wrong sample-size regime: the same discipline-class error, one level down. Additionally: the "Chen-2019 finite-P scan" attribution was wrong — Chen 2019 is the Rudnick–Waxman prime-angle *variance* result; the Sato-Tate semicircular convergence rate is governed by **effective Sato-Tate** (Thorner; Murty–Sinha discrepancy bounds). No functional form was ever fitted (the code did a too-weak monotonicity check); the attribution is **retracted**. The pooled global-norm-cutoff scan was also the wrong instrument — the ST discrepancy is governed by **per-form prime depth**, not pooled n or level.

**Corrected analysis (`run_floor_analysis.py` → `data/phase34f_cohh/floor_analysis.json`): KS / n-floor vs per-form prime depth k.** The corpus structure is decisive: the **bulk of the ~39k genuine-non-CM forms have only ≈100 good primes** (the AP lists are short); only a small deep subpopulation has ≥200.

| field:stratum | regime | KS | n-floor | **KS / floor** |
|---|---|---|---|---|
| Q(i):C | bulk (depth≈100, n≈3.9M) | 0.0314 | 4.4e-4 | **71×** |
| Q(i):C | deep (depth=800) | 0.0077 | 2.4e-3 | **3.2×** |
| Q(√−3):C | bulk (depth≈100, n≈4.1M) | 0.0333 | 4.3e-4 | **78×** |
| Q(√−3):C | deep (depth=800) | 0.0088 | 3.0e-3 | **3.0×** |
| Q(i):B | bulk (depth≈100) | 0.0316 | 2.5e-3 | **12×** |
| Q(i):B | deep (depth=800) | 0.0094 | 6.1e-3 | **1.5×** |
| Q(√−3):B | bulk (depth≈100) | 0.0332 | 2.4e-3 | **14×** |
| Q(√−3):B | deep (depth=800) | 0.0093 | 6.6e-3 | **1.4×** |

KS decreases **monotonically** with per-form depth (C: 0.057→0.043→0.031→0.011→0.0085→0.0077 for k=25→800) at the rate effective-Sato-Tate predicts. On the **depth-sufficient subpopulation** (≥800 primes/form) it is at/near the floor (B 1.4×, C 3×). On the **bulk corpus** at its native ~100-prime depth, a ~0.03 residual remains = **12–78× floor**. §6/§4 independently validate engine and decode, so this residual is the **finite-prime-depth Sato-Tate discrepancy of the corpus**, not an engine/decode defect — theory-governed (effective-ST) and shrinking with depth as expected, but the corpus's per-form prime depth is the binding limit and cannot drive it to the n-floor.

- **C:** consistent with BCGNT's *Bianchi* semicircular up to the effective-ST finite-prime-depth discrepancy; converging with depth; **not** floor-validated on the bulk.
- **B:** same behaviour via the *classical* Newton–Thorne route (separate stratum, never pooled with C, §7.ter.49); reaches the floor (1.4×) on the deep subpopulation.
- **A (CM):** KS≈0.26, decisively ≠ semicircular. This is a **one-sided discrimination control only** — it shows the engine separates "semicircle" from "not-semicircle"; it is **not** matched to CM's own ½δ₀+split-prime-arcsine measure (the §5 pre-spec item, not pinned ⇒ `_DESCRIPTIVE_ONLY`). A two-sided positive control (CM matched to its own measure) was not performed.

## Verdict map (asymmetric — proven-theorem-calibration tier, METHODS §1)

- **Cell (CORRECTED):** `COHOMOLOGICAL_H_SATO_TATE_CONSISTENT_TO_FINITE_PRIME_DEPTH_DISCREPANCY` — the engine is consistent with the BCGNT-proven semicircular up to the effective-ST finite-prime-depth discrepancy, monotone-converging with depth (to ~1.4–3× floor on the depth-sufficient subpopulation); the bulk-corpus ~12–78×-floor residual is the corpus prime-depth limitation, **not** engine/decode. **Floor-level validation is NOT achieved and is not achievable with this corpus's per-form prime depth.** Instrument validation against a proven theorem, bounded as stated; **not** a discovery, **not** a substantive convergence claim, **does not touch the Q(√−3) Δ-closer**. The original `METHODOLOGY_VALIDATED_AT_FINITE_P` is retracted.
- **Forward:** 34f-G-H / 34f-E-H Maass Sato-Tate engine inherits the *bounded* validation (engine+decode sound; ST consistency demonstrated to the corpus's prime depth). Does NOT change 34f-G/E-Δ `DATA_ACQUISITION_BLOCKED` or the §D.4 closer status.

## Methodology

No new numbered generalisation — faithful application of §7.ter.55 (validate the instrument on known truth: §4 decode vs bc=1 signature + BCGNT Thm A on 82k forms; §6 engine vs exact semicircular) and §7.ter.57. **Three §7.ter.57-class instrument-regime errors were caught and corrected in this cell** — the §6 single-draw KS-p>0.05 gate (false-fails ≈5% under H₀ since the KS p is Uniform), the §7 large-n KS-p>0.01 criterion (meaningless at n≳10⁵), and **the headline KS-statistic read in the wrong sample-size regime** (Will's catch; 0.022 is calibrator-grade at n~2000, a large deviation at n~10⁷). Canonical sharpening of §7.ter.57: **a statistic is only interpretable against its own sample-size/regime floor — for KS, the verdict is KS / (0.8687/√n) vs per-form prime depth, never KS alone, never a p-value at large n.** Two further lessons: (i) synthetic pre-flights must validate at *realistic* n, not convenient n — the §6/§7 bugs were n-scale-only failure modes a small-n harness passes; (ii) self-caught: the re-analysis's own max-depth "endpoint" was an artifact (the `len≥k` filter collapses to the few deepest forms) — fixed to a two-regime (bulk vs deep-subpop) report. The convergence model is **effective Sato-Tate (Thorner / Murty–Sinha)**, not Chen-2019/RW.

## Outputs

```
PHASE34F_COHOMOLOGICAL_H_BRIEF.md (committed b1361d8)
phase34f_cohh/bianchi_data_loader.py   — fetch/parse/decode/stratify
phase34f_cohh/run_cohh.py              — §6 + §4 gates + substantive
phase34f_cohh/fetch_bmf_lmfdb.py       — demoted; optional LMFDB cross-check
data/phase34f_cohh/{newforms.1.1-100000,newforms.3.1-150000} [gitignored, 57 MB]
data/phase34f_cohh/{checkpoint_gate,st_results}.json [gitignored]
```
