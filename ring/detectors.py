"""Every detector this arc will report, declared HERE before it is built.

`detector_spec.DetectorSpec` refuses a detector without a negative set and a
named nearest confusable. This module is the arc's registry of those
declarations, so the Stage 0 checkpoint ("for every statistic you plan to
report you can name the negative set, the nearest confusable, and the
surrogate it beats") is a file that either constructs or raises, not a
paragraph.

Two states per detector:
  BUILT     — `record()` is called from a generator's banked output and
              `certify()` runs on the board (verify_ring.py).
  DECLARED  — the spec constructs (negative set + confusable named) but
              nothing scores it yet. The checker asserts it CONSTRUCTS and
              asserts it is NOT certified, so a declared detector can never be
              read as a passed one (gate_certifies_half_say_so).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from detector_spec import DetectorSpec                        # noqa: E402

# Threshold for "the marginal mode is present": lam1 above -LAM1_TOL. Set
# against the measured eps=0 floor (|lam1| ~ 1e-15) and BELOW the nearest
# confusable one dial step up (eps=1e-4: lam1 ~ -2.6e-7 at T=2000), so the
# confusable is silent by >100x, not by luck. A threshold at 1e-6 would have
# fired on it. DECLARED in stage1_marginal.py's sense: this constant is the
# detector, and verify_ring.py checks it against both rows of the banked table.
LAM1_TOL = 1e-9
AMP_MIN = 0.3   # a bump has to exist for its position to be marginal


def marginal_mode_spec() -> DetectorSpec:
    """BUILT (Stage 1, measure 1). Fires when a bump exists AND its position is
    a marginal direction of the fixed-point Jacobian."""
    return DetectorSpec(
        name="ring_marginal_mode",
        fires_on="bump amplitude > AMP_MIN and lam1 > -LAM1_TOL at a converged "
                 "fixed point (resid_max small)",
        positive_set={
            "intact_eps0_T200": "eps=0, T=200: exact continuum, lam1 at machine zero",
            "intact_eps0_T2000": "eps=0, T=2000: same, longer integration",
        },
        negative_set={
            "weak_pin_eps1e-4_T2000": "one dial step up; lam1 ~ -2.6e-7 — the "
                                      "NEAREST CONFUSABLE, still looks marginal "
                                      "at any tolerance looser than ~1e-7",
            "pinned_eps0.1_T2000": "fully collapsed to ~3 discrete attractors, "
                                   "lam1 ~ -1.5e-2",
            "no_bump_J1=1.0_T2000": "uniform state, no bump; amplitude gate must "
                                    "keep the detector silent even if lam1 is near 0",
        },
        nearest_confusable="the weakly pinned ring at eps=1e-4 — a continuum "
                           "broken by a perturbation four orders below the "
                           "drive, whose spectral signature is one part in 1e7",
        negative_rationale="a marginal-mode detector that fires on a weakly "
                           "pinned ring would call every real heterogeneous "
                           "network a continuous attractor",
    )


def ph_continuous_attractor_spec() -> DetectorSpec:
    """DECLARED (Stage 1, measure 2). The inference 'H1 rank 1 from PH on
    population vectors => continuous attractor'. Negative set is two-sided:
    topology without an attractor, attractor without a continuum."""
    return DetectorSpec(
        name="ph_topology_implies_continuous_attractor",
        fires_on="persistent H1 rank 1 on the population-vector cloud, after "
                 "the jitter ladder, within-cell ISI-order scramble, and "
                 "subsetting sweep",
        positive_set={
            "intact_ring_cloud": "population vectors from the eps=0 ring",
        },
        negative_set={
            "independent_modulated_poisson_S1": "di Sarra et al. 2025 "
                "construction on S^1: independent Poisson units with circular "
                "tuning + theta/eta oscillatory rate modulation, NO recurrence "
                "— reproduces the topology with no attractor",
            "pinned_ring_cloud": "eps=0.1 ring: a real attractor (three "
                "discrete points) with no continuum; H1 must NOT read rank 1 "
                "as 'continuous'",
        },
        nearest_confusable="the di Sarra construction — same barcodes, no "
                           "dynamics; PH is order-blind so the cloud alone "
                           "cannot tell them apart (plan v5, Stage 1)",
        negative_rationale="a marginal claim (cloud shape) is being read as a "
                           "dynamical one (attractor); the negative set holds "
                           "the two apart",
    )


def rotation_fit_spec() -> DetectorSpec:
    """DECLARED (Stage 2). jPCA-style rotation, with a rejection region."""
    return DetectorSpec(
        name="rotational_dynamics_fit",
        fires_on="r2_skew within tolerance of r2_full AND skew_frac above the "
                 "TME 95th percentile; fit_rejected otherwise",
        positive_set={
            "asymmetric_W_alpha_high": "W_sym + alpha W_asym at alpha where "
                                       "eigenvalues are complex",
        },
        negative_set={
            "symmetric_W": "alpha=0, gradient dynamics; any rotation is the "
                           "constraint's",
            "pure_decay_noise": "linear decay plus noise, TME-matched",
        },
        nearest_confusable="TME surrogates of the asymmetric run — same "
                           "covariance across time, neurons and conditions, "
                           "no dynamics; what jPCA with no rejection region "
                           "cannot refuse",
        negative_rationale="failure mode #14: a class space with no rejection "
                           "region; the negative set IS the rejection region",
    )


BUILT = {"ring_marginal_mode": marginal_mode_spec}
DECLARED_ONLY = {
    "ph_topology_implies_continuous_attractor": ph_continuous_attractor_spec,
    "rotational_dynamics_fit": rotation_fit_spec,
}
