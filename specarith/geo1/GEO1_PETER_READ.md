# GEO1 Peter-correlation seal: read (2026-10-31)

**Verdict: PASS, primary and secondary.** The γ(r)/γ(0) ratios and the raw γ(r) on fresh traces 10⁶ < t ≤ 3·10⁶ agree
with Peter's Euler product, which has zero free parameters, at all 45 sealed statistics. No statistic was UNPOWERED.

## Order of events

| Step | When / where | Evidence |
|---|---|---|
| Seal | tag `geo1p-seal`, commit 2430bc32 | `GEO1_PETER_SEAL.md`, `results/peter/seal/SEAL_PARAMS.json` |
| Stamp | 2026-10-31 08:00 UTC | `timestamps/GEO1P_SEAL_STAMP_2026-10-31.txt` |
| Fresh run, launch 1 | 08:01 UTC | Stopped by its cost check; partial outputs unread (`GEO1_PETER_RUNLOG.md`) |
| Fresh run, launch 2 | 08:31–09:19 UTC | One logged post-seal deviation, in the launcher's cost guard and stop handling only. 200 chunks; cost checks 1.05–1.17× the 12 ms per t model; PARI 8.0 core-hours |
| Bitcoin attestation | block 973951, 08:05:44 UTC | Merkle root checked on blockstream.info and mempool.space; `verify_geo1p_stamp.py` passes every check (`..._VERIFY.json`) |
| Read | after the attestation was verified | Fresh files copied locally; all 21 sha256 match the run's `HASHES.txt` |
| Double read | two separate processes | Terminal output went to files, not the screen. `READ1.json` and `READ2.json` are byte-identical (`cmp` status 0, `results/peter/seal/read/cmp.txt`) before either verdict was looked at. Wall time is in `.timing` sidecars |

## Inputs

**Independent class-number check.** 200 of 200 sampled (t, u) match on both h and N(ε). The independent routes were
`qfbclassno` for h and the continued-fraction period parity for N(ε). Nothing is missing.

**Integrity checks.**
- Coverage is complete: t = 1,000,001 … 3,000,000, contiguous, and every g > 0.
- The development-data hash and the pool-source hash both match their pins.

**GRH.** The production class numbers (`quadclassunit`) are GRH-conditional, so this result is GRH-conditional in its
input. Peter's theorem itself is unconditional.

## Witnesses

| Witness | Required | Primary | Secondary |
|---|---|---|---|
| Shuffled t (seeded permutation of the fresh α̃) | FAIL | FAIL | FAIL |
| Matched-marginal independent-lag null | FAIL | FAIL | FAIL |
| Planted Euler-product series, against its exact values | PASS | PASS | PASS |

## Statistics

Fresh window: n ∈ [1,000,001, 2,999,880], N = 1,999,880. Full table: `results/peter/seal/read/READ1.json`.

| Statistics | Largest \|value − prediction\| | Largest \|diff\|/tolerance |
|---|---|---|
| 22 ratios γ(r)/γ(0) | 2.0·10⁻⁵ (r = 12) | 0.05 (r = 9) |
| γ(0) | 9.8·10⁻⁶ (0.328349 against 0.328358) | 0.01 |
| 22 raw γ(r) | 3.4·10⁻⁶ (r = 60) | 0.03 |

Examples:
- γ(1) is −0.148609 against −0.148608;
- γ(2) is 0.033126 against 0.033126;
- the ratio at r = 12 is 0.594242 against 0.594221;
- the ratio at r = 120 is 0.639563 against 0.639544.

The arithmetic pattern Peter's product predicts appears in full:
- odd lags are negative (a 2-adic effect);
- lags divisible by 4 are enhanced;
- odd lags are less negative the more small odd primes divide them: −0.45 at r = 1, −0.43 at 11, −0.35 at 7, −0.29
  at 5, −0.27 at 3 and −0.23 at 15;
- smooth lags (12, 36, 60, 120) give the largest ratios.

## Descriptive, after the read (not part of the verdict)

**Agreement versus the fresh window's own block-jackknife SE** (199 blocks of 10⁴):
- for γ: z RMS 0.07, largest |z| 0.16;
- for the ratios: z RMS 0.13, largest |z| 0.20.

The fresh block SEs (1.2·10⁻⁵ to 7.4·10⁻⁵ for γ) are about what the seal projected (1.2·10⁻⁵ to 8.2·10⁻⁵). The actual
deviations are about 10× smaller still.

**Probable explanation (not tested).**
- α(n) is a product of local densities that are periodic in n.
- Over a window of length N, each periodic component averages out with an error of order (its period)/N, not 1/√N.
- Block means still vary, from primes with periods longer than a block, and block jackknife treats that variation as
  independent noise.
- The development range already showed the same direction (z RMS 0.59 against block SE). Here the effect is stronger.

**Consequence for the tolerances.** The sealed tolerances, made of the trend allowance plus 3.26·SE, were 20–100× wider
than the observed deviations. The test passed with a large margin. The agreement it shows is at the level of 10⁻⁵ in
the ratios, about 3·10⁻⁵ of their size. The tolerances alone would certify only about 10⁻³.

## What this does and does not establish

**Established.** On traces not computed before the seal, the multiplicity correlations of the modular surface's length
spectrum match Peter's Euler product to about 10⁻⁵, at small-prime, prime-power, composite and smooth lags, with no
fitted parameter. This is a confirmation, at the sealed precision, of a known theorem (Peter 2002) on new data. It is not
a new mathematical result.

**Not established.**
- A rate of convergence (Peter gives none). The trend allowance was an allowance, not a measurement.
- The behaviour of the block-jackknife SE beyond this window.
- Anything unconditional on GRH about the input class numbers.
