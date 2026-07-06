# Poisson-Pivot Falsification Calibrator · Findings

**Phase 36, 2026-06-01.** The rigidity-vs-clustering taxonomy
([[torus_transition_rigidity_vs_clustering]]) was sharpened last session to a PREDICTIVE claim: **Poisson is
the PIVOT where BOTH ARS axes go blind** — the repulsion axis is one-sided (resolves sub-Poisson/rigid,
collapses >=Poisson onto BL), the clustering axis lives on the super-Poisson side. A near-Poisson-throughout
transition should therefore be invisible to both, and was flagged as a buildable FALSIFICATION CALIBRATOR.
Built (`phase36/falsification_calibrator.py`), two arms, each able to come back POSITIVE (Will's guard).
Artifact-aware after the same session's mechanism correction: continuous-time, unit-mean spacings, single
renewal stream, NO grid/binning/high-rate pooling ([[pooled_rhythmic_repulsion_confound]]).

## Arm A — Gamma-renewal CV sweep THROUGH the pivot (positive control + pivot demonstration)
Single family, shape `k`, CV = 1/sqrt(k); N=4000, 5 seeds.

| k | CV | rep_med | quad | mass<0.3 | ks_Poi | ks_GUE |
|---|---|---|---|---|---|---|
| 4.00 | 0.50 | 0.340 | **TR** | 0.033 | 0.257 | 0.043 |
| 2.00 | 0.71 | 0.205 | TR | 0.120 | 0.144 | 0.093 |
| 1.50 | 0.82 | 0.131 | TR | 0.172 | 0.090 | 0.142 |
| **1.00** | **1.00** | **0.022** | **BL** | **0.259** | **0.012** | 0.218 |
| 0.75 | 1.15 | 0.002 | BL | 0.320 | 0.066 | 0.272 |
| 0.50 | 1.41 | 0.0005 | BL | 0.413 | 0.163 | 0.354 |
| 0.25 | 2.00 | 0.000 | BL | 0.567 | 0.342 | 0.501 |

The two axes **partition cleanly around the pivot**: repulsion `rep_med` decays monotonically
0.34 (sub, TR) -> 0.022 (pivot, BL) -> 0.0 (super); clustering `mass<0.3` rises monotonically
0.033 -> 0.259 (= Poisson baseline 1-e^-0.3) -> 0.567. **k=1 is blind on BOTH** (BL, rep at floor, mass at
baseline). Sub-Poisson side fires the repulsion axis (and Gamma(4) lands near the GUE form, ks_GUE 0.043 — a
genuine Wigner-class read); super-Poisson side fires the clustering axis with repulsion at BL. Exactly the
predicted structure. (Note: "clustering fires" is mass ABOVE the pivot baseline; the pivot sits AT baseline.)

## Arm B — NULL calibrator (the actual falsification): serial correlation at fixed Poisson marginal
Exponential marginals held EXACTLY (AR(1) Gaussian latent -> normal-CDF -> exponential inverse-CDF, so the
marginal is Exp(1) for every rho; only serial dependence changes). N=4000, 5 seeds.

| rho | rep_med | quad | CV | mass<0.3 | ks_Poi |
|---|---|---|---|---|---|
| 0.00 | 0.017 | BL | 1.007 | 0.262 | 0.012 |
| 0.30 | 0.0 | BL | 1.003 | 0.261 | 0.010 |
| 0.60 | 0.0 | BL | 0.997 | 0.260 | 0.012 |
| 0.85 | 0.0 | BL | 0.987 | 0.262 | 0.016 |
| 0.95 | 0.0 | BL | 0.975 | 0.255 | 0.028 |

A genuine dynamical transition (strong serial dependence at rho=0.95) is **INVISIBLE to both axes** — BL
throughout, CV~1, mass at baseline, ks_Poisson tiny. The test COULD have fired (if the NNS marginal-spacing
engine leaked serial-correlation sensitivity it would have); it did not. **Taxonomy holds — not falsified.**

## Verdict
**POISSON-PIVOT TAXONOMY CONFIRMED (positive control passes, falsification arm does not falsify).**
- The pivot (CV=1) is a genuine two-axis blind spot.
- The repulsion (sub-Poisson) and clustering (super-Poisson) axes partition the two sides of Poisson, monotone.
- A near-Poisson-throughout transition reads null on both — the instrument reads the MARGINAL spacing
  distribution and does not manufacture structure from serial correlation. (This also bounds ARS: a
  transition carried purely in temporal CORRELATIONS at fixed marginal is in the blind spot — addressability
  caveat, sibling of the manifold-geometry blind spot in [[ars_resolving_power]].)
