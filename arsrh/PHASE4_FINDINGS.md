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
  conclusion rests on that completeness, **not** on ⟨r̃⟩. **Grade of the structural argument, recorded:** the
  one-sequence-per-parity claim rests on **level-1 Maass spectral simplicity (multiplicity-one / no residual
  symmetry) — believed, not proven** (same provenance category as the RH-conditional reference curves). File it
  as the conditional it is; it does not weaken the result, but the argument is conditional, not certified.
- **parity=1 sits +2.27σ above pure Poisson** — mildly elevated. **This is a CANDIDATE explanation, not a
  bracket:** "the known finite-spectral-range departure of arithmetic Maass from exact Poisson" is an
  *attribution* I did **not** verify — I never checked the +2.27σ magnitude against a *predicted* departure
  (the way Berry saturation earned "excluded-because-known" by matching theory). Until that check is done it is a
  plausible label, not an established bracket. What IS solid: 0.4267 is firmly Poisson-side of the gap (≫ closer
  to 0.386 than 0.531), so it doesn't threaten the endpoint. And I sealed ~0.40 and got 0.43 — a **conservative
  point-estimate miss, same direction as the rest of the session** (see verdict: this makes it 5-for-5, not a
  confirm-known exception).

## Verdict (in-scope, §0 maintained)

**ENDPOINT CONFIRMED (the binary).** Both parity sectors of the level-1 arithmetic Maass spectrum classify
**Poisson**, GOE excluded at **7.3σ and 6.4σ**.

**The pooling decoy is the headline, not a footnote — a powered falsifier that FIRED.** Most of this arc's catches
were falsifiers *discovered to be inert* (the unfold test, etc.). This one demonstrated its power by **producing
the very artifact it was built to detect** — synthetic GOE pooled to 0.53→0.4297, a manufactured false-Poisson.
Because the false-positive mechanism was exhibited and the real spectrum was measured *outside* it (within-sector),
the per-sector result's specificity is **shown, not argued.** That is the reusable template
([[powered_falsifier_that_fires]]): a specificity guard earns its verdict when it can *construct* the confound it
rules out.

**Scope of what's retired, stated precisely (shared-source antibody applied to myself).** The brackets are
independent; the underlying **eigenvalue list is the same one** CP1 used. So this is **two independent analyses of
one dataset with a specificity guard the first lacked** — NOT two independent witnesses. What is retired:
**construction-artifact as an explanation for CP1's Poisson** (real, worth having). What is **not** retired:
anything upstream of both analyses — **extraction, list provenance, truncation/completeness.** Shared source is not
corroboration ([[null_excludes_only_its_confound]]); a second witness would require an independently-computed Maass
spectrum.

**Only the ARITHMETIC endpoint is certified, on real data.** The GOE "endpoint" here is a **hand-built synthetic
reference** (an instrument check), NOT a certification that actual non-arithmetic surfaces sit at GOE — that is
well-supported *elsewhere in the literature*, but nothing in this session measured it. So branch (i) (the
deformation **rate**) is **not** unlocked by "both endpoints certified." (i) has **TWO gates, design before
compute**: (a) **design** — does a matched interpolating null even *exist*? If Hecke-vs-generic is a hard binary,
there may be no interpolating family to match against, and (i) cannot clear its own specificity bar *regardless of
how much deformed-Maass data arrives* (this is the original objection, untouched by endpoint certification); and
only then (b) **compute** — the deformed-Maass eigensolve behind the 34f `DATA_ACQUISITION_BLOCKED` wall. Not this
phase.

**§0: none of this bears on RH; the Sarnak anomaly is established, and this is its instrument-corroboration.**

**Sealed prediction — binary CONFIRMED, point estimate MISSED (same direction — 5-for-5).** The Poisson-not-GOE
binary held (≥6σ). But the ⟨r̃⟩ *point* prediction (~0.40) missed to 0.4267 — a **conservative miss, the same
direction as the other four**, so the session's point-estimate lean is now **5-for-5**, and it **includes a
confirm-known task**. This run therefore does **not** evidence the discovery-vs-confirm-known refinement — it is
merely *compatible* with it. The simpler competing account — **the lean is general, and a coarse >6σ binary is
robust to a mild lean** — fits this data identically and is what the run actually supports. The binary survived
*because it was coarse*, not because the prediction was accurate. (Correction of an earlier overclaim that this was
"the cleanest evidence the decoupling diagnosis is right" — that was the file confirming itself on a point that
mildly contradicts it.) **Verification status:** reviewed against reported numbers, not independently audited;
bracket sanity + pooling decoy are the in-band self-checks.
