# VERDICT B — the clustered calibrator class + the two repairs

git SHA `6da3f807bb` · seed 20260712

**Pre-committed HARD STOP:** the clustered class must read **negative on unclipped `I_rep`**
and **q < 0 on unbounded Brody**, *monotonically in clustering strength*. If it does not, **the
REPAIR is wrong, not the class** — and Jobs C/D do not run.

## Reference poles, through the repaired estimators

| reference | unclipped I_rep | unbounded Brody q |
|---|---|---|
| poisson | -0.0094 | -0.0052 |
| GOE(inv-cdf) | +0.3277 | +1.0032 |
| GUE(inv-cdf) | +0.3857 | +1.5325 |

## The clustered sweep (the half-line that has never been observed)

| kind | strength | CV | **unclipped I_rep** | **unbounded Brody q** |
|---|---|---|---|---|
| gamma_renewal | 1.5 | 1.50 | **-0.3874** | **-0.4203** |
| gamma_renewal | 2.0 | 2.01 | **-0.7930** | **-0.6152** |
| gamma_renewal | 3.0 | 2.94 | **-1.7891** | **-0.7687** |
| gamma_renewal | 5.0 | 4.15 | **-4.6338** | **-0.8321** |
| gamma_renewal | 8.0 | 4.83 | **-9.9566** | **-0.8472** |
| gamma_renewal | 13.5 | 5.62 | **-19.6400** | **-0.8544** |
| cox | 0.5 | 1.29 | **-0.1315** | **-0.1375** |
| cox | 1.0 | 1.96 | **-0.4273** | **-0.2964** |
| cox | 1.5 | 3.15 | **-1.3494** | **-0.4606** |
| cox | 2.0 | 3.35 | **-2.8997** | **-0.5569** |
| cox | 2.5 | 10.01 | **-3.7011** | **-0.6852** |
| neyman_scott | 2.0 | 1.86 | **-1.3758** | **-0.5524** |
| neyman_scott | 5.0 | 2.99 | **-4.9508** | **-0.6048** |
| neyman_scott | 10.0 | 4.26 | **-10.9612** | **-0.6192** |
| neyman_scott | 20.0 | 6.00 | **-22.1064** | **-0.6219** |

- all clustered read **I_rep < 0**: **True**
- all clustered read **Brody q < 0**: **True**
- **monotone in clustering strength** (Spearman(CV, I_rep) < −0.5): **True**

## GATE: **PASS** — the repairs are correct and the half-line now has a sign convention and a scale.