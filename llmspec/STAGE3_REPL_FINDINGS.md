# G3 replication findings (STAGE3_REPL_PREREG.md, 8147f53; scorer stage3_repl.py, validated on 1.4B in STAGE3_FINDINGS §14)

## Pythia-1B (16 L × 8 H × 256, 26 revisions; completed 2026-09-26 09:52)
- **A. Sealed null: HOLDS in 260/260 cells.**
  - Worst |Δ⟨r̃⟩| 0.0058 (per-head K); worst |Δq| 0.026. Tolerances 0.010 / 0.10.
  - G0 MP passes for all six types (≤ 2 of 16 matrices above KS95).
  - The 1B witness reads β=1 and is scale-invariant for all 10 types.
- **B. Replication criteria:**

  | R | criterion | 1B value | verdict |
  |---|---|---|---|
  | R1 K rotary | ≥ null + 0.10; rotary-row norm ≤ 0.27 | 0.549 vs 0.251; rows 0.194 | **REPLICATES** |
  | R2 cross-head sharing | Q and K below the input-rotation null | Q 0.217 < 0.528; K 0.219 < 0.599 | **REPLICATES** |
  | R3 update-rank rise | 15k/1k ratio ≥ 3 for ALL six types | Q 5.6, K 8.5, MLP_IN 19.1, MLP_OUT 3.5, **V 2.98, O 1.80** | **DOES NOT REPLICATE** |
  | R4 OV before QK | at step 512: OV out ≥ 0.5, QK out ≤ 0.2 | OV 0.945, QK 0.164 (OV already 0.906 at 256) | **REPLICATES** |
  | R5 induction | first max-induction ≥ 0.3 at 1000 or 2000 | (512, 1000) | **REPLICATES** |
  | R6 MP-fit collapse | Q and K ≥ 90% of layers failing by 2000 | Q 1.00, K 1.00 (already 1.00 / 0.94 at 1000) | **REPLICATES** |

- **R3 as registered does not replicate.** The update-rank rise holds strongly for Q, K and both MLP matrices, but
  the OV path rises much less at 1B: O 67 → 121, V 36 → 106.
  - V misses by a hair (2.98); O clearly (1.80).
  - The 1.4B statement "every type's update rank rises 5–15×" is therefore not size-general. The sound reading is
    "QK and MLP updates become much higher-rank at constant LR; OV updates less so, size-dependently".
  - That reading is post-hoc and is reported as such.

## Pythia-410M (24 L × 16 H × 64, 26 revisions; completed 2026-09-26 12:54)
- **A. Sealed null: HOLDS in 260/260 cells.**
  - Worst |Δ⟨r̃⟩| 0.0069 (MLP_OUT); worst |Δq| 0.089 (per-head Q).
  - Per-head spectra have only 64 levels here, so q is noisier; still within the 0.10 tolerance. G0 passes for all six
    types.
- **B. Replication criteria:**

  | R | 410M value | verdict |
  |---|---|---|
  | R1 K rotary | mass 0.465 vs null 0.249 (+0.216, passes); **rotary-row norm share 0.2704 > 0.27 ceiling** | **DOES NOT REPLICATE** (norm clause, by 0.0004) |
  | R2 cross-head sharing | Q 0.240 < 0.559; K 0.147 < 0.438 | **REPLICATES** |
  | R3 update-rank rise | Q 6.8, K 9.0, MLP_IN 14.5; **V 1.89, O 1.43, MLP_OUT 2.11** | **DOES NOT REPLICATE** |
  | R4 OV before QK | step 512: OV 0.987, QK 0.034 | **REPLICATES** |
  | R5 induction | (512, 1000): 0.005 → 0.906 | **REPLICATES** |
  | R6 MP-fit collapse | Q 1.00, K 1.00 by 2000 | **REPLICATES** |

- **R1 fails as registered, on the norm-control clause only.** At 410M the rotary rows carry 27.04% of K's norm
  (slightly above isotropic 25%). The registered ceiling was 27%. The concentration itself (0.465, nearly 2× the
  null) replicates. The verdict stands as sealed. The reading that the concentration greatly exceeds what a 27%
  norm share implies is post-hoc and not a test.
- The equal-interval LR fields were corrected with the model's own peak (3e-4; ratio exactly 1.500), as for 1B. R3 uses
  stable ranks and was unaffected.

## Across sizes (1.4B / 1B / 410M)
| | 1.4B | 1B | 410M |
|---|---|---|---|
| Sealed bulk null | HOLDS 260/260 | HOLDS 260/260 | HOLDS 260/260 |
| R1 K rotary | ✓ (0.484; rows 0.227) | ✓ (0.549; rows 0.194) | ✗ norm clause (0.465; rows 0.2704) |
| R2 cross-head sharing | ✓ | ✓ | ✓ |
| R3 update-rank rise ≥ 3× all types | ✓ (min 4.2) | ✗ (V 2.98, O 1.80) | ✗ (V 1.89, O 1.43, MLP_OUT 2.11) |
| R4 OV before QK | ✓ | ✓ | ✓ |
| R5 induction (512, 1000) | ✓ | ✓ | ✓ |
| R6 MP-fit collapse by 2000 | ✓ | ✓ | ✓ |

- **Size-general** (all three): the sealed null; R2 cross-head sharing; R4 OV departing before QK (at step 512 the OV
  fraction is ≥ 0.945 while QK is ≤ 0.164); R5 induction forming at 512–1000; R6 MP-fit collapse by step 1000–2000.
- **K rotary concentration (R1):** the concentration replicates at every size (0.465–0.549 vs ~0.25 null). The
  registered norm-control clause fails at 410M by 0.0004.
- **R3 is not size-general** (post-hoc pattern, not a test): output-side update ranks (V, O, then MLP_OUT) rise less
  the smaller the model. QK and MLP_IN updates rise ≥ 5.6× at every size.
- **Next:** the PolyPythias seed leg (410M, 9 seeds + standard) scores exactly these criteria per seed (running since
  12:54).
