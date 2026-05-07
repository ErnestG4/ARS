# Progress log — Arithmetic Resonance Spectrograph (ARS)

Live running tally of analyses applied with the ARS analytical-NNS
pipeline.  Newest at top.  Older overnight-batch entries in
`OVERNIGHT_PROGRESS.md`.

For consolidated current results: `MORNING_SUMMARY.md` + `RESULTS.md`.

---

## 2026-05-07 12:54 — Fungal mycelium spike statistics ✅

`run_fungal_nns.py` applies analytical-NNS to 18 long electrical
recordings (Adamatzky / unconv-comp lab, *Pleurotus ostreatus* and
grain-substrate fruiting bodies, 60–360 h each, 8 differential
channels, 1 Hz).  Spike detection via 1-h rolling-median baseline
plus σ ∈ {3, 4, 6} threshold-cross, picking the σ that yields 20–150
spikes per channel (min ISI 120 s, min spike width 10 s).

**Pooled across 35 (file, channel) units, 1,470 inter-spike spacings:**

| metric        | value | reference (Poisson) | reference (Wigner GUE) |
|---------------|-------|---------------------|------------------------|
| KS_Poisson    | 0.400 | 0.022 (calibrator)  | —                      |
| KS_GOE        | 0.590 | —                   | —                      |
| KS_GUE        | 0.641 | —                   | 0.022 (calibrator)     |
| **mass<0.3**  | **0.654** | 0.259 (analytic) | ~0.10 (analytic)       |
| best          | Poiss | —                   | —                      |

**Headline**: fungal spike timing is **strongly clustered (super-
Poissonian)**, even more than earthquakes (mass<0.3 = 0.33).
65 % of normalised inter-spike intervals are shorter than 0.3 of the
mean — bursty point-process structure, no random-matrix universality.
KS_min = 0.40 is far above any clean-classification threshold, so the
"best=Poiss" label is the metric's most-charitable Wigner-form
neighbour rather than a real Poisson identification.

**ISI two-population check** (Adamatzky 2020 reports peaks near
2.6 min and 14 min): primary peak observed at 2.2 min (155 events,
broader and centred slightly earlier than Adamatzky's 2.6 min);
14-min peak much weaker (only 30 events in a ±2 min window vs 432
at the fast peak).  Mean ISI = 178 min inflated by long inter-burst
gaps; median ISI = 10 min matches the within-burst timescale.

A living network with no nervous system produces a clearly-clustered
point process, distinct from arithmetic level repulsion and distinct
from neural-bandpass quasi-periodicity artifact.

Outputs: `plots/29_fungal_nns.png`, `plots/30_fungal_isi.png`,
`data/fungal_results.json`.  Section §7.ter.5 in `RESULTS.md`.

---

## Cross-signal mass<0.3 ladder

Single-number summary of where each signal sits on the
clustering ↔ level-repulsion axis:

| signal class                | mass<0.3 | best  | KS_min | regime               |
|-----------------------------|----------|-------|--------|----------------------|
| Wigner GUE eigenvalues      | 0.10     | GUE   | 0.022  | level repulsion (calibrator) |
| ζ zeros (heights ~10⁶)      | 0.024    | GUE   | 0.012  | arithmetic level rep. |
| LMFDB EC L-functions        | 0.024    | GUE   | 0.012  | arithmetic level rep. |
| Dirichlet L (q ≤ 149)       | 0.016    | GUE   | 0.035  | arithmetic level rep. |
| EEG θ-band zero-crossings   | 0.001    | "GUE" | 0.18   | bandpass artifact     |
| Poisson process (calib.)    | 0.259    | Poiss | 0.022  | random (calibrator)   |
| USGS earthquakes M ≥ 4.5    | 0.33     | Poiss | 0.075  | weak clustering       |
| **Fungal spikes**           | **0.65** | Poiss | 0.40   | **strong clustering** |
| Mertens M(x) sign changes   | 0.93     | Poiss | 0.32   | sparse arithmetic seq |

---

For older overnight entries see `OVERNIGHT_PROGRESS.md`.
