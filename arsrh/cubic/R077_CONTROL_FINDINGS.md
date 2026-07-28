# R-077 — testing the PREMISE before the mechanism

**Seals:** `arsrh/seals/R077_CONTROL_PRECOMMIT.json` + `_ADDENDUM_1.json`, both written **unrun**.
**Code:** `arsrh/cubic/r077_control.py`, `r077_lookelsewhere.py`, `r077_conditional.py`.
**Scope gate (§0):** this measures a property of continued-fraction orbits and of an estimator.
It does not estimate Λ, does not bear on RH, and does not touch boundedness of partial quotients.

---

## 0. What was wrong with how this thread was proceeding

R-158 left R-077 with a sharp-sounding question: *does the residue mod Δ carry information about
the future beyond y?* That question asks **why** the prediction
`P(g|event) = E[(1+y)1{g}] / E[(1+y)]` fails.

It was never established **that** it fails. The +3.30 sem was never compared against an orbit for
which the prediction is a **theorem** — so "the prediction is off by 3.3 sem on cubics" and "this
estimator is off by 3.3 sem on *anything*" had not been separated. Asking why before establishing
that is how a thread spends months on an instrument artifact.

Two further defects, both mine, found while setting this up:

- **The analysis code was in `/tmp`.** R-156 and R-158 banked numbers into the register from
  scripts in a session scratch directory. The prose was committed; the code was not. A number
  whose generating code is in a temp directory has **no provenance** — it cannot be re-run,
  audited, or regression-tested. Fixed: `r077_conditional.py` is a *verbatim* consolidation (not
  an improved one, so it reproduces what was banked) and it does: **+3.30 iid, +3.07 block,
  predicted 0.0682 vs measured 0.1057, n_events 492.**
- **No trials factor, anywhere.** The +3.30 is the most interesting cell of **nine**. Neither the
  register nor any seal states a multiplicity correction. A per-cell z reported as a global
  significance is the sem-vs-CI family in a new costume: a number correct for the quantity it
  measures, filed in a slot that owns a different one.

---

## 1. The control, and why this one

**A generic real through the identical pipeline.** Same `certified_cf` at DIG=1200/NPQ=1400, the
six |t|=13 matrices **verbatim**, same A=20, same 45-term tail guard, same pooling, same z
formula. The only thing swapped is the number.

**Why the density matches:** for almost every real the Gauss natural extension is ergodic, so
(x_n, y_n) equidistributes w.r.t. `1/(ln2·(1+xy)²)` **exactly** — the density the prediction is
derived from. H0 holds by theorem, not by assumption.

**The control I rejected, recorded because it was my first design:** an i.i.d. Gauss–Kuzmin
a-sequence. It is the obvious null and it is the **wrong density** — drawing a_i i.i.d. makes
`x = [0;a_{n+1},…]` and `y = [0;a_n,…,a_1]` functions of disjoint independent blocks, hence
*exactly* independent, whereas a real orbit couples them by `1/(1+xy)²`. It would have tested a
different object. *(Null must match the generating construction, including its curvature.)*

---

## 2. Result — SEALED OUTCOME B

**Instrument gate passed first:** n_events median **482** vs the cubic's 492; CF length median
**1163**; g-divisor set exactly **{1, 13, 169}** in every one of 200 replicates.

| | control (200 generic reals) | cubic |
|---|---|---|
| mean z(g=13) | **−0.020** (sem 0.070) | — |
| sd z(g=13) | **0.985** | — |
| 99th percentile | **+2.18** | — |
| observed | — | **+3.30** |
| P(control ≥ observed) | **0 / 200** | |

**The estimator is unbiased on continued-fraction orbits: z ~ N(0,1) to within its own sem.**
So the +3.30 is not an estimator artifact. The premise survives.

### The powered falsifier, and it fires

A quiet control is worthless unless it could have spoken. The injection arm builds, by hand,
exactly the dependence R-158 hypothesises — a_{n+1} pushed into the event range with probability
δ whenever the residue at n lies in the g=13 class:

| δ | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|---|
| mean z | **−0.04** | +1.22 | **+3.51** | +6.49 | +13.30 |

Silent at δ=0, firing at +3.5 by δ=0.05. **Sensitivity and specificity both demonstrated by
construction rather than asserted**, which is what licenses reading an absence from this
instrument at all.

**Effect-size calibration — the number any mechanism must reproduce:** the observed +3.30
corresponds to **δ ≈ 0.047**, i.e. the cubic anomaly is the size of about **4.7% of g=13-residue
indices having their next partial quotient pushed into the event range.** This converts a z into
something a mechanism can be held to.

---

## 3. What this arm does and does not license

**Excluded:** estimator bias shared by all CF orbits — the whole class of "the formula is just
wrong" explanations.

**Also excluded, and *stronger* than the parent seal credited:** the seal listed "the specific
matrices M being unusual" among confounds *not* excluded. That was over-cautious — the control
holds M **verbatim** and flips only the number, so the matrix confound *is* excluded. Recorded
here rather than by editing the seal.

**NOT excluded by this arm:**
- The look-elsewhere effect over 9 branches — **the addendum arm**, run separately.
- Any mechanism. Nothing here says *why* the prediction fails on cubics.
- Generality: these are 20 particular cubic fields, not "cubics".

**Specificity prior held FIXED per the seal.** A clean control excludes *one* confound. An
instrument sensitive enough to beat a prior can, by the same sensitivity, resolve unnamed
confounds — "resolves more" must not couple to "what it resolved is real."

---

## 3b. The look-elsewhere arm — SEALED OUTCOME LE_A

The +3.30 is the most interesting cell of **nine**. No trials factor existed anywhere.

**Empirical max-|z| null** — exact rather than Bonferroni, and it correctly handles the fact that
branches within a stratum are *not* independent (their proportions sum to 1):

| | value |
|---|---|
| max-\|z\| null, 95th pct | **2.633** (a single N(0,1) gives 1.96 — **that gap is the trials factor**) |
| max-\|z\| null, 99th pct | 3.517 |
| observed T = max\|z\| | **3.5871** at \|t\|=5, g=25 |
| **p** | **0.0100** (2/200) |
| Wilson 95% CI on p itself | **[0.0027, 0.0357]** — below 0.05 across the *whole* interval |

All nine per-branch control means sit in [−0.15, +0.18], sd 0.88–1.02: **the estimator is unbiased
on every branch**, not just the reported one.

**Corrected p per branch:**

| branch | cubic z | corrected p | |
|---|---|---|---|
| \|t\|=5, g=25 | **−3.5871** | **0.0100** | survives — *depletion* |
| \|t\|=13, g=1 | −3.2867 | **0.0150** | survives |
| \|t\|=13, g=13 | **+3.2954** | **0.0150** | survives — *enrichment*, R-156's cell |
| \|t\|=5, g=5 | +2.0333 | 0.2050 | |
| all others | | ≥ 0.345 | |

Three survive; g=1 and g=13 within |t|=13 are the same fact, so there are **two independent
surviving effects**.

### The largest effect had been set aside for a reason that did not apply to it

R-158 discarded the |t|=5 rows because their block bootstrap returns n_eff/n > 1 — overlapping
blocks under-dispersing. **That diagnostic is right, and it impeaches `z_block` only.**
Under-dispersion inflates the *block* z; it says nothing about `z_iid`, which was never impeached.
The whole row was dropped on a criticism of one column — and the row contained the **largest
effect in the table and the best corrected p of all nine**.

So: **R-156's cell does survive** (p = 0.0150). It is simply not the strongest, and the strongest
points the **other way** — depletion at g = t², not enrichment at g = t. Any third localisation
must address both. *Correct-fact / wrong-slot, mine, again.*

**Filed as a candidate, explicitly not a finding:** in both live strata Δ = t², so g ∈ {1, t, t²}
and the transfer factor g²/Δ ∈ {1/t², **1**, t²}. The enriched branch is g = t in both — exactly
where the transfer law λ′ = (g²/Δ)λ is **neutral**. This is the "it all fits together" shape, which
is the signal to run discipline rather than the reward: a **rhyme until proven an identity**.

---

## 4. A number that was never a candidate, stated before the run so it could not become an insight

The (1+y) reweighting moves the |t|=13, g=13 prediction from **0.0674** (marginal) to **0.0682**
(weighted) — **0.07 sem**, against a discrepancy of **3.30 sem**. The weight is **47× too small**
to have ever explained the gap.

R-156's "the weight is negligible" is therefore correct but under-stated. The honest form: **this
apparatus has essentially no power to test the weight, and the weight was never the live
hypothesis.** The derivation was worth doing — it is exact and it is now verified to 1e-16 — but
it was never going to close R-077, and a candidate that could not have explained the effect is
not really a candidate eliminated.

---

## 5. Two corrections to banked prose

- **R-156 says "pooled over 8 objects per stratum."** The |t|=13 stratum contains **six** objects
  (`collect_cyclic`'s `per` is a cap; only 6 cubics in the box have |t|=13). The banked z is
  unaffected — the pooling used whatever was there — but the stated n is wrong.
- **R-158's localisation sentence is under audit**, not accepted: "the residue mod Δ is a function
  of the full past that y does not determine." The standard CF identity `q_n/q_{n-1} =
  [a_n; a_{n-1},…,a_1]` makes `y_n = q_{n-1}/q_n = [0; a_n,…,a_1]` — which *determines* the whole
  past, hence determines the residue. If that holds, the sentence is false and the real
  localisation is a **joint equidistribution** failure of the skew product on
  [0,1]² × (ℤ/Δ)², not a "y doesn't determine the residue" failure. Referred to the review agent
  for independent computation; **not banked either way here.**
