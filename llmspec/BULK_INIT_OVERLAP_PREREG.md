# Bulk–initialisation overlap — pre-registration (SEALED at commit; Will, 2026-10-02: "it's sealed before it's read")

**Question.** How much of the trained bulk is still the initialisation? If the trained bulk subspace is mostly the step-0
weights shrunk by weight decay, the "reservoir" reading of the bulk (ARMA_PREREG_SKELETON §0, H_RES) is close to settled
before any arm-A GPU time is spent; if the bulk has left the initialisation, the reservoir needs the co-adapted calibrator
to be tested at all.

## 1. Data (split-sample rule unchanged)
- Pythia-1.4B and PolyPythias 410M seeds 1–5, all 26 schedule revisions, streamed (`remote_st`), per layer, matrices Q, K,
  V, O, MLP_IN, MLP_OUT; W₀ = the same matrix at step 0 (banked for every run). Seeds 6–9, 410M-std, 1B, 70M and Arm B
  stay UNREAD. CPU on spot (fp64 SVD), as `stage3_extract_mf.py`.
- Bulk definition: for W_t with singular triplets (u_k, σ_k, v_k), the bulk is k ≥ s₀ = 32 (the spike edge used in
  MF_EXPLORE and ARMA); P_t = U_b U_bᵀ (·) V_b V_bᵀ projects onto the bulk left and right subspaces of W_t. The deepest
  octave is reported separately (MF_EXPLORE §3).

## 2. Measurements (per matrix, per checkpoint; banked with their nulls)
- α̂ = ⟨W_t, W₀⟩_F / ‖W₀‖²_F (least-squares scale of the init inside W_t) and the weight-decay prediction
  α_wd(t) = ∏_{s<t}(1 − λ·lr_s) from the published schedule (λ = 0.1 for Pythia... AS CONFIGURED; the config value is read
  and recorded, not assumed).
- d(t) = ‖W_t − α̂ W₀‖_F / ‖W_t‖_F (relative residual after removing the shrunk init).
- **ρ_bulk(t) = ⟨P_t W_t, P_t W₀⟩_F / (‖P_t W_t‖_F ‖P_t W₀‖_F)**: the cosine between the trained bulk and the
  initialisation seen through the trained bulk subspace. Also ρ_full (no projection) and ρ_top (k < s₀).
- **E_init(t) = α̂² ‖P_t W₀‖²_F / ‖P_t W_t‖²_F**: the fraction of the trained bulk's energy accounted for by the shrunk init.
- Nulls, same construction: (a) W₀ replaced by an independent Gaussian matrix of the same Frobenius norm (ρ_bulk and
  E_init under "no memory of init"); (b) W₀ replaced by a different layer's W₀ of the same type (same distribution,
  wrong instance). Known answers, run first: W_t := α W₀ + ε G (ε small) → ρ_bulk ≈ 1; W_t := fresh Gaussian → ρ_bulk ≈ 0
  ± 1/n; W_t := α W₀ + a rank-32 spike → ρ_bulk ≈ 1 while ρ_top is small.

## 3. Reading rule (declared now; words from the memo vocabulary)
At the final checkpoint (143000), over the 144 (1.4B) + 5 × 144 (seeds) matrices, excluding the deepest octave:
- **INIT-DOMINATED BULK** iff ρ_bulk ≥ 0.80 on ≥ 90 % of matrices (and the Gaussian null reads |ρ| ≤ 0.05 on ≥ 99 %):
  the reservoir reading of H_RES is SUPPORTED for the bulk directions; arm A's calibrator stays necessary only for the
  *functional* question.
- **LEARNED BULK** iff ρ_bulk ≤ 0.20 on ≥ 90 % of matrices: the bulk has left the initialisation; the reservoir reading
  needs the co-adapted calibrator and is not settled here.
- **MIXED** otherwise, with the ρ_bulk distribution and its trajectory reported (and per type / per layer tables).
- The trajectory ρ_bulk(t) and E_init(t) vs α_wd(t) are reported in full as descriptives (when does the bulk leave the
  init, if it does; does the init's residual energy track weight-decay shrinkage).
- Per-type splits are reported, never counted as separate verdicts; the deepest octave is a separate descriptive row.

## 4. Deliverables
`bulk_init_overlap.py` (committed before the first real run; synthetic known-answers + nulls in `verify_bulk_init_overlap.py`
with `--redpath`), `results/bulk_init_overlap/*.{json,csv}`, `BULK_INIT_OVERLAP_FINDINGS.md`.
