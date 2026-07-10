# Phase 38 — The Reliability Ledger (Allen per-unit axes)

**Primary deliverable is the ledger, not the axis.** Every empirical per-unit axis on
Allen carries a banked split-half ρ against its admissibility gate, or it carries no
orthogonality verdict at all. Whether `p7_mean_z` survives is a *byproduct*.

Doctrine: `TOOLKIT.md` §9 (ceiling arm, commit f616c50). Gate code:
`phase32b/reliability_gate.py`. Exhibit: `phase32b/PROPOSED_7TER50_RETROSCOPE.md`.

---

## Frame

Phase 32b §7.ter.50 banked `BOTH_ORTHOGONAL` on Allen from three per-cell axes
(`p7_mean_z`, `rep_med`, `ks_gue_med`) regressed on Williamson noise-correlation FA.
None had its reliability measured. `R²(R,B) ≤ ρ(R)`, so a low R² is the expected
reading of an unreliable axis.

Measured 2026-07-09: `ρ(p7_mean_z) ∈ [0.132, 0.437]` across defensible centering
frames, against a required `> 0.565`. Cause is estimator noise (z against **3**
surrogates → `max|z| = 190`; rank-robust ρ rises monotonically with event count,
`Spearman(quartile,ρ) = +1.000`, lowest quartile `ρ = −0.221`). `rep_med` and
`ks_gue_med` have **no per-window values banked at all** — their ρ is not merely low,
it is *unmeasured*, and every verdict resting on them is in an unknown state.

A repair that raised only `p7_mean_z`'s surrogate count would let a fresh ORTHOGONAL
verdict slip in under a ceiling nobody computed. The ledger is the deliverable.

## Structural-null audit (front-loaded)

Analysis object: **a finite-sample per-unit estimate**, whose reliability is being
measured. This is a new family for the audit — not support-restricted, not
random-walk, not spectral-coordinate. Its natural null:

- **Null for "is ρ real":** a cell with **no stable per-cell axis** — replace each
  window's events with a rate-matched Poisson draw at that cell's own rate. Split-half
  ρ must return **≈ 0**. Any positive ρ here is estimator-side leakage (shared
  normalization, shared q-set, shared unfold) and invalidates the ledger.
- **Positive control for "does ρ recover":** inject a known per-cell offset into the
  windows (a synthetic axis of known reliability ρ_true). The estimator must recover
  ρ_true within CI.

Both are mandatory pre-flight. Per `synthetic_validate_fitters`: the ρ estimator is a
fitter and gets validated against ground truth before any absolute ρ is reported.
**No axis ρ is read until both calibrators pass.**

## Goals

1. **Bank per-window raw values** for all three axes on the same 5-window partition:
   `z_w0..4` (p7, at 100 surrogates), `rep_med_w0..4`, `ks_gue_med_w0..4`. Raw objects,
   not just point estimates — no recompute next time.
2. **Bank split-half ρ + bootstrap CI** for each axis, on the cohort the banked R² was
   measured on.
3. **Decide each axis against its gate** (`ρ > R²_obs/τ`) and bank the verdict:
   ADMISSIBLE-ORTHOGONAL / INDETERMINATE / SUBSUMED-CERTIFIED.
4. **Run the noise-vs-nonstationarity discriminator per axis** (ρ by event-count
   quartile). Names the repair for any axis that fails.
5. Resolve the pre-registered `p7` surrogate-count prediction (below).

## Methodology — four bound requirements

These exist to stop the repair reintroducing the disease. Each is a defect found in the
current code, not a hypothetical.

**B1 — Freeze the unfold.** `unfold_unit_mean` computes `sp / sp.mean()` *per call*
(`run_phase21_falsification.py:71`), a self-derived rate. Windowed, each window would
normalize by its own mean, so windowed and full-train `rep_med` would live on different
scales and ρ would not transport to the banked R². **Compute the unit-mean spacing once
on the full train; apply that single divisor to every window.** Report full-train vs
per-window unfold as a sensitivity panel, but gate on the frozen one.

**B2 — Match the decimation regime.** `JPF_CAP = 5000` stride-decimates spacings above
the cap. Full trains trip it; windows (≈n/5) mostly will not — a silently different
estimator across the split. **Disable the cap for both, or apply an identical decimation
factor to both.** Declare which. (cf. `stride_decimation_destroys_prime_angle_structure`.)

**B3 — Fix the q-set.** `rep_med = median(rep_int_q over well-powered q)`. The
well-powered set is recomputed per window, so the median would run over a *different*
q-set in each window — inter-window disagreement manufactured by aperture drift rather
than by the cell. **Fix a common q-set: q well-powered in all 5 windows *and* in the
full train.** Bank `n_q_common` per cell; if it collapses, that is the finding.

**B4 — Cohort invariance (the one that would fake a pass).** `MIN_EVENTS_PER_Q = 30`
against 5× fewer events per window will trim the cohort toward high-event cells. ρ rises
monotonically with event count. **Trimming inflates ρ, so an axis could clear its gate
because the cohort was selected on the variable that drives ρ.** Therefore:

  - ρ MUST be reported on the **same cohort** as the R² it is gating; and
  - if the cohort is trimmed, **R² is re-measured on the trimmed cohort** and the gate
    recomputed (`ρ > R²_obs^trimmed / τ`);
  - **both** the full-cohort and trimmed-cohort ledgers are banked, and a verdict that
    differs between them is **INDETERMINATE**, not the cohort you liked.

**Surrogate count.** 3 → 100, `p7` only. `rep_med`/`ks_gue_med` use no surrogates — they
are direct statistics, so *no surrogate count can raise their ρ*. Their reliability is
set by events-per-window and by B1–B3. State this plainly in the ledger so nobody later
"repairs" them by adding surrogates.

**Threshold scale (declare, do not inherit).** τ applies to **disattenuated (true)** R².
Phase 27 used `ORTHOGONAL < 0.3`; Phase 32b hardcodes `0.20` while claiming to replicate
it. **Pre-register τ = 0.20 on the true scale for all three axes**, and report the τ=0.3
reading as a sensitivity row. Never compare an observed R² to a threshold across metrics
of differing ρ.

## Pre-registered predictions (written before execution)

- **P1.** If 3-surrogate denominator noise dominates `p7_mean_z`, then at 100 surrogates
  `ρ(p7) > 0.50`. If `ρ(p7)` remains `< 0.40`, the residual noise lives in the *observed*
  statistic (events per window), no surrogate count fixes it, and **the axis has no
  stable per-cell value at this windowing** — a per-cell regression was the wrong model.
- **P2.** `ρ(rep_med)` and `ρ(ks_gue_med)` exceed `ρ(p7 @ 3 surrogates)`, since they are
  full-train-style statistics free of a surrogate denominator. Falsified if not.
- **P3.** The event-count quartile trend, which is `+1.000` for p7 @ 3 surrogates,
  **flattens** for p7 @ 100 surrogates. A persisting `+1.0` trend means the noise is in
  the observed statistic, corroborating the P1 failure branch.

## Acceptance criteria

**PASS (phase-level):** every one of the three axes carries a banked ρ, CI, cohort, and
gate decision — including axes that fail. The ledger is complete or the phase fails.
Axis survival is not an acceptance criterion.

Per-axis verdicts, in the only directions the evidence can support:

- **ADMISSIBLE-ORTHOGONAL** — `ρ_CI_lower > R²_obs/τ`. Orthogonality is now a real claim.
- **INDETERMINATE** — `ρ` fails the gate anywhere in its CI/frame band. Default. Not
  orthogonal, **not** subsumed.
- **SUBSUMED-CERTIFIED** — permitted *only* if ρ is pinned tightly enough that
  `R²_obs / ρ_CI_upper ≥ 0.50`, i.e. the disattenuated value clears the SUBSUMED floor
  across the whole CI. Otherwise INDETERMINATE. **Disattenuation raises the lower bound;
  it cannot certify the upper.**

**FAIL:** any axis regressed on a baseline without a banked ρ in the same commit.

**Calibrator gate (blocking):** Poisson-null cells return `ρ ≈ 0` and the synthetic
known-ρ control recovers ρ_true within CI. If either fails, no axis ρ is reported.

## Out of scope

- **RESULTS.md §7.ter.50 rewrite** — remains HELD for Will. This phase supplies the
  measurement; the verdict rewrite is a separate, reviewed act.
- Other substrates (pvc-11, hc-3, ret-1, IBL). The gate applies to them; this phase does
  not run them. Their orthogonality verdicts stay **uncertified** meanwhile.
- Phase 32a's population-level `PER_WINDOW_SUBSTRATE_CONSISTENT` — averaging across cells
  can recover a population effect no single cell supports. Untouched.
- The session-level cross-engine `ρ = −0.086 (n=6)`. Flagged **attenuation-unsafe**; n=6
  cannot support a session-level reliability estimate. Carried as a bound, not resolved.
- Arithmetic surveys 34a/b/c — immune (`ρ≈1` by construction: exact full-sequence
  entering quantities, stratum-vs-null verdicts, no cross-unit correlation to attenuate).

## Methodological commitments carried through

- Calibrator zoo **before** axis readout (Poisson-null + synthetic known-ρ).
- Report the **ρ band across centering frames**, not a point. A verdict that flips inside
  the band is INDETERMINATE.
- Bank raw per-window objects (`no_forbidden_recompute`).
- Gate output strings must name **which part** of the claim they certify
  (`gate_certifies_half_say_so`).
- Report honestly: an axis failing its gate is a deliverable. No post-hoc retuning of τ,
  the window count, or the cohort until something passes.

## Cost / execution notes

- Data: all 6 sessions cached at `/home/combust/fmexplorer/allen_cache/` (14.1 GB). **No
  download.** Loader: `phase32b/per_cell_decomposition.py:84 → loader.load_session`.
- Compute: 431 cells × 5 windows × 100 surrogates for `p7` (≈33× the p7 leg of 32b), plus
  windowed `joint_q_profile` ×5 per cell for `rep_med`/`ks_gue_med`.
- Workers: **10** (`worker_count_bandwidth_bound` — local 5900x peaks ~10, not 18).
- venv: `/home/combust/fmexplorer/bin/python3`.
- Outputs → `data/phase38_results/`: `per_cell_windowed_axes.parquet` (raw per-window
  values, all three axes), `reliability_ledger.parquet` (axis × cohort × ρ × CI × R²_obs ×
  ρ_required × verdict), `calibrator_validation.json`.
