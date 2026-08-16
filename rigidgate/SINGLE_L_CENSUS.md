# Single-L Σ² Gate Census

**Date:** 2026-08-16. **Why:** the RIGID_GUE arc's F4 finding — a marginal-**exact** construction
(a permutation of an iid Wigner spacing draw, so its NNS is identical by multiset identity) tuned
to f\* ≈ 0.056 sits **inside** the GUE band. No rule built on Σ² at a single L can exclude it,
because it matches on both measured quantities. That is not a footnote to the RIGID work: it is a
standing property of **every single-L Σ² call site in the repo**, so the first step is knowing
which they are. Census scope: all call sites of the long-range statistics
(`II1_sigma2_at_L`, `II2_delta3_at_L`, `longrange_stats`, `longrange_verdict`) at head.

## Census — 6 gate call sites, **all single-L, none sweeps L**

| # | call site | L policy | consumes | exposure |
|---|---|---|---|---|
| 1 | `cross_substrate/longrange_audit.py:36` | **fixed `AUDIT_L = 50.0`** for every row | verdict → the banked arithmetic rows (ζ, L-functions, pooled) | **highest** — one fixed L across heterogeneous substrates |
| 2 | `cross_substrate/longrange_allen_audit.py:73` | fixed `L = 50.0` | verdict → "0/100 Allen V1 cells RIGID_GUE" | high (a *negative* result, so a spoof would have to manufacture rigidity, not hide it) |
| 3 | `cross_substrate/longrange_allen_psth_audit.py:78` | fixed `L = 50.0` | verdict → PSTH-unfold audit | high |
| 4 | `cross_substrate/trial_psth_unfold.py:124` | caller-supplied single `L` | verdict | medium |
| 5 | `rf_lenses/threadE_universality_diff.py:36-37` | `matched_L` default (single) | Thread-E lens comparison | medium |
| 6 | `rf_lenses/threadE_figure.py:12` | `matched_L` default (single) | figure | low (descriptive) |
| — | `audit/phase5_runtime.py:85,94` | default (single) | audit-of-the-audit, not a banked claim | n/a |

**Multi-L call sites: zero.** `longrange_verdict` computes Δ₃ alongside Σ² at the *same* L and
uses it only as a secondary readout (`primary = s2j["verdict"]`), so the second statistic is
present but not conjoined — the gate is single-L **and** effectively single-statistic.

## What the exposure actually is (stated precisely, not alarmingly)

The spoof is **adversarial**: it requires a construction that knows the gate's L. No natural
substrate does this, and nothing in the census is evidence that any banked row is wrong. What the
census establishes is a **scope bound**: every RIGID_GUE row in the repo certifies *rigidity at
one scale*, and none of them certifies *class* against a constructed alternative. Rows 2–3 are
additionally insulated by direction — they are negative results, and the spoof manufactures
rigidity rather than concealing it.

The sharper practical worry is not adversaries but **scale policy**: row 1 uses a fixed L=50 for
every arithmetic substrate. For ζ at height T ≈ 2.5×10³ the Berry saturation scale is
ln(T/2π) = 5.99, so the banked ζ row was judged at **8.3× its own saturation scale** (measured at
that exact configuration: Σ² = 0.313, band 0.765 ± 0.194, **z = −2.33**). A fixed L cannot be
right for substrates whose GUE-validity windows differ by an order of magnitude.

## Proposed hardening, in priority order (for the owning program)

1. **Substrate-aware L** — replace the fixed `AUDIT_L` with a per-substrate cap at its own
   validity scale (for ζ-like substrates, L ≲ ln(T/2π)). This is the cheapest change and it fixes
   the real-world issue, not the adversarial one.
2. **Conjoin Δ₃** — it is already computed at every call site and currently discarded as
   secondary. See the registered-open on the Δ₃ variant: at a substrate-aware L it may dominate
   the current gate on both axes.
3. **Two L values** — the minimum that converts "rigidity at a scale" into a statement about
   growth; the RIGID_GUE arc measured the power cost of doing this naively (a 2× lever is
   underpowered on Σ²; Δ₃ is 12:1 and does the job).
4. **Record the adversarial bound** in the module docstring so the scope travels with the code.

Generator for the ζ-at-banked-config numbers: `rigidgate/gate_probe.py` (`bands`, `sigma2`);
config L=50, n_ref=2000, deg 6.
