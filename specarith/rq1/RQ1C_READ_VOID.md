# RQ1-c sealed read — VOID (cmp mismatch), 2026-10-29

Seal `RQ1C_SEAL.md` (tag `rq1c-seal`, b936b358), Bitcoin-attested (blocks 973605 / 973607) and verified on two
explorers (15f2080b) before the read. Launched on spot 2026-10-28 16:57 PDT after a load check (load 1.0, 114 GB free).

## What ran (`run_rq1c_read_spot.sh`)
- Mount guard: passed.
- `sha256sum -c rq1c_read_pins.sha256`: all 18 OK (`results/rq1c_read_void/pins_check.txt`).
- `sha256sum -c` on the 30,200 segments: zs2 10,000 / zi 10,100 / zw 10,100 OK, exit 0 each.
- read1 (29,844 s wall) and read2 (31,481 s), each exit 0; CPU 70,304 s per read, 0.69× the model.
- `cmp read1.json read2.json`: **differ at byte 9584, line 397 → VOID (cmp), as sealed (§5, condition 1).**

## Cause (diagnosed after the VOID; no value printed)
Walking both JSONs: 19 leaves differ, all of them CPU-timing fields — `cost[*].cpu_s`, `cost[*].ratio` and
`cpu_core_h` — which `rq1c_read.py read` writes into the output JSON (the Cost class records `time.process_time()`
per stage). Every other field is identical between the two reads. So the mismatch is a defect of the read code: its
output carries run-dependent timings, and the docstring's claim that the double read compares byte-identical was never
true for `read` mode (the `repro` and `zw34d` modes ran once each and were not double-read). It was not caught before
sealing; it is mine.

## Disclosure
`rq1c_read.py read` prints its verdict line to the log, so the outcome lines of both reads were visible on completion
(`results/rq1c_read_void/read1.log`, `read2.log`, last lines). No other value was inspected before this note.

## Status
VOID as sealed. No redesign, rerun or ruling taken: the choice is Will's. Files: `results/rq1c_read_void/` (both JSONs,
logs, cmp, pins and segment checks, timing).
