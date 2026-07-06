# ARS Math Toolkit — Portable Reference Digest

A hand-off map of the reusable engines, calibrators, substrates, certified math machinery, and
working disciplines across the three sibling repos. Paths are relative to `/home/combust/fmexplorer/`.
Verified against the code (2026-07). One-off `run_phaseNN_*.py` scripts are omitted; only reusable
pieces are listed.

## 0. Orientation

**ARS = Arithmetic Resonance Spectrometer.** It takes a point process (sorted event timestamps — spikes,
zeta zeros, primes, earthquakes, map iterates) and asks two *formally distinct* questions about its
timing texture, plus, for operators, the spacing statistics of a **spectrum**. Firing rate is treated as
a nuisance to be removed; verdicts certify the **marginal** spacing distribution, not a universality
*class* (long-range statistics are needed for that — see §9).

- **Repos:** `criticality_tool/` (the ARS repo, 435 `.py`), `cross_substrate/` (subdir: the substrate
  landscape), `approximability/` (subdir: certified spectral/number-theory machinery),
  `riemann_explorer/` (the host FM/PLV engine, imported on PYTHONPATH), `mathtest/` (clean-room
  reference suite, `refsuite/`).
- **Environment:** run everything with `/home/combust/fmexplorer/bin/python3` (pandas/numpy live in that
  venv; bare `python3` bites post-reboot). Most scripts need
  `PYTHONPATH=/home/combust/fmexplorer/riemann_explorer`. Neural NWB streaming uses the MAIN venv
  (`venv_allen311` numpy is too old for `np.trapezoid`).
- **Seed convention:** `BASE_SEED = 20240517` throughout.

## 1. The two headline engines (`criticality_tool/`)

Both defined in **`arithmetic_toolkit.py`** (812 lines); the NNS reference distributions live in
**`universality.py`**. They are distinct objects, not two views of one engine.

### NNS engine — nearest-neighbour spacing / spacing universality
- **`universality.py`** — canonical RMT reference + level statistics of a **unit-mean-unfolded** point
  process. `nns_poisson/goe/gue(s)` + `..._cdf_...(s)`; `compute_nns(events) -> NNSResult(spacings,
  ks_poisson/goe/gue, p_*, best_fit)` — **origin of `ks_gue`**. Also `number_variance(events, L_max)`
  → Σ²(L) vs analytic curves, `spectral_form_factor`, `pair_correlation`. *Inputs must be pre-unfolded
  to mean spacing 1; Σ² needs ≥50 events, R₂ ≥20.*
- **`arithmetic_toolkit.joint_q_profile(t_k, q_max=200, min_events_per_q=30, fc_ref=1.0) -> DataFrame`**
  — the deployed NNS engine: decomposes the process over **Farey-rational bands**, analytical passage
  times per band, per-q level statistics + indicator-mode `|a_q|`; flags `underpowered` bands. Load-bearing
  outputs `ks_gue_med`, `rep_med`. Carries **dynamics-class** signal (Poisson / Wigner / TR / BR) at the
  recording-aggregate level. Feeds `bulk_recovery`.
- **Band-invariance proposition (§7.ter.10):** any `{filter Farey → analytical passage → unit-mean NNS →
  KS}` engine is invariant under linear time-scaling and **cannot** detect prime-base asymmetry on
  stationary signals. This is *why the RF engine exists* — trying to get per-prime structure out of
  `joint_q_profile` is architecturally impossible.

### RF engine — Ramanujan-Fourier / p-adic
- **`arithmetic_toolkit.ramanujan_fourier(t_k, q_max=200, normalize=True, n_bins=None) -> dict`** —
  `normalize=True`: `a_q = (1/φ(q))·E_n[f(n)·c_q(n)]` on the unit-mean interval sequence (spacing-
  correlation mode). `normalize=False`: **indicator mode** — `f(n)` = event count in integer time-bins,
  detects integer-period structure (weekly=7, etc.). Returns `amplitudes=|a_q|, top10_q, peak_q, mode`.
- **`padic_amplitude_v4(...)`** (+ `padic_profile`, `padic_per_band`) — per-prime arithmetic-class signal:
  aggregates `|a_q|` over q divisible by each tested prime, normalized against total amplitude. v1–v3
  failed acceptance (band-invariance); v4 routes through RF on indicator functions and passed. *Indicator-
  mode `a_q` needs a zoo-CALIBRATED floor (~6, not ~1); it is marginal-dominated and does not escape the
  marginal-vs-class downgrade.*

### The fingerprint
- **`full_analysis(t_k, label='') -> dict`** runs all five engines (NNS, RF, Fano, pair-correlation,
  Stern-Brocot directional split) + returns the **10-dim `fingerprint_vector`**: `[KS_GUE, KS_GOE,
  KS_Poisson, mass<0.3, F(T=1), F(T=5), repulsion_integral, top_ramanujan_q, sb_symmetry_ks,
  padic_dominant_prime]` with `fingerprint_keys`. Helpers: `ramanujan_sum_array(q,N)`, `euler_phi`,
  `mobius`. Needs ≥20 events (≥5 for RF).
- **Scope:** classification runs at **full-sequence** and **per-window** timescales; survival at one does
  not imply the other, and every surrogate-survival claim must state its scope.

## 2. The fingerprint axes — `cross_substrate/axes.py`

Pure axis functions on a substrate's **unfolded positions** (unit-mean; `canonical_spacings()` =
`phase35a.unfold_rotnum.spacings`, 2–98% tail-trim + renorm, identical across substrates). Gates
`MIN_N_NNS=20`, `MIN_N_FIT=50`, `MIN_N_LONGRANGE=200`. N/A returns `None`+reason, never a sentinel.

- **Family I — NNS distances:** `I.1_w1_clock` (W1 to δ(s−1), rigidity); `I.2/3/4_w1_gue/goe/poisson`;
  `I.5_ks_gue` (KS to GUE, the bridging axis); `I.6_ks_clock`, `I.7_ks_poisson`; `I.8_brody_q` (MLE
  Brody q, 0=Poisson→1=Wigner); `I.9_berry_robnik_rho` (GOE fraction); `I.10_cv` (sign-carrying
  clustering: <1 repulsive, >1 clustered); `I.11_mass03` (fraction of spacings <0.3, super-Poisson
  mass, N-robust); `I.12_cv2` (Holt CV2, **rate-robust local** on raw ISIs); `I.13_lv` (Shinomoto Lv,
  rate-robust cross-check).
- **Family II — long-range:** `II.1_sigma2_L` (number variance Σ²(L)), `II.2_delta3_L` (spectral
  rigidity Δ₃), `II.3_K_tau1` (form factor). *These are what NNS cannot fake — the class certifier.*
- **Family III — RF arithmetic:** `III.1_p2/p3/p5/p7` (RF amplitude at q=p), `III.4_scalar_sum`.
- **Family IV — spectral box-dim:** `IV.2_spectral_box_dim` (defined in `sturmian_hamiltonian_run.box_dim`).
- **Family V — dynamical:** `V.1_lyapunov` (Rosenstein λ₁ for data-only; runners override with tangent-
  space Benettin for known-equation substrates), `V.2_correlation_dim` (Grassberger-Procaccia D₂).
- **Family VI — extraction-meta:** `VI.1_L_iter_alpha`, `VI.2_N_scaling_beta`, `VI.3_cross_extraction_var`.
- **Family VII:** inter-leg disagreement `|I.5q − I.5|` (computed at analysis time).

## 3. Point-process generators, calibrators, extractors (`criticality_tool/`)

- **`field_generator.py`** — `generate(class_name, params, n_events, seed) -> t_k` for
  `poisson|wigner_gue/goe/gse|periodic|uniform_jitter`; `generate_mixed(component_specs, …)` superposes
  weighted components (preserves component periodicities, not unit-mean).
- **`signal_gen.py`** — low-level ensembles: `make_beta_ensemble_eigenvalues(n, beta, seed)`,
  `make_gue_eigenvalue_signal`, `make_hardcore_process`, `make_uniform_jitter`,
  `make_poisson_zeta_like`, `make_ginibre_projected`.
- **`calibrator_panel.py`** — named calibrator lists: `STATIONARY_CALIBRATORS` (8),
  `TRANSITION_CALIBRATORS` (6), `EXTENDED_CALIBRATORS`. Each `gen_fn(seed)` → ~400-event unit-mean seq.
  *Distinctness claims must be re-verified on the current panel.*
- **`extractors.py`** — six event→event boundary extractors, `extract(t_k, name)`; registry `EXTRACTORS =
  {direct_events, pll_passage, find_peaks_prominence, derivative_zeros, threshold_crossing,
  modular_bin_events}`; `synthesize_continuous(...)` builds the density trace continuous extractors run
  on. **`boundary_extractor.py`** exposes the two 8/8-reliable ones (`direct_events`, `pll_passage`).
- **`llm_extractors.py`** — attention-based extractors from a stored LLM cascade (`extract_llm(cascade,
  name)`): `residual_norm_peaks` (control → BR_artifact), `attention_*_sink*`, `layer_kl_divergence_events`.
- **`extractor_distinctness.py`** — `distinct_pair(a, b, n_seeds=5, seed_threshold=4)` decides whether
  two extractors are mechanism-distinct (produce disagreeing per-q-band classifications; 4/5 ≈ α=0.05).
- **`transition_calibrators_blended.py`** — `gen_blended_transition(origin, destination, shape, …)` with
  shapes `sharp_step|linear_ramp|sigmoidal|exponential_approach|damped_oscillatory|metastable_middle`
  (n≥10⁴ for stable per-window class).
- **`transition_calibrators_dynamical.py`** — bifurcation-driven event sequences: logistic map (+ swept-r
  period-doubling), **Mackey-Glass** (+ 3 mechanism-distinct extractors), Lorenz (lobe transitions).
  Continuous systems need 3-extractor consensus (Phase-19 discipline).

## 4. Analysis, inverse, apparatus engines (`criticality_tool/`)

- **`bulk_recovery.py`** — recover a class's generative params from a `joint_q_profile` DataFrame with
  bootstrap CIs: `recover_poisson_rate`, `recover_wigner_beta`, `recover_periodic_q`,
  `recover_periodic_jitter`, `recover_uniform_jitter_sigma`, `recover_spectral_decomposition`. `flagged` =
  out-of-domain (profile inconsistent with the class).
- **`transition_diagnostic.py`** — `characterize_transition(trajectory) -> dict` (detects transition
  window, endpoints, shape, metastable state, period-doubling); `trajectory_from_events(...)`.
- **`dfa.py`** — `dfa_hurst(series, scales, order=1) -> {hurst, r2, F, …}` (needs ≥64 samples).
- **`intermittency.py`** — PLL lock-map → point-process pipeline: `analyze_lock_map(lock_map, sr, …) ->
  IntermittencyReport` (dwell sequences, lock-onset events, `fit_power_law_mle` Clauset-Shalizi-Newman,
  Fano curves, unfolded aggregate, Stern-Brocot depth histograms); `fast_sweep_summary(...)` scalar-only
  ~30ms/cell for HDF5 sweeps. CPU-only (the "refine on CPU" half). F<1 = repulsion, F>1 = clustering.
- **`as_topology.py`** — CAIDA AS-graph hop distances (`load_as_graph`, `bfs_distances_from`) for the BGP
  substrate.
- **`cross_substrate/instrument_confound.py`** — **apparatus-subtraction** stage (subtract the instrument
  before classifying the substrate): `apply_deadtime` (dead time → fake GUE), `random_thin` (efficiency
  → fake Poisson), `apparatus_bracket(...)` labels each axis `SUBSTRATE_ROBUST|INDETERMINATE|
  APPARATUS_EXPLAINS|NULL`, `method_perturbation(...)` labels METHOD_INVARIANT vs COVARIANT (only
  invariant axes promote), plus a lensing ledger (`build_lensing_record`, `write_ledger`, `validate`).
  *Invariance means "robust to the manipulations we ran", never "the territory".*
- **`cross_substrate/longrange_discriminator.py`** — separate real GUE from a marginal-matching
  **Wigner-renewal decoy** using Σ²(L)/Δ₃(L): `longrange_stats(positions) -> {L, sigma2, delta3}`,
  `wigner_renewal(n, rng)` (the decoy), unfolding lenses `unfold_empirical(deg=6)` /
  `rate_aware_unfold(bw_mult=20)`, `ks_gue(positions)` (the marginal axis "the decoy fools"). Needs ≥200
  events; unfolding can *manufacture* (over) or *erase* (under) rigidity — degree must be disciplined.

## 5. The substrate zoo — `cross_substrate/` (~25 substrates, 6 families)

Program frame ("operator-IS-substrate"): each system is fingerprinted on its spectral/event side and
placed in the shared GUE↔Poisson↔clock landscape. Central result — **approximability stratification:**
ordering by a Diophantine frequency, the fingerprint sorts by rational-approximability (least-approximable
golden/metallic → GUE-like / higher fractal dim; most-approximable Liouville → clustered/Poisson/lower).
All write `coordinates/<substrate>.jsonl`; verdicts are deferred (flag-don't-interpret).

**Dynamical (Family V):**
- `mackey_glass_run.py` — Mackey-Glass delay ODE `ẋ=βx_τ/(1+x_τⁿ)−γx`, τ-sweep (stable→chaos);
  `mg_lyapunov_benettin` tangent-space λ₁ (validated τ=17→0.005). 3 extractors for VI.3.
- `lorenz_logistic_run.py` — **Lorenz** 3-D flow (ρ-sweep, lobe-transition events, RK4 Benettin) +
  **logistic** map (period-doubling, IEI events, analytic λ=⟨ln|r(1−2x)|⟩).
- `dynamical_breadth.py` — Rössler, Chua, Duffing (flows) + Hénon (map), bifurcation sweeps; λ₁ Benettin,
  D₂ Grassberger-Procaccia; median-upcrossing events.
- `chialvo_run.py` — Chialvo 2-D neuron map, a **torus-breakdown→chaos calibrator** (sweep recovery `a`
  through Neimark-Sacker → Arnold-tongue → breakdown; `ns_locus` analytic onset; `chialvo_lyapunov`
  Benettin). Harness `chialvo_calibrate.py`. **Verdict: NOT-SPECTRALLY-SEPARABLE** (clustering-type
  transition, repulsion-axis-blind).
- Kuramoto: no generator — **harvested** by `harvest.py::harvest_kuramoto` from `data/phase30_results/`.
  *(No kaneko / coupled-map-lattice module exists.)*
- `attractor_analysis.py` — read-only EC-vs-CA3 attractor-topology from banked neural ports (per-cell KS +
  Cliff's-delta, CA1/DG bridge).

**Quasi-periodic operators (symbolic + Schrödinger):**
- `sturmian_run.py` — Sturmian **word** substrate (Beatty-sequence events, 7 Lagrange classes). The word
  does NOT stratify (3-distance-rigid).
- `sturmian_hamiltonian_run.py` — Sturmian **Hamiltonian** (α=golden ⇒ Fibonacci Hamiltonian). Defines the
  shared Family-IV instrument: `sturmian_eigs`, `poly_unfold` (deg-12 IDS unfold), `box_dim`. The
  **spectrum** stratifies where the word didn't (Cantor D_box<1, class-graded).
- `quasiperiodic_operators.py` — `OPERATORS = {maryland (always-PP control), gaah (mobility edge),
  mosaic, ext_harper}`, 9 classes × 6 couplings; approximability↔D_box (gaah ρ=−0.72, ext_harper −0.70).
  `quasiperiodic_deepening.py` refines the two near λ=1.

**AM↔Fibonacci confluence arc:**
- `am_confluence.py` — almost-Mathieu `Vₙ=2λcos(2π(θn+φ))` at θ=golden through self-dual λ=1
  (D_box V-curve bottoms at ≈0.513). `fibonacci_lambda_run.py` — Fibonacci D_box(λ) crosses AM-crit at
  λ≈3.46. `theta_class_correspondence.py`, `lambda_star_classes.py`, `lambda_star_nconv.py`,
  `liouville_nconv.py` — map λ*(class); **e is the discriminator** (μ=2 but unbounded CF): λ* tracks
  approximability continuously, AM-crit D_box is approximability-invariant ~½.

**CF-mechanism discriminators:** `cf_mechanism.py` (Predictor-A gap-CV local boundedness vs Predictor-B
irrationality measure μ; e splits them), `cf_discriminator.py` (hold alphabet {1,2}, vary only
periodicity via `thue_morse`/`fib_word` quotients → the brocot trigger is **boundedness, not
quadraticity**).

**DEGT spectral-dimension:** `trace_map_dimension.py` (proper Fibonacci dimension via periodic-approximant
band structure — see §6.3), `gold_silver_ladder.py` (fills gold↔silver with mixed-digit quadratics; per
member α, Lagrange constant, DEGT `degt_C`; C controlled by Λ, not digit-statistics),
`dimension_theory_check.py` (deprecated box-counting predecessor).

**SOC calibrators (known ground truth):** `comcat_fetch.py` (self-sizing sequential USGS ComCat quake
downloader, dedup, resumable), `comcat_port.py` (fingerprint recovers clustering; Gardner-Knopoff
declustering moves it toward Poisson; irreversibility / Omori-asymmetry gates), `goes_flares.py` (GOES
solar flares via HEK; solar-cycle knob), `soc_synthetic_validate.py` (inhomogeneous-Poisson / Hawkes /
duplicate-contaminate ground truth for the local-rate-unfold discriminator).

**Aggregators/views (not generators):** `harvest.py` (no-recompute harvest of banked NNS → landscape
records: pvc-11, Allen, Kuramoto, NANOGrav pulsar, ζ/Dirichlet/EC L-zeros, Mertens, Liouville, primes,
Maass), `agreement_check.py` (I.5q↔I.5 proxy regressions), `landscape_view.py` / `confluence_view.py`
(figures).

## 6. Certified spectral / number-theory machinery — `approximability/`

Operates on the discrete Schrödinger operator `(Hψ)_n = ψ_{n+1}+ψ_{n-1}+V_nψ_n` with period-q Sturmian
potential `V_n = λ·χ_{[1−p/q,1)}({np/q})`.

### 6.1 Floquet band engine (exact bands, no resolution wall)
- **`floquet_bands(V)`** (`task1_floquet_bank.py`) / **`periodic_edges(V, corner)`** (`depth4/5`,
  `fifth_ladder.py`) — the `2q` band edges (`Δ(E)=±2`) are exactly the eigenvalues of the period-q
  operator under **periodic** (corner +1) and **antiperiodic** (corner −1) BCs; sort, pair → q bands by
  construction; exponentially thin bands arrive as adjacent eigenvalue pairs. Use `sla.eigvalsh(H,
  overwrite_a=True, driver='evr')` (MRRR) — NOT `driver='ev'` (QR saturates cores). CERTIFIED vs frozen
  refsuite golden (k=12 grid resolves 98/144, Floquet gets all 144).
- **`count_eq_q` gate:** a period-q operator has exactly q bands → `nbands==q` is the hard completeness
  gate (the real bank criterion). q=2 corner is degenerate → use exact `W₂=√(λ²+16)−λ`.

### 6.2 CF / convergent / potential / discriminant (`task1_pi_depth5.py`)
- `cf_frac(x, n)` (fractional-part CF), `convergents(a) -> (ps, qs)` (a₀=0 convention),
  `potential(p, q, lam)` = **integer-arithmetic impurity gate** `(n·p mod q) ≥ q−p` (the float form
  `{np/q}≥1−p/q` drops the boundary site and collapses to the free Laplacian — the root-cause bug),
  asserting `int(round(V.sum()/lam))==p`; `disc_direct(E, p, q, lam)` (ground-truth O(q) transfer-matrix
  discriminant). **Gates:** potential-layer impurity-count assert + **two-precision CF** (bank only where
  dps=50 and dps=80 agree). **CONDEMNED:** `disc_fast` (Chebyshev trace-map recursion) computes a
  *different* operator (0/q at band midpoints) — quarantined, do not reuse.

### 6.3 Dimension estimators
- `bs_dim(bands, q) = ln q / ln(1/mean_width)` — band-scaling, the certified bank readout (single-level,
  scale-dependent → read the depth *trajectory*).
- `box_dim(bands, e0, e1, n=12)` — box-counting; **rails/saturates on multifractal spectra** (resolution-
  limited), so the "estimators agree ≤0.02" flag is a diagnostic, not a bank gate.
- `trace_map_dimension.py`: `dim_pressure(widths)` (Bowen `Σ|w|^d=1`, **scale-dependent — the `--sweep`
  path, avoid**) vs `dim_growth(alpha, lam, q_targets)` (**correct, scale-invariant** thermodynamic
  growth rate, the `--degt` path). DEGT constant `C = dim·lnλ` as **λ→∞ extrapolation of λ≥16 points**
  (golden → 0.877 vs `ln(1+√2)=0.88137`). Spectra are not dimension-regular in general (Hausdorff≠box,
  Liu-Peyrière-Wen 2007) — validate scale-convergence before trusting any asymptotic constant.

### 6.4 Number-theoretic constants (`thread3_constants.py`, `panel_A_*.py`) — all closed
- **Lévy 𝓛** = (1/period)·log(dominant eigenvalue of CF period matrix). gold=log φ=0.48121, silver=
  log(1+√2)=0.88137, bronze=1.19476. a.e. Lévy-Khinchin `π²/(12ln2)=1.18657` (dps=160 MC).
- **Lagrange Λ** = cyclic `max_i (aᵢ + [0;overline{…}] + [0;overline{…}])`; metallic Λ=√(n²+4).
- **dim E₂** (Hausdorff dim of CF-digits ∈{1,2}) — two independent routes (Chebyshev-Nyström transfer
  operator + periodic-orbit dynamical determinant) → Jenkinson-Pollicott `0.531280506277205…` to 3e-17.
- **Liu-Wen liminf-K** — `K(α)=liminf_k(a₁···a_k)^{1/k}`; theorem (Liu-Wen 2004, V>20): `dim_H σ<1 ⟺
  liminf K<∞`. Exact for metallics (=a) and e (→∞, provable); empirical-but-unproven for π.

### 6.5 Thouless per-step bandwidth law (`thouless_law.py`, `thouless_predictions.py`)
Total bandwidth `W_k = Σ band widths` per convergent step. Three faces: (1) `W_k ≈ 4/λ^{m_k}`,
`m_k=#{a_j≥2}`; (2) per-step factor `W_{k-1}/W_k → λ·g(a)`, g↑1 saturating by a=5 (g: golden a=1→0.313,
silver a=2→0.638, bronze a=3→0.918); (3) a=1 step governed by older-block fraction `q_{k-2}/q_k`.
`floquet_bands_tw(V) -> (q, tw)`, `metallic_convergents(m, K)`. λ=8 fully resolved; λ=24/32 hit the
narrow-band wall past q~1600–4000.

## 7. Reference / validation suite — `mathtest/refsuite/`

Clean-room, literature-only reimplementation (SPEC v2), built in isolation to be diffed against analysis
code it never sees. Every closed form has a citation + an independent computational route; gate failures
are recorded as data (`gate_failed=true`), never tuned away. Infra: `schema.py` (`Row`/`Table`, seeded
RNG, loud asserts).

- **Part I** (`partI/theory.py`, `ensembles.py`, `unfolding.py`, `statistics.py`) — spacing surmises:
  `nns_pdf/cv/p0`, `sigma2(L, ensemble)`, `delta3(L)`; Poisson/GOE/GUE spectra; analytic + polynomial
  unfolding; ordering gate Poisson>GOE>GUE (597 rows).
- **D1** (`d1_fibonacci.py`) — Fibonacci Hamiltonian: `fibonacci_word(k)`, `discriminant(E,k,lam)` +
  independent `direct_discriminant`, `find_bands_nested`, `box_count_dimension`, `band_scaling_dimension`
  (two estimators that must agree; 36 rows).
- **D2** (`d2_cf.py`) — CF + Gauss-Kuzmin: `cf_from_fraction/_mpf`, `cf_two_precision`, `gk_pmf/gk_tail`,
  `running_geomean` (Khinchin), `record_process`; e/metallic/Liouville CFs (650 rows).
- **D3** (`d3_farey.py`) — Farey gaps: `triangle_cdf(tau0)` global gap law, `enumerate_window`
  (Stern-Brocot), verifies `p′q−pq′=1` (110 rows).
- **`reference_table.csv`/`.json`** — 1393 rows, one per `(module, statistic, source, parameter)` with
  `theory_value | sample_value ± se | seed | asymptotic_regime | outside_proven_regime | gate_failed` —
  the machine-comparable deliverable.

## 8. Host FM engine — `riemann_explorer/`

The pre-existing Arnold-tongue / FM-coherence scanner (imported on PYTHONPATH by nearly everything; the
approximability machinery uses it mostly for path/env). Coherence metric = inter-sideband **PLV** (phase-
locking value) of an FM signal's Bessel sidebands, aggregated over a Farey pair list, correlated against
Riemann zeta-zero heights. `scanner.py` (`ScanParams`, `scan(signal, params)` → GPU CuPy/PyTorch or CPU
joblib, `ZETA_ZEROS`, `GENERATORS`), `sweeper.py` (multi-scan sweeps), `server.py` (FastAPI WebSocket
browser explorer). *ARS is an applied implementation; the analytical content (Farey PLL frequencies,
Ramanujan-Fourier, Mangoldt / Bost-Connes) is not original to this codebase.*

## 9. Cross-cutting disciplines ("the protocol is the product")

The durable methodology — apply these regardless of substrate:

- **Marginal ≠ class.** NNS/`ks_gue` certifies only the *marginal* spacing. A universality **class** needs
  long-range Σ²/Δ₃ (the Wigner-renewal decoy has GUE marginals but wrong rigidity). Pole tests are
  ABSOLUTE, not ordinal.
- **RF (Family III) and Family II are independent probes only off the flat corner.** The RF power spectrum
  `{a_q²}` is Wiener–Khinchin dual (Gadiyar–Padma; `R(h)=Σ_q a_q² c_q(h)`, verified) to the *raw integer-lag*
  autocorrelation of the event indicator; Family II reads the *unfolded* (unit-rate) spacing. **These coincide at
  constant event rate and diverge only for variable-rate substrates.** Demonstrated on primes: Family II reads them
  Poisson (Gallagher) while RF carries the even-q Hardy–Littlewood singular series — same object, provably disjoint
  readings. Consequence: running both engines is **redundant on flat/dynamical calibrators and informative only on
  variable-rate arithmetic substrates** (primes, ζ/L-zeros). Check rate-constancy before spending a second engine.
  (`rf_lenses/threadA_*`.)
- **A probe's validity domain is substrate-dependent; out-of-domain is a finding, not a reading.** Density-unfolding
  statistics (Family II Σ²/Δ₃) require a local mean spacing to unfold to. A singular/Cantor density — e.g. a
  quasicrystal spectrum where the top few gaps hold most of the span — has none, so the reading becomes a *free
  parameter of the unfold* (diatonic crystal: Σ²/L 56→0→>1000 across unfold choice). Bank this as a **domain
  boundary — no value**, never as an ambiguous rigidity. The substrate is still readable, just on a different
  observable (here Family IV fractal band-dimension). Same category as running a spacing statistic on an object with
  no unit rate. (`rf_lenses/threadE_*`.)
- **Record/Farey agreement is record-conditional — NOT independent joint confirmation.** The CF **record process is a
  running-maximum filter by construction** — it can only register a partial quotient that is a *new record*; the
  **Farey aperture** registers *every* large quotient. So `{record-visible cusps} ⊆ {Farey-visible cusps}`
  definitionally: the record channel is a **maxima-filtered shadow** of the Farey channel, not a second view. When
  "the record process and the Farey aperture *both* flag cusp X," that is **one complete view (Farey) + its shadow
  (record)** — they *must* agree on records and carry **no independent weight** there; never count it as two arithmetic
  faces agreeing. Genuine cross-face independence comes from *dimension* (spectral) vs an arithmetic face, not
  record-vs-Farey. This retro-scopes any banked "record + Farey both registered X" reading (e.g. the Session-B fifth
  Λ-cusp) to one-view-plus-shadow — a lens to apply when those results are next touched, **not** a re-run trigger.
  The three-tier reach nesting `eigensolve ⊆ record ⊆ Farey` follows: record⊆Farey is definitional; the eigensolve
  tier is reach-limited (q ≤ spectral frontier) and independent of the filter relationship.
  (`approximability/fifth_cusp_map.*`.)
- **Support-set-respecting nulls.** A surrogate must respect the point process's support set (squarefrees,
  primes, the S¹ unit-orbit quotient). Full-N required for bulk readout on angle substrates — stride-
  decimation destroys prime-angle structure.
- **The right null is substrate-specific.** Structural null depends on the generative mechanism (support /
  random-walk / unfolding). Self-derived rate-unfold is structurally circular — use an external rate.
- **Apparatus before substrate.** Run `instrument_confound`: dead-time fakes GUE, finite efficiency fakes
  Poisson. Only METHOD_INVARIANT axes promote to substrate candidates; the ledger claims robustness to the
  manipulations run, never universality.
- **Synthetic-validate every fitter** against known ground truth (Poisson→ρ≈0, GOE→ρ≈1) before reporting
  fitted params as absolute. (A Berry-Robnik fitter bug was caught this way.)
- **Within-substrate before pooled.** Test any X↔Y within each substrate before claiming a covariate Z
  gates it — pooled multi-substrate data manufactures Simpson's-paradox covariate-dependence. Per-cell
  `ks_gue↔burst` coupling is substrate-relative (~0.8 hc-3 to ~0 Allen), NOT universal.
- **Cross-substrate validity bridge.** Splicing region-A(sub-1) vs region-B(sub-2): measure a SHARED
  anchor region in BOTH; if the anchor δ≈max the contrast is recording-context, not biology. Carry every
  interesting axis but label its comparison-validity scope.
- **Rate-regime dependence.** Rate-match cells before cross-substrate/time comparison; the surrogate floor
  must match analysis resolution.
- **Observable choice is per-axis.** In coupled-oscillator work: clustering axis wants pooled-temporal,
  repulsion axis wants snapshot (pooled-temporal superposition contaminates it). Pooling rhythmic emitters
  manufactures sub-Poisson regularity → false BR — wants matched-snapshot re-read.
- **Layer-zero gates first.** Print/assert the operator's integer invariant (impurity count == p),
  two-precision agreement, `count_eq_q`, `p′q−pq′=1`. Three prior Task-1 failures were layer-zero (did the
  operator even exist), not pipeline.
- **Discriminant exact-question check.** Before any verdict gate: "exact substantive question or heuristic
  proxy?" Decompose a confound with a *designed* instance (hold one property fixed, flip the other — e.g.
  the {1,2}-alphabet periodicity discriminator).
- **Validate scale-convergence before an asymptotic constant.** Quick estimators can look right at moderate
  scales yet be wrong asymptotically; forms are verifiable, constants need the right formalism.
- **Report honestly.** Gate failure is a deliverable — don't retune post-hoc until it passes. When an
  auto-gate reproduces only part of a claim, the output string must name which part. Seed-replicate near a
  TR/BL boundary (report the distribution, not one quadrant). Scope every claim (full-sequence vs
  per-window; depth-scoped for CF tails). Recompute is never categorically forbidden — bank the raw object
  so it isn't paid twice.
- **Ops:** GPU for wide parameter-matrix sweeps, CPU for precise refinement; local 5900x streaming/large-
  array work peaks ~10 threads. Never `xargs -P` / overlapping curls on shared paths (corruption) —
  sequential + size-verify.

## 10. Condemned paths & known gotchas

- `disc_fast` (trace-map recursion) — computes the wrong operator; quarantined.
- `dim_pressure` / `--sweep` single-level dimension — scale-dependent, fails its own gate; use
  `dim_growth` / `--degt`.
- Float potential boundary (`{np/q}≥1−p/q`) — collapses to free Laplacian; use integer `(np mod q)≥q−p`.
- `box_dim` rails on multifractal spectra (resolution-limited) — diagnostic only, bank on `bs_dim`.
- Floquet corner degenerate at q=2 — use the exact period-2 discriminant.
- `driver='ev'` (QR) saturates cores at large q — use `driver='evr'` (MRRR).
- Bare `python3` lacks pandas — use `/home/combust/fmexplorer/bin/python3`.
