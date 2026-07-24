# ARS-RH Phase 0 — calibrator + measure-declaration gate (BLOCKING, complete)

Spec: the ARS-RH measurement program (calibration, not a proof program — §0 anti-claim binding).
Phase 0 is the blocking gate: the classifier must reproduce a theorem-grade known answer before any
other substrate is touched. **PASS.** Report-before-proceeding: S1 (ζ height), S2 (heat flow),
S4/S5 (Maass) NOT started, per build order.

Artifacts: `arsrh/phase0_measure_gate.py`, `phase0_measure_gate_measured.json`;
existing `approximability/farey_class_certify.py` (Hall spacing gate).

## The Farey→Hall spacing gate was already certified — reproduced

`approximability/farey_class_certify.py`, banked RESULTS_MATRIX.md:130, reproduced this session on
the global sequence F_Q:

| Q | \|F_Q\| | gaps | KS vs Hall (BCZ) | best RMT | min τ vs 3/π² |
|---|---|---|---|---|---|
| 3000 | 2,736,189 | 2.7M | **0.00015** | 0.132 (GOE) | 0.30412 vs 0.30396 |
| 5000 | 7,600,459 | 7.6M | **0.00013** | 0.143 (GOE) | 0.30408 vs 0.30396 |

Hall beats the best RMT surmise by ~1000×; the classifier does **not** return Poisson (KS=0.274) —
the cheapest false-positive check passes. The hard gap sits exactly at Hall's 3/π² = 0.304.
**Theorem-grade known-answer gate: PASS.**

## The three remaining Phase-0 items (this session)

**(A) Completeness / cardinality gate — PASS.** `|F_n| = 1 + Σ_{k≤n} φ(k)` verified *exactly*
(n=50: 775; n=200: 12,233; n=1000: 304,193 — all exact). This is the missing-fraction check that
caught the CP1 completeness defect; a dropped fraction would masquerade as a class shift and this
would catch it.

**(B) Open decision #1 — does unfolding-free ⟨r̃⟩ need modification for bounded support? RESOLVED:
no.** ⟨r̃⟩ = mean of min(sₙ,sₙ₊₁)/max(sₙ,sₙ₊₁) is a ratio of consecutive gaps — scale-free and
local, so bounded vs unbounded support is irrelevant. Witnessed directly: an affine remap of F₂₀₀₀
(x·10⁶−3) leaves ⟨r̃⟩ = 0.7051 invariant to **5.8e-14**. Value matches the banked 0.7051 (Poisson
0.386, GUE 0.603), so the estimator is well-defined and non-Poisson on the n²-density process.

> **⚠ FILING FLAG (dominant error mode — attribution).** ⟨r̃⟩ = 0.7051 **exceeds all four RMT
> surmises** (Poisson 0.386, GOE 0.536, GUE 0.603, GSE ≈0.674). It is the Farey/Hall value —
> Hall repulsion is stronger than any random-matrix ensemble — and it is **off the RMT ladder
> entirely.** It must never be filed against an RMT class; in particular it is *not* "GSE-like"
> just because 0.7051 > 0.674. A future reader (or memory recall) seeing "0.7051, strong
> repulsion" is exactly where the slot error lands. File it as Farey/Hall, full stop.

**(C) §3a measure-declaration gate — PASS (the new, high-value piece).** No tree-derived point
process has a class without a declared sampling measure; the two canonical singular measures must be
separated by a known-answer statistic:

| N | fair-coin AM | Gauss AM (log₂N) | fair-coin max | Gauss max | Gauss GM |
|---|---|---|---|---|---|
| 10⁴ | 1.997 | 14.86 (13.3) | 12 | 41,886 | 2.679 |
| 10⁵ | 2.004 | 13.24 (16.6) | 19 | 114,000 | 2.659 |
| 10⁶ | 2.000 | 18.82 (19.9) | 19 | 881,277 | 2.679 |

- **Fair coin (Minkowski ?-measure):** partial quotients ~ geometric(½), arithmetic mean stable at
  **2.000** (all moments finite), as the theorem requires.
- **Gauss (Lebesgue-typical):** arithmetic mean **divergent** — it tracks log₂N (14.9→18.8 against
  13.3→19.9), never settling; geometric mean → **2.679 ≈ Khinchin K₀ = 2.6854**.
- **Cleanest separator — the max partial quotient:** Gauss max scales ~linearly in N
  (log-max/log-N = **0.99**; heavy 1/k Gauss-Kuzmin tail), fair-coin max scales ~log₂N
  (slope **0.21**; geometric tail). At N=10⁶ that is 881,277 vs 19.

Minkowski and Lebesgue are mutually singular; the estimator separates them on every discriminator
(finite-vs-divergent AM, max-PQ scaling exponent, and the geometric mean landing on distinct
constants). **Instrument passes the singularity separation.**

## The transfer (why Phase 0 is worth doing independent of everything downstream)

§3a is a toy of the fungal Cox-process confound (#4259167) *with a theorem for ground truth*: the
measured class is a property of the generating **measure** (the rate envelope), not of the raw
points — fair coin and Gauss produce different classes from the "same" tree. The portable lesson: a
rate-envelope-preserving surrogate must reshuffle points **without changing the CF-digit measure**,
and that surrogate can now be validated against this known answer before being ported to the fungal
spike trains. That port is the reusable deliverable; it does not depend on any RH-adjacent phase.

## Status / next (held for review, per the blocking-gate protocol)

Phase 0 PASS on all items. Per build order the next steps are **Phase 1** (ζ height crossover in
1/log(γ/2π), sealed prediction first) and **Phase 2** (dBN heat-flow threshold localization — the
portable resolution deliverable), which may run in parallel; **Phase 4** (S4/S5 Maass bridge) is
gated on Phase 0 and now unblocked. None started — reporting first, as the spec requires.

**Anti-claim (§0) reaffirmed:** nothing here is evidence for or against RH. Phase 0 calibrates the
classifier against theorem-grade point processes and declares the sampling measure; that is its
whole content.
