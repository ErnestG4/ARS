# Bulk–initialisation overlap — findings (2026-10-03)

Pre-registration `BULK_INIT_OVERLAP_PREREG.md` (91e1308) + Amendment A1 (b42d2c3, pre-read). Code sealed 063b6d6
(`bulk_init_overlap.py`, `bulk_init_overlap_verdict.py`; verifier PASS, red path fires). Run on spot 2026-10-02 22:53 →
2026-10-03 02:13 (CPU, streamed; 0 errors). Results: `results/bulk_init_overlap/` (verdict.json; per-model long CSVs
committed; per-model JSON and band CSVs kept locally and on spot). Words are the sealed vocabulary, read mechanically
(`bulk_init_overlap_verdict.py`, CHECKRUN PASS); nothing was re-thresholded after the run.

## 1. Verdicts (as sealed; final checkpoint 143000; ρ_bulk = cosine between the trained bulk, k ∈ [32, r), and the
step-0 weights seen through the trained bulk subspace; thresholds ≥ 0.80 on ≥ 90 % → INIT-DOMINATED, ≤ 0.20 on ≥ 90 % → LEARNED)
| Row | Word | n | frac ρ_bulk ≥ 0.80 | frac ≤ 0.20 | Gaussian null |ρ| ≤ 0.05 | Continuity gate |
|---|---|---|---|---|---|---|
| pythia-1.4b | **MIXED** | 144/144 | 0.014 | 0.368 | 100 % | PASS (step 1 ≡ step 0 on every matrix: Pythia applies lr(0) = 0 at the first update, so the gate's upper side cannot fire and the low side is flagged, as the verdict script declares) |
| pythia-410m seeds 1–5 | **MIXED** | 720/720 | 0.254 | 0.346 | 100 % | PASS, same note, all five |
| pooled (descriptive) | MIXED | 864 | 0.214 | 0.350 | 100 % | — |
- Both nulls read ≈ 0 everywhere (Gaussian: median |ρ_bulk| 1e-4, max 0.008; wrong-instance: max 0.008). Step 0 reads
  ρ = 1.000, α̂ = 1.000 on every matrix (sanity).
- Neither sealed word fired. The MIXED word is honest but hides two very different populations (§2–§3).

## 2. The normal runs: the bulk leaves the initialisation smoothly, by type, and keeps MORE init than weight decay predicts
(1.4B and seeds 1, 2, 5; medians over matrices; seeds 1/2/5 agree to two digits)
| step | ρ_bulk 1.4B | ρ_bulk 410M-s1 | E_init 1.4B | α̂ 1.4B | α_wd 1.4B | d 1.4B |
|---|---|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0 |
| 2000 | 0.973 | 0.972 | 0.832 | 0.974 | 0.975 | 0.42 |
| 8000 | 0.787 | 0.734 | 0.234 | 0.833 | 0.865 | 0.80 |
| 16000 | 0.609 | 0.506 | 0.074 | 0.764 | 0.738 | 0.92 |
| 32000 | 0.415 | 0.315 | 0.020 | 0.636 | 0.547 | 0.97 |
| 64000 | 0.280 | 0.224 | 0.007 | 0.497 | 0.337 | 0.99 |
| 143000 | **0.237** | **0.191** | **0.005** | **0.358** | 0.228 | 0.99 |
- **Energy vs amplitude.** At the end the shrunk init still has 36 % of its amplitude inside W_t (α̂) but supplies only
  0.5 % (1.4B) / 0.3 % (410M) of the trained bulk's energy (E_init): the Kosson-equilibrium expectation declared in A1
  (E_init ≈ 1 %, ρ ≈ 0.1) is met in order of magnitude. The bulk's correlation with the init decays with a half-life of
  ≈ 20k steps (1.4B) / 16k (410M) and flattens at 0.19–0.24 under the cosine LR tail.
- **Red flag fired in the declared direction, the other way round:** A1 expected α̂ ≤ α_wd (updates anti-aligned with the
  init). Observed α̂ > α_wd from ≈ 8k onward on every normal run (1.4B 0.358 vs 0.228 at the end; 410M 0.233 vs 0.109):
  the trained matrices retain ~1.6–2.1× the init amplitude that decoupled weight decay alone leaves. Reported, not
  interpreted (candidates: updates partly aligned with W₀; an effective decay below the configured one; both).
- **By matrix type (143000, medians; 1.4B / 410M-s1):** MLP_IN 0.73 / 0.73 (its near-spike octave 0.99), V 0.41 / 0.34,
  K 0.27 / 0.16, Q 0.21 / 0.14, MLP_OUT 0.17 / 0.19, **O 0.06 / 0.06** (96–100 % of O matrices ≤ 0.20). The per-type
  prediction declared in A1 is answered: W_O, the type Staats et al. find closest to the MP law, has the bulk that has
  LEFT its initialisation the most. MP-shape is not init memory.
- **By spectral position (143000, 1.4B / 410M-s1):** top-32 0.86 / 0.79, near-spike octave [32, 64) 0.90 / 0.70,
  bulk 0.24 / 0.19, deepest octave 0.11 / 0.09. The geometric expectation in A1 (near-spike octave LOWER than the bulk)
  is reversed: init memory decreases monotonically with depth into the spectrum, and the smallest singular directions
  are the least initialisation-like (consistent with MF_EXPLORE §3's late neuron-side structure living there, and with
  Staats et al.'s function at the small edge). The high ρ_top says the top directions grew along initial structure, not
  orthogonally to it (descriptive; the top subspace is 32-dimensional, so this is a correlation of content, not of
  subspace).
- **By layer:** layer 0 keeps the most init (0.51 / 0.40), layers ≥ 8 the least (≈ 0.2 / 0.15).
- **Sign agreement** p(W_t, W₀) = 0.51–0.60 by type (Gaussian map ρ ≈ 0.03–0.3), consistent with ρ_full 0.03–0.29.

## 3. The spike seeds (3 and 4): their post-spike checkpoints are RESTARTS, not continuations (provenance check DONE)
`polypythias_restart_check.py` (reading rule in its docstring; results/polypythias_restart_check.json): elementwise Pearson
correlation of every late checkpoint with every other revision of the SAME seed, layers 0/12/23, Q and MLP_IN; seed 1 as
control.
- **Seed 4:** step 128000 correlates 0.95–0.995 with its own step 256 / 512 / 0 (L00 Q: 0.970 with step 0, 0.966 with
  1000, 0.891 with 2000, 0.56 with 8000) and only 0.07–0.53 with its predecessor at 96000; 143000 continues from 128000
  (0.92–0.99). → RESTART/MISLABEL CANDIDATE on 6/6 (128k) and 4/6 (143k) cells. The published seed-4 "late" checkpoints
  are a run restarted from near the initialisation after the divergence, uploaded under the original step names.
- **Seed 3:** step 96000 correlates 0.05–0.55 with its predecessor at 64000 and at most 0.66–0.91 with ANY earlier
  revision (best: step 0/1000), then 128000 and 143000 continue from 96000 (0.93–0.998). → RESTART on 6/6 cells at 96k:
  a restarted run (not a resume from a stored checkpoint of the same run), partially trained by 96k.
- **Seed 1 (control):** CONTINUATION on 18/18 cells; predecessor correlations 0.91–0.99, decreasing with grid distance.
- Readings: the "late loss spikes" of seeds 3 and 4 (FINDINGS_MEMO §2; final losses 2.475 / 2.857) are not instabilities
  inside a trajectory but a comparison of early-training states (restarted runs) against late ones; open lead 6 ("seed 4's
  spike as a natural experiment") is WITHDRAWN; MF_EXPLORE §3's "seeds 3 and 4 lose the deep-band localisation after their
  spikes" is the same artefact (an early-training state has not yet formed it); PolyPythias' own account of these two
  runs (deviate "long before", σ_λ drop) should be re-read in this light. The seed rows of the sealed verdict stand as
  MIXED, with the ≥ 0.80 fraction (25 %) carried by seeds 3/4 and MLP_IN; on seeds 1/2/5 alone the 410M row would read
  frac ≥ 0.80 ≈ 0.07 (MLP_IN only), frac ≤ 0.20 ≈ 0.55 — MIXED still, closer to LEARNED.
- For every later use: PolyPythias 410M seeds 3 and 4 are VALID only through step 64000 (seed 3) and 96000 (seed 4);
  their later revisions are a different training segment. Stage 3 seed results that used them at 143000 (STAGE3_SEED_FINDINGS,
  FINDINGS_MEMO rows 1/5–10 "10 seeds") need a dated note: those two seeds' final-checkpoint cells are not end-of-training
  states.

## 4. What this settles for arm A (ARMA_PREREG_SKELETON §0, H_RES)
- "The trained bulk is the initialisation shrunk by weight decay" is **false for O, Q, K, MLP_OUT** at both sizes
  (ρ_bulk ≤ 0.27, E_init ≤ 1 %) and **partly true for MLP_IN** (0.73) and V (0.3–0.4). The reservoir reading therefore
  cannot be settled by the init alone: a bulk that has left W₀ can still be a load-bearing random-feature reservoir
  (re-randomised by Adam noise rather than retained), which is exactly what the co-adapted calibrator tests. Arm A's
  calibrator stays necessary; this test removes one cheaper route to the answer and adds a per-type prior (O first).
- The scope statement of A1 holds: Pythia keeps far more init than a tuned modern run would (τ ≈ 0.64 vs τ_opt ≈ 0.06),
  and still its bulk energy is < 1 % init at the end.
