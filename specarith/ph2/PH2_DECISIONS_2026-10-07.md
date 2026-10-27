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

## Twenty-second round (Will, 2026-10-10) — novelty wording after the Coram–Diaconis read

The amended wording is right, plus one addition: CD's lag-1 anti-correlation (−0.2 between consecutive blocks' W) is
in spirit an earlier glimpse of the kind of effect Stage 1 measured, and a reader who knows the paper would expect it
mentioned; leaving it out would overstate the novelty. Two cautions keep it from undercutting the claim: (1) CD's
blocks are each rescaled to their own length, and consecutive block lengths are anti-correlated in any rigid sequence,
the sine kernel included, so the −0.2 may be generic rigidity, not arithmetic; CD made no sine-kernel comparison and
their numbers do not allow one; (2) we read the 2000 technical report, and the 2003 journal version may differ; the
wording says so. PH2S_STAGE1_FINDINGS.md drops "novelty not yet claimed" for this paragraph:

> To our knowledge, no published work measures how the across-block variance of a local pair statistic of the zeta
> zeros (test function a few mean spacings wide) depends on block length, or compares it with the sine kernel and a
> theory-fixed arithmetic prediction. The closest precedent is Coram & Diaconis (2003; read in its 2000 technical-report
> version). They tested the across-block distribution of |Σ_j e^{iθ_j}|², a pair sum in a single block-scale Fourier
> mode, for blocks of n ≈ log(T/2π) = 42 zeros wrapped onto the circle, found agreement with CUE₄₂, and noted a lag-1
> anti-correlation (−0.2) between consecutive blocks' values, without a sine-kernel or arithmetic comparison.

On the numerics (Will): the precision probe passing down to 10⁻³ separation against a grid minimum of 1.3·10⁻³ is the
right kind of margin; the cluster check at the grid corner closes the last untested configuration, and the
prediction's precision story is complete once it lands.

## Twenty-third round (Will, 2026-10-10) — Stage 2: amendment 7 approved, with a condition before the seal

```
Stage 2 decision (Will): Amendment 7 APPROVED — prediction = CS08 correlation
averaged over each F2 file's heights; oscillating-part check uses grid step
≤ 0.1, height-averaged.
Condition before seal: state explicitly that prediction and estimator are the
same quantity —
(i) the Stage 2 estimator removes the smooth height-dependence of the window
    mean (as Stage 1's drift removal), OR the prediction includes the
    between-window mean-variance term (the F2 pre-read's within-file height-
    drift item feeds this); and
(ii) any oscillating height-dependence of the two-point mean is shown
    negligible at ≤ 1e-3 of v, quantified like the four-point check.
Stage 1 vs Stage 2 near-match stays descriptive (different statistic).
```
Work on the condition: `cs4/diag_mu2.py` (the two-point mean μ(ℓ) across each F2 file); record in
`cs4/GS_ZETA_RESULTS.md` §5.

## Twenty-fourth round (Will, 2026-10-10) — Stage 2 estimator: successive differences (option B)

```
Stage 2 decision (Will, round 24): (iii) → option B.
Estimator: successive differences, Σ(S_{i+1} − S_i)²/(2(n−1)b);
expectation v(b)(1 − ρ₁), exact. Extend the long-range grid to 6·10⁴ on spot
(~3 h) to compute the predicted ρ₁. Re-measure GUE baselines and the F1
comparison with the new estimator.
(i) and (ii): settled as reported; c∞ cancels under B (closes amendment 1's
c∞ item).
Descriptive / open leads: non-decaying C(r) (RMS 0.053 to 4.8·10⁴); F1
neighbour-window ρ ≈ −0.03 to −0.04 vs GUE ≈ 0 (seen data); check whether
the theory's ρ₁ for Coram–Diaconis's configuration explains their lag-1 −0.2.
```
Recorded in `cs4/G_S_DESIGN.md` §6 amendment 8; open leads in `OPEN_LEADS.md`.

## Twenty-fifth round (Will, 2026-10-10) — publication timing, two round-24 calls, and the Coram–Diaconis wording

```
push the branch and all existing seal tags;
add a tag on the prediction commit, something like ph2s-stage2-prediction, so the prediction's public timestamp is
unambiguous;
leave the Zenodo snapshot until after the Stage 2 read, and bundle prediction, seal and result into one release.

On the round-24 results, three quick calls:

The lag-term oscillating part (2σ ≈ 1.8×10⁻³, missing the 10⁻³ standard): accept as recorded. In g it's about
6×10⁻⁴, against a per-file SE around 0.04, so it can't affect the test. Record that it misses the standard and why
that doesn't matter.
The lag term's cutoff convergence at b = 10⁴: check it before the seal. It's the sealed quantity, and the earlier
diagnostic showed cutoff sensitivity growing with b (0.64% at b = 100, 0.75% at b = 300 at low cutoffs). One height
at b = 10⁴, cutoffs 3×10⁵ against 10⁶, is enough. That's cheap, and it's the one unchecked piece of the core number.
The Coram–Diaconis wording: revise it. GUE giving about 0 against the zeros' −0.25 under their construction argues
against the "may be generic rigidity" reading I suggested. New wording: "not explained by GUE-level rigidity (GUE
gives ≈ 0 under the same construction); an arithmetic origin is conjectured (possibly prime 2) and not yet tested."
My earlier wording was too quick; the correction should be recorded as such.
```
- Tag `ph2s-stage2-prediction` (annotated) on 8bc570d1, the commit that records the estimator-B prediction.
- Lag-term oscillating part: recorded in `cs4/GS_ZETA_RESULTS.md` §6.2.
- Cutoff check: `cs4/gs_zeta_cutB.py` (ℓ = 15.7502, every node pair, pmax 10⁶ vs the stored 3·10⁵); result in
  `cs4/GS_ZETA_RESULTS.md` §6.2.
- Coram–Diaconis: the twenty-second-round caution is corrected in `ph2s/lit/PAIRSUM_VARIANCE_LIT.md`, with an addendum
  to `ph2s/PH2S_STAGE1_FINDINGS.md` and `OPEN_LEADS.md` L5.

## Twenty-sixth round (Will, 2026-10-11) — the lag-term cutoff result; a lesson; on to the F2 pre-read

```
That's a clean result, and the side finding is the best part. Under the old estimator the cutoff error was 5×10⁻³
in v at b = 10⁴, which the b ≤ 300 check couldn't see, while estimator B removes it exactly because it's a constant
shift. So the switch to B, made for a different reason (turning a bound into an identity), turns out to also protect
the prediction from a cutoff error nobody had measured. Worth recording as a lesson too: a convergence check run at
small b doesn't certify large b when the error grows with b.

g_B converged to six decimal places (0.670275 → 0.670276) is as settled as a sealed prediction gets. Push 85aeff84
when convenient, then on to the F2 pre-read with estimator B.
```
- **Lesson (recorded):** a convergence check certifies only the scale it was run at. If the error grows with the
  scale parameter, run the check at the sealed scale, or show how the error scales. Here amendment 4 (b ≤ 300) passed,
  while at b = 10⁴ the same cutoff move shifted v by 5×10⁻³. Estimator B was adopted to turn a bound into an identity,
  and it also cancels this error exactly, because the error is a constant in C. (`cs4/GS_ZETA_RESULTS.md` §6.2.)
- Will pushed 85aeff84; both remotes were verified.

## Twenty-seventh round (Will, 2026-10-11) — the Stage 2 rule

```
Stage 2 rule (Will, round 27): option (a).
PASS iff pooled deviation within 2 SE (R2, k=2) AND ≥ 4 of 5 files within
3 SE (R1, k=3). Precision guard: RESOLVABLE iff 2·SE_pool ≤ 0.07.
Seal records: GUE calibration (z SD 1.04–1.08); actual false-fail rate
~6–7%; power vs a 20% shrink error 0.92 (low side) / 0.68 (high side,
towards GUE). Read report gives pooled ĝ_B ± CI beside the prediction,
regardless of verdict.
Then: build seal JSON + read script with md5 verification before decode.
```
- Will pushed e7fbf200; both remotes were verified.
- **Correction found while building the seal (mine):** the pre-read (e7fbf200) calibrated against the Stage 1 GUE
  sequences (16 × 10⁶). The dedicated Stage 2 baseline exists and is complete: 24 × 10⁶ fresh sequences from the 10-10
  overnight queue (item 4; `ph2s2/f2_gue_levels.py`, seed base 20261012). The nineteenth round's "GUE baselines reusing
  the F2 sequences" refers to those.
  - The calibration, the false-FAIL rate of the adopted rule, and the dry run's GUE stand-in are re-run on the Stage 2
    sequences. The Stage 1 sequences are kept as a replication.
  - The numbers the seal records come from that re-run (`ph2s2/PH2S_STAGE2_PREREAD.md` §3, revised).
- Built: `ph2s2/s2read.py` (read and dry run; every F2 md5 is checked before any decode) and `ph2s2/make_seal_json.py`.
  The text is `ph2s2/PH2S_SEAL_2.0.md`, for Will's go; the seal commit and tag are Will's call.

## Twenty-eighth round (Will, 2026-10-11) — pooling construction C; conditional GO for the Stage 2 seal

```
Stage 2 (Will, round 28): pooling = option C — weights fixed pre-data,
∝ number of b = 10⁴ windows per file. Seal records C's GUE calibration:
false-fail 5.5–5.7%, power vs a 20% shrink error 0.88 (low) / 0.76 (high);
note the round-27 "6–7%" figure was superseded (simplified model;
inverse-variance pooling gave 9.0% on the proper Stage 2 GUE baseline).
Conditional GO: after switching s2read.py to C, re-run both dry runs (F1
pipeline check, GUE stand-in) and make_seal_json.py --check. If all pass
as before: commit the seal, tag ph2s-stage2-seal. If anything changes: hold
and report.
Will: push 66380cba, 35bd8dd1 (and the seal commit + tag once made);
then download the five F2 files for the read on spot.
```
- **Weights as implemented:** W_f ∝ n_f(10⁴) − 1, the number of successive differences at b = 10⁴. The counts come
  from the pinned height ranges (`s2read.windows_from_range`), not from the data. They are pinned in the seal JSON.
- **Outcome:** after the switch to C, the dry run and `--check` all held as before, so the seal was committed
  (91f74031) with tag `ph2s-stage2-seal`. Will pushed both; both remotes were verified.
- **Read (2026-10-11, 23f4c947):** all five F2 md5s matched their pins. The verdict is **PASS**: pooled ĝ_B = 0.6792
  [0.6441, 0.7143] against 0.6830, z_pool = −0.22, 5 of 5 files within 3 SE, 2·SE_pool = 0.035
  (`ph2s2/PH2S_STAGE2_FINDINGS.md`).

## Twenty-ninth round (Will, 2026-10-11) — Stage 2 headline, limits, Zenodo release

```
That's a strong result. A parameter-free prediction built from Conrey–Snaith's four-point correlations was computed,
publicly tagged before the test data was downloaded, and then matched on five fresh heights: measured shrink equal to
1.01 times the predicted one, 95% interval [0.89, 1.14], with the zeros 16 SE away from the sine kernel. Stage 1 found
that the suppression exists; Stage 2 shows its size is what the arithmetic structure of the zeros predicts.

Suggested headline: "On five fresh heights, the suppression of the zeta zeros' pair-statistic block variance matches a
parameter-free prediction from Conrey–Snaith's four-point correlations (conditional on the ratios conjecture):
measured/predicted shrink = 1.01 [0.89, 1.14]; the zeros sit 16 SE below the sine-kernel value. The prediction was
publicly tagged before the test data was read."

Keep these limits in the write-up, as you already have:

It's conditional on the ratios conjecture, like R₂. A PASS is evidence for that conjecture's higher-order structure,
not a theorem about ζ.
The agreement is to about ±13%; nothing finer is supported.
There's one statistic and one taper. No height trend is claimed, and the two top files landing on opposite sides is
just what five files look like.

This is the right moment for the Zenodo release, as planned: Stage 1 (direction, fresh heights), the Stage 2
prediction tag, seal and PASS, the CS08 erratum, and the novelty paragraph with the revised Coram–Diaconis wording.
It's a complete, self-contained finding with a full audit trail.

From here, the open threads are route (a)'s spacing law on F3 (s ≤ 1.8), Phase 1, and the open leads: Coram–Diaconis's
lag-1 correlation and the non-decaying C(r).
```
- **Correction (mine):** the first findings draft (23f4c947) did *not* state the ratios-conjecture condition or the
  one-statistic, one-taper scope. Both were added with the headline in `ph2s2/PH2S_STAGE2_FINDINGS.md`.
- **Release metadata 2026.10.11** (CITATION.cff, .zenodo.json): adds Stage 2, the CS08 erratum and the novelty
  paragraph with the revised Coram–Diaconis wording. New references, each checked against its Crossref record:
  - Conrey & Snaith (2008), doi:10.4310/CNTP.2008.v2.n3.a1;
  - Coram & Diaconis (2003), doi:10.1088/0305-4470/36/12/302;
  - Platt (2017), doi:10.1090/mcom/3198, the F1 and F2 zero data.

## Note (not a decision round, 2026-10-11) — release done
- Will tagged and released v2026.10.11. The GitHub release fed Zenodo automatically.
- Verified: the tag is annotated on main merge 137590d5 and is on both remotes.
- Will asked what's next. My proposal: route (a) on F3, with the estimand (μ amplitude vs κ-type) as Will's call.
- *Renumbered at Will's instruction (thirty-second round).* This entry was first filed as the thirtieth round.

## Thirtieth round (Will, 2026-10-11) — route (a) GO, estimand μ

```
Route (a) (Will, round 30): GO step 1 — ζ p(s; E) at the F3 heights on spot,
with checks: n=2 part reproduces R₂ machinery; positivity / valid density on
s ≤ 1.8 at every height; ζ-side n≤4 truncation bound (not inherited from U(N));
prime-cutoff convergence at the sealed quantity itself. Tag the prediction
before any F3 decode.
Estimand (decision ii): μ, the amplitude of CS08's arithmetic lower-order
part (μ=1 full strength; μ=0 sine kernel). Fit window s ≤ 1.8, model
normalised over the window. Findings will also translate Phase 2's
CUE(N_eff) curve into an equivalent μ (descriptive, answers L2).
Order: L5 after route (a); L3 descriptive only. Phase 1 waits on the
D1–D6 draft upload.
```
- **Filed late.** This block first reached the session after the thirty-third round was written, which is why
  rounds 31–32 precede it in time of filing. Until then a placeholder stood here (0905c118), recorded only from the
  thirty-second round's description.
- **"Phase 1 waits on the D1–D6 draft upload"** was already met: rounds 31–33 are Will's decisions on that draft.
- **The window s ≤ 1.8** is the twenty-first round's; that round's U(N) gate also found no n = 5 term at 1.8. The
  ζ-side truncation bound asked for here is a separate check and is not taken from that gate.

## Thirty-first round (Will, 2026-10-11) — Phase 1 decisions D1–D6

```
Phase 1 decisions (Will, round 31):
Corrections: (1) §7 — USp/EC zeros already generated 10-10 (generation only);
seal pins those hashes; only the U family remains to generate. (2) §4 — with
φ̂ ⊂ (−1,1), SO(even)/SO(odd)/O have identical one-level densities: D(φ)
separates U / USp / orthogonal-family; even vs odd comes from first-zero laws.
D1: USp, EC = generated ranges (pinned). U = primitive COMPLEX χ mod prime
q ≤ 1000, conjugate pairs counted once; real χ belong to USp only. Add the
E₁₁ quadratic-twist family (DHKMS published value, route (b)).
D2: fit/test split = seeded random split stratified by conductor band (not
contiguous ranges). Fit statistic = central-vanishing count. Fallback (c) if
the fit set has < 30 central vanishings.
D3: Fejér-type φ, φ̂ = triangle on (−3/4, 3/4) for all families (inside all
proved ranges incl. Young's (−7/9, 7/9)); per-family maximal supports
descriptive.
D4: seal the NULL — peak_q shows no family dependence beyond the calibrated
RMT band; PASS iff differences stay within it. Wiring committed first.
D5: per-statistic z-distance from calibrated bands; combine D(φ) and first-
zero law by sum of squares; nearest type with separation margin ≥ 3, else
ambiguous. Verdict on pooled conductor range per family; bands descriptive.
D6: plain conductor scaling for main arms; DHKMS N_eff only in the excised arm.
```
- **Correction (2) checked:** on the Fourier side,
  - SO(even): Ŵ = δ + ½η;
  - SO(odd): Ŵ = δ − ½η + 1;
  - O: Ŵ = δ + ½;
  - here η = 1 on |u| < 1. On supp φ̂ ⊂ (−1, 1) all three are δ + ½, so they coincide. The draft's §4 classifier
    would have tried to separate them through D(φ); it is now corrected in `ph1/PH1_SEAL_DRAFT.md`.
- **The 10-10 generation was checked before the seal pins it:**
  - The χ_d set is exactly the 121,588 fundamental discriminants with 3 ≤ |d| ≤ 2·10⁵. This was counted
    independently from the definition; no zero was read.
  - Six of the 16 `chi_*.jsonl` chunks are empty, with sha256 e3b0c442…, the hash of an empty file. This is expected:
    chunks go by list index mod 16, and fundamental discriminants never fall in index classes {2, 6, 10, 11, 14, 15}.
  - Close-pair recheck: 0 mismatches for χ_d (2,323 rechecked) and for EC (3,983 rechecked).

## Thirty-second round (Will, 2026-10-11) — Phase 1 P1–P7; numbering

```
Round 32 (Will) — Phase 1 P1–P7:
P1 log-spaced conductor bands per family: accept.
P2 accept (mean lowest non-central scaled zero sealed; KS descriptive; extra-
   central-vanishing curves excluded from first-zero law, kept in D(φ); U: one
   sample per conjugate pair). Report excluded fraction per family/band.
P3 accept: margin ≥ 3 on difference of combined distances; G0 ≥ 99%.
P4 accept: size matched per member; ≥ 200 repeats per band.
P5 E₁₁ twists: (i) known answer — reproduce DHKMS on d ≤ 4·10⁵ (calibration,
   not evidence); (ii) test on fresh d > 4·10⁵ up to a limit declared from the
   probe's cost (~1 day on spot); cut-off = the one DHKMS §5.4 states explicitly.
P6 accept: N_eff for E₁₁ only; N_std per band for all EC.
P7 accept, plus: RMT draws through the identical pipeline, truncated to the same
   number of low zeros per member; per-pair bands set so the FAMILY-WISE
   false-fail rate is 5% (6 pairs), calibrated empirically on the draws.
Numbering: route (a) GO + μ estimand = round 30 (paste that block); the
release note is a non-decision entry.
```
- **Spot is down** after an ESXi crash, then a power issue. It stays down until Will is back. The probe, the U
  generation and the E₁₁ cost measurement wait for it.
- **P7's six pairs read as the four families of the RF null:** U, USp, EC ε = +1 and EC ε = −1. The E₁₁ twists are not
  in the RF null. This is flagged in the draft for Will to confirm.
- **Round 30:** Will's text did not reach this session. A placeholder is recorded above.

## Thirty-third round (Will, 2026-10-11) — Phase 1 P5, P7 family set, P8, P9

```
Round 33 (Will) — Phase 1:
P8 accept hybrid: first-zero law at conductor-matched size; D(φ) and peak_q
   calibration at a size covering the full data window (scaled height 8).
   Seal records why D(φ)'s calibration size exceeds matched N.
P9 accept: bands from ≥ 1,000 repeats; hold-out family-wise rate must land
   in 3.5–6.5% (correction 8.7% → 4.2–6.1% recorded).
P7 family set: U, USp, EC ε=+1, EC ε=−1 (6 pairs). E₁₁ even twists excluded
   (same type as EC ε=+1); they stay in their own P5 arm.
P5 cut-off: X′ = largest d with projected generation ≤ 24 h at the rate
   measured on spot, rounded down; declared in the seal before generation.
```
- **Round 30's block arrived with this round** and is now filed verbatim above, in place of the placeholder.
- **P5 has two cut-offs, and this round settles one.** It fixes the range limit X′. The draft's open P5 item was the
  other one: DHKMS §5.4's low-lying cut-off, 0.5916·e^{−N_std/2}, stated at N_std = 12 (X = 4·10⁵). Whether the fresh
  range recomputes N_std from X′ (proposed) or holds 0.001466 fixed is still open. It has to be settled before the seal.
- **Readings to confirm, both in the draft:**
  - "Projected generation ≤ 24 h" counts the fresh range (4·10⁵, X′] only. The reproduction range d ≤ 4·10⁵ is
    generated separately.
  - "Rounded down" means to a multiple of 10⁵.
- **Spot** still refused ssh at the time of filing (connection refused on port 22).

## Note (not a decision round, 2026-10-11) — route (a) step 1 found a second CS08 erratum
- **What happened.** Route (a)'s spacing-law integrator (`cs4/route_a_zeta.py`) found the error before anything was
  tagged.
  - It evaluates ρ₄ with all four points inside a gap s ≤ 1.8. As two points merged, ρ₄^ζ tended to a negative
    constant.
  - CS08 counts distinct zeros, so ρ₄ is a density and must vanish there; ρ₂ and ρ₃ do.
- **Localised by an independent check** (`cs4/check_ratios_j.py`). Every J* was rebuilt from CS08's own
  ratios-conjecture definition by numerical mixed derivatives.
  - J₁₁, J₁₂ and J₂₂ match to ≤ 3.5e-16. This also confirms the earlier A* erratum and the B₄ reading.
  - J₁₃ is off by exactly −2 × its prime-sum term. CS08 prints that term with the wrong sign, in arXiv v1 and in the
    journal's eq. (5.36).
  - Under the twentieth-round rule it is recorded as an erratum: `cs4/CS08_ERRATUM.md` §4.
- **Fixed** in `cs4lib`, `cs4fast` (and so `cs4fastc`, `cs4lr`) and `cs4ref`.
- **Stage 2 (sealed, read, released) is unaffected.**
  - The correction has no constant part and oscillates in r at ≥ 0.39 per spacing, so the b ≥ 100 windows remove it.
  - Checked: the window integral is ≤ 2.7e-19, against v_B(100) ≈ 0.075 (`cs4/check_s13_stage2.py`).
  - Pointers were added the same day in `PH2S_STAGE2_FINDINGS.md`, `GS_ZETA_RESULTS.md` and `OPEN_LEADS.md` L3.
- **For Will:** the released v2026.10.11 carries `CS08_ERRATUM.md` without §4. Whether a new release should carry it
  is Will's call.

## Thirty-fourth round (Will, 2026-10-12) — route (a) rules, P5, erratum §4

```
Round 34 (Will):
1. Small-s skip: SKIP = 1e-8. Declared bound assumes ζ/sine ratio ≤ 100 (not
   the unproven ≤ 1) → ≤ 1e-6, ≪ bin resolution.
2. n=5 truncation: option (i) — construct ζ T₅ from the ratios-conjecture
   definition (extend check_ratios_j.py) at the edge nodes. GATE first: the
   same construction's U(N) analogue must reproduce exact CUE T₅ from the
   determinant. If the gate fails or cost runs away → fallback (ii) s ≤ 1.6,
   recorded as a forced change to round 30's window.
3. P5: recompute N_std from X′ (DHKMS formula carries over, not the value
   0.001466); state this in the seal.
4. Erratum §4: re-release after the Stage 2 recompute regardless of outcome.
   Rewrite §4.1 around the recompute; update L3's C(r) note; publish new
   Zenodo version. If the recompute moves any sealed value beyond 1e-3, the
   findings say so plainly per round 33's rule.
```
- **Context:** the J₁₃ sign error was in our code (transcribed as printed), and that code computed the sealed Stage 2
  prediction. The full recompute (`cs4/run_gs_zeta_fix4_spot.sh`, output `results/gs_zeta_fix4`, the sealed outputs
  untouched) started 2026-10-12 00:12 on spot. Route (a)'s term run is paused for it: 10 of 408 jobs are kept, and it is
  restartable.
- **"Round 33's rule" in item 4:** this reads as Will's rule of 2026-10-12, given just before this round ("if it's larger,
  the sealed prediction was wrong, and the findings have to say so plainly, whatever it does to the verdict"). The
  thirty-third round was Phase 1 only.
- **Item 1 also covers T₃ at s = 0.03**, which SKIP = 1e-12 still evaluated inside the cancellation-prone region.
- **Applied** in `cs4/route_a_zeta.py` (SKIP = 1e-8, SKIP_RATIO = 100; also enforced at merge, so the 10 jobs done under
  1e-12 stay valid). On the sealed nodes it skips T₃ for s ≤ 0.07 and T₄ for s ≤ 0.45.

## Note (not a decision round, 2026-10-12) — overnight results
- **Stage 2 recompute with the J₁₃ fix:** all 256 tasks exited 0. Compared with the sealed values against Will's 1e-3
  budget (`cs4/compare_fix4.py`), the largest change is 1.2e-9: per-file ĝ_B ≤ 3.4e-10, pooled 0.6830255987 →
  0.6830255986, ρ₁ ≤ 7.6e-10, z_pool unchanged. The PASS stands.
- **Item 2 gate (U(N) T₅ by the ratios construction against the determinant):** PASS at all 20 node/N pairs, max
  |diff| 4.8e-15.
- **ζ T₅ run:**
  - Run 1 was stopped after 7.5 h with no job finished. Will's two checks: spot is not oversubscribed (56
    single-thread workers on 56 vCPUs), and the run was under half done.
  - Run 2 uses the 1.8× faster code, as 54 single-job tasks, heaviest first.
- **Route (a):** resumed on all 40 chunks.

## Thirty-fifth round (Will, 2026-10-12) — item 1, re-release

```
Round 35 (Will), item 1 — Re-release: GO. Draft the findings note; rewrite
erratum §4.1 around the recompute (max change 1.2e-9; exact-integral
suppression ~e⁻²⁴⁰ vs pipeline ~1e-9 grid/NUFFT noise); update the L3 note;
prepare the Zenodo metadata. Will publishes.
```
- **Done:**
  - the post-release note in `ph2s2/PH2S_STAGE2_FINDINGS.md`;
  - `cs4/CS08_ERRATUM.md` §4.1 rewritten around the recompute, plus the header line on which release carries §4;
  - the `cs4/GS_ZETA_RESULTS.md` note;
  - the `OPEN_LEADS.md` L3 note, with the recomputed C(r) RMS (+1.5e-6 to +5.4e-6, about 1e-4 relative);
  - `CITATION.cff` and `.zenodo.json` set to 2026.10.12, with the erratum sentence naming both errata and the
    recompute.
- **The ~1e-9 is attributed, not tested:** it is put down to the pipeline's grid and NUFFT floor, which is consistent
  with its own diagnostics (pair overlaps 1e-8, Fourier tails ~5e-6). This was not tested separately, and §4.1 says so.

## Thirty-sixth round (Will, 2026-10-12) — route (a): the n ≤ 5 model

```
Round 36 (Will): route (a) truncation → INCLUDE computed Δ₅ (n ≤ 5 model),
conditions before tagging:
(1) T₅ prime-cutoff check (p ≤ 1000 vs 3000) passes;
(2) declare the s-range where |T₅^sine| > 1e-7; confirm computed nodes span it;
    state the interpolation rule + its error bound;
(3) n = 6 truncation bound = |T₆^sine| (exact, from the determinant) × 100
    ratio cap; must be well below bin resolution at s = 1.8.
Record descriptively: low-height ζ correlations behave like CUE with N ≈ 4
(ρ₅^ζ/ρ₅^sine ≈ 1e-4 at ℓ = 14.8, rising to 0.83 at ℓ = 67); small negative
∫ρ₅^ζ ≈ −3e-9 noted as asymptotic slack with its size. Do not pre-judge the
relation to Phase 2's L2 result; route (a)'s prediction decides it.
```
- **(1) The criterion, declared by me** (Will said "passes" without setting a number):
  |Δ₅(p ≤ 3000) − Δ₅(p ≤ 1000)| ≤ 1e-6 at every checked node, i.e. 100× below the ~1e-4 bin resolution.
  - The checked nodes are the outermost and one inner edge node, at the lowest and highest F3 heights. The result is
    applied to all five heights.
  - Code: `cs4/ratios_t5.py` merge (`CUTOFF_TOL`). This is open to Will's change.
- **(2) The range:** |T₅^sine| > 1e-7 for s > 1.2895 (bisection on the determinant). The computed Δ₅ nodes are the ten
  Chebyshev–Lobatto nodes 1.2444, 1.35, 1.448, 1.536, 1.614, 1.679, 1.731, 1.769, 1.792 and 1.8, so they span it with
  one node below.
  - Below the edge nodes, |T₅^sine| < 1e-8 and the round-34 bound applies: 100·|T₅^sine| ≤ 1e-6.
- **(2) The interpolation rule:** the n ≤ 5 Δp is fixed at the 25 Chebyshev–Lobatto nodes on [0, 1.8] and carried to
  the fit grid (Δs = 0.001) by barycentric Chebyshev interpolation.
  - The error estimate is the largest of the last three Chebyshev coefficients (`cheb_tail`).
  - The conservative check is the 13-node subset interpolant against the 25-node values at the odd nodes.
  - Both are reported per height in `results/route_a_zeta.json`.
- **(3) The n = 6 term,** exact from the determinant: |T₆^sine| = 1.427e-9 at s = 1.8 (4.1e-11 at 1.6). With the ×100
  cap the bound is 1.4e-7 at s = 1.8, about 700× below the bin resolution.
  - The declared limit is TRUNC_MAX = 1e-5 on the window.
- **Code:** `route_a_zeta.py` merge (check (c) is now the n ≤ 5 model). It refuses to run without `results/ratios_t5.json`.
  - Its PASS requires all three conditions.
  - On a toy input whose computed nodes do not span the range, it FAILs: this is the red path.
- **Descriptive record:** low-height ζ correlations behave like CUE with N ≈ 4.
  - At the point (0, 0.45, 0.9, 1.35, 1.8), ρ₅^ζ/ρ₅^sine = 1e-4, 0.19 and 0.83 at ℓ = 14.8, 25.8 and 67.
  - CUE_N matched on ρ₄ at the same points (N ≈ 4, 6, 15) gives ρ₅ ratios of about 0.03, 0.33 and 0.86.
  - At s ≤ 1.35 (ℓ = 14.76), ∫ρ₅^ζ comes out slightly negative, about −3e-9 (T₅^ζ = +5.7e-10 and +4.2e-10). This is
    noted as the conjecture formula's asymptotic slack. It is far below any resolution here.
  - The relation to Phase 2's L2 result is not pre-judged; route (a)'s prediction decides it.

## Note (not a decision round, 2026-10-12 evening) — compute after the brownout
- **The 17:40 brownout reboot.**
  - Lost: the in-progress T₅ jobs (~90 core-hours) and route (a)'s in-progress jobs.
  - Kept intact: 12/54 T₅ and 227/408 route (a) results; all 61 pinned data files re-verified.
  - T₅ is now checkpointed per batch, bit-identical on resume (ckpt_selftest).
- **Second box (char@10.0.0.31; Will: same rules as spot):** i5-6600K, 4 cores, about 5.6× a loaded spot worker; RTX 3080
  working after Will's reboot.
- **T₅ split:** spot runs jobs 12–26, char runs 50–53 and 27–49.
- **Route (a) on GPU** (`cs4/route_a_gpu.py`): 15–31 s per job. On eight finished s = 1.8 jobs it agrees to ≤ 1.7e-12
  absolute (≤ 5e-11 relative). That fails the 1e-12 tolerance declared beforehand. **Will chose CPU instead.**
- **Route (a) on CPU across machines** (`cs4/route_a_jobs.py`; same long-double code path):
  - 168 jobs remained. A static, disjoint, cost-weighted split gives spot 54 jobs plus its 40 in progress (its pool
    retires each legacy chunk worker by PID after it writes), this machine 51 (6 workers, CS4_CHUNK = 16, 3 GB
    per-process cap, MemAvailable watchdog at 2 GB), and char 23 (queued after its T₅ share).
- **Cross-machine reproducibility is not bitwise, even on CPU.**
  - A finished spot job (s = 0.9) recomputed here agrees exactly in T₂ and T₃; T₄ differs by 7.2e-16 absolute.
  - The cause is a different CPU and Python build: double rounding.
  - The same holds for char's T₅ share against spot's. The GPU differences (≤ 1.7e-12) are the same kind, about 10³
    larger.

## Will, 2026-10-12 evening — compute choices (filed as stated)
- "go with CPU, 6 workers here" (after the GPU validation narrowly failed its declared 1e-12).
- Asked whether everything should run on spot, since a change might need a full rerun for the seal. The answer given:
  nothing sealed requires one machine, and spot alone would not be bitwise-reproducible elsewhere either. Will's
  decision: **"keep the split, add the cross-machine check".**
- **The check (`cs4/xcheck.py`, declared before it runs):**
  - Spot-computed jobs are recomputed on this machine and on char: route (a) terms on both, T₅ on char (p ≤ 1000).
  - Every quantity must agree with spot's to ≤ 1e-12 absolute.
  - The route (a) merge will require its PASS before tagging. That gate is added to `route_a_zeta.py` only after T₅
    finishes, because the file is in T₅'s checkpoint code hash.
- **Measured so far:** one spot route (a) job recomputed here: T₂ and T₃ exact, T₄ 7.2e-16.
- **Checkpointed T₅ code reproduces a finished run-2 value bit for bit on spot** (job 0: 5.669071673075182e-10, both
  times; recheck finished 2026-10-12 ~22:40). The 12 run-2 results and the checkpointed results are therefore from an
  identical code path on spot.
- **Rebalance (2026-10-12 23:55).**
  - T₅: spot's share (jobs 12–26) finished, all 15 exits 0; 27/54 T₅ rows are on spot.
  - Route (a): this machine finished its 51 jobs (23:10). Char's 23 had not started (char is still on T₅, 12/27), so
    its queued pool was cancelled by PID and the list moved to this machine (6 workers, same caps and watchdog).
  - Spot's remaining 29 jobs stay where they are (running, and not checkpointed).
- **Idle spot cores used for Phase 1 P5(i) (2026-10-13 00:22):**
  - Zeros of the E₁₁ even twists over the DHKMS reproduction range d ≤ 4·10⁵ (8,431 twists).
  - Generation only, with no statistic computed; independent of X′.
  - `ph1/run_gen_e11_repro_spot.sh`: 64 chunks on 48 workers, while route (a) has 4 jobs left on spot.
  - The X′ cost probe still waits for an idle spot.
- **Cross-machine evidence from duplicated jobs (2026-10-13 00:38; Will: record it as evidence, not just waste).**
  - **How the duplicates arose:** the job lists were split a few minutes before spot's pool started. In that gap
    several legacy chunk workers finished their current job and began the next, which the split had assigned to this
    machine. Those ran to completion on both machines.
  - **Spot vs this machine:** 5 route (a) jobs (289, 313, 314, 360, 364) were computed independently on spot (Intel
    Xeon E5-2690 v4, Python 3.12.15) and on this machine (AMD Ryzen 9 5900X under WSL, Python 3.12.3), both on numpy
    2.5.3 / scipy 1.18.1 / mpmath 1.4.1. T₂, T₃ and T₄ (ζ) agree **bit for bit, difference exactly 0**, on all five.
  - **Spot vs spot:** job 365 ran twice on spot (legacy worker and pool), identical.
  - **Not always bitwise:** the deliberate recompute of a spot job here (s = 0.9) differed in T₄ by 7.2e-16. Cross-CPU
    results are mostly bitwise, sometimes 1 ulp-scale.
  - **Char not yet covered:** these overlaps are spot vs this machine only. Char (i5-6600K, Python 3.14) has no overlap
    yet; the declared check (`xcheck.py`, ≤ 1e-12) will cover it.
  - **Merge:** keys on the job, so the duplicates are harmless. These six pairs are added to the cross-machine evidence.

## Thirty-seventh round (Will, 2026-10-13) — route (a) prediction approved, conditional

```
Round 37 (Will): route (a) prediction APPROVED, conditional on the new-box
cross-machine recompute passing (bit-identical or within declared float bound).
- Truncation: governing bound = node-set 6.7e-7 (> n=6 bound 1.4e-7); record.
- Record descriptively: ρ₅^ζ ≈ 0 at all F3 heights (|Δ₅|/|T₅^sine| = 0.99–1.01);
  n≤5 model mainly removes the sine kernel's own 5-point term.
- State the prediction's definition (file-averaged Δp vs Δp at zero-weighted
  mean height) matching the read's estimator; δμ ≈ 1e-4 noted.
- After cross-check: tag `route-a-prediction`, push before any F3 download;
  then pre-read (GUE calibration, power, rule; Phase 2 CUE(N_eff) → equivalent
  μ, descriptive) → seal → F3 read.
- Spot idle now: run the E₁₁ X′ cost measurement and worker-count probe.
```
- **The truncation bound that governs: 6.7e-7.** This is the node-set bound: 100·|T₅^sine| at the nodes below the
  computed edge (s ≤ 1.13), where Δ₅ is not computed. It is larger than the n = 6 bound at s = 1.8 (100·|T₆^sine| =
  1.4e-7). Its worst-sign effect on μ is ≤ 1.2e-5.
- **Descriptive: ρ₅^ζ ≈ 0 at all five F3 heights.** |Δ₅|/|T₅^sine| = 0.99–1.01 at every height
  (`results/ratios_t5.json`), so ζ's own 5-point term is about zero on the window. Including Δ₅ (the n ≤ 5 model)
  therefore mainly removes the sine kernel's own 5-point term from p_μ's arithmetic part. Its effect on μ is
  δμ = −1.0e-4 to −1.5e-4.
- **The prediction's definition.**
  - **What is computed:** for each F3 file, Δp(s) is evaluated at the file's zero-weighted mean height ℓ̄
    (`zero_weighted_t`: ∫ℓ² dt/∫ℓ dt over the file's declared range).
  - **What the read estimates:** the read pools a file's spacings into one histogram. Each spacing sits at its own
    height, and their number grows with the zero density ∝ ℓ, so the histogram's expectation is the zero-weighted file
    average of p(s; ℓ).
  - **The gap is second order in the file's ℓ spread:**
    - Measured at the widest file (zeros_15146000, ℓ 14.695–14.825, zero-weighted Var ℓ = 1.40e-3) by the
      three-height average (t₀, ℓ̄, t₁): δμ ≈ +1.0e-4.
    - Scaled by Var ℓ to the others: ≈ +3.7e-5 (zeros_25646000, Var 5.2e-4), ≈ 4e-7 (zeros_248246000), ≈ 5e-9
      (zeros_2373446000) and ≈ 2e-10 (zeros_10639046000). These are estimates; only the first is computed.
  - **Sealed form:** the mean-height Δp, with this file-average gap stated as a known bias of at most ~1e-4 in μ.
    The seal can require the file average instead; that would mean computing the end heights for the second file.
- **E₁₁ reproduction range, generated (2026-10-13 03:26):** d ≤ 4·10⁵, 8,431 twists, 68,950 zeros; close-pair recheck
  0 mismatches in 192; 64 chunks, all exits 0 (`ph1/results/zeros_e11_repro_MANIFEST.json`). Wall time 3.07 h at
  48 workers, about 48 s per twist on average.
- **X′ measurement started on an idle spot (09:00; round 37)** with `ph1/run_e11_probe_spot.sh`:
  - a worker-count probe at d ≈ 10⁶ (P = 16, 28, 40, 56);
  - then a cost curve at the best P (d ≈ 0.5, 1, 1.5, 2·10⁶);
  - X′ = the largest d with projected generation ≤ 24 h, rounded down to 10⁵ (`ph1/e11_probe.py project`).

## Thirty-eighth round (Will, 2026-10-13) — the prediction's definition; systematic allowance

```
Round 38 (Will): prediction definition = Δp at each file's zero-weighted mean
height. Declare systematic allowance δμ_sys = 2e-4 for the mean-height vs
file-average gap (from the widest file's measured 1.0e-4 + second-order scaling
for the others); no exact file-average computation needed. Then cross-check →
merge → annotated tag `route-a-prediction` (Will pushes) as planned.
```
- **Applied:** `cs4/route_a_zeta.py` merge records `DMU_SYS = 2e-4` and its basis in `results/route_a_zeta.json`
  (`definition`, `delta_mu_sys`).
- **Cross-machine check: PASS (2026-10-13 ~09:10).** 16 comparisons, all identical to spot to the bit (difference
  exactly 0); declared tolerance 1e-12 (`cs4/results/xcheck.json`):
  - 6 recomputed on char (i5-6600K, Python 3.14): 3 route (a) jobs and 3 T₅ jobs;
  - 9 jobs duplicated between spot and this machine;
  - 1 job duplicated within spot ("fedora" is spot's hostname).
  - The deliberate local recompute of 2026-10-12, in a different environment, differed by 7.2e-16 and is noted above.
- **Merge rerun: TAGGABLE = True.** Per-height checks (a)–(c) pass, the cross-check passes, and δμ_sys = 2e-4 is
  recorded.
- **Raw inputs committed** (`cs4/results/route_a_raw/`, 224 files) with `cs4/results/route_a_prediction_MANIFEST.json`.
  The manifest holds sha256 for the raw files, the 9 code files and the 6 merged outputs. Rebuilding the merge from
  the committed raw files gives a byte-identical `route_a_zeta.json`.
- **`route-a-prediction` pushed by Will (2026-10-13)** to both remotes. Verified: the annotated tag 0d2ac239 points to
  0f0c5f77 on GitHub and on Forgejo, and both branches are at 0f0c5f77. No F3 file had been downloaded before this.
- **E₁₁ X′ measurement (2026-10-13, spot otherwise idle; `ph1/results/e11_probe/`).**
  - **Worker-count probe at d ≈ 10⁶:**
    - P = 16: 188 s per twist, about 306 twists/h.
    - P = 28: 197 s, about 512/h.
    - P = 40: 252 s, about 571/h.
    - P = 56: **exhausted spot's 117 GB** (about 09:25). The memory killer took down the whole user session, including
      tmux and the desktop greeter. Spot recovered by itself; no data was lost. This was my error: worker count was
      raised without measuring memory per worker.
  - **Peak RSS of one worker:** 2,993 MB at d ≈ 10⁶ and 3,045 MB at 1.5·10⁶. Memory, not CPU, bounds the run:
    **P = 30** (≈ 90 GB, 77% of RAM) is the memory-safe count. A memory guard ran alongside and never fired.
  - **Cost curve at P = 30** (30 twists each): 102, 233, 355 and 485 s per twist at d ≈ 0.5, 1, 1.5 and 2·10⁶. Fit:
    t(d) = 4.12e-5·d^1.123 s.
  - **Projection:**
    - Timed main computation only: largest d within 24 h is 1,204,097, so X′ = 1.2·10⁶ (14,730 twists, 23.8 h).
    - The production run also recomputes a random 2% at divz 128, which the probe did not time. Counting it as a 4–5%
      overhead, the largest d within 24 h is about 1.18·10⁶, so **X′ = 1.1·10⁶ (12,917 twists, projected about 20.3 h
      at P = 30).**
  - **Proposed:** X′ = 1.1·10⁶, since the round-33 rule's "projected generation" should include the production
    recheck. Will declares X′ in the seal before generation.
- **F3 downloaded by Will (2026-10-13, ~13:55), after `route-a-prediction` was pushed.**
  - All five files match their pinned md5s, both here and on spot after the copy:
    zeros_15146000 12759c6b…, zeros_25646000 17769568…, zeros_248246000 763374d8…, zeros_2373446000 10af7827…,
    zeros_10639046000 6203cd45….
  - No file has been decoded. The pre-read (GUE calibration, power, rule, Phase 2 CUE(N_eff) as an equivalent μ) and
    the seal come first.

## Will, 2026-10-13 evening — X′ and the fresh-range generation
- **UPS swap:** Will swapped the UPS. Spot came back; its VM was started by hand. All 128 pinned files re-verified on spot:
  the Phase 1 χ_d, EC, U and E₁₁-reproduction chunks, and the F1/F2/F3 Platt files.
- **Spot is now off the battery-backed side** (Will). The generation is checkpointed per twist, so a power loss costs
  only the twists in progress.
- **X′ declared before generation.** Will said to start the compute after the proposal above; this is recorded as
  accepting it:
  - **X′ = 1.1·10⁶**: 12,917 fresh twists in (4·10⁵, 1.1·10⁶], projected ≈ 20.3 h at P = 30, including the 2% recheck.
  - The two readings stand: rounded down to a multiple of 10⁵, and the 24 h counts the fresh range only.
- **P5 low-lying cut-off on the fresh range** (thirty-fourth round: the DHKMS formula carries over):
  - N_std = log(√11·X′/2π) = 13.272;
  - cut-off 0.5916·e^{−N_std/2} = 7.76·10⁻⁴.
  - The value 0.001466 applies only to the reproduction range (N_std = 12).
- **If Will meant a different X′:** the twists already computed carry over (same code path per twist).

## Thirty-ninth round (Will, 2026-10-13) — X′ declared (verbatim; filed late, 2026-10-13 evening)
Round 39 (Will):
- X′ = 1.1·10⁶ DECLARED (fresh range (4·10⁵, 1.1·10⁶], ~12,917 twists,
  ~20.3 h at 30 workers incl. the 2% recheck). "Rounded down" = multiple of
  10⁵; the 24 h budget covers only the fresh range.
- Commit this declaration (decisions log + Phase 1 seal draft) BEFORE
  launching generation; the Phase 1 seal pins it when sealed. Generation
  only — no statistics before the seal.
- Launch after Will's UPS swap (spot idle now = ideal window); if the swap
  must happen mid-run, stop workers cleanly first.
- Route (a): proceed with the GUE-only pre-read → seal → F3 read.

- **Filing note:** this round was lost from my context when the session was compacted. The section "Will, 2026-10-13
  evening — X′ and the fresh-range generation" above recorded the same X′ as accepted from "start the compute". Will
  re-sent the text, and it is filed here verbatim.
- **Compliance check:**
  - The declaration was committed (0911b876, 16:23:02) before the launch (16:23:03, spot log).
  - The Phase 1 seal draft (v6) carries X′. It is a DRAFT, so it is not in git.
  - Generation only: no statistic has been computed on the fresh twists.
  - The launch came after the UPS swap. Spot is now off the battery side, so if power is cut mid-run, the twists in
    progress are lost and every finished twist is kept (checkpointed per twist).

## Fortieth round (Will, 2026-10-13 evening) — route (a) pre-read guidance (verbatim)
Route (a) pre-read guidance (Will, round 40):
- GUE calibration through the identical pipeline: CUE (N ≥ 10³ per block) mapped
  onto each F3 file's density, unfolded back with exact θ; expect μ̂ ≈ 0.
- Red path = declared goodness-of-fit test (KS or binned χ² vs p_μ̂ in-window),
  threshold calibrated on CUE; non-p_μ families read "model misfit".
- Order: draft + commit the rule from GUE power BEFORE any real-zero check;
  then seen Phase 2 bins as a descriptive pipeline/SE check only.
- Draft rule (by analogy with Stage 2): fixed pre-data weights ∝ spacing count;
  RESOLVABLE iff 2·SE_pool ≤ 0.25; PASS iff |μ̂_pool − 1| ≤ 2·SE_pool + δμ_sys
  AND ≥ 4/5 files within 3 SE of 1; seal records the empirical false-fail rate
  and power (assumption: μ=1 correlations ≈ μ=0); report μ̂_pool ± CI always.

## Forty-first round (Will, 2026-10-13 evening) — route (a) rule additions before commit (verbatim)
Round 41 (Will) — route (a) rule additions before commit:
- Defaults accepted: binned χ² (36 bins) GOF; per-file thresholds from CUE
  replicates for 1% family-wise false misfit; block length = shortest of
  {300, 1000, 3000, 10000} with bootstrap SE ≥ 0.95 × replicate spread.
- Bias: from the 200 replicates; declare pre-data either subtraction (with its
  uncertainty propagated) or inclusion in the allowance.
- SE = max(CUE replicate spread, zeros' own block-bootstrap SE at the selected
  and longer block lengths) — as Phase 2's A1.
- Verdict precedence: PASS requires the μ condition AND GOF pass in ≥ 4/5
  files. Misfit flagged in ≥ 2 files → verdict MODEL MISFIT; μ̂ reported
  descriptively with misfit location from the χ² bins.
- L2 translation table stays descriptive.
Commit the rule before any real-zero check; then Phase 2 bins descriptive.

**Implementation (route_a_read.py docstring + rule(); route_a_calib.py declare()), committed before the calibration
finished and before any real-zero check:**
- Bias: **subtracted**, declared now, whatever the replicates show: μ̃_f = μ̂_f − b_f, SE_f² += SD_f²/R_f (R = 200 →
  SE × 1.0025). Unconditional (no significance branch), so nothing about the handling depends on the calibration data.
- SE_f = max(SD_f, SE_boot,f(L) for every L ≥ BLOCK), then the bias term above.
- Block criterion, one refinement for Will to confirm: "SE_boot ≥ 0.95·SD" is applied to the **geometric mean over the
  five files** of SE_boot(L)/SD_f, not file by file. Reason: SD_f's own sampling error at R = 200 is ±5%, so a perfectly
  calibrated bootstrap fails "≥ 0.95 in every file" with probability ≈ 1 − 0.84⁵ ≈ 58%; the five-file mean (±2.2%)
  fails it ≈ 1%. No L qualifying → BLOCK = 10⁴ (declared fallback); SE_f ≥ SD_f per file holds either way.
- GoF threshold T_f: (1 − α₁) quantile of a·χ²_ν matched to the replicates' χ² mean and variance, α₁ = 1 − 0.99^{1/5};
  the empirical family-wise rate and the empirical vs fitted q90/q99 recorded beside it.
- Precedence: MODEL MISFIT (≥ 2 files over T_f) > UNRESOLVED (2·SE_pool > 0.25) > PASS / FAIL; PASS also needs ≥ 4/5
  files under T_f (implied once MODEL MISFIT is excluded). Misfit location: per-bin (O − E)/√E (MuFit.gof_detail).
- rule_selftest (`route_a_read.py ruletest`): every verdict fires on a constructed input, the precedence holds, bias
  subtracted, SE floored at SD and widened by SD/√R. PASS.
- Operating characteristics from the joint replicates (declare): false-fail = P(≠ PASS) with μ̂ + 1; power = P(FAIL) at
  μ = 0; descriptive only, P(≠ PASS) at Phase 2's fitted-SECONDARY μ* (μ condition only).

**Sampler defect found and fixed the same evening (calibration restarted).** The pipeline check's Platt writer refused a
negative step: cbe's GPU roots had 47 spacings ≈ −1e-13 in 4.9M (≈ 1% of N = 1000 matrices). The real-form Newton step
(cbe.py, introduced for speed) solves sin(f/2)·|Φ*| = 0, which vanishes at every root; when two roots share a grid
bracket a slot could converge to its neighbour (f = ±2π), doubling it and missing its own. The self-test's V1 (dense
comparison on 38 matrices) was too small to see a 1%-per-matrix event. Fix: a root is accepted only on its own branch
(|f| < 1; a visit to a neighbour just shrinks the sign-kept bracket), and every matrix is certified (roots strictly
increasing within one period; certify() raises). (A first fix, real-form step only while |f| < π, was also correct but
~1.75× slower per GPU warp; replaced the same evening, same roots to 1e-13, before any calibration row was kept.) The re-run self-test then stalled at β = 1 (8 roots not converged): where ψ′ reaches ~1e16 no double θ
has |f| < 1 and the step rounds back onto θ; such a stalled step now bisects, and a root is also accepted once its
sign-kept bracket (which always holds root m alone) has collapsed to 4 ulp (θ to machine precision). New V4: no spacing < 1e-3 on 10⁴ N = 1000 matrices (CUE expectation ~0.01), red path = the old
step on the same α must double roots. The 12 replicates and 3 pipeline checks run before the fix are set aside on char
(results/calib/defective_dup_roots/), not used.

## Forty-second round (Will, 2026-10-13 night) — block criterion and bias accepted; sampler-defect log (verbatim)
Round 42 (Will): block-length criterion = geometric mean of the bootstrap/
replicate SE ratio over the five files ≥ 0.95 (fallback 10⁴); per-file SE
floored at its replicate spread. Bias subtraction (unconditional) accepted.
Log: confirm no sealed result used cbe.py (Stages 1–2 and Phase 2 used
separate generators); record that the Platt writer's negative-gap refusal
caught the sampler defect, and that the false-pass self-tests were fixed.

**Log record (2026-10-13 night):**
- **No sealed result used cbe.py.** cbe.py was first committed in a2203384 (2026-10-13); `git tag --contains` lists no
  tag (ph2-seal-2.1, ph6-seal-6.0, ph6.1-seal, ph2r2-seal, ph2s-stage1-seal, ph2s-stage2-prediction, ph2s-stage2-seal,
  route-a-prediction all predate it). Its only importers are cs4/route_a_calib.py and cs4/route_a_read.py (route (a)
  pre-read, unsealed); no other file mentions Verblunsky/Killip/Prüfer. The sealed stages' CUE draws came from separate
  dense generators (Haar by QR + eigvals, Mezzadri): Phase 2 ph2lib.haar_unitary_phases / cue_spacings, R₂
  ph2r2/g0b.cue_block, Stage 2 cs4/gs_cue_mc.haar_phases; Phase 2's CUE_N laws are Fredholm tables (ph2lib), not samples.
  route_a_zeta.py and route_a_equiv.py (the tagged prediction and the L2 table) do not import cbe.
- **What caught the defect:** the Platt writer (route_a_read.write_platt) refused a negative gap while the full-size
  pipeline-identity check wrote CUE levels for zeros_15146000 (struct.error at zero 424,122: a doubled root, spacing
  −1.4e-13). The writer now raises an explicit ValueError for any step outside (0, 2^104). The sampler's own V1 (38
  matrices against dense eigvals) was too small to see a ~1%-per-matrix event; V4 (10⁴ matrices, red path) now covers it.
- **False-pass self-tests fixed:** `cbe.py selftest` and `route_a_read.py selftest / ruletest` exited 0 whatever their
  verdict (the earlier `exit=0` recorded on char for the cbe self-test therefore certified nothing beyond "no crash");
  each now exits on its verdict, and `cbe.py check OUT.json` verifies a recorded run in full (a tampered record is
  refused). Commits fd143231, ef7119f4.
- Implementation already matches round 42 (route_a_calib.declare; route_a_read.file_se); no code change.

## Forty-third round (Will, 2026-10-14 morning) — calibration accepted; sensitivity split and outcome table before the seal (verbatim)
Route (a): keep the rule and the PASS band unchanged. Before the seal:

Data-free sensitivity split. Recompute the route (a) prediction on the declared statistic with (i) n = 2 terms only, with higher orders from the sine kernel, and (ii) the full n ≤ 5 terms. Report the difference in μ-equivalent units against the ±0.015 band. If the n ≥ 3 terms move the statistic by less than about 0.25 of the band, record in the seal that route (a) tests two-point structure only. Estimate the cost first. Run it on char now if it takes ≤ a few hours; otherwise flag it to me and we seal with the reading marked conditional.
Pre-declared outcome table in the seal:
(a) μ̂ in the band → PASS.
(b) μ̂ in about [0.955, 0.985] → FAIL, read as “spacing law deviates from CS n≤5 at μ = 1, in the direction of Phase 2’s fitted law”. Since R₂ μ̂ = 1.003 ± 0.006, attribute to n ≥ 3 / truncation / estimator, weighted by the item 1 split. A follow-up to separate these is pre-declared.
(c) any other μ̂ → FAIL, unattributed.
MODEL MISFIT is reported independently of all three.
Calibration notes for the record, no change needed. The false-misfit rate of 3/200 against an expected 2 is binomially unremarkable. The lowest-file bias (z up to 2.4) is subtracted per file, as declared.

Then continue in order: Phase 2 bins check on char → seal draft to me → OpenTimestamps-stamp the seal → F3 decode. E₁₁ close-out when it finishes (~10:00–10:30) as planned.

## Forty-fourth round (Will, 2026-10-14 morning) — cumulant cut before the seal; n = 5 presence check; outcome (b) attribution (verbatim)
Round 44:

Cumulant cut, before the seal. Data-free. Compute pooled μ* for:
C2: T₂ from ζ; T₃, T₄, T₅ from the sine kernel.
C3: T₂ and T₃ from ζ; T₄ and T₅ from the sine kernel.
C4: T₂–T₄ from ζ; T₅ from the sine kernel.
C5: everything from ζ. It must reproduce 1.000, as the gate.
Report each increment and how it compares with the ±0.016 band.
The n = 5 term really is in the sum (this guards against a silently dropped term). Report the n = 5 block increment in μ* to full precision, and the size of ρ₅^ζ − ρ₅^sine at a few quadrature points, so we can see the correction is non-zero and that the term actually enters the sum. If the n = 5 increment is ≪ the band and the decay is consistent, state in the seal that truncation is excluded from attribution, and give the bound used.
Seal outcome (b) attribution:
Weight the attribution by the cumulant increments from item 1, not the block cut.
Attribution candidates: pair arithmetic (C2 share), connected higher-order (C3–C5 shares), estimator.
Truncation is listed only if item 2 fails to exclude it.
The gate-tolerance change is accepted as documented: it is pre-data, and the integrator offset was already on record.

Order is unchanged: bins check → seal draft to me → OpenTimestamps stamp → F3 decode. E₁₁ close-out when the exits land.

## Forty-fifth round (Will, 2026-10-14 midday) — cut validity; R₂-anchored attribution bound; read environment (verbatim)
Round 45:

Cumulant cut. Let it finish. Add a validity check: for each cut model, check positivity of ρ₃–ρ₅ and of p(s) on the quadrature grid. If a model is non-positive anywhere, or the increments alternate rather than decay, report it as “not a valid decomposition at N_eff ≈ 3.4” and don’t use it for weights.
Primary attribution route: an R₂-anchored bound.
Compute ∂μ*/∂μ₂, where μ₂ scales only the T₂ arithmetic correction wherever T₂ appears, including inside ρ₃–ρ₅, with T₃–T₅ held at their CS values. Use a symmetric finite difference at ±0.01 and confirm it is linear.
Bound the pair-level effect: B₂ = |∂μ*/∂μ₂| · (|1.003 − 1| + 2 × 0.006), using R₂ at its own heights. State that μ is assumed to be a height-independent amplitude.
Seal outcome (b): a deviation |μ̂ − 1| > B₂ (and outside the band) is attributed to connected n ≥ 3 structure or to the estimator. Within B₂, it is consistent with pair-level uncertainty.
Truncation: excluded, with the bound ≤ 1.2e-5 cited.
Environment for the real read.
Pin the Python, numpy and scipy versions in the seal.
Run the dry run and the real read under that interpreter.
Run the real read twice and require bit-identical outputs; any mismatch voids the run before interpretation.
Log the P6 segfault as an environment incident.
MODEL MISFIT reading confirmed as you have it: the row is always reported beside the verdict, and precedence stays as sealed.
Order unchanged: cumulant cut + dry run → seal draft to me (blanks filled) → OTS stamp → F3 read (twice). Do the E₁₁ close-out when the remaining exits land.

**Environment incident (logged per round 45), 2026-10-14 09:47 PDT, char.** The Phase 2 bins check for P6
(`cs4/route_a_ph2bins.py`, zeros_30404246000.dat, 7.45·10⁶ spacings) died with a segmentation fault inside the
interpreter: kernel "python[31880]: segfault … error 4 in python3.14", exit 139, no core kept, no OOM event in the kernel log
(20 GB available when checked 12 minutes later). It ran 3 bins at a time beside an unrelated timing test. Interpreter: char venv, Python 3.14.4, numpy 2.5.3,
scipy 1.18.1, mpmath 1.4.1. Rerun alone with the same code and input: exit 0, output bit-exact against Phase 2's
arrays. Cause not determined. The first run's log is kept (`cs4/results/ph2bins/crash1/`). The dry run and the real read
run on spot (`ph6c`: Python 3.12.15, numpy 2.5.3, scipy 1.18.1, mpmath 1.4.1), which the seal pins; the read refuses any
other interpreter and must reproduce itself bit for bit.

## Forty-sixth round (Will, 2026-10-14 afternoon) — row (b) follow-up named; bounds; near-edge reporting (verbatim)
Round 46:

Row (b) follow-up, named in the seal:
Use an independent observable with its own estimator and the same CS n ≤ 5 model: the next-nearest-neighbour spacing law, or the third cumulant of the counting function. Choose by power, before seeing any route (a) result.
Before its seal, it needs its own data-free sensitivity split showing a majority of its arithmetic part from connected n ≥ 3 terms. Use the same R₂-anchored derivative method as B₂.
It runs on fresh zeros not yet downloaded, with a tagged prediction, an OpenTimestamps stamp and a separate seal.
Reading: both observables deviate in the predicted direction → connected structure. Only route (a) deviates → its estimator.
Detailed parameters may be sealed later, but before that data is downloaded. The seal commits to this logic now.
If route (a) PASSes, the same design runs as an independent replication.
Row (b) bounds stay at [0.955, 0.985].
Record in the seal the 90.5% capture rate under Phase 2’s fitted law, and that the bounds approximate μ_P2 ± 2 SE_pool.
(c) results within 0.005 of a (b) edge are reported with their distance and not reclassified.
B₂ attribution applies to every FAIL below the band.
Cut validity criteria accepted as you fixed them.
Fill the blanks once the dry run, the anchor run and the cumulant cut have landed. Then the draft comes to me → OpenTimestamps stamp → double read.

## Forty-seventh round (Will, 2026-10-14 evening) — go after two text fixes; F3 provenance; external-timestamp gate (verbatim)
Round 47: go, after two text fixes.

F3 provenance. Reconcile in writing:
your statement today that nothing from F3 has been downloaded or read;
the earlier record that F3 was downloaded and md5-verified, not decoded;
your 10/14 morning line “Pipeline identity: all five F3 files now round-trip exactly”.
State where every F3 file is now, on any machine, with timestamps, and what “round-trip” operated on. The seal’s provenance section records the true history: download date and md5 checks if they happened, and whether any F3 content was ever decoded. If anything was decoded, stop and report to me before sealing.
External-timestamp gate.
Add a refusal: the read verifies the prediction JSON’s sha256 against the OpenTimestamps-stamped manifest from f75e5816, independently of git.
Run ots upgrade and ots verify on that receipt. It must be complete before the seal is stamped. Record the Bitcoin block in the seal.
Add a red path for a prediction-hash mismatch.
Accepted as-is: B₂ and the §4 statement; the invalid cumulant cut reported descriptively; the bare-clone tag check; the launcher incident note (no recompute: all 360 jobs present, and the attribution margin is 4.9×).
Then: rename to ROUTE_A_SEAL.md → build on spot → Will commits, tags and pushes → OpenTimestamps-stamp the seal → F3 to spot (if it isn’t already there) → read twice → compare → report.

**F3 provenance audit (round 47; 2026-10-14 evening).**
- **Download (did happen).** Will downloaded the five F3 files on 2026-10-13, after `route-a-prediction` was pushed. They
  went into `specarith/ph2r2/data/platt_fresh/` on the desktop; file mtimes are 13:55:01–13:56:06 PDT, with matching
  Windows Zone.Identifier files and Recent-folder shortcuts at 13:55:11–13:56:05.
- **md5 checks (did happen), all matching the pins:**
  - desktop, 2026-10-13 ~13:56 PDT;
  - spot, after the scp the same minute (spot mtimes 13:56:32–13:56:35);
  - spot again after the UPS swap that evening, as part of the 128-file re-verification;
  - both machines again on 2026-10-14 at 16:25, in this audit.
- **Where the files are now:**
  - Desktop: `…/worktrees/ph6-xp/specarith/ph2r2/data/platt_fresh/`, the five files plus their Zone.Identifier files.
    No other copy exists under /home or C:\Users (the Recent .lnk files are shortcuts only).
  - Spot: `~/tmp/claude/specarith/ph2r2/data/platt_fresh/`, the five files.
  - char: none.
  - Every copy matches its pin: 12759c6b…, 17769568…, 763374d8…, 10af7827…, 6203cd45….
  - The files' access times now read 16:25 on 2026-10-14, set by this audit's own md5 reads, so access times cannot
    show earlier non-access. The evidence for that is the next item.
- **Decoded: never.**
  - The only code that reads `platt_fresh` with an F3 file name is `route_a_sealread.read()`. It refuses unless
    `seals/ROUTE_A_SEAL.json` exists, and that file has never existed.
  - The other code that uses `platt_fresh` (ph2s/s1read.py, ph2s2/s2read.py, tapered.py, cd_lag1.py) names F1 or F2
    files only.
  - A search of every session transcript under ~/.claude/projects for tool calls naming an F3 file or `platt_fresh`
    found only `ls`, `md5sum` and `scp` on the real files.
  - The n_f counts and pooling weights come from θ (N̄(t₁) − N̄(t₀)), not from file headers.
- **What "round-trip" operated on: synthetic files only.**
  - `route_a_read.py pipeline` on char, 2026-10-13 21:10–23:47 PDT: CUE_1000 spacings (GPU sampler, seeds
    [20261013, 99, i]) were placed at each F3 file's height range with exact θ and written in the Platt format to
    `~/tmp/claude/synthetic_<F3 name>`. They were decoded by the read's path, compared (max spacing error 0, dμ 0) and
    deleted.
  - Records, now committed: `cs4/results/calib/pipeline_*`.
  - The dry-run stand-ins on spot (`cs4/results/dryrun_synth/<F3 name>`, 2026-10-14 11:00–11:15) are likewise
    synthetic CUE files. Their md5s are not the pins (3efa79ab…, bbec7951…, 171a89c8…, c6c5c2bb…, 678ff938…).
  - "All five F3 files now round-trip exactly" meant five synthetic files at F3 geometry, each carrying an F3 file's
    name. It did not mean the F3 files.
- **Correction.** Two statements of 2026-10-14 were wrong about the download:
  - the seal draft's "No F3 zero has been downloaded or decoded";
  - my message to Will, "nothing about the F3 zeros has been downloaded or read".
  The true history: downloaded and md5-verified on 2026-10-13, never decoded. The seal text now says so.
- **Timestamp order.** The F3 download (2026-10-13 20:55 UTC) came before the pre-decode receipt's first Bitcoin
  attestation (block 971369, 2026-10-14 07:09:08 UTC). So that stamp shows the prediction existed by then, not that it
  predates the download. That it predates the download rests on GitHub's PushEvent for 0f0c5f77 at 2026-10-13
  16:31:01 UTC (`cs4/timestamps/ROUTE_A_PREDICTION_GITHUB_PUSH.json`; route_a_zeta.json at 0f0c5f77 has sha256
  98fc2356…, the stamped value).

## Forty-eighth round (Will, 2026-10-15) — PASS accepted; connected-term constraints; follow-up selection rule; findings (verbatim)
Round 48: PASS row (a) accepted as sealed.

Connected-term constraints (post hoc, data-free, labelled as derived).
Compute ∂μ*/∂μ₃ and ∂μ*/∂μ₄, each scaling only the connected T₃ or T₄ arithmetic part wherever it appears, with the others at CS values.
Use symmetric ±0.01 differences with a linearity check (the same method as B₂), and check that ρₙ and p(s) stay positive at ±0.02.
Report the implied constraint |μ_k − 1| ≤ (|μ̃ − 1| + 2·SE_pool)/|∂μ*/∂μ_k|.
GoF note (descriptive only): compare the five χ² values with the calibration’s mean χ² under CUE, and state whether this fits the rigidity-conservative covariance seen in the bins check.
Follow-up observable.
Commit the selection rule first: choose the observable with the larger |∂stat/∂μ₃|/SE_stat at the follow-up’s data geometry, with ties broken by |∂stat/∂μ₄|/SE.
Then compute both and choose mechanically. Record that the choice was made after the route (a) PASS.
It runs as an independent replication: tagged prediction → OpenTimestamps stamp → fresh zeros → seal → read.
Still open from round 47; put both in the findings file:
the reconciled F3 history (download date, md5 checks, and confirmation that nothing was decoded before 10/15 08:03);
the Bitcoin block of the f75e5816 prediction-manifest receipt.
Seal stamp: ots upgrade and the two-explorer check once it’s attested.
Findings wording: “consistent with the CS n ≤ 5 prediction (conditional on the ratios conjecture; one statistic; ±1.6%); the statistic depends substantially on n ≥ 3 correlation functions; connected-term sensitivity per item 1.”

## Forty-ninth round (Will, 2026-10-15) — stamp timing; protocol change; connected terms not identifiable; selection-rule amendment (verbatim)
Round 49:

Stamp timing (findings + protocol).
Record: the prediction and the rule files were anchored at block 971369 (2026-10-14 00:09 PDT), before any F3 decode. The seal is anchored by 08:21, after the read began at 08:03.
Record that the verdict is insensitive to the rule’s tunable parameters: |μ̃ − 1| = 0.05 of the band.
Add the GitHub push-event time for the route-a-seal tag once it appears, as a third-party timestamp.
Protocol change, effective now: no decode until the seal’s OpenTimestamps receipt is Bitcoin-attested and verified.
Connected-term constraints. Report them as model-dependent and not identifiable at N_eff ≈ 3.4. Give the reasons: node-rule sensitivity, the sign flip, and negative ρ₄ at ±0.02. Keep 0.063 and 0.19 out of the headline. Finish the μ₂ positivity check and state B₂’s status the same way.
Selection-rule amendment. Commit it before computing either candidate’s power; it replaces 6122a236’s metric and S_A definition.
Metric: |∂stat/∂μ|/SE_stat in the sealed global μ family. Eligible candidates need a block-cut n ≥ 3 share of at least 0.55. Highest metric wins; if neither is eligible, report that and stop.
S_A: the largest s on {1.0, 1.1, …, 3.0} where the n = 6 truncation bound in μ units is ≤ 0.01 × the candidate’s band. This is computed data-free from CUE replicate SEs.
Record that the amendment was made after the PASS and after the earlier rule turned out to be defective.
Findings headline: “Route (a) PASS: consistent with the joint CS n ≤ 5 prediction (conditional on the ratios conjecture; one statistic; ±1.6%). The statistic depends substantially on the n ≥ 3 correlation functions; per-order connected constraints are not identifiable at this N_eff.”
Open lead: per-order constraints may become identifiable at larger N_eff, where the cancellation is less severe. Weigh that against the smaller arithmetic corrections there.

## Fiftieth round (Will, 2026-10-16) — selection abandoned; both observables as independent replications (verbatim)
Round 50: option 3. Both observables run as independent replications, with no selection.

Record that the selection was abandoned after the defective run (d3c50fa8), and that both candidates’ SEs were seen before this decision. The n ≥ 3 share criterion is withdrawn as ill-conditioned for (B), for the same reason as §3’s non-identifiability.
Mechanical fixes (from amendment 2, needed for calibration only):
Fit (A) only on bins where p⁽²⁾_sine is resolved and positive.
A fit at its bound is a failure, not a value.
Define the every-node variants’ small-s handling, or drop those variants.
Add a red path: an injected negative-interpolation bin must trigger failure, not a bound value.
(A)’s window, data-free. S_A is the largest s where the T₅ bracket disagreement, in μ units, is ≤ 0.01 × (A)’s band. Commit the rule before computing it. On current numbers that’s around 1.65–2.0, so the window can’t go past 2.0 without the exact T₅.
(B)’s L, data-free. Choose L by |∂stat/∂μ|/SE in the global μ family, computed with the fixed code. Commit the rule first.
For each observable:
measure ∂μ*/∂μ properly, with no assuming it equals 1;
tagged prediction → calibration (false-FAIL rate and power) → seal → OpenTimestamps stamp, Bitcoin-attested before decode → fresh zeros not yet downloaded → double read.
Joint reading, declared in both seals:
Each test keeps its own calibrated false-FAIL rate. Report the family-wise rate, about 1 − (1 − α₁)(1 − α₂).
Both PASS: replication of route (a) by two further observables.
Exactly one FAIL: reported as a FAIL for that observable, with attribution limited to “observable-specific model terms or estimator”. It is not a refutation of route (a).
Both FAIL: route (a)’s PASS is called into question, and that gets reported plainly.
§3 stands with the n = 5 minima as committed in 878f9837.

**Record (filed with round 50).**
- The follow-up selection (FOLLOWUP_SELECTION_RULE.md, 6122a236 + amendment 1, 968a8066) is abandoned after its one
  run, which was defective (d3c50fa8). No choice was made from it.
- Both candidates' replicate SEs were printed by that run and seen before this decision: (A) SE_pool 0.0386 → 0.0039
  over s ≤ 1.0 … 2.1 (skip-rule variants); (B) SE_pool 0.0235, 0.0162, 0.0187, 0.0154, 0.0145 at L = 0.5, 1, 1.5, 2, 3.
  So both data-free window rules below are fixed after those SEs were seen.
- The block-cut n ≥ 3 share criterion is withdrawn for (B): Δκ₃ = 3ΔF₂ + ΔF₃ nearly cancels, so the share is
  ill-conditioned (3.9, 9.0, 15.8 at L = 1.5, 2, 3; identically 1 at L = 1), the same cancellation that makes the
  per-order constraints in findings §3 non-identifiable.

## Fifty-first round (Will, 2026-10-16) — F4/F5 geometry; S_A committed with a red path; (B)'s L = 3 known-answer flag; findings line (verbatim)
Round 51:

Geometry.
Keep the gap rule.
F4, for (A): the three declared files (L = 17.5, 19.75, 21.25).
F5, for (B): those three plus the L ≈ 15.59 file.
Record the asymmetry and the reason: the weaker observable gets the extra low-height file, decided before any F4/F5 prediction, calibration or download.
Then commit FRESH_SETS_F4_F5.md.
(A). Commit S_A = 1.6 from the rerun, together with the refusal fix (invalid window = invalid, never a hang). Add a red path: an injected negative-density window must be recorded as invalid and must not stall the pool.
(B)’s L = 3 known-answer flag. L stays at 3. Before running anything, commit this reading:
Then rerun the L = 3 known-answer fit with fresh seeds and at least 2× the replicates.
If χ² has p ≥ 0.01: record it as chance.
If p < 0.01: record the known-answer check as marginal at L = 3, and carry that as a caveat on (B)’s result.
Findings line, descriptive: the μ = 1 CS n ≤ 5 NNN prediction goes non-positive near s ≈ 2.9 at F-set heights, which is a validity edge of the truncated expansion.
Then, per observable: prediction → tag → calibration (false-FAIL rate and power at the final geometry) → seal → OpenTimestamps stamp, attested before decode → download → double read. The joint reading rule is as in round 50.

## Fifty-second round (Will, 2026-10-17) — launch the full prediction run; then merge, gates, tags, calibration, seal drafts (verbatim)
Round 52: launch the full prediction run, with the 10⁶ cutoff check at every node, mirroring route (a). When it finishes:

Merge the results and run the cutoff convergence check.
Run the gates, then tag the predictions for (A) and (B).
Run calibration on the final geometry: false-FAIL rate and power for each observable, plus the family-wise rate.
Send me the seal drafts.

Standing rule: no F4/F5 download or decode until each seal’s OpenTimestamps receipt is Bitcoin-attested and verified.

## Fifty-third round (Will, 2026-10-17) — (B)'s slope to SE ≤ 0.005; (A)'s GoF bins accepted with a count floor; per-file condition accepted; seal drafts (verbatim)
Round 53:

(B) slope.
Commit this rule first: run CUE_N replicates at L = 3 until SE(slope) ≤ 0.005.
If |slope − 1| > 2·SE, divide the slope out and carry its SE in δμ_sys. Otherwise take slope = 1 and carry its SE in δμ_sys.
Then run, and report (B)’s band and rates under the final δμ_sys.
(A) GoF. Equal-sine-probability bins (30) are accepted. Record them as a pre-data deviation from route (a), with the reason. Require an expected count ≥ 5 per bin per file. If any bin falls short, merge adjacent groups by a rule committed first. The thresholds come from calibration only.
Per-file condition. “All files but one within 3 SE” is accepted. Each seal states the calibrated combined false-FAIL rate, including this condition.
Seal drafts to me, with the false-FAIL rates, power, the family-wise rate, both receipts, and the md5 pins for F4 and F5.
Before any download: Will pushes followup-a-prediction and followup-b-prediction, the seals are stamped, and both receipts are Bitcoin-attested and verified.

## Fifty-fourth round (Will, 2026-10-18) — both seals approved after two §4 edits; correction note; sealing and reading order (verbatim)
Round 54: both seals approved, after these edits.

§4 in both seals. Add: “If one test reads MODEL MISFIT, UNRESOLVED or FIT FAILURE, the other test’s verdict is reported on its own (a one-observable replication or FAIL), and no statement is made about the pair.”
§4 in both seals. Replace “so their false-FAIL events are independent under μ = 1” with “treated as independent under μ = 1: disjoint ranges, ≥ 6·10⁶ apart in height; residual long-range arithmetic correlation between them is not modelled.”
Decisions log. Note the 891a238f correction: “BLOCK = 100 is the shortest length with ratio ≥ 0.95”. No history rewrite.
Then: rename the drafts, build both seal JSONs → Will commits, tags followup-a-seal and followup-b-seal, and pushes → stamp both seals → upgrade until Bitcoin-attested and verified on two explorers → Will downloads F4 and F5 by hand → each read runs twice, compare, report.
Order of reading. Read (A) and (B) independently. Don’t open one test’s output to interpret the other until both comparisons are done.

**Correction to commit 891a238f's message (round 54; no history rewrite).** Its phrase "BLOCK 100 windows (SE_boot/SD
geomean 0.983-0.987, none >= 0.95 needed... shortest qualifying)" is garbled. Correct: BLOCK = 100 is the shortest length
with ratio ≥ 0.95 (the geometric-mean SE_boot/SD ratios are 0.987, 0.984, 0.983 and 0.987 at 100, 333, 1000 and 3333
windows, all ≥ 0.95). The declared calibration file itself (`results/calib/followup_calib_B_declared.json`) is correct.
Check of the new §4 wording: the smallest gap between any F4 and any F5 height range is 6,300,000.

**Round 54 record: seal tags re-pointed before stamping (2026-10-18).** Will's seal commit e9b385d1 holds both seal
texts, both seal JSONs and the build logs (each blob's sha256 equal to what was built on spot). The first tags
`followup-a-seal` (object e8b4b840…) and `followup-b-seal` (object 168d1e3e…) were created on the parent 81928d3a, which
has none of the seal files, and pushed. Before anything was stamped against them and before any F4/F5 download, Will
re-pointed both to e9b385d1 and force-pushed the two tags only (new objects a0de8a70…, 8cfae8ec…; GitHub ls-remote
2026-10-18 14:21 UTC). The seal manifests name the re-pointed tags. Both stamped 2026-10-18 14:21 UTC.

## Fifty-fifth round (Will, 2026-10-18) — findings for the replications; Diagnostic D (exploratory, no verdict) (verbatim)
Round 55:

Findings section (“Replications, round 50–54”). Use the wording above. Record the heterogeneity numbers (χ² 282.7 on 3; calibration mean 3.0, max 15.1). State that a calibrated false FAIL would not show between-file heterogeneity of this size. State, as reasoning only, that a smooth-in-height model error is unlikely to produce a non-monotone pattern. List the slow-arithmetic-fluctuation hypothesis as untested.
Diagnostic D (exploratory, no verdict). Commit the design before running anything.
D1, scale dependence. For each F5 file, compute k₃ in contiguous sub-blocks over a fixed list of sizes (e.g. 1/2, 1/4, 1/8 … of the file, down to the 300-unit bootstrap block). Compare the between-sub-block variance with the variance expected from within-block SEs.
Signature of slow variation: excess variance that grows with sub-block size.
Controls: CUE stand-ins at F5 geometry (expect no excess); F4 and F3 files (already read, descriptive only).
D2, the second-order analogue. Run the same scale analysis for κ₂(3), the count variance, on the same files, to see whether pair-level count statistics carry the same slow component at a smaller relative size.
D3, theory. Find, from primary sources, the size and period of the off-diagonal (nearly resonant prime) contributions to the third moment of S(t+h) − S(t) over a finite t-window: Selberg, Tsang, and any later work on moments of S(t). Estimate whether they reach about 0.007 in k₃ at L = 3 over a window of 2·10⁶ in height.
Declare in advance: D1 showing scale-growing excess in the zeros but not in CUE supports the hypothesis; a flat D1 excess, or none, points toward the model terms or a pipeline defect.
Pipeline check alongside D1 (cheap). Split each F5 file into halves and report k₃ per half with its SE. Recheck each file’s zero-count completeness against θ, as for route (a) (|count − θ count| ≤ 2).
Nothing about route (a)’s or (A)’s verdicts changes.

## Fifty-sixth round (Will, 2026-10-18) — phase-averaged k₃ (post hoc); grid-anchoring sibling sweep; G1b; corrected (B) queued; findings §9 attribution (verbatim)
Round 56:

Phase-averaged k₃ on F5 (descriptive, post hoc).
Average k₃ over grid offsets u ∈ [0, L), using 32 evenly spaced offsets.
Get the SE from a joint block bootstrap over all offsets.
Report μ̃ per file and pooled, and the heterogeneity χ².
No verdict; label it “post-hoc, data seen”.
Grid-anchoring sibling sweep.
Add an “anchoring/origin” defect family to Task 0b.
Grep for windowed or gridded statistics whose window origin is tied to the data: specarith Stage 1/2 block pair sums, legacy Σ²/Fano/count statistics, and any floor((x − x0)/L) patterns.
Test each with an origin-shift red path: the same data at grid offsets u ∈ [0, 1) must give the same statistic within SE. Failures are flagged in the ledger.
Stage 2 specifically: recompute the measured shrink on F2 at 8 grid offsets (descriptive) and report the spread against Stage 2’s CI.
Engine v2 spec. Add G1b, an origin/translation-invariance gate: outputs must not depend on the grid origin or the window phase unless declared, in the same way G1 tests units. The calibrator for any windowed statistic must reproduce the real data’s anchoring, or the estimator must average over it.
Corrected (B), queued, not now. Its own pre-registration, an offset-averaged k₃ estimator, a CUE calibration through the same estimator, and fresh files. Run it after the engine-repair work.
Findings §9. Add the grid-lock attribution:
(B)’s FAIL is attributed to its estimator: the phase-locked window grid against a phase-averaged prediction.
Evidence: r = −0.99 for k₂ and −0.88 for k₃ against cos 2πφ across 12 files.
Record that the slow-arithmetic hypothesis was tested and not supported.
Route (a) and (A) are unaffected, because spacings don’t depend on the window origin.

## Fifty-seventh round (Will, 2026-10-18) — untestable Σ² sites; offset-test recalibration; corrected (B) data-free prep (verbatim)
Round 57:

The five untestable Σ² sites.
Ledger: flag every claim traced through rigidgate and lcap as “F22-suspected (untestable at the frozen commit)”. The flag stays until a test clears it.
Make them testable: load the imported live-tree modules at their frozen-commit versions inside the test harness, without editing the live tree, then rerun the origin-shift test.
Recalibrate the offset test.
RED means the maximum shift across offsets exceeds the 99th percentile of that maximum under translation-invariant nulls (Poisson, and CUE with random rotation). Match each site’s window length and sample size.
Re-grade all 36 testable sites under this rule, including the 7 marginal ones.
Record that the witness move to L = 10 was post-hoc, made on synthetic controls only.
The G1b requirement to average over phase for L ≤ 3 stays.
Corrected (B), data-free prep on spot, in parallel with the engine repair.
Estimator: k₃ averaged over grid offsets u ∈ [0, L).
Choose L by a data-free power rule, committed first. The F5 post-hoc result at L = 3 must not influence the rule.
Calibrate the averaged estimator from scratch on CUE (bias, SD floor, false-FAIL rate, power). Don’t reuse the phase-locked floor.
Check that fresh files are feasible under the gap rule (call the set F6) before building predictions.
Sealing waits for my review, and the read waits for Bitcoin attestation as usual.

## Fifty-eighth round (Will, 2026-10-18) — F6 geometry; the L rule's SE in μ units; continue the corrected (B) (verbatim)
Round 58:

F6 is four files: the three gap-feasible files at L ≈ 17.5, 19.75 and 21.25, plus zeros_46646000.dat at L ≈ 15.84.
Reason (record it): the low heights carry the largest corrections, the test stands alone, and the set is comparable to F5. Decided before any prediction.
Confirm that all four are distinct from F3, F4 and F5 and satisfy the gap rule against every touched range.
Pin the md5s and commit FRESH_SET_F6.md.
The L rule’s SE must be in μ units, SE(k₃_avg)/|Δκ₃(L)|. If the committed rule says otherwise, amend it before the CUE outputs are read, and record that the amendment came before any rule output.
Then continue: L* → predictions at F6 → tag → calibration of the averaged estimator from scratch → seal draft to me.

**Record (filed with round 58, before any L-rule output).** The committed rule (CORRECTED_B_DESIGN.md §2, f014f447;
code b2_rule.py, 04a2a14a) already computes SD_f(L) as the replicate standard deviation of μ̂_f(L) =
(k̄₃ − κ₃^sine(L))/Δκ₃,f(L), i.e. SD(k̄₃)/|Δκ₃,f(L)| in μ units, and SE_pool(L) = (Σ w_f² SD_f(L)²)^½ from those. No
amendment is needed. At the time of this record the CUE replicates were still running on char, `b2_rule.py rule` had
not been run, and no rule output existed.

## Sixty-first round (Will, 2026-10-19) — corrected (B) seal approved with a §4 addition; ARSv2 round-59 dispositions; G1b amendment (verbatim)
Round 61:

Corrected (B) seal approved. Add to §4: “The F5 phase-averaged value (μ̃ = 1.0034, L = 3) was post-hoc on data already seen. It informed the choice of estimator and is descriptive context only. This read, at L* = 4 on fresh F6 data under a data-free L rule, is the confirmatory test; the two are not pooled.” Then rename to CORRECTED_B_SEAL.md and build the seal JSON → Will commits, tags corrected-b-seal and pushes → stamp → Bitcoin-attested and verified on two explorers → Will downloads F6 → read twice → compare → report.
ARSv2 round 59 dispositions.
No further compute.
All 101 claims stay F22-suspected, marked “superseded by Task 3 (engine v2, G1b)”. The 11 claims with no rerun row get the same disposition and are listed by name.
Cited-only claims are in scope.
Phase22a’s index anchor stays untagged: anchoring to the event index doesn’t depend on a position origin.
The rigidgate generators’ live-tree imports are marked “audit-incomplete”.
Engine v2 spec, an amendment to G1b. Every windowed statistic is phase-averaged by construction. The origin-shift test is a check only where the positive control shows power at the statistic’s (n, L). Record round 59’s power map as the reason.

**Will's review of the corrected (B) seal draft, filed with round 61 (verbatim):**

> Corrected (B) seal: approved, with one line added. I checked it line by line.
>
> The band holds up. I recomputed SE_pool from the weights and SDs: 0.00550, which gives a band of 0.0154, matching the draft. The weights are proportional to the pre-data zero counts.
> The calibration is consistent. The acceptance curve gives 198 PASS out of 200 at μ = 1, the same as the stated 1% false-FAIL rate. Bias z-values up to 1.9 across four files are ordinary.
> L = 4 is right by the rule.* It has the lowest SE in the committed table (0.00489, against 0.00509 at L = 3). The CUE mean is about 0 at every L.
> Offset averaging removes the grid lock properly. With 32 offsets over L = 4 there are 8 samples per lattice period, so whatever phase dependence is left sits at the 8th harmonic. Jitter of about 0.3–0.4 suppresses that by a factor of roughly e^(−2π²σ²·64), which is effectively zero. The red path shows this: the averaged estimator moves at most 0.86 SE across grid origins, while the single-offset estimator moves 6.4 SE.
> F6 meets the gap rule exactly. Three files sit exactly one file-width away from F4, which is legal, and this test is read alone, so closeness to F4 doesn’t matter.
>
> The addition, in §4: “The F5 phase-averaged value (μ̃ = 1.0034, L = 3) was post-hoc on data already seen. It informed the choice of estimator and is descriptive context only. This read, at L* = 4 on fresh F6 data under a data-free L rule, is the confirmatory test; the two are not pooled.” The design history needs to be visible next to the verdict.
>
> ARSv2 round 59 dispositions (the same as round 60, now applied to the final tally):
>
> Unrun cells: narrow the scope, no more compute. All 101 claims stay F22-suspected, marked “superseded by Task 3 (engine v2, G1b)”. No claim’s status depends on clearing the flag.
> The 11 claims with no rerun row: the same disposition, listed by name.
> Readings:
> Cited-only claims count as in scope; that’s the conservative reading.
> Leave phase22a’s index anchor untagged. Blocks anchored to the event index don’t depend on any position origin, so F22 doesn’t apply.
> Mark the rigidgate generators’ live-tree imports “audit-incomplete” on top of the F22 flag.
>
> A lesson for engine v2, from the positive control. The offset test has no power at n = 1,600 at several window lengths, and none at all at non-integer L. So at small n, origin invariance can’t be tested in; it has to be built in. G1b should require phase averaging by construction for every windowed statistic, and use the test only as a check where it has power.

**Filing notes (round 61).** The ARSv2 dispositions are filed in ARSv2 `DECISIONS.md` and applied there. "Round 60" in
the review is not filed in this log or in ARSv2 `DECISIONS.md` (this session has no record of it); round 61 is applied
as written. The corrected (B) seal commit, like round 54's, is Will's: the text, JSON and build log are left
uncommitted for it, and `corrected-b-seal` should be created on that commit (round 54's tags were first made on its
parent and had to be re-pointed).

## Sixty-second round (Will, 2026-10-19) — audit-incomplete sibling sweep; D12 narrowed; corrected (B) stamp order (verbatim)
Round 62:

RIGIDGATE_RATE_ANNOTATIONS gets audit-incomplete, because the flag is about provenance, not windowing. Sibling search: scan the producing scripts of every ledger claim for live-tree path manipulation before import, and mark each hit audit-incomplete. Report the count.
Narrow D12’s scope:
Phase averaging by construction is required for position-anchored windows.
Index-anchored blocks are exempt, because no lattice mismatch is possible when every block holds exactly k events. They must pass an origin-shift check on the starting index wherever the positive control has power.
Record the reason in ENGINE_V2_SPEC.md.
Corrected (B): after Will pushes the branch and tag, verify that GitHub matches → stamp → attested and verified on two explorers → tell Will to download F6.

**Record (round 62, corrected (B)).** Already done when round 62 arrived: Will pushed `corrected-b-seal`; GitHub
(`git ls-remote`, 2026-10-19 17:31:17 UTC) showed tag object a31c806f… on d775b8a8, equal to the local tag, branch
specarith at d775b8a8. The seal manifest `cs4/timestamps/CORRECTED_B_SEAL_STAMP_2026-10-19.txt` (sha256 4c156c35…) was
stamped 10:31 PDT (018f6750); the receipt is being upgraded. No F6 file has been downloaded. The ARSv2 items are filed
and applied in ARSv2 `DECISIONS.md`.

## Sixty-third round (Will, 2026-10-19) — findings §10 (corrected (B)); ARSv2 open-question defaults; push list (verbatim)
Round 63:

Findings §10: corrected (B), with this wording:
PASS, sealed: μ̃_pool = 1.0017 ± 0.0055, against a band of ±0.0154, with a calibrated false-FAIL rate of 1.0%.
All four files within 3 SE, with no heterogeneity.
Stands alone. Consistent with the phase-locking attribution of the sealed (B)’s FAIL; it does not reverse that FAIL. The F5 post-hoc value is context only and not pooled.
Summary table: route (a), (A) and corrected (B) as three independent observables on disjoint fresh heights, all consistent with the CS n ≤ 5 prediction in the global μ family (conditional on the ratios conjecture), plus Stage 2.
Descriptive, labelled as such: Δκ₃ = 3ΔF₂ + ΔF₃ (≈ −0.14 + 0.12) is pinned to about 2·10⁻⁴ absolute, so each piece agrees to roughly 0.2% unless their errors cancel. This is not a per-order constraint (see §3).
ARSv2 open questions. Unless the details change things, apply these defaults and report back:
Start-index control (index-anchored blocks): use the same nulls as round 59 (Poisson and rotated CUE, matched in n and k), and check only where the positive control has power. Otherwise report it as unpowered.
Scan depth for live-tree imports: follow transitive imports to the first module outside the repo. Report direct and transitive hits separately.
Producing scripts that can’t be found: flag the claim “provenance-missing”. Like audit-incomplete, it can’t be cleared until the script is found, and it is listed by name.
Pushes: list for Will every unpushed commit and tag on both repos, in order.

**Filing note (round 63).** Findings §10 is in `../cs4/ROUTE_A_FINDINGS.md`. The ARSv2 items are filed and applied in
ARSv2 `DECISIONS.md`; the start-index control computes on the workstation only (the engine-repair arc's rule).

## Sixty-fourth round (Will, 2026-10-19) — calibration conservatism; Var_zeros/Var_CUE open lead; push list (verbatim)
Round 64:

Findings §10 (or §11, “Calibration conservatism”). Add one paragraph: across route (a) GoF (18th percentile), the (A) heterogeneity check (χ² 0.6 on 2), the bins-check SE trend and corrected (B) homogeneity (4th percentile), the zeros fluctuate less than the CUE null predicts. A likely cause is Berry-type saturation of Σ² (untested). Consequence: the CUE-floor SEs are conservative for the zeros, so the PASSes stand and power against modest deviations was understated.
Open lead: the ratio Var_zeros/Var_CUE of block statistics as a function of block length, from the existing bootstrap outputs, as a direct measure of number-variance saturation at fresh heights. Descriptive first; any confirmatory version gets its own pre-registration. Candidate for the engine v2 gallery.
Then send the push list once the ARSv2 commits land.

**Filing note (round 64).** Added as `../cs4/ROUTE_A_FINDINGS.md` §11 and `../OPEN_LEADS.md` L6. §11 adds one caveat
already recorded in the R₂ findings: the CUE calibration blocks carry no correlation beyond a block, so a long CUE_N
baseline is needed to separate generic rigidity from an arithmetic cause.

## Sixty-fifth round (Will, 2026-10-19) — L6 descriptive pass; long-baseline design draft; release-notes draft (verbatim)
Round 65:

L6 descriptive pass: go. Build the table of Var_zeros/Var_CUE against block length across F6 (corrected B), F3 and F4 (route a and A), and the R₂ bins drift-removed series.
Mark every block ≥ about 1,000 levels “baseline invalid: stitched CUE_1000” and don’t interpret it. The calibration’s CUE is independent rotated 1,000-level matrices, so long blocks see no long-range rigidity in the baseline.
Interpret only shorter blocks, labelled descriptive. Add the note to OPEN_LEADS L6, stating that the long baseline is what unblocks the long-block comparison.
Long-baseline design and pre-registration: draft only, for my review, run nothing.
One sequence of at least 10⁵ levels. Prefer CUE via a banded CMV representation (no unfolding). The fallback is Dumitriu–Edelman β = 2, bulk only, with semicircle unfolding and its high-pass caveat stated.
If cbe.py is reused, re-run its red paths first.
Gates: Σ²(L) against the exact CUE/sine-kernel formula up to about 10³ spacings; and the block-variance ratio of baseline against an independent baseline replicate ≈ 1 at every block length.
Then the identical block statistics as for the zeros.
Release notes: draft them from §9–§11 for Will’s re-release (route a, A, corrected B, the sealed (B) FAIL with its grid-lock attribution, and the calibration-conservatism note). Draft only.
§8’s per-order lead and L3–L5 stay queued behind L6.

## Sixty-sixth round (Will, 2026-10-19) — §11 revised; L6 long baseline approved; calibration-method note; release notes (verbatim)
Round 66:

Revise §11. Replace “Berry-type saturation (untested)” with: “consistent with the arithmetic suppression of block variance already established for the pair statistic: R₂ §6 against a single 10⁶-level GUE sequence (5 of 5 bins), confirmed on fresh heights in Stage 1, size matched to CS08 in Stage 2. R₂ §6 judged Berry saturation alone too weak and named few-prime form-factor fluctuations as the candidate. Part of the conservatism in the CUE_1000-calibrated tests may also come from stitching (see L6).” Mark it as a round-66 correction.
L6 long baseline: design approved. Run step 0 first, then the generation on spot, then Gates 1 and 2 with their witnesses, then the comparisons. Report three ratios per block length: stitched/long (the artifact), zeros/long (the arithmetic part), and the cross-check against the 10⁶ GUE pair baseline. Descriptive only.
Calibration-method note, for future tests: if Gates 1 and 2 pass, propose single-sequence CUE baselines as the calibration standard in place of stitched CUE_1000. Proposal only; no sealed result is re-read.
Release notes:
±1 SE throughout, with a separate “sealed band” column and a footnote.
ARSv2 out of scope, with one line saying the engine repair continues separately.
Confirm the J₁₃ erratum and the 10/14 review-response banners are included.
Still draft, for Will.

## Phase 6 near-miss check (Will, 2026-10-19; unnumbered, after round 66) — descriptive only (verbatim)
Phase 6 near-miss check (descriptive only, no verdicts):

Inventory first. For every 6.1 candidate and any 6.2 deformation scan, list what was saved: spectra, S(τ) arrays, τ grid, taper, regularisation parameters, basis size and convergence status. Report what exists before computing anything.
If the arrays exist, commit this rule first, then run it:
For each converged spectrum, compute the prime-hit rate: the fraction of log pᵏ (pᵏ ≤ the bound declared in Phase 6.0) with a peak inside the sealed resolution window.
Compute the same rate for 200 fake sets of log m, with m random non-prime-powers matched in count and range.
Report the true rate’s percentile among the fake sets, plus the correlation of matched peak amplitudes with log p/√p, and its sign.
Deformation paths (if 6.2 ran): the same two numbers at each parameter value. Report any monotone trend with its rank correlation.
Label everything post-hoc and descriptive. A true-prime percentile above 95 on any spectrum or path gets flagged for a pre-registered follow-up; it is not reported as a finding.

**Filing note.** Filed here, where the session's rounds are logged; Phase 6's own log is `../ph6/PH6_DECISIONS_2026-10-07.md`
(a pointer is added there). Step 1 is the inventory only; nothing is computed before Will has seen it.

## Sixty-seventh round (Will, 2026-10-20) — L6 V7 diagnostic and its reading; Phase 6 near-miss hit definition (verbatim)
Round 67:

L6 Step 0, V7 diagnostic.
Commit this reading first: run V7’s residual on the N = 10⁴ roots already verified against the dense solver.
If any verified root exceeds F_ACCEPT: V7 is miscalibrated. Recalibrate its threshold against the verified roots so it scales with N, record a post-hoc gate amendment, re-run V7 at N = 10⁵ under the amended threshold, and if it passes, generate 50 CMV sequences on spot in parallel.
If the verified roots pass V7: the N = 10⁵ failure is real. Fall back to Dumitriu–Edelman as pre-declared, unfolding with the finite-N density, not the asymptotic semicircle, with the high-pass caveat stated.
Skip the GPU port.
Phase 6 near-miss check, hit definition. Commit this before computing anything:
A hit at τ₀ (log pᵏ, or log m for fake sets) means S(τ₀), interpolated, exceeds the 99th percentile of S over the band [τ₀ − B, τ₀ + B].
The band excludes ±1 resolution width around every true and fake test point.
B = 10 resolution widths.
Use the identical rule for the true and fake sets, and the same 200 fake sets. Report the percentile of the true rate, plus the amplitude correlation with log p/√p.
Post-hoc and descriptive throughout.

**Will's notes with round 67 (verbatim):**

> L6 baseline: run option 2 first. It takes 11 minutes and decides everything else.
>
> This week has a clear pattern: nearly every first-run gate failure turned out to be a fault in the gate’s design, not in what it was checking. V5 already shows the Prüfer roots matching dense eigenvalues to 4·10⁻¹⁰ at N = 10⁴, and V6 certifies the N = 10⁵ draw. So V7’s residual criterion may be flagging roots that are correct. The N = 10⁴ check answers that directly, because the true roots are known there. Declare the reading before running it:
>
> V7 flags the dense-verified roots at N = 10⁴: V7’s threshold is miscalibrated. Recalibrate it against those verified roots so it scales with N, and record that as a post-hoc gate amendment. Then generate with CMV on spot, running the 50 sequences in parallel. At 6.9 hours each, that’s well under a day of wall time on spot’s cores, and spot is otherwise idle.
> V7 doesn’t flag them: the N = 10⁵ failure is real. Fall back to Dumitriu–Edelman as pre-declared.
>
> I’d avoid the fallback if possible. Unfolding with the semicircle introduces slow drifts in density, and slow, long-range variance is exactly what this baseline is meant to measure. If D–E becomes necessary, unfold with the finite-N density, not the asymptotic semicircle. Skip option 3: porting to the GPU adds engineering risk for no scientific gain.
>
> Phase 6 near-miss hit definition: use amplitude at a fixed point, not peak-picking.
>
> A hit at τ = log pᵏ means S(τ), interpolated at exactly that point, exceeds the 99th percentile of S over a local reference band around it.
> The reference band excludes ±1 resolution width around every test point, true or fake.
> Apply the identical definition to the fake log m sets.
>
> Peak-picking adds choices (thresholds, prominence, how close is close) that can drift toward the answer. A fixed-point amplitude has no free knob beyond the band width and the percentile, and both are committed before computing.

## Sixty-eighth round (Will, 2026-10-20) — L6 V7 targeted check at N = 10⁵; Phase 6 near-miss closed as a null (verbatim)
Round 68:

L6, option 2: go. Re-run the N = 10⁵ step-0 draw (seed 967), saving θ and ψ′ per root. For every root with V7 residual > 1, apply three independent checks:
(a) the ψ′·ulp(θ) floor accounts for the residual;
(b) f changes sign across a bracket a few ulps wide;
(c) refining the root in extended precision moves it by ≤ 10⁻⁶ of the mean spacing.
If (a), (b) and (c) all hold for every flagged root, apply the pre-committed K amendment and generate the CMV baselines on spot. If any root fails (b) or (c), fall back to Dumitriu–Edelman via a committed design addendum.
Phase 6 near-miss check: close it as a null.
Record that C1a and C1b’s flags are a defect in the flag rule. The percentile is ill-posed when the fake hit counts are near zero.
Under an exact Poisson tail with the theoretical 1% chance rate (expected 0.34 hits per 34 points), C1a’s 2 hits give p ≈ 0.05 and C1b’s 1 hit gives p ≈ 0.29, before correcting across 4 candidates.
No amplitude correlation (|r| ≤ 0.29, against −1.000 for the zeros).
Conclusion, descriptive: no prime-line structure in the xp candidates, consistent with the 1D-integrability expectation. No follow-up.
Amend the rule note: future near-miss checks use exact count tails, with the chance-rate floor, not percentiles among sparse fake sets.

## Sixty-ninth round (Will, 2026-10-21) — L6 CMV route accepted; ruling on the V7 targeted check; amended (a) (verbatim)
Round 69: CMV route accepted.

Commit a ruling record citing 1ae0db16: all 9 flagged roots pass (b) and (c); the m = 37,025 failure of (a) is a check-definition flaw (derivative at θ, not across the bracket); K = 4 applied as pre-declared.
The pipeline accepts v7check’s exit 0 or this ruling, matched by the sha256 of the v7check output. Don’t modify the check itself.
Post-hoc amendment to (a) for future runs: use the slope across the bracket, not ψ′ at θ. Re-run the amended (a) on the saved N = 10⁵ arrays and confirm all roots pass. Record it.
Generate the 50 CMV sequences and the Gate 1/2 witnesses on spot, checkpointed per sequence. Then Gates 1 and 2, then the L6 comparisons (stitched/long, zeros/long, the 10⁶-GUE pair cross-check). Descriptive only.

## Seventieth round (Will, 2026-10-22) — L6 gate 2 ruling; comparisons run, labelled; §11 and release notes revised; future gate-2 witness (verbatim)
Run the comparisons, labelled. The gate didn't fail because the instrument is broken. It failed because my prediction about stitching was wrong, and the design already said what to do in that case.
What the two gates establish:
The baseline is sound. Gate 1 shows the 50 long sequences match the exact CUE number variance from 1 to 1,000 levels, and all three witnesses fail as they must. The two halves agree. That's the instrument validated.
The stitched witness was a hypothesis, not a correctness check. It assumed stitching changes these block statistics, and it doesn't, within ±14% at G = 1,000 and ±30% at G = 10,000. In hindsight that makes sense. Stitching only breaks long-range correlations at the seams, and these three statistics are averages of local quantities (spacings, next-nearest spacings, counts in windows of 4), whose block variance comes from short-range covariance. Gate 1 confirms stitching does change long-window count variance. These statistics just don't see it.
So I was wrong to say stitching might explain part of the conservatism. For these statistics it doesn't, and that makes the zeros' lower variance more interesting, not less. It's real, and its cause for local statistics isn't established. The arithmetic suppression we measured for the pair statistic is the obvious candidate, but for these statistics it's untested.
For future runs, replace gate 2's witness with one that must fire on block statistics: a planted, known excess of block variance, for example a sequence with slow segment-wise rate modulation. That way the gate tests power, not a guess about the physics. 
Round 70:
Ruling, recorded in design §13. Gate 2's stitched witness was mis-specified: it encoded an expected stitching effect that doesn't exist for these local block statistics. Baseline validity rests on gate 1 (with its three failing witnesses) plus the agreement of the two halves, and the stitched/long sensitivity is stated (±14% at G = 1,000, ±30% at G = 10,000). The pipeline accepts this ruling, matched by the hash of the gate record. Don't modify the gate.
Run the comparisons, labelled "descriptive; gate-2 stitched witness did not fire (see §13)": the zeros' ratios to the long baseline at every block size, plus the cross-check against the 10⁶-level GUE pair windows.
Revise §11 and the release notes.
Remove "part of the conservatism may come from stitching". Replace it with: "stitching shown not to affect these statistics' block variance within ±14% at G = 1,000; the zeros' lower variance is therefore not a calibration artifact. Its cause for these local statistics is untested; the arithmetic suppression established for the pair statistic is a candidate."
Revise the L6 table's "invalid at ≥ 1,000" marks to "valid within stated sensitivity" for these three statistics.
Future witness design. Gate 2's witness becomes a planted block-variance excess of known size, for example a sequence with slow segment-wise rate modulation, which must fire. Record it in the design template.

## Seventy-first round (Will, 2026-10-22) — own-bootstrap SE validation; CS08 feasibility note; push list (verbatim)
Round 71 (all descriptive):

Validate the own-bootstrap SE. For route (a), (A) and corrected (B), take the per-file estimates and per-file own-bootstrap SEs across every fresh file each statistic was read on, and compute the scatter χ² against those SEs. Report χ²/dof and the percentile under the χ² law. Data already seen, so descriptive only. If it validates, draft a proposed calibration rule for future pre-registrations: own-bootstrap SE at a declared block length, with a fallback to the CUE floor when the bootstrap is unstable. Draft only.
Feasibility note. For each of the three statistics, list the highest correlation order its block variance requires, and say whether a CS08 prediction is reachable with the existing n ≤ 5 machinery. No computation; just the note, for my review.
Push list. Update it to include c5871335 and e03abe52.

## Seventy-second round (Will, 2026-10-22) — CUE scatter control; no bootstrap calibration rule; pair-connected approximation; pushes (verbatim)
Round 72:

Control first (descriptive). Using the L6 long CUE sequences, form file-sized segments matched to the F3/F4/F6 zero counts. Run the identical per-file estimators (route a, A, corrected B) with their own-bootstrap SEs at G = 300, and compute the same scatter χ² and percentile. Commit the method first. If CUE χ²/dof ≈ 1, record the zeros’ low scatter as a property of the zeros (long-range rigidity). If CUE is also low, stop and diagnose the estimator pipeline.
No bootstrap calibration rule. Record that block bootstrapping can’t calibrate the zeros: negative long-range covariance means the SE falls with block length and never levels off below file scale. Sealed tests keep the CUE floor. A between-file-scatter SE may be proposed for a future test only with ≥ 10 files, pre-registered.
Theory, exploratory. Implement the pair-connected approximation for the block variance of the three statistics. Validate it first against the long CUE baseline (known answer), and report agreement per statistic and G. Don’t apply it to ζ until that validates. The n = 6 extension waits on this result.
Pushes. Run git fetch origin, confirm the unpushed list, and give Will the final count. Stray tags: Will deletes them locally.

## Seventy-third round (Will, 2026-10-22) — CUE control accepted; pair-connected wording; L6 bias correction; n = 6 scoping; pushes (verbatim)
Round 73:

The CUE control is accepted as recorded. The file-sized long-CUE run (about 120 hours) isn’t needed: stitching was shown irrelevant for these statistics, and file-sized stitched replicates give about 1.
Pair-connected wording. Record it as “not validated (known answer contaminated by short-segment block bias)”. The ≤0.2% pair-channel bound holds within the approximation only, with an unvalidated implementation. Note the consistency with Stage 2, where the shrink came through the long-range 4-point term, as a hypothesis, not a finding.
L6 correction (descriptive). Re-estimate the long-baseline block variance at G = 3,000 and 10,000 with an estimator free of the within-sequence mean-subtraction bias: global mean, or the concatenated variant, plus an explicit bias correction. Report the revised zeros/long ratios next to the old ones, and update the L6 table and findings §11 if they change.
n = 6 scoping only. Draft a design for the exact CS08 n = 6 block-variance prediction for corrected (B): the long-range term’s structure, a cost estimate scaled from Stage 2’s I₄,long, a U(N) known-answer check at n = 6, and fresh-height test geometry. Nothing runs until I’ve reviewed it.
Pushes: 34 commits on specarith for Will. The published lowercase seal tags stay.

## Seventy-fourth round (Will, 2026-10-22) — L6 correction accepted; n = 6 staged (a)–(d); shrink clarification (verbatim)
Round 74:

L6 correction accepted as applied (revised at G ≥ 3,000 only).
n = 6, staged:
(a) Run the U(N) exact-trace prediction for corrected (B)’s block variance now. Compare it with the L6 long baseline at every G and report agreement. Data-free.
(b) Extraction step, time-boxed to 3 sessions: derive the long-range non-oscillating part for 3+3 clusters. Commit the gate first: it must reproduce the sine-kernel long-range result within SE. If it doesn’t pass within the budget, stop and report.
(c) Short range: bound the arithmetic n = 6 short-range correction at a low prime cutoff before computing it fully. If it’s below the test’s resolution, carry it as a bounded systematic.
(d) Fresh set: 5–8 files across ℓ ≈ 15.5–22 under the gap rule, chosen by a rule committed first.
Clarify “shrink about 0.8” in the scoping draft: which quantity and which G. Reconcile it with the 0.16–0.31 zeros/long ratios before setting the test geometry.
Nothing beyond (a) runs until (b)’s gate result and (c)’s bound come back to me.

(Will, same message: "I pushed as well." The 36 commits through 3a054880 are on origin.)

## Seventy-fifth round (Will, 2026-10-22) — stage (a) accepted; stage (b) gates amended; session clock; (c) may run (verbatim)
Round 75:

Stage (a) accepted. Record in findings §11 and OPEN_LEADS L6: exact U(N) block variance for corrected (B) is flat in G (to 0.05%), and the CUE covariance is gone by r ≈ 10. The zeros’ halving of block variance between G = 300 and 10,000 is therefore entirely arithmetic long-range in origin. The rounds 72–73 CUE “fall” was estimator bias, measured as +10% at G = 300 and +5% at G = 1,000.
Stage (b) gates, amended before any derivation. Add two gates with ζ-regime resolution:
G-b2, reduction: the 3+3 long-range term, with the extra points reduced by the cumulant relations, must reproduce the validated cs4lr 2+2 long-range term at the same heights and r, within its precision.
G-b3, brute-force spot check: at a prime cutoff of 10³, full n = 6 quadrature at 4–6 configurations with r ∈ [100, 500], compared with the extraction at the same cutoff.
The U(N) gate stays. The deliberately wrong variants must fail all three gates.
Session clock: the 3-session box starts with the derivation, not the gate commit.
(c) and (d): as committed. (c) may run its n = 6 construction and U(N) check, then the low-cutoff bound on spot (10–100 core-hours), alongside (b). (d) stays unrun.

## Seventy-sixth round (2026-10-23) — G-b2 accepted; stage (c) construction fix; G-b1 staged; cost update; time box (verbatim)
Round 76:
G-b2 PASS accepted. The relative/absolute tolerance coding error is recorded, corrected to the declared absolute criterion.
Stage (c): a construction fix, not a gate amendment.
Below a separation threshold (declared before running), the n = 6 construction evaluates in high precision (double-double or mpmath).
A runtime guard refuses below-threshold evaluation in double.
Add a path-agreement check at the threshold.
Re-run the committed U(N) pointwise gate unchanged (10⁻³ configurations included). It must pass via the high-precision path.
Record the change as a post-hoc construction change.
Then (c)'s bound and G-b3 may proceed.
G-b1.
(i) Now: the identical-node determinant comparison, averaged over one period in r, labelled "algebra check, not G-b1".
(ii) Session 2: the cross-factor expansion, with a truncation-error estimate validated against the exact determinant at moderate r for a few points.
(iii) G-b1 against the exact Fredholm answer, which must pass before any ζ computation.
Update the n = 6 scoping cost estimates with the corrected node counts before session 2, and send them to Will and me.
Time box: 1 of 3 sessions used. If G-b1 and G-b3 aren't passing by the end of session 3, stop and report.

## Seventy-seventh round (2026-10-23) — G-b3 attribution; the ζ fix; (c) at 6 + 8 nodes; sibling check; time box (verbatim)
Round 77:

G-b3 FAIL recorded, attributed to beat terms (slow components from products of primes near e^ℓ mixing with the carrier), with the gap table.
The fix for ζ: evaluate the full function on the estimator’s 1/8-unit r grid, made affordable by the session-2 cross-factor expansion. In the expansion, only smooth envelopes are expanded in window/r; carrier and prime phases are carried exactly, never treated as slow. The expansion must pass G-b3 (brute force at cutoff 10³) and G-b1 before any ζ prediction.
Stage (c) bound: 6 nodes plus an 8-node convergence check (about 130 core-hours) on spot. Commit before running.
Sibling check: confirm that Stage 2’s dropped ℓ-oscillating part (≤ 0.9% at 2+2) was computed, not assumed, and carried as a systematic. List any other banked result that used the phase filter as exact.
Time box unchanged: 1 of 3 sessions used. If G-b1 and G-b3 aren’t passing by the end of session 3, stop and report. Record the beat-term finding (it carries 1–30% of the 3+3 long-range piece at r ≤ 500) either way.

## Seventy-eighth round (2026-10-23) — (c) redefined to the connected 6-point term; witnesses; pilot first; (b) session 2 starts (verbatim)
Round 78:
(c) redefinition. Commit before running: the bounded quantity is the arithmetic part (ζ − U) of the fully connected 6-point term only. Everything through ρ₅ stays out of scope, as originally declared. Record that the round-77 amendment bounded the whole (3,3) piece by mistake.
(c) witnesses, committed before running.
U(N)-for-ζ null: the arithmetic part must be zero to within precision, at 8 and 10 nodes.
Convergence: 8 against 10 nodes, with the agreement criterion declared in advance.
(c) pilot first. One or two r values (r = 6 included) at 8 and 10 nodes on ζ, plus the null. Report to me. Run the full computation (about 800 core-hours on spot) only if the pilot converges and the null passes.
Stage (b) session 2: start now, in parallel. Use the full-function expansion with exact phases, evaluate at several heights per file (to answer the averaging question), and use G-b1 and G-b3 as the gates. Time box: this is session 2 of 3.

## Seventy-ninth round (2026-10-24) — time box honored; session 3 is close-out (verbatim, with Will's reasoning)
Will's reasoning, sent with the round:

My call: honor the time box. This is the situation it was set up for. Session 2 has established that the ζ extraction G-b3 needs doesn’t exist yet, and designing, building and validating one in a single session isn’t realistic. Pushing past the box would be exactly the “one more fix” spiral we agreed to avoid.

Use session 3 to close out, not to chase G-b1. G-b1 is reachable, but it would only validate the U(N) side, and stage (a)’s exact trace formula already gives us CUE’s block variance. Spending around 10³ core-hours there buys almost nothing without a ζ prediction to go with it. Session 3 should bank what this arc has actually produced:

The exact four-term covariance form for disjoint windows: C(r) = κ₃₃ + 9κ₂₁κ₁₂ + 9κ₁₁κ₂₂ + 6κ₁₁³. It’s verified against Fredholm to between 10⁻¹¹ and 10⁻⁶.
The beat-term finding: at 3+3, slow components from prime products near e^ℓ carry 1–30% of the long-range piece at fixed height. That’s why no phase-filter extraction can work for ζ at this order.
The averaging result, once the run lands: how much the height spread within a file suppresses the beats, compared with the prediction CC stated before running.
The (c) pilot result, as a convergence and size record. The full run of about 700 core-hours isn’t funded, because without a ζ prediction the bound has nothing to bound.
The spectral route as an open lead. A one-page sketch: compute the near-zero-frequency content the Bartlett sum sees, prime product by prime product. Why it might work, what it would need, and an honest note that it’s new analysis. No design or costing now.

What we actually learned stands on its own. The zeros’ five-fold block-variance deficit is real, entirely arithmetic and long-range, and predicting it from the ratios conjecture at 6-point order needs a new analytic tool. Knowing exactly why it’s hard is a legitimate result.

Catching the in-window repeated-node defect before any result was read was handled well, and confirming the d² scaling first made the fix exact rather than just plausible.

Round 79: time box honored.

Let running jobs finish: the (c) pilot (about 85 core-hours) and the beat-averaging test (about 145 core-hours). Report both against their pre-stated readings.
Don’t fund the full (c) run (about 700 core-hours) or G-b1 brute force (about 10³ core-hours). Without a ζ extraction, neither feeds a prediction.
Session 3 is close-out. Write N6_CLOSEOUT.md containing:
the exact four-term covariance form with its Fredholm verification;
the beat-term finding (1–30% of the 3+3 long-range piece at fixed height, cutoff 10³);
the averaging result;
the (c) pilot as a convergence and size record;
the in-window repeated-node defect, caught before any result;
the stop: “an exact CS n = 6 prediction of corrected (B)’s block variance requires a ζ extraction that retains beat terms; not available; arc stopped at the time box.”
Open lead L7: the spectral route, a one-page sketch only. Near-zero-frequency content of the Bartlett-weighted C(r), prime product by prime product: rationale, requirements, why it’s new analysis. No design or costing.
Update findings §11 and OPEN_LEADS L6 to point to the close-out. Pushes to Will.

## Eightieth round (2026-10-24) — averaging FAIL recorded; §3 rewritten; settling test (post-hoc) under the estimator's kernel; waiter; pilot runners (verbatim)
Round 80.

Averaging test: recorded as FAIL against its pre-stated prediction at r = 100 and r = 300 (close-out §4). Rewrite close-out §3 so the main carrier of the class-1 gap is the ~1.04 cycles/unit near-carrier leak through G-b3’s two-period average, with a slow remainder that is also not e^ℓ-like. Strike “no phase-filter extraction can work for ζ at this order” and the beat-terms stop wording from round 79, with a note that round 79 asserted them before this test.
Run the settling test (~100 core-hours), labelled post-hoc. Original G-b3 FAIL stays as sealed. Before computing, commit:
The kernel: corrected (B)’s exact effective weighting of C(r) (offset-averaged k₃, L* = 4, 32 offsets), derived from the estimator code.
Known answer: the kernel applied to the exact U(N) C(r) reproduces stage (a)’s exact CUE block variance. If it doesn’t, the test is void.
Witness: a planted 1.04 cycles/unit component and a planted slow component of known amplitudes. Their transfer factors are predicted, then checked.
Points: r = 100 and 300. Tolerance: G-b3’s original, unchanged.
Reading:
PASS at both points → stop reads “paused at the time box; extraction viable under the estimator’s kernel; resumption is a new arc, Will’s call”.
FAIL at either → stop reads “extraction inadequate under the estimator’s own kernel”, with the slow-content share at each point.
The full (c) run and G-b1 stay unfunded either way.
Waiter: exit 0 when the failure list is empty; nonzero only on failure.
Pilot second runner: confirm atomic chunk writes. Diff any chunk both runners computed and report bit-identity. Then record the pilot in §5 as planned.

## Eighty-first round (2026-10-25) — housekeeping; n = 6 resumes as arc N6-2 (two sessions); plan before computing (verbatim)
Round 81.

Housekeeping from round 80:
Cite the G-b3 seal line showing the 1% tolerance.
Report the (c) pilot against its null, witness and 8-vs-10 convergence criteria.
Report the bit-identity diff on chunks both runners computed.
Confirm the waiter fix.
Push status: 4 unpushed commits on specarith; pushes stay with Will.
Will resumes n = 6 as a new arc, N6-2, time box two sessions. Write N6-2_PLAN.md before computing. It must contain:
every piece of corrected (B)’s full estimator sum, with the cost of each;
the gate, frozen as in 739ccde4: same kernel, the same known-answer check, both planted witnesses and the 1% tolerance;
the reading: the extraction holds at this height only if every piece passes. Any failing piece is recorded and stops step 2.
Step 1: run the frozen gate across all pieces at ℓ = 15.75. If the total cost is ≤ 300 core-hours, start straight away. Otherwise report the cost first.
Step 2, only if step 1 passes: G-b1 convergence at 8, 10 and 12 nodes for U(N), with the convergence criterion committed first. Then confirm the extraction at one fresh height and fresh values of r, chosen by a rule committed before anything is computed.
Decision point after step 2. Report before anything else is funded: the full (c) run, the production cutoffs, and the sealed prediction of corrected (B).

## Eighty-second round (2026-10-25) — every-piece gate withdrawn; pilot FAIL as sealed; node check; sampled gate; decision point (verbatim)
Round 82.

Every-piece gate withdrawn. It is a full-grid brute force and defeats the extraction’s purpose. Record the cost table and the structural point in N6-2_PLAN.md as the reason.
(c) pilot: record the convergence FAIL as sealed (E 0.056 vs 0.033, ΔI 0.050 vs 0.030; class 0 agrees to 1.7%). FULL_RUN_ALLOWED stays false.
Node check on the settling pass (first, cap 300 core-hours). Report a cost estimate before running if it would exceed that.
Recompute the brute − extraction gap at r = 100 and 300 at 6 and 8 nodes, same kernel.
Report the 4-vs-6 quadrature-error branch of the sealed G-b3 rule.
Reading, committed now: the settling pass stands only if the gap stays within tolerance at 6 and 8 nodes. Otherwise it’s recorded as a 4-node artifact, and N6-2 pauses.
Sampled gate, replacing step 1. Commit before computing:
Sample: a seeded draw of members, stratified by piece group and log-spaced in r out to 10,000, including far members. Run at ℓ = 15.75 and at the fresh height zeros_2365046000 (ℓ = 19.7466). The four fresh r values already drawn go in the (3,3) stratum.
Tolerance, in units of the final answer:
Cap the projected total gap at 0.5% of the extraction’s full-grid total.
Projection per stratum: the largest |gap| in that stratum’s sample × that stratum’s summed kernel weight.
The total is the sum over strata.
This replaces the per-piece 1% rule and removes both declared hazards.
Witness: each stratum’s planted tone and planted slow component are sized as a fixed share of the budget, not of the (3,3) piece’s brute-force value. A witness that isn’t recovered at its predicted size makes that stratum void.
Cost: confirm the extraction’s full-grid cost, then size the sample to ≤ 300 core-hours at the node count item 3 supports.
Runs only if item 3 passes.
Step 2 (G-b1 at 12 nodes, ~1,750 core-hours): stays queued behind item 4. It isn’t funded yet.
Decision point after item 4. Report the honest production bill: G-b1, (c) at the node count it actually needs (cost the 10-vs-12 pilot), production cutoffs, and a measured speed-up for a 4090 port on one piece. Will then decides whether to resume, port or pause.

## Eighty-third round (2026-10-25) — stop narrowed to 4 nodes; item 4 withdrawn; node diagnostic first; cost model (verbatim, with Will's reasoning)
Will's reasoning, sent with the round:

Round 83: don’t raise the cap, and don’t start the port. First run one cheap diagnostic, about 265 core-hours, which can kill the settling pass but can’t confirm it.

My error, now three rounds running: I set caps without a cost model, and CC has had to bounce two designs (rounds 81 and 82) at 50–200× over. Round 82 also left out ψ's weights from the projection and used a denominator nobody can compute. CC caught both. From here, any step I propose gets priced with CC’s cost formula before I issue it.

I checked CC’s cost figures and they hold up. Configurations per point = C(n,3)²: 4² = 16, 20² = 400, 56² = 3,136. Multiplying through by 158 points, the per-configuration times and spot’s ~4× slowdown gives 95, 1,750 and about 14,900 core-hours.

What that means for the settling pass. At 4 nodes, each cluster sees only 4 triples of nodes. The (c) pilot is already under-resolved for the oscillating classes at 8 nodes. So the settling pass shows the extraction holds at 4 nodes, and we don’t yet know it holds at real resolution. The round 80 stop wording, “extraction viable under the estimator’s kernel”, claims more than that. It gets narrowed now, whatever happens next.

Why the diagnostic comes first:

What it does: a 6-node check at the kernel points carrying the most weight.
If the gap moves: the pass was an artifact of the coarse grid, N6-2 pauses with an honest record, and no port is needed.
If it holds: the port measurement becomes worth its cost. At that point you decide whether to share the 4090 with the ARSv2 session.

That uses spot now, under the cap, on the question that decides everything else.

Round 83.

Reword the stop now (close-out, findings §11, L6):
“Settling test PASS at 4 nodes per coordinate (one height, r = 100 and 300, the (3,3) piece only); resolution not established. Extraction viable at 4 nodes; at production resolution, untested.”
Note that round 80’s wording claimed more than this.
Round 82 item 4 is withdrawn as designed. The 0.5% denominator is uncomputable and ψ's weights were missing. Keep the |c_a c_b| weights in the plan.
Node diagnostic. Cap 300 spot core-hours, estimate ~265. Commit before computing:
Points: the 12 kernel points with the largest |kernel weight × ψ weight| at each of r = 100 and r = 300 (24 points), selected by that rule alone.
Compute: brute force and extraction at 6 nodes. Reuse the 4-node values.
Report:
the change from 4 to 6 nodes in the kernel-weighted partial sums of brute force and of the gap;
the change in brute force, as the 4-vs-6 quadrature-error estimate from the sealed rule, restricted to these points.
Reading: a diagnostic, not a gate, and asymmetric.
If the partial gap changes by more than 1% of the partial brute-force value at either r, record the settling pass as a 4-node artifact. N6-2 then pauses.
Otherwise, record “no 4→6 movement at the dominant points”. That makes no claim of convergence.
Cost model in the plan: write the formula (configurations C(n,3)² per point × points × seconds per configuration × spot factor 4.08) into N6-2_PLAN.md. Price every proposed step with it before it’s issued.
4090 port: not now. If item 3 doesn’t trigger a pause, Will decides on sharing the 4090 with the ARSv2 session before a one-piece benchmark is measured.

## Eighty-fourth round (2026-10-25) — node diagnostic: artifact; N6-2 paused; node audit; stop wording; TOOLKIT §9 rule; cost model; L7 (verbatim)
Round 84.

Let r = 300 finish. Report both r against the committed reading. Record the cap breach: ~595 core-hours against 300, caused by the slowdown at 48 processes.
Record the reading: the settling pass is a 4-node artifact. N6-2 is paused. Add the U(N) node-convergence table (4–16 nodes) to the record as a known answer.
Node audit. For each stage (b) ζ result, state the node count it ran at: G-b3, the averaging test (8/16 heights), the settling test, and the class-content attributions in close-out §3–§4. Mark every result below 8 nodes “unresolved; reading not established”. The sealed G-b3 FAIL stays as sealed, and its attribution (beat or leak) is marked not established. Strike the round 81 sentence “the G-b3 FAIL was the proxy average’s leak”.
Stop wording: “Paused. No stage (b) ζ measurement at resolved quadrature exists. U(N) needs 8–10 nodes; ζ needs ≥ 10 (≥ 14,400 configurations per point). Resumption requires a faster evaluator and is a new arc, Will’s call.”
New standing rule, in TOOLKIT §9: a gate comparing two estimates is valid only after each estimate is shown converged at the settings used, against a known answer where one exists. Note that this caught N6-2.
Cost model: add the per-process slowdown as a function of process count. New run rule: if the first wave’s mean task time exceeds the model by more than 25%, stop and report before the second wave.
L7 (the spectral route): update its note. It is now also the candidate if a faster brute-force evaluator proves infeasible.

## Eighty-fifth round (2026-10-25) — n = 6 stopped; G-b3 VOID; TOOLKIT §9.E asymmetry; new arc RQ1 (ℤ[√2] prime angles) (verbatim)
Round 85.

n = 6 stopped at the time box. Status: “stopped; resumption needs a ≥10-node evaluator or L7, as a new arc.”
G-b3 reclassified VOID. The sealed rule’s quadrature branch was never computed. Measured now, it exceeds the 4-node values. The 1%-alone shortcut is valid for PASS claims only, never for FAIL. Note that round 82 accepted the shortcut. Add the asymmetry to TOOLKIT §9.E.
New arc RQ1: real-quadratic prime angles in ℤ[√2]. Time box: two sessions. The cost model and first-wave rule apply.
Step 0 (no compute). Report:
Phase 34d: what it computed on Gaussian prime angles, its readouts and results, and whether it tested Rudnick–Waxman.
Literature: Rudnick–Waxman, arXiv:1705.07498, Conjecture 1.2; the refined lower-order conjecture for Gaussian sectors; Hecke’s equidistribution of real-quadratic prime angles; any real-quadratic analogue. Primary sources or UNVERIFIED.
Derivation for ℤ[√2]:
The angle θ(𝔭) = log|π/π′| / (2 log ε) mod 1, with ε = 1+√2. Show it is well defined under units.
The characters λᵏ, and how their analytic conductors grow with k.
The leading-order sector-variance prediction. Will’s reviewer’s heuristic is N/K · min(1, 2 log K / log N); derive it or refute it.
Lower-order terms, if they can be derived.
If no definite formula comes out, RQ1 is exploratory: a gallery, no verdict.
Step 1 (build and gates; may run now).
Generator: split primes p ≡ ±1 mod 8. Solve a² − 2b² = ±p in exact integer arithmetic, and reduce to a fundamental domain. Each split prime gives two ideals, at θ and −θ. Exclude 2 and the inert primes. Assert N(π) = ±p for every prime.
Gates:
The sector-variance estimator on uniform i.i.d. points gives exactly N/K (binomial).
CUE eigenphases give the exact arc number variance.
The same pipeline on ℤ[i] reproduces Rudnick–Waxman’s published numerics, within a tolerance stated before running.
Witnesses that must be flagged: inert primes included (a spike at θ = 0), and double-counted conjugate pairs.
§9.E applies: show the statistic is stable across two values of X before comparing anything.
Step 2 (data; may run now). Generate the angle archive to X = 10¹⁰ (10¹¹ if the cost model says it fits). Hash it, and compute no statistic from it. Then draft the reading seal: the prediction, the K grid, the tolerance, and both X values.
Step 3. Read only after Will approves the seal and its OpenTimestamps receipt is Bitcoin-attested. Pinned environment, double read.
Report Step 0, the Step 1 gates and the costs before the seal.

## Eighty-sixth round (2026-10-25) — 34d defect banners + sibling search; G3 FAIL as sealed; Chen cross-check; seal (B) amended; ℤ[i] archive; X = 10¹² reserved (verbatim)
Round 86.

Phase 34d defect.
Banner the affected 34d sections in place (ℤ[i] and ℤ[ω]). The defect: half-sample averaging maps the ratio r to (r+1)/2, toward the comparison value 1, so the “within 1σ” verdicts are not established.
Sibling search across specarith for variance or count ratios averaged over random subsamples. Run a reproducing test at each site.
Write a ledger note for Will to hand to ARSv2.
G3: FAIL as sealed. Cause: the convention of Rudnick–Waxman’s Figure 1 is unidentified; the pipeline is verified against 34d’s angle set and against both estimators. No further convention trials.
Post-hoc cross-check: Chen et al.’s published code, version-pinned, run on our ℤ[i] angle set at the same X. Commit the agreement tolerance first.
Secondary: their Figure 1.
Wording fix: the X-dependence is finite-size behaviour, not a §9.E convergence issue. The statistic is exact at fixed X.
Seal reading (B), with these amendments:
B2: derive the heuristic offset (expected to be about Δlog c / log N, roughly +0.08 at 10¹¹), and the SE at each β, before sealing. The pass criterion is the sign. Report the magnitude against the heuristic. If unpowered at any β, mark it so.
B1: state the basis for the 0.05 tolerance from the lower-order estimate.
B3 replaced: both B1 and B2 must hold at both 10¹⁰ and 10¹¹. Report the X-dependence; don’t gate on it.
Matching variable: N = the number of prime ideals.
Data: generate the ℤ[i] archive to 10¹¹ (~30 core-hours). Hash it and read nothing.
X = 10¹² is reserved unseen for a possible option (C) prediction, adapting Chen et al.’s refined conjecture to ℤ[√2]. No statistics at 10¹².
Order: final seal → Will approves → OpenTimestamps receipt Bitcoin-attested → read, in a pinned environment with a double read.

## Eighty-seventh round (2026-10-25) — B1 dropped (descriptive D(β)); B2 as amended; Chen primary not needed; archives; seal to Will; cost recalibration (verbatim)
Round 87.

B1 → option (iii). Drop B1 as a gate. Report D(β) = ℤ[√2] − ℤ[i] at matched N, at every β on the grid, at both X, with SEs. It is descriptive, with the heuristic’s Δlog c / log N curve overlaid. Record the reason in the seal: the heuristic’s saturation timing is contradicted by our own ℤ[i] data at 10⁸, so a B1 FAIL couldn’t be attributed.
B2 as amended:
Gated on sign at β = 0.40 and 0.45 at both X, and at β = 0.30 at 10¹¹. β = 0.20, and β = 0.30 at 10¹⁰, are UNPOWERED.
Magnitude reported against the derived offset (~1.85/log X).
Chen et al.: the secondary check passes (25 points within 0.0014, tolerance 0.01), which validates the angle set and the statistic. Primary (Mathematica): “blocked; not needed”. No Wolfram activation.
Data: launch the ℤ[i] archive to 1.01·10¹¹ once the ℤ[√2] archive is done. Hash both and fill seal §6. Read nothing.
Finalize the seal and send it to Will. Order after his approval: stamp → wait for the Bitcoin attestation of the OpenTimestamps receipt → read, in the pinned environment, as a double read in separate processes.
Cost model: note that archive-type tasks ran at 0.43× the model. Recalibrate that task class.

## Eighty-eighth round (2026-10-25) — seal not approved; SE recalibration on mirrored sets; witness rebuilt under §9.D; version drift; angle precision; ℤ[i] map; estimator check on spot; order, memory cap, attribution (verbatim)
Round 88. Seal not approved yet; fix these, then resubmit.

SE model and mirror pairing. Recalibrate c on symmetrised sets: draw N/2 points and add their mirrors at 1 − θ, for both Poisson and CUE-like data. Recompute SE_diff and the gating. Any cell below 2·SE_diff becomes UNPOWERED. Expect β = 0.30 at 10¹¹ to drop out.
Witness, rebuilt under §9.D, on symmetrised synthetic sets at the archives’ matched N:
Null: remove the 1/32 reasoning, since the gated cells are correlated (same data across β, and 10¹⁰ is nested in 10¹¹). Measure the B2 rule’s false PASS rate with ≥ 100 replicates. Commit a maximum rate before running, e.g. ≤ 0.10.
Planted: mixtures of a rigid lattice fraction ρ and i.i.d. points (R ≈ 1 − ρ). The two sets differ by a known ΔR of about the heuristic size at each gated β. The rule must read PASS in ≥ 90% of replicates.
Report the empirical SEs against the model.
Witness failure → the read is VOID.
Version drift.
State what differs between rq1_angles.py a30f02ea and 7764c23e, and confirm the ℤ[√2] generation and angle path is unchanged.
Regenerate a seeded random sample of 10 ℤ[√2] segments bit-identically, in addition to segments 0 and 999.
Angle precision. Use primes in a window just above 1.01·10¹¹, outside both archives. Compare float θ against mpmath (50 digits), and check that multiplying by a unit shifts θ by exactly 1, for both fields. Report the maximum |Δθ| against the smallest window, 1/K_max.
ℤ[i] map: state θ for ℤ[i] explicitly in §1.
Estimator check: rerun READ_ESTIMATOR_CHECK on spot in the pinned ph6c environment (numba 0.68).
Order: add “re-check the sha256 of rq1_read.py and rq1_angles.py on spot against §6” before the read. Add a memory cap per read process.
Attribution:
PASS supports the heuristic’s field dependence through the conductor constant, and its direction.
FAIL means that field dependence does not show as predicted at these X, for example because lower-order terms dominate.
VOID: a cmp mismatch, a witness failure, or a hash mismatch.
Items 1, 2, 4 and 6 use synthetic data or primes outside the archives only. Run them on spot now; nothing is read from the archives.

## Eighty-ninth round (2026-10-25) — B2 margin rule (k selected on the witness replicates, confirmed on fresh seeds); SE model checked against the witness; planted symmetrisation confirmed (verbatim)
Round 89. Commit this to the seal before any witness result is read.

B2 margin rule. Rule: D > k·SE_diff at every gated cell.
Selecting k: after the witness lands, re-score the existing replicates at k ∈ {0, 0.5, 1.0, 1.5}. Choose the smallest k that gives null false PASS ≤ 5/100 and planted PASS ≥ 90/100. No new compute is needed for this step.
Confirmation: run 100 fresh null and 100 fresh planted replicates at the chosen k, on new seeds and with the same criteria. Selection and confirmation are reported separately.
If no k qualifies, or confirmation fails: B2 is UNPOWERED at these X. The read becomes descriptive only: D(β) at every β, plus the magnitudes. No verdict.
Reading: the rule replaces the sign-only one. PASS iff the confirmed rule holds at every gated cell. FAIL iff any gated cell fails it.
Check the SE model against the witness. If the empirical SE_diff exceeds the model by more than 20% at any gated cell, recompute offset/SE from the empirical SE. Any cell below 2 becomes UNPOWERED. Then select k on the remaining gated cells.
Confirm symmetrisation: the i.i.d. part of the planted mixtures is symmetrised (N/2 points plus their mirrors), as in the null arm.
Report the selection table (null and planted counts at each k), the confirmation counts, and empirical against model SEs, together with the seal for Will.
Order otherwise unchanged. Pushes stay with Will (5 unpushed).

## Ninetieth round (2026-10-26) — B2 statistic T with a null-calibrated threshold and a per-cell guard; replaces round 89's k-grid rule (verbatim)
Round 90. Commit before any witness result is read; this replaces round 89’s k-grid rule.

B2 statistic. T = Σ over the gated cells of D_c / (s_c·SE_diff,c). The SE check and the rescaling s_c (your choices 1 and 2) stay as committed. Cells that the SE check drops to UNPOWERED leave the sum.
Threshold.
On the existing null replicates, compute T for each one and set t = 2·SD(T_null), with no centring.
t is then frozen for the confirmation run and for the read.
The null replicates must store D per cell per replicate. If they don’t, report that before scoring.
Guard. No gated cell may have D_c < −2·s_c·SE_diff,c.
Rule. PASS iff T > t and the guard holds. FAIL otherwise. The per-cell D_c and their signs are always reported.
Selection criteria (same bars):
null false PASS ≤ 5/100;
planted PASS ≥ 90/100, on the existing planted replicates (round-88 design, kept as committed).
Report T’s null mean and SD, t, and both counts.
Confirmation. 100 fresh null and 100 fresh planted replicates on new seeds, scored at the frozen t and the guard, with the same bars. If selection or confirmation fails, B2 is UNPOWERED and the read is descriptive only, as round 89 committed.
The k-grid is withdrawn, not kept beside T. One rule only.
Your choices 1–3 from round 89 are accepted as written.

### Round 90 note (2026-10-26; Will, verbatim) — t's SD reading confirmed
Yes, that’s what I meant. RMS about zero, divided by 100, is the right reading. Centring would subtract any bias in the null mean and hide it. The uncentred form keeps a bias as part of the threshold, which is the safer direction.

Everything else is as specified:

There’s one rule, committed before any witness result was opened.
Selection stops with “D not stored” if a value is missing, so a missing D can’t be scored as zero.
The read refuses to run without the confirmation file.

CC’s note that fitting t and scoring on the same replicates flatters the null count is correct. That’s what the fresh-seed confirmation run is for. Its forecast has one weak case: if the cells are as correlated as they can be, the planted arm reaches 90 of 100 only 78% of the time. The witness will show which case we’re in. If it fails, the read becomes descriptive, which is an outcome the seal already allows for.

## Ninety-first round (2026-10-26) — seal approved once these edits are in; archive integrity pins before the read; one heuristic file; SE-model attribution (verbatim)
Round 91. Seal approved once these edits are in, with no change to the rule.

Archive integrity before the read:
Add both MANIFEST.json files to read_pins.sha256, with the §6 hashes aa6d15fc… and 8fd61856….
Add a pre-read step that checks every segment file of both archives against its manifest hash. Any mismatch: VOID (hash), no read.
If rq1_read.py already does this, say where; otherwise don’t change the read code.
Text: replace “the conjunction’s power” in §5 with “the T rule’s power”.
Heuristic overlay: one file (HEURISTIC_B_MIRROR.json) for both the offsets and the D(β) overlay. Pin its sha256 in §6.
Attribution, add: “The SE model is calibrated on synthetic mirror-symmetric sets (c = 0.627, the Poisson minimum; CUE-like sets give 2.6–5.0). Its validity for the arithmetic data is assumed, not tested. A PASS is conditional on it.”
Recommit, report the diff, and then: stamp → wait for the Bitcoin attestation and verify it on two explorers → sha256sum -c on spot (code, JSONs, manifests, segments) → double read under the caps → cmp.
Pushes stay with Will.

## Ninety-second round (2026-10-26) — RQ1 session 2: findings separation, open leads, post-hoc conductor-scaling collapse, 10¹² pricing, draft collapse seal (verbatim)
Round 92: RQ1 session 2.

Findings. B2 PASS as sealed (direction; conditional on the SE model). Keep the descriptive size, shape and scaling disagreement with the flat-offset heuristic clearly separate from the verdict.
Record the 0.90 plateau as an open lead (possibly Chen et al.’s lower-order terms).
Record β = 0.90 as outside calibration.
Post-hoc descriptive check, no verdict: the conductor-scaling collapse.
The heuristic’s field dependence enters only via 2 log k + C_F. In the continuum limit that gives R_ℤ√2 = R_ℤi, a = e^{ΔC/2} = π/(√2·log(1+√2)) ≈ 2.520.
Verify this identity on the heuristic formula numerically first.
Then, at 10¹⁰ and 10¹¹ on the already-read archives, compute R_ℤi against R_ℤ√2 on a fine K grid (e.g. β in steps of 0.01, 0.20–0.70). Report residuals with SEs, and D(β) against R′_ℤi·log a / log N.
Label everything post hoc.
Price the 10¹² test with the cost model: archive generation for both fields, the read, and disk space (raw versus binned storage, and the binning error against 1/K_max for β ≤ 0.70). Report it before generating anything.
Draft only, no seal yet: if item 2 looks coherent, draft a 10¹² collapse seal. Statistic, tolerance basis, and witnesses: a planted known shift and an unshifted null. ℤ[ω] can be added as a third field with its own C, if Step 0 can derive it.

### Round 92 note (2026-10-26; Will, verbatim) — for the 10¹² draft, no action until the collapse check reports
Note for the 10¹² draft (no action until the collapse check reports):

Mount guard. The generator and read must refuse to start unless mountpoint -q /mnt/data succeeds. Will is fixing the fstab UUID.
Collapse witnesses need a K-dependent synthetic family. i.i.d. sets have flat R and can’t detect a shift.
Family: mirror-symmetrised jittered lattices, where R depends on K·σ.
Planted arm: σ-ratio a gives R_A(K) = R_B(aK) exactly.
Null arm: equal σ.
Shape: choose σ so the synthetic R(K) matches the data’s shape and slope over the gated range.
Witness N. Price witnesses at reduced N (~10⁹, ≥ 40 points per window at K_max) with the same K grid. Include a check of SE at reduced versus full N at 2–3 values of K. Re-cost with this design.
ℤ[ω]: include it in the draft if Step 0 derives C_ℤ[ω]. Report the derivation.

## Ninety-third round (2026-10-26) — collapse recorded (approximate in both regimes); no crossover-only seal; RQ1-b Step 0 (Chen et al. refined formula for a general quadratic field); 10¹² archives now; environment re-pin rule (verbatim)
Round 93.

Collapse findings. Record as written, with one addition: the crossover residual is up to +3.2 SE at 10¹¹ (D/shift 1.01–1.30). So the pure rescaling is approximate in both regimes, and the residual changes sign at β ≈ 0.52–0.53 at both X.
No crossover-only collapse seal (option 1 declined: it tests a model already known to be approximate).
RQ1-b, Step 0 (no compute; time box one session).
Derive Chen et al.’s refined sector-variance formula for a general quadratic field. State every field-dependent constant (conductor, and any L′/L(1, χ), Euler–Kronecker or residue terms). Primary sources or UNVERIFIED.
Verify C_ω (d·(wk/2)² → 27k²) against a source or the explicit formula.
Then, labelled post hoc: compute the formula’s zero-parameter D(β) and the full R curves for ℤ[√2] and ℤ[i] at 10¹⁰ and 10¹¹ against the read data. Report residuals with SEs in both regimes.
If coherent, draft a 10¹² full-curve seal for three fields, using the jittered-lattice witness at reduced N. If not, report and stop.
Archives now. Generate the 10¹² archives for ℤ[√2] and ℤ[i] on /mnt/data, with the mount guard; hash them; read nothing. ℤ[ω] waits for C_ω. Cost model and first-wave rule apply.
Environment. Spot’s kernel changed (7.2.11 now). The collapse check reproduced the sealed cells bit-for-bit, which is good. Any new seal re-pins the environment and reruns the estimator check.

## Ninety-fourth round (2026-10-27) — final step of RQ1-b (fair check on Chen et al.'s own statistic, formula at finite X); RQ1 close-out; 10¹² archives reserved (verbatim)
Round 94: final step of RQ1-b; RQ1 closes after it, whatever the result.

Fair check (post hoc, zero parameters).
Compute Chen et al.’s statistic exactly as defined: log N𝔭 weights, inert primes included at θ = 0, Φ = 1_(0,1]. Run it on the 10¹⁰ and 10¹¹ data for ℤ[√2] and ℤ[i]. The inert primes are generated fresh; nothing at 10¹² is touched.
Validate first: reproduce your ℤ[i] check against Chen’s figure at 10⁹.
Evaluate the general-field formula at finite X, including the contour integrals.
Report the residuals for each field and for D, with SEs, in the rigidity range and around λ = ½.
The two analogy substitutions stay marked UNVERIFIED in the report.
Branch:
Coherent in the rigidity range: draft a 10¹² seal of the general-field formula on Chen’s statistic for ℤ[√2], ℤ[i] and ℤ[ω]. Then ℤ[ω]’s archive can start. The bifurcation region is excluded from any gate.
Not coherent: no seal.
RQ1 close-out, written in either branch. RQ1_FINDINGS gets a summary section:
the sealed B2 PASS (direction, conditional on the SE model);
the descriptive results: D peaks at the bifurcation; the conductor rescaling is approximate in both regimes; the flat-offset forms (heuristic and Chen) miss in the rigidity range and have no field dependence above λ = ½, while the data show D ≈ +0.03 there;
the 34d half-sample defect and its banners;
open lead L8: field dependence of the sector variance peaks at the rigidity–randomness crossover, where no available formula applies.
Reserved: the 10¹² archives for ℤ[√2] and ℤ[i], hashed and unread.
Archives: let the 10¹² generation finish, then commit manifests and pins.

## Ninety-fifth round (2026-10-27) — RQ1-c: a 10¹² seal of theory-light predictions (P1 replication, P2 scaling, P3 crossover location, P4 ℤ[ω]); ℤ[ω] archive queued (verbatim)
Round 95: RQ1-c, a 10¹² seal of theory-light predictions. Applies in either round-94 branch. RQ1 itself closes as written; this is a new arc with a two-session time box.

Queue the ℤ[ω] archive (10¹², with the mount guard) to start automatically after ℤ[i]. Before generating, state its θ map (arg/(π/3), with a mirror) and split rule (p ≡ 1 mod 3). Only 34d’s ≤ 10⁸ data has ever been seen.
Draft one seal with four predictions. All are committed from the 10¹⁰ and 10¹¹ results before anything at 10¹² is read.
P1 (replication): the B2 T rule plus guard at 10¹², with t recalibrated by witnesses at that N. Reduced-N witnesses are allowed if the SE check at 2–3 values of K passes.
P2 (scaling): at the B2 cells and the crossover cells, a pre-committed prediction for D(10¹²) under each law: ∝ 1/log X, ∝ 1/log² X, and X^{−δ} with δ from the two points. Propagate the SEs, including the nesting correlation. A law is consistent iff |D − pred| ≤ 2·SE. Compute separability first; any cell where the laws differ by < 3·SE is UNPOWERED for P2.
P3 (crossover location): the sign change of the collapse residual lies in β ∈ [0.51, 0.54] at 10¹². Report the location with its resolution.
P4 (ℤ[ω]):
Ordering R_ℤ√2 > R_ℤω > R_ℤi at matched N, in the rigidity cells and at all three X, which are all unseen for ℤ[ω]. It needs its own witnesses.
The crossover ratio D_ωi / D_√2i against 0.28: descriptive, or gated with a tolerance justified by the 0–30% collapse error.
Cost each item with the model. Witnesses at reduced N use the jittered-lattice and i.i.d./lattice designs. Send me the draft, the costs and the separability table before sealing.

## Ninety-sixth round (2026-10-27) — RQ1-c choices: P1 exact replication; P2 descriptive; P3 gated; P4 gated at β = 0.55; seal prerequisites (verbatim)
Round 96: RQ1-c choices.

P1: exact replication, the same B2 cells and rule at 10¹², with t recalibrated by witnesses. No added cells. Record the power under each law (0.89 / 0.82 / 0.34) in the seal. Attribution for a FAIL: consistent with the steepest decay law, not a refutation of the 10¹⁰/10¹¹ PASS.
P2: descriptive only. Commit each law’s predicted D(10¹²) at the four cells, with propagated SEs, in the seal now, and report where the data land. No gate, no redesign.
P3: gated as drafted. The sign change of the collapse residual lies in β ∈ [0.51, 0.54], with the witness confirming that resolution.
P4:
Gate the ordering R_ℤ√2 > R_ℤω > R_ℤi at β = 0.55, only at the X where the predicted ℤ[ω]–ℤ[i] separation is ≥ 2·SE (report which), with three-set witnesses.
The rigidity cells and the 0.28 ratio stay descriptive.
Seal prerequisites: re-pin the environment (kernel 7.2.11), rerun the estimator check, validate the binned estimator at the gated β, and run the full-N SE check for the reduced-N witnesses.
Round 94: if its fair check comes out coherent, propose any addition as a separate P5 for my review. Don’t fold it in.
Send the final seal for Will’s approval. Pushes stay with Will.

## Ninety-seventh round (2026-10-27) — RQ1-c SE-check design: block estimate, validated first (verbatim)
Round 97: SE-check design.
Use the block estimate. About 500 independent arcs on the mirror half; the block width must be ≥ 10× the window at every gated cell. Report the block width and the window at each cell.
Validation first (N = 10⁹, 100 replicates, both synthetic families). Pass iff the block SE agrees with the replicate-to-replicate SD within ±15% at β = 0.40, 0.45 and 0.55. Commit before running. On failure: report and stop, with no automatic fallback.
Then compare: block SEs at full N against reduced N at the same three β, with the existing 20% bar. If that passes, use reduced-N witnesses; if not, report.
Then price and run the P1, P3 and P4 witnesses, write the manifests, and send the final seal to Will. Pushes stay with Will.

## GEO1 opened (2026-10-27; Will, verbatim) — length spectrum of the modular surface, then the Picard group
For later: GEO1: the length spectrum of the modular surface, then the Picard group. New arc, two-session time box. Step 0 starts now with no compute; spot work queues after RQ1-c's archives and witnesses.
Step 0 (no compute). Primary sources or UNVERIFIED.
Modular surface. Closed geodesics ↔ primitive hyperbolic classes ↔ classes of indefinite binary quadratic forms. Lengths 2·arccosh(t/2) for integer traces t ≥ 3. Multiplicity at trace t = Σ h(d) over the discriminants d with t² − 4 = d·u².
Known answers to state exactly:
Sarnak (1982): Σ_{ε_d ≤ x} h(d) ~ Li(x²).
Mean multiplicity of lengths, ~ c·e^{ℓ/2}/ℓ: derive c, or cite Bogomolny et al.
Cutting sequences of closed geodesics (Series 1985): the partial quotients over all closed geodesics up to length L tend to the Gauss–Kuzmin law P(a = k) = −log₂(1 − 1/(k+1)²).
Picard group PSL(2, ℤ[i]), stage 2. Complex lengths from traces in ℤ[i]. Multiplicities via binary Hermitian forms. The prime geodesic theorem for Bianchi groups (Sarnak 1983). Rotation (holonomy) angle equidistribution (Sarnak–Wakayama, Duke 1999). Check every one of these against the source.
Look for a non-trivial quantitative prediction we could seal. Candidates: finite-L corrections to the multiplicity law, multiplicity fluctuations, or correlations among rotation angles. If none exists, the arc is known-answer verification plus a descriptive gallery, with no verdicts.
Step 1 (build and gates, once spot is free).
Enumerate the reduced forms and their cycles. Compute h(d) up to a discriminant bound priced with the cost model.
Gates:
brute-force enumeration of SL(2,ℤ) conjugacy classes at small t agrees with the class-number sums;
the R²L² check: t = 6, d = 8, cycle word RRLL;
Sarnak's sum and Gauss–Kuzmin, each within a tolerance stated before running.
Witness that must fail: random L/R words of matched length must not match Gauss–Kuzmin; their run lengths are geometric.
Step 2 (descriptive). The length spectrum with multiplicities; multiplicity growth against the law; the partial-quotient histogram; for the Picard stage, the joint distribution of length and rotation.
Note for later, not now: the cutting-sequence readout (run lengths of any up/down zigzag against Gauss–Kuzmin) is a candidate ARSv2 readout. It waits until after H1.
Pushes stay with Will.

## GEO-KAM1 opened (2026-10-27; Will, verbatim) — Greene residue sweep, metallic tails m = 1…10, standard map
GEO-KAM1: Greene residue sweep, metallic tails m = 1…10, Chirikov–Taylor standard map. New arc, time-boxed to two sessions. No spot until RQ1-c releases it; run on the 4090 desktop’s CPU or on char.

Model and convention. y′ = y − (K/2π) sin 2πx, x′ = x + y′ (mod 1), which is Greene’s normalization. Rotation numbers ω_m = [0; m̄] = (√(m²+4) − m)/2, with convergents p_n/q_n.
Method. Find symmetric periodic orbits of type p_n/q_n by 1-D shooting on the dominant symmetry line (Greene 1979; Kook–Meiss 1989). Compute the residue R = (2 − tr M)/4. K_n is the K at which R crosses a fixed threshold R*. Run R* ∈ {0.25, 0.5, 1.0} and report how sensitive K_c is to the choice. Do not assume the golden threshold carries over.
Precision. MPFR or mpmath at two precisions, which must agree. Fibonacci q up to about 10⁶ and Pell up to about 2×10⁵. Report δ per Gauss step, one continued-fraction digit, so 1.628 and 2.650 never get mixed.
Gates, which must pass before any new number counts:
golden K_c = 0.9716354063(2) (Greene; Fox–Meiss);
golden δ = 1.62795006… (Arioli–Koch).
Sealed before any m ≥ 2 output is read; commit and hash.
The fit window: the last 6 levels at or below q_max.
The joint fit K_n − K_c ≈ A·δ^{−n}, solving for (K_c, δ, A) together.
The decision rule: silver δ is reported as matching 2.44159 or 2.4569 (de la Llave–Olvera–Petrov) only if exactly one of them lies within 3σ. Otherwise report “neither” or “both”.
The silver K_c comparison with 0.957447(6) (Fox–Meiss) uses the same 3σ rule.
Witness that must fail. Run the same pipeline on the e tail [0; 1,2,1,1,4,1,1,6,…]. It must fail the geometric-convergence check, because no single δ fits.
Output. A table of m, K_c(m), δ_m and δ_m/λ_m − 1 with uncertainties, plus residue-versus-K plots per level. Price the run before launching.

## GEO-CM1 opened (2026-10-27; Will, verbatim, "OK we can use this box, but with some updates") — Ford exponent of critical circle-map tongues along metallic paths; read here as replacing GEO-KAM1 (parked)
GEO-CM1: the Ford exponent of critical circle-map tongues along metallic paths. New arc, time-boxed to two sessions. CPU-bound in double-double or MPFR. Spot is still on RQ1-c, so use the desktop CPU or char.

Model. θ ↦ θ + Ω − (K/2π) sin 2πθ at K = 1, a cubic critical point. Paths are the convergents p_n/q_n of ω_a = [0; ā] for a = 1…10, plus the cusp sequence 1/N for N = 2…200.
Method. p/q is locked iff min_x(F^q(x) − x) ≤ p ≤ max_x(F^q(x) − x). Both extremes increase in Ω, so each tongue edge is a 1-D bisection in Ω.
Seed each extremum from a grid with M ≥ 16q points.
Then polish with Newton on the saddle-node system F^q(x) − x − p = 0, (F^q)′(x) = 1, using the chain-rule derivative.
Gate the method by requiring bisection edges and Newton edges to agree to ≤ 10⁻³ of the width.
Width w_n = Ω₊ − Ω₋. Per-step Ford exponent f_n = ln(w_n/w_{n+1}) / (2 ln(q_{n+1}/q_n)). Path exponent f(a) = lim f_n, which equals ln|δ_a| / (2 ln λ_a).
Precision. Widths shrink by roughly |δ_a| per level, and that grows fast with a. Keep going until the edge precision reaches 10⁻⁶ of the width or q hits 2×10⁴, whichever comes first. Run two precisions and require them to agree. For large a only 4–5 levels fit, so extrapolate the ratios with a declared convergence model: geometric correction, fitted (δ, c, ρ).
Gates, before any a ≥ 3 output is read:
golden |δ| = 2.833612, f(1) = 1.0822;
silver |δ| = 6.79924, f(2) = 1.0874 (ORSS 1983);
cusp path f_N → 1.5, the q⁻³ law (Ecke–Farmer–Umberger 1989; CSS 1985). Its slow approach (≈1.44 at N = 24 in the browser preview) is expected. Declare the extrapolation form before reading it, and require the limit to be 1.5 ± 0.02.
Sealed prediction, committed and hashed before reading a ≥ 3:
f(a) is strictly increasing on a = 1…10.
f(a) < 1.5 for every a.
Extrapolated f(∞) = 1.5 ± 0.05.
Report bronze |δ_3| and f(3) as new values (no published value found), with uncertainties.
Witness that must fail. The same pipeline on a quintic critical map (inflection order z = 5) must give f(1) different from 1.0822 by more than 5σ. If it doesn’t, the exponent is λ-bookkeeping and not a property of the universality class.
Output. A table of a, λ_a, |δ_a|, f(a) and the level count, plus the f_n convergence plots per path. One extra figure: f(a) against the per-digit geodesic length 2 ln λ_a. Price the run before launching.

### GEO-CM1 note (2026-10-27; Will, verbatim) — five corrections before go
Nearly a go. The price arithmetic checks out: 16q points × q iterations × 2 edges at q = 2·10⁴ is about 1.3·10¹⁰ evaluations, and at 1.18 ns that’s about 15 s. I don’t have the derivation behind f(a) and the 1.5 limit in this conversation, so I’ve only reviewed the method, not the predicted values. Make sure those trace to a committed derivation. Five corrections before go:

Check every seeded bracket in high precision before bisecting. Double precision is not safe at the deepest levels. After q = 2·10⁴ iterations its rounding error can reach about q·10⁻¹⁶ ≈ 10⁻¹², which is the same size as the narrowest widths. So “only has to find the basin” may fail exactly where it matters, for large a at q ≈ 10⁴. Before bisection, check each bracket end at 30 digits: the right rotation number or sign on each side. If it’s wrong, widen the bracket and re-seed. Report how many brackets needed fixing.
f(a) needs an uncertainty, and large a has few levels. With q ≤ 2·10⁴, a = 3 gets about 8 convergent levels, but a = 10 gets only 4–5 (q = 1, 10, 101, 1020, 10301). An exponent fitted to 4 points is soft. Commit, before reading:
which levels enter each fit, and the correction model;
an SE per a, taken from level-to-level stability (for example, the fit on the last 3 levels against the last 4).
Judge the inequalities with margins. f(a) < 1.5 is hardest to show for large a, where f is supposed to approach 1.5. Commit how “monotonic” and “< 1.5” are judged, for example f(a+1) − f(a) > −2·SE and f(a) + 2·SE < 1.5. Any a whose SE can’t support the judgement is UNPOWERED for that clause, not a PASS.
f(∞) = 1.5 ± 0.05 needs a stated basis. Say where the ±0.05 comes from, given the extrapolation model and the per-a SEs. Using the cusp path as a known-limit test of the extrapolation form is the right idea: commit how far off it may be before the form counts as validated.
Say exactly what the quintic witness must fail. Which clause, and by how much, committed in advance. Also say whether a FAIL on the quintic is guaranteed by known theory, or whether that’s only expected. If it’s only expected, the witness isn’t a clean must-fail.

Standing rules. Since a ≥ 3 is unseen, the usual rules apply even though the computation is deterministic: OpenTimestamps attestation before the read, a pinned environment, and a double read that cmps bit-identical. mpmath is deterministic, so that’s cheap.

### GEO-CM1 go (2026-10-27; Will, verbatim)
GEO-CM1: go, with two additions to the seal before the gates run:

K = 0.5 must-fail: use per-level mpmath precision of about q·log₁₀(1/K) + 20 digits, or cap that path at q ≤ 34. State which.
f(∞) fit: say how an a with no SE enters. Either it’s excluded, or it gets a conservative SE committed now (for example the largest SE among the powered a). The a = 10 UNPOWERED expectation is accepted, and it may extend to a = 8 or 9; report which.

Everything else as committed. Then gates → stamp → attestation → double read → read a ≥ 3. Pushes stay with Will.

### GEO-CM1 re-gate (2026-10-27; Will, verbatim) — post hoc, labelled; the original FAILs stay filed
GEO-CM1 re-gate. Post hoc, labelled as such; the original FAILs stay filed.

Golden and silver.
Verify δ against ORSS 1983 (and the silver source) in the primary text.
New tolerance: half a unit in the last quoted digit, plus 3 SE.
Re-gate on the existing numbers.
Replace the f(∞) clause with a local-exponent clause.
h_a = ln(δ_{a+1}/δ_a) / (2 ln(λ_{a+1}/λ_a)).
Prediction: h_a → 1.5.
Form: h∞ + c₁/λ + c₂/λ², with λ taken at the pair’s geometric mean.
Judgement rules as before: SUPPORT / CONTRADICT / UNPOWERED at ±2 SE, plus the 2·SE(h∞) ≤ 0.03 power clause.
Keep the monotonic and f(a) < 1.5 clauses unchanged.
Cusp validation on fresh data.
Declare f∞ + b/N + c/N², fitted on N ≤ 199 only.
Commit predictions with SEs for fresh N in 200–1000 (a declared subset), then compute them.
Validated iff every fresh point lands within its 2·SE prediction band and the fit recovers 1.5 ± 0.002.
Only then does the form family count for h_a.
Power. Price raising the q cap to about 1.1·10⁵, so a ≥ 6 gains one more level. Raise it only if it costs ≤ 1 core-hour per path.
Then: re-seal, stamp, attest, double read, read a ≥ 3.
Report the quintic’s f(1; z = 5) = 1.1564 descriptively, with a literature check on whether a quintic golden δ has been published.

### GEO-CM1 silver decision and rule refinement (2026-10-27; Will, verbatim; post hoc, labelled)
GEO-CM1: the silver decision and a rule refinement (post hoc, labelled).

Tolerance rule: the source’s stated uncertainty where it gives one, otherwise half a unit in the last quoted digit, plus 3 SE.
Primary gate values: dLOP (preprint, as read; the published 2007 version is unread, so note that). ORSS is a cross-check under the same rule. Golden and silver pass on both; record all four comparisons.
Drop the 2.833612 reference; it comes only through a citing preprint.
Quintic: record the agreement with dLOP (3.0433806 against 3.04337774, 1.6 SE, on a different map family) as a universality cross-check of the method. Still not a gate.
Cap: raise it for a = 8 only (0.78 core-h). a = 8 stays UNPOWERED for the SE clauses.
Then: the cusp verdict on the fresh N → re-seal with the h_a clause → stamp → attestation → double read → read a ≥ 3.
