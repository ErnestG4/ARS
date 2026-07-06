# §5b Anchor-Constructibility — the pre-§3-analytic GATE (2026-05-17)

**Status:** THEORY / gate analysis (Step 2's prerequisite, Will 2026-05-17).
No instrument, no compute, parallel to everything. Lit-lock discipline:
claims are *constructible-in-principle, cited not independently verified* —
the specific relations are to be verified at derivation-execution. This
gate decides **which §3-analytic branches may proceed**; it is not the
derivation.

## The question (precisely)

§3 derives a generative law for the AM IDS-unfolded NNS — branch **(A)
Fibonacci-Cantor**, branch **(B) AC-fine-structure**. §5b must validate a
derived law **non-circularly**: the derived NNS must match a feature
predicted from spectral/multifractal data by a relation **independent of
the NNS-derivation itself**. Absent that, §5b is self-consistency — a
wrong-but-self-consistent derivation passes (the §D.0b surface). Gate: for
each branch, is such an independent anchor *constructible in principle*?
A branch with no constructible anchor is unfalsifiable and must not be
stamped (descriptive-only at most).

## Branch (A) — Fibonacci-Cantor: anchor CONSTRUCTIBLE + rational-θ-validatable (strong)

- DGY give **rigorous exact** control of the Fibonacci substrate: spectrum
  dimension and the DOS multifractal spectrum f(α) / generalized
  dimensions D_q, via trace-map hyperbolicity on the Fricke–Vogt surface
  (coupling-dependent exact exponents).
- The IDS-unfolded NNS of a multifractal Cantor spectrum has small-s
  behaviour and low moments governed by the **local scaling exponents of
  the DOS** — the standard thermodynamic-formalism multifractal-measure →
  spacing-statistics map. So an independent feature — the small-spacing
  exponent β of P(s)~s^β, and low moments ⟨s^q⟩ — is derivable **from
  DGY's f(α)** by a route that does *not* pass through the direct NNS
  derivation (f(α) comes from the trace-map hyperbolic-set thermodynamic
  formalism — a different computation). Non-circular by construction.
- **Anchor-relation self-check available:** the rational-θ approximant
  (θ=p/q) is exactly solvable — IDS plateaus exactly at k/q, band
  structure exact, q-band-periodic NNS elementary. The f(α)→feature
  relation can be **validated on the exact rational case before** trusting
  it at irrational θ. (A)'s anchor is not just constructible but
  *anchor-validatable*.
- **BAR constraint (standing, load-bearing — §7.ter.48):** DGY is
  *Fibonacci-specific*; AM/Harper is a *different* operator (analytic
  cocycle vs Sturmian). The (A) anchor must use the operator's *own*
  exponents — Fibonacci-DGY for the Fibonacci substrate; for the **AM**
  substrate, AM-critical multifractal exponents (Avila one-frequency
  cocycle / critical-Harper multifractal — exist, *cited not verified*,
  not DGY-rigorous). **No silent Fibonacci→AM transfer**; folklore "both
  critical QP" is below the BAR. §3-(A) must state which operator's
  exponents its anchor actually uses and scope the claim accordingly.

**Verdict (A): PROCEED.** Anchor constructible & rational-θ-validatable;
the f(α)→feature relation is a *required, rational-θ-cross-checked
deliverable*; operator-scope (Fibonacci vs AM) explicit per the BAR.

## Branch (B) — AC-fine-structure (subcritical AM): anchor CONSTRUCTIBLE-IN-PRINCIPLE but falsification-sharpness AT RISK

- Regime: spectrum Cantor-as-a-set (Ten Martini) but spectral *measure*
  absolutely continuous, states extended; the validated leg (G5b) shows
  the IDS-unfolded NNS is **near-clock** (W1δ≈0.004 at λ=0.1) — extreme
  rigidity. Control machinery is **not** DGY-multifractal; it is Avila
  one-frequency analytic cocycle / **quantitative almost-reducibility**:
  zero Lyapunov exponent on the spectrum, IDS highly regular with
  quantitative Hölder bounds set by the Diophantine class of θ and by λ.
- Independent anchor in principle: the **leading deviation from exact
  clock** (the small W1δ / first correction to picket-fence) is controlled
  by the **IDS modulus-of-continuity / Hölder exponent** and the θ
  Diophantine constant — quantities characterizable from almost-
  reducibility, *independent* of the NNS derivation. So an anchor exists
  in principle: derived clock-deviation scale == almost-reducibility-
  predicted IDS-regularity correction.
- **Sharpness risk (load-bearing).** The AC-regime NNS is *near-degenerate*
  (clock + tiny correction; W1δ≈0.004). The feature to anchor is a subtle
  leading-order deviation, not an O(1) shape. The validated leg's own W1δ
  resolution floor (its L_iter-convergence tolerance, ~few×10⁻³ in the
  G3 study) sits **at the same scale as the signal**. Risk: the
  independent prediction and the derived NNS "agree" merely because both
  are ≈clock within the instrument's noise — a degenerate self-confirming
  agreement that is *not* a real cross-check (a subtler §D.0b trap).

**Verdict (B): PROCEED ONLY WITH a first-deliverable sharpness
assessment** — quantify the almost-reducibility-predicted deviation scale
vs the validated leg's resolution floor *before* any (B) derivation is
trusted. If the predicted feature is below instrument noise, (B) is
**§5b-non-falsifiable ⇒ descriptive-only, not stamped** (honest non-stamp,
§D.0b discipline). The sharpness assessment is (B)'s gate-within-the-gate.

## Gate outcome

Neither branch is blocked. (A): proceed — anchor strong, rational-θ-
validatable, BAR-scoped. (B): proceed only after the sharpness assessment;
descriptive-only if the feature sits under instrument noise. This is the
§5b gate Will named; §3-analytic may now proceed on (A) cleanly and on
(B) sharpness-assessment-first. The derivation itself ("genuine hard
mathematics that may not resolve") is the ongoing work, not this gate.

## §3-analytic — well-posed setup (what the derivation must produce)

- **(A)** Derive P_A(s) (IDS-unfolded Cantor NNS) and, *independently*,
  β_A and ⟨s^q⟩_A from the operator's own f(α); cross-check the f(α)→
  feature relation on rational θ=p/q (exact); state operator scope
  (Fibonacci vs AM) per the BAR; §5b = derived-vs-anchor match at the
  §7.ter.59 floor.
- **(B)** First: the sharpness assessment (predicted deviation scale vs
  leg floor). If sharp enough: derive the clock-deviation law from
  almost-reducibility + Diophantine class; §5b = deviation-scale match.
  If not: declare descriptive-only.
- Both: brief-and-hold on *stamping*; the derivation is theory and may
  return `DERIVATION_INTRACTABLE` (honest, valid). No instrument needed —
  fully parallel to Step 1.
