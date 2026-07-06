# criticality_tool — Full Capability Report for claude.ai

Self-contained summary of everything the toolkit can do, what it has done,
where it falls short, and what's available-but-unused. Paste-ready for
briefing a fresh claude.ai session. **Current as of 2026-05-15** (Phase
34f-E + BCGNT-2025 lit-lock; latest commit `6616ac5`; RESULTS.md
§7.ter.7–58).

> Companion internal docs: `README.md` and `EPISTEMIC_STATE.md` (both
> last fully rewritten 2026-05-11 — they predate the Phase 34d–34f
> arithmetic-spectral arc; this report is the most current synthesis).

---

## 1. What the tool is

The **Arithmetic Resonance Spectrometer (ARS)** is a point-process
universality classifier. It takes sorted event timestamps {t_k} (spike
times, photon arrivals, transaction timestamps, peak times, **or
arithmetic spectra** — L-function zeros, Maass-form Laplace
eigenvalues) and classifies the spacing statistics against universality
classes: Poisson, Wigner GOE / GUE / GSE, periodic-at-integer-q,
uniform-with-jitter.

The output is a fingerprint in a 2D plane defined by repulsion integral
(rep_int_q) and Ramanujan–Fourier amplitude (rf_amplitude_q), plus a
quadrant assignment (BL / TR / BR / TL / ambiguous). A calibration and
falsification protocol distinguishes signal-structure classifications
from extractor-pipeline artifacts.

It is an applied implementation of the Farey-rational PLL framework
(Planat & collaborators, FEMTO-ST 2002–2026); **it does not contribute
new theoretical mathematics.** Arithmetic-side outputs are
instrument-validation or methodology-validation against known
results — never claims that extend the underlying number theory.

**Two operating modes** (same engines, different front/back ends):

- **Empirical point-process mode** (Phases 10–33): the deployed
  `joint_q_profile` classifier on neural / astrophysical / financial /
  biological event trains.
- **Arithmetic-spectral mode** (Phases 34a–34f): the same NNS/RF/p-adic
  engines with a Weyl-law unfolding front-end and a Berry-Robnik ρ
  back-end, applied to arithmetic point processes (sign-change loci,
  L-function zeros, prime angles, Maass spectra).

Project layout (three sibling tools under `$HOME/fmexplorer/`):
`criticality_tool/` (ARS, this tool), `riemann_explorer/` (FM scanner),
`fm_explorer/` (handoff docs). **Run scripts with
`$HOME/fmexplorer/bin/python3`** — pandas lives only in that
venv; bare `python3` fails on `ars_classify`'s pandas import
post-reboot (not listed in requirements.txt; transitive via
phase22a/ars_classify.py).

---

## 2. Core classifier pipeline (used in every deployed empirical analysis)

```
sorted t_k (event timestamps)
  │  joint_q_profile(t_k, q_max=30)
  ▼
per-q DataFrame  (rep_int_q, rf_amplitude_q, ks_gue_q, ks_goe_q,
                  mass_lt_0_3_q, underpowered)
  │  joint_quadrant_diagnostic(df)
  ▼
per-q quadrant (BL / TR / BR_artifact / BR_novel / TL / ambiguous)
  │  modal-aggregate across well-powered q-bands
  ▼
(primary, rep_med, ks_gue_med, n_well)
```

Conventions: Q_MAX=30, MIN_EVENTS_PER_Q=30, JPF_CAP=1500.
Pre-processing: unit-mean unfolding → engine. Entry point:
`phase22a.ars_classify.classify(events)`.

**Two engines inside `joint_q_profile`** (architectural detail Phase
31a surfaced, formalised in EPISTEMIC_STATE.md / README §"What this is"):

- **NNS engine** (pooled passage-time spacings): operates on the
  unit-mean-normalised IEI distribution. Q-flat — f_pll = a/q cancels
  under unit-mean normalisation, so ks_gue_q and rep_int_q are
  essentially scalars replicated across q (std ~10⁻⁵). Carries
  dynamics-class signal at the recording-aggregate level. **Proved
  limitation (§7.ter.10 band-invariance):** this architecture is
  invariant under linear time scaling and cannot detect prime-base
  asymmetry on stationary signals.
- **RF engine** (`ramanujan_fourier` per q, indicator mode): genuinely
  per-q via Ramanujan sums. The TL flag (per-q RF spike |a_q| > 5×
  median) is the only modally-discriminating per-q signal in the
  deployed pipeline. Carries per-prime arithmetic-class signal; powers
  p-adic v4.

The classifier operates at **two timescales** — full-sequence and
per-window. Full-sequence survival does not imply per-window survival;
any surrogate-survival claim must specify scope (Phase 31/32a).

Quadrants: **BL** rep<0.10, no RF spike → Poisson; **TR** 0.10–0.55,
no spike → Wigner (GUE/GOE/GSE); **BR_artifact** ≥0.55, no spike →
uniform-with-jitter saturation; **BR_novel** ≥0.55 reserved for
well-fitting Wigner despite saturated rep_int; **TL** ≥0.10 with RF
spike → periodic at integer period q.

---

## 3. Ramanujan–Fourier engine — `ramanujan_fourier(t_k, q_max, normalize, n_bins)`

- `normalize=True` (default): RF on unit-mean-normalised intervals;
  spacing-correlation patterns; period-insensitive.
- `normalize=False` (indicator mode): RF on the integer-time-bin event
  indicator; detects integer-period structure (weekly=7, monthly=30 in
  day units). The indicator-mode |a_q| are the discriminating signal
  for the TL quadrant and the p-adic engine.

Returns {q_values, amplitudes, top10_q, peak_q, mode}.

---

## 4. p-adic engine — `padic_amplitude_v4(t_k)` (deployed canonical)

For each prime p ∈ {2,3,5,7,11,13} and q_max=200, sums |a_q| over
q ∈ {p, p², …} ∩ [1,q_max], normalised two ways: `normalised` (vs total
RF power; small-prime-biased) and `normalised_per_q` (mean per
pure-power band ÷ global mean; recommended). Returns
`dominant_prime_per_q`.

Status: validated on synthetic period-injection (5/6 single-prime
detections; period-13 narrow miss at tested SNR). v1–v3 (padic_profile /
padic_per_band) failed acceptance via the §7.ter.10 band-invariance
proposition; v4 sidesteps by working in the RF-amplitude domain.

**Now applied** (no longer "unused"):

- **Phase 32a/31 Round-4:** per-window p-adic at q_max=200 on V1
  recordings. Cross-substrate prime-specific axis is real but
  **temporal-scope-split** — pvc-11 carries it long-term, Allen
  short-term; pvc-11 natural-movie p=7 NULL vs Allen +3.49 (§7.ter.39,
  §7.ter.41).
- **Phase 32b:** cross-engine correlation F1/F0↔rep_med (NNS) vs p=7
  (RF) — Allen INDEPENDENT_AXES (ρ=−0.086, n=6); two-engine direction
  match is **two findings, not one** (§7.ter.42, §7.ter.50).
- **Phase 34a–34d:** RF + p-adic v4 as the "orthogonal channel" survey
  on arithmetic substrates (see §12b).

---

## 5. Calibrator zoo — `calibrator_panel.STATIONARY_CALIBRATORS` + `TRANSITION_CALIBRATORS`

Eight stationary classes (ground-truth quadrant labels): `poisson`
(BL), `beta=1_GOE` / `beta=2_GUE` / `beta=4_GSE` (TR), `zeta_first_400`
(TR), `uniform_jitter` (BR_artifact), `periodic_q7` (BR_artifact),
`mixed_q7_q12` (TR). Acceptance: 7/8 must land before any analysis;
verified at every phase start; current 8/8 PASS.

Transition calibrators (Phase 20.5+): blended GUE↔Poisson (sharp_step,
sigmoidal, linear_ramp, metastable_middle), logistic-map (chaotic,
period-4), Mackey-Glass. Via EXTENDED_CALIBRATORS.

**Arithmetic-spectral calibrators (Phase 34d–34f):** Poisson, Wigner
β=1/2/4 (Hermite tridiagonal), COE/CUE/CSE (Mezzadri 2007
QR-with-phase), Berry-Robnik mixtures (known ρ), synthetic Weyl spectra
(2-D quadratic + 3-D cubic). The phase34f synthetic-validation harness
runs Poisson/GOE/BR-0.3 through the full pipeline; **all 6 gates pass**
for both the Picard (34f-G) and Bianchi-Z[ω] (34f-E) volumes.

---

## 6. Surrogate battery — `phase22a/h2_surrogates.py`, `surrogates.py`

`rate_matched_poisson` (per-unit rate; **operational default since
Phase 26**), `cell_shuffle`, `ln_evoked`, `state_modulated`,
`lightcurve_modulated_poisson`. Phase 26 lesson (standing discipline):
surrogate floor must match the rate regime of the analysis.

Coupled-GLM Pillow-style surrogate (Pass D, Phase 22b/25) =
**FIT-CEILING** — methodologically untestable in the Phase 25 family;
use Pillow's non-positive history-kernel constraint.

**Arithmetic-substrate nulls (Phase 34a–34d, standing discipline):**

- **Support-set-respecting nulls (§7.ter.47, Phase 34a):** the
  surrogate must respect the arithmetic point process's support set
  (squarefrees, primes, …). Sibling of §7.ter.19.
- **Right-null is substrate-specific (§7.ter.48, Phase 34b):** the
  structural null depends on the substrate's generative mechanism
  (support / random-walk / unfolding) — not one universal null.
- **Bootstrap σ² + 20-seed subsample-replicate (§7.ter.51, Phase
  34d):** single-shot NNS verdicts near the TR/BL boundary need a
  20-seed 80%-subsample replicate; report the distribution, not a
  single quadrant (§7.ter.22-application).
- **Pooled-substrate sub-pool sweep (§7.ter.49, Phase 34c):** pooling
  sub-populations (EC root number, CM/non-CM) can manufacture a
  false-positive; stratify before pooling.

---

## 7. PLL bank — `pll_bank.py` (parallel infrastructure, not on deployed path)

Literal second-order PLL bank (quadrature mixer + IIR LPF; e =
sin(φ_sig−φ_osc), v = ρv + K_i·e, dφ = K_p·e + v; lock detection; CPU +
CuPy/CUDA, 3.5e-6 parity). **Not used by any deployed ARS
classification** — `arithmetic_toolkit` imports only `farey_rationals`.
Phase 31a established `joint_q_profile` and `pll_bank` are distinct
objects, not closed-form limits of each other. Phase 31c (PLL-as-ARS,
ISF per Hajimiri–Lee 1998) **scoped, still not executed.**

---

## 8. Per-class parameter recovery — `bulk_recovery.py` + `phase34e/run_berry_robnik.py`

`bulk_recovery.py`: β̂ (Wigner, n≥1000 for ≥80% CI), σ̂ (uniform_jitter,
n≥200), period+jitter (periodic, n≥200).

**Berry-Robnik ρ fitter — `phase34e/run_berry_robnik.py` (Phase
34e/34f):** MLE fit of empirical NNS to the Berry-Robnik P_BR(s;ρ)
interpolation (ρ=0 Poisson … ρ=1 GOE), 30-bootstrap σ. **Numerically
normalized PDF** (Z, μ via scipy.quad, cached on a ρ-grid) guaranteeing
∫P=1 and ∫sP=1 — see the bug history in §16. Synthetic-validated:
pure Poisson → ρ≈0.09, pure GOE → 1.00, BR-0.3 → 0.26.

---

## 9. Multi-order falsification

Every ARS classification reports the full per-q DataFrame, not just
the modal collapse: inspect `quadrants_per_q` (unanimous vs contested),
`rep_int_per_q`/`ks_gue_per_q` (sub-modal variation), TL-flagging
q-bands. **Caveat:** the NNS engine is q-flat (§7.ter.39 / §16 item 8)
— only the RF engine has true per-q channels.

---

## 10. Spatial / local-cluster analysis — Phase 27 Analysis 3 + Phase 28 (COMPLETE)

Per-cluster ARS on neighbour-windowed unit subsets vs recording-wide
aggregate.

- **Phase 27 (pvc-11, Utah 400 µm):** CONTRA-OHIORHENUAN bounded to
  400–600 µm — local clusters show *less* structure than aggregate
  (§7.ter.37).
- **Phase 28 (Allen Neuropixels, <300 µm) — COMPLETE (§7.ter.40,
  commit `9edeb25`):** **SPATIAL-SCALE-DEPENDENT**, non-monotone
  TR-fraction; the local bin (100–300 µm) is the *least* TR-structured.
  The Ohiorhenuan engagement caveat is **CLOSED**. (Supersedes the
  stale "built but not committed; aborted" status in older reports.)

---

## 11. Kuramoto simulator — `phase30/kuramoto.py` (Phase 30, COMMITTED `58f87e3`)

All-to-all Kuramoto, Lorentzian frequencies, classical/stochastic;
2π-wrap spike generation; per-oscillator rate-matched surrogate; |r(t)|.
K_c = 2γ (Strogatz 2000), corrected from the brief's 2γ/π.

Phase 30 verdict (§7.ter.38): **NO MECHANISTIC MATCH** — Analysis 1
INSENSITIVE (BR_artifact at every K); Analysis 2 RATE_REGIME_CONFOUNDED
(K) / PARTIAL_RATE_CONFOUND (σ); Analysis 3 156/160 well-powered real
V1/Allen rows have no Kuramoto cell match. Kuramoto-class formalism does
**not** explain ARS findings. Alternative coupled-oscillator models
(Stuart–Landau, Wilson–Cowan, coupled HH, latent-state generative) are
the load-bearing forward direction.

---

## 12. Stationarity check — `phase30/stationarity.py`

Non-overlapping-window NNS classification: non-stationary if
fraction_modal < 0.90 OR CV(rep_med) > 0.20 OR CV(ks_gue_med) > 0.20.
Phase 30 critical-band check: 0/15 + 0/54 boundary cells flagged.
Standard preprocessing pass going forward.

---

## 12a. Arithmetic-spectral pipeline (Phases 34e–34f) — NEW MAJOR CAPABILITY

The same NNS/Berry-Robnik engines with a **Weyl-law unfolding
front-end**, applied to Maass-form Laplace eigenvalue spectra.

- **2-D unfolding** (`phase34e/sl2z_unfolding.py`): SL(2,ℤ) x_j =
  r_j²/12; Γ₀(N) x_j = [SL(2,ℤ):Γ₀(N)]/12 · r_j² (λ = 1/4 + r²).
- **3-D Bianchi unfolding** (`phase34f/bianchi_unfolding.py`): cubic
  Weyl x_j = vol·r_j³/(6π²), λ = r²+1. Volumes **PINNED Humbert-direct**
  (commit `c2cbf22`): Picard G/3 ≈ 0.30532186 (Then 2003 anchor);
  Bianchi-Z[ω] √3·L(2,χ₋₃)/8 ≈ 0.16915693. `volume_constants_self_test()`
  enforces the chain against the Then-2003 Picard anchor; EGM 0.0846 is
  the ω↔ω² Z/2 extended-orbifold quotient (cited, not used).
- **Maass loader** (`phase34e/maass_loader.py`): Seymour-Howell 2022
  Zenodo parser; Γ₀(N) index + Weyl constant.
- **Sato-Tate** (`phase34e/run_sato_tate_v3.py`): a(p) at primes, no
  rescale (SH 2022 §3 Hejhal-lineage convention).

**Phase 34e — Γ₀(N) Maass calibrator (§7.ter.52, commits `a458e02` +
`0723183`): SARNAK_ANOMALY_REPLICATED_AT_GAMMA0_N_SQUAREFREE.** 6
squarefree levels {91,95,85,77,93,87}: bulk-Δ NNS BL on all 6 in 20/20
seeds (rep_med 0.02–0.07); corrected Berry-Robnik ρ_GOE = 0.126±0.032
(near-Poisson, just above the 0.09 pure-Poisson fitter baseline);
Sato-Tate semicircular KS p=0.22–0.77. N=1 SL(2,ℤ) trivial level
pending LMFDB access.

**Phase 34f-G / 34f-E — 3-D Bianchi pipelines: both
PIPELINE_VALIDATED_READY_TO_FIRE; both substantive
DATA_ACQUISITION_BLOCKED.**

- 34f-G (Picard, **replication** leg, §7.ter.57): Then 2003's 13,950
  eigenvalues unpublished (~60 OCR-mangled samples only); LMFDB Bianchi
  reCAPTCHA-blocked; de-novo Hejhal-on-ℍ³ multi-week. Pipeline
  synthetic-validated 6/6.
- 34f-E (Bianchi-Z[ω] Q(√−3), **first-measurement** leg, §7.ter.58,
  commit `8cbd40a`): `phase34f/zomega_loader.py` (§D.0a/§D.0b gates,
  self-validated on known-good + known-bad inputs) +
  `run_pipeline_validation_e.py` (6/6 gates, statistics identical to
  34f-G — confirms volume-substrate-correctness). No accessible Z[ω]
  Maass dataset. Pre-spec labels:
  `SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA` /
  `_WITH_FIELD_SHIFT` / `NO_ANOMALY_AT_PSL2_Z_OMEGA`.
- The Q(√−3) three-coordinate closer (§D.4) is now **34f-E-Δ-Maass-
  blocked only** — 34d-E angle + 34c χ₋₃ zero data already cached; all
  closer infrastructure built + validated.

**BCGNT-2025 lit-lock + cohomological-H cell brief (commit `6616ac5`,
EXECUTION HELD).** Boxer–Calegari–Gee–Newton–Thorne 2025 (Forum Math Pi
v13 e10, arXiv:2309.15880) proves Ramanujan + Sato-Tate
**unconditionally** for *cohomological* (regular-algebraic
parallel-weight) Bianchi forms over CM fields — **NOT** the
non-cohomological Bianchi-Maass substrate (definitional; the
Ramanujan-conditional caveat stands for 34f's Maass cells). This makes
Cremona's LMFDB cohomological Bianchi-newform Hecke eigenvalues a
*proven*-Sato-Tate-equidistributed dataset (non-CM stratum) →
`PHASE34F_COHOMOLOGICAL_H_BRIEF.md` (brief written, execution held for
review): calibrate the Sato-Tate engine against a *proven theorem*
(new asymmetric-label tier — see §17). Scope-bounded: H-side
methodology validation only; does NOT advance the Q(√−3) Δ-closer.

---

## 12b. Orthogonal-channel survey (Phases 34a–34d) — arithmetic RF/p-adic

The "orthogonal channel" survey applies RF + p-adic v4 (and bulk-NNS)
to arithmetic substrates, asking whether structure survives the
*right* (substrate-specific) null.

- **34a Mertens, 34b Liouville sign-changes (§7.ter.47–48):**
  NULL_IN_ORTHOGONAL_CHANNELS beyond the support/random-walk null.
  Dual-layer cross-phase: PARALLEL_SIGNAL@wrong-null +
  PARALLEL_NULL@right-null.
- **34c ζ + Dirichlet + EC L-zeros (§7.ter.49):** 5/6
  NULL_BEYOND_RMT; EC root-minus q=17 AMBIGUOUS (pooling-null
  methodology gap → false-positive-equivalence-class typology).
- **34d Gaussian + Eisenstein prime angles (§7.ter.51):** the
  spectral-coordinate prime-angle sub-family (Rudnick-Waxman 2019).
  **RW_SHAPE_CONFIRMED_AT_FINITE_X** — the saturation deficit resolves
  as a finite-X correction; Eisenstein β=0.65 hits the RW asymptote
  1.000±0.022 within 1σ at X=10⁸. Both substrates BL-bulk in the
  20-seed subsample-replicate (an earlier TR was a threshold artifact).
  Cross-phase = METHODOLOGICAL_CONSISTENCY (not "convergent null").
  Lesson: stride-decimation destroys prime-angle structure — full-N
  required for bulk readout on S¹ unit-orbit-quotient substrates;
  RW Prop 5.3 forces σ²(K,X) as the required global-moment complement
  to bulk-ARS on Wigner-Dyson β-class right nulls.

---

## 12c. Cross-domain envelope (Phases 33a–33c)

Probing whether ARS structural readouts transfer to non-neural domains.

- **33a NANOGrav pulsar TOAs (§7.ter.44):** STRUCTURAL_MISMATCH —
  published TOAs are folded-template aggregates. §7.ter.19 generalises
  across domains to **any pre-aggregated published product**.
- **33b CERN Open Data (§7.ter.45):** STRUCTURAL_MATCH_BOUNDED —
  NanoAOD strips timestamps; mass-spectrum framing is
  instrument-validation only.
- **33c single-molecule fluorescence (§7.ter.46):**
  STRUCTURAL_MISMATCH + INSTRUMENT_VALIDATION_BOUNDED. Substantive
  result = convergent-validation across 4 fields on §7.ter.19.
- **Cross-domain audit discipline:** three pre-pilot questions
  (published-product level / surrogate adequacy / calibrator-zoo
  coverage) at the entry point of any cross-domain phase brief.

---

## 13. Domain pipelines (full deployed list)

| Pipeline | Domain | Status |
|---|---|---|
| phase22a/, phase22b/ | pvc-11 macaque V1 (Smith & Kohn) | **LOCKED** H1 ρ_partial +0.720 / H2 surviving / FIT-CEILING Pass D |
| phase24/ | Allen Brain Observatory awake mouse V1 (12 sessions) | **LOCKED** H1 cross-species (meta ρ +0.363); F1/F0 substrate-systematic sign-flip |
| phase25/ | V1 multi-frame STA Pass D | FIT-CEILING (canonical→kernel collapse / unconstrained→runaway) |
| phase26/ | GRB 230307A QPO replication + rate-regime reframe | substantive FAIL + per-cell rate-regime feature (ρ −0.48 → −0.89) |
| phase27/ | Pre-publication framing | F1/F0 substrate-systematic LOCKED; ks_gue_med SUBSUMED by 8-factor FA (R²=0.73–0.80); rep_med ORTHOGONAL; spatial CONTRA-OHIORHENUAN 400–600 µm |
| phase28/ | Allen Neuropixels <300 µm spatial-scale | **COMPLETE** §7.ter.40 — SPATIAL-SCALE-DEPENDENT, non-monotone, Ohiorhenuan caveat CLOSED |
| phase30/ | Kuramoto simulation testbed | NO MECHANISTIC MATCH (committed `58f87e3`) |
| phase31b/ | Engineering-layer audit + deployed-classifier sensitivity | §7.ter.39 — joint_q_profile ≠ pll_bank; +0.23 residual rate-stratified within-cell |
| phase32a/ | pvc-11 natural-movie per-window p-adic q_max=200 | §7.ter.41 PER_WINDOW_SUBSTRATE_CONSISTENT; stimulus-content ruled out |
| phase32b/ | cross-engine F1/F0↔rep_med vs p=7 | §7.ter.42/50 Allen INDEPENDENT_AXES; both axes novel |
| phase32c/ | awake macaque V1 data-pathway assessment | §7.ter.43 MIXED → DATA_AVAILABLE_BUT_INCOMPATIBLE |
| phase33a/b/c/ | NANOGrav / CERN / single-molecule cross-domain | §7.ter.44–46 STRUCTURAL_MISMATCH(_BOUNDED); §7.ter.19 generalised |
| phase34a/b/ | Mertens / Liouville sign-changes | §7.ter.47–48 NULL_IN_ORTHOGONAL_CHANNELS @ right-null |
| phase34c/ | ζ + Dirichlet + EC L-zeros | §7.ter.49 5/6 NULL_BEYOND_RMT; EC q=17 AMBIGUOUS |
| phase34d/ | Gaussian + Eisenstein prime angles | §7.ter.51 RW_SHAPE_CONFIRMED_AT_FINITE_X |
| phase34e/ | Γ₀(N) Maass calibrator | §7.ter.52 SARNAK_ANOMALY_REPLICATED_AT_GAMMA0_N_SQUAREFREE |
| phase34f/ | Picard + Bianchi-Z[ω] 3-D Bianchi pipelines | §7.ter.57/58 both PIPELINE_VALIDATED_READY_TO_FIRE; substantive DATA_ACQUISITION_BLOCKED; cohomological-H brief execution-held |
| bgp_pipeline.py | BGP route timing | exploratory PoC (§7.ter.27) |
| grb_pipeline.py | GRB photon timing | lightcurve-modulated Poisson surrogate central |
| run_eeg_* | PhysioNet EEGMMIDB θ-band ZCR | FALSIFIED — bandpass filter artifact |
| run_fungal_nns.py | Adamatzky mycelium spikes | super-Poissonian, n=1470 (§7.ter.5) |
| run_earthquake_nns.py | USGS M≥4.5 | Poisson-clustered (mass<0.3=0.33); ETAS-consistent |
| run_phase14_binance.py | BTCUSDT trade timing | essentially random (BL) |
| run_phase10_llm.py–17 | LLM cascade fingerprints | extraction-pipeline-artifact lessons (§7.ter.14–23) |
| run_dirichlet_*, run_lmfdb_*, run_zeta_*, run_primes_scaling.py, run_mertens_liouville.py, run_padic_v4.py | Arithmetic L-functions / ζ / primes | INSTRUMENT-VALIDATION (reproduce known literature results) |
| run_phase9_extended.py, run_phase11_planat.py, run_chirp_prediction.py | Planat / number-theoretic models | bounded (§7.ter.16) |

---

## 14. Auxiliary infrastructure (selected)

Empirical-mode: `extractors.py`, `boundary_extractor.py`,
`extractor_distinctness.py`, `intermittency.py`, `topology_hawkes.py`
(§7.ter.27), `dfa.py`, `signal_gen.py`, `field_generator.py` (FM
coherence), `transition_calibrators_blended.py`,
`transition_calibrators_dynamical.py`, `as_topology.py`,
`universality.py`, `bulk_recovery.py`, `fix_gue_generator.py`,
`phase34c/rmt_sampler.py` (β-Hermite / Mezzadri COE/CUE/CSE).

Arithmetic-spectral mode: `phase34e/maass_loader.py`,
`sl2z_unfolding.py`, `run_nns_classification.py`,
`run_berry_robnik.py` (synthetic-validated fitter),
`run_sato_tate_v3.py`, `run_cross_level.py`, `plot_phase34e.py`;
`phase34f/bianchi_unfolding.py` (pinned volumes + self-test),
`zomega_loader.py` (Z[ω] schema + §D.0a/§D.0b gates),
`run_pipeline_validation.py` (34f-G), `run_pipeline_validation_e.py`
(34f-E).

---

## 15. Validated outputs (the headline list)

**Arithmetic / number-theoretic (instrument or methodology
validation — do NOT extend the corresponding literatures):**

- Riemann ζ first 2,000 zeros: KS_GUE = 0.041, rep_int = 0.425; at
  heights ~10⁶: KS_GUE = 0.012–0.015.
- LMFDB 87 elliptic-curve L-functions, ~10,000 zeros: bulk GUE, edge
  separation by root number.
- Dirichlet L q ≤ 149, 630 characters, 4.05M pooled spacings: bulk
  GUE; conductor-normalised γ₁ separates Sp from U at p=0.001.
- Primes ≤ 10⁶ (log-density unfolding): σ̂ ≈ 0.048; twin primes ≤ 10⁷:
  σ̂ ≈ 0.093. *(Corrected: the prior report's primes line was
  corrupted in transcription.)*
- Mertens / Liouville sign-changes (34a/b): NULL in RF + p-adic v4
  beyond the support / random-walk null.
- ζ / Dirichlet / EC L-zeros (34c): 5/6 NULL_BEYOND_RMT.
- Gaussian / Eisenstein prime angles (34d): RW shape confirmed at
  finite X (Eisenstein hits the RW asymptote within 1σ at X=10⁸).
- Γ₀(N) Maass (34e): **SARNAK_ANOMALY_REPLICATED_AT_GAMMA0_N_
  SQUAREFREE** across 6 squarefree levels (bulk-NNS BL 20/20 seeds;
  near-Poisson Berry-Robnik ρ; semicircular Sato-Tate). The first
  cross-level joint analysis on the integrated toolchain.
- 3-D Bianchi pipelines (34f-G/E): synthetic-validated, ready-to-fire;
  substantive verdicts DATA_ACQUISITION_BLOCKED (no fabrication).

**Physical / biological:**

- USGS M≥4.5: Poisson-clustered (mass<0.3=0.33).
- Adamatzky fungal mycelium: super-Poissonian (mass<0.3=0.65), n=1470.
- Solar X-ray flares: Poisson-clustered. Binance BTCUSDT: BL.
- EEG θ-band ZCR: FALSIFIED — bandpass filter artifact.
- pvc-11 macaque V1: H1 OSI↔ks_gue_med ρ_partial +0.720 (LOCKED); H2
  surviving on monkey1_natural_movie + monkey2_gratings_movie at 30/30
  q-bands × 7 seeds (LN-Poisson floor); F1/F0↔rep_med +0.388 (LOCKED).
  Phase 25 FIT-CEILING on history-coupled-GLM elimination + positive
  temporal-autocorrelation co-finding.
- Allen awake mouse V1: H1 LOCKED cross-species (meta ρ +0.363, 12/12
  positive); DSI cross-species REPLICATED stronger; F1/F0
  substrate-different (meta −0.183); H2 BOUNDED to pvc-11.
- GRB 230307A: Chen 2025 909 Hz QPO substantively FAIL; late-prompt TR
  reframed as per-cell rate-regime feature (Phase 26).
- Phase 28: SPATIAL-SCALE-DEPENDENT, Ohiorhenuan caveat closed.
- Phase 30: Kuramoto-class formalism does NOT explain ARS — NO
  MECHANISTIC MATCH.
- Cross-domain (33a-c): STRUCTURAL_MISMATCH(_BOUNDED);
  convergent-validation of §7.ter.19 across 4 fields.

---

## 16. Known failure modes (check before claiming any new result)

1. **Continuous-trace + peak-detection extraction** — spacing stats =
   trace autocorrelation length, not dynamics (§7.ter.19).
2. **Threshold-upcrossing on near-iid input** → rep_int_q ≈ 0.34 → TR
   on pure noise. Any threshold-extractor TR needs an
   equivalent-statistics noise control (§7.ter.23).
3. **rep_int_q is a signal-level scalar in BR_artifact** — per-q
   variation at FP noise (§7.ter.22).
4. **σ̂ recovery** = gap-distribution position in the calibrator
   family, not the underlying signal (for peak-extracted traces).
5. **Sample-size by class** — Wigner β̂ needs n≥1000; others ≥200.
6. **Pooled-rate surrogate failure** (Phase 26) — surrogate at the
   analysis rate regime.
7. **JPF_CAP=1500** caps per-q passage; large recordings subsampled
   (shape preserved, classification unchanged).
8. **NNS engine is not per-q** (§7.ter.39) — ks_gue_q / rep_int_q are
   q-flat scalars; only the RF engine has true per-q channels.
   Confidence-stratifying NNS findings "by channel" is meaningless.
9. **Un-normalized distribution-fitter bias (§7.ter.57, Phase 34f).**
   The Berry-Robnik P_BR(s;ρ) closed form was un-normalized for
   intermediate ρ (∫P=1.12 at ρ=0.3); MLE positive bias fitted pure
   Poisson to ρ≈0.44, contaminating Phase 34e Test 2 (since corrected
   to ρ≈0.126, Sarnak conclusion strengthened). Caught only because
   the phase34f synthetic-validation harness exercised the fitter on
   known-ground-truth inputs. **Synthetic-validate any
   distribution-fitter against known truth before treating a fitted
   parameter as an absolute measurement.**
10. **Pooled-substrate right-null gap (§7.ter.49, Phase 34c).** Pooling
    sub-populations (EC root number, CM/non-CM) can manufacture a
    false positive; stratify before any aggregate statistic.
11. **Stride-decimation destroys prime-angle structure (§7.ter.51,
    Phase 34d).** Full-N required for bulk readout on S¹
    unit-orbit-quotient substrates.
12. **Data-acquisition discipline.** When the underlying dataset is
    unavailable (Then 2003 list; Z[ω] Maass), the verdict is
    DATA_ACQUISITION_BLOCKED — never fabricate an underpowered result
    from OCR-mangled samples or unavailable data.
13. **venv trap.** Bare `python3` post-reboot misses pandas; use
    `$HOME/fmexplorer/bin/python3`.

---

## 17. Architectural caveats / scope clarifications

- The "Farey-bank of PLL channels" framing is metaphorical for the
  deployed classifier. The literal `pll_bank.py` is parallel
  infrastructure off the deployed path.
- H1 OSI↔ks_gue_med is LOCKED cross-species but ks_gue_med is SUBSUMED
  by 8-factor FA on pvc-11 (R²=0.73–0.80). Biological correspondence,
  not orthogonal-novelty.
- H2 surviving structure is BOUNDED to pvc-11 (Allen 3/12 default, 1/8
  rate-matched).
- Coupled-GLM Pillow surrogate FIT-CEILING on V1 natural-movie.
- **Asymmetric verdict-label discipline (Phase 34d+, METHODS §1) —
  THREE epistemic tiers:** (i) *empirical-anchor* (published
  numerical/asymptotic prediction — `RW_SHAPE_CONFIRMED_AT_FINITE_X`);
  (ii) *structural-extension first-measurement* (no published
  prediction — `SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA`,
  never "REPLICATED"); (iii) *proven-theorem calibration* (target is a
  proven theorem — `SATO_TATE_METHODOLOGY_VALIDATED_AGAINST_PROVEN_
  TARGET_BCGNT2025`; instrument-scoped, never a result/discovery, no
  leak onto unrelated coordinates). Treating tiers symmetrically leaks
  an unearned claim.
- **Two-regime Ramanujan-conditionality (Phase 34f, BCGNT 2025).**
  Cohomological Bianchi = Ramanujan/Sato-Tate *proven* (BCGNT); the
  non-cohomological **Bianchi-Maass** substrate (34f-G/E-Δ) stays
  *conditional* (GHY 2025 path). State the regime per substrate;
  CM/non-CM stratify-before-pool (Phase 34c precedent).
- **Bulk-NNS is unfolding-scale-invariant** — the 34f volume
  reconciliation changes no verdict; RW-class substrates additionally
  require the σ²(K,X) global-moment readout (bulk-ARS alone is "right
  β class" only).
- Arithmetic outputs are instrument/methodology-validation — ARS does
  not extend the underlying number theory.

---

## 18. What hasn't been done / opportunities

1. **Phase 34f-G / 34f-E data acquisition** — the single blocking
   dependency for the Q(√−3) three-coordinate closer. Pipelines
   ready-to-fire. Paths: Then direct / Strömberg-Lemurell archives /
   LMFDB non-reCAPTCHA / de-novo Hejhal-on-ℍ³ (multi-week).
2. **Cohomological-H cell** — brief written, execution held for
   review; CM-stratum target measure is the open pre-spec item.
3. **N=1 SL(2,ℤ) Maass** — pending LMFDB access (reCAPTCHA-blocked).
4. **Cross-coordinate Test 4 (§D.4)** — 34f-E-Δ-Maass-blocked only;
   34d-E + 34c χ₋₃ data cached.
5. **PLL bank as alternative ARS** (Phase 31c) — scoped, not executed;
   ISF per Hajimiri–Lee.
6. **RF engine per-q sensitivity** — ∂|a_q|/∂t_k closed-form via
   Ramanujan-sum derivative (Phase 31b-class).
7. **Sub-modal continuous-metric promotion** — Phase 30 surfaced +0.10
   K-axis drift / +0.23 Δks residual the modal collapse discards.
8. **Kuramoto alternatives** — Stuart–Landau / Wilson–Cowan / coupled
   HH / latent-state generative (Phase 30 forward direction).
9. **Stationarity check retroactively** to all existing
   classifications.

---

## 19. Per-phase commit convention (for orientation)

- RESULTS.md: each phase adds `### 7.ter.N` (chronological body) + a
  §8 "Validated outputs" bullet. **One commit per phase**
  (code + RESULTS + in-place cross-phase amendments).
  Reconciliation/lit-lock batches are separate commits with no §7.ter
  number when nothing is executed.
- Brief→execute pattern: a `PHASE..._BRIEF.md` (Frame / Goals /
  Acceptance / Out-of-scope / Methodological commitments + verdict
  vocabulary) is reviewed before execution; findings docs mirror it.
  Asymmetric verdict labels per the §17 tiers.
- §7.ter ladder spans **§7.ter.7 → §7.ter.58** (53–56 are
  sub-generalisations inside the 34e/34f entries). Latest committed:
  **§7.ter.58 (Phase 34f-E), commit `8cbd40a`**; head `6616ac5`
  (BCGNT lit-lock + cohomological-H brief, execution held).
- Phases 28 / 30 / 31 are committed (older reports' "uncommitted"
  status is stale). Phase 31c is scoped, not executed.
- Pushes are manual (codeberg credential unavailable in-session).

---

## 20. Key memory entries (live state across sessions)

`~/.claude/projects/-home-combust-fmexplorer-criticality-tool/memory/`
— MEMORY.md index (41 entries). Highlights:

- **User / project:** FM-coherence + lock-statistics for arithmetic
  signals; three sibling tools; venv-python-required; brief-template;
  RESULTS.md phase convention; tarball convention; GPU-sweep/CPU-refine.
- **Claim status:** ARS claim status (2026-05) — H1 LOCKED
  cross-species, F1/F0 substrate-systematic LOCKED, H2 PVC-11-SPECIFIC,
  FIT-CEILING coupled-GLM; rate-regime dependence lesson.
- **Neuro phases:** phase28_complete (spatial-scale-dependent,
  Ohiorhenuan closed); phase30_kuramoto_bounded; phase31_engineering_
  audit; phase32a/b/c; session handoffs.
- **Cross-domain:** phase33a/b/c; cross-domain audit discipline.
- **Arithmetic arc:** phase34a/b/c complete; support-set-respecting
  nulls; right-null-substrate-specific; false-positive equivalence
  classes; phase34d complete + lit summary; stride-decimation lesson;
  bulk-vs-global-moment readout; seed-replicate-near-boundary;
  phase34e_34f_complete (Sarnak replicated; both Bianchi pipelines
  validated-ready-to-fire; BCGNT lit-lock; cohomological-H brief
  execution-held); synthetic-validate-fitters (§7.ter.57).

---

*Source: criticality_tool/README.md, EPISTEMIC_STATE.md, METHODS.md,
RESULTS.md §7.ter.7–58 + §8, code under criticality_tool/, and the
memory index at
~/.claude/projects/-home-combust-fmexplorer-criticality-tool/memory/.
Current as of 2026-05-15 (commit 6616ac5).*
