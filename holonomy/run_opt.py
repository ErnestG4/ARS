"""Optional pairs (brief §8) — run IFF the sealed wall-clock trigger fired.
COMMITTED GENERATOR of holonomy/opt_measured.json.

OP1 (exploratory-lane point-check, no sealed continuum prediction):
  surrogate-generation <-> unfolding, 1-D, trended GUE at dial 1.0.
  Surrogate = n iid uniforms over the CURRENT state's span, from PRE-DRAWN
  per-slot uniforms (§0, tripwire 6).  Verdicts limited to
  POINT_CHECK_CLEAN / NONCOMMUTING_UNPREDICTED / UNDERPOWERED.

OP2 (sealed-formula pair): disattenuation <-> pooling.
  Two groups, anticorrelated x/y reliabilities; sealed Jensen-gap formula
  Delta_pred = rho * (1 - mean_g sqrt(Rxg Ryg) / sqrt(Rxbar Rybar))
  evaluated against the measured paired Delta at k*sigma.
"""

import hashlib
import json
import sys
import time

import numpy as np
from scipy.stats import norm

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

from transitions import gen_trended_set, unfold_poly, sigma2_at        # noqa: E402

SEAL = json.load(open(f"{ROOT}/holonomy/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/holonomy/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f} — dated addendum required"

K = SEAL["k_arc"]
OP = SEAL["optional_pairs"]


def op1():
    L = OP["op1_L"]
    dd = []
    for s in range(OP["op1_seeds"]):
        st = gen_trended_set(seed=500 + s, N=2048, n_keep=1200,
                             a=0.25, ell=600.0)
        x = np.sort(st["x"])
        u_pre = np.random.default_rng(600 + s).uniform(size=x.size)  # §0
        def surr(y):
            return np.sort(y[0] + u_pre * (y[-1] - y[0]))
        def unf(y):
            return np.sort(unfold_poly(np.sort(y), 5))
        sA = float(sigma2_at(surr(unf(x)), [L])[0])   # unfold -> surrogate
        sB = float(sigma2_at(unf(surr(x)), [L])[0])   # surrogate -> unfold
        dd.append(sA - sB)
    d = np.array(dd)
    sem = float(d.std(ddof=1) / np.sqrt(len(d)))
    z = float(d.mean() / sem)
    powered = bool(K * sem <= OP["op1_mdd"])
    clean = bool(abs(z) <= K)
    meas = ("POINT_CHECK_CLEAN" if clean and powered else
            "UNDERPOWERED" if not powered else "NONCOMMUTING_UNPREDICTED")
    return dict(mean=float(d.mean()), sem=sem, z=z, powered=powered,
                measurement=meas)


def op2():
    rho = OP["op2_rho"]
    R = OP["op2_reliabilities"]          # [[Rx1,Ry1],[Rx2,Ry2]]
    sq = [np.sqrt(rx * ry) for rx, ry in R]
    Rxb = np.mean([r[0] for r in R])
    Ryb = np.mean([r[1] for r in R])
    delta_pred = rho * (1.0 - np.mean(sq) / np.sqrt(Rxb * Ryb))
    n = OP["op2_n_per_group"]
    dd = []
    for s in range(OP["op2_seeds"]):
        rng = np.random.default_rng(700 + s)
        xs, ys = [], []
        r_disatt = []
        for (rx, ry) in R:
            z0 = rng.standard_normal(n)
            x = np.sqrt(rx) * (np.sqrt(rho) * z0
                               + np.sqrt(1 - rho) * rng.standard_normal(n)) \
                + np.sqrt(1 - rx) * rng.standard_normal(n)
            y = np.sqrt(ry) * (np.sqrt(rho) * z0
                               + np.sqrt(1 - rho) * rng.standard_normal(n)) \
                + np.sqrt(1 - ry) * rng.standard_normal(n)
            xs.append(x)
            ys.append(y)
            r_disatt.append(np.corrcoef(x, y)[0, 1] / np.sqrt(rx * ry))
        A = float(np.mean(r_disatt))                       # disatt -> pool
        xp, yp = np.concatenate(xs), np.concatenate(ys)
        B = float(np.corrcoef(xp, yp)[0, 1] / np.sqrt(Rxb * Ryb))
        dd.append(A - B)
    d = np.array(dd)
    sem = float(d.std(ddof=1) / np.sqrt(len(d)))
    z = float((d.mean() - delta_pred) / sem)
    law = bool(abs(z) <= K)
    meas = "COMMUTATOR_MEASURED" if law else "NONCOMMUTING_UNPREDICTED"
    return dict(mean=float(d.mean()), sem=sem, delta_pred=float(delta_pred),
                z_vs_pred=z, law_agrees=law, measurement=meas)


def main():
    t0 = time.time()
    # trigger check (sealed BEFORE compute)
    tot = sum(json.load(open(f"{ROOT}/holonomy/{f}"))["elapsed_sec"]
              for f in ("p1_measured.json", "p2_measured.json",
                        "p3_measured.json"))
    fired = bool(tot < SEAL["optional_trigger_wallclock_sec"])
    out = dict(seal_cited="holonomy/prereg_sealed.json",
               mandatory_wallclock_sec=float(tot), trigger_fired=fired)
    if fired:
        out["op1"] = op1()
        print(f"OP1: {out['op1']['measurement']} mean="
              f"{out['op1']['mean']:+.4f}±{out['op1']['sem']:.4f}")
        out["op2"] = op2()
        print(f"OP2: {out['op2']['measurement']} mean="
              f"{out['op2']['mean']:+.5f}±{out['op2']['sem']:.5f} "
              f"pred={out['op2']['delta_pred']:+.5f} "
              f"z={out['op2']['z_vs_pred']:+.2f}")
    else:
        print(f"optional trigger NOT fired (wallclock {tot:.0f}s >= "
              f"{SEAL['optional_trigger_wallclock_sec']}s) — skipped by rule")
    out["elapsed_sec"] = float(time.time() - t0)
    json.dump(out, open(f"{ROOT}/holonomy/opt_measured.json", "w"), indent=1)


if __name__ == "__main__":
    main()
