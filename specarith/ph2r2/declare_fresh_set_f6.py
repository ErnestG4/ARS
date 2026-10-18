"""Declare and md5-pin the fresh set F6 for the corrected (B) (round 58), before any prediction. Nothing is downloaded or
decoded.

Rule: check_fresh_set_f6.py's (declare_fresh_sets.py's v2 gap rule at F3's targets; touched = the 13 files seen by
2026-10-09, Phase 2's Odlyzko bins, every F1–F5 pick). Its three picks (L ≈ 17.5, 19.75, 21.25) plus EXTRA_F6 =
zeros_46646000.dat (L ≈ 15.84), the gap-feasible file nearest the infeasible low targets.

Round 58 (Will): F6 is these four files. Reason: the low heights carry the largest corrections, the test stands alone,
and the set is comparable to F5. Decided before any prediction.

Asserted: all four are distinct from F3, F4 and F5; each pick's extended range (previous file's start to next file's end)
overlaps no touched range and no other pick.

  python declare_fresh_set_f6.py  ->  FRESH_SET_F6.md
"""
import hashlib
import math
import os
import re

import check_fresh_set_f6 as C
import declare_fresh_sets as D

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA_F6 = "zeros_46646000.dat"


def main():
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
    touched = [rng[g] for g in C.SEEN] + [(tofL(a), tofL(b)) for a, b in D.SEEN_L]
    blocked = list(touched)
    picks, infeasible = [], []
    for L in C.TARGETS:
        cand = [f for f in names if rng[f][0] >= 14 and rng[f][1] < 1e12 and not any(overl(ext(f), b) for b in blocked)]
        f = min(cand, key=lambda f: abs(mid(f) - L))
        if abs(mid(f) - L) > 0.3:
            infeasible.append((L, f, mid(f)))
            continue
        picks.append((L, f))
        blocked.append(rng[f])
    assert {f for _, f, _ in infeasible} == {EXTRA_F6}, infeasible
    picks.append((round(mid(EXTRA_F6), 2), EXTRA_F6))
    prior = set(C.F1_F3) | set(C.F4_F5)
    F3_F5 = set(C.F1_F3[-5:]) | set(C.F4_F5)
    checks = {}
    for L, f in picks:
        others = touched + [rng[g] for _, g in picks if g != f]
        checks[f] = dict(distinct_from_F1_F5=f not in prior, gap_ok=not any(overl(ext(f), b) for b in others))
        assert checks[f]["distinct_from_F1_F5"] and checks[f]["gap_ok"], (f, checks[f])
    assert len({f for _, f in picks}) == 4
    assert not ({f for _, f in picks} & F3_F5)
    out = ["# Fresh set F6 — declared and md5-pinned BEFORE any prediction or download (round 58, 2026-10-18)", "",
           "Generator: `declare_fresh_set_f6.py` (rule in its docstring; `check_fresh_set_f6.py`'s gap rule plus the "
           f"round-58 extra file). Index `ph2/data/platt_md5.txt` sha256 "
           f"{hashlib.sha256(open(D.INDEX, 'rb').read()).hexdigest()}.", "",
           f"**Round 58 (Will): F6 is four files** — the three gap-feasible files at L ≈ 17.5, 19.75 and 21.25 plus "
           f"{EXTRA_F6} (L-midpoint {mid(EXTRA_F6):.3f}). Reason: the low heights carry the largest corrections, the test "
           "stands alone, and the set is comparable to F5. Decided before any prediction.", "",
           "**Checked (asserted):** all four are distinct from every F1–F5 file (so from F3, F4 and F5); each one's "
           "extended range (previous file's start to next file's end) overlaps no touched range (the 13 files seen by "
           "2026-10-09, Phase 2's Odlyzko bins A and B, F1–F5) and no other F6 file. Infeasible targets (not "
           "substituted): " + "; ".join(f"L = {L} (nearest feasible {f}, {m:.3f})" for L, f, m in infeasible) + ".", "",
           "## F6 — corrected (B): offset-averaged third cumulant of the count", "",
           "| target L | file | height range [t0, t1) | L range | md5 (pinned) |", "|---|---|---|---|---|"]
    for L, f in sorted(picks):
        t0, t1 = rng[f]
        out.append(f"| {L:.2f} | {f} | [{t0:,}, {t1:,}) | {Lof(t0):.4f}–{Lof(t1):.4f} | {md5[f]} |")
    out += ["", "None is to be downloaded before the corrected (B)'s seal receipt is Bitcoin-attested and verified, nor "
            "decoded before its seal. Download by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into "
            "`specarith/ph2r2/data/platt_fresh/`, verified against this table before any use.", ""]
    open(os.path.join(HERE, "FRESH_SET_F6.md"), "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
