"""Descriptive (seen F1 + Stage 1 GUE; no verdict): lag-k autocorrelation of the tapered window sums S(c; b) stored by
ph2s2/tapered.py, and the change in the sample variance under a linear / quadratic detrend in the window centre.
Cited in GS_ZETA_RESULTS.md §5.

  python diag_f1_wincorr.py ../ph2s2/results/tapered
"""
import glob
import json
import sys

import numpy as np

d = sys.argv[1]
for f in sorted(glob.glob(d + "/zeros_*.json")) + sorted(glob.glob(d + "/gue_*s00[0-3].json")):
    r = json.load(open(f))
    name = r.get("bin", r["file"])
    out = []
    for b in ("100", "1000", "3000", "10000"):
        s = np.array(r["ladder"][b]["sums"])
        n = len(s)
        x = np.arange(n, dtype=float)
        dev = s - s.mean()
        v0 = dev @ dev / (n - 1)
        ac = [float(dev[:-k] @ dev[k:] / (dev @ dev)) for k in (1, 2, 3)]
        res = {}
        for p in (1, 2):
            X = np.vander(x, p + 1)
            beta, rss, *_ = np.linalg.lstsq(X, s, rcond=None)
            e = s - X @ beta
            res[p] = (e @ e) / (n - p - 1) / v0
        out.append("b=%s n=%d ac1..3 %+.2f %+.2f %+.2f  lin/const %.3f quad/const %.3f"
                   % (b, n, *ac, res[1], res[2]))
    print(name)
    print("   " + "\n   ".join(out))
