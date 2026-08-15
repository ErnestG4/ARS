# RESULTS — Survey Arc (DESI DR1 LRG NGC, projected tomographic slices)

**Date:** 2026-08-15. **Brief:** `SURVEY_ARC_BRIEF.md` (approved, amendments folded).
**Seal:** `survey/prereg_sealed.json` (93ce1d7; 10 files blob-SHA frozen; null-model freeze
clause binding — the debugging window closed with the seal).

**Anti-claim (§0, verbatim by seal):** no cosmology inference; no statements about the 3D
matter field; no "hyperuniformity of the universe" claims in either direction; claims attach
to the projected 2D point process of each sealed slice, over the sealed scale range only.

## TL;DR — verdicts (per slice, via `verdict_lattice.resolve`, no flags raised)

| Slice | Verdict | Class | Exponent (F−1 ∝ L^s) | drift χ² |
|---|---|---|---|---|
| **primary 0.6–0.8** (n=533,955) | **CLASS_MEASURED** | **SUPER-Poissonian, 28/28 tiles** | **s = 1.190 ± 0.026** | 0.27 (clean power law) |
| **comparison 0.4–0.6** (n=346,761) | **CLASS_MEASURED** | **SUPER-Poissonian, 28/28 tiles** | **s = 1.190 ± 0.033** | 0.01 |

The §0.1 expectation registration (super-Poissonian at all sealed scales) is confirmed;
INSTRUMENT_HOLD never fired; no obstruction flag; zero tiles excluded by budget in either
slice (weight budget max observed dev 2.35% vs the 5% seal).

**Pooled F(L)** (mean ± tile-scatter SE over 28 tiles):

| L | primary | comparison |
|---|---|---|
| 0.1° | 1.384 ± 0.011 | 1.266 ± 0.010 |
| 0.2° | 1.891 ± 0.024 | 1.610 ± 0.021 |
| 0.5° | 3.607 ± 0.081 | 2.807 ± 0.069 |

**Inter-slice comparison row (descriptive, gateless by seal — physics, not drift):** class
identical (expected); amplitude lower in the 0.4–0.6 slice at every L; and the scaling
exponents agree to three digits (1.190 vs 1.190) — the projected clustering *amplitude*
evolves between slices while the *exponent* does not, at this precision. Filed as
observation; no gate, no interpretation. *Validity remark on the pattern (added at review):
slope-preservation under amplitude evolution is precisely the Limber-projection expectation
for scale-free clustering with fixed 3D slope and evolving amplitude — the gateless row read
the specific physics the per-slice lattice amendment was protecting, and the original
(pre-amendment) lattice would have gated on behavior the correct theory says must decouple.*

*drift χ² dof annotation (record ruling, too-good screen third application, first from the
too-good side):* the log(F−1)-vs-log(L) fit has 3 points − 2 parameters = **1 dof**; χ² of
0.27 and 0.01 against 1 dof are unremarkable (P(χ²₁ < 0.01) ≈ 8% — mildly lucky, not
suspicious). No conservative-error diagnosis needed; the adjacency effective-N statement is
not deflating anything at the sealed scales.

**Validity remark (cross-check, not inference):** s = 1.19 corresponds to an effective
angular-correlation slope w(θ) ∝ θ^−0.81 over the sealed range — consistent with canonical
LRG angular clustering, i.e. the pipeline's first science read lands where the literature
says a projected LRG process lives.

## Route comparison (descriptive Σ²-from-pcf, per sealed §11.3 division of labor)

F_pcf (from ĝ integrated over the exact square-cell pair-distance mass) reads systematically
below F_cells: 1.12 vs 1.38 (L=0.1°, primary), converging by L=0.5° (3.37 vs 3.61). **This
gap is constructional, not an obstruction:** the pcf route integrates ĝ only above the sealed
r_min = 0.05° (fiber-collision boundary; nothing quoted below it), while counts-in-cells see
all pairs including sub-r_min clustering. Same class sign in every row; the sealed
OBSTRUCTION_BANKED definition (class disagreement AND excess beyond envelope) correctly
stays silent. The gap's sign and its shrinkage with L are both as the r_min seal predicts.

## Gate record (all green before the data could answer anything)

- **Mask KAG (D1): PASS** after catching a real estimator-null bias on its first run —
  randoms-shot-noise term in cell expectations (+4%, algebraically forced at 25× randoms
  density) and weighted-pair effective-count z's. Fixed on synthetic, pre-seal, three-event
  labeled (`D1_LOG.md`). Red path: the forbidden analytic window manufactures F(1°) = 15–19
  (|z| = 130) — the standing quantitative answer to "just use a simple window" (TOOLKIT
  §11.1).
- **FIX-2 weights gate (D2): PASS** — powered wrong lens (injected gradient, expectations
  blind to it) fires at ≥5σ in every test tile (F(0.5°) = 2.5–3.1 vs right ~1.05); powered
  right lens within arms; **real-amplitude observation:** ignoring DESI's released weights
  shifts F by up to 4.47σ — weights matter at real amplitude, just under the firing line
  (the registered near-inert expectation was slightly conservative).
- **Projection twin** green at accepted-range declination extremes; **Q5**: randoms-backed
  MC geometry sufficient, no pixelized hybrid.

## Scope and boundaries

Claims bounded to: the projected 2D processes defined by the sealed slices, tracer (LRG),
footprint (NGC), weight model (released WEIGHT), scale range (Σ²: L ∈ [0.1, 0.5]°, capped
below the tile-edge interaction per the adjudicated D1 watch item; pcf: r ∈ [0.05, 1.0]°),
r_min = 0.05° (hardware-anchored; nothing below it, even descriptively). L = 1.0° re-enters
only via the sealed numeric extension rule (dry-run-verified) — not the front door.
Everything in brief §7 remains out of scope.

## Reproduction

`survey/` order: `acquire.py` (needs network; MANIFEST SHAs verify) → `run_mask_kag.py` →
`seal_prereg.py` → `run_d2_gates.py` → `run_d3_measure.py` (freeze check at start) →
`verify_survey.py` (live checker, nonzero exit on regression). FITS files local-only
(8.1 GB, gitignored; MANIFEST.json is the provenance record).
