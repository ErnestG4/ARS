# Route (a) — CS08 n ≤ 5 nearest-neighbour spacing law of the ζ zeros, tested on F3 (ROUTE_A_SEAL)

**Status: the seal text.** `seals/ROUTE_A_SEAL.json` pins this file's sha256 and is built by `route_a_sealread.py seal`
on Will's go (round 47). The record so far: cumulant cut and R₂ anchor merged 76392dac; witnesses a3a33320; round 47
provenance, stamp check and receipt verification f276596a / 0f36c007; final dry run d364ac51. The order:
1. Build `seals/ROUTE_A_SEAL.json` (`route_a_sealread.py seal`, which re-runs
   every check and refuses on any failure). It runs on spot under ph6c with `GIT_DIR=~/tmp/claude/route_a_tag.git`, a
   bare clone of tag `route-a-prediction` (spot's copy is not a git checkout). Then the seal commit and tag
   `route-a-seal` and the push; all three are Will's.
2. OpenTimestamps stamp of the seal manifest (tag object, seal JSON, this text) before any F3 decode.
3. F3 is already on spot (`~/tmp/claude/specarith/ph2r2/data/platt_fresh/`, md5-verified; §6 Provenance); nothing to
   copy.
4. On spot, under the pinned interpreter: `python route_a_sealread.py read run1`, then `read run2` in a separate
   process, then `compare`. The read checks every md5 against the pins before decoding anything and prints no estimate.
   `compare` requires the two runs to be bit-identical before the report is printed; any mismatch voids the read before
   interpretation (round 45). Then the report to Will.

- **Design decisions:** rounds 30–47 (`../ph2/PH2_DECISIONS_2026-10-07.md`).
- **The prediction is already public.** It is tag `route-a-prediction` (commit 0f0c5f77). GitHub recorded the push
  of that commit at 2026-10-13 16:31:01 UTC. The OpenTimestamps receipt `timestamps/ROUTE_A_PRESTAMP_2026-10-14.txt.ots`
  covers it together with the rule files at fd143231; it is Bitcoin-attested from block 971369 (2026-10-14 07:09:08
  UTC). Details are in §6.
- **F3 was downloaded on 2026-10-13 and md5-verified; no F3 content has ever been decoded** (§6 Provenance). Pre-read
  work used CUE draws, Phase 2's seen Platt bins and model computations only.

## 1. What is tested
CS08's ratios-conjecture correlations ρ₂…ρ₅, assembled into the nearest-neighbour spacing density through the
inclusion–exclusion series, predict how the zeros' spacing law departs from the sine kernel's at the F3 heights. Route (a)
measures the size of that departure, μ, in units of the prediction.
- **Model:** p_μ(s) = p_sine(s) + μ·Δp_f(s) on the window s ≤ 1.8. Δp_f is CS08's n ≤ 5 arithmetic part at file f's
  zero-weighted mean height (`results/route_a_zeta.json`, tagged). μ = 1 is the prediction and μ = 0 the sine kernel.
- **Estimator:** conditional maximum likelihood in the window (`route_a_read.MuFit`), with moving-block bootstrap SEs.
- **Nothing in the prediction is fitted to zeros.**

| F3 file | heights [t₀, t₁) | ℓ̄ | max\|Δp\| | n_f (pre-data) | weight |
|---|---|---|---|---|---|
| zeros_15146000.dat | [15,146,000, 17,246,000) | 14.762 | 0.0331 | 4,933,734 | 0.16676 |
| zeros_25646000.dat | [25,646,000, 27,746,000) | 15.262 | 0.0313 | 5,100,911 | 0.17241 |
| zeros_248246000.dat | [248,246,000, 250,346,000) | 17.496 | 0.0248 | 5,847,698 | 0.19765 |
| zeros_2373446000.dat | [2,373,446,000, 2,375,546,000) | 19.750 | 0.0200 | 6,601,009 | 0.22312 |
| zeros_10639046000.dat | [10,639,046,000, 10,641,146,000) | 21.250 | 0.0175 | 7,102,295 | 0.24006 |

Precision of the prediction (`route_a_zeta.json`): every check passes (TAGGABLE). The truncation bound is ≤ 1.2e-5
in μ per file. The systematic allowance δμ_sys = 2e-4 (round 38) covers the gap between the mean-height value and the
file average.

## 2. What the statistic tests (rounds 43–45; data-free)
**Block split** (`results/route_a_split.json`): each truncated model is taken as the truth for the read's own estimator,
and μ* is that estimator's limit (pooled with the weights above).

| model | n = 2 only (ρ₃..₅ sine) | n ≤ 3 | n ≤ 4 | n ≤ 5 (prediction) |
|---|---|---|---|---|
| pooled μ* | 0.449 | 0.836 | 1.000 | 1.000 |

- The n ≥ 3 terms move μ* by 0.551, about 34 band half-widths.
- **So route (a) does NOT test two-point structure only** (round 43's 0.25-band criterion).

**Cumulant cut** (round 44; `results/route_a_cumul.json`): Ck takes the connected correlations κ_j from ζ for j ≤ k and
from the sine kernel above.

| | C2 (pair) | C3 − C2 | C4 − C3 | C5 − C4 |
|---|---|---|---|---|
| pooled μ* increment | +0.2132 | +0.2661 | +0.0920 | +0.4286 |
| × band (0.016) | 13.3 | 16.6 | 5.7 | 26.8 |

Pooled μ* of the cut models: C2 0.2132, C3 0.4794, C4 0.5713, C5 0.99996.

- **Gate:** C5 recomputed (n ≤ 4 through the cumulant code path) reproduces the prediction: the recomputed n ≤ 4 terms equal the stored ones to
  1.5e-15, C5 equals the committed equivalence check to 3.0e-11, and pooled C5 = 0.99996. The partition algebra
  passes its known answers on CUE_4 and CUE_10 (cycle formula, reassembly and identity cut, all ≤ 3e-16).
- **Validity (round 45, criteria declared before the cut results):** the decomposition counts as valid only if every
  cut model is positive everywhere (ρ₃–ρ₅ ≥ −1e-12 on every quadrature grid, p(s) > 0 on the window grid) and the
  increments decay, |C3 − C2| > |C4 − C3| > |C5 − C4|. Result: **not a valid decomposition at N_eff ≈ 3.4.**
  - Every cut model has negative correlation functions. The minima over files and quadrature points are: ρ₃ of C2
    −0.048; ρ₄ of C2 −0.056 and of C3 −0.077; ρ₅ of C2 −0.048, of C3 −0.129 and of C4 −0.627.
  - p(s) stays positive on the window grid for every model (minimum 7.4e-5).
  - The increments do not decay. All four are positive, and |C5 − C4| = 0.429 exceeds |C4 − C3| = 0.092.
  A non-valid decomposition is reported descriptively and is not used for weights.
- **The cut models are not point processes.** Their n = 5 term is about 200 × T₅^sine at s = 1.8 (smoke test,
  2026-10-14), because replacing one cumulant class breaks the cancellation that makes ρ₅ small. So the cut pieces are
  computed at every node, and an n = 6 probe of the cuts at s = 1.8 shows no decay for C3 and C4: ΔT₆/ΔT₅ is +1.31e-2/−1.36e-2 (C3) and
  −1.99e-2/+1.72e-2 (C4). C2 alone decays (−4.7e-4/+1.47e-2). The prediction itself (C5) has T₆^sine = 1.4e-9 there.

**n = 5 presence** (round 44):
- **Block increment:** the n = 5 block increment in pooled μ* is −4.13e-4 (n ≤ 5 minus n ≤ 4: 0.99996434588 −
  1.00037734219; full precision in `route_a_split.json`). This is 0.026 band.
- **Pointwise values:** at the heaviest T₅ quadrature points (lowest file, s = 1.8), ρ₅^ζ is 1.8e-7–3.9e-7 against
  ρ₅^sine at 5.6e-4–6.0e-4. The correction is therefore about −ρ₅^sine: non-zero, and it enters the sum
  (`results/cumul/presence.json`). ζ's five-point density at these heights is about 0.05% of the sine kernel's (N_eff ≈ 3.4).
- **Truncation is excluded from attribution** (round 45). The n ≥ 6 terms, and n = 5 below the edge nodes, are bounded
  by ≤ 1.2e-5 in μ per file (`route_a_zeta.json`, check (c)), which is ≤ 0.001 band.

**R₂-anchored bound (round 45; `results/route_a_anchor.json`; primary attribution route).**
- **Construction:** μ₂ scales only the pair (κ₂) arithmetic correction, wherever κ₂ appears, including inside ρ₃–ρ₅.
  κ₃–κ₅ are held at their CS values, and μ₂ = 1 is the prediction.
- **Slope:** ∂μ*/∂μ₂ = +0.21771 (pooled), from the symmetric difference at ±0.01. Per file it runs from +0.2347 (lowest)
  to +0.2034 (highest). Linearity: the one-sided slopes agree to 2.4e-4 relative, and ±0.02 gives +0.21771.
- **Bound:** B₂ = |∂μ*/∂μ₂| · (|1.003 − 1| + 2 × 0.006) = 0.21771 × 0.015 = **0.00327** (0.20 band). This uses R₂'s own μ̂ = 1.003 ± 0.006, measured at R₂'s
  heights.
- **Assumption:** μ is a height-independent amplitude.

## 3. Rule (rounds 40–42; committed fd143231 / ef7119f4, calibration 397fe1f3)
**Calibration:** 200 CUE_1000 replicates per file, at each file's pre-data size, run through the identical pipeline
(`results/calib/route_a_calib_declared.json`, sha256 722e19de…b825, pinned in `route_a_read.CALIB_SHA256`).

| file | bias b_f (subtracted) | z(b_f) | SD_f | GoF threshold T_f |
|---|---|---|---|---|
| zeros_15146000.dat | +0.00244 | +2.36 | 0.01459 | 60.92 |
| zeros_25646000.dat | +0.00218 | +2.26 | 0.01367 | 62.48 |
| zeros_248246000.dat | +0.00156 | +1.27 | 0.01733 | 58.93 |
| zeros_2373446000.dat | +0.00136 | +1.08 | 0.01773 | 62.09 |
| zeros_10639046000.dat | −0.00107 | −0.75 | 0.02015 | 64.17 |

**Ingredients of the rule:**
- **Block length:** BLOCK = 300 (the geometric mean of SE_boot/SD over the five files is 0.996–0.998 at every length).
- **Corrected estimate:** μ̃_f = μ̂_f − b_f.
- **Per-file SE:** SE_f = max(SD_f, SE_boot,f(L) for L ≥ 300), widened by SD_f/√R in quadrature.
- **Pooling:** μ̃_pool = Σ w_f μ̃_f, SE_pool = (Σ w_f² SE_f²)^½.
- **GoF:** binned χ² with 36 bins on the window; T_f is the scaled-χ² quantile at α₁ = 1 − 0.99^{1/5}.

**Verdicts, in precedence order:**
- **MODEL MISFIT** iff χ²_f > T_f in at least 2 files.
- **UNRESOLVED** iff 2·SE_pool > 0.25.
- **PASS** iff |μ̃_pool − 1| ≤ 2·SE_pool + δμ_sys, and at least 4 of 5 files have |μ̃_f − 1| ≤ 3·SE_f, and at least
  4 of 5 files pass the GoF.
- **FAIL** otherwise.

**Always reported:** μ̃_pool ± 2·SE_pool and the per-file values; for any misfit file, the χ² bin residuals.

**Band:** at the SE floor, 2·SE_pool + δμ_sys = 0.016. The read's own bootstrap can only widen it.

**Operating characteristics (CUE, 200 replicates; round 43 notes):**
- **False FAIL with μ = 1:** 11/200 (5.5%).
- **Power against μ = 0:** 200/200.
- **Empirical false-misfit rate:** 3/200 at the file level, against an expected 2 (binomially unremarkable). 0/200 reach
  the 2-file MODEL MISFIT verdict.
- **At Phase 2's fitted SECONDARY law** (μ* = 0.958–0.976 per file; `route_a_equiv.json`), the verdict is not PASS in
  97.5% of replicates.

## 4. Outcome table (round 43; attribution round 45)
| row | condition | reading |
|---|---|---|
| (a) | verdict PASS | PASS: the spacing law agrees with CS08 n ≤ 5 at μ = 1 within the band |
| (b) | not PASS and μ̃_pool ∈ [0.955, 0.985] | FAIL, read as "the spacing law deviates from CS n ≤ 5 at μ = 1, in the direction of Phase 2's fitted law" |
| (c) | any other μ̃_pool | FAIL; above the band unattributed. A (c) result within 0.005 of a (b) edge is reported with its distance and not reclassified (round 46) |

- **Attribution (rounds 45–46).** It applies to every FAIL below the band (rows (b) and (c) alike) and uses the
  R₂-anchored bound B₂ = 0.00327 of §2:
  - A deviation 1 − μ̃_pool > B₂ is attributed to connected n ≥ 3 structure or to the estimator.
  - A deviation within B₂ is consistent with pair-level uncertainty. **This arm cannot fire at the sealed B₂.** A FAIL
    below the band needs 1 − μ̃_pool > 2·SE_pool + δμ_sys, which is at least 0.01598 at the SE floor (SE_pool ≥ 0.00789);
    that is 4.9 × B₂. So every FAIL below the band reads "connected n ≥ 3 structure or the estimator". The witness
    (`route_a_sealread.py witness`) confirms this and shows the arm's code fires with a constructed B₂ = 0.5.
  - Truncation is excluded (bound ≤ 1.2e-5).
  - The cumulant increments are used as weights only if §2 finds the decomposition valid.

  The read reports this statement itself (`route_a_sealread.evaluate`).
- **Row (b) bounds (round 46):** [0.955, 0.985], unchanged.
  - They approximate μ_P2 ± 2·SE_pool: Phase 2's fitted SECONDARY law gives pooled μ* = 0.966, and 2·SE_pool = 0.016 at
    the SE floor, so μ_P2 ± 2·SE_pool = [0.950, 0.982].
  - Under that law the rows capture as follows (replicates below): row (b) 90.5%, row (c) 7.0%, PASS 2.5%.
- **Row rates on the 200 CUE calibration replicates**, with each file's μ̂ shifted to a truth (`route_a_sealread.row_rates`):

  | truth | PASS (a) | FAIL (b) | FAIL (c) |
  |---|---|---|---|
  | μ = 1 | 94.5% | 2.5% | 3.0% |
  | Phase 2 fitted SECONDARY (pooled μ* 0.966) | 2.5% | 90.5% | 7.0% |
  | μ = 0.97 | 5.0% | 91.5% | 3.5% |
  | μ = 0.94 | 0 | 3.5% | 96.5% |
  | μ = 0 (sine) | 0 | 0 | 100% |

- **MODEL MISFIT** is reported independently of the row (confirmed in round 45). The row is always reported beside the
  verdict, and the precedence stays as sealed.

## 4a. Pre-declared follow-up (round 46; this seal commits to the logic, its parameters are sealed later)
- **Observable:** independent of the spacing law route (a) uses, with its own estimator and the same CS n ≤ 5 model.
  Either the next-nearest-neighbour spacing law or the third cumulant of the counting function, chosen by power before
  any route (a) result is seen.
- **Before its own seal:** a data-free sensitivity split, by the same R₂-anchored derivative method as B₂, showing that a
  majority of its arithmetic part comes from connected n ≥ 3 terms.
- **Data and record:** fresh zeros not yet downloaded, a tagged prediction, an OpenTimestamps stamp and a separate seal.
  Detailed parameters may be sealed later, but before that data is downloaded.
- **Reading:**
  - If both observables deviate in the predicted direction, the deviation is connected structure.
  - If only route (a) deviates, it is route (a)'s estimator.
- **If route (a) PASSes,** the same design runs as an independent replication.

## 5. Pre-read record (no F3 zero read)
- **Pipeline identity:** CUE levels at each F3 file's full geometry were placed with exact θ, written in the Platt
  format, decoded and unfolded. All five are bit-exact, with dμ = 0 (`results/calib/pipeline_*.json`).
- **Phase 2 bins check** (descriptive, seen data; `results/ph2bins/`). Each bin uses the nearest-ℓ F3 template, so its
  μ̂ is not a measurement.
  - P1–P6 decode through the read's path bit-identical to Phase 2's arrays.
  - μ̂: P1 +1.20, P2 +0.977, P3 +1.051, P4 +1.073, P5 +1.024, P6 +0.911; P1 and P6 lie outside the F3 ℓ range.
  - All χ² values are below their template's T.
  - The bootstrap SE falls with block length in every bin (the zeros' rigidity) and stays ≤ 1.03 × the scaled CUE SD,
    so the SE floor at the CUE spread binds.
- **Dry run** (`route_a_sealread.py dryrun`: the read code itself, on CUE stand-ins at F3 geometry under a dry-run seal;
  `results/dryrun/ROUTE_A_DRYRUN.json`):
  - **First pass** (`results/dryrun/first_run/`): the read decoded all five stand-ins and returned FAIL, row (c),
    μ̃_pool = −0.0123 ± 0.0164, with all five GoF-clean.
    - Shifted to μ = 1, the same results read PASS, row (a).
    - Shifted to Phase 2's fitted μ*, they read 0.9538: row (c), 0.0012 below row (b). The expectation of row (b) from
      a single draw was mis-specified, since one draw cannot certify a ~90% event. Row firing is certified by the
      replicate rates in §4 instead.
  - **Second pass** (row rates added; `results/dryrun/` at ac5cb2cf): identical result (fixed seeds), with all four
    expectations holding.
  - **Round-46 pass** (5b29d6df), identical to the final pass below.
  - **Final pass** (round-47 code, the code this seal pins: interpreter pins, the stamp check, two reads in separate
    processes, then compare; spot, ph6c; d364ac51):
    - run1 = run2 bit for bit (sha256 736cb437…).
    - FAIL, row (c), μ̃_pool = −0.0123 ± 0.0164, as in every earlier pass.
    - Attribution reported: 1 − μ̃_pool = 1.0123 > B₂ = 0.0033.
    - All five expectations hold.
- **Seal preflight** (`route_a_sealread.py seal --check`, writes nothing; `results/witness/seal_check.log`, d364ac51):
  it refused on `text_exists` alone, before this file was renamed to `ROUTE_A_SEAL.md`; every other check passed on
  spot.
- **Refusals** (`results/witness/refusals.log`, spot, ph6c). All fourteen fire, and a correct seal passes every pin
  check (positive control):
  - no seal;
  - interpreter, derived file, code, prediction, calibration or weights differing from the pins;
  - round 47: a one-byte change to the prediction with the seal rebuilt to agree with it (only the OpenTimestamps
    check catches this), a tampered stamped manifest, and a tampered receipt;
  - an md5 mismatch; a missing file; heights outside the range;
  - two runs that differ (VOID).
- **Reporting witnesses** (round 46; `results/witness/witness.log`): one calibration replicate shifted to set pooled μ̃
  values.
  - 0.952 → FAIL (c), reported 0.003 from the 0.955 edge and not reclassified, beyond B₂.
  - 0.945 → FAIL (c), not near an edge, beyond B₂.
  - 0.970 and 0.980 → FAIL (b), beyond B₂.
  - 1.000 → PASS (a), no attribution.
  - 1.040 → FAIL (c) above the band, no attribution.
- **Sampler record (round 42):** no sealed result used cbe.py. The Platt writer's negative-gap refusal caught the
  duplicate-root defect, which was fixed before the calibration.

## 6. Data
F3 (`../ph2r2/FRESH_SETS_F1_F3.md`, pinned 2026-10-09; at least a 1-file gap from every touched height range):

| file | md5 (pinned) |
|---|---|
| zeros_15146000.dat | 12759c6bf4892f90244d240a7893c96a |
| zeros_25646000.dat | 17769568c69cbabc1c47138f7159812e |
| zeros_248246000.dat | 763374d804b79351fa5890bc56cae1b4 |
| zeros_2373446000.dat | 10af7827aba9e214d135847c686e6d69 |
| zeros_10639046000.dat | 6203cd45f34fb389b3be1108bdf9c913 |

**Provenance (round 47; full audit in `../ph2/PH2_DECISIONS_2026-10-07.md`, round 47).**
- **Download:**
  - Will downloaded the five files by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` on 2026-10-13,
    at 13:55–13:56 PDT (20:55–20:56 UTC).
  - This was after `route-a-prediction` was pushed: GitHub's push event for 0f0c5f77 is at 16:31:01 UTC
    (`timestamps/ROUTE_A_PREDICTION_GITHUB_PUSH.json`).
- **md5 checks:** every check matched the pins:
  - on the desktop and on spot, 2026-10-13 13:56 PDT;
  - on spot after the UPS swap that evening;
  - on both machines on 2026-10-14 at 16:25 PDT, in the audit.
- **Copies now:**
  - the desktop worktree's `specarith/ph2r2/data/platt_fresh/`;
  - spot's `~/tmp/claude/specarith/ph2r2/data/platt_fresh/`;
  - none on char.
- **Decoded: never, up to this seal.**
  - The only code path that decodes F3 is this read, and it refuses without the seal JSON, which did not exist before
    this seal was built.
  - A search of every session transcript found only `ls`, `md5sum` and `scp` on the real files.
  - The n_f counts come from θ, not from file headers.
- **"Round-trip" and the dry run used synthetic CUE files only.** They carried F3 file names and geometry, but not F3
  content (`results/calib/pipeline_*`, `results/dryrun_synth` on spot, whose md5s differ from the pins).
- **Correction:** two statements of 2026-10-14 said F3 had not been downloaded; both were wrong about the download.
- **What the timestamps show:**
  - The F3 download (2026-10-13 20:55 UTC) came before the receipt's first Bitcoin block (2026-10-14 07:09 UTC). So
    the stamp shows the prediction existed by 07:09 UTC on 2026-10-14, not that it predates the download.
  - That it predates the download rests on GitHub's push record (16:31 UTC on 2026-10-13, 4.4 h before).
  - The prediction is computed from CS08's formulas alone, with no zeros.
- **Read safeguards:** `route_a_sealread.py read` refuses unless:
  - the seal JSON exists;
  - the prediction JSON's sha256 equals the one in the OpenTimestamps-stamped manifest of f75e5816 (round 47). This is
    checked without git or the seal: the manifest's sha256 must be the digest the receipt commits to, which is pinned
    in the code;
  - this code, ph2lib, the prediction, the calibration and the weights match their pins;
  - all five md5s match before any file is decoded;
  - each file's heights lie in its pinned range;
  - the interpreter matches the pins (round 45).
- **Interpreter (pinned):** spot `ph6c` environment, with Python 3.12.15, numpy 2.5.3, scipy 1.18.1 and mpmath 1.4.1.
  The dry run ran under it.
- **Environment incident:** P6's first bins-check run segfaulted inside char's Python 3.14.4
  (`../ph2/PH2_DECISIONS_2026-10-07.md`, round 45 log). Rerun alone, it was clean and bit-exact. Neither the dry run nor
  the read uses that interpreter.
- **External timestamp gate (round 47):** `ots upgrade` completed on the pre-decode receipt.
  - It has Bitcoin attestations at blocks **971369** (2026-10-14 07:09:08 UTC; block hash
    000000000000000000012340e4b23b48d910fceea62ac9cd95421c0d2f4a2cfc), 971402 and 971415.
  - `ots verify` needs a local Bitcoin node, which is not available here. `verify_prestamp.py` makes the same
    comparison: each merkle root the receipt replays to equals that block header's merkle root on blockstream.info and
    on mempool.space (`timestamps/ROUTE_A_PRESTAMP_VERIFY.json`). The seal builder requires this and records the blocks.
- **The seal's own timestamp:** the seal gets its own OpenTimestamps receipt before the decode. A stamp bounds when the
  seal existed. It cannot show that data already on disk was not looked at; that rests on the audit above and the
  md5-before-decode checks.
