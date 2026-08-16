# RESULTS — RIGID_GUE Gate Characterization

**Date:** 2026-08-16. **Brief:** `RIGIDGATE_BRIEF.md`. **Seal:** `rigidgate/prereg_sealed.json`
(5 files frozen; addenda RG-ADD-1..5). Discharges `cross_substrate/PROGRESS_REPORT.md`
REGISTERED-OPEN (holonomy ADD-5). **Instrument arc — no new science claims; nothing under
`cross_substrate/` written; no banked row re-verdicted.**

## TL;DR — the answer to the question as posed

**The boundary is calibrated, not fitted, and its ingredients check out analytically.** It is
`gue_mean + 2.5·gue_ensemble_sd`; the 2.5 is a chosen tolerance (commit 78e0ee1), but the bands
themselves land where theory says: measured GUE band vs the Mehta asymptotic agrees to **0.2% at
n=2000/L=40**, 6.9% at n=1200/L=20, 10.6% at n=343/L=6.86, and the renewal decoy matches its
Var(s)·L asymptote to 1.2–7.9% — all inside the sealed 20%.

**The margin is a property of the configuration, not of the decoy family.** Against the family the
gate was calibrated on, at n≥1200 the separation is 3.6–3.8σ with a false-RIGID rate of **0.000**.
At the small-n configuration that the banked approximability rows actually use (n=343, L=6.86) it
is **1.5σ with a false-RIGID rate of 0.035**.

**There is a real hole, and it is not about margins at all.** The rule is one-sided by deliberate
design ("more rigid than GUE is still GUE-class"), so it is unbounded below: a **perfect clock
earns RIGID_GUE at z = −5.09**, and a jittered clock at z = −4.22. The clock is a banked zoo
calibrator. As deployed, `RIGID_GUE` means *"not floppier than GUE"* — not *"consistent with
GUE."*

**Fix: split the cell, don't move the boundary.** `|z| ≤ 2.5 → RIGID_GUE`, `z < −2.5 →
HYPER_RIGID`. Same formula, same multiplier, no new constant, no new statistic. It rejects every
hyper-rigid spoof, costs **zero** specificity (real-GUE false-HYPER rate 0.00 at all three
configs), and **moves neither banked row** (brocot z=+0.49; ζ z=−2.36).

## Findings

**F1 — Provenance.** Boundary = GUE reference-ensemble mean + 2.5 × ensemble **spread** (not a
standard error). One-sided since 78e0ee1 (2026-06-04), deliberately. A second conjunct requiring
separation from the *renewal* band existed until c8695ef, where switching the second reference
from renewal to Poisson dropped it; at every configuration measured here that conjunct would have
been **redundant** (renewal sits above the GUE-side boundary), so its loss is a documentation
defect, not an operational one.

**F2 — Margin, corrected in both directions (RG-ADD-2).** ADD-5's "≈1.1σ" was a small-sample
artifact of mine: 8 draws, an over-estimated sd (1.5 vs the 200-draw 0.72), and a min compared to
a boundary rather than a band. Properly measured at that configuration the margin is 3.6σ,
false-RIGID 0.000. **But the concern is re-vindicated where it matters more:** at n=343 the rate
is 3.5%. Thinness is configuration-dependent and concentrated at small n — which is exactly what
the ADD-5 trigger's per-verdict margin re-derivation is designed to catch.

| config | renewal band | boundary | margin | P(false RIGID) |
|---|---|---|---|---|
| C-brocot (n=343, L=6.86) | 1.34 ± 0.26 | 0.945 | **1.5σ** | **0.035** |
| C-add5 (n=1200, L=20) | 3.61 ± 0.72 | 0.994 | 3.6σ | 0.000 |
| C-zeta (n=2000, L=40) | 6.89 ± 1.54 | 1.071 | 3.8σ | 0.000 |

**F3 — The hole, demonstrated on a banked calibrator.** clock → `RIGID_GUE` (z=−5.09);
jittered clock → `RIGID_GUE` (z=−4.22); marginal-exact antithetic constructions at f ≤ 0.02 →
`RIGID_GUE`. Under the proposed split all three read `HYPER_RIGID`.

**F4 — A fundamental limit, stated as scope (RG-ADD-4).** The adversarial family is a *permutation*
of an iid Wigner spacing draw, so its NNS marginal is exact by multiset identity (KAG cell D:
18/18 bit-identical). Tuned to f\* ≈ 0.056 it sits **inside** the GUE band (z=+0.67) while keeping
GUE NNS. No rule built on Σ² at a single L can exclude it — it matches on both measured
quantities. The gate's claim is bounded to non-adversarial substrates. This is the module's own
founding lesson one level up: NNS certifies the marginal, not the class; **Σ²(one L) certifies
rigidity at that scale, not the class.**

**F5 — Materiality on banked rows (reported, NOT applied).** brocot/golden: z=+0.49, no move.
ζ_first_2000 (RvM-unfolded, L=40): Σ²=0.385, **z=−2.36**, no move — but only 0.14σ inside the
proposed lower edge, and the lens sweep reaches −2.48 at deg 3. **The ζ row would move to
HYPER_RIGID under a 2.0 multiplier or a slightly different lens.** Adopting the split therefore
requires the owning program to decide what it wants that row to say; this arc does not decide it.

**F6 — Two fixes measured and rejected, with reasons.** (a) A Σ² *growth* arm failed its own
two-sided KAG witness — at a 2× L lever the GUE log-increment (~0.07) sits under single-realization
noise (~0.13): it passed real GUE 42% and passed a flat process 75%. Underpowered by
construction. (b) A Δ₃ growth arm is well powered (increment 0.1053 ± 0.0086, ~12:1) and rejects
every spoof — **but it rejects ζ at z=−9.5**, because ζ_first_2000's variance is nearly flat in L
(0.30→0.39 across L=2→40 against GUE's 0.40→0.74). That flatness is **real, not instrumental**:
the deg-6 lens absorbs **0.0%** at n=2000 (0.6810 vs 0.6811 on GUE) and the deviation is
lens-invariant across deg 3/6/10/15. At T≈2.5×10³ the Berry saturation scale is ln(T/2π)=**5.99**,
so GUE-like growth is not expected above L≈6 — while the gate's matched-L default puts ζ at
**L=40**, far outside that window. A growth arm cannot separate "genuinely more rigid than
finite-N GUE" from "not GUE at all", because at the level of Σ²(L) those are the same measurement
outcome. That is why the honest repair names the outcome instead of tuning a statistic to sort it.

## Verdict, and a lattice hole of this arc's own (RG-ADD-1)

The sealed lattice offered GATE_SOUND / GATE_BOUNDED (both requiring the R2 target met at every
config) and GATE_DEFECTIVE (defined by a banked verdict being *wrong*). What occurred — target met
at two configs, missed at one, with **no banked verdict shown wrong** — has no cell. `run_gate.py`'s
else-branch printed `GATE_DEFECTIVE`, which the sealed prose does not authorise. The raw JSON keeps
that output so the hole stays visible; the substantive verdict is

> **GATE_CONFIG_DEPENDENT + BOUNDED** — sound against its calibrated decoy family at n ≥ 1200,
> thin at n = 343 (3.5% false-RIGID), with a demonstrated hole outside that family (hyper-rigid
> processes earn the GUE pole) and a fundamental single-L limit against adversarial constructions.

Also corrected against myself: **RG-ADD-3**, the R5 battery tested the adversarial family at f\*,
the boundary-crossing member, where any band rule passes by construction — so that flag carried no
information; **RG-ADD-5**, marginal-exactness is an identity pre-cumsum and agrees to 3×10⁻⁴ after
the round-trip (floating-point non-associativity), so the run's `identical=False` is about the
round-trip, not the construction.

## Recommendations to the owning program (proposed, not applied)

1. **Adopt the HYPER_RIGID split** (`proposed_rule.rigid_cell`) — minimal, zero specificity cost,
   moves no banked row today. Decide deliberately what ζ_first_2000 should read, given F5.
2. **Report the per-verdict false-RIGID rate** at the verdict's own (n, L, lens), as the ADD-5
   trigger proposed; the n=343 row is where it earns its keep.
3. **Scope the class claim to the L window where GUE growth is expected** — for ζ at height T that
   is L ≲ ln(T/2π); the matched-L default currently exceeds it by ~7×.
4. **Record the scope bound from F4** in the module docstring: single-L Σ² is not adversary-proof.

## Reproduction

`rigidgate/`: `gate_probe.py` → `kag_gate.py` → `seal_prereg.py` → `run_gate.py` →
`patch_addenda.py` → `verify_rigidgate.py` (live checker, nonzero exit).
