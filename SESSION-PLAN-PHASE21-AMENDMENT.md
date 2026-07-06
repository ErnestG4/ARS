# SESSION-PLAN-PHASE21 — Phase 20.5 amendment

Phase 21 (GRB transition-window analysis) was discussed but not yet
spec'd as a full session-plan file at the time Phase 20.5 ran.  This
file records the integration points so when the Phase 21 plan is
written, these amendments are pre-baked.

## Tier 3 verdict-map additions

The Phase 21 verdict map gains two outcome rows:

| outcome | reading |
|---|---|
| ARS classification matches published QPO with metastable-middle transition shape | Strong validation of central-engine-evolution timescale; transition shape itself becomes a physical observable. |
| ARS classification shows period-doubling cascade structure during prompt emission | Novel finding: GRB prompt emission may have nonlinear-dynamics signature beyond what current QPO methodology captures. |

Both verdicts depend on `transition_diagnostic.characterize_transition`
being applied to per-(event, instrument) trajectories.  See §7.ter.28
for the diagnostic's documented limitations:

- Period-doubling cascade detection requires trajectory variation
  beyond quadrant-label resolution; on the logistic-map sweep the
  detector currently fails because the joint_q_profile coarse-grains
  away the period-2 / period-4 / period-8 structure.  Phase 21's
  application of `characterize_transition` should therefore expect
  no period-doubling signature unless GRB transitions span quadrant
  boundaries cleanly, OR a finer-resolution classifier is
  substituted.
- Metastable-middle detection requires the intermediate state to
  occupy ≥ 30 % of the transition window with a distinct quadrant
  label; brief excursions or sub-quadrant-resolution intermediates
  will not register.

## Tier 3 procedure step 5

> Apply `characterize_transition` to per-(event, instrument)
> trajectory; report shape classification, parameters, and
> period-doubling signature where present.

## Tier 4 falsification step

> Apply `characterize_transition` to surrogate-generated trajectories;
> verify surrogates produce different transition shapes than empirical
> data, or document that they don't.

## Compatibility note

`characterize_transition` requires a trajectory DataFrame with at
least the column `primary` (per-sub-window quadrant label).  The
GRB analysis pipeline's sub-window classification output should
match this schema; if Phase 21 introduces additional columns
(e.g., per-instrument or per-energy-band sub-classification), the
diagnostic accepts the DataFrame and ignores extra columns.

## What this amendment does NOT cover

- The Phase 21 GRB data acquisition pipeline (which instruments,
  which events, which timing precisions).
- The Phase 21 falsification surrogate panel for GRB-class signals
  (Phase 18 surrogates + topology-aware Hawkes is general but may
  need GRB-specific augmentation, e.g., shot-noise surrogates).
- The Phase 21 verdict map's other outcome rows.

These are written when the full Phase 21 session-plan is drafted.
