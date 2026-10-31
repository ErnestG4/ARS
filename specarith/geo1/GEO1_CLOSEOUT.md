# GEO1 close-out (2026-10-31): length spectrum of the modular surface

Arc: Step 0 (literature) → Step 1 (build and gates) → Step 2 (descriptive) → Peter-correlation seal. Brief and rulings
are in `ph2/PH2_DECISIONS_2026-10-07.md`. The Picard stage is not started and is recorded as open lead L12
(`OPEN_LEADS.md`).

## Step 1: build and gates (`GEO1_STEP1_RESULTS.md`)

The closed geodesics of SL(2, ℤ)\H were counted by trace t through three independent routes:
- explicit reduced words, t ≤ 3·10⁴;
- PARI class numbers, g = Σ_u h⁺((t² − 4)/u²), t ≤ 10⁶;
- Gauss reduction of forms, t ≤ 40.

Every gate passed, and each one has a red path that fails:

| Gate | Result |
|---|---|
| Class counts across routes | 0 mismatches in 29,998 traces |
| R²L² check | exact |
| Prime geodesic theorem | \|Π(T)/Li(ε²) − 1\| = 4.6·10⁻⁷ at T = 10⁶ |
| Gauss–Kuzmin | TV 2.5·10⁻⁵ over 3.8·10⁸ digits |

Π(10⁶) = 37,607,967,545 classes. Cost: 2.34 spot core-hours.

## Step 2: descriptive (`GEO1_STEP2.md`; no verdicts)

- **Multiplicities** follow the mean law 2e^{ℓ/2}/ℓ. Band means of g/(t/log t) reach 0.9999958 on 10⁵–10⁶.
- **Partial quotients** of the closed geodesics sit on the Gauss–Kuzmin law.
- **Mean even period** sits on Pollicott's (6 log 2/π²)ℓ.
- **Rates, descriptive only:**
  - *Prime geodesic theorem remainder.* The slope of log|Π/Li − 1| against log x over x = 10⁶–10¹² is −0.556 ± 0.022.
    The running-maximum envelope gives −0.494 ± 0.011. That is about the square-root rate (−½), well beyond the best
    proven exponent (Soundararajan–Young 2013, −11/36 = −0.306). **Slope caveat:** the remainder changes sign, so an OLS
    on log|·| is pulled by near-zero crossings (the two fits differ by 0.06). The data cover x ≤ 10¹² and cannot
    separate x^{−1/2} from x^{−1/2}·(log factors). This is consistent with the conjectured rate, not evidence for it.
  - *Gauss–Kuzmin convergence.* TV ∝ t^{−1.10 ± 0.02} by band. It sits 2–3.5× below the multinomial sampling floor:
    the digits are more regular than independent draws. Pollicott gives no rate.

## Peter-correlation seal (`GEO1_PETER_SEAL.md`, `GEO1_PETER_READ.md`): PASS

- **Prediction and data.** The prediction is Peter's (2002) Euler product for the multiplicity correlations γ(r), with
  zero parameters. It was tested on fresh traces 10⁶ < t ≤ 3·10⁶ at 22 lags plus r = 0: 45 statistics (ratios
  γ(r)/γ(0) primary; γ(0) and raw γ(r) secondary).
- **Procedure.** Seal, stamp (Bitcoin block 973951, verified on two explorers), fresh run, double read, `cmp` identical.
- **Inputs.** 200 of 200 independent class numbers match.
- **Witnesses.** As required: shuffled t and the matched-marginal null fail; the planted series passes.
- **Certified about 10⁻³, observed about 10⁻⁵.**
  - The sealed tolerances run from 6·10⁻⁵ to 1.4·10⁻³.
  - The observed deviations are at most 2·10⁻⁵ for the ratios and 10⁻⁵ for γ.
  - The SE method (block jackknife) overstated the error about 10× on this arithmetic sequence: fresh z RMS 0.07 / 0.13.
    That is the origin of TOOLKIT §9.G, and of lead L13 for RQ1.
- **What it is.** A confirmation of a known theorem on new data, not a new result.
- **Process notes** (`GEO1_PETER_RUNLOG.md`):
  - Launch 1 stopped at its cost check. My price assumed one discriminant per trace, but the average is 2.18.
  - Five orphaned workers outlived the stop and were killed by PID.
  - Launch 2 ran with a logged, Will-approved deviation in the launcher's cost guard and stop handling only.

## GRH

- **Up to t = 3·10⁴,** the class numbers are confirmed by the exact word count.
- **Beyond that,** including the whole Peter range, they come from PARI `quadclassunit`, which is conditional on GRH and
  not certified by PARI. The independent check (`qfbclassno` with a continued-fraction unit-norm parity, 200 samples)
  agrees, but it is not a certificate either.
- **Scope of the caveat.** Every multiplicity beyond 3·10⁴, and so the Step 2 rates on that range and the Peter seal,
  is GRH-conditional in its input. Peter's theorem and the prime geodesic theorem bounds are unconditional.

## Open

- **L12:** the Picard stage (PSL(2, ℤ[i]): complex lengths, multiplicities, holonomy angles).
- **L13:** does RQ1's SE model share the jackknife's overstatement on arithmetic angle sets?

Pushes (tag `geo1p-seal` and the commits since 4ee432e2) are Will's.
