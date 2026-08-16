# Full-Sequence Holonomy — Arc Brief (DRAFT FOR WILL'S REVIEW, NOT RUN)

**Status:** DRAFTED 2026-08-16 under the overnight authorization, item 4 — **prepared, not
executed**, per Will's instruction. Needs Will's review, amendments, and an explicit go before
any compute.
**Lineage:** the holonomy pilot (`holonomy/COMMUTATOR_TABLE.md`, seal a583d9f + ADD-1..7) bounded
**pairwise** order-sensitivity and said so explicitly in its §7: *approximate pairwise commutation
does not bound full-sequence holonomy.* This is that registered follow-up. It inherits the
pilot's machinery (transitions, lattice module, canonical registry, census ownership map) and its
disciplines (TOOLKIT §9, including the three rules the pilot itself generated).
**Posture:** protocol arc. Synthetic data and already-banked substrates only; **no new science
claims.** The deliverable is a measured statement about how pairwise commutators compose, plus a
verdict-flip risk number for banked rows.
**Honest one-line frame:** the pilot measured what happens when you swap two steps. A pipeline
applies five or six, and the question is whether swapping two at a time tells you anything about
reordering the whole stack — or whether the interactions are where the risk actually lives.

---

## 0. The three things that break the pairwise bound

Stated first because they are the arc's whole reason to exist, and because each becomes a cell.

1. **Mid-stack dial values.** Every pairwise Δ in the table was measured on a *bare substrate*.
   Inside a stack, the input to step *k* has already been reweighted, eroded, unfolded. Its
   gradient, density, weight variance — the very dials the pairwise laws are written in — are
   different. A pairwise law evaluated at the wrong dial is not a bound, it is a category error.
2. **Non-linear amplification.** Disattenuation divides by √R; thresholds and verdict lattices are
   step functions. A Δ that is negligible in Σ² units can be decisive in *verdict* units — the
   pilot's own materiality metric (margin-to-boundary) exists because of this, and at the boundary
   the amplification is unbounded.
3. **Combinatorics.** Six transitions admit 720 orderings; the type constraints (you cannot
   edge-correct before you have a window) prune that but not to a handful.

## 1. The idea that makes it tractable

Full-sequence holonomy is **not** *n!* independent numbers. Any ordering is a permutation, any
permutation decomposes into transpositions, and to leading order the total commutator of an
ordering σ should be the **sum of the pairwise commutators of its inversions**, each evaluated at
its *local* (mid-stack) dial:

    Δ_pred(σ)  =  Σ_{(i,j) inverted in σ}  δ_ij( dial_mid(i, j, σ) )

This is a BCH-style first-order composition. **It is falsifiable, and falsifying it is the point.**
The residual

    H(σ)  =  Δ_measured(σ) − Δ_pred(σ)

*is* the higher-order holonomy — the genuine curvature of the measurement stack, the object the
pairwise table cannot see. The arc's primary result is the size, sign, and structure of H, not a
catalogue of orderings.

## 2. Cells

- **S0 Dial-propagation table** (prerequisite; cheap; the thing that makes S2 meaningful). For each
  transition, measure how it moves the dial variables the *downstream* pairwise laws are written
  in (gradient ratio, window-to-trend-scale ratio, weight variance, effective n). Deliverable: a
  small matrix, `dial_propagation.json`, with a committed generator. **If this cell shows the dials
  barely move, the arc's premise weakens and §7's kill-criterion applies.**
- **S1 First-order predictor, constructed and red-pathed.** Build Δ_pred(σ) from the banked
  pairwise laws + S0. Witness (two-sided, per §9): it must reproduce measured Δ for **single**
  transpositions (where it is exact by construction — a sanity floor, labeled as such), and it must
  **fail** on a deliberately constructed three-transition sequence whose higher-order term is known
  nonzero analytically. A predictor that cannot be caught being wrong predicts nothing.
- **S2 Measured H(σ) over a sealed permutation sample.** Not all orderings: a sealed sample —
  all adjacent transpositions of the reference order, all 3-cycles, the reversal, and a fixed
  random draw — with the sample and its seed fixed before any run.
- **S3 Amplification through the decision layer.** Take the measured continuous-layer Δ and push it
  through the **actual banked verdict lattices as code** (`survey/verdict_lattice.py`,
  `holonomy/lattice_h.py`, the proposed `rigidgate` cell). Output: per banked row, a **verdict-flip
  probability**, not a Σ² number. This is the cell that produces the thing anyone would act on.
- **S4 Materiality + scoping.** Which banked rows carry flip probability above a sealed threshold;
  what ordering discipline (registry entries) removes it.

## 3. Scope, fixed before design, because this is where the arc could sprawl

**One pipeline, not all of them.** Proposal: the **survey dialect** — it is fully instrumented, its
transitions are enumerated in the census ownership map, its lattice exists as code, its banked rows
have measured margins, and C4 + P3 already give two of its pairwise laws. **Sequence length 5.**
Everything else — 1D dialect full sequences, cross-dialect stacks — is out of scope and stays
registered.

## 4. Verdict lattice (sealed; extends the pilot's, does not replace it)

- **FIRST_ORDER_SUFFICIENT** — |H(σ)| within the sealed tolerance for every sampled σ: the pairwise
  table *does* bound the stack, and the pilot's scope caveat can be formally relaxed (with the
  sample's coverage stated).
- **HIGHER_ORDER_MEASURED(law)** — H is resolvable and follows a sealed predicted form (e.g. scaling
  with the number of inversions, or with a specific triple's dial product); banked with sign and
  coefficient.
- **VERDICT_FLIP_RISK** — some banked row's flip probability exceeds the sealed threshold. This is
  the outcome with teeth: it forces a canonical *sequence* (not just pairwise orders) into the
  registry and a re-run of the affected rows under it.
- **UNDERPOWERED** — H not resolvable against σ_H at the sealed sample size; extension = one
  declared sample-size doubling, dry-run verified, fires once.

Per the §9 fail-closed rule, the materiality obligation is discharged **in the shared resolver**,
not per-runner — the pilot learned that one the hard way (holonomy ADD-1).

## 5. Cost, honestly

The expensive cell is S2: each sampled ordering is a full pipeline run. With a 5-transition
sequence, ~20 sampled orderings, and the survey F path at ~1 s per tile-set evaluation, S2 is
minutes, not hours — **the compute is not the constraint.** The constraint is S0 and S1: the
dial-propagation table and the predictor are where the design work and the defect risk live, and
they are where a rushed version would produce a confident wrong answer. My estimate: **one full
session for S0+S1 with its gates, a second for S2–S4 and banking.** I would not compress it into
one, and I would rather it be two clean sessions than one long one.

## 6. Tripwires

1. The permutation sample and its seed are sealed before any measurement; no ordering is added or
   dropped after seeing an H.
2. Mid-stack dials come from the **measured** S0 table, never from the bare-substrate values — using
   a bare dial inside the predictor is the arc's signature defect and would make S1 silently wrong.
3. Higher-order H is reported against σ_H over the substrate ensemble; verdict-flip probability is
   reported against each row's own margin. Two denominators, never crossed (inherited).
4. The decision layer is exercised as **the banked lattice code**, never a re-typed copy
   (rulings-as-code).
5. Non-inertness of every constructed witness is argued analytically *and* checked against the
   estimator's own suppressors before running — the C4 cell's red demo was inert for exactly the
   missed-suppressor reason (holonomy ADD-6), and that near-miss is now the §9 rule.
6. Nothing under `survey/` or `cross_substrate/` is written; frozen surfaces only.

## 7. Kill criteria — when NOT to run this

Stated up front so the arc can be declined on evidence rather than abandoned halfway:

- **If S0 shows the dials barely move through the stack**, then mid-stack ≈ bare-substrate, the
  first-order predictor is trivially right, and the arc collapses to a restatement of the pairwise
  table. Bank S0, close the arc, relax the pilot's §7 caveat with the S0 evidence as its basis.
- **If every banked row's margin exceeds the largest conceivable Δ by a wide factor**, S3 has no
  teeth and the arc is an academic exercise. The pilot's numbers suggest margins are 3σ+ while
  pairwise Δs are ≲0.005 in F units — so **this kill criterion is live and should be checked
  first**, cheaply, before S1 is built. I recommend making that check the arc's opening cell.

## 8. Open questions for Will

1. **Pipeline choice** — survey dialect (my recommendation: best instrumented, real margins) or the
   1D home dialect (more transitions, more interesting commutators, no banked survey rows at risk)?
2. **Is §7's second kill criterion the right opening cell?** It would let the arc self-abort in
   under an hour if the risk is not real, which I think is the responsible design — but it also
   means the arc may return "nothing to see here," and that should be an acceptable outcome
   *before* it starts, not a disappointment after.
3. **Does VERDICT_FLIP_RISK license re-running banked rows**, or only registering a canonical
   sequence and reporting? The pilot's precedent says report-not-re-verdict for another program's
   rows; for the survey rows (ours) I'd propose re-run-under-canonical with three-event labels.
4. **Sequence length 5, or the full census-enumerated stack?** Five is my recommendation; the full
   stack multiplies S2 without, I think, changing the answer's shape.
