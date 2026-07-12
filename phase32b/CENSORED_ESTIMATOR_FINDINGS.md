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

## 6. The sweep — RUN. It is not two instances. It is **five**, and the gate that should have caught them is structurally blind.

All verified independently, not taken on the sweep's word.

### (i) `I8_brody_q` and (ii) `I9_berry_robnik_rho` — `cross_substrate/axes.py:147,163`
```python
res = minimize_scalar(nll, bounds=(0.0, 1.0), method="bounded", ...)
```
**Brody q = 0 *is* Poisson** (its own docstring, line 141) — **and it is also the search floor.**
Berry-Robnik ρ = 0 likewise. Clustered data wants q < 0 and **rails**. Measured (n=20k, my own run):

| case | CV | `brody_q` | `BR_rho` |
|---|---|---|---|
| **Poisson (the NULL)** | 1.00 | **0.0023** | **0.0335** |
| clustered lognormal | 1.58 | 0.0001 | 0.0025 |
| **EXTREME clustered** | **6.46** | **0.0001** | **0.0015** |
| GOE (repulsive ref) | 0.62 | 0.4893 | 0.7605 |

**A CV = 6.5 burst process reads *more Poisson than actual Poisson*.** Real Poisson's sampling noise
lets `q` wander off the bound; clustered data slams *into* it. The fitter is not merely blind on the
super-Poisson side — **it is anti-informative there.** The rail is *tighter* than the null.

**Berry-Robnik compounds it, and this is the nastiest thing in the sweep:** every bootstrap replicate
rails too, so **the CI collapses**. The clustered case is reported as Poisson **~45× more confidently
than actual Poisson data** (boot_sd 0.0013 vs 0.059). *The rail makes the wrong answer look precise.*

Note the contrast with `ks_poisson`, which returns **nonzero** on clustered data. KS is
**sign-blind** (it flags "not Poisson" without a direction). Brody/BR are **null-collapsing** (they
return the Poisson value *itself*). **These are different failures and the second is far worse** —
and `axes.py:178` lumps them together (*"The KS/W1/Brody axes are sign-blind across the Poisson
pivot"*), which is **why this survived**: it made "add CV as a companion axis" look like a sufficient
mitigation, when the estimator was in fact reporting a **false null**.

### (iii) `bulk_recovery.py:196` — the same bug delivered by interpolation clamping
```python
mass_anchors = np.array([0.0, 0.001, 0.001, 0.005, 0.020, 0.080, 0.260])  # 0.260 = "(Poisson regime)"
sigma_hat = float(np.interp(mass, mass_anchors, sigma_anchors))
```
`np.interp` returns `fp[-1]` above the last knot — and the last knot is the value **the code's own
comment labels "Poisson regime."** Verified: mass = 0.35 / 0.55 / 0.90 → **σ = 0.500 every time**,
the Poisson σ. Every clustered band is clamped onto the Poisson anchor. *(Bonus, unrelated but real:
`mass_anchors` has a **duplicate knot** (0.001 twice) — `np.interp` requires strictly increasing `xp`,
so σ ∈ [0.05, 0.10] is unresolvable.)*

### (iv) **The MANDATORY validation gate was structurally incapable of catching any of this.**
`cross_substrate/validate_fitters.py:56-59`:
```python
CASES = [("poisson", sample_poisson, 0.0, 0.0, 0.15),
         ("goe",     sample_goe,     1.0, 1.0, 0.20)]
```
**These are exactly the two endpoints of `bounds=(0.0, 1.0)`.** A boundary-railing bug is
**invisible to a harness that only probes at the boundaries.** It PASSed. It calls itself
*"MANDATORY before any fitted value is banked"* (§7.ter.57).

> **Probing only at the rails cannot detect railing.**

**REPAIRED (this commit, additive — test harness only, no estimator touched):** added
`clustered` / `clustered_extreme` (super-Poisson lognormal, `q_true < 0` — i.e. **outside the
fitter's reachable range**). The gate now **correctly FAILS 4/4** on them while still passing both
endpoints. *A FAIL here is the gate working.* The §7.ter.57 doctrine is amended: **a validation suite
must include at least one case whose true value lies OUTSIDE the fitter's reachable range.**

### (v) Epistemic knock-on — a "falsification" that was partly circular
`phase36/falsification_calibrator.py:140,164` reads the repulsion axis's *silence* on the clustered
side as a **confirmed prediction** (*"ALL BL: near-Poisson transition INVISIBLE to both (taxonomy
holds)"*). But **BL on the clustered side is manufactured by the clip.** The axis is *constructed*
unable to leave BL there. That confirmation must be **re-run against an unclipped `I_rep`** before it
counts. Flagged, not retracted — [[guard-doctrine arm (c)]]: skepticism is not a free action.

### Checked and genuinely FINE (recorded so the sweep isn't padded)
KS statistics (`max|F_emp − F_theory|`) — non-negative by construction, but clustered data returns
**nonzero**, so no collapse. `sessionK`'s `r̃ = min/max` — bounded [0,1] but **the Poisson null
(0.386) sits in the INTERIOR**: *this is the correct design pattern*, and it is why ⟨r̃⟩ is the
trustworthy discriminant. `I10_cv`, `I11_mass03`, `I12_cv2`, `I13_lv` — nulls (1.0, 0.259, 1.0, 1.0)
all interior. Safe. `clip(p,0,1)` on p-values, `clip(x,-1,1)` before `arcsin`, GLM `eta` clips, KPM
DOS clip — domain/overflow guards, not at a null. Fine.

### The finding-under-the-finding: the knowledge was already here, filed in the wrong slot
`cross_substrate/instrument_confound.py:64-78` **already annotates the rails**:
```python
"I.8_brody_q": (0.0, 1.0),   # Brody q — 0 Poisson rail, 1 GUE rail
```
and even cites *"the same railed-estimator trap as the KPM-floor lesson."* But that insight was
scoped **only to perturbation-sensitivity** (an axis near a rail is indeterminate *under
perturbation*). It was **never applied to the estimator's own primary read** — that a value sitting
*on* the Poisson rail cannot distinguish Poisson from clustering. **Textbook
[[filing_discipline_attribution_slot]]: right value, wrong slot.** The project knew about the rail
and asked the wrong question of it.

## 7. Standing sweep (permanent)

> Sweep every estimator for `np.maximum(0,`, `np.clip(`, `abs()`/`**2` on a signed quantity, bounded
> MLEs (`bounds=(0,·)`), `np.interp` clamping onto a reference knot, and any one-sided fitter. For
> each: compare the implementation's **reachable range** to the **docstring's claimed range**, and
> flag every case where the boundary of the reachable range is a **null/reference value**.
> **Then check whether the fitter's own validation suite probes anywhere except that boundary.**
