# MORNING_A — Session A: two candidate axes → promotion (queue #1)

Branch `rf-promo-diatonic-battery` off master 859907c. `/home/combust/fmexplorer/bin/python3`,
`PYTHONPATH=…/riemann_explorer`, `BASE_SEED=20240517`. Adversarial: keep an axis ONLY if METHOD_INVARIANT;
a collapse is the deliverable (scope or kill, killing perturbation named). Nothing tool-side modified.

**Pre-flight note.** `git push origin master` **could not run** — `codeberg.org` needs interactive credentials this
non-interactive shell can't supply. Master is untouched; all work is on the branch. The push stays pending for the
user (`!git push origin master`).

---

## Axis A1 — RF-multiplicativity R² — **PROMOTE, scoped to {strictly-coprime pairs, a₁-normalized}.**
Artifacts: `promoA1_multiplicativity.py`, `promoA1.json`, `promoA1_matchedSNR.png`.

**Layer-zero A1-Z (all pass):** (1) `c_q(n)∈ℤ` across the full q-grid (max frac part 0.0); (2) `a₁(squarefree)=0.60793
= 6/π²` (exact); (3) the estimated-a_q pipeline reproduces the **closed-form** squarefree coefficients
`(6/π²)μ(q)/∏(p²−1)` to worst 1.7e-5 (induction-on-noise guard — the estimator is trusted before it touches noisy
data).

**The decisive pre-registered gate — matched-SNR — PASSES.** The confound: `c_q` multiplicativity in q is a theorem,
so R²=1 on arithmetic could be re-deriving it and the dynamical R²≈0 could be an SNR floor (squarefree N=182k events
vs MG 680). Control: squarefree re-estimated at **matched event count (829)**, and separately `random_thin`-ed
(banked `instrument_confound`) to 662 over the full support.

| substrate | events | Kronecker R² (canonical) |
|---|---|---|
| squarefree (full) | 182k | 0.99998 |
| primes (full) | 25k | 0.99961 |
| **squarefree match-N** | **829** | **0.978** |
| squarefree thin (sparse) | 662 | 0.578 |
| Poisson | 680 | 0.030 |
| Mackey–Glass | 680 | 0.002 |

At MG's own event count the arithmetic R² stays **0.82–0.99** (median 0.978, min across 18 configs 0.818) while MG
stays ≤0.08 — robust across all 3 estimators. **The kill condition (arithmetic collapses under matched SNR) does not
trigger: the multiplicativity is genuine substrate structure, not an SNR/N artifact.**

**Method-invariance + named scope boundaries.** Canonical form (a₁-normalized) is invariant across 3 estimators
{OLS, Theil–Sen, Huber} × 3 q-supports {all, prime-power, squarefree} — 9/9 separate, matched-SNR robust. Two
perturbations collapse it, **both scope boundaries, not kills** (named per convention):
- **Relaxing coprimality LEAKS** — non-coprime pairs reach R²=0.92 (median 0.21). The claim is coprime-dominated but
  not coprime-exclusive ⇒ the axis **must enforce strictly-coprime pairs**.
- **Huber on UN-normalized coefficients breaks** (arith R²→−0.05) — a scale artifact of Huber's robust threshold on
  the wrong scale ⇒ **a₁-normalization is required** before robust estimation. (OLS/Theil–Sen absorb the scale; Huber
  does not.)

**Verdict A1: PROMOTE within scope {strict coprime, a₁-normalized}.** Survived: 9 canonical estimator×support configs
+ the decisive matched-SNR gate (the precedent-setting adversarial control). Scope boundaries banked.

---

## Axis A2 — Function-field 𝔽_q[T] RF-calibrator error-rate — **PROMOTE (scope: genus-0; genus>0 BANKED).**
Artifacts: `promoA2_ff_calibrator.py`, `promoA2.json`, `promoA2_exponent.png`.

**Layer-zero A2-Z (the hardest, PROVABLE, fires unconditionally):** the exact prime-polynomial theorem
`Σ_{deg f=n} Λ(f) = q^n` holds for q ∈ {2,3,5,7} — the genus-0 Weil fact (`N_v = q^v+1` on ℙ¹; bound trivial/exact).
Asserted before any error-rate is computed.

**SCOPE BANKED (discipline).** Grep-confirmed: the banked Thread-C machinery has **zero** curve/genus/point-counting
symbols — it is 𝔽_q[T] = the line, **genus 0 only**. The spec's genus>0 curve-family sweep and the nontrivial Weil
bound `|N_v−(q^v+1)| ≤ 2g·q^{v/2}` require a curve point-counting module that does not exist → **banked as a separate
dedicated session, not built here.** (This is the stop-and-bank the block called for.)

**Promotion on banked machinery.** The calibrator's convergence exponent β (a_m → μ(m)/φ(m) at rate ~q^{−βD}) is:
- **estimator-invariant + degree-window-invariant**: within each field, β spread CV ≤ 0.11 across {OLS, Theil–Sen,
  last-2} × {high, low degree window}. β(q=2)=0.228 (CV 0.07), β(q=3)=0.379 (CV 0.11), β(q=5)=0.534 (CV 0.11).
- **cleanly q-scaling**: β increases monotonically with q and follows **β ≈ 0.76·log₁₀(q)** across all three fields
  (ratios 0.76/0.79/0.76) — a universal empirical rate, not per-field noise.

**Verdict A2: PROMOTE** (method-invariant error-rate, scope genus-0 𝔽_q[T]). This earns the "calibration-backbone
upgrade" word: the first conjecture-free (Weil) arithmetic calibrator now has a **characterized, method-invariant
error-rate**. Two items BANKED, not claimed: (a) the genus>0 curve sweep (new machinery); (b) the identification of
the empirical 0.76 with a specific Weil rate — the exact FF error-rate theorem was **not verified from source** this
session, so the exponent is measured-and-invariant but not asserted equal to a derived constant (verify-then-claim).

---

## Session-A close
- **Both queue-#1 axes resolved:** A1 PROMOTE-with-scope, A2 PROMOTE (genus-0). The calibration backbone upgrade is now
  formally footed (A2), and RF-multiplicativity is a validated substrate classifier within its coprime/normalized scope.
- **Gate-caught bug (banked):** memoizing `factor`/`cm_holder` across `setq()` field changes returned stale
  factorizations from the previous field (div-by-zero at q=3) — caches must clear on every field change. Same
  cross-context contamination family as the rank-unfold false-negative; caught by the results erroring, not silently.
- **Carry-forward:** genus>0 curve calibrator (A2, new machinery) + exact FF error-rate theorem (A2, verify-then-claim)
  → both queue breadcrumbs for a dedicated session.
