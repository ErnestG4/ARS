# Instrument / collection-method confounds — FINDINGS

Module: `instrument_confound.py`. Closed-loop validation (`validate()`) +
first real-substrate lensing-ledger pass (`grb_ledger_pass()`). Run with the
main venv: `/home/combust/fmexplorer/bin/python3 instrument_confound.py`.

## Audit — what was already in place (verdict: GAPS CONFIRMED)
- **Nulls/calibrators are ~all mathematical.** Poisson / GOE / GUE / GSE /
  Hawkes / phase-randomized / cumulant-matched / hardcore-Matérn. The **only**
  instrument model is `run_phase21_calibrators.synthesise_deadtime_signal`
  (Fermi/BATSE/RHESSI), GRB-specific and not reused — the baseline panel and
  every cross-substrate port are 100% math nulls. No efficiency/thinning model,
  no sort/threshold model.
- **Provenance is lossy.** `coordinates/*.jsonl` carry IDs + Family-I axes + a
  one-line source stamp. Collection params (`DT=0.025`, sampling rate, subsample
  cap, sort label) live in loader hardcodes/docstrings and are dropped from the
  result. No ledger object.
- **No short-range dead-time-vs-repulsion separator** (caught post-hoc today via
  mass<0.3→0). **Thinning** exists only as a compute cap, never as a confound
  probe. The induction-on-noise harness (`run_phase18`) fires only on arithmetic
  findings, with math-null surrogates.

## What was built
Operators at the `positions` level (upstream of `canonical_spacings`), read on
the small-spacing-sensitive axes `{I.5_ks_gue, I.11_mass03, I.10_cv, I.12_cv2,
I.8_brody_q}`:
1. `apply_deadtime(τ, paralyzable=)` — non-extending (absolute refractory) and
   extending (detector-saturation) dead time.
2. `random_thin(p_keep)` — finite efficiency as Bernoulli retention.
3. `apparatus_subtracted_comparison` — empirical vs bare-null vs dead-time-
   injected-null → `{NULL, APPARATUS_EXPLAINS, RESIDUAL_STRUCTURE}`.
4. `thin_sweep` — deletion-fraction trajectory + washout flag
   `{THINNING_ROBUST, EFFICIENCY_DRIVEN}`.
5. `method_perturbation` — covariant / invariant / **saturated** across a
   {deadtime, thinning, binning} grid; only `METHOD_INVARIANT` promotes.
6. `Provenance` + `LensingRecord` + `write_ledger` — the durable output.

## Results

**VALIDATED (closed loop, ALL_PASS, A–H):**
- **A** Poisson thinning-invariant on all five axes.
- **B** dead time onto Poisson fakes repulsion (mass03 0.257→0.054, ks_gue
  0.283→0.192) and the injected null absorbs it → `APPARATUS_EXPLAINS`.
- **C** GRB deadtime synthetic → **no promotable substrate candidate** (repulsion
  axes read covariant or saturated, never invariant).
- **D** regular endpoint washes out under mild thinning (CV 0.07→Poisson, 51% of
  gap closed at 30% deletion) → `EFFICIENCY_DRIVEN` fires.
- **E** (crux) genuine GUE vs realistic-dead-time-injected null →
  `RESIDUAL_STRUCTURE` at z≈41. Same "looks-repulsive" observable as B, opposite
  origin, correctly separated.

**HARDENING for real data (2nd phase — addresses pre-hc-3 review):**
- **F** dead-time estimation uncertainty propagates into the injected null: with
  40% relative τ error the injected band widens 0.012→0.085 and the artifact is
  STILL absorbed. On real tetrode data τ is estimated, not known — a point-
  estimate null under-absorbs (promotes artifacts) or, if τ is set too large,
  over-absorbs (buries residual). `Provenance.dead_time_rel_err` carries the
  estimate's error; `build_lensing_record` feeds it through. RESIDUAL_STRUCTURE
  becomes a conservative call.
- **G** Finding-1 cuts both ways: a low-efficiency apparent-Poisson read is
  consistent with a *thinned sub-Poisson* substrate. The ledger flags
  `POISSON_CONSISTENT_WITH_THINNED_SUB_POISSON` when efficiency < 0.7 and the read
  is Poisson-consistent — so the caveat attaches to the Poisson null too, not only
  to sub-Poisson claims.
- **H** soft saturation (headroom, not exact rails): an axis NEAR a boundary that
  barely moves is indeterminate even if not exactly railed (mass03=0.012 →
  `METHOD_SATURATED`). The discriminant tests headroom + absolute movement: near a
  rail it promotes nothing unless the axis demonstrably swings OFF the rail
  (large absolute movement → covariant). Closes the approximately-invariant
  sneak-through the exact-rail guard left open.

**THREE-ZONE BRACKET (3rd phase — the real-data attribution method):**
The short-ISI hole in tetrode data MIXES genuine biological refractoriness
(substrate, keep) with pipeline censoring (sorter refractory + DAQ dead time,
subtract). A single empirical-floor τ captures whichever binds, so it
over-absorbs when biology dominates — a fine conservative *promotion* bar but a
corrupt *attribution* if stamped `APPARATUS_EXPLAINS`. So `apparatus_bracket`
runs two nulls — TIGHT (hardware/sorter refractory, minimal) and WIDE (empirical
ISI-floor, maximal) — and records the **zone**:
- **SUBSTRATE_ROBUST** — survives even the WIDE null → beyond maximal plausible
  apparatus → promotable. (Test **J**: genuine GUE.)
- **INDETERMINATE** — survives TIGHT but absorbed by WIDE → attribution genuinely
  ambiguous between biological refractoriness and pipeline; NOT promoted, NOT
  stamped apparatus. (Test **K**: moderate hole, span bracket.)
- **APPARATUS_EXPLAINS** — explained by even the TIGHT null. (Test **I**: known
  artifact, bracket containing the true τ.)
`estimate_deadtime_floor` uses the **P0.5 percentile** of ISIs (NOT the sample
min — an extreme order statistic the bootstrap underestimates) and a deliberately
**widened rel_err** (default 0.5); the band errs wide so the apparatus is not
under-modeled.

**OPEN — power, not correctness:** the z≈41 in (E) shows the separator is correct,
NOT that it has power. On real hc-3 the apparatus null will absorb most short-range
structure and the residual z will be small; detection power at realistic n is the
live question for the hc-3 pass. Report residual z WITH its uncertainty band, not a
bare verdict.

**GRB lensing-ledger pass (first real substrate):**
`coordinates/instrument_lensing_ledger.jsonl` — RHESSI 6µs deadtime, n=5206.
`mass03`→0 and `brody`→1 read `METHOD_SATURATED` (railed = the documented
`mass<0.3=0` dead-time signature); `ks_gue`/`cv`/`cv2` covariant. **PROMOTED:
(none).** Correct known-answer.

## hc-3 first real-substrate pass (CA3 + CA1 pyramidal, `hc3_instrument_pass.py`)
Local CRCNS cache: CA3 ec013.922 (36 pyramidal, 3362s) + CA1 ec016.106 (16
pyramidal ≥200 spk, 622s epoch; pulled fresh). Per unit: bracket between a TIGHT
null (2 ms hardware/sorter refractory) and a WIDE null (empirical P0.5-ISI floor,
rel_err 0.5); matched-n contiguous-segment cap (NOT decimation — that would
Poissonize bursts).

**Result — both regions, all units:** clustering axes (`mass03`, `cv`, `cv2`,
`ks_gue`) read **SUBSTRATE_ROBUST** at residual z ≈ 37–54 vs even the maximal-
apparatus WIDE null. `brody_q` reads NULL on all (Brody is repulsion-only, blind
to clustering — the SOC one-sided-fitter lesson). Ledgers (session-tagged):
`coordinates/instrument_lensing_ledger_hc3_{CA3,CA1}_p_<session>.jsonl`.

**Interpretation (directional, not a power claim):** dead time *removes* small
spacings, so it SUPPRESSES clustering — a bursty cell sits on the opposite side of
every dead-timed null. The confound cannot FAKE clustering, only hide it. So the
burst-clustering / pillar-2 signal is robust to the dead-time confound **by
direction**, and the high z is honest (a large-amplitude effect, not the small-
residual regime where power is the worry). **The dead-time bracket is near-trivially
passed by clustered cells** — its discriminating power is for REPULSION/regular
cells (the dead-time-fakes-repulsion crux). That is the interneuron population,
which is ALSO the thinning-fragile endpoint (Finding 1) — so pass 2 (pyr/int
contrast) carries BOTH apparatus risks and is where the separator is actually
tested. [[pillar2_burst_control_systematic]]

**Contamination backfill — the additive flank (the ONLY apparatus effect that can
fake clustering).** Dead time / thinning are subtractive; sort OVER-MERGE is
additive — it injects another unit's spikes → sub-refractory ISIs → spurious
short-lag structure reading as burstiness. So clustering is armored against the
censoring confounds and WIDE OPEN to contamination. Per-unit refractory-violation
rate (RPV, ISIs < 2 ms) added to every ledger record + a CLEAN/MARGINAL/
MERGE_SUSPECT flag. **Result: zero merge suspects.** CA3 — 30 CLEAN / 6 MARGINAL /
0 SUSPECT (median RPV 0.25%, max 1.56%); CA1 — all 16 CLEAN (max 0.38%). The
SUBSTRATE_ROBUST clustering survives the additive confound too: it is not a merge
artifact. Pillar-2 burst-clustering is now armored on BOTH flanks.

## Pass 2 — interneurons (the regular/fast population; where the separator is tested)
CA3 interneurons, 44 units across 4 cached ec016 sessions (ec016.674/733/749/799),
each unit keeping its OWN apparatus null (combined evidence, NEVER raw spikes
pooled across sessions). Within-session anchor ec016.41: 1 pyr SUBSTRATE_ROBUST
z≈45 vs 10 int mixed — apparatus held constant, so the contrast is not cross-session.

**Result — the separator discriminates here, unlike on pyramidal:**
- Global clustering axes (`mass03`,`cv`): 41/44 SUBSTRATE_ROBUST but at much lower
  residual z (mass03 median 10.5 vs pyramidal ~45–54).
- **Rate-robust LOCAL axis `I.12_cv2`: 15 SUBSTRATE / 20 INDETERMINATE / 5
  APPARATUS / 4 NULL, residual z median 1.6, IQR [1.0,3.2] straddling threshold.**
  The apparatus ambiguity concentrates here — the wide-band / INDETERMINATE regime
  is the method WORKING (genuine biology-vs-pipeline ambiguity), not a null result.
- `brody_q`: 38 NULL / 4 INDETERMINATE / 2 APPARATUS — some interneuron repulsion-
  side structure is apparatus-influenced (the dead-time-fakes-repulsion flank, live).
- Contamination: all 44 CLEAN (max RPV 0.41%) — not merge.

**Mechanism (interpretable):** interneurons fire fast (median 29 Hz, mean ISI
~34 ms), so the apparatus dead-time/refractory scale (2 ms tight → P0.5 floor wide)
is a LARGE fraction of their ISIs → apparatus and biology overlap on the fast axis
→ INDETERMINATE. Slow pyramidal (mean ISI ~0.3–1 s) have a tiny apparatus fraction
→ fast axis stays clean → SUBSTRATE. This is precisely the small-residual regime
where the z≈41-synthetic was correctness-not-power: here the residuals ARE small
and the verdicts genuinely mixed. Ledgers:
`coordinates/instrument_lensing_ledger_hc3_CA3_i_ec016.*.jsonl`.
**Bound:** INDETERMINATE means the manipulations we could run can't separate
biological refractoriness from pipeline censoring on that axis — not "no structure".

## Induction-on-noise fold (Phase-18 harness, `run_phase18_finding_validation.py`)
The harness had ONE arm (math nulls: phase-randomized / Hawkes / cumulant-matched
— the substrate probe). Added a SECOND arm (the instrument probe): each finding is
perturbed by dead time (0.15, 0.30 × mean ISI) and thinning (10%, 25%) and
re-classified in the harness's native quadrant space. Polarity is opposite and
labelled: surrogate "survives" = different class; apparatus "robust" = quadrant
UNCHANGED. Output: `data/phase18_apparatus_robustness.parquet` (gitignored).

**Apparatus-robustness result (full run, 84 rows, 1321 s):**
| finding | deadtime | thinning | verdict |
|---|---|---|---|
| zeta_first_2000 / zeta_high_height | 1.00 | 1.00 | APPARATUS_ROBUST |
| lmfdb_ec_pooled / dirichlet_pooled | 1.00 | 1.00 | APPARATUS_ROBUST |
| primes_1e6 | 1.00 | 1.00 | APPARATUS_ROBUST |
| earthquakes_M45 | 0.50 | 1.00 | robust except quadrant MOVES at dead time 0.30 |
| twin_primes_1e7 | 0.00 | 1.00 | DEADTIME_SENSITIVE |

- The TR (repulsive) arithmetic findings and primes_1e6 are apparatus-robust:
  their verdicts are not collection-method artifacts.
- earthquakes (BL/clustered) moves only at the STRONG dead time (0.30) — directly
  consistent with the hc-3 directional finding (dead time suppresses clustering).
- twin_primes_1e7 is flagged DEADTIME_SENSITIVE (quadrant labile under dead time,
  thinning-robust) — the apparatus arm earning its keep on a near-boundary finding.

**NOTE (pre-existing, NOT from this fold):** the SUBSTRATE arm triggers its
STOP CONDITION — zeta/lmfdb/dirichlet TR findings are reproduced by
phase_randomized + cumulant_matched. That is the known property that an NNS verdict
is largely a function of the marginal spacing distribution those surrogates
preserve; the apparatus fold is additive-only (106 insertions, 0 deletions; surrogate
code byte-unchanged) and does not affect it. Flagged for the substrate-arm owner.

## Dataset-selection call before any CA1 pull (`hc3_cv2_diagnostic.py`)
Pass 2 left 20/44 CA3 interneurons INDETERMINATE on `cv2` at z≈1.6. Before
spending a CRCNS request, settle on data in hand: is that indeterminacy
SAMPLING-limited (more units → population verdict → pull worth it) or
τ-SYSTEMATIC (a shared apparatus mis-attribution that does not shrink with N →
need better apparatus, not more units)? Decompose the τ-floor by quadrature: wide
null at rel_err=0 (sampling sd) and rel_err=0.5 (sampling+τ); τ-floor = √(σ_tot²−σ_samp²).

**Result:** the INDETERMINATE subset is strongly **consistent** (19/21 same-signed,
negative — interneurons read more regular than the apparatus null). But the
consistent component `|r̄|=0.036` sits **ON** the systematic τ-floor (`0.034`,
ratio **1.06**); it clears only the INDEPENDENT τ-floor (√N, 0.006, ~6×). So it is
clear iff τ errors are independent across units; if the apparatus mis-estimate is
shared across same-rig/sorter units (likely), it is **buried**. **VERDICT:
τ-LIMITED, not sampling-limited → DON'T pull CA1 on this.** More interneurons only
shrink the sampling part, already 6× below the signal; they do nothing to the
systematic τ-floor that is the actual limit. The unlock is **collapsing the τ-floor**:
documented hardware dead time for these Mizuseki/Buzsáki recordings (rel_err→small
moves it to the √N regime where the signal is ~6σ clear), or a slower comparison
population (smaller apparatus/ISI ratio). The pull is a dataset-selection error
until then.

## Resolution-floor domain-of-validity bound (in every ledger record)
Separability is set by **(apparatus timescale)/(mean ISI)** — a stated bound, not
a per-unit quirk. The lens goes blind on the local/fast axis whenever the apparatus
timescale (dead time + its uncertainty) is not small against the substrate's own
ISI: fast interneurons (~29 Hz) put the 2 ms apparatus across a real fraction of the
local axis (biology↔pipeline overlap → cv2 INDETERMINATE), while slow bursty
pyramidals (ISI ~0.3–1 s) make 2 ms negligible (clean separation). `RESOLUTION_BOUND`
+ `domain_of_validity()` ship this in `LensingRecord.domain_of_validity`. The coarse
(timescale)/(mean ISI) ratio can mislead (mean ISI is the wrong denominator for a
local-axis floor; the true limit is the τ-uncertainty), so the regime is taken from
the AUTHORITATIVE empirical local-axis (cv2) bracket zone when available:
INDETERMINATE → TAU_LIMITED. hc-3 regimes: CA3/CA1 pyramidal 53/53 RESOLVING;
CA3 interneurons 24 RESOLVING / **20 TAU_LIMITED** (the resolution floor, made
explicit per record). This is the method's domain of validity: it goes blind when
the apparatus timescale isn't small against the substrate's own.

## Long-range audit — the verdict's OWN statistic (`longrange_discriminator.py`, `longrange_audit.py`)
The Phase-18 STOP CONDITION's real meaning: marginal-preserving surrogates reproduce
the NNS verdict, so NNS certifies the MARGINAL, not the long-range structure that
DEFINES the universality class. Proof via a Wigner-renewal decoy (i.i.d. Wigner
spacings → GUE NNS, zero rigidity): closed-loop ALL_PASS — real GUE and decoy share
NNS (ks≈0.01) but Σ² separates >20× (RIGID_GUE vs MARGINAL_ONLY), and a cumulant-
matched surrogate keeps NNS while collapsing the long-range (the STOP-CONDITION
mechanism). The long-range verdict compares Σ²(L)/Δ₃(L) to memoized real-GUE and
renewal ensembles; RIGID is one-sided (at-or-below GUE rigidity is still GUE-class).

**UNFOLDING IS THE LONG-RANGE ARM'S OWN LENS** (the analog of dead time for NNS).
Σ²/Δ₃ need a flat mean density; NNS does not. So adding the long-range arm stacked a
new apparatus stage — unfolding — that can MANUFACTURE rigidity (over-unfold) or
ERASE it (under-unfold → σ²≫Poisson). `unfold_empirical(deg)` applied UNIFORMLY to
data + references; `unfolding_sensitivity()` SWEEPS the degree and reports
LENS-INVARIANT (trustworthy) vs LENS-COVARIANT (verdict is an unfolding artifact) —
the unfolding method-perturbation, same discipline as the apparatus arm. The lens
degree is carried in every verdict.

**Audit of the banked arithmetic claims (with the lens sweep, degs 3/6/10/15):**
- **zeta_first_2000 → RIGID_GUE, LENS-INVARIANT** (σ²≈0.37–0.43 across all degrees).
  GUE-class CONFIRMED. Its EXCESS rigidity (σ² *below* the GUE ensemble) is lens-
  invariant ⇒ NOT an unfolding artifact ⇒ a **real RESIDUAL to explain**: leading
  candidate the arithmetic prime correction (Berry–Keating / Bogomolny–Keating two-
  point form), alternative finite-height — the lens sweep rules out the unfolding
  alternative. Residual-is-the-product, now in the most-banked claim.
- **zeta_high_height → LENS-COVARIANT** (MARGINAL_ONLY σ²=10.8 @deg3 → INTERMEDIATE
  @deg6 → RIGID_GUE σ²≈0.5 @deg10/15). The σ²=71 default read was UNDER-unfolding
  (high zeros have a steeper density a deg-6 poly can't flatten); at adequate degree
  it converges to RIGID_GUE. Verdict is lens-dependent ⇒ NOT promotable without the
  right lens; with it, GUE-class. The lens screaming, then resolved.
- **lmfdb_ec_pooled / dirichlet_pooled → MARGINAL_ONLY, LENS-INVARIANT** (σ²≈9
  across all degrees). The downgrade is ROBUST, not an unfolding artifact ⇒ a REAL
  effect: pooling independent spectra superposes → long-range Poissonization even
  when each component is GUE and the pooled NNS looks GUE. The **arithmetic twin of
  the neural no-pooling rule** — "marginal-only on pooled data" is expected.
- Controls (real GUE→RIGID, Poisson→floppy, decoy→MARGINAL_ONLY) all correct.

**Discipline output:** the unfolding-sensitivity sweep trisects cleanly — CONFIRMED
+ residual (zeta_first), lens-artifact-needs-right-degree (zeta_high), REAL downgrade
(pooled). A long-range statistic is only meaningful on properly-unfolded data, and
the lens must be carried + swept like any apparatus stage. Phase-18
`expected_survives` relabelled: the four TR findings expect only the marginal-
DESTROYING surrogate (hawkes) to flip an NNS verdict; the class claim is carried by
the long-range arm, not NNS.

**The generalization (queued):** this is not arithmetic-specific. EVERY verdict
resting on NNS alone — including the neural pillars (pillar-1 GUE/Poisson, H1
ks_gue) — inherits it. Run the same marginal-surrogate + long-range statistic
against each banked universality claim. Two sharpenings for the neural pass:
(1) NNS under-certifies BOTH poles — exponential NNS is necessary-not-sufficient for
Poisson (a correlated process can wear an exponential marginal), so Σ²(L) must
certify rigidity for the GUE pole AND Σ²(L)≈L for the Poisson pole, or pillar-1
carries the gap on both sides (needs a Poisson reference added alongside GUE/renewal).
(2) The ≥200-event floor (MIN_N_LONGRANGE) is real: below it Σ²/Δ₃ are themselves
underpowered, which on fast low-yield interneuron-style units folds back into the
pass-2 resolution-floor problem. `enough_for_longrange()` pre-checks per-cell event
counts so the long-range statistic is only run where the data supports it.

## Neural-pillar long-range audit (`longrange_neural_audit.py`)
Both-poles certification added to the discriminator: references are now GUE (rigid)
AND Poisson (Σ²≈L), with the Poisson pole judged by RATIO bands (Σ²≈L within a
factor — Poisson Σ² is intrinsically noisy, sd≈L/3, so an sd-band would swallow
renewal-level). Verdicts: RIGID_GUE / POISSON_INDEP / INTERMEDIATE / SUPER_POISSON.
Proof re-validated (real→RIGID, Poisson→POISSON_INDEP, decoy/cumulant→INTERMEDIATE).

Ran on **783 hc-3 cells across 23 cached sessions** (≥200-event floor,
`enough_for_longrange`), each its own verdict (no spike-train pooling), fixed
reference n + lens sweep (deg 3/6/10). TWO findings, named separately so the
negative doesn't eat the positive:

**(1) METHODOLOGICAL (negative refinement) — the Poisson pole is under-certified.**
Of **57 NNS-exponential (Poisson-pole) cells, 54/57 (95%) are NOT POISSON_INDEP**:
41 SUPER_POISSON (clustered), 9 INTERMEDIATE, 7 POISSON_INDEP (only 3 lens-invariant).
**Exponential spacing ≠ independence** — the neural "Poisson pole" is a MARGINAL-
Poisson, not a process-Poisson (point 4, confirmed). Robust at n=57 (was n=7 on 4
sessions — the thin-substrate worry is addressed; the negative holds at 95%).

**(2) SUBSTANTIVE (positive) — hc-3 cells are genuinely clustered at long range.**
**664/702 SUPER_POISSON cells are LENS-INVARIANT** (to smooth-poly across deg 3–10);
673/783 (86%) lens-invariant overall, spanning CA1/CA3/EC/DG. This is the standalone
characterization of hc-3 long-range statistics, not just a foil for the Poisson
story. CONDITIONAL on smooth-poly being a sufficient unfold (see caveat) — framed as
"lens-invariant to smooth-poly", NOT "stationary".

- **GUE pole: 0 cells in hc-3** (neurons rarely show GUE-level repulsion) →
  UNTESTABLE here; needs a GUE-reading substrate (Allen V1 / pvc-11). **Queued
  self-test (a DISAMBIGUATOR, not just confirmation):** H1 is OSI↔ks_gue POSITIVE
  ([[h1_direction_corrected]]) → high-OSI cells read FAR from the GUE pole on the NNS
  marginal. But "far from GUE" on the marginal alone is TWO-SIDED — more clustered
  (Poisson-like) OR more rigid (periodic-like) — and NNS cannot tell which. The long-
  range tool splits it: if high-OSI cells read SUPER_POISSON, the mechanism is bursty
  stimulus-driven firing pulling spacings into clusters; if they read RIGID, it is
  stimulus-LOCKING pulling spacings into regularity. So the second instrument hands H1
  a MECHANISM CANDIDATE it cannot get from NNS alone — worth more than concordance.
  (Sanity leg still holds: the lowest-ks_gue cells should read RIGID if H1's GUE end
  is genuine; SUPER_POISSON there would say ks_gue was reading clustering, not rigidity.)

**Rate-nonstationarity caveat (load-bearing) + the rate-aware attempt (NEGATIVE
RESULT):** neural σ² conflates genuine long-range clustering with slow rate drift;
smooth-poly unfold + lens sweep removes/flags SMOOTH trends only. The named next step
was a rate-aware / local-density unfold (`rate_aware_unfold`, time-rescaling via a
kernel rate estimate, bandwidth as the swept lens). **Built, swept, and it FAILS the
decoy validation** (`validate_rate_unfold` → INADEQUATE): at every usable bandwidth
the renewal DECOY reads false-RIGID and the GUE↔Poisson pole separation collapses
(60×→<4×). Reason is FUNDAMENTAL, not a bug: estimating the rate from the SAME train
and unfolding at scales ≤ L removes the very correlations Σ²(L) measures — **drift and
correlation ALIAS at the measurement scale.** Drift at scale ≫L is already removed by
the poly; drift at scale ~L is unremovable from the train alone. So self-estimated
rate cannot harden the bulk. **The 664/702 stands as "lens-invariant to smooth-poly"**;
a definitive neural long-range claim needs an EXTERNAL rate (behavioral covariates /
trial PSTH / simultaneous population rate) — new information beyond the spike train.
That is the real next step, reframed by this negative result.

**THE PATTERN IS ITSELF A FINDING:** same discriminator, two substrates so far
(arithmetic: zeta CONFIRMED, pooled DOWNGRADED; neural: Poisson pole DOWNGRADED), the
SAME structural move — an NNS/marginal universality claim gets refined by the long-
range check. This is a cross-substrate methodological result, fits the landscape
program ([[cross_substrate_program]]) as much as either substrate's individual reads.

## Allen V1 GUE-pole audit + H1 self-test (`longrange_allen_audit.py`)
The GUE pole hc-3 couldn't test (0 GUE-pole cells). Allen V1 drifting-gratings units
DO populate the GUE end (the H1 OSI↔ks_gue substrate). 100 V1 units (≥200 gratings
spikes, reusing `allen_osi_gap.gratings_train` + the banked 111-unit OSI parquet),
86 lens-invariant, per-cell verdicts.

- **GUE pole → MARGINAL-ONLY (THIRD downgrade).** 0/100 cells read RIGID_GUE; 93
  SUPER_POISSON. ks_gue RANKS a long-range clustering gradient (Spearman ks_gue↔σ²
  = +0.48, p=3e-6) — the NNS ordering is meaningful — but even the nearest-GUE
  quartile is 100% SUPER_POISSON, 0% RIGID. The NNS GUE pole is marginal-only,
  mirroring hc-3's Poisson pole. (Auto-verdict initially mislabeled this "concordant
  → genuine"; corrected — rank-concordance ≠ a genuine pole; the genuine test is
  whether nearest-GUE cells actually read RIGID, and none do.)
- **H1 self-test → mechanism candidate.** PRECISION: this used the PLAIN NNS ks_gue
  (`i5`, which the long-range Σ² extends), OSI↔i5 = +0.55 (p=6e-8) — selective cells
  read FAR from GUE on the plain marginal. (The banked q-banded H1 pillar leg
  OSI↔ks_gue_med is a DIFFERENT statistic, −0.22 in Allen per [[h1_direction_corrected]];
  the plain-vs-q-banded sign divergence IS the Allen OSI-gap allen_osi_gap.py studies.
  So this is the plain-NNS leg, not the q-banded pillar.) The 2nd instrument
  disambiguates "far from GUE" on the plain leg: high-OSI cells are 29/29 SUPER_POISSON
  → the CLUSTERED side (bursty stimulus-driven), NOT stimulus-locking (RIGID) — locking
  ruled out 29/29. Mechanism candidate: selective V1 cells are long-range-CLUSTERED,
  not regular/locked. (OSI↔σ² weak +0.14 because the whole population is clustered —
  little verdict dynamic range. Reconciling with the q-banded pillar leg is a further
  step.)
- **Load-bearing caveat:** the gratings train is presentation-CONCATENATED →
  stimulus-driven rate modulation (non-smooth, per-presentation) inflates Σ² and
  smooth-poly can't remove it; the all-SUPER_POISSON conflates intrinsic clustering
  with stimulus drive. UNLIKE hc-3, the external rate (trial PSTH) IS available here
  → the **trial-PSTH unfold is the concrete realization of the external-rate fix the
  #2 negative result demanded**, and the decisive next step to isolate intrinsic
  structure. The mechanism claim stands only as "not stimulus-locking" until then.
  **STANDING RULE before deploying the trial-PSTH (or any) unfold: run the decoy
  battery first** (renewal decoy must not read RIGID; GUE↔Poisson separation must
  survive; no false-RIGID — `validate` + `validate_rate_unfold`). External rate
  removes the SELF-derivation circularity that killed #2, but has its OWN aliasing
  modes (if the trial structure induces correlation at scale L, same alias) — so the
  battery is the standard pre-deployment gate. [[longrange_lens_discipline]]:
  pole tests are ABSOLUTE not ordinal; decoy battery gates every lens.

**THE PATTERN, now 3 substrates × both poles:** arithmetic (zeta CONFIRMED, pooled
DOWNGRADED), hc-3 neural (POISSON pole DOWNGRADED), Allen V1 neural (GUE pole
DOWNGRADED). On real neural data BOTH NNS poles are marginal-only — the long-range
check downgrades them, cells live in a clustered regime and the "poles" are gradients
within it, not genuine long-range RMT/Poisson classes (modulo the rate/stimulus
confound the trial-PSTH unfold will resolve). The marginal-vs-class downgrade is a
tool-level cross-substrate result. [[cross_substrate_program]]

## Trial-PSTH (external-rate) unfold — the decisive Allen de-confound (`trial_psth_unfold.py`, `longrange_allen_psth_audit.py`)
The #2 negative result demanded an EXTERNAL rate; gratings has one. λ_c(τ) = the
within-trial rate averaged across OTHER presentations of the same condition (LEAVE-
ONE-OUT, orientation×temporal-freq), time-rescaling unfold. NOT self-derived → breaks
#2's circularity.

**DECOY BATTERY FIRST (standing rule) → PASSED.** Imposed a known stimulus modulation
(tuning steps + F1) on synthetic GUE/Poisson/renewal via inverse-rescale, then
unfolded: GUE→RIGID (recovered), Poisson→POISSON_INDEP, renewal→INTERMEDIATE — **no
false-RIGID**. The trial structure does NOT induce a scale-L alias (Will's concern);
the external unfold inverts an imposed stimulus and recovers the true class, exactly
where the self-unfold (#2) failed. Validated for deployment.

**Deployed on the 100 V1 cells — three decisive results:**
1. **The clustering is BEYOND-STIMULUS, not stimulus-driven.** After removing the
   stimulus-locked rate: 96/100 still SUPER_POISSON (90/93 of the pre-SUPER cells
   stay), median σ² only 332→281 (−15%). The long-range clustering survives external-
   rate removal — it is not the stimulus.
2. **The GUE-pole downgrade is ROBUST to the stimulus confound:** still **0/100
   RIGID_GUE** after stimulus removal. No genuine long-range GUE pole in V1 gratings —
   it was not stimulus drive masking one.
3. **H1 refinement (disciplined walk-back):** OSI↔σ² collapses +0.135 → −0.077 (null)
   after PSTH. The OSI-GRADED clustering WAS the stimulus tuning rate-steps; once
   removed, clustering is UNIFORM across OSI. Selective cells are clustered (locking
   still ruled out, high-OSI 34/34 SUPER) but **NOT MORE than other cells** — the
   selectivity↔long-range-clustering gradient was stimulus-driven, not intrinsic to
   selective cells. (The pre-PSTH "selective cells specially clustered" mechanism
   candidate is corrected to "all V1 cells intrinsically clustered; the OSI grading
   was stimulus".)

**Bound:** trial-PSTH removes the STIMULUS-LOCKED rate; the surviving clustering is
"beyond the stimulus" but could be intrinsic bursting OR non-stimulus slow drift
(arousal/running) — separating those needs behavioral covariates (a further external
rate). K=10 within-trial bins target the L=50 (cross-presentation/slow) scale; fast
F1 is short-range and contributes little at L=50. The external-rate unfold is
decoy-validated and DEPLOYABLE (unlike the self-derived #2). [[longrange_lens_discipline]]

## Durable methodological outputs
- **Mild thinning does not easily erase the clustered or repulsive endpoints**
  (mass03 ~10% / GUE ks_gue ~42% of gap closed at 30% deletion); only the
  **regular/sub-Poisson endpoint is detection-efficiency-fragile** (one missed
  event → doubled gap). ⇒ substrate claims resting on clustering/repulsion are
  robust to moderate inefficiency; sub-Poisson claims carry a live efficiency
  caveat. → memory [[instrument_confound_thinning_asymmetry]]
- **Saturation ≠ invariance.** A railed axis (mass03@0, brody@1) has no dynamic
  range, so the perturbation discriminant cannot distinguish substrate from
  apparatus on it — it is INDETERMINATE, deferred to the injected-null stage. Same
  railed-estimator trap as the KPM floor. → [[floor_is_rigidity_not_density]]
- **Two-stage division of labor.** `method_perturbation` answers "method-sensitive
  vs method-robust" (genuine-but-fragile GUE AND apparatus both read covariant);
  `apparatus_subtracted_comparison` answers "reproduced by the *estimated*
  apparatus or not" (APPARATUS_EXPLAINS vs RESIDUAL_STRUCTURE). Promotion needs
  invariance; fragile-but-real structure is rescued as RESIDUAL only against the
  data's *estimated* dead time — which is exactly why the ledger carries the
  estimate as provenance, not a free knob (a too-large injected dead time would
  over-subtract real structure).

## Verdict
**MODULE VALIDATED — CLOSED-LOOP + GRB KNOWN-ANSWER.** Apparatus subtraction
separates dead-time-faked repulsion from genuine GUE and efficiency-faked Poisson
from genuine regularity, on the existing calibrators with no new data. Bound
held: method-invariance = robust to the manipulations run, not the territory.

## Queued
- Apply the lensing ledger to banked neural results (hc-3 tetrode first: real
  spike-sort + hardware refractory; pillar-2 most exposed). [[pillar2_burst_control_systematic]]
- ComCat Mc-completeness as a real detection-efficiency analog (thinning with a
  known SOC direction). [[soc_pair_complete]]
- Promote the dead-time operator + thinning sweep into the induction-on-noise
  harness so neural/cross-substrate findings get the same surrogate treatment
  arithmetic findings already do.

---

# RF-engine (Ramanujan-Fourier) confound run — the calibrator zoo applied

`cross_substrate/rf_decoy_battery.py`. The long-range arc taught us an NNS verdict
certifies the MARGINAL, not the class, and needed a Wigner-renewal decoy to split
them. The RF engine has its OWN observable — the indicator-mode amplitude `a_q`
(`joint_q_profile.rf_amplitude_q`), reading integer-PERIOD structure on the raw
event grid. The calibrator zoo (`calibrator_panel.py`) is the RF engine's native
known-answer substrate, so the same three checks run THROUGH it. (The confound
stack never touched the RF engine before this — it lived entirely on the
NNS/spacing path.)

## What the calibrator zoo provides
The zoo carries the **`a_q` ground truth**: periodic_q7 → peak AT q=7; mixed_q7_q12
→ 7 & 12; poisson / GOE / GUE / GSE / ζ / jitter → no integer period → `a_q` flat.
That is the no-false-NEGATIVE answer key the spacing-side decoy battery didn't need.
The KEY MISSING member — now BUILT — is the **`a_q` decoy**: a matched-marginal-
order-destroyed twin (the RF analog of Wigner-renewal). Two twins per calibrator:
*order-scramble* (permute the ISI multiset, re-cumsum — identical multiset) and
*iid-marginal* (resample ISIs i.i.d. — matched distribution). Plus an order-borne
**positive control** (`rigid_grid_jittered`: rigid 7-grid, broad ISI marginal via
bounded ±1 position jitter) to prove the decoy isn't blind.

## Findings (N=400, q_max=30, 8 seeds)

- **METHODOLOGY — `a_q` pole-absolute needs a zoo-CALIBRATED floor (≈6.1), NOT ~1.**
  The max of a normalized `a_q` spectrum over ~29 bands is extreme-value-inflated:
  the no-period classes peak at median 3.67 / max 7.32 / 95th-pct 6.10. The
  no-period zoo members ARE that calibration. A guessed threshold of 3.0 sat BELOW
  the noise-floor max and false-flagged all six structureless classes. Same
  pole-tests-ABSOLUTE discipline as the Allen GUE mislabel — but the absolute is a
  calibrated floor, not a constant. → [[nns_certifies_marginal_not_class]]

- **SUBSTANTIVE — indicator-mode `a_q` is a MARGINAL-DOMINATED observable; it does
  NOT escape the marginal-vs-class downgrade.** The disentangling result:
    - periodic_q7 (near-delta marginal): `a_q`=7 = 17.6, survives scramble (17.1)
      AND iid (24.3) → **MARGINAL_ENCODABLE**. The period IS the marginal — a delta
      ISI fully determines the grid, so any matched-marginal twin reproduces it.
    - rigid_grid_jittered (broad marginal, bounded phase): `a_q`=7 = 14.6, DESTROYED
      by scramble (→13%) and iid (→10%) → **ORDER_BORNE**. Period lives in serial
      order, not the marginal. ← proves `a_q` CAN be a genuine non-marginal
      observable AND the decoy isn't blind.
    - mixed_q7_q12 (broad marginal + 30% exp background): peak BELOW floor (2.4 < 6.1)
      → RF MISSES a period it should see. A no-false-negative SENSITIVITY caveat:
      indicator-`a_q` needs a (near-)delta marginal or a sharp bounded-phase grid to
      fire; a diluted multi-period mixture falls under its own noise floor.
  So `a_q` is, if anything, MORE marginal-dependent than NNS: it fires robustly only
  when the period is (near-)marginal-encoded. The orthogonality to the NNS axis holds
  — GUE reads ks_gue@pk=0.041 (strong GUE-marginal match) with `a_q` FLAT (3.89): the
  two observables are independent. → [[false_positive_equivalence_classes]]

- **APPARATUS GATES PASS — the confounds that bite NNS do NOT manufacture/erase `a_q`
  periods in the regime where `a_q` fires.** (a) Dead time (τ/ISI 0.3, 0.6) on
  poisson & GUE injects NO spurious peak (post stays at the pre-existing floor; it is
  subtractive — carves small spacings, cannot ADD a comb). (b) Thinning preserves a
  strong `a_q`=7 down to 40% efficiency (17.6→11.7, still ≫ floor). The dead-time-
  fakes-repulsion / thinning-fakes-Poisson confounds are NNS-axis effects; they do
  not transfer to the period axis. → [[instrument_confound_thinning_asymmetry]]

## Verdict
**RF-ENGINE CONFOUND RUN COMPLETE — calibrator-zoo-based, validated.** The zoo is the
RF engine's known-answer substrate; it gained the `a_q` decoy battery (order-scramble
+ iid-marginal + order-borne positive control). Net: (1) `a_q` pole verdicts need a
zoo-calibrated floor; (2) indicator-`a_q` is marginal-dominated and does not give the
RF engine a marginal-escaping observable (the decoy CAN find order-borne period
structure — `rigid_grid_jittered` — but the deployed periodic calibrators are
marginal-encodable); (3) `a_q` periods are robust to dead time and thinning in their
firing regime. Bound held: method-invariance = robust to the manipulations run.
