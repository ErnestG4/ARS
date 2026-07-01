# Tier-2 verification — long-range unfold (unit-mean/raw vs density-adaptive guarded)

Question: for each EXPOSED Family-II site, does switching from the banked unit-mean/raw path (axes.py II.1/II.2, NO internal unfold) to the guarded density-adaptive poly-unfold (`longrange_verdict`) CHANGE Σ²(L) and/or the verdict?

Params: n_seeds=8, n_ref=1500, guarded unfold_deg default=6 (swept 3/6/10/15 for lens sensitivity). MIN_N_LONGRANGE=200.


## SANITY GATE — homogeneous Poisson (np.cumsum(rng.exponential(size=3000)))

Flat-density control where unit-mean IS correct → both paths must read ≈Poisson (Σ²≈L).

- L (matched) = 50.000
- banked Σ²(unit_mean) = 39.175
- guarded Σ²(obs)     = 42.590
- Poisson ref mean    = 42.233  |  GUE ref mean = 0.906
- guarded verdict     = **POISSON_INDEP**
- GATE: both read ≈Poisson (Σ²≈L≈50.000) → PASS


## Per-site results


### mertens_signchanges
- source: data/phase34a_results/mertens_signchanges_N10000000.npz['signchanges']; fed at phase34a nns/family-II via unit-mean
- status: **OK**
- n = 3866  |  L(matched) = 50.000
- banked (unit_mean): Σ²(L) = 4868.892, Δ₃(L) = 77.313
- guarded (poly-unfold deg6): Σ²(obs) = 3024.713, verdict = **SUPER_POISSON**
- refs: GUE Σ²=0.906, Poisson Σ²=42.233 | z_vs_GUE=13691.83, z_vs_Poisson=275.81
- Σ² banked/guarded ratio = 1.61×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['SUPER_POISSON']
  - per-degree Σ²(obs)/verdict: deg3: 4345.494/SUPER_POISSON; deg6: 3024.713/SUPER_POISSON; deg10: 3390.923/SUPER_POISSON; deg15: 2090.766/SUPER_POISSON
- CONCLUSION: Σ² changes MATERIALLY (1.61×); guarded verdict lens-INVARIANT.

### liouville_signchanges
- source: data/phase34b_results/liouville_signchanges_N1000000000.npz['signchanges']
- status: **UNDERPOWERED**
- note: n=133 < MIN_N_LONGRANGE=200
- n = 133

### brocot/golden(depth8)
- source: brocot_landscape.py:52 / brocot_approximability.py:83 — RAW partials predict_partials([1,0.618034],[8,8]); n=343
- status: **OK**
- n = 343  |  L(matched) = 6.860
- banked (raw): Σ²(L) = 0.189, Δ₃(L) = 0.013
- guarded (poly-unfold deg6): Σ²(obs) = 0.635, verdict = **RIGID_GUE**
- refs: GUE Σ²=0.576, Poisson Σ²=5.981 | z_vs_GUE=0.49, z_vs_Poisson=-4.85
- Σ² banked/guarded ratio = 0.30×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['RIGID_GUE']
  - per-degree Σ²(obs)/verdict: deg3: 0.526/RIGID_GUE; deg6: 0.635/RIGID_GUE; deg10: 0.445/RIGID_GUE; deg15: 0.635/RIGID_GUE
- CONCLUSION: Σ² changes MATERIALLY (0.30×); guarded verdict lens-INVARIANT.

### brocot/liouville(depth8)
- source: brocot_landscape.py:52 / brocot_approximability.py:83 — RAW partials predict_partials([1,0.110001],[8,8]); n=345
- status: **OK**
- n = 345  |  L(matched) = 6.900
- banked (raw): Σ²(L) = 0.958, Δ₃(L) = 0.034
- guarded (poly-unfold deg6): Σ²(obs) = 1.618, verdict = **INTERMEDIATE**
- refs: GUE Σ²=0.579, Poisson Σ²=6.123 | z_vs_GUE=7.28, z_vs_Poisson=-3.29
- Σ² banked/guarded ratio = 0.59×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['INTERMEDIATE']
  - per-degree Σ²(obs)/verdict: deg3: 1.783/INTERMEDIATE; deg6: 1.618/INTERMEDIATE; deg10: 1.350/INTERMEDIATE; deg15: 1.165/INTERMEDIATE
- CONCLUSION: Σ² changes MATERIALLY (0.59×); guarded verdict lens-INVARIANT.

### brocot/pi_minus_3(depth8)
- source: brocot_landscape.py:52 / brocot_approximability.py:83 — RAW partials predict_partials([1,0.141593],[8,8]); n=345
- status: **OK**
- n = 345  |  L(matched) = 6.900
- banked (raw): Σ²(L) = 1.256, Δ₃(L) = 0.033
- guarded (poly-unfold deg6): Σ²(obs) = 1.385, verdict = **INTERMEDIATE**
- refs: GUE Σ²=0.579, Poisson Σ²=6.123 | z_vs_GUE=5.65, z_vs_Poisson=-3.46
- Σ² banked/guarded ratio = 0.91×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['INTERMEDIATE']
  - per-degree Σ²(obs)/verdict: deg3: 2.257/INTERMEDIATE; deg6: 1.385/INTERMEDIATE; deg10: 1.458/INTERMEDIATE; deg15: 1.443/INTERMEDIATE
- CONCLUSION: Σ² not materially changed; guarded verdict lens-INVARIANT.

### allen/VISp/natural_scenes/u915960569
- source: allen_depth_fam2.py:47-48 unit_mean(train); session 732592105
- status: **OK**
- n = 98416  |  L(matched) = 50.000
- banked (unit_mean): Σ²(L) = 94.125, Δ₃(L) = 3.930
- guarded (poly-unfold deg6): Σ²(obs) = 286.725, verdict = **SUPER_POISSON**
- refs: GUE Σ²=0.906, Poisson Σ²=42.233 | z_vs_GUE=1294.19, z_vs_Poisson=22.61
- Σ² banked/guarded ratio = 0.33×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['SUPER_POISSON']
  - per-degree Σ²(obs)/verdict: deg3: 331.917/SUPER_POISSON; deg6: 286.725/SUPER_POISSON; deg10: 307.848/SUPER_POISSON; deg15: 298.584/SUPER_POISSON
- CONCLUSION: Σ² changes MATERIALLY (0.33×); guarded verdict lens-INVARIANT.

### allen/VISp/natural_movie_three/u915960569
- source: allen_depth_fam2.py:47-48 unit_mean(train); session 732592105
- status: **OK**
- n = 89527  |  L(matched) = 50.000
- banked (unit_mean): Σ²(L) = 99.925, Δ₃(L) = 3.292
- guarded (poly-unfold deg6): Σ²(obs) = 492.735, verdict = **SUPER_POISSON**
- refs: GUE Σ²=0.906, Poisson Σ²=42.233 | z_vs_GUE=2227.01, z_vs_Poisson=41.66
- Σ² banked/guarded ratio = 0.20×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['SUPER_POISSON']
  - per-degree Σ²(obs)/verdict: deg3: 503.510/SUPER_POISSON; deg6: 492.735/SUPER_POISSON; deg10: 525.690/SUPER_POISSON; deg15: 552.220/SUPER_POISSON
- CONCLUSION: Σ² changes MATERIALLY (0.20×); guarded verdict lens-INVARIANT.

### allen/VISrl/natural_scenes/u915966387
- source: allen_depth_fam2.py:47-48 unit_mean(train); session 732592105
- status: **OK**
- n = 88795  |  L(matched) = 50.000
- banked (unit_mean): Σ²(L) = 92.053, Δ₃(L) = 3.558
- guarded (poly-unfold deg6): Σ²(obs) = 496.571, verdict = **SUPER_POISSON**
- refs: GUE Σ²=0.906, Poisson Σ²=42.233 | z_vs_GUE=2244.37, z_vs_Poisson=42.01
- Σ² banked/guarded ratio = 0.19×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['SUPER_POISSON']
  - per-degree Σ²(obs)/verdict: deg3: 446.096/SUPER_POISSON; deg6: 496.571/SUPER_POISSON; deg10: 467.658/SUPER_POISSON; deg15: 428.676/SUPER_POISSON
- CONCLUSION: Σ² changes MATERIALLY (0.19×); guarded verdict lens-INVARIANT.

### pvc-11/monkey1_spontaneous/u66
- source: phase2b_recompute.py:92 unit_mean(concatenated_spikes); monkey1_spontaneous unit 66
- status: **OK**
- n = 27542  |  L(matched) = 50.000
- banked (unit_mean): Σ²(L) = 214.250, Δ₃(L) = 7.671
- guarded (poly-unfold deg6): Σ²(obs) = 460.730, verdict = **SUPER_POISSON**
- refs: GUE Σ²=0.906, Poisson Σ²=42.233 | z_vs_GUE=2082.09, z_vs_Poisson=38.70
- Σ² banked/guarded ratio = 0.47×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['SUPER_POISSON']
  - per-degree Σ²(obs)/verdict: deg3: 432.468/SUPER_POISSON; deg6: 460.730/SUPER_POISSON; deg10: 429.997/SUPER_POISSON; deg15: 423.496/SUPER_POISSON
- CONCLUSION: Σ² changes MATERIALLY (0.47×); guarded verdict lens-INVARIANT.

### pvc-11/monkey1_spontaneous/u58
- source: phase2b_recompute.py:92 unit_mean(concatenated_spikes); monkey1_spontaneous unit 58
- status: **OK**
- n = 24413  |  L(matched) = 50.000
- banked (unit_mean): Σ²(L) = 218.367, Δ₃(L) = 9.187
- guarded (poly-unfold deg6): Σ²(obs) = 409.399, verdict = **SUPER_POISSON**
- refs: GUE Σ²=0.906, Poisson Σ²=42.233 | z_vs_GUE=1849.66, z_vs_Poisson=33.95
- Σ² banked/guarded ratio = 0.53×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['SUPER_POISSON']
  - per-degree Σ²(obs)/verdict: deg3: 482.135/SUPER_POISSON; deg6: 409.399/SUPER_POISSON; deg10: 431.812/SUPER_POISSON; deg15: 438.945/SUPER_POISSON
- CONCLUSION: Σ² changes MATERIALLY (0.53×); guarded verdict lens-INVARIANT.

### pvc-11/monkey1_spontaneous/u32
- source: phase2b_recompute.py:92 unit_mean(concatenated_spikes); monkey1_spontaneous unit 32
- status: **OK**
- n = 23186  |  L(matched) = 50.000
- banked (unit_mean): Σ²(L) = 158.105, Δ₃(L) = 7.422
- guarded (poly-unfold deg6): Σ²(obs) = 442.538, verdict = **SUPER_POISSON**
- refs: GUE Σ²=0.906, Poisson Σ²=42.233 | z_vs_GUE=1999.71, z_vs_Poisson=37.02
- Σ² banked/guarded ratio = 0.36×
- lens sweep (deg 3/6/10/15): **INVARIANT** verdicts=['SUPER_POISSON']
  - per-degree Σ²(obs)/verdict: deg3: 432.984/SUPER_POISSON; deg6: 442.538/SUPER_POISSON; deg10: 438.135/SUPER_POISSON; deg15: 469.228/SUPER_POISSON
- CONCLUSION: Σ² changes MATERIALLY (0.36×); guarded verdict lens-INVARIANT.

## Blocked

- (none)
