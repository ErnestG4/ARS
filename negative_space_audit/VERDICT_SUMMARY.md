# NEGATIVE-SPACE AUDIT — SUMMARY

**Design principle: DO NOT GREP FOR THE BUG. ENUMERATE THE RESOURCES AND ASSERT EACH RESOLVES.**

| cat | what | denominator | findings |
|---|---|---|---|
| **0** | canary | 2 planted | **2 detected — GATE PASS** |
| **A** | tilde/non-expanding idioms | 483 .py | **5** |
| **B** | data roots (positive) | 50 roots | **2 dead/empty** |
| **C** | absence claims in prose | 33413 docs | **239 to verify vs disk** |
| **D** | silent drops | 483 .py | **70** handlers, **11** loaders w/o counts |
| **E** | dormant gates | 483 .py | **0** |
| **F** | un-run preregs | — | see VERDICT_F |

*101.9s*
---

## THE FINDING — THE GENERATING EVENT, and it is ONE COMMIT

**`95b2324` (2026-06-03) — "Repo hygiene: de-identify hardcoded `$HOME` paths"**

```diff
- nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/...')
+ nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/...')
```

**72 files changed.** A de-identification commit find-replaced `$HOME` → `$HOME` **without
wrapping anything in `expandvars`**, converting every working absolute path in the repo into a dead
literal, in one stroke.

**The 2026-06-30 truth audit ran TWENTY-SEVEN DAYS LATER.** It found **one** symptom
(`phase24/loader.py:49`), fixed it, and **reported success**. It **never traced the generating commit**
— which was sitting in the history with *"de-identify hardcoded `$HOME` paths"* in its subject line.

> **THE 22 "INSTANCES" WERE NEVER 22 MISTAKES. THEY WERE ONE COMMIT AND 22 SYMPTOMS.**
> **The audit found an instance and never asked for the generating event.**

**New doctrine line (the operational form):**
> **When you find a defect, ask `git log -L` for the commit that INTRODUCED it. If one commit
> introduced N instances, fixing one is not a fix — it is a SAMPLE.**

### The reproducibility consequence (worse than the paths)

`phase24/run_per_session_h1.py:115` — the script that **generated `per_session_h1_ars.parquet`**, the
banked data the entire 32b audit rests on:

```python
nwb_path = Path(f'$HOME/.../session_{sid}.nwb')
if not nwb_path.exists() or ...:
    print(f"  session {sid}: NWB not ready; skip")   # <-- fires for EVERY session, forever
    continue
```

**The gate can never pass.** And `phase24/loader.py:49` — the one the audit *did* fix — is **never
reached**, because the guard skips first. The banked parquet (May 10, run-log shows sessions loading
cleanly) **predates the hygiene commit**, so **the DATA is valid — but the CURRENT CODE CANNOT
REPRODUCE IT.** It would emit `"NWB not ready; skip"` for all 26 sessions and produce nothing, while
printing a message that reads like a benign data-availability notice.
**A silent-skip masquerading as an absence claim — Category D and Category C in the same three lines.**
**FIXED** (5 f-string sites, `phase24/`).

### dr-port — **THE PREDICTION IS FALSIFIED**

Predicted: *"dr-port is a dead loader, not a remote dataset. Base rate 22/22."*
**Wrong.** `open_dandi_asset` → `resolve_dandi_url` → genuine HTTP-range streaming. No `000638` cache
exists, no dead loader. **Positive assertion: DANDI 000638 is REACHABLE — 33 assets, first is 32.5 GB.**

**But the positive audit found what the grep would not have:** *"remote-streamed"* is an **accurate**
absence claim that has been **treated as a blocker when it is a COST.** dr-port is **runnable** — it
needs network time, not new engineering. **n can go from 6 to 7.**
