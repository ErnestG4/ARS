"""Is the long-double phase path genuinely taken? (Will, 2026-10-10.) Reports np.longdouble's epsilon on this machine
(80-bit x87: ~1.08e-19; a silent fallback to double: 2.2e-16) and compares p^{e} from cs4fast.pexp (long-double phase)
and from the v1 double code, np.exp(e·log p), against mpmath at 40 digits, for Im(e)·log p up to ~1e5 rad.
Pass: epsilon < 1e-18 and pexp's worst relative error ≤ 1e-14 (the double code's is expected ~1e-12–1e-11).

  python check_longdouble.py
"""
import json
import platform

import mpmath as mp
import numpy as np

import cs4fast as F
import zeta_em as ZE

mp.mp.dps = 40


def main():
    eps = float(np.finfo(np.longdouble).eps)
    rng = np.random.default_rng(5)
    p = np.array([2.0, 97.0, 9973.0, 99991.0])
    lp_ld = np.log(p.astype(np.longdouble))[None, :]       # as cs4fast now builds it (v2 cast a double log up: no gain)
    lp = lp_ld.astype(float)
    e = (rng.uniform(-1, 1, 6) + 1j * rng.uniform(-8000, 8000, 6))[:, None]
    new = F.pexp(e, lp, lp_ld)
    old = np.exp(e * lp)
    zn = ZE.cpow_neg(-e[:, 0], lp_ld[0])                   # exp(+e·log p) through zeta_em's path
    worst = {"pexp": 0.0, "double_v1": 0.0, "zeta_em_cpow": 0.0}
    for i in range(e.shape[0]):
        for j in range(len(p)):
            ref = mp.exp(mp.mpc(e[i, 0].real, e[i, 0].imag) * mp.log(int(p[j])))
            for key, val in (("pexp", new[i, j]), ("double_v1", old[i, j]), ("zeta_em_cpow", zn[i, j])):
                worst[key] = max(worst[key], float(abs(val - complex(ref)) / abs(ref)))
    res = dict(machine=platform.node(), longdouble_eps=eps, max_phase_rad=float(np.max(np.abs(e.imag * lp))),
               worst_rel=worst, PASS=bool(eps < 1e-18 and worst["pexp"] <= 1e-14 and worst["zeta_em_cpow"] <= 1e-14))
    print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    main()
