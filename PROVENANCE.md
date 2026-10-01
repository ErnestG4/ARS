# Provenance of this repository

This is the full development history of the ARS repository: all 13 branches and 1,441 commits, published 2026-09-30.
It was prepared in a fresh clone; the development repository itself was not modified. Two changes were made, and
nothing else:

1. **Commit messages:** AI-assistant attribution trailers were removed (`Co-Authored-By: Claude …`,
   `Claude-Session: …` links). The rest of every message is unchanged.
2. **Third-party files:** seven copies of other authors' papers were removed from all of history. They are not ours to
   redistribute (see `comb/lit/README.md`). The citations remain in `phase34d/lit/LIT_SUMMARY.md` and
   `comb/lit/README.md`.
   - `phase34d/lit/{chen_refined_2019,katz_2017,rudnick_waxman_2019}.{pdf,txt}`
   - `comb/lit/KRR_arxiv2001.09513.tex`

Every commit keeps its original author, committer, dates and file tree, apart from change 2. This was verified
commit by commit for all 1,441 commits.

## Commit hashes cited in the documents

Change 1 changes commit hashes, so the hashes the documents cite (for example "sealed at 766c92c") are
development-repository hashes. `provenance/cited_commits.tsv` maps every one of the 182 cited hashes to its published
commit here:

| status | count | meaning |
|---|---|---|
| development-history hash | 57 | the same commit, published here under a new hash |
| pre-2026-09-21 hash | 123 | on 2026-09-21 the development history was rewritten to normalise author e-mail addresses (tree, date and message unchanged); the map gives the published commit |
| amended before publication | 1 | `ca0d94b`; the published commit is the amended version (same date and message) |
| merge redone before publication | 1 | `458a697`, never pushed; the published merge is `b0046d509b59` |

Commit hashes quoted inside commit messages were updated to the published hashes automatically.

## Checking integrity

- **Sealed code:** pre-registrations list the sha256 (or a 16-hex-digit prefix) of each file they freeze, and
  `llmspec/armb/B4_SEAL.json` is the manifest the Arm B analysis verified before running.
- **Sealed inputs:** each Arm B result JSON records the sha256 of every cache file it read.
- **Checkers:** `CHECKRUN … EXIT=… PASS/FAIL` lines are machine-written by `checkrun.sh` when a checker runs.

Git dates are set by the author's machine. The independent timestamp is the Zenodo deposit of tag `v2026.09.30`.
