# 35b — transition_diagnostic non-circular validation on AM — FINDINGS (2026-05-17)

**Status:** SCOPING / arc-finish (tooling-confidence). Validated ratio-free
leg (61e11d5). No §3 adjudication, no stamping, Class II blocked. Verdict
is a Will adjudication (asymmetric-label + 5th harness-criterion mis-spec
this build-phase; surfaced not self-adjudicated, per pre-commitment).
Data: `run_35b_results.json`, `run_35b_log.txt`.

## What ran
Signal: AM λ∈{0.5,0.7,0.85,0.95,1.05,1.25,1.5,2.0} (brackets the proven
λ=1, EXCLUDED), θ=golden, φ=0, N=2584, rotnum-unfold L=1e6 → classifier →
characterize_transition. α-null (§7.ter.48 substrate-generated,
non-circular): fixed λ=1.5, vary α=φ over 8 values, same pipeline.

## Result (honest)

1. **No false positive — clean partial validation.** characterize_transition
   → `transition_detected=False` on BOTH signal and α-null. AM is
   `BR_artifact`-throughout (no quadrant transition exists); the diagnostic
   correctly did NOT manufacture one. transition_diagnostic does not
   false-positive a quadrant transition on a non-synthetic substrate whose
   transition is sub-quadrant. **This part validates.**
2. **Signal sub-quadrant is sharply transition-shaped at the proven λ=1:**
   rep_med two-plateau {sub≈0.84 (λ0.5–0.95) | sup≈0.69 (λ1.05–2.0)}, step
   exactly between λ=0.95 and 1.05; W1δ 0.005–0.029 → ~0.28 likewise.
3. **α-null is NOT flat at finite (N,L):** clean φ-PERIODIC oscillation
   (period 0.5; rep_med range ~0.05, W1δ range ~0.115). Ergodicity gives a
   flat α-null only as N,L→∞; at N=2584 the substrate-generated null
   carries its own finite-size φ-structure. Underestimated in the design.
4. **`UNRESOLVED` by the automated criterion.** Branch-(b) used max−min
   drift, signal≫5×null; ratio ~2.4× → not met. **max−min is the wrong
   discriminant** — conflates a *transition* (two-plateau monotone step)
   with a *periodic oscillation* (zero net shift). By shape: signal=
   transition at the known location; α-null=periodic-no-transition. Under
   a shape discriminant branch (b) is arguably met; under magnitude it is
   not. A verdict-criterion call → Will. (5th harness mis-spec this
   build-phase: max−min vs transition-shape. Pattern owned; surfaced, not
   spun, per pre-commitment.)

## For Will's adjudication
- Branch (a) quadrant-flip: not met (no flip — expected; AM BR_artifact ∀λ).
- No-false-positive sub-claim: cleanly met (diagnostic well-behaved).
- Branch (b) §7.ter.28 sub-quadrant: **shape-clear, magnitude-crude-criterion
  UNRESOLVED** — your call on the discriminant.
- Sharpening options (NOT auto-run; your steer): (i) higher N drives the
  α-null finite-size φ-structure → 0, opening the separation; (ii) a
  shape discriminant (sustained two-plateau step at the a-priori λ=1 vs
  periodic-no-net-shift) instead of max−min.

## Recorded, NOT interpreted (parked / out of scope)
The sharp signal rep_med/W1δ two-plateau step *exactly* at λ=1 is a
ratio-clean substrate measurement of the AM transition location; the
α-null's period-0.5 φ-structure is a substrate fact. Both are
§3/parked-arc, NOT discoveries — noted per the survey-the-horizon ethic,
not adjudicated.
