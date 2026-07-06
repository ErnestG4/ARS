# MORNING_F — genus>0 FF calibrator: certified point-counter; A2-β extension scoped

Branch `genus-ff-calibrator` off main (separate worktree `ars-F`, independent of Session G). New machinery —
certified-before-trusted. main/refsuite untouched. Direct enumeration only (SEA out of scope).

## The new machinery — curve point-counter (genus 1, 2)
`ff_curve.py`: genus-1 (y²=x³+ax+b) and genus-2 (y²=f, deg 5) point counts over 𝔽_p; Frobenius/L-polynomial →
all N_v; the two provable (Weil) gates: **Hasse–Weil** `|N_v−(q^v+1)|≤2g·q^{v/2}` and **RH-for-curves** (all
Frobenius eigenvalues |α_i|=√p).

## Certification (make-or-break) — PASS, after a battery-caught bug
- **Genus 1:** N₂ from the Frobenius recurrence == independent brute-force 𝔽_{p²} count (55=55, 195=195, 48=48).
- **Bug caught by the method-invariance battery, then fixed:** the genus-2 power-sum recurrence used the k>4
  Newton identity for k=3,4 — missing the +3e₃ / −4e₄ correction terms. The eigenvalues (e's) and RH were fine
  (RH passed), but N_v for v≥3 were wrong; Hasse–Weil, being a loose *bound*, passed the buggy values for some
  curves and **failed for others (p=11)** — which is how the battery surfaced it. Fixed with the correct
  Newton identities + a consistency assert (S[2]==s₂).
- **Re-certified:** genus-2 N₃ recurrence == brute-force 𝔽_{p³} count (344=344, 2152=2152, 324=324, 2198=2198).
- **Method-invariance:** **77 smooth (curve × base-field × genus) cases — Hasse–Weil + RH ALL PASS** (p up to 29,
  four genus-1 + four genus-2 families, singular curves filtered by a squarefree-f check). METHOD_INVARIANT on
  the provable gates.

## The β-extension — honestly scoped (this is the key epistemic call)
A2's β (≈0.76·log₁₀q) is the convergence rate of the **RF von-Mangoldt COEFFICIENTS** `a_m → μ(m)/φ(m)` computed
with **polynomial Ramanujan sums c_m(f) over 𝔽_q[T]** (genus 0). Extending *that exact β* to genus>0 requires
**Ramanujan sums over the CURVE's function field** (ray-class-group arithmetic) — which this spec does **not**
restate (it restates the point-counter gates only) and is a substantial build. **Per verify-then-build, that
extension is BANKED, not forced.** What I established genus>0 instead:
- **The point-count / zeta convergence** `N_n/q^n → 1` decays at the **RH rate 0.5·log₁₀q**, with the exponent
  **genus-independent** (genus enters only the 2g prefactor): measured rate/(0.5·log₁₀q) = **0.975 (g=1), 0.958
  (g=2)**. This is a *different* convergence object from A2's RF-coefficient β — so it **neither confirms nor
  refutes** the 0.760-vs-0.7675 / ⅓ question.
- **The ⅓ candidate (β=(⅓)ln q ⇒ 0.7675·log₁₀q) stays a genus-0 A2 question.** Genus>0 point-counts do not bear
  on it; discriminating 0.760 from 0.7675 needs a sharper genus-0 𝔽_q[T] refit (more base fields / D-range),
  banked as a genus-0 follow-up. ⅓ status: **neither supported nor refuted here** (not the same β).

## Verdict
- **Certified genus>0 arithmetic is banked** — the conjecture-free (Weil) calibrator zoo now spans genus 1–2 with
  Hasse–Weil + RH provable gates, method-invariant across 77 curves. A real asset: provable ground-truth curves
  beyond the genus-0 𝔽_q[T] line.
- **A2's genus-0 β promotion stands** (unaffected). Its genus>0 extension is a **named, banked build** (curve
  function-field Ramanujan sums), not a failure.

## Close
Committed on branch `genus-ff-calibrator`; main/refsuite untouched. Artifacts: `ff_curve.py`, `F_results.json`.
Carry-forward: (a) curve-function-field Ramanujan-sum construction to extend A2's exact β to genus>0 (needs the
prior F spec's construction detail); (b) a genus-0 β refit to resolve 0.760 vs 0.7675 / ⅓; (c) SEA as the banked
next tier if large-q curves are ever needed.
