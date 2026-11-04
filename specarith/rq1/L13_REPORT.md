# L13: RQ1's sealed SE model against empirical SEs on the arithmetic angle sets (descriptive; no seal)

**Current reading (Will, 2026-11-04; replaces "no conclusion"): see "L13 reading" at the end.** The sections in between
are the record in order; their "no conclusion" lines were correct when written and are superseded by that reading.

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

## Slices: second differences over disjoint matched-N slices (Will, 2026-11-03; descriptive, new run)

Method and cost committed before running (55fe5b23, `rq1_l13_slices.py`); run on spot as pueue 1220 in specarith-scored,
after ARSv2's first wave had its cores. Cost 0.44 core-h, 0.87× the model. Output: `results/l13/L13_SLICES.json`.

**Design.** Nine consecutive disjoint slices of n = 227,524,967 rows (RQ1's 10¹⁰ matched n) below the 10¹¹ boundary,
the same rows for both fields. Per slice R at K = round((2n)^β). Then σ̂² = Σ d²/(6·7) from the seven second
differences d = R_t − 2R_{t+1} + R_{t+2}, which cancel a linear drift in prime order exactly. The 90% interval comes
from the exact i.i.d.-normal null of the quadratic form (factor 0.65–2.21 on σ). Slice 0 reproduced the sealed 10¹⁰ R
bit for bit (guard).

| Field | β | K | Slices: model / empirical [90%] | Reading | L13 A (block arcs) | L13 B (residue subsets) [90%] | Drift per slice | Curvature z |
|---|---|---|---|---|---|---|---|---|
| ℤ[√2] | 0.40 | 2,906 | 0.955 [0.433, 1.480] | consistent | 0.317 | 0.558 [0.41, 0.70] | −0.0065 | −0.13 |
| ℤ[√2] | 0.45 | 7,873 | 1.403 [0.636, 2.175] | consistent | 0.204 | 0.317 [0.23, 0.40] | −0.0079 | −0.17 |
| ℤ[√2] | 0.55 | 57,801 | 1.941 [0.879, 3.008] | consistent | 0.056 | 0.135 [0.10, 0.17] | −0.0101 | +0.76 |
| ℤ[√2] | 0.60 | 156,616 | 0.316 [0.143, 0.489] | above | 0.043 | 0.195 [0.14, 0.25] | −0.0092 | −0.70 |
| ℤ[i] | 0.40 | 2,906 | 1.403 [0.636, 2.174] | consistent | 0.273 | 1.093 [0.80, 1.38] | −0.0088 | +0.13 |
| ℤ[i] | 0.45 | 7,873 | 1.051 [0.476, 1.629] | consistent | 0.219 | 0.742 [0.54, 0.93] | −0.0089 | +0.07 |
| ℤ[i] | 0.55 | 57,801 | 0.948 [0.430, 1.469] | consistent | 0.120 | 0.244 [0.18, 0.31] | −0.0091 | −0.00 |
| ℤ[i] | 0.60 | 156,616 | 0.490 [0.222, 0.759] | above | 0.083 | 0.265 [0.19, 0.33] | −0.0097 | −0.36 |

**Reading (descriptive, as declared).**
- **Slices against the model.** Consistent at 6 of 8 cells, including both fields at β 0.40, 0.45 and 0.55. Above at
  β 0.60 for both fields, at 2.0–3.2× the model.
- **The other estimates.**
  - The curvature-corrected σ and the three disjoint triples alone give the same picture (in the JSON).
  - The curvature checks are all |z| < 0.8, so no quadratic drift is detected.
- **Against L13's methods.**
  - The slices disagree with method A at all 8 cells (intervals do not overlap). They disagree with method B at 3 (ℤ[√2]
    0.45 and 0.55, ℤ[i] 0.55) and overlap it at 5.
  - The slices agree with FN1's cross-stage offset differences (L16: 0.69× the model at β 0.55, nine fields).
- **The drift is real but cancels here.** It runs −0.006 to −0.010 in R per slice, comparable to or larger than the
  model noise. Methods A and B do not segment by prime order (the L13 check, 2026-11-03), so their excess over the model
  is not this drift.
- **What this does not do.** It does not relabel RQ1, RQ1-c or L13's table. The three methods still disagree, so under
  Will's L13 rule no conclusion is drawn here. That is Will's to read.

### Will's record (2026-11-03, verbatim)

"Disjoint-slice second differences and the FN1 L16 stage difference are both drift-cancelled and independent of each
other. Both put the noise consistent with the SE model at β 0.40–0.55, with wide intervals (nine slices). At β 0.60
both fields sit at 2–3× the model. Method A disagrees at 8/8 cells and method B at 3/8." The L13 rule stands: no
conclusion yet. Accepted as descriptive; no relabelling.

### Which β each RQ1, RQ1-c and FN1 verdict used (Will, 2026-11-03)

| Verdict | Cells (β at X) | Uses the SE model? |
|---|---|---|
| RQ1 B2 (`RQ1_FINDINGS.md` §2) | β 0.40, 0.45 at 10¹⁰ and 10¹¹; K 2,906 / 7,873 / 7,013 / 21,213 | yes (T with SE_diff) |
| RQ1 B1 | dropped as a gate (round 87); D(β) descriptive at every β | — |
| RQ1-c P1 | β 0.40, 0.45 at 10¹²; K 16,987 / 57,395 | yes |
| RQ1-c P2 | descriptive, β 0.40–0.60 at 10¹² (the β 0.60 D falls below both logarithmic windows) | descriptive |
| RQ1-c P3 | crossover location on the fine grid β 0.45–0.65 at 10¹²; the verdict is the first crossing (0.538) | **no** (location only); β 0.60 lies on the grid beyond the crossing and does not decide it |
| RQ1-c P4 | β 0.55 at 10¹⁰, 10¹¹, 10¹²; K 57,801 / 194,125 / 655,245 | yes |
| FN1 stages 1–2 | β 0.55 primary; 0.45 and 0.40 secondaries | no for the rank verdicts (exact permutation); power and the −7 margin only |

**No sealed verdict in RQ1, RQ1-c or FN1 rests on a β 0.60 cell.** P4's 10¹¹ and 10¹² cells use larger K (194,125,
655,245) than the slices' β 0.60 cell (156,616), but far more points per bin (N/K ≈ 2·10⁴ and 5.7·10⁴, against 2,905).
The slices tested neither combination.

### OPEN ITEM: β 0.60 (Will, 2026-11-03; recorded only, no action)

At β 0.60 (K = 156,616, N/K ≈ 2,905 at the 10¹⁰ slice size) both fields' slice estimates sit at 2–3× the SE model. The
two candidate causes, as Will states them:
1. **The SE model breaking down at large blocks.**
2. **Deterministic oscillation between ranges** that second differences don't cancel.

No action beyond recording it.

## §9.G method calibration: A, B and slices on planted witnesses (Will, 2026-11-03; descriptive)

Method, cost and failure rule committed before running (88ec5207, `rq1_l13_calib.py`). Run on spot in specarith-filler
(idle weight): chunk 0 first (1.03× its model), then chunks 1–15. 160 replicates per case; total CPU 1.20× the model
(about 9.4 core-h). Outputs: `results/l13/calib/` (L13_CALIB.json and the 16 chunk files).

**Setup.**
- Nine ordered slices of 2·10⁶ half-angles per replicate, at L13's 10¹⁰ K values.
- Truth = the replicate SD of slice 0's R. Each method's estimate is the RMS over replicates, with 90% bootstrap
  intervals.
- **Declared failure:** the interval lies wholly outside [0.8, 1.25].
- (ii) is sized so that ΔR = |1 − R_ℤ[i]| at each cell (0.457 / 0.372 / 0.210 / 0.143), my reading of "the observed R
  excess". (ii)-small is 0.1× that.

**Estimate ÷ true SE** (A at its primary M; ! = fails the declared band):

| Witness | K 2,906 | K 7,873 | K 57,801 | K 156,616 |
|---|---|---|---|---|
| (i) iid: A / B / slices | 0.96 / 0.94 / 0.93 | 0.89 / 0.88 / 0.89 | 0.97 / 0.97 / 0.93 | 0.99 / 0.97 / 0.98 |
| (ii) modulation, full: A | 1.15 [1.05, 1.27] | **1.36 [1.25, 1.49] !** | 1.24 [1.14, 1.37] | **1.69 [1.55, 1.87] !** |
| (ii) full: B / slices | 0.99 / 0.95 | 0.99 / 1.02 | 0.94 / 0.96 | 1.08 / 1.15 [1.04, 1.28] |
| (ii)-small (0.1×): A / B / slices | 0.96 / 0.96 / 0.99 | 1.04 / 1.04 / 1.04 | 1.10 / 1.09 / 1.09 | 0.95 / 0.93 / 0.90 |
| (iii) linear drift: A / B / slices | 0.95 / 0.93 / 1.00 | 0.99 / 0.96 / 1.00 | 0.95 / 0.92 / 0.96 | 0.98 / 0.95 / 1.01 |
| (iii) quadratic drift: A / B / slices | 0.96 / 0.98 / 1.02 | 0.97 / 0.98 / 1.03 | 0.98 / 0.97 / 1.06 | 0.97 / 0.95 / 1.06 |
| (iv) ℤ[i] primes, uncoupled: A / B / slices | 1.08 / 1.07 / 1.09 | 1.11 / 1.08 / 1.09 | 1.02 / 1.01 / 1.00 | 1.05 / 1.04 / 1.00 |
| (iv) ℤ[i], coupled: B | **2.37 !** | **2.55 !** | **4.38 !** | **4.60 !** |
| (iv) ℤ[i], coupled: A / slices | 1.06 / 1.07 | 0.93 / 0.89 | 1.10 / 1.03 | 1.04 / 0.98 |
| (iv) ℤ[√2] primes, uncoupled: A / B / slices | 0.98 / 1.00 / 1.00 | 0.99 / 1.01 / 0.99 | 1.01 / 1.03 / 1.02 | 1.08 / 1.08 / 1.09 |
| (iv) ℤ[√2], coupled: B | **2.19 !** | **2.99 !** | **3.93 !** | **4.78 !** |
| (iv) ℤ[√2], coupled: A / slices | 0.99 / 1.03 | 1.08 / 1.07 | 0.98 / 0.98 | 1.10 / 1.12 |

**Further detail** (in the JSON):
- Truth ÷ model under (i) is 0.93–1.02: at this scale the SE model is accurate on iid angles.
- **A's inflation under (ii) depends on the arc count.** At M = 250 it is 1.84 (K 57,801) and 2.78 (K 156,616). At the
  primary M the lower bound is above 1 at all four cells.
- B's coupled failures come entirely from m = 5, the coupled modulus (5.0–11.8×). The m = 7 and m = 13 parts stay at
  0.88–1.10, so pooling dilutes the effect.

**Reading, by the declared rule and Will's ("A method that fails its witness is recorded as invalid for L13"):**
- **Method A: fails witness (ii) at 2 of 4 cells and is inflated at all 4.** Will's named hypothesis, that A inflates
  under smooth angular structure, is supported. Recorded as invalid for L13.
  - The planted modulation, sized at |1 − R|, inflates A by 1.15–1.69×. L13 measured A at 3–23× the model, so a
    modulation of this size accounts for only part of that. Descriptive.
- **Method B: fails witness (iv)-coupled at 8 of 8 cells** (2.2–4.8× pooled, through the coupled modulus). Passes
  (i)–(iii) and (iv)-uncoupled. Recorded as invalid for L13: it is not robust to angle–residue coupling. Whether the
  real angle sets carry such a coupling is not tested here.
- **Slices: fail no witness** (36 case-cells). The worst is 1.15 [1.04, 1.28] under the full modulation at K 156,616.
  Quadratic drift of the planted size moves it 2–6%.
- **What this does not do.** Nothing in RQ1, RQ1-c or L13's table is relabelled. Whether this resolves L13, with A and
  B invalid and slices standing, is Will's reading.

## L13 reading (Will, 2026-11-04, verbatim; replaces "no conclusion")

"Slices are the only noise estimator that passed every §9.G witness (36/36). Method A inflates under angular
modulation and method B under angle–residue coupling, so both are invalid as noise estimators for this statistic. By
slices, the noise is consistent with the SE model at β 0.40–0.55 for ℤ[√2] and ℤ[i], with 2–3× excess at β 0.60.
Open: the planted modulation explains only 1.15–1.69× of A's 3–23× excess, and coupling in the real data is untested."

§9.G calibration accepted (Will, 2026-11-04).

## Slices for ℤ[ω] (Will, 2026-11-04; descriptive, new run)

Method and cost committed before running (fe4dcd54, `rq1_l13_slices_zw.py`). It reuses 4ed68e0f's functions unchanged
on the ℤ[ω] archive: the same nine matched-N row ranges below the 10¹¹ matched n, and the same K. Run on spot as pueue
1391 (specarith-scored): CPU 824 s, **0.91× the model**. The guard held: slice 0's R at β 0.40, 0.45 and 0.55 equals the
RQ1-c read's 10¹⁰ ℤ[ω] cells bit for bit. Output: `results/l13/L13_SLICES_ZW.json` (with the ℤ[√2] and ℤ[i] tables
copied from `L13_SLICES.json`, not recomputed).

| β | K | ℤ[ω]: model / empirical [90%] | Reading | Curvature z | ℤ[√2] (4ed68e0f) | ℤ[i] (4ed68e0f) |
|---|---|---|---|---|---|---|
| 0.40 | 2,906 | 1.005 [0.455, 1.558] | consistent | +0.18 | 0.955 [0.433, 1.480] | 1.403 [0.636, 2.174] |
| 0.45 | 7,873 | 0.866 [0.392, 1.343] | consistent | −0.03 | 1.403 [0.636, 2.175] | 1.051 [0.476, 1.629] |
| 0.55 | 57,801 | 0.968 [0.438, 1.500] | consistent | +0.19 | 1.941 [0.879, 3.008] | 0.948 [0.430, 1.469] |
| 0.60 | 156,616 | 0.437 [0.198, 0.677] | above | −0.49 | 0.316 [0.143, 0.489] | 0.490 [0.222, 0.759] |

- ℤ[ω] shows the same pattern as the other two fields: consistent with the SE model at β 0.40–0.55, and above it at β
  0.60 (about 2.3× the model).
- **Process note (§9.I).** `rq1_l13_slices_zw.py`, like 4ed68e0f's `rq1_l13_slices.py` and the calibration's
  `rq1_l13_calib.py`, does not call `safeio.enforce()`. All three wrote only under `~/tmp/claude` on spot, and their
  outputs were copied into the repo by explicit scp + git add. The rule's substance held, but it was not enforced in
  code as §9.I requires. The ℤ[ω] run was also first started outside pueue (by running `pq-scored` directly over ssh).
  I killed my own three PIDs after about 2.5 minutes and requeued it as 1391. No output from the aborted start was
  kept.

## Label check (Will, 2026-11-04; desk arithmetic, no data read)

Definitions committed before the ℤ[ω] numbers existed (fe4dcd54, `rq1_label_check.py`; output
`results/l13/LABEL_CHECK.json`).
- **Slice upper bound** u = 1 ÷ the lower end of the slices' 90% interval on model/empirical, at the verdict's β and
  field.
- **Caveat:** the slices were taken at the 10¹⁰ matched N. The verdicts' 10¹¹ and 10¹² cells use the same β at larger N
  and K, and u at that β is applied to them as the brief says.

| Field | u at β 0.40 | 0.45 | 0.55 | 0.60 |
|---|---|---|---|---|
| ℤ[√2] | 2.31 | 1.57 | 1.14 | 6.99 |
| ℤ[i] | 1.57 | 2.10 | 2.33 | 4.51 |
| ℤ[ω] | 2.20 | 2.55 | 2.28 | 5.06 |

| Verdict | β used (X; K) | Flip factor | Upper bound U | Outcome |
|---|---|---|---|---|
| **RQ1 B2** (T rule) | 0.40, 0.45 at 10¹⁰ and 10¹¹ (K 2,906 / 7,873 / 7,013 / 21,213) | **1.42** (T/t = 7.443/5.238) | **2.31** (max over both fields and both β) | **keep** |
| **RQ1-c P1** (T rule) | 0.40, 0.45 at 10¹² (K 16,987 / 57,395) | **1.12** (4.412/3.928) | **2.31** | **keep** |
| **RQ1-c P4 ordering** (sign rule) | 0.55 at 10¹⁰, 10¹¹, 10¹² (K 57,801 / 194,125 / 655,245) | **1.40** (weakest inequality) | **2.33** (that inequality) | **keep** |

**How the flip factors are defined.**
- **B2 and P1:** if the true noise is f × the model at every cell, T in true units is T/f against the same t. So the
  verdict flips at f* = T/t, compared with the largest u over the verdict's fields and β.
  - Also computed: B2's T with each cell's SE scaled field by field to its u is 3.93, against t = 5.24.
- **P4:** the sealed rule is sign-only (R_√2 > R_ω > R_i), so no noise inflation changes the observed ordering.
  - Under its sealed null (three sets at equal R, exchangeable independent noise), the false-PASS rate is about (1/6)³
    at any noise scale. This reading is reported, but it does not address what the label is about: whether the
    separations exceed the noise.
  - **The declared reading is per inequality:** f* = z/1.645, the inflation at which that inequality stops being
    one-sided 5% significant, compared with U = max(u_a, u_b) at β 0.55. An upgrade needs all six inequalities to
    clear their bound.

| X | Inequality | z (model SE) | f* = z/1.645 | U | z at the slice bound | Clears U? |
|---|---|---|---|---|---|---|
| 10¹⁰ | ℤ[√2] − ℤ[ω] | 6.45 | 3.92 | 2.28 | 3.65 | yes |
| 10¹⁰ | ℤ[ω] − ℤ[i] | 2.30 | **1.40** | 2.33 | 1.00 | **no** |
| 10¹¹ | ℤ[√2] − ℤ[ω] | 10.09 | 6.14 | 2.28 | 5.70 | yes |
| 10¹¹ | ℤ[ω] − ℤ[i] | 3.06 | **1.86** | 2.33 | 1.33 | **no** |
| 10¹² | ℤ[√2] − ℤ[ω] | 13.80 | 8.39 | 2.28 | 7.76 | yes |
| 10¹² | ℤ[ω] − ℤ[i] | 5.03 | 3.06 | 2.33 | 2.18 | yes |

**Result.**
- **No verdict qualifies for the upgrade.** The labels stay as they are: "PASS under the sealed SE model; L13 shows
  empirical fluctuation measures exceed that model (methods disagree); significance unresolved". Both numbers are
  stated beside each label in `RQ1_FINDINGS.md`, `RQ1C_READ_REPORT.md` and `RQ1C_FINDINGS.md`.
- **No verdict is changed.**
- **What sits closest:**
  - **P4's ℤ[√2] > ℤ[ω] half** clears its bound at all three X.
  - **Its ℤ[ω] > ℤ[i] half** clears it only at 10¹².
  - **B2 and P1** are bounded by the wide nine-slice intervals at β 0.40 (ℤ[√2], u 2.31). Their flip factors (1.42,
    1.12) lie inside the range the slices cannot exclude.
