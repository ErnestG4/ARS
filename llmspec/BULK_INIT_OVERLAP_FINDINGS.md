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

## 3. The spike seeds (3 and 4) are a provenance anomaly, not a dynamics result (PROVENANCE CHECK RUNNING)
- Seed 4 (loss spike 96k–128k): ρ_bulk 0.195 at 96000 → **0.993 at 128000 → 0.969 at 143000**; α̂ 0.265 → 0.972 → 0.893;
  d 0.996 → 0.263 → 0.475; E_init 0.003 → 0.942 → 0.778. The 128k checkpoint is, to three digits, the signature of a
  ~step-1000 checkpoint of a normal run (ρ_bulk 0.99, α̂ 0.97, d 0.3): the weights are the initialisation at nearly full
  amplitude with a small learned part. Continued training cannot produce that from a 96k state (the init amplitude was
  already decayed to 0.13 by then).
- Seed 3 (spike 64k–96k): ρ_bulk 0.225 at 64000 → **0.794 at 96000** → 0.681 → 0.651; α̂ 0.336 → 0.705 → 0.579 → 0.545 —
  the signature of a ~8k-step state, then continuing decay.
- Reading (pending the direct check): the late checkpoints of seeds 3 and 4 are not continuations of their own earlier
  checkpoints; they look like training RESTARTED from an early checkpoint (seed 4: ≈ step 1000; seed 3: ≈ step 8000)
  after the divergence, with the restarted run's later steps uploaded under the original step names. If so, the
  "late loss spikes" in FINDINGS_MEMO §2, open lead 6 ("seed 4's loss spike as a natural experiment"), the MF_EXPLORE §3
  remark that seeds 3/4 "lose" the deep-band localisation after their spikes, and PolyPythias' own reading of these two
  runs are all the same artefact: an early-training state compared against late ones. `polypythias_restart_check.py`
  (reading rule in its docstring; seed 1 as control) is running on spot; this section is finalised from its output.
- Until then the seed rows stand as sealed (MIXED), and the 25 % "≥ 0.80" fraction in the 410M row is noted as carried
  almost entirely by seeds 3 and 4 plus MLP_IN.

## 4. What this settles for arm A (ARMA_PREREG_SKELETON §0, H_RES)
- "The trained bulk is the initialisation shrunk by weight decay" is **false for O, Q, K, MLP_OUT** at both sizes
  (ρ_bulk ≤ 0.27, E_init ≤ 1 %) and **partly true for MLP_IN** (0.73) and V (0.3–0.4). The reservoir reading therefore
  cannot be settled by the init alone: a bulk that has left W₀ can still be a load-bearing random-feature reservoir
  (re-randomised by Adam noise rather than retained), which is exactly what the co-adapted calibrator tests. Arm A's
  calibrator stays necessary; this test removes one cheaper route to the answer and adds a per-type prior (O first).
- The scope statement of A1 holds: Pythia keeps far more init than a tuned modern run would (τ ≈ 0.64 vs τ_opt ≈ 0.06),
  and still its bulk energy is < 1 % init at the end.
