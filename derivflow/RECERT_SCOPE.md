# Instrument re-certification — scope

**Opened 2026-09-10.** Trigger: `TAIL_AUDIT_2026_09_09.md`. The sealed Richardson readout is
biased over the k range that sets the fit windows, the bias is seed-class-dependent, and both
existing known-answer gates are structurally blind to it.

**Not yet authorised:** re-deriving any banked science. This scope covers the instrument only.
Stage 4 is where that decision gets made, with numbers in hand.

---

## How to read this document

Each stage below states its own ENTRY, EXIT and WHAT IT NEEDS FROM OUTSIDE. That is deliberate:
a stage should be resumable by someone — a later session, a subagent, Will in three weeks — who
has read only that stage and the artifacts it names, not this project's corpus. If a stage cannot
be picked up cold, the stage is written wrong, not the reader.

The organising principle is not topic. It is **where a claim can escape unchecked**:

| layer | guard | today's record |
|---|---|---|
| cell construction | `reachable.Bar` refuses unreachable bars; `compose` raises without an EXISTENCE arm; `modelparams` forces TESTED-or-DECLARED | zero failures |
| commit | `sealgen.sh` refuses staged outputs; `commit-msg` hook refuses unproduced CHECKRUN lines | zero failures |
| banked artifact | `verify_*.py`, board 47/47 | zero failures |
| **prose** | `verify_paper_numbers` — built 2026-09-09, one checker, one document | caught the de-link |
| **conversation** | none | **all three of today's errors** |

Every guard that exists fires at the moment of the act, and every one of them held. The three
wrong numbers I reported yesterday — the tail exponents and their ordering, the 36x sensitivity
ratio, the n-independence argument — were all made in the two bottom rows, where nothing refuses.
Documentation does not fix that layer, because consulting documentation requires already attending
to the thing you have forgotten. Refusals fix it. Stage 0 exists for that reason.

---

## Stage 0 — the missing gate (DO THIS FIRST; nothing else is interpretable without it)

**ENTRY:** none. Additive; touches no existing science.

**THE DEFECT IT ANSWERS.** Gate L is the picket fence, exactly periodic. Gate H is the Hermite
seed, near-crystalline. A bandwidth bias that acts equally on every gap is translation-invariant,
so in a gap-RATIO statistic it cancels identically on an ordered configuration — r-tilde is
unchanged when all gaps are scaled the same way. Both gates are therefore incapable of seeing this
defect class, which is why they were green throughout. Measured: picket readouts sit 4-6 orders
below the bias the audit found.

**GATE D — perturbed lattice, disordered, with an EXACT known answer at any statistic value.**
For gaps `s_i = 1 + eta*z_i`, z iid standard normal:

        1 - <r-tilde>  =  (2/sqrt(pi)) * eta       exactly, independent of window size

Verified numerically 2026-09-09: at eta = 1e-4 the statistic reads 1.122 / 1.129 / 1.130 / 1.128 /
1.128 e-4 at W = 200 / 800 / 3200 / 12800 / 51200, against a predicted 1.1284e-4.

Three properties, and it is the conjunction that matters:
  1. **Disordered** — a translation-invariant bias does NOT cancel, so the gate can fire.
  2. **Exact** — closed form, not a numerical reference that itself needs certifying.
  3. **Tunable to any value of the statistic**, including the 1e-5 regime where the tail lives and
     where the bias was measured. Gates L and H each pin one point; this one sweeps the axis.

**EXIT:** `knownanswer.py` exists as an importable guard module (sibling of `reachable.py`,
`railed.py`), exposing the configuration, the exact truth, and an assertion helper. It is
red-pathed: an injected bias of known size must make it FAIL, and the size it can detect must be
stated. A gate that has not been shown to fire is not a gate — that is the defect that produced
this scope.

**NEEDS FROM OUTSIDE:** nothing.

---

## Stage 1 — measure the bias surface

**ENTRY:** Stage 0 exit met.

**WHAT:** on Gate D, sweep bandwidth scale c and k. Report where the Richardson pair
`2F(eps) - F(2eps)` is valid and where it over-corrects. The audit's mechanism to confirm or
refute: at the sealed setting eps is 0.70-4.03 mean spacings, the raw S(eps) curve is
non-monotone with a minimum near 0.25-0.5 delta, and the pair over-corrects outside its O(eps^2)
regime. Independent reproduction required — the audit ran 9 iid replicates at n=1024 and single
replicates at n=2048/4096, which is not enough to bank.

**EXIT:** a bias surface over (c, k, statistic value), with the valid operating region stated as a
region, not a point. The current operating point marked on it.

**NEEDS FROM OUTSIDE:** `eps_rule_v15`, `reference_cdf` — both in `track0_iid_scaling.py`, both
read-only here.

---

## Stage 2 — choose the operating point, from the gate

**ENTRY:** Stage 1 exit met.

**WHAT:** pick the bandwidth rule from the measured valid region. The rule must be chosen by the
gate, not by convention and not by which value reproduces the banked numbers. State the new rule
and the residual bias it leaves at every k in the science range.

**EXIT:** a rule, a defence, and a bias budget. Gates L, H and D all re-run green under it — L and
H because the post-change protocol requires it, D because it is the only one that can see this.

**NEEDS FROM OUTSIDE:** a decision from Will if the valid region does not contain a rule that also
keeps Gates L and H green. That would mean the instrument cannot serve all three regimes and the
scope of the science has to shrink instead.

---

## Stage 3 — what moves

**ENTRY:** Stage 2 exit met.

**WHAT:** recompute, and report as a diff against banked, in this order:
  a. the fit WINDOWS. Converged GUE k=16 = 1.035e-3 and converged iid k=24 = 1.266e-3 are both
     above the 1e-3 floor, so both windows are expected to grow. GUE's grows more.
  b. the shape parameters and z, on the corrected windows.
  c. `k*`, the level crossing, which is the arc's declared comparison statistic.
  d. the tail exponents, which the audit puts at iid -2.489 +- 0.052 and GUE -3.0 +- 0.1 —
     opposite ordering to what was reported, GUE off by ~0.9.

**THE QUESTION THIS STAGE ANSWERS, and it is the only one that matters:** the sealed verdict is
that the seed classes DIFFER. The windows differ by class (16 points vs 11) because of a bias that
is itself class-dependent. Does `RATE-SEED-DEPENDENT` survive when both classes are read on a
commensurable window? Note the arc's own rule already applies: tau is degenerate with beta and is
not commensurable across windows, so the comparison belongs at `k*`.

**EXIT:** a diff table, and a verdict on the verdict.

**NEEDS FROM OUTSIDE:** nothing. This stage reports; it does not decide.

---

## Stage 4 — the decision

**ENTRY:** Stage 3 exit met.

**WHAT:** Will decides what the paper says. The precedent is on the record and is the same shape:
the v1 verdict was retracted at `c235861` when the protocol's own regression step found a
reference-grid aliasing artifact, re-certified, and re-adjudicated to
`INCONCLUSIVE-ON-INSTRUMENT-GROUNDS` before a grid amendment resolved it. That chain is
Appendix A of the paper and it is the paper's strongest section. This would be its second entry.

**NEEDS FROM OUTSIDE:** everything. Not a technical stage.

---

## Standing constraints

- Nothing in `paper.tex` is re-worded before Stage 3 exits. The Campbell letter's tail paragraph
  is already pulled; the rest of that letter stands on results this scope does not touch.
- The instrument change itself triggers the post-change protocol: gates re-certified before
  science is recomputed. That is what Stage 2's exit is.
- Per-replicate curves are now banked for the roster (`roster_stretch_error.json`); the dense-grid
  science still banks only stats(), so any per-replicate work at Stage 3 costs a re-run. Bank them
  this time.

---

# AMENDMENT 1 — 2026-09-11. What the first three stages found, and why Stage 2 changed.

Appended rather than edited in. The predictions above stay visible because half of
them were wrong, and which half is the useful part.

## Status

| stage | state | outcome |
|---|---|---|
| 0 — the missing gate | **DONE** `2110f9b` | Gate D built, red-pathed, on the board as `verify_knownanswer` |
| 1 — bias surface | **DONE** `89354ae` | `NO_RESOLVABLE_BANDWIDTH_BIAS_AT_THE_SCIENCES_OPERATING_POINT` |
| 2a — section sweep | **DONE** `3be4d7e` | `FLATNESS_IS_AN_ARTIFACT_OF_THE_CENTRAL_WINDOW` |
| 2b — finite reference | **RUNNING** `b8789f3` | — |
| 2 — choose an operating point | **OBSOLETE** | see below |
| 3 — what moves | **BLOCKED** on 2b | re-pointed, see below |
| 4 — the decision | unchanged | Will's |

`verify_recert` (`b93df29`) holds the series on the board: resolutions re-derive
from `knownanswer`, headline bars re-derive from their own surfaces, and the two
cells are checked against each other ACROSS artifacts.

## What was found

> **SUPERSEDED IN PART, 2026-09-13 — see `RECERT_CORRECTIONS.md` before quoting
> anything in this section.** An independent audit of this series' commit
> messages against its banked artifacts found twelve overstatements, all
> verified. Three of them are quoted below and are corrected there:
> **"+0.73%" is a noise draw** (~1 sigma, sign-flipping across eta; supportable
> statement is "no bias resolvable, |bias| < 0.79%"); **"+20.2% at 0.95"
> understates the artifact by 48x** (the same cell reads +965.94% at
> eps/Delta = 2.0, inside the science's own span); and **the "|pos| = 0.70
> boundary" is not an instrument property** but an eta- and bandwidth-contingent
> crossing of a relative resolution by a fixed ~2e-5 absolute offset -- it
> vanishes entirely at eta = 0.01 and must NOT be used to put a number on
> EDGE-0. The two VERDICTS below are unaffected and both stand.


**The bandwidth is not the defect.** Against a known answer on a disordered
configuration, the Richardson readout is biased +0.73%, identical at every
eps/Delta from 0.125 to 4.5. The raw and Richardson arms agree to every printed
digit -- there is no O(eps^2) bias here for Richardson to correct. The science's
whole operating span, 0.704 to 4.031, sits inside that.

**But only at the centre.** Sectioning (Will's proposal) found the bias varies by
21.8% across (position, size) cells. The inner two-thirds read true at every
window size; past |pos| ~ 0.70 of the half-support it degrades, reaching +20.2%
at 0.95. Stage 1's single central window could not have seen it.

**Which quantifies EDGE-0.** The paper ARGUES the edge is unreadable because
unfolding against a moving support endpoint does not define a local coordinate.
Stage 2a MEASURES where: the boundary is near |pos| = 0.70, not at the edge. The
science's own window (BULK_FRACTION = 0.20, centred) lies entirely inside the
clean region -- so this scopes the instrument without indicting banked numbers.

## Why Stage 2 as written is obsolete

Stage 2 said: "pick the bandwidth rule from the measured valid region." There is
nothing to pick. The surface is flat across the whole swept range at the centre,
so no bandwidth choice trades against another, and the valid region contains the
science's entire span. A stage whose job is to optimise a flat function has no
job. It is retired rather than quietly skipped.

## Stage 3, re-pointed

Stage 3 was written as "recompute the science and report a diff", on the
assumption that Stage 2 would change the operating point. It will not. So Stage 3
now depends entirely on 2b:

- **If 2b MEETS** (`THE_FINITE_REFERENCE_CARRIES_THE_COST`): the mechanism is
  reference accuracy, not smoothing. Stage 3 is then *fix the reference*, not
  *recompute the windows* -- and the fix is a different piece of engineering
  (more seed points, or a smoothed/analytic reference where one is available)
  whose cost must be scoped before anything is re-run.
- **If 2b MISSES** (`THE_FINITE_REFERENCE_IS_INNOCENT_TOO`): the audit's
  17%-271% has no remaining candidate in this family, and the honest next move
  is to reproduce the audit's own measurement directly on flowed configurations
  rather than on Gate D. That is a different cell again, and it should be sealed
  before it is run, not after the answer is known.

Either way, **the original Stage 3 question is unchanged and still the only one
that matters**: the sealed verdict is that the seed classes DIFFER, and their fit
windows differ by class (16 points vs 11) because of a bias that is itself
class-dependent. Nothing found so far touches that. It is not yet answered.

## One standing rule added, from five instances in three days

**Cross-cell values are READ from the artifact, never typed.** Stage 2a typed its
Stage-1 reference as `0.007265` and so carries four significant figures with no
source; `verify_recert` prints that on every board run rather than hiding it
behind a loosened tolerance. Same shape as `knownanswer._REL_SD_PER_ROOT_GAP`
(typed 0.0654, measured 0.905, wrong by 14x in the direction that OVERSTATES
sensitivity) and the hardcoded grid indices in Stages 1 and 2b. Every one was
caught by a guard rather than by reading the code.
