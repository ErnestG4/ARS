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
- **Product-Ginibre null** (stage3_circuit_null.py, 4000 draws): OV score 1–99% band [−0.027, +0.028]; QK
  symmetric fraction [0.4994, 0.5011].
- **Fraction of heads outside that band:**

  | step | 0 | 512 | 1000 | 2000 | 8000+ |
  |---|---|---|---|---|---|
  | OV score | 2.3% | 98.7% | 99.7% | 100% | ~99% |
  | QK symmetric fraction | 3.1% | 3.4% | 51% | 96% | ~96–99.5% |

  - At step 0 the rates match the 2% the band admits.
  - **The OV departure precedes the QK departure.** OV is out of band by step 512, before induction forms; QK is
    mostly out only by step 2000.
  - Caveat: the QK null is very narrow, so the departure is small in magnitude (median 0.51–0.52).

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
- **Change-point null calibration** (a smooth-sigmoid null), if change points are to
  carry weight.
- **G3 replication** (410M/1B, PolyPythias seeds): not started.

## 8. Review response (2026-09-25 ~23:55; post-hoc checks in stage3_confounds.py, results/stage3_confounds.json)
Each earlier descriptive claim is restated below with its status. Sections 3–7 above are superseded wherever they
conflict with this section.

- **Null wording (§1), refined.**
  - The precise claim is: no bulk departure larger than 0.010 in ⟨r̃⟩ or 0.10 in q, at any checkpoint, in any type.
  - The Poisson check shows the instrument sees a gross departure (~0.14). The tolerances bound what could hide.
    q ≤ 0.10 is loose; the observed worst |Δq| was 0.034.
- **"Turning points at ~2k" — LR-CONFOUNDED, unresolved.**
  - Pythia's warmup ends at step 1430 (config: warmup 0.01 × 143000; Adam lr 2e-4; cosine to 2e-5).
  - The 1000 → 2000 interval straddles it, and the LR integral per interval jumps from 0.05 (512 → 1000) to 0.19
    (1000 → 2000), then stays ~0.2 per 1000 steps.
  - Any extremum reported "at 2k" sits at the first checkpoint after warmup ends. Pythia offers no finer checkpoints
    there. Only arm B (own dense checkpoints, varied warmup) can separate learning from schedule.
- **"Outliers peak ~2k then decline" — RETRACTED as outlier dynamics (edge artefact).**
  - From 2k to the end, the fitted MP edge grows 5.6× (O: 0.28 → 1.54) and 5.4× (MLP_OUT), faster than σ_max
    (O 1.08 → 3.35, 3.1×) and σ at rank 200 (4.3×).
  - The top singular values keep growing; the bulk widens up to meet them.
  - The count against a moving edge is not an outlier trajectory. Report absolute top-σ quantiles instead.
- **"Top singular vectors localise from 2k–8k" — RE-SCOPED.**
  - The IPR / Porter–Thomas signal is on the LEFT (output-space) vectors. What it measures:
    - Concentration on single heads: mass in the heaviest head, Q 0.24 and V 0.22 at the end vs 1/16 isotropic.
    - For K, concentration on rotary dims: 0.48 vs 0.25 isotropic (V, which has no rotary structure, reads exactly
      0.25).
  - It is NOT the massive-activation / LayerNorm phenomenon: the right (residual-space) top vectors of Q/K/V share
    0 of their 8 heaviest residual coordinates in every layer, and put ≤ 3× isotropic mass on the top LN-gain
    coordinates.
  - So the claim becomes: top singular directions of Q and V concentrate in a few heads, and K's top directions
    concentrate on rotary dims. That is a head-block/rotary structural statement per matrix type, not basis-free
    localisation.
- **"ΔW low-rank early, high-rank late" — PENDING** (stage3_motion_eq.py, equal 1000-step intervals).
  - The consecutive-schedule intervals grow from 1 step to 1000+ steps, and their LR integrals from 1e-7 to 0.2. The
    early low rank may be spacing and LR.
  - Equal intervals exist only from step 1000 on, so the sub-1000 regime cannot be tested at equal spacing.
- **"QK departs later and only slightly" — REVISED (aggregation).**
  - For the 14 heads with final induction score > 0.3, the fraction outside the product-Ginibre QK band is 21% at
    step 512 and 100% at 1000. For the other heads it is 2.7% and 49%.
  - Median |sym − 0.5|: induction heads 0.037 vs others 0.009 at the end.
  - The QK change is earlier and larger in exactly the heads that do induction. The all-head average had masked it.
  - "OV departs before induction" is a single-checkpoint precedence (step 512) at the resolution limit.
- **Sink timing — NOT COMMENSURABLE with the brief's 10–20×.**
  - arXiv 2606.02378 defines a BOS-classified head as ≥ 30× first-token selectivity against a uniform-position
    baseline, on a synthetic "[filler] A B [filler] A" batch with class competition.
  - Their 10–20× is for DCLM/OLMo. For **Pythia-1B, their own numbers** are induction ≈ 6B tokens and BOS-50% at
    300B tokens, a ≈ 50× gap.
  - Our probes have no BOS token (Pythia does not prepend one). Approximating their threshold (the uniform baseline
    over our query positions ≈ 0.0070, so 30× ≈ mean attention > 0.21), our "BOS-classified" fraction crosses 10% at
    32k–48k and 50% at 64k–96k steps.
  - Their Pythia-1B BOS-10% (~6B tokens, co-emerging with induction) is much earlier than our approximate one.
    Definition, probe and BOS presence all differ; no comparison is drawn.
- **G2 (bulk permutation, +2.66 nats) — PENDING controls** (stage3_g2b.py, pre-registered 86b6b31): size-matched
  Gaussian perturbation, local-window shuffles, MP-bulk-only shuffle, dose-response.

## 9. Second review round (2026-09-26 ~00:10; stage3_confounds2.py, stage3_headnull.py)
- **MP-fit validity: "outlier vs MP edge" is UNDEFINED for trained Pythia.**
  - Per matrix, the KS of the spectrum to MP at the median-matched scale exceeds the G1 witness 95th percentile in
    96–100% of layers for every type: from step 512–1000 (O, MLP_OUT, Q, K, MLP_IN) and from ~2000 (V). Before that
    it fails in ≤ 21% of layers.
  - A bulk that is itself heavy-tailed inflates any MP edge fitted to it. **All mp_fit_v2 outlier counts after ~1000
    steps are withdrawn**, including §3's detachment timings beyond the first departures.
  - What remains is top-k σ (layer means): Q σ₁ 1.26 → 2.1 (512) → 7.6 (2k) → 10.9 (32k) → 17.3 (143k); K σ₁
    peaks ~10 over 8k–32k and ends at 8.9; O and MLP_OUT rise steadily. Full table in results/stage3_confounds2.json.
  - The gap criterion (largest σᵢ/σᵢ₊₁ in the top 10%) almost always lands at i = 1, so it is uninformative here.
- **Head concentration: the "1/16" baseline was the wrong null.**
  - A within-head OUTPUT rotation is degenerate for this statistic: a head's share of a left singular vector is exactly
    invariant under it (observed = null to every digit).
  - The informative null randomises each head's INPUT side independently (W_h O_h, Haar), keeping every head's
    spectrum and norm. Under it, top-8 left vectors would concentrate MORE: 0.59 (Q), 0.50 (K), 0.37 (V), vs observed
    0.24 / 0.13 / 0.22.
  - So head norms alone would predict more concentration than exists. The actual structure is **cross-head sharing**:
    heads read common top input directions, which spreads the top singular vectors over several heads. "Head
    concentration vs 1/16" is not a finding.
- **K's rotary concentration SURVIVES the norm check.**
  - K's top-8 left vectors put 0.48 of their mass on rotary dims (0.38 at 8k). The within-head rotation null (which
    mixes rotary and non-rotary dims) gives 0.25.
  - K's rotary rows carry only 0.227 of ‖W_K‖_F², less than their 25% share. So this is not "rotary rows are heavier":
    K's high-σ directions concentrate in position-coded dims.
  - Q shows a weaker version: 0.28 vs 0.25, with rotary rows carrying only 0.146 of the norm. V, which has no rotary
    structure, reads 0.25 as a control.
  - This is the one localisation result that stands: position-driven structure dominates K's top spectrum.
- **LayerNorm folding (W·diag(γ)).** The residual-side conclusions hold on both raw and folded matrices, with one
  addition:
  - Q/K/V share 0 of their 8 heaviest residual coordinates in every layer, raw and folded.
  - After folding, in late layers (16–23), 3–5 of Q's 8 heaviest residual coordinates coincide with the top-8
    LN-gain coordinates. Their mass is small (1.2% per top vector, 3× isotropic).
  - Mild residual-coordinate specialness exists in late-layer Q. It is not the source of the left-side signal.
- **Induction heads, reworded.**
  - Lead with timing: the 14 heads with final induction > 0.3 leave the QK null band earlier (21% at step 512 and 100%
    at 1000, vs 2.7% / 49% for other heads).
  - Magnitude (0.037 vs 0.009 median |sym − 0.5| at the end) is partly built in: heads chosen for a high induction
    score have unusual QK structure by construction.
- **ΔW.**
  - The equal-interval run (queued) records ‖ΔW‖/(‖W‖·LR integral) as well as equal lengths, since the cosine decay
    changes the step size after step 1430.
  - **The "low-rank early" half moves to arm B:** Pythia has no equally spaced checkpoints before step 1000, so it
    cannot be tested here.
- **G2 controls (amended before running, 0190896).** Size is matched on ‖W′ − W‖_F. The pre-registered half-cost rule
  now compares against a Gaussian perturbation confined to the same bulk singular subspace. The isotropic one is kept
  as a harsher bound.
- **G2 bulk shuffle is stable:** +2.66 / +2.64 / +2.70 nats (3 seeds). Full shuffle: +9.30 / +9.52. What it means is
  for the controls to decide.

## 10. G2 functional witness — result as pre-registered (stage3_g2.py, 0970140; results/stage3_g2.json)
- **Setup:** step 143000, text-probe loss (baseline 2.0983), σ permuted within a rank band in all 144 layer matrices,
  rebuilt in fp16.
- **Results:**
  - Identity control: Δloss +0.0000, so the witness is valid.
  - bulk (ranks 10–90%): +2.66 / +2.64 / +2.70 → **FUNCTIONAL**.
  - full: +9.30 / +9.52 / +9.46 → FUNCTIONAL (≥ 1 nat).
  - upper (90–99%): +0.10 (3 seeds) → FUNCTIONAL by the registered threshold (3 × |identity| + 0.01 = 0.01).
  - lower (1–10%): +0.007 → INERT.
- **Registered verdict:** "Diffract replicates" = **false**, because the bulk is not inert.
- **Interpretation is deferred to G2b** (pre-registered 86b6b31, amended 0190896 before running). The first control is
  already in and warns against reading "bulk ordering carries function" off this: the isotropic Gaussian
  perturbation, size-matched on ‖W′ − W‖_F, costs **+6.13 nats**, much more than the bulk shuffle it matches. So size
  alone is ample to explain large losses. The like-for-like bulk-subspace control decides the registered rule.
- **Scope differences from Diffract** (to reconcile before calling anything a non-replication): here "bulk" is a
  rank band, not the MP bulk, and every matrix is permuted simultaneously. G2b's mpbulk and dose conditions address
  both.

## 11. G2b controls — result (stage3_g2b.py, pre-registered 86b6b31, amended 0190896; results/stage3_g2b.json)
- **SIZE (registered rule, like-for-like control).** A Gaussian perturbation confined to the same bulk singular
  subspace, size-matched on ‖W′ − W‖_F, costs **+1.80 nats** (1.79 / 1.72 / 1.87), against G2's bulk shuffle at
  +2.67. The ratio 0.67 is ≥ 0.5, so **perturbation size explains at least half of the effect, and "the ordering of
  bulk singular values carries function" is NOT established.**
  - The isotropic size-matched control costs +6.23 (harsher: it also hits the top directions the shuffle leaves
    alone).
- **GRADED.** Shuffles confined to windows of k = 2 / 8 / 32 neighbouring bulk ranks cost ≈ 0 (≤ +0.0001 nats).
  - **REVISED 2026-09-30 (G2c, stage3_g2c.py a145694; results/stage3_g2c.json; Will's critique #11).** The original
    reading here ("local reordering of bulk σ is functionally inert") is WITHDRAWN as a reading.
    - The local shuffles are tiny: ‖ΔW‖ is 0.14% / 0.56% / 2.2% of the bulk shuffle's (median 0.07% / 0.28% / 1.1%
      of ‖W‖ per matrix). fp16 re-storage adds ≤ 4%.
    - A same-subspace random perturbation of the same size also costs ≈ 0 (≤ 0.0004 nats).
    - So near-zero cost is what size alone predicts. The k-sweep neither supports nor contradicts "fine ordering
      is irrelevant".
    - Descriptive: at k = 32 the control costs 4–6× the local shuffle in both seeds, all below 1e-3 nats.
    - All six local conditions reproduced G2b's banked dloss exactly (regression check).
  - The SIZE conclusion (at least two-thirds of the bulk shuffle's cost is explained by perturbation size) is
    unaffected.
- **mpbulk.** Permuting every σ below the fitted MP edge costs +7.9 / +8.2 / +8.4.
  - This is NOT a gentler, Diffract-style bulk. Trained spectra fail the MP fit (§9), so the fitted edge sits high:
    "below the edge" spans ranks ~162–2048 and includes large σ.
  - For trained Pythia the "MP bulk" is not a well-defined region, so this condition cannot serve as the Diffract
    reconciliation.
- **DOSE.**
  - One matrix (L12 Q / L12 MLP_IN): +0.005 / +0.005.
  - One layer (L12 / L0, all six): +0.035 / +0.080.
  - All 144 (G2): +2.67.
  - The effect is **strongly superadditive** across layers: 24 single layers at ~0.05 each would sum to ~1.2.
- **Reading.**
  - Shuffling the middle-80% singular values of every matrix at once is costly, but mostly because of how much it
    perturbs the weights: a same-subspace random perturbation of equal size costs two-thirds as much. Locally
    reordering the same values costs nothing.
  - Per-matrix and per-layer shuffles are nearly harmless (≤ 0.08 nats). That is closer to Diffract's "bulk
    permutation roughly harmless", which may have been per-matrix or per-layer; their scope is not confirmed here.
  - The registered "Diffract replicates = false" stands as sealed, attributed to scope (all 144 matrices at once) and
    size, not to evidence that bulk ordering carries function.

## 12. Equal-interval ΔW (stage3_motion_eq.py; cache/s3_motion_eq/)
- **Setup:** 1000-step intervals (t → t+1000). The LR integral is 0.187–0.200 for t = 1k … 31k, then 0.127 (63k), 0.025
  (127k) and 0.020 (142k).
- **Update rank rises at constant step count and ~constant LR** (layer-mean stable rank of ΔW, 1k → 31k):
  - Q 20 → 240; K 10 → 203; V 25 → 252; O 58 → 265; MLP_IN 34 → 503; MLP_OUT 88 → 343.
  - So from step 1000 on, "updates become higher-rank" is a property of the dynamics, **not** an artefact of checkpoint
    spacing or LR.
  - The later decline (to ~100–165 by 127k–143k) coincides with a 10× fall in the LR integral, so it is LR-confounded.
  - The sub-1000 half ("low-rank early") cannot be tested in Pythia and belongs to arm B.
- **Relative update per unit LR** (‖ΔW‖ / (‖W‖ · LR integral)) falls 2–10× from 1k to 31k: O 7.7 → 0.82; MLP_OUT
  7.9 → 0.77; Q 2.3 → 0.80; V 1.1 → 0.71.
- **Alignment with W's top-32 left subspace.** Q and K updates carry 14–16% of their squared norm there over 1k–3k
  (~9× the isotropic 0.016), decaying to ~2× by 15k and staying there. V, O and MLP_OUT sit at 1.3–4×.
- **Unexplained feature at 4k → 5k.** The update rank of V, O and MLP_OUT drops sharply (V 111 → 35, O 179 → 45,
  MLP_OUT 314 → 193) and recovers by 7k → 8k; Q and K do not dip. A low-rank update burst in the OV/MLP-output
  path. Reported, not interpreted (loss spike or data event are both possible; the 4k–5k markers show no loss jump:
  text loss 2.71 → 2.64).

## 13. Compression timing with dense V checkpoints (post-hoc extension; stage3_wave.py; results/stage3_wave.json)
- **Setup:** 8 extra revisions (5k, 7k, 9k, 10k, 11k, 13k, 14k, 15k) give 1000-step resolution over 2k–16k. Per layer:
  the first step at which stable rank ≤ half its step-0 value.
- **V (null at 1000-step resolution): NO layer ordering.** Half-times spread over 3k–12k across layers with no
  early-to-late trend (Spearman ρ = −0.00, p = 0.995).
  - The grid is fine enough to see a wave in V, and there is none.
  - A null for V's compression timing at this resolution, not a failure to resolve.
- **Q, K, O, MLP_IN, MLP_OUT:** unchanged. They all compress in 256–2000 steps, where only 512 / 1000 / 2000 exist.
  UNRESOLVED; only arm B (own dense checkpoints) can address it.

## 14. Replication-scorer consistency check on 1.4B (stage3_repl.py; results/stage3_repl.json)
- The G3 scorer, re-run on 1.4B, reproduces the earlier review scripts:
  - Deterministic quantities exactly: R1 rotary mass 0.484, rotary rows 0.227; R2 observed Q 0.243 / K 0.133; R3
    ratios (Q 10.2 … MLP_OUT 4.2); R5 (512, 1000); R6.
  - Monte-Carlo nulls within sampling noise: R1 null 0.2505 vs 0.2503; R2 null Q 0.609 vs 0.588; R4 QK fraction out
    0.042 vs 0.034 (the band is re-sampled).
- All six criteria read REPLICATES on 1.4B, and none is near its threshold.
- So the scorer is validated before its Pythia-1B / 410M verdicts are read.

## 15. Change-point null calibration (stage3_cp_null.py; rule declared before running; results/stage3_cp_null.json)
- **Setup:** smooth monotone curves with NO change point, run through the same BIC binary segmentation at the 25
  schedule steps.
  - Noise is matched to the observed series: median relative residual SD 0.085, tested at 0.5× / 1× / 2×.
- **False change-point rates:**
  - sigmoid: 0.98 / 0.86 / 0.59
  - saturating exponential: 0.98 / 0.89 / 0.70
  - pure linear: 0.18 / 0.22 / 0.16
- **Verdict: NOT LICENSED** (the rule required ≤ 0.05). The 270/337 series with "changes" in the 1.4B run are what
  smooth trajectories produce under this detector.
  - Change points carry no evidential weight, and no event alignment rests on them. The earlier "descriptive only"
    label is now calibrated, not just asserted.
  - A licensed change detector would need a null-calibrated penalty; this is not attempted.
