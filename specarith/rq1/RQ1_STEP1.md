# RQ1 Step 1: generator, estimator, gates (round 85; criteria declared in `rq1_gates.py` before running, e179155a)

## Generator (`rq1_angles.py`)
**Method.**
- **Primes:** split p ≡ ±1 mod 8; √2 mod p by Tonelli–Shanks.
- **Generator π:** π = gcd(p, s + √2) in ℤ[√2] by the norm-Euclidean algorithm, in exact Python integers.
- **Reduction:** by ±ε^n into 1 ≤ |π/π′| < ε², with a > 0. Of {π, π′ε} the one with θ ≤ ½ is kept, and the other
  ideal sits at 1 − θ.
- **Exclusions:** 2 and the inert primes.
- **Assertion:** N(π) = ±p, asserted for every prime both before and after reduction.

**Checks (local).**
- All 1,121 split primes below 2·10⁴ are covered, and each appears once.
- θ matches brute-force enumeration of a² − 2b² = ±p, taken mod 1, on 300 primes, with 0 mismatches.
- Spot and local give the same output at X = 10⁶ (39,221 primes).
- The int32 storage holds: at X = 10¹¹ the largest |a| is 3.5·10⁵.

**Estimator.**
- It is RW's eq. 1.2: the window-centre-averaged variance of N_{K}(θ), with window 1/K on θ ∈ [0, 1).
- It is computed exactly: N(c) is piecewise constant with breakpoints θ_i ± 1/(2K), so it is summed over the 2N
  breakpoints, with no grid.

## Gates (`results/GATES.json`; local, 183 s)

| gate | criterion (declared) | result |
|---|---|---|
| G0 estimator exactness | vs the brute pair formula to 10⁻⁹ | max relative 8.7·10⁻¹³: **PASS** |
| G1 uniform i.i.d. | mean = (N/K)(1 − 1/K) within 3 SE, K = 4, 16, 64, 256 | z = +1.54, −2.19, −0.56, +0.65: **PASS** |
| G2 CUE_100 | mean = exact arc variance Σ_m sin²(πmw)/(πm)²·min(\|m\|, N) within 3 SE, K = 2, 5, 10, 25, 50 | z = −0.98, −0.40, −0.84, −1.81, −1.88: **PASS** |
| G3 ℤ[i] vs RW Figure 1 | \|Δ\| ≤ 0.03 at all β ≥ 0.5; median \|Δ\| ≤ 0.05 for β < 0.5 | max 0.264; median 0.173: **FAIL** |
| W witnesses | the inert spike and the conjugate double count must be flagged; the clean archive must pass | inert: "spike at θ = 0: 226 rows"; conjugates: "repeated p: 332,213"; clean: no issues: **PASS** |

**G2 note.** All five z are negative. They come from the same 4,000 matrices, so they are correlated. All are within
the declared 3 SE.

## G3 FAIL: what it is
**Ours against RW Figure 1.**
- **Where the values come from.** RW's Figure 1 has no table, so its 46 plotted points were recovered exactly from
  the PDF's vector drawing commands (`tools/rw_fig1_parse.py` → `results/RW_FIG1_POINTS.json`), calibrated on the
  axis ticks.
- **Pattern.** Ours, at x = 10⁸, is below theirs at every β:

  | β | 0.30 | 0.50 | 0.66 | 0.80 | 0.98 |
  |---|---|---|---|---|---|
  | ours | 0.243 | 0.607 | 0.878 | 0.922 | 0.937 |
  | RW Figure 1 | 0.431 | 0.844 | 0.999 | 0.979 | 0.979 |

- **§9.E stability.** Ours at x = 10⁷ is lower still, by up to 0.14. The statistic is moving with x, upward toward
  the conjecture, but it is not stable between these two x values.

**Our pipeline is not the source of the gap.**
- On the same x it reproduces Phase 34d's ℤ[i] angle set exactly: identical arrays once the inert points are dropped.
- Phase 34d's grid estimator agrees with our exact one within grid noise: 0.320 / 0.319, 0.585 / 0.596 and
  0.794 / 0.835 at β = 0.3, 0.5 and 0.65, x = 10⁷.
- **It also confirms the Phase 34d thinning defect (Step 0 §1) quantitatively.** The full-sample ratio at x = 10⁷,
  β = 0.65 is 0.79–0.84, and (r + 1)/2 = 0.90–0.92 reproduces 34d's reported half-sample 0.923.

**Post-hoc: two other conventions tried.**
- One angle per split prime on [0, π/4], and one angle per split prime with odd real part.
- Neither reproduces Figure 1: max deviations 0.19 and 0.24.
- **RW's Figure 1 convention is not identified.** The paper gives "x ≈ 10⁸" and the definition (1.2), but not the
  computation behind the figure.

**Options for gate 3 (Will):**
- **(a) Replace the target with Chen et al.'s Figure 1** (arXiv:1901.07386).
  - Their computation is fully specified by the Mathematica code in their Appendix A (X = 10⁹, smoothed ψ-weighted
    statistic).
  - Its points can be recovered from the vector PDF the same way.
  - The gate would then test our pipeline (with their weights) against a published, reproducible computation.
- **(b) Ask the authors** for Figure 1's x, K rounding and estimator.
- **(c) Record G3 as unidentifiable,** and rest the pipeline on G0–G2, the witnesses and the Phase 34d
  cross-reproduction.

**Not a finding about ℤ[i].** Our ℤ[i] numbers fall well below min(1, 2β) at x ≤ 10⁸: 0.61 at β = 0.5, 0.88 at
β = 0.66. That is a finite-x statement only, unsealed and descriptive. It matters for the RQ1 seal's tolerance
(`RQ1_SEAL.md` §4).

## Cost (the cost model, `../l6/N6-2_PLAN.md` §10)
- **Step 1 gates:** local, 183 s.
- **Step 2 archive** (ℤ[√2], X = 10¹¹, 1,000 segments of 10⁸):
  - Measured locally at 9 µs per split prime near 10⁷, 20 µs near 10¹⁰ and 22 µs near 10¹¹, ×4.1 on spot at
    28 processes.
  - Predicted: ≈ 50 spot core-h (4.8 to X = 10¹⁰), ≈ 16.5 GB.
  - The first-wave rule is built into the launcher.
