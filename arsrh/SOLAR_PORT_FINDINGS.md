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

### The merge-window bisection (reviewer's diagnostic) — the z is null-variance-limited, the signal is robust

Is the z=6.3 aggressive-merge row the honest number, or an over-merge amputating real fast
sympathetic flares? Bisected the merge window 0–30 min (`solar_merge_bisection.py`), decomposing z
into the GAP (obs mass03 − cycle-null mean) and the null_sd:

| gap (min) | 0 | 5 | 10 | 15 | 20 | 25 | 30 |
|---|---|---|---|---|---|---|---|
| **GAP** (obs − null) | 0.249 | 0.203 | 0.239 | 0.310 | 0.271 | 0.261 | 0.222 |
| null_sd | 0.0095 | 0.026 | 0.028 | 0.033 | 0.014 | 0.015 | 0.039 |
| z | 26.2 | 7.9 | 8.4 | 9.4 | 19.3 | 17.0 | 5.6 |

**The z swings (6–26) track the null_sd (4× swing), not the GAP — so z was never the finding.** But
"the GAP is flat" then has to earn being load-bearing, and two checks (`solar_gap_checks.py`, B=400,
z-free) re-grade it *down* from my first read:

| gap (min) | 0 | 5 | 10 | 15 | 20 | 25 | 30 |
|---|---|---|---|---|---|---|---|
| obs mass03 | 0.591 | 0.568 | 0.600 | 0.600 | 0.545 | 0.534 | 0.529 |
| null_mean | 0.342 | 0.364 | 0.354 | 0.290 | 0.273 | 0.277 | 0.305 |
| null p99 | 0.363 | 0.396 | 0.389 | 0.377 | 0.296 | 0.358 | 0.363 |
| **GAP** (±95% CI) | 0.250 | 0.204 | 0.246 | 0.310 | 0.272 | 0.257 | 0.224 |
| obs > null p99? | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

- **Check 1 — null_mean WANDERS** (0.273–0.364, range 0.090 ≫ its MC SE ~0.001). Since n barely drops
  (6608→5787, 12%), the null_sd 4× blowup is **rate-fit instability on the thinned catalog, not
  small-n** — so the null mean is drifting under the GAP, exactly the branch that says "the flatness
  needs a second look."
- **Check 2 — the GAP has REAL window structure** (spread 0.106 ≫ mean 95% CI 0.0024). The 0.310 at
  gap=15 is a genuine excursion, not noise. **So "flat GAP ~0.25" is wrong** — both obs and null
  drift and their difference varies ±0.05 with real structure. I was waving off 0.310 the same way
  both auto-verdicts waved off the z.
- **Z-free existence holds regardless:** obs mass03 exceeds the null's **99th percentile at every
  merge window** (no ratio, no sd), and the null is not heavy-tailed (mean ≈ median). **GAP floor
  (min across windows) = 0.204.**

### Quotable state — EXISTENCE with a magnitude FLOOR, no constant magnitude, no z

- *Survival-over-cycle* — earned, quote freely.
- *Intrinsic (beyond cycle AND catalog sub-flare artifacts)* — earned as an **existence claim with a
  floor:** observed mass03 exceeds the 99th percentile of a cycle-preserving null at **every**
  de-duplication merge window (0–30 min) and under the catalog's own `multipleID` grouping; the excess
  is **robustly positive, floor ≈ 0.20** in mass03. It is **not** a constant ~0.25 (both obs and null
  drift; the GAP has real window structure), and **no z is quotable** (the significance denominator is
  a rate-fit-unstable estimator, z spans 6–26 on that instability). **Fungal earned a magnitude; solar
  earns an existence with a floor.** Quote the p99-exceedance and the floor; never a z.
- Do **not** lean on the SOC check (same catalog, §(C) above).

**Specimen banked:** z is a ratio; a moving ratio does not tell you which of numerator/denominator
moved until you read the parts separately. Both auto-verdicts (mine "GAP shrinks", the reviewer's
"amputation") pattern-matched the noisy z to a *signal* story while the flat-then-structured GAP and
the wandering null_mean were sitting in adjacent columns falsifying both. Read a ratio's parts before
attributing its motion.
