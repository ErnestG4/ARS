# RQ1-c seal: theory-light predictions at X = 10¹² — STATUS: DRAFT for Will (round 95). Not sealed; nothing at 10¹² read

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

## 2. The four predictions

### P1 — replication of B2 at 10¹²
- **Rule:** the round-90 T rule plus guard on the 10¹² cells β ∈ {0.40, 0.45}: T = Σ D_c/(s_c·SE_diff,c) > t and no
  D_c < −2 s_c SE_diff,c. **t recalibrated** by witnesses at the 10¹² matched N (≈ 3.76·10¹⁰), selection and fresh-seed
  confirmation as in rounds 89–90 (null false PASS ≤ 5/100, planted PASS ≥ 90/100).
- **Reduced-N witnesses** (N = 10⁹, the same K) are used if the SE check passes: empirical/model SE_diff at full and
  reduced N agree within 20% at K for β = 0.40, 0.45 and 0.55 (10 replicates each at full N, binned estimator).
- **Power** (`results/RQ1C_POWER.json`): with D(10¹²) from the P2 laws, T's mean is 6.1 / 5.5 / 3.0 against t ≈ 3.8,
  **power 0.89 / 0.82 / 0.34** (1/log X, 1/log² X, X^{−δ}). Under the steepest law P1 is not powered. *Open choice
  for Will:* accept, or add cells (e.g. β 0.35–0.50 in steps of 0.05) to raise T's power under X^{−δ}.

### P2 — scaling of D: **UNPOWERED at every candidate cell** (separability table)
`rq1c_p2.py` → `results/RQ1C_P2.json` (ρ = 0.09 nesting correlation; ρ = 0.23 sensitivity in `RQ1C_P2_rho023.json`,
same verdicts). Predictions for D(10¹²), each law fitted to 10¹⁰ and 10¹¹:

| β | D(10¹⁰) | D(10¹¹) | SE at 10¹² | 1/log X | 1/log² X | X^{−δ} | largest pairwise separation | P2 |
|---|---|---|---|---|---|---|---|---|
| 0.40 | +0.039 ± 0.026 | +0.022 ± 0.017 | 0.011 | +0.024 | +0.022 | +0.013 | 0.54 SE | UNPOWERED |
| 0.45 | +0.047 ± 0.019 | +0.025 ± 0.012 | 0.007 | +0.028 | +0.025 | +0.013 | 1.18 SE | UNPOWERED |
| 0.55 | +0.076 ± 0.009 | +0.064 ± 0.005 | 0.003 | +0.060 | +0.054 | +0.054 | 2.37 SE | UNPOWERED |
| 0.60 | +0.037 ± 0.006 | +0.030 ± 0.003 | 0.0015 | +0.028 | +0.025 | +0.024 | 1.90 SE | UNPOWERED |

- Separability bar: |pred_a − pred_b| ≥ 3·SE_ab, SE_ab² = Var(pred_a − pred_b) + Var(D₁₂). No pair reaches it. The
  X^{−δ} law's δ from two points carries most of the error; the 1/log X vs 1/log² X pair is limited by the 10¹⁰ SE.
- **As round 95 specifies, P2 is UNPOWERED and carries no verdict.** It can be kept as a descriptive report (the three
  pre-committed predictions and windows are in the JSON). *Open choice:* drop P2, or redesign (e.g. pool the crossover
  band β 0.53–0.62 of the fine grid into one statistic; not computed).

### P3 — crossover location
- **Statistic:** on the collapse fine grid (β 0.45–0.65, step 0.01, `rq1_collapse.py` at 10¹²), the first β where the
  residual R_ℤ[√2](K) − R_ℤ[i](aK) goes from ≤ 0 to > 0, located by linear interpolation; resolution = the residual's
  model SE / |slope| at the crossing.
- **Prediction:** the location lies in **[0.51, 0.54]**.
- **From 10¹⁰ / 10¹¹:** 0.525 ± 0.009 and 0.529 ± 0.005; at 10¹² the resolution is ≈ 0.003 if the slope is unchanged,
  so the window spans about ±5 resolution units. PASS iff the location is in the window; no crossing in [0.45, 0.65]
  is FAIL.
- **Witness (to build):** a planted crossing at a known β (two-component jittered-lattice sets whose rescaled residual
  changes sign there) and a no-crossing null, at reduced N.

### P4 — ℤ[ω]
- **Expected separations** (`results/RQ1C_POWER.json`): D_ωi = 0.283·D_√2i (log a_ω / log a_√2, C_ω = log 27, round
  93; UNVERIFIED externally), D_√2ω = 0.717·D_√2i.

| Cell | 10¹⁰ D_ωi / SE | 10¹¹ | 10¹² (1/log X law) | D_√2ω / SE at 10¹⁰ / 10¹¹ / 10¹² |
|---|---|---|---|---|
| β 0.40 | 0.42 | 0.37 | 0.62 | 1.05 / 0.93 / 1.58 |
| β 0.45 | 0.72 | 0.60 | 1.11 | 1.83 / 1.52 / 2.82 |
| β 0.55 (crossover) | 2.47 | 3.72 | 6.39 | 6.27 / 9.42 / 16.2 |

- **The ordering in the rigidity cells, as specified, is UNPOWERED** (R_ℤω − R_ℤi below 1.2 SE at every X). At the
  crossover cell it is powered at 10¹¹ and 10¹² (3.7 and 6.4 SE). *Open choice:* gate the ordering at β = 0.55 (with
  its own null and planted witnesses; three-set designs), keep the rigidity cells descriptive.
- **Crossover ratio D_ωi / D_√2i against 0.28.** The collapse error at the crossover was 0–30% on D/shift (round 92).
  If that error is common to both pairs it cancels in the ratio; if not, it allows ±30%. The ratio's statistical SE at
  10¹² is ≈ 15% (D_ωi at 6.4 SE). *Recommendation:* descriptive, since no measured basis separates the common and
  field-specific parts of the 0–30%.

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

## 4. Order (to be fixed at sealing)
Archives complete and hashed → witnesses → seal approved → OTS stamp → Bitcoin attestation verified on two explorers →
`sha256sum -c` on spot (code, JSONs, manifests, segments, mount guard) → double read under caps → `cmp`.
