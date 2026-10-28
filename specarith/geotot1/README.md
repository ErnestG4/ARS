# GEO-TOT1: bounded-dwell keys a/q, per q

For a/q in lowest terms (0 < a < q) with continued fraction [0; a₁, …, a_k], E_N = {all a_i ≤ N}. GEO-TOT1 counts the
keys of each q in E_N for every q ≤ 10⁶ and tests the sealed claim that the per-q count scales as q^(2δ_N − 1),
N = 3, 4, 5 (δ_N the Hausdorff dimension of the bounded-type Cantor set; brief: Will, 2026-10-27, filed in
`../ph2/PH2_DECISIONS_2026-10-07.md`).

**Who would know if this is already known:** the Zaremba / Bourgain–Kontorovich line: A. Kontorovich and M. Magee
(the singular series and uniform congruence counting), then S. Huang, H. Oh, D. Hensley, and the Khabarovsk school
(I. D. Kan, D. A. Frolenkov, V. A. Bykovskii, A. V. Ustinov). Fuller list in `GEOTOT1_STEP0.md` (end).
**Also for Kontorovich and Magee: L9** (`../OPEN_LEADS.md`): an N-dependent anomaly in the non-fold bounded keys of
prime squares (GEO-TOT2): an N = 3 surplus whose ratio to the fold count grows ≈ +0.67 per decade, an N = 4 deficit,
nothing at N = 5; and the unattributed excess at squares of 2^k.

## Result (sealed read, 7658da82): PASS for N = 3, 4, 5
| N | per-q slope on [10⁵, 10⁶) | SE | 2δ_N − 1 | miss | alt. convention |
|---|---|---|---|---|---|
| 3 | 0.411280 | 7.4·10⁻⁵ | 0.411322 | −4.2·10⁻⁵ | 0.411276 |
| 4 | 0.577930 | 6.2·10⁻⁵ | 0.577891 | +3.9·10⁻⁵ | 0.577928 |
| 5 | 0.673660 | 1.4·10⁻⁵ | 0.673659 | +1.5·10⁻⁶ | 0.673661 |

Tolerance ±0.03; the slopes increase with N. The surrogate witness (digits redrawn i.i.d. Gauss–Kuzmin at each key's
length) recovers its own exponents 0.7107 / 0.7665 / 0.8041 (predicted 0.7115 / 0.7668 / 0.8043) and misses 2δ_N − 1 by
0.13–0.30, so the estimator separates the two. Gates: Farey length (303,963,552,393) equal per q to an independent sieve;
Ford sum within 3.0·10⁻¹³ of ζ(3)/ζ(4); bound-4 exceptions to 10⁶ exactly {6, 54, 150}; no bound-5 exception; cumulative
slopes within 4·10⁻⁶ of 2δ_N. Both reads byte-identical; 4 re-enumerated chunks array-identical.

**Descriptive (not sealed; post hoc where noted):**
- c_N(q) = count / q^(2δ_N − 1) depends on the arithmetic type of q (window means, N = 3: prime 1.40, prime power 1.42,
  smooth 0.61, other 0.82). Multiplying by q/φ(q), the Bourgain–Kontorovich local factor, brings all four types to
  1.403 / 1.395 / 1.365 (N = 3 / 4 / 5) for primes, smooth and other q (agreeing to ≤ 0.005).
- Prime powers stay slightly above after that correction: 1.460 / 1.407 / 1.377, n = 128 in the window (mostly p²), 3.5 / 2.3 / 4.9 SE
  above the primes. Post hoc, unpowered: an observation, not a claim.
- Mean depth Σa_i − 1 follows (6/π²) ln²q + 1.574 ln q (the second-order coefficient is Panov's c₁ = (12/π²)(2γ − 1 −
  2ζ′(2)/ζ(2)) = 1.57374, Math. Notes 32 (1982), eq. (10): `GEOTOT1_DEPTH_TERM.md`; a fit on primes to 3·10⁶ gives
  1.5734 ± 0.001 and constant −0.528 against Panov's c₂ + 1 = −0.524 for Σa_i); the
  residual splits by type through the a = 1, q − 1 keys (2q/φ(q)). Depth at a fixed q is heavy-tailed, with a
  tail close to index 1 in the figure (median 58 against mean 136 at q = 999,983).

## Files
- `GEOTOT1_SEAL.md` — the seal (tag `geotot1-seal`; stamped 2026-10-28 04:28 UTC, Bitcoin block 973499, verified on two
  explorers: `timestamps/`). `GEOTOT1_STEP0.md` — Step 0 literature.
- `geotot1.py` (enumeration), `geotot1_analyze.py` (seen / gates / witness / read), `run_geotot1_spot.sh` (launcher),
  `geotot1_hash.py`, `geotot1_reenum.py`, `geotot1_outputs.py`, `verify_geotot1_stamp.py`.
- `results/`: `ENUM_HASHES.json` (part, merged-file and per-array sha256), `GATES.json`, `WITNESS.json`,
  `READ1.json` = `READ2.json`, `REENUM.json`, `SEEN_RANGE.json`, `OUTPUTS.json` (hashes of the outputs below and their
  consistency checks), `GEOTOT1_q_le_1e5.json` (compact columns for the bench page's Totient keys tab), `figures/`.
- `data/` (gitignored; sha256 in `results/OUTPUTS.json` and `results/ENUM_HASHES.json`): `GEOTOT1_Q1e6.npz` (the merged
  enumeration, 1.14 GB), `GEOTOT1_perq.parquet` (per-q scalars: φ, E_N counts in both conventions, depth and length
  sums, c_N), `GEOTOT1_perq_hist.parquet` (per-q histograms of length, log₂ depth, log₂ max quotient).
- Cost: 20.4 spot core-h, 0.86× the model.
