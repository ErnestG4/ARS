"""Verify the merged cumulant-cut and R2-anchor results (rounds 44-45) as committed, without recomputing them.

Checks: every chunk and merge exit is 0; the jsonl rows cover every declared job exactly; the cumulant gate fields
hold their declared tolerances; B2 equals |dmu*/dmu2| x (|1.003 - 1| + 2 x 0.006); linearity < 0.01; and the
cut-validity verdict follows from its own stored minima and increments under the round-45 criteria. Exit 0 only if
all hold.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_a_anchor as RA  # noqa: E402
import route_a_cumul as RC  # noqa: E402

R = os.path.join(HERE, "results")


def exits(d):
    ex = [open(f).read().strip() for f in sorted(glob.glob(os.path.join(R, d, "logs", "c*.exit")))]
    return ex + [open(os.path.join(R, d, "merge.exit")).read().strip()]


def keys(d, prefix):
    rows = [json.loads(l) for f in sorted(glob.glob(os.path.join(R, d, prefix + "*.jsonl"))) for l in open(f)]
    return {(r["file"], r["part"], r["s"]) for r in rows}, len(rows)


cu = json.load(open(os.path.join(R, "route_a_cumul.json")))
an = json.load(open(os.path.join(R, "route_a_anchor.json")))
ok = {}
ce, ae = exits("cumul"), exits("anchor")
ok["exits"] = len(ce) == 33 and len(ae) == 21 and all(e == "exit=0" for e in ce + ae)
ck, cn = keys("cumul", "cumul_c")
ak, anr = keys("anchor", "anchor_c")
ok["cumul_jobs_complete"] = ck == set(RC.jobs()) and cn == len(ck) == 361
ok["anchor_jobs_complete"] = ak == set(RA.jobs()) and anr == len(ak) == 360
g = cu["gate"]
ok["cumul_gate"] = (g["recompute_vs_stored_max_abs"] <= 1e-10 and g["C5_vs_committed_equiv"] <= 1e-9
                    and abs(g["C5_pool"] - 1) <= 1e-4 and g["PASS"] is True)
ok["trunc_bound_le_1.2e-5"] = cu["trunc_dmu_bound_pool"] <= 1.2e-5
ok["B2_arithmetic"] = abs(an["B2"] - abs(an["dmu_dmu2_pool"]) * (abs(1.003 - 1) + 2 * 0.006)) < 1e-15
ok["linear"] = an["linearity_max_rel"] < 0.01
cv = an["cut_validity"]
inc = list(cv["increments"].values())
pos = all(v >= -1e-12 for v in cv["min_rho"].values()) and all(cv["min_p"][k] > 0 for k in ("2", "3", "4"))
dec = abs(inc[1]) > abs(inc[2]) > abs(inc[3])
ok["cut_validity_consistent"] = (cv["increments"] == cu["increments"] and cv["positive"] == pos and cv["decays"] == dec
                                 and cv["valid"] == (pos and dec))
print(json.dumps(ok, indent=1))
print(f"cut decomposition valid: {cv['valid']} ({cv['reading']});  B2 = {an['B2']:.5f};  dmu*/dmu2 = {an['dmu_dmu2_pool']:+.5f}")
sys.exit(0 if all(ok.values()) else 1)
