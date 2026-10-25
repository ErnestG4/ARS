"""Round 84 known answer: U(N) node convergence of the (3, 3) piece ∫_{A³×B³}(ρ₆ − ρ₃ρ₃) at r = 100, N = 10⁵, with the
distinct-node rule used by G-b3, the averaging test, the settling test and the node diagnostic (n6b_extract._tuples:
distinct sorted tuples × 3!; valid because the integrand vanishes at in-cluster coincidence), on exact determinants.

  python n6b_unode.py OUT_JSON
"""
import json
import sys

import numpy as np

import n6b_extract as E

N, R, NQS = 100_000, 100.0, (4, 6, 8, 10, 12, 16)


def main(out):
    rows = []
    for nq in NQS:
        XA, WA = E._tuples(nq, 3)
        PA, PB = np.repeat(XA, len(XA), 0), np.tile(XA, (len(XA), 1))
        W = np.repeat(WA, len(XA)) * np.tile(WA, len(XA))
        v = E._det_rho(np.concatenate([PA, PB + R], 1), N) - E._det_rho(PA, N) * E._det_rho(PB + R, N)
        rows.append(dict(nq=nq, configs=len(W), value=float(np.sum(W * v))))
        print(nq, len(W), f"{rows[-1]['value']:.10e}", flush=True)
    ref = rows[-1]["value"]
    for x in rows:
        x["rel_err_vs_16"] = abs(x["value"] / ref - 1)
    json.dump(dict(label="round 84 U(N) node convergence, (3,3) piece at r = 100 (known answer)", N=N, r=R, rows=rows),
              open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
