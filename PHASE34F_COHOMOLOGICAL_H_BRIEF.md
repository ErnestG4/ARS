# PHASE 34f-cohomological-H BRIEF
## Sato-Tate methodology validation against the BCGNT 2025 *proven* target — cohomological Bianchi newforms, Q(i) + Q(√−3)

**Status:** Pre-execution. **BRIEF ONLY — execution held** per Will's Decision 1 (2026-05-15): the proven-theorem calibration is a novel verdict-class and the CM/non-CM stratification needs deliberate pre-spec, so brief approval is a meaningful checkpoint before the (non-trivial) bianchi-progs pull + engine run.

**Lit-lock:** BCGNT 2025 verified — Boxer–Calegari–Gee–Newton–Thorne, "The Ramanujan and Sato–Tate Conjectures for Bianchi modular forms," Forum of Mathematics Pi vol. 13 e10 (2025), DOI 10.1017/fmp.2024.29, arXiv:2309.15880. Scope confirmed: regular-algebraic parallel-weight (cohomological) GL₂(A_F), F any CM field; **non-cohomological weight-0 Bianchi-Maass NOT covered** (definitional). See PHASE34F_BRIEF §H.5 / §B.4.

---

## §0. Frame

BCGNT 2025 proves Ramanujan **and** Sato–Tate **unconditionally** for cohomological Bianchi modular forms over any CM field; for the **non-CM** stratum the normalized Satake parameters equidistribute per the semicircular measure (2/π)√(1−x²)dx on [−2,2].

Consequence: **Cremona's LMFDB cohomological Bianchi-newform Hecke eigenvalues are a *proven*-Sato-Tate-equidistributed dataset** (non-CM stratum). This is the first opportunity to calibrate the integrated ARS Sato-Tate instrument against a **mathematically proven theorem** rather than an empirical/Ramanujan-conditional anchor (every prior ARS Sato-Tate calibration — Phase 34d Gaussian/Eisenstein, 34e-H — used an empirical or conditional target).

This is a distinct substrate from 34f-G-Δ / 34f-E-Δ (Bianchi-**Maass**, non-cohomological, Ramanujan-conditional). The cell decouples H-side instrument validation from the multi-week Bianchi-Maass data-acquisition wait: when Maass H-side data eventually arrives it inherits *earned* engine validation rather than only `CONVENTION_PROPAGATED_FROM_34e`.

## §1. Goals

1. Validate the ARS Sato-Tate engine (Phase 34d/34e H-side machinery: RP-normalized a(𝔭), semicircular-KS test, Chen-2019 NLO finite-P correction) against the BCGNT-proven **non-CM semicircular** target, on cohomological Bianchi newforms over **both** Q(i) and Q(√−3).
2. Characterize the **CM** stratum against its own (non-semicircular) target with deliberately pre-spec'd per-stratum verdict labels.

## §2. Scope

**IN:**
- Cohomological Bianchi newform Hecke eigenvalues at prime ideals, fields Q(i) and Q(√−3).
- Non-CM stratum (semicircular target) and CM stratum (Hecke-character-measure target), stratified.
- Finite-P scan with Chen-2019 NLO structure (P_max as data depth allows).

**OUT (load-bearing):**
- **NOT** the Bianchi-Maass substrate; no Maass-side anything.
- **NOT** progress on the §D.4 Q(√−3) three-coordinate Δ-closer. Sato-Tate is the universal/null calibrator, not the signal-bearing Maass coordinate; the closer stays 34f-E-Δ-Maass-blocked (METHODS §1 proven-target-leak prohibition).
- **NOT** a test of the Ramanujan or Sato-Tate conjectures for cohomological forms — BCGNT *proved* them. We calibrate our instrument against the theorem; we do not test the theorem. Any |a(𝔭)|>2 escape or KS-fail on the non-CM stratum is an ARS-engine / data-pipeline error to debug, **never** a BCGNT counterexample.
- **NOT** a discovery/convergence cell — calibration-class only.

## §3. Data infrastructure + §D.0a pre-flight (THE FIRST GATE)

The §D.0a data-availability gate runs first and honestly (34f-G/34f-E discipline — no fabricated data).

- **Primary non-reCAPTCHA path:** Cremona's `bianchi-progs` (GitHub git-clone, https://github.com/JohnCremona/bianchi-progs). C library — build/run cost; supports class-number-1 imaginary-quadratic fields incl. Q(i), Q(√−3) on the holomorphic/cohomological side.
- **Secondary:** LMFDB API / bulk data dumps (NOT the reCAPTCHA-blocked browser page — explicitly burned for Bianchi in this conversation). Lower-cost if a dump exposes Hecke eigenvalues + a CM flag directly.
- **Gate assertion:** confirm in-environment extraction of `(form_id, field ∈ {Q(i), Q(√−3)}, prime_ideal_norm, hecke_eigenvalue_RP_normalized, CM_flag)` for cohomological Bianchi newforms, with enough non-CM forms × primes for a powered KS test.
- If not pullable in-env → **DATA_ACQUISITION_BLOCKED** with the concrete path documented (mirrors 34f-G/34f-E; pipeline still synthetic-validatable per §5).

## §4. §D.0b normalization gate

- a(𝔭) RP-normalized ∈ [−2,2]. **KEY DIFFERENCE from the Maass cells:** here the bound is **UNCONDITIONAL** (BCGNT proven) — an escape is a data/methodology-error flag, full stop, **not** a Ramanujan-conditional hedge. (METHODS §1 two-regime discipline.)
- Prime-ideal indexing: Q(i) split p≡1(4) / inert p≡3(4) / ramified above 2; Q(√−3) split p≡1(3) / inert p≡2(3) / ramified above 3.
- Document the analytic (unitary/RP) normalization giving [−2,2]; assert convention before any statistic.

## §5. CM/non-CM stratification (MANDATORY, pre-spec)

Split the newform set by CM flag **before any aggregate Sato-Tate statistic** — pooling CM and non-CM is the Phase 34c EC-root-number pooling-null false-positive class (§7.ter.49 / false-positive-equivalence-classes; METHODS §1).

- **Non-CM stratum:** target = (2/π)√(1−x²)dx semicircular (BCGNT Thm B). Proven; this is the calibration target.
- **CM stratum:** does **NOT** target semicircular. A CM Bianchi newform is an automorphic induction from a Hecke character ξ of a quadratic extension; its Satake parameters are governed by ξ and the Sato-Tate measure is the pushforward of the Hecke-character equidistribution — a **different** (non-semicircular) measure. **Pre-spec item:** the CM target measure must be written down explicitly before the run. If it cannot be pinned precisely pre-spec, the CM stratum is reported **descriptively and flagged**, not forced into a pass/fail.

## §6. Engine synthetic pre-validation (instrument discipline, runs BEFORE real data)

Per §7.ter.55/57 (validate the instrument on the known target before the unknown data — the discipline that caught the Berry-Robnik bug):

1. **Positive control:** draw N samples directly from the exact (2/π)√(1−x²)dx semicircular measure; confirm the ARS Sato-Tate engine KS-passes at the expected rate and the Chen-2019 finite-P correction recovers ≈0 on the exact-measure draw.
2. **Negative control:** draw from a deliberately wrong measure (uniform on [−2,2]); confirm the engine KS-**rejects**.

Only after both controls pass does the engine touch Cremona data.

## §7. Verdict vocabulary (asymmetric — proven-theorem-calibration tier, METHODS §1)

**Non-CM, per field K ∈ {Q(i), Q(√−3)}:**
- `SATO_TATE_METHODOLOGY_VALIDATED_AGAINST_PROVEN_TARGET_BCGNT2025_(K)` — KS-pass + finite-P documented.
- `SATO_TATE_VALIDATED_AT_FINITE_P_WITH_CORRECTION_(K)` — Chen-2019 NLO correction documented.
- `SATO_TATE_ENGINE_DISCREPANCY_(K)` — KS-fail on the proven target ⇒ **ARS-engine / pipeline debug trigger**, never a BCGNT counterexample.

**CM, per field K:**
- `SATO_TATE_CM_STRATUM_MATCHES_HECKE_CHARACTER_MEASURE_(K)` / `_DIVERGES_(K)` / `_DESCRIPTIVE_ONLY_(K)` (last if the CM target measure can't be pinned pre-spec).

**Cell-level:**
- `COHOMOLOGICAL_H_METHODOLOGY_VALIDATED` — both fields non-CM validated, CM stratum characterized ⇒ H-side engine carries earned validation forward.
- `DATA_ACQUISITION_BLOCKED` — §D.0a fired.
- **Never** a substantive convergence/anomaly verdict.

## §8. Forward / scope boundary

- On validation: 34f-G-H / 34f-E-H Maass Sato-Tate engine inherits earned validation (upgrades `CONVENTION_PROPAGATED_FROM_34e` → `ENGINE_VALIDATED_ON_PROVEN_BIANCHI_TARGET`).
- Does **NOT** change 34f-G-Δ / 34f-E-Δ `DATA_ACQUISITION_BLOCKED`, does **NOT** change the §D.4 Q(√−3) three-coordinate closer (still 34f-E-Δ-Maass-blocked).
- §7.ter generalisation: the proven-theorem-calibration tier already landed in METHODS §1 (PHASE34F_BRIEF §G.3). Promotion to a *numbered* §7.ter entry earns its place only if the run surfaces something substantive — no manufactured generalisations.

## §9. Methodological commitments

- Asymmetric-label, **proven-theorem-calibration tier** (METHODS §1) — instrument-scoped, no result/discovery leak, no leak onto the unrelated Δ-closer.
- **CM/non-CM stratify-before-pool** (Phase 34c precedent, METHODS §1).
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
