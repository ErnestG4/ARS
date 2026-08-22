# Overnight 2026-08-22 — SEALED PREDICTIONS AND PASS CRITERIA

**Committed alone, before any generator or output exists.** A question without a stated pass
criterion carries a free parameter into scoring; these fix the test statistic and the threshold, not
only the question.

## B1 — brocot per-class ordering (supersedes the WITHDRAWN railed-subset medians)

The withdrawn claim was golden +1.316 > e−2 +1.175 > bronze +1.105 > silver +1.101 > metallics ≈ 1.05,
computed over cells **selected by bounded-q railing** and therefore differentially truncated.

**Test (full population, no selection):** per-class **median `I8_brody_q_unbounded`** over all 255 α,
correlated against **max CF quotient** across the **five metallic classes** (golden 1, silver 2,
bronze 3, metallic4 4, metallic5 5 — no ties). Spearman ρ, bootstrap 95% CI over per-class samples,
2000 resamples.

> **SURVIVES iff ρ ≤ −0.60 AND the 95% CI excludes 0.**
> Direction: golden is least approximable → most rigid → highest q, so q must *fall* with max CF
> quotient. **Secondary, reported not scored:** the same over all 9 classes (4 tie at maxq = 99).

## B2 — the unbanked sign reversal (supersedes the selected-on-q subgroup correlation)

The unbanked result was ρ(D_Q, unbounded q) = −0.209 **inside the railed subset** — selected on q
itself, so range restriction can manufacture it.

**Test (selection on the PREDICTOR, which is legitimate, never on the outcome):** split all 255 α into
**terciles of D_Q**, then compute ρ(D_Q, unbounded q) **within the top-D_Q tercile**. Bootstrap 95% CI,
2000 resamples.

> **REVERSAL IS REAL iff ρ within the top-D_Q tercile is NEGATIVE with 95% CI excluding 0.**
> Anything else — CI covering zero, or positive — and the reversal **does not survive** and the
> subgroup result stands retired. *A CI grazing zero counts as not surviving; the threshold is
> exclusion, decided here rather than while looking at the interval.*

## B3 — the 250 unchecked coverage keys

**Categories (fixed here):** `BOUNDED_FIT` (a parameter with a declared numeric bound), `CORRELATION_LIKE`
(a coefficient on [−1,1] or similar, e.g. `rho1`), `COUNT_OR_ID`, `OTHER`, `UNCLASSIFIABLE`.

**Counting convention: DISTINCT KEY NAMES, not occurrences.** No rounding is involved; the score is an
integer count, so the 2026-08-19 rounding-convention defect cannot recur here.

> **Prediction: `BOUNDED_FIT` ≤ 15 of the ~250 distinct key names.**
> Reasoning: the rail census already matched the three obvious bounded-fit families, and the largest
> unmatched key checked so far (`rho1`, 1,439 values) proved to be a correlation coefficient. Most
> remaining names are expected to be counts, ids and diagnostics. **A result above 15 means the rail
> census's coverage was materially worse than reported and the lower bound needs restating.**

## B4 — the four extraction rows: verdicts land under a DECLARED mapping

`run_controls`, `run_analytical_nns`, `run_per_pll_nns`, `universality` currently sit at
`NEEDS_JUDGMENT` for a **tooling** reason (the argmin is present without a function of that name).
Building an extraction route is pure tooling. **But their verdicts land under the same
code-feature→verdict mapping whose size-guard clause is docket item one**, and that mapping is
**DECLARED, not SEALED** (`8ba9d52`).

> **Every row these produce is labelled `DECLARED — size-guard clause pending adjudication`.** If any
> of the four has a generic size guard, its row **inherits the same contingency as the existing 8**
> and moves if the clause is ruled the other way. They must not arrive looking settled beside a table
> that already says otherwise.

## Out of scope for this overnight

The adjudication docket: the size-guard clause (8 rows hinge), the `run_phase4` taxonomy extension,
the severity gradient as organizing axis. **Building overnight work on a presumed resolution would be
the resolution rule chosen BEFORE the ruling rather than after the result — the same defect, mirrored
in time.** Also out of scope: any C3 migration; the inventory is descriptive only.
