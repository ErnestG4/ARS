# RESUME — Tier B Brody recompute, paused for reboot 2026-07-29

**Nothing is in flight.** No compute was running when this was written; the reboot loses nothing.

---

## What is DONE (verified, committed)

The repair is at the registry — `cross_substrate/axes.py :: FAMILY_I` now contains
`I.8_brody_q_unbounded` — so any port that iterates `FAMILY_I` emits it with **no code edit**.
`I.8_brody_q` is retained bit-identical under its own key.

**8,972 values now carry the repaired axis:**

| substrate | n | reproduction gate | bounded railed | repaired median |
|---|---|---|---|---|
| **allen-hpf-cell** | 4,358 | **EXACT** | **100.0%** (4325/4326) | **−0.6125** |
| brocot.fm | 3,854 | *n/a — see below* | 6.9% | +0.1380 |
| ret1-cell | 325 | **EXACT** | 85.5% | −0.2644 |
| allen-hpf-pop | 255 | **EXACT** | 83.3% | −0.1854 |
| qpo-gaah + qpo-ext_harper | 180 | **EXACT** | 91.1% | −0.4108 |

`brocot.fm` is a **fresh computation, not a recompute** — its category enumeration changed
independently (41 exemplars per category → 64), so it describes a different object set and no
reproduction gate is possible. Do not report it as a recompute.

**The repaired axis does not itself rail** — the rail audit sees `I.8_brody_q_unbounded` in the store
and does not flag it, while `I.8_brody_q` still flags at 65.0%. Specificity confirmed on real data.

---

## What REMAINS

| port | values | command | notes |
|---|---|---|---|
| **ibl** | ~1,556 | `cross_substrate/ibl_port.py --run` | ⚠ **do NOT use `--all`** — see below. Run **alone**. |
| **buzsaki** | ~4,346 | `cross_substrate/buzsaki_port.py --run --all --workers 6` | 62 GB cache; biggest job |
| **dual_region** | ~1,365 | `cross_substrate/dual_region_port.py --run --workers 5` | streams DANDI 000638 over HTTP range; API verified reachable, 33-asset manifest present |
| **hc3-port-cell** | ~916 | *producer not yet identified* | was not in the six ports surveyed; find it before assuming coverage |

### ⚠ Two traps, both hit already

1. **`ibl --all` is the WRONG configuration.** It sets `visual_only=False` and writes a different
   object set (1,141 → 3,025 cells) into `ibl-port-cell.jsonl`. That is not a recompute of the
   banked file. Determine which configuration produced the banked 1,141 rows *before* re-running.
   The run also **crashed** (`BrokenProcessPool`, memory pressure alongside allen_hpf) — **run it
   alone.**
2. **Never `git add -A` while a port is running.** `f8e4982` did, capturing four coordinate files
   that had just been truncated to zero by `open(..., "w")`, and committed them empty (5,769
   deletions). Repaired in `135f32c`. **Stage explicit paths.**

---

## Safety notes that matter before the next run

- **Six coordinate files are UNTRACKED** (`.gitignore` 47–54 plus the `goes-flares` pair):
  `allen-depth`, `allen-depth-fam2`, `allen-avalanche`, `brocot-landscape`, `goes-flares`,
  `goes-flares-allfrm-contaminated`. An overwrite there is **not** recoverable via git. See
  `cross_substrate/coordinates/UNTRACKED_FILES_NOTICE.md`.
- **Pre-run baselines of all six live OUTSIDE the repo with checksums:**
  `$HOME/fmexplorer/coordinate_baselines_2026_07_29/` + `SHA256SUMS`.
  ⚠ **Also make a fresh full baseline before the next port run** — the `/tmp` copy used this session
  will not survive the reboot, and it was the only recovery path **twice** (brocot overwritten,
  ibl committed empty).

```bash
mkdir -p $HOME/fmexplorer/coordinate_baselines_$(date +%F)
cp cross_substrate/coordinates/*.jsonl $HOME/fmexplorer/coordinate_baselines_$(date +%F)/
```

- **Verification helper** used for every port (recreate if lost — it lived in `/tmp`): load the new
  and baseline jsonl, assert `I.8_brody_q` is bit-identical, report the new axis, the railed
  fraction, and the medians. The reproduction gate is what licenses the repaired numbers.

---

## Guard state at pause

- 22/22 fixtures; five watchers green.
- **rail audit:** 9 flagged, 4 resolved, 5 unresolved, ratchet green. `I.11_mass03` newly resolved
  `plausibly-legitimate-ambiguous` (72.9% zeros, **entirely brocot.fm**, 0.0% on every neural
  substrate; mass03 = mean(s<0.3), so 0 is correct for a rigid spectrum — a floor of the measure,
  not a clip). **Not fully settled** — confirming it needs the brocot spectra checked for genuine
  rigidity.
- migration ratchet 239 open, non-increasing.

## Also open, from the overnight (unrelated to Tier B)

- **H2's definitive test** — needs the Pass-E surrogate battery re-run on `rep_int_signed_q`. Present
  result *bounds* the risk (rail bias is conservative) rather than removing it.
- **The `+0.388` defect class** — worth grepping other `*_REF` constant dicts for the same shape:
  headline numbers with no live derivation.
- **The class-label problem (R-177)** — `BL = "Poisson noise"` is 99.9% clustered. Needs a new
  quadrant through a sealed re-registration; the largest single item on the board.
