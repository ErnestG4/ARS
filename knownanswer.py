"""GATE D — a DISORDERED known-answer configuration with an exact local statistic.

A guard module, in the shape of `reachable.py` and `railed.py`: importable, no
side effects, and it REFUSES rather than reports.

WHY IT EXISTS
-------------
derivflow's two known-answer gates are Gate L (picket fence, exactly periodic)
and Gate H (Hermite seed, near-crystalline). Both are ORDERED configurations,
and that is a structural blindness rather than a strictness setting:

    an ORDERED configuration has no gap FLUCTUATION, and the bias class of
    interest damps the fluctuation about the mean gap.

Damping s -> mu + (1-d)(s - mu) moves a disordered configuration's statistic by
exactly -d and leaves a picket fence at identically zero, because a picket
fence's gaps are already all mu. So neither ordered gate can object no matter
how large the damping gets.

CORRECTED 2026-09-13. This docstring, and the demonstration in
verify_knownanswer.py, previously attributed the blindness to r-tilde's
invariance under a COMMON RESCALING of the gaps. That invariance is real but it
is CONFIGURATION-INDEPENDENT -- rescaling a disordered lattice by any factor
moves the statistic by 0 to 3.4e-15 as well -- so it cannot explain why an
ordered gate is blind and a disordered one is not. The conclusion was right and
the stated reason was wrong; an independent audit found it. The checker now
exercises the damping map on both configurations AND shows the rescaling control
failing to discriminate, so the two cannot be conflated again. Measured 2026-09-09: picket-fence
readouts sit at 1e-9..1e-11 while the same instrument carried a +17% to +271%
bias on disordered input (TAIL_AUDIT_2026_09_09.md). The gates were not lax.
They were blind, and running them harder would never have helped.

THE CONFIGURATION
-----------------
A perturbed lattice: gaps s_i = 1 + eta * z_i, with z iid standard normal. For
small eta the mean gap-ratio distance has a closed form,

    1 - <r-tilde>  =  (2 / sqrt(pi)) * eta  +  O(eta^2)

because 1 - r-tilde = eta * |z_i - z_{i+1}| + O(eta^2), and z_i - z_{i+1} is
N(0, 2), whose mean absolute value is 2/sqrt(pi).

Three properties, and it is the CONJUNCTION that makes it a gate:

  1. DISORDERED — a translation-invariant bias does not cancel, so it can fire.
  2. EXACT — a closed form, not a numerical reference that would itself need
     certifying. Gate H's truth is exact Hermite roots; this is the same move
     one level cheaper.
  3. TUNABLE TO ANY VALUE OF THE STATISTIC. Gates L and H each pin one point of
     the axis (crystalline, near-crystalline). eta sweeps it continuously,
     including the 1e-5 regime where derivflow's tail lives and where the bias
     was measured. That is the property neither existing gate has at all.

AND IT STATES WHAT IT CAN DETECT. `detectable_bias` returns the smallest
relative bias this configuration can resolve at a given (eta, n_gaps, reps).
A gate whose sensitivity is unstated is one that has not been shown to fire,
which is the exact defect that produced this module.
"""
import numpy as np

__all__ = ["EXACT_COEFF", "exact_statistic", "perturbed_lattice", "rtilde_distance",
           "truth_by_simulation", "detectable_bias", "assert_recovers",
           "KnownAnswerFailure"]

EXACT_COEFF = 2.0 / np.sqrt(np.pi)      # 1.1283791670955126

# Relative sd of a single-window estimate of 1-<r-tilde>, times sqrt(n_gaps).
# DERIVED, not chosen: measured 2026-09-10 over W = 200..51200 x 400 reps, giving
# 0.8984 / 0.9137 / 0.9157 / 0.9178 / 0.8779 (no trend; the spread is Monte-Carlo
# noise). `verify_knownanswer.py` RE-DERIVES this on every board run and fails if
# it drifts, so it cannot quietly go stale or stay wrong.
#
# It was first written here as 0.0654 -- a number typed rather than measured, and
# wrong by 14x in the direction that OVERSTATES the gate's sensitivity. Recorded
# because a known-answer gate that overstates what it can resolve is the precise
# failure this module exists to prevent, and it happened during the writing of
# the module. Used ONLY to report sensitivity, never to correct a reading.
_REL_SD_PER_ROOT_GAP = 0.905


class KnownAnswerFailure(AssertionError):
    """A known-answer gate did not recover its own truth."""


def exact_statistic(eta):
    """1 - <r-tilde> for gaps 1 + eta*z, to leading order in eta.

    The O(eta^2) term is genuinely negligible where a gate wants to sit: at
    eta = 1e-4 the closed form matches simulation to ~4 significant figures. For
    eta above ~1e-2, certify with `truth_by_simulation` instead of trusting this.
    """
    return EXACT_COEFF * float(eta)


def perturbed_lattice(n, eta, rng):
    """Positions whose consecutive gaps are 1 + eta*z, z iid standard normal.

    Returns positions (not gaps) because that is what an unfolding pipeline
    consumes. Gaps are clipped to stay positive, which matters only for eta
    large enough that the closed form has already stopped applying.
    """
    g = 1.0 + float(eta) * rng.standard_normal(int(n) - 1)
    g = np.maximum(g, 1e-12)
    return np.concatenate(([0.0], np.cumsum(g)))


def rtilde_distance(positions):
    """1 - <r-tilde> over the gaps of `positions`. The statistic under test."""
    s = np.diff(np.asarray(positions, dtype=np.float64))
    s = s[s > 0]
    if s.size < 2:
        return float("nan")
    a, b = s[:-1], s[1:]
    return float(1.0 - np.mean(np.minimum(a, b) / np.maximum(a, b)))


def truth_by_simulation(eta, n=20001, reps=200, seed=0):
    """Standalone truth: the statistic computed WITHOUT any unfolding.

    The same move Gate L makes by computing the picket fence's true one-step
    response standalone (<= 1e-8) before gating the pipeline against it. Nothing
    here touches the instrument, so a disagreement between this and a pipeline
    reading is a property of the pipeline.

    Returns (mean, sem).
    """
    rng = np.random.default_rng(seed)
    v = np.array([rtilde_distance(perturbed_lattice(n, eta, rng))
                  for _ in range(int(reps))])
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(v.size))


def detectable_bias(n_gaps, reps=1, n_sigma=5.0):
    """Smallest RELATIVE bias in 1-<r-tilde> this gate resolves, as a fraction.

    The statistic is a mean over gap pairs, so its relative sampling error falls
    as 1/sqrt(n_gaps * reps) and is independent of eta (eta scales signal and
    noise together) -- which is exactly why eta can be pushed to the regime of
    interest without losing sensitivity.

    Report this next to any PASS. A gate that cannot resolve the bias size under
    discussion is inert, and an inert gate reporting PASS is non-evidence.
    """
    rel_sem = _REL_SD_PER_ROOT_GAP / np.sqrt(float(n_gaps) * float(reps))
    return float(n_sigma * rel_sem)


def assert_recovers(measured, eta, n_gaps, reps=1, n_sigma=5.0, name="gate D"):
    """REFUSE unless `measured` recovers the exact truth within the gate's own
    resolution. Raises KnownAnswerFailure; returns the relative deviation.

    The tolerance is DERIVED from the configuration's sampling error, not chosen.
    A hand-set tolerance on a known-answer gate is a free parameter sitting
    exactly where the answer is decided.
    """
    truth = exact_statistic(eta)
    if not np.isfinite(measured) or truth <= 0:
        raise KnownAnswerFailure(f"{name}: non-finite reading {measured!r}")
    rel = float(measured - truth) / truth
    tol = detectable_bias(n_gaps, reps, n_sigma)
    if abs(rel) > tol:
        raise KnownAnswerFailure(
            f"{name}: read {measured:.6e}, truth {truth:.6e} "
            f"({rel:+.2%}), outside {tol:.2%} at {n_sigma:g} sigma "
            f"({int(n_gaps)} gaps x {int(reps)} reps). "
            "A translation-invariant bandwidth bias cancels on an ORDERED "
            "configuration; this one is disordered, so it does not.")
    return rel
