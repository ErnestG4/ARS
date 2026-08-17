# Per-Realization Reliability — thresholds fixed BEFORE any measurement

**Date:** 2026-08-16. **Why this exists before the policy work runs** (Will's requirement): if the
threshold is set after seeing which harnesses would fail, it drifts toward the answer — the same
drift the 1D kill criterion was sealed against. The two gate types have genuinely different natural
forms, so this is not one number; what is fixed in advance is **the rule for deriving it, stated
per gate type.**

## Gate type A — CLASSIFIER (judges one point set into a class)

*Instances: `longrange_discriminator._judge`; any zoo verdict assigning a class to a realization.*

**Estimand:** per-realization error rate, **both directions**.
- **FP**: rate at which the nearest confusable known class earns the target label.
- **FN**: rate at which the true class fails to earn its own label (or earns a neighbouring cell —
  for the split branch, `HYPER_RIGID` counts as a miss).

**Derivation rule (fixed now, not chosen later).** The gate's own multiplier implies its nominal
error: a ±k·sd band with k = 2.5 admits 2·Φ(−2.5) = **1.24%** under its own Gaussian assumption.
The requirement is that *measured* error not exceed that nominal rate by more than a factor of 4,
rounded to a conventional value:

> **FP ≤ 0.05 and FN ≤ 0.05, each at the 95th percentile of a bootstrap over realizations.**

Both must hold **at every candidate cap**, and a cap is admissible only where both do. Tying the
threshold to the gate's own stated tolerance means it is derived from the instrument's existing
design commitment rather than from what the measurement happens to show.

**Reference point already measured** (n=2000): FP at L=50 is **0.57**, at L=40 **0.60**, at L=20
**0.03**, at L=8 **0.05**. FN is **not yet measured at any L** — that is the missing half.

## Gate type B — FITTER (returns a continuous estimate deployed once per substrate)

*Instances: `I8_brody_q`, `I9_berry_robnik_rho`, and anything `validate_fitters.py` certifies.*

**Estimand:** per-realization scatter against the tolerance the *deployment* actually needs — not
the bias of the ensemble mean.

**Derivation rule (fixed now).** A fitter is deployed to place one substrate relative to reference
classes, so the tolerance it must clear is the **gap to the nearest adjacent expected class value**.
Requiring a single realization to land on the correct side with the same confidence the classifier
gate demands (k = 2.5):

> **sd(estimate across seeds) ≤ gap_to_nearest_class / (2 × 2.5) = gap / 5**,
> evaluated at the deployment n, with the gap taken from the harness's own `CASES` table.

**Both** this and the existing bias check must pass. The bias check is retained, not replaced — it
tests a real property; it is simply not sufficient alone (see §9).

**Note:** `validate_fitters.py` already banks `brody_q_per_seed`, so this quantity is computable
from data the harness records today. The change is a few lines and no new computation.

## What is NOT covered by these rules

Gates that legitimately certify populations (an ensemble-level claim, a distributional comparison)
keep separation-of-means; the rules above apply where the operational decision is made on a single
realization. Deciding which a given harness is remains a judgement call, and the census
(`ESTIMAND_CENSUS.md`) records that judgement per instance rather than assuming it.
