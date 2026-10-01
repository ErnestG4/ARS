# A0r — identical-config rerun of A0 (paired-run divergence floor for Q1). SEALED before A0r exists.

**Written 2026-10-01, before any A0r step is trained.** Will's call (10-01): "the matching null is an identical-config
rerun of A0 … GPU nondeterminism compounds chaotically, and over 3,000 steps paired reruns can drift apart further than
you'd expect … it decides whether Q1's verdict survives."

## 1. What runs
- `train.py A0r`: the same code path as A0 (commit of this seal), the same init (`EleutherAI/pythia-70m` step 0), the
  same Pythia batch order, W = 1430, stop 3000, the same B1a grid (`grids.arm_grid("A0r", 3000)` = A0's grid; grids.py is
  sealed and unchanged — `stop` is passed explicitly). The ONLY code change is the `ARMS` entry `"A0r": (1430, 3000)` in
  train.py (not a sealed file). No B-G1 gate puller (A0 only); A0r is a null-pair run, not an anchor.
- The only intended difference from A0 is GPU nondeterminism (compiled kernels, fused AdamW, atomics). Nothing else is
  varied. If anything else is found to differ (package versions, data bytes, init hash), it is disclosed and the run is
  labelled accordingly, not re-run silently.
- Checkpoints go to spot:`~/llmspec_armb/ckpt/A0r/` (sha256 .ok markers), ~47 GB, like A0.

## 2. Reading rule (declared now)
- **Known-answer test of the Q1 pipeline.** A0r is scored by the SEALED Q1 code (b4_extract → q1 warp licence v2)
  exactly as A2 was, with A0 as the reference, via a wrapper that substitutes only the arm name (committed before any
  A0r data is read). An identical-config run must read as the IDENTITY (STEP) map within the licence's noise. If the
  sealed pipeline instead returns NO SIMPLE ANCHOR or a preferred non-identity map for A0r, then Q1's A2 verdict is
  downgraded to **NOT RESOLVABLE at this noise model**: the licence noise (curve roughness, 0.2–0.3%) is smaller than
  paired-run divergence, and A2's 2.4% misfit is not separable from it.
- **Descriptive floor c_pair.** For each Q1 metric, the relative RMS residual between A0 and A0r under the identity map
  over the Q1 window, in the same units as the A0→A2 misfit (ARMB_FINDINGS §2). Reported beside the Q1 verdict.
  c_pair is ONE draw of paired divergence (n = 1): it is a measured floor, not a distribution.
- **Verdict table:** (a) identity within noise AND c_pair < A2 misfit by the licence's own margin → NO SIMPLE ANCHOR
  stands, with c_pair quoted; (b) identity within noise but c_pair ≥ A2 misfit → NOT RESOLVABLE (the misfit is within
  paired divergence); (c) non-identity verdict for A0r → NOT RESOLVABLE (pipeline mis-reads a known null). No other
  outcome is scored.
- Nothing in q1_licence / q1_warp_v2 / b4_extract / b4_analyze is edited (B4 seal, armb/B4_SEAL.json).

## 3. Also banked for later (not read as evidence here)
- A0 vs A0r divergence trajectories per metric (where the pair separates: the earliest step at which the paired
  difference exceeds the A0 curve roughness) — descriptive, for the Q2 wave-without-layer-0 and bulk-count nulls.
