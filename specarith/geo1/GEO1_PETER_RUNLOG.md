# GEO1 Peter seal: fresh-run log

## Launch 1 (2026-10-31 01:01 PDT): STOPPED by the first cost check

- **Launch.** `run_peter_fresh_spot.sh peter_fresh 16` ran in tmux claude:geo1p with spot load at 36 of 56. The first
  check fired after 5 chunks, at cpu/model = 1.810 against a stop threshold of 1.25×. The launcher killed xargs and wrote
  STOPPED.
- **Chunk cost.** The 16 chunks that finished (000–015, t ≤ 1,160,000) took 99–130 CPU-s each, mean about 120 s per 10⁴ t.
  That is about 12 ms per t, against the 6.0 ms model.
- **Cause: a pricing error of mine.** The 6.0 ms per t was taken from the per-discriminant benchmark: `quadclassunit`
  takes 4.0–4.9 ms per d at 10¹²–10^13.5. But a trace has on average 2.18 valid discriminants (t² − 4)/u², counted from t
  alone; the dev range near t = 9·10⁵ has the same 2.18. So 2.18 × ~5 ms ≈ 11 ms, which matches the ~12 ms measured.
  The corrected price is about 12 ms per t: about 6.7 core-hours, or about 30 minutes wall at 16 processes.
- **Process slip.** Killing xargs did not kill its running children. Five orphaned workers (chunks 016–020) kept running
  for about 45 s. Their sh and python PIDs were found and killed by explicit PID. No such worker is left. The Step 1
  launcher has the same pattern.
- **Outputs.** The partial outputs (parts 000–015) were moved, unread, to
  `~/tmp/claude/specarith/geo1/peter_fresh_stopped_cost/` on spot. Nothing from them has been read or copied. No
  statistic exists.
- **No relaunch without Will.** A relaunch needs the launcher's cost model changed from 6.0 to 12.0 ms per t. The launcher
  is a sealed file (it is in the stamp manifest), so that change would be a logged post-seal deviation affecting only the
  cost guard. Any fix for the orphaned children also needs Will's decision.
