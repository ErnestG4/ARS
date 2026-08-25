"""An existence question needs an existence statistic. Typed, not remembered.

WHY STRUCTURAL AND NOT A DOCSTRING
-----------------------------------
Three times now, a median has been used to answer "does any?":

  1. gate_census/c3_inline_inventory.py — coincidence counts aggregated per
     denominator by MEDIAN. At q=8 two of three nodes were collision-free, so
     the median read 0 and the detector declared q=8 saturated. Off by one in
     the horizon, found only because the boundary looked wrong.
  2. cross_substrate/brocot_useful_depth.py — the same shape, fixed there with
     a comment recording the lesson: "A central-tendency summary cannot answer
     an existence question."
  3. cross_substrate/brocot_theorem_scope.py — `refl_other` reported by MEDIAN,
     read 0.0 at every index, taken as absence. It was NOT absence: 10/17/25/34
     nodes carried one. The data was collected and buried by the summary.

Instance 3 was committed **in the file whose docstring records the fix from
instance 2**, two runs later, by the author of that docstring. That is the
pre-checkrun exit-code pattern exactly: a rule living in prose fails to bind the
hands that wrote it. This repo has measured, twice, what such rules are worth.

    A RULE YOU CONSULT IS A RULE YOU'LL SKIP.

So the question type becomes a typed argument, on the classify_guard grammar:
passing nothing is not a default, it is a refusal. And as with
`classify_guard(constant, derivation=None)`, the honest admission is the cheap
path — `summarise(..., CENTRAL_TENDENCY)` is one word, and it puts the choice in
the record where a reader can see it.

    summarise("refl_other", counts, EXISTENCE)        -> n_nonzero, any, witness
    summarise("slope", values, CENTRAL_TENDENCY)      -> median, mean, spread
    summarise("refl_other", counts, CENTRAL_TENDENCY) -> RAISES: the name is
                                                         detection-shaped

WHAT THIS CANNOT DO, stated plainly: it cannot know your intent. A field named
`slope` that is secretly a detection count passes as central tendency. The name
heuristic is a syntactic check on a semantic property — the same honest limit
`detector_spec` carries. What does the work is that the common case, a
detection-shaped name, now has to be argued for out loud.
"""
import re

EXISTENCE = "EXISTENCE"
CENTRAL_TENDENCY = "CENTRAL_TENDENCY"
_QUESTIONS = (EXISTENCE, CENTRAL_TENDENCY)

# Names that look like detections. Deliberately broad: a false positive costs
# one `acknowledge=` argument, a false negative costs a buried finding.
_DETECTION_NAME = re.compile(
    r"(^|_)(n|num|count|hits?|found|detected|fires?|matches|occurrences|"
    r"present|any|coincidences?|collisions?|violations?|failures?|"
    r"survivors?|refl_\w+|\w+_other)($|_)", re.I)


class WrongStatisticForQuestion(AssertionError):
    pass


def looks_like_a_detection(name):
    return bool(_DETECTION_NAME.search(str(name)))


def summarise(name, values, question, acknowledge=None):
    """Summarise `values` under a DECLARED question type.

    EXISTENCE        -> how many are non-zero, whether any is, and a witness.
                        Never a median: the whole failure mode is a majority of
                        zeros hiding a minority of ones.
    CENTRAL_TENDENCY -> median / mean / spread. Refused for detection-shaped
                        names unless `acknowledge` states why it is right here.
    """
    if question not in _QUESTIONS:
        raise WrongStatisticForQuestion(
            f"'{name}': question must be one of {_QUESTIONS}, not {question!r}. "
            "Passing nothing is not a default — the question type is the choice "
            "this function exists to make visible.")

    vals = [v for v in values if v is not None]

    if question is EXISTENCE or question == EXISTENCE:
        nz = [i for i, v in enumerate(vals) if v]
        return dict(question=EXISTENCE, n=len(vals), n_nonzero=len(nz),
                    any=bool(nz), all=bool(nz) and len(nz) == len(vals),
                    first_witness=(nz[0] if nz else None),
                    witnesses=nz[:8])

    if looks_like_a_detection(name) and not acknowledge:
        raise WrongStatisticForQuestion(
            f"'{name}' is a detection-shaped name and you asked for a "
            "CENTRAL_TENDENCY summary. A median over detections answers 'does "
            "the typical case fire', when the question is almost always 'does "
            "ANY case fire' — and a majority of zeros will bury a real minority. "
            "Measured three times in this repo; the third was committed in the "
            "file that records the fix for the second.\n"
            "    Use EXISTENCE, or pass acknowledge='<why the average is the "
            "quantity of interest here>'.")

    import statistics as _st
    return dict(question=CENTRAL_TENDENCY, n=len(vals),
                median=(_st.median(vals) if vals else None),
                mean=(_st.fmean(vals) if vals else None),
                spread=((max(vals) - min(vals)) if vals else None),
                acknowledged=acknowledge)


if __name__ == "__main__":
    print("--- red path 1: the historical refl_other data, summarised as central ---")
    # the real shape: most nodes carry nothing, a real minority carries something
    refl_other = [0] * 117 + [4, 2, 2, 4, 2, 6, 2, 4, 2, 2]
    try:
        summarise("refl_other", refl_other, CENTRAL_TENDENCY)
        raise SystemExit("RED PATH FAILED: a detection-named median was accepted")
    except WrongStatisticForQuestion as e:
        print(f"    raised as required: {str(e)[:96]}...")

    print("\n--- what the median actually said, and what was true ---")
    import statistics
    print(f"    median = {statistics.median(refl_other)}   <- read as 'absent'")
    ex = summarise("refl_other", refl_other, EXISTENCE)
    print(f"    EXISTENCE: any={ex['any']}  n_nonzero={ex['n_nonzero']}/{ex['n']}  "
          f"first witness at index {ex['first_witness']}")

    print("\n--- red path 2: an undeclared question ---")
    try:
        summarise("refl_other", refl_other, None)
        raise SystemExit("RED PATH FAILED: a missing question type was accepted")
    except WrongStatisticForQuestion as e:
        print(f"    raised as required: {str(e)[:88]}...")

    print("\n--- green path: a genuine central-tendency field ---")
    print(f"    {summarise('slope', [4.94, 8.63, 7.86, 0.31], CENTRAL_TENDENCY)}")

    print("\n--- green path: a detection name, average argued for out loud ---")
    print(f"    {summarise('n_partials', [31, 31, 30, 29], CENTRAL_TENDENCY, acknowledge='partial COUNT is a magnitude here, not a detection')}")

    print("\nEXISTENCE_SELF_TEST_PASS — a detection-shaped median is refused, the "
          "question type has no default, and the honest admission is one argument.")
