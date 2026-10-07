# Phase 6 — proposed amendments to PH6_SEAL_6.0.md (for Will; none applied)

Written overnight 2026-10-07 from the pre-read (seal §9). The seal text says the red-path reachability result is
reported to Will before the seal commit; this file is that report's decision part. Nothing below is in force until
Will approves it and it is appended to the seal's Amendments section.

## A1. G1-s — small-window Maass identity (tests the elliptic weights)

**Finding.** At G1's sealed window (T₀ = 49.38, σ = 5.81) the elliptic terms (1/8)∫h/cosh(πr) and
(1/(3√3))∫h cosh(πr/3)/cosh(πr) are ~e⁻³⁶: the test function is negligible near r = 0, where those kernels live. RP5
("elliptic weights ×2") is therefore INAPPLICABLE in both sectors (max |removed term|/2ε ≈ 1e-10;
`results/preread/preread_tables.json`). G1 as sealed cannot test the very weights Will's failure ladder (round 3)
names first. This is the same situation G0-s fixed for ζ's smooth terms.

**Proposal.** Add G1-s: the per-sector Maass identity (seal §5, unchanged formulas and tolerance construction) at two
fixed windows, Layer A only, with RP5–RP9 and their reachability rule:

| window (T₀, σ) | upper edge T₀ + 8.5σ (list complete to 98.765) | max \|elliptic term\| | RP5 reach ratio (estimate) |
|---|---|---|---|
| (12, 4) | 46.0 | 4.0·10⁻³ | ≈ 2·10³ per sector |
| (20, 5) | 62.5 | 1.2·10⁻⁴ | ≈ 3·10¹ per sector |

(Estimate from the RHS and a density-based ε; the sealed ε would be computed by preread.py exactly as for G1.) Both
windows also put weight on the lowest forms (r₁ = 9.53 odd, 13.78 even), so they exercise the region Session K found
GOE-like in the odd sector — irrelevant to an exact identity, but noted.

**Cost.** Minutes. No new data.

## A2. Wording: RP16 (drop the mirror term) is marginal

RP16 is reachable only at G0-s window (10, 4), and there only by its upper bound (Σ w(−γ) gives 2.2× the threshold).
The actual |M(τ)| is not computed before the gate run (it is part of the LHS). If at the run it falls below 2ε, the seal
already says RP16 is reported INAPPLICABLE. No change proposed; flagged so it is not a surprise.

## Reachability summary (all from the RHS / positions only; no gate statistic)

| gate | red path | max ratio | status |
|---|---|---|---|
| G0 | RP1 drop k ≥ 2 | 2.4·10⁶ | REACHABLE |
| G0 | RP2 flip prime sign | 1.4·10⁷ | REACHABLE |
| G0 | RP3 data + 100δ (first-order estimate) | 2.1 | REACHABLE (modest) |
| G0-s (10,4) | RP13 Γ / RP14 pole / RP15 asym. ψ / RP16 mirror (upper bound) | 7.6·10⁷ / 1.5·10⁷ / 5.6·10⁵ / 2.2 | all REACHABLE |
| G0-s (40,3) | RP13 / RP14 / RP15 / RP16 | 5.6·10⁷ / 2·10⁻³¹ / 4.9·10² / 9·10⁻⁶⁴ | R / INAPPL. / R / INAPPL. |
| G0-s (150,10) | RP13 / RP14 / RP15 / RP16 | 7.4·10² / 2·10⁻⁴² / 3·10⁻⁴ / 4·10⁻⁵² | R / INAPPL. / INAPPL. / INAPPL. |
| G0-c | RP1 / RP2 / RP3 | 2.7·10⁶ / 1.5·10⁷ / 2.4 | REACHABLE |
| G1-even | RP5 / RP6 / RP8 / RP9 | 2·10⁻¹⁰ / 1.2·10⁶ / 1.4·10⁶ / 9.6·10⁵ | INAPPL. / R / R / R |
| G1-odd | RP5 / RP6 / RP9 | 1.5·10⁻¹⁰ / 9.4·10⁵ / 7.4·10⁵ | INAPPL. / R / R |
| G1 | RP7 swap parity | 2.4·10⁶ | REACHABLE |
| G2 | RP10, RP11 | pending (χ₋₄ zeros) | |
