# Survey-Catalog Arc — Σ² Scaling Class of a Tomographic Galaxy Point Process (DESI DR1)

**Status:** APPROVED (Will's draft 2026-08-15; CC review amendments folded same day: per-slice
verdict lattice, 4.30× lineage correction, INSTRUMENT_HOLD sealed checklist + exit, tile-adjacency
clause, OBSTRUCTION envelope clause, BGS + projection-twin dry-runs, DD/RR ≡ 1 as the leading mask-KAG
identity). Ready for its sessions — split: D0+D1, then D2+D3, then D4.
**Lineage:** Bridge arc (KAG-validated 2D pipeline: K_inhom, edge-corrected pcf, Σ², DPP fits; TOOLKIT §11); §11.3 corrected SNR law A = μ²/Var (bridge remediation, 32f28bf); comb arc (tier schema, BOUNDED-AT-SCALE precedent, promoted protocol rules); B2 powered FIX-2 designed instance (wrong lens manufactures +14% at 4.30× gradient (1.2⁸), in-code firing criterion; figure per bridge remediation 32f28bf).
**Epistemic posture:** the measured object carries no theory tier — it is survey data. Gate anchoring uses **theorem-tier calibrators only** (Poisson, Ginibre); the comb (conjecture-backed-computable) serves as cross-check, never sole anchor (`assert_sole_anchor_allowed` enforced).
**Honest one-line frame:** this arc measures the number-variance scaling class of a projected tomographic galaxy point process under a fully stated mask/selection model — it is the pipeline's first contact with data whose window is hostile and whose intensity is not a theorem. The science claim is deliberately narrow; the durable output is the mask-and-selection discipline, gate-covered end to end.

---

## 0. Anti-claim (drafted before data, binding)

The measurement object is: **the projected 2D point process obtained from a sealed tomographic slice of a sealed DESI DR1 LSS tracer sample, under the survey's own randoms-defined window and weight model.** The arc claims, at most: its pair statistics and its Σ²(R) scaling class over a sealed scale range, per the Torquato taxonomy, with errors.

Explicitly out of scope, in the results header verbatim:
- **No cosmology inference.** No statements about Ω, bias, BAO, growth, or any parameter.
- **No statements about the 3D matter field.** Projection mixes scales; the claim attaches to the projected process as defined, full stop.
- **No "hyperuniformity of the universe" claims in either direction.** Harrison–Zel'dovich hyperuniformity is a k→0 statement outside any survey's reach; nothing measured here touches it.
- No class claims beyond the sealed scale range and slice (BOUNDED-AT-SCALE machinery standing by, per comb precedent).

## 0.1 Expectation registration (sealed with the prereg)

The registered expectation is **super-Poissonian (clustered) scaling at all accessible scales** — galaxy tracers are positively correlated; Var grows faster than the mean. This expectation is itself part of the seal, with the standing rule: **a surprising-direction outcome (sub-Poissonian/hyperuniform-class at any sealed scale) triggers instrument audit as the first response, banking only after the audit clears.** The arc's value does not depend on surprise; it is the class measurement plus its discipline. The interesting measured quantities are the scaling exponent, its scale-dependence, and the crossover structure — not the sign of the departure from Poisson, which is known.

## 1. Structural-null audit (front-loaded)

**Generative-substrate family:** weighted, masked, inhomogeneous point set on the celestial sphere within a redshift slice; window and radial/angular selection defined operationally by the survey's randoms.
**Natural null:** **the survey's own randoms**, weight-matched and thinned to the data's effective intensity — Poisson-through-the-actual-window. Every mask hole, ragged boundary, and depth variation is reproduced by construction; departures from this null are the measurement.
**What the wrong null would do:** an unmasked or analytically-windowed Poisson manufactures "clustering" from every mask hole and "regularity" from every boundary erosion. No analytic-window nulls appear anywhere in this arc's data path (they remain in synthetic KAGs only, where the window IS analytic).
**Null implementation:** randoms-backed expectation is the primary estimator route throughout (Landy–Szalay-style counting against randoms for pcf/K; randoms-normalized cell expectations for Σ²). The bridge's `dist_to_boundary()`/`area()` window API gains a **RandomsWindow** class whose geometry queries are Monte Carlo integrals over the randoms. Analytic border correction survives only as the synthetic-KAG cross-check.

## 2. Data (sealed at D0)

- **Catalog:** DESI DR1 LSS clustering catalogs, public release (`data.desi.lbl.gov/public/dr1/.../LSScats/`, version sealed at D0 — v1.5 unless CC finds cause), `*_clustering.dat.fits` + matched `*_clustering.ran.fits` randoms with completeness and imaging-systematics weights per Ross et al.
- **Tracer + slice (proposed, final at seal):** LRG, NGC footprint only (contiguity), one redshift slice in 0.6–0.8; BGS held as the denser low-z alternative if the power seal demands it. Second slice (0.4–0.6) reserved for the inter-slice comparison row.
- **Randoms:** all released random files for the tracer, concatenated; their 2500 deg⁻² per-file density is the window's operational definition.
- **Provenance:** blob-SHA manifest of every downloaded file in the seal; committed acquisition script (D0 is a cell, not a footnote).

## 3. Cells

### D0 — Acquisition + provenance
Download, verify, manifest. Deliverable: `survey/MANIFEST.json` (SHAs, versions, row counts), acquisition generator committed.

### D1 — Window engineering + mask KAG (the arc's load-bearing cell)
- **RandomsWindow** class implementing the window API against randoms (point-in-window, effective area, boundary handling via randoms density).
- **Tiling scheme:** tangent-plane projections of pre-registered sub-patches (proposed ~10°×10°, gnomonic, equal-area-corrected), each tile a replicate; projection/curvature distortion budget computed per tile and sealed (tiles whose distortion exceeds budget are excluded *by the sealed rule, before measurement*).
- **Mask KAG (the witness that can fail):** synthetic Poisson realized by thinning the randoms themselves to matched intensity, pushed through the full estimator stack. **The gate in ratio form: thinned-randoms-as-data must return DD/RR ≡ 1 in expectation within sealed tolerance** — that is the window-cancellation identity the randoms-backed route certifies; the three observable gates follow from it: g ≡ 1, K_inhom = πr², Σ² ∝ mean, per tile class. This gate fires red on any mask-handling defect by construction. Run at both KAG and per-tile-acceptance grade.
- TOOLKIT §11.1 gains its **mask row** (decision rule: randoms-backed primary; analytic corrections synthetic-only) in the same stroke.

### D2 — Intensity/selection model (the FIX-2 crucible)
- Intensity = randoms density × survey weights, **exclusively external**: completeness and imaging-systematics weights as released, radial selection from the randoms' dN/dz. **The selection function is never fitted on the catalog being measured** (§11.2 preference order, top slot).
- **Ported powered designed instance as a gate:** the deliberately-wrong lens (unweighted randoms where weights are required) must manufacture spurious clustering above its in-code firing criterion, and the right lens must return the mask-KAG Poisson within budget. The B2 instance's pattern, re-aimed at survey weights.
- Weight-variation budget per tile sealed; tiles exceeding it excluded by rule.

### D3 — Measurement
- Per-tile, per-slice: edge-corrected pcf and K_inhom versus the randoms null; **small-scale exclusion sealed at r_min above the fiber-collision scale** (fiber assignment suppresses close pairs; PIP weighting is explicitly out of scope, so the sealed r_min is the honest instrument boundary and is stated in every artifact).
- **Σ²(R) by direct count-variance in mask-aware cells** across a sealed R-range — this carries the class measurement. **Sealed division of labor per corrected §11.3:** at survey μ the gluing identity's amplification A = μ²/Var is 10⁴–10⁸; the Σ²-from-pcf route is descriptive-only, never a gate, and its rows say so.
- Class assignment per Torquato taxonomy on the projected process; scaling exponent with per-tile scatter as the error model (tiles as replicates; the comb's correlated-z lesson applies *within* tiles, tile-to-tile is the independent axis). **Adjacency clause:** adjacent tiles share large-scale modes, so for r-bins approaching the tile scale the error model uses sealed non-adjacent tile subsets (or a sealed effective-N statement) — tile scatter is not treated as fully independent at the largest bins.
- **Inter-slice comparison (descriptive, no gate):** the second redshift slice is a different projected process — bias evolution and projection depth make inter-slice differences physics, not drift. Consistency of *class* is expected and reported; exponent differences are filed descriptively. Within-slice drift across the sealed R-range is the BOUNDED-AT-SCALE axis.
- DPP fitting: omitted from gates (clustered data; repulsion families are the wrong shelf); permitted as one descriptive row if cheap.

### D4 — Filing
RESULTS_SURVEY.md (verdict TL;DR, per-tile table, class + exponent + errors, drift section); EPISTEMIC_STATE.md same-stroke; TOOLKIT §11 amendments (mask row, survey-weights preference-order entry); memory updates; comb-style three-event labeling for anything post-hoc.

## 4. Verdict lattice (shared module, per rulings-as-code)

Implemented in the verdict module the runner imports, not prose. **Verdicts attach per slice** — the claim attaches to "a sealed tomographic slice" (§0), and the lattice matches the anti-claim:
- **CLASS_MEASURED(slice, class, exponent, range):** mask KAG + FIX-2 gate green in every included tile of the slice; pooled per-tile class assignment consistent; no within-slice drift across the sealed R-range beyond counting error.
- **CLASS_MEASURED_BOUNDED_AT_SCALE(slice):** as above with coherent *within-slice* drift across the R-range; drift law filed in the claim. (Inter-slice differences are physics and never enter any verdict — they file as the D3 descriptive comparison row.)
- **UNDERPOWERED(slice):** sealed power criterion unmet after the (numeric, dry-run-verified) extension rule fires once.
- **OBSTRUCTION_BANKED(slice):** pcf-side and count-variance-side class calls disagree after transitions audited clean, **and the disagreement exceeds the §11.3 predicted envelope** — at survey μ the two routes are *expected* to disagree within A = μ²/Var of the measured pcf noise floor at that scale, so the verdict requires excess beyond the computed envelope; otherwise every large-R row would be an "obstruction" and the genus dilutes to noise.
- **INSTRUMENT_HOLD(slice):** the §0.1 surprise clause fired. The hold ships with its **sealed audit checklist**: weight-variance map of the offending tile(s); mask-hole density vs neighboring tiles; redshift-failure spatial correlation against the offending region; randoms-density uniformity test at the offending scale. **Exit condition, sealed:** all checklist items pass at their sealed thresholds → the result banks with the audit attached; any item fails → defect filed, tile(s) excluded by rule, measurement re-run. No banking, and no other analyst action, while in hold.

## 5. Tripwires

1. **Double-weighting:** weights enter the intensity model *or* the pair estimator normalization by one sealed convention — never both. (FIX-2's survey-scale twin.)
2. **Randoms reuse:** the randoms thinned for the mask KAG and the randoms used as the null in measurement are disjoint subsets, sealed split.
3. **Tile-selection freedom:** tile inclusion/exclusion is by sealed budget rules only; no post-measurement tile pruning.
4. **r_min honesty:** no statistic quoted below the fiber-collision seal, including descriptively.
5. **Scale-range creep:** the Σ² R-range is sealed; extensions follow the one-shot numeric rule or don't happen.
6. **Analytic-window leakage:** any analytic-window computation touching survey data (rather than synthetic KAG) is a defect, not a convenience.

## 6. Carried-through protocol (inherited, cited)

Code freeze + blob-SHA at seal; prediction-first where predictions exist (here: expectation registration §0.1); committed generator for every banked number; sealed-contingency dry-runs (extension rule, tile-exclusion rules, **the BGS fallback — loader + power — executed once on synthetic before seal**, and **a projection twin in D1's KAG: the thinned-randoms test run on tiles at declination extremes, confirming the gnomonic distortion budget covers what it claims**); witness-must-be-able-to-fail (mask KAG's red path demonstrated deliberately once); verdict lattice as shared module; live `verify_survey.py` nonzero-exit checker; pilot-informed-seal addendum if any pilot shapes the seal; sole-anchor tier rule enforced in code.

## 7. Out of scope

3D statistics; PIP/angular-upweighting; cross-tracer or cross-survey comparisons; DES Y6 (deferred — photometric z's are a different arc's problem); any k-space statement; any claim below r_min or outside the sealed R-range; cosmological interpretation of any number.

## 8. Open questions for CC (resolve at D0/seal)

1. Tracer + slice power check: LRG 0.6–0.8 NGC vs BGS low-z — which delivers the sealed σ targets at the proposed tile size (analytic power seal before download commits the choice).
2. Tile size trade (curvature budget vs per-tile counts vs number of replicate tiles): propose from the randoms' footprint geometry before sealing.
3. v1.2 vs v1.5 catalog version; NGC-only confirmation.
4. Fiber-collision scale for the LRG sample → numeric r_min proposal for the seal.
5. Whether the RandomsWindow MC geometry queries meet the estimator stack's precision needs at KAG grade, or whether a hybrid (randoms + pixelized mask) is required — decide in D1, file the decision.
