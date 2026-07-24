# Fungal surrogate port — Phase 0 §3a cashed in on the open failure (#4259167)

The Phase-0 §3a measure gate validated, against a theorem (Minkowski vs Gauss), that the measured
class tracks the generating **measure** and that a rate-envelope-preserving surrogate must match the
generating construction. This ports that discipline to the fungal clustering, where nothing brackets
the answer and the validation failure was still open. Artifacts: `arsrh/fungal_surrogate_port.py`,
`fungal_surrogate_port_measured.json`.

## The construction was mis-described — the first thing the port found

Commit 4259167 described fungal as "a pool of 153 units (~10 events each)" and built its null as a
**Palm–Khintchine superposition** of 153 sparse floored-Poisson spike trains. That is not the
construction. `run_fungal_nns.py:250-257` builds the pooled statistic as the **concatenation of
per-unit *normalized* spacings** over the **35 units with ≥ 20 spikes** (`n_units_classified = 35`;
Σ(n−1) over those 35 = **1470** = `pooled_direct.n`, exactly):

```
for each unit with >=20 spikes:   sp = diff(sorted(spikes));   append sp / sp.mean()
pool = concatenate(...);          mass03 = (pool < 0.3).mean()      # = 0.654 observed
```

So the substrate-matched null is: per unit, a floored-Poisson train at that unit's rate/count →
normalize its spacings → concatenate across the 35 units. That preserves the generating measure
(per-unit rate envelope + 120 s dead-time floor + normalize-then-concatenate) and reshuffles only
the within-unit times — the §3a surrogate, on the right construction.

## (1) The clustering SURVIVES the correctly-constructed null — more strongly than before

| | null mass03 | fungal | verdict |
|---|---|---|---|
| correct construction (B=500) | 0.2451 ± 0.0101 (range 0.212–0.280) | 0.6544 | **z = 40, p < 1e-4** |

Fungal's mass03 = 0.654 is **unreachable** by the substrate-matched null. The clustering is real, and
this is *stronger* evidence than 4259167's (which used the mis-built superposition null, mass03 ≈
0.256). The 120 s floor, if anything, suppresses short gaps and makes the detection conservative.

## (2) The flagged I_rep false-positive is CONSTRUCTION-DEPENDENT — and absent on the real substrate

Commit 4259167 flagged that the deployed exact-zero I_rep detector (I_rep = ∫₀¹ max(0, 1−R₂) dr,
clipped ≥ 0) false-positives — a slightly-clustered null clips to exactly 0.000 and the exact-zero
flag calls it "clustered." Measured on both constructions:

| null construction | I_rep mean | % exact-zero (false-positive) |
|---|---|---|
| **fungal's actual** (per-unit normalized-spacing concat) | **+0.0484** | **0 %** |
| 4259167's (153-unit spike-time superposition) | +0.0000 | **100 %** |

The false-positive appears **only on the superposition construction** (Palm–Khintchine drives the
pooled process to Poisson-ish, 1−R₂ goes slightly negative, the clip pins it to 0.000). On fungal's
**actual** construction the per-unit floor's short-range repulsion survives the normalization and
keeps I_rep = +0.048 (repulsion-side), so the exact-zero flag never fires on the null. **4259167
flagged the detector bug on the wrong construction** — the same §3a lesson (the null must match the
generating construction), one level down. On the real substrate the I_rep detector does not
false-positive; and the surviving headline statistic (mass03) was never dependent on it anyway.

> **⚠ THE DETECTOR BUG IS NOT CLEARED — IT IS DORMANT (governs every other substrate).** "4259167
> flagged the bug on the wrong construction" must **not** compress to "there was no bug." The clip
> pathology — a near-zero-*negative* rep pinned to 0.000 and read as CLUSTERED — is **confirmed and
> unfixed.** Fungal's null simply sits at rep ≈ +0.05, far from the boundary, so it never fires
> *here*. The bug is **live on any substrate whose null sits near-zero-negative**, and clearing it
> per-substrate (by showing the null is far from the boundary) is not the same as fixing the clip.

### Half 2 is on the DEPLOYED detector now, not the reconstruction

The table above used a *reconstruction* (`pair_correlation_full` on one pooled train). The deployed
detector is `joint_q_profile` (per-denominator-q passage-time `rep_int_q`, one row per q) +
`joint_quadrant_diagnostic` (BL quadrant, exact-0 = clustered) — the "fungal 194/194 exact-0" flag
(commit 9ad46d6) counts 194 **q-band rows**, not units. Re-run on that actual code path
(`arsrh/fungal_real_detector.py`) against the count-anchored corrected null: **190 BL q-band rows,
0 exact-zero** on a single null (real fungal reads 194/194). So the deployed path agrees with the
reconstruction — "faithful in behavior" upgraded to **confirmed on the real code path**. (A small
B-null distribution corroborates; see `fungal_real_detector_measured.json`.)

### Count anchor = certification of record

The construction was genuinely slippery across three passes — "153 units ~10 spikes" → "35 units ≥20
spikes" → "per-unit-normalized concat of 1470 spacings" — and the only thing that ever pinned it was
the integer match **Σ(n−1) = 1470 = `pooled_direct.n`**. That is the certification of record and the
regression test: `fungal_real_detector.py` asserts it. If anything re-touches this pipeline, 1470 is
the anchor.

### Two halves are not equally certified — stated plainly

- **mass03 survival (z=40):** rests on the exact deployed statistic against a count-anchored null. Solid.
- **I_rep no-false-positive:** now on the deployed `joint_q_profile` path (0/190 single null), not the
  reconstruction — banked, with the standing caveat that it is a *dormant* not a *cleared* bug.

## Net

Both halves of the open failure close, and in the reassuring direction: the clustering is
**confirmed** against a correctly-constructed, measure-preserving null (z = 40), and the flagged
detector false-positive is shown to be an artifact of 4259167's mismatched superposition null, not a
property of fungal's construction. This is exactly the payoff the Phase-0 detour was for — a
surrogate whose discipline was rehearsed against a theorem, then applied where the answer is unknown.

**Correction filed to `DEMODULATION_FINDINGS.md` / commit 4259167:** the "153-unit pool" construction
is superseded by the "35 high-count units, per-unit normalized-spacing concatenation" construction;
the clustering verdict is unchanged (strengthened), and the I_rep false-positive is reclassified as a
mismatched-null artifact rather than a property of the substrate.

**Caveat (honest scope):** the deployed fungal pipeline reads mass03 (+ KS/gap), not I_rep; the I_rep
here is reconstructed by pair-correlation on the pooled normalized spacings (cumsum), a faithful but
not bit-identical re-application of the separate exact-zero detector. The mass03 result is exact to
the deployed statistic; the I_rep result is the correct qualitative and quantitative behavior of that
detector on the two constructions.
