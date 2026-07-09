# Post-Crystallization — Sub-gate 0 + Part B (crossover, gated)

Executed 2026-07-08 under the sealed Post-Crystallization plan. Raw: `partB_measured.json`.
Standing discipline: unfolding-free ⟨r̃⟩ but **insufficient alone** (0.50 confound);
shape + long-range required; theory-fixed density; Gate 0 before any crossover statistic;
measurement and interpretation in separate fields.

## Reference reconciliation (flagged in review)
Session K used **GOE ⟨r̃⟩ = 0.5359** (ABGR 3×3 surmise) throughout; there is no 0.5307
in the code — 0.5307 is the N→∞ asymptotic. The 0.005 gap is far below K's 7–8σ GOE
exclusion (unaffected). For Part B — where 0.50 (semi-Poisson) vs 0.53 (GOE) is the whole
game — references are **empirical, same-estimator, matched-n**, not surmise constants:
Poisson=iid Exp(1); semi-Poisson=iid Γ(2, 0.5) [P(s)=4s e^{−2s}]; GOE=real eigenvalues.

## Sub-gate 0 — small-spacing-loss artifact — **PASS**
The crux: semi-Poisson (⟨r̃⟩≈0.50) and artifact-contaminated Poisson (≈0.50) are the
**same number**; the mean cannot tell them apart. Gate 0 is the prerequisite.
- **Loss surrogate (calibration):** merging Poisson levels closer than δ inflates ⟨r̃⟩:
  δ=0→0.385, 0.05→0.418, 0.10→0.445, 0.20→0.488. So resolution loss *can* fake ~0.49.
- **Real-data certification:** the LMFDB `maass_rigor` spectrum has min raw spacing
  **2.7e-4** (close pairs fully resolved, no cutoff); unfolded spacings extend to ~0.003.
  → **No selective loss. Gate 0 PASS** (exact rigor data — the artifact family cannot apply).

## Part B — is there a genuine intermediate class at r*≈45?
Windows on the odd (sym1) sector, where the crossover is strongest.

| window | n | ⟨r̃⟩ | small_frac<0.2 | β (Poisson~0, GOE~0.8) |
|---|---|---|---|---|
| **low-r r<45** | 57 | **0.523** (95%CI [0.447,0.596]) | 0.218 (CI [0.11,0.33]) | +0.04 (CI [−0.30,0.54]) |
| trans 35–55 | 61 | 0.490 | 0.220 | — |
| **high-r r>55** | 242 | **0.406** | 0.321 (≈Poisson 0.337) | +0.03 |

refs @ n=57: Poisson 0.384 / semiP 0.498 / GOE 0.533; small_frac 0.337 / 0.148 / 0.111.

**Two robust facts + one irreducible limit:**
1. **Low-r rigidity is REAL and Gate-0-clean.** The mean 95% CI [0.447, 0.596] **excludes
   Poisson** (0.386) — the elevation is not an artifact and not noise; consistent with
   semi-Poisson *or* GOE.
2. **But the class is unresolvable at the irreducible n≈57.** The shape discriminants that
   would pick semi-Poisson vs GOE vs contaminated-Poisson — β (CI [−0.30, 0.54]) and
   small_frac (CI [0.11, 0.33]) — **both span the entire Poisson→GOE range**. Only ~57 odd
   Maass forms *exist* below r=45; this n cannot be increased. The pre-registered
   "genuine intermediate class" bar (Gate0 **and** linear repulsion **and** semi-Poisson
   long-range) is **not met** → **do not promote.** The long-range leg is doubly blocked
   (n too small at low-r; Σ² unfolding-fragile — high-r Σ² came out flat 0.63→0.72, a known
   artifact, so Σ² is not load-bearing and the high-r Poisson call rests on the robust
   short-range trio).
3. **High-r (r>55) is cleanly Poisson** (mean 0.406, small_frac ≈ Poisson).

**Verdict (banked):** arithmetic-Poisson is Poisson wherever the statistics allow (high-r,
well-powered). The finite-r crossover harbors **real, Gate-0-clean elevated rigidity** whose
**exact class is statistics-limited** by the finite number of low-r Maass forms — *not*
substrate-ambiguous, *not* an artifact, *not* a confirmed intermediate class. **The
confoundable mean (0.52, GOE-looking) was correctly NOT promoted to a class** — the plan's
discipline held; the null on "confirmed intermediate class" is banked as a real result.

**Interpretation (separate field, not promoted):** the low-r elevated rigidity is most
naturally the finite-r generic-BGS repulsion, superseded by arithmetic degeneracy (the
Run-3 exponential length-multiplicity) as r grows — but the specific class is beyond this
spectrum's reach.

## What would move it (queued, not tonight)
Resolving semi-Poisson-vs-GOE at low r is **impossible with more of the same substrate**
(the low-r forms are exhausted). It requires either a different arithmetic surface with a
denser low-r spectrum, or the n=5 non-arithmetic contrast (whose low-r regime, if GOE,
would show whether the modular low-r repulsion is arithmetic-specific). Both are the
deliberate downstream arcs.
