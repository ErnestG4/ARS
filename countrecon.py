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
    ledger.settle()          # raises unless every count is CONNECTED

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
        """Counts not CONNECTED to the rest by explained differences.

        Completeness is not required and should not be: deltas compose. If
        a - b is explained and b - c is explained, then a - c is IMPLIED, not a
        further fact needing its own sentence. Demanding all N(N-1)/2 pairs
        produced, on this guard's first real use, ten explanations reading "as
        above" -- and boilerplate is how a guard goes inert. What must hold is
        that no count stands APART from the others: an unconnected count is one
        whose relationship to the population was never stated.
        """
        parent = {k: k for k in self._counts}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for a, b, _d, _w in self._expl.values():
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
        # counts sharing a value need no explanation to be reconciled
        by_value = {}
        for k, v in self._counts.items():
            by_value.setdefault(v, []).append(k)
        for ks in by_value.values():
            for k in ks[1:]:
                ra, rb = find(ks[0]), find(k)
                if ra != rb:
                    parent[ra] = rb
        groups = {}
        for k in self._counts:
            groups.setdefault(find(k), []).append(k)
        if len(groups) <= 1:
            return []
        comps = sorted(groups.values(), key=len, reverse=True)
        anchor = comps[0]
        return [(k, anchor[0], self._counts[k] - self._counts[anchor[0]])
                for comp in comps[1:] for k in sorted(comp)]

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
                f"    {a} ({self._counts[a]}) is not connected to "
                f"{b} ({self._counts[b]}) by any explained difference "
                f"({abs(d)} unaccounted)" for a, b, d in bad)
            raise UnreconciledCounts(
                f"{self.population}: {len(bad)} count(s) stand apart from the population.\n"
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
