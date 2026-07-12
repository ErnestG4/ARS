# VERDICT C — the census, re-run on the REPAIRED axes

git SHA `6da3f807bb` · seed 20260712

**Pre-committed:** the census verdict (**every neural substrate is CLUSTERED**) *must* reproduce.
It was established on the **Poisson null**, which no repair touches. **If it does not reproduce,
something in the repair is wrong.** This is a consistency gate, not a new result.

It also converts a **detection** into a **measurement**: *how* clustered, on a half-line that now
has units.

| substrate | cells | median unclipped I_rep | median unbounded Brody q | % I_rep<0 | % q<0 | verdict |
|---|---|---|---|---|---|---|
| **allen-hpf-cell** | 400 | **-4.8526** | **-0.6199** | 94% | 100% | **CLUSTERED** ✓ |
| **hc3-port-cell** | 400 | **-2.4727** | **-0.4892** | 87% | 96% | **CLUSTERED** ✓ |
| **ret1-cell** | 325 | **-4.7427** | **-0.2644** | 97% | 86% | **CLUSTERED** ✓ |

## GATE: **PASS** — the census reproduces on the repaired axes, now as a graded measurement.