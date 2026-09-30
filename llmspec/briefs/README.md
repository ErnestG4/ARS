# llmspec/ — Shapes of LLM weights and transforms over training

Governing brief: CC Brief v1.1 (Will, 2026-09-25; supersedes v1). Will's answers to §8 (2026-09-25):
1. Stage 1 peak criterion = MP-calibrated KDE (sealed: seals/stage1_peak_criterion.json, stage1_calibrate.py).
2. Arm B (AdamW vs Muon) = HOLD.
3. Bulk NNS / <r~> beta=1 null = ADOPTED as a pre-registered instrument check (sealed before Stage 3).
Download budget: no cap (stream single tensors by HTTP range; remote_st.py).

Brief corrections found at execution (G4): Pythia `stepN` revisions store F32 safetensors (only `main` is F16);
OLMo 2 1B checkpoints are stored F32, not bf16. Whether the F32 values sit on an fp16/bf16 grid is measured per
tensor (specs.grid_audit) and reported with every result.

Interrupt: `touch llmspec/STOP` (clean exit between tensors). Resume: rerun the same command (per-layer cache).
