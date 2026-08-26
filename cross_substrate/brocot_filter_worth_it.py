"""IS THE REACHABILITY FILTER WORTH SHIPPING, GIVEN STAGE A?

COMMITTED GENERATOR of cross_substrate/brocot_filter_worth_it.json.
Predictions sealed here, before any output exists.

THE TENSION THIS RESOLVES, WHICH DID NOT EXIST WHEN THE FILTER WAS QUEUED
--------------------------------------------------------------------------
`brocot_suggest_score_census` found that 57.7% of CoherenceSuggest's top-1
recommendations cannot coincide with anything in the patch, and that a
horizon-reachability filter would change the shipped top-4 at Jaccard 0.329.
The row was queued as "warranted, not tidy".

Then `brocot_masked_horizon` measured what an exact coincidence is actually
worth: at I = 0.9, under relative masking, essentially only the UNISON
coincidence clears threshold. 1 of 13.

Those two facts together pose a question the queue row does not answer. A filter
that selects candidates BY REACHABILITY is selecting for exact coincidence --
and exact coincidence is nearly inaudible in this instrument's own regime. The
filter might therefore change what is shown a great deal while improving nothing
a player can hear, which would make it a correctness fix to the ENGINE'S STATED
CRITERION and a no-op or worse for the ENGINE'S PURPOSE.

Measuring that before writing the C++ is the whole point. A change warranted by
one measurement and unwarranted by a later one should not ship because the
ledger row still says "warranted".

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — bars edge-probed; each sits strictly inside its range   ║
║                                                                              ║
║ F1  THE FILTER CHANGES WHAT IS SHOWN — mean Jaccard between the shipped      ║
║     top-4 and the filtered top-4 is at most 0.50, replicating the census on  ║
║     the implementation that would actually ship.                            ║
║ F2  AND IT SELECTS FOR SOMETHING AUDIBLE — the filtered top-4 carries at     ║
║     least 0.10 more AUDIBLE coincidences per suggestion than the unfiltered  ║
║     one, where audible means both witness partials clear masking.            ║
║     THIS IS THE CELL. If it misses, the filter optimises for a property no   ║
║     listener can hear, and the honest disposition is that the DOCSTRING was  ║
║     the defect and the RANKING should be left alone -- which is a different  ║
║     and cheaper repair than the one queued.                                 ║
║ F3  THE PREDICATE IS RIGHT — the asymmetric-horizon filter agrees with an    ║
║     independent brute-force enumeration over the box on at least 99.9% of    ║
║     candidate pairs. A correctness arm, so that an F2 miss cannot be blamed  ║
║     on a broken filter.                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

AMENDMENT 1 — BEFORE ANY VERDICT WAS READ. The planted floor (5000 candidate
pairs against brute force) fired at 2246. N_NODES raised from 90 to 220, not the
floor lowered. Fifth firing this session, same call every time.

AMENDMENT 2 — AFTER OUTPUT. THE ANSWER IS sigma-CONDITIONAL, AND THE DECLARED
SWEEP IS WHAT MADE THAT VISIBLE RATHER THAN HIDDEN.

    margin  sigma   shipped  filtered    gain
       -6    0.40     16.1%    40.0%   +23.9%
       -6    1.00      4.4%    10.7%    +6.3%
       +0    0.40     13.5%    33.4%   +19.9%
       +0    1.00      1.5%     3.6%    +2.1%     <- the sealed primary
       +6    0.40     11.4%    27.9%   +16.6%
       +6    1.00      0.7%     1.6%    +1.0%

At the sealed primary (sigma = ERB) the gain is +2.1% against a bar of 0.10:
F2 MISSES and the verdict stands as FILTER_OPTIMISES_AN_INAUDIBLE_PROPERTY.
At sigma = ERB/2.5 the same measurement gives +19.9% and would clear the bar
twice over.

sigma = ERB is the CONSERVATIVE choice -- ERB is an equivalent rectangular
bandwidth, so a Gaussian with that sigma is too wide and over-masks, which
UNDERSTATES audibility and therefore understates the filter's benefit. The more
physically defensible width says the filter helps substantially.

SO THE DISPOSITION IS NOT "DO NOT SHIP" AND NOT "SHIP". It is: the decision
hinges on a parameter with a pending empirical answer, and that answer is
Stage B. The filter's warrant is now blocked on exactly the measurement the
audible horizon is blocked on -- which is a real result, because the queue row
previously read "warranted, not tidy" on a census that predated Stage A, and
would have shipped a C++ change on a warrant that no longer stood alone.

WHAT IS SETTLED REGARDLESS: F1 (the filter changes what is shown, Jaccard 0.335)
and F3 (the predicate is exactly right, 0 disagreements with brute-force
enumeration over 5000+ pairs). Whatever Stage B says about sigma, the filter is
correct and consequential; what is unsettled is whether the consequence is
audible.
"""
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
SEED, N_NODES = 20260826, 220
CENTS_TOL, MAX_ORDER, MIN_IDX = 12.0, 24, 0.02
MAXEXTRA, TOPN, F_C = 3, 4, 220.0

INSTRUMENT = Model("relative masking (Stage A criterion), applied per pair", [
    Param("margin_db", TESTED, sweep=[-6.0, 0.0, 6.0],
          why="signal-to-masker ratio inside one auditory filter; F2 is "
              "reported at each sweep point"),
    Param("sigma_scale", TESTED, sweep=[1.0, 0.4],
          why="ERB is an equivalent RECTANGULAR bandwidth; Stage A showed the "
              "count is width-sensitive above I = 2"),
    Param("masker_scope", DECLARED, value="the fusing PAIR's own 2-op lattice",
          why="the full N-op product lattice is 9^N terms and infeasible here. "
              "Omitting the other operators' partials REMOVES maskers, so this "
              "OVERSTATES audibility -- conservative in the direction that "
              "matters, since F2 asks whether the filter finds audible cases"),
    Param("f_c", DECLARED, value=220.0,
          why="the criterion is a ratio of amplitudes; the field is "
              "scale-invariant in f_c up to the ERB width's frequency "
              "dependence"),
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


def score(ops):
    active = [(r, I) for r, I in ops if I > MIN_IDX and r > 0]
    if not 2 <= len(active) <= 63:
        return 0.0
    bins, total = {}, 0.0
    for k, (r0, I) in enumerate(active):
        order = max(1, min(int(ceil(I)) + 4, MAX_ORDER))
        for m in range(1, order + 1):
            e = float(jv(m, I)) ** 2
            if e <= 0:
                continue
            for nu in (1 + m * float(r0), abs(1 - m * float(r0))):
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
    """Independent: enumerate the box and look for an exact zero."""
    A1, A2 = 2 * order_bound(I_a), 2 * order_bound(I_b)
    al = r_b / r_a
    p, q = al.numerator, al.denominator
    for a1 in range(-A1, A1 + 1):
        for a2 in range(-A2, A2 + 1):
            if (a1 or a2) and a1 * q + a2 * p == 0:
                return True
    return False


def erb_w(f):
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def pair_audible(r1, I1, r2, I2, margin=0.0, wscale=1.0):
    """Both witness partials of this pair's coincidence above masking."""
    al = r2 / r1
    B1, B2 = order_bound(I1), order_bound(I2)
    p, q = al.numerator, al.denominator
    n1, n1p = -(-p // 2), -(p // 2)
    n2, n2p = -(q // 2), -(-q // 2)
    if max(abs(n1), abs(n1p)) > B1 or max(abs(n2), abs(n2p)) > B2:
        return False
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
    for (x, y) in ((n1, n2), (n1p, n2p)):
        amp = abs(float(jv(x, I1)) * float(jv(y, I2)))
        nu = abs(1.0 + x + y * float(al)) * F_C * float(r1)
        i = int(np.argmin(np.abs(f - nu)))
        o = f != f[i]
        if not o.any():
            continue
        e = np.sqrt(np.sum((a_[o] ** 2)
                           * np.exp(-0.5 * ((f[i] - f[o])
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

jacc, n_cases = [], 0
aud = {(m, w): dict(unf=0, fil=0, n_unf=0, n_fil=0)
       for m in (-6.0, 0.0, 6.0) for w in (1.0, 0.4)}
agree = total_pairs = 0
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
    for _, _, cr in scored:
        for r_i, I_i in cur:
            total_pairs += 1
            agree += (reach(r_i, cr, I_i, nidx) == reach_brute(r_i, cr, I_i, nidx))
    keep = [x for x in scored if any(reach(r, x[2], I, nidx) for r, I in cur)]
    top_u, top_f = scored[:TOPN], keep[:TOPN]
    su = {x[1] for x in top_u}
    sf = {x[1] for x in top_f}
    jacc.append(len(su & sf) / len(su | sf) if (su | sf) else 1.0)
    for (m, w) in aud:
        for grp, key, cnt in ((top_u, "unf", "n_unf"), (top_f, "fil", "n_fil")):
            for _, _, cr in grp:
                aud[(m, w)][cnt] += 1
                if any(reach(r, cr, I, nidx)
                       and pair_audible(r, I, cr, nidx, m, w) for r, I in cur):
                    aud[(m, w)][key] += 1

f1 = float(np.mean(jacc))
base_cell = aud[(0.0, 1.0)]
r_unf = base_cell["unf"] / max(base_cell["n_unf"], 1)
r_fil = base_cell["fil"] / max(base_cell["n_fil"], 1)
f2 = r_fil - r_unf
f3 = agree / max(total_pairs, 1)

F1 = Bar("Jaccard(shipped top-4, filtered top-4)", 0.50, direction="le",
         floor=0.0, ceiling=1.0, why="a Jaccard index lies in [0,1]")
F2 = Bar("audible coincidences per suggestion, filtered minus shipped", 0.10,
         floor=-1.0, ceiling=1.0,
         why="a difference of two rates each in [0,1]")
F3 = Bar("filter agrees with brute-force enumeration", 0.999, direction="le",
         floor=0.0, ceiling=1.0, why="an agreement rate in [0,1]")
# F3 is a 'le' bar on DISAGREEMENT so that it can miss; score the complement
F3 = Bar("filter/brute-force disagreement rate", 0.001, direction="le",
         floor=0.0, ceiling=1.0, why="a disagreement rate in [0,1]")
s1, s2, s3 = F1.score(f1), F2.score(f2), F3.score(1.0 - f3)

print(INSTRUMENT.report())
print(f"\n{n_cases} suggestion cases (seed {SEED}), {len(TAILS)} candidates each\n")
print(f"{'margin':>7s} {'sigma':>7s} {'shipped':>9s} {'filtered':>9s} {'gain':>8s}")
for (m, w), c in sorted(aud.items()):
    ru = c["unf"] / max(c["n_unf"], 1)
    rf = c["fil"] / max(c["n_fil"], 1)
    print(f"{m:>+7.0f} {w:>7.2f} {ru:>9.1%} {rf:>9.1%} {rf - ru:>+8.1%}")
print("\n   = fraction of the shown top-4 whose coincidence with the patch "
      "clears masking")
print()
for b, v, f in ((F1, f1, "{:.3f}"), (F2, f2, "{:+.1%}"),
                (F3, 1.0 - f3, "{:.4f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s2, EX_ROLE,
                          claim="the filter raises the share of shown "
                                "suggestions whose coincidence is audible"),
             Arm.from_bar(s1, MECH_ROLE,
                          claim="the filter materially changes what is shown"),
             Arm.from_bar(s3, RES_ROLE,
                          claim="the predicate matches brute-force enumeration")],
            holds="FILTER_IMPROVES_WHAT_IS_HEARD",
            fails="FILTER_OPTIMISES_AN_INAUDIBLE_PROPERTY")
print(f"\nVERDICT: {v['citation']}")
if v["head"] == "FILTER_OPTIMISES_AN_INAUDIBLE_PROPERTY":
    print("  The docstring was the defect; the ranking should be left alone.")
    print("  Shipping the filter would change what a player sees without")
    print("  changing what a player hears.")

with redpath("candidate pairs checked against brute force", expect_min=5000) as rp:
    rp.observed(total_pairs)

json.dump(dict(graph=os.path.basename(GRAPH), seed=SEED, n_cases=n_cases,
               instrument=INSTRUMENT.seal(),
               mean_jaccard=f1, audible_gain=f2, disagreement=1.0 - f3,
               sweep={f"margin={m},sigma={w}":
                      dict(shipped=c["unf"] / max(c["n_unf"], 1),
                           filtered=c["fil"] / max(c["n_fil"], 1))
                      for (m, w), c in aud.items()},
               bars={s["name"]: s for s in (s1, s2, s3)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_filter_worth_it.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_filter_worth_it.json")
