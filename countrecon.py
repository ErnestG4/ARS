"""Two instruments counting the same population must reconcile, or say why not.

WHY THIS IS STRUCTURAL AND NOT A REMINDER
-----------------------------------------
`gate_census/copy_dedup.json` reported, in one object, on one population:

    "sites_checked": 19,
    "bodies_found":  15,

and nothing anywhere reconciled 19 to 15. The divergence inventory then analysed
11 variants drawn from the 15, and the ruling docket was very nearly written
against that sample. The missing four were not noise -- three of the four were
the COMPUTED_UNUSED sites, i.e. THE HARD TAIL. The extractor surveying for
structural irregularity was blind to exactly the structurally irregular cases.

That is the truncation-inverts-order lesson in a new coordinate: a subset that
looks like a sample is a *biased* sample whenever the thing that excluded rows is
correlated with the thing being measured -- and an unreported count difference is
the only visible trace it leaves.

    AN UNEXPLAINED COUNT MISMATCH IS A COVERAGE HOLE ANNOUNCING ITSELF.

Both numbers were published, honestly, in plain sight. Publication was not the
problem. Nothing REQUIRED the difference to be accounted for, so the difference
sat there being true and inert for two days.

    ledger = CountLedger("classifier call sites")
    ledger.report("copy_dedup.sites_checked", 19)
    ledger.report("copy_dedup.bodies_found", 15)
    ledger.explain("copy_dedup.sites_checked", "copy_dedup.bodies_found", 4,
                   "four sites classify inline; a FunctionDef-named extractor "
                   "cannot see them")
    ledger.settle()          # raises unless EVERY pair is reconciled

THE EXPLANATION MUST CARRY THE EXACT DELTA. `explain(a, b, delta, why)` verifies
that delta equals the measured difference. A hand-wave that names the right cause
with the wrong magnitude is a partially-understood coverage hole, which is the
dangerous kind: it feels settled. Getting the arithmetic to close is what forces
you to enumerate the missing rows rather than gesture at them.

WHAT THIS CANNOT DO, stated plainly: it cannot tell you the explanation is TRUE.
It can only insist one exists and that it accounts for every missing unit. A
false explanation of the right size passes. As with detector_spec, the part that
does the work is the part a placeholder cannot fake -- here, the enumeration the
arithmetic demands.
"""


class UnreconciledCounts(AssertionError):
    pass


class CountLedger:
    def __init__(self, population):
        self.population = population
        self._counts = {}
        self._expl = {}

    def report(self, name, n):
        """Register a count. Re-reporting a different value for the same name is
        itself a mismatch and is refused immediately."""
        n = int(n)
        if name in self._counts and self._counts[name] != n:
            raise UnreconciledCounts(
                f"{self.population}: '{name}' reported twice with different "
                f"values ({self._counts[name]} then {n})")
        self._counts[name] = n
        return n

    def explain(self, a, b, delta, why):
        for k in (a, b):
            if k not in self._counts:
                raise UnreconciledCounts(f"{self.population}: no count named '{k}'")
        if not why or not str(why).strip():
            raise UnreconciledCounts(
                f"{self.population}: explanation for {a} vs {b} is blank. "
                "Name what the missing units ARE.")
        actual = self._counts[a] - self._counts[b]
        if int(delta) != actual:
            raise UnreconciledCounts(
                f"{self.population}: explanation for {a} vs {b} claims a delta of "
                f"{delta}, but the measured difference is {actual}. An explanation "
                "that does not carry the exact delta is a partially-understood "
                "coverage hole -- enumerate the missing units.")
        self._expl[frozenset((a, b))] = (a, b, actual, str(why).strip())

    def unreconciled(self):
        names = sorted(self._counts)
        out = []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if self._counts[a] == self._counts[b]:
                    continue
                if frozenset((a, b)) not in self._expl:
                    out.append((a, b, self._counts[a] - self._counts[b]))
        return out

    def settle(self, verbose=True):
        bad = self.unreconciled()
        if verbose:
            print(f"COUNT LEDGER — {self.population}")
            for k in sorted(self._counts):
                print(f"    {k:44s} {self._counts[k]:>6d}")
            for a, b, d, why in self._expl.values():
                print(f"    reconciled {a} - {b} = {d}: {why}")
        if bad:
            lines = "\n".join(
                f"    {a} ({self._counts[a]}) vs {b} ({self._counts[b]}): "
                f"difference {abs(d)} UNEXPLAINED" for a, b, d in bad)
            raise UnreconciledCounts(
                f"{self.population}: {len(bad)} count pair(s) do not reconcile.\n"
                f"{lines}\nEach difference is a set of units one instrument saw and "
                "the other did not. Enumerate them; do not assume they resemble the "
                "units both instruments saw.")
        if verbose:
            print(f"    RECONCILED — {len(self._counts)} counts, "
                  f"{len(self._expl)} explained difference(s)")
        return True


if __name__ == "__main__":
    # RED PATH: the guard must FAIL on the case that motivated it, before it is
    # trusted anywhere. The historical numbers are used verbatim.
    print("--- red path: the copy_dedup mismatch, unexplained ---")
    led = CountLedger("classifier call sites (historical, unexplained)")
    led.report("copy_dedup.sites_checked", 19)
    led.report("copy_dedup.bodies_found", 15)
    try:
        led.settle()
        raise SystemExit("RED PATH FAILED: an unexplained 19-vs-15 settled clean")
    except UnreconciledCounts as e:
        print(f"    raised as required:\n{e}\n")

    print("--- red path: an explanation with the WRONG delta ---")
    led2 = CountLedger("classifier call sites (wrong magnitude)")
    led2.report("copy_dedup.sites_checked", 19)
    led2.report("copy_dedup.bodies_found", 15)
    try:
        led2.explain("copy_dedup.sites_checked", "copy_dedup.bodies_found", 2,
                     "a couple of sites classify inline")
        raise SystemExit("RED PATH FAILED: a wrong-magnitude explanation was accepted")
    except UnreconciledCounts as e:
        print(f"    raised as required:\n{e}\n")

    print("--- green path: the same mismatch, correctly enumerated ---")
    led3 = CountLedger("classifier call sites")
    led3.report("copy_dedup.sites_checked", 19)
    led3.report("copy_dedup.bodies_found", 15)
    led3.explain("copy_dedup.sites_checked", "copy_dedup.bodies_found", 4,
                 "run_controls, run_analytical_nns, run_per_pll_nns, universality "
                 "classify inline; a FunctionDef-named extractor cannot see them")
    led3.settle()
    print("\nCOUNTRECON_SELF_TEST_PASS — fires on both historical shapes, "
          "silent when the delta is enumerated")
