# Cross-Substrate Findings Log

Conservative substrate-observations from coordinate computation. No
over-interpretation; cluster structure is for Will to read (anti-hypothesis-test
discipline, instructions §6). Entries are dated and cite the source pass.

---

## 2026-05-21 — Phase 2a harvest: first cross-substrate `I.5q` readout

**What.** Harvested already-banked NNS metrics across 10 substrates into
`coordinates/*.jsonl` (8,275 records, no recompute). The axis `I.5q_ks_gue_med`
is the ARS Farey-q-banded KS distance to GUE (`joint_q_profile`), median over
well-powered q-bands. Lower = closer to GUE.

**Readout (median I.5q, per substrate):**

| substrate | n (measured) | median | p10–p90 | leg |
|---|--:|--:|--|--|
| gaussian-primes | 2 | 0.240 | — | q-banded |
| eisenstein-primes | 1 | 0.250 | — | q-banded |
| maass-Γ₀(N) | 6 | 0.275 | 0.27–0.30 | q-banded (+ matched I.9 ρ≈0) |
| L-zeros (ζ/Dirichlet/EC) | 8 | 0.293 | 0.03–0.32 | q-banded |
| allen-np (mouse V1) | 544 | 0.464 | 0.39–0.53 | q-banded |
| kuramoto | 6361 | 0.507 | 0.39–0.53 | q-banded |
| pvc-11 (monkey V1) | 1159 | 0.508 | 0.36–0.64 | q-banded |
| pulsar-nanograv | 10 | 0.745 | 0.30–0.97 | **direct (raw_toas), NOT q-banded** |
| mertens | 3 | 0.904 | 0.89–0.92 | q-banded |
| liouville | 4 | 0.906 | 0.77–0.93 | q-banded |

**Comparison-validity flags (carried in records, not enforced):**
- **AM is absent from this axis.** AM has only plain-NNS W1δ (object (a)); it
  enters this q-banded frame only via a Phase 2b/AM recompute. Do NOT place AM
  against this column yet.
- **Pulsar is a different leg.** Direct mode on raw TOAs, not q-banded; tagged
  cross-domain STRUCTURAL_MISMATCH-bounded (phase33a). Its 0.745 is not
  instrument-matched to the q-banded substrates.
- **Arithmetic n is tiny** (1–8 cells each) — segment/panel/level granularity,
  not a population. Medians are descriptive only.

**Observations (descriptive, no mechanism claimed):**
- The arithmetic-spectrum substrates (primes, Maass, L-zeros) sit low on I.5q
  (≈0.24–0.29); the random-walk/sign-change arithmetic objects (Mertens,
  Liouville) sit high (≈0.90); the biological + Kuramoto substrates sit in a
  middle band (≈0.46–0.51). Not interpreted here.
- Maass-Γ₀(N) additionally carries a matched Berry-Robnik ρ≈0 (from phase34e,
  the same validated fitter) — the only harvested substrate with an
  object-(a)-comparable axis besides AM.

**Coverage gaps surfaced:**
- allen-np: 544/719 cells measured; 175 underpowered (n_well=0, banked as
  I.5q=None + reason). Multi-scope: cells span spatial `bin` (fine-local … ).
- kuramoto: 6361/6363 measured across a K-sweep (per-oscillator + aggregate).
- Family III (RF) harvested only where `rf_amp_per_q` was banked: pvc-11,
  allen-np, kuramoto.

---

## 2026-05-21 — Phase 2b: pvc-11 matched object-(a) recompute (1159 cells)

**What.** Recomputed the matched plain-unfolded-NNS axes (I.1–I.9, II.1–II.3) per
pvc-11 cell from raw spike trains (loader → unfold_unit_mean → unfold_rotnum.spacings,
the AM-matched leg), merged into `coordinates/pvc-11.jsonl`. 337s, fitter gate passed.

**Matched Family-I/II distribution (median, p10–p90):**

| axis | median | p10–p90 |
|---|--:|--|
| I.1_w1_clock | 1.097 | 0.86–1.32 |
| I.2_w1_gue | 0.817 | 0.55–1.08 |
| I.4_w1_poisson | 0.432 | 0.15–0.74 |
| I.5_ks_gue (object-a) | 0.506 | 0.36–0.64 |
| I.7_ks_poisson | 0.255 | 0.09–0.40 |
| I.8_brody_q | 0.000 | 0.00–0.00 |
| I.9_berry_robnik_rho | 0.001 | 0.00–0.01 |
| II.1_sigma2_L | 137.8 | 61–483 |
| II.2_delta3_L | 5.94 | 3.2–11.2 |

**FLAG (surprise, not interpreted) — instrument agreement.** Across all 1159
cells, the object-(a) plain-NNS `I.5_ks_gue` and the q-banded `I.5q_ks_gue_med`
agree at **Pearson r = 0.998, mean|diff| = 0.003** — two independent code paths
(fresh unfold→ks vs banked Farey-q-banded median) on the same spike trains land
on essentially the same value. *Possible implication (for Will, not concluded):*
for spike-train substrates the q-banded harvest (2a) may be effectively
comparable to AM's plain-NNS axis after all — but this is ONE substrate; the legs
could diverge elsewhere (AM sub↔sup precedent). Needs the same r-check on Allen /
Kuramoto before any cross-leg comparison is trusted.

**Descriptive note.** pvc-11 shows essentially no level repulsion anywhere
(Brody q≈0, BR ρ≈0 across the population) — uniformly Poisson-leaning-or-below on
object (a). Not interpreted.

---

## 2026-05-21 — Phase 2b: arithmetic + Maass matched recompute (24 cells)

**What.** Regenerated each banked cell's exact point process via the originating
phase's own generator (Maass eigenvalues, Mertens/Liouville sign-changes, ζ/
Dirichlet/EC zeros, Gaussian/Eisenstein prime angles), unfolded as that phase did,
computed matched Family I/II, merged into coordinates. Regeneration **faithful**:
`n_events_regen` matched each cell's banked `n_events_in` exactly (Mertens full=3866,
zeta-low=10000, gaussian_X1e5=9567, …). The object-(a) recompute uses the FULL
sequence (uncapped — matched to AM's W1δ); the q-banded `I.5q` ran on the JPF-capped
(~1500) subset, so the two differ in N by design.

**Matched readout (object-(a)):**

| cell | I.5 (obj-a) | I.5q | I.1 W1δ | Brody q | BR ρ |
|---|--:|--:|--:|--:|--:|
| zeta-low-height-bulk | 0.027 | 0.036 | 0.314 | 1.00 | 0.999 |
| zeta-mid-1e5-2e5 | 0.016 | 0.018 | 0.323 | 1.00 | 0.999 |
| gaussian_X1e5 | 0.236 | 0.237 | 0.644 | 0.23 | 0.314 |
| eisenstein_X1e6 | 0.246 | 0.250 | 0.664 | 0.20 | 0.283 |
| dirichlet-real-Sp | 0.304 | 0.327 | 0.769 | 0.00 | 0.006 |
| ec-root-plus-SO-even | 0.293 | 0.302 | 0.753 | 0.00 | 0.079 |
| maass level_91 | 0.283 | 0.298 | 0.741 | 0.00 | 0.002 |
| maass level_95 | 0.258 | 0.270 | 0.691 | 0.08 | 0.281 |
| mertens full | 0.907 | 0.904 | 1.850 | 0.00 | 0.00 |
| liouville full_133 | 0.920 | 0.922 | 1.862 | 0.00 | 0.00 |
| liouville sub_high (n=41) | 0.889 | **0.719** | 1.701 | None | None |

**Matched-instrument confirmations (descriptive):**
- **ζ-zeros → Brody q=1.00, BR ρ=0.999** (full GUE repulsion). The matched object-(a)
  leg independently recovers Montgomery-Odlyzko GUE — a sanity-check that the leg
  reads true universality class, not just an ARS-internal statistic.
- **Mertens / Liouville → q=0, ρ=0, W1δ≈1.8** (far from GUE; W1δ ≫ Poisson's 0.736 ⇒
  strongly clustered). Consistent with their BL classification.
- **Maass → ρ spread 0.00–0.28 across levels** — consistent with the Sarnak anomaly
  (Poisson-leaning despite arithmetic origin).

**I.5 ↔ I.5q agreement generalizes.** Across bio (pvc-11, r=0.998) AND arithmetic
substrates, object-(a) `I.5` and q-banded `I.5q` agree to ~0.01–0.02 — despite the
N difference (full vs JPF-capped). *Possible implication (Will's to draw):* the cheap
2a q-banded harvest may be effectively comparable to AM's matched leg for
fingerprint-placement purposes. **One exception flagged:** liouville `sub_high`
(n=41) diverges (0.889 vs 0.719) and fitters return None — small-sample, not trusted.
