# Night-2 Brief — C1 θ-class extension (silver + Liouville)

**Status:** plan ready; re-probe + smoke before compute-go. **Date:** 2026-05-22.
**Companion:** Night-1 brief §4 (this is its scoped optional extension); `landscape.md`, `viewpoints.md`.

## §1 — Frame
AM Phase 1 placed the golden-θ cells in the landscape. The Phase-35 fingerprint found
θ-class sensitivity is side-specific (sub θ-sensitive ~3.55× across classes; sup
θ-universal within ~30%). This run extends AM along the θ-axis on the **matched
object-(a) leg** to test that contrast directly, with the highest-information pair:
**silver (Diophantine) vs Liouville (non-Diophantine, predicted structurally different).**

## §2 — Cells (2)
N=70k, **sup** (λ=1.5), L=2.56×10⁷, 16 φ ∈ [0,0.5) (matched to golden sup_N70k).

| name | θ-class | θ value | rationale |
|---|---|---|---|
| sup_N70k_silver | silver | √2 − 1 ≈ 0.41421356 | Diophantine alternative (rev-5.2 C1 chain) |
| sup_N70k_liouville | Liouville | Σ_{k≥1} 10^{−k!} ≈ 0.110001000… | non-Diophantine; predicted structurally different — the high-info cell |

Matched to golden sup_N70k (already banked) → 3-way θ comparison at fixed (N, λ, L).

## §3 — Pipeline / compute
- Same `am_reextract.py` (Stage A eigensolve+bank → Stage B unfold @ L → per-φ aggregate),
  with **per-cell θ** threaded through `am_eigs` + `unfold_rotnum` (both already accept θ).
- **Workers = 10** (throughput-optimal, banked default).
- **PRE-LAUNCH (mandatory, the N=125k lesson):** re-probe one φ-task at 10w for these
  cells, project the 2-cell wall-clock, confirm it fits the overnight window; add a
  wall-clock halt. Full-coverage smoke before launch.
- Eigenvalues + event-trains → `coordinates/am_work/` (permanent on disk, gitignored).

## §4 — Coordinates
Family I (I.1–I.9) + II (II.1/II.2/II.3) per cell, per-φ aggregation (NOT position-concat —
the superposition bug). VI.1 α from this run if L-sweep available (else N/A). Append to
`coordinates/am.jsonl`; update `landscape.md` AM row note + `findings_log.md`.

## §5 — Acceptance / verdict
- Bank what we get. **Flag, don't interpret:** does Liouville's fingerprint differ
  structurally from silver/golden (W1δ, Brody q, ks_gue)? Is the sup side θ-universal
  within ~30% on the matched leg (testing the Phase-35 sub-θ-sensitive / sup-θ-universal
  finding)? Report the 3-way (golden/silver/Liouville) sup_N70k comparison.

## §6 — Out of scope
- bronze + Salem θ-classes (defer to a follow-up; resumable if added).
- slate-4 (N=125k sup @ L-converged, N=200k) — multi-day, separate brief.
- Sub-side θ-classes (the Phase-35 θ-sensitive side) — a natural follow-up, but this
  run is sup-only to match the golden sup_N70k baseline first.
- Alternate unfolding leg; new operators.

## §7 — Reporting
Per-cell elapsed (at 10w) + banking confirmations; the 3-way θ comparison; non-degeneracy
(frac-zero) + any divergence flagged; cost vs the re-probe projection.
