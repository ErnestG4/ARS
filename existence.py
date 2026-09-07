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

THE FAMILY GENERALISES — SECOND MEMBER, 2026-08-24
---------------------------------------------------
The same category error appeared again in a different costume. A verdict lattice
keyed `SURVIVES_EXTENSION` on ONE threshold at ONE value of N — "> 50% at N = 4" —
and read 44.5%, returning a label that contradicted its own table, because the
series ran 5% -> 17% -> 45% -> 66%. The measured quantity was a TREND and it was
scored with a scalar sampled at an arbitrary point.

So the type is over QUESTION SHAPES, not just over existence:

    EXISTENCE         does ANY case fire        -> count, any, witness
    CENTRAL_TENDENCY  what is the typical case  -> median, mean, spread
    TREND             which way does it go      -> direction, endpoints, crossing

A trend answered by a scalar at one sample point is the same defect as an
existence answered by a median: right number, wrong question shape.

FOURTH MEMBER, 2026-08-28: PRESENCE ANSWERED BY A SHARE.
`brocot_modulation_cue` measured cue FRACTION -- a beat band's share of the
total exact-vs-twin difference -- and reported a small share as "the partials
are NOT IN THE SIGNAL AT ALL". They were: measured directly, every ratio carried
the cue at 21 to 101 dB above the envelope floor. A small share of a large
difference means the CONFOUND dominates, which is a statement about
attributability and says nothing about presence.

The claim lasted an hour and was overturned by its own redo. It was also MORE
confident than the claim it replaced -- "not present" was offered as stronger
than "masked below threshold" precisely because it needs no perceptual model.
A share can be small for two reasons and only one of them is absence.

    EXISTENCE         does ANY case fire        -> count, any, witness
    CENTRAL_TENDENCY  what is the typical case  -> median, mean, spread
    TREND             which way does it go      -> direction, endpoints, crossing
    PRESENCE          is the thing THERE        -> measure IT, not its share of
                                                   something else

WHAT THIS CANNOT DO, stated plainly: it cannot know your intent. A field named
`slope` that is secretly a detection count passes as central tendency. The name
heuristic is a syntactic check on a semantic property — the same honest limit
`detector_spec` carries. What does the work is that the common case, a
detection-shaped name, now has to be argued for out loud.
"""

# ── LITERATURE ────────────────────────────────────────────────────────────────
# NOT SEARCHED. A sweep was run on 2026-09-06 and its author RETRACTED the
# result for this module as FABRICATED: verbatim quotations, page ranges and
# explicit "Opened"/"Extracted" verification labels were generated from recall
# for sources never retrieved. Discarded in full rather than triaged, because
# a source that was labelled verified and was not cannot be partially trusted.
LITERATURE = dict(
    status="PARTIAL",
    note="THE HONEST SWEEP FOUND THE OPPOSITE OF THE FABRICATED ONE. The "
         "retracted 2026-09-06 report concluded the quantifier axis was "
         "unoccupied -- the conclusion this repo most wanted. The re-sweep "
         "(same day, primary text fetched for every claim) found the axis "
         "OCCUPIED under at least three names in psychology alone, plus a "
         "regulation-grade frame and an exact formal-methods dual. The DEFECT "
         "is named. The REPAIR is named. What is not found anywhere searched "
         "is the ENFORCEMENT: a construction-time type system that classifies "
         "the question and RAISES on a mismatched statistic.",
    anchors=[
        "McManus, Young & Sweetman, Adv. Methods Pract. Psychol. Sci. (AMPPS) "
        "2023: 'the group-to-person generalizability problem'. Verified from "
        "fetched full text: group-level claims can 'describe only a "
        "(sometimes tiny) minority of participants', and simulated group "
        "effects 'can emerge without a single participant's responses "
        "matching' -- an aggregate asserting what NO unit exhibits.",
        "Speelman & McGann 2020 (Front. Psychol., PMC7711086), title verbatim: "
        "'Statements About the Pervasiveness of Behavior Require Data About "
        "the Pervasiveness of Behavior' -- the title IS this module's rule. "
        "They coined 'the ergodic fallacy' for it (coinage confirmed in "
        "Collabra 2024, 10.1525/collabra.92888, which measured the fallacy's "
        "prevalence across a year of three journals). Verified text: 'it is "
        "not the fashion to report the number of people in the study that "
        "showed the effect', and the repair 'will often require that a "
        "precise criterion is defined whereby we can determine if the "
        "behavior has been observed, or not' -- an existence statistic, as "
        "exhortation.",
        "Fisher, Medaglia & Jeronimus, PNAS 2018 (PMC6142277): 'Lack of "
        "group-to-individual generalizability is a threat to human subjects "
        "research.' Only for ERGODIC processes do group-level inferences "
        "transfer to individuals; measured intraindividual variance 2.09-4x "
        "the interindividual estimate across six samples. Lineage: Molenaar "
        "2004.",
        "ICH E9(R1) addendum (database.ich.org official PDF, "
        "EMA/CHMP/ICH/436221/2017), fetched: 'Central questions ... are to "
        "establish the EXISTENCE, and to estimate the MAGNITUDE, of "
        "treatment effects' -- the framework itself splits this module's "
        "axis -- and 'a population-level summary for the variable should be "
        "specified' is a MANDATORY estimand attribute (A.3.3): the summary "
        "statistic is a declared property of the question, chosen in advance.",
        "Formal-methods dual, verified from two independent course texts "
        "(Willemse, TU/e 2IW55, explicitly 'Chapter 6.3, 6.4' of Clarke, "
        "Grumberg & Peled, Model Checking, MIT Press 1999; Chechik, Toronto "
        "csc2108): 'A formula with a universal path quantifier has a "
        "counterexample consisting of one trace; a formula with an "
        "existential path quantifier has a WITNESS consisting of one trace.' "
        "An existential claim is discharged by exhibiting one trace, never by "
        "an aggregate. (CGP book itself not fetched; cited via both courses.)",
        "Kimball, JASA 52(278), 1957, Type III error -- 'the right answer to "
        "the wrong problem' -- verified against primary text by a different "
        "agent in the earlier sweep; kept. The container is too large to be "
        "actionable alone.",
        "Kravitz, Duan & Braslow's RCT-side statement (PMC2953542), fetched: "
        "if 50% of patients improve, 'an equally valid inference is that ALL "
        "of the patients' respond half the time -- the group summary "
        "underdetermines the per-unit distribution entirely.",
    ],
    ours="the enforcement: summarise() classifies the QUESTION (EXISTENCE / "
         "CENTRAL_TENDENCY / TREND / PRESENCE) and raises "
         "WrongStatisticForQuestion at construction time. The literature "
         "names the defect and pleads; nothing found REFUSES. Also the "
         "application to per-realization gates on point-process substrates "
         "(estimand_matches_decision).",
    searched="2026-09-06 re-sweep after the fabricated report was struck. "
             "Method: 2 semantic queries (Exa), then primary text fetched for "
             "EVERY anchored claim -- ICH PDF from database.ich.org, PMC full "
             "texts, both course PDFs; quotes above are from fetched text "
             "only. Bound: psychology/clinical/formal-methods reached; "
             "econometrics, measurement theory, reliability engineering NOT "
             "specifically swept. What would upgrade PARTIAL->NAMED: finding "
             "a refusing implementation (type system, linter, estimand "
             "checker) that enforces question-statistic match; none surfaced.",
)

import re

PRESENCE = "PRESENCE"
EXISTENCE = "EXISTENCE"
CENTRAL_TENDENCY = "CENTRAL_TENDENCY"
TREND = "TREND"
_QUESTIONS = (EXISTENCE, CENTRAL_TENDENCY, TREND, PRESENCE)

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

    if question is PRESENCE or question == PRESENCE:
        # A presence question is answered by measuring the thing against its own
        # noise floor, never by its share of a total. `values` must therefore be
        # the quantity itself; a ratio-valued input is refused.
        if acknowledge is None and all(0.0 <= v <= 1.0 for v in vals if v is not None):
            raise WrongStatisticForQuestion(
                f"'{name}': every value lies in [0, 1], which is what a SHARE "
                "looks like. A presence question is answered by measuring the "
                "quantity against its own floor, not by its fraction of a "
                "total -- a small share can mean absence OR a dominant "
                "confound, and only one of those is absence. Measured once, "
                "cost an hour and a retraction.\n    Pass the quantity itself, "
                "or acknowledge='<why a fraction IS the presence measure here>'.")
        return dict(question=PRESENCE, n=len(vals),
                    n_present=sum(1 for v in vals if v),
                    minimum=(min(vals) if vals else None),
                    maximum=(max(vals) if vals else None),
                    acknowledged=acknowledge)

    if question is TREND or question == TREND:
        if len(vals) < 3:
            raise WrongStatisticForQuestion(
                f"'{name}': a TREND needs at least 3 points; got {len(vals)}. "
                "Two points are a difference, not a direction.")
        up = all(b >= a for a, b in zip(vals, vals[1:]))
        down = all(b <= a for a, b in zip(vals, vals[1:]))
        cross = None
        if acknowledge is not None:
            try:
                thr = float(acknowledge)
                for i, v in enumerate(vals):
                    if (up and v >= thr) or (down and v <= thr):
                        cross = i
                        break
            except (TypeError, ValueError):
                thr = None
        return dict(question=TREND, n=len(vals), first=vals[0], last=vals[-1],
                    monotone=(up or down),
                    direction=("rising" if up and not down else
                               "falling" if down and not up else "non-monotone"),
                    ratio=(vals[-1] / vals[0] if vals[0] else None),
                    crossing_index=cross)

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

    print("\n--- red path 3: the real dissolution series, read as a scalar ---")
    series=[0.047,0.173,0.445,0.659]      # above-horizon coincidence rate, N=2..5
    print(f"    series {series}  (N = 2,3,4,5)")
    print(f"    scalar read at N=4: {series[2]:.3f} < 0.50  ->  verdict 'SURVIVES'")
    tr=summarise("above_rate",series,TREND,acknowledge=0.5)
    print(f"    TREND: {tr['direction']}, monotone={tr['monotone']}, "
          f"{tr['first']:.3f} -> {tr['last']:.3f} ({tr['ratio']:.1f}x), "
          f"crosses 0.5 at index {tr['crossing_index']} (N={2+tr['crossing_index']})")
    print("    the trend answers the question the scalar got wrong")
    try:
        summarise("above_rate",[0.047,0.659],TREND)
        raise SystemExit("RED PATH FAILED: a 2-point trend was accepted")
    except WrongStatisticForQuestion as e:
        print(f"    2-point trend raised: {str(e)[:72]}...")

    print("\n--- green path: a detection name, average argued for out loud ---")
    print(f"    {summarise('n_partials', [31, 31, 30, 29], CENTRAL_TENDENCY, acknowledge='partial COUNT is a magnitude here, not a detection')}")

    print("\n--- red path 4 · a presence question answered by a share ---")
    try:
        summarise("cue_present", [0.000, 0.003, 0.816, 0.994, 1.000], PRESENCE)
        raise SystemExit("RED PATH FAILED: a share was accepted as presence")
    except WrongStatisticForQuestion as e:
        print(f"    raised as required: {str(e)[:92]}...")
    print("    the real values that caused the retraction: cue FRACTION, read")
    print("    as absence, while the measured cue sat 21-101 dB above the floor")
    print(f"    {summarise('cue_snr_db', [21.3, 24.4, 51.7, 101.0], PRESENCE)}")

    print("\nEXISTENCE_SELF_TEST_PASS — a detection-shaped median is refused, the "
          "question type has no default, a share cannot answer a presence question, and "
          "the honest admission is one argument.")
