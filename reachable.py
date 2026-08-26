"""A bar you cannot reach is not a prediction. Declared at seal time, or refused.

WHY STRUCTURAL, AND WHY NOW
---------------------------
Three arms in this programme have been scored against bars no data could have
met, and each was read as evidence against the thing it could not test:

  1. RIGID_GUE's one-sided threshold — calibrated from one side, with an
     unmeasured error rate on the other.
  2. The a_q floor at ~1 where the zoo said ~6 — a bar set against the best
     observed rather than the ideal.
  3. cross_substrate/brocot_above_horizon.py H2 — "the gap spans at least 10x".
     Dirichlet caps the gap at 1/A and the box floors it at 1/QMAX, so the span
     inside that box cannot exceed QMAX/A = 5.0. The bar was unreachable BY
     ARITHMETIC, from two constants already in the file, and it was scored
     MISSED and wired into a conjunction whose label then read as an absence of
     structure. The power was computable before the run; nobody computed it.

The common shape: **the reachable range of a statistic is a property of the
DESIGN, not of the data, and it is almost always cheap to state.** What is
missing is never the arithmetic — it is the obligation to do it.

So this is not a checklist. `Bar` will not construct without a ceiling and a
floor, and it RAISES when the threshold sits outside them. A sealed cell that
imports it cannot seal an inert arm, because the seal will not run.

    P2 = Bar("gap span", thresh=10, floor=1.0, ceiling=QMAX / A,
             why="Dirichlet: gap <= 1/A; box floor 1/QMAX")   -> raises

WHAT THIS CANNOT DO, plainly: it takes your ceiling on trust. A wrong ceiling
passes. What it buys is that the ceiling now EXISTS, in the file, next to the
bar, where a reader can disagree with it — which is exactly what nobody could
do when the number was never written down.
"""


class UnreachableBar(AssertionError):
    pass


class UnprobedEdge(AssertionError):
    pass


def edge_probe(name, lo, hi, predicate, step=1, inside=None):
    """Probe a DECLARED DOMAIN at its edges. Construction-time obligation.

    THE MEASURED REGULARITY THIS ENFORCES. Every wrong bound found in this arc
    sat at the edge of its own declared range, and every one was found by
    somebody else:

        "convergents are ancestors"        broken by 0/1, the 0th convergent
        "unconditional in alpha > 0"       broken by alpha = 7, where the
                                           tie-break names no rational
        H2's Dirichlet ceiling             exceeded by 4 of 332 gaps
        P3A's parent ceiling               13 declared, 14 observed
        B1a's distinct-value ceiling       25,772 declared, 4,387 achievable
        B3's range                         data-derived, so unauditable
        E1 and E3                          bars sitting ON their own ceilings

    Edges are where claims die. So a declared domain must be evaluated AT its
    bounds and ONE STEP PAST them, at planting time rather than at adversarial
    review, and the predicate must actually CHANGE across the boundary -- a
    boundary nothing crosses is not a boundary, it is a decoration.

        edge_probe("alpha in (1/A, A)", Fraction(1, 8), 8,
                   lambda a: parent_of(a) is not None,
                   step=Fraction(1, 100))

    Raises UnprobedEdge when the predicate holds (or fails) on both sides of a
    declared bound, because then the bound is not the thing doing the work.
    `inside` optionally supplies a point known to be interior, for domains where
    lo+step is not yet inside.
    """
    at_lo, at_hi = predicate(lo), predicate(hi)
    below, above = predicate(lo - step), predicate(hi + step)
    mid = predicate(inside) if inside is not None else predicate((lo + hi) / 2)
    if below == at_lo == mid and mid == at_hi == above:
        raise UnprobedEdge(
            f"'{name}': the predicate is constant across both declared bounds "
            f"({lo} and {hi}) — nothing changes at either edge, so the domain "
            "is not doing the work the declaration claims for it.")
    return dict(name=name, lo=lo, hi=hi, at_lo=at_lo, below_lo=below,
                at_hi=at_hi, above_hi=above, interior=mid,
                lo_is_a_boundary=(below != at_lo or below != mid),
                hi_is_a_boundary=(above != at_hi or above != mid))


class Bar:
    """A sealed threshold with its own reachable range attached.

    `direction` is 'ge' (met when value >= thresh) or 'le' (met when <=).
    A 'ge' bar above the ceiling can never fire; a 'le' bar below the floor
    can never fire. Either is a refusal, not a warning.
    """
    __slots__ = ("name", "thresh", "floor", "ceiling", "direction", "why",
                 "edges")

    def __init__(self, name, thresh, floor, ceiling, why, direction="ge"):
        if direction not in ("ge", "le"):
            raise UnreachableBar(f"{name}: direction must be 'ge' or 'le'")
        if floor is None or ceiling is None:
            raise UnreachableBar(
                f"'{name}': floor and ceiling are required. The reachable range "
                "of a statistic is a property of the design, not the data — if "
                "you cannot state it, you do not yet know what the arm tests.")
        if not why:
            raise UnreachableBar(
                f"'{name}': `why` must say where the floor and ceiling come "
                "from. An undefended range is a number, not a bound.")
        if floor > ceiling:
            raise UnreachableBar(f"'{name}': floor {floor} exceeds ceiling {ceiling}")
        # BOTH SIDES. Until 2026-08-25 this refused only bars that could not be
        # MET, which is the one-sided-threshold-calibration lesson committed
        # inside the guard written against it: a bar that cannot MISS launders
        # a null into a pass just as surely. Found by adversarial review, which
        # constructed Bar("x", 0.5, floor=1.0, ceiling=5.0) and watched it
        # report MET on every reachable value.
        if direction == "ge" and thresh <= floor:
            raise UnreachableBar(
                f"'{name}': bar {thresh} sits AT OR BELOW the reachable floor "
                f"{floor} — every possible value meets it, so the arm cannot "
                f"MISS and any MET it reports is non-evidence. ({why})")
        if direction == "le" and thresh >= ceiling:
            raise UnreachableBar(
                f"'{name}': bar {thresh} sits AT OR ABOVE the reachable ceiling "
                f"{ceiling} — every possible value meets it, so the arm cannot "
                f"MISS. ({why})")
        if direction == "ge" and thresh > ceiling:
            raise UnreachableBar(
                f"'{name}': bar {thresh} sits ABOVE the reachable ceiling "
                f"{ceiling} — no data from this design can meet it, so the arm "
                f"is inert and any MISSED it reports is non-evidence. ({why})")
        if direction == "le" and thresh < floor:
            raise UnreachableBar(
                f"'{name}': bar {thresh} sits BELOW the reachable floor {floor} "
                f"— no data from this design can meet it. ({why})")
        self.name, self.thresh = name, thresh
        self.floor, self.ceiling = floor, ceiling
        self.direction, self.why = direction, why
        # EDGE PROBE, at construction. The refusals above are exactly this
        # probe's two failure modes; recording it makes the obligation visible
        # in the score rather than implicit in a raise that did not happen.
        lo_met = (floor >= thresh) if direction == "ge" else (floor <= thresh)
        hi_met = (ceiling >= thresh) if direction == "ge" else (ceiling <= thresh)
        self.edges = dict(at_floor=bool(lo_met), at_ceiling=bool(hi_met),
                          discriminates=bool(lo_met != hi_met))

    def score(self, value):
        """Score a value, and FLAG it if it falls outside the declared range.

        The module says the ceiling is taken on trust. This is where that trust
        is audited by the only thing that can audit it: an observation the
        range said was impossible. It happened within the hour of writing that
        sentence — brocot_above_horizon_parent declared a ceiling of 13
        parents and observed 14, because the ceiling assumed parents were drawn
        from the in-range nodes and they are not. A value outside its range
        does not mean the measurement is wrong; it means the RANGE is wrong,
        and the bar that shares that range is now unaudited."""
        met = value >= self.thresh if self.direction == "ge" else value <= self.thresh
        out = value > self.ceiling or value < self.floor
        return dict(name=self.name, value=value, thresh=self.thresh,
                    floor=self.floor, ceiling=self.ceiling, met=bool(met),
                    direction=self.direction, out_of_range=bool(out),
                    edges=self.edges,
                    headroom=(self.ceiling - self.thresh if self.direction == "ge"
                              else self.thresh - self.floor),
                    why=self.why)

    def line(self, value, fmt="{:.3f}"):
        s = self.score(value)
        op = "≥" if self.direction == "ge" else "≤"
        return (f"{self.name}: {fmt.format(value)} ({op} {self.thresh} ?) "
                f"{'MET' if s['met'] else 'MISSED'}"
                f"   [reachable {fmt.format(self.floor)}–{fmt.format(self.ceiling)}]"
                + ("  << OUT OF DECLARED RANGE: the range is wrong, so this "
                   "bar is unaudited" if s["out_of_range"] else ""))


if __name__ == "__main__":
    QMAX, A = 40, 8
    print("--- red path 1 · the real H2, re-sealed through this module ---")
    try:
        Bar("gap span", thresh=10, floor=1.0, ceiling=QMAX / A,
            why="Dirichlet caps gap at 1/A; the box floors it at 1/QMAX")
        raise SystemExit("RED PATH FAILED: the inert H2 bar was accepted")
    except UnreachableBar as e:
        print(f"    refused: {str(e)[:104]}...")
    print("    the bar that produced NOT_DIFFERENTIATED cannot now be sealed\n")

    print("--- red path 2 · a range that was never stated ---")
    for kw, label in ((dict(floor=None, ceiling=5.0), "no floor"),
                      (dict(floor=1.0, ceiling=None), "no ceiling")):
        try:
            Bar("gap span", thresh=3, why="x", **kw)
            raise SystemExit(f"RED PATH FAILED: {label} was accepted")
        except UnreachableBar as e:
            print(f"    {label:11s} refused: {str(e)[:72]}...")
    try:
        Bar("gap span", thresh=3, floor=1.0, ceiling=5.0, why="")
        raise SystemExit("RED PATH FAILED: an undefended range was accepted")
    except UnreachableBar as e:
        print(f"    no `why`    refused: {str(e)[:72]}...")

    print("\n--- red path 3b · a bar that cannot MISS, both directions ---")
    for kw, lab in ((dict(thresh=0.5, floor=1.0, ceiling=5.0), "ge under floor"),
                    (dict(thresh=1.0, floor=0.0, ceiling=1.0, direction="le"),
                     "le at ceiling")):
        try:
            Bar("x", why="an arm that every value satisfies", **kw)
            raise SystemExit(f"RED PATH FAILED: {lab} was accepted")
        except UnreachableBar as e:
            print(f"    {lab:16s} refused: {str(e)[:64]}...")

    print("\n--- red path 3 · the other direction, a 'le' bar under the floor ---")
    try:
        Bar("p-value", thresh=1e-6, floor=1.0 / 999, ceiling=1.0, direction="le",
            why="999 permutations give a smallest attainable p of 1/999")
        raise SystemExit("RED PATH FAILED: an unreachable 'le' bar was accepted")
    except UnreachableBar as e:
        print(f"    refused: {str(e)[:96]}...")

    print("\n--- red path 4 · the real wrong ceiling, caught by its own data ---")
    b = Bar("distinct parents", 8, floor=1, ceiling=13,
            why="a parent must be an in-range node, and there are 13 of them")
    print("   ", b.line(14, "{:.0f}"))
    if not b.score(14)["out_of_range"]:
        raise SystemExit("RED PATH FAILED: 14 against a ceiling of 13 was not flagged")
    print("    the premise 'parents are in-range nodes' was false; the bar "
          "passed anyway and would have gone unexamined")

    print("\n--- green path · a bar with honest headroom ---")
    b = Bar("gap span", thresh=3.0, floor=1.0, ceiling=5.72,
            why="exact: the max/min gap over the whole fixed node set, "
                "enumerated — the analytic 1/A bound is LOOSE here, because "
                "Dirichlet bounds a2 only and this box bounds a1 as well")
    print("   ", b.line(5.72, "{:.2f}"))
    print(f"    headroom above the bar: {b.score(5.72)['headroom']:.2f}")

    print("\n--- edge_probe · a declared domain whose bounds do nothing ---")
    try:
        # a domain declared [1, 10] for a predicate true everywhere near it:
        # neither bound is where anything changes, so the declaration is doing
        # no work — which is what "alpha > 0" was for the tie lemma.
        edge_probe("declared [1, 10]", 1, 10, lambda a: a > -100, step=1)
        raise SystemExit("RED PATH FAILED: a boundary nothing crosses passed")
    except UnprobedEdge as e:
        print(f"    refused: {str(e)[:92]}...")

    print("\n--- edge_probe · the real scope, whose lower bound DOES bite ---")
    from fractions import Fraction as F
    pr = edge_probe("alpha in (1/A, A), A = 8", F(1, 8), 8,
                    lambda a: a > F(1, 8), step=F(1, 100))
    print(f"    lower bound is real: {pr['lo_is_a_boundary']}   "
          f"at {pr['lo']} -> {pr['at_lo']}, one step below -> {pr['below_lo']}")

    print("\n--- every Bar now carries its edge probe ---")
    b2 = Bar("f", 0.5, floor=0.0, ceiling=1.0, why="a fraction")
    print(f"    {b2.edges}")

    print("\n--- score() must actually score, not always agree ---")
    b = Bar("s", 0.5, floor=0.0, ceiling=1.0, why="a fraction")
    if not (b.score(0.9)["met"] and not b.score(0.1)["met"]):
        raise SystemExit("RED PATH FAILED: score() does not discriminate")
    bl = Bar("s", 0.5, floor=0.0, ceiling=1.0, direction="le", why="a fraction")
    if not (bl.score(0.1)["met"] and not bl.score(0.9)["met"]):
        raise SystemExit("RED PATH FAILED: 'le' score() does not discriminate")
    print("    ge: 0.9 MET / 0.1 MISSED    le: 0.1 MET / 0.9 MISSED")

    print("\nREACHABLE_SELF_TEST_PASS — every declared range is probed at its "
          "edges at construction, a bar that cannot be MET and a bar that "
          "cannot MISS are both refused, an unstated range is a refusal, "
          "score() discriminates in both directions, and a value outside its "
          "declared range is flagged as a broken range.")
