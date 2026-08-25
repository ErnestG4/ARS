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


class Bar:
    """A sealed threshold with its own reachable range attached.

    `direction` is 'ge' (met when value >= thresh) or 'le' (met when <=).
    A 'ge' bar above the ceiling can never fire; a 'le' bar below the floor
    can never fire. Either is a refusal, not a warning.
    """
    __slots__ = ("name", "thresh", "floor", "ceiling", "direction", "why")

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
                    out_of_range=bool(out),
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

    print("\nREACHABLE_SELF_TEST_PASS — an inert bar cannot be constructed, an "
          "unstated range is a refusal, both directions are covered, and a "
          "value outside its declared range is flagged as a broken range.")
