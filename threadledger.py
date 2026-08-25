"""Threads and their disposition, machine-checked. A compact kills threads.

NAMED threadledger, NOT queue: `queue` is a stdlib module, and the repo root
precedes stdlib on sys.path, so a file called queue.py here broke
`concurrent.futures` for every script run from the root. Found by adversarial
review, demonstrated, fixed. A ledger for visibility that silently breaks
unrelated imports is not a good trade.

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
         verdict="TIE_CASE_IS_A_THEOREM_WHERE_IT_NAMES_A_RATIONAL",
         note="max(p,q) is strictly increasing in q, so the shipped tie-break "
              "selects the smallest-q minimiser and Lagrange applies; 545/545 "
              "of the 546 ties WHERE IT NAMES A RATIONAL -- the remaining 1 "
              "selects a2 = 0 (alpha = 7, A = 6) and names none, which is why "
              "'unconditional in alpha > 0' was withdrawn. The three decoy "
              "tie-breaks select non-convergents 100%/97.6%/97.6% of the time "
              "(their CONVERGENT rates are 0%/2.4%/2.4%)"),
    dict(id="map-fusion-density", status=LANDED,
         request="does a pairwise horizon field earn a graph dimension, or is "
                 "it a column the map already has under another name?",
         artifact="cross_substrate/brocot_map_dimension.json",
         verdict="EARNS_A_DIMENSION",
         note="fusion density: 260 distinct values, max |Spearman| 0.042 "
              "against every existing field, resolves within families. Ships "
              "as a FUSION DENSITY readout, not a beat readout -- only 7.0% of "
              "nodes beat in (0,20) Hz because some pair almost always fuses "
              "at N=16"),
    dict(id="asymmetric-corollary", status=LANDED,
         request="prove and verify the asymmetric horizon the fusion-density "
                 "column rests on, to the symmetric theorem's standard",
         artifact="cross_substrate/brocot_asymmetric_horizon.json",
         verdict="ASYMMETRIC_COROLLARY_VERIFIED",
         note="4784/4784 exact across 16 index pairs, witness re-derived "
              "against two boxes at 1250 reachable triples, relabelling "
              "invariant, 234 flips across 78 distinct ratios when the higher "
              "index moves (was banked as '468 ratios' -- an ordered-pair "
              "double count read as a ratio count; corrected)"),
    dict(id="suggest-census", status=LANDED,
         request="measure CoherenceSuggest's wrong-criterion rate before "
                 "repairing it, so the repair has a before",
         artifact="cross_substrate/brocot_suggest_census.json",
         verdict="CRITERION_WRONG_IN_PRACTICE",
         note="97.5% of the enumerated candidate pool at I=0.9; the near-unity "
              "stratum is WORSE at 99.7-100%. Owed on this evidence: a "
              "docstring rewrite. NOT owed: a ranking rewrite, until "
              "Coherence.h's actual score is censused separately"),
    dict(id="index-routing", status=LANDED,
         request="does A4's swap non-invariance reach the shipped column, and "
                 "is the map conditioned on a routing convention?",
         artifact="cross_substrate/brocot_index_routing.json",
         verdict="COLUMN_IS_CONDITIONED_ON_ROUTING",
         note="SEALED head reported unchanged; the amended reading is "
              "ORDER_DEPENDENT_BUT_UNBIASED. 6.1% of 1.14M pairs swap-sensitive "
              "and 64.0% of nodes would change, but alignment is 0.4995 +/- "
              "0.0037 -- no convention. The head's NAME presumed the mechanism "
              "arm's conclusion, a limit now recorded in verdictlattice"),
    dict(id="suggest-docstring", status=DROPPED,
         request="rewrite CoherenceSuggest's docstring: correct criterion, cite "
                 "the census, leave the score's status explicitly open",
         artifact="cross_substrate/brocot_suggest_census.json",
         verdict="CRITERION_WRONG_IN_PRACTICE",
         note="the deliverable is an .h edit in the BROCOT repo, which this "
              "ledger cannot verify — its `artifact` pointed at another "
              "thread's JSON, so verdict_matches was trivially green and could "
              "never detect the edit reverting. An inert row inside a 'n/n "
              "verify' tally. Reclassified DROPPED rather than left as a false "
              "LANDED; the edit is real and lives at brocot "
              "source/audio/CoherenceSuggest.h."),
    dict(id="suggest-score-census", status=DROPPED,
         request="census Coherence.h's actual score, not just the docstring's "
                 "criterion — does the shipped RANKING inherit the defect?",
         note="brocot_suggest_census deliberately did not call the score. The "
              "stated justification is false at 97.5-100% of candidates, but "
              "whether the topN a user sees is correspondingly wrong depends "
              "on what coherence computes, which may be a softer notion. "
              "Without this, 'the engine is broken' is an overclaim and only "
              "'the engine's justification is false' is supported. DROPPED "
              "2026-08-25: superseded by score-census, which answered exactly "
              "this. The board showed both -- one OPEN and one LANDED on the "
              "same question -- which is the failure this ledger exists to "
              "prevent, committed in the ledger."),
    dict(id="score-census", status=LANDED,
         request="does the shipped ranking inherit CoherenceSuggest's false "
                 "criterion, or does its 12-cent binning put it outside the "
                 "horizon's jurisdiction?",
         artifact="cross_substrate/brocot_suggest_score_census.json",
         verdict="RANKING_DOES_NOT_DEPEND_ON_EXACT_COINCIDENCE",
         note="SEALED head reported unchanged; the roles were mis-assigned and "
              "the amended head is RANKING_PARTLY_DEPENDS_ON_EXACT_COINCIDENCE. "
              "64.9% of the score's shared energy is EXACTLY coincident, so the "
              "horizon does govern it; 57.7% of top-1 suggestions cannot "
              "coincide with anything in the patch; filter Jaccard 0.329. A "
              "reachability filter is warranted and needs current's indices"),
    dict(id="truncated-butterfly", status=LANDED,
         request="re-test D-section-0 with the horizon as a CUTOFF, using "
                 "index-dependence as the discriminating arm",
         artifact="cross_substrate/brocot_truncated_butterfly.json",
         verdict="MAP_TRACKS_THE_TRUNCATION",
         note="WEAK AND ONE-FIELD. matched-mismatched +0.0434 on crit, "
              "permutation p = 0.005 post-hoc, but matched 0.137 vs plain q "
              "0.111 there while q dominates tonal (0.217 vs 0.090) and dense "
              "(0.309 vs 0.083). Suggestive, NOT a shippable layer under D1; "
              "D0 stays falsified. H2 was inert as first written and is left "
              "MISSED after replacement rather than repaired into a pass"),
    dict(id="butterfly-prior-art", status=DROPPED,
         request="is a bounded-denominator / truncated Hofstadter butterfly a "
                 "known object, and is the Arnold-tongue analogy formal?",
         artifact="cross_substrate/brocot_truncated_butterfly.json",
         verdict="MAP_TRACKS_THE_TRUNCATION",
         note="SAME INERT-ROW PROBLEM as suggest-docstring: the deliverable is "
              "brocot phase3/butterfly.md, which this ledger cannot verify, and "
              "its artifact pointed at another thread's JSON. Reclassified. "
              "Content: no named truncated "
              "object; the literature's analogue is exponential gap-width decay "
              "in |label| (arXiv:1712.04700), structurally like our epsilon "
              "floor. NO Hofstadter<->FM link exists anywhere -- open "
              "territory. CORRECTION: Bjerklov-Jager's AMO<->mode-locking "
              "bridge uses ENERGY as the tongue parameter, not flux, so the "
              "queued Arnold-tongue identification is WITHDRAWN"),
    dict(id="suggest-reachability-filter", status=QUEUED,
         request="pass current's indices into suggestExtensions and filter "
                 "candidates by the asymmetric horizon; measure the change in "
                 "user-visible top-4 against the censused before",
         note="warranted by score-census: Jaccard 0.329 means the filter "
              "materially changes what is shown. Blocked on the signature "
              "change -- suggestExtensions currently receives only newIndex"),
    dict(id="hofstadter-horizon-cutoff", status=DROPPED,
         request="re-test the butterfly correspondence with the horizon as its "
                 "CUTOFF: BROCOT-SPEC D§0 was falsified partly because gap "
                 "prominence was 'fully shadowed by plain Farey simplicity q', "
                 "and the horizon supplies the bounded-denominator structure "
                 "that distinguishes the two",
         note="the butterfly is a q -> infinity object; the instrument only "
              "ever resolves q <= A = 2*order_bound(I), so the object to "
              "compare against is the butterfly TRUNCATED at the horizon, "
              "which has finitely many bands and MOVES with the depth control. "
              "Design constraint from D§1: nothing ships as a visual layer "
              "unless it beats a shuffle null AND an effect-size floor AND the "
              "trivial baselines -- and q is the baseline that shadowed it "
              "last time, so the sealed test must show the horizon-truncated "
              "predictor separating FROM q, not merely correlating with the "
              "geometry. Needs the asymmetric-horizon extension already used "
              "in brocot_map_dimension. SHARPENED 2026-08-25: the "
              "discriminating arm is INDEX-DEPENDENCE, because plain q is "
              "STATIC and the horizon-truncated predictor moves with I by "
              "construction. So the sealed test is not a single-I correlation "
              "contest -- which is what plain q won last time -- but whether "
              "the map geometry TRACKS THE TRUNCATION as I varies: pre-register "
              "which features appear or vanish, and at which I the theorem says "
              "they cross. No static predictor can match a moving target as "
              "anything but coincidence, so the baseline is ruled out by its "
              "own constancy rather than by out-correlating it. DROPPED "
              "2026-08-25: superseded by truncated-butterfly, which ran exactly "
              "this design. Result was a weak one-field positive, not a "
              "shippable layer. Reopen only with a mechanism for why crit "
              "responds and tonal/dense do not."),
    dict(id="audible-horizon", status=LANDED,
         request="is the epsilon = 1e-3 horizon audible, or does it classify "
                 "using partials no listener could hear?",
         artifact="cross_substrate/brocot_audible_horizon.json",
         verdict="EPS_HORIZON_OVERSTATES_AUDIBILITY",
         note="witness partials sit -78 to -92 dB below the strongest partial "
              "at the epsilon horizon. At I=0.9 the 13 structural regions are "
              "3 audible at -40 dB and 5 at -60 dB. E4 FAILED: the count moves "
              "40% between those floors, so it is not floor-free. A '17 dB per "
              "rung' law I asserted in a commit message was RETRACTED the same "
              "session -- read off six sorted rows, contradicted by the full "
              "series"),
    dict(id="audible-horizon-calibration", status=QUEUED,
         request="fix the audibility floor empirically instead of picking it: "
                 "(A) excitation-pattern masked-threshold census over the 508 "
                 "cells and the asymmetric grid; (B) 2AFC detune-twin "
                 "discrimination using the instrument's own setDetuneCents, "
                 "adaptive staircase on max(p,q), >=1 s sustain",
         note="the -40/-60 dB split is a guess and the 40% swing between them "
              "is why it must not stay one. B also discharges heard-as-"
              "listening: below the audible horizon the detuned twin BEATS "
              "where the exact one fuses, which is a dynamic cue in the regime "
              "the marker gate could not reach. Sustain length is load-bearing "
              "-- separations of 1-24 Hz need 40 ms to 1 s to exist at all, so "
              "a staccato stimulus cannot carry the category"),
    dict(id="coherence-model-gap", status=QUEUED,
         request="Coherence.h models the spectrum as a SUM of independent combs "
                 "(partials only at |1 +/- m*r|, energy J_m(I)^2) when "
                 "simultaneous modulators produce a PRODUCT lattice at "
                 "1 + n1*r1 + n2*r2 with energy J_n1*J_n2. Measure what the "
                 "meter misses.",
         note="raised by independent review. The omitted cross-partials carry "
              "(1 - J0(I)^2)^2 of the energy: ~12% at I=0.9, ~55% at 1.5, ~90% "
              "at 2.0 -- so at I>=1.5 the meter scores a minority of the "
              "spectrum. Distinct from the CoherenceSuggest criterion defect: "
              "that one is the docstring, this one is the score's generative "
              "model. NOT yet independently verified by me -- the (1-J0^2)^2 "
              "figure reproduces arithmetically but the claim that the comb "
              "model misses the theorem's witnesses needs checking, since "
              "comb-comb overlaps ARE lattice coincidences with both "
              "coordinates nonzero"),
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
              "perceptual wording is not carried by the structural evidence. "
              "SHARPENED 2026-08-25: brocot_marker_erb_gate measured events "
              "STATICALLY, at a point, and found them sharply resolved (16.13x "
              "separation in ERB, better than u's 2.11x) but at 0.67x a 1-cent "
              "detune -- below the floor of noticing. The listening cell must "
              "seal the DYNAMIC question instead: a coincidence forming as the "
              "player sweeps through it may register in transition at "
              "magnitudes that are static-invisible. Re-asking the static "
              "question would only reproduce a gate that has already fired."),
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
