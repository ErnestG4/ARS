# FN1 stage-2 seal: the field ladder on the fresh slice (10¹⁰, 10¹¹]. PROPOSED, NOT SEALED (for Will's review)

**Brief:** Will, 2026-11-02 (filed verbatim). "Stage 2 (10¹¹): draft a seal only after item 2. Primary replication on the
fresh part (10¹⁰, 10¹¹]; a residual-by-L′/L prediction if item 2 supports one; −7's displacement as a stated
prediction. Price the archives; no compute before review."

**Item 2 is done** (`lead/FN1_LEAD_LPRIME.md`). It does not support a residual-by-L′/L prediction, at L′/L(1) or in
Chen's L′/L(2) form, so this draft carries none.

**No stage-2 compute has been run.** The only stage-2 numbers here are parametric: `lead/fn1_stage2_power_sketch.py`,
which uses the stage-1 read values and the sealed SE model, and no new data.

**Order (as stage 1):** archives generated and hashed → witnesses → §9.F dry run → Will's review → seal → stamp →
Bitcoin attestation verified on two explorers → double read → `cmp` → verdicts. The verdict lines go to files and are
not viewed before the `cmp`.

## 1. Data

**Fresh slice.** For every field, rows [n₁₀, n₁₁) of its split-prime list in prime order:
- n₁₀ = 227,524,967 and n₁₁ = 2,059,026,114, the ℤ[√2] split-prime counts below 10¹⁰ and 10¹¹ (RQ1 `read1.json`);
- n_f = 1,831,501,147 rows, so N_f = 3,663,002,294 points with the mirror;
- K = round(N_f^β): **182,016** (β 0.55), 20,125 (0.45), 6,692 (0.40).

The rows are disjoint from stage 1. The fresh slice shares no data with the stage-1 statistic.

**Statistic.** R_F(β) = var_stream(θ, K)/(N_f/K), exact, with the sealed `rq1_read.var_stream`. Fields, C_F and angle
maps are as stage-1 §1.

**Archives.**
- **The seven w = 2 fields** extend `/mnt/data/fn1/archive_1e10_D*` to 1.01·10¹¹ with contiguous segments and the same
  generator and integrity checks (`fn1_archive.py`, unchanged).
- **Prefix check:** the stage-1 segment hashes must re-verify byte-identically. Then only new segments are generated.
- **The 1% margin covers row n₁₁ in every field**, as at stage 1, where it gave 229.7M rows against 227.5M needed.
- **ℤ[i], ℤ[ω], ℤ[√2]:** the pinned RQ1-c 10¹² archives, as prefixes.

**Pins.** All ten manifest sha256 values go in `fn1_pins2.json`, sealed with this text.

## 1b. Prior exposure

| What | Seen where | Relation to the fresh-slice statistic |
|---|---|---|
| All nine fields, R at β 0.40 / 0.45 / 0.55 on rows [0, n₁₀) | FN1 stage 1 | disjoint rows |
| ℤ[√2], ℤ[i]: R at 10¹¹, full range rows [0, n₁₁), on RQ1's β grid | RQ1 read, RQ1-c REPRO, L13 | the fresh slice is 89% of those rows, so their fresh-slice R is **largely predictable** from seen values |
| ℤ[ω]: R at 10¹¹, full range, β 0.40 / 0.45 / 0.55 | RQ1-c read | the same: largely predictable |
| The seven w = 2 fields beyond row n₁₀ | never generated | **fresh** |

So stage 2 is fresh for seven of nine fields and partly seen for ℤ[i], ℤ[ω] and ℤ[√2]. As at stage 1, a fresh-only ρ_s
on the seven w = 2 fields is reported descriptively. It is unpowered at n = 7 (needs ρ_s ≥ 0.893).

## 2. Predictions and rules (proposed)

**Primary: replication.** Spearman ρ_s between C_F and R_F at β = 0.55 on the fresh slice, across the nine fields.
- PASS iff the exact one-sided permutation p < 0.01 and ρ_s > 0: Σd² ≤ 26 (ρ_s ≥ 0.7833, p = 0.0086), over 9!
  orderings. Otherwise FAIL, read as in §3a.

**Secondary (β 0.45, β 0.40).** The same rule, each reported separately. Their labels are set from the power table
computed before sealing (§3).

**ℤ[√2] placement.** PASS iff R_−67 < R_ℤ[√2] < R_−163 at β 0.55. Reported with the stage-1 caveat: the margin was below
the per-field noise, and a middle placement by chance is about 1 in 3.

**−7 displacement (stated prediction).** At stage 1, −7 has the lowest C_F but ranks fifth. Its linear residual on C_F
is +0.035, the largest of the nine. It sits above its two nearest-C neighbours −8 and −11, which C_F orders above it.
- **Prediction:** at β 0.55 on the fresh slice, **R_−7 > R_−8 and R_−7 > R_−11**.
- PASS iff both inequalities hold; otherwise FAIL.
- **Proposed reading rule** (the analogue of §3a; Will's call): the PASS counts as informative only if the
  "no-displacement" false-PASS rate at the read-time noise is ≤ 0.05. Above that, a PASS is reported as "PASS (not
  separated from the C-ordered null at the read-time noise)".
- A FAIL is informative whenever the power under persistence is ≥ 0.80.

**Descriptive (no verdict).**
- ρ_s against log|D|, and the near-equal-C pairs, as at stage 1.
- The fresh-only seven-field ρ_s.
- The linear residuals on C_F, and their stage-1 versus stage-2 correlation: does the U-shape persist?
- The Chen-form ordering P_F (with and without A′) from `lead/FN1_CHEN_LTERM.json`, as a fit comparison only. No
  verdict, since item 2 found no support.
- Segment noise at all three β, raw and detrended.

**Ties.** Any exact tie in a compared set means that test is VOID (ties).

**VOID (any one voids the read):**
- any pin mismatch;
- the stage-1 prefix hashes not re-verifying;
- `/mnt/data` not mounted;
- an exact tie;
- the double read not byte-identical under `cmp`.

## 3. Power (parametric sketch; to be finalised, with the B2 cells, before sealing)

**Model.** R_F = a + b·C_F (+ δ on −7) + σε, where:
- σ = the sealed SE model at the stage-2 K (0.00342 at β 0.55, which is 0.56× stage 1's) × a noise scale;
- the scales are 1×, 1.71× (the stage-1 detrended segment ratio) and 3.37× (the stage-1 raw sealed ratio);
- b = the stage-1 OLS slope 0.0455, or Chen's 1/log 10¹¹ = 0.0395;
- δ = +0.0352 (the stage-1 −7 residual);
- 200,000 seeded replicates.

| Scale | b | Primary power, δ = 0 | Primary power, δ = 0.035 | −7 prediction: power (δ persists) | −7 prediction: false-PASS rate (δ = 0) |
|---|---|---|---|---|---|
| 1× | 0.0455 | 1.000 | 1.000 | 0.999 | 0.000 |
| 1.71× | 0.0455 | 1.000 | 0.999 | 0.961 | 0.005 |
| 3.37× | 0.0455 | 1.000 | 0.946 | 0.798 | 0.074 |
| 1× | 0.0395 | 1.000 | 1.000 | 1.000 | 0.000 |
| 1.71× | 0.0395 | 1.000 | 0.988 | 0.982 | 0.011 |
| 3.37× | 0.0395 | 0.999 | 0.855 | 0.842 | 0.096 |

**Reading.**
- The primary is powered at every scale considered.
- The −7 prediction is powered at every scale.
- It separates from the null only below roughly 2.5–3× noise. That is why the reading rule above is proposed.

**The stage-1 β 0.40 and 0.45 slopes were a third of β 0.55's** (0.013–0.014 per unit C). So their stage-2 power must
use those slopes, not 0.0455. That goes in the pre-seal table.

### 3a. Read-time noise rule

- **Rule:** the stage-1 §3a estimator unchanged, on the fresh slice: 8 prime-order segments per field, raw relSD
  pooled over the nine fields.
- **Interpretation:** as stage 1. Primary power at the read-time noise ≥ 0.80 means a FAIL is informative; < 0.80
  means FAIL (UNPOWERED).
- **The same noise also sets the −7 reading:** the false-PASS rate and the power above.
- **Drift:** the stage-1 drift along prime order inflates the raw estimate about 2×. The detrended estimate is
  reported descriptively. Changing the rule to it would be a design change, so it is listed in §8 for Will.

## 4. Witnesses (as stage 1, at stage-2 K)

- **Null (slope 0):** must PASS at about α.
- **Planted target** at b = 0.0455: must PASS at the power table's rate.
- **Shuffled C:** must FAIL.
- **−7 must-fail witness:** the C-ordered null with δ = 0, at the read-time noise rule. Its false-PASS rate must match
  the table.
- **−7 must-pass witness:** δ = +0.035.
- All parametric plus the stage-1 planted-set machinery: about 1–2 core-h.

## 5. §9.F rehearsal

- **Dry archives:** synthetic rows for the seven w = 2 fields (`fn1_dry_archives.py`) at stage-1 size, plus **one
  full-size synthetic field.** That one checks the memory peak (about 45 GB: a 29 GB θ array and a 15 GB half copy) and
  the timing on the real code path.
- **Double dry read,** byte-identical under `cmp`.
- **Red paths:**
  - a flipped segment byte, including in the stage-1 prefix → AssertionError, no output;
  - an altered pin → AssertionError;
  - an exact tie → VOID;
  - the stage-1 prefix hash check fired on a modified prefix segment.
- **Real fresh data:** none is read before the seal.

## 6. Attribution, fixed before the read

As stage-1 §6, including Will's class-number note: a PASS supports log(w²|D|) and does not separate conductor from
L(1,χ). Plus:

- **Primary PASS at stage 2:** the C_F ordering replicates on disjoint data, about 8× larger than stage 1.
- **Primary FAIL (informative):** the stage-1 PASS does not replicate on the fresh slice, and this is reported as a
  failure to replicate.
- **−7 PASS (informative):** a field-specific displacement beyond C_F persists. Its cause is open. It is not L′/L(1)
  and not Chen's L′/L(2) term at the size computed (`lead/FN1_LEAD_LPRIME.md`). −7 is the only field here with 2 split.
- **−7 FAIL:** the stage-1 displacement is not stable. It is read as noise or prime-range drift.

## 7. Price (spot core-hours; nothing run)

**Archive increment.** The seven w = 2 fields, (1.01·10¹⁰, 1.01·10¹¹], about 1.85·10⁹ new rows each, about 1.29·10¹⁰ in
all. Two routes:
- the stage-1 measurement (14.24 core-h for 7 × 229.7M rows) × the row ratio (8.0) × the log p cost growth (about 1.1)
  gives about 125 core-h;
- Step 0's model, calibrated by stage 1's measured/model 0.897, minus the prefix, gives about 143–174.

| Item | Core-h | Wall / memory / disk |
|---|---|---|
| Archive increment | **about 125–175** | about 5–6 h at 28 processes (load-checked first; spot is shared); about 105 GB on `/mnt/data` (403 GB free) |
| Prefix re-verification and pre-archive checks | under 0.5 | |
| Witnesses (parametric) | about 1–2 | |
| §9.F rehearsal (seven small synthetic fields + one full-size) | about 3 | 45 GB peak |
| Double read (ten fields; three β plus segment noise) | about 3.2 (about 1.6 per read; scaled 8× in N and 1.1× for the sort from stage 1's 0.19) | **run one after the other**, about 45 GB peak each |
| **Total** | **about 135–185** | dominated by the archives |

## 8. Open choices for Will

1. **The −7 prediction's form.** The two-neighbour inequality is proposed. Alternatives: "the −7 linear residual > 0",
   which is weaker, or "R_−7 above ℤ[i] as well", which has about 50% power under persistence.
2. **The −7 reading rule.** Is a false-PASS rate ≤ 0.05 at the read-time noise what makes the PASS informative?
3. **The noise rule.** Keep the raw §3a estimator (proposed, for continuity), or seal the detrended one?
4. **The secondaries.** Keep β 0.45 and β 0.40 as secondaries, labelled from the pre-seal power table at their own
   (stage-1) slopes?
5. **Spot time.** About 5–6 h of 28 processes for the archives, on the shared box.
