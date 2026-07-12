# OVERNIGHT 2026-07-12 — brief (as authorized)

Four jobs. Fully pre-registered. Deterministic, seeded, unattended. Every job writes its verdict
**even on failure** — a silent null is the most dangerous object in this project.

- **GATE** — grep-confirm what LV and ks_gue actually compute. *(Already fired: found that
  `phase35a/unfold_rotnum.py:70` does a POSITIONAL slice, not a value-tail trim. It removes no
  outliers. See VERDICT_GATE.md.)*
- **A** — within-cell ISI shuffle (N=200). **Can retract the session's load-bearing claim.**
- **B** — clustered calibrator class (Cox / Neyman–Scott / gamma, swept) + unclipped signed `I_rep`
  + Brody with **both** bounds opened. **HARD STOP** if the clustered class fails its own
  pre-committed reading: the *repair* is wrong, not the class. C and D then do not run.
- **C** — census re-run on the repaired axes. **Consistency gate**, not a new result.
- **D** — the row-3 (correlational) instrument. First in the project's history. Exploratory, no
  pre-committed verdict.

## Morning read order
**VERDICT_A.md first** — it is the one that can change what the session meant.
Then B's calibrator table. C is a consistency check; if it fails, stop and re-read B. D is dessert.

## Out of scope (deliberately)
φ / PHI_CONTAMINATION (pre-registered as a *rested-instrument* job — unattended is worse than tired);
the threshold-matched `burst_frac` recompute (its framing depends on A's outcome — sequenced, not
parallel); the §7.ter.50 retro-scope (needs eyes).
