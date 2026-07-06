# PHASE 35 SLICING — EXISTING-DATA T0 READ: FINDINGS

**What this is.** The first runnable item of the signed-off
slicing-comparison spec, on Will's explicit compute-go (2026-05-19,
"launch the first"). A **read** of the banked ratio-free sub/super W1δ
data (`sensitivity_confirm_results.json` — rotation-number leg, no
ref-N, N∈{50000,70000,100000}, λ_sub=0.5 / λ_sup=1.5, 16 φ∈[0,0.5),
L=1e5, golden θ) **reframed under the signed-off T0-Excise schema**. Not
a new eigensolve; no slate-2-numeric dependency; G1a-met. The
designation of this banked contrast as the T0 existing-data instance is
pre-registered and signed off (rev-3 §3; slate-2 §A: δ_max=0.5 is the
banked-continuity outermost rung) — a **sanctioned re-scoping, not a
silent purpose-violation**.

## Pre-registered (discriminant_exact_question_check)

- **EXACT QUESTION:** at the δ_max=0.5 rung, on the banked ratio-free
  data, is the sub-bracket (λ=0.5) vs super-bracket (λ=1.5) W1δ contrast
  significant against the §C α-ensemble floor — DISJOINT and gap ≥
  max(sub_spread, sup_spread) — per N∈{50000,70000,100000}?
- **CODED TEST:** the §C criterion VERBATIM (the signed-off slate-2 §C
  generalization of the validated `sensitivity_confirm` criterion)
  applied to the stored sub_spread/sup_spread/gap/disjoint. Not a new
  discriminant; not a re-run.
- **Honest terminals:** `T0_DELTA_MAX_SIGNIFICANT` (all N) /
  `T0_DELTA_MAX_NOT_SIGNIFICANT` (none) / `T0_DELTA_MAX_MIXED` (some).

## Result

| N | sub_spread | sup_spread | gap | §C-floor | gap − floor | disjoint | call |
|---|---|---|---|---|---|---|---|
| 50000 | 0.000292 | 0.122862 | 0.374969 | 0.122862 | **+0.252107** | True | T0-significant |
| 70000 | 0.000027 | 0.076560 | 0.177402 | 0.076560 | **+0.100842** | True | T0-significant |
| 100000 | 0.000146 | 0.007146 | 0.496135 | 0.007146 | **+0.488989** | True | T0-significant |

**TERMINAL: `T0_DELTA_MAX_SIGNIFICANT`** — uniform across all three N,
by a wide margin, disjoint everywhere.

## What this does and does not establish

**Does:** at the outermost rung δ=0.5, the T0-Excise treatment's primary
observable — the subcritical-vs-supercritical (AC-vs-PP) W1δ contrast —
is robustly above the substrate's *own* φ-ensemble noise (the §C floor)
at every N in {5e4,7e4,1e5}. The AC/PP spectral-type difference at fixed
detuning is real, not a substrate-φ-noise artifact, and ratio-clean (no
ref-N anywhere).

**Does NOT (ceiling — rev-3 §4 T0, stated, not hedged):**
- **Says NOTHING about the critical point.** T0 excises λ=1 and its
  whole neighbourhood by construction; this is the AC-vs-PP contrast at
  δ=0.5 only.
- **Is not treatment-robustness.** One rung, one treatment. Width-
  robustness (§B w-ladder), the inner δ-rungs, parts-to-whole, and
  cross-treatment (T1/T2/T3) are all separate and mostly G1b-/§3-held.
- **Does not inherit the banked `SENSITIVITY_VALIDATED_NON_CIRCULAR`
  verdict** — same numbers, a different (T0) question; the sensitivity
  verdict stays Step-1's, on its own footing.
- Instrument/methodology validation; asymmetric label; **not an AM
  discovery, not §3, not Class-II.**

## Status / next

The existing-data T0 read is complete and clean. Remaining runnable set
(each its **own separate compute-go**, Will's): outer-rung **new T0**,
**T2-core**. Held: T1 / T1′ / T2 N-refinement / **inner δ-rungs**
(pending the §D Fibonacci/DGY campaign); T3 (§3-(A)). Uncommitted —
commit is Will's call. brief-and-hold; nothing else runs; banked Step-1
untouched.
