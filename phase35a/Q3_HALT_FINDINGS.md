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

---

## Will's adjudication (2026-05-17) — folded into brief rev 7

- **Finding 1 accepted; the rev-6 forward-analysis's quantitative reasoning
  (monotone-triple) was reference-artifactual** (coarse 24000-ref property),
  not substrate. Qualitative `U_NOT_REACHED` survived; reasoning did not.
- **Finding 2 (λ-collapse) → QUARANTINED, candidate phantom.** It inherits
  Finding-1's reference-artifact suspicion (a striking quantitative pattern
  in the same reference-sensitive §Q3 W1δ). Must clear three checks before
  §3 is ever asked to explain it: (a) own-vs-common reference — **✓ own**
  (code-inspection: ref built inside the per-λ loop); (c) >1 cell-N —
  **artifact-consistent** (existing §Q3 log: inter-λ rel-spread shrinks
  monotonically F_22 ~2.7% → F_26 ~0.014% as cell-N→ref-N, i.e. the
  collapse is a large-cell-N-near-ref-N effect, not a substrate constant);
  (b) does it survive a reference-resolution change — **the decisive
  mandated test, RUNNING** (`q3_finding2_refcheck.py`). "λ-collapse is a
  concrete thing the §3 analytic half must explain" is **struck** from the
  pre-§3 framing until (b) clears. Building a model to explain an artifact
  would be §D.0b on the critical path.
- **"Diverging / no stable law" CORRECTED.** W1δ=E|s−1| is bounded (≲0.75)
  and monotone on the up-slope ⇒ a bounded monotone sequence converges: a
  limiting law **exists in principle**. §Q3 shows the *empirical W1δ-vs-N
  route* exhausted within F_26 (convergence too slow to be finite-N-
  reachable), **not** divergence and **not** "no law." This *preserves*
  §3's premise; `STABLE_LIMITING_LAW_NOT_ESTABLISHED` must be read as
  "empirical route exhausted," never "no law." (Caveat, Will's: rests on
  up-slope monotonicity; the top end may share Finding-2's contamination —
  the clean mid-range up-slope independently carries both "a limit exists"
  and `U_NOT_REACHED`, so the headline is robust regardless.)
- **Arc-claim downgraded to its robust core:** "the empirical W1δ-vs-N
  route to small-λ AM's limiting law is exhausted within F_26." "λ-
  independently" (un-cleared Finding 2) and "diverging" (imprecise) struck.
- **Finding 3 affirmed; L REDEFINED** to the U-curve upturn, located by the
  ΔW1δ sign-change beyond ±c_U·U-floor (argmin carries estimation noise) —
  not a raw argmin, not the floor-crossing.
- **§3-go (Will's, alone):** analytic-half-go *supported, sharper* — a law
  exists in principle, the empirical route is confirmed dead ⇒ analysis is
  the **sole surviving route**. The unchanged decision-critical pre-§3 gate
  is §5b's independent f(α)→NNS-feature anchor constructibility for **both**
  (A) and (B) — the real §D.0b-falsifiability question; **not** the
  quarantined λ-collapse.

**Finding-2 (b) disposition: PENDING** — `q3_finding2_refcheck.py` running
(`REFERENCE_ARTIFACT_CONFIRMED` ⇒ struck permanently; `SURVIVED_ESCALATE`
⇒ escalate to Will, not auto-promoted to substrate). To be appended here +
in brief rev 7 on completion. SCOPING; no §3 adjudication; brief-and-hold.

---

## (b) reference-resolution check — RESULT (decisive, and it CASCADES)

`q3_finding2_refcheck.py` → **`REFERENCE_ARTIFACT_CONFIRMED`** (both cell-Ns,
overall). Evidence (`q3_finding2_refcheck_results.json`):

- **W1δ ≈ f(cell-N / ref-N), substrate-λ sub-dominant.** Ratio 0.236 →
  W1δ≈0.0853 at (cell 17711, ref 75025) AND ≈0.0852 at (cell 46368, ref
  196418) — identical across unrelated absolute sizes. At fixed cell-N,
  varying ref-N swings W1δ by 0.07–0.21 vs an inter-λ spread ~1–3e-4
  (reference moves it 200–4000× more than λ).
- **Finding 2 = CONFIRMED REFERENCE-ARTIFACT PHANTOM** — struck
  **permanently** (not merely quarantined). §3 must **not** be tasked to
  explain the λ-collapse: there is nothing to explain; the 4-dp collapse is
  the cell-N/ref-N ratio carrying no λ.

**CASCADE (honest, load-bearing — the check invalidates more than its
target).** §Q3 held the reference FIXED at 196418 and swept cell-N, so the
**entire §Q3 W1δ-vs-N curve = f(cell-N/196418)**: F_24→ratio0.236→0.085
(≡ §Q3 log 0.0852); F_26→ratio0.618→0.292 (≡ §Q3 log 0.2918). Therefore the
**U-shape and the `U_NOT_REACHED` headline are properties of the harness
ratio-function f, NOT the AM substrate.** §Q3 **does not stand as a
substrate measurement.** Will's pre-stated caveat (top-end contamination ⇒
"still growing at F_26" suspect) is realised, and stronger than "partly":
*dominant across the whole curve*.

**Corrected state (NOT a §3 adjudication — input only):**
- The empirical W1δ-vs-N route is **UNMEASURED (harness-dominated
  instrument), NOT "exhausted within F_26."** The rev-7 framing "analysis
  is the sole surviving route because the empirical route is confirmed
  dead" is **WITHDRAWN**. The analytic half remains the irreducible §3
  content, but its justification is no longer "empirical route dead."
- A residual ~0.25–2.2% inter-λ λ-dependence **is** present and grows as
  ref≫cell (small ratio) — the genuine substrate signal exists but was
  *swamped* by f in §Q3's configuration. So the state is "AM substrate
  structure **unmeasured here**," **not** "AM has no structure."
- A non-ratio-dominated instrument (reference scaled with cell to hold the
  ratio→0; or an analytic/gap-labelling IDS) is required to speak to
  substrate convergence. That redesign is **§3-grade / a Will-adjudicated
  spec decision** — NOT pursued autonomously here.

`STABLE_LIMITING_LAW_NOT_ESTABLISHED` / `U_NOT_REACHED` as **substrate**
verdicts are **retracted**; they were harness-artifact readings. The only
surviving §Q3-era substrate fact is the small residual λ-dependence
(direction-correct, magnitude tiny, uncharacterised). brief-and-hold; no
§3 adjudication; "demonstrated zoo gap" (the *certified-instrument*
result, independent of §Q3) still stands.

---

## Post-(b) catches — cascade followed further (Will, 2026-05-17)

Two "survivors" from the prior report were over-claimed; corrected:

1. **L→upturn FALLS.** The U-curve is f(cell-N/ref-N) — harness, not
   substrate; its minimum is a harness feature. Redefining L to it just
   relocates L between artifacts. Only Finding-3's *principle* survives
   (floor-crossing L was an artifact). **L is now UNDEFINED / SUSPENDED**
   pending a non-ratio-dominated instrument. The rev-7 "L = U-curve upturn"
   fix is **withdrawn**.
2. **Zoo gap: "probably robust, pending its own reference-check," NOT
   "stands, independent."** The artifact is a property of fixed-reference
   W1δ-unfolding; the certified grid used exactly that. **Inspection
   (regated_instrument.py):** clock calibrator → `unfold_arcsine`
   (ratio-free); Poisson → raw point process (ratio-free); AM cells →
   `unfold_ids_ref` at cell-N/ref-N ratio (ratio-dependent). The
   BR_artifact verdict thus compares a ratio-contaminated AM unfolding
   against ratio-free calibrators — *not* ratio-clean as it stands.
   **Rescue (ratio-immune substrate fact):** at fixed cell-N=2584 / same
   reference (⇒ identical ratio ∀λ), subcritical W1δ≈0.04 vs supercritical
   ≈0.26 — a 6× contrast a ratio-function cannot produce at fixed ratio.
   Real sub≠super substrate difference exists; only the BR_artifact
   *label*'s ratio-cleanliness is unverified (needs calibrators
   re-unfolded at AM-matched ratios + verdict surviving a ref-N variation).

**Critical-path elevation:** the non-ratio-dominated empirical-instrument
redesign is now a **prerequisite** to BOTH zoo-gap re-validation AND §3's
empirical half / HALT / (A)/(B). The whole arc's empirical leg is
non-functional until rebuilt. Will-adjudicated, §3-grade; not autonomous.

**§3-go input undisturbed** (affirmed): analytic-half-go supportable on the
corrected justification (law plausibly exists; analytic half irreducible
regardless; gate = §5b f(α)→NNS anchor for (A)&(B)); catch 2 does not
reach it. brief-and-hold; no §3 adjudication.

---

## Sign-off + two forward items (Will, 2026-05-17) — cascade RESOLVED, no further revision

Catch-2 **converted from "pending" to settled-factual**: the BR_artifact
verdict is **not ratio-clean** (code-confirmed: clock=`unfold_arcsine`
ratio-free, Poisson=raw ratio-free, AM=`unfold_ids_ref` ratio-dependent) —
established, not asserted. A real **sub≠super substrate difference is
established** (ratio-immune: 6× at fixed cell-N=2584/same ref). The only
open item: whether the *gap label* holds under a ratio-clean instrument.

Forward items (additive; NOT flaws in the diagnosis):
1. **Zoo-gap re-validation spec (when written) must also characterise the
   Wigner calibrator's unfolding** (inspection covered clock+Poisson only).
   The not-ratio-clean conclusion holds without it; completeness item.
2. **§9-iv sharpened to its complete form:** the cascade reaches *every
   claim sharing the contaminated mechanism* (fixed-reference unfolding) —
   not only the run that surfaced the artifact (L→upturn fell: U-curve IS
   the harness fn; zoo-label fell: certified grid used the same unfold).

**Track independence (hold for the two decisions):** §3-analytic go is
**independent of the redesign** (deriving (A)/(B) needs no instrument);
the two tracks parallelize; only §3's empirical half waits on the
redesign. The redesign is genuine §3-grade design (scale-ref-with-cell
*mitigates*; gap-labelling IDS *removes* — that's the brief's weigh).

State: cascade correctly & completely resolved; empirical leg honestly
non-functional pending redesign; surviving substrate facts precisely
stated; §3-analytic path clear & gap-independent. **Two clean forward
decisions remain (Will's), not another revision.** brief-and-hold; §3
untouched; Class II blocked.
