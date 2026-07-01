# Tier 1 — L-function NNS guard robustness
Canonical `(5.0, 19845)` vs banked `0.5`-guard `(0.5, inf)`. Verbatim estimator; validation-gated against banked JSON.

### lmfdb_family (EC L-functions, height 200)
- bands: 43 total; 29 admitted by 0.5-guard but dropped by canonical (f_pll range [0.125,8.000])

| group | guard | n_pool | ks_u | gap | best |
|---|---|---|---|---|---|
| all curves | 0.5-drift | 2508764 | 0.012 | +0.065 | GUE |
| all curves | canonical | 493060 | 0.010 | +0.068 | GUE |
| root_number = +1 | 0.5-drift | 2008306 | 0.012 | +0.067 | GUE |
| root_number = +1 | canonical | 394894 | 0.011 | +0.068 | GUE |
| root_number = -1 | 0.5-drift | 500458 | 0.014 | +0.056 | GUE |
| root_number = -1 | canonical | 98166 | 0.011 | +0.062 | GUE |
| rank = 0 | 0.5-drift | 2008306 | 0.012 | +0.067 | GUE |
| rank = 0 | canonical | 394894 | 0.011 | +0.068 | GUE |
| rank ≥ 1 | 0.5-drift | 500458 | 0.014 | +0.056 | GUE |
| rank ≥ 1 | canonical | 98166 | 0.011 | +0.062 | GUE |

**Validation (lmfdb_family (EC L-functions, height 200)): PASS — 0.5-repro matches banked**
**Guard-robustness:**
  - all curves: best GUE→GUE (stable); gap +0.065→+0.068
  - root_number = +1: best GUE→GUE (stable); gap +0.067→+0.068
  - root_number = -1: best GUE→GUE (stable); gap +0.056→+0.062
  - rank = 0: best GUE→GUE (stable); gap +0.067→+0.068
  - rank ≥ 1: best GUE→GUE (stable); gap +0.056→+0.062

### lmfdb_extend (EC L-functions, height 1000)
- bands: 43 total; 29 admitted by 0.5-guard but dropped by canonical (f_pll range [0.125,8.000])

| group | guard | n_pool | ks_u | gap | best |
|---|---|---|---|---|---|
| all curves | 0.5-drift | 2508764 | 0.012 | +0.065 | GUE |
| all curves | canonical | 493060 | 0.010 | +0.068 | GUE |
| root_number = +1 | 0.5-drift | 2008306 | 0.012 | +0.067 | GUE |
| root_number = +1 | canonical | 394894 | 0.011 | +0.068 | GUE |
| root_number = -1 | 0.5-drift | 500458 | 0.014 | +0.056 | GUE |
| root_number = -1 | canonical | 98166 | 0.011 | +0.062 | GUE |

**Validation (lmfdb_extend (EC L-functions, height 1000)): PASS — 0.5-repro matches banked**
**Guard-robustness:**
  - all curves: best GUE→GUE (stable); gap +0.065→+0.068
  - root_number = +1: best GUE→GUE (stable); gap +0.067→+0.068
  - root_number = -1: best GUE→GUE (stable); gap +0.056→+0.062

### dirichlet_family (Dirichlet L-functions)
- bands: 43 total; 29 admitted by 0.5-guard but dropped by canonical (f_pll range [0.125,8.000])

| group | guard | n_pool | ks_u | gap | best |
|---|---|---|---|---|---|
| all primitive non-trivial | 0.5-drift | 4051472 | 0.035 | +0.067 | GUE |
| all primitive non-trivial | canonical | 331558 | 0.039 | +0.067 | GUE |
| real characters (Sp predicted) | 0.5-drift | 565942 | 0.039 | +0.067 | GUE |
| real characters (Sp predicted) | canonical | 46367 | 0.043 | +0.067 | GUE |
| complex characters (U predicted) | 0.5-drift | 3485530 | 0.035 | +0.067 | GUE |
| complex characters (U predicted) | canonical | 285191 | 0.038 | +0.066 | GUE |

**Validation (dirichlet_family (Dirichlet L-functions)): PASS — 0.5-repro matches banked**
**Guard-robustness:**
  - all primitive non-trivial: best GUE→GUE (stable); gap +0.067→+0.067
  - real characters (Sp predicted): best GUE→GUE (stable); gap +0.067→+0.067
  - complex characters (U predicted): best GUE→GUE (stable); gap +0.067→+0.066

### mertens_liouville

| signal | guard | fc_ref | n_bands_kept | n_pool | gap | best |
|---|---|---|---|---|---|---|
| mertens | 0.5-drift | 13526.2 | 43 | 95863 | -0.024 | Poiss |
| mertens | canonical | 13526.2 | 28 | 54337 | -0.028 | Poiss |
| liouville | 0.5-drift | 9061951.5 | 43 | 4847 | -0.009 | Poiss |
| liouville | canonical | 9061951.5 | 0 | 0 | — | insufficient |

(Note: mertens/liouville fc_ref is large → the canonical Nyquist cap 19845 bites the HIGH bands, unlike the L-functions where the 5.0 lower bound bites the low bands.)
