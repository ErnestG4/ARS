# Comb k-Tuple Constellations — Arc Brief (DRAFT, needs review + go)

**Status:** DRAFTED 2026-08-18. Not run. The registered follow-up from the comb arc
(`comb/RESULTS_COMB.md`), which measured **pairs** and explicitly left constellations open.
**Posture:** calibrator arc, conjecture-backed-computable tier. **No claims about primes** — the
object is whether the *comb calibrator* reproduces a *computed* prediction, exactly as in the pair
arc; the number theory is input, not output.
**One-line frame:** the pair arc showed Gaussian-prime comb weights match the computed ℤ[i]
Hardy–Littlewood singular series for differences. The obvious next question — do k-tuples match too
— is only worth asking if it can distinguish the k-tuple prediction from the naive product of
pairwise ones, because otherwise a "match" is arithmetic bookkeeping rather than a test.

---

## 0. The discriminator, stated first because it decides whether the arc is worth running

For a constellation (h₁, …, h_{k−1}) the ℤ[i] singular series is **not** the product of the
pairwise singular series of its differences. The k-tuple 𝔖 involves a local density at each prime
that counts residues *jointly* — the joint count is what makes 𝔖 a k-body object rather than a
product of 2-body ones.

**So the arc's real question is not "do k-tuple weights match 𝔖?" but "is the difference between
𝔖(k-tuple) and ∏𝔖(pairs) large enough to measure at the banked annulus, and does the comb follow
the former?"** If the two predictions agree to within the achievable error, a match confirms
nothing the pair arc did not already establish, and the arc should not run.

## 1. Cells

- **K0 — countability and the discriminator gap (the kill criterion; runs FIRST).** For each
  candidate constellation shape at the banked annulus (R₁,R₂ = 3000, 3600 from
  `bridge/gaussian_prime_annulus.py`): how many instances exist, what is the resulting counting
  error, and **how far apart are 𝔖(k-tuple) and ∏𝔖(pairs) in units of that error?**
  **ABORT if the gap is below the sealed resolvability threshold** — with the honest note that
  "the annulus is too small to tell the two predictions apart" is itself a bankable result and the
  cheapest possible outcome.
- **K1 — compute 𝔖 for the sealed shapes.** Extend `comb/singular_series.py` from the pair form to
  the k-tuple form, with the same discipline that arc used: an **executable hand-table gate** (a
  small set of constellations whose local densities are computed by hand and asserted in code —
  the gate that caught the even-residual factorization bug in the pair arc).
- **K2 — measure comb weights for the sealed shapes**, through the existing banked machinery.
- **K3 — adjudicate against BOTH predictions**, reporting the measured weights against 𝔖(k-tuple)
  and against ∏𝔖(pairs) side by side. The verdict is which one the comb follows, not whether it
  matches "the" prediction.
- **K4 — per-realization and boundary-rate hygiene.** Every rate banked as k/n; any rate at 0 or 1
  reported with its Clopper–Pearson interval (`boundary_rate.py`); the arc's headline pinned in
  `comb/verify_comb.py` with a demonstrated red path. *(These are now definition-of-done, not
  optional — see TOOLKIT §9.)*

## 2. Sealed before anything runs

Constellation shapes and the annulus; the resolvability threshold for K0; the hand-table entries
for K1; the adjudication rule for K3 (including what "follows neither" looks like); the error model
for the comb weights. **Prediction-first:** 𝔖 values are computed and committed before the comb
weights are measured, as in the pair arc.

## 3. Verdict lattice

- **KTUPLE_MATCHES_SINGULAR_SERIES** — weights follow 𝔖(k-tuple), and 𝔖(k-tuple) is separated from
  ∏𝔖(pairs) by the sealed margin. *The only outcome that adds something the pair arc did not.*
- **PRODUCT_INDISTINGUISHABLE** — the two predictions are not separable at this annulus; banked as a
  scope statement about the calibrator's reach, not a null result about arithmetic.
- **FOLLOWS_PRODUCT** — weights track ∏𝔖(pairs) and not 𝔖(k-tuple). Would be the interesting
  failure: it would say the comb encodes 2-body structure only, which bounds what the calibrator can
  certify.
- **UNDERPOWERED** — counts too low at the sealed shapes; one declared annulus enlargement, fires
  once.

## 4. Carried-through protocol

Executable hand-table gate (K1); committed generators throughout; seal with blob-SHA freeze;
witness-must-fail with **analytic non-inertness argued first**; rates as k/n; headline pinned in the
checker with a red path; and a **coverage argument for the constellation sample** — which shapes the
sealed set spans and which it provably does not — built from what the pair arc already knows about
which local densities dominate, not from a fresh study.

## 5. Open questions for review

1. **Which k?** k=3 only, or k=3 and k=4? My recommendation is k=3 alone for the first arc: the
   counts fall steeply with k and K0 will likely kill k=4 at this annulus anyway, so including it
   mostly buys a predictable abort.
2. **Is `FOLLOWS_PRODUCT` actually reachable**, or is it excluded by construction given how the comb
   weights are built? Worth settling before sealing — a verdict cell that cannot occur is exactly the
   inert-arm defect this repo keeps finding.
3. **Does the sole-anchor rule bite?** `gp_comb` is seated as a conjecture-backed-computable
   calibrator; if a k-tuple result would be used to anchor anything, `assert_sole_anchor_allowed()`
   must be consulted first.
