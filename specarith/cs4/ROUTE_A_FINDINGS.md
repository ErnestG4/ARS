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
  CS values (`route_a_connected.py`; `results/route_a_connected.json` once the n = 5 tail lands; the n = 3 and n = 4 rows
  are in `results/connected/` on spot).
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
- The n = 5 points (ρ₅ through the ratios model, hours per node) are still being computed. They cannot make these
  families positive.

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

## 7. Follow-up (rounds 46, 48, 49)
- **Selection rule:** committed before any computation for it (`FOLLOWUP_SELECTION_RULE.md`, 6122a236). Its S_A
  criterion turned out to be empty on its grid.
- **Amendment 1** (968a8066): made after the PASS and after that defect, and before either candidate's power was
  computed. It gives the metric in the global μ family, the eligibility condition (block-cut n ≥ 3 share ≥ 0.55) and
  the new S_A. The choice is made after this PASS.
- **Form:** it runs as an independent replication: tagged prediction → OpenTimestamps stamp → fresh zeros → seal →
  read.

## 8. Open lead (round 49)
Per-order connected constraints may become identifiable at larger N_eff, where the cancellation near coincidence is less
severe. That has to be weighed against the smaller arithmetic corrections there.
