# MORNING_G — CF-convergence-rate bridge: PARTIAL (magnitudes + Farey-governance transfer; a=1 monotonicity trips)

Branch `cf-convergence-bridge` off `pi292-sparse-eigensolve` (44a7ca1 — needs the certified fast solver; main lacks
it). `/home/combust/fmexplorer/bin/python3`, `PYTHONPATH=…/riemann_explorer`, `BASE_SEED=20240517`. main/refsuite
untouched. numba fast solver (E-run) is the tool.

## Layer-zero gates — PASS
1. **Solver regression:** reproduces banked bit-for-bit — π q6=66317 → **0.63681 == E-run banked**, fifth q=15601 →
   **0.4660 == banked dense**, π q113 → 0.6276. Not drifted since 44a7ca1.
2. **Fifth CF re-gate:** three-precision CF depth 48; records (1,1),(3,2),(5,3),(7,5),**(9,23)**,**(14,55)** — a=23@9
   (q=15601), a=55@14, from certified computation.
3. **Completeness:** count_eq_q Sylvester-rigorous at every new depth (10–13).

## In-sample fit (π depths 1–8) — the law
`dim_n = ln q_n/ln(q_n/W_n)`, W thinning per step: a≥2 → λ·g(a); a=1 → f(older-block fraction). Fit **in-sample on
π's own steps**: a8=2 → **g(2)=0.844**; the four a=1 steps → the a=1 curve at fractions {0.003,0.062,0.334,0.499}
→ factors {1.00,1.00,1.74,4.18}. (Note: π's single a=2 gives g(2)=0.844, higher than the metallic/fifth ~0.638 —
a transfer risk flagged before sealing.)

## Sealed out-of-sample prediction + blind measurement (fifth depths 10–13, beyond the old q=15601 frontier)
Sealed byte-locked before measuring; pipeline frozen. All four steps are **FAREY-ONLY** (below the a=23 record).

| depth | a | q | measured | predicted | resid | step |
|---|---|---|---|---|---|---|
| 9 | — | 15601 | 0.4660 (anchor) | — | — | — |
| 10 | 2 | 31867 | 0.45351 | 0.44421 | +0.009 | DROP |
| 11 | 2 | 79335 | 0.44282 | 0.43115 | +0.012 | DROP |
| 12 | 1 | 111202 | **0.44432** | 0.43096 | +0.013 | **RISE** |
| 13 | 1 | 190537 | 0.43489 | 0.42671 | +0.008 | DROP |

## Verdict — **PARTIAL** (sealed monotonicity falsifier TRIPPED, honestly)
- **Magnitudes transfer within tolerance:** max |measured−predicted| = **0.013 < 0.02**. A systematic +0.008…+0.013
  offset — exactly π's g(2)=0.844 over-thinning the fifth's a=2 steps (fifth's true g(2)≈0.638).
- **BUT the sealed strict-monotonicity falsifier TRIPS at depth 12:** the a=1 step at older-block fraction 0.287
  **rose** (+0.0015) where the π-fit law predicted a marginal drop. The a=1 factor curve does not transfer precisely
  — the fifth's factor at f=0.287 is 1.40 (≈ its q-growth 1.40 → dim ~flat/rise) vs the π-fit 1.58 (→ marginal drop).
  Depth 12 sits right at the rise/drop crossover, so a small factor error flips the direction. **Not rescued.**
- **Residual analysis (pre-registered) — the valuable part.** Residuals are ~flat (+0.008…+0.013, std 0.002),
  **not cusp-structured** — a uniform g(2)/a=1 transfer offset, not a missing structural channel. And critically:
  **all four FAREY-ONLY steps were predicted to within 0.013 by the FAREY-COMPLETE law** — a record-only law would
  be *blind* to them. So **convergence is Farey-governed (non-record), confirming the Session-C §9 record/Farey
  non-equivalence** empirically: the running-record channel alone cannot set the convergence rate; the Farey channel
  is essential.

## What this means for the arc
- The convergence-rate mechanism is **directionally-general for a≥2 steps and magnitude-general within a
  context-dependent g-offset**, and its **Farey-channel nature is confirmed out-of-sample**. But it is **not** clean
  enough to claim "class and reach fully readable from the CF": the a=1 fine structure (at the rise/drop crossover)
  and g(2) carry context-dependence that break strict transfer. So the framing upgrades to: **the CF's Farey channel
  sets convergence rate up to context-dependent per-step factors** — a real but qualified gain, not the full upgrade.
- E-run's π retreat stands (in-sample). The fifth departure is a transferability limit, banked plainly.

## Close
Committed on branch; main/refsuite untouched. Artifacts: `G_insample_seal.py`, `G_fifth_prediction_SEALED.json`,
`G_measure_blind.py`, `G_fifth_measured.json`, `G_seal_verdict.json`, `G_fifth_bridge.png`. Carry-forward: (a) the
context-dependence of g(2) and the a=1 factor curve is the next probe — are they predictable from CF neighborhood?
(b) the Farey-governance of convergence is now empirical — a clean §9-adjacent result; (c) reaching the fifth's a=55
cusp (depth 14, q≈1.06e7) is beyond the O(q²) solver (~days) — a numba-prange win only gets ~10× more, so q~1e7
needs a better algorithm (banked).
