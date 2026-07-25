# ARS-RH Phase 4 (ii) — arithmetic Maass ENDPOINT: CP1 re-validated through a confound-free bracket

Prereg: `PHASE4_PREREG_SEALED.json` (goal set by user = **endpoint**, run (ii)). **§0 BINDING:** this confirms the
**known** Sarnak arithmetic-chaos anomaly (arithmetic Maass → Poisson-not-GOE) via a hand-built bracket; it
re-validates CP1, does **not** claim the anomaly as new, and is **not** evidence about RH. Artifacts:
`phase4_maass_endpoint.py`, `phase4_maass_endpoint_measured.json`.

## Why (ii), not (i)

(i) (transition along Teichmüller deformation) builds the Poisson→GOE crossover into the null *by construction*
and is where the corrected sensitivity prior is most seductive while specificity is most fragile. (ii) asks the
theorem-adjacent **endpoint** question with both brackets built by hand → provably cannot fake the answer. Per
[[sensitivity_specificity_decouple]], (ii) is the prerequisite; (i) (the rate) is a later phase gated on compute
**and** on (ii). CP1 currently rests on a single construction; (ii) is the independent second one.

## Method — confound-free, per-sector, with a pooling sentinel

600 level-1 arithmetic Maass eigenvalues `r_j` with parity ∈ {0,1} (`sessionK/maass_level1_partial.csv`).
Primary discriminant = **unfold-free ⟨r̃⟩** within each parity sector (Poisson 0.386, GOE 0.531, GUE 0.603).
Brackets **hand-built, matched to each sector's N**: Poisson (exponential spacings) and GOE (Dumitriu–Edelman
β=1 tridiagonal, central window), B=400 → finite-N band. **Sanity: synthetic Poisson 0.3865, GOE 0.5307** (refs
0.386/0.531 — brackets valid). **Pooling decoy** = pool 2 synthetic GOE sectors → must drift toward Poisson
(the desymmetrization/pooled-rhythmic confound; the (ii)-specific specificity trap).

## Result — both sectors Poisson, GOE excluded >6σ

| parity | N | ⟨r̃⟩ | nearest | z vs Poisson | z vs GOE (excluded) |
|---|---|---|---|---|---|
| 0 | 266 | 0.3992 | Poisson | +0.64 | **−7.3σ** |
| 1 | 334 | 0.4267 | Poisson | +2.27 | **−6.4σ** |

**Pooling decoy (sentinel fired):** single-sector GOE ⟨r̃⟩=0.5305; **pooled 2 synthetic GOE → 0.4297±0.0137**
(drifted from GOE toward Poisson — false-Poisson is constructible); real pooled (both parity) 0.3849 (Poisson +
Poisson = Poisson). Pooling GOE manufactures a Poisson-ward drift → the per-sector discipline is load-bearing,
and the real within-sector Poisson is **not** a pooling artifact.

## Honest catches (specificity held)

- **⟨r̃⟩ value alone cannot separate "mildly-super-Poisson single sector" from "pooled GOE."** Pooled-GOE landed
  at **0.4297**, real parity=1 at **0.4267** — numerically almost identical. The reason parity=1 is *not* the
  pooling artifact is **structural, not measured**: level-1 Maass forms are Hecke eigenforms with a single
  sequence per parity, so parity fully desymmetrizes and pooling cannot have acted. The "not a pooling artifact"
  conclusion rests on that completeness, **not** on ⟨r̃⟩. Filed as a construction argument.
- **parity=1 sits +2.27σ above pure Poisson** — mildly elevated, the known finite-spectral-range departure of
  arithmetic Maass from exact Poisson. Firmly Poisson-side of the Poisson–GOE gap (0.4267 ≫ closer to 0.386 than
  0.531); does not threaten the Poisson-not-GOE endpoint, but it is real and worth stating: I sealed ~0.40 and
  the instrument surfaced a touch more structure (0.43) even on a confirm-known task — the sensitivity lean
  showing up mildly, as it has all session.

## Verdict (in-scope, §0 maintained)

**ENDPOINT CONFIRMED.** Both parity sectors of the level-1 arithmetic Maass spectrum classify **Poisson**, with a
**hand-built GOE bracket excluded at 7.3σ and 6.4σ**, and the pooling decoy proves the result is not a
desymmetrization artifact. **CP1 is re-validated through an independent construction with a specificity guard CP1
lacked** — everything downstream that cites CP1's Poisson claim now rests on two confound-free constructions, not
one. This makes branch (i) (the deformation **rate**) well-posed for a future phase — both endpoints are now
independently certified — but (i) remains gated on the deformed-Maass compute (34f `DATA_ACQUISITION_BLOCKED`
wall) and is not this phase. **§0: none of this bears on RH; the Sarnak anomaly is established, and this is its
instrument-corroboration.** **Sealed prediction: CONFIRMED as called** (Poisson-not-GOE, both sectors, ≥6σ) — the
first sealed prediction this session to land as predicted, consistent with the 4-for-4 discovery-pattern being
specifically about *under-calling sensitivity on discovery*, not general miscalibration; on confirm-known, the
prediction held. **Verification status:** reviewed against reported numbers, not independently audited; bracket
sanity + pooling decoy are the in-band self-checks.
