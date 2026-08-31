# Arithmetic Resonance Spectrometer (ARS)

Python implementation of a two-engine point-process classifier built on
the Farey-rational phase-locked loop framework developed by M. Planat
and collaborators (FEMTO-ST, 2002–2026).

## What this is

**In plain language.**  The toolkit studies the *timing texture* of
activity — whether events are clumped, evenly spread, random, or rhythmic
— by taking an ordered list of event times and analysing the gaps between
consecutive events.  In the neural setting that list can be a **single
neuron's spikes** (the per-cell mode), or it can be built **across many
neurons at once**: the pooled spikes of a whole population, the times when
the population bursts or synchronizes together, or the spacing in the
**eigenvalue spectrum of the neuron-to-neuron correlation matrix** (random-
matrix analysis of the population covariance — the most directly cross-unit
mode).  It often runs in short time windows and compares across them, asking
whether a pattern is steady through time or only emerges over the whole
recording.  The same method applies to non-neural event lists (Riemann-zeta
zeros, prime numbers, earthquake times).  Throughout, the *firing rate
itself* — how fast events come and how that speeds up or slows down — is
treated as a nuisance to be removed, so that what is read is the genuine
texture of the spacing and not an artifact of rate changes.  (One result of
the cross-unit arm: those population observables disagree with each other —
the correlation-matrix spectrum reads spread-out/rigid, synchrony-event
times read random, avalanche onsets read in-between — so there is no single
"population fingerprint"; see `cross_substrate/population_fingerprint.py`.)
A caution carried by the whole arc: these spacing verdicts certify the
*marginal* gap distribution, not a universality *class* — see RESULTS.md §8
"Reconciliation (2026-06-05)".

Technically, the toolkit takes a point process (sorted event timestamps) and
asks two formally distinct questions about it.

The **NNS engine** (`joint_q_profile`) decomposes the point process
over Farey-rational bands, computes analytical passage times per band,
and reads nearest-neighbour spacing statistics against Poisson / GOE
/ GUE references.  Its load-bearing outputs are `ks_gue_med` (median
over q-bands of the KS distance to GUE) and `rep_med` (median repulsion
integral).  The NNS engine carries dynamics-class signal (Poisson /
Wigner / TR / BR) at the recording-aggregate level.

The **RF engine** (`padic_amplitude_v4`) computes Ramanujan-Fourier
amplitudes on the event-indicator function and aggregates `|a_q|` over
q's divisible by each tested prime, normalised against the total
amplitude.  The RF engine carries per-prime arithmetic-class signal.

These two engines are formally distinct objects, not different views
of one engine.  The deployed classifier has both because of a proved
limitation of the first: any engine with the architecture `{filter
Farey rationals → analytical passage → unit-mean-normalised NNS →
KS}` is invariant under linear time scaling and **cannot** detect
prime-base asymmetry on stationary signals (§7.ter.10 band-invariance
proposition).  Three versions of p-adic profile (v1, v2, v3) failed
acceptance for this structural reason before v4, which routes through
the RF engine on indicator functions, passed.  Future work that
proposes to extract per-prime structure from `joint_q_profile` is
attempting an architecturally impossible measurement.

The classifier operates at two timescales — **full-sequence** (the
entire recording treated as one object) and **per-window** (tiled
into shorter epochs).  Full-sequence survival does not imply
per-window survival, and the same recording can carry a signature at
one scope and not the other.  Any surrogate-survival claim must
specify scope.

The framework's analytical content (Farey rationals as PLL natural
frequencies, Ramanujan-Fourier amplitudes, the Mangoldt-function
and Bost-Connes connections) is not original to this codebase.  ARS
is an applied implementation; it does not contribute new theoretical
mathematics.

## The mathematics, concretely

Everything reduces to **spacing statistics of a sequence derived from
the point process**.  The input is always a sorted list of event times
`t_k`.  The two engines differ in *which* derived sequence they read
and *against what reference* they compare it.  (Function names below
refer to `arithmetic_toolkit.py` unless noted.)

### The arithmetic core — Ramanujan sums

Both engines are indexed by a denominator `q` and built on the
**Ramanujan sum**

>  c_q(n) = Σ_{a : 1 ≤ a ≤ q, gcd(a,q)=1} exp(2πi · a n / q)

— the sum of the n-th powers of the *primitive* q-th roots of unity.
It is computed not by summing roots but via **Hölder's identity**

>  c_q(n) = μ(q/d) · φ(q) / φ(q/d),    d = gcd(n, q)

with μ the Möbius function and φ Euler's totient (`ramanujan_sum_array`,
`mobius`, `euler_phi`).  The c_q(n) are integer-valued and multiplicative
in q; they are the basis the Planat framework substitutes for the usual
Fourier characters exp(2πikn).

### The RF engine — "RF" is Ramanujan-Fourier

It decomposes a sequence f(n) onto the Ramanujan sums instead of onto
complex exponentials:

>  f(n) = Σ_q a_q · c_q(n),    a_q = (1/φ(q)) · ⟨ f(n) · c_q(n) ⟩_n

(the Carmichael–Wintner mean; `ramanujan_fourier`, where the code is
literally `a[q-1] = mean(f * c_q) / phi(q)`).  The amplitude |a_q|
measures how much of the signal sits at "denominator q" — i.e. at
integer period q and the periods that divide into it.  (The c_q are
orthogonal only in the Cesàro / density limit, not ℓ²-orthogonal on a
finite window, so the empirical a_q are *estimators* that carry some
inter-band leakage — most pronounced at high q, where few periods of
support fit the record.  The per-band noise floor in v4 is partly a
guard against this.)  Two input modes:

- **normalized mode** — f(n) = the unit-mean inter-event intervals.
  Reads spacing-correlation structure; blind to absolute period (it
  divides it out).
- **indicator mode** — f(n) = a histogram of events into unit-width
  integer time bins, f(n) = #{k : ⌊t_k − t_min⌋ = n}.  Reads genuine
  integer-period structure of the raw times (period-7, period-30, …).

The deployed **p-adic profile `padic_amplitude_v4`** runs the indicator
mode, then for each prime p sums |a_q| over the *pure prime powers*
q ∈ {p, p², p³, …} ≤ q_max and normalizes twice — by total RF power and
by the per-band mean amplitude as an explicit noise floor (the per-band
form removes the "small primes have more powers ≤ q_max" bias).  A peak
at p means RF power is concentrated on powers of p — p-adic resonance in
the event grid.  This is the per-prime, arithmetic-class signal.

### The NNS engine — nearest-neighbour level spacing

"NNS" is the level-spacing statistic of random-matrix theory.
`joint_q_profile` is the deployed implementation:

1. **Farey-PLL bands.**  Enumerate Farey rationals a/q with q ≤ q_max
   (both sub- and super-unison, reciprocal-augmented; `farey_rationals`
   in `pll_bank.py`) and read each as a phase-locked-loop natural
   frequency f = fc·a/q.  For each, form the **passage times**
   t_k·f − 1 (keep the positive ones), take their consecutive
   differences, and normalize those to unit mean.  (The −1 sets a
   one-period left-truncation — it keeps events with t_k > 1/f and drops
   the pre-first-period transient; the offset itself cancels under the
   differencing, so the spacings within a band are the raw inter-event
   spacings up to that truncation.  That the band frequency f cancels in
   the unit-mean normalization is the band-invariance proposition made
   concrete, and the reason a separate RF engine is needed.)
2. **Pool by denominator.**  Pool the normalized spacings across all
   numerators a sharing a denominator q → one "q-band," matching the RF
   coefficient indexing.
3. **Classify against the analytic level-spacing laws** by
   Kolmogorov–Smirnov distance (`universality.py`):

   >  Poisson (uncorrelated):  P(s) = e^{−s}
   >  GOE / Wigner β=1:        P(s) = (π/2)·s·e^{−πs²/4}
   >  GUE / Wigner β=2:        P(s) = (32/π²)·s²·e^{−4s²/π}

   giving per-band `ks_gue_q`, `ks_goe_q`, `ks_p_q`, and `mass_lt_0_3`
   (fraction of spacings below 0.3 — a clustering proxy; GUE → ~0,
   Poisson → larger).  The headline scalars are **medians over the
   well-powered q-bands**: `ks_gue_med = median_q ks_gue_q` and
   `rep_med = median_q rep_int_q`.

The **repulsion integral** `rep_int_q = ∫₀¹ (1 − R₂(r)) dr`
(`pair_correlation_full`) is the second NNS axis: R₂ is the
pair-correlation function, so the integral is positive under level
repulsion, ~0 for Poisson, negative under clustering.  The **quadrant
diagnostic** (`joint_quadrant_diagnostic`) then places each q-band on a
(rep_int × RF-spike) plane: BL = Poisson, TR = Wigner-class, BR =
uniform/saturated, TL = periodic (flagged when |a_q| exceeds 5× the
median amplitude).

### Why there are two engines — the band-invariance proposition

The NNS pipeline normalizes every passage-spacing set to unit mean, so
it is **invariant under t → λt** and therefore cannot, on a stationary
signal, detect prime-base asymmetry (§7.ter.10).  That is the structural
reason the RF engine exists.  Three p-adic profiles built *inside* the
NNS pipeline (v1–v3) failed acceptance for exactly this reason; v4
escapes it by reading the raw integer grid in the RF spectrum.  The two
engines are formally distinct objects, not two views of one.

### The other summations — the long-range and rate-robust arms

The marginal NNS statistic sees only the gap *histogram*.  Several
further statistics — fingerprint axes, and in the 2026-06 audit the
discriminators that *downgraded* the marginal verdicts — read the
structure NNS cannot:

- **Fano factor** F(T) = Var N(T) / Mean N(T) over non-overlapping
  windows of length T, multiscale (`fano_curve`).
- **Number variance** Σ²(L) = Var of counts in sliding length-L windows
  (`universality.number_variance`; `axes.II1`).  Poisson grows as
  Σ² = L; GUE as (1/π²)(ln 2πL + γ + 1); the leading coefficient is
  2/(βπ²), so GOE has asymptotically twice GUE's number variance.  The
  long-range rigidity test.  (The deployed long-range discriminator
  judges against empirical GUE/Poisson ensembles at matched (n, L), not
  these analytic curves.  As of 2026-08 the judged L is substrate-aware
  and capped — `L_judge = min(requested_L, validity_L,
  discrimination_L)` — after the L-policy arc showed a large default L
  can dilute a real 9σ effect and admit GOE at small n; see `lcap/`.)
- **Spectral rigidity** Δ₃(L): mean-square deviation of the counting
  staircase from its best-fit line over length L (`axes.II2_delta3_at_L`).
- **Spectral form factor** K(t) = (1/N)·|Σ_n e^{2πi t x_n}|²
  (`spectral_form_factor`).
- **The marginal-vs-class discriminator.**  The **Wigner-renewal decoy**
  (`cross_substrate/longrange_discriminator.wigner_renewal`) is a renewal
  process whose i.i.d. spacings are drawn from the GUE surmise — *identical
  marginal NNS* to real GUE, but with no long-range correlation (its Σ²
  grows linearly, not as log L).  NNS cannot tell it from real GUE;
  Σ²/Δ₃ separate them >20×.  This is the proof that `ks_gue` / `rep_med`
  certify the marginal gap distribution, not the universality class.
- **Rate-robust local irregularity — the neuroscience-standard pair.**
  **CV2** (Holt et al. 1996), mean over adjacent ISIs of
  2·|Iᵢ − Iᵢ₊₁| / (Iᵢ + Iᵢ₊₁), and **Lv** (Shinomoto et al. 2003), mean
  of 3·((Iᵢ − Iᵢ₊₁)/(Iᵢ + Iᵢ₊₁))² (`axes.I12_cv2`, `axes.I13_lv`).  Both
  are parameter-free (Poisson → 1, regular → <1, bursty → >1) and robust
  to slow rate drift because adjacent ISIs see ~the same rate; added in
  Phase 37 to dissolve a slow-drift artifact that had inflated the global
  CV.
- The cross-substrate landscape adds **Brody q** and **Berry–Robnik ρ**
  (intermediate-statistics NNS interpolation fits), spectral
  **box-counting dimension**, and **Lyapunov / correlation-dimension**
  axes for the dynamical substrates (`axes.py` Families I–V).

### The calibrator zoo

The "zoo" is the panel of known-class generators run *before* any unknown
signal, so the apparatus's response to known structure is characterized
first (`calibrator_panel.py`, `extractor_distinctness.STANDARD_CALIBRATORS`,
`signal_gen.py`):

- **Stationary panel (8 classes):** Poisson; **β-ensemble eigenvalues**
  — GOE (β=1), GUE (β=2), GSE (β=4) — generated as Dumitriu–Edelman
  tridiagonal Hermite matrices, semicircle-unfolded and bulk-trimmed
  (`make_beta_ensemble_eigenvalues`); the first N Riemann ζ zeros;
  uniform_jitter; periodic_q7 (period 7 + 5% jitter); mixed_q7_q12 (two
  interleaved periods).
- **Transition panel (6, Phase 20.5):** blended GUE→Poisson (sharp step),
  Poisson→GUE (sigmoidal), GUE→TL→GUE (metastable middle), Poisson→TL
  (linear ramp), and logistic-map events in the chaotic (r = 3.7) and
  period-4 (r = 3.5) regimes — for non-stationary / transition signals.
- Additional repulsion references in `signal_gen.py`: Matérn-II
  **hard-core** (minimum-spacing) processes and **Ginibre-projected**
  spectra.

A signal's class is read as its position *relative to* this panel — never
on an absolute threshold the panel has not been shown to separate.  This
is the operational form of the boundary-readout commitment below.
(Deployed practice lagged this commitment for a long time: a 2026-08
census found the workhorse `_classify` — depended on by 93 files — is an
argmin over {Poisson, GOE, GUE} with **no rejection region**; 7/7
non-member inputs received a confident label, and 9 of 11 deployed
classifier implementations were one-sided or had an unrecorded
complementary rate.  See `gate_census/GATE_CENSUS.md`; the HYPER_RIGID
split and per-realization gates are the first repairs.)

## Why this exists

ARS was built on a specific epistemological frame.  The world is taken
to be a high-dimensional deterministic field structure, and every
empirical observation is understood as boundary readout — a partial
projection of the field onto a measurement apparatus that has its own
structural properties.  Every classification claim about a signal's
universality class is therefore a joint claim about the underlying
field and the readout apparatus.  Distinguishing what the field is
doing from what the apparatus is doing is the whole job.

The methodology in METHODS.md — calibrator zoo, extractor-invariance
test, induction-on-noise falsification — is not generic statistical
practice applied rigorously.  It is the specific discipline this
frame requires: the calibrator zoo characterises what the apparatus
does to signals of known structure before any unknown signal is read;
the extractor-invariance test checks whether a classification depends
on the readout method; the induction-on-noise step asks whether the
apparatus produces the same apparent finding when given input of
equivalent statistical character known not to contain the claimed
structure.

See `WHYTHISEXISTS.md` for the full framing, including the
implications for human + LLM collaborative reasoning under the same
boundary-readout commitment.

## The journey

This project was not planned as the thing it became.  It started as a
universality-class classifier for point processes and turned, over
roughly thirty-seven numbered phases and a parallel cross-substrate
program, into a study of what such a classifier can and cannot see.
The arc matters as much as any single finding, because most of the
phases are eliminations — each one narrows what the tool is entitled
to claim.  The chronological record lives in `RESULTS.md` (§7.ter.N,
one phase per entry).

**Origin — the two-engine instrument.**  The toolkit began as a single
NNS engine (`joint_q_profile`): decompose a point process over
Farey-rational bands, compute analytical passage times, read
nearest-neighbour spacing against Poisson / GOE / GUE references.  A
proved limitation forced the second engine — any classifier with the
architecture *{filter Farey rationals → analytical passage →
unit-mean-normalised NNS → KS}* is invariant under linear time
scaling and **cannot** detect prime-base asymmetry on stationary
signals (the §7.ter.10 band-invariance proposition).  Three versions
of a p-adic profile failed acceptance for this structural reason
before the RF engine (`padic_amplitude_v4`), routing through
Ramanujan-Fourier amplitudes on the event-indicator function, passed.

**Arithmetic instrument-validation (Phases 3–17).**  The instrument
was calibrated against substrates with *known* universality class:
Riemann ζ zeros (GUE, KS = 0.041 on the first 2,000, 0.012–0.015 at
heights ~10⁶), LMFDB elliptic-curve and Dirichlet L-functions (bulk
GUE, edge separation by root number / family symmetry), prime gaps.
These reproduce existing literature; they do not extend it.  They are
the ground truth the rest of the tool is measured against.

**The LLM arc — the canonical retraction (Phases 9–17).**  The
toolkit was applied to transformer residual-stream and attention
dynamics across four architectures and eight extractor mechanisms.  It
produced a sequence of exciting-looking findings — Wigner-class
classifications, cross-architecture σ̂ invariance, an "LLM and primes
share a parameter neighbourhood" reading — **every one of which was
retracted** across three rounds of artifact diagnosis (find_peaks
autocorrelation rhythm at §7.ter.19; metric-resolution collapse at
§7.ter.22; threshold-upcrossing TR induction, Finding F, at
§7.ter.23).  No measurement survived that could be attributed to the
model rather than to the extraction pipeline.  An EEG θ-band reading
was likewise falsified as a bandpass-filter artifact.  This arc is
preserved, not buried: it is the worked example of the boundary-readout
problem the whole tool is built to handle, and the fact that it
*terminated cleanly* — rather than continuing to generate findings
forever — is what the discipline is for.

**Discipline-hardening + physical PoCs (Phases 18–21).**  Out of the
retractions came the method: the calibrator zoo, the extractor-
invariance test, induction-on-noise falsification, the surrogate-
calibration and distinctness matrices.  Proof-of-concept runs on BGP
route-timing cascades and gamma-ray-burst timing exercised the
pipeline on real non-stationary data.

**The cortical-V1 turn (Phases 22a–32) — the bulk of the work.**  The
tool pivoted to neural data: pvc-11 anesthetised macaque V1 (Smith &
Kohn) and Allen Brain Observatory awake mouse V1.  This produced the
load-bearing correlational findings — **H1** (orientation selectivity
↔ `ks_gue_med`), the **F1/F0 ↔ `rep_med`** substrate-systematic
sign-flip, the triply-bounded **H2** population-event structure,
**DSI**, and the **p=7** cross-substrate temporal-scope asymmetry — and,
just as importantly, the eight disciplines below, which crystallised
because each finding had to survive them.  The phase also produced its
eliminations: Kuramoto-class formalism does **not** match V1 (Phase 30,
four-way joint null); history-coupled GLMs hit a FIT-CEILING as an H2
target (Phase 25); H2 is **not** a local-spatial-cluster phenomenon at
any tested scale (Phases 27–28); the GRB 909 Hz QPO replication
substantively **failed** (Phases 23, 26).

**Cross-domain envelope (Phase 33).**  Could the event-level method
reach published data in other fields — pulsar timing (NANOGrav),
particle physics (CERN Open Data), single-molecule fluorescence?
Mostly no, and *informatively* no: published data products are
pre-aggregated (folded TOAs, post-trigger NanoAOD, post-state-detection
dwell times), so they are structurally incompatible with an event-level
reader.  The durable output is a generalisation of §7.ter.19 to an
entry-point discipline — audit the published-product level before any
cross-domain pilot.

**Arithmetic orthogonal-channel survey (Phases 34a–34f).**  Back to the
number-theory side, on a wider front: Mertens and Liouville
sign-changes, ζ / Dirichlet / EC L-zeros as a spectral-coordinate
family, Gaussian + Eisenstein prime angles, Γ₀(N) Maass forms (the
Sarnak anomaly replicated across squarefree levels), and 3-D Bianchi
pipelines validated against a proven theorem.  The recurring lesson:
the right surrogate null is substrate-specific (support-set-respecting
for arithmetic point processes), and a pooled-substrate null can
manufacture false structure.

**The cross-substrate "operator-IS-substrate" program (2026-05).**  A
second program grew alongside the phase line and eventually audited it.
Instead of extracting utility from one substrate, it fingerprints
*many* on a shared coordinate family and reads the cross-substrate
*comparison*.  Its central thread is an **approximability
stratification**: organise substrates by a Diophantine frequency
parameter and the spectral fingerprint grades by how well that
parameter is rationally approximable — including the result that the
**almost-Mathieu operator and the Fibonacci Hamiltonian are the same
operator family** up to an approximability-dependent reparametrisation.
The program also pushed the neural work across substrates — Buzsáki
CA1, IBL, entorhinal / CA3, retinal ganglion cells — and added
self-organised-criticality calibrators (earthquake and solar-flare
catalogues), finding that **per-cell fingerprints cohere while
population-level observables fragment**.  Phase 36 then split the
quasiperiodicity→chaos transition into rigidity-type and clustering-type
breakdowns; Phase 37 dissolved a CV-16 nonstationarity artifact and,
with rate-robust CV2/Lv axes, revealed a genuine hippocampal-vs-sensory
clustering gradient.

**The marginal-vs-class reckoning (2026-06).**  Finally the auditing
program caught up with the deployed verdicts.  A long-range
discriminator (Σ²(L) / Δ₃(L) with a Wigner-renewal decoy) and an
apparatus-subtraction stage established the load-bearing correction:
**NNS / `ks_gue` / `rep_med` certify the marginal gap distribution, not
the universality class.**  An order-scramble surrogate reproduces
0.87–1.00 of the quadrant's per-band labels on every real substrate —
the quadrant is order-blind by construction.  Consequences: ζ was read
as *confirmed at class level* — a reading **SUPERSEDED 2026-08-16**:
the one-sided RIGID_GUE rule certifies only "not floppier than GUE" (a
perfect clock earns it too), and judged inside its own Berry validity
window ζ_first_2000 is **HYPER_RIGID, z = −9.10**, the same marginal
measurement sharpened, not overturned (`lcap/RESULTS_LCAP.md`,
`rigidgate/RESULTS_RIGIDGATE.md`) — while L-function bulk-GUE stands
and pooled long-range claims are caveated to marginal-only; the neural per-cell
"poles" are downgraded to gradients within an intrinsically clustered
regime; H1's marginal correlation survives in full, but the structural
reading that selective cells are a distinct level-repulsion class is
walked back (the OSI-graded clustering was stimulus-driven rate-stepping,
collapsing to null under an external-rate unfold).  The lasting gain is
the methodology, not any single verdict — and the open scientific
question is sharper than before: H1 has a robust marginal correlate but
no mechanism, and the audit removed the story that would have supplied
one.  The full per-claim accounting is in `RESULTS.md` §8
"Reconciliation (2026-06-05)".

**Where this leaves the tool.**  The throughline of the journey is not a
result but a method.  What survived every phase is a measurement
discipline: the calibrator zoo and induction-on-noise (does the
apparatus manufacture this finding from structureless input?), apparatus
subtraction for dead-time and thinning, the long-range Σ²/Δ₃
discriminator with its Wigner-renewal decoy (does the verdict certify
the class or only the marginal?), the external-rate unfold (is the
structure intrinsic or stimulus-driven?), and the rate-matched /
rate-stratified / per-window / cross-substrate / cross-engine ladder.
Each was forced into existence by a finding that did not survive it.
That toolkit transfers; it is the part of this work most likely to be
useful elsewhere.

What the tool now needs is **more data**, not more method.  The two
sharpest open questions are both data-limited.  (i) H1's marginal
correlate is robust but mechanism-free, and the macaque-vs-mouse /
anesthetised-vs-awake confounds that block a clean read are only
breakable with **awake-macaque or anesthetised-mouse V1** recordings
matched to the existing substrates.  (ii) The p=7 cross-substrate
temporal-scope asymmetry has the same confound.  More broadly, several
of the strongest signatures rest on two V1 recordings; the cross-substrate
neural ports (CA1, IBL, entorhinal, retina) widen the base but each
arrives on a slightly mismatched selectivity axis.  The next decisive
step is acquisition — additional substrates that hold one confounding
variable fixed while flipping another — rather than a new statistic.

## Disciplines

Eight disciplines now structure what counts as a surviving finding.
A finding's confidence is its current position in this list.

1. **Full-sequence surrogate floors** — Aitchison-null, rate-matched
   Poisson, cell-shuffle, LN-evoked, state-modulated.  The aggregate
   signature is not reproduced by a null model with the relevant
   property preserved.
2. **Rate-matched surrogates** — isolate dynamics from rate.
3. **Rate-stratified within-cell comparison** — necessary elaboration
   of rate-matched; the dynamics signal may live in a specific rate
   tertile, so per-cell tertile comparison is the cleaner
   discrimination.
4. **Per-window surrogate** — full battery repeated on each window;
   asks for stationarity.
5. **Per-window p-adic** — same on the RF engine, separating long-
   coherence aggregation phenomena from short-coherence stationary
   ones.
6. **Spatial-scale stratification** — local-cluster, recording-wide,
   or scale-dependent.
7. **Cross-substrate** — replication across recording substrates with
   different spatial pitch, species, and brain state.
8. **Cross-engine** — NNS and RF engines agree on substrate-systematic
   direction.

A simpler **stationarity check** (modal-classification stability over
windows, without a full surrogate battery) is a weaker but useful
filter.

## What has been validated

These measurements have been reproduced at the precision indicated
on the specific datasets named.  They are reported as
**instrument-validation outputs** — they reproduce statistics
consistent with prior results in the corresponding literatures.
They do not extend those literatures.

### Arithmetic instrument validation

- Riemann ζ first 2,000 Odlyzko zeros: KS_GUE = 0.041, rep_int_q = 0.425.
  ζ at heights ~10⁶: KS_GUE = 0.012–0.015.  Marginal spacings consistent
  with the GUE conjecture. (§7.ter.7, §7.ter.21.)  The long-range reading
  is window-sensitive: inside its Berry validity window (L ≈ 6),
  ζ_first_2000 is measurably *more* rigid than the finite-N GUE ensemble
  — HYPER_RIGID, z = −9.10, lens-invariant.  This is expected slow
  low-height convergence, not a claimed asymptotic GUE violation
  (`lcap/RESULTS_LCAP.md`).
- LMFDB elliptic curve L-functions, 87 curves, ~10,000 zeros: bulk
  GUE, edge separation by root number. (§7.ter.4.)
- Dirichlet L-functions, q ≤ 149, 630 primitive non-trivial characters,
  4.05M pooled spacings: bulk GUE, conductor-normalised γ₁ Sp/U
  separation at p = 0.001.  Consistent with Katz–Sarnak family
  symmetry predictions. (§7.ter.3.)
- Primes ≤ 10⁶ log-density unfolding: σ̂ = 0.048 [0.023, 0.073];
  twin primes ≤ 10⁷: σ̂ = 0.093 [0.068, 0.118]. (§7.ter.23 Tier 4.)

### Cortical-V1 application (the bulk of recent work)

These are the load-bearing findings from the Phase 22a–32a sweep on
two V1 substrates (CRCNS pvc-11 anesthetised macaque V1, Smith &
Kohn; Allen Brain Observatory Visual Coding Neuropixels awake mouse
V1).  Each has cleared the disciplines listed in parentheses; the
detailed per-finding map is in `EPISTEMIC_STATE.md`.

- **H1: OSI ↔ ks_gue_med.**  Cellular orientation selectivity
  correlates with the global marginal-spacing statistic.  Read as
  "selectivity ↔ a marginal-spacing *gradient*", not "↔ a
  level-repulsion *class*": the class reading collapsed under the
  external-rate unfold (see The journey above; `EPISTEMIC_STATE.md`).
  pvc-11 partial ρ = +0.720; Allen meta-fixed ρ = +0.363 across 12
  sessions (all positive sign).  *Disciplines: full-sequence
  surrogate, within-recording, within-SNR-tertile, cross-substrate,
  rate-stratified within-cell.*
- **F1/F0 ↔ rep_med substrate-systematic sign-flip.**  **RE-VERIFIED on the repaired instrument
  2026-07-29 (R-181…R-184) — STAYS LOCKED.** The between-substrate contrast, which is the actual
  claim, survives at **4.70σ** (Δρ 0.3590, p=2.6e−06); the Allen arm *strengthens* to **−0.2502,
  12/12 sessions negative**. But the quoted **+0.388 is an unattributed constant** (reproducible
  value **+0.2983**), and the **pvc-11 arm alone is no longer significant** (+0.1088, p=0.116) —
  82.4% of its cells sat on the clip's rail.  ~~pvc-11 +0.388~~
  vs Allen meta-fixed −0.183 (12/12 sessions negative, all 4 Cre
  lines).  Hietanen 2013 spike-count-bias deflation ruled out.
  *Disciplines: full-sequence surrogate, rate-matched (3 methods),
  rate-stratified within-cell on both substrates, cross-substrate,
  Ibbotson 2005 phylogenetic-conservation deflation.*
- **H2 surviving population-event structure (triply bounded).**
  Population NNS structure on specific pvc-11 recordings survives
  the required Aitchison-null surrogate conjunction at 30/30 q-bands.
  Bounded to: (i) recording-wide aggregate (not local-cluster at any
  tested spatial scale, Phase 27 + Phase 28); (ii) two specific
  anesthetised macaque V1 recordings (Allen 12-session does not
  replicate at rate-matched); (iii) post-window-aware refinement
  (monkey1_natural_movie WINDOW_AWARE_LOCKED 8/10 windows,
  monkey2_gratings_movie WINDOW_MIXTURE 5/10).
- **DSI ↔ ks_gue_med.**  Direction-selectivity index correlates with
  `ks_gue_med` with *stronger* Allen magnitude (+0.269 vs pvc-11
  +0.223), biologically plausible given mouse V1's heavier direction
  selectivity.  monkey2 NOT_SIGNIFICANT, signal carried by monkey1
  + monkey3.
- **p=7 cross-substrate temporal-scope asymmetry.**  pvc-11
  spontaneous + gratings carry p=7 enrichment at full-recording
  scope (mean z = +2.22 spontaneous, monkey1_gratings z = +9.77).
  Allen awake mouse V1 carries p=7 enrichment at per-window scope in
  natural_movie_one (mean z = +3.49 across 4 Cre lines, 19/30 windows
  z>2).  Phase 32a ruled out stimulus content as the load-bearing
  axis (pvc-11 natural-movie per-window p=7 = NULL at mean z = −0.25,
  0/10 windows z>2).  Macaque-vs-mouse and anesthetised-vs-awake
  remain confounded; awake-macaque or anesthetised-mouse data
  required to disambiguate.  The cross-substrate axis is **prime-
  specific** — both substrates carry per-window p=2 enrichment
  during movies; p=7 is the substrate-systematic prime.

### Other physical and biological signal classifications

These are single-dataset classifications on small samples.  They
should be read as findings about the specific datasets tested rather
than as findings about those domains broadly.

- USGS earthquake catalog M ≥ 4.5: Poisson-clustered (mass<0.3 = 0.33),
  consistent with ETAS aftershock dynamics.
- Adamatzky fungal mycelium spike pool, 1,470 events: super-Poissonian
  (mass<0.3 = 0.65).
- Solar X-ray flares (NOAA GOES, M+ class): Poisson-clustered.
- Binance BTCUSDT trade timing (one trading day): essentially random
  (BL quadrant).
- EEG θ-band zero-crossings (PhysioNet EEGMMIDB, 32 subjects):
  mass<0.3 ≈ 0.001, **identified as bandpass filter artifact** rather
  than a property of the underlying neural signal.

### Synthetic calibrators

- Pure-class parameter recovery on Poisson, Wigner (β=1, 2, 4),
  periodic, and uniform_jitter signals: passes acceptance criteria
  (CI coverage ≥ 80%, median relative error ≤ 10%) at n_events ≥ 200,
  with Wigner classes requiring n_events ≥ 1000.

## Cross-substrate universality-class landscape (2026-05 program)

A recent program turns the classifier into a *cross-substrate instrument*: each substrate
is fingerprinted on its spectral side and placed in a shared universality-class space, the
yield being the cross-substrate *comparison* rather than utility-extraction from any one
substrate ("operator-IS-substrate").  The fingerprint is extended beyond `ks_gue_med` /
`rep_med` to a coordinate family — nearest-neighbour spacing distances (W1δ, Brody q,
Berry-Robnik ρ), long-range rigidity (Σ² / Δ₃ / K), spectral box-dimension, and dynamical
(Lyapunov / correlation-dimension) axes — computed where each applies.

About twenty-five substrates across six families are charted: the two V1 recordings and the
broader Allen Brain Observatory cell population, additional neural ports (Buzsáki CA1, IBL,
entorhinal / CA3, retinal ganglion cells), Kuramoto, arithmetic L-functions (ζ / Dirichlet /
elliptic-curve), Mertens / Liouville, Gaussian + Eisenstein primes, Maass forms, NANOGrav
pulsar timing, the dynamical systems Mackey-Glass / Lorenz / logistic (and Rössler / Chua /
Duffing / Hénon), the brocot.fm synthesis corpus (its class-level headline ρ(rank,q) = −0.91
was superseded 2026-08-19 as a one-representative-per-Lagrange-class artifact; the relation
survives per-α at ρ = +0.699, n = 255, and the arc continued into a masking-derived
audible-horizon / listening program — `cross_substrate/brocot_*`,
`cross_substrate/BROCOT_SYNTH_IMPLICATIONS.md`), self-organised-criticality calibrators
(earthquake and solar-flare catalogues), the Sturmian word and the Sturmian / Fibonacci
Hamiltonian, generalised-Harper / mosaic / Maryland variants, and the almost-Mathieu (AM)
operator.  The run-by-run record and the synthesis are in
`cross_substrate/PROGRESS_REPORT.md` and `cross_substrate/findings_log.md`.

These are **exploratory charting results — progress-log, with verdicts adjudicated
separately; they are not folded into the validated set above.**  The load-bearing ones:

- **`ks_gue_med` is an unbiased proxy for the matched (plain-unfold) ks-to-GUE** (slope ≈ 1,
  n ≥ 100, away from strong stimulus-locking) — so the cheap q-banded harvest is trustable
  for landscape placement, and expensive matched recompute is deferrable.
- **The almost-Mathieu operator and the Fibonacci Hamiltonian are empirically the same
  operator family up to an approximability-dependent reparametrization.**  Sweeping coupling
  at the golden frequency, the AM fingerprint passes through the Fibonacci Hamiltonian's at a
  matched coupling, and this generalises across the Lagrange spectrum: the matching coupling
  stratifies *continuously* by approximability (rational-approximation quality — combining
  continued-fraction quotient size and irrationality measure), not by a bounded/unbounded-CF
  step, indicating a single universality class.  AM-criticality's spectral box-dimension is
  approximability-*invariant* near ½ (consistent with Jitomirskaya–Krasovsky and the
  Wilkinson–Austin 1994 numerical conjecture); the Fibonacci side is approximability-*graded*
  (consistent with the Damanik–Gorodetski / Cao–Qu a.e.-frequency dimension-constancy
  framework).  A quantitative cross-check of the Damanik–Embree–Gorodetski–Tcheremchantsev
  (2008) strong-coupling constant ln(1+√2) confirmed the 1/ln(λ) *form* but **not the
  constant** — finite-spectrum estimators can verify a form but not an asymptotic constant;
  that needs the trace-map thermodynamic formalism (deferred).
- **Per-cell fingerprints cohere; population-level observables fragment.**  Across the Allen
  cell population (8,462 cells × 7 areas), per-cell fingerprints behave as one "visual cortex"
  substrate and H1 (OSI ↔ `ks_gue`) generalises beyond V1 to all visual areas and LGN.  But
  three population-level observables of the *same* recordings span the whole class axis —
  the correlation-matrix eigenspectrum reads GUE-like, avalanche onsets intermediate,
  synchrony-event times Poisson-like — so aggregation, not biology, sets the class and there
  is no single "population fingerprint" (`cross_substrate/population_fingerprint.py`).
  Avalanche near-criticality is orthogonal to per-cell class.

Two method notes this program adds to the disciplines above: (i) an estimator can *look*
right at moderate scales yet be wrong asymptotically — validate scale/size-convergence and
scale-invariance before trusting an extrapolated constant; (ii) sweep coupling-class /
reference parameters before declaring two substrates distinct (a fixed-reference comparison
read the AM–Fibonacci pair as "distinct" and would have missed the confluence a sweep revealed).

## Negative-elimination findings

A complete record requires the eliminations as well.  Each is a real
result; the absence of these from a publication framing would
overstate what the tool currently claims.

- **Kuramoto-class formalism does not match cortical V1.**  Across
  the canonical (K, σ) parameter space (Phase 30), real V1 / Allen
  data has no Kuramoto-match (156/160 well-powered rows; aggregate
  modal = BR_artifact uniformly).  Kuramoto per-window p-adic at
  q_max=200 is also null.  **Four-way joint null** across both
  engines and both timescales.  (Phase 36's two-axis re-audit refines
  the reading: the null is clustering-type and repulsion-blind — a
  refinement, not an overturn; see `RESULTS_MATRIX.md`.)
- **History-coupled GLM as H2 elimination target: FIT-CEILING.**
  24-cell grid (n_lags × bin_ms × variant) produces zero FIT-PROPER
  cells; canonical → kernel collapse, unconstrained → runaway with
  invariant kernel shape.  Methodologically untestable in the Phase
  25 model family.  Co-finding: V1 spike trains have positive temporal
  correlation beyond what linear spatiotemporal stim filtering can
  absorb.
- **H2 is not a local-spatial-cluster phenomenon at any tested
  scale.**  pvc-11 Utah array 400–600 µm (Phase 27): CONTRA-OHIORHENUAN.
  Allen Neuropixels <300 µm (Phase 28): SPATIAL-SCALE-DEPENDENT
  with the local 100–300 µm bin LEAST TR-structured.  Combined: H2
  surviving structure operates at supra-300 µm or is not spatially
  localized at all.
- **GRB 230307A 909 Hz QPO (Chen 2025): substantive fail.**  Targeted
  replication at the time-slice adjustment detects no signature
  distinguishing the published 45–47 s claim window from surrounding
  sub-windows.  The Phase 26 broadband-TR side-finding is a per-cell
  rate-regime feature of ARS classification, not energy-band sensitivity
  (falsified) or aspect-mediated.

## Known failure modes

The toolkit has been characterised to fail in these specific ways.

- **Continuous-trace inputs with peak-detection extraction.**
  `scipy.signal.find_peaks(prominence=0.3)` applied to autocorrelated
  continuous traces produces spacing statistics determined by the
  input's autocorrelation length, not by the underlying dynamics.
  Classifications on such inputs reflect the extractor. (§7.ter.19.)
- **Threshold-upcrossing extractors on near-iid input.**  Applied to
  iid exponential noise, threshold-upcrossing event extractors produce
  rep_int_q ≈ 0.34, which falls in the TR (Wigner-class) quadrant.
  Any TR reading from a threshold-style extractor must be cross-checked
  by applying the same extractor to noise of equivalent statistical
  character. (Finding F, §7.ter.23.)
- **rep_int_q is a signal-level scalar on stationary inputs.**  On
  continuous synthetic uniform_jitter inputs, the per-q variation in
  rep_int_q is at floating-point noise level (std ~10⁻⁴).  The joint
  plane is effectively 1D for inputs in the BR_artifact regime; the
  Ramanujan-Fourier amplitude axis carries the discriminative
  information when periodic structure is present. (§7.ter.22 amendment.)
- **σ̂ recovery describes the gap distribution position.**  For
  signals that are point processes by construction, σ̂ describes their
  gap distribution.  For signals extracted from continuous traces via
  peak detection, σ̂ describes the extractor's gap distribution.
- **Sample-size requirements vary by class.**  Wigner-class β̂
  recovery requires n_events ≥ 1000 for ≥ 80% CI coverage; other
  classes require n_events ≥ 200. (§7.ter.23 Tier 3.)
- **Integer-spacing structural confound.**  When the underlying t_k
  is integer-valued and dense, the minimum normalised spacing is
  bounded above zero by arithmetic, and mass<0.3 = 0 occurs for
  structural rather than dynamical reasons.  The diagnosis flag in
  `joint_q_profile` reports this when detectable.
- **q_max=30 is underpowered for absolute-threshold p-adic
  discrimination.**  Rate-matched Poisson surrogates pass the
  §7.ter.13 1.5× threshold 95.6% of the time at q_max=30.  Use
  matched real-vs-surrogate z-scores at q_max=30; absolute thresholds
  require q_max=200. (§7.ter.39.)
- **Rate-matched Poisson surrogate is necessary but not sufficient.**
  For sub-modal dynamics-vs-rate isolation, within-cell rate-stratified
  comparison is the required next discipline. (§7.ter.39.)
- **Per-cell rate-regime structure on non-stationary signals.**  On
  rate-evolving inputs (GRB lightcurves, BGP cascades), ARS
  classification has per-cell rate dependence that the standard
  rate-matched surrogate does not fully control.  Currently in
  capability-uncertain territory pending an explicit per-cell rate-
  matched discipline. (§7.ter.36.)

Four further failure modes were characterised in the 2026-08 audit arcs:

- **Argmin classification with no null option.**  The workhorse
  `_classify` selects the nearest of {Poisson, GOE, GUE} with no
  rejection region: 7/7 non-member inputs received a confident label,
  and a perfect clock reads GUE at 15× the KS critical value.  9 of 11
  deployed classifier implementations shared the defect in some form.
  (`gate_census/GATE_CENSUS.md`, `gate_census/SWEEP_TRIAGE_TABLE.md`.)
- **One-sided thresholds admit the far side.**  RIGID_GUE meant "not
  floppier than GUE", so a perfect clock earned the GUE pole at
  z = −5.09.  Fixed by the RIGID_GUE / HYPER_RIGID split.  A threshold
  calibrated from one side has an unmeasured error rate on the other.
  (`rigidgate/RESULTS_RIGIDGATE.md`.)
- **Bounded fitters rail and return a constant.**  pvc-11's Brody-q
  coordinate returned the identical positive constant for 1,152 of
  1,159 cells — wrong sign and wrong magnitude; after repair pvc-11 is
  clustered in 99.4% of cells with median q = −0.373.  Distinct-value
  ratio is the diagnostic: an optimizer floor gives few distinct values,
  real concentration gives many. (`cross_substrate/PROGRESS_REPORT.md`.)
- **Pairwise holonomy tables are not a conservative bound.**  Exhaustive
  out-of-sample testing over all 59 admissible orderings falsified
  sub-additivity: the pairwise sum can *underestimate* composed
  transition holonomy by up to 6.9×, concentrated where UNFOLD follows
  POOL (a saturation regime). (`fullseq/RESULTS_FULLSEQ.md`.)

## Application to LLM internal states (canonical retracted-claim arc)

The toolkit was applied to transformer residual stream activations
and attention dynamics across four architectures (Qwen 2.5 3B,
Phi-3-mini-4k, TinyLlama 1.1B, Mistral 7B v0.1) and eight extractor
mechanisms.  After three rounds of artifact diagnosis (§7.ter.19,
§7.ter.22, Finding F at §7.ter.23), **with one exception no
measurement was obtained that could be attributed to the model rather
than to the extraction pipeline**.  The exception (Phase 37,
`phase37/VERIFICATION.md` Set 3): the fp16→int4 quantisation contrast
survives its extractor controls — int4 genuinely restructures the
surprisal sequence toward clustering (mass03 shift +0.0604, identical
plain and dithered, surrogate-controlled; verdict SUBSTRATE, not
readout).  It is a *within-extractor differential*, not a model-state
classification.

This section is preserved as the canonical worked example of the
boundary-readout problem the tool is built to handle.  Provisional
findings retracted during development:

- Wigner-class classification on residual_norm_peaks: retracted as
  find_peaks autocorrelation rhythm.
- Cross-architecture σ̂ invariance: retracted as metric-blindness on
  integer-position event sequences.
- Wigner-class reading on three by-construction extractors at
  rep_int_q ≈ 0.34: retracted as threshold-upcrossing TR induction.
- "LLM and primes share a parameter-space neighbourhood within
  BR_artifact": retracted as extractor-conditional comparison.
- Two distinct LLM attention-dynamics families: retracted after
  three additional state-based extractors classified as BR_artifact
  consistent with all change-based extractors.

The negative result is bounded to the extractors and architectures
tested.  It does not generalise to RMT analysis of LLM weight matrices
(Staats et al. 2024; Martin & Mahoney 2018–2024), which uses different
methodology and is outside the scope of this work.

The arc terminating cleanly rather than continuing forever is what
differentiates this from the failure modes the frame is designed to
identify.

## How to use

See `METHODS.md` for the protocol, including calibrator-zoo
construction, extractor-invariance testing, and induction-on-noise
falsification.  See `RESULTS.md` for the chronological empirical
record under which each measurement was produced.  See
`EPISTEMIC_STATE.md` for the per-finding map of disciplines cleared
and outstanding.  See `cross_substrate/PROGRESS_REPORT.md` for the
cross-substrate universality-class landscape program (synthesis) and
`cross_substrate/findings_log.md` for its run-by-run record.
See `TOOLKIT.md` for the cross-cutting disciplines (§9), condemned
paths (§10), the 2D point-process protocol (§11), and the canonical
order registry (§12).  `AUDIT.md` + `REPRODUCE.md` define the
`verify_all.py` green-board contract (green means the checkers pass,
not that the instrument measures what we claim); `threadledger.py`
is the machine-checked queue of open/landed/dropped threads, and
`verdictlattice.py` / `redpath.py` / `reachable.py` carry rulings as
code.

Installation:
```
pip install -r requirements.txt
```

Minimal example:
```python
from arithmetic_toolkit import joint_q_profile, padic_amplitude_v4

# t_k is a sorted numpy array of event timestamps

# NNS engine: dynamics-class signal at recording-aggregate level
profile = joint_q_profile(t_k, q_max=200)   # DataFrame, one row per q
well = profile[~profile['underpowered']]
ks_gue_med = well['ks_gue_q'].median()
rep_med = well['rep_int_q'].median()

# RF engine: per-prime arithmetic-class signal
result_rf = padic_amplitude_v4(t_k, q_max=200)
p7_amplitude = result_rf['per_prime'][7]['normalised_per_q']
```

For any non-stationary-rate input, run rate-matched and
rate-stratified within-cell surrogates before interpreting either
engine's output.  For any surrogate-survival claim, specify scope
(full-sequence vs per-window).

## Related work

The Farey-rational-PLL framework is developed in:

- Planat, M. & Henry, E. (2002).  The arithmetic of 1/f noise in a
  phase-locked loop.  *Applied Physics Letters* 80(13), 2413–2415.
- Planat, M. & Rosu, H. (2002).  Ramanujan sums for signal processing
  of low-frequency noise.  *Physical Review E* 66, 056128.
- Planat, M. (2006).  Huyghens, Bohr, Riemann and Galois: Phase-Locking.
  *International Journal of Modern Physics B* 20, 1833–1850.
- Planat, M. (2026).  Painlevé Confluence and 1/f Phase-Locking
  Dynamics.  *Machine Learning and Knowledge Extraction* 8(3), 73.

Standard random-matrix-theory and adjacent references applied here:

- Bohigas, O., Giannoni, M.-J. & Schmit, C. (1984).  Characterization
  of chaotic quantum spectra and universality of level fluctuation
  laws.  *Physical Review Letters* 52, 1.
- Mehta, M. L. (2004).  *Random Matrices* (3rd ed.).
- Odlyzko, A. M. (1987, 2001).  On the distribution of spacings between
  zeros of the zeta function.
- Katz, N. & Sarnak, P. (1999).  *Random Matrices, Frobenius Eigenvalues,
  and Monodromy*.
- Dumitriu, I. & Edelman, A. (2002).  Matrix models for beta ensembles.
- Cramér, H. (1936).  On the order of magnitude of the difference
  between consecutive prime numbers.

Almost-Mathieu / Fibonacci Hamiltonian spectral theory engaged by the
cross-substrate program (further dimension-theory references —
Jitomirskaya–Krasovsky, Damanik–Gorodetski, Cao–Qu, Wilkinson–Austin —
are cited in context in `cross_substrate/PROGRESS_REPORT.md`):

- Aubry, S. & André, G. (1980).  Analyticity breaking and Anderson
  localization in incommensurate lattices.  *Ann. Israel Phys. Soc.* 3,
  133–164.  (The λ ↔ 1/λ self-duality; criticality at λ = 1.)
- Avila, A. & Jitomirskaya, S. (2009).  The Ten Martini Problem.
  *Annals of Mathematics* 170, 303–342.  (Cantor spectrum of the AM
  operator for all irrational frequency and non-zero coupling.)
- Damanik, D., Embree, M., Gorodetski, A. & Tcheremchantsev, S. (2008).
  The fractal dimension of the spectrum of the Fibonacci Hamiltonian.
  *Communications in Mathematical Physics* 280, 499–516.  (Strong-coupling
  asymptotic dim(Σ_λ)·ln λ → ln(1+√2).)

Cortical-V1 literature specifically engaged by the Phase 22a–32a sweep:

- Hietanen, M. A., Crowder, N. A., Ibbotson, M. R. & Price, N. S. C.
  (2013).  F1/F0 spike-count bias.  *Neuroscience* 235.
- Ibbotson, M. R., Price, N. S. C. & Crowder, N. A. (2005).  F1/F0
  bimodality phylogenetic conservation.  *Journal of Neurophysiology*.
- Williamson, R. C., Cowley, B. R., Litwin-Kumar, A., Doiron, B.,
  Kohn, A., Smith, M. A. & Yu, B. M. (2016).  Factor analysis on
  pvc-11.  *PLoS Computational Biology* 12.
- Ohiorhenuan, I. E., Mechler, F., Purpura, K. P., Schmid, A. M., Hu,
  Q. & Victor, J. D. (2010).  High-order correlations in V1.
  *Nature* 466.
- Charles, A. S., Park, M., Weller, J. P., Horwitz, G. D. & Pillow,
  J. W. (2018).  Dethroning the Fano factor.  *Neural Computation* 30.

## Provenance

This toolkit was developed through extended dialogue with Claude
(Anthropic) without prior exposure to Planat's published work.  The
convergence on the Farey-rational-PLL framework occurred during
dialogue with a model whose training corpus included Planat's papers
from 2002 onward.  Subsequent reading of those papers (correspondence
with M. Planat, May 2026) confirmed that the analytical scaffolding
the toolkit implements was developed by Planat and collaborators over
the preceding two decades.  ARS is an applied implementation of an
existing framework, arrived at through an unusual transmission path;
it does not derive from those papers in the conventional read-then-
build sense, and it does not extend the framework analytically.

`WHYTHISEXISTS.md` includes a field-report section on what
AI-assisted independent research can and can't do, written from the
position of someone who built this project under those conditions.

## License

See `LICENSE`.
