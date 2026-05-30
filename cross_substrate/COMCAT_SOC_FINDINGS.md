# ComCat + GOES SOC pair — FINDINGS (progress log, NOT validated results; verdicts Will's)

Phase brief: COMCAT_SOC_BRIEF.md. Run state: COMCAT_SOC_RUNSTATE.md. Date: 2026-05-30 (overnight).
Banked: coordinates/comcat-fingerprint.jsonl, coordinates/goes-fingerprint.jsonl, figures/P_comcat_soc.png.

## Data (entry-point audit clean — per-event origin times, not aggregates; §7.ter.19 safe)
- **Global M≥4.5, 2000-2025**: 173,122 events, 25.0 yr, 6924/yr, M[3.4,9.1]. (FDSN count cross-check 173,122.)
- **Central San Andreas box** (lat35-37, lon-122..-119) M≥2.5 1990-2025: 5,945 events (G3, N-limited).
- **GOES/SWPC flares** 1996-2025 via HEK: [pending fetch completion].

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
- This is the headline calibration: the excess was triggering (removed by declustering), not secular rate
  drift; and ARS moves in the known direction by the known amount. **ARS passes the clustering calibrator.**

## G3 — single-fault (N-LIMITED; no-false-positive regime, flagged)
- Central-SAF n=5945: ks_gue=0.426, ks_poisson=0.219 → MORE clustered than global (regional small-mag
  catalog = more aftershocks), NOT repulsion. No quasiperiodic level-repulsion signal.
- Honest scope: N too small for a repulsion CLAIM; a null here is uninformative and a positive would need
  surrogate confirmation. Characteristic-earthquake recurrence lives in the handful of on-fault mainshocks
  (N≈single digits) — below the robust-NNS point. Reported as no-false-positive-only, as briefed.

## G4 — directionality probe: the gap NNS structurally cannot see
- Pooled-NNS forward ≡ reversed: on a deterministic spacing axis the invariance is **EXACT** —
  raw ks_poisson fwd = rev = 0.079710, Δ = 0.00e+00. The ~1e-3 residual seen in the aggregate
  matched-fingerprint max|Δ| (0.001-0.008 run-to-run) is the Berry-Robnik bootstrap fitter's stochastic
  noise, NOT arrow sensitivity. The spacing engine is arrow-blind (§7.ter.10 band-invariance) — confirmed
  to machine precision.
- Ordering-sensitive observables DO see the arrow: irreversibility incr_skew z = −2.3, lagprod z = −2.0
  (vs shuffled-order surrogate); magnitude-conditioned **Omori after/before = 3.1×** (n_main=300, ±30d,
  100km) — 3× more events after a mainshock than before (causal aftershock decay; no symmetric foreshock
  buildup).
- The GAP: the same catalog gives strong clustering (mass excess, declustering-reversible) AND a strong
  time arrow (Omori 3.1×, irreversibility z≈−2), yet the pooled-NNS fingerprint is ~invariant under time
  reversal. Clustering is what the spacing engine reads; directionality is what it discards. A literal
  demonstration of the band-invariance proposition on a substrate with a lot of both.

## G5 — GOES solar-flare pair: clustering is GENUINE MEMORY (survives rate-envelope removal)
**220,548 GOES/SWPC flares 1996-2025 (HEK), 29 yr, 7606/yr.** (Many records have empty GOES class
→ flux NaN; fingerprint uses peak TIMES only, so unaffected. Detection threshold = completeness analogue.)

- Homogeneous fingerprint: ks_gue=0.509, ks_poisson=0.377; mass<0.3=**0.617** (Poisson-floor 0.259),
  CV=**8.71** — far MORE clustered than earthquakes (the SOC contrast: solar 8.7 vs tectonic 1.2 CV).
  Brody q / BR ρ railed at 0 again (one-sided-fitter fact, 2nd substrate).
- **Rate-envelope control (the load-bearing check, brief commitment #2 / ars-rate-dependence /
  within-substrate-before-pooled).** The solar cycle modulates flare rate ~20×, so a homogeneous-
  Poisson null would mistake the cycle ENVELOPE for clustering. Local-rate unfolding (inhomogeneous-
  Poisson null; sliding W-event window, W=21/51/201 all agree) removes the envelope:
  mass<0.3 0.617→**0.477**, CV 8.71→**1.56**. Drops substantially (envelope WAS inflating it) but stays
  **well above the inhomogeneous-Poisson floor** (~0.26 / 1.0). ⇒ Flares carry **genuine short-timescale
  memory** (sympathetic/triggered flaring) on top of the cycle envelope. The live Poisson-vs-memory
  question, answered on this catalog: **memory survives the correct null.**
- **Solar-cycle knob — read through unfolding (raw CV meaningless; see below).** MAX years (n=182,534):
  unfolded mass<0.3=0.502, CV=1.58. MIN years (n=8,388): unfolded mass<0.3=0.430, CV=2.06. The two
  Poisson-excess readouts DISAGREE on direction (mass: MAX>MIN; CV: MIN>MAX) and MIN is 22× smaller-N
  (noisier tail-driven CV). **Honest verdict: residual memory PERSISTS in both phases and is NOT strongly
  cycle-dependent once the envelope is removed.** The dramatic raw MAX/MIN difference was almost entirely
  the rate envelope + a pooling artifact — NOT a within-phase clustering difference. (Naive "MAX clustered,
  MIN Poisson" expectation NOT confirmed; the disciplined result is more defensible.)
- **Pooling-across-disjoint-years artifact caught (within-substrate-before-pooled).** The data-driven
  MAX/MIN split pools non-contiguous year-sets from 3 different solar cycles; each omitted boundary year
  injects one multi-year inter-event gap → raw CV = 122 (MAX) / 41 (MIN), pure artifact. Local-rate
  unfolding WITHIN each phase removes it. Banked as the reason raw split CVs are uninterpretable.

## SOC-pair synthesis
Two SOC substrates, same clustering question, both pass the calibrator AND yield a genuine result:
- **Earthquakes (M≥4.5 global)**: mildly clustered (CV 1.20); most survives local-rate unfolding
  (0.34→0.29 mass, CV→1.07) and is removed by GK declustering → triggering, on a fairly stationary rate.
- **Solar flares**: strongly clustered (CV 8.71); ~half is the solar-cycle rate envelope, but substantial
  short-timescale memory survives the inhomogeneous-Poisson null (CV 1.56) → genuine sympathetic flaring.
- **Instrument facts (both)**: ks_poisson/mass<τ/CV read clustering; Brody q & BR ρ are blind (rail at 0);
  pooled-NNS is exactly time-reversal-invariant (arrow-blind, §7.ter.10) while Omori 3.1× and
  irreversibility z≈−2 show the arrow lives in discarded observables.
- The clean cross-substrate axis: **homogeneous-vs-unfolded clustering ratio** distinguishes
  envelope-clustering (solar, big drop) from stationary-triggering-clustering (tectonic, small drop) —
  a new calibrator-zoo discriminator the local-rate-unfold control exposes.

Figure: figures/P_comcat_soc.png (4-panel: NNS clustered/declustered; calibration ladder incl. GOES
homog-vs-unfolded; railed one-sided fitters; directionality-gap panel).

## Methodological notes banked
1. **One-sided-fitter caveat** (G1): Brody/BR rail at 0 on super-Poisson; clustering needs the Poisson-
   excess-side readouts. Read alongside any future clustered substrate.
2. **Trim is clustering-robust** (G1, checked): the matched 2-98% trim does NOT attenuate the clustering
   readout — untrimmed vs trimmed mass<0.3 and CV are identical here. (A pre-registered worry, falsified by
   direct check — still worth re-checking per substrate, but not a general confound.)
3. **Declustering as a calibrator move** (G2): a known-direction perturbation (remove triggering) that ARS
   tracks correctly — a template for validating the engine against near-ground-truth.
