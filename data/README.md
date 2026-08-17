# data/ — external datasets are fetched, not redistributed

This directory is git-ignored: the datasets here are third parties' work and are
not ours to republish. This file records what the checks need, where to get it,
and how to know you got the right thing.

## Required by the verification board

`verify_all.py` needs exactly one external file. Without it, two checkers report
`SKIP (missing data)` rather than failing — the board stays honest instead of
showing a red row that means nothing.

| file | what it is | where |
|---|---|---|
| `odlyzko_zeros1.txt` | the first 100,000 nontrivial zeros of ζ(s), imaginary parts, one per line | A. M. Odlyzko's tables, `https://www-users.cse.umn.edu/~odlyzko/zeta_tables/` (file `zeros1`) |

Check you have the same bytes we used:

```sh
sha256sum data/odlyzko_zeros1.txt
# 3436c916a7878261ac183fd7b9448c9a4736b8bbccf1356874a6ce1788541632
```

Expected shape: 100,000 lines, first value `14.134725142`, second `21.022039639`.

## Everything else here

Other files in this directory are intermediate results produced by the runners
in this repository, not inputs. They regenerate; see `REPRODUCE.md`. The
neuroscience ports additionally need recordings from CRCNS, Allen, and IBL,
which have their own access terms — `cross_substrate/crcns_client.py` reads
credentials from `~/.netrc` and never stores them.
