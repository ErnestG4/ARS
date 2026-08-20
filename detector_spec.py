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
