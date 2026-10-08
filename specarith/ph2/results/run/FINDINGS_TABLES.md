# Phase 2 results tables (under PH2_SEAL_2.1)

## Sealed verdicts per bin

| bin | N_eff | n | arm | κ̂ = N̂/N_eff | interval (PRIMARY widened) | ½-width pred → achieved | G1 | N=∞ excluded | h_bin arm | ±20% arm | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 2.326 | 243,454 | PRIMARY | 1.4049 | [1.1927, 1.6236] | 0.1739 → 0.2155 | **NOT RESOLVABLE (achieved)** | True | INAPPLICABLE | False | PRIMARY least informative: truncation bias ≈ allowance by construction (N_eff 2.16–2.42, allowance 0.160) |
| A | 2.326 | 243,454 | SECONDARY | 1.2106 | [1.1646, 1.2624] | 0.0226 → 0.0489 | **FAIL** | True | False | False | the sharp test (statistical CI only) |
| B | 2.694 | 1,397,836 | PRIMARY | 1.3130 | [1.1861, 1.4412] | 0.1123 → 0.1275 | **FAIL** | True | INAPPLICABLE | False |  |
| B | 2.694 | 1,397,836 | SECONDARY | 1.1685 | [1.1474, 1.1908] | 0.0130 → 0.0217 | **FAIL** | True | False | True | the sharp test (statistical CI only) |
| P1 | 3.052 | 4,426,101 | PRIMARY | 1.2429 | [1.1573, 1.3291] | 0.0774 → 0.0859 | **FAIL** | True | INAPPLICABLE | False |  |
| P1 | 3.052 | 4,426,101 | SECONDARY | 1.1326 | [1.1185, 1.1472] | 0.0098 → 0.0143 | **FAIL** | True | False | True | the sharp test (statistical CI only) |
| P2 | 3.451 | 5,010,883 | PRIMARY | 1.1877 | [1.1213, 1.2547] | 0.0595 → 0.0667 | **FAIL** | True | INAPPLICABLE | False |  |
| P2 | 3.451 | 5,010,883 | SECONDARY | 1.1026 | [1.0880, 1.1178] | 0.0115 → 0.0149 | **FAIL** | True | False | True | the sharp test (statistical CI only) |
| P3 | 3.914 | 5,683,861 | PRIMARY | 1.1516 | [1.0957, 1.2083] | 0.0490 → 0.0563 | **FAIL** | True | INAPPLICABLE | False |  |
| P3 | 3.914 | 5,683,861 | SECONDARY | 1.0852 | [1.0686, 1.1026] | 0.0135 → 0.0170 | **FAIL** | True | False | True | the sharp test (statistical CI only) |
| P4 | 4.373 | 6,350,091 | PRIMARY | 1.1209 | [1.0705, 1.1724] | 0.0443 → 0.0509 | **FAIL** | True | INAPPLICABLE | True |  |
| P4 | 4.373 | 6,350,091 | SECONDARY | 1.0685 | [1.0490, 1.0892] | 0.0172 → 0.0201 | **FAIL** | True | False | True | the sharp test (statistical CI only) |
| P5 | 4.833 | 7,018,718 | PRIMARY | 1.1015 | [1.0573, 1.1468] | 0.0396 → 0.0448 | **FAIL** | True | INAPPLICABLE | True |  |
| P5 | 4.833 | 7,018,718 | SECONDARY | 1.0571 | [1.0373, 1.0782] | 0.0179 → 0.0205 | **FAIL** | True | False | True | the sharp test (statistical CI only) |
| P6 | 5.133 | 7,453,225 | PRIMARY | 1.0820 | [1.0397, 1.1256] | 0.0383 → 0.0430 | **FAIL** | True | INAPPLICABLE | True |  |
| P6 | 5.133 | 7,453,225 | SECONDARY | 1.0454 | [1.0242, 1.0680] | 0.0196 → 0.0219 | **FAIL** | True | False | True | the sharp test (statistical CI only) |
| H1 | 5.633 | 9,999 | PRIMARY | 1.1519 | [0.7074, ∞] | 0.5751 → inf | **NOT RESOLVABLE** | False | INAPPLICABLE | False |  |
| H1 | 5.633 | 9,999 | SECONDARY | 1.0746 | [0.6864, ∞] | 0.6312 → inf | **NOT RESOLVABLE** | False | False | False | the sharp test (statistical CI only) |
| H2 | 10.260 | 9,999 | PRIMARY | inf | [0.5260, ∞] | 1.9040 → inf | **NOT RESOLVABLE** | False | INAPPLICABLE | False |  |
| H2 | 10.260 | 9,999 | SECONDARY | inf | [0.4945, ∞] | 2.0240 → inf | **NOT RESOLVABLE** | False | False | False | the sharp test (statistical CI only) |
| H3 | 10.779 | 9,999 | PRIMARY | 0.6210 | [0.3848, ∞] | 2.0673 → inf | **NOT RESOLVABLE** | False | INAPPLICABLE | False |  |
| H3 | 10.779 | 9,999 | SECONDARY | 0.6014 | [0.3707, ∞] | 2.2145 → inf | **NOT RESOLVABLE** | False | False | False | the sharp test (statistical CI only) |

## Red paths

| bin | mean spacing (band) | RP-misprint (mean, κ̂ prim, κ̂ sec) → fails as required | RP-mix | RP-shuffle | RP-Λ |
|---|---|---|---|---|---|
| A | 0.99999720 (±4.1e-05) ok | (FIRED, INAPPLICABLE (achieved), FIRED) → True | DISTINGUISHED (power 0.84) | INAPPLICABLE (achieved) | INAPPLICABLE (unreachable, declared) |
| B | 1.00000000 (±7.2e-06) ok | (FIRED, FIRED, FIRED) → True | DISTINGUISHED (power 0.94) | UNCHANGED | INAPPLICABLE (unreachable, declared) |
| P1 | 0.99999983 (±2.3e-06) ok | (FIRED, FIRED, FIRED) → True | DISTINGUISHED (power 0.93) | UNCHANGED | INAPPLICABLE (unreachable, declared) |
| P2 | 0.99999998 (±2.0e-06) ok | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (DISTINGUISHED) (power 0.59) | UNCHANGED | INAPPLICABLE (unreachable, declared) |
| P3 | 0.99999997 (±1.8e-06) ok | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (DISTINGUISHED) (power 0.28) | UNCHANGED | INAPPLICABLE (unreachable, declared) |
| P4 | 0.99999981 (±1.6e-06) ok | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (NOT DISTINGUISHED) (power 0.13) | UNCHANGED | INAPPLICABLE (unreachable, declared) |
| P5 | 0.99999999 (±1.4e-06) ok | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (NOT DISTINGUISHED) (power 0.09) | UNCHANGED | INAPPLICABLE (unreachable, declared) |
| P6 | 1.00000002 (±1.3e-06) ok | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (NOT DISTINGUISHED) (power 0.07) | UNCHANGED | INAPPLICABLE (unreachable, declared) |
| H1 | 1.00010870 (±1.0e-03) ok | (FIRED, INAPPLICABLE, INAPPLICABLE) → True | INAPPLICABLE (power 0.03) | INAPPLICABLE | INAPPLICABLE (unreachable, declared) |
| H2 | 0.99996991 (±1.0e-03) ok | (FIRED, INAPPLICABLE, INAPPLICABLE) → True | INAPPLICABLE (power 0.03) | INAPPLICABLE | INAPPLICABLE (unreachable, declared) |
| H3 | 1.00010637 (±1.0e-03) ok | (FIRED, INAPPLICABLE, INAPPLICABLE) → True | INAPPLICABLE (power 0.03) | INAPPLICABLE | INAPPLICABLE (unreachable, declared) |

## Descriptive (never scored)

| bin | PRIMARY with sum allowance (A3) | window 1.8: κ̂ prim / sec | window 2.2: κ̂ prim / sec (flags) |
|---|---|---|---|
| A | NOT RESOLVABLE [1.0634, 1.7529] | 1.4065 / 1.1811 | 1.5423 / 1.2264 (interior, interior) |
| B | NOT RESOLVABLE [1.0941, 1.5332] | 1.3214 / 1.1445 | 1.4075 / 1.1828 (interior, interior) |
| P1 | FAIL [1.0917, 1.3947] | 1.2566 / 1.1128 | 1.3259 / 1.1521 (interior, interior) |
| P2 | FAIL [1.0730, 1.3031] | 1.2087 / 1.0905 | 1.2641 / 1.1274 (interior, interior) |
| P3 | FAIL [1.0587, 1.2453] | 1.1690 / 1.0737 | 1.1981 / 1.0984 (interior, interior) |
| P4 | FAIL [1.0412, 1.2018] | 1.1371 / 1.0589 | 1.1575 / 1.0793 (interior, interior) |
| P5 | FAIL [1.0334, 1.1707] | 1.1175 / 1.0491 | 1.1405 / 1.0737 (interior, interior) |
| P6 | FAIL [1.0186, 1.1467] | 1.1041 / 1.0461 | 1.1078 / 1.0528 (interior, interior) |
| H1 | NOT RESOLVABLE [0.6901, ∞] | 1.2175 / 1.0859 | inf / 2.5897 (interior, interior) |
| H2 | NOT RESOLVABLE [0.5212, ∞] | 1.3108 / 1.5405 | 3.1009 / inf (interior, interior) |
| H3 | NOT RESOLVABLE [0.3805, ∞] | 0.5287 / 0.4998 | 0.4546 / 0.4501 (interior, interior) |
