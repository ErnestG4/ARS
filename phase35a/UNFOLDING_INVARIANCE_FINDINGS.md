# Phase 35a scoping — unfolding-invariance campaign FINDINGS (2026-05-16)

**Status:** SCOPING (not 35a execution). Resolves rev-3's structure per Will's
pre-registered decisive criterion (unfolding-invariance, not marginal shape).
Data: `phase35a/unfolding_invariance_results.json`, log
`phase35a/unfolding_invariance_log.txt`. Script
`phase35a/unfolding_invariance_campaign.py`. Run: 27m35s, clean (the
`fix_gue_generator` import side-effect from the prior run was fixed by
inlining the unfoldings).

## Headline — the Stage-0 gate FAILED the instrument on known truth (§7.ter.55/57)

λ=0 free Laplacian, exact truth P(s)=δ(s−1) (clock, zero variance):

| N | unfold | var(s) | nearest | quad |
|---|---|---|---|---|
| 377/2584/6765 | **arcsine (truth)** | **0.0000** | clock/wigner | **BR_artifact** |
| 377/2584/6765 | deg-11 (suspect) | 0.009–0.010 | wigner | BR_artifact |
| 377/2584/6765 | deg-3 (neutral) | 0.069–0.073 | wigner | TR/BL |

Three instrument failures, all on a substrate whose answer is *exactly known*:

1. **The zoo classifier does NOT bin the exact clock into TR — it puts it in
   `BR_artifact`.** This *falsifies* the Q2 reconciliation hoped for last turn
   ("subcritical reads TR is consistent with is-clock because TR bins clock").
   TR does not bin clock; clock → BR_artifact. The subcritical-reads-TR finding
   is therefore *not* explained by clock-in-TR.
2. **My KS-vs-clock statistic is broken.** It reports KS≈0.53 (floor ratio
   11–49) against the *exact* clock (var(s)=0.0000, literally a point mass).
   This is a delta-vs-step KS artifact (the empirical CDF of identical points
   crosses the step at s=1, giving KS≈0.5 by construction). Every "nearest"
   label and clock-floor-ratio in this campaign is therefore **unreliable
   wherever clock is the true answer**. `var(s)` is the only trustworthy
   clock indicator here, and it *is* recorded faithfully.
3. **deg-11 does NOT reproduce clock on the smooth arcsine IDS** (var 0.009 vs
   truth 0; deg-3 far worse, 0.07). This is exactly Will's pre-stated trigger:
   *"if deg-11 distorts even the easy case, it is implicated for every λ≠0
   cell and pre-confirms Reading-2."* It distorts the easy case. Reading-2 is
   pre-confirmed.

Per Will's instruction the gate **gates the whole campaign**: no clock /
Wigner / Poisson *label* from Stage 1 is trustworthy as stated. What survives
is instrument-independent: `var(s)` and the *divergence between unfoldings*.

## What IS robust (instrument-failure-proof) — and the decisive call it forces

The pre-registered decisive criterion (Will): unfolding-**invariant** ⇒ genuine
localization-Poisson ⇒ class I descopes; unfolding-**dependent** ⇒ silent
mis-fit ⇒ class I stays.

Observed across essentially every supercritical and near-critical cell:

- **Polynomial legs (deg-11, deg-3):** `var(s)` *explodes* and grows
  monotonically with N — supercritical deg-11 var 2.7 → 237 (N 377→6765);
  deg-3 up to ~674. Classifier → **BL/Poisson**. This is precisely the
  Reading-2 artifact: a smooth polynomial cannot follow the devil-staircase
  IDS, so Cantor gap mass is left as residual large-spacing → variance blows
  up → low rep_int → BL.
- **IDS leg (follows the staircase):** `var(s)` ≈ 0.17–0.39 (supercritical),
  ≈ 0.002–0.03 (subcritical) — three orders of magnitude smaller, *not*
  growing pathologically. Classifier → `BR_artifact` everywhere (the *same*
  bucket the exact clock falls into in Stage 0).
- The two pictures **disagree by 10²–10³× in var(s) and on every quadrant /
  nearest-class assignment.** The verdict is **strongly unfolding-DEPENDENT**,
  not invariant.

**Therefore, by Will's pre-registered criterion (not an adjudication — the
criterion was fixed in advance):**

- The supercritical **"BL/Poisson ⇒ class I descopes" reading from the prior
  run is an unfolding artifact. The descope is dead.** A deg-11 pipeline
  launders Cantor spectra into "Poisson" with no flag — exactly the
  asymmetric silent-corruption the gate was built to prevent (Will:
  "a wrong descope silently corrupts every 35b classification with no flag").
  The gate prevented it. The loop worked as designed.
- **Class I STAYS on rev-3.** This is the heavier branch Will named.

## Q2 / Class-II — premise not refuted, but now blocked at the instrument level

- The "reads-TR ⇒ is-clock" reconciliation is **falsified by the gate** (clock
  → BR_artifact, not TR).
- *However*, under the IDS unfolding subcritical λ=0.10 gives var(s) ≈ 0.004
  (near-clock-rigid) and lands in BR_artifact — the *same signature the exact
  clock produces under the truth unfolding in Stage 0*. So the clock-rigid
  Class-II premise is **consistent with the IDS-leg low-variance result**;
  it simply **cannot be confirmed by an instrument that cannot recognize the
  exact clock**. Class-II characterization is **blocked until the instrument
  is fixed and re-gated**, not refuted.
- The λ-ordering Will flagged (0.10 lowest-var/most-rigid → 0.30/0.50 →
  0.80/0.95) is visible in the IDS-leg var(s) trend and is still consistent
  with "clock-rigid Class II with a (λ,N) HALT boundary." Reading the HALT off
  the grid is **deferred** until the re-gated instrument exists.

## Campaign gap (flagged, honest)

The IDS-ref unfolding leg has **no known-truth gate** — Stage 0 deliberately
ran arcsine/deg-11/deg-3 only (λ=0 has no gaps for an IDS-ref). So the IDS
leg's low-variance result is *suggestive but itself un-validated*. The robust
conclusion (unfolding-DEPENDENCE ⇒ class I stays) does **not** rely on
trusting either leg individually — only on their unambiguous disagreement —
so it stands. But any *positive* Class-II characterization needs the IDS leg
gated on known truth too (e.g. a high-N free-Laplacian reference for λ=0, and
a known Poisson case).

## Net for rev-3 (for Will's adjudication — NOT auto-adjudicated)

1. **Class I is NOT descoped — it stays.** Verdict was unfolding-dependent;
   the descope rested on the deg-11 artifact the gate exposed. rev-3 is the
   heavier branch (P3 + P1/P2-root + class I retained).
2. **The scoping instrument failed its Stage-0 gate** (clock-KS metric broken;
   classifier puts exact clock in BR_artifact). Before any further (λ,N)
   characterization or reading P3's HALT off the grid, the instrument must be
   fixed and re-gated on known truth (clock; Poisson; and an IDS-leg
   known-truth gate). Characterizing Class II with the current pipeline is
   not yet possible.
3. **Q2:** Class-II premise is not refuted (IDS-leg low var is consistent with
   clock-rigid); it is blocked pending the instrument fix.

The descope is the load-bearing, hard-to-reverse claim Will flagged; the gate
he designed prevented a wrong one. Recorded in full (incl. the JSON horizon
record) regardless of immediate interest, per the survey-the-horizon ethic.

---

## Re-gated instrument + certified grid (2026-05-16, Will's 3 specs + Gate-C adjudication)

`phase35a/regated_instrument.py` ; data `regated_instrument_results.json` ;
log `regated_instrument_log.txt`. Run 2m38s, clean.

**Instrument now CERTIFIED on known truth (the prior campaign's Stage-0 failure repaired):**
- SPEC-1: KS-to-δ + Kuiper dropped (degenerate vs a point mass). var(s) primary,
  W1δ=E|s−1| companion. Gate A: exact clock → var=0, W1δ=0 (non-degenerate now).
- SPEC-2: clock is a first-class derived label (τ_clock from Gate A), not
  BR_artifact-noise. Gate B (synthetic Poisson) PASS: var≈1.02, W1δ≈0.74,
  KS-Poisson on floor, BL, not clock_rigid.
- SPEC-3: IDS leg gated on rational-θ known truth. `ok_absorb` PASS
  (θ=8/13,13/21 → IDS-unfold var≈0.0008, gaps absorbed = the
  campaign-critical property). Corrected `ok_plateau` PASS (large-spacing
  IDS values all on (1/q)ℤ, maxdev ~1e-4 ≪ tol ~3.5e-3). NOTE: the
  `n_open_gaps` count (17 for q=13, 21 for q=21) is "large-spacing events,
  all lattice-consistent" — includes van-Hove band-edge thinning, which
  also sits at k/q; it does not impugn certification (the substantive
  property — every large spacing's IDS ∈ (1/q)ℤ — holds strongly).

**Certified grid (the decisive picture, now interpretable):**
- **Polynomial legs (deg11, deg3):** var(s) explodes and grows
  MONOTONICALLY with N (deg11 2.6→252; deg3 17→718) — the mechanistic
  Reading-2 signature (more N → more resolved Cantor gaps → more gap-mass
  the polynomial cannot track). Labels: poisson (supercritical, λ=0.95),
  wigner (λ=0.10,0.50). Quad BL/TR.
- **Certified IDS leg:** var(s) SMALL and bounded (0.002–0.16); label
  **wigner across the WHOLE 35b grid** — supercritical λ→1⁺ AND subcritical
  small-λ. NOT Poisson anywhere; NOT clock_rigid anywhere; classifier
  → BR_artifact (the missing-calibrator gap, SPEC-2 restated).
- **Unfolding-invariance:** supercritical (1.05/1.25/2.0) and λ=0.95/0.50
  → **NO** (deg-poly poisson/wigner vs certified-ids wigner; the
  var-exploding polynomial artifact). λ=0.10 → **YES** (all three wigner).
- **Certified Class-II-relevant separation:** at N=2584, ids W1δ ≈ 0.04
  for subcritical small-λ (0.10,0.50) and 0.95, vs ≈ 0.26 for supercritical
  — small-λ is markedly closer to clock. ids W1δ GROWS with N at fixed λ
  (λ=0.10: 0.013→0.039→0.113) — the resolution crossover; P3's HALT is now
  readable off this certified trend.

**Robust conclusions (instrument-certified):**
1. **Descope is dead — reconfirmed on a certified instrument.** Supercritical
   strongly unfolding-DEPENDENT; the polynomial Poisson/BL was the
   var-exploding Reading-2 artifact; the certified leg says wigner-class.
2. The certified leg shows AM NNS across 35b's grid is **low-variance,
   repulsive, NOT Poisson, NOT clock, nearest-Wigner, and BR_artifact in
   the zoo** (no proper class). This moves class I from "precautionary
   guard" toward "the certified instrument shows an unrecognized object
   that needs a dedicated calibrator."
3. **But "nearest-Wigner under the certified leg" ≠ "is GUE."** There is no
   known-truth for the irrational-θ AM NNS (that is precisely the §3
   derivation question). A Cantor-NNS could be low-variance/repulsive and
   read nearest-Wigner among three coarse references without being Wigner.
   Scoping cannot settle whether the needed calibrator is class I (Cantor)
   or an extended Class II — that is the rev-3 / §3 content, Will's call.

**For Will's adjudication (NOT auto-adjudicated):**
- (Q-i) Does "certified leg → nearest-Wigner, low bounded var, BR_artifact"
  mean the zoo *recognizes* AM (→ class I retained precautionary only) or
  *still mis-fits* it (BR_artifact → unrecognized object → dedicated
  calibrator needed)?
- (Q-ii) Is the Class-II calibrator "exact-clock + perturbation" or
  "low-variance wigner-class drifting off clock with N" (what the certified
  instrument actually measures)?
- (Q-iii) Extract P3's HALT off the certified ids-W1δ-vs-(λ,N) trend next?
