# Substrate-Aware L Policy — Arc Brief (DRAFT, READY FOR A GO)

**Status:** DRAFTED 2026-08-16 following the ruling that this is **the highest-value item on the
queue, above the full-sequence holonomy arc**. Not run.
**Lineage:** the RIGID_GUE characterization arc (`rigidgate/`, seal + RG-ADD-1..8) produced three
findings that review collapsed into one defect: a **fixed L policy colliding with
substrate-specific physics**. This arc fixes the defect the three findings share.
**Posture:** instrument arc. **No new science claims.** The owning program adopts or amends; this
arc proposes, validates, and quantifies — it does not install, and it does not re-verdict.
**One-line frame:** the gate judges every substrate's rigidity at an L chosen by the *gate*, not by
the *substrate* — so it asks ζ a question about a scale where ζ's own physics says the answer is
"saturated," and then reads the answer as a class call.

---

## 0. The defect, in one paragraph

`longrange_audit.py:36` uses `AUDIT_L = 50.0` for every arithmetic substrate. For the Riemann zeros
at height T ≈ 2.5×10³ the Berry saturation scale is **ln(T/2π) = 5.99**: above it, Σ²(L) saturates
and GUE-like logarithmic growth is *not expected*, as a matter of known physics rather than
instrument failure. The banked ζ row was therefore judged **8.3× past its own validity window**.
Three consequences, all measured in the RIGID_GUE arc: (i) the row sits below the GUE band
(z = −2.33) where a one-sided rule cannot distinguish "more rigid than GUE" from "not GUE at all";
(ii) the Δ₃ growth arm — well powered at ~12:1 and correct on every spoof — was filed as *rejected*
because it flagged that row; (iii) the prose read the resulting label as class confirmation.

## 1. Cells

- **L0 — Validity-scale map (the arc's core deliverable).** For each substrate family in the audit,
  derive and bank its GUE-validity scale with a committed generator and a literature anchor:
  ζ / L-functions → Berry saturation ln(T/2π) (Berry 1988); finite spectra (GUE/GOE calibrators,
  operator spectra) → the n-limited scale; renewal-like and neural substrates → their own bound or
  an explicit "no validity window derived" entry, which is a legitimate and informative row.
  Deliverable `validity_scales.json`. **A substrate with no derivable window is banked as such** —
  the map's honesty depends on it having empty cells.
- **L1 — Re-judge at capped L (reported, not applied).** Every banked long-range row re-evaluated at
  min(current L, its validity cap), under (a) the deployed one-sided rule, (b) the proposed
  HYPER_RIGID split, (c) the split + the Δ₃ growth arm. Output: a table of what each row *would*
  read. **Registered in advance:** ζ inside its window is the row most likely to move, and the
  arc's value does not depend on which way it moves.
- **L2 — Δ₃ arm deployability inside the window.** The arm's ζ failure is the hypothesis under test:
  if the failure was an L-policy artifact, then at L ≲ ln(T/2π) the arm should keep ζ *and* reject
  every spoof. Both arms measured; the arm is promoted only if both hold (sensitivity/specificity
  discipline — improving one at the other's cost is a defect, not a fix).
- **L3 — Power at capped L.** Capping L costs statistical power (fewer independent windows, smaller
  separation). Measure the cost: band widths, false-RIGID rate, and the minimum detectable class
  separation at the capped L for each substrate. **A cap that fixes the physics and destroys the
  power is not a fix** — this cell can kill the arc's recommendation and is why it exists.
- **L4 — Recommendation.** A concrete L policy for the owning program: per-substrate caps, the
  Δ₃ conjunct if L2 supports it, and the power cost stated per row.

## 2. Gates before measurement

Two-sided, per §9. The validity-scale map must be checked against a substrate where the answer is
independently known (a finite GUE calibrator, whose n-limited scale is derivable) — the map must
reproduce it. The Δ₃ arm re-test must be able to fail: a constructed process that is genuinely
GUE-like inside the window must pass, and a hyper-rigid one must be rejected, before ζ is scored.
**Non-inertness argued analytically first, including against the estimator's own suppressors** —
the C4 near-miss is the standing reminder that naming the mechanism is not enough.

## 3. Verdict lattice

- **L_POLICY_FIXED** — capped L keeps power (L3) and the Δ₃ arm deploys cleanly (L2); a concrete
  policy is recommended.
- **L_POLICY_TRADEOFF** — the cap fixes the physics but costs decisive power; the recommendation
  becomes a documented trade with numbers on both sides, not a change.
- **NO_VALIDITY_SCALE** — a substrate family admits no derivable window; its rows are scoped rather
  than re-judged.
- **UNDERPOWERED** — cannot resolve L2/L3 at the sealed sampling; one declared doubling, fires once.

## 4. Tripwires

1. Nothing under `cross_substrate/` is written; propose-only, as in the RIGID_GUE arc.
2. No banked row is re-verdicted — L1 reports what a policy *would* do, labeled.
3. Validity scales are **derived with a literature anchor**, never fitted to make a row come out a
   particular way; each entry names its source. A scale chosen to keep ζ is the defect this arc
   exists to remove, reintroduced.
4. The Δ₃ promotion requires **both** arms (L2), and the power cost (L3) is reported with it.
5. Debugging closes with the seal.

## 5. Cost

Small. The machinery exists (`rigidgate/gate_probe.py`, the discriminator's own surfaces), the
substrates are banked, and the expensive object — GUE reference ensembles — is memoized per (n, L).
**One session**, with L0 and L3 carrying the design risk rather than the compute.

## 6. Open questions for Will

1. **Scope of L0:** arithmetic substrates only (where the physics is cleanest and the banked claims
   live), or the full audit including neural rows?
2. **If L1 shows ζ moves inside its own window** — is that a result to bank and act on, or does it
   want its own adjudication round before anything is written down?
3. Does the recommendation land as a proposed patch to the owning program, or as a policy note in
   TOOLKIT §12-style prose that the next arc touching the gate must honour?
