# MORNING_H (Arm 1) — the a=1 crossover: monotonicity is DERIVED (form-universal, crossover-computable)

> **CORRECTION + EXTENSION (post-review, `H_direction_law.py` / `H_direction_law.json`).** Two fixes to the first
> pass below, one of which is my own over-claim:
> 1. **The crossover is NOT `factor = q-growth` (f\*≈0.287 universal).** The exact sign of dim_n−dim_{n−1}
>    (dim=L/(L+B), L=ln q, B=ln(1/W)) is: rise iff L_n/L_{n−1} > B_n/B_{n−1}, i.e.
>    **DROP iff ln(factor)/ln(q-growth) > (1/dim_{n−1} − 1)**. The threshold is **(1/dim−1), not 1** — they
>    coincide only at dim=0.5. So there is **no universal crossover fraction**; the crossover is a dim-dependent
>    surface. `g(1,f)=1/(1−f)` remains the exact *q-growth* (algebraic), but the "f\*≈0.287 straddle" was the
>    dim=0.5 simplification. Under the exact law the fifth's depth-12 **rises comfortably** (ratio 0.996 <
>    threshold 1.258) — which is *why* G's monotone-drop predictor tripped there, correctly explained now.
> 2. **General q-growth is a/(1−f), not a+f.** From q_n = a·q_{n−1}+q_{n−2}: 1 = a·(q_{n−1}/q_n)+f ⇒
>    **q-growth = a/(1−f)** (reduces to 1/(1−f) at a=1). Verified exact in all 17 banked rows.
>
> **The extension (banked, no new measurement):** the exact law predicts the direction of **ALL 17 banked steps
> (π 7/7 + fifth 10/10), a=1 AND a≥2**, including the big-quotient cases the simple version misses (π a=15 DROPS,
> fifth a=5 RISES — simple gets these backwards, 15/17). So the **full finite-depth DIRECTION structure is
> closed-form** in (a, f, dim, factor):  **DROP iff ln(W_{n−1}/W_n) > (1/dim_{n−1}−1)·ln(a/(1−f))**. The only
> non-closed piece is the thinning-factor **magnitude** (λ·g_metallic(a) for a≥2; g(1,f) for a=1), which carries the
> ~30% per-substrate scatter — that, not direction, is what e/cubics should probe. The 7/7 a=1 *directions* below
> still stand (robust); only the "universal crossover constant" framing is retracted.

---


Branch `crossover-surface` off `pi292-sparse-eigensolve` (needs the certified fast solver). numba fast solver the tool.
main/refsuite untouched. Artifacts: `H_arm1_seal.py`, `H_phi_prediction_SEALED.json`, `H_phi_measured.json`,
`H_phi_verdict.json`, `H_arm1_crossover.json`, `H_crossover_surface.png`.

## Layer-zero
1. **Definitions from the certified pipeline:** per step, `factor_n = W_{n-1}/W_n` (W from `bands_W_fast`);
   `q_growth = q_n/q_{n-1}`; `margin M_n = ln(factor_n) − ln(q_growth)`, sign(M) = retreat (M>0 ⇒ dim drops). For a=1,
   `factor_n = g(1, older-block fraction q_{n-2}/q_n)`.
2. **φ CF = all-1s, q_n = F_{n+1} (Fibonacci)** — exact integer gate, PASS.
3. **Regression:** solver reproduces banked bit-for-bit; count_eq_q Sylvester-complete at every φ depth.

## In-sample a=1 table + sealed curve (π + fifth only)
| fraction | g(1,f) | substrate |
|---|---|---|
| 0.003 | 1.00 | π a5 |
| 0.062 | 1.00 | π a3 |
| 0.226 | 1.06 | fifth a6 |
| 0.287 | 1.40 | fifth a12 |
| 0.334 | 1.74 | π a7 |
| 0.416 | 3.55 | fifth a13 |
| 0.499 | 4.18 | π a6 |

π and fifth points **interleave onto one monotone curve**. Sealed g(1,f) byte-locked before φ.

## The headline — **the a=1 margin is COMPUTABLE; the crossover is exact**
For any a=1 step, q_n = q_{n-1}+q_{n-2} ⇒ **q-growth = 1/(1−f)** exactly. So the crossover M=0 is precisely
**g(1,f) = 1/(1−f)** — and it predicts the direction of **all 7 banked a=1 steps across π/fifth/φ (7/7)**:

| substrate | f | g | 1/(1−f) | margin | predicted | banked |
|---|---|---|---|---|---|---|
| π a5 | 0.003 | 1.00 | 1.003 | −0.003 | RISE | RISE ✓ |
| π a3 | 0.062 | 1.00 | 1.066 | −0.064 | RISE | RISE ✓ |
| fifth a6 | 0.226 | 1.06 | 1.293 | −0.195 | RISE | RISE ✓ |
| **fifth a12** | **0.287** | **1.40** | **1.402** | **−0.002** | **STRADDLE** | rose (G falsifier) ✓ |
| π a7 | 0.334 | 1.74 | 1.501 | +0.148 | DROP | DROP ✓ |
| fifth a13 | 0.416 | 3.55 | 1.713 | +0.729 | DROP | DROP ✓ |
| π a6 | 0.499 | 4.18 | 1.997 | +0.739 | DROP | DROP ✓ |

**Crossover f\*≈0.287** — *exactly* where the fifth's depth-12 straddled (why G's strict-monotonicity tripped there:
it sat ON the crossover). **Below f\* dim rises, above f\* dim retreats.** Monotonicity is now a **derived** property of
where each a=1 step's fraction sits vs 0.287 — not a substrate mystery. This is the reframe Arm 1 sought, delivered.

## φ blind measurement + unseal
φ (pure a=1, fractions 0.375–0.40 converging to 0.382): **all margins positive (+0.29…+0.64) ⇒ φ retreats
monotonically**, converged factor **g=2.50** at f=0.382 (= banked golden self-similar 2.51), consistent with the sealed
π+fifth curve there (2.64) to ~5% (max pointwise 14%, finite-size oscillation). φ **confirms the retreat-side
prediction** — but because φ is **fraction-locked at 0.382** (converges fast; q=2 blocks wider), it **cannot test the
fraction-dependence**; the π+fifth interleave is what establishes that.

## Substrate-independence — form yes, magnitude partially
g(1,f) is **substrate-independent in FORM** (one monotone curve; the crossover/direction is universal and derivable),
but carries **~30% residual per-substrate MAGNITUDE scatter**: fifth vs a π-only curve deviates −24% / −11% / **+32%**
(fifth a6/a12/a13). Same picture as a≥2 (π's g(2)=0.844 vs fifth's ~0.638). So the **parameters are partially local**
(±~30%), which can nudge the crossover slightly but does not flip any banked direction.

## Verdict — **form-universal + crossover-derivable; parameters ~30% local**
Upgrade over G's "form-universal, parameter-local": the **direction (and the monotonicity) is now COMPUTABLE** via the
crossover g(1,f)=1/(1−f), f\*≈0.287, validated 7/7 across three substrates. The residual is the ~30% magnitude scatter
in g itself (not the crossover), and φ can't sharpen it (single fraction). So: **class, reach, AND per-step direction
are readable from the CF; the thinning MAGNITUDE keeps a ~30% substrate-local component.**

## Close
Committed on `crossover-surface`; main/refsuite untouched. Carry-forward: (a) the ~30% g-magnitude substrate scatter —
is it predictable from CF neighborhood (the a_{n±1} context)? the next probe; (b) the crossover f\*≈0.287 is now a
banked, tested constant of the a=1 slice; (c) natural next substrates to map g(a,f) off the a=1 slice: **e** (patterned
CF, mixed a-values) then the **cubics** (∛2 — generic, non-periodic).
