# 04 — Guardrail Wiring Trace (Bucket 5: guardrail gap)

READ-ONLY audit. Code is ground truth. Tags: [code] = read from source, [inferred] = reasoned from
wiring, [documented] = from docstring/prose. Every wiring claim cites file:line, including absences
(the grep that found zero importers).

## Central question answered first

**Does anything auto-run calibrators / induction-on-noise / decoy checks when the live instrument
`cross_substrate/axes.py` computes a verdict?**

**No — `axes.py` is a bare estimator bank with no runtime guardrails.** [code]
- Its only imports are reference curves and fitters: `universality`, `phase35a.unfold_rotnum`,
  `phase34e.run_berry_robnik` (`cross_substrate/axes.py:46,50,51`). A targeted grep for
  `calibrat|decoy|surrogate|verdict|instrument_confound` over the whole file returns **only the
  three `import` lines above and zero guardrail tokens** (grep on `cross_substrate/axes.py`).
- `axes.py` returns raw per-axis floats (`compute_family_I` → dict of estimates,
  `axes.py:244-250`). **It never emits a verdict string, never compares against a calibrator, never
  draws a surrogate.** Quadrant/TR-BL labels and verdicts are assembled downstream, per-port.
- Therefore: when the instrument changes, **nothing re-validates it automatically.** The one
  exception baked into the instrument itself is the rate-robust CV2/Lv pair (see #4).

The guardrail logic that *is* genuinely wired lives in exactly one downstream subsystem
(`longrange_discriminator.longrange_verdict`, the Family-II path) plus the per-phase hand-run
falsification scripts. Everything else — the calibrator zoo, the RF decoy battery, fitter
validation, coordinate audit, apparatus subtraction — is **runnable but disconnected**: standalone
`__main__` scripts nobody re-runs when `axes.py` changes.

## Ladder table

| # | Artifact | Ladder | Evidence (file:line) | What re-runs it |
|---|----------|:------:|----------------------|-----------------|
| 1 | `cross_substrate/calibration_anchors.py` — **the canonical "run GUE/Poisson/clock/GOE/GSE/jitter through the LIVE axes" self-validation** | **b** | imports the live instrument (`calibration_anchors.py:35` `from cross_substrate.axes import …`), runs the zoo "same instrument as substrates" and banks `calibration-anchors.jsonl`; docstring is literally an instrument-revalidation check ("do GUE→q≈1, Poisson→q≈0, clock→W1δ≈0?", `:101`). **Zero importers** (grep: `calibration_anchors: 0 importer(s)`), pure `--run`/`__main__` (`:102,113`). | Nothing. Hand-run only. **This is the headline gap.** |
| 1 | `calibrator_panel.py` (`STATIONARY_/EXTENDED_CALIBRATORS`) | **b** | imported **only** by hand-run scripts: `run_phase20_5_distinctness_revalidation.py:27`, `rf_decoy_battery.py:62`, `phase22a/verify_calibrators.py:56`. Never by an axes verdict path. | Hand-run revalidation / `verify_calibrators` / the (disconnected) decoy battery. |
| 1 | `run_phase13/15/20/20_5/21_calibrators.py` | **b** | each is a standalone `__main__` phase runner (e.g. `run_phase20_5_calibrators.py:24,322`). Per-phase, not a canonical set. | Hand-run, that phase only. |
| 1 | `transition_calibrators_blended.py`, `transition_calibrators_dynamical.py` | **b** | imported by `calibrator_panel.py:47,48`, `run_phase20_5_calibrators.py`, and `tests/test_transition_calibrators.py:20,23` (+ `phase36/track0_regression.py:157`). All hand-run / pytest, never an axes verdict. | `pytest tests/test_transition_calibrators.py`; else hand-run. |
| 1 | `cross_substrate/chialvo_calibrate.py` | **b** | `__main__` only (`:280`), **zero importers** (grep: `chialvo_calibrate: 0`). | Nothing. |
| 1 | `cross_substrate/soc_synthetic_validate.py` | **b** | `__main__` only (`:137`), **zero importers** (grep: `soc_synthetic_validate: 0`). | Nothing. |
| 1 | `cross_substrate/validate_fitters.py` (GOE/GUE/Poisson → Brody/BR ground-truth check) | **b** | imports live fitters `axes.I8_brody_q, I9_berry_robnik_rho` (`:28`) but is `__main__` only (`:104`), **zero importers** (grep: `validate_fitters: 0`). | Nothing. The "synthetic-validate fitters" discipline is **not** auto-enforced. |
| 2 | `surrogates.py` (induction-on-noise / rate-matched / phase-randomized nulls) | **a** *(within hand-run paths)* | `cumulant_matched_events` is imported and used inside the wired long-range verdict (`longrange_discriminator.py:47`); `phase_randomized_iei_events` etc. drive the verdict in `run_phase21_falsification.py:52` + `classify`/survival (`:83,167,253`), `run_phase20_falsification.py:47`, `run_phase18_*`. Surrogate rejection **gates the verdict** in those scripts. **But** every consumer is itself a hand-run `__main__`. | `pytest tests/test_surrogates.py`; otherwise the per-phase falsification scripts, by hand. |
| 3 | `cross_substrate/audit_coordinates.py` (dataset/coordinate audit) | **b** | `__main__` only (`:87`), **zero importers** (grep: `audit_coordinates: 0`). And it only scans coordinate JSONL for NaN/inf bad-floats (`_bad_floats`, `:22`) — a **sanity checker, not an inclusion/selection-criteria gate**. No selection-criteria audit code found beyond per-port rate-match logic. | Nothing. |
| 4 | **Rate-robustness CV2/Lv** (the CV-16 artifact fix) | **a** | `I12_cv2`/`I13_lv` (`axes.py:215,227`) are merged by default: `compute_family_I` does `out.update(family_local(positions))` (`axes.py:249`). **Computed by default** in the canonical Family-I path. | Auto, every `compute_family_I` call (13 ports). **Caveat:** ports that iterate `FAMILY_I` directly over `canonical_spacings` instead of calling `compute_family_I`/`family_local` **skip** CV2/Lv — found 2: `cross_substrate/brocot_audio_harness.py`, `cross_substrate/quasiperiodic_deepening.py`. Docstring flags this contract (`axes.py:237-242`). |
| 5 | `cross_substrate/instrument_confound.py` (apparatus subtraction: deadtime/thinning/lensing) | **a / b (split)** | **(a)** its calibrator-position generators `gue_positions, poisson_positions, axis_values` are imported and called *inside* the wired long-range verdict (`longrange_discriminator.py:42`, used in `_reference_ensembles` `:175,176`). **(b)** the full apparatus-subtraction stage is invoked only by dedicated hand-run scripts: `cross_substrate/hc3_instrument_pass.py:35`, `cross_substrate/hc3_cv2_diagnostic.py:38`, `run_phase18_finding_validation.py:60`, and `rf_decoy_battery.py:63`. `__main__` self-test at `:985`. No port runs apparatus subtraction as part of its normal verdict. | (a) auto inside `longrange_verdict`; (b) hand-run apparatus-pass scripts. |
| 6 | **Long-range decoy battery** — Wigner-renewal decoy + N≥200 floor (`longrange_discriminator.py`) | **a (verdict) / b (adequacy self-test)** | The verdict path is wired: `longrange_verdict` (`:180`) judges live data against GUE/Poisson **reference ensembles built at call time** (`_reference_ensembles:163-176`), and consumers gate on the `MIN_N_LONGRANGE=200` floor via `enough_for_longrange` (`longrange_allen_audit.py:67`, `longrange_neural_audit.py:89`). **But** the decoy-**adequacy** self-tests `validate()` (`:336`) and `validate_rate_unfold()` (`:284`) are **not auto-run** by `longrange_verdict`; of 5 consumers only `longrange_audit.py:71` even exercises the `wigner_renewal` decoy as a data row, and **none** call `validate_rate_unfold`. | (a) `longrange_verdict` + `enough_for_longrange` run every audit; (b) decoy-adequacy gate is opt-in, almost never invoked. |
| 6 | `cross_substrate/rf_decoy_battery.py` (RF-engine decoy battery) | **b** | imports `calibrator_panel` + `instrument_confound` (`:62,63`) but is `__main__` only (`:308`), **zero importers** (grep: `rf_decoy_battery: 0`). | Nothing. |
| — | `cross_substrate/axes.py` (**LIVE INSTRUMENT**) | n/a | bare estimator bank; no calibrator/surrogate/decoy import (`:46-51` + token grep = 0). | Self-validation only via `calibration_anchors.py` — which is disconnected (#1). |

## Tally

- **(a) RUNNABLE & INVOKED:** 3 distinct guards — rate-robust CV2/Lv (default in `compute_family_I`);
  the long-range calibrator-reference-ensemble + N≥200 floor inside `longrange_verdict`; surrogate
  rejection inside `longrange_verdict` / per-phase falsification scripts. `instrument_confound` is
  (a) **only** in its narrow role as a GUE/Poisson position generator for `longrange_verdict`.
- **(b) RUNNABLE BUT DISCONNECTED:** ~12 — `calibration_anchors`, `calibrator_panel`,
  `rf_decoy_battery`, the five `run_phaseN_calibrators`, `transition_calibrators_*` (as calibrators),
  `chialvo_calibrate`, `soc_synthetic_validate`, `validate_fitters`, `audit_coordinates`, and the
  apparatus-subtraction stage of `instrument_confound`.
- **(c) DESCRIBED ONLY:** 0 pure-prose artifacts — everything has executable backing. **But the
  *concept* of a canonical calibrator set auto-re-run when the instrument changes is effectively (c):
  it exists as code (`calibration_anchors.py`) yet has no caller, so operationally it is documented
  intent without enforcement.**

## Verdict on the central question

The live instrument is **NOT guarded at runtime.** `axes.py` is a pure estimator bank. The single
guardrail compiled into it is the CV2/Lv rate-drift control, and only for the ~13 ports that call
`compute_family_I`/`family_local` (2 ports bypass it). Every other guardrail — the calibrator zoo,
the RF decoy battery, fitter ground-truth validation, the coordinate audit, the apparatus-subtraction
stage — is a standalone `__main__` script that **nothing imports and nothing re-runs** when the
instrument changes; the canonical self-validation that does feed the live axes
(`calibration_anchors.py`) has zero importers. The lone exception is the Family-II long-range path
(`longrange_discriminator.longrange_verdict`), which genuinely wires calibrator reference ensembles +
the N≥200 floor + a marginal-preserving surrogate into the verdict at call time — but even there the
decoy-**adequacy** check is opt-in and 4 of 5 consumers skip it. The falsification protocol can
therefore silently fail to be enforced: a change to `axes.py` triggers no automatic re-validation,
and per-cell/per-port Family-I verdicts ship without any calibrator, surrogate, or decoy check unless
a human remembers to run the disconnected scripts.
