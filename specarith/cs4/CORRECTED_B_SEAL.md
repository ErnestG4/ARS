# Corrected (B): the offset-averaged third cumulant of the zeros' count at L* = 4, tested on F6 (CORRECTED_B_SEAL)

**Status: the seal text, approved by Will in round 61 (with the §4 addition on the F5 value).**
`seals/CORRECTED_B_SEAL.json` pins this file's sha256 and is built by `b2_sealread.py seal`, which re-runs every check and
refuses on any failure (spot, `ph6c`, with `GIT_DIR` a clone carrying the prediction tag). Then Will commits, tags `corrected-b-seal` and pushes; the seal manifest is
stamped with OpenTimestamps; the receipt is upgraded until Bitcoin-attested and verified on two explorers; only then
does Will download F6 by hand. The read runs twice in separate processes, then compare, then the report.
**The test stands alone (round 58):** its verdict is reported as the corrected (B)'s, with its own calibrated false-FAIL
rate. There is no joint reading with (A) or with the sealed (B).

- **Design:** `CORRECTED_B_DESIGN.md` (f014f447, committed before any computation for it; round 57). Decisions: rounds
  57, 58 and 61 (`../ph2/PH2_DECISIONS_2026-10-07.md`).
- **Why a corrected (B):** the sealed (B) read FAIL. That FAIL is attributed to its window grid being phase-locked to
  the zeros' near-lattice (`ROUTE_A_FINDINGS.md` §9, `DIAG_D_RESULTS.md`). Engine gate G1b now requires a windowed
  statistic at small L to average over the grid phase. This test is that statistic, on fresh data, with a calibration
  built from scratch. Nothing from the sealed (B)'s calibration is reused.
- **The prediction is public and timestamped.** Tag `corrected-b-prediction` (object 36796601…, commit 2ace4d7c),
  pushed to GitHub by Will on 2026-10-18 (seen by `git ls-remote` at 06:07:55 UTC on 10-19). OpenTimestamps receipt
  `timestamps/CORRECTED_B_PRESTAMP_2026-10-18.txt.ots`, Bitcoin-attested at block **972110** (2026-10-19 05:54:01 UTC);
  merkle root checked on blockstream.info and mempool.space (b4eadfbf).
- **No F6 file has been downloaded.** The only F6 facts used are the declared height ranges (n_f from exact θ).

## 1. What is tested
CS08's n ≤ 5 model (only ρ₁–ρ₃ enter) predicts the third cumulant of the number of zeros in an unfolded window of
length L: κ₃(L) = L + 3F₂ + F₃, i.e. κ₃^sine(L) plus an arithmetic part Δκ₃,f(L) at file f's height. The test measures
the amplitude μ of that arithmetic part in route (a)'s global μ family. μ = 1 is the prediction; μ = 0 is the sine kernel.
- **Estimator (design §1):** unfolded positions x = N̄(γ) − N̄(t₀) (exact θ, as in the sealed reads). For each of NU = 32
  offsets u_k = kL/32, take the counts in the windows [u_k + jL, u_k + (j + 1)L) that lie wholly inside [0, x_last], and
  their k-statistic k₃(u_k). Then **k̄₃ = mean over k of k₃(u_k)**, and **μ̂_f = (k̄₃ − κ₃^sine)/Δκ₃,f**.
- **SEs:** a joint-offset segment bootstrap (segments of 300, 1000, 3000 and 10000 unfolded units resampled together
  across all offsets), in μ units.
- **L\* = 4** by the design's data-free rule (§2): argmax of 1/SE_pool over {1, 1.5, 2, 3, 4, 5, 6}, from R = 100
  CUE_1000 replicates at F3 geometry (3071af35, `results/b2_rule.json` sha256 4add4356…).

  | L | 1 | 1.5 | 2 | 3 | **4** | 5 | 6 |
  |---|---|---|---|---|---|---|---|
  | SE_pool | 0.00815 | 0.00835 | 0.00639 | 0.00509 | **0.00489** | 0.00507 | 0.00603 |

  Every L was eligible on quadrature (max relative error 7e-9). The CUE mean μ̂ is within 0.0007 of 0 at every L.
- **G1b red path** (`b2_read.py` selftest, e3dfa9b3). On a jittered lattice (σ 0.3, n 2·10⁵, 8 random grid origins),
  the offset average moves at most 0.86 SE_boot across origins, against the 1 SE bound. The single-offset estimator
  moves 6.38 SE: the witness fires.
- **Nothing in the prediction is fitted to zeros.**

| F6 file | heights [t₀, t₁) | ℓ̄ | Δκ₃,f(4) | n_f (pre-data) | weight |
|---|---|---|---|---|---|
| zeros_46646000.dat | [46,646,000, 48,746,000) | 15.842 | −0.018511 | 5,294,932 | 0.21303 |
| zeros_256646000.dat | [256,646,000, 258,746,000) | 17.529 | −0.017674 | 5,858,774 | 0.23571 |
| zeros_2365046000.dat | [2,365,046,000, 2,367,146,000) | 19.747 | −0.016373 | 6,599,825 | 0.26553 |
| zeros_10630646000.dat | [10,630,646,000, 10,632,746,000) | 21.249 | −0.015449 | 7,102,031 | 0.28573 |

κ₃^sine(4) = 0.003703. Δκ₃ = 3ΔF₂ + ΔF₃ nearly cancels (−0.1406 + 0.1221 at the lowest file), as in the sealed (B).

## 2. Precision of the prediction and ∂μ*/∂μ
- **Prediction** `results/b2_pred.json` (sha256 df408d43…b5c836). All gates held before the tag (2ace4d7c):
  - G1: Δκ₃ ≠ 0 at every height.
  - G2: cutoff convergence 3·10⁵ → 10⁶, pooled δμ 3.9e-7 against 1% of the band (9.8e-5).
  - G4: cross-machine, 6 jobs recomputed on char (both cutoffs, both triangle orders), worst difference 0.0.
  - G5: the read selftest.

  Its own δμ: cutoff ≤ 4.9e-7, quadrature ≤ 3.2e-11, file average ≤ 8.9e-7 (lowest file); pooled 5.9e-7.
- **∂μ*/∂μ (round 53's rule).** The exact linear limit is 1. The offset-averaged estimator's known-answer slope on CUE_N
  at L = 4 (`results/b2_cuen.json`, sha256 f55bf032…; 24,000 batches of 20,000 Haar U(N), N = 8, 12, 16, 24, 32, with
  the cost-minimising allocation committed first, d7b757ee) is **slope 0.9976 ± 0.0044** (χ² 2.51 on 3, p = 0.47). The
  SE target ≤ 0.005 was reached without extension. |slope − 1| = 0.0024 ≤ 2·SE = 0.0088, so by the rule **g = 1** and
  **SE(slope) = 0.00438 enters δμ_sys**.
- **δμ_sys = 0.00438** (5.9e-7 prediction + 0.00438 slope).

## 3. Rule (followup_read.rule("B"), one code path; `b2_read.py`)
**Calibration** (`results/calib/b2_calib_declared.json`, sha256 3cebd02d…98dafd65, d7dd6282): 200 CUE_1000 replicates per
file at each file's pre-data size (char GPU, `b2_calsamp.py`), through the identical estimator. Nothing is reused from the
sealed (B)'s calibration. No fit failed.

| file | bias b_f (subtracted) | z(b_f) | SD_f |
|---|---|---|---|
| zeros_46646000.dat | +0.00092 | +1.22 | 0.01064 |
| zeros_256646000.dat | −0.00029 | −0.36 | 0.01130 |
| zeros_2365046000.dat | +0.00142 | +1.88 | 0.01069 |
| zeros_10630646000.dat | −0.00029 | −0.37 | 0.01098 |

**Ingredients:**
- **Block length:** BLOCK = 300 unfolded units, the shortest segment whose geometric-mean SE_boot/SD over files is ≥ 0.95
  (1.002, 1.001, 0.999 and 0.998 at 300, 1000, 3000 and 10000).
- **Corrected estimate:** μ̃_f = (μ̂_f − b_f)/g, g = 1.
- **Per-file SE:** SE_f = max(SD_f, SE_boot,f at segments ≥ BLOCK), widened by SD_f/√R in quadrature.
- **Pooling:** μ̃_pool = Σ w_f μ̃_f, SE_pool = (Σ w_f² SE_f²)^½.
- No goodness-of-fit test (a single statistic per file).

**Verdicts, in precedence order:**
- **FIT FAILURE** iff any file's estimate fails (not expected for k₃).
- **UNRESOLVED** iff 2·SE_pool > 0.25.
- **PASS** iff |μ̃_pool − 1| ≤ 2·SE_pool + δμ_sys, and at least 3 of 4 files have |μ̃_f − 1| ≤ 3·SE_f.
- **FAIL** otherwise.

**Band:** at the SE floor, 2·SE_pool + δμ_sys = 2 × 0.00550 + 0.00438 = **0.0154**. The read's own bootstrap can only
widen it. That is 2.5× narrower than the sealed (B)'s 0.0384.

**Operating characteristics** (200 CUE replicates per file, the whole rule including the per-file condition and the
final δμ_sys):
- **False-FAIL rate at μ = 1: 2/200 = 1.0%** (95% Clopper–Pearson 0.1–3.6%).
- **Power against μ = 0 (the sine kernel): 200/200 FAIL** (≥ 98.2%).
- **Acceptance (PASS count of 200):** μ 0.97: 1, 0.98: 42, 0.99: 174, 1.00: 198, 1.01: 179, 1.02: 39, 1.03: 1;
  0 at μ ≤ 0.96 and ≥ 1.04.

## 4. Reading
The verdict is reported as the corrected (B)'s, with its calibrated false-FAIL rate α = 1.0% (2/200).
- **PASS:** the arithmetic part of κ₃ at L = 4 is seen at the predicted amplitude once the grid phase is averaged out.
  This is consistent with attributing the sealed (B)'s FAIL to phase-locking. It does not reverse that sealed FAIL,
  which stands as read.
- **FAIL:** reported as a FAIL for this observable, with attribution limited to "observable-specific model terms or
  estimator". The phase-locking account of the sealed (B) does not cover it.
- **UNRESOLVED or FIT FAILURE:** reported as such, with no statement about μ. Neither is ever a PASS.

The F5 phase-averaged value (μ̃ = 1.0034, L = 3) was post-hoc on data already seen. It informed the choice of estimator
and is descriptive context only. This read, at L* = 4 on fresh F6 data under a data-free L rule, is the confirmatory
test; the two are not pooled.

## 5. Data
F6 (`../ph2r2/FRESH_SET_F6.md`, f6469b62; gap rule, ≥ 1-file gap from every touched range including F1–F5;
zeros_46646000.dat is the round-58 extra low-height file):

| file | md5 (pinned) |
|---|---|
| zeros_46646000.dat | aa9f1f18b0e724dc54f3d184cc596bd2 |
| zeros_256646000.dat | 020344a4229d8fc85f73fa1180aef729 |
| zeros_2365046000.dat | 93c286212f9405741d6454370e0e108d |
| zeros_10630646000.dat | ec13d8753e5e6e0a1161539df1d14a0a |

**Before any download:** Will has pushed `corrected-b-prediction` (done); this seal is stamped; its receipt is
Bitcoin-attested and verified. Download by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into
`specarith/ph2r2/data/platt_fresh/`.

**The read** (`b2_sealread.py read`) refuses unless the seal JSON exists and pins all of the following:
- this text;
- the code (twelve files);
- the interpreter (spot `ph6c`: Python 3.12.15, numpy 2.5.3, scipy 1.18.1, mpmath 1.4.1);
- the prediction, L\* (`b2_rule.json`), the slope run (`b2_cuen.json`), the calibration and the weights.

It also refuses unless the prediction matches the OpenTimestamps-stamped manifest (checked without git). It checks
every md5 before decoding anything, and each file's heights against its range. It runs twice in separate processes;
the two runs must be bit-identical or the read is VOID. It prints no estimate before that.

**Pre-seal record:**
- **Pipeline identity** at full F6 geometry (1c749cba). CUE stand-ins were placed at each file's heights, written in
  the Platt format, and decoded by the read's path. Per-offset k₃ and bootstrap SEs were identical to the estimator on
  the placed positions in all four files (positions differ by ≤ 9.3e-10, rounding of the long-double placement).
- **Dry run and refusals on the final code** (aacd3709). run1 = run2 bit for bit (37f1d9a6…). The stand-ins (μ = 0)
  read FAIL at μ̃_pool = −0.0086 ± 0.0118. Shifted to μ = 1, the same draw reads PASS at 0.9914 (descriptive). Every
  constructed defect is refused, and a correct seal passes.
- **Seal builder preflight** (spot, with the pushed tag; 50d2c90c) refused on `text_exists` alone, before this text was
  renamed from its draft. Every other check held.

## 6. Receipts
- **Prediction:** `timestamps/CORRECTED_B_PRESTAMP_2026-10-18.txt.ots`, manifest sha256 1b110981…ea0eb52, Bitcoin
  block 972110 (2026-10-19 05:54:01 UTC), verified on two explorers (`CORRECTED_B_PRESTAMP_2026-10-18_VERIFY.json`).
- **This seal:** `timestamps/CORRECTED_B_SEAL_STAMP_<date>.txt.ots`. It is stamped after the seal commit, then upgraded
  and verified (`verify_followup_stamp.py`) before any F6 download.
