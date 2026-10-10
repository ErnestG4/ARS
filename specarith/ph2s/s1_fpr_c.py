"""PH2S Stage 1 pre-read (Will, 2026-10-09): arm C's empirical false-positive rate with the unit-resampled SE
(s1preread.arm_width_units), over 500 random 8/8 splits of the 16 Stage 1 GUE sequences. The stand-in "zeros" are GUE
sequences shared across bins, so their side is resampled jointly (as their real dependence). Reported at k = 2 and 3 SE.
Also: the seen-R dry run of arm C with the same SE (zeros windows resampled within bins), and its power at the seen Δ.

  python s1_fpr_c.py [NSPLITS]  ->  results/preread/fpr_c.json
"""
import json
import math
import os
import sys

import numpy as np

import s1lib as S
import s1preread as SP

OUT = os.path.join(S.HERE, "results", "preread")


def main(nsplits=500):
    F1c = list(S.CORE)
    base = {n: SP.load_base(OUT, n) for n in F1c}
    rng = np.random.default_rng(20261013)
    rows = []
    for i in range(nsplits):
        perm = rng.permutation(16)
        a, b = set(perm[:8].tolist()), set(perm[8:].tolist())
        za = {n: [r for r in base[n] if r["seed"] in a] for n in F1c}
        bb = {n: [r for r in base[n] if r["seed"] in b] for n in F1c}
        res = SP.arm_width_units(za, bb, F1c, zeros_joint=True, nboot=1000, seed=i)
        rows.append((res["mean"], res["se"], sum(x > 0 for x in res["delta_u"])))
    m, se, npos = (np.array(c) for c in zip(*rows))
    fpr = {str(k): float(np.mean((npos >= 3) & (m > k * se))) for k in (2.0, 3.0)}
    Rn = list(S.R)
    seenZ = {n: json.load(open(os.path.join(OUT, f"seen_{n}.json"))) for n in Rn}
    baseR = {n: SP.load_base(OUT, n) for n in Rn}
    dry = SP.arm_width_units(seenZ, baseR, Rn, zeros_joint=False, nboot=2000, seed=99)
    out = dict(nsplits=nsplits, fpr_by_k=fpr, nominal_one_sided={"2.0": 0.0228, "3.0": 0.00135},
               null_mean_over_se_sd=float((m / se).std()), null_mean_over_se_mean=float((m / se).mean()),
               dryrun_seen_R=dry,
               power_at_seen={str(k): 0.5 * math.erfc(-((dry["mean"] - k * dry["se"]) / dry["se"]) / math.sqrt(2))
                              for k in (2.0, 3.0)})
    json.dump(out, open(os.path.join(OUT, "fpr_c.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
