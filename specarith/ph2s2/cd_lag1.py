"""Open lead L5 (twenty-fourth round): Coram–Diaconis's lag-1 serial correlation of the trace statistic, on GUE and on
F1 (seen data); descriptive.

CD (2000 report §1–3): consecutive blocks of n spacings, each wrapped onto the circle by its own cumulative spacings,
θ_j = 2πΔ_j/Δ_n (j = 1..n); W = |Σ_j e^{iθ_j}|². They found ρ̂₁(W) = −0.2 on 1190 blocks of n = 42 (zeros near 10²⁰,
log(T/2π) ≈ 42.3). Will's caution: per-block rescaling alone may anti-correlate neighbours in any rigid sequence.
Two wrappings, to separate that:
  own   — CD's: by the block's own length Δ_n;
  unit  — by the nominal length n (unit mean spacing; the sequences are unfolded), so no per-block rescaling.

  python cd_lag1.py OUT
  python cd_lag1.py scan OUT      ρ₁ (own wrapping) for n = 4 … 64 on F1b, F1x and 4 GUE sequences, against
                                  u = ℓ/n: the mode e^{2πiΔ/n} probes the zeros at frequency u in t (log p ↔ prime p)
"""
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2r2"))
sys.path.insert(0, os.path.join(HERE, "..", "ph2s"))

NS = (42, 16, 22)


def W_blocks(x, n, wrap):
    s = np.diff(x)
    nb = len(s) // n
    cum = np.cumsum(s[: nb * n].reshape(nb, n), axis=1)
    L = cum[:, -1:] if wrap == "own" else float(n)
    z = np.exp(2j * np.pi * cum / L).sum(axis=1)
    return np.abs(z) ** 2


def lag_corr(Ws, k=1):
    """Pooled lag-k correlation over sequences, each centred on its own mean; SE ≈ 1/√(number of pairs)."""
    num = den = 0.0
    npairs = 0
    for W in Ws:
        d = W - W.mean()
        num += float(np.dot(d[:-k], d[k:]))
        den += float(np.dot(d, d))
        npairs += len(d) - k
    return num / den, 1 / math.sqrt(npairs), npairs


def main(out):
    res = {}
    gue = [np.load(f) for f in sorted(glob.glob(os.path.join(HERE, "gue_s1", "gue_L1000000_s0*.npy")))]
    for n in NS:
        for wrap in ("own", "unit"):
            Ws = [W_blocks(x, n, wrap) for x in gue]
            r1, se, m = lag_corr(Ws)
            mw = float(np.mean(np.concatenate(Ws)))
            res[f"GUE_n{n}_{wrap}"] = dict(rho1=r1, se=se, pairs=m, mean_W=mw)
            print("GUE (16 x 1e6)  n=%2d  %-4s  ρ₁ %+.4f ± %.4f  (pairs %d, mean W %.3f)" % (n, wrap, r1, se, m, mw), flush=True)
    import r2prep as P
    import r2run as RR
    import s1lib as S1
    for name in ("F1a", "F1b", "F1c", "F1d", "F1e", "F1x"):
        t = RR.read_platt_heights(os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh", S1.F1[name][0]))
        x = np.asarray(P.nbar(t), float)
        ell = float(np.log(np.median(t) / (2 * np.pi)))
        for n in (42, int(ell)):
            for wrap in ("own", "unit"):
                r1, se, m = lag_corr([W_blocks(x, n, wrap)])
                res[f"{name}_n{n}_{wrap}"] = dict(ell=ell, rho1=r1, se=se, pairs=m)
                print("%s (ℓ %.2f)  n=%2d  %-4s  ρ₁ %+.4f ± %.4f" % (name, ell, n, wrap, r1, se), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "cd_lag1.json"), "w"), indent=1)


def scan(out):
    import r2prep as P
    import r2run as RR
    import s1lib as S1
    gue = [np.load(f) for f in sorted(glob.glob(os.path.join(HERE, "gue_s1", "gue_L1000000_s00[0-3].npy")))]
    seqs = {"GUE": (gue, None)}
    for name in ("F1b", "F1x"):
        t = RR.read_platt_heights(os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh", S1.F1[name][0]))
        seqs[name] = ([np.asarray(P.nbar(t), float)], float(np.log(np.median(t) / (2 * np.pi))))
    res = {}
    for name, (xs, ell) in seqs.items():
        rows = []
        for n in range(4, 65):
            r1, se, _ = lag_corr([W_blocks(x, n, "own") for x in xs])
            rows.append(dict(n=n, u=(ell / n if ell else None), rho1=r1, se=se))
        res[name] = dict(ell=ell, rows=rows)
        print(name, "ℓ =", ell)
        print("   " + "\n   ".join("n=%2d u=%s ρ₁ %+.3f" % (r["n"], "%.3f" % r["u"] if r["u"] else "  -  ", r["rho1"]) for r in rows))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "cd_lag1_scan.json"), "w"), indent=1)


if __name__ == "__main__":
    scan(sys.argv[2]) if sys.argv[1] == "scan" else main(sys.argv[1])
