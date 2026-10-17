"""Gates on the two replications' predictions before they are tagged (round 52; mirrors route (a)'s pre-tag checks).
Data-free. Run after `followup_pred.py merge`.

Declared before the merged values are seen:
  G1 TAGGABLE: followup_pred's own flag ((A): the μ = 1 density positive on the fitted bins at every F4 height and the
     re-measured ∂μ*/∂μ within 1e-3 of 1; (B): Δκ₃ ≠ 0 at every F5 height).
  G2 cutoff convergence (prime cutoff 3·10⁵ → 10⁶ at every node and height): the pooled δμ_cutoff (Σ w_f δμ_cutoff,f)
     is ≤ CUTOFF_FRAC × the observable's band at F3 geometry (2·SE_pool from the round-50 window runs: (A) at S_A = 1.6,
     followup_window_A.json; (B) at L = 3, followup_window_B.json, divided by the CUE_N slope), the same 1% scale as
     the S_A rule (rules §3). Reported beside it: the largest relative change of Δp⁽²⁾ / Δκ₃.
  G3 the other precision checks are inside δμ_sys and reported, not gated (quadrature, T₅ bracket, n = 6 bound, file
     average, half-grid interpolation), as route (a).
  G4 cross-machine check (route (a)'s xcheck, TOL = 1e-12 absolute): jobs computed on spot are recomputed on another
     machine with the same code; every stored quantity must agree to ≤ TOL.
  G5 selftests: followup_fit.py selftest and followup_read.py selftest exit 0 (their logs are recorded by the run).
The predictions are taggable only if G1, G2, G4 and G5 all hold. Anything else goes to Will.

  python followup_gates.py recompute PRED_DIR KIND N OUT.jsonl     KIND = A3 (T₃ jobs), A4 (T₄ at s ≤ 0.6), B (κ₃)
  python followup_gates.py gate RECOMP.jsonl [...]  [--selftests FIT_EXIT READ_EXIT]   → results/followup_gates.json
"""
import json
import os
import socket
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import followup_pred as P  # noqa: E402

TOL = 1e-12
CUTOFF_FRAC = 0.01
NUM = ("T_sine", "dT", "F2_sine", "F3_sine", "dF2", "dF3")


def spot_rows(d):
    out = []
    for fn in sorted(os.listdir(d)):
        if fn.startswith("pred_c") and fn.endswith(".jsonl"):
            out += [json.loads(x) for x in open(os.path.join(d, fn)) if x.strip()]
    return out


def recompute(pred_dir, kind, n, out):
    rows = spot_rows(pred_dir)
    if kind == "A3":
        sel = [r for r in rows if r["obs"] == "A" and r["part"] == "T3"]
    elif kind == "A4":
        sel = [r for r in rows if r["obs"] == "A" and r["part"] == "T4" and r["s"] <= 0.6]
    else:
        sel = [r for r in rows if r["obs"] == "B"]
    sel = sorted(sel, key=lambda r: (r["pmax"], r["file"], r["which"], r["m"], r["s"]))
    pick = [sel[i] for i in np.unique(np.linspace(0, len(sel) - 1, n).round().astype(int))] if sel else []
    host = socket.gethostname()
    for r in pick:
        t = time.time()
        job = (r["obs"], r["file"], r["which"], r["pmax"], r["m"], r["part"], r["s"])
        x = P.run_one(job)
        x.update(host=host, t_sec=round(time.time() - t, 1))
        with open(out, "a") as fh:
            fh.write(json.dumps(x) + "\n")
        print(job, f"{x['t_sec']} s", flush=True)


def gate(recs, selftests=None):
    A = json.load(open(os.path.join(HERE, "results", "followup_pred_A.json")))
    B = json.load(open(os.path.join(HERE, "results", "followup_pred_B.json")))
    wa = json.load(open(os.path.join(HERE, "results", "followup_window_A.json")))
    wb = json.load(open(os.path.join(HERE, "results", "followup_window_B.json")))
    band = {"A": wa["windows"][f"{P.S_A:.1f}"]["band"],
            "B": 2 * wb["windows"][str(P.L_B)]["se_pool_raw"] / wb["windows"][str(P.L_B)]["cuen_slope"]}
    out = dict(round=52, tol=TOL, cutoff_frac=CUTOFF_FRAC, band_F3=band)
    for o, R in (("A", A), ("B", B)):
        w = R["weights"]
        cut = float(sum(w[f] * R["files"][f]["dmu"]["cutoff"] for f in R["files"]))
        out[o] = dict(G1_taggable=bool(R["TAGGABLE"]), dmu_cutoff_pool=cut, G2_limit=CUTOFF_FRAC * band[o],
                      G2_cutoff=bool(cut <= CUTOFF_FRAC * band[o]), delta_mu_sys=R["delta_mu_sys"],
                      dmu_by_file={f: v["dmu"] for f, v in R["files"].items()})
    # G4
    ref = {}
    for r in spot_rows(os.path.join(HERE, "results", "followup_pred")):
        ref[(r["obs"], r["file"], r["which"], r["pmax"], r["m"], r["part"], r["s"])] = r
    worst, n, by = 0.0, 0, {}
    for p in recs:
        for x in map(json.loads, open(p)):
            k = (x["obs"], x["file"], x["which"], x["pmax"], x["m"], x["part"], x["s"])
            d = max(abs(x[q] - ref[k][q]) for q in NUM if q in x)
            worst, n = max(worst, d), n + 1
            h = by.setdefault(x["host"], dict(n=0, worst=0.0))
            h["n"] += 1
            h["worst"] = max(h["worst"], d)
    out["G4_xcheck"] = dict(n=n, worst=worst, by_host=by, PASS=bool(n > 0 and worst <= TOL))
    st = None
    if selftests:
        st = {p: open(p).read().strip() for p in selftests}
    out["G5_selftests"] = dict(exits=st, PASS=bool(st and all(v == "exit=0" for v in st.values())))
    out["TAGGABLE"] = {o: bool(out[o]["G1_taggable"] and out[o]["G2_cutoff"] and out["G4_xcheck"]["PASS"]
                               and out["G5_selftests"]["PASS"]) for o in "AB"}
    json.dump(out, open(os.path.join(HERE, "results", "followup_gates.json"), "w"), indent=1)
    for o in "AB":
        v = out[o]
        print(f"({o}) G1 TAGGABLE flag {v['G1_taggable']}; G2 pooled δμ_cutoff {v['dmu_cutoff_pool']:.2e} ≤ "
              f"{v['G2_limit']:.2e}: {v['G2_cutoff']}; δμ_sys {v['delta_mu_sys']:.2e}")
    print(f"G4 cross-machine: {n} jobs, worst {worst:.1e} (≤ {TOL}): {out['G4_xcheck']['PASS']} {by}")
    print(f"G5 selftests: {st} → {out['G5_selftests']['PASS']}")
    print(f"taggable: (A) {out['TAGGABLE']['A']}, (B) {out['TAGGABLE']['B']}")
    return out


if __name__ == "__main__":
    if sys.argv[1] == "recompute":
        recompute(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
    elif sys.argv[1] == "gate":
        a = sys.argv[2:]
        st = None
        if "--selftests" in a:
            i = a.index("--selftests")
            st, a = a[i + 1:i + 3], a[:i]
        gate(a, st)
