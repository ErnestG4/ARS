# IDS-Unfold Leg Redesign — BRIEF (filled 2026-05-17)

**Status:** BRIEF — fill + commit only. **Brief-and-hold:** no build, no compute, no arc-resume without an explicit go. This brief *fixes the instrument*; it does **not** resume the 35a/35b arc (everything stays parked at its logged checkpoint). Asymmetric label throughout: a redesigned instrument is **validated**, never a discovery.

## §1 Frame

`unfold_ids_ref(eigs, eigs_ref)` unfolds a cell spectrum by the *empirical IDS of a finite reference spectrum* (`searchsorted`-rank into a sorted reference of size N_ref, scaled by N_cell). The reference is itself a finite-N_ref staircase, so the unfolded statistic carries **two** discretization scales — N_cell and N_ref — and the Finding-2 (b) check proved the output is dominated by their **ratio** (W1δ ≈ f(N_cell/N_ref), substrate sub-dominant: ratio 0.236 → W1δ≈0.085 at two unrelated absolute scales; ref-N swung W1δ 200–4000× the inter-λ spread). This is what invalidated §Q3 (`U_NOT_REACHED`/`STABLE_LIMITING_LAW_NOT_ESTABLISHED` retracted; Finding 2 phantom; the U-curve = the harness function) and downgraded the certified zoo-gap *label* to not-ratio-clean. Context/retraction logs: `phase35a/Q3_HALT_FINDINGS.md` ((b)-cascade + post-(b) sections), `PHASE35A_BRIEF.md` post-(b) amendment, memory `phase35_am_arc_design`. **Prior art in-repo, ratio-free already:** `unfold_arcsine` (analytic IDS, no reference) and the raw-point-process path (Poisson calibrator, no unfolding) — both have *one* scale, not two. The redesign brings IDS-unfolding into that family.

## §2 Goal

The redesigned IDS-unfold leg's unfolded statistic reflects the **substrate**, not the cell-N/ref-N ratio — i.e. it has no second (reference) discretization scale.

## §3 Scope

**IN:** the IDS-unfold leg itself and its validation (§5), kept **drop-in** for the existing classifier/zoo interface (same call signature → unfolded unit-mean positions; `joint_q_profile`/`joint_quadrant_diagnostic`, `var(s)`, W1δ unchanged downstream).
**OUT (load-bearing):** re-running §Q3; re-validating the zoo gap; §3 (analytic or empirical); 35b — **all stay parked at their logged checkpoints.** This brief fixes the instrument; it does not resume the arc, re-open a retraction, or touch Class II (still fully blocked). The §3-*analytic* track remains independent of and parallel to this redesign (deriving (A)/(B) needs no instrument); only §3's *empirical* half and the zoo-gap re-validation are downstream of this leg.

## §4 Design decision — the call

**Decision: (b) — remove the reference-N. Build the IDS-unfold leg on a reference-free, per-energy IDS: the transfer-matrix rotation number (Prüfer-phase winding) of the AM cocycle, with gap-labelling (IDS ∈ ℤ+θℤ on gaps) as exact anchors.** (a) is rejected. Reasoning:

- **(a) manage the ratio — rejected, two ways.** *Hold the ratio fixed across the sweep:* removes only the *trend* artifact (a constant f(ratio) pedestal remains), so absolute comparisons against the ratio-free calibrators — exactly what the zoo-gap BR_artifact verdict requires — stay apples-to-oranges. *Scale N_ref = c·N_cell, c large:* the principled limit (ratio→0 recovers the true IDS), but O((c·N_cell)²) eigensolves are cost-prohibitive precisely where the substrate signal lives (the divergent branch needed N_cell ≳ 10⁵; calibration: N=2.5×10⁵ already ≈ 450 s, O(N²)). (a) *manages* the failure mode; it does not *remove* it, and is infeasible at the N that matters.
- **(b) remove the reference-N — chosen.** The IDS of a 1-D ergodic Schrödinger operator is the **rotation number of its transfer-matrix cocycle**, a *per-energy* convergent quantity (Prüfer-angle winding / sign-count of the iterated cocycle). It has **no reference spectrum and no N_ref** — its only error parameter is the iteration length **L_iter**, which is **decoupled from N_cell** (fixed large constant, chosen for rotation-number convergence, *independent of the cell*). Unfold each cell eigenvalue E by N(E) so computed: zero second discretization scale ⇒ **ratio-free by construction**. This is not a new family — it is the *generalisation of the in-repo prior art*: `unfold_arcsine` is exactly this rotation-number IDS in closed form for the λ=0 free cocycle. (b) brings IDS-unfolding into the same ratio-free family `unfold_arcsine` already lives in.
- **Band-interior wrinkle — stated treatment.** Gap-labelling gives the IDS *exactly* on every gap (N(E) ∈ ℤ+θℤ; for rational θ=p/q exactly (1/q)ℤ). For AM the gaps are *dense*, so the IDS is pinned to exact analytic values on a dense set; the rotation-number computation fills the (Hölder, non-elementary) band-interior *between* those exact pins. So the treatment is: **rotation-number interior + gap-labelling-exact pinning at every gap**, a reference-free IDS with dense exact anchors. **Honest caveat (a §5 gate, not an assumption):** L_iter for rotation-number convergence is regime-dependent — slow near critical coupling (small Lyapunov/critical regime); §5 must *verify* L_iter-convergence per regime (L_iter-doubling), never assume a fixed L_iter. The convergence is substrate-intrinsic (an L_iter limit), categorically unlike a cell-N/ref-N ratio. If L_iter-convergence proves intractable in some regime, that regime is honestly out-of-envelope (a bounded, stated limit), not a silent ratio artifact.

## §5 How we'll know it worked

The routine once-over for the rebuilt leg — read every statistic against its own empirical noise floor (§7.ter.59 discipline), asymmetric labels:

- **Ratio-invariance gate (the decisive new one — directly targets the §Q3 artifact).** Fix the substrate (fixed (λ, N_cell) AM cell); sweep the *reference treatment* (for (b): L_iter over ≥2 decades). **Pass:** the unfolded W1δ/var is *stable* — converges in L_iter, with cross-L_iter swing ≤ the φ-ensemble sampling-noise SE. Explicitly contrast against the **old** leg on the *same* substrate (ref-N swung W1δ 200–4000× the spread): the redesigned-leg swing must collapse to ≤ ~1× the spread — i.e. the §Q3 artifact is *gone*, demonstrated, not assumed. Also re-derive, on the redesigned leg, the certified-grid sub-vs-super contrast (≈0.04 vs ≈0.26) — it must persist (it is the ratio-immune substrate fact; the redesign must not erase it).
- **Known-truth gates (reused; must still pass under the redesigned leg).**
  - *Exact clock* (λ=0): the rotation-number IDS must reduce to the closed-form **arcsine to machine precision** → var(s)≈0. (Doubles as the (b)≡`unfold_arcsine`-at-λ=0 consistency anchor.)
  - *Synthetic Poisson:* the raw-point-process path is untouched; confirm the redesigned leg, applied to a spectrum with a known IDS, returns the expected NNS (no leg-induced distortion of a known-Poisson input) at the Poisson floor.
  - *Rational-θ periodic approximant θ=p/q:* IDS plateaus must land **exactly at k/q** (the exact rational gap-labelling values) — now a *reference-free* known-truth check, so it simultaneously certifies the band-interior method and ratio-freeness on a fully-known case.
  - *Gap-labelling consistency (λ≠0):* on AM gaps the computed N(E) ∈ ℤ+θℤ within tolerance — the dense exact anchor for the band-interior method.
  - *L_iter-convergence gate (per regime):* L_iter-doubling → N(E) stable within tolerance, verified across the (λ) range, not assumed.
- **Verdict vocabulary (asymmetric):** `IDS_LEG_RATIO_FREE_VALIDATED` (all gates pass, ratio-invariance demonstrated) / `_PARTIAL` (ratio-free but a regime fails L_iter-convergence — bounded out-of-envelope, stated) / `IDS_LEG_REDESIGN_INTRACTABLE_HALT` (band-interior not reference-free-computable within the envelope). Never a discovery/measurement verdict.

## §6 Brocot glance

**Brocot is clean.** Quick look (not an audit): "Brocot" in-repo = `stern_brocot_depth(p,q)` (`intermittency.py:256`) — a pure integer tree-depth recursion on locking/Farey rationals, consumed by the lock-depth histograms (`run_zeta_phase2.py`, `run_controls.py`) and Engine-5's Stern-Brocot directional split (`arithmetic_toolkit.py:516`); the synth's LUT/vector tables are Farey rational enumerations (`farey_rationals`, `pll_bank`). This path is entirely in the **integer-rational domain** — no eigenvalue spectrum, no IDS, no reference, **no cell-N/ref-N ratio anywhere**. Every `unfold_ids_ref` caller is a phase35a/`fix_gue` *spectral* path; none touch the Stern-Brocot/Farey tables. The §Q3 reference artifact **cannot** have propagated into the synth's LUT/vector-table entries; Brocot inherits nothing here.

## §7 House notes

- **Asymmetric labels:** the redesigned leg is *validated* (`IDS_LEG_RATIO_FREE_VALIDATED`), never framed as a discovery/measurement.
- **Amend-don't-rewrite:** the §Q3/zoo retraction logs stay as-is; this brief is additive (a new file), pointed to from `phase35_am_arc_design` + `PHASE35A_PRECOMPUTE_REVIEW.md`, not a rewrite of them.
- **Commit the filled brief** so there is a thing to point at (this file, brief-and-hold).
- Brief-and-hold: filling/committing this brief authorises **nothing** to build or run; the redesign build, like §3, awaits an explicit go (Will's). The §3-analytic track remains parallel and independent; only §3-empirical and zoo-gap re-validation are gated on this leg being `RATIO_FREE_VALIDATED`.

---

End of brief — **IDS-unfold leg redesign: call made (b), reference-free rotation-number/Prüfer IDS with gap-labelling-exact anchors; (a) rejected (mitigation-only / cost-prohibitive). §5 = ratio-invariance gate + reused known-truth gates + L_iter-convergence gate, asymmetric labels. Brocot clean. Brief-and-hold; arc parked; build awaits explicit go.**
