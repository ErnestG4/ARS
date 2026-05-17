# Phase 35a §Q3 — HALT extraction FINDINGS (2026-05-17)

**Status:** SCOPING. Executed exactly per the signed-off rev-6 two-boundary
spec (after an off-by-one Fibonacci index was caught pre-results, fixed,
relaunched — commit history). NO §3 adjudication; §3 untouched;
brief-and-hold stands. Data `phase35a/q3_halt_results.json`, log
`phase35a/q3_halt_log.txt`, script `phase35a/q3_halt_extraction.py`.
Run ≈ 2.4k s/λ (U_NOT_REACHED ⇒ full ladder to F_26 each).

## Pre-registered returns (faithful to spec)

| λ | L | U | cross-check (per script) |
|---|---|---|---|
| 0.10 | **144 (censored)** | **U_NOT_REACHED** @F_26=121393 | DISAGREE (emp L=144 vs analytic 440) |
| 0.30 | **144 (censored)** | **U_NOT_REACHED** @F_26 | AGREE (144 vs 58) |
| 0.50 | **144 (censored)** | **U_NOT_REACHED** @F_26 | DISAGREE (144 vs 24) |

- **`U_NOT_REACHED` is decisive, not marginal.** At the top rung the paired
  increment is ≈0.111 against a paired-difference floor ≈1e-6 — ≈10⁵× the
  floor, and still *growing* (ΔW1δ 0.095→0.111 over the last step). Robust to
  any reasonable c_U or n_φ by inspection (off by 4–5 orders of magnitude) —
  a confirmatory robustness sweep would confirm the obvious at ~4 h cost and
  is therefore **deliberately not run** (over-generation = method-compromising;
  Will's "don't compromise the method" constraint).
- **L = 144 is CENSORED** (= smallest ladder rung F_12). The onset was not
  bracketed below it ⇒ the cross-check AGREE/DISAGREE labels are **not clean
  doubly-certified statements**. The meaningful part of the cross-check is the
  *ordering* of the analytic-L (440 > 58 > 24 as λ = 0.10 < 0.30 < 0.50),
  which is consistent with the perturbative expectation (larger λ ⇒ wider
  gaps ⇒ resolved at smaller N); the empirical side is censored.

## Substantive structure beyond the returns (the horizon)

1. **W1δ-vs-N is U-shaped (non-monotone), not a monotone climb.** Each λ:
   W1δ *decreases* from N=144 to a minimum at N≈3–7k (λ0.10 ≈0.0025@2584;
   λ0.30 ≈0.0033@6765; λ0.50 ≈0.0039@6765), then climbs steeply to ≈0.292
   at F_26 (per-step drift ≈2.3–2.4×, tapering to ≈1.6× at the top — *not*
   converging).
2. **Reference-dependence caveat (load-bearing).** §Q3's IDS reference
   (N_ref=196418, 1 φ) differs from the certified campaign's (NREF=24000,
   2 φ). W1δ-to-clock depends on reference resolution, so §Q3 absolute W1δ
   are **not comparable** to the certified-grid W1δ. The rev-6 forward-
   analysis premise ("0.013→0.039→0.113 monotone triple toward 0.74") was a
   property of the *coarser* reference; the high-resolution reference reveals
   the U-shape. The qualitative conclusion (`U_NOT_REACHED`, pre-asymptotic)
   **holds and is strengthened**; the monotone-triple premise does not.
3. **Large-N λ-collapse.** At F_26: W1δ = 0.29183 / 0.29185 / 0.29187 for
   λ = 0.10 / 0.30 / 0.50 — identical to 4 decimals; per-step drifts
   near-identical across λ. In the large-N regime the certified-leg
   W1δ-to-clock is **essentially λ-independent** across the small-λ corner.
   A strong, surprising structural fact for §3 (the divergent branch is not
   coupling-controlled in the way a perturbed-clock picture would predict).
4. **Methodological catch — the pre-registered L conflates two effects.**
   Small-N W1δ is inflated by *coarse sampling of a high-resolution
   reference* (an under-resolution artifact: a 144-point cell mapped through
   a 196418-point IDS), which decreases as N grows. The L-rule
   (first W1δ > c_L·floor) therefore fires at the ladder floor on the
   *artifact*, not on Cantor-structure onset. The genuine structure-onset is
   the **U-curve upturn** (the minimum, N≈3–7k), where the artifact has
   decayed and finite-N Cantor/stranding structure begins to drive W1δ up.
   The "L" that §3 / Class-II / P3 actually want (onset of *Cantor*
   structure) is the upturn, **not** L=144. Surfaced; **not auto-fixed** —
   an L-definition change (extend the ladder below F_12; or define L as the
   upturn) is a spec call, Will's, not an autonomous scoping decision.

## Bearing on the 35a decisions (NOT a §3 adjudication — input only)

- **`U_NOT_REACHED` confirmed and strengthened** ⇒ the §3-go is, on this
  evidence, a go on the **analytic half only**; the empirical (A)/(B)
  model-vs-grid decision is `MALFORMED_FROM_DATA` / structurally deferred
  (the grid does not reach a converged domain within F_26, and is *diverging*,
  not slowly approaching). Reinforces last turn's highlight 2.
- **Arc-level risk reinforced (highlight 3):** small-λ AM's certified-leg
  W1δ-to-clock has **no finite-N-reachable stable law within F_26** and is
  *diverging* — and the divergence is **λ-independent** at large N. This
  bears on 35b's well-posedness and is a candidate *arc-reshaping finding*,
  not just a §3 internal. The λ-collapse is a new, concrete structural clue
  the analytic half (highlight 1's f(α)→NNS-relation question) must explain.
- **Class-II/P3 fallback (highlight 4):** the maximal honest statement now
  is the U-curve itself — a clock-proximal *minimum* at N≈3–7k (not a
  converged regime), with structure-onset at the upturn and no convergence
  thereafter. P3's HALT, properly defined, is the **upturn**, not the
  censored L.
- The pre-§3 check (highlight 1 — is §5b's independent f(α)→NNS-feature
  anchor constructible-in-principle for (A) and (B)) is **unchanged and
  remains the single decision-critical pre-go question.**

## Why the held-tentative robustness annex was NOT run

It was insurance against a *marginal* L/U call. The call is not marginal
(`U_NOT_REACHED` by ≈10⁵×; L censored at the floor by 6–16×). The genuinely
live issues (L-conflation, the U-shape, λ-collapse, the reference caveat)
are **conceptual/spec-level**, not resolvable by varying c_U/n_φ/k — they
belong in Will's review surface, not in 4 h of confirmatory compute.
Running it would confirm the obvious at cost = exactly the
method-compromising over-generation the "cleared exclusively" constraint
forbids. The prepared annex stays unused in `phase35a/_tentative_review/`
(uncommitted), with this decision recorded.
