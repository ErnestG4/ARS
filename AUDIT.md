# Auditing this repository

Everything here is designed to be checked by someone who does not trust it. This
document says how, what the automated checks cover, and — more usefully — where
they cannot help and you have to look yourself.

## The fastest thing you can do

```sh
python3 verify_all.py          # ~4 min, needs numpy/scipy/mpmath
```

Every arc keeps a `verify_*.py` that re-derives its banked claims from the
committed artifacts and **exits nonzero on any regression**. `verify_all.py`
runs the board and returns nonzero if any checker fails. They are self-locating,
so a fresh clone works with no configuration.

Several checkers additionally carry **blob-SHA tamper evidence** against their
seal's freeze list: if an artifact was edited after it was sealed, the checker
fails even when the numbers still look plausible. That is the property worth
knowing about — it is what makes "the record was not quietly adjusted" a
checkable statement rather than a promise.

## What a green board means, precisely

Green says three things:

1. The numbers quoted in the findings documents are the numbers in the artifacts.
2. Sealed artifacts have not been modified since they were sealed.
3. Derived quantities re-derive from their inputs.

Green does **not** say:

- that the measurements are correct;
- that the instrument measures what we claim it measures;
- that a stated conclusion follows from its data;
- that a literature-gap claim still holds (those are dated, not standing).

No checker can decide any of those. They are exactly the judgements an outside
reader is for, and the four sections below are where we think they bite hardest.

## Where to attack first

Ranked by our own estimate of where an error is most likely to be hiding. This
list is maintained honestly; if you find something not on it, we would like to
know, and it belongs on it.

**1. Definitional choices that no gate can test.** A gate can prove an
implementation matches a known answer. It cannot prove the quantity means what
we say. The sharpest live instance is in `derivflow`: spacings are unfolded
against the fractional free convolution of the empirical seed measure — theory
built for the *proportional* regime `k = ⌊sn⌋` — while the measurement runs at
`k = O(1)`, where `κ − 1 = k/(n−k) ≈ 0.0027`. There the exact reference is
absolutely continuous but rippled at the gap scale, which is the scale being
measured. `TRACK0_FINDINGS.md` §9 addendum states this plainly: refining the
quadrature grid converges toward the rippled limit rather than the macroscopic
density the unfolding wants, so the small-`k` reference was settled by a
definition, not a theorem.

**2. Error models, especially where they are suspiciously good.** In
`derivflow` the GUE primary arm is *under*-dispersed (χ²/dof ≈ 0.017), which we
attribute to cross-`k` correlation from shared replicates — an explanation that
is stated but **not tested**. The conservative `max(1, χ²/dof)` covariance
rescale is therefore inert on that arm while inflating the other, so a stated
5.84σ leans on the arm whose error model we ourselves flag. Backlogged in
`derivflow/ROADMAP.md`, not repaired.

**3. Any number whose generator is not committed.** The standing rule is that
every banked number has a committed generator that reproduces it; the failure
mode is a value that entered a document by hand and was never re-derived. Three
such were found on 2026-08-16 by an independent re-derivation pass and corrected
in commit `340280b` — in each case the prose, not the artifact, was wrong. Assume
more exist.

**4. One-sided rules and inert guards.** A verdict rule that can only fire one
way certifies half of what its name suggests. See `TOOLKIT.md` §9 and
`rigidgate/` for the worked example: a gate that awarded `RIGID_GUE` to a
perfect clock, and the split that fixed it.

## Reading the record

- `TOOLKIT.md` — the methodological rules, numbered, each with the failure that
  produced it. §9 is the guard doctrine; §12 the transition-order work.
- `EPISTEMIC_STATE.md` — what is currently believed and at what grade.
- `RESULTS.md` — the long-form record, in phase order.
- `*/prereg_sealed.json`, `*/seals/*.json` — pre-registered rules, disclosure
  ledgers, and blob-SHA freeze lists. These were written **before** the data
  they adjudicate, and the checkers pin them.
- `audit/` — an earlier internal truth-audit, kept including its findings.

## Retractions are in the record, not removed from it

Superseded results keep their banner and stay in place; a retraction leaves a
test behind so the same error cannot recur silently. `derivflow`
`TRACK0_FINDINGS.md` §7 is the clearest worked example: a sealed result that
did not survive, the instrument artifact that killed it (found by the project's
own regression step, not by a critic), the honest downgrade, and the
re-adjudication at higher resolution — each step a separate commit.

If a claim here looks stronger than its evidence, that is a bug. Please say so.
