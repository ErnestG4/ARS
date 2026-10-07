# Phase 6 — 6.0 gate results (prime-spectroscopy instrument)

Sealed: `PH6_SEAL_6.0.md` + `seals/PH6_SEAL_6.0.json`, commit 9c75507 (tag `ph6-seal-6.0`), with amendments A1, A3,
A4(b), A5, A6, A7–A10, A12 (A11 not adopted). Run: `gates.py run` on 2026-10-07 07:38–08:25 (local WSL venv, the
pinned environment), all inputs checked against the seal before any statistic. Raw output: `results/gates/gate_results.json`.

## Verdict: all gates PASS as sealed. The instrument is calibrated; 6.1 candidates may be read (after Phase 2's CUE(N_eff), per Will's order).

**Framing (Will, 2026-10-07):** these results confirm known mathematics — the explicit formula, the Selberg trace
formula, Poisson summation. They show the instrument works; the new science starts with the candidates, whose expected
FAIL on prime spectroscopy will now come from an instrument shown to see primes when they are there.

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

## Sensitivity — the detection floor (descriptive, post-seal; Will 2026-10-07)
The red paths show gross errors fire. `detection_floor.py` (output `results/detection_floor.json`) asks how small an
error the exact bar catches: one term or weight family of the sealed RHS is perturbed by a relative ε (or one prime's
line is moved by δ in τ), and bisection finds the smallest |ε| or |δ| at which max_τ |LHS − RHS′|/ε_tol(τ) exceeds 1. LHS,
RHS and tolerance are the sealed ones.

| gate | all prime-power weights | k ≥ 2 harmonics | one prime's weight (p = 2 / 3 / 89) | one prime's line shifted (δ in τ) | other terms |
|---|---|---|---|---|---|
| G0 (ζ, 10⁵ zeros) | 7.5·10⁻⁸ | 2.1·10⁻⁷ | 7.5·10⁻⁸ / 9.2·10⁻⁸ / 5.0·10⁻⁷ | 2.0·10⁻¹² (p = 2) … 1.3·10⁻¹¹ (p = 89) | — |
| G0-c (ζ, 3·10⁴) | 6.5·10⁻⁸ | 1.8·10⁻⁷ | 6.5·10⁻⁸ / 8.0·10⁻⁸ / 4.3·10⁻⁷ | 5.0·10⁻¹² … 3.4·10⁻¹¹ | — |
| G0-s (10,4) | 4.9·10⁻⁹ | 1.1·10⁻⁸ | 4.3·10⁻⁹ / 4.9·10⁻⁹ / 2.2·10⁻⁸ | 4.2·10⁻¹⁰ … 2.2·10⁻⁹ | Γ term 5.0·10⁻¹⁰; pole 1.4·10⁻⁸ |
| G2 (χ₋₄, 4·10⁴) | 7.6·10⁻¹⁰ | 2.6·10⁻⁹ | — / 7.6·10⁻¹⁰ / 4.1·10⁻⁹ | 3.8·10⁻¹⁴ (p = 3) … 2.0·10⁻¹³ (p = 89) | — |
| G2-s (10,4) | 2.6·10⁻¹¹ | 1.0·10⁻¹⁰ | — / 3.1·10⁻¹¹ / 1.6·10⁻¹⁰ | 3.1·10⁻¹² … 1.6·10⁻¹¹ | Γ term 2.5·10⁻¹² |

| Maass gate (even / odd) | identity | elliptic | glide R | hyperbolic H | ζ-lines 2Λ(n)/n (even) |
|---|---|---|---|---|---|
| G1 | 2.6·10⁻⁷ / 3.3·10⁻⁷ | **not detectable** (terms ~e⁻³⁶) | 3.9·10⁻⁷ / 5.3·10⁻⁷ | 5.2·10⁻⁷ / 6.7·10⁻⁷ | 3.5·10⁻⁷ |
| G1-s (12,4) | 7.1·10⁻⁹ / 1.9·10⁻⁸ | 2.8·10⁻⁶ / 7.5·10⁻⁶ | 2.6·10⁻⁸ / 6.9·10⁻⁸ | 3.0·10⁻⁸ / 9.2·10⁻⁸ | 2.2·10⁻⁸ |
| G1-s (20,5) | 1.0·10⁻⁷ / 1.9·10⁻⁷ | 3.8·10⁻⁴ / 7.0·10⁻⁴ | 9.0·10⁻⁸ / 1.6·10⁻⁷ | 1.0·10⁻⁷ / 1.9·10⁻⁷ | 7.8·10⁻⁸ |

Reading it:
- **The identity bar catches relative weight errors of ~10⁻⁷ (ζ), ~10⁻⁹ (χ₋₄) and ~10⁻⁷–10⁻⁸ (Maass hyperbolic/glide).**
  A factor-of-2 error (the trap the elliptic sources warned about) sits 5–6 orders above every floor in the table,
  including the elliptic floor at G1-s (12, 4), 2.8·10⁻⁶; at G1 alone the elliptic weights are invisible, which is why A1
  was needed.
- **Line positions are pinned to ~10⁻¹²–10⁻¹¹ in τ** (10⁻⁸ of a line width): the line phase e^{i(τ − log n)T₀} rotates
  at rate T₀, so a misplaced line breaks the identity long before its envelope moves.
- **This is the floor for the instrument's mathematics (Layer A), not for candidates.** Candidates are judged by T3
  (Layer B), whose sensitivity is the null band: a candidate's line amplitude c_n is distinguishable from the explicit-
  formula value a_n only to within B_n. At the candidate configuration (G0-c's, 3·10⁴ levels) B_n runs from 0.10 at
  log 2 to 0.26 at log 90 (max 0.30; resolvable set 24/34); at G0's size, 0.06 to 0.15 (max 0.17; 29/34). So "how close a candidate can come"
  is answered in units of B_n, roughly 10⁶ times coarser than the identity floor — the identity floor guarantees the
  reference a_n the candidate is compared with is right to far better than the comparison can resolve.

## Not yet done (brief "Outputs")
- Plots of S(τ) / C(τ) for every spectrum on common axes (descriptive; next).
- zeros6 replication (descriptive, §10).
- 6.1 candidates (≥ 3·10⁴ levels; T1 fixes the energy scale before T3) — after programme Phase 2's CUE(N_eff) known answer,
  which T2 needs (Will's order).

## Open leads
- None from the gates. The instrument reads every arithmetic positive exactly and rejects every null and confusable at
  the sealed rates.
