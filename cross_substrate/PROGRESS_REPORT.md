# Cross-Substrate Landscape — Progress Report

**Date:** 2026-05-23. **Status:** working synthesis of the program to date.
Companions: `landscape.md` (map), `viewpoints.md` (axes), `findings_log.md`
(chronological detail), `coordinates/*.jsonl` (banked values). Progress log —
NOT validated results; verdicts are Will's.

---

## 1. Frame

Operator-IS-substrate: each substrate is fingerprinted on its spectral side and
placed in a shared universality-class landscape; the yield is the cross-substrate
*comparison*, not utility-extraction from any one substrate. Explorer-shaped
(charting, not hypothesis-testing).

## 2. What's populated (14 substrates, ~8,300 coordinate records)

| substrate | cells | leg(s) | notes |
|---|--:|---|---|
| AM | 11 | matched object-(a) (Phase 1 + θ-class) | eigenvalues re-extracted + permanently banked |
| pvc-11 V1 (monkey) | 1159 | q-banded + matched | full Family I/II |
| Allen NP V1 (mouse) | 719 (544 meas.) | q-banded (+ matched on 110 OSI units) | |
| Kuramoto | 6363 | q-banded | K-sweep trajectory |
| ζ/Dirichlet/EC L-zeros | 8 | q-banded + matched | bimodal (split TODO) |
| Mertens / Liouville | 3 / 4 | q-banded + matched | |
| Gaussian / Eisenstein primes | 2 / 1 | q-banded + matched | |
| Maass Γ₀(N) | 6 | q-banded + matched | |
| Pulsar (NANOGrav) | 10 | direct-leg | cross-domain bounded |
| **Mackey-Glass** | 5 | matched + Family V | τ-sweep trajectory; peak-NNS |
| **Lorenz** | 4 | matched + Family V | ρ-sweep trajectory; lobe-NNS |
| **Logistic** | 5 | matched + Family V | r-sweep (period-doubling); IEI-NNS; analytic λ |

Plus **Sturmian-word** (8 α, Lagrange-class sweep) and **Sturmian-Hamiltonian** (7 α; = Fibonacci
Hamiltonian at golden) → **16 substrates**. Families computed: I (NNS distances I.1–I.9),
II (Σ²/Δ₃/K), III (RF, where banked), **IV (spectral box-dimension — first axis, Sturmian-Ham)**,
V (dynamical λ₁/D₂ — 3 dynamical substrates), VI (extraction-meta α/β/cross-extract), VII (inter-leg
disagreement). No single axis spans all (q-banded I.5q ⊃ ARS-classified; matched W1δ ⊃ object-(a);
Family V ⊃ time-series; Family IV ⊃ operator-spectrum substrates).

**Number-theoretic thread resolved (Sturmian word vs Hamiltonian).** The Lagrange/CF-class
stratification predicted in §4 is a SPECTRAL phenomenon: the symbolic Sturmian *word* does NOT
stratify (3-distance-rigid, q=1 universal; tracks first CF quotient), but the Sturmian *Hamiltonian*
spectrum DOES — Cantor (D_box<1, q=0) for all irrational α, with D_box stratifying by class
(quadratics ≈0.63–0.65, Liouville 0.724, rational→AC band 0.805). Consistent with AM's θ-class
(also spectral). Symbolic-side path↔event-train is real; the deep number theory surfaces in the operator.

## 3. Load-bearing results

**(a) Proxy verdict — `I.5q` is an unbiased substitute for matched `I.5`.**
Regression `I.5q = a + b·I.5`: per-substrate-medians slope 0.991, pvc-11-internal
1.001, intercept ≈ 0. Conditions: n ≥ 100 and away from strong stimulus-locking.
⇒ the cheap q-banded harvest is trustable for landscape placement; expensive matched
recompute is deferrable. (Allen/Kuramoto placed on q-banded as-is.)

**(b) Matched leg recovers known universality classes** (independent validation):
ζ-zeros → GUE (Brody q=1.00, BR ρ=0.999); Mertens/Liouville → clustered (W1δ≈1.8);
Maass → Sarnak anomaly; AM sub → clock-rigid, AM sup → intermediate. The leg reads
true class, not an ARS-internal artifact.

**(c) H1 de-confounded + cross-species.** OSI↔KS-to-GUE holds on BOTH legs (q-banded
AND plain-NNS) in pvc-11 (ρ≈0.74/0.70) AND Allen mouse V1 (ρ≈0.48/0.49) — H1 is NOT a
Farey-q-banding artifact in either species. Strengthens a foundational ARS claim.

**(d) Family VII (inter-leg disagreement |I.5q − I.5|) — a discovered axis.** Not
proxy-noise: OSI-graded in pvc-11 monkey V1 (ρ=0.47, robust to rate/n/value), ABSENT
in Allen mouse V1 → differentiates state/species. The conjectured driver (F1/F0
temporal locking) was REFUTED (ρ=0.06, per-q DIFFUSE).

**(e) AM fingerprint (Phase 1 + θ-class, 11 cells).** sub (λ<1, AC) → clock-rigid;
sup (λ>1, PP) → intermediate, N-drifting clock→Poisson (the L-underconvergence
fingerprint, VI.2 β≈2.87). θ-class: **sup carries θ-structure** (Brody q golden 0.81
→ silver 0.44 → Liouville 0.28; non-Diophantine most Poisson-leaning); **sub
θ-invariant**. The apparent inversion of Phase 35's "sub θ-sensitive 3.55×" was
RESOLVED — that 3.55× is a ratio of clock-floor (~1e-4) micro-spreads; sub is
θ-invariant in magnitude (reproduced 3.556 / mean_ratio 1.0003). No inversion.

**(f) Dynamical substrates + Family V (breadth).** Mackey-Glass, Lorenz, logistic each
placed as a bifurcation-sweep *trajectory* (stable→periodic→chaotic), giving the landscape
its first dynamical axes. **V.2 D₂ (correlation dimension) is validated everywhere** (Lorenz
ρ=28→2.21 vs lit 2.06; MG chaotic→2.3–2.4; logistic chaos→1.0). **V.1 λ via tangent-space
(correct sign + magnitude):** Benettin for flows (Lorenz ρ=28→0.909 vs known 0.906; MG
τ=17→0.005; stable→negative), analytic ⟨ln|f'|⟩ for the map (logistic r=3.7→+0.356;
period-3 window r=3.83→−0.370, correctly λ<0 inside chaos). Tangent-space is the right tool
for *simulated* substrates (known equations); time-series Rosenstein is retained for future
data-only substrates. The three sit as chaos-ordered trajectories in the D₂×W1δ plane (P4).

## 4. Methodology established

Matched-instrument across compared legs (carry every viewpoint, annotate
comparison-validity, don't discard non-matching instruments); synthetic-validate
distribution fitters before banking; per-φ aggregation (never concatenate positions
across φ — superposition bug); permanent on-disk banking of raw spectra/event-trains;
worker-count = 10 for bandwidth-bound unfolds (probe, don't assume); ratio-vs-magnitude
discipline (the Phase-35 3.55× lesson); tangent-space (not time-series) Lyapunov for
simulated substrates with known equations.

**Positioning — ARS within point-process methodology (Cox / Neural-TPP / FDA).** A point
process is characterizable at four complementary levels: (1) *smooth structure* — FDA treats
the counting/intensity as a smooth function; (2) *rate covariates* — Cox / modulated-Poisson
model the conditional rate vs covariates; (3) *predictability* — neural TPPs learn the
conditional intensity for next-event prediction; (4) *universality class* — the unfolded
nearest-neighbour spacing distribution's RMT/clock/Poisson class. **ARS operates at level (4):**
after rate-removal (unfolding to unit mean) it classifies the spacing-statistics universality
class. It does NOT model rate (2), predict events (3), or fit smooth intensity (1) — those are
complementary, not competing. The landscape's claims are universality-class placements; this
note fixes what ARS reads vs. what it does not.

**Number-theoretic frame (Stern-Brocot / Sturmian / Lagrange stratification).** The
arithmetic-parameter side (brocot.fm; AM's θ) has a unifying structure. Every infinite
Stern-Brocot path (modulo eventually-monotone tails) encodes an irrational α via its
continued-fraction expansion; the **Sturmian word** of slope α (the mechanical/Beatty
sequence) is the natural event-train — making *parameter-side path ↔ spectral-side
event-train* explicit. **Lagrange's theorem** stratifies α by CF structure: rationals
(terminating CF / finite path) · quadratic irrationals (eventually-periodic CF — the metallic
means golden=[1;1,…], silver=[2;2,…], bronze=[3;3,…]) · higher-algebraic/transcendental
(non-periodic, unbounded partial quotients — Liouville). This predicts the Sturmian-toward-α
family (and AM's θ-class family) should **cluster by CF class**: bounded-quotient (Diophantine)
vs unbounded (Liouville-like). The AM sup-θ result is consistent — Brody q falls golden (0.81,
hardest-to-approximate) → silver (0.44) → Liouville (0.28, super-approximable), a
Lagrange-stratification signature in the spectral fingerprint. **brocot.fm (when added) tests
this directly:** sweep a Stern-Brocot path, watch the fingerprint move along the stratification.
Proposed as a viewpoints substrate-class.

## 5. Descriptive landscape observations (flagged, not interpreted)

Figures committed (`cross_substrate/figures/`, static PNG): **P1** universal q-banded
(I.5q × rep_med), **P2** matched repulsion plane (Brody × BR, 11 substrates), **P3** I.5q
strip, **P4** Family-V dynamical sub-landscape (D₂ × W1δ trajectories). Regenerate via
`landscape_view.py`. Interactive / unified-all-14 projection still pending (no single axis
spans all 14 — see §2).

- Arithmetic spectra (ζ/Dirichlet/EC, Maass, primes) cluster GUE-like (low I.5q).
- Mertens/Liouville far-from-GUE (clustered). Bio (pvc-11, Allen) + Kuramoto middle.
- Kuramoto is a *trajectory* (K-sweep climbs repulsion) — multi-scope movement.
- Viewpoint-dependence: pvc-11 and Mertens/Liouville collapse together in Brody/BR
  space but separate sharply in W1δ — the operational case for many viewpoints.

## 6. Open threads

- **L-zeros split** — separate ζ (GUE) from Dirichlet/EC (Poisson-leaning) in §3.
- **Math-path** — derive the condition the sup θ / OSI inter-leg gap depends on
  (across-band-skew ruled out as primary).
- **Breadth** — FM/brocot.fm (Will's own substrate); Family V on Kuramoto (order-parameter
  trajectory); **Sturmian-word θ-sweep** across Lagrange classes (cheap, arithmetic — directly
  tests the CF-class cluster prediction of §4's number-theoretic frame; the bridge to brocot.fm).
- **AM** — sub-side at converged L (currently non-converged); slate-4 N-trajectory
  (multi-day).

*Done since v1:* aggregator fixed (~200× via capped Family-II windows); Family-II
consistency re-run (all matched substrates on one algorithm); Mackey-Glass + Lorenz +
logistic added with validated Family V; AM θ-class extension; views refreshed to 14
substrates (figures P1–P4); Family-V λ moved to tangent-space (Benettin/analytic) —
correct sign+magnitude, Lorenz ρ=28→0.909.
