# MORNING2 — second overnight run (honesty ledger)

Ran the remaining MORNING.md queue "start to finish." Honest framing: bounded session, jobs backgrounded with
checkpoints. Seeds 20240517. Failures at equal prominence.

## Task 1 (π depth-5 dimension) — ROOT CAUSE FOUND & FIXED; still NO bank (resolution)
The three prior Task-1 failures had a single, mundane root cause — **a floating-point bug in the potential**, not the
recursion and not "insufficient depth":
- `V_n = λ·χ_{[1-p/q,1)}({n p/q})` implemented as `frac >= 1 - p/q` drops the **boundary site to rounding**
  (`6·(1/7)=0.857…571` in float64 < `1−1/7=0.857…572`), so **every approximant collapsed to the free Laplacian**
  (1 band, edges exactly `[−2,2]`). Exposed by ground-truthing the trace vs an explicit 2×2 product: `V=[0,0,0,0,0,0,0]`
  where it should hold one λ.
- **Fix:** exact integer arithmetic `V_n = λ·[ (n·p mod q) ≥ q−p ]`. q=7 immediately resolved to **7 bands**.
- A second bug fixed too: level-0 = whole line poisoned the level-2 nesting parent.
- **Result now (integer potential + nested refinement, both fixes):** counts are in the right ballpark but not exact —
  λ=8: `7, 85, 106, 19684` (want `7,106,113,33102`); λ=24/32 lose even q=7's last gap (6, not 7). Dims land in (0,1)
  (0.60–0.73) but are **not banked** (band-count==q gate fails; under-resolved ⇒ mean-width biased). The registered
  `dim5<dim4` did NOT reproduce (0.72 vs 0.64 @λ=8) — but on under-resolved counts, so it's not a real measurement.
- **What's actually left (corrected diagnosis):** the remaining blocker is **adaptive bracketing of exponentially-narrow
  bands** — uniform grids miss sub-grid gaps. This is exactly where **Raymond-1995's per-parent child-band count is
  needed** (to know how many children to hunt in each parent and refine until found). So the hardened rule stands, but
  the FIRST blocker was the potential bug (now cleared). Task 1 is now a *resolution* problem with correct physics, not a
  mystery. Hardened rule reaffirmed: ground-truth the potential AND the trace before any deep run.

## Task 3 / D3 redo — DONE (previous exchange): semiconvergent sawtooth, 100% q_min prediction. (See MORNING.md.)

## Pending parameter turns — COMPLETE (`finish_morning_params.py` → `finish_morning_params.json`, ~85 min wall)
Consolidated driver imports the FROZEN refsuite functions with new params (no logic edits), writes to
`approximability/` (does not touch `mathtest/` tables), per-section try/except = checkpoint. All four sections ran.
Two clean passes, one phantom-escalate traced to a driver off-by-one, one estimator bug fixed on rerun. Honest ledger:

- **Part-I M=2000 → CLEAN HARD-PASS.** GUE Σ²(L=50) = **0.74269** vs closed form **0.74239** (SE 0.0013), `gue_hard_pass=True`;
  Poisson Σ²(L=50)=48.14. The M=200 soft-pass is now a hard-pass (SE shrank ~√10). **Bankable.**
- **3.5σ exceedance re-resolve → PHANTOM (no bias); resolved to a driver off-by-one.** The driver's inline
  `gk_tail(m)=log₂(1+1/(m+1))` = `P(a≥m+1)` (=12553) was WRONG; frozen convention is `exceedance(a,m)=count(a≥m)` with
  `gk_tail(m)=log₂(1+1/m)` = `P(a≥m)` (=**13750.35**). Against the correct frozen baseline the 10⁴-realization sample mean
  **13748.67** sits at **z=−1.53σ → regresses to theory, NO genuine bias.** The "escalate" was a self-inflicted baseline
  error (re-derived a constant instead of importing `exceedance_expected`). Driver fixed; `exceedance_reresolve_CORRECTED`
  in the json. *(Same class as the audit meta-lesson: re-derive constants, don't trust an inline reimplementation.)*
- **D1 λ→{128,256} → estimator bug FIXED, but pre-registered convergence gate FAILS honestly.** Original errored
  (`box_count_dimension` returns a 3-tuple `(dim,scales,counts)`; driver did `abs(dim_bs − whole_tuple)`). Fixed to `[0]`.
  Result: dim·lnλ = **{64: 0.8720, 128: 0.8858, 256: 0.8737}**, all within **±0.009 of DEGT ln(1+√2)=0.88137**, and the two
  estimators (box-count vs band-scaling) **agree ≤0.02 at each λ**. BUT the `non-increasing-distance-to-DEGT` gate is
  **FALSE**: λ=256 overshoots back under (dist 0.0094→0.0045→0.0077). Cause is resolution, not physics: λ=256's
  `max_valid_level` drops to **5** (vs 10 at λ=128) — bands go exponentially narrow so fast the nested refinement hits the
  stability boundary early ⇒ the λ=256 dim is under-resolved. **Same wall as Task 1.** So: DEGT bracketed by all three within
  1% (supports the limit), estimators agree, but **monotone convergence NOT demonstrated** — don't overclaim. `d1_lambda_ext_FIXED`.
- **Task 2 (π Khinchin trajectory) → RAN, two-precision-gated.** Two independent precisions agreed to **depth 51812**
  (~55k digits), so N=10⁵ is **honestly blocked** (json flags `"blocked": two-precision agreed only to depth 51812`) — the
  gate fired as designed. π running geomean **{100: 2.683, 1000: 2.663, 10000: 2.663}**, all **inside the Gauss-orbit 5–95%
  bands** at each N (bands tighten 2.26–3.25 → 2.64–2.74), tracking Khinchin K₀=**2.68545**. Exact controls correct
  (e→K=∞ spine, √2→2.0, golden→1.0). **Bankable** (π geomean-in-band up to N=10⁴; N=10⁵ deferred to a deeper-digit turn).

**Net param-turn ledger:** 2 clean banks (Part-I M2000 hard-pass, π geomean-in-band ≤10⁴), 1 phantom killed honestly
(exceedance off-by-one → no bias), 1 gate-fail-with-known-cause (D1 λ=256 under-resolved, DEGT still bracketed ±1%).
Nothing faked; both bugs were in MY driver, not the frozen refsuite; both are annotated `SUPERSEDED` in the json.

## Constitution
Gates fixed pre-launch, none changed. Task-1 band-count gate fired → no bank (not tuned). Integer-potential fix is a
correctness fix to MY panel-side code (`task1_pi_depth5.py`), NOT the frozen refsuite. Seeds logged; jobs checkpoint;
`MORNING2.md` written unconditionally. Nothing faked; the under-resolved Task-1 dims are labelled not-a-measurement.

## One-line status
Task-1 **root bug found & fixed** (free-Laplacian potential collapse) — physics now correct, counts in ballpark, but
band-count==q still needs adaptive bracketing (Raymond per-parent counts) ⇒ **no dimension banked, honestly**; param
turns **COMPLETE** — Part-I M2000 **hard-pass**, π geomean **in orbit-band ≤10⁴** (10⁵ two-precision-blocked), exceedance
"3.5σ" was a **phantom off-by-one** (no bias, z=−1.53σ vs correct baseline), D1 λ→{128,256} estimator-bug fixed but
**convergence gate fails** (λ=256 under-resolved; DEGT still bracketed ±1%); D3 semiconvergent redo **done** (prior).
Both param-turn bugs were in my driver, not the frozen refsuite; annotated `SUPERSEDED` in the json.
