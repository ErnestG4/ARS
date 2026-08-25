"""THE MAP FIELD: parent regions and spectral events, in closed form.

COMMITTED GENERATOR of cross_substrate/brocot_two_layer_field.json — the data a
brocot map overlay would consume. This is a CONSTRUCTION, not a measurement, so
it carries assertions rather than sealed predictions: every claim it makes about
its own output is checked here and fails the run if false.

WHAT IT EMITS, AND WHY TWO LAYERS
----------------------------------
    REGION  the perceptual category: which below-horizon rational a ratio is
            heard as a detuning of. Piecewise constant in alpha; boundaries are
            mediants of node pairs. A fill colour.
    EVENT   the spectral discontinuity: where partials merge. At the nodes.
            A tick mark.

`brocot_jump_display_v3` established these are DISJOINT BY CONSTRUCTION — a
node is its own parent with gap 0, so a neighbourhood of it takes that node as
its parent and the category can only switch strictly between nodes. Events sit
at region centres; boundaries sit where nothing happens. That is asserted below
(A4), not assumed: a fill and a tick never contend for the same pixel.

SCOPE, WHICH IS NARROW AND MUST TRAVEL WITH THE FEATURE
--------------------------------------------------------
  * TWO OPERATORS. `brocot_dissolution_curve` puts the coincidence rate above
    0.9 by N = 7, so on a 16-operator patch essentially every parameter set
    coincides somewhere and the categorisation is vacuous. This is a per-PAIR
    overlay, not a patch-level one.
  * THE DIRECT CHANNEL, two sine modulators, epsilon = 1e-3 — the coincidence
    horizon's own scope, inherited unchanged.
  * The parent needs an argmin over the box, NOT a prefix of PullIndex's stored
    path (measured: 30.1%). 289 integer ops at I = 0.9, computed offline.

THE BEAT RATE IS THE WITHIN-REGION COORDINATE and it is in Hz, so it scales
with the carrier: a region that beats at 5.5 Hz at f_c = 220 beats at 11 Hz an
octave up. The emitted field carries the dimensionless gap; Hz is a display
conversion, done at draw time against the played note.
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
from phase3.partial_prediction import order_bound                 # noqa: E402

LO, HI = Fraction(7, 10), Fraction(7, 5)      # brocot's defining regime
I_LIST = [0.9, 1.5, 2.0, 3.0]
F_C_REF = 220.0                               # reference only; Hz is a display unit


def gap_and_parent(alpha, A):
    """(gap, parent) — the minimum of |a1 + a2*alpha| over the box, and the
    rational |a1|/|a2| attaining it. Exact rational arithmetic throughout."""
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            key = (abs(a1 * q + a2 * p), max(abs(a1), abs(a2)), -a2)
            if best is None or key < best[0]:
                best = (key, a1, a2)
    (v, _, _), a1, a2 = best
    return Fraction(v, q), (Fraction(abs(a1), abs(a2)) if a2 else None)


def build(I):
    A = 2 * order_bound(I)
    nodes = sorted({Fraction(n, d) for n in range(1, A + 1)
                    for d in range(1, A + 1) if LO <= Fraction(n, d) <= HI})
    # candidate boundaries: a tie needs |a1 +/- b1| / |a2 +/- b2|, so numerator
    # and denominator are bounded by 2A. No grid anywhere in this.
    cands = sorted({Fraction(n, d) for n in range(1, 2 * A + 1)
                    for d in range(1, 2 * A + 1)
                    if LO < Fraction(n, d) < HI})
    edges = [LO] + cands + [HI]
    mids = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
    pars = [gap_and_parent(m, A)[1] for m in mids]

    regions, start = [], LO
    for i in range(1, len(mids) + 1):
        if i == len(mids) or pars[i] != pars[i - 1]:
            end = HI if i == len(mids) else edges[i]
            par = pars[i - 1]
            inside = [nd for nd in nodes if start <= nd <= end]
            g0, g1 = gap_and_parent((start + end) / 2, A)[0], None
            # beat range over the region, sampled at the two ends and the middle
            gs = [gap_and_parent(start + (end - start) * Fraction(k, 8), A)[0]
                  for k in range(1, 8)]
            regions.append(dict(parent=str(par), lo=float(start), hi=float(end),
                                lo_exact=str(start), hi_exact=str(end),
                                nodes=[str(x) for x in inside],
                                gap_min=float(min(gs)), gap_max=float(max(gs)),
                                beat_hz_min=float(min(gs)) * F_C_REF,
                                beat_hz_max=float(max(gs)) * F_C_REF))
            start = end
    return A, nodes, cands, regions


out = {}
for I in I_LIST:
    A, nodes, cands, regions = build(I)

    # ---- A1 the regions tile [LO, HI] exactly: no gap, no overlap ----------
    assert regions[0]["lo_exact"] == str(LO) and regions[-1]["hi_exact"] == str(HI), \
        f"I={I}: regions do not span [{LO}, {HI}]"
    for a, b in zip(regions, regions[1:]):
        assert a["hi_exact"] == b["lo_exact"], \
            f"I={I}: gap or overlap between {a['hi_exact']} and {b['lo_exact']}"

    # ---- A2 the parent really is constant inside each region --------------
    for r in regions:
        a, b = Fraction(r["lo_exact"]), Fraction(r["hi_exact"])
        for k in range(1, 8):
            got = gap_and_parent(a + (b - a) * Fraction(k, 8), A)[1]
            assert str(got) == r["parent"], \
                f"I={I}: parent {got} != {r['parent']} inside [{a}, {b}]"

    # ---- A3 every node is its own parent, with gap exactly 0 --------------
    for nd in nodes:
        g, par = gap_and_parent(nd, A)
        assert g == 0, f"I={I}: node {nd} has nonzero gap {g}"

    # ---- A4 THE DISJOINTNESS: no node lies on a region boundary -----------
    bounds = {r["lo_exact"] for r in regions} | {r["hi_exact"] for r in regions}
    bounds -= {str(LO), str(HI)}                 # the range ends are not events
    on = [str(nd) for nd in nodes if str(nd) in bounds]
    assert not on, f"I={I}: node(s) {on} sit ON a region boundary — a tick and " \
                   "a fill edge would contend for the same pixel"

    # ---- A5 THE FIELD IS A VORONOI TESSELLATION OF THE EVENTS -------------
    # Each region contains exactly one node, and that node is the region's own
    # parent. Not designed for: it falls out of the fact that a node is its own
    # parent with gap 0 and the parent is a nearest-in-the-weighted-metric
    # rational. It is what makes the two layers legible together — a fill is
    # always one tick's basin, never a stripe between two.
    for r in regions:
        assert len(r["nodes"]) == 1, \
            f"I={I}: region [{r['lo_exact']}, {r['hi_exact']}] holds " \
            f"{len(r['nodes'])} events, not 1: {r['nodes']}"
        assert r["nodes"][0] == r["parent"], \
            f"I={I}: region of {r['parent']} contains event {r['nodes'][0]}"
    assert len(regions) == len(nodes), \
        f"I={I}: {len(regions)} regions but {len(nodes)} events"

    out[str(I)] = dict(I=I, B=order_bound(I), A=A, n_regions=len(regions),
                       n_events=len(nodes), n_candidates=len(cands),
                       events=[str(x) for x in nodes], regions=regions)

print(f"alpha in [{LO}, {HI}] — brocot's defining regime (limit_ratio 9/7)\n")
print(f"{'I':>5s} {'B':>3s} {'A':>3s} {'regions':>8s} {'events':>7s} "
      f"{'widest region':>15s} {'beat span (Hz @220)':>20s}")
for I in I_LIST:
    d = out[str(I)]
    w = max(d["regions"], key=lambda r: r["hi"] - r["lo"])
    gs = [r["beat_hz_max"] for r in d["regions"]]
    print(f"{I:>5.1f} {d['B']:>3d} {d['A']:>3d} {d['n_regions']:>8d} "
          f"{d['n_events']:>7d} {w['parent']:>9s} ±{(w['hi'] - w['lo']) / 2:.3f} "
          f"{min(r['beat_hz_min'] for r in d['regions']):>9.1f}–{max(gs):<9.1f}")

d = out[str(0.9)]
print(f"\nthe field at I = 0.9 (A = {d['A']}): {d['n_regions']} regions, "
      f"{d['n_events']} events")
print(f"{'region':>15s} {'heard as':>9s} {'events inside':>14s} "
      f"{'beat Hz @ 220':>14s}")
for r in d["regions"]:
    print(f"{r['lo']:>7.4f}–{r['hi']:<7.4f} {r['parent']:>9s} "
          f"{','.join(r['nodes']) or '—':>14s} "
          f"{r['beat_hz_min']:>6.1f}–{r['beat_hz_max']:<7.1f}")

with redpath("regions in the I = 0.9 field", expect_min=8) as rp:
    rp.observed(d["n_regions"])

json.dump(dict(lo=float(LO), hi=float(HI), lo_exact=str(LO), hi_exact=str(HI),
               f_c_reference=F_C_REF, I_list=I_LIST,
               scope=dict(operators=2, channel="direct", waves="sine",
                          epsilon=1e-3,
                          vacuous_beyond_N="coincidence rate > 0.9 by N = 7 "
                                           "(brocot_dissolution_curve)"),
               fields=out),
          open(f"{HERE}/brocot_two_layer_field.json", "w"), indent=1)
print("\nA1 regions tile exactly · A2 parent constant within · A3 every node "
      "has gap 0 · A4 no node on a boundary\nA5 exactly one event per region, "
      "and it is that region's parent — the field is a VORONOI TESSELLATION of "
      "the events\n   under the denominator-weighted metric. All asserted, all "
      "held, at every I.")
print("written -> cross_substrate/brocot_two_layer_field.json")
