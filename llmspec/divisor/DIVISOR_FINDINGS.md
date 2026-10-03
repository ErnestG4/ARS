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
- Agreement with Kantamneni & Tegmark (2502.00873, verified): their helix periods T = [2, 5, 10, 100] on GPT-J / Pythia-6.9B /
  Llama-3.1-8B are exactly the classes d = 2, 5, 10 here, now measured against a symmetry baseline at 70M–1.4B. d = 4 is
  new relative to their list (they chose T by magnitude and a base-10 prior; a period-4 component is not a base-10 habit
  — candidates: quarter-structure of the decade, or an alias of the strong period-2 and period-5 components through the
  open-lattice window; left as an open lead, not interpreted).
- Tokenisation is not the explanation in the simple sense: every number 0–99 is a single NeoX token (audit), so the
  periodicities are properties of the token representations, not of a digit-by-digit encoding.

## 4. Trajectory (DESCRIPTIVE; Arm B A0, AdamW 70M, 23 checkpoints; gates PASS at every step)
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
- Order of appearance: numbers period 5 first (step 256, before the month cycle exists), then period 10 and 2 (≤ 1500),
  period 4 last (≈ 6000); the month circle forms between 512 and 1000; hour parity (d = 2) becomes a Holm rejection from
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
  (' H') column is DESCRIPTIVE and pending (A2 rerun on spot); the per-layer column likewise.
- The Lorentzian baseline has no noise term (brief §5.4); σ̂ is descriptive. Fit contamination by large excesses is declared
  (A1) and visible as the d = 20/25 deficits.

## 6. Open leads (not claims)
1. Hour parity (d = 2): same sign in 3/3 released models and a Holm rejection along the A0 trajectory — is it the
   even/odd token-frequency structure of "H:00" times (e.g. 12:00/18:00 vs 13:00/19:00 usage), or a representation of
   parity itself? A sealed test would plant parity into the templates' statistics (or read the first-token column).
2. Numbers d = 4: alias of the period-2 × period-5 structure through the open window, or a genuine quarter-decade
   component? Testable with a synthetic that has only periods 2, 5, 10 at the measured amplitudes (does d = 4 appear?).
3. Months at higher power: per-template spectra (16 draws) as replicates of the class statistic.
4. Trajectory for a Muon run (M0s1 bank) beside A0 — same order of appearance?
Figures: `plots/divisor/<tag>_spectra.png`, `<tag>_{months,hours}_polygons.png` (untracked; regenerated by `divisor_plots.py`).
