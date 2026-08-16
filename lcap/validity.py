"""L0 — validity-scale map.  COMMITTED GENERATOR of lcap/validity_scales.json.

For each substrate family, the scale beyond which the GUE form is NOT
expected to describe the number variance — derived, with an anchor, never
fitted to make a row come out a particular way (brief tripwire 3).

  * zeta / L-functions — BERRY SATURATION.  For zeros near height T the
    number variance follows the RMT form only up to L ~ ln(T/2pi) in mean-
    spacing units; above it the prime-sum contribution truncates and Sigma^2
    saturates.  Anchor: M.V. Berry, "Semiclassical formula for the number
    variance of the Riemann zeros", Nonlinearity 1 (1988) 399-407.  This is
    SUBSTRATE PHYSICS, independent of any instrument in this repo.
  * finite random-matrix spectra — n-LIMITED.  Derived empirically here: the
    largest L at which the finite-n ensemble mean stays within DEV_TOL of the
    Mehta asymptotic.  Derived, not assumed, and checkable.
  * Poisson / renewal — NO SATURATION.  Sigma^2 grows linearly for all L;
    the GUE form never applied, so there is no GUE-validity window to cap.
    Recorded as NOT_APPLICABLE (an informative row, not a missing one).
  * clock / jittered clock — NO GUE VALIDITY WINDOW.  These are not GUE
    substrates at any scale; the rule must classify them correctly at every
    L, which is exactly what the zoo gate tests.

A substrate with no derivable window is banked as such — the map's honesty
depends on it having explicit empty cells.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap"):
    if p not in sys.path:
        sys.path.insert(0, p)
import gate_probe as G                                          # noqa: E402

DEV_TOL = 0.10          # sealed: 10% departure from the Mehta asymptotic
L_SCAN = [2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0, 40.0, 50.0, 70.0, 100.0]


def berry_scale(t_max):
    """Berry saturation scale in mean-spacing units."""
    return float(np.log(t_max / (2.0 * np.pi)))


def finite_n_scale(n, seeds=16, deg=6):
    """Largest scanned L whose ensemble mean is within DEV_TOL of Mehta."""
    best = None
    devs = {}
    for L in L_SCAN:
        gue, _ = G.bands(n, L, seeds, deg)
        gm = gue["sigma2"]["mean"]
        an = G.sigma2_gue_analytic(L)
        dev = abs(gm - an) / an
        devs[str(L)] = dict(measured=float(gm), analytic=float(an),
                            rel_dev=float(dev))
        if dev <= DEV_TOL:
            best = L
        else:
            break
    return best, devs


def main():
    zeros = np.load(f"{ROOT}/zeros_2000.npy")
    out = {"tolerance": DEV_TOL, "L_scan": L_SCAN, "substrates": {}}

    L_berry = berry_scale(float(zeros[-1]))
    out["substrates"]["zeta_first_2000"] = dict(
        kind="arithmetic/L-function", n=int(zeros.size),
        T_max=float(zeros[-1]), validity_L=L_berry,
        basis="BERRY_SATURATION",
        anchor="Berry 1988, Nonlinearity 1:399 — Sigma^2 follows RMT only "
               "for L << ln(T/2pi); saturates above",
        derived_not_fitted=True)
    print(f"  zeta_first_2000: T={zeros[-1]:.0f} -> validity L = "
          f"{L_berry:.2f} (Berry)", flush=True)

    for tag, n in (("gue_n2000", 2000), ("gue_n1200", 1200),
                   ("gue_n343", 343)):
        Lmax, devs = finite_n_scale(n)
        out["substrates"][tag] = dict(kind="finite random-matrix spectrum",
                                      n=n, validity_L=Lmax,
                                      basis="FINITE_N_DERIVED",
                                      anchor="largest scanned L within "
                                             f"{DEV_TOL:.0%} of the Mehta "
                                             "asymptotic (measured here)",
                                      scan=devs, derived_not_fitted=True)
        print(f"  {tag}: validity L = {Lmax} (finite-n, derived)", flush=True)

    for tag in ("poisson", "wigner_renewal"):
        out["substrates"][tag] = dict(
            kind="linear-growth process", validity_L=None,
            basis="NOT_APPLICABLE",
            anchor="Sigma^2 grows linearly at all L; the GUE form never "
                   "applied, so there is no GUE-validity window to cap")
        print(f"  {tag}: NOT_APPLICABLE (no GUE window to cap)", flush=True)

    for tag in ("clock", "jitter_clock"):
        out["substrates"][tag] = dict(
            kind="hyper-rigid deterministic", validity_L=None,
            basis="NO_GUE_WINDOW",
            anchor="not a GUE substrate at any scale; the rule must "
                   "classify it correctly at every L (zoo gate)")
        print(f"  {tag}: NO_GUE_WINDOW", flush=True)

    json.dump(out, open(f"{ROOT}/lcap/validity_scales.json", "w"), indent=1)
    print(f"banked {len(out['substrates'])} validity rows", flush=True)


if __name__ == "__main__":
    main()
