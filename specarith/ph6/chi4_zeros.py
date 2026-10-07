"""Phase 6 pre-read computation 9.1: zeros of L(s, chi_-4) by PARI (seal §9.1).

Usage (on spot, env `specarith`, PARI 2.17.2 via cypari2 2.2.4):
    python -I chi4_zeros.py main OUTDIR            # all zeros 0 < gamma <= 20000 at realprecision 38
    python -I chi4_zeros.py check OUTDIR           # zeros in [0,1000] and [19000,20000] at realprecision 57

Writes OUTDIR/chi4_zeros_T20000_p38.txt (one ordinate per line, as PARI prints it at the working precision) or
OUTDIR/chi4_zeros_check_p57.txt, plus a .json with PARI version, precision, count, wall time.
Reads no gate statistic: this only produces the input list for G2 and its accuracy check.
"""
import json
import sys
import time

import cypari2

T_MAX = int(sys.argv[3]) if len(sys.argv) > 3 else 20000   # third argument only for smoke tests
CHECK_WINDOWS = [(0, 1000), (19000, 20000)]


def main():
    mode, outdir = sys.argv[1], sys.argv[2]
    pari = cypari2.Pari()
    pari.allocatemem(8 * 10**9)
    prec = 38 if mode == "main" else 57
    pari.set_real_precision(prec)
    # Evaluate through GP strings: cypari2's library calls default to 64-bit precision whatever realprecision
    # says (found 2026-10-07: pari.lfunzeros(...) returned 64-bit zeros at realprecision 57).
    t0 = time.time()
    if mode == "main":
        zs = [pari(f"lfunzeros(lfuncreate(-4), {T_MAX})")]
        name = f"chi4_zeros_T{T_MAX}_p{prec}"
    elif mode == "check":
        zs = [pari(f"lfunzeros(lfuncreate(-4), [{a}, {b}])") for a, b in CHECK_WINDOWS]
        name = f"chi4_zeros_check_p{prec}"
    else:
        raise SystemExit(f"unknown mode {mode}")
    vals = [str(z) for v in zs for z in v]
    with open(f"{outdir}/{name}.txt", "w") as f:
        f.write("\n".join(vals) + "\n")
    bits = sorted({int(pari.bitprecision(z)) for v in zs for z in v})
    meta = dict(mode=mode, pari_version=str(pari.version()), realprecision=prec, bitprecision=bits, n_zeros=len(vals),
                windows=CHECK_WINDOWS if mode == "check" else [[0, T_MAX]], wall_s=round(time.time() - t0, 1))
    with open(f"{outdir}/{name}.json", "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
