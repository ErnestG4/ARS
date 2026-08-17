# derivflow — local spacing statistics under repeated differentiation

Sealed measurements of what happens to the *local* root-spacing statistics of real-rooted
polynomials as you differentiate them repeatedly — the regime between the proven global laws
(the empirical root measure is asymptotically frozen for all k = o(n) for real roots;
Angst–Nguyen–Poly 2026) and the proven k → ∞ endpoints (Cosine/Hermite universality). To our
knowledge these are the first measurements in that regime, and it is live exploration: everything
here — scope amendments, seals, verdicts, retractions, and the instrument crisis in the middle —
is committed as it happened.

## The result stack

| # | Result | Status |
|---|---|---|
| 1 | Relaxation of 1 − ⟨r̃⟩ toward crystalline follows a **stretched exponential** for every seed class tested (AICc-best of a pre-registered ladder, all instrument bands, n = 1024…16384) | graded (best-of-ladder; χ²/dof disclosed) |
| 2 | **Parameters are seed-dependent**: iid (τ = 1.73, β = 0.79) vs GUE (0.89, 0.70), z = 20σ/9σ sealed, 12σ/5.8σ conservative | **sealed verdict: RATE-SEED-DEPENDENT** |
| 3 | **Crystallization scale is O(1) in n**: k\* ≈ 11 (iid) / 6 (GUE) at every n across 16×; sealed point-prediction discrimination at n = 16384 | **sealed verdict: SCALE-FLAT** |
| 4 | The stretch survives environment conditioning at BOTH k = 0 and k = 2 (the isoconfigurational move) — not seed-carried, not instantaneous-environment-carried | exploratory, rules pinned blind |

Grade on the sealed verdicts: **SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK** — pre-committed rules
executed faithfully, prior looks disclosed in the seals' own ledgers.

## How to read this directory

- `TRACK0_SCOPE.md` — the scope, v1.0 → v1.6, every amendment dated and reasoned. §4 is the
  instrument definition; §9 is the literature status with the adversarial-pull verdicts.
- `TRACK0_FINDINGS.md` — findings §§1–14 in order, including the superseded v1 verdict (banner
  marked), the instrument review, and both sealed verdicts. The TL;DR's FINAL STATE bullet is
  the summary.
- `seals/` — `RATE_QUESTION_SEAL.json` and `SCALE_LAW_SEAL.json`: the pre-committed
  adjudication rules, disclosure ledgers, and code bindings.
- `ROADMAP.md` — the post-verdict step-through document with per-step STATE/LOG.
- `paper/` — `PROSE.md` (full draft), `NOTE.md` (working skeleton with review annotations),
  `figs/` + `make_figs.py`.
- Artifacts (`*.json`) — every run's banked numbers; `archive_v1grid/` preserves the
  pre-correction instrument's outputs for comparison.
- `essays/` (repo root) — the methodology essay and its review.

## The honesty chain (the feature)

The first sealed verdict did not survive: the protocol's own regression step (ROADMAP Step 1)
exposed a reference-grid aliasing artifact, the contamination was measured at 24–38σ on the fit
anchors, the instrument was redefined sight-unseen under the seal's post-change protocol, failed
its own new gate once, was amended, re-certified, and the verdict was downgraded to
INCONCLUSIVE — then resolved at higher grid resolution with the current verdicts. Every step is
a commit; findings §§8–12 narrate it; two pre-submission adversarial reviews (internal +
literature) are applied on top. A hostile reader looking for the weakness should find we
published it first.

## Reproducing

Python via the repo venv (`/home/combust/fmexplorer/bin/python3` locally; numpy/scipy/mpmath).
All RNG derives from `SeedSequence(20260811)` with a child-index allocation pinned in the seals
— every replicate is enumerable in advance. Gates first: `track0_harness.py` (Hermite self-map),
`free_conv.py` (closed-form evaluator gates), `reference_v2_gates.py` (reference known-answers).
Then the science runners (`science_dense.py`, `step3_parallel.py`, `step2*.py`). Wall-clock
economics are in the paper's Appendix C — the big runs are hours-to-a-day; the memory-bandwidth
wall binds before the core count does.
