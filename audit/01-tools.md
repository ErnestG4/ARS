# Audit 01 — Tool Inventory (Phase 1)

READ-ONLY ground-truth inventory of the ARS codebase at
`/home/combust/fmexplorer/criticality_tool` (= codeberg.org/Combust/ARS).
No code was modified. Scope: **canonical + drift** — the live tool surface;
`phaseNN/` dirs are application drivers, not re-audited line-by-line (duplicate
estimator copies noted where seen).

## Honesty / provenance notes (read first)

- **Citation provenance.** Layers **B** and **C** rows were read line-by-line by
  the auditor in this session (`[code]` = verified here). Layers **A** and **D**
  were inventoried largely via two read-only sub-agents over ~93 `cross_substrate/`
  files + root `run_*.py`; their `file:line` citations are **mostly correct but
  not every line was independently re-opened by the auditor**. Rows the auditor
  personally spot-verified are marked **(verified)**; the rest are
  **(agent-relayed)** and should be re-confirmed in a deeper Phase if a citation
  is load-bearing. This is flagged rather than laundered into clean-looking truth.
- **Could-not-locate items** are listed at the bottom — never inferred into
  existence.
- **Drift findings** (code disagreeing with docstrings / two copies of an
  estimator / parameter mismatches) are in their own section.
- Tags: `[code]` read from executable code · `[documented]` read from
  comment/docstring only · `[inferred]` deduced.

---

## LAYER A — Substrate loaders / data ingestion

One row per substrate the code can actually ingest. `file:line` is the
loader/generator entry point.

### A.1 Arithmetic / mathematical substrates

| name | layer | file:line | inputs | outputs | what it computes | tag |
|---|---|---|---|---|---|---|
| Riemann ζ zeros (cached) | A | `run_analytical_nns.py:129` (verified) | `zeros_1000.npy` (1000 sorted zeros) | sorted eigenvalue array → passage-time spacings | loads ζ-zero heights for NNS/passage analysis | [code] |
| Riemann ζ zeros (height-convergence) | A | `run_zeta_height_convergence.py` (agent-relayed) | Odlyzko zeros text dump | unfolded spacings binned by height | KS_GUE convergence vs height | [code] |
| Riemann ζ chirp (on-the-fly) | A | `run_zeta_phase2.py` (agent-relayed) | generated chirp signal | chirp → PLL lock events → spacings | synthesises ζ FM signal | [code] |
| EC (elliptic-curve) L-zeros | A | `run_lmfdb_family.py:42` INPUT_FILE (verified), `:113` parse, `:150` PARI `lfunzeros`, `:172` `json.dump` (verified) | `lmfdb_ec_curvedata_0507_1029.txt` → PARI compute | `data/lmfdb_zeros.json` (per-curve zeros + root_number) | computes EC L-function zeros up to height 200 | [code] |
| EC L-zeros (reload) | A | `run_lmfdb_edge.py` / `phase34c/zeros_loaders.py` (agent-relayed) | `data/lmfdb_zeros.json` | conductor-unfolded per-curve zeros | normalized spacings, γ₁ distribution | [code] |
| Dirichlet character L-zeros | A | `run_dirichlet_family.py` (agent-relayed) → `data/dirichlet_zeros.json`; reload `run_dirichlet_edge.py` | PARI on-the-fly (q ≤ 80) | per-character zeros + is_real flag | Dirichlet L-zeros by character type | [code] |
| Mertens M(x) / Liouville L(x) sign-changes | A | `run_mertens_liouville.py:51` `mu_lambda_sieve` (verified), `:86` `find_sign_changes` (verified) | on-the-fly sieve to N=10⁷ | sign-change positions (integer crossings) | μ(n)/λ(n) cumulative-sum zero-crossings | [code] |
| Prime / twin-prime sequence | A | `run_primes_scaling.py` (agent-relayed) | on-the-fly sieve | log-unfolded prime spacings; Fano F(T) | prime-counting + Fano scaling | [code] |
| Almost-Mathieu (AM) spectra | A | `cross_substrate/am_confluence.py` + `phase35a/unfold_rotnum.py:am_eigs` (agent-relayed) | on-the-fly eigensolve (N≈50k, golden θ, λ-sweep) | eigenvalues → poly-unfold → Family I/II | AM operator spectrum at λ | [code] |
| Quasiperiodic operators (Maryland/GAAH/mosaic/ext-Harper) | A | `cross_substrate/quasiperiodic_operators.py` (agent-relayed) | on-the-fly eigensolve | Family I/II + D_box | quasiperiodic Schrödinger spectra | [code] |
| Sturmian Hamiltonian | A | `cross_substrate/sturmian_hamiltonian_run.py` (agent-relayed) | tridiagonal solver, 7 α-classes | `coordinates/sturmian-hamiltonian.jsonl` | Sturmian spectrum (Cantor D_box) | [code] |
| Circle-map / Farey rationals | A | `pll_bank.py:374` `farey_rationals` (verified) | integer `q_max` | list of (p,q) in [1/q_max, q_max] | Farey sequence + reciprocals | [code] |
| Stern-Brocot / brocot approximability | A | `cross_substrate/brocot_approximability.py` (agent-relayed) | 9 Lagrange targets (golden→Liouville) | `coordinates/brocot-approximability.jsonl` | depth-sweep Family I/II | [code] |
| Gold/Silver/Metallic CF ladder | A | `cross_substrate/gold_silver_ladder.py` (agent-relayed) | periodic CF sequences | IDS staircases + DEGT dimension | metallic-mean spectral ladder | [code] |
| Fibonacci / λ* Lagrange classes | A | `cross_substrate/lambda_star_classes.py` (agent-relayed) | 9 Lagrange classes | `coordinates/lambda-star-classes.jsonl` | Fibonacci-class fingerprints | [code] |
| Maass forms Γ₀(N) (SL₂ℤ) | A | `phase34e/maass_loader.py` (agent-relayed) | Seymour-Howell Zenodo `data/maassdata/*.txt` | Hecke eigenvalue pairs (r, level) | Maass-form spectral data | [documented] |
| p-adic engine (v3/v4/finance) | A | `run_padic_v3.py`, `run_padic_v4.py`, `run_padic_finance.py` (agent-relayed) | synthetic (Poisson+period-7) or `financial_settlements.csv` if present | per-band median KS_GUE / RF p-adic profile | p-adic resonance via RF | [code] |

### A.2 Neural / physical / empirical substrates

| name | layer | file:line | inputs | outputs | what it computes | tag |
|---|---|---|---|---|---|---|
| Allen Visual Coding (depth) | A | `cross_substrate/allen_depth.py:54` NWB_GLOB, `:67` `build_targets`, `:97` `extract_train` (verified) | locally-cached `session_*.nwb` via **h5py-direct** (not allensdk) | spike-time trains per (cell,stimulus) | ingests Allen NPx spikes | [code] |
| Allen variants (burst / OSI-gap / avalanche / HPF / Fam2) | A | `cross_substrate/allen_{v1_burst,osi_gap,avalanche,hpf,fam2_analysis}.py` (agent-relayed) | same cached NWBs | spike trains + per-axis features | OSI, burst, avalanche reads | [code] |
| Buzsáki CA1 | A | `cross_substrate/buzsaki_port.py` (+ placefields/swr/thetagamma/selectivity/ratematch) (agent-relayed) | NWB/HDF5 | spike trains | CA1 pyramidal/interneuron port | [code] |
| IBL brain-wide | A | `cross_substrate/ibl_port.py` (agent-relayed) | DANDI 000409 processed NWB | spike trains by region | IBL region-scan ingest | [code] |
| CRCNS hc-3 (EC/CA3/CA1/DG) | A | `cross_substrate/hc3_port.py:109` `parse_session`, `:75` `load_cell_table`, `:55` `load_behavior_map` (verified); fetch `crcns_client.py`/`crcns_fetch.py` | Neuroscope `.res`/`.clu`/`.xml`/`.whl` (20 kHz / 39 Hz) | per-cell spike-time + region + burst stats | Mizuseki/Buzsáki tetrode port | [code] |
| ret-1 retina RGC | A | `cross_substrate/ret1_port.py`, `ret1_rf.py`, `ret1_surrogate.py` (agent-relayed) | Meister white-noise `.mat` via scipy.io | RGC spike trains | retinal feedforward port | [code] |
| ComCat earthquakes | A | `cross_substrate/comcat_port.py:48` `load_catalog` (verified), `:128` `fingerprint`, `:176` `gardner_knopoff`; fetch `comcat_fetch.py` | USGS FDSN CSV catalog | event times → clustering fingerprint | quake NNS + GK-decluster | [code] |
| GOES solar flares | A | `cross_substrate/goes_flares.py:81` `fetch`, `:129` `load` (verified) | HEK API (paged JSON, single-FRM filter) | flare onset event series | flare clustering calibrator | [code] |
| GRB gamma-ray bursts | A | `grb_pipeline.py` (agent-relayed) | Fermi GBM FITS TTE photon times (HEASARC) | photon arrival times | GRB QPO/timing ingest | [code] |
| Fungal electrophysiology | A | `run_fungal_nns.py`, `fungi/` (agent-relayed) | Adamatzky 8-channel voltage CSV | spike/event series | fungal spike NNS | [code] |
| EEG (PhysioNet) | A | `run_eeg_full.py`, `run_eeg_depth.py` (agent-relayed) | EDF (physionet.org motor-movement set) | theta-band zero-crossings | EEG event extraction | [code] |
| Dual-region MEC/CA1/DG | A | `cross_substrate/dual_region_port.py` + `nwb_remote.py` (agent-relayed) | DANDI 000638 NWB via **HTTP-range streaming** (no full DL) | region-tagged spike trains | selective remote MEC extraction | [code] |
| Binance BTCUSDT | A | `run_phase14_binance.py` (agent-relayed) | ms-precision trade CSV | trade event times (buy/sell split) | financial microstructure ingest | [code] |
| Chaotic-map substrates (Lorenz/logistic/Mackey-Glass/Chialvo) | A | `cross_substrate/{lorenz_logistic_run,mackey_glass_run,chialvo_run}.py` (agent-relayed) | on-the-fly ODE/DDE/map integration | event series via extractors | dynamical-systems calibrator substrates | [code] |

### A.3 Cross-domain substrates — present but bounded/stubbed

| name | layer | file:line | status | tag |
|---|---|---|---|---|
| NANOGrav pulsar TOAs | A | `phase33a/` (agent-relayed) | loader entry present; STRUCTURAL_MISMATCH per memory (folded-template aggregate) | [inferred] |
| CERN Open Data (CMS dimuon) | A | `phase33b/` (agent-relayed) | mass-spectrum CSV; instrument-validation-bounded | [code] |
| Bianchi / Z[ω] Picard Maass | A | `phase34f/zomega_loader.py` (agent-relayed) | **STUB** — data-availability gate fired; pipeline VALIDATED_READY_TO_FIRE, no dataset | [documented] |
| Eisenstein / Dedekind zeta | A | — | **could-not-locate a live loader** — referenced in briefs only | [inferred] |

---

## LAYER B — Analysis engines

### B.1 NNS (nearest-neighbour spacing) engine — canonical

| name | layer | file:line | inputs | outputs | what it computes | tag |
|---|---|---|---|---|---|---|
| `compute_nns` | B | `universality.py:95` (verified) | unfolded event array | `NNSResult` (spacings, KS to P/GOE/GUE, p-vals, best_fit) | unit-mean spacings + KS classification | [code] |
| analytical reference CDFs | B | `universality.py:38` `nns_cdf_poisson`, `:42` `nns_cdf_goe`, `:47` `nns_cdf_gue` (verified) | s grid | CDF values | closed-form Poisson/GOE; GUE by trapezoid integration | [code] |
| `_ks_pvalue` | B | `universality.py:80` (verified) | KS stat, n | p-value | asymptotic Kolmogorov p-value | [code] |
| analytical passage-time NNS (ζ-canonical driver) | B | `run_analytical_nns.py:84` `analytical_nns` (verified), `:77` `to_zeta_density`, `:224` `measured_nns` (verified) | eigenvalue list, fc_ref, q_max | pooled per-PLL normalised passage spacings + KS | bypasses chirp/PLL: zero-passage spacings through Farey freqs | [code] |
| PLL measurement stack (instrument) | B | `pll_bank.py:84` `single_pll_cpu`, `:187` `pll_bank_cpu`, `:305` `pll_bank_gpu` (CuPy RawKernel `:235`) (verified) | FM signal, freq list, sr, `PLLParams` | `lock_map[N_pll×N]`, phase_error | quadrature-mix + IIR-LP + 2nd-order PLL lock detection | [code] |
| in-engine direct NNS | B | `arithmetic_toolkit.py:119` `_direct_nns`, `:105` `_classify` (verified) | t_k array | best-fit + KS_{p,o,u} + mass03 | quick sort-diff NNS classify (reused by RF engine) | [code] |

### B.2 Ramanujan-Fourier (RF) engine — canonical (this is where `rf_amp_per_q` is produced)

| name | layer | file:line | inputs | outputs | what it computes | tag |
|---|---|---|---|---|---|---|
| `ramanujan_fourier` (RF engine proper) | B | `arithmetic_toolkit.py:130` (verified) | t_k array, q_max | dict `{amplitudes |a_q|, top10_q, peak_q, a0, mode}` | a_q = (1/φ(q))·E_n[f(n)·c_q(n)]; normalised (interval) OR indicator (period) mode | [code] |
| `ramanujan_sum_array` | B | `arithmetic_toolkit.py:88` (verified) | q, N | c_q(n) array | Ramanujan sum via Hölder identity | [code] |
| `joint_q_profile` ← **produces `rf_amp_per_q`** | B | `arithmetic_toolkit.py:618` (verified); RF amps at `:648`, columns `rf_amplitude_q`/`rf_amplitude_q_normalized` at `:702-708` | t_k array, q_max | pandas DataFrame, one row per q (rf_amplitude_q, ks_gue_q, rep_int_q, F_T1/5, …) | fuses indicator-RF |a_q| with per-q-band Farey passage NNS | [code] |
| `joint_quadrant_diagnostic` | B | `arithmetic_toolkit.py:724` (verified) | joint_q_profile DataFrame | per-q quadrant labels (BL/TR/BR/TL + rf_spike) | Tier-2 calibrator-scatter quadrant assignment | [code] |
| `padic_profile` (RF p-adic) | B | `arithmetic_toolkit.py:300` def, `:327` calls `ramanujan_fourier(normalize=False)` (verified) | t_k, primes, q_max | `{per_prime, dominant_prime, total_power}` | sums |a_q| over q∈{p,p²,…}; per-q-normed to kill small-prime bias | [code] |
| `full_analysis` (5-engine fingerprint) | B | `arithmetic_toolkit.py:557` (verified) | t_k | 10-dim fingerprint dict (NNS + RF peak_q + p-adic + Fano + pair-corr + SB-split) | packs all engines into one fingerprint vector | [code] |
| Family-III RF **consumer** (not producer) | B | `cross_substrate/axes.py:341` `III1_p_concentration`, `:351` `III2_small_prime_vector`, `:362` `compute_family_III_from_rf` (verified) | pre-banked `rf_amp_per_q` vector | RF amplitude at q=p (2,3,5,7) + scalar sum | reads a banked RF vector; does NOT compute the RF spectrum | [code] |

---

## LAYER C — Estimators / statistics

Family **I** = marginal (single-spacing) distribution distances; Family **II** =
long-range correlation statistics. Canonical homes: `cross_substrate/axes.py`
(Family I/II/III axis wrappers) and `universality.py` (raw long-range kernels).

### C.1 Family I — marginal NNS distances (`cross_substrate/axes.py`, all verified)

| name | layer | file:line | inputs | outputs | what it computes | family |
|---|---|---|---|---|---|---|
| `I1_w1_clock` | C | `axes.py:88` | spacings | float | W1δ = E|s−1| (clock distance) | I |
| `I2_w1_gue` | C | `axes.py:96` (helper `_w1_cdf:67`) | spacings | float | 1-Wasserstein to GUE CDF | I |
| `I3_w1_goe` | C | `axes.py:101` | spacings | float | W1 to GOE | I |
| `I4_w1_poisson` | C | `axes.py:106` | spacings | float | W1 to Poisson | I |
| `I5_ks_gue` | C | `axes.py:111` (helper `_ks_cdf:80`) | spacings | float | KS to GUE (matched plain-NNS) | I |
| `I6_ks_clock` | C | `axes.py:118` | spacings | float | KS to δ(s−1) | I |
| `I7_ks_poisson` | C | `axes.py:129` | spacings | float | KS to Poisson | I |
| `I8_brody_q` | C | `axes.py:147` (`brody_pdf:139`, `_brody_b:134`) | spacings | float [0,1] | MLE Brody q (0=Poisson,1=GOE) | I |
| `I9_berry_robnik_rho` | C | `axes.py:163` (calls `phase34e.run_berry_robnik.fit_rho`) | spacings | float | MLE Berry-Robnik ρ (GOE fraction) | I |
| `I10_cv` | C | `axes.py:175` | spacings | float | CV — sign-carrying clustering magnitude (global) | I |
| `I11_mass03` | C | `axes.py:187` | spacings | float | fraction of spacings < 0.3 | I |
| `I12_cv2` | C | `axes.py:215` (`_ordered_intervals:206`) | raw positions | float | Holt CV2 — rate-robust local irregularity | I |
| `I13_lv` | C | `axes.py:227` | raw positions | float | Shinomoto Lv — rate-robust local variation | I |
| `compute_family_I` | C | `axes.py:244` | positions | dict of I.1–I.13 | runs all Family-I axes (+`family_local:237`) | I |
| `canonical_spacings` | C | `axes.py:61` (calls `phase35a.unfold_rotnum.spacings`) | positions | spacing array | 2–98% trim + unit-mean renorm (matched extractor) | I |

### C.2 Family II — long-range (`cross_substrate/axes.py` wrappers + `universality.py` kernels, all verified)

| name | layer | file:line | inputs | outputs | what it computes | family |
|---|---|---|---|---|---|---|
| `II1_sigma2_at_L` | C | `axes.py:277` (`_window_starts:269`, `matched_L:255`) | positions, L | float | number variance Σ²(L), capped searchsorted windows | II |
| `II2_delta3_at_L` | C | `axes.py:293` | positions, L | float | spectral rigidity Δ₃(L) (lstsq staircase residual) | II |
| `II3_K_at_tau` | C | `axes.py:315` | positions, τ | float | spectral form factor K(τ) at fixed τ | II |
| `compute_family_II` | C | `axes.py:327` | positions | dict (II.1/II.2/II.3; II.4 = None unimplemented) | runs Family-II axes | II |
| `number_variance` (kernel) | C | `universality.py:126` (verified) | events | dict {L, sigma2, poisson/goe/gue curves} | Σ²(L) via sliding window (slide_step=0.1) + RMT refs | II |
| `spectral_form_factor` (kernel) | C | `universality.py:173` (verified) | events | dict {t, K} | K(t)=(1/N)|Σ e^{2πi t x}|² | II |
| `pair_correlation` (kernel) | C | `universality.py:194` (verified) | events | dict {r, R2, gue, poisson} | R₂(r) pair-separation histogram vs RMT | II |

### C.3 Family V / VI — dynamical & extraction-meta (`cross_substrate/axes.py`, verified)

| name | layer | file:line | inputs | outputs | what it computes | family |
|---|---|---|---|---|---|---|
| `V1_lyapunov` | C | `axes.py:392` (`_embed:387`, `_embed_lag:377`) | time series | float | largest Lyapunov exp (Rosenstein) — sign-indicator | V |
| `V2_correlation_dim` | C | `axes.py:439` | time series | float | correlation dimension D₂ (Grassberger-Procaccia) | V |
| `VI1_L_iter_alpha` | C | `axes.py:466` | banked loglog α | dict | L_iter convergence rate readout | VI |
| `VI2_N_scaling_beta` | C | `axes.py:477` | N values, spreads | dict {beta, local_slopes} | N-scaling exponent β fit | VI |

---

## LAYER D — Calibrators / falsification harness

`wired` = imported & called by other modules · `standalone` = hand-run script
(`if __name__=='__main__'`, not imported). Wiring re-confirmed by sub-agent grep;
a deeper wiring audit runs separately.

| name | layer | file:line | what it calibrates / falsifies | wired vs standalone | tag |
|---|---|---|---|---|---|
| `calibrator_panel` (zoo) | D | `calibrator_panel.py:59` STATIONARY, `:123` TRANSITION, `:133` EXTENDED | 8 stationary universality classes + transition calibrators | **wired** (imported by `run_phase20_5_distinctness_revalidation.py:51`, `rf_decoy_battery.py:62`, `phase22a/verify_calibrators.py`) | [code] |
| `surrogates` | D | `surrogates.py:50` phase_randomized, `:159` `_fit_hawkes_exponential`, `:373` hawkes_matched_events, `:452` SURROGATES, `:459` generate | phase-randomized / Hawkes / cumulant-matched event surrogates | **wired** (8 sites incl. `topology_hawkes.py`, `run_phase18/20/21_*`, `longrange_discriminator.py`, `tests/test_surrogates.py`) | [code] |
| `transition_diagnostic` | D | `transition_diagnostic.py:357` `characterize_transition`, `:469` `trajectory_from_events`, `:285` `_classify_shape` | quadrant-trajectory transition characterisation | **wired** (≥9 sites incl. `chialvo_calibrate.py`, `phase36/track0_regression.py`, `run_phase20_5/21_*`) | [code] |
| `transition_calibrators_blended` | D | `transition_calibrators_blended.py:313` `gen_blended_transition`, `:375` `enumerate_blended_panel` | blended class-pair × shape transition calibrators | **wired** (`calibrator_panel.py:47`, `run_phase20_5_calibrators.py`, tests) | [code] |
| `transition_calibrators_dynamical` | D | `transition_calibrators_dynamical.py:98` logistic_to_events, `:156` mackey_glass, `:284` lorenz_integrate, `:314` lorenz_lobe_transition_events | logistic/Mackey-Glass/Lorenz dynamical calibrators | **wired** (`calibrator_panel.py:48-49`, `lorenz_logistic_run.py`, `mackey_glass_run.py`, `phase36/`, tests) | [code] |
| `instrument_confound` (apparatus-subtraction) | D | `instrument_confound.py:113` apply_deadtime, `:141` random_thin, `:274` `apparatus_subtracted_comparison`, `:332` estimate_deadtime_floor, `:216` gue_positions | dead-time/thinning/method-perturbation apparatus ledger | **wired** (5 sites: `run_phase18_finding_validation.py`, `hc3_cv2_diagnostic.py`, `hc3_instrument_pass.py`, `rf_decoy_battery.py`, `longrange_discriminator.py`) | [code] |
| `lightcurve_modulated_surrogate` | D | `lightcurve_modulated_surrogate.py:33` empirical_lightcurve, `:63` lightcurve_modulated_poisson | GRB rate-envelope null (inhomogeneous Poisson) | **wired** (4 sites: `run_phase21_falsification.py`, `phase23/*`, `phase26/per_cell_surrogate.py`) | [code] |
| `rf_decoy_battery` | D | `rf_decoy_battery.py:159` calibrate_floor, `:180` run_ground_truth_and_decoy, `:254` run_apparatus_gate | RF a_q floor + order/marginal decoy + apparatus gate | **standalone** (`__main__` at :308; not imported) | [code] |
| `calibration_anchors` | D | `calibration_anchors.py:71` `run`, `:59` `_fingerprint` | 6 canonical-class anchor fingerprints → jsonl | **standalone** (`__main__` at :113) | [code] |
| `soc_synthetic_validate` | D | `soc_synthetic_validate.py:48` inhomogeneous_poisson, `:57` hawkes, `:84` readout, `:111` main | local-rate-unfold known-answer (memory vs envelope) | **standalone** (`__main__` at :137) | [code] |
| `chialvo_calibrate` | D | `chialvo_calibrate.py:120` run_detection, `:159` run_nfp, `:188` run_sensitivity, `:205` run_qmax_guard | torus-breakdown transition + NFP/sensitivity/q_max guard | **standalone** (`__main__` at :280) | [code] |
| `validate_fitters` (→ `fitter_validation.json`) | D | `cross_substrate/validate_fitters.py:64` main (Poisson/GOE ground-truth) | gates Brody-q / Berry-Robnik-ρ banking (§7.ter.57) | **standalone** (`__main__` at :104) | [code] |
| `run_gue_calibration` | D | `run_gue_calibration.py:59` run_cell | does GUE chirp reproduce ζ depth-4 peak? | **standalone** (module-level, not imported) | [code] |
| `run_calibration` | D | `run_calibration.py:213` per_pll_stats, `:244` summarise | instrument GUE-vs-GOE distinguishability + ζ interp | **standalone** (module-level) | [code] |
| `fix_gue_generator` | D | `fix_gue_generator.py` (R=2 semicircle unfold diagnosis); `unfold_empirical` | GUE generator unfolding fix (R=2 vs broken) | **dual** — `__main__` harness + `unfold_empirical` imported by `phase35a/resolution_crossover.py` | [code] |

---

## DRIFT FINDINGS (code vs docs / duplicates / parameter mismatches)

1. **PLL gain mismatch — canonical run ≠ `PLLParams` defaults.**
   `pll_bank.py:66-68` defaults are `K_p=0.10, K_i=0.005, rho=0.95`, but the
   ζ-canonical driver `run_analytical_nns.py:216` instantiates
   `PLLParams(K_p=0.02, K_i=0.001, rho=0.95)`. The "canonical" measurement params
   are the driver's, not the dataclass defaults — a reader trusting the defaults
   would mis-state the instrument. `[code]`
2. **Two Σ²(L) implementations.** `universality.py:126` `number_variance` uses a
   fine sliding window (`slide_step=0.1`, O(N) per L); `axes.py:277`
   `II1_sigma2_at_L` is a re-implementation with capped searchsorted windows
   (`N_WIN_CAP=400`) and matched-L. They are NOT the same estimator — long-range
   results depend on which is used. `[code]`
3. **GUE/GOE number-variance refs recently corrected.** `universality.py:165-167`
   now sets GUE=1/π², GOE=2/π² (HEAD commit `1a6c7a1` "Fix swapped GOE/GUE
   number-variance reference curves"). Any banked Σ²-vs-RMT verdict produced
   before that commit used swapped reference curves — flag for cross-check. `[code]`
4. **RF engine has two callers with opposite `normalize` defaults.**
   `ramanujan_fourier` defaults `normalize=True` (interval mode), but the p-adic
   and `joint_q_profile` paths force `normalize=False` (indicator/period mode)
   (`arithmetic_toolkit.py:327`, `:648`). The "RF amplitude" banked as
   `rf_amp_per_q` is the **indicator-mode** spectrum, not the documented default.
   `[code]`
5. **Family-III is a consumer, not the RF engine.** `cross_substrate/axes.py:341+`
   (`III*`) only *reads* a pre-banked `rf_amp_per_q` vector; the RF spectrum is
   produced upstream in `arithmetic_toolkit.joint_q_profile`. The brief's pointer
   to axes.py for "where rf_amp_per_q is produced" is the consumer site — the
   producer is `arithmetic_toolkit.py:618/648/702`. `[code]`
6. **Duplicate GUE/GOE generators.** `gen_gue`/`gen_goe` appear inline in
   `run_analytical_nns.py:63-74`, again in `fix_gue_generator.py`, and as
   `instrument_confound.gue_positions` (`:216`, tridiagonal Dumitriu-Edelman) —
   at least 3 distinct GUE samplers with different unfolding conventions. Not a
   single canonical generator. `[code/inferred]`

---

## COULD-NOT-LOCATE (not inferred into existence)

- **Eisenstein / Dedekind zeta live loader** — referenced in briefs/memory but no
  `run_*.py` or `cross_substrate/*.py` ingest path was found. (Bianchi/Z[ω] Picard
  loader `phase34f/zomega_loader.py` exists but is a data-blocked STUB.)
- **Exact `fit_rho` / `run_berry_robnik` internals** — `axes.py:51` imports
  `phase34e.run_berry_robnik.fit_rho`; the fitter body lives in a `phase34e/`
  driver and was not line-audited here (out of canonical scope).
- **Per-line re-verification of most Layer A neural/physical and Layer D
  standalone scripts** — citations are sub-agent-relayed; auditor spot-verified
  Allen, hc-3, ComCat, GOES, LMFDB, Mertens entry points only. Remaining rows
  flagged `(agent-relayed)` need re-confirmation if load-bearing.

---

*End of audit/01-tools.md. No files were modified during this audit.*
