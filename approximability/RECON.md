# RECON — Approximability Spacing Panels (§0 deliverable)

Read-only recon before any panel code. Tags: `[code]` read from executable code, `[documented]` from a
docstring/comment, `[inferred]` deduced. Pinned at `master @ 1a84047`. Deliverables land in `approximability/`.

---

## §0.1 — What is `C` (the "DEGT dimension constant")? **IDENTIFIED.**

**`C` = the DEGT dimension = `dim(Σ_λ) · ln(λ)`** — the fractal dimension of the **spectrum `Σ_λ` of the
Sturmian/metallic Schrödinger (Fibonacci Hamiltonian) operator** at coupling `λ`, multiplied by `ln λ`.

- **DEGT** = Damanik–Embree–Gorodetski–Tcheremchantsev (2008). Golden strong-coupling target:
  `dim(Σ_λ)·ln(λ) → ln(1+√2) = 0.88137` as `λ→∞`. `[documented]` `trace_map_dimension.py:16`,
  `dimension_theory_check.py:5-6`.
- **Definition constant in code** `[code]`: `dimension_theory_check.py:45` and `trace_map_dimension.py` —
  `DEGT = np.log(1.0 + np.sqrt(2.0))   # 0.88137`.
- **Two estimators of `dim(Σ_λ)`:**
  1. **Box-counting on finite eigenvalues** — `dimension_theory_check.py` `box_dim_naive:56`, `box_dim_windowed:64`,
     `box_counts:48`. **Known to FAIL** at large λ (cluster-splitting + finite-N caps the resolvable Cantor depth;
     `box_dim·ln λ` drifts *down*, away from 0.881). `[documented]` `dimension_theory_check.py:8-14`. This is the
     memory note [[validate_scale_convergence_before_asymptotic_constant]].
  2. **PROPER: Bowen-pressure on periodic-approximant band widths** — `trace_map_dimension.py`. Fibonacci-period-q
     approximant `α_n=F_{n-1}/F_n`; period-q discriminant `Δ_q(E)=Tr∏T_j(E)`; spectrum `= {E: |Δ_q(E)|≤2}` = union of
     q bands; dimension `d` solves the **Bowen pressure equation `Σ_k |band_k|^d = 1`**; `d_n → dim` as `q→∞`.
     `[documented]` `trace_map_dimension.py:1-20`. This is "how DEGT/physics-lit compute it."
- **Per-object value + fingerprint axis** `[code]`: banked as `dim_times_lnlam` (+ a `converged` flag +
  `lagrange_class`) in `coordinates/trace-map-dimension.jsonl`; the live fingerprint axis is
  **`IV.2_spectral_box_dim`** in `axes.py` (used at `confluence_view.py:63,76`).

**LINEAGE VERDICT (the §0.1 answer):** `C` is a **spectral Cantor-set dimension** (dimension lineage), specifically
the **DEGT Fibonacci-Hamiltonian** constant — **NOT** the Lévy growth-rate `𝓛=(1/p)log ε`, and **NOT** the
Jenkinson–Pollicott CF-Cantor `E_2` dimension (0.531280…). The three are related through thermodynamic formalism but
`C`-as-computed is the operator-spectrum dimension.
- **Implication for Panel A (H1):** the spec's H1 ("`C` is the rate functional `𝓛`, `Λ` the max functional") is testing
  whether this *spectral* dimension is affine in the Lévy constant. It is a genuine open empirical question — the
  DEGT constant `ln(1+√2)` is itself the log of the *silver* ratio, hinting at a growth-rate connection, but `C` is not
  `𝓛` by construction. Panel A's regression (C vs {𝓛, Λ, p, max-digit, dim E_alphabet}) is the right test; run it.
- **Reference-value cross-check** (spec §0): the spec's outside estimates gold≈0.875, silver≈0.867, bronze≈0.913,
  metallic-4≈0.994, e−2≈1.17 are finite-λ `dim·ln λ` values (breakaway intercepts), consistent with the golden DEGT
  gate 0.881 and e "flying to 1.17". `[documented]` `e_vs_metallics_visuals.py:9-11,171-172`.

---

## §0.2 — Reused engines (do NOT rewrite; wrap these)

**Spacing engines** `[code]`:
- **NNS / Family I marginal** — `cross_substrate/axes.py`: `canonical_spacings:61`, `I1_w1_clock`…`I13_lv`,
  `I5_ks_gue:111`, `I8_brody_q:147`, `I10_cv:175`, `compute_family_I:244`.
- **Long-range Σ²/Δ₃** — two routes: raw `axes.py` `II1_sigma2_at_L:277`, `II2_delta3_at_L:293`, `compute_family_II:327`
  (NO internal unfold — caller must unfold); and the **GUARDED** `longrange_discriminator.py` `longrange_verdict:180`
  (density-adaptive poly unfold + built-in GUE/Poisson calibrator references + lens-sensitivity). **Use the guarded
  path for any Σ²/Δ₃ verdict** (see FIX deps).
- **Reference CDFs / surmises** — `universality.py`: `nns_cdf_poisson/goe/gue`, `number_variance:126`,
  `spectral_form_factor:173`, Wigner surmises.
- **Surrogates / induction-on-noise** — `surrogates.py`.
- **Calibrator zoo** — `calibration_anchors.py` (GUE/GOE/GSE/Poisson/clock through the live axes — but import-broken +
  produced the inverted Σ², see FIX deps), `calibrator_panel.py`, `rf_decoy_battery.py`.

**CF / dimension engines** `[code]`:
- `trace_map_dimension.py` — `band_widths`, `_potential`, `cf_convergent`, `DEGT`, Bowen-pressure dimension. **The C engine.**
- `dimension_theory_check.py` — box-dim estimators (validation counterpart at moderate λ).
- `cf_mechanism.py` — `max_cf_quotient:58` (max partial quotient), `gap_cv:48`; `cf_discriminator.py` — CF class discriminators.
- `brocot_approximability.py` — Lagrange-target depth sweep (9 Lagrange classes; an EXPOSED Family-II site, see FIX).
- `lambda_star_classes.py` — λ*(class), box_dim + poly_unfold(deg12) fingerprint per metallic/quadratic.
- `gold_silver_ladder.py` — the metallic ladder `[¯n]` (Panel A's fixed-word control).

**Plot views to EXTEND (not fork)** `[code]`:
- `e_vs_metallics_visuals.py` — sunflowers / CF barcodes / **spectral Cantor sets** (`fig_cantor:150`, annotates `C`) /
  **DIMENSION BREAK-AWAY** (`fig_breakaway:179`, the V8 dim·lnλ extrapolation with DEGT dashed line at `:203`). **= V8.**
- `confluence_view.py` — `D_box(λ)` coupling view (`fig_coupling:114`), Brody-q vs W1δ scatter. **= a V-series coupling panel.**
- `landscape_view.py` — landscape scatter.

**Plot theme / raw-output convention** `[inferred]`: reuse the repo's matplotlib theme used across `*_view.py`;
keep raw `C/𝓛/Λ` tables as CSV (spec §9) alongside the banked `.jsonl` under `coordinates/`.

---

## §0.3 — What is already plotted (V5/V7/V8)

- **V8 = `e_vs_metallics_visuals.fig_breakaway`** `[code]` `:179-204` — `dim·ln(λ)` vs λ per Lagrange class, per-class
  intercept marker `<` at λ→∞, DEGT golden dashed line `ln(1+√2)`. e-class "breaks away" to ~1.17.
- **Spectral-Cantor / band-structure = `e_vs_metallics_visuals.fig_cantor`** `[code]` `:150-174` — band/gap staircase
  annotated `C=…`. (The IDS-staircase relatives are `sturmian_run.py` / `am_confluence.py`.)
- **`D_box(λ)` coupling = `confluence_view.fig_coupling`** `[code]` `:114-152`.
- **V7 (Lagrange-axis `C`-vs-`Λ` zigzag + triangle) — NOT yet pinned to a single file.** `[inferred]` Candidates that
  carry a Lagrange axis: `gold_silver_ladder.py`, `cf_discriminator.py`, `cf_mechanism.py` (`_figure:144`),
  `brocot_approximability.py:162`. **ACTION:** confirm the exact V7 producer on the first read of the Panel A/C build
  (Panel C §6.2 re-draws V7's polyline three ways, so its source must be located then). Do not assume.

---

## §0.4 — Blocking FIX dependencies (checked against `audit/06-fix-list.md` + `verify/`)

**The `C` computation is FIX-CLEAN** `[code]` (verified: `trace_map_dimension.py` / `dimension_theory_check.py` import
none of `axes`/`universality`/`surrogates`/`signal_gen`/`unfold`/`compute_family`). Panel A's C engine + the from-scratch
`𝓛`,`Λ` (period-matrix eigenvalue `ε`) are independent of every open FIX. **Panel A is unblocked.**

**But the C constant has its own known hazard** (not a FIX, a convergence gate): box-counting does not reach the DEGT
constant. **Gate:** use `trace_map_dimension.py --validate` first — the band-pressure `d` must match banked `box_dim` at
moderate λ∈{2,4,8} (golden λ=2 → 0.628) before trusting large-λ values. `[documented]` `trace_map_dimension.py:22-25`.
This is the [[validate_scale_convergence_before_asymptotic_constant]] discipline; spec §4 calibration gate depends on it.

**Panels B & D (spacing readouts) DO depend on open FIX items:**
- **FIX-1 (`$HOME` import break):** `signal_gen.py:16` literal `$HOME` breaks import on a clean process. If any panel
  imports `signal_gen` (or `calibration_anchors`, which imports it), run under
  `PYTHONPATH=$HOME/fmexplorer/riemann_explorer`. `[code]` verified in `verify/`.
- **FIX-2/7 (Σ² magnitude, verdict-safe):** raw `compute_family_II(unfold_unit_mean(...))` gives an unreliable Σ²
  *magnitude* on non-flat-density inputs (Tier-2: 0.19×–1.6×), though the **verdict is lens-invariant**. **Mandate for
  B1/D:** read Σ²/Δ₃ through `longrange_verdict` (density-adaptive), NOT raw `compute_family_II`; quote verdicts, not
  absolute Σ². `[code]` `verify/00-summary.md`.
- **FIX-8 (guardrails disconnected) + poisoned anchors:** `calibration_anchors.jsonl` was deleted (inverted Σ²); the
  calibrator zoo is not auto-run. **Mandate (aligns with spec §3/§8):** every panel runs its own calibrator inline
  (GK-random, golden, Poisson, rigid) — do not trust any banked calibrator coordinate.
- **NNS-marginal caveat (spec §8):** short-range NNS cannot resolve approximability class (structural). Enforce the
  spec's "no class claim from an NNS-only probe" — long-range Σ²/Δ₃ (guarded) is the class instrument.

---

## Summary for the build
1. **`C` is the DEGT spectral-Cantor dimension** `dim(Σ_λ)·ln λ` (gate `ln(1+√2)=0.88137`), via Bowen-pressure band
   widths — dimension lineage, not Lévy-rate, not `E_2`. Panel A regresses it against `𝓛/Λ/…`; C engine is FIX-clean.
2. **Reuse:** `trace_map_dimension` (C), `axes`+`longrange_discriminator` (spacing, guarded), `cf_mechanism`/`cf_discriminator`
   (CF stats), `e_vs_metallics_visuals`/`confluence_view` (plots to extend).
3. **Gates:** trace-map `--validate` before any large-λ C; inline calibrators per panel; guarded Σ² for B/D; PYTHONPATH
   shim for `$HOME`.
4. **One open recon item:** pin V7's exact source file before Panel C §6.2's re-ordering test.
