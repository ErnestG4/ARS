# Survey arc D0+D1 log (2026-08-15)

## D0 — sealed decisions (derivations in acquire.py docstring)
- Q1: **LRG NGC, primary slice 0.6–0.8** (in-slice: n=533,955, W=536,803 → 155/deg² eff,
  ~10.5k/tile; the nz-header power estimate of 197/deg² overcounted via bin edges — power
  still ≥70σ class separation everywhere). Comparison slice 0.4–0.6. **BGS fallback dry-run
  DISCHARGED** (loader + power row; 4× denser; not needed).
- Q3: **v1.5, NGC only.** Q4: **r_min = 0.05°** (DESI positioner patrol scale;
  arXiv:2404.03006, 2406.04804, 2411.12025).
- Randoms: 8 of 18 files, sealed disjoint halves (even=KAG, odd=null), ~25× data each.
- MANIFEST.json: 11 files, SHA256 + row counts (9.39M/randoms file = 2500/deg²·footprint ✓).

## D1 — window engineering + mask KAG
- Tiling: 28 accepted 10°×10° gnomonic tiles (corner distortion 1.54% ≤ 2% budget;
  MIN_EFF_FRACTION 0.60). Accepted-tile declination range −10°..+45° (centers −5..+35);
  higher-dec rows fail the fill fraction as the footprint narrows — excluded by rule.
- **Mask KAG: PASS, with one estimator-null defect caught and fixed first — three events:**
  1. **First green run FAILED** (worst |z| 5.52; every tile's F at +3–7%): the gate fired on
     Poisson-through-the-real-window data — no science measurement existed yet.
  2. **Diagnosis (derivable, not tuned):** two missing terms in the estimator null model:
     (a) randoms shot noise in the cell expectations — Var(N−E) = w̄₂_D·Ē + (W_D/W_R)·w̄₂_R·Ē;
     the second term is ≈+4% at 25× randoms density, matching the observed offset;
     (b) weighted-pair z calibration — raw √DD understates σ for weighted pairs; replaced by
     effective counts DD²/Σ(pairweight²) on both DD and RR sides, plus the small-mean Poisson
     4th-moment term in σ_F. **Null-model corrections, not tolerance changes** — the arms
     (worst |z| ≤ 4.5, self-calibrated grand-mean) are untouched.
  3. **Re-run PASS:** worst |z| 3.43, grand mean +0.558 (thr 0.642), F both sides of 1.
- **Red path fired at |z| = 130** (F(1°) = 15–19 under the forbidden uniform-box window):
  the witness can fail, demonstrated deliberately, per §6.
- **Projection twin:** KAG tiles at the accepted-range declination extremes (−5°, +35°) all
  green — the gnomonic budget covers what it claims over the range that will be measured.
- **Q5 DECISION: randoms-backed MC geometry is sufficient at KAG grade** — the full
  ratio-estimator stack nulls correctly against the real window with no pixelized-mask
  hybrid; hybrid not built. Filed per brief §8.5.
- Watch item for D3 (filed, not fixed): F(L=1.0°) leans low across tiles (0.82–1.08,
  mean ≈ 0.93) — within the arms, but the largest-L cells interact with tile edges and the
  adjacency clause; revisit when sealing the D3 R-range.
