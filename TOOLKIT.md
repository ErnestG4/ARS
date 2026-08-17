# ARS Math Toolkit — Portable Reference Digest

A hand-off map of the reusable engines, calibrators, substrates, certified math machinery, and
working disciplines across the three sibling repos. Paths are relative to `$HOME/fmexplorer/`.
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
- **Environment:** run everything with `$HOME/fmexplorer/bin/python3` (pandas/numpy live in that
  venv; bare `python3` bites post-reboot). Most scripts need
  `PYTHONPATH=$HOME/fmexplorer/riemann_explorer`. Neural NWB streaming uses the MAIN venv
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

- **`calibrator_panel.py` carries the epistemic-tier schema and the 2D calibrators**
  (comb arc, 2026-08-15): `CALIBRATOR_TIERS` (theorem-backed / conjecture-backed-computable /
  construction-defined — the tier of a calibrator's GROUND TRUTH; `zeta_first_400` is
  conjecture-backed, Montgomery), `assert_sole_anchor_allowed(name, claim_tier)` (gate hook,
  RAISES when a non-theorem calibrator would solely anchor a theorem-tier claim), and
  `CALIBRATORS_2D` = {`poisson2d`, `ginibre2d` (theorem-backed; bridge sampler),
  `gp_comb` (conjecture-backed; ℤ[i] HL comb, validated at TWO DISJOINT norm bands
  [9·10⁶, 1.296·10⁷] and [3.6·10⁷, 5.184·10⁷] — the gap between them is UNMEASURED —
  `comb/RESULTS_COMB.md`; deterministic, seed ignored)}. Register a tier with every new
  calibrator; an import-time self-check rejects untiered entries.
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
- **Locate every claim against BOTH references: the noise floor AND the triviality ceiling.** A permutation-null
  is a *floor*; a baseline B is a *ceiling*. Each guard **alone manufactures the other's false positive**. The two
  arms:

  **(a) Floor arm — "R adds structure beyond B" needs B, not a shuffle.** Any rich report beats a label-shuffle
  null whenever it carries *any* signal — including signal a trivial baseline already has; "R beats the null"
  ⇏ "R adds structure." Same error as richness-re-encoding-the-obvious reading as discovery. The correct control
  is the **baseline B itself, run head-to-head in the same cells**, PLUS the report stripped of its baseline-
  overlapping features (B-orthogonalized R). Choose a *strong* trivial B on purpose (rigidity scalar / density-
  variation / spectral-type). (Part C refusal-zoo: R beat the perm-null by +0.458 in 100% of cells → looked
  POSITIVE; the B-within-cell control 0.861 > R 0.826 and the B-orthogonalized-R loss gave the true NULL →
  dark-appendix. `sessionK/partC_*`.)

  **(b) Ceiling arm — "R is orthogonal to B" needs reliability(R), not a low R².** Attenuation gives
  `r_obs = r_true·√(ρ_R·ρ_B)`, hence the hard inequality **`R²(R,B) ≤ ρ(R)` for any B whatsoever**.
  *Decorrelation is the signature of unreliability*: an unreliable axis is orthogonal to everything, including
  the truth. So a low R² against B is not evidence of a novel axis — it is the expected reading of a noisy one.
  You cannot see R's relationship to anything more clearly than the instrument sees R agreeing with itself; the
  instrument's self-consistency is a hard ceiling on every relational claim about the substrate. This equally
  voids **`ρ≈0` "INDEPENDENT_AXES"** readings: unreliability attenuates every correlation toward zero.

  **The admissibility gate (standing, mandatory) — a CONJUNCTION over two independent legs.** No ORTHOGONAL /
  INDEPENDENT verdict on an *empirical per-unit axis* unless **both** legs pass. Either leg failing → the verdict
  is **INDETERMINATE** — not orthogonal, and *not* subsumed.

  - **Leg 1 — reliability.** A **banked split-half reliability** clearing the verdict's own threshold: for
    threshold `τ` and observed `R²_obs`, true orthogonality requires `ρ(R) > R²_obs/τ`.
  - **Leg 2 — the unfold is not self-rate-circular on that substrate.** An unfold that divides by a *self-derived*
    rate (per-call mean spacing) — or that silently decimates — corrupts `R²` **independently of ρ**. This leg is
    not implied by Leg 1 and cannot be inferred from it.

  **Why the conjunction, not one gate (this is a correction, not an addendum).** The one-gate rule was
  *under-specified*: Phase 38 §6 found **two independent reasons** 32b's `BOTH_ORTHOGONAL` fails, and only the
  first is reliability. The second is the unfold: `unfold_unit_mean` divides by a per-call mean spacing
  (self-derived rate — the circularity §9 already names as a *null-choice* rule) and stride-decimates above
  `JPF_CAP = 5000`. Under the frozen unfold with decimation disabled, `ks_gue_med ~ FA-drift` moves from a banked
  `R²` of **0.126 → 0.238**, carrying **`R²_true = 0.243 > τ`** (τ=0.20, true scale) — *"for reasons that have
  nothing to do with reliability at all."* ρ was never implicated. So self-rate-circularity is not merely a null-
  choice hygiene rule; it is a **second, independent leg of the orthogonality verdict itself**, and it must be
  checked at the verdict, not assumed away by a clean ρ. (`phase38/PHASE38_FINDINGS.md` §6.)

  **Disattenuation raises the lower bound; it cannot certify the upper.** `R²_true = R²_obs/ρ` divides by a small,
  imprecisely-estimated ρ — the textbook instability of correction-for-attenuation, worst exactly where ρ is
  smallest and least certain. The correction robustly *kills* orthogonality (it clears τ across the whole plausible
  ρ-band) but can never *establish* subsumption (that needs the true value pinned, and it is not). **Bank
  INDETERMINATE flat.** Correcting an overclaim into its mirror is the failure this doctrine is most primed to
  commit, because it feels like rigour. Resolve the direction by *repairing the instrument* (raise ρ — e.g. more
  surrogates) and re-measuring, never by dividing by a small ρ.

  **(c) Skepticism is not a free action — the trigger fires or it doesn't; partial satisfaction is UNRESOLVED.**
  The same machinery that launders a *win* also launders a *retraction*. Declaring "instrument artifact, retract"
  on inconclusive data is the identical over-satisfying move as accepting the pretty positive — just wearing
  skepticism's coat. A discipline whose failure modes all point toward "retract" / "null" is **not calibrated, it
  is biased** in the direction that feels safe. This is the four-state verdict (ADMISSIBLE / NOT-ORTHOGONAL /
  SUBSUMED-CERTIFIED / INDETERMINATE) lifted from the *axis* to the *gate*: a pre-registered trigger that is only
  partly satisfied returns UNRESOLVED, never a pole. **Design rule (sits next to "specify the demoted form before
  the source is read"): build a pre-registered trigger as a CONJUNCTION over independent legs**, so that partial
  satisfaction routes to UNRESOLVED rather than to either pole. A disjunction — or a single-leg "no structure →
  retract" — would fire on partial evidence and bank a false negative on a real effect. (Exhibit — Phase 35a φ
  contamination close: demoted-form trigger = "no per-α N-structure **AND** smooth approximability gradient →
  retract." Result had the first leg, not the second → **NOT retracted**, held UNRESOLVED, even though retracting
  matched the pre-committed lean. A disjunctive trigger would have retracted a possibly-real α-arithmetic effect.
  `phase38/PHI_CONTAMINATION_PREREG.md`.)

  **(c-companion) UNRESOLVED must be a waypoint, never a berth — the load-bearing correction to (c).** Arm (c)
  opens a safe harbor (partial satisfaction routes to UNRESOLVED rather than a pole). The exploit it opens is that
  **the harbor becomes a permanent hedge**: an UNRESOLVED that names nothing is unfalsifiable, costs nothing, and
  can be re-declared forever — indefinite deferral laundered as rigour. That is *precisely* the (c) failure one
  level up: skepticism is not a free action, and **neither is suspending judgement**. So UNRESOLVED is only a
  verdict if it ships with both:
  1. **The named gap** — the specific reason the trigger was only partly satisfied (which leg failed, and why).
  2. **The named closer** — the specific, pre-registered measurement that would resolve it, with its instrument
     fixed in advance (so the closer cannot be quietly re-specified into reach).

  An UNRESOLVED lacking either is not a verdict; it is an evasion, and should be forced to a pole or to an
  explicit "abandoned — not worth the closer."

  *Self-test, already passed (the worked example is the exhibit above).* The Phase-35a φ contamination close
  banks **INCONCLUSIVE at accessible scale — neither retracted nor vindicated**, and it is admissible under this
  clause because it names both: **gap** = the finite-L `unfold_rotnum` W1δ proxy cannot reach the `N=F₂₄=46368`
  regime where the real under-resolved window lives (the accessible-N proxy has none, and its own numerical
  degeneracy is documented — 0.0000 floor at L≤300, spurious uniform 0.333 at L≈1.5N); **closer** = reproduce
  `aa33e44`'s exact §4/C2 contamination-ratio machinery at `N=F₂₄` on the α-ladder (φ@F₂₄, √2@Pell-near 33461,
  e@non-convergent as the clean dark null), **reproducing the ratio definition exactly — no re-proxy**. Note the
  instrument is pinned *in the closer itself*: the temptation under fatigue is not to run it badly but to
  re-proxy "just to check," which silently swaps the instrument at the one N where instrument identity *is* the
  experiment. A closer that does not pin its instrument is not a closer. (`phase38/PHI_CONTAMINATION_PREREG.md`.)

  **(e) Instruments launder nulls too — an estimator whose support boundary coincides with the null value cannot
  discriminate the null.** Arms (b)/(c) govern *gates*: reliability laundering a relational claim, triggers
  laundering a retraction. **(e) governs the instrument underneath them.** The gate can be perfectly designed,
  pre-registered, conjunctive — and still read zero, because the *estimator* cannot represent the alternative.

  **Corollary (this is the one that fires in practice): a flat null against a censored estimator is uninterpretable
  in the direction of the censoring — it is exactly what saturation looks like.** Everything past the boundary is
  mapped *onto* the null, so "we measured the null" and "we measured far past the null" return the same number.
  Absence-of-effect and maximal-effect are the same reading. No amount of statistical care downstream recovers the
  distinction; the information was destroyed at the estimator.

  **Exhibit 1 — `I_rep`, the repulsion integral (`arithmetic_toolkit.py:507`).**
  `I_rep = trapezoid(np.maximum(0, 1 − R₂), r)` — the clip makes the negative branch **unreachable**, while its own
  docstring (line 494) advertises *"negative → clustering."* The floor sits **exactly at the Poisson value**
  (R₂≡1 ⟹ integrand≡0). So **all clustering is mapped onto Poisson** — and the quadrant classifier (line 789) then
  reads `rep < 0.10 → BL`, whose docstring (line 734) names that class **"Poisson noise."** `BL` is a **collapse
  class named after one of the two things it collapses.** Confirmed against ground truth *we ourselves banked*:
  GOES solar flares — a known-clustered SOC process, established as clustered in our own SOC phase, which even
  recorded *"one-sided fitters blind to super-Poisson"* — read **`rep_int_q` = 0.000 → BL → "Poisson noise."**
  Exactly 0.000 is the floor, not a measurement. Two facts sat in this repo un-collided.
  **Exhibits 2-4 — `I8_brody_q`, `I9_berry_robnik_rho` (`cross_substrate/axes.py:147,163`), `bulk_recovery.py:196`.**
  Brody `q=0` **is** Poisson *and* is the `bounds=(0.0, 1.0)` search floor; clustered data wants `q<0` and **rails**.
  Measured: Poisson → q=**0.0023**; a **CV=6.5** burst process → q=**0.0001**. **The clustered process reads *more
  Poisson than Poisson***, because real Poisson's sampling noise lets q wander off the bound while clustered data
  slams into it. **The rail is tighter than the null — the estimator is not blind there, it is anti-informative.**
  Berry-Robnik compounds it: **every bootstrap replicate rails too, so the CI collapses** and the clustered case is
  reported as Poisson **~45× more confidently than actual Poisson data**. *The rail makes the wrong answer look
  precise.* `bulk_recovery.py` delivers the same bug via `np.interp` **clamping onto a knot its own comment labels
  "(Poisson regime)"** — every clustered band returns the Poisson σ. **Five instances. It is a class.**

  **Sign-blind ≠ null-collapsing — do not lump them (this is *why* it survived).** `ks_poisson` returns **nonzero**
  on clustered data: it is *sign-blind* (flags "not Poisson", no direction). Brody/BR return **the Poisson value
  itself**: *null-collapsing*. `axes.py:178` lumps them (*"KS/W1/Brody axes are sign-blind across the Poisson
  pivot"*), which made "add CV as a companion axis" look like sufficient mitigation while the estimator was
  reporting a **false null**. A companion axis rescues sign-blindness; **nothing downstream rescues a false null.**

  **THE VALIDATION GATE CANNOT CATCH THIS BY CONSTRUCTION — probing only at the rails cannot detect railing.**
  §7.ter.57's mandatory harness (`cross_substrate/validate_fitters.py`) shipped `CASES = [poisson→0, goe→1]` —
  **exactly the two endpoints of the fitters' own `bounds=(0,1)`**. It **PASSED**, and called itself *"MANDATORY
  before any fitted value is banked."* **A validation suite must include at least one case whose true value lies
  OUTSIDE the fitter's reachable range.** (Repaired: `clustered`/`clustered_extreme`, super-Poisson, `q_true<0`;
  the gate now correctly **FAILS**. A FAIL there is the gate working.) **§7.ter.57 is hereby amended — the old rule
  was not merely incomplete, it named the blind probes.**

  **Standing sweep (mandatory on any new estimator).** Grep for `np.maximum(0,`, `np.clip(`, `abs()`/`**2` applied
  to a **signed** quantity, bounded MLEs (`bounds=(0,·)`), `np.interp` **clamping onto a reference knot**, and any
  one-sided fitter. For each: compare the implementation's **reachable range** to the **docstring's claimed range**
  (same class as `phase24/loader.py:49` — a docstring advertising a capability the code does not have), and **flag
  every case where the boundary of the reachable range is a null/reference value** — **then check whether the
  fitter's own validation suite probes anywhere except that boundary.** A clip on a genuinely-non-negative quantity
  (a variance, a count, a KS statistic) is fine — say so and move on. The lethal case is *floor == null*.
  **The correct design pattern, for contrast:** `sessionK`'s `r̃ = min/max` is bounded [0,1] **but its Poisson null
  (0.386) sits in the INTERIOR** — which is exactly why ⟨r̃⟩ is the trustworthy discriminant. `I10_cv`, `I11_mass03`,
  `I12_cv2`, `I13_lv` likewise (nulls 1.0, 0.259, 1.0, 1.0 — all interior). **Put the null in the interior.**

  **THE DISPERSION CLAUSE — read the rail, don't only fix it. At a rail, the CONFIDENCE INTERVAL is the signal and
  the POINT ESTIMATE is noise.** A railed estimator's *dispersion* is informative even when its *location* is not:
  **railed point estimate + collapsed CI ⇒ the data is pinned OUTSIDE the reachable range ⇒ detection**; near-rail
  point estimate + **wide** CI ⇒ sampling noise around a genuine null. **This is what makes (e) survivable rather
  than merely fatal** — the bug becomes the instrument. Validated on ground truth, and note the shortcut it kills:
  the *point estimate alone cannot do it* (**true Poisson rails ~40% of the time**, stable over n=200–2000), but
  **among railed cells the bootstrap sd separates PERFECTLY** — Poisson `boot_sd` median 0.0045, **always > 0**;
  clustered (σ=1.15 *and* 1.8) `boot_sd` **exactly 0.00000, 40/40**. Zero overlap. It even catches **mild**
  clustering that `I_rep`'s zero-floor misses entirely: **the rescued instrument is strictly more sensitive than the
  one it rescues.** Corollary (free, no bootstrap): since `P(rail | true Poisson) ≈ 0.40` is *measured*, **excess
  railing is a binomial test on banked scalars**. Result: **72.5% of the zoo's 20,801 `brody_q` values are railed**,
  and **every neural substrate rejects Poisson** (allen-hpf-cell 4325/4326, buzsaki 99.4%, pvc-11 99.4%, hc3 94.8%,
  ibl 86.7%, ret1 85.5% — all p < 1e-64, robust even at a mis-specified P0 = 0.99). They had all been sitting in the
  Poisson bin. The arithmetic substrates rail *below* chance (`brocot.fm` 4.8%) and are fine — **the damage is
  concentrated exactly where clustering is the substrate's expected state. The instrument failed where the biology
  lives.** (`phase32b/RAIL_AS_DETECTOR.md`.)

  **(e) HAS TWO FACES — name the second or it gets rediscovered.** *Face 1: a censored instrument launders a NULL*
  (the `I_rep` flat null). *Face 2: a censored instrument MANUFACTURES A CONFIRMATION* —
  `phase36/falsification_calibrator.py:140,164` reads the repulsion axis's **silence** on the clustered side as a
  **confirmed prediction** (*"ALL BL: near-Poisson transition INVISIBLE to both (taxonomy holds)"*), when the axis
  is **constructed unable to leave BL there**. Same disease, opposite sign — **and the confirming direction is the
  one nobody audits.** Arm (c) says a *gate* can launder a null; (e) says an *instrument* can launder a null **and
  forge a confirmation**.

  **The validation lesson in its strongest form (belongs beside (c)'s conjunction rule — same shape).** Not "add a
  case outside the range," but: **probing at the endpoints of an instrument's reachable range cannot detect that the
  range IS the bug. A gate built from the instrument's own vocabulary is a tautology with a PASS attached.**
  `validate_fitters.py` was **structurally incapable of failing** — and it said **MANDATORY**. A test whose failure
  mode is unreachable by construction is not a test.

  **(e) ROOT CAUSE — EIGHT DEFECTS, ONE GENERATING ASSUMPTION. Do not file them as eight entries.**

  > **An instrument built and validated against a calibrator set that EXCLUDES a region will accumulate
  > defects that are individually invisible and JOINTLY FATAL in exactly that region. THE DEFECTS WILL BE
  > INDIVIDUALLY DEFENSIBLE — each is *correct behaviour inside the corridor* — which is why they survive
  > review, and why fixing them ONE AT A TIME DOES NOT STOP THE NEXT ONE.**

  *That clause is the one that explains how eight of them shipped past a project with this much
  falsification discipline: **none of them was a mistake.** `s < 10.0` is a sensible outlier trim.
  `bounds=(0,1)` is a sensible Brody range. `np.maximum(0, ·)` is a sensible non-negativity constraint.
  A global unit-mean is a sensible normaliser. **Every one is defensible in isolation, and every one is a
  censoring at the boundary of a region the calibrators never visited.** Review cannot catch this, because
  review examines defects one at a time — which is exactly the frame in which each one is correct.*

  The zoo shipped GOE / GUE / GSE / periodic / mixed / jitter / ζ / Poisson — and **no clustered class at
  all.** Poisson was the most-clustered object in it. That single gap was not one hole; **it was a licence**
  for every one of these, each of which is *harmless inside the corridor and destructive outside it*:
  `I_rep`'s `np.maximum(0,·)` clip · Brody's `bounds=(0,1)` (**both** ends) · Berry-Robnik's collapsing CI ·
  `bulk_recovery`'s `np.interp` clamp onto the "(Poisson regime)" knot · `I8_brody_q`'s `s < 10.0` truncation ·
  `unfold_unit_mean`'s **global** normalizer · `spacings()`'s "2–98 % tail trim" that is a **positional slice
  removing no outliers** · and `validate_fitters` probing **only at the two rails**. **All are CV-scaling
  defects, and they stacked hardest on the highest-CV substrate** — measured, not supposed: value-trimming
  moves Allen-HPF's `ks_gue` **0.854 → 0.416** and hc-3's only **0.532 → 0.494**.
  **Fix the calibrator gap and the defect class stops regenerating. Fix the eight bugs and it doesn't.**
  (Built + PASSED, overnight 2026-07-12: Cox / Neyman–Scott / gamma, swept. Poisson → `I_rep` −0.009;
  clustered → **−0.39 … −19.6, monotone**; **GUE → Brody q = 1.533, ABOVE the old ceiling** — the top rail
  confirmed from a second, independent direction. `overnight_2026_07_12/`.)

  **(e) POSITIVE FORM — THE ESCAPE IS A CHANGE OF DOMAIN, NOT A CHANGE OF PARAMETER.** "Probe outside the
  reachable range" says what is *forbidden*; this says **where to go**. **A robustness check drawn from the
  instrument's own vocabulary certifies the vocabulary, not the finding.** Exhibit — **the two-pole test**: to
  test whether the substrate-relativity ladder was an artifact of its reference pole, we re-ran it on
  `ks_poisson` instead of `ks_gue`. The ordering survived; the check **PASSED**. But **`ks_gue` and
  `ks_poisson` are BOTH MARGINAL statistics** — *changing the pole while staying in the domain cannot detect a
  domain-level contaminant.* The ladder then **died instantly on a change of domain** (marginal → consecutive-
  pair): Allen-HPF's ρ(ks_gue,burst) = **−0.277** but ρ(LV,burst) = **+0.540** — dead on every marginal axis,
  **top of the zoo** on the pair axes, because its global CV is **16.2** (CV/LV = 13.5 — *the Phase-37 "CV-16"
  drift artifact, already diagnosed and fixed, and never applied to the headline it was built for*).
  **The right instinct, correctly executed, inside the broken frame — returning a reassuring PASS.**
  Every real escape this session was a **domain change**; every check that stayed in-domain passed and was
  wrong. The ones that worked: **location → dispersion** (the CI-at-a-rail inversion); **point estimate →
  interior fraction**; **single-cell → pooled** (Palm–Khintchine); and above all **observed → SHUFFLED**.

  **THE VALIDATING EXHIBIT — the rule caught its own author's finding.** The "Allen-HPF marginal/pair
  dissociation" was the session's load-bearing result. It survived **every** falsifier aimed at it — the
  reference-pole change, the rate partial, the quantile-threshold challenge, the compression test. **Every one
  of those lived inside the marginal domain, and every one of them passed.** The **within-cell ISI shuffle** —
  the *first* check drawn from **outside** the estimator's vocabulary (it destroys order and drift while
  preserving the ISI marginal **exactly**, giving the renewal null with the observed marginal, a *theorem about
  the data*) — **killed it in one run**: `ρ(burst, LV_shuf)` = **+0.517** ≈ `ρ(burst, LV_obs)` = **+0.576**.
  **LV carried essentially no order information; LV is a MARGINAL functional (`E[LV]=3/(2k+1)` under renewal).
  "Marginal → pair" was never a domain change — it was GLOBAL- vs LOCAL-NORMALIZATION. THE DOMAIN CHANGE WAS
  A CHANGE OF NORMALIZER.** *A robustness check drawn from the instrument's own vocabulary certifies the
  vocabulary, not the finding* — demonstrated, at cost, on the people who wrote the rule.

  **LEGITIMATE CORROBORATION — the rule that survives arm (d).** Arm (d)'s trap is **corroboration
  SUBSTITUTING for calibration** (ζ's top rail "confirmed" by a safe axis; the artifact welded into the ledger
  by a genuine neighbour). The legitimate case is the exact inverse: **calibrate each instrument against
  ground truth FIRST, and only then let agreement count as evidence.** Exhibit — `pvc-11` reads **CLUSTERED**
  on **two independent censored axes**: `I_rep` exact-zero (80.2 % of its BL cells; 0/200 false positives on
  the n-matched Poisson null) and the **Brody lower rail** (99.4 %; conservative P₀=0.60; decimation-immune by
  mechanism). **Different censoring mechanisms** (pointwise integrand clip vs optimizer bound) on **different
  statistics**, each **separately validated before comparison** — plus a third line from the rate-robust
  CV2/LV coupling. **That is two instruments, not one instrument twice.**

  **A FIX IS NOT LANDED UNTIL EVERY CLAIM THAT DEPENDS ON THE BROKEN AXIS HAS BEEN RE-RUN.** Building the
  replacement estimator is the easy half; **the hard half is the recompute list.** The CV-16 case is the
  strongest form of the filing failure and its own remedy: a fix that was **written, tested, and named**, then
  **not applied to the headline it was built for.** Standing artifact: **`ESTIMATOR_CLAIM_PROVENANCE.md`** —
  a maintained estimator→claim table. When an estimator changes, **every claim in its row is presumed STALE
  until re-run.** This is the structural fix for a failure that **vigilance lost five times.**

  **The knowledge was already in the repo, filed in the wrong slot.** `cross_substrate/instrument_confound.py:64-78`
  *already annotates* `"I.8_brody_q": (0.0, 1.0),  # Brody q — 0 Poisson rail, 1 GUE rail` and cites *"the same
  railed-estimator trap as the KPM-floor lesson."* But it was scoped **only to perturbation-sensitivity** (an axis
  near a rail is indeterminate *under perturbation*) and **never asked of the estimator's own primary read**. Right
  value, wrong slot — the §9 filing-discipline failure, committed against §9's own material.

  **Unclipping is necessary and NOT sufficient — the freed half-line is uncalibrated.** Removing the clip exposes a
  range that has *never been observed*, so the values on it are **numbers without a sign convention**. Before any
  substrate, run the calibrator zoo through the repaired estimator with anchors on **both** sides: a positive
  anchor (Farey — hard gap at `s_min = 3/π²`, short-range repulsion stronger than any RMT class, must sit far above
  the floor and pin the scale) **and a known-clustered negative anchor** (Cox / Neyman–Scott / bursty gamma).
  A repaired estimator with one anchor is still not an instrument.

  **Reliability does not detect censoring — and here it pointed the wrong way.** A censored axis can be measured
  *perfectly reliably*; **reliably measuring a floor is still measuring a floor.** Leg 1 cannot see this, which is
  why (e) is not a special case of (b). The tempting dual — *"censoring is the signature of spurious reliability,
  as decorrelation is of unreliability"* — was **tested on `rep_med` and DID NOT FIRE**: ρ on the uncensored subset
  (`>0` in all 5 windows) **rose**, 0.892 → 0.909; the banked 0.921 stands. A floor inflates ρ only when the point
  mass is large **and the positive half is noisy**; here the positive half was genuinely reliable, and the
  partially-censored cells *depressed* ρ. **Bank the dual with its precondition — measure both before invoking it.**
  The real lesson is sharper and more uncomfortable: **reliability and validity came apart cleanly, and the
  admissibility gate cannot see the difference.**

  **Also fix the scale.** A threshold must declare whether it applies to *observed* (attenuated) or *true*
  (disattenuated) R². An observed-scale threshold is not comparable across metrics of differing ρ. (Phase 27 used
  `ORTHOGONAL < 0.3`, Phase 32b used `< 0.20` while claiming to replicate it; neither named a scale.)

  **Scope boundary — what the ceiling arm bites.** It bites **every verdict resting on a finite-sample per-unit
  estimate** (neural per-cell, per-channel, per-window, GRB per-cell — anything windowed). It spares **every
  verdict resting on a high-reliability full-sequence estimate**, because a deterministic exact computation on a
  long sequence has `ρ≈1` by construction — nothing to attenuate, nothing to correct. This is a property of **R's
  noise, not B's shape**: the arithmetic surveys (34a/b/c) are immune because their entering quantities are exact
  full-sequence objects and their verdicts are stratum-vs-null comparisons rather than cross-unit correlations —
  *not* because they happened to use RMT/random-walk baselines. Before declaring any stratified sub-analysis
  immune, verify its entering quantity is full-sequence and not per-stratum-windowed.

  **Then scope the null precisely.** "R adds nothing beyond B **here** (this substrate set, these statistics)" is
  a **measurement-null**, NOT a refutation of the underlying object — the axis can be real and simply not cash out
  as an orthogonal observable. (Ceiling-arm exhibit — Phase 32b §7.ter.50: `p7_mean_z` was crowned "the strongest
  INDEPENDENT_AXES reading" on the *lowest* R²=0.045. It was "strongest" *because it was noisiest*. Repaired and
  re-measured in Phase 38: `ρ=0.281 [0.131,0.401]` against a required `>0.565` → **carries no orthogonality
  verdict at any baseline**. `rep_med`/`ks_gue_med`, by contrast, measure `ρ=0.921`/`0.978` and *do* clear the
  gate against FA-nmo. `phase38/PHASE38_FINDINGS.md`.)

  **Corollary — the reliability estimator is itself an instrument, and needs its own null.** The first ρ measured
  for `p7_mean_z` (`[0.132, 0.437]`) was *inflated by the very defect it was diagnosing*. `phase32b/…:173`
  re-seeded `default_rng(seed + 98765)` **inside** the window loop; with `win_dur` constant per session the
  surrogate triple became a deterministic function of `n` alone, so equal-`n` cells drew byte-identical surrogates
  and `z` was a deterministic function of `(real_p7, n)` — i.e. of *firing rate*, which is stable within a cell.
  On **pure Poisson cells with no per-cell axis at all**, that estimator returns `ρ=+0.257 [+0.088,+0.282]`.
  **Mandatory: run the split-half on a null cell** (rate-matched Poisson at the cell's own per-window counts)
  before reporting any ρ; it must return ≈0. Pair it with a synthetic known-ρ positive control. Leakage-corrected,
  `p7 @ 3 surr` gave `ρ≈0.071` and hence `R²_true = 0.113/0.071 = 1.59` — **an R² above 1**. When disattenuation
  returns a value outside the range of the quantity it estimates, that is not an imprecise estimate; it is proof
  the correction was inadmissible. Shared/derived surrogate seeds are a *correlation channel*, never a saving.
  (`phase38/calibrator_gate.py`.)
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
- **Every banked number has a committed generator that reproduces it.** (Bridge arc D-1/D-2, 2026-08-14.)
  Gates check numbers against theory, never numbers against committed code — so a banked artifact whose
  generator lives only in an uncommitted session script, or a committed file that still carries a bug the
  banked numbers were produced *without*, is a provenance gap **invisible to every gate**. Closure
  standard: the generator is committed in the same lineage as the artifact, and re-running it reproduces
  the banked numbers (bit-identically where seeded). Companion to "every ledger entry has a test twin";
  audit-cycle form is mechanical — enumerate banked artifacts, demand a generator path in the commit
  lineage of each. (`bridge/RESULTS_BRIDGE.md` Defect ledger; `bridge/fix2_replicates.py` is the
  reference instance.)
- **Sealed contingencies get a dry-run before sealing.** (Comb arc, 2026-08-15: the sealed
  extension wedge θ∈[0.45,0.85] was geometrically unfillable — canonical reps end at π/4 — and would
  have manufactured a ~16% spurious FAIL from pure geometry had it fired.) Every pre-registered
  escape hatch (extension rule, fallback substrate, park branch) is executed once on synthetic or
  cheap data at seal time, proving it CAN run. An untested contingency is a sealed promise that the
  arc's own gates never audit — precisely where a defect survives longest.
- **Vocabulary rulings must be code, not prose.** (Comb arc: the verdict-lattice holes closed at
  brief level survived one floor down in the runner — knowledge-does-not-propagate operating across
  the design→implementation boundary.) A sealed verdict lattice lives as a shared module/enum the
  runner imports, so a ruling lands once and every consumer inherits it; a lattice transcribed by
  hand into an if/elif chain re-opens every cell the ruling closed. Next arc with a sealed lattice
  implements it this way; retro-fitting frozen runners is not required — their completed lattices
  are addendum-documented.
- **A witness must be able to fail.** (Bridge review, 2026-08-15: an intensity-budget gate computed
  from theory alone could never fail; a support-set witness reported the very peak it existed to
  exclude.) Same genus as the committed-generator rule: checks that check nothing are recorded as
  green. For every gate/witness, name the input that would flip it red — if none exists, it is not
  a check. Terminal form: `verify_*.py` live checkers with nonzero exits
  (`bridge/verify_bridge.py`, `comb/verify_comb.py` are the reference instances), run after any
  edit touching a banked arc.
- **Pilot-informed seals carry their pedigree as a dated addendum.** When pilot runs legitimately shape a
  seal's windows or metrics (their declared purpose), the sealed JSON gets a clearly-dated,
  annotation-only field stating the sequence (pilots → decision → seal → disjoint-seed gates), mirrored
  in the sealing script, altering no criterion. Cheap enough to be the default; precedent:
  `bridge/prereg_sealed.json` `post_seal_addendum_2026_08_14`.
- **A witness's non-inertness is proven, not assumed.** (Holonomy KAG, 2026-08-16: the first P1
  red-demo construction — rank-windowing composed with renormalisation — was *invariant under the
  very transformation it was built to probe* (rank selection commutes with every monotone map), so
  its Δ was a pure scale factor Σ² barely feels. It was caught only because the demo carried a
  fire requirement inside a gated KAG; in any context without one, the silence would have read as
  COMMUTES.) An inert witness that goes uncaught certifies a detector that cannot detect — the
  failure is silent and looks like a pass. Rule: every witness construction is sealed WITH an
  analytic non-inertness argument — name the mechanism by which the construction CAN move the
  detector (and the invariances it must avoid) *before* running it. This is the witness for the
  witness: [[witness_must_be_able_to_fail]] demands a demonstrated red; this demands proof the
  red is *reachable* at construction time. Two-line invariance checks (is my probe invariant
  under rank selection? under monotone maps? under the estimator's self-normalisation?) are the
  cheapest form and would have caught both this near-miss and the P3 suppressor structure.
- **Sealed obligations fail closed and are inherited by default.** (Holonomy audit, 2026-08-16:
  the §2 materiality obligation was wired into the mandatory pairs' resolver but not
  `run_opt.py`, so the optional pair banked to green with the obligation silently undischarged;
  the census enumeration likewise excluded surrogate sites, so OP1's call-site facts surfaced
  only during the late repair. Same underlying shape both times: the optional work inherited the
  mandatory work's *language* but not its *machinery*.) Two clauses. **Fail closed:** a per-item
  obligation lives in the shared resolver and RAISES when undischarged — a new runner that
  forgets to wire it in cannot run to green; skipping must be impossible, not merely
  discouraged. Preventing divergence between two wired paths is not enough; the failure mode is
  silence in the third path nobody wired. **Inherited by default:** optional, later-added, or
  extension work inherits every sealed obligation (materiality, census coverage, controls,
  power) automatically; any exclusion is declared explicitly AT SEAL, never arising from which
  code path happened to get wired. An undeclared exclusion is a defect even when the excluded
  check would have passed.
- **A retraction leaves a test behind.** When a ruling, constant, or claim is reversed, the
  repair includes a negative test asserting the retracted version is rejected (reference
  instance: `verify_holonomy.py` asserts `assert_canonical` refuses the retracted OP1 order) —
  otherwise a later refactor reading old prose can silently reintroduce it. Prose retractions
  decay; failing tests don't.

## 10. Condemned paths & known gotchas

- `disc_fast` (trace-map recursion) — computes the wrong operator; quarantined.
- `dim_pressure` / `--sweep` single-level dimension — scale-dependent, fails its own gate; use
  `dim_growth` / `--degt`.
- Float potential boundary (`{np/q}≥1−p/q`) — collapses to free Laplacian; use integer `(np mod q)≥q−p`.
- `box_dim` rails on multifractal spectra (resolution-limited) — diagnostic only, bank on `bs_dim`.
- Floquet corner degenerate at q=2 — use the exact period-2 discriminant.
- `driver='ev'` (QR) saturates cores at large q — use `driver='evr'` (MRRR).
- Bare `python3` lacks pandas — use `$HOME/fmexplorer/bin/python3`.

---

## §10 — UNWRAPPED PHASE MANUFACTURES DRIFT: check the null before pre-registering

**Added 2026-08-02 from the Gaia phase-spiral arc. This is a statistics lesson,
not a claim about either substrate — nothing here connects the two programs.**

Any statistic built from an **unwrapped phase** accumulates drift for free,
because unwrapping a noisy phase sequence turns a random walk into an apparent
trend. So a threshold on *total* advance can be nearly uninformative while
*looking* like a strong criterion.

**Measured instance.** A pre-registered gate read "monotone phase advance across
≥1.5 turns". Against a phase-shuffled null over 35 annuli:

| quantity | real | null | verdict |
|---|---|---|---|
| total m=1 advance | −9.14 rad (−1.45 turns) | 8.32 ± 5.93 rad | **+0.1σ** |
| monotone fraction | 82% | 57% | **+5.3σ** |
| step-direction coherence | 0.942 | 0.18 ± 0.09 | **+8.2σ** |

**The null reached ≥1.45 turns in 39.5% of draws.** All the power lived in the
word *monotone*; the "≥1.5 turns" carried essentially none. Two conditions were
written as if they had similar weight and their weights differ by ~50×.

**The rule.** For a phase-derived statistic, score **step-direction coherence**
(are the increments consistently signed?), never accumulated total. Report the
total as a descriptive number with no evidential weight. And run the null
*before* pre-registering a threshold — the point of pre-registration is to bind
you, which it cannot do if the threshold is free to clear.

Generalises to: cumulative sums, integrated phase, unwrapped angles, winding
numbers, and any "total displacement" over many noisy steps.

### §10.1 — Amplitude-weighted coherence needs an unweighted companion

**Added 2026-08-02, the general form of §10.** A weighted coherence statistic can
report the same confidence whether the signal is there or not, because **a few
loud annuli carry the resultant while the rest are noise**. The weights are
exactly what lets a sparse, noisy regime masquerade as a coherent one.

**Measured twice, on the same afternoon:**

*Radial sweep.* Amplitude-weighted winding σ sat at **+7.5σ to +8.1σ across the
entire radial range**, including radii where the unweighted monotone fraction had
fallen to **53% — chance**. The weighted statistic could not distinguish its two
arguments. Occupancy there was ~65 stars/cell against ~3.2 km/s shot noise.

*A published prediction.* An m=2 (two-armed) hypothesis scored **+5.8σ to +7.1σ**
on weighted coherence and **+1.4σ / −0.1σ** unweighted. The weighted number alone
would have been reported as a detection.

**The rule.** Report weighted coherence and the **unweighted sign fraction**
together, always. Where they disagree, the unweighted one is right and the
weighted one is being carried by a minority of cells. Same species as an inert
symmetry diagnostic, one level up: a statistic that returns the same answer
under signal and under noise is not a measurement.

### §10.2 — A parity test is vacuous when parity IS the mode number

**Added 2026-08-03. The third of the trio, and the most structural.**

Before building a symmetry test, check whether the symmetry acts as a **global
phase** on the estimator. If it does, the test cannot distinguish its two
arguments and is vacuous — not mistuned, *vacuous*.

**The instance.** In a plane where the diagnostic is the m=1 Fourier mode, the
parity operation (z, v) → (−z, −v) is exactly θ → θ+π. That shifts every
annulus's m=1 phase by the same constant, leaving amplitudes and inter-annulus
phase *differences* identical. So "compare the statistic of the flipped data to
the statistic of the real data" returns its own input, always, signal or noise.
It would have PASSED on real data while testing nothing.

**The repair, and its own limit.** Comparing the *maps* instead is not vacuous —
but on real data it still failed, because the map was **61% even** from ordinary
physics (velocity-ellipsoid tilt), which swamped the sign: it read +0.571 where
the criterion expected −1. A structurally valid test can still be dominated by a
large nuisance component.

**The rule.** Ask of any symmetry diagnostic: *what does this operation do to my
estimator?* If it is a global phase, the test is inert — score the maps, or the
odd/even variance split, not the derived scalar. Then check whether a nuisance
term dominates the quantity you are about to threshold.

**Companion rule — a null must be interpretable before it is a result.**
A null result only means something if the selection function is symmetric enough
to support it. We closed an m=2 hypothesis as null at three radii where the
north/south count imbalance was 0.5–8.4%, and explicitly REFUSED to close it
inside R ≈ 7 kpc where imbalance reached 11–15%. "No signal" and "no power to
see a signal" are different claims and must be reported as different claims.

## 11. 2D point-process protocol — edge correction & intensity estimation
*(Founded 2026-08-14 by the Bridge arc (`bridge/`); this section is the birth of the 2D protocol,
not an amendment. First customer: the Ginibre central-sub-window KAG run, `bridge/ginibre_sampler.py`.)*

### 11.1 Edge correction (C1)

An observation window clips pairs whose second point falls outside it; uncorrected K/g/L are biased
low at all r > 0. Three standard corrections (Ripley/Baddeley lineage) and the decision rule:

- **Border (minus-sampling):** count pairs only from "eroded" points ≥ r from the boundary;
  denominator uses eroded-set intensity. Statistically wasteful, but **bias-transparent** — no
  correction-weight code path to get wrong. **Mandatory for known-answer-gate runs**: a KAG should
  not certify a correction-weight implementation and the statistic in one stroke.
- **Translation:** weight each pair (x,y) by |W|/|W ∩ W_{x−y}|. Exact for stationary processes,
  efficient, geometry-general. **Default for rectangular windows in production runs.**
- **Isotropic (Ripley):** weight by the reciprocal fraction of the circle ∂b(x,|x−y|) inside W.
  Assumes isotropy. **Default for disk/annulus windows** (e.g. Ginibre central sub-window,
  Gaussian-prime annulus).

**Survey-mask row (survey arc D1, 2026-08-15):** when the window is a survey mask, the mask
is NOT geometry to correct for — it is a point set the survey ships. **Randoms-backed ratio
estimators are primary** (DD/RR for pcf/K; randoms-normalized cell expectations for Σ²): the
window cancels in the ratio, holes and all, and the mask KAG (thinned-randoms-as-data must
return DD/RR ≡ 1) is the witness. Analytic border corrections survive only in synthetic KAGs.
Estimator-null musts, both caught by the first real-window KAG run (survey/D1_LOG.md): the
cell-expectation variance carries a randoms-shot-noise term (W_D/W_R)·w̄₂_R·Ē alongside the
weighted-Poisson term, and weighted-pair z-scores use effective counts DD²/Σ(pairweight²),
never raw √DD. **The quantitative case against "just use a simple window":** the D1 red path
ran the forbidden uniform-box analytic window against DESI DR1 Poisson-through-mask data and
manufactured F(1°) = 15–19 — an order of magnitude of fake super-Poissonianity from mask
holes alone (|z| = 130). That number is why tripwire 6 exists and why the randoms-backed
architecture is not a convenience choice.

**r_max rule:** never evaluate K/g beyond r_max = ¼ of the shortest window dimension (annulus:
¼ of the radial width). Beyond that, correction weights dominate and variance explodes.

**1D ancestor (filed):** the per-sector Weyl-completeness window gate
(`sessionK/maass_analysis.py:5`) — same defect genus: objects missing near the window boundary
bias the statistic. The 1D remedy is *gate the window's completeness before computing*; the 2D
remedy is *weight or discard near the boundary*. Both are boundary-accounting, and both must be
declared per run.

### 11.2 Intensity estimation for inhomogeneous substrates (C2)

For stationary substrates: single global λ̂ = n/|W|; done. For inhomogeneous substrates, in order
of preference:

1. **Parametric / theory-supplied λ(x)** (e.g. Gaussian primes: λ ∝ 1/(2 ln r) from the Landau
   ideal-count asymptotic). External, non-circular — the analogue of unfolding with an external
   rate (§9 "the right null is substrate-specific").
2. **Thin-window near-constancy:** window the data so λ varies less than a **pre-registered
   variation budget**; then use the stationary estimators with the residual variation filed as a
   declared approximation.
3. **Kernel-smoothed λ̂(x):** bandwidth is a free parameter and **must be pre-registered**.
   Too-small bandwidth absorbs the very repulsion/clustering being measured — the 2D twin of the
   structurally-circular self-derived rate-unfold (§9). Never tune bandwidth on the statistic
   being reported.

**Double-application tripwire (pre-registered, Bridge §3.1):** never unfold AND intensity-reweight
the same data path. A path in mean-spacing (unfolded) units takes the *stationary* estimators; a
path handed to K_inhom keeps raw coordinates and carries λ(x). Each pipeline declares which
transition it uses — one transition per path, cited by file:line.

**FIX-2 twin (filed):** wrong intensity ⇒ corrupted K_inhom is the same defect class as wrong
unfolding lens ⇒ inverted Σ² (the FIX-2 precedent). The intensity model is part of the claim and
gets audited first when a 2D reading surprises.

### 11.3 The gluing identity loses SNR exactly where rigidity is strongest (Bridge-arc instrument note)

The Σ²-from-pcf identity (Var N = λ|B| + λ²∫(g−1)γ_B) is a **near-cancellation** for
hyperuniform/rigid processes: exact Ginibre gives Var N(R) = R/√π against an area term λπR² = R²,
and 1D GUE gives Σ²(L) ~ (1/π²)ln L against L. Two consequences, both measured in the Bridge arc
(`bridge/pilot2_gluing.py`, `bridge/pilot4_thomas.json`):

1. **Offset amplification ~ (λ|B|)²·δ / Var.** Any baseline offset δ in ĝ−1 — bin noise, the
   residual normalization offset (~1/√n_pairs, irreducible whether ĝ is normalized by the model λ
   or by λ̂; pilot-4 measured ~4·10⁻³ at n≈14k in a 120² window), finite-sample bias — enters the
   identity multiplied by the *area term squared* and then competes with Var. On plain 2D Poisson
   this already grows 2.7%→48% across R=2→6; rigidity makes it strictly worse because Var is
   smaller still (2D Ginibre, per-unit-offset A=(λπR²)²/Var: 14→528 across R=2→6; 1D GUE at L=20: L²/Σ² ≈ 555×). [Numbers corrected 2026-08-15: an earlier column banked μ/Var — one factor of μ short of the law; see bridge seal addendum.]
2. **Consequence: gate the identity only at small windows, whatever the substrate** (Bridge arc
   sealed R=2 / L≤5 at n~10⁴–10⁵), and report large-window rows descriptively with the
   amplification factor alongside. A gluing "failure" at large R/L is the amplification law, not
   a transition defect — but a failure at small R/L is a real defect (dimension slip, factor
   error, normalization inversion — the FIX-2 class the gate exists to catch).

## §12 Canonical Order Registry (Holonomy pilot, 2026-08-16)

**The executable owner of every ruling below is `holonomy/canonical.py`** (rulings-as-code;
call sites guard with `assert_canonical(pair_key, order)`; if this prose ever disagrees with
that module, the module wins and the prose is the defect). Full evidence:
`holonomy/COMMUTATOR_TABLE.md`; seal `holonomy/prereg_sealed.json`.

Transitions in a pipeline are applied in an order, and the order is part of the estimator.
The pilot measured which orders matter, under what law, and ruled the ones that do. The
ruling-basis field says what kind of weight each ruling carries: **RULED_CORRECT** (bias
separated against ground truth where measured), **RULED_CORRECT_BY_TRANSFER** (separated on a
synthetic analogue, applied where truth is absent), **RULED_CONSISTENT** (coordination only).

| pair | canonical order | basis | short reason |
|---|---|---|---|
| unfold ↔ window (1D) | **window, then unfold** | RULED_CORRECT (transfer at zeta) | estimate/normalise the unfolding on the analysis window; bias 0.09 vs 4.85 at the resonance dial. `compute_nns` self-enforces this for NNS as a *mechanism* (its internal renorm — census C1); the both-orders-equivalence *datum* is zeta-only (seal ADD-4). **Σ² consumers do not inherit either and must re-unfold per window** |
| reweight ↔ edge-correct (2D) | **edge-correct, then fit λ̂** | RULED_CORRECT (by transfer to future callers) | fit intensity on the eroded domain the statistic integrates over; continuum law confirmed to 4.30× gradient. No live λ̂-estimating caller exists today (census C3) |
| weight ↔ thin (survey) | weight, then thin (frozen semantics) | RULED_CONSISTENT | POINT_CHECK_CLEAN **at sealed points/power only — not COMMUTES**: mechanism real (−10⁴ counts/draw, 12σ suppressor-free), suppression owned by the ratio/self-normalising estimator family; a refactor abandoning DD/RR normalisation does not inherit the clean row |
| surrogate ↔ unfold (1D) | **MATCHED LENS** (surrogate and data pass the identical unfold apparatus; no bare sequence order) | RULED_CONSISTENT, leg run, **separation UNDER_RESOLVED — not a null** (seal ADD-1/ADD-3; original blanket order retracted) | measured non-commutation ΔΣ²(20)=+1.15±0.23; materiality NOT clean at the RIGID_GUE gate under the worst-case screen (1.4×<k=3) → correctness leg run: mixed order biases marginal-class data rigid-ward in both runs (z −0.32 vs −0.04, ~1.4σ) — under-resolved at k=3, not absent; site-specific effect ~0.3σ of the classification band; rerun consumed |
| disattenuate ↔ pool | **disattenuate, then pool** | RULED_CORRECT | pooled-then-disattenuated biased by the Jensen factor; sealed formula confirmed z=0.64 |
| window ↔ project (survey, C4) | *(unruled — census-found, unmeasured)* | — | fused single order in `tile_points`; registered for a future arc, do not treat as free |

**Standing distinctions this section exists to preserve:** POINT_CHECK_CLEAN ≠ COMMUTES (the
former claims nothing off its sealed points); a clean row can be OWNED by an estimator family
rather than by the transition pair; and pairwise cleanliness does not bound full-sequence
holonomy (brief §7 scope limit).

**§12 registry additions (2026-08-16, overnight items 2–3).** Two rows join the Canonical Order
Registry (`holonomy/canonical.py` remains the owner):

| pair | canonical | basis | short reason |
|---|---|---|---|
| window ↔ project (survey, C4) | **matched** (same order for data and randoms) | RULED_CONSISTENT, `NO_TRUTH_BY_CONSTRUCTION` | mechanism real and predicted — q ≈ 0.79·θ², 0.6% of points change tile membership at the deployed 10° tile — but statistic-level effect suppressed by the ratio estimator **and** `cells_F`'s CELL_FLOOR; mismatching the order inflates F by ≈ q (measured −0.054 at 30°) |

`NO_TRUTH_BY_CONSTRUCTION` is a third separation status alongside `UNDER_RESOLVED`: the former
means no correctness leg *can* exist (both arms are legitimate), the latter means one exists but
did not resolve at arc power. A reader must not read either as evidence the orders are equivalent.

- **A calibrated boundary certifies its reference ensemble, not its power to exclude neighbours.**
  (RIGID_GUE arc + L-policy arc, 2026-08-16, Will's naming.) The long-range gate's boundary was
  properly calibrated — bands validated against the Mehta and renewal asymptotes to 0.2%, a stated
  2.5·sd tolerance — and its **separation from adjacent classes was never characterized as a
  function of the judging scale.** At the deployed L=50, **GOE — a genuinely different universality
  class — read `RIGID_GUE`**, because across L=3→50 the GUE band's spread grows ~5.7× while the
  GUE–GOE gap grows only ~1.4×. Calibration is a statement about the reference; **discrimination is
  a separate statement about the neighbours, and it must be measured against the nearest confusable
  class at the configuration actually deployed** — and re-measured per n, since the band widens as n
  falls (the same gate separates GOE by +4.0σ at n=2000/L=40 and only +2.2σ at n=343/L=6.86, the
  configuration banked rows used). Distinct defect class from the one-sided-vocabulary problem, and
  both of that arc's caps came from asking a question nobody had asked of the deployed
  configuration.
  **"Nearest confusable class" is a LIVE obligation, not a fixed reference.** Naming a specific
  neighbour once (this arc named GOE) makes the rule satisfiable by re-measuring against that same
  neighbour forever, while the zoo grows underneath it. So: the nearest confusable class is
  **re-identified from the CURRENT zoo at each measurement** — whichever member sits closest to the
  target's band at the deployed configuration — and **adding a zoo member that sits closer than the
  incumbent automatically triggers a re-measure of every cap derived against the incumbent.** Record
  which neighbour a cap was derived against (`lcap/policy_n.json` registers GOE) so the trigger has
  something to compare to; the record is the mechanism, not the exemption.
- **A principled RESTRICTION is not automatically a power sacrifice.** (L-policy arc; Will's
  update, stated at the general level with L as the instance that produced it.) The intuition
  "narrower ⇒ less data ⇒ weaker result" is not reliable, because a restriction acts on the null
  band and on the effect *separately*: whenever it shrinks the reference band faster than it
  shrinks the effect, significance **rises**. Nothing in that mechanism is specific to window
  length — it applies to **any restriction carrying a validity argument: a scale cap, a quality
  cut, a subsample, a mask, a redshift or height slice.** So a proposed restriction has its power
  measured on both terms, never assumed in either direction, and the measurement can return "the
  restriction is free" as readily as "the restriction is expensive." Instance that produced the
  rule: ζ judged at its Berry validity scale reads **z = −9.10** against **−2.33** at the deployed
  L=50 — the wide-L policy was diluting a 9σ effect, so the cap *bought* significance. An
  L3-style power cell is the general instrument.
- **A policy adopted into shared code does not silently re-scale existing call sites.** (L-policy
  adoption, 2026-08-14→16.) Installing a scale/threshold policy so that it takes effect wherever a
  parameter was previously passed explicitly would change banked outputs without a re-run anyone
  authorized — the same shape as enforcing a blanket ordering mid-flight (the OP1 retraction). The
  correct division: **the policy ships as a helper the call sites opt into, the call sites keep
  passing their parameter explicitly, and a live checker pins the policy present and correct** so
  the adoption cannot silently lapse either. Migration of a call site is then its own dated,
  authorized step with its own re-run.
- **Before measuring how well, establish WHAT — tie the estimand to the operational decision.**
  (L-policy arc, 2026-08-16; Will's promotion of the round's closing observation.) Three numbers in
  that arc dissolved on inspection because an *estimator's variance* went unmeasured — a **precision**
  failure. The fourth dissolved for a worse reason: the **estimand was wrong**. The cap was measuring
  separation of population means while the gate it certified classifies **one point set at a time**,
  and separation-of-means cannot see the spread that decides a single realization's fate. **A wrong
  estimand is a different and worse category than imprecision, because more precision on the wrong
  quantity converges confidently on the wrong answer** — and it retroactively explains why the caps
  kept moving: an estimator cannot be stabilised while it is estimating the wrong thing.
  Rule: **a gate that classifies one realization must be certified by a per-realization error rate,
  in BOTH directions** (false positive AND false negative — a restriction that fixes discrimination
  can destroy sensitivity, and one rate alone cannot see that). Separation-of-means is valid only
  where the decision itself is about populations. Measured instance: at the deployed configuration
  the separation-of-means statistic read a merely-marginal +2.48 while the true per-realization
  misclassification rate was **57%** — the wrong estimand was understating a coin-flip gate by an
  order of magnitude. **The mismatch is not usually confined to one gate:** censusing for it found
  two further validation harnesses certifying per-realization machinery with population statistics,
  including the one that certifies the calibrator zoo's fitters (`lcap/ESTIMAND_CENSUS.md`). A
  mean-based validation tests **bias**, which is legitimate; it does not test **per-realization
  reliability**, and if nothing else supplies that half the certification is incomplete. When the
  idiom turns out to be house-wide, the repair is a policy change, not a per-gate fix.
  **The purest instance, worth quoting because it needs no estimator subtlety at all:**
  `validate_fitters.py` banks `brody_q_per_seed` and then computes its PASS from `mean(qs)` — the
  harness *had the per-realization data and threw it away*. The fix is a few lines; that it was
  never made means **nobody ever asked what the PASS was for.** Alongside the 57% number, that is
  the failure in its two forms: one where the wrong estimand hid a coin-flip gate behind a
  marginal-looking +2.48, and one where the right data sat unused in the same function.
  Corollary for thresholds: **fix the derivation rule per gate type BEFORE measuring**, or the
  threshold drifts toward whatever the harnesses turn out to do (`lcap/RELIABILITY_THRESHOLDS.md`).
- **A sealed sample protects against post-hoc selection, not against unrepresentativeness — enumerate
  when you can.** (Full-sequence arc, 2026-08-17.) The arc sealed a 7-ordering sample by rule before
  measuring, which correctly prevented adding or dropping orderings after seeing the answers. Its
  three multi-inversion members all came back sub-additive, and the write-up concluded composition
  is sub-additive so the pairwise table is a conservative upper bound. Tested **exhaustively** on all
  59 admissible orderings hours later, **that claim was false**: 12 have H ≤ 0 and 10 are
  significantly super-additive, because the failures concentrate in a region (UNFOLD applied after
  POOL) that the sealed sample happened not to reach. **The sample was not biased — it was chosen by
  a rule fixed in advance — it was unrepresentative**, and no amount of sealing discipline detects
  that. Rule: when the space of possibilities is small enough to enumerate (here 5! filtered to 59),
  **enumerate it**; sample only when you cannot, and when you must sample, treat any structure found
  as provisional until an exhaustive or independently-drawn set confirms it. Corollary that made the
  catch cheap: the sampled result becomes a *falsifiable prediction* for the rest of the space, so
  the follow-up is a real out-of-sample test rather than a re-analysis.
- **Validate a census detector on known answers before trusting its silence.** (Estimand census,
  2026-08-17.) A search that returns few hits is only reassuring if it can find the hits you already
  know about. An AST detector built to census one defect pattern across the repo was run first
  against the two instances confirmed by hand: it found one and **missed the other**, because that
  one hides as a ratio of two dictionary lookups with no syntactic collapse to key on. Reporting the
  sweep as a clean census would have converted a 50%-sensitive instrument into a false all-clear over
  17 directories. Rule: **every automated census names its known-positive self-test and its measured
  false-negative rate in the same breath as its result**, and reports as a LOWER BOUND when the test
  is not perfect. Companion to the "not examined ≠ cleared" scoping rule — that one covers what the
  search never looked at, this one covers what it looked at and could not see.
