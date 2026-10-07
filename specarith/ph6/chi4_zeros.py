"""Phase 6 pre-read computation 9.1: zeros of L(s, chi_-4) by PARI (seal §9.1).

Run on spot, env `specarith` (PARI 2.17.2 via cypari2 2.2.4):
    python -I chi4_zeros.py plan                      # print the chunk boundaries (equal estimated cost)
    python -I chi4_zeros.py chunk A B OUTDIR [PREC]   # zeros in [A, B] at realprecision PREC (default 38)
    python -I chi4_zeros.py merge OUTDIR              # merge chunks, dedupe boundaries, check counts vs N(T, chi)

All PARI evaluation goes through GP strings: cypari2's library calls default to 64-bit precision whatever
realprecision says (found 2026-10-07 — pari.lfunzeros(...) returned 64-bit zeros at realprecision 57).

Chunking: one call over [0, 20000] would take ~13 h (128-bit cost per unit height grows ~T^1.7: 3.9 s for
[1000,1100], 64 s for [5000,5100] on spot). The range is cut into N_CHUNKS pieces of equal estimated cost and run
in parallel. Accuracy check (seal §9.1): the chunks [0,1000] and [19900,20000] are re-run at realprecision 57.
Reads no gate statistic: this only produces G2's input list and its accuracy check.
"""
import json
import sys
import time

T_MAX = 20000
N_CHUNKS = 20
COST_EXP = 1.7
CHECK_WINDOWS = [(0, 1000), (19900, 20000)]


def plan():
    edges = [round(T_MAX * (k / N_CHUNKS) ** (1 / (COST_EXP + 1))) for k in range(N_CHUNKS + 1)]
    edges[0], edges[-1] = 0, T_MAX
    return list(zip(edges[:-1], edges[1:]))


def chunk(a, b, outdir, prec):
    import cypari2
    pari = cypari2.Pari()
    pari.allocatemem(3 * 10**9)
    pari.set_real_precision(prec)
    t0 = time.time()
    z = pari(f"lfunzeros(lfuncreate(-4), [{a}, {b}])")
    vals = [str(x) for x in z]
    bits = sorted({int(pari.bitprecision(x)) for x in z})
    name = f"{outdir}/chi4_p{prec}_{a:05d}_{b:05d}"
    with open(name + ".txt", "w") as f:
        f.write("\n".join(vals) + "\n")
    meta = dict(a=a, b=b, realprecision=prec, bitprecision=bits, n_zeros=len(vals),
                pari_version=str(pari.version()), wall_s=round(time.time() - t0, 1))
    with open(name + ".json", "w") as f:
        json.dump(meta, f)
    print(json.dumps(meta), flush=True)


def smooth_count(T):
    """MV Thm 14.5 smooth part for chi_-4 (q = 4, odd, kappa = 1): arg Gamma(3/4 + iT/2)/pi + (T/2pi) log(q/pi)."""
    import mpmath as mp
    return float(mp.im(mp.loggamma(mp.mpf(3) / 4 + 1j * mp.mpf(T) / 2)) / mp.pi
                 + T / (2 * mp.pi) * mp.log(4 / mp.pi))


def merge(outdir):
    from decimal import Decimal
    rows, allz = [], []
    for a, b in plan():
        name = f"{outdir}/chi4_p38_{a:05d}_{b:05d}"
        meta = json.load(open(name + ".json"))
        z = [Decimal(s) for s in open(name + ".txt").read().split()]
        assert all(a <= float(x) <= b for x in z), (a, b)
        expect = smooth_count(b) - smooth_count(a)
        rows.append(dict(a=a, b=b, n=len(z), expect=round(expect, 2), dev=round(len(z) - expect, 2),
                         bits=meta["bitprecision"], wall_s=meta["wall_s"]))
        allz += z
    allz.sort()
    dedup = [allz[0]] + [x for p, x in zip(allz, allz[1:]) if x - p > Decimal("1e-20")]
    gaps = [float(y - x) for x, y in zip(dedup, dedup[1:])]
    out = dict(n_total=len(dedup), n_duplicates_removed=len(allz) - len(dedup),
               expect_total=round(smooth_count(T_MAX), 2), min_gap=min(gaps), max_gap=max(gaps), chunks=rows)
    with open(f"{outdir}/chi4_zeros_T{T_MAX}_p38.txt", "w") as f:
        f.write("\n".join(str(x) for x in dedup) + "\n")
    with open(f"{outdir}/chi4_zeros_T{T_MAX}_p38.merge.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "chunks"}))
    worst = max(rows, key=lambda r: abs(r["dev"]))
    print("worst chunk count deviation vs smooth count:", worst["a"], worst["b"], worst["dev"])


def accuracy(outdir):
    """Seal §9.1: delta_chi = 10 x max |p38 - p57| over the check windows; the counts must match exactly."""
    from decimal import Decimal
    merged = [Decimal(s) for s in open(f"{outdir}/chi4_zeros_T{T_MAX}_p38.txt").read().split()]
    rows, worst = [], Decimal(0)
    for a, b in CHECK_WINDOWS:
        hi = [Decimal(s) for s in open(f"{outdir}/chi4_p57_{a:05d}_{b:05d}.txt").read().split()]
        lo = [x for x in merged if a <= x <= b]
        assert len(lo) == len(hi), (a, b, len(lo), len(hi))
        d = max(abs(x - y) for x, y in zip(sorted(lo), sorted(hi)))
        worst = max(worst, d)
        rows.append(dict(window=[a, b], n=len(hi), max_abs_diff=float(d)))
    delta = max(float(worst) * 10, 1e-30)
    out = dict(windows=rows, max_abs_diff=float(worst), delta=delta,
               rule="delta = 10 x max |p38 - p57| over the check windows (seal §9.1)")
    with open(f"{outdir}/chi4_zeros_T{T_MAX}_p38.accuracy.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "accuracy":
        accuracy(sys.argv[2])
        sys.exit(0)
    if mode == "plan":
        for a, b in plan():
            print(a, b)
    elif mode == "chunk":
        chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 38)
    elif mode == "merge":
        merge(sys.argv[2])
    else:
        raise SystemExit(f"unknown mode {mode}")
