# Arm B pre-registration — Part B1b: Q1–Q4 tests (rev 2, after Will's 09-27 review)

**Status: DRAFT, not sealed.** It is sealed together with `q1_models.py`, `q1_licence.py` (Q1 + Q2 localisation licences)
and the analysis code, before A0's first optimizer step. Changes after any arm trajectory has been seen are dated
amendments, labelled post-hoc.

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

### Decision (per primary metric)
- **If A0 has no licensed turning point:** Q1 is **NOT APPLICABLE AT 70M** for that metric. That is a size finding
  against the 1.4B rebound.
- **For each decidable arm X ∈ {A1, A2}:** model m is CONSISTENT iff |t̂_X − P_m| ≤ e_c, INCONSISTENT otherwise.
- **Model m is SUPPORTED** iff it is CONSISTENT in every decidable arm AND every other model is INCONSISTENT in at least
  one decidable arm.
  - **NO SIMPLE ANCHOR** iff every model is INCONSISTENT in some arm.
  - Otherwise **INCONCLUSIVE**.
  - With only one decidable arm, a verdict can still separate models whose predictions differ in that arm, and this is
    stated.
- **A turning point present in A0 but absent in A1 or A2** (or vice versa): reported as such, with no model verdict for
  that arm.
- This replaces the earlier "slope ≈ 0 / ≈ 1" bands. The three models' predictions ARE the numeric, non-overlapping
  bands, and the decidability rule enforces their separation.

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
  - E4: registration shift of arm X onto A0 around the rebound. E4 gives t̂_X − t₀ directly. It is used ONLY with
    Will's sign-off (a method change from "measure turning-point steps") and is licensed the same way, on synthetic
    shifted pairs.
- Among the licensed candidates, the one with the smallest worst-case e(σ) at each σ is used, fixed by the licence run.

## Q2 — ordering the events in steps 256–2000
- **Events** (on A0; M0 descriptive), each the first grid step at which its trajectory crosses its threshold:
  - E_ind: max induction score ≥ 0.3.
  - E_OV / E_QK: ≥ 50% of heads outside the product-Ginibre band.
  - E_MP(Q) / E_MP(K): MP KS > witness KS95 in ≥ 90% of layers.
  - E_sr(M): layer-mean stable rank ≤ ½ its step-0 value.
  - E_loss: text-probe loss below the midpoint of the step-0 loss and the step-3000 loss.
- **Uncertainty = localisation error of the crossing time, from a known-answer licence** (in q1_licence.py). Synthetic
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
- **E4 (registration) without Will's sign-off:** E4 is dropped from the candidates before the licence runs.
