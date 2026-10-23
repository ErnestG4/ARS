"""Fresh set F7 for an n = 6 corrected-(B) block-variance test (round 74 (d)): the selection rule, committed BEFORE it is
run. Nothing is downloaded, decoded or pinned here. Round 74: nothing beyond stage (a) runs until stage (b)'s gate
result and stage (c)'s bound are back with Will, so this file is committed and NOT run until then.

Rule (declared now):
- declare_fresh_sets.py's v2 gap rule, unchanged: at each target L, the gap-feasible file whose L-midpoint is nearest the
  target, within 0.3; otherwise the target is INFEASIBLE and is not substituted. Gap-feasible means a >= 1-file gap
  (the file's extended range, previous file's start to next file's end) from every touched range and from every
  earlier pick.
- Targets: 8, evenly spaced in L across [15.75, 21.75] (step 6/7), processed in ascending order, each pick blocking
  its neighbours for the next.
- Touched: the 13 files seen by 2026-10-09, Phase 2's Odlyzko bins A and B, every F1–F3 pick (F1 Stage 1, F2 Stage 2,
  F3 route (a)), every F4/F5 pick and the four F6 files.
- Size: the set is the feasible picks if there are 5–8 of them. Fewer than 5 is reported to Will, with the gap-feasible
  files within 1.0 in L of each target, and no file is added by this rule.

  python check_fresh_set_f7.py  ->  FRESH_SET_F7_FEASIBILITY.md
"""
import hashlib
import math
import os
import re

import declare_fresh_sets as D

HERE = os.path.dirname(os.path.abspath(__file__))
F1_F3 = re.findall(r"\| (zeros_\d+\.dat) \|", open(os.path.join(HERE, "FRESH_SETS_F1_F3.md")).read())
F4_F5 = re.findall(r"\| (zeros_\d+\.dat) \|", open(os.path.join(HERE, "FRESH_SETS_F4_F5.md")).read())
F6 = re.findall(r"\| (zeros_\d+\.dat) \|", open(os.path.join(HERE, "FRESH_SET_F6.md")).read())
SEEN = D.SEEN + F1_F3 + F4_F5 + F6
TARGETS = [round(15.75 + k * 6 / 7, 4) for k in range(8)]
MIN_FILES, MAX_FILES = 5, 8


def main():
    assert len(F1_F3) == 16 and len(F4_F5) == 7 and len(F6) == 4, (len(F1_F3), len(F4_F5), len(F6))
    md5 = {}
    for line in open(D.INDEX):
        h, f = line.split()
        md5[f.lstrip("*")] = h
    starts = sorted((int(re.match(r"zeros_(\d+)\.dat", f).group(1)), f) for f in md5)
    rng = {f: (s, starts[i + 1][0] if i + 1 < len(starts) else math.inf) for i, (s, f) in enumerate(starts)}
    Lof = lambda t: math.log(t / (2 * math.pi))                                          # noqa: E731
    tofL = lambda L: 2 * math.pi * math.exp(L)                                           # noqa: E731
    names = [f for _, f in starts]
    pos = {f: i for i, f in enumerate(names)}
    ext = lambda f: (rng[names[max(pos[f] - 1, 0)]][0], rng[names[min(pos[f] + 1, len(names) - 1)]][1])  # noqa: E731
    overl = lambda a, b: a[0] < b[1] and b[0] < a[1]                                      # noqa: E731
    mid = lambda f: 0.5 * (Lof(rng[f][0]) + Lof(min(rng[f][1], 1e12)))                   # noqa: E731
    touched = [rng[g] for g in SEEN] + [(tofL(a), tofL(b)) for a, b in D.SEEN_L]
    blocked = list(touched)
    picks, infeasible, near = [], [], {}
    for L in TARGETS:
        cand = [f for f in names if rng[f][0] >= 14 and rng[f][1] < 1e12 and not any(overl(ext(f), b) for b in blocked)]
        near[L] = sorted((f for f in cand if abs(mid(f) - L) <= 1.0), key=lambda f: abs(mid(f) - L))
        f = min(cand, key=lambda f: abs(mid(f) - L))
        if abs(mid(f) - L) > 0.3:
            infeasible.append((L, f, mid(f)))
            continue
        picks.append((L, f))
        blocked.append(rng[f])
    out = ["# Fresh set F7 — selection under the gap rule (round 74 (d); nothing downloaded, nothing pinned)", "",
           "Generator: `check_fresh_set_f7.py` (rule and touched set in its docstring). Index `ph2/data/platt_md5.txt` "
           f"sha256 {hashlib.sha256(open(D.INDEX, 'rb').read()).hexdigest()}. Touched: {len(SEEN)} files "
           "(13 seen by 2026-10-09, F1–F3, F4–F5, F6) and Phase 2's Odlyzko bins.", ""]
    out += ["## Gap-rule picks at the eight F7 targets (in order; each pick blocks its neighbours for the next)", "",
            "| target L | file | height range [t0, t1) | L-midpoint | md5 (index) |", "|---|---|---|---|---|"]
    for L, f in picks:
        t0, t1 = rng[f]
        out.append(f"| {L:.2f} | {f} | [{t0:,}, {t1:,}) | {mid(f):.3f} | {md5[f]} |")
    out += ["", "**Infeasible targets (no gap-feasible file within 0.3 in L):** "
            + ("; ".join(f"L = {L} (nearest feasible: {f}, L-midpoint {m:.3f})" for L, f, m in infeasible)
               if infeasible else "none") + ".", ""]
    out += ["## Gap-feasible files within 1.0 in L of each target (before picks block neighbours; for review)", ""]
    for L in TARGETS:
        out.append(f"- **L = {L}:** " + (", ".join(f"{f} ({mid(f):.3f})" for f in near[L][:8]) or "none"))
    n = len(picks)
    out += ["", f"**Size:** {n} feasible picks; " + ("within 5–8: this is the F7 set, for Will's review before pinning."
            if MIN_FILES <= n <= MAX_FILES else "fewer than 5: reported to Will; nothing added by this rule."), "",
            "Pinning (FRESH_SET_F7.md) follows Will's review, before any prediction is built.", ""]
    open(os.path.join(HERE, "FRESH_SET_F7_FEASIBILITY.md"), "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
