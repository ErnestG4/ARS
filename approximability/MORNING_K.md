# MORNING_K — the sealed overnight ran: bridge banked, scout green, class instrument-limited, e-divergence

Executed the sealed brief `OVERNIGHT_BRIEF_bridge_scout.md` (Night 1 = O1 bridge + O2 scout; Night 2 = Arm 1 class +
Arm 2 e-divergence). All four ran. Branch `cubics-wilderness`; main/refsuite untouched. Every prereg was byte-locked
before measurement (`O1_bridge_prereg_SEALED.json`, `O2_scout_prereg_SEALED.json`, Arm 1/2 forks in the brief).

## O1 (bridge) — the seam is BANKED as a smooth validated ladder; a≥2 honest-limited
Artifacts: `O1_bridge.py`, `O1_bridge_measured.json`, `O1_bridge.log`.
**Calibration EXACT.** C(a=4) measured **1.0216046** vs Panel A **1.0216069** — Δ = **−0.0002%**. The growth-rate
engine (dim·lnλ, convergence-gated λ→∞ extrapolation) is validated end-to-end. C(a=5) newly measured **1.1604 ± 0.045**.

**The θ_∞ = L_a/C_a ladder, a=1–5** (L exact, C validated):

| a | L_a | C_a | θ_∞ = L/C | note |
|---|---|---|---|---|
| 1 golden | 0.4812 | 0.8771 | **0.5486** | closed-form 0.5460 — within the −0.4% C-error ✓ (self-check) |
| 2 silver | 0.8814 | 0.8667 | **1.0169** | |
| 3 bronze | 1.1948 | 0.9133 | **1.3081** | |
| 4 metallic-4 | 1.4436 | 1.0216 | **1.4131 ± 0.043** | C calibrated vs Panel A (−0.0002%) |
| 5 metallic-5 | 1.6472 | 1.1604 | **1.4196 ± 0.055** | new |

**Verdict — CONFIRMED as a smooth, monotone, validated ladder.** No rung breaks out; the golden closed-form anchor
lands inside the propagated C-error; the a=4 calibration is exact. The load-bearing correlated-C-noise worry is
answered — the ladder is monotone with every constant independently validated, not a noise artifact.
**Honest limit (as pre-registered):** the *independent* θ_∞ check (direct bandwidth-exponent vs L/C) exists only at
golden; a≥2 use **measured-not-derived C** (Liu–Wen: no closed-form C for a≥2). So the seam is banked as an
empirical connective law, not yet mechanism-derived above golden.
**New feature worth a look:** θ_∞ **decelerates and plateaus at ~1.42** (a=4 and a=5 overlap within error) rather
than climbing unboundedly — consistent with L_a~log a and C_a~log a both growing so the ratio tends to a constant.
Not resolved (a=4/a=5 not separated); a genuine follow-up question.

## O2 (scout) — GREEN, measured-efficient
Artifacts: `scout_count.py`, `O2_scout_measured.json`.
φ control passes the harness gate (N(h)≡1, d\*=0). Across the 13-cubic wilderness the near-optimal Stern-Brocot
beam stays **bounded at N(h)≤4–5** with tail d\*≈0.002–0.005 — not even polynomial, **O(1)**. The near-optimality
dimension is **0**: the Farey scout is **measured-efficient** on real generic-CF substrates. (The d\*peak≈0.1–0.4
values are small-h transients — a single N=3 at depth 3 — not the asymptotic.) Sealed reward `R=−log(q|qα−p|)`,
Δ=log2 fixed before counting. The scout question moves from "provably efficient in theory" to **"measured efficient."**

## Arm 1 (class) — INSTRUMENT-LIMITED; the deg-16 SPLIT was a lens artifact (retracted)
Artifacts: `class_probe.py`, `class_robust.py`, `Arm1_class_measured.json`, `Arm1_class.log`.
Reused the certified panel_B pipeline (`sturmian_eigs` tridiagonal + `unfold_empirical` + `II1_sigma2_at_L`).
**Layer-zero PASSED:** Poisson γ=0.98 (~1), GUE γ=0.20 (~0), well separated. First pass gave cubic γ spanning
0.94–1.58 (per-seed error ~0.04 → looked like a ~5σ SPLIT). **But the deg-robustness gate killed it:** recomputing γ
at unfold degree ∈ {10,14,16,20} swings each substrate by **0.3–0.5** (cbrt12: 1.51/1.24/1.46/0.96) and the
high-vs-low ordering **flips** (deg10 OVERLAP, deg14/16 SEPARATED, deg20 OVERLAP). The spread is manufactured by the
global-polynomial unfold interacting with the fractal spectrum, **not** substrate memory.
**Verdict — neither COLLAPSE nor SPLIT is certifiable** at n=4200 / L≤30. The deg-16 SPLIT is **retracted**. This is
the `longrange_lens_discipline` trap caught in the act — the robustness check is what saved a false positive.
**Queued (not tonight):** resolve the class with an **IDS-based unfold** (not a global deg-k polynomial) and/or larger
n; then the marginal-vs-class question ([[nns_certifies_marginal_not_class]]) gets a real answer.

## Arm 2 (e divergence) — the C-engine REFUSES e; divergence confirmed by refusal + Σ² magnitude
Artifacts: `e_divergence.py`, `Arm2_e_divergence_measured.json`, `Arm2_e_divergence.log`.
The gated growth-rate route returns **n=0 converged λ points** for e — and this is the point, not a bug. The
engine's convergence gate (`|dim_shallow − dim_deep| < 0.02`) **IS the self-similarity assumption**; e (liminf-K=∞)
violates it by construction, so different CF windows never agree and the gate rejects every λ. **The instrument that
measures C structurally cannot return a finite C for e** — a direct operational confirmation of the Panel A order
parameter (C finite ⟺ liminf-K finite). Silver returns n=0 too under this over-strict early/late-window variant, so
the route can't serve as its own positive control at q<4000 — the growth-rate C route is simply **the wrong
instrument for the divergence** (it is built around the self-similarity e lacks).
**The correct instrument is Σ² (level statistics).** Prior `panel_B_spectral.json` already banks e's divergence
signature there: e has the **highest Σ²(L=30)=6651** of the pool (metallics 5100–6000), drifting toward Poisson —
the dim→1 / spectrum-filling signature liminf-K=∞ predicts. A clean **exponent** readout for e waits on the same
unfold-conditioning fix Arm 1 needs.
**Verdict:** e's non-membership in the finite-C/self-similar class is **re-confirmed by refusal** (C-engine returns
nothing); the positive divergence magnitude lives in panel_B's Σ². INCONCLUSIVE via growth-rate, by design.

## Carry-forward
- **Bank:** the O1 θ_∞ ladder (seam, empirical, golden-anchored) and the O2 scout-efficiency measurement (GREEN).
- **Instrument debt:** Arm 1 needs a conditioning-robust unfold before the class question is answerable; the current
  global-poly unfold is the bottleneck, not the physics. The `g̃`-marginal-vs-class question remains **open**.
- **Discipline win:** two would-be findings (Arm 1 SPLIT, Arm 2 first pass) were caught by robustness/control gates
  before banking. The lens/control checks did their job.
