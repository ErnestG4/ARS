"""Arc-level verdict resolution (rulings-as-code) — COMMITTED GENERATOR of
holonomy/arc_verdicts.json.  All inputs are measured JSONs + the seal; all
cell logic is lattice_h.resolve_pair; the sealed powered rule for dialed
pairs: powered iff |prediction at (dial-top, largest scale)| >= k * SEM
there (the law must be resolvable where it is largest)."""

import hashlib
import json
import sys

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

from lattice_h import resolve_pair                                     # noqa: E402

SEAL = json.load(open(f"{ROOT}/holonomy/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/holonomy/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f} — dated addendum required"


def main():
    p1 = json.load(open(f"{ROOT}/holonomy/p1_measured.json"))
    p2 = json.load(open(f"{ROOT}/holonomy/p2_measured.json"))
    p3 = json.load(open(f"{ROOT}/holonomy/p3_measured.json"))
    pred1 = json.load(open(f"{ROOT}/holonomy/p1_prediction.json"))
    pred2 = json.load(open(f"{ROOT}/holonomy/p2_prediction.json"))
    census = json.load(open(f"{ROOT}/holonomy/ownership_map.json"))["census"]
    out = {}

    # P1 — dialed; census both-orders TRUE (C1/C2)
    top_dial = SEAL["p1"]["dials"][-1]
    top_L = SEAL["p1"]["L_fracs"][-1] * SEAL["p1"]["n_W"]
    # powered where the law is largest: max |pred| cell vs its SEM
    best = max(((abs(pred1["prediction"][f"dial{d}"][f"L{f * SEAL['p1']['n_W']:.1f}"]
                     ["delta_pred"]),
                 d, f) for d in SEAL["p1"]["dials"]
                for f in SEAL["p1"]["L_fracs"]))
    cell = p1["synth"][f"dial{best[1]}"]["cells"][
        f"L{best[2] * SEAL['p1']['n_W']:.1f}"]
    p1_powered = bool(best[0] >= SEAL["k_arc"] * cell["sem"])
    # sealed P1 materiality rule (zeta NNS consumer)
    ks = p1["zeta"]["nns_ks"]
    same_class = ks["A"]["best"] == ks["B"]["best"]
    gaps = sorted(v for k, v in ks["A"].items() if k != "best")
    gap = gaps[1] - gaps[0]
    dks = abs(ks["A"]["gue"] - ks["B"]["gue"])
    p1_mat = bool(same_class and dks < SEAL["p1_materiality_frac"] * gap)
    out["P1"] = dict(
        verdict=resolve_pair(kind="dialed", both_orders_live=True,
                             materiality_clean=p1_mat,
                             fp_all_within_tol=False,
                             law_agrees=p1["law"]["law_agrees"],
                             powered=p1_powered),
        law=p1["law"], control=p1["control"], zeta=p1["zeta"],
        materiality=dict(same_class=same_class, class_gap=float(gap),
                         delta_ks_gue=float(dks), clean=p1_mat),
        census_row=census[0]["finding"])

    # P2 — dialed; single order; materiality STRUCTURAL (census C3: no live
    # lambda-hat estimation caller — the mechanism cannot touch banked rows)
    topG = f"G{SEAL['p2']['ladder'][-1]:.3f}"
    topr = f"r{SEAL['p2']['r_list'][-1]}"
    p2_powered = bool(abs(pred2["prediction"][topG][topr]["delta_pred"])
                      >= SEAL["k_arc"] * p2["ladder"][topG][topr]["sem"])
    out["P2"] = dict(
        verdict=resolve_pair(kind="dialed", both_orders_live=False,
                             materiality_clean=True,
                             fp_all_within_tol=False,
                             law_agrees=p2["law"]["law_agrees"],
                             powered=p2_powered),
        law=p2["law"], ruling_input=p2["ruling_input"],
        materiality="STRUCTURAL_CLEAN (census C3)",
        census_row=census[1]["finding"])

    # P3 — resolved inside run_p3 (stochastic point-check)
    out["P3"] = dict(verdict=p3["verdict"], cells=p3["cells"],
                     dcount=p3["dcount"], materiality=p3["materiality"],
                     census_row=census[2]["finding"])

    try:
        opt = json.load(open(f"{ROOT}/holonomy/opt_measured.json"))
        out["optional"] = opt
    except OSError:
        pass
    json.dump(out, open(f"{ROOT}/holonomy/arc_verdicts.json", "w"), indent=1)
    for pair in ("P1", "P2", "P3"):
        v = out[pair]["verdict"]
        print(f"{pair}: {v['primary']} (measurement={v['measurement']}, "
              f"flags={v['flags']})")


if __name__ == "__main__":
    main()
