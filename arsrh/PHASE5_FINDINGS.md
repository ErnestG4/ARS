# ARS-RH Phase 5 — HALTED AT GATE G2. No ζ reading was taken.

Seal: `seals/PHASE5_SEAL.json`, committed pre-run (`b5ac6fb`). Run: `phase5_attribution.py`,
output `phase5_attribution_measured.json`. §0 held.

**Honest state: COMPUTE-BLOCKED — no, INSTRUMENT-BLOCKED, and the block is my own gate design.**

## What happened

The seal's failure condition read: *"G2 fails → the decomposition cannot localize a KNOWN localized
signal; H_flat is uninterpretable; halt and report the instrument limit rather than a ζ result."*

**G1 PASSED.** The curvature-matched GUE bracket at N=500 has sd(L=1) = 0.0113, so the full-block gap of
0.0321 is 2.84σ per sub-block — above the sealed 2σ requirement.

**G2 FAILED.** The designed heterogeneous synthetic (sub-block 1 super-rigid, sub-blocks 2–4 GUE, on ζ's
exact-θ backbone) was not localized by the sealed criterion:

| sub-block | γ_mid | Σ² dev/sd @ L=1 | @ L=8 |
|---|---|---|---|
| 1 (super-rigid by construction) | 471.9 | **+0.94** | **−6.15** |
| 2 (GUE) | 1127.0 | +0.89 | +1.54 |
| 3 (GUE) | 1706.0 | −1.13 | −0.11 |
| 4 (GUE) | 2250.4 | −0.58 | +0.44 |

Sealed criterion: sub-1 < −3σ **at L=1**, sub-2..4 within ±2σ. Sub-1 gave +0.94. **FAIL.**

**The run halted. ζ was not read. P1's corroboration line is therefore still unre-derived.**

## Why it failed: the gate arm had no contrast, and this is the second instance this session

The criterion was written on **L = 1**, which is the L at which the designed contrast is smallest.
Measured directly (flat unit-density, 15 realizations each, N=500):

| L | GUE Σ² | super-rigid Σ² | **contrast** |
|---|---|---|---|
| 1 | 0.3423 | 0.3416 | **0.0007** |
| 2 | 0.4197 | 0.3426 | 0.0771 |
| 4 | 0.5004 | 0.3411 | 0.1594 |
| 8 | 0.5846 | 0.3406 | **0.2440** |

The contrast at L=8 is **364× the contrast at L=1**. A jittered picket fence and GUE have almost
identical number variance in a one-level window; the rigidity of a picket fence is a *long-range*
property (Σ² → 2η² = 0.18) and is invisible at L=1. **The sealed gate asked a question the designed
signal could not answer, at the one L where it could not answer it.**

**This is the same error as Task B's `P-B2-power`, in the same session.** There, the conjunction included
a Poisson arm against an *additive* artifact — an 8% effect, invisible by construction. Here, the gate was
placed at the L with 0.3% of the available contrast. Twice I sealed a power gate on the arm with the least
signal, and both times the substantive question was answerable on a different arm of the same measurement.
The Task B lesson as filed ("check each arm's power separately") was not enough to prevent the repeat: it
tells you to check, not what to check against. The operative version is **compute the expected contrast
for every candidate arm and gate on the maximum** — a number, produced before sealing, not a judgement.

## What is NOT claimed, and what I am not doing about it

- **The post-hoc observation is not a rescue.** At L=8 the decomposition *does* localize the designed
  signal cleanly: −6.15σ in the constructed sub-block against +1.54 / −0.11 / +0.44 in the three GUE
  sub-blocks. That is a good sign for the method. It is **post-hoc**, it was seen after the seal failed,
  and it cannot be used to score the seal. A seal edited after data is seen is void.
- **The gate is not being rewritten and the run is not being repeated in this phase.** The correct move is
  a **new seal** with the criterion on the contrast-maximising L, run as a fresh phase. That is queued,
  not done.
- **No ζ number was read and none is reported here.** The four ζ sub-block rows were never computed; the
  script exits at G2 before reaching them.

## Consequences that stand

1. **P1's arc-summary corroboration line remains unsupported.** Every number underneath it moved (short-L
   figures re-slotted to poly9 with the sign inverted; the long-L order-3 companion shown to be a
   fitted-unfold artifact), and the replacement bracket is still held. **Until Phase 5 re-runs under a
   valid gate, P1 is ONE WITNESS, UNCORROBORATED, and any summary saying otherwise overclaims.** It may
   well survive — the corrected readings put ζ more rigid than GUE, the same sign as P1, possibly a
   stronger corroboration than the original. That is a reason to measure it, not to assume it.
2. **G1's pass is a real, reusable result.** The curvature-matched θ-path bracket resolves to sd = 0.0113
   at N=500, so the sub-block decomposition has the separation it needs. The instrument is adequate; the
   gate was not.
3. **The pre-run reframe is untested.** The seal recorded, before running, that with an exact unfold
   fluctuation heterogeneity cannot manufacture rigidity (Σ² averages local Σ²), so the question is which
   height owns the excess rather than whether it exists. Nothing in this run bears on that either way.

## Scorecard

| gate / prediction | outcome | had power? |
|---|---|---|
| G1 separation | **PASS** (sd 0.0113, 2.84σ per sub-block) | yes — it could have blocked the phase |
| G2 powered falsifier | **FAIL** | **no — 0.3% of the available contrast at the chosen L** |
| H_bottom / H_flat / H_null / H_split | **not scored** — halt before ζ | n/a |

Two falsifiers fired in Task B against three catalogued inert ones previously. This one did not fire and
did not stay inert: it **mis-fired**, returning FAIL on a signal that was present and detectable 20 level
units away. That is a third category and it belongs in the catalogue alongside the other two.
