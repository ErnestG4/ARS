# Route (a) replication (A): the next-nearest-neighbour spacing law of the ζ zeros, tested on F4 (FOLLOWUP_A_SEAL)

**Status: the seal text, approved by Will in round 54.** `seals/FOLLOWUP_A_SEAL.json` pins this file's sha256 and is built by
`followup_sealread.py seal A`, which re-runs every check and refuses on any failure (spot, `ph6c`, with `GIT_DIR`
a bare clone carrying the prediction tags). Then Will commits, tags `followup-a-seal` and pushes; the seal manifest is stamped
with OpenTimestamps; the receipt is upgraded until Bitcoin-attested and verified on two explorers; only then does Will
download F4 by hand. The read runs twice in separate processes, then compare, then the report. (A) and (B) are read
independently: neither test's output is opened to interpret the other until both comparisons are done (round 54).

- **Design decisions:** rounds 46 and 48–54 (`../ph2/PH2_DECISIONS_2026-10-07.md`); rules in
  `FOLLOWUP_REPLICATION_RULES.md` (4cd011d8, addenda 7a6ef0db and 9e191edc).
- **The prediction is public and timestamped.** Tag `followup-a-prediction` (object cfbd50f0…, commit 19101965), pushed
  to GitHub by Will on 2026-10-17 (seen by `git ls-remote` at 00:08 UTC on 10-18, `timestamps/FOLLOWUP_PREDICTION_GITHUB_TAGS.json`).
  OpenTimestamps receipt `timestamps/FOLLOWUP_PRESTAMP_2026-10-17.txt.ots`, Bitcoin-attested at block **971918**
  (2026-10-17 23:43:33 UTC) and 971922; merkle roots checked on blockstream.info and mempool.space
  (`timestamps/FOLLOWUP_PRESTAMP_2026-10-17_VERIFY.json`, dae368bb).
- **No F4 file has been downloaded.** The only F4 facts used are the declared height ranges (n_f from exact θ).

## 1. What is tested
This replicates route (a)'s PASS (μ̃ = 0.9992 ± 0.0159) on an independent observable. CS08's n ≤ 5 ratios-conjecture
correlations predict how the zeros' next-nearest-neighbour spacing law p⁽²⁾(s) departs from the sine kernel's at the F4
heights. (A) measures the size of that departure, μ, in units of the prediction, in route (a)'s global μ family (every
arithmetic part scaled jointly; μ = 1 the prediction, μ = 0 the sine kernel).
- **Model:** p_μ(s) = p⁽²⁾_sine(s) + μ·Δp⁽²⁾_f(s) on the resolved bins of [S_RES, S_A), S_RES = 0.1714, S_A = 1.6.
  Δp⁽²⁾_f = ΔT₃ − 2ΔT₄ + 3ΔT₅ at file f's zero-weighted mean height, with ΔT₅ = −T₅^sine (the primary end of the T₅
  bracket; the ratios model's T₅^ζ ≈ 0 for s ≤ 1.8). Route (a)'s skip rule; prime cutoff 3·10⁵.
- **Estimator:** binned conditional maximum likelihood on 1e-4 bins (`followup_fit.fit_A`). A fit at its bound,
  non-finite, or with density ≤ 0 is a FAILURE, never a value. Moving-block bootstrap SEs (Phase 2's series form).
- **Nothing in the prediction is fitted to zeros.**

| F4 file | heights [t₀, t₁) | ℓ̄ | max\|Δp⁽²⁾\| | n_f (pre-data) | weight | ∂μ*/∂μ |
|---|---|---|---|---|---|---|
| zeros_252446000.dat | [252,446,000, 254,546,000) | 17.513 | 0.0239 | 5,853,282 | 0.29931 | 1.00000 |
| zeros_2369246000.dat | [2,369,246,000, 2,371,346,000) | 19.748 | 0.0202 | 6,600,418 | 0.33752 | 1.00001 |
| zeros_10634846000.dat | [10,634,846,000, 10,636,946,000) | 21.250 | 0.0182 | 7,102,163 | 0.36317 | 1.00001 |

## 2. Precision of the prediction (`results/followup_pred_A.json`, sha256 5b32efbb…4dc2fa; gates `results/followup_gates.json`)
- **Gates, all held before the tag:**
  - G1 positivity (min p_{μ=1} on the fitted bins 5.6e-7) and ∂μ*/∂μ re-measured at the F4 heights within 1e-3 of 1;
  - G2 cutoff convergence 3·10⁵ → 10⁶ at every node: pooled δμ 4.2e-7, against 1% of the band (1.2e-4);
  - G4 cross-machine: 10 spot jobs recomputed on the desktop and char, worst 2.2e-15;
  - G5 both selftests.
- **δμ_sys = 9.75e-5**, the w_f-pooled sum of every check in μ units: T₅ bracket 7.4e-5 / 9.7e-5 / 1.2e-4 per file
  (dominant), prime cutoff ≤ 7.2e-7, quadrature ≤ 1.2e-7, file average ≤ 2.5e-7, n = 6 bound ≤ 2.6e-8. Half-grid
  interpolation ≤ 1.1e-6 in Δp⁽²⁾.
- **Validity edge (findings §7):** the μ = 1 truncated prediction goes non-positive near s ≈ 2.9; the window stops at
  S_A = 1.6 by the data-free rule of rules §3.

## 3. Rule (rounds 50–53; `followup_read.py`, 9e191edc)
**Calibration** (`results/calib/followup_calib_A_declared.json`, sha256 3f039fce…300336, eeec6463): 200 CUE_1000
replicates per file at each file's pre-data size (char GPU, seeds [20261017, 52, 4, i, rep]), through the identical
estimator. No replicate fit or bootstrap fit failed.

| file | bias b_f (subtracted) | z(b_f) | SD_f | GoF threshold T_f |
|---|---|---|---|---|
| zeros_252446000.dat | −0.00052 | −0.59 | 0.01232 | 50.6 |
| zeros_2369246000.dat | +0.00009 | +0.08 | 0.01519 | 52.9 |
| zeros_10634846000.dat | +0.00068 | +0.61 | 0.01581 | 52.5 |

**Ingredients:**
- **Block length:** BLOCK = 300 (geometric mean SE_boot/SD over the files 1.015–1.018 at every length).
- **Corrected estimate:** μ̃_f = (μ̂_f − b_f)/g_f, g_f = ∂μ*/∂μ of §1.
- **Per-file SE:** SE_f = max(SD_f, SE_boot,f(L) for L ≥ 300), widened by SD_f/√R in quadrature, divided by g_f.
- **Pooling:** μ̃_pool = Σ w_f μ̃_f, SE_pool = (Σ w_f² SE_f²)^½.
- **GoF (round 53, a recorded pre-data deviation from route (a)):** binned χ² in 30 groups of equal sine-kernel
  probability on [S_RES, 1.6), not route (a)'s equal widths, because the window starts where p⁽²⁾_sine ~ s⁷ ≈ 1e-6 and
  equal widths would leave near-empty bins. Count floor: every group's pre-data expected count per file ≥ 5, with the
  committed adjacent-merge rule; at the F4 sizes no group merges (smallest expected count 31,103). T_f is the scaled-χ²
  quantile at α₁ = 1 − 0.99^{1/3} from the calibration only.

**Verdicts, in precedence order:**
- **FIT FAILURE** iff any file's fit fails (reported with its reason; never a value).
- **MODEL MISFIT** iff χ²_f > T_f in at least 2 files.
- **UNRESOLVED** iff 2·SE_pool > 0.25.
- **PASS** iff |μ̃_pool − 1| ≤ 2·SE_pool + δμ_sys, at least 2 of 3 files have |μ̃_f − 1| ≤ 3·SE_f (round 53: all files
  but one), and at least 2 of 3 files pass the GoF.
- **FAIL** otherwise.

**Band:** at the SE floor, 2·SE_pool + δμ_sys = 2 × 0.00856 + 0.0001 = **0.0172**. The read's own bootstrap can only
widen it.

**Operating characteristics (200 CUE replicates per file, the whole rule including the per-file condition):**
- **Combined false-FAIL rate at μ = 1: 10/200 = 5.0%** (95% Clopper–Pearson 2.4–9.0%). All ten are FAIL; none is
  MODEL MISFIT.
- **Power against μ = 0 (the sine kernel): 200/200 FAIL** (≥ 98.2%).
- **Acceptance (PASS count of 200) at other truths:** μ 0.96: 2, 0.97: 20, 0.98: 89, 0.99: 169, 1.00: 190, 1.01: 167,
  1.02: 83, 1.03: 18, 1.04: 1; 0 at μ ≤ 0.94 and ≥ 1.06.
- **Empirical GoF misfit:** 2/200 replicates have a file over its T_f (expected ≈ 2); 0/200 reach MODEL MISFIT.

## 4. Joint reading (round 50; declared identically in both seals)
- Each test keeps its own calibrated false-FAIL rate: **α_A = 5.0%** (10/200, this seal), **α_B = 3.0%** (6/200, (B)'s
  seal, under round 53's final δμ_sys). The **family-wise false-FAIL rate is 1 − (1 − α_A)(1 − α_B) = 7.85%**. The two
  tests use disjoint files (F4, F5), treated as independent under μ = 1: disjoint ranges, ≥ 6·10⁶ apart in height; residual long-range arithmetic correlation between them is not modelled.
- **Both PASS:** replication of route (a) by two further observables.
- **Exactly one FAIL:** reported as a FAIL for that observable, with attribution limited to "observable-specific model
  terms or estimator". It is not a refutation of route (a).
- **Both FAIL:** route (a)'s PASS is called into question, and that is reported plainly.
- If one test reads MODEL MISFIT, UNRESOLVED or FIT FAILURE, the other test’s verdict is reported on its own (a
  one-observable replication or FAIL), and no statement is made about the pair. If both do, each is reported as such
  and neither gives a reading. MODEL MISFIT, UNRESOLVED and FIT FAILURE are never a PASS (witnessed: every arm
  fires on constructed pairs, `results/followup_witness/witness.log`).

## 5. Data
F4 (`../ph2r2/FRESH_SETS_F4_F5.md`, 2528fdc5; v2 gap rule, ≥ 1-file gap from every touched range):

| file | md5 (pinned) |
|---|---|
| zeros_252446000.dat | 4d9c80df1f369a48e985cf5f2da870e6 |
| zeros_2369246000.dat | d2d328ee9dc75e908f4194d6aa45e0db |
| zeros_10634846000.dat | 873b302f888a8c58642ca9a6f4952a79 |

**Before any download (round 53):** Will has pushed `followup-a-prediction` (done, verified 2026-10-18 00:08 UTC); this
seal is stamped; its receipt is Bitcoin-attested and verified. Download by hand from
`https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into `specarith/ph2r2/data/platt_fresh/`.

**The read** (`followup_sealread.py read A`, eba70d06):
- refuses unless the seal JSON exists and pins this text, the code (eight files), the interpreter (spot `ph6c`: Python
  3.12.15, numpy 2.5.3, scipy 1.18.1, mpmath 1.4.1), the prediction, the calibration and the weights, and the
  prediction matches the OpenTimestamps-stamped manifest (checked without git);
- checks every md5 against the pins before decoding anything, and each file's heights against its pinned range;
- decodes with Phase 2's path (exact-θ unfolding, `followup_read.unfold`), forms the NNN bin sequence, fits;
- runs twice in separate processes; the two results must be bit-identical or the read is VOID; prints no estimate
  before that comparison.

**Pre-seal record:**
- **Pipeline identity** at full F4 geometry (2b6b9e56): CUE stand-ins placed at each file's heights, written in the
  Platt format, decoded by the read's path: spacing error 0.0, NNN bin sequences identical, in all three files.
- **Dry run** (87fe28cd, rerun on the final code below): run1 = run2 bit for bit; the stand-ins (μ = 0) read FAIL at
  μ̃_pool = 0.010 ± 0.018 with no misfit; shifted to μ = 1 the same draw reads PASS at 1.010 (descriptive).
- **Refusals:** 14 constructed defects each refused with the right reason; a correct seal passes every pin check.
- **On the final code** (b67372f8): read selftest; refusals: every constructed defect refused, a correct seal passes;
  joint-reading witness; dry run again bit-identical (a27e68e4…), same result. Seal builder preflight refuses on
  `text_exists` alone (before this text was renamed from its draft).

## 6. Receipts
- **Prediction:** `timestamps/FOLLOWUP_PRESTAMP_2026-10-17.txt.ots`, manifest sha256 995dc21c…cf82fc, Bitcoin blocks
  971918 (2026-10-17 23:43:33 UTC) and 971922, verified on two explorers (`FOLLOWUP_PRESTAMP_2026-10-17_VERIFY.json`).
- This seal: `timestamps/FOLLOWUP_A_SEAL_STAMP_<date>.txt.ots` — **to be stamped after the seal commit**, then upgraded
  and verified (`verify_followup_stamp.py`) before any F4 download.
