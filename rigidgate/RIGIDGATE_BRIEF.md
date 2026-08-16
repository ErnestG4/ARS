# RIGID_GUE Gate Characterization — Micro-Arc Brief

**Status:** ARCHITECTED BY CC under Will's overnight authorization (2026-08-16), item 1 of 3.
Discharges `cross_substrate/PROGRESS_REPORT.md` REGISTERED-OPEN (holonomy seal ADD-5).
**Posture:** instrument-characterization arc. **No new science claims.** No banked verdict is
re-verdicted by this arc; no file under `cross_substrate/` is modified. Any fix is **proposed**
for the owning program to adopt or amend.
**Question (Will's framing, verbatim):** is the margin a property of the discriminator or of the
specific decoy family, and does the boundary have a derivation or was it fitted? Answer either
"the gate is fine, here's why" or "the gate is thin, here's the fix."

## 0. Objects

The gate: `cross_substrate/longrange_discriminator.longrange_verdict`, judging Σ²(L) of a
deg-6-poly-unfolded point set against a GUE reference ensemble and a Poisson reference ensemble.
Deployed rule, verbatim from code: `if o <= gue_mean + 2.5*gue_sd: RIGID_GUE`, where `gue_sd` is
the **ensemble spread** of the reference draws, not a standard error.

Deployment-representative configurations, sealed (matched_L = clip(0.02n, 5, 50)):
**C-brocot** (n=343, L=6.86, the banked approximability rows), **C-add5** (n=1200, L=20, the
configuration ADD-5 was computed at), **C-zeta** (n=2000, L=40, the ζ-family scale).

## 1. Cells

- **R0 Provenance** (documented, no compute). Where the boundary comes from; what is derived and
  what is chosen; the git history of the rule.
- **R1 Band validity.** Are the reference bands where theory says? Measured GUE band vs the Mehta
  asymptotic Σ²_GUE(L) = (ln 2πL + γ + 1)/π²; measured renewal decoy vs the renewal asymptote
  Var(s)·L with Var(s) = 3π/8 − 1 (exact for the GUE Wigner surmise). **Sealed tolerance 20%**;
  a band that is not where theory says would mean the *lens*, not the boundary, is the story.
- **R2 Error rates on the banked decoy family.** P(false RIGID | renewal) and the specificity arm
  P(RIGID | real GUE), by direct sampling at each sealed configuration. This is the honest
  "how thin" number and it **supersedes ADD-5's estimate** (see R0).
- **R3 Adversarial marginal-exact family.** `antithetic_renewal(f)`: a **permutation** of the same
  iid Wigner spacing draw, so the NNS marginal is preserved *exactly* (multiset invariance) while
  serial anticorrelation lowers Σ². Bisect f* where the family crosses the boundary; verify the
  NNS-KS is bit-identical to the renewal decoy of the same seed. Plus the **clock** and
  **jittered-clock** calibrators already banked in the zoo (`calibration_anchors.py` corners),
  which are hyper-rigid by construction.
- **R4 Materiality on banked rows.** Every banked RIGID_GUE row re-evaluated (read-only, not
  re-verdicted) under: the deployed rule, a naive two-sided band, and the proposed rule (R5).
  Registered in advance: **the ζ-family rows read BELOW the GUE band** ("slight excess rigidity
  below the GUE ensemble … a real residual", RESULTS.md), so a naive two-sided fix would flag
  them — a fix that flips a banked claim on a technicality is not a fix.
- **R5 Proposed rule + validation.** Stated before measurement (§2), validated on the full
  battery with **both arms required to move in the right direction** (sensitivity/specificity
  decouple discipline): keep real GUE, keep ζ, keep brocot; reject Poisson, renewal,
  antithetic-f*, clock.

## 2. The proposed rule, pre-registered before its validation runs

**Prediction (stated now, tested in R5):** the hole, if there is one, is that the deployed rule is
**one-sided and unbounded below** — a deliberate 2026-06-04 choice ("make RIGID one-sided: more
rigid than GUE is still GUE-class", commit 78e0ee1), defensible for finite-N fluctuation but not
against processes systematically far below the band. A process can then be *more rigid than GUE*
and earn the GUE pole. The correct discriminator is not a lower band — that would flag ζ on a
technicality — but the **growth law**: GUE class requires Σ²(L) to grow like (1/π²)·ln L, whereas
hyper-rigid spoofs are **flat** in L. Proposed conjunct, to be validated:

    RIGID_GUE  requires  (i)  o(L) <= gue_mean(L) + 2.5*gue_sd(L)      [deployed, unchanged]
                    AND  (ii) SHAPE: Sigma2(L_hi) - Sigma2(L_lo)  >=  SHAPE_FRAC * the GUE
                              ensemble's own mean increment over the same two L

with L_lo/L_hi sealed per configuration and SHAPE_FRAC sealed at 0.35. Arm (ii) is a
**growth** test, so it is invariant to the overall rigidity level and cannot flag ζ for being
rigid — it asks only whether rigidity *accumulates* the way a GUE spectrum's does.

**Non-inertness of arm (ii), proven before running** (TOOLKIT §9): the two hypotheses give
analytically distinct values of the tested quantity — log-growth gives an increment
(ln L_hi − ln L_lo)/π² > 0, a flat process gives 0 — so the arm can move; and it is not invariant
under the transformations that defeated the single-L arm (scaling the whole Σ² curve leaves the
*increment* changed, not fixed).

## 3. Verdict lattice (sealed)

- **GATE_SOUND** — error rates below the sealed target at every sealed configuration AND no
  member of any tested decoy family crosses the boundary.
- **GATE_BOUNDED** — sound against the families it was calibrated on, with a demonstrated hole
  outside them; claim must be scoped and a fix proposed (validated in R5).
- **GATE_DEFECTIVE** — a banked verdict is wrong under the gate's own stated intent.
- **UNDERPOWERED** — sampling insufficient to resolve the error rate at the sealed target;
  extension = one seed-count doubling, declared here, fires once.

Materiality is **margin-denominated** against each banked row's own z. The arc reports; it does
not re-verdict another program's banked rows (that is the owning program's call, per ADD-5).

## 4. Gates before measurement (KAG, the legal debugging window)

Two-sided witness on the classifier itself: the error-rate machinery must return ≈1.0 RIGID-rate
for real GUE (it *can* say yes) and ≈0.0 for Poisson (it *can* say no). The shape arm gets the
same treatment: it must pass real GUE and reject a constructed flat process. A one-sided witness
certifies nothing (TOOLKIT §9).

## 5. Tripwires

1. Nothing under `cross_substrate/` is written; the gate is characterized through its own public
   surfaces so the object measured is the deployed gate.
2. No banked row is re-verdicted; R4 reports what a rule *would* do, labeled as such.
3. The proposed rule is validated on **both** arms (keep-set and reject-set); a fix that improves
   sensitivity by sacrificing specificity is a defect, not a fix.
4. Debugging closes with the seal (D1 clause).
5. ADD-5's own numbers are corrected in the record if measurement contradicts them — an audit
   item that turns out to have been mis-measured is itself a finding, filed as such.
