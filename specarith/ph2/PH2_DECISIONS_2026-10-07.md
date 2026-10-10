# Phase 2 decisions (Will, 2026-10-07, ~02:40) — on the BBLM / Bogomolny–Keating literature report

Filed verbatim. They answer `lit/bblm_bk.md` (agent report). Phase 2 is not sealed; these bind its pre-registration.

```
check these against the primary sources before anything is sealed.

1. Λ: adopt the corrected value, but it doesn't change anything you'd measure. Citing Bornemann–Forrester–Mays (2017) with Λ = 1.5731510713… is right. The size of the effect, though: N_eff scales as 1/√Λ, so a change in the fifth decimal moves N_eff by about 3.5 parts per million, far below anything the data could resolve. Record it as a citation correction, not a risk.

2. Bogomolny–Keating: accept. My brief cited "Bogomolny–Keating (1995–96)" without saying which paper. The pair correlation with arithmetic lower-order terms is the 1996 PRL; the Nonlinearity papers are about higher correlations. Cite the PRL for Phase 2 and the comb leg.

3. The heights: this is a real error in my brief. I listed Odlyzko tables "around 10¹², 10²¹, 10²², 10²³" and mixed up zero number with height. The public tables reach zero number 10²², which is height about 1.37×10²¹, as the report says. But Phase 2 doesn't need the 10²³ data:

The finite-size law depends on log(E/2π), and the public tables already span it from about 9 (low zeros) to about 46 (zero number 10²²).
That's enough heights to test the N_eff law across a wide range.
Have CC check whether David Platt's rigorously verified zeros, available through the LMFDB, add useful intermediate heights.
Re-scope "10²³" to "any additional height with a public, hashable source." Don't block on it.

4a. α versus ᾱ: decide by source, before data. I can't verify the ᾱ = 2α − 1 relation from here. The clean rule:

primary model: BBLM's leading correction (N_eff alone), with BBLM's own scale convention;
secondary model: the higher-order kernel, with whatever scale convention its own source (Bornemann–Forrester–Mays) defines, verified there.

Mixing a scale factor from one paper with a kernel from another is exactly the wrong-slot error.

4b. Unfolding density: avoid both formulas and use the exact one. The density of zeros is (1/2π)·log(E/2π). The log(E/2πe) form belongs to the counting function N(E), so the "misprint" is likely a mix-up between N and its derivative. The two differ by about 1/log(E/2π), around 2% at the top heights, larger than the effect itself, as the report says. Sidestep the issue the same way the Phase 6 seal does: unfold with the exact smooth count, θ(E)/π + 1, from the Riemann–Siegel theta function, not with either density approximation. That also keeps Phase 2 and Phase 6 consistent.
```

Actions (CC): Phase 2 to-dos added to `../NOTES.md`'s overnight plan — (a) verify the report's load-bearing claims
against the primary sources (Λ digits, BBLM eqs. 16/19/24, BFM's ᾱ and its scale convention, the sine/CUE_N determinant
method); (b) scope Platt's LMFDB zeros as additional public, hashable heights.

## Second round (Will, 2026-10-07 morning) — 4a and data

Filed verbatim:

```
Phase 2 4a: both arms declared; PRIMARY = "N_eff alone" (BBLM convention);
SECONDARY = BBLM eq. 24 / BFM higher-order with ᾱ = 2α − 1 per BFM. No mixing.
Data: Platt blocks by md5 at heights declared pre-data (log(E/2π) 9–22.3,
not the full 1.29 TB) + Odlyzko top tables; 24.5–44.6 gap stated as a limit.
```

## Third round (Will, 2026-10-07 midday) — guidance for the Phase 2 seal

Filed verbatim:

```
Phase 2, a few things for its seal, on top of your decisions (both curves, with "N_eff alone" primary; exact-θ unfolding; heights declared before data; BFM's Λ):

Use the known misprint as a red path. Unfolding with the log(E/2πe) form is a real error from the literature, about 2% at the top heights, larger than the effect being measured. The gate should fail on it. That shows the instrument is sensitive to precisely the mistake that's already caught people. Declare the Λ correction (about 3.5 ppm in N_eff) as an unreachable red path in the pre-read, the way Phase 6 listed its unreachable red paths.
Expect a huge effect at low heights. N_eff = log(E/2π)/√(12Λ) is only about 2 at the lowest zeros, rising to about 10.6 near zero number 10²². The finite-size correction is enormous at the bottom and subtle at the top, so per-height results matter more than a pooled one.
Gate structure per height bin:
G0: CUE draws at N_eff reproduce BBLM's published curves. The known answer, run before any zeros are read.
G1: the real zeros match CUE(N_eff) within the sealed tolerance.
Power arm: asymptotic GUE (N = ∞) must be rejected, at least at low heights where the gap is large.
Resolution arm: CUE at N_eff × 0.8 and × 1.2 should also be rejected where the data has the power. That turns "consistent with N_eff" into "N_eff pinned to within ±20%," a much stronger statement.
One witness, not three. Per Task B, F(α), Σ² and Δ₃ count as a single witness. Pick the primary statistic, the ⟨r̃⟩ distribution or the nearest-neighbour spacing, and seal it.
```

CC notes (checked before drafting; carried into PH2_SEAL_DRAFT):
- ⟨r̃⟩ cannot be the primary: Nishigaki 2025 (lit/bblm_bk.md) — the CUE_N gap-ratio correction is O(N⁻⁴) (the O(N⁻²)
  term cancels), so ⟨r̃⟩ is blind to the N_eff⁻² effect. Primary = the consecutive-spacing distribution (BBLM's).
- N_eff at the very lowest zeros is ≈ 0.19 (first zero), 1.17 at γ = 10³, 2.16 at the top of zeros1 (log(E/2π) = 9.39);
  10.78 at zero number 10²² (log 46.83). Below N_eff ≈ 2 the p₀ + p₁N⁻² expansion is not meaningful.
- CUE(N) is defined by matrices only for integer N; BBLM/BFM evaluate it at real N_eff via the Fredholm determinant
  det(I − K^N) (K^N = sin πx/(N sin(πx/N)), real N) and the closed form p₁ = −(1/12)(s²p₀)″ (Forrester–Shen).
- Release v2026.10.07 published by Will: "checkpoint for the specarith branch taken before the work begins".

## Fourth round (Will, 2026-10-07) — answers to PH2_SEAL_DRAFT §9

Filed verbatim:

```
Phase 2 decisions (Will):
1. Primary = p(s); ⟨r̃⟩/Σ²/F(α)/Δ₃ descriptive, one witness.
2. Seal bins with N_eff ≥ 2; justify the cutoff in the seal from the
   pre-read's next-order-term estimate. Lower bins descriptive.
3. Truncation allowance: adopt for the PRIMARY only (leading-order law).
   Per bin, if the widened tolerance prevents rejecting N=∞ or makes the
   resolution arm meaningless → primary NOT RESOLVABLE there. SECONDARY
   (BFM higher-order) uses statistical tolerance only — the sharp test.
4. Platt heights ≈13, 15, 17, 19, 21, 22.3 (one file each), md5-pinned in
   the seal before download.
5. Per-bin resolution target sealed from the pre-read (e.g. 3× predicted
   SD of N̂); ±20% remains the floor target; achieved intervals always
   reported.
```

## Fifth round (Will, 2026-10-07) — seal text approved with amendment A1

Filed verbatim:

```
Phase 2 seal text: APPROVED with one amendment (A1):
A1. CI robustness: add a moving-block bootstrap of each bin's own
spacings (block lengths declared pre-data, e.g. sweep 10/30/100 × N_eff
levels). G1 uses the WIDER of the CUE-calibrated CI and the bootstrap CI.
G0d also validates bootstrap coverage on CUE surrogates. Reason: concatenated
CUE_N blocks impose a within-block sum constraint and zero between-block
correlation that the zero sequence does not share.
κ = N/N_eff estimand: approved.
Commit as PH2_SEAL text; proceed to code + pre-read.
```

## Sixth round (Will, 2026-10-07 afternoon) — the pre-read's proposed amendments PA1–PA4

Filed verbatim:

```
Phase 2 amendment decisions (Will):
PA1 adopt: fit window s ≤ 2.0, model normalised over the window, every bin,
both arms. Report windows 1.8 and 2.2 descriptively (sensitivity).
PA2: allowance = MAX of the two shifts. Rationale for the seal: the
exact-CUE_N shift and the secondary shift measure distance to two
ALTERNATIVE references for the truth (ζ = CUE(N_eff) vs ζ = BFM higher-
order); only one can hold, so the allowance must cover the larger, not
their sum. Sum-based verdicts for bins A and B reported descriptively.
PA3 adopt.
PA4: Will downloads the six Platt files manually into
specarith/ph2/data/platt/; verify with fetch_data.sh against pinned md5s.
```

Status at filing: PA4 done (all six md5 OK, results/logs/fetch_data.log, commit "all six Platt files … verified").

## Seventh round (Will, 2026-10-07 evening) — PA5 and the achieved-width refinement

Filed verbatim:

```
PA5: ACCEPT as implemented — SECONDARY uses the same NOT RESOLVABLE rule
(cannot exclude N=∞ or wider than ±20%), statistical CI only; red-path
checks that cannot fire in a bin read INAPPLICABLE.
Refinement: pre-data classification from predicted spread stands; post-data,
any arm whose ACHIEVED CI cannot exclude N=∞ or exceeds ±20% reads
"NOT RESOLVABLE (achieved)" — flagged, never PASS/FAIL. Report predicted
and achieved widths per bin.
```

## Eighth round (Will, 2026-10-07 night) — PA6, new PA7, proceed

Filed verbatim:

```
PA6: option (a) — PRIMARY h_bin arm INAPPLICABLE pre-data (primary
resolution is bounded by its own theoretical truncation; statistical
resolution is carried by the SECONDARY's h_bin arm). Report primary ±20%
floor arm and achieved interval.
PA7 (new): red paths are REQUIRED to fail only where pre-read power ≥ 0.80;
below that they are reported descriptively, not scored. → RP-mix required
in A, B (and P1 if power ≥ 0.80); descriptive at P2 (power 0.59).
Proceed: dry run + achieved witness results to Will, then seal on go.
```

## Ninth round (Will, 2026-10-07 night) — GO for the seal

Filed verbatim:

```
GO: build the Phase 2 seal.
make_seal_json.py --pa2 max --adopted PA1,PA2,PA3,PA4,PA5,PA6,PA7
→ seal commit. Will pushes.
Then the real run reads zeros only under the matching seal; report every bin
(sealed and descriptive), with bin A's primary flagged as least informative
(bias ≈ allowance by construction) and the secondary as the sharp test.
```

## Tenth round (Will, 2026-10-07 night) — framing of the result; next steps

Filed verbatim:

```
Phase 2 item 1 — framing: headline as "the O(N⁻²)-truncated finite-size law
(BFM, ᾱ) under-describes ζ spacings at N_eff 2.3–5.1 at 0.5–1% precision;
residual consistent with a missing O(N⁻⁴) term" — not "zeros do not follow BFM".
Decisions:
1. Before any new model: lit check for a known next-order spacing correction
   (Forrester–Mays 2015; CFZ ratios conjecture / Conrey–Snaith lower-order
   terms). Then seal ONE theory-fixed p₂ (no fitted params); confirmatory
   test on FRESH Platt heights (e.g. L = 14, 16, 18, 20, 22; md5 pinned pre-
   download). Original 8 bins under the new model: descriptive only.
2. Low heights (N_eff < 2): descriptive, labelled outside expansion validity.
3. Order: lit check → Phase 6.1 candidates → Phase 1; fresh-height test when
   its model is sealed.
Will pushes 4839b52.. incl. tag ph2-seal-2.1.
```
Accompanying note (Will): the clean design commits to one theoretical source for p₂ before computing its prediction,
because choosing the theory after seeing the residual is a forking path; if an N⁻⁴ coefficient already exists in the
literature, matching it is a replication and the claim changes accordingly.

## Eleventh round (Will, 2026-10-08) — after the next-order literature check

Filed verbatim:

```
Phase 2 decision 1 (Will):
(i) NEW confirmatory phase: pair correlation R₂ at small separations vs the
    BK 1996 PRL / Conrey–Snaith two-point formula with arithmetic lower-order
    terms — ONE source committed before computing; parameter-free; FRESH
    Platt heights L = 14,16,18,20,22 (md5 pinned pre-download).
(ii) Scope (a) — ζ-specific O(N⁻⁴) spacing term from Conrey–Snaith — as a
    research project; report scope before committing. Skip (b).
(iii) (c) descriptive only on seen bins: comparison vs exact CUE(N_eff),
    noting the opposite-sign deviation as an open lead. No seal.
Verify (or log) the possible missing 1/15 in BBLM v1 eq. (8).
```
Accompanying note (Will): the new R₂ phase is the programme's Phase 2 "new part" (the comb leg), run as a new phase so
Task B's one-witness rule is not violated; (c)'s opposite-sign fact suggests the ζ-specific (arithmetic) corrections may
dominate and act against the matrix-size ones — an open lead, no verdict.

## Twelfth round (Will, 2026-10-08) — R₂ phase decisions R1–R5; route (a)

Filed verbatim:

```
R₂ phase (Will):
R1 accept CS 2007 Thm 4.1; seal states it rests on the ratios conjecture
   (test of a conjecture's lower-order prediction).
R2 frame as probable replication: find/file the BK/Odlyzko comparison
   (cf. Berry–Keating 1999 SIAM Review). Novelty = calibrated μ with CI
   across fresh heights + sealed nulls → "independent quantitative replication".
R3 ONE primary test function, chosen pre-data where the predicted
   arithmetic term/noise is largest; 2–3 others descriptive; no sweeps.
R4 pairs fully inside each file, separation ≤ declared max; report
   excluded fraction.
R5 resolvable iff pre-read power to reject μ=0 ≥ 0.80; target ½-width
   min(3·predicted SD, 0.5); declared bootstrap sweep, wider CI; (achieved) rule.
Route (a): GO after R₂ sealed; milestone 1 = U(N) construction reproduces
   exact CUE_N tables before any ζ number (gate; stop if it fails).
Phase 6.1: approved IF the text implements D1–D6 as summarized; upload for
   a full review if preferred.
```

## Thirteenth round (Will, 2026-10-09) — after the 6.1 read

R₂ seal text: "If it implements R1–R5 as decided, approve it; if you'd like a full review, upload it. Either way, the
five fresh Platt files need downloading by hand before the read." CC checked R1–R5 against PH2R2_SEAL_1.0.md §§1–3:
implemented; u_max (R4) and the bootstrap block lengths (R5) are named but not valued in the text and are declared in
the pre-read before any fresh zero is read. Status set to TEXT APPROVED. Also (Will): push 70be2bc7 (tag ph6.1-seal) and
0405f475 (Will pushes); a Zenodo snapshot of Phase 6 as a complete unit; then the R₂ read, route (a)'s U(N) milestone and
Phase 1 on spot.

## Fourteenth round (Will, 2026-10-09 morning) — R₂ seal held for the achieved-rule fix

```
R₂: HOLD seal. Achieved-rule fix (pre-data):
NOT RESOLVABLE (achieved) iff achieved CI contains BOTH 0 and 1, or
half-width > 0.5. Otherwise G1 PASS iff 1 ∈ CI, else FAIL.
Re-run dry run: expect μ=0 → FAIL; μ=1 → PASS; small-sample witness →
NOT RESOLVABLE (achieved). Then rebuild seal JSON; then my go.
Phase 2 erratum (no verdict change): its "cannot exclude N=∞" achieved
clause conflated outcome with precision; only achieved firing (A primary)
was width-based; H bins were pre-data NR.
Decision 1: approve raw / surrogate-relative / drift-removed reporting;
declare the drift-removal method (e.g. per-block exact-density
normalisation) in the seal before the read.
```
Will's diagnosis: the dry run showed every μ = 0 surrogate reading NOT RESOLVABLE (achieved) with tight CIs that exclude
μ = 1, so the instrument could never reject Conrey–Snaith in favour of μ = 0. The guard mixed precision with outcome.
Will noted that the same conflation entered Phase 2 through the PA5 refinement (A6(iii)).

Filed as PH2R2_SEAL_1.0 **A2** (rule) and **A3** (A1 three ways; drift removal c_i·e(t_c)/e(t_i), with e the
sine-kernel expectation at the exact smooth density N̄′(t)). The Phase 2 erratum is PH2_FINDINGS §6; CC checked the
facts against §1 (A's PRIMARY 0.215 > 0.20 is the only achieved firing; no A–P6 CI contains κ = ∞; H1–H3 pre-data NR).

## Fifteenth round (Will, 2026-10-09 afternoon) — confirming the shrinking error bars

```
Shrink-confirm decisions (Will):
(a) Two-stage: Stage 1 = direction-only seal on fresh set F1 (now).
    Stage 2 = quantitative few-prime model, own known-answer gate,
    prediction sealed on a separate fresh set F2. Stage 1 does not wait.
(b) Primary window 10⁶ levels; 2·10⁵ secondary.
(c) Disjoint fresh sets declared + md5-pinned now: F1 (shrink direction),
    F2 (quantitative model), F3 (route (a)); interleaved quarter/half-integer
    L between all seen heights.
(d) Other members: secondary arms with matched GUE baselines. Seal the
    mechanism's directional predictions as arms: wider bump → larger shrink;
    shrink weakens with height.
Call the long-baseline result on v2 only.
```
Also in this round, Will on the R₂ read: keep the headline as written. Next steps in order: the long sine-kernel baseline,
then the confirmatory seal, the other members (descriptive), route (a) milestone 1, then Phase 1; a Zenodo snapshot of
Phase 2 + R₂. F1–F3 declared in `ph2r2/FRESH_SETS_F1_F3.md` (generator `declare_fresh_sets.py`).

## Sixteenth round (Will, 2026-10-09 evening) — Stage 1 decisions; fresh-set gap rule

```
Stage 1 decisions (Will):
1. Arm A: ≥4/5 F1 bins at >3 combined SE (as declared); pooled one-sided
   test descriptive.
2. Reference effect = ½ smallest seen shrink at 10⁶: accept.
3. Arm C: accept (paired per-u difference, ≥3/4 u, mean > 2 SE).
4. Arm D: add two F1 bins at the height extremes (L ≈ 13.25, ≈ 22.1),
   md5-pinned pre-download, used for D (descriptive for A). If D power
   still < 0.80 → D descriptive.
Low-L adjacency: require ≥1-file gap from every touched file; re-pin
F1's 14.25 accordingly before download.
Long-baseline call on v2 10⁶ tier only, at ~20:00.
```
Applied in `declare_fresh_sets.py` v2 (gap from every touched height range and between picks). **L ≈ 13.25 is
infeasible:** it lies inside the seen P1 file (zeros_2546000, L 12.91–13.51). The only file between P1 and R1
(zeros_4646000) is adjacent to both. Everything lower overlaps Phase 2's Odlyzko bins A/B. The lowest gap-feasible file
is zeros_10946000 (L 14.37–14.55), which becomes F1's re-pinned low bin; F2's low bin moves 14.5 → 16.5. F1 = 6 bins (5
for A, + 22.1 for D).

## Seventeenth round (Will, 2026-10-09 night) — Stage 1 arm rules after the pre-read

```
Stage 1 decisions (Will):
1. Arm C: recompute SE by resampling the 16 GUE sequences as units, paired
   across members; re-run the 500 splits. If empirical rate ≈ nominal
   (0.023) → keep 2 SE. Otherwise (or if unvalidated pre-seal) → 3 SE.
   Report the empirical rate under the sealed rule either way.
2. Arm B: descriptive (unresolvable pre-data in all bins).
3. Seal records Arm A's joint power (≈0.51 at the half-size reference;
   ≈1 at the seen effect) so a FAIL is interpreted accordingly.
F1a NOT RESOLVABLE stays; Arm A needs all four of F1b–F1e.
```
Also from Will this evening, before the pre-read: add data rather than change rules (double short bins, gap kept); a
pre-data change of primary L is acceptable; never the full seen effect as reference or a 2-SE A threshold. If F1a alone
is short: leave it NOT RESOLVABLE with the 4-of-5 rule unchanged.
Result (`s1_fpr_c.py`): with unit-resampled SE, arm C's empirical false-positive rate is 0.042 at 2 SE (nominal 0.023;
consistent with the 8-vs-8 split's t₇ tail) and 0.014 at 3 SE, so **C is sealed at 3 SE**. Power at the seen Δ: 1.00.

## Eighteenth round (Will, 2026-10-10) — after the Stage 1 read; Stage 2 and route (a) combined

Will on the Stage 1 read: "A strong result, correctly reported." Headline adopted (`ph2s/PH2S_STAGE1_FINDINGS.md`); bring
forward that the conservative reference did not bind (observed shrinks at the seen size). A blinded literature check
must come before any novelty claim: four-point/higher correlations (Conrey–Snaith 2008, Bogomolny–Keating), mesoscopic
fluctuations (Bourgade–Kuan, Rodgers), form-factor self-averaging. Zenodo snapshot: add Stage 1 with the headline,
arm D's FAIL stated plainly and the joint-power note.

Stage 2 refinement (Will): try Conrey–Snaith's four-point lower-order terms for a theory-fixed, parameter-free prediction
of the shrink on F2, the move that worked for R₂. **Combined with route (a) (Will):** "One careful transcription of
Conrey–Snaith's n = 2, 3, 4 correlations, then two different known-answer gates on the U(N) analogue: for route (a): it
reproduces the exact CUE_N spacing tables; for Stage 2: it reproduces the flat sine-kernel baseline you actually
measured." The shared code means the F2 and F3 results are not independent in method, but they test different
hypotheses on disjoint data. The few-prime model stays the fallback until the transcription passes both gates. Next:
the literature findings and the combined plan, together.

## Nineteenth round (Will, 2026-10-10) — Stage 2 statistic; gates; proceed

```
Stage 2 / CS4 combined plan decisions (Will):
1. Option (a): Stage 2 statistic = variance across smooth tapered windows
   satisfying CS08's analyticity (holomorphic |Im x| < 2), for both
   prediction and measurement. New pre-read (GUE baselines reusing the F2
   sequences, power, false-positive splits) before the F2 seal.
   Bridge: tapered statistic on F1 (seen) reported descriptively beside
   Stage 1's sharp-block results.
2. Third known answer: U(N) assembly reproduces Aguirre–Soshnikov–Sumpter
   exact CUE pair-statistic variance before block/taper geometry enters (gate).
3. BLS autocovariance-sum estimate: unsealed sanity check of sign/scale.
Novelty wording waits for Coram–Diaconis 2003 (Will can fetch the PDF by hand).
Proceed: CS08 n=2,3,4 transcription + U(N) gates.
```
Will's reason for (a): the prediction should be exact for the statistic measured. Under (b), the edge-effect bound
could be as large as the effect. On the Berry correction: "the dated correction note is the right way to handle it."

## Twentieth round (Will, 2026-10-10) — CS4: erratum handling; the split plan

```
CS4 decisions (Will):
- Erratum: check CNTP published version first; record as "arXiv v1 typo,
  corrected in journal" if fixed there; otherwise as erratum.
- Split plan: GO, plus:
  (1) direct sparse evaluation of connected R4 at a few hundred large-r points
      (log grid, parallel on spot) to verify the analytic r-averaged constant
      before using it;
  (2) positivity/validity guard: declare the constant-part approximation's
      range; predicted variance must stay positive for all block lengths
      ≤ 10⁴, else gate FAIL;
  (3) U(N) validation (flat baseline + small-N MC) before any ζ number;
      seen-data comparison descriptive only; sealed test on F2.
```

## Twenty-first round (Will, 2026-10-10) — sparse check; cutoff; Stage 2 prediction form; route (a) window

```
Decisions (Will):
- Sparse check: PASS recorded with 1.9× margin; suspected cancellation in the
  non-oscillating sum noted; r > 2·10⁴ unchecked. No further work (Stage 2
  needs ~1e-3 relative; evaluator error irrelevant at that scale).
- Cutoff: converges (not logarithmic; record that the log hypothesis was
  wrong). Use cutoff ≥ 3·10⁵; analytic rewrite dropped.
- Stage 2 prediction: NO functional form (drop K + c∞·b). Compute predicted g
  directly at the sealed block lengths and taper from the evaluated
  integrals; check positivity on computed values; report the log b
  behaviour descriptively.
- Route (a): window s ≤ 1.8 (comparable to Phase 2's 1.8 sensitivity fits);
  add n = 5 only if the gate still fails at 1.8.
- CNTP PDF: Will fetches by hand. Phase 1 D1–D6: Will uploads draft for review.
```
Route (a) at s ≤ 1.8, read from the gate's existing interpolants (`results/route_a_pgate.json`; no rerun):
max |p₄ − p_N| = 5.6e-8 (N = 4), 5.0e-5 (N = 10), 6.9e-5 (N = 50), all below the ~1e-4 bin resolution and within
the n = 5 truncation bound, so **no n = 5 term**. Recorded in `SCOPE_CS_SPACING.md` (window amendment) and
`cs4/G_S_DESIGN.md` §6.
