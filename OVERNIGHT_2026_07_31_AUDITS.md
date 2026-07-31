# Two audits run alongside Tier B, 2026-07-31

Both were produced by parallel read-only agents while the ports computed. **The
full reports were written to `/tmp` and a reboot destroyed them**, which is
itself the knowledge-does-not-propagate failure this project keeps hitting. What
survives is recorded here. Provenance is marked per claim: **[VERIFIED]** means
re-derived directly in this repo after the fact; **[REPORTED]** means the agent
stated it and it has *not* been independently checked.

---

# A. Unattributed constants — headline numbers with no live derivation

Swept 568 py files for reference-constant dictionaries and transcribed literals.
**21 confirmed findings, 12 explicit false positives recorded.** Concentrated in
`approximability/`, `arsrh/`, `thermo/`; the neuro phase dirs are largely clean.

## Tier 1 — a wrong number that INVERTS a result [VERIFIED]

`approximability/depth5_q33215_floquet.py:35`

```python
W4=0.007434711  # banked depth-4 total width (lam=8)
...
W5_over_W4=tw/W4
```

The JSON in the same directory carries the real value,
`0.007434960053747872`. They differ in the 7th significant figure. Re-derived
against `approximability/depth5_q33215_floquet.json`
(`total_width = 0.007434960044994936`):

| W4 used | W5/W4 | reading |
|---|---|---|
| literal `0.007434711` | **1.0000334976** | width **GROWS** depth 4→5 |
| JSON `0.0074349600537…` | **0.9999999988** | **FLAT to 9 digits** |

The wrong ratio **is already banked** into the output JSON, and confirming
depth-4→5 behaviour is the run's stated purpose. Depth-5 total width in fact
matches depth-4 to the 11th digit; the literal manufactured the growth.

The same literal recurs at `thouless_predictions.py:30` — where every *other*
entry is full float64 — and a third, **correct** copy sits at
`fifth_analysis.py:36`.

## Tier 2 — load-bearing, no derivation [REPORTED]

- `arithmetic_toolkit.py:791-794` — the **deployed per-cell quadrant classifier**
  thresholds (`0.10 / 0.55 / 5.0 / 0.10`). Provenance is prose: *"Tier 2
  calibrator scatter, Phase 15"* — no file, no script, nothing re-derives them.
  Every BL/TR/BR/TL verdict rests on these four literals. `audit/04-discrepancies.md`
  independently flagged this function as unguarded. Ties directly to R-177 below.
- `bulk_recovery.py:127` — β-recovery interpolation table; 3 of 6 anchors
  unexplained.
- `arsrh/phase5b_leverage.py:118-119` + `phase5_attribution.py:62,65` — a
  "PROCEED / existence entailed" verdict and a hard `SystemExit` gate built
  entirely from pasted literals, while the source JSON sits unloaded in the same
  directory.

## Tier 3 — inconsistencies [REPORTED]

- `FUNGAL_IREP_SIGNED_TRUTH = -2.21198` is **defined and never asserted**; the
  repo reports **−2.21224** for the same quantity elsewhere.
- GOE ⟨r̃⟩ is `0.53070` in one file, `0.53590` in three others (surmise vs
  asymptotic — a real distinction, but `phase4_maass_endpoint.py`'s table mixes
  conventions).
- Two `cross_substrate/` D_box references are triplicated with **no banked
  artifact anywhere**; the two scripts cite each other's output by transcription.

## Two corrections the agent made against itself

1. `arsrh/phase7_exact_moments.py:102`'s bare `0.1762478124` looked like a prime
   instance — it is **not**. Recomputed: it is Goldston's Σ, matching the live
   mpmath derivation in `scout10_goldston.py` to 9.6 digits. Downgraded.
2. `K = 1.400967852459` (triplicated) is **correct to 5e-14** against its live
   recomputation. The finding is the missing link, not a bad value.

`thermo/gate_fixtures.py` and `tests/test_known_defects.py` already implement the
fix pattern (cross-checked references + retained-corruption regression asserts).
The gap is that neither has been applied to the reference-constant dictionaries.

---

# B. R-177 — the class-label problem

## Where the label lives [REPORTED]

- `arithmetic_toolkit.py:800` — docstring: `BL  low rep_int AND no RF spike → Poisson noise`
- `arithmetic_toolkit.py:855-856` — the assignment, thresholding `rep_int_q`
  (the **clipped** field) at 0.10
- `arithmetic_toolkit.py:565` — the censored estimator
  `I_rep = trapezoid(np.maximum(0, 1 - R2), r)`; its floor is *exactly* the
  Poisson value. **The repaired `I_rep_signed` exists at :568 and the classifier
  does not consume it.**
- Restated in `METHODS.md:48`, `RESULTS.md:2424`, `TOOLKIT.md:432`,
  `CAPABILITY_REPORT.md:65`.

## The claim is correct, and understated [REPORTED]

**1,658 / 1,660 = 99.88%** of BL cells have `rep_med_signed < 0`; median −0.744.

1. **TR is contaminated too** — 108/203 (53%) clustered; pvc-11's TR is 15/15.
2. **The banked mitigation is falsified.** `ESTIMATOR_CLAIM_PROVENANCE.md:41`
   records that *interior* BL is "genuine, correctly-measured weak repulsion".
   Recomputed: interior BL is **335/337 = 99.4% clustered**.
3. **Independent of the repulsion integral entirely:** against a 12-seed
   genuine-Poisson envelope built through the project's own `axes.py`, pvc-11's
   1,144 banked BL rows fall outside it — all in the clustered direction — on
   `I.7_ks_poisson` 99.5%, `I.4_w1_poisson` 99.2%, `I.8_brody_q` 99.4%,
   `I.9_berry_robnik_rho` 94.2%, `Σ²(L)/L` 98.4% (median **4.18** vs Poisson 1.0).

## Cause: the label is wrong, the generator is not [REPORTED]

Two label-side defects: axis censoring (repaired in `I_rep_signed`, never
propagated into the classifier), and a vocabulary with **no negative region** —
so even a repaired axis has nowhere to put clustering. **Pooling is ruled out**:
pvc-11 `spontaneous` cells take the branch returning the raw single-unit train
verbatim (`phase22a/loader.py:90-91`) and are 99.77% clustered; and the
documented pooling confound manufactures *repulsion*, the wrong direction.

## Blast radius [REPORTED]

~44,300 BL rows across 43 parquets; 1,681 in the coordinate store. Plus:

- **The gate cannot fail.** `phase22a/verify_calibrators.py:66` has no clustered
  calibrator (`'poisson': 'BL'`, rest TR/BR). "8/8 calibrators pass" certifies
  only the classes the vocabulary can represent. `validate_fitters.py` already
  fixed exactly this for Brody/Berry-Robnik and it was never propagated.
- **`RESULTS.md:4923` is false as stated** — "V1 single-unit spike trains are
  dominantly Poisson under ARS" describes the 1,144 rows that are 99.83% clustered.
- GRB Tier-4 null (`RESULTS.md:4567-4590`) — real and surrogate both land on the
  collapse class: **uninterpretable, not wrong**.
- `transition_diagnostic.py:60` puts BL at the geometric **origin (0,0)** and
  uses it as the default fallback origin class (`:423`).
- Phase 23 QPO, Phase 26/27/28 `frac_BL`, Phase 30 Kuramoto (6,257/6,300 BL),
  BGP, earthquakes, Phase 36 taxonomy test.
- **Safe:** hc3, buzsaki, ibl, ret1, allen-hpf, brocot, dynamical bank
  `I.10_cv`/`I.11_mass03` and **no quadrant label** — the clustering⊥coupling and
  pillar work does not sit on `primary`.

## Recommendation [REPORTED]

**Option B — split the axis, then re-register a 5-class vocabulary** (add `CL`
for `rep_signed < −ε`; narrow `BL` to Poisson-consistent). `ARS.rep_med_signed`
already exists for all 8,001 recomputed rows, so re-deriving `primary` for the
three big substrates is a pure relabel, not a re-extraction. Option A (relabel
only) is a necessary first step under any option; Option C (retire the
classifier, publish on continuous axes) is where the program has already drifted.

**Three decision inputs before sealing anything:**
(a) `ε` must be **measured** from the genuine-Poisson `rep_med_signed`
distribution using the same sealed rule as `GUE_EXPECTATION_REREGISTRATION.json`,
not chosen; (b) the seal should be gated on running clustered calibrators through
`joint_quadrant_diagnostic` on the signed axis and confirming separation;
(c) **check first whether the 43 parquets store a signed per-q column** — that
single fact decides whether Option B is a relabel or a re-run, and it was not
checked.
