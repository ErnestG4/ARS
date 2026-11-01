# L13: RQ1's sealed SE model against empirical SEs on the arithmetic angle sets (descriptive; no seal)

Brief: Will, 2026-10-31. Code: `rq1_l13.py` (criteria committed before running, 35d9b579; loader and cost-guard fix
5c1aa813 after launch 1 stopped, relaunch approved by Will). Data: the already-read 10¹⁰ / 10¹¹ sets, sliced from the
pinned 10¹² archives. Every R was bit-identical to the sealed read (guard). Cost 1.71 spot core-hours (0.67× the
model). Output: `results/l13/L13.json`.

## Calibration first (synthetic Poisson; `results/l13/CALIB.json`)

Both empirical methods recover the true replicate SD:
- block arcs: 1.03 (K = 2,000) and 0.85 (K = 20,000);
- residue-class subsets: 1.04 and 0.85.

The precision is about ±9%. The sealed model is 1.22× and 0.93× the truth. So on a set whose truth is known, the methods
work.

## Result: model SE / empirical SE (90% intervals)

| X | β | field | A: block arcs | B: residue subsets | A vs B |
|---|---|---|---|---|---|
| 10¹⁰ | 0.40 | ℤ[√2] | 0.32 [0.28, 0.35] | 0.56 [0.41, 0.70] | disagree |
| 10¹⁰ | 0.40 | ℤ[i] | 0.27 [0.24, 0.30] | 1.09 [0.80, 1.38] (consistent) | disagree |
| 10¹⁰ | 0.45 | ℤ[√2] | 0.20 [0.18, 0.23] | 0.32 [0.23, 0.40] | disagree |
| 10¹⁰ | 0.45 | ℤ[i] | 0.22 [0.20, 0.24] | 0.74 [0.54, 0.94] | disagree |
| 10¹⁰ | 0.55 | ℤ[√2] | 0.056 | 0.14 [0.10, 0.17] | disagree |
| 10¹⁰ | 0.55 | ℤ[i] | 0.12 | 0.24 [0.18, 0.31] | disagree |
| 10¹⁰ | 0.60 | ℤ[√2] | 0.043 | 0.20 [0.14, 0.25] | disagree |
| 10¹⁰ | 0.60 | ℤ[i] | 0.083 | 0.27 [0.19, 0.33] | disagree |
| 10¹¹ | 0.40 | ℤ[√2] | 0.25 [0.23, 0.28] | 0.58 [0.43, 0.74] | disagree |
| 10¹¹ | 0.40 | ℤ[i] | 0.26 [0.23, 0.29] | 0.75 [0.55, 0.95] | disagree |
| 10¹¹ | 0.45 | ℤ[√2] | 0.15 | 0.26 [0.19, 0.33] | disagree |
| 10¹¹ | 0.45 | ℤ[i] | 0.16 | 0.48 [0.35, 0.61] | disagree |
| 10¹¹ | 0.55 | ℤ[√2] | 0.034 | 0.089 [0.065, 0.11] | disagree |
| 10¹¹ | 0.55 | ℤ[i] | 0.076 | 0.14 [0.11, 0.18] | disagree |
| 10¹¹ | 0.60 | ℤ[√2] | 0.027 | 0.14 [0.10, 0.18] | disagree |
| 10¹¹ | 0.60 | ℤ[i] | 0.050 | 0.17 [0.13, 0.22] | disagree |

- **Method A:** 250 arcs at the three declared cells (10¹⁰ β 0.40 and 0.45, 10¹¹ β 0.40), 1,000 elsewhere. The interval
  is ±5% where not shown. The two arc counts agree to within 0.01 everywhere.
- **Method B:** pooled over m = 5, 7 and 13. The per-m ratios scatter widely; at 10¹¹ β 0.60 ℤ[i] they are 0.12, 0.62
  and 0.16.

## Reading, as declared before the run

- **Each method's direction.**
  - Method A puts the noise **above** the model at all 16 cells.
  - Method B puts it above at 15 and is consistent with the model at 1.
  - Neither puts it below anywhere. **So the hypothesis that RQ1's passes are conservative is not supported.**
- **Agreement.** The two empirical methods **disagree at all 16 cells**: their 90% intervals never overlap, and A's
  noise is 1.6–5× B's.
- **Will's rule therefore applies: report the disagreement and draw no conclusion.**

## Always reported, descriptive only (declared in advance; not a verdict)

| | t | sealed T (model SE) | T with A's SE | T with B's SE |
|---|---|---|---|---|
| B2 T at 10¹⁰ / 10¹¹ | 5.238 | 7.443 | 1.62 | 3.57 |
| P1 T at 10¹², the 10¹¹ ratio carried over (extrapolation) | 3.928 | 4.412 | 0.82 | 1.89 |

**If** either empirical SE were the right noise for these statistics, both B2 and P1 would fall below their thresholds.
Because the methods disagree, the rule draws no conclusion from this. It is stated so the stakes are visible.

## What is open (possibilities, not tested)

**What each method may be measuring.** Both methods may be measuring structure that is not sampling noise:
- *Method A, the block arcs:* the arcs' contributions to the variance integral may differ systematically, through a
  smooth finite-X modulation of the angle density.
- *Method B, the residue-class subsets:* classes p mod m may carry class-dependent secondary terms, of Chebyshev-bias
  type.

Either would inflate the "SE" without being noise in the sense the sealed comparison needs.

**What the sealed model's c captures.** The model's c was calibrated on mirror-symmetrised Poisson and lattice families,
not on arithmetic sets. Whether the right noise model for a deterministic arithmetic set is any of these three is itself
the open question. It mirrors GEO1, where the deterministic structure went the other way (the jackknife overstated by
about 10×).

**What would settle it** is a third method whose meaning is unambiguous for a deterministic set, for example the spread
of D across disjoint X-ranges at matched N. That needs Will's decision.
