"""POST-HOC pipeline investigation after Diagnostic D (2026-10-18; not in DIAG_D_DESIGN.md, no verdict).

Hypothesis (ours, after D1/D2 read 'none' and k₂ at L = 3 was seen to differ between files at the same height): the
unfolded zeros sit near a lattice, x_k = N̄(γ_k) − N̄(t₀) ≈ (N(t₀) + k − ½) − N̄(t₀) − S(γ_k), with S(t) of standard
deviation only ~0.4. Windows of integer length L = 3 starting at x = 0 then see the lattice at a fixed phase
φ = frac(N(t₀) − N̄(t₀)) per file, and the count cumulants depend on φ (zeros jitter across window edges more or less
often). The CUE calibration rotates each matrix at random, so it averages over φ. If so, the per-file k₂ and k₃ are
smooth functions of φ.

  python diag_d_phase.py        → results/diag_d/PHASE.json (needs the decoded scale tables of diag_d.py)
"""
import glob
import json
import os
import struct
import sys

import mpmath as mp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import followup_pred as P  # noqa: E402
import route_a_read as RR  # noqa: E402

SETS = {"F5": P.F5, "F4": P.F4, "F3": RR.F3}
FRESH = os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh")


def phase(f, t0):
    with open(os.path.join(FRESH, f), "rb") as fh:
        struct.unpack("<Q", fh.read(8))
        _, _, n0, _ = struct.unpack("<ddQQ", fh.read(32))       # N(t0) of the first block (Platt header)
    with mp.workdps(30):
        nbar = mp.siegeltheta(t0) / mp.pi + 1
    return int(n0), float(nbar), float((n0 - nbar) % 1)


def main():
    out = {}
    for p in sorted(glob.glob(os.path.join(HERE, "results", "diag_d", "scales", "F*.json"))):
        name = os.path.basename(p)[:-5]
        s, f = name.split("_", 1)
        t0 = SETS[s][f][0]
        n0, nbar, phi = phase(f, t0)
        sc = json.load(open(p))
        out[name] = dict(N_t0=n0, Nbar_t0=nbar, phi=phi, cos2piphi=float(np.cos(2 * np.pi * phi)),
                         k2=sc["k2_full"], k3=sc["k3_full"])
        print(f"{name:28s} N(t0) {n0}  N̄(t0) {nbar:.4f}  φ {phi:.4f}  cos2πφ {np.cos(2 * np.pi * phi):+.3f}  "
              f"k2 {sc['k2_full']:.4f}  k3 {sc['k3_full']:+.5f}", flush=True)
    c = np.array([v["cos2piphi"] for v in out.values()])
    k2 = np.array([v["k2"] for v in out.values()])
    k3 = np.array([v["k3"] for v in out.values()])
    summ = dict(corr_k2_cos=float(np.corrcoef(c, k2)[0, 1]), corr_k3_cos=float(np.corrcoef(c, k3)[0, 1]))
    print(summ)
    json.dump(dict(note="POST-HOC pipeline investigation; no verdict", files=out, summary=summ),
              open(os.path.join(HERE, "results", "diag_d", "PHASE.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
