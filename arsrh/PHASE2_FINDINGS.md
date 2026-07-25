# ARS-RH Phase 2 — de Bruijn–Newman heat-flow threshold localization (the portable resolution)

Prereg: `arsrh/PHASE2_PREREG_SEALED.json`. **§0 ANTI-CLAIM BINDING and load-bearing here:** a measured
transition location is an **instrument property, NOT the de Bruijn–Newman constant Λ**, and nothing
here bears on RH. The deliverable is the classifier's threshold-localization **RESOLUTION** in units of
the dBN parameter t — portable to every other substrate. Artifacts: `phase2_dbn_flow.py`,
`phase2_dbn_flow_measured.json`, `phase2_gue_control_measured.json`.

## Method — exact Calogero–Moser realization of the dBN flow

H_t(x) = ∫ e^{t u²} Φ(u) cos(xu) du satisfies the **backward heat equation** ∂_t H_t = −H_t″ (∂_t
pulls down u², ∂_xx pulls down −u²). Differentiating the zero condition H_t(x_j(t))=0 gives the exact
zero flow, with **t the actual dBN parameter** (so the [0, 0.22] theorem bracket — Rodgers–Tao Λ≥0,
Polymath15 Λ≤0.22 — is in these units):

```
    dx_j/dt = 2 Σ_{k≠j} 1/(x_j − x_k)
```

Repulsive: forward t rigidifies (spacings → uniform), backward t collides (realness boundary). Evolved
the actual Riemann zeros (first 4000, γ~2500) by RK4, analyzing the interior 50% (edge zeros feel the
truncated neighbour sum). r̃ is a purely local statistic invariant to density (Phase 1 density check),
so it reads the fluctuation structure, not the flow-induced density change.

## Forward — the rigidity crossover is massively resolvable within [0, 0.22]

⟨r̃⟩(t) rises monotonically from the GUE-like start toward the crystalline (picket-fence) limit 1:

| t | 0 | 0.02 | 0.05 | 0.11 | 0.22 | 0.40 | 0.80 |
|---|---|---|---|---|---|---|---|
| ⟨r̃⟩ | 0.617 | 0.672 | 0.735 | 0.824 | 0.913 | 0.970 | — |
| dev/floor | 3 | 15 | 30 | 50 | **70** | 82 | — |

The rise over the bracket [0, 0.22] is +0.30 — **66× the finite-window jitter floor** (≈0.0045 at the
interior W). The crossover is not close: it is the dominant feature.

**⚠ File this as an INSTRUMENT result, not a ζ result (reviewer).** The GUE-flow control below rigidifies
*identically* — which excludes the density confound AND proves this +0.30 forward rise carries **almost no
ζ-specific information**: it is the flow's universal action on any GUE-class spectrum, present in the control
*by construction*. "66× the floor" is the classifier tracking a **known universal crossover** with high
resolution — a strong statement about the instrument, not about ζ. The ζ-specific content is only the
**residual** between ζ and the control (next section), which is sub-percent and single-witness. Do not let
the headline number read as a strong ζ finding.

## The classifier's RESOLUTION — the portable number

Resolution = (jitter floor) / (slope d⟨r̃⟩/dt). At t=0 the slope is ~2.76, floor ~0.0045, so

> **classifier t-resolution ≈ 0.0016 in the dBN parameter** — about **0.7% of the 0.22 theorem
> bracket** — at this window (γ~2500, gap~1.05).

**Height-dependent, honestly:** the flow speed is dx/dt = 2/gap, so higher-γ windows (smaller gaps,
higher density) rigidify *faster* in t and give a finer t-resolution; the ~0.0016 is the value at
γ~2500. The resolution scales with the local gap. This is the reusable output: on a substrate where
the control parameter drives a rigidity crossover, the ARS ⟨r̃⟩ classifier localizes the crossover to
~(jitter floor)/(local slope) — the number to carry to fungal etc.

## The reviewer's Phase-2 prerequisite — settled by a control

The concern: the flow moves local density as t varies; if r̃ read density drift, it would report
density change as a threshold approach (the solar failure, at Phase 2's core). Two things settle it:
(1) Phase 1's **matched-density null** showed r̃ is invariant to a smooth density gradient (GUE on the
ζ density backbone stays at 0.600). (2) A **GUE-flow control** (`phase2_gue_control_measured.json`):
evolve a *matched-density GUE* spectrum (same density backbone as the ζ window, pure GUE fluctuations)
under the identical CM flow and compare ⟨r̃⟩(t):

| t | 0 | 0.02 | 0.05 | 0.11 | 0.22 |
|---|---|---|---|---|---|
| ζ-flow | 0.617 | 0.672 | 0.735 | 0.824 | 0.913 |
| matched-GUE-flow | 0.605 | 0.664 | 0.730 | 0.820 | 0.911 |

**ζ and GUE rigidify identically** (slopes 2.76 vs 2.98, ratio 0.92; converge to 0.913 vs 0.911 by
t=0.22). The rigidification is **universal (GUE-class), set by the gap-scale — not ζ-specific and not
density drift.** r̃ reads the real rigidity. Prerequisite settled.

## The ζ-vs-control RESIDUAL — the only ζ-specific part, characterized against control jitter (reviewer)

The control's identity cuts both ways: it excludes density drift *and* strips ζ-content out of the +0.30
headline. The genuinely ζ-specific quantity is the **residual** between ζ-flow and the matched-density
GUE-flow. To know whether that residual exceeds the control's own realization-to-realization jitter or is
noise, I ran **12 independent GUE-flow realizations** (`phase2_residual_measured.json`, N=2000, interior
1000) and measured (ζ − control_mean)/control_sd at each t:

| t | ζ-flow | control mean | control sd | (ζ−ctrl)/sd | absolute gap |
|---|---|---|---|---|---|
| 0.000 | 0.6172 | 0.5986 | 0.0091 | **+2.04** | +0.0186 |
| 0.050 | 0.7181 | 0.7081 | 0.0067 | +1.51 | +0.0100 |
| 0.110 | 0.7989 | 0.7914 | 0.0048 | +1.57 | +0.0075 |
| 0.220 | 0.8887 | 0.8828 | 0.0026 | +2.23 | +0.0059 |

Reading, filed precisely:
- **The residual is real at ~2σ and does not wash out under the flow.** The *absolute* gap decays
  (0.019 → 0.006) but the control jitter decays proportionally (0.009 → 0.003), so in σ-units it holds at
  ~+1.5–2.2σ across the whole bracket. This is the Phase-1 finite-height offset (ζ starts +0.0186 above the
  control mean) being **carried** by the flow, not new ζ-structure the flow generates.
- **It is ONE witness, not four — and it is the SAME witness as Phase 1, not a second one.** The four rows
  are the *same* ζ spectrum flowed to four times (fully correlated), and the **t=0 row is literally the
  Phase-1 measurement before any flow** (+2.04σ here vs 2.4σ in Phase 1 — *same effect, two window
  definitions*; the gap between 2.04 and 2.4 is the "walks if the window moves" caution made concrete, and
  it is two readings of one witness, not two witnesses). So Phase 1's crossover and Phase 2's residual are
  **one leg under two headings** — the finite-height offset seen once at rest (Phase 1) and once carried by
  the flow (Phase 2) — NOT two independent one-witness claims. Filing them as two overstates the support.
- **⚠ The σ-column has SHAPE, and that is the open question.** (ζ−ctrl)/σ across t = +2.04, +1.51, +1.57,
  **+2.23** — it dips in the middle and *sharpens* at the crystalline end, not monotone-decay as passive
  carrying would give. Two live readings: **(a)** flat-in-σ, dip is noise (12 realizations → ~20% error on
  σ, so +1.51 and +2.23 may not be resolvably different → "~+1.8σ throughout, carried constant"); or **(b)**
  the t=0.22 sharpening is real — the flow compressing toward the rigid limit acts as a *magnifying glass*
  on the exact non-smooth residual, making the endpoint a genuine second look through a different lens.
  Distinguished by a fresh disjoint-block flow-sweep (`phase2_thetacert_freshblock.json`), gated on the
  θ-certification below.
- **Verdict on the residual: resolved, not robust, ONE witness (shared with Phase 1).** Real above the
  matched-control jitter, sub-percent, single-window, and the *same* finite-height offset Phase 1 measured.
  The clean, robust output of Phase 2 is the **resolution 0.0016**, not the residual.

### The θ-certification — blocking prerequisite for BOTH queued witnesses (reviewer)

The two queued second-witnesses — Σ²/number-variance for Phase 1, and the fresh-block flow-sweep for the
σ-shape here — test different things but **share one dependency**: the θ-expansion order (Riemann–Siegel
θ(t) asymptotic → the smooth-counting used to build the matched-density control and to unfold for Σ²). A
fresh ζ block CAN separate "carried-constant" from "flow-amplified residual" (two blocks share the flow's
universal action but NOT their specific residual or closest-pair structure — the test has power), but it
CANNOT separate either from a **t-dependent θ-truncation error**, which both blocks share. So θ-order
t-stability across the flow must be certified first, or that confound rides underneath both witnesses — the
same shared-provenance seam as the Σ² cross-check. **Certification (`phase2_thetacert_freshblock.json`):**
build the control at leading-order θ (current, +7/8) and next-order θ (+1/(48πt)) from the *same* GUE draws,
flow both, and confirm the paired Δr̃(t) stays ≪ the control jitter at every t — i.e. r̃'s smooth-density
invariance (established at rest) survives the nonlinear flow. Only then does the σ-shape carry meaning. One
certification unlocks Σ² (Phase 1) and the fresh-block sweep (Phase 2), both then mechanistically
independent of the density confound and of each other.

**θ-CERT RESULT — PASSES.** Paired Δr̃(next−lead) = **0.000000 at every t** (|Δr̃|/jitter = 0.000, t=0→0.22).
The next-order term 1/(48πt) ≈ 2e-7 at γ~34000, and because r̃ is smooth-density-invariant, the θ-order (which
only moves the smooth backbone) perturbs r̃ by ≤1e-6 ≪ jitter (0.007→0.001) **even under the nonlinear flow**.
r̃'s smooth-density invariance, established at rest in Phase 1, **survives the CM flow**. The θ-truncation
confound is certified absent — it rides underneath neither witness. Both unlocked.

## Fresh disjoint-block flow-sweep — the σ-shape REPRODUCES; reading (b) confirmed (reviewer)

Ran the identical t-sweep on a **disjoint block at γ≈34000** (`zeros1[40000:42000]`, 14× the original height,
non-overlapping zeros, different closest-pair structure), 12 GUE-flow realizations:

| t | (ζ−ctrl)/σ, γ≈34000 (fresh) | (ζ−ctrl)/σ, γ≈2500 (original) |
|---|---|---|
| 0.000 | +1.26 | +2.04 |
| 0.050 | +0.98 | +1.51 |
| 0.110 | +1.77 | +1.57 |
| 0.220 | **+2.29** | **+2.23** |

**The dip-then-sharpen reproduces, and t=0.22 is the sharpest point on BOTH blocks (+2.29/+2.23) — reading (b),
not the noise dip of (a).** Decisive detail: the *at-rest* offset is much smaller at high γ (+1.26 vs +2.04 — ζ
nearer GUE, as Phase 1's height-decay predicts), yet the flow-end sharpening recovers to the **same ~+2.3σ**.
Passive carrying would scale the endpoint *down* with the smaller t=0 offset; it does not.

**Mechanism, named:** the CM flow is a **variance-reducer**. Under crystalline compression the realization
jitter collapses (σ: 0.007→0.0008) *faster* than the absolute ζ−ctrl gap decays (0.0059→0.0018). ζ carries a
persistent finite-height rigidity excess (its "approach to GUE from above"); the flow preserves that offset in
absolute terms while shrinking the denominator, so σ-significance *rises* toward the rigid end. The flow
**magnifies** the non-smooth residual rather than averaging it away — identically on two independent height
blocks. This is the reviewer's magnifying-glass, made concrete and mechanistic.

**Boundary held:** this is real, reproducible, θ-certified, mechanistic structure — but it is still the
**r̃/finite-height leg** (now at two heights + under flow-magnification), **NOT a second orthogonal witness.**
The genuinely-independent leg is **Σ² number-variance** — still owed. Status upgrade: the residual moved from
"one witness, possibly a noise shape" to "one witness with a confirmed reproducible mechanistic flow-signature"
— materially stronger while Σ² is pending, but not yet corroborated.

**⚠ What "confirmed" does and does NOT mean here (reviewer — the resolved-vs-robust distinction, one level up
in the MECHANISM).** Confirmed is earned because the discriminator was pre-registered and directional: flat
σ-shape or mismatched shape would have killed it; only "reproduces AND amplifies with compression" survived,
and the effect got *relatively stronger from a weaker start* (+2.29 from +1.26 vs +2.23 from +2.04) — which a
passive-carry model cannot produce. So the **sign of the compression-scaling** is confirmed. But **two blocks
is a slope from two points**: "σ-amplification scales with compression strength" is a *functional law*, and
two heights fix a direction, not a curve. The magnifying-glass mechanism makes a *quantitative* prediction —
the σ-amplification should track the (computable) gap-scale/compression ratio between blocks — and that
magnitude-law is **UNTESTED**; a third intermediate-γ block either lands on the curve (mechanism nailed) or
confirms sign but misses magnitude (mechanism incomplete, something else contributing). **File precisely: sign
of the scaling CONFIRMED on two heights; magnitude-law UNTESTED.** "Confirmed" = the effect is real and
mechanistic; it does NOT mean the magnifying-glass *law* is established. Not gated on — the sign-reproduction
already earned confirmed-flow-signature — but do not let the two claims merge.

## Backward — the realness boundary (instrument, NOT Λ)

Evolving backward, the smallest gap collides first (the closest Lehmer-type pair — the near-critical
pairs that drove the Rodgers–Tao Λ≥0 bound). The window's first-collision time is **t* = −0.001**, a
**finite-window instrument boundary** set by the window's minimum gap. **§0: t* near 0 is NOT "Λ≈0"
and NOT support for RH** — it reflects the known fact that Riemann zeros have Lehmer-type close pairs
(as close as GUE allows); the instrument measures where a finite-window CM flow first collides.

## Verdict (in-scope, anti-claim maintained)

The ARS ⟨r̃⟩ classifier **localizes the dBN heat-flow rigidity crossover with a resolution of ~0.0016
in the dBN t** at γ~2500 (finer at higher γ), the rigidification confirmed universal (GUE-class) by a
matched-density GUE-flow control, and the finite-window realness boundary sits at t*≈−0.001. **None of
this estimates Λ or bears on RH** — it is the classifier's threshold-localization resolution on a
theorem-bracketed control parameter, the portable number the phase was for.

**The instrument/ζ split, filed clean:** the strong, robust result is an **instrument** result — the
classifier tracks a known *universal* rigidity crossover to ~0.0016 in t; the +0.30 / 66× headline is
the flow's universal action (present in the control by construction), not ζ. The only **ζ-specific**
content is the ζ-vs-control residual, ~+2σ, single-window, sub-percent — **resolved, not robust**, and
awaiting an independent Σ² second witness before any hardening. **Verification status:** reviewed
against reported numbers, not independently audited; as good as the committed deterministic scripts
being faithful to the ⟨r̃⟩/flow path.

**Scope honesty:** this is the Calogero–Moser realization (exact zero dynamics), not a direct H_t(z)
integral computation (Polymath15-scale, not attempted). Finite-window truncation is a real systematic
(mitigated by interior analysis). The seal's prediction of a resolvable forward rigidification was
correct in direction (and, per the session's pattern, my instinct again under-predicted how cleanly:
66× the floor).
