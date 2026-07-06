# Track 4 — Continuous Front-End Feasibility · Configuration Justification

**Authored before execution** (brief non-negotiable). Phase 36. Date 2026-05-31.
Gated on Track 0 PASS. **Calibrator-only — NO real neural data in this track.**

## Question
Can a *principled* continuous front-end feed the already-VALIDATED core (IDS-unfold, ratio spectra)
without smuggling in an uncontrolled knob — tested by making it reproduce the **banked AM
point-process verdict** before it ever touches real data? PASS → the continuous arm is a real
missing piece (§7.ter.19 was a front-end limitation, not a core one). FAIL → §7.ter.19 reaffirmed
with *positive* evidence (we name the knob that broke it). **Both outcomes are wins.**

## Ground truth (owned)
Analytic Almost-Mathieu operator `(Hψ)_n = ψ_{n+1}+ψ_{n−1} + 2λcos(2π(θn+φ))ψ_n`, golden θ
(`am_eigs`, `am_diag` in phase35a/unfold_rotnum.py). Metal-insulator transition at **λ=1**:
- λ<1 metal — absolutely continuous spectrum, extended states, transport.
- λ>1 insulator — pure point spectrum, exponentially localized states, no transport.

**Banked point-process verdict to recover** (Track 0 reproduced it): NO quadrant flip across the
transition (NFP), and the transition lives **sub-quadrant** as W1δ: sub-critical W1δ→floor (≈5×10⁻³),
super-critical W1δ large (≈0.28), separable at N≳5×10⁴. The promotion test is whether a continuous
front-end recovers THIS (transition location at λ=1, NFP in the metallic regime, sensitivity floor
no worse than the point-process path).

## Two front-ends (each relocates the knob differently)

### F2 — spectral-measure → IDS-unfold  (CONSERVATIVE; inherits banked validation)
**Honest framing (Finding 2):** the validated leg ALREADY is `am_eigs → rotation-number IDS →
unfolded W1δ`. F2 only inserts a continuous **density-of-states estimator** in front of the unfold
instead of using exact sorted eigenvalues: estimate the spectral density (Gaussian KDE on the
eigenvalues at bandwidth h), then unfold the smoothed cumulative-DOS and read W1δ. So F2 is expected
to pass nearly by construction; the real content is whether a *smoothed/estimated* DOS front-end
still recovers the verdict, and how robust that is to the estimator bandwidth.
- **Knob:** KDE bandwidth h (relocated from "reference N" to "estimator bandwidth").
- **Knob-robustness sweep:** h ∈ {0.25, 0.5, 1.0, 2.0} × Silverman — verdict must be stable.

### F1 — Hilbert instantaneous-phase → rotation-number stream  (THE REAL NEW TEST)
Native to mode-locking / torus dynamics; genuinely new front-end. Bridge from the *spectral* object
to a *continuous-time signal*: the **wavepacket return amplitude**
  φ(t) = ⟨e₀| e^{−iHt} |e₀⟩ = ∫ e^{−iEt} dμ₀(E),
the Fourier transform of the local spectral measure μ₀ at site 0. This is the standard
spectral-measure→signal map, and its behaviour IS the transport signature of the transition:
- metal (AC spectrum): φ(t) **decays** (return probability →0), broadband instantaneous phase.
- insulator (pure point): φ(t) is **recurrent / quasi-periodic** (no decay), mode-locked phase.
Computed exactly from the eigendecomposition: φ(t) = Σ_k |⟨e₀|v_k⟩|² e^{−iE_k t} (a continuous
function of t we sample on a fine grid — a true continuous front-end, not a point process).
- **Front-end pipeline:** Re φ(t) → band-pass filter → Hilbert analytic signal → instantaneous
  phase → unwrap → phase-increment (rotation-number) stream → unit-mean renormalised → NNS / the core.
- **Knob:** the band-pass filter band (relocated from "reference N" to "filter band").
- **INHERITED phase-knob confound (must factor out):** φ(t) is computed at a phase α (= the operator
  phase φ — the SAME degree of freedom that is φ-noisy at N=2584, per item 3 / the α-ensemble). So
  F1 has TWO knobs, and a filter-band "instability" could secretly be an unlucky α rather than a
  front-end failure. Therefore the robustness gate **sweeps filter-band and α INDEPENDENTLY**, not
  jointly: (i) pin α in the high-N-stable regime (N≳5×10⁴, where the α-ensemble spread has collapsed
  — Track 0 item 4) for the **headline verdict**; (ii) sweep α separately at fixed band to **bound
  the phase confound**; (iii) sweep band at fixed (stable) α to test the actual front-end knob. An
  instability is attributed to the front-end ONLY if it survives at high-N-stable α — otherwise it is
  charged to the substrate's known phase-noise, not to F1.
- **Knob-robustness sweep:** band ∈ a pre-declared set of center/width pairs spanning the spectral
  support (at pinned stable α) — verdict must be stable. Separately: α-sweep at fixed band must show
  the band-verdict is not α-contingent. Instability that survives the high-N α = uncontrolled knob =
  F1 fails the discipline test (independent of whether it hit λ=1 once).

## Promotion criterion (pre-registered, both front-ends)
A front-end is PROMOTED only if it recovers ALL of:
1. **Transition location** — a clear metallic↔insulating separation bracketing λ=1.
2. **No-false-positive in the metallic (extended) regime** — no spurious transition flagged where
   the spectrum is AC.
3. **Sensitivity floor no worse** than the point-process path (the separation is achievable at a
   sample budget ≤ the banked path's, order-of-magnitude).
AND (4) **knob-robustness** — the verdict is stable across the pre-declared knob sweep, with the
   F1 phase-confound factored out (headline at high-N-stable α; band-instability charged to F1 only
   if it survives that α).

## Outcomes (bank either)
- **PASS** → continuous front-end is a real missing piece; promote the F-passing front-end to a
  *narrow* continuous arm; only THEN consider continuous substrates + re-derive a continuous
  analogue of the §7.ter.19 boundary. (Does NOT run real data in this track.)
- **FAIL** → §7.ter.19 reaffirmed with positive evidence; document WHICH knob broke it (filter band
  for F1, estimator bandwidth for F2). A stronger statement of the gate than the current one.

## Configuration specifics (justified, not convenience)
- AM cell N for F1/F2: N=2584 (F_18, banked) for the eigendecomposition; metallic λ=0.5 vs
  insulating λ=1.5 (the banked sub/sup pair), plus a finer λ-bracket {0.5,0.85,0.95,1.05,1.25,1.5}
  for the transition-location read. λ=1 excluded as a measured substrate (banked convention).
- φ(t) sampling: grid dt and horizon T chosen so the Nyquist band covers the spectral support
  [−(2+2λ), (2+2λ)] and T resolves the slowest recurrence — declared in-run, sensitivity-checked.
- Core/instrument config matched to Track 0 (NNS canonical_spacings, 2–98% trim, unit-mean).
- Engine attribution recorded (NNS vs RF) for each front-end's recovered signal.
