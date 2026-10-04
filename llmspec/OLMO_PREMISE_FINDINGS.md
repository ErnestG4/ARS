# OLMo premise check — findings (2026-10-03; OLMO_PREMISE_PREREG.md sealed 6a4b1fc with A1, A2; olmo_premise.py; results/olmo_premise.json)

Run 18:00–18:13 (CPU, streamed; 5 revisions × 16 layers × Q, K; 2000 confusable draws per class). Known answers PASS
(raw Gaussian FPR 0.000; planted two-component 1.000). Words from the sealed reading rule (§3 + A1 + A2).

## 1. Verdict: **NOT LICENSED (row-norm confusable)** — the stage-1-end Q multimodality (memo row 3) does not stand
- **T2, the confusable that fires:** Gaussian 128 × 2048 blocks whose rows are scaled by a real head's OWN row norms read
  MULTIMODAL under the dip rule in **20.7%** of draws over all levels and
  **7.8%** with the near-zero trim (licence requires ≤ 2 %). With the dead rows replaced by the
  median: 7.9% / 8.2%. Lognormal row norms: 0 / 0 (so it is the SHAPE of the real
  row-norm distribution, not heterogeneity per se). The folded (gain × W_Q) branch: 18.6% / 6.0% on
  gain-folded Gaussians (A2: not licensed; layer-0 cell 64 %).
- **Observed rates against that floor (f0 = 0.207 all levels, 0.082 trimmed):** stage-1 end Q raw
  0.246 / 0.133 (binomial p 0.073 / 0.0038), K raw 0.199 / 0.086
  (p 0.64 / 0.44). SHOWS PEAKS (≥ 0.10 and p < 1e-3) fires nowhere. Step 0: 0 / 0 (G0 PASS).
- **Descriptive remainder (Will, 10-04): "NOT LICENSED" is not "fully explained".** The trimmed Q rate,
  13.3% (34/256), still sits above the own-row-norm floor f0 = 0.082: binomial p = 0.0038, short of the sealed
  p < 1e-3 bar and of nothing else. All levels: 24.6% vs 0.207, p = 0.073. K trimmed: 8.6%, p = 0.44
  (no remainder). So directional multimodality does not stand, but a small Q excess over the row-norm null remains
  unexplained at this power; it is reported, not interpreted.
- **T3 names the mechanism:** σ-multimodal heads are the row-norm-bimodal heads. Q raw 2×2 [[40, 23], [19, 174]],
  Fisher p = 1.4e-16; K raw [[45, 6], [40, 165]], p = 4.7e-20 (folded: 3.3e-20 / 1.4e-25). Dead-row presence
  alone does NOT predict it (Q p = 0.37, K p = 0.027). Reading: the "peaks" in the per-head singular
  spectra are row-scale structure — rows inside a head living at two norm scales — not a two-population structure of
  the query map's directions.
- **Endpoint (T4, descriptive since nothing is licensed):** ingredient 3 Q raw 0.254 / 0.129, K 0.211 / 0.102;
  ingredients 1–2 (exploratory runs) the same to ±0.01. Nothing changes through the anneal; "fades" is not on the table.

## 2. Gain column (A2, descriptive)
Q: 19.1% of heads have a multimodal gain histogram; a Gaussian folded with the head's own gains reads
multimodal in 18.8%; 23.4% of heads are folded-multimodal, and 14.5% of all heads are folded-multimodal AND read multimodal
with their own gain alone — about 62% of the folded-multimodal heads. K similar.

## 3. Dead rows (T5, descriptive; WD bound UNVERIFIED-config)
Q: 1936 rows (of 32 768) below 0.1 × median, median norm 0.0032 × median; **98.1% of them have a
gain entry below 0.1 × the median |gain|** (Li 2606.04405's gain ≈ 0 ⇔ dead row holds). K: 2002 rows, 99.9%. The
decoupled-WD bound over stage 1 under the assumed config (peak 4e-4, WD 0.1, cosine) is e^{−38} ≈ 3e-17 of the init
norm. The median dead row sits at 3e-3 × its head's median row norm, but that is the median of everything below the
0.1 × median cut, not the deepest rows: only the first 400 dead rows were banked (none below 7e-3 × median), and the full
minimum was not. FINDINGS_MEMO lead 2's ~1e-28 refers to singular values of 8 RANK_COLLAPSED heads, a different quantity.
No weight-decay conclusion is drawn from T5 (config UNVERIFIED, depth distribution incomplete).

## 4. What this changes
- FINDINGS_MEMO row 3: "OLMo stage-1 end: Q/K multimodality (dip, 13.3 %)" → **NOT LICENSED (row-norm confusable)**; the
  licence battery of Stage 1b did not contain the real row-norm shape, and that class fires at 8–21 %.
- STAGE1_FINDINGS (dated correction in its Stage 1b reading), README row 3 and open lead 1, memo open lead 1 re-worded
  the same way (10-03/10-04). The Stage 1b calibration (`seals/stage1b_dip_calibration.json`)
  needs the own-row-norm class added before any future dip reading (amendment for Will).
- The OLMo trajectory plan (1) loses its premise: there is no licensed multimodality to track. What remains is a
  descriptive, possibly interesting object — within-head row-norm bimodality and the gain ≈ 0 dead rows — for a
  differently designed test (row-norm structure as the primary object, not singular spectra).
- Lit v2 item 4 (dip conservativeness) is moot here: the problem was a missing confusable, not test power.

## 4b. Mechanism hypothesis (Will, 10-04; NOT tested — the config check is pending)
In OLMo-2 the query is q = g ⊙ RMSNorm(W_Q x). A gain entry g_i ≈ 0 multiplies the direct gradient reaching row i of W_Q
by ≈ 0, so that row stops learning while decoupled weight decay keeps shrinking it; the head ends up with two row-norm
populations (live rows and decaying rows), which is exactly what the dip test read as "peaks". Consistent with T3
(σ-multimodal ⇔ row-norm-bimodal) and T5 (98 % of dead rows have g ≈ 0). Untested: whether W_Q rows are in the WD group
and q_norm gains are not, the stage-1 LR/WD schedule, and the full depth distribution of the dead rows (only 400 banked).
RMSNorm couples rows through the normaliser, so "≈ 0 gradient" is approximate; stated as a hypothesis.

## 5. Open leads
1. A per-head gain-matched / row-norm-matched null for the dip (the head's own D_r·G as its null) — method change.
2. Row-norm bimodality itself: when in stage 1 do rows split into two scales, and is it the same rows as the gain ≈ 0 set?
4. **For whoever studies QK-norm (Diffract, arXiv 2608.10850):** Diffract's multi-peak attention spectra in OLMo 2 may
   be this same QK-norm / row-scale effect rather than directional structure. Test: their per-head spectra against
   Gaussian blocks with each head's own row norms and gains (this file's T2 classes).
3. Verify the stage-1 WD groups (q_norm gains, dead rows) against the OLMo-core config, and bank the full dead-row depth distribution, before any weight-decay reading of T5.
