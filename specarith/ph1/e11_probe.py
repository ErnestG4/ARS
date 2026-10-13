"""E₁₁ fresh-range cost on spot (thirty-third round P5: X′ = largest d with projected generation ≤ 24 h at the rate
measured on spot, rounded down; thirty-seventh round: measure on an idle spot, plus a worker-count probe).

Workers run gen_twists_e11.one (the production code path, divz 64) on DISTINCT twists near a magnitude d₀, all started
together, so each timing is taken under the load of P concurrent workers. Nothing is kept but the timings (zeros are
discarded; this is not generation).

  python e11_probe.py worker MAG W K OUT    worker W times K twists from items(MAG, MAG + 60000)[W·K : (W+1)·K]
  python e11_probe.py project PROBE_DIR P   per-twist cost model t(d) = a·d^b from the P-worker cost runs, then X′
"""
import glob
import json
import math
import os
import sys
import time

import gen_twists_e11 as G

BUDGET_H = 24.0
D0 = 400_000
ROUND_TO = 100_000          # "rounded down" read as: to a multiple of 10⁵ (thirty-third round; reading recorded)


def worker(mag, w, k, out):
    pari = G.setup()
    ds = G.items(mag, mag + 60_000)[w * k:(w + 1) * k]
    for d in ds:
        t0 = time.time()
        G.one(pari, d, 64)
        rec = dict(mag=mag, worker=w, d=d, secs=time.time() - t0)
        with open(out, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
            fh.flush()


def project(probe_dir, P):
    import numpy as np
    rows = [json.loads(l) for f in glob.glob(os.path.join(probe_dir, f"cost_P{P}_*.jsonl")) for l in open(f)]
    d = np.array([r["d"] for r in rows], float)
    t = np.array([r["secs"] for r in rows], float)
    b, loga = np.polyfit(np.log(d), np.log(t), 1)
    a = math.exp(loga)
    print(f"cost model at P = {P}: t(d) = {a:.3e}·d^{b:.3f} s  ({len(rows)} twists, d {d.min():.0f}–{d.max():.0f})")
    for mag in sorted({r["mag"] for r in rows}):
        sel = [r["secs"] for r in rows if r["mag"] == mag]
        print(f"  d ≈ {mag:.1e}: mean {np.mean(sel):.0f} s per twist (n = {len(sel)})")
    # cumulative projected wall time over the fresh range (4·10⁵, X]: Σ t(d) / P
    items = G.items(D0, 3_000_000)
    cum, X = 0.0, None
    for dd in items:
        cum += a * dd ** b / P
        if cum / 3600 > BUDGET_H:
            break
        X = dd
    Xr = (X // ROUND_TO) * ROUND_TO
    n = sum(1 for dd in items if dd <= Xr)
    wall = sum(a * dd ** b for dd in items if dd <= Xr) / P / 3600
    out = dict(P=P, a=a, b=b, n_probe=len(rows), budget_h=BUDGET_H, X_raw=X, X_prime=Xr, n_twists=n, projected_wall_h=wall)
    json.dump(out, open(os.path.join(probe_dir, "xprime.json"), "w"), indent=1)
    print(f"largest d within {BUDGET_H} h: {X}; X′ (rounded down to 10⁵) = {Xr}: {n} twists, projected {wall:.1f} h at P = {P}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "worker":
        worker(int(a[1]), int(a[2]), int(a[3]), a[4])
    elif a[0] == "project":
        project(a[1], int(a[2]))
    else:
        raise SystemExit(__doc__)
