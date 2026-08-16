# COMMUTATOR TABLE — Holonomy Pilot

**Date:** 2026-08-16. **Brief:** `HOLONOMY_PILOT_BRIEF.md` (approved, A1–A3 + R1–R5 folded, af7a94f).
**Seal:** `holonomy/prereg_sealed.json` (a583d9f; 16 files blob-SHA frozen; debug window closed
with the seal, D1 clause verbatim). **Protocol arc — no new science claims.** Verdicts via
`lattice_h.resolve_pair` / `resolve_arc.py` only; canonical orders live as code in
`holonomy/canonical.py` (the owner; §12 prose cites it).

## TL;DR — verdict board

| Pair | Primary verdict | Measurement layer | One-line |
|---|---|---|---|
| **P1** unfold↔window (1D) | **ORDER_RULING_REQUIRED** | NONCOMMUTING_UNPREDICTED | census found BOTH orders live (C1/C2); law confirmed 14/15 cells, the one violation at the registered omitted-term cell; **ruled: window-then-unfold (RULED_CORRECT)** |
| **P2** reweight↔edge (2D) | **COMMUTATOR_MEASURED** | COMMUTATOR_MEASURED | sealed continuum law confirmed across the full gradient ladder (max fam-z 2.16 / 3.58); ruling pre-positioned for future λ̂-estimating callers |
| **P3** weight↔thin (survey) | **POINT_CHECK_CLEAN** | POINT_CHECK_CLEAN | mechanism real (−10,003 counts/draw, sealed sign −1 hit 32/32; 12σ suppressor-free), estimator suppression holds (max fam-z 2.49 / 3.21, powered, MDD 0.0018 ≤ 0.01) |
| **OP1** surrogate↔unfold (1D, exploratory) | **ORDER_RULING_REQUIRED → resolved (seal ADD-1/ADD-3)** | NONCOMMUTING_UNPREDICTED | ΔΣ²(20) = +1.15 ± 0.23 (z 4.9) — real; worst-case materiality NOT clean at the RIGID_GUE gate → correctness leg run → **ruled MATCHED_LENS, RULED_CONSISTENT-with-leg-run** (original blanket order retracted) |
| **OP2** disattenuate↔pool | COMMUTATOR_MEASURED | — | sealed Jensen-gap formula confirmed: +0.02484 ± 0.00042 vs +0.02457 (z 0.64) |

*Lattice-vocabulary declaration (seal ADD-2):* the measurement-layer value NONCOMMUTING_UNPREDICTED
is an implementation-time completion of the brief's §3 lattice, authored pre-seal (dc2448c,
frozen blob 52a1e575 in a583d9f, 11 seconds before the seal, measurement after) — same class as
the survey's CLASS_INCONSISTENT_ACROSS_TILES. The survey seal declared its completion; this one
did not — a declaration defect caught by Will's post-banking audit and repaired by dated addendum.

§7a promotion trigger: **did not fire** (P3 clean) — the survey synthetic analogue stays parked.
Optional-pair trigger: fired (mandatory wall-clock 270 s < 3600 s sealed) — both optional pairs run
by rule, not appetite.

## P1 — unfold → window vs window → unfold

**Census (the first trigger):** both orders live in the repo via the renormalisation half of the
unfold — `run_zeta_height_convergence.py:85` windows then unfolds per chunk; `universality.py:118`
(`compute_nns`) renormalises whatever set it is handed (C1, a hidden per-set unfold inside a
statistic). The pointwise RvM/semicircle map commutes with windowing exactly; the per-set
estimation/normalisation does not.

**Law vs sealed continuum prediction** (trended GUE, a=0.25, deg 5, 24 seeds; Δ = Σ²(A) − Σ²(B),
A = unfold-then-window):

| dial (W/ℓ) | L=10 | L=20 | L=40 |
|---|---|---|---|
| 0.25 | −0.003 vs 0.000 (z −0.3) | +0.003 vs 0.000 (z +0.2) | +0.045 vs 0.000 (z +2.0) |
| 0.5 | +0.008 vs +0.007 (z +0.1) | +0.038 vs +0.028 (z +0.6) | +0.152 vs +0.111 (z +1.3) |
| 1.0 | +1.175 vs +1.183 (z −0.9) | +4.773 vs +4.765 (z +0.2) | **+19.188 vs +19.216 (z −0.2)** |
| 2.0 | **+0.211 vs −0.013 (z +7.8)** | +4.380 vs +4.197 (z +1.8) | +27.312 vs +27.183 (z +0.5) |
| 4.0 | +0.304 vs +0.310 (z −0.5) | +1.193 vs +1.216 (z −0.5) | +3.681 vs +3.729 (z −0.2) |

14/15 cells within the family-wise threshold (z_fam 3.75), including sub-percent agreement on the
largest effects (the dial-1.0 resonance and dial-2.0 top). The single violation is the small-|pred|
sign-flip cell — **exactly the signature the seal registered in advance for the known-omitted
fluctuation-absorption term** (`p1_prediction_scope`), with the predicted positive sign (B's
truncated fit absorbs real fluctuations). By rulings-as-code the lattice still reads
NONCOMMUTING_UNPREDICTED — no post-hoc exception cells; the attribution lives here as
interpretation, and "add the absorption term to the continuum derivation" is the registered
prediction upgrade for any future 1D-order arc.

**Correctness leg (the ruling basis):** window-then-unfold is decisively less biased where the
orders separate — bias 0.091 ± 0.013 vs 4.848 ± 0.034 at dial 1.0 / L20 (and 25.5 vs 52.9 at
dial 2.0 / L40). **Ruling: `window_then_unfold`, RULED_CORRECT** (transfer to fixed substrates
recorded). ⟨r̃⟩ control: never fired (max fam-z 1.97) — the instrument stayed clean.

**Affected banked results, re-run (three-event label):** (1) banked zeta height-convergence NNS
rows, pre-arc; (2) census C2 + this ruling triggered re-examination; (3) re-derived under BOTH
orders on `zeros_2000.npy`: identical class calls (gue/gue), ΔKS ≈ 5×10⁻¹⁴ — no banked verdict
moves. Materiality clean by the sealed rule. Closure note: compute_nns's hidden renormalisation
(C1) — flagged by the census as a defect-shaped finding — turns out to be the thing that has been
*silently enforcing the low-bias order* for NNS consumers; the enforcement **mechanism** is
unconditional in code (the renorm runs on every input), but the both-orders-equivalence **datum**
is zeta-window-only (seal ADD-4) — other substrates inherit the mechanism, not the measurement.
Σ² consumers have no such self-enforcement, which is where the ruling has teeth. Zeta leg ΔΣ² ∈ {−0.015, −0.017,
+0.014}, within its jitter envelope (envelope_ok).

## P2 — intensity-reweight → edge-correct vs edge-correct → reweight

Mechanism: the λ̂ **estimation domain** (full vs eroded); sealed strip-fit estimator, exp-gradient
ladder to 4.30×. Sealed continuum law **confirmed**: max fam-z 2.16 (vs 3.58); measured Δ
monotone in the ladder, sign negative (reweight-first more biased), e.g. G=4.30, r=1:
ΔK = −0.1016 ± 0.0086 vs predicted −0.0973. Correctness leg two-sided witness passed at KAG
(separated construction ruled correctly at 5.6σ; symmetric construction indistinguishable).
**Materiality: STRUCTURAL_CLEAN by census C3** — no live caller estimates λ̂ from data (bridge
designed instances used known intensity), so no banked row is downstream of the mechanism.
Ruling pre-positioned in `canonical.py` for future callers: `edge_then_reweight` (fit on the
domain the statistic integrates over), RULED_CORRECT with transfer noted.

## P3 — weight-application → randoms-thinning vs thinning → weighting

The A1 upgrade (dial-less ≠ seed-less) did the work: 32 pre-drawn u-draws, both orderings per
draw. **Mechanism (R1), named and measured:** scalar keep-rate normalisation — weighted
(p=0.038599) vs count (p=0.039335) totals, w̄_kag 1.0245 vs w̄_data 1.0053 → nested keep-sets,
predicted count difference −9,991; **measured −10,003 ± 137, sealed sign −1 hit on all 32 draws
(A3).** Suppressor-free, the mechanism is a 12σ retained-mass effect (KAG red-A). **Suppressor
(R1), also named and measured:** the ratio/self-normalising F path holds it below detection —
mean ΔF = +0.00021 ± 0.00008 (L=0.1°, z 2.49) and −0.00051 ± 0.00057 (L=0.5°, z −0.90), family-wise
clean (z_fam 3.21), powered (achieved MDD 0.0018 vs sealed 0.01), materiality clean (worst bound
0.0022 in F vs minimum survey margin 3.16σ ≈ 0.15 in F). **POINT_CHECK_CLEAN — the narrower
claim, as sealed: no detectable order effect at the sealed points and power; no law, no off-point
claim. The clean row is OWNED by the estimator family** (canonical.py carries the ownership
clause); witness for the unmodified path: injected spatial δ=0.05 detected at 14σ (KAG red-B).

## Optional pairs (ran by sealed trigger)

**OP1 surrogate↔unfold — the audit-driven arc within the arc (seal ADD-1/ADD-3):**
ΔΣ²(20) = +1.15 ± 0.23 (z 4.9) — surrogates passing the unfold lens inherit the fit's variance
absorption; real non-commutation, exploratory lane (no sealed prediction by design). The pair
was first banked RULED_CONSISTENT on a bare order with **no materiality pass — a §2 obligation,
omitted; Will's audit caught it.** The owed pass (op1_materiality.py, run through the consumer's
own module) came back **NOT clean**: the nearest downstream consumer is the RIGID_GUE gate
(`cross_substrate/longrange_discriminator.py`), renewal-arm min 2.71 vs boundary 1.056 → margin
1.65 = **1.4× |Δ| against k=3**. The call-site search simultaneously found that every live site
runs surrogate-then-SHARED-lens *deliberately* (the module's own "# same lens"; the
instrument-matched-null doctrine) — so the originally ruled order would have **broken** the
principled design it claimed to govern; it is retracted. The §3-forced correctness cell
(op1_correctness.py, prediction committed before running): direction as predicted in both runs —
matched-lens marginal-class data reads its own null (z −0.04) while the mixed order biases it
rigid-ward (z −0.32) — but separation 0.28 ± 0.20 does not reach k=3 (8-seed first run banked
in-file; one pre-committed 64-seed rerun). Per §3, biases-don't-separate → **ruled
MATCHED_LENS** (surrogate and data pass the identical unfolding apparatus; no bare sequence
order enforced), basis RULED_CONSISTENT **with the leg run and the site-specific effect
quantified** (~0.3σ of the classification band — 4× smaller than the bare-pair Δ measured on the
trended substrate; the worst-case screen and the site measurement are both banked and do not
conflict). Site-hardening watch item ADD-5: the discriminator's absolute renewal-to-RIGID margin
is thin in its own units independent of order effects; registered to the cross-substrate program.
**OP2 disattenuate↔pool:** sealed Jensen-gap formula confirmed (z 0.64); ruled
`disattenuate_then_pool`, RULED_CORRECT (truth by construction).

## Gate record (all green before measurement; kag_measured.json, frozen in the seal)

Commutation nulls non-vacuous, worst rel-Δ 1.5×10⁻¹⁶ vs 10⁻¹² tolerance (fp tolerance scoped to
the exact-commutation regime only, A2). Both dialed red demos fire (P1's first construction was
INERT — rank-windowing is invariant under monotone maps — replaced and labeled inside the KAG
window). Correctness-leg witness two-sided PASS. P3: `thin_pre` equivalence vs frozen
`thin_to_data` bit-identical (tested transfer surface, R2); red-A (suppressor-broken) labeled
DETECTION-IN-PRINCIPLE; red-B fired at the unmodified path. Census: 53/53 classified, coverage
1.000 ≥ 0.9 floor, committed denominator (R3).

## Scope

Pairwise order-sensitivity only (brief §7): no full-sequence holonomy claim. C4
(window↔project, census-found) registered, unsealed, unmeasured. Survey synthetic analogue
parked (trigger 7a did not fire). Prediction upgrade for P1 (absorption term) registered.

## Reproduction

`holonomy/` order: `ownership_map.py` → `predict_p1.py` + `predict_p2.py` → `kag_holonomy.py` →
`seal_prereg.py` → `run_p1.py` + `run_p2.py` + `run_p3.py` → `run_opt.py` → `resolve_arc.py` →
`verify_holonomy.py` (live checker, nonzero exit).
