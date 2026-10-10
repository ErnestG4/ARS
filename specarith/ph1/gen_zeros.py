"""Phase 1 zero generation (Will, overnight queue 2026-10-10 item 3): GENERATION ONLY. No test statistic is computed on
these zeros before the Phase 1 seal. The ranges are a deliberately wide superset of D1's options (Will decides D1 later;
the seal selects subsets, declared before any statistic):
  chi  — quadratic characters χ_d = (d/·) for every fundamental discriminant d with 3 ≤ |d| ≤ 2·10⁵ (both signs);
  ec   — one curve per isogeny class (Cremona's optimal curve, label suffix 1) for every conductor N ≤ 5·10⁴, from PARI's
         elldata (Cremona tables; elldata.tgz sha256 dd551e64…, downloaded 2026-10-10 to ~/tmp/claude/pari_data on spot).
Zeros of L(s) on the critical line up to raw height T = min(40, 8·2π/log c) (scaled height 8 with c = |d| or N),
EC central zeros included with multiplicity; per L-function also root number and (EC) analytic rank.

PARI discipline (memory: pari_lfunzeros_close_pairs; Phase 6): PARI 2.17.2 through GP strings (cypari2 library calls are
64-bit), realprecision 38, every zero list asserted 128-bit; lfunzeros sampling divz = 64; a random 2% of L-functions
(seeded) recomputed at divz = 128, counts must agree (close-pair check).

  python gen_zeros.py chi CHUNK NCHUNKS OUT
  python gen_zeros.py ec CHUNK NCHUNKS OUT
  python gen_zeros.py merge OUT
"""
import glob
import hashlib
import json
import math
import os
import random
import sys
import time

D_MAX = 200_000
N_MAX = 50_000
DATADIR = "/home/combust/tmp/claude/pari_data/data"


def setup():
    import cypari2
    pari = cypari2.Pari()
    pari.allocatemem(2 * 10 ** 9)
    pari(f'default(datadir, "{DATADIR}")')
    pari("default(realprecision, 38)")
    return pari


def T_of(c):
    return min(40.0, 8 * 2 * math.pi / math.log(c))


def zeros(pari, Lexpr, T, divz):
    z = pari(f"lfunzeros({Lexpr}, {T:.10f}, {divz})")
    out = [str(x) for x in z]
    nz = [x for x in z if x != 0]                    # EC central zeros come back as exact 0 (bitprecision +oo)
    if nz:
        assert int(pari(f"bitprecision({nz[0]})")) >= 128, Lexpr
    return out


def items(kind):
    if kind == "chi":
        return [d for d in range(-D_MAX, D_MAX + 1) if abs(d) >= 3]
    return list(range(11, N_MAX + 1))


def run(kind, chunk, nchunks, out):
    pari = setup()
    rnd = random.Random(20261010 + (kind == "ec"))
    recs = []
    t0 = time.time()
    for i, x in enumerate(items(kind)):
        if i % nchunks != chunk:
            continue
        check = rnd.random() < 0.02
        if kind == "chi":
            if not int(pari(f"isfundamental({x})")):
                continue
            L = f"lfuncreate({x})"
            T = T_of(abs(x))
            z = zeros(pari, L, T, 64)
            rec = dict(d=x, conductor=abs(x), T=T, zeros=z, root_number=1)
        else:
            labels = [str(s) for s in pari(f"apply(e->e[1], ellsearch({x}))")]
            reps = sorted({lab for lab in labels if lab.endswith("1") and not lab[-2].isdigit()})
            for lab in reps:
                E = f'ellinit("{lab}")'
                T = T_of(x)
                z = zeros(pari, f"lfuncreate({E})", T, 64)
                rec = dict(label=lab, conductor=x, T=T, zeros=z, root_number=int(pari(f"ellrootno({E})")),
                           analytic_rank=int(pari(f"ellanalyticrank({E})[1]")))
                if check:
                    rec["divz128_count"] = len(zeros(pari, f"lfuncreate({E})", T, 128))
                recs.append(rec)
            continue
        if check:
            rec["divz128_count"] = len(zeros(pari, L, T, 128))
        recs.append(rec)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"{kind}_{chunk:03d}.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(kind, chunk, len(recs), "L-functions, %.0f s" % (time.time() - t0), flush=True)


def merge(out):
    res = {}
    for kind in ("chi", "ec"):
        files = sorted(glob.glob(os.path.join(out, f"{kind}_*.jsonl")))
        recs = [json.loads(line) for f in files for line in open(f)]
        chk = [r for r in recs if "divz128_count" in r]
        bad = [r for r in chk if r["divz128_count"] != len(r["zeros"])]
        res[kind] = dict(n_L=len(recs), n_zeros=sum(len(r["zeros"]) for r in recs), n_closepair_checked=len(chk),
                         n_closepair_mismatch=len(bad), files={os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest()
                                                                for f in files})
    json.dump(res, open(os.path.join(out, "MANIFEST.json"), "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "files"} for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        merge(sys.argv[2])
    else:
        run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
