# Phase 2 dry run (synthetic CUE_N bins at full size; no zero file opened)

## Estimates vs G0d known answers

| bin | N | arm | κ̂ | κ* (G0d) | (κ̂−κ*)/SD | G1 | widened/stat interval | ½-width pred → achieved | h_bin arm | ±20% arm |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 2 | prim | 0.6917 | 0.6888 | +0.89 | FAIL | [0.5249, 0.8586] | 0.1739 → 0.1668 | INAPPLICABLE | False |
| A | 2 | sec | 0.7583 | 0.7508 | +1.23 | FAIL | [0.7458, 0.7714] | 0.0226 → 0.0128 | False | False |
| B | 3 | prim | 1.0382 | 1.0442 | -0.97 | PASS | [0.9224, 1.1545] | 0.1123 → 0.1161 | INAPPLICABLE | True |
| B | 3 | sec | 1.1129 | 1.1262 | -1.42 | FAIL | [1.0937, 1.1331] | 0.0130 → 0.0197 | False | True |
| P1 | 3 | prim | 0.9177 | 0.9172 | +0.13 | FAIL | [0.8411, 0.9944] | 0.0774 → 0.0766 | INAPPLICABLE | True |
| P1 | 3 | sec | 0.9750 | 0.9739 | +0.24 | FAIL | [0.9651, 0.9853] | 0.0098 → 0.0101 | False | True |
| P2 | 3 | prim | 0.8064 | 0.8099 | -1.26 | FAIL | [0.7506, 0.8622] | 0.0595 → 0.0558 | INAPPLICABLE | False |
| P2 | 3 | sec | 0.8457 | 0.8497 | -1.10 | FAIL | [0.8385, 0.8530] | 0.0115 → 0.0072 | False | True |
| P3 | 4 | prim | 0.9895 | 0.9849 | +0.79 | PASS | [0.9400, 1.0395] | 0.0490 → 0.0497 | INAPPLICABLE | True |
| P3 | 4 | sec | 1.0301 | 1.0247 | +0.74 | FAIL | [1.0157, 1.0451] | 0.0135 → 0.0147 | False | True |
| P4 | 4 | prim | 0.8819 | 0.8816 | +0.05 | FAIL | [0.8419, 0.9222] | 0.0443 → 0.0402 | INAPPLICABLE | True |
| P4 | 4 | sec | 0.9111 | 0.9108 | +0.03 | FAIL | [0.8988, 0.9238] | 0.0172 → 0.0125 | False | True |
| P5 | 5 | prim | 1.0071 | 1.0111 | -0.50 | PASS | [0.9667, 1.0483] | 0.0396 → 0.0408 | INAPPLICABLE | True |
| P5 | 5 | sec | 1.0322 | 1.0393 | -0.72 | FAIL | [1.0137, 1.0518] | 0.0179 → 0.0191 | False | True |
| P6 | 5 | prim | 0.9557 | 0.9521 | +0.49 | FAIL | [0.9196, 0.9926] | 0.0383 → 0.0365 | INAPPLICABLE | True |
| P6 | 5 | sec | 0.9821 | 0.9760 | +0.67 | PASS | [0.9639, 1.0013] | 0.0196 → 0.0187 | False | True |

## Red paths

| bin | misprint (mean, κ̂ prim, κ̂ sec) → FAILS as required | RP-mix (power) | RP-shuffle | mean spacing (band) |
|---|---|---|---|---|
| A | (FIRED, FIRED, FIRED) → True | DISTINGUISHED (0.84) | UNCHANGED | 0.99999738 (±4.1e-05) |
| B | (FIRED, FIRED, FIRED) → True | DISTINGUISHED (0.94) | UNCHANGED | 0.99999963 (±7.2e-06) |
| P1 | (FIRED, FIRED, FIRED) → True | DISTINGUISHED (0.93) | UNCHANGED | 1.00000006 (±2.3e-06) |
| P2 | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (DISTINGUISHED) (0.59) | UNCHANGED | 0.99999998 (±2.0e-06) |
| P3 | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (DISTINGUISHED) (0.28) | UNCHANGED | 0.99999999 (±1.8e-06) |
| P4 | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (DISTINGUISHED) (0.13) | UNCHANGED | 1.00000003 (±1.6e-06) |
| P5 | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (NOT DISTINGUISHED) (0.09) | UNCHANGED | 0.99999995 (±1.4e-06) |
| P6 | (FIRED, FIRED, FIRED) → True | DESCRIPTIVE (DISTINGUISHED) (0.07) | UNCHANGED | 0.99999995 (±1.3e-06) |

## A6(iii) witness (P1, first 3000 spacings)

FIRED: {"prim_predata_resolvable": true, "prim_G1": true, "sec_G1": true, "prim_achieved_wider_than_predicted": true, "misprint_N_prim": true, "misprint_N_sec": true, "mix": true, "shuffle": true}

half-widths predicted → achieved: PRIMARY 0.0774 → 0.6951; SECONDARY 0.0098 → 1.5186
