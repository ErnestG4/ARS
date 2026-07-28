"""
test_known_defects.py — every real defect this arc found, as a NAMED regression fixture.

THE MODEL, found by the propagation sweep itself: `thermo/gate_fixtures.py` keeps the
Jenkinson–Pollicott digit transposition as `DIM_E2_REPO_TRANSPOSED` — the *wrong* value retained,
named, and tested against, rather than deleted. Deleting a wrong value loses the evidence the error
ever happened; keeping it as a named fixture means the suite permanently tests that this specific
error cannot come back.

So: fixed-and-FIXTURED, not fixed-and-forgotten. And a fixture is in the shared test path by
construction, which is the only form that survives the propagation channel.

This file ALSO runs the four watchers, because they were built as standalone scripts that nobody
imports — which put them in exactly the state `irep_unclipped` was in on 2026-07-12: correct,
validated, and unable to fire. A guard that must be remembered is not a guard. Now `pytest` fires them.
"""
from __future__ import annotations
import subprocess
import sys
import os

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# ─────────────────────────────────────────────────────────────────────────────
# NAMED DEFECTS. Each constant records a value the repo once reported, with the
# mechanism that produced it. The test asserts the repaired path no longer does.
# ─────────────────────────────────────────────────────────────────────────────

IREP_CLIPPED_SATURATES_TO_ZERO = 0.0
"""What `repulsion_integral` reports for ANY clustered process. Real fungal read exactly this
while its true signed value was -2.212. One-ended saturation: hides magnitude."""

FUNGAL_IREP_SIGNED_TRUTH = -2.21198
"""The value the clip erased. Reproduced under both (r_max=5,n=50) and (10,100)."""

BRODY_AXIS_SATURATES_BOTH_ENDS = (0.0, 1.0)
"""`I8_brody_q` fits on these bounds, so clustered pins to ~0.0000 and GOE *and* GUE both pin to
~0.9999 (true +1.0032 and +1.5325). TWO-ended saturation: hides IDENTITY, not just magnitude —
the axis could not distinguish the RMT classes the program exists to separate."""

BRODY_GUE_TRUTH = 1.5325
BRODY_GOE_TRUTH = 1.0032


def _inv_cdf(pdf, n, rng, hi=6.0, m=200001):
    g = np.linspace(0, hi, m)
    F = np.cumsum(pdf(g))
    F /= F[-1]
    s = np.interp(rng.random(n), F, g)
    return s / s.mean()


def test_irep_signed_recovers_what_the_clip_erased():
    """Defect 1: np.maximum(0, 1-R2) clipped the INTEGRAND, so any clustered process read 0.000."""
    from arithmetic_toolkit import pair_correlation_full
    rng = np.random.default_rng(7)
    m = 4000 // 3
    c = np.cumsum(rng.exponential(1.0, m))
    t = np.sort((c[:, None] + rng.normal(0, 0.15, (m, 3))).ravel())
    d = np.diff(t); d = d[d > 0]
    out = pair_correlation_full(np.cumsum(d / d.mean()))
    assert out["repulsion_integral"] == pytest.approx(IREP_CLIPPED_SATURATES_TO_ZERO, abs=1e-9), \
        "the deprecated field must stay bit-identical; banked numbers depend on it"
    assert out["repulsion_integral_signed"] < -0.5, \
        "the signed field must represent clustering the clip erased"


def test_brody_unbounded_separates_goe_from_gue():
    """Defect 2: bounds=(0,1) pinned GOE and GUE to the SAME value. Class-collapse."""
    from cross_substrate.axes import I8_brody_q, I8_brody_q_unbounded
    from universality import nns_goe, nns_gue
    rng = np.random.default_rng(7)
    goe = _inv_cdf(nns_goe, 40000, rng)
    gue = _inv_cdf(nns_gue, 40000, rng)

    d_goe, d_gue = I8_brody_q(goe), I8_brody_q(gue)
    assert abs(d_goe - d_gue) < 0.01, \
        "the deployed axis must stay bit-identical -- it DOES collapse the classes, and that is why"
    assert d_gue == pytest.approx(BRODY_AXIS_SATURATES_BOTH_ENDS[1], abs=1e-3)

    r_goe, r_gue = I8_brody_q_unbounded(goe), I8_brody_q_unbounded(gue)
    assert r_goe == pytest.approx(BRODY_GOE_TRUTH, abs=0.05)
    assert r_gue == pytest.approx(BRODY_GUE_TRUTH, abs=0.05)
    assert r_gue - r_goe > 0.4, "the repaired axis must SEPARATE the classes"


def test_clip_bias_is_two_sided_and_opposite():
    """Defect 3: the clip is conservative on the observed side (saturation) and ANTI-conservative
    on the null side (rectification of symmetric noise). Opposite directions, different sizes."""
    from arithmetic_toolkit import pair_correlation_full
    # R-101's lesson, applied to a fixture: assert the DIRECTION over replicates, never a
    # magnitude seen in one draw. At n=4000 the signed Poisson value scatters over ~+/-0.03
    # between seeds, so `abs(signed) < 0.01` was pinning noise.
    rng = np.random.default_rng(11)
    clipped, signed = [], []
    for _ in range(20):
        x = rng.exponential(1.0, 4000)
        out = pair_correlation_full(np.cumsum(x / x.mean()))
        clipped.append(out["repulsion_integral"])
        signed.append(out["repulsion_integral_signed"])
    c, g = np.array(clipped), np.array(signed)
    assert c.mean() > g.mean(), "the clip must rectify Poisson UPWARD relative to the signed field"
    assert (c > g).mean() >= 0.9, "and do so on almost every draw, not on average only"
    assert abs(g.mean()) < 3 * g.std(ddof=1) / np.sqrt(len(g)), \
        "the signed field must be consistent with 0 on Poisson, within its OWN sem"


SPACINGS_POSITIONAL_TRIM_REMOVES_NO_OUTLIERS = True
"""`phase35a/unfold_rotnum.spacings` slices d[2%:98%] of an UNSORTED diff array -- positional, so it
drops edge-of-record gaps, not extreme ones. Measured effect on Allen ks_gue: 0.854 -> 0.416."""

BULK_RECOVERY_INTERP_CLAMPS = True
"""`np.interp` clamps outside its range, so every clustered band mapped to the Poisson-regime knot."""

BERRY_ROBNIK_EVERY_CALIBRATOR_SITS_AT_A_RAIL = True
"""rho is a GOE fraction so [0,1] is definitionally right -- but poisson 0.0015, clustered 0.0045,
goe 0.9965, gue 0.9975 are ALL rail-proximate. The axis identifies only in the interior."""

GLOBAL_UNFOLD_LEAVES_DRIFT = 1.2185
"""CV of a rate-halving cell under global unit-mean unfolding; windowed gives 1.0122, true 1.0."""


def test_value_trim_removes_outliers_where_positional_does_not():
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "phase35a"))
    from unfold_rotnum import spacings, spacings_value_trimmed
    rng = np.random.default_rng(5)
    d = np.concatenate([rng.exponential(1.0, 500), [40.0, 55.0], rng.exponential(1.0, 498)])
    u = np.cumsum(d)
    assert (spacings(u) > 10).sum() > 0, "deployed positional trim must still RETAIN outliers"
    assert (spacings_value_trimmed(u) > 10).sum() == 0, "value trim must remove them"


def test_berry_robnik_flags_every_calibrator_as_rail_proximate():
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "cross_substrate"))
    from cross_substrate.axes import I9_berry_robnik_rail_flag
    from validate_fitters import sample_poisson, sample_goe, sample_clustered, sample_gue
    for f in (sample_poisson, sample_goe, sample_clustered, sample_gue):
        assert I9_berry_robnik_rail_flag(f(4000, 0)) is True


def test_windowed_unfold_removes_drift_global_leaves():
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "phase22a"))
    from ars_classify import unfold_unit_mean, unfold_unit_mean_windowed
    rng = np.random.default_rng(4)
    t = np.cumsum(np.concatenate([rng.exponential(1.0, 2000), rng.exponential(3.0, 2000)]))
    cv = lambda u: (lambda d: d.std() / d.mean())(np.diff(u)[np.diff(u) > 0])
    assert cv(unfold_unit_mean(t)) > 1.15, "global unfold must retain the drift"
    assert abs(cv(unfold_unit_mean_windowed(t)) - 1.0) < 0.05, "windowed must remove it"


def test_pair_correlation_warns_on_non_unit_mean_input():
    import warnings
    from arithmetic_toolkit import pair_correlation_full
    rng = np.random.default_rng(4)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        pair_correlation_full(np.cumsum(rng.exponential(0.3, 3000)))
        assert any("rate-contaminated" in str(x.message) for x in w)


# ─────────────────────────────────────────────────────────────────────────────
# THE WATCHERS. Built as scripts nobody imports -> unable to fire. pytest fires them.
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("script", [
    "commensurable.py",
    "arsrh/rep_int_migration.py",
    "propagation_watch.py",
])
def test_watcher_reports_no_regression(script):
    """Each watcher exits non-zero only on a REGRESSION (ratcheted). A red here means something
    got worse, not that a backlog exists."""
    r = subprocess.run([sys.executable, os.path.join(ROOT, script), "--summary"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, f"{script} reports a REGRESSION:\n{r.stdout[-1200:]}"


def test_commensurable_guard_is_live_and_specific():
    """The guard's own sensitivity/specificity/interface suite must pass."""
    import commensurable
    assert commensurable._selftest(verbose=False), "commensurable guard is not live"


CYCLIC_STRATUM_POOLS_DUPLICATE_ORBITS = {5: (8, 2), 13: (6, 3), 17: (6, 3), 29: (4, 2)}
"""`gate0e_precision.collect_cyclic` enumerates POLYNOMIALS and dedups by nothing, so each stratum
pools GL2(Z) translates of the SAME cubic irrational -- identical (g,y,lambda) orbits. Map is
|t| -> (n_polynomials, n_independent_orbits). Duplication leaves meas and pred unchanged and
multiplies n by k, so every pooled |z| inflates by exactly sqrt(k): |t|=5 by 2.00x, |t|=13 by 1.41x.
This is what made R-156/R-158's +3.30 and R-161's look-elsewhere p=0.0100 look significant."""


def test_cyclic_strata_contain_duplicate_gl2z_orbits():
    """Defect 10: the deployed collector pools duplicate orbits; the repair separates them."""
    import mpmath as mp
    _s = sys
    _s.path.insert(0, os.path.join(ROOT, "arsrh", "cubic"))
    from gate0e_precision import collect_cyclic, gl2z_orbit_reps

    by_t = collect_cyclic(box=14, per=8)

    # the deployed collector must stay bit-identical -- it DOES pool duplicates, and that is why
    for t, (n_poly, n_orb) in CYCLIC_STRATUM_POOLS_DUPLICATE_ORBITS.items():
        assert len(by_t[t]) == n_poly, f"|t|={t} polynomial count changed"

    # and the duplication is EXACT, not statistical: two |t|=13 roots differ by exactly 1
    mp.mp.dps = 260
    roots = []
    for (A, B, C, _M) in by_t[13]:
        r = sorted(mp.re(x) for x in mp.polyroots([1, A, B, C], maxsteps=400, extraprec=800))
        roots.append(r[0])
    exact_int_pairs = sum(1 for i in range(len(roots)) for j in range(i + 1, len(roots))
                          if abs((roots[i] - roots[j]) - mp.nint(roots[i] - roots[j])) < mp.mpf(10) ** -50)
    assert exact_int_pairs >= 2, "|t|=13 must contain GL2(Z) translates (roots differing by an integer)"

    # the repair must recover the true independent-orbit counts
    for t, (_n_poly, n_orb) in CYCLIC_STRATUM_POOLS_DUPLICATE_ORBITS.items():
        assert len(gl2z_orbit_reps(by_t[t])) == n_orb, \
            f"|t|={t}: dedup must find {n_orb} independent GL2(Z) orbits"


BOX_DIM_FITS_THROUGH_SATURATED_TAIL = True
"""`sturmian_hamiltonian_run.box_dim` selects `m = counts > 1`, which INCLUDES the fine-scale regime
where every eigenvalue lands in its own box, so counts -> N and the log-log slope flattens toward a
value set by the SAMPLING rather than by the set. Same saturation family as the Brody bounds and the
clipped I_rep. box_dim_windowed (written in a leaf nothing imports, propagated 2026-07-28) fits only
where counts >= 8 and <= 0.5N."""

PROMOTED_PRIVATE_SYMBOLS = [
    ("cross_substrate.trace_map_dimension", "potential", "_potential"),
    ("universality", "ks_pvalue", "_ks_pvalue"),
    ("surrogates", "fit_hawkes_exponential", "_fit_hawkes_exponential"),
    ("surrogates", "simulate_hawkes", "_simulate_hawkes"),
    ("transition_diagnostic", "distance_trajectory", "_distance_trajectory"),
    ("cross_substrate.allen_depth", "session_tasks", "_session_tasks"),
]
"""Six symbols leaf modules reached past the public API for (watcher signature A). Promoted as
ALIASES so the private name stays bit-identical -- banked numbers came off calls to it."""


@pytest.mark.parametrize("mod,pub,priv", PROMOTED_PRIVATE_SYMBOLS)
def test_promoted_symbol_is_an_alias_not_a_reimplementation(mod, pub, priv):
    """The promotion must be a same-object alias: a re-implementation could drift from the
    private version that banked numbers came off, which is the whole risk being avoided."""
    import importlib
    m = importlib.import_module(mod)
    assert hasattr(m, priv), f"{mod}.{priv} must be RETAINED, not renamed"
    assert hasattr(m, pub), f"{mod}.{pub} must exist"
    assert getattr(m, pub) is getattr(m, priv), \
        f"{mod}.{pub} must BE {priv} (same object), not a copy"


def test_box_dim_windowed_beats_deployed_on_a_set_of_known_dimension():
    """Defect 11: known-answer test. Uniform points on an interval have box dimension 1.0."""
    from cross_substrate.sturmian_hamiltonian_run import box_dim, box_dim_windowed
    rng = np.random.default_rng(0)
    e = np.sort(rng.random(4000))
    deployed = box_dim(e)
    repaired, n_window = box_dim_windowed(e)
    assert n_window >= 4, "the window must retain enough points to fit"
    # the deployed estimator must stay bit-identical -- it IS biased low, and that is the record
    assert deployed < 0.95, "deployed box_dim must still fit through the saturated tail"
    assert abs(repaired - 1.0) < abs(deployed - 1.0), \
        "the windowed fit must be CLOSER to the known dimension 1.0"
