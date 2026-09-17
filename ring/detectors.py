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


def ph_consistent_with_continuous_attractor_spec() -> DetectorSpec:
    """DECLARED (Stage 1, measure 2 — the detector measure 2 actually scores).

    The MARGINAL claim: the population-vector cloud has the topology a
    continuous attractor would leave (H1 rank 1 on S^1), and that topology
    survives the surrogates that destroy fine-timescale coincidence (jitter
    ladder) and sequence (within-cell ISI-order scramble). It says nothing
    about how the state MOVES. Named "consistent with" so that a clean
    measure-2 result cannot be banked as a dynamical finding."""
    return DetectorSpec(
        name="ph_topology_consistent_with_continuous_attractor",
        fires_on="persistent H1 rank 1 on the population-vector cloud, "
                 "stable under the jitter ladder below tau_c and under the "
                 "subsetting sweep",
        positive_set={
            "intact_ring_cloud": "population vectors from the eps=0 ring",
        },
        negative_set={
            "pinned_ring_cloud_converged": "eps=0.1 ring sampled AFTER "
                "collapse (T=2000, resid 3e-11): three discrete points, "
                "H0=3, H1=0",
            "jittered_cloud_above_tau_c": "the intact cloud with spike jitter "
                "above the ladder's critical tau: topology destroyed (di Sarra "
                "2025: 100-500 ms on real grid modules)",
            "within_cell_scrambled_cloud": "the intact cloud with each cell's "
                "ISI order scrambled (marginals kept, coincidence destroyed)",
        },
        nearest_confusable="the pinned ring sampled BEFORE collapse: its "
                           "transient cloud traces the ring (H1 rank 1) while "
                           "the attractor is three discrete points — the eps*T "
                           "contour puts the same network on both sides of "
                           "this detector depending on the window",
        negative_rationale="PH is order-blind; the surrogates are what "
                           "separate 'has the shape' from 'happened to pass "
                           "through the shape'. KNOWN BLIND SPOT of the "
                           "scramble (measure 2, 2026-09-16): a unit that fires "
                           "in ONE contiguous block is invariant under ISI "
                           "shuffling, so the surrogate only destroys sequence "
                           "expressed as REVISITS. On a single-sweep cloud (C) "
                           "it left a loop in 2/3 seeds; on multi-visit clouds "
                           "(A: 3 rotations) it killed it. Its power must be "
                           "stated per dataset as visits-per-unit before a "
                           "silent scramble is read as evidence.",
    )


def ph_with_continuous_traversal_spec() -> DetectorSpec:
    """DECLARED (Stage 3a) — the KINEMATIC rung between consistent_with and
    implies: the population state moves continuously along the manifold with a
    well-defined winding count (DREiMac circular coordinate, lifted). Stage 3a
    measured the ceiling: an independent-unit construction on the same
    trajectory (IND) reads identically, so this rung says nothing about an
    attractor. Its sealed statistic (per-step continuity) was DEFEATED on the
    random-order static cloud (0.998: smoothing bridges 15 jumps in 2000
    steps); the replacement candidate is total variation / net winding of the
    lifted path, to be sealed before it is scored."""
    return DetectorSpec(
        name="ph_topology_with_continuous_traversal",
        fires_on="circular coordinate readable (standard-range class) AND the "
                 "lifted path is continuous by a statistic that survives "
                 "smoothing + rare jumps (per-step continuity does NOT)",
        positive_set={
            "driven_ring_A": "3.18 rotations; |n| = 3 in 9/9 readable seeds",
            "independent_units_IND": "same trajectory, no recurrence; reads "
                                     "identically — a POSITIVE here, the "
                                     "confusable one rung up",
        },
        negative_set={
            "random_order_static_C_perm": "16 static bumps in random order: "
                "no traversal; per-step continuity read 0.998 (defeated); "
                "|n| random 0/1",
            "converged_pinned_D": "three static clusters, no motion",
            "unreadable_low_rho": "no standard-range class: must read "
                "UNREADABLE, never a count (the fallback emitted 14/15 wrong)",
        },
        nearest_confusable="C_perm — a sequence of static states whose rare "
                           "jumps smoothing turns into fast sweeps; the "
                           "statistic must see the jumps, not the steps",
        negative_rationale="a lift that reads a shuffled sequence as a "
                           "traversal would certify order-to-topology "
                           "conversion as motion",
    )


def ph_implies_continuous_attractor_spec() -> DetectorSpec:
    """DECLARED THROUGH ALL OF STAGE 1, BY DESIGN. No barcode promotes it.

    The DYNAMICAL claim: the state moves along the manifold the cloud has.
    Certifying it needs a temporal statistic — Stage 3's path-lifting decoder
    (persistent cohomology -> circular coordinates -> lift to the universal
    cover) or zigzag persistence. Until one exists the board refuses to let
    this read as certified (verify_ring.py R1), and measure 2's output is
    NOT the thing that clears it."""
    return DetectorSpec(
        name="ph_topology_implies_continuous_attractor",
        fires_on="ph_topology_consistent_with_continuous_attractor fires AND a "
                 "temporal statistic (path-lifted trajectory winding, or "
                 "zigzag H1 persisting across time windows) is consistent "
                 "with motion along the manifold",
        positive_set={
            "intact_ring_trajectory": "the eps=0 ring's state trajectory, "
                                      "lifted to the universal cover",
        },
        negative_set={
            "independent_modulated_poisson_S1": "di Sarra et al. 2025 "
                "construction on S^1: independent Poisson units with circular "
                "tuning + theta/eta oscillatory rate modulation, NO recurrence "
                "— same barcodes, no attractor, no motion along the manifold",
            "pinned_ring_transient": "the pinned ring before collapse: the "
                "cloud traces the ring but the lifted trajectory slides to a "
                "point and stops",
        },
        nearest_confusable="the di Sarra construction — identical marginal "
                           "topology by construction; only a temporal "
                           "statistic separates it (plan v5, Stage 1)",
        negative_rationale="this is the inference the manifold literature "
                           "makes from a barcode; the negative set is the "
                           "reason it cannot be made from one",
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
    "ph_topology_consistent_with_continuous_attractor":
        ph_consistent_with_continuous_attractor_spec,
    "ph_topology_with_continuous_traversal":
        ph_with_continuous_traversal_spec,
    "ph_topology_implies_continuous_attractor":
        ph_implies_continuous_attractor_spec,
    "rotational_dynamics_fit": rotation_fit_spec,
}
# Certification paths, so nobody reads a DECLARED detector as pending the
# wrong measurement:
#   consistent_with  -> Stage 1 measure 2 (ripser barcodes + persim distances)
#   with_traversal   -> Stage 3a path-lifting (DREiMac); statistic to be re-sealed
#   implies          -> Stage 3b: transverse-relaxation anisotropy with a
#                       tangent-projected residual (L4b); L4's 32-bin residual
#                       did not separate even at the rate level
#   rotational_fit   -> Stage 2 (skew_frac vs TME); a real path, exists
STAGE1_CANNOT_CERTIFY = {"ph_topology_implies_continuous_attractor"}
