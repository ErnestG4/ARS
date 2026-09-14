"""Certify GATE D — and prove it can fire, on the exact defect class that made it necessary.

A known-answer gate that has never been shown to FAIL is not evidence, and that
is not an abstract worry here: derivflow's Gate L and Gate H ran green through
the entire campaign while carrying a +17% to +271% bias, because both are
ORDERED configurations and the bias class cancels identically on those. This
checker therefore does four things, and the last two are the point:

  1. The closed form is right. (2/sqrt(pi))*eta against direct simulation.
  2. The stated sensitivity is right, and RE-DERIVED rather than trusted.
  3. RED PATH — an injected bias larger than the stated resolution must make
     `assert_recovers` RAISE, and one below it must not.
  4. THE BLINDNESS DEMONSTRATION — the same injected bias applied to an ORDERED
     configuration must leave the statistic unmoved, reproducing in miniature
     why the two existing gates could not object.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from knownanswer import (EXACT_COEFF, exact_statistic, perturbed_lattice,   # noqa: E402
                         rtilde_distance, truth_by_simulation, detectable_bias,
                         assert_recovers, KnownAnswerFailure, NonPositiveGap,
                         _REL_SD_PER_ROOT_GAP)
sys.path.insert(0, os.path.join(HERE, "derivflow"))
from track0_harness import rtilde as _instrument_rtilde                   # noqa: E402

bad = []
rng = np.random.default_rng(20260910)

# ---- 1. the closed form ------------------------------------------------------
print("  closed form (2/sqrt(pi))*eta vs direct simulation:")
for eta in (1e-5, 1e-4, 1e-3):
    got, sem = truth_by_simulation(eta, n=20001, reps=120, seed=3)
    want = exact_statistic(eta)
    rel = (got - want) / want
    flag = "" if abs(rel) < 5 * (sem / want) + 2e-3 else "   <-- OFF"
    print(f"    eta={eta:<8.0e} sim {got:.6e} +- {sem:.1e}   exact {want:.6e}"
          f"   {rel:+.3%}{flag}")
    if flag:
        bad.append(f"closed form off by {rel:+.3%} at eta={eta}")

# ---- 2. the sensitivity constant, re-derived --------------------------------
ks = []
for W in (200, 800, 3200, 12800):
    v = np.array([rtilde_distance(perturbed_lattice(W + 1, 1e-4, rng))
                  for _ in range(300)])
    ks.append(float(v.std(ddof=1) / v.mean() * np.sqrt(W)))
k_meas = float(np.mean(ks))
drift = (k_meas - _REL_SD_PER_ROOT_GAP) / _REL_SD_PER_ROOT_GAP
print(f"\n  sensitivity constant: module {_REL_SD_PER_ROOT_GAP:.3f}, "
      f"re-derived {k_meas:.3f} ({drift:+.1%}); per-W {['%.3f' % k for k in ks]}")
if abs(drift) > 0.10:
    bad.append(f"sensitivity constant drifted {drift:+.1%} — "
               f"module says {_REL_SD_PER_ROOT_GAP}, measurement says {k_meas:.3f}")

# ---- 3. RED PATH: the gate must fire, and must not over-fire ----------------
# THE SCIENCE'S OWN CONFIGURATION, not a convenient one. derivflow reads the
# central BULK_FRACTION = 0.20 of n = 4096 (~806 gaps) over a 16-replicate
# ensemble, so that is the sensitivity the gate must be quoted at. A first pass
# here used 800 gaps x 1 rep, which resolves only 16% -- and the checker REFUSED
# to certify, because the smallest bias the audit measured in the real
# instrument is 17%. The gate declining to vouch for itself at an inadequate
# ensemble size is the reachability guard working on the guard.
N_GAPS, REPS, ETA = 806, 16, 1e-4
tol = detectable_bias(N_GAPS, REPS)
print(f"\n  stated resolution at {N_GAPS} gaps x {REPS} rep: {tol:.2%} "
      f"(5 sigma). Audit's measured bias: 17%-271%.")

def read(eta, damping, n_gaps, seed, reps=REPS):
    """A fluctuation-damping bias: smoothing shrinks the gap fluctuation, so the
    statistic reads (1-damping) x truth. This is the shape of the bandwidth
    defect -- NOT a common rescaling, which r-tilde is exactly invariant to."""
    r = np.random.default_rng(seed)
    return float(np.mean([
        rtilde_distance(perturbed_lattice(n_gaps + 1, eta * (1.0 - damping), r))
        for _ in range(reps)]))

clean = read(ETA, 0.0, N_GAPS, 101)
try:
    assert_recovers(clean, ETA, N_GAPS, REPS)
    print(f"    damping  0.0%   read {clean:.4e}   PASSES (correct)")
except KnownAnswerFailure as e:
    bad.append(f"gate refused a CLEAN configuration: {e}")
    print(f"    damping  0.0%   read {clean:.4e}   <-- WRONGLY REFUSED")

fired = {}
for damp in (0.01, 0.02, 0.17, 0.50):
    m = read(ETA, damp, N_GAPS, 202)
    try:
        assert_recovers(m, ETA, N_GAPS, REPS)
        fired[damp] = False
        print(f"    damping {damp:5.1%}   read {m:.4e}   passes")
    except KnownAnswerFailure:
        fired[damp] = True
        print(f"    damping {damp:5.1%}   read {m:.4e}   REFUSED (gate fires)")
if fired.get(0.01):
    bad.append("gate fired on a 1% bias, below its own stated resolution — "
               "it is over-firing and would refuse a sound instrument")
if not fired.get(0.17) or not fired.get(0.50):
    bad.append("gate did NOT fire on a bias the audit measured in the real "
               "instrument (17%/50%) — it is inert where it matters")

# ---- 4. THE BLINDNESS DEMONSTRATION, corrected 2026-09-13 ------------------
# The first version applied `np.arange(N+1) * (1 - damp)` -- a COMMON RESCALING --
# and reported the picket fence "unmoved to 1e-12". That demonstrated nothing:
# r-tilde = min/max is invariant under a common rescaling on ANY configuration,
# ordered or not, so the test could not discriminate the two cases. Its
# "unmoved" was 0/0 float noise on a statistic that is identically zero.
#
# The real mechanism is that an ORDERED configuration has no fluctuation to
# damp. This version shows both halves, and shows the rescaling control failing
# to discriminate, so the distinction cannot be lost again.
def damp_gaps(s_, d):
    """The bias under test: shrink the FLUCTUATION about the mean gap."""
    mu = np.mean(s_)
    return mu + (1.0 - d) * (s_ - mu)

def stat_of_gaps(s_):
    a, b = s_[:-1], s_[1:]
    return float(1.0 - np.mean(np.minimum(a, b) / np.maximum(a, b)))

rng4 = np.random.default_rng(777)
dis = 1.0 + ETA * rng4.standard_normal(N_GAPS)      # disordered
orq = np.ones(N_GAPS)                                # ordered (picket fence)
print("\n  the bias under test is FLUCTUATION DAMPING, not rescaling:")
print(f"    {'damping':>9} {'disordered':>14} {'ordered':>12}")
disc = []
for d in (0.17, 0.50, 0.90):
    sd_ = stat_of_gaps(damp_gaps(dis, d)) / stat_of_gaps(dis) - 1.0
    so_ = stat_of_gaps(damp_gaps(orq, d)) - stat_of_gaps(orq)
    disc.append((sd_, so_))
    print(f"    {d:>8.0%} {sd_:>13.2%} {so_:>12.2e}")
if not all(abs(a) > 0.5 * d for (a, _), d in zip(disc, (0.17, 0.50, 0.90))):
    bad.append("damping did NOT move the disordered statistic — the gate cannot "
               "see the bias class it exists for")
if max(abs(b) for _, b in disc) > 1e-12:
    bad.append("damping DID move the ordered statistic — the blindness claim is "
               "wrong and knownanswer.py's premise needs rewriting")

print("  and a COMMON RESCALING is invisible on BOTH, so it cannot be the reason:")
resc = []
for c in (0.5, 7.0):
    resc.append((abs(stat_of_gaps(dis * c) - stat_of_gaps(dis)),
                 abs(stat_of_gaps(orq * c) - stat_of_gaps(orq))))
    print(f"    x{c:<7} disordered moved {resc[-1][0]:.2e}   "
          f"ordered moved {resc[-1][1]:.2e}")
if max(max(r) for r in resc) > 1e-12:
    bad.append("a common rescaling moved the statistic — r-tilde's scale "
               "invariance does not hold and every bar in the series is affected")
else:
    print("    -> rescaling moves NEITHER. It is scale invariance, which is "
          "configuration-\n       independent, so it cannot explain why ordered "
          "gates are blind.\n       The discriminating fact is that a picket "
          "fence has no fluctuation to damp.")

# ---- 5. THE GATE AND THE INSTRUMENT COMPUTE THE SAME QUANTITY --------------
# Until 2026-09-14 this module filtered `s = s[s > 0]` while
# track0_harness.rtilde filters nothing. Same name, two estimators, and the
# gate was strictly MORE FORGIVING than the instrument it certifies -- so it
# could pass a configuration on which the real statistic is corrupted. The
# filter provably never fired (smallest gap 0.532 over 806,200 gaps spanning
# every eta the series used), so no banked number moved when it was replaced by
# a detector. This row keeps the two definitions welded together.
rng5 = np.random.default_rng(4242)
pos5 = np.concatenate(([0.0], np.cumsum(1.0 + 1e-3 * rng5.standard_normal(4031))))
gate5 = rtilde_distance(pos5)
inst5 = 1.0 - _instrument_rtilde(np.diff(pos5))
print(f"\n  gate vs instrument on identical gaps: {gate5:.17g} vs {inst5:.17g}")
if gate5 != inst5:
    bad.append(f"gate and instrument disagree by {abs(gate5 - inst5):.2e} — the "
               "same quantity has two estimators again")

# ---- 6. THE DETECTOR FIRES, AND THE INSTRUMENT DOES NOT --------------------
bad6 = pos5.copy()
bad6[2000] = bad6[2001] + 0.5            # force one non-monotone point
fired = False
try:
    rtilde_distance(bad6)
except NonPositiveGap:
    fired = True
allowed = rtilde_distance(bad6, "allow")
unguarded = 1.0 - _instrument_rtilde(np.diff(bad6))
print(f"  one non-positive gap in {len(pos5) - 1}: detector "
      f"{'FIRES' if fired else 'SILENT'}; statistic moves {gate5:.5f} -> "
      f"{allowed:.5f} ({allowed / gate5:.1f}x), and the instrument reports "
      f"{unguarded:.5f} without complaint")
if not fired:
    bad.append("the non-positive-gap detector did NOT fire — the silent filter "
               "is back, or the raise path is unreachable")
if allowed != unguarded:
    bad.append("gate('allow') and instrument disagree on a non-monotone input — "
               "the refusal is changing the arithmetic, which it must not")

if bad:
    print("\nVERIFY_KNOWNANSWER: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("\nVERIFY_KNOWNANSWER: PASS — closed form holds, sensitivity re-derived, "
      "the gate fires on the audit's measured bias sizes, and the ordered "
      "configuration is demonstrably blind to them")
