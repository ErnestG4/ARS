# Maintenance backlog — deliberately parked, do not action mid-arc

## git object store (noted 2026-08-19, parked on the owner's call)
Every commit prints two warnings:
  - "The last gc run reported the following ... remove .git/gc.log"
  - "too many unreachable loose objects; run 'git prune'"

Fix, to be run only when NO session is mid-work (other sessions write `khinchin/data/`,
`phase34e/data/`, `derivflow/`):
    git prune && rm -f .git/gc.log && git gc
Harmless to defer: it is disk hygiene, not corruption. The warnings are noise on every commit,
which is its own small cost — it trains the eye to ignore git's stderr, and a real error would
arrive in the same channel.

## BLAS thread oversubscription (noted 2026-08-19)
OpenBLAS here is built MAX_THREADS=64 on 24 cores; concurrent sessions each spawning full-width
BLAS thrash a 15 GB box. Suspected cause of the 2026-08-18 "timeout" that was really a 3-minute
job. Mitigation when sessions overlap:  export OMP_NUM_THREADS=8

## sealgen.sh and long-running generators (2026-08-23)

`sealgen.sh` commits the generator and then RUNS it in the foreground of the same
call. Any generator that outlives the shell's timeout is killed mid-run — the
seal is committed and correct, but no output is produced, and the failure looks
like a generator that produced nothing rather than one that was interrupted.

Hit by `overnight_2026_08_23/mutate_module_baselines.py` (12 GPU script runs,
~3 min). Workaround used: seal with sealgen, then launch detached via
`setsid nohup ... &` and wait on the PID with `kill -0`.

NOT fixed in sealgen itself, deliberately: making it background its runs would
break the CHECKRUN line it emits, which is what the commit-msg hook checks
outcome claims against. Better fix if this recurs: a `--detach` flag that seals,
launches, and prints the PID instead of a CHECKRUN line — so the absence of a
CHECKRUN line is itself the signal that the outcome is not yet known.
