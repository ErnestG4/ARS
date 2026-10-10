"""Gate G-a(i) (combined plan §2; route (a) milestone 1, part 1): the transcribed U(N) correlations R_{N,n} (CS08 §5
RMT formulas through cs4lib's assembly) equal the exact CUE_N determinantal densities det[S_N(x_i − x_j)], for
n = 2, 3, 4 and N ∈ {2, 3, 5, 10, 50}, at random distinct points, to relative error ≤ 1e-10 (mpmath, 30 digits).
Also asserts the assembly's term counts against CS08's explicit lists.

  python gate_a1.py  ->  results/gate_a1.json
"""
import json
import os
import random

import mpmath as mp

import cs4lib as C

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 1e-10


def red_paths(seed=7):
    """Each J* piece must be exercised: a planted error in any one of J11, J12, J13, J22 must make the gate fail."""
    rnd = random.Random(seed)
    res = {}
    for piece in ("J11", "J12", "J13", "J22"):
        class Bad(C.RMT):
            pass
        orig = getattr(C.RMT, piece)
        setattr(Bad, piece, lambda self, *a, _o=orig: 1.01 * _o(self, *a))
        R = Bad(5)
        worst = 0.0
        for n in (2, 3, 4):
            for _ in range(4):
                xs = [mp.mpf(rnd.uniform(0, 6.28)) for _ in range(n)]
                ref = C.cue_det(xs, 5)
                worst = max(worst, float(abs(R.R(xs) - ref) / max(abs(ref), mp.mpf(5) ** n * mp.mpf("1e-6"))))
        res[piece] = dict(worst_rel_err=worst, FAILS_AS_REQUIRED=bool(worst > TOL))
    return res


def main(points_per=12, seed=20261010):
    C.check_counts()
    rnd = random.Random(seed)
    rows, worst = [], 0.0
    for N in (2, 3, 5, 10, 50):
        R = C.RMT(N)
        for n in (2, 3, 4):
            for _ in range(points_per):
                xs = [mp.mpf(rnd.uniform(0, 2 * 3.141592653589793)) for _ in range(n)]
                got, ref = R.R(xs), C.cue_det(xs, N)
                err = float(abs(got - ref) / max(abs(ref), mp.mpf(N) ** n * mp.mpf("1e-6")))
                worst = max(worst, err)
                rows.append(dict(N=N, n=n, x=[float(x) for x in xs], got=complex(got).real, imag=complex(got).imag,
                                 ref=float(ref), rel_err=err))
    rp = red_paths()
    out = dict(PASS=bool(worst <= TOL), worst_rel_err=worst, tol=TOL, n_points=len(rows),
               red_paths=rp, RED_PATHS_ALL_FIRE=all(v["FAILS_AS_REQUIRED"] for v in rp.values()), rows=rows)
    print("red paths (1% planted error per J* piece):", {k: ("fails" if v["FAILS_AS_REQUIRED"] else "SILENT")
                                                         + " %.1e" % v["worst_rel_err"] for k, v in rp.items()})
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "gate_a1.json"), "w"), indent=1)
    print("G-a(i)", "PASS" if out["PASS"] else "FAIL", "worst rel err %.2e over %d points" % (worst, len(rows)))
    for N in (2, 3, 5, 10, 50):
        for n in (2, 3, 4):
            e = max(r["rel_err"] for r in rows if r["N"] == N and r["n"] == n)
            print(f"  N={N:3d} n={n}: max rel err {e:.2e}")


if __name__ == "__main__":
    main()
