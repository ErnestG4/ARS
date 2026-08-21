# Cross-Substrate Landscape — Progress Report

**Date:** 2026-05-24. **Status:** v1 consolidation. §0 = the legible-at-a-glance synthesis;
§1–7 = the detailed chronological build-record (retained as the audit trail).
Companions: `landscape.md` (map + §0 dashboard), `viewpoints.md` (axes), `findings_log.md`
(run-by-run detail), `coordinates/*.jsonl` (banked values). Progress log —
NOT validated results; verdicts are Will's.

---

## §0 — Program state (v1 consolidation, 2026-05-24)

### Inventory — ~25 substrates across 6 families
- **Quasi-periodic / arithmetic operators (eigenvalue spectra):** almost-Mathieu (AM), Fibonacci/Sturmian
  Hamiltonian, generalized-AAH (gaah), extended-Harper, mosaic-AM, Maryland; ζ / Dirichlet / EC L-zeros,
  Mertens, Liouville, Gaussian + Eisenstein primes, Maass forms.
- **Dynamical systems (Family V):** Mackey-Glass, Lorenz, logistic, Rössler, Chua, Duffing, Hénon.
- **FM synthesis:** brocot.fm (4,292 exemplars + the Stern-Brocot-walk approximability test) — the only
  substrate with BOTH sides directly accessible (SB-path parameter + analytic partial spectrum).
- **Neural:** pvc-11 V1 (monkey); Allen Brain Observatory (8,462 cells × 7 areas × 8 stimuli) +
  population-level observables (corr-eig / avl-onset / sync-event).
- **Other point processes:** Kuramoto, NANOGrav pulsar.
- **Calibration anchors:** GUE / GOE / GSE / Poisson / clock / uniform-jitter (the landscape corners).
- **Axes:** Family I (NNS I.1–I.9), II (Σ²/Δ₃/K long-range), III (RF per-prime), IV (spectral box-dim),
  V (λ₁/D₂ dynamical), VI (extraction-meta), VII (inter-leg disagreement). Figures P1–P11 + P_allen_depth /
  P_brocot_approx / P_qpo_approx / P_qpo_deepening.

### Headline I — APPROXIMABILITY STRATIFICATION (the central thread)
Across substrates organized by a Diophantine frequency parameter, the spectral fingerprint stratifies by
the parameter's **approximability** (rational-approximation quality): least-approximable (golden / metallic
means) → repulsive / GUE-like / higher fractal dimension; most-approximable (Liouville, high-μ) → clustered
/ Poisson / lower. Established across **6 substrates in two mechanistically-distinct classes:**
- **Quasi-periodic operators** (AM, Fibonacci, gaah, ext_harper): D_box / Brody q stratify at the
  critical/fractal coupling (ρ(rank,D_box)≈−0.7; N-robust, robust across coupling). CONDITIONED on a
  critical regime — Maryland (always-pure-point) is a flat negative control, mosaic doesn't stratify → NOT
  universal across all quasi-periodic operators.
- **FM synthesis** (brocot.fm, partial spectra): Brody q falls with approximability, ρ(rank,q)=−0.91 — a
  mechanistically-different substrate confirming the axis is a substrate-CLASS property.
  **⚠ SUPERSEDED 2026-08-19 — see "BROCOT RESOLVED" at the end of this file. The −0.91 is an artifact
  of using ONE representative per Lagrange class; on class means the CI includes zero, so the
  "substrate-CLASS property" reading specifically DOES NOT HOLD. The phenomenon survives as a
  PER-α relation at the instrument's resolution (ρ = +0.699, n = 255).**
Two structural claims recur across all: (1) a "Diophantine GUE corner" the least-approximable classes share
(universal-ish); (2) graded separation of the approximable classes. **GROSS-axis agreement, FINE-structure
SPLIT:** the operator family agrees on fine structure (continuous-in-approximability / quotient-magnitude;
e stays with the metallic means), while brocot is the lone outlier (bounded-vs-unbounded-CF *step*; e drops
with the unbounded group). AM≡Fibonacci specifically: the same operator family up to an
approximability-dependent coupling reparametrization (λ* α-invariant within metallic means → ~3× larger for
Liouville). The quantitative DEGT strong-coupling constant ln(1+√2) is FORM-confirmed, constant-DEFERRED
(needs trace-map thermodynamic formalism). **Mechanism question — RESOLVED (cf_mechanism.py):** why
operators are continuous-in-approximability while brocot is a CF-boundedness step. brocot Brody q STEPS on
the bounded/quadratic-vs-transcendental CF binary (mean 0.982 vs 0.271, Δ=+0.71); operator D_box is
CONTINUOUS in μ (ρ=−0.63). **e−2 is the discriminator that splits the two predictors** (transcendental/
unbounded CF, but μ=2): brocot q(e)=0.568 drops with the transcendentals, operator D_box(e)=0.782 stays high
with golden — the same number on opposite sides of the two fingerprints. ⇒ brocot's NNS reads the LOCAL CF
structure (three-distance theorem: periodic CF ⇒ self-similar balanced {nα} gaps ⇒ repulsive), the
operators' D_box reads the GLOBAL spectral dimension (trace-map integrates the whole CF). Confirms the WHY,
not just the THAT. **Confound DECOMPOSED (cf_discriminator.py):** cf_mechanism had to flag that boundedness
& quadraticity are confounded for natural α. A designed second discriminator resolves it — hold the CF
quotient alphabet fixed at {1,2} and vary ONLY periodicity (periodic_12=√3−1 bounded-quadratic vs Thue–Morse
/ Fibonacci-word bounded-NONquadratic). The bounded-nonquadratic α give brocot q=1.000, WITH the bounded-
quadratic anchor (golden/silver/periodic_12 mean 0.969), far from the unbounded anchor (e/liouville 0.284);
flipping periodicity left q unchanged. **⇒ the brocot trigger is BOUNDEDNESS of partial quotients (the
badly-approximable / Diophantine class), NOT the algebraic quadratic class**
**[REFINED 2026-08-19, see "BROCOT RESOLVED" below: this survives in its FINITE-WINDOW form — max CF
term over the first 8, ρ = −0.599 — but NOT as an asymptotic class statement. The instrument's
sidebands are bounded by the FM index, so it cannot see the CF tail that defines the class.]** — quotient MAGNITUDE sets
convergent-denominator growth → three-distance gap balance; CF periodicity is irrelevant. Operator control:
all μ=2 bounded targets D_box=0.785±0.016 (flat across periodicity) — operators read μ, blind to the split.
**Split is SUBSTRATE-TYPE-GROUNDED, not an axis artifact (observable-binding clarification):** the
brocot-step/operator-continuum 2×2 has two intrinsically-uninformative off-diagonals — brocot box-dim is
comb-noise (no fractal in a deterministic FM partial set), operator NNS is Cantor-degenerate (q≈0 every
class/coupling 0.5–4). Spectral TYPE forces the observable (point-process→NNS, Cantor→box-dim); neither
substrate is readable on the other's axis. Two-layer landscape architecture (with the dynamical-breadth
Family-V finding): (L1) substrate CLASS needs observable FAMILY [Family V λ/D₂ vs Family I–III for spectral];
(L2) within a family, spectral TYPE affords the specific observable [NNS vs box-dim] — both layers say
substrate type forces observable, and the SHARED finding is the underlying approximability axis each
observable exposes. Honest caveat: boundedness-step & μ-continuum are partly observable-bound (boundedness is
what NNS sees, μ what box-dim sees) — strengthens the landscape (explains differential manifestation without
trivial-confound or over-universality). Banked as clarification (findings_log; the 2×2 is the durable artifact).

### Headline II — NEURAL: per-cell COHERES, population FRAGMENTS
- **Per-cell** (Allen, 8,462 cells): fingerprints cohere as one "visual cortex" substrate. H1 (OSI↔ks_gue)
  GENERALIZES across all visual areas + LGN (pathway-independent, not V1-specific); orientation-domain
  tuning (OSI/DSI/F1F0) couples, frequency tuning (SF/TF) does not; within-cell STIMULUS-STATE is a live
  axis (a fixed cell's class shifts with stimulus); no spatial autocorrelation < 1 mm.
- **Population** (all 12 sessions): fingerprints FRAGMENT by aggregation — 3 trustable observables span the
  full axis (corr-eig→GUE / avl-onset→intermediate / sync-event→Poisson), consistent across sessions;
  aggregation (not session) sets the class. No single "population fingerprint." Avalanche-criticality
  (near-critical, Beggs-Plenz-consistent) is ORTHOGONAL to per-cell class. Family VII (|I.5q−I.5| OSI-grading)
  is monkey-STRONG / mouse-WEAK (graded, not absent).

### Methodology spine (the disciplines that emerged — detail in §4; memory-linked)
**DISCRIMINATION FAMILY (is this the real question / the real signal?):** discriminant-exact-question
(substantive question vs heuristic proxy, [[discriminant_exact_question_check]]); decompose-confound-with-a-
designed-instance (e-discriminator + Thue-Morse-CF, [[decompose_confound_designed_instance]]); intrinsic-vs-
extrinsic predictor (the strong correlate is often intrinsic/tautological — burst↔ks_gue; the meaningful link
is extrinsic selectivity, [[intrinsic_vs_extrinsic_predictor]]); observable-binding clarifies (spectral TYPE
forces the observable; substrate-type-grounded, not artifact; region-match the selectivity axis in brain-wide
data, [[observable_binding_clarifies]]).
**VERIFICATION (validate before trusting):** synthetic-validate fitters/estimators against known ground
truth ([[synthetic_validate_fitters]]); validate scale-convergence + scale-invariance before an asymptotic
constant ([[validate_scale_convergence_before_asymptotic_constant]]); confirm per-cell/selectivity
correlations at FULL n (3-session hints flip under power); induction-on-noise to confirm extractor artifacts;
per-prime-baseline z-scoring — raw amplitudes NOT cross-prime comparable (p2-saturation artifact, sibling of
[[support_set_respecting_nulls]]); per-φ aggregation (never position-concat).
**CROSS-SUBSTRATE:** matched-instrument + carry-viewpoints-annotate-validity; sweep coupling-class before
declaring distinctness ([[sweep_coupling_class_before_distinctness]]); close BOTH escape hatches (finite-N AND
finite-range); fingerprint is blind-to-route (coincident coordinates assert shared class, not mechanism);
rate-match-from-the-start incl. the population-level recipe ([[ars_rate_dependence_lesson]]).
**ACQUISITION:** sequential + size-verify ([[parallel_curl_corruption]]); turnkey DANDI NWB (desc-processed
not desc-raw) → h5py-direct; fsspec remote-HDF5 region-scan to target brain-wide data without bulk download;
custom-format off-DANDI = a planned ENGINEERING ARC, not a cycle ([[planned_engineering_arc]]).

### Status — landed vs open
**LANDED** (committed; pushed through `5b72706`; unpushed `12e5c1b`/`ee637c3`/`4172bc7`): the approximability
program (6 substrates, gross-agree/fine-split, DEGT form-confirmed); the neuro arc (per-cell + population +
criticality); the 7-system Family-V dynamical landscape; calibration anchors; the brocot bridge + corpus;
landscape v1 dashboard; the CF-boundedness-vs-continuous MECHANISM (cf_mechanism.py — e splits brocot's
LOCAL three-distance step from the operators' GLOBAL continuous-μ); the boundedness-vs-quadraticity
DISCRIMINATOR (cf_discriminator.py — designed bounded-nonquadratic α; the brocot trigger is boundedness,
not quadraticity; confound decomposed).
**OPEN:** trace-map TD-formalism dimension (deferred quantitative DEGT piece); Tier-2 Buzsaki / Tier-3 IBL (acquisition — interactive);
brocot submodule-bump + tooling relocation (when recordings land); p2-saturation RF diagnostic (minor).

---

## 1. Frame

Operator-IS-substrate: each substrate is fingerprinted on its spectral side and
placed in a shared universality-class landscape; the yield is the cross-substrate
*comparison*, not utility-extraction from any one substrate. Explorer-shaped
(charting, not hypothesis-testing).

## 2. What's populated (original operator/arithmetic snapshot — full current inventory in §0)

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

**(k) Dimension-theory cross-check vs DEGT — PARTIAL, exact constant DEFERRED (dimension_theory_check.py
+ trace_map_dimension.py).** Quantitative test of §3(j)'s connection: does the Fibonacci D(λ) curve
confirm the Damanik-Embree-Gorodetski-Tcheremchantsev (CMP 2008, arXiv:0705.0338) strong-coupling
asymptotic **dim(Σ_λ)·ln(λ) → ln(1+√2) ≈ 0.8814** (golden)? **Honest landing — form confirmed, constant
deferred.** (1) The **D ~ C/ln(λ) FORM holds** (R²≈0.98, moderate λ). (2) An **exact band-edge instrument**
(band edges = periodic/antiperiodic eigenvalues of the period-q approximant — grid-free, resolves all q
bands at any λ) was built and **VALIDATED against box_dim at λ=8 (0.370 vs 0.369)**; dim·ln(λ) climbs into
the **0.77–0.84 neighborhood** of 0.8814 at moderate λ. (3) BUT **a sharp confirmation is NOT achieved by
the accessible estimators**: eigenvalue box-counting breaks at large-λ cluster-splitting (spectrum → V=0 +
V=λ clusters, span-relative boxes measure the gap) + finite-N depth-capping; and the single-level Bowen
pressure Σ|band|^d=1 is **NOT scale-invariant** → diverges with q/λ (golden dim·ln(λ)→1.72 at λ=1024,
extrapolated C=2.12 — artifact; q=64 not q-converged: 0.82→0.98 over q=377→1597). The correct estimator
needs renormalization **contraction RATIOS** (Moran/pressure Σrᵢ^d=1) — the trace-map **thermodynamic
formalism**, a dedicated future arc. No valid P11 (broken extrapolations not banked). Flagged.

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
diligence, not a response to misbehavior; both legs converged cleanly); **"looked right at
moderate scales" ≠ "correct asymptotically" — validate an estimator's scale/size-convergence
before trusting an extrapolated asymptotic constant** (§3(k): box-counting plateaus then breaks
at cluster-splitting, and the Bowen pressure Σw^d=1 is scale-DEPENDENT — uses absolute widths, so
it looks plausible at moderate q/λ but diverges as they grow; a self-similar-Cantor dimension needs
the scale-invariant Moran/thermodynamic-formalism pressure on contraction RATIOS). Accessible quick
estimators can verify a FORM but not an asymptotic CONSTANT — that needs the right formalism, not a
finer sweep. Sibling of [[synthetic_validate_fitters]]; **data-acquisition discipline** (carried from
Phase 24, [[parallel_curl_corruption]]): fetch large external datasets SEQUENTIALLY with
size-verification — never parallel/overlapping curls on shared paths — and scope the cache + download
footprint BEFORE committing an overnight run.

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
  ~~Fibonacci-side dimension-theory cross-check~~ **ATTEMPTED → DEFERRED** (§3(k)): form confirmed +
  band-edge instrument validated at moderate λ, but the exact DEGT constant ln(1+√2) needs the
  **trace-map thermodynamic formalism** (Moran/pressure on renormalization contraction ratios) — a
  dedicated future arc; accessible quick estimators (box-counting; single-level band-pressure) can't
  pin the asymptotic constant.
- **Math-path** — derive the condition the sup θ / OSI inter-leg gap depends on
  (across-band-skew ruled out as primary).
- **Breadth** — FM/brocot.fm (Will's own substrate); Family V on Kuramoto (order-parameter
  trajectory); **Sturmian-word θ-sweep** across Lagrange classes (cheap, arithmetic — directly
  tests the CF-class cluster prediction of §4's number-theoretic frame; the bridge to brocot.fm).
- **AM** — sub-side at converged L (currently non-converged); slate-4 N-trajectory
  (multi-day).
- **Neuro (from §7):** spatial axes (depth-stratified — needs better layer assignment than
  probe_vertical proxy; population-level fingerprints as a distinct substrate — avalanche-criticality
  is orthogonal to per-cell, §7(h)); Tier-2 Buzsaki hippocampus / Tier-3 IBL (own acquisition lift —
  CRCNS credentials / ONE-api, scope interactively); the 4-way Family-VII candidate disambiguation
  (species / state / tech / sampling-geometry — needs awake-macaque or anesthetised-mouse + a 2D-array
  vs 1D-probe contrast).

*Done since v1:* aggregator fixed (~200× via capped Family-II windows); Family-II
consistency re-run (all matched substrates on one algorithm); Mackey-Glass + Lorenz +
logistic added with validated Family V; AM θ-class extension; views refreshed to 14
substrates (figures P1–P4); Family-V λ moved to tangent-space (Benettin/analytic) —
correct sign+magnitude, Lorenz ρ=28→0.909.
*Done 2026-05-23 (data-shoring + confluence):* integrity audit (all files clean); L-zeros split
(ζ/Dirichlet/EC, pooling caveat); AM-vs-Fibonacci confluence test (partial confluence, FLAGGED;
am-confluence.jsonl + P5); unified bridged ks-GUE strip P6 (resolves "no single axis spans all").
*Done 2026-05-24:* AM↔Fibonacci arc closed (metallic-mean generalization §3(h), θ-propagation §3(i),
λ*-approximability stratification §3(j), P7/P8/P9/P10); dimension-theory cross-check §3(k) PARTIAL
(form confirmed, constant deferred to thermodynamic formalism). **NEXT: pivot to neuro spike-train
depth expansion — Tier-1 Allen Brain Observatory depth-extension** (all visual areas + LGN across
sessions; q-banded at scale via the proxy verdict; H1/Family-VII/cross-area hooks). Scope download
footprint first (acquisition discipline, §4).
*Done 2026-05-24 (neuro depth-extension, §7):* 60,833 (cell,stimulus) records / 8,462 cells across 12
sessions × 7 areas × 8 stimuli (no download — cached); I.5q+I.5+W1δ + Family II + avalanche criticality;
8 findings (a–h) — H1 generalizes across areas, OSI/DSI privileged, Family VII mouse-weak, tight
cross-area cluster, within-cell stimulus-state axis, weak depth gradient / no spatial autocorrelation,
Family II partially-distinct, avalanche-criticality orthogonal to per-cell. classify worker-knee=14.
All FLAGGED for adjudication; staged uncommitted for review.

---

## 7. Neuro depth-extension — Allen Brain Observatory (2026-05-24)

Tier-1 spike-train depth expansion (the neuro pivot). Scaled Phase-2a (719 V1 cells, drifting
gratings) to the full cached corpus: **12 sessions × 6 visual areas (V1/LM/RL/AL/PM/AM) + LGN ×
8 stimulus blocks → 60,833 (cell,stimulus) records, 8,462 cells**, each with I.5q + matched I.5 +
W1δ (allen_depth.py) + Family II Σ²/Δ₃/K (allen_depth_fam2.py), tagged area + tuning (OSI/DSI/SF/TF/
F1F0/run). No download (cached NWBs, h5py-direct). Runners: allen_depth*.py, allen_avalanche.py;
analysis: allen_depth_analysis.py / _spatial.py / allen_fam2_analysis.py. All FLAGGED (verdicts Will's).

**Headline findings:**
- **(a) H1 generalizes across ALL visual areas.** OSI↔ks_gue ρ≈0.39–0.46 in V1/LM/RL/AL/PM/AM (all
  p≪1e-30; V1 p=2.5e-118), LGN weaker 0.27 — a general mouse visual-cortex property, complementing the
  cross-species result. Matched I.5 ≈ I.5q throughout (proxy verdict holds at scale).
- **(b) Tuning-dim privilege = orientation-domain.** OSI (0.44) ≈ DSI (0.42) ≈ f1_f0 (0.32) couple;
  pref_sf (0.05) / pref_tf (−0.04) NULL; run_mod (0.14) weak. Orientation/direction selectivity couple
  to the universality class; spatial/temporal-frequency tuning does not. OSI not uniquely privileged.
- **(c) Family VII monkey-STRONG / mouse-WEAK** (refines "mouse-absent"). |I.5q−I.5|↔OSI ρ=0.08–0.18
  per area (significant at scale), vs pvc-11 ρ≈0.47. Candidate explanations now 4: species, state,
  recording-tech, **sampling-geometry** (Allen ~1 mm sparse multi-probe all-layers vs pvc-11 Utah ~4 mm
  dense 2D L2/3 — quantified via CCF; lateral-extent + density + layer-coverage, not crude 1D-vs-2D).
- **(d) Cross-area = tight visual-cortex cluster.** Per-area median I.5q 0.42–0.47 / W1δ 0.95–1.03;
  areas cluster as "visual cortex," LGN marginally more GUE-like — a gentle thalamus offset, not a split.
- **(e) Within-cell stimulus-state is a live axis.** A fixed cell's I.5q shifts with stimulus (spread
  median 0.169, p90 0.30): natural movies/spontaneous most GUE-far, flashes most GUE-near. Family II's
  Σ² is even more state-dependent (spontaneous 286 → flashes 12). A new state axis beyond area/tuning.
- **(f) Spatial structure.** Depth (probe_vertical proxy; no ecephys layer label): only a WEAK gradient
  (ρ≈−0.06…−0.09, superficial marginally GUE-ish). Spatial decorrelation: ρ(CCF-dist, |ΔI.5q|)≈0
  everywhere — NO spatial autocorrelation within ~1 mm; the fingerprint is per-cell, not spatially clustered.
- **(g) Family II partially-distinct axis.** Δ₃ carries an OSI signal (ρ=0.24, phase-coupling hook
  partial-yes); Family II ρ(I.5q)≈0.5–0.58 (not redundant); K(τ=1) nearly independent (0.13).
- **(h) Avalanche criticality — orthogonal level.** Mouse V1 populations consistently near-critical
  (τ≈1.9, α≈2.2, crackling≈1.2 vs predicted 1.32, |Δ|≈0.1, all 12 sessions; matches the Beggs-Plenz /
  crackling literature) BUT criticality does NOT track the per-cell fingerprint (ρ≈0, n=12, underpowered).
  ⇒ population avalanche-criticality and per-cell universality-class are ORTHOGONAL — population-collective
  structure is a distinct substrate from per-cell spacing class (not recovered by per-cell Family II).

**Method note:** classify is compute-bound — worker-knee = 14 (probed), NOT the bandwidth-bound "10"
default (workload-specific; see [[worker_count_bandwidth_bound]]). Spatial axes (depth/decorrelation/
population-level) and Tier-2 Buzsaki / Tier-3 IBL are future arcs. Figures: figures/P_allen_depth.png.

**Adjudication (Will, 2026-05-24).**
- **(a)** H1 is now a property of **orientation-tuned mouse visual neurons regardless of pathway
  position** — not "a V1 property." LGN weaker (0.27) fits an upstream relay with less-elaborated
  orientation tuning. The cleanest generalization of the cross-species finding; a strong empirical anchor.
- **(c)** Reframe: the question is **not "present vs absent" but "what makes Family VII 4–5× stronger
  in pvc-11."** Disambiguating the 4 candidates (species / state / tech / sampling-geometry) needs
  **orthogonal-design data** — awake-monkey-V1-Utah or anesthetized-mouse-V1-Neuropixels (both exist;
  queue as a future Tier acquisition IF Family VII becomes load-bearing).
- **(f)** Coherent picture with (d): **visual cortex is roughly homogeneous at the fingerprint level,
  with cell-by-cell variation that is NOT spatially organized below mm scales.** Three reads to keep
  open: cell-intrinsic firing character dominates local-network effects / local cell-type heterogeneity
  gives all-scale diversity / the property is an individual-cell spike-train statistic, not a "which
  neighbours" property.
- **(h)** The load-bearing framing: **population avalanche-criticality and per-cell universality class
  are TWO DIFFERENT OBSERVABLES of the same system — both real, both measurable, neither implies the
  other.** The avalanche literature sees something true the per-cell instrument doesn't (criticality);
  the per-cell instrument sees things the avalanche literature doesn't (H1, tuning-privilege, stimulus-
  state). This connects the program to the Beggs-Plenz criticality tradition **without subsuming or
  being subsumed by it** — more precise than "confirmed" or "refuted" criticality.
- **(e)** Methodology: **long-range Family II (Σ²) carries more state information than short-range
  Family I (I.5q)** — if state-trajectory characterization becomes a focus, Σ² is the more sensitive axis.

**Follow-ups (2026-05-24, post-adjudication):**
- **Calibration anchors** (calibration_anchors.py): GUE/GOE/GSE/Poisson/clock/uniform-jitter banked as
  explicit landscape corners + instrument re-validation (GUE→q≈1, Poisson→q≈0, clock→W1δ≈0). The clean
  comparison baseline. coordinates/calibration-anchors.jsonl.
- **Population-level fingerprints** (population_fingerprint.py; §7(h) follow-up): population fingerprints
  **FRAGMENT by aggregation** — corr-eig (correlation-matrix bulk eigenvalues, principled spectral) → GUE;
  sync-event (threshold) → Poisson; avl-onset → intermediate; rate-peak (find_peaks) → §7.ter.19 artifact
  (control). No single "population fingerprint" — the aggregate picks the class; population-level is a
  FAMILY of mutually-disagreeing observables (sharpens §7(h)). coordinates/population-fingerprint.jsonl.
- **Landscape v1 consolidation** (landscape.md §0 dashboard): mapped / pending / surprises at a glance.

**REGISTERED-OPEN (2026-08-16, from holonomy pilot ADD-5, priority-ranked by Will above the
protocol work): RIGID_GUE gate margin hardening.** The long-range discriminator's renewal-band
margin to the RIGID_GUE boundary is ~1.1σ of the band at (L=20, deg-6 lens, n=1200): renewal
min Σ²(20)=2.71 vs boundary 1.056 with band sd ~1.5 (holonomy/op1_materiality.json, computed
through this module's own ensembles). That is thin *in the gate's own units*, independent of
transition-order effects, and the gate carries class claims (RIGID_GUE certifications, Thread-E
promotables). **Proposed trigger (adopt or amend at the next seal that touches this gate):
before any NEW RIGID_GUE verdict is banked, re-derive the renewal-band margin at that verdict's
own (n, L, lens) configuration and require margin ≥ 3× band-sd; below that, the verdict HOLDS
pending either a config change that shrinks the band (more windows / matched-L adjustment) or
an explicit margin-accepting ruling.** Already-banked RIGID_GUE rows are not retroactively
reopened by this entry; the existing validate_rate_unfold guard covers the lens-bandwidth
failure mode but not this absolute-margin one. Owner: the next arc that consumes or produces a
RIGID_GUE verdict.

**DISCHARGED 2026-08-16 — see `rigidgate/RESULTS_RIGIDGATE.md`** (sealed characterization arc,
`rigidgate/verify_rigidgate.py` on the green board). Headline: the boundary is *calibrated*, not
fitted (bands match the Mehta and renewal asymptotes to 0.2–10.6%); the ADD-5 thinness figure was
a small-sample artifact of the holonomy arc's own materiality run (corrected: 3.6σ, false-RIGID
0.000 at n=1200) **but is re-vindicated at n=343 — the configuration the banked approximability
rows use — where the false-RIGID rate is 3.5%.** The bigger finding is not a margin at all: the
rule is one-sided by design, so **a perfect clock (a banked zoo calibrator) earns RIGID_GUE at
z=−5.09**. Proposed minimal fix (not applied here): split the branch into RIGID_GUE (|z|≤2.5) and
**HYPER_RIGID** (z<−2.5) — same boundary formula, same multiplier, zero specificity cost, moves
neither banked row. Two growth-based fixes were measured and rejected, one of them because it
flags ζ for a physically real reason (Berry saturation at ln(T/2π)=5.99 vs the matched-L default
of 40). Owner's decisions still open: adopt the split; scope class claims to L ≲ ln(T/2π); record
that single-L Σ² is not adversary-proof (a marginal-exact permutation construction sits inside the
band with GUE NNS).

**REGISTERED-OPEN (2026-08-16, from the RIGID_GUE arc, Will's review round): single-L Σ² is
defeatable by an adversary who knows the gate.** A marginal-**exact** construction — a permutation
of an iid Wigner spacing draw, so its NNS is identical by multiset identity — tuned to f\* ≈ 0.056
sits **inside** the GUE band. No rule built on Σ² at one L can exclude it. Census run
(`rigidgate/SINGLE_L_CENSUS.md`): **6 gate call sites, all single-L, none sweeps L; multi-L sites
zero**; Δ₃ is computed at every site and discarded as secondary, so the gate is single-L *and*
effectively single-statistic. Highest exposure is `longrange_audit.py:36`, which uses a **fixed
AUDIT_L = 50.0 across heterogeneous arithmetic substrates** — the banked ζ row was judged at 8.3×
its own Berry saturation scale (ln(T/2π)=5.99; measured z=−2.33 at that configuration). Scope
statement: the spoof is adversarial, no natural substrate does it, and nothing here shows a banked
row wrong — what is established is that every RIGID_GUE row certifies **rigidity at one scale, not
class**. Hardening in priority order: (1) substrate-aware L cap, (2) conjoin Δ₃, (3) a second L,
(4) record the adversarial bound in the module docstring. Owner: next arc touching the gate.

**REGISTERED-OPEN (2026-08-16): Δ₃ growth arm is PROMOTABLE, not rejected** (RIGID_GUE seal
RG-ADD-7). The arc first filed it under rejected designs because it flags the banked ζ row at
z=−9.5. That is a mismatch between the **gate's L policy** and the **substrate's validity window**,
not a defect in Δ₃: the arm rejects every spoof at ~12:1 power (GUE increment 0.1053 ± 0.0086) and
fails only on a substrate judged 8.3× past its own saturation scale. **A Δ₃ variant with a
substrate-aware L cap may dominate the deployed gate on both axes** — rejecting hyper-rigid spoofs
while keeping genuine low-height arithmetic rows. The measured power numbers carry over as its
starting calibration. Pairs naturally with hardening step (1) above.

---

## ⇧ CONSOLIDATION (2026-08-16, Will's ruling): the three items above are ONE defect

The single-L census, the Δ₃ "rejection", and the ζ class-level misreading are **three faces of one
problem: a fixed L policy colliding with substrate-specific physics.**

- `AUDIT_L = 50.0` applied to every arithmetic substrate, against ζ's Berry saturation scale of
  **ln(T/2π) = 5.99** — an 8.3× mismatch.
- The Δ₃ growth arm was filed as rejected *because* it flagged ζ — but it flagged a substrate being
  judged 8.3× past its own validity window. The arm was right; the L was wrong.
- The ζ row read as "class level" *because* a one-sided rule at an out-of-window L cannot say
  anything sharper — the label absorbed a scale error.

**One fix addresses all three: a substrate-aware L cap.** Cap each substrate's judging L at its own
GUE-validity scale (for ζ-like substrates, L ≲ ln(T/2π)); inside that window the Δ₃ growth arm
becomes deployable rather than ζ-flagging, and the class-vs-rigidity vocabulary question becomes
answerable rather than absorbed. **Will's ruling: this is the highest-value item on the queue,
above the full-sequence holonomy arc.** Brief drafted at `LCAP_BRIEF.md`, ready for a go.

**⇧ DISCHARGED 2026-08-16 — `lcap/RESULTS_LCAP.md`** (sealed arc, `lcap/verify_lcap.py` on the
green board). Two caps, both derived without reference to ζ: **validity** (Berry ln(T/2π)=5.99 for
ζ; finite-n departure from Mehta for RMT spectra — note n=343 caps at L=8.0, so the gate's *own
reference ensemble* goes out of window at small n) and **discrimination** (zoo-derived: across
L=3→50 the GUE band's spread grows ~5.7× while the GUE–GOE gap grows only ~1.4×, so **GOE read
`RIGID_GUE` at the deployed L=50** — the zoo gate caught this before ζ was touched). Policy:
`L_judge = min(deployed_L, validity_L, discrimination_L)`, `discrimination_L = 40`. Zoo gate passes
6/6 known-class members under it. **ζ at its own validity scale reads HYPER_RIGID at z = −9.10**
(vs −2.33 at L=50): the large-L policy was diluting a 9σ effect, and the "excess is an artifact of
judging past validity" hypothesis is ruled out — the effect grows when the artifact is removed and
is 3.6× the resolution floor. Verdict **L_POLICY_FIXED** — the cap fixes the physics *and* improves
discrimination at no meaningful power cost. Still the owning program's calls: adopt the policy;
adopt the HYPER_RIGID split it depends on; what the ζ row should say.

**FLAG (2026-08-16, `lcap/` LC-ADD-1) — banked approximability rows judged outside their own
discrimination window.** brocot/golden (n=343) was judged at L=6.86, where GOE is separated from
the GUE band by only **+2.14σ** against the required 3.0. **What this flag does and does not
impeach, itemised:** the *measurement* (Σ²=0.635, z=+0.49) **stands**; the `RIGID_GUE` label read
as *"not floppier than GUE"* **stands** — that is what the branch certifies and the row satisfies
it; **only the GUE-vs-GOE discrimination at that configuration is unsupported.** The row is not
impeached, one specific inference from it is. Re-judging inside the window needs the substrate
point set, which the L-policy arc does not hold — so this is a flag for the owning program, not a
move.

**⇧ ESCALATION (2026-08-16, `lcap/` LC-ADD-2): the exposure is the DEFAULT SCALE POLICY, not five
call sites.** `matched_L(n) = clip(0.02n, 5, 50)` grows linearly in n while the discrimination cap
does not, and the census n-column finds `matched_L` **outside the discrimination window at every n
tested** (343, 700, 1200, 1600, 2000). Any site using `matched_L` judges at a scale where the
nearest confusable known class is not reliably excluded. **Precision caveat, flagged against our
own numbers:** two independent derivations at different seed counts disagree by up to ~2× per entry
(n=1200: 8 vs 20; n=2000: 40 vs 30) — the per-n values are provisional and n=2000 straddles the
boundary; the *ordering* is what is robust. Registered-open: re-derive the cap at seed counts
sufficient to quote it, measuring the estimator's own variance first (the ADD-5 discipline). The
installed `DISCRIMINATION_L_BY_N` table is marked provisional in the module.

**⇧ OPERATIONAL HEADLINE (2026-08-17), stated hard because the soft version invites a fix that
cannot work:** *this gate has essentially never distinguished GUE from GOE at deployed
configurations.* Measured per-realization false-positive rates (the operationally correct estimand):
GOE earns `RIGID_GUE` **32–90% of the time at EVERY L tested at n=343** — so **no admissible
configuration exists at that n**, and it cannot be fixed by choosing L; it needs a different
statistic or more data. n=343 is the configuration the banked approximability rows use. Across the
full (n, L) grid **exactly one admissible cell exists** (n=2000, L=5) against a deployed default of
40 — wrong by 8× at its best point, with no correct answer at two of three n. Full derivation and
the both-directions error table: `lcap/RESULTS_LCAP.md`.

**Δ₃ VARIANT — INTERIM (2026-08-18, `rigidgate/delta3_short_lever.py`, run in progress).** The
opening obligation from RG-ADD-9 is measured at n=343 and n=1200, and it settles the question in an
unexpected direction. **The lever was not the problem:** SNR on the short lever L∈[2,6] is
**higher**, not lower, than on the long lever (n=343: 10.8 vs 4.2; n=1200: pending/9.6 long) —
the increment's spread shrinks faster than the increment itself, so the promotion's worry about a
3× lever was misplaced. **But the arm fails for a different and fatal reason: GOE has a
false-positive rate of 1.00 on BOTH levers at every n measured so far.** A Δ₃ *growth* test cannot
separate GUE from GOE because **both are RMT classes and both grow logarithmically** — growth is
exactly the feature they share. The arm rejects hyper-rigid spoofs (clock 0.00, antithetic 0.00 on
the long lever) and is blind to the nearest confusable class, which is the specific discrimination
the whole L-policy arc was about. **CONFIRMED at n=2000** (originally 14 draws, targeted at the FP question after the full run was
believed to have timed out on the n=2000 eigensolves — **that attribution was WRONG, corrected
2026-08-19**: the full three-n run completes in **~3 minutes, exit 0**, and the clean 40-draw
numbers below are from it. One eigensolve at n=2000 is 0.27 s and a Δ₃ evaluation is 0.02 s, so the
whole n=2000 row is ~1.4 min of compute. Whatever consumed the 50-minute cap that night, it was not
this arithmetic — most likely BLAS thread oversubscription against the other sessions then running,
i.e. the already-banked bandwidth-bound lesson firing again unrecognised. **No hardware was ever the
constraint here**): GUE increment 0.1043±0.0112 long / 0.0552±0.0023 short — SNR **23.6** on the
short lever (40 draws, full run), the highest of any configuration — and **FP(GOE) = 1.00 on both
levers at every n.**

**FINAL: the Δ₃ growth arm is NOT a candidate instrument.** Not for the reason RG-ADD-9 feared. The
lever worry was wrong twice over — short-lever SNR is *higher* at every n (10.8 / 20.1 / 24.0 against
4.2 / 9.6 / 9.3 long) — but the arm admits GOE **100% of the time at every n and both levers**,
because a *growth* test cannot separate GUE from GOE when logarithmic growth is exactly what the two
classes **share**. It rejects hyper-rigid spoofs and is blind to the nearest confusable class, which
is precisely the discrimination the L-policy arc exists to protect.

**Consequence for brocot, now settled: n=343 needs MORE DATA, not a different statistic** — the
outcome RG-ADD-9 named as emptying the queue slot. The remaining route is raising n into the range
where an admissible L exists (the only admissible cell measured anywhere is n=2000 / L=5), which for
the approximability rows means more partials, not a re-analysis.

**BROCOT n-SCOPING — MEASURED (2026-08-19).** The cost question is now well-posed and answered by
running the generator rather than estimating.

*The bar:* n ≥ 2000. The only admissible cell measured anywhere is n=2000/L=5, and the grid tested
{343, 1200, 2000} — **n=1200 has no admissible cell either**, so the requirement is not softly
satisfied somewhere in between. Deployed rows are n=343, i.e. **5.8× short**.

*Is it reachable?* **Yes, but only on one knob, and it is the wrong knob.** Sweeping the three
candidates on `predict_partials([1, φ⁻¹], [d, d])`:

| knob | deployed → best | reaches 2000? |
|---|---|---|
| amplitude threshold (−50 → −120 dB) | 343 → 439 | **no** — saturates at 1.28× |
| audio band `f_max` (20 kHz → 1 MHz) | 343 → 343 | **no** — not binding at any depth |
| bin resolution (0.5 → 0.05 Hz) | 343 → 343 | **no** — partials are not colliding |
| **FM index** (8 → 24 / 32 / 48) | 343 → 1857 / 2994 / 4845 | **yes** |

So the only route to the bar is raising the FM modulation index to ≳24. Two things make that a
different proposition from "collect more data":

1. **n is non-monotone in index** — depth 40 gives **1531**, *below* depth 32's 2994 — and the fold
   is not an artifact of any of the three obvious caps: it survives −120 dB (1662), a 1 MHz band,
   and 0.05 Hz bins. It is the Bessel sideband arithmetic itself. The count also saturates near
   ~5167 by index 48. **There is no "turn it up until it's enough" dial.**
2. **The index IS this program's independent variable.** FM depth is the coupling analogue here
   (higher depth → sharper mode-locking); the banked rows measure Brody q against approximability
   *at* depth [8,8]. Re-measuring at [32,32] does not extend those rows — **it replaces the
   substrate**, on the very axis the finding is about.

**Terminal state, sharpened: the banked n=343 approximability rows are not rescuable.** Not by a
different statistic (Δ₃ settled that), not by re-analysis, and not by more partials at their own
operating point — because the only knob that reaches the admissibility bar is the one that changes
what is being measured. What remains available is a **new arc at high FM index**, which would be a
fresh measurement of the same question on a differently-coupled instrument, and worth costing on its
own merits rather than as a repair. The existing rows keep their standing label: the measurement and
the "not floppier than GUE" reading stand; only GUE-vs-GOE discrimination at that configuration is
unsupported.

## BROCOT RESOLVED (2026-08-19) — the claim was mis-indexed, not underpowered

Ran the exact-question check before buying the high-index arc. It changed the answer, and the arc
turned out not to be needed.

**Stage 1 — the class-indexed claim fails.** The banked headline is ρ(rank, Brody q) = **−0.91**
across 9 Lagrange classes. Reproduced exactly (−0.909), then given the two things it never had:

- *An error bar.* A Lagrange class contains infinitely many α; the banked run used **one
  representative per class**. Twelve representatives per class — generated *exactly*, since
  prepending CF terms preserves the tail and hence the class by construction — give **within-class
  RMS sd 0.192 against between-class sd 0.217, a ratio of 0.88.**
- *An honest x-axis.* ρ is taken against `np.arange(9)`, annotated "already ~approximability-
  ordered". But **six of the nine classes have identical μ = 2.0**; their listed order comes from max
  CF quotient, a finer and different notion. The deployed axis splices two orderings and imposes a
  strict order on six tied points.

Swapping the single representative for the class mean: ρ **−0.909 → −0.717**, 95% CI
**[−0.862, −0.033]**. Against μ: **[−0.900, 0.000]**. Against max CF quotient: **[−0.818, +0.044]**.
**Both include zero.** The banked representatives are systematic outliers for their own classes at
the approximable end — ln2 banked 0.515 vs class mean 0.905 ± 0.107 (**3.6 sd**), e−2 0.568 vs
0.933 ± 0.153 — and that is what manufactured the slope. *The famous constants are not typical
members of their classes*, the same trap as the banked "anchor a.e. Khinchin, not π" lesson.

**Stage 2 — the phenomenon is real; the class was the wrong index.** The sideband lattice is
k₁ + k₂α with |k| bounded by the FM index, so it can only resolve near-resonance at **small
denominators** — set by the *first* CF terms, which is exactly what prepending changes. Stage 1's
"noise" is the quantity the instrument responds to. Measuring approximability **per α** at the
matched scale, D_Q(α) = min_{q≤Q} q‖qα‖ with **Q = 2·depth** (matched, not assumed), over **n = 255**
α spanning all nine classes plus 40 generic:

| x-axis | ρ(x, q) | 95% CI |
|---|---|---|
| **D_Q** (small = resonant) | **+0.699** | [+0.612, +0.768] |
| max CF term, first 8 | −0.599 | [−0.683, −0.511] |

Both in the predicted direction, both clear of zero, at **28× the n** of the class-level test. The
prediction committed before the run (|ρ| > 0.5, CI clear of zero) is **met**.

**Confound audit — SURVIVES_BOTH.** *(a) Partial count:* near-resonance collides sidebands, so n
could drive q. Measured — n ∈ [276, 345], ρ(D, n) = −0.067 and ρ(n, q) = −0.055, both CIs spanning
zero, and the **partial correlation controlling for n is +0.678 [+0.590, +0.750]**, essentially
unmoved. *(b) Brody rail:* **39.6% of q sit at the bound 1.000**, so the rank correlation could be an
artifact of which side of the rail things fall on. Through the unbounded estimator (range −0.585 to
+2.378) it is **+0.658 [+0.560, +0.742]** — the rail was compressing real variation and the result
does not depend on it.

**VERDICT: brocot's finding is corroborated in refined form and its scale problem dissolves.** "q
tracks approximability" holds as a **per-α** statement at the instrument's own resolution; it does
**not** hold indexed by Lagrange class, which is an asymptotic label the instrument cannot see. The
earlier statement that the trigger is *boundedness of partial quotients* survives as the first-8-term
version (ρ = −0.599), not the asymptotic one.

**Kept visible because it is the cost of the error, not a footnote: the high-FM-index arc sat on the
queue as NECESSARY for two rounds** — first as "brocot needs more partials, not a different
statistic", then as a scoped costing exercise ("what n clears the bar, is that reachable") that ran to
a measured answer about FM index, Bessel folding and band limits. All of it was downstream of a
correlation that was mis-indexed rather than underpowered. The costing was competent work on a
question that should never have been asked, and the check that would have pre-empted it costs
nothing: *does the index live at the same scale as the instrument?* Filed in TOOLKIT §9.

**Consequence for the queue: the high-FM-index arc is NOT NEEDED for this question.** n ≥ 2000 came
from the GUE-vs-GOE gate, which class-assigns a single row; the actual claim is correlational and is
now measured at **n = 343 per α with n = 255 α** and tighter CIs than the original ever had. No
bigger n, no GPU, no new substrate. The high-index arc remains available as a genuine
*generalization* test (does the relation survive a 4× change in coupling?) — now a real question
rather than a repair, and costed on its own merits.

### Queue after the brocot resolution (2026-08-19)

1. **Gate enumeration for one-sided calibration — interactive, next session.** The highest-value open
   item. One-sided calibration is a confirmed class with **two** instances, and both syntactic
   detectors failed their known-positive self-test, so **the number of instances is unknown rather
   than two**. Judgment-heavy is exactly where a manual pass earns its cost; the population is small
   and named (verdict lattices, tier assignments, decoy floors, fitter tolerances) and the question
   per gate is one sentence — *which side was calibrated, and was the other ever measured?*
2. **The 19 small-n boundary rows in other programs' artifacts.** Mechanical, two treatments already
   defined. These live in others' artifacts, so the deliverable is **report-and-propose, not repair**.
3. **Comb k-tuple arc — last, and cheap to start.** Its brief already frames the right question:
   whether the k-tuple prediction is **separable from the pairwise product**. If it is not, the arc
   is one cell and closes early — a good property for the back of a queue.

*Not on the queue:* the high-FM-index arc (optional generalization test, see above) and the P1
straddle form (needs 3–4 more degrees at 200 seeds, under an hour, not urgent — the mechanism carries
ADD-7 without it).

## ⚠ CORRECTION TO THE C2 BRIEF CELL (filed 2026-08-20)

**The next-session brief's C2 cell quotes the PROBE: "140 cells, 100% negative, median −0.412,
uniformly clustered." Those numbers are correct and their population is superseded.** The probe
covered `_spontaneous` recordings from **3 of 15**; the full file gives **99.4%, median −0.373, range
to +0.098**. Correct numbers, wrong slot — filed against the brief itself so the next session does not
quote **−0.412** as the finding. The full-file numbers below are the finding. *(The change is a strict
improvement: the 7 exceptions are exactly the cells where bounded and repaired agree, which
strengthens the repair's validity rather than weakening the result.)*

## C2 COMPLETE (2026-08-19) — pvc-11 repaired, and a recovered substrate signal

**Instrument half.** All **1,159** pvc-11 records now carry `I.8_brody_q_unbounded` alongside an
**untouched** `I.8_brody_q`, matching the five-substrate layout. Run took 22 s, 0 skipped. The write
went through a direct estimator call, **not** `phase2b_recompute._matched_axes`, which nulls the
bounded key when the fitter gate fails — policy-correct behaviour that would still have destroyed the
banked record this finding rests on. Gated by the acceptance verifier **sealed before the write**
(baseline pinned by hash): 1,159 records, 1,159 bounded keys present, all bit-identical, 1,152 at the
rail constant, 0 nulls. Re-checked independently after the write rather than assumed.

**Science half — this is a recovered signal, not hygiene.** Across all 1,159 cells and all conditions:

| | value |
|---|---|
| railed at either bound | **0.0%** |
| range | **−0.634 … +0.098** |
| median | **−0.373** |
| negative (clustered) | **99.4%** |
| headroom to the −1.0 bound | **0.366** |

**pvc-11 (macaque V1) is clustered in 99.4% of cells, median Brody q ≈ −0.37**, and the bounded
coordinate reported **1,152 of them as the identical positive constant `6.610696135189609e-05`** —
wrong sign, wrong magnitude, zero variance. The headroom number is recorded so the wider-bound
question is not reopened: the most extreme cell sits **0.366 away** from the (−1.0) bound.

**Scope correction the probe forced, and it changed the number.** The 140-cell probe covered only
`_spontaneous` recordings from 3 of 15, and reported *100% negative, median −0.412*. The full file
gives **99.4% and −0.373** — the probe was not representative, exactly as the population join
predicted, and its numbers are **not** the finding.

**Independent internal validation.** The **7** cells whose repaired q is non-negative are **exactly**
the 7 whose bounded fit was interior rather than railed (7/7), with the two estimators agreeing
closely where both are informative (0.101↔0.098, 0.088↔0.094, 0.034↔0.031). So the repair reproduces
the bounded estimator wherever the bounded one was actually measuring, and diverges only where it was
pinned to its floor.

### Implications of the rail arc for the BROCOT program (2026-08-20)

The bounded-Brody rail affects brocot, **at the opposite end from every neuro substrate**, and it
lands on exactly the classes the program is about.

**1. brocot rails UP, not down.** Per-α study (n=255): **5.9%** at q=0, **39.6% at q=1 — with exactly
ONE distinct value**, a true rail by the pileup criterion. The neuro substrates rail at 0 (clustered
data with nowhere to go); brocot rails at 1 (**rigid** data with nowhere to go). Beyond q=1 lie GUE
(≈2) and GSE (≈4), which are physically ordinary — so this is a **CONVENTION** bound, same class as
the q<0 case, mirrored.

**2. The headline finding SURVIVES.** ρ(D_Q, q) = **+0.699 bounded, +0.658 unbounded**. The per-α
approximability relation is not an artifact of the rail, and the confound audit had already checked
this. **No banked brocot conclusion is overturned.**

**3. The rail is directionally HONEST here, which makes it much milder than the neuro case.** Of the
101 railed cells, **zero** have a true q below 1 — everything pinned at 1 genuinely is ≥1. Contrast
pvc-11, where clustered cells were reported as *marginally more Poisson than Poisson* — **wrong sign**.
brocot's rail **compresses**; it does not invert.

**4. But it compresses precisely where the program's subject lives.** The upper rail is owned by
golden (21), silver (18), bronze (15), metallic5 (8) — the **badly-approximable** classes — plus
e_minus_2 (17) and ln2 (9). Unbounded, those cells span **+1.015 … +2.378** (median +1.122; 6.9% are
GUE-like at 1.5–2.5; none beyond 2.5). **The bounded estimator reports that entire span as a single
number.** Per-class medians inside the rail: golden **+1.316**, e_minus_2 +1.175, bronze +1.105,
silver +1.101, ln2 +1.055, metallic4 +1.055, metallic5 +1.053.

**5. Whether the compressed region carries SIGNAL is unresolved, and the obvious test is confounded.**
Inside the rail, ρ(D_Q, unbounded q) = **−0.209, CI [−0.400, −0.002], p = 0.036** — nominally
significant, opposite in sign to the global relation, and **not trustworthy as it stands**: the subset
is defined *by the bounded value railing*, i.e. selected on q itself, so range restriction can induce
a correlation. A CI whose upper bound is −0.002 is a `PLAUSIBLE`, not a `CONFIRMED`. **Do not bank the
sign reversal.** The properly-powered version is a designed test, not a subgroup correlation.

**Recommended, cheap, not urgent:** re-run the brocot per-α analysis with `I8_brody_q_unbounded` as
the **primary** axis (it is validated and already banked alongside). The finding does not need
rescuing — this buys **resolution at the rigid end**, where 40% of measurements are currently a single
point, and where golden-vs-metallic ordering is currently unmeasurable by construction.
