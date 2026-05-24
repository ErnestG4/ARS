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

**(h) The confluence is UNIVERSAL across Lagrange classes; the matching coupling λ* stratifies
(theta_class_correspondence.py + liouville_nconv.py).** AM-critical (λ=1, self-dual) vs Fibonacci-α
D_box(λ) per class: golden (AM-crit 0.513, λ*=3.42), silver (0.520, 3.32), bronze (0.511, 3.41) all
confluence at λ*≈3.3–3.4 — the matching coupling is **α-invariant within the metallic means** (one
universal λ*, not a per-α adjustment). **Liouville also confluences** (Liouville N-check: AM-crit-Liouville
D_box=0.490 N-converged 50k–200k; Fibonacci-Liouville reaches it at **λ*≈10.7** — the λ≤8 "no crossing"
was a grid-range artifact, NOT N-limited and NOT a class boundary). ⇒ **AM ≡ Fibonacci up to
parameterization across the WHOLE Lagrange spectrum** (strongest operator-IS-substrate state the program
has produced); the Lagrange-stratification signature lives in the **coupling-correspondence** (λ*≈3.4 for
metallic means → ~10.7 for super-approximable Liouville), not in whether confluence occurs. Mechanistically
(flagged): Liouville's long near-periodic stretches make its Sturmian spectrum more band-like at given λ,
so it needs stronger coupling to fractalize to AM-crit's 0.49. Sub-finding: (i) **AM-critical D_box is
class-near-INVARIANT (~0.51 quadratics, 0.49 Liouville)** — contrast to the AM-sup-θ Brody stratification
(0.81/0.44/0.28); criticality washes out the θ-sensitivity the localized regime shows (≈½ universal
critical-AM box-dim). Figures P8 (metallic means) + P9 (Liouville N-conv).

**(i) θ-class information propagates differently through AM's three phase regimes — a substrate
property.** Reading the same operator (AM, golden vs other θ) at three phase-diagram points gives three
distinct relationships to Diophantine structure:
- **Sub (λ<1, AC regime):** clock-rigid, **θ-invariant** — the spectrum is too smooth (absolutely
  continuous, band) to carry θ-class information; Diophantine distinctions suppressed.
- **Critical (λ=1, self-dual transition):** D_box **θ-invariant among quadratics (~0.51)** — the
  self-dual critical point is Diophantine-UNIVERSAL; it does not resolve fine class distinctions (§3(h)).
- **Sup (λ>1, PP regime):** Brody q **θ-STRATIFIED** (golden 0.81 → silver 0.44 → Liouville 0.28,
  §3(e)) — the localized/fragmented spectrum carries θ-class info in its level repulsion.
⇒ same parameter, same operator, three phase points → θ-class info is **suppressed (sub) / washed out
(critical) / preserved (sup)**. A substantive finding about how AM *processes* Diophantine-class
structure as a function of where in the phase diagram the fingerprint is read. (Flagged, not interpreted.)

**(j) λ\*(class) is a CONTINUOUS APPROXIMABILITY stratification — single universality class
(lambda_star_classes.py + lambda_star_nconv.py).** Mapping the matching coupling λ* across 9 Lagrange
classes (golden/silver/bronze/metallic4/5, e−2, ln2, π−3, Liouville) resolves what λ* tracks, refuting
BOTH binary extremes: (1) **NOT a step at CF-boundedness** — the discriminator **e** (μ=2, UNbounded CF)
lands at λ*=3.78 (N-confirmed @100k), with the metallic means, not Liouville; (2) **NOT pure-μ** — at
fixed μ=2, λ* spreads 3.32 (silver) → 4.98 (metallic5) with CF-quotient magnitude. ⇒ λ* tracks
**approximability** (rational-approximation quality, combining quotient size AND μ): most-Diophantine
classes floor at λ*≈3.3–3.8, rising continuously through ln2/metallic5/π to Liouville's ~10.7 — the
metallic-mean cluster and Liouville are endpoints of an **approximability continuum, not two CF classes**.
Two distinct claims: **(i) AM-crit D_box is approximability-INVARIANT** (~½, in [0.49,0.53] across all 9)
— AM-criticality universal in the Bellissard sense; consistent with **Jitomirskaya-Krasovsky (D≤½)** +
**Wilkinson-Austin 1994 (~½)**. **(ii) The Fibonacci λ-Cantor-curve is approximability-GRADED** — more-
approximable α needs more coupling to fractalize (high approximability ≈ almost-rational → Fibonacci AC
band → stronger coupling to reach Cantor); all the λ* variation lives on the Fibonacci side. **Connects
to Damanik-Gorodetski 2014 / Cao-Qu 2023** (a.e.-frequency dim-constancy at large coupling): empirically
confirms the asymptotic constancy AND characterizes its approach — more-approximable (measure-zero) α
reach the asymptotic regime at higher λ (a convergence-rate extension). N-confirmed (e/π drift <0.1
50k→100k; Liouville ~10.7). Figure P10. (Verdict: Will, 2026-05-23.)

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
not assumed-canonical — sibling of ratio-vs-magnitude); **when a crossing/match is ABSENT,
check both N-convergence AND parameter-range before concluding** (the Liouville λ≤8 "no
crossing" was a grid-range artifact, not a class boundary — the crossing was at λ≈10.7;
absence-of-crossing has two escape hatches, finite-N and finite-range, and both must be
closed); **carry the Phase-35 L_iter convergence discipline into cross-substrate work** —
unbounded-CF substrates (Liouville) raise legitimate finite-N concerns, so N-converge the
fingerprint empirically before declaring a class boundary (the Liouville N-check was
diligence, not a response to misbehavior; both legs converged cleanly).

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
curves on one axis; Fibonacci reaches AM-crit at λ≈3.46), **P8** θ-class correspondence (Fibonacci-α
D_box(λ) per Lagrange class vs AM-crit-θ; quadratics confluence at λ*≈3.4; `theta_class_correspondence.py`),
**P9** Liouville N-convergence (AM-crit-Liouville N-converged 0.49; Fibonacci-Liouville crosses at λ*≈10.7;
`liouville_nconv.py`), **P10** λ*(class) approximability stratification (λ* vs μ, CF-boundedness encoded;
`lambda_star_classes.py`). Regenerate via `landscape_view.py` + `confluence_view.py` +
`theta_class_correspondence.py` + `liouville_nconv.py` + `lambda_star_classes.py`. Interactive projection still pending; P6 is the static unified view.

- Arithmetic spectra (ζ/Dirichlet/EC, Maass, primes) cluster GUE-like (low I.5q).
- Mertens/Liouville far-from-GUE (clustered). Bio (pvc-11, Allen) + Kuramoto middle.
- Kuramoto is a *trajectory* (K-sweep climbs repulsion) — multi-scope movement.
- Viewpoint-dependence: pvc-11 and Mertens/Liouville collapse together in Brody/BR
  space but separate sharply in W1δ — the operational case for many viewpoints.

## 6. Open threads

- ~~L-zeros split~~ **DONE** (lzeros_split.py) — ζ-GUE / Dirichlet / EC now separate substrates;
  Dirichlet/EC Poisson-reading carries the cross-conductor-pooling caveat.
- ~~Fibonacci-λ-sweep~~ **DONE** (§3(g)) and ~~Fib-θ-class sweep~~ **DONE** (§3(h)) — AM↔Fibonacci
  confluence generalizes across the quadratics (golden/silver/bronze, λ*≈3.4); Liouville is N-ambiguous.
- ~~Liouville N-convergence check~~ **DONE** (liouville_nconv.py) and ~~intermediate-class λ* sweep~~
  **DONE** (§3(j); lambda_star_classes.py + lambda_star_nconv.py) — λ* is a continuous approximability
  stratification, single universality class; AM-crit approximability-invariant, Fibonacci side graded.
  Possible next: **a Fibonacci-side dimension theory cross-check** — compare the approximability-graded
  D_box(λ) curves against the Damanik-Gorodetski/Cao-Qu predicted large-λ asymptotics quantitatively
  (does the convergence rate match a known functional form in the approximation exponents?).
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
