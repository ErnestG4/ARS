# Instrument / collection-method confounds in point-process classification — BRIEF

## Frame
The ARS fingerprint classifies a point process, but a point process is already
**(substrate ⊗ instrument)**. The collection method imprints structure in the
exact observable we classify on — the spacings. Two apparatus artifacts
impersonate our two endpoints:

- **dead time / refractory window** → carves a short-range hole in the spacings
  → fakes GUE-style level repulsion.
- **finite detection efficiency / missed events** → acts as random thinning →
  drives any process toward Poisson → fakes the null.

Goal: subtract the apparatus before attributing structure to the substrate.

## Goals
1. **Dead-time-injected nulls.** Apply each dataset's estimated dead time /
   refractory window to the candidate null, re-derive expected NNS, compare the
   empirical against *that* — not the bare Poisson/GUE.
2. **Thinning sweep.** Randomly delete a range of point fractions; track how the
   class estimate moves; flag features that wash out under mild thinning as
   efficiency-driven.
3. **Method-perturbation disambiguation.** Vary threshold / sort / dead-time /
   bin-width; report which spacing features are method-covariant vs
   method-invariant. Only method-invariant features promote to substrate
   candidates.
4. **Lensing ledger.** Tag every result with full collection metadata and the
   perturbations it survived. The ledger, not the class label, is the durable
   output.

## Acceptance (closed-loop, no new data)
- **A** Poisson is thinning-INVARIANT (no false efficiency artifact).
- **B** Dead time injected onto Poisson FAKES repulsion, and the dead-time-injected
  null ABSORBS it → `APPARATUS_EXPLAINS`, not `RESIDUAL_STRUCTURE`.
- **C** The Phase-21 GRB deadtime synthetic (known apparatus artifact) yields NO
  promotable substrate candidate.
- **D** (positive control) the thinning sweep actually FIRES: the regular endpoint
  washes out under mild thinning → `EFFICIENCY_DRIVEN`.
- **E** (crux) genuine GUE, compared against a null with the data's *realistic*
  dead time injected, reads `RESIDUAL_STRUCTURE` — same "looks-repulsive"
  observable as (B), opposite origin, correctly separated.

## Out of scope (this pass)
- Per-lab spike-sort simulators (template matching, cluster curation) — the
  thinning sweep is the efficiency proxy; a real sort-parameter sweep is a later
  engineering arc. [[planned_engineering_arc]]
- Wiring instrument-aware nulls into the baseline calibrator panel / every port —
  this pass delivers the reusable module + the GRB known-answer pass.
- Cross-substrate re-audit of banked neural results (queued; GRB first because it
  is the known-answer that proves the discriminant).

## Methodological commitments
- **Bound, load-bearing:** method-invariance means "robust to the manipulations
  we could run", NEVER "the territory". The ledger records the perturbation set
  survived; it makes no universality claim. [[carry_viewpoints_annotate_validity]]
- Anchors calibrated empirically **through our own extractor** (2–98% trim +
  unit-mean), not textbook values. [[discriminant_exact_question_check]]
- A railed/saturated axis is **indeterminate** to the perturbation discriminant
  (it cannot move whether structure is substrate or apparatus) — never auto-
  promoted; deferred to the apparatus-subtraction stage. [[floor_is_rigidity_not_density]]
- Operators act at the **positions** level, upstream of `canonical_spacings`, so
  the entire Family-I axis stack is reused unchanged and the method is
  substrate-agnostic. [[support_set_respecting_nulls]]
