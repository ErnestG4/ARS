"""Phase 1 zero generation, U family (Will, thirty-first round D1): GENERATION ONLY, no statistic before the Phase 1 seal.

  u — primitive COMPLEX Dirichlet characters mod prime q ≤ 1000, conjugate pairs counted once. The representative is the
      PARI character [k] on the generator of znstar(q,1), k = 1 … (q−3)/2; its conjugate is [q−1−k], and [(q−1)/2] is the
      real (Legendre) character, which belongs to USp. 37,812 L-functions.
Zeros on [−T, T] with T = 8·2π/log q (scaled height 8 on both sides): for a complex χ the negative zeros are those of χ̄,
so one representative's two-sided list is the pair's zeros, counted once.

Discipline as gen_zeros.py (memory: pari_lfunzeros_close_pairs): PARI 2.17.2 through GP strings, realprecision 38,
128-bit asserted, divz = 64; a seeded random 2% recomputed at divz = 128 (counts must agree). Before the run, `check`
verifies on a few characters that χ̄'s zeros are χ's negated (the two-sided convention rests on it).

  python gen_zeros_u.py check
  python gen_zeros_u.py u CHUNK NCHUNKS OUT
  python gen_zeros_u.py merge OUT
"""
import glob
import hashlib
import json
import math
import os
import random
import sys
import time
from decimal import Decimal, getcontext

getcontext().prec = 50
Q_MAX = 1000


def setup():
    import cypari2
    pari = cypari2.Pari()
    pari.allocatemem(2 * 10 ** 9)
    pari("default(realprecision, 38)")
    return pari


def T_of(q):
    return 8 * 2 * math.pi / math.log(q)


def primes():
    return [q for q in range(5, Q_MAX + 1) if all(q % p for p in range(2, int(q ** 0.5) + 1))]


def items():
    return [(q, k) for q in primes() for k in range(1, (q - 3) // 2 + 1)]


def zeros(pari, q, k, divz):
    T = T_of(q)
    z = pari(f"lfunzeros(lfuncreate([znstar({q},1), [{k}]]), [-{T:.10f}, {T:.10f}], {divz})")
    out = [str(x) for x in z]
    if len(z):
        assert int(pari(f"bitprecision({z[0]})")) >= 128, (q, k)
    return out


def check():
    pari = setup()
    print("PARI", pari("version()"))
    worst = 0.0
    for q, k in [(5, 1), (101, 7), (997, 3), (997, 400)]:
        assert int(pari(f"znconreyconductor(znstar({q},1), [{k}])")) == q, (q, k)       # primitive
        a = sorted(Decimal(x.replace(" E", "E")) for x in zeros(pari, q, k, 64))       # 38 digits: floats would cap at 1e-15
        b = sorted(Decimal(x.replace(" E", "E")) for x in zeros(pari, q, q - 1 - k, 64))
        assert len(a) == len(b), (q, k, len(a), len(b))
        worst = max([worst] + [float(abs(x + y)) for x, y in zip(a, b[::-1])])
        print(q, k, len(a), "zeros on [-T,T]")
    print("max |z(chi) + z(chi-bar) reversed| =", worst)
    assert worst < 1e-25
    assert len(items()) == 37812
    print("check PASS")


def run(chunk, nchunks, out):
    pari = setup()
    rnd = random.Random(20261011)
    recs = []
    t0 = time.time()
    for i, (q, k) in enumerate(items()):
        if i % nchunks != chunk:
            continue
        chk = rnd.random() < 0.02
        rec = dict(q=q, k=k, conductor=q, T=T_of(q), zeros=zeros(pari, q, k, 64))
        if chk:
            rec["divz128_count"] = len(zeros(pari, q, k, 128))
        recs.append(rec)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"u_{chunk:03d}.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print("u", chunk, len(recs), "L-functions, %.0f s" % (time.time() - t0), flush=True)


def merge(out):
    files = sorted(glob.glob(os.path.join(out, "u_*.jsonl")))
    recs = [json.loads(line) for f in files for line in open(f)]
    chk = [r for r in recs if "divz128_count" in r]
    res = dict(u=dict(n_L=len(recs), n_zeros=sum(len(r["zeros"]) for r in recs), n_closepair_checked=len(chk),
                      n_closepair_mismatch=sum(r["divz128_count"] != len(r["zeros"]) for r in chk),
                      files={os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest() for f in files}))
    assert res["u"]["n_L"] == 37812, res["u"]["n_L"]
    json.dump(res, open(os.path.join(out, "MANIFEST_U.json"), "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "files"} for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "check":
        check()
    elif sys.argv[1] == "merge":
        merge(sys.argv[2])
    else:
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
