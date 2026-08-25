"""Queued threads and their disposition, machine-checked. A compact kills threads.

WHY THIS EXISTS
---------------
On 2026-08-24 a ledger check asked after two ERB cells queued before a context
compact: the marker validation and the reopened linearisation. Both had in fact
been RUN and banked — `brocot_marker_erb_gate.json` (MAY_SAY_STRUCTURAL_EVENT_
ONLY, marker separation 0.67x a 1-cent detune) and `brocot_linear_morph_erb.json`
(NOT_LINEARISABLE_ON_ERB, reduction 0.985x against a 3x bar). Nothing was lost.

But nothing was VISIBLE either. The results existed in the repo and could not be
seen from outside it, so a reasonable reader concluded a thread had been dropped.
That is this repo's recorded failure mode in its purest form: knowledge that does
not propagate is knowledge filed where it cannot fire. "I will remember it" is
not a mechanism; a summary is not a mechanism; both were tried.

So disposition becomes data, on the `verify_pending_debt` pattern:

    QUEUED   asked for, not yet run — printed on EVERY green board
    LANDED   run and banked, with the artifact and verdict named and CHECKED
    DROPPED  deliberately not doing it, with the reason recorded

A LANDED entry whose artifact is missing, or whose recorded verdict no longer
matches the artifact, FAILS the board. That is what stops this file drifting
into the decorative changelog every such file becomes.
"""
import json
import os

QUEUED, LANDED, DROPPED = "QUEUED", "LANDED", "DROPPED"

# id, status, one-line request, artifact (LANDED only), verdict (LANDED only)
ENTRIES = [
    dict(id="erb-marker-gate", status=LANDED,
         request="validate the coincidence markers in the ERB coordinate "
                 "before the display ships",
         artifact="cross_substrate/brocot_marker_erb_gate.json",
         verdict="MAY_SAY_STRUCTURAL_EVENT_ONLY",
         note="separation 16.1x on ERB but only 0.67x a 1-cent detune, so the "
              "caption is gated to structural events and carries no audibility "
              "claim"),
    dict(id="erb-linearisation", status=LANDED,
         request="reopened linearisation: arc-length reparameterisation on the "
                 "ERB coordinate against the same 3x bar",
         artifact="cross_substrate/brocot_linear_morph_erb.json",
         verdict="NOT_LINEARISABLE_ON_ERB",
         note="reduction 0.985x against a 3x bar — the run that refuted the "
              "'not at set changes therefore continuous' inference"),
    dict(id="parent-100s", status=LANDED,
         request="promote the two empirical 100%s to theorems where they are "
                 "theorems, or state their population",
         artifact="cross_substrate/brocot_parent_theorem.json",
         verdict="P2_IS_A_THEOREM_ON_1_OVER_A_TO_A",
         note="P1 definitional; P2 proved via Lagrange + prefix-in-q, boundary "
              "at alpha outside (1/A, A) characterised as the carrier category"),
    dict(id="tie-lemma", status=LANDED,
         request="prove or bound the tie case left as 'empirical, n = 304' in "
                 "the parent theorem — an empirical 100% is not a resting place",
         artifact="cross_substrate/brocot_tie_lemma.json",
         verdict="TIE_CASE_IS_A_THEOREM",
         note="max(p,q) is strictly increasing in q, so the shipped tie-break "
              "selects the smallest-q minimiser and Lagrange applies; 545/545 "
              "over 546 ties, with three decoy tie-breaks firing at 0%/2.4%/2.4%"),
    dict(id="amplitude-event-layer", status=QUEUED,
         request="the ~70% of large timbral jumps that are amplitude-threshold "
                 "crossings — an amplitude scan the horizon cannot supply; "
                 "needed for a complete EVENT layer",
         note="scoped out of the shipped display, which says structural events "
              "only. Open by choice, not by oversight."),
    dict(id="heard-as-listening", status=QUEUED,
         request="validate 'heard as a detuned X' by ERB or by listening; until "
                 "then the display says 'nearest ringing ratio + beat rate'",
         note="the beat coordinate crosses perceptual regimes within one region "
              "(5.5 Hz fusion-with-beating vs 31 Hz separation), so the "
              "perceptual wording is not carried by the structural evidence"),
]


def load(root):
    out = []
    for e in ENTRIES:
        e = dict(e)
        if e["status"] == LANDED:
            p = os.path.join(root, e["artifact"])
            e["artifact_exists"] = os.path.exists(p)
            e["verdict_matches"] = False
            if e["artifact_exists"]:
                try:
                    e["verdict_matches"] = (
                        json.load(open(p)).get("verdict") == e["verdict"])
                except Exception:                              # noqa: BLE001
                    pass
        out.append(e)
    return out


if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.abspath(__file__))
    for e in load(ROOT):
        mark = ("" if e["status"] != LANDED else
                "  OK" if e["verdict_matches"] else "  BROKEN")
        print(f"{e['status']:>8s}  {e['id']:<24s}{mark}")
