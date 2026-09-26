# Stage 3 findings — Pythia-1.4B trajectory (brief v1.1 aims 2–6)

- **Pre-registration:** STAGE3_PREREG.md, sealed at 0cf53ba.
- **Amendments:**
  - A0 (pre-data): long-range unfolding switched to kde(32).
  - A1 (post-hoc): mp_fit_v1 collapses on non-MP bulks, so mp_fit_v2 was added.
- **Data:** 26 revisions (0, 1, 2, …, 512, 1k … 143k), all extracted with none missing. Streamed; exact fp64 SVD.
- **Outputs:**
  - results/stage3_long.parquet (G5 columns), stage3_null.json, stage3_changepoints.json, stage3_event_table.json.
  - plots/stage3_*.png (regenerate with stage3_report.py).
- **Scope:** one model, one seed. Replication (G3: sizes, PolyPythias seeds, OLMo) has NOT been done. Every
  statement below is about Pythia-1.4B only.

## 1. Sealed null (aim 6) — HOLDS, 260/260 cells
- **Claim tested.** Bulk ⟨r̃⟩ and bulk Brody q stay at the pooled-null (β=1) witness value at every checkpoint.
  - Covers 26 checkpoints × {Q, K, V, O, MLP_IN, MLP_OUT full matrices; Q, K, V, O per-head}.
  - Tolerances: |Δ⟨r̃⟩| ≤ 0.010 and |Δq| ≤ 0.10.
- **Result:** HOLDS in all 260 cells.
  - Worst |Δ⟨r̃⟩| = 0.0040 (MLP_OUT). Worst |Δq| = 0.034 (per-head Q).
  - Largest by type: |Δ⟨r̃⟩| 0.0022–0.0040; |Δq| 0.012–0.034.
- **Licensing gates.**
  - G1 witness: 10 types, R = 20, fp16-rounded at the real rms. It reads β=1: bulk ⟨r̃⟩ 0.5304–0.5311, q 1.007–1.011,
    all scale-invariant.
  - G0 at step 0: MP KS passes for all six types (≤ 4 of 24 matrices above the witness KS95; binomial p ≥ 0.03).
  - The instrument can fire: Poisson levels read ⟨r̃⟩ ≈ 0.39 (verify_s3stats.py), a violation of ~0.14.
- **Reading.** This is the pre-registered instrument check, confirmed. The bulk nearest-neighbour statistics are
  β=1 throughout training, matching Staats–Thamm–Rosenow and arXiv 2603.27885 on a 1.4B model. It is a null and is
  reported as one: it says nothing about edges, long-range statistics or vectors.

## 2. Precision (G4)
- Pythia's stored values are fp16 (100% on the fp16 grid). fp16 rounding moves bulk ⟨r̃⟩ by ≤ 0.0017 in every
  witness type.
- **Lower band.**
  - As sealed, lower-band statements are PRECISION_LIMITED for K (+0.0042), V (−0.0026) and MLP_IN (−0.0024),
    against a 0.002 bar.
  - Qualification: that rule compares a 20-replicate mean with a 5-replicate mean and has no sampling allowance.
    The lower-band replicate SD is ~0.002–0.004, so these excesses are within noise. The label stands as sealed.

## 3. Edges (aim 2) — descriptive (mp_fit_v2; mp_fit_v1 is DEGENERATE for trained Q/K and is not used)
- **Upper-edge outlier detachment** (σ > τ₊ × MP edge, median-matched scale; layer means):
  - The output side detaches first:
    - O: 0.5 → 40 at step 512 → 311 at step 2000 → 152 at the final step.
    - MLP_OUT: 0 → 37 → 398 → 160.
  - Both rise to a peak around step 2000, then fall back.
  - Q and K detach later and monotonically: 5 at step 512, 60 at 2000, 250 at the final step.
  - V is last: 0.7 at step 512, 23 at 2000, 160 at the final step.
- **Lower edge.**
  - Rectangular MLPs: departures below the MP lower edge appear in MLP_OUT by step 1000–2000 (77 at step 2000) and in
    MLP_IN later and growing (25 at 8k, 82 at the final step).
  - Square Q/K/V/O: the lowest-10% KS against MP stays at the witness floor (0.058) until about step 2000 (O) and
    about step 8000 (Q, K). It then rises to 0.24–0.26 for Q/K and 0.13–0.15 for V/O.
  - **Precision check (added 23:35, a bound rather than a simulation): the rise is NOT precision-limited.**
    - The fp16 rounding error matrix has ‖E‖₂ ≲ u·rms·(√m+√n) with u = 2⁻¹¹.
    - The lowest-decile σ sit 44–80× above that bound at step 0, 8k and 143k (median of the lowest decile, all four
      types). Only the few very smallest σ reach it.
    - By Weyl's inequality, rounding moves those σ by ≤ 2.3%, which shifts the lowest-10% KS by roughly ≤ 0.01. The
      observed rise is ~0.19.
    - The prereg's premise ("smallest σ ≈ 0.02 rms, below the fp16 floor") is true of the minimum σ, not of the
      decile this statistic uses.
- **Stable rank** (layer means):
  - Q/K/O/MLP_OUT collapse between steps 128 and 2000 (Q 515 → 36; K 514 → 40; O 514 → 79; MLP_OUT 913 → 111).
  - V collapses later: still 493 at step 1000, 237 at 8k.
  - **Non-monotone:** O and MLP_OUT rebound after step 2000 (O 79 → 168; MLP_OUT 111 → 227) while Q/K stay
    compressed (37–47).
- **Compression wave (aim 5, Liu):** not resolved.
  - Per-layer time to half the initial stable rank shows no significant layer ordering: Spearman ρ = +0.17 (Q),
    +0.38 (K, p = 0.07), +0.10 (V), +0.04 (O).
  - Q/K/O/MLP compress between 256 and 2000 steps, where the schedule has only 512 / 1000 / 2000. That is too coarse
    to see a wave, so this is **not** a null replication of Liu.
  - V compresses over 3k–12k, where Pythia has 1000-step checkpoints. A denser V run is queued.
- **MLE α** (htsr_mle_v1; quoted only where the bootstrap p ≥ 0.1):
  - The power-law fit fails at init (MP) for every matrix.
  - Fits become acceptable by 2k–8k steps for Q, K, MLP_IN and MLP_OUT. The fail fraction at the final step is
    0.08–0.29 for those four; V fails in 71% of layers and O in 21%.
  - Final α (valid layers only): Q 3.53, K 3.47, MLP_IN 3.47, MLP_OUT 4.99, O 6.46, V 7.79.
  - Not comparable to Liu's rank-slope exponent (G6). The rank-slope (liu_rankslope_v1) is plotted separately and
    labelled.

## 4. Vectors (aim 4) — descriptive
- **Upper-band left singular vectors of Q, K and V localise over training.**
  - Porter–Thomas KS median 0.017 → 0.036–0.038 (Q/K), 0.025 (V).
  - IPR × dim 3.0 (random) → 3.9–4.1 (Q/K), 3.5 (V).
  - Timing: from about step 2000–8000 on.
- **O and MLP_OUT upper-band vectors stay delocalised** (PT KS 0.014, IPR × dim 3.01–3.03).
- **Top-8 left-subspace overlap with the final checkpoint** grows gradually:
  - At step 8k (5.6% of training): MLP_IN 0.69, MLP_OUT 0.50, K 0.48, Q 0.43, O 0.32, V 0.26.
  - "Top vectors stabilise early" (Yunis et al.) holds for MLP_IN more than for O/V here; descriptive only.

## 5. Circuits (aim 3) — descriptive
- LayerNorm gains are folded in; centering and biases are ignored (declared).
- **Copying score** (Elhage, full OV circuit): median head ≈ 0 throughout. The top decile rises from 0.04
  (step 512) to 0.16 (1000) to 0.27 (2000) to 0.31–0.35 afterwards, i.e. copying heads appear with induction
  formation.
- **OV eigenvalue score** (residual basis, no embeddings): median head strongly negative (−0.44 at step 512, −0.96 at
  2000), recovering to −0.33 by the end. The top decile turns positive after step 8000 (0.93 at the end).
- **QK symmetric-energy fraction** (non-rotary dims 32–127): median 0.50–0.52 throughout. The top decile reaches 0.70
  at step 2000, then settles at 0.54.
- The product-Ginibre null is not yet computed; step 0 serves as the empirical null (≈ 0.50 / 0.00).

## 6. Motion — descriptive
- ΔW between consecutive revisions is **low-rank early and high-rank late**.
  - Stable rank of ΔW: Q 2.7 → 4.7 → 12 → 20 (steps ≤ 2000), then 95 → 234 → 162.
  - The same pattern holds for every type.
- The fraction of ‖ΔW‖² in W's top-32 left subspace exceeds the isotropic baseline (32/2048 = 0.016; 32/8192 for
  MLP_IN) by 3–9×, peaking around step 2000 for Q/K (0.14).
- Q's last interval (128k → 143k) rises to 0.17. That is the tail of the LR schedule; no interpretation is offered.

## 7. Events and markers
- **Induction formation: between steps 512 and 1000.**
  - Max induction attention 0.01 → 0.91; repeated-sequence second-half loss 12.8 → 3.6.
  - Pythia has no public checkpoints in between, so this interval is the resolution limit.
- **First sink head** (mean attention to position 0 > 0.5): between 48k and 64k (1/384). The mean attention to
  position 0 rises from 0.007 to 0.20.
  - The brief's "sink precedes/follows induction by 10–20× in tokens" comparison: the first sink head arrives
    ~50–100× later than induction under this sink definition. That definition is strict (> 0.5); the mean-sink
    trajectory is the fairer comparison and is in plots/stage3_markers_circuits.png.
- **Many metrics change in the same interval.** Stable-rank collapse of Q/K/O/MLP, O/MLP_OUT outlier detachment,
  copying-score onset and the loss drop all occur between steps 256 and 2000, bracketing induction formation. With
  only 512/1000/2000 in that window, this data **cannot order** those events.
- **Change points are descriptive only.** BIC binary segmentation flags ≥ 1 change in 270/337 series. No null was
  calibrated for it, and smooth curvature in log-step produces breaks. No alignment claim rests on change points.

## Queue / Will's calls
- **G2 functional witness** (Diffract replication) is running (stage3_g2.py, pre-registered 0970140).
- **Denser V trajectory** (1000-step checkpoints over 2k–16k) to resolve a V-compression wave, if wanted.
- **Product-Ginibre circuit null.** Change-point null calibration (a smooth-sigmoid null), if change points are to
  carry weight.
- **G3 replication** (410M/1B, PolyPythias seeds): not started.
