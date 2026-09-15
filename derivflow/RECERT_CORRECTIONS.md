# Recert series — corrections, 2026-09-13

An independent audit of the series' own commit messages, checked against the banked
artifacts. Every item below was re-verified before being written down. The commits
stand as written; this document is the correction, because deleting a claim removes
the evidence that it was made.

---

## 1. "the Richardson bias is +0.73%" — WITHDRAWN. It is a noise draw.

Claimed in `89354ae` and re-quoted in `b8789f3`, `f608830`, `df53435`.

The banked Richardson bias at the science's operating point (eps/Delta = 0.704,
k = 64) by eta:

| eta | 1e-5 | 1e-4 | 1e-3 | 1e-1 |
|---|---|---|---|---|
| bias | **-0.645%** | **+0.727%** | +0.026% | -7.70% |

Gate D's 1-sigma at that window is **0.792%**. The readings are ~1 sigma and they
**change sign**. A fluctuation-damping bias is eta-independent by construction; an
additive offset scales as 1/eta. Neither describes this.

**Supportable statement:** *no bias is resolvable at the centre; |bias| < 0.79%
(1 sigma).* The VERDICT (`NO_RESOLVABLE_BANDWIDTH_BIAS_AT_THE_SCIENCES_OPERATING_POINT`)
was always correct and conservative. The prose around it was not.

**Consequence:** `STAGE1 = 0.007265`, typed into Stage 2a as a reference value, is a
noise draw given the standing of a measurement. `b93df29` flagged it as
"typed not read"; it is worse than that -- it should not have been a number at all.

## 2. Stage 1's eta = 0.1 column measures the TRUTH FORMULA failing, not the instrument.

`1-<r~> = (2/sqrt(pi))*eta` is leading order. Independently measured relative error
of the closed form: +0.027% (eta=1e-5), +0.019% (1e-4), -0.061% (1e-3), -0.843%
(1e-2), **-7.55% (1e-1)**. Stage 1 reads -7.69% at eta=0.1.

So ~98% of that column is the closed form breaking down. `knownanswer.py`'s own
docstring says to certify above ~1e-2 with `truth_by_simulation`, and the cell swept
1e-1 anyway without doing so. **That column is unreadable and nothing in the cell or
the checker says so.**

## 3. Gate D's blindness DEMONSTRATION is vacuous. The conclusion survives; the proof does not.

`verify_knownanswer.py` section 4 applies `p = np.arange(N+1) * (1.0 - damp)` -- a
**common rescaling** -- and reports the picket fence "unmoved to 1e-12". But
`r~ = min/max` is invariant under common rescaling on ANY configuration: applying the
same rescaling to a DISORDERED perturbed lattice moves the statistic by 0.0-3.4e-15.
So section 4 cannot discriminate ordered from disordered and demonstrates nothing.
Its "unmoved" is 0/0 float noise on a statistic that is identically zero.

The real mechanism is different and is still correct: **an ordered configuration has
no fluctuation to damp.** Verified separately -- the damping map
`s -> 1 + (1-d)(s-1)` moves the disordered statistic by exactly -1.00%/-17.00%/-50.00%
at d = 0.01/0.17/0.50, and leaves the picket fence identically 0.

`knownanswer.py`'s module docstring carries the same conflation and is wrong as
written. **Conclusion unchanged, argument replaced.**

## 4. Stage 2a: "+20.2% at 0.95" understates the artifact by 48x.

`3be4d7e` reported the primary panel only. The same cell (pos 0.95, size 0.05) at
**eps/Delta = 2.0, eta = 1e-5 reads +965.94%** -- and 2.0 is INSIDE the science's own
span of 0.704-4.031. The banked `section_spread` of 0.2184 is the primary panel;
across all 180 cells it is **9.687**.

## 5. Stage 2a: the "|pos| = 0.70 boundary" is not an instrument property.

The edge defect is a fixed ABSOLUTE offset of ~2e-5, not a relative bias. The
"boundary" is simply where that offset crosses the 5-sigma RELATIVE resolution at the
chosen eta: at eta = 0.01 there is no boundary anywhere out to 0.95, and at eta = 1e-6
the whole support would fail. **It is contingent on eta = 1e-4 and eps/Delta = 0.704,
and must not be quoted as "where the instrument stops being trustworthy" or used to
put a number on EDGE-0.**

## 6. Stage 2a: THREE TABLE ROWS ARE THE SAME WINDOW. A real bug in `section_idx`.

`section_idx` clamps `lo` to `m - w`, so distinct requested positions collapse:

| size | distinct windows actually measured |
|---|---|
| 0.2 | pos 0.0, 0.25, 0.5, 0.7 separate; **pos 0.85 and 0.95 are the SAME window** |
| 0.4 | pos 0.0, 0.25, 0.5 separate; **pos 0.7, 0.85 and 0.95 are ALL the same window** |

That is why `3be4d7e`'s table shows identical +4.62% twice and +2.35% three times: it
is one window reported repeatedly, presented as independent positions. The C3 arm is
decided by the size-0.2 column, where it has **one** distinguishable failing cell, not
two. The size-0.4 cell labelled |pos| = 0.70 is centred at 0.60 with its outer edge
flush against the support endpoint.

## 7. "Stage 1 found ZERO bandwidth dependence with a perfect reference" — FALSE off-centre.

Claimed in `b8789f3` and `df53435` as the framing premise for Stage 2b. Stage 2a's own
artifact shows the edge offset growing **~4.5x** from eps/Delta = 0.704 to 2.0 with the
analytic reference. **Stage 2b's reconciliation logic rests on a premise that Stage 2a
had already falsified.**

## 8. Stage 2b: "an ADDITIVE FLOOR" — REFUTED. The behaviour is QUADRATURE.

At eta = 0.01 the truth (1.128e-02) exceeds the floor, so the model is testable:

| n_seed | observed | quadrature | additive |
|---|---|---|---|
| 1024 | 1.2754e-02 | 1.2631e-02 (**-1.0%**) | 1.6959e-02 (+33.0%) |
| 4096 | 1.1493e-02 | 1.1586e-02 (**+0.8%**) | 1.3911e-02 (+21.0%) |
| 8192 | 1.1305e-02 | 1.1424e-02 (**+1.1%**) | 1.3070e-02 (+15.6%) |

The finite reference injects an INDEPENDENT gap perturbation delta that adds in
QUADRATURE: reading = C*sqrt(eta^2 + delta^2), with delta ~ 2.33e-3 at n_seed = 4096.
The implied deviation varies by 85x across eta at n_seed = 8192 -- an additive floor
varies by 1x. The claim looked true only because it was read at two eta where the
truth already sits far below the floor, which makes the agreement circular.

**This changes the reach argument.** Under quadrature a residual uncorrelated delta
still contributes sqrt(eta^2 + delta^2), so the science's ability to read 1e-5 has to
be argued about delta_residual, not about "the floor is absent".

## 9. `df53435` READ AN ARM ITS OWN LATTICE DECLARED UNREAD.

The artifact's `composed.unread` contains BOTH `'fitted exponent of |bias| against
n_seed'` and `'bandwidth spread of |bias| at n_seed = 4096'`. The commit disclaimed
only the second, and headlined the first: *"C2 is the one arm here that means what it
says"*. **A failed premise makes every non-premise arm unreadable; that is the entire
purpose of the lattice, and I overrode it in prose.** The -0.583 exponent is withdrawn
as a reported result. (It is also a point estimate with no error bar, ranging -0.533
to -0.590 across the other bandwidth nodes.)

## 10. Stage 2b's "overstates the science" argument is HALF sound.

Sound: a floor is a lower bound on the reading, so the science reading 8.2e-05 at
k = 64 does establish that it does not carry a 2.6e-03 floor.

Not sound: that bounds the floor's SIZE, not its EXISTENCE. A residual floor of, say,
5e-05 is consistent with everything measured and would still swallow the k = 64
reading. Getting from 2.6e-03 to below 8.2e-05 requires cancelling >=97% of the
reference's sampling error -- **asserted, never measured**. And the proposed mechanism
is a global-to-local inference: a reference that tracks the configuration's DENSITY
need not track its LOCAL gap fluctuations, which is what generates the floor.

## 11. `verify_recert.py` cannot see any of items 1, 2, 4, 5, 8.

It reads only the primary slice (`eta_primary`, `eps_nodes[0]`), so the +965.94% cell
and the sign-flipping eta column are never touched. It re-derives resolutions from the
identical expression that produced them, so it verifies a copy rather than a
correctness. Its continuity check passes on two readings that **disagree in sign**
(-0.121% vs +0.727%) because the bar is 2.25 sigma of their combined error. And
**Stage 2b has no checker at all** -- `recert_finite_seed.json` was banked after the
checker was written and never added.

## 12. Stage 1's C3 value is RAILED.

"largest eps/Delta still within the gate's resolution = 4.50" is the top of `EPS_GRID`.
It is where the sweep stopped, not where the valid region ends. `verify_recert`
reproduces it faithfully and does not flag the rail -- the exact defect `railed.py`
exists to catch, in a cell that does not use it.

---

## What survives, unchanged

- **`NO_RESOLVABLE_BANDWIDTH_BIAS_AT_THE_SCIENCES_OPERATING_POINT`** — the verdict is
  correct and was always the conservative reading. Only the quoted magnitude was wrong.
- **`FLATNESS_IS_AN_ARTIFACT_OF_THE_CENTRAL_WINDOW`** — the verdict is correct and
  UNDERSTATED. The artifact supports it far more strongly than the commit claimed.
- **Gate D is blind-discriminating in the right direction** — ordered configurations
  cannot see a fluctuation-damping bias. Only the demonstration needs replacing.
- **Stage 2b composed INVALID and that was right.** Its premise failure is what makes
  items 8-10 corrections to prose rather than to a standing verdict.
- **Stage 3 is untouched by all of this.** It refits the sealed science on shared
  windows with the instrument pinned; none of the above enters it.

---

# Items 13–15, added 2026-09-15 on Will's review of the overnight

## 13. Stage 3d's P2 "cross-cell reproduction" — the shared surface was never itemized.

8.282 vs 8.242, different cell, different resampler, different night, reference
READ from the artifact. The hygiene is right. But "independent" was doing work
that had not been itemized. Itemized now:

| | zbeta_correlated_error | stage3d_error_model | |
|---|---|---|---|
| data | n=4096 flows, MASTER_SEED children 32–47 / 80–95, own recovery | same seeds, Stage 3's recovery (0/80 identical) | **SHARED** |
| spacing statistic | `one_flow` → `one_minus_rtilde` | same | **SHARED** |
| unfolding | Richardson via `reference_cdf` | same | **SHARED** |
| fit | multi-start F3, same grid, same bounds | structurally identical `fit_f3` | **SHARED** |
| window rule | `mean > 1e-3` | same | **SHARED** |
| resample unit | whole replicate curve | same | SHARED |
| resampler | own loop, own RNG seed, B=2000 | own loop, own seed, B=400 | independent |

So P2 certifies the **last mile** — that two separately written resampling loops
with different seeds produce the same bootstrap SE on identical data through
identical plumbing. That is worth having. It says nothing about the chain above
the resampler, and "genuine cross-cell reproduction" suggested more. The lineage
guard would have refused this pair about `protocol`, and was not asked.

## 14. Stage 3d's "the correct error model" — overstated. Neither model is correct at both ends.

Measured at the swing's denominator cell (k_lo=5, k≤11, seven points):

| n | class | se_β covariance | se_β bootstrap | boot/cov | corr(τ,β) |
|---|---|---|---|---|---|
| 1024 | iid | 0.284 | 0.047 | 0.16 | 0.999 |
| 4096 | iid | 0.117 | 0.019 | 0.16 | 0.999 |
| 4096 | gue | 0.048 | 0.012 | 0.24 | 1.000 |

The fit is **degenerate** there — (τ,β) correlation 0.999+ at every n. The
covariance reports the degeneracy honestly; the bootstrap cannot see it, because
sixteen near-identical replicates do not explore a flat direction in parameter
space. So at short windows the *bootstrap* is the overconfident one, by 4–6×.

The two models have different blind spots. Covariance: sees degeneracy, blind
to across-k correlation and to misspecification. Bootstrap: sees correlation and
part of the misspecification, blind to degeneracy. 3d's verdict string
`WINDOW_SWING_SURVIVES_THE_CORRECT_ERROR_MODEL` stands as a measurement and is
mis-named as a claim. The separation at k* is reported with bootstrap errors
because k* is not degenerate in the way (τ,β) are.

## 15. Why the inflation grows with n — answered. It is misspecification, not correlation.

Will asked. The obvious hypothesis (across-k correlation grows with n) is
**refuted**: iid median |r| is 0.906 / 0.857 / 0.859 at n=1024/2048/4096, flat.
The denominator cell (item 14) is n-invariant. The trend lives at the **long**
window and tracks iid's growing F3 misspecification exactly:

| n | χ²/dof iid | z_cov/z_boot at sealed | inflation |
|---|---|---|---|
| 1024 | 0.76 | 0.67 | 1.11 |
| 2048 | 2.29 | 0.89 | 1.32 |
| 4096 | 3.76 | 1.12 | 2.23 |

`absolute_sigma=True` treats the supplied σ as exact, so a χ²/dof of 3.76 does
not widen the covariance. The fit is systematically wrong and the model reports
it as if it were right, by a margin that grows with the misspecification; the
bootstrap partly sees it because resampled fits scatter more when the model is
wrong. **Not benign.** The paper disclosed χ²/dof growth "as a finding" without
connecting it to the validity of the error bars it quotes. Connected now, in §4.

## The 0.87 percentile, mechanism (item 5 of the morning summary, completed)

Will: three n giving the same percentile to two decimals is evidence of a shared
determinant, not a law, and it was self-flagging before the bootstrap ran.
Confirmed and localized: the percentile is a rank among 15 cells (resolution
1/15, so "two decimals" was never the right frame). The sealed cell sat at rank
13 at every n under covariance and scattered to 14 / 7 / 13 under bootstrap. The
full ordering is NOT pinned (covariance rank-correlation across n is 0.92 /
0.50 / 0.58) — only the sealed cell's rank is, because it always has the most
points and covariance-z is driven by point count. Filed as
[[suspicious-agreement-is-a-shared-determinant]].

## 16. Stage 3d's C2 "the covariance model inflated it" — BACKWARDS. Found by the fork refusing its own threshold.

Building the error-model fork as code (`errormodel.py`) with a declared
degeneracy threshold of 0.95 and applying it to 3d's surface: **15 of 15 cells
are degenerate, including the sealed 16/11-point windows** (|corr(τ,β)| = 0.982
iid, 0.994 GUE; ≥ 0.999 on the shortest). The (τ,β) degeneracy is a property of
F3 on this data at every window length, not a short-window pathology.

So the covariance model — which sees the degeneracy — is the one whose swing is
honest, and the bootstrap — blind to it — is the one that UNDERSTATES. 3d's C2
read "worst swing_cov / swing_boot = 2.23 ≥ 1.5 MET, the covariance inflated
it". The direction is reversed: the bootstrap deflated it. The 04:08 caveat and
the paper paragraph written from it carried the same reversed reading; the paper
now says so explicitly.

The verdict string `WINDOW_SWING_SURVIVES_THE_CORRECT_ERROR_MODEL` stands as a
measurement (the bootstrap swing does clear 3x everywhere) and is mis-named as a
claim about which model is correct. There is no correct model here; there is a
declared rule and both numbers.

And the consequence for the headline: z(τ) = 20.4 and z(β) = 9.3 are marginals
of ONE elongated constraint, reported along two axes. They are not two pieces of
evidence. §4 says this now, and it is the structural reason the section leads
with k*.

---

# Items 17–19, added 2026-09-15 on Will's second review

## 17. "The covariance swing is the honest one" — re-committed the error item 14 disowned.

Item 14 said there is no correct model, then item 16 picked a winner anyway.
Retracted. The statement that survives: **covariance is honest about SHAPE,
bootstrap about SCALE, neither about both.** The covariance has the geometry
right and the scale wrong — `absolute_sigma=True` with χ²/dof = 3.76 understates
parameter uncertainty by roughly √3.76 ≈ 1.9× at n=4096, and that error grows
with n. The bootstrap has the scale closer and sees less of the flat direction.
Neither swing is "the honest one".

## 18. GLS as a discriminator — F3 is wrong as a FUNCTION for iid, not just mis-weighted.

Will: if GLS (carrying the across-k correlation) fits at χ²/dof ≈ 1 where OLS
gives 3.76, the misspecification was in the error structure and F3 is fine as a
form; if GLS is still ≈ 3.76, no weighting rescues F3. Computed from the banked
n=4096 per-replicate curves (GLS χ² was banked nowhere):

| class | OLS diagonal | GLS shrink 0.05 / 0.1 / 0.2 / 0.4 |
|---|---|---|
| iid | 3.76 | **11.40 / 9.05 / 7.26 / 5.69** |
| gue | 0.017 | 0.22 / 0.14 / 0.08 / 0.04 |

GLS makes iid's fit WORSE. The residuals carry a systematic S-shape, and
whitening by a covariance that says "these points move together" makes a
trend that is NOT noise-like stand out more. **The misspecification is not in
the error structure. F3 is structurally incomplete for iid at n=4096.** For
GUE, GLS moves χ²/dof toward 1 — the signature of a sound form with a mis-scaled
error model. The asymmetry is the finding, and it decides which paper this is:
the richer-form successor is not optional. It also decides where zbeta's GLS
z(β) = 9.97–11.12 belongs — they are the least-wrong error model for a form
that is itself wrong for one class, which is not a footnote.

## 19. The degenerate direction IS the measurement — and the successor form falls out of it.

Eigendecomposing the (τ,β) covariance block at the sealed n=4096 window:

| | direction (τ,β) | sd | |
|---|---|---|---|
| iid | (+0.19, −0.98) | 0.0013 | constrained |
| iid | (−0.98, −0.19) | 0.035 | flat — condition 27.7× |
| gue | (+0.25, −0.97) | 0.0006 | constrained |
| gue | (−0.97, −0.25) | 0.024 | flat — condition 37.6× |

The class difference (Δτ, Δβ) = (+0.846, +0.085) projected onto the pooled
frame: **z = 50.9 along the constrained direction, 19.9 along the flat one,
Mahalanobis 54.7.** The marginals z(τ) = 20.4 and z(β) = 9.3 were
UNDERSTATING the separation — they project a 2D difference onto axes where
the 0.98 correlation smears it. One honest number plus a stated blind spot,
replacing two misleading marginals. (Covariance-model errors; scale
understated by ~1.9× per item 17, conclusion robust to that.)

The constrained direction is essentially **β** (weight −0.98). F3 measures β
well; τ is the flat over-parameterization. Tested three reparameterizations:

| parameterization | corr, sealed iid | corr, sealed gue |
|---|---|---|
| (λ, τ, β) native | 0.982 | 0.994 |
| (λ, β, c = β·ln τ) | 0.988 | — |
| **(λ, β, k\*)** — τ eliminated via the level crossing | **0.316** | **0.522** |

And the native degeneracy does NOT decrease with range — synthetic exact-F3 data
gives corr 0.9916 at 11 points and 0.9975 at 256 points across 22 decades. It is
intrinsic to `(k/τ)^β`, not a window effect. Parameterized in (λ, β, k\*), the
(β, k\*) pair is well-conditioned, k\* fitted directly returns 10.889 against the
banked 10.8891, and on the sealed iid window the fork's bootstrap branch FIRES
(worst remaining correlation 0.944, now λ-vs-shape) — the real red-path Will
asked for. **The arc's "compare at the level crossing" rule was identifying the
well-conditioned coordinate all along.** The successor form is F3 in (λ, β, k\*),
and the design constraint is specific: remove τ, not F3.

## 20. "Blind to the flat direction" (items 14, 16) — WITHDRAWN by Stage 3e's C3, whose bar was set first.

Will: test before accepting bootstrap-blindness as structural. C3's bar (cloud
|corr(τ,β)| ≤ 0.95 at k=5..11, B=8000) was sealed before those rows existed.
Measured: **0.981 (iid), 0.995 (GUE)**, against the covariance's 0.999. Plateaued
by B=2000 — not under-resampling. The bootstrap SEES the flat direction at every
window. What it disagrees with the covariance on is the EXTENT: σ_τ = 0.099
(bootstrap) vs 0.643 (covariance) on seven iid points at n=4096, 6.5×. Same
direction, different length. "Blind" is withdrawn; "shape vs scale" is the
statement that survives.

## 21. A paper numeral misread twice over — caught by the checker, not by me.

The sentence above first read "3×, σ_τ = 0.096 against 0.284". The 0.284 was
σ_β, not σ_τ, and from n=1024, not n=4096: I misread my own diagnostic table.
`verify_paper_numbers` refused it because it derived from nothing. The corrected
value (0.643) is recomputed from the banked curves on every board run; the wrong
one stays in the paper's footnote as a disclosed error and is named in the
checker's `DISCLOSED_WRONG` list so it cannot be mistaken for a source.

---

## Section 4 collapsed, 2026-09-15 — the history moved to the paper's Appendix D.

Will's test per footnote: does it prevent an error the READER could make, or
record an error I made? The first stays in §4; the second moves. Result: §4 went
from 180 lines and 8 footnotes to 115 lines and 1. The survivor is the warning
that z(τ) and z(β) are marginals of one elongated constraint — a natural
misreading that does not compress into "we report k*". Also kept inline as
load-bearing negatives: `absolute_sigma=False` is not the fix; the lower window
edge is the sensitive one; F3 is AICc-best on all 24 cells so holding it is not
question-begging.

Strengthened during the collapse, not only softened: GLS making iid worse at all
four shrinkages means the misspecification was the PARAMETERIZATION, not the
weighting — and 3e names the same defect (τ) from the identifiability side. §4
now says the successor is motivated by evidence rather than discomfort.

Re-filed: 3e's P2 at 0.000σ is an algebraic identity confirmed numerically, not
reproduction — k* is a deterministic function of (λ,τ,β), so agreement to all
digits is what correctness looks like and disagreement would have been a bug.
§4 files it as a check on the algebra and leads 3e with C1 (corr 0.99 → 0.52),
which is the claim that the new form is actually better conditioned.

This ledger stays as the working record; the paper's Appendix D is the reader's.
