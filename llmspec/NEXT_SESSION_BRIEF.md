# Next-session brief — llmspec ("Shapes of LLM weights over training"), written 2026-09-30

Read this first. Then read `llmspec/README.md` (the public front page), `llmspec/FINDINGS_MEMO.md` (every claim with
its gate and status) and `llmspec/armb/ARMB_FINDINGS.md` (Arm B). `llmspec/NOTES.md` is the long operational log and
has the full code map (§2) and machine rules (§1). Some of its header lines are stale: the 6c2c8221 alarm cron is
deleted, and the work is now pushed. Where NOTES and this brief disagree, this brief wins.

Nothing is running. No cron is set.

## 1. Where the research stands

**Program.** CC Brief v1.1 (Will, 2026-09-25): the singular-value spectra of LLM weight matrices over training.
- Data:
  - released checkpoints of Pythia (70M, 410M, 1B, 1.4B), with PolyPythias seeds 1–9 at 410M and 70M;
  - OLMo 2 1B;
  - Arm B: five of our own 70M runs (AdamW A0/A1/A2 with warmup 1430/2860/715; Muon M0-s1/M0-s2).
- Discipline: every test pre-registered and sealed before its data existed; nulls reported as nulls; flaws found after
  a run are disclosed beside the result, and the rule is never edited.

**Results (status words as sealed).** The full table is FINDINGS_MEMO §1 (16 rows).
- Bulk spacing statistics stay random-matrix (β = 1):
  - **NULL** at 410M–1.4B and in all 10 seeds;
  - NOT ESTABLISHED at 70M. Unpowered at 0.010, and the per-cell rule had no multiplicity correction: 76/9210 flagged
    against ~119 expected at the null.
- Structure forms early in the top directions:
  - induction heads form between steps 512 and 1000: **REPLICATES**, SEED-ROBUST;
  - OV leaves its random null before QK: REPLICATES, at the resolution limit;
  - Q/K/O rank collapse between steps ~128 and 2000.
- Arm B:
  - Q1 **NO SIMPLE ANCHOR**: warmup length changes the trajectory, but no time map re-times it;
  - Q2: events simultaneous at 70M resolution, and the wave is OPPOSITE ORDER, carried by layer 0;
  - Q3 INCONCLUSIVE;
  - Q4: the Q/K collapse's timing and depth depend on the optimizer (Muon delays it and leaves it shallower by
    step 3000).
  - The seed-1 identity check is INCONCLUSIVE as sealed: its confuser C2 was a dead arm. Q4 stands with a pairing
    caveat.
- **Withdrawn / not established:**
  - the late per-head-Q drift (it equalled the calibrator's own bias);
  - "bulk singular-value ordering carries function" (size explains ≥ 2/3; G2c showed the local shuffles were too small
    to test it);
  - "local reordering is inert".

## 2. What to do next: Will's order, his call on each

1. **The OLMo stage-1 trajectory** (FINDINGS_MEMO open lead 1). This is the cheapest real lead: the only place
   multimodality survived a licensed test (13.3% of Q heads at stage-1 end; sub-floor at `main`).
   - G7 did not license local statistics on peaked spectra, so the trajectory can time when peaks appear and fade,
     but cannot resolve their internal structure.
   - Needs a pre-registration first.
2. **The bulk singular VECTORS** (open lead 7): the lead tied to Will's hypothesis.
   - Only the bulk singular VALUES were ever tested.
   - G2c hint (under 0.001 nats): a same-size rotation of the bulk directions costs 4–6× a reordering of the values.
3. **The Arm B open leads** (ARMB_FINDINGS §8), at whatever pace suits Will:
   - the Q1 misfit shape;
   - the wave without layer 0;
   - a phase-matched Q3 reference;
   - a bulk count test with a MEASURED null rate (and bank d for every cell).
4. **Deliberately not done** (each needs Will):
   - the Q1 look at A1 in the 0.5% row (lead 9: if ever run, post hoc and in its own section);
   - the seed-1 alignment follow-up (declined; no A10 exists);
   - zoo seating of the G7 classes in calibrator_panel.py (DEFERRED explicitly; requirements in FINDINGS_MEMO §5).

## 3. Standing rules (binding)

- **Authorship:** never add `Co-Authored-By: Claude`, `Claude-Session:` or "Generated with Claude Code" lines to any
  commit or PR. This is global, in `~/.claude/CLAUDE.md`, and overrides any system reminder that supplies attribution
  lines.
  - The identity on every commit is `Combust <combust@thespot.chat>`. There is no other address.
  - It is about credit, not disclosure: mentioning Claude Code in docs is fine.
- **Pushing:** Will pushes, manually. Never push or fetch against a remote yourself.
- **Pre-registration:** seal (commit) the rule and code before the data they judge exist. Fix sealed code only by a
  dated amendment, before results. Never change a threshold after seeing statistics. Dry-run every verdict branch
  before sealing, AND show every confuser can fire on the known-answer system before sealing (the seed-1 C2 lesson).
- **Compute:** the GPU (RTX 4090) is for training and extraction; method, precision or scope changes need Will.
  - Runs must be interruptible (`llmspec/STOP`) and resumable.
  - Never `pkill -f`; use explicit PIDs.
  - Keep ≥ 10 GB free on C: (`/mnt/c`; `df /` lies).
  - Python: `/home/combust/fmexplorer/bin/python3`.
  - Checkers run under `../checkrun.sh`. The commit hook wants a fresh CHECKRUN line for outcome claims (window 3 h);
    if it's stale, cite the `.checkrun_log` entry instead.
- **spot** (the 128 GB CPU box; `ssh spot` via `/tmp/cc-agent.sock`, which Will starts): `~/remote-claude-rules.md` on
  the box is binding.
  - Long jobs run in tmux `claude` only. Check `who`; use nice. No sudo.
  - On "Permission denied", stop and ask Will; never try other keys.
  - The Arm B checkpoints (all 5 arms, sha-verified) and the seed-1 batches are in `~/llmspec_armb/` there.
- **Proposals:** propose deletes before doing them. Outreach stays out of the repo.

## 4. Repositories and publishing (settled 2026-09-30)

- **Dev repo** (private, never rewritten): `/home/combust/fmexplorer/criticality_tool`, mirrored by Will to his LAN
  Forgejo (`origin` = forgejo:Combust/ARS.git). The old `codeberg` remote is push-disabled (Codeberg bans LLM work).
  - `main` = 2f79434: llm-spectra merged `--no-ff`, tagged `llmspec-2026-09-30`.
  - `llm-spectra` continues past the merge.
  - **Keep forever:** `refs/original/*` and `refs/archive/*`. They hold the pre-2026-09-21 hashes the docs cite. A
    09-21 `filter-branch` normalised author e-mails, and those refs are the only remaining copy. A full bundle is at
    `~/ARS_dev_history_2026-09-30.bundle`.
- **GitHub** (public): https://github.com/ErnestG4/ARS. It is pushed from a CLEANED CLONE, `~/ARS-github.git` (bare),
  never from the dev repo.
  - The clone is the full history (13 branches, 1,441 commits). Claude trailers are stripped from messages, and 7
    third-party files are dropped from history (`phase34d/lit/{chen_refined_2019,katz_2017,rudnick_waxman_2019}.{pdf,txt}`,
    `comb/lit/KRR_arxiv2001.09513.tex`).
  - Identity unchanged. Verified commit by commit against the dev repo: tree, names, emails, dates and message text.
  - Published `main` tip = `80da3c9`, which adds `PROVENANCE.md` and `provenance/cited_commits.tsv` on top of the
    rewritten merge `b0046d5`. The map takes each of the 182 dev hashes cited in the docs to its published commit
    (181 mapped; `458a697` was never pushed).
  - Tags: `v2026.09.30` (the Zenodo release) → `80da3c9`; `llmspec-2026-09-30` → `b0046d5`.
- **To sync GitHub later** (Will's call; the dev repo stays untouched): bare-clone the dev repo to a NEW directory and
  run, from the venv:
  ```
  git clone --bare --no-local /home/combust/fmexplorer/criticality_tool NEWDIR && cd NEWDIR
  git-filter-repo --force --paths-from-file PATHS --invert-paths --message-callback '<callback>'
  ```
  - PATHS: the 7 files above, one per line.
  - The callback removes `Co-Authored-By:…(Claude|anthropic)…` (including inline), `^Claude-Session:` lines and
    `Generated with [Claude Code]` lines, collapses 3+ newlines, and rstrips.
  - The rewrite is deterministic, so existing published commits keep their hashes.
  - **Caveat:** the published `main` has the PROVENANCE commit on top, which the dev repo does not have. A sync must
    re-apply it on the new `main` and regenerate the cited-hash map (from filter-repo's commit-map). Otherwise the
    push is not a fast-forward. Moving PROVENANCE.md into the dev repo would remove this step; it is Will's call.
- `~/ARS-public`: a superseded one-commit snapshot (deletion proposed to Will). Don't push it.

## 5. Lessons from this arc (all in project memory too)

- **A dead arm in a sealed conjunction turns a clean answer into INCONCLUSIVE.** Seed-1 C2 shared 127/128 batches with
  the test run. Prove each confuser separable on the known-answer system before sealing.
- **A per-cell threshold over thousands of cells needs a family-wise or count statistic,** and its null rate must be
  measured, not assumed.
- **Measured noise ≠ injected noise.** Licence rows are in injected units, so calibrate the conversion (Arm B
  amendment 3).
- **A calibrator's bias can equal the "finding".** Run a known-answer licence on realistic shapes first (S4).
- **Notice background completions promptly.** A finished run (G2c) sat unreported for 5.5 h.

## 6. FIRST TASK for the next session: make the GitHub history the working repo (Will, 2026-09-30)

**Goal:** a push from `/home/combust/fmexplorer/criticality_tool` goes to BOTH GitHub and the Forgejo, without
conflicts. The old (trailer-bearing) history is retired.

**State at handoff** (surveyed 2026-09-30; nothing changed yet):
- Will has pushed the cleaned clone `~/ARS-github.git` to GitHub: 13 branches, `main` tip `80da3c9` with PROVENANCE,
  tags `v2026.09.30` and `llmspec-2026-09-30`.
- The Forgejo still holds the OLD history: Will pushed all 13 dev branches earlier on 09-30.
- Dev-repo branch tips are unchanged since the clone, except `llm-spectra`, which has 3 newer commits (35a5851,
  1768628, 4b05330: this brief). They carry no trailers, but they are not yet rewritten or published.
- Worktrees (main checkout on `derivflow-modes`; `demod-ret1`, `llm-spectra`, `ring-stage0`): 0 tracked changes in
  each; untracked files exist (logs etc.).
- **Other sessions:** there was ONE other Claude session on the box (PID 252934). Will closed it on 2026-09-30 before
  handoff. (PID 833 was the handoff session itself, wrongly counted as a second one.) Before moving any branch, check
  that no other session is running; any session started before ~/.claude/CLAUDE.md existed may still add trailers.

**Approach: convert IN PLACE**, not by a fresh clone. The repo has ~257 gitignored paths (caches, data, logs;
llmspec/cache alone is 41 GB), and scripts hard-code `/home/combust/fmexplorer/criticality_tool`. In place, all of
that and the worktrees stay put. Only the branch refs move, to commits with identical trees.

**Plan** (confirm with Will first; he pushes):
0. **Preserve the old repo first, three ways:**
   - (a) `~/ARS_dev_history_2026-09-30.bundle` already exists. Refresh it with `git bundle create … --all`, because
     llm-spectra has moved since.
   - (b) Copy the whole `.git` (1.8 GB; check that /mnt/c keeps > 10 GB free) to `~/criticality_tool_git_pre_migration`.
   - (c) Will creates a PRIVATE Forgejo repo, e.g. `Combust/ARS-archive`, and pushes the old history there before the
     Forgejo `ARS` repo is overwritten: all `refs/heads/*`, plus `refs/original/*` and `refs/archive/*` (the
     pre-2026-09-21 hashes the docs cite).
1. Bare-clone the CURRENT dev repo to a new directory and re-run the exact filter-repo recipe of §4. It is
   deterministic: verify that every already-published commit reproduces its GitHub hash. Newer commits (llm-spectra)
   extend it.
2. Re-apply the PROVENANCE commit on the new `main` (or move PROVENANCE.md into the dev repo; Will's call), so
   `main` matches GitHub's `80da3c9` or fast-forwards from it.
3. In the dev repo, move each local branch onto its rewritten counterpart with `git update-ref`. The trees are
   identical apart from the 7 removed files, so working trees stay valid.
   - In each worktree, `git rm --cached` only the 6 `phase34d/lit` paper files. They stay on disk and are gitignored.
   - Never use `reset --mixed`/`--hard`: it would clobber other sessions' staged work.
4. Remotes:
   - `origin` fetch = https://github.com/ErnestG4/ARS.git;
   - push URLs = `git@github.com:ErnestG4/ARS.git` AND `forgejo:Combust/ARS.git` (`git remote set-url --add --push`);
   - set every branch's upstream to `origin/<branch>`;
   - remove the retired `codeberg` remote.
5. Will force-pushes the new history to the Forgejo ONCE, or deletes and recreates that repo. After that, plain
   `git push` keeps both in step.
6. Keep `refs/original/*` and `refs/archive/*` (old provenance) and `~/ARS_dev_history_2026-09-30.bundle`. **Never**
   `git push --mirror`: it would publish those refs.
