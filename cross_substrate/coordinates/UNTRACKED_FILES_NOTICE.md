# ⚠ Six coordinate files are UNTRACKED — an overwrite here is NOT recoverable via git

**Found 2026-07-29 while running the Tier B recomputes (R-186).** Before launching the ports I
checked whether the coordinate store was git-tracked, so that a port opening its output with `"w"`
would leave a recoverable diff. I checked **five** files, found all five tracked, and concluded the
store was safe. **Six files are not tracked**, and `brocot-landscape.jsonl` — one of them — was
overwritten before I noticed.

| file | rows (pre-run) | ignored by |
|---|---|---|
| `allen-depth.jsonl` | 60,833 | `.gitignore:47` |
| `allen-depth-fam2.jsonl` | 60,833 | `.gitignore:48` |
| `allen-avalanche.jsonl` | 24 | `.gitignore:49` |
| `brocot-landscape.jsonl` | 4,292 | `.gitignore:54` |
| `goes-flares.jsonl` | 50,999 | (untracked) |
| `goes-flares-allfrm-contaminated.jsonl` | 220,548 | (untracked) |

**The ignores are deliberate** — these are large derived products, and `.gitignore:52` says brocot's
is *"derived; regenerable via brocot_landscape.py"*. So the exposure is **regeneration cost, not
data loss** for that one. Whether `allen-depth` and the `goes-flares` pair are equally regenerable
has **not been verified**.

## Baselines preserved

A pre-run copy of all six sits **outside the repo** (they are too large to commit — 63 MB — and
committing them would defeat the reason they are ignored):

```
$HOME/fmexplorer/coordinate_baselines_2026_07_29/   +  SHA256SUMS
```

## The lesson

> **"I checked five and they were all tracked" is not "the store is tracked."** A safety property
> asserted from a sample is not a safety property. Before any job that opens outputs with `"w"`,
> enumerate the **whole** target set and check each — the same positive-assertion discipline the
> `$HOME` audit needed (`negative_space_audit/`).

## On brocot specifically

Its row count moved 4,292 → 4,490 and the bounded axis did **not** reproduce — but that is **not**
caused by the Brody repair. The category enumeration itself changed (baseline 41 exemplars per
category, now 64), so the new file describes a **different object set**. No reproduction gate is
possible against the old file; the new values are a fresh computation and must be labelled as such,
not as a recompute of the banked ones.
