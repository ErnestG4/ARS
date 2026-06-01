# Confound-Fingerprint Re-Audit · Findings

**Phase 36, 2026-06-01.** The durable Phase-36 output is an ARS INSTRUMENT CONFOUND: a pooled-temporal
observable of rhythmic units can read as false high-rep (BR/BR_artifact) where the matched snapshot reads
clean BL. The re-audit pass (queued in [[pooled_rhythmic_repulsion_confound]]) checks past banked verdicts
for the fingerprint — **pulsar-timing first** (most periodic objects in nature → textbook suspect), neural
pooled-spike next. This pass also re-derived the confound's *mechanism* and corrected it.

---

## Item 1 — Phase 33a NANOGrav pulsar timing: NOT a confound suspect (verdict uncorrupted)

Phase 33a (banked STRUCTURAL_MISMATCH on NANOGrav 15-yr folded-template TOAs) is the strongest prior
suspect on the "most periodic objects" intuition. Re-read `data/phase33a_results/pilot_direct_stats.parquet`
(the actual rep_int/CV numbers, which the findings doc table omitted):

| mode | rep_med | CV | z_rep | side of Poisson |
|---|---|---|---|---|
| raw_toas (Mode A) | **0.02–0.04** (low) | **9.7–14.7** | −123 to −597 | deep super-Poisson (clustering) |
| epoch_collapsed (Mode B) | 0.42–0.88 | **1.2–2.5** | ≤ Poisson (−1.6 to −19; B1855 +3.3) | super-Poisson (clustering) |

**Verdict: NOT a suspect.** The confound manufactures *sub-Poisson rigidity* (CV<1, high-rep BR/BR_artifact).
Every Phase 33a read is on the **clustering side of Poisson** (CV>1) with low-to-moderate rep_med and z_rep
at-or-below Poisson — driven by apparatus (Mode A = radio-backend frequency-channel coincidence; Mode B =
telescope scheduling cadence). Per the confound's **asymmetry rule** (the artifact *makes* rigidity, it does
not *erase* it → clean-clustering / low-rep reads are SAFE), Phase 33a's STRUCTURAL_MISMATCH is uncorrupted.

Two notes:
- **Doc-label correction.** `PHASE33A_FINDINGS.md` calls the high `mass<0.3` a "BR_artifact indicator /
  BR_artifact-shape." That is backwards: in the pilot, `rep_med = fraction(s>0.3) ≈ 1 − mass<0.3`, so high
  `mass<0.3` = **low** rep_med = clustering/BL-side — the *opposite* of BR_artifact (which needs rep_int
  HIGH ≥0.55). The pilot also used a proxy `rep_int(s,κ=0.3)`, **not** the real `joint_quadrant_diagnostic`
  (thresholds 0.10/0.55 + GUE-form-fit), so Phase 33a never assigned a real quadrant/BR_artifact label.
- **Why "most periodic objects" did NOT fire:** Phase 33a never reached the per-pulse layer. TOAs are
  folded-template aggregates; their pooling structure (channels + schedule) is *clustering*, not regularity.
  The genuinely-periodic layer (per-pulse arrivals, extraction-mode-D) was never accessed — and a single
  pulsar's per-pulse train would be *real* periodicity (a TL read), not a pooling artifact.

---

## Mechanism correction (the important part) — the confound is TEMPORAL-GRID QUANTIZATION, not superposition

Re-deriving *why* the Kuramoto desync pooled-temporal train read sub-Poisson (CV 0.72 → declined
BR_artifact) exposed that the **banked mechanism was wrong**.

**The banked claim** ([[pooled_rhythmic_repulsion_confound]] as written): "finite-N superposition of
near-periodic crossings → residual regularity, CV<1."

**Test 1 — clean synthetic, pure periodic units, continuous time** (`no` simulation grid):
superposition of N pure-periodic units at fixed per-unit rate, random phases:
- broad frequency spread → pooled CV → **1.0** monotonically (0.87→0.96→0.99→1.00 for N 10→2000) = Palm-Khintchine.
- identical frequency, random phase → CV ~1 (non-monotone), **never →0**.
⇒ pure periodic superposition in continuous time does **NOT** manufacture sub-Poisson. "Anti-bunching" is not it.

**Test 2 — refine the simulation timestep** (Kuramoto desync K=0, N=100, *identical spike count* 24671):

| dt | mean pooled IEI / dt | pooled CV | rep_med | quadrant |
|---|---|---|---|---|
| 0.005 (default) | 1.62 | 0.72 | **0.75** | **BR_artifact** |
| 0.002 | 4.05 | 0.87 | — | — |
| 0.001 | 8.11 | 0.93 | — | — |
| 0.0005 | 16.21 | 0.95 | **0.16** | **TR** |

As dt shrinks (same spikes, finer placement), CV climbs toward Poisson and the **repulsion-axis quadrant
flips BR_artifact → TR** (rep_med 0.75 → 0.16). The sub-Poisson / BR_artifact was substantially a
**finite-dt temporal-quantization artifact**: at the default dt the mean pooled IEI is ~1.6 timesteps, so
threshold-crossings snap onto the grid → spurious regularity. The N-scaling I first saw (CV 0.82→0.20 for
N 50→500) is the *same* mechanism — higher N → higher pooled rate → IEI approaches dt → worse quantization,
NOT genuine anti-bunching.

**Corrected mechanism:** a high-rate pooled-temporal observable whose **pooled event rate approaches the
data's temporal resolution** (simulation dt / sample clock / bin width) quantizes onto the time grid →
spurious sub-Poisson regularity → inflated rep_int → false BR/BR_artifact. Rhythmicity is the *setup* (many
units → high aggregate rate), the grid is the *mechanism*.

**Knock-on check — the sibling CLUSTERING-axis verdict survives (and was understated).** The mechanism
correction could have threatened the "Kuramoto is clustering-type" finding (which rests on the clustering-axis
CV separation desync→sync). It does not — it strengthens it. At fine dt the separation GROWS:

| dt | desync CV (kf0) | sync CV (kf2) | sep (sync−desync) |
|---|---|---|---|
| 0.005 | 0.72 | 1.57 | 0.85 |
| 0.001 | 0.93 | 2.14 | 1.21 |

Quantization pulls pooled CV *downward* at both ends. At desync that crosses *below* Poisson → false-rigid
(the repulsion artifact). At sync it only compresses genuine super-Poisson (stays >1). So the **sign** of the
clustering separation is preserved and its magnitude was *suppressed* by coarse dt — only the REPULSION-axis
read was qualitatively corrupted. Clustering-type verdict SAFE.

**What survives / what changes:**
- SURVIVES: the pooled-temporal observable misrepresents the repulsion axis; the matched **snapshot is the
  correct observable** (instantaneous phase gaps, no grid-snapped event times → dt-robust → clean BL, rep→0).
  The per-axis-observable principle and the Kaneko/Kuramoto split-dissolution are unchanged.
- CHANGES: the *mechanism* (superposition anti-bunching → temporal-grid quantization at high pooled rate),
  and therefore the **diagnostic** and the **searchable fingerprint** (below).

---

## Sharpened fingerprint + diagnostics (supersedes the superposition framing)

**Suspect signature:** BR / BR_artifact (or any sub-Poisson/high-rep read) on a **pooled-temporal**
observable whose **pooled event rate approaches the data's temporal resolution** (mean pooled IEI within a
small multiple of the sample/grid/bin interval). Rhythmic underlying units make this more likely (predictable
firing → more coincident grid-snaps) but are not strictly required — any sufficiently high-rate pooled train
on a coarse grid can quantize.

**Diagnostics (cheap, decisive):**
1. **Compute mean-pooled-IEI / temporal-resolution.** If ≲ a few, treat the rigidity read as SUSPECT.
2. **Snapshot / superposition-free re-read** (best fix) — instantaneous spatial config, no temporal pooling.
3. **Refine temporal resolution** (or decimate the pooled rate) — if the rigidity weakens as resolution
   improves, it was the quantization artifact (Kuramoto: rep 0.75→0.16 over a 10× dt refinement).

**Asymmetry (unchanged):** the artifact MANUFACTURES rigidity, it does not ERASE it → clean-BL / clustering
(super-Poisson) pooled reads are SAFE; only high-rep pooled-temporal reads on high-rate trains are suspect.

---

## Item 2 — neural pooled-spike re-audit (queued, now with a sharper criterion)

The neural pooled-spike candidates (Allen avalanche, Buzsáki theta-gamma — dedicated NWB-engineering arcs,
allen_cache 29GB on disk) gain a concrete, cheap pre-check from the corrected mechanism: **pooled
population-spike rate vs the recording sample resolution** (e.g. 30 kHz → ~33 µs). If a banked rigidity/
high-rep read came from a pooled train whose rate approaches the sample clock, it is a quantization suspect.
Otherwise (clustering-side / low-rate-pooled), it is safe. Deferred to the NWB arc.

## Status
Phase 33a re-audited: NOT a suspect, verdict uncorrupted. Flagship mechanism CORRECTED (temporal-grid
quantization, not superposition); headline + snapshot-fix survive. Fingerprint + diagnostics sharpened.
