# TIER B — COMPLETE 2026-07-31

All four ports left open at the 2026-07-29 reboot pause are done. **Every one
reproduced its banked `I.8_brody_q` bit-identically before its repaired values
were accepted** — that gate is the whole licence, and it was powered (verified
to fail on a 1e-12 perturbation and on a single dropped row) before being trusted.

| port | values | gate | bounded railed | median repaired | outside [0,1] |
|---|---|---|---|---|---|
| ibl | 1,141 | **EXACT** | 86.7% | −0.1708 | 87.8% |
| dual_region | 1,365 | **EXACT** | 98.6% | −0.4221 | 99.1% |
| buzsaki | 4,019 | **EXACT** | 99.4% | −0.5954 | 99.8% |
| hc3 | 923 | **EXACT** | 94.8% | −0.4816 | 96.4% |

**7,448 values this session; 17,030 in the store now carry
`I.8_brody_q_unbounded`.** Largest pileup on the repaired axis across the whole
store: 7 values (0.04%) — it does not rail. Rail audit: 9 flagged, 5 unresolved,
high-water 5, NO REGRESSION.

Every substrate reads the same direction once the bound is lifted: negative
median, i.e. clustered. That is the direction the bounded fitter structurally
could not express.

## Verifier

`cross_substrate/verify_brody_repair.py <substrate>` — the helper that lived in
`/tmp` and was lost twice. Now in the repo. Its rail criterion is the **largest
exact-value pileup**, matching `rail_audit.py`; a within-1e-9-of-a-bound test
reports 0% railed on data that is 86% railed, because the optimiser converges to
6.610696135189609e-05, just *inside* the declared bound rather than onto it.

## Corrections to the previous note

- **`--all` was never the ibl culprit.** `all_sessions` is accepted by argparse
  and never referenced in `run()`. The blowup (1,141 → 3,025) came from
  `IBL_GLOB` matching 8 cached NWBs while the bank covers only the 5 `sub-*`
  sessions. Reproduce with `--glob 'sub-*.nwb'`.
- **`--all` IS load-bearing for buzsaki** — opposite direction, same flag name.
  Omitting it writes ~820 rows from one session. Check the function body, not
  the argparse block.
- The previous note's per-port counts (~1,556 ibl, ~4,346 buzsaki, ~916 hc3)
  were **non-null bounded values summed across a port's files**, not row counts.
  Both are right; they are different quantities. Row counts are 1,141 / 4,019 /
  923.
- **hc3's producer is `cross_substrate/hc3_port.py`** (it was not unidentified),
  but it could not reproduce its own bank — see below.

## The mode-"w" hazard is now observed, not predicted

The first buzsaki run was killed mid-write by a reboot, leaving the files
truncated at 3,188/4,019 and 263/348. Recovery came from git HEAD and was
confirmed **byte-identical (SHA256)** against the out-of-repo baseline; a
full-store checksum then showed no collateral damage. Two independent recovery
paths, both intact. **Take the baseline before every port run:**

```bash
B=$HOME/fmexplorer/coordinate_baselines_$(date +%F)
mkdir -p $B && cp cross_substrate/coordinates/*.jsonl $B/
(cd $B && sha256sum *.jsonl > SHA256SUMS)
```

Note the two baseline naming conventions (`…2026-07-31`, `…2026_07_29`) do **not**
sort chronologically; select by mtime.

## Open, carried forward

1. **3,688 values still carry only the stale axis**, across 30 files. The
   substantive ones: `population-strat` 1,454, `pvc-11` 1,159,
   `ibl-port-cell-visual` 417, `quasiperiodic-operators` 216. The remaining 26
   files hold <110 each. This is the Tier C scope.
2. **`ec016.11/ec016.106`** (hc3, acquired 2026-06-04) is on disk and excluded
   from the bank. Incorporating it is an **extension**, a different operation
   from a repair, and needs its own gate. `hc3_reproduce_bank.py` excludes it by
   deriving the session list from the bank itself.
3. **The `s < 10` confound is measured on ibl only.** See
   `cross_substrate/BRODY_REPAIR_DIFFERENCES.md`: the repaired fitter changes
   three things, not one; on ibl the outlier-cut change moves the median +0.0067
   and flips 1.1% of signs, so the clustering direction survives — but exposure
   on dual_region, buzsaki and hc3 is unquantified.
4. **Population channel is non-deterministic.** `population_fingerprint.py:74`
   unfolds via `np.polyfit` (emits RankWarning); `I.9_berry_robnik_rho` moved in
   2 of 15 ibl pop rows across identical runs. `I.8_brody_q` did not move. Gate
   on the **cell** files.
5. `rail_audit.py --axis <one>` **ratchets the high-water mark down** to that
   single axis's count — it wrote 0 over 5 this session and had to be reverted.
   Run the full audit, or teach `--axis` not to write the manifest.

## Also open, from the overnight (unrelated to Tier B)

- **H2's definitive test** — Pass-E surrogate battery on `rep_int_signed_q`.
- **Unattributed constants** — swept this session, `/tmp/unattributed_constants_audit.md`:
  21 confirmed. Tier 1 is `approximability/depth5_q33215_floquet.py:35`, whose
  literal `W4` disagrees with the JSON beside it and **inverts** the depth-4→5
  result (ratio 1.0000335 "grows" vs 0.9999999988 flat). The deployed quadrant
  classifier's four thresholds (`arithmetic_toolkit.py:791-794`) have prose-only
  provenance.
- **R-177 class label** — scoped, `/tmp/r177_class_label_scope.md`. Verified
  1,658/1,660 = **99.88%** of BL cells clustered. The banked mitigation
  ("interior BL is genuine weak repulsion", `ESTIMATOR_CLAIM_PROVENANCE.md:41`)
  is **falsified**: interior BL is 335/337 = 99.4% clustered. Pooling ruled out.
  The gate cannot fail — `phase22a/verify_calibrators.py:66` has no clustered
  calibrator. Recommended fix and three decision inputs are in the report.
