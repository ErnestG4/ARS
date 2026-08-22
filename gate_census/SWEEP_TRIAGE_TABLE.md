# Gate enumeration — TRIAGE TABLE

Mechanical pass against `TRIAGE_CRITERIA_SEALED.md`. **Adjudication has not happened.** Every row is a
verdict from the sealed vocabulary; no row is silent.

## SCORED PREDICTION: MISSED, HIGH, under both readings

| | |
|---|---|
| sealed prediction | **4–5** (half-down) / **4–6** (half-up, half-to-even) of 11 |
| measured | **9 of 11** |
| result | **MISSED under both readings** — the dual-scoring did not rescue it, and was never going to |

**The prediction was wrong in a specific, recorded way.** Its stated reasoning was: *"Gate 1's severity
(argmin with no rejection region at all) is expected to be **unusual**, not typical."* **That is
falsified. Gate 1 was typical.** 8 of 11 distinct implementations have **no rejection region at all**,
and a 9th has one whose complementary error rate is unrecorded.

**Per the seal, this is a pre-committed finding, not a disappointment:** *"A 12/12 result would mean
the defect is systemic and the class-space finding generalises past the three instruments already
known."* At **9/11** the systemic tail is where we landed. The one-sided class space is **the house
default**, not three unlucky instruments.

## The table

| verdict | implementation | basis |
|---|---|---|
| `NO_NAMED_SET` | `run_lmfdb_family` | argmin, no fit-quality rejection |
| `NO_NAMED_SET` | `run_fungal_nns` | ″ |
| `NO_NAMED_SET` | `run_mertens_liouville` **(+3 identical)** | ″ |
| `NO_NAMED_SET` | `run_eeg_full` | ″ |
| `NO_NAMED_SET` | `run_zeta_height_convergence` **(+1 identical)** | ″ |
| `NO_NAMED_SET` | `run_phase5` | ″ |
| `NO_NAMED_SET` | `run_eeg_depth` | ″ |
| `NO_NAMED_SET` | `run_lmfdb_edge` | ″ |
| `UNMEASURED` | `verify/tier1_lfunction_guard` | rejection region present **and compared**, but no complementary error rate recorded at the site |
| `NEEDS_JUDGMENT` | `run_phase4` | **computes** `pv_p/pv_o/pv_u`, **never compares them** — measures-but-ignores, taxonomy extension deferred |
| `MEASURED_NEGATIVE_SET` | `arithmetic_toolkit` | rejection region compared, threshold calibrated against measured non-members |

**Plus 4 rows outside the sealed 11** — `run_controls`, `run_analytical_nns`, `run_per_pll_nns`,
`universality` — all `NEEDS_JUDGMENT`: they carry the argmin but no function of that name. **Not
exempt**; extraction by another route required.

**The headline, with its tautological half removed.** It is tempting to write *"the only
`MEASURED_NEGATIVE_SET` is the one this arc repaired, and the only `UNMEASURED` is the verifier this
arc touched"* — but **the touching WAS the measuring.** This arc is the only process that has ever
asked these instruments the negative-set question, so its footprint and the measurement's footprint
coincide by construction. That half is a tautology and should not be quoted as a coincidence.

**The non-tautological content is stronger and is the right headline: no instrument in this codebase
acquired a rejection region except through this arc's deliberate intervention.** Not *"we happened to
fix the only broken ones"* but **"the house default produces instruments that cannot refuse, and every
exception was manufactured."**

**And the miss dissolves the selection worry raised at sealing.** The concern was that Gate 1 might
have been examined first *because something already smelled wrong* — a non-random draw inflating the
expected rate. It was not unusual. **It was the house style, sampled.**

## Disclosed interpretation layer — **DECLARED, NOT SEALED** (commit-order test applied)

The seal fixed the four questions and the five verdicts; it did **not** fix the mapping from code
features to verdicts. **And the mapping does not have seal status**: `run_sweep.py` and
`sweep_table.json` both entered the record in the **same commit, `8ba9d52`**. By the standard applied
to the rounding convention at `3b501fe`, that makes this **declared with its sensitivity stated**, not
provable-prior. I wrote it before running — *and commit order is the evidence, not recollection.*

**Second instance of the same pattern in two days**, so it now has a structural fix (`sealgen.sh`,
below) rather than another resolution to be careful.

The mapping is written in `run_sweep.py` and stated rather than left implicit. Its load-bearing clause: **a size guard (`n < k → 'insufficient'`) is a
PRECONDITION refusal, not a negative-set refusal** — it says *"I cannot measure"*, not *"this is none
of my classes"* — so it does not earn `MEASURED_NEGATIVE_SET`. Every `NO_NAMED_SET` row above has a
size guard; none has a rejection region. **If adjudication rejects that reading, all 8 rows move**,
which is why the clause is stated at the top rather than buried.

## For adjudication (nothing ruled here)

- **The size-guard clause FIRST — 8 rows hinge on it.** A size guard refuses to *measure*; a
  rejection region refuses to *classify*. `n < k` says *"I can't produce an answer"*; a negative set
  says *"I produced an answer-space and this input is outside it."* Conflating them would count
  *insufficient data* as instrument self-awareness, which it is not — an instrument with a size guard
  and no rejection region will, given enough data, classify **anything** into [rigid…Poisson].
  **Refinement to test at adjudication, and it is derivation-shaped so it extends rather than bends:**
  *precondition refusals do not count as negative sets, **except** where the precondition is derived
  from the classification's own validity rather than from generic statistical caution.* Worked case
  for the exception: this arc's own `MIN_N = 1/RAIL_RATIO`, below which the discriminator's arm
  provably cannot fire — that guard is doing partial rejection-region work. None of the 8 rows' guards
  are of that kind (all are generic `n < 5` / `n < 50`), but the boundary should be ruled, not assumed.
- The severity gradient offered earlier: **no rejection region < computes-and-ignores <
  computes-and-acts**. `run_phase4` sits in the middle and is the nearest miss.
- Whether `COMPUTED_UNUSED` becomes a verdict — **as a ruling, in its own commit, for future sweeps**,
  not retrofitted here.
- The 4 no-function sites need an extraction route before they can be classified at all.
