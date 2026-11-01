# GEO1 bridge-kit A2: the averaging rate of the Peter residual, derived from the coefficient decay

Brief: Will, 2026-10-31 (the ARS ↔ PLL-fabric bridge kit, Part A2). This document comes first; the code that evaluates
it (`geo1_peter_spec.py`) follows it, and no comparison with data is made until both are committed. The A1 rates
(`results/peter/rate/`, descriptive) were seen before this was written. The test this derivation sets up is the fresh
range above 3·10⁶, which has not been computed.

## 0. What is a theorem, what is assumed, what is approximated

| Step | Status |
|---|---|
| α's correlations γ(r) + 1 = Π_p F_p(r) | **Theorem** (Peter 2002; the theorem block was read verbatim; every local factor checked against SL(2, ℤ/q) counts) |
| α's spectral measure is the Fourier transform of that product, so it sits on rationals with product weights | **Follows** from the theorem: γ is α's autocorrelation (Wiener–Khinchin for mean-square almost-periodic sequences) |
| The window-average variance equals ∫ K_L dμ | **Standard** (Fejér kernel; the variance is taken as a mean over window positions) |
| The product y_r(n) = α̃(n) α̃(n + r) has product-form local weights (4-point local densities) | **Assumed:** the same local-density structure one order higher. Peter proves only the 2-point case. The planted generator satisfies it by construction |
| Within one prime-power denominator, every frequency carries the same weight ("flat") | **Approximation.** Checked on the planted witness, whose exact spectrum is known |

## 1. The spectrum from Peter's Euler product

**The local factors.** For an odd prime p (b = 1), the local factor of α is the trace density
δ_p(n) = (p² + p·χ_p(n² − 4))/(p² − 1). It is periodic mod p and has mean 1; checked in `tables-check`. Higher prime
powers p^b enter through Peter's A_r(p^b) terms.

**The spectral measure of α.** Since γ(r) + 1 = Π_p F_p(r), each F_p is periodic in r mod p^B. Taking the discrete
Fourier transform:

  μ_α(a/q) = Π_{p^k ∥ q} μ̂_p(a_p/p^k),  μ̂_p(θ) = (1/p^B) Σ_{r mod p^B} F_p(r) e(−rθ),

where a/q ↔ (a_p/p^k) is the CRT decomposition, and μ̂_p(0) = 1 for every p.

**Size of the weights (b = 1).**
- Write S_r(p) = Σ_n χ(n² − 4) χ((n + r)² − 4), the autocorrelation of χ(f).
- At a ≠ 0, μ̂_p(a/p) = p²·|χ(f)^(a)|² / (p² − 1)², where χ(f)^(a) = (1/p) Σ_n χ(n² − 4) e(−an/p). (The DFT over r of
  S_r is p²|χ(f)^(a)|². The same weight is |δ̂_p(a)|², the squared Fourier coefficient of δ_p itself, so the 2-point
  theorem and the local-factor picture agree.)
- By Parseval, Σ_{a≠0} |χ(f)^(a)|² = Var χ(f) ≈ 1, so the mass at denominator p is
  M_p = Σ_{a≠0} μ̂_p(a/p) ≈ p²/(p² − 1)² ≈ p⁻².
- That is about p⁻³ per frequency.
- By Weil's bound (|Σ_n χ(n² − 4) e(an/p)| ≤ 2√p, so |χ(f)^(a)|² ≤ 4/p), no single frequency carries more than about
  4p⁻³.
- **For b = 1 primes the flat weight needs only the mass**, and Parseval gives it in O(p) without a DFT:
  mass = mean(g²)/mean(g)² − 1. DFTs are needed only for the prime powers p ≤ 13.

This is the "coefficient decay": for squarefree q, the weight is about q⁻³ per frequency, i.e. Fourier coefficients of
size about q^(−3/2).

**The product y_r.** Under the local-density assumption, y_r's spectral measure is
(1 + γ(r))² Π_{p^k∥q} ν_p(a_p/p^k), with ν_p = |ĝ_p|²/m_p², where g_p(n) = δ_p(n) δ_p(n + r) and m_p = mean g_p = F_p(r).
- Since g_p ≈ 1 + ε_p(n) + ε_p(n + r), its mass is ν_p ≈ |ε̂_p(a)|²·|1 + e(ar/p)|².
- Averaged over a, that is twice α's mass when p ∤ r, and four times when p | r.

## 2. From the spectrum to the rate

For a window of length L, averaged over its position, the residual's mean square is

  E²(L) = Σ_{θ ≠ 0} μ(θ) K_L(θ),  K_L(θ) = |(1/L) Σ_{n<L} e(nθ)|².

**Exact kernel sums.** Write T(q, L) = Σ_{(a,q)=1} K_L(a/q).
- By Möbius over divisors, T(q, L) = Σ_{e|q} μ(q/e) F(e, L).
- F(e, L) = Σ_{a mod e} K_L(a/e) = (e/L²)·(s(m + 1)² + (e − s)m²), where L = me + s.

**Flat weights.** With w(p^k) = (mass at exact denominator p^k)/φ(p^k) and W(q) = Π_{p^k∥q} w(p^k):

  E²(L) ≈ c₀ Σ_{q ≥ 2} W(q) T(q, L),

with c₀ = 1 for α and (1 + γ(r))² for y_r.

**Asymptotics.** These show where the rate comes from; the prediction itself uses the exact partial sums.
- For q ≤ L, T(q, L) ≈ (q²/(6L²)) Π_{p|q}(1 − p⁻²), so each squarefree q contributes about
  (1/(6L²)) Π_{p|q} c_p (1 − p⁻²)/p, with c_p = p³·w(p).
- For q > L, the frequencies spread uniformly at scale 1/L. They contribute about (1/L) Σ_{q>L} W(q) φ(q), which is
  also O(L⁻²·(log)^(c−1)).
- Hence E²(L) ≍ L⁻² Σ_{q≤L} μ²(q) Π_{p|q} c_p/p, which goes as (ln L)^c / L².
  - **α (c_p ≈ 1):** E_α ∝ (ln L)^(1/2) / L.
  - **y_r (c_p ≈ 2):** E_y ∝ ln L / L.

**The analogue of E8a's threshold.** A coefficient decay of |ŷ| ~ q^(−κ) per frequency gives E ~ L^(−min(1, κ − ½)) up
to logs. The arithmetic case, κ = 3/2, sits exactly at the boundary where the rate saturates at 1/L. That is why a log
correction appears, as at E8a's s = d/2. It is far from the CLT's L^(−½), and that gap is what the block jackknife gets
wrong.

**Finite L.** The (ln L)^c form converges slowly (the Euler products Π(1 + c_p/p)(1 − 1/p)^c). So the prediction is
the exact sum, evaluated numerically, and not the leading power of the log.

## 3. The computable prediction (zero free parameters)

`geo1_peter_spec.py` evaluates E²(L) from §2:
- w(p^k) comes from exact DFTs of the local factors for p ≤ 13, using prime powers up to the BPOW exponents, and from
  Parseval masses for 13 < p ≤ 10⁵;
- above 10⁵, from the leading term 2·Var(δ_p)/(p − 1) for y (p ∤ r), and Var(δ_p)/(p − 1) for α;
- q runs to Q = 2·10⁷; the tail is (1/L)·(M_total − Σ_{q≤Q} W(q) φ(q)).

**Outputs:** the predicted E_rms(L) for the α mean and for each lag's γ̂(r), on the A1 L grids, and their log-log
slopes.

**Checks before any comparison with data:**
1. **The flat approximation, on the planted witness.** The same code is given the planted generator's spectrum (p ≤ 997,
   exact tables) and must reproduce the planted series' measured E_rms(L). The criterion is fixed now: within 25% at
   every L in [10³, 10⁵], and the slope within 0.05.
2. **Mass bookkeeping.** M_total from the product must equal the series' variance (for α: γ(0); for y: its exact second
   moment under the model) to 1%.

Only if both hold is the real-data prediction reported, and then compared with A1's measured rates as a descriptive
check on the already-read ranges.

## 4. A seal (if cheap): price first

- **Fresh traces 3·10⁶ < t ≤ T₃.** PARI costs about 12–14 ms per t at d ~ 10¹³–10¹⁴ (2.18 discriminants per t; the GEO1
  launch-2 measurement):
  - T₃ = 6·10⁶: about 11 core-hours;
  - T₃ = 10⁷: about 27 core-hours.
- **Candidate sealed statistic** (to be fixed only after the §3 checks): per lag, E_rms(L) on disjoint windows tiling the
  fresh range at L = 10³, 10⁴, 10⁵, as a ratio to the §3 prediction. Also the log-log slope over [10³, 10⁵] against the
  predicted slope.
- **Witnesses:**
  - i.i.d. α must fail;
  - the planted product must pass;
  - a "CLT rate" alternative, the prediction scaled by L^(+½), must fail.
- Tolerances from the planted witness's scatter and the §3 check's measured flat-approximation error, with D23 ≥ 0.95.

## 5. Rebuild (Will, 2026-10-31: approved once), fixed before any rebuild code is written

**What failed.** Check 1 failed (`results/peter/rate/SPEC_PLANTED.json`): α and lag 1 passed, lags 0, 2 and 4 failed.
The flat weights within each prime-power denominator are the suspect.

**Cutoff: Q_ex = 10⁴.**
- **Frequencies a/q with q ≤ 10⁴ are summed one by one,** with exact weights. Each weight is the product of the exact
  DFT weights of its CRT components: tables mod p^B for p ≤ 13, and the DFT of g_p (or δ_p) mod p for 13 < p ≤ 10⁴.
  The kernel is K_L(a/q) = sin²(πLa/q)/(L² sin²(πa/q)), exactly.
- **Frequencies with q > 10⁴ keep the flat weights** of §3, and the q > Q tail is as before.

**Justification.**
1. *Where the error came from.* The per-q contribution to E²(L) for q ≤ L is about (1/(6L²)) Π_{p|q} c_p/p. So the
   small denominators carry the most weight per q, and the failed lags are those where the small primes' weights are
   most uneven near θ = 0.
2. *What the cutoff covers.* With exact weights to 10⁴, the flat part of the near sum is the q range (10⁴, L]. As a
   fraction of the near sum, that is about ln(L/10⁴)/ln L: 0 at L = 10⁴, and 0.2 at L = 10⁵, the top of the checked
   range.
3. *Why flat is reasonable beyond the cutoff.*
   - For q > 10⁴ the frequency near 0 is a CRT mixture of many components.
   - For b = 1 primes the per-frequency weights scatter about their mean, with Weil-bounded size.
   - So replacing them by the mean is unbiased in expectation, and the error averages down over the many q involved.
4. *Cost.* About 3·10⁷ frequencies per curve, cheap.

**The cutoff is not tuned.** It was chosen before any rebuilt code ran on a witness. The only tests before the rerun are
unit tests on small exactly periodic products: δ₅·δ₇ and δ₃·δ₁₁·δ₁₃, where E_rms over all window positions is exact.
The spectral sum must reproduce them to 10⁻¹⁰.

**Second planted witness** (new construction and new seed, not run during the rebuild): the local-density product
truncated at p ≤ 499 (same BPOW for p ≤ 13), with shifts from seed 20261110. Same statistics (α̃ and lags 0, 1, 2, 4),
same fresh-range tiling. Its prediction uses its own spectrum (p ≤ 499).

**The rerun criterion is unchanged** (within 25% at every L in [10³, 10⁵], slope within 0.05, mass within 1%) and must
hold on both witnesses at every statistic. If either fails, A2 remains a derivation with no reported prediction, and
there is no further rebuild.
