"""Conditioned polynomial fit — the repair for a numerics bug found 2026-08-19.

WHAT BROKE.  The P1 continuum PREDICTION fits polynomials with `np.polyfit` on
the raw coordinate, which spans 0..1200 here.  The Vandermonde condition number
of that basis is 4.5e15 at deg 5, 1.2e28 at deg 9 and **2.9e40 at deg 13**,
against roughly 1e16 of usable double precision.  numpy's SVD-based lstsq
degrades gracefully for a while -- raw and centred fits agree to four decimals at
deg 5 and deg 9 -- and then stops: at deg 13, dial 5.0 the raw prediction reads
0.2467 while the conditioned one reads 1.0410, and the MEASURED value is 1.0408.
The "96-sem anomaly" at that cell was the prediction's own arithmetic.

WHAT DID NOT BREAK.  The MEASUREMENT path (`transitions.unfold_poly`) uses the
same raw polyfit and is clean to four decimals at every degree tested, including
13 -- it fits a counting function that is smooth and nearly linear in x, so the
fit is well determined despite the basis.  So the deployed instrument is sound
and every measured value stands; only predicted values needed recomputing.

THE FIX is a basis change, not a model change: centre and scale x before fitting
and evaluate on the same transformed coordinate.  The fitted FUNCTION is
identical in exact arithmetic; only the conditioning differs (37 / 2.0e3 / 1.2e5
at deg 5 / 9 / 13).  `assert_deg5_unchanged` is the guard that this repair does
not move any sealed row -- the sealed instrument is deg 5, so the repair must be
a no-op there, and if it ever is not, that is a change to sealed numbers and must
be handled as one rather than absorbed as a bug fix.
"""
import numpy as np


def polyfit_scaled(x, y, deg):
    """polyfit on a centred+scaled abscissa. Returns (coefs, transform)."""
    x = np.asarray(x, float)
    m, sd = x.mean(), x.std()
    if not np.isfinite(sd) or sd == 0:
        sd = 1.0
    return np.polyfit((x - m) / sd, y, deg), (m, sd)


def polyval_scaled(coefs, tf, xe):
    m, sd = tf
    return np.polyval(coefs, (np.asarray(xe, float) - m) / sd)


def fit_eval(x, y, deg, xe):
    c, tf = polyfit_scaled(x, y, deg)
    return polyval_scaled(c, tf, xe)


def cond_raw_vs_scaled(x, deg):
    x = np.asarray(x, float)
    V = np.vander(x, deg + 1)
    Vs = np.vander((x - x.mean()) / x.std(), deg + 1)
    return float(np.linalg.cond(V)), float(np.linalg.cond(Vs))


def assert_deg5_unchanged(x, y, xe, tol=1e-6):
    """The sealed instrument is deg 5. The repair MUST be a no-op there."""
    raw = np.polyval(np.polyfit(x, y, 5), xe)
    new = fit_eval(x, y, 5, xe)
    d = float(np.max(np.abs(raw - new)))
    if d > tol:
        raise AssertionError(
            f"conditioned fit moves the deg-5 result by {d:.3e} > {tol:.0e}; "
            "that is a change to SEALED numbers, not a bug fix — stop and treat "
            "it as a re-verdict")
    return d
