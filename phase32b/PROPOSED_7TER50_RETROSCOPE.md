# PROPOSED retro-scope of RESULTS.md §7.ter.50 — HELD FOR REVIEW

**Status: NOT APPLIED.** Rewrites a committed verdict; held per standing rule.
Reproduce with `phase32b/reliability_gate.py`. Doctrine: `TOOLKIT.md` §9 ceiling arm.

---

## What breaks

§7.ter.50 classified `p7_mean_z` as ORTHOGONAL to FA-nmo (`R²=0.113`) and to raw
per-cell properties (`R²=0.054`), and called it **"the strongest INDEPENDENT_AXES
reading"** — on the *lowest* R² in the panel.

`R²(R,B) ≤ ρ(R)` for any B. A low R² against B is the expected reading of an
**unreliable** axis, not evidence of a novel one. Reliability was never measured.

Split-half reliability of the 5-window mean, across defensible centering frames:

| frame | ρ₅ |
|---|---|
| raw pooled, Pearson | 0.132 |
| within-session z, Pearson | 0.251 |
| raw pooled, Spearman | 0.365 |
| within-session rank→z, Spearman | 0.371 |
| within-session rank, Spearman | 0.437 |

**ρ band = [0.132, 0.437].** True orthogonality at τ=0.20 requires `ρ > R²_obs/τ`:

| target ~ baseline | R²_obs | ρ required | banked | corrected |
|---|---|---|---|---|
| `p7_mean_z` ~ FA-nmo | 0.113 | **> 0.565** | ORTHOGONAL | **INDETERMINATE** — fails across entire band |
| `p7_mean_z` ~ raw props | 0.054 | > 0.270 | ORTHOGONAL | **INDETERMINATE** — flips inside band |

## Why INDETERMINATE and not SUBSUMED

Disattenuated `R²_true(FA-nmo)` across the band = **[0.259, 0.856]**. Every value
clears τ=0.20, so the ORTHOGONAL kill is robust. But the band spans the SUBSUMED
floor (0.50) by a factor of 3.3, driven entirely by denominator uncertainty —
correction-for-attenuation is least stable exactly where ρ is smallest.

**Disattenuation raises the lower bound; it cannot certify the upper.**
Bank INDETERMINATE flat. Do not let a future reader round it up.

## Diagnosed cause: estimator noise, not nonstationarity

`z(p=7)` per window is scored against **3 surrogates** — an sd-of-three denominator.
Result: `max|z| = 190`; `|z|>5` in 14.8% of windows (Gaussian: 0.00006%).

Rank-robust split-half ρ by min-event quartile — monotone in event count
(`Spearman(quartile,ρ) = +1.000`), lowest quartile **anti-correlated with itself**:

| min-events | n | ρ |
|---|---|---|
| 35–173 | 108 | **−0.221** [−0.389, −0.028] |
| 175–414 | 108 | +0.123 |
| 415–1130 | 107 | +0.234 |
| 1177–6628 | 108 | +0.262 |

Nonstationarity would leave this flat. It is **estimator noise**. `p7_mean_z` was
"the strongest INDEPENDENT_AXES reading" *because it was the noisiest metric in the
panel* — the only one built from short windows against 3 surrogates, while
`rep_med`/`ks_gue_med` are full-train estimates.

## Consequences to bank alongside

1. **`rep_med` and `ks_gue_med` are UNCERTIFIED, not untouched.** No per-window
   values were banked, so their ρ is unmeasured. They require `ρ > 0.565` and
   `ρ > 0.630` respectively (`R²_obs` 0.113 / 0.126 vs FA-drift). Until banked,
   **every ORTHOGONAL / INDEPENDENT_AXES verdict resting on them is in an unknown
   state, not a safe one.**

2. **The session-level cross-engine `INDEPENDENT_AXES (ρ = −0.086, n=6)` is
   attenuation-unsafe.** An unreliable axis attenuates every correlation toward
   zero; `ρ≈0` is what noise manufactures.

3. **Threshold scale was never specified, and drifted.** Phase 27 used
   `ORTHOGONAL < 0.3`; Phase 32b uses `< 0.20` while claiming to replicate it.
   Neither declares observed vs disattenuated. An observed-scale threshold is not
   comparable across metrics of differing ρ — so the `BOTH_ORTHOGONAL` comparison
   between `p7_mean_z` (ρ≈0.3) and `ks_gue_med` (ρ unmeasured) was never on one scale.

4. **Not affected:** Phase 32a's population-level `PER_WINDOW_SUBSTRATE_CONSISTENT`
   — averaging across cells can recover a population effect no single cell supports.
   Arithmetic surveys 34a/b/c — entering quantities are exact full-sequence objects
   (`ρ≈1` by construction) and verdicts are stratum-vs-null, not cross-unit
   correlations. Verified: EC root-minus `n=17` counts *curves*; the axis statistic
   is computed on 149,964 pooled exact zeros. Its known weakness (`q=K=17`) is the
   already-banked pooling-null artefact, a different disease.

## Resolution path (do not disattenuate — repair)

Re-run per-window `p=7` with **~100 surrogates** instead of 3. This raises ρ directly.
Then re-measure split-half ρ:

- ρ clears 0.565 and `R²_obs` stays low → **ORTHOGONAL, admissible.** Real axis.
- ρ clears 0.565 and `R²_obs` rises → **SUBSUMED**, now certifiable.
- ρ stays low at high surrogate count → the axis has no stable per-cell value;
  a per-cell regression was the wrong model.

Also re-measure ρ for `rep_med` / `ks_gue_med` (bank per-window values this time)
before re-certifying any of their orthogonality verdicts.

## Proposed verdict line

> **Verdict: INDETERMINATE (was BOTH_ORTHOGONAL).** `p7_mean_z` fails the
> reliability admissibility gate against FA-nmo across the entire ρ band; its
> ORTHOGONAL classification was an artefact of a 3-surrogate estimator.
> Subsumption is **not** certified — the disattenuated estimate is unstable.
> `rep_med` / `ks_gue_med` orthogonality is **uncertified pending banked
> reliability**. The session-level `ρ=−0.086 INDEPENDENT_AXES` is
> **attenuation-unsafe**. Resolve by instrument repair (100 surrogates), not by
> correction-for-attenuation.
