#!/usr/bin/env python3
"""STAGE 2b — is the REFERENCE the defect the bandwidth was not?

COMMITTED GENERATOR of derivflow/recert_finite_seed.json.
Predictions sealed here, before any finite-seed reading exists.

WHY THIS RUNS
-------------
Stage 1 (89354ae) measured the bandwidth against a known answer and found the
Richardson bias flat at +0.73% across eps/Delta = 0.125 to 4.5 -- identical to
every printed digit, with the raw and Richardson arms agreeing exactly. So the
bandwidth is not where the audit's 17%-271% comes from.

But Stage 1 bought that cleanliness with a choice it disclosed: the reference was
an ANALYTIC semicircle. The science's reference is `F_empirical` of a FINITE
random seed, free-convolved. That difference was excluded by construction, and it
is now the leading remaining candidate -- a mismatch between the flowed roots'
true density and the free convolution of finitely many seed points is a
REFERENCE-ACCURACY defect, which is a different defect with a different fix than
a smoothing one.

THE DESIGN keeps the truth exact and changes only the reference. The
configuration is still placed by bisection on the analytic mu_s =
semicircle(sigma*sqrt(1-s)), so 1-<r~> = (2/sqrt(pi))*eta remains exact. It is
then unfolded against F_empirical of n_seed draws from the SAME semicircle. Any
deviation is the price of a finite reference, measured against a known answer --
which is exactly what the audit could not do, because it had only one setting to
compare against another.

THE BANDWIDTH ARM IS THE POINT. Stage 1 found no bandwidth dependence with a
perfect reference. If a finite reference INTRODUCES one, then the audit's
observation (the reading moves when you scale the bandwidth) is real, its
mechanism is the reference rather than the smoothing, and the two findings stop
contradicting each other. C3 tests exactly that.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     the analytic identity holds: max rel. error between           ║
║                 semicircle(sigma*sqrt(1-s)) and the pipeline's own            ║
║                 flow_density <= 1e-4. The truth density must be the one       ║
║                 claimed or nothing below is a bias.                          ║
║ P2  PREMISE     THE LIMIT IS RIGHT. At the largest n_seed the bias must come  ║
║                 within 1.5x the gate's resolution of Stage 1's +0.73%. A      ║
║                 finite reference must approach the analytic one; if it does   ║
║                 not, the two cells are measuring different things and the     ║
║                 comparison below is void.                                     ║
║ C1  EXISTENCE   A FINITE SEED AT THE SCIENCE'S OWN n COSTS SOMETHING          ║
║                 RESOLVABLE: |bias| at n_seed = 4096 >= the gate's             ║
║                 resolution. MISSED means the reference is innocent too, and   ║
║                 the audit's effect has no candidate left in this family --    ║
║                 which would be a real and reportable dead end.                ║
║ C2  MECHANISM   IT SCALES LIKE A SAMPLING ERROR: the fitted exponent of       ║
║                 |bias| against n_seed lies at or below -0.25, i.e. it decays. ║
║                 A finite-sample defect must shrink with n; something that     ║
║                 does not is a bug, not a sampling cost. Reachable both ways.  ║
║ C3  RESOLUTION  AND IT IS BANDWIDTH-DEPENDENT, which Stage 1's was not:       ║
║                 max - min |bias| across the bandwidth nodes at n_seed = 4096  ║
║                 >= the gate's resolution. MET reconciles this cell with the   ║
║                 audit and names the reference as the mechanism. MISSED means  ║
║                 the finite seed costs a constant offset that no bandwidth     ║
║                 choice can trade against, which would NOT explain the audit.  ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Measures the INSTRUMENT against a known answer with the science's own
style of reference. Refits nothing, touches no banked verdict. The configuration
is Gaussian-perturbed rather than flowed, so this bounds the reference's cost and
does not certify the science.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from knownanswer import (exact_statistic, perturbed_lattice, rtilde_distance,  # noqa: E402
                         detectable_bias)
from reachable import Bar                                              # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,        # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED                 # noqa: E402
from track0_iid_scaling import _abs_cdf_at_roots                       # noqa: E402
from track0_harness import bulk_idx, BULK_FRACTION                     # noqa: E402
from free_conv import F_semicircle, F_empirical, flow_density, rho_sc  # noqa: E402

N_SCIENCE = 4096
K_FLOW = 64
SIGMA = 1.0
SEEDS_N = [512, 1024, 2048, 4096, 8192]
N_SEED_REAL = 6
REPS = 6
ETA_GRID = [1e-5, 1e-4, 1e-2]
ETA_PRIMARY = 1e-4
EPS_NODES = [0.25, 0.704, 1.5, 4.0]
SEED = 20260911
STAGE1 = 0.007265
# The swept seed size that matches the science's own n, DERIVED rather than
# typed. A first draft hardcoded 4096 and crashed the moment the sweep did not
# contain it -- the same fragility as the hardcoded grid indices in Stage 1.
N_REF = min(SEEDS_N, key=lambda v: abs(v - N_SCIENCE))

INSTRUMENT = Model("Gate D against a FINITE empirical reference", [
    Param("n_seed", TESTED, sweep=SEEDS_N,
          why="THE axis. The science's reference is F_empirical of exactly "
              "n=4096 seed points; this brackets that by 8x either way so the "
              "cost can be seen to SCALE rather than just to exist at one size"),
    Param("eps_over_delta", TESTED, sweep=EPS_NODES,
          why="Stage 1 found the reading identical at every bandwidth with a "
              "PERFECT reference. Whether a finite reference introduces "
              "bandwidth dependence is this cell's whole reconciliation with "
              "the audit, so the bandwidth must be swept, not fixed"),
    Param("eta", TESTED, sweep=ETA_GRID,
          why="sets the true statistic. Stage 1 learned this the hard way: an "
              "additive floor over a shrinking truth explodes while a bias does "
              "not, and a finite reference is a candidate source of exactly "
              "such a floor"),
    Param("seed_realisations", DECLARED, value=N_SEED_REAL,
          why="the reference is now RANDOM, so a single draw would confound the "
              "reference's systematic cost with one realisation's luck. "
              "Averaged over draws; the spread is reported"),
    Param("k_flow", DECLARED, value=K_FLOW,
          why="the largest k on the science's dense grid, matching Stage 1"),
    Param("replicates", DECLARED, value=REPS,
          why="configurations per (seed, eta); with 8 seed draws this is 64 "
              "readings per cell, the ensemble Gate D's resolution is quoted at"),
    Param("configuration", DECLARED, value="analytic semicircle placement",
          why="the TRUTH is held exact while only the reference changes. That "
              "isolation is the cell's design: a deviation here cannot be the "
              "configuration's fault because the configuration is unchanged "
              "from Stage 1"),
])


def sc_cdf(x, R):
    t = np.clip(np.asarray(x, float) / R, -1.0, 1.0)
    return 0.5 + (t * np.sqrt(np.maximum(1.0 - t * t, 0.0)) + np.arcsin(t)) / np.pi


def sc_quantile(p, R, iters=80):
    lo = np.full_like(np.asarray(p, float), -R)
    hi = np.full_like(np.asarray(p, float), R)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        go = sc_cdf(mid, R) < p
        lo = np.where(go, mid, lo)
        hi = np.where(go, hi, mid)
    return 0.5 * (lo + hi)


def sc_sample(ns, rng, sig):
    """ns draws from semicircle(sig) by exact quantile transform."""
    return np.sort(sc_quantile(rng.random(ns), 2.0 * sig))


t0 = time.time()
m, s = N_SCIENCE - K_FLOW, K_FLOW / N_SCIENCE
R = 2.0 * SIGMA * np.sqrt(1.0 - s)
SIG_S = SIGMA * np.sqrt(1.0 - s)

xt = np.linspace(-0.95 * R, 0.95 * R, 21)
p1_err = float(np.max(np.abs(flow_density(F_semicircle(SIGMA), xt, s,
                                          1e-6 / (1.0 - s))[0]
                             - rho_sc(xt, SIG_S)) / np.maximum(rho_sc(xt, SIG_S), 1e-300)))
print(f"P1 analytic identity: {p1_err:.2e}", flush=True)

GATE_RES = detectable_bias(int(BULK_FRACTION * m), REPS * N_SEED_REAL)
print(f"gate resolution at {int(BULK_FRACTION * m)} gaps x "
      f"{REPS * N_SEED_REAL} readings: {GATE_RES:.2%}", flush=True)

acc = {}
for ns in SEEDS_N:
    for si in range(N_SEED_REAL):
        rs = np.random.default_rng(SEED + 7919 * si + ns)
        F_ref = F_empirical(sc_sample(ns, rs, SIGMA))
        for eta in ETA_GRID:
            for rep in range(REPS):
                rng = np.random.default_rng(SEED + 104729 * rep + si)
                u = perturbed_lattice(m, eta, rng)
                x = sc_quantile(u / u[-1], R)
                d = (x[-1] - x[0]) / m
                for c in EPS_NODES:
                    F1, _, _, _ = _abs_cdf_at_roots(F_ref, x, s, c * d)
                    F2, _, _, _ = _abs_cdf_at_roots(F_ref, x, s, 2.0 * c * d)
                    un = (2.0 * np.asarray(F1) - np.asarray(F2)) * m
                    acc.setdefault((ns, eta, c), []).append(
                        rtilde_distance(un[bulk_idx(m)]))
    print(f"  n_seed={ns} done ({time.time() - t0:.0f}s)", flush=True)

bias = {k: float(np.mean(v)) / exact_statistic(k[1]) - 1.0 for k, v in acc.items()}
sd = {k: float(np.std(v, ddof=1) / np.sqrt(len(v)) / exact_statistic(k[1]))
      for k, v in acc.items()}

at_ref = {c: bias[(N_REF, ETA_PRIMARY, c)] for c in EPS_NODES}
band_spread = float(max(abs(v) for v in at_ref.values())
                    - min(abs(v) for v in at_ref.values()))
by_n = {ns: abs(bias[(ns, ETA_PRIMARY, EPS_NODES[1])]) for ns in SEEDS_N}
expo = float(np.polyfit(np.log([float(n) for n in SEEDS_N]),
                        np.log([max(by_n[n], 1e-12) for n in SEEDS_N]), 1)[0])
limit_gap = abs(by_n[max(SEEDS_N)] - STAGE1)

P1 = Bar("max rel. error, analytic mu_s vs the pipeline's free convolution",
         1e-4, floor=0.0, ceiling=1.0, direction="le",
         why="same premise as Stages 1 and 2a; a relative density error lies in "
             "[0,1] and 1e-4 is two orders above the comparison's 1e-6 floor")
p1 = P1.score(p1_err)
P2 = Bar("|bias at the largest n_seed minus Stage 1's analytic reading|",
         1.5 * GATE_RES, floor=0.0, ceiling=10.0, direction="le",
         why="a finite reference must approach the analytic one as n_seed "
             "grows; a relative-bias difference is non-negative and 10 is a "
             "stated practical ceiling. 1.5x the resolution allows for the "
             "largest seed still being finite")
p2 = P2.score(limit_gap)
C1 = Bar(f"|bias| at n_seed = {N_REF}, the science's own seed size", GATE_RES,
         floor=0.0, ceiling=10.0, direction="ge",
         why="a relative bias against a known answer; the bar is the gate's own "
             "resolution at this ensemble, so MISSED means the finite reference "
             "costs nothing this instrument can see")
c1 = C1.score(abs(bias[(N_REF, ETA_PRIMARY, EPS_NODES[1])]))
C2 = Bar("fitted exponent of |bias| against n_seed", -0.25,
         floor=-3.0, ceiling=3.0, direction="le",
         why="d log|bias| / d log n_seed. A sampling cost must DECAY, so the "
             "bar is negative; +3 and -3 bracket anything a finite-sample term "
             "can plausibly do, and a positive exponent (growing with n) would "
             "indicate a bug rather than a sampling cost")
c2 = C2.score(expo)
C3 = Bar(f"bandwidth spread of |bias| at n_seed = {N_REF}", GATE_RES,
         floor=0.0, ceiling=10.0, direction="ge",
         why="max minus min |bias| across the bandwidth nodes; non-negative, 10 "
             "a stated practical ceiling. Stage 1 measured this as zero to "
             "every printed digit with a perfect reference, so any resolvable "
             "value here is introduced BY the finite reference")
c3 = C3.score(band_spread)

print(f"\n|bias| vs n_seed at eta={ETA_PRIMARY:.0e}, eps/Delta={EPS_NODES[1]}:")
for ns in SEEDS_N:
    print(f"   n_seed={ns:<6} {bias[(ns, ETA_PRIMARY, EPS_NODES[1])]:+8.2%} "
          f"+- {sd[(ns, ETA_PRIMARY, EPS_NODES[1])]:.2%}")
print(f"   fitted exponent {expo:+.3f}   (Stage 1 analytic reference: {STAGE1:+.2%})")
print(f"\nbandwidth dependence at n_seed={N_REF}, eta={ETA_PRIMARY:.0e}:")
for c in EPS_NODES:
    print(f"   eps/Delta={c:<7} {at_ref[c]:+8.2%}")
print()
for bb, val, f in ((P1, p1_err, "{:.2e}"), (P2, limit_gap, "{:.3%}"),
                   (C1, abs(bias[(N_REF, ETA_PRIMARY, EPS_NODES[1])]), "{:.3%}"),
                   (C2, expo, "{:+.3f}"), (C3, band_spread, "{:.3%}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(p1, PREM_ROLE, claim="the truth density is the one claimed"),
     Arm.from_bar(p2, PREM_ROLE, claim="and the finite reference converges to it"),
     Arm.from_bar(c1, EX_ROLE, claim="a finite reference costs something resolvable"),
     Arm.from_bar(c2, MECH_ROLE, claim="and it decays with seed size like a sampling term"),
     Arm.from_bar(c3, RES_ROLE, claim="and it is bandwidth-dependent, which Stage 1's was not")],
    holds="THE_FINITE_REFERENCE_CARRIES_THE_COST",
    fails="THE_FINITE_REFERENCE_IS_INNOCENT_TOO")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N_SCIENCE, k_flow=K_FLOW, m=m, sigma=SIGMA, seeds_n=SEEDS_N,
    seed_realisations=N_SEED_REAL, reps=REPS, eta_grid=ETA_GRID,
    eta_primary=ETA_PRIMARY, eps_nodes=EPS_NODES, stage1_reading=STAGE1,
    gate_resolution=GATE_RES, mu_s_identity_rel_err=p1_err,
    bias={f"n{k[0]}_eta{k[1]:.0e}_eps{k[2]}": val for k, val in bias.items()},
    sem={f"n{k[0]}_eta{k[1]:.0e}_eps{k[2]}": val for k, val in sd.items()},
    fitted_exponent=expo, n_ref=N_REF, bandwidth_spread_at_ref=band_spread,
    limit_gap=limit_gap,
    bars={sc_["name"]: sc_ for sc_ in (p1, p2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="RECERT_SCOPE Stage 2b. Holds the TRUTH exact and changes only the "
          "REFERENCE to the science's own finite-empirical style. Refits "
          "nothing; the configuration is Gaussian-perturbed rather than flowed.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "recert_finite_seed.json"), "w"), indent=1)
print("\nwrote recert_finite_seed.json")
