"""DESCRIPTIVE ONLY (Will, eleventh round, decision (iii)): on the seen Phase 2 bins, compare the observed κ̂ (both arms)
with the κ* the estimator would return if the zeros followed the EXACT CUE law at N = N_eff (all orders in 1/N; the BFM
kernel at real N, A4). No verdict, no seal: the fact recorded is the direction of the zeros' deviation relative to
CUE's own higher-order terms. Writes results/run/CUE_EXACT_COMPARE.md."""
import json
import os

import numpy as np

import ph2lib as P
import preread as R

RUN = os.path.join(R.RES, "run")


def main():
    Mp, Ms = P.Model(), P.Model(abar_grid=P.SECONDARY_ABAR_GRID)
    Wp, Ws = P.WindowFit(Mp), P.WindowFit(Ms)
    md = ["# Observed κ̂ vs the exact CUE(N_eff) law — DESCRIPTIVE ONLY (seen bins; no verdict)", "",
          "κ*_CUE = what each arm's estimator returns when p(s) is the exact CUE_N law at N = the bin's median N_eff "
          "(all orders in 1/N). κ = 1 is the arm's own model. Sign column: whether the zeros sit on the same side of 1 "
          "as exact CUE(N_eff).", "",
          "| bin | N_eff | arm | κ*_CUE (exact CUE at N_eff) | κ̂ (zeros) | κ*_CUE − 1 | κ̂ − 1 | same side of 1? |",
          "|---|---|---|---|---|---|---|---|"]
    rows = []
    for b in ["A", "B", "P1", "P2", "P3", "P4", "P5", "P6"]:
        o = json.load(open(os.path.join(RUN, f"{b}.json")))
        N = o["N_eff_median"]
        ab = R.abar_of_L(N * R.NEFF_DEN)
        pN, _, _ = P.spacing_tables(S=P.S_C + 0.05, N=N, abars=())
        for arm, W, abar in (("prim", Wp, None), ("sec", Ws, ab)):
            ks = P.kappa_from_c(W.expected_c(pN, N, abar=abar))
            kh = o[arm]["kappa"]
            same = (ks - 1) * (kh - 1) > 0
            rows.append(dict(bin=b, N_eff=N, arm=arm, kappa_cue_exact=ks, kappa_hat=kh, same_side=bool(same)))
            md.append(f"| {b} | {N:.3f} | {'PRIMARY' if arm == 'prim' else 'SECONDARY'} | {ks:.4f} | {kh:.4f} |"
                      f" {ks - 1:+.4f} | {kh - 1:+.4f} | {'yes' if same else '**no**'} |")
            print(md[-1], flush=True)
    json.dump(rows, open(os.path.join(RUN, "cue_exact_compare.json"), "w"), indent=1)
    open(os.path.join(RUN, "CUE_EXACT_COMPARE.md"), "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
