# G3 replication pre-registration — Pythia-1B and Pythia-410M (brief v1.1 §5 G3)

This is committed BEFORE any statistic on either model is computed. Only raw extraction (which chooses no statistic)
may run before this commit.

## Substrates
| model | layers | heads × d_head | d_model | FF | rotary dims/head |
|---|---|---|---|---|---|
| Pythia-1B (EleutherAI/pythia-1b) | 16 | 8 × 256 | 2048 | 8192 | 64 |
| Pythia-410M (EleutherAI/pythia-410m) | 24 | 16 × 64 | 1024 | 4096 | 16 |

- **Shared with 1.4B:** the GPT-NeoX code path, tokenizer, data (the Pile, standard order), and the 26-revision
  schedule (pythia_1.4b_schedule.txt).
- **Training configs** (EleutherAI/pythia `models/<size>/*.yml`, read 2026-09-26 before this commit):
  - All three sizes: Adam betas (0.9, 0.95), weight decay 0.1, warmup 0.01 × 143000 = 1430 steps, cosine decay to
    10% of peak over 143000.
  - Peak LR: 1.4B 2.0e-4; 1B 2.5e-4; 410M 3.0e-4. Micro-batch 16 (1B) / 32 (410M).
  - The same warmup end (1430) means the ~2k LR confound applies to all three. LR integrals are computed per model
    from its own peak.
- **Code:** the model-general pipeline (mcfg.py; LLMSPEC_MODEL selects the model). It is regression-gated against the
  banked 1.4B results:
  - verify_refactor_regression.py: extraction bit-identical.
  - verify_analyze_regression.py: analysis values identical.

## A. The sealed null, replicated unchanged
- Bulk ⟨r̃⟩ and bulk Brody q (kde(4)) stay at each model's own G1 pooled-null witness value:
  - |Δ⟨r̃⟩| ≤ 0.010 and |Δq| ≤ 0.10, at every checkpoint, for every type (6 full + 4 per-head).
- G0 (step-0 MP KS per matrix vs witness KS95, binomial) and the gate-first ladder carry over verbatim.
- Prediction: HOLDS in all 260 cells per model.

## B. Replication criteria for the review-hardened 1.4B descriptives
Each is REPLICATES or DOES NOT REPLICATE, with the numbers reported. The 1.4B value is given for reference.
- **R1 — K rotary concentration** (1.4B: 0.48 vs null 0.25; rotary rows 0.227 of the norm).
  - Measured at step 143000: the mean over layers of K's top-8 left-vector mass on rotary dims.
  - Requirement 1: it exceeds the within-head-rotation null by ≥ 0.10.
  - Requirement 2: the rotary rows' share of ‖W_K‖_F² is ≤ 0.27 (i.e. not norm-driven).
  - Replicates iff both hold.
- **R2 — Cross-head sharing** (1.4B: observed below the input-rotation null for Q, K and V).
  - At step 143000, the top-8 left-vector top-head mass is below the per-head input-rotation null mean (Haar,
    2 draws) for BOTH Q and K.
- **R3 — Update rank rises at constant LR** (1.4B: ratio ≥ 4.2 for every type).
  - Layer-mean ΔW stable rank over 15k → 16k is ≥ 3× that over 1k → 2k, for EVERY one of the six types.
- **R4 — OV departs before QK** (1.4B at step 512: OV 0.987, QK 0.034).
  - At step 512, against each model's own product-Ginibre 1–99% band (recomputed for its head shapes): the fraction
    of heads outside the OV band is ≥ 0.5 AND the fraction outside the non-rotary QK band is ≤ 0.2.
- **R5 — Induction forms early** (1.4B: 512–1000).
  - Max induction attention first reaches ≥ 0.3 at a checkpoint in {1000, 2000}. The interval is reported as the
    (previous, first) checkpoints.
- **R6 — MP-fit validity collapses** (1.4B: 96–100% of layers by ~512–2000).
  - For Q and K, the per-matrix MP-fit KS (median-matched scale) exceeds that model's witness KS95 in ≥ 90% of layers
    by step 2000.
- **Scope note:** these are within-family replications (one seed per size). The seed leg (PolyPythias) is separate and
  not covered here.

## Outputs
- results/stage3_*_pythia-1b.*, results/stage3_*_pythia-410m.*
- results/stage3_repl.json (R1–R6 for all three models, including 1.4B re-derived by the same code as a consistency
  check against stage3_confounds2 / headnull / circuit_null / motion_eq).
- STAGE3_REPL_FINDINGS.md
