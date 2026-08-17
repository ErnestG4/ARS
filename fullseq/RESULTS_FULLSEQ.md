# RESULTS — Full-Sequence Holonomy (1-D dialect)

**Date:** 2026-08-17. **Brief:** `FULL_SEQUENCE_BRIEF.md` (Option B, rulings folded).
**Seal:** `fullseq/prereg_sealed.json` (2 files frozen; kill criterion sealed with named targets
and their margins recorded **before S0 ran**).
**Protocol arc — no new science claims; nothing under `cross_substrate/` or `survey/` written; no
banked row re-verdicted.**

## TL;DR — HIGHER_ORDER_MEASURED, and the pairwise table errs conservatively

The pairwise commutator table does **not** exactly bound full-sequence holonomy — but it fails in
the safe direction. The first-order predictor (sum of pairwise commutators at mid-stack dials) is
exact for single transpositions by construction, and **breaks at multi-inversion orderings with H
resolvable up to 10σ**. In every case **H > 0**, meaning the measured effect is *smaller* in
magnitude than the pairwise sum predicts: **composition is sub-additive, so the pairwise table is a
valid upper bound in this dialect.**

## The kill criterion did not fire

Sealed threshold: abort as NO_RISK if Δ_max < 0.201σ (= 0.1 × the smallest named margin,
brocot/golden at 2.01σ). **Measured Δ_max = 3.06 = 2.32σ** of the reference band — an order of
magnitude above the abort line. Reordering effects in the 1-D dialect are large, so the arc had
something to measure.

## S0 — the dials do move, which is what makes S1 meaningful

| transition | n | density | CV |
|---|---|---|---|
| T1 WINDOW | ×0.60 | ×1.00 | ×1.00 |
| T2 UNFOLD | ×1.00 | ×1.00 | ×1.00 |
| **T3 THIN** | ×0.70 | **×0.70** | **×1.55** |
| T4 RESCALE | ×1.00 | ×1.00 | ×1.00 |
| **T5 POOL** | ×1.50 | **×1.50** | **×1.46** |

Two of the five transitions move the dial variables materially (density and CV by 40–55%), so
evaluating a pairwise law at bare-substrate dials mid-stack **is** the category error the brief
named. The predictor below uses mid-stack dials throughout.

## S1/S2 — H(σ) is second-order in inversion count

| ordering | inversions | measured Δ | predicted Δ | **H** | z |
|---|---|---|---|---|---|
| T2T1T3T4T5 | 1 | −0.019 | −0.019 | 0.000 | 0.0 |
| T1T3T2T4T5 | 1 | −0.765 | −0.765 | 0.000 | 0.0 |
| T1T2T4T3T5 | 1 | −1.610 | −1.610 | 0.000 | 0.0 |
| T1T2T3T5T4 | 1 | −3.061 | −3.061 | 0.000 | 0.0 |
| T2T3T1T4T5 | 2 | −0.049 | −0.384 | **+0.335** | **+5.3** |
| T3T1T2T4T5 | 2 | −0.807 | −1.130 | **+0.323** | +2.9 |
| T3T2T1T4T5 | 3 | −0.365 | −1.149 | **+0.785** | **+10.0** |

The single-transposition rows are the **sanity floor** — the predictor is exact there by
construction, and returning exactly 0.000 confirms the machinery composes correctly rather than
confirming the law. The real test is the three multi-inversion rows, and **two of three are
resolvable at |z| > 3**, the third at 2.9.

**H grows with inversion count and does so faster than linearly** (0.33, 0.32 at 2 inversions;
0.785 at 3), consistent with a BCH-style expansion whose leading correction is quadratic in the
number of transpositions — the first-order term being exact for a single swap is exactly what that
expansion predicts.

**Mechanistically coherent:** both resolvable 2-inversion cases move **T3 (THIN)** to an early
position, and T3 is one of the two dial-moving transitions. Moving a dial-changing step earlier
propagates its effect through more of the downstream stack, which is precisely where a first-order
composition should break.

**Control clean:** ⟨r̃⟩ never fired (max |z| = 1.65 against a halt line of 3.0), so the effect is
not an instrument defect masquerading as holonomy.

## What this licenses, and what it does not

**Licensed:** the pairwise table's scope caveat can be **sharpened, not lifted** — pairwise
commutators do not compose exactly, but they compose *conservatively* at these magnitudes, so a
pairwise-derived bound is an upper bound rather than an estimate. That is a stronger and more
useful statement than the caveat it replaces.

**Not licensed:** this is one dialect, one sequence length, one substrate family, and a 7-ordering
sample. Sub-additivity is measured, not derived; a different dialect (especially one with
non-linear downstream steps like disattenuation or thresholding, which the brief flagged) could
compose super-additively. **No banked row is re-verdicted**: per the sealed rule, VERDICT_FLIP_RISK
licenses flagging, not re-running, because full-sequence canonicalisation is what this arc was
trying to establish and re-deriving under a mid-flight sequence would repeat the OP1 error at
pipeline scale. No flip risk arose in any case — the kill criterion's named margins (2.01σ, 6.60σ,
0.068 KS) all exceed the measured Δ in their own units.

## Reproduction

`fullseq/`: `transitions_1d.py` → `seal_prereg.py` → `run_fullseq.py` → `verify_fullseq.py`.

## Side cell — the survey-dialect kill criterion, banked as promised

Option A was not chosen as the arc, but its answer is cheap and belongs on the board regardless.
Bounding the full-sequence effect by the **sum** of the banked survey-dialect pairwise commutators
(C4 window↔project 0.00138 F-units, P3 weight↔thin 0.00223) gives **0.00361**, against a smallest
banked margin of **0.0624 F-units (1.97σ)** — a ratio of **17×**.

> **NO_RISK — pairwise is sufficient for everything currently banked in the survey dialect.**

Two labels on that, both required for it to be read correctly:

- **Transfer.** Using the pairwise sum as an *upper* bound relies on sub-additive composition, which
  this arc measured in the **1-D** dialect and did **not** measure in the survey dialect. It
  survives the transfer because each survey pairwise effect was separately measured *suppressed to
  within noise of zero*, so the sum is a sum of near-zeros rather than of real effects.
- **Size, stated honestly.** 17× is comfortable but **not unassailable** — composition would have to
  be super-additive by more than 17× in this dialect to close it, which is large but not absurd.
  (An earlier draft of the generator's docstring claimed "~2 orders of magnitude" before the number
  existed; corrected in place rather than left to flatter the conclusion.)

And the scope that matters for reuse: this says the pairwise table is sufficient for the survey rows
**as banked** — not that the survey dialect has no holonomy.
