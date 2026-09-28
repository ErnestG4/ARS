# llmspec STATUS (brief v1.1 + Arm B) — updated 2026-09-28 14:55 PDT

**Read NOTES.md first**: it is the full state file (mandate, machine rules, code map, results with commits, queue,
lessons). This file is the short version. There is no fixed end time (Will, 09-26 04:50). The alarm cron was removed 09-27 ~09:20 (queue
empty). Interrupt: `touch llmspec/STOP`.

## Where things stand
- **Stage 1** (existence): the sealed KDE rule was non-evidence. The licensed dip test finds OLMo Q/K multimodality at
  stage-1 end and none in Pythia. Aim 1 deferred (the OLMo stage-1 trajectory is Will's call).
- **Stage 2** (G7): NOT LICENSED as registered (fails β=2). Raw ⟨r̃⟩ licensed.
- **Stage 3** (Pythia-1.4B): sealed bulk null HOLDS 260/260. G2/G2b: the bulk-shuffle cost is size-dominated.
  Equal-interval ΔW rank rises at constant LR. Change points not licensed.
- **G3 size replication:** 1B and 410M null HOLDS 260/260 each. R2 / R4 / R5 / R6 size-general. R1 fails at 410M;
  R3 fails at 1B and 410M.
- **Seed leg** (410M × 10 runs), COMPLETE (c2c635f):
  - Null holds everywhere (2 cells → DENSITY_ARTIFACT).
  - R2 / R4 / R5 / R6 SEED-ROBUST. R1 (2/10) and R3 (4/10) SEED-DEPENDENT, with spreads.
  - Frozen drift test (S1/S2): FINDING_CANDIDATE as sealed; calibrator fidelity (S2): INCONCLUSIVE as sealed.
  - **Addendum S4 (known-answer calibrator licence): the frozen calibrator manufactures q −0.0207 / −0.0164 under a
    true β = 1 (the observed residual was −0.0197). q arm NOT RESOLVABLE (no calibrator within ±0.005 at N = 64);
    ⟨r̃⟩ arm quiet under the licensed v2_c16 (−0.00086, t₉ −1.6), with power against the claimed size (S4-sup).
    The per-head-Q drift is NOT established.**
  - QK-product "function" reading WITHDRAWN (a realistic density alone moves q by ~0.12 under β = 1).

## Running (auto) — Arm B (09-28 01:55)
- **A0 v2 COMPLETE; B-G1 PASS at all 14 steps 0–3000** (worst |z| 1.87 vs T 5.67).
- **A1 COMPLETE** (14:29, 5000 steps). **A2 training** since 14:29 on the dense grid (B1a-A8; replica check passed), ETA
  ~21:00.
- **Pending Will:** fix the Q1 E4 licence's HALFWAY confuser, which coincides with the LR_INT map (b121908). Decide
  before B4 reads any arm.
- **Queue:** A0 → [B-G1 3000] → A1 (to 5000) → A2 → M0s1 (via chain_after.sh 447697) → M0s2.
- **spot:** B-G1 daemon (tmux claude:0). Seed-1 batches COMPLETE (3000/3000, MANIFEST consistent).
- **Alarms:** cron d06bd494 at :13/:43 (Will asked). memwatch 12700.
- **Will, morning:** rotate the ssh agent (/tmp/cc-agent.sock) before ~13:05; A1 uploads checkpoints then.
- Earlier today: bf16 A0 aborted (A4); fp16 v1 FAILED B-G1 at 128 from loss-scale underflow, a diagnosis confirmed
  by a pre-committed test (A5); Muon update test PASS (A6); seed0 data known-answer 51,200/51,200 (A7).

## Held
- Arm B; OLMo stage-1 trajectory (Will's calls).
