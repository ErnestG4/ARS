"""The criterion was sealed; its instrument wasn't. Typed, not remembered.

WHY STRUCTURAL — THREE INSTANCES, EACH FOUND AFTER THE VERDICT
----------------------------------------------------------------
A cell seals its predictions carefully and then imports a perceptual or physical
model whose own parameters were never sealed against. Three times in this arc a
constant inside the INSTRUMENT turned out to be doing classification work, and
each was written down only after a verdict rested on it:

  1. eps = 1e-3 in `order_bound`. It floors a single Bessel factor and thereby
     sets the entire horizon. Its sensitivity was measured only when an outside
     review asked, and the answer moved the shipped region count from 13 to 3.
  2. The -40/-60 dB audibility floor. Chosen, not derived, and the cell's own
     robustness arm then showed the count swings 40% across it.
  3. sigma = ERB in the masking model. `brocot_masked_horizon` sealed M2 against
     the MARGIN and left sigma unsealed — and sigma turned out to matter more:
     at I = 3.0 the audible count runs 0 to 6 across a fourfold change.

The shape is always the same. The PREDICTIONS are pre-registered; the
INSTRUMENT that evaluates them arrives with free parameters nobody enumerated,
so a sensitivity that would have been cheap before the run becomes an amendment
after it. Sealing the question while leaving the ruler adjustable is the
sealed-ruler clause, one level down.

    A CRITERION IS ONLY AS SEALED AS THE INSTRUMENT THAT EVALUATES IT.

So the enumeration becomes a typed obligation, on the `classify_guard`
derivation-or-None grammar: every parameter of an imported model is declared
TESTED (with the sweep that tested it) or DECLARED (with the reason it is held
fixed). There is no third option and no default, because the failure mode is
precisely a parameter nobody thought to list.

    Model("relative masking, Glasberg-Moore ERB", [
        Param("margin_db", TESTED, sweep=[-6, 0, 6],
              why="signal-to-masker ratio inside one filter"),
        Param("sigma_scale", TESTED, sweep=[1.0, 0.5, 0.4, 0.25],
              why="ERB is an equivalent RECTANGULAR bandwidth, not a sigma"),
        Param("f_c", DECLARED, value=220.0,
              why="the criterion is a ratio of amplitudes at one frequency, so "
                  "it is invariant in f_c up to the ERB width's mild "
                  "frequency dependence"),
    ]).seal()

WHAT THIS CANNOT DO, stated plainly: it cannot know a parameter exists. A model
with a hard-coded constant nobody names passes, exactly as `detector_spec`
cannot know about an unlisted confound. What it buys is that the enumeration is
now a REFUSAL rather than a habit — a cell that imports a model and lists
nothing will not run — and that TESTED carries its sweep, so "we checked" is a
claim with data attached rather than a recollection.
"""

# ── LITERATURE ────────────────────────────────────────────────────────────────
LITERATURE = dict(
    status="NAMED",
    note="swept() prevents reporting a selected maximum as if it were a "
         "measurement. This is among the best-named problems in all of "
         "metascience and we should cite rather than re-derive it.",
    anchors=[
        "Gelman & Loken, 2013 — THE GARDEN OF FORKING PATHS: analysis choices "
        "contingent on the data inflate the result even with no explicit "
        "multiple testing and no intent.",
        "Simmons, Nelson & Simonsohn, Psych. Science 22(11), 2011 — "
        "RESEARCHER DEGREES OF FREEDOM / false-positive psychology.",
        "Steegen, Tuerlinckx, Gelman & Vanpaemel, PPS 11(5), 2016 — MULTIVERSE "
        "ANALYSIS; Simonsohn, Simmons & Nelson — SPECIFICATION CURVE ANALYSIS. "
        "swept()'s 'report the pre-registered configuration WITH the full "
        "spread beside it' is a small specification curve, and should be "
        "described as one.",
    ],
    ours="Nothing here is ours except that swept() HAS NO WAY TO RETURN THE "
         "MAXIMUM. The literature recommends reporting the spread; this makes "
         "reporting only the winner unrepresentable.",
)


TESTED = "TESTED"
DECLARED = "DECLARED"
_KINDS = (TESTED, DECLARED)


class UnsealedInstrument(AssertionError):
    pass


class SelectedMaximum(AssertionError):
    pass


def swept(name, results, prereg, swing_tol=0.25):
    """Report a swept statistic by its PRE-REGISTERED configuration, never its max.

    THE DEFECT THIS PREVENTS, measured 2026-08-28 in brocot_cue_salience. A
    correlation was computed over nine configurations (three concentration
    statistics x three band widths), the largest was taken as the result, and a
    bootstrap was run on the winner. That interval is not a confidence interval;
    it is the winner's interval conditional on having won -- selection on the
    dependent variable wearing a CI as camouflage.

    THE TELL IS REUSABLE: a concept that survives its own binning does not swing
    like this.

        participation_ratio   0.5 Hz 0.749   1.0 Hz 0.418   2.0 Hz 0.459
        gini                  0.5 Hz 0.741   1.0 Hz 0.275   2.0 Hz 0.470
        top_band_share        0.5 Hz 0.568   1.0 Hz 0.056   2.0 Hz 0.527

    Those are not one measurement with noise. They are several measurements of
    possibly different things, and the largest is the least trustworthy of them.

    So: a swept statistic is reported by the configuration NAMED IN ADVANCE. The
    spread travels with it, and the maximum is not available as an answer --
    this function has no way to return it. If the swing exceeds `swing_tol` the
    result carries `unstable=True`, because a bar cleared by a configuration
    that varies that much has not been cleared by the concept.

        swept("rho vs answer rate", {"pr|0.5": 0.749, "pr|1.0": 0.418, ...},
              prereg="pr|1.0")     -> value 0.418, swing 0.693, unstable True

    The estimator choice is part of the ruler, and the sealed-ruler clause
    covers rulers.
    """
    if not results:
        raise SelectedMaximum(f"'{name}': no results to report")
    if prereg not in results:
        raise SelectedMaximum(
            f"'{name}': the pre-registered configuration {prereg!r} is not "
            f"among the {len(results)} computed. Naming it AFTER seeing the "
            "table is choosing an analysis; naming it before is the whole "
            f"point. Available: {sorted(results)}")
    vals = [abs(v) for v in results.values()]
    swing = (max(vals) - min(vals)) / max(max(vals), 1e-30)
    best = max(results, key=lambda k: abs(results[k]))
    return dict(name=name, value=results[prereg], prereg=prereg,
                n_configs=len(results), spread=dict(results),
                minimum=min(vals), maximum=max(vals), swing=float(swing),
                unstable=bool(swing > swing_tol),
                max_config=best, max_value=results[best],
                selection_penalty=(abs(results[best]) - abs(results[prereg])))


class Param:
    __slots__ = ("name", "kind", "sweep", "value", "why")

    def __init__(self, name, kind, why, sweep=None, value=None):
        if kind not in _KINDS:
            raise UnsealedInstrument(
                f"'{name}': kind must be TESTED or DECLARED, not {kind!r}. "
                "There is no default — a parameter nobody classified is the "
                "failure this module exists to prevent.")
        if not why:
            raise UnsealedInstrument(
                f"'{name}': `why` is required. For TESTED it says what the "
                "parameter means; for DECLARED it says why holding it fixed is "
                "defensible. An undefended constant is the whole defect.")
        if kind == TESTED:
            if sweep is None or len(sweep) < 2:
                raise UnsealedInstrument(
                    f"'{name}': TESTED needs a sweep of at least 2 values — "
                    "one point is a setting, not a sensitivity. Got "
                    f"{sweep!r}.")
            if len(set(sweep)) != len(sweep):
                raise UnsealedInstrument(
                    f"'{name}': TESTED sweep has repeated values {sweep!r}; "
                    "a repeated point adds no sensitivity.")
        elif value is None:
            raise UnsealedInstrument(
                f"'{name}': DECLARED needs the `value` it is held at. A "
                "parameter declared fixed at an unstated number is not fixed, "
                "it is hidden.")
        self.name, self.kind, self.why = name, kind, why
        self.sweep, self.value = sweep, value

    def line(self):
        if self.kind == TESTED:
            return f"{self.name:>14s}  TESTED    sweep {self.sweep}"
        return f"{self.name:>14s}  DECLARED  fixed at {self.value}"


class Model:
    """An imported instrument, with every free parameter accounted for."""

    def __init__(self, name, params):
        if not name:
            raise UnsealedInstrument("a model needs a name")
        if not params:
            raise UnsealedInstrument(
                f"'{name}': no parameters listed. A model with no free "
                "parameters is possible but rare; if that is truly the case, "
                "say so with an explicit DECLARED entry rather than an empty "
                "list, so a reader can see the claim was made.")
        seen = set()
        for p in params:
            if not isinstance(p, Param):
                raise UnsealedInstrument(f"'{name}': {p!r} is not a Param")
            if p.name in seen:
                raise UnsealedInstrument(f"'{name}': duplicate parameter "
                                         f"'{p.name}'")
            seen.add(p.name)
        self.name, self.params = name, list(params)

    def seal(self):
        return dict(model=self.name,
                    params=[dict(name=p.name, kind=p.kind, why=p.why,
                                 sweep=p.sweep, value=p.value)
                            for p in self.params],
                    n_tested=sum(p.kind == TESTED for p in self.params),
                    n_declared=sum(p.kind == DECLARED for p in self.params))

    def report(self):
        out = [f"instrument: {self.name}"]
        for p in self.params:
            out.append("  " + p.line())
        return "\n".join(out)


if __name__ == "__main__":
    print("--- the real masking instrument, sealed ---")
    m = Model("relative masking, Glasberg-Moore ERB", [
        Param("margin_db", TESTED, sweep=[-6.0, 0.0, 6.0],
              why="signal-to-masker ratio inside one auditory filter"),
        Param("sigma_scale", TESTED, sweep=[1.0, 0.5, 0.4, 0.25],
              why="ERB is an equivalent RECTANGULAR bandwidth, not a Gaussian "
                  "sigma, so sigma = ERB over-masks"),
        Param("f_c", DECLARED, value=220.0,
              why="the criterion is a ratio of amplitudes, invariant in f_c up "
                  "to the ERB width's mild frequency dependence"),
    ])
    print(m.report())

    print("\n--- red path 1 · the historical defect: sigma listed at one value ---")
    try:
        Param("sigma_scale", TESTED, sweep=[1.0], why="ERB width")
        raise SystemExit("RED PATH FAILED: a one-point sweep was accepted")
    except UnsealedInstrument as e:
        print(f"    refused: {str(e)[:88]}...")

    print("\n--- red path 2 · a parameter with no classification ---")
    try:
        Param("eps", "PROBABLY_FINE", why="it has always been 1e-3")
        raise SystemExit("RED PATH FAILED: an unclassified parameter passed")
    except UnsealedInstrument as e:
        print(f"    refused: {str(e)[:88]}...")

    print("\n--- red path 3 · DECLARED without its value, and without a why ---")
    for kw, lab in ((dict(kind=DECLARED, why="fixed by convention"), "no value"),
                    (dict(kind=DECLARED, value=1e-3, why=""), "no why")):
        try:
            Param("eps", **kw)
            raise SystemExit(f"RED PATH FAILED: DECLARED with {lab} passed")
        except UnsealedInstrument as e:
            print(f"    {lab:9s} refused: {str(e)[:74]}...")

    print("\n--- the real swept correlation, reported honestly ---")
    r = swept("rho vs answer rate",
              {"participation_ratio|0.5": 0.749, "participation_ratio|1.0": 0.418,
               "participation_ratio|2.0": 0.459, "gini|0.5": 0.741,
               "gini|1.0": 0.275, "gini|2.0": 0.470, "top_band_share|0.5": 0.568,
               "top_band_share|1.0": 0.056, "top_band_share|2.0": 0.527},
              prereg="participation_ratio|1.0")
    print(f"    reported {r['value']:.3f} at the pre-registered "
          f"{r['prereg']}, not {r['max_value']:.3f} at {r['max_config']}")
    print(f"    swing {r['swing']:.3f} over {r['n_configs']} configs -> "
          f"unstable={r['unstable']};  selection penalty "
          f"{r['selection_penalty']:+.3f}")
    if r["value"] >= 0.60:
        raise SystemExit("RED PATH FAILED: the pre-registered value should miss")
    print("    the pre-registered value MISSES the 0.60 bar the max cleared")

    print("\n--- red path 5 · naming the configuration after seeing the table ---")
    try:
        swept("rho", {"a": 0.4, "b": 0.7}, prereg="c")
        raise SystemExit("RED PATH FAILED: an unlisted prereg was accepted")
    except SelectedMaximum as e:
        print(f"    refused: {str(e)[:84]}...")

    print("\n--- red path 4 · a model that lists nothing ---")
    try:
        Model("some criterion", [])
        raise SystemExit("RED PATH FAILED: an empty parameter list passed")
    except UnsealedInstrument as e:
        print(f"    refused: {str(e)[:88]}...")

    print("\n--- green path · the seal record ---")
    s = m.seal()
    print(f"    {s['n_tested']} tested, {s['n_declared']} declared")

    print("\nMODELPARAMS_SELF_TEST_PASS — an unclassified parameter, a "
          "one-point sweep, a valueless DECLARED, an undefended constant and "
          "an empty model are all refused, and a swept statistic reports its "
          "pre-registered configuration with the maximum unavailable.")
