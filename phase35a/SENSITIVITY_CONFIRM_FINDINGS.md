# Non-circular sensitivity confirmation — FINDINGS (2026-05-19)

**Status:** instrument-validation of transition_diagnostic SENSITIVITY
(asymmetric label — NOT an AM discovery / §3 / Class-II). Data
`sensitivity_confirm_results.json` (18w MP, bit-identical-serial, 586s).
brief-and-hold; Class II blocked; no §3 adjudication; banked verdicts
& §3-(A) `S3A_REDUCED` unaffected (this ADDS, does not reopen).

## Result — VERDICT: SENSITIVITY_VALIDATED_NON_CIRCULAR

Exact pre-registered sharpening criterion (disjoint AND gap ≥
max(sub_spread,sup_spread) on the exact 16-φ∈[0,0.5) period-0.5
α-ensemble) — **verbatim unchanged from the run that correctly FAILED
at N=2584** — holds at ALL three pinned robust N:

| N | sub_spread | sup_spread | gap | gap/sup | PASS |
|---|---|---|---|---|---|
| 50000 | 0.00029 | 0.12286 | 0.37497 | 3.05 | ✓ |
| 70000 | 0.00003 | 0.07656 | 0.17740 | 2.32 | ✓ |
| 100000| 0.00015 | 0.00715 | 0.49614 | 69.43 | ✓ |

No goalpost moved: same exact criterion, only N changed (to the
lever-cost-pinned robust regime, ≥3 N, conservative PASS-iff-all,
deliberately OFF the thin-margin onset N*≈4.3e4). Pre-flight
(discriminant_exact_question_check) recorded before the run. Margins
≥2.3 (N=7e4 tightest, still ≫1 — residual damped-modulation; not
marginal).

## What this establishes / does NOT

- **Establishes:** the SENSITIVITY half of 35b — on circular
  Phase-20.5 footing, `NOT_ESTABLISHED` at N=2584 — is now
  NON-CIRCULAR at N≳5e4: the sub-quadrant statistic separates the
  PROVEN subcritical/supercritical regimes by more than the
  substrate-generated α-null's own EXACT finite-N φ-spread.
- **Combined with banked no-false-positive VALIDATED ⇒ BOTH halves of
  the non-circular transition_diagnostic validation are established.
  Step-1 ("finish what §Q3 interrupted") COMPLETE; the tooling-
  confidence payoff delivered (non-circular, on a mathematically-
  proven-transition substrate).**
- **Does NOT claim:** an AM discovery / §3 / Class-II calibrator.
  Intrinsically **N-scoped**: validated non-circular in the N≳5e4
  regime where the substrate's α-null φ-structure is sub-dominant; at
  N=2584 correctly remains NOT-ESTABLISHED. That N-scope IS the
  honest complete statement (= what the dense-log-N lever-cost work
  pinned).

## Step-1 net (complete)
leg VALIDATED → zoo-gap RATIO-CLEAN-CONFIRMED → 35b no-false-positive
VALIDATED (banked) → 35b sensitivity VALIDATED non-circular @N≳5e4.
The exploration arc landed fully: flat-then-steep mechanistically
explained, ladder non-representativeness established, lever-cost pinned
(N*≈4–5e4 by direct dense measurement), sensitivity half confirmed
non-circular at that N. First clean PASS of the arc with NO preceding
criterion-misspec — the discipline-fix (exact pre-registered criterion
+ rigorously-pinned N) paying off. §3 still sits inside the arc;
Step-2 §3-(A) `S3A_REDUCED` is the remaining live track (own effort).
