# PHASE 35 SLICING-COMPARISON — SLATE UNIT 1: §4 CANDIDATE ROWS (DRAFT)

**Status:** DRAFT for Will's rev-2 §4 cut. Produced *in parallel now*
(Will 2026-05-19) against slicing-brief rev-1 + the **ratified G1-split**
(G1a-met / G1b-open / G2-met). This is a reviewable pre-registration
artifact — **NOT a run; brief-and-hold; uncommitted.** The matrix and
its rows are **Will's to cut / add / fix** — authored-for-review, not
signed off (the §Q3 lesson: authored-and-unreviewed pre-registration is
hollow; the *spec*, not a number, is what Will reviews). **Numbers
(scale ratios, excision widths, floors) are deferred to slate unit 2.**
Gate-language here is rev-1+split (pre-rev-2) and gets the agreed light
reconcile pass once rev-2 is cut. No §3 adjudication; T3/reverse-coupling
annotated, not adjudicated. BAR rider carried throughout: every
Fibonacci/DGY known-truth check below is **instrument-fidelity only, NOT
Fib→AM substrate transfer.** Asymmetric labels — these are *treatments*,
never "AM characterized."

---

## 1. Proposed §4 schema change — operationalize the G1-split rider

rev-1 §4 has one `Gate` column. The split established the membership
rule: **any row gets the question that split G1 — which axis does it
vary, is that axis cleared?** Propose replacing the single `Gate` column
with two, from which the **graded** gate column is *derived* (not
asserted), making graded gating per-row auditable:

| New column | Content |
|---|---|
| **Varied axis** | the axis the row varies to make λ=1 enter the comparison (the thing whose cleanliness the split interrogates) |
| **Axis-clearance → inherited gate** | the axis's clearance *status* and, if open, *which gate it inherits* — `G1a-met` / `G1b-open(inherits G1b)` / `G2-met` / `§3-(A)-gated` / `terminal-open` |

The rev-1 "graded gate" column is then the **derived** read of the
second column ("unblocks now" ⇔ no open-axis inheritance; "holds" ⇔
inherits an open gate). The membership test for *any* new row Will adds
is exactly column 2: a row with no honest axis-clearance answer is not
admissible. This makes Will's rider the matrix's admission rule, in the
schema itself.

---

## 2. rev-1 rows T0–T3, audited under the new columns

(Not new rows — the brief's own rows, annotated under §1's schema so the
graded column is auditable. Surfacing one substantive correction in T2.)

| Row | Varied axis | Axis-clearance → inherited gate | Derived gate |
|---|---|---|---|
| **T0 — Excise** | λ across a declared excision gap, **at fixed N**; the excision-neighborhood **width is a declared sub-axis** (the named "tuned-to-result" risk ⇒ width is pre-registered as a ladder, never free) | λ@fixed-N is exactly what no-FP exercised on the ratio-free leg → **G1a-met**; no vary-N. Width-sub-axis declared, not a gate | **Unblocks now** (incl. existing ratio-immune sub/super data as a T0 instance) |
| **T1 — N-resolved** | **N at λ=1** — the singular slice along N | precisely **G1b-open** → **inherits G1b**; clears via the Fibonacci/DGY-exact validate-on-known-truth of the leg's vary-N fidelity (BAR-scoped) | **Holds on G1b** |
| **T2 — Two-sided limit** | λ→1∓ along the bracket ladders **at fixed N** (core); **N** for any limit-sharpening refinement | **core: G1a-met → unblocks**; **N-refinement: G1b-open → inherits G1b** (correction vs a flat reading: T2 is *split* — its core runs, its refinement does not). Intrinsic ceiling (brackets may not reach a limiting law) is a **terminal**, not a gate | **Core unblocks; N-refinement holds on G1b** |
| **T3 — Analytic substitution** | none empirical of its own — consumes T2-class brackets + §3-(A)'s derived law | forward: **§3-(A)-gated** (≠`INTRACTABLE`); the **reverse arm inherits G1b** (no trustworthy T1 slice to hand back to §3-(A) without it) — bidirectional confrontation, G1b doubly load-bearing | **Forward holds on §3-(A); reverse holds on G1b** |

The T2 split (core G1a-met / N-refinement G1b-inherited) is the one
audit finding worth your eye — rev-1's prose says "T2's core unblocks"
but doesn't carry the refinement→G1b inheritance into the table; §1's
schema forces it explicit.

---

## 3. Candidate new rows (the "etc." — Will's to cut/add)

### T1′ — Lyapunov/Thouless-anchored critical-slice indexing

**Drafted on your framing** ("index the critical slice *without* a
vary-N axis ⇒ sidesteps G1b") **and pressure-tested under your own
rider — landing terminal-open, not pre-softened.**

The comparison becomes: the λ=1 slice indexed not by N (T1) but by an
*intrinsic* substrate coordinate via the Thouless relation
γ(E)=∫log|E−E′| dN(E′)+const, comparing the critical slice's NNS along
that coordinate against the bracket slices.

**The pressure-test (your rider applied to this idea):**

1. *The spectrum-averaged anchor is not merely degenerate at λ=1 — it is
   identically flat on the entire λ≤1 side.* Avila–Jitomirskaya / Avila
   global theory (rev-1 §6 lit-lock): the AM Lyapunov exponent on the
   spectrum is L(λ)=max(0, log|λ|) — **L≡0 for all λ≤1**, not just at
   λ=1. A spectrum-averaged Lyapunov anchor therefore has **zero
   resolving power across the whole subcritical bracket *and* the
   critical slice** — it cannot index either by value. So T1′ is *not*
   "Lyapunov-value as the index"; that form is dead on arrival.
2. *The admissible form is the energy-resolved Thouless coordinate
   within a slice* (γ(E) carries E-structure even where the
   spectrum-average is 0). The honest open question is then exactly your
   remove-vs-relocate: does an energy-resolved Thouless coordinate at
   λ=1 **remove** the clearance burden (a genuine intrinsic index, no
   vary-N, no G1b), or merely **relocate** it — from "vary-N fidelity of
   the rotation-number IDS at λ=1" (G1b) to "**finite-N fidelity of the
   Thouless/γ(E) estimate at λ=1**" (a structurally identical pathology:
   both bite at the singularity for the same finite-N
   hierarchy-truncation reason)?

**Axis-clearance → inherited gate:** an energy-resolved Thouless
coordinate (candidate intrinsic index). **`terminal-open`** — the row's
pre-registered question *is* remove-vs-relocate, validated against
Fibonacci/DGY-exact (where the gap-labelling IDS ∈ ℤ+θℤ and the
Thouless/Lyapunov structure are **exactly** known — BAR-scoped,
instrument-fidelity only). Pre-registered terminals: `T1′_SIDESTEPS_G1B`
(Thouless-anchor N-robust at criticality on the known-truth check) /
`T1′_RELOCATES_TO_G1B′` (its finite-N estimate at λ=1 carries the same
N-pathology — then T1′ inherits a renamed-not-removed gate).
**Derived gate:** *unknown until run* — T1′ is **not gate-free**; it
trades G1b for a known-truth check it must still pass, and may relocate
rather than remove. Drafted on the sidestep framing, **not asserting the
sidestep.**

### T0′ — Substrate-matched self-similar windowing of the critical slice

**Flagged the most speculative of the proposals — offered for Will to
cut.** The disciplined response to rev-1 §0 ("the critical slice is not
quasi-stationary — never treat it as one") that *neither* excises (T0)
*nor* naively vary-Ns (T1): window the λ=1 slice by a **self-similar /
golden-mean-matched** scheme tracking the spectrum's own scale-invariance
(declared scale-ratio axis), comparing it against bracket slices read
under standard windowing.

**Axis-clearance → inherited gate:** the self-similar windowing-scale, a
declared axis, at fixed N. **G1a-met** for the no-ref-N part; **but**
multi-scale windowing at fixed matrix-N bumps the finite-N
hierarchy-truncation confound (G1b confound (i)) at its *deepest* scales
⇒ **partial G1b-adjacent inheritance: runnable above the N-set
truncation floor, holds/annotates for scales near it.** Ceiling: the
windowing scheme is a **phenomenological description, not a generative
model** (35a §9) — a candidate *for* §3, not a generator; that ceiling
is the row's, stated, not a gate.

---

## 4. Membership / cut-criterion (your rider as the admission rule)

- The column-2 axis-clearance question **is** the matrix admission test.
  Any row Will adds inherits it; any row that cannot answer it honestly
  is inadmissible.
- **T1′** is offered as a row that *tests* a sidestep hypothesis, not one
  that *claims* it — its value is the pressure-test landing terminal-open
  (remove vs relocate), not a presumed escape from G1b.
- **T0′** is the genuine "etc." additional and the most speculative —
  explicitly offered for you to cut; its partial-G1b-adjacent inheritance
  and phenomenological-not-generative ceiling are stated up front so the
  cut decision is informed.
- Tight set by design (4 audited + 2 proposed) — the discipline is a
  defensible candidate set for you to cut/add, **not** a maximized row
  count.

---

## 5. Scope / discipline

Reviewable DRAFT, not signed off — Will's to cut/add/fix; rev-2 §4 is
his cut. brief-and-hold; **nothing computes**; uncommitted. Numbers
deferred to slate unit 2 (ladder + T0 excision-width + floor estimator).
Gate-language pre-rev-2; light reconcile pass after rev-2. No §3
adjudication; T3 forward = §3-(A)-gated, reverse = G1b-inherited, neither
adjudicated. BAR rider on every Fibonacci/DGY check (instrument-fidelity,
not Fib→AM transfer). Asymmetric labels — treatments / instrument
framings, never "AM characterized," never a discovery. Banked Step-1
untouched/additive.
