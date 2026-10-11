# PH2S Stage 2 — CS08's theory-fixed prediction of the zeros' tapered window-variance growth, tested on F2 (PH2S_SEAL 2.0)

**Status: TEXT FOR WILL'S GO, with one item open: the pooling construction (§4; `PH2S_STAGE2_PREREAD.md` §6).**
- **Design decisions:** nineteenth to twenty-seventh rounds (`../ph2/PH2_DECISIONS_2026-10-07.md`); the prediction is
  `../cs4/G_S_DESIGN.md` §6, amendments 1–8.
- **The prediction is already public:** tag `ph2s-stage2-prediction` (commit 8bc570d1), pushed before any F2 zero was
  downloaded.
- **Pre-read:** complete (`PH2S_STAGE2_PREREAD.md`). No F2 zero has been downloaded or decoded.
- **Order after Will's go:**
  1. Build the seal JSON (`make_seal_json.py`), then the seal commit and tag `ph2s-stage2-seal`.
  2. Will downloads the five F2 files by hand into `../ph2r2/data/platt_fresh/`.
  3. Run `python s2read.py read` on spot. It checks every md5 against the pins before decoding anything.

## 1. What is tested, and its standing
Stage 1 (sealed, read on F1) established the direction: the zeros' pair-sum error bars shrink with block length beyond
a long sine-kernel baseline. Stage 2 tests the size of that shrink against a parameter-free prediction. The prediction
uses Conrey–Snaith's (CS08) ratios-conjecture n ≤ 4 correlations, through an assembly that reproduces the sine kernel
and the exact CUE results (`../cs4/GS_UNITARY_RESULTS.md`). It is computed for the statistic actually measured: the
file-averaged expectation of estimator B (amendments 7 and 8). Nothing in it is fitted to zeros.

## 2. Statistic and prediction
- **Window sums.** In unfolded coordinates x = N̄(t) (exact smooth count):
  S(c; b) = Σ_{i≠j} F(x_i − x_j)·exp(−π((x_i + x_j)/2 − c)²/b²).
  - F is the R₂ bump (u, w) = (0.5, 0.3), with pairs |x_i − x_j| ≤ 3.
  - Window centres are 3b apart, with the full ±4σ window inside the file (`tapered.py`).
- **Estimator B.** v̂_B(b) = Σ(S_{i+1} − S_i)²/(2(n − 1)b), and **ĝ_B = √(v̂_B(10⁴)/v̂_B(100))**.
  - E[v̂_B] = v(b)(1 − ρ₁(b)) exactly, which the prediction carries.
  - A smooth drift of the window mean and any constant part of C cancel.
- **SE.** SE_f = ½·ĝ_f·√(rSE₁₀₀² + rSE₁₀⁴²), with each rSE from the lag-0–2 autocovariances of the squared differences
  (`tapered.pooled_diff`).

| F2 file | ℓ (zero-weighted mean) | **g_B predicted** | windows n(100) / n(10⁴) |
|---|---|---|---|
| zeros_42446000.dat | 15.7502 | **0.6703** | 17546 / 175 |
| zeros_90746000.dat | 16.4972 | **0.6656** | 18379 / 183 |
| zeros_193646000.dat | 17.2491 | **0.6646** | 19216 / 192 |
| zeros_1848446000.dat | 19.5003 | **0.6829** | 21724 / 217 |
| zeros_17541746000.dat | 21.7500 | **0.7201** | 24231 / 242 |

- Sine kernel (GUE): g_GUE,B = 0.9591.
- Precision of the prediction (`../cs4/GS_ZETA_RESULTS.md` §2, §6.2): every check is ≤ 3e-5 of v. The dropped
  oscillating lag term is (2.0 ± 8.9)e-4 of v; it misses the 10⁻³ standard, accepted in the twenty-fifth round as
  ~6e-4 in g against a per-file SE of ~0.04.
- Prime-cutoff convergence at b = 10⁴: g_B moves by 9e-7 for 3·10⁵ → 10⁶.

## 3. Rule (Will, twenty-seventh round; option (a))
Per file: z_f = (ĝ_f − g_pred,f)/SE_f. Pooled, with weights w_f = 1/SE_f²:
d_pool = Σw(ĝ − g_pred)/Σw, SE_pool = (Σw)^{−1/2}, z_pool = d_pool/SE_pool.
- **Precision guard (reads only the SEs):** RESOLVABLE iff 2·SE_pool ≤ 0.07. Otherwise **NOT RESOLVABLE**.
- **PASS iff RESOLVABLE, |z_pool| ≤ 2 (R2) and ≥ 4 of 5 files have |z_f| ≤ 3 (R1).** Otherwise **FAIL**.
- **Reported regardless of verdict:**
  - pooled ĝ_B ± 95% CI (± 2·SE_pool), beside the pooled prediction with the same weights;
  - per-file ĝ_f ± SE_f beside g_pred,f;
  - the v̂_B ladder at all five rungs (descriptive).
- **Reading.**
  - PASS means the zeros' growth agrees with CS08 to within about ±13% of the predicted shrink (pooled 2·SE ≈ 0.037),
    less tightly on the high side, towards GUE (§4).
  - FAIL means a pooled deviation beyond 2 SE, or two or more files beyond 3 SE.
  - The direction against GUE is not a separate arm: Stage 1 established it, and the band excludes GUE.

## 4. Pre-read record (no F2 zero read; `PH2S_STAGE2_PREREAD.md`)
- **SE validity for the zeros.** A Gaussian model with CS08's non-decaying window correlations would make the lag-0–2
  SE 2.4–4× too small at b = 100. On F1 (seen data) it is not: lag-0–2, lag-K (K ≤ 100) and batch-means SEs agree at
  every rung in all six files.
- **GUE calibration, on the Stage 2 baseline** (24 × 10⁶ sequences, `f2_gue_levels.py`; Stage 1's 16 as replication):
  - **Per file:** z SD 1.05–1.09; P(|z| > 3) = 0.006–0.009 (nominal 0.0027). The plug-in SE is 5–9% small, with a
    heavier lower tail.
  - **Pooled, as adopted (inverse-variance weights):** z_pool mean −0.35, SD 1.12.
  - **The actual false-FAIL rate of the adopted rule is 9.0%** (Stage 1 replication: 8.5–9.0%). Round 27 recorded
    "~6–7%", taken from the χ² model, which understates the skew. Weights ∝ 1/ĝ² favour low draws.
  - **PENDING WILL (`PH2S_STAGE2_PREREAD.md` §6):** keep this construction and record 9%, or switch to weights fixed
    pre-data ∝ n_f(10⁴) − 1 (false-FAIL 5.5–5.7%; power 0.88 / 0.76 against a 20% shrink error).
- **Operating characteristics of the adopted rule** (`opchar`; SE model κ·√(3/(n − 1)), κ = 1 typical of F1 and
  κ = 1.37 the worst F1 file). Alternatives are g = g_pred + ε(g_GUE,B − g_pred).

  | ε | −0.3 | −0.2 | −0.1 | 0 | +0.1 | +0.2 | +0.3 | GUE |
  |---|---|---|---|---|---|---|---|---|
  | P(PASS), κ = 1 | 0.001 | 0.076 | 0.56 | 0.937 | 0.81 | 0.32 | 0.039 | 0.000 |
  | P(PASS), κ = 1.37 | 0.027 | 0.24 | 0.66 | 0.921 | 0.91 | 0.65 | 0.29 | 0.000 |

  - **Power against a 20% error in the shrink:** 0.92 on the low side and 0.68 on the high side (towards GUE) at κ = 1;
    0.76 / 0.35 at κ = 1.37.
  - **False-FAIL rate with the prediction exact:** 6.3% (κ = 1) to 7.9% (κ = 1.37). On GUE see above.
- **Dry run (`s2read.py dryrun`, the read code):**
  - **F1 (seen; decoded through the read path; prediction interpolated in ℓ and held at the end values):** PASS, with
    z_pool = −0.24 and per-file |z| ≤ 0.92. The read path reproduces the stored window sums exactly. This is a pipeline
    check, not evidence.
  - **GUE stand-in at F2 geometry:** FAIL against the ζ prediction; PASS against the GUE prediction.
  - **Guard witness:** a would-be PASS (ĝ = prediction) with per-file SE 0.10 reads NOT RESOLVABLE.

## 5. Data
F2 (`../ph2r2/FRESH_SETS_F1_F3.md`, pinned 2026-10-09; a ≥ 1-file gap from every touched height range):

| file | heights [t₀, t₁) | md5 (pinned) |
|---|---|---|
| zeros_42446000.dat | [42,446,000, 44,546,000) | b9e8b34c5bab7367b68848c9e61940b0 |
| zeros_90746000.dat | [90,746,000, 92,846,000) | 8b05f3b38121178a7e563517ea08d0fe |
| zeros_193646000.dat | [193,646,000, 195,746,000) | 69b955f15e063c3646f4c92092f12290 |
| zeros_1848446000.dat | [1,848,446,000, 1,850,546,000) | 2169ed28b1dba1b889ccb25778eba4fc |
| zeros_17541746000.dat | [17,541,746,000, 17,543,846,000) | c706184af0a09d8f0df825ee9a81718a |

- **Download:** by hand by Will from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>`.
- **Read safeguards:** `s2read.py read` refuses unless:
  - the seal JSON exists;
  - this code, the decode modules and the prediction file match their pins;
  - all five md5s match before any file is decoded;
  - each file's heights lie in its pinned range.
- **Release:** the Zenodo release follows the read, bundling prediction, seal and result (twenty-fifth round).
