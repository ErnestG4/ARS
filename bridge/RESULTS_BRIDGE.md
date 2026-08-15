# RESULTS — ARS Bridge Arc (transition functions to the spatial-statistics atlas)

**Date:** 2026-08-14. **Brief:** amended Bridge brief (Will's revision of same date).
**Prereg:** `bridge/prereg_sealed.json` (sealed after pilot/anchor derivation, before all gate
compute; pilot seeds disjoint from gate seeds — see seal `author` field).
**Anti-claim (binding, brief §5):** no new universality-class claims. Deliverables are
translations, cross-checks, and protocol.

**Header disclosures (sealed-before or caught-during, all filed):**
- **Tripwire-2 catch in the draft brief itself:** the draft filed Ginibre under "logarithmic
  number-variance growth"; Ginibre is Torquato **Class I** (perimeter law, S(k)~k²) and log
  growth (Class II) belongs to the 1D sine-kernel. Caught in CC review pre-seal; recorded per
  the amended brief (`prereg_sealed.json` `filing_note_tripwire2_catch`).
- **Step zero:** R + spatstat 3.6-2 installed user-space (micromamba) at `bridge/.rquarantine/`
  (gitignored). Observer B is genuine spatstat; the pure-Python independence caveat was NOT
  needed. Declared family list verified installed: dppGauss, dppCauchy, dppMatern, dppPowerExp.
- **Declared approximation (B-cells):** the Ginibre kernel is complex and outside every real
  DPP family fitted here; all claims are class-level (tripwire 6). On the exact Ginibre curve
  every real family saturates its existence boundary (`at_boundary=True` in the fitter's own
  rail) — the theory-predicted signature.
- **B2 window sealed before B1 ran** (`gaussian_prime_annulus.py`: r∈[3000,3600], θ∈[0.15,0.35];
  support = checkerboard sublattice of Z[i]; intensity model λ(r)=2/(π ln r)).

---

## BRIDGE-A — translation table + dual-dialect calibrator runs: **CONFIRMED**

Deliverable: `bridge/TRANSLATION_TABLE.md` (12 rows incl. the 5 mandatory ones).
Estimators: `bridge/observer_b.py` (dimension-tagged, border-corrected).
Measured: `bridge/bridge_a_measured.json`. **All eight sealed gates PASS:**

| Gate | Result | Sealed tolerance | Owner of tolerance |
|---|---|---|---|
| G-A1 1D (Poisson K, g) | max dev 0.0134 / 0.0493 | 0.05 / 0.109 | pilot (seeds 100-102) |
| G-A1 2D (Poisson L, g) | max dev 0.0479 / 0.0588 | 0.088 / 0.122 | pilot (seeds 100-105) |
| G-A2 (zeta pcf vs sine kernel) | max dev **0.0640** on s∈[0.25,5] | 0.0908 | **banked anchor** `bridge/gue_pcf_anchor.json` (88,512 pooled GUE levels, semicircle-CDF unfold) |
| G-A3 1D Poisson (gluing) | rel ≤ 0.4% at L∈{2,5,10,20} | 5% | pilot |
| G-A3 1D zeta (gluing, L≤5) | 7.9% (L=2), 14.7% (L=5) | 11.3% / 21.7% | GUE gluing pilot, noise-scaled (seal) |
| G-A3 2D (Poisson + Thomas, R=2) | 6.4% / 1.2% | 10% / 15% | pilot-4 |
| G-B1 (Ginibre pcf vs 1−e^{−r²}) | RMS **0.0194** (max 0.0597) | RMS 0.0408 | pilot-3 |
| XCHECK (ours vs spatstat Kest border) | 0.41% (Poisson), 1.08% (Ginibre) | 2% | seal |

Observer-A numbers on the zeta window (dual-dialect row): ⟨r̃⟩ = 0.61092, KS_GUE = 0.0193 vs
KS_Poisson = 0.2982, Σ²(20) = 0.584 (GUE asymptotic reference 0.650, `universality.py`
number_variance docstring). Same data, Observer B: pcf hugs 1−(sin πs/πs)² to 0.064 max dev.
The two dialects read the same substrate the same way through their own charts.

*⟨r̃⟩ annotation (descriptive row — NO gate consumed ⟨r̃⟩; G-A2 is pcf-based):* the +0.008
excess over the GUE reference 0.60266 (constant owner:
`arsrh/phase1_zeta_crossover_measured.json` `reference_GUE_rtilde`; Atas–Bohigas–Roux–Vivo
2013 per `arsrh/PHASE1_PREREG_SEALED.json` "reference") is NOT tolerance headroom and NOT
finite-window jitter (≈9× the n=100k jitter scale). It is the **already-banked P1 low-height
crossover**: P1's matched-window GUE null band at W=10⁴ is [0.5952, 0.6065] with
`all_heights_inside_null_band: false`, and the excess decreases with height inside our own
window (low half 0.6119 → high half 0.6100; heights 14–74,921 = the low-γ leg P1/P5b/5c
chased). Implementation validated on synthetic GUE (0.60305 ± 0.002, 4 seeds). Cross-ref
`arsrh/PHASE1_FINDINGS.md`; no new claim here.

**P3 attribution-slot outcome:** the GUE R₂ analytic *form* is owned by `universality.py`
(pair_correlation); **no repo file owned a g(s)-shape tolerance** — `arsrh/phase3_sigma2.py:78`
holds a Σ²-slot tolerance and citing it in the R₂ slot would have been an attribution-slot
violation. The banked micro-anchor `bridge/gue_pcf_anchor.json` now owns it.

### Instrument finding (banked, TOOLKIT §11.3): the gluing identity's SNR law

The Σ²-from-pcf identity (G-A3's transition) is a **near-cancellation for rigid processes** and
amplifies any pcf baseline offset δ by ~(λ|B|)²/Var. Measured, all filed descriptively in
`bridge_a_measured.json`:
- 2D Poisson: rel dev 6.4% → 32% across R=2→6 (identity vs pooled grid-count direct);
- zeta: 7.9% → 142% across L=2→20 (amplification L²/Σ² ≈ 555 at L=20);
- Ginibre (Class I, worst case): 1% → 33% across R=2→6, amplification factor 3.6→14.7.
Consequence sealed pre-gate: gate the identity only at small windows (R=2 / L≤5); large-window
rows are the amplification law, not transition defects. A *small-window* failure remains a real
defect (dimension slip, factor error, normalization inversion — the FIX-2 class).

---

## BRIDGE-B — other-atlas check via DPP fitting

### B1 (Ginibre KAG, class-level): **CONFIRMED**

Measured: `bridge/bridge_b_measured.json` `B1`. Python minimum-contrast (`bridge/dpp_python.py`)
on the pooled 12-seed ĝ: best real family = **Gaussian-kernel DPP**, D = 0.0468 vs Poisson
0.3863 (8.3×) and Thomas 0.3863 (degenerate to Poisson); r_half/spacing = 0.332 ∈ sealed
[0.2, 1.0]. **spatstat's own `dppm` lands on the same family with D = 0.0467 under the uniform
contrast** — the two implementations of the other atlas agree to 3 decimals. G-B1 (exact-theory
gate) passed upstream in A2. Sealed class-level claim satisfied on every criterion.

### B2 (Gaussian-prime annular wedge, window sealed pre-B1): measured + triangulated

n = 31,107 split Gaussian primes; λ̂ = 0.07855 vs Landau model 0.07858 (**0.04%**); intensity
variation 1.9% predicted / 1.0% banded — inside the sealed 5% budget.

**The fine-bin pcf is a lattice comb** (bins 0.25): support exactly at checkerboard-Z[i]
distances — g = 3.07 at √2, 2.01 at 2, 1.48 at 2√2, 3.66 at √10, **zero elsewhere below 4**.
The peaks are prime *constellations* (both endpoints prime at lattice offset — the Z[i] analog
of twin primes), Hardy–Littlewood-weighted. The other atlas's own dialect displays the
support-set discipline (TOOLKIT §9) raw.

**Class-level fit outcome (one row, two clauses — scale-qualified by requirement):** best DPP
improves the contrast over Poisson by only 2.3% (D 12.98 vs 13.28, dominated by the comb);
Thomas degenerates to Poisson in both implementations (python: κ→bound; spatstat: κ=256,
scale=239 → flat). Coarse-grained g (bins 1.5) fluctuates about 1 with no systematic
inhibition or clustering trend. Read, both halves inseparable: **(i) Poisson-class AT SPACING
SCALE** — a coarse-grained statement, bins ≥ lattice pitch, r ≳ 2; **(ii) BELOW spacing scale
the pcf is by construction a lattice comb** (points live on the checkerboard sublattice, so
discrete support with Hardy–Littlewood constellation weights is the support set talking, not a
class property). Quoting clause (i) without clause (ii) — or reading them as contradictory —
is the slot hazard this wording exists to prevent: same fact, two scales.
spatstat cross-check (θ-subwindow n=7,727; full wedge + dppPowerExp OOM at 15GB — declared
limitation): same D ordering (12.99–13.01 vs 13.28).

**B3 triangulation filing: AGREEMENT (interface-coverage triangulation).** ARS class verdict
for this substrate is the Phase 34d **Hecke-Poisson** read on the angle observable
(`PHASE34D_FINDINGS.md`, verdict table row 34d). The other atlas, reading the planar
configuration, returns Poisson-class as well. Observable-binding note
(observable_binding_clarifies): the spatial dialect *sees* the lattice comb the angle
observable cannot; the comb is constellation clustering on the support set, not repulsion, so
it does not contest the class agreement — it maps a structure the home dialect's 34d chart had
no axis for. **No new universality claim** is made of it (brief §5); it is filed as the
DES/DESI-relevant capability demonstration: K_inhom + coarse/fine pcf on an inhomogeneous
arithmetic 2D substrate, end to end.

### K_inhom / FIX-2 exercises (transition 4 of the table)

- **Thin-window observation (pre-registered demo, found INERT):** on the wedge (2.2% intensity
  variation), K_inhom with the correct λ(r) and with a deliberately *inverted* gradient are
  identical to 3 digits (+6.2% at r=2, from the comb). At thin-window intensity variation the
  lens choice is immaterial — which is *why* the thin-window option (TOOLKIT §11.2 option 2) is
  safe. A falsifier that cannot fire certifies nothing (powered-falsifier discipline), so:
- **Powered designed instance (replacement, 3 seeds):** inhomogeneous Poisson on the same
  wedge, λ(r) ∝ (r/3000)⁸ (4.7× variation). Correct lens: K_inhom/πr² − 1 within ±1–2% (all r,
  all seeds). Wrong lens (stationary K, gradient ignored): **+13.4% to +15.6% everywhere** —
  manufactured clustering, the FIX-2 twin firing on demand.
- **Bonus in-vivo catch:** the first powered run drew Poisson(λ_max·A·**1.05**) proposals — a 5%
  sampler/model intensity mismatch that K_inhom faithfully reported as +5% across all r and
  seeds, caught by the replicate check (`fix2_powered.sampler_bug_note`). The estimator
  amplifies nothing and hides nothing: wrong intensity in ⇒ wrong K out, at exactly the
  mismatch factor.

---

## BRIDGE-C — protocol lift: **DELIVERED (founding, not amendment)**

No 2D protocol existed in the repo. Founded as **TOOLKIT.md §11**: §11.1 edge corrections
(border/translation/isotropic + decision rule + r_max rule; Weyl-completeness gate
`sessionK/maass_analysis.py:5` filed as 1D ancestor), §11.2 intensity estimation (3-option
preference order + double-application tripwire + FIX-2 twin), §11.3 the gluing-identity SNR law
(instrument note from this arc's own pilots). First customer served as planned: P1's Ginibre
central sub-window (`bridge/ginibre_sampler.py`, C_WINDOW=0.8).

---

## Verdicts

| Cell | Verdict |
|---|---|
| BRIDGE-A | **CONFIRMED** — all 8 sealed gates pass; both dialects reproduce each other's numbers within sealed tolerance |
| BRIDGE-B1 | **CONFIRMED** — sealed class-level claim passes; python and spatstat agree to 3 decimals |
| BRIDGE-B2/B3 | **TRIANGULATION-AGREEMENT (scale-qualified)** — Poisson-class *at spacing scale* in both atlases (34d Hecke-Poisson ↔ DPP-fit near-Poisson, coarse-grained r ≳ 2); *below spacing scale* the pcf is by construction a lattice comb (checkerboard-ℤ[i] support, HL constellation weights) — one fact, two scales, both clauses required in any quotation; observable-binding capability note, no class claim |
| BRIDGE-C | **DELIVERED** — TOOLKIT §11 founded; cross-referenced from EPISTEMIC_STATE.md |

No OBSTRUCTION-BANKED verdicts: every apparent non-gluing during the arc (Ginibre gluing 111%,
Poisson gluing 34%, K_inhom +5%) was run to ground pre-seal or by replicate and attributed —
two to the amplification law (instrument property, banked §11.3), one to a sampler bug (fixed,
filed). The transitions themselves glue.

## Reproduction

`bridge/` pipeline order: `ginibre_sampler.py` (KAG) → `bank_gue_pcf_anchor.py` →
`pilot_tolerances.py` / `pilot2_gluing.py` / `pilot3_gb1.py` / `pilot4_thomas.py` →
`seal_prereg.py` → `run_bridge_a.py` → `run_bridge_b.py` → `patch_b2_addenda.py`.
R env: `bridge/.rquarantine/envs/rspat` (micromamba; not a runtime dependency of core ARS).
Python: `/home/combust/fmexplorer/bin/python3` with `PYTHONPATH=criticality_tool`.

---

## Defect ledger (exposure audit — every found defect, its window, its consumers)

**D-1: 1.05× proposal-count bug in the FIX-2 synthetic sampler.**
- *What:* `patch_b2_addenda.py` block (b), first execution, drew Poisson(λ_max·A·**1.05**)
  proposals instead of the thinning-theorem-exact Poisson(λ_max·A) — realized intensity 5%
  above the model handed to K_inhom, which reported +5% across all r and seeds.
- *Exposure window:* one run (the first `fix2_powered` execution). The sampler was **created
  after every gate had already run** — sequence: seal → `run_bridge_a.py` (all 8 A-gates +
  G-B1) → `run_bridge_b.py` (B1 criteria, B2 fits, inert demo on *real* Gaussian primes) →
  `patch_b2_addenda.py` (first use of any rejection-thinning synthetic).
- *Could it have touched a gate in principle?* No gate consumes rejection-thinned synthetics:
  gate samplers are numpy uniform/poisson (Poisson calibrators), matrix eigensolves
  (Ginibre/GUE), offspring sums (Thomas), deterministic sieve (Gaussian primes).
- *Runs in the window and verdict on each:* `fix2_powered` first run — AFFECTED, retained
  with `sampler_bug_note`, superseded by `fix2_powered_replicates` (3 seeds, fixed sampler:
  right lens ±1–2%, wrong lens +13.4–15.6%). All gate rows — UNTOUCHED.
- *Commits:* bug, catch, and fixed replicates all occurred pre-commit inside `7b488ba`; this
  audit found `7b488ba`'s copy of `patch_b2_addenda.py` still carried the 1.05 line and the
  replicates had no committed generator — both corrected in the follow-up commit
  (`patch_b2_addenda.py` fixed; `fix2_replicates.py` added as the committed generator).

**D-2 (found by this audit): reproduction gap.** The replicate generator existed only as an
inline session script. Closed: `bridge/fix2_replicates.py`.

No other defects were found in-arc; the three large pilot anomalies (Ginibre gluing 111%,
2D Poisson gluing 34–48%, GUE-1D gluing 194%) were attributed pre-seal to the §11.3
amplification law — instrument property, not defect — and shaped the sealed gate windows.

## Registered follow-ups (parked; anti-claim intact)

1. **Gaussian-prime comb as a 2D arithmetic calibrator candidate — REGISTERED.** A pcf
   supported on computable checkerboard-ℤ[i] offsets with Hardy–Littlewood constellation
   weights is a 2D point process whose two-point structure is predicted by number theory.
   **Epistemic tier (header-grade): conjecture-backed-computable** — the HL singular-series
   constants are computable to arbitrary precision but unproven, a distinct tier from the
   theorem-backed zoo entries (zeta window / Farey / Ginibre) and it must be filed as such.
   The future micro-arc: gate empirical comb weights (B2 measured g(√2)=3.07, g(2)=2.01,
   g(2√2)=1.48, g(√10)=3.66) against computed singular series; would give the calibrator zoo
   its first 2D arithmetic entry. B2 was, in effect, its unplanned pilot. Until that arc runs,
   the observable-binding finding remains a capability statement.
2. **Commutativity/holonomy pilot cell — still open (atlas-review recommendation).**
   Unfold-then-window vs window-then-unfold; orderings that disagree get filed. Now cheaper:
   this arc built dual implementations of every transition involved. One pre-registered pilot
   cell, next protocol arc.
3. **DES/DESI entry unblocked** — K_inhom, edge-corrected pcf, DPP fits, hyperuniformity-class
   Σ² all KAG-validated; §11.3 supplies the large-window validity constraint galaxy catalogs
   will hit first.

**Follow-up priority (decided 2026-08-14, Will's recommendation adopted):** (1) comb
micro-arc first — small, fully scoped, pilot data already banked; seats the zoo's first 2D
arithmetic entry and forces the conjecture-backed-computable tier into the zoo header schema.
(2) commutativity/holonomy pilot as the next protocol arc's opening cell (registered there;
loses nothing by waiting). (3) DES/DESI under its own scope brief, inheriting the validated
pipeline and §11.3 as founding constraints.
