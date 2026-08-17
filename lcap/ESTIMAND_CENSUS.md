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
