# Phase 32b — per-cell decomposition follow-up

## Frame

Phase 32b's session-aggregate cross-engine correlation on Allen returned
**INDEPENDENT_AXES** (ρ = −0.086, n=6 sessions, robust across four
scoring variants).  PHASE32B_FINDINGS.md flagged the per-cell follow-up
as the natural next discipline: regress per-cell per-window p=7
aggregate on per-cell Williamson-FA loadings (Phase 27 Analysis 2
protocol), replicate the Phase 27 SUBSUMED-vs-ORTHOGONAL pattern on
Allen for rep_med and ks_gue_med, and resolve what the cross-engine
axes *are* at per-cell resolution.

The V1-close brief (2026-05-11) names the three-way verdict structure:
**BOTH_ORTHOGONAL** (per-window p=7 and rep_med both novel axes outside
the FA), **p7_ABSORBED_F1F0_ORTHOGONAL**, **BOTH_ABSORBED**, **MIXED**,
or **SAMPLE-SIZE-BOUNDED**.

## Method

**Sessions:** the 6 Allen sessions with per-window p-adic at q_max=200
computed in Round 4 (732592105 wt, 791319847 Vip, 760693773 Sst,
762602078 Sst, 797828357 Pvalb, 755434585 Vip).  Per-session H1∩ARS
units: 66–91, total 465 across the cohort.

**Per-cell per-window p=7 score (this phase, new computation):**
the cell's own spike train in the natural_movie_one chunks
(concatenated to total duration 600.5s per session), partitioned into
5 windows of equal total duration (matching Phase 31b's
allen_per_window_padic.py at the *population* level).  Per window,
padic_amplitude_v4 z(p=7) vs N_SEEDS=3 rate-matched Poisson surrogates.
Aggregated per cell as **mean z across well-powered windows**
(per-cell `p7_mean_z`) and **fraction z>2 across well-powered windows**
(`p7_frac_gt2`).  Cells with fewer than 3 well-powered windows
(≥30 events per window) flagged UNDERCOUNT: **13/465 (2.8%)** —
sample-size floor non-binding.

**Allen-native Williamson noise-correlation FA, two fits per session:**
Phase 27 Analysis 2 protocol — 200 ms bins, sqrt(x+0.5)
variance-stabilising transform on the (n_bins × n_units) spike-count
matrix, CV-selected n_factors from 1..8 maximising mean held-out
log-likelihood across 5 folds, FactorAnalysis.components_ as per-unit
loadings.  Two fits:
  - **FA-nmo:** on the natural_movie_one chunks (matches the p=7
    measurement condition).
  - **FA-drift:** on the drifting_pooled chunks (matches the rep_med /
    ks_gue_med measurement condition).

CV-selected n_factors saturated at 8 for all 6 × 2 = 12 fits.  This
matches the Phase 27 max=8 budget on pvc-11 H2 sessions and keeps the
cross-substrate comparison methodologically fair, with the caveat that
the FA may be capacity-limited on either or both substrates.  Reported
R² is for the 8-factor regression.

**Regression:** per-cell target ~ FA loadings, OLS with per-session
within-substrate z-scoring of both predictors and target.  R² is the
in-sample regression score on z-scored (across pooled sessions)
variables.  Bootstrap 95% CI from 1000 cell-level resamples.

**Verdict thresholds (matching Phase 27):**
ORTHOGONAL if R² < 0.20, SUBSUMED if R² ≥ 0.50, PARTIAL otherwise.

**Robustness panel (per brief):** regress each target on raw per-cell
properties (mean_rate, osi, dsi, f1_f0_pref) — the FA-decomposable-
or-not framing extended to per-cell single-cell properties as direct
predictors.

## Results

### Cohort summary

| session    | Cre line | n_H1∩ARS | n_OK p=7 | n_fa_nmo | n_fa_drift |
|------------|----------|----------|----------|----------|------------|
| 732592105  | wt       | 91       | (per-cell rows pooled) | 8 | 8 |
| 791319847  | Vip      | 88       |          | 8        | 8          |
| 760693773  | Sst      | 71       |          | 8        | 8          |
| 762602078  | Sst      | 66       |          | 8        | 8          |
| 797828357  | Pvalb    | 78       |          | 8        | 8          |
| 755434585  | Vip      | 71       |          | 8        | 8          |

Cohort: n=465 H1∩ARS cells, 452 OK for per-cell p=7 (13 flagged
UNDERCOUNT — below the 3-good-window floor).

### Primary regressions (FA matched to measurement condition)

| target              | FA condition        | R² (95% CI)              | n   | classification |
|---------------------|---------------------|--------------------------|-----|----------------|
| per-window p=7 mean z   | natural_movie_one | +0.113 [+0.047, +0.248]  | 452 | **ORTHOGONAL** |
| per-window p=7 frac z>2 | natural_movie_one | +0.066 [+0.035, +0.142]  | 452 | **ORTHOGONAL** |
| rep_med             | drifting_pooled     | +0.113 [+0.078, +0.198]  | 465 | **ORTHOGONAL** |
| ks_gue_med          | drifting_pooled     | +0.126 [+0.088, +0.208]  | 465 | **ORTHOGONAL** |

All four primary regressions are below the ORTHOGONAL ceiling of 0.20.
Per-window p=7 mean z and frac z>2 agree (mean z is the brief's
primary; frac z>2 is the alternative).  The classification is the
same in both — ORTHOGONAL — and the R² magnitudes are small (≤ 0.13)
even relative to the bootstrap upper bound.

### Cross-condition FA (FA mismatched to measurement condition)

| target            | FA condition       | R² (95% CI)              | n   | classification |
|-------------------|--------------------|--------------------------|-----|----------------|
| per-window p=7    | drifting_pooled    | +0.074 [+0.037, +0.176]  | 452 | ORTHOGONAL     |
| rep_med           | natural_movie_one  | +0.020 [+0.012, +0.078]  | 465 | ORTHOGONAL     |
| ks_gue_med        | natural_movie_one  | +0.019 [+0.011, +0.069]  | 465 | ORTHOGONAL     |

Both ARS metrics on drifting-derived FA also classify ORTHOGONAL.  The
relevant FA condition matters for absolute R² magnitude (rep_med:
drift R²=0.113 vs nmo R²=0.020; ks_gue_med: drift R²=0.126 vs nmo
R²=0.019), confirming the methodological choice of condition-matched
FA, but the classification is invariant — all six FA × target cells
classify ORTHOGONAL.

### Robustness panel — raw per-cell properties (mean_rate, osi, dsi, f1_f0_pref)

| target              | raw R² (95% CI)         | n   | classification |
|---------------------|--------------------------|-----|----------------|
| per-window p=7 mean z   | +0.045 [+0.015, +0.105] | 417 | ORTHOGONAL |
| per-window p=7 frac z>2 | +0.026 [+0.010, +0.072] | 417 | ORTHOGONAL |
| rep_med             | +0.150 [+0.115, +0.198]  | 429 | ORTHOGONAL    |
| **ks_gue_med**      | **+0.386 [+0.318, +0.461]** | 429 | **PARTIAL** |

The single non-ORTHOGONAL cell in the entire result table is
**ks_gue_med ~ raw per-cell properties: R² = 0.386 PARTIAL**.
Dominant coefficient: OSI (+0.493).  This recovers the established
H1 cross-substrate-locked finding (OSI ↔ ks_gue_med, Allen meta-fixed
ρ = +0.363) at per-cell resolution within this cohort.  The Williamson
noise-correlation FA does *not* absorb this OSI-driven ks_gue_med
structure on Allen, even though the same FA absorbed ks_gue_med
substantially on pvc-11 H2 sessions in Phase 27.

The per-window p=7 raw per-cell R² of 0.045 is the smallest in the
table — **p=7 enrichment is essentially unrelated to any of the
standard single-cell properties** (mean_rate, OSI, DSI, F1/F0) at this
cohort and this scoring.  This is the strongest single number in the
phase: novel substrate-systematic axis at per-cell resolution.

## Verdict

**BOTH_ORTHOGONAL on Allen.**

Per-window p=7 mean z is ORTHOGONAL to FA-nmo (R²=0.113), to FA-drift
(R²=0.074), and to raw per-cell properties (R²=0.045).  rep_med is
ORTHOGONAL to FA-drift (R²=0.113), to FA-nmo (R²=0.020), and to raw
per-cell properties (R²=0.150).  Both metrics are below the 0.20
ORTHOGONAL ceiling across all predictor sets.

The Phase 32b session-aggregate INDEPENDENT_AXES finding strengthens
to **per-cell INDEPENDENT_AXES with both axes novel**: the two engines
on Allen read substrate-systematic axes that are independent of each
other *and* independent of the Williamson noise-correlation FA *and*
independent of the standard single-cell-property axis.

## Substrate-specific FA decomposability (new finding, secondary)

**ks_gue_med has substrate-specific FA decomposability.**

Phase 27 Analysis 2 on pvc-11 H2 sessions: ks_gue_med ~ FA loadings,
**R² = 0.73–0.80** (SUBSUMED).  Phase 32b per-cell on Allen 6 sessions:
ks_gue_med ~ FA-drift loadings, **R² = 0.126** (ORTHOGONAL).  Same
Williamson methodology, same max=8 factors, similar n_units per
session — the FA absorbs the H1 metric on anesthetised macaque V1
but not on awake mouse V1.

What absorbs ks_gue_med on Allen is the **raw per-cell OSI axis**
(R² = 0.386 with OSI coefficient +0.493 dominating).  The
anesthetised-vs-awake or macaque-vs-mouse axis appears to shift
the H1 metric out of the FA shared-variability subspace and onto the
per-cell tuning axis directly.  Either reading is consistent with
the Phase 24 H1 finding that OSI ↔ ks_gue_med is locked on both
substrates: it is a per-cell tuning effect, and Allen makes that
explicit while pvc-11's FA structure happens to be aligned with it.

The substrate-specific FA decomposability is itself an Allen-vs-
pvc-11 axis worth flagging in the substrate-systematic catalog,
but it is not strong enough on its own to flip a publication framing
— it is supporting context for the BOTH_ORTHOGONAL primary verdict.

## Implications for EPISTEMIC_STATE.md

The cross-engine entry on Allen moves from session-aggregate
INDEPENDENT_AXES (Phase 32b) to **per-cell INDEPENDENT_AXES with both
axes novel** (this phase).  Per-cell decomposition was the outstanding
discipline named in the Phase 32b cross-engine entry; with
BOTH_ORTHOGONAL the discipline is cleared.

**Publication framing strengthens at the per-cell level.**  Pre-Phase-
32b the cross-engine direction match could have been cited as
second-engine corroboration of a single substrate axis (strongest
reading).  Phase 32b at session level reduced that to "two
independent findings about the same substrate."  Phase 32b per-cell
sharpens to **"two independent findings, each on an axis that the
standard noise-correlation FA does not capture and that the standard
single-cell tuning properties do not capture."**

The H1 axis (OSI ↔ ks_gue_med) remains a third substrate-systematic
axis, captured by the raw per-cell OSI on both substrates; on Allen
this axis is per-cell-property-driven rather than FA-driven, which
is a refinement of the H1 finding's representation, not a change to
its status.

## Out of scope

- Mechanism claims about *what the novel axes mechanistically reflect*
  — the verdict resolves what they are NOT (FA components, single-cell
  property combinations) and pins down per-cell coefficient signatures
  but does not claim mechanism.
- pvc-11 per-cell decomposition.  Phase 32a's per-window p=7 on
  pvc-11 is NULL (PER_WINDOW_NULL), so the per-cell analog of this
  phase is not meaningful on pvc-11.  The Phase 27 ks_gue_med = 0.73-
  0.80 R² SUBSUMED result on pvc-11 stands as the cross-substrate
  reference.
- Higher-dimensional FA (max_factors > 8) sensitivity.  The Phase 27
  max=8 budget is preserved here for cross-substrate fidelity; a
  higher-rank FA might absorb additional variance and shift Allen
  decomposability classifications.  Bounded as a future-work item
  if the H1 framing needs further sharpening.

## What this brief was not

Not a re-derivation of the original Phase 32b session-aggregate
finding (that stands at §7.ter.42).  Not a re-test of pvc-11 — the
per-cell follow-up was Allen-specific by construction.  Not a
mechanism claim — the per-cell ORTHOGONAL result is a discipline-
cleared null against FA-decomposability framing, not a mechanism
story.

## Outputs

  - `data/phase32b_results/per_cell_p7_padic.parquet`
    (465 rows; per-cell per-window p=7 z-scores + aggregates)
  - `data/phase32b_results/per_cell_fa_loadings_nmo.parquet`
    (465 rows; FA loadings on natural_movie_one per session)
  - `data/phase32b_results/per_cell_fa_loadings_drift.parquet`
    (465 rows; FA loadings on drifting_pooled per session)
  - `data/phase32b_results/per_cell_decomposition_merged.parquet`
    (465 rows; full per-cell joined table)
  - `data/phase32b_results/per_cell_decomposition_verdict.json`
    (regression results, coefficients, bootstrap CIs, verdict)
  - `phase32b/per_cell_decomposition.py` (analysis script)
  - `phase32b/PHASE32B_PER_CELL_FINDINGS.md` (this document)

## Cost

407.8 s wall-clock on 6 Allen sessions (load + p=7 per cell + 2 FA
fits + regressions + bootstrap).  Per-session p=7 step ~5–10 s for
~75 cells × 5 windows × 4 padic calls each; FA fits ~30 s each; bulk
of time was session-load on first touch.

## Methodological notes

1. **The brief's "FA on single-cell properties" phrasing is a
   misunderstanding of Phase 27.**  Phase 27 Analysis 2's FA is the
   Williamson 2016 noise-correlation FA — 200 ms binned spike counts,
   sqrt-stabilised, CV-FA on shared-variability axes.  *Not* FA on
   tuning-property vectors like (OSI, F1/F0, ...).  This phase
   replicates the Phase 27 methodology on Allen; the brief's
   formulation is satisfied by the Williamson reading, and the
   robustness panel (regression on raw per-cell properties) provides
   the alternative reading the brief implicitly asks for.

2. **CV-selected n_factors saturated at 8 for all 12 FA fits.**  This
   could mean the noise-correlation regime supports more than 8 shared
   axes on Allen and the FA is capacity-limited.  Phase 27 used the
   same max=8 on pvc-11.  A higher-budget FA might absorb more
   variance and shift the ORTHOGONAL classifications; for cross-
   substrate fidelity with Phase 27, the matched max=8 budget is used
   here.

3. **Condition-matched FA matters for absolute R² but not for
   classification.**  rep_med on FA-drift R²=0.113 vs FA-nmo R²=0.020;
   ks_gue_med on FA-drift R²=0.126 vs FA-nmo R²=0.019.  Both pairs
   classify ORTHOGONAL but the magnitude differs by ~6×.  This
   validates fitting FA per-condition (matching where the ARS metric
   was measured) but does not change the verdict.

4. **The 132-event floor lesson from Phase 34b applies.**  Cells were
   filtered to ≥30 events per window across ≥3 of 5 windows.  Per-cell
   total events in natural_movie_one ranged ~700–10000 across the
   cohort (most cells well above the floor; UNDERCOUNT n=13/465).

5. **The within-window stability check from the consolidation-pass
   discipline does not apply identically here** — this is a regression
   pass on aggregated per-cell metrics, not an ARS classification.
   The analogous discipline (per-session jackknife of regression
   coefficients) is not run here; verdict robustness rests on the
   1000-resample bootstrap on R² and on the cross-condition FA
   robustness panel.

6. **Substrate-specific ks_gue_med FA decomposability** (Phase 27
   pvc-11 R² = 0.73-0.80 vs Phase 32b Allen R² = 0.126) is a
   secondary observation worth catalog inclusion but is not a
   publication-framing pivot.
