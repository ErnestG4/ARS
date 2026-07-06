# Phase 37 — Overnight Brief (2026-06-01)

**Frame.** Phase 36 produced two reusable instruments. Phase 37 applies them across the whole substrate
arc (LLM → retina → V1 → IBL → hippocampus CA1/EC/CA3/DG/MEC) + calibrators:
1. **Two-axis taxonomy** (confirmed, [[torus_transition_rigidity_vs_clustering]]): the original ARS read
   the REPULSION axis (ks_gue/w1_clock/Brody). Those are SIGN-BLIND across the Poisson pivot — a
   super-Poisson (clustered) and a sub-Poisson (repulsive) process can sit equidistant. The CLUSTERING
   magnitude (CV, mass<0.3) is the sign-carrier. Past "null/INSENSITIVE/Poisson" verdicts read on the
   repulsion axis only may be AXIS-INCOMPLETE (the Kuramoto flip demonstrated this).
2. **Quantization confound** (corrected mechanism, [[pooled_rhythmic_repulsion_confound]]): pooled+gridded
   observables manufacture spurious rigidity when pooled rate ≈ resolution. (Program-internal target
   `population-temporal` deferred to a later pass; flagged here.)

**Scope chosen with Will:** Set 1 (full two-axis re-audit) + Set 4 (calibrator family map) + Set 3 full
(3a fingerprint re-analysis + 3b fresh Qwen2.5-3B extraction on the 4090). "Don't be compute-shy."

---

## Set 1 — Whole-program two-axis re-audit
**Mechanism.** Added two sign-carrying clustering axes to the shared `cross_substrate/axes.py`
`compute_family_I`: **I.10_cv** (CV of matched unit-mean spacings; Poisson→1, repulsive→<1, clustered→>1)
and **I.11_mass03** (fraction of spacings <0.3; Poisson baseline ≈0.259). Both validated against
calibrators (Poisson CV 1.02/mass 0.27; Gamma(4) sub-Poisson CV 0.49/mass 0.04; Gamma(0.25) super-Poisson
CV 1.98/mass 0.57). Because ALL substrate ports route through `compute_family_I`, **re-running each port
regenerates its coordinate file WITH the clustering axis** — minimal-surface, no per-port rewiring.

**Configuration justification.** (a) τ=0.3 for mass: the established ARS clustering threshold (matches the
quadrant diagnostic + the Phase-33a/Kaneko probes; NOT chosen for convenience). (b) CV on the matched
`canonical_spacings` extractor (2–98% trim + unit-mean) — the SAME extractor the repulsion axes use, so the
two axes are read off one spacing array (no extractor mismatch). (c) MIN_N_NNS gate inherited (cells below
it return None, not a forced value). (d) No q_max touched — Family I is q-flat under unit-mean normalization
(§7.ter.10). Engine = NNS throughout.

**Re-audit logic (reaudit_summary.py).** Per substrate, aggregate the two axes and assign each cell a
two-axis label: REPULSIVE (CV<0.9 & near-GUE), POISSON-PIVOT (CV≈1 & low mass), CLUSTERED (CV>1.1 & high
mass). FLAG a substrate as AXIS-INCOMPLETE if its banked repulsion verdict was null/BL/Poisson-pole but a
material fraction of cells are CLUSTERED (super-Poisson) — i.e. the clustering axis carries signal the
repulsion axis missed. Interface-readout framing on all real-data verdicts. NFP vs sensitivity tracked
separately (a substrate reading clean-Poisson on BOTH axes is a genuine null; only super-Poisson-on-
clustering with repulsion-null is axis-incomplete).

**Substrates (ports re-run, sequential to avoid network contention per [[parallel_curl_corruption]]):**
retina ret1 (local); hippocampus buzsaki CA1 / hc3 EC-CA3-CA1-DG / dual_region MEC / allen_hpf (stream);
V1/cortex allen_v1_burst / allen_depth_fam2; IBL ibl_port (stream); + local calibrators/dynamical/arithmetic
for landscape context. Coordinates backed up to `coordinates_backup_pre_twoaxis.tgz` (reversible).

## Set 3 — LLM numerical-quantization parallel
**Question.** Does numerical quantization (fp16→int8→int4) shift the ARS fingerprint the same way
temporal-grid quantization did (Phase 36)? Preliminary in banked fingerprints: surprisal_threshold
structured mass03 0.294→0.308→0.354 (rises with coarser quant), surprisal_cumulative `best` flips
GOE→Poisson at int4. **3a** re-analyzes the banked 97KB fingerprints with bootstrap (is the shift real?).
**3b** fresh-extracts Qwen2.5-3B across fp16/int8/int4 on the 4090 (more text, surrogate floor) to confirm.
Config: surrogate = rate/length-matched per-condition; same extractors as banked (surprisal_threshold /
_cumulative / residual_norm_peaks); quantization is the only varied knob (structure/text held).

## Set 4 — Falsification-calibrator family map (synthetic)
Extend the confirmed Poisson-pivot calibrator across renewal families (Gamma, Weibull, log-normal,
inverse-Gaussian, hyperexponential) + a single sub→through→super CV sweep at fine pivot resolution +
crossing/recrossing. Map the pivot blind spot fully; confirm the two-axis partition is family-general and
that near-Poisson-throughout transitions stay null on both. Pure synthetic, continuous-time (no grid →
artifact-aware). Failed/surprising families are findings, banked not discarded.

---
## Acceptance
- Set 1: every re-runnable substrate emits I.10_cv + I.11_mass03; reaudit_summary flags axis-incomplete
  substrates with per-substrate two-axis tables. Genuine-null vs axis-incomplete distinguished.
- Set 3: 3a significance verdict on the quant shift; 3b fresh fingerprints across 3 precisions + surrogate.
- Set 4: family-general pivot map; any family breaking the partition is flagged.
## Out of scope (deferred)
- population-temporal pooled-quantization re-read (Set 2) — flagged, next pass.
- Allen-avalanche / Buzsáki-theta-gamma dedicated observable audit (NWB arc).
