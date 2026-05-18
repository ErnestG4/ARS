# Fibonacci-Neighborhood Structure Run — OUTCOME-MAP READ (2026-05-19)

**Status:** SCOPING / instrument N-behaviour characterisation — asymmetric
label, NEVER an AM finding. Reads Will's PRE-REGISTERED outcome map; no
auto-verdict beyond it; ambiguity flagged. Data
`phase35a/fib_neighborhood_mp_results.json` (10-worker MP, bit-identical
to serial, 154 N-points / 4928 pure tasks, 15111s). brief-and-hold;
Class II blocked; no §3 adjudication; OUT = rate-extrap/sensitivity-
remeasure/any-AM-result. Exact rate setup unchanged (golden θ,
λ_sub=0.5/λ_sup=1.5, 16 φ∈[0,0.5), L=1e5; N the only variable).

## Pre-registered map → READ

- **Commensurability / tight-cluster band-edge: RULED OUT.** Tight
  cluster F_n±{1,2,3,5,8} clu_rng(sup_spread) ≤ 0.034 (≤0.008 for
  F19..F26); gap clu_rng similarly tiny. F_n is NOT a razor extremum
  (±1 tracks F_n to ~1%). Cluster variation is 10–60× SMALLER than the
  inter-rung structure it would need to rival. (Matches Will's
  ‖(F_n±1)θ‖≈0.38 note.)
- **Crossover / "neighbourhoods flat" / ladder-representative: RULED
  OUT.** Interval profiles (F_n→¼→½→¾) vary smoothly & substantially
  everywhere — ranges 0.05–0.33 (≫ the 0.003–0.034 cluster noise
  floor). The Fibonacci ladder is NOT representative; it samples one
  phase of an N-modulation.
- **Smooth-interval / log-periodic-class: SUPPORTED** (the surviving
  branch). Structure lives in the inter-rung interval, smooth, not at
  razor-F_n.

## Richer than the three discrete branches (honest)

A smooth inter-rung **modulation SUPERPOSED on a genuine underlying
decay**. sup_spread@F_n bounces 0.43–0.62 across F16..F22 (modulation
dominates ⇒ the original "flat" region) then drops cleanly
F23→F24→F25→F26 = 0.367→0.176→0.072→0.043 (decay dominates ⇒ the
"steep" region). **The flat-then-steep is mechanistically explained:**
modulation masks the decay at small rungs, decay overtakes it at large
rungs; the rate run's off-ladder points (10000, 40000) sampled RANDOM
modulation phases — the direct cause of its non-uniform/unreliable
3-point fit. NOT claimed: clean single-frequency log-periodicity (11
intervals don't prove strict log-N periodicity; decay is superposed;
per-interval shapes differ). IS established: not-crossover,
not-commensurability, structure-in-interval-not-cluster,
ladder-NON-representative.

## Sub-question — does the gap carry its own F_n structure?

**It carries the same INTERVAL structure, not cluster structure.** gap
tight-cluster flat (≤0.024; ≤0.005 for F20+) but gap interval profiles
swing 0.05–0.36 (e.g. F25: 0.205→0.317→0.470→0.407). BOTH numerator
(sup_spread) and denominator (gap) are inter-rung-modulated.

## Consequences (Will's pre-registered, for the surviving branch)

- A Fibonacci-ladder-based rate extrapolation is **NOT sound as-is** —
  the ladder samples one phase of an N-modulation present in BOTH
  sup_spread and gap. The earlier RATE_NOT_CLEANLY_PINNED is now
  root-caused: not just non-uniform decay, but a ladder/off-ladder
  sampling of an inter-rung modulation superposed on a real decay.
- Pinning the rate requires **resolving the modulation
  dense-in-log-N** (not merely larger N) AND modelling it in BOTH
  numerator and denominator. Whether to pursue that = Will's "does
  anything downstream need non-circular sensitivity?" call — NOT
  auto-run.

Banked Step-1 verdicts & §3-(A) `S3A_REDUCED` unaffected (this is
instrument N-behaviour, upstream of any rate work). The exploration
answered exactly what it was designed to: the ladder is not
representative, and the path to a real rate is dense-in-log-N
modulation-resolution, not bigger N.
