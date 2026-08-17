# Reproducing the numbers

Three tiers, by how much of your time they cost. Start at the top; each tier is
useful on its own, and you never have to run the expensive one to check the
cheap one.

Requirements: Python 3 with `numpy`, `scipy`, `mpmath`. Nothing else. No data
downloads are needed for any arithmetic or synthetic arc (the neuroscience ports
need external recordings; see the per-arc notes).

---

## Tier 1 — check the record against itself (~4 minutes)

```sh
python3 verify_all.py
```

Re-derives every arc's banked claims from its committed artifacts and exits
nonzero on any regression. This does not recompute the science; it checks that
the documents and the artifacts agree and that sealed artifacts are unmodified.
See `AUDIT.md` for exactly what that does and does not establish.

## Tier 2 — re-run the calibrators (minutes)

The calibrators are the part worth checking first, because they are the only
components with **known answers**. If they pass, the instrument reproduces cases
where the truth is independently known; if they fail, nothing downstream matters.

Worked example, `derivflow` (each is standalone; run from the repo root):

```sh
cd derivflow
python3 track0_harness.py       # Hermite self-map: H_n' = 2n·H_{n-1} places
                                #   roots EXACTLY. ~13 s. Checked against mpmath
                                #   at 40 digits; worst deviation 1.35e-13 of
                                #   local spacing over 480 composed steps.
python3 free_conv.py            # free-convolution evaluator vs two closed forms
                                #   (semicircle stability, Bernoulli/arcsine),
                                #   plus a predicted atom threshold. ~1 min.
python3 reference_v2_gates.py   # the two permanent known-answer gates that
                                #   bracket the unfolding reference: a maximally
                                #   rippled input (lattice) and a maximally
                                #   smooth one (Hermite through the FULL path
                                #   against exact H_{n-k}). ~30 s.
```

Other arcs keep their calibrators in the same shape; `phase22a/verify_calibrators.py`
runs the synthetic zoo (Poisson, GOE, GUE, clustered, picket-fence) end to end.

## Tier 3 — recompute the science (hours to a day)

Only needed if you want the measurements themselves rather than the record of
them. Costs below are measured, single machine.

| arc | command | cost | produces |
|---|---|---|---|
| derivflow, main grid | `python3 science_dense.py` | 5.4 h | `science_dense_grid.json` |
| derivflow, scale arm | `python3 step3_parallel.py` | 23.5 h (both arms) | `step3_scale_law.json` |
| derivflow, mechanism | `python3 step2_env_decomposition.py` | 78 min | `step2_env_decomposition.json` |
| derivflow, mechanism | `python3 step2b_isoconfig.py` | 86 min | `step2b_isoconfig.json` |

The memory-bandwidth wall binds before the core count does: the replicate pool
nets roughly 1.3–2× on five workers, not five.

### Randomness is enumerable, not merely seeded

Every replicate derives from `SeedSequence(20260811)` with a child allocation
fixed **in advance**:

- `.spawn(96)` — children 0–47 are the iid replicates (16 per degree, degree
  ascending), 48–95 the GUE replicates.
- the `n = 16384` arm re-spawns to 128 — children 96–111 iid, 112–127 GUE.
  Children 0–95 are never reused.

So the ensemble is enumerable before it is run, and selecting a favourable
replicate after the fact is impossible by construction rather than by policy.
A rerun reproduces the identical intended computation; an interruption is
wall-clock only.

---

## If you only want one number

The measured spacing statistic for `derivflow` — 20 values of `k` × 2 seed
ensembles × 4 degrees, each the mean of 16 independent seeds with its standard
error — is:

```
derivflow/science_dense_grid.json    .data.<ensemble>.<n>.<k>.{mean, sigma_mean}   (n ≤ 4096)
derivflow/step3_scale_law.json       .data.<ensemble>.<k>.{mean, sigma_mean}       (n = 16384)
```

Everything else in that arc — the functional form, its parameters, the
transition scale — is an inference *from* that table, and the table is the only
part that is a measurement. Each cell was also computed on two deliberately
biased smoothing bandwidths as an instrument check; those arms sit alongside the
primary values in the same files under `mean_epsraw` / `mean_2eps`.

## Where the reasoning lives

- `derivflow/TRACK0_FINDINGS.md` — findings §§1–14 in order, including the
  superseded first result under its banner and the instrument review that
  produced it.
- `derivflow/TRACK0_SCOPE.md` — §4 defines the instrument; §9 is the literature
  status, dated.
- `derivflow/seals/` — the pre-registered adjudication rules and their
  disclosure ledgers, written before the data they judge.
- `AUDIT.md` — how to attack all of the above.
