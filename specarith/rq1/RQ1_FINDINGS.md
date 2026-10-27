# RQ1 findings: the sealed read (reading B, ℤ[√2] against ℤ[i] prime angles at matched N)

**Verdict: B2 PASS, as sealed.** T = 7.443 > t = 5.238 and the guard holds. The rule, the cells and t are as sealed
(`RQ1_SEAL.md`, tag `rq1-seal`), and the double read is byte-identical. The verdict is about **direction**: ℤ[√2] above
ℤ[i] at matched N in the rigidity regime. It is **conditional on the SE model** (round 91).

The verdict is §2 alone. §3 (size, shape and scaling against the flat-offset heuristic), §4 (open leads) and §5 (the
post-hoc conductor-scaling check, round 92) are descriptive and carry no verdict. Anything computed after the read is
labelled post-hoc.

## 0. Close-out summary (round 94; RQ1 closes here)

- **Sealed verdict: B2 PASS** (tag `rq1-seal`, OTS-stamped and Bitcoin-attested before the read; double read
  byte-identical). T = 7.443 > t = 5.238 with the guard holding: ℤ[√2] above ℤ[i] at matched N in the rigidity regime
  at 10¹⁰ and 10¹¹. **Direction only, and conditional on the SE model** (calibrated on synthetic mirror-symmetric
  sets; its validity for arithmetic data is assumed, not tested).
- **Descriptive results (no verdict):**
  - D(β) peaks at the rigidity–randomness crossover (β ≈ 0.55, D/SE 8.7 and 13.1), not in the rigidity range.
  - The conductor rescaling R_ℤ[√2](K) = R_ℤ[i](aK), a = 2.5204, is approximate in both regimes: D is 0.26–0.74 of
    the shift in the rigidity range and 1.01–1.30 of it at the crossover (residual up to +3.2 SE at 10¹¹); the
    residual changes sign at β ≈ 0.52–0.53 at both X (§5).
  - The flat-offset forms, RW-type heuristic (1.849/log X) and Chen et al.'s Conjecture 1.2 generalised (1.695/log X),
    both miss: their D is too large in the rigidity range, and above λ = ½ they have no field dependence, while the
    data show D ≈ +0.03 there. On Chen's own statistic (round 94) ℤ[i] fits the formula and ℤ[√2] does not
    (`RQ1B_STEP0.md` §6). **That is a failure of the formula as generalised here**, with two substitutions
    UNVERIFIED (L(s, χ_F) in C_Φ,L and F's inert primes in A′_Φ). It does not show that Chen et al.'s conjecture fails
    to extend to other fields.
  - The plateau at β ≥ 0.70 (§4): on Chen's statistic it matches 1 − 2/log X within 0.002; on our unweighted
    statistic it sits 0.013–0.017 lower, probably from the weighting, not checked against a formula.
- **Phase 34d's half-sample defect.** Its σ²/(N/K) values were means over 50 random half-samples, which maps a ratio r
  to ≈ (r + 1)/2. The affected verdicts (RW replicated at X = 10⁸, β = 0.65; "within 1σ of the RW asymptote";
  "rigidity regime matches RW within 1σ") are bannered in place in `PHASE34D_FINDINGS.md` (2026-10-25) as not
  established; the ARSv2 ledger note is `ARSV2_LEDGER_NOTE_34D.md` (with Will).
- **Open lead L8** (`specarith/OPEN_LEADS.md`): the field dependence of the sector variance peaks at the
  rigidity–randomness crossover, where no available formula applies.
- **Reserved:** the 10¹² archives for ℤ[√2] and ℤ[i] (and ℤ[ω], round 95), hashed and unread; they are RQ1-c's data.

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
- **Kernel:** spot's boot of 2026-10-13 16:22 to 2026-10-26 14:47 PDT ran 6.19.14-200.fc43, the pinned kernel; the
  witness, the confirmation and the read (11:38–12:48 PDT) all ran in it. Spot rebooted afterwards into 7.2.11
  (`journalctl --list-boots`); later spot runs record their kernel.

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

## 3. Descriptive, not the verdict: size, shape and scaling against the flat-offset heuristic

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
- **Levels.** The absolute levels in the rigidity regime are well below the heuristic's (e.g. 0.54–0.58 against
  0.69–0.88 at β = 0.40), as the seal's §5 caveat expected; the offset is a difference, and a common level error
  cancels to first order. The plateau at β ≥ 0.70 is an open lead (§4).
- **β ≤ 0.30 (UNPOWERED, reported).** D is positive at both X but within 2.1 SE.

## 4. Open leads and calibration limits (descriptive)

- **The plateau at β ≥ 0.70 (narrowed in the close-out).** Both fields level off near R ≈ 0.896 (10¹⁰) and 0.908
  (10¹¹) on our unweighted statistic, the same in both fields, so not a field effect. On Chen et al.'s weighted
  statistic (round 94) both fields level at 0.911 and 0.920, within 0.002 of their field-independent 1 − 2/log X
  (Δ_Φ term). Ours sits 0.013–0.017 lower, probably from the weighting; that is not checked against a formula. It is
  not an open lead of its own; L8 is the field difference peaking at the crossover.
- **Outside calibration: β = 0.90.** D is −0.0010 and −0.0003, at −3.4 and −3.0 SE. There, N/K is only 7.3 and 9.2
  points per window, far from where the SE model was calibrated (K = 20–200), so these SE are not trusted and
  the values are not interpreted. β = 0.80 (N/K 54–84) is near that edge too.

## 5. Post-hoc conductor-scaling collapse (round 92; descriptive, no verdict)

**Everything in this section is post hoc** (round 92; computed after the sealed read, on the same archives; no
verdict). `rq1_collapse.py` → `results/collapse/COLLAPSE.json`; figure `results/collapse/collapse.png`
(`rq1_plot_collapse.py`).

**The identity.** The heuristic's field dependence enters only through 2 log k + C_F, so in the continuum
R_ℤ[√2](K) = R_ℤ[i](a·K) with a = e^{ΔC/2} = π/(√2·log(1 + √2)) = 2.5204. Checked on the heuristic formula itself:
|R_ℤ[√2](K) − R_ℤ[i](aK)| ≤ 1.2·10⁻³ (at β = 0.20, from the discrete sum) and ≤ 2.3·10⁻⁵ for β ≥ 0.40, at both X and
both L, against heuristic offsets of 0.003–0.09. The collapse therefore tests the conductor-scaling structure without
the heuristic's flat-offset shape.

**The data** (β = 0.20 to 0.70 in steps of 0.01, at the read's matched N; spot, kernel 7.2.11, 3.6 core-h against 7.4
modelled). The 8 read cells at each X were reproduced bit-exactly. Residual = R_ℤ[√2](K) − R_ℤ[i](aK), in units of
its model SE. Values at neighbouring β share data and are strongly correlated, so counts of points beyond 2 SE are
not independent.

| β range | 10¹⁰: residual / SE | 10¹⁰: D / shift prediction | 10¹¹: residual / SE | 10¹¹: D / shift prediction |
|---|---|---|---|---|
| 0.20–0.34 | −1.6 to +0.3 | — (SE ≥ 0.03) | −3.5 to +0.6 | — (SE ≥ 0.02) |
| 0.35–0.50 (rigidity range; B2 cells 0.40, 0.45) | −2.1 to −1.5 | 0.40–0.74 | −4.5 to −2.0 | 0.26–0.62 |
| 0.53–0.62 (crossover) | +0.6 to +2.1 | 1.08–1.28 | +0.2 to +3.2 | 1.01–1.30 |
| 0.63–0.70 | +0.1 to +1.4 | — (D → 0) | +0.3 to +1.9 | — (D → 0) |

- **The single-parameter collapse does not hold across the range.** The residual changes sign between β = 0.52 and
  0.53 at both X.
  - In the rigidity range, ℤ[√2] sits below the shifted ℤ[i] curve. D there is a quarter to three quarters of what a
    shift of log K by log a would give. The shortfall is larger at 10¹¹ (residual −0.044 to −0.059, about −4 SE at
    β 0.40–0.45) than at 10¹⁰ (−0.020 to −0.040, about −1.6 to −2.1 SE).
  - At and past the crossover (β ≈ 0.53–0.62), the shift accounts for D within 0–30%. ℤ[√2] sits slightly above the
    shifted curve, up to +2.1 SE (10¹⁰) and +3.2 SE (10¹¹) at β ≈ 0.57.
- **Round 93 addition.** The crossover residual is up to +3.2 SE at 10¹¹ (D / shift 1.01–1.30). So the pure
  rescaling is approximate in both regimes, and the residual changes sign at β ≈ 0.52–0.53 at both X. No
  crossover-only collapse seal (round 93: it would test a model already known to be approximate).
- **First order against the full shift.** R′_ℤ[i]·log a / log N and R_ℤ[i](aK) − R_ℤ[i](K) agree closely for
  β ≥ 0.30, so the linearisation is not the issue.
- **Reading, descriptive only.** Near the crossover, the field difference behaves like a rescaling of K by the
  conductor ratio. In the rigidity range it is smaller than that, and the gap grows from 10¹⁰ to 10¹¹. Lower-order
  terms that do not enter through 2 log k + C_F are one candidate (cf. the plateau note, §4); two X cannot
  separate the possibilities. The B2 verdict (direction) is untouched: D > 0 throughout the rigidity range at both X.
- **Caveats.** The SE is the sealed model (assumed for arithmetic data, round 91); the witness found it accurate to
  conservative at 10¹¹ (empirical/model 0.83–1.04) on synthetic sets. Fine-grid β points beyond the sealed cells were
  never used for any decision.

## 6. What this does not show

- Nothing about the leading order (§4 of the seal); the reading is about the conductor-constant offset at these X.
- Not the heuristic's size: at the gated cells the measured D is 0.3–0.7 of it.
- The PASS rests on the SE model holding for arithmetic data (round 91 attribution), which was assumed, not tested.
- X = 10¹² stays unseen (reserved for a possible option (C) prediction).

## 7. Files

- `results/read/`: read1.json and read2.json (identical), logs, pins_check.txt, segments_check.txt, first_wave.txt,
  timing.txt, cmp.txt, D_beta.png.
- `results/collapse/` (post hoc, round 92): COLLAPSE.json, collapse.log, collapse.png.
- Seal and pins: `RQ1_SEAL.md` at tag `rq1-seal`, `read_pins.sha256`, `archive_segments.sha256`; stamp, receipt,
  verification and remote-tag record in `timestamps/`.
