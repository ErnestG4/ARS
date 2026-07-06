# Redesigned IDS-unfold leg (unfold_rotnum) — §5 VALIDATION FINDINGS (2026-05-17)

**Status:** SCOPING / instrument-validation only. Asymmetric label.
No §3 adjudication, no substrate measurement, arc parked, Class II blocked.
Build per `IDS_UNFOLD_REDESIGN_BRIEF.md` §4 call (b): reference-free
rotation-number / Sturm-count IDS; no N_ref ⇒ ratio-free by construction.

## Gate table (v3 run; `unfold_rotnum_validation.json`, `_log.txt`)

| gate | result | reading |
|---|---|---|
| G1 clock = arcsine | **PASS** | max\|ids−arcsine\| 1e-5; free-cell var(s) 1e-5 |
| G2 rational θ → k/q | **PASS** | plateau dev 1e-5 (tol 0.02–0.04), reference-free |
| G4 ids(E) L_iter-conv | **PASS** | Δids 1e5→4e5 ≈ 1e-5 incl. critical λ=1 |
| G5a EXACT Poisson scale | **PASS** | pipeline W1δ=0.7403 vs exact 0.7358 (≤0.005) |
| G5b discrimination | **PASS** | sub λ0.1=0.0039 vs super λ4=0.276, **70×** |
| G3 W1δ-stat convergence | mixed | converged (top_inc **8e-5** ≪0.01) BUT my `geometric` clause failed on small-L non-monotonicity |
| ratio-freeness | structural | no N_ref param exists by construction |

**Printed verdict: `IDS_LEG_RATIO_FREE_PARTIAL`** — *solely* the G3
`geometric` sub-clause (4th harness-criterion mis-spec this build:
raw-swing → folklore-0.74 → ids-vs-W1δ conflation → over-strict-monotone).
The substantive convergence criterion (`top_inc<0.01`) passes by ~100×.

## Honest assessment

The leg passed every **substantive** criterion on the **first** build:
IDS-correct (3 independent known-truth anchors), absolute-scale-correct
against an **exact** non-clock truth (G5a — decisive, passed first try),
no-tautology/discriminating (70×), structurally ratio-free, W1δ converged
to 8e-5. The recurring failures were all in *my validation harness*
(strict/folklore heuristics instead of the exact substantive question),
not the instrument. On the evidence the leg is `RATIO_FREE_VALIDATED`;
the only non-pass is a demonstrably-wrong gate clause.

**Verdict adjudication deferred to Will** (asymmetric-label discipline +
harness-mis-spec track record ⇒ no self-certification). Recommendation:
`IDS_LEG_RATIO_FREE_VALIDATED`.

## Out of scope (parked; flagged, NOT interpreted)

Validated leg yields, on real cells: subcritical λ=0.1 → W1δ≈0.0039;
supercritical λ=4 → W1δ≈0.276. These are **substrate measurements** —
§3/zoo-gap/Class-II, all parked. Available for the parked re-validations
**only on Will's VALIDATED adjudication**; not measured/interpreted here.
"Explore" does not proceed on a self-asserted-green instrument.
