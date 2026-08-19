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
| **C4** window↔project (survey) | **ORDER_RULING_REQUIRED** (seal ADD-6) | NONCOMMUTING_UNPREDICTED | mechanism real and predicted (q ≈ 0.79·θ², 0.6% of points at the deployed 10° tile; law confirmed at tiles 10/20/30, missed at tile 5 — a **demonstrated quadrature artifact of the prediction**); statistic-level effect suppressed (ΔF zero-consistent, max\|z\| 0.90); **ruled MATCHED** |

*Lattice-vocabulary declaration (seal ADD-2):* the measurement-layer value NONCOMMUTING_UNPREDICTED
is an implementation-time completion of the brief's §3 lattice, authored pre-seal (dc2448c,
frozen blob 52a1e575 in a583d9f, 11 seconds before the seal, measurement after) — same class as
the survey's CLASS_INCONSISTENT_ACROSS_TILES. The survey seal declared its completion; this one
did not — a declaration defect caught by the post-banking audit and repaired by dated addendum.

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
omitted; the audit caught it.** The owed pass (op1_materiality.py, run through the consumer's
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
conflict). **Separation status: UNDER_RESOLVED, not null** (registry field, audit round 2) —
the direction confirmed in both runs at ~1.4σ; this row must not be read as evidence the orders
are equivalent, and the pre-committed rerun is consumed. Site-hardening watch item ADD-5: the discriminator's absolute renewal-to-RIGID margin
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

## C4 — window → project vs project → window (seal ADD-6, measured 2026-08-16)

The census-found pair, closed. **Mechanism, predicted first:** a sky-rectangle is not a
plane-rectangle under gnomonic projection, so membership differs on the symmetric difference of
the two regions; the committed continuum derivation gives q ≈ 0.79·θ² (θ = tile half-angle),
i.e. **0.6% of points change tile membership at the deployed 10° tile**. Measured: z = +0.90 /
+0.77 / +1.39 at tiles 10/20/30. The tile-5 cell missed at z = +5.57 and the lattice returned
ORDER_RULING_REQUIRED, banked as produced — then **demonstrated** to be a quadrature artifact of
my own prediction (q_pred(t=5) converges 0.00098 → 0.00149 as NQ goes 3000 → 24000, meeting the
measured 0.00144 ± 0.00008; both tiles land on the same q/θ² ≈ 0.79 plateau). Verdict not
retro-changed; prediction upgrade registered.

**Suppressor:** ΔF(L) under matched ordering is zero-consistent at every dial (max |z| 0.90) and
on the real survey randoms (ΔF = −0.0004 at q = 0.0045). Suppression is owned by the DD/RR-style
ratio estimator **and** by `cells_F`'s `CELL_FLOOR` mask — a refactor dropping either does not
inherit this row. **No correctness leg exists by construction** (both regions are legitimate
windows; a stationary process is unbiased on either), so the ruling is **MATCHED** — cut and
project in the same order on both sides — basis RULED_CONSISTENT with `NO_TRUTH_BY_CONSTRUCTION`,
which the registry distinguishes from OP1's `UNDER_RESOLVED`.

**KAG note, recorded:** the red demo's first non-inertness argument was *wrong* — it named the
mechanism but missed that `cells_F`'s own cell floor drops exactly the cells the mechanism
creates. The KAG fired red and halted the run. The §9 non-inertness rule did its job even though
my analytic argument was incomplete; v2 runs at the dial top and fires at z = −41.7 with a
magnitude matching the derived −q to 4%.

## P1 absorption term — derived, tested, attribution REFUTED (seal ADD-7)

The seal registered a known-omitted fluctuation-absorption term and pre-registered its signature.
Derived parameter-free (the LS unfolding fit is a linear projection, so it absorbs Π_O η and
reduces the sliding variance by an exactly-computable A_O(L)), the term has the **predicted sign**
and magnitude 0.003–0.027. Three tests: in-sample it improves mean |z| 1.14 → 1.03 but does not
change the 14/15 pass count; its own falsifier (**dial-independence**) is **falsified** at L=10
(flatness χ² = 122.5/4 dof); and out-of-sample at two new dial values it is **not resolvable**
(mean |z| 0.88 amended vs 0.87 trend-only).

**So the seal's registered attribution is refuted:** the term is real but ~80× too small to
explain the violated cell's +0.224 residual — the pre-registered signature matched in *sign* by
coincidence, not by mechanism. A second contribution was measured (the continuum prediction is
ill-conditioned exactly there: an O(1%) domain-span jitter moves it across −0.001…+0.061, more
than its own base value of −0.013) and is also ~3.6× short. **The residual is now an open,
registered item** rather than an explained one.

**Independently: the sealed P1 law is now confirmed OUT-OF-SAMPLE** — 6/6 cells at two dial values
never measured (1.5, 3.0), all |z| ≤ 1.51. The original arc had no out-of-sample test; it does
now. P1's banked verdict is untouched.

## Scope

Pairwise order-sensitivity only (brief §7): no full-sequence holonomy claim — see
`FULL_SEQUENCE_BRIEF.md` (drafted, not run). Survey synthetic analogue parked (trigger 7a did not
fire). Open: the dial-2.0/L=10 residual (ADD-7); the C4 prediction's NQ-scaling upgrade (ADD-6).

## Reproduction

`holonomy/` order: `ownership_map.py` → `predict_p1.py` + `predict_p2.py` → `kag_holonomy.py` →
`seal_prereg.py` → `run_p1.py` + `run_p2.py` + `run_p3.py` → `run_opt.py` → `resolve_arc.py` →
`verify_holonomy.py` (live checker, nonzero exit).

---

## Full-sequence follow-up (2026-08-17) — this table is NOT a bound on sequences

`fullseq/RESULTS_FULLSEQ.md` measured what happens when the pairwise results here are composed into
whole-sequence reorderings, and the answer bears directly on how this table may be used.

**The scope caveat in §7 is confirmed and strengthened, not lifted.** A first-order predictor —
summing the pairwise commutators of an ordering's inversions, evaluated at mid-stack dials — is
exact for single transpositions by construction and **fails at multi-inversion orderings**. Tested
exhaustively over all 59 admissible orderings of a 5-transition 1-D pipeline, **12 have H ≤ 0 and 10
are significantly super-additive (z < −3): the pairwise sum can UNDERESTIMATE the true effect by up
to 6.9×.**

**Mechanism:** every significantly super-additive ordering places UNFOLD in the last or
second-to-last slot, and their measured Δ is pinned at a floor (≈ −3.20) independent of the sum —
a **saturating** composition, which no additive predictor can represent.

**So, concretely, for anyone reading this table:** a pairwise Δ here bounds the effect of swapping
*those two* transitions in *that* configuration. It does not bound, and must not be summed to
estimate, the effect of reordering a sequence — **in either direction.** An earlier version of the
full-sequence write-up claimed the sum was a conservative upper bound; that claim was retracted the
same night by its own pre-registered out-of-sample test, and the retraction is pinned in
`fullseq/verify_fullseq.py`.

## The dial-2.0 residual — scaling test run, and it is INCONCLUSIVE by my own design gap

The residual is **isolated**: at L=10 the measured-minus-predicted values across the dial ladder are
−0.003, +0.001, −0.008, **+0.224**, −0.006 at sems ~0.01–0.03. Four dials match the continuum law
within noise and one does not, and that one is the only cell in the grid where the prediction passes
through **zero** (−0.0128). Two readings were pre-committed with opposite signatures: a **missing
continuum term** survives growing n; a **finite-n floor** shrinks.

Measured at n_full = 1200 → 2400, geometry held dimensionless-fixed:

| | n=1200 | n=2400 | direction |
|---|---|---|---|
| residual, absolute Σ² units | 0.2242 | 0.5175 | **grew** ×2.3 |
| residual / \|predicted\| | 17.6 | 10.1 | **fell** |
| residual / sem | 7.8 | 4.8 | **fell** |

**The generator printed `MISSING_TERM`, and that verdict is not safe.** It reads the absolute-Σ²
column — but **Σ² is dimensionful and grows with L, and the design scaled L with n** (L = n_W/60), so
"absolute units" is not a neutral choice. Two other defensible normalizations point the opposite way.
**I sealed the prediction ("shrinks") without sealing the units it would be judged in**, and the
three natural choices disagree, so the test cannot settle the question it was built for. The raw JSON
keeps the script's verdict so the disagreement stays visible.

**Why a clean version is not simply a rerun.** In this construction the unfolded coordinate has unit
mean spacing by definition, so *n and the geometry cannot be varied independently* — more points
means a longer window in the same units. There is no pure density knob to turn. Settling the question
therefore needs a **different design**, not a bigger run: isolate the fit's finite-n response on a
substrate with **no trend at all** (where the continuum term is exactly zero by construction, so
anything left is the finite-n contribution measured directly), then ask whether that contribution
accounts for +0.224 at the sealed geometry.

**Status: the residual remains OPEN**, now with one candidate explanation tested and rejected
(absorption, ~80× too small), one measured but insufficient (continuum ill-conditioning, ~3.6× short),
and one attempted and inconclusive (n-scaling, normalization-dependent). Registered with the
corrected design attached.
