# GEO-TOT1 seal — STATUS: DRAFT (Step 0 literature pending; δ_N and κ to be filled from it). Nothing above q = 2000 computed

Brief: Will, 2026-10-27 (filed verbatim in `specarith/ph2/PH2_DECISIONS_2026-10-07.md`). Hardware per Will's note: spot's
free cores (or char); the 4090 is not used.

## 1. Question and sealed claim
For a/q in lowest terms, 0 < a < q, with continued fraction [0; a₁, …, a_k], E_N = {all a_i ≤ N}. The sealed claim
(Hensley's heuristic; a heuristic, not a theorem): the per-q count #{a coprime to q : a/q ∈ E_N} scales as
q^(2δ_N − 1) for N = 3, 4, 5. A FAIL is a finding about local factors, not a pipeline failure, provided the cumulative
gate passes.

## 2. Conventions (fixed here)
- **Primary: canonical, "last ≥ 2"** ([…; a_k] with a_k ≥ 2 for q ≥ 2): a/q ∈ E_N iff max a_i ≤ N. It reproduces the
  known bound-4 exceptions {6, 54, 150} for q ≤ 2000 (seen range). Step 0 records the literature's Zaremba convention.
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
- **Targets:** 2δ_N − 1 with δ_N from Step 0 (§5): [TO FILL].
- **Verdict per N:** PASS iff |slope − (2δ_N − 1)| ≤ 0.03; the claim PASSES iff all three do. Reported alongside: the
  ordering of the three slopes, the alternative-convention slopes, every bound-4 exception up to Q (never filtered), and
  c_N(q) = count / q^(2δ_N − 1) split by q prime / prime power / smooth (all prime factors ≤ 100) / other (descriptive).

## 4. Gates (all must pass before any new number counts)
| Gate | Pass condition |
|---|---|
| Farey length | per-q φ from the enumeration equals an independent totient sieve at every q ≤ Q, and 1 + Σφ agrees |
| Ford sum | |Σ_{q ≤ Q} φ(q)/q⁴ − ζ(3)/ζ(4)| ≤ 1/(2Q²) (the tail bound) |
| Bound-4 exceptions | exactly {6, 54, 150} for q ≤ 2000 (canonical) |
| Bound 5 | no exception for q ≤ Q; any exception is a suspected bug until brute force (Python integers) reproduces it, and the gate fails |
| Cumulative count | OLS slope of ln C(Q′) on ln Q′ at the window's 11 bin edges within ±0.03 of 2δ_N, N = 3, 4, 5 |
Seen range: cumulative misses +0.0004, −0.0033, −0.0025 (q ≤ 1995).

## 5. Step 0 literature
[TO FILL from GEOTOT1_STEP0.md: Yao–Knuth statement and the 31.5 / 21.06 gap; δ_N; counting theorem; Hensley's per-q
heuristic and local factors; Zaremba exception lists and verified ranges; depth limit law; κ.]

## 6. Witness that must fail
- **Surrogate:** each key keeps its real CF length L; its digits are redrawn i.i.d. Gauss–Kuzmin. Membership in E_N
  then has probability P_N^L, P_N = 1 − log₂(1 + 1/(N + 1)), so per q the surrogate count is Σ_L Binomial(L_hist[q, L],
  P_N^L), numpy default_rng(20261027). The identical slope estimator and window.
- **Own exponent (computed before running):** 1 + μ ln P_N + ½κ(ln P_N)², μ = 12 ln 2/π² = 0.8428, κ from Step 0.
  With κ = 0.516 (to confirm): 0.712 (N = 3), 0.767 (4), 0.804 (5). Seen-range check: the surrogate's expectation slope
  on q = 200 … 1995 is 0.712, 0.768, 0.806, within 0.002 of these. The variance term is ½κ(ln P_N)² ≈ 0.039, 0.024,
  0.016, larger than the brief's 0.01–0.02 for N = 3.
- **Pass:** for each N, |surrogate slope − own exponent| ≤ 0.03 AND |surrogate slope − (2δ_N − 1)| > 0.03. Gaps to
  2δ_N − 1: ≈ 0.30, 0.19, 0.13. The surrogate's expectation slope over the window is reported too.

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
[TO FILL at sealing: geotot1.py, geotot1_analyze.py sha256; spot environment (python, numpy, numba versions, kernel).]
