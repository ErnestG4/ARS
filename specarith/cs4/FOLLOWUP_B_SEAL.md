# Route (a) replication (B): the third cumulant of the zeros' count at L = 3, tested on F5 (FOLLOWUP_B_SEAL)

**Status: the seal text, approved by Will in round 54.** `seals/FOLLOWUP_B_SEAL.json` pins this file's sha256 and is built by
`followup_sealread.py seal B`, which re-runs every check and refuses on any failure (spot, `ph6c`, with `GIT_DIR`
a bare clone carrying the prediction tags). Then Will commits, tags `followup-b-seal` and pushes; the seal manifest is stamped
with OpenTimestamps; the receipt is upgraded until Bitcoin-attested and verified on two explorers; only then does Will
download F5 by hand. The read runs twice in separate processes, then compare, then the report. (A) and (B) are read
independently: neither test's output is opened to interpret the other until both comparisons are done (round 54).

- **Design decisions:** rounds 46 and 48–54 (`../ph2/PH2_DECISIONS_2026-10-07.md`); rules in
  `FOLLOWUP_REPLICATION_RULES.md` (4cd011d8, addenda 7a6ef0db and 9e191edc).
- **The prediction is public and timestamped.** Tag `followup-b-prediction` (object 98610c85…, commit 19101965), pushed
  to GitHub by Will on 2026-10-17 (seen by `git ls-remote` at 00:08 UTC on 10-18). OpenTimestamps receipt
  `timestamps/FOLLOWUP_PRESTAMP_2026-10-17.txt.ots` (the same manifest as (A)'s), Bitcoin-attested at block **971918**
  (2026-10-17 23:43:33 UTC) and 971922; merkle roots checked on blockstream.info and mempool.space (dae368bb).
- **No F5 file has been downloaded.** The only F5 facts used are the declared height ranges (n_f from exact θ).

## 1. What is tested
An independent replication of route (a)'s PASS through the counting function. CS08's n ≤ 5 model (here only ρ₁–ρ₃
enter) predicts the third cumulant of the number of zeros in an unfolded window of length L = 3:
κ₃(3) = L + 3F₂ + F₃, at κ₃^sine(3) = 0.004823 plus the arithmetic part Δκ₃,f at file f's height. (B) measures the
amplitude μ of that arithmetic part in route (a)'s global μ family (μ = 1 the prediction, μ = 0 the sine kernel).
- **Estimator:** μ̂_f = (k₃ − κ₃^sine)/Δκ₃,f, with k₃ = W²m₃/((W − 1)(W − 2)) the k-statistic of the counts in the
  disjoint windows [jL, (j + 1)L) of the unfolded positions x = N̄(γ) − N̄(t₀) (exact θ). Moving-block bootstrap SEs over
  windows (exact, from block sums).
- **L = 3** by the data-free rule of rules §4 (b3fa4824); its round-50 known-answer χ² flag was chance (round 51 rerun
  p = 0.91, be061f38).
- **Nothing in the prediction is fitted to zeros.**

| F5 file | heights [t₀, t₁) | ℓ̄ | Δκ₃,f | n_f (pre-data) | weight |
|---|---|---|---|---|---|
| zeros_36146000.dat | [36,146,000, 38,246,000) | 15.594 | −0.015407 | 5,211,811 | 0.21051 |
| zeros_244046000.dat | [244,046,000, 246,146,000) | 17.479 | −0.013977 | 5,842,019 | 0.23597 |
| zeros_2377646000.dat | [2,377,646,000, 2,379,746,000) | 19.752 | −0.012343 | 6,601,600 | 0.26665 |
| zeros_10643246000.dat | [10,643,246,000, 10,645,346,000) | 21.250 | −0.011350 | 7,102,427 | 0.28688 |

Δκ₃ = 3ΔF₂ + ΔF₃ nearly cancels (e.g. −0.1132 + 0.0978 at the lowest file), which is why the block-cut share
criterion was withdrawn (round 50) and why (B) is the weaker observable; it gets the extra low-height file (round 51).

## 2. Precision of the prediction and ∂μ*/∂μ
- **Prediction** `results/followup_pred_B.json` (sha256 c0687b9a…7d149e). Gates all held before the tag: G1 Δκ₃ ≠ 0 at
  every height; G2 cutoff convergence 3·10⁵ → 10⁶: pooled δμ 2.6e-7 against 1% of the band (2.9e-4); G4 cross-machine
  (10 jobs incl. a κ₃ job, worst 2.2e-15); G5 both selftests. Its own δμ: cutoff ≤ 4.2e-7, quadrature ≤ 6e-11, file
  average ≤ 4.6e-6 (lowest file); pooled 1.25e-6.
- **∂μ*/∂μ (round 53).** The exact linear limit is 1 (κ₃ is linear in μ). The k-statistic's known-answer slope on
  CUE_N at L = 3 (`results/followup_cuen_r53.json`, sha256 72fe9f7f…cc1dd1; 227,000 batches of 20,000 Haar U(N),
  cost-minimising allocation committed first, 9e191edc): **slope 1.0019 ± 0.0045** (χ² 1.38 on 3, p = 0.71). The SE
  target ≤ 0.005 was reached without extension. |slope − 1| = 0.0019 ≤ 2·SE = 0.0090, so by the rule **g = 1** and
  **SE(slope) = 0.00449 enters δμ_sys**.
- **δμ_sys = 0.00449** (1.25e-6 prediction + 0.00449 slope).

## 3. Rule (rounds 50–53; `followup_read.py`)
**Calibration** (`results/calib/followup_calib_B_declared.json`, sha256 4d5ad7eb…cc3a9428, 891a238f): 200 CUE_1000
replicates per file at each file's pre-data size (char GPU, seeds [20261017, 52, 5, i, rep]), through the identical
estimator. No fit failed.

| file | bias b_f (subtracted) | z(b_f) | SD_f |
|---|---|---|---|
| zeros_36146000.dat | +0.00206 | +0.91 | 0.03205 |
| zeros_244046000.dat | −0.00366 | −1.64 | 0.03164 |
| zeros_2377646000.dat | +0.00189 | +0.75 | 0.03564 |
| zeros_10643246000.dat | −0.00070 | −0.29 | 0.03388 |

**Ingredients:**
- **Block length:** BLOCK = 100 windows (300 unfolded units; geometric mean SE_boot/SD 0.983–0.987 at every length).
- **Corrected estimate:** μ̃_f = (μ̂_f − b_f)/g, g = 1.
- **Per-file SE:** SE_f = max(SD_f, SE_boot,f(L) for L ≥ 100 windows), widened by SD_f/√R in quadrature.
- **Pooling:** μ̃_pool = Σ w_f μ̃_f, SE_pool = (Σ w_f² SE_f²)^½.
- No goodness-of-fit test (a single statistic per file).

**Verdicts, in precedence order:**
- **FIT FAILURE** iff any file's estimate fails (not expected for k₃; kept for symmetry with (A)).
- **UNRESOLVED** iff 2·SE_pool > 0.25.
- **PASS** iff |μ̃_pool − 1| ≤ 2·SE_pool + δμ_sys, and at least 3 of 4 files have |μ̃_f − 1| ≤ 3·SE_f (round 53: all
  files but one).
- **FAIL** otherwise.

**Band:** at the SE floor, 2·SE_pool + δμ_sys = 2 × 0.01695 + 0.00449 = **0.0384**. The read's own bootstrap can only
widen it.

**Operating characteristics (200 CUE replicates per file, the whole rule including the per-file condition and the
final δμ_sys):**
- **Combined false-FAIL rate at μ = 1: 6/200 = 3.0%** (95% Clopper–Pearson 1.1–6.4%).
- **Power against μ = 0 (the sine kernel): 200/200 FAIL** (≥ 98.2%).
- **Acceptance (PASS count of 200):** μ 0.94: 22, 0.96: 103, 0.97: 148, 0.98: 177, 0.99: 191, 1.00: 194, 1.01: 191,
  1.02: 176, 1.03: 146, 1.04: 98, 1.06: 25; 0 at μ ≤ 0.90 and ≥ 1.10. (B) resolves μ about 2.2× less finely than (A).

## 4. Joint reading (round 50; declared identically in both seals)
- Each test keeps its own calibrated false-FAIL rate: **α_A = 5.0%** (10/200), **α_B = 3.0%** (6/200). The
  **family-wise false-FAIL rate is 1 − (1 − α_A)(1 − α_B) = 7.85%**. The two tests use disjoint files (F4, F5), treated as independent under μ = 1: disjoint ranges, ≥ 6·10⁶ apart in height; residual long-range arithmetic correlation between them is not modelled.
- **Both PASS:** replication of route (a) by two further observables.
- **Exactly one FAIL:** reported as a FAIL for that observable, with attribution limited to "observable-specific model
  terms or estimator". It is not a refutation of route (a).
- **Both FAIL:** route (a)'s PASS is called into question, and that is reported plainly.
- If one test reads MODEL MISFIT, UNRESOLVED or FIT FAILURE, the other test’s verdict is reported on its own (a
  one-observable replication or FAIL), and no statement is made about the pair. If both do, each is reported as such
  and neither gives a reading. MODEL MISFIT, UNRESOLVED and FIT FAILURE are never a PASS (witnessed: every arm
  fires on constructed pairs, `results/followup_witness/witness.log`).

## 5. Data
F5 (`../ph2r2/FRESH_SETS_F4_F5.md`, 2528fdc5; v2 gap rule, ≥ 1-file gap from every touched range; zeros_36146000.dat is
the round-51 extra low-height file):

| file | md5 (pinned) |
|---|---|
| zeros_36146000.dat | 8fb15afc113768103c1b3891a83f9d54 |
| zeros_244046000.dat | 4f19fac76037c7f361b1a0c12a706b9b |
| zeros_2377646000.dat | abbec916f56f69bc96df594e735c5401 |
| zeros_10643246000.dat | 916639a260da1c6b84b291260b5627e6 |

**Before any download (round 53):** Will has pushed `followup-b-prediction` (done); this seal is stamped; its receipt is
Bitcoin-attested and verified. Download by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into
`specarith/ph2r2/data/platt_fresh/`.

**The read** (`followup_sealread.py read B`): refuses unless the seal JSON exists and pins this text, the code (eight
files), the interpreter (spot `ph6c`: Python 3.12.15, numpy 2.5.3, scipy 1.18.1, mpmath 1.4.1), the prediction, the
calibration, the weights and `followup_cuen_r53.json`, and the prediction matches the OpenTimestamps-stamped manifest
(checked without git); checks every md5 before decoding anything and each file's heights against its range; runs twice
in separate processes; the two must be bit-identical or the read is VOID; prints no estimate before that.

**Pre-seal record:**
- **Pipeline identity** at full F5 geometry (2b6b9e56): CUE stand-ins placed at each file's heights, written in the
  Platt format, decoded by the read's path: spacing error 0.0, window-count sequences identical, in all four files.
- **Dry run and refusals on the final code** (b67372f8): run1 = run2 bit for bit (03f245b7…); the stand-ins (μ = 0)
  read FAIL at μ̃_pool = −0.0001 ± 0.0368; shifted to μ = 1 the same draw reads PASS at 0.9999 (descriptive). Every
  constructed defect refused, a correct seal passes; joint-reading witness. Seal builder preflight refuses on
  `text_exists` alone (before this text was renamed from its draft).

## 6. Receipts
- **Prediction:** `timestamps/FOLLOWUP_PRESTAMP_2026-10-17.txt.ots`, manifest sha256 995dc21c…cf82fc, Bitcoin blocks
  971918 (2026-10-17 23:43:33 UTC) and 971922, verified on two explorers (`FOLLOWUP_PRESTAMP_2026-10-17_VERIFY.json`).
- **This seal:** `timestamps/FOLLOWUP_B_SEAL_STAMP_<date>.txt.ots` — to be stamped after the seal commit, then upgraded
  and verified (`verify_followup_stamp.py`) before any F5 download.
