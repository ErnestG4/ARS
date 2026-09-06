"""Definition-of-done for a threshold or detector: BOTH rates, negative set named FIRST.

WHY STRUCTURAL AND NOT A REMINDER.  One-sided calibration has now appeared three
times in this repo: the RIGID_GUE boundary, the a_q period floor, and a guard
built during the very session that named the class, by the person who named it.
That is not carelessness. **"Check whether the detector fires" feels like
completion.** The false-positive side has no natural prompt -- nothing draws
attention to a case where the CORRECT behaviour is silence -- so vigilance is the
wrong instrument. The fix has to make the omission VISIBLE.

So: a detector is not certified until it declares a NEGATIVE SET -- the things it
must NOT fire on -- and that set has to be named when the detector is DEFINED,
before any measurement. Then forgetting to test it shows up as a blank required
field rather than as an absence nobody notices.

    spec = DetectorSpec(
        name="dual-grid invariance",
        fires_on="a quantity that moves between overlapping grids",
        positive_set={"deg13_raw": ...},      # must fire
        negative_set={"deg9_raw": ...},       # must stay SILENT  <-- required
        negative_rationale="deg 9 raw and conditioned predictions are identical, "
                           "so there is no bug present and firing is a false positive",
    )
    spec.record("deg13_raw", fired=True); spec.record("deg9_raw", fired=False)
    spec.certify()      # raises unless BOTH sets are complete and correct

NEGATIVE SETS ARE NOT ARBITRARY.  The useful negative case is the NEAREST
CONFUSABLE thing -- the one that most resembles a positive without being one.
A detector tested against far-away negatives has a specificity number and no
information (see TOOLKIT: the nearest confusable class sets the requirement).
`nearest_confusable` is therefore also required, and is free-text on purpose:
naming it is the part that does the work.
"""

# ── LITERATURE ────────────────────────────────────────────────────────────────
LITERATURE = dict(
    status="PARTIAL",
    note="The components are named; the conjunction as a BUILD-TIME "
         "PRECONDITION is the narrower of this repo's two candidate "
         "contributions. ICH Q2(R2) §3.1.2.1 comes close enough that the claim "
         "is weak and should be stated weakly.",
    anchors=[
        "Campbell & Fiske, Psych. Bulletin 56(2), 1959 — DISCRIMINANT VALIDITY "
        "and the multitrait-multimethod matrix: a measure must be shown to "
        "differ from what it is not, not merely to correlate with what it is.",
        "Hard negative mining (ML) — training explicitly on the confusable "
        "cases rather than on random negatives.",
        "Assay validation / specificity and positive controls; ICH Q2(R2) "
        "§3.1.2.1 on demonstrating discrimination against nearest analogues.",
    ],
    ours="Requiring the negative set and the nearest confusable BEFORE the "
         "detector is built, and refusing to construct one without them.",
)



class DetectorNotCertified(AssertionError):
    pass


class DetectorSpec:
    def __init__(self, name, fires_on, positive_set, negative_set,
                 nearest_confusable, negative_rationale=""):
        if not positive_set:
            raise ValueError("positive_set is empty: name what MUST fire")
        if not negative_set:
            raise DetectorNotCertified(
                f"{name}: NEGATIVE SET IS EMPTY. Name the cases this detector "
                "must NOT fire on, before measuring anything. A detector checked "
                "only where it fires is calibrated on one side — three instances "
                "in this repo so far.")
        # EMPTY-BUT-PRESENT is the obvious way to satisfy this without
        # satisfying it: a declared set whose cases name nothing. Blank and
        # placeholder keys are refused. NOTE HONESTLY WHAT THIS CANNOT DO: it is
        # a syntactic check on a semantic requirement, and this repo has twice
        # measured such checks failing their own known-positive self-tests. A
        # negative set of real-looking but irrelevant cases will pass here. What
        # actually does the work is `nearest_confusable` — naming the case that
        # most resembles a positive without being one is the part a placeholder
        # cannot fake, because it has to be a specific claim about the domain.
        _PLACEHOLDER = {"todo", "tbd", "fixme", "none", "n/a", "na", "xxx",
                        "placeholder", "tbc", "?", "-"}
        bad = [k for k in negative_set
               if not str(k).strip() or str(k).strip().lower() in _PLACEHOLDER]
        if bad:
            raise DetectorNotCertified(
                f"{name}: negative set contains blank/placeholder cases {bad}. "
                "A declared set that names nothing is an empty set with extra "
                "steps — name the actual inputs this detector must stay silent on.")
        if not nearest_confusable:
            raise DetectorNotCertified(
                f"{name}: nearest_confusable is unset. A specificity number "
                "measured against far-away negatives carries no information; "
                "name the case that most resembles a positive without being one.")
        self.name, self.fires_on = name, fires_on
        self.positive_set = dict(positive_set)
        self.negative_set = dict(negative_set)
        self.nearest_confusable = nearest_confusable
        self.negative_rationale = negative_rationale
        self.observed = {}

    def record(self, case, fired):
        if case not in self.positive_set and case not in self.negative_set:
            raise KeyError(f"{case!r} is in neither declared set; add it to the "
                           "spec rather than scoring an undeclared case")
        self.observed[case] = bool(fired)

    def rates(self):
        untested = ([c for c in self.positive_set if c not in self.observed]
                    + [c for c in self.negative_set if c not in self.observed])
        tp = sum(self.observed.get(c, False) for c in self.positive_set)
        tn = sum(not self.observed.get(c, True) for c in self.negative_set)
        return dict(sensitivity=f"{tp}/{len(self.positive_set)}",
                    specificity=f"{tn}/{len(self.negative_set)}",
                    untested=untested,
                    complete=not untested,
                    perfect=bool(not untested and tp == len(self.positive_set)
                                 and tn == len(self.negative_set)))

    def certify(self):
        r = self.rates()
        if r["untested"]:
            raise DetectorNotCertified(
                f"{self.name}: UNTESTED CASES {r['untested']} — both rates are "
                "part of the definition of done, not an optional extra")
        if not r["perfect"]:
            raise DetectorNotCertified(
                f"{self.name}: sensitivity {r['sensitivity']}, specificity "
                f"{r['specificity']} — a detector wrong in EITHER direction is "
                "not usable; a false pass and a false fire are one defect")
        return r


class ClassSpaceNotCertified(AssertionError):
    pass


class ClassSpace:
    """A declared class space must say what lies BEYOND each of its endpoints.

    WHY THIS IS CODE AND NOT PROSE.  TOOLKIT.md had already documented this exact
    failure in TWO instruments -- the quadrant classifier's `BL` collapse class
    and Brody `q` railing at its (0,1) floor -- in writing, with worked numbers.
    It did not prevent `arithmetic_toolkit._classify` from having the same defect,
    and did not cause anyone to look until a census pointed at it. **Documenting a
    failure mode does not immunize against it.** So the requirement moves into the
    same place as the named-negative-set requirement: a thing you cannot construct
    without answering.

    THE DEFECT IT CATCHES.  A class space parameterised [rigid ... Poisson] treats
    Poisson as an ENDPOINT. Super-Poisson data is then not mis-measured, it is
    UNREPRESENTABLE -- so it lands exactly ON the boundary rather than near it,
    and reads as the endpoint class. Measured across three independent instruments:
    a CV=6.5 burst process reads Brody q=0.0001 (more Poisson than Poisson's own
    0.0023); GOES flares read `rep_int_q`=0.000 -> "Poisson noise"; clustered
    synthetic reads `best='Poisson'` at KS 0.535. A perfect clock reading GUE is
    the SAME failure at the other end.

        ClassSpace(
            name="NNS surmise argmin",
            ordered_classes=["GUE", "GOE", "Poisson"],   # rigid -> random
            beyond={"GUE": "hyper-rigid / clock-like — REPRESENTED as HYPER_RIGID",
                    "Poisson": None},                    # <-- refuses: nothing beyond
        )

    `beyond` must name, for EACH endpoint, what lies past it and where such data
    goes. `None` is the admission that it has nowhere to go, and is refused.
    """

    def __init__(self, name, ordered_classes, beyond):
        if len(ordered_classes) < 2:
            raise ValueError("a class space needs at least two ordered classes")
        self.name = name
        self.ordered_classes = list(ordered_classes)
        self.endpoints = (self.ordered_classes[0], self.ordered_classes[-1])
        missing = [e for e in self.endpoints if e not in beyond]
        if missing:
            raise ClassSpaceNotCertified(
                f"{name}: endpoints {missing} have no `beyond` entry. State what "
                "lies past each end of the space and where such data is "
                "represented — an endpoint with an unstated exterior is where "
                "unrepresentable data silently piles up.")
        unrepresented = [e for e in self.endpoints if not beyond.get(e)]
        if unrepresented:
            raise ClassSpaceNotCertified(
                f"{name}: NOTHING LIES BEYOND {unrepresented} — data past that "
                "end has nowhere to go and will land ON the boundary, reading as "
                "the endpoint class. Measured three times in this repo: burst "
                "data reads 'more Poisson than Poisson'; a perfect clock reads "
                "GUE. Either extend the space, or add an explicit refusal branch "
                "and declare it here.")
        self.beyond = dict(beyond)

    def rail_check(self, values, endpoint_value, tol=1e-3):
        """Fraction of outputs sitting AT a boundary rather than near it.
        A pileup exactly on an endpoint is the signature of unrepresentable data
        (see gate_census/). Returns the fraction and a verdict."""
        import numpy as np
        v = np.asarray(list(values), float)
        v = v[np.isfinite(v)]
        if v.size == 0:
            return dict(n=0, railed_fraction=None, verdict="NO DATA")
        railed = float(np.mean(np.abs(v - endpoint_value) <= tol))
        return dict(n=int(v.size), railed_fraction=railed,
                    verdict=("RAILED — a mass of outputs sits exactly at the "
                             f"boundary ({railed:.1%}); the class space is likely "
                             "too narrow for the data being fed to it"
                             if railed > 0.05 else
                             f"OK — {railed:.1%} at the boundary"))
