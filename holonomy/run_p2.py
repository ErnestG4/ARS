"""P2 measurement: reweight->edge vs edge->reweight.  COMMITTED GENERATOR
of holonomy/p2_measured.json.  Post-seal; thresholds from prereg; verdicts
via lattice_h only.  Law vs the sealed continuum prediction (family-wise z);
correctness leg vs K_true = pi r^2 (exact for inhomogeneous Poisson)."""

import hashlib
import json
import sys

import numpy as np
from scipy.stats import norm

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

from transitions import sample_inhom_poisson, p2_apply, k_inhom_marks   # noqa: E402

SEAL = json.load(open(f"{ROOT}/holonomy/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/holonomy/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f} — dated addendum required"

P2 = SEAL["p2"]
K = SEAL["k_arc"]
PRED = json.load(open(f"{ROOT}/holonomy/p2_prediction.json"))


def main():
    import time
    t0 = time.time()
    out = dict(seal_cited="holonomy/prereg_sealed.json", ladder={})
    zs = []
    for G in P2["ladder"]:
        beta = np.log(G) / P2["Lx"]
        dd = {r: [] for r in P2["r_list"]}
        bias = {r: {"A": [], "B": []} for r in P2["r_list"]}
        for s in range(SEAL["p2_seeds"]):
            pts, _ = sample_inhom_poisson(seed=400 + s, beta=beta,
                                          n_target=P2["n_target"])
            dom = (0.0, P2["Lx"], 0.0, P2["Ly"])
            KA = KB = None
            for order, tag in (("reweight_then_edge", "A"),
                               ("edge_then_reweight", "B")):
                pe, marks, d2 = p2_apply(pts, dom, order, rmax=P2["rmax"])
                Kv = k_inhom_marks(pe, marks, d2, P2["r_list"])
                for r in P2["r_list"]:
                    bias[r][tag].append(abs(Kv[r] - np.pi * r * r))
                if tag == "A":
                    KA = Kv
                else:
                    KB = Kv
            for r in P2["r_list"]:
                dd[r].append(KA[r] - KB[r])
        row = {}
        for r in P2["r_list"]:
            d = np.array(dd[r])
            sem = float(d.std(ddof=1) / np.sqrt(len(d)))
            pred = PRED["prediction"][f"G{G:.3f}"][f"r{r}"]["delta_pred"]
            z = (d.mean() - pred) / sem
            zs.append(abs(z))
            row[f"r{r}"] = dict(mean=float(d.mean()), sem=sem, pred=pred,
                                z=float(z),
                                bias_A=float(np.mean(bias[r]["A"])),
                                bias_B=float(np.mean(bias[r]["B"])))
            print(f"  G={G:.3f} r={r}: dK={d.mean():+.5f}±{sem:.5f} "
                  f"pred={pred:+.5f} z={z:+.2f}", flush=True)
        out["ladder"][f"G{G:.3f}"] = row
    n_cells = len(P2["ladder"]) * len(P2["r_list"])
    zf = float(norm.isf(2.0 * norm.sf(K) / (2.0 * n_cells)))
    out["law"] = dict(z_fam=zf, max_abs_z=float(max(zs)),
                      law_agrees=bool(max(zs) <= zf))
    # ruling input: bias separation at ladder top (leg witnessed two-sided)
    top = out["ladder"][f"G{P2['ladder'][-1]:.3f}"]
    out["ruling_input"] = dict(
        bias_A_top=[top[f"r{r}"]["bias_A"] for r in P2["r_list"]],
        bias_B_top=[top[f"r{r}"]["bias_B"] for r in P2["r_list"]])
    out["elapsed_sec"] = float(time.time() - t0)
    json.dump(out, open(f"{ROOT}/holonomy/p2_measured.json", "w"), indent=1)
    print(f"P2: law_agrees={out['law']['law_agrees']} "
          f"(max|z|={max(zs):.2f} vs z_fam={zf:.2f})")


if __name__ == "__main__":
    main()
