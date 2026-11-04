# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 archive cost rule (TOOLKIT §9.H; FN1H2_SEAL.md §8). Reads only the archive logs (CPU seconds per segment);
no archive data.

  python fn1h2_costs.py ROOT wave1|check

Model per task: the §9.H first wave's measured CPU (user + sys) at k = 1 / 100 / 199 for the six case fields,
interpolated linearly in k per field, flat beyond. A field outside the wave takes the case of its Cornacchia type
(D ≡ 1 mod 4: −15, −115, −427; D ≡ 0 mod 4: −20, −52, −232) nearest in log|D|.
- wave1: prints the wave's total against the price (61.2 s per segment, seal §8) and the projected bulk total
  (3,600 segments under the interpolated model) against the price; last line OK if the projection ≤ 1.25 × the price.
- check: sum measured / sum model over completed non-wave tasks; last line OK if ≤ 1.25, else EXCEEDS. Tasks above
  2× their model are listed (reported, not a stop rule).
Exit status 0 for OK, 1 otherwise.
"""
import glob, math, os, sys

import numpy as np

FIELDS = [-15, -20, -24, -35, -40, -51, -52, -88, -91, -115, -123, -148, -187, -232, -235, -267, -403, -427]
CASES = {1: [-15, -115, -427], 0: [-20, -52, -232]}
KS = (1, 100, 199)
PRICE = 61.2
NSEG = 200


def measured(root):
    m = {}
    for f in glob.glob(os.path.join(root, "logs", "cpu_D*.log")):
        D = -int(os.path.basename(f)[5:-4])
        for l in open(f):
            w = l.split()
            if len(w) == 4:
                m[(D, int(w[0]))] = float(w[1]) + float(w[2])
    return m


def case_of(D):
    t = 0 if (-D) % 4 == 0 else 1
    return min(CASES[t], key=lambda c: abs(math.log(-c) - math.log(-D)))


def model(m):
    out = {}
    for D in FIELDS:
        c = case_of(D)
        ys = [m[(c, k)] for k in KS]
        for k in range(NSEG):
            out[(D, k)] = float(np.interp(k, KS, ys))
    return out


def main(root, mode):
    m = measured(root)
    miss = [(c, k) for t in CASES.values() for c in t for k in KS if (c, k) not in m]
    if miss:
        print("first-wave points missing:", miss); print("EXCEEDS"); return 1
    mod = model(m)
    if mode == "wave1":
        w = sum(m[(c, k)] for t in CASES.values() for c in t for k in KS)
        proj = sum(mod.values())
        print(f"wave1 CPU {w:.0f} s over 18 tasks = {w / 18:.1f} s/task; price {PRICE} s ({w / 18 / PRICE:.3f}x)")
        print(f"projected bulk {proj / 3600:.1f} core-h for 3,600 segments; price {PRICE * 3600 / 3600:.1f} core-h "
              f"({proj / (PRICE * 3600):.3f}x)")
        ok = proj <= 1.25 * PRICE * 3600
    else:
        wave = {(c, k) for t in CASES.values() for c in t for k in KS}
        done = [key for key in m if key not in wave]
        sm, so = sum(m[k] for k in done), sum(mod[k] for k in done)
        big = [(k, round(m[k] / mod[k], 2)) for k in done if m[k] > 2 * mod[k]]
        print(f"completed {len(done)} tasks: measured {sm:.0f} s, model {so:.0f} s, ratio {sm / max(so, 1):.3f}; "
              f"against the price {sm / max(len(done), 1) / PRICE:.3f}x; above 2x: {big[:20]}")
        ok = sm <= 1.25 * so
    print("OK" if ok else "EXCEEDS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
