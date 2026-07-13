# MORNING_E-run — π-292 depths 6–8 measured; sealed retreat CONFIRMED

Branch `pi292-sparse-eigensolve` (continued). `$HOME/fmexplorer/bin/python3`,
`PYTHONPATH=…/riemann_explorer`, `BASE_SEED=20240517`. The certified inertia core (`sparse_floquet.py`, 5ab7b6e)
is unchanged; the only new code is a speedup wrapper. main/refsuite untouched.

## The wrapper (certified core untouched)
`sparse_floquet_fast.py`: the certified cyclic-tridiagonal inertia recurrence, **numba-JIT'd (`@njit`, identical
logic) and parallelized (`prange`) across the 2q independent per-eigenvalue bisections** (24 cores). The LDL
recurrence stays sequential *within* an eval; we parallelize *across* evals. Completeness stays Sylvester-rigorous
(`inertia(lo)==0`, `inertia(hi)==q` asserted per sector). **numba 0.66.0 installed cleanly into the venv.**

## Gate 1 — wrapper certification vs the certified core (make-or-break) — PASS
- JIT inertia == certified `inertia_cyclic`: **0 mismatches / 120 checks** (bit-identical recurrence).
- Fast vs serial core on overlap: π q=113 dim **0.62761** (W rel 3.1e-12); fifth q=665 dim **0.42016** (W rel 1.7e-8).
- Extended overlap vs **banked dense**: fifth q=15601 dim **0.4660 == banked 0.4660** (6.3 s). count_eq_q rigorous.
The wrapper reproduces the oracle to ≤1e-8 W / 5-digit dim, and is fast (q=665: 7.7 s → ~0 s). Trusted.

## Blind measurement (pipeline frozen, seal untouched)
`pi292_measure_blind.py` — frozen pipeline `bands_W_fast → W → dim = ln q/ln(q/W)`, no seal reference. On 24 cores:

| depth | q | count_eq_q | W | **dim (blind)** | wall |
|---|---|---|---|---|---|
| 6 | 66317 | ✓ (Sylvester) | 1.77850e-3 | **0.63681** | 119 s |
| 7 | 99532 | ✓ | 1.02235e-3 | **0.62566** | 263 s |
| 8 | 265381 | ✓ | 1.51368e-4 | **0.58676** | 1883 s |

(The RAM wall was the banked blocker; these ran in O(q) memory, ~38 min total. The recurrence's O(q²) compute wall
is cleared by JIT+parallel: numba stacks with `prange` to bring q₈ from ~weeks-serial to 31 min.)

## Unseal + verdict — **CONFIRMED**
`pi292_unseal_compare.py` opened the locked seal (`pi292_prediction_SEALED.json`, Session-D 352231a, byte-unchanged)
only after the blind dims were logged. Anchor dim5=0.6799 (banked).

| depth | measured | predicted | Δ | step |
|---|---|---|---|---|
| 5 | 0.6799 | 0.680 (anchor) | — | — |
| 6 | 0.63681 | 0.63632 | **+0.000** | DROP |
| 7 | 0.62566 | 0.62180 | +0.004 | DROP |
| 8 | 0.58676 | 0.59137 | −0.005 | DROP |

- **Direction (the load-bearing claim): CONFIRMED.** dim 0.680 → 0.637 → 0.626 → 0.587 — monotone retreat, exactly
  as sealed. The sealed falsifier ("dim rising / non-monotone up across 6–8") is **not tripped**.
- **Magnitudes also matched to ≤0.005** — better than the seal's own "estimates" caveat. Depth 6 essentially exact;
  depth 7 (flagged softest) had the middle deviation (+0.004) but still dropped and matched. So the Thouless a=1
  older-block-fraction calibration was *more* accurate than advertised — a bonus strengthening of the law.

## What this closes
The **π (a=292) finite-depth retreat is now MEASURED, not just predicted**, on the correct (Thouless) law — the
mechanism (post-292 consecutive a=1 steps are golden-regime, older-block fractions ~50%/33%, that thin W, plus the
a₈=2 step) is validated. This closes the finite-depth-direction question that opened when Liu–Wen fell out (Session D)
and AMO failed identification: **Liu–Wen wrong anchor, AMO wrong operator, but the Thouless-dim route is RIGHT** — and
now empirically confirmed to depth 8. The certified **parallel/JIT inertia solver is banked as a general asset** for
future deep-CF eigensolves (O(q) memory, Sylvester-complete, JIT-fast).

## Close
- Committed on branch; main + refsuite untouched. Carry-forward: (a) the intuited CF-convergence-rate bridge
  (measure-thinning ↔ cusp reach) now has a deep π datum (depths 6–8) to test; (b) the sparse solver is a reusable
  asset. Still queued unchanged: genus>0 FF calibrator (+β≈⅓·ln q), Gauss/Kloosterman concentration axis, the
  CF-cusp divergence-profile candidate. numba is now in the venv.
