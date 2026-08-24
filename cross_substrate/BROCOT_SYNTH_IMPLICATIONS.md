# What the ARS brocot work says about the Brocot synthesizer

**2026-08-23.** Read against `~/fmexplorer/brocot` — `BROCOT-SPEC.md`, `source/pull/Landscape.h`,
`source/audio/CoherenceSuggest.h`, `phase3/partial_prediction.py`.

The connection is not analogical. `predict_partials(ratios, depths, f_carrier)` **is** Brocot's
parallel-FM topology (spec §2.2), so every ARS measurement in this programme is a measurement of a
real Brocot patch. That makes the findings directly applicable — and it also means an error in the
analysis regime is an error about the instrument.

---

## 0. First, a correction that governs everything below

**`depths` is the MODULATION INDEX, not a tree depth.** Every brocot ARS measurement ran at
`[8.0, 8.0]`. `BROCOT-SPEC.md` §1:

> *"Modulation indices are **low** — around half the first Bessel peak, so I ≈ 0.9 typically, with
> the meaningful range being **0.1 to 3.0** rather than the DX7's 0.5 to 8.0."*
> *"the depth slider's perceptually useful range is 0 to ~3, not 0 to 8"*

So the programme had been measuring **above the top of the instrument's useful range**, and the
"depth sweep" that closed the knob caveat swept {4, 6, 8, 10, 12, 14} — every point outside the
regime. Re-run at musical indices (`brocot_musical_depth.json`):

| finding | at I = 8 | at I ∈ {0.9, 1.5, 2.0, 3.0} |
|---|---|---|
| saturation (slope collapses toward the rigid end) | holds | **holds at all four**, and *stronger* (\|Δslope\| 4.02 at I=0.9 vs 3.32) |
| class position predicts a class's own slope | CI [−0.958, −0.300] | **CI covers zero at every musical index** |

**The primary finding reaches the instrument. The class-level one does not** — read as a power
limit, not a refutation: the point estimates at 0.9 (−0.708) and 3.0 (−0.556) sit near I = 8's
−0.651, but ten classes cannot resolve them with noisier per-class slopes.

---

## 1. Applicable: the soundspace metric is not perceptually uniform

`Landscape.h` finds "where we are" by **parameter distance** — *"a depth-weighted ratio histogram of
the current patch vs each node"* — and walks routes with `PullIndex::morph`. That design assumes
equal parameter distance buys equal timbral change.

Measured at I = 0.9 over the spec's defining range [0.70, 1.40] (`brocot_ratio_sensitivity.json`):

| | |
|---|---|
| gradient p10 / median / p90 | 6.9 / 14.3 / **83.6** |
| **p90 / p10** | **12.0×** |
| median gradient near a simple rational (q ≤ 4, d < 0.01) | **75.7** |
| median gradient far from one (d > 0.05) | **11.7** |

**A morph crossing a near-rational region changes timbre roughly 6× faster than one crossing a
plateau, for the same distance travelled.** That is a property of the soundspace, not of the
interpolator — so it cannot be smoothed away in `morph`. It can only be fixed by making the metric
match the gradient.

**Concretely:** `Landscape`'s ratio-histogram distance could be reweighted by the local gradient
(precomputable offline, exactly like the existing gradient fields), so waypoint spacing reflects
timbral change rather than parameter change. Everything needed is already offline — the file is
built by `phase3/gpu_paths.py gradients`.

## 2. Applicable: the noble/metallic region is a timbral plateau on this axis

The saturation finding, stated for the instrument: **d(spectral rigidity)/d(approximability) is
large near simple rationals and near zero at the noble ratios.** Per-class slopes at I = 8, with
the flat classes being exactly the ones sitting at the rigid end:

- **responsive** — generic +4.94, liouville +8.63, π−3 +7.86
- **flat** — golden +0.31, e−2 +0.28, ln2 +0.81, silver +0.82

Golden and e−2 are flat at *large* within-class spread, so they are well-powered nulls, not
underpowered ones.

**Design reading:** the noble ratios are where ratio-modulation stops doing anything on this axis.
That makes them good for *stable* sustained timbres and poor for expressive ratio sweeps. If the UI
or factory presets treat "most irrational" as the exciting end, that is backwards for this axis.

*Caveat carried honestly:* the per-class ordering above is established at I = 8 and does not
resolve at musical indices (§0). What survives at musical indices is the population-level
saturation, not the class-by-class ranking.

## 3. Applicable, and sharpest: **the analysis axis fails at the instrument's most idiomatic ratios**

The synth navigates a Stern–Brocot tree, so it lands on **exact** rationals. A grid sweep steps over
them — 0.75 vs 0.7500000000000001 give different partial sets. Evaluated at the 33 exact tree nodes
with q ≤ 12 in [0.70, 1.40], at I = 0.9:

| node | partials | `I8_brody_q_unbounded` |
|---|---|---|
| **1/1** | **6** | **REFUSED** |
| 3/4 | 22 | **+4.0000 — the estimator's upper bound** |
| 4/5 | 25 | +2.2198 |
| 6/5 | 29 | +1.5091 |
| 5/4 | 25 | +2.4643 |
| **4/3** | **20** | **REFUSED** |
| 7/5 | 31 | +2.1915 |

**1/1 is the unison default. 4/3 is the spec's own first named example of the defining regime.**
Both are unmeasurable at the typical modulation index — 1/1 because both modulators coincide and
the spectrum collapses to six partials.

And a floor: at **I = 0.5, 47 of 60 α clear the 20-partial bar and the estimator returns `None` on
all 47** — an estimator refusal, with a sharp usability threshold between 0.5 and 0.9. **The lower
half of the instrument's own useful range (0.1–0.9) is not analyzable on this axis.**

**Operational consequence for the v2 analysis hooks** (`ModTarget.h`, the parameter system's stated
v2 integration points): any readout of this axis must **refuse loudly** below I ≈ 0.9 and at
degenerate nodes, and must never print a value sitting at ±the estimator bound as though it were a
measurement. That is this repo's oldest recorded defect — a bounded estimator read as though its
bound were data — and it would land here at exactly the ratios a user reaches first.

---

## What is NOT applicable, said plainly

- **The classifier work** (one-sidedness, rejection regions, the C3 census) is about *analysis
  instruments*, not audio. Nothing in it constrains the synth.
- **Class-by-class slope ordering** — I = 8 only (§0).
- **Anything about I < 0.9** — not measured, because it cannot be measured on this axis.

## Provenance

Generators sealed before their outputs: `brocot_musical_depth.py` (§0), `brocot_ratio_sensitivity.py`
(§1, §3), with §2 resting on `brocot_slope_by_class.json` and `brocot_within_between.json`.
Predictions were scored — **M2, M3, M4, G3 all missed**, and §0 and §3 are consequences of those
misses rather than of the hits.

---

# ADDENDUM 2026-08-23 — the structure horizon, and why morphs lurch

## 4. Are we missing pieces of the FM pie by sticking to rationals? **No — the opposite.**

`brocot_useful_depth.json`, **MECHANISM_CONFIRMED**, exact at all 508 node×index combinations
(accuracy 1.0000, tested per node with no aggregation):

> **A ratio p/q has sideband-coincidence structure at modulation index I
> ⟺ max(p, q) ≤ 2·order_bound(I).**

Two sidebands collide when `n₁ + n₂α = n₁′ + n₂′α`. Writing `a = n₁−n₁′`, `b = n₂′−n₂` gives
`a·q = b·p`, and `gcd(p,q)=1` forces `b = mq`, `a = mp` — both bounded by 2·order_bound. Above that,
**no coincidence is reachable at all.**

| modulation index | order_bound | structure horizon max(p,q) ≤ |
|---|---|---|
| 0.9 (spec typical) | 4 | **8** |
| 1.5 | 5 | 10 |
| 2.0 | 6 | 12 |
| 3.0 | 7 | 14 |

**This is why complex ratios sound like noise.** Above the horizon every ratio yields the same
structureless dense cluster — identical partial count, top-5 energy and spectral entropy — differing
only in where the partials sit. Measured at I = 0.9: q ≥ 7 all give 31 partials, 0.716, 0.709.

**And it answers the rationals question directly.** An irrational has no finite q, so it is *always*
above the horizon. **The rationals are not a restriction on the interesting region — they are the
interesting region**, and everything the tree cannot reach is exactly the part with no coincidence
structure. The constraint the spec calls "the feature" is better founded than it knew.

**What is actually being missed** is the other direction: the instrument lets the tree be navigated
arbitrarily deep at any modulation index, when the mathematics binds them. At I = 0.9 every node
past max(p,q) = 8 is spectrally equivalent to every other.

> **Proposed feature — the structure horizon.** Compute `2·order_bound(depth)` live and mark
> tree nodes beyond it as inert. It costs one Bessel order bound, already computed in
> `order_bound()`. This gives the depth slider a second, visible meaning: *how much of the tree is
> alive right now.* Turning depth up does not merely brighten — it extends the horizon and brings
> new ratios into structure.

## 5. Why the wormholes lurch — and why reweighting will not fix it

`brocot_linear_morph.json`, on the path 3/4 → 4/3 at I = 0.9, 24 waypoints:

| parameterisation | CV of per-step \|Δu\| | worst step | waypoints near a simple ratio |
|---|---|---|---|
| uniform in ratio | **1.129** | 2.235 | 11 |
| arc length in timbre | 0.697 | **2.670** | 19 |

Arc-length reparameterisation moves in the right direction — it concentrates waypoints where the
ground moves fast (11 → 19) — but cuts variability only **1.6×** against a sealed 3× bar, and the
**worst step gets worse**. Verdict: `NOT_LINEARISABLE_BY_REWEIGHTING`.

**The reason is structural, not statistical.** `u(α)` is deterministic — no RNG anywhere in
`predict_partials` or the Brody fit — so its roughness is not estimation noise that smoothing could
remove. It *is* the soundspace. And §4 says why: coincidences appear and vanish **discontinuously**
at every p/q below the horizon, so ratio space is **punctuated by coincidence events**, not a smooth
manifold. A densely punctuated space cannot be linearised by reparameterising a continuous
coordinate.

> **What would actually work.** Stop treating the path as continuous. Choose **waypoints over tree
> nodes**, spaced by measured timbral distance rather than by ratio distance, with the horizon
> deciding which nodes are eligible. That is what Stern–Brocot navigation already *is* — the
> linearisation belongs in waypoint *selection*, not in the interpolator.
>
> Concretely, for `Landscape`: keep the existing gradient fields, but score candidate next-hops by
> Δu rather than by ratio-histogram distance, and skip nodes above the horizon. All of it is
> offline-computable; nothing is added to the audio thread.

## 6. Do the criticality measurements need re-running for the maps? **No.**

- The shipped maps are **already in the musical regime**: median modulation index **1.078**, 93.6%
  at or below 3.0, max 5.0. They do not inherit the I = 8 error of §0.
- The maps' `crit` field is a **layout** property — the angular-gap / void-rim score of the 2D
  embedding (`gpu_paths.py:52`) — not an approximability measure, so the saturation result does not
  govern it.
- `phase3/butterfly_map_study.py` already tested the CF-sum criticality insight against the shipped
  maps and found it **not confirmed** (op-count dominates at whole-config level; only a weak
  single-op prominence signal survived). Nothing here overturns that, and §4–§5 do not depend on it.

What the maps *lack* is a **timbral-distance field** — §5's Δu between adjacent nodes. That is new
work, not a re-run.
