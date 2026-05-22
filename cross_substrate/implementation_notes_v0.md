# Implementation Notes — Cross-Substrate Coordinate Module (v0)

Methodological observations from building `axes.py` / `harvest.py` and the
Phase 2a harvest. Refinements to `viewpoints.md` are **proposed here, not made**
(Will's edit, not Claude Code's — instructions §5).

---

## Code map

- `cross_substrate/axes.py` — pure axis functions, Families I/II/III/VI.
  Reuses (matched, already-debugged): `phase35a/unfold_rotnum.spacings` (the
  2–98%-trim canonical spacing extractor, identical across substrates),
  `universality.py` (reference CDFs + Σ²/K(τ)/R₂), the corrected
  `phase34e/run_berry_robnik.fit_rho`. New code: Δ₃, Brody fitter, W1-to-ref
  CDF integrals, matched-L.
- `cross_substrate/validate_fitters.py` + `fitter_validation.json` — synthetic
  gate (Poisson→0, GOE→1). **all_pass=True** (Brody q: 0.007/0.99; BR ρ:
  0.07/1.00). Fitted axes bank only behind this gate (§7.ter.57).
- `cross_substrate/harvest.py` — Phase 2a harvester; per-source adapters →
  `coordinates/{substrate}.jsonl`.

## Matched-instrument decisions

1. **`I.5q` vs `I.5` (instrument split).** pvc-11/Allen/Kuramoto/arithmetic
   banked `ks_gue_med` is the Farey-q-banded `joint_q_profile` statistic. AM's
   W1δ is plain unfolded-NNS via `unfold_rotnum`. These are different objects.
   Banked as `I.5q_ks_gue_med` (distinct label); the matched plain-NNS `I.5_ks_gue`
   (object (a)) is computed only in Phase 2b. Carry both, annotate validity
   (per the standing stance). **Proposed viewpoints.md refinement:** add `I.5q`
   as a first-class catalogued axis distinct from `I.5`.

2. **`ARS.rep_med` is an un-catalogued axis.** Every ARS-classify substrate
   banks `rep_med` (repulsion-integral median over q-bands), not in viewpoints
   §2. Carried as `ARS.rep_med`. **Proposed:** add to a new "ARS-native" family
   or to Family I.

3. **Pulsar is direct-leg, not q-banded.** `phase33a` used ARS-classify direct
   mode on raw TOAs. Tagged in `extraction_method`; not instrument-matched to the
   q-banded substrates. Cross-domain bounded.

4. **Matched-L for Σ²/Δ₃ (II.1/II.2).** Chose `matched_L = clip(n_events·0.02,
   5, 50)` — window as a fixed fraction of event count, for cross-substrate
   comparability. **Flagged for Will (instructions §8.4):** the fraction (2%) and
   clip bounds are a defensible default, not derived; revisit when comparing
   substrates with very different event counts.

5. **III.4 scalar reduction = sum over {2,3,5,7}.** III.2 vector always banked
   alongside, so the reduction is reversible (instructions §8.3).

6. **III.1 p-concentration choice.** Defined as RF amplitude at mode q=p (peak),
   not sum over multiples of p. **Flagged** — alternative (sum over q∈{p,2p,…})
   is defensible; revisit.

## Provenance

- `data/` is gitignored, so `source_commit` is null by design; recorded
  `source_artifact` (path) + `source_mtime` instead. If durable provenance is
  wanted, the result artifacts would need committing or hashing.

## Gotchas / fixes

- **NumPy 2.x removed `np.trapz`** (→ `np.trapezoid`), same family as the earlier
  `np.ptp` removal. Fixed in `_w1_cdf`. Standing hazard for any ported code.
- Underpowered cells (n_well=0 / NaN ks) banked as `I.5q=None` + `_I.5q_na_reason`,
  never a sentinel number (instructions §4).

## Cost (Phase 2b probe, 2026-05-21)

pvc-11 object-(a) Family I+II recompute: **~291 ms/cell** (Family II Σ²/Δ₃
dominates at ~247 ms). Projected: all 1159 pvc-11 cells ≈ **5.6 min**. For
scale: Allen ≈ 3.5 min, Kuramoto-oscillators ≈ 31 min. No idle-gating/batching
needed for the non-AM substrates; only AM Phase 1 eigensolves are the expensive
tier.
