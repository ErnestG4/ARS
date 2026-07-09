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
  δ=0→0.385, 0.0075→0.389, 0.02→0.401, 0.05→0.420, 0.10→0.446, 0.20→0.489.
- **PASS by measurement, not absence-of-evidence:** min raw spacing **2.7e-4** vs local mean
  spacing ~0.08–0.27 at r~40 ⇒ resolution floor bounded at **floor/⟨s⟩ ≈ 1e-3–3e-3** (min
  *unfolded* spacing 0.0075). Fed back through the surrogate, δ≈0.0075 gives ⟨r̃⟩=0.389 —
  **indistinguishable from the δ=0 null (0.385)**. So the measured floor sits *quantitatively*
  inside the region where the artifact is provably null: the selective-small-spacing-loss (b)
  direction is closed **by measurement**, the version that survives a hostile reader.

## Part B — is there a genuine intermediate class at r*≈45?
Windows on the odd (sym1) sector, where the crossover is strongest.

| window | n | ⟨r̃⟩ | small_frac<0.2 | β (Poisson~0, GOE~0.8) |
|---|---|---|---|---|
| **low-r r<45** | 57 | **0.523** (95%CI [0.447,0.596]) | 0.218 (CI [0.11,0.33]) | +0.04 (CI [−0.30,0.54]) |
| trans 35–55 | 61 | 0.490 | 0.220 | — |
| **high-r r>55** | 242 | **0.406** | 0.321 (≈Poisson 0.337) | +0.03 |

refs @ n=57: Poisson 0.384 / semiP 0.498 / GOE 0.533; small_frac 0.337 / 0.148 / 0.111.

**One marginal fact + one irreducible limit + one clean fact:**
1. **Low-r elevation is MARGINAL, not robust — and the exclusion is reference-to-reference,
   not CI-vs-point.** The matched-n=57 Poisson reference is *not* the point 0.386 with zero
   width; it is 0.388 ± 0.043 (sampling se at n=57), 95% upper tail **0.474**. The real low-r
   window is 0.523, bootstrap 95% lower **0.448** — so the two 95% intervals **marginally
   overlap**. The elevation over the Poisson null is **z ≈ 2.3σ reference-to-reference**
   (≈3.1σ observed-vs-null): real-but-marginal, *suggestive not robust*. (An earlier draft
   said "robustly excludes Poisson (0.386)" by comparing the real CI to the Poisson *point* —
   that CI-vs-point compression hid the finite-n confound this whole arc exists to refuse; it
   is corrected here.) Gate 0 rules out an artifact, so the marginal elevation is not a loss
   artifact — but at ~2.3σ its very existence is only suggestive.
2. **The class is unresolvable at the irreducible n≈57.** The shape discriminants that
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
well-powered). The finite-r crossover is **statistics-limited at both levels**: the low-r
elevation itself is only *marginal* (~2.3σ, CIs overlap), and *even if* real, its class is
unresolvable at the irreducible n≈57. Gate 0 excludes the loss artifact by measurement, so
what elevation exists is not an artifact — but nothing here rises to a confirmed intermediate
class, and the elevation is not "robust." **The confoundable mean (0.52, GOE-looking) was
correctly NOT promoted to a class, and — this turn's correction — the finite-n confound on the
mean's own significance is now reported reference-to-reference rather than CI-vs-point.** The
null on "confirmed intermediate class" is banked; the discipline held, including against my
own summary compression.

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
