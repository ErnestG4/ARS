# Phase 38 findings — the Reliability Ledger

**Deliverable met.** All 431 cells, all three empirical per-unit axes on Allen now carry a
banked split-half ρ against their admissibility gate. Zero cells trimmed (B4 satisfied by
construction: `status == OK` for 431/431, `n_q_common = 50` for every cell — B3 not binding).

Doctrine: `TOOLKIT.md` §9. Brief: `PHASE38_RELIABILITY_LEDGER_BRIEF.md`.
Artifacts: `data/phase38_results/{calibrator_validation.json, per_cell_windowed_axes.parquet,
reliability_ledger.parquet}`.

---

## 1. Calibrator gate (BLOCKING) — passed, and indicted the prior measurement

| arm | ρ₅ | split-half [95% CI] | |
|---|---|---|---|
| **A** — 3 surr, shared seed (**as-implemented in phase32b**) | **+0.257** | +0.186 [+0.088, +0.282] | **LEAKS** |
| **B** — 3 surr, independent | +0.047 | −0.014 [−0.109, +0.080] | clean |
| **C** — 100 surr, independent | ~0 | −0.018 [−0.111, +0.077] | clean |
| **D** — positive control | recovers ρ_true at a = 0.05/0.10/0.20/0.40 | | OK |

Arm A is run on **pure rate-matched Poisson cells with no per-cell axis whatsoever** and
still returns ρ = +0.257.

**Cause.** `phase32b/per_cell_decomposition.py:173` re-seeds `default_rng(seed + 98765)`
*inside* the window loop. `win_dur` is constant within a session, so the surrogate triple is
a deterministic function of `n` alone — equal-`n` cells receive byte-identical surrogates and
`z` becomes a deterministic function of `(real_p7, n)`. Since `n` is firing rate, stable
within a cell and correlated with FA loadings, the estimator correlates with itself through
rate.

**Consequence for the TOOLKIT §9 exhibit.** The ρ band `[0.132, 0.437]` reported for
`p7_mean_z @ 3 surrogates` was *itself inflated by the defect it diagnosed*. Measured against
its own null in an identical frame: real `+0.133` vs null `+0.096`, **excess +0.037,
95% CI [−0.111, +0.191], P(excess ≤ 0) = 0.32.** At 3 surrogates `p7_mean_z` is not
distinguishable from a cell with no axis. Leakage-corrected ρ ≈ 0.071 gives
`R²_true = 0.113/0.071 = 1.59` — **an R² above 1**, i.e. the disattenuation formula returns a
value outside the range of the quantity it estimates. This is the strongest possible
vindication of the §9 rule that disattenuation *can never certify the upper bound*.

## 2. The ledger (repaired estimator, τ = 0.20 on the true scale)

ρ is the Spearman–Brown reliability of the 5-window mean, rank-robust, bootstrap CI n=2000.

| axis | ρ (full cohort) | 95% CI | frame band |
|---|---|---|---|
| `p7_mean_z` @100 surr | **0.281** | [0.131, 0.401] | [0.290, 0.375] |
| `rep_med` | **0.921** | [0.896, 0.942] | [0.905, 0.915] |
| `ks_gue_med` | **0.978** | [0.971, 0.983] | [0.970, 0.970] |

| axis ~ baseline | R²_obs | ρ required | verdict |
|---|---|---|---|
| `p7_mean_z` ~ FA-nmo / FA-drift / raw | 0.118 / 0.104 / 0.085 | 0.588 / 0.520 / 0.424 | **INDETERMINATE (reliability below gate)** ×3 |
| `rep_med` ~ FA-nmo | 0.059 | 0.293 | **ADMISSIBLE-ORTHOGONAL** |
| `rep_med` ~ FA-drift | 0.177 | 0.885 | **INDETERMINATE** (B4: verdict flips across cohorts) |
| `rep_med` ~ raw props | 0.242 | 1.211 | **NOT-ORTHOGONAL** (R²_true = 0.263) |
| `ks_gue_med` ~ FA-nmo | 0.100 | 0.499 | **ADMISSIBLE-ORTHOGONAL** |
| `ks_gue_med` ~ FA-drift | 0.238 | 1.190 | **INDETERMINATE** (B4: verdict flips across cohorts) |
| `ks_gue_med` ~ raw props | 0.405 | 2.027 | **NOT-ORTHOGONAL** (R²_true = 0.414) |

**`p7_mean_z` carries NO orthogonality verdict at any baseline, on any cohort.**

### A fourth verdict state was required
A high-ρ axis whose `R²_true` clears τ is **not** "indeterminate" — it is reliably measured
and simply *not orthogonal*. Collapsing that into INDETERMINATE (which means *the instrument
cannot see*) would launder a real negative result into an unknown one. Hence
**NOT-ORTHOGONAL (subsumption not certified)**: `R²_true > τ` across the ρ CI, but the
SUBSUMED floor (0.50) is not cleared across the whole CI, so subsumption stays uncertified.
`SUBSUMED-CERTIFIED` was emitted for nothing.

## 3. Pre-registered predictions

- **P1 — FAILURE BRANCH.** Predicted `ρ(p7) > 0.50` if surrogate-denominator noise dominates;
  `< 0.40` ⇒ noise lives in the observed statistic and no surrogate count fixes it.
  **Result: ρ = 0.281, CI [0.131, 0.401].** 33× more surrogates did not rescue the axis.
  *Refinement, stated honestly:* the CI excludes zero, so a weak but real per-cell component
  exists (ρ ≈ 0.28). "No stable per-cell value" is too strong; the correct statement is **a
  weak, genuine per-cell component far below what any orthogonality verdict requires.**
- **P2 — CONFIRMED, emphatically.** `ρ(rep_med) = 0.921`, `ρ(ks_gue_med) = 0.978`, both far
  above `ρ(p7 @ 3 surr)`. Surrogate-free statistics carry no denominator noise.
- **P3 — CONFIRMED.** The event-count trend does **not** flatten at 100 surrogates
  (`+1.000 → +0.800`), corroborating P1's failure branch: the residual noise is in the
  observed statistic (events per window), not the surrogate denominator. Quartile ρ:
  `[−0.112, 0.132, 0.374, 0.366]`.

The trend is `+1.000` for `rep_med` and `ks_gue_med` too — reliability rises with event count
for *every* axis. This is exactly why B4 exists, and it fired.

## 4. B4 fired — twice

Trimming to `min_n ≥ 150` raised ρ for every axis (`0.921→0.963`, `0.978→0.984`) **and moved
R²**, flipping two verdicts in opposite directions:

- `rep_med ~ FA-drift`: ADMISSIBLE-ORTHOGONAL (full) → NOT-ORTHOGONAL (trimmed)
- `ks_gue_med ~ FA-drift`: NOT-ORTHOGONAL (full) → ADMISSIBLE-ORTHOGONAL (trimmed)

Per the brief, a verdict differing across cohorts is **INDETERMINATE**, not the cohort you
liked. Had the runner trimmed for computational convenience — the obvious engineering choice —
it would have selected on the very variable that drives ρ and delivered a clean, false result.

## 5. Scope limit — the ledger does NOT re-certify the banked 32b verdicts

Phase 32b's `rep_med`/`ks_gue_med` came from `phase24_results/per_session_h1_ars.parquet`, a
**different event set** (median `n_events_used` = 1,596 vs nmo 3,153; ratio 0.49). Cross-version
agreement is only `ρ = +0.547` (rep_med) and `+0.643` (ks_gue_med). These are **sibling
quantities, not the same measurement.** The Phase 38 ledger gates the R² of the Phase 38
quantity against the ρ of the Phase 38 quantity — internally coherent — and says nothing
directly about the banked numbers.

Applying the attenuation inequality across versions (valid **only** under the assumption that
both measure the same latent axis, which the differing event sets make uncertain) gives a free
lower bound `ρ_old ≥ r²/ρ_new`:

| banked axis | lower bound on ρ_old | gate | status |
|---|---|---|---|
| `rep_med` | ≥ 0.325 | > 0.565 | **still UNCERTIFIED** |
| `ks_gue_med` | ≥ 0.422 | > 0.630 | **still UNCERTIFIED** |

The bounds are non-trivial but insufficient. **The banked `rep_med` / `ks_gue_med` orthogonality
verdicts remain uncertified**; the ledger certifies a sibling, not them.

## 6. Two independent reasons 32b's BOTH_ORTHOGONAL fails

1. **Reliability** — the `p7_mean_z` leg cannot support a verdict (ρ = 0.281 ≪ 0.588), and its
   original ρ was inflated by shared-seed surrogate leakage.
2. **The unfold** — `unfold_unit_mean` divides by a *per-call* mean spacing (self-derived rate,
   the circularity §9 already names) and stride-decimates above `JPF_CAP = 5000`. Under the
   frozen unfold with decimation disabled (B1+B2), `ks_gue_med ~ FA-drift` moves from a banked
   R² of 0.126 to 0.238 — nearly double — carrying `R²_true = 0.243 > τ`. That leg fails for
   reasons that have **nothing to do with reliability at all.**

## 7. What is now true

- The H1 axis is **strengthened, and certified**: `ks_gue_med ~ raw props` (OSI-dominant) has
  `R²_true = 0.414` on an axis with ρ = 0.978. This is a reliable measurement of a real
  relationship, not an artefact. (`h1_direction_corrected` stands.)
- **`rep_med` and `ks_gue_med` are orthogonal to the natural-movie FA** — `ADMISSIBLE-ORTHOGONAL`
  on both cohorts. This is the first orthogonality claim in the project that has cleared a
  reliability gate. It is a *real* claim now, where before it was an unguarded one.
- **`p7_mean_z` — the axis §7.ter.50 called "the strongest INDEPENDENT_AXES reading" — is the
  only one that cannot carry any verdict.** It was strongest because it was noisiest.

## 8. Held / open

- `RESULTS.md` §7.ter.50 rewrite: **still HELD for Will.** Draft in
  `phase32b/PROPOSED_7TER50_RETROSCOPE.md`, now supersedable by this document.
- Banked `rep_med`/`ks_gue_med` ρ: **unmeasured on their own event set.** To certify the banked
  verdicts, re-run the windowed ledger on the ARS event set (`per_session_h1_ars` conditions).
- Session-level cross-engine `ρ = −0.086 (n=6)`: still **attenuation-unsafe**, unresolved.
- Other substrates (pvc-11, hc-3, ret-1, IBL): orthogonality verdicts remain **uncertified**.
- Fixed en route: `phase24/loader.py:49` held a literal, unexpanded `Path('$HOME/...')` — the
  bug named in the 2026-06-30 truth audit, still live and still breaking `load_session`.
