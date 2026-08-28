"""THE METER'S GENERATIVE MODEL: sum of combs, when the truth is a product lattice.

COMMITTED GENERATOR of cross_substrate/brocot_coherence_model.json.
Predictions sealed here, before any output exists.

THE GAP, RAISED BY REVIEW AND VERIFIED BEFORE SEALING
-------------------------------------------------------
BROCOT-SPEC section 2 justifies `Coherence.h` with "the full spectrum is a sum of
N independent combs". For SIMULTANEOUS modulators that is wrong: the spectrum is
a PRODUCT lattice at 1 + n1*r1 + n2*r2 with energy J_n1(I1)*J_n2(I2), and the
comb model keeps only the lattice points where every OTHER index is zero.

The omitted cross-partials carry (1 - J0(I)^2)^2 of the total energy at matched
indices -- verified both by formula and by direct lattice summation:

    I = 0.9  ->  0.121        I = 1.5  ->  0.545        I = 2.0  ->  0.902

So at I >= 1.5 the meter scores a minority of the spectrum.

WHAT THIS CELL DOES NOT ASSUME, HAVING LEARNED FROM THE FILTER
---------------------------------------------------------------
`brocot_filter_worth_it` measured a correctness fix that changed what a user
SEES without changing what a user HEARS, and the queue row that warranted it had
gone stale. The same trap is open here: the comb model is provably the wrong
generative model, and that is a documentation defect regardless. Whether it is a
RANKING defect is a separate question, and it is the one that decides whether
any C++ changes.

So the deciding arm is not "is the model wrong" -- that is settled arithmetic --
but "does scoring on the true lattice change what the engine recommends".

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — bars edge-probed                                        ║
║                                                                              ║
║ M1  THE GAP IS REAL AT THE INSTRUMENT'S OWN INDEX — omitted energy is at      ║
║     least 10% at I = 0.9. A premise check; settled arithmetic, and cheap.    ║
║ M2  THE SCORES DIFFER MATERIALLY — median relative difference between the     ║
║     comb score and the full-lattice score is at least 20%.                   ║
║ M3  AND THE RANKING CHANGES — mean Jaccard between the shipped top-4 and the  ║
║     full-lattice top-4 is at most 0.50. THIS IS THE DECIDING ARM. If it       ║
║     misses, the comb model is wrong and harmless: the docstring owes a        ║
║     correction and the ranking owes nothing, which is the cheaper repair and  ║
║     must be reported as such rather than upgraded.                           ║
║ M4  THE EFFECT GROWS WITH INDEX — the score difference at I = 2.0 exceeds     ║
║     that at I = 0.9, as (1 - J0^2)^2 says it must. A mechanism arm: if the    ║
║     difference does not track the omitted energy, the diagnosis is wrong      ║
║     whatever M2 and M3 say.                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import gzip
import json
import os
import sys
from fractions import Fraction
from math import ceil, log2

import numpy as np
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
sys.path.insert(0, ROOT)
sys.path.insert(0, BROCOT)
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

GRAPH = f"{BROCOT}/resources/landscape_graph_16mix.json.gz"
SEED, N_NODES = 20260827, 140
CENTS_TOL, MAX_ORDER, MIN_IDX = 12.0, 24, 0.02
MAXEXTRA, TOPN = 3, 4
I_LIST = [0.9, 1.5, 2.0]

INSTRUMENT = Model("Coherence.h, reproduced exactly, against the product lattice", [
    Param("cents_tolerance", TESTED, sweep=[6.0, 12.0, 24.0],
          why="the engine's bin width. It is the free parameter of the SCORE, "
              "and a ranking change that only appears at one bin width is a "
              "property of the bin, not of the model"),
    Param("index", TESTED, sweep=I_LIST,
          why="the omitted energy is (1-J0(I)^2)^2, so the gap is a strong "
              "function of index; M4 tests that the effect tracks it"),
    Param("max_order", DECLARED, value=MAX_ORDER,
          why="the engine's own cap, reproduced rather than chosen"),
    Param("min_index", DECLARED, value=MIN_IDX,
          why="the engine's own audibility floor for a modulator"),
    Param("lattice_order", DECLARED, value="order_bound(I) per operator",
          why="the product lattice is truncated at the same Bessel order bound "
              "the horizon uses, so the two models are compared over the same "
              "reachable set and the difference is the MODEL, not the cutoff"),
])
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


def _shared(bins, total):
    if total <= 0:
        return 0.0
    return sum(be for be, mk in bins.values() if mk and (mk & (mk - 1))) / total


def comb_score(ops, cents):
    """Coherence.h exactly: per op, partials only at |1 +/- m*r|."""
    act = [(r, I) for r, I in ops if I > MIN_IDX and r > 0]
    if not 2 <= len(act) <= 63:
        return 0.0
    bins, total = {}, 0.0
    for k, (r0, I) in enumerate(act):
        order = max(1, min(int(ceil(I)) + 4, MAX_ORDER))
        for m in range(1, order + 1):
            e = float(jv(m, I)) ** 2
            if e <= 0:
                continue
            for nu in (1 + m * float(r0), abs(1 - m * float(r0))):
                if nu <= 1e-4:
                    continue
                total += e
                b = bins.setdefault(int(round(1200.0 * log2(nu) / cents)),
                                    [0.0, 0])
                b[0] += e
                b[1] |= 1 << k
    return _shared(bins, total)


def lattice_score(ops, cents):
    """The true product lattice: partials at 1 + sum n_i r_i, energy prod J.

    'Shared' keeps the same meaning -- energy in a bin touched by two or more
    operators -- but an operator is counted as present when its own index is
    nonzero, so a cross-partial marks every operator that contributed."""
    act = [(r, I) for r, I in ops if I > MIN_IDX and r > 0]
    if not 2 <= len(act) <= 6:
        return None
    orders = [order_bound(I) for _, I in act]
    bins, total = {}, 0.0
    idx = [range(-o, o + 1) for o in orders]

    def rec(k, nu, amp, mask):
        nonlocal total
        if k == len(act):
            if mask == 0 or abs(nu) <= 1e-4:
                return
            e = amp * amp
            total += e
            b = bins.setdefault(int(round(1200.0 * log2(abs(nu)) / cents)),
                                [0.0, 0])
            b[0] += e
            b[1] |= mask
            return
        r, I = act[k]
        for n in idx[k]:
            a = float(jv(n, I))
            if a == 0.0:
                continue
            rec(k + 1, nu + n * float(r), amp * a,
                mask | ((1 << k) if n != 0 else 0))

    rec(0, 1.0, 1.0, 0)
    return _shared(bins, total)


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
        if 1 <= sum(1 for o in nd["ops"] if o["enabled"]) <= 2]
sample = [pool[i] for i in rng.choice(len(pool), N_NODES, replace=False)]

omitted = {I: (1.0 - float(jv(0, I)) ** 2) ** 2 for I in I_LIST}
rel, jac, per_I = [], [], {I: [] for I in I_LIST}
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
        ops = cur + [(cr, nidx)]
        c = comb_score(ops, CENTS_TOL)
        L = lattice_score(ops, CENTS_TOL)
        if L is None:
            continue
        scored.append((c, L, base + t))
        if c > 0:
            rel.append(abs(L - c) / c)
    if len(scored) < TOPN:
        continue
    su = {p for _, _, p in sorted(scored, key=lambda x: -x[0])[:TOPN]}
    sl = {p for _, _, p in sorted(scored, key=lambda x: -x[1])[:TOPN]}
    jac.append(len(su & sl) / len(su | sl))
    for I in I_LIST:
        ops = [(r, I) for r, _ in cur] + [(walk(base + TAILS[0]), I)]
        c, L = comb_score(ops, CENTS_TOL), lattice_score(ops, CENTS_TOL)
        if c and L is not None:
            per_I[I].append(abs(L - c) / c)

m1 = omitted[0.9]
m2 = float(np.median(rel)) if rel else 0.0
m3 = float(np.mean(jac)) if jac else 1.0
med = {I: (float(np.median(v)) if v else 0.0) for I, v in per_I.items()}
m4 = med[2.0] - med[0.9]

M1 = Bar("omitted cross-partial energy at I=0.9", 0.10, floor=0.0, ceiling=1.0,
         why="(1 - J0^2)^2 is a fraction of total lattice energy: 0 to 1")
M2 = Bar("median relative score difference", 0.20, floor=0.0, ceiling=10.0,
         why="|L - c| / c with both scores in [0,1] and c bounded away from 0 "
             "by the sample; 10 is a generous ceiling on a relative difference")
M3 = Bar("Jaccard(comb top-4, lattice top-4)", 0.50, direction="le",
         floor=0.0, ceiling=1.0, why="a Jaccard index lies in [0,1]")
M4 = Bar("score difference at I=2.0 minus at I=0.9", 0.0, floor=-10.0,
         ceiling=10.0, why="a difference of two relative differences")
s1, s2, s3, s4 = M1.score(m1), M2.score(m2), M3.score(m3), M4.score(m4)

print(INSTRUMENT.report())
print(f"\n{len(jac)} suggestion cases (seed {SEED}), {len(TAILS)} candidates each\n")
print(f"{'I':>5s} {'omitted energy':>15s} {'median |L-c|/c':>16s}")
for I in I_LIST:
    print(f"{I:>5.1f} {omitted[I]:>15.1%} {med[I]:>15.1%}")
print()
for b, v, f in ((M1, m1, "{:.1%}"), (M2, m2, "{:.1%}"),
                (M3, m3, "{:.3f}"), (M4, m4, "{:+.1%}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s3, EX_ROLE,
                          claim="scoring on the true lattice changes what the "
                                "engine recommends"),
             Arm.from_bar(s2, RES_ROLE,
                          claim="the two scores differ materially at all"),
             Arm.from_bar(s1, RES_ROLE,
                          claim="the omitted energy is non-trivial at I=0.9"),
             Arm.from_bar(s4, MECH_ROLE,
                          claim="the difference tracks the omitted energy, so "
                                "the diagnosis is the right one")],
            holds="MODEL_GAP_REACHES_THE_RANKING",
            fails="MODEL_GAP_IS_DOCUMENTATION_ONLY")
print(f"\nVERDICT: {v['citation']}")
if v["head"] == "MODEL_GAP_IS_DOCUMENTATION_ONLY":
    print("  The comb model is provably the wrong generative model AND the")
    print("  ranking does not inherit it. The docstring owes a correction; the")
    print("  C++ owes nothing. That is the cheaper repair and it is the one")
    print("  the measurement supports.")

with redpath("suggestion cases scored on both models", expect_min=100) as rp:
    rp.observed(len(jac))

json.dump(dict(graph=os.path.basename(GRAPH), seed=SEED, n_cases=len(jac),
               instrument=INSTRUMENT.seal(),
               omitted_energy={str(I): omitted[I] for I in I_LIST},
               median_rel_diff={str(I): med[I] for I in I_LIST},
               median_rel_overall=m2, mean_jaccard=m3,
               bars={s["name"]: s for s in (s1, s2, s3, s4)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_coherence_model.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_coherence_model.json")
