# Khinchin Landscape — epistemic state

**Status:** Phases 0, 1, 1b, 2 complete, all gates green. Phase 3 (sonification) not started.
**Date:** 2026-08-03. **Commit:** see git log for `khinchin/`.
**Relation to ARS:** ARS-adjacent (approximability arc). Not a phase of ARS-RH.
K is the same order parameter as `approximability/panel_A_K_reframe.py:47`; the a≥2
rate is the `m_k` of the banked Thread-1 bandwidth law `W ≈ 4/λ^{m_k}`
(`approximability/FINDINGS.md:317`). Slot-checked before compute — no drift.

## Banked summary

The unit interval was rendered as a field — position α × continued-fraction depth n,
colour K_n(α) — at N=65536 columns, depth 2048, on exact 8192-bit integer Euclid.
The a.e. convergence of Khinchin's theorem is visible and quantitatively exact: the
median K over 16384 Sobol-sampled columns at depth 2048 is **2.684837** against
K₀ = 2.685452 (0.023%), and the a≥2 rate field lands at 0.5849609 against the
Gauss–Kuzmin 0.5849625 (2.7e−6). All eleven gates pass, including an added G0f that
tests the Euclid engine itself (G0a–G0d as specified test only closed forms and
would pass with the engine broken).

**Two spec defects were found and corrected before production.** (i) The specified
golden grid offset ξ=1/φ makes *every* column a quadratic irrational in Q(√5) — the
measure-zero exceptional set — and costs a measured **+0.54%** bias in median K at
depth 2048 with a bootstrap CI excluding K₀ (+1.35%, ~11σ at preview scale); the
offset is now π−3, transcendental, so no column is algebraic. (ii) Gate G1 asks a₁
to match Gauss–Kuzmin, but on a Lebesgue-uniform grid a₁ has the exact law
1/(k(k+1)); as written the gate fails at p=1.1e−113 and against the correct law
p≈1.0. Gauss–Kuzmin is now tested where it applies, at a₆₄ (p=0.258).

**The field measured something back.** Standardising K_n by the i.i.d. Gauss–Kuzmin
sd left sd(z)=0.932 flat across n=16…2048. The partial quotients are correlated: the
measured autocovariances of log₂a alternate and decay by ratio ≈−0.30 — the
**Gauss–Kuzmin–Wirsing constant** λ=0.30363, the transfer operator's second
eigenvalue — giving Birkhoff σ_B=1.5946 vs marginal 1.7127 and predicting
sd(z)=0.9310 against 0.932 observed.

**The recalled −1.6% RECONCILES — and it was contaminated after all.** Both original
numbers were re-run from the original container and reproduce bit-identically here
(`conductor_sweep.py`): N=3072 at depth 200 gives **−1.60%**, N=4096 at depth 512
gives **+1.35%**. Same offset, same code; the bridging variable is **N itself**.

| N | factorisation | golden d200 | golden d512 | π−3 d200 | π−3 d512 |
|---|---|---|---|---|---|
| 3072 | 2¹⁰·3 | **−1.60%** | −1.86% | −0.12% | +0.18% |
| 4093 | prime | +1.68% | +1.60% | −0.20% | −0.15% |
| 4096 | 2¹² | +1.07% | **+1.35%** | −0.03% | +0.06% |
| 6144 | 2¹¹·3 | +0.70% | +0.19% | −0.20% | +0.03% |

**A previous conclusion here was wrong and is withdrawn.** `chase_preview_number.py`
argued the −1.6% was clean, on the grounds that every contaminated reading is
*positive*. That generalised the sign of the bias from a single N (4096) to all N
without testing it. It is false: at N=3072 the golden bias is −1.86%. The depth-20
median-skew observation in that script remains true of N=4096 and is worth keeping,
but it is **not** the explanation of the recalled number. Superseded by this section.

**Antibody on λ₂ (binding).** This is the *shelf-identity* side of the Gauss-map
spectral story that CP2 already owns — the same transfer operator, independently
re-measured here from a fluctuation field built to look at something else. It is a
corroboration of the correlated-quotient picture, **not a new weld**, and no caption,
filename or note may imply that the landscape establishes a link it merely re-measures.
See [[session-k-arithmetic-chaos]] / CP2 for the slot that owns the operator.

**Spec §1 is amended.** As written it promised "the measure-zero exceptional set
showing as veins that refuse." That is poetry making a false claim, and the run
falsified it. Amended text of record:

> The unit interval is rendered as a field so that Khinchin's theorem is visible:
> the a.e. flow of K_n toward K₀. The exceptional set cannot appear as data — a
> Lebesgue grid meets it with probability zero at any resolution — and its
> presence is instead legible two ways: as the **geometry of absence**, since badly
> approximable numbers admit no strong rational approximants and so sit in
> flare-free calm (the negative space of the Farey storm); and as the
> **constructed atlas** of R7, where exceptional columns are exhibited rather than
> sampled, always labelled as construction.

**The exceptional set cannot appear in this render, and that is a result, not a
shortfall.** A Lebesgue-sampled grid contains no exceptional column with
probability 1. R1z holds contrast constant at every depth, where a refusing column
would saturate as a full-height vein; none does, and none will at any N, D or B.
The nobles/quadratics appear only as explicitly-labelled inserted exact anchor
strips. What the grid does show near 1/φ is real and is an *absence*: badly
approximable ⇒ no strong rational approximations ⇒ comparatively flare-free
surroundings.

## Anomalies and their disposition

| Observed | Disposition |
|---|---|
| median K +1.35% high at preview | **Real.** Golden-offset grid is quadratic-irrational. Corrected; see validation/report.md §2.1 |
| a₁ χ² vs Gauss–Kuzmin p=1e−113 | **Spec defect, not data.** Wrong law named. Corrected §2.2 |
| sd(z) = 0.932 flat in depth | **Real dynamics.** Gauss-map correlation; σ_B closes it to 0.1% §4.1 |
| \|z\|>3 rate 0.121% vs 0.270% | Two causes, both resolved: σ_B (above) and finite-n skewness §4.2 |
| masked fraction exactly 0 | **True and reported as trivial.** Horizon never binds at B=8192, D=2048 §3 |
| R1 spec-literal render near-black | Real consequence of spread ~1/√n. R1z added as the legible companion |
| R3 flare invisible on linear-K layout | Render defect, fixed: flares are shallow raw-quotient objects §5 |
| Preview median recalled as −1.6% | **RESOLVED — contaminated, and N-dependent.** Reproduced bit-identically at its true config (N=3072, depth 200). The golden bias is a function of N of *either sign*: −3.80% (N=4095) … +1.60% (N=4093). `conductor_sweep.py` |
| My earlier "clean, on sign alone" verdict | **WITHDRAWN.** Generalised the bias sign from one N to all N without testing. The depth-20 median-skew result stands for N=4096 only. |
| Golden bias jumps between adjacent N | **Real, 34× the noise.** N=4094…4098 at depth 512: −2.42, −3.80, +1.35, −1.31, −0.43 (%), spread 5.15% vs median SE 0.15%. Smooth finite-size EXCLUDED. |

## Standing cautions carried forward

- **π−3 is an ordinary generic column here.** No claim is made or implied about
  liminf K(π). Empirically-supported, unproven. It is also the grid offset, which
  gives it no special status: no column equals π−3.
- **S1 is never "liminf K."** It is the running-min shadow from n₀, downward-biased;
  burn-in sensitivity is 2.2552 (n₀=16) vs 2.4550 (n₀=64) and is reported wherever
  S1 is shown.
- **R6 claims no weld.** S1 lives on the liminf-K axis; the butterfly's fine
  classification lives on the CF-boundedness/Diophantine axis; these are
  non-equivalent criteria (theorem-level disjoint on the special sets). R6 is an
  illustration of the null union. No identity-form language in any caption,
  filename or note.
- **R7 is construction, never data.** The atlas exhibits bounded-type F_m, metallic,
  noble-tail, arithmetic-growth and Liouville classes as *built* sequences. Their CFs
  are exact at every depth so no trust horizon applies; the grey tail on the Liouville
  column is the generator cap (k≤24), not a precision mask. No claim is made that any
  named real belongs to any of these classes.
- **The golden-grid bias is N-dependent with either sign — the dangerous kind.**
  A good-faith grid-size sensitivity test on the golden grid would watch the answer
  move with N and could read it as convergence trouble, or worse, as structure.
  **Mechanism (SKETCH, not certified):** the columns are the surds (2i−1+√5)/2N; the
  map to √5 has determinant 2N, not ±1, so Serret does not apply and they are not
  tail-equivalent to φ. Each N attaches the ensemble to orders of conductor ~2N in
  ℚ(√5), each family carrying its own period-quotient statistics. The sweep is
  *consistent* with this and excludes smooth finite-size, but does not establish it:
  over 16 N the sign correlates only loosely with small-prime content, and is not a
  clean function of it (2¹¹, 2¹², 2¹³ give +0.81%, +1.35%, −0.03%). Order-theoretic
  account is plausible-mechanism grade. Do not cite it as measured.
- **The three-criteria disjointness stands.** Nothing here welds this picture to
  mode-locking or Sturmian criteria; the render lives on the approximability axis only.

## Reproduce

    /home/combust/fmexplorer/bin/python3 compute.py phase1   # 14 s, 22 workers
    /home/combust/fmexplorer/bin/python3 gates.py   phase1
    /home/combust/fmexplorer/bin/python3 derive.py  phase1
    /home/combust/fmexplorer/bin/python3 render.py  phase1
    /home/combust/fmexplorer/bin/python3 grid_audit.py       # the offset finding
    /home/combust/fmexplorer/bin/python3 conductor_sweep.py  # the N-dependence

**Phase 3 sketch, if it gets a go:** add λ₂ as a decay envelope — the ringdown time
the landscape already told us (autocovariance decay ratio ≈ −0.3036). Still its own
go/no-go; nothing here authorises it.

Master artifact `data/quotients_phase1.npy` (2048×65536 float16 log₂a_n, 256 MB) —
everything else derives from it. `data/derived/` is regenerable, not archival.
