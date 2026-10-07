# Phase 6 — 6.0 gate results (prime-spectroscopy instrument)

Sealed: `PH6_SEAL_6.0.md` + `seals/PH6_SEAL_6.0.json`, commit 9c75507 (tag `ph6-seal-6.0`), with amendments A1, A3,
A4(b), A5, A6, A7–A10, A12 (A11 not adopted). Run: `gates.py run` on 2026-10-07 07:38–08:25 (local WSL venv, the
pinned environment), all inputs checked against the seal before any statistic. Raw output: `results/gates/gate_results.json`.

## Verdict: all gates PASS as sealed. The instrument is calibrated; 6.1 candidates may be read (after Phase 2's CUE(N_eff), per Will's order).

### Layer A — exact identities (max |LHS − RHS| / ε over the identity grid; PASS ≤ 1)

| gate | what | max ratio | verdict |
|---|---|---|---|
| G0 | ζ, 10⁵ zeros (Weil explicit formula) | 0.0026 | PASS |
| G0-s (10,4) / (40,3) / (150,10) | ζ small windows (smooth/pole/exact-θ terms) | 0.041 / 0.019 / 0.023 | PASS |
| G0-c | ζ, first 30,000 zeros | 0.0046 | PASS |
| G1-even / G1-odd | Maass per sector (BS07 (2.39)), window inside r ≤ 98.76 | 0.073 / 0.054 | PASS |
| G1-s (12,4) even / odd | Maass small window (elliptic terms live) | 0.13 / 0.19 | PASS |
| G1-s (20,5) even / odd | | 0.11 / 0.13 | PASS |
| G1a / G1b (implied) | sum / difference, at G1 and both G1-s windows | — | PASS |
| G2 | χ₋₄ to T = 4·10⁴ (58,220 zeros) | 0.0033 | PASS |
| G2-s (10,4) / (40,3) | χ₋₄ small windows (Γ parity live at (10,4)) | 0.00015 / 0.00035 | PASS |
| G4 confusable / incommensurate | picket fences (Poisson summation) | 0.028 / 0.027 | PASS |

The elliptic weights 1/8 and 1/(3√3) (Booker–Strömbergsson; Will's failure-ladder concern) and the χ₋₄ Γ parity
ψ(¾ + iu/2) are now tested exactly — G1-s and G2-s pass, and the red paths that perturb them fire.

### Red paths (each must FIRE where reachable)
Every reachable red path FIRED: RP1–RP4 (G0), RP1–RP3 + RP17 (G0-c), RP13–RP16 at G0-s (10,4), RP13/RP15 at (40,3),
RP13 at (150,10), RP6–RP9 at G1 and G1-s, RP5 at both G1-s windows, RP10 at G2 and G2-s, RP11 at G2-s (10,4), RP13 at
G2-s, RP12 at both pickets. INAPPLICABLE exactly where the pre-read said (RP5 at G1; RP11 at G2 and G2-s (40,3); RP14/RP16
at (40,3); RP14–RP16 at (150,10)). No red path reported DID_NOT_FIRE.

### Layer B — the spectroscopy readout (T3's instrument)
| gate | requirement | result |
|---|---|---|
| G0 | vs ζ weights PASS; vs χ₋₄ FAIL | PASS (R = 29/34) |
| G0-c | vs ζ PASS; M ⊆ R; \|R\| ∈ [22, 30] | PASS (R = 24/34) |
| G2 | vs χ₋₄ PASS incl. SILENCE at 2, 4, 8, 16, 32, 64 and SIGN at 3 (+), 5 (−), 7 (+), 9 (−); vs ζ FAIL | PASS (R = 24/28; all four named sign arms PASS, including 9) |
| G3 (held-out, G0 config) | silence within allowance; ζ rejected 100%; positive control ≥ 95% | PASS — GUE 1/100 exceed (allowance 4), Poisson 0/100; ζ rejected 100/100 (both); positive control 99/100 |
| G3-c (held-out, G0-c config, GUE) | same; ζ FAIL 100% | PASS — 2/100 exceed; ζ FAIL 100/100; positive control 98/100 |
| G4 confusable (λ = log 2) | POSITION fires at 2^k; c = +log 2; silent at 3, 5, 7; T3 vs ζ FAIL (WEIGHT/SIGN) | PASS |
| G4 incommensurate (λ = 1.2345) | silent at all n ≤ 90; T3 vs ζ FAIL (POSITION) | PASS |

## Disclosures (carried from the seal and the overnight log)
- Pilots before the seal (§11): EF agent's 50/81-zero identity check; SB agent's Weyl counts; PARI timing.
- A5: the original §7 null known-answer bar was evaluated on the calibration draws first and FAILED everywhere (omitted
  LS factor √2, and a per-n bar below sampling noise); the analytic Gamma-law band was written after those values were
  seen. All six nulls pass it (0/89 outside [0.659, 1.433]).
- χ₋₄ zeros: the first recipe (PARI default divz = 8) missed close pairs; caught by the fail-closed count check before
  any statistic; the sealed list (divz 64) passed count, S-block and accuracy checks.
- G3's held-out draws ran in a worker pool (fixed seeds; verified identical to sequential on non-sealed seeds).
- G0 Layer B reads c_n = a_n to ~1e-10 (exact identity; e.g. c_2 = −0.4901, c_3 = −0.6343, c_5 = −0.7198,
  c_29 = −0.6253); that is a check of the readout, not evidence of power. Power is G3/G3-c (null spectra rejected
  100/100) and the G4 confusable (positions fire, weights refuse).

## Not yet done (brief "Outputs")
- Plots of S(τ) / C(τ) for every spectrum on common axes (descriptive; next).
- zeros6 replication (descriptive, §10).
- 6.1 candidates (≥ 3·10⁴ levels; T1 fixes the energy scale before T3) — after programme Phase 2's CUE(N_eff) known answer,
  which T2 needs (Will's order).

## Open leads
- None from the gates. The instrument reads every arithmetic positive exactly and rejects every null and confusable at
  the sealed rates.
