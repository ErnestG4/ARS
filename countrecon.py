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

# ── LITERATURE ────────────────────────────────────────────────────────────────
# NOT SEARCHED — see the retraction note in existence.py. The same sweep
# fabricated this module's result too.
LITERATURE = dict(
    status="PARTIAL",
    note="BOTH HALVES ARE NAMED; THE CONJUNCTION-AS-MACHINERY IS NOT FOUND. "
         "The fabricated 2026-09-06 report claimed 'thoroughly named, nothing "
         "here is ours' with invented quotations. The honest re-sweep "
         "(primary text fetched per claim) lands NEAR the same verdict for "
         "half A and half B separately -- a reminder that fabrication cannot "
         "be triaged by plausibility: the invented verdict this repo WANTED "
         "(existence.py 'unoccupied') proved false, and the invented verdict "
         "it expected to lose proved largely true. Both were unevidenced "
         "until today.",
    anchors=[
        "HALF A, auditing: PCAOB AS 1105 fetched from pcaobus.org. AS "
        "1105.11, verbatim: 'Completeness -- All transactions and accounts "
        "that should be presented in the financial statements are so "
        "included.' (The retracted report's paragraph number happened to be "
        "real; now it is verified rather than lucky.) Beside it, verbatim: "
        "'Existence or occurrence' as a distinct assertion -- auditing "
        "separates the two axes the way existence.py does. AS 1105.10: 'Test "
        "the accuracy and completeness of the information' produced by the "
        "company. AS 1105.07: relevance includes whether a procedure is "
        "designed to 'test for understatement or overstatement' -- "
        "DIRECTIONAL evidence design, kin to onesidedness_is_the_default.",
        "HALF A, trials: CONSORT 2010 (Schulz, Altman & Moher, BMJ "
        "2010;340:c332), fetched: 'The CONSORT 2010 Statement is this paper "
        "including the 25 item checklist ... and the FLOW DIAGRAM' tracking "
        "every participant through enrolment, allocation, follow-up, "
        "analysis. Accounting for every unit at every stage is constitutive "
        "of the reporting standard, not an appendix. Current: CONSORT 2025, "
        "BMJ 388:e081123 (bibliographic via EQUATOR; not fetched).",
        "HALF B, the name: 'informative missingness' and 'informative "
        "censoring' are standard vocabulary -- verified in Little, 'Missing "
        "Data Assumptions', Annual Review of Statistics, which lists them as "
        "alternatives to MAR. The danger this module guards -- THE MISSING "
        "CASES ARE THE INFORMATIVE ONES -- is the nonignorable/MNAR branch "
        "of a large literature, not an in-house discovery.",
        "HALF B, attribution CORRECTED (the brief predicted mis-citation; "
        "confirmed): Rubin, Biometrika 63(3), 1976, 581-592 defines 'missing "
        "at random' AND 'observed at random' and does NOT contain MCAR or "
        "MNAR -- verified via Seaman, Galati, Jackson & Carlin (arXiv "
        "1306.2812): 'In his original 1976 paper, Rubin did not mention "
        "MCAR'; realised-MCAR = realised-MAR + observed-at-random (Heitjan "
        "1994; Little 1976 discussion). The acronym taxonomy is Little & "
        "Rubin 1987; Rubin 1987 himself 'largely avoided the term MAR', "
        "preferring 'ignorable'. Downstream usage is inconsistent (realised "
        "vs everywhere MAR -- Seaman et al.'s core point). Cite Rubin 1976 "
        "for MAR/OAR/ignorability ONLY.",
    ],
    ours="the conjunction as fail-closed machinery: CountLedger makes two "
         "instruments counting one population RECONCILE AT CONSTRUCTION TIME "
         "or refuse to report, and treats the unreconciled remainder as the "
         "hypothesis (blind_spot_correlates_with_defect), where auditing and "
         "CONSORT are reporting duties on humans and the missing-data "
         "literature models the mechanism after the fact.",
    searched="2026-09-06 re-sweep after the fabricated report was struck. "
             "Method: direct fetch of PCAOB AS 1105 and CONSORT 2010 BMJ "
             "text; Rubin-attribution chased through Seaman et al. and "
             "Little's review, quotes from fetched text only. NOT re-checked "
             "from the discarded list: ISA 315, Cochrane Handbook, RoB 2, "
             "Wu & Carroll, Diggle & Kenward, Biemer, Bird et al. 2009 -- "
             "those names remain unevidenced here and are NOT cited.",
)



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
