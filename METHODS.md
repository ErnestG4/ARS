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

- Wigner β-ensembles (Dumitriu–Edelman tridiagonal, β ∈ {1, 2, 3, 4, 6, 8})
- Hard-core (Matérn-II) point processes
- Ginibre projection (real_part, symmetric_part_eigvals)
- Uniform-with-jitter (t_n = n + σ · N(0, 1), σ ∈ {0, 0.02, 0.05, 0.10,
  0.15, 0.20, 0.30, 0.50})
- Pure Poisson

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
the classification must be invariant across at least four distinct
extractor mechanisms before it is reported as a property of the
underlying signal.  "Distinct" means mechanisms that differ in their
detection criterion, not just in parameter settings of the same
mechanism.

Examples of extractor families that are not mutually distinct:

- `find_peaks(prominence=0.3)` and `find_peaks(prominence=0.5)`
  (same mechanism, different parameter)
- threshold-upcrossings on signal A vs threshold-upcrossings on signal B
  (same threshold mechanism)

Examples of extractor families that are distinct:

- find_peaks vs threshold-upcrossings vs argmax-position-jumps vs
  by-construction categorical (e.g., "argmax target IS in sink set")

An extractor-invariance pass is necessary but not sufficient.  See
§7.ter.20 for the framework's distinction between "principled" (passes
extractor-invariance) and "induced" (does not pass) classifications.

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
