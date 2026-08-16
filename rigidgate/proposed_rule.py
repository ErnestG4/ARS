"""PROPOSED RIGID_GUE rule — offered to the cross-substrate program for
adoption or amendment.  NOT installed: this arc writes nothing under
cross_substrate/ and re-verdicts no banked row.

── What the deployed rule does ──────────────────────────────────────────────
    if o <= gue_mean + 2.5 * gue_sd:  RIGID_GUE
One-sided by deliberate choice (commit 78e0ee1, 2026-06-04: "make RIGID
one-sided (more rigid than GUE is still GUE-class)").  Right for finite-N
fluctuation — a real GUE sample lands below the band mean half the time —
but unbounded below, so ANY process at or beneath the GUE rigidity level
earns the GUE pole, including processes that are not GUE at all.

── The fix: split the cell, do not move the boundary ────────────────────────
    o >  mean + 2.5*sd   ->  (unchanged downstream cells)
    |o - mean| <= 2.5*sd ->  RIGID_GUE      (consistent with GUE rigidity)
    o <  mean - 2.5*sd   ->  HYPER_RIGID    (MORE rigid than finite-N GUE)

HYPER_RIGID is a measurement outcome, not a class call: it says the observed
rigidity exceeds what the GUE reference ensemble produces at this (n, L,
lens), and hands adjudication back to the analyst.  Same boundary formula,
same 2.5 multiplier, no new tuned constant, no statistic added.

── Two design alternatives measured and REJECTED in the pre-seal window ─────
(recorded so the choice is auditable, per pilot-informed-seal discipline)

1. A Sigma^2 GROWTH arm (require the observed Sigma^2 increment across two L
   to reach a fraction of the GUE ensemble's increment).  FAILED its own
   two-sided KAG witness: at a 2x lever the GUE log-increment (~0.07) is
   buried in single-realization noise (~0.13), so the arm passed real GUE
   only 42% of the time and passed a constructed flat process 75% of the
   time.  Underpowered by construction, not by implementation.

2. A Delta_3 growth arm.  Well powered (GUE increment 0.1053 +/- 0.0086,
   ~12:1) and it does reject every spoof — but it ALSO rejects the banked
   zeta row at z = -9.5, because zeta_first_2000's number variance is nearly
   flat in L (0.30 -> 0.39 across L = 2 -> 40 against GUE's 0.40 -> 0.74).
   That flatness is measured to be REAL, not an artifact: the deg-6 lens
   absorbs 0.0% at n=2000 (0.6810 vs 0.6811 on GUE), and the deviation is
   lens-invariant across deg 3/6/10/15.  At height T ~ 2.5e3 the Berry
   saturation scale ln(T/2pi) = 5.99, so GUE-like growth is not expected
   above L ~ 6 anyway.  A growth arm therefore cannot separate "genuinely
   more rigid than finite-N GUE" (zeta at low height) from "not GUE at all"
   (a clock) — at the level of Sigma^2(L) those two ARE the same measurement
   outcome, which is precisely why the honest repair is to give that outcome
   its own name rather than to tune a statistic until it sorts them.
"""

import numpy as np


def rigid_cell(sigma2_obs, gue_band, mult=2.5):
    """Proposed replacement for the deployed RIGID branch.

    gue_band: dict with 'mean' and 'sd' (the gate's own reference ensemble).
    Returns (verdict_or_None, z).  None means "not in the RIGID branch" —
    the caller's existing Poisson-side cells decide, unchanged.
    """
    gm, gs = float(gue_band["mean"]), float(gue_band["sd"])
    z = (float(sigma2_obs) - gm) / gs if gs > 0 else np.inf
    if z > mult:
        return None, z                      # deployed cells take over
    return ("RIGID_GUE" if z >= -mult else "HYPER_RIGID"), z


def deployed_cell(sigma2_obs, gue_band, mult=2.5):
    """The deployed rule, replicated exactly for side-by-side reporting."""
    gm, gs = float(gue_band["mean"]), float(gue_band["sd"])
    return ("RIGID_GUE" if sigma2_obs <= gm + mult * gs else None,
            (float(sigma2_obs) - gm) / gs if gs > 0 else np.inf)


def delta3_growth_diagnostic(d3_lo, d3_hi, gue_inc_mean, gue_inc_sd):
    """REPORTED, NOT GATED (rejected alternative 2 above): z of the observed
    Delta_3 increment against the GUE ensemble's own increment.  Useful as a
    characterisation of HOW a substrate is rigid; must not be used as a
    verdict arm without a scale-validity scope, since real substrates
    saturate (Berry) inside the deployed L range."""
    inc = float(d3_hi) - float(d3_lo)
    return dict(obs_increment=inc, gue_increment=float(gue_inc_mean),
                z=(inc - gue_inc_mean) / gue_inc_sd if gue_inc_sd > 0 else None)
