"""PH6_SEAL 6.1 §2 convergence check: a candidate's levels at two resolutions must agree to ≤ 10⁻³ local mean spacings
(max over the read window), else NOT RESOLVABLE (not converged). The local mean spacing at level n is the mean of the
100 nearest spacings of the resolution-1 list. Reads only the two level lists (no T1–T4 statistic).

  python convergence61.py DIR ID [ID ...]      (files DIR/<ID>_res1.npy, DIR/<ID>_res2.npy) -> DIR/convergence61.json
"""
import json
import os
import sys

import numpy as np

TOL = 1e-3


def check(d, ident):
    a = np.sort(np.load(os.path.join(d, f"{ident}_res1.npy")))
    b = np.sort(np.load(os.path.join(d, f"{ident}_res2.npy")))
    a, b = a[a > 0], b[b > 0]
    out = dict(id=ident, n_res1=int(len(a)), n_res2=int(len(b)))
    n = min(len(a), len(b))
    s = np.diff(a)
    k = 100
    cs = np.concatenate([[0.0], np.cumsum(s)])
    idx = np.clip(np.arange(n) - k // 2, 0, len(s) - k)
    local = (cs[idx + k] - cs[idx]) / k
    dev = np.abs(a[:n] - b[:n]) / local[:n]
    out.update(max_dev_in_spacings=float(dev.max()), at_level=int(dev.argmax()), median_dev=float(np.median(dev)),
               counts_equal=bool(len(a) == len(b)), converged=bool(len(a) == len(b) and dev.max() <= TOL))
    return out


if __name__ == "__main__":
    d = sys.argv[1]
    path = os.path.join(d, "convergence61.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    for ident in sys.argv[2:]:
        res[ident] = check(d, ident)
        print(json.dumps(res[ident]), flush=True)
    json.dump(res, open(path, "w"), indent=1)
