"""Gates on the corrected (B)'s F6 prediction before it is tagged (round 58; followup_gates.py's, for one observable).
Data-free. Committed before `b2_pred.py merge` is run.

  G1 TAGGABLE: b2_pred's own flag (Δκ₃(L*) ≠ 0 at every F6 height).
  G2 cutoff convergence (prime cutoff 3·10⁵ → 10⁶ at every file): the pooled δμ_cutoff (Σ w_f δμ_cutoff,f) is
     ≤ CUTOFF_FRAC × the band at F3 geometry, 2·SE_pool(L*) from the L rule (results/b2_rule.json; μ units, slope 1).
  G3 the other precision checks (quadrature, file average) are inside δμ_sys and reported, not gated.
  G4 cross-machine check (TOL = 1e-12 absolute): b2_pred jobs computed on spot are recomputed on another machine with the
     same code; every stored quantity must agree to ≤ TOL.
  G5 selftests: b2_read.py selftest (with the G1b red path) exits 0.
The prediction is taggable only if G1, G2, G4 and G5 all hold. Anything else goes to Will.

  python b2_gates.py recompute PRED_DIR N OUT.jsonl
  python b2_gates.py gate RECOMP.jsonl [...] --selftest READ_EXIT        → results/b2_gates.json
"""
import json
import os
import socket
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b2_pred as BP  # noqa: E402

TOL = 1e-12
CUTOFF_FRAC = 0.01
NUM = ("F2_sine", "F3_sine", "dF2", "dF3")


def spot_rows(d):
    out = []
    for fn in sorted(os.listdir(d)):
        if fn.startswith("b2pred_c") and fn.endswith(".jsonl"):
            out += [json.loads(x) for x in open(os.path.join(d, fn)) if x.strip()]
    return out


def recompute(pred_dir, n, out):
    sel = sorted(spot_rows(pred_dir), key=lambda r: (r["pmax"], r["file"], r["which"], r["m"]))
    pick = [sel[i] for i in np.unique(np.linspace(0, len(sel) - 1, n).round().astype(int))] if sel else []
    host = socket.gethostname()
    for r in pick:
        t = time.time()
        x = BP.run_one(BP.key(r))
        x.update(host=host, t_sec=round(time.time() - t, 1))
        with open(out, "a") as fh:
            fh.write(json.dumps(x) + "\n")
        print(BP.key(r), f"{x['t_sec']} s", flush=True)


def gate(recs, selftest):
    R = json.load(open(os.path.join(HERE, "results", "b2_pred.json")))
    rule = json.load(open(os.path.join(HERE, "results", "b2_rule.json")))
    L = BP.L_star()
    band = 2 * rule["L"][str(L)]["SE_pool"]
    w = R["weights"]
    cut = float(sum(w[f] * R["files"][f]["dmu"]["cutoff"] for f in R["files"]))
    out = dict(round=58, L_star=L, tol=TOL, cutoff_frac=CUTOFF_FRAC, band_F3=band,
               G1_taggable=bool(R["TAGGABLE"]), dmu_cutoff_pool=cut, G2_limit=CUTOFF_FRAC * band,
               G2_cutoff=bool(cut <= CUTOFF_FRAC * band), delta_mu_sys=R["delta_mu_sys"],
               dmu_by_file={f: v["dmu"] for f, v in R["files"].items()})
    ref = {BP.key(r): r for r in spot_rows(os.path.join(HERE, "results", "b2_pred"))}
    worst, n, by = 0.0, 0, {}
    for p in recs:
        for x in map(json.loads, open(p)):
            d = max(abs(x[q] - ref[BP.key(x)][q]) for q in NUM)
            worst, n = max(worst, d), n + 1
            h = by.setdefault(x["host"], dict(n=0, worst=0.0))
            h["n"] += 1
            h["worst"] = max(h["worst"], d)
    out["G4_xcheck"] = dict(n=n, worst=worst, by_host=by, PASS=bool(n > 0 and worst <= TOL))
    st = open(selftest).read().strip()
    out["G5_selftest"] = dict(exit=st, PASS=st == "exit=0")
    out["all_pass"] = bool(out["G1_taggable"] and out["G2_cutoff"] and out["G4_xcheck"]["PASS"] and out["G5_selftest"]["PASS"])
    json.dump(out, open(os.path.join(HERE, "results", "b2_gates.json"), "w"), indent=1)
    print(f"G1 TAGGABLE flag {out['G1_taggable']}; G2 pooled δμ_cutoff {cut:.2e} ≤ {out['G2_limit']:.2e}: "
          f"{out['G2_cutoff']}; δμ_sys {out['delta_mu_sys']:.2e}")
    print(f"G4 cross-machine: {n} jobs, worst {worst:.1e} (≤ {TOL}): {out['G4_xcheck']['PASS']} {by}")
    print(f"G5 selftest: {st} → {out['G5_selftest']['PASS']}")
    print(f"taggable: {out['all_pass']}")
    return out


if __name__ == "__main__":
    if sys.argv[1] == "recompute":
        recompute(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "gate":
        a = sys.argv[2:]
        i = a.index("--selftest")
        gate(a[:i], a[i + 1])
