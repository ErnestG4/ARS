# Track 4 — Continuous Front-End Feasibility · Findings

**Phase 36, 2026-05-31.** Calibrator-only, falsification-gated. Config:
`TRACK4_CONFIG_JUSTIFICATION.md`. Ground truth: analytic Almost-Mathieu operator (golden θ, N=2584),
metal (λ<1, AC/transport) vs insulator (λ>1, pure-point/localized), transition at λ=1.
Driver: `phase36/track4_frontend.py`; raw: `track4_frontend_results.json`.

## Headline
**Neither F1 nor F2 is PROMOTABLE to a validated continuous arm — but for different, informative
reasons, and the continuous front-end demonstrably CARRIES the transition that event-extraction
(Track 1.1 Chialvo) lost.** §7.ter.19 reaffirmed with *positive, mechanism-named* evidence; the
result maps exactly what a continuous arm would need.

## The φ(t) bridge is sound (pre-check)
Wavepacket return amplitude φ(t)=⟨e₀|e^{−iHt}|e₀⟩ shows the textbook transport signature:
|φ| late/early ratio = 0.080 (λ=0.5 metal, decays) → 0.438 (λ=0.95) → 0.990 (λ=1.5 insulator,
recurs). Monotone metal→critical→insulator. So the continuous front-end's raw signal carries the
metal-insulator distinction directly.

## F1 — Hilbert instantaneous-phase → rotation-number stream  →  `CARRIES-TRANSITION / α-CONFOUND-UNRESOLVABLE`
Pipeline: φ(t) → Re → band-pass → Hilbert → unwrapped phase → 2π-crossing intervals → unit-mean → NNS.
- **Transition location (pinned α=0, default band 0.05–0.30 Hz, T=2000):** W1δ MONOTONE across λ —
  0.097 (λ0.5) → 0.034 (0.85) → 0.013 (0.95) → 0.004 (1.05) → 0.001 (1.25) → 0.001 (λ1.5). Metal
  phase-crossings are structured; insulator phase advance is clock-regular (W1δ→floor). A clean,
  monotone, transition-bracketing signal — exactly what event-extraction could NOT produce on the
  related Chialvo torus-breakdown.
- **Band knob-robustness (pinned α=0):** 4 bands, separation insul−metal = −0.096, −0.091, −0.091,
  −0.033 — all same sign (metal > insul). Band-robust. ✓
- **α CONFOUND sweep (the decisive catch):** separation is NOT α-robust at N=2584 —
  α=0.00: −0.096, α=0.13: **+0.002**, α=0.27: **−0.003**, α=0.41: −0.112. At α∈{0.13,0.27} the metal
  W1δ collapses to floor and the separation vanishes. This is the inherited phase-knob confound
  (α = the operator phase φ, the SAME d.o.f. that is φ-noisy at N=2584 — the α-ensemble that made
  the 35b sub-quadrant branch UNRESOLVED).
- **Why it can't be factored out (the load-bearing blocker):** the protocol says pin α in the
  high-N-stable regime (N≳5×10⁴, where the α-spread collapses) for the headline. **But F1 needs the
  return amplitude φ(t), which needs eigenVECTORS (weights |v_k[0]|²) — O(N²) memory (~20 GB at
  N=5×10⁴).** So F1 is structurally capped at moderate N (a few thousand), exactly where α-noise is
  present. Unlike the eigenvalue-only spacing leg, F1 cannot escape the substrate's phase-noise by
  going to high N. The α-instability is *consistent with* the substrate's known phase-noise, but F1
  cannot reach the regime that would confirm it ⇒ promotion BLOCKED by an unresolvable confound
  (not refuted; not promotable).
- **Resolution path (queued):** compute the site-0 spectral weights |v_k[0]|² as Gauss-quadrature
  weights via an O(N) Lanczos / continued-fraction method (not the full O(N²) eigenvector matrix),
  which would let φ(t) — and hence the α-sweep — reach N≳5×10⁴ and cleanly attribute the α-instability.

## F2 — spectral-measure (KDE-DOS) → IDS-unfold  →  `SEPARATES_ROBUST_BUT_NO_FLOOR`
Estimate DOS by Gaussian KDE on the eigenvalues; unfold eigenvalues through the smoothed cumulative
DOS; read W1δ. Knob: KDE bandwidth h.
- **Separation:** insul−metal W1δ = +0.337, +0.365, +0.369, +0.344 across h ∈ {0.25,0.5,1,2}×Silverman
  — robustly positive (insulator more structured), knob-robust. ✓
- **But NO floor:** metal W1δ = 0.48 / 0.60 / 0.76 / 1.00 (rising with h) — nowhere near the banked
  rotation-number floor (≈0.005). The smoothed density does NOT capture the fine IDS, so unfolding
  leaves O(0.5) residual fluctuation even in the AC/metal regime.
- **Conclusion:** a smoothed-spectral-density continuous front-end SEPARATES the regimes robustly in
  the correct direction, but does NOT inherit the banked validation — the metal→floor is load-bearing
  on the **exact rotation-number IDS**, not on "a spectral measure." F2's inheritance is partial
  (direction yes, floor no). NOT promoted (strict criterion requires floor recovery).

## What this buys the program (both outcomes are wins)
1. **§7.ter.19 reaffirmed with positive evidence**, and the knob that breaks each front-end is named:
   F2 — the estimator smoothing loses the floor; F1 — the eigenvector-O(N²) wall prevents factoring
   out the α phase-confound.
2. **The continuous arm is the right TOOL for this transition class, but not in turnkey form.** F1 at
   pinned α gives the monotone λ-signal that event-extraction (Chialvo) could not — corroborating the
   Track-1.1 convergence (transition lives in continuous modulation). The continuous arm needs (a) the
   *exact* IDS, not a smoothed density (F2 lesson), and (b) an O(N) spectral-weight method to escape the
   α-confound at high N (F1 lesson). Both are concrete, queued engineering steps — not open-ended.
3. **No promotion to real continuous data** (the gate did not pass) — §7.ter.19 holds; Track-3-style
   continuous substrates remain out until a front-end passes the gate.

Status tags: F1 `CARRIES_TRANSITION_α-CONFOUND-UNRESOLVABLE_AT_REACHABLE_N`;
F2 `SEPARATES_ROBUST_BUT_NO_FLOOR`. [[sweep_inherited_knob_independently]],
[[gate_certifies_half_say_so]], cross-refs Track 1.1 convergence.

---

## Follow-up — O(N) Lanczos local measure RESOLVES the F1 blocker (definitively, not by punt)

`phase36/lanczos_local_measure.py`. The F1 blocker was "α-confound unresolvable because φ(t) needs
eigenVECTORS (O(N²) wall) so we can't reach high N." Lanczos-from-|e₀⟩ on the AM tridiagonal gives the
Jacobi matrix whose eigendecomposition yields the Gauss nodes/weights = local spectral measure dμ₀ at
**O(m·N), no N×N eigenvectors** (φ(t)=Σ_k w_k e^{−iθ_k t}).

**Calibrator gate (run first, [[synthetic_validate_fitters]] discipline) — PASSED.** At N=1200 (exact
diag banked), full Lanczos reproduces exact φ(t) bit-exact (maxΔφ=0.00e+00 metal; ~2e-16 insul) and the
F1 W1δ EXACTLY incl. the insulator FLOOR (0.00135→0.00135). The ghost-eigenvalue risk that could forge a
false floor did NOT materialize. Convergence ladder at N=8000: a **sub-N** moment count m=1500 (0.19·N)
already reproduces exact metal 0.09742 AND insul floor 0.00135 — φ(t) on horizon T needs only ~T-driven
moments, independent of N. `none`-reorth (the O(N)-memory config used at high N) reproduces both exactly
at N=8000 (guard passed). So the machinery earned its place against the known answer before high-N use.

**High-N α-resolution at N=50000, m=2000 (the regime the eigenvector wall had blocked) — DECISIVE.**
α-sweep separations (insul−metal W1δ): α=0.00 → −0.0961, α=0.13 → +0.0023, α=0.27 → −0.0033,
α=0.41 → −0.1123. Mixed-sign, spread 0.115 — **α-confound PERSISTS at high N**, and the values are
**bit-identical to N=2584**. 

**Interpretation (sharper than the original finding):** φ(t) on a fixed horizon depends on the local
spectral measure, which CONVERGES in N (already by N≈2584) ⇒ the F1 readout is N-invariant ⇒ the
α-dependence does NOT shrink with N. It is therefore **INTRINSIC to the wavepacket-phase observable, not
finite-N substrate phase-noise.** This cleanly distinguishes it from the spacing leg's α-ensemble noise
(which IS finite-N and collapses by N≳5×10⁴, per 35b) — the earlier "F1 inherits the same N=2584
phase-noise" framing was WRONG. F1's metal-insulator contrast is genuinely phase-contingent in the
thermodynamic limit (clean separation at α∈{0,0.41}, collapses at α∈{0.13,0.27}). So F1 is
**DEFINITIVELY NOT promotable** — answered, not punted: reaching high N (via the validated O(N) measure)
showed the confound is real, not a compute artifact. Updated tag:
`α-CONFOUND_INTRINSIC_N-CONVERGED_NOT_PROMOTABLE`.

**Still queued (well-specified):** F2's missing floor — the Lanczos LOCAL measure (site-0 projection)
is not the global DOS/IDS; recovering the floor for F2 needs a KPM global-DOS estimator (Chebyshev
moments + stochastic trace, floor from moment convergence not KDE bandwidth). F1's resolution does not
supply it. This is the remaining concrete engineering step, not open-ended.

**Methodological gem banked:** the two legs respond to α DIFFERENTLY — the eigenvalue-spacing leg's
α-scatter is finite-N (collapses with N), the φ(t)-phase leg's α-dependence is thermodynamic-limit
intrinsic (N-invariant). "Go to higher N to escape phase-noise" is valid for the first, useless for the
second — and only the high-N test (enabled by the O(N) Lanczos measure) could tell them apart.

---

## WHY F1's death does NOT transfer to F2 — the local-vs-global split (ergodicity pressure-test)

The correction that earns this section: Lanczos-from-|e₀⟩ gives the LOCAL measure dμ₀ — right for F1,
useless for F2 (a single starting vector can't give a trace). F2 needs the GLOBAL DOS/IDS, its own
estimator. But the split is not bookkeeping — it is the REASON F1's death does not transfer:
- **F1's observable is dμ₀, the local spectral measure, which DEPENDS on α** ⇒ its α-contingency is real
  and fatal (confirmed: intrinsic, N-invariant).
- **F2's observable is the IDS, which by the ergodic theorem is a.s. INDEPENDENT of α (self-averaging).**
  F2 reads a phase-invariant object BY CONSTRUCTION. The confound that killed F1 is a property of
  LOCALITY, not of the continuous arm. F2 is structurally immune.

**Pressure-test (exact diag, N=2584, same operator / same α-set as F1):** IDS-unfold W1δ across
α∈{0,0.13,0.27,0.41}:
- **metal (λ=0.5): [0.005, 0.006, 0.004, 0.006], spread 0.0022** — α-STABLE at the floor, where F1's
  local φ(t) metal swung [0.097,0.001,0.010,0.147] (spread 0.146). The load-bearing structure (the floor)
  is α-invariant already at N=2584. ✓ claim confirmed.
- insul (λ=1.5): [0.277,0.390,0.828,0.301], spread 0.55 — still α-scattered at N=2584, BUT this is the
  FINITE-N scatter that collapses by N≳5×10⁴ (banked sensitivity floor) — categorically unlike F1's
  N-invariant intrinsic α-dependence.

⇒ the IDS self-averages: FAST in the metal (extended states; α-invariant by N=2584), SLOWLY in the
insulator (localized states; finite-N scatter collapsing with N) — always collapsing, never intrinsic.
**F2 reads a phase-invariant object in the limit; it is the right tool, not a consolation prize.**

This turns F2's queued KPM step into something with a BUILT-IN CORRECTNESS CHECK: recover the floor via
Chebyshev moments + stochastic trace + Jackson kernel (Gibbs-ringing damping), gated like Lanczos
(moment-convergence ladder vs the banked N=1200 floor before any high-N run) — AND the recovered floor
must come out α-INDEPENDENT. If it does, the IDS is behaving as the ergodic theorem requires and the
separation is clean for the right reason; if it comes out α-dependent, the estimator is broken (the IDS
CANNOT be), caught before trust. F2's floor is recovered AGAINST A THEOREM. [[two_legs_respond_to_alpha_differently]].

---

## F2 RESOLVED — the floor is spectral RIGIDITY, not density (KPM build, `phase36/kpm_dos.py`)

Built the principled DOS estimator: Chebyshev moments via STOCHASTIC TRACE (O(M·R·N) matvecs, no
diagonalization) + Jackson kernel (Gibbs damping); unfold eigenvalues through the KPM-IDS. Gated at
N=1200 vs the banked exact floor, with the alpha-invariance free check.

**Result — the alpha-invariance check PASSED, the floor did NOT recover, and the two together ARE the answer:**
- **Moment-convergence ladder (metal):** M=256->4096 gives W1d 1.10->1.15 — does NOT converge down to the
  banked floor (~0.005); rails high, slightly WORSENS with M. (KDE-DOS railed at 0.48-1.0; KPM rails
  higher — neither recovers it.)
- **alpha-invariance (M=2048):** metal W1d across alpha = [1.146,1.140,1.140,1.137], spread **0.0088** — the
  KPM floor IS alpha-invariant. The estimator reads the IDS as the ergodic theorem requires; FAITHFUL, not broken.
- **Separation:** metal 1.146 vs insul 1.419 (sep 0.273) — separates, right direction.

**Why the floor can't be recovered cheaply (the structural reason):** the metal->floor is spectral
RIGIDITY — the AC-metal levels are near-uniformly spaced (clock-like), so unfolding them to W1d->0.005
needs the IDS accurate to << the mean spacing (~ bandwidth/N ~ 0.005). KPM's Jackson-damped resolution is
a/M ~ 0.0015 at M=4096 — COMPARABLE to the spacing, not << it. Resolving the floor needs M>>N moments,
which costs more than diagonalization. So **no moment/kernel DOS estimator recovers the floor at
sub-diagonalization cost: the floor is exact-level-POSITION information (the rotation-number/Sturm IDS
supplies it exactly, O(N^2)), NOT density information.** KDE smooths it away, KPM moment-truncates it away
— same root cause.

**The alpha-invariance check did exactly its job:** it confirmed the estimator is faithful (alpha-invariant
=> not broken), so the missing floor is a RESOLUTION LIMIT, not an ergodicity failure. The gate drew the
distinction it was designed to draw.

### Track 4 — both front-ends now mechanism-resolved (CLOSED)
- **F1 (local phi(t)) — NOT promotable:** intrinsic alpha-dependence (a property of LOCALITY; dmu_0 is
  phase-dependent), persists to the thermodynamic limit (Lanczos high-N test).
- **F2 (global DOS) — separates robustly AND alpha-invariantly (ergodic, CONFIRMED), but cannot recover the
  floor by any cheap DOS estimator:** the floor is exact spectral-rigidity (level positions), below
  moment/kernel resolution without M>>N.
- **NET:** the continuous arm CARRIES the transition (robust, phase-invariant SEPARATION via F2) but NOT
  the floor's fine RIGIDITY (exact-level information). That is the precise boundary of what a continuous
  front-end buys for this operator class. §7.ter.19 reaffirmed with positive, fully-mechanism-resolved
  evidence on BOTH fronts. No real continuous data run. Tags: F1 `alpha-CONFOUND_INTRINSIC_NOT_PROMOTABLE`,
  F2 `ERGODIC-SEPARATES_FLOOR-IS-RIGIDITY-NOT-DENSITY`.
