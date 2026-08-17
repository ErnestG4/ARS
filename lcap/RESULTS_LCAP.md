# RESULTS — Substrate-Aware L Policy

**Date:** 2026-08-16. **Brief:** `LCAP_BRIEF.md`. **Seal:** `lcap/prereg_sealed.json` (7 files
frozen). Run under the three conditions, with the ordering enforced in code.
**Instrument arc — no new science claims; no banked row re-verdicted.** *(Note: the arc RAN
propose-only. The split and the L policy were subsequently **adopted into
`cross_substrate/longrange_discriminator.py` on the explicit call** — see the adoption section
at the end.)*

## THE OPERATIONAL HEADLINE, stated in the strongest terms the data supports

> **This gate has essentially never distinguished GUE from GOE at deployed configurations.**

Not "the default scale policy needs revision" — that framing invites a scale fix, and **at n=343 no
scale fix exists.** GOE is admitted as `RIGID_GUE` **32–90% of the time at every L tested**, so
there is **no admissible configuration at that n**: the gate can only be repaired there by a
different statistic or more data, not by choosing L better. And n=343 is **where the banked
approximability rows live.**

Across the whole (n, L) grid, **exactly one admissible cell exists** — n=2000, L=5 — against a
deployed default of L=40. So the default was wrong **by 8× at its best point and had no correct
answer at two of the three n tested.** Everything below is the derivation of that sentence.

## TL;DR

**The fix revealed more signal, not less.** Judged inside its own validity window, ζ_first_2000's
excess rigidity is **z = −9.10** — four times more significant than the **z = −2.33** it showed at
the deployed L=50. The large-L policy had been *diluting a 9σ effect down to 2.3σ* and then reading
it through a one-sided rule that had no name for it. Condition 3's alternative explanation
(*"the excess was an artifact of judging past validity"*) is **ruled out**: the effect is 3.6× the
minimum detectable at the capped L, and lens-invariant across deg 3/6/10/15.

**And the zoo gate caught something before ζ was ever touched:** at the deployed L=50, **GOE — a
genuinely different universality class — read `RIGID_GUE`.**

## Condition 1: the policy earned its trust on the zoo alone

The first zoo run **failed**. Across L = 3→50 the GUE band's spread grows ~5.7× while the GUE–GOE
gap grows only ~1.4×, so GOE's exclusion collapses from +7.4σ to **+1.8σ** and it lands inside the
band. That produced a **second cap, independent of the validity argument and derived entirely from
the zoo**: judging at large L destroys class discrimination *even where the GUE form is perfectly
valid*.

    L_judge(substrate) = min( deployed_L , validity_L , discrimination_L )

with `discrimination_L = 40` (largest L holding GOE out by ≥3σ, at that L and every smaller one).
Under the policy the gate passes on all six known-class members:

| member | L_judge | Σ² | z | verdict | expected |
|---|---|---|---|---|---|
| GUE (n=2000) | 40.0 | 0.817 | +0.70 | RIGID_GUE | RIGID_GUE ✓ |
| **GOE** | 40.0 | 1.275 | **+3.95** | **INTERMEDIATE** | NOT RIGID_GUE ✓ |
| Poisson | 40.0 | 36.51 | +253.7 | POISSON_INDEP | POISSON_INDEP ✓ |
| clock | 40.0 | 0.000 | −5.09 | HYPER_RIGID | HYPER_RIGID ✓ |
| jittered clock | 40.0 | 0.141 | −4.09 | HYPER_RIGID | HYPER_RIGID ✓ |
| Wigner-renewal | 40.0 | 6.33 | +39.8 | INTERMEDIATE | INTERMEDIATE ✓ |

Farey is **reported only** (Σ² = 16.19, INTERMEDIATE): its expected Σ² class is not independently
established, and letting an unestablished expectation adjudicate the policy would defeat the point
of the gate.

**Validity map (L0), literature-anchored or derived, never fitted:** ζ → 5.99 (Berry 1988,
saturation at ln(T/2π)); GUE n=2000 → 50, n=1200 → 30, **n=343 → 8.0** (derived: largest L within
10% of the Mehta asymptotic — note the gate's *own reference ensemble* goes out of window at small
n); Poisson and renewal → NOT_APPLICABLE (linear growth, no GUE window to cap); clock and jittered
clock → NO_GUE_WINDOW.

## Condition 2: the sealed direction held; the magnitude expectation did not

**Sealed before the run:** z(ζ) < 0 at L_judge, with z ≥ 0 halting as an inconsistency with the
banked lens-invariant measurement. **Held: z = −9.10.**

The seal also **disclosed in advance** that the *"at reduced significance"* expectation was
likely to be violated — the rigidgate arc had already measured ζ at L = 2…40 (z_d6 = −3.90, −6.07,
−4.40, −4.33, −4.76, −2.89, −2.57), which implies significance *increases* as L falls because the
band's sd shrinks faster than the deficit does. That disclosure was registered rather than
discovered: **significance increased ~4×.** The sign half — the load-bearing pre-commitment — was
untouched by the disclosure and held.

## Condition 3: the power number, computed before ζ

| substrate | L_judge | band | MDD (k=2.5) |
|---|---|---|---|
| ζ_first_2000 | 5.99 | 0.5169 ± 0.0359 | 0.0898 |
| GUE n=343 | 8.00 | 0.5654 ± 0.1094 | 0.2734 |
| GUE n=2000 | 40.0 | 0.7183 ± 0.1411 | 0.3527 |

ζ's measured effect is **0.327 against an MDD of 0.090 — 3.6× resolvable.** So the UNDER_RESOLVED
reading does not apply, and the two explanations condition 3 was built to separate are cleanly
separated: the excess is **not** an artifact of judging past validity (it grows when the artifact
is removed), and it is **not** a power limitation (it is 3.6× the resolution floor).

## Verdict: L_POLICY_FIXED

The cap fixes the physics **and** improves discrimination, at no power cost that matters — the
opposite of the L3 trade-off the brief was prepared to accept.

## The ζ row's own history, banked beside its value

Per the presentational requirement: *a row that has moved three times is trustworthy if the
moves are visible and merely unstable if they aren't.*

| # | date | reading | why it moved |
|---|---|---|---|
| 1 | 2026-06-04 | **"GUE confirmed at class level"** (RIGID_GUE at L=50) | the deployed one-sided rule returned RIGID_GUE and the prose read that as class confirmation |
| 2 | 2026-08-16 | **SUPERSEDED** | `RIGID_GUE` is one-sided and certifies "not floppier than GUE" — a clock earns it too; ζ sits *below* the band (z=−2.33), on the untested side |
| 3 | 2026-08-16 | **HYPER_RIGID, z = −9.10** at L=5.99 | judged inside its own Berry validity window under the zoo-validated policy; effect 3.6× resolvable, lens-invariant (deg 3→15: −8.94, −9.10, −9.10, −9.53) |

**What each move did and did not change:** the *measurement* never moved — ζ's Σ² deficit relative
to finite-N GUE has been present and lens-invariant at every L from 2 to 40 throughout. What moved
is the **scale it was judged at** and the **vocabulary available to name the result**. Move 1→2 was
a labeling correction; move 2→3 is a scale correction that *sharpened the same measurement* from
2.3σ to 9.1σ.

**What this does and does not say about ζ.** It says: ζ_first_2000 is measurably **more rigid than
the finite-N GUE ensemble**, robustly and at high significance, inside the window where the
comparison is meaningful. It does **not** say ζ violates GUE asymptotically — the
Montgomery–Odlyzko picture concerns T → ∞, these are the first 2000 zeros at T ≲ 2.5×10³, and slow
convergence of low-height ζ statistics to RMT is expected and documented. Naming that outcome is
the owning program's call; this arc supplies the number, the window, and the vocabulary.

**Unmoved rows:** Allen V1's "0/100 RIGID_GUE" is a negative result and the policy can only tighten
the rigid branch, so its direction cannot flip; not re-run. ~~brocot/golden unmoved~~ — **CORRECTED
by LC-ADD-1 below: under the n-dependent discrimination cap the brocot rows ARE outside their
window.** The claim here was derived from the validity cap plus the n=2000 discrimination constant,
which was the wrong form.

## Reproduction

`lcap/`: `validity.py` → `policy.py` → `zoo_validate.py` (gate, must pass) → `seal_prereg.py` →
`run_lcap.py` (refuses to touch ζ unless the gate recorded PASS) → `verify_lcap.py`.

---

## LC-ADD-1 (2026-08-16, review) — the discrimination cap is n-DEPENDENT

**Three-event label.** (1) The sealed policy derived `discrimination_L = 40` at n_ref = 2000 and
applied it as a single global constant. (2) review asked whether the small-n
reference-window finding needed its own check against the banked approximability rows, which run
at exactly that n — *"a third cap binding on the configuration those rows used."* (3) Measured: it
does, and **the sealed constant was wrong in form, not merely in value.**

| n | discrimination_L | why it moves |
|---|---|---|
| 343 | **5.0** | the GUE band's spread grows as n falls while the GUE–GOE gap does not |
| 1200 | 8.0 | |
| 2000 | 40.0 | (the sealed value — correct only at this n) |

**Consequence for the banked approximability rows — FLAGGED, NOT RE-VERDICTED, AND THE FLAG NAMES
EXACTLY WHAT IT IMPEACHES.** brocot/golden was judged at **L = 6.86 with n = 343**, where GOE is
separated by only **+2.14σ** against the required 3.0 — outside its own discrimination window. What
that does and does not touch, itemised, because a flag left as a general caution will be read six
months out as impeaching the row wholesale:

| component | status |
|---|---|
| the **measurement** (Σ² = 0.635 at L = 6.86, z = +0.49 vs its GUE band) | **STANDS** — untouched |
| the **`RIGID_GUE` label** read as *"not floppier than GUE"* | **STANDS** — that is what the branch certifies and the row satisfies it |
| the **GUE-vs-GOE discrimination** at that configuration | **UNSUPPORTED** — this and only this |

So the row is not impeached; one specific inference from it is. Re-judging inside the window
requires the substrate point set, which this arc does not hold — hence a flag for the owning
program, not a move. (My earlier report that "the policy does not move this row" was derived from
the validity cap plus the n=2000 discrimination constant; under the corrected n-dependent form it
does.)

**Registration (adopted).** The discrimination cap is **GOE-derived**: GOE is the
nearest neighbour in the zoo we have, not necessarily the nearest in the space. Recording the basis
means a future zoo member sitting closer to GUE at large L tightens the cap as a *refinement of a
stated basis* rather than an arbitrary-looking move.

## Adopted into the deployed module (2026-08-16, the owner's call)

`cross_substrate/longrange_discriminator.py`: the **HYPER_RIGID split** is installed in `_judge`
(same formula, same 2.5 multiplier — the branch is split, not moved), and the **L policy** is
installed as `l_judge()` / `discrimination_L()` / `VALIDITY_L`, documented with its GOE basis.
The policy is deliberately **not wired into the default path**: call sites pass `L` explicitly and
silently re-scaling them would change banked outputs without a re-run anyone asked for. Verified
live on the deployed path: a clock now returns **HYPER_RIGID** (was RIGID_GUE); Poisson still
returns POISSON_INDEP; `l_judge(50, 2000, "zeta_first_2000") = 5.99 [validity]`;
`l_judge(6.86, 343, "gue_n343") = 5.0 [discrimination]`.

## LC-ADD-2 — the census n-column: this is a property of the DEFAULT SCALE POLICY

Ruling: the n-dependence reaches all six single-L call sites, not just the one row that
happened to get checked. The sharp form of the question is whether the exposure belongs to
individual call sites or to `matched_L(n) = clip(0.02n, 5, 50)` itself, which grows **linearly** in
n while the discrimination cap does not.

| n | matched_L | discrimination_L | default policy |
|---|---|---|---|
| 343 | 6.86 | 5.0 | **OUTSIDE** |
| 700 | 14.00 | 8.0 | **OUTSIDE** |
| 1200 | 24.00 | 20.0 | **OUTSIDE** |
| 1600 | 32.00 | 20.0 | **OUTSIDE** |
| 2000 | 40.00 | 30.0 | **OUTSIDE** |

**The default scale policy is outside the discrimination window at every n tested.** So the
exposure is not five unaudited call sites — it is the repo's default L policy, and the call sites
inherit it. Any site using `matched_L` is judging at a scale where the nearest confusable known
class is not reliably excluded.

### Precision caveat — flagged against my own numbers (the ADD-5 lesson, applied)

The per-n cap values above carry **substantial sampling noise** and must not be quoted as precise.
Two independent runs at different seed counts disagree materially:

| n | run A (24 band seeds, 6 GOE draws) | run B (12 seeds, 5 draws) |
|---|---|---|
| 343 | 5.0 | 5.0 |
| 1200 | **8.0** | **20.0** |
| 2000 | **40.0** | **30.0** |

The `largest L separated at that L and all smaller` rule is sensitive to a single noisy band sd, so
individual entries can move by a factor of ~2. **What is robust across both runs is the ordering** —
`matched_L ≥ discrimination_L` at every n tested — **except at n = 2000, where the two runs
straddle the boundary** (run A: 40 ≤ 40, inside; run B: 40 > 30, outside). Treat the per-n numbers
as order-of-magnitude until re-derived at higher seed counts; treat the *conclusion about the
default policy* as supported, with n = 2000 marked undetermined.

**Registered-open:** re-derive the discrimination cap per n at seed counts sufficient to quote it
(the estimator's own variance needs measuring first — the same discipline that caught ADD-5's
1.1σ). Until then the cap ships in `DISCRIMINATION_L_BY_N` as an explicitly provisional table.

## LC-ADD-3 — the structural argument, stated separately because it cannot dissolve

note adopted: the finding has two layers and they should not share a fate.

**Layer 1 — structural, independent of every measured cap value.**
`matched_L(n) = clip(0.02n, 5, 50)` grows **linearly** in n. The discrimination cap is
**flat-to-slowly-growing** in n, because it is set by where the GUE band's spread overtakes the
class gap, and the band's spread shrinks only slowly as n rises. Two curves of those shapes
**diverge with n by construction.** So the *form* of the default scale policy is wrong regardless of
where any individual crossing sits: a policy whose scale grows linearly in n cannot track a cap
that doesn't, and the mismatch necessarily widens over the range the repo actually uses. **This
layer does not depend on any number in LC-ADD-2's table and cannot be dissolved by re-measurement.**

**Layer 2 — the specific crossings, currently NOT load-bearing.** The per-n cap values, and
therefore each individual "OUTSIDE" verdict, rest on an estimator whose own variance was never
measured. Worse, per review: the cap rule is a **max over a monotone condition**, and extrema of noisy
quantities are **systematically biased downward** — one unlucky draw at a small L truncates the
whole run. Downward bias in the cap pushes rows *outside* their window, which is **the same
direction as the finding.** The estimator's known failure mode therefore cannot be distinguished
from the effect it is being used to demonstrate. Until that is ruled out, layer 2 is suspended.

`lcap/cap_rederive.py` is the check: paired realizations across L (so the z-curve is not
independently noisy per point), a bootstrap over draws giving each cap its own sampling
distribution, and **two estimators compared on the same replicates** — the hard-max rule against a
smooth crossing that cannot truncate on one point. Their difference *is* the downward bias,
measured rather than argued, and the "outside" test becomes `matched_L > cap's 95th percentile`
rather than an inequality between two point estimates.

**Why this runs before full-sequence holonomy** (the ruling): this arc has now produced two
numbers that dissolved on inspection — ADD-5's 1.1σ, and possibly LC-ADD-2's caps — and both
dissolved because *an estimator's own variance went unmeasured*. A third would be a pattern rather
than an accident. Full-sequence is seal-ready and will still be seal-ready afterwards.

## LC-ADD-4 — the cap re-derivation: the bias prediction CONFIRMED, LC-ADD-2's table WITHDRAWN

Run before anything else, per the ruling,. Paired realizations across L, 32 draws per class,
400-replicate bootstrap, two estimators on the same replicates.

**The hard-max estimator is downward-biased, as predicted from its structure:** mean
(smooth − hard-max) = **+7.11**, positive at every n (+0.9, +13.2, +7.1). One unlucky draw at a
small L truncates the whole run, and the z-curves are visibly non-monotone (n=1200:
7.32, 4.64, 3.52, **4.56**, 2.25, …), which is exactly the condition the max rule cannot survive.

**LC-ADD-2's conclusion does not survive as measured.** Against the smooth estimator's 95th
percentile, two of three verdicts reverse:

| n | matched_L | hard-max cap (biased) | smooth cap [p05, p95] | outside vs p95? |
|---|---|---|---|---|
| 343 | 6.86 | 3.2 | 4.2 [3.0, 6.4] | **yes** |
| 1200 | 24.00 | 11.7 | 24.9 [18.4, 33.5] | **no** |
| 2000 | 40.00 | 42.7 | 49.9 [50.0, 50.0] | **no** |

**LC-ADD-2's table is withdrawn.** The "outside at every n tested" claim was an artifact of a
downward-biased estimator, pointing in the same direction as the finding — precisely the
confound named in review before the measurement ran. **That is the third number in this arc to dissolve
on inspection** (ADD-5's 1.1σ, RG-ADD-6's re-vindication-by-luck, now this), and all three
dissolved for the same reason: *an estimator's own variance went unmeasured.*

## LC-ADD-5 — a specification error in my cap definition, and the foundational finding re-established

The re-derivation surfaced something worse than bias: **the cap was measuring the wrong quantity.**
I defined separation as `z = (mean_GOE − mean_GUE)/sd_GUE ≥ 3` — a statement about **population
means**. But the gate never classifies a population; it classifies **one point set**, via
`|o − gue_mean| ≤ 2.5·gue_sd`. The operationally correct quantity is the **per-realization
misclassification rate**, which separation-of-means cannot see because it ignores the GOE spread
entirely.

Measured at n=2000, 40 paired realizations, with bootstrap CIs:

| L | GUE band | GOE | z of means | **misclassification rate** |
|---|---|---|---|---|
| 8 | [0.457, 0.676] | 0.894 ± 0.095 | +7.48 | **0.05** [0.00, 0.10] |
| 20 | [0.432, 0.850] | 1.070 ± 0.170 | +5.13 | **0.03** [0.00, 0.12] |
| 40 | [0.414, 1.133] | 1.148 ± 0.261 | +2.61 | **0.60** [0.23, 0.75] |
| 50 | [0.293, 1.235] | 1.232 ± 0.255 | +2.48 | **0.57** [0.30, 0.75] |

**The foundational GOE defect stands, and it is far worse than anything reported so far: at the
deployed L=50 a GOE spectrum earns `RIGID_GUE` roughly 57% of the time — a coin flip.** The
separation-of-means number at L=40 (+2.61) reads "marginal"; the truth at that L is a **60%**
misclassification rate. My wrong definition was *understating* the defect, not inventing it.

**Consequences.** (i) The cap must be defined by misclassification rate, not separation of means —
at n=2000 the rate jumps from 3% at L=20 to 60% at L=40, so the correct cap there is between 20 and
40, well below both the 40 and 50 the biased estimator produced. (ii) `matched_L(2000) = 40` sits
squarely in the bad region, so LC-ADD-2's conclusion is **re-established at n=2000 by a correct
measurement** — but the other n remain **unmeasured under the correct definition** and their
verdicts stand withdrawn until they are. (iii) The structural argument (LC-ADD-3, layer 1) is
untouched throughout: it never depended on a cap value.

**Evidential-status note (the record item).** The two surviving "OUTSIDE" verdicts do **not**
rest on the same footing and the record must not let them read as if they do:

| n | verdict | evidential status |
|---|---|---|
| 2000 | OUTSIDE | **re-established by a correct measurement** — the per-realization misclassification rate (0.60 at L=40, 0.57 at L=50 vs 0.03–0.05 at L≤20) |
| 343 | OUTSIDE | **survives from a WITHDRAWN table** — it was never re-measured under the corrected estimand, and its original derivation used the downward-biased hard-max rule on separation-of-means. It is *not evidence*; it is an un-retracted entry awaiting re-measurement. |

**Registered-open, now the top item — and RESCOPED (see `lcap/ESTIMAND_CENSUS.md`).** The estimand
mismatch is not confined to this gate: censusing found it in `validate_rate_unfold` (a ratio of
ensemble means as one arm of a deployment decision) and in `validate_fitters.py` (the calibrator
zoo's fitter certification passes on the *mean across seeds*, while fitters deploy per substrate).
So the work is a **policy change, not a cap fix**: establish the per-realization form once, apply it
to every harness certifying a per-realization gate, and re-derive this gate's caps under it —
**measuring both directions** (false positive AND false negative) at every candidate cap, since a
cap that fixes discrimination can destroy sensitivity and one rate cannot see that.

## LC-ADD-6 — the policy re-derivation at the correct estimand, both directions

Caps re-derived from per-realization error rates against thresholds fixed in advance
(`RELIABILITY_THRESHOLDS.md`: FP_p95 ≤ 0.05 **and** FN_p95 ≤ 0.05). Reference band built from
**disjoint** GUE draws from the test set — testing draws against a band they helped define would
bias FN optimistically.

**False-positive rates (GOE admitted as RIGID_GUE) — the robust arm:**

| L | n=343 | n=1200 | n=2000 |
|---|---|---|---|
| 3 | 0.39 | 0.00 | 0.00 |
| 5 | 0.57 | 0.07 | 0.04 |
| 8 | 0.54 | 0.04 | 0.04 |
| 20 | 0.86 | 0.32 | 0.18 |
| 40 | 0.86 | 0.54 | 0.32 |
| 50 | 0.82 | 0.54 | 0.50 |

**At n=343 the gate is effectively blind**: GOE is admitted 39–86% of the time at *every* L tested.
At n=2000 the rate climbs from 0.00 at L=3 to 0.50 at L=50. Against `matched_L` of 6.9 / 24 / 40
respectively, the default scale policy sits deep in the bad region at every n — **the conclusion is
re-established on the FP arm, which is the arm that does not depend on my draw count.**

### Power caveat on the FN arm — flagged against my own measurement

With 28 test draws, the bootstrap p95 of a *zero-count* sample is ≈0.11. **So FN_p95 ≤ 0.05 is not
demonstrable at 28 draws regardless of the truth**, and every "INADMISSIBLE on FN" reading in the
run is an artifact of my sampling, not a property of the gate. Reaching the sealed FN threshold
needs roughly **n_draws ≥ 60**. Consequently:

- **FP-based conclusions stand** (rates of 0.3–0.86 are far above any threshold and far above
  sampling noise);
- **FN-based inadmissibility is not interpretable** and the combined "no admissible L anywhere"
  verdict must not be quoted as a finding;
- **registered-open:** re-run the FN arm at ≥60 draws before any cap is quoted as final.

This is the fourth time in this arc that a number needed its own estimator's power checked before
it could be read — recorded here rather than discovered later.

### Corrected caps (FP arm only, provisional pending the FN re-run)

n=2000 → L ≈ 3–5; n=1200 → L ≈ 3–5; **n=343 → none exists at any tested L.** These are an order of
magnitude below the separation-of-means values (30–50) the withdrawn derivation produced, in the
direction the estimand error predicted: the wrong estimand was understating the defect throughout.

## LC-ADD-7 — the two harness repairs

**`validate_rate_unfold` (pole_sep):** `INADEQUATE` now fires on the **per-realization arm alone**;
the ensemble-mean ratio is retained as `pole_sep_diagnostic`, not a gate arm. No banked verdict
changes — both arms fired in the measured case.

**`validate_fitters` — per-realization reliability arm added** (additive; the bias arm is retained
and still reported, matching the harness's existing "second column, not a swap" pattern).
Certification now requires **both** arms. Threshold from the fixed rule: sd across seeds ≤
gap-to-nearest-class / 5, at 12 seeds (3 cannot estimate an sd).

**Two defects found in my own arm by reading its first outputs, both fixed:**
1. *Censoring scored as precision.* `brody_q` is bounded to [0,1], so GUE and the clustered classes
   rail and return a **bit-identical value every seed — sd = 0.0000 — which my arm scored as
   perfect reliability.** A rail guard now reports `UNCERTIFIABLE_RAILED` instead of PASS. An arm
   that cannot distinguish precision from censoring is inert in exactly the direction it exists to
   guard.
2. *The guard then over-fired.* GOE's ρ **is** 1.0 — its true value sits at the bound, so being
   pinned there is correct, not censored. The guard now fires only when the expectation lies **away**
   from the bound the values are pinned to.

Result: `poisson` and `goe` certify on both arms; `clustered`, `clustered_extreme`, and `gue`
report `UNCERTIFIABLE_RAILED` on `brody_q` — which is exactly the set the harness's own commentary
already identifies as out-of-representable-range. The reliability arm independently rediscovers the
rail finding it was not built to look for.

## LC-ADD-8 — FN power caveat RESOLVED at 60 draws; the binding arm is FP

Re-run of LC-ADD-6 at 60 reference + 60 test draws per class, which brings the bootstrap p95 of a
zero-count sample to ≈0.03 and so makes the sealed FN_p95 ≤ 0.05 threshold demonstrable.

**FN is small everywhere** (0.00–0.08, p95 0.00–0.18) — the true-positive side is not what the gate
is failing on. **FP is the binding arm at every n**, and the picture is unchanged from the
under-powered run, which is the point of re-running it:

| L | FP n=343 | FP n=1200 | FP n=2000 |
|---|---|---|---|
| 3 | 0.32 | 0.03 | **0.00** |
| 5 | 0.48 | 0.07 | **0.00** ← only admissible cell |
| 8 | 0.68 | 0.08 | 0.02 |
| 20 | 0.72 | 0.43 | 0.12 |
| 40 | 0.90 | 0.55 | 0.40 |
| 50 | 0.87 | 0.62 | 0.55 |

**Exactly one admissible cell exists in the whole grid: n=2000, L=5** (FP p95 0.03, FN p95 0.03).
At n=1200 nothing is admissible at any tested L (best is L=5 at FP p95 0.13); **at n=343 the gate is
blind** — GOE is admitted 32–90% of the time everywhere.

Against `matched_L` of 40 / 24 / 6.9, the default policy sits **8× or more above** the only
admissible scale. The conclusion is now established on a powered measurement of the correct
estimand in both directions, and the earlier caveat is discharged.

*Estimator note, again:* the hard-max rule returns `None` even at n=2000, because L=3 fails on FN
(p95 0.07) and the rule requires every smaller L to pass — the same truncation behaviour measured
at +7.11 bias earlier. The smooth crossing gives 7.4. **Quote the admissible cell (L=5), not either
cap estimator.**
