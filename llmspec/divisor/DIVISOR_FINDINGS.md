# Divisor Harmonics v0 — findings (2026-10-03)

Pre-registration `DIVISOR_PREREG.md` (sealed 8c28a31; A1 pre-read 0f0638f; A2 post-read code fix, no analysis change).
Brief: `briefs/DIVISOR_HARMONICS_V0.md`. Extraction `divisor_extract.py` (GPU, 08:26–08:30; manifest with sha256 in
`results/divisor/acts/manifest.jsonl`); analysis `divisor_spectrum.py` on spot (numpy; B = 4000 bootstrap draws,
10 000 item shuffles, 200 power draws per class and planted size); results `results/divisor/<tag>_last_primary.json`
(26 files, committed ddd8e23). Words are the sealed vocabulary (prereg §6 + A1). Every claim names its gate.

## 1. Verdict table (primary model pythia-1.4b, step143000, blocks 8–15 averaged, last item token, template-averaged)
Control gates (all must pass): weekdays whiteness p = 0.94 PASS; nouns cycle p = 0.98 PASS; nouns min class p = 0.25 PASS.
Holm over the 17 (concept × nontrivial class) tests, α = 0.05.

| Concept | Cycle gate (ρ₁, shuffle p) | Class d | z | one-sided p | R_d = excess / L̂ | smallest detectable f (Holm power ≥ 0.8) | Word |
|---|---|---|---|---|---|---|---|
| months | 0.26, p = 0.0001 PRESENT | 2 (n=6) | −0.8 | 0.77 | −0.31 | 0.4 | NOT RESOLVABLE |
| | | 3 (n=4; quarters bet) | +0.6 | 0.24 | +0.28 | 0.4 | NOT RESOLVABLE |
| | | 4 (n=3; quadrimesters bet) | −0.5 | 0.66 | −0.11 | 0.4 | NOT RESOLVABLE |
| | | 6 (n=2) | −0.1 | 0.50 | 0.00 | 0.8 | NOT RESOLVABLE |
| hours | 0.63, p = 0.0001 PRESENT | 2 (n=12) | +1.6 | 0.076 | +1.17 | 0.4 | NOT RESOLVABLE (not rejected) |
| | | 3 (n=8) | 0.0 | 0.41 | +0.21 | 0.2 | **H0 HOLDS** |
| | | 4 (n=6) | −0.2 | 0.49 | −0.04 | 0.2 | **H0 HOLDS** |
| | | 6 (n=4,20; shift bet) | −0.6 | 0.70 | −0.37 | 0.4 | NOT RESOLVABLE |
| | | 8 (n=3,9,15,21; shift bet) | −0.8 | 0.79 | −0.36 | 0.8 | NOT RESOLVABLE |
| | | 12 (n=2,10; am/pm bet) | −0.6 | 0.71 | −0.24 | none | NOT RESOLVABLE |
| numbers (open) | 0.50, p = 0.0001 PRESENT | **2** (n=50; bet) | **+28.5** | 0.0002 | **+9.1** | 0.02 | **H1 HOLDS** (Holm p_adj 0.004) |
| | | **4** (n=25,75) | **+12.3** | 0.0002 | **+2.8** | 0.02 | **H1 HOLDS** |
| | | **5** (n=20,40,60,80; bet) | **+40.8** | 0.0002 | **+7.2** | 0.02 | **H1 HOLDS** |
| | | **10** (n=10,30,70,90; bet) | **+9.0** | 0.0002 | **+1.7** | 0.05 | **H1 HOLDS** |
| | | 20 | −2.1 | 0.99 | −0.30 | 0.1 | H0 HOLDS (deficit, see §3) |
| | | 25 | −2.4 | 1.00 | −0.21 | 0.1 | H0 HOLDS (deficit, see §3) |
| | | 50 | +0.7 | 0.24 | +0.11 | 0.1 | H0 HOLDS |
| weekdays (prime control) | 0.14, p = 0.003 PRESENT | only d = 7 (trivial) | −0.5 | 0.83 | 0.00 | — | gate PASS (white residuals) |
| nouns (shuffled control) | −0.13, p = 0.98 NULL | 2, 3, 4, 6 | −1.2 … +0.6 | ≥ 0.25 | — | — | gate PASS (INAPPLICABLE by design) |

- **Numbers: H1 HOLDS for d = 2, 4, 5, 10.** The item-axis spectrum of 0–99 has peaks at n = 50 (period 2), 25 and 75
  (period 4), 20/40/60/80 (period 5) and 10/30/70/90 (period 10) far above the translation-symmetry baseline: P/L̂ at
  n = 40 is 11.9, at n = 50 10.1, at n = 20 6.6, at n = 10 2.4. The three declared bets (d = 2, 5, 10) all hold; d = 4 is an
  undeclared fourth class (reported, not a bet). The trivial class d = 100 also exceeds (z = +5.4; not a test).
- **Months: NOT RESOLVABLE on every class.** No class is rejected (|z| ≤ 0.8), and the instrument's smallest detectable
  excess at this geometry (k_eff = 8, N = 12) is 40 % of the Lorentzian power (80 % for d = 6, 12), so a quarterly excess
  smaller than that would not have been seen. The two bets read R = +0.28 (d = 3, rank 1 of 4) and −0.11 (d = 4).
- **Hours: H0 HOLDS for d = 3 and d = 4; NOT RESOLVABLE for the bets** (am/pm d = 12: no planted size up to 0.8 reaches
  power 0.8 — the class holds n = 2 and n = 10, whose null spread is dominated by n = 2's Lorentzian weight; shifts d = 6, 8:
  0.4 / 0.8). The one positive class is **d = 2 (n = 12, the Nyquist harmonic: hour PARITY, odd vs even hours)**, R = +1.17,
  p = 0.076, not rejected; see §2 and §4.

## 2. Replication (pythia-410m, pythia-70m, step143000; same 17 tests; gates PASS in both)
| Class | 1.4B z | 410M z | 70M z | Word |
|---|---|---|---|---|
| numbers d=2 | +28.5 | +31.5 | +26.1 | REPLICATES 2/2 |
| numbers d=4 | +12.3 | +10.6 | +3.8 (p = 0.0007) | REPLICATES 2/2 |
| numbers d=5 | +40.8 | +37.3 | +25.8 | REPLICATES 2/2 |
| numbers d=10 | +9.0 | +7.8 | +6.1 | REPLICATES 2/2 |
| hours d=2 (parity) | +1.6 (p 0.076) | +2.6 (p 0.025) | +3.0 (p 0.011) | not rejected in any model after Holm; same sign 3/3 (descriptive) |
| months, all classes | |z| ≤ 0.8 | |z| ≤ 0.7 | |z| ≤ 1.0 | NOT RESOLVABLE in all three |
The numbers deficits at d = 20, 25 (z ≈ −2) also replicate (410M −2.0/−2.0; 70M −1.9/−2.7).

## 3. What the numbers result is and is not
- It is the amplitude statement the brief asked for: the base-10 divisor classes carry an order of magnitude more power
  than translation symmetry predicts, on top of a baseline that is itself barely Lorentzian (σ̂ = 0.04 domain units ≈ two
  lattice sites; the whiteness statistic of the numbers fit reads p = 0.000 — the residuals are NOT white, which is the
  excess itself, not a pipeline fault: weekdays' residuals are white in all three models).
- The deficits at d = 20, 25 are the declared contamination signature (A1): the fit is pulled up by the peaks, so the
  classes without peaks sit below it. They are not evidence of suppression.
- Prior work (both verified from arXiv, prereg §0 and A3): Zhou, Fu, Sharan & Jia, arXiv 2406.03445 (NeurIPS 2024 per
  Will; venue UNVERIFIED on the arXiv page) find outlier Fourier components of periods 2, 2.5, 5 and 10 in pre-trained
  LLMs' number representations used for addition (GPT-2-XL and others; period 2.5 is class d = 5 on this lattice);
  Kantamneni & Tegmark, arXiv 2502.00873, report number helices with T = [2, 5, 10, 100] (GPT-J, Pythia-6.9B,
  Llama-3.1-8B). **Periods 2, 5, 10 therefore REPLICATE published findings in a new framing** (the Ramanujan–Fourier
  divisor decomposition against a translation-symmetry baseline, at 70M–1.4B). **Period 4 is the part not in those
  papers** — and the one most exposed to the frequency confound (powers of 2 in computing text).
- **Frequency (Will's review, settled 10-03):** round numbers, even numbers and powers of 2 are far commoner in text, and
  the step-256 onset is the unigram/bigram stage, so a frequency comb was the first alternative to exclude. A3 (linear /
  quadratic log-frequency residualisation, §7) changed no z but was INAPPLICABLE by its own can-fire letter; A4 v2 (a
  within-frequency-strata permutation null that carries ANY function of frequency, §7b; a confirmation run) leaves
  d = 2, 5, 10 SURVIVING in all three models and d = 4 SURVIVING at 1.4B and 410M (NOT RESOLVABLE at 70M). Frequency does
  not explain the result; period 4 stands as the new class at 410M–1.4B.
- Tokenisation is not the explanation in the simple sense: every number 0–99 is a single NeoX token (audit), so the
  periodicities are properties of the token representations, not of a digit-by-digit encoding.

## 4. Trajectory (DESCRIPTIVE; Arm B A0, AdamW 70M, 23 checkpoints; gates PASS at every step)
Source of every checkpoint: the A0 run itself — steps ≤ 3000 from the B4 bank, steps 4000–10000 from the Q4EXT extension
(`train.py A0 --stop 10000`, the SAME run resumed from its step-3000 resume.pt, Q4EXT_PREREG §1; not a different run and
not Pythia-70M's released trajectory). **Onset steps are DETECTION steps, not presence steps** (the OLMo lesson): the
instrument's smallest detectable excess at each checkpoint is in every JSON — numbers 0.02 (d = 2, 4, 5; 0.05 for d = 10
from step 1000) and hours d = 2 0.2 at all 23 checkpoints — so "first detectable at step 256" means a ≥ 2 % excess was
not there at 128 and was at 256; a smaller one could be earlier.
| step | months cycle | hours cycle | numbers cycle | numbers z (d=2 / 4 / 5 / 10) | hours d=2 z | Holm rejections |
|---|---|---|---|---|---|---|
| 0–128 | no | no | no | −3 / −0.7 / −0.9 / +0.5 | −1.1 | none |
| 256 | no | YES | YES | −2.3 / −0.2 / **+4.9** / +0.8 | −1.0 | numbers d=5 |
| 512 | no | yes | yes | −1.2 / −0.9 / +4.6 / +2.8 | −0.7 | numbers d=5 |
| 1000 | YES | yes | yes | +2.7 / −0.1 / +9.6 / +2.3 | +0.2 | numbers d=5 |
| 1500 | yes | yes | yes | +8.1 / +0.6 / +15.5 / +4.3 | +1.6 | numbers d=2, 5, 10 |
| 3000 | yes | yes | yes | +18.8 / +1.0 / +20.5 / +6.1 | +4.1 | numbers d=2, 5, 10; **hours d=2** |
| 6000 | yes | yes | yes | +26.2 / +3.7 / +29.9 / +7.5 | +4.8 | numbers d=2, 4, 5, 10; hours d=2 |
| 10000 | yes | yes | yes | +25.4 / +4.8 / +29.4 / +8.0 | +5.0 | numbers d=2, 4, 5, 10; hours d=2 |
- Order of first detection: numbers period 5 first (step 256, before the month cycle is detectable), then period 10
  and 2 (≤ 1500), period 4 last (≈ 6000, in the extension segment); the month circle becomes detectable between 512 and
  1000; hour parity (d = 2) becomes a Holm rejection from
  step 3000 in this run and keeps growing (z 4–5.7 to 10000), while in the three released Pythia models at 143k it is
  positive but below the Holm line. Descriptive: one run, one optimiser; the step-0 z = −3 for numbers d = 2 is the
  init's own spectrum through the same fit (no cycle present; INAPPLICABLE as a test).
- Months show no class excess at any step (|z| ≤ 1.2 for d = 3).

## 5. Gates, power and caveats (named)
- Pipeline validity: verifier PASS with both red paths (sealing commit); prime control white in all three models and at
  every A0 step; shuffled nouns null everywhere.
- Power is the limiting factor for months and the hour bets: the instrument sees ≥ 2–5 % excesses on the 100-item open
  lattice but only ≥ 40 % on the 12-item circle. A months verdict needs either more items per class (not possible for
  months) or a lower-variance statistic than summed class power; that is a method change for Will.
- The hours primary read is at the shared final token ':00' (brief rule; the hour lives in context). The first-token
  (' H') column (§5c) and the per-layer column (§5b) are done and DESCRIPTIVE.
- The Lorentzian baseline has no noise term (brief §5.4); σ̂ is descriptive. Fit contamination by large excesses is declared
  (A1) and visible as the d = 20/25 deficits.

## 5b. Per-layer column (DESCRIPTIVE; `--layers all`, B = 400, 1000 shuffles; results/divisor/<tag>_last_all.json)
- **Numbers:** every class d = 2, 4, 5, 10 is positive at EVERY layer of all three models (1.4B layer 1: z = 28.5 / 9.0 /
  25.6 / 7.5). Depth profile: d = 5 and d = 10 grow with depth (1.4B d = 10: 7.5 at layer 1 → 17.6 at layer 24; d = 5: 26 →
  42–49), d = 4 peaks in the middle (1.4B 14.7 at layer 11, 4.9 at 24; 410M 10.8 at 11), d = 2 is flat (22–31). The
  primary read (blocks 8–15) is therefore not a lucky window: the excess is present from the embedding output onward.
- **Hour parity (d = 2):** an EARLY-layer feature that fades as the hour circle forms: 1.4B z = 6.3 at layer 2, 2–3 through
  layer 12, 0.4 by layer 20, while ρ₁ (the smooth cycle) rises from 0.17 to 0.80 over the same depth; 410M peaks at layers
  10–11 (z 4.5–4.9), 70M at layer 3 (4.2). Plain reading (Will's correction): **consistent with parity inherited from
  number representations** — hours are numbers, the numbers concept carries a strong period-2 component, and the item's
  end can compute parity by attending back to the number token; the weaker first-token reading (§5c) does not rule
  inheritance out. With "never past Holm" it stays descriptive. am/pm (d = 12) is slightly negative at every layer.
- **Months:** no class at any layer (d = 3 z ≤ 0.7, d = 4 z ≥ −0.7, all three models); ρ₁ grows 0.18 → 0.30 with depth
  at 1.4B.

## 5c. Hours, first item token ' H' (DESCRIPTIVE declared column; `--read first`; results/divisor/<tag>_first_primary.json)
| model | ρ₁ (cycle p) | parity d=2: z, p, R | am/pm d=12: z, R | shifts d=6 / d=8: R | smallest f (d=2 / 12) |
|---|---|---|---|---|---|
| 1.4B | 0.36 (0.0001) | +0.9, 0.17, +0.35 | −0.5, −0.08 | −0.30 / −0.24 | 0.2 / 0.4 |
| 410M | 0.38 (0.0001) | +1.4, 0.09, +0.59 | −0.7, −0.12 | −0.31 / −0.23 | 0.2 / 0.4 |
| 70M | 0.34 (0.0001) | +2.1, 0.036, +0.71 | −0.5, −0.08 | −0.26 / −0.24 | 0.1 / 0.4 |
- The hour cycle is already present at the hour-number token (ρ₁ 0.34–0.38 vs 0.63 at ':00'), with higher effective
  dimension (k_eff 9–11 vs 3–4), so this column has MORE power (smallest detectable 0.1–0.2 for d = 2, 3, 4, 6).
- Parity (d = 2) is positive in all three models here too but SMALLER than at ':00' (R +0.35/+0.59/+0.71 vs
  +1.17/+1.66/+1.35): the parity excess grows between the number token and the item's end. That does NOT establish that
  it is independent of the number token's parity (the end position can attend back to it); the reading stays "consistent
  with parity inherited from number representations" (§5b), descriptive.
- am/pm (d = 12) is negative in both reads at every model: at this power (smallest f 0.4) an am/pm excess ≥ 40 % of the
  Lorentzian power is excluded descriptively; smaller ones are not.
- Both shift classes (d = 6, 8) read negative in both columns in all models.

## 7. A3 — token-frequency control for the numbers result (sealed 5914913; run 2026-10-03 11:20; results/divisor/numbers_freq_control.json)
Counts: the exact item tokens ' 0' … ' 99' over the 6.29 × 10⁹-token Pile sample on spot (3000 seed-1 batches; results/
divisor/number_token_counts.json). The comb is real in the counts: frequency falls steeply with magnitude (' 0' 8.0 M, ' 1'
6.8 M, ' 9' 1.5 M, ' 99' ≈ 0.2 M) with local peaks at multiples of 10 (' 10' 2.39 M vs ' 9' 1.51 M / ' 11' 0.92 M), at
multiples of 5 and at powers of 2 (' 32' 279 k, ' 64' 164 k vs neighbours ≈ 150 k).
- **Can-fire prerequisite (sealed, > 10 % of the covariate's DFT power in d ∈ {2, 4, 5, 10}): reads 0.097 → NOT MET
  by the letter.** The mean-centred log-frequency profile is dominated by the smooth magnitude decay (trivial class d = 100:
  0.62 of its power; d = 50, the one-digit/two-digit step: 0.19); its comb part is d = 5 0.068, d = 10 0.016, d = 2 0.010, d = 4 0.003 — concentrated on exactly the
  right harmonics (4 of 50 harmonics carrying 6.8 % is 3.4× flat) but 9.7 % in total against the declared 10 %. **As
  sealed, the control is INAPPLICABLE; the residualisation below is reported as DESCRIPTIVE, and the threshold is not
  moved.**
- **Residualisation (run anyway, same script):** the linear log-frequency direction explains 16 % / 18 % / 16 % of the
  centred numbers matrix (1.4B / 410M / 70M; quadratic 22 % / 25 % / 21 %) — a large magnitude component — and
  removing it leaves every class excess unchanged or larger:
| model | d | before z / R | linear-resid z / R | quadratic-resid z / R | Holm p_adj (linear) | smallest f (resid) | word (descriptive) |
|---|---|---|---|---|---|---|---|
| pythia-1.4b | 2 | +28.5 / +9.13 | +31.6 / +8.71 | +30.9 / +7.98 | 0.00425 | 0.02 | SURVIVES |
| pythia-1.4b | 4 | +12.3 / +2.78 | +13.4 / +2.72 | +13.3 / +2.54 | 0.00425 | 0.02 | SURVIVES |
| pythia-1.4b | 5 | +40.8 / +7.16 | +45.2 / +6.94 | +45.9 / +6.61 | 0.00425 | 0.02 | SURVIVES |
| pythia-1.4b | 10 | +8.9 / +1.67 | +11.9 / +1.89 | +13.0 / +1.96 | 0.00425 | 0.05 | SURVIVES |
| pythia-410m | 2 | +31.5 / +11.07 | +36.3 / +10.44 | +34.0 / +9.49 | 0.00425 | 0.02 | SURVIVES |
| pythia-410m | 4 | +10.6 / +2.64 | +12.0 / +2.57 | +11.8 / +2.37 | 0.00425 | 0.02 | SURVIVES |
| pythia-410m | 5 | +37.3 / +7.31 | +43.9 / +7.03 | +43.9 / +6.65 | 0.00425 | 0.02 | SURVIVES |
| pythia-410m | 10 | +7.8 / +1.62 | +10.9 / +1.85 | +11.8 / +1.91 | 0.00425 | 0.05 | SURVIVES |
| pythia-70m | 2 | +26.1 / +8.29 | +28.8 / +7.96 | +27.1 / +7.43 | 0.00425 | 0.02 | SURVIVES |
| pythia-70m | 4 | +3.8 / +0.87 | +4.4 / +0.82 | +4.0 / +0.76 | 0.00425 | 0.02 | SURVIVES |
| pythia-70m | 5 | +25.8 / +4.55 | +29.3 / +4.35 | +29.2 / +4.17 | 0.00425 | 0.02 | SURVIVES |
| pythia-70m | 10 | +6.1 / +1.15 | +8.6 / +1.34 | +9.4 / +1.41 | 0.00425 | 0.05 | SURVIVES |
- **Reading.** An activation component LINEAR (or quadratic) in log token frequency cannot be what carries the period-2/4/
  5/10 excess: projecting that component out (comb part included, since the regression removes the whole direction along
  c) changes none of the z-scores (they rise slightly as the smooth magnitude part leaves the Lorentzian baseline). What
  this does NOT exclude: an activation feature that tracks the comb part of frequency separately from its magnitude part
  (a non-linear frequency effect, e.g. a "round number" feature). That is the covariate the sealed rule says can fire,
  and it is drafted as A4 for Will (prereg), not run.
- The 1.4B deficits at d = 20, 25 (z ≈ −2) are unchanged (contamination signature, A1).
- Status of §3's framing after A3: periods 2, 5, 10 (replication of Zhou et al. / Kantamneni–Tegmark) and period 4 (new)
  are NOT a linear log-frequency comb; "new" still waits on A4 (detrended-comb covariate) because the sealed control did
  not fire by its own letter.

## 7b. A4 v2 — stratified-permutation frequency null (CONFIRMATION RUN; sealed 6a4b1fc; results/divisor/numbers_strat_control.json)
10 000 permutations of the item order within 10 strata of 10 items matched on exact item-token count (bin 0 spans
2.0–8.0 M, bin 4 164–229 k, bin 9 70–75 k), scored against the observed Lorentzian fit held fixed; Holm over d = 2, 4, 5, 10.
| d | 1.4B z, p, word | 410M | 70M | unstratified shuffle p (1.4B / 410M / 70M) |
|---|---|---|---|---|
| 2 | +15.4, 0.0001, SURVIVES | +16.8, 0.0001, SURVIVES | +17.7, 0.0001, SURVIVES | 0.0001 / 0.0002 / 0.0001 |
| 4 | +4.6, 0.0002, SURVIVES | +3.5, 0.0027, SURVIVES | +0.0, 0.4660, NOT RESOLVABLE | 0.0814 / 0.1972 / 0.8583 |
| 5 | +15.5, 0.0001, SURVIVES | +12.7, 0.0001, SURVIVES | +11.1, 0.0001, SURVIVES | 0.0001 / 0.0001 / 0.0001 |
| 10 | +13.5, 0.0001, SURVIVES | +11.9, 0.0001, SURVIVES | +10.7, 0.0001, SURVIVES | 0.0001 / 0.0001 / 0.0001 |
- **d = 2, 5, 10 SURVIVE in all three models** (z 11–18 against a null that carries any function of frequency):
  frequency, linear or not, does not explain them. **d = 4 SURVIVES at 1.4B and 410M, NOT RESOLVABLE at 70M** (where
  its excess is at the null's mean; at 70M even the ordinary shuffle does not reject d = 4).
- Beside the sealed verifier finding that no monotone function of the real counts can create a comb at all, the
  frequency reading is closed for periods 2, 5, 10 at all three sizes and for period 4 at 410M–1.4B. The 5-bin
  sensitivity column reads the same words. This is a confirmation run (designed after A3's descriptive result).
- Period 4 therefore stands as the new class at 410M–1.4B, with the caveat that at 70M it is not resolvable.

## 8. Open leads (not claims)
1. Hour parity (d = 2): same sign in 3/3 released models and a Holm rejection along the A0 trajectory — is it the
   even/odd token-frequency structure of "H:00" times (e.g. 12:00/18:00 vs 13:00/19:00 usage), or a representation of
   parity itself? A sealed test would plant parity into the templates' statistics (or read the first-token column).
2. Numbers d = 4: alias of the period-2 × period-5 structure through the open window, or a genuine quarter-decade
   component? Testable with a synthetic that has only periods 2, 5, 10 at the measured amplitudes (does d = 4 appear?).
3. Months at higher power: per-template spectra (16 draws) as replicates of the class statistic.
4. Trajectory for a Muon run (M0s1 bank) beside A0 — same order of appearance?
5. **Pitch classes (Will):** the 12 pitch classes form the same 12-item circle (same divisor-class power limit), but the
   circle of fifths is the n = 5 (≡ 7) harmonic — the star polygon {12/5} — and augmented / diminished chords are the
   classes d = 3 and d = 4; music text is full of fifth-relatedness, so an n = 5 excess could be large enough for 12 items
   to resolve. Tokenisation audited 10-03 (NeoX): naturals are single tokens; sharps split (' C', '#') with the shared
   final '#' for all five; flats mixed (' Db', ' Eb', ' Ab' single; ' Gb', ' Bb' split as (' G', 'b')). No spelling gives
   12 single tokens, so the read position needs a sealed choice (last token shared for sharps, as for hours). Not in v0.
Figures: `plots/divisor/<tag>_spectra.png`, `<tag>_{months,hours}_polygons.png` (untracked; regenerated by `divisor_plots.py`).
