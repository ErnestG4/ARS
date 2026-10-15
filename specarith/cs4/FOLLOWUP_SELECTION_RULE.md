# Route (a) follow-up — observable selection rule (round 48)

**Committed before either candidate's sensitivity or SE is computed.** The choice is made **after** the route (a) read
(PASS, row (a), 798065dc, 2026-10-15). By round 46, the follow-up therefore runs as an independent replication:
tagged prediction → OpenTimestamps stamp → fresh zeros → seal → read.

## Rule (Will, round 48)
- **Primary:** choose the candidate with the larger |∂stat/∂μ₃| / SE_stat at the follow-up's data geometry.
- **Tie-break:** a tie is broken by the larger |∂stat/∂μ₄| / SE_stat.
- **Choice:** mechanical; no other input.

## Definitions (fixed here; parameters chosen only by the data-free procedures below)
- **μ_k (as route (a), round 48):** κ_k → κ_k^sine + μ_k(κ_k^ζ − κ_k^sine) wherever κ_k appears, with every other κ_j at
  CS08's values. ∂stat/∂μ_k is the derivative of the statistic's expectation at μ_k = 1, by the ±0.01 symmetric
  difference (or exactly, where the statistic is linear in κ_k).
- **SE_stat:** the standard deviation of the statistic over CUE_1000 replicates (char GPU sampler, as route (a)'s
  calibration) at the geometry below.
  - R = 100 replicates per file, the same replicates for both candidates, with seeds disjoint from every earlier use.
  - The five files are pooled with weights ∝ n_f, as route (a).
- **Ratio:** |∂stat/∂μ_k| / SE_stat does not depend on the statistic's units. It is the number of SEs the statistic
  moves per unit change of μ_k.
- **Pooling:** each candidate's statistic is a per-file amplitude μ̂_f (μ = 1 the CS prediction, μ = 0 the sine
  kernel), pooled with w_f ∝ n_f. The pooled ratio is
  |Σ w_f ∂μ*_f/∂μ_k| / (Σ w_f² SE_f²)^½.
- **Tie:** the two candidates' primary ratios lie within 5% of each other (the ratio of the smaller to the larger ≥ 0.95).
- **Geometry:** route (a)'s F3 geometry, as a proxy: five files with F3's ℓ̄ and n_f (ROUTE_A_SEAL.md §1). The fresh
  replication set is declared later, before any download, with matching ℓ̄ and n_f. If its geometry differs, the
  comparison is not redone; the choice stands.

## Candidates
**(A) Next-nearest-neighbour spacing law.**
- **Statistic:** s⁽²⁾_i = x_{i+2} − x_i in unfolded units (exact θ, the route (a) decode path).
- **Model:** p⁽²⁾_μ = p⁽²⁾_sine + μ·Δp⁽²⁾ on the window s ≤ S_A, where Δp⁽²⁾ is CS08's n ≤ 5 arithmetic part at each
  file's zero-weighted mean height. μ̂ is the conditional ML estimate in the window (route (a)'s estimator class), and
  stat = μ̂.
- **S_A (data-free):** the largest s on the grid {1.8, 2.0, …, 3.0} at which the sine kernel's n = 6 inclusion–exclusion
  term of p⁽²⁾ is no larger than route (a)'s n = 6 term at its window edge, T₆^sine(1.8) = 1.43e-9
  (`results/route_a_cumul.json`, n6_probe). This keeps the n ≤ 5 truncation no looser than route (a)'s.

**(B) Third cumulant of the counting function.**
- **Statistic:** N_j = the number of zeros in disjoint unfolded windows [jL, (j+1)L), and k₃ is the k-statistic of
  {N_j} in each file. The per-file amplitude is μ̂_B = (k₃ − κ₃^sine(L)) / Δκ₃(L), with Δκ₃ = κ₃^CS − κ₃^sine at the
  file's zero-weighted mean height.
- **Expectation:**
  κ₃(L) = ∫ρ₁ + 3∫∫ρ₂^c + ∫∫∫ρ₃^c over [0, L], where ρ^c are the connected (cluster) functions. These are the
  factorial-cumulant terms.
  - It involves ρ₁–ρ₃ only, so ∂stat/∂μ₄ = 0 identically and ∂stat/∂μ₃ = ∫∫∫_{[0,L]³}(κ₃^ζ − κ₃^sine), exactly.
  - No truncation enters.
- **L (data-free):** chosen from {0.5, 1.0, 1.5, 2.0, 3.0} by the same primary ratio, computed on the same CUE
  replicates, before the A–B comparison. The comparison then uses that L.

## Round-46 condition for the chosen observable
Before its own seal, the chosen observable needs a data-free sensitivity split, by the R₂-anchored derivative method of
B₂, showing that a majority of its arithmetic part comes from connected n ≥ 3 terms. This is reported whatever it shows.
If the chosen observable fails it, that goes to Will before any seal. The selection rule above is not re-run.

## Record
- **Results file:** `results/followup_selection.json`. It records both ratios, both tie-break ratios, S_A, L, R and
  the seeds, then the choice.
- **Commit order:** this file first, then the computations, then the choice, each as its own commit.

---

## Amendment 1 (round 49, Will, 2026-10-15) — replaces the metric and the S_A definition above
**When and why.** This amendment was made after the route (a) PASS, and after the rule above (6122a236) turned out to
be defective:
- Its S_A criterion, 4·T₆^sine(s) ≤ 1.43e-9, holds nowhere on its grid {1.8, …, 3.0}; it first holds at s = 1.7.
- It is committed before either candidate's power is computed.
- The κ₃ terms for (B) and the CUE replicates were running when it was committed. Their outputs had not been read or
  combined: only row counts had been seen.

**Global μ.** μ is the sealed route (a) family's global amplitude: every arithmetic part (CS08's n ≤ 5 correction)
is scaled jointly, with μ = 1 the prediction and μ = 0 the sine kernel.

**Metric (replaces the primary and tie-break ratios).**
- metric = |∂stat/∂μ| / SE_stat in the global μ family. stat is the candidate's pooled per-file amplitude μ̂ (as
  defined above).
- SE_stat comes from the CUE replicates (R = 100 per file, the same replicates for both candidates).
- The pooled metric is |Σ w_f ∂μ*_f/∂μ| / (Σ w_f² SE_f²)^½.

**Eligibility.** A candidate is eligible only if its block-cut n ≥ 3 share is at least 0.55. The block-cut share is the
share of its arithmetic part that comes from the n ≥ 3 correlation functions: the model with ρ₃… at the sine kernel's
values and ρ₂ at ζ's, against the full model, as route (a)'s block split.
- (A): Δp⁽²⁾ = ΔT₃ − 2ΔT₄ + 3ΔT₅ involves no ρ₂, so its block-cut share is 1 by construction.
- (B): the share is (ΔF₃ + 3L·ΔF₂)/(3ΔF₂ + ΔF₃), since ∫∫∫_{[0,L]³}Δρ₃ = ΔF₃ + 3L·ΔF₂.

**Choice.**
- The highest metric among eligible candidates wins.
- (B)'s L is chosen from {0.5, 1.0, 1.5, 2.0, 3.0} by the same metric among its eligible L. If no L is eligible, (B) is
  not eligible.
- If neither candidate is eligible: report that and stop.
- Exact ties: (A). This has no other role.

**S_A (replaces the definition above).** S_A is the largest s on {1.0, 1.1, …, 3.0} at which the n = 6 truncation bound
in μ units is ≤ 0.01 × (A)'s band at that window. It is computed data-free from the CUE replicate SEs:
- The bound is route (a)'s construction (route_a_zeta check (c)) applied to p⁽²⁾'s n = 6 term, 4·T₆:
  trunc(s) = 4·T6_CAP·|T₆^sine(s)| (T6_CAP = 100) at the nodes.
  δμ_trunc = Σ|trunc|·|Δp⁽²⁾| / Σ(Δp⁽²⁾)² on the window grid.
- (A)'s band at window s is 2·SE_pool,A(s), with SE_pool,A(s) from the CUE replicates' μ̂_A on the window s⁽²⁾ ≤ s.
- If no s on the grid qualifies, (A) is not eligible.

**Protocol (round 49, effective now).** No decode until the seal's OpenTimestamps receipt is Bitcoin-attested and
verified. This binds the follow-up's read.
