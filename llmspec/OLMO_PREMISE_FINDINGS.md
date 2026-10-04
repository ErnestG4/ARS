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
- **T3 names the mechanism:** σ-multimodal heads are the row-norm-bimodal heads. Q raw 2×2 [[40, 23], [19, 174]],
  Fisher p = 1.4e-16; K raw [[45, 6], [40, 165]], p = 4.7e-20 (folded: 3.3e-20 / 1.4e-25). Dead-row presence
  alone does NOT predict it (Q p = 0.37, K p = 0.027). Reading: the "peaks" in the per-head singular
  spectra are row-scale structure — rows inside a head living at two norm scales — not a two-population structure of
  the query map's directions.
- **Endpoint (T4, descriptive since nothing is licensed):** ingredient 3 Q raw 0.254 / 0.129, K 0.211 / 0.102;
  ingredients 1–2 (exploratory runs) the same to ±0.01. Nothing changes through the anneal; "fades" is not on the table.

## 2. Gain column (A2, descriptive)
Q: 19.1% of heads have a multimodal gain histogram; a Gaussian folded with the head's own gains reads
multimodal in 18.8%; of the folded-multimodal heads (23.4%), 14.5% are explained by their own gain alone. K similar.

## 3. Dead rows (T5, descriptive; WD bound UNVERIFIED-config)
Q: 1936 rows (of 32 768) below 0.1 × median, median norm 0.0032 × median; **98.1% of them have a
gain entry below 0.1 × the median |gain|** (Li 2606.04405's gain ≈ 0 ⇔ dead row holds). K: 2002 rows, 99.9%. The
decoupled-WD bound over stage 1 under the assumed config (peak 4e-4, WD 0.1, cosine) is e^{−38} ≈ 3e-17 of the init
norm; the observed 3e-3 is ~14 orders above it, so these rows did NOT decay at the WD rate — either WD is not applied
to them, the config differs, or they keep receiving updates; config UNVERIFIED, no cause attributed.

## 4. What this changes
- FINDINGS_MEMO row 3: "OLMo stage-1 end: Q/K multimodality (dip, 13.3 %)" → **NOT LICENSED (row-norm confusable)**; the
  licence battery of Stage 1b did not contain the real row-norm shape, and that class fires at 8–21 %.
- STAGE1_FINDINGS row 3 / README row 3 re-worded the same way. The Stage 1b calibration (`seals/stage1b_dip_calibration.json`)
  needs the own-row-norm class added before any future dip reading (amendment for Will).
- The OLMo trajectory plan (1) loses its premise: there is no licensed multimodality to track. What remains is a
  descriptive, possibly interesting object — within-head row-norm bimodality and the gain ≈ 0 dead rows — for a
  differently designed test (row-norm structure as the primary object, not singular spectra).
- Lit v2 item 4 (dip conservativeness) is moot here: the problem was a missing confusable, not test power.

## 5. Open leads
1. A per-head gain-matched / row-norm-matched null for the dip (the head's own D_r·G as its null) — method change.
2. Row-norm bimodality itself: when in stage 1 do rows split into two scales, and is it the same rows as the gain ≈ 0 set?
3. Verify the stage-1 WD groups (q_norm gains, dead rows) against the OLMo-core config to settle T5's 14 orders.
