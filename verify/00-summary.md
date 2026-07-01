# Overnight Verification — Summary

Follow-on to the ground-truth audit (`audit/`). Question: did any audit-flagged code defect actually **move a
banked result**? Method: verify-first — recompute the affected estimator on the **same cached inputs** with
corrected/canonical parameters and **diff against banked**, each harness gated by a validation check that it
reproduces the banked value under the *original* parameters before any diff is trusted. No driver was edited.
Harnesses + raw output: `verify/tier1_*.py|md`, `verify/tier2_*.py|md`, `verify/tier3_*.py|md`.

## Headline: no banked *conclusion* is corrupted. Two quantitative caveats + one real (unbanked) bug.

| tier | finding tested | validation | verdict on banked results |
|---|---|---|---|
| 1 | L-function NNS guard drift (FIX-4) | PASS (repro matches banked) | **ROBUST** — claims survive; guard drift is substrate-*necessary* |
| 2 | long-range Σ² unfold (FIX-2/7) | PASS (flat-Poisson control agrees) | **verdicts safe**, but Σ² *magnitudes* unfold-dependent |
| 3A | chirp GUE unfold (FIX-3) | repro validated | **bug confirmed** — but script banks nothing |
| 3B | phase20/21 JPF_CAP drift (FIX-5) | PASS (cap-1500 reproduces banked) | **material but tiny** — 3/146 dense windows |

---

## Tier 1 — L-function guard (`tier1_results.md`)
The `0.5`-guard admits 29/43 Farey bands canonical drops (fc_ref=1.0, f_pll∈[0.125,8]). Re-pooling under canonical:
- **lmfdb_family / lmfdb_extend / dirichlet_family:** every group stays `best=GUE`, gap essentially unchanged
  (family +0.065→+0.068; Dirichlet real(Sp)/complex(U) both +0.067), **despite the canonical pool being ~80% smaller**
  (2.5M→493k events). Katz–Sarnak root-number & Sp/U separations are **guard-invariant**.
- **Mertens/Liouville:** `fc_ref` is huge (Liouville ≈9.06M) so the canonical *audio* Nyquist cap (19845) drops **all**
  bands → Liouville `insufficient`. This proves the `0.5`/no-upper-cap guard is a **necessary arithmetic-substrate
  adaptation**, not a bug — the audio constants can't transfer. **FIX-4 downgrades**: consolidate to a
  substrate-parametrized guard, but nothing is wrong in the banked numbers.

## Tier 2 — long-range Σ² unfold (`tier2_results.md`)
Flat-Poisson control: unit-mean and guarded agree (Σ²≈L) ✅. Across all exposed sites:
- **Every verdict is lens-INVARIANT** (identical across unfold_deg 3/6/10/15) — mertens SUPER_POISSON, brocot-golden
  RIGID_GUE, allen/pvc-11 SUPER_POISSON, etc. **No substrate's pole classification is an unfolding artifact.** The
  feared GUE→SUPER_POISSON *inversion* (audit/05 calibrator) does **not** occur on these real inputs — the
  density-adaptive lens neutralizes the trend.
- **But Σ²(L) magnitude is unfold-sensitive** at nearly every site (0.19×–1.61× between unit-mean and guarded;
  direction varies with density structure — mertens unit-mean *inflates* 1.6×, allen/pvc-11 unit-mean *under-reads*
  ~3×). **Actionable:** any claim quoting an **absolute** Σ²(L) on these substrates should use the guarded lens; the
  pole/verdict claims are safe. Liouville is UNDERPOWERED (n=133<200), not an unfold issue.

## Tier 3 — chirp GUE bug + cap drift (`tier3_results.md`)
- **3A (FIX-3 confirmed):** the global-mean unfold measurably corrupts the GUE reference — at the script's actual N=100
  (seed 42): `I5_ks_gue` 0.103 (global-mean) vs 0.068 (semicircle fix); CV 0.594 vs 0.444 (GUE surmise ≈0.42). The
  corruption is in the edge eigenvalues; `run_chirp_prediction` uses *untrimmed* spacings so its deployed GUE reference
  is the corrupted one. Mitigant: the script **banks nothing** (stdout only), so no stored result is affected — but any
  printed GUE prediction used a bad reference.
- **3B (FIX-5 material, small):** phase21 has 146/250 windows >1500 events (decimation actually fires). Re-running the
  classify path verbatim: cap-1500 **reproduces the banked `primary` exactly** (0/146 differ — replication validated);
  at cap-5000, **3/146 windows flip BL→TR** (GRB230307A @26s/@28s, GRB221009A @180s — all 77k–712k-event windows).
  phase20 (no cap in unfold) is cap-insensitive (0/64). So: deployed classification matches its banked output; the real
  issue is that the classifier (1500) and its calibrators (5000) would **disagree on ~2% of the densest GRB windows**.

---

## Net effect on the fix list
- **FIX-4** → downgrade to "consolidate to a substrate-parametrized guard"; **claims verified robust**, not corrupted.
- **FIX-2/7** → sharpen: the risk on real substrates is a **wrong Σ² magnitude**, not verdict inversion; still fix the
  un-asserted unfold, and re-quote any absolute-Σ² claims through the guarded lens.
- **FIX-3** → confirmed real with numbers; low urgency (unbanked), still worth fixing the reference.
- **FIX-5** → material but small; the fix (unify `JPF_CAP`) matters most for classifier-vs-calibrator consistency on
  dense windows. Re-classify those 3 GRB windows after unifying.
- No new P0s. The audit's P0 correctness set (FIX-1/2/3) stands; none of them silently corrupted a banked conclusion.
