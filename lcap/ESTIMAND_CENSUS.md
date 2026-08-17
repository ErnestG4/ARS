# Estimand Census — does the validation match the decision?

**Date:** 2026-08-16. **Why:** the L-policy arc found that its own cap was measuring
**separation of population means** while the gate it certified **classifies one point set at a
time**. Will's question before spending a session re-deriving one gate's caps: *is that mismatch
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

Will's second pre-check. The misclassification table so far reports only **GOE earning
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

Will's question: does the deployable verdict require both arms, or either? The code settles it:

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

## Census scope — the named complement, per Will

A reader cannot infer what a search missed from what it found. **Examined:**
`cross_substrate/`, `arsrh/`, `rf_lenses/` — classification and validation harnesses, searched for
the population-vs-realization pattern. **NOT examined, and therefore NOT cleared:**
`approximability/`, `thermo/`, `khinchin/`, `derivflow/`, `bridge/`, `comb/`, `survey/`,
`holonomy/`, `mathtest/refsuite/`, `audit/`, `verify/`, `riemann_explorer/`, and the top-level
phase scripts (`run_phase*.py`, `run_calibration.py`, `universality.py`'s consumers). Several of
those (`bridge/`, `comb/`, `survey/`, `holonomy/`) were built under the sealed-arc discipline and
carry their own per-realization gates, so they are *plausible* clean — but plausible is not
examined, and this list is what a follow-up census would have to cover.
