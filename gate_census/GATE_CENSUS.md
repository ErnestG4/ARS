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

**⇧ RECALIBRATED 2026-08-21 BY THE SWEEP — the finding is not what it was written as.** It was filed
as *"three instruments independently share a defect."* Measured across all 11 distinct classifier
implementations: **9 of 11 have no rejection region, or one whose complementary rate is unrecorded.**
The prediction (4–6) missed **high** under both readings, and its stated reasoning — *"no rejection
region is a severe, rare defect"* — is **falsified**. It is neither severe-and-rare nor a coincidence
of three:

> **One-sidedness is what an UNAUDITED classifier looks like. Two-sidedness is an artifact of audit.**

**Independently rederived along a second axis (2026-08-22).** The C3 divergence inventory — a
*separate* generator under a *separate* sealed rule, asking about behavioural differences rather than
negative sets — flagged the KS distances themselves as **computed but never compared** in several
variants. Not a false positive: `min()` is a call, not a comparison, so in those variants the
distances are consumed by the **argmin** and never tested against any threshold. **Selection without
rejection, reached by two sealed instruments along different axes.** As close to independent
confirmation as static analysis gets.

The three instruments were not unlucky; they were **sampled from the default**. No instrument in this
codebase acquired a rejection region except through deliberate intervention — every exception was
manufactured. This also **dissolves the selection worry raised when the sweep was sealed** (that Gate 1
might have been examined first *because* something smelled wrong): it was not unusual, it was the
house style, sampled. **Any future instrument should be assumed one-sided until its negative set is
named and measured** — that is now a prior with a measured base rate, not a caution.

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

### The rail is ONE FLOAT, repeated — and pvc-11's recompute is already refused by the repo's own gate

Investigating the pvc-11 recompute turned up the closing datum. `cross_substrate/fitter_validation.json`
**already measured this**, in its own words:

- clustered case: **expected q = −0.3**, bounded `brody_q_mean` = **6.611e-05**, `brody_q_pass` = **False**
- the **repaired/unbounded** estimator on the same data: **−0.1235 / −0.1462 / −0.1322**, `pass` = **True**
- reliability: **sd = 1.42e-20** across 12 seeds, `railed` = True, status = **`UNCERTIFIABLE_RAILED`**
- and therefore **`all_pass = False`** — *the fitter gate is False because of exactly this case*

**So the recompute answer changes: the current pipeline does not need to be asked to add an unbounded
companion for pvc-11 — it already REFUSES to emit bounded Brody at all** (`_matched_axes` sets
`I.8_brody_q = None` when the gate fails). The 1,152 pvc-11 values are outputs the repo's own gate
would no longer produce. What the file needs is the **repaired** estimator, which the validation shows
passing.

**And the rail is not 15,174 measurements that happened to land at zero. It is ONE FLOAT.** The value
`6.610696135189609e-05` appears **bit-for-bit identical**:

| occurrences | file |
|---|---|
| 4,325 | `allen-hpf-cell.jsonl` |
| 3,983 | `buzsaki-port-cell.jsonl` |
| 1,346 | `dr-port-cell.jsonl` |
| 1,152 | `pvc-11.jsonl` |
| 985 | `ibl-port-cell.jsonl` |
| 919 | `population-temporal.jsonl` |

Six substrates, ~12,700 slots, **one number to sixteen significant figures** — the bounded optimizer's
floor output, not a property of any dataset. `sd = 1.42e-20` across seeds is the same fact from the
other side. **A railed coordinate does not carry degraded information; it carries the optimizer's
return address.**

### Provenance of the rail constant — the solver's terminal step, NOT a hardcoded floor

The exact figure decides how to describe the artifact, so it was measured rather than assumed. Source
inspection rules out a written-down epsilon immediately — there is no `max(q, …)` anywhere and the
bound is literally `(0.0, 1.0)`:

```python
minimize_scalar(nll, bounds=(0.0, 1.0), method="bounded", options={"xatol": 1e-4})
```

`method="bounded"` is scipy's Brent-bounded (`fminbound`), so the `differential_evolution`/grid-seed
candidate is out too. Four tests, all agreeing:

| test | result | reading |
|---|---|---|
| **vary `xatol`** | 1e-3→**3.998e-4**, 1e-4→**6.611e-5**, 1e-5→**5.961e-6**, 1e-6→**5.363e-7** | **scales with the tolerance** (≈0.4–0.66 × `xatol`) — a solver stopping point, not a constant |
| **move the lower bound** | (0,1)→6.611e-5; (−0.5,1)→**−0.49994**; (−1,1)→**−0.5617** | the value **vanishes** when the bound moves; at (−0.5,1) it simply rails on the NEW bound |
| **different data** | three independent clustered draws → **identical to 17 significant figures** | carries **zero** information about the data |
| **interior optimum** | Poisson-ish draw → 0.00411, varying | the estimator works fine when the optimum is inside |

**Verdict: `6.610696135189609e-05` is the terminal step of Brent's bounded search sitting a
tolerance-scaled distance inside a lower bound of exactly zero.** The correct sentence for the record
is *"the optimizer's terminal step inside a bound at zero"*, **not** *"a floor constant in the
wrapper"* — so there is **no magic number loose in the codebase** and the reach is confined to
bounded-solver call sites.

**But test 2 also delivers the substantive number:** with room to move, the clustered synthetic's true
optimum is **q ≈ −0.56** — a genuine interior minimum. The banked rail was standing in for a real,
strongly negative value.

**Where else the same exposure exists** — every `method="bounded"` call whose optimum can lie outside
its bounds: `axes.py:160` (Brody, the known case), `axes.py:246` (Berry–Robnik ρ, also `(0.0, 1.0)`,
and `axes.py:212` already documents that ρ saturates), `brody_cut_diagnostic.py:34`,
`overnight_2026_07_12/run_overnight.py:346`, `phase34e/run_berry_robnik.py:128,144`, and
`bridge/dpp_python.py:72,86` (bounds `(1e-3, amax)` and `(1e-4, 100.0)` — lower bounds *near* zero,
same shape). **The general tell, now checkable by grep: a bounded solver whose bound is a
scientifically reachable value rather than a mathematical impossibility.**

### Bounded-solver triage — MATHEMATICAL bounds vs CONVENTIONS encoding a prior

These are **two different defects with the same symptom**, and they need different fixes. A class
space with Poisson as an endpoint is a *modelling choice about what can be represented* → fix is a
**wider class space**. A bound at 0 on a parameter where negative means clustering is a *constraint
accidentally encoding a prior* → fix is **move the bound**. Both rail, both silently.

The census question is the one already asked of class spaces: **what lies beyond this endpoint, and
can data legitimately go there?**

| # | site | bound | beyond it | verdict |
|---|---|---|---|---|
| 1 | `axes.py:160` Brody q | (0.0, 1.0) | **q<0 = clustering, physically real** — measured optimum **−0.56** | **CONVENTION** — repaired via `_unbounded` |
| 2 | `axes.py:191` Brody unbounded | (−1.0, 4.0) | q<−1 for extreme clustering | **WIDER CONVENTION** — "unbounded" is a misnomer; still a bound, just further out |
| 3 | `axes.py:246` Berry–Robnik ρ | (0.0, 1.0) | **nothing — ρ is a mixing fraction** | **MATHEMATICAL** — saturation is a real answer (pure Poisson / pure GOE), and the rail census found only **0.2%** there, consistent with that |
| 4 | `brody_cut_diagnostic.py:34` | `(lo, hi)` **required args, no default** | caller's choice | **CALLER-DETERMINED** — low risk |
| 5 | `run_overnight.py:346` | (−1.0, 4.0) | as #2 | already the wide version |
| 6 | `phase34e/run_berry_robnik.py:128,144` | (0.0, 1.0) | nothing | **MATHEMATICAL**, as #3 |
| 7 | **`bridge/dpp_python.py:72,86`** | (1e-3, amax), (1e-4, 100.0) | **α→0 = no repulsion; κ→0 = no clustering — both reachable** | **NUMERICAL GUARDS, and see below** |

**The DPP bridge carries a one-sided boundary check.** `fit_dpp` records
`at_boundary = bool(res.x > 0.995 * amax)` — it tests the **upper** bound (a genuine DPP existence
condition) and **never the lower one**, which is the numerical guard at `1e-3`. `fit_thomas` has no
boundary check at all on `(1e-4, 100.0)`. So a fit that has railed at "no repulsion" or "no
clustering" is reported as **a small but measured value**, not as a rail — and 1e-3 does not announce
itself the way 0.0 does. **One-sided boundary reporting, in the same session and the same shape as
one-sided calibration.** Not swept here; registered as the next bounded-solver item.

**Keep visible, because it is the size of the error and not merely its sign:** the clustered synthetic's
true optimum is **q ≈ −0.56**, banked as **6.6e-05**. That is not a slightly-shifted value — it is a
substantial clustering signal reported as *marginally more Poisson than Poisson*, **at the wrong sign
entirely**.

---

## Pre-brief verification (2026-08-19) — four claims tested, two of mine wrong

Run before committing the next-session brief, because three of its cells rested on unverified reads.

**1. C2 is VIABLE — my worry that the repaired estimator would also rail is REFUTED.** Read-only probe
over 140 pvc-11 cells:

| estimator | result |
|---|---|
| bounded `I.8_brody_q` | **100% railed**, and **100% exactly `6.610696135189609e-05`** |
| repaired `I.8_brody_q_unbounded` | **0% railed** at either bound; range **−0.571 … −0.077**, median **−0.412** |
| sign | **100% negative** |

Every probed pvc-11 cell is clustered, with median q ≈ **−0.41**, and the bounded fit reported all of
them as the same positive constant. The repair has ample headroom (worst −0.571 against a bound at
−1.0), so **C2 works and does not need a wider bound.**

**2. C2's destruction risk is CONFIRMED.** With `all_pass: False`, `_matched_axes` nulls
`I.8_brody_q` and leaves `I.8_brody_q_unbounded` populated. So running `phase2b_recompute.py pvc-11`
today would **add the repair and destroy the 1,152 banked bounded values in one pass** — breaking
bit-identical retention on the one file the accessor exists to protect. Verified against a copy; the
artifact was not touched.

**3. C1's DPP item is LATENT, not live — this changes the brief's premise.** Swept every banked
`alpha`/`kappa`: **558 α values, min 0.022** (22× the 1e-3 bound); **17 κ values, min 1.2**
(12,000× the 1e-4 bound). **Zero at a lower bound.** The one-sided boundary *reporting* gap in
`fit_dpp`/`fit_thomas` is real and worth fixing, but it has **produced no damage** — the code is
one-sided, the data never went there.

**4. Coverage self-test on the rail census — honest partial.** Pattern-matching banked keys flagged
**251** that the census's `brody_q|berry_robnik|rep_int` match would miss. Checked the largest,
**`rho1` (1,439 values)**: it ranges **−0.79 … 0.59**, so it is a correlation coefficient, not a
bounded fit — out of scope, and my self-test over-counted the same way the one-sided-calibration grep
did. The remaining 250 are unchecked, so **census coverage is a lower bound, better than the naive
test suggested and not proven exhaustive.**

**Consequence for the brief: C1 is not the live cell.** The only site with banked damage is Brody at
73.8%, already addressed by C2 plus the accessor. Everything else measured clean — Berry–Robnik 0.2%
(mathematical bound, a real answer), `rep_int` 2.4% on n=83, DPP/Thomas 0%. **C1 is a classification
and prevention cell, not damage discovery**, and it can follow C2 rather than precede it.

### C2 population join — "100% railed" survives, but its SCOPE does not

The brief said *"measured on 140 cells: bounded 100% railed."* The file shows **1,152 railed of 1,159
= 99.4%**. Two correct numbers, and the unverified assumption was that they describe the same
population. Joined, read-only:

**The 7 interior fits, and where they live:**

| value | cell |
|---|---|
| 0.1012 | `monkey5_spontaneous/M5_ch086_u2` |
| 0.0967 | `monkey2_gratings_movie/M2_ch032_u2` |
| 0.0878 | `monkey2_gratings/M2_ch017_u1` |
| 0.0544 | `monkey5_spontaneous/M5_ch032_u2` |
| 0.0340 | `monkey3_gratings/M3_ch090_u1` |
| 0.0321 | `monkey2_gratings/M2_ch060_u1` |
| 0.0252 | `monkey1_gratings/M1_ch057_u1` |

**Result: 0 of the 7 lie inside the 140-cell roster, and banked values on the roster are 140/140 at
the rail constant. "100% railed on the 140" STANDS.**

**But the join exposes a scope limit the count alone hid.** The roster covers **three recordings, all
`_spontaneous`** (monkey1/2/3) — the probe took the first 140 cells it could process and never reached
a gratings condition. **Five of the 7 interior fits are in gratings or movie conditions**, and the
other two in `monkey5_spontaneous`, which the roster also never reached.

So the honest C2 characterisation is narrower than the brief's: **median q = −0.412, 100% negative, is
measured on spontaneous-condition cells from 3 of 15 recordings.** It does *not* establish that
gratings-condition cells behave the same — and the interior fits being **concentrated in exactly the
conditions the probe missed** is mild evidence they may not. **"pvc-11 is uniformly clustered" must
become "pvc-11 spontaneous is uniformly clustered"** until the full run says otherwise.

**Consequence for C2's execution:** the full run covers all 1,159, so the write-up must recompute the
characterisation on the complete set rather than quoting the probe. The probe's job was viability, and
it did that — the repaired estimator has headroom and does not rail. Its numbers are not the finding.
