# Solar flare surrogate port — the last load-bearing detection through the §3a wringer

Prereg: `arsrh/SOLAR_PREREG_SEALED.json` (sealed before running). The sharpest §3a test in the
program: solar M+X flare rate has a **~1000× solar-cycle envelope** (1 event/yr at minimum, 1865 at
maximum, 1986–2023), so the flagged clustering (deployed detector: 191/191 BL rows exact-0, commit
9ad46d6) could be *entirely* that rate modulation — a Cox confound — not intrinsic flare clustering.
Artifacts: `arsrh/solar_surrogate_port.py`, `solar_surrogate_port_measured.json`.

## The sealed prediction was WRONG — and that is the result

I sealed "**envelope-driven / weaker survival than fungal, plausibly does not survive**": the 1000×
envelope means most short inter-flare gaps come from high-rate solar-max periods, which a
cycle-preserving inhomogeneous-Poisson null reproduces. **The data overrode it.** The clustering is
**intrinsic — it survives the cycle-preserving null at every bandwidth tested.**

Rate-envelope-preserving null: intensity λ(t) by Gaussian-kernel smoothing the real onsets at
bandwidth *b*, then inhomogeneous-Poisson draws (preserves the solar cycle, destroys intrinsic
short-range clustering). Observed mass03 = **0.5968** (homogeneous-Poisson ref 0.259):

| kernel bw (days) | null mass03 | real z | null I_rep | verdict |
|---|---|---|---|---|
| 15 | 0.452 ± 0.014 | **10.2** | +0.58 | intrinsic |
| 30 | 0.409 ± 0.012 | **15.9** | +0.66 | intrinsic |
| 45 | 0.388 ± 0.011 | **19.6** | +0.68 | intrinsic |
| 60 | 0.376 ± 0.014 | **15.6** | +0.70 | intrinsic |
| 90 | 0.354 ± 0.011 | **21.5** | +0.73 | intrinsic |

**The honest object is the whole curve**, and it says two things at once:
1. **The solar cycle explains part of the excess.** The cycle-preserving null lifts mass03 from the
   homogeneous 0.259 to 0.35–0.45 — roughly *half way* to the observed 0.597. So a real fraction of
   the "clustering" the detector flagged *is* the solar-cycle rate modulation (the §3a confound is
   genuinely present, unlike fungal where the floor made things conservative).
2. **But the rest is intrinsic.** Observed 0.597 clears the cycle-preserving null by z = 10–21 at
   every bandwidth 15–90 days. There is substantial short-range clustering *beyond* the cycle — which
   is exactly what the SOC-phase ground truth says (M+X flares are intrinsically clustered;
   GK-declustering → Poisson). The two independent lines agree.

## The dormant clip bug does not threaten solar either — but for a different reason than fungal

The reviewer's near-zero-negative question: the cycle-preserving null sits at I_rep ≈ **+0.58 to
+0.73** (strongly repulsion-side, *far* from the near-zero-negative danger band), while real solar
reads I_rep = 0.000 (clipped — genuinely clustered, below the null). So real solar is clustered
relative to a null that is itself far from the clip boundary; the dormant clip does not fire here.

**Deployed `joint_q_profile` confirmation (the real code path, not the reconstruction):**

| | BL q-band rows | exact-zero | frac |
|---|---|---|---|
| **real solar** | 191 | **191** | 1.000 (reproduces the 9ad46d6 flag exactly) |
| cycle-preserving null 0 | 196 | 0 | 0.000 |
| cycle-preserving null 1 | 187 | 0 | 0.000 |
| cycle-preserving null 2 | 193 | 0 | 0.000 |

The deployed detector reproduces the banked **191/191** for real solar *exactly* (confirming the code
path is faithful), and gives **0 exact-zero** on the solar-cycle-preserving nulls. So on the real
detector: real solar is unambiguously flagged clustered, the cycle-preserving null is not, and the
dormant clip does not fire (the null is far from the near-zero-negative boundary). Both halves — the
mass03 survival *and* the deployed exact-zero behavior — are on the real code path, not a proxy.

## Verdict, stated with the confound named

Solar M+X flare clustering is **intrinsic — real beyond the solar cycle** (z = 10–21 vs a
cycle-preserving null, all bandwidths), *and* the solar cycle accounts for roughly half of the raw
excess. The flagged detection stands, now correctly separated into its rate-envelope part (real,
~half) and its intrinsic part (real, survives). This is the opposite of the sealed prediction, and
the sealed-then-falsified protocol is what surfaced it — the envelope confound was genuinely there
and genuinely insufficient to explain the signal.

**Caveats (honest scope):** (1) mass03 is the exact deployed statistic; the I_rep column is the
reconstruction (`pair_correlation_full`), and the deployed-`joint_q_profile` confirmation on the
solar null closes it on the real code path. (2) The bandwidth sweep is the result; a single bandwidth
would be the seal-threshold error one level down.

## ⚠ TWO CORRECTIONS (reviewer) — and the falsifying test, RUN

**(A) Fungal and solar are NOT the same strength — do not flatten "both through the wringer."**
On **fungal** the §3a confound was *absent*: mass03 sat far above every construction-matched null,
the Cox explanation ate nothing → **a clean detection.** On **solar** the confound is *present and
eats about half*: the cycle-preserving null lifts mass03 from the homogeneous 0.259 to 0.35–0.45
against observed 0.597 → **a residual detection, and the residual is the fragile kind.** "Survived
the confound" denotes two different epistemic states (confound-absent vs confound-present-
residual-survives); merging them is the eleventh-instance failure one level up, on the conclusions.
File them apart: **fungal = clean; solar = residual.**

**(B) The dedup was the FALSIFYING test for the intrinsic half, not a confirmatory footnote — and
it RAN.** The sealed prediction failed *because* the surviving signal lives at timescales shorter
than the cycle envelope reaches (burst timescale) — which is exactly and only where sub-flare
catalog over-segmentation lives. The cycle-preserving null cannot separate "intrinsic burst
clustering" from "catalog double-counting"; the two compete for the identical quantity. Recon
confirmed the danger: **44%** of short-ISI M+X pairs overlap in [tstart,tend], **34%** share a
`multipleID` (the catalog's own sub-flare group), and 9750 M+X rows carry only 7375 distinct
`multipleID`. So the caveat was load-bearing. Ran it (`solar_dedup_test.py`):

| onset list | n events | mass03 | cycle-null | z |
|---|---|---|---|---|
| raw | 9750 | 0.597 | 0.388 | 22.5 |
| **dedup by `multipleID`** (catalog's own sub-flare grouping) | 7375 | 0.615 | 0.386 | **26.1** |
| dedup by [tstart,tend] overlap-merge | 6608 | 0.591 | 0.341 | 28.8 |
| aggressive merge (≤30 min gap) | 5787 | 0.529 | 0.302 | 6.3 |

**Verdict: the intrinsic residual SURVIVES de-duplication** — under the catalog's own sub-flare
grouping (z=26) and physical overlap-merge (z=29). Removing the flagged duplicates does *not* kill
it: distinct flares still cluster in time (active-region / solar-storm temporal clustering, a real
phenomenon beyond sub-flare artifacts). So the reviewer's "confirmed or halved" resolves to
**confirmed** — but honestly: the **magnitude is dedup-window-sensitive** (z ranges 6–29; the
aggressive 30-min merge weakens it to 6.3σ, partly from fewer events). The intrinsic claim survives
in *sign* across every dedup variant; its *significance* is not robust to the merge window.

**(C) The SOC "independent ground truth" is NOT independent — corrected.** The SOC-phase flare
source is the **same** GOES Plutino catalog (`solar_flares_plutino_1986_2023.csv`; used by both
`run_phase13_solar.py` and the SOC pair). It inherits the identical over-segmentation, so its
agreement is *not* two witnesses — I overstated it above. The intrinsic claim rests on the dedup
survival (z=26 after removing the catalog's own duplicates), **not** on the SOC agreement.

**Quotable state:** *survival-over-cycle* — earned, quote freely. *Intrinsic (beyond the cycle)* —
now earned too, since it survives the catalog's own sub-flare dedup at z=26, **but** quote it with
the dedup-window sensitivity (z 6–29) and without leaning on the non-independent SOC check.
