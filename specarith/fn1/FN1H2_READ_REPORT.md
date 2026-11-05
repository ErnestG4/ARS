# FN1-h2 read report: conductor or L-value, using the class-number-2 fields

**Sealed by** `FN1H2_SEAL.md` (SEALED 2026-11-04; tag `fn1h2-seal`, object afb0cda1 on 8bd42211).

**Read:** 2026-11-04 (PST) on spot, through the shared pueue queue. Sealed `fn1h2_read.py` sha256 36fdc6d3…, pins
`fn1h2_pins.json` e591fc3f….

**Remote tag:** Will pushed `fn1h2-seal`. `git ls-remote` at 23:37 UTC 2026-11-04 showed `refs/tags/fn1h2-seal` =
afb0cda1f5ed8d2ca05bfecf226c7ab7fdd14bf1 (peeled 8bd42211…), identical to the local tag, before the attestation and
before any read.

**Bitcoin attestation:** verified on two explorers, blockstream.info and mempool.space. Earliest block **974604**
(2026-11-05 00:40:51 UTC); also 974606 (00:50:33 UTC). Both merkle roots match the block headers on both explorers,
before any read.

**Double-read cmp:** **byte-identical** (cmp 0). READ1.json = READ2.json, sha256
4ab297584208ea5084718c9f99e25421aaece688d526a621b3029360e033fa71, on spot and again here.

**Status:** for Will's review. Nothing below §1 changes the verdict.

## 0. Protocol

| Step | Record |
|---|---|
| Seal | 8bd42211 "FN1-h2 SEALED 2026-11-04"; annotated tag `fn1h2-seal` (object afb0cda1); pushed by Will, remote confirmed identical 23:37 UTC |
| Stamp | OTS 2026-11-04 23:24 UTC, four calendars; manifest of 53 paths at the tag, sha256 6cb94948… (commit 52f90803) |
| Bitcoin attestation | blocks 974604 and 974606; both merkle roots match the block headers on blockstream.info and mempool.space (`timestamps/FN1H2_SEAL_STAMP_2026-11-04_VERIFY.json`, commit f44d07c6). All six verifier checks hold. |
| Launch guards (`run_fn1h2_read_one.sh`) | Before each read: the attestation record has every check true and both attestations verified; the pins file's sha256 is e591fc3f…; every code file's sha256 equals the pins file's code block; mount present; MemAvailable 103 GB (read 1) and 106 GB (read 2), against the 30 GB floor; the output did not exist |
| Inside the read | manifest pins, refs pin, (★) predictions pin and controls pin checked; the recomputed h = 1 references equal the committed D2 (b) file (`results/h2/FN1H2_REFS.json`, c0ee6cb5) exactly. Any mismatch raises; none did. |
| Double read | pueue group `specarith-scored`, sequential: task 2224 (17:36:25 → 19:17:00 PST), task 2225 (19:17:00 → 20:23:22), both rc 0 |
| cmp | **0** (task 2226): `READ1.json` and `READ2.json` byte-identical (sha256 4ab29758…), on spot and again after copying here |
| Verdicts | viewed only after the cmp |
| VOID conditions | none: reference slope b = 0.0561 > 0; no pin mismatch; cmp 0 |

Outputs: `results/h2/read/` (both reads, timing sidecars, logs, status, cmp, queue ids). Record checker:
`verify_fn1h2_read.py`. It recomputes the reference line, s and the verdict from the record's R values in plain Python
with the sealed constants restated, and checks the references against the committed file.

## 1. Verdict (as sealed, §4)

| Test | Statistic | Cuts | Verdict |
|---|---|---|---|
| **Primary**, β 0.55, the nine primary h = 2 fields against the h = 1 line | s = **−0.393** (line a = 0.6253, b = 0.0561) | CONDUCTOR iff s > −0.5545; L-VALUE iff s < −0.8318 | **CONDUCTOR** |

- Conductor predicts s = 0 and L-value predicts s = −log 4 = −1.386. The observed s is 0.162 above the CONDUCTOR cut
  and 0.993 above the L-value prediction.
- The sealed simulation (§5) gives the straight-line primary a bias under the curved truth the references show:
  −0.036 under conductor, −0.244 under L-value. So the expected ŝ is −0.04 under conductor and −1.63 under L-value.

**Attribution, as sealed (§9).**
- **CONDUCTOR:** at matched X and K, the h = 2 principal-prime sets sit on the h = 1 curve. R follows the analytic
  conductor |D|(w/2)², not L(1, χ_D), which differs from it by log 4 at these fields. This holds within the order kept
  (Rudnick–Waxman's leading form plus the conductor constant).
- **It rests on "runs in X"** (§2), which rests on two heuristics: Rudnick–Waxman's RMT form, and Rudnick–Sarnak
  independence for the cross term. Neither is proved.
  - If the term ran in N instead, a true conductor effect would sit at s ≈ +0.66 and still read CONDUCTOR.
  - A true L-value effect under "runs in N" would read CONDUCTOR 24% of the time under a straight-line truth, and
    0.003 under the curved truth the references show (§5, seal addition (b)). That 0.003 is a compensation from the
    line's curvature bias, not robustness.
- The straight-line primary's bias under curved truth is −0.036 (conductor) and −0.244 (L-value) (seal addition (a)).
- K0, the quadratic sensitivity check, K2, the descriptive nine, the χ′ control, matched N and the controls carry no
  conclusion (§2 below).

## 2. Reported, descriptive (as sealed, §4, §6, §7; no verdict)

**Quadratic sensitivity check (§4).** s against the frozen h = 1 quadratic: **−0.280** (not at the grid edge; SSE
0.00439). Under the primary cuts it would read CONDUCTOR. It carries no verdict.

**Matched-N reference (§6).** Each h = 1 field cut to its first n̄ = 220,546,415 rows. Line a = 0.6755, b = 0.0451.
s = **−0.553**, against the sealed prediction ≈ −0.55 under conductor and "runs in X".

**K0 (§7).** The OLS quadratic over the nine primary (C, R) pairs: ĉ₂,h2 = 0.0117 (SE 0.0069), against the h = 1
references' c₂ = 0.0272. t = 1.71, beside the one-sided 5% point 1.943. Descriptive only, by Will's ruling.

**Other β (§6).** s = +5.75 at β 0.45 and +6.89 at β 0.40. The h = 1 reference slopes there are small (b = 0.0122
and 0.0112, against 0.0561 at β 0.55), so s in units of b is large. In R units the primary nine sit +0.070 and
+0.077 above the h = 1 line. Neither hypothesis predicts this (§3 (b)).

**Per field, β 0.55.** C = log|D|. Drift is the total relative change in R across eight prime-order segments.

| Field | Set | C | R 0.55 | R 0.45 | R 0.40 | s_j | Drift | Detrended relSD |
|---|---|---|---|---|---|---|---|---|
| −15 | descriptive (K2) | 2.708 | 0.8240 | 0.6821 | 0.6100 | **+0.830** | −0.152 | 0.0158 |
| −20 | descriptive | 2.996 | 0.8084 | 0.6907 | 0.6294 | +0.265 | −0.122 | 0.0100 |
| −24 | descriptive | 3.178 | 0.7944 | 0.7008 | 0.6154 | −0.167 | −0.109 | 0.0070 |
| −35 | primary | 3.555 | 0.8163 | 0.6934 | 0.6141 | −0.154 | −0.122 | 0.0139 |
| −40 | primary | 3.689 | 0.8206 | 0.6978 | 0.6192 | −0.212 | −0.089 | 0.0041 |
| −51 | primary | 3.932 | 0.8226 | 0.6904 | 0.6086 | −0.419 | −0.109 | 0.0063 |
| −52 | primary | 3.951 | 0.8271 | 0.6730 | 0.6002 | −0.357 | −0.084 | 0.0128 |
| −88 | primary | 4.477 | 0.8562 | 0.7004 | 0.6223 | −0.365 | −0.129 | 0.0040 |
| −91 | primary | 4.511 | 0.8485 | 0.7050 | 0.6407 | −0.536 | −0.099 | 0.0077 |
| −115 | primary | 4.745 | 0.8635 | 0.7056 | 0.6209 | −0.503 | −0.113 | 0.0099 |
| −123 | primary | 4.812 | 0.8692 | 0.6964 | 0.6085 | −0.469 | −0.098 | 0.0090 |
| −148 | primary | 4.997 | 0.8766 | 0.7147 | 0.6213 | −0.521 | −0.114 | 0.0113 |
| −187 | descriptive | 5.231 | 0.9061 | 0.7182 | 0.5997 | −0.230 | −0.130 | 0.0189 |
| −232 | descriptive | 5.447 | 0.8923 | 0.7896 | 0.6548 | −0.692 | −0.134 | 0.0101 |
| −235 | descriptive | 5.460 | 0.9255 | 0.7448 | 0.6587 | −0.113 | −0.151 | 0.0206 |
| −267 | descriptive | 5.587 | 0.9213 | 0.7820 | 0.6389 | −0.315 | −0.137 | 0.0195 |
| −403 | descriptive | 5.999 | 1.0075 | 0.7846 | 0.6889 | +0.808 | −0.284 | 0.0281 |
| −427 | descriptive | 6.057 | 1.0162 | 0.8076 | 0.6925 | +0.905 | −0.297 | 0.0315 |

- **Means of s_j:** primary nine −0.393 (the primary s); all 18 −0.125; descriptive nine +0.144. The descriptive nine
  lie outside the h = 1 C range [1.95, 5.09], so that mean is an extrapolation (flagged, as sealed).
- **K2:** −15's s_j = +0.830.
- **Within-field drift:** R falls along prime order in all 18 sets: −0.084 to −0.129 in the primary nine, and −0.109
  to −0.297 in the descriptive nine (−403 and −427 the largest). Stages 1 and 2 also showed drift in all nine h = 1
  fields.

**Spearman ρ of R_h2 on C over the 18 (β 0.55):** ρ = 0.961; seeded permutation p (one-sided) < 5·10⁻⁶ (0 of
200,000).

**Controls (Will; §6).** Pearson r of s_j with each control constant (β 0.55).

| Control | Primary nine: r | Exact 9! p (two-sided) | All 18: r |
|---|---|---|---|
| L′/L(1, χ_D) | −0.598 | 0.086 | +0.252 |
| Chen's L-term −2·L′/L(2, χ_D) | +0.879 | 0.0020 | +0.111 |

Across the primary nine, Chen's term is almost a linear function of C (§3 (d)), so this r is not separable from the
C-trend of s_j.

**χ′ control (D5; D′ = 5).** Each h = 1 reference restricted to (5/p) = +1 (about half the rows, n ≈ 2.205·10⁸).
ΔR = R_thin − R_ref, beside (★)'s committed values under "runs in X" and "runs in N".

| Field | β 0.55: ΔR / X / N | β 0.45: ΔR / X / N | β 0.40: ΔR / X / N |
|---|---|---|---|
| −7 | +0.054 / +0.046 / +0.062 | +0.116 / +0.065 / +0.088 | +0.119 / +0.067 / +0.088 |
| −8 | +0.053 / +0.044 / +0.060 | +0.084 / +0.065 / +0.088 | +0.089 / +0.067 / +0.089 |
| −11 | +0.078 / +0.040 / +0.055 | +0.134 / +0.065 / +0.088 | +0.116 / +0.067 / +0.089 |
| ℤ[i] | +0.062 / +0.035 / +0.049 | +0.096 / +0.064 / +0.088 | +0.088 / +0.066 / +0.089 |
| −19 | +0.082 / +0.033 / +0.046 | +0.104 / +0.064 / +0.087 | +0.093 / +0.066 / +0.089 |
| ℤ[ω] | +0.052 / +0.029 / +0.040 | +0.109 / +0.063 / +0.086 | +0.117 / +0.066 / +0.089 |
| −43 | +0.033 / +0.024 / +0.033 | +0.102 / +0.062 / +0.084 | +0.107 / +0.066 / +0.088 |
| −67 | +0.005 / +0.019 / +0.027 | +0.136 / +0.060 / +0.081 | +0.119 / +0.065 / +0.088 |
| −163 | −0.074 / +0.013 / +0.018 | +0.216 / +0.054 / +0.072 | +0.181 / +0.063 / +0.087 |

## 3. Post hoc (written after the verdict was viewed; labelled; no verdict changed)

Script `lead/fn1h2_read_posthoc.py`, output `lead/FN1H2_READ_POSTHOC.json` (sha256 0ecfbec2…). Arithmetic on
READ1.json and the pinned simulation only; no data read.

**(a) Where s sits against the four sealed-simulation scenarios** (curved truth, σ_μ 0.0213; robust SD of ŝ).

| Scenario | Median ŝ | SD | Observed s in SDs from it |
|---|---|---|---|
| Conductor, runs in X | −0.036 | 0.237 | −1.5 |
| L-value, runs in X | −1.630 | 0.198 | +6.3 |
| Conductor, runs in N | +1.382 | 0.388 | −4.6 |
| L-value, runs in N | −1.110 | 0.187 | +3.8 |

- Only conductor / runs in X is within 2 SD.
- The matched-N s (−0.553) also sits at that scenario's sealed prediction (≈ −0.55).
- Both use the parametric noise model of §5 and are descriptive.

**(b) β 0.45 and 0.40: the half-size sets sit above (★).**

| β | Primary nine minus the h = 1 line (R) | Minus the matched-N line (R) | Mean R: h = 1 full / matched N / h = 2 primary |
|---|---|---|---|
| 0.55 | −0.022 | −0.025 | 0.803 / 0.818 / 0.845 |
| 0.45 | +0.070 | +0.044 | 0.614 / 0.637 / 0.697 |
| 0.40 | +0.077 | +0.050 | 0.528 / 0.552 / 0.617 |

- Truncating the h = 1 sets by prime cutoff to the h = 2 size (matched N) raises mean R by about +0.02 to +0.03 at
  every β.
- Halving them by a character (the χ′ control) raises it far more at β 0.45 and 0.40: mean ΔR +0.122 and +0.114,
  against (★)'s +0.062 / +0.085 (β 0.45) and +0.066 / +0.088 (β 0.40) under X / N. 8 of 9 fields are above both
  predictions at each of these β.
- The h = 2 principal sets are a character projection too, and they sit +0.07 to +0.08 above the h = 1 line at those
  β.
- So at β 0.45 and 0.40, projecting by a character raises R by more than (★) gives under either "runs in X" or "runs
  in N". (★)'s order does not contain this. Its mechanism is not known here.
- §2 states that the principal projection leaves E[R] unchanged at the order kept. The sealed attribution for CONDUCTOR
  is scoped to that order and to β 0.55. At β 0.55 the h = 2 offset is −0.022 in R. This is offered as a lead, for
  Will.

**(c) The χ′ control at β 0.55 does not separate X from N cleanly.**
- Mean measured ΔR is +0.038, between (★)'s X (+0.031) and N (+0.044).
- Field by field, 2 of 9 are nearer X, 4 are above both and 2 below both.
- Without −163 (ΔR −0.074, the only negative), the mean is +0.052, above both.
- So the read's own descriptive check of X against N (seal §9) does not favour X at β 0.55. (a) does: the primary and
  the matched-N s together fit conductor / runs in X and none of the other three scenarios. These two descriptive
  readings point in different directions.

**(d) The controls and C.** Over the primary nine:
- Chen's L-term correlates with C at r = −0.985, and L′/L(1) at r = +0.854;
- s_j correlates with C at r = −0.866: s_j falls from −0.15 (−35) to −0.52 (−148), i.e. the h = 2 R rise with C more
  slowly than the h = 1 line;
- so the control correlations of §2 (+0.879, −0.598) are the C-trend of s_j seen through near-functions of C, and
  can't be separated from it on these nine fields.

## 4. Cost

| Item | Model | Measured |
|---|---|---|
| Sealed double read (references, 18 h = 2 sets, χ′ control, matched N; ×2) | ≈ 3 core-h | 9,178 CPU-s = **2.55 core-h** (0.85×): read 1 5,361 CPU-s (6,033 s wall), read 2 3,817 CPU-s (3,980 s wall) |

## 5. Files

- `results/h2/read/`: READ1.json, READ2.json (sha256 4ab29758…), timing sidecars, read logs, status.txt, cmp.txt
  (empty), ids.txt (pueue 2224 / 2225 / 2226).
- `verify_fn1h2_read.py`: the record checker.
- `lead/fn1h2_read_posthoc.py`, `lead/FN1H2_READ_POSTHOC.json`: §3, post hoc.
- `timestamps/FN1H2_SEAL_STAMP_2026-11-04.txt.ots` (attested) and `_VERIFY.json`.
