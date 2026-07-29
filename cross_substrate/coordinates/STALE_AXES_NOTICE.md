# ⚠ STALE AXES IN THIS COORDINATE STORE — read before using `I.8_brody_q` or `ARS.rep_med`

Marked 2026-07-27 during the propagation arc. **Nothing here is deleted; the entries are retained
so the record of what was computed survives.** But two banked axes in this store were computed on
the *pre-repair* deployed path and are **not** the quantities their names suggest.

## `I.8_brody_q` — computed with `bounds=(0.0, 1.0)`
**20,801 values across 46 substrates; 74.8% sit at a bound.** The fitter could not represent
clustering (q < 0) or GUE/GSE (q ≈ 1.5 / 2.0), so it returned the rail. Split by whether the
substrate was independently established as clustered:

| | n | at 0.0 | at 1.0 |
|---|---|---|---|
| neural (known clustered) | 15,107 | **13,773 (91.2%)** | 143 (0.9%) |
| other | 5,694 | 1,302 (22.9%) | 351 (6.2%) |

⚠ **q = 0.0 is ALSO the correct reading for a genuinely Poisson process**, so "at a bound" is an
*upper* bound on saturation, not a count of it. The neural row is confirmed saturation; the other
row is not. Repaired fitter: `cross_substrate.axes.I8_brody_q_unbounded`.

## ⚠ CORRECTED 2026-07-28 (R-173/R-175) — THIS NOTICE UNDERCOUNTED THE DAMAGE

This notice counted only the clip's **lower** rail (`exactly 0`). The clip **also rails HIGH**: when
R₂ ≡ 0 the integrand is 1.0 across the mask and the integral returns the **mask width, 0.85**.
Recomputed on kuramoto (6,298 cells, deployed values reproduced 6,298/6,298 first):

- **56.2% sit on the UPPER rail at exactly 0.85**, collapsing a true range of **+0.403 … +0.850**.
- **81.7% of cells change** under the repair; the clip inflates the mean by **24.6%**.
- **58 genuinely clustered cells were reported as REPULSIVE** (deployed median +0.2048 vs signed
  −0.6880; worst +0.1065 where the truth is −2.4622). **The opposite class, not just a lost
  magnitude.**

So "16.6% exactly 0" below is a floor on the corruption, not a measure of it. Repaired values for
kuramoto: `coordinates/kuramoto.repaired.jsonl` (`ARS.rep_med_signed`).

## `ARS.rep_med` — computed with the `np.maximum(0, ·)` clip
**8,106 values; 16.6% exactly 0.** For pvc-11 specifically: **median 0.0000, 79.2% exact zeros.**
Repaired field: `pair_correlation_full(...)["repulsion_integral_signed"]`.

## What does NOT rest on these entries — checked, not assumed
- **The n=7 clustering ⊥ coupling finding** (`CLUSTERING_COUPLING_FINDINGS.md`) is computed on the
  **repaired** signed `I_rep` over unit-mean-normalised spacings — its title says "on a repaired
  instrument" and its values are negative (−0.236 … −8.306), which the clipped field cannot produce.
  Its pvc-11 value is **−0.863** while this store's pvc-11 `ARS.rep_med` is **0.0000**: *different
  quantities under related names*. The finding's columns contain **no Brody axis at all.**
- **No class labels are banked here.** Zero entries carry an explicit GOE/GUE/Poisson/GSE label in
  `axes_computed`, so this store records **values, not derivations**, and no banked misclassification
  is demonstrated.

## So the honest status
**The coordinates are stale. The conclusions are not.** Anything reading these two axes out of this
store — landscape views, dashboards, `harvest.py` — is displaying pre-repair values. Recompute
through the repaired functions before using them for anything but provenance.
