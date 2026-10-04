# Arm A — review packet for Will before the seal (2026-10-04)

The document to seal is `ARMA_PREREG_SKELETON.md` (unchanged here except the per-type priors added 10-04). This packet
lists (A) your two named checks, (B) every open `[TBD]` with a proposed value, (C) each lit-v2 design change with a
recommendation, and (D) what this week's results imply. Nothing below is in force until you seal it. Prediction figure:
`seals/armA_predictions.png` (needs the per-type panel rows before sealing).

## A. Your two checks
1. **Scale axis = spectral octaves. ✓, with one choice to make.** §2 defines octave bands by singular-value INDEX from
   the spike edge: B_j = [s₀2ʲ, s₀2ʲ⁺¹). That is octaves of spectral RANK (d = 2048 → 6 octaves, 1.8 decades). The
   alternative is octaves of singular-VALUE magnitude. Inside the MP bulk the two are monotonically related but not
   proportional, so they bin differently. **Proposal: index octaves (as drafted)**, because every report (P_j, costs)
   is a sum over directions and index bands hold the direction count per band fixed in log steps; σ-octaves reported
   descriptively.
2. **MLP_IN = the declared reservoir candidate. ✓** §0 per-type priors: H_RES predicts RESERVOIR for MLP_IN with the
   smallest calibrator gap (bulk keeps 0.73 of its init content at 1.4B and 410M); O, Q, K are the learned-function
   candidates, O the most informative (0.06 init content, MP-shaped). Never pooled across types.

## B. Open `[TBD]`s, with proposals
| § | item | proposal | why |
|---|---|---|---|
| 1 | models | Pythia-70M (own infra, calibrator fine-tunes) + Pythia-410M standard for the perturbation arm | 410M-std is held out for arm B's bulk vectors, so it is clean for arm A; 1.4B too costly for the calibrator fine-tunes |
| 1 | probe set X | 64 × 2048 tokens of the Pile validation split, hashed; plus order-shuffled and Zipf+LRD sets (lit v2) | real vs structure-destroyed probes separate data-kernel scale from architecture |
| 1 | checkpoints | final (143k) + one mid checkpoint + step 0 sanity | mid at 8k–16k, where ρ_bulk crosses 0.5 (BULK_INIT §2): the bulk is half-left the init there |
| 2 | s₀ | 32 at d = 2048, 16 at d = 1024 (scaled ∝ d) | see D2: the [32, 64) octave behaves like the top (0.90 init content), so s₀ = 32 may be too low — consider s₀ = 64 or report [32, 64) separately |
| 2 | doses | 5, geometric, factor 2 | regime check needs ≥ 3 in the quadratic range |
| 2 | N_k (random subspaces) | 32 per k | CV² needs ~30 draws for a ±25 % estimate |
| 2 | linearity tolerance | successive-dose cost ratio 4 ± 25 % | quadratic regime ⇔ ratio 4 at factor-2 doses |
| 4 | ε_rec | probe loss within 0.01 nats of the original | the G2 bulk-shuffle cost was +2.66 nats; 0.01 is < 0.5 % of it |
| 4 | replicates | 3 | the skeleton's floor |
| 5 | planted α | 1.6–1.7 (lit v2: 1 + α_SAE, Michaud et al.) and 1.0 | one data-motivated, one generic |
| 6 | min octaves | 4, counted on MP-interior octaves only (lit v2) | the first octave violates AEK flatness (lit v2 item 8) |
| 6 | ε (flat) | 2 × the calibrator replicate SD per band | ties FLAT to the measured noise |
| 6 | CV² slope tolerance | −1 ± 0.2 | sampling SD of a fitted log-log slope over 8 k values ≈ 0.1 |

## C. Lit v2 design changes (lit/v2/S.md §5 + item 1), with recommendations
| # | change | source | recommend |
|---|---|---|---|
| C1 | **§6 verdict table:** the generic data prediction for P_j is a U-shape or a knee at a data-kernel scale, not a power law; "break elsewhere → anomaly" misreads it; SELF-SIMILAR must mean "exponent ≠ calibrator's" | Staats v3; Karkada Cor. 2 (HIGH) | **ADOPT** — add U-SHAPE and KNEE (data-kernel) verdict regions; drop "anomaly" |
| C2 | Record Staats' decile-removal shapes as prior art before the seal (Q/K/V monotone decreasing, O ≈ flat, MLP up/down U-shaped, Pythia-410m) | Staats v3 | **ADOPT** — draw them as the "known" panels in the prediction figure |
| C3 | §0: H_KNEE split into architectural (d_head) vs data-kernel scale | lit v2 | **ADOPT** |
| C4 | §0: "run test #1 first; its word funds §4" | lit v2 | **DONE** — BULK_INIT_OVERLAP ran: MIXED, rules out the shrunk-init reading, so the calibrator is the only deciding null (§0 priors) |
| C5 | §1: probe sets real / order-shuffled / Zipf+LRD; context length as a knob; mid checkpoint at a phase boundary | Montemurro & Degli Esposti; Yang et al.; Li et al. | **ADOPT** probes and mid checkpoint; context length descriptive only (cost) |
| C6 | §2: allow negative antithetic costs (negative Hessian eigenvalues in mlp.up); bank (3 − 1×2) | Dauphin et al.; Meterez et al. (item 6) | **ADOPT** — matters most for MLP_IN, the reservoir candidate |
| C7 | §2: split-half reproducible rank k* beside CV² | Thomas 2607.05872 | **ADOPT** as descriptive |
| C8 | §3: calibrator P_j on the calibrator's own post-fine-tune activations | Nakamuta & Teramae | **ADOPT** |
| C9 | §4: name the primary calibrator — Haar-within-subspace vs rainbow resample | Guth et al. | **Haar-within-subspace primary** (as drafted); rainbow as a sensitivity row. See D4 |
| C10 | §5: plant α ≈ 1.6–1.7; hierarchical-kernel plant; order-2 clone null | Michaud; Nava & Wyart; Rende et al. | **ADOPT** α and the hierarchical plant; clone null if cheap |
| C11 | §6: add U-shape and Lorentzian fits; min-octaves on MP-interior octaves only; pool within type only | Karkada; AEK; Ormaniec et al. | **ADOPT** — "within type only" matches the per-type priors |
| C12 | §3 caution "3 = 1 × 2" holds for the Gauss–Newton part only | item 6 | **ADOPT** as a stated limitation |

## D. What this week's results imply for arm A
1. **The calibrator is the only deciding null** (bulk–init overlap): the bulk is not the init shrunk by weight decay
   (0.5 % of its energy), so H_RES can only be decided by the co-adapted random bulk. Per-type priors are in §0.
2. **The spike edge is not where the init-memory edge is.** Top-32 content correlates 0.86 with W₀, the next octave
   [32, 64) 0.90, the bulk 0.24, the deepest octave 0.11 (1.4B). With s₀ = 32 the first "bulk" octave is init-like and
   also violates AEK flatness (lit v2 item 8). **Proposal: s₀ = 64 at d = 2048, or keep 32 and make [32, 64) its own
   reported band excluded from the fits.** Your call; it changes the octave count from 6 to 5.
3. **The small edge is where learned structure sits** (deepest octave least init-like; Staats' small-edge overlap;
   MF_EXPLORE §3). Arm A's last octave should be predicted, not just fitted: under H_SS and under Staats, P_j rises at
   the small edge (a U-shape), which C1 makes a verdict region instead of an anomaly.
4. **Confusables must carry the substrate's own nuisance structure** (OLMo premise: a battery with smooth stand-ins
   licensed a rule that the real row-norm shape broke). For arm A: the Haar-within-subspace calibrator keeps σ and the
   top directions but changes how the bulk spreads over rows and columns. **Proposal: report the calibrator's row- and
   column-norm profiles against the trained matrix's as a nuisance check**, and plant the red-path models on the real
   densities and shapes, not smooth ones.
5. **Every statistic gets a known-answer licence on realistic shapes before it is read** (PDYN: a P2 statistic passed
   synthetic checks and still could not separate β = 2 from β = 1; its full-bin C(x) is under a realistic-shape check
   now). The §5 red path already does this for the verdicts; add the regime checks and CV² to it.
6. **Held-out data:** seeds 6–9, 410M-std, 1B and 70M bulk vectors are UNREAD (split-sample rule). Proposal B uses
   410M-std, which is clean for arm A, and must be named in §1. PolyPythias seeds 3 and 4 are valid only through 64k / 96k
   (restart discontinuity) if any seed is used.
7. **Cost order unchanged:** calibrator + red-path plants first (GPU), arm A proper after. The 4090 is free per NOTES §4.

## E. Decisions only you can make
1. s₀ = 64, or s₀ = 32 with [32, 64) reported separately (D2).
2. Index octaves (proposed) vs σ-value octaves (A1).
3. Which released size for the perturbation arm: 410M-std (proposed) vs 1.4B.
4. Adopt C1–C12 as recommended, or name exceptions.
