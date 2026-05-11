# Arithmetic Resonance Spectrometer (ARS)

Python implementation of a two-engine point-process classifier built on
the Farey-rational phase-locked loop framework developed by M. Planat
and collaborators (FEMTO-ST, 2002–2026).

## What this is

A toolkit that takes a point process (sorted event timestamps) and
asks two formally distinct questions about it.

The **NNS engine** (`joint_q_profile`) decomposes the point process
over Farey-rational bands, computes analytical passage times per band,
and reads nearest-neighbour spacing statistics against Poisson / GOE
/ GUE references.  Its load-bearing outputs are `ks_gue_med` (median
over q-bands of the KS distance to GUE) and `rep_med` (median repulsion
integral).  The NNS engine carries dynamics-class signal (Poisson /
Wigner / TR / BR) at the recording-aggregate level.

The **RF engine** (`padic_amplitude_v4`) computes Ramanujan-Fourier
amplitudes on the event-indicator function and aggregates `|a_q|` over
q's divisible by each tested prime, normalised against the total
amplitude.  The RF engine carries per-prime arithmetic-class signal.

These two engines are formally distinct objects, not different views
of one engine.  The deployed classifier has both because of a proved
limitation of the first: any engine with the architecture `{filter
Farey rationals → analytical passage → unit-mean-normalised NNS →
KS}` is invariant under linear time scaling and **cannot** detect
prime-base asymmetry on stationary signals (§7.ter.10 band-invariance
proposition).  Three versions of p-adic profile (v1, v2, v3) failed
acceptance for this structural reason before v4, which routes through
the RF engine on indicator functions, passed.  Future work that
proposes to extract per-prime structure from `joint_q_profile` is
attempting an architecturally impossible measurement.

The classifier operates at two timescales — **full-sequence** (the
entire recording treated as one object) and **per-window** (tiled
into shorter epochs).  Full-sequence survival does not imply
per-window survival, and the same recording can carry a signature at
one scope and not the other.  Any surrogate-survival claim must
specify scope.

The framework's analytical content (Farey rationals as PLL natural
frequencies, Ramanujan-Fourier amplitudes, the Mangoldt-function
and Bost-Connes connections) is not original to this codebase.  ARS
is an applied implementation; it does not contribute new theoretical
mathematics.

## Why this exists

ARS was built on a specific epistemological frame.  The world is taken
to be a high-dimensional deterministic field structure, and every
empirical observation is understood as boundary readout — a partial
projection of the field onto a measurement apparatus that has its own
structural properties.  Every classification claim about a signal's
universality class is therefore a joint claim about the underlying
field and the readout apparatus.  Distinguishing what the field is
doing from what the apparatus is doing is the whole job.

The methodology in METHODS.md — calibrator zoo, extractor-invariance
test, induction-on-noise falsification — is not generic statistical
practice applied rigorously.  It is the specific discipline this
frame requires: the calibrator zoo characterises what the apparatus
does to signals of known structure before any unknown signal is read;
the extractor-invariance test checks whether a classification depends
on the readout method; the induction-on-noise step asks whether the
apparatus produces the same apparent finding when given input of
equivalent statistical character known not to contain the claimed
structure.

See `WHYTHISEXISTS.md` for the full framing, including the
implications for human + LLM collaborative reasoning under the same
boundary-readout commitment.

## Disciplines

Eight disciplines now structure what counts as a surviving finding.
A finding's confidence is its current position in this list.

1. **Full-sequence surrogate floors** — Aitchison-null, rate-matched
   Poisson, cell-shuffle, LN-evoked, state-modulated.  The aggregate
   signature is not reproduced by a null model with the relevant
   property preserved.
2. **Rate-matched surrogates** — isolate dynamics from rate.
3. **Rate-stratified within-cell comparison** — necessary elaboration
   of rate-matched; the dynamics signal may live in a specific rate
   tertile, so per-cell tertile comparison is the cleaner
   discrimination.
4. **Per-window surrogate** — full battery repeated on each window;
   asks for stationarity.
5. **Per-window p-adic** — same on the RF engine, separating long-
   coherence aggregation phenomena from short-coherence stationary
   ones.
6. **Spatial-scale stratification** — local-cluster, recording-wide,
   or scale-dependent.
7. **Cross-substrate** — replication across recording substrates with
   different spatial pitch, species, and brain state.
8. **Cross-engine** — NNS and RF engines agree on substrate-systematic
   direction.

A simpler **stationarity check** (modal-classification stability over
windows, without a full surrogate battery) is a weaker but useful
filter.

## What has been validated

These measurements have been reproduced at the precision indicated
on the specific datasets named.  They are reported as
**instrument-validation outputs** — they reproduce statistics
consistent with prior results in the corresponding literatures.
They do not extend those literatures.

### Arithmetic instrument validation

- Riemann ζ first 2,000 Odlyzko zeros: KS_GUE = 0.041, rep_int_q = 0.425.
  ζ at heights ~10⁶: KS_GUE = 0.012–0.015.  Consistent with the GUE
  conjecture. (§7.ter.7, §7.ter.21.)
- LMFDB elliptic curve L-functions, 87 curves, ~10,000 zeros: bulk
  GUE, edge separation by root number. (§7.ter.4.)
- Dirichlet L-functions, q ≤ 149, 630 primitive non-trivial characters,
  4.05M pooled spacings: bulk GUE, conductor-normalised γ₁ Sp/U
  separation at p = 0.001.  Consistent with Katz–Sarnak family
  symmetry predictions. (§7.ter.3.)
- Primes ≤ 10⁶ log-density unfolding: σ̂ = 0.048 [0.023, 0.073];
  twin primes ≤ 10⁷: σ̂ = 0.093 [0.068, 0.118]. (§7.ter.23 Tier 4.)

### Cortical-V1 application (the bulk of recent work)

These are the load-bearing findings from the Phase 22a–32a sweep on
two V1 substrates (CRCNS pvc-11 anesthetised macaque V1, Smith &
Kohn; Allen Brain Observatory Visual Coding Neuropixels awake mouse
V1).  Each has cleared the disciplines listed in parentheses; the
detailed per-finding map is in `EPISTEMIC_STATE.md`.

- **H1: OSI ↔ ks_gue_med.**  Cellular orientation selectivity
  correlates with the global level-repulsion class statistic.
  pvc-11 partial ρ = +0.720; Allen meta-fixed ρ = +0.363 across 12
  sessions (all positive sign).  *Disciplines: full-sequence
  surrogate, within-recording, within-SNR-tertile, cross-substrate,
  rate-stratified within-cell.*
- **F1/F0 ↔ rep_med substrate-systematic sign-flip.**  pvc-11 +0.388
  vs Allen meta-fixed −0.183 (12/12 sessions negative, all 4 Cre
  lines).  Hietanen 2013 spike-count-bias deflation ruled out.
  *Disciplines: full-sequence surrogate, rate-matched (3 methods),
  rate-stratified within-cell on both substrates, cross-substrate,
  Ibbotson 2005 phylogenetic-conservation deflation.*
- **H2 surviving population-event structure (triply bounded).**
  Population NNS structure on specific pvc-11 recordings survives
  the required Aitchison-null surrogate conjunction at 30/30 q-bands.
  Bounded to: (i) recording-wide aggregate (not local-cluster at any
  tested spatial scale, Phase 27 + Phase 28); (ii) two specific
  anesthetised macaque V1 recordings (Allen 12-session does not
  replicate at rate-matched); (iii) post-window-aware refinement
  (monkey1_natural_movie WINDOW_AWARE_LOCKED 8/10 windows,
  monkey2_gratings_movie WINDOW_MIXTURE 5/10).
- **DSI ↔ ks_gue_med.**  Direction-selectivity index correlates with
  `ks_gue_med` with *stronger* Allen magnitude (+0.269 vs pvc-11
  +0.223), biologically plausible given mouse V1's heavier direction
  selectivity.  monkey2 NOT_SIGNIFICANT, signal carried by monkey1
  + monkey3.
- **p=7 cross-substrate temporal-scope asymmetry.**  pvc-11
  spontaneous + gratings carry p=7 enrichment at full-recording
  scope (mean z = +2.22 spontaneous, monkey1_gratings z = +9.77).
  Allen awake mouse V1 carries p=7 enrichment at per-window scope in
  natural_movie_one (mean z = +3.49 across 4 Cre lines, 19/30 windows
  z>2).  Phase 32a ruled out stimulus content as the load-bearing
  axis (pvc-11 natural-movie per-window p=7 = NULL at mean z = −0.25,
  0/10 windows z>2).  Macaque-vs-mouse and anesthetised-vs-awake
  remain confounded; awake-macaque or anesthetised-mouse data
  required to disambiguate.  The cross-substrate axis is **prime-
  specific** — both substrates carry per-window p=2 enrichment
  during movies; p=7 is the substrate-systematic prime.

### Other physical and biological signal classifications

These are single-dataset classifications on small samples.  They
should be read as findings about the specific datasets tested rather
than as findings about those domains broadly.

- USGS earthquake catalog M ≥ 4.5: Poisson-clustered (mass<0.3 = 0.33),
  consistent with ETAS aftershock dynamics.
- Adamatzky fungal mycelium spike pool, 1,470 events: super-Poissonian
  (mass<0.3 = 0.65).
- Solar X-ray flares (NOAA GOES, M+ class): Poisson-clustered.
- Binance BTCUSDT trade timing (one trading day): essentially random
  (BL quadrant).
- EEG θ-band zero-crossings (PhysioNet EEGMMIDB, 32 subjects):
  mass<0.3 ≈ 0.001, **identified as bandpass filter artifact** rather
  than a property of the underlying neural signal.

### Synthetic calibrators

- Pure-class parameter recovery on Poisson, Wigner (β=1, 2, 4),
  periodic, and uniform_jitter signals: passes acceptance criteria
  (CI coverage ≥ 80%, median relative error ≤ 10%) at n_events ≥ 200,
  with Wigner classes requiring n_events ≥ 1000.

## Negative-elimination findings

A complete record requires the eliminations as well.  Each is a real
result; the absence of these from a publication framing would
overstate what the tool currently claims.

- **Kuramoto-class formalism does not match cortical V1.**  Across
  the canonical (K, σ) parameter space (Phase 30), real V1 / Allen
  data has no Kuramoto-match (156/160 well-powered rows; aggregate
  modal = BR_artifact uniformly).  Kuramoto per-window p-adic at
  q_max=200 is also null.  **Four-way joint null** across both
  engines and both timescales.
- **History-coupled GLM as H2 elimination target: FIT-CEILING.**
  24-cell grid (n_lags × bin_ms × variant) produces zero FIT-PROPER
  cells; canonical → kernel collapse, unconstrained → runaway with
  invariant kernel shape.  Methodologically untestable in the Phase
  25 model family.  Co-finding: V1 spike trains have positive temporal
  correlation beyond what linear spatiotemporal stim filtering can
  absorb.
- **H2 is not a local-spatial-cluster phenomenon at any tested
  scale.**  pvc-11 Utah array 400–600 µm (Phase 27): CONTRA-OHIORHENUAN.
  Allen Neuropixels <300 µm (Phase 28): SPATIAL-SCALE-DEPENDENT
  with the local 100–300 µm bin LEAST TR-structured.  Combined: H2
  surviving structure operates at supra-300 µm or is not spatially
  localized at all.
- **GRB 230307A 909 Hz QPO (Chen 2025): substantive fail.**  Targeted
  replication at the time-slice adjustment detects no signature
  distinguishing the published 45–47 s claim window from surrounding
  sub-windows.  The Phase 26 broadband-TR side-finding is a per-cell
  rate-regime feature of ARS classification, not energy-band sensitivity
  (falsified) or aspect-mediated.

## Known failure modes

The toolkit has been characterised to fail in these specific ways.

- **Continuous-trace inputs with peak-detection extraction.**
  `scipy.signal.find_peaks(prominence=0.3)` applied to autocorrelated
  continuous traces produces spacing statistics determined by the
  input's autocorrelation length, not by the underlying dynamics.
  Classifications on such inputs reflect the extractor. (§7.ter.19.)
- **Threshold-upcrossing extractors on near-iid input.**  Applied to
  iid exponential noise, threshold-upcrossing event extractors produce
  rep_int_q ≈ 0.34, which falls in the TR (Wigner-class) quadrant.
  Any TR reading from a threshold-style extractor must be cross-checked
  by applying the same extractor to noise of equivalent statistical
  character. (Finding F, §7.ter.23.)
- **rep_int_q is a signal-level scalar on stationary inputs.**  On
  continuous synthetic uniform_jitter inputs, the per-q variation in
  rep_int_q is at floating-point noise level (std ~10⁻⁴).  The joint
  plane is effectively 1D for inputs in the BR_artifact regime; the
  Ramanujan-Fourier amplitude axis carries the discriminative
  information when periodic structure is present. (§7.ter.22 amendment.)
- **σ̂ recovery describes the gap distribution position.**  For
  signals that are point processes by construction, σ̂ describes their
  gap distribution.  For signals extracted from continuous traces via
  peak detection, σ̂ describes the extractor's gap distribution.
- **Sample-size requirements vary by class.**  Wigner-class β̂
  recovery requires n_events ≥ 1000 for ≥ 80% CI coverage; other
  classes require n_events ≥ 200. (§7.ter.23 Tier 3.)
- **Integer-spacing structural confound.**  When the underlying t_k
  is integer-valued and dense, the minimum normalised spacing is
  bounded above zero by arithmetic, and mass<0.3 = 0 occurs for
  structural rather than dynamical reasons.  The diagnosis flag in
  `joint_q_profile` reports this when detectable.
- **q_max=30 is underpowered for absolute-threshold p-adic
  discrimination.**  Rate-matched Poisson surrogates pass the
  §7.ter.13 1.5× threshold 95.6% of the time at q_max=30.  Use
  matched real-vs-surrogate z-scores at q_max=30; absolute thresholds
  require q_max=200. (§7.ter.39.)
- **Rate-matched Poisson surrogate is necessary but not sufficient.**
  For sub-modal dynamics-vs-rate isolation, within-cell rate-stratified
  comparison is the required next discipline. (§7.ter.39.)
- **Per-cell rate-regime structure on non-stationary signals.**  On
  rate-evolving inputs (GRB lightcurves, BGP cascades), ARS
  classification has per-cell rate dependence that the standard
  rate-matched surrogate does not fully control.  Currently in
  capability-uncertain territory pending an explicit per-cell rate-
  matched discipline. (§7.ter.36.)

## Application to LLM internal states (canonical retracted-claim arc)

The toolkit was applied to transformer residual stream activations
and attention dynamics across four architectures (Qwen 2.5 3B,
Phi-3-mini-4k, TinyLlama 1.1B, Mistral 7B v0.1) and eight extractor
mechanisms.  After three rounds of artifact diagnosis (§7.ter.19,
§7.ter.22, Finding F at §7.ter.23), **no measurement was obtained
that could be attributed to the model rather than to the extraction
pipeline**.

This section is preserved as the canonical worked example of the
boundary-readout problem the tool is built to handle.  Provisional
findings retracted during development:

- Wigner-class classification on residual_norm_peaks: retracted as
  find_peaks autocorrelation rhythm.
- Cross-architecture σ̂ invariance: retracted as metric-blindness on
  integer-position event sequences.
- Wigner-class reading on three by-construction extractors at
  rep_int_q ≈ 0.34: retracted as threshold-upcrossing TR induction.
- "LLM and primes share a parameter-space neighbourhood within
  BR_artifact": retracted as extractor-conditional comparison.
- Two distinct LLM attention-dynamics families: retracted after
  three additional state-based extractors classified as BR_artifact
  consistent with all change-based extractors.

The negative result is bounded to the extractors and architectures
tested.  It does not generalise to RMT analysis of LLM weight matrices
(Staats et al. 2024; Martin & Mahoney 2018–2024), which uses different
methodology and is outside the scope of this work.

The arc terminating cleanly rather than continuing forever is what
differentiates this from the failure modes the frame is designed to
identify.

## How to use

See `METHODS.md` for the protocol, including calibrator-zoo
construction, extractor-invariance testing, and induction-on-noise
falsification.  See `RESULTS.md` for the chronological empirical
record under which each measurement was produced.  See
`EPISTEMIC_STATE.md` for the per-finding map of disciplines cleared
and outstanding.

Installation:
```
pip install -r requirements.txt
```

Minimal example:
```python
from arithmetic_toolkit import joint_q_profile, padic_amplitude_v4

# t_k is a sorted numpy array of event timestamps

# NNS engine: dynamics-class signal at recording-aggregate level
result_nns = joint_q_profile(t_k, q_max=200)
ks_gue_med = result_nns['ks_gue_med']
rep_med = result_nns['rep_med']

# RF engine: per-prime arithmetic-class signal
result_rf = padic_amplitude_v4(t_k, q_max=200)
p7_amplitude = result_rf['per_prime'][7]['normalised_per_q']
```

For any non-stationary-rate input, run rate-matched and
rate-stratified within-cell surrogates before interpreting either
engine's output.  For any surrogate-survival claim, specify scope
(full-sequence vs per-window).

## Related work

The Farey-rational-PLL framework is developed in:

- Planat, M. & Henry, E. (2002).  The arithmetic of 1/f noise in a
  phase-locked loop.  *Applied Physics Letters* 80(13), 2413–2415.
- Planat, M. & Rosu, H. (2002).  Ramanujan sums for signal processing
  of low-frequency noise.  *Physical Review E* 66, 056128.
- Planat, M. (2006).  Huyghens, Bohr, Riemann and Galois: Phase-Locking.
  *International Journal of Modern Physics B* 20, 1833–1850.
- Planat, M. (2026).  Painlevé Confluence and 1/f Phase-Locking
  Dynamics.  *Machine Learning and Knowledge Extraction* 8(3), 73.

Standard random-matrix-theory and adjacent references applied here:

- Bohigas, O., Giannoni, M.-J. & Schmit, C. (1984).  Characterization
  of chaotic quantum spectra and universality of level fluctuation
  laws.  *Physical Review Letters* 52, 1.
- Mehta, M. L. (2004).  *Random Matrices* (3rd ed.).
- Odlyzko, A. M. (1987, 2001).  On the distribution of spacings between
  zeros of the zeta function.
- Katz, N. & Sarnak, P. (1999).  *Random Matrices, Frobenius Eigenvalues,
  and Monodromy*.
- Dumitriu, I. & Edelman, A. (2002).  Matrix models for beta ensembles.
- Cramér, H. (1936).  On the order of magnitude of the difference
  between consecutive prime numbers.

Cortical-V1 literature specifically engaged by the Phase 22a–32a sweep:

- Hietanen, M. A., Crowder, N. A., Ibbotson, M. R. & Price, N. S. C.
  (2013).  F1/F0 spike-count bias.  *Neuroscience* 235.
- Ibbotson, M. R., Price, N. S. C. & Crowder, N. A. (2005).  F1/F0
  bimodality phylogenetic conservation.  *Journal of Neurophysiology*.
- Williamson, R. C., Cowley, B. R., Litwin-Kumar, A., Doiron, B.,
  Kohn, A., Smith, M. A. & Yu, B. M. (2016).  Factor analysis on
  pvc-11.  *PLoS Computational Biology* 12.
- Ohiorhenuan, I. E., Mechler, F., Purpura, K. P., Schmid, A. M., Hu,
  Q. & Victor, J. D. (2010).  High-order correlations in V1.
  *Nature* 466.
- Charles, A. S., Park, M., Weller, J. P., Horwitz, G. D. & Pillow,
  J. W. (2018).  Dethroning the Fano factor.  *Neural Computation* 30.

## Provenance

This toolkit was developed through extended dialogue with Claude
(Anthropic) without prior exposure to Planat's published work.  The
convergence on the Farey-rational-PLL framework occurred during
dialogue with a model whose training corpus included Planat's papers
from 2002 onward.  Subsequent reading of those papers (correspondence
with M. Planat, May 2026) confirmed that the analytical scaffolding
the toolkit implements was developed by Planat and collaborators over
the preceding two decades.  ARS is an applied implementation of an
existing framework, arrived at through an unusual transmission path;
it does not derive from those papers in the conventional read-then-
build sense, and it does not extend the framework analytically.

`WHYTHISEXISTS.md` includes a field-report section on what
AI-assisted independent research can and can't do, written from the
position of someone who built this project under those conditions.

## License

See `LICENSE`.
