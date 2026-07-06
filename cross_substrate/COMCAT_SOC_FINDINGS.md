# ComCat + GOES SOC pair — FINDINGS (progress log, NOT validated results; verdicts Will's)

Phase brief: COMCAT_SOC_BRIEF.md. Run state: COMCAT_SOC_RUNSTATE.md. Date: 2026-05-30 (overnight).
Banked: coordinates/comcat-fingerprint.jsonl, coordinates/goes-fingerprint.jsonl, figures/P_comcat_soc.png.

## Data (entry-point audit clean — per-event origin times, not aggregates; §7.ter.19 safe)
- **Global M≥4.5, 2000-2025**: 173,122 events, 25.0 yr, 6924/yr, M[3.4,9.1]. (FDSN count cross-check 173,122.)
- **Central San Andreas box** (lat35-37, lon-122..-119) M≥2.5 1990-2025: 5,945 events (G3, N-limited).
- **GOES SWPC flares** 1996-2025 via HEK: single-FRM clean pull IN PROGRESS (~50k expected; exact n
  pending — see G5). Contaminated all-FRM pull (220,548) retained separately as a negative example.

## G1 — clustered read: ARS RECOVERS known clustering, but conservatively
- Matched fingerprint: ks_poisson=0.080, ks_gue=0.349 → near the Poisson corner, far from GUE.
- Clustering readout (Poisson-excess side): mass<0.3 = **0.338** vs rate-matched-Poisson surrogate **0.259**;
  CV = **1.20** (Poisson = 1). Super-Poisson, i.e. clustered — recovered.
- **One-sided-fitter finding CONFIRMED at scale**: Brody q = 6.6e-5, Berry-Robnik ρ = 1.5e-3 — BOTH railed
  at 0. The repulsion-family fitters (q∈[0,1], ρ∈[0,1]: Poisson→GOE) structurally cannot represent the
  super-Poisson side; clustering is legible ONLY on ks_poisson / mass<τ / CV. This is a calibrator-zoo
  fact about the instrument, established on a near-ground-truth substrate.
- Trim-robustness CHECKED (hypothesis that the 2-98% trim attenuates clustering — FALSIFIED): un-trimmed
  raw normalized spacings give mass<0.3 = 0.3379, CV = 1.2015; matched (trimmed) gives 0.3385, 1.2020 —
  identical. The mild-clustering reading is NOT a trim artifact. (M≥4.5 global is genuinely only modestly
  clustered at this resolution; the strong clustering lives in the small-magnitude aftershock population
  that an M≥4.5 threshold excludes — consistent with ETAS productivity.)

## G2 — declustered read: the calibration WIN (motion in the a-priori-known direction)
Gardner-Knopoff windowing, window-scale sensitivity ×0.5 / ×1 / ×2:
| scale | kept | frac | ks_poisson | mass<0.3 | CV |
|------:|-----:|-----:|-----------:|---------:|---:|
| ×0.5  | 71075 | 41% | 0.014 | 0.271 | 1.04 |
| ×1.0  | 55741 | 32% | 0.014 | 0.271 | 1.04 |
| ×2.0  | 41227 | 24% | 0.016 | 0.274 | 1.04 |
- Declustering collapses the fingerprint TOWARD Poisson: ks_poisson 0.080→0.014 (5.7×), mass<0.3
  0.338→0.271 (≈ Poisson floor 0.259), CV 1.20→1.04 (→1). Stable across window scale (direction robust).
- **The earthquake calibrator passes via PERTURBATION-RESPONSE, not absolute magnitude.** At M≥4.5 the
  clustering is only mild (CV 1.20), so the convincing evidence is the declustering MOVE, and within that
  move the load-bearing number is **ks_poisson 0.080→0.014** (5.7×); the CV 1.20→1.04 move is real but
  small — lean on ks_poisson, not CV, for the tectonic half. The excess was triggering (removed by
  declustering), not secular rate drift; ARS moves in the known direction by ~the known amount.
- **The two substrates pass DIFFERENT halves of the calibrator** (do not let the headline conflate them):
  earthquakes supply the **perturbation-response** half (mild clustering, but declustering demonstrably
  moves the fingerprint home); solar flares supply the **strong-clustering recovery** half (large super-
  Poisson signal, FRM-clean-confirmed — see G5). "ARS passes the clustering calibrator" holds, but as the
  conjunction of these two halves, not as either substrate alone.

## G3 — single-fault: POPULATION-MISMATCH-bounded, NOT evidence against quasiperiodicity
- Central-SAF n=5945: ks_gue=0.426, ks_poisson=0.219 → MORE clustered than global. NOT repulsion.
- **The bound is population-mismatch (the retinal lesson again), not a refutation.** The characteristic-
  earthquake / seismic-gap repulsion hypothesis lives in LARGE-event recurrence times: M≥6.5–7, of which
  a single fault has tens at most over the instrumental era — far below the no-false-positive N. A
  5,945-event single-fault pull is utterly DOMINATED by the small-event population, which is aftershock-
  clustered by construction. So "more clustered, no repulsion" is measuring the WRONG POPULATION for the
  repulsion question — axis/population-mismatch (cf. ret-1 STA-SNR ≠ tuning; IBL contrast ≠ orientation),
  NOT evidence against quasiperiodic recurrence. The hypothesis is untouched, not falsified.
- **The real test is N-unreachable from instrumental catalogs.** Large-event recurrence on one fault is
  single-to-low-double digits in the catalog era — below the robust-NNS point regardless of pull. Testing
  it would need PALEOSEISMIC recurrence intervals (trench-dated earthquake sequences, e.g. SCEC/UCERF
  recurrence datasets) — a different acquisition entirely, queued as a [[planned_engineering_arc]]-style
  heavy test, not squeezable from ComCat. Reported as no-false-positive-only AND population-mismatch-bounded.

## G4 — directionality probe: pooled-NNS is PROVABLY arrow-blind; the arrow is PROVABLY present
**Framing (corrected — the stronger claim).** Δ=0 is an IDENTITY, not a measurement. Time-reversing the
sequence leaves the multiset of inter-event spacings unchanged (the gap between consecutive reversed
events is the same set of gaps), and pooled-NNS discards order, so forward≡reversed is a mathematical
identity — Δ=0 to machine precision *because it cannot be otherwise*, not because a measurement happened
to come out null. The empirical content lives ENTIRELY on the ordering-sensitive side. So G4 does not
*illustrate* §7.ter.10 — it *proves* it on this substrate: pooled-NNS is provably arrow-blind AND the
arrow is provably present (Omori 3.1×, irreversibility z≈−2). Both halves are real claims; the blind half
is a theorem, the present half is the measurement.
- Identity half: raw ks_poisson fwd = rev = 0.079710, Δ = 0.00e+00 — confirms the identity numerically
  (the ~1e-3 residual in the aggregate matched-fingerprint max|Δ| is just Berry-Robnik bootstrap noise).
- Empirical half — the arrow IS there, in observables NNS discards: irreversibility incr_skew z = −2.3,
  lagprod z = −2.0 (vs shuffled-order surrogate); magnitude-conditioned **Omori after/before = 3.1×**
  (n_main=300, ±30d, 100km) — 3× more events after a mainshock than before (causal aftershock decay; no
  symmetric foreshock buildup).
- The GAP: same catalog, strong clustering + strong (proven-present) time arrow, yet pooled-NNS is
  identically arrow-blind. Clustering is what the spacing engine reads; directionality is what it
  structurally discards (order, marks). On a substrate with a lot of both, the proposition is demonstrated
  as the identity-vs-measurement pairing it actually is.

## G5 — GOES solar flares: FRM-dedup gate, then REAL multi-day clustering (sub-day "regularity" = artifact)
### Data-integrity gate FIRST (this dominated the result)
HEK aggregates flare detections from MANY feature-recognition methods (FRMs); the SAME physical flare
appears from multiple FRMs. **The naive pull (frm_name= query param does NOT filter server-side) returned
220,548 events dominated by the "Flare Detective" auto-trigger** — with a **29%-of-spacings <60 s
duplicate pile** (the exact super-Poisson signature; the contaminated CV=8.71 was largely this). The
canonical NOAA **SWPC** human-vetted list is the clean one: **50,999 flares** (77% of the naive pull was
multi-FRM/duplicate contamination). Client-side single-FRM filter now in goes_flares.fetch
(CLEAN_FRM="SWPC"). Verified: clean dt<60s = **0.12%** (was 29%). **This is the solar analogue of the
seismic Mc gate — a one-pass check that had to precede every clustering number.** Contaminated catalog
kept as `goes-flares-allfrm-contaminated.jsonl` (gitignored) as a negative example.

### Clean SWPC fingerprint (n=50,999, 29 yr, 1759/yr) — MEASURED on the full catalog
- ks_gue=0.444, ks_poisson=0.174; homogeneous mass<0.3=**0.376**, CV=**5.76** (contaminated was 0.376-ish
  mass but CV 8.71 — the CV inflation was duplicates). Brody q / BR ρ railed at 0 again (one-sided-fitter
  fact, 2nd substrate).
- **The clustering is TIMESCALE-STRUCTURED — the bandwidth sweep IS the finding** (press #3: report the
  sweep, not one number). Local-rate unfold CV by window, beside the no-memory synthetic floor:

  | W | 5 | 7 | 11 | 15 | 21 | 31 | 51 | 101 | 501 |
  |---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
  | GOES unfolded CV | 0.71 | 0.79 | 0.89 | 0.96 | 1.04 | 1.14 | 1.27 | 1.48 | 1.78 |
  | synth-A (NO memory) | 0.78 | 0.85 | 0.91 | 0.93 | 0.95 | 0.97 | 0.98 | 0.99 | — |
  | synth-B (Hawkes memory) | 0.89 | 1.03 | 1.19 | 1.28 | 1.36 | 1.42 | 1.47 | 1.50 | — |

  **The super-Poisson half is REAL; the sub-Poisson half is an ARTIFACT (both retracted-and-rechecked).**
  - **Large-W (super-Poisson) — REAL clustering.** GOES rises monotonically and DIVERGES upward from the
    no-memory synth-A (which stays flat ~0.95–0.99) for W≳21, tracking the Hawkes-memory synth-B shape.
    Genuine multi-day clustering above the rate envelope.
  - **Small-W (sub-Poisson, CV<1) — NOT physics (dual artifact).** Press #2 was right. (i) The no-memory
    synth-A ALSO dips sub-Poisson at small W (0.78 at W5, 0.85 at W7) — so CV<1 at small W is the
    LOCAL-RATE-UNFOLD ESTIMATOR'S FLOOR (short windows over-fit real fluctuation as rate), not regularity.
    GOES at small W sits AT/BELOW synth-A (0.79 vs 0.85 at W7), the opposite of the memory signature
    (synth-B sits well above, 1.03). (ii) The raw ISI distribution has a HARD DEAD-TIME WALL at exactly
    60 s (min ISI = 60 s; the [0,1 min) bin is empty) — SWPC merges X-ray peaks within ~1 min, a catalog
    bookkeeping floor that depletes the shortest intervals. **The earlier "flares are regular at the
    shortest scale" reading is RETRACTED** — it was the unfold floor + catalog dead-time, not active-region
    refractoriness. (A real refractoriness effect would need to clear BOTH controls; it does not here.)
- **The clustering timescale matches the mechanism, and is PHASE-RESOLVED (physical-time crossover, press
  #5).** Cycle-average: CV=1 crossover at **W≈18 events ≈ 1.5 days** (median ISI 7380 s ≈ 2.05 h) — at the
  short end of active-region flare-productive lifetimes (~days), quantitative support for the same-AR-
  clustering mechanism, not a free parameter. Phase-resolved (each phase uses its OWN median ISI):
  **MIN crossover W≈8.6 ev ≈ 0.8 d; MAX crossover W≈33.5 ev ≈ 2.7 d.** The crossover MOVES with cycle phase.
  - **The DIRECTION is mildly surprising — and that sharpens the mechanism (NOT "overlap-driven").** Naive
    Palm–Khintchine: superposing more INDEPENDENT AR point-processes at solar MAX should drive the pooled
    process TOWARD Poisson — structure should wash out *more* completely at MAX, ideally leaving no super-
    Poisson residual at any scale. Instead MAX retains real super-Poisson structure (CV 1.07→1.26 at
    W51→W101; a genuine crossover at 2.7 d, not flat at 1). **Any surviving structure at MAX is exactly what
    independent superposition forbids.** So the earlier "overlap-driven" label is wrong-signed; the clean
    resolution is that **solar-max ARs are NOT independent** — active longitudes, AR nests, sympathetic/
    correlated emergence — and the longer-surviving structure at MAX is a (mild) signature of *correlated AR
    emergence*, not independent overlap. At MIN the few isolated regions emit same-AR bursts that clear
    Poisson in ~a day; at MAX correlated emergence sustains structure out to ~3 days despite the 20× denser
    stream. A sharper, falsifiable mechanism than "overlap-driven".
  - **Crucial check — the movement is in W (events), NOT a unit-conversion artifact.** Median ISI is nearly
    phase-INVARIANT (MAX 1.95 h vs MIN 2.12 h) — the 20× rate swing lives in the long-gap tail, not the
    median — so the W→time multiplier is ~constant across phases. The crossover shift (8.6 vs 33.5 events)
    is therefore real clustering structure, not the rate-swing smearing the map. (The earlier "W-in-events
    smears physical time" caveat is thus bounded: it smears the tail, not the median-anchored crossover.)
  - **The CV crossover is BLIND to the discriminating signal; the RF engine is not (queued follow-up).** If
    the surplus MAX structure is correlated AR emergence, it is PERIOD-structured (rotation-locked active
    longitudes, ~27-d Carrington band and harmonics) — which pooled-NNS/CV scrambles by construction (it
    discards phase; cf. G4 band-invariance). A **phase-stratified RF/resonance scan (MAX vs MIN)** asking
    whether the longer-surviving MAX structure carries enhanced Carrington-band (~27 d) / active-longitude
    amplitude is the test that converts "correlated emergence" from a plausible label into a measured
    mechanism. This ties directly to the **Phase 13 solar resonance run** (RESULTS.md §7.ter — same GOES-type
    flare process), which already saw rotation-band structure via the resonance engine: indicator-mode
    q=86≈3×27 d and q=43≈1.6×27 d (Carrington multiples), Planat-mode 21 d (≈rotation/2) and 35/42 d
    sub-Carrington / AR-emergence peaks. Two independent engines (resonance amplitudes there, SOC-unfold
    crossover here) pointing at the SAME rotation-modulated-AR physics. Queued, not done — the SOC-pair
    result stands without it; this would upgrade the MAX mechanism specifically.
- **Solar-cycle knob (clean, unfolded W51) — bootstrapped at full N (press #4).** MAX (n=27,386): CV=1.07,
  bootstrap 95% CI [1.06, 1.09]. MIN (n=6,303): CV=2.27 (point), but its bootstrap median CI is [1.94, 2.05]
  — the point estimate sits above its own resample band, the low-N heavy-tail regime, so report MIN as
  **≳1.9, not 2.27**. The **difference** MIN−MAX = **+0.92, 95% CI [0.86, 0.98]** — excludes zero decisively.
  So **MIN is robustly MORE clustered than MAX** (direction solid; MIN magnitude tail-sensitive). At solar
  MIN the few isolated active regions emit same-AR bursts against empty background (high residual CV). The
  MAX side is the interesting one (see the crossover-direction note above): MAX residual CV is LOW but NOT
  at the floor — independent AR superposition would predict the floor, so the surviving MAX structure points
  to correlated AR emergence (active longitudes / nests), not independent blending. Completeness cuts the
  safe way (missing small filler flares at MAX would only raise MAX CV, understating the gap). Raw split CV=103(MAX)/34(MIN) is the pooling-across-disjoint-cycle-years artifact —
  ignore; only the unfolded readout is interpretable
  ([[within_substrate_before_pooled]]).

### Synthetic validation of the unfold discriminator
`soc_synthetic_validate.py` — a new discriminator needs its own calibrator. Ground-truth processes, all
with the SAME 20× sinusoidal rate envelope:
Measured (these ran on full synthetic catalogs, n≈120-180k each — trustworthy):
| process | true memory | homogeneous CV | unfolded CV (W11→W101) | verdict |
|---|---|--:|--:|---|
| process | true memory | homog. CV | unfolded CV (W5 / W7 / W21 / W101) | verdict |
|---|---|--:|--:|---|
| A inhom-Poisson (20× envelope) | none | 1.91 | 0.78 / 0.85 / 0.95 / 0.99 | → floor ✓ (sub-Poisson at small W!) |
| B Hawkes branch 0.5 | yes | 2.75 | 0.89 / 1.03 / 1.36 / 1.50 | memory survives ✓ |
| C Hawkes branch 0.8 | strong | 4.53 | 0.88 / 1.02 / 1.55 / 2.28 | survives more ✓ (monotone in branch) |
| D inhom-Poisson + duplicates | NONE | 2.35 | 1.06 / 1.15 / 1.28 / 1.33 | **fakes memory** — unfold can't remove |
- **Discriminator VALIDATED**: separates A (→floor) from B/C (survive), monotone in true branching ratio.
  **Three things it establishes:** (1) the rate envelope DOES inflate homogeneous CV substantially (A
  homogeneous CV=1.91 with zero memory) and the unfold correctly removes it back to ≈floor — so local-rate
  unfolding is doing its job. (2) Duplicates (D) are INDISTINGUISHABLE from real memory (B) at LARGE W
  post-unfold ⇒ **dedup MUST precede unfold; the discriminator cannot rescue contaminated data.** (3) **The
  unfold floor is BELOW CV=1 at small W** (synth-A: 0.78 at W5, 0.85 at W7, climbing to ~0.99 by W101) —
  short windows over-fit fluctuation as rate, so a sub-Poisson reading at small W is the ESTIMATOR'S floor,
  NOT regularity. Always compare a small-W CV<1 against the matched no-memory synthetic before calling it
  physics (this is what caught the GOES sub-day "regularity" as an artifact). Banked as the calibrator for fact #3.
- **Bonus cross-check — the small-W dip doubles as a duplicate-purity test.** The two no-info processes
  diverge at small W: clean-no-memory A DIPS sub-Poisson (W5=0.78, W7=0.85), but duplicate-contaminated D
  does NOT (W5=1.06, W7=1.15) — coincident duplicates inject near-zero spacings that pull CV up exactly
  where the estimator floor would pull it down. Clean GOES dips (0.71 at W5, 0.79 at W7) → it sits on the A
  curve, not the D curve ⇒ no substantial residual duplicate pile survived the FRM gate. (Caveat: this rules
  out a SUBSTANTIAL residual, not literally zero — a handful of duplicates would only shallow the dip, not
  flip its sign. As a free cross-check on the dedup, clean.)

## SOC-pair synthesis (both halves complete)
- **Earthquakes (M≥4.5 global).** Mildly clustered (CV 1.20); the calibrator passes via PERTURBATION-
  RESPONSE — GK declustering moves ks_poisson 0.080→0.014 in the a-priori-known direction, and local-rate
  unfolding (0.34→0.29 mass, CV→1.07) shows most survives → triggering on a fairly stationary rate.
- **Solar flares (SWPC-clean, n=50,999).** AFTER the mandatory FRM-dedup gate: REAL multi-day clustering.
  Unfolded CV rises above the no-memory synthetic floor for W≳21 (CV 1.27 at W51, 1.78 at W501), tracking
  the Hawkes-memory shape; the CV=1 crossover at W≈18 events ≈ **1.5 days** lands on active-region flare-
  productive lifetimes — same-AR clustering. The apparent sub-Poisson "regularity" at small W (CV 0.79 at
  W7) is an ARTIFACT — both the unfold estimator's small-W floor (the no-memory synthetic dips there too)
  AND a 60-s catalog dead-time wall — RETRACTED, not physics. Solar MIN robustly MORE clustered than MAX
  (MIN−MAX = +0.92, 95% CI [0.86,0.98]; MIN ≳1.9, MAX 1.07); the surprising part is that MAX residual is
  above the floor at all — independent AR superposition predicts the floor, so the surplus is a mild
  signature of CORRELATED AR emergence (active longitudes/nests), period-structured and checkable with a
  phase-stratified RF scan (Carrington ~27 d band) — ties to the Phase 13 solar resonance run. Sharper than
  "strong clustering recovered": real, multi-day, active-region, cycle-modulated — sub-day half correctly killed.
- **Two substrates, two flavours of clustering** (the cross-substrate payoff): tectonic = mild, aftershock-
  triggering, declustering-removable, fairly rate-stationary; solar = real multi-day active-region
  clustering (crossover ≈1.5 d), cycle-modulated (MIN>MAX), with no genuine sub-day structure once unfold-
  floor + catalog dead-time are removed. Both required a completeness/integrity gate first (seismic Mc;
  solar FRM-dedup) — that gate is the transferable lesson.
- **Instrument facts (both)**: (1) ks_poisson/mass<τ/CV read clustering; Brody q & BR ρ are blind (rail at
  0). (2) pooled-NNS is provably (identically) time-reversal-invariant while Omori 3.1× and irreversibility
  z≈−2 prove the arrow is present in discarded observables. (3) the rate envelope DOES inflate homogeneous
  CV (synthetic A=1.91) and unfold removes it — the discriminator works, but cannot tell real memory from
  coincident duplicates (synthetic D), so a dedup gate is a prerequisite and the bandwidth sweep must be
  reported, not a single W. Synthetic-validated against Hawkes ground truth before banking.

Figure: figures/P_comcat_soc.png (6-panel: (a) NNS clustered/declustered; (b) clustering calibration ladder;
(c) railed one-sided fitters; (d) directionality-gap; (e) GOES unfold-CV vs W against the no-memory floor +
crossover; (f) phase-resolved MAX/MIN unfold curves with moving crossover).

## Open / queued
- **Phase-stratified RF/resonance scan, solar MAX vs MIN (the sharp follow-up).** Tests whether the
  surplus-above-floor MAX structure carries enhanced Carrington-band (~27 d) / active-longitude amplitude —
  i.e. whether "correlated AR emergence" is the actual mechanism. The RF engine sees rotation-locked period
  structure that the CV crossover is blind to (NNS scrambles phase). Ties to Phase 13 solar run (RESULTS.md
  §7.ter.17: indicator q=86≈3×27 d, q=43≈1.6×27 d; Planat 21 d, 35/42 d). Tooling exists (run_phase13_solar.py
  + the RF/resonance engine); just needs the MAX/MIN flare split fed through it. Converts the MAX mechanism
  from plausible label to tested. Does NOT affect the current SOC-pair result, which stands as-is.
- Paleoseismic large-event recurrence (G3 real test; off-ComCat acquisition).
- Lower-Mc regional seismic catalog to reach the strong-clustering tectonic regime (if wanted).
- Per-active-region flare sequencing (would localise the solar triggering memory to within-AR).
