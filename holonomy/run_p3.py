"""P3 measurement: weight->thin vs thin->weight on the D1 KAG randoms.
COMMITTED GENERATOR of holonomy/p3_measured.json.  Post-seal; A1 u-draw
ensemble; A3 sign check on retained counts; tripwire 7 (no survey/ writes,
null_half read-only reference).  Verdict via lattice_h.resolve_pair.
"""

import hashlib
import json
import sys

import numpy as np
from scipy.stats import norm

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

from transitions import thin_pre                                      # noqa: E402
from lattice_h import resolve_pair                                    # noqa: E402

SEAL = json.load(open(f"{ROOT}/holonomy/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/holonomy/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f} — dated addendum required"

P3 = SEAL["p3"]
K = SEAL["k_arc"]


def main():
    import time
    t0 = time.time()
    from p3_common import load_all, prep_null_tiles, pooled_F
    print("[P3] loading survey objects (read-only)...", flush=True)
    scal, kag, nulls, tiles = load_all()
    ntiles = prep_null_tiles(nulls, tiles)
    del nulls
    p_wt = scal["W_data"] / scal["W_kag"]
    p_tw = scal["N_data"] / scal["N_kag"]
    assert int(np.sign(p_wt - p_tw)) == P3["sign_predicted"], \
        "sealed scalars drifted from KAG-time values"
    L_LIST = P3["L_list"]
    dF = {L: [] for L in L_LIST}
    dcount, sign_ok_all = [], True
    for dr in range(P3["n_draws"]):
        u = np.random.default_rng(P3["u_seed0"] + dr).uniform(
            size=scal["N_kag"])
        thin_A = thin_pre(kag, p_wt, u)      # weight -> thin (frozen sem.)
        thin_B = thin_pre(kag, p_tw, u)      # thin -> weight (count norm.)
        nA, nB = len(thin_A["w"]), len(thin_B["w"])
        dcount.append(nA - nB)
        if np.sign(nA - nB) != P3["sign_predicted"] and nA != nB:
            sign_ok_all = False
        FA, _ = pooled_F(thin_A, ntiles, tiles, L_LIST)
        FB, nt = pooled_F(thin_B, ntiles, tiles, L_LIST)
        for L in L_LIST:
            dF[L].append(FA[L] - FB[L])
        print(f"  draw {dr}: dcount={nA - nB:+d} " + " ".join(
            f"dF({L})={dF[L][-1]:+.5f}" for L in L_LIST), flush=True)

    zf = float(norm.isf(2.0 * norm.sf(K) / (2.0 * len(L_LIST))))
    cells, zmax = {}, 0.0
    for L in L_LIST:
        d = np.array(dF[L])
        sem = float(d.std(ddof=1) / np.sqrt(len(d)))
        z = float(d.mean() / sem)
        zmax = max(zmax, abs(z))
        cells[f"L{L}"] = dict(mean=float(d.mean()), sem=sem, z=z)
    mean_within = bool(zmax <= zf)
    # powered? sealed MDD in F units at the family-wise threshold
    mdd = max(zf * cells[f"L{L}"]["sem"] for L in L_LIST)
    powered = bool(mdd <= P3["mdd_F"])
    # materiality: worst |dF| bound vs the survey slices' margin to Z_CLASS
    d3 = json.load(open(f"{ROOT}/survey/d3_measured.json"))
    z_class = json.load(open(f"{ROOT}/survey/prereg_sealed.json"))[
        "lattice"]["Z_CLASS"]
    margins = []
    for srow in d3["slices"].values():
        for t in srow["tiles"].values():
            for fr in t["F"]:
                if fr["L"] in L_LIST:
                    margins.append((fr["F"] - 1.0) / fr["sigma"] - z_class)
    margin_min_sigma = float(min(margins))
    worst_bound = max(abs(cells[f"L{L}"]["mean"]) + K * cells[f"L{L}"]["sem"]
                      for L in L_LIST)
    med_sigF = float(np.median([fr["sigma"] for srow in d3["slices"].values()
                                for t in srow["tiles"].values()
                                for fr in t["F"] if fr["L"] in L_LIST]))
    mat_clean = bool(worst_bound / med_sigF < margin_min_sigma)
    verdict = resolve_pair(kind="stochastic_point", both_orders_live=False,
                           materiality_clean=mat_clean, powered=powered,
                           mean_within_ksem=mean_within,
                           sign_ok=bool(sign_ok_all))
    out = dict(seal_cited="holonomy/prereg_sealed.json", scalars=scal,
               p_wt=float(p_wt), p_tw=float(p_tw),
               dcount=dict(mean=float(np.mean(dcount)),
                           sd=float(np.std(dcount, ddof=1)),
                           sign_predicted=P3["sign_predicted"],
                           sign_ok_all_draws=bool(sign_ok_all)),
               cells=cells, z_fam=zf, mean_within_ksem=mean_within,
               mdd_F=dict(achieved=float(mdd), sealed=P3["mdd_F"],
                          powered=powered),
               materiality=dict(margin_min_sigma=margin_min_sigma,
                                worst_dF_bound=float(worst_bound),
                                med_sigma_F=med_sigF, clean=mat_clean),
               n_tiles_per_L={str(L): nt[L] for L in L_LIST},
               verdict=verdict)
    out["elapsed_sec"] = float(time.time() - t0)
    json.dump(out, open(f"{ROOT}/holonomy/p3_measured.json", "w"), indent=1)
    print(f"P3: verdict={verdict['primary']} (meas={verdict['measurement']}, "
          f"flags={verdict['flags']}) max|z|={zmax:.2f} vs z_fam={zf:.2f}; "
          f"dcount mean={np.mean(dcount):+.0f} sign_ok={sign_ok_all}; "
          f"powered={powered} materiality_clean={mat_clean}")


if __name__ == "__main__":
    main()
