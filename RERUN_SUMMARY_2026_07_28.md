# The 2026-07-28 rerun arc — what was recomputed, what it found, where it goes

Four reruns, all sharing one design: **reproduce the deployed number first, then read the repaired
one beside it.** A repaired value from a pipeline that cannot reproduce its own banked output is
worthless, and that check is the only evidence the pipeline was re-entered correctly. It passed
every time — **8,001 + 21 rows reproduced, zero mismatches** — which is what licenses everything
below.

---

## 1. `gate0e` — deduped (R-172)

`collect_cyclic` enumerates **polynomials** and dedups by nothing; several per stratum are GL₂(ℤ)
translates of the same cubic. `z` scales as √k under k-fold duplication, so `χ² = Σz²` scales as k.

| block | χ²/df dup → dedup | p dup | **p dedup** | |
|---|---|---|---|---|
| `by_a` | 1.82 → 1.03 | 1.2e−02 | **0.42** | retracted |
| `by_lambda` | 1.95 → 1.07 | 5.8e−03 | **0.38** | retracted |
| **`by_conditional_g`** | 2.63 → 1.19 | **6.4e−05** | **0.24** | **retracted** |
| `both_corrections` | 3.31 → 1.83 | 1.5e−04 | 0.043 | weakened |

**Ratios were predicted invariant before the run and held to ~1%** (bias +0.0817 → +0.0819).
**The trend survived**: slope −0.0399 ± 0.0112 → −0.0378 ± 0.0111, because it regresses across
*strata*, which duplication cannot touch. **The dispersion verdict was an artifact; the systematic
is real** — and the systematic is what keeps R-077's grade at CALIBRATED.

`gate0f` needed **no** rerun — checked, not assumed: it computes no pooled z or χ². One claim was
corrected (it reported witnesses as *distinct discriminants*, which **undercounts**: |t|=5 has 1
discriminant but 2 orbits).

---

## 2–4. The coordinate store — kuramoto, pvc-11, allen-np (R-173 … R-176)

`source_artifact` points at a **results table, not the raw object**, so recomputability had to be
decided per substrate. All three were regenerable; all three reproduced exactly.

| substrate | recs | repro | at 0.0 | changed | clustered | **sign-inverted** | dep median | signed median | signed min |
|---|---|---|---|---|---|---|---|---|---|
| kuramoto | 6,298 | 6,298/6,298 | 20 | 5,146 | 78 | **58** | **+0.8500** | +0.6584 | −4.48 |
| pvc-11 | 1,159 | 1,159/1,159 | **918 (79.2%)** | **100%** | 1,157 | **239** | **0.0000** | −0.7015 | −5.57 |
| allen-np | 544 | 544/544 | **385 (70.8%)** | **100%** | 537 | **152** | **0.0000** | −0.7240 | −2.67 |
| **total** | **8,001** | **0 mismatch** | | **6,849 (86%)** | **1,772 (22%)** | **449 (5.6%)** | | | |

### Three findings, in ascending order of consequence

**(a) The clip has an UPPER rail nobody had looked for.** When R₂ ≡ 0 the integrand is 1.0 across
the mask, so the integral returns the **mask width, 0.85**. **56.2% of kuramoto sits there**,
collapsing a true range of +0.403…+0.850 onto one number. All prior work characterised only the
*lower* rail (0.0).

**(b) 449 cells reported the OPPOSITE CLASS.** Not lost magnitude — the clip integrates only the
*positive* excursions of (1−R₂), so a net-clustering process with any repulsive range comes out
**positive**. pvc-11's worst: deployed +0.1065 where the truth is −2.4622.

**(c) ★ THE CLASS LABEL INHERITS THE RAIL (R-177).** `primary` is assigned by thresholding the
**clipped** field — `BL: rep_int < 0.10 → "Poisson noise"`. The axis floor is 0, so clustering has
nowhere to go but BL. **Of 1,660 cells labelled BL, 1,658 are genuinely clustered.** BL is not
"Poisson noise"; it is **99.9% clustered**. A further 108 clustered cells sit in TR
("Wigner-class").

> This is the one that matters. `rep_med` is a coordinate; **`primary` is the classification**, and
> it is banked in every fingerprint and per-cell verdict downstream. The recompute fixed the
> coordinate. **The label is still wrong.**

It is also [[soc_pair_complete]] recurring verbatim — that entry already says *"one-sided fitters
are blind to super-Poisson"* and records the joint-plane classifier calling solar flares "Poisson
noise". Banked lesson, unchanged call site.

### Why one summary statistic never characterised this store

The rails are **substrate-specific and point in opposite directions**: kuramoto is dominated by the
**upper** rail (median +0.85), pvc-11 and allen-np by the **lower** rail (median 0.0). Averaging
across them ("16.6% exactly 0") cancelled the two failure modes against each other.

`clipped ≥ signed` holds on all 8,001 cells — the one surviving invariant, and the reason a banked
value is usable as an **upper bound** and nothing else.

---

## Mistakes made and caught, this arc

- **Thin-slice costing.** Timed `classify` on `sim.spikes[0]` (n=157) and projected 6 min; the
  median oscillator is n=2,304 and the true cost was 4.0 h. **A 45× miss from sampling the first
  element** — the same sampling-frame error `gate0f` exists to document.
- **`.get(key, 0)` across a changed schema.** The first combined roll-up read kuramoto as *0
  clustered, 0 inverted* because that report predates those keys. **A missing field defaulted to a
  number that reads as a finding.**
- **Asserted gate0f was corrupted** before checking. It wasn't.

---

## Where this can go — five directions

**1. Fix the class vocabulary (largest, and newly visible).** BL conflates Poisson with clustered
because the axis had no negative region. The repair is a **new quadrant**, not a threshold tweak —
a change to the class vocabulary requiring a **sealed re-registration**, then re-deriving every
banked `primary`. Everything downstream of the classifier rests on this.

**2. Tier B — the 19,619 `I.8_brody_q` values.** The remaining known-corrupt block, needing the
per-substrate pipelines re-run over the 29–62 GB caches. Now with a specific reason: Brody has the
same two-ended rail structure this arc made quantitative for `rep_med`, and `I8_brody_q_unbounded`
already exists.

**3. A standing rail detector (the systemic move).** We have now found rails in `rep_int` (both
ends), `brody_q` (both ends), and `berry_robnik_rho` (all four calibrators rail-proximate). Rather
than auditing axes one at a time, build a guard that sweeps **every axis in the store** and reports
saturation per axis per substrate, wired into `tests/`. This converts a recurring discovery into a
check that fires by convention.

**4. Downstream consequence sweep.** 449 sign inversions and 1,658 mislabelled BL cells — which
banked *findings* rest on them? The n=7 clustering⊥coupling finding was already verified to use the
repaired field, but pvc-11's block feeds the H1/pillar work and its `primary` labels are suspect.

**5. Research, untouched by any of this.** **R-044** — the far block at 10²² tests the F-integral
where SPCC predicts exactly 1, to 0.33%; still the only item pointing at a conjecture rather than a
theorem. **Dirichlet between-object** — 630 characters local, pairings theory-specified, cubic
machinery transports, now carrying the GL₂(ℤ)-orbit-dedup warning before anything is pooled.

**Also open, mechanical:** the 239-site `rep_int` migration (tracked, non-increasing).
