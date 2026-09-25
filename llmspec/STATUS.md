# llmspec STATUS (brief v1.1) — updated 2026-09-25 12:05 PDT

Run window: until 09:00 PDT Sat 2026-09-26, alarm every 30 min (cron `7,37 * * * *`, session-only).
GPU in use (Will). Interrupt: `touch llmspec/STOP`. Resume: `./queue.sh <queue file>` (per-layer / per-checkpoint caches).
Since the 10:59 WSL crash: ONE heavy job at a time (`queue.sh`); `memwatch.sh` logs memory every 30 s to logs/memwatch.log.

## Done
- Stage 1 peak criterion SEALED (34de628) before any real spectrum was examined.
  Per-head (128x2048): h=0.0435, p*=0.002, holdout 0.990; resolves narrow peaks at separation >= 0.12 (w=0.01).
  Full-matrix (2048x2048): h=0.128, p* on the floor (0.0), resolves only >= 0.30 (coarse; stated).
- AMENDMENT A1 (post-hoc, declared) + spectra estimator v2 committed (ee83e79) BEFORE the analysis reruns.
- G4 findings: Pythia F32 checkpoints are fp16 upcasts (100% on the fp16 grid); OLMo 2 F32 are fp32 masters
  (bf16 grid at chance). The brief's "OLMo bf16" premise does not hold.
- Observation (pre-verdict): OLMo 2 Q/K heads carry dead query/key rows (L4h5 stage1-end: 105/128 rows at
  norm ~1e-28). This could drive part of the "multi-peak" density; A1 separates near-zero from bulk modes.

## Running (queue1.txt)
1. s1_spectra_v2_olmo (main, stage1-end, step0) -> 2. s1_spectra_v2_pythia (step143000, step0)
3. s1_analyze_v2 (sealed rule + A1) -> 4. s1_calibrate_v2check (seal re-derived under estimator v2; the
   per-head half already agreed before the crash: h equal to 3e-16, p* 0.002 identical).

## Queued
- Resume Pythia-1.4B checkpoint banking (12/26 banked; bank_checkpoints.py resumes .incomplete).
- Stage 2 (G7): stage2_g7.py written (pre-registration in its docstring), NOT yet dry-run, NOT committed.
  Targets come from the Stage 1 substrate decision. Commit prereg -> synthetic dry run -> real targets.
- Stage 3: seal the bulk-null pre-registration (aim 6) before any trajectory statistic; then Pythia-1.4B
  trajectory (G0 at step0, G1 witnesses, global/edge/vector/circuit observables).
- Arm B: HELD (Will).
