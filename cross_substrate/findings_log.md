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

---

## 2026-05-21 — Landscape look (figures in cross_substrate/figures/)

Three exploratory projections (`landscape_view.py`); descriptive only.

- **P1 universal (I.5q × ARS.rep_med, all 10).** Kuramoto is a clear *trajectory*,
  not a point: the K-sweep climbs rep_med 0→0.85 while I.5q stays mid (substrate-as-
  trajectory, landscape §1). Arithmetic spectra (ζ/Dirichlet/EC, Maass, primes)
  cluster bottom-left (low I.5q, low rep). pvc-11 + allen-np spread along rep≈0 at
  mid I.5q. Mertens/Liouville far-right (far-from-GUE, no repulsion). Pulsar isolated
  mid (direct-leg, not q-banded — comparison-invalid flag).
- **P2 matched repulsion plane (Brody q × BR ρ, 7 substrates).** ζ-zeros sit at the
  GUE corner (q=1, ρ=1) — the matched leg independently recovers Montgomery-Odlyzko.
  Gaussian/Eisenstein primes + Maass intermediate (q≈0.2, ρ≈0.3). pvc-11 forms an arc
  hugging the Poisson axis. Mertens/Liouville/Dirichlet/EC at the Poisson corner.
- **Viewpoint-dependence (concrete instance).** pvc-11 and Mertens/Liouville COLLAPSE
  together at the Poisson corner in Brody/BR space (all q≈0, ρ≈0), but W1δ separates
  them sharply (1.10 vs 1.85). Which viewpoint you pick changes whether two substrates
  look alike — the operational argument for carrying many viewpoints.
- **CAVEAT — L-zeros is internally bimodal; its median masks it.** The 8 L-zeros cells
  span the whole plane: ζ cells are GUE (q=1), Dirichlet/EC cells Poisson-leaning
  (q≈0). The substrate is not a point. Read per-cell, never the pooled median (sibling
  of the per-cell-vs-pooled lesson). [landscape.md §3 grouping caveat added; split TODO.]

**Framework-doing-real-work notes (the predictions are paying out):**
- **Multi-scope movement is real (Kuramoto).** The K-sweep is a connected *trajectory*
  in (I.5q, rep_med), not a point — repulsion climbs 0→0.85 across coupling. Empirical
  instance of landscape §1's "substrate-as-trajectory."
- **Viewpoint-dependence is operationally meaningful.** pvc-11 and Mertens/Liouville are
  indistinguishable in Brody/BR space (Poisson corner) yet sharply separated in W1δ
  (1.10 vs 1.85). Which projection you pick changes the answer — the concrete
  justification for carrying many viewpoints rather than one.

---

## 2026-05-21 — Agreement formalization: is I.5q an unbiased proxy for I.5?

**Test.** Regress `I.5q = a + b·I.5` over matched cells; unbiased ⟺ b=1, a=0.
(`agreement_check.py`, `agreement_check.json`, figures/AGR_proxy_and_floor.png.)

**VERDICT — yes, unbiased within documented conditions.**

| regression | n | slope | intercept | r | unbiased@5% |
|---|--:|--:|--:|--:|:--:|
| R1 pvc-11 internal (leg-only, N-matched) | 1159 | 1.001±0.002 | 0.001±0.001 | 0.998 | ✓ |
| R2 per-substrate medians (equal wt, range 0.27–0.92) | 7 | 0.991±0.007 | 0.008±0.004 | 0.9999 | ✓ |
| R3 all cells pooled | 1182 | 0.999±0.002 | 0.002±0.001 | 0.998 | ✗* |

\*R3's "biased" flag is the pooled trap: n=1159 makes a **practically-negligible
0.002 intercept** statistically significant. R1 (leg difference only, since pvc-11's
two legs are both ~JPF-capped) and R2 (full dynamic range, each substrate one vote)
are the honest reads — both unbiased. R2's slope=0.991 sits within 1σ of the slope=1
the q-banded↔plain-NNS analytical relationship would predict.

**Residual structure (where the proxy works vs whether it works) — two distinct
failure modes, neither overturns the verdict:**
1. **Small-N floor.** liouville `sub_high` (n=41) diverges (|diff|=0.17): too few
   well-powered q-bands → unstable q-banded median. Bracketed by n=41 (fails) and
   n=91 (agrees, |diff|=0.007). **Banked recommendation: require n ≥ 100** for the
   I.5q↔I.5 comparison (and for trusting q-banded placement of low-event cells).
2. **Stimulus-condition residual (NOT sample size).** All 7 large-n (1500–2800)
   divergences are pvc-11 **drifting-gratings** units: mean|diff|=0.008, 3.3% exceed
   0.05. Every other condition (spontaneous, natural/noise/gratings movie) agrees
   near-perfectly (mean 0.0018, **0%** diverge). Strong stimulus-locking is the one
   regime where the cheap proxy degrades — and even there only in a 3% tail.

**STRATEGIC CONSEQUENCE.** I.5q is a trustworthy unbiased substitute for the matched
I.5 for fingerprint *placement*, given n≥100 and away from strongly stimulus-locked
trains. ⇒ **Allen and Kuramoto's 2a-only (q-banded) placement is trustable as-is; their
medium/high-cost matched 2b recompute can be deferred or skipped.** Caveat to watch:
if Allen includes drifting-grating conditions, expect a similar small divergent tail
(placement-level, not disqualifying).

---

## 2026-05-21 — Gratings-divergence study: what drives the 3% tail (210 cells)

`gratings_divergence.py` / `_results.json` / figures/GRD_*.png. Brief:
`gratings_divergence_brief.md`. Verdict vocabulary applied with rate-control mandatory.

**Conjecture REFUTED, sharper finding in its place.**

- **F1/F0 (temporal stimulus-locking) — REFUTED.** |D|~F1/F0 Spearman ρ=+0.055 (p=0.43);
  OSI~F1/F0 ≈ 0 (distinct axes). The divergence is NOT linear stimulus-locking /
  drift-rhythmicity. Per-q Δ is flat across all 30 bands (DIFFUSE) — no temporal-frequency
  resonance, reinforcing the refutation.
- **OSI (orientation selectivity) — CONFIRMED, robust.** |D|~OSI Spearman ρ=+0.466
  (p=1e-12). Survives every control: partial|rate ρ=0.44, |n ρ=0.46, |rate+n ρ=0.45,
  and crucially |I.5+rate+n ρ=0.36 (p=8e-8) — i.e. NOT mere value-scaling, NOT rate, NOT n.
  Orientation-selective gratings cells specifically drive the q-banded↔plain-NNS gap, and
  the sign is q-banded > plain (signed D~OSI ρ=+0.29): the Farey leg reports cells as
  slightly *less* GUE-like than plain-NNS, graded by tuning sharpness.
- **DSI null** (ρ=0.085) — it's orientation, not direction, selectivity.

**De-confounding bonus for H1.** OSI↔GUE-distance holds STRONGLY on BOTH legs —
q-banded I.5q (ρ=0.739) AND matched plain-NNS I.5 (ρ=0.704). So the H1 finding
(OSI↔ks_gue_med) is **not an artifact of the Farey q-banding machinery**; it replicates
on plain unfolded-NNS. H1 is leg-robust — a real spike-train NNS property, strengthened.

**Reframe.** The proxy-divergence `|I.5q − I.5|` is not noise: it is a small, OSI-graded
substrate signal — a candidate landscape coordinate that responds to orientation tuning
sharpness, distinct from (orthogonal to) the universality-class axes and from temporal
stimulus-locking. Banked as viewpoints.md Family VII (inter-leg disagreement).

### Cross-species follow-up — Allen mouse V1 (awake), session 732592105, 110 units

`allen_osi_gap.py`. Read cached Allen .nwb directly via h5py (allensdk's EcephysSession
loader version-mismatches these legacy files; allensdk-the-package is installed in
venv_allen311 for future data *downloads*). Two clean results:

- **OSI-gap is monkey-specific — does NOT recur in mouse awake V1.** |D|~OSI ρ=−0.02
  (p=0.82) raw; partial|i5+rate+n = −0.20 (weakly negative, opposite to monkey's +0.36).
  So the Family-VII OSI-graded divergence is NOT a universal V1 property — it
  **differentiates** monkey-anesthetised from mouse-awake. The inter-leg axis carries
  substrate/state-specific signal (answers the Family VII applicability question: it is
  substrate-specific, not universal).
- **H1 leg-robustness GENERALIZES cross-species.** OSI↔I.5q ρ=+0.478 AND OSI↔I.5(plain)
  ρ=+0.486 — both legs in mouse, mirroring monkey (both ~0.70). So H1 (OSI↔ks_gue_med) is
  not a Farey-machinery artifact in EITHER species. Mouse ρ≈0.48 vs monkey ≈0.70 tracks
  the known ~58% awake-mouse attenuation (ars_claim_status). Banked as a cross-species
  strengthening of H1.
- **Caveat:** single session (the full OSI-characterised set in h1_allen_comparison.parquet);
  a real but one-session test of the gap's absence.

---

## 2026-05-22 — AM Phase 1 complete: 6 core cells matched-recompute (Night-1 brief)

`am_reextract.py` (Stage A eigensolve+bank → Stage B unfold @ converged L →
per-φ aggregate). Eigenvalues + unfolded event-trains PERMANENTLY banked
(`coordinates/am_work/`). 6 cells: sup N=50k/70k/100k (λ=1.5, converged) + sub
N=70k/100k/125k (λ=0.5; N=70k/125k not-L-converged, banked as characterization).

| cell | W1δ | ks_gue | Brody q | BR ρ | Σ²(L) |
|---|--:|--:|--:|--:|--:|
| sup_N50k | 0.302 | 0.092 | 1.00 | 0.999 | 0.97 |
| sup_N70k | 0.444 | 0.148 | 0.81 | 0.896 | 1.23 |
| sup_N100k | 0.500 | 0.148 | 0.54 | 0.781 | 0.95 |
| sub_N70k | 0.005 | 0.528 | (clock) | (clock) | 0.19 |
| sub_N100k | 0.000 | 0.532 | (clock) | (clock) | 0.19 |
| sub_N125k | 0.006 | 0.529 | (clock) | (clock) | 0.19 |

- **Reading.** Subcritical (λ=0.5, AC spectrum) → clock-rigid (W1δ≈0; Brody pegs at
  the rigid bound). Supercritical (λ=1.5, PP) → intermediate AND **N-drifting**
  clock→Poisson (W1δ 0.30→0.50, q 1.0→0.54 over N=50k→100k). The L-underconvergence/
  N-scaling pathology IS the AM fingerprint (VI.2 β≈2.87 across sup spreads).
- **VERIFIED against Phase 35** (the matched leg is the same `unfold_rotnum`): per-φ W1δ
  mean = 0.3020 and per-φ spread = 0.1151/0.3816/0.8470 reproduced bit-exact.

**METHODS — φ-ensemble aggregation bug (caught + fixed).** First agg concatenated the
16 φ unfolded *positions* and re-diffed → interleaves 16 separately-unfolded spectra =
a SUPERPOSITION with spurious near-Poisson statistics (gave W1δ=0.146 for sup_N50k;
sub cells falsely 1.8). Fixed: aggregate **per-φ** (Family II per-φ then mean; Family I
on pooled per-φ *spacings*) — never concatenate positions across φ. The Phase-35
reproduction check is what surfaced it (always verify a regeneration against
ground-truth before banking).

**METHODS — cost-probe underestimate.** Single-task probe projected ~3.5 h; actual
~13.7 h. Causes: (1) N=125k not in the probe and largest by N·L; (2) the isolated-task
probe ran at full memory bandwidth, but 18 concurrent large-`N×L` workers contend →
~3–4× slower each. Lesson: probe at full worker count (or discount for bandwidth) for
memory-bound array work; add a wall-clock halt to long runners.
**RESOLVED — worker-count optimum (worker_scaling_probe.py):** throughput PEAKS
at 10 workers (5.21× serial) and DECLINES past it (18 → 4.62×, ~12% slower in
aggregate AND each task 2× slower). The 5900x dual-channel memory saturates ~8–10
streaming `ids_rotnum` workers. Default set to `--workers 10` (faster total +
leaves cores free). 18 was strictly worse. Don't raise without re-probing.

---

## 2026-05-23 — AM C1 θ-class extension (5 cells: sup silver/Liouville, sub silver/Liouville/bronze)

`am_reextract.py --cells c1` (sup, L=2.56e7) + `--cells subc1` (sub, L=6.4e6).
3-way sup + 4-way sub θ comparison at matched (N=70k, L). All matched object-(a) leg.

| side | θ-class | W1δ | per-φ spread | Brody q | BR ρ |
|---|---|--:|--:|--:|--:|
| sup λ=1.5 | golden | 0.444 | 0.382 | 0.812 | 0.896 |
| | silver | 0.507 | 0.570 | 0.438 | 0.776 |
| | liouville | 0.497 | 0.594 | **0.281** | 0.431 |
| sub λ=0.5 | golden | 0.0054 | 0.000 | 1.000 | 1.000 |
| | silver | 0.0056 | 0.000 | 1.000 | 1.000 |
| | liouville | 0.0057 | 0.000 | 1.000 | 1.000 |
| | bronze | 0.0056 | 0.000 | 1.000 | 1.000 |

**FLAG (apparent inversion of Phase 35; NOT resolved).** On the matched leg the
**sup** side carries the θ-class structure — W1δ universal within ~13% (consistent
with Phase-35 sup-universal) but Brody q strongly θ-graded (golden 0.81 → silver 0.44
→ Liouville 0.28; the non-Diophantine Liouville is most Poisson-leaning, as predicted).
The **sub** side is θ-INVARIANT (all 4 classes clock-rigid, W1δ≈0.006, per-φ spread≈0).
This APPEARED to invert Phase 35's framing (sub θ-sensitive 3.55× / sup θ-universal).

**RESOLVED — no inversion (2026-05-23).** Pinned Phase 35's "3.55×" to its exact metric
(`curiosity_theta_robustness`): it is `spread_ratio_silver_over_golden` on sub = the ratio
of per-φ W1δ *spreads* at L=1e5. Reproduced bit-close from banked eigenvalues:
silver/golden spread ratio = **3.556** (Phase 35: 3.555), mean_ratio = **1.0003**. But the
absolute spreads are **clock-floor ~1e-4** (golden 2.7e-5, silver 9.5e-5) and the MEANS are
θ-invariant (1.0003). So Phase 35's "sub θ-sensitive 3.55×" is a **ratio of negligible
micro-spreads**, not a magnitude effect — sub is θ-invariant in magnitude (Phase 35's own
mean_ratio=1.0003 already said so). The matched-leg result (sub θ-invariant W1δ; sup carries
θ-structure via Brody q) is **fully consistent** with Phase 35's underlying numbers. The
genuine θ-structure is on the **sup** side. Methods: a "3.55× sensitivity" that is a ratio
of ~1e-4 clock-floor values is not substantive — ratio-vs-magnitude (discriminant-exact-question).

**METHODS — aggregator is the new bottleneck (not compute).** Stage B sub-θ finished in
the projected time, but `--agg` is single-threaded and recomputes Family II (Σ²/Δ₃
sliding-window/lstsq) per-φ for every cell: ~17 min/cell (50 min for 3), and `--cells all`
re-crunches all 11 each run (~4 h, which I had to kill). **FIXED (2026-05-23):** root
cause was Family II over-sampling sliding windows (Δ₃ slid by L/4 → ~N/12 windows;
Σ²'s `number_variance` used O(N) boolean masks per window). Capped window placements to
≤400 + switched to searchsorted (`_window_starts` in axes.py). Result: full 11-cell agg
**53 s (was ~3 h, ~200×)**; Family I byte-identical; Σ² now correctly →0 for clock-like
substrates (sub 0.19→0.008). NOTE: pvc-11/arithmetic Family II were computed with the old
window scheme — re-run for strict consistency is now cheap (a cross-substrate follow-up).

---

## 2026-05-23 — Mackey-Glass substrate placed (breadth) + first Family V axes

`mackey_glass_run.py` (reuses transition_calibrators_dynamical integrator + 3 extractors).
5-regime τ-sweep, peak-interval NNS + Family V (Lyapunov, corr-dim) + VI.3 cross-extraction.

| τ regime | n_ev | W1δ | λ₁ | D₂ | VI.3 |
|---|--:|--:|--:|--:|--:|
| 4 stable | 5 | NA | −0.49 | 0.00 | NA |
| 10 periodic | 967 | 0.001 | +0.002 | 0.99 | 0.000 |
| 17 period-dbl | 604 | 0.070 | +0.200 | 1.96 | 0.003 |
| 23 chaotic | 638 | 0.219 | +0.160 | 2.31 | 0.004 |
| 30 deeper | 635 | 0.301 | +0.108 | 2.41 | 0.004 |

- **Substrate-as-trajectory:** the τ-sweep moves stable→periodic→chaotic (W1δ broadens
  0.001→0.30; like Kuramoto's K-sweep). Banked as 5 cells.
- **V.2 D₂ — VALIDATED, good magnitudes:** stable 0 → periodic 1.0 → chaotic 2.3–2.4,
  matching MG literature (D₂≈2). Clean first Family V axis.
- **V.1 λ₁ — regime-SIGN validated, magnitude PROVISIONAL:** sign ordering correct
  (stable −0.49, periodic ≈0, chaotic >0 → reliable chaos detector), BUT magnitudes
  unreliable (τ=17→0.20 vs literature ~0.009; within-chaos order 17>23>30 inverted —
  Rosenstein linear-region not tuned). Banked as chaos-sign indicator only
  (synthetic-validate-fitters discipline: don't report as absolute λ). Tuning the
  fit-region is a follow-up.
- VI.3 cross-extraction variance (W1δ across 3 extractors): 0 for periodic (extractors
  agree), 0.003–0.004 for chaotic (they diverge) — sensible.

### REFUTED HYPOTHESIS (recorded so it is not re-resurrected)

**H (refuted):** "Drifting gratings produce rhythmic stimulus-phase locking → Farey-
rational-aligned spike-time structure that q-banding picks up and plain-NNS averages
out; therefore |D| should track F1/F0 and localize to stimulus-TF-related q-bands."

**Killed by, directly:** (1) |D|~F1/F0 ρ=+0.055 (p=0.43) — no relationship; (2) per-q
divergence is FLAT across all 30 bands (DIFFUSE) — no temporal-frequency resonance;
(3) OSI~F1/F0 ≈ 0 — the real driver (OSI) is a distinct axis from the conjectured one.
The divergence is about what the spike train *carries* (orientation-tuned firing
structure), NOT what the stimulus *drives* at specific temporal frequencies. Do not
revive the temporal-locking story.

### Math-path opener (across-band mechanism — TESTED, redirected)

`mathpath_acrossband.py`. Will's speculative mechanism: tuned cells have skewed/
dispersed across-q-band ks_gue, so the band-median (I.5q) diverges from pooled (I.5).
**Result: present but NOT the mediator.** Across-band dispersion weakly tracks OSI
(std ρ=+0.18) and |D| (std ρ=+0.24); tuned cells have fewer GUE-like bands
(frac<0.3 ~ OSI ρ=−0.21). BUT controlling |D|~OSI for band std+skew barely moves it
(0.466→0.434). ⇒ **the math-path should NOT target across-band-uniformity** — that's a
minor contributor. The residual OSI gap lives in how the **Farey-passage transform
itself** (t·(a/q) mod 1) responds to orientation-tuned firing differently from the
plain unit-mean unfold — a subtler, still-open derivation target.
