# METHODS

The protocol the ARS toolkit implements, including calibrator-zoo
construction, extractor-invariance testing, and induction-on-noise
falsification.  The protocol is an applied integration of standard
statistical practices (null-hypothesis controls, calibration with
synthetic ground truth, post-hoc verification on noise inputs); it is
not a novel methodological framework.

## Pipeline

```
sorted t_k (event timestamps)
   │
   │  joint_q_profile(t_k, q_max)
   ▼
joint_q_profile DataFrame
   ├─ rep_int_q  (repulsion integral per Farey-q band)
   ├─ rf_amplitude_q  (Ramanujan-Fourier amplitude per q)
   ├─ ks_gue_q, ks_goe_q  (KS distances against Wigner forms)
   ├─ mass_lt_0_3_q  (short-spacing mass)
   ├─ underpowered  (n_events_q < min_events_per_q)
   │
   │  joint_quadrant_diagnostic(jdf)
   ▼
per-q quadrant assignment (BL / TR / BR / TL / ambiguous)
   │
   │  recover_*(...)  (per-class parameter recovery)
   ▼
parameter estimate + 95% CI + flagged-out-of-domain bool
```

The two axes of the joint plane:

- **rep_int_q** = ∫₀¹ (1 − R₂(r)) dr, the pair-correlation repulsion
  integral over r ∈ [0, 1].  Empirically a near-scalar across q for any
  uniform-jitter-class signal (std(rep_int_q) ≈ 10⁻⁴ on continuous
  synthetic inputs).  Values range from ≈ 0 (Poisson, no repulsion) to
  ≈ 0.9 (near-uniform spacing).
- **rf_amplitude_q** = |a_q| from the Ramanujan-Fourier expansion of the
  integer-time-bin event indicator.  Spikes at specific q identify
  periodic structure at period q.

The four quadrants:

| quadrant | rep_int_q | RF spike | reading |
|---|---|---|---|
| BL | low (< 0.10) | no | Poisson noise |
| TR | mid (0.10–0.55) | no | Wigner-class |
| BR | high (≥ 0.55) | no | uniform-with-jitter |
| TL | any | yes (> 5× median) | periodic at q |

Within BR, the toolkit further distinguishes BR_artifact (KS_GUE ≥ 0.10,
nearest-Wigner-form fit returns saturated rep_int_q) from BR_novel
(KS_GUE < 0.10, signal genuinely fits Wigner GUE despite saturated
rep_int_q).  Calibrator inputs do not produce BR_novel; the label is
reserved for genuine surprises.

## Required tests before reporting a classification

Three pre-registration tests must pass before a classification on a real
input is reported as a property of the input.  A classification that
fails any of these tests must be reported as a property of the
extraction pipeline, not of the input.

### 1. Calibrator-zoo membership

The toolkit's σ̂ recovery and quadrant-diagnostic anchors are calibrated
on a fixed set of synthetic inputs:

- Wigner β-Hermite ensembles (Dumitriu–Edelman tridiagonal,
  β ∈ {1, 2, 3, 4, 6, 8}) — for spectra on the real line
- Circular β ensembles (CUE / COE / CSE via Mezzadri 2007
  QR-with-phase-normalization, β ∈ {1, 2, 4}) — for spectra on
  S¹ (function-field Frobenius eigenphases, prime-angle Hecke
  L-function statistics, etc.). Added in Phase 34d (§7.ter.51) for
  number-field prime-angle substrates.
- Hard-core (Matérn-II) point processes
- Ginibre projection (real_part, symmetric_part_eigvals)
- Uniform-with-jitter (t_n = n + σ · N(0, 1), σ ∈ {0, 0.02, 0.05, 0.10,
  0.15, 0.20, 0.30, 0.50})
- Pure Poisson

**Spectrum-coordinate dispatch (Hermite + Circular).**  Choose the
calibrator family by where the substrate's spectral coordinate lives:

- Spectrum on **R** → Hermite β-ensemble (Dumitriu–Edelman tridiagonal).
  Applicable to number-field L-function zeros (ζ, Dirichlet L, EC L
  in Phase 34c §7.ter.49).
- Spectrum on **S¹** → Circular β-ensemble (Mezzadri 2007 QR-with-phase).
  Applicable to function-field Frobenius eigenphases (Katz 2017 IMRN
  framework) and number-field prime-angle Hecke L-function statistics
  (Rudnick-Waxman 2019, Phase 34d §7.ter.51).

Per Rudnick-Waxman 2019 Proposition 5.3, the three classical compact-group
families G ∈ {U(N), USp(2N), SO(2N)} all give identical bulk variance
min(n, N) at leading order; the bulk-dominated ARS engines (NNS, RF Mode
B, p-adic v4) inherit this indistinguishability and cannot tell
CUE-from-COE-from-CSE on a substrate whose right null is in the
Wigner-Dyson β class.  When the substrate's right null lives at the
*global moment* level (Rudnick-Waxman class), the σ²(K, X) curve must
be recorded as a required complement to the bulk-ARS readout — ARS
provides "in the right β class" confirmation; only the global moment
σ²(K, X) directly tests the literature target (§7.ter.52).

**Asymmetric verdict labelling discipline (Phase 34d).**  When a phase
runs both a *literature-confirmed* substrate (target prediction exists
in published form, e.g., Rudnick-Waxman 2019 for Gaussian primes) and a
*first-measurement* substrate (target is a structural extension with
no published prediction, e.g., Eisenstein primes extending RW to Z[ω]
where no dedicated paper exists), the per-substrate verdict labels
must be **asymmetric** — they encode different epistemic content and
treating them symmetrically leaks an unearned claim.

  - **Literature-confirmed substrate** → labels reference the
    published asymptote with bootstrap-quantified deficit:
    `RW_SHAPE_CONFIRMED_AT_FINITE_X` (shape ✓, magnitude X-limited
    with documented gap), `RW_REPLICATED` (only if the deficit is
    within bootstrap error of the published prediction at the
    measured X), etc.  Never report "REPLICATED" without an error bar
    plus a documented finite-X correction model.

  - **First-measurement substrate** → labels reference the structural-
    extension hypothesis: `FIRST_MEASUREMENT_SHAPE_CONSISTENT_WITH_STRUCTURAL_EXTENSION`,
    `FIRST_MEASUREMENT_DIVERGES_FROM_EXTENSION`, etc.  Never re-use
    `REPLICATED` for a substrate where no published prediction exists
    — the right semantic is "extended-by-analogy" or "first
    measurement of the natural extension shows the same finite-X
    behavior as the calibrator," not replication.

The two substrates' agreement at finite X (Phase 34d
`CONSTANT_LEVEL_AGREEMENT`) is *consistency evidence* for the
structural-extension hypothesis, not replication of an asserted
prediction.  See PHASE34D_FINDINGS.md SQ-2 and the §7.ter.51 entry in
RESULTS.md for the canonical application.

**Proven-theorem calibration tier + two-regime Ramanujan-conditionality
(Phase 34f, BCGNT 2025).**  The asymmetric-label discipline above has
two epistemic tiers — *empirical-anchor* (published numerical/asymptotic
prediction) and *structural-extension first-measurement* (no published
prediction).  A third, sharper tier exists when the instrument is
calibrated against a **mathematically proven theorem** rather than an
empirical anchor:

  - **Proven-theorem-calibration substrate** → the target is a theorem,
    not a measured/published number.  Verdict labels name the theorem
    and assert *instrument* validation, never a result:
    `<STAT>_METHODOLOGY_VALIDATED_AGAINST_PROVEN_TARGET_<CITATION>`
    (Phase 34f canonical: `SATO_TATE_METHODOLOGY_VALIDATED_AGAINST_
    PROVEN_TARGET_BCGNT2025`).  This is the cleanest possible
    calibration — the target carries no conditionality or finite-sample
    caveat of its own — but the label must stay *instrument-scoped*:
    matching a proven equidistribution validates the engine, it does
    not "confirm" or "discover" anything (the theorem already settled
    it).  Never let a proven-target match leak into a substantive
    convergence/anomaly claim about an *unrelated* coordinate (Phase
    34f: a cohomological-H Sato-Tate validation is NOT progress on the
    Q(√−3) three-coordinate Δ-Maass closer — Sato-Tate is the
    universal/null calibrator, not a signal-bearing coordinate).

Companion **substrate-handling discipline — split conditionality by
substrate type before reporting any Ramanujan-conditional caveat.**
When a phase touches automorphic-form Hecke eigenvalues, the
Ramanujan-Petersson status is **not uniform across substrate types** and
must not be stated monolithically:

  - A substrate whose Ramanujan/Sato-Tate is *proven* for its class
    (e.g. cohomological / regular-algebraic parallel-weight Bianchi
    forms over CM fields — BCGNT 2025) carries **no** conditional
    caveat; an out-of-[−2,2] escape there is a data/methodology-error
    flag, full stop.
  - A substrate where Ramanujan is *open* (e.g. non-cohomological
    weight-0 Bianchi-**Maass** forms, which BCGNT explicitly does not
    reach; conditional path Getz–Hahn–Yao 2025) keeps the
    Ramanujan-conditional handling — document any escape as a
    methodology-error candidate, not a Ramanujan falsification.

State the regime per substrate; conflating them either leaks an
unearned unconditional claim onto the open case or attaches a spurious
caveat to the proven one.  **CM/non-CM stratify-before-pool:** a proven
Sato-Tate target (BCGNT semicircular) holds for the *non-CM* stratum
only; CM forms have a distinct Satake distribution (automorphic
induction from a Hecke character — a different measure).  Stratify
before any aggregate Sato-Tate statistic and give each stratum its own
verdict label — pooling CM and non-CM is the same false-positive class
as the Phase 34c EC-root-number pooling-null (§7.ter.49 /
false-positive-equivalence-classes).  This discipline generalises
beyond 34f to any future Hecke-eigenvalue work with Ramanujan-Petersson
open (higher-rank GL_n, non-CM, class-number > 1 Bianchi).  See
PHASE34F_BRIEF §B.4 / §H.5 and PHASE34F_COHOMOLOGICAL_H_BRIEF.md.

A real input's joint-plane position must be reported relative to this
calibrator family.  `recover_uniform_jitter_sigma` returns σ̂ = position
within the uniform-jitter calibrator family; reading σ̂ as "the σ
parameter of the input's underlying generative process" is only
appropriate when the input is known to be in the uniform-jitter class
(for example, synthetic inputs generated from uniform_jitter, or point
processes by construction such as primes or ζ zeros).

For continuous-trace inputs extracted via peak detection, σ̂ describes
the extractor's gap distribution within the calibrator family, not a
property of the underlying signal.

### 2. Extractor-invariance

When the input is a point process extracted from a continuous trace,
the classification must be invariant across at least four
**empirically mechanism-distinct** extractors before it is reported as
a property of the underlying signal.  "Mechanism-distinct" is an
empirical property as of Phase 19 (§7.ter.26):

> A pair of extractors (A, B) is demonstrably distinct iff there is at
> least one calibrator class for which A and B produce different
> per-q quadrant assignments under `joint_quadrant_diagnostic`,
> robustly across calibrator-level resamples (≥ 4 of 5 seeds at
> α ≈ 0.05).

Description-distinctness (different names, different code paths) is
not sufficient; the test must be run on the standard 8-class calibrator
panel before invariance can be claimed.

Examples of extractor families that are not mutually distinct (verified
empirically in Phase 19):

- `find_peaks(prominence=0.3)` and `find_peaks(prominence=0.5)`
  — same mechanism, different parameter; pairwise test returns
  `distinct = False`.
- The four LLM attention extractors `attention_sink_events`,
  `layer_kl_divergence_events`, `attention_argmax_sink`,
  `attention_multi_head_sink_consensus` collapse into a single
  equivalence class on the calibrator panel — they read attention
  concentration on sink tokens via different surface mechanisms but
  share the underlying threshold-on-derived-signal step.

Examples of extractor families that are distinct (verified empirically):

- The six general-panel extractors (`direct_events`, `pll_passage`,
  `find_peaks_prominence`, `derivative_zeros`, `threshold_crossing`,
  `modular_bin_events`) are mutually mechanism-distinct under the
  empirical test.

The empirical-distinctness API is in `extractor_distinctness.py`;
`run_phase19_distinctness_matrix.py` produces the full pairwise matrix
for the project's extractor panel.

An extractor-invariance pass is necessary but not sufficient.  See
§7.ter.20 for the framework's distinction between "principled" (passes
extractor-invariance with ≥ 4 mechanism-distinct extractors) and
"induced" (does not pass) classifications.

### 3. Induction-on-noise falsification

For each extractor used, run the same extractor on a noise input of
equivalent statistical character to the underlying continuous trace
(typically iid exponential or Poisson noise of matched magnitude and
length).  If the extractor's events from noise input land in the same
quadrant as the events from real input, the classification is
extractor-induced and must be retracted.

Examples documented in this codebase:

- find_peaks(prominence=0.3) on autocorrelated continuous traces
  produces rep_int_q saturating in BR_artifact regardless of the
  underlying trace (§7.ter.19 layer-0 diagnosis).
- moving-mean + k·σ → up-crossings on iid exponential noise produces
  rep_int_q ≈ 0.34 with TR-quadrant assignment (§7.ter.23 Finding F).

Both were diagnosed during LLM-internal-state application and retracted
the corresponding provisional readings.

## Sample-size requirements

The σ̂ and β̂ recovery routines have empirically determined minimum
n_events for ≥ 80% CI coverage (§7.ter.23 Tier 3):

| class | min n_events |
|---|---|
| Poisson | 200 |
| uniform_jitter | 200 |
| periodic | 200 |
| Wigner GOE / GUE / GSE | 1000 |

Inputs below these thresholds produce CIs that do not bracket the true
parameter at the stated coverage and should be reported as
underpowered rather than as recovered values.

## Reporting protocol

A classification on a real input should be reported with the following
information:

1. The input (n_events, source, any pre-processing applied)
2. The extractor used (if extracted from a continuous trace)
3. The joint-plane position: rep_int_q, rf_amplitude_q at each q (or
   median across q), KS_GUE, mass<0.3
4. The primary quadrant assignment, with quadrant_confidence label
5. The σ̂ (or β̂, λ̂, q̂, etc.) point estimate with 95% CI, flagged if
   out of calibrator domain
6. The result of the extractor-invariance test (which extractors agree,
   which disagree, on the quadrant)
7. The result of the induction-on-noise falsification (does the same
   extractor produce a similar classification on noise input)

Items 6 and 7 are mandatory for any real input that is not directly a
point process (e.g., zeros of a known function, eigenvalues of a known
matrix ensemble).

## Code entry points

- `arithmetic_toolkit.joint_q_profile(t_k, q_max=200)` — primary
  classification call.  Returns a DataFrame keyed by q.
- `arithmetic_toolkit.joint_quadrant_diagnostic(jdf)` — quadrant labels.
- `bulk_recovery.recover_poisson_rate(t_k)` — Poisson rate λ̂.
- `bulk_recovery.recover_wigner_beta(jdf)` — Wigner β̂.
- `bulk_recovery.recover_uniform_jitter_sigma(jdf)` — uniform-jitter σ̂.
- `bulk_recovery.recover_periodic_q(jdf)` — periodic period q̂.
- `field_generator.generate(class_name, params, n_events, seed)` —
  synthetic ground-truth point process for any of the calibrator
  classes.
- `run_phase17_threshold_induction.py` — worked induction-on-noise
  falsification example for threshold-upcrossing extractors.

## Limitations of this protocol

- The extractor-invariance test requires judgment on what mechanisms
  are "distinct".  In practice this is decided ad hoc and may miss
  shared deeper mechanisms (e.g., two different attention extractors
  that both internally apply a moving-mean threshold).
- The calibrator zoo is finite.  Inputs that lie outside any
  calibrator class produce flagged-out-of-domain σ̂ values that
  should be read as "this input is not in the uniform-jitter family"
  rather than as a quantitative recovery.
- The protocol does not provide a positive criterion for novel
  universality classes; BR_novel is reserved as a placeholder for
  signals that fit Wigner GUE well *and* have saturated rep_int_q,
  which is empirically not produced by any current calibrator class.
- The protocol has been applied successfully to point-process inputs
  with established universality classifications (instrument
  validation) and to one negative-result application (LLM internal
  state).  It has not been applied to a real input that produced a
  novel positive classification, and the calibration of the
  extractor-invariance and induction-on-noise checks for such a case
  is therefore untested.
