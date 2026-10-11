# Stage 2 G-s, U(N) step — results (G_S_DESIGN.md §5.1, §6; 2026-10-10)

Both U(N) known answers PASS. The assembly and the declared split reproduce the sine kernel's v(b) on the whole
ladder, and the assembly with its taper geometry reproduces an exact CUE_N Monte Carlo.

## (i) Sine kernel: v(b) computed directly vs through the split, and vs the measured long-GUE baseline
`gs_unitary.py`, `results/gs_unitary/gs_unitary.json`.
- **Direct:** the full determinant over all r. The integrand is band-limited to |ω| ≤ 4π, so a trapezoid with
  Δr = 0.2 is exact.
- **Split:** the full function × χ for r < 20, plus the non-oscillating pieces of the CS08 U(N) transcription in its
  sine limit × (1 − χ). In that limit the pieces re-sum to the determinant to 4e-15.

| b | v direct | split − direct | measured GUE (16 × 10⁶, `ph2s2/results/tapered`) | z |
|---|---|---|---|---|
| 100 | 0.119956 | −4.1e-8 | 0.1206 ± 0.0007 | +0.9 |
| 300 | 0.113720 | −4.1e-8 | 0.1122 ± 0.0012 | −1.3 |
| 1000 | 0.111536 | −4.4e-8 | 0.1126 ± 0.0022 | +0.5 |
| 3000 | 0.110912 | −1.8e-8 | 0.1178 ± 0.0040 | +1.7 |
| 10⁴ | 0.110694 | −8.3e-8 | 0.1212 ± 0.0076 | +1.4 |

- **The split is safe for U(N).** The ℓ-oscillating long-range part it drops changes v(b) by less than 1e-7, so the
  §3 claim holds here.
- **The flat-baseline expectation in §5.1(i) was wrong in detail.** v(b) falls as v∞ + κ/b, because the connected
  two-pair function has a −1/r² tail. **The predicted GUE g = √(v(10⁴)/v(100)) is 0.961, not 1.** Measured g is
  1.003 ± ~0.03 (1.3 SE). The ladder z-scores are correlated, since every rung comes from the same sequences.
- **Consequence for Stage 2:** any comparison against the GUE baseline uses the predicted g_GUE = 0.961, not 1.

## (ii) CUE_400 Monte Carlo of the tapered variance vs the assembly with the CUE_N kernel
`gs_cue_mc.py`, `results/gs_cue_mc/gs_cue_mc_N400.json`. 10⁵ Haar matrices, 4 centres each; pass if |z| ≤ 3 at every
b and every red path has |z| > 3.

| b | V (MC) | V (prediction) | z | red z: 3-pt × 2 | no 4-pt | overlap width as W | descriptive: sine kernel |
|---|---|---|---|---|---|---|---|
| 10 | 2.02704 ± 0.00462 | 2.03137 | −0.94 | +954 | −3345 | −95 | −1.07 |
| 20 | 3.13988 ± 0.00715 | 3.14200 | −0.30 | +1243 | −4470 | −59 | −0.64 |
| 40 | 5.35041 ± 0.01215 | 5.34876 | +0.14 | +1464 | −5340 | −33 | −0.68 |

**PASS.**
- **The MC can fire.** Its subtlest red path, an overlap (W⋆W) of the wrong width, sits 33–95 SE away.
- **The finite-N kernel is not resolved.** At N = 400 the sine kernel in place of K_N moves V by about 0.2% at b = 40,
  under 1 SE.
