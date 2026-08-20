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

**⚠ THRESHOLD SUPERSEDED — 0.09 → 0.0629.** The 0.09 below was read off ONE calibrator (uniform at
n=2000 measured 0.091) and therefore sat *exactly on it*: at n=3000 uniform reads 0.0878, making the
gate a coin flip on its own nearest confusable case. **One-sided calibration, committed inside the
census that found the class — the fourth instance.** Recalibrated with both error rates across
n ∈ {500, 1000, 2000, 5000, 10000} × 12 reps (`calibrate_fitpoor.py`): worst **genuine member 0.0567**,
best **non-member 0.0699** — separated — so the threshold is the **geometric midpoint 0.0629**,
sitting off both calibrators. `DetectorSpec` certifies **sensitivity 5/5, specificity 2/2**. Effect of
the correction on the work list: **754 → 936 rows** at the poor-fit tier, i.e. the too-high threshold
was *missing* 182 poor fits.

**THE METHOD, worth naming because it generalizes past this gate: when a goodness threshold is
needed, calibrate it against MEASURED NON-MEMBERS THROUGH THE SAME INSTRUMENT, not against a
theoretical distribution — and calibrate it from the SEPARATION between measured members and measured
non-members, never from where one calibrator happened to land.** The 0.09 tier is not a distributional cutoff — it is *"fits no better than
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

---

## Severity-first triage (Q2) — and the finding is structural, not a row count

Sorted by **severity, not block size**: 8 rows fit worse than the **perfect clock (0.533)**, the
calibrator already known to be unclassifiable. They fall in two programs.

| best_ks | n | label | source |
|---|---|---|---|
| **0.786** | 3,865 | Poiss | `mertens_liouville_results.json` → `mertens.direct_nns` |
| **0.752** | 95,863 | Poiss | `mertens_liouville_results.json` → `mertens.analytical_nns` |
| **0.736** | 141 | Poisson | `solar_flare_results.json` → `solar_min.primary` |
| 0.705 ×3 | 422k / 20k | Poisson | `solar_flare_results.json` → `strata.solar_min.*` |
| 0.582 | 6,428 | Poisson | `solar_flare_results.json` → `solar_max.primary` |
| 0.579 | 528 | Poiss | `earthquake_results.json` → `by_tile[13]` |

**Q2 answer for both worst files: NO stated finding rests on the bad label — and in both cases the
record ALREADY CONTAINS THE CORRECT VERDICT, from a better instrument.**

- **Mertens.** `verify/00-summary.md` records the verified, **lens-invariant** verdict as
  **`SUPER_POISSON`**. The argmin says `Poiss` at 0.786.
- **Solar flares.** `COMCAT_SOC_RUNSTATE.md` G5 records *"flares clustered > Poisson floor; solar MAX
  more clustered than solar MIN"*, established against a Poisson floor rather than by this classifier.
  The argmin says `Poisson` at 0.705–0.736.

So the labels are **inert leftovers**, exactly as Q3's theorem predicts — overclaimed, not misdirected.

### The structural finding: the CLASS SPACE is one-sided

`TOOLKIT.md:444` already documents this collapse in **two** other instruments — the quadrant
classifier, whose `BL` class is *"a collapse class named after one of the two things it collapses"*
and which read known-clustered GOES flares as *"Poisson noise"*; and Brody `q`, where a **CV = 6.5
burst process reads q = 0.0001, more Poisson than Poisson's own 0.0023**, because clustered data wants
`q < 0` and rails at the `bounds=(0,1)` floor.

**`_classify` is the third instrument with the same blind spot, and the cause is shared: each
parameterises [rigid … Poisson] with POISSON AS AN ENDPOINT.** Super-Poisson data is not
mis-measured — it is **unrepresentable**, so it piles up at the boundary. Confirmed here in synthetic
(clustered → Poisson at 0.535) *and* in real data twice over (flares 0.705, Mertens 0.786).

**This is one-sided calibration one level up: not a one-sided THRESHOLD but a one-sided CLASS SPACE.**
The family of failures now reads: a one-sided threshold (`RIGID_GUE`), a one-sided class space (these
three instruments), and an argmin with no null option (gate 1). All three are the same sentence —
**the answer space does not contain the truth**, so the gate returns the nearest thing it can say.

*Also noted:* `run_mertens_liouville.py:139` carries its **own copy** of `classify()` (`'Poiss'`
rather than `'Poisson'`), so the 93-file import count **undercounts** the blast radius — duplicated
implementations do not import the repaired one and will not pick up `fit_poor`.

---

## Duplicate hunt — 19 independent copies, one of them a VERIFIER

Grepping by **structure** (argmin over a Poisson/GOE/GUE KS triple) and by **value** (the distinctive
short string `'Poiss'`, the `nns_cdf_*` triple computed together), as the owner suggested — a
paraphrased copy that dodges a structural grep usually still carries the constants.

**19 files define their own argmin classifier rather than importing the repaired one.** The repair to
`arithmetic_toolkit._classify` therefore reaches **one of nineteen**; the other eighteen will not pick
up `fit_poor` or `fit_rejected`:

`run_lmfdb_family` · `run_controls` · `run_fungal_nns` · `run_mertens_liouville` · `run_eeg_full` ·
`run_lmfdb_postprocess` · `run_dirichlet_family` · `run_zeta_height_convergence` · `run_phase5` ·
`run_eeg_depth` · `run_phase4` · `run_analytical_nns` · `run_earthquake_nns` · `run_lmfdb_extend` ·
`run_per_pll_nns` · `universality.py` · `run_lmfdb_edge` · **`verify/tier1_lfunction_guard.py`**

**The last one is the finding.** A **verifier** carries its own copy of the defective classifier — so
a gate whose job is to catch regressions shares the blind spot it would need in order to catch this
one. That is the checker-cannot-see-its-own-class problem, in the strongest possible location.

*The owner's prediction was right and the scale is worse than "more than one": three instruments
independently reinvented the one-sided class space, and within just this instrument there are
nineteen copies of it.*

---

## RAIL CENSUS — the pileup is silent by design, and it is 37.9%

Unrepresentable data does not land *near* an endpoint, it lands *on* it. So the signature of a
too-narrow class space is a **mass of outputs sitting within numerical tolerance of a boundary** —
checkable with the same instrument as the boundary-rate sweep, pointed at **parameters** instead of
**rates**, and it is evidence about the **instrument** rather than about any individual row.

| parameter | n banked | at boundary | fraction | reading |
|---|---|---|---|---|
| **`I.8_brody_q`** (floor q=0) | **40,106** | **15,195** | **37.9%** | **RAILED — class space too narrow** |
| `I.9_berry_robnik_rho` (ρ=1) | 20,290 | 33 | 0.2% | ok *(and ρ=1 legitimately IS pure Poisson)* |
| `rep_int` (floor 0) | 83 | 2 | 2.4% | ok (small n) |

**Over a third of every Brody q ever banked in this repo sits exactly on the (0,1) floor** — a value
that means *"Poisson, or anything more clustered than Poisson, and we cannot tell which."*

### And the knowledge was already here, twice

`cross_substrate/axes.py:294` records **rail audit R-178**, which measured exactly this and in
stronger terms — *"`I.8_brody_q` is not merely degraded on the Tier-B substrates, it is ENTIRELY RAIL
— allen-hpf-cell 100.0%, buzsaki-port-cell 99.4%, pvc-11 99.4%, dr-port-cell 98.6%. Those coordinates
carry no information at all."* **An unbounded estimator, `I8_brody_q_unbounded`, was written in
response and sits in the registry.**

So: the failure was documented (TOOLKIT §9, two instruments), **the fix was built** (an unbounded
estimator, already deployed in the axis registry), and **15,195 banked values are still on the rail.**
That is the strongest available statement of the owner's point — *documenting a failure mode does not
immunize against it*, and neither does **fixing** it, if the fix is optional and the old key is
retained bit-identical for comparability.

### Consequence: the requirement moved into code

`detector_spec.ClassSpace` now refuses to construct unless **each endpoint declares what lies beyond
it and where such data is represented**; `None` is the admission that it has nowhere to go, and is
refused. It also carries `rail_check`, which reports the boundary-pileup fraction directly. This is
the structural analogue of the named-negative-set requirement, and it is the version that would have
caught all three instruments — because each would have had to answer *"what lies beyond Poisson?"* at
construction time, and none of them could.

### Rail concentration — measured before deciding, and it shrinks the problem to a read-through change

**Correction to my own 37.9% first.** That denominator wrongly included `brody_q_unbounded` values
(the substring `brody_q` matches both). Separating them: **15,174 of 20,558 BOUNDED Brody q values are
railed — 73.8%, not 37.9%.** The bounded estimator carries no information nearly three-quarters of
the time, which is *worse* than reported. But the migration is far smaller than either number suggests:

| railed | of | frac | cum | unbounded banked alongside? | file |
|---|---|---|---|---|---|
| 4,325 | 4,326 | **100.0%** | 28.5% | yes | `allen-hpf-cell.jsonl` |
| 3,983 | 4,006 | 99.4% | 54.8% | yes | `buzsaki-port-cell.jsonl` |
| 1,346 | 1,365 | 98.6% | 63.6% | yes | `dr-port-cell.jsonl` |
| 1,152 | 1,159 | 99.4% | 71.2% | **no** | `pvc-11.jsonl` |
| 986 | 1,139 | 86.6% | 77.7% | yes | `ibl-port-cell.jsonl` |
| 868 | 916 | 94.8% | **83.4%** | yes | `hc3-port-cell.jsonl` |

**Two facts decide the migration.**

1. **6 files carry 80% of all railed values** (of 44 with any). R-178's numbers were representative —
   the same cell datasets, at the same near-100% rates.
2. **91.7% of railed values (13,908 of 15,174) sit in artifacts that ALREADY carry an
   unbounded-estimator value alongside.** For those the repair is *already banked* — nothing needs
   recomputing, only a **read-through change** so the consumer sees the informative number.

**So the migration is not 15,195 recomputes. It is a read-through change covering 91.7%, plus one
file — `pvc-11.jsonl`, 1,152 railed values, no unbounded companion — that genuinely needs a decision.**
That is the boundary-rate collapse again: 105 → 19, and here 15,174 → effectively one file.
