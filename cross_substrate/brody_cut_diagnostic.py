#!/usr/bin/env python3
"""Isolate the `s < 10.0` confound in the repaired Brody axis, on real IBL cells.

I8_brody_q         : bounds (0,1),   s>0 AND s<10, n>=MIN_N_FIT(50)
I8_brody_q_unbounded: bounds (-1,4), s>0 only,     n>=MIN_N_NNS(20)

Three changes at once.  This refits the SAME spacings a third way -- bounds
opened but the s<10 cut RETAINED -- so the bound change can be separated from
the outlier-filter change.  Writes only to /tmp.
"""
import os
import sys
import json
import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool")
sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/cross_substrate")

import h5py                                                        # noqa: E402
from scipy.optimize import minimize_scalar                         # noqa: E402
from cross_substrate.axes import (canonical_spacings, brody_pdf,   # noqa: E402
                                  I8_brody_q, I8_brody_q_unbounded,
                                  MIN_N_FIT, MIN_N_NNS)
from cross_substrate.ibl_port import MIN_SPIKES, _decode           # noqa: E402


def brody_fit(s, lo, hi, cut, min_n):
    s = np.asarray(s, dtype=np.float64)
    s = s[(s > 0) & (s < 10.0)] if cut else s[s > 0]
    if s.size < min_n:
        return None, 0
    def nll(q):
        return -np.sum(np.log(np.maximum(brody_pdf(s, q), 1e-300)))
    return float(minimize_scalar(nll, bounds=(lo, hi), method="bounded",
                                 options={"xatol": 1e-4}).x), s.size


def main():
    import glob
    files = sorted(glob.glob(os.path.expandvars("$HOME/fmexplorer/ibl_cache/sub-*.nwb")))
    out = []
    for f in files:
        with h5py.File(f, "r") as h:
            u = h["units"]
            sti = u["spike_times_index"][:]; st_all = u["spike_times"]
            nU = len(sti)
            for i in range(nU):
                spk = st_all[(0 if i == 0 else int(sti[i - 1])):int(sti[i])]
                if spk.size < MIN_SPIKES:
                    continue
                s = canonical_spacings(spk)
                s = np.asarray(s, dtype=np.float64)
                n_all = int((s > 0).sum())
                n_cut = int(((s > 0) & (s < 10.0)).sum())
                q_dep = I8_brody_q(s)
                q_rep = I8_brody_q_unbounded(s)
                q_mid, _ = brody_fit(s, -1.0, 4.0, cut=True, min_n=MIN_N_NNS)
                sv = s[s > 0]
                out.append(dict(
                    file=os.path.basename(f), unit=i,
                    n_all=n_all, n_cut=n_cut,
                    n_outliers=n_all - n_cut,
                    max_s=float(sv.max()) if sv.size else None,
                    q_deployed=q_dep, q_repaired=q_rep, q_repaired_cut=q_mid))
        print(f"  done {os.path.basename(f)}  ({len(out)} cells so far)", flush=True)

    with open("/tmp/brody_cut_diagnostic.jsonl", "w") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")

    # ---- report ----------------------------------------------------------
    both = [r for r in out if r["q_repaired"] is not None and r["q_repaired_cut"] is not None]
    rep = np.array([r["q_repaired"] for r in both])
    cut = np.array([r["q_repaired_cut"] for r in both])
    d = cut - rep
    has_out = np.array([r["n_outliers"] > 0 for r in both])

    print(f"\ncells with both fits: {len(both)}")
    print(f"cells having >=1 spacing s>10 : {has_out.sum()} ({100*has_out.mean():.1f}%)")
    print(f"total outlier spacings        : {sum(r['n_outliers'] for r in both)}")
    print()
    print(f"median q  repaired (no cut) : {np.median(rep):+.4f}")
    print(f"median q  repaired (s<10)   : {np.median(cut):+.4f}")
    print(f"median shift from the cut   : {np.median(d):+.4f}")
    print(f"negative fraction  no cut   : {100*(rep<0).mean():.1f}%")
    print(f"negative fraction  s<10     : {100*(cut<0).mean():.1f}%")
    print()
    if has_out.any():
        print(f"  cells WITH outliers (n={has_out.sum()}): median shift {np.median(d[has_out]):+.4f}, "
              f"neg {100*(rep[has_out]<0).mean():.1f}% -> {100*(cut[has_out]<0).mean():.1f}%")
    if (~has_out).any():
        print(f"  cells W/O  outliers (n={(~has_out).sum()}): median shift {np.median(d[~has_out]):+.4f}, "
              f"neg {100*(rep[~has_out]<0).mean():.1f}% -> {100*(cut[~has_out]<0).mean():.1f}%")
    print()
    flip = int(((rep < 0) & (cut >= 0)).sum())
    print(f"cells NEGATIVE without the cut but NON-NEGATIVE with it: {flip} "
          f"({100*flip/len(both):.1f}%)  <-- the confounded population")


if __name__ == "__main__":
    main()
