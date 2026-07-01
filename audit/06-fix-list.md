# 06 — Fix List (nothing fixed inline — this is the to-do)

**Audit pinned at commit `1a6c7a1` (`1a6c7a1aad3246d03b99a5d72f74b70ca3582372`), branch `master`.** Line numbers are
as of that commit; they drift — re-confirm by symbol before editing.

Every actionable defect, with `file:line`, evidence artifact, proposed fix, severity. **Read-only audit: none touched.**

> ### Audit-integrity notice (2026-06-30 reviewer review)
> Two items from the first pass were **wrong and are retracted** — both the exact "fluent-claim-without-recheck"
> antiprocess this audit exists to catch, reproduced *inside* the audit:
> - **FIX-16 (RETRACTED):** claimed `I10_cv` docstring "GUE≈0.42" was wrong / "true ≈0.522". **The docstring is correct.**
>   GUE Wigner-surmise CV = √(3π/8−1) = **0.422**; 0.522 is the *GOE* value. The first pass wrote the right formula
>   then miscomputed √0.178 as 0.522. Empirically confirmed live: GUE β=2 I.10_cv=0.448, GOE β=1=0.558.
> - **FIX-14 (RETRACTED):** claimed the Pillar-2 DSI axis "has no code". **It does** — `phase22a/h1_functional.py:96`
>   computes it, and it's used as a Pillar-2 descriptor. A sub-agent absence-claim (weakest evidence class) that wasn't
>   grep-confirmed. Lesson applied below: **absence claims (FIX-13) are now grep-confirmed before any doc is softened.**
>
> Root cause for both: a load-bearing constant / an absence assertion was relayed from a sub-agent without independent
> re-derivation/grep. The fix-list now ships P0s as **failing-first regression tests** so audit N+1 can't re-find — and
> can't re-mis-find — these.

---

## Work the dependency DAG, not the P0→P2 column

The fixes are **not** independent. Order matters, because some fixes are unsafe or meaningless until their prerequisites land:

```
  FIX-1 ($HOME import)  ─┐
                         ├──>  FIX-8 (wire self-validation / CI gate)   <-- installing this BEFORE
  FIX-2 ⇔ FIX-7 (Family II un-asserted unfold;  ─┘     ▲                     1+2 land = a gate that
        SAME ROOT CAUSE — fix once)                     │                     certifies the instrument
                                                        │                     BACKWARDS. Do not.
  FIX-4 / FIX-5 / FIX-6  (de-fork the 9–10 estimator copies)  ──────────┘
        └─> prerequisite for FIX-8 & FIX-12: you cannot durably guard an
            instrument whose estimators live in forks — you'd guard one fork.

  FIX-3 (chirp GUE unfold)   — independent P0, ship with its own regression test.
  POISON (anchors.jsonl)     — done (deleted); independent.
```

**Ordering, concretely:**
1. **FIX-1**, **FIX-2+FIX-7** (one fix), **FIX-3** — the P0 correctness layer. Each ships a failing-first test.
2. **FIX-4 / FIX-5 / FIX-6** — consolidate the estimator forks to single imported sources. *Prerequisite for any durable guard.*
3. **FIX-8 / FIX-12 / FIX-10 / FIX-9 / FIX-11** — the guard layer. Only meaningful once 1–2 hold.
4. **FIX-13 (grep-confirmed) / FIX-15** — claim/doc alignment.
5. **P2** docs/naming — anytime.

---

## Priority table (with dependencies)

| ID | sev | depends on | one-line | file:line |
|---|---|---|---|---|
| FIX-1 | **P0** | — | literal `$HOME` breaks `signal_gen` import (16 importers) | `signal_gen.py:16` |
| FIX-2 | **P0** | (=FIX-7) | calibrator Σ² inverted (GUE>Poisson) — wrong unfolder | `calibration_anchors.py:63-67` |
| FIX-7 | **P0** | (=FIX-2) | Family II trusts an un-asserted unit-mean precondition | `axes.py:277,293` |
| FIX-3 | **P0** | — | GUE ref uses documented-"OLD broken" global-mean unfold | `run_chirp_prediction.py:111` |
| POISON | **P0** | FIX-2 | **DONE** — deleted poisoned `calibration-anchors.jsonl` | `cross_substrate/coordinates/` |
| FIX-4 | P1 | — | `analytical_nns` ×9 copies, PLL freq-guard drifted | 9 files |
| FIX-5 | P1 | — | `unfold_unit_mean` ×10 copies, `JPF_CAP` 5000 vs 1500 | 10 files |
| FIX-6 | P1 | — | ≥3 divergent GUE generators/unfolders | `fix_gue_generator.py`, … |
| FIX-8 | P1 | 1,2,7,4,5,6 | wire self-validation into CI (theorem-anchored) | `axes.py`, `tests/` |
| FIX-12 | P1 | 4,5,6 | fold canonical calibrators into the test suite | (see below) |
| FIX-10 | P1 | 2,7 | make long-range lens/decoy check mandatory | `longrange_discriminator.py:243` |
| FIX-9 | P1 | 4 | deployed verdict ships per-cell with no surrogate gate | `arithmetic_toolkit.py:724` |
| FIX-11 | P1 | 5 | 2 ports skip the CV2/Lv rate-robust default | `brocot_audio_harness.py`, `quasiperiodic_deepening.py` |
| FIX-13 | P1 | — | claimed RF `peak_q` L-family discriminator not wired **(grep-confirmed absent)** | (claim only) |
| FIX-15 | P1 | 8 | default verdict leads with marginal NNS, long-range opt-in | `arithmetic_toolkit.py:781-801` |
| FIX-17 | P2 | — | "2–98% tail trim" is an ordinal edge trim, mislabeled | `unfold_rotnum.py:72` |
| FIX-18 | P2 | — | `pair_correlation` docstring promises a GOE form it omits | `universality.py:204` vs `231` |
| FIX-19 | P2 | — | `unfolded_spacings_zeta` returns positions not spacings | `run_second_order.py:36` |
| FIX-20 | P2 | — | banked `rf_amp_per_q` indicator-mode vs engine `normalize=True` | `arithmetic_toolkit.py:~177` |
| FIX-21 | P2 | — | ζ-canonical PLL gains ≠ `PLLParams` defaults | `run_analytical_nns.py` vs `pll_bank.py` |
| FIX-22 | P2 | — | `run_fungal_nns.analytical_nns` is a different algo, same name | `run_fungal_nns.py:119` |
| ~~FIX-14~~ | — | — | **RETRACTED** — DSI *is* implemented (`h1_functional.py:96`) | — |
| ~~FIX-16~~ | — | — | **RETRACTED** — `I10_cv` "GUE≈0.42" was correct | — |

---

## P0 — Correctness / blockers (each ships a failing-first regression test)

### FIX-1 — literal `$HOME` in `signal_gen.py:16`
```python
sys.path.insert(0, '$HOME/fmexplorer/riemann_explorer')   # never expands -> ModuleNotFoundError: scanner
```
`scanner.py` exists at the expanded path; the literal string is never expanded, so `signal_gen` (16 importers) is
import-broken on a clean process (it only "works" if `riemann_explorer` is already on `PYTHONPATH`/cwd). **Fix:**
`os.path.expanduser('~/fmexplorer/riemann_explorer')` (or compute relative to the repo / read an env var).
**Regression test (the durable win):** a one-line test that does `subprocess.run([sys.executable, '-c', 'import signal_gen'])`
in a clean env and asserts exit 0. That test would have caught this cycles ago.

### FIX-2 ⇔ FIX-7 — same root cause: the long-range Σ² is computed on un-renormalized density
`calibration_anchors._fingerprint` (`:63-67`) calls `compute_family_II(unfold_unit_mean(events))`; `unfold_unit_mean`
is a *global* mean rescale that leaves the semicircle density gradient in, so Σ²(L=50) integrates over it →
GUE=107 > Poisson=55, inverted (reproduced live, `05` RUNTIME-2). **FIX-7 is the same defect one layer down:**
`axes.py` `II1_sigma2_at_L:277` / `II2_delta3_at_L:293` apply no internal renorm and trust an un-asserted unit-mean
precondition. **Fix once, at the estimator:**
- **General fix = a density-ADAPTIVE local unfold** (the local polynomial fit `longrange_verdict` already uses,
  `unfold_deg`), NOT a semicircle unfold. ⚠️ **Trap to avoid:** "apply a semicircle unfold to eigenvalue inputs" only
  works for semicircle-density inputs — applied to Poisson/clock it reintroduces a *different* version of the same bug.
  Do not trade one hard-coded density assumption for another; use the adaptive fit that conforms to whatever density is present.
- Have Family II either (a) require already-locally-unfolded input and **assert** it (warn if `|mean(diff)−1|>tol` or if a
  low-order density fit is non-flat), or (b) do the local unfold internally.
- Route `calibration_anchors` Family-II through `longrange_verdict` so the calibrator uses the same adaptive lens + the
  lens-sensitivity check.

**Regression test:** assert the **sign**, not a threshold (see FIX-8) — `Σ²_GUE(L) < Σ²_Poisson(L)` at the audit L.

### FIX-3 — `run_chirp_prediction.py:111` GUE reference uses the "OLD broken" unfold
Unfolds the GUE reference by global-mean spacing — the method `fix_gue_generator.py:60` itself labels "OLD broken" —
while a comment claims semicircle parity. Result: a `gue` reference that is **not Wigner-distributed**. **Fix:** use the
adaptive/semicircle unfold (`fix_gue_generator.unfold_semicircle_R:67`) and correct the comment. **Regression test:** the
generated GUE reference's NNS must pass a KS-vs-Wigner check (the calibrator confusion test already does this for the
marginal axes — extend it to this generator).

### POISON — `calibration-anchors.jsonl` (DONE)
Written by the inverted calibrator (FIX-2), so its long-range column held wrong anchor values. **Grep-confirmed: nothing
*reads* it** — only `calibration_anchors.py:96` *writes* it (no downstream consumer of banked anchors). The committed
copy (Phase-37 `6cc8c06`) is *also* poisoned. **Action taken:** deleted the working-tree file (git shows `D`; reversible
via `git checkout`). **Recommend:** commit the deletion; regenerate only *after* FIX-2 lands.

---

## P1 — Estimator copy-drift (prerequisite for the guard layer)

> You cannot durably wire a guard (FIX-8/12) onto an instrument whose estimators live in 9–10 forks — you'd guard one
> fork while the others drift unseen. **Consolidate first.**

### FIX-4 — nine `analytical_nns`, drifted PLL frequency-admission guard
Reference `run_analytical_nns.py:84`. Copies: `run_phase4.py:52`, `run_phase5.py:53`, `run_lmfdb_family.py:66`,
`run_lmfdb_postprocess.py:23`, `run_dirichlet_family.py:52`, `run_lmfdb_extend.py:36`, `run_mertens_liouville.py:120`;
plus `run_fungal_nns.py:119` (a *different* algorithm sharing the name — FIX-22). Guard drifted `5.0<f<SR*0.45` vs
`f>0.5` (Nyquist cap dropped) vs `>5.0` cap-off. **Fix:** one canonical `analytical_nns` in a module; import everywhere;
reconcile the guard.

### FIX-5 — ten `unfold_unit_mean`, drifted `JPF_CAP`
`run_phase20_classification.py:56`, `run_phase20_calibrators.py:71`, `run_phase21_classification.py:59`,
`run_phase21_calibrators.py:61`, `run_phase21_falsification.py:71` (+ the `ars_classify` copy). `JPF_CAP` 5000 vs 1500,
different decimation strides, a same-phase fork. **Fix:** single canonical `unfold_unit_mean`; pin `JPF_CAP`.

### FIX-6 — divergent GUE generators / unfolders
≥3 generators with different unfolding (`fix_gue_generator.py`, `run_phase9_extended.py:35`, `run_chirp_prediction.py`
per FIX-3). **Fix:** one GUE generation+unfolding helper; route all calibrators through it.

---

## P1 — Guardrail wiring (only meaningful after the layers above)

### FIX-8 — wire the self-validation into CI, anchored to the THEOREM not a fitted threshold
`axes.py` runs no calibrator at compute time; `calibration_anchors.py` has zero importers + is import-broken (FIX-1).
**Fix:** a `tests/test_axes_calibration.py` that runs the calibrator zoo through the live axes and asserts. **Anchor
each assertion to a result, not a tuned constant**, so it can't drift and trips loud on any future regression:
- marginal (pass today, `05` Block 1): GUE→Brody q≈1 & ks_gue<Poisson's; Poisson→Brody q≈0; clock→W1δ≈0.
- **long-range (the one that was inverted): assert the SIGN `Σ²_GUE(L) < Σ²_Poisson(L)` at the audit L.** That
  inequality is a theorem (rigid spectrum vs Poisson), not a threshold — it would have tripped the instant the
  unit-mean-unfold copy inverted Σ², which is exactly how this stayed unseen. **Prereq: FIX-1, FIX-2/7.**

### FIX-12 — fold the canonical calibrator subset into `tests/`
Disconnected (`__main__`-only, zero importers): `rf_decoy_battery`, `validate_fitters`, `audit_coordinates`,
`chialvo_calibrate`, `soc_synthetic_validate`, `calibrator_panel`, the `run_phaseN_calibrators`. **Fix:** run the
canonical subset (GUE/Poisson/picket + decoy battery) in `tests/`, against the *consolidated* estimators (FIX-4/5/6).

### FIX-10 — make the long-range lens/decoy check mandatory before a promotable verdict
`unfolding_sensitivity` (`:243`) / `validate_rate_unfold` are opt-in; 4/5 consumers skip them. `05` RUNTIME-3 shows a
clean GUE is lens-**COVARIANT** at default `unfold_deg=6` (verdict moves POISSON_INDEP→INTERMEDIATE across degrees).
**Fix:** `longrange_verdict` should run the lens sweep by default and refuse to emit a *promotable* RIGID_GUE/
POISSON_INDEP when COVARIANT; and **document that semicircle-density inputs need a higher `unfold_deg`** (the default 6
under-unfolds them). **Prereq: FIX-2/7.**

### FIX-9 — attach a falsification gate to the deployed verdict
`joint_quadrant_diagnostic` (`arithmetic_toolkit.py:724`) emits per-cell quadrants with no surrogate/calibrator check.
**Fix:** require a calibrator-anchored confidence or per-call induction-on-noise comparison. **Prereq: FIX-4.**

### FIX-11 — two ports skip the CV2/Lv rate-robust default
`brocot_audio_harness.py`, `quasiperiodic_deepening.py` iterate `FAMILY_I` directly, bypassing `family_local`.
**Fix:** route through `compute_family_I` (`axes.py:244`) or merge `family_local(positions)`. **Prereq: FIX-5.**

---

## P1 — Claims vs code (confirm-by-grep before softening any claim)

- **FIX-13** — RF `peak_q` L-function family discriminator. **Grep-confirmed absent** (2026-06-30): no
  `lmfdb`/`dirichlet`/`lfunc` script references `peak_q` or `peak_divergence_q` (the only `peak_divergence_q` is
  `gratings_divergence.py`, neural). Safe to either implement+wire on `run_lmfdb_family.py`/`run_dirichlet_family.py`, or
  soften the README/CAPABILITY_REPORT claim.
- **FIX-15** — NNS-downgrade emphasis: deployed verdict leads with marginal NNS (`arithmetic_toolkit.py:781-801`),
  long-range opt-in. Docs are *honest* about this, so lower priority — principled fix is to **emit the Σ²/Δ₃ long-range
  cross-check alongside the marginal quadrant by default**. **Prereq: FIX-8** (don't foreground a path until it's guarded).

---

## P2 — Docs / naming / cosmetic
- **FIX-17** `unfold_rotnum.py:72` — "2–98% tail trim" is an *ordinal edge* trim, not a percentile-of-value trim. Rename/comment.
- **FIX-18** `universality.py:204` vs `:231` — `pair_correlation` docstring promises a GOE R₂ form the return omits. Doc or implement.
- **FIX-19** `run_second_order.py:36` — `unfolded_spacings_zeta` returns *positions*, a same-named function elsewhere returns *spacings*. Rename one.
- **FIX-20** banked `rf_amp_per_q` indicator-mode vs engine `normalize=True` default (`arithmetic_toolkit.py:~177`). Document stored-artifact semantics.
- **FIX-21** ζ-canonical run uses `K_p=0.02/K_i=0.001` ≠ `PLLParams` defaults `0.10/0.005`. Reconcile or document.
- **FIX-22** `run_fungal_nns.py:119` — `analytical_nns` is a different algorithm sharing the canonical name. Rename.

---

## Not a bug — explicitly cleared (do **not** "fix")
- **GOE/GUE number-variance reference curves** (commit `1a6c7a1`): fully consistent; single function; `axes.py` never used them (`02 §7`).
- **One-sided KS, trapezoidal GUE-CDF, 64-pt Δ₃ integral, Brody q∈[0,1] cap** — benign approximations, uniform (`02 §5`).
- **Guarded `longrange_verdict` reading INTERMEDIATE/COVARIANT on a semicircle GUE** is *correct behavior* (refuses to over-promote); the fix is the calibrator (FIX-2) + default-degree docs (FIX-10), not the verdict.
- **`I10_cv` docstring "GUE≈0.42"** — correct (RETRACTED FIX-16).
- **Pillar-2 DSI axis** — implemented (RETRACTED FIX-14).

## Audit-created / modified files
- `audit/*.md`, `audit/phase5_runtime.py` — read-only reproducer + reports. Keep or delete.
- `cross_substrate/coordinates/calibration-anchors.jsonl` — **deleted** (poisoned by FIX-2; nothing reads it). Commit the deletion.
