# Retrospective Two-Axis Audit · Findings

**Phase 36, 2026-05-31.** Re-examine past banked verdicts through the rigidity-vs-clustering lens
(repulsion axis = rep_int/quadrant, Poisson↔GUE; clustering axis = CV/mass<τ, Poisson↔super-Poisson).
Premise: the repulsion axis is structurally blind to clustering (super-Poisson reads BL, same as
Poisson), so past NULL/negative verdicts on clustering-type processes (sync/collective/bursting) read
only on the repulsion axis may be AXIS-INCOMPLETE. Tonight's Chialvo correction + Kaneko proved the lens.

## Candidate list (ranked by clustering-type-likelihood × data-availability)
1. **Phase 30 Kuramoto — INSENSITIVE** (canonical sync model; repulsion/NNS axis only; data regenerable). TOP.
2. Allen avalanche-criticality ⊥ per-cell ks_gue — ORTHOGONAL (SOC = collective super-Poisson cascades;
   repulsion axis only; coordinates/allen-avalanche.jsonl). HIGH.
3. Buzsáki theta-gamma CFC — BOUNDED-NEGATIVE (collective rhythmic clustering; phase-locking-quality
   only; coordinates/buzsaki-thetagamma-*.jsonl). HIGH (measurement-floor caveat).
4. Phase 31/32 coupled-GLM — FIT-CEILING (mechanism fit, not a substrate axis-miss). LOWER.
- NOT candidates: attractor-topology BOUNDED-NEGATIVE (topological, not clustering).

## Re-check #1 — Phase 30 Kuramoto: AXIS-INCOMPLETE (confirmed, in + out-of-sample)
`phase36/kuramoto_clustering_recheck.py` (parallel, 10 workers). Regenerated the K-sweep (K_factor 0→2,
K_c=2γ), AGGREGATE pooled population spike train, BOTH axes, order parameter R as independent marker.

| K/Kc | R (in) | rep_med | quad | CV | mass<.3 || R (oos N=200) | rep_med | CV |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 0.088 | 0.733 | BR_artifact | 0.72 | 0.00 || 0.062 | 0.80 | 0.52 |
| 1.0 | 0.465 | 0.717 | BR_artifact | 0.97 | 0.00 || 0.165 | 0.80 | 0.54 |
| 2.0 | 0.803 | 0.633 | BR_artifact | 1.57 | 0.20 || 0.741 | 0.75 | 0.98 |

**Adjudication (desync R<0.35 → sync R>0.65):**
- repulsion axis (rep_med): sep **−0.07** in-sample, **−0.05** oos — FLAT; quadrant modal BR_artifact at
  every K. **Reproduces Phase 30's banked INSENSITIVE.**
- clustering axis (CV): sep **+0.67** in-sample, **+0.46** oos — RISES monotonically with R, SAME sign,
  out-of-sample-robust. (mass<.3 also moves, +0.1 in-sample.)

⇒ **Phase 30 "Kuramoto INSENSITIVE" was AXIS-INCOMPLETE.** The canonical synchronization model IS
sensitive — on the clustering axis (CV tracks the order parameter R), where the repulsion axis is flat.
Kuramoto is a clustering-type substrate, exactly as the rigidity-vs-clustering taxonomy predicts and
parallel to Kaneko. Verdict correction: `INSENSITIVE` → `REPULSION-AXIS-INSENSITIVE / CLUSTERING-AXIS-SENSITIVE`.

### Three interpretability corrections (Will's checks — the headline word "repulsion-blind" must be earned)
1. **Repulsion null is INCONCLUSIVE, not blind, for Kuramoto.** `BR_artifact` is NOT the "no-rigidity"
   landing zone: per arithmetic_toolkit.py:744-801, BL = rep_int<0.10 (clean low-rep "no rigidity"),
   whereas BR = rep_int≥0.55 (HIGH) and `BR_artifact` = "nearest-Wigner-form rule fitting a NON-Wigner
   shape — stable but NON-CLEAN KS" = a DECLINED regime. Kuramoto sits in BR_artifact at every K (rep_med
   ~0.73 high), so the repulsion axis is in a non-clean regime — its flatness is INCONCLUSIVE, not a clean
   negative. Honest verdict: Kuramoto = clustering-SENSITIVE / repulsion-**INCONCLUSIVE**. (Contrast
   KANEKO snapshot → rep_med 0.0 / BL = a CLEAN low-rep negative ⇒ "repulsion-BLIND" is earned ONLY for
   Kaneko. The two clustering-type substrates differ on the repulsion side: Kaneko clean-blind (BL),
   Kuramoto inconclusive-declined (BR_artifact).)
2. **N not fixed (in-sample N=100 / oos N=200).** The same-sign clustering separation is robust, but the
   cross-row magnitude compression (CV desync 0.72→0.52, sync 1.57→0.98) is the Palm-Khintchine
   superposition N-effect (more independent components → CV→1), NOT out-of-sample degradation. Magnitude
   is interpretable only with N pinned; only the same-sign verdict survives the N-mismatch.
3. **Observable choice is PER-AXIS, not global** (the principle that ties this together). The same
   observable is a trap on one axis and the right tool on the other:
   - **Clustering axis → pooled-temporal.** Snapshot is the √N trap (H-D tautology, non-dynamical),
     established in the Kaneko magnitude probe. Do NOT chase the snapshot to amplify the clustering swing.
   - **Repulsion axis → snapshot.** The pooled-temporal train is superposition-CONTAMINATED on the
     repulsion axis — merging N independent temporal trains manufactures the bimodal spacing structure
     that the GUE-form fit can't handle → the declined BR_artifact → Kuramoto's repulsion-INCONCLUSIVE.
     The snapshot (N positions at one time, no superposition) is intensive on the repulsion axis and would
     give a CLEAN verdict (BL = blind, or genuine rigidity).
   So Kuramoto's repulsion-inconclusiveness is partly an OBSERVABLE error (pooled-temporal is the wrong
   observable for the repulsion axis). QUEUED concrete payoff: re-check Kuramoto's repulsion axis on the
   configuration SNAPSHOT (needs the Phase 30 sim re-instrumented to return phase snapshots) — would
   upgrade Kuramoto from repulsion-INCONCLUSIVE to a definite BLIND-or-rigid verdict. Observable-fixed
   discipline is INTRA-substrate AND per-axis. [[observable_choice_is_per_axis]].

**Caveat (honest):** the effect here is MODEST (pooled-temporal CV 0.5→1.6) vs Kaneko's spatial SNAPSHOT
(CV 1→50). Reason = observable: the pooled-temporal train of narrowly-distributed oscillators is
sub-Poisson/regular in desync (CV<1) rising to mild-super-Poisson when locked; the Kaneko-style SNAPSHOT
phase-config observable would show the dramatic version. Phase 30 was thus BOTH axis-incomplete (repulsion
only) AND observable-suboptimal (pooled-temporal, not snapshot). The snapshot re-check needs re-instrumenting
the Phase 30 sim to return phase snapshots — queued, ties to the within-Kaneko magnitude question.

## What this buys
The audit premise is VALIDATED on the top candidate: a banked past negative (Phase 30 INSENSITIVE) WAS
axis-incomplete, and the two-axis lens recovers a real, generalizing clustering-axis signal. The
rate/mechanism conclusions of Phase 30 (rate-confounded, no real-data match) are NOT overturned — only
the "INSENSITIVE" framing is refined: insensitive on the repulsion axis, sensitive on the clustering axis.
Remaining HIGH candidates (Allen avalanche, Buzsáki theta-gamma) queued for the same re-check.
