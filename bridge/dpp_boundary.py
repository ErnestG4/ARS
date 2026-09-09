#!/usr/bin/env python3
"""Boundary reporting for the bridge fitters, as a SUCCESSOR rather than an edit.

WHY THIS IS A NEW FILE AND NOT A PATCH
---------------------------------------
`proposals/PROPOSED_boundary_reporting.md` asked for `at_lower_boundary` /
`at_upper_boundary` keys inside `dpp_python.py`. That file is under blob-SHA
freeze (`verify_bridge.py` checks it against the seal's addendum), and the freeze
exists so the banked bridge numbers stay reproducible FROM FROZEN CODE. Editing
it and re-deriving the addendum hash would preserve the numbers while destroying
the property the freeze was protecting -- the frozen artifact would no longer be
the thing that produced them.

So nothing here touches `dpp_python.py`. This module supplies the boundary
reporting the proposal wanted, future fits import it, and
`dpp_boundary_audit.py` applies it retrospectively to the fits already banked --
which is where the missing machine record actually needs to appear.

THE BOUNDS ARE DECLARED HERE AND CHECKED AGAINST THE FROZEN SOURCE. A successor
module that hard-codes bounds is one edit away from disagreeing silently with the
fitter it describes, so `assert_bounds_match_frozen()` greps the frozen file for
the literals below and raises if they are gone. If the freeze is ever lifted and
a bound changes, this notices instead of reporting the old one.

IT USES `railed.Bounded`, WHICH HAD NO CALL SITES. That module was written to
make a railed value refuse silent float use, and until now nothing imported it --
a codified rule with no call site, which `guard_usage_census` measured and this
repo's oldest meta-finding predicts. The bridge's Thomas fits are railed and were
reported as ordinary floats; that is precisely the case `Bounded` exists for.
"""
import os
import re

import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from railed import Bounded                                          # noqa: E402

FROZEN = os.path.join(HERE, "dpp_python.py")

# Bounds as they appear in the frozen fitters.
DPP_ALPHA_LO = 1e-3          # fit_dpp: minimize_scalar(..., bounds=(1e-3, amax))
THOMAS_KAPPA_LO = 1e-4       # fit_thomas: bounds=(1e-4, 100.0)
THOMAS_KAPPA_HI = 100.0
THOMAS_SIGMA_GRID = (0.05, 10.0)   # np.geomspace(0.05, 10.0, 60)

# Relative tolerance for "at the bound". The frozen fitters use
# scipy's bounded Brent, which stops a hair short of a bound it is pressed
# against, so an ABSOLUTE tolerance that works at kappa~100 is meaningless at
# alpha~0.35. Everything below scales the tolerance by the bound's magnitude.
REL_TOL = 1e-4


def assert_bounds_match_frozen():
    """The constants above must EQUAL the numbers in the frozen fitter.

    An earlier version only checked that the source still CONTAINED certain
    literals, which a red-path exposed as insufficient: editing a constant here
    to disagree with the source left the check passing, because the source was
    untouched. A successor that silently describes a different bound than the
    fitter it audits is worse than no successor. So the numbers are PARSED out
    and compared."""
    src = open(FROZEN).read()
    found, problems = {}, []

    def grab(pat, what):
        m = re.search(pat, src)
        if not m:
            problems.append(f"{what}: not found in the frozen source at all")
            return None
        return tuple(float(g) for g in m.groups())

    dpp = grab(r"bounds=\(([0-9.e-]+),\s*amax\)", "fit_dpp lower bound")
    tho = grab(r"bounds=\(([0-9.e-]+),\s*([0-9.e+]+)\)\s*,?\s*method=\"bounded\"\)"
               , "fit_thomas bounds")
    if tho is None:
        tho = grab(r"minimize_scalar\(D_of,\s*bounds=\(([0-9.e-]+),\s*([0-9.e+]+)\)",
                   "fit_thomas bounds")
    sig = grab(r"geomspace\(([0-9.e-]+),\s*([0-9.e+]+),\s*\d+\)",
               "fit_thomas sigma grid")

    for got, want, what in ((dpp and dpp[0], DPP_ALPHA_LO, "DPP_ALPHA_LO"),
                            (tho and tho[0], THOMAS_KAPPA_LO, "THOMAS_KAPPA_LO"),
                            (tho and tho[1], THOMAS_KAPPA_HI, "THOMAS_KAPPA_HI"),
                            (sig and sig[0], THOMAS_SIGMA_GRID[0], "SIGMA grid lo"),
                            (sig and sig[1], THOMAS_SIGMA_GRID[1], "SIGMA grid hi")):
        if got is None:
            continue
        if got != want:
            problems.append(f"{what}: this module declares {want}, the frozen "
                            f"source uses {got}")
    if problems:
        raise AssertionError(
            "dpp_boundary.py has drifted from the frozen dpp_python.py it "
            f"describes: {problems}. Every reading it produces is about a "
            "different fitter until this is reconciled.")
    found.update(dpp_alpha_lo=dpp and dpp[0], thomas=tho, sigma=sig)
    return found


def _tol_for(bound):
    return max(abs(bound) * REL_TOL, 1e-12)


def dpp_alpha(alpha, alpha_max):
    """Both ends of fit_dpp's alpha, as Bounded readings.

    The UPPER bound is a genuine DPP existence condition -- alpha_max is the
    largest alpha for which the family is a valid DPP -- so a rail there is a
    real statement: the data wants more repulsion than the family can express.
    The LOWER bound is a numerical guard, and a rail there would mean 'no
    repulsion', which is a Poisson-like reading wearing a small positive alpha.
    """
    return dict(
        upper=Bounded(alpha, boundary=alpha_max, tol=_tol_for(alpha_max),
                      name="alpha (upper: DPP existence bound)"),
        lower=Bounded(alpha, boundary=DPP_ALPHA_LO, tol=_tol_for(DPP_ALPHA_LO),
                      name="alpha (lower: numerical guard)"))


def thomas_kappa(kappa):
    """Both ends of fit_thomas's kappa. Neither is checked by the frozen fitter.

    kappa -> infinity IS the Poisson limit for a Thomas process (the clustering
    term carries 1/kappa), so a rail at the upper bound is the fit saying 'no
    clustering'. That reading is CORRECT and is already stated in prose in
    RESULTS_BRIDGE.md; what it has never had is a machine record.
    """
    return dict(
        upper=Bounded(kappa, boundary=THOMAS_KAPPA_HI,
                      tol=_tol_for(THOMAS_KAPPA_HI),
                      name="kappa (upper: Poisson limit)"),
        lower=Bounded(kappa, boundary=THOMAS_KAPPA_LO,
                      tol=_tol_for(THOMAS_KAPPA_LO),
                      name="kappa (lower: numerical guard)"))


def thomas_sigma(sigma):
    """sigma is not optimised -- it is scanned over a fixed geomspace grid, so
    its 'bounds' are the grid ENDPOINTS. Landing on one means the best sigma was
    at or beyond the edge of the scan, which the frozen fitter cannot report and
    which is a different statement from a bounded optimiser railing."""
    lo, hi = THOMAS_SIGMA_GRID
    return dict(
        upper=Bounded(sigma, boundary=hi, tol=_tol_for(hi),
                      name="sigma (upper grid endpoint)"),
        lower=Bounded(sigma, boundary=lo, tol=_tol_for(lo),
                      name="sigma (lower grid endpoint)"))


def report(fit):
    """Boundary reading for one banked fit record, whatever family it is."""
    fam = fit.get("family")
    out = {"family": fam}
    if "alpha" not in fit and "kappa" not in fit:
        # Poisson has no free parameter, so it cannot rail. That is not the same
        # statement as "it did not rail", and collapsing the two is how a
        # parameterless row would come to look like a clean bill of health.
        out["any_rail"] = None
        out["no_free_parameter"] = True
        out["frozen_fitter_reported"] = fit.get("at_boundary")
        return out
    if fam == "thomas":
        k = thomas_kappa(fit["kappa"])
        s = thomas_sigma(fit["sigma"])
        out["kappa_railed_upper"] = k["upper"].railed
        out["kappa_railed_lower"] = k["lower"].railed
        out["sigma_at_grid_edge"] = s["upper"].railed or s["lower"].railed
        out["any_rail"] = (k["upper"].railed or k["lower"].railed
                           or out["sigma_at_grid_edge"])
        out["frozen_fitter_reported"] = None      # fit_thomas has no check at all
    else:
        a = dpp_alpha(fit["alpha"], fit["alpha_max"])
        out["alpha_railed_upper"] = a["upper"].railed
        out["alpha_railed_lower"] = a["lower"].railed
        out["any_rail"] = a["upper"].railed or a["lower"].railed
        out["frozen_fitter_reported"] = fit.get("at_boundary")
    return out
