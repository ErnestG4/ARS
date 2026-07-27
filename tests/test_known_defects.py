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
