# Shapes of LLM weights over training

## In plain language

A language model stores what it learns in weight matrices. This project asks what those matrices look like as a
model trains, and which features of their structure are real rather than noise. It studies their **singular-value
spectra**: how large each singular value is, and how the values are spaced.

**Data:**
- the released training checkpoints of **Pythia** (70M, 410M, 1B and 1.4B), including ten independently seeded runs
  (PolyPythias) at 410M and 70M;
- **OLMo 2 1B**;
- five 70M training runs of our own (**Arm B**). These vary the learning-rate warmup and swap the optimizer (AdamW vs
  Muon), with dense checkpoints over the early steps the released runs skip.

**Method.** Borrowed from random-matrix theory: compare each measured statistic with what a random matrix of the same
shape gives, and call something structure only if it survives that comparison and its controls.
- **Every test was pre-registered.** Its decision rule was committed before the data it judges existed.
- **Every null is reported as a null.**
- Where a check proved flawed after it ran, the flaw is disclosed beside the result, and the rule is not changed.

**What we found, in brief:**
- **The fine-scale spacing of the bulk of singular values is what a random matrix gives,** at every checkpoint of
  Pythia 410M, 1B and 1.4B and in all ten 410M seeds. At 70M the test is not powered at the same tolerance, and
  nothing departs beyond the test's own noise.
- **Structure forms in the largest few directions, early.**
  - Query, key and output matrices lose effective rank between roughly steps 128 and 2000; value matrices do so
    later.
  - Induction heads, and the output-value circuit's departure from randomness, appear between steps 512 and 1000 in
    every seed.
- **The early turning points are tied to the learning-rate schedule** (changing the warmup changes the trajectory),
  but none of step count, warmup end or learning-rate integral simply re-times them. The schedule reshapes the
  curve.
- **The Q/K rank collapse happens under both AdamW and Muon.** Muon delays it and leaves it shallower by step 3000.
- **Several attractive readings did not survive their controls and are withdrawn:**
  - a late per-head drift, which equalled the calibrator's own bias;
  - "the ordering of the bulk singular values carries function";
  - "local reordering is functionally inert".

## Headline results

Full table, gates and caveats: [FINDINGS_MEMO.md §1](FINDINGS_MEMO.md#1-headline).

| # | Question | Status |
|---|---|---|
| 1 | Bulk spacing statistics stay random-matrix (β = 1) at every checkpoint | **NULL** at 410M–1.4B (260/260 cells per model; 10 seeds). NOT ESTABLISHED at 70M (unpowered at 0.010) |
| 2 | A late per-head-Q departure from β = 1 | **NOT ESTABLISHED** (equals the calibrator's own bias) |
| 3 | Multi-peak ("Diffract-style") attention spectra exist | Pythia: none. OLMo: 13.3% of Q heads at stage-1 end, largely gone by the final checkpoint |
| 4 | Local statistics on peaked spectra | NOT LICENSED as registered |
| 5 | Induction heads form between steps 512 and 1000 | **REPLICATES** at 3 sizes; **SEED-ROBUST** 10/10 |
| 6 | The OV circuit leaves its random null before QK | **REPLICATES**; SEED-ROBUST (at the resolution limit) |
| 7 | Heads share their top input directions | **REPLICATES**; SEED-ROBUST |
| 8 | K's top directions concentrate on the rotary (position) dimensions | Holds in 9/10 seeds, but the registered test is SEED-DEPENDENT |
| 9 | Trained spectra leave Marchenko–Pastur by steps 1000–2000 | **REPLICATES**; SEED-ROBUST |
| 10 | Update rank rises ≥ 3× over training at constant learning rate | 1.4B only; not size-general; SEED-DEPENDENT |
| 11 | The ordering of bulk singular values carries function | **NOT ESTABLISHED** (size explains ≥ 2/3 of the effect) |
| 12 | Compression runs as a layer-ordered wave (Liu) | NULL for V at 1.4B; OPPOSITE ORDER for Q/K at 70M, carried by layer 0 |
| 13 | Change points align with training events | NOT LICENSED |
| 14 | What anchors the early turning points (Arm B) | **NO SIMPLE ANCHOR** |
| 15 | Early updates are low-rank (Arm B) | INCONCLUSIVE (Q/K yes, V/O/MLP no, descriptively) |
| 16 | AdamW vs Muon (Arm B) | Timing and depth of the Q/K collapse depend on the optimizer |

Status words: NULL = a registered null that held; REPLICATES / SEED-ROBUST / SEED-DEPENDENT = replication verdicts
across sizes and seeds; NOT ESTABLISHED = a reading that did not survive its test; NOT LICENSED = the instrument could
not answer. Details: [FINDINGS_MEMO.md](FINDINGS_MEMO.md) (status vocabulary at the top).

## Open leads

Each lead needs its own pre-registration before it is read as evidence. Details:
[FINDINGS_MEMO.md §6](FINDINGS_MEMO.md#6-open-leads-for-specialists-none-of-these-is-running).

1. **OLMo multimodality that fades:** 13.3% of Q heads are multimodal at stage-1 end, and sub-floor after
   mid-training. When do the peaks appear and fade?
2. **Dead rows in OLMo Q:** near-zero modes in 170 heads at stage-1 end, and 92 at the final checkpoint.
3. **The low-rank update burst at steps 4k → 5k** in V/O/MLP-out (1.4B). Unexplained, and absent at 70M.
4. **Q/K lower-decile departure from Marchenko–Pastur** from ~8k steps, 44–80× above the precision bound.
5. **K's concentration on rotary dimensions:** robust as a concentration, seed-dependent as registered.
6. **A late loss spike (seed 4, 96k–128k steps)** as a natural experiment.
7. **The bulk singular VECTORS.** Only the bulk singular values were tested. A hint (G2c, under 0.001 nats) says that
   rotating the bulk directions costs more than reordering the values.
8. **Arm B leads** (70M): the shape of the Q1 misfit, the wave without layer 0, a phase-matched Q3 reference, and a
   bulk count test with a measured null rate. See
   [armb/ARMB_FINDINGS.md §8](armb/ARMB_FINDINGS.md#8-open-leads-none-of-these-ran-each-would-need-its-own-pre-registration).

## Where things are

| file | what |
|---|---|
| [FINDINGS_MEMO.md](FINDINGS_MEMO.md) | The summary: every claim with its gate and status, the confounds, the instrument notes, what was not done, and the open leads |
| [armb/ARMB_FINDINGS.md](armb/ARMB_FINDINGS.md) | Arm B: the five own training runs, Q1–Q4, the bulk null at 70M, and the seed-1 identity check |
| STAGE1/2/3_FINDINGS.md, STAGE3_REPL_FINDINGS.md, STAGE3_SEED_FINDINGS.md | The stage documents that hold the numbers, tables and commits |
| STAGE3_PREREG.md, STAGE3_REPL_PREREG.md, STAGE3_SEED_PREREG.md, armb/ARMB_PREREG*.md | The pre-registrations, with dated amendments |
| results/ | Banked outputs (JSON / parquet). Each is written by a committed script named in the stage documents |
| NOTES.md | The working state file (operational log; not needed to read the results) |

## Reproducing

- Python 3 with PyTorch (CUDA), numpy, scipy and transformers.
- Checkpoints stream from the Hugging Face Hub (EleutherAI Pythia / PolyPythias, AllenAI OLMo 2). Weights are not
  redistributed here; only derived statistics are.
- Arm B training needs a GPU. The analysis stages re-run from the banked caches and results.
- Paths in the scripts and logs refer to the original machines and need adapting.

## License

Code: AGPL-3.0 (the repository's [LICENSE](../LICENSE)). Pythia and PolyPythias are Apache-2.0; OLMo 2 is Apache-2.0.
This project publishes derived statistics only, no model weights.
