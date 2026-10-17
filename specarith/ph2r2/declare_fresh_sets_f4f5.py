"""Declare and md5-pin two more disjoint fresh Platt sets (round 50, cs4/FOLLOWUP_REPLICATION_RULES.md §5): F4 = route (a)
follow-up (A), the next-nearest-neighbour law; F5 = follow-up (B), the third cumulant of the count. Nothing here is
downloaded or decoded.

Rule: declare_fresh_sets.py's v2 rule unchanged (the gap-feasible file whose L-midpoint is nearest the target, within
0.3; else INFEASIBLE, reported and not substituted; a >= 1-file gap from every touched range and between picks), at F3's
targets, so both replications have route (a)'s geometry. Touched = the 13 files seen by 2026-10-09, Phase 2's Odlyzko
bins A and B, and every F1–F3 pick. On 2026-10-16 every zeros_*.dat on the desktop, spot and char is one of those
(listed by find on all three; the remaining copies under cs4/results/dryrun_synth are synthetic dry-run inputs named
after F3). Picks are made in order F4, F5.

Round 51 (Will): the gap rule stays; F4 keeps its three files. F5 also gets the L ≈ 15.59 file, the one gap-feasible
file nearest the infeasible low targets (EXTRA_F5, asserted to be that file and gap-separated from everything). The
asymmetry is deliberate: the weaker observable, (B), gets the extra low-height file. It was decided before any F4/F5
prediction, calibration or download.

  python declare_fresh_sets_f4f5.py  ->  FRESH_SETS_F4_F5.md
"""
import hashlib
import math
import os
import re

import declare_fresh_sets as D

HERE = os.path.dirname(os.path.abspath(__file__))
F1_F3 = re.findall(r"\| (zeros_\d+\.dat) \|", open(os.path.join(HERE, "FRESH_SETS_F1_F3.md")).read())
SEEN = D.SEEN + F1_F3
TARGETS = {"F4": [14.75, 15.25, 17.5, 19.75, 21.25], "F5": [14.75, 15.25, 17.5, 19.75, 21.25]}
ORDER = ("F4", "F5")
EXTRA_F5 = "zeros_36146000.dat"            # round 51
PURPOSE = {"F4": "route (a) follow-up (A): next-nearest-neighbour spacing law",
           "F5": "route (a) follow-up (B): third cumulant of the count"}


def main():
    assert len(F1_F3) == 16 and not set(F1_F3) & set(D.SEEN), F1_F3
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
    picks, infeasible = [], []
    for S in ORDER:
        for L in TARGETS[S]:
            cand = [f for f in names if rng[f][0] >= 14 and not any(overl(ext(f), b) for b in blocked)]
            f = min(cand, key=lambda f: abs(mid(f) - L))
            if abs(mid(f) - L) > 0.3:
                infeasible.append((S, L, f, mid(f)))
                continue
            picks.append((S, L, f))
            blocked.append(rng[f])
    near = {f for S, L, f, m in infeasible}
    assert near == {EXTRA_F5}, near
    picks.append(("F5", round(mid(EXTRA_F5), 2), EXTRA_F5))
    for S, L, f in picks:
        others = touched + [rng[f2] for _, _, f2 in picks if f2 != f]
        assert not any(overl(ext(f), b) for b in others), f
    assert len({f for _, _, f in picks}) == len(picks)
    out = ["# Fresh Platt sets F4–F5 — declared and md5-pinned BEFORE download (round 50, 2026-10-16)", "",
           "Generator: `declare_fresh_sets_f4f5.py` (rule and touched set in its docstring; declare_fresh_sets.py's v2 "
           "rule at F3's targets). Index: "
           f"`ph2/data/platt_md5.txt` sha256 {hashlib.sha256(open(D.INDEX, 'rb').read()).hexdigest()}. Every pick is "
           "separated by >= 1 file from the 13 files seen by 2026-10-09, Phase 2's Odlyzko bins A and B, every F1–F3 "
           "pick and every other pick (asserted). None is to be downloaded before its observable's seal is "
           "Bitcoin-attested and verified (round 49 protocol), nor decoded before its seal.", ""]
    if infeasible:
        out += ["**Infeasible targets (no gap-feasible file within 0.3 in L; not substituted):** " + "; ".join(
            f"{S} L = {L} (nearest feasible: {f}, L-midpoint {m:.3f})" for S, L, f, m in infeasible) + ".", ""]
    out += [f"**Round 51 (Will): asymmetric by decision.** F4 keeps its three files. F5 also gets {EXTRA_F5} "
            f"(L-midpoint {mid(EXTRA_F5):.3f}), the gap-feasible file nearest the infeasible low targets. The weaker "
            "observable, (B), gets the extra low-height file. This was decided before any F4/F5 prediction, calibration or "
            "download. Its row's target L is its own L-midpoint.", ""]
    for S in ORDER:
        out += [f"## {S} — {PURPOSE[S]}", "",
                "| target L | file | height range [t0, t1) | L range | md5 (pinned) |", "|---|---|---|---|---|"]
        for S2, L, f in sorted(p for p in picks if p[0] == S):
            t0, t1 = rng[f]
            assert t1 < 1e12
            out.append(f"| {L:.2f} | {f} | [{t0:,}, {t1:,}) | {Lof(t0):.4f}–{Lof(t1):.4f} | {md5[f]} |")
        out.append("")
    out += ["Touched (excluded) files: " + ", ".join(SEEN) + ".", "",
            "Download: by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into "
            "`specarith/ph2r2/data/platt_fresh/`, verified against this table before any use.", ""]
    open(os.path.join(HERE, "FRESH_SETS_F4_F5.md"), "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
