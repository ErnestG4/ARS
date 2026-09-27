# Arm B pre-registration — Part B1b: Q1–Q4 tests

**Status: DRAFT, not sealed.** It is sealed, together with its licence and analysis code, before A0's first optimizer
step. Nothing here may be changed after any A0/A1/A2/M0 trajectory is seen; later changes are dated amendments,
labelled post-hoc.

**Common rules.**
- Parent: ARMB_PREREG.md (B1a, sealed 01fc4b5).
- Status vocabulary as in FINDINGS_MEMO.md.
- Every statistic comes from the fp32 masters, with Stage 3's estimator versions unchanged (G5 columns plus `arm`).
- Per-head local statistics: ⟨r̃⟩ only; q is not read at N = 64 (memo §4, S4).
- Arms:
  - A0: AdamW, Pythia schedule, W = 1430, stop 5000.
  - A1: W = 2860, stop 3000.
  - A2 (optional): W = 715, stop 3000.
  - M0 × 2 seeds: Muon, Pythia schedule, stop 3000; the rule is Will's decision 3.
- Seeds: A0/A1/A2 use seed 1234; the M0 seeds are 1234 and 4321.
- Layer-mean = the mean over the 6 layers. Matrix types: Q, K, V, O, MLP_IN, MLP_OUT.

## Q1 — LR confound: do turning points move with the end of warmup?
**Observables (primary).** The layer-mean stable rank sr(t) of O and of MLP_OUT on each arm's full grid. These are
Stage 3's "rebound after ~2k" (§3: O 79 → 168, MLP_OUT 111 → 227 on 1.4B).
- A turning point is an interior minimum of sr(t) followed by a sustained rise.
- Secondary (descriptive only): the same for Q, K, V, MLP_IN.

**Estimator licence (known answer, BEFORE any arm data; `armb/q1_licence.py`, sealed with this document).**
- **Synthetic trajectories on each arm's exact grid:**
  - (a) NO turning point: monotone decreasing curves (exponential / power-law / logistic decay to a floor);
  - (b) a planted minimum at t₀ ∈ {800, 1500, 2200, 2900} with rebound depths {5%, 15%, 40%} of the curve's range,
    asymmetric shapes included;
  - (c) plateau-then-rise curves whose minimum is flat over 200–600 steps.
- **Noise:** i.i.d. Gaussian at relative SD ∈ {0.5%, 1%, 2%, 5%} of the local value, plus an AR(1) variant with φ = 0.5.
  2000 draws per cell.
- **Candidate estimators:**
  - E1: the argmin of a Savitzky–Golay-smoothed curve in log-step (window 9, order 2), with a residual-bootstrap CI;
  - E2: a unimodal vs isotonic-decreasing fit comparison, where a turning point exists iff the unimodal fit reduces
    the SSE with permutation p < 0.01, located at the unimodal fit's minimum and given a bootstrap CI.
- **Licence per noise level, criteria per estimator:**
  - false "turning point" on (a) ≤ 5%;
  - detection on (b) ≥ 80% at depth ≥ 15%;
  - on detected (b)/(c): location |bias| ≤ max(one grid interval, 5% of t₀), and 90% CI coverage ≥ 85%.
- **At analysis:** each arm's residual noise is measured as the relative SD about E1's smooth fit. It is a measurement
  of noise, not of the effect. The licence row at the next-higher noise level applies.
- If no estimator is licensed at that noise level, Q1 is DESCRIPTIVE ONLY for that metric.
- If several are licensed, the one with the smaller worst-case |bias| is used, fixed by the licence run.

**Decision (per primary metric), using licensed t* with CIs:**
- **If A0 shows NO turning point** (the licensed estimator says none): Q1 is **NOT APPLICABLE AT 70M** for that
  metric. This is itself a size finding against Stage 3's 1.4B rebound, and is reported as such.
- **Otherwise** fit b = Δt*/ΔW:
  - two arms: b = (t*_A1 − t*_A0)/1430;
  - with A2: OLS over the three arms (W = 715, 1430, 2860).
  - The CI comes from the bootstrap draws of the t* values.
- **Verdicts:**
  - **LR-DRIVEN** iff the 90% CI of b ⊂ [0.75, 1.25];
  - **LEARNING-DRIVEN** iff the 90% CI of b ⊂ [−0.25, 0.25];
  - otherwise **INCONCLUSIVE**. An intermediate b (e.g. 0.5), with its CI excluding both bands, is reported as
    **MIXED**, i.e. part schedule, part learning.
- **A turning point in A0 but none in A1 (or vice versa):** reported as such. That is informative on its own (e.g.
  warmup ×2 abolishes the rebound before 3000), but it is not a slope verdict.

## Q2 — ordering events in steps 256–2000 (A0; M0 separately, descriptive)
**Events** (each is the first grid step at which the criterion holds):

| event | criterion (from Stage 3 / G3) |
|---|---|
| E_ind | max induction score ≥ 0.3 (R5 marker) |
| E_OV | ≥ 50% of heads' OV score outside the product-Ginibre 1–99% band (R4) |
| E_QK | ≥ 50% of heads' QK symmetric fraction (non-rotary) outside its band (R4) |
| E_MP(Q), E_MP(K) | MP KS > witness KS95 in ≥ 90% of layers (R6) |
| E_sr(M), M ∈ 6 types | layer-mean stable rank ≤ ½ its step-0 value |
| E_loss | text-probe loss drops below (step-0 loss + final-at-3000 loss)/2 (a midpoint marker for the loss drop) |

- **CIs:** each event time gets a 90% CI by bootstrap over its units: heads for OV/QK/induction, layers for MP and
  stable rank. The E_loss CI is the grid resolution only.
- **Ordering:** E_a PRECEDES E_b iff the upper CI of E_a < the lower CI of E_b. Overlapping CIs are SIMULTANEOUS AT
  THIS RESOLUTION.
- **Tested pairs, each sealed:**
  - E_OV vs E_QK: G3 R4 says OV first.
  - E_OV vs E_ind and E_QK vs E_ind: Stage 3 says OV departs before induction, and QK around it.
  - E_sr(Q) vs E_sr(V): Stage 3 says V compresses later.
  - E_MP(Q) vs E_ind.
  - Holm correction is not applied to CI-based ordering. Every pair is reported.
- **Descriptive:** all events are placed on one timeline together with the warmup end (1430).

**Layer-ordered compression wave (Liu, arXiv 2604.22778: "Stable-rank compression travels as a wave from early to late
layers … Q/K matrices carry the depth-dependent dynamics while V/O compress uniformly").**
- **Per layer:** t_half(M, L) = the first grid step at which layer L's stable rank of type M ≤ ½ its step-0 value.
- **Statistic:** Spearman ρ between L (0–5) and t_half, with an exact permutation p-value over the 720 orderings
  (ties handled by averaging).
- **Liu REPLICATES** iff ρ > 0 with one-sided exact p < 0.05 for BOTH Q and K, i.e. early layers compress first.
  - V/O uniformity is reported: p ≥ 0.05 for each.
  - ρ < 0 with p < 0.05 for Q or K is OPPOSITE ORDER.
  - Anything else is NOT REPLICATED (no ordering resolved).
- **Power note (declared):** with 6 layers, one-sided p < 0.05 needs ρ ≳ 0.83. A perfect monotone ordering gives
  p = 1/720. A weaker wave is undetectable at 70M, and a NOT REPLICATED here is a bounded null, not a refutation.

## Q3 — are early updates low-rank?
- **Update:** ΔW over an interval [t₁, t₂] on the grid, per layer and type. Statistic: layer-mean stable rank of ΔW.
- **Two matched comparisons.** Stable rank is scale-free, so LR matters only through how many effective updates
  accumulate.
  - **(S) Equal step count.** 10-step intervals [100, 110], [200, 210], [300, 310], [400, 410] vs [1000, 1010] and
    [2000, 2010]. The grid has every 10 steps up to 500. Above 500 the grid is 25-step, so [1000, 1025] and
    [2000, 2025] are used against early 25-step spans [100, 125] (on the 10-grid: 100 → 130, i.e. 30 steps). This is
    DECLARED: the early span is longer, which biases early rank UP, so the comparison is conservative.
  - **(L) Equal LR integral.** Early intervals starting at 100, 200, 300 extend until ∫lr matches ∫lr over [1000, 1025],
    on the 10-step grid (e.g. [100, ~350] at the warmup LR). Longer spans bias early rank UP, so this is also
    conservative.
- **LOW-RANK EARLY** iff, in BOTH (S) and (L), for ≥ 4 of the 6 types, the early/late ratio of ΔW stable rank is
  ≤ 0.5, using the earliest early interval vs the [1000, *] interval.
  - **NOT LOW-RANK EARLY** iff the ratio is ≥ 0.8 for ≥ 4 of 6 types in both comparisons.
  - Otherwise INCONCLUSIVE.
  - CIs by bootstrap over layers are reported.
- Arms: A0 is primary; A1 is descriptive (its warmup is longer, so its LR is lower over the same steps).

## Q4 — AdamW vs Muon (M0 × 2 seeds vs the AdamW reference)
- **Bulk null per arm.** Stage 3's sealed rule, applied to every M0 checkpoint on the shared steps and on the full grid:
  bulk ⟨r̃⟩ within 0.010 of the G1 witness for full-matrix and per-head cells. q is reported but not read per-head.
  - An M0 cell violating is VIOLATED, followed by the ladder (density-matched witness, with the licensed ⟨r̃⟩
    calibrator from S4).
  - Verdict: **BULK NULL HOLDS UNDER MUON** / **VIOLATED (attributed …)**.
- **Spectral entropy** (normalised Shannon entropy of σ²/Σσ², layer-mean per type) and **update rank** (Q3's ΔW
  stable rank at the shared intervals).
  - At each B-G1 shared step: d = mean(M0) − m_ref, with SE = √(s_ref²/10 + s_M0²/2) and a Welch–Satterthwaite t.
  - **OPTIMIZER-DIFFERENT** iff |t| exceeds the Bonferroni t over the family (types × shared steps) AND both M0 seeds
    individually lie outside the AdamW band (|z| > T of B-G1).
  - **NOT DISTINGUISHED** otherwise.
  - The M0 seed spread enters through s_M0 and through the both-seeds requirement. With 2 seeds, s_M0 is poorly
    estimated; that is declared, and the both-seeds clause is the guard.
- **Event timing (Q2 events) in M0 vs A0:** descriptive, with the Q2 CIs.

## What would change these plans (pinned now)
- **B-G1 fails:** nothing here is read (brief §3 B2).
- **Q1 licence yields no estimator:** Q1 is descriptive only, and says so.
- **A2 is not run** (Will's decision 2): Q1 uses the two-arm slope, with its wider CI, and says so.
