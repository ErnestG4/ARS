# Comb Calibrator Micro-Arc — Gaussian-Prime Constellation Weights vs Computed Singular Series

**Status:** APPROVED WITH AMENDMENTS (Will, 2026-08-14) — ready for its own session.
**Review record:** Will independently verified the §2 derivation against the general HL shape
(C = ∏(1−ν(p)/p)/(1−1/p)^r), hand-recomputed C′_G through the prime inventory (0.879 after
the primes above 5 → 0.842 through q≈50 → ≈0.838–0.84 tail), and verified the N=50/18/26
factorizations including (7+i)/(1+i) = −i(2+i)² — the discriminator genuinely tests the
multiplicity rule. Amendments in this revision: §4.5 seal items (code freeze,
prediction-first registration, numeric extension rule, power seal), §5 verdict lattice
restructured to the 2×2 (pooled level-test × orthogonal drift test), N=32 added to the
pure-(1+i) ladder, L1 resolved to the Gross–Smith + KRR anchor stack, §8 registry ruling.
**Lineage:** Bridge arc B2/B3 (`bridge/RESULTS_BRIDGE.md`, registered follow-up #1, priority
decided 2026-08-14); Phase 34d (Gaussian primes, sieve machinery); calibrator-zoo discipline
(precision-audits-the-calibrator-zoo; clustered-calibrator-class precedent).
**Epistemic tier (header-grade, binding):** **CONJECTURE-BACKED-COMPUTABLE.** The
Hardy–Littlewood constellation weights for ℤ[i] are unproven; the singular-series constants
are computable to arbitrary precision. This is a *distinct tier* from the theorem-backed zoo
entries (ζ window / Farey / Ginibre / Poisson), and every artifact this arc banks carries the
tier in its header. Seating the tier vocabulary in the zoo schema is itself a deliverable.
**Honest one-line frame:** B2 measured four comb weights it never sought; this arc asks
whether number theory predicts them, with the prediction pipeline built to calibrator-zoo
grade and the verdict gated on *fresh* data, because the banked B2 numbers have already been
glimpsed against a back-of-envelope prediction (disclosure in §0.5 — this shapes the whole
design).

---

## 0. Frame

Bridge B2 found the pcf of split Gaussian primes in a wedge to be a lattice comb: support
exactly at checkerboard-ℤ[i] offsets, weights g(√2)=3.07, g(2)=2.01, g(2√2)=1.48,
g(√10)=3.66 (bins 0.25; `bridge/bridge_b_measured.json`). The B3 filing scoped this as an
observable-binding capability, no class claim. The registered follow-up: if the weights match
the computable HL singular series for ℤ[i] constellations, the comb becomes the zoo's first
2D arithmetic calibrator — a point process whose two-point structure is *predicted by number
theory* rather than sampled from a model.

## 0.5 Brief-time disclosure (binding on the design)

During brief drafting, CC derived the site-level prediction (§2) and ran it against the four
banked B2 weights as a feasibility check. The result cannot be un-seen and is disclosed
rather than laundered:

- The three (1+i)-only shells (√2, 2, 2√2) back out a **shell-independent** 𝔖̂′ ≈ 0.83–0.84
  after geometric normalization (4 offsets/shell ÷ bin annulus area ÷ site density) — three
  different g values collapsing to one constant is already a nontrivial structure check.
- The √10 shell backs out 𝔖̂′ ≈ 1.12 ≈ 0.84 × 4/3 — exactly the predicted (q−1)/(q−2)
  correction for offsets divisible by a prime of norm 5.
- A partial product for the ℤ[i] twin constant C′_G (primes to q ≲ 50) gives ≈ 0.84.

**Consequence 1:** the B2 window is hereby demoted to *disclosed pilot glimpse*. All gates in
this arc run on **fresh, disjoint data** (new wedge, pre-registered before any fresh-data
compute) — the out-of-sample-window discipline applied at arc scale.
**Consequence 2:** the arc's value is not the binary "does it match" (the glimpse says it
plausibly does) but the *precision instrument*: exact-offset counting, per-shell error model,
C′_G to certified precision with tail bounds, discriminating shells the glimpse never touched,
and finite-size drift measurement. If the match survives all of that at few-percent precision,
the calibrator is seated; if it breaks anywhere, that break is the finding.

**Standing on the glimpse (review ruling):** do not undersell it. Three unrelated g-values
collapsing to one constant that independently matches the computed C′_G, plus the 4/3 factor
appearing on cue at √10, is a **four-point structural agreement with a zero-parameter
prediction**. The fresh arc is not checking whether something is there; it is measuring how
precisely, testing shells the glimpse never saw, and earning pre-registered ground for the
seating. `RESULTS_COMB.md`'s TL;DR frames the glimpse as the pilot it was, not as a
contamination to be apologized for — disclosed pilots are how honest instruments get built.

## 1. Structural-null audit (front-loaded)

**Generative-substrate family:** support-restricted — the configuration lives on the
checkerboard sublattice {a+bi : a+b odd} = odd-norm points of ℤ[i], with radial intensity
λ(r) = 2/(π ln r) (Landau, validated to 0.04% in B2).
**Natural null:** **independent site occupation on the checkerboard at matched λ(r)** —
Poisson-on-the-support, the same null family as Mertens-on-squarefrees (34a). Under this
null every comb POSITION is reproduced (positions are the support talking — B2's filing) and
every site-level weight is exactly **𝔖′ ≡ 1**. The measurement object of this arc is
therefore the per-offset-class ratio 𝔖̂′(h) = (observed pairs at exact offset h) / (expected
under the support null), and the science content is entirely in 𝔖̂′ ≠ 1.
**What the wrong null would do:** rate-matched *continuum* Poisson manufactures the comb
itself as "clustering" (every peak infinitely anomalous vs a continuous null). The Bridge
already filed this; no continuum-null comparisons appear anywhere in this arc.

## 2. Prediction (theory side, computed not fitted)

For offset h in the difference lattice (1+i)ℤ[i], the conjectural site-level weight is

  𝔖′(h) = C′_G · ∏_{π odd, π | h} (q−1)/(q−2),  q = N(π),

  C′_G = ∏_{π odd} (1 − 2/q)/(1 − 1/q)²   (product over odd primes of ℤ[i]:
         split p≡1 mod 4 contribute two factors at q=p; inert p≡3 contribute one at q=p²;
         the ramified (1+i) factor is absorbed by the checkerboard support normalization).

Divisibility (π | h) is yes/no — multiplicity does not enter (the local condition excludes
residues, not valuations). Derivation from local residue counting mirrors the classical HL
2C₂ ∏(p−1)/(p−2). **L1 RESOLVED at review (anchor stack fixed):** **Gross–Smith** owns the
Hardy–Littlewood generalization to algebraic number fields (the conjecture's owner);
**Kuperberg–Rodgers–Roditty-Gershon (Ramanujan J., 2022)** is the modern treatment of exactly
this singular series — and G2's tail-bound work leans on KRR's estimates rather than deriving
from scratch. Execution-time L1 work: fetch both, confirm whether Gross–Smith states the
ℤ[i] pair case explicitly or only the general-K form (determines citation form), and verify
§2's re-derivation against the published shape. **The blocking clause stands:** any
discrepancy between the re-derivation and the literature form halts measurement until
reconciled (L1_DISCREPANCY), reconciliation filed either way.

**Per-shell predictions** (offsets enumerated exactly; examples the arc must cover):

| shell N(h) | offsets | odd-prime divisors | predicted 𝔖′ |
|---|---|---|---|
| 2, 4, 8, 16, **32** | 4 each | none | C′_G |
| 10, 20, 40 | 8 each | one prime above 5 | (4/3)·C′_G |
| 18 | ±3±3i (4) | inert 3 (q=9) | (8/7)·C′_G |
| 26 | 8 | one prime above 13 | (12/11)·C′_G |
| **50** | **±5±5i (4): both primes above 5 → (4/3)²·C′_G; ±7±i, ±1±7i (8): (2+i)² ∥ h → one factor 4/3·C′_G** | | **two classes, same |h|** |

(N=32 added at review: extends the shell-independence check of C′_G — the single most
load-bearing structural claim — essentially for free.)

Shell N=50 is the designed discriminator: two offset classes at the *same Euclidean
distance* with predicted weights differing by 4/3. Distance-binned pcf cannot see this;
exact-offset counting must. It is also a direct test of the multiplicity rule ((2+i)²∥7+i
counts once).

## 3. Goals

1. **G1 (instrument):** exact-offset pair counting on integer coordinates (no distance bins),
   with per-offset-class expected counts under the §1 support null and a Poisson error model;
   committed generator for every banked number (TOOLKIT §9 committed-generator rule, named
   from this lineage's own audit).
2. **G2 (theory):** C′_G to certified precision (target: relative error < 10⁻³ with an
   explicit tail bound on the truncated product) + per-class 𝔖′ predictions for all assessed
   shells; literature anchoring (L1).
3. **G3 (measurement, fresh data):** 𝔖̂′ per offset class on the pre-registered fresh window,
   two norm bands for finite-size drift (validate-scale-convergence discipline).
4. **G4 (seating):** if gates pass, register the comb as a zoo calibrator with the
   conjecture-backed-computable tier in the zoo header schema; tier field applied to existing
   entries in the same stroke (knowledge-does-not-propagate).

## 4. Methodology / pipeline

**Carried through:** `phase34d/gaussian_primes.py` sieve + Cornacchia;
`bridge/gaussian_prime_annulus.py` window construction pattern; B2's intensity model +
variation budget discipline; TOOLKIT §11.1 window rules (exact-offset counting is
border-corrected trivially: eroded cores by max assessed |h|).

**New work:**
- `comb/exact_offsets.py` — offset-class enumeration (shells to N ≤ 50 minimum; class =
  orbit under units × conjugation × divisor pattern), exact pair counts, null expectations,
  𝔖̂′ with errors.
- `comb/singular_series.py` — C′_G + per-class predictions, truncation tail bound stated in
  the output artifact; committed generator of the banked constants.
- **Fresh window (pre-registered in the seal before fresh compute; B2 window excluded):**
  proposal — same annulus norms, disjoint angular wedge θ ∈ [0.45, 0.65] (still inside the
  first octant, away from both B2's wedge and the axes), plus a second norm band at ~4× the
  norm for drift. Final numbers fixed at seal time.
- **Error model:** per-class Poisson counting error (B2-scale power estimate: ~8k unordered
  pairs in the √2 class alone → ~1% on 𝔖̂′ for rich shells); finite-size drift assessed
  across the two norm bands per the §5 lattice.

### 4.5 Seal contents (review-mandated; all residual analyst freedom eaten here)

The theory side has zero free parameters — nothing on the prediction side can be tuned
toward the glimpse — so the seal must close the *measurement* side completely:

1. **Code freeze.** The commit hashes of `comb/exact_offsets.py` and
   `comb/singular_series.py` are referenced in the seal **before the fresh wedge is
   sieved**. No analysis-code change after fresh data exists; a post-freeze defect fix
   requires a dated seal addendum (pilot-informed-seal pattern) and re-derivation of every
   affected number.
2. **Prediction-first registration.** The full predicted table — C′_G at its certified
   precision with the KRR-anchored tail bound, and every mandatory shell's 𝔖′ — is written
   into the seal itself. Prediction filed before measurement, classical style.
3. **Numeric extension rule.** The exact enlargement geometry (the specific wider θ-range
   and/or added norm span) is stated in the seal as numbers, and the rule fires **once**.
   No promissory "per pre-registered extension rule."
4. **Power seal.** Before any fresh compute, verify from λ(r) and the sealed window geometry
   that every mandatory shell delivers the σ its k·σ criterion assumes (the fresh wedge at
   0.2 rad is plausibly narrower-counted than B2's). A shell that fails the power check gets
   the window adjusted **at seal time** — the extension rule is not burned on a foreseeable
   defect.

## 5. Acceptance criteria — the 2×2 lattice (review-restructured)

**k = 3 (sealed).** Two orthogonal tests per class, so every outcome has exactly one address
and single-band excursions cannot fall between named cells (with ~10 shells × 2 bands ≈ 20
tests at 3σ, a true match would produce a lone one-band excursion with ~5% probability — that
outcome must have a home *before* the data exists):

- **Level test (primary):** the **pooled** estimate — inverse-variance combination of 𝔖̂′
  across the two norm bands — vs 𝔖′_pred, at k·σ_pooled. Single-band excursions are
  absorbed into the pooled statistic where they belong.
- **Drift test (orthogonal):** band disagreement (𝔖̂′_high − 𝔖̂′_low) vs its own counting
  error, tested separately — disentangled from the level test, which also gives the drift
  test its full power.

| | no drift | coherent drift beyond counting error |
|---|---|---|
| **pooled match (all classes)** | **PASS (WEIGHTS_MATCH_SINGULAR_SERIES)** → G4 seating | **SOFT PASS (MATCH_WITH_BOUNDED_DRIFT)** → seated **BOUNDED-AT-SCALE** |
| **pooled deviation (any class)** | **FAIL (substantive) (DEVIATION_BEYOND_ERRORS)** | **DEVIATION_BEYOND_ERRORS** (drift does not rescue a level failure) |

- PASS additionally requires the N=50 discriminator to resolve its two classes in the
  predicted order with the 4/3 separation.
- **MATCH_WITH_BOUNDED_DRIFT (canonical per review):** the filed drift law carries **sign and
  fitted coefficient**, not just "1/log-type"; the calibrator's registry entry states its
  **validated norm range** so no future consumer can quote it outside the scale where it was
  seated.
- **DEVIATION_BEYOND_ERRORS:** the deviation is the finding (a measured departure from the
  ℤ[i] HL prediction at computable offsets is worth more than the calibrator); no seating;
  exact class and magnitude filed.
- **UNDERPOWERED (clean FAIL):** counts too thin for the sealed k·σ at a mandatory shell
  *despite* the §4.5 power seal → fire the numeric extension rule once; if still thin, file
  UNDERPOWERED, no seating.
- **Blocking (L1_DISCREPANCY):** literature form disagrees with §2's re-derivation → halt
  measurement until reconciled; reconciliation filed either way.

## 6. Out of scope

- No universality-class claims; no promotion of B2/B3's scale-qualified filing.
- No proof-tier language anywhere: the tier is conjecture-backed-computable and every
  artifact says so.
- No k-tuple generalizations beyond pairs (triple constellations are a future arc if the
  pair calibrator seats).
- No continuum-Poisson comparisons (§1).
- The B2 window is not re-measured (it is the disclosed glimpse; its numbers stand as-is).

## 7. Methodological commitments carried through

Calibrator-zoo-first (the zoo's own precedent: a new class must PASS its known-answer
construction before use); committed-generator rule (TOOLKIT §9) on every banked constant and
count; pilot-informed-seal pedigree addendum if any pilot shapes the seal; support-set null
only; out-of-sample gate after the §0.5 disclosure; verdict words used exactly as §5 names
them.

## 8. Deliverables

1. `comb/` package: `exact_offsets.py`, `singular_series.py`, seal, measured JSONs — every
   banked number with its committed generator.
2. `comb/RESULTS_COMB.md` — TL;DR verdicts up top per §5 vocabulary; per-shell table
   (predicted / measured / σ / verdict); drift section; L1 anchoring section.
3. Zoo registration entry (PASS/SOFT PASS only) with tier field; tier vocabulary added to
   the zoo header schema and applied to existing entries. **Registry ruling (review):** the
   tier field lands wherever a gate *reads labels at runtime*, not where humans browse — if
   `calibrator_panel.py` is what verdict code consumes, the schema lives there and
   `calibration_anchors.py` cross-references; if the anchors file is consumed, invert.
   Mechanical test: the tier must be *capable of blocking something* (e.g., a future rule
   that conjecture-backed calibrators cannot be sole gate anchors for a theorem-tier claim).
   A tier field no gate can see is documentation cosplaying as schema. SOFT PASS entries
   additionally carry the validated norm range (§5).
4. Cross-references: `bridge/RESULTS_BRIDGE.md` follow-up #1 closed with pointer;
   `EPISTEMIC_STATE.md` same-stroke update; memory update.

## 9. Open questions for CC from the repo (resolve at execution)

1. Which file does verdict code actually consume for calibrator labels
   (`calibrator_panel.py` vs `cross_substrate/calibration_anchors.py` vs
   `mathtest/refsuite`) — determined by reading the gate call sites, then the §8 registry
   ruling applies. (L1 anchor question: RESOLVED at review — Gross–Smith + KRR stack, §2;
   only the explicit-vs-general-K citation form remains for execution.)
2. Whether the fresh wedge at θ ∈ [0.45, 0.65] has any axis-adjacent contamination concern
   at the sealed norm bands (expected no — same octant-interior logic as B2), and whether
   the §4.5 power seal forces a wider wedge or a longer norm span for the thin shells
   (N=32, N=50 classes are the likely binding constraints).
