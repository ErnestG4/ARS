# Overnight 2026-07-28/29 — the locked findings, audited on the repaired instrument

**Thread taken:** the one I named when you asked whether the project has found anything anyone else
would want to know — *"run the four locked findings through the repaired instruments and the rail
audit, and see which survive."* Bounded, and it converts "probably fine" into an inventory.

**Everything below was sealed before it was run.** Three seals, one sealed re-registration. Two
verdicts reversed my own prior conclusions.

---

## The headline

**The four locked findings come out: 3 clean or restored, 1 flagged-but-not-downgraded, and one
number retracted outright.** Nothing was lost that was real; one thing was gained that wasn't there
before — a measured basis for each.

| finding | axis | rail exposure | verdict |
|---|---|---|---|
| **H1** OSI ↔ ks_gue_med | `ks_gue_med` | 0.05% pileup | **CLEAN — confirmed, not merely unchallenged** |
| **DSI** ↔ ks_gue_med | `ks_gue_med` | 0.05% pileup | **CLEAN** |
| **H2** population survival | `rep_int_per_q` | 20% railed | **EXPOSED but bias runs CONSERVATIVE → stays locked** |
| **F1/F0** ↔ rep_med | `rep_med` | **79–82% railed** | **Re-verified: contrast survives at 4.70σ → stays locked, structure restated** |

---

## 1. F1/F0 — the deciding measurement, and I was wrong twice

Both arms recomputed on the signed axis. **Reproduction gates passed exactly: pvc-11 to five
decimals, Allen 910/910.**

| axis | pvc-11 | Allen | Δρ | Fisher z |
|---|---|---|---|---|
| deployed (clipped) | +0.2983 (n=210) | −0.2016 (11/12 neg) | 0.4999 | +6.59 |
| **repaired (signed)** | **+0.1088 (p=0.116, ns)** | **−0.2502 (12/12 neg)** | **0.3590** | **+4.70, p=2.6e−06** |

**The substrate-systematic sign flip — the finding's actual claim — survives**, attenuated ~28%.
The Allen arm *strengthens* and goes to **12/12 sessions negative**.

**My two errors, both corrected in the record:**
- I concluded from the pvc-11 arm alone that F1/F0 *"must come off the locked list."* **Too harsh.**
  My seal scoped the test to one arm, and that scope was a limitation of the seal, not a licence to
  conclude about a finding whose claim is a *contrast*. Corrected in R-184 and propagated.
- I propagated the downgrade into three documents, then had to propagate the correction with the
  same energy an hour later. Leaving the harsher note because it was written first would have been
  exactly the stale-table failure this session has been cataloguing.

**What did genuinely change:**
1. **The pvc-11 arm alone is no longer significant** (+0.1088, p = 0.116). 82.4% of its cells sat on
   the clip's rail — the deployed correlation was carried by the 17.6% that escaped.
2. **The evidential structure is now Allen-arm-plus-contrast**, not two mutually-confirming arms.
3. **The quoted +0.388 is retracted** — see below.

---

## 2. ★ The headline number has no derivation (R-181)

**`+0.388` lives as a hardcoded entry in a dict named `PVC11_REF` at
`phase24/run_meta_analysis.py:127`. Nothing in the repo computes it.** The repo's own artifact
(`data/phase27_results/analysis1_verdict.json`) stores **+0.29834625**, which an independent
pipeline reproduces to **five decimals** at the matching n=210. **The banked figure overstates by
~30%**, and it was quoted in **three** documents including the locked-findings inventory.

**This surfaced because a seal fired and I honoured it.** The R0 gate required reproducing +0.388 to
±0.05; I got +0.2983 and declared the test **VOID as sealed** rather than waving it through. The
reference was then re-registered to the stored artifact under a **tighter** rule (3 decimals), with
the non-blindness disclosed. *The discipline that looks like pedantry was the detector.*

This is the third instance of the family — see `unattributed_constant` in memory.

---

## 3. ★ Exposure is not a verdict — the direction is finding-specific (R-183)

The **same rail**, on the **same field**, biased two findings in **opposite directions**:

| finding | how the rail enters | direction | outcome |
|---|---|---|---|
| **F1/F0** | 79–82% of cells pinned at 0; the correlation was carried by the 17.6% that escaped | **toward** the claim | arm collapses on repair |
| **H2** | criterion is `real > surrogate_p95`; a railed band is 0.0 and **cannot** exceed a positive p95 | **against** the claim | **railed bands survive 0.0%** vs 57.7% unrailed |

Verified `survives_rep` is exactly `real > p95` (1.000 agreement, 1,260 rows), then measured: 240
railed bands, **zero** survive.

> **A finding that survives a test biased against it is not undermined by that bias.** So H2 stays
> locked. Reading "exposed" as "probably inflated" would have downgraded H2 wrongly; reading it as
> "probably fine" would have kept F1/F0 wrongly.

H2's exposure is also far milder — **20%** of q-values railed vs pvc-11's 79–82%, median +0.50, 317
distinct values still present.

**H2's load-bearing statistic is not stated in `EPISTEMIC_STATE` at all.** I resolved it from code
(`phase22b/pass_e_tighten_seeds.py:111`) rather than defaulting to indeterminate — which is itself a
reportable defect in how findings are recorded.

---

## 4. Tier B — the structural repair (R-179)

`FAMILY_I` is the registry every port iterates. Adding `I.8_brody_q_unbounded` **there** means five
of seven ports emit it with no per-substrate edit — **12,170 of 19,619 values**. Only
`quasiperiodic_deepening` and `brocot_audio_harness` name axes explicitly and were patched by hand.

Verified the repair separates what the bounded fitter collapses: GOE 0.9999 → **1.0146**, GUE
0.9999 → **1.5362**, clustered 0.0001 → **−0.3439**.

---

## Still running / still open

- **qpo recompute** — relaunched detached after I discovered my earlier "completion" was **exit 124,
  my own 40-minute timeout**. Running, prints only on completion.
- **Tier B neural ports** — scoped and free-by-registry, not yet run (29 GB + 62 GB caches).
- **H2 definitive test** — needs the Pass-E surrogate battery re-run on `rep_int_signed_q`. Present
  result *bounds* the risk rather than removing it.
- **The +0.388 defect class** — worth grepping other `*_REF` constants for the same shape.

## State

Commits `cc4b981` … `2011636`. Tree clean. 22/22 fixtures, five watchers green, rail audit
5 unresolved (ratchet green). Three memory entries banked: `unattributed_constant`, the
exposure-direction lesson, and the rail-detection principle.
