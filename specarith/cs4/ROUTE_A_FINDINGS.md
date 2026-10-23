# Route (a) — findings: the ζ nearest-neighbour spacing law against CS08's n ≤ 5 prediction on F3

**Headline (Will's wording, round 49):** Route (a) PASS: consistent with the joint CS n ≤ 5 prediction (conditional on
the ratios conjecture; one statistic; ±1.6%). The statistic depends substantially on the n ≥ 3 correlation functions;
per-order connected constraints are not identifiable at this N_eff.

**Record:**
- Sealed under ROUTE_A_SEAL (commit 563cf804, tag `route-a-seal`, object b37e42a5). Will accepted the verdict as sealed
  in round 48.
- Read on spot under the pinned interpreter (ph6c: Python 3.12.15, numpy 2.5.3, scipy 1.18.1, mpmath 1.4.1),
  2026-10-15 08:03–08:25 PDT.
- Two reads in separate processes, bit-identical (sha256 28b23df8…); results in `results/read/` (798065dc).
- `verify_route_a_read.py` recomputes the verdict exactly from the stored per-file records.

## 1. Sealed verdict
**PASS, outcome row (a).**
- μ̃_pool = 0.9992 ± 0.0159 (95% CI [0.9833, 1.0151]).
- Files within 3 SE: 5/5. GoF pass: 5/5. No misfit file and no attribution (the attribution applies to a FAIL only).
- **The verdict does not depend on the rule's tunable parameters.** |μ̃_pool − 1| = 0.00076 is 0.05 of the band
  (2·SE_pool + δμ_sys = 0.0161).

| file | ℓ̄ | zeros decoded | μ̃_f (bias-corrected) ± SE_f | χ² (T_f) |
|---|---|---|---|---|
| zeros_15146000.dat | 14.762 | 4,933,732 | 0.9930 ± 0.0146 | 37.3 (60.9) |
| zeros_25646000.dat | 15.262 | 5,100,911 | 1.0026 ± 0.0137 | 31.2 (62.5) |
| zeros_248246000.dat | 17.496 | 5,847,696 | 0.9995 ± 0.0174 | 24.2 (58.9) |
| zeros_2373446000.dat | 19.750 | 6,601,008 | 1.0023 ± 0.0181 | 24.1 (62.1) |
| zeros_10639046000.dat | 21.250 | 7,102,294 | 0.9981 ± 0.0202 | 32.4 (64.2) |

- Each file's decoded zero count is within 2 of its pre-data θ count, and every height lies in its pinned range.
- SE_f is the calibration SD floor in every file.

## 2. What the statistic tests (pre-read, data-free; ROUTE_A_SEAL.md §2)
- **Block split:** the n ≥ 3 terms move the read's estimator limit by 0.551, about 34 band half-widths. So the statistic
  depends substantially on n ≥ 3 correlation functions; it is not a two-point test.
- **Cumulant cut:** not a valid decomposition at N_eff ≈ 3.4, so its increments are descriptive only.
- **Pair-level bound:** B₂ = 0.00327.

## 3. Connected-term sensitivity (rounds 48–49; POST HOC, data-free, derived)
**Per-order connected constraints are model-dependent and not identifiable at N_eff ≈ 3.4.**
- **Construction:** μ_k scales only κ_k's arithmetic part, k = 3, 4, wherever it appears, with every other cumulant at
  CS values (`route_a_connected.py`; `results/route_a_connected.json`; the 360 positivity rows, n = 3, 4 and 5, are in
  `results/connected/`).
  - For n ≤ 5 the change is exactly (μ_k − 1)(C_k − C_{k−1}) of the cumulant cut. A CUE known-answer test confirms
    this to 5.4e-16.
  - Derivatives use B₂'s method: the symmetric ±0.01 difference of the read's estimator limit, with changes at every
    node.
- **Why they are not identifiable:**
  - **Node-rule sensitivity:** the pooled derivatives change a lot with the treatment of the low-s nodes. ∂μ*/∂μ₃ is
    +0.267 with changes at every node (B₂'s rule) and +0.417 with the prediction's skip rule.
  - **Sign flip:** ∂μ*/∂μ₄ is +0.087 with changes at every node and −0.054 with the skip rule.
  - **Negative ρ₄ at ±0.02:** μ₃ and μ₄ at 0.98 and at 1.02 already give negative ρ₄. So these families are not point
    processes even 2% from the prediction.
    - Minimum over the quadrature points at s > 0.3: ρ₄ −3.9e-3 (μ₃ = 0.98), −2.0e-3 (μ₃ = 1.02), −1.5e-3
      (μ₄ = 0.98), −3.0e-3 (μ₄ = 1.02).
    - ρ₃ reaches −9.5e-4 (μ₃ = 0.98) and −1.1e-5 (μ₃ = 1.02).
    - These are against ζ's own minima there of ρ₃ > 0 and ρ₄ ≥ −5e-8, the numerical floor of ρ₄ at primes ≤ 1000
      (round 45's convention for n = 4).
    - Round 45's −1e-12 floor cannot be used for this comparison. ζ's own ρ₄ at primes ≤ 1000 is as low as −3.8e-2 at
      the smallest node (s = 0.0077), and its ρ₃ at primes ≤ 3·10⁵ is as low as −1.0e-6 there. So the comparison is
      made against ζ's own floor, at s > 0.3.
  - **The cause:** at N_eff ≈ 3.4, ρ_n vanishes near coincidence only because the connected terms cancel. Scaling one
    order alone breaks the cancellation where ρ_n^ζ ≈ 0. These are the same nodes the skip rule removes.
- The formal values |μ₃ − 1| ≤ 0.063 and |μ₄ − 1| ≤ 0.19 (B₂'s method) are not headline numbers; they are
  model-dependent.
- **B₂'s μ₂ family, checked the same way: also not a point process at ±0.02**, so B₂ is model-dependent in the same
  way.
  - At s > 0.3: ρ₃ −8.6e-6 (μ₂ = 0.98) and −9.5e-4 (μ₂ = 1.02); ρ₄ −9.9e-4 and −1.1e-3.
  - The μ₂ and μ₃ families mirror each other near coincidence (μ₂ = 1.02 ≈ μ₃ = 0.98): the κ₂ and κ₃ arithmetic
    corrections cancel there.
  - B₂ was never used: the read passed, and the attribution applies only to a FAIL.
- **n = 5 (ρ₅ through the ratios model, primes ≤ 1000):** every family also gives negative ρ₅ at ±0.02. At s > 0.3 the
  minima are −4.2e-3 (μ₃ = 0.98), −2.6e-3 (μ₃ = 1.02), −5.2e-3 (μ₄ = 0.98), −1.5e-2 (μ₄ = 1.02), −7.1e-4 (μ₂ = 0.98)
  and −9.5e-4 (μ₂ = 1.02), against ζ's own minimum there of −2.3e-8. At s > 1.0, every family's minimum is below ζ's at
  every node (60 of 60 rows each).

## 4. GoF note (descriptive only)
- **χ² against CUE, per file:** the five χ² values (37.3, 31.2, 24.2, 24.1, 32.4) set against the calibration's CUE
  means (33.0, 33.6, 32.8, 33.3, 33.9; SD 7.6–8.7) sit at the 72nd, 41st, 12th, 10th and 44th percentiles. Four of the
  five are below their CUE mean.
- **Pooled:** the sum is 149.2 against a CUE mean of 166.6 ± 19.4 (200 replicates), the 18.5th percentile
  (z = −0.89).
- **Reading:** the direction fits the rigidity-conservative covariance seen in the Phase 2 bins check. There, the zeros'
  bootstrap SE falls with block length and stays at or below the CUE spread. The read shows the same pattern: the
  bootstrap SE at L = 300 is 0.74, 0.85, 0.87, 1.02 and 0.95 × the CUE SD. The size of the χ² deficit is not
  distinguishable from CUE at five files.

## 5. F3 history (round 47, reconciled)
- **Download:** Will downloaded the five F3 files by hand from LMFDB on 2026-10-13 at 13:55–13:56 PDT (20:55–20:56
  UTC). This was after `route-a-prediction` (commit 0f0c5f77) had been pushed: GitHub's PushEvent is at 16:31:01 UTC.
- **md5 checks:** all matched the pins:
  - desktop and spot, 2026-10-13 ~13:56 PDT;
  - spot after the UPS swap that evening;
  - both machines, 2026-10-14 16:25 PDT (the round-47 audit);
  - spot, 2026-10-15 08:03 PDT, just before the read.
- **Copies:** the desktop worktree's `ph2r2/data/platt_fresh/` and spot's; none on char.
- **Nothing from F3 was decoded before 2026-10-15 08:03 PDT, when the sealed read began.**
  - The only code path that decodes F3 is the read, and it refuses without the seal JSON.
  - A search of every session transcript found only `ls`, `md5sum` and `scp` on the real files before then.
  - The pre-data counts came from θ.
  - The 2026-10-14 "round-trip" used synthetic CUE files at F3 geometry, written and deleted on char
    (`results/calib/pipeline_*`).
  - Full audit: `../ph2/PH2_DECISIONS_2026-10-07.md`, round 47.

## 6. Timestamps
**Summary (round 49).**
- The prediction and the rule files were anchored at Bitcoin block 971369 (2026-10-14 00:09 PDT), before any F3 decode.
- The seal is anchored by 08:21 PDT on 2026-10-15, after the read began at 08:03.
- GitHub's push-event time for the `route-a-seal` tag is a third-party timestamp: PENDING; GitHub's event feed showed no 2026-10-15 event
  as of 15:00 PDT.
- **Protocol change (round 49), effective now:** no decode until the seal's OpenTimestamps receipt is Bitcoin-attested
  and verified.

- **Prediction manifest** (f75e5816, `timestamps/ROUTE_A_PRESTAMP_2026-10-14.txt`, manifest sha256 444fa47f…):
  - Bitcoin block **971369** (2026-10-14 07:09:08 UTC; hash 000000000000000000012340e4b23b48d910fceea62ac9cd95421c0d2f4a2cfc),
    and also 971402 and 971415.
  - Each merkle root matches the block header on blockstream.info and mempool.space (`timestamps/ROUTE_A_PRESTAMP_VERIFY.json`).
  - That block is later than the F3 download. That the prediction came before the download rests on GitHub's push
    record.
- **Seal manifest** (485b7d20, `timestamps/ROUTE_A_SEAL_STAMP_2026-10-15.txt`, manifest sha256 1ce90d87…):
  - Bitcoin blocks **971591** (2026-10-15 15:21:06 UTC = 08:21 PDT) and 971594, verified the same way
    (`timestamps/ROUTE_A_SEAL_STAMP_VERIFY.json`).
  - It went to the calendars at 08:02 PDT, one minute before the read started. Its first Bitcoin block is 18 minutes
    after the read started, and the read did not wait for it.
  - So the Bitcoin anchor bounds the seal's existence only to 08:21 PDT. That the seal came before the decode rests on
    the tag's push to GitHub before the stamp (observed by ls-remote at about 08:00 PDT), the calendars' receipt at
    08:02, and the read's own refusal without the seal JSON.

## 7. Follow-up (rounds 46, 48–51)
- **Selection rule:** committed before any computation for it (`FOLLOWUP_SELECTION_RULE.md`, 6122a236). Its S_A
  criterion turned out to be empty on its grid.
- **Amendment 1** (968a8066): made after the PASS and after that defect, and before either candidate's power was
  computed. It gives the metric in the global μ family, the eligibility condition (block-cut n ≥ 3 share ≥ 0.55) and
  the new S_A. The choice is made after this PASS.
- **Form:** it runs as an independent replication: tagged prediction → OpenTimestamps stamp → fresh zeros → seal →
  read.
- **Selection abandoned (round 50).** The selection's one run (d3c50fa8) was defective: (A)'s ∂μ*/∂μ check returned 0
  and the every-node fits failed. No choice was made from it. Both candidates' replicate SEs were seen before round 50.
  (B)'s n ≥ 3 share criterion is withdrawn as ill-conditioned (the same cancellation as §3).
- **Both observables run as independent replications (rounds 50–51; `FOLLOWUP_REPLICATION_RULES.md`):**
  - (A), the next-nearest-neighbour law: window s ≤ S_A = 1.6, where the T₅ bracket disagreement first exceeds
    0.01 × the band at 1.7. ∂μ*/∂μ measured 1.0000. Fresh set F4: three files, L = 17.5, 19.75, 21.25.
  - (B), the third cumulant of the count: L = 3.0. ∂μ*/∂μ is the exact linear limit times a CUE_N known-answer slope
    (1.012 ± 0.026 at L = 3). The first run's L = 3 known-answer fit had χ² 11.0 on 3; the round-51 rerun (fresh seeds,
    2× the replicates; reading committed first, 7a6ef0db) gives χ² 0.54 (p = 0.91), slope 0.982 ± 0.018, so the first
    value is recorded as chance and no caveat is carried. Fresh set F5: the same three heights plus L ≈ 15.59. The weaker observable gets the extra
    low-height file, by Will's decision before any F4/F5 prediction, calibration or download
    (`../ph2r2/FRESH_SETS_F4_F5.md`).
  - Joint reading, declared in both seals: each test keeps its own calibrated false-FAIL rate, and the family-wise
    rate 1 − (1 − α₁)(1 − α₂) is reported. Both PASS: replication of route (a) by two further observables. Exactly
    one FAIL: a FAIL for that observable, with attribution limited to observable-specific model terms or estimator;
    not a refutation of route (a). Both FAIL: route (a)'s PASS is called into question, reported plainly.
- **Validity edge (descriptive).** The μ = 1 CS n ≤ 5 next-nearest-neighbour prediction goes non-positive near
  s ≈ 2.9 at F-set heights, which is a validity edge of the truncated expansion (`results/followup_window_A.json`:
  the windows s ≤ 2.9 and 3.0 are invalid).

## 8. Open lead (round 49)
Per-order connected constraints may become identifiable at larger N_eff, where the cancellation near coincidence is less
severe. That has to be weighed against the smaller arithmetic corrections there.

## 9. Replications, rounds 50–54
**Headline:** (A) replicates route (a): PASS. (B) reads FAIL. By the sealed joint reading that is exactly one FAIL: a FAIL
for observable (B), with attribution limited to observable-specific model terms or estimator. It is not a refutation of
route (a).

**Record:**
- Predictions tagged `followup-a-prediction` / `followup-b-prediction` (19101965), OpenTimestamps-attested at block
  971918 (dae368bb). Seals `FOLLOWUP_A_SEAL.md` / `FOLLOWUP_B_SEAL.md` (commit e9b385d1, tags `followup-a-seal` /
  `followup-b-seal`, re-pointed there before any stamp; decisions log round 54), seal receipts attested at block 972010
  and verified on two explorers (2009f818).
- F4/F5 downloaded by hand by Will on 2026-10-18 (09:42–09:44 PDT), after both seal receipts were verified; all seven
  md5s equal the pins on the desktop and on spot.
- Each observable read twice in separate processes on spot under the pinned interpreter; both pairs bit-identical
  ((A) sha256 74140319…, (B) 13006e00…). Neither result was opened until both compares were done (round 54). Results
  in `results/followup_read/` (c5cf6279).

**(A) Next-nearest-neighbour spacing law on F4: PASS.**
- μ̃_pool = 0.9981 ± 0.0171 against a band of ±0.0172.
- Per file 1.0025, 1.0043 and 0.9888, all within 3 SE.
- GoF χ² 19.0, 19.8 and 26.4 against thresholds 50.6, 52.9 and 52.5: no misfit.

**(B) Third cumulant of the count at L = 3 on F5: FAIL.**
- μ̃_pool = 0.8457 ± 0.0339 against a band of ±0.0384.
- Per file 0.546, 0.596, 1.255 and 0.891 (ℓ̄ 15.59, 17.48, 19.75, 21.25); none within 3 SE.

**Joint reading (sealed):** exactly one FAIL, (B). Family-wise false-FAIL rate 7.85% (α_A 5.0%, α_B 3.0%).

**Between-file heterogeneity in (B) (POST HOC, descriptive; `followup_posthoc.py`,
`results/followup_read/POSTHOC_between_file.json`).**
- The four files disagree with each other: χ²_between = Σ_f ((μ̃_f − μ̃_pool)/SE_f)² = **282.7 on 3**. The same statistic
  on the 200 CUE calibration replicates has **mean 3.0 and maximum 15.1** (none of 200 reaches the read). (A)'s files
  give 0.6 on 2.
- A calibrated false FAIL would not show between-file heterogeneity of this size: the calibration replicates are the
  false-FAIL distribution, and their largest between-file χ² is 15.1.
- Reasoning only, not tested: a model error that is smooth in height would move the four files' values monotonically
  with ℓ̄. The observed pattern (0.55, 0.60, 1.26, 0.89 with rising height) is non-monotone, so a smooth-in-height model
  error is unlikely to produce it on its own.
- At the two lower files the zeros' own bootstrap SEs (0.014–0.017 in μ) are about half the CUE spread (0.032), so the
  sealed SE floor binds there.
- **Untested hypothesis:** slow arithmetic fluctuations. Off-diagonal (nearly resonant prime) contributions to the third
  moment of the count would vary on height scales comparable to or longer than a file and not average out within one
  file, so each file's k₃ would carry its own offset. Δκ₃ is the small difference of two terms each about 7× larger, so
  a modest offset in k₃ (about 0.007 at the lower files) moves μ̂ a long way. Diagnostic D (round 55) is designed to
  test this; until then it is a hypothesis only.

Nothing about route (a)'s or (A)'s verdicts changes.

**Attribution of (B)'s FAIL (round 56; Diagnostic D, `DIAG_D_RESULTS.md`, 4905e226).**
- (B)'s FAIL is attributed to its **estimator**: the window grid is phase-locked, against a phase-averaged prediction.
  In unfolded coordinates the zeros sit near a lattice (S(t) has a standard deviation of about 0.4), and (B)'s
  integer-length windows start at N̄(t₀), so each file is read at one lattice phase φ = frac(N(t₀) − N̄(t₀)). The
  prediction, built from translation-invariant correlation functions, is the average over phase. The CUE calibration
  rotated every matrix at random and so averaged over phase; it could not detect this.
- **Evidence:** across 12 zero files (F3, F4, F5), r = −0.99 for k₂ and r = −0.88 for k₃ against cos 2πφ.
- **The slow-arithmetic hypothesis was tested and not supported:** D1/D2 read "none" in every F5 file (no excess
  between sub-blocks at any scale against each file's CUE null), each file's halves agree, and D3 estimates the
  near-resonant prime contribution at 2–7·10⁻⁵ in k₃, about 100× too small.
- **Route (a) and (A) are unaffected**, because spacings do not depend on the window origin.
- **Corrected (B): queued, not run** (round 56): its own pre-registration, an offset-averaged k₃ estimator, a CUE
  calibration through the same estimator, and fresh files; after the engine-repair work. (Since run and read: §10.)

## 10. Corrected (B), rounds 57–63
**Headline (Will's wording, round 63):** PASS, sealed: μ̃_pool = 1.0017 ± 0.0055, against a band of ±0.0154, with a
calibrated false-FAIL rate of 1.0%. All four files within 3 SE, with no heterogeneity. Stands alone. Consistent with the
phase-locking attribution of the sealed (B)'s FAIL; it does not reverse that FAIL. The F5 post-hoc value is context only
and not pooled.

**Record:**
- **Design:** `CORRECTED_B_DESIGN.md` (f014f447, round 57), committed before any computation for it. The estimator is
  k₃ of the counts averaged over 32 grid offsets u_k = kL/32. L\* = 4 was chosen by a data-free power rule on CUE
  replicates at F3 geometry (3071af35).
- **Prediction:** tag `corrected-b-prediction` (2ace4d7c), Bitcoin block 972110 (b4eadfbf).
  - ∂μ\*/∂μ: the CUE_N slope is 0.9976 ± 0.0044, so g = 1 and δμ_sys = 0.00438 (183912e1).
- **Calibration:** from scratch, 200 CUE_1000 replicates per file (d7dd6282). The sealed (B)'s calibration was not reused.
- **Seal:** `CORRECTED_B_SEAL.md` (approved in round 61 with the §4 line on the F5 value). Tag `corrected-b-seal`
  (d775b8a8), Bitcoin block 972187, verified on two explorers (be790e5d).
- **Data:** fresh set F6 (four files; `../ph2r2/FRESH_SET_F6.md`, f6469b62), downloaded by Will after that attestation.
  All md5s matched the pins locally and on spot before any decode.
- **Read:** on spot under the pinned interpreter, twice in separate processes, bit-identical (sha256 74deb6e7…).
  Results in `results/b2_read/` (8466747d).

**Sealed result.**
- μ̃_pool = 1.0017; SE_pool = 0.0055, at the calibration floor (the read's bootstrap did not widen it); 95% CI
  [0.9907, 1.0127].
- The band is 2·SE_pool + δμ_sys = 0.0154. |μ̃_pool − 1| = 0.0017 is 0.11 of the band.
- Files within 3 SE: 4/4 (3 needed).

| file | ℓ̄ | zeros decoded | μ̃_f (bias-corrected) ± SE_f |
|---|---|---|---|
| zeros_46646000.dat | 15.842 | 5,294,933 | 0.9991 ± 0.0107 |
| zeros_256646000.dat | 17.529 | 5,858,775 | 0.9996 ± 0.0113 |
| zeros_2365046000.dat | 19.747 | 6,599,825 | 1.0032 ± 0.0107 |
| zeros_10630646000.dat | 21.249 | 7,102,033 | 1.0041 ± 0.0110 |

- Each file's decoded count is within 2 of its pre-data θ count, and every height lies in its pinned range.
- **No heterogeneity (descriptive):** χ²_between = Σ_f ((μ̃_f − μ̃_pool)/SE_f)² = 0.16 on 3. The same statistic on the
  200 CUE calibration replicates has mean 3.1 and maximum 16.6, and 4% of them are at or below 0.16. The sealed (B) on
  F5 gave 282.7.
- **Reading (sealed §4):**
  - The arithmetic part of κ₃ at L = 4 is seen at the predicted amplitude once the grid phase is averaged out.
  - This is consistent with §9's attribution of the sealed (B)'s FAIL to phase-locking. It does not reverse that FAIL,
    which stands as read.
  - The F5 phase-averaged value (μ̃ = 1.0034 at L = 3, `DIAG_D_RESULTS.md`) was post-hoc on data already seen. It
    informed the choice of estimator and is context only; it is not pooled.

**Δκ₃'s two pieces (DESCRIPTIVE).** Δκ₃ = 3ΔF₂ + ΔF₃ is a near-cancellation: −0.141 + 0.122 at the lowest file, and
−0.112 + 0.096 at the highest.
- The read pins Δκ₃ to about 2·10⁻⁴ absolute: (|μ̃_pool − 1| + 2·SE_pool) × the weighted |Δκ₃| of 0.0169 is 2.2·10⁻⁴.
- So each piece agrees with the prediction to roughly 0.2%, unless their errors cancel.
- This is not a per-order constraint. As in §3, a test that varies one order alone is model-dependent at this N_eff,
  and the read constrains only the sum.

**Summary: three independent observables on disjoint fresh heights, plus Stage 2.** Each was sealed with a publicly
tagged prediction before its data was read.

| test | observable | fresh set (files) | CS orders entering | sealed result | SE_pool | band | calibrated false-FAIL |
|---|---|---|---|---|---|---|---|
| route (a) | nearest-neighbour spacing law | F3 (5) | n ≤ 5 | PASS, μ̃_pool = 0.9992 | 0.0080 | ±0.0161 | 5.5% |
| (A) | next-nearest-neighbour spacing law, s ≤ 1.6 | F4 (3) | n ≤ 5 | PASS, μ̃_pool = 0.9981 | 0.0086 | ±0.0172 | 5.0% |
| corrected (B) | offset-averaged κ₃ of the count, L = 4 | F6 (4) | n ≤ 3 | PASS, μ̃_pool = 1.0017 | 0.0055 | ±0.0154 | 1.0% |
| Stage 2 | tapered pair-statistic block variance (shrink vs CS) | F2 (5) | n ≤ 4 | PASS, shrink 1.01 [0.89, 1.14] | — | — | — |

- **The first three rows** are in the global μ family: μ = 1 is the CS n ≤ 5 prediction and μ = 0 the sine kernel. All
  three are consistent with μ = 1, conditional on the ratios conjecture.
- **Stage 2** is a different parameterisation: the measured/predicted shrink of a pair statistic's block variance under
  CS08's n ≤ 4 correlations (`../ph2s2/PH2S_STAGE2_FINDINGS.md`). It is consistent to about ±13%, also conditional on
  the ratios conjecture.
- **The sealed (B) on F5 (§9) is not in the table.** Its FAIL stands as read and is attributed to its estimator.
- The four fresh sets are disjoint by the gap rule (`../ph2r2/FRESH_SET_F6.md` asserts F6 against F1–F5).
- The rows are not pooled, and no combined significance is claimed. Each test keeps its own calibrated false-FAIL
  rate.

## 11. Calibration conservatism (round 64; across tests, descriptive)
In four places, measured at different heights with different statistics, the zeros fluctuate less than the CUE null
predicts:
- route (a)'s pooled GoF χ² sits at the 18.5th percentile of its CUE calibration (§4);
- (A)'s between-file χ² is 0.6 on 2 (§9);
- in the R₂ bins check, the zeros' drift-removed bootstrap SD falls to 0.59–0.75 of its 100-level value by 10⁴ levels,
  while a single 10⁶-level GUE sequence run through identical code stays at 0.92–0.99 (`../ph2r2/PH2R2_FINDINGS.md`
  §3, §6);
- the corrected (B)'s between-file χ² of 0.16 on 3 is at the 4th percentile of its CUE replicates (§10).

**Cause (round-66 correction; Will's wording, replacing round 64's "Berry-type saturation (untested)"):** consistent
with the arithmetic suppression of block variance already established for the pair statistic:
- R₂ §6, against a single 10⁶-level GUE sequence (5 of 5 bins);
- confirmed on fresh heights in Stage 1;
- size matched to CS08 in Stage 2.

R₂ §6 judged Berry saturation alone too weak and named few-prime form-factor fluctuations as the candidate.

**Stitching (round 70; replaces round 66's "part of the conservatism may come from stitching"):** stitching shown not to
affect these statistics' block variance within ±14% at G = 1,000; the zeros' lower variance is therefore not a
calibration artifact. Its cause for these local statistics is untested; the arithmetic suppression established for the
pair statistic is a candidate.
- The evidence is the L6 long CUE baseline: 50 CMV sequences of 10⁵ levels each (`../l6/L6_BASELINE_DESIGN.md` §13).
- The sensitivity is ±30% at G = 10,000.
- Against that baseline (descriptive; gate-2 stitched witness did not fire), Var_zeros/Var_long is:
  - route (a): 0.77, 0.68, 0.54, 0.40;
  - (A): 0.69, 0.56, 0.53, 0.44;
  - corrected (B): 0.31, 0.21, 0.18, 0.16;

  at G = 300, 1,000, 3,000 and 10,000.
- **Round 73 revision:** the G = 3,000 and 10,000 values use a long-baseline estimator free of the per-sequence
  bootstrap's mean-subtraction bias (`../l6/L6_BIAS_CORRECTION.md`). They were 0.58 / 0.43, 0.56 / 0.51 and 0.19 /
  0.18. The revised values match the file-sized stitched calibration's ratios.
- **Exact U(N) block variance (round 75; `../l6/N6_STAGE_A.md`):**
  - For corrected (B), the exact U(N) block variance is flat in G, to 0.05%. The CUE covariance is gone by r ≈ 10.
  - The zeros' halving of block variance between G = 300 and 10,000 is therefore entirely arithmetic long-range in
    origin.
  - The rounds 72–73 CUE "fall" was estimator bias, measured as +10% at G = 300 and +5% at G = 1,000.
  - Against the exact denominator, the zeros' ratio is 0.315, 0.209, 0.183 and 0.157 at G = 300, 1,000, 3,000 and
    10,000.

For route (a), (A) and the corrected (B), the calibration replicates are independent CUE_1000 blocks with no correlation
beyond a block, so they cannot separate generic long-sequence rigidity from an arithmetic cause. (Round 70: the L6 long
baseline now makes this separation for the three statistics. The deficit persists against a true long CUE sequence;
see above.)

**Correction (round 65): the pair statistic already has this separation on record.**
- **Long baseline:** R₂ §6 ran a 10⁶-level GUE baseline (Dumitriu–Edelman) through identical code. The zeros' shrink was
  distinguished in 5 of 5 bins.
- **Fresh heights:** PH2S Stage 1 confirmed it on F1.
- **Size:** Stage 2 matched it to CS08's n ≤ 4 prediction (shrink 1.01 [0.89, 1.14]).
- **Mechanism:** R₂ §6 judged Berry saturation of the mean two-point function too weak on its own (it moves a 10⁴-level
  block's variance only at order log b), and named few-prime form-factor fluctuations at τ < 1 as the candidate. That is
  Stage 2's model.
- **How this text went wrong:** the first version of this section (249f0470) copied R₂ §3's pre-§6 wording, which said
  the long baseline had not been run.
- **What was open, and is now done:** the separation for the three statistics above. Round 70's L6 long CUE baseline
  shows the deficit at every block size from 300 to 10,000 levels (descriptive). **What stays open** is its cause for
  these local statistics.

**Consequence:** the CUE-floor SEs are conservative for the zeros. The PASSes stand, and every sealed rule's power
against modest deviations from μ = 1 was understated. No verdict changes; the sealed bands are the ones read.

**Open lead (round 64; `../OPEN_LEADS.md` L6):** the ratio Var_zeros/Var_CUE of block statistics as a function of block
length, taken from the existing bootstrap outputs, as a direct measure of number-variance saturation at fresh heights.
It is descriptive first; any confirmatory version gets its own pre-registration. It is a candidate for the engine v2
gallery.
