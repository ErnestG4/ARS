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
