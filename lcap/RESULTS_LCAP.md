# RESULTS — Substrate-Aware L Policy

**Date:** 2026-08-16. **Brief:** `LCAP_BRIEF.md`. **Seal:** `lcap/prereg_sealed.json` (7 files
frozen). Run under Will's three conditions, with the ordering enforced in code.
**Instrument arc — no new science claims; no banked row re-verdicted.** *(Note: the arc RAN
propose-only. The split and the L policy were subsequently **adopted into
`cross_substrate/longrange_discriminator.py` on Will's explicit call** — see the adoption section
at the end.)*

## TL;DR

**The fix revealed more signal, not less.** Judged inside its own validity window, ζ_first_2000's
excess rigidity is **z = −9.10** — four times more significant than the **z = −2.33** it showed at
the deployed L=50. The large-L policy had been *diluting a 9σ effect down to 2.3σ* and then reading
it through a one-sided rule that had no name for it. Condition 3's alternative explanation
(*"the excess was an artifact of judging past validity"*) is **ruled out**: the effect is 3.6× the
minimum detectable at the capped L, and lens-invariant across deg 3/6/10/15.

**And the zoo gate caught something before ζ was ever touched:** at the deployed L=50, **GOE — a
genuinely different universality class — read `RIGID_GUE`.**

## Condition 1: the policy earned its trust on the zoo alone

The first zoo run **failed**. Across L = 3→50 the GUE band's spread grows ~5.7× while the GUE–GOE
gap grows only ~1.4×, so GOE's exclusion collapses from +7.4σ to **+1.8σ** and it lands inside the
band. That produced a **second cap, independent of the validity argument and derived entirely from
the zoo**: judging at large L destroys class discrimination *even where the GUE form is perfectly
valid*.

    L_judge(substrate) = min( deployed_L , validity_L , discrimination_L )

with `discrimination_L = 40` (largest L holding GOE out by ≥3σ, at that L and every smaller one).
Under the policy the gate passes on all six known-class members:

| member | L_judge | Σ² | z | verdict | expected |
|---|---|---|---|---|---|
| GUE (n=2000) | 40.0 | 0.817 | +0.70 | RIGID_GUE | RIGID_GUE ✓ |
| **GOE** | 40.0 | 1.275 | **+3.95** | **INTERMEDIATE** | NOT RIGID_GUE ✓ |
| Poisson | 40.0 | 36.51 | +253.7 | POISSON_INDEP | POISSON_INDEP ✓ |
| clock | 40.0 | 0.000 | −5.09 | HYPER_RIGID | HYPER_RIGID ✓ |
| jittered clock | 40.0 | 0.141 | −4.09 | HYPER_RIGID | HYPER_RIGID ✓ |
| Wigner-renewal | 40.0 | 6.33 | +39.8 | INTERMEDIATE | INTERMEDIATE ✓ |

Farey is **reported only** (Σ² = 16.19, INTERMEDIATE): its expected Σ² class is not independently
established, and letting an unestablished expectation adjudicate the policy would defeat the point
of the gate.

**Validity map (L0), literature-anchored or derived, never fitted:** ζ → 5.99 (Berry 1988,
saturation at ln(T/2π)); GUE n=2000 → 50, n=1200 → 30, **n=343 → 8.0** (derived: largest L within
10% of the Mehta asymptotic — note the gate's *own reference ensemble* goes out of window at small
n); Poisson and renewal → NOT_APPLICABLE (linear growth, no GUE window to cap); clock and jittered
clock → NO_GUE_WINDOW.

## Condition 2: the sealed direction held; the magnitude expectation did not

**Sealed before the run:** z(ζ) < 0 at L_judge, with z ≥ 0 halting as an inconsistency with the
banked lens-invariant measurement. **Held: z = −9.10.**

The seal also **disclosed in advance** that Will's *"at reduced significance"* expectation was
likely to be violated — the rigidgate arc had already measured ζ at L = 2…40 (z_d6 = −3.90, −6.07,
−4.40, −4.33, −4.76, −2.89, −2.57), which implies significance *increases* as L falls because the
band's sd shrinks faster than the deficit does. That disclosure was registered rather than
discovered: **significance increased ~4×.** The sign half — the load-bearing pre-commitment — was
untouched by the disclosure and held.

## Condition 3: the power number, computed before ζ

| substrate | L_judge | band | MDD (k=2.5) |
|---|---|---|---|
| ζ_first_2000 | 5.99 | 0.5169 ± 0.0359 | 0.0898 |
| GUE n=343 | 8.00 | 0.5654 ± 0.1094 | 0.2734 |
| GUE n=2000 | 40.0 | 0.7183 ± 0.1411 | 0.3527 |

ζ's measured effect is **0.327 against an MDD of 0.090 — 3.6× resolvable.** So the UNDER_RESOLVED
reading does not apply, and the two explanations condition 3 was built to separate are cleanly
separated: the excess is **not** an artifact of judging past validity (it grows when the artifact
is removed), and it is **not** a power limitation (it is 3.6× the resolution floor).

## Verdict: L_POLICY_FIXED

The cap fixes the physics **and** improves discrimination, at no power cost that matters — the
opposite of the L3 trade-off the brief was prepared to accept.

## The ζ row's own history, banked beside its value

Per Will's presentational requirement: *a row that has moved three times is trustworthy if the
moves are visible and merely unstable if they aren't.*

| # | date | reading | why it moved |
|---|---|---|---|
| 1 | 2026-06-04 | **"GUE confirmed at class level"** (RIGID_GUE at L=50) | the deployed one-sided rule returned RIGID_GUE and the prose read that as class confirmation |
| 2 | 2026-08-16 | **SUPERSEDED** | `RIGID_GUE` is one-sided and certifies "not floppier than GUE" — a clock earns it too; ζ sits *below* the band (z=−2.33), on the untested side |
| 3 | 2026-08-16 | **HYPER_RIGID, z = −9.10** at L=5.99 | judged inside its own Berry validity window under the zoo-validated policy; effect 3.6× resolvable, lens-invariant (deg 3→15: −8.94, −9.10, −9.10, −9.53) |

**What each move did and did not change:** the *measurement* never moved — ζ's Σ² deficit relative
to finite-N GUE has been present and lens-invariant at every L from 2 to 40 throughout. What moved
is the **scale it was judged at** and the **vocabulary available to name the result**. Move 1→2 was
a labeling correction; move 2→3 is a scale correction that *sharpened the same measurement* from
2.3σ to 9.1σ.

**What this does and does not say about ζ.** It says: ζ_first_2000 is measurably **more rigid than
the finite-N GUE ensemble**, robustly and at high significance, inside the window where the
comparison is meaningful. It does **not** say ζ violates GUE asymptotically — the
Montgomery–Odlyzko picture concerns T → ∞, these are the first 2000 zeros at T ≲ 2.5×10³, and slow
convergence of low-height ζ statistics to RMT is expected and documented. Naming that outcome is
the owning program's call; this arc supplies the number, the window, and the vocabulary.

**Unmoved rows:** Allen V1's "0/100 RIGID_GUE" is a negative result and the policy can only tighten
the rigid branch, so its direction cannot flip; not re-run. ~~brocot/golden unmoved~~ — **CORRECTED
by LC-ADD-1 below: under the n-dependent discrimination cap the brocot rows ARE outside their
window.** The claim here was derived from the validity cap plus the n=2000 discrimination constant,
which was the wrong form.

## Reproduction

`lcap/`: `validity.py` → `policy.py` → `zoo_validate.py` (gate, must pass) → `seal_prereg.py` →
`run_lcap.py` (refuses to touch ζ unless the gate recorded PASS) → `verify_lcap.py`.

---

## LC-ADD-1 (2026-08-16, Will's review) — the discrimination cap is n-DEPENDENT

**Three-event label.** (1) The sealed policy derived `discrimination_L = 40` at n_ref = 2000 and
applied it as a single global constant. (2) Will's review asked whether the small-n
reference-window finding needed its own check against the banked approximability rows, which run
at exactly that n — *"a third cap binding on the configuration those rows used."* (3) Measured: it
does, and **the sealed constant was wrong in form, not merely in value.**

| n | discrimination_L | why it moves |
|---|---|---|
| 343 | **5.0** | the GUE band's spread grows as n falls while the GUE–GOE gap does not |
| 1200 | 8.0 | |
| 2000 | 40.0 | (the sealed value — correct only at this n) |

**Consequence for the banked approximability rows — FLAGGED, NOT RE-VERDICTED, AND THE FLAG NAMES
EXACTLY WHAT IT IMPEACHES.** brocot/golden was judged at **L = 6.86 with n = 343**, where GOE is
separated by only **+2.14σ** against the required 3.0 — outside its own discrimination window. What
that does and does not touch, itemised, because a flag left as a general caution will be read six
months out as impeaching the row wholesale:

| component | status |
|---|---|
| the **measurement** (Σ² = 0.635 at L = 6.86, z = +0.49 vs its GUE band) | **STANDS** — untouched |
| the **`RIGID_GUE` label** read as *"not floppier than GUE"* | **STANDS** — that is what the branch certifies and the row satisfies it |
| the **GUE-vs-GOE discrimination** at that configuration | **UNSUPPORTED** — this and only this |

So the row is not impeached; one specific inference from it is. Re-judging inside the window
requires the substrate point set, which this arc does not hold — hence a flag for the owning
program, not a move. (My earlier report that "the policy does not move this row" was derived from
the validity cap plus the n=2000 discrimination constant; under the corrected n-dependent form it
does.)

**Registration (Will's addition, adopted).** The discrimination cap is **GOE-derived**: GOE is the
nearest neighbour in the zoo we have, not necessarily the nearest in the space. Recording the basis
means a future zoo member sitting closer to GUE at large L tightens the cap as a *refinement of a
stated basis* rather than an arbitrary-looking move.

## Adopted into the deployed module (2026-08-16, Will's call)

`cross_substrate/longrange_discriminator.py`: the **HYPER_RIGID split** is installed in `_judge`
(same formula, same 2.5 multiplier — the branch is split, not moved), and the **L policy** is
installed as `l_judge()` / `discrimination_L()` / `VALIDITY_L`, documented with its GOE basis.
The policy is deliberately **not wired into the default path**: call sites pass `L` explicitly and
silently re-scaling them would change banked outputs without a re-run anyone asked for. Verified
live on the deployed path: a clock now returns **HYPER_RIGID** (was RIGID_GUE); Poisson still
returns POISSON_INDEP; `l_judge(50, 2000, "zeta_first_2000") = 5.99 [validity]`;
`l_judge(6.86, 343, "gue_n343") = 5.0 [discrimination]`.
