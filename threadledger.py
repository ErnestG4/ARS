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

# WARRANT STALENESS, added 2026-08-26 after the second instance.
#
# A queued row's WARRANT is a finding with a timestamp: "warranted, not tidy"
# was minted against a world in which coincidence-reachability and audibility
# were the same thing. Stage A severed them, and the action inherited a premise
# change in silence. Twice now:
#
#   hofstadter-horizon-cutoff   superseded by truncated-butterfly running its
#                               own design; dropped only because a human noticed
#   suggest-reachability-filter warranted by score-census, which predated
#                               masked-horizon-stage-a; a C++ signature change
#                               was one step from shipping on a dead premise
#
# WARRANTS CARRY A LAYER, added the same week. A row's warrants are not all the
# same KIND of claim: some are theorem-grade and unconditional, others are
# measurements sitting downstream of a parameter that is not yet settled. A row
# whose warrants are listed flat invites the reader to treat the weakest as
# though it had the strength of the strongest -- which is exactly the
# compression COINCIDENCE-HORIZON now warns about for "parity can't matter".
# So a warrant is (artifact, verdict_at_minting, layer), and the layer is
# printed beside it. Two-tuples are still accepted and shown as "unlabelled",
# because a missing label should be visible rather than assumed benign.
#
# FRAMING DEATH, added 2026-08-28. WARRANT_STALE compares VERDICTS, and that
# misses the case that actually arrived: a warrant whose verdict is unchanged
# and whose MEANING is dead. brocot_masked_horizon still says
# MASKING_GIVES_A_DERIVED_HORIZON and the measurement behind it is untouched --
# but "audible" was reclassified from a property of the spectrum to a property
# of a model with a criterion in it, so "Stage B will pin sigma" was always
# "Stage B fits a parameter for one listener at one attention level". The
# verdict did not move; the question it was answering did.
#
# A row may therefore declare `framing_dead`: (artifact, reason) pairs that
# force WARRANT_STALE regardless of verdict, clearable only by naming the
# artifact in `warrant_reviewed`. Semantic staleness needs a human; the flag
# just refuses to let it pass unnoticed.
#
# The queue is exactly where premises age while actions wait, so a QUEUED row
# may name the artifacts its warrant rests on AND the verdict each carried when
# the row was minted. If a warrant artifact's verdict has since MOVED, the row
# is WARRANT_STALE and the board FAILS until it is re-adjudicated -- which means
# recording the new verdict in `warrant_reviewed`, i.e. saying out loud that the
# action still makes sense under the changed premise. Seeing staleness is not
# enough; the bite is having to re-affirm.

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
         verdict="ORDER_DEPENDENT_NO_CONVENTION_DETECTED",
         note="RE-POINTED 2026-09-02 to the AMENDED head (the seal, "
              "COLUMN_IS_CONDITIONED_ON_ROUTING, is preserved in the artifact's "
              "`verdict` key and is what was pre-registered). The amended reading is "
              "ORDER_DEPENDENT_NO_CONVENTION_DETECTED (was 'BUT_UNBIASED' -- a "
              "null non-rejection cannot assert absence, only bound it). "
              "6.1% of 1.12M unequal-index pairs swap-sensitive "
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
         verdict="RANKING_PARTLY_DEPENDS_ON_EXACT_COINCIDENCE",
         note="RE-POINTED 2026-09-02 to the AMENDED head (seal preserved in the "
              "artifact). The roles were mis-assigned and the amended head is "
              "RANKING_PARTLY_DEPENDS_ON_EXACT_COINCIDENCE -- the NEGATION of the "
              "sealed one, and the most consequential of the six amendments the "
              "ledger was blind to, because two other rows warrant off it. "
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
    dict(id="filter-worth-it", status=LANDED,
         request="given Stage A, does the reachability filter improve what a "
                 "player HEARS, or optimise an inaudible property?",
         artifact="cross_substrate/brocot_filter_worth_it.json",
         verdict="FILTER_OPTIMISES_AN_INAUDIBLE_PROPERTY",
         note="sigma-CONDITIONAL and the declared sweep made it visible. At the "
              "sealed primary (sigma = ERB) the audible gain is +2.1% against a "
              "0.10 bar; at sigma = ERB/2.5 it is +19.9%. sigma = ERB "
              "over-masks and so understates the benefit. Settled regardless: "
              "the filter changes what is shown (Jaccard 0.335) and the "
              "predicate is exactly right (0 disagreements vs brute force over "
              "5000+ pairs). What is unsettled is whether the consequence is "
              "audible"),
    dict(id="suggest-reachability-filter", status=QUEUED,
         framing_dead=[("cross_substrate/brocot_masked_horizon.json",
                        "'audible' was reclassified from a property of the "
                        "spectrum to a property of a model with a criterion in "
                        "it. There is no perceptual wall, so 'Stage B pins "
                        "sigma' was always 'Stage B fits a parameter for one "
                        "listener at one attention level'. Re-frame the "
                        "question before acting on this warrant.")],
         warrant=[("cross_substrate/brocot_suggest_score_census.json",
                   "RANKING_DOES_NOT_DEPEND_ON_EXACT_COINCIDENCE",
                   "STRUCTURAL/the score's exact-coincidence share"),
                  ("cross_substrate/brocot_filter_worth_it.json",
                   "FILTER_OPTIMISES_AN_INAUDIBLE_PROPERTY",
                   "AUDIBILITY/sigma-conditional")],
         warrant_reviewed=[("cross_substrate/brocot_masked_horizon.json",
                            "MASKING_GIVES_A_DERIVED_HORIZON"),
                           # RE-ADJUDICATED 2026-09-02, and the direction matters:
                           # the structural warrant did not weaken, it REVERSED
                           # TOWARD the action. Minted as "the ranking does not
                           # depend on exact coincidence" (i.e. the horizon has no
                           # jurisdiction here), the artifact now says it PARTLY
                           # does -- 64.9% of the score's shared energy is exactly
                           # coincident. So the structural case for filtering is
                           # STRONGER than when this row was parked, and the row
                           # stays QUEUED for two unrelated reasons only: the C++
                           # signature change, and the fact that its AUDIBILITY
                           # warrant is framing-dead. Recorded rather than acted
                           # on -- a warrant that moves in your favour is still a
                           # premise change, and gets the same re-adjudication as
                           # one that moves against you.
                           ("cross_substrate/brocot_suggest_score_census.json",
                            "RANKING_PARTLY_DEPENDS_ON_EXACT_COINCIDENCE")],
         request="RE-FRAMED 2026-08-28. The decision was parked on 'Stage B "
                 "pins sigma', which is not a thing that can happen. Re-posed: "
                 "the filter's benefit is +2.1% at sigma = ERB and +19.9% at "
                 "ERB/2.5, so state the DECISION as a function of criterion and "
                 "let a human choose the operating point, rather than waiting "
                 "for a measurement that cannot arrive. Still blocked on the "
                 "signature change either way. Superseded ask: pass current's "
                 "indices into suggestExtensions and filter "
                 "candidates by the asymmetric horizon; measure the change in "
                 "user-visible top-4 against the censused before",
         note="WARRANT DOWNGRADED 2026-08-26 by filter-worth-it. The row read "
              "'warranted, not tidy' on a census that predated Stage A, and "
              "would have shipped a C++ change on a warrant that no longer "
              "stands alone: at the conservative filter width the filter "
              "changes what is SHOWN without changing what is HEARD. Now "
              "blocked on Stage B (the listening test), which settles the "
              "auditory filter width the decision hinges on -- the same "
              "measurement audible-horizon-calibration waits for. Also still "
              "blocked on the signature change: suggestExtensions receives "
              "only newIndex and the filter needs current's indices."),
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
         framing_dead=[("cross_substrate/brocot_masked_horizon.json",
                        "'audible' was reclassified from a property of the "
                        "spectrum to a property of a model with a criterion in "
                        "it. There is no perceptual wall, so 'Stage B pins "
                        "sigma' was always 'Stage B fits a parameter for one "
                        "listener at one attention level'. Re-frame the "
                        "question before acting on this warrant.")],
         warrant=[("cross_substrate/brocot_audible_horizon.json",
                   "EPS_HORIZON_OVERSTATES_AUDIBILITY",
                   "AUDIBILITY/chosen-floor, and its seal was vacuous"),
                  ("cross_substrate/brocot_masked_horizon.json",
                   "MASKING_GIVES_A_DERIVED_HORIZON",
                   "AUDIBILITY/sigma-conditional")],
         warrant_reviewed=[("cross_substrate/brocot_masked_horizon.json",
                            "MASKING_GIVES_A_DERIVED_HORIZON")],
         request="RE-FRAMED 2026-08-28 after the framing death. The old ask was "
                 "'fix the audibility floor empirically', which presumed a "
                 "floor exists to be fixed. It does not: detection has no wall, "
                 "so there is no sigma to pin. The question becomes AT WHAT "
                 "CRITERION DOES EACH CLAIM HOLD -- report the audible count as "
                 "a FUNCTION of criterion rather than a number, exactly as "
                 "audible counts already travel with their dB floor. That is "
                 "answerable without listeners and mostly already computed. "
                 "Superseded ask, kept for provenance: "
                 "(A) excitation-pattern masked-threshold census; (B) 2AFC "
                 "detune-twin discrimination using the instrument's own "
                 "setDetuneCents, adaptive staircase on max(p,q), >=1 s "
                 "sustain. (C) WAS MIS-SPECIFIED AND IS CORRECTED HERE. It "
                 "read 'RE-SEAL brocot_audible_horizon so exposure_audit's "
                 "refusal clears on its own merits'. That refusal CANNOT "
                 "clear: exposure_audit runs the cell as it stood at the "
                 "BASELINE COMMIT, which is frozen in history, so no present "
                 "edit can change what it does. The exposure is a permanent "
                 "historical fact and disclosure is its only honest treatment "
                 "-- which is what verify_exposure_window enforces. What CAN "
                 "be discharged is the QUESTION, and it already is: "
                 "brocot_masked_horizon asks it with a DERIVED floor and live "
                 "arms, and supersedes the chosen-floor cell. Cite the "
                 "successor, not the exposed cell.",
         note="the -40/-60 dB split is a guess and the 40% swing between them "
              "is why it must not stay one. B also discharges heard-as-"
              "listening: below the audible horizon the detuned twin BEATS "
              "where the exact one fuses, which is a dynamic cue in the regime "
              "the marker gate could not reach. Sustain length is load-bearing "
              "-- separations of 1-24 Hz need 40 ms to 1 s to exist at all, so "
              "a staccato stimulus cannot carry the category. STAKES RAISED "
              "2026-08-26 by masked-horizon-stage-a: the masking model now "
              "predicts near-total inaudibility of STATIC merges (1 of 13 at "
              "I=0.9, and 1/1 is the one). That is a strong pre-registered "
              "target a listening session can cleanly confirm or embarrass, "
              "which is the best inheritance a listening test can get -- it "
              "arrives with a falsifiable prediction rather than an open "
              "question. Note the prediction is about MERGES; the detune-twin "
              "stimulus also probes the BEAT, where audibility was never in "
              "doubt, so the two arms must be scored separately. BUILT-IN "
              "CALIBRATION, which the arm-split hands over for free: the BEAT "
              "arm inherits the POSITIVE prediction (squarely audible, "
              "Hz-scale) and the MERGE arm the negative one. A listener who "
              "fails the beat arm is not hearing the stimulus, so the merge "
              "arm's null cannot quietly mean 'nobody was listening'. The beat "
              "arm is therefore a required pass-gate on each listener before "
              "their merge data counts, and that gate must be DECLARED in the "
              "seal rather than applied after seeing results -- a post-hoc "
              "listener exclusion is the oldest way to manufacture a null."),
    dict(id="masked-horizon-stage-a", status=LANDED,
         request="Stage A of audible-horizon-calibration: derive the floor from "
                 "masking instead of choosing it",
         artifact="cross_substrate/brocot_masked_horizon.json",
         verdict="MASKING_GIVES_A_DERIVED_HORIZON",
         note="at I=0.9 only the UNISON coincidence clears threshold (1 of 13; "
              "1/1 at +10.7 dB SMR, 3/4 at -21 to -34 dB). M2 decisive: 0% "
              "change across 12 dB of margin vs the chosen floor's 40%. M3 "
              "MISSED in the unpredicted direction -- masking is MORE "
              "restrictive than -40 dB, not less. Filter width was the untested "
              "knob: robust at I=0.9 (1-2 over a 4x change), NOT at I>=2 (0-6). "
              "Bounds EXACT-coincidence audibility only; the beat coordinate is "
              "dynamic and outside static masking's jurisdiction"),
    dict(id="offset-mechanism", status=LANDED,
         request="is the 0.0017 offset explained by the spacing scale, and do "
                 "offset markers locate anything?",
         artifact="cross_substrate/brocot_offset_mechanism.json",
         verdict="OFFSET_REAL_BUT_UNEXPLAINED",
         note="RE-POINTED 2026-09-02 to the AMENDED head (seal "
              "MARKERS_ARE_THE_WRONG_OBJECT preserved in the artifact). The spacing-scale hypothesis is FALSIFIED: CV ratio "
              "1.126 vs a shuffled null of 1.094, indistinguishable. O3's +16% "
              "gain was carpet-bombing -- predicted offsets beat random by "
              "+1.7% (sd 3.5%) and lose to simply widening the window "
              "(53.1% vs 55.6%). Exact markers + a 1.8e-3 window is the best "
              "event layer available, at 55.6%. The offset itself stands: "
              "median 0.0017 alpha, grid-stable, unexplained"),
    dict(id="the-0017-offset", status=DROPPED,
         warrant=[("cross_substrate/brocot_event_layer.json",
                   "RESIDUAL_SURVIVES_CLOSED_FORM",
                   "STRUCTURAL/measured offset, grid-stable")],
         request="what IS the 0.0017 offset? The median large jump sits that "
                 "far in alpha from the nearest closed-form marker, and the "
                 "distance percentiles are stable under grid doubling, so it "
                 "is a physical scale and not a sampling artifact",
         note="LEADING SUSPECT, to be sealed against: the jump may not be AT a "
              "coincidence but where a NEAR-coincidence enters the spacing "
              "distribution. u = I8_brody_q_unbounded(canonical_spacings(...)) "
              "is most sensitive to the SMALLEST spacings, so a pair at gap "
              "delta perturbs it hardest when delta is comparable to the "
              "smallest spacings already present -- which happens at some "
              "offset FROM the exact coincidence, not at it. That predicts the "
              "offset scales with the local spacing scale rather than being a "
              "constant, which is directly testable and would explain why four "
              "marker sets built on exact events all missed. If it holds, the "
              "event layer's markers are the wrong OBJECT rather than an "
              "incomplete list -- a different repair from adding a channel. "
              "DROPPED 2026-08-27: run as offset-mechanism, hypothesis "
              "falsified. Reopen only with a DIFFERENT mechanism -- the "
              "spacing scale is excluded, and any successor must carry an "
              "economy control, since this one's coverage arm turned out to be "
              "alpha-area rather than information."),
    dict(id="coherence-model-measured", status=LANDED,
         request="does the sum-of-combs model error reach the RANKING, or is it "
                 "documentation only?",
         artifact="cross_substrate/brocot_coherence_model.json",
         verdict="RANKING_EFFECT_UNRESOLVED",
         note="RE-POINTED 2026-09-02 to the AMENDED head (seal "
              "MODEL_GAP_IS_DOCUMENTATION_ONLY preserved in the artifact). Note the "
              "direction: the seal said the gap was DOCUMENTATION ONLY and the "
              "amendment says the ranking effect is UNRESOLVED, so the ledger was "
              "recording a closure where the artifact records an open question. M3 Jaccard 0.517 with 95% CI "
              "[0.468, 0.566] and the 0.50 bar INSIDE it, so the arm does not "
              "resolve either way; ~1170 cases would, 140 do not. M1 settles "
              "that the model IS wrong (12/55/90% omitted at I=0.9/1.5/2.0) so "
              "the docstring correction is owed on that alone. M4 missed: the "
              "relative difference FALLS with index while omitted energy rises, "
              "so a ratio was the wrong statistic for a tracking claim"),
    dict(id="coherence-model-gap", status=DROPPED,
         # RE-ADJUDICATED 2026-09-02: this row had ALREADY been marked reviewed
         # against this artifact -- at the artifact's SEALED verdict, which the
         # artifact had by then amended. A warrant_reviewed entry pinned to a
         # superseded value is worse than none: it silences the staleness check
         # while recording a review that never saw the current claim. The DROP
         # stands and is strengthened -- the note's own correction ("the horizon
         # DOES govern what the meter sees") is exactly what the amendment says.
         warrant_reviewed=[("cross_substrate/brocot_suggest_score_census.json",
                            "RANKING_PARTLY_DEPENDS_ON_EXACT_COINCIDENCE")],
         warrant=[("cross_substrate/brocot_suggest_score_census.json",
                   "RANKING_DOES_NOT_DEPEND_ON_EXACT_COINCIDENCE",
                   "STRUCTURAL/the meter's generative model")],
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
              "model. VERIFIED 2026-08-25: the (1-J0^2)^2 figure reproduces "
              "both by formula and by direct summation over the lattice "
              "(0.121/0.550/0.902 at I=0.9/1.5/2.0), and Coherence.h does "
              "enumerate only single-op sidebands |1 +/- m*r|. But the review's "
              "framing needs one correction: comb-comb overlaps ARE genuine "
              "lattice coincidences (a = m1, b = -m2, both nonzero), so the "
              "horizon DOES govern what the meter sees -- which is why "
              "score-census stands. The meter's defect is that it misses the "
              "OTHER coincidences, those involving cross-partials, so it "
              "under-counts sharing and is conservative rather than wrong"),
    dict(id="waveform-parity", status=LANDED,
         request="does Ian Fritz's even-harmonic suppression touch the horizon, "
                 "and what does a harmonic stack actually extend?",
         artifact="cross_substrate/brocot_waveform_parity.json",
         verdict="PARITY_IS_HORIZON_ORTHOGONAL",
         note="parity-matched stacks ([1,3,5] vs [1,2,6] vs [1,4,4]) ring on "
              "IDENTICAL sets, symmetric difference 0 -- only extent matters. "
              "Corrected the paper twice over: the extension is ASYMMETRIC (max "
              "numerator stays 8 = 2B for every wave; only the denominator "
              "grows) and the banked '8 -> 11' is brocot's ratio WINDOW, not "
              "the waveform -- widened down, triangle reaches q = 39 while sine "
              "stays at 8. A continuous even-suppression control is therefore "
              "SAFE to add: it moves no ratio in or out of the ringing set"),
    dict(id="double-pulse-sweep", status=LANDED,
         request="does Fritz's CONTINUOUS control touch the horizon, and is the "
                 "frozen oscilloscope trace the same structure as the horizon?",
         artifact="cross_substrate/brocot_double_pulse_sweep.json",
         verdict="SWEEP_IS_HORIZON_ORTHOGONAL",
         note="20 dB even-harmonic swing across beta, ZERO ratios moved in or "
              "out of the ringing set at any beta, ZERO coincidences audible at "
              "either filter width. Closes the gap the endpoint test left: an "
              "intermediate double pulse has saw's SUPPORT with different "
              "amplitudes, and support is all the predicate sees. SCOPE ARM: a "
              "carrier-triggered trace freezes on q carrier cycles (period-lock, "
              "denominator alone) while the horizon is max(p,q) vs 2B -- "
              "ringing ratios span 10 denominators and 5 of them (7-11) also "
              "appear among non-ringing, so the trace cannot indicate fusion"),
    dict(id="double-pulse-control", status=QUEUED,
         warrant=[("cross_substrate/brocot_waveform_parity.json",
                   "PARITY_IS_HORIZON_ORTHOGONAL", "STRUCTURAL/unconditional"),
                  ("cross_substrate/brocot_double_pulse_sweep.json",
                   "SWEEP_IS_HORIZON_ORTHOGONAL", "STRUCTURAL/unconditional"),
                  ("cross_substrate/brocot_masked_horizon.json",
                   "MASKING_GIVES_A_DERIVED_HORIZON", "AUDIBILITY/sigma-conditional")],
         request="add a continuous even-suppression control to Operator: a "
                 "beta knob mixing a pulse with its half-period-displaced "
                 "inverted copy, per Fritz's double-pulse construction",
         note="TWO WARRANTS AT TWO LAYERS, deliberately not flattened. The "
              "STRUCTURAL half is theorem-grade: the ringing predicate sees "
              "SUPPORT, never amplitude, so beta cannot move the ringing set "
              "for any pulse width, carrier or listener. The AUDIBILITY half "
              "-- 'no coincidence becomes audible at any beta' -- is a "
              "measurement under the masking model and is sigma-conditional "
              "like everything downstream of Stage A, so masked_horizon is "
              "listed as a warrant and WARRANT_STALE will force re-adjudication "
              "if Stage B moves it. The null held at BOTH widths tested so it "
              "very likely survives; the point is that it is flagged now rather "
              "than assumed later. Blocked on nothing measured -- the "
              "anti-aliasing a pulse train demands is engineering, not "
              "research."),
    dict(id="event-layer-closed-form", status=LANDED,
         request="is the residual 70% of timbral jumps really beyond closed "
                 "form, as four cells and a shipped document assert?",
         artifact="cross_substrate/brocot_event_layer.json",
         verdict="RESIDUAL_SURVIVES_CLOSED_FORM",
         note="tested direct + REFLECTED (q<=2B, p<=2B+2, never previously "
              "marked) + f_min crossings, all exactly enumerable. Union covers "
              "33.3% against a 60% bar; the reflected class adds EXACTLY 0. "
              "Median large jump sits 0.0017 in alpha from the nearest marker. "
              "The attribution is now a measurement. V4's miss was a window "
              "artifact -- grid-scaled window on a physical offset -- corrected "
              "to 1.11 under a fixed-alpha window"),
    dict(id="amplitude-event-layer", status=DROPPED,
         warrant_reviewed=[("cross_substrate/brocot_jump_display_v3.json",
                            "JUMPS_NOT_EXPLAINED")],
         warrant=[("cross_substrate/brocot_jump_display_v3.json",
                   "JUMPS_NOT_EXPLAINED", "STRUCTURAL/coverage of large jumps")],
         request="the ~70% of large timbral jumps that are amplitude-threshold "
                 "crossings — an amplitude scan the horizon cannot supply; "
                 "needed for a complete EVENT layer",
         note="scoped out of the shipped display, which says structural events "
              "only. Open by choice, not by oversight."),
    dict(id="stageb-protocol", status=LANDED,
         request="take Stage B as far as it goes without listeners: generate "
                 "the stimuli, seal the predictions, declare the gate",
         artifact="cross_substrate/brocot_stageb_protocol.json",
         verdict="PROTOCOL_SEALED_AWAITING_DATA",
         note="AMENDED TWICE PRE-DATA. (1) task was under-specified as 2AFC; "
              "now 3-interval odd-one-out, chance 1/3. (2) a listener's first "
              "impression broke the blinding and the positive control: the arms "
              "were categorically distinguishable by partial density, and "
              "alpha=1 is DEGENERATE (identical operators, 7-partial harmonic "
              "series) so B3 is WITHDRAWN and the gate is the only positive. "
              "This also corrected Stage A: ZERO non-degenerate ratios clear "
              "masking, at every index. Stimuli at 44.1 kHz / 2 s under "
              "cross_substrate/"
              "stageb_stimuli (gitignored, regenerate with the cell). MERGE "
              "arm: 7 below-horizon ratios, exact vs 6-cent twin, masking "
              "predicts only 1/1 discriminable. BEAT arm: 6 above-horizon "
              "ratios at 3-8 Hz separation, the per-listener >=90% inclusion "
              "gate. B4 is the number two dispositions wait on: the count "
              "discriminated above 60% pins sigma. NO audibility claim is made "
              "by this cell"),
    dict(id="heard-as-listening", status=QUEUED,
         framing_dead=[("cross_substrate/brocot_masked_horizon.json",
                        "'audible' was reclassified from a property of the "
                        "spectrum to a property of a model with a criterion in "
                        "it. There is no perceptual wall, so 'Stage B pins "
                        "sigma' was always 'Stage B fits a parameter for one "
                        "listener at one attention level'. Re-frame the "
                        "question before acting on this warrant.")],
         warrant=[("cross_substrate/brocot_marker_erb_gate.json",
                   "MAY_SAY_STRUCTURAL_EVENT_ONLY",
                   "AUDIBILITY/static, 0.67x a 1-cent detune"),
                  ("cross_substrate/brocot_masked_horizon.json",
                   "MASKING_GIVES_A_DERIVED_HORIZON",
                   "AUDIBILITY/sigma-conditional")],
         warrant_reviewed=[("cross_substrate/brocot_masked_horizon.json",
                            "MASKING_GIVES_A_DERIVED_HORIZON")],
         request="RE-FRAMED 2026-08-28, TWICE OVER. (i) The framing death: "
                 "'is it heard' has no criterion-free answer. (ii) The "
                 "stimulus cannot isolate fusion at all -- a ratio detune moves "
                 "every partial that depends on alpha (26 of 31 at 5/4), so "
                 "no ratio-detune contrast can attribute a discrimination to "
                 "the coincidence. BLOCKED ON A CONTRAST, not on listeners: "
                 "until someone finds a manipulation that splits the witness "
                 "pair while leaving the rest within a JND, this cell cannot "
                 "be run at all. My instinct is that no such manipulation "
                 "exists by ratio detune, since one alpha controls both. "
                 "Superseded ask: validate 'heard as a detuned X' by ERB or by "
                 "listening; until "
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
              "question would only reproduce a gate that has already fired. "
              "UNBLOCKING PATH REGISTERED 2026-09-02: the contrast this row "
              "waits on is now three QUEUED rows below -- detune-impossibility, "
              "resynthesis-apparatus, decorrelation-battery. If the first "
              "finds a fold case that DOES split the witness pair, this row "
              "unblocks without the other two."),

    # ------------------------------------------------------------------
    # THE CONTRAST ARC, queued 2026-09-02. Design given in session; not one
    # line of it has been run. It is written down here for one reason: the
    # plan currently exists only in a conversation, and this file exists
    # because a compact kills threads that live only in conversations.
    # ------------------------------------------------------------------
    dict(id="detune-impossibility", status=LANDED,
         artifact="cross_substrate/brocot_detune_impossibility.json",
         verdict="EXACT_ISOLATION_IMPOSSIBLE_LOCAL_DETUNE_COSTS_MORE_THAN_IT_BUYS",
         warrant=[("cross_substrate/brocot_modulation_cue.json",
                   "STIMULUS_CONTRAST_IS_CLEAN",
                   "STRUCTURAL/the twin is a different spectrum"),
                  ("cross_substrate/brocot_cue_presence.json",
                   "CUE_IS_PRESENT_THROUGHOUT",
                   "STRUCTURAL/unconditional, survives int16")],
         request="turn 'no ratio detune can isolate the fusion cue' from a "
                 "belief into a scoped theorem. Every partial sits at "
                 "|1 + n1 + n2*alpha|*f_c, so a detune has ONE degree of "
                 "freedom and moves each alpha-dependent partial with velocity "
                 "|n2|: the shift vector is confined to a one-dimensional "
                 "subspace whose direction the lattice fixes. 'Split the "
                 "witnesses, freeze the rest' needs a shift vector off that "
                 "line, so no d-alpha achieves it at any magnitude. MUST cover "
                 "the FOLD/reflected cases -- that is the standing caveat and "
                 "the fold has bitten this arc three times.",
         note="LANDED 2026-09-02, and it split into two answers that are not "
              "in tension. EXACT ARM (E2), unbounded in magnitude and decided "
              "in rational arithmetic over a COMPLETE candidate set -- 2306 "
              "candidates across 8 ratios, folds and permutations included, "
              "ZERO returns. No delta of any size returns the bystander "
              "spectrum to itself while splitting the witness pair. That is "
              "the scoped theorem the row asked for, and the fold did not hide "
              "a counterexample this time.\n"
              "PRACTICAL ARM (E3) MISSED, and the miss is recorded as a miss: "
              "isolation margin > 1 for 8 ratios of 8, against a sealed "
              "prediction of zero. But the margin lives at 815-1499 CENTS -- "
              "8 to 15 semitones, a different ratio rather than a detune. The "
              "post-hoc local statistic, labelled as post-hoc: separating the "
              "witness pair by one cent costs 2.4x to 7.4x that much bystander "
              "movement, linear to 0.75% across a 50x tolerance sweep. Ratio "
              "detune is not merely unable to isolate; locally it is "
              "ANTI-selective.\n"
              "TWO INSTRUMENT DEFECTS CAUGHT BY THE CELL'S OWN MECHANISM ARM, "
              "both recorded as Amendment 1 rather than quietly fixed. (a) The "
              "lattice really does put partials at DC -- (2,-4) at alpha=3/4 "
              "and (3,-3) at 4/3, both clearing the 1e-4 floor -- where |a| "
              "has a corner and the shift direction is undefined; M1 scored "
              "exactly 1.0, which is the signature of a structural error and "
              "not of noise. (b) Worse: with f0 = 0 the cents metric is "
              "log(x/0), so those two ratios fell through to an initialised "
              "margin of 0.0 and were COUNTED AS PASSES of the headline arm on "
              "a division by zero -- non-evidence scored as a verdict, in my "
              "own denominator, in the cell that cites the rule. Pin 7 of the "
              "checker is that defect's permanent test. (c) The tau column was "
              "also pure grid artifact at 1.2-cent steps, which R1 did not "
              "catch because R1 was scoped to the margin verdict alone; R1 now "
              "guards both halves.\n"
              "CONSEQUENCE FOR THE ARC: resynthesis-apparatus is now warranted "
              "by a measurement rather than by an instinct, and "
              "heard-as-listening stays blocked on the same contrast -- but "
              "blocked on a theorem now, not on my belief about one."),

    dict(id="resynthesis-apparatus", status=LANDED,
         artifact="cross_substrate/brocot_resynthesis_fidelity.json",
         verdict="APPARATUS_IS_FAITHFUL_AND_CARRIES_THE_CUE_"
                 "WHERE_THE_WITNESS_PAIR_IS_AUDIBLE",
         warrant=[("cross_substrate/brocot_cue_presence.json",
                   "CUE_IS_PRESENT_THROUGHOUT",
                   "STRUCTURAL/unconditional, survives int16"),
                  ("cross_substrate/brocot_detune_impossibility.json",
                   "EXACT_ISOLATION_IMPOSSIBLE_LOCAL_DETUNE_COSTS_MORE_THAN_IT_BUYS",
                   "STRUCTURAL/theorem-grade on the exact arm, measured on the "
                   "local one")],
         request="additive resynthesis as the contrast apparatus: render the "
                 "exact spectrum from its own partial list (26-31 knobs at "
                 "I=0.9), then build the twin by moving ONLY the witness pair "
                 "with every other partial bit-frozen -- the manipulation "
                 "detune-impossibility says the FM synthesis path cannot "
                 "express.",
         note="LANDED 2026-09-04. The obligation was discharged and it paid "
              "for itself twice.\n"
              "FIDELITY HOLDS. Ground truth is the TIME-DOMAIN FM render, not "
              "the partial list -- comparing the additive render against the "
              "list it was built from is circular and passes by construction -- "
              "so what the gate measures is box TRUNCATION. Median error 0.013 "
              "of the contrast against a 0.10 bar, monotone in B, and the "
              "deliberately truncated B=2 rival FAILS the same bar at 3.30, so "
              "the arm discriminates instead of merely passing.\n"
              "AND THE SELECTIVITY ARM WAS MIS-RULERED, caught by the arm I "
              "expected to be boring. ERB's kernel is ~57 Hz at the witness "
              "frequencies; the manipulation moves each partial 1-3 Hz. The "
              "static metric CANNOT SEE ITS OWN OBJECT, and two ratios reported "
              "selectivity of 5770 and 8735 -- not excellence, a zero "
              "denominator. The tell was R1: witness phase changed the result "
              "by nothing to six figures, and beat salience is phase-sensitive, "
              "which is the entire reason phase held TESTED status. A PASSING "
              "resolution arm certified that the existence arm above it was "
              "inert. Observable-choice-is-per-axis: fidelity is a snapshot "
              "question, selectivity is a MODULATION-domain one.\n"
              "THE CORRECT READOUT PASSES WITH BOTH CONTROLS, using "
              "brocot_cue_presence's envelope instrument unchanged: FM twin "
              "shows the beat 8/8 (positive), additive EXACT does not 8/8 "
              "(negative -- its pair is merged), additive twin carries it 7/8 "
              "at 37-88 dB while moving ~30x less on ERB.\n"
              "SCOPE, NAMED NOT AVERAGED: 5/7 is excluded. Its witness pair "
              "sits at amplitude ~2e-4 and cannot beat audibly alone -- and its "
              "FM twin scores 25.9 dB against 42-117 dB elsewhere, so that "
              "ratio's apparent cue was mostly COLLATERAL, which is the arc's "
              "own thesis surfacing as a control failure. Pin 4 of the checker "
              "fails if 5/7 starts passing OR if a second ratio joins it.\n"
              "ORIGINAL OBLIGATION TEXT: it "
              "model-ran-on-abstraction defect one layer down: the resynthesized "
              "EXACT stimulus must be verified against the FM render under a "
              "SEALED spectral-distance bar on an ERB metric, so 'the same "
              "sound' is measured and not assumed. Parameters go through "
              "modelparams.swept() -- PHASES ESPECIALLY. Beat salience is "
              "phase-sensitive and the FM render chose the phases for us, so "
              "phase is a free parameter that must hold TESTED status, not "
              "DECLARED. Blocked on nothing but detune-impossibility's result, "
              "which decides whether this apparatus is needed at all."),

    dict(id="decorrelation-battery", status=LANDED,
         artifact="cross_substrate/brocot_decorrelation_battery.json",
         verdict="INVALID",
         warrant=[("cross_substrate/brocot_cue_salience.json",
                   "SKIP_STRUCTURE_IS_REAL_MECHANISM_UNRESOLVED",
                   "MECHANISM/open -- selected max + undiscriminating arm"),
                  ("cross_substrate/brocot_resynthesis_fidelity.json",
                   "APPARATUS_IS_FAITHFUL_AND_CARRIES_THE_CUE_"
                   "WHERE_THE_WITNESS_PAIR_IS_AUDIBLE",
                   "STRUCTURAL/the apparatus this row rides on, scoped to 7 "
                   "ratios with 5/7 excluded by name")],
         request="rides on resynthesis-apparatus: matched-energy / "
                 "differing-concentration stimulus pairs and the reverse, to "
                 "decorrelate the two accounts brocot_cue_salience could not "
                 "separate. Constructible under resynthesis; NEVER constructible "
                 "by ratio detune, where one alpha moves both together.",
         note="LANDED 2026-09-05 as a NEGATIVE, three ways, and the row stays "
              "open in spirit via decorrelation-battery-v2 below.\n"
              "(1) INVALID AT ITS OWN PREMISE. P1 asked whether energy and "
              "concentration really are confounded in the FM detune family: "
              "|rho| = 0.432 against a 0.5 bar. MISSED, so the lattice refuses "
              "and the four arms below are UNREAD -- not false, unread. The "
              "battery's entire justification was 'these cannot be separated "
              "by detuning', and at 0.43 that premise is weaker than the "
              "argument needed. No partial credit taken.\n"
              "(2) THE BATTERY CAME OUT WORSE THAN THE FAMILY IT REPLACES: "
              "|rho| 0.546 vs 0.432, and ZERO matched-energy/differing-"
              "concentration pairs at every one of 11 ratios. Diagnosis, "
              "visible in the table: concentration span 1.12-1.27 while energy "
              "spans 1.2e11. Subset size is an ENERGY knob, not a "
              "concentration one -- splitting k bins does not spread the "
              "modulation difference across k bands, because that difference "
              "is broadband and its concentration sits near saturation "
              "whatever k is. One knob again, pointed at the wrong axis. The "
              "battery reproduced the very defect it was built to remove.\n"
              "(3) SCOPE MISMATCH, MINE: the sealed docstring says 7 ratios "
              "(the apparatus's validated set), the code excluded only 5/7 "
              "from 12 and ran 11. There is a real argument for 11 -- this "
              "battery splits arbitrary coincident bins and never touches the "
              "witness pair, so 'carries the cue' was never binding here -- but "
              "I am making it after the fact and the seal says 7. Recorded as "
              "a mismatch, not resolved in the flattering direction.\n"
              "TWO GUARD BUGS FELL OUT, both on paths never previously walked. "
              "compose()'s failed-premise branch returned no `citation` key, so "
              "the documented way to report a verdict crashed with KeyError the "
              "first time a PREMISE arm ever actually missed -- a refusal path "
              "that cannot report its own refusal, looking like a caller bug. "
              "And Bar.line()'s rival message printed 'rival ALSO CLEARS IT' "
              "whenever the arm failed to discriminate, including when the "
              "rival had plainly missed too; `discriminating is False` has TWO "
              "causes and the message assumed one. Both fixed, both pinned "
              "(pin 6 of the checker).\n"
              "ORIGINAL RATIONALE: this is why the salience lead and the fusion question share one "
              "apparatus, and it is the whole reason the resynthesis cost is "
              "worth paying. DESIGN-TIME OBLIGATION: every arm names the rival "
              "stimulus family that must FAIL it, via Bar(rival=...) -- the "
              "rule minted from this row's own warrant, applied to the cell "
              "that produced it. When a listening session eventually runs, it "
              "reports detection AS A FUNCTION OF CRITERION per manipulation, "
              "never a threshold: criterion-as-axis survives the framing "
              "death."),

    dict(id="decorrelation-battery-v2", status=QUEUED,
         warrant=[("cross_substrate/brocot_decorrelation_battery.json",
                   "INVALID",
                   "NEGATIVE/the v1 diagnosis this row is built on"),
                  ("cross_substrate/brocot_resynthesis_fidelity.json",
                   "APPARATUS_IS_FAITHFUL_AND_CARRIES_THE_CUE_"
                   "WHERE_THE_WITNESS_PAIR_IS_AUDIBLE",
                   "STRUCTURAL/the apparatus still stands")],
         request="rebuild the battery with a REAL concentration knob. v1 varied "
                 "subset size and always assigned DISTINCT beat rates, so the "
                 "one contrast that would actually concentrate the modulation "
                 "difference -- k bins split at ONE COMMON rate, piling it into "
                 "a single band, against k bins at k rates -- never appears in "
                 "it at all. Its absence there is not evidence about it.",
         note="REGISTERED RATHER THAN RE-RUN, deliberately. v1's design was "
              "changed in my head the moment I saw its table, and a design "
              "adjusted after seeing the result and then run until it goes "
              "green is precisely what the seal exists to prevent. So v2 gets "
              "its own sealed predictions and its own commit, and v1's "
              "negative stays on the record with its diagnosis pinned by "
              "verify_decorrelation_battery.\n"
              "TWO OBLIGATIONS v2 INHERITS. (a) P1 must be RE-POSED, not "
              "reused: v1's premise bar of 0.5 was missed at 0.432, so 'the FM "
              "family confounds them' is not established at that strength and "
              "v2 cannot quietly assume it. Either defend a lower bar in "
              "advance or drop the premise and make the battery's value an "
              "unconditional claim. (b) The scope must be ONE set, stated once: "
              "7 or 11, decided before the run and not narrated afterwards.\n"
              "AND THE DESIGN-TIME RULE FROM THE APPARATUS CELL APPLIES HERE "
              "TOO: each arm names the ruler appropriate to ITS OWN axis. "
              "Energy and concentration are different observables and v1 read "
              "both off one banded difference spectrum; the resynthesis cell "
              "already showed what happens when one ruler is asked two "
              "questions."),

    dict(id="ff-curve-singularity-guard", status=QUEUED,
         warrant=[("approximability/F_reproduce.json",
                   "SESSION_F_CLAIMS_DO_NOT_REPLICATE",
                   "STRUCTURAL/the run that hit the gap")],
         request="give approximability/ff_curve.py a squarefree guard. g2_Nv "
                 "asserts only len(fc)==6 and fc[5]%p!=0 -- degree five with a "
                 "nonzero leading coefficient -- and performs NO squarefree "
                 "test, so a singular f returns confidently wrong N_v.",
         note="FOUND 2026-09-05 by running it: y^2 = x^5 + x^3 = x^3(x^2+1) "
              "sailed through at p=13 and p=29 and was caught only because the "
              "Weil gates rejected it afterwards. MORNING_F says singular "
              "curves were 'filtered by a squarefree-f check' -- so Session F "
              "did that filtering in the DRIVER, and the driver was never "
              "committed, so the check left the repo with it. The module is "
              "banked as 'a real asset: provable ground-truth curves beyond "
              "the genus-0 line', and an importer who does not know to filter "
              "gets wrong answers caught only sometimes, because Hasse-Weil is "
              "a loose bound. That is the same shape as Session F's own "
              "recorded Newton-identity bug.\n"
              "NOT DONE IN PASSING because ff_curve.py belongs to Session F's "
              "arc, which is freshly landed; a guard added to another arc's "
              "banked machinery is a change that arc should see. "
              "F_reproduce.py implements the check locally (poly_gcd_deg) so "
              "the code to move is already written and tested."),

    dict(id="orphan-session-branches", status=QUEUED,
         request="PARTLY DONE 2026-09-02 -- Session G LANDED (see note), three "
                 "remain. Adjudicate and land the July-2026 session branches whose "
                 "single commit each is reachable from NEITHER main NOR "
                 "cubics-wilderness: cf-convergence-bridge (af5349f, Session G "
                 "CF-convergence bridge PARTIAL), genus-ff-calibrator (c93a363, "
                 "Session F certified genus>0 point-counter), third-refit "
                 "(b823c68, Session H arm 2, 1/3 genus-0 refit "
                 "INDISTINGUISHABLE at 3 base fields), thouless-amo-identify "
                 "(352231a, Session D AMO identification NEGATIVE -- Sturmian "
                 "!= cosine -- plus the pi-292 Thouless predictor).",
         note="FOUND 2026-09-02 during a loose-ends sweep, not by any checker. "
              "The tell is arithmetic and was sitting in plain sight: the "
              "MORNING_* series on HEAD runs A,B,C,E,E_run,H_arm1,I,J,K,lambda "
              "-- and the four missing letters, D/F/G/H_arm2, are EXACTLY the "
              "four unmerged branches. A gap in a numbered series is a "
              "detector nobody had pointed at anything.\n"
              "TWO THINGS MAKE THIS MORE THAN TIDYING. (1) THE SEAL/MEASUREMENT "
              "SPLIT: G_fifth_measured.json IS on HEAD -- carried forward by "
              "Session H Arm 1 (479de0b), identical blob -- while its "
              "G_fifth_prediction_SEALED.json is NOT, and "
              "approximability/H_arm1_seal.py:22 reads that measurement. So a "
              "SEALING script on the working branch stands on a measurement "
              "whose own sealed prediction exists only on an unmerged branch. "
              "By this repo's own standard that is an unsealed measurement in "
              "load-bearing use, and it is the one gap that should not wait. "
              "(2) SESSION F CANNOT BE MERGED AS-IS: its commit writes to "
              "criticality_tool/approximability/... -- committed from the "
              "PARENT directory, so the paths carry a stray repo-name prefix. "
              "Almost certainly why it never merged, and it needs a path repair "
              "before it lands, which is why this is a queued adjudication and "
              "not a drive-by merge.\n"
              "Also orphaned: Session D's pi292_thouless_prediction.py -- the "
              "GENERATOR of pi292_prediction_SEALED.json, which IS on HEAD. A "
              "banked sealed number whose generator is on no reachable branch "
              "is the committed-generator rule failing quietly; the rest of "
              "that arc (measured/unseal_compare/seal_verdict) did survive.\n"
              "SESSION G LANDED 2026-09-02 (merge c0f1037, commit af5349f). It "
              "was the urgent one and it was worse than a filing gap: "
              "G_fifth_measured.json carries \"note\": \"BLIND -- seal not "
              "opened\", so it announced a governing seal that did not exist on "
              "the branch consuming it, and H_arm1_seal.py:22 builds its a=1 "
              "factor curve from exactly the fifth a12/a13 points whose seal "
              "returned PARTIAL with the strict-monotonicity falsifier TRIPPED "
              "at depth 12 -- the a=1 step. The science was never lost "
              "(MORNING_H_arm1.md explains the trip at f*~0.287 and was written "
              "as G's follow-up); the EVIDENCE was, and a reader on this branch "
              "met dangling references to a session whose documents were "
              "absent. 8 pure additions, no conflict, measured blob "
              "byte-identical.\n"
              "AND IT FOUND A DEFECT IN verify_seal_order. Registering the "
              "(prediction, measured) pair reported SEALED -- because git's "
              "default history simplification attributed the measurement to "
              "479de0b, twelve hours after the seal, when in truth both files "
              "are in ONE commit and the honest label is DECLARED. The checker "
              "built so that SEALED is a property of the graph rather than of "
              "recollection was being fooled by a traversal flag. Fixed with "
              "--full-history, red-pathed, no existing pair changes verdict.\n"
              "ALL FOUR LANDED 2026-09-05. G (c0f1037), then D, H arm 2 and "
              "F. D restored pi292_thouless_prediction.py, the GENERATOR of a "
              "pi292_prediction_SEALED.json that had been sitting on this "
              "branch without one. F needed its criticality_tool/ path prefix "
              "repaired (git mv, so the rename shows in the graph) and then "
              "exposed a SECOND generator gap: ff_curve.py is a pure module "
              "with no __main__, so F_results.json's four banked numbers have "
              "no producing code on any branch. Rather than reconstruct a "
              "driver to hit '77/77' -- tuning to a target, and a "
              "reconstruction is a hypothesis about what was run -- "
              "F_reproduce.py declares its OWN family and reports what that "
              "gives: gates replicate 212/212 (the load-bearing "
              "method-invariance claim, corroborated on curves Session F never "
              "used), rate ratios do NOT, and the genus-2 one is banked to 17 "
              "significant figures on a quantity with sd 0.296 spanning "
              "0.65-1.86. See ff-curve-singularity-guard above.\n"
              "DECIDED 2026-09-02: main was fast-forwarded to cubics-wilderness "
              "WITHOUT these four, deliberately, so the merge stayed a "
              "zero-risk fast-forward and the adjudication kept its own "
              "commit. Do not delete the four branches: they are already on origin "
              "(0 unpushed), so nothing is at risk of loss, but they are the "
              "only refs from which these four commits are reachable AT ALL -- "
              "deleting them orphans the objects to gc."),
]


def _verdict_of(root, rel):
    """The artifact's EFFECTIVE verdict: the amendment if one exists, else the
    seal.

    BLIND SPOT FOUND 2026-09-02, in the file built to make verdict drift fail
    the board. This read `.get("verdict")` alone. But a sealed cell that is
    later corrected does NOT overwrite its seal -- the seal is the whole point,
    it records what was pre-registered -- it writes a sibling `verdict_amended`
    key. So every amendment in the repo was invisible to exactly the check whose
    job is to catch a verdict that no longer says what a row claims it says.

    Six citations across five rows were reporting superseded verdicts, and four
    of the six amendments REVERSE or materially weaken the seal they replaced:

        NOT_DIFFERENTIATED                        -> DIFFERENTIATED_BUT_NOT_BY_1/q
        MODEL_GAP_IS_DOCUMENTATION_ONLY           -> RANKING_EFFECT_UNRESOLVED
        RANKING_DOES_NOT_DEPEND_ON_EXACT_COINCIDENCE
                                                  -> RANKING_PARTLY_DEPENDS_...
        MARKERS_ARE_THE_WRONG_OBJECT              -> OFFSET_REAL_BUT_UNEXPLAINED
        COLUMN_IS_CONDITIONED_ON_ROUTING           -> ORDER_DEPENDENT_NO_...

    The worst of them is a WARRANT, not a record: `suggest-reachability-filter`
    is QUEUED, one C++ signature change from shipping, and it was warranted by
    "RANKING_DOES_NOT_DEPEND_ON_EXACT_COINCIDENCE" while the artifact had
    already amended to the NEGATION of that sentence. That is the precise
    scenario WARRANT_STALE was built for -- the second recorded instance of it
    -- and the mechanism sat green through it because the amendment was in a
    key it never read.

    NOT every verdict reader wants this. The sweep that followed found two
    board checkers that read `verdict` directly and MUST keep reading the seal:
    `verify_reachable_bar` ("the sealed lattice verdict is reported unchanged
    -- the seal must not be rewritten") and `verify_verdict_lattice` ("reports
    its sealed label unchanged" + "carries the correction beside it"). Those are
    the opposite obligation -- seal INTEGRITY, that a correction was made by
    addition and not by quietly overwriting the pre-registration -- and they are
    right as written. Do not "fix" them to match this. The rule is by question:
    integrity checks read `verdict`; anything asking WHAT IS TRUE NOW reads the
    effective verdict through here.

    Lesson, general: a staleness detector reads ONE field, and a correction
    convention that writes a DIFFERENT field is invisible to it by construction.
    Whenever a repo gains a way to supersede a value, every checker that reads
    the superseded value has to be re-pointed the same day. Filed with
    `filing-discipline-attribution-slot` and `knowledge-does-not-propagate`.
    """
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p))
    except Exception:                                          # noqa: BLE001
        return None
    if not isinstance(d, dict):
        return None
    # Amendment wins. A row that wants to cite the seal must say so explicitly
    # via warrant_reviewed, which is a human act and leaves a trace.
    return d.get("verdict_amended") or d.get("verdict")


def load(root):
    out = []
    for e in ENTRIES:
        e = dict(e)
        stale = []
        for w in e.get("warrant", []):
            art, minted = w[0], w[1]
            layer = w[2] if len(w) > 2 else "unlabelled"
            now = _verdict_of(root, art)
            if now != minted:
                reviewed = dict(e.get("warrant_reviewed", []))
                if reviewed.get(art) != now:
                    stale.append(dict(artifact=art, minted=minted, now=now,
                                      layer=layer))
        for art, why in e.get("framing_dead", []):
            if art not in dict(e.get("warrant_reviewed", [])):
                stale.append(dict(artifact=art, minted="(verdict unchanged)",
                                  now="FRAMING DEAD: " + why,
                                  layer="SEMANTIC"))
        e["warrant_stale"] = stale
        if e["status"] == LANDED:
            p = os.path.join(root, e["artifact"])
            e["artifact_exists"] = os.path.exists(p)
            e["verdict_matches"] = False
            if e["artifact_exists"]:
                # THROUGH _verdict_of, not a second inlined json.load. The
                # 2026-09-02 amendment fix landed on the warrant path and this
                # branch stayed blind, because the same read existed TWICE --
                # so half the ledger was fixed and the board said nothing. Same
                # shape as the 18 outstanding argmin copies in the C3 census:
                # a duplicated read is a place a correction does not reach.
                e["verdict_matches"] = (
                    _verdict_of(root, e["artifact"]) == e["verdict"])
        out.append(e)
    return out


if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.abspath(__file__))
    for e in load(ROOT):
        mark = ("" if e["status"] != LANDED else
                "  OK" if e["verdict_matches"] else "  BROKEN")
        print(f"{e['status']:>8s}  {e['id']:<24s}{mark}")
