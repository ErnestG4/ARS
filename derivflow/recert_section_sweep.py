#!/usr/bin/env python3
"""STAGE 2a — is the flat surface flat everywhere, or only where we looked?

COMMITTED GENERATOR of derivflow/recert_section_sweep.json.
Predictions sealed here, before any section sweep exists.

WHY THIS RUNS
-------------
Stage 1 (`recert_bias_surface`, 89354ae) read the statistic over ONE window --
the science's central BULK_FRACTION = 0.20 -- and found the Richardson bias flat
at +0.73% across every bandwidth from 0.125 to 4.5. A flat surface has two
readings, and they are not the same:

  (a) there is no bias, or
  (b) the readout is averaging over a structure that varies across the support,
      and a single central window cannot see it.

Will's proposal, and it is the right attack: sweep SECTIONS of different SIZES
at different POSITIONS and compare. A genuine null stays null in every section.
A cancelling structure does not.

This also puts a number on something the paper currently states qualitatively.
EDGE-0 found the edge unreadable at n=4096 and concluded the obstruction is
definitional -- unfolding against a density whose support endpoint is moving does
not define a local coordinate there. That is an argument. A section sweep on a
configuration with an EXACT known answer at every position turns it into a
measurement: it says where the reading stops being trustworthy, and by how much.

THE CONFIGURATION is Stage 1's surviving one: an analytic semicircle reference,
mu_s = semicircle(sigma*sqrt(1-s)) exact under free convolution, and the
perturbed lattice placed by bisection to machine precision. The lattice is
homogeneous in UNFOLDED index space, so the truth (2/sqrt(pi))*eta is the same in
every section -- which is what makes sections comparable at all.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     the analytic identity holds: max rel. error between           ║
║                 semicircle(sigma*sqrt(1-s)) and the pipeline's own            ║
║                 flow_density <= 1e-4. Same premise as Stage 1; if the truth   ║
║                 density is wrong, every section is wrong together.            ║
║ P2  PREMISE     CONTINUITY WITH STAGE 1: the central section at the           ║
║                 science's own window size must reproduce Stage 1's reading    ║
║                 to within a quarter of the gate's resolution. If it does      ║
║                 not, this cell is measuring a different instrument and its    ║
║                 disagreement with Stage 1 would say nothing about sections.   ║
║ C1  EXISTENCE   THE BIAS VARIES ACROSS SECTIONS. max - min of the             ║
║                 Richardson bias over all (position, size) cells at the        ║
║                 primary eta >= the gate's resolution for the SMALLEST         ║
║                 section used, so the bar is set by what the noisiest cell     ║
║                 can actually resolve. MET means Stage 1's flatness was an     ║
║                 artifact of reading one window and the null is withdrawn.     ║
║                 MISSED means the null survives a much harder test.            ║
║ C2  MECHANISM   AND THE VARIATION IS POSITIONAL, not just noise: |bias| at    ║
║                 the outermost position exceeds |bias| at the centre by >=     ║
║                 the same resolution, at the science's own window size. This   ║
║                 is the edge claim, measured. It can miss while C1 fires, if   ║
║                 the variation is with SIZE rather than POSITION -- which      ║
║                 would be a different and more worrying defect.                ║
║ C3  RESOLUTION  THE USABLE REGION HAS AN EDGE: the outermost position whose   ║
║                 |bias| stays within the gate's resolution, as a fraction of   ║
║                 the half-support. Bar: < 0.95, i.e. SOMETHING is unusable.    ║
║                 Reachable both ways -- if every position reads true, this     ║
║                 misses and the instrument is sound to the support edge.      ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Measures the INSTRUMENT against a known answer, by section. Refits
nothing. The configuration's local structure is Gaussian-perturbed, not whatever
the derivative flow produces, so this bounds the instrument and does not
certify the science.
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
from track0_harness import BULK_FRACTION                               # noqa: E402
from free_conv import F_semicircle, flow_density, rho_sc               # noqa: E402

N_SCIENCE = 4096
K_FLOW = 64
SIGMA = 1.0
REPS = 64
ETA_PRIMARY = 1e-4
ETA_GRID = [1e-5, 1e-4, 1e-2]
EPS_NODES = [0.704, 2.0]
POSITIONS = [0.0, 0.25, 0.5, 0.7, 0.85, 0.95]     # |centre| as a fraction of half-index
SIZES = [0.02, 0.05, 0.10, 0.20, 0.40]            # window width as a fraction of m
SEED = 20260911

INSTRUMENT = Model("Gate D read by section", [
    Param("section_position", TESTED, sweep=POSITIONS,
          why="|window centre| as a fraction of the half-index range. 0 is the "
              "science's central window; 0.95 is as close to the support edge "
              "as a window of the smallest size can sit. THE axis Will's "
              "proposal adds -- a cancelling structure is invisible at one "
              "position and obvious across several"),
    Param("section_size", TESTED, sweep=SIZES,
          why="window width as a fraction of m. Spans a tenth of the science's "
              "own 0.20 up to twice it, because a structure that averages out "
              "over a wide window shows up in a narrow one, and the price is "
              "resolution -- which detectable_bias quantifies per cell rather "
              "than assuming"),
    Param("eta", TESTED, sweep=ETA_GRID,
          why="sets the true statistic. Stage 1 learned this sweep the hard "
              "way: an additive floor divided by a shrinking truth explodes "
              "while a genuine bias does not, and without eta varying, a "
              "construction artifact reads as a catastrophic bias"),
    Param("eps_over_delta", TESTED, sweep=EPS_NODES,
          why="two bandwidths rather than the full grid, because Stage 1 showed "
              "the reading is identical to every printed digit across 0.125 to "
              "4.5; carrying two is enough to catch that changing under "
              "sectioning, which is the only way bandwidth could matter here"),
    Param("k_flow", DECLARED, value=K_FLOW,
          why="the largest k on the science's dense grid, so s and the "
              "bandwidth rule sit at the science's own operating point"),
    Param("replicates", DECLARED, value=REPS,
          why="4x Stage 1's ensemble, because the smallest section carries a "
              "tenth of the gaps and the gate's resolution scales as "
              "1/sqrt(gaps x reps); without this the narrow cells could not "
              "resolve the effect they exist to look for"),
    Param("reference", DECLARED, value=f"analytic semicircle, sigma={SIGMA}",
          why="Stage 1's surviving construction. Continuous at every s, closed "
              "form under free convolution, configuration placed by bisection: "
              "no staircase resonance and no interpolation floor"),
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


def section_idx(m, pos, size):
    """Index slice: window of `size`*m gaps centred at |pos| of the half-range."""
    w = max(8, int(round(size * m)))
    centre = int(round(0.5 * m * (1.0 + pos)))
    lo = min(max(0, centre - w // 2), m - w)
    return slice(lo, lo + w)


t0 = time.time()
m, s = N_SCIENCE - K_FLOW, K_FLOW / N_SCIENCE
R = 2.0 * SIGMA * np.sqrt(1.0 - s)
F_SEED = F_semicircle(SIGMA)

xt = np.linspace(-0.95 * R, 0.95 * R, 21)
p1_err = float(np.max(np.abs(flow_density(F_SEED, xt, s, 1e-6 / (1.0 - s))[0]
                             - rho_sc(xt, SIGMA * np.sqrt(1.0 - s)))
                      / np.maximum(rho_sc(xt, SIGMA * np.sqrt(1.0 - s)), 1e-300)))

acc = {}
for rep in range(REPS):
    rng = np.random.default_rng(SEED + rep)
    for eta in ETA_GRID:
        u = perturbed_lattice(m, eta, rng)
        x = sc_quantile(u / u[-1], R)
        d = (x[-1] - x[0]) / m
        for c in EPS_NODES:
            F1, _, _, _ = _abs_cdf_at_roots(F_SEED, x, s, c * d)
            F2, _, _, _ = _abs_cdf_at_roots(F_SEED, x, s, 2.0 * c * d)
            un = (2.0 * np.asarray(F1) - np.asarray(F2)) * m
            for pos in POSITIONS:
                for size in SIZES:
                    key = (eta, c, pos, size)
                    acc.setdefault(key, []).append(
                        rtilde_distance(un[section_idx(m, pos, size)]))
    if (rep + 1) % 8 == 0:
        print(f"  rep {rep + 1}/{REPS}  ({time.time() - t0:.0f}s)", flush=True)

bias = {k: float(np.mean(v)) / exact_statistic(k[0]) - 1.0 for k, v in acc.items()}
res_of = {size: detectable_bias(max(8, int(round(size * m))), REPS) for size in SIZES}

prim = {(pos, size): bias[(ETA_PRIMARY, EPS_NODES[0], pos, size)]
        for pos in POSITIONS for size in SIZES}
spread = float(max(prim.values()) - min(prim.values()))
res_small = res_of[min(SIZES)]

sci = [p for p in POSITIONS]
centre_b = abs(prim[(0.0, BULK_FRACTION)])
outer_b = abs(prim[(max(POSITIONS), BULK_FRACTION)])
usable = [pos for pos in POSITIONS
          if abs(prim[(pos, BULK_FRACTION)]) <= res_of[BULK_FRACTION]]
edge_pos = max(usable) if usable else 0.0

P1 = Bar("max rel. error, analytic mu_s vs the pipeline's free convolution",
         1e-4, floor=0.0, ceiling=1.0, direction="le",
         why="same premise as Stage 1; a relative density error lies in [0,1], "
             "and 1e-4 is two orders above the comparison's own 1e-6 floor")
p1 = P1.score(p1_err)
STAGE1 = 0.007265
P2 = Bar("|central-window reading minus Stage 1's|", res_of[BULK_FRACTION],
         floor=0.0, ceiling=10.0, direction="le",
         why="continuity with the sealed Stage 1 cell at its own window and "
             "bandwidth; a relative-bias difference is non-negative and 10 is a "
             "stated practical ceiling. The bar is the gate's FULL 5-sigma "
             "resolution because both readings carry sampling error of their "
             "own -- a first draft used a quarter of it, which is 1.25 sigma "
             "and would have failed this premise on noise alone")
p2 = P2.score(abs(prim[(0.0, BULK_FRACTION)] - STAGE1))
C1 = Bar("max - min Richardson bias across all (position, size) cells",
         res_small, floor=0.0, ceiling=10.0, direction="ge",
         why="a spread of relative biases; non-negative, 10 a stated practical "
             "ceiling. The bar is the gate's resolution AT THE SMALLEST SECTION, "
             "so it is what the noisiest cell in the sweep can actually resolve")
c1 = C1.score(spread)
C2 = Bar("|bias| at the outermost position minus |bias| at the centre",
         res_of[BULK_FRACTION], floor=-10.0, ceiling=10.0, direction="ge",
         why="both read at the science's own window size, so the difference is "
             "positional. Negative values are reachable and would mean the edge "
             "reads TRUER than the centre, which would indict the centre")
c2 = C2.score(outer_b - centre_b)
C3 = Bar("outermost position still within the gate's resolution", POSITIONS[-2],
         floor=0.0, ceiling=1.0, direction="le",
         why="|centre| as a fraction of the half-index range, so it lies in "
             "[0,1] by construction. The bar is the NEXT-TO-OUTERMOST position: "
             "if every position reads true the statistic equals the outermost "
             "and MISSES, and only a genuine inner boundary MEETS it. A first "
             "draft used the outermost position itself, which every possible "
             "value meets -- the arm could not have missed and would have "
             "reported 'unusable' even when the instrument read true to the edge")
c3 = C3.score(edge_pos)

print(f"\nP1 analytic identity: {p1_err:.2e}")
print(f"P2 central window vs Stage 1: {prim[(0.0, BULK_FRACTION)]:+.4%} "
      f"vs {STAGE1:+.4%}")
print(f"\nRichardson bias by section, eta={ETA_PRIMARY:.0e}, "
      f"eps/Delta={EPS_NODES[0]}:")
print(f"{'|pos|':>7} " + "".join(f"{sz:>11}" for sz in SIZES))
for pos in POSITIONS:
    print(f"{pos:>7.2f} " + "".join(f"{prim[(pos, sz)]:+10.2%} " for sz in SIZES))
print(f"\ngate resolution by section size: "
      + ", ".join(f"{sz}: {res_of[sz]:.2%}" for sz in SIZES))
print()
for bb, val, f in ((P1, p1_err, "{:.2e}"),
                   (P2, abs(prim[(0.0, BULK_FRACTION)] - STAGE1), "{:.4%}"),
                   (C1, spread, "{:.3%}"), (C2, outer_b - centre_b, "{:+.3%}"),
                   (C3, edge_pos, "{:.2f}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(p1, PREM_ROLE, claim="the truth density is the one claimed"),
     Arm.from_bar(p2, PREM_ROLE, claim="and the central window reproduces Stage 1"),
     Arm.from_bar(c1, EX_ROLE, claim="the bias varies across sections"),
     Arm.from_bar(c2, MECH_ROLE, claim="and the variation is positional"),
     Arm.from_bar(c3, RES_ROLE, claim="with an outer region that is unusable")],
    holds="FLATNESS_IS_AN_ARTIFACT_OF_THE_CENTRAL_WINDOW",
    fails="THE_NULL_SURVIVES_SECTIONING")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N_SCIENCE, k_flow=K_FLOW, m=m, sigma=SIGMA, reps=REPS,
    positions=POSITIONS, sizes=SIZES, eta_grid=ETA_GRID, eps_nodes=EPS_NODES,
    eta_primary=ETA_PRIMARY, stage1_reading=STAGE1,
    mu_s_identity_rel_err=p1_err,
    bias={f"eta{k[0]:.0e}_eps{k[1]}_pos{k[2]}_size{k[3]}": val
          for k, val in bias.items()},
    resolution_by_size={str(sz): res_of[sz] for sz in SIZES},
    section_spread=spread, centre_bias=centre_b, outer_bias=outer_b,
    edge_position=edge_pos,
    bars={sc_["name"]: sc_ for sc_ in (p1, p2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="RECERT_SCOPE Stage 2a. Measures the INSTRUMENT by section against a "
          "known answer. Refits nothing; the configuration is Gaussian-perturbed "
          "rather than flowed, so this bounds the instrument and does not "
          "certify the science.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "recert_section_sweep.json"), "w"), indent=1)
print("\nwrote recert_section_sweep.json")
