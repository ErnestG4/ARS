# CC Brief — Divisor Harmonics v0 (Will, 2026-10-03; verbatim)
**Side project. Runs only in idle GPU time and on spot's CPUs; it never preempts the main arc's queue. All operating rules carry over: GPU-only hard assert, seal before reading, no method changes without Will, jobs detached and resumable, completion notification.**

## 1. Question
Karkada et al. (arXiv 2602.15029) show that translation symmetry in co-occurrence statistics makes models represent periodic concepts with Fourier modes.
- The harmonic amplitudes follow a Lorentzian rolloff, a_n² ∝ 1/(1+σ²k_n²), set by the concept's correlation length σ.
- In the plane of harmonic n, the items of a period-N cycle land on vertex n·m mod N. They therefore form a regular polygon with N/gcd(n, N) vertices. For months (N = 12 = 2²·3): n=6 gives a line, n=4 a triangle, n=3 a square, n=2 a hexagon, and n=1 or 5 a 12-gon.

That polygon geometry is pure aliasing: under translation symmetry alone it is present but carries no extra amplitude. The question is about **amplitude, not geometry**:

> **Does real usage give the divisor classes of composite periods more amplitude than the Lorentzian (translation-symmetry) model predicts?**

Plausible sources of such an excess include quarterly reporting for months, shift patterns for hours, and base-10 habits for numbers. Related prior work: Kantamneni & Tegmark (2025) report number representations on helices with periods 2, 5, 10 and 100, the factors of the base. **Verify this citation before relying on it.**

The analysis tool is ARS's Ramanujan–Fourier engine. Ramanujan sums group harmonics by gcd class, so an RF decomposition gives one component per divisor q, which is exactly one polygon family each.

## 2. Hypotheses
- **H0 (translation symmetry only):** after fitting the Lorentzian, the leftover power shows no excess in any divisor class.
- **H1 (divisor excess):** one or more nontrivial divisor classes (1 < q < N) carry leftover power above the null, for composite N.
- **Prime control:** weekdays, N = 7. There are no nontrivial divisor classes. The Lorentzian should fit, with white residuals. Any "excess" here means the pipeline is broken.
- **Direction stated in advance (descriptive bets, not tests):**
  - months: the q = 3 and q = 4 classes (quarters and quadrimesters);
  - hours: q = 12 (am/pm) and q = 6 or 8 (shift patterns);
  - numbers: q = 2, 5 and 10 (frequencies 50, 20 and 10 on 0–99).

## 3. Concepts and prompts
| Concept | Items | N | Boundary condition | Notes |
|---|---|---|---|---|
| Months | Jan–Dec | 12 | periodic | "May" is ambiguous: use disambiguating templates (as the paper did) |
| Hours | 0:00–23:00 | 24 | periodic | 24 h format; avoid the am/pm ambiguity in the items themselves |
| Weekdays | Mon–Sun | 7 | periodic | **prime control** |
| Numbers | 0–99 | 100 | open | lattice with open BC; treat periods as frequencies |
| Shuffled control | 12 arbitrary nouns in a fixed random order | 12 | — | no cycle: everything should be null |

- **Templates:** 15–20 per concept, written and frozen before any activations are extracted. The position read is the last token of the item.
- **Tokenisation audit, done before sealing:** record how the Pythia/NeoX tokenizer splits every item, and flag any multi-token items. Numbers that split into several tokens get their own column in the results. Report every exclusion along with the reason.

## 4. Models
- **Primary:** Pythia-1.4B, final checkpoint.
- **Replication:** Pythia-410M and Pythia-70M, final checkpoints.
- **Trajectory (descriptive):** Arm B's A0 checkpoints (70M, already on spot), to see when any divisor excess appears.

## 5. Pipeline
1. **Extract** the residual stream at every layer, last item token, for every concept, template and item, on the 4090 (minutes). Store fp32 at about 0.6 GB per model.
2. **Average over templates for each item.** That is the sealed choice; per-template spectra are reported as a descriptive robustness check.
3. **Compute the harmonic spectrum.**
   - Mean-centre over items.
   - Take the DFT along the item axis of the (N × d) matrix.
   - Sum the power over all model dimensions (Parseval) to get P(n), for n = 1 … ⌊N/2⌋.
   - This needs no PCA, so it doesn't depend on the basis.
4. **Fit the Lorentzian null.**
   - For periodic N, use the paper's finite-lattice kernel: P(n) ∝ (1−q²)/(1−2q·cos(2πn/N)+q²), with q = e^(−2/(σN)).
   - For numbers (open BC), use the paper's open-BC quantisation.
   - The free parameters are σ and the scale. The fit is weighted.
5. **Decompose by divisor class.**
   - Group the leftover power by gcd(n, N) = q. This is the RF decomposition, one component per divisor class.
   - The statistic for each class is the summed excess over the Lorentzian, normalised by the null's spread.
6. **Primary layers:** the middle third of the depth, averaged. That is sealed; every other layer is descriptive.

## 6. Nulls, red paths and gates
- **Item-shuffle null:** 10,000 shuffles of the item order on spot's CPUs. It tests whether there is any cycle structure at all.
- **Lorentzian null:** a parametric bootstrap on synthetic activations with the fitted Lorentzian spectrum plus matched noise. It tests whether the leftover power exceeds what translation symmetry alone produces.
- **Red paths, run before sealing:** plant a divisor-class excess of known size into the synthetic data.
  - The pipeline must detect it at the declared rate.
  - With nothing planted, it must stay silent.
  - Report the smallest detectable excess per concept. If the planted excess can't be detected, H1 is NOT RESOLVABLE for that concept.
- **Control gates:** weekdays and the shuffled nouns must come out null. If either fires, nothing is interpreted.
- **Multiplicity:** Holm correction across all (concept × divisor class) tests in the primary model.

## 7. Outputs
- **DIVISOR_FINDINGS.md**, using the memo's status vocabulary, with every claim naming its gate.
- **Figures:**
  - for each concept, P(n) with the Lorentzian fit and bars coloured by divisor class;
  - for months and hours, the projections onto each harmonic pair, showing the polygon families. These illustrate the aliasing geometry and are not evidence.
- An **Open leads** section.

## 8. Compute
- **Extraction:** minutes on the GPU per model.
- **Nulls and bootstraps:** CPU-minutes on spot.
- **Trajectory over Arm B checkpoints:** minutes, since the weights are already on spot.
- **Optional extension:** the Pythia-1.4B revisions cost about 3 GB each to download, so they're bandwidth-bound. Only run that if Will asks.
