# GEO-TOT1 seal — STATUS: SEALED as of the tag geotot1-seal (stamped 2026-10-28 04:28 UTC; Bitcoin block 973499). Read 7658da82: PASS (README.md)

This header line was updated after the read; the tagged text's header still read "DRAFT for Will" (a stale header: the body was final at the tag). Nothing else changed.

Brief: Will, 2026-10-27 (filed verbatim in `specarith/ph2/PH2_DECISIONS_2026-10-07.md`). Hardware per Will's note: spot's
free cores (or char); the 4090 is not used.

## 1. Question and sealed claim
For a/q in lowest terms, 0 < a < q, with continued fraction [0; a₁, …, a_k], E_N = {all a_i ≤ N}. The sealed claim
(a heuristic, not a theorem): the per-q count #{a coprime to q : a/q ∈ E_N} scales as q^(2δ_N − 1) for N = 3, 4, 5.
Step 0 (§5): no source states this per-q law as Hensley's (his 1996 conjecture is a set statement); its main-term form
is the Bourgain–Kontorovich heuristic, multiplicity ∝ 𝔖(q)·q^(2δ−1) with 𝔖(q) = ζ(2)·φ(q)/q (INFERENCE from BK (4.33)).
φ(q)/q averages to 6/π² within every bin, so the bin-mean slope tests the same exponent. A FAIL is a finding about local factors, not a pipeline failure, provided the cumulative
gate passes.

## 2. Conventions (fixed here)
- **Primary: canonical, "last ≥ 2"** ([…; a_k] with a_k ≥ 2 for q ≥ 2): a/q ∈ E_N iff max a_i ≤ N. It reproduces the
  known bound-4 exceptions {6, 54, 150} for q ≤ 2000 (seen range). The literature is split (Step 0 §5): OEIS
  (A141822/A195901, PARI `contfrac`), Kontorovich's survey and Hensley 1994 use the canonical form; Bourgain–Kontorovich
  and Magee–Oh–Winter define the set existentially ("some representation"). The canonical form is primary because the
  exception list and its search ranges (no further bound-4 exception below 10⁷) are stated in it.
- Alternative (either form; [… a_k] = [… a_k − 1, 1]) computed and reported, never gated. Seen range: it gives {54, 150}
  at bound 4 (5/6 = [0; 1, 4, 1]).
- Depth: S = Σ a_i is stored; the Stern–Brocot depth is S − 1 (the browser's 31.5 at q = 360 is S − 1 = 31.54).

## 3. Q, bins, estimator, window, tolerance
- **Q = 10⁶** (priced §7; fits the 2-hour box on spot's free cores).
- **Bins:** 10 per decade; bin j = {q : 10^(j/10) ≤ q < 10^((j+1)/10)}.
- **Per-q estimator:** per bin, x = mean ln q over its integers, y = ln(bin total / #q in the bin); OLS slope of y on x.
  No per-q logs.
- **Fit window:** q ∈ [Q/10, Q) = bins 50 … 59 (q = 100,000 … 999,999).
- **Tolerance ±0.03.** Seen-range basis (`results/SEEN_RANGE.json`, bins 23 … 32, q = 200 … 1995): misses −0.003,
  +0.003, +0.003 (N = 3, 4, 5, canonical), all inside 0.03, so the brief's tolerance stands and the per-q test is not
  replaced by the ordering.
- **Targets:** 2δ_N − 1 = 0.411322 (N = 3), 0.577891 (4), 0.673659 (5), with δ₃ = 0.70566090803, δ₄ = 0.78894555748,
  δ₅ = 0.83682944368 (Pollicott–Vytnova, ± 10⁻¹²; Step 0 §2). Cumulative targets 2δ_N = 1.411322, 1.577891, 1.673659.
- **Verdict per N:** PASS iff |slope − (2δ_N − 1)| ≤ 0.03; the claim PASSES iff all three do. Reported alongside: the
  ordering of the three slopes, the alternative-convention slopes, every bound-4 exception up to Q (never filtered), and
  c_N(q) = count / q^(2δ_N − 1) split by q prime / prime power / smooth (all prime factors ≤ 100) / other, and the
  same with the Bourgain–Kontorovich local factor removed, c_N(q)·q/φ(q) (descriptive; no verdict on q-dependence).
  Seen range (q ≤ 1000, N = 3): c_N by type 0.71–1.45; c_N·q/φ(q) 1.39–1.53.

## 4. Gates (all must pass before any new number counts)
| Gate | Pass condition |
|---|---|
| Farey length | per-q φ from the enumeration equals an independent totient sieve at every q ≤ Q, and 1 + Σφ agrees |
| Ford sum | |Σ_{q ≤ Q} φ(q)/q⁴ − ζ(3)/ζ(4)| ≤ 1/(2Q²) (the tail bound) |
| Bound-4 exceptions | exactly {6, 54, 150} for q ≤ 2000 (canonical) |
| Bound 5 | no exception for q ≤ Q; any exception is a suspected bug until brute force (Python integers) reproduces it, and the gate fails |
| Cumulative count | OLS slope of ln C(Q′) on ln Q′ at the window's 11 bin edges within ±0.03 of 2δ_N, N = 3, 4, 5 |
Seen range: cumulative misses +0.0004, −0.0033, −0.0025 (q ≤ 1995).

## 5. Step 0 literature (`GEOTOT1_STEP0.md`; agent-drafted, spot-checked; tags kept)
1. **Yao–Knuth:** the average is over all m ≤ n, not coprime m only: Σ = (6/π²) n (ln n)² + O(n log n (log log n)²)
   (abstract only; body UNVERIFIED). The coprime version is Panov 1982 / Liehl 1983 (SECONDARY). The 31.5 vs 21.06 gap at
   q = 360: 31.5 is Σa_i − 1 (Σa_i = 32.54); the second-order term ≈ 1.57·ln q adds ≈ 9.3 (INFERENCE from Myerson and
   Zhabitskaya via Minelli–Sourmelidis–Technau); a = 1 and a = q − 1 alone add 2q/φ(q) = 7.5, which depends on the
   factorisation of q. The mean is dominated by a heavy tail (typical size (12/π²) ln q ln ln q, Aistleitner–Borda–Hauke).
2. **δ_N:** the browser's four values hold; δ₆ = 0.86761917324015 (± 10⁻¹³) (VERIFIED; a conflicting PV Table 4 row
   is treated as a typo).
3. **Cumulative count:** an asymptotic with a constant, C_m x^{2δ_m}, canonical form (Hensley 1994, Pacific J. Math.,
   VERIFIED; the 1990 theorem SECONDARY); BK quote two-sided bounds only.
4. **Per-q law:** no fixed-q asymptotic is stated or proven; heuristic main term ∝ (φ(q)/q) q^(2δ−1) (BK (4.33),
   simplification INFERENCE); Hensley 1994's proven mod-n equidistribution gives the same local factor.
5. **Zaremba:** density one at A = 50 (BK), A = 5 (Huang); positive proportion for {1..4} (Kan 2017). Bound-4
   exceptions {6, 54, 150}, none further below 10⁷ (OEIS A195901, checked). Bound 5: no exception known.
6. **Depth law:** over denominators ≤ Q (double average), a stable law of index 1 after centring (12/π²) ln Q (ln ln Q −
   γ) (Bettin–Drappeau Thm 2.5); for a fixed q only concentration is known.
7. **κ = 0.51606240889999…** (Hensley's constant; Lhote 2004; OEIS A375066, checked), proven for averages over pairs;
   for fixed q only an O(log q) bound. Seen range: dVar(L)/d ln q ≈ 0.517.

## 6. Witness that must fail
- **Surrogate:** each key keeps its real CF length L; its digits are redrawn i.i.d. Gauss–Kuzmin. Membership in E_N
  then has probability P_N^L, P_N = 1 − log₂(1 + 1/(N + 1)), so per q the surrogate count is Σ_L Binomial(L_hist[q, L],
  P_N^L), numpy default_rng(20261027). The identical slope estimator and window.
- **Own exponent (computed before running):** 1 + μ ln P_N + ½κ(ln P_N)², μ = 12 ln 2/π² = 0.8428, κ from Step 0.
  With κ = 0.51606240890: **0.7115 (N = 3), 0.7668 (4), 0.8043 (5)**. κ is proven only for pair averages (Step 0 §7),
  so the seen range is the check: the surrogate's expectation slope on q = 200 … 1995 is 0.7123, 0.7679, 0.8056, within
  0.0013 of these. The variance term is ½κ(ln P_N)² ≈ 0.039, 0.024,
  0.016, larger than the brief's 0.01–0.02 for N = 3.
- **Pass:** for each N, |surrogate slope − own exponent| ≤ 0.03 AND |surrogate slope − (2δ_N − 1)| > 0.03. Gaps to
  2δ_N − 1: 0.300, 0.189, 0.131. The surrogate's expectation slope over the window is reported too.

## 7. Cost (priced on the seen range)
- Local single thread: 6.1 ns per Euclid step (q = 1001 … 2000, all a < q). Steps to Q: Σ (q − 1)(μ ln q + c), c fitted
  on the seen range: 4.65·10¹⁰ (Q = 10⁵), 5.62·10¹² (Q = 10⁶).
- Q = 10⁶: 9.5 local core-h; ≈ 22 spot core-h at the ×2.3 spot factor; ≈ 45–50 min wall at 28 processes. Q = 10⁵:
  0.2 spot core-h.
- Plan: [2, 10⁶] split into 200 chunks of equal modelled cost, one single-thread process each (NUMBA_NUM_THREADS=1), at
  most 28 at a time, nice; first-wave check (stop above 1.25×) and checks at 25 / 50 / 75%.
- Outputs ≈ 1.1 KB per q (≈ 1.1 GB); per-chunk .npz merged, sha256 of each chunk and of the merged file listed in the
  stamp; no statistic of q > 2000 displayed before attestation.

## 8. Order
Seal and stamp → enumerate (spot) → hash the outputs → Bitcoin attestation verified on two explorers → gates → witness →
sealed read, twice in separate processes from the hashed file, `cmp` byte-identical; plus a re-enumeration of 4 chunks
(seeded choice) whose arrays must equal the first run's (`np.array_equal` on every array: .npz bytes carry zip
timestamps, so the stamp lists both the file sha256 and a sha256 of each array's bytes). Then the Parquet tables, figures and the q ≤ 10⁵ JSON.

## 9. Pins
- `geotot1.py` sha256 bb1d0bad0e1b180aba152fc709226f6ccf7bfa1b9169e82ed37353c8ca7c5474
- `geotot1_analyze.py` sha256 58a12452f8d52df6ed0a75c81dbe45ea3884eced3217d299ad213ef5b1b1ea9f
- `run_geotot1_spot.sh` sha256 db7077f812f802c33dbcdb529d05c23da8251a2277c66910d5cd4291f7544145
- All three identical on spot (checked). Environment (spot, ph6c): Python 3.12.15, numpy 2.5.3, numba 0.68.0, kernel
  7.2.11-100.fc43.x86_64. The spot enumeration of q ≤ 2000 equals the local (WSL; numpy 2.4.4, numba 0.66.0) arrays
  exactly.
- Launch: `run_geotot1_spot.sh 1000000 P OUT_DIR`, P = spot's free cores at launch (≤ 28; the ℤ[ω] archive holds 28
  until it ends). Seed for the witness: 20261027. Tag `geotot1-seal`; the stamp manifest lists these files' committed
  sha256.
