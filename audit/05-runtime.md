# 05 — Runtime Verification

*Audit pinned at commit `1a6c7a1` (branch `master`).*

**Status: RAN (with one workaround).** Every number below is real output from the live tool on this tree, not
extrapolated. Reproduce with `audit/phase5_runtime.py` (the calibrator confusion table is the project's own
`cross_substrate/calibration_anchors.py --run`).

**Invocation:**
```bash
PYTHONPATH=$HOME/fmexplorer/riemann_explorer \
  $HOME/fmexplorer/bin/python3 cross_substrate/calibration_anchors.py --run
PYTHONPATH=$HOME/fmexplorer/riemann_explorer \
  $HOME/fmexplorer/bin/python3 audit/phase5_runtime.py
```

### Blocker found while setting up (logged, not fixed) — `RUNTIME-1`
The canonical self-validation **would not run at all**: `cross_substrate/calibration_anchors.py` →
`import signal_gen` → `signal_gen.py:16` does `sys.path.insert(0, '$HOME/fmexplorer/riemann_explorer')` with a
**literal `$HOME`** (Python never expands shell vars in a string), so `import scanner` fails with
`ModuleNotFoundError`. `scanner.py` really exists at `$HOME/fmexplorer/riemann_explorer/scanner.py`.
**`signal_gen` has 16 importers** — this is a load-bearing module that is import-broken on a clean process.
Worked around non-invasively by adding the real path via `PYTHONPATH`. (See `06-fix-list.md` FIX-1.)

---

## Block 1 — Known-class confusion table (live instrument, N=3000, 6-seed mean)

Generators are the project's own calibrator zoo (`signal_gen.make_beta_ensemble_eigenvalues`,
`make_uniform_jitter`, `extractor_distinctness._gen_poisson`). Instrument = `cross_substrate/axes.py`.

| true class | I.5q ks_gue | I.5 ks_gue | W1δ(clock) | Brody q | BR ρ | **read as (marginal)** | pass? |
|---|---|---|---|---|---|---|---|
| clock (rigid) | 0.533 | 0.533 | **0.000** | 1.000 | 1.000 | rigid / picket | ✅ |
| GUE (β=2) | **0.033** | 0.023 | 0.358 | **1.000** | **0.999** | GUE | ✅ |
| GOE (β=1) | 0.094 | 0.086 | 0.442 | 0.876 | 0.978 | intermediate-Wigner | ✅ |
| GSE (β=4) | 0.045 | 0.060 | 0.283 | 1.000 | 0.999 | strong-repulsion Wigner | ✅ |
| uniform-jitter | 0.273 | 0.272 | 0.113 | 1.000 | 1.000 | near-rigid (BR-regime) | ✅ |
| Poisson | 0.284 | 0.284 | 0.736 | **0.006** | **0.093** | Poisson | ✅ |

**Family-I marginal verdict: 6/6 correct.** GUE→ks_gue≈0 + Brody q≈1; Poisson→Brody q≈0, ρ≈0; clock→W1δ=0.
The marginal instrument recovers every known class. This is also the **induction-on-noise pass on the marginal
axes**: Poisson reads Brody q=0.006 — it does *not* manufacture a Wigner/GUE class.

### …but the long-range Σ² column is INVERTED — `RUNTIME-2`

Same run, Family-II Σ²(L) column:

| class | Σ²(L=50) via calibrator (`unfold_unit_mean`) | expected |
|---|---|---|
| GUE (β=2) | **107.2** | small (~0.8; GUE is rigid) |
| Poisson | **55.1** | ≈ L = 50 ✅ |

GUE reads **more clustered than Poisson** — backwards. Confirmed by the same-input/two-unfolder micro-test
(`phase5_runtime.py` Block B):

```
GUE  Σ²(L) via unfold_unit_mean (CALIBRATOR path): 107.44   <- inverted
Poisson Σ²(L) via unfold_unit_mean              :  56.34   <- correct (~L)
```

**Cause (confirmed):** the calibrator unfolds eigenvalues with **global `unfold_unit_mean`**, which preserves the
**semicircle density gradient** of GUE eigenvalues; Σ²(L=50) then integrates over that gradient and inflates.
This is the Family-II "no internal renorm / wrong-unfold" deviation from `02-math §4` and `04-discrepancies` Bucket 4,
now **empirically reproduced**. The marginal NNS axes are immune (they're local), which is why Family I read GUE
correctly while Σ² inverted. (See `06-fix-list.md` FIX-2.)

---

## Block 2 — Rate-drift control (CV vs CV2/Lv) — **CONFIRMED**

Inhomogeneous Poisson, rate swept 0.1→2.0 over the window (slow single cycle); homogeneous Poisson control.

| input | n | raw global CV | I.10_cv (global) | **I.12_cv2** (robust) | **I.13_lv** (robust) |
|---|---|---|---|---|---|
| homogeneous Poisson | 4044 | 0.978 | 0.979 | 0.985 | 0.977 |
| **slow rate drift** | 4242 | **1.879** | **1.912** | **0.994** | **0.992** |

**Result: claim CONFIRMED, directionally and mechanistically.** Slow drift inflates global CV **~1.9×** while CV2/Lv
stay pinned at ≈1.0. The 1.9× lands at the low end of the documented "2–7×" range — expected, since my drift is a
single mild sinusoid; the documented epoch-gap concatenation (CV-16 artifact) is more extreme. The *correction* (CV2/Lv
rate-robustness) behaves exactly as documented.

---

## Block 3 — Induction-on-noise through the GUARDED long-range path — **CONFIRMED**

| input | guarded `longrange_verdict` | Σ²_obs (Poisson ref) | over-claims? |
|---|---|---|---|
| homogeneous Poisson | **POISSON_INDEP** | 54.0 (ref 42.2) | no — declines correctly ✅ |

The guarded path reads Poisson as Poisson; it does not manufacture a rigid/GUE class.

---

## Block 4 — Guarded GUE-pole recovery is lens-COVARIANT — `RUNTIME-3` (nuanced, not a bug)

Feeding a **clean** GUE (β=2, N=3000) to the guarded `longrange_verdict` and sweeping its unfolding degree
(the project's own `unfolding_sensitivity`):

| unfold_deg | Σ²_obs | verdict |
|---|---|---|
| 3 | 41.83 | **POISSON_INDEP** (calls GUE Poisson!) |
| 6 (default) | 15.85 | INTERMEDIATE |
| 10 | 4.23 | INTERMEDIATE |
| 15 | 1.22 | INTERMEDIATE |
| — | (true GUE ≈0.8) | `lens = COVARIANT, promotable = False` |

**Interpretation (honest):** on a semicircle-density GUE calibrator, Σ²_obs only converges toward the true GUE value
as the unfolding degree rises; the **default deg-6 under-unfolds** (reads INTERMEDIATE, not RIGID_GUE), and deg-3 is
actively wrong. **This is NOT a tool bug** — `longrange_verdict` + `unfolding_sensitivity` *correctly* report the lens
as COVARIANT and refuse to promote the GUE-pole call. The guarded path is epistemically careful. The actionable point
is comparative: the **calibrator** (`calibration_anchors`) runs *neither* the proper unfold *nor* the lens check, so it
would silently bank the inverted Σ²=107. Two takeaways for `06-fix-list.md`: (a) the calibrator should fingerprint
Family II through the guarded discriminator, not raw `unfold_unit_mean`; (b) the default `unfold_deg=6` is marginal for
clean GUE-pole recovery — worth documenting that semicircle-density inputs need a higher degree / the lens sweep before
any RIGID_GUE claim.

---

## Pass/fail summary

| check | result |
|---|---|
| Marginal known-class confusion (6 classes) | ✅ 6/6 correct |
| Induction-on-noise, marginal (Poisson ≠ GUE) | ✅ declines |
| Induction-on-noise, guarded long-range (Poisson→POISSON_INDEP) | ✅ declines |
| Rate-drift: CV inflates, CV2/Lv stable | ✅ confirmed (~1.9×) |
| Long-range Σ² on calibrator GUE | ❌ inverted (107>Poisson) — `RUNTIME-2` |
| Guarded GUE-pole recovery at default unfold | ⚠️ INTERMEDIATE / lens-COVARIANT — `RUNTIME-3` |
| Canonical self-validation runs at all | ❌ import-broken (`$HOME`) — `RUNTIME-1` |

**Bottom line:** the marginal instrument is empirically sound (6/6 + declines on noise) and the rate-robust correction
is real. The soft spots are all on the **long-range + self-validation** side: the canonical calibrator is import-broken,
and when forced to run it mis-unfolds the long-range column (GUE reads more clustered than Poisson). The *deployed*
verdict never touches long-range, so this doesn't corrupt shipped per-cell results — but it means the one artifact that
would catch instrument drift is itself broken and, when run, wrong on the axis that matters most for class-level claims.
