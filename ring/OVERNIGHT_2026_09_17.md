# ring/ — overnight run, 2026-09-17 (01:23 → 02:35 compute; cadence held to 08:00)

Branch `worktree-ring-stage0`, **53 commits ahead of `main`, unpushed.**
Board 53/53 at every commit; `verify_seal_order.py` PASS on the final graph.
Every generator was sealed after its pre-registration and before its output;
every sealed prediction is scored as declared in `ring/verify_ring.py`
(rows R13–R15) and the brief carries the results next to the predictions.

## What ran and what was banked

| arm | commit | sealed prediction → score |
|---|---|---|
| **Stage 3b** recurrence (L4b, I1, I2, T1) | `c7bfea3` | L4b sealed-to-fail **confirmed** (rate level: IND_n reads *more* residual autocorrelation than the ring — model error, smooth in φ); **I1: continuous attractor retains the along-manifold kick (1.00, 3/3), input-driven IND_u restores it (0.00, 3/3)**; driven pinned ring retained 0.88 (sealed < 0.1: **FAIL** — drive ≫ pinning, re-posed trapped); I2 transverse kicks return in both (rate, not kind); T1: R = TV/net separates C_perm (3.3–5.3) from A/IND (1.00), C_ord reads 2.06 (**FAIL**: R − 1 ≈ noise-TV/net; pinned as R's false-negative channel). Traversal detector certified on its declared sets with that caveat printed. |
| **I1b** trapped negative + depinning curve | `e2c761c` | ε = 0.1: trapped (γ = 0) restores **0.019 PASS**; sliding (γ = 0.02) retains 0.72 PASS; depinning crossing in **(0.01, 0.02]**; monotone in γ **FAIL** (well-dependent restoring rate after the tilt); ε = 0.03 INAPPLICABLE at 300τ. |
| **Stage 4** sine circle map | `d52f5a4` | Rails all green: Denjoy |ρ₁₀⁴ − ρ₁₀⁵| ≤ 4.8e-5 for K < 1; 0/1 tongue within one grid step of K/2π; Farey coverage at K = 0 within 11%; multistability 0 for K ≤ 1, fires above; hysteresis D(K) = 0 everywhere (dead region holds; none at K > 1 either, admissible). Residence Ω-fraction monotone in K on [0,1] PASS. **Staircase test at tol 10⁻³ INAPPLICABLE AS POSED — rigid rotation (K = 0) passes it too (0.872): rival rule on my own sealed test.** |
| **Stage 4b** pinned ring's tongue predicted from the measured pinning landscape | `622ebb8` | **γ*_pred = 7.99e-3 vs γ*_meas = 8.25e-3 at ε = 0.1; 1.98e-3 vs 2.25e-3 at ε = 0.03 — both within one grid step (PASS, PASS)**; ε-scaling 0.248× (sealed 0.3 ± 25%, PASS); ε = 0 rail ρ = 1.0000; ρ monotone, → 0.98. The clause "γ*_pred in the I1b interval (0.01, 0.02]" **FAIL** — a retention-at-300τ crossing is not a tongue edge; I conflated two observables in one seal. |
| **I1c** ε = 0.03 at 3000τ | `af625c6` | Crossing straddles the 4b edge: γ = 0.001 restores (0.001), γ = 0.003 slides (2.0) — **PASS, the two observables agree about the edge**; R(0) = 0.368 **FAIL** (< 0.1): this well's λ_eff = 3.3e-4, 10× below the Stage 1 median — well-dependence quantified; retention > 1 above threshold recorded (R is a trapped-system statistic). |
| **M2b / M2c** staircase test re-posed | `594dc88` | tol 10⁻⁵: K = 1 covers 0.74, K = 0 covers 0.029 on the grid — separation PASS, but the K = 0 number is **exactly 29/1001: φ(1)+φ(7)+φ(11)+φ(13) points of j/1001 are Farey fractions** (a rational grid is itself a Farey object — B-grid rail). With random Ω: K = 0 0.0130 vs Farey 0.0155 (−16%), K = 1 0.736 — **M2c PASS; the staircase test now discriminates against its rival.** |

**Doctrines banked (`8591ff5`):** the rail class **boundary-supported signal**
(B-sup: sup at an excluded edge; B-avg: average hides isolated-boundary
signal; now B-grid: rational grid vs rational target set); *the integer never
errs, it becomes undefined* as the sharper form of topological protection;
*a library's graceful-degradation path is a null-laundering channel unless
opt-in with its own detector spec*.

## The night's findings, in one paragraph each

**The dynamical rung is reachable by intervention and not by observation.**
An along-manifold kick separates a continuous attractor (retains, 1.00), a
trapped discrete attractor (restores, 0.02), and an input-driven look-alike
(restores, 0.00) in kind; every deviation-from-manifold statistic tried
(L4, L4b) fails even at the rate level. On this substrate, "attractor" is an
interventional predicate.

**Drive vs pinning is one competition seen by four instruments.** Stage 1's
contour (median pinning velocity c·ε), I1b/I1c's retention crossing, Stage
4b's ρ-tongue edge (maximal pinning velocity, max/median 3.02 in-table; 2.75 against the contour's c·ε), and the
circle map's Ω_c = K/2π. The reduced phase model predicts the full ring's
depinning to 3% from a quantity measured at γ = 0, at two ε.

**Restoring rates are well-dependent by up to 10×.** The median λ₁ is not the
well; any per-well statement needs the well identified. Two sealed
monotonicity/threshold clauses failed on this and both are recorded, not
re-scoped.

## Decisions queued for Will (none taken overnight)

1. **Does intervention-only certification count for the `implies` rung?**
   Register `attractor_by_along_manifold_memory` (simulation/experiment;
   negative set: IND_u, trapped pinned ring) and bank "possibly unreachable
   observationally" as a finding — or fold I1 into `implies` with the
   intervention requirement in `fires_on`.
2. **The QUEUED ring→ARS arm under (b) is vacuous for this generator.** The
   ring's spikes are inhomogeneous Poisson from the rate envelope, so a
   matched-Cox control with the same envelope is *identical in distribution*
   to the ring unit's train: the per-cell margin is zero by construction.
   Running it would be non-evidence scored as a verdict (#19). It needs a
   spiking ring (spikes feeding back into the dynamics). Not run.
3. **Noise-corrected R for T1** (R − 1 ≈ noise-TV/net; a MAD-based jump
   count would flag C_ord as stepwise — which it is — so the traversal
   predicate may need "monotone winding" as a second clause).
4. **N = 256 for the Sγ exponent** — left provisional per your call.
5. **Zigzag (Dionysus 2.2.3 wheel) for the time-varying E clouds** — declared,
   not installed overnight.
6. **Push** the branch; clear the untracked v4 doc and `Zone.Identifier` in
   your checkout's `criticality_tool/ring/`.

## Instrument notes for the next session

- `stage4b_ringtongue.py` used an einsum-batched integration (689 s); two
  BLAS matmuls do it in ~30 s. Not re-run; the numbers stand.
- I1/I1b/I1c retention is a trapped-system statistic; above threshold it
  wanders and can exceed 1.
- Every rational parameter grid is suspect against a rational target set
  (B-grid). Random draws or an irrational-offset grid, declared.

---
Cadence closed 07:42 PDT, board 53/53, 14 board-check wakes 02:54–07:42 all green.

## Post-read resolutions (2026-09-17 → 2026-09-20)

*The counts above ("53 commits", "board 53/53", "unpushed") were as of the
morning close; the branch was merged by Will into `derivflow-modes` and
pushed 2026-09-17.*

1. **Resolved (Will, 09-17): separate detector.** `attractor_by_along_manifold_memory`
   registered as an intervention-class detector (R16); the observational
   `implies` rung stays DECLARED. Stage 3e then found the MSD growth law
   separates in kind, so "unreachable observationally" was **not** banked.
2. **Resolved (Will, 09-17): the ARS arm is BLOCKED ON A SPIKING RING**, not
   option (b). Plan QUEUED entry re-filed.
3. **Ran as T2 → T3.** MAD jump count + monotone winding; T2 failed on the
   statistic (uncentered MAD under drift), T3 separated qualitatively and
   failed its numbers (kernel support 4σ). Ordering pinned (R13d), thresholds
   deferred to a negative-set calibration — Will's call, not a fourth seal.
4. **Stands provisional** (Will).
5. **Installed 09-17** (Dionysus 2.2.3, zigzag present); unused so far.
6. **Done** (merge + push by Will; v4 doc and Zone.Identifier cleared).

Also since: **Stage 3e** (MSD) ran — and its "anharmonic well" explanation
of the trapped clauses' common factor was **retracted 2026-09-20 as S5**
after Stage 3h swept the MSD well itself (harmonic to 0.1 rad). The cause of
λ_eff/λ₁ = 0.19–0.35 is open. **Stage 5 is next.**
