# dr-port (DANDI 000638) — THE 7th SUBSTRATE

**SCOPE, PRE-COMMITTED BEFORE THE RUN:** dr-port **extends the coupling range** and **tests the
dissociation**. **IT DOES NOT RESURRECT THE LADDER.** The fine-grained ordering swapped under the
cell-cap — a nuisance parameter. A 7th substrate does not stabilise an object that moves under one.
**If the ordering comes back looking clean, that is the moment to RE-PERTURB THE CELL-CAP, not to
believe it.**

Streamed over HTTP-range. **n_seen = 300 · n_used = 299** (171s).

| quantity | value |
|---|---|
| clustering (median unclipped `I_rep`) | **-0.833** |
| split-half ρ(I_rep) | **+0.932** |
| split-half ρ(logCV) | **+0.994** |
| **coupling** ρ(log-ISI CV, I_rep) | **-0.549** |
| coupling ρ(gamma-k, I_rep) | **+0.801** |
| **coupling, disattenuated** | **-0.570** |
| R²_marginal (variance decomposition) | **0.145** |

## Reference (n=6, from `ladder_n6.json`)

| substrate | clustering | ρ(I) | coupling | R²_marg |
|---|---|---|---|---|
| ibl-port | −0.236 | 0.988 | **−0.694** | 0.794 |
| hc3-port | −1.962 | 0.913 | **−0.604** | 0.705 |
| buzsaki | −2.389 | 0.903 | **−0.482** | 0.582 |
| allen-hpf | −8.306 | 0.598 | **−0.429** | 0.574 |
| ret1 | −0.309 | 0.970 | **−0.187** | 0.656 |
| pvc-11 | −0.863 | 0.954 | **+0.076** | 0.761 |
| **dr-port** | **-0.833** | **0.932** | **-0.549** | **0.145** |

**Read it against the DISSOCIATION (clustering ⊥ coupling), not against the ordering.**