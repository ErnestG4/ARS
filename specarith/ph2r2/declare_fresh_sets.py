"""Declare and md5-pin three disjoint fresh Platt sets (Will, 2026-10-09): F1 = shrink direction (Stage 1), F2 = the
quantitative few-prime model (Stage 2), F3 = route (a). Quarter/half-integer L = log(E/2π) interleaved between all seen
heights; nothing here is downloaded or decoded.

Grid: L = k + {0.25, 0.5, 0.75} for k ∈ {14, 15, 17, 19, 21}, the three offsets rotated across F1/F2/F3 from one k to
the next, so every set spans L ≈ 14.25–21.75 with five bins. Selection rule (as PH2_SEAL_2.1 §3 and R₂): the file whose
start height is the largest ≤ E = 2π·e^L, from the pinned LMFDB index (ph2/data/platt_md5.txt, 14,580 entries). A
file's range is [its start, the next file's start). Refuses unless every pick is disjoint from every seen file's range
and from every other pick.

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
KS = (14, 15, 17, 19, 21)
OFFS = (0.25, 0.5, 0.75)
SETS = ("F1", "F2", "F3")
PURPOSE = {"F1": "shrink direction (Stage 1)", "F2": "quantitative few-prime model (Stage 2)", "F3": "route (a)"}


def main():
    md5 = {}
    for line in open(INDEX):
        h, f = line.split()
        md5[f.lstrip("*")] = h
    starts = sorted((int(re.match(r"zeros_(\d+)\.dat", f).group(1)), f) for f in md5)
    rng = {f: (s, starts[i + 1][0] if i + 1 < len(starts) else math.inf) for i, (s, f) in enumerate(starts)}
    Lof = lambda t: math.log(t / (2 * math.pi))
    picks = []
    for j, k in enumerate(KS):
        for i, off in enumerate(OFFS):
            S = SETS[(i - j) % 3]
            L = k + off
            E = 2 * math.pi * math.exp(L)
            s, f = max((s, f) for s, f in starts if s <= E)
            picks.append((S, L, f))
    overl = lambda a, b: a[0] < b[1] and b[0] < a[1]
    for S, L, f in picks:
        for g in SEEN:
            assert not overl(rng[f], rng[g]), (f, "overlaps seen", g)
        for S2, L2, f2 in picks:
            assert f2 == f or not overl(rng[f], rng[f2]), (f, f2)
    assert len({f for _, _, f in picks}) == len(picks)
    out = ["# Fresh Platt sets F1–F3 — declared and md5-pinned BEFORE download (Will, 2026-10-09)", "",
           "Generator: `declare_fresh_sets.py` (selection rule, grid and checks in its docstring). Index: "
           f"`ph2/data/platt_md5.txt` sha256 {hashlib.sha256(open(INDEX, 'rb').read()).hexdigest()}. Every pick is "
           "disjoint from all 13 seen Platt files' height ranges and from every other pick (asserted). None is to be "
           "decoded before its stage's seal.", ""]
    for S in SETS:
        out += [f"## {S} — {PURPOSE[S]}", "",
                "| target L | file | height range [t0, t1) | L range | md5 (pinned) |", "|---|---|---|---|---|"]
        for S2, L, f in sorted(p for p in picks if p[0] == S):
            t0, t1 = rng[f]
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
