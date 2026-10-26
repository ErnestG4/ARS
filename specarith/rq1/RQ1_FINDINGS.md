# RQ1 findings: the sealed read (reading B, ℤ[√2] against ℤ[i] prime angles at matched N)

**Result: B2 PASS.** T = 7.443 > t = 5.238 and the guard holds. The rule, the cells and t are as sealed (`RQ1_SEAL.md`, tag
`rq1-seal`). The double read is byte-identical. Everything below the B2 line is descriptive; anything computed after the
read is labelled post-hoc.

## 1. Provenance and order (all UTC, 2026-10-26)

| Step | Time | Record |
|---|---|---|
| Seal approved (round 91, with its edits) | — | d9777e5c; annotated tag `rq1-seal` (object 3f717aa2) |
| OpenTimestamps stamp of the stamp manifest | 16:50:05 | 1d0d56e6, `timestamps/RQ1_SEAL_STAMP_2026-10-26.txt(.ots)` |
| Bitcoin block containing the attestation | 16:56:10 | block 973261 |
| Tag seen on GitHub (Will pushed) | 17:49:27 | `timestamps/RQ1_SEAL_REMOTE_TAG.json` |
| Receipt upgraded; attestation verified on blockstream.info and mempool.space | 18:35:25 | ce029309 (committed 18:35:38), `timestamps/RQ1_SEAL_STAMP_2026-10-26_VERIFY.json`, all six checks true |
| Pre-read checks started on spot | 18:35:45 | `results/read/pins_check.txt`, `segments_check.txt` |
| read1 started | 18:38:43 | `results/read/read1.log` |
| read2 started | 19:13:07 | `results/read/read2.log` |
| Both done, `cmp` | 19:48:11 | `results/read/cmp.txt` |

- No statistic was computed from either archive before 18:35:45. The `rq1 sealed read: pre-read checks` entry at 16:52 in
  spot's `~/claude-work.log` is the launcher's dry run: fake two-segment archives built from primes below 2·10⁶ in a
  scratch directory (e810342d), since removed.
- **Pre-read checks:** all 8 entries of `read_pins.sha256` matched, and all 2,010 segment files of both archives
  matched their manifest hashes. Not VOID (hash).
- **Double read:** two separate processes, each under a 40 GB cap, single-threaded, conda env `ph6c`. Both outputs have
  sha256 ed5cd333be7445fad48439799f138c520bf44372b29d4a4f2ad63d58c3949317; `cmp` exit 0.
- **Cost:** read1 2,064 s and read2 2,104 s wall, against the 83 min (≈ 1.4 spot core-h) modelled per read (0.41–0.42×).
  The first-X rule held: the 10¹⁰ rows came after 210 s, against a 622 s limit.

## 2. B2 (the sealed criterion)

| Cell | K | R_ℤ[√2] | R_ℤ[i] | D | SE_diff | D / SE (term of T) | Guard (D ≥ −2 SE) |
|---|---|---|---|---|---|---|---|
| 10¹⁰, β 0.40 | 2,906 | 0.58162 | 0.54293 | +0.03869 | 0.02636 | +1.47 | holds |
| 10¹⁰, β 0.45 | 7,873 | 0.67519 | 0.62786 | +0.04733 | 0.01856 | +2.55 | holds |
| 10¹¹, β 0.40 | 7,013 | 0.58365 | 0.56117 | +0.02248 | 0.01727 | +1.30 | holds |
| 10¹¹, β 0.45 | 21,213 | 0.68126 | 0.65664 | +0.02462 | 0.01160 | +2.12 | holds |

- **T = 7.443 > t = 5.238** (t = 2 × the uncentred SD of T over the 100 round-88 null replicates, frozen in
  `witness/SELECTION.json`). The guard holds at every cell. **B2: PASS.** All four D are positive.
- The rule was confirmed beforehand on fresh synthetic replicates: null false PASS 2/100, planted PASS 96/100
  (`results/r90/confirm/CONFIRM.json`).
- **Attribution (sealed, rounds 88 and 91).** PASS supports the heuristic's field dependence through the conductor
  constant, and its direction: ℤ[√2] above ℤ[i] at matched N in the rigidity regime. The SE model is calibrated on
  synthetic mirror-symmetric sets (c = 0.627, the Poisson minimum; CUE-like sets give 2.6–5.0). Its validity for the
  arithmetic data is assumed, not tested. A PASS is conditional on it.
- **Post-hoc, descriptive:** no T among the 200 synthetic null replicates (selection and confirmation) reaches 7.443;
  their maximum is 5.706.

## 3. Descriptive: D(β) at every β, and the magnitudes (no verdict)

Figure: `results/read/D_beta.png` (`rq1_plot_read.py`), D(β) with ±2 SE_diff and the heuristic offsets from
`results/HEURISTIC_B_MIRROR.json` overlaid.

| β | 10¹⁰: D | D/SE | heuristic offset (log X / log N) | 10¹¹: D | D/SE | heuristic offset (log X / log N) |
|---|---|---|---|---|---|---|
| 0.20 | +0.0462 | +0.57 | 0.079 / 0.091 | +0.0905 | +1.41 | 0.072 / 0.082 |
| 0.30 | +0.0285 | +0.60 | 0.080 / 0.091 | +0.0753 | +2.07 | 0.073 / 0.083 |
| 0.40 | +0.0387 | +1.47 | 0.079 / 0.085 | +0.0225 | +1.30 | 0.072 / 0.077 |
| 0.45 | +0.0473 | +2.55 | 0.076 / 0.065 | +0.0246 | +2.12 | 0.070 / 0.062 |
| 0.50 | +0.0564 | +4.43 | 0.069 / 0.029 | +0.0399 | +5.27 | 0.064 / 0.026 |
| 0.55 | +0.0761 | +8.74 | 0.041 / 0.011 | +0.0640 | +13.14 | 0.035 / 0.009 |
| 0.60 | +0.0374 | +6.70 | 0.017 / 0.004 | +0.0299 | +10.16 | 0.013 / 0.003 |
| 0.70 | +0.0017 | +0.79 | 0.002 / 0.001 | +0.0008 | +0.77 | 0.001 / 0.000 |
| 0.80 | −0.0008 | −1.02 | 0.000 / 0.000 | +0.0001 | +0.29 | 0.000 / 0.000 |
| 0.90 | −0.0010 | −3.40 | 0.000 / 0.000 | −0.0003 | −3.01 | 0.000 / 0.000 |

- **Size at the gated cells.** D is 0.46–0.73 of the heuristic offset at 10¹⁰, and 0.29–0.40 at 10¹¹. The heuristic
  offset falls by about 9% from 10¹⁰ to 10¹¹ (∝ 1/L); the gated D fall by 42–48%. So the direction matches, but the
  size is below the heuristic and falls faster with X at these cells. The seal reports the size and does not gate it
  (§5). Two X are too few to say how the size scales.
- **The difference persists past the heuristic's crossover.** D peaks at β = 0.55 (+0.076 and +0.064, D/SE 8.7 and
  13.1), where the heuristic offset has mostly saturated away (0.009–0.041). The data's crossover sits later than the
  heuristic's, as the Step 1 ℤ[i] data at 10⁸ already showed. This is why B1 was dropped as a gate (round 87).
- **Levels.** Both fields saturate near R ≈ 0.896 (10¹⁰) and 0.908 (10¹¹) at β ≥ 0.70, not at the heuristic's 1. The
  ℤ[i] data at 10⁸ (Step 1) were 0.88–0.92 there. The absolute levels in the rigidity regime are well below the
  heuristic's (e.g. 0.54–0.58 against 0.69–0.88 at β = 0.40), as the §5 caveat expected; the offset is a difference,
  and a common level error cancels to first order.
- **β = 0.90 (not gated).** D is −0.0010 and −0.0003, at −3.4 and −3.0 SE. There, N/K is only 7.3 and 9.2 points per
  window, far from where the SE model was calibrated, so these SE are not trusted and the values are not interpreted.
- **β ≤ 0.30 (UNPOWERED, reported).** D is positive at both X but within 2.1 SE.

## 4. What this does not show

- Nothing about the leading order (§4 of the seal); the reading is about the conductor-constant offset at these X.
- Not the heuristic's size: at the gated cells the measured D is 0.3–0.7 of it.
- The PASS rests on the SE model holding for arithmetic data (round 91 attribution), which was assumed, not tested.
- X = 10¹² stays unseen (reserved for a possible option (C) prediction).

## 5. Files

- `results/read/`: read1.json and read2.json (identical), logs, pins_check.txt, segments_check.txt, first_wave.txt,
  timing.txt, cmp.txt, D_beta.png.
- Seal and pins: `RQ1_SEAL.md` at tag `rq1-seal`, `read_pins.sha256`, `archive_segments.sha256`; stamp, receipt,
  verification and remote-tag record in `timestamps/`.
