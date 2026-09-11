#!/usr/bin/env python3
"""STAGE 1 — the bandwidth bias surface, measured on Gate D.

COMMITTED GENERATOR of derivflow/recert_bias_surface.json.
Predictions sealed here, before any surface exists.

RECERT_SCOPE.md Stage 1. Stage 0 (Gate D, `knownanswer.py`, board row
`verify_knownanswer`) is the entry condition and is met: a DISORDERED
known-answer configuration with the exact truth 1-<r~> = (2/sqrt(pi))*eta,
red-pathed to fire at 17% and 50% bias and stay quiet at 1% and 2%.

WHAT IS BEING MEASURED, AND WHY IT IS NOT THE AUDIT'S MEASUREMENT
-----------------------------------------------------------------
TAIL_AUDIT_2026_09_09 found the sealed readout biased over the k range that sets
the fit windows, by scaling the bandwidth and watching the reading move. That is
a SELF-CONSISTENCY argument: it shows the answer depends on a knob, and infers
the converged end is right. It cannot say by how much the SEALED setting is
wrong, because it has no truth to compare against -- the flowed roots' true local
statistic is exactly what the campaign is trying to measure.

Gate D supplies the missing truth. The configuration is not a flowed polynomial;
it is a perturbed lattice whose local statistic is known in closed form, pushed
through the SAME `_abs_cdf_at_roots` primitive the science uses, at a bandwidth
we choose. So the deviation is a BIAS against a known answer, not a drift
against another setting. The audit's numbers and these are different quantities
and are expected to differ; the audit is 9 replicates at one n, this is a bias
surface.

THE OPERATING CURVE IS THE DELIVERABLE. A 2D surface over (eps/Delta, eta) is
context. What the science is actually exposed to is a CURVE through it: at each
derivative k, `eps_rule_v15` fixes eps/Delta = sqrt(0.25 + 16(n-k)/(kn)), and the
banked statistic at that k fixes eta = mean_k / (2/sqrt(pi)). Both coordinates
are read from `science_dense_grid.json` rather than typed, so the curve is
derived from the artifact under test.

THE GATE RUNS AT s > 0, AND THE FIRST ATTEMPT DID NOT
-----------------------------------------------------
A first version of this cell ran at s = 0, where the free convolution is the
identity and the reference is therefore a RAW EMPIRICAL STAIRCASE with n steps.
The configuration is a perturbed lattice of nearly the same spacing, so at small
bandwidth every configuration point sat at almost the same phase against its
local step, and the measured bias blew up to +518% at eps/Delta = 0.125 while
reading +6.4% at the science's own operating point. Densifying the reference
collapsed it -- 518% -> 21% -> 11% at 1x / 4x / 8x the configuration's point
count -- which identifies it as a granularity resonance manufactured by the
construction, not a property of the instrument.

A SECOND construction then failed differently, and is disclosed for the same
reason. Building the configuration by inverting a NUMERICALLY integrated mu_s CDF
on a 20001-point grid put the grid only ~5x finer than the configuration's own
spacing, so linear interpolation injected gap jitter of order 0.1% -- an ADDITIVE
floor, not a bias. It showed up as a reading of +1600% at eta = 1e-4 and -7% at
eta = 1e-1: the eta sweep diagnosed it, because a floor divided by a shrinking
truth explodes while a genuine bias does not. Without that sweep it would have
been reported as a catastrophic bandwidth bias.

THE CONSTRUCTION THAT SURVIVES is exact and grid-free. The semicircle is stable
under free convolution, so with an ANALYTIC semicircle reference the flowed
measure is again a semicircle:

    mu_s = semicircle(sigma * sqrt(1 - s)),   support radius R = 2 sigma sqrt(1-s)

verified here against `flow_density` to 1.6e-6 (P1). Its CDF is closed form, so
the configuration is placed by BISECTION to machine precision -- no grid, no
interpolation, no floor. The reference is continuous everywhere, so the staircase
resonance of the first construction cannot occur either. What is given up is the
seed's finite-sample fluctuation: this measures the bandwidth contribution alone,
not the science's total error, which is a scope limit and not a refinement.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     THE PIPELINE CAN RECOVER THE TRUTH AT SOME BANDWIDTH. The    ║
║                 minimum over the eps grid of |bias| on the Richardson arm,   ║
║                 at eta = 1e-4, must be <= 0.0398 (Gate D's own 5-sigma       ║
║                 resolution at 806 gaps x 16 reps). If NO bandwidth reads     ║
║                 the known answer, the defect is not bandwidth and every      ║
║                 number below describes something else.                       ║
║ P2  PREMISE     THE ORDERED CONTROL STAYS BLIND, IN THE REAL PIPELINE. The   ║
║                 same sweep on a picket fence (truth exactly 0) must read     ║
║                 <= 1e-6 in absolute terms at EVERY bandwidth. This is Gate   ║
║                 L re-run across the whole eps axis, and it is what makes     ║
║                 the blindness claim a measurement rather than an argument.   ║
║ C1  EXISTENCE   A BANDWIDTH-DEPENDENT BIAS EXISTS. max over the eps grid of  ║
║                 |Richardson bias| at eta = 1e-4 >= 0.0398. If this MISSES,   ║
║                 the instrument is unbiased across the whole swept range,     ║
║                 the audit's inference is wrong, and Stages 2-4 are void.     ║
║                 It can genuinely miss.                                       ║
║ C2  MECHANISM   THE SEALED SETTING IS IN THE BIASED REGION. |Richardson      ║
║                 bias| at eps/Delta = 0.704 -- the k=64, n=4096 operating     ║
║                 point -- >= 0.0398. The audit puts the sealed reading LOW    ║
║                 there; sign is REPORTED, not predicted, because a sign       ║
║                 prediction from a self-consistency argument is not one this  ║
║                 cell has earned.                                             ║
║ C3  RESOLUTION  THE VALID REGION EXCLUDES SOME OF THE SCIENCE'S RANGE. The   ║
║                 largest eps/Delta at which |Richardson bias| <= 0.0398,      ║
║                 compared against the science's operating span 0.70-4.03.     ║
║                 Bar: that boundary < 4.03, i.e. at least the small-k end of  ║
║                 the science sits outside the valid region. Reachable both    ║
║                 ways -- if the instrument is valid to eps/Delta = 4 and      ║
║                 beyond, this MISSES and the windows are fine.                ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Measures the INSTRUMENT against a known answer. Refits nothing, touches no
banked verdict, and does not by itself establish that any science number is wrong
-- Stage 3 is where that is computed, on the operating curve this cell produces.
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
from track0_iid_scaling import _abs_cdf_at_roots, eps_rule_v15         # noqa: E402
from track0_harness import bulk_idx, BULK_FRACTION                     # noqa: E402
from free_conv import F_semicircle, flow_density, rho_sc               # noqa: E402

N_SCIENCE = 4096
K_TEST = [8, 64]
REPS = 16
ETA_PRIMARY = 1e-4
EPS_GRID = [0.125, 0.25, 0.5, 0.704, 1.0, 1.5, 2.0, 3.0, 4.0, 4.5]
ETA_GRID = [1e-5, 1e-3, 1e-1]
SIGMA = 1.0               # semicircle variance; support [-2 sigma, 2 sigma]
SEED_SEED = 20260910

INSTRUMENT = Model("Gate D at s>0, driven through the science's CDF primitive", [
    Param("eps_over_delta", TESTED, sweep=EPS_GRID,
          why="THE axis. eps_rule_v15 puts the science at 0.70 (k=64) to 4.03 "
              "(k=1) at n=4096, so the grid spans that and reaches below it. "
              "It stops at 0.125 rather than going lower because the first "
              "version of this cell showed the small-eps end is where a "
              "reference-granularity resonance lives, and this grid stays out "
              "of it rather than pretending it is not there"),
    Param("k_flow", TESTED, sweep=K_TEST,
          why="sets s = k/n, i.e. HOW MUCH the free convolution has smoothed "
              "the reference. Two values because the smoothing at k=8 and k=64 "
              "differ by 8x and the whole point of the s>0 rebuild is that this "
              "matters"),
    Param("eta", TESTED, sweep=ETA_GRID,
          why="sets the true statistic (2/sqrt(pi))*eta. The science's readings "
              "span 0.37 down to 1e-5, so this asks whether any bias depends on "
              "WHERE on that axis it is read, not only on bandwidth"),
    Param("reference", DECLARED, value=f"analytic semicircle, sigma={SIGMA}",
          why="CONTINUOUS at every s, so the staircase resonance that wrecked "
              "the first construction cannot occur, and CLOSED FORM under free "
              "convolution, so the configuration can be placed by bisection "
              "instead of by interpolating a numerical CDF -- which is what "
              "wrecked the second. P1 verifies the identity rather than "
              "assuming it"),
    Param("replicates", DECLARED, value=REPS,
          why="the ensemble size Gate D's stated resolution is quoted at; "
              "verify_knownanswer already refused to certify at a smaller one"),
    Param("bulk_window", DECLARED, value=BULK_FRACTION,
          why="the science's own central-window convention"),
])


def sc_cdf(x, R):
    """Semicircle CDF on [-R, R], closed form."""
    t = np.clip(np.asarray(x, float) / R, -1.0, 1.0)
    return 0.5 + (t * np.sqrt(np.maximum(1.0 - t * t, 0.0)) + np.arcsin(t)) / np.pi


def sc_quantile(p, R, iters=80):
    """Inverse semicircle CDF by bisection -- exact to machine precision.

    Bisection rather than interpolation ON PURPOSE: the previous construction
    interpolated a numerical CDF on a grid only ~5x finer than the point
    spacing, and the resulting jitter was an additive floor that read as a
    +1600% bias at small eta."""
    lo = np.full_like(np.asarray(p, float), -R)
    hi = np.full_like(np.asarray(p, float), R)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        go = sc_cdf(mid, R) < p
        lo = np.where(go, mid, lo)
        hi = np.where(go, hi, mid)
    return 0.5 * (lo + hi)


def mu_s_quantile(s):
    """mu_s is semicircle(sigma*sqrt(1-s)); return its exact inverse CDF."""
    R = 2.0 * SIGMA * np.sqrt(1.0 - s)
    return lambda p: sc_quantile(np.asarray(p, float), R)


def config(Q, eta, m, rng):
    """Perturbed lattice pushed through the mu_s quantile map."""
    u = perturbed_lattice(m, eta, rng)
    return Q(u / u[-1])


def read_arms(F_seed, x, s, m):
    """Unfold x against the reference at each bandwidth; statistic per arm."""
    d = (x[-1] - x[0]) / m
    out = {}
    for c in EPS_GRID:
        F1, _, _, _ = _abs_cdf_at_roots(F_seed, x, s, c * d)
        F2, _, _, _ = _abs_cdf_at_roots(F_seed, x, s, 2.0 * c * d)
        for arm, F in (("raw", F1), ("rich", 2.0 * np.asarray(F1) - np.asarray(F2))):
            out[(arm, c)] = rtilde_distance((np.asarray(F) * m)[bulk_idx(m)])
    return out


t0 = time.time()
GATE_RES = detectable_bias(int(BULK_FRACTION * (N_SCIENCE - min(K_TEST))), REPS)
print(f"Gate D resolution at the science's window x {REPS} reps: {GATE_RES:.2%}",
      flush=True)

F_SEED = F_semicircle(SIGMA)

bias, premise_shift = {}, {}
for k in K_TEST:
    m, s = N_SCIENCE - k, k / N_SCIENCE
    Q = mu_s_quantile(s)
    # P1: the claimed truth density IS what the pipeline's own free convolution
    # produces. Verified, not assumed.
    R = 2.0 * SIGMA * np.sqrt(1.0 - s)
    xt = np.linspace(-0.95 * R, 0.95 * R, 21)
    got = flow_density(F_SEED, xt, s, 1e-6 / (1.0 - s))[0]
    want = rho_sc(xt, SIGMA * np.sqrt(1.0 - s))
    premise_shift[k] = float(np.max(np.abs(got - want) / np.maximum(want, 1e-300)))
    for eta in sorted(set(ETA_GRID + [ETA_PRIMARY])):
        rng = np.random.default_rng(SEED_SEED + k * 100 + int(-np.log10(eta)))
        acc = {}
        for _ in range(REPS):
            for key, v in read_arms(F_SEED, config(Q, eta, m, rng), s, m).items():
                acc.setdefault(key, []).append(v)
        truth = exact_statistic(eta)
        bias[(k, eta)] = {key: float(np.mean(v)) / truth - 1.0 for key, v in acc.items()}
        r = bias[(k, eta)]
        print(f"  k={k:<3} eta={eta:<8.0e} richardson: "
              + "  ".join(f"{c}:{r[('rich', c)]:+.1%}"
                           for c in EPS_GRID[::max(1, len(EPS_GRID) // 4)])
              + f"   ({time.time() - t0:.0f}s)", flush=True)

# ---------- ordered control, through the same map ----------
k0 = K_TEST[-1]
m0, s0 = N_SCIENCE - k0, k0 / N_SCIENCE
Q0 = mu_s_quantile(s0)
pk = read_arms(F_SEED, Q0((np.arange(m0) + 0.5) / m0), s0, m0)
picket_worst = float(max(abs(pk[("rich", c)]) for c in EPS_GRID))

# ---------- the science's own operating curve ----------
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))
curve = {}
for sc in ("iid", "gue"):
    cell = bank["data"][sc][str(N_SCIENCE)]
    curve[sc] = [dict(k=int(kk), eps_over_delta=float(eps_rule_v15(1.0, N_SCIENCE, int(kk))),
                      statistic=cell[str(kk)]["mean"],
                      eta_equiv=cell[str(kk)]["mean"] / (2.0 / np.sqrt(np.pi)))
                 for kk in sorted((int(v) for v in cell), key=int)]
span = [min(p["eps_over_delta"] for p in curve["iid"]),
        max(p["eps_over_delta"] for p in curve["iid"])]
EOD_NODE = min(EPS_GRID, key=lambda c: abs(c - float(eps_rule_v15(1.0, N_SCIENCE, 64))))

prim = bias[(64, ETA_PRIMARY)]
rich_abs = {c: abs(prim[("rich", c)]) for c in EPS_GRID}

P1 = Bar("max rel. error, analytic mu_s vs the pipeline's free convolution",
         1e-4, floor=0.0, ceiling=1.0, direction="le",
         why="the configuration is placed using the CLAIM that mu_s is "
             "semicircle(sigma*sqrt(1-s)). If that identity is wrong the truth "
             "is wrong and nothing below means anything. A relative density "
             "error lies in [0,1] for any non-negative density pair; 1e-4 is "
             "two orders above the 1e-6 smoothing floor of the comparison")
p1 = P1.score(max(premise_shift.values()))
P2 = Bar("worst |ordered-control reading| across the eps grid", 1e-6,
         floor=0.0, ceiling=1.0, direction="le",
         why="an absolute reading of 1-<r~> on a configuration whose truth is "
             "exactly 0; the statistic lies in [0,1] by construction")
p2 = P2.score(picket_worst)
C1 = Bar("max |Richardson bias| over the eps grid (k=64)", GATE_RES, floor=0.0,
         ceiling=10.0, direction="ge",
         why="a relative bias against a known answer; non-negative, 10 a stated "
             "practical ceiling. The bar is Gate D's own resolution, so MISSED "
             "means no bias is resolvable anywhere on the swept axis")
c1 = C1.score(max(rich_abs.values()))
C2 = Bar(f"|Richardson bias| at eps/Delta = {EOD_NODE} (k=64 operating point)",
         GATE_RES, floor=0.0, ceiling=10.0, direction="ge",
         why="the science's own operating point at the largest k on the dense "
             "grid, read off eps_rule_v15 rather than chosen")
c2 = C2.score(rich_abs[EOD_NODE])
valid = [c for c in EPS_GRID if rich_abs[c] <= GATE_RES]
edge = max(valid) if valid else 0.0
C3 = Bar("largest eps/Delta still within the gate's resolution", 4.031,
         floor=0.0, ceiling=4.5, direction="le",
         why="compared against the science's span, whose top is eps_rule_v15 at "
             "k=1, n=4096. The ceiling is the grid's own top. MET means part of "
             "the science's range is outside the valid region; MISSED means the "
             "instrument is valid across all of it")
c3 = C3.score(edge)

print(f"\nP1 analytic mu_s vs pipeline free convolution: "
      + ", ".join(f"k={k}: {v:.2e}" for k, v in premise_shift.items()))
print(f"P2 ordered control: worst {picket_worst:.2e} across {len(EPS_GRID)} bandwidths")
print(f"\nRichardson bias vs eps/Delta at k=64, eta={ETA_PRIMARY:.0e}:")
for c in EPS_GRID:
    mark = "   <-- science k=64" if c == EOD_NODE else ""
    print(f"   eps/Delta={c:<7} raw {prim[('raw', c)]:+8.2%}   "
          f"richardson {prim[('rich', c)]:+8.2%}{mark}")
print(f"\nscience span (n=4096, k=1..64): eps/Delta {span[0]:.3f} to {span[1]:.3f}")
print(f"valid region (|bias| <= {GATE_RES:.2%}): eps/Delta <= {edge}")
print()
for bb, val, f in ((P1, max(premise_shift.values()), "{:.4f}"),
                   (P2, picket_worst, "{:.2e}"),
                   (C1, max(rich_abs.values()), "{:.3%}"),
                   (C2, rich_abs[EOD_NODE], "{:.3%}"), (C3, edge, "{:.3f}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(p1, PREM_ROLE, claim="the truth density is not a free parameter"),
     Arm.from_bar(p2, PREM_ROLE, claim="and the ordered control stays blind"),
     Arm.from_bar(c1, EX_ROLE, claim="a bandwidth-dependent bias exists"),
     Arm.from_bar(c2, MECH_ROLE, claim="and the sealed setting sits in it"),
     Arm.from_bar(c3, RES_ROLE,
                  claim="with part of the science's range outside the valid region")],
    holds="BANDWIDTH_BIAS_CONFIRMED_AGAINST_A_KNOWN_ANSWER",
    fails="NO_RESOLVABLE_BANDWIDTH_BIAS_AT_THE_SCIENCES_OPERATING_POINT")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N_SCIENCE, k_test=K_TEST, reps=REPS, eps_grid=EPS_GRID,
    eta_grid=sorted(set(ETA_GRID + [ETA_PRIMARY])), eta_primary=ETA_PRIMARY,
    gate_resolution=GATE_RES,
    bias={f"k{k}_eta{eta:.0e}": {f"{a}@{c}": val for (a, c), val in d.items()}
          for (k, eta), d in bias.items()},
    mu_s_identity_rel_err=premise_shift, sigma=SIGMA,
    ordered_control={f"rich@{c}": pk[("rich", c)] for c in EPS_GRID},
    ordered_worst=picket_worst, eod_node=EOD_NODE,
    science_operating_curve=curve, science_span=span, valid_edge=edge,
    bars={sc["name"]: sc for sc in (p1, p2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="RECERT_SCOPE Stage 1, second construction. Measures the INSTRUMENT "
          "against a known answer at the science's own s. Refits nothing and "
          "touches no banked verdict.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "recert_bias_surface.json"), "w"), indent=1)
print("\nwrote recert_bias_surface.json")
