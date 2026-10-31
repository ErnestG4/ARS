# GEO1 Step 2 (2026-10-30): the modular surface's length spectrum — descriptive, no verdicts

From the Step 1 data (gates passed: `GEO1_STEP1_RESULTS.md`). Script `geo1_step2.py` (committed before it ran);
numbers in `results/step2/STEP2.json`, figures in `results/step2/`. The full table (t, ℓ, g_all, g_prim for t ≤ 10⁶)
is `data/length_spectrum.csv.gz` (gitignored; sha256 in the commit message). Desktop, seconds; no spot time.

**Not computed on purpose:** multiplicity fluctuations and correlations (Peter 2002's γ(r)), the candidate sealable
prediction in `GEO1_STEP0.md`. **Disclosure:** while checking a sentence of this file, one fluctuation statistic was looked at: on t ∈ [10⁵, 10⁶],
the 1st–99th percentiles of g_prim(t)/(t/log t) are 0.32 and 3.0 (min 0.20, max 6.1). Nothing else (no variance, no
correlation). A seal on Peter's correlations or on α's distribution should use fresh traces beyond 10⁶.

1. **Length spectrum** (`geo1_length_spectrum.png`). Each trace t ≥ 3 is one length ℓ = 2 arccosh(t/2); multiplicities
   (primitive oriented classes) to t = 10⁶ (ℓ ≈ 27.6), up to 386,208 at a single length (t = 903,890). Band means
   follow the mean law 2e^{ℓ/2}/ℓ (Bolte 1993; Bogomolny 2003) from ℓ ≈ 7 on; individual traces scatter around it.
2. **Mean multiplicity** (`geo1_multiplicity_growth.png`). Band means of g_prim(t)/(t/log t): 0.963 (t 10–10²), 0.9958
   (10²–10³), 0.99965 (10³–10⁴), 0.999975 (10⁴–10⁵), 0.9999958 (10⁵–10⁶). The prime geodesic theorem's ratio
   Π(T)/Li(ε(T)²) − 1 falls from ≈ −0.2 at T = 10 to 4.6·10⁻⁷ at 10⁶, mostly negative below 10⁵.
   - *Interpretation, not checked:* the band means sit far closer to 1 than independent per-trace scatter would allow
     (that would give ≈ 10⁻³). The likely reason is that the multiplicity's fluctuations are arithmetic: α(n) is
     limit-periodic (Peter 2002), so they cancel over complete residue cycles. The same would make the PGT remainder
     small (1.7·10⁴ at T = 10⁶, below x itself).
3. **Partial quotients** (`geo1_partial_quotients.png`). Pooled over the primitive classes with t ≤ 3·10⁴ (3.8·10⁸
   digits), the frequencies sit on −log₂(1 − 1/(k+1)²) for every k ≤ 64; random words of matched length give the
   geometric law instead. The total variation from Gauss–Kuzmin falls with trace: 0.055 (t ≈ 15), 2.9·10⁻³ (150),
   2.1·10⁻⁴ (1,500), 9.4·10⁻⁵ (6,300), 2.7·10⁻⁵ (19,000).
4. **Mean period** (`geo1_mean_period.png`). The mean even period length (runs of the R/L word) per band of t lies on
   Pollicott's (6 log 2/π²)·ℓ from ℓ ≈ 8 on. The cumulative form (Pollicott's Prop. 3(i), Σ over e^ℓ ≤ e^L divided
   by the count, read at L) is 0.908, 0.924, 0.942, 0.949 of (6 log 2/π²)·L at T = 10², 10³, 10⁴, 3·10⁴. It approaches
   1 from below, as it must: geodesics up to L have mean length below L.

Next in the arc (Will's call): a seal on Peter's multiplicity correlations, on fresh traces beyond 10⁶; and/or the
Picard stage (PSL(2, ℤ[i]): complex lengths, multiplicities, holonomy angles).

## Additions (Will, 2026-10-30; descriptive) — `geo1_step2b.py`, `results/step2/STEP2B.json`, `results/step2/geo1_rates.png`
5. **Prime geodesic theorem, remainder rate.** OLS slope of log|Π(T)/Li(x) − 1| on log x, x = ε(T)² (the norm), over
   T ∈ [10³, 10⁶] (80 log-spaced T; x from 10⁶ to 10¹²): **-0.556 ± 0.022**; the running maximum of |·|
   (an envelope, less sensitive to sign changes) gives -0.494 ± 0.011.
   - Compare: −1/2, the conjectured square-root remainder (E(x) ≪ x^{1/2+ε}, as "believed" in Soundararajan–Young
     2013; original source not traced), against the best proven unconditional bound, Soundararajan–Young, *J. reine
     angew. Math.* 676 (2013), Thm 1.1 (arXiv:1011.5486): π_Γ(x) = li(x) + O(x^{25/36+ε}) for PSL(2,ℤ), i.e. relative
     x^{−11/36} = slope −0.306 (VERIFIED from the arXiv source; pages 105–120 SECONDARY). A preprint claim of 2/3
     (Kaneko, arXiv:2402.12133 v3) is unrefereed (`GEO1_STEP0B_PETER.md`, Task 2).
   - The data fall at the square-root rate over six decades of x, far below the proven bound's rate. Descriptive.
6. **Gauss–Kuzmin rate.** TV from Gauss–Kuzmin by band of t (4 bands per decade, t ≈ 10²–3·10⁴): slope of log TV on
   log t **-1.10 ± 0.02**, i.e. TV ∝ t^{−1.1} (Pollicott gives no rate). In every band the TV is
   2–3.5× **below** the multinomial sampling floor for the same digit count (median TV of 200 seeded multinomial
   draws from the Gauss–Kuzmin law): the digits of closed geodesics are more regular than independent sampling.
   Descriptive.
7. **Length-spectrum figure** redrawn at uniform density in ℓ (19,310 traces from 40,000 uniform ℓ), so the first
   version's t = 3,000 switch from every trace to a sample is no longer an edge.
