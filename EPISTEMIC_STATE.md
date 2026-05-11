# ARS epistemic state

*Internal working reference, 2026-05-11.  Not a writeup, not a publication
draft, not a hierarchy of what to lead with.  A map of what the tool
currently knows, at what confidence, under which disciplines, and what is
still open — so that future phase briefs can scope against an honest
inventory.*

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

### F1/F0 ↔ rep_med substrate-systematic sign-flip

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

### Cross-engine substrate-systematic pattern (hypothesis, discipline outstanding)

The pattern — *not* yet a finding — is that the NNS engine (F1/F0 ↔
rep_med) and the RF engine (p=7 enrichment) point in the same
substrate-systematic direction: pvc-11 anesthetised macaque V1 on one
side, Allen awake mouse V1 on the other.  **Engine: cross-engine NNS +
RF.**  **Mechanism status: open.**  The status of the *cross-engine*
claim itself is *hypothesis*, not locked, because the discipline that
would distinguish "two engines viewing one underlying axis" from
"coincidental co-direction of two independent substrate-axes" has not
been run.  **Disciplines cleared:** the engine-individual disciplines
for F1/F0 and p=7 separately (listed in their own entries above), but
those clear the per-engine findings, not the cross-engine claim.
**The cross-engine claim has zero disciplines specifically cleared.**
**Outstanding:** explicit cross-engine correlation analysis — within
each session, do the units that contribute most to the F1/F0 ↔ rep_med
signal also contribute most to the p=7 enrichment?  Within each
substrate, does the inter-recording variation in NNS substrate-position
correlate with inter-recording variation in RF substrate-position?
Until that runs, the cross-engine entry is a hypothesis with a clear
next discipline, not a multi-discipline-cleared finding.  **Open:**
coincidence vs shared-axis is *the* core question, not a refinement.
If shared-axis: the §7.ter.10 band-invariance result becomes
interesting — it says the NNS engine can't see arithmetic structure
on stationary signals, so why does it co-direct with the RF arithmetic-
structure engine?  If coincidence: the substrate divergence has at
least two independent axes that happen to point the same way, and the
publication framing has to engage that multiplicity rather than collapse
it.

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

## Open questions across findings

The temporal-coherence-asymmetry mechanism story is the largest live
open question, and Phase 32a (2026-05-11) narrowed it from three-axis
to two-axis.  pvc-11 anesthetised macaque V1 carries long-coherence
p=7 structure (full-recording visible, per-window null in 14/15
recordings); Allen awake mouse V1 carries short-coherence p=7 structure
(per-window visible in natural_movie_one across all Cre lines,
full-recording null).  **Phase 32a ruled out stimulus content as the
load-bearing axis** (pvc-11 natural-movie per-window p=7 is null at
mean z = −0.253, 0/10 windows z>2, against Allen's +3.49 / 19/30).
The remaining candidate mediating axes — species (macaque vs mouse)
and state (anesthetised vs awake) — remain confounded in the
pvc-11/Allen comparison.  The natural test is **awake macaque V1 or
anesthetised mouse V1**, which would disambiguate.  Awake-macaque-V1
data with matched recording duration and population size is the
load-bearing missing comparator.  Without it, the species-vs-state
interpretation remains a candidate rather than a tested mechanism.
**A secondary observation surfaced by Phase 32a:** the cross-substrate
axis is prime-specific, not presence-vs-absence — both substrates
carry per-window p=2 enrichment during movies (pvc-11 mean z = +2.53
on natural-movie, +5.15 PER_WINDOW_STATIONARY on monkey2_gratings_movie;
Allen +7.92).  The p=7 axis is the substrate-systematic one; p=2 is
substrate-shared.  A per-prime substrate-systematic profile may be a
more interpretable framing than p=7 in isolation.

Whether F1/F0 substrate-systematic and p-adic substrate-systematic
share an underlying biological mechanism or are independent
substrate-axes is the second large open question.  Both engines land on
the same pvc-11-positive / Allen-negative direction with the same
substrate split.  An explicit cross-engine correlation analysis — do
the units/sessions that contribute most to one signal also contribute
most to the other — is the missing discipline.  If yes, the substrate
difference has one axis viewed by two engines.  If no, the substrate
difference has multiple axes that happen to project onto the same
direction in the two engine outputs.  This is also the answer to "what
is the right deflationary alternative the publication needs to engage
with."

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
