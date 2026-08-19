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
