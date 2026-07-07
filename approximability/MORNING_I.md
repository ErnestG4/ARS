# MORNING_I — e as magnitude probe: the ~30% was an f-artifact; a=1 magnitude is UNIVERSAL

Branch `e-magnitude-probe` off `crossover-surface`. numba fast solver the tool. main/refsuite untouched.
Artifacts: `e_W_cheap.json`, `e_W_deep.json`, `e_analyze.py`, `e_analysis.json`, `I_verdict.json`,
`I_magnitude_collapse.png`, `H_direction_law.json` (boundary check).

## Layer-zero (all passed)
1. **e CF exact** (hard integer gate): partial quotients a₁… = [1,2,1,1,4,1,1,6,1,1,8,1,1,10,…], the 1,1,2k pattern.
   (`cf_frac` returns from a₁, dropping a₀=2 — harmless: the Floquet potential is invariant to the integer part.)
2. **Reach budget stated up front, no silent truncation:** the rising even spine caps O(q²) reach at **depth ≤14
   (q≤208k, a≤10)**; depth 16 (a=12, q≈5M) parked with the a=55 cusp (same algorithm wall). Measured n=2–14.
3. **Boundary reduction CHECKED (the check skipped before a+f):** g̃(a,f)=factor/λ is ONE continuous surface —
   a=1 upper edge 0.523 (f=0.499) meets a=2 lower edge 0.521 (f=0.080), gap 0.0014. My H "g(1,f) raw factor" and
   "g(a)=factor/λ" were display conventions of the same object. a≥2 corroboration valid on this surface.

## Primary — neighborhood-MAGNITUDE memory: **REFUTED**
Post-big a=1 class (n=5,8,11,14), full pre-registered n=4: **g̃ = 0.126 / 0.125 / 0.125 / 0.125 for a_prev = 4/6/8/10**
— span 0.0008, slope −1.2e−4/unit. The neighbor's *magnitude* leaves no trace.
- **Deflated-n honesty:** these 4 points sit in the curve's flat low-f region (a_prev ⟂ f, r=−0.98), so e's post-big
  alone is a weak test (both a_prev and f are null there). **The stronger leg is π:** its a=1 steps with a_prev=**15**
  and a_prev=**292** (a huge neighbor) have residual −0.0003 and −0.0001 — zero. A neighbor quotient spanning 4→292
  across two substrates produces no magnitude residual. Neighborhood-magnitude memory is refuted, not merely absent.

## The result — a=1 magnitude is a SINGLE UNIVERSAL g̃(1,f); H's ~30% was the f-confound
Sorted by f, all 14 a=1 points (π+fifth+e) lie on **one monotone curve**, no substrate jump:
```
f: .003π .062π .105e .132e .179e .226F .287F .334π .416F .429e .451e .465e .472e .499π
g̃: .125  .125  .125  .125  .126  .133  .175  .217  .443  .500  .521  .522  .522  .523
```
e interleaves π and fifth exactly. The H "~30% per-substrate magnitude scatter" (−24/−11/+32%, g(2) 0.844/0.638)
**was the f-distribution confound** — π sampled high-f, fifth low-f, on a steep curve, so they *looked* offset.
Matched by f they coincide. **This corrects H:** the a=1 magnitude is not substrate-local — it is fraction-determined
and substrate-universal. The neighborhood enters **only** by setting which side the big quotient sits (→ f), never by
its size. (Figure `I_magnitude_collapse.png`.)

## a≥2 — corroboration + the one surviving sliver
- **Metallic saturates:** e's a=4,6,8,10 all give g̃ = 1.008–1.016 (saturated by a=4), matching π/fifth large-a ~1.0.
- **a=2 corner UNDERPOWERED/OPEN:** does the a=2 "split" (π 0.844 vs fifth 0.52–0.68) dissolve under f-matching too?
  Can't tell — π's only a=2 point (f=0.25) sits **beyond** the fifth's a=2 f-range (≤0.197); the residual-beyond-f is
  6% (local-slope) to 19% (global-linear extrapolation), extrapolation-sensitive and unresolvable. e's spine is
  saturated, so e **cannot** probe a=2. This is the sole open piece.

## Verdict — direction closed (H) + a=1 magnitude universal (I); only the a=2 corner remains
Across G→H→I the finite-depth trajectory has gone from "monotonicity is a substrate mystery" to almost fully
CF-derivable: **direction** is closed-form (H, 17/17); **a=1 magnitude** is a universal function g̃(1,f) with no
substrate or neighborhood-magnitude component (I). The residual is now a single sliver — the **a=2 magnitude corner**,
underpowered here — not a broad ~30% substrate memory. That's a much more contained boundary than H reported.

## Close / carry-forward
- **What the a=2 corner needs (next spec, not this arm):** an a=2 point at matched f (f≈0.05–0.20) on a THIRD
  substrate, to test whether π's 0.844 is on the fifth's g̃(2,f) trend or genuinely offset. e can't (no a=2); a
  substrate with a=2 steps in the fifth's f-window is required. The **cubics** (∛2 kin) — generic CF with recurring
  small quotients — are the natural source and the pre-registered next substrate.
- e's a≥12 spine (q≳5M) parked with the a=55 cusp (algorithm problem, not a session).
- H-Arm2 ⅓ and the function-field Ramanujan build stay deferred (unrelated).
