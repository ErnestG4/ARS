"""CRITERION SCOPE v2: same seal, corrected premise, input pinned by hash.

COMMITTED GENERATOR of cross_substrate/brocot_criterion_scope_v2.json.

v1 (brocot_criterion_scope.py) composed INVALID because its premise arm R2
compared against brocot_filter_worth_it.json, whose declared input -- the
16mix landscape graph in the SIBLING repo -- was regenerated on 2026-08-31,
five days after those rates were banked. That was a discovery, not a defect:
the committed generator re-run unmodified on the current graph agrees with
v1's pipeline at 0 of 12 rates mismatched, and that re-run is banked with the
graph pinned by sha256 as brocot_filter_worth_it_regraph.json.

v2 changes EXACTLY TWO THINGS and inherits everything else verbatim from
v1's seal (which predates any output):
  1. R2 compares against the regraph artifact -- committed generator on the
     input AS IT EXISTS -- and the input is verified against its pinned
     sha256 at run time, failing closed on any further drift.
  2. The output filename.
DISCLOSURE: v2 is sealed after v1's numbers were seen. Bars C1-C5 are
therefore inherited predictions, not fresh ones; their sealing credit
belongs to v1's commit (1f3159b), where they were written before any output
existed. R2's bar is the only arm whose comparison target changed, and its
target is pinned so the failure mode it caught cannot silently recur.

The claims and their regions are v1's docstring's; read it first.
"""
import hashlib
import gzip
import json
import os
import sys
from fractions import Fraction
from math import ceil, gcd, log2

import numpy as np
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
sys.path.insert(0, BROCOT)
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,   # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from existence import summarise, EXISTENCE as EX_Q                # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402

I_LIST = [0.9, 1.5, 2.0, 3.0]
MARGINS = [-6.0, 0.0, 6.0]
SIGMAS = [1.0, 0.7, 0.5, 0.4, 0.25]        # decreasing; 0.7 is the new interior point
F_C = 220.0
LO, HI = Fraction(7, 10), Fraction(7, 5)
GRAPH = f"{BROCOT}/resources/landscape_graph_16mix.json.gz"
GRAPH_SHA256 = "1b6c755f4174ca38dfe8411f5c03b52df4eac7d9229cd9873fb86f26feeaa30c"
_h = hashlib.sha256(open(GRAPH, "rb").read()).hexdigest()
if _h != GRAPH_SHA256:
    raise SystemExit(f"INPUT DRIFT: {GRAPH} sha256 {_h[:16]}... != pinned "
                     f"{GRAPH_SHA256[:16]}... -- the graph moved again. Re-pin "
                     "DELIBERATELY (new regraph artifact) or check out the "
                     "pinned state; do not run against an unpinned input.")
SEED, N_NODES = 20260826, 220              # filter_worth_it's, unchanged: same sample
CENTS_TOL, MAX_ORDER, MIN_IDX = 12.0, 24, 0.02
MAXEXTRA, TOPN = 3, 4
SHIP_BAR = 0.10                            # filter_worth_it's F2 threshold, reused

INSTRUMENT = Model("relative masking, Glasberg-Moore ERB, criterion-plane sweep", [
    Param("margin_db", TESTED, sweep=MARGINS,
          why="signal-to-masker ratio inside one auditory filter"),
    Param("sigma_scale", TESTED, sweep=SIGMAS,
          why="ERB is an equivalent RECTANGULAR bandwidth; the sigma axis is "
              "the criterion the framing death made first-class. 0.7 added so "
              "the ship-bar crossing lands in an interval, not a chasm"),
    Param("f_c", DECLARED, value=F_C,
          why="criterion is a ratio of amplitudes; invariant in f_c up to the "
              "ERB width's mild frequency dependence"),
    Param("both_witnesses_required", DECLARED, value=True,
          why="a coincidence is two partials landing together"),
    Param("masker_scope_part2", DECLARED, value="the fusing PAIR's own 2-op lattice",
          why="inherited from filter_worth_it verbatim; omitting other "
              "operators REMOVES maskers, overstating audibility -- "
              "conservative for the filter question"),
    Param("graph_and_seed", DECLARED,
          value=f"16mix graph sha256 {GRAPH_SHA256[:16]}..., seed {SEED}, {N_NODES} nodes",
          why="the SAME sample as filter_worth_it so R2 is exact replication, "
              "not a fresh draw"),
])

# ---------- Part 1 machinery: masked_horizon, verbatim ----------
def erb_w(f):
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def lattice(alpha, I, B):
    out = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            a = float(jv(n1, I)) * float(jv(n2, I))
            if a == 0.0:
                continue
            nu = 1.0 + n1 + n2 * float(alpha)
            f = abs(nu) * F_C
            if f < 20.0 or f > 16000.0:
                continue
            out[round(f, 6)] = out.get(round(f, 6), 0.0) + abs(a)
    return np.array(sorted(out)), np.array([out[k] for k in sorted(out)])


def audible(fk, ak, f, a, margin_db, width_scale=1.0):
    other = f != fk
    if not other.any():
        return True
    e = np.sqrt(np.sum((a[other] ** 2)
                       * np.exp(-0.5 * ((fk - f[other])
                                        / (erb_w(f[other]) * width_scale)) ** 2)))
    if e <= 0:
        return True
    return 20.0 * np.log10(ak / e) > margin_db


def witness_audible(alpha, I, B, margin_db, width_scale=1.0, _lc={}):
    p, q = alpha.numerator, alpha.denominator
    n1, n1p = -(-p // 2), -(p // 2)
    n2, n2p = -(q // 2), -(-q // 2)
    if max(abs(n1), abs(n1p)) > B or max(abs(n2), abs(n2p)) > B:
        return None
    key = (alpha, I)
    if key not in _lc:
        _lc[key] = lattice(alpha, I, B)
    f, a = _lc[key]
    ok = True
    for (x, y) in ((n1, n2), (n1p, n2p)):
        amp = abs(float(jv(x, I)) * float(jv(y, I)))
        nu = abs(1.0 + x + y * float(alpha)) * F_C
        idx = np.argmin(np.abs(f - nu))
        if not audible(f[idx], amp, f, a, margin_db, width_scale):
            ok = False
    return ok


def below_horizon(I):
    B = order_bound(I)
    A = 2 * B
    return B, sorted({Fraction(p, q) for q in range(1, A + 1)
                      for p in range(1, A + 1)
                      if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
                      and max(p, q) <= A}, key=float)


# ---------- Part 1: the count grid ----------
grid = {}          # (I, margin, sigma) -> dict(total, nondeg, audible=[...])
for I in I_LIST:
    B, ratios = below_horizon(I)
    for m in MARGINS:
        for s in SIGMAS:
            aud = [f for f in ratios if witness_audible(f, I, B, m, s)]
            grid[(I, m, s)] = dict(
                total=len(aud),
                nondeg=sum(1 for f in aud if f != 1),
                audible=[str(f) for f in aud])

# R1: reproduce the 28 banked masked_horizon numbers.
banked = json.load(open(os.path.join(HERE, "brocot_masked_horizon.json")))
mismatch = 0
for lab, s in (("ERB", 1.0), ("ERB/2", 0.5), ("ERB/2.5", 0.4), ("ERB/4", 0.25)):
    for I in I_LIST:
        if grid[(I, 0.0, s)]["total"] != banked["width_sensitivity"][lab][str(I)]:
            mismatch += 1
for I in I_LIST:
    for m in MARGINS:
        if grid[(I, m, 1.0)]["total"] != banked["per_I"][str(I)]["counts"][str(m)]:
            mismatch += 1
R1 = Bar("Part-1 mismatches vs 28 banked masked_horizon counts", 0.5,
         direction="le", floor=0, ceiling=28,
         why="a count of disagreements with the committed artifact, 0 to 28")
r1 = R1.score(mismatch)

# C1: the corrected headline across the sigma >= 0.4 subplane at I = 0.9.
wide_cells = [(m, s) for m in MARGINS for s in SIGMAS if s >= 0.4]
c1_fail = sum(1 for (m, s) in wide_cells if grid[(0.9, m, s)]["nondeg"] > 0)
C1 = Bar("cells with sigma >= 0.4 where a non-degenerate ratio is audible (I=0.9)",
         0.5, direction="le", floor=0, ceiling=len(wide_cells),
         why=f"a count over the {len(wide_cells)} wide-filter cells")
c1 = C1.score(c1_fail)

# C2: the region's edge — existence question, existence statistic.
edge_counts = [grid[(0.9, m, 0.25)]["nondeg"] for m in MARGINS]
edge = summarise("nondegenerate audible at sigma=0.25, I=0.9 (per margin)",
                 edge_counts, EX_Q)
C2 = Bar("margin cells at sigma = 0.25 with a non-degenerate audible ratio",
         0.5, floor=0, ceiling=len(MARGINS),
         why="a count over the 3 margin cells; >= 1 means the headline's "
             "region has an edge inside the swept plane")
c2 = C2.score(edge["n_nonzero"])

# ---------- Part 2 machinery: filter_worth_it, verbatim + pair-lattice cache ----------
_pc = {}


def walk(path):
    if path in _pc:
        return _pc[path]
    ln, ld, hn, hd = 0, 1, 1, 0
    for c in path:
        mn, md = ln + hn, ld + hd
        if c == "L":
            hn, hd = mn, md
        else:
            ln, ld = mn, md
    _pc[path] = Fraction(ln + hn, ld + hd)
    return _pc[path]


def score(ops):
    active = [(r, I) for r, I in ops if I > MIN_IDX and r > 0]
    if not 2 <= len(active) <= 63:
        return 0.0
    bins, total = {}, 0.0
    for k, (r0, I) in enumerate(active):
        order = max(1, min(int(ceil(I)) + 4, MAX_ORDER))
        for mm in range(1, order + 1):
            e = float(jv(mm, I)) ** 2
            if e <= 0:
                continue
            for nu in (1 + mm * float(r0), abs(1 - mm * float(r0))):
                if nu <= 1e-4:
                    continue
                total += e
                key = int(round(1200.0 * log2(nu) / CENTS_TOL))
                b = bins.setdefault(key, [0.0, 0])
                b[0] += e
                b[1] |= 1 << k
    if total <= 0:
        return 0.0
    return sum(be for be, mk in bins.values() if mk and (mk & (mk - 1))) / total


def reach(r_a, r_b, I_a, I_b):
    al = r_b / r_a
    return (al.numerator <= 2 * order_bound(I_a)
            and al.denominator <= 2 * order_bound(I_b))


def reach_brute(r_a, r_b, I_a, I_b):
    A1, A2 = 2 * order_bound(I_a), 2 * order_bound(I_b)
    al = r_b / r_a
    p, q = al.numerator, al.denominator
    for a1 in range(-A1, A1 + 1):
        for a2 in range(-A2, A2 + 1):
            if (a1 or a2) and a1 * q + a2 * p == 0:
                return True
    return False


def pair_build(r1, I1, r2, I2, _pl={}):
    """The lattice + witness list of filter_worth_it.pair_audible, built once
    per pair; audibility at each (margin, sigma) is then a cheap evaluation.
    Identical arithmetic; only the loop order moved."""
    key = (r1, I1, r2, I2)
    if key in _pl:
        return _pl[key]
    al = r2 / r1
    B1, B2 = order_bound(I1), order_bound(I2)
    p, q = al.numerator, al.denominator
    n1, n1p = -(-p // 2), -(p // 2)
    n2, n2p = -(q // 2), -(-q // 2)
    if max(abs(n1), abs(n1p)) > B1 or max(abs(n2), abs(n2p)) > B2:
        _pl[key] = None
        return None
    lat = {}
    for a in range(-B1, B1 + 1):
        for b in range(-B2, B2 + 1):
            amp = abs(float(jv(a, I1)) * float(jv(b, I2)))
            if amp == 0:
                continue
            f = abs(1.0 + a + b * float(al)) * F_C * float(r1)
            if 20 <= f <= 16000:
                lat[round(f, 6)] = lat.get(round(f, 6), 0.0) + amp
    f = np.array(sorted(lat))
    a_ = np.array([lat[k] for k in sorted(lat)])
    wit = []
    for (x, y) in ((n1, n2), (n1p, n2p)):
        amp = abs(float(jv(x, I1)) * float(jv(y, I2)))
        nu = abs(1.0 + x + y * float(al)) * F_C * float(r1)
        i = int(np.argmin(np.abs(f - nu)))
        o = f != f[i]
        wit.append((amp, f[i], o))
    _pl[key] = (f, a_, wit)
    return _pl[key]


def pair_audible_at(built, margin, wscale):
    if built is None:
        return False
    f, a_, wit = built
    for amp, fi, o in wit:
        if not o.any():
            continue
        e = np.sqrt(np.sum((a_[o] ** 2)
                           * np.exp(-0.5 * ((fi - f[o])
                                            / (erb_w(f[o]) * wscale)) ** 2)))
        if e > 0 and 20 * np.log10(amp / e) <= margin:
            return False
    return True


def tails(mx):
    out, cur = [], [""]
    for _ in range(mx):
        cur = [t + c for t in cur for c in "LR"]
        out += cur
    return out


TAILS = tails(MAXEXTRA)

G = json.load(gzip.open(GRAPH))
rng = np.random.default_rng(SEED)
pool = [nd for nd in G["nodes"]
        if 1 <= sum(1 for o in nd["ops"] if o["enabled"]) <= 3]
sample = [pool[i] for i in rng.choice(len(pool), N_NODES, replace=False)]

aud = {(m, w): dict(unf=0, fil=0, n_unf=0, n_fil=0)
       for m in MARGINS for w in SIGMAS}
n_cases = 0
for nd in sample:
    cur = [(walk(o["path"]), o["depth"]) for o in nd["ops"] if o["enabled"]]
    cur = [(r, d) for r, d in cur if r > 0]
    if not cur:
        continue
    base = next(o["path"] for o in nd["ops"] if o["enabled"])
    nidx = float(np.median([d for _, d in cur])) or 0.9
    scored = []
    for t in TAILS:
        cr = walk(base + t)
        if any(abs(float(cr) - float(r)) < 1e-9 for r, _ in cur):
            continue
        scored.append((score(cur + [(cr, nidx)]), base + t, cr))
    if len(scored) < TOPN:
        continue
    scored.sort(key=lambda x: -x[0])
    n_cases += 1
    keep = [x for x in scored if any(reach(r, x[2], I, nidx) for r, I in cur)]
    top_u, top_f = scored[:TOPN], keep[:TOPN]
    for (m, w) in aud:
        for grp, key, cnt in ((top_u, "unf", "n_unf"), (top_f, "fil", "n_fil")):
            for _, _, cr in grp:
                aud[(m, w)][cnt] += 1
                if any(reach(r, cr, I, nidx)
                       and pair_audible_at(pair_build(r, I, cr, nidx), m, w)
                       for r, I in cur):
                    aud[(m, w)][key] += 1

rates = {}
for (m, w), c in aud.items():
    rates[(m, w)] = dict(shipped=c["unf"] / max(c["n_unf"], 1),
                         filtered=c["fil"] / max(c["n_fil"], 1))
    rates[(m, w)]["gain"] = rates[(m, w)]["filtered"] - rates[(m, w)]["shipped"]

# R2: reproduce filter_worth_it's 6 grid points + n_cases.
fbank = json.load(open(os.path.join(HERE, "brocot_filter_worth_it_regraph.json")))
mm2 = 0 if n_cases == fbank["n_cases"] else 1
for k, v in fbank["sweep"].items():
    m = float(k.split(",")[0].split("=")[1])
    w = float(k.split("sigma=")[1])
    for fld in ("shipped", "filtered"):
        if abs(rates[(m, w)][fld] - v[fld]) > 1e-12:
            mm2 += 1
R2 = Bar("Part-2 mismatches vs 13 regraph-pinned filter_worth_it numbers", 0.5,
         direction="le", floor=0, ceiling=13,
         why="12 regraph rates + n_cases; a count of disagreements, 0 to 13")
r2 = R2.score(mm2)

# C3: monotone gain in sigma at every margin.
inversions = 0
for m in MARGINS:
    g = [rates[(m, w)]["gain"] for w in SIGMAS]     # sigma decreasing
    inversions += sum(1 for a, b in zip(g, g[1:]) if b < a)
C3 = Bar("adjacent gain inversions along the sigma axis, all margins", 0.5,
         direction="le", floor=0, ceiling=12,
         why="4 adjacent pairs x 3 margins = 12 chances to invert")
c3 = C3.score(inversions)

# C4/C5: the ship-bar crossing at margin = 0 — exists, and is unique.
g0 = [rates[(0.0, w)]["gain"] for w in SIGMAS]
crossings = sum(1 for a, b in zip(g0, g0[1:])
                if (a >= SHIP_BAR) != (b >= SHIP_BAR))
C4 = Bar("0.10-bar crossings along sigma at margin 0", 0.5,
         floor=0, ceiling=4, why="4 adjacent intervals; >= 1 means a crossing exists")
C5 = Bar("0.10-bar crossings along sigma at margin 0 (uniqueness)", 1.5,
         direction="le", floor=0, ceiling=4,
         why="the same count; <= 1 means the decision is one interval")
c4, c5 = C4.score(crossings), C5.score(crossings)
cross_iv = [(SIGMAS[i], SIGMAS[i + 1]) for i in range(4)
            if (g0[i] >= SHIP_BAR) != (g0[i + 1] >= SHIP_BAR)]

# ---------- report ----------
print(INSTRUMENT.report())
print(f"\nPART 1 — audible count grid (total / non-degenerate), f_c = {F_C:.0f} Hz")
for I in I_LIST:
    print(f"\n  I = {I}   (B = {below_horizon(I)[0]})")
    print(f"  {'sigma':>7s} " + "".join(f"{'m=' + str(int(m)):>10s}" for m in MARGINS))
    for s in SIGMAS:
        row = "".join(f"{grid[(I, m, s)]['total']:>6d}/{grid[(I, m, s)]['nondeg']:<3d}"
                      for m in MARGINS)
        print(f"  {s:>7.2f} {row}")
print(f"\n  headline region at I = 0.9: nondeg = 0 on "
      f"{len(wide_cells) - c1_fail}/{len(wide_cells)} cells with sigma >= 0.4; "
      f"edge cells at sigma = 0.25 nonzero in {edge['n_nonzero']}/3 margins "
      f"(witness margin index: {edge['first_witness']})")

print(f"\nPART 2 — filter gain(margin, sigma), {n_cases} cases, ship bar {SHIP_BAR:.2f}")
print(f"  {'sigma':>7s} " + "".join(f"{'m=' + str(int(m)):>10s}" for m in MARGINS))
for s in SIGMAS:
    print(f"  {s:>7.2f} " + "".join(f"{rates[(m, s)]['gain']:>+10.1%}" for m in MARGINS))
print(f"\n  THE DECISION, as a function of criterion (margin 0): "
      + ("; ".join(f"crossing in sigma ({b:.2f}, {a:.2f})" for a, b in cross_iv)
         if cross_iv else "no crossing — one action over the whole axis"))

print()
for b, v, f in ((R1, mismatch, "{:.0f}"), (R2, mm2, "{:.0f}"),
                (C1, c1_fail, "{:.0f}"), (C2, edge["n_nonzero"], "{:.0f}"),
                (C3, inversions, "{:.0f}"), (C4, crossings, "{:.0f}"),
                (C5, crossings, "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(r1, PREM_ROLE,
                          claim="Part 1 is masked_horizon's instrument, not a cousin"),
             Arm.from_bar(r2, PREM_ROLE,
                          claim="Part 2 is filter_worth_it's instrument, not a cousin"),
             Arm.from_bar(c1, EX_ROLE,
                          claim="the corrected headline holds across the whole "
                                "sigma >= 0.4 subplane, margins -6..+6"),
             Arm.from_bar(c2, EX_ROLE,
                          claim="and its region has a measured edge by sigma = 0.25"),
             Arm.from_bar(c3, MECH_ROLE,
                          claim="filter gain moves one way as the filter narrows"),
             Arm.from_bar(c4, RES_ROLE,
                          claim="the ship decision crosses its bar on the swept axis"),
             Arm.from_bar(c5, RES_ROLE,
                          claim="and only once, so the decision is one interval")],
            holds="CLAIMS_NOW_TRAVEL_WITH_THEIR_CRITERION_REGION",
            fails="CRITERION_REGION_NOT_ESTABLISHED")
print(f"\nVERDICT: {v['citation']}")

with redpath("witness-audibility evaluations on the criterion plane",
             expect_min=1000) as rp:
    rp.observed(sum(len(below_horizon(I)[1]) for I in I_LIST) * len(MARGINS)
                * len(SIGMAS))

json.dump(dict(
    I_list=I_LIST, margins=MARGINS, sigmas=SIGMAS, f_c=F_C, ship_bar=SHIP_BAR,
    graph=os.path.basename(GRAPH), seed=SEED, n_cases=n_cases,
    grid={f"I={I},m={m},s={s}": dict(total=g["total"], nondeg=g["nondeg"],
                                     audible=g["audible"])
          for (I, m, s), g in grid.items()},
    filter_rates={f"m={m},s={s}": r for (m, s), r in rates.items()},
    crossing_intervals=cross_iv,
    headline_region=dict(holds_on=f"sigma >= 0.4, margins {MARGINS}, I = 0.9",
                         failing_wide_cells=c1_fail,
                         edge=edge),
    bars={s_["name"]: s_ for s_ in (r1, r2, c1, c2, c3, c4, c5)},
    instrument=INSTRUMENT.seal(),
    scope="relative masking only; sigma-conditional BY CONSTRUCTION — the "
          "criterion-dependence is the measured object, not a caveat",
    verdict=v["head"], composed=v),
    open(os.path.join(HERE, "brocot_criterion_scope_v2.json"), "w"), indent=1)
print("\nwrote brocot_criterion_scope_v2.json")
