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
