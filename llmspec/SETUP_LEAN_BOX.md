# Bootstrapping the lean GPU box (6–8 GB VRAM) for llmspec work — 2026-10-01

Purpose: take extraction and the descriptive training queue off the 4090. A Claude Code session on that box reads this
file first. Hostnames, keys and the branch name are Will's choices; placeholders are marked `<...>`.

## 0. What the box can and cannot run
- **Can:** every extractor (all run under a 6 GB cap: `stage3_extract.py`, `armb/b4_extract.py`, `stage3_extract_mf.py`
  is CPU-only anyway); the OLMo plan-(1) extraction (three stage-2 ingredient finals, stage-1 end gain-folded, later the
  stage-1 trajectory); the DESCRIPTIVE Q4 extension queue (`armb/ext_queue.sh`) with a smaller micro-batch; arm A's
  calibrator fine-tunes later.
- **Micro-batch:** 70M training uses micro-batch 8 ≈ 12 GiB (fp32 logits dominate). ≈ 6 GB at micro-batch 4, ≈ 4 GB at 2.
  Changing it is a disclosed method change (fp16 accumulation order); fine for descriptive runs, NOT for known-answer
  reruns that must match a reference config (A0r-type).
- **Cannot:** paired/known-answer reruns of 4090 runs; anything needing > VRAM.

## 1. System
```
# Linux + NVIDIA driver (nvidia-smi works); git; python3.12; rsync; ssh
git clone https://github.com/ErnestG4/ARS.git ~/ARS && cd ~/ARS
git checkout -b llm-spectra-lean origin/llm-spectra      # own branch; Will merges; never push from the box without Will
python3 -m venv ~/fmexplorer && ~/fmexplorer/bin/pip install -U pip
~/fmexplorer/bin/pip install torch --index-url https://download.pytorch.org/whl/cu128   # pick the wheel for the driver
~/fmexplorer/bin/pip install numpy scipy pandas pyarrow huggingface_hub safetensors transformers matplotlib requests
```
Code hard-codes `/home/combust/fmexplorer/bin/python3` and `/home/combust/fmexplorer/criticality_tool` in places
(`armb/queue_runner.py`, `armb/ext_queue.sh`, `checkrun.sh`, `armb/train.py` ROOT via `__file__` is fine). Either use the
same user/paths (`combust`, `~/fmexplorer`, `~/fmexplorer/criticality_tool` as a symlink to the clone) or grep and patch
`PY=`/`ROOT=` lines on the lean branch.

## 2. Disk guard
`remote_st.check_stop()` refuses to proceed below 10 GB free on `remote_st.HOST_DISK` (the WSL host drive, `/mnt/f`). On a
native Linux box there is no such mount: `stage3_extract_mf.py` already rebinds the guard to the output filesystem; for `stage3_extract.py` /
`b4_extract.py` add the same rebinding (or set `LLMSPEC_DISK=/` if that env hook is added) before any run. Keep ≥ 10 GB
free on the data disk; never bank full checkpoints locally (stream HF → RAM → GPU).

## 3. Reaching spot (checkpoint store, 128 GB CPU box)
- `~/.ssh/config`: `Host spot` → 10.0.0.225, user combust, key of Will's choosing (never load a passphrase key into an
  agent; Will's rule). `ssh spot 'who'` must work non-interactively (BatchMode) before any training: `train.py` uploads
  every checkpoint to `spot:~/llmspec_armb/ckpt/<arm>/` and `b4_extract.py` pulls them back.
- Spot rules are binding: `~/remote-claude-rules.md` on spot (tmux `claude` only, nice, no sudo, scratch in
  `~/tmp/claude/`, log actions in `~/claude-work.log`).

## 4. Claude Code on the box
- `~/.claude/CLAUDE.md`: copy the global rules (no Co-Authored-By / Generated-with lines, ever; Will pushes; seal before
  data; propose deletes). Commit identity `Combust <combust@thespot.chat>`.
- Read `llmspec/NEXT_SESSION_BRIEF.md`, `llmspec/NOTES.md` §1 (machine rules) and §4 (running now), then the queue.
- Two sessions, one repo: the lean box works on `llm-spectra-lean`; it edits NOTES only under a `## 4-lean` heading to
  avoid merge conflicts; Will merges into `llm-spectra`.
- Long jobs: detached (`setsid nohup … &`), a completion wait re-armed on every 2 h expiry, plus an hourly in-session
  alarm (CronCreate) that checks jobs and launches the next sealed item. Never `pkill -f`; explicit PIDs.

## 5. First jobs for the box (in order)
1. Smoke: `~/fmexplorer/bin/python3 llmspec/verify_fetch.py` and `verify_mf_extract.py` (CPU); then one layer of
   `stage3_extract.py pythia-70m step143000` to confirm the GPU path and the disk guard.
2. OLMo plan (1) premise/endpoint extraction once Will seals its prereg (draft: `OLMO_PREMISE_PREREG.md` when it exists).
3. If the 4090 is reclaimed: continue `armb/ext_queue.sh` here with `--micro 4` (to be added to `train.py` on the lean
   branch as a CLI flag; default unchanged), resuming from the `staging/<arm>/resume.pt` rsynced from the 4090 box.
