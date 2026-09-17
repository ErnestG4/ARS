"""T2 — traversal statistic re-sealed: MAD-based jump count + monotone-winding clause.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage3f_traversal2_measured.json.
Pre-registration: RING_BRIEF.md "T2" (3ad1651). verify_ring.py R13d scores.
J_mad = #{steps with |dphi| > 5 * MAD(|dphi|)}; M = fraction of steps with
sign(dphi) = sign(net winding) among steps with |dphi| > MAD. Same clouds as T1
(A, IND, C_ord, C_perm, D), 3 seeds, rho = 50, bin 0.5, sigma_s 1.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import json
import sys
import time
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import order_parameter                              # noqa: E402
from ring import stage1_ph as PH                                      # noqa: E402
from ring import stage3_lift as S3                                    # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                # noqa: E402

warnings.filterwarnings("ignore")
INSTRUMENT = Model("ring_traversal2_v1", [
    Param("mad_mult", DECLARED, value=5.0, why="conventional MAD multiplier for a jump; no new scale parameter"),
    Param("mono_floor", DECLARED, value=1.0, why="steps with |dphi| > 1*MAD count toward monotonicity"),
    Param("rho", DECLARED, value=50.0, why="as T1"),
    Param("bin", DECLARED, value=0.5, why="as T1"),
    Param("sigma_s", DECLARED, value=1.0, why="as T1"),
    Param("seed_emit", TESTED, sweep=[41, 42, 43], why="as T1"),
    Param("cloud", TESTED, sweep=["A", "IND", "C_ord", "C_perm", "D"], why="as T1"),
])
P = {p.name: p for p in INSTRUMENT.params}
dt = S3.dt
N = S3.N


def stats(phi):
    d = np.angle(np.exp(1j * np.diff(phi)))
    a = np.abs(d)
    mad = float(np.median(np.abs(a - np.median(a))))
    mad = max(mad, 1e-12)
    J = int((a > P["mad_mult"].value * mad).sum())
    net = float(np.unwrap(phi)[-1] - np.unwrap(phi)[0])
    sgn = np.sign(net) if net != 0 else 1.0
    big = a > P["mono_floor"].value * mad
    M = float((np.sign(d[big]) == sgn).mean()) if big.any() else float("nan")
    return dict(J_mad=J, M=M, mad=mad, net_turns=net / (2 * np.pi), n_steps=int(len(d)))


def main():
    t0 = time.time()
    prof, psi0 = S3.bump_profile()
    g = 0.02
    ratesA = S3.simulate(g, 50.0, 1000.0, 0.37)
    _, psiA = order_parameter(ratesA)
    ratesIND = S3.ind_rates(psiA, prof, psi0)
    B = 16
    offgrid = 2 * np.pi * (np.arange(B) + 0.37) / B
    segs = [S3.simulate(0.0, 50.0, 1000.0 / B, a) for a in offgrid]
    ratesD = np.concatenate([S3.simulate(0.0, 2000.0, 1000.0 / B, a) for a in offgrid[:3]], 0)
    PH.P["rho"].value = P["rho"].value
    rows = []
    for seed in P["seed_emit"].sweep:
        perm = np.random.default_rng(seed + 500).permutation(B)
        clouds = {"A": ratesA, "IND": ratesIND, "C_ord": np.concatenate(segs, 0),
                  "C_perm": np.concatenate([segs[i] for i in perm], 0), "D": ratesD}
        for name in P["cloud"].sweep:
            rates = clouds[name]
            sp = PH.emit(rates, np.random.default_rng(seed))
            X = S3.popvecs(sp, rates.shape[0] * dt, P["bin"].value, P["sigma_s"].value)
            L = S3.lift(X)
            if L is None or L["mode"] != "standard":
                rows.append(dict(cloud=name, seed=seed, readable=False))
                print(f"{name:<6} seed={seed}: UNREADABLE")
                continue
            st = stats(L["phi"])
            rows.append(dict(cloud=name, seed=seed, readable=True, **st))
            print(f"{name:<6} seed={seed}: J_mad={st['J_mad']:3d} M={st['M']:.3f} MAD={st['mad']:.4f} net={st['net_turns']:+.2f} turns")
    PH.P["rho"].value = 50.0
    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), rows=rows,
               wall_s=round(time.time() - t0, 1))
    with open(os.path.join(HERE, "stage3f_traversal2_measured.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote stage3f_traversal2_measured.json ({out['wall_s']}s)")


if __name__ == "__main__":
    main()
