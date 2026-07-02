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

## Depth-4 (q=33102, a₄=292) — DONE. Band-count gate PASSES; pre-registration FALSIFIED.
`depth4_q33102_floquet.py` (λ=8, dense `eigvalsh(overwrite_a=True, **driver='evr'**)` — MRRR, fast + low-workspace;
in-place tridiagonalization ~8.8 GB peak in 13 GB; **26.2 min/matrix ×2 = 52.6 min wall**). *(First attempt used
`driver='ev'` (plain QR) — it saturated all 24 cores at ~1–2 hr/matrix and was killed; `evr` is the right driver for
all-eigenvalues-only at this size.)* Result → `depth4_q33102_floquet.json`, edges → `depth4_q33102_edges.npy`.

**Methodological win:** `bands == q == 33102`, `count_eq_q = True`. The Floquet eigensolve resolves band-count==q at the
depth where **every** prior approach hard-stopped. Task 1's structural gate is met at depth-4.

**π spectral-dimension trajectory, λ=8** (`dim = ln q / ln(1/mean_width)`, band-count==q exact at every depth):

| depth | q | bands | total width | mean width | dim | dim·lnλ |
|------:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | 7 | 4.924e-01 | 7.035e-02 | 0.7331 | 1.5245 |
| 2 | 106 | 106 | 6.051e-02 | 5.708e-04 | 0.6244 | 1.2984 |
| 3 | 113 | 113 | 6.051e-02 | 5.355e-04 | 0.6276 | 1.3051 |
| 4 | 33102 | 33102 | **7.435e-03** | 2.246e-07 | **0.6798** | 1.4137 |

**Pre-registration FALSIFIED (reported at equal prominence per the constitution).** The registered prediction was
*dim(depth-4, incl. a₄=292) < dim(depth-3)* — "the big partial quotient thins the spectrum ⇒ lower dimension."
**dim ROSE, 0.6276 → 0.6798.** The prediction was directionally wrong.

**Why — measure ≠ dimension (the honest resolution):** the spectrum genuinely *is* thinner at depth-4 — total
bandwidth collapsed **8.1×** (6.05e-02 → 7.44e-03) when the 292 entered. But the *dimension* is a scaling exponent
(count vs width), not a measure: band count grew 293× while mean width shrank ~2400×, and in log-ratio the count won,
so `ln q / ln(1/mean_w)` rose. The pre-registration conflated **measure-thinness** (confirmed) with **dimension-drop**
(false). This is a clean, if humbling, distinction the depth-4 data forced.

**Resolution caveat (honest):** 2035 / 33102 bands (6.1%) are narrower than eigenvalue precision (~2.2e-15), and 2015
gaps are numerically closed (`width_min = 0.0`). But bands narrower than 1e-8 carry only **0.19%** of total width
(`frac_width_in_narrow = 0.00186`), so `total_width` / `mean_width` / `dim` are robust; only individual sub-precision
band *widths* are unreliable (they don't enter the mean-width readout materially). `dim` here is a **single-level
band-scaling estimator** (scale-dependent) — the DEGT limit would need the depth→∞ trajectory; read this as one more
trajectory point, not "the dimension of σ(H_π)".

**Robustness (running):** `depth4_lambdas.py` repeats depth-4 at λ=24, 32 to check whether the dim-rise is
λ-general or a λ=8 artifact → `depth4_q33102_lam{24,32}.json`.

**Net:** Task-1's band-count==q gate is met at depth-4 (the deliverable that was blocked for three sessions); the
substantive pre-registered *direction* is falsified honestly; the corrected reading (thinner in measure, higher in
dimension estimate) is the finding.
