# Arithmetic Resonance Spectrometer (ARS)

Python implementation of a point-process universality classifier based on the
Farey-rational phase-locked loop framework developed by M. Planat and
collaborators (FEMTO-ST, 2002–2026).

## What this is

A toolkit that takes a point process (sorted event timestamps) and classifies
its spacing statistics against a set of universality classes (Poisson, Wigner
GOE/GUE/GSE, periodic, uniform-with-jitter) by measuring passage-time
nearest-neighbour spacings through a bank of Farey-rational phase-locked
loops. The output is a fingerprint vector locating the signal in a 2D plane
defined by the repulsion integral and Ramanujan-Fourier amplitude, plus a
quadrant-diagnostic assignment.

A calibration and falsification protocol is included for distinguishing
classifications that reflect signal structure from classifications that
reflect extraction-pipeline artifact.

The framework's analytical content (Farey rationals as PLL natural
frequencies, the Mangoldt-function and Bost-Connes connections) is not
original to this codebase. ARS is an applied implementation; it does not
contribute new theoretical mathematics.

## What has been validated

These specific measurements have been reproduced at the precision indicated:

- Riemann ζ first 2,000 zeros at joint-plane resolution: KS_GUE = 0.041.
  Riemann ζ at heights ~10⁶: KS_GUE = 0.012–0.015. Consistent with the
  GUE conjecture and Odlyzko's tabulated zeros.

- Dirichlet L-functions, q ≤ 149, 630 primitive non-trivial characters,
  4.05M pooled spacings: bulk GUE classification, conductor-normalised γ₁
  distinguishing Sp from U at p = 0.001. Consistent with Katz–Sarnak
  family symmetry predictions.

- LMFDB elliptic curve L-functions, 87 curves, ~10,000 zeros: bulk GUE,
  edge separation by root number. Consistent with established
  characterisations.

- USGS earthquake catalog M ≥ 4.5: classified as Poisson-clustered
  (mass<0.3 = 0.33). Consistent with ETAS aftershock dynamics.

- Adamatzky fungal mycelium spike recordings, 1,470 events from 35 units:
  classified as super-Poissonian (mass<0.3 = 0.65) on the dataset tested.

- EEG θ-band zero-crossings (PhysioNet EEGMMIDB, 32 subjects):
  mass<0.3 ≈ 0.001, identified as bandpass filter artifact rather than
  spacing statistic of the underlying signal.

- σ̂ recovery on synthetic uniform_jitter signals: median relative error
  ≤ 10% across the calibrator family at n_events ≥ 200; CI coverage ≥ 80%.

- Pure-class parameter recovery on synthetic Poisson, Wigner (β=1, 2, 4),
  periodic, and uniform_jitter inputs: passes specified acceptance
  thresholds at n_events ≥ 200 (Wigner classes require n_events ≥ 1000).

These measurements reproduce statistics consistent with prior results in
the corresponding literatures. They are reported as instrument-validation
outputs. They do not extend those literatures.

## Known failure modes

The toolkit has been characterised to fail in these specific ways. Each
failure mode was diagnosed during development; details are in the indicated
RESULTS.md sections.

- **Continuous-trace inputs with peak-detection extraction.**
  `scipy.signal.find_peaks(prominence=0.3)` applied to autocorrelated
  continuous traces produces spacing statistics determined by the input's
  autocorrelation length, not by the signal's underlying dynamics.
  Classifications on such inputs reflect the extractor. (§7.ter.19.)

- **Threshold-upcrossing extractors on near-iid input.** Applied to iid
  exponential noise, threshold-upcrossing event extractors produce
  rep_int_q ≈ 0.34, which falls in the TR (Wigner-class) quadrant of the
  diagnostic. Any TR reading from a threshold-style extractor must be
  cross-checked by applying the same extractor to noise of equivalent
  statistical character. (Finding F, §7.ter.23.)

- **rep_int_q is a signal-level scalar.** On continuous synthetic
  uniform_jitter inputs, the per-q variation in rep_int_q is at
  floating-point noise level (std ~10⁻⁴). The joint plane is therefore
  effectively 1D for inputs in the BR_artifact regime; the
  Ramanujan-Fourier amplitude axis carries the discriminative information
  when periodic structure is present. (§7.ter.22 amendment.)

- **σ̂ recovery interprets gap distribution position in the calibrator
  family.** For signals that are point processes by construction (primes,
  ζ zeros, synthetic ensembles), σ̂ describes their gap distribution. For
  signals extracted from continuous traces via peak detection, σ̂
  describes the extractor's gap distribution rather than a property of
  the underlying signal.

- **Sample-size requirements vary by class.** Wigner-class β̂ recovery
  requires n_events ≥ 1000 for ≥ 80% CI coverage. Other classes require
  n_events ≥ 200. (§7.ter.23 Tier 3.)

- **Mixed-class spectral decomposition is partial.** Periodic-component
  identification via Ramanujan-Fourier peak detection works (4/4 cases on
  the test panel). Per-component class assignment via rep_int_q
  segmentation does not separate Poisson + uniform-jitter components in
  pooled mixed-stream data.

- **Integer-spacing structural confound.** When the underlying t_k is
  integer-valued and dense, the minimum normalised spacing is bounded
  above zero by arithmetic, and mass<0.3 = 0 occurs for structural rather
  than dynamical reasons. The diagnosis flag in `joint_q_profile` reports
  this when detectable.

## Application to LLM internal states

The toolkit was applied to transformer residual stream activations and
attention dynamics across four architectures (Qwen 2.5 3B, Phi-3-mini-4k,
TinyLlama 1.1B, Mistral 7B v0.1) and across eight extractor mechanisms.
After three rounds of artifact diagnosis, no measurement was obtained
that could be attributed to the model rather than to the extraction
pipeline.

Specific provisional findings retracted during development:

- Wigner-class classification on residual_norm_peaks: retracted as
  find_peaks autocorrelation rhythm (§7.ter.19).
- Cross-architecture σ̂ invariance: retracted as metric-blindness on
  integer-position event sequences (§7.ter.22 amendment).
- Wigner-class reading on three by-construction extractors at
  rep_int_q ≈ 0.34: retracted as threshold-upcrossing TR induction
  (Finding F, §7.ter.23).

The negative result is bounded to the extractors and architectures tested
above. It does not generalise to RMT analysis of LLM weight matrices
(Staats et al. 2024, Martin & Mahoney 2018–2024), which uses different
methodology and is outside the scope of this work.

## How to use

See `METHODS.md` for the protocol, including calibrator-zoo construction,
extractor-invariance testing, and induction-on-noise falsification. See
`RESULTS.md` for the empirical context in which each measurement was
produced.

Installation:
```
pip install -r requirements.txt
```

Minimal example:
```
from arithmetic_toolkit import full_analysis, joint_q_profile

# t_k is a sorted numpy array of event timestamps
result = joint_q_profile(t_k, q_max=200)
```

## Related work

The Farey-rational-PLL framework is developed in:

- Planat, M. & Henry, E. (2002). The arithmetic of 1/f noise in a
  phase-locked loop. *Applied Physics Letters* 80(13), 2413–2415.
- Planat, M. & Rosu, H. (2002). Ramanujan sums for signal processing of
  low-frequency noise. *Physical Review E* 66, 056128.
- Planat, M. (2006). Huyghens, Bohr, Riemann and Galois: Phase-Locking.
  *International Journal of Modern Physics B* 20, 1833–1850.
- Planat, M. (2026). Painlevé Confluence and 1/f Phase-Locking Dynamics.
  *Machine Learning and Knowledge Extraction* 8(3), 73.

Standard random-matrix-theory references applied here:

- Bohigas, O., Giannoni, M.-J. & Schmit, C. (1984). Characterization of
  chaotic quantum spectra and universality of level fluctuation laws.
  *Physical Review Letters* 52, 1.
- Mehta, M. L. (2004). *Random Matrices* (3rd ed.).
- Odlyzko, A. M. (1987, 2001). On the distribution of spacings between
  zeros of the zeta function. (Tabulated zeros and analyses.)
- Katz, N. & Sarnak, P. (1999). *Random Matrices, Frobenius Eigenvalues,
  and Monodromy*.
- Dumitriu, I. & Edelman, A. (2002). Matrix models for beta ensembles.
- Cramér, H. (1936). On the order of magnitude of the difference between
  consecutive prime numbers.

## Provenance

This toolkit was developed through extended dialogue with Claude
(Anthropic) without prior exposure to Planat's published work. The
convergence on the Farey-rational-PLL framework occurred during dialogue
with a model whose training corpus included Planat's papers from 2002
onward. Subsequent reading of those papers (correspondence with M. Planat,
May 2026) confirmed that the analytical scaffolding the toolkit
implements was developed by Planat and collaborators over the preceding
two decades. ARS is an applied implementation of an existing framework,
arrived at through an unusual transmission path; it does not derive from
those papers in the conventional read-then-build sense, and it does not
extend the framework analytically.

## License

See `LICENSE`.
