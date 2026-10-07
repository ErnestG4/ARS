"""Phase 6 pre-read 9.1, second recipe: zeros of L(s, chi_-4) by PARI with a finer zero search (seal §9.1; A8).

Why v2: the v1 run (chi4_zeros.py, PARI's default divz = 8) MISSED close zero pairs. Its merged list had 26,893 zeros
against MV Thm 14.5's smooth count 26,903.37 (the fail-closed count assertion fired), and the four widest gaps (3.0-3.5
mean spacings) each hid a pair 0.016-0.07 apart. divz = 16 still misses the closest (0.016); divz = 32 finds all four.
v2 uses divz = 64 for margin and adds a Turing-style completeness check: S_k = (k - 1/2) - Nbar(gamma_k) is O(1) with zero
mean, so a missed zero leaves a persistent -1 step in its block means.

Run on spot, env `specarith` (PARI 2.17.2 via cypari2 2.2.4); all PARI evaluation through GP strings (cypari2 library
calls are 64-bit whatever realprecision says):
    python chi4_zeros_v2.py plan T_MAX N_CHUNKS [T_LO]     # cost-balanced chunk edges (cost/unit ~ 0.44 + 1.77e-5 T, v1 timings)
    python chi4_zeros_v2.py chunk A B OUTDIR PREC DIVZ      # zeros in [A, B]
    python chi4_zeros_v2.py merge OUTDIR T_MAX              # merge the p38 chunks listed in OUTDIR/jobs.txt; checks; write list
    python chi4_zeros_v2.py accuracy OUTDIR T_MAX           # delta = 10 x max |p38 - p57| on the p57 check windows
Reads no gate statistic.
"""
import json
import math
import sys
import time

DIVZ = 64
BLOCK = 250                       # zeros per block for the S-profile check
BLOCK_MEAN_LIMIT = 0.6            # |block mean of S| above this flags a missed (or spurious) zero


def plan(t_max, n_chunks, t_lo=0):
    a0, a1 = 0.44, 1.77e-5        # per-unit cost model from the v1 chunk timings (s per unit height at divz 8)
    C = lambda T: a0 * T + a1 * T * T / 2
    total = C(t_max) - C(t_lo)
    edges = [t_lo]
    for k in range(1, n_chunks):
        target = C(t_lo) + total * k / n_chunks
        lo, hi = float(t_lo), float(t_max)
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if C(mid) < target else (lo, mid)
        edges.append(int(round((lo + hi) / 2)))
    edges.append(t_max)
    return list(zip(edges[:-1], edges[1:]))


def chunk(a, b, outdir, prec, divz):
    import cypari2
    pari = cypari2.Pari()
    pari.allocatemem(3 * 10**9)
    pari.set_real_precision(prec)
    t0 = time.time()
    z = pari(f"lfunzeros(lfuncreate(-4), [{a}, {b}], {divz})")
    vals = [str(x) for x in z]
    bits = sorted({int(pari.bitprecision(x)) for x in z})
    name = f"{outdir}/chi4_p{prec}_d{divz}_{a:05d}_{b:05d}"
    with open(name + ".txt", "w") as f:
        f.write("\n".join(vals) + "\n")
    meta = dict(a=a, b=b, realprecision=prec, divz=divz, bitprecision=bits, n_zeros=len(vals),
                pari_version=str(pari.version()), wall_s=round(time.time() - t0, 1))
    with open(name + ".json", "w") as f:
        json.dump(meta, f)
    print(json.dumps(meta), flush=True)


def smooth_count(T):
    """MV Thm 14.5 smooth part for chi_-4 (q = 4, odd, kappa = 1): arg Gamma(3/4 + iT/2)/pi + (T/2pi) log(q/pi)."""
    import mpmath as mp
    return float(mp.im(mp.loggamma(mp.mpf(3) / 4 + 1j * mp.mpf(T) / 2)) / mp.pi
                 + T / (2 * mp.pi) * mp.log(4 / mp.pi))


def _jobs(outdir, prec):
    rows = []
    for line in open(f"{outdir}/jobs.txt"):
        a, b, p, d = line.split()
        if int(p) == prec:
            rows.append((int(a), int(b), int(d)))
    return rows


def merge(outdir, t_max):
    from decimal import Decimal
    import numpy as np
    rows, allz = [], []
    for a, b, d in _jobs(outdir, 38):
        name = f"{outdir}/chi4_p38_d{d}_{a:05d}_{b:05d}"
        meta = json.load(open(name + ".json"))
        z = [Decimal(s) for s in open(name + ".txt").read().split()]
        assert all(a <= float(x) <= b for x in z), (a, b)
        expect = smooth_count(b) - smooth_count(a)
        rows.append(dict(a=a, b=b, n=len(z), expect=round(expect, 2), dev=round(len(z) - expect, 2),
                         divz=meta["divz"], bits=meta["bitprecision"], wall_s=meta["wall_s"]))
        allz += z
    assert rows[0]["a"] == 0 and rows[-1]["b"] == t_max and all(r["b"] == s["a"] for r, s in zip(rows, rows[1:]))
    allz.sort()
    dedup = [allz[0]] + [x for p, x in zip(allz, allz[1:]) if x - p > Decimal("1e-20")]
    g = np.array([float(x) for x in dedup])
    S = (np.arange(1, len(g) + 1) - 0.5) - np.array([smooth_count(t) for t in g])
    nb = len(S) // BLOCK
    bm = [float(S[i * BLOCK:(i + 1) * BLOCK].mean()) for i in range(nb)]
    flagged = [(i, round(m, 3), float(g[i * BLOCK])) for i, m in enumerate(bm) if abs(m) > BLOCK_MEAN_LIMIT]
    gaps = np.diff(g)
    out = dict(n_total=len(dedup), n_duplicates_removed=len(allz) - len(dedup),
               expect_total=round(smooth_count(t_max), 2), count_dev=round(len(dedup) - smooth_count(t_max), 3),
               min_gap=float(gaps.min()), max_gap=float(gaps.max()),
               S_block_mean_min=min(bm), S_block_mean_max=max(bm), S_blocks_flagged=flagged, chunks=rows)
    with open(f"{outdir}/chi4_zeros_T{t_max}_p38.txt", "w") as f:
        f.write("\n".join(str(x) for x in dedup) + "\n")
    with open(f"{outdir}/chi4_zeros_T{t_max}_p38.merge.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "chunks"}))
    assert abs(out["count_dev"]) < 2, ("count vs MV Thm 14.5", out)
    assert out["min_gap"] > 1e-8, ("near-duplicate zeros", out["min_gap"])
    assert not flagged, ("S-profile blocks flagged (missed or spurious zeros)", flagged)


def accuracy(outdir, t_max):
    from decimal import Decimal
    merged = [Decimal(s) for s in open(f"{outdir}/chi4_zeros_T{t_max}_p38.txt").read().split()]
    rows, worst = [], Decimal(0)
    for a, b, d in _jobs(outdir, 57):
        hi = [Decimal(s) for s in open(f"{outdir}/chi4_p57_d{d}_{a:05d}_{b:05d}.txt").read().split()]
        lo = [x for x in merged if a <= x <= b]
        assert len(lo) == len(hi), (a, b, len(lo), len(hi))
        dmax = max(abs(x - y) for x, y in zip(sorted(lo), sorted(hi)))
        worst = max(worst, dmax)
        rows.append(dict(window=[a, b], n=len(hi), max_abs_diff=float(dmax)))
    out = dict(windows=rows, max_abs_diff=float(worst), delta=max(float(worst) * 10, 1e-30),
               rule="delta = 10 x max |p38 - p57| over the check windows (seal §9.1)")
    with open(f"{outdir}/chi4_zeros_T{t_max}_p38.accuracy.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out))


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "plan":
        for a, b in plan(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 0):
            print(a, b)
    elif m == "chunk":
        chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), int(sys.argv[6]))
    elif m == "merge":
        merge(sys.argv[2], int(sys.argv[3]))
    elif m == "accuracy":
        accuracy(sys.argv[2], int(sys.argv[3]))
    else:
        raise SystemExit(m)
