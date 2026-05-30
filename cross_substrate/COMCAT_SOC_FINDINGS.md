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

## G5 — GOES solar flares: FRM-dedup gate, then TIMESCALE-STRUCTURED clustering (multi-day, not sub-day)
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
  sweep, not one number). Local-rate unfold CV by window:

  | W | 7 | 11 | 21 | 51 | 101 | 201 | 501 |
  |---|--:|--:|--:|--:|--:|--:|--:|
  | unfolded CV | 0.79 | 0.89 | 1.04 | 1.27 | 1.48 | 1.65 | 1.78 |
  | mass<0.3 | 0.177 | 0.199 | 0.226 | 0.259 | 0.283 | 0.301 | 0.314 |

  CV rises **monotonically** with window and is **sub-Poisson (regular, CV<1) at the tightest scales**
  (W7→0.79), only super-Poisson at multi-day windows. So flares are NOT clustered at the shortest inter-
  event scale — they are clustered over **multi-day windows**. The earlier "memory survives at every
  bandwidth, CV≈1.2-1.6" claim is **RETRACTED** (it was projected from a partial fetch); the honest
  statement is timescale-dependent, sub-day-regular / multi-day-clustered.
- **It IS real clustering, not just the rate envelope** (the discriminating check): matched against the
  synthetic no-memory inhom-Poisson-with-20×-envelope (process A), GOES and synth-A agree at W11 (0.89 vs
  0.91) but DIVERGE as W grows — GOES W21/51/101 = 1.04/1.27/1.48 while synth-A stays flat at 0.95/0.98/0.99.
  The envelope alone produces NO rising-with-W signal; GOES does ⇒ genuine multi-day clustering above the
  envelope (physically: active regions persist ~days and emit multiple flares — same-AR sympathetic flaring).
- **Solar-cycle knob (clean, unfolded W51).** MAX years (n=27,386): unfolded CV=**1.07** (≈ floor). MIN
  years (n=6,303): unfolded CV=**2.27** (well above). **MIN is MORE clustered than MAX** — the OPPOSITE of
  the naive "max=clustered" expectation, and it survives the window-confound check (median dt 117 min MAX
  vs 127 min MIN ⇒ W51 spans ~4.1 vs ~4.5 days, comparable wall-clock, so the contrast is not a fixed-
  event-W artifact). Interpretable: at solar MIN the sparse flares come in isolated same-AR bursts
  separated by long quiet gaps (high residual clustering); at MAX flares are so dense the local-rate
  unfold absorbs most structure (residual ≈ floor). Raw split CV=103(MAX)/34(MIN) is the pooling-across-
  disjoint-cycle-years artifact — ignore; only the unfolded readout is interpretable
  ([[within_substrate_before_pooled]]).

### Synthetic validation of the unfold discriminator
`soc_synthetic_validate.py` — a new discriminator needs its own calibrator. Ground-truth processes, all
with the SAME 20× sinusoidal rate envelope:
Measured (these ran on full synthetic catalogs, n≈120-180k each — trustworthy):
| process | true memory | homogeneous CV | unfolded CV (W11→W101) | verdict |
|---|---|--:|--:|---|
| A inhom-Poisson (20× envelope) | none | 1.91 | 0.91→0.99 | → floor ✓ (no false-positive) |
| B Hawkes branch 0.5 | yes | 2.75 | 1.19→1.50 | memory survives ✓ |
| C Hawkes branch 0.8 | strong | 4.53 | 1.23→2.28 | survives more ✓ (monotone in branch) |
| D inhom-Poisson + duplicates | NONE | 2.35 | 1.22→1.33 | **fakes memory** — unfold can't remove |
- **Discriminator VALIDATED**: separates A (→floor) from B/C (survive), monotone in true branching ratio.
  **Two things it establishes:** (1) the rate envelope DOES inflate homogeneous CV substantially (A
  homogeneous CV=1.91 with zero memory) and the unfold correctly removes it back to the floor (0.91-0.99) —
  so local-rate unfolding is doing its job. (NB: at W11 even Hawkes-B reads only 1.19, near the floor, which
  is why the GOES tight-window dip is ambiguous and needs the full catalog + a wider bandwidth read.)
  (2) Duplicates (D) are INDISTINGUISHABLE from real memory (B) post-unfold (both ≈1.2-1.3 at W11) ⇒
  **dedup MUST precede unfold; the discriminator cannot rescue contaminated data.** This is precisely why
  the GOES FRM gate is mandatory and why the contaminated GOES unfolded-CV was uninterpretable. Banked as
  the calibrator for fact #3.

## SOC-pair synthesis (both halves complete)
- **Earthquakes (M≥4.5 global).** Mildly clustered (CV 1.20); the calibrator passes via PERTURBATION-
  RESPONSE — GK declustering moves ks_poisson 0.080→0.014 in the a-priori-known direction, and local-rate
  unfolding (0.34→0.29 mass, CV→1.07) shows most survives → triggering on a fairly stationary rate.
- **Solar flares (SWPC-clean, n=50,999).** AFTER the mandatory FRM-dedup gate: clustering is TIMESCALE-
  STRUCTURED — sub-Poisson at the shortest scale (unfolded CV 0.79 at W7), super-Poisson over multi-day
  windows (CV 1.78 at W501), and genuinely above the rate envelope (diverges from synthetic no-memory
  process A as W grows). Solar MIN is MORE residually-clustered than MAX (unfolded CV 2.27 vs 1.07),
  opposite the naive expectation. So flares DO carry real clustering, but at multi-day (active-region)
  timescales, not the sub-day inter-event scale — a sharper result than "strong clustering recovered".
- **Two substrates, two flavours of clustering** (the cross-substrate payoff): tectonic = mild, aftershock-
  triggering, declustering-removable, fairly rate-stationary; solar = timescale-structured, sub-day-regular
  / multi-day-clustered, cycle-modulated. Both required a completeness/integrity gate first (seismic Mc;
  solar FRM-dedup) — that gate is the transferable lesson.
- **Instrument facts (both)**: (1) ks_poisson/mass<τ/CV read clustering; Brody q & BR ρ are blind (rail at
  0). (2) pooled-NNS is provably (identically) time-reversal-invariant while Omori 3.1× and irreversibility
  z≈−2 prove the arrow is present in discarded observables. (3) the rate envelope DOES inflate homogeneous
  CV (synthetic A=1.91) and unfold removes it — the discriminator works, but cannot tell real memory from
  coincident duplicates (synthetic D), so a dedup gate is a prerequisite and the bandwidth sweep must be
  reported, not a single W. Synthetic-validated against Hawkes ground truth before banking.

Figure: figures/P_comcat_soc.png (4-panel: NNS clustered/declustered; calibration ladder incl. GOES
homog-vs-unfolded; railed one-sided fitters; directionality-gap panel).

## Open / queued
- Paleoseismic large-event recurrence (G3 real test; off-ComCat acquisition).
- Lower-Mc regional seismic catalog to reach the strong-clustering tectonic regime (if wanted).
- Per-active-region flare sequencing (would localise the solar triggering memory to within-AR).
