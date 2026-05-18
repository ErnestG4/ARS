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

---

## Will adjudication (2026-05-18) — SPLIT verdicts, recorded SEPARATELY

§7.ter.28 entry pulled (not paraphrased). Its Phase-20 retroactive text:
"the diagnostic correctly returns origin==destination==BR_artifact at
quadrant-label resolution" + sub-quadrant rep_med variation is "at the
**limit** of the [diagnostic's] resolution … conducted on rep_med
trajectories rather than quadrant [labels]". ⇒ §7.ter.28 is a
PRECEDENT/PATTERN, **not a positive 'branch (b)' tier**.

Three verdicts, banked/scored independently (bundling would let the
unresolved half drag the solid half or borrow its credit):

1. **ZOO-GAP — UPGRADE BANKED.** Was "probably-robust, pending its own
   reference-check" (post-§Q3 cascade). Now **ratio-clean-confirmed,
   catch-2 CLOSED, the gap is real substrate.** Stands.
2. **35b NO-FALSE-POSITIVE — VALIDATED, banked, stands alone.**
   Non-circular: on AM (non-synthetic, mathematically-proven transition,
   sub-quadrant) the diagnostic correctly does not manufacture a
   quadrant flip; signal & α-null both correctly null. This **is an
   instance of the §7.ter.28 precedent itself** (confirmed by pulling
   the entry) — not a new tier, the pattern realised on a proven
   substrate. The framed payoff; banked regardless of (3).
3. **35b POSITIVE SUB-QUADRANT SEPARATION — NOT ESTABLISHED, live
   anchored candidate.** "Shape-clear-but-magnitude-crude" fails the
   no-eyeballing bar. Good candidate (sits at the *proven* λ=1, not a
   fitted location — anchored, not cherry-picked) but anchored ≠
   established. §7.ter.28 has no positive sub-quadrant tier and
   explicitly flags this regime as resolution-limited — *reinforces*
   candidate-not-established (the §Q3 lesson: "looks like structure" is
   where artifacts live). A clean positive separation would be a **NEW
   non-circular *sensitivity* result beyond §7.ter.28**, not a label
   §7.ter.28 confers.

5th harness-criterion mis-spec (max−min vs transition-shape) owned;
standing rule sharpened → memory `discriminant_exact_question_check`
("exact question or heuristic proxy?" pre-flight before any discriminant
runs).

## Sharpening run — Will's CONDITIONAL call (NOT run; awaiting)
Buys: the no-false-positive result is non-circular, but the diagnostic's
*sensitivity* (fires when it should) still rests on the circular
Phase-20.5 calibrators; a clean positive separation = the sensitivity
half on non-circular footing. Authorize iff non-circular sensitivity is
needed downstream; else banking (2) + logging (3) as candidate is a
legitimate stop ("does anything actually need this?"). **If authorized:
go EXACT** — the α-null's finite-N φ-structure IS golden-mean
continued-fraction structure, computable: characterize the α-null's
finite-N distribution *exactly* and test the signal against it at the
proven λ=1 (higher N helps drive φ-structure→0 but the clean path is
exact null-characterisation, NOT heuristic discriminant #6). No
untethered discriminant design.

---

## Sharpening run — SENSITIVITY_NOT_ESTABLISHED (2026-05-18; exact path; honest)

`sharpening_sensitivity.py` (exact α-null characterisation; first
application of memory `discriminant_exact_question_check` — pre-flight
recorded; methodology validated: period-0.5 confirmed to MACHINE ZERO
⇒ the dense [0,0.5) φ-grid is the EXACT finite-N α-null).

Data: subcritical λ=0.5 W1δ∈[0.0041,0.0087] φ-range **0.0046** (tight,
robust); supercritical λ=1.5 W1δ∈[0.255,**0.811**] φ-range **0.556**
(enormous exact φ-dependence). Ensembles **disjoint** (gap 0.246) BUT
the supercritical α-null's own φ-spread (0.556) > gap (0.246).

**VERDICT: SENSITIVITY_NOT_ESTABLISHED** (separate verdict; does NOT
drag/credit the banked ones). Substantive, not a criterion artifact:
non-circular sensitivity requires the regime signal dominate the
substrate-generated null's own structure; at fixed supercritical λ the
phase α alone moves W1δ by 0.556 > 2× the regime gap. (Weakening to
"disjoint⇒pass" rejected — that is the post-hoc criterion-softening the
new memory forbids.)

**New finding surfaced (honest):** prior supercritical sub-quadrant W1δ
(35b, zoo-gap recheck — both φ=0 only) were SINGLE-φ SLICES of an
exactly-φ-dominated quantity (0.255–0.811). Supercritical sub-quadrant
statistic = **α-dominated, NOT a substrate constant**; subcritical IS
tight. "sub≠super" holds **as disjointness only**; the supercritical
magnitude is not a substrate value.

**Touch analysis (split-verdict discipline):**
- Banked verdicts STAND: zoo-gap *ratio-clean-confirmed* (about
  ratio-cleanness — unaffected); 35b *no-false-positive* (quadrant-
  level; 35b itself φ-varied the α-null → all BR_artifact,
  transition_detected=False → φ-robust in its own data).
- One NEW open sub-question (NOT auto-adjudicated): the zoo-gap
  recheck's "BR_artifact everywhere" was φ=0-only; supercritical
  *quadrant*-verdict φ-robustness is unexamined. Does NOT retract the
  banked gap result (ratio-cleanness holds); honest caveat on the
  supercritical side.
- Lever (Will's call, NOT auto-run): higher N drives the α-null
  φ-structure → 0 (Will's earlier note); whether to pursue
  non-circular sensitivity that way is "does anything need it?".
