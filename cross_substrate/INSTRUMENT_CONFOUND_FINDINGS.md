# Instrument / collection-method confounds — FINDINGS

Module: `instrument_confound.py`. Closed-loop validation (`validate()`) +
first real-substrate lensing-ledger pass (`grb_ledger_pass()`). Run with the
main venv: `/home/combust/fmexplorer/bin/python3 instrument_confound.py`.

## Audit — what was already in place (verdict: GAPS CONFIRMED)
- **Nulls/calibrators are ~all mathematical.** Poisson / GOE / GUE / GSE /
  Hawkes / phase-randomized / cumulant-matched / hardcore-Matérn. The **only**
  instrument model is `run_phase21_calibrators.synthesise_deadtime_signal`
  (Fermi/BATSE/RHESSI), GRB-specific and not reused — the baseline panel and
  every cross-substrate port are 100% math nulls. No efficiency/thinning model,
  no sort/threshold model.
- **Provenance is lossy.** `coordinates/*.jsonl` carry IDs + Family-I axes + a
  one-line source stamp. Collection params (`DT=0.025`, sampling rate, subsample
  cap, sort label) live in loader hardcodes/docstrings and are dropped from the
  result. No ledger object.
- **No short-range dead-time-vs-repulsion separator** (caught post-hoc today via
  mass<0.3→0). **Thinning** exists only as a compute cap, never as a confound
  probe. The induction-on-noise harness (`run_phase18`) fires only on arithmetic
  findings, with math-null surrogates.

## What was built
Operators at the `positions` level (upstream of `canonical_spacings`), read on
the small-spacing-sensitive axes `{I.5_ks_gue, I.11_mass03, I.10_cv, I.12_cv2,
I.8_brody_q}`:
1. `apply_deadtime(τ, paralyzable=)` — non-extending (absolute refractory) and
   extending (detector-saturation) dead time.
2. `random_thin(p_keep)` — finite efficiency as Bernoulli retention.
3. `apparatus_subtracted_comparison` — empirical vs bare-null vs dead-time-
   injected-null → `{NULL, APPARATUS_EXPLAINS, RESIDUAL_STRUCTURE}`.
4. `thin_sweep` — deletion-fraction trajectory + washout flag
   `{THINNING_ROBUST, EFFICIENCY_DRIVEN}`.
5. `method_perturbation` — covariant / invariant / **saturated** across a
   {deadtime, thinning, binning} grid; only `METHOD_INVARIANT` promotes.
6. `Provenance` + `LensingRecord` + `write_ledger` — the durable output.

## Results

**VALIDATED (closed loop, ALL_PASS, A–H):**
- **A** Poisson thinning-invariant on all five axes.
- **B** dead time onto Poisson fakes repulsion (mass03 0.257→0.054, ks_gue
  0.283→0.192) and the injected null absorbs it → `APPARATUS_EXPLAINS`.
- **C** GRB deadtime synthetic → **no promotable substrate candidate** (repulsion
  axes read covariant or saturated, never invariant).
- **D** regular endpoint washes out under mild thinning (CV 0.07→Poisson, 51% of
  gap closed at 30% deletion) → `EFFICIENCY_DRIVEN` fires.
- **E** (crux) genuine GUE vs realistic-dead-time-injected null →
  `RESIDUAL_STRUCTURE` at z≈41. Same "looks-repulsive" observable as B, opposite
  origin, correctly separated.

**HARDENING for real data (2nd phase — addresses pre-hc-3 review):**
- **F** dead-time estimation uncertainty propagates into the injected null: with
  40% relative τ error the injected band widens 0.012→0.085 and the artifact is
  STILL absorbed. On real tetrode data τ is estimated, not known — a point-
  estimate null under-absorbs (promotes artifacts) or, if τ is set too large,
  over-absorbs (buries residual). `Provenance.dead_time_rel_err` carries the
  estimate's error; `build_lensing_record` feeds it through. RESIDUAL_STRUCTURE
  becomes a conservative call.
- **G** Finding-1 cuts both ways: a low-efficiency apparent-Poisson read is
  consistent with a *thinned sub-Poisson* substrate. The ledger flags
  `POISSON_CONSISTENT_WITH_THINNED_SUB_POISSON` when efficiency < 0.7 and the read
  is Poisson-consistent — so the caveat attaches to the Poisson null too, not only
  to sub-Poisson claims.
- **H** soft saturation (headroom, not exact rails): an axis NEAR a boundary that
  barely moves is indeterminate even if not exactly railed (mass03=0.012 →
  `METHOD_SATURATED`). The discriminant tests headroom + absolute movement: near a
  rail it promotes nothing unless the axis demonstrably swings OFF the rail
  (large absolute movement → covariant). Closes the approximately-invariant
  sneak-through the exact-rail guard left open.

**THREE-ZONE BRACKET (3rd phase — the real-data attribution method):**
The short-ISI hole in tetrode data MIXES genuine biological refractoriness
(substrate, keep) with pipeline censoring (sorter refractory + DAQ dead time,
subtract). A single empirical-floor τ captures whichever binds, so it
over-absorbs when biology dominates — a fine conservative *promotion* bar but a
corrupt *attribution* if stamped `APPARATUS_EXPLAINS`. So `apparatus_bracket`
runs two nulls — TIGHT (hardware/sorter refractory, minimal) and WIDE (empirical
ISI-floor, maximal) — and records the **zone**:
- **SUBSTRATE_ROBUST** — survives even the WIDE null → beyond maximal plausible
  apparatus → promotable. (Test **J**: genuine GUE.)
- **INDETERMINATE** — survives TIGHT but absorbed by WIDE → attribution genuinely
  ambiguous between biological refractoriness and pipeline; NOT promoted, NOT
  stamped apparatus. (Test **K**: moderate hole, span bracket.)
- **APPARATUS_EXPLAINS** — explained by even the TIGHT null. (Test **I**: known
  artifact, bracket containing the true τ.)
`estimate_deadtime_floor` uses the **P0.5 percentile** of ISIs (NOT the sample
min — an extreme order statistic the bootstrap underestimates) and a deliberately
**widened rel_err** (default 0.5); the band errs wide so the apparatus is not
under-modeled.

**OPEN — power, not correctness:** the z≈41 in (E) shows the separator is correct,
NOT that it has power. On real hc-3 the apparatus null will absorb most short-range
structure and the residual z will be small; detection power at realistic n is the
live question for the hc-3 pass. Report residual z WITH its uncertainty band, not a
bare verdict.

**GRB lensing-ledger pass (first real substrate):**
`coordinates/instrument_lensing_ledger.jsonl` — RHESSI 6µs deadtime, n=5206.
`mass03`→0 and `brody`→1 read `METHOD_SATURATED` (railed = the documented
`mass<0.3=0` dead-time signature); `ks_gue`/`cv`/`cv2` covariant. **PROMOTED:
(none).** Correct known-answer.

## Durable methodological outputs
- **Mild thinning does not easily erase the clustered or repulsive endpoints**
  (mass03 ~10% / GUE ks_gue ~42% of gap closed at 30% deletion); only the
  **regular/sub-Poisson endpoint is detection-efficiency-fragile** (one missed
  event → doubled gap). ⇒ substrate claims resting on clustering/repulsion are
  robust to moderate inefficiency; sub-Poisson claims carry a live efficiency
  caveat. → memory [[instrument_confound_thinning_asymmetry]]
- **Saturation ≠ invariance.** A railed axis (mass03@0, brody@1) has no dynamic
  range, so the perturbation discriminant cannot distinguish substrate from
  apparatus on it — it is INDETERMINATE, deferred to the injected-null stage. Same
  railed-estimator trap as the KPM floor. → [[floor_is_rigidity_not_density]]
- **Two-stage division of labor.** `method_perturbation` answers "method-sensitive
  vs method-robust" (genuine-but-fragile GUE AND apparatus both read covariant);
  `apparatus_subtracted_comparison` answers "reproduced by the *estimated*
  apparatus or not" (APPARATUS_EXPLAINS vs RESIDUAL_STRUCTURE). Promotion needs
  invariance; fragile-but-real structure is rescued as RESIDUAL only against the
  data's *estimated* dead time — which is exactly why the ledger carries the
  estimate as provenance, not a free knob (a too-large injected dead time would
  over-subtract real structure).

## Verdict
**MODULE VALIDATED — CLOSED-LOOP + GRB KNOWN-ANSWER.** Apparatus subtraction
separates dead-time-faked repulsion from genuine GUE and efficiency-faked Poisson
from genuine regularity, on the existing calibrators with no new data. Bound
held: method-invariance = robust to the manipulations run, not the territory.

## Queued
- Apply the lensing ledger to banked neural results (hc-3 tetrode first: real
  spike-sort + hardware refractory; pillar-2 most exposed). [[pillar2_burst_control_systematic]]
- ComCat Mc-completeness as a real detection-efficiency analog (thinning with a
  known SOC direction). [[soc_pair_complete]]
- Promote the dead-time operator + thinning sweep into the induction-on-noise
  harness so neural/cross-substrate findings get the same surrogate treatment
  arithmetic findings already do.
