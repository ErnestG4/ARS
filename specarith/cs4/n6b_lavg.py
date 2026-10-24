"""n = 6 stage (b), session 2 (round 78): the averaging question. Do the 3 + 3 beat terms average out over a file's ℓ
range? (l6/N6_STAGE_B.md, session 2; declared before running.)

The (3, 3) piece ρ₆ − ρ₃ρ₃ of the full construction, split by phase class k (n6b_extract.FilteredModel.rho_cls; class 0
carries −ρ₃ρ₃), ζ at PMAX 10³, 4 in-window nodes (distinct sorted tuples × 3!²: valid, the integrand vanishes at
in-cluster coincidence), each class averaged over the 15 triangular shifts (the G-b3 treatment). After the average the
carriers are gone; what is left in a class k ≠ 0 is its beat (near-DC) content.

Heights: stratified midpoints in ℓ across the lowest corrected (B) file, zeros_46646000.dat (ℓ 15.8202–15.8643), with
weights ∝ ℓe^ℓ (zero density in ℓ); 8 heights at r = 100, 16 at r = 300.

Prediction stated before running (dephasing kernel): a beat with log(n) ≈ kℓ has phase 2πr(k − log n/ℓ), which moves
with ℓ at 2πrk/ℓ, so the file average multiplies class k's beat by S(r, k) = |Σ_ℓ w e^{2πirk(ℓ−ℓ̄)/ℓ̄}|:
0.878 (r = 100, k = 1) and 0.190 (r = 300, k = 1) for this file; ≈ 1 for the two highest files up to r ~ 10³–10⁴.
Reported per class: the dephasing ratio |Σ w b_k(ℓ)| / (Σ w |b_k(ℓ)|²)^½ beside S(r, k). Descriptive.

  python n6b_lavg.py task ELL R J OUT_DIR    one (ℓ, r, shift j) → OUT_DIR/l_*.json
  python n6b_lavg.py jobs                    the declared task list
  python n6b_lavg.py summary OUT_DIR         → OUT_DIR/LAVG.json
"""
import glob
import json
import math
import os
import sys
import time

import numpy as np

import n6b_extract as E

PMAX, NQ = 1000, 4
L_LO, L_HI = 15.8202, 15.8643                     # zeros_46646000.dat: log(t/2π) at t = 46,646,000 and 48,746,000
CASES = [(100.0, 8), (300.0, 16)]


def ells(n):
    e = [L_LO + (k + 0.5) * (L_HI - L_LO) / n for k in range(n)]
    w = np.array([x * math.exp(x) for x in e])
    return [float("%.7f" % x) for x in e], (w / w.sum()).tolist()


def jobs():
    return [(ell, r, j) for r, n in CASES for ell in ells(n)[0] for j in range(len(E.TRI))]


def task(ell, r, j, out_dir):
    path = os.path.join(out_dir, f"l_{ell}_{r}_{j:02d}.json")
    if os.path.exists(path):
        return 0
    sj = E.TRI[j][0]
    XA, WA = E._tuples(NQ, 3)
    PA, PB = np.repeat(XA, len(XA), 0), np.tile(XA, (len(XA), 1))
    W = np.repeat(WA, len(XA)) * np.tile(WA, len(XA))
    M = E.FilteredModel("zeta", ell, pmax=PMAX)
    ds = [PA[:, k] for k in range(3)] + [PB[:, k] + r + sj for k in range(3)]
    from ratios_t6 import guard
    guard(ds)
    t = time.time()
    cls = M.rho_cls(ds, {3, 4, 5})
    prod = np.real(M.rho([PA[:, k] for k in range(3)]) * M.rho([PB[:, k] for k in range(3)]))
    g = {str(k): [float(np.sum(W * np.real(v))), float(np.sum(W * np.imag(v)))] for k, v in cls.items()}
    g["0"][0] -= float(np.sum(W * prod))
    rec = dict(ell=ell, r=r, j=j, shift=sj, g=g, wall_s=round(time.time() - t, 1))
    json.dump(rec, open(path + ".part", "w"))
    os.replace(path + ".part", path)
    print(ell, r, j, rec["wall_s"], flush=True)
    return 0


def summary(out_dir):
    rec = {}
    for p in glob.glob(os.path.join(out_dir, "l_*.json")):
        d = json.load(open(p))
        rec[(d["ell"], d["r"], d["j"])] = d
    res = dict(label="round 78 stage (b) session 2: file-averaging of the 3+3 beat terms (descriptive)", cases={})
    for r, n in CASES:
        es, ws = ells(n)
        lm = sum(w * e for e, w in zip(es, ws))
        per = []
        for e in es:
            avg = {}
            for j, (_, tj) in enumerate(E.TRI):
                for k, (re_, im_) in rec[(e, r, j)]["g"].items():
                    avg[k] = avg.get(k, 0j) + tj * complex(re_, im_)
            per.append(avg)
        ks = sorted(per[0], key=int)
        row = {}
        for k in ks:
            b = np.array([p[k] for p in per])
            fav = complex(np.sum(np.array(ws) * b))
            rms = float(np.sqrt(np.sum(np.array(ws) * np.abs(b) ** 2)))
            kk = abs(int(k))
            S = float(abs(np.sum(np.array(ws) * np.exp(2j * math.pi * r * kk * (np.array(es) - lm) / lm)))) if kk else 1.0
            row[k] = dict(per_ell=[[v.real, v.imag] for v in b], file_avg=[fav.real, fav.imag], rms=rms,
                          ratio=abs(fav) / rms if rms else None, S_pred=S)
        beat = np.array([sum(p[k] for k in ks if k != "0") for p in per]).real
        full = np.array([sum(p[k] for k in ks) for p in per]).real
        res["cases"][str(r)] = dict(ells=es, weights=ws, classes=row, beat_per_ell=beat.tolist(), full_per_ell=full.tolist(),
                                    beat_file_avg=float(np.sum(np.array(ws) * beat)),
                                    beat_rms=float(np.sqrt(np.sum(np.array(ws) * beat ** 2))),
                                    full_file_avg=float(np.sum(np.array(ws) * full)))
        c = res["cases"][str(r)]
        print(f"r={r}: beat file-avg {c['beat_file_avg']:+.4f}, rms over ℓ {c['beat_rms']:.4f}, full file-avg {c['full_file_avg']:+.4f}")
        for k, v in row.items():
            if k != "0":
                print(f"   class {k}: |file avg|/rms {v['ratio']:.3f}  S_pred {v['S_pred']:.3f}")
    json.dump(res, open(os.path.join(out_dir, "LAVG.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "task":
        sys.exit(task(float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]))
    if sys.argv[1] == "jobs":
        for j in jobs():
            print(*j)
        sys.exit(0)
    if sys.argv[1] == "summary":
        sys.exit(summary(sys.argv[2]))
