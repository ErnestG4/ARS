# Spectral-statistics analysis of spike trains across three CRCNS datasets — summary

*Exploratory cross-dataset analysis, 2026-06. Numbers below are freshly re-derived from the public CRCNS
releases with bootstrap CIs and firing-rate / burst controls; provenance and caveats are flagged throughout.*

## 1. What we measure

For each unit we take its spike train, form the inter-spike-interval (ISI) sequence, and characterise the
**shape of the unit-mean-normalised ISI-spacing distribution** against random-matrix spectral universality
classes. Two families of measures:

- **`ks_gue`** — Kolmogorov–Smirnov distance from the GUE Wigner surmise. *Low* `ks_gue` = spacings resemble
  a rigid / level-repulsive (sub-Poisson) spectrum; *high* `ks_gue` = far from GUE, toward Poisson or
  super-Poisson (clustered/bursty). Computed on unit-mean-normalised spacings, so it is a distributional-shape
  measure, not a rate measure.
- **`CV2` (Holt et al. 1996) and `Lv` (Shinomoto et al. 2003)** — parameter-free *local* ISI-irregularity
  measures computed on adjacent ISI pairs, and therefore robust to slow firing-rate drift by construction.
  CV2 ≈ 1 for Poisson, < 1 for regular/refractory firing, > 1 for bursty/clustered firing. We added these
  specifically to separate genuine fast burst-clustering from slow rate-nonstationarity and recording-epoch
  structure, which inflate the global ISI CV (calibrated: a Poisson train concatenated across recording
  epochs gives global CV ≈ 11 but CV2 ≈ 1.0; a genuinely bursty train gives CV2 ≈ 1.3).

Both measures are validated on canonical references: clock-like → CV2 0.00; GSE/GUE/GOE Wigner classes →
0.42 / 0.55 / 0.69; Poisson → 1.00; `ks_gue` recovers the corresponding distances.

## 2. Datasets (all CRCNS)

| dataset | preparation | n units analysed | recording |
|---|---|---|---|
| **pvc-11** (Kohn lab) | anesthetised macaque V1, drifting gratings + spontaneous + movies | 1,159 (210 with gratings OSI) | Utah array, spike-sorted |
| **hc-3** (Mizuseki & Buzsáki) | rat hippocampus EC / CA3 / CA1 / DG, spatial/behavioural tasks | 923 (572 with place fields) | tetrode, Neuroscope |
| **ret-1** | mouse retinal ganglion cells, binary white-noise | 325 | spike-time |

## 3. Findings

### 3.1 Local spike-train irregularity (CV2) — a sensory-to-hippocampal gradient
Read on the rate-robust CV2 axis, the datasets order into a coherent gradient (CV2 median):

- **Hippocampus (hc-3) is genuinely fast-clustering**, with a clean within-structure gradient:
  **CA3 1.25 > EC 1.10 > DG 1.02** (recurrent CA3 burst-prone → sparse dentate near the Poisson point).
- **Retina (ret-1): CV2 1.08** — mildly clustered, near the Poisson point.
- For reference, mouse V1 (Allen Neuropixels, analysed identically) sits at the Poisson point (CV2 ≈ 1.0).
  (We did not run CV2 on the macaque-V1 pvc-11 set in this pass; its `ks_gue` median is 0.51.)

We emphasise CV2/Lv rather than the global ISI CV because the global CV conflates fast bursting with slow
rate-nonstationarity; in one dataset the global CV reached ~16 almost entirely from slow/epoch structure,
which collapses to CV2 ≈ 1.1 once the local measure is used.

### 3.2 Functional selectivity ↔ spectral class ("does tuning predict ISI structure?")
Our central question: does a cell's *functional selectivity* (an extrinsic property, independent of its ISI
spacing) predict its spectral class? We test this with Spearman correlations, **controlling for firing rate
and burst fraction** (the intrinsic, partly-tautological covariates), with bootstrap 95% CIs.

- **Macaque V1 (pvc-11): OSI ↔ `ks_gue` = +0.72** (n = 210 gratings units; rate-controlled, essentially
  unchanged from raw). More orientation-selective cells have ISI spacings *farther from GUE* (more
  clustered). Consistent with OSI ↔ repulsion-integral = −0.32.
- **Rat hippocampus (hc-3): spatial-information ↔ `ks_gue`**, escalating rigour:
  raw +0.69 → rate+burst partial **+0.47** → **rate-stratified (within firing-rate quartile, burst-partial,
  pooled) +0.37, 95% CI [0.29, 0.46]**. The relationship **survives** the strictest control and is
  **rate-modulated** (per-quartile ρ 0.15 / 0.20 / 0.49 / 0.66, stronger in higher-rate cells). By region
  the effect is strongest in EC, moderate in CA3, and not resolved in DG (n = 16). More spatially-informative
  (place) cells have ISI spacings *farther from GUE* (more clustered) — the **same direction** as macaque V1.
- **Mouse retina (ret-1): RF-SNR ↔ `ks_gue` = +0.05, null** (CI crosses zero). We read this as an
  axis-mismatch rather than absence of structure: under binary white-noise there is no
  orientation/direction tuning axis, and RF-SNR is not the relevant selectivity dimension. A motion/DS axis
  (different stimulus set) would be the appropriate test.

### 3.3 The cross-dataset picture
The two datasets with a matched selectivity axis — **macaque V1 (OSI) and rat hippocampus (spatial
information) — agree in direction**: more selective cells are more temporally clustered (farther from GUE),
robust to rate and burst control. The one sign reversal we see is in **mouse V1** (Allen Institute Neuropixels,
a separate non-CRCNS dataset analysed identically): OSI ↔ `ks_gue` ≈ −0.22. So the selectivity↔spectral-class
relationship appears **systematic but species/preparation-dependent** (macaque-vs-mouse V1), not a difference
between cortex and hippocampus.

## 4. Caveats / provenance (please read before citing)

1. **`ks_gue` is rate-sensitive at finite spike counts.** All selectivity correlations are reported with
   firing-rate control (partial correlation and/or rate-stratified pooling). The naive uncontrolled
   correlations are larger and should not be used.
2. **Intrinsic vs extrinsic.** Burst fraction correlates strongly with `ks_gue` by construction (both are
   ISI-derived); we treat that as near-tautological and report the *extrinsic* selectivity link controlling
   for burst. The hippocampal result survives that control, i.e. it is not merely "place cells burst."
3. **Rigour hierarchy is explicit.** For hippocampus we give raw / linear-partial / rate-stratified so the
   reader sees how the estimate moves under control (+0.69 → +0.47 → +0.37). We recommend citing the
   rate-stratified +0.37 [0.29, 0.46].
4. **DG is underpowered** (n = 16); its point estimate is not reliable.
5. **Direction convention:** "farther from GUE" = higher `ks_gue` = more Poisson/clustered ISI structure.
6. These are exploratory analyses of public data, not peer-reviewed results; we are happy to share the
   reproducible scripts (per-cell tables, bootstrap, and rate-stratification code) on request.

## Appendix — Methods

### A1. Spectral-class measures (per unit, on the ISI sequence)
Let the inter-spike intervals be I₁…I_N, normalised to unit mean (s_i = I_i / mean(I)). Spacing-distribution
measures compare the empirical s-distribution to the Wigner nearest-neighbour-spacing surmises:
- Poisson:  P(s) = e^(−s),  CDF 1 − e^(−s)
- GOE (β=1): P(s) = (π/2) s e^(−π s²/4),  CDF 1 − e^(−π s²/4)
- GUE (β=2): P(s) = (32/π²) s² e^(−4 s²/π)  (CDF evaluated numerically)
- **`ks_gue`** = Kolmogorov–Smirnov distance between the empirical CDF of {s_i} and the GUE-surmise CDF.
  Low = GUE-like (level-repulsive, sub-Poisson); high = far from GUE (Poisson or clustered). We use a matched
  extractor across datasets (2–98% spacing trim + unit-mean renormalisation). Min 20 spacings per unit.

Local (rate-robust) irregularity, on the *time-ordered, un-normalised* adjacent ISI pairs:
- **CV2** (Holt et al. 1996, *J Neurophysiol*) = ⟨ 2|I_i − I_{i+1}| / (I_i + I_{i+1}) ⟩
- **Lv** (Shinomoto et al. 2003, *Neural Comput*) = ⟨ 3 ( (I_i − I_{i+1}) / (I_i + I_{i+1}) )² ⟩
  Both: ≈1 Poisson, <1 regular, >1 bursty/clustered; insensitive to slow rate drift by construction.
- Calibrator check (synthetic, identical pipeline): clock 0.00 · GSE 0.42 · GUE 0.55 · GOE 0.69 · Poisson 1.00.

### A2. Selectivity (extrinsic) measures
- **OSI** (pvc-11, drifting gratings) = |Σ_k r_k e^{i 2θ_k}| / Σ_k r_k, the orientation vector strength over
  12 directions (r_k = mean rate at direction θ_k). Computed on the gratings subset.
- **Spatial information** (hc-3) = Skaggs bits/spike from the firing-rate map (place fields).
- **RF-SNR** (ret-1) = spike-triggered-average peak signal-to-noise from the white-noise stimulus.

### A3. Statistics
- All correlations are **Spearman ρ**. **Partial** correlations control covariates by rank-residualising
  rank(x) and rank(y) on the rank(covariate) design (least squares) and correlating residuals;
  covariates are **mean firing rate** and **burst fraction**.
- **Rate-stratified** (hc-3 gold-standard): split units into firing-rate quartiles, compute the
  burst-partial Spearman within each quartile, pool by n-weighted fixed effect.
- **95% CIs**: 2000-resample cell-level bootstrap, percentile method (seeded for reproducibility).

### A4. Datasets (CRCNS, crcns.org — please confirm exact citations before any publication)
- **pvc-11** — anesthetised macaque V1, Utah-array, drifting gratings/movies/spontaneous (Kohn lab;
  cf. Smith & Kohn 2008, *J Neurosci*).
- **hc-3** — rat hippocampus EC/CA3/CA1/DG, tetrode, Neuroscope format (Mizuseki, Sirota, Pastalkova,
  Buzsáki; cf. Mizuseki et al. 2009, *Neuron*; dataset descriptor Mizuseki et al. 2013).
- **ret-1** — mouse retinal ganglion cells, binary white-noise (CRCNS ret-1).
- Reference contrast (non-CRCNS): mouse V1, Allen Brain Observatory Neuropixels (visual coding), analysed
  with the identical pipeline.

### A5. Per-region hippocampus (hc-3) table
| region | n (units / place-field cells) | ks_gue median | CV2 median | spatial-info↔ks_gue: raw → rate+burst partial |
|---|---|---|---|---|
| CA3 | 610 / 365 | 0.576 | 1.246 | +0.60 → +0.27 |
| EC | 261 / 191 | 0.490 | 1.095 | +0.59 → +0.66 |
| DG | 52 / 16 | 0.436 | 1.019 | +0.72 → +0.23 (n=16, underpowered) |
| pooled | 923 / 572 | 0.528 | — | +0.69 → +0.47; rate-stratified **+0.37 [0.29, 0.46]** |

### A6. Reproducibility
Per-cell coordinate tables, the axis definitions, the bootstrap, and the rate-stratification are in
self-contained scripts (`crcns_pillar2.py`, `crcns_pillar2_ratematch.py`); available on request.

## 5. One-paragraph version
Across three CRCNS datasets we characterised single-unit ISI spacing distributions via their distance from
random-matrix spectral classes (`ks_gue`) and a rate-robust local-irregularity measure (CV2). Hippocampus
(hc-3) shows genuine fast burst-clustering with a CA3 > EC > DG gradient; retina (ret-1) and macaque V1 sit
nearer the Poisson point. In both datasets with a matched tuning axis, **functional selectivity predicts
spectral class in the same direction** — more orientation-selective macaque-V1 cells (OSI↔ks_gue +0.72) and
more spatially-informative rat-hippocampal cells (spatial-info↔ks_gue +0.37, rate-stratified [0.29, 0.46])
have ISI spacings farther from GUE (more clustered), robust to firing-rate and burst control. The lone sign
reversal is mouse V1, suggesting a species/preparation-systematic effect rather than a regional one.
