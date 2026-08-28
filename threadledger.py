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
         verdict="COLUMN_IS_CONDITIONED_ON_ROUTING",
         note="SEALED head reported unchanged; the amended reading is "
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
         warrant=[("cross_substrate/brocot_suggest_score_census.json",
                   "RANKING_DOES_NOT_DEPEND_ON_EXACT_COINCIDENCE",
                   "STRUCTURAL/the score's exact-coincidence share"),
                  ("cross_substrate/brocot_filter_worth_it.json",
                   "FILTER_OPTIMISES_AN_INAUDIBLE_PROPERTY",
                   "AUDIBILITY/sigma-conditional")],
         request="pass current's indices into suggestExtensions and filter "
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
         warrant=[("cross_substrate/brocot_audible_horizon.json",
                   "EPS_HORIZON_OVERSTATES_AUDIBILITY",
                   "AUDIBILITY/chosen-floor, and its seal was vacuous"),
                  ("cross_substrate/brocot_masked_horizon.json",
                   "MASKING_GIVES_A_DERIVED_HORIZON",
                   "AUDIBILITY/sigma-conditional")],
         request="fix the audibility floor empirically instead of picking it: "
                 "(A) excitation-pattern masked-threshold census; (B) 2AFC "
                 "detune-twin discrimination using the instrument's own "
                 "setDetuneCents, adaptive staircase on max(p,q), >=1 s "
                 "sustain. AND (C) RE-SEAL brocot_audible_horizon with "
                 "falsifiable arms -- the disclosure is the honest interim "
                 "state, not the end state; the end state is a cell whose "
                 "EXISTENCE designation is load-bearing again, so that "
                 "exposure_audit's single refusal clears on its own merits "
                 "rather than by being explained.",
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
    dict(id="the-0017-offset", status=QUEUED,
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
              "incomplete list -- a different repair from adding a channel."),
    dict(id="coherence-model-gap", status=QUEUED,
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
    dict(id="amplitude-event-layer", status=QUEUED,
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
         warrant=[("cross_substrate/brocot_marker_erb_gate.json",
                   "MAY_SAY_STRUCTURAL_EVENT_ONLY",
                   "AUDIBILITY/static, 0.67x a 1-cent detune"),
                  ("cross_substrate/brocot_masked_horizon.json",
                   "MASKING_GIVES_A_DERIVED_HORIZON",
                   "AUDIBILITY/sigma-conditional")],
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


def _verdict_of(root, rel):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p)).get("verdict")
    except Exception:                                          # noqa: BLE001
        return None


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
        e["warrant_stale"] = stale
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
