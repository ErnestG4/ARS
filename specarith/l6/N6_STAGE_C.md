# n = 6, stage (c): results as they come (method: `N6_STAGE_C_BOUND.md`)

## Steps 1–2: the n = 6 construction and its U(N) pointwise gate (`cs4/ratios_t6.py`; spot)
- The construction is `ratios_t5.Model` at n = 6. It is general in n, so no new transcription was needed.
- **Gate result: FAIL** (`cs4/results/n6c/UGATE6.json`), with tolerance 10⁻¹² + 10⁻⁶·|det|, pointwise:

  | N | configurations (8 each) | max relative difference | max absolute difference | result |
  |---|---|---|---|---|
  | 10 | spread over [0, 6) | 1.0·10⁻⁷ | 1.4·10⁻¹² | pass |
  | 10 | one pair 10⁻³ apart | 9.6 | 6.5·10⁻¹⁰ | **fail** |
  | 50 | spread over [0, 6) | 3.3·10⁻⁷ | 2.5·10⁻¹² | pass |
  | 50 | one pair 10⁻³ apart | 1.7·10⁹ | 3.4·10⁻⁸ | **fail** |
  | 50 | 3 + 3 at r = 5 | 1.9·10⁻⁷ | 3.1·10⁻¹² | pass |
  | 50 | 3 + 3 at r = 9 | 2.1·10⁻⁸ | 2.0·10⁻¹⁴ | pass |

- **The failure is near coincidence.** With a pair 10⁻³ apart, ρ₆ falls to 10⁻⁶–10⁻¹⁸, which is ∝ d², and the
  construction carries an absolute error of up to 3·10⁻⁸ there. That comes from cancellation between z-factors
  1/(1 − e^{−x}) at x ~ 10⁻³. Away from coincidence, the relative accuracy is 2·10⁻⁸–3·10⁻⁷.
- **By the committed rule, no ζ value is read** (no bound, no G-b3) until Will rules.
- **Relevance (for that ruling, not a ruling):** the quadratures that would use the construction never come near
  coincidence. Distinct Gauss–Legendre nodes, 6 per 4-unit window, are at least 0.54 apart, and the clusters are
  ≥ 20 apart in G-b1 and G-b3. An amended gate would test near-coincidence at the quadrature's minimum separation, or
  evaluate near-coincident configurations in mpmath. **That is Will's call.**

## Large-N diagnostic (not a gate; `cs4/results/n6c/LARGEN.json`)
The construction against the determinant in the 3 + 3 geometry (4 configurations each), max relative difference:

| N | r = 20 | r = 100 | r = 1000 |
|---|---|---|---|
| 10³ | 8.8·10⁻¹¹ | 7.4·10⁻¹⁴ | (r > N/2) |
| 10⁴ | 7.9·10⁻⁸ | 1.6·10⁻¹⁰ | 2.3·10⁻³ (a configuration with det 2.8·10⁻⁸) |
| 10⁵ | 1.8·10⁻¹¹ | 2.3·10⁻¹² | 7.1·10⁻¹² |

**At N = 10⁵ the construction is accurate to about 10⁻¹¹ out to r = 1000,** so G-b1 can use stage (a)'s N directly.

## Round 76: post-hoc construction change (committed before the re-run)
**What changed.** This is a construction fix, not a gate amendment (round 76).
- **Threshold, declared now:** DELTA_TH = 0.1 unit spacings. A configuration whose smallest pairwise separation is
  below it is evaluated in mpmath (`cs4/ratios_hp.py`, mp.dps = 40). That is the same construction term for term:
  the same (S, T) enumeration, phase-filter option, θ grids and prime groups.
- At or above the threshold it is evaluated in double by `ratios_t5.Model`, unchanged. `ratios_t6.rho_auto`
  dispatches between the two.
- **Guard:** `ratios_t6.guard` raises if any configuration below DELTA_TH reaches a double evaluation.
- **This is a post-hoc construction change,** made after the committed gate failed on near-coincident pairs
  (f73f3895). The gate itself is unchanged.

**Checks, declared before running.**
1. **Path agreement at the threshold** (`ratios_t6.py threshold`): U(N) at N = 10 and 50, 4 configurations each, with
   smallest separation exactly 0.1. The two paths must agree to 10⁻¹² + 10⁻⁷·|hp|, ten times tighter than the gate.
2. **The committed U(N) pointwise gate, re-run unchanged:** the same seed, the same 48 configurations including the
   16 with a pair 10⁻³ apart, and the same tolerance 10⁻¹² + 10⁻⁶·|det|. It is evaluated through rho_auto, which
   sends 29 of the configurations below 0.1 to the mpmath path. **It must pass.**

**Local smoke tests (not gates).**
- **U(N) N = 10, n = 6:** the mpmath path gives 0.65762858171708360, against det 0.6576285817170834 and double
  0.6576285817170845. It takes 50 s per configuration.
- **ζ at PMAX 30:** mpmath and double agree to 1–3·10⁻¹⁶ at n = 2, 3 and 4, at separations ≥ 0.5.

**Why the ζ path does not block (c) or G-b3.** No ζ evaluation in (c) or G-b3 falls below the threshold. Their
in-window Gauss–Legendre nodes are ≥ 0.54 apart, and the guard would raise if one did. The ζ mpmath path exists, and
its threshold agreement can be run on request.

**Results after the construction change (spot):**
- **Path agreement at the threshold: PASS** (`cs4/results/n6c/THRESHOLD.json`). Double against mpmath at a smallest
  separation of exactly 0.1: max absolute difference 7.3·10⁻¹⁵ (N = 10) and 5.0·10⁻¹⁵ (N = 50); relative ≤ 3.6·10⁻⁹.
- **The committed U(N) gate, re-run unchanged: PASS** (`cs4/results/n6c/UGATE6.json`; the failed first run is in
  `run1/`). 29 of the 48 configurations went through the mpmath path.

  | configurations | high-precision | max relative difference |
  |---|---|---|
  | N = 10, spread | 6 of 8 | 5.1·10⁻¹¹ |
  | N = 10, near-coincident | 8 of 8 | 1.5·10⁻⁸ |
  | N = 50, spread | 2 of 8 | 7.2·10⁻⁹ |
  | N = 50, near-coincident | 8 of 8 | 1.1·10⁻⁵ (absolute 5.7·10⁻¹⁷, at det down to 4·10⁻¹⁸) |
  | N = 50, 3 + 3 at r = 5 | 2 of 8 | 1.0·10⁻¹² |
  | N = 50, 3 + 3 at r = 9 | 3 of 8 | 2.8·10⁻¹² |

- **Per round 76, (c)'s bound and G-b3 may now proceed.** G-b3 is launched. (c) waits on Will's choice of node count,
  because the committed 4-node bound is expected to come back "not established" (cost update, round 76).

## Round 77: the bound, amended to 6 nodes plus an 8-node check (committed before running)
**Why it was amended.** The per-piece quadrature check (round 76) showed the committed 4-node bound underestimates the
(3, 3) piece by ~70%. Will approved 6 nodes plus an 8-node convergence check, about 130 core-h. The design below fixes
that budget, using the per-configuration costs measured in G-b3 (≈ 90 s at PMAX 10³ under load).

**The quantity.**
- The (3, 3) piece I₃₃(r) = ∫_{A³×B³}[ρ₆ − ρ₃ρ₃] is the only place ρ₆ enters C(r).
- It is computed **by phase class** k = −3…3, for ζ and for U(N) (N = 10⁵) at identical nodes:
  `n6b_extract.FilteredModel.rho_cls`. The classes sum to the full function within 8·10⁻¹⁶, and class 0 equals the
  filtered part exactly (local check).
- Arithmetic correction per class: Δg_k = g_k^ζ − g_k^U.
- **The envelope E(r) = Σ_k |Δg_k(r)|** bounds |ΔI₃₃| at every carrier phase, so the bound does not depend on where
  the sparse r grid falls relative to the carrier. That is the beat lesson applied: no class is assumed slow or
  dropped.

**Grid.**
- r ∈ {0.27, 1.17, 2.07, 3.46, 4, 6, 10, 20}. The small r are chosen so that the two windows' 6-node grids stay
  ≥ 0.22 apart, keeping the double path valid under the guard.
- r = 0 itself needs the mpmath path (the grids coincide) and is not evaluated. Its weight is one 1/8-grid point of
  160, covered by the max-envelope bound.

**Runs.**
- ζ at ℓ = 15.75: PMAX 10² and 3·10², all 8 r.
- ζ at ℓ = 21.75: PMAX 10², all 8 r.
- ζ at ℓ = 15.75: PMAX 10³ at r = 2.07 and 10 (the cutoff trend).
- U(N): all 8 r.
- **8-node check:** ζ (ℓ = 15.75, PMAX 10²) and U(N), at r = 6.

That is 1,242 tasks of 16 configurations each, about 115 core-h, checkpointed per task.

**The bound and its reading.**
- **B₆ = 2·max(1, E₈/E₆)·40·max_r E(r)** in κ₃ units:
  - 40 ≈ Δ·(1 + 2·159), the Bartlett sum over r < 20 at weight ≤ 1;
  - 2 is the safety factor;
  - E₈/E₆ is the 8-node over the 6-node envelope at r = 6.
- **Established** iff 0.5 ≤ E₈/E₆ ≤ 2 and the cutoff change |E(10³) − E(3·10²)| ≤ 30%·E(3·10²) at both trend r.
  Otherwise the bound is "not established".
- **Negligible** iff established and B₆ ≤ 0.01·R(G)·W_CUE at every G. That is a third of the ~3% test resolution on R,
  with R = 0.315, 0.209, 0.183, 0.157 and W_CUE = 0.2111. The strictest threshold is 3.3·10⁻⁴ at G = 10⁴.
- If negligible, the term is carried as a bounded systematic, ±B₆. Otherwise it goes to Will.

Code: `cs4/n6c_bound.py`. Launcher: `cs4/run_n6c_bound_spot.sh`.

## Round 77 bound: result (spot, 2026-10-23; all 1,242 tasks, summary under its own status 0)
Files: `cs4/results/n6c/bound/N6C_BOUND.json`, `summary.log`, `CLASSES.txt` (per-class sums), `tasks.tgz` (per-task
records), `jobs.txt`.

**Verdict by the declared rule: NOT ESTABLISHED.** Not negligible, so per the method it goes to Will.

| criterion (declared) | value | required | |
|---|---|---|---|
| 8-node vs 6-node envelope at r = 6, E₈/E₆ | 2.58 / 21.0 = **0.123** | 0.5–2 | **fails** |
| cutoff change 3·10² → 10³, r = 2.07 | 0.27% | ≤ 30% | passes |
| cutoff change 3·10² → 10³, r = 10 | 0.005% | ≤ 30% | passes |
| B₆ = 2·max(1, E₈/E₆)·40·max E | 4.4·10³ (κ₃ units) | ≤ 3.3·10⁻⁴ (G = 10⁴) | (not read: not established) |

Envelope E(r) = Σ_k |Δg_k(r)|, 6 nodes:

| ζ case | 0.27 | 1.17 | 2.07 | 3.46 | 4 | 6 | 10 | 20 |
|---|---|---|---|---|---|---|---|---|
| ℓ = 15.75, PMAX 10² | 17.2 | 14.7 | 31.0 | 32.4 | 19.2 | 21.0 | 46.8 | 54.8 |
| ℓ = 15.75, PMAX 3·10² | 17.5 | 15.0 | 31.0 | 32.4 | 19.2 | 21.1 | 46.8 | 54.7 |
| ℓ = 21.75, PMAX 10² | 24.5 | 12.7 | 23.5 | 19.0 | 10.1 | 9.6 | 8.3 | 19.3 |

Total (all classes) ζ − U difference of the (3, 3) piece, ΔI₃₃ (descriptive): at ℓ = 15.75, PMAX 10², it is −10.4,
−13.2, −13.3, −6.7, −4.5, −16.3, −10.2 and +10.9 over the r grid. At r = 6 with 8 nodes it is **−0.25** (6 nodes:
−16.3). The individual pieces are large: the U(N) (3, 3) piece is −767 at r = 0.27 and −1.18 at r = 20.

**Diagnosis (post-hoc; descriptive).** Two separate defects. Either one alone makes the bound unusable.
1. **Quadrature.** Six nodes do not resolve the ζ − U difference.
   - At r = 6, going from 6 to 8 nodes moves the U(N) piece from −18.5 to −22.8 (−19%, in line with the cost update's
     −26%) and the ζ piece from −34.8 to −23.0. Their difference falls 65-fold, from −16.3 to −0.25.
   - The arithmetic difference is a small residue of two large, under-resolved integrals. Most of the 6-node error sits
     in classes ±1.
   - Whether 8 nodes resolve it is unknown: there was no 10-node check.
2. **The quantity (my error in the round-77 amendment).** The committed method (`N6_STAGE_C_BOUND.md`) defines ΔC₆ as
   the part coming **only from the arithmetic part of ρ₆**: the 3 + 3 cross-connected term. "Everything through ρ₅ ...
   is not part of this bound."
   - The amendment bounded the full (3, 3) piece, ρ₆ − ρ₃ρ₃, instead.
   - That difference also contains products of lower cross-connected functions: for example a cross pair's connected
     ρ₂ times in-cluster densities, or the 2 + 2 cross-connected ρ₄ times ρ₁ρ₁. Their arithmetic parts are of order
     ρ₅ and below.
   - In C(r) those products are weighted by ψ's coefficients and cancel against the (2, 3), (3, 2), (2, 2), … pieces.
   - So ΔI₃₃ is not ΔC₆. It overstates ΔC₆ by an amount that is O(1) per r.
   - **Plausibility (not a verification):** even the 8-node ΔI₃₃ at r = 6 (−0.25) would give a ΔW of order 10 if it
     were a correction to W, against W_CUE = 0.21 and a total arithmetic change in W of about −0.15. So most of it must
     cancel against the lower pieces.

**What a usable bound needs (for Will; nothing runs):**
- **(i) The declared quantity.** Either ρ₆ᶜ, the fully cross-connected part (the cluster expansion with every lower
  cross-connected product removed), or equivalently the full ΔC(r) over all (a, b) ≤ 3 pieces minus its through-ρ₅
  part. Both are evaluated at identical nodes for ζ and U(N). The lower ρ's are cheap next to ρ₆.
- **(ii) Nodes: 8 per coordinate, with a 10-node check.**
  - The measured cost here is about 21 core-s per 6-point configuration.
  - 8 nodes give 56² = 3,136 configurations per (case, r), so the same case list costs about 600 core-h.
  - A 10-node check at one r for ζ and U(N) costs about 170 core-h.
  - Total about 800 core-h. This is a rough estimate, scaled from this run.
- **Not affected:** the cutoff trend is flat (≤ 0.3% from 3·10² to 10³; ≤ 3% from 10² to 3·10²), so the low-cutoff
  premise of (c) holds.
- **Height dependence:** at r ≥ 6, ℓ = 21.75 gives envelopes 3–6 times smaller than ℓ = 15.75.

## Round 78: the bound redefined to the connected 6-point term; witnesses; pilot (committed before running)
**Record of the error.** The round-77 amendment bounded the whole (3, 3) piece, ρ₆ − ρ₃ρ₃, by mistake. The committed
method (`N6_STAGE_C_BOUND.md`) declared the arithmetic part of ρ₆ only, with everything through ρ₅ out of scope. The
round-77 numbers above therefore bound the wrong quantity, as well as being unconverged.

**The bounded quantity (round 78).**
- **T₆** is the fully connected (Ursell) 6-point function. It is obtained from ρ_m on all 63 nonempty subsets of the
  3 + 3 points by Möbius inversion over the 203 set partitions:
  T₆ = Σ_π (−1)^{|π|−1}(|π| − 1)!·Π_{b∈π} ρ_{|b|}(x_b).
- **Every other term of ρ₆ is a product of T_m with m ≤ 5,** i.e. through ρ₅. Those stay out of scope, as declared
  originally.
- **T₆ enters C(r) only through the (3, 3) piece,** with coefficient c₃c₃ = 1. So ΔC₆(r) = ∫_{A³×B³}(T₆^ζ − T₆^U),
  ordered over the in-window Gauss–Legendre nodes (distinct sorted tuples × 3!²).
- **Phase classes and the envelope:**
  - Each subset's ρ_m is split by class with `FilteredModel.rho_cls`. Phases multiply, so the classes of a product add.
  - The envelope E(r) = Σ_k |ΔT₆,k(r)| keeps round 77's phase-robust bound.
- **Code:** `cs4/n6c_conn.py`.
- **Local self-test (not a gate):**
  - The Möbius sum on determinant ρ's matches the determinantal cycle formula T₆ = −Σ_{6-cycles} Π K to 1.7·10⁻¹⁴.
  - The class-resolved Möbius sum matches the plain one to 1.1·10⁻¹⁴.
  - On one U(N) chunk, the class sum of the construction's T₆ matches the determinant's to about 10⁻¹².

**Witnesses (declared before running).**
1. **U(N)-for-ζ null, at 8 and 10 nodes.** U(N) (N = 10⁵) takes ζ's place through an independent route: the exact
   determinant det[K(x_i, x_j)] for every subset. The U slot is the ratios construction, exactly as in the real
   comparison.
   - **PASS** iff |∫(T₆^det − T₆^constr)| ≤ 4·10⁻⁷ at each node count. That is 10% of the per-r allowance:
     4.1·10⁻⁶ = 3.3·10⁻⁴/(2·40).
   - **Why not the same code twice:** that would be zero bit for bit and could not fire.
   - **The null compares class sums,** because the determinant has no class split.
   - **It must be able to fire.** A planted arithmetic part, ρ₆ of the determinant slot × (1 + 10⁻⁸), goes through the
     same Möbius sum. It gives about 7·10⁻⁶, near the per-r allowance.
   - The null passes only if the planted case exceeds the tolerance AND its measured size (planted minus unplanted)
     matches 10⁻⁸·∫ρ₆^det within 10%.
2. **Convergence, 8 against 10 nodes** (ζ ℓ = 15.75, PMAX 10², r = 6). Both the envelope E and the class-summed ΔI must
   satisfy |X₈ − X₁₀| ≤ 0.2·|X₁₀| + 4·10⁻⁷. The 0.2 sits inside the bound's safety factor of 2. The absolute term is the
   null tolerance.

**Pilot (round 78: "one or two r values (r = 6 included) at 8 and 10 nodes on ζ, plus the null").**
- **Runs:** r = 6 only, ζ (ℓ = 15.75, PMAX 10²) and U(N) (construction plus determinant), at 8 and 10 nodes.
- **Size:** 3,136 + 14,400 configurations per model, 2,192 tasks of 16.
- **Cost:** measured locally at 440 s per ζ chunk and 190 s per U chunk, so about 190 core-h. That is about 11 h on
  spot at 28 processes.
- **Why one r:** a second r would double the cost. The 10-node grid is the expensive part, and r = 6 is the declared
  check point.
- **Reading:** FULL_RUN_ALLOWED iff the pilot CONVERGES and the null PASSES (with its witness). It is reported to Will
  either way.
- **The full computation does not start without Will.** Its size, scaled from the measured costs: 8 nodes on round
  77's case list, ζ at 26 (case, r) and U(N) at 8 r, about 700 core-h. The 10-node check is already in the pilot.
  - Before then, the 8-node grids at r < 4 must be checked for separation ≥ 0.1. The round-77 grid was chosen for 6
    nodes.
- **Descriptive only:** `B6_from_r6_only` = 2·40·E₁₀(6) is reported, and it is not a bound.

Code: `cs4/n6c_conn.py`. Launcher: `cs4/run_n6c_pilot_spot.sh`. Outputs: `cs4/results/n6c/pilot/`.

### Round 78 pilot: quadrature-rule defect, found ~8 min after launch; stopped; corrected before any result
- **The defect.** The pilot as committed (56ef7961) integrated T₆ with the distinct-node rule inherited from round 77
  (`E._tuples`: distinct sorted node tuples × 3!). That rule equals the product Gauss–Legendre rule only for integrands
  that vanish at in-cluster coincidence.
  - ρ_m and ρ₆ − ρ₃ρ₃ vanish there. That is why rounds 76–77, G-b3 and the algebra check are unaffected.
  - T₆ does not vanish there: for the sine process, T₂(x, x) = −1.
- **Measured** (U(N), determinants, r = 6; `cs4/n6c_conn.py quadtest` and a local check):
  - The distinct-node rule gives +1.5·10⁻³, −2.4·10⁻³, −7.5·10⁻³ and −5.4·10⁻³ at 6, 8, 10 and 12 nodes. It does not
    converge.
  - The product rule gives −0.04607, −0.09343, −0.095200 and −0.0952267 at 6, 8, 10 and 12 nodes; the 24-node reference
    is −0.0952268871.
  - At r = 20 the pattern is the same: the product rule gives −6.98046·10⁻³; the distinct rule gives −5·10⁻⁴.
- **Action.** The pilot was stopped by explicit PIDs after ~8 min (spot; no task file had been written). This
  correction was made before any result was read.
- **The correction (post-hoc quadrature change; the quantity, witnesses and criteria are unchanged).**
  - The product Gauss–Legendre rule, folded by symmetry onto sorted node multisets i ≤ j ≤ k with weight
    (3!/Π mult!)·Π w: 120 per cluster at 8 nodes and 220 at 10.
  - At a repeated node, every subset ρ containing both copies is set to exactly 0. Every other subset is evaluated at
    distinct points, through the guard.
  - **Basis:** ρ_m ∝ d² at coincidence for the ζ model too. On the mpmath path at ℓ = 15.75, PMAX 10², ρ₂ = 3.0230·10⁻⁴,
    3.0230·10⁻⁶ and 3.0230·10⁻⁸ at d = 10⁻², 10⁻³ and 10⁻⁴. ρ₃ behaves the same way.
- **Local checks (not gates):**
  - The folded rule with determinant ρ's equals the product-rule trace formula to ~10⁻¹¹ at 6, 8 and 10 nodes.
  - Construction against determinant on two 8-node U(N) chunks, one all-diagonal and one all-distinct: 2·10⁻¹⁶ and
    7.7·10⁻¹⁵.
  - The planted witness came back at 1.39487·10⁻⁹ against the expected 1.39487·10⁻⁹.
- **For the convergence reading:** for U(N), 8 against 10 nodes differ by 1.9% on ∫T₆ itself. The criterion is on the
  ζ − U difference.
- **New size and cost:** 14,400 (8 nodes) and 48,400 (10 nodes) configurations per model, 7,850 tasks of 16. The
  configurations with a repeated node cost ρ₅ or less, so the estimate is ~220 core-h, ~12–13 h on spot.
- **Relaunch 2 (performance only).** The chunk-16 relaunch was stopped after ~45 min (161 of 7,850 tasks; set aside
  as `pilot_run2_chunk16`).
  - **Why:** at 16 configurations per task, numpy overhead dominates. Measured locally per point: ζ (PMAX 10²) 15.8 s at
    batch 16 against 7.0 s at batch 128; U(N) 8.3 s at batch 16 against 0.39 s at batch 2048.
  - **Change:** chunks of 128 (ζ) and 512 (U), 616 tasks. Nothing else changes: quantity, rule, witnesses, criteria
    and sums.

### Round 78 pilot: result (2026-10-24; recorded in `N6_CLOSEOUT.md` §5)
- **NULL_PASSES:** residual 1.9·10⁻¹¹ (8 nodes) and 2.3·10⁻¹² (10 nodes); the planted witness fires and is recovered.
- **CONVERGES = false:** E 0.2204 / 0.1648 and ΔI −0.1994 / −0.1492 at 8 / 10 nodes. Class 0 agrees to 1.7%; the
  oscillating classes are under-resolved at 8 nodes.
- **FULL_RUN_ALLOWED = false.**
- **Size at r = 6:** ΔI ≈ −0.15, against U(N)'s own ∫T₆ of −0.095 (descriptive).
