# Sparse direct check of the fast ζ four-point evaluator — failure, cause, fix (record)

**Check** (Will, twentieth round (1)): the fast vectorised evaluator (`cs4fast.py`) against a direct evaluation at 300
log-grid points of the connected two-pair function (heights L = 16.5, 21.75; offsets (0.5,0.5), (0.3,0.8), (1.0,0.4);
r = 10–2·10⁴ spacings). **Declared threshold: |fast − direct| ≤ 1e-9, unchanged throughout.**

## 1. The failure (2026-10-10, overnight run; `results/sparse/sparse_check.json`)
**FAIL: worst 1.27e-9, 4 of 300 points over the threshold.** All four are at r > 10⁴ spacings, at node d = (0.3, 0.8),
height L = 16.5. The error grew steadily with r: median 3e-13 at r < 100, 1e-10 beyond 5,000, maximum 1.3e-9.

## 2. Causes
1. **Phase precision in the fast evaluator.** At these separations the phases Im(s)·log n and Im(e)·log p reach ~1e5 rad.
   In double precision that loses ~5 digits before the exponential. A first fix (long-double multiply) gained nothing,
   because of two leaks found by `check_longdouble.py` (Will: verify the long-double path, don't assume it):
   - (a) log p and log n were computed in double and cast up, keeping their 1e-16 rounding (× Im s ~ 1e4 = 1e-11);
   - (b) the 2π used for the mod-2π reduction was a double π cast up (≈ 1.5·10⁴ periods × 2.4e-16 = 4e-12).
2. **The comparison side was never a reference.** The "slow" evaluator (`cs4lib.Zeta` via `cs4split`) computes ζ in
   mpmath but its prime sums and Euler products in numpy complex double, so it shares the same large-phase limit. A
   known answer must come from somewhere independent.

## 3. Fixes
- `zeta_em.py`, `cs4fast.py`: log p and log n computed with `np.log` on long-double arrays; 2π parsed at long-double
  precision; phase reduced mod 2π in long double before the exponential (`pexp`, `cpow_neg`).
- `cs4ref.py`: an independent 50-digit reference. Every prime sum and Euler product (A, B, Q, B1–B4, S13, A*) is an
  mpmath loop; ζ, ζ′/ζ and (ζ′/ζ)′ are mpmath at 50 digits.

| quantity, against mpmath | before | after |
|---|---|---|
| p^e at phases up to 9·10⁴ rad (`check_longdouble.py`, both machines; long-double ε = 1.08e-19) | 9.3e-12 | 5.4e-15 |
| ζ(1+x) (`zeta_em.py` check) | 6e-12 | 2.5e-15 |
| ζ′/ζ(1+x) | 2e-10 | 8.5e-14 |
| (ζ′/ζ)′(1+x) | 4e-10 | 8.0e-14 |

## 4. Re-validation
**4.1 Against the 50-digit reference at the 4 failing + 4 passing points** (2026-10-10 08:41; `results/ref50/`):

| d | r (spacings) | \|ρ₄c non-osc\| | slow evaluator error | fixed fast evaluator error |
|---|---|---|---|---|
| (0.3, 0.8) | 1,000 | 1.3e-2 | 9.3e-11 | 9.8e-12 |
| (0.3, 0.8) | 12,558 | 4.3e-3 | **1.60e-9** | 2.5e-10 |
| (0.3, 0.8) | 14,665 | 4.7e-4 | **1.26e-9** | 5.6e-11 |
| (0.3, 0.8) | 17,126 | 4.9e-3 | 8.7e-10 | 2.9e-10 |
| (0.3, 0.8) | 20,000 | 2.4e-3 | **1.44e-9** | 1.5e-10 |
| (0.5, 0.5) | 10 | 7.1e-3 | 3.0e-13 | 4.9e-13 |
| (0.5, 0.5) | 300 | 7.8e-2 | 3.3e-12 | 8.6e-13 |
| (1.0, 0.4) | 5,000 | 2.3e-2 | 2.2e-11 | 1.8e-11 |

- **Most of the original 1.3e-9 was on the comparison side.** The slow evaluator's double-precision prime sums are off
  by up to 1.6e-9 at r > 10⁴.
- **The fixed fast evaluator is within 2.9e-10 at every point**, including the four that failed.
- The full rerun must therefore compare against the 50-digit reference, not the slow evaluator.

**4.2 The full 300-point check against the 50-digit reference, threshold 1e-9:** running (pending).
