# Phase 6.1 — findings: published xp-type candidates through the calibrated instrument

Read under **PH6_SEAL 6.1** (commit 70be2bc7, tag `ph6.1-seal`; amendments A1–A4), 2026-10-08, via `tests61.py read`
(every pinned code, input, level and band hash re-checked before each level file was opened). Per-candidate JSON:
`results/read61/<id>.json`. T3 is the sealed Phase 6.0 instrument (`ph6lib.py`, `preread.py` at their 6.0 hashes).

**Outcome, as the brief anticipated: every readable candidate FAILs T3 (prime spectroscopy).** None carries a line at
any log p^k; the instrument records exactly how each misses: POSITION and WEIGHT fail at **every** resolvable prime power
for every model, SILENCE holds everywhere (no spurious lines at non-prime-powers). Every readable candidate is also an
integrable crystal locally (⟨r̃⟩ ≈ 0.9999), so T2 FAILs and T4 is INAPPLICABLE; T1 FAILs for all, with model-specific
attributions that match each paper's own counting formula. No "Riemann Hamiltonian" language applies to any candidate.

## Verdicts (T1, T2, T3, T4)

| candidate | T1 smooth count | T2 local statistics | T3 prime spectroscopy | T4 symmetry class |
|---|---|---|---|---|
| **C1a** Sierra–Rodríguez-Laguna H_I = x(p + ℓ_p²/p), ϑ₂₀₁₁ = π/4 | **FAIL** (constant) | **FAIL** (crystal) | **FAIL** | INAPPLICABLE (crystal) |
| **C1b** S-RL, ϑ₂₀₁₁ = 0 (≡ ϑ₂₀₁₉ = π) | **FAIL** (constant) | **FAIL** (crystal) | **FAIL** | INAPPLICABLE (crystal) |
| **C2** Berry–Keating 2011 (x + 1/x)(p + 1/p) | **FAIL** (constant, slope) | **FAIL** (crystal) | **FAIL** | INAPPLICABLE (crystal) |
| **C4** Sierra–Townsend LLL, λ = 6·10⁴ | **FAIL** (constant, slope) | **FAIL** (crystal) | **FAIL** | INAPPLICABLE (crystal) |
| C3a Bolte–Egger–Keppeler lattice | NOT RESOLVABLE | NOT RESOLVABLE | NOT RESOLVABLE | NOT RESOLVABLE — decided in advance: not converged (A2: low-|E| levels move up to 157 mean spacings between N = 3·10⁴ and 6·10⁴; the torus is tied to N) |
| C3b BEK, E-linked torus | INAPPLICABLE | INAPPLICABLE | INAPPLICABLE | INAPPLICABLE — decided in advance (A1: the paper defines no single spectrum) |
| Bender–Brody–Müller 2017 | INAPPLICABLE | INAPPLICABLE | INAPPLICABLE | INAPPLICABLE — decided in advance (levels defined by the zeros; 6.0 §6.3) |
| Sierra δ-mirror Dirac (2014/2019) | INAPPLICABLE | INAPPLICABLE | INAPPLICABLE | INAPPLICABLE — decided in advance (levels tuned per zero; 6.0 §6.3) |

## Per model

**T1** (δ_n = (n − ½) − N̄(t_n), N̄ = θ/π + 1 containing the 7/8; τ₁ = 0.02; A4: T1 tests density and zeros-level
count rigidity including the global offset; density/slope component reported separately):

| | δ̄ (constant) | slope on log t | density/slope component alone | reading |
|---|---|---|---|---|
| C1a | −0.999 | −0.0023 | within τ₁ | the n-th level sits at Riemann's smooth position n + ½: one level short — the constant is 7/8 − 1 = −1/8 instead of 7/8 (as the 2011 ϑ = π/4 choice gives; `lit/xp_candidates.md` §3 CC check) |
| C1b | −0.874 | −0.0020 | within τ₁ | constant 0 instead of 7/8 — "the constant 7/8 … is missing" (Sierra 2019, p. 10) |
| C2 | −0.913 | +0.048 | **outside** τ₁ | no 7/8 (BK11 eq. 5.7), and a slope from BK11's own −(8π/t) log(t/2π) correction, large at low t |
| C4 | −1.05·10⁵ | −6.0·10⁴ | **outside** | the Sierra–Townsend count is an absorption count (continuum minus N̄, ST eq. 23); its level density is not Riemann's |

**T2:** ⟨r̃⟩ = 0.99994 (C1a, C1b), 0.99995 (C2), 0.99987 (C4) — integrable crystals by the A4 criterion (⟨r̃⟩ ≥ 0.9);
GUE band z ≈ +262 (descriptive). Each smooth spectrum is locally a picket fence.

**T3** (resolvable set R at each candidate's own configuration; arms that failed, by n):

| | R (resolvable prime powers) | POSITION failed | WEIGHT failed | SIGN failed | SILENCE |
|---|---|---|---|---|---|
| C1a | 22: 2,3,4,5,7,9,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71 | all 22 | all 22 | 2, 3, 13, 29, 31, 37, 43 | holds |
| C1b | same 22 | all 22 | all 22 | 2, 3, 4, 9, 11, 19, 29, 31, 37, 53, 59, 61, 67, 71 | holds |
| C2 | 19: 2,3,4,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,67 | all 19 | all 19 | 7, 13, 31, 41 | holds |
| C4 | 32: 2,3,4,5,7,8,9,11,13,16,17,19,23,25,27,29,31,32,37,41,43,47,49,53,59,61,67,71,73,79,83,89 | all 32 | all 32 | 2,3,4,5,8,9,13,19,25,27,29,31,47,61,79,89 | holds |

How to read it: POSITION fails where no line rises above the null band B_n at log n; WEIGHT where the readout is not
within B_n of the explicit-formula amplitude −Λ(n)/√n; SIGN where the readout's real part has the wrong sign (for a
spectrum with no line, the sign is that of noise, so SIGN failures are a random subset); SILENCE would fail on a spurious
line at a non-prime-power — none occurs. C4's larger R reflects its tighter band (configuration to E ≈ 3.8·10⁵).

**T4:** INAPPLICABLE for all four (integrable crystals, decided by the A4 criterion before T4 is read).

## What the result shows (Will, 2026-10-09)
1. **T1 is an additional known answer, not only a failure.** The instrument recovered each paper's own counting
   constant from the levels alone: C1a one level short (7/8 − 1, the 2011 ϑ = π/4 choice), C1b missing the 7/8 (Sierra
   2019's own statement), C2 missing the 7/8 with the slope of BK11's own −(8π/t) log(t/2π) correction (eq. 5.7), C4 the
   absorption count of ST eq. 23. An instrument that reproduces the authors' published formulas from their spectra is
   reading these models correctly — a validation of the read alongside the verdict.
2. **The T3 pattern is the clean "no line" signature.** POSITION and WEIGHT fail at every resolvable prime power, SIGN
   failures form a random subset (the sign of noise), and **SILENCE holds everywhere**: no model has a prime line, and
   none has a spurious line at a non-prime-power. The second half matters — a model with lines at log 6 or log 10 would
   have been a different, more interesting failure.
3. **T2/T4 is why T3 fails, not a separate failure.** ⟨r̃⟩ ≈ 0.9999 for all four: every one-dimensional xp
   regularisation is locally a crystal, as the reachability argument behind 6.3's design predicted — a single
   primitive orbit family per energy (BK11 §6) cannot generate the proliferating periodic orbits whose lengths are the
   log p^k. The crystal (T2) and the absent lines (T3) are one fact seen by two tests.

## What it means for 6.3
The open question is now well posed: the one-dimensional xp family is exhausted. Any candidate worth testing must be
chaotic — a two-or-more-dimensional system or a quantum graph. The SILENCE arm is ready for the quantum-graph
confusable (spurious spikes at log 6, log 10: lengths that are sums of prime-length bonds).

## Context
- Calibration (pre-read, all before the seal): zeros (first 3·10⁴) read (PASS, PASS, PASS, GUE); red paths fire
  (T1 +⅛ constant and 2% density; T2 on an exact-density CUE null; T3 on nulls and pickets; the A4 intermediate-class
  witness); Srednicki fixture exact; convergence of every read candidate ≤ 4.2·10⁻⁹ mean spacings (C1a/C1b 6.7·10⁻¹¹,
  C4 7.2·10⁻⁷). `results/preread61/`, `results/candidates/convergence61.json`.
- The candidates' own papers state the outcome qualitatively: BK11 §6 "a single primitive periodic orbit for each
  energy … This absence of connection with the primes is shared by all variants of xp"; S-RL p. 4 and ST p. 3: the
  fluctuations are missing. The instrument turns these statements into calibrated, per-prime-power records.
- Open leads (descriptive): `specarith/OPEN_LEADS.md`.
