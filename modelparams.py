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

TESTED = "TESTED"
DECLARED = "DECLARED"
_KINDS = (TESTED, DECLARED)


class UnsealedInstrument(AssertionError):
    pass


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
          "an empty model are all refused.")
