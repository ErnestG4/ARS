"""Validation of cs4lr.LongRangeZeta (Fourier/NUFFT evaluation on a uniform r-grid) against cs4fastc.FastZetaCached
(pointwise; itself checked against the 50-digit reference to ≤ 5.4e-10 for r ≤ 2·10⁴, SPARSE_CHECK_RECORD §4.2).
Height ℓ = 16.5 and 21.75, pmax 1e5 (both evaluators), in-pair offsets (0.5, 0.5) and (0.3, 0.8). Three grids:
  long:  r = 4 + 0.5k, 2048 points (r ≤ 1027.5), non-oscillating and oscillating parts;
  far:   r = 30000 + 0.5k, 512 points (beyond the sparse check's range: agreement of two algorithms only);
  short: r = 0.05 + 0.1k, 200 points (r < 20), the full connected function, away from coincidences (δ ≥ 0.02).
Tolerance (Stage 2 needs ~1e-3 relative on v(b); twenty-first round): max |Δ| ≤ 1e-8 absolute per grid.
Also reports the Fourier-tail (aliasing) diagnostic and the time per grid.

  python cs4lr_check.py OUT
"""
import json
import math
import os
import sys
import time

import numpy as np

import cs4fastc as FC
import cs4lr as LR

TOL = 1e-8


def near_coinc(d1, d2, r, dmin=0.02):
    pts = np.array([-d1 / 2, d1 / 2, r - d2 / 2, r + d2 / 2])
    D = np.abs(pts[:, None] - pts[None, :])[np.triu_indices(4, 1)]
    return D.min() < dmin


def main(out):
    rows = []
    for L in (16.5, 21.75):
        t = 2 * math.pi * math.exp(L)
        lr = LR.LongRangeZeta(t, pmax=100_000)
        ref = FC.FastZetaCached(t, pmax=100_000)
        for d1, d2 in ((0.5, 0.5), (0.3, 0.8)):
            for name, r0, dr, n, nonosc in (("long", 4.0, 0.5, 2048, False), ("far", 30000.0, 0.5, 512, True),
                                            ("short", 0.05, 0.1, 200, False)):
                r = r0 + dr * np.arange(n)
                t0 = time.time()
                o, nn = lr.connected(d1, d2, r, nonosc_only=nonosc)
                tl = time.time() - t0
                idx = np.unique(np.linspace(0, n - 1, 16).astype(int))
                if name == "short":
                    idx = np.array([i for i in idx if not near_coinc(d1, d2, r[i])])
                t0 = time.time()
                ro, rn = ref.connected(d1, d2, r[idx], nonosc_only=nonosc)
                tr = time.time() - t0
                if name == "short":
                    err = np.abs((o[idx] + nn[idx]) - (ro + rn))
                else:
                    err = np.abs(nn[idx] - rn) if nonosc else np.maximum(np.abs(nn[idx] - rn), np.abs(o[idx] - ro))
                tail = max(lr.diag.values()) if lr.diag else 0.0
                row = dict(L=L, d1=d1, d2=d2, grid=name, n=n, n_cmp=len(idx), max_err=float(err.max()),
                           max_abs_val=float(np.abs(rn).max()), fourier_tail=tail, t_lr=tl, t_ref_per_pt=tr / len(idx),
                           PASS=bool(err.max() <= TOL))
                rows.append(row)
                print(L, d1, d2, name, "max err %.2e (|val| ≤ %.1e)  tail %.1e  lr %.1fs for %d pts; ref %.2fs/pt"
                      % (row["max_err"], row["max_abs_val"], tail, tl, n, row["t_ref_per_pt"]), flush=True)
    ok = all(r["PASS"] for r in rows)
    os.makedirs(out, exist_ok=True)
    json.dump(dict(rows=rows, PASS=ok, tol=TOL), open(os.path.join(out, "cs4lr_check.json"), "w"), indent=1)
    print("cs4lr check", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main(sys.argv[1])
