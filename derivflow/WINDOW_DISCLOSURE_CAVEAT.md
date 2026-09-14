# The window disclosure quotes z(beta) from the wrong error model

**2026-09-14 04:08. Diagnostic, not a sealed measurement. FLAGGED FOR WILL — the
paper paragraph is committed (`be1823c`) and marked FOR REVIEW; it has not been
edited on the strength of this.**

## What I found

Stage 3b/3c compute z(beta) from the **fit covariance** with `absolute_sigma`
diagonal errors. `zbeta_correlated_error` established months ago that this is the
wrong error model for these curves: the 16 replicates are SHARED across k, with
median |r| of 0.875 (iid) and 0.729 (GUE) between k-pairs. The k* side of 3b/3c
is bootstrapped and unaffected. **The z(beta) side — the exact quantity the new
paragraph is about — is not.**

Four window cells at n=4096, 400 bootstrap resamples of the banked per-replicate
curves:

| window | z from covariance | z from bootstrap | ratio |
|---|---|---|---|
| (k_lo=1, sealed) | 9.31 | **8.15** | 0.87 |
| (k_lo=1, k<=11) | 10.99 | 12.82 | 1.17 |
| (k_lo=3, sealed) | 0.37 | 0.59 | 1.59 |
| (k_lo=5, k<=11) | 0.12 | **0.69** | 5.89 |

Two things follow.

**The sealed cell reproduces.** Bootstrap z(beta) = 8.15 at the sealed window
against `zbeta`'s independently computed 8.24 — a 1% agreement from a different
cell, which is the reassuring part.

**But the ratio is not constant: 0.87 to 5.89.** The covariance model most
understates z at the SHORT windows, exactly where the swing's denominator lives.
So the swing is inflated by the error model: across these four cells the
covariance range is 0.12–10.99 (92x) and the bootstrap range is 0.59–12.82
(**22x**).

## What this does and does not change

**Does not change:** the separation is robust (6–8%, bootstrapped throughout,
untouched). The classes separate under every window rule at every n.
RATE-SEED-DEPENDENT is not in question. The qualitative disclosure stands — the
significance IS window-dependent, by a lot, and the sealed window IS favourably
placed.

**Does change:** the headline number. "95.6x swing" is computed with an error
model known to be optimistic, and the optimism is window-dependent rather than a
constant factor, so it does not cancel. A bootstrap surface would likely quote
something nearer 20x. The paper currently says 95.6x, 108.9x and 15.1x.

**Scope of this diagnostic:** 4 cells of 45, one n, 400 resamples. It is enough
to show the ratio is not constant — which is the claim that matters — and not
enough to replace the table. Replacing it means a bootstrap z(beta) across the
full surface at all three n, which is a sealed cell, not a 4am patch.

## Why it is flagged rather than fixed

The paragraph is committed and marked FOR REVIEW. Editing a disclosure at 04:08
on a 4-cell diagnostic, in the same night I wrote it, is how a number that is
merely better-founded gets mistaken for one that is right. The correction wants
its own sealed cell with both edges declared and the error model as a TESTED
parameter — which is precisely the shape of defect this arc has spent a week
learning to declare rather than assume.

Related: `RECERT_CORRECTIONS.md` (twelve overstatements, same failure mode),
`verify_declared_params.py` (the error model is itself an undeclared parameter
of Stage 3b/3c).
