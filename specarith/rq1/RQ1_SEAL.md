# RQ1 reading seal — STATUS: FINAL DRAFT for Will's approval (rounds 85–87). Not sealed; no OpenTimestamps receipt; nothing read

**Step 3 runs only after:** Will approves this seal, its OTS receipt is Bitcoin-attested and verified on two explorers,
the environment is pinned, and the double read is in place.

**Archives.** The reduced generators, one per split prime, from `rq1_archive.py`: ℤ[√2] to 10¹¹ and ℤ[i] to
1.01·10¹¹.
- Their hashes are in §6: for each, the sha256 over the segment hashes, plus per-segment hashes in `MANIFEST.json`.
- No statistic of the angles has been computed from either.

## 1. Statistic
R(β, X) = Var(N_{K,X}) / (N/K):
- **Var:** RW's eq. 1.2 (window-centre average over θ ∈ [0, 1), window 1/K), computed exactly (`rq1_angles.var_exact`).
- **N:** the number of prime ideals above split p with N𝔭 ≤ X (both ideals: θ and 1 − θ). Inert primes and 2 are
  excluded; RW's N would include them, which differs by ≤ √X points at θ = 0.
- **K = round(N^β).**

## 2. X values and K grid
- **X:** 10¹⁰ (N ≈ 4.6·10⁸) and 10¹¹ (N ≈ 4.1·10⁹), both from the one archive.
- **β grid:** {0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90}, the same at both X.

## 3. Prediction (Step 0 §3)
- **Leading order, at the level of RW's heuristic:** R → min(1, 2β).
- **Lower-order terms are not derived.**
- **A heuristic next-order statement** (not a derivation):
  - With log q(λ^k) = 2 log k + C_F, the field enters only through C_F: C_ℤ[√2] = log(8π²/log²ε) = 4.62 and
    C_ℤ[i] = log 16 = 2.77.
  - So at matched N and β, ℤ[√2] should sit above ℤ[i] in the rigidity regime by roughly
    (C_ℤ[√2] − C_ℤ[i])/log N ≈ 1.85/log N (≈ 0.09 at X = 10¹⁰).
  - The difference should vanish in the saturation regime.

## 4. Why a direct test against min(1, 2β) is not proposed
- **The finite-X correction is not small.** On ℤ[i], descriptively and unsealed (Step 1, G3), the same statistic at
  x = 10⁸ is 0.24 at β = 0.3 (prediction 0.60), 0.61 at β = 0.5 (1.0) and 0.92 at β = 0.8 (1.0). At x = 10⁷ it is
  lower still.
- **Scaled to X = 10¹⁰–10¹¹** by 1/log X, the deviation near β = ½ is still tens of percent.
- **So the direct test would fail on the known finite-X effect,** not on anything about ℤ[√2]. A tolerance wide
  enough to pass it would make it uninformative.

## 5. Reading (B), as amended in round 86 (options A and C are not chosen; C may use the reserved X = 10¹²)
**Matching variable.** N is the number of prime ideals above split primes.
- ℤ[i]: both ideals above each p ≡ 1 mod 4; inert primes and (1 + i) excluded.
- ℤ[√2]: both ideals above each p ≡ ±1 mod 8; inert primes and 2 excluded.
- At each ℤ[√2] X (10¹⁰, 10¹¹), with n = the number of ℤ[√2] split primes ≤ X (manifest row count), the ℤ[i] set is
  its first n split primes in increasing order, both ideals each. N = 2n is then exactly equal for both fields, and
  K = round(N^β) is identical. This is what `rq1_read.py` does.
  - The cut is taken from the manifests' row counts; no angle is read to choose it.
  - It falls just above X: the n-th ℤ[i] split prime lies in (10¹⁰, 1.01·10¹⁰] (n = 227,524,967; 227,523,275 ℤ[i]
    split primes are ≤ 10¹⁰) and in (10¹¹, 1.001·10¹¹] (n = 2,059,026,114; 2,059,020,280 are ≤ 10¹¹).
  - (Corrected before sealing: the earlier wording "smallest X_i with N_ℤ[i](X_i) ≥ N_ℤ[√2](X)" did not match the
    code, which matches N exactly.)

**Heuristic, derived (`rq1_heuristic.py` → `results/HEURISTIC_B.json`; no archive data used).**
- **The formula:** R_F(K, X) = K·Σ_{k≠0} sin²(πk/K)/(πk)²·min(1, (2 log|k| + C_F)/L). That is RW's §5 form, with the
  field entering only through the conductor constant, C_ℤ[√2] = 4.6214 and C_ℤ[i] = 2.7726.
- **The offset** is R_ℤ[√2] − R_ℤ[i], with L = log X, or log N as a variant:

| β | 10¹⁰: offset (L = log X / log N) | SE_diff | offset/SE | 10¹¹: offset | SE_diff | offset/SE |
|---|---|---|---|---|---|---|
| 0.20 | +0.079 / +0.091 | 0.089 | 0.9 (unpowered) | +0.072 / +0.082 | 0.071 | 1.0 (unpowered) |
| 0.30 | +0.080 / +0.091 | 0.047 | 1.7 (unpowered) | +0.073 / +0.083 | 0.034 | 2.1 |
| 0.40 | +0.079 / +0.085 | 0.023 | 3.4 | +0.072 / +0.077 | 0.015 | 4.9 |
| 0.45 | +0.076 / +0.065 | 0.015 | 4.2 | +0.070 / +0.062 | 0.009 | 6.5 |
| 0.60 | +0.016 / +0.004 | 0.004 | 1.0 | +0.013 / +0.003 | 0.002 | 1.4 |
| 0.70 | +0.002 / +0.001 | 0.002 | 0.4 | +0.001 / +0.000 | 0.001 | 0.4 |
| ≥ 0.80 | 0.000 | ≤ 0.001 | — | 0.000 | ≤ 0.001 | — |

- **SE model:** relative SD of the estimator = sqrt(2/(cK)), with c = 1.4. That is the smallest c in a Monte Carlo
  calibration (Poisson 1.4–1.8, CUE 6–10), so the SE is conservative for rigid data.
- **The offset sits at ≈ ΔC/L = 1.85/log X** in the rigidity regime (+0.08 at 10¹⁰, +0.07–0.08 at 10¹¹), as round 86
  expected.

**A caveat on the heuristic, from the ℤ[i] data at x = 10⁸ (descriptive; Step 1, G3).**
- Its absolute level overshoots: 0.50 against 0.243 measured at β = 0.30, 0.83 against 0.607 at 0.50, and 0.98 against
  0.878 at 0.66.
- Its saturation sets in too early, as the missing lower-order terms of Chen et al. (the −K_Φ term below the crossover)
  would imply.
- **The offset is a difference, so a common level error cancels to first order. The size of the offset is reported,
  not gated.**

**B2 (sign; the pass criterion).**
- R_ℤ[√2] − R_ℤ[i] > 0 at β ∈ {0.40, 0.45} at both X, and at β = 0.30 at X = 10¹¹. These are the β where the heuristic
  offset is ≥ 2·SE_diff (power ≥ 0.977 if the true offset equals the heuristic).
- **β = 0.20 (both X) and β = 0.30 at 10¹⁰ are marked UNPOWERED:** reported, not gated.
- The magnitude is reported against 1.85/log X and 1.85/log N at every β.

**B1: dropped as a gate (round 87, option (iii)). Reported descriptively as D(β).**
- **Why:** the heuristic's saturation timing is contradicted by our own ℤ[i] data at 10⁸, which is still unsaturated
  (0.88–0.92) at β = 0.66–0.80 where the heuristic has saturated. A B1 FAIL therefore could not be attributed: it might
  be a ℤ[√2]–ℤ[i] difference, or only the heuristic's crossover.
- **What is reported:** D(β) = R_ℤ[√2] − R_ℤ[i] at matched N, at every β on the grid and at both X, with SE_diff. It
  is plotted with the heuristic's ΔC/L curves (L = log X and L = log N) overlaid, from `results/HEURISTIC_B.json`.
  No verdict.

**Reading.** PASS iff B2 holds at every gated (β, X): R_ℤ[√2] − R_ℤ[i] > 0 at β = 0.40 and 0.45 at X = 10¹⁰ and
10¹¹, and at β = 0.30 at 10¹¹. FAIL iff any gated difference is ≤ 0. The X-dependence of R and of D is reported, not
gated.

**Witness for B2 (run on the archives' sizes, not their angles).**
- Two independent uniform i.i.d. angle sets at each matched N go through the identical pipeline and B2 rule, 20
  seeded replicates.
- Under no true offset, each gated sign is a fair coin, so the full B2 rule (all 5 gated cells positive) reads PASS
  with probability 1/32 per replicate. The witness passes iff the rule reads PASS in ≤ 5 of the 20 replicates.
- Its purpose is to show the B2 rule cannot pass on noise alone with high probability. B2's own power is the
  ≥ 2·SE_diff criterion above.

**Reserved:** X = 10¹² is unseen. It is held for a possible option (C) prediction (Chen et al.'s refined conjecture
adapted to ℤ[√2]). No statistic at 10¹².

**Order (round 87):**
1. Will approves this seal.
2. The seal file is stamped with OpenTimestamps.
3. Wait for the receipt's Bitcoin attestation, verified on two explorers.
4. Read in the pinned environment (§6), as a double read in two separate processes from a clean start. Both must
   produce byte-identical result JSONs.

**Chen et al. cross-check (`CHEN_XCHECK.md`).**
- **Secondary: PASS.** Our transcription of their Appendix A on our ℤ[i] angle set reproduces their Figure 1's 25
  points within 0.0014 (tolerance 0.01). This validates the angle set and the statistic machinery.
- **Primary (their Mathematica code): blocked; not needed** (round 87). No Wolfram activation.

## 6. Pins (Step 2 data and the read)
**ℤ[√2] archive** (spot `~/tmp/claude/specarith/rq1/archive/`; manifest copy `results/archive_zs2/MANIFEST.json`,
sha256 aa6d15fc67b262021f4ccda3dc9ebf6edf064bb84762fcf4ed46626ebc5722f1).
- **Contents:** 1,000 segments of 10⁸, 2,059,026,114 split primes below 10¹¹ (227,524,967 below 10¹⁰).
- **Integrity:** passes on every segment (the norms are exactly the split primes, in order).
- **Hash:** sha256 over the segment hashes c8433b089ebfc618a2bb725dc6a7565926167eb685c355951616db6cb030c0f0.
- **Generator:** `rq1_angles.py` @ e179155a (sha256 a30f02ea…442b) with `rq1_archive.py` @ b015d653.
  - The current `rq1_angles.py` regenerates segments 0 and 999 bit-identically.
- **No statistic computed.**

**ℤ[i] archive** (spot `~/tmp/claude/specarith/rq1/archive_zi/`, to 1.01·10¹¹; manifest copy
`results/archive_zi/MANIFEST.json`, sha256 8fd61856ea8a76c9b6fdc9f0f2e5cd6affc60d98a6ddae3e35b29d57b982d0cb).
- **Contents:** 1,010 segments of 10⁸, 2,078,758,475 split primes p ≡ 1 mod 4 below 1.01·10¹¹ (227,523,275 below
  10¹⁰). Each row is the Cornacchia pair (u, v), 0 < u < v, u² + v² = p; inert primes and (1 + i) are excluded.
- **Integrity:** passes on every segment (u² + v² is exactly the split primes, in order, with 0 < u < v).
- **Hash:** sha256 over the segment hashes a268e132e08030cb7f5fe5f223d0e7bee42959a9bbf8cc006fe1d2dfb5b72bc8
  (recomputed locally from the manifest).
- **Generator:** `rq1_angles.py` sha256 7764c23e…1a0c (the read-code pin below) with `rq1_archive.py` sha256
  eed304ce3512719eadec173cfae74aa3ece96540b150e6e8a6a17feee2cf037f (@ dde7502f), both checked identical on spot.
- **No statistic computed.**
- **Cost:** 27.9 spot core-h against 23.1 modelled (1.21×), 1 h 33 min wall at 28 processes, 16 GB.

**Read code.**
- `rq1_read.py`, sha256 ba570de90fddc813200e116bb98c50e56efa29b9e4663299258626c45a1f5e49.
- `rq1_angles.py`, sha256 7764c23ef64c1f53efb1fb12bd1152d93f8956745cf623d40af93e108e7d1a0c.
- **Estimator check:** exact streaming variance against `var_exact` to 8.0·10⁻¹³ relative (K = 2…5000), and the
  sorted-uniform generator's mean ratio 0.998 ± 0.010 against 1 − 1/64 = 0.984 (`results/READ_ESTIMATOR_CHECK.json`).
  Synthetic data only.

**Pinned environment (spot):**
- conda env `ph6c`: Python 3.12.15, numpy 2.5.3, scipy 1.18.1, numba 0.68.0 (spot; local is 0.66.0), mpmath 1.4.1;
- kernel 6.19.14-200.fc43;
- single-threaded (OMP / OPENBLAS / MKL / NUMBA_NUM_THREADS = 1).

**Double read** (two separate processes, run one after the other because each needs about 70 GB at 10¹¹):

    cd ~/tmp/claude/specarith/rq1
    env NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 ~/miniforge3/envs/ph6c/bin/python rq1_read.py archive archive_zi read1.json
    env NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 ~/miniforge3/envs/ph6c/bin/python rq1_read.py archive archive_zi read2.json
    cmp read1.json read2.json                      # must be byte-identical; otherwise the read is VOID

- **Cost by the model:** 40 estimator passes over up to 8.2·10⁹ breakpoints plus the witness (200 passes), single
  core. That is a few core-hours per read, priced at the archive class's factor once the first pass is timed.
- **The first-wave rule applies to the read:** if the first X's timing exceeds the model by more than 25%, stop and
  report.
