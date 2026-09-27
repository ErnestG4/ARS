"""S4-sup (STAGE3_SEED_PREREG.md, S4 note, 746d130): LABELLED SUPPLEMENTARY -- outside the S4 licence.
The frozen S4 planted effect overshoots (1 level per head -> flat dq -0.058). Here one level is replaced in a random third
of heads (128 of 384; flat dq ~ -0.019), otherwise identical to stage3_calib_v2.pool_one: paired, both truth families,
R = 100, seed offset +2,000,000. Reports each calibrator's recovery at the observed effect size. A licensed calibrator
whose recovery here is outside [0.7, 1.3] is reported "licensed at 3x effect, degraded at 1x" (qualifies the re-score's
reading; does not change its lattice verdict).
Output: results/stage3_calib_v2_sup.json (+ _pools.jsonl, resumable). STOP-aware.
"""
import json, os, sys
from pathlib import Path
from multiprocessing import Pool
import numpy as np
import stage3_calib_v2 as C
import remote_st as RS

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "stage3_calib_v2_sup.json"
POOLS = ROOT / "results" / "stage3_calib_v2_sup_pools.jsonl"


def pool_one(args):
    fam, r = args
    rng = np.random.default_rng(C.SEED + r + 2_000_000 + (0 if fam == "T_lam" else 1_000_000))
    T = [C.truth(fam, np.sort(s ** 2)) for s in C.real_heads("pythia-410m")]
    planted = set(rng.choice(len(T), len(T) // 3, replace=False).tolist())
    u = [C.coe(64, rng) for _ in T]
    ub = [C.plant(x, 1 / 64, rng) if i in planted else x for i, x in enumerate(u)]
    up = [C.coe(64, rng) for _ in T]
    A = [C.to_sig(x, t) for x, t in zip(u, T)]; B = [C.to_sig(x, t) for x, t in zip(ub, T)]
    rec = {"fam": fam, "pool": r, "a": C.q_rt(A), "b": C.q_rt(B), "truth_fresh": C.q_rt([C.to_sig(x, t) for x, t in zip(up, T)])}
    for k in C.KINDS:
        Fa = [C.fit(k, np.sort(s ** 2)) for s in A]; Fb = [C.fit(k, np.sort(s ** 2)) for s in B]
        rec[k] = {"cal_a": C.q_rt([C.to_sig(x, F) for x, F in zip(up, Fa)]), "cal_b": C.q_rt([C.to_sig(x, F) for x, F in zip(up, Fb)])}
    return rec


def main(workers=10):
    done = {(d["fam"], d["pool"]) for d in map(json.loads, POOLS.read_text().splitlines())} if POOLS.exists() else set()
    todo = [(fam, r) for r in range(C.R_POOLS) for fam in C.FAMS if (fam, r) not in done]
    with Pool(workers) as P:
        for rec in P.imap_unordered(pool_one, todo):
            with open(POOLS, "a") as fh:
                fh.write(json.dumps(rec, default=float) + "\n"); fh.flush(); os.fsync(fh.fileno())
            print(f"sup {rec['fam']} pool {rec['pool']:3d}", flush=True)
            RS.check_stop()
    ka = C.summarise([json.loads(l) for l in POOLS.read_text().splitlines()])
    out = {"doc": __doc__, "known_answer": ka,
           "recovery_in_band": {X: {k: all(0.7 <= ka[f][k][X]["recovery"] <= 1.3 for f in C.FAMS) for k in C.KINDS}
                                for X in ("q", "rt")}}
    RS.durable_save(OUT, lambda p: p.write_text(json.dumps(out, indent=1, default=float)))
    print(json.dumps(out["recovery_in_band"], indent=1))
    for f in C.FAMS:
        print(f, "E_q", ka[f]["E_q"], "E_rt", ka[f]["E_rt"])
        for k in C.KINDS:
            print(f"  {k:7s} q rec {ka[f][k]['q']['recovery']:+.3f}  rt rec {ka[f][k]['rt']['recovery']:+.3f}")


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    try:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 10)
    except RS.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
