"""THE EAR TRUNCATES THE PATH. The parent is a prefix, not a computation.

COMMITTED GENERATOR of cross_substrate/brocot_path_truncation.json.
Predictions sealed here, before any output exists.

WHERE THIS COMES FROM
---------------------
`brocot_above_horizon_parent.json`: above the horizon every ratio is heard as a
detuning of a parent, that parent is below the horizon at 100%, and it is a
Stern-Brocot ANCESTOR of the ratio at 100%.

`source/audio/Operator.h` in the synth: "The SB path picks *which* rational;
detune sets *how far off* it the effective ratio sits." The parameter model is
already (base rational, detune in cents).

Those are the same decomposition, arrived at from opposite ends -- one from
psychoacoustics, one from a parameter design made years earlier for unrelated
reasons. If the perceptual parent is not merely SOME ancestor but the DEEPEST
in-box one, then the map does not have to compute anything: `PullIndex` stores
path strings, and the perceptual category is that string truncated at the
horizon. A prefix, not an argmin.

That is the claim under test, and it is sharper than what has been measured.
"Is an ancestor" was 100%; "is the deepest in-box ancestor" is a strictly
stronger statement and could be false at any node where a shallower ancestor
happens to minimise the gap.

WHY T3 IS IN THE SEAL
---------------------
A display that never moves is not a display. The horizon is A = 2*order_bound(I),
so raising the modulation index should cut the path DEEPER and split the map
into finer regions. If the truncation depth does not respond to I, the feature
is a static overlay and the depth slider is decoration -- worth knowing before
anything is drawn.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ T1  The perceptual parent IS the deepest Stern-Brocot ancestor with          ║
║     max(p,q) <= A, for at least 90% of above-horizon ratios. If this holds,  ║
║     the category is a string prefix and the synth already stores it.         ║
║ T2  The truncation is not a constant cut: at least 4 distinct truncation     ║
║     DEPTHS occur. A single depth would mean the horizon is doing no work     ║
║     that a fixed path-length limit would not do more simply.                 ║
║ T3  The cut responds to the modulation index: mean truncation depth at       ║
║     I = 3.0 is at least 1.2x that at I = 0.9. The depth slider must move the ║
║     map, or the overlay is static.                                           ║
║                                                                              ║
║ T1 IS THE ONE THAT DECIDES THE IMPLEMENTATION. If it misses, the parent is   ║
║ still well defined and still an ancestor, but it must be found by argmin     ║
║ over the box at display time rather than read off a stored string -- which   ║
║ is a slower and much less elegant feature, and should be described as such   ║
║ rather than papered over.                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from existence import summarise, EXISTENCE                        # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

LO, HI, QMAX = 0.70, 1.40, 40
I_LIST = [0.9, 1.5, 2.0, 3.0]
I_MUS = 0.9

NODES = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 60)
                if LO <= p / q <= HI and gcd(p, q) == 1}, key=float)


def sb_path(target):
    """(ratio, direction-string) at each step of the Stern-Brocot descent."""
    lo_n, lo_d, hi_n, hi_d = 0, 1, 1, 0
    out, s = [], ""
    for _ in range(4000):
        mn, md = lo_n + hi_n, lo_d + hi_d
        med = Fraction(mn, md)
        if med == target:
            return out
        out.append((med, s))
        if target < med:
            s += "L"
            hi_n, hi_d = mn, md
        else:
            s += "R"
            lo_n, lo_d = mn, md
    return out


def parent_of(alpha, A):
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            key = (abs(a1 * q + a2 * p), max(abs(a1), abs(a2)), -a2)
            if best is None or key < best[0]:
                best = (key, a1, a2)
    _, a1, a2 = best
    return Fraction(abs(a1), abs(a2)) if a2 else None


per_I = {}
for I in I_LIST:
    A = 2 * order_bound(I)
    rows = []
    for f in NODES:
        if max(f.numerator, f.denominator) <= A:
            continue                                  # below the horizon: fuses
        path = sb_path(f)
        inbox = [(r, s) for r, s in path
                 if max(r.numerator, r.denominator) <= A]
        deep = inbox[-1] if inbox else None
        par = parent_of(f, A)
        rows.append(dict(ratio=str(f), A=A, parent=str(par),
                         deepest_inbox=(str(deep[0]) if deep else None),
                         trunc_depth=(len(deep[1]) if deep else 0),
                         path_len=len(path),
                         matches=bool(deep is not None and deep[0] == par)))
    per_I[I] = rows

base = per_I[I_MUS]
n = len(base)
v1 = sum(r["matches"] for r in base) / n
depths = [r["trunc_depth"] for r in base]
v2 = len(set(depths))
mean_lo = sum(depths) / n
hi_rows = per_I[3.0]
mean_hi = sum(r["trunc_depth"] for r in hi_rows) / len(hi_rows)
v3 = mean_hi / mean_lo if mean_lo else float("inf")
max_depth = max(r["path_len"] for r in base)

T1 = Bar("parent is the deepest in-box ancestor", 0.90, floor=0.0, ceiling=1.0,
         why="a fraction over the above-horizon ratios: 0 to 1 by construction")
T2 = Bar("distinct truncation depths", 4, floor=1, ceiling=max_depth,
         why=f"a truncation depth is a proper prefix length, so it lies in "
             f"[0, {max_depth}] over this fixed node set")
T3 = Bar("mean depth at I=3.0 / at I=0.9", 1.2, floor=0.0, ceiling=max_depth,
         why="the ratio of two mean prefix lengths; the numerator cannot "
             f"exceed the longest path, {max_depth}, and the denominator is "
             "at least 1 in practice")

s1, s2, s3 = T1.score(v1), T2.score(v2), T3.score(v3)

print(f"alpha in [{LO}, {HI}], q <= {QMAX}: {len(NODES)} ratios\n")
print(f"{'I':>5s} {'B':>3s} {'A':>3s} {'above':>6s} {'mean cut':>9s} "
      f"{'depths':>7s}  {'deepest-ancestor match':>22s}")
for I in I_LIST:
    r = per_I[I]
    d = [x["trunc_depth"] for x in r]
    print(f"{I:>5.1f} {order_bound(I):>3d} {2 * order_bound(I):>3d} {len(r):>6d} "
          f"{sum(d) / len(d):>9.2f} {len(set(d)):>7d}  "
          f"{sum(x['matches'] for x in r) / len(r):>21.1%}")

print(f"\nworked examples at I = {I_MUS} (A = {2 * order_bound(I_MUS)}):")
print(f"{'ratio':>8s} {'path':>14s} {'cut':>4s} {'parent':>7s}   heard as")
for r in base[:4] + base[len(base) // 2:len(base) // 2 + 2] + base[-3:]:
    f = Fraction(r["ratio"])
    path = sb_path(f)
    full = path[-1][1] + ("L" if False else "") if path else ""
    print(f"{r['ratio']:>8s} {full[:14]:>14s} {r['trunc_depth']:>4d} "
          f"{r['parent']:>7s}   a detuned {r['parent']}")

print()
for b, v, f in ((T1, v1, "{:.1%}"), (T2, v2, "{:.0f}"), (T3, v3, "{:.2f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s1, EX_ROLE),
             Arm.from_bar(s2, RES_ROLE, note="cut is not constant"),
             Arm.from_bar(s3, RES_ROLE, note="cut responds to I")],
            holds="PARENT_IS_A_PATH_PREFIX", fails="PARENT_NEEDS_AN_ARGMIN")
print(f"\nVERDICT: {v['head']}")
if v["qualifiers"]:
    print(f"   qualified by: {', '.join(v['qualifiers'])}")
if v["head"] == "PARENT_IS_A_PATH_PREFIX":
    print("  The perceptual category is the operator's own Stern-Brocot path,")
    print("  truncated at the horizon. PullIndex already stores that string, so")
    print("  the map needs a prefix, not a computation.")

ex = summarise("n_matches", [r["matches"] for r in base], EXISTENCE)
with redpath("above-horizon ratios with an in-box ancestor", expect_min=100) as rp:
    rp.observed(sum(1 for r in base if r["deepest_inbox"]))

json.dump(dict(lo=LO, hi=HI, qmax=QMAX, I_list=I_LIST, I_mus=I_MUS,
               n_nodes=len(NODES), max_path_len=max_depth,
               mean_cut={str(I): sum(x["trunc_depth"] for x in per_I[I]) / len(per_I[I])
                         for I in I_LIST},
               match_rate={str(I): sum(x["matches"] for x in per_I[I]) / len(per_I[I])
                           for I in I_LIST},
               bars={s["name"]: s for s in (s1, s2, s3)},
               verdict=v["head"], composed=v, rows=base),
          open(f"{HERE}/brocot_path_truncation.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_path_truncation.json")
