"""Close-out §3.2 (round 79; post-hoc, descriptive): what the period-averaged class content is made of.

Per height and class k ≠ 0, fit the 15 shift-resolved values of n6b_lavg's task files as
(cubic envelope)·e^{2πifs} + (constant + linear), with f scanned on |f| ∈ [0.3, 3]; report f and the share of the
two-period triangular average (E.TRI) carried by the oscillating component and by the near-DC part. A 1.75-unit
window cannot separate true DC from |f| ≲ 0.3, so "near-DC" here is that whole band.

  python n6b_lavg_shiftfit.py DIR R    → DIR/SHIFTFIT_<R>.json
"""
import glob
import json
import os
import sys

import numpy as np

import n6b_extract as E


def main(d, r):
    s = np.array([t[0] for t in E.TRI])
    w = np.array([t[1] for t in E.TRI])
    ells = sorted({float(os.path.basename(p).split("_")[1]) for p in glob.glob(os.path.join(d, f"l_*_{r}_*.json"))})
    out = []
    for ell in ells:
        for k in ("1", "2", "3"):
            v = np.array([complex(*json.load(open(os.path.join(d, f"l_{ell:.7f}_{r}_{j:02d}.json")))["g"][k])
                          for j in range(len(E.TRI))])
            best = None
            for f in np.linspace(-3, 3, 6001):
                if abs(f) < 0.3:
                    continue
                e = np.exp(2j * np.pi * f * s)
                A = np.stack([e, s * e, s * s * e, s ** 3 * e, np.ones_like(s), s], 1)
                c = np.linalg.lstsq(A, v, rcond=None)[0]
                res = float(np.linalg.norm(A @ c - v))
                if best is None or res < best[0]:
                    best = (res, f, A[:, :4] @ c[:4], A[:, 4:] @ c[4:])
            res, f, osc, dc = best
            row = dict(ell=ell, k=int(k), f=float(f), resid=res, rms=float(np.sqrt(np.mean(np.abs(v) ** 2))),
                       tri=[complex(w @ v).real, complex(w @ v).imag], tri_osc=[complex(w @ osc).real, complex(w @ osc).imag],
                       tri_dc=[complex(w @ dc).real, complex(w @ dc).imag])
            out.append(row)
            print(f"ell {ell:.4f} k {k} f {f:+.3f} resid/rms {res / row['rms']:.3f}  TRI {complex(w @ v):.4f}  "
                  f"osc {complex(w @ osc):.4f}  dc {complex(w @ dc):.4f}")
    json.dump(dict(label="close-out §3.2 shift fit (post-hoc, descriptive)", r=r, rows=out),
              open(os.path.join(d, f"SHIFTFIT_{r}.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], float(sys.argv[2])))
