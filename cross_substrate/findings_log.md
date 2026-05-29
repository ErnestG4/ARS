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

---

## 2026-05-23 — Lorenz + logistic substrates + Family V validation synthesis

`lorenz_logistic_run.py`. Two more dynamical anchors (14 substrates total).

**Lorenz (ρ-sweep, 4 cells):** stable ρ=20 (n_ev=0, λ₁=−1.43, D₂=0) → chaotic ρ=28/35/40
(D₂≈2.1–2.2, λ₁>0). Lobe-transition events; W1δ≈0.55 in chaos.
**Logistic (r-sweep, 5 cells):** period-doubling route; IEI events; analytic λ.

**FAMILY V — now validated, with a clean tool-by-regime split:**
- **V.2 D₂ (Grassberger-Procaccia): reliable magnitudes across all 3 dynamical substrates.**
  Lorenz ρ=28 → 2.21 (lit 2.06); MG chaotic → 2.3–2.4; logistic chaos → 0.97 (1D map).
  Stable/periodic → 0–1 correctly. This is the trustworthy dynamical axis.
- **V.1 λ — METHOD MATTERS:**
  - *Maps (analytic λ=⟨ln|f'|⟩): EXACT.* Logistic r=3.7 → +0.356 (lit ≈0.36); the period-3
    window r=3.83 → **−0.370 (correctly λ<0 INSIDE chaos)** — a sharp, definitive validation.
  - *Flows (Rosenstein on x(t)): SIGN-valid, magnitude ~7× INFLATED.* Lorenz ρ=28 → 6.3 vs
    known 0.906; MG similarly inflated. The inflation is a CONSISTENT factor (≈7×) across
    MG+Lorenz → likely a fixable Rosenstein calibration (fit-region/units), not random.
    Banked as a chaos-sign indicator; flag for calibration before using as absolute λ.

**Takeaway (flag, not interpret):** the dynamical substrates form a chaos-ordered family
(stable → periodic → chaotic) on D₂ and λ-sign; the three flows (MG, Lorenz) + map (logistic)
give the landscape a validated dynamical axis (D₂) and a sign-reliable λ.

**RESOLVED (2026-05-23) — λ via tangent-space, not Rosenstein.** The Rosenstein magnitude
issue was the wrong-tool problem: time-series Rosenstein is for DATA-ONLY substrates, but
these are SIMULATED (we have the equations). Switched the simulated substrates to the
gold-standard tangent-space (Benettin) method: co-evolve a perturbation under the Jacobian
(flows) / analytic ⟨ln|f'|⟩ (map), renormalize, average log-growth. Now correct SIGN AND
magnitude everywhere:
- **Lorenz (Benettin):** ρ=28 → λ=0.909 (known 0.906, essentially exact); stable ρ=20 →
  −0.155 (correct negative). ρ-sweep λ ordered.
- **MG (DDE Benettin):** stable τ=4 → −0.028; periodic τ=10 → ≈0; chaotic τ=17/23/30 →
  +0.0053/+0.0101/+0.0073 (correct sign, magnitude ~lit 0.0086, ordering).
- **Logistic (analytic):** exact (unchanged) — the map's tangent-space λ.
`axes.V1_lyapunov` (Rosenstein) is retained for FUTURE data-only substrates (real time
series without equations), flagged as a sign-indicator there. The open Rosenstein-calibration
item is closed by method choice.

---

## 2026-05-23 — Sturmian-word substrate: Lagrange-class cluster prediction REFINED

`sturmian_run.py`. The bridge substrate (number-theoretic frame, PROGRESS_REPORT §4):
Sturmian word of slope α → 1-positions (Beatty) as event-train; sweep α across Lagrange
classes; two legs (ARS-classify q-banded+RF, matched NNS). 8 cells. **Prediction tested:
does the fingerprint cluster by continued-fraction class?**

| α (class) | n_ev | I.5q | W1δ | Brody q | III.4 (RF) |
|---|--:|--:|--:|--:|--:|
| golden (quad, a₁=1) | 247k | 0.344 | 0.292 | 1.000 | 0.028 |
| silver (quad, a₁=2) | 166k | 0.374 | 0.201 | 1.000 | 0.019 |
| bronze (quad, a₁=3) | 121k | 0.447 | 0.128 | 1.000 | 0.007 |
| √3−1 (quad, per-2) | 293k | 0.351 | 0.340 | 1.000 | 0.012 |
| e−2 (transc, Dioph) | 287k | 0.333 | 0.342 | 1.000 | 0.018 |
| Liouville Σ10^−k! | 44k | 0.524 | 0.018 | 1.000 | 0.008 |
| Liouville Σ2^−k! | 306k | 0.378 | 0.325 | 1.000 | 0.023 |
| 3/5 (rational) | 240k | 0.533 | 0.267 | 1.000 | 0.002 |

**VERDICT — prediction NOT borne out at the SYMBOLIC level; stratification is SPECTRAL.**
1. **Repulsion axis θ-universal:** Brody q = BR ρ = 1.000 for *every* α — the 3-distance
   theorem makes the Beatty event-train ultra-rigid (fitters peg at the rigid bound).
2. **W1δ / I.5q / RF track the FIRST CF quotient ⌊1/α⌋ (local gap structure), not Lagrange
   class:** metallic means order by a₁ (golden→silver→bronze monotone on W1δ AND III.4), but
   √3−1, e−2, Liouville-2 co-cluster (~0.33), and the two Liouvilles split — i.e. gap-ratio
   driven, not quadratic-vs-transcendental.
3. **Rational (periodic) is cleanly distinct** (RF 0.002, degenerate) — rational↔irrational
   separates; deep CF-class does not.

**Interpretation (flag): the CF-class stratification Will predicted — and that AM's θ-class
fingerprint SHOWED (Brody q golden 0.81→Liouville 0.28) — is a SPECTRAL/operator phenomenon,
NOT a symbolic-word one.** The symbolic Sturmian word is governed by local 3-distance rigidity
+ first-quotient; the deep Lagrange structure requires the operator spectrum (AM / Sturmian
Hamiltonian = Fibonacci at golden). This sharpens the §4 frame: parameter-side path ↔ event-train
is real, but Lagrange stratification lives on the spectral side. (Secondary flag: Liouville-2
shows a p=7 RF concentration of 0.019, the canonical ARS p=7 enrichment — not interpreted.)

---

## 2026-05-23 — Sturmian Hamiltonian operator sweep: spectral stratification CONFIRMED (capstone)

`sturmian_hamiltonian_run.py`. Tests the prediction the word refuted: does the OPERATOR
spectrum stratify by Lagrange class? Tridiagonal H, V_n=λ·χ_{[1−α,1)}({nα+φ}), λ=2, N=8000,
8φ; polynomial-IDS unfold → NNS + box-counting spectral dimension D_box (golden = Fibonacci
Hamiltonian). 16th substrate; first Family IV axis (IV.2 spectral box-dim).

| α (class) | W1δ | Brody q | D_box |
|---|--:|--:|--:|
| golden (quad) | 1.790 | 0.000 | 0.628 |
| silver (quad) | 1.774 | 0.000 | 0.649 |
| bronze (quad) | 1.789 | 0.000 | 0.644 |
| √3−1 (quad) | 1.773 | 0.000 | 0.640 |
| e−2 (transc-Dioph) | 1.754 | 0.000 | 0.651 |
| Liouville | 1.590 | 0.000 | **0.724** |
| rational 3/5 | 0.534 | **0.880** | **0.805** |

**VERDICT — CONFIRMED: the spectrum stratifies where the symbolic word did not.**
(1) all irrational α → Cantor spectrum (D_box<1, q=0, W1δ≈1.8 clustered); (2) D_box stratifies
by class — quadratics cluster (~0.63–0.65), Liouville separates higher (0.724, less-gappy),
e−2 in-between (0.651); (3) rational → AC band spectrum, opposite regime (D_box=0.805, q=0.88).
**Resolves the number-theoretic thread:** the Lagrange/CF-class stratification is a SPECTRAL
(operator) phenomenon — absent from the symbolic word (3-distance-rigid), present in the
Hamiltonian spectrum — consistent with AM's θ-class fingerprint (also spectral). Bonus: first
Family IV axis; Fibonacci Hamiltonian effectively placed (golden). Flag, not interpreted.

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

---

## 2026-05-23 (later) — data-shoring + AM-vs-Fibonacci confluence test

### Integrity audit (audit_coordinates.py)
All 16 (then 18) coordinate files clean: no malformed JSON, no missing top-level keys,
no NaN/inf in any axes_computed. Every "partial-coverage" axis is correct
non-applicability (allen/kuramoto RF subset + `_I.5q_na_reason`; logistic/lorenz/
mackey-glass stable-regime cells carry only Family V). Family I in 13 files (absent
only from the q-banded/direct-only allen-np, kuramoto, pulsar); I.5q+rep in 11;
IV.2 box-dim was in 1 (now 2 with am-confluence). Confirms the proxy-bridge column
(I.5 where present, else I.5q) is the one axis spanning every substrate.

### L-zeros split (lzeros_split.py)
The pooled 8-cell `L-zeros` cell was internally bimodal; split by L-function class into
**L-zeros-zeta** (2, GUE: q=1.0, ρ=0.999, I.5=0.022), **L-zeros-dirichlet** (2,
Poisson-leaning: q=0, I.5=0.295), **L-zeros-ec** (4, q≈0.017, I.5=0.283). The
Poisson-leaning reading on Dirichlet/EC is carried with a CAVEAT (extraction_audit.
class_caveat): it is confounded by cross-conductor pooling — superposed independent
L-function spectra → Poisson regardless of each one's true symmetry class (Sp/U/SO all
repel). Flagged, not interpreted (phase34c / false_positive_equivalence_classes).
Both source pipelines (harvest q-banded leg, phase2b_arith matched leg) + the color/
list registries patched so a regen stays split. No recompute (relabel only).

### AM-vs-Fibonacci confluence test (am_confluence.py) — the strongest concrete prediction
Does the AM operator's fingerprint TRAJECTORY (λ-sweep at golden θ, through criticality
λ=1) pass through the Fibonacci Hamiltonian's fingerprint (D_box≈0.628, q≈0)?
INSTRUMENT-MATCHED to Fibonacci: D_box via box_dim on raw eigenvalues (Family IV,
instrument-independent — the axis Fibonacci is placed on) + Family I/II via the SAME
poly_unfold. Compares to sturmian-hamiltonian.jsonl, NOT am.jsonl (this is a separate,
Fibonacci-matched instrument, not the rotnum matched leg). Cheap: direct eigensolve
(O(N²) tridiagonal, 14s/φ @ N=50k), no O(N·L) rotnum unfold. 11 λ ∈ [0.5,1.5] @ N=50k
+ finite-N at λ∈{0.99,1.0,1.01}. Hedge first: D_box on banked AM-sub-golden eigs = 0.85
(off-critical baseline), vs Fib 0.628 — two-point contrast "doesn't match" as predicted.

**Trajectory (D_box, Fib ref 0.628):** a clean **V bottoming at criticality**:
λ=0.5→0.851, 0.7→0.770, 0.9→0.621, 0.95→0.565, 0.99→0.516, **1.0→0.513 (min)**,
1.05→0.553, 1.1→0.606, 1.3→0.726, 1.5→0.787. Near-symmetric about λ=1 (Aubry-André
self-duality λ↔1/λ: the 0.9↔1.11 dual pair reads 0.621 vs 0.606). q=0 across a WIDE
plateau (λ≈0.9–1.3), nonzero only at the extremes (λ=0.5 q=0.97, 1.5 q=0.19).

**Verdict candidates (FLAGGED — Will adjudicates):** Will's outcome (2),
**"bends nearby without quite reaching" — partial confluence; similar-but-distinct
operator families.** (a) Qualitative class DOES confluence at criticality: q→0,
W1δ→1.98, ks_gue→1.0, Cantor spectrum — fingerprint TYPE matches Fibonacci. (b)
Quantitative coincidence does NOT: AM-critical D_box≈0.513 OVERSHOOTS below Fib 0.628;
the trajectory crosses 0.628 only off-criticality (λ≈0.9, ≈1.1, positive-measure-Cantor
points), not at the zero-measure critical point. (c) Finite-N: critical D_box is
CONVERGED (0.513/0.513/0.514 @ N=50k/100k/200k) — not an artifact; ks_gue still drifts
up 0.93→1.0 (approaching the singular-continuous limit).

**Caveats to flag before any verdict:** (1) COUPLING CORRESPONDENCE — AM-critical is its
self-dual λ=1; the Fib ref is at *its* λ=2, and Fibonacci's D_box is itself
coupling-dependent, so the 0.513-vs-0.628 gap is partly a non-corresponding-coupling
comparison. A Fibonacci-λ-sweep would disentangle whether some Fib coupling matches
AM-crit's 0.51. (2) AM-crit D_box≈0.51 sits near the known ≈1/2 box-dimension for the
critical almost-Mathieu spectrum at golden flux — instrument reads real structure
(context, not a claim). Banked: coordinates/am-confluence.jsonl (15 cells); figure P5.

### Visuals consolidated (landscape_view.py + confluence_view.py)
P1–P4 refreshed with the L-zeros split; am-confluence excluded from P2 median scatter
(it's a trajectory, lives in P5). New: **P5** confluence (D_box-vs-λ V + repulsion-plane
trajectory) and **P6** unified bridged ks-GUE strip — every substrate on one axis
(matched I.5 ● where present, else q-banded I.5q ■ via the proxy verdict).

### Fibonacci-λ-sweep (fibonacci_lambda_run.py) — resolves the confluence coupling caveat
Follow-up to §3(g): sweep the Fibonacci/Sturmian-Ham coupling λ at α=golden (N=50k,
MATCHED to am_confluence — the banked Fib ref was N=8000, box_dim is resolution-sensitive),
asking whether some Fib coupling's D_box reaches AM-crit's 0.514.
**(1) N-mismatch cleared:** at λ=2, D_box=0.628/0.627/0.628 @ N=8k/50k/100k — N-stable, so
the banked 0.628 and the original AM-crit(0.513@50k)-vs-Fib(0.628@8k) comparison were sound.
**(2) The Fibonacci family REACHES AM-crit's fingerprint** — D_box decreases monotonically
with λ (0.25→0.927 … 2→0.628 … 8→0.369), crossing AM-crit 0.514 at **λ≈3.46** (interp
λ=3:0.546 → λ=4:0.475). And not just D_box: at the crossing the full Family-I fingerprint
coincides (AM-crit λ=1: W1δ=1.96/ks_gue=0.93/q=0/D_box=0.513; Fib λ≈3.5: W1δ≈1.96/ks_gue≈0.94/
q=0/D_box≈0.51). **⇒ the earlier "distinctness" was an artifact of comparing at
non-corresponding couplings (λ=2) — shifts §3(g) from outcome (2) toward outcome (1):
AM-critical IS a member of the Fibonacci fractal-Cantor family, reached at a stronger
Fibonacci coupling.** NUANCE TO FLAG: AM-crit is a SPECIAL point (self-dual, zero-measure,
phase transition); Fibonacci λ≈3.5 is GENERIC (Cantor ∀λ, no self-dual criticality) — same
fingerprint VALUE, different dynamical STATUS. Banked: fibonacci-lambda.jsonl (13 cells);
figure P7 (both D_box(λ) curves on one axis). Flag, not interpreted.

**VERDICT (Will, 2026-05-23):** confluence = **outcome (1)** — AM and Fibonacci confluence
at the fingerprint level; the routes differ (AM via phase transition, Fibonacci generic).
Dynamical-status difference is enrichment, not refutation. Two methodology lessons banked to
§4: (i) **matched-reference discipline** — sweep coupling-class parameters before declaring
distinctness (the λ=2 two-point test would have read "distinct" and missed the confluence);
(ii) **fingerprint blind-to-route** — the axes resolve spectral structure not dynamical-system
structure, so special-point vs generic Cantor is indistinguishable; mechanism is
under-determined by fingerprint alone (a feature for universality-class confluence, a limit on
mechanism inference).

### θ-class correspondence (theta_class_correspondence.py) — does AM↔Fibonacci generalize beyond golden?
AM-critical (λ=1, self-dual — θ-independent) vs Fibonacci-α D_box(λ) per Lagrange class, N=50k,
8φ, same instrument. **CONFLUENCE GENERALIZES ACROSS THE QUADRATIC (metallic-mean) CLASSES:**
golden (AM-crit 0.513, λ*=3.42), silver (0.520, λ*=3.32), bronze (0.511, λ*=3.41) — all three
confluence at nearly identical coupling λ*≈3.3–3.4. ⇒ **golden is NOT uniquely special among the
metallic means; the correspondence is a bounded-CF (Diophantine) family property** — strongest
operator-IS-substrate state for that family (AM ≡ Fibonacci up to parameterization across quadratics).
Golden λ*=3.42 here vs 3.46 (dedicated sweep) — consistent within grid resolution.

**Two sub-findings (flagged):** (1) **AM-critical D_box is class-INVARIANT among quadratics (~0.51)**
— sharp contrast to the AM-SUP-θ Brody stratification (golden 0.81→silver 0.44→Liouville 0.28).
Criticality WASHES OUT the θ-class sensitivity the localized (sup) regime shows; the self-dual
critical point is more universal (consistent with the ≈½ universal critical-AM box-dim). (2)
**Liouville is the boundary, but N-AMBIGUOUS not a clean break:** AM-crit-Liouville 0.491 vs
Fibonacci-Liouville floor 0.530 (no crossing in the λ≤8 grid). BUT Liouville's unbounded CF quotients
make box_dim finite-N-fragile, and neither Liouville value is N-converged (unlike golden's 50k–200k
stability). Honest read: Diophantine confluence robust; Liouville UNRESOLVED pending an N-convergence
check — would disentangle "correspondence is bounded-CF-only" from "N=50k under-resolves Liouville".
Banked: am-confluence-theta.jsonl (4) + fibonacci-lambda-theta.jsonl (44); figure P8. Flag, not interpreted.

### Liouville N-convergence check (liouville_nconv.py) — RESOLVED: confluence is universal across Lagrange classes
Disambiguating §3(h)'s Liouville ambiguity by pushing both legs to higher N. **Both N-converge:**
AM-crit-Liouville (λ=1) D_box = 0.491/0.491/0.490 @ N=50k/100k/200k (rock-stable); Fibonacci-Liouville
λ=8 = 0.530/0.533/0.534 @ 50k/100k/200k (floor flat — N is NOT the lever). **Extending λ instead:**
Fib-Liouville D_box continues down (λ10→0.500, λ12→0.471, λ16→0.453), CROSSING AM-crit's converged 0.490
at **λ*≈10.7**. ⇒ outcome (B)-via-λ: the earlier "no crossing" was a λ-RANGE artifact (λ≤8), NOT
N-limited and NOT a class boundary. **Confluence is UNIVERSAL across all tested Lagrange classes**
(golden/silver/bronze/Liouville); Liouville is not outside the universality class.
**Refined finding (sharper than bounded-CF-only):** the matching coupling λ* STRATIFIES by Diophantine
class — α-invariant ~3.4 within the metallic means, jumping to ~10.7 for super-approximable Liouville.
AM↔Fibonacci is the same operator family across the whole Lagrange spectrum via an α-dependent
reparametrization (flat within metallic means, much larger for Liouville). The Lagrange signature lives
in the COUPLING-CORRESPONDENCE, not in whether confluence occurs. Mechanistically consistent (flagged):
Liouville's long near-periodic stretches make its Sturmian spectrum more band-like at given λ → needs
stronger coupling to fractalize to AM-crit's 0.49. Banked: liouville-nconv.jsonl (8 cells); figure P9.

### λ*(class): step or continuum? (lambda_star_classes.py + lambda_star_nconv.py) — CONTINUOUS APPROXIMABILITY STRATIFICATION
Mapping the AM↔Fibonacci matching coupling λ* across 9 Lagrange classes resolves what λ* tracks.
λ* @N=50k (unbounded-CF cells N-confirmed @100k, drift <0.1): golden 3.42, silver 3.32, bronze 3.41,
metallic4 4.20, metallic5 4.98, e−2 3.78, ln2 3.81, π−3 7.73, Liouville ~10.7.
**Refutes BOTH binary extremes:** (1) NOT a step at CF-boundedness — **e** (μ=2, UNbounded CF) lands at
λ*=3.78, with the metallic means, not Liouville (the discriminator; N-confirmed). (2) NOT pure-μ — at
fixed μ=2, λ* spreads 3.32 (silver) → 4.98 (metallic5) with CF-quotient magnitude. **Synthesis (Will's
verdict): continuous APPROXIMABILITY stratification, single universality class.** λ* tracks how well α
is approximated by rationals (combining CF-quotient size AND μ): most-Diophantine classes (small-quotient
metallic means + e, slow-growing quotients) floor at λ*≈3.3–3.8; λ* rises continuously through ln2/
metallic5/π to Liouville's ~10.7. The metallic-mean cluster and Liouville are endpoints of an
approximability continuum, NOT two CF-boundedness classes.

**Two distinct claims:** (1) **AM-crit D_box is approximability-INVARIANT** — stays in [0.49,0.53] (~½)
across all 9 classes; AM-criticality is genuinely universal in the Bellissard sense across this space.
Consistent with Jitomirskaya-Krasovsky (D ≤ ½ theorem) and Wilkinson-Austin 1994 (~½ numerical conjecture).
(2) **Fibonacci-Hamiltonian λ-Cantor-curve is approximability-GRADED** — more-approximable α needs more
coupling to fractalize its spectrum to the same D_box (high approximability ≈ "almost rational", and
Fibonacci at rational α → AC band, so stronger coupling needed to push into Cantor). The variation lives
entirely on the Fibonacci side. **Connects to Damanik-Gorodetski 2014 / Cao-Qu 2023** (a.e.-frequency
Hausdorff-dim constancy at large coupling): our finding empirically CONFIRMS the asymptotic constancy AND
characterizes the approach to it — more-approximable (measure-zero) α need higher λ to reach the
asymptotic regime; metallic means reach it sooner. A convergence-rate extension of the constancy theorem.
Banked: lambda-star-classes.jsonl (108) + lambda-star-nconv.jsonl (9); figure P10. Flag, not interpreted.

### Dimension-theory cross-check vs DEGT (dimension_theory_check.py + trace_map_dimension.py) — PARTIAL, constant DEFERRED
Quantitative test of §3(j)↔DG/Cao-Qu: does Fibonacci dim(Σ_λ)·ln(λ) → ln(1+√2)≈0.8814 (golden;
Damanik-Embree-Gorodetski-Tcheremchantsev CMP 2008)? **Form confirmed, constant deferred.**
- D~C/ln(λ) FORM holds (R²≈0.98, moderate λ).
- Built an EXACT band-edge instrument (band edges = periodic/antiperiodic eigenvalues of the period-q
  approximant — grid-free, resolves all q bands at any λ, unlike eigenvalue box-counting which breaks at
  large-λ cluster-splitting + finite-N). VALIDATED vs box_dim at λ=8 (band-pressure 0.370 vs box 0.369);
  dim·ln(λ) climbs into the 0.77–0.84 neighborhood of 0.8814.
- BUT the single-level Bowen pressure Σ|band|^d=1 is NOT scale-invariant (absolute widths) → diverges
  with q/λ: golden dim·ln(λ) → 1.72 at λ=1024, extrapolated C=2.12 (artifact); q-convergence at λ=64
  climbs 0.82→0.98 (q=377→1597), not stabilizing. Box-counting separately breaks at cluster-splitting.
- DIAGNOSIS: a self-similar-Cantor dimension needs the scale-invariant Moran equation Σrᵢ^d=1 on
  renormalization CONTRACTION RATIOS — the trace-map thermodynamic formalism — not absolute band widths.
  A dedicated future arc. Both accessible quick estimators (box-counting at resolution; single-level
  band-pressure at scale-invariance) can verify the FORM but not the asymptotic CONSTANT.
- METHODOLOGY (§4): "looked right at moderate scales" ≠ "correct asymptotically" — validate an
  estimator's scale/size-convergence (q-convergence, scale-invariance) before trusting an extrapolated
  asymptotic constant. No valid P11 banked (broken extrapolations excluded). Flag, not interpreted.

---

## 2026-05-24 — Allen Brain Observatory depth-extension (Tier-1 neuro pivot)

Scaled Phase-2a (719 V1 cells, drifting gratings) to the full cached corpus: 12 sessions × 6
visual areas (V1/LM/RL/AL/PM/AM) + LGN × 8 stimulus blocks → **60,833 (cell,stimulus) records,
8,462 cells**, I.5q + matched I.5 + W1δ each, tagged area + tuning. No download (cached NWBs,
h5py-direct). classify worker-knee = 14 (compute-bound; the bandwidth-bound "10" default did NOT
apply — workload-specific recalibration). All findings FLAGGED (verdicts Will's).

**(1) H1 OSI↔ks_gue GENERALIZES across all visual areas.** ρ(OSI, I.5q)/ρ(OSI, I.5) per area
(drifting gratings): V1 0.46/0.48 (p=2.5e-118), LM 0.43, RL 0.39, AL 0.43, PM 0.44, AM 0.44 — all
p≪1e-30; LGN (thalamus) weaker 0.27 (p=6.6e-9). ⇒ H1 is a GENERAL mouse visual-cortex property,
not V1-specific — the cross-area generality complementing the cross-species (monkey+mouse) result.

**(2) Tuning-dim privilege — orientation-domain, not frequency-domain.** Pooled V1+higher visual,
ρ(tuning, I.5q): OSI +0.44, DSI +0.42, f1_f0 +0.32 (all p≈0) — but pref_sf +0.05, pref_tf −0.04
(≈NULL), run_mod +0.14. ⇒ orientation/direction selectivity (+F1/F0) couple to the universality
class; spatial/temporal-frequency tuning does NOT. OSI is not uniquely privileged (DSI ≈ equal).

**(3) Family VII at scale — WEAK-but-significant in mouse (refines "absent").** |I.5q−I.5| vs OSI
per area ρ = 0.08–0.18 (V1 0.098 p=3.8e-6; all areas p<0.005 at large n). NOT zero — the 12× sample
revealed a weak grading — but far below pvc-11's ρ≈0.47. ⇒ Family VII is monkey-STRONG / mouse-WEAK,
not monkey-only. (Candidate explanations: species / state / tech / sampling-geometry — see below.)

**(4) Cross-area landscape — tight visual-cortex cluster.** Per-area median I.5q 0.42–0.47, W1δ
0.95–1.03 — areas cluster together as "visual cortex," NOT separated by functional role; LGN
marginally more GUE-like (0.42) — a gentle thalamus-vs-cortex offset, not a sharp split.

**(5) Within-cell stimulus-state IS a live axis.** A fixed cell's I.5q shifts substantially with
stimulus: within-cell spread median 0.169, p90 0.299. Per-stimulus median I.5q: natural movies /
spontaneous most GUE-FAR (0.48), flashes most GUE-NEAR (0.36), gratings/scenes mid. ⇒ universality
class is stimulus-state-dependent within a fixed cell — a new (state) axis beyond across-area / across-tuning.

**(6) Spatial structure (allen_depth_spatial.py; position joined unit→channel, no recompute).**
- DEPTH (probe_vertical proxy; ecephys has NO clean layer label): only a WEAK gradient (ρ≈−0.06 to
  −0.09; superficial marginally more GUE-like), depth-bin medians differ ~0.02 — largely depth-invariant.
- SPATIAL DECORRELATION: ρ(CCF-distance, |ΔI.5q|) ≈ 0 in every area (−0.03…+0.02, mostly n.s.) — NO
  spatial autocorrelation within ~1 mm; the fingerprint is a per-cell property, not spatially clustered.
- SAMPLING GEOMETRY (4th Family-VII candidate, refined): with full CCF, Allen samples ~1 mm³/area
  (multi-probe → ~1 mm lateral, NOT 0). So it's "Allen ~1 mm sparse multi-probe all-layers" vs
  "pvc-11 Utah ~4 mm dense 2D L2/3" — candidate stands but is lateral-extent + density + layer-coverage,
  not a crude 1D-vs-2D. (Banked alongside species / state / recording-tech as Family-VII-split candidates.)

### Allen depth-extension — Family II (long-range) + avalanche criticality cross-references

**Family II (allen_fam2_analysis.py; Σ²/Δ₃/K on the matched unfold, 60,833 records).**
- **Δ₃ (spectral rigidity) carries an OSI signal** (ρ=0.240), Σ² weaker (0.094), K(τ=1) 0.076 — the
  phase-coupling hook is a PARTIAL yes (long-range rigidity, esp. Δ₃, couples to orientation tuning).
- **Family II is partially-distinct from Family I**: ρ(Σ², I.5q)=0.505, ρ(Δ₃, I.5q)=0.578 (~25–33%
  shared variance — not redundant), and **K(τ=1) is nearly independent** of I.5q (0.128) — a distinct axis.
- **Strong within-cell stimulus-state dependence on the long-range axis**: median Σ² spontaneous 286 →
  natural movies ~200 → static gratings 143 → flashes 12. (Even sharper than Family I's state axis;
  brief sparse stimuli carry little long-range structure.) Per-area Σ²/Δ₃ differ mildly; LGN lowest Δ₃.

**Avalanche criticality (allen_avalanche.py; Beggs-Plenz, per session × {spontaneous, drifting
gratings}).** Pooled target-area population spikes, binned at population mean-ISI; size/duration
power-laws + crackling relation. **All 12 sessions near-critical and remarkably stable**: τ≈1.90–1.94
(size), α≈2.18–2.25 (duration), empirical crackling exponent ≈1.16–1.28 vs predicted (α−1)/(τ−1)≈1.32–1.33,
|Δ_crackling|≈0.04–0.16. Replicates the cortical-avalanche literature's exponents; spontaneous ≈
drifting-gratings. **CROSS-REFERENCE NULL**: ρ(|Δ_crackling|, med I.5q)=−0.035 (p=0.91, n=12),
ρ(|Δ_crackling|, W1δ)=−0.11 (p=0.73) — population avalanche-criticality does NOT track the per-cell
fingerprint. Underpowered (n=12, narrow |Δ| range — all sessions similarly near-critical), BUT the
qualitative read stands: **population avalanche-criticality and per-cell universality-class are
ORTHOGONAL levels** — population-collective structure is a distinct substrate from per-cell spacing
class, not recovered by per-cell Family II. (Flag; verdicts Will's.)

### Calibration anchors + population-level fingerprints (2026-05-24, post-adjudication)

**Calibration anchors (calibration_anchors.py) — explicit landscape corners + instrument re-validation.**
Canonical classes generated (calibrator zoo: β-ensemble eigenvalues, Poisson, clock, uniform-jitter),
N=3000, 6-seed mean, SAME instrument as substrates. Validates: GUE_b2 → I.5q=0.033, q=1.00, ρ=0.999;
GOE_b1 → I.5q=0.094, q=0.876; GSE_b4 → q=1.00; clock → W1δ=0.000, Σ²=0.000; uniform_jitter → q=1.0,
Σ²=0.12 (BR-regime); Poisson → q=0.006, ρ=0.093, W1δ=0.736. The corners are now explicit reference
points (coordinates/calibration-anchors.jsonl) — clean baseline for every substrate. (Instrument re-validated:
GUE→q≈1, Poisson→q≈0, clock→W1δ≈0.)

**Population-level fingerprints (population_fingerprint.py) — §7(h) follow-up. FRAGMENT by aggregation.**
One session (732592105) × {spontaneous, drifting_gratings}, 4 population observables fingerprinted.
**Population-level fingerprints do NOT form a coherent landscape position — they fragment by aggregation
choice (consistently across both blocks; aggregation, not stimulus, is the determining variable):**
- **corr-eig** (pairwise correlation-matrix bulk eigenvalue NNS — the principled spectral observable,
  no extractor): I.5q≈0.07, q≈0.91–0.96, ρ≈0.997 → **GUE** (empirical-covariance bulk is Wigner; RMT-standard).
- **avl-onset** (avalanche onset times, point process): I.5q≈0.24, q≈0.59 → intermediate.
- **sync-event** (population-rate threshold-upcrossing times): I.5q≈0.55, q=0.000, ρ=0.001 → **Poisson**
  (network-event timing is clustered).
- **rate-peak** (find_peaks on smoothed population rate): q=1.000 → Wigner, but this is the §7.ter.19
  find_peaks autocorrelation-rhythm ARTIFACT (flagged; a within-study control — behaves exactly as the
  known failure mode, NOT a real population property).
**Reading (flag):** there is no single "population fingerprint." The population's CORRELATION structure
→ GUE, its EVENT TIMING → Poisson-ish, naive peak-extraction → artifact — genuinely different observables,
each landing where its nature dictates. Sharpens §7(h): population-level is a FAMILY of mutually-disagreeing
observables, and "which aggregate" picks the universality class. The principled spectral choice (corr-eig)
is GUE. Per-cell fingerprints cohere (visual-cortex cluster, §7d); population fingerprints do not.
Banked: coordinates/population-fingerprint.jsonl (8). Verdicts Will's.

---

## 2026-05-24 — brocot.fm: the cross-substrate approximability BRIDGE TEST

brocot.fm = a Stern-Brocot/Bessel-structured multi-modulator FM synthesizer (codeberg.org/combust/brocot,
fmexplorer/brocot). Spectral side = analytic Bessel-sideband partial spectrum (phase3/partial_prediction.
predict_partials — NO audio, no extractor artifact); parameter side = Stern-Brocot path → ratio. The one
substrate where BOTH sides are directly accessible. ARS toolkit vendored at phase3/ars/.

**DESIGN-VALIDATION PROBE (synthetic-validate-the-design).** Candidate walk designs tested on golden/
silver/Liouville: a single modulator at a rational ratio is a regular comb → clock NNS; the CONVERGENT
sequence (rational approximations) → combs, NO class separation. The approximability signal lives in the
IRRATIONAL-α quasi-periodic partial set {m+nα} (carrier-comb [ratio 1] × modulator at irrational target
α). FM modulation DEPTH is the coupling analogue (higher depth sharpens separation, like AM λ). So the
test reframed (cleaner than the convergent-walk): a DEPTH-SWEEP at fixed irrational-α targets — directly
parallel to the AM/Fibonacci λ-sweep, parameter accessed DIRECTLY (ratio IS α, no operator indirection).

**HEADLINE RESULT (brocot_approximability.py; 9 Lagrange classes × 7 depths).** brocot.fm — a third,
mechanistically-DIFFERENT substrate (FM synthesis, not a Schrödinger operator) — shows the SAME
approximability stratification as AM/Fibonacci. Endpoint (depth=8) Brody q ordered by approximability:
metallic means golden/silver/bronze/metallic4/5 (μ=2) → q≈0.91–1.0 (GUE/repulsive); e−2, ln2 → q≈0.52–0.57;
π−3 (μ=7.1), Liouville → q=0.000 (Poisson). **ρ(approximability-rank, Brody q) = −0.909.** Depth sharpens
(I=2→8 drives Liouville/π q→0). ⇒ **approximability stratification is a substrate-CLASS property that
transcends operator family** (Will's "if yes" outcome). Both AM↔Fib claims hold: metallic means share a
"Diophantine GUE corner" (universal-ish), approximable classes grade away (graded).

**NUANCE — a real cross-substrate DIFFERENCE (flag).** brocot's Brody q looks like a bounded-vs-unbounded-CF
STEP: e−2 (μ=2 but unbounded CF) drops to q=0.57 with the unbounded group, while ALL metallic means (incl.
large-quotient metallic4/5) stay q≈1. This DIFFERS from the λ*(class) study (ec82368), where e grouped WITH
the metallic means and quotient-magnitude separated them (continuous-in-approximability). So the substrates
AGREE on the gross stratification (ρ=−0.91) but DIFFER on the fine discriminator — brocot ≈ CF-boundedness
step, AM/Fibonacci ≈ continuous approximability. (Possibly because brocot's Brody q vs the λ*-via-D_box
metric read different facets.) Figure P_brocot_approx.png. I.5q (q-banded) N/A for brocot — joint_q_profile's
integer-time-bin q-banding doesn't suit wide-Hz partials; plain Family-I leg carries it. Verdicts Will's.

### brocot.fm landscape placement (brocot_landscape.py) — deliverable 1
Fingerprinted the full phase3 pull_index corpus: 4,292 exemplars × 33 musical-family categories
(4,006 with NNS Family I), partial-frequency NNS + RF per-prime, partials from predict_partials.
**brocot.fm places as a spectral-DENSITY-ordered substrate spanning the GUE↔Poisson axis:** sparse-
harmonic families at the GUE/repulsive corner (Prime-2 q=1.0, Truax/first-principles q=1.0, Triangle
0.86, Prime-3 0.78), dense "Textured-Smooth" carpets at the Poisson/clustered corner (q≈0.12–0.29).
Σ² grows with op-count (4→64 ops: 0→302 — denser carpets carry more long-range structure). **NEGATIVE
(flag):** the RF per-prime leg is p2-SATURATED across all families (0.21–0.51) — the search's "Prime-p"
families (defined via KL + RF characteristic_q) do NOT translate to clean p-adic RF dominance on the
ARS-predicted partials (Prime-3 still p2-dominant 0.329, p3 0.051). The discriminating leg is NNS
Brody q, not RF-per-prime. Banked: coordinates/brocot-landscape.jsonl. Verdicts Will's.

### Population-level fingerprints × all 12 Allen sessions (population_fingerprint.py --all) — fragmentation CONFIRMED CONSISTENT
Extended the §7(h) 1-session pilot to all 12 sessions × 4 aggregations × 2 blocks (96 records). The
fragmentation-by-aggregation is HIGHLY CONSISTENT across the corpus (n=24 per aggregation, both blocks):
corr-eig (correlation-matrix bulk eigenvalues, principled spectral) → Brody q=0.952±0.052, I.5=0.083±0.012
(GUE); avl-onset → q=0.664±0.075 (intermediate); sync-event → q=0.000±0.000 (Poisson — EXACTLY zero in all
24, no variance); rate-peak (find_peaks) → q=1.000±0.039 (the §7.ter.19 artifact). Within-aggregation std
is tiny (0.04–0.08) while between-aggregation separation spans the full q∈[0,1]. ⇒ **the aggregation choice,
NOT the session/area, determines the universality class** — each population observable has a fixed, robust
landscape position. Firms §7(h) at scale: no single "population fingerprint"; population-level is a family
of mutually-disagreeing observables, and which observable you pick (not which recording) sets the class.
Banked: coordinates/population-fingerprint-all.jsonl (96). Verdicts Will's.

**Artifact checks on the two suspected population observables (Will's flags, induction-on-noise discipline):**
- **sync-event q=0 is REAL Poisson, not a Brody-boundary clip.** All 4 metrics corroborate: I.5=0.554
  (far-GUE), W1δ=1.115 (clustered, > Poisson's 0.74), BR ρ=0.001, Brody q=0.000. The position is genuine
  (synchrony-event times Poisson-to-clustered). KEEP as a trustable observable.
- **rate-peak q=1 is a CONFIRMED extractor artifact.** Induction-on-noise: a rate-matched Poisson
  SURROGATE population, fed through the same rate-peak (find_peaks) extractor, gives Brody q=1.000 (vs
  real 0.996) — Wigner manufactured from known-Poisson input (§7.ter.19 peak-spacing-regularity). DROP /
  document as the artifact control.
⇒ THREE trustable population observables, spanning the full axis: **corr-eig→GUE, avl-onset→intermediate,
sync-event→Poisson** — all real, all distinct. The cross-substrate landscape gains 3 population positions
(+ rate-peak as the documented artifact control). Refines §7(h): population-level is a family of
mutually-disagreeing observables, and even after removing the one artifact, ≥3 real positions remain —
each population observable IS its own substrate, not a measurement of "the" population.

### Quasi-periodic operator family — approximability stratification extends to 5 operators (quasiperiodic_operators.py)
Tested whether the AM↔Fibonacci↔brocot approximability axis extends across the broader quasi-periodic-operator
family: 4 operators × 9 Lagrange classes × 6 couplings, N=50k, D_box discriminator. (Brody q is 0 at strong
coupling — washed out; D_box at the CRITICAL coupling is the discriminator, as in AM-confluence.)
Per-operator ρ(approximability-rank, D_box) at max-spread coupling:
- **gaah (generalized-AAH, mobility edge): ρ=−0.717** @λ=1 (D_box golden 0.81 → Liouville 0.69) — JOINS.
- **ext_harper (extended-Harper, self-dual line): ρ=−0.700** @λ=1 (golden 0.79 → Liouville 0.65) — JOINS.
- **maryland (always-pure-point): ρ=+0.250, λ-INVARIANT flat** (~0.47–0.50) — clean NEGATIVE CONTROL (no
  critical regime → no θ-stratification, as predicted).
- **mosaic-AM: ρ=+0.267, weak/non-monotone** — does NOT cleanly stratify (a real negative).
**⇒ the approximability axis extends from 3 → 5 substrates (+gaah, +ext_harper); it's a quasi-periodic-
operator-CLASS property, CONDITIONED on a critical/fractal regime** (where the Cantor dimension is
θ-sensitive). NOT universal: always-localized (maryland) and mosaic (in-range) don't show it.
**Fine-structure generalizes "agree-gross-diverge-fine":** gaah/ext_harper show the metallic4/5
quotient-magnitude dip and e-stays-high-with-small-quotient-metallics — matching the λ*(class)
CONTINUOUS-approximability fine structure, NOT brocot's CF-boundedness step. So the quasi-periodic-OPERATOR
family (AM/Fib/gaah/ext_harper) agrees on fine structure; brocot (FM synthesis) is the fine-structure
outlier. Gross-axis agreement across all 5+brocot; fine-structure splits operators-vs-brocot.
Banked: coordinates/quasiperiodic-operators.jsonl (216); figure P_qpo_approx.png. Verdicts Will's.

### Dynamical-substrate breadth (Job 3, dynamical_breadth.py) — Family-V landscape extended to 7 systems
Added Rössler/Chua/Duffing (3-D flows) + Hénon (2-D map), each a bifurcation-sweep trajectory placed by
Family V (λ₁ tangent-space Benettin + D₂ Grassberger-Procaccia) + event-NNS (median-upcrossing transitions,
not find_peaks). All give clean chaos-ordered trajectories, validated vs known: Rössler c=8.5–12 chaotic
(λ≈0.09, D₂≈1.9), period windows at c=4/6/18; Chua α=15.6 double-scroll (λ=0.42, D₂=2.77); Duffing γ=0.3 &
0.5 chaotic (λ≈0.07), γ=0.37 = the known periodic window (λ<0); Hénon period-doubling a=1.06→1.4 (λ 0.05→0.42,
D₂→1.21, matches known 0.42/1.26). λ via Benettin matches known values precisely. ⇒ Family-V dynamical
landscape now 7 substrates (MG/Lorenz/logistic + these 4). Event-NNS Brody q≈1 throughout (oscillatory-event
regularity — secondary axis). Banked: coordinates/dynamical-breadth.jsonl (17). Verdicts Will's.

### QPO deepening (quasiperiodic_deepening.py) — gaah/ext_harper stratification firmed (robust + N-stable)
Deepened the two operators that joined the approximability family (Job 1). (a) FINE coupling grid λ∈[0.6,1.4]:
ρ(rank,D_box) stays negative throughout — gaah −0.55…−0.78 (spread peaks ~λ=0.8), ext_harper −0.30…−0.83
(strongest λ=0.8, spread peaks λ=1.0–1.2). Stratification is ROBUST across the critical regime, not a
knife-edge. (b) N-CONVERGENCE @λ=1 (50k→100k): gaah ρ=−0.717→−0.717 (identical), ext_harper −0.700→−0.783;
golden/Liouville D_box move <0.002 — D_box N-STABLE, ρ stable/strengthening. ⇒ the stratification is
N-robust (NOT a finite-N artifact); gaah & ext_harper firmly in the approximability-stratification family.
The 3→5 substrate extension is solid. Banked: coordinates/quasiperiodic-deepening.jsonl (180); fig P_qpo_deepening. Verdicts Will's.

### CF-mechanism test (cf_mechanism.py) — WHY brocot steps but operators are continuous: e splits them
The open mechanism question from the brocot bridge + λ*(class) arcs: brocot's fine discriminator is a
bounded-vs-unbounded-CF STEP, but the operators' (AM/Fib/gaah/ext_harper) is CONTINUOUS in μ — why? Two-
mechanism hypothesis: brocot NNS = three-distance-theorem gap statistics of {nα mod 1} (responds to a LOCAL
CF property), operator D_box = trace-map-integrated transfer-matrix cocycle (responds to GLOBAL μ). **The
discriminator is e−2: transcendental/unbounded CF, but μ=2 like the metallic means — the two predictors
DISAGREE on it.** Result (9 Lagrange classes; brocot endpoint Brody q vs gaah+ext_harper D_box @λ=1):
- **(1) brocot Brody q STEPS on the CF-structure binary** (bounded/quadratic vs transcendental/unbounded):
  bounded/quadratic mean=0.982 (n=5: golden/silver/bronze/metallic4/5 all ≈1.0) vs transcendental/unbounded
  mean=0.271 (n=4: e/ln2 partial-drop, π/liou→0). Δ=+0.711. NOT maxQ-magnitude (metallic5 maxQ=5 stays 1.0,
  e maxQ=4 drops) — it's the bounded/quadratic-CF vs transcendental Lagrange dichotomy.
- **(2) operator D_box is CONTINUOUS in μ** (GLOBAL): ρ(D_box, μ)=−0.634 monotone golden→liouville.
- **(3) DISCRIMINATOR e−2 splits them:** brocot q(e)=0.568 DROPS (with the transcendentals, NOT μ);
  operator D_box(e)=0.782 STAYS HIGH (with golden, μ=2, NOT CF-structure). The same number lands on
  opposite sides of the two fingerprints — exactly as the two mechanisms predict.
**⇒ MECHANISM CONFIRMED (the WHY, not just the THAT): brocot Brody q follows the three-distance / LOCAL /
bounded-quadratic-CF STEP (periodic CF ⇒ self-similar balanced {nα} gaps ⇒ repulsive; non-periodic ⇒
degenerate ⇒ clustered); operator D_box follows μ CONTINUOUSLY (trace-map integrates the whole CF
sequence). e is the discriminator that makes it mechanistic, not just descriptive.**
CAVEAT (flagged): boundedness & quadraticity are confounded for natural α (quadratic ⟺ periodic ⟺ bounded;
no unbounded-quadratic exists, bounded-transcendentals are exotic) — so the brocot trigger is "the Lagrange
bounded/quadratic dichotomy," which I can't decompose further with accessible classes. Distinct from μ
either way (e proves it). The exact LOCAL statistic (maxQ) is an imperfect proxy (metallic5 maxQ=5 stays
because it's bounded-periodic; the trigger is structure, not magnitude). Banked: figure P_cf_mechanism.png
(brocot STEPS on CF-structure binary | operator CONTINUOUS in μ; e in red on opposite sides). Verdicts Will's.

### CF-discriminator (cf_discriminator.py) — brocot reads BOUNDEDNESS, not quadraticity (confound decomposed)
cf_mechanism flagged one confound: for natural α, "bounded" (small partial quotients) and "quadratic"
(eventually-periodic CF / Lagrange class) coincide, so "brocot follows the bounded/quadratic dichotomy" hid
two claims. THE CONTROLLED EXPERIMENT: hold the CF quotient ALPHABET fixed at {1,2} (boundedness & μ=2
IDENTICAL) and vary ONLY periodicity — periodic_12=[0;1,2,1,2,…] (bounded QUADRATIC, =√3−1) vs
thue_morse_12 & fib_word_12 (bounded NON-quadratic: TM/Fibonacci-word quotient sequences, non-periodic ⇒
not quadratic by Lagrange). All three: maxQ=2, μ=2, near-identical convergent growth; differ ONLY in CF
periodicity. Result (endpoint brocot Brody q + gaah/ext_harper D_box @λ=1, 7 targets):
- **brocot DISCRIMINATOR:** bounded-NONquadratic tests thue_morse_12 q=1.000 & fib_word_12 q=1.000 land
  WITH the bounded-quadratic anchor (golden/silver/periodic_12 mean=0.969), FAR from the unbounded-
  nonquadratic anchor (e/liouville mean=0.284; midpoint 0.627). ⇒ flipping periodicity (alphabet held)
  left brocot q UNCHANGED — periodicity is INVISIBLE to brocot.
- **operator CONTROL:** all bounded targets (μ=2) D_box=0.785±0.016 (tight, flat across periodicity) vs
  liouville 0.675 — operators read μ and are BLIND to this split (mirror of the e-discriminator: e split
  CF-structure from μ; periodicity splits boundedness from quadraticity, and operators ignore both).
**⇒ THE BROCOT TRIGGER IS BOUNDEDNESS OF PARTIAL QUOTIENTS (the badly-approximable / Diophantine class),
NOT the algebraic quadratic class.** Decomposes the cf_mechanism caveat: it's quotient MAGNITUDE/growth
(three-distance: bounded quotients ⇒ controlled convergent-denominator growth ⇒ balanced {nα} gaps ⇒
repulsion; a large quotient ⇒ one very-good convergent ⇒ near-degenerate gap ⇒ clustering), and CF
periodicity is irrelevant. This is the three-distance theorem's exact prediction, now confirmed by a
designed-α second discriminator. Caveat now RESOLVED, not just flagged.
NOTE (honesty): the two bounded-nonquadratic tests returned identical q to 16 digits (0.99993) — the Brody
fit saturating its q→1 repulsive ceiling, not a coincidence; both sit unambiguously on the bounded side
regardless. Banked: coordinates/cf-discriminator.jsonl (7); figure P_cf_discriminator.png. Verdicts Will's.

### Axis-vs-substrate clarification (banked-data interrogation, no new script) — observable-binding
Raised after cf_discriminator: was the cf_mechanism "brocot-step vs operator-continuous" split an arbitrary
AXIS-selection confound (brocot read on short-range Brody q, operators on global box-dim)? Tested by trying
to fill the 2×2 from banked data + a Σ²(L) robustness recompute. The two OFF-DIAGONAL cells turn out to be
INTRINSICALLY uninformative — and WHY is the answer:

                | short-range NNS (Brody q)        | global (box-dim / long-range)
  brocot        | reads BOUNDEDNESS (clean, ρ=0.91)| comb-dominated NOISE (~344 deterministic FM sidebands;
                |                                  |   Σ²(L) non-robust, sign-flips across L=3..12)
  operators     | Cantor-DEGENERATE (q≈0 every     | reads μ (clean, ρ=−0.63)
                |   class, every coupling 0.5–4)    |

⇒ VERDICT: SUBSTRATE-TYPE-GROUNDED, not an axis artifact. The diagonals hold the substrate-appropriate
observables; the off-diagonals are uninformative BECAUSE the spectral TYPES don't support the cross-
observable — point-process substrates (brocot partials, RMT-class) have NO fractal for box-dim to measure;
Cantor-set substrates (quasiperiodic-operator spectra) have hierarchical clustering that DEGENERATES NNS.
You literally cannot read brocot on the operators' axis or vice-versa — spectral type FORCES the observable.
The headline split SURVIVES the challenge and gains a sharper reason.

**Two-layer landscape architecture (this clarification + the dynamical-breadth arc say the same thing):**
  (L1) Different substrate CLASSES need different observable FAMILIES — Family V (λ₁/D₂) for dynamical
       systems vs Family I–III (NNS/Σ²/RF) for spectral substrates (the Rössler/Hénon/Chua/Duffing finding:
       point-process axes didn't discriminate them; their native λ/D₂ did).
  (L2) WITHIN an observable family, different substrate spectral TYPES afford different specific observables
       — NNS Brody q for point-process spectra, box-dim for Cantor spectra (THIS clarification).
  Both layers: SUBSTRATE TYPE FORCES OBSERVABLE. Cross-substrate findings live in whichever observable each
  type affords; the SHARED finding is the underlying axis (here approximability) that both observables expose
  through their substrate-appropriate readings.

**Honest caveat, stated as part of the finding:** the boundedness-STEP (brocot) and μ-CONTINUUM (operators)
are partly OBSERVABLE-BOUND — boundedness is what NNS sees, μ is what box-dim sees. The mechanism story
holds (three-distance for NNS, trace-map for box-dim), but the empirical distinction is observable-binding-
aware. This framing makes the landscape STRONGER: it explains why one axis manifests differently across
substrates without inviting either the "trivial axis-confound" critique OR overclaiming substrate-independent
universality. Banked as clarification (the 2×2 table is the durable artifact). Verdicts Will's.

### Stratified population fingerprints (population_strat.py / _analysis.py) — Step-2 neural arc
Stratified the 3 trustable population observables (corr-eig / avl-onset / sync-event; rate-peak artifact
dropped) across 8 stimulus blocks × 7 areas × 12 sessions = 1,456 cells (parallel, 10 workers, 11 min),
then asked what STRUCTURES the population landscape position.

- **(0) FRAGMENTATION IS ROBUST, NOT A POOLING ARTIFACT.** corr-eig q=0.892±0.112, avl-onset q=0.608±0.135,
  sync-event q=0.002±0.015; the canonical ordering corr-eig>avl>sync holds in 449/478 (94%) of
  fully-populated (session,area,block) cells. The three observables occupy distinct, stable bands within
  EVERY stratified cell ⇒ population fragmentation is intrinsic to the observable, not an artifact of
  aggregating across areas/stimuli. Confirms + sharpens the prior 12-session whole-population finding.
- **(1) EACH OBSERVABLE IS KEYED TO A DIFFERENT FACTOR (marginal η² on Brody q):**
    corr-eig:  area 0.03 / stim 0.05 / session 0.05 — NEAR-INVARIANT (stably ~GUE everywhere; a robust
               population spectral signature, barely moved by anything).
    avl-onset: area 0.19 / stim 0.03 / **session 0.44** — structured by SESSION >> AREA >> stimulus.
    sync-event: ~0 / ~0 / 0.10 — invariant Poisson.
- **(2) AREA STRUCTURES THE AVALANCHE OBSERVABLE, CONSISTENTLY (Kendall W=0.783 across session×block).**
  avl-onset q ordering: VISp/VISal/VISl (≈0.44) < VISrl/VISpm (0.48-0.50) < LGd/VISam (0.57-0.59) — primary
  & lateral visual LOW, higher-order areas + LGN HIGH. corr-eig area W=0.045, sync W=0.006 (no area
  structure). So the population's area dependence lives in the AVALANCHE (collective-dynamics) observable,
  not the spectral or network-event ones. (W is across session×block groups ⇒ area effect is within-session
  controlled, robust to the session dominance in η².)
- **(3) STIMULUS BARELY STRUCTURES THE POPULATION** (corr-eig W=0.055, avl W=0.244, sync W=0.005) — NO
  coherent stimulus trajectory. CONTRASTS with the per-cell finding that within-cell stimulus-state IS a
  live axis: at the population level the fingerprint is far more stimulus-invariant than the individual cell.
- **(4) POPULATION AREA-STRUCTURE ≠ PER-CELL AREA-STRUCTURE.** ρ(population corr-eig q, per-cell ks_gue)
  across 7 areas = −0.143 — the population spectral area pattern does NOT track the per-cell ks_gue (H1)
  area pattern; and the strong population area signal (avalanche) is a collective property with no per-cell
  analogue. Reinforces population-IS-a-distinct-substrate / avalanche-orthogonal-to-per-cell.
CAVEAT (flagged): avl-onset's session dominance (η²=0.44) may partly reflect recording characteristics
(unit count / firing-rate differences per session), not pure biology — the area effect (W=0.78) is the
cleaner within-session-controlled signal. Banked: coordinates/population-strat.jsonl (1456);
figure P_population_strat.png. Verdicts Will's.

### Rate-match de-confound of the population AREA effect (population_ratematch.py) — Step-2 cycle 2
The stratified-population finding flagged that avl-onset's area ordering (W=0.78) might be rate-mediated
(areas differ in unit count + firing rate; avalanche structure is rate-dependent). De-confounded by matching
every area WITHIN each (session,block) to a common (N_match units, R_match total spikes) — subsample units +
thin the pooled train — then recomputing avl-onset q (K=5 repeats averaged); corr-eig carried as control.
- **AREA EFFECT SURVIVES RATE-MATCHING ⇒ INDEPENDENT OF RATE (biological).** Matched avl-onset area
  Kendall W=0.808 (raw 0.783 — survives, slightly strengthens), SAME ordering: VISp(0.42)<VISl(0.44)<
  VISal(0.45)<VISpm(0.47)<VISrl(0.48) << VISam(0.59)<LGd(0.61). V1/lateral LOW → higher-order areas + LGN
  HIGH, holding when unit-count and total spike-count are equalised across areas within each recording.
- corr-eig control: matched W=0.215 (raw 0.045) — matching unit-count reveals a FAINT corr-eig area
  structure (VISal highest), but still far below avalanche's 0.808; corr-eig remains the near-invariant
  observable. (Side-note, not load-bearing: the MP-edge depends on N, so equalising N sharpens it slightly.)
**⇒ the honest reporting of the area effect is complete: the avalanche-timing area gradient is a rate-
INDEPENDENT (biological) property, not a recording-rate confound.** The session dominance (η²=0.44) was the
rate-sensitive part; the area gradient is the clean, matched signal. Banked: coordinates/
population-ratematch.jsonl (488); figure P_population_ratematch.png. Verdicts Will's.

### Temporal-stability cut (population_temporal.py) — Step-2 cycle 3, completes the stratification triad
Split each (session,area,block) into EARLY/LATE halves, recomputed the 3 observables per half (1,453 pairs,
4.8 min), test-retest of half-1 vs half-2 Brody q + within-cell |Δq| vs between-cell sd:
- **avl-onset: TEMPORALLY STATIONARY** — test-retest ρ=0.844, within|Δq|=0.054 ≪ between-sd 0.138. The
  avalanche fingerprint is a FIXED, reproducible property of the (area,stimulus) condition — it doesn't
  drift during the recording. Reinforces the rate-matched biological area effect: avl-onset is the informative
  population observable (structured by area+session, rate-independent area gradient, AND temporally stable).
- **corr-eig: INVARIANT-BUT-NOISY** (NOT drifting). test-retest ρ=−0.033, within|Δq|=0.110 ≈ between-sd
  0.100 — near-constant ~0.89 everywhere; its small spread is half-data estimation NOISE, not reproducible
  structure or systematic drift. (The script's crude within>between auto-tag said "DRIFTS"; the substantive
  read — ρ≈0 + within≈between with a tiny between-sd — is no-reproducible-structure. Discriminant-exact-
  question caveat noted.) Consistent with corr-eig's η²≤0.05 on every factor.
- **sync-event: trivially STATIONARY at Poisson** — both halves ≈0 (within 0.007, between 0.024); low ρ=0.26
  reflects ~no signal to correlate. Invariantly Poisson.
**⇒ Step-2 triad complete. The three population observables differ not just in landscape position but in
STRUCTURE-vs-NOISE-vs-INVARIANCE: avl-onset is the structured + stationary + biologically-area-graded
observable; corr-eig is invariant-and-featureless (~GUE everywhere); sync-event is invariant Poisson. "No
single population fingerprint" sharpens to: one observable carries reproducible biological structure, two
are condition-invariant.** Banked: coordinates/population-temporal.jsonl (1453); fig P_population_temporal.png.
Verdicts Will's.

### Buzsáki CA1 framework-port — full 8-session verdicts (Step-3 cycle 1; cross-substrate generalization)
Applied the IDENTICAL Allen tooling (observables/classify/dt/_fp) to CA1 (Grosmark 000044, 8 sessions:
Achilles×2/Buddy/Cicero×3/Gatsby×2). 348 pop + 4019 per-cell + 690 selectivity records. Verdicts (Will's):

- **G1 — FRAGMENTATION: PARTIAL GENERALISATION.** Structural ANCHORS generalise — corr-eig stays ~GUE
  (0.850±0.176, Allen 0.89), sync-event stays Poisson (0.000). The BIOLOGICAL/INTERMEDIATE observable
  DIVERGES — avl-onset collapses (0.104±0.183 vs Allen 0.61); canonical corr-eig>avl>sync ordering only
  33%. In CA1 the avalanche is NOT a stable intermediate; it is STATE-GATED (see G3). ⇒ the landscape's two
  poles are substrate-general, the middle is substrate-specific.
- **G2 — H1 GENERALISES, substrate-appropriately (intrinsic-vs-extrinsic discipline).** Extrinsic selectivity
  tracks per-cell ks_gue: spatial information (bits/spike, the place-coding analogue of OSI) ρ=+0.279
  (p=2e-13; exc-only +0.293), theta phase-locking ρ=−0.341 (exc-only −0.213, p=6e-7) — both robust at n=668.
  The STRONGEST correlate, burst_index ρ=+0.515, is INTRINSIC to the spike train (burst & ks_gue both
  ISI-derived) ⇒ flagged as largely TAUTOLOGICAL, NOT the H1-analogue. ⇒ H1 (extrinsic-selectivity↔class)
  GENERALISES from V1 to CA1 with the substrate-appropriate selectivity axis (orientation→spatial-coding);
  modest (ρ~0.3) but robust. NB the 3-session read (spatial ρ=0.09 NS) was underpowered — full-8 needed.
- **G3 — STATE EFFECT: one robust, two killed by rate-match + power.** Rate-matched (common spike-count,
  same CA1 units, K=5): wake_state Maze-Awake(0.427)→Awake-in-sleep(0.001) Δ=−0.43 SIGN-CONSISTENT across 8
  sessions ⇒ avalanche structure is gated by ACTIVE BEHAVIOUR, rate-INDEPENDENTLY. NonREM consolidation
  (Δ=−0.05, sign-VARIES at 8 — was sign-consistent at 3) and REM consolidation (underpowered, ~0→0 matched)
  do NOT survive. The intriguing 3-session POST-REM raw q=0.63 was a low-n rate-saturation artifact — gone
  under matching. (Vindicates rate-match-from-the-start + full-8-for-REM-power.)
- **G4 — CELL-TYPE: a robust new within-substrate axis (Allen lacked).** Per-cell ks_gue pyramidal(exc)
  med=0.685 (n=3259) > interneuron(inh) med=0.575 (n=760); population avl-onset exc 0.213 > inh 0.105.
  Pyramidal cells are more GUE/repulsive than interneurons, robust across 8 sessions.

**SYNTHESIS — the framework GENERALISES with structured reorganisation:** the structural poles (corr-eig
GUE-high / sync Poisson-low) are substrate-general; the per-cell extrinsic-selectivity↔class link (H1)
generalises with the substrate's own selectivity axis (spatial coding); but the biological MIDDLE
(avalanche) reorganises — in CA1 it is behaviour-state-gated rather than a stable intermediate. Cross-
substrate the SHARED structure is the universality-class poles + the extrinsic-selectivity principle; what
VARIES is which biology occupies the middle and which selectivity axis is relevant. Banked:
buzsaki-port-{pop,cell}.jsonl, buzsaki-selectivity.jsonl, buzsaki-ratematch.jsonl; fig P_buzsaki_port.png.

### Buzsáki cycle-2a: place-field structure ↔ per-cell class (deepens G2) — 8 sessions
Deepened the G2 H1-analogue (spatial-info↔ks_gue) by computing proper place-field metrics on the maze and
asking WHICH aspect of place coding tracks the per-cell universality class. 690 per-cell records, 668 merged
with Maze-Awake ks_gue. Robust full-8 verdicts (1-session hints that did NOT survive flagged):
- **Place-coding QUALITY/ORGANISATION is the class correlate, more than info content.** spatial COHERENCE
  (Muller-Kubie, rate-map smoothness/organisation) ρ=+0.467 (exc +0.375) ≥ spatial INFO ρ=+0.371 (exc
  +0.392). ⇒ the H1-analogue sharpens: it's how spatially ORGANISED the place code is, not just how many
  bits/spike, that tracks the universality class.
- **PLACE-CELLS are MORE GUE than non-place-cells:** ks_gue med 0.596 (n=374) vs 0.501 (n=294),
  Mann-Whitney p=2.6e-11. Robust, balanced n. Being a place cell ↔ more repulsive spike-timing class.
- **NON-robust (confirm-at-full-n discipline):** spatial_stability ρ=+0.066 (was +0.238 at 1 session — noise),
  n_fields ρ=−0.049 (was −0.385 at 1 session — noise), and the 1-session place-cell contrast SIGN-FLIPPED
  (1-sess place-cells LOWER ks_gue with only n=7 non-place → full-8 place-cells HIGHER). Vindicates full-8.
- **Cell-type confound:** peak_rate ρ=−0.083 all but +0.372 exc-only (interneurons high-rate + different class).
**⇒ cycle-2a deepens G2: the CA1 selectivity↔class link is carried by place-coding QUALITY (spatial
coherence + place-cell identity), robust at full power — G2 is firm enough to anchor cycle-2b (theta-gamma)
and cycle-2c (replay/SWR).** Banked: coordinates/buzsaki-placefields.jsonl (690); fig P_buzsaki_placefields.png.
Verdicts Will's.

### Buzsáki cycle-2b: theta-gamma / temporal organisation — BOUNDED-NEGATIVE (8 sessions)
Tested Will's synthesis (organisational QUALITY tracks class — does TEMPORAL organisation, theta-gamma CFC,
track per-cell class as SPATIAL organisation did in 2a, ρ=+0.47?). 48 substrate + 652 per-cell records.
- **PER-CELL gamma phase-locking ↔ ks_gue (the cleaner, channel-magnitude-independent test): WEAK/NULL.**
  slow_gamma_mrl ρ(all)=−0.033, ρ(exc)=−0.071 (~0); fast_gamma_mrl ρ(all)=−0.045, ρ(exc)=−0.203 (modest).
  vs theta_mrl −0.33/−0.14, vs spatial-coherence +0.47. ⇒ spikes do NOT robustly lock to whatever gamma
  exists in a way that tracks class. A real negative (interpretation independent of CFC channel/magnitude).
- **SUBSTRATE Tort MI: near-floor + measurement-suspect ⇒ INCONCLUSIVE (not definitively null).** All MI
  0.0003–0.0025 (synthetic-strong 0.055, literature CA1 ~0.01+); estimator VALIDATED on synthetic (coupled
  0.055 / uncoupled 0.000). Colgin check INVERTED (sleep CFC > active: slow 0.0008>0.0003, fast 0.0016>0.0011)
  — opposite the canonical active-running theta-gamma ⇒ raw-LFP CFC on this silicon-probe prep (no CSD,
  intermittent Maze theta) is measurement-limited. MI vs avalanche q (G1): slow ρ=−0.24, fast −0.06 (weak).
- **VERDICT: temporal organisation (theta-gamma) does NOT robustly track per-cell class, unlike spatial
  (2a). Synthesis NARROWS — falsification-style outcome.** Per-cell arm load-bearing (clean negative);
  substrate arm bounded by the CFC measurement caveat.
- **REFINEMENT BANKED — the LEVEL of organisation matters.** H1-substrate-general is specifically a PER-CELL
  EXTRINSIC-SELECTIVITY-QUALITY principle (V1: orientation-tuning organisation; CA1: place-coding
  organisation — both at cell level → track class), NOT a substrate-level oscillatory-organisation principle
  (CA1 theta-gamma CFC at substrate level → does NOT track per-cell class). Sharper than "organisational
  quality tracks class": it specifies the LEVEL (per-cell selectivity, not substrate-wide temporal coupling).
- **CFC measurement caveat banked, NOT invested in now.** A proper CFC pipeline (CSD / layer-specific
  channel / stricter theta-epoch gating) is its own dedicated arc (like the TD-formalism dimension) — deferred
  until/unless theta-gamma becomes load-bearing. Cycle 2c (replay/SWR) may pull in fast-gamma/ripple-band
  diagnostics contextually but doesn't require it.
Banked: coordinates/buzsaki-thetagamma-{sub,cell}.jsonl; fig P_buzsaki_thetagamma.png. Verdicts Will's.

### Buzsáki cycle-2c-a: sharp-wave-ripples — SWR-rate consolidation enrichment + participation null (8 sessions)
Detected SWRs (150-250Hz ripple-band events, NonREM; channel = max ripple-power; peak>5σ/edge>2σ/15-250ms),
per-cell SWR participation, cross-ref with class + place-quality. 16 event-summary + 690 per-cell records.
- **(2c-1) SWR-RATE PRE→POST ENRICHMENT: ROBUST.** PRE 15.4/min → POST 19.6/min, Δ=+4.2, Wilcoxon p=0.0078,
  ALL 8/8 sessions positive (POST−PRE [6.5,7.7,4.3,1.8,3.5,6.3,3.4,0.2]). The canonical post-experience
  replay-enrichment signature, replicated. NB the consolidation paradigm IS present in this data via SWR
  RATE — even though the avalanche-consolidation effect (G3/2-cycle) died under rate-match+power; SWR rate is
  the more robust consolidation observable. (Also validates the SWR detector + plausible ~15-20/min rates.)
- **(2c-2) SWR PARTICIPATION does NOT track per-cell class (de-confounded).** all-cells ρ(participation,
  ks_gue)=−0.288 was the CELL-TYPE CONFOUND (interneurons participate ~5× more: inh med 0.683 vs exc 0.128);
  EXC-only ρ=+0.030 = NULL. place-coherence exc ρ=−0.124 (weak); place-cells marginally MORE engaged (exc
  med 0.133 vs non-place 0.121, p=0.037 — tiny). ⇒ SWR engagement is ANOTHER per-cell property that does NOT
  track class — reinforcing the refined H1: PLACE-CODING QUALITY is specifically the class-linked per-cell
  property, not general circuit engagement (SWR participation) or temporal locking (gamma, 2b).
- **Methodology: SWR participation is heavily cell-type-confounded** (interneurons ~5× pyramidal) — all
  per-cell SWR cross-refs must be exc-only; sibling of the theta_mrl cell-type confound.
**⇒ cycle-2c-a: one robust hippocampus-specific POSITIVE (SWR-rate consolidation enrichment, 8/8, p=0.008)
+ a reinforcing per-cell NULL (SWR engagement ⊥ class). The H1 refinement holds across THREE per-cell probes
now: place-coding quality TRACKS class (2a); gamma phase-locking (2b) and SWR participation (2c-a) do NOT.**
Banked: coordinates/buzsaki-swr-{event,cell}.jsonl; fig P_buzsaki_swr.png. Bayesian replay-sequence decoding
(2c-b) is the open follow-on. Verdicts Will's.

### IBL Brain-Wide-Map framework-port (THIRD substrate) — PILLAR 1 generalises (n=3); PILLAR 2 needs region-targeting
Ported the Allen+Buzsáki tooling to IBL (DANDI 000409 processed NWBs, turnkey h5py; 5 sessions, 1141 cells)
— third substrate CLASS (cortex+subcortex, visual decision task). The processed NWBs (~0.3GB) have
spikes + trials (gabor contrast, wheel choice) + spike-width cell-typing + electrode CCF region.
- **PILLAR 1 — STRUCTURAL ANCHORS GENERALISE at n=3 (strong).** corr-eig q=0.814±0.098 (~GUE, matches Allen
  0.85-0.89 / CA1 0.85); sync-event q=0.012±0.024 (~Poisson, matches 0.00); avl-onset q=0.633±0.075
  (INTERMEDIATE — like Allen 0.61, NOT collapsed like CA1). ⇒ the GUE/Poisson POLES hold across V1, CA1, AND
  brain-wide cortex+subcortex; and IBL's biological MIDDLE is intermediate-avalanche (like Allen),
  reinforcing that the CA1 avalanche-collapse was the hippocampus-specific reorganisation. Region-agnostic
  (population observables over all cells) — robust.
- **PILLAR 2 — H1 NOT PROPERLY TESTED on IBL (region-mismatch, methodology lesson).** ks_gue vs
  contrast_tuning ρ≈0 (all −0.004, wide −0.110); choice_selectivity weak (wide ρ=−0.180). BUT the 5 picked
  sessions (selected SMALLEST-size) have ZERO visual cells — they're hippocampal/prefrontal/thalamic
  (SWC-066=CA1, witten-19=orbital/prelimbic, NR-0029=ventral/hypothalamus). So contrast-tuning↔class is
  UNTESTABLE here (non-visual cells have no contrast tuning; ρ≈0 is trivially expected, not informative).
  Choice-selectivity (brain-wide-apt, decision-related) is the testable arm here and is weak (wide −0.18) —
  but choice is a decision variable, not the sensory-tuning analog of OSI/place. ⇒ pillar-2 INCONCLUSIVE on
  IBL pending VISUAL-region sessions. cell-type (spike-width): ks_gue wide 0.374 vs narrow 0.373 — no
  difference (unlike CA1 pyr>int; but these are non-visual non-CA1 regions).
- **METHODOLOGY LESSON (new): in brain-wide data, REGION-TARGET the selectivity axis.** The H1-analogue
  selectivity property only exists in the cells that carry it (contrast→visual cortex, place→CA1,
  orientation→V1). Size-first session selection failed SILENTLY (picked non-visual). Sibling of
  observable-binding: match the EXTRINSIC-SELECTIVITY axis to the region, not just the dataset. The proper
  IBL pillar-2 test requires VISp-containing insertions.
Banked: coordinates/ibl-port-{cell,pop}.jsonl; scripts ibl_port.py. Verdicts Will's. NEXT: acquire
visual-cortex IBL sessions for the proper pillar-2 (contrast-tuning↔class) test.

### IBL pillar-2 region-resolved (visual cortex) + n=3 cross-substrate synthesis
Remote-scanned IBL processed NWBs via fsspec (read electrodes/location WITHOUT full download — efficient
region-targeting), found visual-rich sessions (witten-20: 267 Primary-visual-area cells, ZFM-01577: 118
lateral-visual, witten-26: 32), downloaded 3, ran the region-resolved pillar-2 on 417 actual visual cells.
- **PILLAR 2 on IBL VISUAL cortex: WEAK.** contrast-tuning↔ks_gue ρ=−0.121 (p=0.014, n=416);
  choice-selectivity ρ=−0.169 (p=0.067, n=118). Significant but small — NOT the strong selectivity↔class
  link of V1-OSI / CA1-place-coherence (ρ≈0.47). cell-type ks_gue wide 0.398 vs narrow 0.412 (no diff).
- **CAVEAT (axis mismatch, load-bearing): IBL's task is CONTRAST DETECTION, not orientation tuning** — so
  contrast-sensitivity is NOT the true OSI-analog (the axis that was H1 in Allen V1). IBL's task design does
  not elicit orientation selectivity, and IBL ks_gue is compressed (~0.40). ⇒ pillar-2 on IBL is BOUNDED
  (weak + selectivity-axis-mismatched), neither clean confirmation nor refutation.
**⇒ n=3 CROSS-SUBSTRATE SYNTHESIS:**
  PILLAR 1 (GUE/Poisson structural poles): V1 ✓, CA1 ✓, IBL ✓ — GENERALISES at n=3 (corr-eig GUE 0.81-0.89,
    sync Poisson 0.00-0.01 across all three). STRONG. The substrate-invariant skeleton holds across mouse
    visual cortex, hippocampus, and brain-wide cortex+subcortex.
  PILLAR 2 (per-cell extrinsic-selectivity-quality ↔ class): V1 ✓ (OSI), CA1 ✓ (place-coding quality,
    ρ=0.47) — confirmed where the substrate's OSI-style selectivity axis IS measured; IBL weak (ρ=−0.12) but
    its task gives no clean OSI-analog (contrast-detection ≠ orientation-tuning). ⇒ pillar-2 confirmed 2/3,
    IBL inconclusive-by-axis-mismatch. REFINEMENT: pillar-2 requires the substrate to actually MEASURE an
    OSI-style tuning-selectivity axis; a detection-task contrast-sensitivity is too weak a proxy.
  METHODOLOGY WIN: fsspec remote-HDF5 region-scan (read electrodes table without downloading 2-3GB files) —
  the efficient way to region-target brain-wide datasets; found visual sessions without bulk download.
Banked: coordinates/ibl-port-cell-visual.jsonl (417); ibl_port.py (--visual-only, --glob, region/is_visual).
Verdicts Will's.

### Pillar-2 status — FORMAL (banked 2026-05-25, after the orientation-data scope)
Scope of orientation/tuning substrates for the definitive pillar-2 test (does per-cell extrinsic
selectivity-QUALITY ↔ class generalise to a third circuit with a measured tuning axis):
  • IBL passive gratings — OUT (no orientation block; task = fixed-orientation contrast-detection).
  • DANDI orientation-tuning — no clean NEW spike substrate: Allen Visual Coding NPX (000021/022) = our own
    V1 class; the tuning datasets (000039/049/050) are two-photon CALCIUM (no spike-times → ks_gue
    observable-mismatched); no primate/non-Allen orientation EPHYS.
  • Off-DANDI retinal (Marre/Chichilnisky/Berry) — the only route giving all three (different circuit +
    spike-timing MEA + measured DS/OS tuning); custom per-lab formats = a dedicated engineering arc.
**FORMAL PILLAR-2 STATEMENTS (verdict ratified by Will):**
  1. DEMONSTRATED 2/3 — across two genuinely DISTINCT circuits (V1 cortex, CA1 hippocampus) with two
     DISTINCT selectivity axes (orientation OSI; place-coding coherence). A substrate-general result.
  2. SPEC REFINED (v1→v2): the principle requires a GRADED TUNING-selectivity axis (orientation / place /
     spatial-info), NOT a detection-task proxy. The IBL outcome (contrast-DETECTION, ρ=−0.12) sharpened the
     spec rather than weakening the claim — it bounded WHAT the test requires.
  3. DEFINITIVE THIRD TEST QUEUED as an off-DANDI retinal ENGINEERING ARC (custom-format parsers,
     registration, lab-specific quirks) — dedicated project scope, not a cycle-level task. Calcium ruled out
     by observable-binding (can't resolve the spike-timing fine structure ks_gue reads).
Pillar 1 (GUE/Poisson poles) remains GENERALISED at n=3 (V1/CA1/IBL). Cross-substrate program: pillars
banked, multiple legitimate next moves open (none forced).

### p2-saturation RF diagnostic — it's a padic-amplitude ARTIFACT, not FM structure (cheap-win roundup)
The brocot RF per-prime (III.1_p{2,3,5,7}) is monotone p2≫p3≫p5≫p7 (corpus median 0.231/0.083/0.065/0.021),
p2 dominating every exemplar regardless of prime-family — flagged as "p2-saturation". Diagnosed by running
padic_amplitude_v4 (q_max=32) on CONTROL frequency sets (synthetic-validate-fitters discipline):
- uniform-random freqs: [0.33,0.19,0.04,0.01] — SAME monotone p2≫p3≫p5≫p7 as brocot.
- harmonic comb (clock): [0.583,0.001,0.146,0.0] — p2 dominates a pure integer-harmonic comb.
- **3-POWER-random (freqs = 110·3^U, deliberately NO 2-structure): [0.376,0.036,0.102,0.017] — p2 STILL
  dominates (0.38) despite frequencies built from powers of 3; p3 is LOW (0.036).** Smoking gun.
**⇒ VERDICT: p2-saturation is a padic_amplitude_v4 ARTIFACT, not a real FM/brocot feature.** Small primes
have more powers/divisors ≤ q_max (2,4,8,16,32 vs 3,9,27 vs 5,25 vs 7) → the p=2 channel accumulates a higher
BASELINE amplitude irrespective of the signal's actual arithmetic. The "normalised" field does not correct
this prime-dependent baseline. Consequences (banked):
- **RF per-prime amplitudes are NOT cross-prime comparable** — p2 always wins; raw per-prime ranking is
  meaningless for prime-specificity. Prime-named brocot families do NOT carry their prime in the raw RF.
- Brocot's per-prime values sit AT/BELOW the uniform-random baseline (p2 0.23<0.26, p3 0.08<0.16) ⇒ NO
  prime-specific enhancement in the raw RF leg at all.
- **Methodology: to test prime-specificity, z-score each prime channel against its OWN prime-matched
  surrogate baseline** (per-prime null), never compare raw amplitudes across primes. Sibling of
  support-set-respecting-nulls. Resolves the standing "do prime-named families carry their prime in RF" Q:
  the raw RF can't answer it (artifact-dominated); the per-prime-baseline version is the valid instrument.
Cheap-win roundup item — closed. No new artifact files (diagnostic on banked brocot-landscape + controls).

### DEGT dimension — CONFIRMED via growth-rate thermodynamic formalism (resolves §3(k))
The deferred quantitative DEGT piece. §3(k) confirmed the FORM (dim·ln(λ)→const) but the CONSTANT was
deferred: the single-level Bowen pressure Σ|band|^d=1 is scale-DEPENDENT (uses absolute widths at one
approximant level → drifts as q→∞; diverged to 1.72 at λ=1024). The fix is the proper thermodynamic
formalism — the dimension is where the partition-function GROWTH RATE across renormalization levels
vanishes: d* = root of slope(log Σ|band|^d vs log q) = 0. Scale-INVARIANT (the level-dependence cancels
at d*; reduces to box-dim = logN/log(1/w) for a self-similar cover).
- **VALIDATED vs box_dim at moderate λ** (golden λ=2→0.611 vs banked 0.628; λ=4→0.455 vs 0.475; λ=8→0.343
  vs 0.369) — synthetic-validate gate passed before trusting at strong λ.
- **CONVERGENCE-GATED** (shallow q∈[55..610] vs deep q∈[233..1597]; |Δ|<0.02 = reliable): golden converged
  λ≤32, depth-wall (drift) at λ≥48 (bands too small for q≤1597 — the periodic-approximant depth limit).
- **DEGT CONFIRMED:** golden extrapolation (converged pts, 1/ln(λ)→0) **C=0.8756 vs ln(1+√2)=0.88137,
  Δ=−0.0058 (~0.6%).** Form AND constant now landed — §3(k) PARTIAL → RESOLVED.
- **New (unpublished) asymptotic dimension constants per class:** silver C=0.867, bronze 0.913, e_minus_2
  1.173. Metallic means (quadratic CF) CLUSTER near DEGT-golden (~0.87–0.91); e (μ=2 but UNBOUNDED/
  transcendental CF) is DISTINCT at 1.17 — the asymptotic dimension constant is approximability/CF-structure
  stratified (echoes the cf_discriminator boundedness finding: e separates from the metallic means).
**⇒ the trace-map TD-formalism dimension arc is COMPLETE: DEGT golden constant confirmed (~0.6%); the method
(growth-rate pressure + convergence-gate + 1/lnλ extrapolation) is the scale-invariant fix that the
single-level pressure lacked.** Banked: coordinates/trace-map-dimension.jsonl; fig P11b_degt_growthrate.png.
Verdicts Will's.

### Gold↔silver ladder — the "missing thing between gold and silver" is a real LAGRANGE-SPECTRUM GAP
Will's intuition (something missing between gold and silver) probed by building a ladder of mixed-digit
periodic-CF quadratics interpolating gold [1̄]→silver [2̄] (plus Markov-5 [2,2,1,1]), placed on the IDS
staircases + the dimension-vs-approximability axis. Lagrange-constant computation VALIDATED: Markov-5
[2,2,1,1] → Λ=2.9732 = √221/5 exactly (the known Markov value).
- **THE GOLD→SILVER APPROXIMABILITY REGION IS A GENUINE GAP.** None of the mixed-CF quadratics land between
  gold (Λ=√5=2.236) and silver (Λ=√8=2.828): they ALL jump to Λ≥2.973 (Markov-5) or >3. This IS the famous
  gap in the Lagrange spectrum — below 3 the spectrum is the DISCRETE Markov sequence {√5, √8, √221/5,
  √1517/13,…→3}, and √5, √8 are CONSECUTIVE (Markov numbers 1,2). So nothing (no quadratic, no real) has
  Λ∈(√5,√8). Gold & silver are the two MOST-extremal numbers in Diophantine approximation, separated by a
  true spectral gap. The "missing something" is the gap itself — a structural hole, not unsampled data.
- **In DIMENSION-space the members spread, non-monotonically** (DEGT C: gold 0.876, silver 0.867, mixed
  0.86–0.94, Markov-5 0.915, bronze 0.913). C is NOT a simple function of Λ in this region — the dimension
  and the approximability are distinct readouts (the gold→silver C-bridge does not interpolate smoothly).
- **IDS-staircase morph (V6):** stacked by Λ, gold has the cleanest single-dominant-gap structure (its big
  gap at IDS={1α}=α); as approximability rises the gaps PROLIFERATE/fragment. The {nα} gap-labelling slides
  with α (the ▶ markers).
**⇒ the approximability axis between the two lowest metallic means is genuinely EMPTY (Lagrange gap √5↔√8);
all other quadratics are MORE approximable than silver. The metallic ladder's first two rungs bracket a hole
that number theory says cannot be filled.** Banked: coordinates/gold-silver-ladder.jsonl; figures
V6_ladder_staircases.png, V7_dim_vs_approximability.png. gold_silver_ladder.py. Verdicts Will's.

---

## 2026-05-28 — EC(MEC continuous-attractor) vs CA3(discrete-attractor): cross-region fingerprint port

**Frame.** Overnight brief: the lecture hypothesis is that continuous-attractor regions (EC grid cells,
toroidal manifold) differ from discrete-attractor regions (CA3 autoassociative point-attractors) in a
responsiveness-vs-stability tradeoff. ARS cannot test attractor topology directly (that needs manifold
inference) — this is a baseline cross-region FINGERPRINT comparison, hypothesis-engagement flagged not
measured. Seizure-perturbation out of scope (no public data).

**P0 — acquisition.** (1) Existing 8 Grosmark/Buzsáki sessions are **CA1-only** (lCA1/rCA1) — no EC/CA3.
(2) CRCNS Mizuseki creds not configured (hard-stop respected; offer open for additive sleep-epoch data).
(3) **DANDI 000638** "Hippocampus + EC Dual Region Silicon Probe" — turnkey NWB, MEC(grid)+CA1+DG+LEC+CA3sp
electrodes. Streamed units+behavior over HTTP range (`nwb_remote.py`, stdlib, no fsspec) — the 30-70GB raw
traces are NOT downloaded. Scanned all 33 sessions: **every session has MEC+CA1+DG but ZERO sorted CA3
units** (electrodes present, no units) and zero LEC units. So 000638 supplies the **continuous-attractor
pole (MEC)** + CA1 + DG. The **discrete-attractor pole (CA3)** comes from the local **Allen** ecephys
(8 sessions, CA3 466 / CA1 2463 / DG 730 good units; no EC). **CA1+DG measured in BOTH = cross-substrate
VALIDITY BRIDGE.**

**P1 — framework-port (identical tooling: ars_classify ks_gue + Family I per-cell; corr-eig/avl-onset/
sync-event population; dt=25ms; cell-type = NWB unit_type for 000638, waveform-duration<0.4ms RS/FS split
for Allen).** 000638: 1365 per-cell + 131 pop records (10 sessions, MEC≥20/CA1≥20/DG≥15). Allen-HPF: 4358
per-cell + 255 pop.
- **Pillar-1 GENERALISES (now n=5 substrate-types: V1, Buzsáki-CA1, IBL, +MEC, +Allen-HPF):** population
  corr-eig stays GUE-like in EVERY region of both substrates — MEC q=0.87, CA3 q=0.95, CA1 q=0.91, DG q=0.86;
  sync-event stays Poisson (q≈0) everywhere. The structural-anchor universality holds in the continuous-
  attractor region (MEC) and across all hippocampal subfields.

**P2 — cross-region comparison. THE DECISIVE RESULT: the validity bridge FAILS.** The shared anchors (CA1,
DG, measured in both substrates) differ by NEAR-MAXIMAL effect size (excitatory, Cliff's δ):
  CA1 000638-vs-Allen: ks_gue δ=−0.934, w1 δ=−0.999, BRρ δ=+0.894 (all LARGE, p<1e-58).
  DG  000638-vs-Allen: ks_gue δ=−0.869, w1 δ=−0.939, BRρ δ=+0.839 (all LARGE).
The MEC-vs-CA3 "headline" gap (ks_gue δ=−0.885, w1 δ=−0.995) is **statistically indistinguishable from the
CA1-vs-CA1 / DG-vs-DG bridge gaps.** ⇒ the entire cross-substrate signal is the **recording-context axis**
(000638 78-min track task @~0.5Hz vs Allen short spontaneous block @~3Hz; different sorting/cohort), NOT
region biology. **MEC-vs-CA3 is NOT measurable as an attractor-topology contrast from these two datasets.**
The bridge correctly flags the comparison invalid (extends the cross-substrate rate/epoch-dependence +
carry-viewpoints-annotate-validity disciplines: a designed validity-anchor caught a confound that the raw
contrast would have mis-sold as biology).

**P2 — WITHIN-substrate (valid; rate-matched, excitatory-only, vs CA1 anchor):**
- **000638:** MEC grid cells fire markedly **LESS burstily than CA1** (burst_frac δ=−0.55 LARGE, cv2
  δ=−0.40 medium — survives rate-match). DG **more GUE-like** than CA1 (ks_gue δ=+0.41 medium, w1 δ=+0.34).
  MEC≈CA1 on ks_gue (negligible).
- **Allen:** CA3 marginally **more GUE-like** than CA1 (ks_gue δ=+0.16 small, rate-matched) + less irregular
  (cv2 δ=−0.21 small). DG less bursty than CA1 (δ=−0.22 small).
- Parallel worth flagging (NOT claimed as cross-substrate, since the bridge fails): in EACH substrate the
  "specialized" region trends MORE GUE-like than CA1 — DG(separator) in 000638, CA3(attractor) in Allen —
  but effects are small/medium and the regions differ. Within-substrate statements only.

**P2.4 — burst structure.** The one LARGE cross-region effect (MEC≪CA1 burstiness) is most parsimoniously
**known intrinsic biophysics** (MEC L2 stellate vs CA1 pyramidal: pyramidals are classically bursty) — an
INTRINSIC predictor (cf. the intrinsic-vs-extrinsic lesson), NOT a readout of attractor topology.

**P1.3/P2.3 — pillar-2 on the CONTINUOUS-attractor substrate (000638 track task, 580 place-field cells:
MEC 363 / CA1 147 / DG 70; running-period 1D rate maps, Skaggs spatial-info + spatial coherence vs
ks_gue, Spearman).** Pillar-2 (per-cell EXTRINSIC selectivity-quality ↔ universality class) HOLDS in MEC:
- **MEC** spatial_info↔ks_gue ρ=+0.43*** (excitatory, n=255); place_coherence↔ks_gue ρ=+0.27*** (all).
- **CA1** spatial_info↔ks_gue ρ=+0.44** (exc, n=49); place_coherence↔ks_gue ρ=+0.32*** (all).
- DG: n.s. excitatory-only (n=17 underpowered).
MEC's ρ≈+0.43 is COMPARABLE to CA1's prior place-coherence↔class +0.47 (Buzsáki cycle-2a). spatial_info is
EXTRINSIC (not the tautological intrinsic burst); qualifies under the pillar-2 v2 spec. NB sign: ks_gue
LOWER=more-GUE; ρ>0 means better spatial coding ↔ higher ks_gue. Within-000638 the link is robust; not a
cross-substrate claim.
**FRAMING (Will, do NOT read as "3/3, retinal unnecessary"):** MEC strengthens pillar-2 but does NOT add a
new selectivity AXIS or an independent sample. (1) MEC and CA1 are both spatial-navigation circuits → same
KIND of axis (spatial coding); axis-diversity is really **2** (visual-orientation in V1; spatial-coding in
CA1+MEC), not 3. (2) MEC and CA1 are NOT independent samples — **grid cells feed place cells**, coupled
stages of one pathway, so a correlation in both is not two independent confirmations. **Correct tally: the
SPATIAL arm now has two (COUPLED) confirmations (CA1, MEC); the ORIENTATION arm has one (V1); a MOTION/
CONTRAST arm is still UNCONFIRMED.** The off-DANDI retinal arc ([[planned_engineering_arc]]) RETAINS FULL
VALUE — retina (DS/OS, motion/contrast) adds genuine selectivity-AXIS independence that MEC cannot.

**P3 — attractor-topology engagement (interpretive, NOT measured).** The lecture hypothesis predicts the
continuous-attractor region (MEC) differs in fingerprint from discrete-attractor/relay regions (CA3/CA1).
**ARS finds NO such distinguishing axis:** (a) cross-substrate MEC-vs-CA3 is confounded-out (bridge fail —
the contrast is recording-context, not biology); (b) **both pillars operate IDENTICALLY in MEC and CA1** —
pillar-1 (corr-eig GUE) is region-INVARIANT, pillar-2 (spatial-quality↔class) holds in BOTH continuous (MEC
ρ=+0.43) and the CA1 relay (ρ=+0.44) at comparable magnitude; (c) the lone LARGE within-substrate cross-
region difference (MEC≪CA1 burstiness) is most parsimoniously known intrinsic biophysics (stellate vs
pyramidal), an INTRINSIC predictor. **Verdict: the attractor-topology framing predicts a regional fingerprint
difference; our data shows the ARS pillars are region-GENERAL (operate the same in continuous- and discrete-
attractor circuits) and the residual differences are recording-context or intrinsic-biophysical. NOT a
confirmation — a bounded NEGATIVE: the fingerprint-level signature does not track continuous-vs-discrete
attractor topology.** ARS cannot directly test attractor topology (needs manifold inference, Gallego/
Churchland tradition); this is a fingerprint-level comparison only.
**RIGHT FRAMING (Will) — the negative bounds the INSTRUMENT as much as the hypothesis.** This is NOT "the
lecture's hypothesis is wrong." It is "**attractor topology is not a spike-train-FINGERPRINT property.**" If
the responsiveness-vs-stability hypothesis holds, it operates at the **population-manifold-geometry** level —
which ARS does not resolve **by construction**. The ARS fingerprint sees (i) per-cell selectivity-quality and
(ii) the structural universality poles; it does NOT see manifold topology. So tonight's negative maps the
RESOLVING POWER of the instrument (cell-level + structural, not manifold-geometric) at least as much as it
constrains the biology. **Knowing what ARS cannot see is itself worth banking** ([[ars_resolving_power]]).

**PROGRAM CONTRIBUTION (separate from the hypothesis-engagement):** pillar-2 selectivity-axis tally is now —
SPATIAL arm: two (coupled, grid→place) confirmations (CA1, MEC); ORIENTATION arm: one (V1); MOTION/CONTRAST
arm: unconfirmed. So 2 axes (not 3), and the two spatial confirmations are not independent samples. Pillar-1
GENERALISES to n=5 substrate-types (V1, Buzsáki-CA1, IBL, +MEC, +Allen-HPF). The off-DANDI retinal arc
([[planned_engineering_arc]]) retains FULL value — it is the only queued test that adds a genuinely
independent selectivity AXIS (motion/contrast, DS/OS) in an independent circuit; MEC cannot substitute.

Banked: coordinates/dr-port-{cell,pop}.jsonl, allen-hpf-{cell,pop}.jsonl, dr-placefields.jsonl,
dr000638_composition.json, attractor_analysis_{plain,ratematch}.txt; figures/P_ec_ca3_attractor.png +
P_ec_ca3_pillar2.png. Code: nwb_remote.py, dual_region_scan.py, allen_hpf.py, dual_region_port.py,
attractor_analysis.py, attractor_figure.py, dual_region_placefields.py. Verdicts Will's.

---

## 2026-05-28 — DE-CONFOUNDED EC-vs-CA3 on CRCNS hc-3 (substrate #6; within ONE dataset)

**Frame.** The same-night 000638-vs-Allen MEC-vs-CA3 was confounded-out by the cross-dataset
[[cross_substrate_validity_bridge]] (shared CA1/DG differed δ≈−0.9). CRCNS **hc-3** (Mizuseki/Buzsáki)
records EC (EC2-5) + CA3 (+DG) **SIMULTANEOUSLY in one implant**, so the EC-vs-CA3 contrast runs WITHIN one
recording — no cross-dataset confound. Will provided CRCNS creds; the de-confounded test is the real version
of tonight's headline.

**P0/build.** crcns_client.py (auth POST index.php, creds from ~/.netrc), crcns_fetch.py (download tarball →
extract ONLY .res/.clu/.whl/.xml → delete tarball; sequential + size-verify, ~10.8 MB/s), hc3_port.py
(Neuroscope/Klusters parser: .xml 20 kHz → .res sample-idx → spike_times; .clu cluster ids ≥2; hc3-cell.csv
→ region + cellType p/i/n; .whl 39.06 Hz position). 20 topdirs have EC+CA3 simultaneous; CA1 NOT co-targeted
in those implants. 7 sessions ported (ec013 ×4 EC+CA3; ec016 ×3 EC+CA3+DG): 368 per-cell (EC 91 / CA3 234 /
DG 43) + 36 pop + 203 placefield records.

**THE de-confounded EC-vs-CA3 result (excitatory, rate-matched ≤1.18 Hz, within-dataset):** LARGE raw
fingerprint difference — ks_gue δ=−0.53***, w1 δ=−0.63***, BRρ δ=+0.42***, **burst_frac δ=−0.82***, cv2
δ=−0.63*** (EC markedly MORE GUE-like and FAR less bursty than CA3). So the cross-dataset confound HAD masked
a real, large within-dataset difference.

**BURST-CONTROL (intrinsic-vs-extrinsic) — the decisive decomposition:** across pooled EC+CA3 excitatory
cells, ks_gue ~ burst_frac Spearman **ρ=+0.80** (n=275, p=3e-62). Residualizing ks_gue on the burst trend,
the EC-vs-CA3 ks_gue gap **COLLAPSES from δ=−0.63 (LARGE) to δ=+0.04 (negligible, p=0.66).** ⇒ **the entire
within-dataset EC-vs-CA3 NNS-fingerprint difference IS the intrinsic burst/ISI axis** (CA3 pyramidal
complex-spike bursting vs EC's less-bursty principal cells) — a tautological cell-class biophysics property
([[intrinsic_vs_extrinsic_predictor]]), NOT an attractor-topology-specific signature. Controlling for burst,
EC ≡ CA3 in universality class.

**Pillars.** Pillar-1: CA3 corr-eig Brody q=0.97 (GUE ✓), sync-event q≈0 (Poisson ✓); EC population
UNDERPOWERED for corr-eig (<20 active EC units/session — the EC implants caught fewer principal cells than
CA3), so EC pillar-1 untested here. Pillar-2: spatial_info↔ks_gue holds in **EC ρ=+0.39 (p=0.006)** AND
**CA3 ρ=+0.25 (p=0.006)**, same sign as MEC/CA1/V1.

**PILLAR-2 TALLY CALIBRATION (Will, keep this so a future read does NOT slide into "5/5, retinal
unnecessary").** Confirmations are now FIVE regions — V1, CA1, MEC, EC, CA3 — but still only **TWO
selectivity-axis KINDS**: orientation (V1, ×1) and spatial-coding (CA1/MEC/EC/CA3, ×4). The four spatial
confirmations are NOT independent samples — they are interconnected hippocampal-formation stages (EC→DG→CA3→
CA1, grid→place), all coding the SAME variable kind. So: 5 confirmations, 2 axis-kinds, one heavily-coupled
spatial arm. **The off-DANDI retinal arc ([[planned_engineering_arc]]) retains its full independent value** —
it is still the only queued test adding a genuinely different selectivity-axis KIND (motion/contrast, DS/OS)
in an independent (non-hippocampal, feedforward) circuit. Count regions, not axis-kinds.
**Honest caveat on the hc-3 pillar-2 specifically:** here the class axis (ks_gue) is burst-DOMINATED
(ρ_ks~burst=0.80), so the EC/CA3 spatial_info↔ks_gue link is partly mediated by burst (place/grid cells are
both spatially-informative AND bursty). spatial_info is extrinsic, but this is a WEAKER form of pillar-2 than
V1's OSI↔class — flag pending a burst-controlled re-test of the spatial_info↔ks_gue link.

**VERDICT — confirms + SHARPENS the bounded-negative, with a clean causal decomposition.** The de-confounded
contrast was essential: it showed EC-vs-CA3 IS large and measurable in raw fingerprint (the cross-dataset
test couldn't even see it), THEN the burst-control showed the difference reduces 100% to intrinsic cell-class
burstiness, 0% to an attractor-topology-specific NNS signature. **The continuous-vs-discrete attractor
distinction produces no spike-train-fingerprint signature beyond what intrinsic biophysics (burst) already
explains** — consistent with [[ars_resolving_power]] (the fingerprint reads cell-level intrinsic ISI
structure, not manifold topology). The [[cross_substrate_validity_bridge]] methodology is vindicated:
cross-dataset was confounded; within-dataset reveals the real difference AND its (intrinsic) origin.

Banked: coordinates/hc3-port-{cell,pop}.jsonl, hc3-placefields.jsonl, hc3_analysis_{plain,ratematch}.txt;
figures/P_hc3_ec_ca3_deconfound.png. Code: crcns_client.py, crcns_fetch.py, hc3_port.py, hc3_analysis.py,
hc3_figure.py. Metadata cached crcns_cache/docs (gitignored raw). Verdicts Will's.

**FOLLOW-UP (3 threads, 22 sessions / 19 topdirs; EC 261 / CA3 610 / DG 52 per-cell):**
- **(3) burst-decomposition REPRODUCED at scale (n=659):** ks_gue~burst_frac Spearman **ρ=+0.78** (p=1e-136);
  EC-vs-CA3 ks_gue RAW δ=−0.51 LARGE → **burst-residual δ=+0.03 negligible (p=0.56).** The de-confounded
  EC-vs-CA3 NNS gap is 100% the intrinsic burst axis — now rock-solid at 4× the original n. burst_frac
  δ=−0.71, cv2 δ=−0.62 (LARGE, EC≪CA3).
- **(1) state-stratification — FLAT (active vs sleep, paired within-cell, ec016.45 = only EC+CA3 topdir with
  sleep; EC n=11, CA3 n=17):** ks_gue and burst_frac are STATE-INVARIANT — EC ks_gue Δ=−0.02 (Wilcoxon p=1),
  CA3 ks_gue Δ=+0.05 (p=0.12), EC burst Δ=+0.01 (p=0.7), CA3 burst Δ=+0.01 (p=0.4); none significant.
  Consistent with the EC-vs-CA3 difference being a FIXED intrinsic cell-class property (burstiness), not a
  state-dependent dynamic. (No .sts/.states in hc-3 sleep tarballs → SWS/REM sub-scoring would need the LFP
  .eeg; active-vs-whole-sleep only. Single-topdir, modest n.)
- **(2) EC pillar-1 (pooled corr-eig, hc3_ec_pillar1.py — align units by (ele,clu) across a topdir's sessions,
  stack count matrices):** at the one powered topdir (ec013.55, 3 linear pooled, 31 EC units) **EC corr-eig
  ks_gue=0.093 — strongly GUE-like**, matching CA3 (0.251) and the GUE pole; + EC avl-onset q=0.82 GUE-leaning
  (n=4). Pillar-1 (structural GUE poles) GENERALISES to the continuous-attractor EC where powered.
  CONFIRMED-BUT-MARGINAL: EC implants caught few principal cells (8-35/topdir) → corr-eig bulk≈30 (Brody/BRρ
  fitters underpowered at that size; ks_gue is the robust readout). Other topdirs EC-underpowered.
- Pillar-2 at larger n: EC spatial_info↔ks_gue ρ=+0.51 (n=144), CA3 ρ=+0.28 (n=273) — both stronger; same
  burst-mediation caveat (class axis is burst-dominated). NB tally unchanged: still 2 axis-kinds (orientation,
  spatial), retinal arc retains independent value.
**NET (complete):** the bounded-negative stands, fully sharpened — EC≠CA3 in raw fingerprint (LARGE, robust
n=659), 100% via intrinsic state-invariant burstiness; pillar-1 GUE poles hold in EC where powered; no
attractor-topology-specific signature. Banked: hc3_analysis_*.txt, hc3_ec_pillar1.txt, hc3_ec_pillar1.py.

---

## 2026-05-29 — What does per-cell ks_gue MEASURE? burst↔ks_gue coupling is SUBSTRATE-specific

**Frame.** The hc-3 burst-control found EC-vs-CA3 ks_gue collapses to the burst axis (ks_gue~burst ρ=0.78).
That raised the program-wide question: is ks_gue (the per-cell I.5q axis used as "universality class" across
ALL neural substrates incl. the H1/pillar-2 work) just a burstiness re-encoding everywhere? Tested on banked
burst+ks_gue (excitatory) across the 3 substrates that have both: hc-3 (EC/CA3/DG), 000638 (MEC/CA1/DG),
Allen-HPF (CA3/CA1/DG). NO new data.

**NOT universal — substrate-specific, by a wide margin:**
- hc-3 (tetrode, task, ~0.3 Hz): burst↔ks_gue ρ=**+0.78** (CA3 +0.80).
- 000638 (Neuropixels, task, ~0.5 Hz): ρ=**+0.44**.
- Allen-HPF (Neuropixels, spontaneous, ~3 Hz): ρ=**−0.08** (CA3 −0.13).
The SAME region (CA3) gives ρ=+0.80 in hc-3 vs −0.13 in Allen.

**It is NOT rate-gating — the pooled "rate crossover" is a SIMPSON'S-PARADOX artifact.** A pooled (all-3-
substrate) rate-binned analysis showed an apparent crossover (ρ≈+0.31 below 1 Hz → ≈−0.09 above), which
looked like rate-gated coupling. But WITHIN each substrate the coupling is ~rate-INVARIANT at its own level
(hc-3 +0.68→+0.83 across 0.04–1.5 Hz; 000638 ~+0.44 across 0.1–1.8 Hz; Allen ~0 to −0.24 across 0.2–10 Hz).
The pooled crossover was manufactured by substrate-sorting (low-rate bins = hc-3/000638 = high coupling;
high-rate bins = Allen = zero coupling) — a clean cautionary tale: **testing a within-cell relationship on
POOLED multi-substrate data can manufacture a spurious covariate-dependence that vanishes within-substrate.**

**Implications (program-wide):**
1. **Per-cell ks_gue is a SUBSTRATE-RELATIVE readout** — what it reflects about a cell ranges from ~80% burst
   (hc-3 tetrode/task) to burst-INDEPENDENT (Allen NPx/spont). So "ks_gue = universality class" cannot be
   interpreted identically across substrates; cross-substrate per-cell ks_gue comparison is fraught (another
   reason the 000638-vs-Allen bridge failed — [[cross_substrate_validity_bridge]]).
2. **The hc-3 EC-vs-CA3 burst-collapse is hc-3-specific** (valid there, where ks_gue IS burst-dominated) —
   NOT a universal "ks_gue=burst" law.
3. **REASSURING for the Allen/V1 H1/pillar-2 work:** in Allen ks_gue is burst-INDEPENDENT (ρ≈0), so the
   H1 (OSI↔ks_gue) and pillar-2 (selectivity↔ks_gue) findings on Allen/Neuropixels data are NOT a hidden
   burst confound. The burst-confound worry is real for low-rate tetrode/task data, absent for the NPx/spont
   regime where H1 was established.
4. ks_gue is also rate-correlated in the pooled set (rate↔ks_gue ρ=+0.36), but this too is partly substrate-
   confounded — rate-match WITHIN substrate remains the discipline ([[ars_rate_dependence_lesson]]).

Banked: figures/P_burst_ksgue_substrate_specific.png. Analysis-only (banked dr-port/allen-hpf/hc3-port
cells). Verdicts Will's.

**V1 H1 burst-control closure (2026-05-29).** Per the "reassuring for H1" hypothesis, computed burst_frac on
the original H1 substrate (Allen V1, VISp, drifting_gratings; n=2144 cells; allen_v1_burst.py — burst was
never banked in allen-depth). Results:
- **OSI↔ks_gue (H1) ρ=+0.479** (reproduces the prior +0.47).
- **OSI↔burst_frac ρ=+0.029 (n.s., p=0.18)** — OSI is **burst-INDEPENDENT** in V1.
- **burst↔ks_gue ρ=+0.25** — V1/gratings ks_gue has SOME burst component (intermediate: hc-3 0.78 ≫ V1
  0.25 ≫ Allen-spont 0).
- **OSI↔ks_gue BURST-RESID ρ=+0.496** — controlling for burst, H1 is UNCHANGED (slightly stronger).
**⇒ H1 is NOT a burst confound. The extrinsic-selectivity↔class link is orthogonal to the burst axis** —
even where ks_gue has a modest burst component, OSI picks out the non-burst variation. This ties the whole
thread together: *intrinsic* region differences (hc-3 EC-vs-CA3) ride the burst axis and COLLAPSE under
burst-control; the *extrinsic* selectivity↔class link (H1, pillar-2) is BURST-ORTHOGONAL and holds. Strong
empirical support for [[intrinsic_vs_extrinsic_predictor]] at scale: intrinsic-axes are tautological/burst-
mediated, extrinsic-axes (OSI, spatial-info) are not — the H1/pillar-2 program rests on the burst-orthogonal
extrinsic side. Banked: coordinates/v1-burst-osi.jsonl; figures/P_v1_h1_burst_control.png; allen_v1_burst.py.
