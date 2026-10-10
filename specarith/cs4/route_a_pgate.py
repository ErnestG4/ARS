"""Route (a), U(N) spacing-law gate (Will, overnight queue item 2; after G-a(ii)): the nearest-neighbour spacing density
p₄(s) = d²E₄/ds² from the transcribed n ≤ 4 correlations (CS08 U(N), through gate_a2's integration), against the exact
CUE_N spacing density (ph2lib.spacing_tables(N=N): Fredholm determinant, Chebyshev second derivative, Phase 2's
G0b-verified tables), on s ∈ [0, 2] (the sealed window of SCOPE_CS_SPACING §1).

E₄ at M + 1 = 25 Chebyshev–Lobatto nodes on [0, 2], differentiated as ph2lib does. Pass criteria on a 201-point grid:
  N = 4 (series terminates): |p₄ − p_N| ≤ 1e-6 (Chebyshev differentiation error);
  N = 10, 50: |p₄ − p_N| ≤ 1.5·|d²S₅/ds²| + 1e-6, S₅ = (1/5!)∫ρ₅ from the determinant at the same nodes (first omitted
  term of the inclusion–exclusion series).

  python route_a_pgate.py [PROCS]  ->  results/route_a_pgate.json
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

import gate_a2 as G2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import ph2lib  # noqa: E402

S_MAX, M = 2.0, 24
NODES = 0.5 * S_MAX * (1 - np.cos(np.pi * np.arange(M + 1) / M))
NS = (4, 10, 50)


def E4_at(job):
    N, s = job
    if s == 0:
        return N, s, 1.0, 0.0
    Sn = {n: G2.S_n_transcribed(N, n, s, 10) for n in (2, 3, 4)}
    E4 = 1 - s + Sn[2] - Sn[3] + Sn[4]
    S5 = G2.S_n_det(N, 5, s) if N >= 5 else 0.0
    print(N, round(s, 4), E4, S5, flush=True)
    return N, s, E4, S5


def main(procs=12):
    with Pool(procs) as p:
        res = p.map(E4_at, [(N, s) for N in NS for s in NODES], chunksize=1)
    grid = np.linspace(0, S_MAX, 201)
    out = dict(rows={})
    for N in NS:
        E4 = np.array([r[2] for r in res if r[0] == N])
        S5 = np.array([r[3] for r in res if r[0] == N])
        p4 = ph2lib.cheb_second_derivative(E4, NODES, S_MAX)[0](grid)
        s5pp = ph2lib.cheb_second_derivative(S5, NODES, S_MAX)[0](grid)
        pN = ph2lib.spacing_tables(S=6.0, M=160, m=40, abars=(), N=N)[0](grid)
        lim = (1e-6 if N <= 4 else 1.5 * np.abs(s5pp) + 1e-6)
        diff = p4 - pN
        out["rows"][str(N)] = dict(max_abs_diff=float(np.max(np.abs(diff))), max_ratio_to_limit=float(np.max(np.abs(diff) / lim)),
                                   PASS=bool(np.all(np.abs(diff) <= lim)), E4_nodes=E4.tolist(), S5_nodes=S5.tolist(),
                                   p4=p4.tolist(), pN=pN.tolist())
        print(f"N={N}: max |p4 − p_N| = {out['rows'][str(N)]['max_abs_diff']:.2e}, max ratio to limit "
              f"{out['rows'][str(N)]['max_ratio_to_limit']:.3f}  {'PASS' if out['rows'][str(N)]['PASS'] else 'FAIL'}", flush=True)
    out["PASS"] = all(v["PASS"] for v in out["rows"].values())
    out["grid"] = grid.tolist()
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "route_a_pgate.json"), "w"), indent=1)
    print("route (a) U(N) spacing-law gate", "PASS" if out["PASS"] else "FAIL")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 12)
