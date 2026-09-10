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
                         assert_recovers, KnownAnswerFailure,
                         _REL_SD_PER_ROOT_GAP)

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

# ---- 4. THE BLINDNESS DEMONSTRATION -----------------------------------------
print("\n  why Gates L and H could not object — same bias, ORDERED configuration:")
picket = np.arange(N_GAPS + 1, dtype=float)
base = rtilde_distance(picket)
moved = []
for damp in (0.17, 0.50, 0.90):
    # damping a fluctuation that is identically zero changes nothing
    p = np.arange(N_GAPS + 1, dtype=float) * (1.0 - damp)   # common rescaling too
    v = rtilde_distance(p)
    moved.append(abs(v - base))
    print(f"    damping {damp:5.1%}   picket reads {v:.3e}  "
          f"(moved {abs(v - base):.1e})")
if max(moved) > 1e-12:
    bad.append("the ordered configuration DID move — the blindness argument is "
               "wrong and this module's premise needs rewriting")
else:
    print("    -> unmoved to 1e-12. A gap-RATIO statistic is invariant under a "
          "common\n       rescaling, and an ordered configuration has no "
          "fluctuation to damp.\n       Gate D reads the same bias at "
          f"{abs((read(ETA, 0.17, N_GAPS, 303) - exact_statistic(ETA)) / exact_statistic(ETA)):.0%}.")

if bad:
    print("\nVERIFY_KNOWNANSWER: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("\nVERIFY_KNOWNANSWER: PASS — closed form holds, sensitivity re-derived, "
      "the gate fires on the audit's measured bias sizes, and the ordered "
      "configuration is demonstrably blind to them")
