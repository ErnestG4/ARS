# Phase 2 — amendments proposed by the pre-read (for Will; none adopted until approved)

Found while writing the code, before any Phase-2 zero is read. Each item: what the approved text says, what fails,
proposal, evidence (reproducible from `preread.py` / scratch scripts named).

## PA1 — the PRIMARY likelihood needs a fit window (s ≤ 2.0, conditional likelihood)

**Text (§4):** κ̂ = maximum-likelihood κ in the family p₀ + p₁N_k⁻². No s-range given (implicitly all spacings).

**What fails.** The first-order family is not a density on the whole half-line at the sealed heights: p₁/p₀ grows like
−s⁴ in the tail, so p₀ + c·p₁/N² turns negative at

| N_eff | 2.0 | 2.5 | 3 | 4 | 5 | 8 | 11 |
|---|---|---|---|---|---|---|---|
| s where p₀ + p₁/N² = 0 (c = 1) | 2.19 | 2.33 | 2.47 | 2.73 | 2.98 | 3.61 | 4.15 |

With every spacing in the likelihood, the MLE is pinned at the positivity boundary set by the **largest observed
spacing** — not by the shape of p(s). Haar CUE_N draws (10⁶ spacings) gave κ̂ = 1.40 (N = 3), 1.39 (N = 5), 0.99
(N = 11) against true κ = 1, and the infinite-sample fit is undefined (no c > 0 keeps the density positive on [0, 6]).
More data makes it worse (larger s_max ⇒ tighter cap). This is a defect of the estimator as specified, not of the code.

**Proposal.** Conditional maximum likelihood on a declared window s ≤ S_C = 2.0, same for every bin and both arms:
ℓ(c) = Σ_{s_k ≤ S_C} [log(p₀(s_k) + c a_k(s_k)) − log(F₀ + c Fa_k)], a_k = r₂(s; ᾱ_k)/N_eff,k², F = ∫₀^{S_C}.
The out-of-window probability is conditioned out (it would otherwise re-import the tail). The c-range is where the
model is positive on the whole window (a model property, computed before data).

Why 2.0: it is the largest round window on which the family stays a density with room for the fit at the lowest
sealed N_eff (bin A, 2.16): positive for c ≤ 2.46 (κ ≥ 0.64); at 2.2 the cap is c ≤ 1.12 (κ ≥ 0.94 — the fit would be
pinned near truth), at 2.5 it is c ≤ 0.48. P(s > 2) ≈ 1–2%; Fisher information lost vs s ≤ 2.2 is modest
(rel. SD(κ̂) per 10⁶ spacings, i.i.d. Fisher: N = 3 0.91% vs 0.72%; N = 5 2.5% vs 2.1%).

**Evidence (window 2.0):** infinite-sample κ* against the exact CUE_N law: 0.931 (N = 3), 0.977 (N = 5), 0.991 (N = 8),
0.995 (N = 11) — the O(N⁻⁴) truncation that §6's allowance is for; Haar draws (8 × 10⁶ spacings) give 0.929, 0.984,
1.002, 1.000, matching κ* within their SD (scratch `test_wf.py`; formalised in G0c/G0d).

Consequences: design SDs in §3 rise somewhat (fewer, less informative spacings); §6 allowance is computed with the
window; the SECONDARY arm uses the same window (one estimator, two families).

## PA2 — allowance combination (decision needed; pre-read reports both)
§6 adds "the shift … (i) exact CUE_N and (ii) SECONDARY" to the half-width without saying how the two combine. They are
distinct higher-order sources (CUE's own O(N⁻⁴) vs the arithmetic ᾱ − 1 term). **Proposal: |δ_i| + |δ_ii|** at the
bin's lowest-N_eff edge (conservative). Alternative: max.

G0c (results/g0c.json, window 2.0) — the two shifts have **opposite signs and nearly equal size** at every height:

| bin | N_eff (low edge) | δ_i (exact CUE_N) | δ_ii (SECONDARY) | sum | max |
|---|---|---|---|---|---|
| A | 2.16 | −0.160 | +0.129 | 0.289 | 0.160 |
| B | 2.53 | −0.103 | +0.092 | 0.195 | 0.103 |
| P1 | 2.97 | −0.070 | +0.066 | 0.136 | 0.070 |
| P2 | 3.44 | −0.050 | +0.048 | 0.099 | 0.050 |
| P3 | 3.91 | −0.038 | +0.037 | 0.075 | 0.038 |
| P4 | 4.37 | −0.030 | +0.029 | 0.059 | 0.030 |
| P5 | 4.83 | −0.024 | +0.024 | 0.048 | 0.024 |
| P6 | 5.13 | −0.021 | +0.021 | 0.043 | 0.021 |
| H1 | 5.63 | −0.018 | +0.017 | 0.035 | 0.018 |
| H2 | 10.26 | −0.005 | +0.005 | 0.010 | 0.005 |
| H3 | 10.78 | −0.005 | +0.004 | 0.009 | 0.004 |

(δ = κ* − 1 of the PRIMARY fit against that law.) Under "sum" the PRIMARY is NOT RESOLVABLE in A (0.289 > 0.20) and in B
(0.195 + any CI > 0.20) by the §4 rule; under "max", A survives (0.160 + CI) and B too. Signed addition (δ_i + δ_ii ≈ 0)
is NOT proposed: the SECONDARY family does not contain CUE's O(N⁻⁴) term, so the two are not known to superpose, and a
near-cancellation would make the primary look sharper than anything licenses. The choice decides A's and B's PRIMARY
verdicts — Will's call.

G0c also gives the cutoff justification §3 asks for: the O(N⁻⁴) remainder max|p_N − p₀ − p₁N⁻²| × N⁴ converges to 0.556
(N = 20) from 0.586 (N = 5), 0.655 (N = 3) and **1.02 at N = 2**, where it is 55% of the leading correction itself
(0.064 vs 0.115; 16% at N = 3). The primary fit's truncation shift is −16% already at N = 2.16.

## PA3 — CUE_N at non-integer N (G0c, allowance (i))
CUE_N is defined at integer N only. The allowance at a bin's real N_eff uses the BFM kernel formula
sin(πd)/(N sin(πd/N)) at real N (its analytic continuation), cross-checked for smoothness against the integer-N values
(G0c table). Proposal: adopt, disclosed.
