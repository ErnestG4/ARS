# Cross-substrate SOC pair — ComCat earthquakes + GOES solar flares

Status: ACTIVE (overnight, authorized 2026-05-30). Verdicts are Will's.
Progress-log discipline: NOT validated results until Will signs off.

## Frame

A **calibrator-zoo addition with near-ground-truth**. Two self-organised-criticality (SOC)
substrates — tectonic (USGS ComCat earthquake catalog) and solar (GOES soft X-ray flares) —
asked the same clustering-vs-quasiperiodic question. The known answer (earthquakes are strongly
clustered; ETAS / Omori-Utsu aftershock physics) is a **feature, not a bug**: the question is not
"are quakes clustered" but whether the ARS fingerprint *recovers* known clustering, *where* it lands
on the GUE↔Poisson axis, and *how far* declustering moves it. If ARS cannot recover known clustering
on a near-ground-truth substrate, that is exactly the kind of failure we want to find on a known
substrate, not a mystery one.

ComCat is open, no registration, clean per-event origin-time tables. A modern complete global window
is 10⁵–10⁶ events — comfortably above the robust-NNS point. So the clustered and declustered reads
are **statistically strong**; the single-fault repulsion read is the **N-limited** one (no-false-
positive regime at best — flagged as such).

The deeper reading of "directionality" is **time-arrow / irreversibility**. Aftershock sequences are
strongly time-asymmetric (buildup ≠ Omori decay), but pooled-NNS is asymmetry-blind by construction
(our own §7.ter.10 band-invariance proposition: NNS of {t_i} ≡ NNS of {−t_i}). A strongly time-
directional substrate is therefore exactly where that blindness can be *demonstrated*: run pooled-NNS
(sees the clustering, misses the arrow) against an ordering-sensitive observable (a time-reversal-
asymmetry statistic and the magnitude-conditioned Omori rate asymmetry), and the **gap** between them
is the directionality NNS structurally cannot see. Clustering is what the spacing engine reads;
directionality is what it is blind to; quakes have a great deal of both. Banked-discipline material.

## Goals (graded)

- **G1 — clustered read (strong, N≈10⁵–10⁶).** Fingerprint (Family I + II via axes.py) of the global
  complete catalog event-time sequence. Does it recover clustering? Where on GUE↔Poisson↔(super-Poisson)?
  Expectation: far from GUE, on the *clustered* side of Poisson (excess mass at small s).
- **G2 — declustered read (strong).** Gardner–Knopoff (window) declustering, plus a second method
  (Reasenberg or a simple ETA/nearest-neighbour) as robustness. The fingerprint should move *toward*
  Poisson. Quantify the displacement on each axis. This is the calibration: the *direction* of motion
  is known a priori.
- **G3 — single-fault repulsion read (N-LIMITED).** A single well-instrumented fault/segment. If
  characteristic-earthquake quasiperiodic recurrence produced level repulsion, would the fingerprint
  see it? Report as **no-false-positive regime at best** — small N, so a null is uninformative and a
  positive would need surrogate confirmation. Flag explicitly; do not over-read.
- **G4 — directionality probe (discipline).** (a) Literally show pooled-NNS forward ≡ reversed
  (band-invariance, §7.ter.10). (b) Compute an ordering-sensitive time-reversal-asymmetry statistic
  on the spacing-increment series, and the magnitude-conditioned Omori rate asymmetry (rate after a
  mainshock ≫ rate before). The gap quantifies what NNS cannot see.
- **G5 — solar-flare pair (GOES soft X-ray).** Same clustering question on a second SOC system; power-
  law waiting times, live Poisson-vs-memory debate. Solar-cycle modulation is a second within-substrate
  knob (solar max → clustered, solar min → more Poisson). Two SOC systems, one tectonic, one solar,
  asking the same question.

## Acceptance

- Fingerprint computed through the matched axes.py contract (unfolded positions → canonical_spacings).
- Declustering moves the fingerprint in the known direction (toward Poisson); displacement quantified.
- Surrogate floor reported (rate-matched homogeneous Poisson) at the analysis resolution.
- The **one-sided-fitter caveat** documented: Brody q ∈ [0,1] and Berry–Robnik ρ ∈ [0,1] span only
  Poisson→GOE; they are blind to super-Poisson clustering and will rail at 0. Clustering is read on the
  Poisson-excess side (mass<τ, CV of spacings, signed W1-to-Poisson). This is itself a calibrator-zoo
  finding about the instrument.
- Directionality gap quantified; pooled-NNS forward≡reversed shown numerically.
- Honest N-flags on G3.

## Out of scope

- ETAS parameter inference / re-deriving seismology. We read the temporal fingerprint, not fit the
  generative model.
- Full spatio-temporal point-process modelling. Temporal (+ magnitude marks) only.
- Magnitude-frequency (Gutenberg–Richter b-value) estimation beyond what completeness checks need.

## Methodological commitments

1. **Entry-point audit (cross-domain audit discipline).** ComCat records are individual event origin
   times — raw-ish per-event products, NOT folded/binned aggregates. Safe w.r.t. §7.ter.19 (no find_peaks-
   on-aggregate artifact). Caveat carried: catalog completeness magnitude (Mc) varies in space/time; use
   a threshold above global Mc and a modern window for the strong reads. GOES flares: event lists are
   peak-flux-thresholded detections — also per-event, but detection threshold ≈ a completeness analogue.
2. **Surrogate adequacy.** Rate-matched homogeneous Poisson is the trivial null. Apparent clustering can
   be manufactured by rate non-stationarity (growing network, completeness drift); guard via (i) modern
   complete window, (ii) a local-rate-unfolding robustness pass, (iii) reporting that declustering — which
   removes *correlated* triggering but not secular rate — collapses most of the excess (if it does, the
   excess was triggering, not drift).
3. **Matched instrument.** Hand axes.py the event-time sequence as unfolded positions (unit-mean
   spacings). Document the one-sided-fitter point above.
4. **Band-invariance / §7.ter.10** is the load-bearing proposition for G4: pooled-NNS is invariant under
   time reversal; the directionality lives in observables the spacing engine discards (order, marks).
5. **Acquisition hygiene.** Sequential paged FDSN pulls only — NO parallel/overlapping curls on shared
   paths (parallel-curl-corruption lesson, Phase 24). Size via the count endpoint, page by time, verify
   each page's byte size + row count before concatenation, cache under coordinates/comcat/.

## Files

- `comcat_fetch.py`   — self-sizing sequential paged FDSN downloader → coordinates/comcat/*.csv
- `comcat_port.py`    — G1/G2/G3/G4: fingerprint, declustering, single-fault, directionality
- `goes_flares.py`    — G5: GOES flare list fetch + same fingerprint + solar-cycle split
- coordinates/comcat-fingerprint.jsonl, figures/P_comcat_soc.png  (banked outputs)
