# DOUBLING-BACK — ARS panel claims audited against the independent clean room

The clean-room reference suite (`/home/combust/fmexplorer/mathtest/`, 1393 rows) was built **in isolation** — literature-only,
"makes no reference to any other project." This is the designated pause-point audit: each banked ARS approximability claim
(A→D, in `FINDINGS.md`) cross-checked against the clean room's *independent* value. Rules carried over: structural/exact
invariants must agree; statistical differences are recorded; conventions/coverage-gaps flagged, not glossed.

**Verdict: convergent validation, no contradictions.** Every load-bearing ARS claim is independently corroborated (often
by a *different* method). The two most important: (1) the **liminf-K criterion values were independently confirmed**, and
(2) smooth-fit unfolding now has **BOTH of its failure modes characterized** — the clean room documented the *suppression*
mode (over-absorption on smooth input), the complement to ARS's *inflation* mode (residual trend on fractal input). See the
two corrections below — these are NOT "the same bug rediscovered" and NOT "independent convergence on our discipline";
overstating either weakens the real (and stronger) result. Discrepancies are all convention (integer-part inclusion) or
coverage (two constants the clean room didn't compute) — none substantive.

### Correction 1 — poly-unfold: mirror image, not "exact mechanism" (two modes, not one bug)
Smooth-fit polynomial unfolding fails in **opposite directions** depending on input:
- **Clean room (SUPPRESSION):** on smooth Poisson, poly7 absorbs genuine long-range fluctuation → Σ²(50)=**42 < 50** (too LOW).
- **ARS FIX-2 / Face-1 (INFLATION):** on a fractal Cantor spectrum, poly cannot flatten the devil's-staircase → residual
  density trend → Σ²≈**5000 ≫ 30** (too HIGH).
Same component, **opposite failure directions.** So the honest result is the **complementary half of the characterization**
— both failure modes of smooth-fit unfolding now documented, from two codebases that never met. That is *stronger* than
"rediscovered the same bug," but only if stated as what it is; "exact mechanism" launders two findings into one.

### Correction 2 — the Farey-Σ² refusal is TRANSMISSION, not independent discovery
The clean room did not compute Σ² on the Farey windows because its **spec forbids it** (D3: "windows emitted as data only,
no window's statistics interpreted in-repo"). That gate was written into the spec *because of* ARS Face-2's retune episode.
Causal chain: **Face-2 lesson → encoded in spec → clean room complied.** This is the protocol working (a lesson becoming
constitution and being obeyed) — but it is **transmission, not emergent convergence**, and this audit does NOT credit the
clean room with reaching our Panel-B judgment on its own. (Crediting a student for following the rubric.)

## Cross-check table

| ARS banked claim | ARS value | clean-room independent value | verdict |
|---|---|---|---|
| **A**: `C=dim·lnλ → ln(1+√2)` (golden) | 0.877 (λ→∞ extrap) | D1 `fib_dim_product` rises 0.773→0.872 (λ=8→64) toward theory **0.881374**; two estimators (band-scaling vs box) agree ≤0.02 | **AGREE** — ARS extrapolation lands in the clean-room high-λ range |
| **A**: Liu–Wen V>20 regime flag | λ=16 below proven | D1 marks λ=8,16 `outside_proven_regime=True`, λ≥24 False | **AGREE** (both honor V>20; clean-room boundary sharper) |
| **A/B**: `K(metallic-a)=a` exactly | 1,2,3,4 | D2 `metallic_geomean==a & single_record` **PASS** | **AGREE (exact)** |
| **A/B**: `K→K₀` (Khinchin) generic | GK 2.64–2.91 | D2 `cf_geomean` iid-GK N=10⁵ = **2.6863** (K₀=2.68545) | **AGREE** |
| **A/B**: `K(e)=K(Liouville)=∞` | e climbs→∞ | D2 Liouville geomean diverges; e spine unbounded | **AGREE** |
| **A/B**: `K(π)→K₀` (conditional) | 2.63→2.85 (k=20–150) | D2 `cf_geomean` π N=100 = **2.683**, inside iid-GK band [2.23,3.27] | **AGREE + enriched** (clean room bands show π is *typical*, not anomalous) |
| **B**: `Σ²_GUE=(1/π²)[ln2πL+γ+1]`, `Σ²_Poisson=L` | tool matched ~3% (L≤30) | Part I analytic unfold matches GUE Σ² to **~0.003** at every L | **AGREE** (clean room tighter — analytic vs poly unfold) |
| **B**: ordering `Σ²_GUE < Σ²_Poisson` | holds | 28 ordering gates pass (Σ² all L; crossover 0.388) | **AGREE** |
| **B / FIX-2 / Face-1**: poly unfold fails → wrong Σ² | Face-1 Cantor Σ²~5000 ≫30 (INFLATION) | **poly7 suppresses Poisson Σ²: 42 vs 50** (SUPPRESSION), `gate_failed` | **COMPLEMENTARY** — opposite failure mode, not same bug (Correction 1) |
| **FIX-16**: GUE surmise CV≈0.42 (not 0.522=GOE) | GUE 0.42 / GOE 0.52 | GOE surmise CV **0.5227** (exact-N 0.5333); GUE surmise 0.42 | **AGREE** — corroborates the FIX-16 correction |
| **B Face-2 / C**: Farey-near-α, `p'q−pq'=1` | invariant assumed | D3 `global_law` ~10⁻⁴; `p'q−pq'=1` verified every pair, all windows clean | **AGREE** |
| **B Face-2**: `Σ²(π)` demoted (uncertified) | struck → detection only | clean room enumerated same windows, computed no Σ² — but by **spec instruction** (D3 gate), which encodes the Face-2 lesson | **SPEC-COMPLIANCE / transmission**, NOT independent convergence (Correction 2) |
| **D**: metallic record count = 1 | 1 | D2 `single_record` PASS | **AGREE** |
| **D**: e records = linear spine | recs @ 1,6,9,12 val 2,4,6,8 | `e_record_process`: t=3k+2, val=2(k+1) | **AGREE modulo convention** (integer-part; see below) |
| **D**: π records ~ log; BB `a_n≥n` i.o. | R=6@N=600; BB≈10 | π `cf_record_count`=3@N=100, `cf_max_over_N`=2.92 (=292/100), exceedances match | **AGREE modulo convention** |

## Convention differences (reconcilable, not contradictions)
- **Integer-part inclusion.** Clean room D2 uses `x∈(0,1)` ⇒ quotients `a₁,a₂,…` with the **integer part excluded**; ARS
  Panel A/D used `cf_digits(mp.e)`/`cf_digits(mp.pi)` **including** `a₀`. This shifts record positions/counts: π record
  count 3 (clean, excl the "3") vs ARS 4 (incl); e-spine positions differ. Structural agreement (linear e-spine, π-log,
  even values); the offset is purely the convention. *(Both defensible; note for any future merge.)*

## Coverage gaps (clean room did NOT independently check these ARS claims)
- **`dim E₂ = 0.5312805`** (Panel A primitive gate, Jenkinson–Pollicott). Clean room D2 computes the *Khinchin* geometric
  mean K₀, not the CF-Cantor Hausdorff dimension E₂ — so E₂ rests only on the ARS transfer-operator computation (which
  itself hit 7 digits, but is un-cross-checked here).
- **`𝓛(gold)=log φ=0.4812118`** (Lévy constant). Clean room does geomean-K, not the Lévy growth-rate — un-cross-checked
  (though `log φ` is trivially exact).

## Refinements the clean room adds (ARS should inherit)
- **Δ₃ asymptotic form is invalid at small L.** Clean room verified the Σ²/Δ₃ *log-formulas* are large-L asymptotics: Δ₃
  goes negative at L=1 and **inverts the GOE/GUE ordering below L≈3.678** (Σ² below 0.388). ARS long-range work used
  Σ²/Δ₃ via `longrange_verdict`; any Δ₃ *closed-form* comparison should be gated to L≥5. (ARS mostly compared to MC
  ensembles, so likely unaffected — but worth the explicit caveat.)
- **Galambos max-quotient law flagged provisional** (clean room couldn't confirm the source via search; cross-checked it
  computationally instead). ARS Panel D's Borel–Bernstein used Liu–Wen/BB directly, so unaffected, but the max-law
  citation is softer than assumed.

## Bottom line
An independently-built, literature-only reference suite **convergently validates** the ARS approximability series: the
DEGT constant (C→ln(1+√2)), the liminf-K criterion (metallic=a, →K₀, e/Liouville=∞), the V>20 regime, and the FIX-16 CV
constants. Two claims are deliberately *not* overstated (see Corrections 1–2): the clean-room poly-unfold finding is the
**complementary (suppression) failure mode** to ARS's inflation mode — together a fuller characterization of smooth-fit
unfolding, not one bug found twice; and the clean room's Farey-Σ² refusal was **spec-compliance transmitting the Face-2
lesson**, not independent convergence. No contradiction anywhere; open items are two un-cross-checked constants
(`dim E₂`, `𝓛` — the Lévy constant is cheap to close later: quadratics have closed forms, a.e. value π²/(12 ln 2)≈1.1866,
verify-before-encode) and the integer-part convention offset in record indexing. The doubling-back closes clean.
