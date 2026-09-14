# Overnight queue — started 2026-09-14 00:40

Authorized by Will: run an overnight, ping every 30 min until 08:00, keep
something going. Each item states its own ENTRY, WHAT, and EXIT so a tick can be
resolved by reading this file rather than the conversation.

**Standing rules for every item below**
- Sealed cells only: `./sealgen.sh <gen.py> "<msg>"`, output committed separately.
- Never read an arm the lattice marks UNREAD. (RECERT_CORRECTIONS item 9.)
- Cross-cell values are READ from artifacts, never typed. (5 instances; item 1.)
- Premise bars derive from the fit's own conditioning, never typed absolutes.
- `./checkrun.sh X > f 2>&1; RC=$?` — never `X | grep && commit`.
- A CHECKRUN line older than 3h is refused by the hook; re-run the board.
- Declare BOTH edges of any window, and the LINEAGE of any cell that will be
  cited alongside another.

---

## 1. RUNNING — Stage 3c, window surface at every n (`8816dd4`)
**Exit:** `stage3c_window_surface_alln.json` written, board green, committed.
Recovers 64 flows at n=1024/2048 and BANKS them. C2 written so the comfortable
outcome MISSES; C3 written so MET is the uncomfortable answer.

## 2. NEXT — fix the `rtilde` estimator collision (no compute)
**Entry:** none. **Why:** `track0_harness.rtilde` applies NO filter to gaps;
`knownanswer.rtilde_distance` filters `s = s[s > 0]`. Same quantity, two
estimators, and the difference appears exactly in the tail. Gate D can therefore
certify a configuration on which the real statistic would be corrupted. Noticed
2026-09-12, not fixed.
**What:** make the gate use the instrument's own definition, and add a
negative-gap DETECTOR (count and report, do not silently drop) to the harness
path. A silent filter is how the collision hid.
**Exit:** both paths provably agree on a configuration containing a negative
gap, board green, committed.

## 3. THEN — `Spacings` provenance type (Will's proposal, narrow version)
**Entry:** item 2 done. **Why:** "unfolded spacings" is the one place where the
derivation difference changes the NUMBER rather than the label; three of the
seven failed Gate D constructions were this collision. Full symbol tagging
across 90 files is too heavy; this targets the demonstrated failure.
**What:** a value + the unfolding estimator that produced it + the substrate;
comparisons between two `Spacings` refuse to construct unless the estimator tags
match. Construction-time enforcement, same shape as `railed.Bounded.__float__`.
**Exit:** module + checker on the board, red-pathed both directions (refuses a
cross-estimator comparison, permits a matching one).

## 4. THEN — lineage declaration + checker
**Entry:** item 3 done. **Why:** the mirror failure — two cells agreeing because
they share machinery, cited as independent confirmation. This arc did it: Stage
2a's P2 "continuity" check shares Stage 1's ENTIRE construction, and the two
readings disagree in SIGN yet pass. That is one route reported twice.
**What:** every cell declares `lineage` (what it shares, what is independent);
a checker refuses to let two cells with overlapping lineage be cited as
independent. Stage 3c already declares its lineage — use that as the template.
**Exit:** checker on the board, red-pathed against the Stage 1 / Stage 2a pair,
which it must flag.

## 5. LAST — paper §4 disclosure (text only, REVIEWABLE, do not push)
**Entry:** item 1 exits. **Why:** the paper discloses a covariance-treatment
range for z(beta) (9.31 / 8.24 / 5.84) and does not disclose that the WINDOW
moves the same number across two orders of magnitude, with the sealed window at
the 87th percentile of that range (3b; confirm at every n from 3c).
**What:** promote the k* SEPARATION over the sigma — it is robust at 6% where
the sigma swings 95x — and add the window sensitivity as a stated limitation.
Do NOT weaken RATE-SEED-DEPENDENT: it survives every window tested.
**Exit:** `paper.tex` edited, `verify_paper_numbers` green, compiled, committed.
Flag clearly for Will rather than treating as settled.

---

## If everything above is done
Re-run the board, push nothing, and write a morning summary at
`derivflow/MORNING_2026_09_14.md` stating: what ran, what each verdict was,
which arms were UNREAD, and what is left. Do not start a new arc unprompted.
