# Task 1 resolved at the band-resolution layer — Floquet periodic/antiperiodic eigensolve

Second overnight follow-up (2026-07-02). The three prior Task-1 "hard stops" were, in order, blamed on
**resolution**, **recursion**, and **Raymond combinatorics** — all three were *pipeline* diagnoses. The actual first
bug lived at **layer zero**: the potential collapsed to the free Laplacian (fixed in MORNING2). This note closes the
*second* layer — band resolution — and it did NOT need Raymond or adaptive bracketing. Floquet theory hands us every
band edge as an eigenvalue.

## Layer-zero gate now enforced (integer invariant, no tolerance)
A Sturmian potential at approximant `p/q` has **exactly `p` impurity sites per period**. Added to `potential()`:
```python
assert int(round(V.sum()/lam)) == p    # π−3 ladder: p = 1, 15, 16, 4687
```
This catches a dead/wrong operator at t=0 in one line — the potential-layer sibling of the `p'q − pq' = 1` Farey gate
that has been quietly earning its keep in D3. (Would have caught all three prior failures instantly.)

## The method: band edges = periodic ∪ antiperiodic spectra
For a period-`q` discrete Schrödinger operator `(Hψ)_n = ψ_{n+1}+ψ_{n-1}+V_n ψ_n`, the spectrum is
`{E : |Δ(E)|≤2}`, `Δ(E)=tr T_q(E)`. The band **edges** (`Δ=±2`) are *exactly* the spectra of the period-`q` operator
under **periodic** (`Δ=+2`) and **antiperiodic** (`Δ=−2`) boundary conditions — two `q×q` symmetric
(tridiagonal-plus-corner) eigensolves. Standard Floquet theory (continuous: Magnus–Winkler / Eastham; discrete:
Teschl, *Jacobi Operators and Completely Integrable Nonlinear Lattices*, Ch. 7; confirmed by web reference check per
house rules — "all edges of the spectral bands of periodic 2nd-order operators are found from the periodic and
antiperiodic boundary value problems"). Sort the `2q` edges → `q` bands **by construction** (no grid, no gap too
narrow: exponentially thin bands arrive as adjacent eigenvalue pairs, machine precision for free).

## Certification (doubling-back discipline — validate the new instrument where the trusted one still works)
- **Golden Fibonacci vs the frozen refsuite grid** (`fibonacci_word(k)`, letters a→λ b→0):
  - k=8 (F=21): grid resolves 21/21, edge-center match **6.8e-10**, total width identical to 6 figures.
  - k=10 (F=55): grid resolves 55/55, match **1.2e-8**.
  - **k=12 (F=144): the uniform grid resolves only 98/144 — Floquet catches all 144.** Total width 3.09e-4 (Floquet)
    vs 2.42e-4 (grid, undercounted). *This is the resolution wall, defeated.*
- **π midpoint certification** (band-mid → |Δ|≤2, gap-mid → |Δ|>2, robust to edge derivative-sensitivity):
  q=7 → 7/7 & 6/6; q=106 → **106/106 & 105/105**; q=113 → 112/113 & 112/112.
  (The naive "Δ at the edge = ±2" check *fails* at q≥106 — but that is the degree-q polynomial's huge edge derivative,
  not a method error; midpoints certify cleanly.)

## Recursion — fair-trial verdict: condemned again, now for the right reason
The fast trace-map `disc_fast` (`T_k = T_{k-2}T_{k-1}^{a_k}`) was originally condemned by comparison against a
*compromised* witness (the free-Laplacian direct product). Retried against the **repaired** product AND the certified
Floquet bands: `disc_fast` scores **0/7, 0/106, 0/113** at the mechanical band midpoints, while `disc_direct` scores
7/7, 106/106, 112/113. So the recursion computes a **different operator** — its own formula is wrong (the level-1 block
`Tb·Ta^{a_1}` is period `a_1+1`, not `a_1`), independent of the witness. The retrial was worth it: we now *know* it is
the recursion, not the reference. Speed for the deep run therefore comes from the structured eigensolve, not the
recursion. Raymond-1995 demotes from blocker to an optional per-parent child-count **cross-check** on the eigensolve.

## Banked (certified): π spectral dimension, depths 1–3 (`task1_floquet_depths123.json`)
`dim = ln(q) / ln(1/mean_bandwidth)`, band-count == q exact at every cell.

| λ  | depth-1 (q=7) | depth-2 (q=106) | depth-3 (q=113) |
|----|---------------|-----------------|-----------------|
| 8  | 0.7331        | 0.6244          | 0.6276          |
| 24 | 0.5204        | 0.4839          | 0.4873          |
| 32 | 0.4833        | 0.4567          | 0.4601          |

Non-monotone (down then slightly up); the a₃=1 quotient (106→113) barely moves it, as expected. **Caveat:** this is a
single-level band-scaling estimator (scale-dependent) — read the *trajectory*, not any one value as "the dimension"
(cf. validate-scale-convergence memory). The pre-registered thinning test lives at **depth-4 (q=33102, a₄=292)**.

## Depth-4 (q=33102) — running
`depth4_q33102_floquet.py` (λ=8, dense `eigvalsh(overwrite_a=True, driver='ev')`, in-place tridiagonalization ~8.8GB
peak in 13GB, ~19 min/matrix ×2). Tests pre-registration dim(depth-4, incl. 292) < dim(depth-3). Result → `.json`.
