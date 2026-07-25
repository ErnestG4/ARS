# ARS-RH Phase 3 — Σ² number variance: the orthogonal long-range witness (curvature-completed)

Prereg: `PHASE3_PREREG_SEALED.json`. **§0 BINDING:** instrument-corroboration of the Phase-1 finite-height
residual through a mechanistically-independent statistic; **NOT evidence about RH.** Artifacts:
`phase3_sigma2.py` (flat decoys + zeta), `phase3b_curvature.py` (curvature-matched decoys + zeta-low-γ),
`phase3_sigma2_measured.json`, `phase3b_curvature_measured.json`.

## Why Σ² — the real fragility was single-STATISTIC dependence

Every Phase-1/2 result lives in the r̃ family (matched-density null, flow control, σ-shape): one **short-range
adjacent-gap** statistic read through many clever nulls. Σ²(L) = Var of the level count in unit-mean-spacing
windows is **orthogonal in mechanism** — long-range rigidity, a different functional of the same spectrum. If it
finds the low-γ rigidity too, Phase 1 becomes two independent statistics agreeing; if clean, the residual is
characterized as short-range. Both outcomes substantive (sealed).

## The decoy battery had to be COMPLETED — flat decoys were insufficient (the load-bearing lesson)

Σ² requires unfolding, and the **general (empirical) unfolding** is the estimator whose verdict must generalize
(to Maass/neural) — so the bespoke θ-exact R–vM path is a **zeta-only ground-truth cross-check, never the general
path**. First pass (`phase3_sigma2.py`): flat Poisson/GUE decoys certified a low polynomial order (3). On zeta:

- **high-γ:** general and θ-exact **agree** (rel-err 0.002); Σ² sits below GUE, −2 to −7.5σ (long-range rigidity).
- **low-γ (the target):** general (order-3) and θ-exact **VIOLENTLY disagree — rel-err 9.08.** Order-3 Σ²
  *explodes* (2.878 at L=32, false anti-rigidity); θ-exact stays flat ~0.28 (rigid). The cross-check verdict
  literally printed *"DISAGREE → unfolding is the story."*

**Diagnosis:** the seal guarded against *over-smoothing* (too-high order → false rigidity). What bit was the
opposite — **under-fitting at low γ**: the flat decoys (Poisson, GUE central window) had no density curvature,
but zeta-low-γ has steep log-density; order-3 leaves a residual density trend → inflates Σ² at large L. **The
decoy battery spanned the rigidity classes but not the target's density CURVATURE.** The θ-exact cross-check is
the only reason this was caught instead of reported as a spurious low-γ anti-rigidity.

### Completion — curvature-matched decoys (`phase3b_curvature.py`)

Build GUE and Poisson on the **zeta-low-γ R–vM density backbone** (Phase-1 matched-density machinery; an
inversion-grid range bug in the first 3b attempt — grid capped below the block's γ-max — was found and fixed).
Require a general unfolding that recovers GUE=analytic **through the curvature** AND keeps Poisson≈L:

| method | GUE Σ² rel-err | Poisson ratio | verdict |
|---|---|---|---|
| poly5 | 0.61 | 1.00 | fail (still under-fits curvature) |
| **poly9** | **0.01** | **0.88** | **PASS** |
| poly13 | 0.03 | 0.87 | PASS |
| spline 1e-3 / 1e-2 / 5e-2 | 0.6–0.9 | **0.00** | fail (over-smooth → Poisson suppressed to 0) |

The splines fail on the **Poisson sentinel** (ratio 0.00 = the over-smoothing false-rigidity trap, made visible);
poly9 threads curvature-vs-over-smoothing. **The general-vs-θ cross-check on zeta then went 9.08 → 0.053 (AGREE):**
the completed battery certifies a curvature-adequate, generalizable estimator.

## ζ-low-γ verdict — MORE rigid than GUE at all scales (curvature-clean, general = θ)

poly9, vs a curvature-matched GUE-on-backbone band:

| L | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| ζ Σ² (general) | 0.309 | 0.348 | 0.344 | 0.295 | 0.288 | 0.301 |
| ζ Σ² (θ-exact) | 0.311 | 0.347 | 0.339 | 0.288 | 0.280 | 0.285 |
| GUE band | 0.345 | 0.417 | 0.491 | 0.572 | 0.643 | 0.717 |
| **(ζ−GUE)/sd** | **−4.5** | **−6.0** | **−10.9** | **−17.5** | **−14.9** | **−10.0** |

The *same block* read −4.5σ **anti**-rigid under the broken order-3 unfolding and −17σ **rigid** under poly9 — the
entire flip is the unfolding. Curvature-clean, general=θ (rel-err 0.053).

## What this corroborates — bounded, specificity held

- **The large long-range deficit is ζ's KNOWN Berry (1988) saturation** — present at high γ too (−7.5σ), stronger
  and earlier at low γ as the saturation scale shrinks with height. Correct instrument recovery, **not new**.
- **The corroboration of Phase 1 is real but bounded to the SHORT scale.** The short-L deficit (−4.5σ at L=1)
  points the *same direction* as r̃'s +2.4σ (ζ-low-γ more rigid than GUE at short range) and is **bigger at low γ
  than high γ (−4.5 vs −2.2)** — tracking the finite-height pattern. A mechanistically-different statistic
  independently finds the low-γ short-range super-rigidity. **Phase 1: "one statistic well-nulled" → "two
  independent statistics agree on the short-range finite-height rigidity."** It is **not** upgraded by the huge
  long-range numbers (known saturation, height-generic).
- **Sealed prediction: wrong again, same conservative direction — now 4-for-4** ([[sensitivity_specificity_decouple]]).
  I sealed "short-range-dominated → Σ² weaker/clean"; it shows strong multi-scale rigidity. Specificity HELD: no
  corroboration read until the curvature-complete general=θ agreement made it trustworthy, and it is bounded to the
  short-L finite-height-specific piece, not the known saturation.

## Verdict (in-scope, §0 maintained)

Σ² is now a **curvature-complete, decoy-gated, generalizable** long-range instrument that reproduces the bespoke
θ-exact path on zeta (rel-err 0.053). It finds ζ-low-γ **more rigid than GUE at all scales**; the long-range piece
is the known saturation, the **short-range piece independently corroborates the Phase-1 finite-height rigidity**
(same sign, height-tracking). Phase 1 now stands on **two mechanistically-independent statistics** at the short
scale — the single-statistic fragility is retired. **§0: none of this bears on RH.** **Verification status:**
reviewed against reported numbers, not independently audited; the decoy gate + general/θ cross-check are the
in-band self-checks. **Methodological banked lesson:** a decoy battery for an unfolding-dependent statistic must
span the target's **density curvature**, not only its rigidity class — flat decoys certify an estimator that
under-fits a curved target and manufactures a sign-flipped verdict; the ground-truth cross-check is what catches it.
