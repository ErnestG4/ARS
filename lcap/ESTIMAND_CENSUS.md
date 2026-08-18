# Estimand Census — does the validation match the decision?

**Date:** 2026-08-16. **Why:** the L-policy arc found that its own cap was measuring
**separation of population means** while the gate it certified **classifies one point set at a
time**. the question before spending a session re-deriving one gate's caps: *is that mismatch
confined to this gate, or is separation-of-means the house idiom?* If the latter, the work is a
**policy change, not a cap fix**.

**Answer: not confined.** Two further instances found, both in **validation harnesses that certify
per-realization machinery using population-level statistics**, and both unremarked until now.

## The distinction being censused

| | certifies | correct estimand |
|---|---|---|
| a gate that classifies **one** point set | this realization | **per-realization error rate** (false-positive AND false-negative) |
| a claim about a **population** | the ensemble | separation of means / bias of the mean |

The deployed **judges** are fine — `longrange_discriminator._judge` compares one observation `o` to
a band, which is correctly per-realization. The mismatch lives one level up, in the code that
*validates* those judges.

## Instance 1 — `longrange_discriminator.validate_rate_unfold` (line ~411)

```python
sep = vr["sigma2"]["poisson"]["mean"] / max(vr["sigma2"]["gue"]["mean"], 1e-9)
...
sep_collapsed = all(o["pole_sep"] < 10 for o in out.values())
```

A **ratio of ensemble means** is one of the two arms deciding whether a lens is deployable. The
other arm (`decoy_false_rigid`) *is* per-realization, so this is a **mixed gate**: half correct.
The population arm produces the "pole separation collapses 60× → <4×" figure quoted in the module
docstring and carried into memory — a number that describes ensembles, used to justify a decision
about single-train deployment.

## Instance 2 — `validate_fitters.py` (lines 131–133)

```python
q_mean, rho_mean = float(np.mean(qs)), float(np.mean(rhos))
q_ok   = abs(q_mean   - exp_q)   <= tol
rho_ok = abs(rho_mean - exp_rho) <= tol
```

The fitter validation — the harness that certifies the calibrator zoo's fitters — passes when the
**mean across seeds** is within tolerance. But fitters are deployed **per substrate**: one substrate
yields one `q`. **A fitter whose per-seed values scatter wildly but average correctly passes this
validation and is useless in deployment.**

**Precise statement of the defect, because the mean test is not simply wrong:** it tests **bias**,
which is a real and legitimate property. What it does not test is **per-realization reliability**,
and nothing else in the harness supplies the missing half. So the validation is **incomplete for
certifying a per-realization gate** — exactly the shape of the cap error. Note the harness already
banks `brody_q_per_seed`: **the raw material for the correct test is present and simply isn't what
the PASS is computed from.**

## Consequence — the re-derivation is rescoped

Per Will: with the mismatch appearing in at least two further harnesses, the work is a **policy
change**, not a cap fix. The re-derivation should establish the per-realization form once and apply
it to every harness that certifies a per-realization gate, rather than repairing one gate's caps
and leaving the idiom in place.

## Design requirement carried into it: BOTH directions

the second pre-check. The misclassification table so far reports only **GOE earning
`RIGID_GUE`** (false positive). The complementary rate — **GUE failing to earn `RIGID_GUE`**, or
earning `HYPER_RIGID` (false negative) — is what determines whether a cap that fixes discrimination
destroys sensitivity. That is the L3 question restated at the correct estimand. A cap at L=8 with a
0.05 false-positive rate looks excellent until its true-positive cost is known. **Both rates, at
every candidate cap** — or the derivation gets revisited a third time.

## Scope note

This census covers classification/validation gates under `cross_substrate/`, `arsrh/`,
`rf_lenses/`. It is a *targeted* search for the population-vs-realization pattern, not an
exhaustive audit of every statistic in the repo; harnesses not listed were not cleared, they were
not examined. That distinction is itself the ADD-5 lesson applied to a census.

---

## Instance 1, RESOLVED — `pole_sep` is a LIVE LATENT DEFECT, not a documentation fix

the question: does the deployable verdict require both arms, or either? The code settles it:

```python
decoy_false_rigid = any(o["decoy"] == "RIGID_GUE" for o in out.values())   # per-realization
sep_collapsed     = all(o["pole_sep"] < 10 for o in out.values())          # ensemble means
out["INADEQUATE"] = bool(decoy_false_rigid and sep_collapsed)
```

`INADEQUATE` is a **negative** verdict — it *rejects* a lens. Requiring **both** arms to fire in
order to reject means **either arm can veto a rejection.** So the population-level arm holds veto
power over the per-realization arm: a lens whose decoy genuinely reads false-RIGID is **not**
declared inadequate if the ensemble separation happens not to collapse. The conjunction makes the
gate **permissive in the direction that matters**.

**This is a recurrence of a banked defect class** — `sealed_conjunction_inert_arm`: a conjunction in
which one arm can be inert makes the whole gate inert. It was filed once and has reappeared in a
gate written afterwards, which is itself the `knowledge_does_not_propagate` pattern.

**Bounding it honestly — the banked verdict is NOT wrong.** In the measured case *both* arms fired,
which is why rate-aware self-unfold was correctly rejected. The defect is **latent**: a false
negative that did not occur. Two further bounds from `audit/04-guardrails.md`: the self-test is
**not auto-run** by `longrange_verdict`, and **none of its five consumers call it** — so its blast
radius is small, though an opt-in gate nobody invokes is its own finding under
`verification_artifact_discipline`.

**Consequence:** re-run not required (no banked verdict depends on it); **repair required** — the
rejection should fire on the per-realization arm alone, with the ensemble ratio demoted to a
reported diagnostic. Filed as a fix for the policy work, not a documentation strike.

## Instance 2, BLAST RADIUS — narrower than feared, and it is not the zoo's class definitions

The zoo's calibrator classes (`calibration_anchors.CLASSES`: clock, GUE_b2, GOE_b1, GSE_b4,
uniform_jitter, poisson) are assigned **by their generators** — constructively. A fitted Brody q is
what the harness *measures and reports* for each already-known class; it is **not** what assigns the
class. **So the zoo's certifications do not inherit the defect.**

What does inherit it: **any claim that reads a fitted q from a single realization per substrate.**
The headline instance is the **brocot approximability stratification** (`ρ(rank, q) = −0.91`), where
each substrate contributes one q from one realization — a per-realization deployment of a fitter
certified on bias alone.

**Direction note, so the flag is not over-read.** A high-variance fitter *attenuates* a correlation.
Observing ρ = −0.91 despite whatever per-realization scatter exists is therefore evidence that the
scatter was small enough *for that claim* — but that is an inference from the result, not a
certification, and it would not protect a weaker or smaller-margin claim resting on the same fitter.
The correct reading: the claim is probably fine and is **uncertified**, and the fix (a few lines,
using data already banked) converts "probably" into "measured".

## Census scope — the named complement, per review

A reader cannot infer what a search missed from what it found. **Examined:**
`cross_substrate/`, `arsrh/`, `rf_lenses/` — classification and validation harnesses, searched for
the population-vs-realization pattern. **NOT examined, and therefore NOT cleared:**
`approximability/`, `thermo/`, `khinchin/`, `derivflow/`, `bridge/`, `comb/`, `survey/`,
`holonomy/`, `mathtest/refsuite/`, `audit/`, `verify/`, `riemann_explorer/`, and the top-level
phase scripts (`run_phase*.py`, `run_calibration.py`, `universality.py`'s consumers). Several of
those (`bridge/`, `comb/`, `survey/`, `holonomy/`) were built under the sealed-arc discipline and
carry their own per-realization gates, so they are *plausible* clean — but plausible is not
examined, and this list is what a follow-up census would have to cover.

---

## Census extension (2026-08-17) — the named complement, scanned

The previous section named 12 directories as *"not examined, therefore not cleared."* They have now
been scanned with an AST-based detector for the shape that matters: **a gate/verdict assignment
whose decision consumes an ensemble-collapsed value** (mean / median / average, including
`float(np.mean(...))` wrappers and `d["mean"]` lookups of precomputed means).

### The detector was validated on known answers first, and it is imperfect

Run against the two instances already confirmed by hand:

| known instance | detector |
|---|---|
| `validate_fitters.py` | **FOUND** |
| `longrange_discriminator.validate_rate_unfold` | **MISSED** |

**1 of 2 — so everything below is a LOWER BOUND with a measured false-negative rate, not a clean
census.** (The miss is instructive: `pole_sep` is a ratio of two dict lookups, and neither the
division nor the lookup names read as a collapse to a syntactic scanner. A pattern that hides from
its own detector is exactly why the "not examined ≠ cleared" label was worth writing down.)

### Result: 26 candidate sites across 19 files

**Candidates are not defects.** Each needs the judgement the census exists to make: *is the
operational decision about a realization or about a population?* Where the ensemble genuinely **is**
the question, a mean-based gate is correct. Triage of what I read:

- **Legitimate by design (ensemble is the decision):** `comb/exact_offsets.py:143` and
  `survey/mask_kag.py:111` — both are across-seed / across-tile grand-mean *bias* arms, built
  deliberately on the independent axis; `holonomy/*` seed-ensemble arms and family-wise controls,
  same. These are not the pattern.
- **Confirmed further instances of the pattern** (read and judged): `arsrh/taskB_falpha.py:195`
  certifies that an estimator recovers an analytic reference from the **mean of 8 draws**, while
  K(α) deploys per substrate; `cross_substrate/rf_decoy_battery.py:281,300` gate "period erased" on
  a **median across trials**, while the decoy question is asked of one train.
- **Defensible-by-intent:** `arsrh/phase3_sigma2.py:73` selects an *unfolding order* — an instrument
  setting, where "does this order preserve the known class ordering on average" is legitimately an
  ensemble question.
- **Unclassified candidates, left as such:** `approximability/class_probe.py`,
  `approximability/panel_B_farey.py`, `arsrh/cubic/r077_control.py`,
  `cross_substrate/population_temporal.py`, `derivflow/science_rate_question.py`,
  `intermittency.py`, `run_phase17_limits.py`, `run_phase17_pure_recovery.py`. **Not examined
  closely enough to classify — listed so the next pass has a work-list rather than a search.**

### Running total

**Four confirmed instances of the pattern repo-wide** (`validate_fitters`, `validate_rate_unfold`,
`taskB_falpha`, `rf_decoy_battery`), two of them repaired. All four sit in **validation or
calibration harnesses**; none is in a deployed judge. That distribution is itself the finding: the
judges were written to classify one thing, and the harnesses that certify them were written to
describe many.

## Census CLOSED (2026-08-17) — all 8 candidates classified, and the correct idiom already exists in-house

| site | classification |
|---|---|
| `approximability/class_probe.py:79` | **legitimate** — asks whether a *set* of cubics clusters; population is the question |
| `arsrh/cubic/r077_control.py:198` | **legitimate** — checks a null distribution is centred and correctly scaled, a population property by definition |
| `cross_substrate/population_temporal.py:101` | **legitimate** — within-vs-between across cells is inherently an ensemble comparison |
| `arsrh/phase3_sigma2.py:73` | **legitimate by intent** — selects an instrument *order*; "preserves the class ordering on average" is the right question for a setting |
| `run_phase17_limits.py:121` | **EXEMPLARY** — gates on **CI coverage**, a per-realization rate expressed as a mean over realizations |
| `run_phase17_pure_recovery.py:153` | **EXEMPLARY** — coverage **and** median relative error: the per-realization arm and the bias arm, both present |
| `approximability/panel_B_farey.py:64` | detector false positive — `dens_cv` summarises bins *within one* window, not across realizations |
| `derivflow/science_rate_question.py:216` | detector false positive — an `all()` universal quantifier over individual values, i.e. the *strictest* per-realization form |
| `intermittency.py:600` | detector false positive — **substring artefact: "aggre`gate`_fano" matched the word list**, and it is a stored statistic, not a gate |

### The useful discovery: the fix has a house precedent

`run_phase17_limits.py` and `run_phase17_pure_recovery.py` **already do exactly what the estimand
rule prescribes** — they gate on the fraction of realizations whose CI covers truth, which *is* a
per-realization error rate, and the recovery harness pairs it with a bias-style arm. So the repair
applied to `validate_fitters` is not a new idiom being imported; it is **an idiom the repo already
uses elsewhere and simply had not applied to the fitter harness.** That is a better argument for
adopting it than any appeal to principle, and it is the form to point at when the remaining two
instances (`taskB_falpha`, `rf_decoy_battery`) are repaired.

### Final tally, repo-wide

**4 confirmed instances** of the pattern (2 repaired: `validate_fitters`, `validate_rate_unfold`;
2 open: `taskB_falpha`, `rf_decoy_battery`) · **4 legitimate ensemble gates** · **2 exemplary
per-realization gates** · **3 detector false positives**. All 4 confirmed instances sit in
validation/calibration harnesses; none in a deployed judge. Scope reminder: the detector's measured
sensitivity was **1 of 2** on known positives, so the confirmed count remains a lower bound.

## Repair recipe for the two open instances (proposed, NOT installed)

Both remaining instances sit in **sealed arc runners** (`taskB_falpha.py` cites
`seals/TASKB_SEAL.json`; `rf_decoy_battery.py` is part of the Thread-E battery), so they are left
**proposed**: modifying a sealed runner would change banked outputs without a re-run anyone
authorised, which is the adoption doctrine already recorded in §9. What follows is the recipe, in
the form the house precedent uses.

**`arsrh/taskB_falpha.py:~191`** — currently `ks = np.mean(ks, 0)` over 8 draws, then a median
relative error against the analytic reference. That certifies the *ensemble mean* recovers the
reference. Add, alongside: compute the relative error **per draw**, and gate on the **fraction of
draws exceeding the tolerance** — the same quantity `run_phase17_*` calls coverage. Keep the
existing mean-based number as the bias arm; require both. The 8 draws are already generated, so the
per-draw errors cost nothing extra.

**`cross_substrate/rf_decoy_battery.py:281,300`** — currently `m7 = np.nanmedian(a7)` across trials,
gated `OK if m7 >= floor`. The decoy question ("did efficiency loss erase a genuine period?") is
asked of **one** train. Add: the **fraction of trials with `a7 < floor`**, gated at a rate fixed in
advance; keep the median as the central-tendency arm.

In both cases the change is additive, the raw per-realization values already exist in the loop, and
the pattern to copy is in-repo (`run_phase17_pure_recovery.py`: coverage **and** median relative
error, both reported, both required).

## Both open instances REPAIRED (2026-08-17) — and one of them found a live defect

The earlier "leave them proposed, they sit in sealed runners" call was **over-strict and is
corrected**: `TASKB_SEAL.json` pre-registers *claims* (predictions, anti-claim, failure conditions)
and does **not** blob-freeze the runner; `rf_decoy_battery` has no seal referencing it at all. An
additive arm therefore cannot violate a pre-registration or move a banked verdict.

**`arsrh/taskB_falpha.py` — repaired, came back CLEAN.** The gate certified that the ensemble mean
of 8 draws recovers the analytic reference while K(α) deploys per substrate. Per-draw errors are now
kept and the fraction exceeding tolerance reported: **0.00 for both Poisson and GUE.** The estimator
*is* per-realization reliable, so the mean-based gate was not hiding anything here. Banked as a
measured negative. *(The arc was started to exercise the arm and killed once the gate block printed
— letting it finish would have rewritten its banked measured JSON, re-deriving another program's
results as a side effect. Banked JSON confirmed untouched.)*

**`cross_substrate/rf_decoy_battery.py` — repaired, and the arm immediately found something.** Both
3a and 3b gated on a **median across seeds**, while the decoy question ("did efficiency loss erase a
genuine period?") is asked of **one train**. With the per-train rate added, at p_keep = 0.4 the
median a_q@7 is 11.70 — comfortably above the calibrated floor of 6.098, gate says OK — while
**per-train survival is 0.75: one train in four loses the period the gate certifies as surviving.**

**The contrast is the evidence.** A rule that flagged everything it touched would only be finding
what it was looking for. One instance clean, one instance a live defect, is the rule discriminating.

### Follow-up: the p_keep dependence, and a control that changed the reading

Deployed values matter here, so they were checked rather than assumed. The named decoy classes use
p_keep **0.90** and **0.75**; `instrument_confound`'s trajectory sweep defaults to removal fractions
`(0.0 … 0.5)`, i.e. **p_keep down to 0.50** — inside the range of interest. Measured at 32 seeds:

| p_keep | 0.75 | 0.70 | 0.65 | 0.60 | 0.55 | 0.50 | 0.45 | 0.40 |
|---|---|---|---|---|---|---|---|---|
| per-train survival | 0.91 | 0.78 | 0.78 | 0.84 | 0.81 | 0.75 | 0.78 | 0.78 |

Two things this says, and one it does not:

1. **The battery's own printed `survival 1.00` at p_keep = 0.7 is a small-sample artifact.** At 32
   seeds the rate there is **0.78**; 8/8 is entirely consistent with a true rate of 0.78 (p ≈ 0.14).
   The first repair's own output needed the same sample-size scepticism as everything else.
2. **The curve is essentially FLAT across 0.40–0.75** — it does not degrade with thinning depth.
   That is *not* the signature of thinning erasing a period.
3. **So the attribution is not yet established.** A flat ~20% failure rate across all thinning
   levels is equally consistent with intrinsic seed-to-seed variability in the `periodic_q7`
   generator — some realizations simply do not show a strong a_q = 7 peak, thinning or no thinning.
   The decisive control is the **unthinned** case at the same seed count (`premise before
   mechanism`: establish *that* thinning causes it before attributing to thinning).

**Control result — attribution established, and both of my earlier readings needed correcting.**
Unthinned (p_keep = 1.0), same 32 seeds, same floor: **per-train survival 0.94.**

| | survival | reading |
|---|---|---|
| p_keep = 1.00 (control) | **0.94** | ~6% of trains fail with **no thinning at all** — intrinsic generator variability |
| p_keep = 0.75 (deployed) | 0.91 | barely above the intrinsic floor |
| p_keep = 0.70 → 0.40 | 0.75–0.84 | a **step**, not a gradient |

So: **thinning does erase the period in a real fraction of trains** — the failure rate roughly
triples from ~6% to ~20% — but it is **not the whole story**, and the dependence is a *step* between
0.75 and 0.70 rather than a slope that deepens with thinning. Corrections to what I wrote before the
control existed: "one train in four loses the period" is right as a raw rate but **~6 points of it
are intrinsic**, so the thinning-attributable share is ~19 points; and "the flat curve suggests
intrinsic variability" was too strong — the control at 0.94 sits distinctly above the 0.75–0.84
band, so thinning is genuinely implicated.

**Status: a real defect in the gate's certification, with the size now properly decomposed.** At
every deployed thinning level the median-based gate certifies survival while 9–25% of individual
trains fail, of which ~6 points would fail anyway. The repaired arm reports the per-train rate so a
reader sees both. Whether the gate's *threshold* should move is the owning program's call; this arc
supplies the decomposition, not the ruling.

## Two findings that must NOT be absorbed into the thinning story

**(A) The small-n boundary-rate problem — a separate, invisible defect class.** The battery's printed
`survival 1.00` at p_keep = 0.7 was not a bug in the repair; it was **a certification computed at a
sample size too small to distinguish "always survives" from "survives 78% of the time."** Unlike the
estimand mismatch, this one gives no signal: a clean 1.00 looks like the strongest possible result.
Swept the banked artifacts: **105 rates sit at exactly 0.0 or 1.0**, mostly with no denominator
recorded beside them (concrete: `high_osi_super_frac = 1.0` at **n=4**, whose 95% lower bound is
≈ 0.40). Filed as a standing sweep target with its own TOOLKIT §9 rule; each such rate needs its n
recovered and an interval attached before it can be read.

**(B) ~6% intrinsic failure is a property of the GENERATOR, not of any gate.** The unthinned control
shows **6% of `periodic_q7` trains fail their own period test with no thinning at all** — roughly one
in sixteen. That is not something the thinning story explains and **it must not be absorbed into
it**: it says the decoy generator emits trains that do not exhibit the period it is built to
inject. Whether that is expected depends on the generator's design (jitter amplitude, train length,
the a_q estimator's own floor at that n), none of which this arc examined. **Registered as an open
question against the generator**, separate from the thinning defect, and separate from the gate's
certification threshold.

### Boundary-rate sweep — denominator recovery first, and it collapses fast

Triage before re-measuring anything, because a boundary rate whose n is unknown cannot even be
sorted: **105 boundary rates → 64 carry a recoverable sibling denominator, 41 do not.** Of the 64,
**19 have n < 20** — that is the actual work list, and it is small. Concrete banked rows currently
reading as certainty:

| row | value | n | 95% lower/upper bound |
|---|---|---|---|
| `phase37/…frac_reg` | 1.0 | 17 | ≥ 0.82 |
| `phase28…sign_consistency_frac` | 1.0 | 12 | ≥ 0.76 |
| `phase34c…fraction_modal` | 1.0 | 10 | ≥ 0.72 |
| `phase37/…frac_clust` | 0.0 | 6 | ≤ 0.39 |
| `longrange_allen_psth…high_osi_super_frac` | 1.0 | 4 | ≥ 0.40 |

**22 of the 41 denominator-less rows are in this session's own `rigidgate/` artifacts** — the sweep's
first obligation is therefore our own house, and those n are recoverable from the committed
generators, which is precisely what the committed-generator rule was for.

### The intrinsic ~6% is UNATTRIBUTED — the earlier filing was premature

The estimator-floor explanation was tested **before** anything else, because if the a_q estimator
itself fails at that train length then the failure is not in the generator and the open question is
misfiled. Discriminator: for each unthinned train, is the a_q **peak** still at q=7? Peak at 7 but
below floor ⇒ the period is present and the estimator did not resolve it. Peak elsewhere ⇒ the train
genuinely lacks the injected period.

| unthinned, 32 seeds, median 400 events | count |
|---|---|
| survive (a_q@7 ≥ floor) | 30/32 |
| fail, **peak still at q=7** → estimator power | **1**/32 |
| fail, **peak elsewhere** → generator | **1**/32 |

**One each — the 6% cannot be attributed at this sample size.** Two failure events split evenly
between two mechanisms resolves nothing, and each count of 1 carries an interval spanning roughly
[0, 16%].

So the honest state is **unattributed**, not "a property of the generator". The earlier phrasing
named a mechanism from **two events** — the same small-n error this section exists to document,
committed one level up, and caught only because the estimator explanation was checked rather than
assumed away. Attribution needs on the order of **10× the seeds** (~20 failure events) to separate a
~3% estimator floor from a ~3% generator floor. **Registered with that cost attached, and against
neither component until it is paid.**

### The 19-row cut, computed — and the interval choice decides the borderline

Applying Clopper–Pearson (exact, conservative — the right choice because a boundary rate is an
*at least* claim) to the 19 small-n rows:

| n (k=n) | CP lower bound | treatment |
|---|---|---|
| 4 | **0.398** | **UNINFORMATIVE** — spans a coin flip; must be marked as carrying no result |
| 6 | 0.541 | real but overstated → restate at the bound |
| 10 | 0.692 | real but overstated → restate at the bound |
| 12 | 0.735 | real but overstated → restate at the bound |
| 17 | 0.805 | real but overstated → restate at the bound |

**A single sweep verdict across all 19 would be wrong in both directions**, exactly as anticipated:
the n=4 rows carry no result and marking them "overstated" would credit them with one, while the
n=17 rows *are* findings and marking them uninformative would discard real evidence. **Two
treatments, split at the point where the interval crosses 0.5.**

**And the interval choice is not cosmetic:** Wilson gives 0.510 for 4/4 where Clopper–Pearson gives
0.398 — the two disagree precisely at the borderline row, one calling it a result and the other
calling it noise. Naming the interval is therefore part of the rule, not a footnote to it.

### Is the 6% attribution worth paying for? — answered on consequence, and the answer is "not as posed"

The queue entry said "attribution needs ~10× the seeds." Before that sits as a default yes, the
question is what decision changes on each branch:

- **If estimator-side:** a_q has a detection floor at ~400 events *on trains that provably contain a
  period*. That propagates to **every a_q reading at that train length, including real substrates** —
  it would mean banked a_q verdicts on short trains carry an unquantified miss rate. **Consequential.**
- **If generator-side:** the decoy generator emits off-spec trains a few percent of the time. That
  perturbs the *calibrated floor* (computed from those trains) but does **not** propagate to
  real-substrate readings. **Narrow.**

So the branches genuinely differ — but **the 10× seed run is the wrong instrument for the
consequential one.** Paying 10× to split 3% from 3% answers "which mechanism", when what matters is
only "does a_q miss periods it should catch at this train length". That second question is
answerable **far more cheaply and more directly**: inject a period at high SNR (minimal jitter),
sweep train length, and measure the detection rate on trains known by construction to contain it.

**Recommendation: do not pay the 10×.** Run the targeted estimator-floor test instead. If a_q detects
at ~100% on high-SNR trains at n≈400, the consequential branch is retired and the residual 6% can sit
**unattributed indefinitely with its honest label** — which is already banked and costs nothing to
leave. If a_q *does* miss at high SNR, that is a documented instrument property worth having on its
own terms, independent of the decoy question that surfaced it. Queue entry amended accordingly:
the 10× attribution is **withdrawn**; the targeted test replaces it.
