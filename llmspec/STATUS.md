# llmspec STATUS — the one-page roll-up (updated 2026-10-03 18:40; previous roll-up 09-30)

**Read order:** this file (where every arc stands, with its word) → NOTES.md §4 (running log, jobs, queue) → the arc's
findings file. FINDINGS_MEMO.md holds the sealed headline rows with gates; README.md the plain-language version.
Interrupt any job: `touch llmspec/STOP`. Jobs are launched/checked through `jobs.sh` (pid file + /proc/<pid>/exe).

## Where things stand (by arc; words are the sealed vocabulary)
| Arc | State | Word(s) | Where |
|---|---|---|---|
| Stage 1 / 1b (existence of peaked spectra) | done 09; **re-read 10-03** | Pythia: none (weak null); OLMo stage-1 end: **NOT LICENSED (row-norm confusable)** — the multimodal heads are the row-norm-bimodal heads | STAGE1_FINDINGS, OLMO_PREMISE_FINDINGS, memo row 3 |
| **OLMo premise** | **done 10-03 (sealed)** | **NOT LICENSED (row-norm confusable):** own-row-norm Gaussian blocks read multimodal 21 % / 8 % vs observed 25 % / 13 %; T3 Fisher 1e-16; folded branch not licensed (gain); endpoint identical (descriptive); dead rows have gain ≈ 0 (98 %); no weight-decay conclusion (only 400 dead rows banked). The OLMo trajectory plan loses its premise. | OLMO_PREMISE_FINDINGS, results/olmo_premise.json |
| OLMo `main` provenance | done 10-01 | DIFFERENT RUN from the stage-2 lineage (no fade claimed) | results/olmo_main_provenance.json, memo row 3 |
| Stage 2 (G7) | done 09 | NOT LICENSED as registered | STAGE2_FINDINGS |
| Stage 3 (Pythia-1.4B bulk null; 410M seeds) | done 09 | bulk null HOLDS 260/260 per model; late-Q departure NOT ESTABLISHED; rows 5–10 replicate; band descriptives reported | STAGE3_*, memo rows 1–10, §16 |
| PolyPythias seeds 3/4 provenance | done 10-03 | the uploaded trajectory is DISCONTINUOUS at a restart (seed 3 from 96k, seed 4 from 128k); valid through 64k / 96k; lead 6 withdrawn | BULK_INIT_OVERLAP_FINDINGS §3, polypythias_restart_check.py |
| **Bulk–init overlap** (how much of the trained bulk is the init) | done 10-03 (sealed) | MIXED (1.4B and 410M seeds); rules out "bulk = init shrunk by WD" (0.5 % energy); α̂ > α_wd red flag opposite sign; O lowest, MLP_IN highest; the co-adapted calibrator is now the ONLY deciding null for H_RES | BULK_INIT_OVERLAP_FINDINGS, verdict.json |
| Arm B B4 (AdamW vs Muon, 70M) | done 09-29 | Q4: timing and depth of the Q/K fall depend on the optimizer (123/368 cells); Q3 INCONCLUSIVE; bulk null at MDD | armb/ARMB_FINDINGS, memo rows 15–16 |
| Arm B Q4EXT (A0/M0s1 → 10000, M0s3 → 3000) | done 10-03 (descriptive) | AdamW Q/K stable rank DIPS to a minimum near 3000 and RECOVERS to 17/15 by 10000; Muon plateaus; Muon σ₁ grows but < AdamW's Q/K σ₁ at 10k; one-draw Muon spread median 2.4 % | ARMB_FINDINGS §9, results/armb_q4ext_descriptive.json |
| Arm B A0r (identical rerun; Q1 floor) | done 10-01 | NOT RESOLVABLE (TP_O identity fit ratio 13.3 > c_fit) | ARMB_FINDINGS §2b, A0R_PREREG |
| Arm B pdyn (parametric spectral dynamics) | phase 1 done 10-02 | P2 FAILS vs C1 as sealed (attributed to the calibrator's velocity memory; OU τ_v 5–10 reproduces); P3 HOLDS; P5 PROVISIONAL; A1 (C1′) DRAFT for Will | armb/PDYN_FINDINGS, PDYN_PREREG(_A1) |
| Arm B MF exploratory look | done 10-01 | impressions only (prior art: Staats v3 Fig. 10, lit v2 item 5); seeds 3/4 remark corrected | MF_EXPLORE_IMPRESSIONS |
| **Divisor Harmonics v0** (side project) | done 10-03 (sealed; A4 done) | numbers: **H1 HOLDS d = 2, 4, 5, 10** (1.4B; REPLICATES 410M, 70M; every layer); **frequency does not explain it** (A4 stratified null: d = 2, 5, 10 SURVIVE ×3, d = 4 at 410M–1.4B, NOT RESOLVABLE at 70M; A3 lowers no z (all rise slightly)); months NOT RESOLVABLE (power); hours H0 HOLDS d = 3, 4, bets NOT RESOLVABLE, parity 3/3 never past Holm | divisor/DIVISOR_FINDINGS §1–7b |
| Lit review v2 | done 10-02 | nine agents + verifier + critic + synthesis; five plan-changing items (S §1); design changes per document (S §5) | lit/v2/S.md |
| Arm A (bulk-vector self-similarity) | **NOT STARTED**; skeleton + prediction figure | `[TBD]`s + lit-v2 design changes await Will; last in Will's order | ARMA_PREREG_SKELETON, seals/armA_predictions.png |

## Will's order (10-03) and what is left
lit v2 read ✓ → push ✓ (Will) → OLMO_PREMISE ✓ done → A4 ✓ done → arm A last. **Nothing is running or queued (10-04).**
Drafts on Will's desk, none in force: PDYN_PREREG_A1 (C1′), Q4EXT Amendment 2 (lit v2 columns; armb/Q4EXT_PREREG.md),
STAGE1B_LICENCE_AMENDMENT.md (own-row-norm confusable → calibration v2), arm A `[TBD]`s + lit-v2 design changes, and the
hours read position (only if hours are re-extracted).

## 09-30 and earlier
See git history (tag llmspec-2026-09-30 = the Zenodo commit; merged to main 2f79434) and NOTES.md §3.
