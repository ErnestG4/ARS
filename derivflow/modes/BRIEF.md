# BRIEF — derivflow/modes: is the measured relaxation the flow's or the reference's?

Status: DRAFT. Nothing here runs until Will says "go".
Author: Claude (chat), 2026-09-17. Executor: Claude Code on Will's 4090 machine.

Launch options (Will sets these when launching):
- WINDOW_HOURS: default 8.
- AFTER_M0: `stop` (wait for review) or `continue` (proceed if M0 raised no STOP).
- PUSH_BRANCH: `yes` or `no`.

## 0. Framing — read first

### 0.1 Where you are
- **Repo:** `$HOME/fmexplorer/criticality_tool/` (the ARS repo). This repo only.
  - Do NOT read or write `$HOME/fmexplorer/riemann_explorer/`, `$HOME/fmexplorer/fm_explorer/`, the brocot.fm repo, or any other repo.
- **Python:** always `$HOME/fmexplorer/bin/python3`, never bare `python3` (venv trap).
- **Arc:** `derivflow/` (real-rooted polynomials under repeated differentiation; the paper "Local crystallization beneath a frozen global measure").
  - Out of scope: the ARS classifier (`phase22a.ars_classify`, `joint_q_profile`), `cross_substrate/`, `lcap/`, `arsrh/`, `holonomy/`. The one exception is the read-only import allowed in §4.3.
  - Also out of scope: the queued successor-form arc (F3 in (λ, beta_kww, k*); CAPABILITY_REPORT open item 16). Do not conflate the two.
  - Numbering: `derivflow/RECERT_SCOPE.md` uses "Stage 0/1/2a…3e/4". That is a different numbering; this brief uses only M0–M6 and gates ML/MT.
- **Git:**
  - Expected `main` = `589d7d8` (CAPABILITY_REPORT, 2026-09-16). Verify it. If it differs, record the actual hash and proceed from it.
  - Never rebase, merge, delete a branch, or commit/push to `main`.
  - The working tree must be clean; otherwise STOP.
  - Create branch `derivflow-modes` from `main` HEAD. If it already exists, STOP.
  - All new files go under `derivflow/modes/`. Push the branch only if PUSH_BRANCH=yes.
- **First commit:** this brief, verbatim, as `derivflow/modes/BRIEF.md`.

### 0.2 Questions
- **Q1.** On identical roots, does omr computed WITHOUT unfolding differ from the production (unfolded) omr in k_star and in tail form?
- **Q2.** What does the production unfolding reference do to a planted displacement wave, as a function of qw and k? This is its transfer function.
- **Q3.** Does one derivative step multiply a small displacement wave by exactly (1 − qw/π)?
- **Q4.** (Night 2, only on Will's go) Does evolving each seed's own gaps with that multiplier predict the no-unfold curve? And is the late-k tail exponent set by the long-wavelength gap spectrum, p_tail = (3 + alpha_spec)/2, rather than by local repulsion?
- **Q5.** (Night 2) Does the crystallized region grow as a front with L_half(k) ∝ k?

### 0.3 Not in scope
- **No re-grades.** RATE-SEED-DEPENDENT and SCALE-FLAT stand as recorded.
- **No paper edits.** Do not modify any copy of the paper. Findings go into the night report as proposals.
- **No exploration.** Every run is a declared cell in the manifest before it executes. Nothing is tuned after outputs are seen.

### 0.4 Permitted edits outside derivflow/modes/
1. Register the new checkers in `verify_all.py`, the same way `verify_recert.py` / `verify_seed_roster.py` are registered (find them first).
2. Append new threadledger rows for this arc (locate the data via `threadledger.py`), with status QUEUED:
   - `derivflow-modes-gate-ml`
   - `derivflow-modes-gate-mt`
   - `derivflow-modes-nounfold-vs-prod`
   - `derivflow-modes-exponent-law`
   - `derivflow-modes-front`

   Never edit existing rows.
3. One new memory entry per night, `derivflow-modes-night<N>`, in `~/.claude/projects/-home-combust-fmexplorer-criticality-tool/memory/`. Never edit existing entries.

Everything else is read-only. That includes all existing `derivflow/*.json`, the seals, `knownanswer.py`, `spacings.py`, `lineage.py`, `errormodel.py`, and anything covered by `verify_frozen_blobs.py`.

### 0.5 When sources disagree
Authority runs in this order:
1. committed artifacts (JSON + generator + checker);
2. code;
3. `RECERT_CORRECTIONS.md` and findings docs;
4. CAPABILITY_REPORT / RESULTS_MATRIX;
5. memory entries;
6. this brief.

Record every conflict in the manifest. Never resolve a conflict by editing.

## 1. Binding vocabulary

| name | meaning | NOT |
|---|---|---|
| `n` | seed degree (roots at k=0) | event counts |
| `k` | derivative order | `k_thresh`, gamma shapes |
| `n_k` | n − k | |
| `t_flow` | k/n | ARS `s` (a spacing) |
| `h` | seed lattice spacing, 2/(n−1) | |
| `qw` | displacement wavenumber, radians per root index, 0 < qw ≤ π | ARS `q` (Farey/RF denominator) |
| `A` | planted amplitude, in units of the local mean spacing | |
| `gain(qw,k)` | real response ratio measured in gate ML | |
| `T(qw,k,arm)` | complex transfer function measured in gate MT | |
| `beta_dyson` | β-Hermite index 1/2/4 | `beta_kww` |
| `beta_kww`, `tau_kww` | F3 stretch exponent and time scale | Dyson β |
| `alpha_spec` | long-wavelength gap-spectrum exponent, S_g ∝ qw^alpha_spec | Brocot/approximability α |
| `omr` | 1 − mean(r̃), with r̃_i = min(g_i, g_{i+1})/max(g_i, g_{i+1}) over consecutive gaps in the bulk window, exactly as production computes it (M0.2 confirms) | |
| `k_star` | crossing of omr = KSTAR_LEVEL | |
| `p_tail` | −(OLS slope of ln mean-omr against ln k) over a declared k range | |
| `L` | Σ² window length in mean spacings | the lcap/ L-policy |

**Arms** (how gaps are formed before omr is computed):
- `PROD_PRIMARY`, `PROD_BW1`, `PROD_BW2`: the paper's primary arm and its two "raw bandwidth" arms, all of them unfolded. Resolve the exact names from the seals in M0.
- `NOUNFOLD`: raw root differences x_{i+1} − x_i in the same bulk window, with no reference.
  - The paper's "raw arms" are PROD_BW1/2, NOT this. Never label NOUNFOLD "raw".
- `POPREF`: unfolded against the fractional free convolution of the ANALYTIC seed law, not the empirical seed.
- `RM1`: each raw gap divided by the mean of the raw gaps at index offsets −1, 0, +1 (truncated at window ends). Witness only.

**Seeds:**
- `IID_UNIFORM`: the paper's seed, i.i.d. Uniform[−1,1].
- `GUE_DE`: the paper's GUE seed, the Dumitriu–Edelman β=2 tridiagonal.
- `BETA_HERMITE_{1,2,4}`: the `seed_roster_beta` generator. Verify BETA_HERMITE_2 ≡ GUE_DE.
- `LATTICE`: n equispaced points on [−1, 1].
- `QLATTICE(law, t_flow)`: x_j = F^{−1}((j + ½)/n_k), where F is the CDF of the analytic law evolved to t_flow.
- `LATTICE_WAVE(qw, A, phi)`: LATTICE plus δx_j = A·h·sin(qw·j + phi).
- `WIGNER_RENEWAL`, `SPEC_ALPHA(alpha_spec)`: constructed as in §4.3.

## 2. Prior look — commit as `derivflow/modes/PRIOR_LOOK.md` right after BRIEF.md

All numbers below come from Claude's chat sandbox: float64, uncertified sandbox solvers, tiny ensembles. Any cell overlapping them is graded DECLARED-WITH-PRIOR-LOOK.

- **Linearization:** one step multiplies a displacement wave by 1 − qw/π. This matched to 6 digits on a periodic 1024-root trigonometric lattice, with A = 1e-4 and qw from 0.006 to 3.14.
- **Circle** (periodic, M = 1024, no unfolding needed):
  - iid (3 seeds): omr 0.0354 at k=10, 0.0093 at k=24, 0.0035 at k=48. First k with omr < 1e-2 is 23. Slope over k 16–48 is −1.46.
  - COE (1 seed): first k = 12, slope −1.98.
  - CUE (1 seed): first k = 9, slope −1.81.
  - Linear evolution of each seed's own gaps:
    - COE/CUE: within 2–8% from k=1, and within 1% after k≈10.
    - iid: about 11% off at k=10 when started from the seed, about 2% when started from the k=10 state.
- **Line** (n = 1024, IID_UNIFORM, central half, 2 seeds, sandbox solver):
  - NOUNFOLD crossing ≈ 27 (interpolated between k=24 and k=32), slope −1.48.
  - Running-mean references:
    - ±25 gaps: slope −1.64.
    - ±5 gaps: crossing ≈ 17, slope −2.80.
    - ±1 gap: crossing ≈ 9.6, slope −3.49.
- **F3 used for comparison:** tau_kww = 1.734, beta_kww = 0.788, with the amplitude set so the curve crosses 1e-2 at k = 10.83.
- **Circle Σ²(L; k)/L at k=48:** 0.109 at L=10, 0.185 at L=20, 0.322 at L=50. Linear theory gives 0.101, 0.194, 0.396, and implies L_half ≈ 1.6·k.
- **Sandbox script:** if Will adds `derivflow_modes.py`, it goes in `derivflow/modes/prior_look/` with a README marking it uncertified. Never import it.

## 3. Night 1

**Priority order if time runs short:** M0 → ML → MT → M3 at n=4096 → M3 at the other n. M6 rides along throughout. At the window edge, stop and bank whatever completed.

### M0 — resolve context, then one smoke cell (writes `derivflow/modes/MANIFEST_M0.json`)
- **M0.1 Git state.** Record HEAD, the branch list, and the clean-tree result.
- **M0.2 Production statistic.**
  - Locate the function that computes omr in `derivflow/` (grep `rtilde|r_tilde|gap_ratio|ratio.*min.*max`).
  - Record: file:line, the exact formula, which gaps it consumes, and how the bulk window is applied.
  - More than one candidate → STOP.
- **M0.3 Constants.** Resolve each of `KSTAR_LEVEL`, `FIT_WINDOW_MIN`, `BULK_FRACTION` to exactly one definition (file:line, value).
  - For BULK_FRACTION, also record whether it selects by root index or by position.
  - Conflicting duplicates → STOP.
- **M0.4 Seals and arms.** From the seal/verdict commits, record:
  - the seal JSON paths;
  - the three production arm names;
  - the sealed k grid (after amendment c986573);
  - the n grid (expected {1024, 2048, 4096, 16384});
  - the replicate count (expected 16).

  The commit chain is:

  | step | commit |
  |---|---|
  | v1 verdict | 4f29d70 |
  | artifact found | c235861 |
  | contamination measured | be7f2b9 |
  | corrected reference | 78ce01a |
  | Richardson amendment | c7275d3 |
  | downgrade | d6a7cff |
  | dense grid | c986573 |
  | RATE-SEED-DEPENDENT | 6cc2562 |
  | SCALE-FLAT | d629f6f (seal 889f472) |
  | disclosure pass | 505931c |
- **M0.5 Machinery.** Locate and record:
  - The derivative-root solver certified by the Hermite self-map gate: entry point and device.
  - The production reference:
    - entry point;
    - the ε_k rule, with its smoothing kernel stated explicitly (e.g. Stieltjes transform evaluated at height ε);
    - the Richardson pairing;
    - whether it exposes unfolded positions or only unfolded gaps;
    - whether its subordination routine accepts an analytic Cauchy transform in place of atoms. If it does not, POPREF is impossible → STOP.
  - The SeedSequence spawn scheme, the `seed_roster_beta` generator, and derivflow's Σ² routine.
- **M0.6 Precision.**
  - Locate what "int128" denotes in this repo (grep `int128|__int128|i128|Int128|INT128`). Record the module, its entry point, and which operations it covers.
  - If the certified solver or the reference has no int128 path → STOP and ask Will. Do not write a new arithmetic backend.
- **M0.7 Paper copies.** List every file containing `Local crystallization beneath` (git ls-files + grep): path, last commit, and whether it contains "Appendix D". Report only.
- **M0.8 Guards.** Read `spacings.py`, `lineage.py`, `errormodel.py`, `sealgen.sh`, `checkrun.sh`, and `.githooks/commit-msg`. Record:
  - how NOUNFOLD will be tagged (reference = none);
  - how shared roots across arms will be declared to `lineage.py`.

  If `spacings.py` cannot represent NOUNFOLD → STOP and propose a minimal extension. Never bypass the guard.
- **M0.9 Banking.** Determine whether per-replicate root sets are banked for the sealed cells (Appendix C mentions a gap).
- **M0.10 Smoke cell.** IID_UNIFORM, n = 4096, sealed replicates and sealed k grid.
  1. Reproduce the banked PROD_PRIMARY omr curve and k_star to the tolerance recorded in its artifact. If roots aren't banked, regenerate them from the sealed SeedSequence.
  2. If reproduction fails → STOP (instrument drift).
  3. Compute NOUNFOLD and POPREF on the identical roots.
  4. Time one step at n ∈ {1024, 4096, 16384}, project every Night 1 cell, and write the projection and any cuts into the manifest BEFORE ML runs.
- **M0.11 Commit** the manifest. Then follow AFTER_M0.

### Seal — `derivflow/modes/seal_night1.json` via `sealgen.sh`, committed before ML
The seal contains:
- every declared parameter, with KSTAR_LEVEL, FIT_WINDOW_MIN and BULK_FRACTION declared explicitly per `verify_declared_params.py`;
- the grids, tolerances and predictions below;
- the branch rules in §3.B;
- the hash of PRIOR_LOOK.md.

`verify_seal_order.py` must show the seal precedes every output it governs.

### ML — linear gain gate
- **Seeds:** LATTICE and LATTICE_WAVE(qw, A, phi = 0.3), at n ∈ {4096, 16384}.
- **Grids:**
  - qw ∈ {0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0}
  - A ∈ {1e-9, 1e-7, 1e-5, 1e-3, 1e-2, 1e-1}
  - k ∈ {1, 2, 4, 8, 16, 32, 64}
- **Measurement:**
  - Difference each wave run against the LATTICE run (same solver, same precision).
  - After k steps, root i of p^(k) sits at seed-index position i + k/2. Project the difference onto sin(qw·(i + k/2) + phi) over the bulk window, using a Hann taper.
  - Convert to local spacings using the LATTICE run's local gaps.
- **Prediction and pass rule:**
  - gain = (1 − qw/π)^k.
  - PASS if relative error ≤ 1e-3 for every A ≤ 1e-5 and qw ≥ 0.1, in cells where (1 − qw/π)^k ≥ 1e-8.
  - qw < 0.1 is report-only, because finite-n corrections of order k/(qw·n) are expected there.
  - Report the nonlinear-onset amplitude: the smallest A where relative error exceeds 1e-2.
- **Precision:**
  - A ∈ {1e-9, 1e-7} runs on the int128 path.
  - Every A also gets a float64 twin; report where float64 departs from int128.
- **Red path:** a solver that finds, per gap, the root of Σ_j sign(x − r_j)·|x − r_j|^(−1.2) = 0 must FAIL this gate. That solver exists only inside the checker's red-path test.
- **NOUNFOLD known answers** (no dynamics):
  - LATTICE: omr ≤ 1e-12.
  - LATTICE_WAVE with A = 1e-4 and qw ∈ {1.0, 2.0}: omr within 1% of (8A/π)·sin²(qw/2).
  - QLATTICE(semicircle at the GUE_DE normalization, t_flow ∈ {0, 64/n}): report NOUNFOLD omr at each n (the density-gradient floor, roughly 1/n). POPREF on the same must read ≤ 1e-10.
- **Existing gates, re-run unchanged:** Hermite self-map, lattice gate, picket fence, Gate D (`knownanswer.py`).
- **Any failure → STOP the night.**

### MT — transfer function of the production reference
- **Seeds:** LATTICE_WAVE(qw, A = 1e-5, phi = 0.3) and LATTICE, at n = 16384.
  - k ∈ {1, 2, 5, 10, 20, 40}
  - qw: the same grid as ML.
- **Arms:** PROD_PRIMARY, PROD_BW1, PROD_BW2, POPREF, RM1. Each run is unfolded against its OWN reference, built from its own seed, exactly as production does it.
- **Definition:** T = (complex projection of the difference in unfolded positions, wave run minus lattice run) ÷ (complex projection of the difference in raw positions, in local spacings).
  - If production exposes only unfolded gaps, unfolded positions are their cumulative sum (declared).
- **Expected:**
  - POPREF: |T − 1| ≤ 0.02.
  - RM1: |T| ≤ 0.05 for qw ≤ 0.1.
- **Sealed prediction for the PROD arms:**
  - T_pred = 1 − B·exp(k·[−ln(1 − qw/π) − qw/π]).
  - B is the arm's smoothing transfer at qw, taken from the kernel recorded in M0.5. For evaluation at height ε, B = exp(−qw·ε_sp), where ε_sp is the bandwidth in local spacings. B = 1 on the Richardson primary arm.
  - PASS if |T − T_pred| ≤ 0.1 for 0.1 ≤ qw ≤ 0.5. Every other qw is report-only; above 0.5 the continuum assumption is least credible.

### M3 — no-reference vs production on the sealed science grid
- **Cells:** IID_UNIFORM and GUE_DE × the sealed n grid × the sealed replicates and k grid, all on identical roots.
- **Arms:** PROD_PRIMARY, PROD_BW1, PROD_BW2, NOUNFOLD, POPREF.
- **The no-reference comparator per class:**
  - IID_UNIFORM → NOUNFOLD.
  - GUE_DE → POPREF, because the semicircle gradient biases NOUNFOLD by roughly 1/n.

  Report both arms for both classes regardless.
- **Bank per (class, n, arm):**
  - per-replicate omr at every k;
  - k_star by two labeled methods: (a) the production F3 fit, and (b) monotone log-linear interpolation of the ensemble mean;
  - p_tail over k ∈ [16, k_grid_max], report-only if k_grid_max < 48;
  - both error models (`errormodel.py`).
- **Lineage:** all arms within a cell share roots. Declare them non-independent to `lineage.py`.
- **Predictions (DECLARED-WITH-PRIOR-LOOK):**
  - comparator k_star > PROD_PRIMARY k_star in every cell;
  - NOUNFOLD k_star for IID_UNIFORM ∈ [20, 32] at every n;
  - NOUNFOLD p_tail for IID_UNIFORM ∈ [1.35, 1.65].
- **Sealed F3 ladder:** also run it on the comparators, labeled as a new object. Any new functional form needs its own seal later.

### M6 — interlacing witness (runs on every flow run)
- At every banked k, compute D_k = sup_x |F_{p^(k)} − F_seed|. Both CDFs are empirical, in original coordinates, each normalized by its own degree.
- Require D_k ≤ 2k/(n − k). This is a theorem, so the check must never fire.
- **Red path:** moving one root outside its Rolle bracket must fire.
- Report max D_k·(n − k)/(2k) per class, including GUE_DE.

### 3.B Branch rules (sealed)
1. ML fails, or M0.10 fails to reproduce → STOP.
2. On the smoke cell, if |k_star(NOUNFOLD) − k_star(PROD_PRIMARY)| ≤ 3σ_eff AND the p_tail values agree within 0.15:
   - the reference hypothesis is DEAD;
   - write a DROPPED ledger row with the reason;
   - Night 2 is cancelled.
3. Otherwise, if MT passes → recommend Night 2. It still needs Will's explicit go.
4. Otherwise (MT fails) → recommend a full MT characterization night instead.

### 3.C `derivflow/modes/NIGHT1_REPORT.md`, then STOP
The report contains:
- the manifest summary, including each ambiguity found and how it was resolved;
- gate outcomes;
- predictions vs results, each graded SEALED, DECLARED-WITH-PRIOR-LOOK or EXPLORATORY;
- which branch rule fired;
- the commit list;
- proposed verdict tokens:
  - GATE_ML_PASS or GATE_ML_FAIL
  - REFERENCE_IS_MACROSCOPIC or REFERENCE_ABSORBS_AND_INJECTS
  - NOUNFOLD_EXCEEDS_PRODUCTION or NOUNFOLD_MATCHES_PRODUCTION
  - INTERLACING_BOUND_HOLDS
- **Paper consequences, as proposals only:** a table covering k_star, the F3 form, the stretch mechanism, the SCALE-FLAT framing, and the roster reading.
- **Housekeeping that holds regardless of outcome:**
  - §1 still quotes o(n/log n);
  - the interlacing bound and GUE_DE coverage;
  - the paper copy that still leads with z(τ)/z(β) and has no Appendix D;
  - the folklore framing.

## 4. Night 2 — only on Will's explicit go after NIGHT1_REPORT.md

### 4.1 Seal `derivflow/modes/seal_night2.json`
The WIGNER_RENEWAL and SPEC_ALPHA cells are unseen, so their predictions are sealable.
- Disclose that the exponent law was formulated after the sandbox saw its alpha_spec = 0 and alpha_spec = 1 instances.
- Use new spawn keys that don't overlap any sealed science seeds, and record them in the seal.

### 4.2 Run matrix (n = 16384, k = 0…200)
- **Seeds and replicates:**
  - 16 each: IID_UNIFORM, WIGNER_RENEWAL, GUE_DE, BETA_HERMITE_1, BETA_HERMITE_4.
  - 8 each: SPEC_ALPHA(alpha_spec) for alpha_spec ∈ {−0.5, 0, 0.5, 1, 1.5, 2}.
- **Banked checkpoints:** k ∈ {0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 100, 128, 160, 200}.
- **At each checkpoint, bank:**
  - root sets as .npz with hashes;
  - omr for NOUNFOLD and POPREF;
  - a Hann-tapered periodogram of the POPREF gap fluctuations in the bulk window;
  - Σ²(L) on POPREF positions, for L ∈ {1, 2, 5, 10, 20, 50, 100, 200, 500}.
- **Cut order** if the M0 timing projects past the window:
  1. SPEC_ALPHA: 8 → 4 replicates.
  2. BETA_HERMITE_1/4: 16 → 8 replicates.
  3. k_max: 200 → 128.

  Never reduce n. Never cut WIGNER_RENEWAL or GUE_DE.

### 4.3 Seed constructions
- **`WIGNER_RENEWAL`:**
  - Draw i.i.d. gaps from P(g) = (32/π²)·g²·exp(−4g²/π) (mean 1, variance 3π/8 − 1).
  - Take the cumulative sum, then affine-map to [−1, 1].
  - The sampler in `cross_substrate/longrange_discriminator.py` may be imported read-only, but only if it passes a KS test against the analytic CDF at 1e6 draws (p > 0.01). Otherwise implement it in `derivflow/modes/seeds_modes.py`.
- **`SPEC_ALPHA(alpha_spec)`:**
  1. On the periodic grid of length n − 1, set S(qw) = |2·sin(qw/2)|^alpha_spec for qw ≠ 0, and S(0) = 0.
  2. ξ = real part of the inverse FFT of (complex white Gaussian noise × sqrt(S)).
  3. Normalize by the theoretical variance (the discrete Parseval mean of S over m ≠ 0), not per seed.
  4. Gaps: g = 1 + 0.2·ξ.
  5. If min g ≤ 0.05, reject the draw, take the next spawn key, and count the rejection.
  6. Take the cumulative sum, then affine-map to [−1, 1].
- **Matched families:** IID_UNIFORM, WIGNER_RENEWAL and SPEC_ALPHA share the uniform global law. GUE_DE and BETA_HERMITE share the semicircle law. Compare within a family first.
- **POPREF inputs** (analytic Cauchy transforms):
  - Uniform[−1,1]: G(z) = ½·log((z+1)/(z−1)).
  - Semicircle of radius R: G(z) = (2/R²)·(z − √(z² − R²)). Read R from the production GUE_DE normalization; never assume it.

### M4 — linear prediction and the exponent law
- **Linear prediction:** for each replicate and each k0 ∈ {0, 2, 5, 10, 20}:
  1. δ = POPREF-unfolded gaps of p^(k0), minus 1, over all gaps.
  2. Mirror-extend δ, multiply its FFT by (1 − qw/π)^(k − k0), and invert.
  3. Compute omr in the bulk window.

  The bar is relative error ≤ 5% for every k ≥ k0 + 2. Report k_lin = the smallest k0 that passes, per class (report-only).
- **Mode-resolved damping:** compare ⟨P(qw,k)⟩ / ⟨P(qw,0)⟩ with the band mean of (1 − qw/π)^(2k).
  - Bands: [0.02, 0.06], [0.06, 0.15], [0.15, 0.4], [0.4, 1], [1, 2].
  - Report where nonlinear refill appears.
- **p_tail:** computed on POPREF over k ∈ [50, 200].
- **Sealed predictions:**
  - SPEC_ALPHA: within ±0.15 of (3 + alpha_spec)/2, for every alpha_spec.
  - WIGNER_RENEWAL: within ±0.15 of 1.5, AND at least 0.3 below GUE_DE.
  - GUE_DE, BETA_HERMITE_1, BETA_HERMITE_4: each within ±0.15 of 2.0.
- **Rival (stated in the seal):** "local repulsion sets the tail" predicts p_tail(WIGNER_RENEWAL) ≈ p_tail(GUE_DE). Only WIGNER_RENEWAL can separate the two readings; the β roster cannot.

### M5 — the front
- L_half(k) = the smallest L with Σ²(L; k)/L ≥ 0.5, log-interpolated, for k ≥ 16.
- Fit L_half ∝ k^γ.
- **Prediction (DECLARED-WITH-PRIOR-LOOK):** γ = 1.0 ± 0.1, and for IID_UNIFORM, L_half ≈ 1.6·k within 20%.
- Also report how Σ²/L collapses when plotted against L/k.

### 4.4 `derivflow/modes/NIGHT2_REPORT.md`
- Same structure as the Night 1 report.
- Proposed tokens:
  - LINEAR_MODES_PREDICT_NOUNFOLD_CURVE
  - TAIL_EXPONENT_TRACKS_LONG_RANGE_SPECTRUM or TAIL_EXPONENT_TRACKS_LOCAL_REPULSION
  - FRONT_GROWS_LINEARLY_IN_K
- Paper consequences are proposals only. The paper decision is Will's.

## 5. Discipline (both nights)
- **Commits:** one per M-stage. A seal commit precedes every output it governs. Verdict tokens in commit messages are ALL-CAPS.
- **CHECKRUN lines:** only as written by `checkrun.sh`. Never typed, never read through a pipe, never older than 3 h, never superseded by a later run.
- **Every banked number** has a committed generator, plus a checker registered in `verify_all.py`.
- **Declared parameters:** every threshold, window, bandwidth, taper and inclusion rule. A sweep is a declared cell, never a follow-up.
- **Error models:** both, always.
- **Precision:** don't bank digits beyond what the dispersion supports.
- **On ANY ambiguity** about which file, function, constant, arm, seed or precision path is meant: STOP and ask Will. A guess is a failure, not a shortcut.
