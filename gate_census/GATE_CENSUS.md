# Gate census — "what should this NOT fire on, and was that ever measured?"

**The question, sharpened by the owner 2026-08-19.** The earlier framing was "find one-sided
calibrations", and the syntactic sweep for that failed its own known-positive self-test twice (see
`lcap/ESTIMAND_CENSUS.md`). The better question is per-gate and semantic:

> **Is there a NAMED SET of things this gate should not fire on, and was that set ever measured?**

A gate can have a two-sided-*looking* threshold and still never have been run against its nearest
confusable class. This census is a manual enumeration, not a grep — the deployed forms of this defect
are bare literals and single-letter variables, invisible to search and obvious to a reader.

Population: functions that assign a class or verdict from a numeric comparison. ~30 sites, many of
them the same classifier copied across `run_*.py`.

---

## GATE 1 — `arithmetic_toolkit._classify` — **FAILS, and it is the widest-blast-radius gate in the repo**

**Depended on by 93 files.** Verdict assignment is:

```python
best = min([('Poisson', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
```

**Named negative set: NONE.** The only refusal is `n < 5` → `'insufficient'`. There is no
goodness-of-fit threshold and **no 'none of the above' branch**. So its specificity against a
non-member distribution is not merely unmeasured — it is **structurally zero by construction**. Every
input with n ≥ 5 is assigned one of three classes.

**Ever measured: no.** Measured now (`gate1_specificity.py`, n = 2000 each):

| input (none of the three classes) | verdict | best-fit KS | vs KS crit (α=0.01) |
|---|---|---|---|
| **perfect clock** (all spacings equal) | **GUE** | 0.533 | **15× the critical value** |
| uniform spacings U(0,2) | GOE | 0.091 | 2.5× |
| lognormal spacings | Poisson | 0.104 | 2.9× |
| bimodal (0.2 / 1.8) | Poisson | 0.334 | 9× |
| clustered (Neyman–Scott-ish) | Poisson | 0.535 | 15× |
| constant 0.5 + noise | **GUE** | 0.533 | 15× |
| *true Poisson (contrast)* | *Poisson* | *0.012* | *FITS* |

**7/7 non-members received a confident class label, and every best fit is rejected by a standard KS
test.** Note the first row: **a perfect clock reads GUE.** That is the RIGID_GUE failure — a clock
earning the GUE pole — reached through an entirely different gate by an entirely different mechanism.
The same wrong answer arrived at twice independently is a statement about the *question* these gates
are asked, not about either implementation.

**This is a distinct defect class from one-sided calibration: an ARGMIN WITH NO NULL OPTION.** A
selection among candidates is not a test. It has no rejection region, so it cannot be wrong in the
direction of "none of these" — and that direction is where every non-member lives. Same shape as the
argmax-has-no-location-error-bar lesson banked earlier the same day: *a selection reported as a
verdict.*

**Repair applied, non-breaking.** The information needed to refuse was **already computed** — the
function returns all three KS distances. Added `best_ks`, `ks_crit_01`, `fit_rejected`; `best` and
every pre-existing key are **bit-identical**, so no banked number moves and callers gain a refusal
they can consult. Verified: pre-existing keys unchanged on a true-Poisson input; perfect clock now
reports `fit_rejected = True` alongside its unchanged `best = 'GUE'`.

**Not yet done — the downstream question this opens.** 93 files consume `best`; none of them checked
fit quality because none was exposed. **How many banked classifications sit on a rejected fit?** That
is now a cheap sweep and it is the natural next step of this census.

**Contrast — `sessionK/nns_stats.classify_empirical` PASSES the precondition half.** It refuses on
`n < 200` and on mean spacing outside (0.7, 1.4) — *"not a unit-density point process"* — a genuinely
named negative set. But it still ends in a bare `min(scores, ...)` with no fit-quality rejection, so
it refuses on **preconditions** and not on **goodness of fit**. Partial pass: the negative set exists
and is named, but does not cover the non-member case.

---

## The 93-file sweep — Q1/Q2/Q3, and a mis-specified first cut

**Nothing was re-measured.** The banked artifacts already store `ks_p / ks_o / ks_u` and `n`, so the
rejection test is arithmetic on existing records. **85 files, 1655 banked classifications.**

### First cut was WRONG, in the way the owner predicted

Using `fit_rejected` — the n-dependent KS significance threshold I had just added — **1613 of 1655
(97.5%)** came back rejected. That is not a work list, it is a **mis-specified test**: median n is
**6,150** and the largest is **52,501,662**, where a deviation of 0.0002 is "rejected at α=0.01".
**Significance is not badness.** Same error I had caught two hours earlier in the invariance
tolerance — *a threshold referenced to the wrong scale* — and the same root as the estimand rule.

### The work list, on EFFECT SIZE calibrated against measured non-members

Calibration comes from `gate1_specificity.py`, through this same gate: true Poisson **0.012**,
uniform **0.091**, lognormal **0.104**, bimodal **0.334**, perfect clock **0.533**.

**THE METHOD, worth naming because it generalizes past this gate: when a goodness threshold is
needed, calibrate it against MEASURED NON-MEMBERS THROUGH THE SAME INSTRUMENT, not against a
theoretical distribution.** The 0.09 tier is not a distributional cutoff — it is *"fits no better than
uniform spacings do when passed through this exact classifier"*. That is why it works where the KS
critical value does not: it inherits the instrument's own quirks, unfolding included, instead of
assuming them away. Same move as measuring a misclassification-rate estimand directly rather than
inferring it from a separation of means.

| tier | count | share |
|---|---|---|
| significance (any deviation) | 1613 | 97.5% — *large-n artifact, discarded* |
| **≥ 0.09 — fits no better than a known non-member** | **754** | **45.6%** |
| ≥ 0.104 — worse than lognormal non-member | 747 | 45.1% |
| **≥ 0.334 — worse than bimodal non-member** | **45** | **2.7%** |

**Q1 — how many banked classifications sit on a genuinely poor fit: 754**, of which **45 fit worse
than a bimodal distribution does through the same gate** and are near-certainly ungradeable. Worst
files: `mertens_liouville` (0.786), `solar_flare` (0.736), `earthquake` (0.579), `binance` (0.414).
Note `eeg_full_results.json` contributes **520** rows at up to 0.262 — the largest single block.

**Q2 — how many are load-bearing for a stated finding: NOT YET DETERMINED.** This is the triage step
and it is deliberately not automated. The file list above is the input to it, not its output.

**Q3 — a THEOREM, not a finding.** *Claim: a rejected row loses its class; it never changes class.*
*Proof:* `best = argmin(ks_p, ks_o, ks_u)` and `best_ks = min(ks_p, ks_o, ks_u)`. Rejection is a
predicate on `best_ks` alone — the residual to the best fit. The **ordering** of the three distances
is independent of the magnitude of their minimum, so no predicate on `best_ks` can change which
element attains the argmin. ∎ This is provable from the function's form and depends on **no
measurement**.

**Consequence, and it caps the blast radius of the entire sweep: the 754 rows are OVERCLAIMED, not
MISDIRECTED.** None of them is wrong in a way that propagates a *different* answer downstream — a
row either keeps its class or has none. So the work list can be cleared at any pace without racing a
contaminated conclusion through the record.

**Nothing has been demoted.** Same discipline as the boundary-rate triage where 105 candidates
collapsed to 19: the sweep produces a work list, a human decides. A mild unfolding imperfection can
raise `best_ks` without the class being wrong, and the 0.09 tier is calibrated but not sacred.

**Repair to the repair:** `_classify` now returns **both** `fit_rejected` (significance — low
information at large n, retained for completeness) and **`fit_poor`** (effect size, `best_ks ≥ 0.09`,
calibrated against measured non-members). The second is the one callers should consult.
