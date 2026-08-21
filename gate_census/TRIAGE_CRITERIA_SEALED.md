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
