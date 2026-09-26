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
