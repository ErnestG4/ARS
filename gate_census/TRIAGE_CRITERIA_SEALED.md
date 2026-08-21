# Gate enumeration — TRIAGE CRITERIA, SEALED BEFORE THE SWEEP

**Sealed 2026-08-20, before any site beyond Gate 1 has been examined.** The temporal gap is the
point: sealing now, with zero sweep output in existence, is a stronger seal than sealing minutes
before the run. If verdicts were emitted first and the criteria refined while looking at them, this
would rebuild the ρ situation at 29-site scale — **rules adopted after seeing the results they
classify.**

## The four schema questions (mechanical)

Applied per site, from the code and the parameter's definition:

1. Is there a **named negative set** — cases the gate must NOT fire on?
2. Was that set ever **measured**?
3. What lies **beyond each endpoint** of its answer space, and can data legitimately go there?
4. Can the gate say **"none of these"** — does it have a rejection region at all?

## Verdict vocabulary — every site gets exactly one, NO SILENT STATES

| verdict | meaning |
|---|---|
| `MEASURED_NEGATIVE_SET` | a named negative set exists **and** both error rates are recorded |
| `UNMEASURED` | a negative set is named or implied, but its error rate was never measured |
| `NO_NAMED_SET` | no negative set exists; the gate cannot be wrong in the "none of these" direction |
| `NEEDS_JUDGMENT` | **the criteria cannot cleanly classify this site** |
| `NOT_A_GATE` | inspected and out of scope (assigns no class from a numeric comparison) |

**`NEEDS_JUDGMENT` is mandatory, not a courtesy.** A census that asks every gate *"can you say none of
these?"* while itself lacking a rejection region would be one-sided calibration told as a joke at its
own expense. **The tool must be able to refuse.** Anything the criteria cannot classify lands as
`NEEDS_JUDGMENT` with the ambiguity stated — never as a best guess.

## SEALED HIT-RATE PREDICTION

The expected-value case for this sweep rests on **n = 1**, and Gate 1 was **not a random draw** —
first-examined sites are often first-examined because something already smelled wrong. So the rate is
predicted here and scored later, converting it from a story into a measurement.

**Denominator matters: predict on DISTINCT IMPLEMENTATIONS, not sites.** ~19 of the ~30 sites are
copies of `_classify`; counting them separately would inflate any rate trivially. Estimated distinct
implementations: **~12**.

> **Prediction: of ~12 distinct gate implementations, 4–6 come back `NO_NAMED_SET` or `UNMEASURED`;
> at most 2 come back `NEEDS_JUDGMENT`.**
>
> Reasoning: *"check whether it fires"* is the default and requires no deliberate thought, while a
> negative set requires naming the nearest confusable case — so a substantial minority failing is the
> base expectation. But Gate 1's severity (argmin with **no rejection region at all**) is expected to
> be **unusual**, not typical.
>
> **A 0/12 result is a real finding about Gate 1's unusualness, not a disappointment to explain away.**
> A 12/12 result would mean the defect is systemic and the class-space finding generalises past the
> three instruments already known.

## Scope

~29 remaining gate sites, plus the **250 unchecked keys** from the rail census's coverage lower bound
(identical work shape: mechanical classification against known categories — bounded-fit,
correlation-like, other — with unclassifiable keys landing in the same triage table).

**Deliverable is the triage table.** Adjudication happens interactively, on the table, afterwards —
the judgment Gate 1 required was *recognising* the defect class, and that is done and named. What
remains is adjudication, and adjudication wants a table in front of it.

---

## AMENDMENT 1 — measured dedup, with the denominator-scaling rule fixed BEFORE the count is known

**Sealed 2026-08-20, still with zero sweep output in existence.**

**The defect this fixes:** the prediction above is stated over "~12 distinct implementations", derived
from "~19 of ~30 sites are copies of `_classify`" — and **that is an unverified read, not a
measurement.** It inherits the assumption that the 19 copies are *identical*, which is precisely what
C3 exists to check and has not. A drifted copy is **not a copy**: it is a distinct implementation with
its own verdict row, and the denominator moves. Standing obligation 7 was written because three cells
rested on unverified reads; here it catches one **inside a sealing document**, which is the strongest
evidence yet that the obligation covers *predictions*, not only execution plans.

**Amendment, in two ordered parts.**

**(a) The scaling rule — fixed HERE, before any hash is computed, and derivation-shaped so it carries
no free parameter.** The original prediction is **4–6 of 12**, i.e. **one-third to one-half** of
distinct implementations. That *fraction* is the sealed quantity; only the denominator is measured:

> **predicted_low = round(N_distinct / 3), predicted_high = round(N_distinct / 2)**, where
> `N_distinct` = the **measured** count of distinct `classify()` implementations by content hash.

At N=12 this reproduces 4–6 exactly, so the amendment **extends** the seal rather than restating it.
No constant is chosen; the fraction was fixed before the count was known, and would read identically
had the count turned out to be anything.

**(b) The measurement, run after (a) is committed.** Hash all 19 `_classify` copies; the dedup map
becomes a **measured artifact**, not an input assumption.
- **All 19 identical** → the sealed prediction stands on its stated basis, **and C3's precondition is
  verified for free.**
- **Any differ** → that is a **finding in its own right** — a drifted copy of a classifier is a quiet
  fork — each divergent copy takes its own verdict row, and `N_distinct` rises with the predicted
  range scaling by the rule above.

**Both outcomes are pre-committed as results.** Neither has a story available afterward that was not
written first.

### AMENDMENT 1 — MEASURED RESULT (run after the rule above was committed)

**The "any differ" branch fired, and it is a finding rather than a denominator tweak.**

| | |
|---|---|
| sites inspected | 19 |
| classifier bodies found | **15** (4 sites carry no `classify`/`_classify` function) |
| **distinct implementations by normalised content hash** | **11** |
| sealed rule applied → predicted | **4–6 of 11** |

**"~19 of ~30 are copies of `_classify`" was wrong.** Only two groups share a hash — a 4-way
(`mertens_liouville`, `lmfdb_postprocess`, `dirichlet_family`, `lmfdb_extend`) and a 2-way
(`zeta_height_convergence`, `earthquake_nns`). **The other nine are singletons.** This is not one
classifier copied nineteen times; it is **eleven distinct implementations**, mostly one-offs.

**The differences are SUBSTANTIVE, not cosmetic.** Diffing two singletons:
`run_lmfdb_family` guards on `pooled.size < 50` and `run_phase4` **has no minimum-n guard at all**;
and `run_phase4` **computes KS p-values** (`pv_p`, `pv_o`, `pv_u`) that the canonical `_classify`
never computes. It **returns them and never acts on them** — so it holds refusal information and
discards it, which is a *different* defect from having none, and arguably a nearer-miss.

**Consequence for C3, which must be reflected before that session runs: the consolidation brief's
premise is materially wrong.** It assumes 19 copies of one thing, with bit-identity as the acceptance
criterion. They are **variants**, at least one of which (`run_phase4`) carries capability the
canonical implementation lacks. **Consolidating onto `_classify` would silently LOSE that capability.**
C3 is therefore not a de-duplication but a **reconciliation**, and its acceptance criteria need a
sixth clause: *no site loses a computed quantity it currently returns.*

**Consequence for this sweep:** each of the 11 takes its own verdict row, which the sealed vocabulary
already provides for. The prediction stands on its stated basis, rescaled by the pre-committed rule
with no free parameter — and 4–6 of 11 happens to coincide with the original 4–6 of 12, so no
prediction was loosened by the correction.

**Also surfaced:** 4 sites (`run_controls`, `run_analytical_nns`, `run_per_pll_nns`, `universality.py`)
have the argmin but no function of that name. They are **not** exempt — they enter the sweep as
`NEEDS_JUDGMENT` pending extraction by a different route.

### AMENDMENT 1 — ROUNDING CONVENTION: the zero-degrees-of-freedom claim DOES NOT STAND as stated

**Self-audit result, against my own claim.** The rule as committed reads `round(N_distinct / 2)` and
**names no rounding convention**. At the count that actually occurred, that matters:

| convention | `round(11/2)` |
|---|---|
| half-to-even (Python's `round`) | **6** |
| half-up | **6** |
| half-down | **5** |

**And the commit record cannot exonerate it.** `measure_copy_dedup.py` (which pins the convention by
using Python's `round`) and `copy_dedup.json` (the result) were committed **in the same commit**,
`3b501fe`. The generator was **not** in the record before the count was known. I wrote it before
running it — but *commit order is the evidence, not recollection*, which is the standard applied to
the classification seal and it applies here to me.

**So the honest scoring for this sweep: predicted 4–5 **or** 4–6, upper end ambiguous.** The substance
barely moves; **the standard being invoked fails**, and that is the part worth recording. A rule
claiming zero degrees of freedom had a one-unit freedom at exactly the boundary the count hit.

**Not resolved by picking one now** — choosing a convention after seeing N = 11 is the defect itself.
The sweep will be scored against **both readings**, and a result of exactly 6 will be reported as
*met under two of three conventions*, stated rather than smoothed.

**Going forward (binding on future amendments, no retroactive effect):** rounding is **half-to-even**,
and any rule with a rounding step must name its convention in the same commit that seals it. *A
derivation with an unspecified convention is not a derivation; it is a derivation plus a choice.*

### AMENDMENT 1 — NORMALISATION SPEC (a constant doing classification work gets written down)

`N_distinct = 11` is a count **under a normalisation**, so the normalisation is part of the
denominator and is specified here beside the map. `measure_copy_dedup.py` extracts each
`classify`/`_classify` body via `ast.get_source_segment`, then:

- **strips** comments and blank lines (`tokenize.COMMENT`, `tokenize.NL`)
- **collapses** all whitespace runs to a single space
- **preserves** variable names, constants, call structure, and control flow
- hashes the result with SHA-256, first 16 hex

**Therefore:** cosmetic reformatting and comment edits do **not** split a group; a **variable rename,
a changed threshold, or any logic difference does.** A stricter rule (AST-shape only, names
normalised) would lower the count; a looser one (raw bytes) would raise it. **The count of 11 is
reproducible only against this spec**, which is why it is committed rather than left implicit — same
status as the discriminator's `RAIL_RATIO`.

### AMENDMENT 1 — `run_phase4` GOES TO `NEEDS_JUDGMENT`, and the taxonomy is NOT extended

`run_phase4.classify` **computes** `pv_p`/`pv_o`/`pv_u`, **returns them, and never acts on them.** The
sealed question *"was the negative set measured?"* is binary; this site **measures-but-ignores** and
fits neither `MEASURED_NEGATIVE_SET` nor `UNMEASURED` without distortion.

**The tempting move is to add a `COMPUTED_UNUSED` verdict. Refused.** That is refining classification
rules after output exists — the exact move this seal forbids — and the refusal region was built for
precisely this case. **`run_phase4` → `NEEDS_JUDGMENT`, with the ambiguity stated.** Any taxonomy
extension happens **at adjudication**, as a ruled-on outcome, in its own commit, **applicable to
future sweeps rather than retrofitted into this one.** *The seal surviving its first hard case matters
more than the tidiness of the table.*

**Recorded for the adjudication session, not applied now — a severity gradient, which is likely that
session's organizing axis:**

> **no rejection region  <  computes-and-ignores  <  computes-and-acts**

`computes-and-ignores` is a **nearer miss** than `never-computes`: the information was in hand and the
marginal cost of acting on it was almost zero. That ordering is an observation offered to adjudication,
**not** a verdict assigned here.

### AMENDMENT 1 — C3 CONSEQUENCE: a divergence inventory, not just a preservation clause

The variants differ in **behaviour**, not only in returned quantities: `run_lmfdb_family` guards on
`pooled.size < 50`, `run_phase4` has **no minimum-n guard at all**. A guard is not a quantity to
preserve — it is a **policy fork**, and consolidation must either **pick a policy** or **preserve both
behind an explicit parameter**.

So C3's brief needs **two** additions, not one:
1. *(named earlier)* **no site loses a computed quantity it currently returns**;
2. **a divergence inventory** — every behavioural difference between the 11 variants listed and
   **ruled on before any site is migrated.**

**That reclassifies C3.** It is no longer "tedious, wants its own session"; it is
**adjudication-shaped**, and wants the same **triage-table** treatment as this sweep: mechanical
inventory first, ruling second.
