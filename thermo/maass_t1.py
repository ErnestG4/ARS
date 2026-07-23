"""
thermo/maass_t1.py — push the Mayer bridge's t_1 from 4 digits to ~20. (v2 handoff §9.1)

`sessionK/mayer_run1.py` already welds CP1 to CP2: it locates parity-resolved zeros of
det(1 -/+ L_s) on Re(s)=1/2 and matched 70 LMFDB Maass eigenvalues. But it is float64 with a
2-term Taylor tail, and scans on a dr=0.02 grid with parabolic refinement, so t_1 lands at
9.5354 vs LMFDB 9.5337 -- about 4 digits. That is a 4-digit weld under a 24-digit operator.

This closes the gap using thermo/gauss_thermo.py, whose `matrix()` already accepts complex s
and closes the n-sum tail EXACTLY in Hurwitz zeta.

  Mayer:  Z_Selberg(s) = det(1 - L_s) * det(1 + L_s)
          det(1 + L_s) = 0  <=>  L_s has eigenvalue -1  <=>  ODD  (LMFDB sym1)
  t_1 is the first ODD Maass eigenvalue, so it is a zero of det(1 + L_s).
  (Parity convention settled in Session K Run 1: sym0=even, sym1=odd. Confirm against
  Lewis-Zagier arXiv math/0101270 before quoting parity downstream -- v2 handoff §5.)

METHOD. F(r) = det(I + L_{1/2+ir}), root-found by secant in the COMPLEX r-plane.
F is complex-valued for real r (it is c*g(r) for a fixed complex phase c and a real g), so
minimising |F| would halve the digits and forcing r real would need the phase divided out.
Letting r be complex avoids both: secant converges superlinearly to the complex root, and

    Im(r) ~ 0 is then a FREE correctness check -- it is not imposed anywhere,
    so recovering it confirms the zero sits on the critical line.

Accuracy is certified by an N-ladder (self-consistency across truncation), not by agreement
with the reference alone -- the same discipline that adjudicated the GKW constant.

Run:  python3 thermo/maass_t1.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thermo.gauss_thermo import GaussOperator          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# Reference from the v2 handoff (Booker, LuCaNT 2023 = LMFDB). Treated as a CHECK, not as
# the certificate: the ladder below is the primary evidence.
T1_REF_STR = "9.53369526135355755434"


def F(op, r, parity="odd"):
    """det(I -/+ L_{1/2+ir}).  odd -> det(I+L) (eigenvalue -1); even -> det(I-L) (+1)."""
    M = op.matrix(mp.mpf("0.5") + 1j * r)
    I = mp.eye(M.rows)
    return mp.det(I + M) if parity == "odd" else mp.det(I - M)


def solve_root(N, dps, Ne, start, parity="odd", op=None):
    op = op or GaussOperator(N=N, dps=dps, Ne=Ne)
    with mp.workdps(dps):
        return mp.findroot(lambda r: F(op, r, parity), mp.mpc(start), solver="secant",
                           tol=mp.mpf(10) ** (-int(0.6 * dps)))


def solve_t1(N, dps, Ne, start="9.5337"):
    return solve_root(N, dps, Ne, start, "odd")


def main():
    mp.mp.dps = 60
    ref = mp.mpf(T1_REF_STR)
    print("Mayer bridge: t_1 as a zero of det(1 + L_s) on Re(s)=1/2\n")
    print(f"  {'N':>4s} {'dps':>5s} {'t_1 (real part)':>34s} {'|Im r|':>10s} {'secs':>7s}")

    rows = []
    for N, dps, Ne in [(24, 40, 100), (32, 55, 100), (40, 70, 110), (52, 85, 120)]:
        t = time.time()
        root = solve_t1(N, dps, Ne)
        el = time.time() - t
        re, im = mp.re(root), mp.im(root)
        rows.append({"N": N, "dps": dps, "t1": mp.nstr(re, 30), "abs_im": mp.nstr(abs(im), 5),
                     "secs": round(el, 1)})
        print(f"  {N:4d} {dps:5d} {mp.nstr(re, 26):>34s} {mp.nstr(abs(im), 3):>10s} {el:7.1f}")

    # --- N-ladder self-consistency: the primary accuracy certificate -------------------
    print("\n  N-ladder self-consistency (successive pairs):")
    ladder = []
    for i in range(len(rows) - 1):
        a, b = mp.mpf(rows[i]["t1"]), mp.mpf(rows[i + 1]["t1"])
        d = float(-mp.log10(abs(a - b) / abs(b)))
        ladder.append({"pair": f"N={rows[i]['N']} vs N={rows[i+1]['N']}", "digits": d})
        print(f"    N={rows[i]['N']:3d} vs N={rows[i+1]['N']:3d}:  agree to {d:5.1f} digits")

    best = mp.mpf(rows[-1]["t1"])
    dref = float(-mp.log10(abs(best - ref) / abs(ref)))
    im_ok = abs(mp.mpf(rows[-1]["abs_im"])) < mp.mpf("1e-15")

    print(f"\n  best t_1 = {mp.nstr(best, 28)}")
    print(f"  reference = {T1_REF_STR}  (Booker LuCaNT 2023 / LMFDB)")
    print(f"  -> agrees with reference to {dref:.1f} digits")
    print(f"  -> |Im r| < 1e-15 (critical line, NOT imposed): {im_ok}")
    print(f"  -> sessionK/mayer_run1.py had 9.5354 vs 9.5337, i.e. ~3.7 digits")

    # --- EVEN sector cross-check: the OTHER Mayer factor must find the even eigenvalues ----
    # Guards against the odd-sector match being an accident of one determinant branch.
    #
    # An N-LADDER, not a single shot. The first version of this check ran only N=32 and
    # reported 13.77975135189073894979391909... -- but that value is converged to only ~18
    # digits; its trailing "...979391..." was SOLVER NOISE. The v3 handoff §4 flagged exactly
    # this ("precision was spent on t_1"), and it was right. The ladder below converges it:
    # N=52 and N=64 agree to 32.4 digits at 13.77975135189073894424367328151771, whose tail
    # "...424367..." is the real continuation. Lesson identical to the calibrator audit -- a
    # value is only trustworthy to the precision an N-LADDER (not one run) certifies.
    print("\n  even-sector cross-check via det(1 - L) = 0, N-ladder:")
    ev_rows = []
    for N, dps, Ne in [(40, 70, 110), (52, 85, 120), (64, 100, 130)]:
        ev = solve_root(N, dps, Ne, "13.7797513", parity="even")
        ev_rows.append((N, mp.re(ev), abs(mp.im(ev))))
        print(f"    N={N:3d}: {mp.nstr(mp.re(ev), 30)}  |Im r| = {mp.nstr(abs(mp.im(ev)), 3)}")
    ev_re, ev_im = ev_rows[-1][1], ev_rows[-1][2]
    ev_ladder = float(-mp.log10(abs(ev_rows[-2][1] - ev_re) / abs(ev_re)))
    ev_d = float(-mp.log10(abs(ev_re - mp.mpf("13.77975135")) / mp.mpf("13.78")))
    print(f"    -> converged to {ev_ladder:.1f} digits (N=52 vs 64); matches LMFDB 10-digit "
          f"display to {ev_d:.1f} digits; |Im r| = {mp.nstr(ev_im, 3)} (not imposed)")

    out = {"even_check": {"value": mp.nstr(ev_re, 34), "lmfdb": "13.77975135",
                          "ladder_digits": ev_ladder, "digits_vs_lmfdb": ev_d,
                          "abs_im": mp.nstr(ev_im, 5)},
           "rows": rows, "ladder": ladder, "reference": T1_REF_STR,
           "best": mp.nstr(best, 30), "digits_vs_reference": dref,
           "im_below_1e15": bool(im_ok),
           "prior_float64_value": 9.5354,
           "PASS": bool(dref > 15 and im_ok)}
    print(f"\n  PASS: {out['PASS']}")
    p = os.path.join(HERE, "maass_t1_measured.json")
    json.dump(out, open(p, "w"), indent=2, default=str)
    print("wrote", p)


if __name__ == "__main__":
    main()
