# The censored estimator — `I_rep` floors at its own null

**Escalated out of the 32b Leg-2 audit; it is not a 32b finding.** The clip is independent of Leg 2
(both modes), independent of the cap, and it is **the only one of the three defects at that call site
that survives the §8 backfill as currently specced.** Doctrine: new TOOLKIT §9 arm **(e)**.

## 0. The defect

`arithmetic_toolkit.py:507`
```python
I_rep = float(np.trapezoid(np.maximum(0, 1 - R2[mask]), r[mask]))
```
Docstring, line 492-494: *"I_rep = ∫₀¹ (1 − R₂(r)) dr … positive → repulsion, zero → Poisson,
**negative → clustering**."* The `np.maximum(0, ·)` makes the negative branch **unreachable**. Same
class as `phase24/loader.py:49`: a docstring advertising a capability the code does not have.

**The floor sits exactly at the null.** R₂ ≡ 1 (Poisson) ⟹ integrand ≡ 0 ⟹ `I_rep` = 0. Everything
*below* Poisson — i.e. **all clustering** — is mapped **onto** the Poisson value.

And clustering is not an exotic corner. **Neural spike trains burst.** SOC processes cluster. On this
axis, the expected state of half the substrates in the program is indistinguishable from noise.

## 1. Confirmed at the classifier, not just inferred from the form

`arithmetic_toolkit.py:789` — the quadrant classifier's **primary axis is `rep_int_q`**:
```python
if rep < rep_int_low:        # rep_int_low = 0.10
    quadrants.append('BL')
```
and its own docstring (line 734):

> `BL   low rep_int (< rep_int_low) AND no RF spike   → **Poisson noise**`

⇒ **`BL` is a collapse class, and it is named after one of the two things it collapses.** Poisson and
clustering both land there, and the label says Poisson.

## 2. The demonstrated misclassification — known ground truth, exactly at the floor

RESULTS.md §cross-signal joint-plane table:

| signal | n | `rep_int_q` | KS_GUE_q | primary |
|---|---|---|---|---|
| **Fungal pool (Adamatzky)** | 1,470 | **0.000** | 0.641 | **BL** |
| **Solar X-ray flares M+** | 2,000 | **0.000** | 0.604 | **BL** |
| Binance BTCUSDT day 1 | 2,000 | 0.018 | 0.150 | BL |

**Exactly 0.000. That is the floor, not a measurement.**

And solar flares are the case where **we already know the answer from our own work**: the SOC pair
phase found GOES flares **clustered** (ARS recovers clustering; GK-declustering → Poisson), and
recorded that *"one-sided fitters are blind to super-Poisson."* The joint-plane classifier read that
same known-clustered substrate as **"BL = Poisson noise," at exactly 0.000.**

This is no longer an inference from the estimator's form. **It is a demonstrated misclassification
against a ground truth we ourselves established, and the two facts sat in the repo un-collided.**
Adamatzky fungal spiking is likewise bursty. Both are censored readings wearing a Poisson label.

⇒ **The threat surface is the `BL` class across the entire cross-signal programme**, not 32b.
Every `BL` verdict in RESULTS.md must be re-read as **"Poisson OR clustered — undetermined."**

## 3. The two hypotheses put to it — one FALSIFIED, one confirmed-and-worse

### (a) "The substrate-relativity ladder's bottom rung may be the floor" — **NO. It is a measurement.** ✅

The ladder's rungs are **ρ(ks_gue, burst)** (~0.8 hc-3 → ~0 Allen), **not** `I_rep`. And on the
banked windowed axes (n=431 cells × 5 windows):

- `ks_gue_med`: **0.0% of (cell, window) values are exactly 0.** No point mass. Not censored.

`ks_gue` is a KS statistic — bounded [0,1] **by construction**, and its boundary is **not** a null
value. The clip does not touch it. **The bottom of the ladder is a real near-zero correlation of an
uncensored axis. The rung is a rung.** The priority question is answered, and answered negative.

### (b) "ρ(rep_med) = 0.921 is inflated by the point mass" — **FALSIFIED by the decisive test.** ❌

Re-estimated ρ on the banked split-half windows, full cohort vs the **uncensored subset**
(`rep_med > 0` in all 5 windows), same estimator both times:

| | n | mean pairwise r | ρ (Spearman-Brown, k=5) |
|---|---|---|---|
| full cohort | 431 | 0.622 | **0.892** |
| **uncensored (>0 in all 5 w)** | 158 (37%) | 0.666 | **0.909** |

**ρ does not collapse — it RISES (+0.017).** The point mass is not doing the work. Banked
**0.921 stands**; so does `ks_gue_med`'s 0.978 (zero point mass).

*Why it didn't bite:* only **21.6%** of cells are zero in *all* five windows (the perfectly-agreeing
set); the positive half carries **genuine** reliability (ρ=0.909) with real spread. The cells that
are zero in *some* windows but not others (41.7%) are **noisy**, and they *depress* ρ. The floor was
deflating this estimate, not inflating it.

**The proposed dual of arm (b) — "censoring is the signature of spurious reliability" — is a real
mechanism but it DID NOT FIRE HERE, and it must be banked with its precondition, not as doctrine:**
a floor inflates ρ only when the point mass is large **and the positive half is noisy**. Measure both
before invoking it. Tested, not confirmed. (Recorded so it is not later remembered as established.)

### Net: the reliability leg of arm (b) SURVIVES for `rep_med`.

§7.ter.50's ORTHOGONAL on `rep_med` is threatened **once, not twice**. The admission was legitimate;
the *predictor* is the problem. A censored variable can be measured perfectly reliably — **reliably
measuring a floor is still measuring a floor.** That is itself the sharper lesson: reliability and
validity came apart cleanly here, and the ledger's gate cannot see the difference.

## 4. Consequence for the §8 backfill — it was insufficient, twice over

1. **Unclip.** Bank the signed `∫₀¹(1 − R₂) dr` (drop `np.maximum(0, ·)`).
2. **Calibrate the negative half BEFORE any substrate.** Unclipping removes the floor but leaves the
   axis **uncalibrated on a half-line that has never been observed**. Run the calibrator zoo through
   the unclipped estimator first:
   - **positive anchor: Farey** — hard gap at `s_min = 3/π²`, short-range repulsion stronger than any
     RMT class; it must sit far above the floor and pin the scale.
   - **negative anchor: a known-clustered calibrator** (Cox / Neyman–Scott / bursty gamma). Without
     it the unclipped values on the neural rows are **numbers without a sign convention**.
3. **The compound, flagged as inference from the code — testable, not established.** The integration
   domain `r ∈ [0,1]` is in units of a mean spacing that **Mode 1 derives from the data being
   classified** (`sp / sp.mean()`). So the null this estimator censors against is **itself a
   data-dependent null**. *Circular null × censoring at the null* is worse than either alone, and
   fixing one leaves the other. The backfill must fix **both** or it measures nothing.

## 5. E2 / RDD — closed, do not spend effort here

The hard gap at the cap is a sharp threshold on a running variable, so an **RDD at the boundary is
the one design that identifies in principle** — my "no adjustment can separate stride from n" was
right about *adjustment* and overstated as a general claim. But it is worthless here for two
independent reasons: it estimates a **LATE at the cutoff**, i.e. exactly where stride ≈ 2 and the
treatment is weakest; and **the outcome is censored**, so it returns the same flat null.

**The censoring, not the positivity violation, is the binding constraint.** Ordering: fix the
estimator → then the backfill → the RDD is at best a free bonus check afterward, never the primary
design.

## 6. Standing sweep (this is a class, not a finding — two instances)

`I_rep` and the SOC one-sided fitters. Both found by self-audit, both in ARS's own estimators.

> Sweep every estimator for `np.maximum(0,`, `np.clip(`, `abs()`/`**2` on a signed quantity, and any
> one-sided or bounded fitter. For each: compare the implementation's **reachable range** to the
> **docstring's claimed range**, and flag every case where the boundary of the reachable range is a
> **null/reference value**.
