# PH2S Stage 1 — the zeros' pair-sum error bars shrink with block length beyond a long sine-kernel baseline (PH2S_SEAL 1.0)

**Status: TEXT FOR WILL'S GO.** Design decisions: fifteenth to seventeenth rounds (`ph2/PH2_DECISIONS_2026-10-07.md`). The
pre-read is complete (`results/preread/`, `results/dryrun/`). No F1 zero has been decoded. Order: Will's go → seal JSON
(`make_seal_json.py`) + seal commit + tag `ph2s-stage1-seal` → F1 md5-verified → `python s1read.py read`.

## 1. What is tested, and its standing
On the seen R₂ bins, the moving-block bootstrap SD of the pair sum's per-level contributions, after drift removal, falls
with block length. A single long GUE sequence through identical code stays near-flat. This was a candidate finding of
the exploratory long-baseline comparison (`ph2r2/PH2R2_FINDINGS.md` §6, v2). Stage 1 is the **direction-only
confirmation on fresh heights (F1)**: at matched window length, the zeros shrink more than the sine kernel. No mechanism
is claimed. Two directional predictions of the candidate mechanism are sealed as arms C and D. The quantitative
few-prime model is Stage 2, on F2.

## 2. Statistic
Per bin (one Platt file, [t₀, t₁)) and test function f_{u,w} (the R₂ family; bin-centre δ; U_MAX = 3 spacings):
- c_i = Σ_{j≠i} f(t_j − t_i) within a window, drift-removed as R₂ A3: c̃_i = c_i·e(t_c)/e(t_i);
- growth g = SD_MBB(10⁴)/SD_MBB(100) of Σc̃ (B = 400), with an independent bootstrap seed per window and per sequence;
- **zeros:** the file cut into disjoint windows of L levels from t₀; g_Z = mean over windows, with its SE;
- **baseline:** 16 Stage 1 long-GUE sequences per L (`gue_levels.py`, seeds distinct from the exploration), each mapped
  onto the bin's heights by t = N̄⁻¹(N̄(t₀) + ½ + u); g_B = mean over sequences, with its SE;
- **d = g_B − g_Z**, SE_c = √(SE_B² + SE_Z²).

## 3. Arms and verdicts (every NOT RESOLVABLE rule is precision-only: R₂ A2's lesson)
- **A (primary): f = (0.5, 0.3), L = 10⁶, the five core F1 bins.**
  - A bin SHRINKS iff it is resolvable and d > 3·SE_c.
  - Resolvable pre-data iff the power at d_ref = ½ × the smallest seen shrink (0.118) is ≥ 0.80. NOT RESOLVABLE
    (achieved) iff the achieved 3·SE_c ≥ d_ref.
  - **PASS iff ≥ 4 core bins shrink**; an unresolvable bin counts as not shrinking. **F1a is NOT RESOLVABLE pre-data**
    (power 0.708), so PASS requires **all four of F1b–F1e**.
  - Fewer than 4 resolvable core bins (achieved) gives NOT RESOLVABLE.
  - **Joint power: ≈ 0.51 at the half-size reference; ≈ 1 at the smallest seen shrink.** A FAIL is interpreted
    accordingly: it is evidence against an effect as large as seen, not against one half as large.
  - A pooled one-sided test is reported descriptively.
- **B: the same at L = 2·10⁵. Descriptive** (unresolvable pre-data in every bin: power 0.13–0.34).
- **C (mechanism i, wider bump → larger shrink):**
  - Δ_u = mean over core bins of d(u, 0.3) − d(u, 0.15), at L = 10⁶.
  - The SE of mean_u Δ_u comes from resampling units (GUE sequences jointly across bins; zeros windows within bins),
    paired across members.
  - **PASS iff Δ_u > 0 for ≥ 3 of 4 u and mean_u Δ_u > 3·SE.** It is 3 SE because the 2-SE rule's empirical
    false-positive rate (0.042) exceeded nominal (0.023) in the pre-read.
  - Empirical false-positive rate under the sealed rule: 0.014 (500 GUE-vs-GUE splits, 8 vs 8). Power at the seen Δ: 1.00.
- **D (mechanism ii, shrink weakens with height):**
  - Weighted least squares of d (primary f, L = 10⁶) on L_bin over all six F1 bins, including F1x at L ≈ 22.10.
  - **PASS iff slope + 2·SE < 0.**
  - Power at the seen slope: 0.863. Empirical false-positive rate: 0.018 (nominal 0.023).
  - The low extreme Will asked for (L ≈ 13.25) is infeasible under the gap rule.

## 4. Pre-read record (no F1 zero read)
- **Baselines:** 16 + 16 fresh GUE sequences pass sanity (mean spacing 1.000000; ⟨r̃⟩ 0.5991–0.6004). Mapped baseline
  g_B at L = 10⁶ is 0.973–0.989 across the F1 bins.
- **Power per core bin at L = 10⁶:** F1a 0.708, F1b 0.875, F1c 0.816, F1d 0.816, F1e 0.882 (F1x 0.913).
- **Specificity (GUE vs GUE, seeds 0–7 vs 8–15):** A FAIL, C FAIL, D FAIL. Over 500 random splits: A 0.000, C 0.014
  (3 SE), D 0.018.
- **Dry run through `s1read.py`:**
  - seen R zeros: A, C and D read PASS;
  - GUE stand-in: A, C and D read FAIL;
  - B is NOT RESOLVABLE in both.
- **Precision-guard witness:** fires. **Drift red path:** raw growth at F1a is inflated by the drift (1.036 vs 0.989)
  and removed by A3.

## 5. Data
F1 (`ph2r2/FRESH_SETS_F1_F3.md` v2; a ≥ 1-file gap from every touched height range). Core: zeros_10946000,
zeros_31946000, zeros_319646000, zeros_1438946000, zeros_13660946000 (L ≈ 14.46, 15.47, 17.75, 19.25, 21.50). Arm D only:
zeros_24891746000 (L ≈ 22.10). Downloaded by hand into `ph2r2/data/platt_fresh/`, md5-verified by `s1read.py` before
decoding.
