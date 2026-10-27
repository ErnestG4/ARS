# RQ1-c seal: theory-light predictions at X = 10¹² — STATUS: DRAFT, round-96 choices applied; prerequisites (§4) pending. Not sealed; nothing at 10¹² read

New arc (round 95), two-session time box. RQ1 closes as written (round 94). Every number below comes from the 10¹⁰ and
10¹¹ results (`RQ1_FINDINGS.md`, `results/read/`, `results/collapse/`) and from synthetic witnesses; nothing at 10¹² is
read before this seal is approved, stamped and Bitcoin-attested.

## 1. Data

| Field | Archive (spot `/mnt/data/rq1/`) | Status | Seen before |
|---|---|---|---|
| ℤ[√2] | `archive_1e12_zs2`, to 10¹² | generating (round 93) | 10¹⁰, 10¹¹ (sealed read) |
| ℤ[i] | `archive_1e12_zi`, to 1.01·10¹² | queued after ℤ[√2] | 10¹⁰, 10¹¹ (sealed read) |
| ℤ[ω] | `archive_1e12_zw`, to 1.01·10¹² | queued after ℤ[i] (round 95) | only Phase 34d's X ≤ 10⁸ |

- **ℤ[ω] (stated before generating; `rq1_zw.py`, f60fb59f, committed before launch).** Split rule p ≡ 1 (mod 3),
  p = u² + 3v² with u, v > 0 (unique); π = u + v√−3. θ = (arg π mod π/3)/(π/3) ∈ [0, 1); the conjugate ideal sits at
  1 − θ (mirror). Inert and ramified primes excluded. Checked on synthetic and small-p data only (see the commit).
- **Matched N at each X:** n = the ℤ[√2] row count below X; the ℤ[i] and ℤ[ω] sets are their first n split primes.
- **The 10¹⁰ and 10¹¹ ℤ[ω] cells (P4) are also unseen;** they come from the same ℤ[ω] archive.

## 2. The four predictions (round 96 choices)

### P1 — exact replication of B2 at 10¹² (gated)
- **Rule:** the round-90 T rule plus guard on the same cells, β ∈ {0.40, 0.45}, at the 10¹² matched N:
  T = Σ D_c/(s_c·SE_diff,c) > t and no D_c < −2 s_c SE_diff,c. No added cells.
- **t is recalibrated by witnesses at the 10¹² matched N** (≈ 3.76·10¹⁰), with selection and fresh-seed confirmation
  as in rounds 89–90 (null false PASS ≤ 5/100, planted PASS ≥ 90/100). The witnesses run at N = 10⁹ with the same K
  only if the full-N SE check passes (§4); otherwise at full N (binned).
- **Power, recorded before the read** (`results/RQ1C_POWER.json`): with D(10¹²) from each P2 law, T's mean is
  6.1 / 5.5 / 3.0 against t ≈ 3.8, **power 0.89 (1/log X) / 0.82 (1/log² X) / 0.34 (X^{−δ})**.
- **Attribution.** PASS: the field difference's direction replicates at 10¹². **FAIL: consistent with the steepest
  decay law (X^{−δ}), under which P1 has power 0.34; it does not refute the 10¹⁰ / 10¹¹ PASS.**

### P2 — scaling of D (descriptive only; no gate, no redesign)
Each law fitted to D(10¹⁰) and D(10¹¹) (`rq1c_p2.py`, `results/RQ1C_P2.json`; nesting correlation 0.09). Committed
predictions for D(10¹²), as prediction ± propagated SE [consistency window ±2·SE_resid, which adds the 10¹² SE]:

| β | 1/log X | 1/log² X | X^{−δ} | model SE of D at 10¹² |
|---|---|---|---|---|
| 0.40 | +0.0244 ± 0.0134 [-0.0090, +0.0578] | +0.0219 ± 0.0119 [-0.0094, +0.0531] | +0.0131 ± 0.0212 [-0.0332, +0.0593] | 0.0111 |
| 0.45 | +0.0277 ± 0.0091 [+0.0055, +0.0499] | +0.0250 ± 0.0081 [+0.0043, +0.0456] | +0.0128 ± 0.0126 [-0.0151, +0.0407] | 0.0071 |
| 0.55 | +0.0598 ± 0.0039 [+0.0507, +0.0690] | +0.0535 ± 0.0035 [+0.0450, +0.0620] | +0.0538 ± 0.0098 [+0.0338, +0.0737] | 0.0026 |
| 0.60 | +0.0283 ± 0.0024 [+0.0228, +0.0337] | +0.0253 ± 0.0022 [+0.0203, +0.0304] | +0.0238 ± 0.0056 [+0.0124, +0.0353] | 0.0015 |

- The laws are not separable at any cell (largest pairwise separation 2.37 SE, at β 0.55; bar 3 SE). The read reports
  where the 10¹² D lands against each window. No verdict.

### P3 — crossover location (gated)
- **Statistic:** on the collapse fine grid at 10¹² (β 0.45–0.65, step 0.01; `rq1_collapse.py`'s construction), the first
  β where the residual R_ℤ[√2](K) − R_ℤ[i](aK) goes from ≤ 0 to > 0, by linear interpolation; resolution = the
  residual's model SE / |slope| at the crossing.
- **Prediction:** the location lies in **[0.51, 0.54]**. PASS iff it does; FAIL if it lies outside or no crossing
  exists in [0.45, 0.65].
- **From 10¹⁰ / 10¹¹:** 0.525 ± 0.009 and 0.529 ± 0.005; ≈ ± 0.003 expected at 10¹².
- **Witness (required before sealing):** planted crossings at known β inside and outside the window (two-component
  jittered-lattice sets at N = 10⁹ with the 10¹² K grid), and a no-crossing null. The rule must place a planted
  crossing at 0.525 inside the window in ≥ 90/100, one at 0.50 or 0.555 outside in ≥ 90/100, and report no crossing on
  the null in ≥ 90/100.

### P4 — ℤ[ω] ordering at β = 0.55 (gated); rigidity cells and the 0.28 ratio descriptive
- **Rule:** R_ℤ[√2] > R_ℤ[ω] > R_ℤ[i] at matched N at β = 0.55, at every X where the predicted ℤ[ω]–ℤ[i] separation is
  ≥ 2·SE. **That is all three X:** 2.47 SE (10¹⁰), 3.72 (10¹¹), 6.39 (10¹², 1/log X law; 5.8 under X^{−δ}). PASS iff
  both inequalities hold at all three; FAIL otherwise.
- **Witnesses (three-set, N = 10⁹ at each X's K for β = 0.55):** null, three sets at equal R (the rule's false PASS
  ≤ 5/100); planted, R levels separated by the predicted D_√2ω and D_ωi at that X (PASS ≥ 90/100). Lattice/i.i.d.
  mixtures, mirror-symmetrised.
- **Descriptive:** the ordering at β 0.40 and 0.45 (predicted ℤ[ω]–ℤ[i] separations 0.4–1.1 SE), and the ratio
  D_ωi / D_√2i against 0.283 at β 0.55.
- C_ω = log 27 is derived (round 93), not checked against a published ℤ[ω] source.

## 3. Costs (cost model; spot core-h)

| Item | Model | Notes |
|---|---|---|
| ℤ[ω] archive to 1.01·10¹² | 234 | queued; ≈ 8.4 h at 28 processes, ≈ 152 GB |
| Binned estimator (2⁻³⁶, 34 GB/field) and its validation against the exact 10¹⁰ / 10¹¹ values | ≈ 5 | new code |
| Histograms of the three 10¹² archives | ≈ 3 | I/O-bound, ≈ 1 h each |
| Read, double: P1/P2 cells 8 passes, P3 fine grid 42, P4 ℤ[ω] cells 3 (and 10¹⁰ / 10¹¹ ℤ[ω] exact) | ≈ 75 | 53 binned passes × 2,540 s × 2 |
| P1 witnesses (N = 10⁹): 200 selection + 200 confirmation replicates | ≈ 20 | i.i.d./lattice design |
| SE check at full N (3 K × 10 replicates × 2 sets, binned) | ≈ 42 | gates the use of reduced N |
| P3 witnesses (planted crossing and null, N = 10⁹) | ≈ 20 | jittered-lattice design, to build |
| P4 witnesses (three-set null and planted ordering, N = 10⁹) | ≈ 30 | if P4 is gated |
| Environment re-pin and estimator check (round 93 rule) | ≈ 1 | kernel 7.2.11 |
| **Total** | **≈ 430** | of which ℤ[ω] 234 |

## 4. Prerequisites before the seal is final (round 96)
1. **Environment re-pin — DONE.** Spot kernel 7.2.11-100.fc43; ph6c env unchanged (Python 3.12.15, numpy 2.5.3,
   scipy 1.18.1, numba 0.68.0, mpmath 1.4.1). `rq1_read_check.py` rerun there: all 9 values bit-identical to round 88
   (`results/r96/READ_ESTIMATOR_CHECK.json`).
2. **Binned estimator — DONE** (`rq1c_binned.py`; `results/r96/BINNED_VALIDATION.json`). On the rounded point set it
   equals `var_stream` exactly (relative difference 0 at 12 settings). On the read archives, with B set so that
   N·δ²·K is at least the 10¹² value at 2⁻³⁶, binned − exact is positive in all 50 comparisons, 0.007–0.25 of
   N·δ²·K, and at most 0.0008 SE at the P1/P4 cells and 0.081 SE on the P3 grid (largest at β 0.65). About 14 ns per
   bin step: ≈ 1,900 spot core-s per 10¹² pass (2,540 modelled).
3. **Full-N SE check:** empirical/model SE_diff at full N (3.76·10¹⁰, binned synthetic sets) and at N = 10⁹ agree within
   20% at K for β = 0.40, 0.45 and 0.55 (10 replicates each). Pass → reduced-N witnesses; fail → full-N witnesses.
4. **Witnesses** for P1 (t), P3 and P4, with their results and the frozen t in §6 pins.
5. **Archives complete and hashed;** manifests pinned (§6).

## 5. Order (to be fixed at sealing)
Archives complete and hashed → witnesses → seal approved → OTS stamp → Bitcoin attestation verified on two explorers →
`sha256sum -c` on spot (code, JSONs, manifests, segments, mount guard) → double read under caps → `cmp`.
