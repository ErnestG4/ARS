# 04 — Discrepancy Synthesis

*Audit pinned at commit `1a6c7a1` (branch `master`). Two items retracted on 2026-06-30 reviewer review — see `06` integrity notice.*

Pure diff of Phases 0–3. Every item cites the prior artifact it came from (`01` tools, `02` math, `02d` =
`02-math-drift.md`, `03` claims, `04g` = `04-guardrails.md`) **and** a `file:line`. No new findings are introduced here
that don't trace to a prior artifact — pull the cited source to verify any line.

**Provenance caveat:** Phases 1–3 + the guardrail trace were produced by read-only sub-agents that pasted `file:line`
for each claim. The canonical-math (`02`) and drift (`02d`) lines were read line-by-line; some Layer-A/D rows in `01`
were sub-agent-relayed and spot-verified, not 100% re-read (stated in `01`). Treat `[likely bug]` items as
*audit-flagged, not yet reproduced* — Phase 5 (gated) is what would confirm them empirically.

## Summary (bucket → count)

| # | bucket | count | headline |
|---|---|---|---|
| 1 | In code, undocumented | 4 | chaos axes (Lyapunov/corr-dim) + SFF/pair-corr computed but not surfaced as claims |
| 2 | Documented, not in code | 3 | RF `peak_q` L-family discriminator **[not-found, grep-confirmed]**; Eisenstein loader; "2–7×" magnitude. ~~DSI axis~~ **RETRACTED** — DSI is in code (`h1_functional.py:96`). |
| 3 | Implemented ≠ described | 4 | `unfold_rotnum` "tail trim" is an edge trim; `pair_correlation` omits promised GOE form; `unfolded_spacings_zeta` returns positions not spacings |
| 4 | Math deviations | 7 | **[likely bug]** `run_chirp_prediction` GUE uses the documented-"OLD broken" unfold; PLL freq-guard + `JPF_CAP` drift across copies. ~~I10_cv docstring~~ **RETRACTED** (audit error — docstring was correct). |
| 5 | **Guardrail gap (highest value)** | 8 | live `axes.py` runs **no** calibrator/surrogate/decoy at compute time; canonical self-validation has **zero importers** (and is import-broken — `05` RUNTIME-1) |
| — | **total** | **26** | both flagged priors confirmed; **2 items retracted on reviewer review (FIX-14 DSI, FIX-16 CV) — see `06`** |

---

## Bucket 1 — In code, undocumented (real capabilities the project doesn't surface)

*Least-swept bucket: the audit targeted the canonical surface + claims ledger, not an exhaustive "what's undocumented"
sweep. Items below are what surfaced incidentally; absence here is not evidence of completeness `[inferred]`.*

1. **Chaos axes computed but unclaimed** — `axes.py` Family V `V1_lyapunov:392`, `V2_correlation_dim:439`, Family VI `VI1_L_iter_alpha`. Live estimators; not among the ~70 extracted claims (`03`). (`01` Layer C; `02`)
2. **Spectral form factor + pair correlation** — `universality.py spectral_form_factor:173`, `pair_correlation:194`. Computed long-range estimators beyond the claimed Σ²/Δ₃ pair. (`02`)
3. **Substrate loaders beyond the claimed roster** — dual-region HTTP-range NWB streaming, GRB FITS, Binance, EEG (`pyedflib`) ingest paths exist in `01` Layer A but aren't surfaced as headline capabilities. (`01` Layer A)
4. **`instrument_confound` dual role** — used as a position-generator *inside* `longrange_verdict` (wired) in addition to its documented standalone apparatus-subtraction role. (`04g §7`)

## Bucket 2 — Documented, not in code (claims with no executable backing)

1. **RF `peak_q` discriminates L-function families with identical NNS — [not-found].** Claimed (`03` Katz–Sarnak theme); not wired into any L-function script. The RF engine exists (`arithmetic_toolkit.py:130`) but no L-family driver calls `peak_q` to separate families. (`03 §6`)
2. ~~**DSI Pillar-2 axis — no located code.**~~ **RETRACTED 2026-06-30 (audit false-negative).** DSI *is* computed: `phase22a/h1_functional.py:96` (`DSI = |Σ rₖe^{iθₖ}|/Σ rₖ`), banked to parquet, used as a pillar-2 descriptor (`phase22b/pass_a_recording_blocked.py:57`, `gratings_divergence.py:100`). The sub-agent did not read `phase22a/`. Claim is **[supported-in-code]**.
3. **Eisenstein / Dedekind-ζ loader — briefs only.** Referenced in phase briefs; no live loader on disk. (`01 §1`)
4. **"global CV inflated 2–7×" specific magnitude — [partial].** The *mechanism* (CV vs CV2/Lv) is backed (`axes.py:175/215/227`); the 2–7× figure is a runtime output, not a code constant. (`03 §6`)

## Bucket 3 — Implemented ≠ described (semantic drift: name ≠ behavior)

1. **`unfold_rotnum.py:72` "2–98% tail trim"** is an *ordinal edge* trim, not a magnitude/percentile-of-value trim as the phrase implies. `[intentional+undocumented]` (`02 §3`)
2. **`pair_correlation` docstring promises a GOE R₂ form the return omits** — `universality.py:204` (docstring) vs `:231` (return). (`02 §3`)
3. **`unfolded_spacings_zeta` returns positions, not spacings**, while a same-named function elsewhere returns spacings — splice/naming hazard. (`02d §3`)
4. **Banked `rf_amp_per_q` is indicator-mode** despite the RF engine's `normalize=True` default — the stored artifact's semantics differ from the engine's default semantics. (`01 §5`)

## Bucket 4 — Math deviations (`[likely bug]` first)

1. **`[likely bug]` `run_chirp_prediction.py:111` GUE reference uses global-mean-spacing unfolding** — the exact procedure `fix_gue_generator.py:60` documents as the **"OLD broken"** method — while its own comment claims parity with the semicircle unfold. Its `gue` reference is therefore **not Wigner-distributed**. Highest-severity math item. (`02d §6`)
2. ~~**`[likely bug]` `I10_cv` docstring "GUE≈0.42"**~~ **RETRACTED 2026-06-30 (audit error).** The docstring is CORRECT: GUE surmise CV = √(3π/8−1) = 0.422; 0.522 is the *GOE* value. The original pass miscomputed √0.178 as 0.522 and flagged a correct constant — the very antiprocess this audit targets, reproduced inside it. Empirically confirmed live (GUE 0.448 / GOE 0.558). No fix. (`02 §1`)
3. **`[parameter-drift]` `analytical_nns` PLL frequency-admission guard drifted 3 ways** across 9 copies: ref `5.0<f_pll<SR*0.45` vs five phases at `f_pll>0.5` (Nyquist cap **dropped**) vs phase5 `>5.0` cap-off. Two phases' "same" estimator admitted different lock sets. (`02d §1`)
4. **`[parameter-drift]` `unfold_unit_mean` `JPF_CAP` drifted 5000 vs 1500** with different decimation strides; a same-phase fork in Phase 20/21 (`classification` cap 1500 vs `calibrators` cap 5000). (`02d §2`)
5. **`[risk, undocumented]` Family II applies no internal unit-mean renorm** — `axes.py` `II1_sigma2_at_L:277`/`II2_delta3_at_L:293` trust an upstream unit-mean contract; L-scale is silently wrong if a caller hands non-unit-mean positions. Latent, guard-gap-shaped. (`02 §4`)
6. **`[parameter-drift]` ζ-canonical run uses `K_p=0.02/K_i=0.001`** ≠ `PLLParams` defaults `0.10/0.005`. (`01 §5`)
7. **`[approximation, benign]`** one-sided KS (max over `i/n`), trapezoidal GUE-CDF, 64-point Δ₃ integral, Brody `q∈[0,1]` one-sided cap — uniform across the codebase, classified benign. (`02 §5`)
8. **`run_fungal_nns.py:119 analytical_nns` is a different algorithm** (no time-band, no tongue threshold) sharing the name — `[semantic-drift]`, not a copy. (`02d §1`)

> **NOT a bug — explicitly cleared:** the GOE/GUE number-variance reference-curve fix (commit `1a6c7a1`) is **fully
> consistent**. The swapped prefactors lived in exactly one function (`universality.number_variance`); post-fix
> GOE=2/π², GUE=1/π² (ratio→2, correct). `axes.py` Family II never imports those analytic curves (it compares to
> Monte-Carlo ensembles), so there was no second copy to drift. (`02 §7`)

## Bucket 5 — Guardrail gap (highest value: the falsification protocol's runtime enforcement)

*Framed on the wiring ladder (`04g`): (a) runnable & invoked / (b) runnable but disconnected / (c) described only.
For a script-archive, "enforced gate" is the wrong yardstick — the question is whether anything **re-runs the guard when
the instrument changes**.*

1. **The live instrument `cross_substrate/axes.py` is NOT guarded at runtime.** Bare estimator bank; imports only reference curves + fitters (`axes.py:46,50,51`); zero `calibrat`/`decoy`/`surrogate`/`verdict` references. Emits raw floats. (`04g §2`)
2. **The canonical self-validation `calibration_anchors.py` has ZERO importers** — the one artifact that runs GUE/Poisson/clock *through the live axes* ("do GUE→q≈1, Poisson→q≈0?") needs a manual `--run` and nothing re-invokes it when `axes.py` changes. This is the headline gap. (`04g §4`)
3. **The deployed per-cell verdict `joint_quadrant_diagnostic` (`arithmetic_toolkit.py:724`) ships with no calibrator/surrogate/decoy check.** (`04g §8`; `03 §2`)
4. **NNS-downgrade emphasis — CONFIRMED [contradicted-by-code] for "default leads with long-range".** The deployed quadrant keys purely on `rep_int_q + ks_gue_q + RF spike` (`arithmetic_toolkit.py:781-801`); grep for `sigma2`/`delta3` in the deployed path → **zero hits**. Long-range Σ²/Δ₃ is opt-in audit-script only. **Mitigating, important:** the docs are *honest* about this (README:29/393, EPISTEMIC_STATE:1774 call the deployed quadrant marginal-only and order-blind by construction) — build-order lag, **not concealment**. (`03 §2,§3`)
5. **Only the Family-II `longrange_verdict` is runtime-guarded** (builds GUE/Poisson references at call time, enforces N≥200) — but its decoy-**adequacy** self-test (`validate`/`validate_rate_unfold`) is opt-in and **4 of 5 consumers skip it**. (`04g §5`)
6. **`surrogates.py` gates verdicts only inside hand-run `__main__` phase scripts** (run_phase18/20/21) — never auto-triggered by `axes.py`. (`04g §6`)
7. **~12 calibrator/falsification scripts are runnable-but-disconnected (b):** `rf_decoy_battery`, `validate_fitters`, `audit_coordinates` (NaN-checker only — *not* a selection-criteria gate), `chialvo_calibrate`, `soc_synthetic_validate`, `calibrator_panel`, the `run_phaseN_calibrators`. Nobody re-runs them when the instrument changes. (`04g §7`)
8. **2 ports skip even the one in-instrument guard** — `brocot_audio_harness`, `quasiperiodic_deepening` iterate `FAMILY_I` directly, bypassing the CV2/Lv rate-robust default that `compute_family_I` provides (`axes.py:249`). (`04g §3`)

> **Net Bucket-5 reading:** the *math* is largely faithful (Bucket 4 is mostly benign approximations + copy-drift in
> parameters, one real GUE-unfold bug). The *protocol* is the soft spot: the durable output — calibrator zoo,
> induction-on-noise, decoy battery, dataset-selection audit — is **real, runnable, and almost entirely disconnected
> from the live instrument**. Changing `axes.py` triggers no automatic re-validation. Per-cell Family-I verdicts ship
> unguarded. This is exactly the "described-but-not-enforced" failure mode the audit was built to find.
