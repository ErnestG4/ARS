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
| L-zeros: ζ / Dirichlet / EC | 2 / 2 / 4 | q-banded + matched | SPLIT by class (was bimodal pool); ζ→GUE, Dirichlet/EC→Poisson-leaning w/ cross-conductor-pooling caveat |
| Mertens / Liouville | 3 / 4 | q-banded + matched | |
| Gaussian / Eisenstein primes | 2 / 1 | q-banded + matched | |
| Maass Γ₀(N) | 6 | q-banded + matched | |
| Pulsar (NANOGrav) | 10 | direct-leg | cross-domain bounded |
| **Mackey-Glass** | 5 | matched + Family V | τ-sweep trajectory; peak-NNS |
| **Lorenz** | 4 | matched + Family V | ρ-sweep trajectory; lobe-NNS |
| **Logistic** | 5 | matched + Family V | r-sweep (period-doubling); IEI-NNS; analytic λ |

Plus **Sturmian-word** (8 α, Lagrange-class sweep) and **Sturmian-Hamiltonian** (7 α; = Fibonacci
Hamiltonian at golden). With the L-zeros split (ζ/Dirichlet/EC → 3) this is **18 distinct
substrates**; plus `am-confluence` (a λ-trajectory of the AM substrate banked separately for the
confluence test — a study artifact, not a new substrate). Families computed: I (NNS distances I.1–I.9),
II (Σ²/Δ₃/K), III (RF, where banked), **IV (spectral box-dimension — Sturmian-Ham + am-confluence)**,
V (dynamical λ₁/D₂ — 3 dynamical substrates), VI (extraction-meta α/β/cross-extract), VII (inter-leg
disagreement). Only the bridged ks-GUE axis (matched I.5 where present, else q-banded I.5q — the
proxy verdict licenses it) spans all substrates (figure P6); the others are leg-scoped (matched W1δ ⊃
object-(a); Family V ⊃ time-series; Family IV ⊃ operator-spectrum substrates).

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

**(g) AM-vs-Fibonacci confluence (am_confluence.py) — partial confluence, FLAGGED.** The
operator-IS-substrate framing's strongest concrete prediction: does AM's fingerprint trajectory
(λ-sweep at golden θ through criticality) pass through the Fibonacci Hamiltonian's? Instrument-matched
to Fibonacci (D_box on raw eigenvalues + same poly_unfold). D_box traces a clean **V bottoming at
criticality** (λ=1 → 0.513), near-symmetric about λ=1 (Aubry-André self-duality), with a wide q=0
plateau (λ≈0.9–1.3). **Qualitative class confluences** at criticality (q→0, W1δ→1.98, ks_gue→1.0,
Cantor) but **quantitative D_box does not** — AM-crit 0.513 overshoots below Fibonacci's 0.628 (which
is at *its* λ=2); the trajectory crosses 0.628 only off-criticality. ⇒ Will's outcome (2),
similar-but-distinct operator families. Critical D_box is N-converged (0.513 across 50k–200k).
AM-crit ≈0.51 sits near the known ≈½ box-dim for critical AM at golden flux (instrument validation).
**Coupling caveat RESOLVED (fibonacci_lambda_run.py):** swept the Fibonacci coupling λ at golden — its
D_box decreases monotonically (N-stable at λ=2: 0.628 across N=8k/50k/100k, clearing the N-mismatch)
and CROSSES AM-crit's 0.514 at λ≈3.46, where the full Family-I fingerprint coincides (W1δ≈1.96,
ks_gue≈0.94, q=0). ⇒ the "distinctness" was a non-corresponding-coupling artifact; AM-critical IS a
member of the Fibonacci fractal-Cantor family (shifts toward outcome (1)). NUANCE: AM-crit is a
special self-dual zero-measure point; Fibonacci λ≈3.5 is generic — same fingerprint value, different
dynamical status. Figure P7 (both D_box(λ) curves).
**VERDICT (Will, 2026-05-23): outcome (1) — they confluence at the fingerprint level; the routes to
the fingerprint differ** (AM via a phase transition at self-dual λ=1, Fibonacci generically Cantor at
λ≈3.46). The dynamical-status difference is ENRICHMENT, not refutation. Two operator families sharing
α=golden produce coordinate-identical fingerprints at matched coupling via different mechanisms —
exactly the universality-class confluence operator-IS-substrate predicts. Strengthens the framing.

## 4. Methodology established

Matched-instrument across compared legs (carry every viewpoint, annotate
comparison-validity, don't discard non-matching instruments); synthetic-validate
distribution fitters before banking; per-φ aggregation (never concatenate positions
across φ — superposition bug); permanent on-disk banking of raw spectra/event-trains;
worker-count = 10 for bandwidth-bound unfolds (probe, don't assume); ratio-vs-magnitude
discipline (the Phase-35 3.55× lesson); tangent-space (not time-series) Lyapunov for
simulated substrates with known equations; **matched-reference discipline — sweep
coupling-class parameters before declaring two substrates distinct** (the AM-vs-Fibonacci
λ=2 lesson: a fixed-reference two-point comparison read "distinct" and would have missed
the confluence a coupling-sweep revealed at λ≈3.46; reference parameters must be matched,
not assumed-canonical — sibling of ratio-vs-magnitude).

**Boundary — the fingerprint is blind to route (what it does and does not resolve).** The
confluence axes (W1δ, ks_gue, Brody q, D_box, Σ²/Δ₃) measure *spectral structure*, not
*dynamical-system structure*. They CANNOT distinguish a phase-transition Cantor (AM at the
self-dual λ=1) from a generic Cantor at modulated coupling (Fibonacci at λ≈3.46): same
coordinates, different operator-internal status. This is not a flaw — it is *why* confluence
is meaningful (universality-class confluence is the program's principal yield) — but it is a
real limit: two substrates at the same coordinates may have reached them by structurally
different mechanisms, so **mechanism is under-determined by fingerprint alone.** Resolving
special-point vs generic Cantor would need axes not currently in viewpoints (phase-diagram
position, operator-dynamical structure beyond NNS/Σ²). Read the landscape accordingly:
coincident coordinates assert shared universality class, not shared mechanism.

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

Figures (`cross_substrate/figures/`, static PNG): **P1** universal q-banded (I.5q × rep_med),
**P2** matched repulsion plane (Brody × BR; am-confluence excluded — trajectory, see P5), **P3**
I.5q strip, **P4** Family-V dynamical sub-landscape (D₂ × W1δ trajectories), **P5** AM-vs-Fibonacci
confluence (D_box-vs-λ V + repulsion-plane trajectory; `confluence_view.py`), **P6** unified bridged
ks-GUE strip — every substrate on one axis (matched I.5 ● / q-banded I.5q ■ via proxy verdict; the
resolution of "no single axis spans all"), **P7** coupling correspondence (AM + Fibonacci D_box(λ)
curves on one axis; Fibonacci reaches AM-crit at λ≈3.46). Regenerate via `landscape_view.py` +
`confluence_view.py`. Interactive projection still pending; P6 is the static unified view.

- Arithmetic spectra (ζ/Dirichlet/EC, Maass, primes) cluster GUE-like (low I.5q).
- Mertens/Liouville far-from-GUE (clustered). Bio (pvc-11, Allen) + Kuramoto middle.
- Kuramoto is a *trajectory* (K-sweep climbs repulsion) — multi-scope movement.
- Viewpoint-dependence: pvc-11 and Mertens/Liouville collapse together in Brody/BR
  space but separate sharply in W1δ — the operational case for many viewpoints.

## 6. Open threads

- ~~L-zeros split~~ **DONE** (lzeros_split.py) — ζ-GUE / Dirichlet / EC now separate substrates;
  Dirichlet/EC Poisson-reading carries the cross-conductor-pooling caveat.
- ~~Fibonacci-λ-sweep~~ **DONE** (fibonacci_lambda_run.py) — Fibonacci D_box reaches AM-crit 0.51 at
  λ≈3.46; coupling caveat resolved toward confluence (§3(g)). Possible next: a Fib-θ-class sweep
  (silver/bronze/Liouville coupling curves) to test whether the AM-θ ↔ Fibonacci correspondence holds
  beyond golden.
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
*Done 2026-05-23 (data-shoring + confluence):* integrity audit (all files clean); L-zeros split
(ζ/Dirichlet/EC, pooling caveat); AM-vs-Fibonacci confluence test (partial confluence, FLAGGED;
am-confluence.jsonl + P5); unified bridged ks-GUE strip P6 (resolves "no single axis spans all").
