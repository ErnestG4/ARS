# Session K — Continuation Findings (Runs 1–3)

Executed 2026-07-08 under the sealed combined pre-registration. Standing gates carried
over (unfolding-free ⟨r̃⟩ primary; Σ² theory-fixed corroborating; completeness/
desymmetrization; blind-then-single-unseal; moonshine dark). Raw: `mayer_run1_measured.json`,
`run2_measured.json`, `run3_measured.json`.

## Run 1 — n=3 Mayer cross-check (KEYSTONE) — **PASS**

Extended the validated 2a GKW discretization to the s-parametrized Mayer–Ruelle
operator `L_s` on the critical line `s = 1/2 + i r`; located eigenvalue-±1 crossings
(zeros of `det(1∓L_s)`), scanning r∈[9,40], N=48 collocation nodes, conditionally-
convergent tail accelerated with complex Hurwitz ζ (mpmath).

- s=1 reduction sanity: λ₀=1, λ₁=−0.303663 (matches 2a/GKW).
- **even (λ=+1): 27 zeros found, max err 0.0075, median 0.0014** vs LMFDB sym0 r_n.
- **odd  (λ=−1): 43 zeros found, max err 0.0017, median 0.0013** vs LMFDB sym1 r_n.
- Both exceed the pre-registered N≥10 per sector; every found zero matches an LMFDB r_n
  to <0.008 (mostly <0.002).

**Quadruple duty discharged:** (a) CP1 mechanism receipt — the Maass spectrum *is* the
Selberg-zeta/transfer-operator zero set; (b) co-primary weld — the same `L_s` family that
produced the Lévy/θ_∞ bridge (CP2) produces the Maass spectrum; (c) **pipeline calibration**
certifying the determinant route for Run 3; (d) **parity convention settled** —
eigenvalue +1 = even = LMFDB **sym0**; eigenvalue −1 = odd = LMFDB **sym1**.

> **Label correction to CP1 (banked commit 5369d91).** CP1 had assumed sym1=even; Run 1
> proves **sym0=even, sym1=odd** (also consistent with the Weyl count — the even sector
> carries the scattering term that *subtracts*, so even is the *fewer* sector, 266 not 334).
> The ⟨r̃⟩ GOE-exclusion is label-independent and unchanged. What swaps: the finite-r
> crossover is in the **odd** sector; the **even** sector is clean Poisson. The Σ² unfold's
> scattering coefficient now sits on the even sector (Σ² is corroborating only).

Corrected CP1 per-sector ⟨r̃⟩ (600-form block, r<100):
- **even (sym0, n=266): ⟨r̃⟩ = 0.399 ± 0.016 → clean Poisson (+0.8σ), GOE excluded 8.4σ**
- **odd  (sym1, n=334): ⟨r̃⟩ = 0.427 ± 0.016 → Poisson + mild finite-r repulsion (+2.6σ), GOE excluded 7.0σ**

## Run 2 — sliding-window ⟨r̃⟩ sweep — both banked-object questions resolved

Sliding-window unfolding-free ⟨r̃⟩ across the complete block (r<100), on the odd (sym1)
sector (the elevated 0.427 aggregate; the plan's "even" under the old mislabel).

- **(i) r\* stability:** the crossover is **real and window-stable at r\*≈45±5** (first
  return-to-Poisson center = 38.4 / 48.8 / 45.2 for window widths 40/60/80). Not a
  window-choice artifact. Low-r windows sit near GOE (⟨r̃⟩=0.530 at r~35, 0.510 at r~42,
  0.476 at r~47, all >Poisson+2σ), then drop.
- **(ii) residual:** the elevated aggregate **collapses toward the 0.386 Poisson surmise
  above r\*** (0.35–0.40 for r∈[50,65]). So the +2.6σ is **finite-r GOE contamination at
  low eigenvalues, not persistent even/odd-sector structure — interpretation closed.**

Both sectors are asymptotically arithmetic-Poisson; the odd sector approaches it more
slowly, with a GOE→Poisson crossover at r\*≈45.

## Run 3 — n=5 vs n=3 periodic-orbit length-degeneracy — **PASS (partial, as pre-registered)**

Named-before-building signature: arithmeticity is carried by *length-multiplicity growth*
of transfer-operator periodic orbits, NOT by any leading-eigenvalue/Lyapunov/θ_∞ difference.
Enumerated primitive cyclic words (necklaces) over the CF alphabet; length ↔ trace of the
product of CF matrices. Only difference between the two systems is the entry ring:
- **n=3 (modular, arithmetic):** `M_a=[[a,−1],[1,0]]`, trace ∈ **ℤ** (rank-1).
- **n=5 (Hecke G₅, non-arithmetic, ℚ(√5)):** `M_a=[[aφ,−1],[1,0]]`, φ=2cos(π/5), trace ∈ **ℤ[φ]** (rank-2), exact.

Metric = mean length-multiplicity (#necklaces / #distinct traces), and its log-growth rate.

| system | k=15 #necklaces | #distinct traces | mean mult | max mult | log-growth rate |
|---|---|---|---|---|---|
| **n=3** | 2182 | **36** | **60.6** | 586 | **0.388** |
| **n=5** | 2182 | 643 | 3.39 | 54 | 0.130 |

- **n=3 shows exponential length-degeneracy** — 2182 orbits compress to just 36 distinct
  integer traces (the Bogomolny–Georgeot–Schmit / Bolte–Steil–Steiner mechanism behind
  CP1's Poisson statistics).
- **n=5 is strongly suppressed** — 18× more distinct traces, log-growth rate 3.0× smaller.
- Verdict: **PASS** (s₃/s₅ = 2.99 > 2.5). The exponential-vs-generic split appears from the
  operator side, independent of any trivial number difference.

**Caveat (honest scope):** uses the simplified {1,2} (and {1,2,3}) alphabet, not the exact
Hurwitz–Nakada admissibility for G₅, so this isolates arithmeticity at the **trace-ring**
level (ℤ vs ℤ[φ]); n=5 retains a residual sub-exponential degeneracy (mean mult →3.4,
one 54-fold *exact* ℤ[φ] coincidence). The full geodesic-length-spectrum contrast with
exact admissibility, and the acquisition of Hecke n=5 *Maass levels* for the direct GOE
nearest-neighbor contrast, remain the queued deliberate-arc items (per plan "Not tonight").

## Net

Both co-primaries now welded on one transfer-operator substrate and cross-validated:
CP2 (Lévy/θ_∞ bridge) and CP1 (Maass spectrum) are two readings of the same `L_s`. The
arithmetic anomaly (Poisson, GOE excluded) is confirmed per sector *and* mechanistically
explained (exponential length-degeneracy), with a non-arithmetic (n=5) operator-side
contrast establishing that the degeneracy — not any surface-level constant — is the
arithmeticity signature.
