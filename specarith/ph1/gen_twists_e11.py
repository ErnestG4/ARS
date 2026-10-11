"""Phase 1 zero generation, E₁₁ quadratic twists (Will, thirty-first round D1 and thirty-second round P5): GENERATION ONLY.

Family (DHKMS §4–5, lit §4.2–4.3): even quadratic twists of E₁₁ = [0, −1, 1, 0, 0] (M = 11, ω(E) = +1) by prime
fundamental discriminants d > 0 (d prime, d ≡ 1 mod 4, d ≠ 11). Sign of the twist = χ_d(−11)·ω(E); only ε = +1 is kept
(PARI ellrootno, checked against the Kronecker symbol (d/11)).
  (i)  known answer (calibration, not evidence): d ≤ 4·10⁵, DHKMS's own range;
  (ii) test: fresh d in (4·10⁵, X′], X′ declared from `cost` (budget about one day on spot; P5).
Zeros to scaled height 8 under the denser of the two scalings, T = 8·2π/log(11 d²/4π²) (DHKMS's analytic density;
plain-conductor log(11 d²) gives a lower scaled height for the same T, and the global N_std scaling lower still). Central
zeros come back from lfunzeros as exact 0 with multiplicity; their count is stored (excess vanishing, P2).

Discipline as gen_zeros.py: PARI 2.17.2 via GP strings, realprecision 38, 128-bit asserted, divz = 64, a seeded 2%
recomputed at divz = 128.

  python gen_twists_e11.py cost [NPER]          time NPER twists at each of several d magnitudes (no zero is kept)
  python gen_twists_e11.py run D0 D1 CHUNK NCHUNKS OUT     d in (D0, D1]
  python gen_twists_e11.py merge OUT TAG
"""
import glob
import hashlib
import json
import math
import os
import random
import sys
import time

E11 = "[0,-1,1,0,0]"


def setup():
    import cypari2
    pari = cypari2.Pari()
    pari.allocatemem(4 * 10 ** 9)
    pari("default(realprecision, 38)")
    return pari


def is_prime(n):
    return n > 1 and all(n % p for p in range(2, int(n ** 0.5) + 1))


def legendre11(d):
    r = pow(d % 11, 5, 11)
    return 1 if r == 1 else -1


def items(d0, d1):
    """Prime d ≡ 1 mod 4 in (d0, d1], d ≠ 11, with (d/11) = +1 (the even twists)."""
    return [d for d in range(d0 + 1, d1 + 1) if d % 4 == 1 and d != 11 and legendre11(d) == 1 and is_prime(d)]


def T_of(d):
    return 8 * 2 * math.pi / math.log(11 * d * d / (4 * math.pi ** 2))


def one(pari, d, divz):
    E = f"elltwist(ellinit({E11}), {d})"
    N = int(pari(f"ellglobalred({E})[1]"))
    eps = int(pari(f"ellrootno({E})"))
    assert N == 11 * d * d, (d, N)
    assert eps == 1, (d, eps)
    z = pari(f"lfunzeros(lfuncreate({E}), {T_of(d):.10f}, {divz})")
    nz = [x for x in z if x != 0]
    if nz:
        assert int(pari(f"bitprecision({nz[0]})")) >= 128, d
    return N, [str(x) for x in z]


def cost(nper):
    pari = setup()
    print("PARI", pari("version()"))
    out = {}
    for mag in (10 ** 4, 10 ** 5, 4 * 10 ** 5, 10 ** 6, 3 * 10 ** 6, 10 ** 7):
        ds = items(mag, mag + 20000)[:nper]
        t0 = time.time()
        nzs = [len(one(pari, d, 64)[1]) for d in ds]
        dt = (time.time() - t0) / len(ds)
        out[mag] = dict(sec_per_L=dt, n=len(ds), mean_zeros=sum(nzs) / len(nzs))
        print(f"d ~ {mag:.0e}: {dt:.2f} s per twist ({len(ds)} twists, mean {out[mag]['mean_zeros']:.1f} zeros)",
              flush=True)
    json.dump(out, open("results/twist_cost.json", "w"), indent=1)


def run(d0, d1, chunk, nchunks, out):
    pari = setup()
    rnd = random.Random(20261011 + d0)
    recs = []
    t0 = time.time()
    for i, d in enumerate(items(d0, d1)):
        if i % nchunks != chunk:
            continue
        chk = rnd.random() < 0.02
        N, z = one(pari, d, 64)
        rec = dict(d=d, conductor=N, T=T_of(d), zeros=z, root_number=1, n_central=sum(1 for x in z if float(x) == 0.0))
        if chk:
            rec["divz128_count"] = len(one(pari, d, 128)[1])
        recs.append(rec)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"e11_{d0}_{d1}_{chunk:03d}.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print("e11", d0, d1, chunk, len(recs), "L-functions, %.0f s" % (time.time() - t0), flush=True)


def merge(out, tag):
    files = sorted(glob.glob(os.path.join(out, "e11_*.jsonl")))
    recs = [json.loads(line) for f in files for line in open(f)]
    chk = [r for r in recs if "divz128_count" in r]
    res = {tag: dict(n_L=len(recs), n_zeros=sum(len(r["zeros"]) for r in recs), n_closepair_checked=len(chk),
                     n_closepair_mismatch=sum(r["divz128_count"] != len(r["zeros"]) for r in chk),
                     files={os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest() for f in files})}
    json.dump(res, open(os.path.join(out, f"MANIFEST_{tag}.json"), "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "files"} for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "cost":
        cost(int(a[2]) if len(a) > 2 else 5)
    elif a[1] == "merge":
        merge(a[2], a[3])
    else:
        run(int(a[2]), int(a[3]), int(a[4]), int(a[5]), a[6])
