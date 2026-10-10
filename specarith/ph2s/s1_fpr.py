"""PH2S Stage 1 pre-read: empirical false-positive rates of arms A, C and D under GUE vs GUE, over many random 8/8 splits
of the 16 Stage 1 GUE sequences (stored per-seed growths; no new computation). The single 0–7 vs 8–15 split in
s1preread.analyse is one draw. The same 16 sequences are mapped onto every F1 height, so baseline errors are correlated
across bins, which the per-bin SEs (and arm D's WLS slope SE) treat as independent. This measures what that does to
each arm's specificity.

  python s1_fpr.py [NSPLITS]  ->  results/preread/fpr.json
"""
import json
import os
import sys

import numpy as np

import s1lib as S
import s1preread as SP

OUT = os.path.join(S.HERE, "results", "preread")


def main(nsplits=500):
    pre = json.load(open(os.path.join(OUT, "preread.json")))
    F1n = list(S.F1)
    base = {n: {r["seed"]: r for r in SP.load_base(OUT, n)} for n in F1n}
    rng = np.random.default_rng(20261012)
    counts = dict(A_pass=0, C_pass=0, D_pass=0, bins_shrink=0, bins_total=0)
    slopes = []
    for _ in range(nsplits):
        perm = rng.permutation(16)
        a, b = set(perm[:8].tolist()), set(perm[8:].tolist())
        val = lambda n, seeds: {L: {k: [base[n][s][str(L)][k] for s in seeds if k in base[n][s][str(L)]]
                                    for k in SP.MEM_IDX} for L in (S.L_PRIMARY, S.L_SECONDARY)}
        res = SP.evaluate(list(S.CORE), {n: val(n, a) for n in F1n}, {n: val(n, b) for n in F1n},
                          pre["d_ref"], pre["resolvable"], F1n)
        counts["A_pass"] += res["A"]["verdict"] == "PASS"
        counts["C_pass"] += res["C"]["verdict"] == "PASS"
        counts["D_pass"] += res["D"]["verdict"] == "PASS"
        counts["bins_shrink"] += sum(res["A"]["bins"][n]["SHRINK"] for n in S.CORE)
        counts["bins_total"] += len(S.CORE)
        slopes.append(res["D"]["slope"] / res["D"]["se"])
    z = np.array(slopes)
    out = dict(nsplits=nsplits, fpr_A=counts["A_pass"] / nsplits, fpr_C=counts["C_pass"] / nsplits,
               fpr_D=counts["D_pass"] / nsplits, fpr_bin_shrink=counts["bins_shrink"] / counts["bins_total"],
               D_slope_over_se_sd=float(z.std()), D_slope_over_se_mean=float(z.mean()),
               D_nominal_one_sided=0.0228)
    json.dump(out, open(os.path.join(OUT, "fpr.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
