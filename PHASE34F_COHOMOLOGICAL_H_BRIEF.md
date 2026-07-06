# PHASE 34f-cohomological-H BRIEF
## Sato-Tate methodology validation against the BCGNT 2025 *proven* target — cohomological Bianchi newforms, Q(i) + Q(√−3)

**Status:** Pre-execution. **BRIEF ONLY — execution held** per Will's Decision 1 (2026-05-15): the proven-theorem calibration is a novel verdict-class and the three-way `(CM, bc)` stratification needs deliberate pre-spec, so brief approval is a meaningful checkpoint before the data pull + engine run. §D.0a pre-flight RUN (§3, 2026-05-16): `DATA_ACCESSIBLE` via LMFDB API `bmf_forms`; three-way stratification propagated through §1/§2/§5/§7/§9.

**Lit-lock:** BCGNT 2025 verified — Boxer–Calegari–Gee–Newton–Thorne, "The Ramanujan and Sato–Tate Conjectures for Bianchi modular forms," Forum of Mathematics Pi vol. 13 e10 (2025), DOI 10.1017/fmp.2024.29, arXiv:2309.15880. Scope confirmed: regular-algebraic parallel-weight (cohomological) GL₂(A_F), F any CM field; **non-cohomological weight-0 Bianchi-Maass NOT covered** (definitional). See PHASE34F_BRIEF §H.5 / §B.4.

---

## §0. Frame

BCGNT 2025 proves Ramanujan **and** Sato–Tate **unconditionally** for cohomological Bianchi modular forms over any CM field; for the **non-CM** stratum the normalized Satake parameters equidistribute per the semicircular measure (2/π)√(1−x²)dx on [−2,2].

Consequence: **Cremona's LMFDB cohomological Bianchi-newform Hecke eigenvalues are a *proven*-Sato-Tate-equidistributed dataset** (non-CM stratum). This is the first opportunity to calibrate the integrated ARS Sato-Tate instrument against a **mathematically proven theorem** rather than an empirical/Ramanujan-conditional anchor (every prior ARS Sato-Tate calibration — Phase 34d Gaussian/Eisenstein, 34e-H — used an empirical or conditional target).

This is a distinct substrate from 34f-G-Δ / 34f-E-Δ (Bianchi-**Maass**, non-cohomological, Ramanujan-conditional). The cell decouples H-side instrument validation from the multi-week Bianchi-Maass data-acquisition wait: when Maass H-side data eventually arrives it inherits *earned* engine validation rather than only `CONVENTION_PROPAGATED_FROM_34e`.

## §1. Goals

Per the three-way `(CM, bc)`-keyed stratification (§3), over **both** Q(i) and Q(√−3):

1. **Headline — Stratum C (genuine non-CM, `CM=0, bc=0`).** Validate the ARS Sato-Tate engine (Phase 34d/34e H-side machinery: RP-normalized a(𝔭), semicircular-KS test, Chen-2019 NLO finite-P correction) against the **BCGNT-proven Bianchi semicircular** target. This is the proven-theorem-calibration instrument test.
2. **Cross-check — Stratum B (base-change non-CM, `cm=0, bc≠0`).** Confirm semicircular agreement, but logged against the **classical GL(2)/ℚ Sato-Tate** lineage (Newton–Thorne) for the form it base-changes from — a *different* proven theorem; reported as a separate stratum, never pooled with C. The `bc=1` (over-ℚ) subset is also the §4 prime-index decode cross-check substrate.
3. **Characterize — Stratum A (CM, `CM≠0`).** Against its own (non-semicircular) Hecke-character-pushforward target, with deliberately pre-spec'd per-stratum verdict labels (or `_DESCRIPTIVE_ONLY` if the measure can't be pinned pre-spec).

## §2. Scope

**IN:**
- Cohomological Bianchi newform Hecke eigenvalues at prime ideals, fields Q(i) and Q(√−3) (LMFDB API `bmf_forms`, dimension-1 rational newforms; §3).
- Three-way `(CM, bc)`-keyed stratification — **A** CM (Hecke-character target), **B** base-change non-CM (classical-Sato-Tate target), **C** genuine non-CM (BCGNT-Bianchi semicircular target — headline) — partitioned before any aggregate statistic.
- Finite-P scan with Chen-2019 NLO structure (P_max as data depth allows).

**OUT (load-bearing):**
- **NOT** the Bianchi-Maass substrate; no Maass-side anything.
- **NOT** progress on the §D.4 Q(√−3) three-coordinate Δ-closer. Sato-Tate is the universal/null calibrator, not the signal-bearing Maass coordinate; the closer stays 34f-E-Δ-Maass-blocked (METHODS §1 proven-target-leak prohibition).
- **NOT** a test of the Ramanujan or Sato-Tate conjectures for cohomological forms — BCGNT *proved* them. We calibrate our instrument against the theorem; we do not test the theorem. Any |a(𝔭)|>2 escape (Ramanujan, proven for *all* cohomological forms incl. CM by BCGNT Thm A) or KS-fail on a semicircular stratum (B or C) is an ARS-engine / data-pipeline error to debug, **never** a BCGNT counterexample.
- **NOT** a discovery/convergence cell — calibration-class only.

## §3. Data infrastructure + §D.0a pre-flight — RUN 2026-05-15/16

**§D.0a verdict: DATA_ACCESSIBLE (clean schema).** Materially de-risked from the brief's pre-run framing. Gate run honestly (34f-G/34f-E discipline — no fabricated data); findings below.

**Path resolution (RUN — verified reality; supersedes the pre-run assumptions).**
- *LMFDB browser/HTML/API:* reCAPTCHA-walled from the agent environment across the **whole `lmfdb.org` domain incl. `/api/`**; from Will's machine the API works but is **rate-limited (reCAPTCHA after ~800 records)** — not a viable bulk path.
- **CHOSEN PATH — Cremona `JohnCremona/bianchi-data` GitHub, `newforms/` consolidated catalogs.** NOT `LMFDB/lmfdb` (website code, zero data) and NOT `bianchi-progs` (the program; heavy eclib→NTL→PARI build). Two single files on GitHub **raw**, reachable from the agent environment, **no reCAPTCHA / no rate-limit / no paging / complete**:
  - `newforms/newforms.1.1-100000` — Q(i) (`2.0.4.1`), levels of norm 1–100000 (~28 MB).
  - `newforms/newforms.3.1-150000` — Q(√−3) (`2.0.3.1`), levels 1–150000 (~29 MB).
  - `newforms/schema.txt` — the **in-repo format spec** (collapses the format-decode unknown).
- *LMFDB partial (~800 records on Will's machine):* demoted to an **optional independent cross-check** (LMFDB-decoded `hecke_eigs` vs our bianchi-data decode on the overlap) — no longer load-bearing.
- Consequence: the whole cell is now **executable end-to-end in the agent environment** (the data was always GitHub-reachable here; only LMFDB was walled).

**Schema (documented — `newforms/schema.txt`).** Whitespace-delimited columns:
`field_label level_label letter level_gens 2 bc cm sfe L/P [AL] x [AP]`. Weight is the literal `2` (parallel weight 2, BCGNT-in-scope); `x` ⇒ rational (a(𝔭) ∈ ℤ); `[AP]` = Fourier coeffs at all primes (good primes = Hecke eigenvalues). **`bc`/`cm` are richer than the LMFDB booleans:** `cm` = 0 (non-CM) or the squarefree CM-field discriminant; `bc` = 0 (not bc / not a bc-twist), d>0 (base change of a form with coeffs in Q(√d); **d=1 = over ℚ**), or −d (twist of a bc). All stratification keys are **inline at source — zero derivation**.

**Bounded §D.0b decode residue (→ §4) — de-risked, not eliminated.** `[AP]` is positionally prime-ideal-indexed in Cremona's *documented* standard ordering (no longer undocumented-format reverse-engineering). Establishing position → 𝔭 → N(𝔭) is still required to RP-normalize a(𝔭)/√N(𝔭) and drop field/level bad primes. **Self-verifiable hard sub-gate:** `bc = 1` forms are base changes of classical GL(2)/ℚ newforms, so the decoded RP a(𝔭) **must** reproduce the known classical coefficients (§7.ter.55 instrument-validation; the split-prime adjacent-equal-pair signature is the visible tell). Decode validated against the `bc=1` subset *before* any statistic; the LMFDB ~800 give a second independent check.

**Three-way stratification (data-driven, keyed on inline `(cm, bc)` — zero derivation).** Per the schema semantics; supersedes the two-way CM/non-CM split (stratify-before-pool, Phase 34c / METHODS §1):

- **Stratum A — CM** (`cm ≠ 0`): automorphic induction from a Hecke character; **non-semicircular**; target measure is the §5 pre-spec item.
- **Stratum B — base-change non-CM** (`cm = 0, bc ≠ 0`): semicircular, but **for a different proven reason** — inherits the classical GL(2)/ℚ Sato-Tate (Newton–Thorne) of the form it base-changes from, *not* the BCGNT-Bianchi route. The `bc = 1` (base change over ℚ) subset is also the §4 decode cross-check substrate.
- **Stratum C — genuine non-CM** (`cm = 0, bc = 0`): the **headline instrument-test stratum** — matching semicircular validates the engine against **BCGNT's Bianchi Sato-Tate theorem specifically**.

**Internal-consistency note:** the Stratum-B predicate is `bc ≠ 0` (base change over *any* field; the `bc = 1`/over-ℚ case is the cross-check subset within B). §1 goal 2 and §5 updated from the earlier `bc = 1` to `bc ≠ 0` in this commit.

Pooling B and C tests two distinct theorems under one label — the false-positive-equivalence-class trap (§7.ter.49). Per-stratum target/verdict treatment is specified in §5/§7; **§1/§2/§5/§7/§9 were propagated to the A/B/C split 2026-05-16 (this commit) — the brief is internally coherent on the three-way stratification.**

**Net.** cohomological-H moves from the pre-run `DATA_ACQUISITION_BLOCKED` risk to **DATA_ACCESSIBLE, near-runnable**: data clean and at source, CM+bc stratification free, one bounded self-verifiable decode between here and a run. Fallback (`bianchi-data` GitHub, raw format) documented if LMFDB API access degrades.

## §4. §D.0b normalization gate

- a(𝔭) RP-normalized ∈ [−2,2]. **KEY DIFFERENCE from the Maass cells:** here the bound is **UNCONDITIONAL** (BCGNT proven) — an escape is a data/methodology-error flag, full stop, **not** a Ramanujan-conditional hedge. (METHODS §1 two-regime discipline.)
- Prime-ideal indexing: Q(i) split p≡1(4) / inert p≡3(4) / ramified above 2; Q(√−3) split p≡1(3) / inert p≡2(3) / ramified above 3.
- Document the analytic (unitary/RP) normalization giving [−2,2]; assert convention before any statistic.

## §5. Three-way stratification (MANDATORY, pre-spec — keyed on inline `(CM, bc)`)

Partition the newform set by the inline `(CM, bc)` pair (§3) **before any aggregate Sato-Tate statistic**. Zero derivation — the partition is read directly off the source columns. Pooling strata that hit the same measure *via different theorems* (B with C), or mixing the non-semicircular stratum (A) into either, is the Phase 34c EC-root-number pooling-null false-positive class (§7.ter.49 / false-positive-equivalence-classes; METHODS §1).

- **Stratum A — CM (`CM ≠ 0`).** Does **NOT** target semicircular. A CM Bianchi newform is an automorphic induction from a Hecke character ξ of a quadratic extension; its Satake parameters are governed by ξ and the Sato-Tate measure is the pushforward of the Hecke-character equidistribution — a **different** (non-semicircular) measure. **Pre-spec item:** the A target measure must be written down explicitly before the run. If it cannot be pinned precisely pre-spec, Stratum A is reported **descriptively and flagged**, not forced into a pass/fail (`_DESCRIPTIVE_ONLY`, §7).
- **Stratum B — base-change non-CM (`cm = 0, bc ≠ 0`).** Target = (2/π)√(1−x²)dx semicircular, but the proven warrant is the **classical GL(2)/ℚ Sato-Tate theorem** (Newton–Thorne lineage) for the form it base-changes from — *not* BCGNT's Bianchi route. Same measure, different theorem; logged as its own stratum. Its `bc = 1` (over-ℚ) subset doubles as the §4 prime-ideal-index decode cross-check substrate (the known classical coefficients are the ground truth for the decode).
- **Stratum C — genuine non-CM (`CM = 0, bc = 0`).** Target = (2/π)√(1−x²)dx semicircular, warranted by **BCGNT 2025 Thm B (the Bianchi route)**. **This is the headline proven-theorem-calibration stratum** — agreement here validates the engine against BCGNT's Bianchi Sato-Tate theorem specifically.

Never pool B with C (two theorems, one label = false-positive trap). Never pool A into B or C (different measure). Stratify per field K ∈ {Q(i), Q(√−3)} as well — do not pool the two fields' strata.

## §6. Engine synthetic pre-validation (instrument discipline, runs BEFORE real data)

Per §7.ter.55/57 (validate the instrument on the known target before the unknown data — the discipline that caught the Berry-Robnik bug):

1. **Positive control:** draw N samples directly from the exact (2/π)√(1−x²)dx semicircular measure; confirm the ARS Sato-Tate engine KS-passes at the expected rate and the Chen-2019 finite-P correction recovers ≈0 on the exact-measure draw.
2. **Negative control:** draw from a deliberately wrong measure (uniform on [−2,2]); confirm the engine KS-**rejects**.

Only after both controls pass does the engine touch Cremona data.

## §7. Verdict vocabulary (asymmetric — proven-theorem-calibration tier, METHODS §1)

Per field K ∈ {Q(i), Q(√−3)}, per stratum (never pooled across strata or fields).

**Stratum C — genuine non-CM (headline; BCGNT-Bianchi proven target):**
- `SATO_TATE_METHODOLOGY_VALIDATED_AGAINST_PROVEN_TARGET_BCGNT2025_C_(K)` — KS-pass + finite-P documented.
- `SATO_TATE_VALIDATED_AT_FINITE_P_WITH_CORRECTION_C_(K)` — Chen-2019 NLO correction documented.
- `SATO_TATE_ENGINE_DISCREPANCY_C_(K)` — KS-fail on the proven target ⇒ **ARS-engine / pipeline debug trigger**, never a BCGNT counterexample.

**Stratum B — base-change non-CM (classical-Sato-Tate proven target; distinct theorem):**
- `SATO_TATE_VALIDATED_AGAINST_CLASSICAL_BASECHANGE_TARGET_B_(K)` — KS-pass; warrant is the classical GL(2)/ℚ Sato-Tate (Newton–Thorne), reported separately from C.
- `SATO_TATE_ENGINE_DISCREPANCY_B_(K)` — KS-fail ⇒ debug trigger (prioritise the §4 prime-index decode, since B *is* the decode cross-check substrate — a B discrepancy most likely means the decode, not the engine).

**Stratum A — CM (non-semicircular):**
- `SATO_TATE_CM_STRATUM_MATCHES_HECKE_CHARACTER_MEASURE_A_(K)` / `_DIVERGES_A_(K)` / `_DESCRIPTIVE_ONLY_A_(K)` (last if the A target measure can't be pinned pre-spec).

**Cell-level:**
- `COHOMOLOGICAL_H_METHODOLOGY_VALIDATED` — Stratum C validated on **both** fields (the load-bearing deliverable), B consistency-confirmed, A characterized ⇒ H-side engine carries earned validation forward.
- `COHOMOLOGICAL_H_PARTIAL` — Stratum C validated on one field only, or B/A incomplete; acceptable forward-progress with the gap documented (asymmetric-label `_PARTIAL` convention).
- `DATA_ACQUISITION_BLOCKED` — retained only as the fallback-path failure label (the §3 §D.0a verdict is `DATA_ACCESSIBLE`; this fires only if the LMFDB API degrades *and* the `bianchi-data` GitHub fallback also fails).
- **Never** a substantive convergence/anomaly verdict.

## §8. Forward / scope boundary

- On validation: 34f-G-H / 34f-E-H Maass Sato-Tate engine inherits earned validation (upgrades `CONVENTION_PROPAGATED_FROM_34e` → `ENGINE_VALIDATED_ON_PROVEN_BIANCHI_TARGET`).
- Does **NOT** change 34f-G-Δ / 34f-E-Δ `DATA_ACQUISITION_BLOCKED`, does **NOT** change the §D.4 Q(√−3) three-coordinate closer (still 34f-E-Δ-Maass-blocked).
- §7.ter generalisation: the proven-theorem-calibration tier already landed in METHODS §1 (PHASE34F_BRIEF §G.3). Promotion to a *numbered* §7.ter entry earns its place only if the run surfaces something substantive — no manufactured generalisations.

## §9. Methodological commitments

- Asymmetric-label, **proven-theorem-calibration tier** (METHODS §1) — instrument-scoped, no result/discovery leak, no leak onto the unrelated Δ-closer.
- **Three-way `(CM, bc)` stratify-before-pool** (Phase 34c precedent, METHODS §1): never pool Stratum B with C (same measure, *different proven theorem*) or A into either (different measure); stratify per field too.
- §D.0a data-availability gate fires honestly; no fabricated data (34f-G/E discipline).
- Engine synthetic-pre-validated against the exact proven target + negative control before real data (§7.ter.55/57).
- §D.0b: [−2,2] is **unconditional** here (NOT a Ramanujan-conditional hedge — that distinction is the Maass cells', METHODS §1 two-regime discipline).

## §10. References

- **BCGNT 2025** — Boxer, Calegari, Gee, Newton, Thorne, "The Ramanujan and Sato–Tate Conjectures for Bianchi modular forms," Forum Math. Pi 13 e10 (2025), DOI 10.1017/fmp.2024.29, arXiv:2309.15880. (Proven target — non-CM semicircular.)
- **GHY 2025** — Getz, Hahn, Yao, "Triple product L-functions and the Ramanujan conjecture," arXiv:2509.14381. (Conditional; Maass-relevant regime — cited for the regime boundary, NOT used here.)
- Cremona, J.E., *bianchi-progs*, https://github.com/JohnCremona/bianchi-progs (primary data path).
- Cross-ref: PHASE34F_BRIEF §B.4 / §H.5 / §G.3; METHODS.md §1 (proven-theorem calibration tier + two-regime conditionality).

---

End of brief — awaiting Will's review before §D.0a pre-flight / execution.
