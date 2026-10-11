"""Declare and md5-pin three disjoint fresh Platt sets (Will, 2026-10-09): F1 = shrink direction (Stage 1), F2 = the
quantitative few-prime model (Stage 2), F3 = route (a). Quarter/half-integer L = log(E/2π) interleaved between all seen
heights; nothing here is downloaded or decoded.

Grid: L = k + {0.25, 0.5, 0.75} for k ∈ {14, 15, 17, 19, 21}, the three offsets rotated across F1/F2/F3 from one k to
the next, so every set spans L ≈ 14.25–21.75 with five bins. Selection rule (as PH2_SEAL_2.1 §3 and R₂): the file whose
start height is the largest ≤ E = 2π·e^L, from the pinned LMFDB index (ph2/data/platt_md5.txt, 14,580 entries). A
file's range is [its start, the next file's start). Refuses unless every pick is disjoint from every seen file's range
and from every other pick.

v2 (Will, sixteenth round, before any download): (1) a >= 1-file gap is required between every pick and every touched
height range (the 13 seen Platt files and Phase 2's Odlyzko bins A: L 9.4-10.5 and B: L 11.0-12.1), and between picks:
a pick's extended range [previous file's start, next file's end) must not overlap any of them; (2) F1 gains two bins
at the height extremes for arm D (Will: L ~ 13.25 and ~ 22.1). Selection becomes: the gap-feasible file whose
L-midpoint is nearest the target, within 0.3; else INFEASIBLE (reported, not substituted). Picks are made in order
F1, F3, F2 (Stage 1 first; F3 keeps its low bin; F2 is the latest-used set). Targets changed from v1: F2 14.5 -> 16.5
(after F1's re-pin, the gap rule leaves one file below P2, F3's 14.75).

  python declare_fresh_sets.py  ->  FRESH_SETS_F1_F3.md
"""
import hashlib
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "..", "ph2", "data", "platt_md5.txt")
# every Platt file read, downloaded or referenced anywhere in the repo or on disk (local + spot), 2026-10-09
SEEN = ["zeros_14.dat", "zeros_2546000.dat", "zeros_19346000.dat", "zeros_151646000.dat", "zeros_1119746000.dat",
        "zeros_8284946000.dat", "zeros_30404246000.dat", "zeros_30607946000.dat",
        "zeros_6746000.dat", "zeros_55046000.dat", "zeros_412046000.dat", "zeros_3047546000.dat",
        "zeros_22522946000.dat"]
SEEN_L = [(9.4, 10.5), (11.0, 12.1)]          # Phase 2 bins A and B (Odlyzko zeros6), as L = log(t/2π) ranges
TARGETS = {"F1": [14.25, 15.5, 17.75, 19.25, 21.5, 13.25, 22.1],      # last two: extremes for arm D (Will, v2)
           "F3": [14.75, 15.25, 17.5, 19.75, 21.25],
           "F2": [16.5, 15.75, 17.25, 19.5, 21.75]}
SETS = ("F1", "F2", "F3")
ORDER = ("F1", "F3", "F2")
PURPOSE = {"F1": "shrink direction (Stage 1)", "F2": "quantitative few-prime model (Stage 2)", "F3": "route (a)"}


def main():
    md5 = {}
    for line in open(INDEX):
        h, f = line.split()
        md5[f.lstrip("*")] = h
    starts = sorted((int(re.match(r"zeros_(\d+)\.dat", f).group(1)), f) for f in md5)
    rng = {f: (s, starts[i + 1][0] if i + 1 < len(starts) else math.inf) for i, (s, f) in enumerate(starts)}
    Lof = lambda t: math.log(t / (2 * math.pi))
    tofL = lambda L: 2 * math.pi * math.exp(L)
    names = [f for _, f in starts]
    pos = {f: i for i, f in enumerate(names)}
    ext = lambda f: (rng[names[max(pos[f] - 1, 0)]][0], rng[names[min(pos[f] + 1, len(names) - 1)]][1])
    overl = lambda a, b: a[0] < b[1] and b[0] < a[1]
    blocked = [rng[g] for g in SEEN] + [(tofL(a), tofL(b)) for a, b in SEEN_L]
    picks, infeasible = [], []
    for S in ORDER:
        for L in TARGETS[S]:
            cand = [f for f in names if rng[f][0] >= 14 and not any(overl(ext(f), b) for b in blocked)]
            mid = lambda f: 0.5 * (Lof(rng[f][0]) + Lof(min(rng[f][1], 1e12)))
            f = min(cand, key=lambda f: abs(mid(f) - L))
            if abs(mid(f) - L) > 0.3:
                infeasible.append((S, L, f, mid(f)))
                continue
            picks.append((S, L, f))
            blocked.append(rng[f])
    for S, L, f in picks:                      # re-check every pick against everything else (seen + other picks)
        others = [rng[g] for g in SEEN] + [(tofL(a), tofL(b)) for a, b in SEEN_L] + \
                 [rng[f2] for _, _, f2 in picks if f2 != f]
        assert not any(overl(ext(f), b) for b in others), f
    assert len({f for _, _, f in picks}) == len(picks)
    out = ["# Fresh Platt sets F1–F3 — declared and md5-pinned BEFORE download (Will, 2026-10-09)", "",
           "Generator: `declare_fresh_sets.py` (selection rule, grid and checks in its docstring). Index: "
           f"`ph2/data/platt_md5.txt` sha256 {hashlib.sha256(open(INDEX, 'rb').read()).hexdigest()}. Every pick is "
           "separated by >= 1 file from all 13 seen Platt files, from Phase 2's Odlyzko bins A and B, and from every "
           "other pick (asserted; v2 rule). None is to be decoded before its stage's seal.", ""]
    if infeasible:
        out += ["**Infeasible targets (no gap-feasible file within 0.3 in L; not substituted):** " + "; ".join(
            f"{S} L = {L} (nearest feasible: {f}, L-midpoint {m:.3f})" for S, L, f, m in infeasible) + ".", ""]
    for S in SETS:
        out += [f"## {S} — {PURPOSE[S]}", "",
                "| target L | file | height range [t0, t1) | L range | md5 (pinned) |", "|---|---|---|---|---|"]
        for S2, L, f in sorted(p for p in picks if p[0] == S):
            t0, t1 = rng[f]
            assert t1 < 1e12
            out.append(f"| {L:.2f} | {f} | [{t0:,}, {t1:,}) | {Lof(t0):.4f}–{Lof(t1):.4f} | {md5[f]} |")
        out.append("")
    out += ["Seen (excluded) files and their L ranges: " + "; ".join(
        f"{g} {Lof(max(rng[g][0], 14)):.3f}–{Lof(rng[g][1]):.3f}" for g in SEEN) + ".", "",
        "Download: by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into "
        "`specarith/ph2r2/data/platt_fresh/` (F1–F3 together or per stage), verified against this table before any use.", ""]
    open(os.path.join(HERE, "FRESH_SETS_F1_F3.md"), "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
