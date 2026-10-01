# Stage 1 findings — existence check (brief v1.1 §1b)

## Verdicts
- **As sealed:** PEAKS in both models (OLMo 2 1B `main`, Pythia-1.4B step143000), so the decision table says
  "BOTH: aim 1 moves to Pythia". Amendment A1's bulk-mode split gives the same answer (BULK_PEAKS in both).
- **As evidence of multi-peak structure: UNRESOLVED (non-evidence).**
  - The sealed criterion was calibrated only on MP spectra (compact, unimodal). Its false-positive rate on the
    nearest confusable class, unimodal heavy-tailed spectra (the documented shape of trained weights), was
    never measured.
  - Direct inspection shows the counted extra modes are overwhelmingly tail specks: a median of 1–2 levels,
    median prominence 3% of the peak, median location σ/median ≈ 1.6.
- **G0 at step 0:**
  - OLMo passes for all four matrix types.
  - Pythia passes Q, K, V and **FAILS-as-sealed for W_O**: 6/384 multimodal, against the 98.5% unimodal bar.
  - Attribution: under the calibrated null rate (0.98% on the holdout), P(X ≥ 6 | n = 384) = 0.18, and the six
    heads are spread over six layers. The sealed G0 bar had no allowance for sampling noise, so the rule itself
    false-fails 18% of the time at n = 384 (24% at n = 256). The label stays FAIL-as-sealed. It is a defect of
    the rule, not evidence against the criterion or the weights.

## What the data do show (descriptive; the thresholds below are post-hoc)
- Heads with a substantial secondary mode (≥ 10 levels and prominence ≥ 0.1 of the peak):

  | model | W_Q | W_V |
  |---|---|---|
  | Pythia final | 78/384 (20%) | 2/384 |
  | OLMo final | 96/256 (38%) | 2/256 |

  This is a Q-specific candidate, pending a test calibrated against unimodal heavy tails.
- **Dead rows (OLMo only):** some W_Q/W_K heads have rows decayed to norm ~1e-28.
  - At stage-1 end, 8 Q heads are RANK_COLLAPSED (median σ below the fp32 floor).
  - A near-zero mode appears in 170 Q heads (stage-1 end) and 92 Q heads (`main`).
  - Pythia has no near-zero modes in Q or K.
- **G4 (storage precision):** Pythia's F32 checkpoints are fp16 upcasts. OLMo 2's are fp32 masters, contrary
  to the brief's "bf16" premise.

## Stage 1b result — Hartigan dip test (POST-HOC, calibration committed first: d16caaf)
- **Calibration.**
  - False positives: 0/2000 for every nearest confusable (MP, Student-t with nu = 2.5/3/4, spiked MP with
    1/3/10 outliers, lognormal), so the test is LICENSED.
  - Power: it needs well-separated, narrow, balanced peaks. Separation 0.2 at sd 0.03 is detected 100%;
    a 20% minority peak at sd 0.1 is detected ~0% even at separation 0.5. Hence "no peaks" is weak
    evidence and "peaks" is strong.
- **Heads multimodal at p < 0.01** (all levels / near-zero cluster excluded):

  | run | W_Q | W_K | W_V | W_O |
  |---|---|---|---|---|
  | Pythia final | 0/384 | 0/384 | 0/384 | 0/384 |
  | Pythia step 0 | 0 | 0 | 0 | 0 |
  | OLMo `main` | 22 (8.6%) / 14 (5.5%) | 12 (4.7%) / 8 | 0 | 0 |
  | OLMo stage-1 end | **63 (24.6%) / 34 (13.3%)** | **51 (19.9%)** / 22 (8.6%) | 1 | 1 |
  | OLMo step 0 | 0 | 0 | 0 | 0 |

- **G0 (with a sampling allowance):** passes for every matrix type in both models.
- **Reading.**
  - Pythia's sealed-Stage-1 "PEAKS" was entirely tail specks: no head is resolvably multimodal.
  - OLMo's resolvable multimodality is real and Q/K-specific. It is strongest at the end of pretraining stage 1
    and partly carried by the dead-row (near-zero) cluster: 13.3% of Q heads remain once that cluster is
    excluded. It is largely removed by the stage-2 anneal.
  - At `main` the excess is significant against the null (binomial P far below 1e-3) but below the declared
    10% effect floor.
- **Decision.**
  - By the declared table, evaluated at the final checkpoint `main`: OLMo NO PEAKS (sub-floor), Pythia NO
    PEAKS, so aim 1 is deferred and this is recorded as a qualified replication.
  - Qualification: Diffract's structure is present during OLMo pretraining (stage-1 end, 4T tokens) at the
    resolution of a licensed test, and is reduced by annealing. Pythia shows none.
  - Pursuing aim 1 on OLMo's stage-1 trajectory is **Will's call**; it is not started. The architectural
    contrast (QK-norm + full RoPE in OLMo vs partial rotary and no QK-norm in Pythia) is the stated hypothesis
    if he does.

**Note 2026-10-01 — `main` is not this lineage's endpoint.** OLMo-2-0425-1B `main` is a different training run from
the released checkpoint lineage: every layout-invariant tensor correlates at ≤ 0.017 with the stage-2 ingredient-3
final and with stage-1 end, while the lineage is self-consistent (0.97–0.999); both rotary row permutations leave
Q/K/V at 0.000; HF history shows `main` still holds the 2025-04-17 upload that every checkpoint branch replaced on
04-26..28 (olmo_main_provenance.py, results/olmo_main_provenance.json: DIFFERENT_RUN). Every statement above that
reads `main` as "after the anneal" ("largely removed by the stage-2 anneal", "reduced by annealing", the decision
table's evaluation "at the final checkpoint `main`") is withdrawn. The `main` readings describe a released model of
unstated provenance. The step-0 and stage-1-end readings stand. The lineage endpoint
`stage2-ingredient3-step23852-tokens51B` is unmeasured; the aim-1 deferral is re-opened.

## (superseded plan) Next (Stage 1b, POST-HOC, declared as such)
- Replace "any KDE mode" with Hartigan's dip test (null = all unimodal densities, heavy tails included) at
  per-head α = 0.01.
- Before applying it to real heads, measure:
  - its false-positive rate on constructed confusables of matched shape: Student-t entries (ν = 2.5, 3, 4) and
    spiked MP with 1–10 BBP outliers;
  - its power on true two-peak spectra.
- Report both calibrations alongside the real-head rates.

## Outputs
- results/stage1_verdict.json, results/stage1_long.parquet (G5 columns), plots/stage1_*.png.
- Seal: seals/stage1_peak_criterion.json (34de628). Amendment A1: ee83e79.
