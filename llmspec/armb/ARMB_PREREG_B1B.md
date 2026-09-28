# Arm B pre-registration — Part B1b: Q1–Q4 tests (rev 2, after Will's 09-27 review)

**Status: B1b SEALED 2026-09-27 ~16:45**, before any arm has trained a step and before the full licence runs.

**Frozen with this seal** (sha256, first 16 hex characters):
- `q1_models.py` cb4a5685aef90b85
- `q1_licence.py` dbbb4440a2b4a7c6
- `q1_warp.py` ca98707fa01b8deb
- `q2_licence.py` 9b19cf60083a9b06
- `bulk_power_70m.py` 8817483bc554b39c

**Disclosed pre-seal smoke runs** (synthetic only, used to exercise the code, no rule tuned on them):
- q1_licence at 5 draws per cell. This revealed E1's kink bias and led to (a) adding E3 and the smooth-U family, and
  (b) replacing CI coverage with e(σ), per Will's review.
- q1_warp at 40 draws per cell: licensed at low noise, not at ≥ 2%.
- q2_licence at 5 draws per cell.

**Analysis code** for Q1–Q4 on real arms (extraction and scoring) is written and committed before B4 reads any arm
beyond the B-G1 gate. It must implement exactly these rules; any gap is a dated amendment.

**Common rules.**
- Parent: ARMB_PREREG.md (B1a sealed 01fc4b5; amendment A1 f04fe17).
- Status vocabulary as in FINDINGS_MEMO.md.
- All statistics come from fp32 masters, with Stage 3's estimator versions unchanged (G5 columns plus `arm`).
- Per-head local statistics: ⟨r̃⟩ only (memo §4, S4).
- **Arms** (B1a-A1):

  | arm | warmup W | init | data order | stop |
  |---|---|---|---|---|
  | A0 | 1430 | pythia-70m step0 | Pythia | 5000 |
  | A1 | 2860 | pythia-70m step0 | Pythia | 5000 |
  | A2 (REQUIRED) | 715 | pythia-70m step0 | Pythia | 3000 |
  | M0-s1 | Pythia schedule, Muon | pythia-70m step0 | Pythia | 3000 |
  | M0-s2 | Pythia schedule, Muon | pythia-70m-seed1 step0 | seed-1 index maps | 3000 |

- Every AdamW arm is a paired run, so seed spread does not enter Q1. The uncertainty of every timing quantity is the
  estimator's LOCALISATION ERROR, taken from its known-answer licence.

## Q1 — LR confound: what anchors the turning points?
### Metrics (operational; all listed now)
- **Primary** (Stage 3 §3: the 1.4B "rebound after ~2k"):
  - **TP_O:** the turning point of the layer-mean stable rank ‖W‖_F²/‖W‖₂² of `attention.dense` (O) along an arm's
    full checkpoint grid.
  - **TP_MLPOUT:** the same for `mlp.dense_4h_to_h`.
- **Turning point:** an interior minimum in [300, stop − 250], followed by a sustained rise, as defined operationally
  by the licensed estimator.
- **Secondary (descriptive only, no verdict):** the same for Q, K, V, MLP_IN; also the turning point of the ΔW update
  rank over consecutive grid intervals.

### Models (sealed as formulas in `armb/q1_models.py`)
Given A0's turning point t₀, arm X's predicted turning point under each anchor is:

| model | anchored to | prediction P_X |
|---|---|---|
| STEP | a fixed step | t₀ |
| WARMUP | warmup end + a fixed offset | t₀ + (W_X − 1430) |
| LR_INT | cumulative applied LR | the smallest t with Λ_X(t) ≥ Λ_0(t₀) |

- Λ(t) = Σ_{k≤t} lr(k−1), using the sealed LR function.
- Illustration only (t₀ = 2000): A1 → 2000 / 3430 / 2712; A2 → 2000 / 1285 / 1643. The code reproduces the reviewer's
  table.
- The smallest inter-model gap is ≈ 357 steps for A2 and ≈ 715 for A1 when t₀ ≥ 1500 (q1_models.py table).

### Uncertainty and decidability (sealed before data)
- **e(σ)** = the 98.75% quantile of |t̂ − t_true| for the licensed estimator. It is the worst case over the licence's
  shape classes (kinked, smooth and plateau minima) at relative noise σ.
  - 98.75% = 1 − 0.05/4: a Bonferroni family-wise allowance over 2 primary metrics × 2 arm comparisons.
  - The licence runs 1000 draws per cell, so this quantile is estimated from ≈ 12 exceedances. That precision is
    stated with it.
- **Noise level σ_X:** each arm's relative residual SD about the licensed estimator's smooth fit (a measurement of
  noise, not of the effect). The licence row at the next-higher σ applies.
- **Combined error for arm X under model m:** e_c = √(e(σ_X)² + (∂P_m/∂t₀ · e(σ_0))²).
  - ∂P/∂t₀ = 1 for STEP and WARMUP; the LR-ratio for LR_INT (q1_models.py).
- **Decidability (sealed):** Q1 is DECIDABLE for arm X iff e_c ≤ (smallest inter-model gap for arm X)/3, so the three
  intervals P_m ± e_c do not overlap and are each separated by ≥ e_c.
  - The gap depends on t₀, which comes from data. So the rule is the pre-computed table of the gap vs t₀ and e_c vs σ
    in q1_models.py / the licence output, read off once t₀ and σ are measured.
  - If it isn't decidable, Q1 for that arm and metric is **DESCRIPTIVE**, and that is stated.
  - If no estimator is licensed at the measured σ, Q1 is DESCRIPTIVE for that metric.

### Decision (per primary metric) — PRIMARY route: E4 warp-and-compare (Will 09-27: approved in this form only)
- **E4** (`armb/q1_warp.py`). For each arm X ∈ {A1, A2} and each model m:
  - map A0's curve through m's time map τ_m (STEP: t; WARMUP: t − ΔW; LR_INT: Λ₀⁻¹(Λ_X(t)));
  - rescale heights by an affine least-squares fit;
  - compute the SSE against X's actual curve over the window common to all three maps (A1: [1450, 3000];
    A2: [300, 2275]).
  - The pure-shift registration is NOT used.
- **Per (arm, metric):**
  - **NO SIMPLE ANCHOR** iff SSE_best/(n·s²) > c_fit;
  - otherwise **SUPPORTED(best model)** iff SSE_second/SSE_best ≥ r*;
  - otherwise **INCONCLUSIVE**.
  - s is the pooled relative noise of A0 and X, measured about their own smooths. c_fit and r* are fixed per (arm,
    noise level, noise type) by the licence.
- **E4 licence (confusion matrix, synthetic, before data).**
  - Arm curves are generated under each true model, plus a HALFWAY truth that matches no model, with amplitude
    changes and noise on both curves. 500 draws per cell.
  - r* = the smallest value in {1.0, 1.1, 1.25, 1.5, 2.0} with every wrong-model rate ≤ 5% and HALFWAY → any single
    model ≤ 20%.
  - LICENSED iff at r* every true-model rate ≥ 80%.
  - The licence row for the measured noise level (next-higher) applies.
- **Overall Q1 verdict per metric:**
  - **Model m SUPPORTED** iff E4 SUPPORTS m in every licensed arm, and in at least one arm.
  - **CONFLICT** if the arms support different models.
  - **NO SIMPLE ANCHOR** if any licensed arm says so.
  - **DESCRIPTIVE** if no arm is licensed at its measured noise.
- **Secondary route (location-based, reported alongside, and used only if E4 is not licensed for an arm).** The t̂
  intervals and decidability rule above, with model m CONSISTENT iff |t̂_X − P_m| ≤ e_c.
  - SUPPORTED iff it is CONSISTENT in every decidable arm and every other model is INCONSISTENT in at least one.
  - NO SIMPLE ANCHOR iff every model is inconsistent somewhere. Otherwise INCONCLUSIVE.
- **If A0 has no turning point:** Q1 location-based is NOT APPLICABLE AT 70M. E4 still compares whole curves, since a
  time map can anchor any trajectory; that is reported, and the verdict is labelled "anchor of the trajectory, not of
  a turning point".
- **A turning point present in A0 but absent in A1/A2** (or vice versa): reported as such.

### Estimator licence (`armb/q1_licence.py`, synthetic, run before any arm data)
- **Families** on each arm's exact grid:
  - (a) no turning point: monotone decreasing curves;
  - (b) planted minima, both KINKED (the shape an LR kink at warmup end would make) and SMOOTH, with t₀ ∈ {800, 1500,
    2200, 2900}, depths 5/15/40% and asymmetric rises;
  - (c) plateaus.
- **Noise:** relative σ ∈ {0.5, 1, 2, 5}%, i.i.d. and AR(1) with φ = 0.5.
- **Licence criteria:**
  - false "turning point" on (a) ≤ 5%;
  - detection on (b) ≥ 80% at depth ≥ 15%;
  - e(σ) reported per family and cell.
- **No coverage criterion.** The earlier bootstrap-CI coverage requirement is replaced by e(σ), taken directly from
  the known-answer error distribution, per the review.
- **Candidates:**
  - E1: Savitzky–Golay argmin;
  - E2: local quadratic in log-step;
  - E3: asymmetric parabola by profile least squares;
  - (E4, the warp-and-compare estimator, is the PRIMARY route above, with its own licence.)
- Among the licensed candidates, the one with the smallest worst-case e(σ) at each σ is used, fixed by the licence run.

## Q2 — ordering the events in steps 256–2000
- **Events** (on A0; M0 descriptive), each the first grid step at which its trajectory crosses its threshold:
  - E_ind: max induction score ≥ 0.3.
  - E_OV / E_QK: ≥ 50% of heads outside the product-Ginibre band.
  - E_MP(Q) / E_MP(K): MP KS > witness KS95 in ≥ 90% of layers.
  - E_sr(M): layer-mean stable rank ≤ ½ its step-0 value.
  - E_loss: text-probe loss below the midpoint of the step-0 loss and the step-3000 loss.
- **Uncertainty = localisation error of the crossing time, from a known-answer licence** (`armb/q2_licence.py`). Synthetic
  monotone and sigmoidal trajectories with planted crossing times on the A0 grid, at matched relative noise, give
  e_x(σ), the 95% quantile of |error|.
  - NOT a head/layer bootstrap: within one run that captures only within-run spread, and Stage 3 showed heads cluster by
    run × layer.
- **Ordering:** E_a PRECEDES E_b iff [t_a ± e_x] and [t_b ± e_x] do not overlap and t_a < t_b. Otherwise SIMULTANEOUS
  AT THIS RESOLUTION.
- **Sealed pairs:** E_OV vs E_QK; E_OV vs E_ind; E_QK vs E_ind; E_sr(Q) vs E_sr(V); E_MP(Q) vs E_ind. Every pair is
  reported.

### Layer-ordered compression wave (Liu, arXiv 2604.22778: "Stable-rank compression travels as a wave from early to late layers … Q/K matrices carry the depth-dependent dynamics while V/O compress uniformly")
- t_half(M, L) = the first grid step at which layer L's stable rank of type M ≤ ½ its step-0 value.
- **Primary (one test, one-sided, in Liu's direction):** S = ρ_Q + ρ_K (Spearman of layer index 0–5 vs t_half, ties
  averaged). The exact null permutes layer labels independently per type (720² orderings). Types are POOLED into this
  one statistic, as declared now.
- **Verdicts:**
  - **Liu REPLICATES** iff one-sided p < 0.05 AND ρ_Q > 0 AND ρ_K > 0.
  - **OPPOSITE ORDER** iff the lower-tail p < 0.05.
  - Otherwise **NOT RESOLVED**.
- V and O: ρ reported, no test.
- **Power declared now:** with 6 layers, even a perfect ordering in ONE type gives p ≈ 0.0014 on its own, and a
  moderate wave (true ρ ≈ 0.5 per type) is not detectable. **A NOT RESOLVED result at 70M is a bounded null, not
  evidence against Liu.**

## Q3 — are early updates low-rank?
Unchanged from rev 1:
- Two matched comparisons, (S) equal steps and (L) equal LR integral, both conservative.
- **LOW-RANK EARLY** iff the early/late ratio of ΔW stable rank is ≤ 0.5 in ≥ 4 of 6 types in both comparisons.
- **NOT LOW-RANK EARLY** iff the ratio is ≥ 0.8 in ≥ 4 of 6 types in both. Otherwise INCONCLUSIVE.
- Change: uncertainty is not a layer bootstrap. Ratios are reported per layer (6 values) with their range, and the
  verdict rests on the type counts as sealed.
- A0 is primary; A1 and A2 are descriptive.

## Q4 — AdamW vs Muon: two independent paired differences
- **Pairs:**
  - P1 = M0-s1 − A0, on the full dense grid (and M0-s1 − released Pythia-70M at the shared steps).
  - P2 = M0-s2 − released pythia-70m-seed1, at the shared steps only.
  - These are two genuinely independent paired differences: different init, different data order.
- **Two pairs = one degree of freedom for the spread.** Q4 can therefore only claim effects that are LARGE and
  CONSISTENT in both pairs:
  - **OPTIMIZER-DIFFERENT** at a (metric, step) iff d₁ and d₂ have the same sign AND |d_i| > T · s_ref for both. Here
    s_ref is the AdamW seed SD at that step (B-G1 band, n = 10), and T = the B-G1 Bonferroni t over the Q4 family
    (metrics × shared steps).
  - Everything else is reported DESCRIPTIVELY. No Welch test is run on 2 pairs.
- **Metrics:** layer-mean stable rank, spectral entropy (normalised Shannon of σ²/Σσ²), Frobenius norm and top σ per
  type; ΔW update rank; probe loss.
- **Bulk null under Muon:** see "Bulk null power" below; the same rule applies to M0.
- **Q2 event times** in M0 vs A0: descriptive, with the Q2 localisation intervals.

## Bulk null power at 70M (computed pre-data: `armb/bulk_power_70m.py`, results/armb_bulk_power_70m.json)
- **Witness at 70M shapes** (fp16-rounded Gaussians, s3stats bulk band, R = 40 pools). One checkpoint's pool has ≈ 2,400
  spacing ratios. SD of bulk ⟨r̃⟩: full 512² 0.0073, MLP 0.0063, per-head Q/K/V 0.0055, per-head O 0.0074.
- **Minimum detectable departure** (one-sided α 0.05, power 0.80) = 0.018 / 0.016 / 0.014 / 0.018. **This exceeds the
  sealed Stage 3 tolerance of 0.010 in every cell type: the 0.010 null is NOT POWERED at 70M.**
- **Rule at 70M:** a cell reads HOLDS AT MDD m (no departure larger than its MDD m) or VIOLATED (|Δ⟨r̃⟩| > m). No cell
  may be reported as holding at 0.010. VIOLATED cells go to the ladder (density-matched witness, licensed ⟨r̃⟩
  calibrator from S4).
- **No pooling of adjacent checkpoints.** Checkpoints 10–25 steps apart are nearly the same matrices; their spacings are
  not independent, and pooling them would manufacture power. Declared.

## What would change these plans (pinned now)
- **B-G1 fails:** nothing here is read.
- **The Q1 licence yields no estimator, or no arm is decidable:** Q1 is descriptive, and says so.
- **The M0-s2 data reconstruction fails its seed0 known-answer check:** M0-s2 is BLOCKED and Q4 falls back to P1 alone,
  DESCRIPTIVE only.
- **E4** is approved (Will 09-27) ONLY as warp-and-compare. No pure-shift estimator is used anywhere.

## B4 amendment — 2026-09-28 ~10:30: the analysis code is SEALED before it reads any arm statistic beyond the B-G1 gate metrics
**Frozen** (sha256, first 16 hex characters):
  - `armb/b4_extract.py` af6e4678145c9706
  - `armb/b4_analyze.py` 2a47aa552dda36d8
  - `mcfg.py` 40fc8f6bc0467a76
  - `armb/test_b4_dryrun.py` ca3750a0dd109941

**What the code is.**
- **Extraction** (`b4_extract.py`, GPU only).
  - Stage 3's `layer()` and `markers()` are imported unchanged: estimator versions stage3-extract-v1 and
    stage3-markers-v1.
  - They run on every arm checkpoint, pulled from spot and sha256-checked against its `.ok` marker. fp32 masters stay
    fp32.
  - They also run on the 10 reference runs at the shared steps, through Stage 3's own `run()`, plus pythia-70m
    step143000, which is the rms source that `stage3_witness.py` needs for the 70M witness.
  - ΔW stable ranks are computed for the sealed Q3 and Q4 intervals.
- **Analysis** (`b4_analyze.py`): Q1–Q4 and the bulk null, as B1b rev 2 words them.

**Operational choices, declared now** (all appear in the code docstring):
- **Noise:** SD of the residual about a Savitzky–Golay smooth (window 9 for Q1, window 5 for Q2; order 2). Relative
  for stable rank and loss; absolute for fractions.
  - A lag-1 autocorrelation above 0.25 selects the AR(1) licence row. The next-higher tabulated level applies.
  - Noise above the largest level means NOT LICENSED.
- **Q2 intervals:** the licence's WORST-SHAPE 95% quantile (the conservative choice).
- **Loss:** E_loss and Q4's loss use the Stage 3 text probe (`MARKERS.npz` loss_text).
- **Wave:** a layer that never crosses is ranked last.
- **Q3 (L) intervals:** built on A0's schedule for every arm. They are primary for A0 only; A1 and A2 are descriptive.
- **Bulk ladder:** DENSITY_ARTIFACT iff |d_obs − d_density| ≤ MDD. The calibrator is the S4-licensed v2_c16.
- **Q4 family:** (4 metric kinds × 6 types + loss) × 14 shared steps + 3 intervals × 6 types = 368, giving
  T = t₉ Bonferroni = 6.33.

**Scope the sealed licences already imply** (derived from the synthetic licence runs; arm data not involved):
- **E4 (warp-and-compare)** is licensed ONLY for A2 at trajectory noise ≤ 0.5%, and never for A1.
- **Location route:** E1 is licensed on the 3000-step grid, but its worst-case localisation error is 425–1075 steps,
  against the ≤ 119 (A2) and ≤ 238 (A1) that decidability needs. Nothing is licensed on the 5000-step grid.
- **Consequence:** Q1 can reach a model verdict only through E4 on A2, and only if A2's stable-rank trajectories are
  smoother than 0.5% relative noise. Otherwise Q1 is DESCRIPTIVE.
- **Q2 crossing intervals:** ±25 to ±375 steps, depending on noise.

**Dry run** (`test_b4_dryrun.py`; fabricated cache; NO arm data): every branch was exercised.
- **Q1 planted known answer:** a warmup-anchored truth gives SUPPORTED: WARMUP on both metrics, via E4 on A2.
- **Q2–Q4:** ran; the planted precedences were recovered.
- **Bulk:** the HOLDS branch, and a forced-violation branch that sent 30 cells through the ladder and produced both
  labels. CHECKRUN armb/test_b4_dryrun.py EXIT=0 PASS.

**Arm data seen before this seal (disclosed):**
- the per-step training logs (loss, lr, grad norm, loss scale, update norms) in liveness checks;
- the B-G1 gate metrics and verdicts (probe loss, stable rank and Frobenius norm at the shared steps) for A0 and the
  aborted/failed runs.
- No B4 extraction has run and no Q1–Q4 statistic exists.

## Q1 E4 licence v2 — 2026-09-28 ~15:20 (Will's sign-off; pre-data; sealed BEFORE it runs and before B4 reads any arm)
Full rule: the `armb/q1_warp_v2.py` docstring (sha256 6f25590574f06dbe).
1. **HALFWAY is retired.** After both warmups it equals the LR_INT map (a shift of ΔW/2), so v1 tested E4 against a copy
   of a hypothesis. The diagnosis is in b121908.
2. **Confusers per arm:** the MIDPOINT maps between adjacent model maps (STEP↔LR_INT, LR_INT↔WARMUP), plus a 1.3t stretch
   and an overshoot by 1.5·ΔW. The cap is unchanged: any confuser assigned to a single model ≤ 20%. Wrong-model rate
   ≤ 5%; true-model rate ≥ 80% at r*.
3. **"No model fits" outcome.** E4 has one (NO_SIMPLE_ANCHOR, via c_fit). It is LICENSED only if it fires on BOTH
   midpoint confusers at ≥ 80% at r*.
   - Verdict wording: a SUPPORTED(X) is reported as "X-driven" only where NO_SIMPLE_ANCHOR is also licensed. Otherwise
     it is "the closest of the three models is X".
4. **E4 itself is unchanged.** Grids and windows come from `grids.arm_grid` (A2 dense, B1a-A8). The re-run is on spot
   for A1 and A2.
5. **B4 wiring:** `b4_analyze.py` switches to the v2 licence, the wording rule and `arm_grid`, via a dated B4
   amendment with a new dry run, before any extraction.

## B4 amendment 2 — 2026-09-28 ~16:00: B4 is RE-SEALED against E4 licence v2 and the arm grids (pre-data: no B4 extraction has run)
**Frozen** (sha256, first 16 hex characters):
  - `armb/b4_extract.py` 9527554f4160d1ab
  - `armb/b4_analyze.py` c6f3e47282b9c32a
  - `armb/grids.py` 8354daa9d4569d65
  - `armb/q1_warp_v2.py` 6f25590574f06dbe
  - `armb/test_b4_dryrun.py` c2a74541006088a4

**Changes:**
- `b4_analyze.py` reads the v2 licence cells (`results/armb_q1_warp_licence_v2.json`, a64d71f).
- The sealed wording rule applies:
  - "X-driven" only where NO_SIMPLE_ANCHOR is licensed; otherwise "the closest of the three models is X";
  - an unlicensed NO_SIMPLE_ANCHOR decision is reported INCONCLUSIVE.
- Extraction and analysis both take grids from `grids.arm_grid` (A2 dense, B1a-A8). E4's window uses the arm grids
  (via q1_warp_v2).

**Dry run** (fabricated cache): every branch passes.
- The planted warmup-anchored truth is reported as "SUPPORTED: WARMUP-driven" via E4 on A2.
- The forced bulk-violation ladder produces both labels.
- CHECKRUN armb/test_b4_dryrun.py EXIT=0 PASS.

**Arm data seen:** unchanged from the first B4 seal (training logs and B-G1 gate metrics only).
