# PRIOR_LOOK — derivflow/modes (disclosure ledger for Night 1)

Source: BRIEF.md §2, written by Claude (chat) on 2026-09-17 from a chat sandbox:
float64, uncertified sandbox solvers, tiny ensembles. Nothing here is certified
and nothing here is imported. Any Night-1 cell that overlaps a number below is
graded DECLARED-WITH-PRIOR-LOOK, never SEALED.

The hash of this file is recorded in `seal_night1.json`.

## Linearization
- One derivative step multiplies a small displacement wave by 1 − qw/π.
- Matched to 6 digits on a periodic 1024-root trigonometric lattice, A = 1e-4,
  qw from 0.006 to 3.14.

## Circle (periodic, M = 1024, no unfolding needed)
- iid (3 seeds): omr 0.0354 at k=10, 0.0093 at k=24, 0.0035 at k=48.
  First k with omr < 1e-2 is 23. Slope over k 16–48 is −1.46.
- COE (1 seed): first k = 12, slope −1.98.
- CUE (1 seed): first k = 9, slope −1.81.
- Linear evolution of each seed's own gaps:
  - COE/CUE: within 2–8% from k=1, within 1% after k≈10.
  - iid: ~11% off at k=10 started from the seed; ~2% started from the k=10 state.

## Line (n = 1024, IID_UNIFORM, central half, 2 seeds, sandbox solver)
- NOUNFOLD crossing ≈ 27 (interpolated between k=24 and k=32), slope −1.48.
- Running-mean references:
  - ±25 gaps: slope −1.64.
  - ±5 gaps: crossing ≈ 17, slope −2.80.
  - ±1 gap: crossing ≈ 9.6, slope −3.49.

## F3 used for comparison
- tau_kww = 1.734, beta_kww = 0.788, amplitude set so the curve crosses 1e-2 at
  k = 10.83.

## Circle Σ²(L; k)/L at k=48
- Measured: 0.109 at L=10, 0.185 at L=20, 0.322 at L=50.
- Linear theory: 0.101, 0.194, 0.396; implies L_half ≈ 1.6·k.

## Sandbox script
- If Will adds `derivflow_modes.py`, it goes in `derivflow/modes/prior_look/`
  with a README marking it uncertified. Never import it. (Not present as of
  2026-09-17 01:20 PDT.)
