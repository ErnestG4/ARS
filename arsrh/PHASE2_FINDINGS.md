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
theorem-bracketed control parameter, the portable number the phase was for. **Verification status:**
reviewed against reported numbers, not independently audited; as good as the committed deterministic
scripts being faithful to the ⟨r̃⟩/flow path.

**Scope honesty:** this is the Calogero–Moser realization (exact zero dynamics), not a direct H_t(z)
integral computation (Polymath15-scale, not attempted). Finite-window truncation is a real systematic
(mitigated by interior analysis). The seal's prediction of a resolvable forward rigidification was
correct in direction (and, per the session's pattern, my instinct again under-predicted how cleanly:
66× the floor).
