"""The covariance/bootstrap fork, as code rather than judgement.

A guard module in the shape of `reachable`, `railed`, `spacings`, `lineage`:
importable, no side effects, and it REFUSES rather than reports.

WHY THIS EXISTS. Stage 3d found that neither error model is right at both ends
of a fit window. The fit-covariance model (absolute_sigma diagonal) sees the
(tau,beta) DEGENERACY on short windows -- corr = 0.999-1.000 on seven points --
and is blind to across-k replicate correlation and to misspecification. The
replicate bootstrap sees the correlation and part of the misspecification, and
is blind to the degeneracy because sixteen near-identical replicates do not
explore a flat direction in parameter space. At the degenerate cell the
bootstrap is overconfident by 4-6x; at the long window the covariance is.

So there is a SELECTION RULE -- degenerate fits get covariance, well-conditioned
fits get bootstrap -- and it is principled. The risk is that it gets applied by
inspection. "Which error model do I trust here" is a researcher degree of
freedom with a known direction of temptation (Will, 2026-09-15). DetectorSpec
style: the threshold is DECLARED, the cell REFUSES to produce a z without the
fork firing one way or the other, and BOTH numbers are reported for every cell
so a reader sees the fork rather than the selection.

WHAT IT ALSO SAYS. At corr(tau,beta) above the threshold the two parameters are
not separately identified -- only a combination is constrained. A cell that
quotes individual tau and beta with individual errors at such a fit is quoting
something the fit does not determine, and the result carries that flag.

WHAT IT DOES NOT FIX. absolute_sigma=False is NOT the alternative. It scales the
covariance by chi2/dof, which assumes misspecification inflates uncertainty
ISOTROPICALLY in parameter space; with corr = 1.000 there is obviously a
direction, and the scaling is wrong exactly where it matters. chi2/dof growing
with n (0.76 / 2.29 / 3.76 for iid) is a model-adequacy problem wearing an
error-bar costume: F3 describes the data WORSE as power increases, which is the
signature of a structurally wrong model being revealed, not of underestimated
noise. This module chooses between two error models for a fit; it does not make
the fit right.
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np

__all__ = ["ShapeZ", "shape_z", "degeneracy_of", "UndeclaredThreshold",
           "COVARIANCE", "BOOTSTRAP"]

COVARIANCE = "covariance"
BOOTSTRAP = "bootstrap"


class UndeclaredThreshold(ValueError):
    """A z was requested without declaring what counts as degenerate."""


@dataclass(frozen=True)
class ShapeZ:
    """Both z's, the degeneracy that decided between them, and the decision.

    Every field is populated for every call. A consumer that wants only the
    selected value must still be handed the other one, which is the point.
    """
    z_covariance: float
    z_bootstrap: float
    degeneracy: float          # max |corr| among the shape parameters, both classes
    threshold: float
    selected: str              # COVARIANCE or BOOTSTRAP
    reason: str
    separately_identified: bool

    @property
    def z(self) -> float:
        return self.z_covariance if self.selected == COVARIANCE else self.z_bootstrap

    def record(self) -> dict:
        return dict(z_covariance=self.z_covariance, z_bootstrap=self.z_bootstrap,
                    degeneracy=self.degeneracy, threshold=self.threshold,
                    selected=self.selected, reason=self.reason,
                    separately_identified=self.separately_identified)


def degeneracy_of(cov, shape_idx=(1, 2)) -> float:
    """Max |corr| among the named shape parameters of one fit covariance."""
    c = np.asarray(cov, dtype=np.float64)
    worst = 0.0
    for i in shape_idx:
        for j in shape_idx:
            if j <= i:
                continue
            d = np.sqrt(c[i, i] * c[j, j])
            if d > 0:
                worst = max(worst, abs(c[i, j] / d))
    return float(worst)


def shape_z(delta: float, se_cov_a: float, se_cov_b: float,
            se_boot_a: float, se_boot_b: float,
            cov_a, cov_b, threshold: Optional[float],
            shape_idx=(1, 2)) -> ShapeZ:
    """Both z's for a parameter difference, and the declared fork.

    REFUSES if `threshold` is None: a cell must say what it counts as degenerate
    before it is allowed a z at all. The fork then fires exactly one way; the
    non-selected number is still returned.
    """
    if threshold is None:
        raise UndeclaredThreshold(
            "shape_z called without a degeneracy threshold. Declare it as a "
            "modelparams Param (TESTED with a sweep, or DECLARED with a defence) "
            "and pass it here. Selecting an error model by inspection is the "
            "researcher degree of freedom this fork exists to remove.")
    if not (0.0 < threshold < 1.0):
        raise UndeclaredThreshold(f"threshold must lie in (0,1), got {threshold!r}")
    deg = max(degeneracy_of(cov_a, shape_idx), degeneracy_of(cov_b, shape_idx))
    zc = float(delta) / float(np.hypot(se_cov_a, se_cov_b))
    zb = float(delta) / float(np.hypot(se_boot_a, se_boot_b))
    if deg >= threshold:
        sel, why = COVARIANCE, (
            f"degenerate: max |corr| among shape params = {deg:.4f} >= "
            f"{threshold}; the bootstrap cannot see a flat direction that "
            "near-identical replicates do not explore")
    else:
        sel, why = BOOTSTRAP, (
            f"well-conditioned: max |corr| = {deg:.4f} < {threshold}; the "
            "covariance ignores across-k replicate correlation and "
            "misspecification, which the bootstrap carries")
    return ShapeZ(zc, zb, deg, float(threshold), sel, why,
                  separately_identified=(deg < threshold))
