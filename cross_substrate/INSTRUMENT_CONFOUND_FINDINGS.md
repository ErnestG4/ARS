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
