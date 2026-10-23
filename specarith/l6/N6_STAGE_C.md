# n = 6, stage (c): results as they come (method: `N6_STAGE_C_BOUND.md`)

## Steps 1–2: the n = 6 construction and its U(N) pointwise gate (`cs4/ratios_t6.py`; spot)
- The construction is `ratios_t5.Model` at n = 6. It is general in n, so no new transcription was needed.
- **Gate result: FAIL** (`cs4/results/n6c/UGATE6.json`), with tolerance 10⁻¹² + 10⁻⁶·|det|, pointwise:

  | N | configurations (8 each) | max relative difference | max absolute difference | result |
  |---|---|---|---|---|
  | 10 | spread over [0, 6) | 1.0·10⁻⁷ | 1.4·10⁻¹² | pass |
  | 10 | one pair 10⁻³ apart | 9.6 | 6.5·10⁻¹⁰ | **fail** |
  | 50 | spread over [0, 6) | 3.3·10⁻⁷ | 2.5·10⁻¹² | pass |
  | 50 | one pair 10⁻³ apart | 1.7·10⁹ | 3.4·10⁻⁸ | **fail** |
  | 50 | 3 + 3 at r = 5 | 1.9·10⁻⁷ | 3.1·10⁻¹² | pass |
  | 50 | 3 + 3 at r = 9 | 2.1·10⁻⁸ | 2.0·10⁻¹⁴ | pass |

- **The failure is near coincidence.** With a pair 10⁻³ apart, ρ₆ falls to 10⁻⁶–10⁻¹⁸, which is ∝ d², and the
  construction carries an absolute error of up to 3·10⁻⁸ there. That comes from cancellation between z-factors
  1/(1 − e^{−x}) at x ~ 10⁻³. Away from coincidence, the relative accuracy is 2·10⁻⁸–3·10⁻⁷.
- **By the committed rule, no ζ value is read** (no bound, no G-b3) until Will rules.
- **Relevance (for that ruling, not a ruling):** the quadratures that would use the construction never come near
  coincidence. Distinct Gauss–Legendre nodes, 6 per 4-unit window, are at least 0.54 apart, and the clusters are
  ≥ 20 apart in G-b1 and G-b3. An amended gate would test near-coincidence at the quadrature's minimum separation, or
  evaluate near-coincident configurations in mpmath. **That is Will's call.**

## Large-N diagnostic (not a gate; `cs4/results/n6c/LARGEN.json`)
The construction against the determinant in the 3 + 3 geometry (4 configurations each), max relative difference:

| N | r = 20 | r = 100 | r = 1000 |
|---|---|---|---|
| 10³ | 8.8·10⁻¹¹ | 7.4·10⁻¹⁴ | (r > N/2) |
| 10⁴ | 7.9·10⁻⁸ | 1.6·10⁻¹⁰ | 2.3·10⁻³ (a configuration with det 2.8·10⁻⁸) |
| 10⁵ | 1.8·10⁻¹¹ | 2.3·10⁻¹² | 7.1·10⁻¹² |

**At N = 10⁵ the construction is accurate to about 10⁻¹¹ out to r = 1000,** so G-b1 can use stage (a)'s N directly.

## Round 76: post-hoc construction change (committed before the re-run)
**What changed.** This is a construction fix, not a gate amendment (round 76).
- **Threshold, declared now:** DELTA_TH = 0.1 unit spacings. A configuration whose smallest pairwise separation is
  below it is evaluated in mpmath (`cs4/ratios_hp.py`, mp.dps = 40). That is the same construction term for term:
  the same (S, T) enumeration, phase-filter option, θ grids and prime groups.
- At or above the threshold it is evaluated in double by `ratios_t5.Model`, unchanged. `ratios_t6.rho_auto`
  dispatches between the two.
- **Guard:** `ratios_t6.guard` raises if any configuration below DELTA_TH reaches a double evaluation.
- **This is a post-hoc construction change,** made after the committed gate failed on near-coincident pairs
  (f73f3895). The gate itself is unchanged.

**Checks, declared before running.**
1. **Path agreement at the threshold** (`ratios_t6.py threshold`): U(N) at N = 10 and 50, 4 configurations each, with
   smallest separation exactly 0.1. The two paths must agree to 10⁻¹² + 10⁻⁷·|hp|, ten times tighter than the gate.
2. **The committed U(N) pointwise gate, re-run unchanged:** the same seed, the same 48 configurations including the
   16 with a pair 10⁻³ apart, and the same tolerance 10⁻¹² + 10⁻⁶·|det|. It is evaluated through rho_auto, which
   sends 29 of the configurations below 0.1 to the mpmath path. **It must pass.**

**Local smoke tests (not gates).**
- **U(N) N = 10, n = 6:** the mpmath path gives 0.65762858171708360, against det 0.6576285817170834 and double
  0.6576285817170845. It takes 50 s per configuration.
- **ζ at PMAX 30:** mpmath and double agree to 1–3·10⁻¹⁶ at n = 2, 3 and 4, at separations ≥ 0.5.

**Why the ζ path does not block (c) or G-b3.** No ζ evaluation in (c) or G-b3 falls below the threshold. Their
in-window Gauss–Legendre nodes are ≥ 0.54 apart, and the guard would raise if one did. The ζ mpmath path exists, and
its threshold agreement can be run on request.

**Results after the construction change (spot):**
- **Path agreement at the threshold: PASS** (`cs4/results/n6c/THRESHOLD.json`). Double against mpmath at a smallest
  separation of exactly 0.1: max absolute difference 7.3·10⁻¹⁵ (N = 10) and 5.0·10⁻¹⁵ (N = 50); relative ≤ 3.6·10⁻⁹.
- **The committed U(N) gate, re-run unchanged: PASS** (`cs4/results/n6c/UGATE6.json`; the failed first run is in
  `run1/`). 29 of the 48 configurations went through the mpmath path.

  | configurations | high-precision | max relative difference |
  |---|---|---|
  | N = 10, spread | 6 of 8 | 5.1·10⁻¹¹ |
  | N = 10, near-coincident | 8 of 8 | 1.5·10⁻⁸ |
  | N = 50, spread | 2 of 8 | 7.2·10⁻⁹ |
  | N = 50, near-coincident | 8 of 8 | 1.1·10⁻⁵ (absolute 5.7·10⁻¹⁷, at det down to 4·10⁻¹⁸) |
  | N = 50, 3 + 3 at r = 5 | 2 of 8 | 1.0·10⁻¹² |
  | N = 50, 3 + 3 at r = 9 | 3 of 8 | 2.8·10⁻¹² |

- **Per round 76, (c)'s bound and G-b3 may now proceed.** G-b3 is launched. (c) waits on Will's choice of node count,
  because the committed 4-node bound is expected to come back "not established" (cost update, round 76).

## Round 77: the bound, amended to 6 nodes plus an 8-node check (committed before running)
**Why it was amended.** The per-piece quadrature check (round 76) showed the committed 4-node bound underestimates the
(3, 3) piece by ~70%. Will approved 6 nodes plus an 8-node convergence check, about 130 core-h. The design below fixes
that budget, using the per-configuration costs measured in G-b3 (≈ 90 s at PMAX 10³ under load).

**The quantity.**
- The (3, 3) piece I₃₃(r) = ∫_{A³×B³}[ρ₆ − ρ₃ρ₃] is the only place ρ₆ enters C(r).
- It is computed **by phase class** k = −3…3, for ζ and for U(N) (N = 10⁵) at identical nodes:
  `n6b_extract.FilteredModel.rho_cls`. The classes sum to the full function within 8·10⁻¹⁶, and class 0 equals the
  filtered part exactly (local check).
- Arithmetic correction per class: Δg_k = g_k^ζ − g_k^U.
- **The envelope E(r) = Σ_k |Δg_k(r)|** bounds |ΔI₃₃| at every carrier phase, so the bound does not depend on where
  the sparse r grid falls relative to the carrier. That is the beat lesson applied: no class is assumed slow or
  dropped.

**Grid.**
- r ∈ {0.27, 1.17, 2.07, 3.46, 4, 6, 10, 20}. The small r are chosen so that the two windows' 6-node grids stay
  ≥ 0.22 apart, keeping the double path valid under the guard.
- r = 0 itself needs the mpmath path (the grids coincide) and is not evaluated. Its weight is one 1/8-grid point of
  160, covered by the max-envelope bound.

**Runs.**
- ζ at ℓ = 15.75: PMAX 10² and 3·10², all 8 r.
- ζ at ℓ = 21.75: PMAX 10², all 8 r.
- ζ at ℓ = 15.75: PMAX 10³ at r = 2.07 and 10 (the cutoff trend).
- U(N): all 8 r.
- **8-node check:** ζ (ℓ = 15.75, PMAX 10²) and U(N), at r = 6.

That is 1,242 tasks of 16 configurations each, about 115 core-h, checkpointed per task.

**The bound and its reading.**
- **B₆ = 2·max(1, E₈/E₆)·40·max_r E(r)** in κ₃ units:
  - 40 ≈ Δ·(1 + 2·159), the Bartlett sum over r < 20 at weight ≤ 1;
  - 2 is the safety factor;
  - E₈/E₆ is the 8-node over the 6-node envelope at r = 6.
- **Established** iff 0.5 ≤ E₈/E₆ ≤ 2 and the cutoff change |E(10³) − E(3·10²)| ≤ 30%·E(3·10²) at both trend r.
  Otherwise the bound is "not established".
- **Negligible** iff established and B₆ ≤ 0.01·R(G)·W_CUE at every G. That is a third of the ~3% test resolution on R,
  with R = 0.315, 0.209, 0.183, 0.157 and W_CUE = 0.2111. The strictest threshold is 3.3·10⁻⁴ at G = 10⁴.
- If negligible, the term is carried as a bounded systematic, ±B₆. Otherwise it goes to Will.

Code: `cs4/n6c_bound.py`. Launcher: `cs4/run_n6c_bound_spot.sh`.
