# ARS epistemic state

*Internal working reference.  Body 2026-05-11/12 (V1 / cross-domain
arc); arithmetic-spectral arc (Phases 34a–34f) appended 2026-05-16 —
see "## Arithmetic-spectral arc" below.  Not a writeup, not a
publication draft, not a hierarchy of what to lead with.  A map of what
the tool currently knows, at what confidence, under which disciplines,
and what is still open — so that future phase briefs can scope against
an honest inventory.*

---

## Preamble

ARS as deployed is a **two-engine classifier of point processes** sitting
on top of a Farey-rational PLL framework.  The first engine is the NNS
engine — `joint_q_profile`, the deployed classifier used in Phase 22a
through the present — which decomposes a point process over Farey-rational
bands, computes analytical passage times per band, and reads
nearest-neighbour spacing statistics against Poisson / GOE / GUE
references.  Its load-bearing outputs are `ks_gue_med` (median over q-bands
of KS distance to GUE) and `rep_med` (median repulsion integral).  The
second engine is the **RF engine** — Ramanujan-Fourier amplitudes on the
event-indicator function — whose canonical product is `p-adic v4`, which
aggregates `|a_q|` over q's divisible by a chosen prime, normalised
against the total amplitude.  These two engines are formally distinct
objects (§7.ter.39, Phase 31a derivation); the parallel `pll_bank`
infrastructure with K_p, K_i, IIR LP and lock detection has *never been
called by the deployed analyses* and is not the basis of any deployed
finding.

The tool measures at **two timescales**.  Full-sequence statistics treat
the entire recording (or entire signal) as one object and ask whether
that object's aggregate spacing distribution carries a signature.
Per-window statistics tile the recording into shorter epochs and ask
whether the signature is *stationary* — present in each tile — or
emergent only at the aggregate scale.  These are different questions
about different objects; the same recording can carry a signature at one
scope and not the other.  We learned to enforce that distinction
empirically (Phase 31f H2, Round 4 p-adic), and it has since become
standard discipline that any surrogate-survival claim names its scope.

A **capability-vs-application distinction** runs through the work.  ARS
is an applied implementation of Planat's framework, and what it
*measures* — the two-engine output on a given input — is well-defined.
Whether any given application is in the tool's capability envelope is a
separate, per-application question that must be answered by calibrator
runs, induction-on-noise checks, and extractor-invariance probes
(METHODS.md).  Several historical "findings" turned out to be artifacts
of an extractor mechanism rather than properties of the signal (LLM
internal states, §7.ter.19 through §7.ter.23).  The capability envelope
has expanded as new disciplines have been added; it has also contracted
when previously assumed-good applications were diagnosed out.

Eight disciplines now structure what counts as a surviving finding.
**Full-sequence surrogate floors** (Aitchison-null, rate-matched Poisson,
cell-shuffle, LN-evoked, state-modulated) check that the aggregate
signature is not reproduced by a null model with the relevant property
preserved.  **Rate-matched surrogates** specifically isolate dynamics
from rate.  **Rate-stratified within-cell comparison** goes one level
deeper: even after rate-matched, the dynamics signal may live in a
specific rate tertile, so per-cell tertile comparison is the cleaner
discrimination (Phase 31b Follow-up).  **Per-window surrogate** repeats
the full-sequence battery on each window and asks for stationarity.
**Per-window p-adic** does the same on the RF engine, separating
long-coherence aggregation phenomena from short-coherence stationary
ones.  **Spatial-scale stratification** asks whether a surviving
signature is local-cluster, recording-wide, or scale-dependent
(Phase 27, Phase 28).  **Cross-substrate** asks whether a signature
replicates across recording substrates with different spatial pitch,
species, and brain state.  **Cross-engine** asks whether the NNS and RF
engines agree on a substrate-systematic direction.  **Stationarity
checks** without a surrogate battery — modal-classification stability
over windows — are a weaker but still useful filter.

The load-bearing architectural fact about the NNS engine is the
**§7.ter.10 band-invariance proposition**: any engine whose architecture
is `{filter Farey rationals → analytical-passage → unit-mean-normalised
NNS → KS}` is invariant under linear time scaling, and therefore
*cannot* produce per-prime asymmetry on stationary signals.  This is a
proved theorem about the deployed engine's reach, not a benchmark
result.  Three versions of p-adic profile (v1, v2, v3) failed acceptance
for this structural reason before v4 — which abandons unit-mean
normalisation and routes through the RF engine — passed.  The
proposition is *why* the two-engine architecture exists: the NNS engine
carries dynamics-class signal (Poisson / GOE / GUE / TR / BR), and the
RF engine carries per-prime arithmetic signal.  Future phase work should
not propose to extract per-prime structure from `joint_q_profile`
output, and findings that mix engines must say which engine is
load-bearing for the claim.

---

## Locked findings with multiple disciplines verified

### H1: cellular orientation selectivity ↔ global level-repulsion class statistic

The finding is that per-unit orientation selectivity index (OSI) of V1
single units correlates with `ks_gue_med`, the global NNS engine output
on the recording.  Numbers: pvc-11 anesthetised macaque V1 partial
ρ = +0.720 (n=210 H1-passing pairs, p < 1e-37, controlling for mean
firing rate); Allen awake mouse V1 meta-fixed ρ = +0.363 across 12
sessions (all 12 positive sign, 10 of 12 individually significant,
I² = 43%).  The cross-substrate magnitude attenuation is ~50–58%; the
direction is preserved.  **Engine: NNS** (KS-to-GUE on Farey-band
analytical passages).  **Mechanism status: open.**  H1 is a
correlational finding between a cellular tuning property and an
aggregate spacing statistic; no specific generative mechanism has been
proposed and tested.  **Disciplines cleared:** full-sequence surrogate
(Phase 22a), Phase 22b within-recording (meta-fixed +0.742, no
between-recording confound) and within-SNR-tertile (T1/T2/T3 = +0.672 /
+0.742 / +0.532), cross-substrate (Phase 24), rate-stratified
within-cell on pvc-11 (sign-consistent 3/3 recordings, mag range 0.21;
SURVIVES_STRATIFIED, Phase 31b).  Phase 27 Analysis 2 found `ks_gue_med`
is SUBSUMED by 8-factor FA loadings (R² = 0.73–0.80) on H2 sessions,
which weakens the *orthogonality-against-FA-specifically* claim but
does not affect the cross-substrate correspondence.  **Outstanding:**
rate-stratified within-cell replication on Allen, per-window
stationarity check on the per-unit OSI ↔ ks_gue_med relationship,
mechanism hypothesis.  **Open:** the finding's interpretive load
currently rests on the unexamined assumption that a per-unit functional
property and a recording-wide aggregate statistic should track each
other — what is the relationship between cell-class composition and
aggregate-NNS that makes this correlation appear?

**Marginal-vs-class downgrade (2026-06-05, see the dated arc section at
the end of this file).**  H1 is a correlation on the NNS *marginal*
(`ks_gue`), and as a marginal correlation it stands fully — it survived
the long-range arc unchanged.  What is downgraded is the structural
reading: under the trial-PSTH external-rate unfold on the same Allen V1
data, OSI↔Σ²(clustering) collapses +0.135→−0.077 (null) — the OSI-graded
clustering was stimulus-driven rate-stepping, not intrinsic to selective
cells.  Selective cells track the marginal spacing statistic but are not
a special universality class and do not lock to GUE (0/100 Allen V1 cells
RIGID at long range).  Read H1 as "selectivity ↔ a marginal-spacing
gradient", not "↔ a level-repulsion *class*".

### F1/F0 ↔ rep_med substrate-systematic sign-flip

> **⚠ RE-VERIFIED ON THE REPAIRED INSTRUMENT, 2026-07-28/29 (R-181…R-184). STAYS LOCKED, with
> its evidential structure restated.** Both arms were recomputed on the signed axis; the
> reproduction gates passed exactly (pvc-11 210/210 to 5 dp, Allen **910/910**).
>
> | | pvc-11 | Allen | Δρ | Fisher z |
> |---|---|---|---|---|
> | deployed (clipped) | +0.2983 (n=210) | −0.2016 (11/12 neg) | 0.4999 | +6.59 |
> | **repaired (signed)** | **+0.1088 (p=0.116, ns)** | **−0.2502 (12/12 neg)** | **0.3590** | **+4.70, p=2.6e−06** |
>
> **The substrate-systematic sign flip — the finding's actual claim — SURVIVES at 4.70σ**,
> attenuated ~28%. The Allen arm *strengthens* (11/12 → 12/12 sessions negative).
>
> **Three things did change and are not cosmetic:**
> 1. **The quoted +0.388 is unattributed and unreproducible** — a hardcoded constant in
>    `phase24/run_meta_analysis.py:127` (`PVC11_REF`) that nothing computes. The repo's own
>    artifact gives **+0.29834625**, reproduced independently to five decimals. **~30% overstated.**
> 2. **The pvc-11 arm alone is no longer significant** (+0.1088, p = 0.116) — 82.4% of its cells
>    sat on the clip's rail, so the deployed correlation was carried by the 17.6% that escaped.
> 3. **The evidential structure is now Allen-arm-plus-contrast**, not two mutually-confirming
>    arms. pvc-11 contributes direction, not significance.
>
> An earlier note here (R-182) said to remove this from the locked list. **That was based on
> testing the pvc-11 arm in isolation and was too harsh** — corrected in R-184.

The finding is that the modulation index F1/F0 (a per-unit simple-vs-
complex-cell marker) correlates with `rep_med` (repulsion integral
median) in **opposite directions** across the two substrates: pvc-11
+0.388 (p = 6e-9), Allen meta-fixed −0.183, all 12 Allen sessions
negative sign across 4 Cre lines.  **Engine: NNS** (RF amplitudes do
not figure here).  **Mechanism status: open.**  The substrate-systematic
direction is real and survives the Hietanen 2013 spike-count-bias
deflation (Phase 27 Analysis 1: 210 rate-matched cross-substrate pairs
at median 3.9 sp/s show pvc-11 ρ=+0.298 vs Allen ρ=−0.222, Δρ=+0.520,
with spike-count covariate contributing at most −0.04 attenuation).
What biological substrate-difference produces the sign change is open.
Two candidate axes — species (macaque vs mouse) and state (anesthetised
vs awake) — are confounded in the pvc-11/Allen comparison; the Phase 31
session-heterogeneous breakdown (5/12 canonical mid+high-negative,
4/12 all-negative, 3/12 other) suggests it is not a simple Cre-line
predictor.  **Disciplines cleared:** full-sequence surrogate,
rate-matched (3 methods, Phase 27 Analysis 1), rate-stratified
within-cell on both substrates (pvc-11 3/3 sign-consistent;
Allen SUBSTRATE_SYSTEMATIC_SURVIVES_STRATIFIED at session-aggregate,
10/12 tertile-mean negative; Phase 31b Follow-ups 2 and 4),
cross-substrate, Ibbotson 2005 phylogenetic-conservation deflation
ruled out, cross-engine substrate-systematic direction matches p-adic
P7_PVC11_SPECIFIC.  **Outstanding:** per-window surrogate on F1/F0 ↔
rep_med (not yet run), within-cell rate-stratified per-window check,
mechanism-specific surrogate (a cell-class-composition-matched null
that holds composition fixed and asks whether the sign survives).
**Open:** is the sign-flip mediated by simple-vs-complex-cell
composition differences between substrates (Ibbotson 2005 weighs
against this), by laminar sampling differences (Utah array vs
Neuropixels target different cortical layers), or by state/anesthesia
effects on cortical dynamics that interact with the modulation index?

### H2 surviving population-event structure

> **⚠ INSTRUMENT-EXPOSED 2026-07-28 (R-180).** H2's surrogate-survival criterion is computed on
> **`rep_int_per_q`** (`phase22b/pass_e_tighten_seeds.py:111`, reported as `n_q_rep_survives`) —
> the CLIPPED repulsion field, which on pvc-11 sits on its lower rail for ~79% of cells. This
> section does not name its own load-bearing statistic; it was resolved from code. **Exposure
> is established; the effect on the verdict is UNTESTED.** Not downgraded — flagged.

The finding is that on specific pvc-11 recordings, population-event NNS
structure on (q=30) Farey-band passages survives the required
conjunction of Aitchison-null surrogates (rate-matched + cell-shuffle +
LN-evoked, or rate-matched + cell-shuffle + state-modulated for
spontaneous) at all q-bands.  **Engine: NNS** at population (not
per-unit) resolution.  **Mechanism status: open.**  The Phase 25
history-coupled-GLM elimination extension was the next stricter
elimination target and returned FIT-CEILING — no configuration in a
24-cell grid produced a usable history-coupled surrogate.  Without that
surrogate, H2's residual structure cannot be definitively attributed
beyond LN-Poisson elimination.  **Disciplines cleared:** full-sequence
surrogate at 30/30 q-bands and 7 surrogate seeds on pvc-11
monkey1_natural_movie and monkey2_gratings_movie (Phase 22b Pass E),
per-window surrogate battery (Phase 31f: monkey1_natural_movie
WINDOW_AWARE_LOCKED at 8/10 windows; monkey2_gratings_movie
WINDOW_MIXTURE at 5/10), spatial-scale stratification at pvc-11
(400–600 µm, Phase 27 Analysis 3: recording-wide-aggregate, NOT
local-cluster, CONTRA-OHIORHENUAN) and Allen Neuropixels (<300 µm,
Phase 28: SPATIAL-SCALE-DEPENDENT with the local 100–300 µm bin LEAST
TR-structured), cross-substrate (Allen 12-session: 3/12 default PASS,
1/8 rate-matched PASS — H2 bounded to anesthetised macaque V1 + specific
recording type).  **Outstanding:** stationarity in the per-window sense
on the 5/10 mixture windows of monkey2_gratings_movie (what is the
window-level discriminator between H2-passing and H2-failing regimes),
a positive mechanism replacing the Phase 25 history-coupled-GLM target,
non-pvc-11 substrates that might show the same surviving structure (so
far all replication attempts fall short).  **Open:** H2 in its current
form is **a very narrow finding**, and the publication framing has to
say so.  It is **triply bounded**: (i) to *recording-wide aggregate*
spatial scope (not local-cluster at any tested scale, Phase 27 +
Phase 28), (ii) to *two specific anesthetised macaque V1 recordings*
(monkey1_natural_movie and monkey2_gratings_movie; no cross-substrate
replication and Allen 12-session falsifies at the rate-matched-
surrogate level), and (iii) to *post-window-aware* refinement
(monkey1 WINDOW_AWARE_LOCKED on 8/10 windows; monkey2 WINDOW_MIXTURE
on 5/10 — not time-stationary).  Whether this triply-bounded survival
is biologically load-bearing or an exhaust of an unmodelled stim-
coupling axis is the live question.  The publication framing should
state the triple bounding explicitly so that downstream readers do not
inflate H2 from "two specific recordings, recording-wide aggregate,
window-mixture in one of them" to "V1 has higher-order population
structure beyond LN-Poisson."

**Marginal-vs-class note (2026-06-05).**  H2 is a surrogate-survival
claim on the NNS *marginal* at population resolution; the marginal-vs-
class arc adds the explicit label that "surviving NNS structure" is a
marginal-spacing statement, not a universality-class one (the deployed
quadrant is order-blind by construction — see the dated arc section at
the end of this file).  H2's substantive content is the surrogate
survival itself, which is unchanged; this is a labelling clarification,
not a downgrade of the result.

### DSI ↔ ks_gue_med

The finding is that direction selectivity index (DSI) correlates with
`ks_gue_med`, replicating in the same direction across substrates with
*stronger* Allen magnitude: Allen meta-fixed +0.269 vs pvc-11 +0.223.
This is biologically plausible given mouse V1's heavier direction
selectivity.  **Engine: NNS.**  **Mechanism status: open** (same status
as H1; the same correlation-vs-mechanism question applies).
**Disciplines cleared:** full-sequence surrogate, cross-substrate
replication, rate-stratified within-cell on pvc-11.  **Round 4 status
upgrade:** the initially-reported PARTIAL_SURVIVAL grade (monkey2
high-rate-tertile sign-flip) is **resolved** by the Round 4 monkey2
sign-flip diagnostic: all monkey2_gratings DSI ↔ ks_gue_med
correlations are p > 0.12, unstratified p = 0.82 — **monkey2 is
underpowered for DSI, not contradicting it**.  The pvc-11 DSI signal
is carried by monkey1 + monkey3 with monkey2 as a null contributor,
not a sign-flipping contributor.  This upgrades DSI's effective status
**closer to H1's grade** than the lingering PARTIAL_SURVIVAL label
suggests.  Publication framing should not lead with
"PARTIAL_SURVIVAL" for DSI — the right label is "SURVIVES_STRATIFIED,
monkey2 underpowered."  **Outstanding:** Allen rate-stratified
within-cell, per-window surrogate, integration with H1 (do H1-passing
units carry the DSI signal too, or are these orthogonal axes within
OSI/DSI space?).  **Open:** what does it mean that the cross-substrate
DSI magnitude exceeds the OSI magnitude in mouse but the reverse holds
in macaque?  The OSI / DSI / `ks_gue_med` triangle has internal
structure that has not been mapped — this is one of the more
mechanism-suggestive open questions in the document and is promoted
to the closing section.

---

## Newer findings still acquiring disciplines

### p=7 enrichment in pvc-11 spontaneous + gratings (full-recording scope)

The finding is that the RF-engine p-adic v4 measurement at q_max=200
shows enrichment of p=7 (q-multiples of 7) above the §7.ter.13
acceptance threshold (1.5× surrogate) in pvc-11 spontaneous (6/6
recordings above, mean z = +2.22, monkey4 z = +6.09) and gratings (3/3
above; monkey1 z = +9.77, monkey3 z = +1.90, monkey2 z = +0.59 — pvc-11
monkey2 marginal).  **Engine: RF (p-adic v4).**  **Mechanism status:
open.**  p=7 at q=7 maps to a period of 35 ms = 28.6 Hz beta
band, which is biologically plausible for V1 but unproven.  Movie
subsets (natural_movie, noise_movie, gratings_movie) suppress p=7
(mean z ≈ −0.4); movie p=7 suppression is **content-driven, not
rate-driven** (monkey1_gratings 27.93 Hz z=+9.77 vs monkey1_natural_movie
24.25 Hz z=−0.96 at matched rate).  **Disciplines cleared:** RF-engine
acceptance at q_max=200 (the §7.ter.13-validated threshold; q_max=30
is underpowered with 95.6% false positive rate against rate-matched
Poisson surrogate), rate-matched surrogate via matched z-score against
rate-matched Poisson, cross-recording within-pvc-11 (12/12 recordings
classified into structured / suppressed by content), cross-substrate
(Allen full 12-session: P7_PVC11_SPECIFIC, mean z = −0.14 spontaneous
vs pvc-11 +2.22, Δ = +2.36; substrate-systematic direction matches
F1/F0).  **Outstanding:** rate-stratified within-cell (p-adic is a
recording-wide aggregate so the per-cell version is not exactly
defined; the right discipline is per-tertile recording aggregation),
per-window stationarity on the surviving p=7 signal in spontaneous +
gratings (Round 4 found p=7 PER_WINDOW_NULL in 9/15 pvc-11 recordings;
only monkey1_spontaneous is per-window-STATIONARY at 4/5 windows z>2 —
see the K-axis Mechanism section below), surrogate-Poisson at q_max=200
on the spontaneous recordings (`q_max=30` confirmed underpowered;
q_max=200 surrogate calibration not yet run as a separate
acceptance gate).  **Open:** is p=7 specifically a 28.6 Hz beta-band
intrinsic oscillation marker, or a numerical artifact of the
sevenfold-rational density at q_max=200?  Phase 31 monkey3_gratings
showed p=2 dominance at q_max=200 in one recording while p=7 holds
across the cohort — the prime-2 result is recording-specific, suggesting
p=7 is the class signal.  Calibration: does the validated RF infrastructure
produce expected p-adic signatures on synthetic Wigner ensembles?

### p=7 enrichment in Allen natural_movie_one (per-window scope)

The finding is that on Allen Neuropixels awake-mouse-V1 sessions,
per-window p-adic at q_max=200 shows p=7 enrichment in natural_movie_one
windows: mean z = +3.49 across 4 Cre lines (Pvalb +3.81, Sst +2.90,
Vip +1.97, wt +1.75), 28/60 windows z>2 (47%), all 4 Cre lines
positive.  At full-recording scope these same sessions are null
(mean z = −0.14 spontaneous, −0.44 natural_movie_one).  **Engine: RF
(p-adic v4) at per-window scope.**  **Mechanism status: open.**  The
cross-substrate finding is a temporal-scope inversion: pvc-11
anesthetised has long-coherence p=7 (visible at full-recording, washes
out per-window), Allen awake has short-coherence p=7 (visible
per-window, washes out at full-recording).  **Disciplines cleared:**
per-window RF engine at q_max=200, cross-Cre-line replication (4/4
positive), within-substrate consistency (mean z positive across 60+
windows), surrogate-Poisson per-window via z-score baseline.
**Disambiguation status: DATA_PATHWAY_BOUNDED (Phase 32c,
2026-05-11).**  The substrate-vs-state disambiguation for the
cross-substrate p=7 asymmetry requires awake-macaque-V1 spike-sorted
public data with recording structure comparable to pvc-11 / Allen
(≥ ~30 simultaneously recorded V1 units, multi-minute conditions
covering natural-movie or equivalent + spontaneous + gratings).
**Phase 32c surveyed the public-data pathway and found this comparator
does not currently exist** under the bounded-ingestion constraint.
Chen 2022 / TVSD provide MUAe only (would trigger §7.ter.19 failure
mode); Cadena 2019 / Coen-Cagli 2015 provide spike-sorted units but
60-ms image-flash structure with no per-window natural-movie
equivalent and ~10 units per session; CRCNS pvc-5 has the right
structure (spike-sorted multi-electrode V1 + 15 min spontaneous +
gratings) but awake/anesthetised state is ambiguous in public
metadata.  Four forward options enumerated in Phase 32c (§7.ter.43):
(1) accept the confound permanently in framing; (2) partial test on
Cadena 2019 with recording-structure-mismatch caveat (~3 days);
(3) verify pvc-5 state via Chu et al. 2014 paywall access (~1 hour)
and run if awake (~1-2 days); (4) wait for Neuropixels-NHP field
maturity (12-24 months) or pursue lab collaboration.  **Option 3 is
the cheapest next step and is currently pending.**  Until Option 3
resolves or Option 2 runs, the cross-substrate p=7 finding's
species-vs-state interpretation remains structurally undecidable
with current public data, *not* merely "awake-macaque data would
help if we had it" — the data-pathway bound is the load-bearing
constraint, and the publication framing must reflect that.

**Disciplines newly emphasised:** cross-Cre-line replication (4/4
genetically distinct cell populations positive: Pvalb +3.81, Sst +2.90,
Vip +1.97, wt +1.75) is the discipline that makes the awake-mouse-V1
p=7 finding more robust than a single-Cre-line signal would be; it is
not "extra evidence" alongside the other disciplines, it is the
discipline that lets the finding survive a "you've found a single-cell-
population artifact" objection.  **Phase 32a closes the
stimulus-content axis (2026-05-11):** pvc-11 natural-movie per-window
p=7 was extracted from the Round 4 parquets — monkey1_natural_movie
and monkey2_natural_movie together, 10 windows total — at mean window-z
= −0.253, 0/10 windows z>2.  Both recordings classify PER_WINDOW_NULL
on p=7 individually.  Against Allen's mean window-z = +3.49 across the
same protocol, **stimulus content is ruled out as the load-bearing
axis** (PER_WINDOW_SUBSTRATE_CONSISTENT verdict).  Natural-movie
viewing alone is insufficient to produce per-window p=7 in
anesthetised macaque V1.  **Outstanding:** cross-recording within
Allen (which sessions carry the signal more strongly), per-window
stationarity within the natural_movie_one period (do the 19/30 z>2
windows have predictable temporal placement, or are they uniformly
distributed — i.e., is "windows-z>2" itself stationary or bursty?),
per-cell decomposition (is the per-window p=7 a population-aggregate
effect or driven by a subset of high-rate units), and the still-
load-bearing **awake-macaque-V1 or anesthetised-mouse-V1 comparator**
to disambiguate state-vs-substrate.  **Open: the candidate
interpretation now narrows from three axes to two.**  Pre-Phase-32a
the candidate space was {stimulus, substrate, state}; post-Phase-32a
it is {substrate, state} with stimulus ruled out.  The supported claim
is: "anesthetised macaque V1 and awake mouse V1 differ in per-window
p=7 production during natural-movie viewing, with the difference
*not* mediated by stimulus content."  Macaque-vs-mouse and
anesthetised-vs-awake remain confounded.  Every external statement of
the finding must say "anesthetised-macaque vs awake-mouse" and *not*
"anesthetised vs awake" or "macaque vs mouse" until the disambiguating
comparator is run.  **Also surfaced by Phase 32a (richer-than-
anticipated):** pvc-11 natural-movie *does* carry per-window p-adic
structure at p=2 (mean z = +2.53) and p=3 (+2.20); Allen carries
per-window enrichment at p=2 (+7.92), p=3 (+3.23), p=7 (+3.49), and
p=13 (+2.64).  **The cross-substrate axis is prime-specific, not
presence-vs-absence of per-window structure.**  A per-prime
substrate-systematic profile may be the more interpretable framing
than the current p=7-centric one.  Also open: whether the Allen
drifting_pooled p=2 STATIONARY signal (5+/12 sessions) is a parallel
finding or a different phenomenon, and whether pvc-11
monkey2_gratings_movie's p=2 PER_WINDOW_STATIONARY (mean z = +5.15)
and monkey2_noise_movie's p=2 mean z = +8.16 — both surfaced by
Phase 32a's broader-prime extraction — constitute a separate finding
category worth its own discipline pass.

### Cross-engine substrate-systematic pattern (Allen INDEPENDENT_AXES with both axes novel; pvc-11 underpowered)

The pattern is that the NNS engine (F1/F0 ↔ rep_med) and the RF engine
(p=7 enrichment) point in the same substrate-systematic direction:
pvc-11 anesthetised macaque V1 on one side, Allen awake mouse V1 on
the other.  **Engine: cross-engine NNS + RF.**  **Mechanism status:
ruled-out-as-SHARED_AXIS on Allen; pvc-11 underpowered.**

**Phase 32b ran the cross-engine correlation discipline (2026-05-11).**
Per-recording (pvc-11) and per-session (Allen) Spearman ρ between the
within-recording/within-session F1/F0 ↔ rep_med ρ and the per-recording
/per-session p=7 score, then cross-recording/cross-session Spearman of
the two.  On Allen: **ρ = −0.086, p = 0.872** (n = 6 sessions with
per-window p-adic), robust across four scoring variants (|ρ| ≤ 0.093
all four).  Pearson r = −0.355 (p = 0.489) — directionally larger but
not significant at n = 6.  On pvc-11: ρ = +1.000 on n = 3 recordings,
which is the only Spearman value achievable when three points
rank-align and is **uninformative** at this sample size (exact-
permutation minimum p ≈ 0.167).  The n = 3 limit is intrinsic: F1/F0
requires drifting-grating stimulus, and only the 3 pure-gratings
recordings (monkey1/2/3_gratings) have F1/F0 measured.

**Verdict on Allen: INDEPENDENT_AXES.**  Sessions that contribute most
to the F1/F0 ↔ rep_med negative-direction Allen finding are **not**
preferentially the same sessions that contribute most to the per-
window p=7 Allen finding.  The two engines are reading independent
substrate-systematic axes that happen to share direction — not
projections of one underlying substrate-systematic axis.

**Verdict on pvc-11: UNDERPOWERED at the per-recording level.**  The
analysis cannot be run on more than 3 recordings without a different
NNS-engine substrate-systematic statistic or a per-cell-level
decomposition that conflates within-recording and between-recording
variation.

**Disciplines cleared:** within-substrate Spearman on Allen at session
aggregate (n=6, four scoring variants); **per-cell decomposition on
Allen (Phase 32b per-cell follow-up, 2026-05-12): n=465 H1∩ARS cells
across the 6 sessions, target ~ Williamson FA loadings with
condition-matched FA fit (200 ms bins, sqrt-stabilised, CV up to 8
factors).  Per-window p=7 mean z ORTHOGONAL on FA-nmo (R²=0.113
[0.047, 0.248]) and on raw per-cell properties (R²=0.045); rep_med
ORTHOGONAL on FA-drift (R²=0.113 [0.078, 0.198]) and on raw per-cell
properties (R²=0.150); ks_gue_med ORTHOGONAL on FA-drift (R²=0.126)
but PARTIAL on raw per-cell properties (R²=0.386, OSI coef +0.493
dominant — recovers the H1 cross-substrate-locked finding at per-cell
resolution on Allen).  Verdict: BOTH_ORTHOGONAL — per-window p=7 and
rep_med are both novel substrate-systematic axes outside the Williamson
FA decomposition AND outside the standard per-cell tuning properties.**
**Outstanding:** pvc-11 substitute NNS-engine substrate-systematic
statistic that doesn't require gratings stimulus, for cross-recording
per-recording-level test on the pvc-11 side; higher-rank FA sensitivity
(max_factors > 8) on Allen as a bound on the BOTH_ORTHOGONAL classification.

**Substrate-specific FA decomposability (secondary observation from
the per-cell pass):** Phase 27 Analysis 2 on pvc-11 H2 sessions had
ks_gue_med ~ FA R² = 0.73–0.80 (SUBSUMED); Phase 32b per-cell on
Allen 6 sessions has ks_gue_med ~ FA-drift R² = 0.126 (ORTHOGONAL).
Same Williamson methodology, same max=8 factors, similar n_units per
session.  On Allen ks_gue_med is captured by raw OSI directly
(R²=0.386).  The H1 axis is cross-substrate locked, but its
representation differs by substrate: FA-loaded on pvc-11, OSI-direct
on Allen.  This is supporting context for the BOTH_ORTHOGONAL
verdict, not a framing pivot.

**Publication-framing implication.**  Pre-Phase-32b the cross-engine
direction match could be cited as second-engine corroboration of the
substrate-systematic finding (a stronger claim).  Phase 32b at session
level reduced this to two independent findings about the same substrate.
Phase 32b per-cell sharpens to **two independent findings, each on an
axis that the standard noise-correlation FA does not capture and that
the standard per-cell tuning properties do not capture**.  The
substrate differs on at least three FA-independent axes (H1
OSI-ks_gue_med, F1/F0-rep_med, per-window p=7), with the first
captured by per-cell tuning on Allen, and the second and third novel
at per-cell resolution.  The §7.ter.10 band-invariance question
narrows further: two formally distinct engines pick out the same
substrate direction because the substrate differs on multiple
FA-independent axes simultaneously.

---

## Mechanism findings

### K-axis aggregate-IEI structure under order-parameter locking (Kuramoto)

The Phase 30/31 finding is that the +0.10 ks_med drift observed in the
Kuramoto K-sweep traces to **order-parameter-driven aggregate-IEI
structure development under locking**, not rate-distribution narrowing
per se.  Across 3 seeds, ρ(|r|, agg_ks_med) = +0.925 vs ρ(rate_std,
agg_ks_med) = −0.503; |r| (the Kuramoto order parameter) is the
stronger predictor of aggregate ks_med than rate_std.  **Engine: NNS**
on simulated Kuramoto spike trains.  **Mechanism status: known.**  This
is the cleanest "we know what produces this signal" finding in the
mechanism category, because the simulation is by-construction.  The
publication-relevant vocabulary update is: cite **|r|, not rate_std**
when explaining the K-axis NNS-engine drift.  **Disciplines cleared:**
multi-seed (3 seeds), stationarity check (non-overlapping-window NNS:
0/15 Analysis 1 cells and 0/54 Analysis 2 cells flagged for time-
varying classification), rate-matched surrogate.  **Outstanding:** none
specific to this finding — it is the simulation result, not a real-data
finding.  **Open:** this mechanism story applies to *simulated* Kuramoto;
real-data Kuramoto-match was independently FALSIFIED (see Phase 30
NO_MECHANISTIC_MATCH below), so the K-axis mechanism does not transfer
to a positive mechanism story for cortical V1.

### Rate-matched +0.23 Δks residual is within-cell rate-stratified

The Phase 31b finding is that the +0.23 Δks_med residual that remains
after rate-matched-Poisson surrogate correction is **carried by the
low-rate oscillators within each (K, σ) cell**: ρ(Δks, rate) = −0.847
in modal-agreement band σ ∈ [0.4, 0.8].  High-rate oscillators within
the same cell converge to rate-matched-Poisson surrogate.  **Engine:
NNS.**  **Mechanism status: known** (it is a property of the residual
within the simulation, identified by stratifying).  The
publication-relevant methodological commitment is: per-cell rate-matched
surrogate is **necessary but not sufficient** for clean dynamics-only
signal isolation — rate-stratified within-cell comparison is required
as the next discipline.  **Disciplines cleared:** rate-stratified
within-cell at the source (the simulation).  **Outstanding:** none
on the simulation side.  **Open:** the methodological generalisation
to real data — every real-data finding that currently rests on
rate-matched-Poisson surrogate should be re-examined with within-cell
rate-stratified comparison.  H1, DSI, F1/F0 have been done (Phase 31b
Follow-ups 2, 4).  H2 spatial-scale, p=7 enrichment, and the GRB 230307A
TR side-finding have not.

### monkey1_spontaneous p=7 coherence time ~60–120 seconds

The Round 4 finding is that pvc-11 monkey1_spontaneous is the *only*
recording in the 15-recording pvc-11 cohort where p=7 is PER_WINDOW_
STATIONARY (4/5 windows z>2 at q_max=200, full-recording z = +9.77 also
satisfied).  Window lengths are on the order of 60–120 seconds.  This
gives a coherence-time estimate for the p=7 structure on this specific
recording.  **Engine: RF (p-adic v4) at per-window scope.**  **Mechanism
status: open.**  **Disciplines cleared:** per-window stationarity on
the only stationary case (other 14 recordings are PER_WINDOW_NULL).
**Outstanding:** alternative window-length sweep to refine the
coherence-time bound (60–120 s is a coarse range; a 10–600 s sweep would
locate the actual coherence time), per-cell decomposition (does the
p=7 stationarity originate from specific units within the recording),
cross-recording check (is monkey1_spontaneous's stationarity unique to
this animal/condition or are there comparable spontaneous recordings
in other cohorts).  **Open:** the long-coherence interpretation
(~minute timescale beta-band intrinsic structure) versus a recording-
specific artifact (e.g., monkey1 had unusually stable preparation, low
electrode drift) cannot be distinguished from the current data.

---

## Negative-elimination findings

### Phase 30: Kuramoto does NOT provide a mechanism story for ARS findings

> **AXIS-INCOMPLETE CORRECTION (2026-05-31, Phase-36 two-axis audit):** the "(1) classical K-sweep:
> INSENSITIVE" outcome below was read on the REPULSION axis only (rep_int/quadrant, NNS engine — note
> "**Engine: NNS**"). Re-checked on the CLUSTERING axis (CV/mass<τ of the aggregate pooled train, K-sweep
> 0→2 K_c, order parameter R as marker): the clustering axis SEPARATES desync→sync (CV sep +0.67
> in-sample / +0.46 out-of-sample N=200, same sign, tracks R) where rep_med stays flat (sep −0.07/−0.05,
> quadrant BR_artifact throughout). So "INSENSITIVE" refines to **`REPULSION-AXIS-INSENSITIVE /
> CLUSTERING-AXIS-SENSITIVE`** — Kuramoto (canonical synchronization model) is a CLUSTERING-type substrate
> ([[torus_transition_rigidity_vs_clustering]]), exactly as the Kaneko/Chialvo taxonomy predicts. The
> rate-confound (2) and no-real-data-match (3) conclusions STAND; only the "insensitive" framing is
> refined to name the axis. Effect modest on the pooled-temporal observable (CV 0.5→1.6).
> **TWO INTERPRETABILITY CORRECTIONS (Will's checks):** (i) the repulsion side is NOT cleanly "blind" —
> Kuramoto sits in BR_artifact (rep_int≥0.55, HIGH but flagged non-clean-GUE-fit per arithmetic_toolkit:
> 744-801), a DECLINED regime, not the clean low-rep BL "no-rigidity" zone. So Kuramoto = clustering-
> SENSITIVE / repulsion-**INCONCLUSIVE** (declined), NOT repulsion-blind. (Contrast Kaneko snapshot →
> rep_med 0.0/BL = a CLEAN low-rep negative ⇒ "repulsion-blind" is earned ONLY for Kaneko.) (ii) N was not
> fixed (in-sample N=100 / oos N=200): the same-sign clustering separation holds, but the cross-row
> magnitude compression (CV 0.72→0.52, 1.57→0.98) is the Palm-Khintchine superposition N-effect, NOT
> generalization — clean magnitude needs N pinned. (iii) Do NOT chase the spatial-snapshot for Kuramoto to
> amplify the swing: snapshot CV~√N is the H-D tautology (non-dynamical); the pooled-temporal observable is
> the honest intensive one FOR CLUSTERING — but the snapshot is the RIGHT observable for the REPULSION axis
> (intensive, superposition-free). **RESOLVED (kuramoto_snapshot_repulsion.py):** Kuramoto's repulsion axis
> on the matched SPATIAL SNAPSHOT (N=2000) is CLEAN BL throughout (rep_med→0; desync CV=0.997 Poisson, not the
> pooled-train sub-Poisson 0.72) ⇒ Kuramoto is repulsion-BLIND (upgraded from inconclusive; the BR_artifact was
> a pooled-temporal SUPERPOSITION ARTIFACT). The Kaneko/Kuramoto substrate-split DISSOLVES into an observable
> effect — on the matched snapshot BOTH sync models are clustering-detectable + clean-BL repulsion-blind. The
> per-axis-observable principle is validated by resolving the inconclusiveness.
> **DURABLE GENERALIZATION — this is an INSTRUMENT CONFOUND, not a Kuramoto fact** ([[pooled_rhythmic_repulsion_confound]]):
> pooling near-periodic/rhythmic emitters into one pooled-temporal train manufactures sub-Poisson regularity →
> false high-rep → BR/BR_artifact. Searchable fingerprint = BR/BR_artifact on a pooled-temporal observable with
> rhythmic units; any such banked repulsion positive/decline is provisionally SUSPECT and wants a matched-snapshot
> re-read (clean-BL-on-pooled negatives are SAFE — the artifact makes rigidity, doesn't erase it). QUEUED RE-AUDIT:
> pulsar-timing FIRST (most periodic objects in nature; check Phase 33a pooled-pulsar reads), neural pooled-spike
> next. TAXONOMY SHARPENED: the repulsion axis is ONE-SIDED (resolves sub-Poisson/rigid, collapses ≥Poisson onto
> BL — shown: rep_med 0.025→0.0 while CV 0.997→2.87); clustering axis = super-Poisson side; POISSON is the pivot
> where both go blind ⇒ a near-Poisson-throughout transition (invisible to both) is a buildable FALSIFICATION
> calibrator. GUARDRAIL: the 2.87-vs-Kaneko-50 magnitude COHERES with magnitude↔ΔR but does NOT test it
> (Kaneko≠Kuramoto in family/topology/N) — coherence, not evidence; magnitude↔ΔR pending a clean within-GCM sweep.
> See AUDIT_TWO_AXIS_FINDINGS.md + kuramoto_snapshot_repulsion.py.
>
> **RE-AUDIT + MECHANISM CORRECTION (2026-06-01, RE_AUDIT_CONFOUND_FINGERPRINT.md).** (a) Pulsar-timing
> re-audit DONE: **Phase 33a is NOT a confound suspect** — NANOGrav reads are super-Poisson CLUSTERING
> (raw-TOA CV 9.7–14.7 / rep_med 0.02–0.04, z_rep −123 to −597; epoch-collapsed CV 1.2–2.5), the OPPOSITE
> side of Poisson from the confound's manufactured rigidity; STRUCTURAL_MISMATCH uncorrupted (per the
> asymmetry rule, clustering/low-rep reads are SAFE). "Most periodic objects" didn't fire because TOAs are
> folded-template aggregates clustering by schedule — never the per-pulse layer. (Doc-label note: the
> findings doc's "mass<0.3 = BR_artifact indicator" is backwards — high mass<0.3 = low rep = clustering, and
> the pilot used a κ=0.3 proxy, not the real quadrant diagnostic, so no BR_artifact was ever assigned.)
> (b) **The confound MECHANISM was WRONG and is corrected: it is TEMPORAL-GRID QUANTIZATION, not superposition
> anti-bunching.** A clean synthetic shows pure periodic superposition in CONTINUOUS time → CV→1
> (Palm-Khintchine), never →0; the sub-Poisson appears only on a time GRID. Proof: Kuramoto desync K=0 N=100
> (identical 24671 spikes) refining dt 0.005→0.0005 raises pooled CV 0.72→0.95 and flips the repulsion
> quadrant **BR_artifact (rep 0.75) → TR (rep 0.16)**; the N-scaling (CV 0.82→0.20 for N 50→500) is the same
> (higher N → higher pooled rate → IEI nears dt → worse quantization). Corrected fingerprint: BR/BR_artifact
> on a pooled-temporal observable where **mean-pooled-IEI ÷ time-resolution ≲ a few** = SUSPECT. Diagnostics:
> snapshot re-read (best), or refine resolution / decimate rate. HEADLINE + snapshot-fix + per-axis-observable
> principle all SURVIVE; only the mechanism (and hence the sharper diagnostic) changed.
>
> **GUARDRAIL ITEM RESOLVED + FALSIFICATION CALIBRATOR CONFIRMED (2026-06-01).** (a) magnitude↔R, previously
> coherence-only, is now WITHIN-SUBSTRATE EVIDENCE (phase36/magnitude_vs_R.py + MAGNITUDE_VS_R_FINDINGS.md):
> sweeping the COUPLING ε at fixed (N,K,Δ) — the pure R-knob — with R measured directly, the N-robust
> clustering magnitude mass<τ is a MONOTONE (rank-corr +0.995) N-INVARIANT (curve overlays |Δmass|=0.002
> across N=1500/3000) function of R. √N-trap confirmed (saturated CV 38→54 ≈ ×√2 while mass<τ saturates 0.999
> at both N). Sharpens the guardrail: the old "2.87-vs-50" was a CV comparison — the √N-contaminated measure;
> a valid cross-substrate magnitude test needs mass<τ-at-matched-τ, not CV. Cross-substrate magnitude open but
> now well-posed. (b) The Poisson-pivot taxonomy's FALSIFICATION CALIBRATOR is BUILT + CONFIRMED
> (phase36/falsification_calibrator.py + FALSIFICATION_CALIBRATOR_FINDINGS.md): Arm A (Gamma-renewal CV sweep
> through the pivot) — rep_med 0.34(sub,TR)→0.022(pivot,BL)→0.0(super), mass<0.3 0.033→0.259→0.567, k=1 blind
> on BOTH, two axes partition exactly as predicted; Arm B (exponential marginals held EXACT, serial
> correlation 0→0.95) — BL throughout, a genuine long-range transition INVISIBLE to both axes (could have
> fired, didn't). Adds an addressability bound: correlation-only transitions at fixed marginal are in the
> pivot blind spot.

Phase 30 ran ARS on classical and stochastic Kuramoto networks across
the canonical (K, σ) parameter space and located the existing pvc-11 /
Allen / Phase 27 findings on the resulting Kuramoto phase-space map.
Outcome triple: (1) classical K-sweep: INSENSITIVE — aggregate modal
= BR_artifact at every K from 0 to 2 K_c; (2) (K, σ) phase-space:
RATE_REGIME_CONFOUNDED — σ-axis drives 10.3× rate inflation that
dominates classification, K-axis modal variation = 0 at every fixed σ;
(3) real-data on map: NO MECHANISTIC MATCH — 156/160 well-powered real-
data rows have no Kuramoto match; only 1 clean match.  **Engine: NNS.**
**Mechanism status: ruled out.**  The negative-elimination conclusion is
that Kuramoto-class coupled-oscillator dynamics do not produce ARS
signatures matching cortical V1 data.  **Disciplines cleared:** full
(K, σ) parameter space sweep, multi-seed, non-overlapping-window
stationarity check.  **Outstanding:** alternative mechanism candidates
(Stuart–Landau coupled networks, Wilson–Cowan E/I rate models, coupled
Hodgkin–Huxley, latent-state generative models, non-oscillator
drift-diffusion-with-coupling) — none have been tested yet.  **Open:**
the locked H1/F1/F0/H2 findings stand in their negative-elimination
posture without a positive mechanism story.  Phase 30 does *not* augment
them with a Kuramoto-class mechanism; the load-bearing forward direction
for mechanism interpretation is now alternative coupled-oscillator and
non-oscillator models.

### Kuramoto per-window p-adic null

A Round 4 follow-up applied per-window p-adic v4 to the Phase 30
Kuramoto K-sweep cells and found no above-threshold p-adic class signal
across the K-axis.  At q_max=30 the above-threshold rate grows +13.4 pp
from K=0 to K=2 K_c (locking-driven small-q amplitude concentration),
but this is at the q_max=30 threshold which is independently known to
have 95.6% false-positive rate vs rate-matched Poisson surrogate.  At
q_max=200 (the validated threshold) the Kuramoto sweep does not produce
per-window p-adic structure.  **Engine: RF (p-adic v4) per-window.**
**Mechanism status: ruled out for Kuramoto.**  Together with Phase 30
NNS-engine null, this confirms that Kuramoto-class formalism does not
match the deployed real-data p-adic findings either.  **Joint-null
framing:** the K-axis mechanism entry above establishes that order-
parameter-driven aggregate-IEI structure produces NNS-engine signal in
simulation; the present null establishes that this same aggregate
structure does *not* produce per-window p-adic structure.  Kuramoto
therefore fails to match cortical V1 **on both engines and at both
timescales** — NNS full-sequence (Phase 30 Analysis 3), NNS per-window
stationarity (Phase 30 stationarity addendum), RF full-sequence
(Round 4), RF per-window (this entry).  That is a four-way joint null,
substantially stronger than any single-engine, single-timescale
elimination, and the publication framing should state the Kuramoto
elimination as four-way joint, not as a single NNS-engine result.

### Phase 28: H2 is not a local-spatial-cluster phenomenon at any tested scale

Combining Phase 27 Analysis 3 (pvc-11 Utah array 400–600 µm:
CONTRA-OHIORHENUAN, local less structured than recording-wide) with
Phase 28 (Allen Neuropixels <300 µm: SPATIAL-SCALE-DEPENDENT, local
100–300 µm bin the LEAST TR-structured among three tested bins): the
H2 surviving structure is *not* a local-cluster phenomenon at any
spatial scale we can test.  **Engine: NNS spatial.**  Ohiorhenuan 2010's
high-order correlation finding (<300 µm local, not 600–2500 µm distant
in anesthetised macaque V1) **does not extend** to the ARS H2 signal
in either of the two spatial regimes available.  **Open:** the H2
surviving structure operates at supra-300 µm spatial scales or is not
spatially localized at all; whether it has a spatial structure beyond
"recording-wide aggregate" is an open question that would need
intermediate-scale data (700 µm–2000 µm Neuropixels-array configurations
or specialised electrode arrays) to test.

### Phase 25: history-coupled GLM as H2 elimination target — FIT-CEILING

A 24-cell grid (n_lags × bin_ms × variant) of history-coupled-GLM
surrogates was tested as the next stricter elimination target after the
Phase 22b Aitchison-null battery.  Zero FIT-PROPER cells: canonical
parameterisation collapses to kernel; unconstrained parameterisation
runs away with invariant kernel shape across all configurations.
Multi-frame STA does NOT reduce runaway (stim-mis-routing diagnostic
FALSIFIED).  Co-finding: V1 anesthetised-macaque spike trains have a
positive temporal correlation structure (median unconstrained-GLM
history-kernel max ~+0.75) invariant across n_lags ∈ {1, 4, 8} and
bin_ms ∈ {5, 10, 20, 40} ms.  **Engine: GLM null target (adjacent to
NNS).**  **Outcome:** the H2 history-coupled-GLM elimination claim is
**methodologically untestable** in the Phase 25 model family.
**Methodological implication:** future coupled-GLM surrogate work on
V1 should use canonical (non-positive) history parameterisation, not
unconstrained.  **Open:** an alternative elimination-target family
(state-space models with latent population modulation, jittered-bin
surrogates, Hawkes-process surrogates with kernel constraints) has not
been tried.

### GRB 230307A 909 Hz QPO (Chen 2025) — substantive fail

Phase 23 targeted replication at the GRB_NEXT_STEPS-specified time-
slice adjustment (100 ms sub-windows, q_max=50) detects no signature
distinguishing the published 45–47 s claim window from surrounding
sub-windows at the 909 Hz q-band; real and lightcurve-modulated Poisson
surrogate both ~zero rep_int_q delta.  **Engine: NNS.**
Phase 21's methodology-only verdict on the published QPO claim is
reaffirmed.  The Phase 26 side-finding (broadband TR signature in the
late-prompt t=26–30 s window) was reframed as a **per-cell rate-regime
feature of ARS classification**, not energy-band sensitivity
(FALSIFIED), not aspect-mediated, not unique to the time window:
Spearman ρ(per-cell rate, TR fraction) = −0.48 in [26, 30) s and
−0.89 in [10, 14) s control window.  At per-cell rate, the lightcurve-
modulated Poisson surrogate reproduces most of the TR signal.
**Open:** the per-cell rate-regime structure of ARS classification on
event-rate-changing data (GRB lightcurves are non-stationary by
construction) is itself a methodological finding worth its own discipline
audit — when does ARS classification depend on per-cell rate, and what
is the right rate-matched surrogate in non-stationary regimes?

---

## Methodological findings

### §7.ter.10 band-invariance proposition

Any p-adic profile engine with the architecture `{filter Farey rationals
→ analytical-passage → unit-mean-normalised NNS → KS}` is invariant
under linear time scaling and **cannot** detect prime-base asymmetry on
stationary signals.  Three engine versions (v1, v2, v3) failed
acceptance for this structural reason before v4 — which abandons
unit-mean normalisation and routes through the RF engine on indicator
functions — passed.  This proposition is *why* the deployed tool has a
two-engine architecture: the NNS engine cannot carry per-prime
asymmetry on stationary signals, period.  Any future phase work that
proposes to read per-prime structure from `joint_q_profile` is
attempting an architecturally impossible measurement.

### Two-engine architecture (NNS + RF)

The deployed classifier (`joint_q_profile`) produces per-q ks_gue_q and
rep_int_q that are q-flat scalars under unit-mean normalisation (std
~10⁻⁵ across q), with per-q variation carried by the Ramanujan-Fourier
amplitude axis only.  This was derived in Phase 31a and verified
empirically.  **Implication:** when a finding cites per-q discrimination
(e.g., q=6 in monkey1_spontaneous H2 surviving), that q-band selectivity
is RF-engine driven; the NNS engine produces q-flat behaviour.  Any
publication-track framing must say which engine is load-bearing for the
specific claim.  The "Farey-bank channels" image is apt for the
RF engine and for the parallel `pll_bank.pll_bank_cpu` infrastructure;
it is **not** apt for the deployed NNS classifier.

### Rate-stratified within-cell as standard discipline

Rate-matched Poisson surrogate is necessary but not sufficient for
dynamics-only signal isolation.  Phase 31b Follow-ups established that
within-cell rate-stratified comparison is the right cleaner
discrimination.  H1 pvc-11 SURVIVES_STRATIFIED, DSI pvc-11
PARTIAL_SURVIVAL (monkey2 sign-flip in high-rate tertile, ultimately
not-significant), F1/F0 pvc-11 PARTIAL_SURVIVAL, F1/F0 Allen
SUBSTRATE_SYSTEMATIC_SURVIVES_STRATIFIED at session-aggregate.
**Commitment:** every future ARS finding that rests on a rate-matched
surrogate should also be checked at within-cell rate-stratified
resolution before being claimed as locked.

### Per-window surrogate as standard discipline

The Phase 31f H2 finding established that full-sequence surrogate
survival does not imply per-window surrogate survival
(monkey2_gratings_movie passes full-sequence but is WINDOW_MIXTURE
at per-window).  Round 4 p-adic confirmed this generalises (Allen
natural_movie p=7 visible per-window only; pvc-11 p=7 visible
full-recording only).  **Commitment:** every future ARS surrogate-
survival claim must specify scope (full-sequence vs per-window) and
report results at the claim-appropriate scope.  The per-finding scope-
vs-claim audit is in `data/phase31b_results/SURROGATE_SCALE_AUDIT.md`.

### q_max=200 required for p-adic discrimination

q_max=30 (the historical default) is **underpowered** for absolute-
threshold p-adic discrimination: rate-matched-Poisson surrogates pass
the §7.ter.13 1.5× threshold 95.6% of the time.  The §7.ter.13
acceptance threshold is q_max=200-validated and only applies at
q_max=200.  At q_max=30, matched z-scores (real vs rate-matched
surrogate) are the right metric; absolute thresholds are not.  This is
the kind of methodological constraint that gets lost between phases
unless made explicit at the tool-state level.

### Capability-vs-application gap

ARS measures certain things well (point-process classification into
Poisson / GOE / GUE / TR / BR with associated metrics; per-prime
arithmetic asymmetry via RF v4 at q_max=200; cellular-property /
recording-aggregate correlations).  Whether *any given application* is
in its capability envelope is a separate question that must be answered
by calibrator-zoo runs, induction-on-noise tests, and extractor-
invariance probes per METHODS.md.  Several intermediate "findings"
turned out to be artifacts of an extractor or pipeline rather than
properties of the signal: LLM internal-state Wigner-class (§7.ter.19,
threshold-upcrossing TR induction), EEG θ-band zero-crossings (§7.ter.6,
bandpass filter artifact), σ̂ alignment between primes and LLM (find_peaks
gap-distribution matching).  The capability envelope is not the same
as the "tested-and-cleanly-applies" envelope.  Findings outside the
latter are exploratory until the application's extractor/pipeline has
been calibrator-vetted.

### §7.ter.19 as dataset-selection discipline (not just within-analysis)

§7.ter.19 originally surfaced as a **within-analysis** discipline:
when applying `scipy.signal.find_peaks(prominence=0.3)` (or any peak-
detection extractor) to autocorrelated continuous traces, the spacing
statistics reflect the extractor's gap structure, not the signal's
dynamics.  The diagnostic move was "check the extractor on noise of
equivalent statistical character before trusting the classification."
The Phase 32c experience demonstrated that the same failure mode
operates **one level up** — as a **dataset-selection** discipline.
When a candidate dataset provides only continuous traces (MUAe / MUA
envelope / LFP) and no spike-sorted single units, *running the ARS
pipeline on that data requires a peak-detection extractor by
construction*.  The choice to use such a dataset commits the analysis
to the §7.ter.19 failure mode before any analysis-time discipline can
be applied.

Concretely: Chen 2022 (1024-channel awake macaque V1+V4 resting state,
21-42 min sessions) and Papale 2024 TVSD (31 Utah arrays awake V1/V4/IT)
both provide MUAe / MUA only.  They are nominally attractive (1000+
channels of awake macaque V1, substantial recording durations,
publicly available CC-BY 4.0) but **using them forces the failure
mode**.  No within-analysis discipline can recover.  The dataset-
selection move is to **rule them out** before the pipeline runs, not
to attempt classification and then notice the artifact.

The generalization: a dataset's compatibility with the ARS pipeline
is determined by **whether its native output is spike-sorted single
units (compatible) or continuous-trace aggregate signal (forces
peak-detection, §7.ter.19-flagged)**.  This is a hard gate, not a
soft preference.  Datasets that would require user-side spike-sorting
(Kilosort + manual curation on raw `.ns6` or NWB ephys) are
"compatible-after-substantial-preprocessing," not "directly
compatible."  Phase 32c made this filter explicit; future cross-
substrate / cross-domain phases should apply it at the data-selection
stage rather than discovering it mid-analysis.

**How this propagates beyond the immediate question:** for any
future ARS application to a domain with multi-electrode population
recording — cortex (other regions / species), retina, hippocampus,
striatum, motor cortex, etc. — the dataset-selection question to ask
first is "does this dataset publish spike-sorted unit-level output,
or only multi-unit / LFP aggregate signal?"  The latter is a hard
no-go without user-side sorting work.  This bound is more constraining
than the field's general sense of "what's available," because most
public neural-recording releases (especially recent high-channel-count
ones) prioritize MUA/LFP publication over spike-sorted-unit
publication.  The ARS-compatible subset of the public-data ecosystem
is smaller than the public-data ecosystem.

### Cross-domain extension and published-data-product compatibility (Phase 33a)

Phase 33a (2026-05-11) extended the §7.ter.19 dataset-selection
discipline from neural-domain MUA-vs-spike-sorted to a **cross-domain
generalisation about published data products**.  The test substrate
was the NANOGrav 15-year pulsar timing array — a domain chosen for
its well-characterised substrate physics (neutron star rotational
dynamics) and its stationarity-by-construction.  The verdict:
**STRUCTURAL_MISMATCH at the published-product level.**

A NANOGrav TOA is not a single pulse arrival.  It is a template-
matched timestamp derived from a folded-and-averaged pulse profile,
where folding has already aggregated ~10⁴-10⁵ individual pulses
within a 10-second sub-integration into one phase-reference
measurement, and the 30-minute observation epoch then contributes ~50
TOAs at different frequency channels and sub-bands.  Per-pulsar TOA
count: hundreds-to-tens-of-thousands over a 15-year baseline.

The empirical pilot (5 representative NANOGrav pulsars: B1855+09,
J0030+0451, J0613-0200, J1909-3744, J0740+6620; direct-statistics
implementation per §7.ter.10 band-invariance, no full Farey
decomposition) tested two extraction modes:

  - **Mode A (raw TOAs as events):** CV 9.7–14.7 (vs 1.0 Poisson),
    mass<0.3 = 96–98 %, median normalized spacing = 0.0000.  z_KS in
    the hundreds-to-thousands.  The signature is *not* pulsar physics
    — it is the radio-backend frequency-channel structure of the
    receivers, which produces ~50 near-coincident TOAs per observation
    by construction.
  - **Mode B (epoch-collapsed):** CV 1.2–2.5, KS_Poisson z = +5 to
    +25.  Still non-Poisson, but the deviation now reflects
    telescope-scheduling cadence (monthly-ish observation blocks
    irregular due to weather, semester time allocation, Arecibo's
    2020 collapse) — also not pulsar physics.

In both modes, ARS produces strong "signal" against rate-matched
Poisson, but the signal sources are identifiable as apparatus
structure (radio-backend grid; telescope-scheduling cadence) rather
than substrate physics.  Pulsar dynamics are captured by (a) the
folded pulse profile within each observation, and (b) the timing
residual series sampled at the irregular TOA epochs — neither of
which is the inter-TOA spacing distribution that ARS reads.

**The generalisation Phase 33a establishes:** the §7.ter.19
compatibility gate operates not just at "is this MUAe vs spike-sorted"
but at **any published-data-product level where the aggregation has
already happened upstream**.  Pulsar-timing collaborations publish
folded-template-matched TOAs because the GW-detection question lives
in residuals, not in pulse spacings.  Neural-recording labs publish
spike-sorted units or MUAe depending on the lab's primary analysis
question.  Both ecosystems record at event-level resolution; both
mostly don't publish at that resolution.  **ARS's compatibility
envelope is determined by the published-product layer, not by the
recording-resolution layer.**

Concretely: extending ARS to a new cross-domain substrate requires
asking *whether the published data product preserves the event-level
resolution at which ARS's measurement model applies*, before asking
whether the substrate physics is interesting.  Substrates whose
published products are pre-aggregated (folded-template TOAs,
LFP/MUAe, calcium-imaging ΔF/F, fMRI BOLD) are dataset-selection-
incompatible regardless of how attractive the substrate physics is.
Substrates whose published products are event-level (neural spike-
sorted units, financial transaction timestamps, GRB photon counts,
radio interferometer photon timestamps from short-burst events, raw
single-pulse pulsar archives) are dataset-selection-compatible.

This is a hard gate at the cross-domain-survey stage.  Phase 33a's
pilot demonstrates empirically that running ARS on an aggregated
published product produces strong-looking signal that is entirely
apparatus structure — exactly the boundary-readout failure mode the
tool was built to catch, instantiated at the dataset-selection level
instead of the within-analysis level.

**What this does not foreclose:**
  - **Cross-pulsar Hellings-Downs-analog analysis** on residuals is a
    real cross-domain extension target, but requires correlation
    methodology ARS doesn't currently have — different framework, not
    a new application of the two-engine pipeline.
  - **Per-pulse arrival point processes from raw radio archives**
    would be a clean structural match.  Compatible-after-substantial-
    preprocessing (PRESTO/PSRCHIVE pipeline work).  Same shape as
    "Chen 2022 spike-sort-yourself" awake-macaque-V1.
  - **Single-pulse pulsar literature** (giant pulses, nulling
    pulsars, mode-switchers) sometimes publishes per-pulse data and
    would be a clean structural match for a different cross-domain
    phase.
  - **Other pulsar-timing arrays** (EPTA, PPTA, IPTA, MeerTime,
    CHIME/Pulsar) all face the same published-product structural
    mismatch.  The bound generalises across pulsar-timing consortia.

### Cross-domain extension — particle physics (Phase 33b)

Phase 33b (2026-05-11) is the second cross-domain assessment.  Per
the brief's amendment, the published-product-aggregation audit was
applied **at the survey entry point** rather than only at the
structural-assessment stage.  CERN Open Data publishes at multiple
processing levels (RAW, AOD, MiniAOD, NanoAOD, derived educational
CSVs), each with different aggregation status.  The audit identified
that **all bounded-effort accessible levels** are (a) post-trigger
and (b) wall-clock-timestamp-stripped: NanoAOD preserves only
Run/LumiBlock/Event identifiers, not actual collision timestamps;
the LHC 40 MHz BX clock exists at RAW level only, which requires
CMSSW + multi-TB infrastructure to access.

**Time-domain framing: STRUCTURAL_MISMATCH at the published-product
level**, same shape as NANOGrav folded-template TOAs.

**Alternative framing — mass-spectrum as point process in mass
coordinate** (analogous to the LMFDB-zeros instrument-validation
work): each dimuon event contributes one invariant mass M to a 1D
point process in mass space.  Standard Model resonance structure
(Z⁰ at 91 GeV, J/ψ at 3.1 GeV, Υ family ~10 GeV) is the known
physics.  Pilot on CERN Open Data record 545 derived CSVs (Zmumu
10k, Jpsimumu 20k, Ymumu 20k, Dimuon_DoubleMu 100k events; direct-
stats per §7.ter.10 band-invariance; surrogate: rate-matched
uniform-in-mass) produced enormous z-scores everywhere — CV 3.4-82,
mass<0.3 = 0.59-0.84, KS_Poisson z = +247 to +838.  But **the signal
is the known resonance peak structure**, what every CMS Drell-Yan
paper plots on figure 1.  No information above existing methods at
this surrogate level.

**Mass-spectrum framing: STRUCTURAL_MATCH at the instrument-
validation level only.**  Reproduces known physics but adds no
measurement beyond histogramming.

**Combined verdict: STRUCTURAL_MATCH_BOUNDED.**  Particle physics
event data is *not* in ARS's substantive cross-domain envelope at
any bounded-effort published-product level.  RAW-level analysis
preserving BX timestamps is compatible-after-substantial-
preprocessing.  Substantive mass-spectrum analysis would require
physics-aware surrogate infrastructure (Drell-Yan continuum
templates, trigger-efficiency models) that ARS doesn't currently
have.

**Two methodological generalisations that propagate beyond Phase
33b:**

  1. **Processing-level audit must precede structural-match
     assessment** at the survey entry point.  Phase 33b applied this
     per the brief's amendment: identifying that NanoAOD strips
     timestamps *before* running any pilot reframed the structural-
     match question to the mass-spectrum framing where it could
     actually run, and saved the deeper-infrastructure path from
     being attempted unnecessarily.  Future cross-domain phases
     should adopt the entry-point audit ordering.

  2. **Surrogate adequacy is a domain-specific question.**  Rate-
     matched Poisson is the canonical "no-structure" prior for neural
     spike trains because Poisson is the natural null in that domain.
     Other domains have different natural nulls: particle physics has
     Drell-Yan continuum + trigger-efficiency-aware Poisson;
     financial timing has GARCH/Hawkes-process baselines;
     gravitational-wave timing has detector noise spectra.  Uniform-
     in-X surrogates produce trivially-large z-scores in any domain
     where the data was selected to contain known structure — the
     signal is just the selection.  Cross-domain extension to a new
     substrate must audit *whether ARS's existing surrogate set
     captures the domain's natural no-structure prior* before
     interpreting z-scores as evidence.  ARS does not currently have
     a physics-aware-surrogate ecosystem outside neural Poisson-like
     baselines; building one is a substantial framework extension.

**What Phase 33b does not foreclose:**
  - RAW-level CMS / ATLAS data preserving BX-clock event-arrival
    timestamps (compatible-after-substantial-preprocessing).
  - Per-event particle-track timing within a single triggered event
    at AOD/MiniAOD level (sub-nanosecond resolution) — separate
    cross-domain target.
  - Physics-aware surrogate ecosystem development — substantial
    infrastructure investment, different framework than deployed
    NNS+RF engines.
  - Cross-detector replication (ATLAS vs CMS) — sits on top of
    either of the above.

### Cross-domain extension — single-molecule fluorescence (Phase 33c)

Third cross-domain assessment, with a specifically different
epistemic role: single-molecule blinking has theoretically predicted
universality structure (power-law on/off-time distributions, Kuno-
Nesbitt universal exponent α ≈ 1.5), making it an instrument-
validation candidate analogous to arithmetic-signal validation.

Per the brief's amendment, the published-product audit was applied
at the survey entry point.  Single-molecule data publishes at three
processing levels: raw photon-count traces (rare; user-side state-
detection needed = §7.ter.19 trap), state-detected event sequences
(sometimes; post-extractor), and distributional summaries (most
common; past event-level resolution).

**Verdict: STRUCTURAL_MISMATCH at the published-product level +
INSTRUMENT_VALIDATION_BOUNDED at the event-sequence level.**

  - Distributional-summary publication form (most common) is past
    event-level resolution — dataset-selection-incompatible.
  - State-detected event sequences are post-extractor; the state-
    detection methodology is the §7.ter.19 trap.
  - Even with clean event access, ARS's calibrator zoo lacks a
    power-law-mixture universality class — instrument-validation
    against single-molecule theory requires calibrator-zoo
    extension as the blocking step.

**Substantive Phase 33c finding — convergent-validation from the
literature.**  The single-molecule biophysics field has
**independently documented the §7.ter.19 failure mode** in its own
vocabulary as the "binning-and-thresholding distortion" problem:

  - Crouch, Sauer, Schuette 2014 (J Chem Phys 140, 114306): "Real
    power law statistics ... would not be observed as such in the
    experimental data after binning and thresholding.  Instead, a
    power law appearance could simply be obtained from the
    continuous distribution of intermediate intensity levels."
  - Houel et al. 2016 (J Phys Chem C): even change-point analysis,
    the better-than-thresholding method, introduces residual bias
    documented at the event-time level.

Two methodologically distinct fields (ARS / criticality_tool +
single-molecule biophysics) reach the **same conclusion** about
extractor-dependence of inferred event-level structure, by independent
paths.  The §7.ter.19 dataset-selection generalisation is not a
tool-specific quirk but a structural feature of quantitative
measurement on continuous traces.  The boundary-readout discipline
from WHYTHISEXISTS.md is empirically vindicated as a domain-general
principle, not a domain-specific finding.

### Three-domain cross-extension synthesis (Phase 33a + 33b + 33c)

The three cross-domain probes were deliberately sequenced (pulsars
→ particle physics → single-molecule) to surface structural
commonalities and divergences in informative order.  The collective
verdict map:

| Domain                    | Substantive verdict                                  | Instrument-validation verdict       | Compatibility-envelope structure          |
|---------------------------|-----------------------------------------------------|-------------------------------------|-------------------------------------------|
| Pulsar timing (NANOGrav)  | STRUCTURAL_MISMATCH (published-product folded TOAs) | n/a (no theoretical prior available at this product level) | Bounded — published product aggregated past event-level resolution |
| Particle physics (CERN OD) | STRUCTURAL_MISMATCH time-domain; STRUCTURAL_MATCH_BOUNDED mass-spectrum | Mass-spectrum reproduces resonance structure trivially — instrument-validation only | Bounded — NanoAOD strips timestamps; mass-framing accessible but surrogate-inadequate |
| Single-molecule fluorescence | STRUCTURAL_MISMATCH (published-product distributional summaries) | INSTRUMENT_VALIDATION_BOUNDED at event-sequence level (calibrator-zoo extension required) | Bounded — predominant publication is distributional summary; event sequences are post-state-detection |

**Structural commonalities** (the load-bearing pattern):

  1. **All three domains record at event-level resolution at the raw
     measurement layer.**  RAW LHC detector ADC samples, radio
     telescope sub-integration photon timestamps, single-fluorophore
     photon counts at instrumental time-resolution.  The event-level
     data exists.
  2. **All three domains publish at processing levels that have
     aggregated past event-level resolution.**  Folded-template TOAs
     for pulsars; NanoAOD + derived CSVs for particle physics;
     distributional summaries (sometimes event sequences) for single-
     molecule.  The aggregation choice is determined by what the
     community's *primary scientific question* is, which is rarely
     "what universality class does the event-arrival process belong
     to."
  3. **The aggregation is methodology-specific and well-documented**
     in each domain.  Pulsar folding is described in PSRCHIVE/PRESTO
     manuals; trigger algorithms are documented per LHC experiment;
     state-detection is documented in single-molecule papers and
     benchmarks.  The methodology being documented does not make
     ARS-on-the-aggregated-product compatible — it makes the
     aggregation auditable.
  4. **Each domain has independently identified the
     §7.ter.19-equivalent extractor-dependence problem within its own
     vocabulary.**  Particle physics has trigger-efficiency
     systematics; single-molecule has binning-and-thresholding
     distortion (Crouch 2014, Houel 2016).  The dataset-selection
     discipline from §7.ter.19 / Phase 32c / Phase 33a-b-c is
     domain-general.

**Structural divergences** (where the three domains differ from each
other and from neural / GRB data, which ARS handles natively):

  - **Pulsar timing**: aggregation strips time-domain event-level
    resolution; alternative framing (residuals) is a continuous
    series, not a point process at all.
  - **Particle physics**: time-domain stripped at NanoAOD level;
    alternative framing (mass spectrum as point process) is
    accessible but the surrogate-adequacy question is unsolved.
    Physics-aware surrogate construction is the missing
    infrastructure.
  - **Single-molecule fluorescence**: theoretically predicted
    universality structure (power-law mixture) is not in ARS's
    calibrator zoo.  Calibrator-zoo extension is the missing
    infrastructure.

**ARS's substantive cross-domain envelope** (as of 2026-05-11, post-
Phase 33c):

  - **In the envelope:** neural spike-sorted unit recordings (the
    training domain); GRB / X-ray binary photon-arrival timing
    (§7.ter.32, §7.ter.36 — primary publication is individual photon
    timestamps); arithmetic signal validation (Riemann ζ, L-function
    zeros, prime counts — point process in spectral coordinate).
  - **Bounded** for instrument-validation only: mass-spectrum framing
    on particle physics (reproduces known structure but adds no
    information); single-molecule event sequences IF calibrator-zoo
    extended.
  - **Out of the envelope at bounded effort:** pulsar timing TOAs;
    particle physics time-domain; single-molecule distributional
    summaries.
  - **Compatible-after-substantial-preprocessing:** raw radio
    archives (PRESTO/PSRCHIVE pipeline work); RAW-level LHC data
    (CMSSW + multi-TB); raw photon-count traces with user-side
    state-detection (committing to the extractor up front).

**The substantive cross-domain extension finding**: ARS's compatibility
envelope is structural to the published-data-product layer across
domains, not incidental to any specific dataset.  Cross-domain
extension to a new substrate must:

  1. **Audit the published-product processing level** at the survey
     entry point (Phase 33b-amendment lesson).
  2. **Audit the natural no-structure prior** of the target domain —
     rate-matched Poisson is canonical for neural, but other domains
     have process-specific natural nulls (Drell-Yan continuum,
     power-law mixtures, GARCH/Hawkes, detector noise spectra).
     Uniform-in-X surrogates produce trivially-large z-scores
     wherever data has been selected to contain known structure.
  3. **Check whether the substrate's predicted universality structure
     is in ARS's calibrator zoo.**  If not, calibrator-zoo extension
     is a blocking step for instrument-validation.

These three pre-pilot audit questions are now standard discipline
for cross-domain ARS phases.  Future cross-domain briefs should
apply them at the survey entry point and report the verdict before
committing to ingestion or pilot work.

**Convergent-validation finding (the cross-domain meta-result):**

The §7.ter.19 dataset-selection generalisation is empirically
vindicated as a domain-general structural feature, not an ARS-
specific lesson.  The single-molecule biophysics field independently
formalized the same discipline as "binning-and-thresholding
distortion."  The particle physics community has trigger-efficiency
systematics that formalize the same concern.  The pulsar timing
community has folded-template-bias systematics.  All four communities
(ARS, single-molecule, particle physics, pulsar timing) converge on
the same structural conclusion about extractor-dependence of
event-level structure, by independent paths.

This convergence strengthens the boundary-readout discipline from
WHYTHISEXISTS.md as a load-bearing meta-principle: distinguishing
field from apparatus is *the* whole job of quantitative measurement
across domains, and the methodologies that survive in mature fields
all incorporate some version of this distinction.

---

## Bounded or exploratory findings

### Number-theoretic instrument validation

The toolkit reproduces statistics consistent with the GUE conjecture
for Riemann ζ (first 2,000 Odlyzko zeros: KS_GUE_q = 0.041, rep_int_q
= 0.425; heights ~10⁶: KS_GUE_q = 0.012–0.015) and consistent with
Katz–Sarnak family-symmetry predictions for L-function families (LMFDB
87 elliptic curves ~10,000 zeros: bulk GUE, edge separation by root
number; Dirichlet L-functions q ≤ 149, 630 primitive non-trivial
characters, 4.05M pooled spacings: bulk GUE, conductor-normalised
γ₁ Sp/U separation at p = 0.001).  Primes ≤ 10⁶ log-density unfolding:
σ̂ = 0.048 [0.023, 0.073]; twin primes ≤ 10⁷: σ̂ = 0.093 [0.068, 0.118].
**Engine: NNS.**  These are reported as **instrument-validation outputs
only** — they do not extend the corresponding literatures, but they
do verify that the tool reads what arithmetic-side literatures predict
it should read.  **Open:** none on the validation side; the open
question is whether ARS produces *novel* arithmetic-side measurements
beyond reproducing existing literature, and the current answer is no.

### Physical / biological signal classifications (§7.ter.4 through §7.ter.18)

The tool classifies these test inputs as expected:
- USGS earthquake catalog M ≥ 4.5: Poisson-clustered (mass<0.3 = 0.33),
  consistent with ETAS aftershock dynamics.
- Adamatzky fungal mycelium spike pool (1,470 events): super-Poissonian
  (mass<0.3 = 0.65) on the dataset tested.
- Solar X-ray flares (NOAA GOES, M+ class): Poisson-clustered.
- Binance BTCUSDT trade timing (one trading day): essentially random
  (BL quadrant).

These are **single-dataset classifications** on small samples; they
should be read as findings about the specific datasets tested rather
than as findings about those domains broadly.  **Open:** all four are
candidate domains for ARS application if the right calibrator panel
and rate-stratified discipline is run — none has been pushed past the
"first-pass classification" stage.

### EEG θ-band zero-crossings — falsified

PhysioNet EEGMMIDB 32-subject cohort gave mass<0.3 ≈ 0.001 (Wigner-class
reading), but this was diagnosed as a **bandpass filter artifact**
rather than a property of the underlying neural signal: the
zero-crossing extractor on bandpass-filtered noise produces the same
signature.  **Outcome:** retracted, classified as an extractor artifact.
This is the canonical worked example of the capability-vs-application
gap in the physical-signal domain.

### LLM cascade — fully retracted

The toolkit was applied to transformer residual stream activations and
attention dynamics across four architectures (Qwen 2.5 3B,
Phi-3-mini-4k-instruct, TinyLlama 1.1B, Mistral 7B v0.1) and eight
extractor mechanisms.  After three rounds of diagnosis (§7.ter.19 through
§7.ter.23), **no measurement remains that can be attributed to the model
rather than to the extraction methodology**.  Retracted claims:
LLM residual-stream Wigner-class, cross-architecture σ̂ invariance,
LLM-primes parameter-space neighbourhood within BR_artifact, two
distinct LLM attention-dynamics families, Wigner-class attention
dynamics on three by-construction extractors, empirical validation of
the Planat 2026 lock-in-phase prediction via Phase 12.  The negative
result is bounded: it applies only to extraction-via-the-tested-
mechanisms; it does not address RMT analysis of LLM weight matrices
(Staats 2024; Martin & Mahoney 2018–2024).  `attention_target_jumps`
produced architecture-discriminating output (Qwen 0.70 vs Phi-3 0.35
in rep_int_q) but reflects argmax-sequence autocorrelation properties,
not a universality-class finding.  **Open:** other extraction
methodologies not tested here might produce measurable structure;
RMT-on-weights is a separate methodology entirely.

### Phase 20 BGP route timing PoC

Cascade trajectory and topology-aware analysis on BGP route-event
timing produced PoC-level classifications that have not been extended.
See BGP_NEXT_STEPS.md.  **Status: exploratory.**

### Phase 21 / 23 / 26 GRB timing PoC

GRB 230307A is now bounded as described in the negative-elimination
section.  Phase 21's broader GRB PoC framework remains exploratory
beyond the Chen-2025 909 Hz claim, which was substantively failed.

### Planat-adjacent number-theoretic instrument scope

The framework's analytical content is Planat's; ARS implements that
framework as software.  The toolkit does not extend Planat 2002–2026
analytically.  The Phase 12 lock-in-phase prediction perturbation sweep
ran cleanly but the Wigner-class baseline it was tested against was
retracted, so Phase 12 is no longer interpretable as a Planat-prediction
test.

---

## Arithmetic-spectral arc (Phases 34a–34f, appended 2026-05-16)

**Honest headline.** The arithmetic-side arc produced **no substantive
arithmetic discovery**.  Its value is (i) methodological — a family of
new disciplines, several of which caught real instrument bugs — and
(ii) instrument-validation: the Sarnak-anomaly calibrator replicated,
and the Sato-Tate engine bounded-validated against a *proven* theorem.
Everything substantive is NULL, instrument-validation, bounded, or
data-acquisition-blocked.  Nothing here is "locked-positive."

### 34a–34d — arithmetic orthogonal-channel survey (RF + p-adic v4 / NNS)

- **Mertens / Liouville sign-changes (34a/b):**
  `NULL_IN_ORTHOGONAL_CHANNELS` beyond the support / random-walk null.
  Dual-layer cross-phase: PARALLEL_SIGNAL@wrong-null +
  PARALLEL_NULL@right-null.
- **ζ / Dirichlet / EC L-zeros (34c):** 5/6 `NULL_BEYOND_RMT`; EC
  root-minus q=17 `AMBIGUOUS` (a pooled-substrate right-null
  methodology gap, not a signal).
- **Gaussian / Eisenstein prime angles (34d):**
  `RW_SHAPE_CONFIRMED_AT_FINITE_X` — the Rudnick-Waxman 2019
  prime-angle variance shape, with the saturation deficit resolving as
  a finite-X correction at X=10⁸ (Eisenstein hits the RW asymptote
  within 1σ).  Both substrates BL-bulk (an earlier TR was a §7.ter.22
  threshold artifact).  Cross-phase = METHODOLOGICAL_CONSISTENCY, not
  "convergent null."
- **Disciplines added (durable):** support-set-respecting nulls;
  right-null-is-substrate-specific; false-positive-equivalence-class
  typology (substrate-side vs machinery-side; pooled-substrate sub-pool
  sweep mandate; prime-K seduction); seed-replicate-near-boundary
  (§7.ter.22-application); bulk-vs-global-moment readout (RW Prop 5.3
  forces σ²(K,X) as the complement to bulk-ARS on Wigner-Dyson β
  nulls); stride-decimation destroys prime-angle structure (full-N
  required on S¹ unit-orbit-quotient substrates).

### 34e — Γ₀(N) Maass Sarnak-anomaly calibrator: REPLICATED

`SARNAK_ANOMALY_REPLICATED_AT_GAMMA0_N_SQUAREFREE` across 6 squarefree
levels {91,95,85,77,93,87}: bulk-Δ NNS BL on all 6 in 20/20 subsample
seeds; corrected Berry-Robnik ρ_GOE ≈ 0.126 (near-Poisson, just above
the 0.09 pure-Poisson fitter baseline); Sato-Tate semicircular KS
p 0.22–0.77.  **Instrument-validation, not discovery** (the Sarnak
anomaly is 30+ yr lit-confirmed).  The phase34f synthetic-validation
harness caught a real **Berry-Robnik fitter bug** (un-normalised PDF →
pure Poisson fitted ρ≈0.44; §7.ter.57) which retroactively amended the
Test-2 numbers (conclusion strengthened, not weakened).  N=1 SL(2,ℤ)
trivial level pending LMFDB access (data-availability note).

### 34f-G / 34f-E — 3-D Bianchi pipelines: VALIDATED_READY_TO_FIRE; substantive DATA_ACQUISITION_BLOCKED

3-D Bianchi Weyl-unfolding pipeline (λ=r²+1, cubic; Humbert-direct
volumes **pinned** with a self-test against the Then-2003 Picard
anchor) built and synthetic-validated (6/6 gates) for **both** Picard
(34f-G, *replication* leg) and Bianchi-Z[ω] (34f-E, **first-measurement**
leg — asymmetric-label discipline: no published anchor, never
"replication").  Substantive bulk-NNS is **DATA_ACQUISITION_BLOCKED**
on both: Then 2003's 13,950 Picard eigenvalues unpublished; no
accessible Z[ω] Maass dataset; de-novo Hejhal-on-ℍ³ is multi-week.
Pipelines are ready-to-fire on acquisition; no underpowered result was
fabricated.

### BCGNT-2025 lit-lock + the proven-theorem-calibration tier

Boxer–Calegari–Gee–Newton–Thorne 2025 proves Ramanujan + Sato-Tate
**unconditionally** for *cohomological* (regular-algebraic
parallel-weight) Bianchi forms over CM fields — **NOT** the
non-cohomological Bianchi-**Maass** substrate (definitional; the §B.4
Ramanujan-conditional caveat stands for the Maass cells).  Added a
**third asymmetric-label tier to METHODS §1 — proven-theorem
calibration** (sibling to empirical-anchor and
structural-extension-first-measurement) + the two-regime
Ramanujan-conditionality discipline + CM/non-CM (and bc) stratify-
before-pool.

### 34f-cohomological-H — bounded instrument validation against a proven theorem (AMENDED)

First ARS calibration against a *proven theorem*.  Data fully resolved
in-environment (Cremona `bianchi-data` `newforms/` catalogs, schema-
documented; 40,030 Q(i) + 42,343 Q(√−3) forms).  §6 engine + §4 decode
(idealnorm; bc=1 base-change signature exact, BCGNT Ramanujan bound
exact on ~82k forms) **independently validated** before any statistic.

**Verdict (corrected, the original `METHODOLOGY_VALIDATED_AT_FINITE_P`
RETRACTED):
`COHOMOLOGICAL_H_SATO_TATE_CONSISTENT_TO_FINITE_PRIME_DEPTH_DISCREPANCY`.**
The engine is consistent with the BCGNT-proven semicircular up to the
**effective-Sato-Tate finite-prime-depth discrepancy** (Thorner /
Murty–Sinha; *not* Chen-2019/RW — that was a misattribution; no
functional form was fitted).  KS decreases monotonically with per-form
prime depth at the effective-ST rate; on the depth-sufficient
subpopulation (≥800 primes/form) KS reaches ~1.4–3× the n-floor
(E[Dₙ]≈0.87/√n), but the **bulk corpus** (~100 primes/form) is
depth-limited to a ~12–78×-floor residual.  §6/§4 validate
engine+decode, so the residual is the corpus prime-depth limitation,
**not** an engine/decode defect; **floor-level validation is not
achieved and not achievable at this corpus depth**.  CM stratum is a
**one-sided discrimination control only** (≠ semicircular; not matched
to its own ½δ₀+arcsine measure).  Instrument-validation, bounded as
stated; **not** a discovery; **does not touch the Q(√−3) Δ-closer**.

**The load-bearing methodological output (§7.ter.57 sharpening):** a
statistic is only interpretable against its own sample-size/regime
floor — for KS the verdict is KS/(0.8687/√n) vs *per-form prime depth*,
never KS alone, never a large-n p-value (which →0 for any
infinitesimal deviation).  Synthetic pre-flights must validate at
*realistic* n, not convenient n.  **Four instrument-regime errors of
this one class were caught and corrected within this single cell**
(the §6 single-draw KS-p gate; the §7 large-n KS-p criterion; the
Chen/RW misattribution; the headline KS-statistic read at the wrong
sample size — the last caught only on Will's review).  Sobering
demonstration that the *form* of a discipline can be applied while a
fresh instance of the same error slips through one level down; the
generalisation is now stated at the level of "statistic vs its own
regime floor," not any single instrument.

### Q(√−3) three-coordinate Δ-closer — STILL BLOCKED

The substantive Q(√−3) three-coordinate joint statement (§D.4) remains
**34f-E-Δ-Maass-data-acquisition-blocked**.  cohomological-H is H-side
instrument validation and explicitly does **not** advance it (Sato-Tate
is the universal/null calibrator, not the signal-bearing Δ coordinate).
34d-E angle + 34c χ₋₃ zero data are cached; only 34f-E-Δ blocks closure.

### Open frontier (arithmetic side)

- **Phase 35 — Almost-Mathieu / quasi-periodic-Schrödinger arc**
  (queued, design-settled, not briefed).  Reframed (after a critical
  review) as **transition-diagnostic instrument-validation, NOT
  AM measurement** (nothing novel to find on AM spacing statistics).
  35a calibrator-extension (Fibonacci/DGY multifractal class via
  IDS/gap-labelling unfolding; clock+band-perturbation AC class
  anchored at the λ=0 exact clock, λ* by the analytical AC bound) /
  35b α-ensemble-null transition-diagnostic validation, supercritical +
  λ→1⁻ only / 35c optional sub-quadrant.  λ=1 explicitly out (Cantor
  spectrum — renormalisation, a different instrument).  See
  [[phase35_am_arc_design]].
- **Data-acquisition blocks:** Then 2003 Picard eigenvalues; Z[ω]
  Maass; N=1 SL(2,ℤ) Maass — all pipeline-ready, externally blocked.
- **EPISTEMIC_STATE refresh discipline:** this arc is appended, not
  woven into the V1-era "Locked / Newer / Mechanism" taxonomy above —
  the arithmetic arc has essentially no "locked-positive" entries to
  slot there, which is itself the honest signal.

---

## Open questions across findings

The temporal-coherence-asymmetry mechanism story is the largest live
open question, and Phases 32a–c progressively narrowed and bounded it.
pvc-11 anesthetised macaque V1 carries long-coherence p=7 structure
(full-recording visible, per-window null in 14/15 recordings); Allen
awake mouse V1 carries short-coherence p=7 structure (per-window
visible in natural_movie_one across all Cre lines, full-recording
null).  **Phase 32a ruled out stimulus content as the load-bearing
axis** (pvc-11 natural-movie per-window p=7 is null at mean z =
−0.253, 0/10 windows z>2, against Allen's +3.49 / 19/30).  The
remaining candidate mediating axes — species (macaque vs mouse) and
state (anesthetised vs awake) — remain confounded in the pvc-11/Allen
comparison.  The natural test is **awake macaque V1 or anesthetised
mouse V1**.  **Phase 32c (2026-05-11) surveyed the public-data pathway
for awake macaque V1** with comparable recording structure (spike-
sorted single units, ≥ ~30 V1 units per session, conditions covering
natural-movie or equivalent + spontaneous + gratings).  Verdict:
**MIXED, leaning DATA_AVAILABLE_BUT_INCOMPATIBLE for bounded-effort
ingestion.**  Every awake-macaque-V1 dataset evaluated has at least
one disqualifying feature: Chen 2022 (1024-channel V1+V4 awake
resting state) and TVSD/Papale 2024 (31 Utah arrays awake V1/V4/IT)
provide MUAe / MUA only — no spike-sorted single units — and using
them would trigger the §7.ter.19 peak-detection failure mode.
Cadena 2019 and Coen-Cagli 2015 provide spike-sorted awake V1 but use
60-ms image-flash trial paradigms with no per-window natural-movie
equivalent and ~10 units per session.  CRCNS pvc-5 has the right
structural match (spike-sorted multi-electrode V1 + 15 min spontaneous
+ gratings) but awake-vs-anesthetised state is ambiguous in public
metadata (likely anesthetised given the Chu et al. 2014 methodology
profile).  The substrate-vs-state confound is **DATA_PATHWAY_BOUNDED** — not
"awake-macaque data would help if we had it," but "spike-sorted
public awake-macaque V1 with comparable recording structure does not
currently exist."  Four forward options surface from Phase 32c:
(1) accept the confound and frame the cross-substrate p=7 finding
permanently as "anesthetised-macaque vs awake-mouse" without
species-vs-state disambiguation; (2) partial test on Cadena 2019 with
recording-structure-mismatch caveat (full-recording p=7 only, not
per-window); (3) verify pvc-5 state (paywall access to Chu et al.
2014) and run if awake; (4) wait for Neuropixels-NHP field maturity
(12-24 months) or pursue direct lab collaboration — external-
engagement decision.  **Option 3 is the cheapest next step (~1 hour
of paper reading) and is currently pending.**  The bottleneck is not
recording technology but the spike-sorted-public-data ecosystem; the
§7.ter.19 hard compatibility gate (now formalized as a dataset-
selection discipline, not just a within-analysis one) makes
"convenient" MUA-only datasets unusable without methodology compromise.
**A secondary observation from Phase 32a:** the cross-substrate axis
is prime-specific, not presence-vs-absence — both substrates carry
per-window p=2 enrichment during movies (pvc-11 mean z = +2.53 on
natural-movie, +5.15 PER_WINDOW_STATIONARY on monkey2_gratings_movie;
Allen +7.92).  The p=7 axis is the substrate-systematic one; p=2 is
substrate-shared.  A per-prime substrate-systematic profile may be a
more interpretable framing than p=7 in isolation.

Whether F1/F0 substrate-systematic and p-adic substrate-systematic
share an underlying biological mechanism or are independent
substrate-axes is now resolved on Allen.  **Phase 32b ran the cross-
engine correlation discipline on Allen at session aggregate (n = 6
sessions): ρ = −0.086, INDEPENDENT_AXES.**  **Phase 32b per-cell
decomposition follow-up (2026-05-12) ran the within-session per-cell
regression discipline on n = 465 H1∩ARS Allen cells: BOTH_ORTHOGONAL
— per-cell per-window p=7 ORTHOGONAL on FA-nmo (R²=0.113) and on raw
per-cell properties (R²=0.045); per-cell rep_med ORTHOGONAL on
FA-drift (R²=0.113) and on raw per-cell properties (R²=0.150).**  The
two engines on Allen read substrate-systematic axes that are
independent of each other *and* independent of the Williamson
noise-correlation FA *and* independent of the standard per-cell
tuning properties.  pvc-11 remains underpowered at the per-recording
level (n = 3 gratings recordings carry F1/F0; the movie + spontaneous
variants don't have F1/F0 by stimulus construction).  The publication
framing is **two independent findings, each on a novel axis** —
substrate differs on at least three FA-independent axes (H1
OSI-ks_gue_med, F1/F0-rep_med, per-window p=7), with the first
captured by per-cell tuning properties on Allen, and the second and
third novel at per-cell resolution.

The OSI / DSI / ks_gue_med triangle has internal structure that has
not been mapped, and this is the most mechanism-suggestive finding-
level open question in the document.  Cross-substrate: DSI magnitude
exceeds OSI magnitude in awake mouse V1 (+0.269 vs +0.363 sign-and-
magnitude-comparable, but mouse V1's heavier direction selectivity
makes DSI the stronger axis), while OSI dominates in anesthetised
macaque V1 (+0.720 vs +0.223).  Within-species: are H1-passing units
the same units that carry the DSI signal, or are these orthogonal
axes within (OSI, DSI) space that both project onto `ks_gue_med`?
What does the joint (OSI, DSI, ks_gue_med) distribution look like
per-unit, and is the joint structure substrate-systematic in a way the
marginals don't reveal?  This is finding-level rather than meta-level,
but mapping it could surface the kind of structural relationship that
would give H1 and DSI a mechanism candidate rather than two independent
correlations.  The data exists; the discipline is a within-unit joint
analysis that hasn't been run.

Whether the §7.ter.10 band-invariance proposition has implications
beyond the immediate engine-design lesson is open.  The proposition is
about what the NNS engine *cannot* see; whether the RF engine has a
parallel structural limitation that hasn't been surfaced yet is
unexamined.  The fact that two formally distinct engines pick out the
same substrate-systematic direction (the previous question) is the kind
of structural coincidence that might motivate looking for a band-
invariance-style theorem about the RF engine, or for a deeper
representational claim that subsumes both engines.

Whether any current finding rises to the "reach out to a study group"
threshold and which group would be the right one is the meta-question
the work currently keeps deferring.  The candidates: a number-theoretic
methods group around Planat or LMFDB could engage on the engine
validation against L-function statistics; a systems-neuroscience group
around the Smith / Kohn / Allen Brain Observatory ecosystem could
engage on the F1/F0 substrate-systematic finding and the H2 spatial-
scale closure; a methodologically-adjacent group around dethroning-
Fano-style V1 variability work (Charles 2018) could engage on the
methodological contribution.  The current finding-set is rich enough
that any one of these is a defensible direction; the constraint is
which one the work is in shape to defend.

The per-cell rate-regime structure of ARS classification on
non-stationary signals (GRB Phase 26) is **a structural-decision
question, not a per-finding question**, and the document flags it as
such.  The Phase 26 reframe — that lightcurve-modulated Poisson
surrogate reproduces most of the TR signal at per-cell rate —
established that ARS classification on time-varying-rate inputs has a
per-cell rate-regime dependence that isn't yet codified as a
discipline.  Until it is, **every non-stationary-rate application is
in capability-uncertain territory**: GRBs (rate evolves with the burst),
BGP route timing (rate evolves with network events), earthquake
sequences (aftershock rate decays), solar flares (cycle-dependent
rate), Binance microstructure (volatility regimes), and any future
domain with intrinsic rate non-stationarity all sit in this category.
The structural decision is binary: either (a) add "per-cell rate-
matched on rate-changing data" as a ninth discipline and audit the
non-stationary back-catalogue against it, or (b) bound ARS's
capability envelope to stationary-rate inputs and label every
existing non-stationary-domain result accordingly.  The decision is
load-bearing for the publication framing of every domain in §7.ter.4
through §7.ter.18 except the explicitly-stationary ones, so it cannot
defer indefinitely.

Whether the rate-stratified within-cell discipline (the standard
elaboration that Phase 31b proved necessary) has a per-finding
back-application backlog is open.  H1, DSI, F1/F0 have been done on
pvc-11; F1/F0 on Allen done.  H2 spatial-scale at within-cell-rate-
stratified has not been done.  p-adic enrichment at within-cell-rate-
stratified resolution has not been done (and the right operational
definition of "per-cell" for an aggregate p-adic measure is itself a
small design question).  The GRB 230307A TR side-finding has not been
done.  Whether to push the rate-stratified-back-application through
the existing findings, or to treat the new discipline as "applies to
future findings only," is a scoping decision.

### V1-side closure status (as of 2026-05-12)

The V1 substrate-side has reached closure on what bounded-effort
public data permits.  **Closed (this consolidation window):** Phase 28
spatial-scale at <300 µm on Allen NP (SPATIAL-SCALE-DEPENDENT, local
bin LEAST TR-structured — Ohiorhenuan engagement closed across both
substrates, §7.ter.40); Phase 32a stimulus-content axis on pvc-11
natural-movie (PER_WINDOW_SUBSTRATE_CONSISTENT, content ruled out as
load-bearing axis, §7.ter.41); Phase 32b cross-engine correlation at
session aggregate on Allen (INDEPENDENT_AXES, §7.ter.42); Phase 32b
per-cell decomposition follow-up (BOTH_ORTHOGONAL with secondary
substrate-specific ks_gue_med decomposability finding, §7.ter.50);
Phase 32c awake-macaque V1 data-pathway audit (DATA_PATHWAY_BOUNDED,
§7.ter.43).  **Outstanding at the bounded-effort level:** the
substrate-vs-state confound (species × awake-vs-anesthetised) for the
cross-substrate p=7 asymmetry, which sits in DATA_PATHWAY_BOUNDED
territory — not "data would help if we had it" but "spike-sorted
public awake-macaque V1 with comparable structure does not currently
exist."  Resolution pathways available: (1) accept and frame as
anesthetised-macaque vs awake-mouse permanently; (2) partial test on
Cadena 2019 with structure-mismatch caveat (full-recording p=7 only);
(3) verify pvc-5 state (paywall paper-reading, ~1 hr — cheapest next
step, currently pending); (4) wait for Neuropixels-NHP maturity or
pursue direct lab collaboration (12–24 month horizon).  pvc-11 per-
cell decomposition for the cross-engine analysis is the other
analytic option that exists at bounded effort (within-session per-cell
F1/F0 ↔ rep_med ↔ p=7 on the 3 pure-gratings recordings), but pvc-11's
per-window p=7 is null (PER_WINDOW_NULL on natural-movie, full-
recording on spontaneous + gratings only), so the natural analog of
Phase 32b per-cell on pvc-11 would be cross-cell within-recording on
the full-recording p=7 score — informative but not a direct test of
the Allen finding.

Further substrate-side extension would require either new public
data ingesting (Neuropixels-NHP becoming available, awake macaque
V1 with comparable structure) — which would change the bound — or
own-extractor preprocessing of currently-inaccessible substrates
(PSRCHIVE/PRESTO on raw pulsar archives per Phase 33a, CMSSW on
RAW-level CMS data per Phase 33b, ds.cms-style raw imaging per Phase
33c).  The "compatible-after-substantial-preprocessing" pathway is
documented but is not on the immediate roadmap.

---

## Phase 36 — Torus-breakdown / quasiperiodicity→chaos extension (2026-05-31, in progress)

Extends `transition_diagnostic` along the torus-breakdown axis (linearization = Harper/Almost-Mathieu,
the operator the leg is validated on). Scope (with Will): Spine + Track 4; discrete-map calibrators
first, strict gate. New vocabulary: **`NOT-SPECTRALLY-SEPARABLE`** — a transition whose dynamical
regimes are not robustly (out-of-sample) separable on the spectral/quadrant ARS fingerprint via any
tested event observable, even though a non-spectral (e.g. combinatorial) signature persists; bounds
the event-extracted spectral instrument for that transition class, not the substrate.

- **Track 0 regression gate — PASS.** All 5 banked verdicts reproduce bit-exact (deterministic AM
  leg): IDS-leg ratio-free (converges in L, no N_ref), zoo-gap 56× sub/sup contrast, 35b no-FP,
  sensitivity floor N≳5×10⁴, logistic+MG loci. NUANCE banked: the 35b auto-verdict is literally
  `UNRESOLVED`; "VALIDATED" = human-adjudicated NO-FALSE-POSITIVE (no quadrant flip); the gate tag is
  `NFP_NO_FLIP_REPRODUCED` and says so (sub-quadrant sensitivity certified separately, item 4). See
  phase36/track0_regression.{py,md}.

- **Track 1.1 Chialvo calibrator — `FAILED — NOT-SPECTRALLY-SEPARABLE` (refined; banked).** Dynamics
  clean (NS onset analytic; torus→Arnold-tongues→chaos via λ₁=0 Benettin at b=0.45,k=0.06, sweep a).
  But the torus→chaos transition is NOT robustly legible on `joint_q_profile`: spike-TIMING observables
  (median/y-upcrossing) read clock-like in every regime (fast-oscillation period regime-stable; only a
  combinatorial 2→3 interval-cardinality signature persists — non-spectral). IEI|Δx| both BL
  (quadrant-blind). |Δpeak-amplitude| separated IN-SAMPLE (BL→TR, rep_med 0.046→0.342) but FAILED the
  out-of-sample check (fresh slice b=0.35,k=0.08: both TR, sep −0.067; same torus type reads BL in one
  slice, TR in another ⇒ fingerprint tracks parameters not regime). The out-of-sample guard converted a
  would-be false `DETECTED` into an honest negative. Implications: (1) bounds the event-extracted
  spectral instrument for amplitude-modulation-carried transitions; (2) calibrator-side instance of the
  Track-4 premise — even amplitude-aware *event* extraction loses this transition class, sharpening the
  case that the continuous front-end is the principled tool here, not a luxury. See
  phase36/TRACK1_1_CHIALVO_FINDINGS.md.

- **Track 1.4 Kaneko GCM — REOPENED as a positive-capable generalization test; verdict two-sided
  `REPULSION-AXIS-BLIND_CLASS-WIDE / CLUSTERING-AXIS-SEPARATES_OOS`.** Globally-coupled circle maps,
  headline observable = SNAPSHOT spatial NNS (sorted phases on S¹ → circular gaps; the high-D structure
  Chialvo lacked), regimes marked by sync order parameter R; NOT temporal timing (the reconfirmation
  trap). Feasibility pre-check passed (snapshot gap-CV 1.18→54 across desync→clustered ⇒ test can be
  positive). Result, in- AND out-of-sample (N=1500,K=1.0): **repulsion axis (rep_med) FLAT at 0/BL across
  the whole transition — blind** (⇒ Chialvo's repulsion-axis negative is CLASS-WIDE, not Chialvo-specific,
  spanning temporal AND spatial observables); **clustering axis (CV/mass<τ) SEPARATES robustly**
  (in-sample +36.95, oos +25.89; mass<.3 0.30→0.9997) (⇒ "spectrally invisible" was AXIS-SPECIFIC — the
  right ARS readout sees it). Mechanism = the collective transition is a CLUSTERING transition
  (Poisson→super-clustered), not a repulsion one — exactly the SOC-pair one-sided-fitter blindness
  (rep_int blind to super-Poisson; legible only on mass<τ/CV). Forced-HH + BGKM (ODE) still deferred.
  See phase36/TRACK1_4_KANEKO_FINDINGS.md.

- **Phase-36 UNIFYING TAXONOMY (earned by Track 1.4).** "Quasiperiodicity↔chaos / torus-breakdown" is NOT
  one ARS-class; it splits by which axis reads it: (i) **RIGIDITY-type** — AM metal-insulator (Track 4):
  metal→clock-rigid W1δ floor vs insulator→Poisson; read by the repulsion/rigidity axis (why F2's W1δ
  separated, why the floor was rigidity). (ii) **CLUSTERING-type** — Chialvo + Kaneko: Poisson→super-
  clustered; blind to the repulsion axis (CLASS-WIDE), legible on the clustering axis (mass<τ/CV). The
  pillar-1 GUE↔Poisson-poles lens reads rigidity-type, not clustering-type. **Cross-check DONE:** Chialvo
  re-read on the clustering axis (CV of |Δpeak-amp|) separates torus→chaos +0.196 in-sample / +0.124
  out-of-sample (SAME sign, generalizes), where its repulsion axis flipped sign oos. So Chialvo is a
  confirmed (weak) clustering-type member like Kaneko (strong) — taxonomy CONFIRMED, two members. This
  CORRECTS Track 1.1: its `FAILED / NOT-SPECTRALLY-SEPARABLE` was AXIS-INCOMPLETE (repulsion-axis only);
  honest verdict `NOT-REPULSION-SEPARABLE` but CLUSTERING-AXIS-DETECTABLE.
- **Track 3.1 pvc-11 — deferred** (premise was a Track-1-calibrated lens, which the Chialvo negative
  shows does not exist for this transition class via event-spectral readout).
- **Track 4 continuous front-end — DONE; neither front-end PROMOTABLE, but the continuous arm
  demonstrably CARRIES the transition (positive falsification-gated result).** φ(t) bridge sound
  (|φ| late/early 0.08 metal → 0.99 insulator, monotone). **F1** (Hilbert phase on wavepacket return
  amplitude → rotation-number NNS): at pinned α=0 gives a MONOTONE λ-bracket signal (W1δ 0.097→0.001
  metal→insulator), band-robust — exactly the transition signal event-extraction (Chialvo) could not
  produce. BUT not α-robust at N=2584 (sep −0.096 at α=0, collapses to ≈0 at α=0.13/0.27) — the
  inherited phase-knob confound; and it CANNOT be factored out because φ(t) needs eigenVECTORS (O(N²),
  ~20GB at N=5×10⁴) so F1 is capped at moderate-N where α-noise lives. Tag
  `CARRIES_TRANSITION_α-CONFOUND-UNRESOLVABLE_AT_REACHABLE_N`; resolution path = O(N) Gauss-quadrature
  spectral-weights (Lanczos), queued. **F2** (KDE-DOS → IDS-unfold): separates robustly (insul−metal
  +0.35 across all bandwidths) but metal W1δ 0.48–1.0 ≠ banked floor (≈0.005) — the floor is
  load-bearing on the EXACT rotation-number IDS, not a smoothed density. Tag
  `SEPARATES_ROBUST_BUT_NO_FLOOR`. NET: §7.ter.19 reaffirmed with positive, knob-named evidence; the
  continuous arm is the right tool for this transition class but needs (a) exact IDS not smoothed,
  (b) O(N) spectral-weights to escape the α-confound. No real continuous data run. See
  phase36/TRACK4_FINDINGS.md.

- **Track 4 FOLLOW-UP (Lanczos O(N) local measure) — F1 blocker RESOLVED definitively (answered, not
  punted).** Lanczos-from-|e₀⟩ → Jacobi → Gauss nodes/weights = local spectral measure dμ₀ at O(m·N),
  NO N×N eigenvectors; φ(t)=Σ w_k e^{−iθ_k t}. Calibrator gate PASSED ([[synthetic_validate_fitters]]):
  at N=1200 reproduces exact φ(t) bit-exact incl. the insulator FLOOR (0.00135); sub-N m=1500 (0.19·N)
  converges metal+floor at N=8000; `none`-reorth high-N config guard exact — the ghost-eigenvalue risk
  did NOT forge a false floor. High-N α-resolution at N=50000, m=2000 (the eigenvector-walled regime,
  now reachable): α-sweep seps [−0.096,+0.002,−0.003,−0.112], mixed-sign, **bit-identical to N=2584** ⇒
  **α-confound PERSISTS, INTRINSIC, N-converged.** φ(t) depends on the local measure which CONVERGES in
  N (already by ~2584) ⇒ F1 readout N-invariant ⇒ the α-dependence is NOT finite-N substrate noise
  (unlike the spacing leg's α-ensemble, which collapses by N≳5e4) but an intrinsic property of the
  wavepacket-phase observable. F1 DEFINITIVELY NOT promotable. New tag
  `α-CONFOUND_INTRINSIC_N-CONVERGED_NOT_PROMOTABLE`. Methodological gem: the two legs respond to α
  DIFFERENTLY (eigenvalue-spacing finite-N / φ(t)-phase limit-intrinsic) — only the high-N test (enabled
  by the validated O(N) Lanczos measure) distinguishes them. See phase36/lanczos_local_measure.py.

- **Track 4 F2 RESOLVED (KPM global-DOS, phase36/kpm_dos.py) — the floor is spectral RIGIDITY, not
  density.** Principled DOS estimator (Chebyshev moments via stochastic trace + Jackson kernel, O(M·R·N),
  no diagonalization), gated at N=1200 vs the banked floor + the α-invariance free check. The α-invariance
  check PASSED (KPM metal W1δ across α spread 0.0088 — recovered quantity α-independent, estimator
  FAITHFUL/ergodic as predicted) but the floor did NOT recover (M=256→4096: W1δ 1.10→1.15, rails high).
  Together ⇒ the missing floor is a RESOLUTION limit, NOT an ergodicity failure. Structural reason: the
  metal→floor is spectral RIGIDITY (near-uniform AC levels) needing IDS accuracy ≪ mean spacing
  (~bandwidth/N) i.e. M≫N moments (> diagonalization cost). So NO moment/kernel DOS recovers the floor
  cheaply — the floor is exact-level-POSITION info (rotation-number/Sturm IDS, O(N²)), not density info
  (KDE smooths it away, KPM moment-truncates it away — same root cause). F2 tag
  `ERGODIC-SEPARATES_FLOOR-IS-RIGIDITY-NOT-DENSITY`. **Track 4 CLOSED — both front-ends mechanism-resolved:
  the continuous arm CARRIES the transition (robust, phase-invariant SEPARATION via F2 — confirmed ergodic)
  but NOT the floor's fine RIGIDITY; F1 not promotable (intrinsic locality-α). The continuous front-end's
  precise value: it buys the separation, not the rigidity.** See phase36/kpm_dos.py + TRACK4_FINDINGS.md.

---

## Instrument-confound + long-range arc — the marginal-vs-class reckoning (2026-06-05)

This section folds in the holistic read of the whole toolkit and records
the arc that re-examined the observable most deployed verdicts rest on.

**The repo is two interwoven programs sharing one engine.**  (A) The
phase-numbered ARS investigation (`RESULTS.md`, phases 5→37): does ARS
reproduce known universality classes, and find structure in arithmetic /
neural / physical / dynamical substrates?  (B) The cross-substrate
"operator-IS-substrate" landscape (`cross_substrate/PROGRESS_REPORT.md`):
fingerprint 18–25 substrates, the AM≡Fibonacci approximability result, and
the instrument-confound/long-range audit.  They share `arithmetic_toolkit`
+ `axes` and cross-pollinate (the neural pillars live in both), but A
accumulates LOCKED claims while B audits them.  The friction between the
two is the current state of the tool, and this arc is where B caught up
with A.

**What the arc built** (`cross_substrate/`): apparatus subtraction
(`instrument_confound.py` — dead-time, thinning, sort-merge, three-zone
bracket); the long-range discriminator (`longrange_discriminator.py` —
Σ²(L)/Δ₃(L) with the Wigner-renewal decoy); the trial-PSTH external-rate
unfold (`trial_psth_unfold.py`, decoy-battery-gated); the RF decoy battery
(`rf_decoy_battery.py`); and the combined-quadrant marginal test
(`quadrant_marginal_test.py`).

**The load-bearing finding: NNS certifies the marginal, not the class.**
`ks_gue` / `rep_med` / the quadrant read the gap *histogram* (marginal),
not the long-range correlation structure that *defines* GUE vs Poisson.
Proof: the Wigner-renewal decoy is indistinguishable from real GUE on NNS
but separates >20× on Σ²/Δ₃.  Confirmed on the deployed quadrant itself —
an order-scramble surrogate (same gap multiset, order destroyed) reproduces
0.87–1.00 of per-q quadrant labels on every real substrate (zeta, primes,
Allen V1, solar); the quadrant is **order-blind by construction** (`rep_int`
is computed on a cumsum of pooled spacings, discarding original order; the
RF `a_q` leg is marginal-dominated, fires on 0–20% of bands, and needs a
near-delta marginal or a sharp bounded-phase grid to fire at all).

**What this downgrades, what it leaves standing:**
- **Arithmetic — confirmed/caveated, not downgraded.**  ζ is *confirmed at
  class level* (ζ_first RIGID_GUE, lens-invariant on Σ²).  L-function bulk
  GUE + edge signatures stand.  *New caveat:* pooled (LMFDB/Dirichlet)
  long-range is MARGINAL_ONLY — pooling Poissonizes the long-range statistic
  (the arithmetic twin of the neural no-pooling rule).
- **Neural — downgraded from class to marginal.**  On real neural data
  *both* NNS poles are marginal-only: 0/100 Allen V1 cells RIGID_GUE; 54/57
  hc-3 NNS-exponential cells NOT process-Poisson.  Cells live in a clustered
  regime and the "poles" are gradients within it.  The per-unit BL/TR
  quadrant is a marginal classification.
- **H1 specifically.**  The marginal correlation (OSI↔`ks_gue`) STANDS in
  full.  The structural reading is walked back: trial-PSTH external-rate
  unfold collapses OSI↔Σ²(clustering) +0.135→−0.077 (null) — the OSI-graded
  clustering was stimulus-driven rate-stepping.  All cells are intrinsically
  clustered (96/100 survive stimulus removal) but uniformly across OSI;
  selectivity is not a clustering determinant and selective cells are not a
  special class.  See the H1 entry's inline downgrade note above.

**Cross-domain envelope (unchanged, reaffirmed).**  ARS reads event-level
timing, so any pre-aggregated published product is structurally
incompatible (NANOGrav folded TOAs, CERN post-trigger NanoAOD, single-
molecule post-state-detection) — §7.ter.19 generalised.  Earthquakes/solar
flares are good calibrators (clustering recovered; declustering moves it
Poisson-ward in the known direction).

**RF engine (this arc).**  Indicator-mode `a_q` is marginal-dominated and
needs a *zoo-calibrated* noise floor (~6, not ~1 — extreme-value-inflated
spectrum max over ~29 bands).  It does not give the RF side a marginal-
escaping observable; the order-scramble decoy + an order-borne positive
control (`rigid_grid_jittered`) confirm it.  Apparatus operators do not
transfer to the period axis (dead time injects no `a_q` peak; thinning
preserves a strong one).  See `rf_aq_marginal_dominated` (memory).

**The durable gain is the methodology**, not any single substrate verdict:
apparatus subtraction, the long-range discriminator + Wigner-renewal decoy,
the external-rate (trial-PSTH) unfold, the decoy-battery pre-deployment gate,
and the marginal-vs-class discipline now standard for every NNS verdict.

**Reconciliation status.**  `RESULTS.md` §8 has a matching subsection
("Reconciliation (2026-06-05): marginal-vs-class — downgrades and what
remains"), with one-line flags at §7.ter.30 and §7.ter.34.  The open
scientific gap is unchanged and now sharper: H1 has a robust marginal
correlate but **no mechanism**, and the structural story that would have
supplied one (selective cells = a distinct level-repulsion class) is the
part the audit removed.

---

*End of state document.  This file is intended to be re-read at the
start of each phase brief, and updated as findings move between
sections (locked → mechanism-known, open → ruled-out,
exploratory → negative-elimination).  Vocabulary commitments
("LOCKED", "WINDOW_AWARE_LOCKED", "WINDOW_MIXTURE",
"SUBSTRATE_SYSTEMATIC_SURVIVES_STRATIFIED", "FIT-CEILING",
"NO_MECHANISTIC_MATCH", "SPATIAL-SCALE-DEPENDENT", "PER_WINDOW_NULL",
"PER_WINDOW_STATIONARY", "PVC11_SPECIFIC") carry their definitions
through this file; new phase work should either reuse them or
explicitly extend the vocabulary with a definition.  "ALLEN_SPECIFIC"
is reserved for future use — it would parallel "PVC11_SPECIFIC" if and
when an Allen-bound finding requires the explicit token; currently the
Allen-bound findings (per-window p=7 in natural_movie_one,
drifting_pooled p=2 STATIONARY) are described in prose without the
shorthand.*

## Bridge arc — transition functions to the spatial-statistics atlas (2026-08-14)

ARS and the Ripley/Baddeley spatial-statistics lineage are two chart systems on point
processes; this arc wrote and validated the transitions between them. No new science claims
(binding anti-claim); the deliverables are the dictionary, the cross-checks, and the 2D
protocol. Full results: `bridge/RESULTS_BRIDGE.md`; prereg `bridge/prereg_sealed.json`;
dictionary `bridge/TRANSLATION_TABLE.md`; protocol **TOOLKIT.md §11** (founded by this arc —
edge correction, intensity estimation, and the gluing-identity SNR law).

What the tool now knows that it didn't:
- **The transitions glue.** Zeta window read identically through both dialects (⟨r̃⟩ 0.611 /
  KS_GUE 0.019 home-side; pcf on the sine-kernel curve to 0.064 spatial-side, sealed tol
  0.091). Our estimators and spatstat agree to ≤1.1% on K; our DPP fitter and spatstat `dppm`
  agree to 3 decimals on the Ginibre KAG. New calibrator capability: true Ginibre sampler
  (`bridge/ginibre_sampler.py`, KAG-passed) and a banked GUE pcf-shape tolerance anchor
  (`bridge/gue_pcf_anchor.json` — P3 found NO prior owner of that slot).
- **The gluing identity (Σ² from pcf) has a measured SNR law** — amplifies pcf baseline offset
  by ~(λ|B|)²/Var, i.e. worst exactly where rigidity/hyperuniformity is strongest (TOOLKIT
  §11.3). Gate it small-window only; large-window disagreement is the law, not a defect.
- **B2/B3 triangulation (Gaussian-prime wedge): AGREEMENT, scale-qualified — one fact, two
  clauses, both required in any quotation.** (i) Poisson-class **at spacing scale**
  (coarse-grained, bins ≥ lattice pitch, r ≳ 2: best DPP beats Poisson by 2.3% only; Thomas
  degenerates in both implementations), concordant with Phase 34d's Hecke-Poisson angle
  verdict. (ii) **Below spacing scale** the pcf is **by construction** a lattice comb — the
  points live on the checkerboard-Z[i] sublattice, so discrete support with Hardy–Littlewood
  constellation weights (g(√2)=3.07, g(√10)=3.66, zero between) is the support set talking,
  not a class property. Quoting (i) without (ii) — or welding them into a contradiction — is
  the slot hazard this wording prevents. Filed as observable-binding capability, not a class
  claim. **Registered follow-up:** the comb is a 2D arithmetic calibrator CANDIDATE
  (epistemic tier: conjecture-backed-computable — HL singular series computable to arbitrary
  precision, unproven; distinct tier from theorem-backed zoo entries) — future micro-arc gates
  empirical comb weights against computed singular series (`bridge/RESULTS_BRIDGE.md`
  Registered follow-ups).
- **The FIX-2 twin fires on demand in the spatial dialect:** wrong-intensity K_inhom on a
  4.7×-gradient synthetic manufactures +14% clustering while the correct lens sits at ±1–2%
  (3-seed replicate); at thin-window (2%) variation the lens choice is provably immaterial —
  the quantitative safety margin behind TOOLKIT §11.2 option 2.

Standing instrument notes: spatstat quarantined at `bridge/.rquarantine` (cross-check only,
never a core dependency); wedge-scale `dppm` and `dppPowerExp` OOM at 15GB (declared, subwindow
scope used); ⟨r̃⟩ and Δ₃ have no spatial twin (their-atlas gap, TRANSLATION_TABLE rows 6-7).
