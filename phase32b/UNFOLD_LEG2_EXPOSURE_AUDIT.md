# Leg-2 (unfold) exposure audit of the ARS event-set path — for the §7.ter.50 retro-scope

**Status: exposure audit + mechanism calibration. NOT a gate.** No result here certifies 32b.
Feeds `PROPOSED_7TER50_RETROSCOPE.md` (which was written when reliability was the *only* reason)
and the §8 backfill spec. Doctrine: `TOOLKIT.md` §9 admissibility gate, Leg 2.

## 1. The call site — CONFIRMED (this was the open state claim)

`phase24/run_per_session_h1.py` (sys.path→`phase22a`) → **`phase22a/ars_classify.py::classify()`
line 72: `ev_unit = unfold_unit_mean(events)`** — unconditional → `unfold_unit_mean()` lines 37–48.

Both Leg-2 failure modes are present, and one is *worse* than the Phase-38 ledger path:

- **Mode 1 — circularity (unconditional).** Line 48: `sp / sp.mean()` — divides by the per-call
  mean spacing **self-derived from the very data being classified**. Fires on **100% of cells,
  regardless of n.** This alone fails Leg 2.
- **Mode 2 — stride decimation.** Lines 46–47: `if sp.size > cap: sp = sp[::max(1, sp.size//cap)]`
  with **`JPF_CAP = 1500`** (line 34) — *not* the 5000 of the Phase-38 measurement.

## 2. Exposure (read from banked `data/phase24_results/per_session_h1_ars.parquet`, no recompute)

`n_events_used` is the **post-decimation** unfolded size (attribution-slot checked at the return
site: `n_in` = raw events pre-unfold; `n_used` = `ev_unit.size`).

| | |
|---|---|
| cell × condition rows | 939 |
| `if nsp>1500` triggers | 705 (75.1%) — **but 159 are stride-1 no-ops** (`sp[::1]`) |
| **genuinely decimated (stride ≥ 2)** | **546 / 939 = 58.1%** |
| median stride among those | **5** (mean 7.1, **max 48**) |
| stride ≥ 10 | 119 cells (12.7%) |
| median decimated cell retains | **20% of its spacings** (worst: 2.1%) |
| worst cell | 72,985 events → 1,522 used, **stride 48** |

**Not used as a natural experiment.** The fired set is *defined* by n>1500, hence perfectly
confounded with n (Phase 38 already caught n as a hidden driver once). No `rep_med` comparison
across that split is made or licensed.

## 3. Mechanism, measured on analytic ground truth (`sessionK/farey_stride_calibrator.py`)

Farey is the one substrate where the instrument can be pointed at itself against a known answer
(ρ≈1 by construction, no reliability confound). Pipeline validated: reproduces the banked
`⟨r̃⟩_true = 0.7051`, `⟨r̃⟩_iid = 0.6120`, gap `+0.0931` **exactly**.

Swept at the **strides actually present in the ARS data (2–48)**, with an **n-matched** marginal
control (KS(decimated, full) vs KS(random-subsample-of-same-n, full) — a fixed KS threshold is
invalid, KS scales ~1.36/√n):

| stride | ⟨r̃⟩ | % correlation-gap destroyed | KS(dec) | KS(rand-subsamp) | p |
|---|---|---|---|---|---|
| 1 | 0.7051 | 0% | 0.0000 | 0.0000 | 1.00 |
| **2** | 0.5977 | **+115%** | 0.0000 | 0.0011 | 1.00 |
| 3 | 0.6447 | +65% | 0.0008 | 0.0019 | 1.00 |
| **5** (ARS median) | 0.6342 | **+76%** | 0.0042 | 0.0027 | 0.16 |
| 10 | 0.6167 | +95% | 0.0042 | 0.0039 | 0.49 |
| **48** (ARS max) | 0.6222 | **+89%** | 0.0118 | 0.0084 | 0.17 |

**VERDICT (i) — stride hypothesis CONFIRMED. The corruption is CORRELATION-SPECIFIC.**
The consecutive-pair statistic collapses to (and past) its iid value; the **marginal is untouched**
(every KS matches its n-matched control, all p ≫ 0.05).

## 4. What this kills, and what it predicts

**(a) "Lower bound" is FALSIFIED — the phrase must NOT enter the retro-scope.** It assumed
corruption is monotone in stride aggressiveness. It is **not**: corruption **saturates at stride 2**
(115% destroyed) and is thereafter flat/noisy (65–98%). The harm is a **cliff, not a gradient**, so
Phase-38's 5000-cap numbers are *not* a lower bound for the 1500-cap path. (Claim raised, tested,
retracted.)

**(b) The exposure reads worse, not better.** Because the cliff is at stride 2, the 58.1% of cells
with stride ≥ 2 have their consecutive-gap correlation **essentially destroyed**, not partially
degraded.

**(c) Predicted asymmetry between the two banked axes (testable):** `rep_med` (repulsion integral —
consecutive-pair sensitive) should be **corrupted** on those 546 cells, pulled toward its
iid-marginal value; `ks_gue_med` (a marginal KS) should be **comparatively spared**. The two banked
32b axes are therefore *not equally damaged*, and a retro-scope that treats them identically will be
wrong in a specific, checkable way.

## 5. Scope — what this does and does not license

- **Establishes the mechanism** on Farey (ground truth). **Does not quantify the Allen-specific
  bias** — spike-train correlation structure differs. Quantifying it requires the **within-cell,
  decimation-on/off, same-cells recompute** (the backfill), not a read.
- **Does not certify or reprieve 32b.** Mode 1 is unconditional; `rep_med`/`ks_gue_med` are
  **Leg-2-failing at the call site**, verified in the ARS path specifically. Only the *magnitude* was
  open, and it is now bounded below by "58% of cells, correlation destroyed."
- **Backfill spec (§8 item a):** must re-run with **decimation disabled AND the normalizer fixed**
  (external rate, not `sp.mean()`), and must **re-measure** exposure rather than inherit Phase-38's
  5000-cap numbers.
