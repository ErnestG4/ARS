# Rate-Robust Two-Axis Re-Audit · Findings (Phase 37, 2026-06-01)

## What happened
The first re-audit wave (Set 1) read per-cell **global CV** as the clustering magnitude and flagged ALL
neural per-cell substrates "100% clustered → AXIS-INCOMPLETE" at CVmed up to **16** (allen-hpf), 9 (CA1).
That was an artifact: global CV conflates fast burst-clustering with **slow rate-nonstationarity +
epoch-gap concatenation** (Allen "spontaneous" = scattered presentations pooled with absolute timestamps →
huge inter-epoch gaps). Diagnosed via the extractor (`np.concatenate` over scattered intervals) + magnitude
(CV 16 is implausible per-cell ISI dispersion).

## The fix
Added parameter-free **LOCAL irregularity** axes to `cross_substrate/axes.py`:
- **I.12_cv2** (Holt 1996): mean of 2|Iᵢ−Iᵢ₊₁|/(Iᵢ+Iᵢ₊₁) over adjacent ISIs.
- **I.13_lv** (Shinomoto 2003): local variation.
Both compare *adjacent* ISIs → robust to slow rate change by construction. Validated:
- synthetic: epoch-concat Poisson → global CV 10.9 but **CV2 1.00**; slow-drift Poisson → CV 1.84 / CV2 0.99;
  bursty → CV2 1.30; regular Gamma(4) → CV2 0.55.
- calibrator anchors: clock 0.00, uniform 0.20, GSE 0.42, GUE 0.55, GOE 0.69, **Poisson 1.00** (repulsion <1,
  pivot at 1).
**Wiring bug caught + fixed:** ports build their axis dict by iterating the `FAMILY_I` *dict* over
`canonical_spacings(spk)` (sorted/trimmed), NOT by calling `compute_family_I` — so axes needing raw
time-order returned None. Added `family_local(positions)` and merged it into all 7 per-cell ports +
calibration_anchors. Pass-1 re-verified bit-exact (deterministic axes unchanged; only I.9 Berry-Robnik
wobbles ~1e-2, proven to be fitter nondeterminism across identical-code runs, not the edit).

## Corrected result (CV2-primary; global CV = slow-structure contrast; %slowdrift = the artifact)
| substrate | n | CV2 | %clust | global CV | %slowdrift | verdict |
|---|---|---|---|---|---|---|
| CA1 (buzsaki) | 4019 | 1.224 | 77% | 9.18 | 21% | genuine fast-clustered |
| hc3 EC/CA3/DG | 923 | 1.204 | 65% | 1.92 | 21% | genuine fast-clustered |
| MEC (dr) | 1365 | 1.142 | 59% | 2.38 | 34% | genuine fast-clustered |
| allen-hpf | 4358 | 1.106 | 51% | **16.2** | **49%** | clustered but HALF slow-structure |
| retina (ret1) | 325 | 1.076 | 45% | 1.35 | 20% | near-pivot |
| V1 (v1-burst) | 7846 | 1.005 | 29% | — | 0% | **Poisson pivot** |
| ibl (partial, 4/8 sess) | 1141 | 1.017 | 18% | 1.33 | 22% | pivot (lean re-run pending) |
| calibration-anchors | 6 | 0.489 | 0% | — | 0% | repulsion anchors ✓ |
| dynamical-breadth | 17 | 0.101 | 0% | — | 0% | chaotic maps, rigid ✓ |

hc3 by region (CV2): **CA3 1.246 (74%) > EC 1.095 (49%) > DG 1.019 (38%)** — biologically coherent gradient
(recurrent CA3 burst-prone → sparse DG near pivot); CV2 discriminates regions where global CV (1.7–2.1) was
nearly flat.

## Interpretation (interface-readout framing)
- **The CV-16 "everything clustered" of the first wave was the artifact.** allen-hpf 16.2 → CV2 1.11 with 49%
  %slowdrift = the inflation was scattered-epoch concatenation, exactly as the synthetic predicted.
- **The corrected picture is a coherent GRADIENT:** hippocampal formation (CA1/CA3/EC/MEC/allen-hpf) is
  genuinely fast-clustering (CV2 1.1–1.25 = real complex-spike/burst dynamics, at HONEST modest magnitude the
  global CV overstated 2–7×); sensory cortex/retina/thalamus (V1/retina/ibl) sit at the Poisson pivot.
- **allen-hpf's flag is the weakest** (CV2 only 1.106, half the cells pure slow-drift) — the substrate whose
  recording structure (scattered spontaneous epochs) most invited the artifact. CA1/CA3 are the robust
  clustering-type substrates.
- These are re-audit POINTERS, not substrate-level verdicts. The genuine-fast-clustered flag on the
  hippocampal formation is the substantive, defensible output.

## ibl intervention
ibl's big-visual sessions (3× 2+GB, ~2500 units) wedged the wave 30+ min on >1M-event `joint_q_profile`
pooled reads (not CV2-relevant, and the wave#1 OOM-crash cause). Killed (exit 137) to unblock the
hippocampal arc; lean re-run on non-visual `sub-*.nwb` (phase37/lean_ibl.sh) recovers ibl per-cell CV2.
(A partial 4-session ibl read with CV2 1.017 was already written at 08:43 — consistent with the pivot.)

## Methodology banked
Global CV (or any unit-mean spacing-distribution magnitude) is **slow-structure-contaminated** for
per-cell trains spanning rate-nonstationary / multi-epoch recordings. Use **CV2/Lv (local, rate-robust)** as
the fast-clustering magnitude; report global CV vs CV2 divergence (%slowdrift) to expose the artifact rather
than hide it. Sibling of [[ars_rate_dependence_lesson]] and the Phase-33a epoch-gap lesson.
