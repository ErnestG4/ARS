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

**4.2 The full 300-point check against the 50-digit reference, threshold 1e-9** (2026-10-10 11:05, spot;
`sparse_check_ref.py`, `results/sparse_ref/sparse_check_ref.json`): **PASS — worst 5.36e-10, 0 of 300 over 1e-9.**
Both sides use the same prime cutoff (pmax = 10⁵), so the error measured here is the evaluator's precision alone, not
the cutoff truncation (that is the separate cutoff diagnostic).

| r (spacings) | n | median error | max error |
|---|---|---|---|
| 10–100 | 90 | 4.1e-13 | 6.0e-12 |
| 100–1,000 | 90 | 6.0e-13 | 5.2e-11 |
| 1,000–5,000 | 66 | 1.6e-11 | 2.9e-10 |
| 5,000–10⁴ | 24 | 4.6e-11 | 5.4e-10 |
| 10⁴–2·10⁴ | 30 | 6.9e-11 | 5.0e-10 |

- **The margin is about 1.9×, not orders of magnitude.** 24 points are above 1e-10, 7 are above 3e-10, and 3 are above 5e-10.
- **The large errors all come from one place:** the non-oscillating part, at node d = (0.3, 0.8), for r > 7,000. They are slightly worse at L = 21.75 (5.4e-10) than at L = 16.5 (4.1e-10).
- **The oscillating part is within 6e-12 everywhere.**
- **The source of the remaining ~5e-10 at large r has not been diagnosed.** The error grows with r, as phase error would, but the long-double phase path is verified at 5e-15. The next suspect is cancellation in the non-oscillating sum at this node.
- **Any use of the evaluator beyond r ≈ 2·10⁴ spacings needs its own check;** this one does not cover it.

| | v1 (vs slow evaluator, before fixes) | v2 (vs 50-digit reference, after fixes) |
|---|---|---|
| worst | 1.27e-9 | 5.36e-10 |
| points over 1e-9 | 4 / 300 | 0 / 300 |
| verdict | FAIL | PASS |
