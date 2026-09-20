"""verify_ring_redpath.py — WHAT TURNS verify_ring.py RED.

Every pin added to ring/verify_ring.py must be able to fail on the finding it
records (green_board_must_be_informative). This checker proves it: for each
pin it mutates ONE banked value in memory (json.load is intercepted; no file
on disk is touched), runs verify_ring.py under the mutation, and requires a
red line naming that pin. A pin whose mutation leaves the board green is
INERT and this checker exits 1.

Added 2026-09-20 after the review's critic found the "each red-pathed by
in-memory mutation" claim in commit 9eb843a had no artifact behind it.
Runs verify_ring.py ~20 times (about 2 s each).
"""
import contextlib
import copy
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
VR = os.path.join(HERE, "verify_ring.py")
SRC = open(VR).read()


def run_mutated(mutator):
    """Run verify_ring.py with json.load wrapped by `mutator(basename, obj)`."""
    real_load = json.load

    def fake_load(f, *a, **k):
        obj = real_load(f, *a, **k)
        return mutator(os.path.basename(getattr(f, "name", "")), obj)

    json.load = fake_load
    buf = io.StringIO()
    g = {"__name__": "__main__", "__file__": VR}
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                exec(compile(SRC, VR, "exec"), g)
                code = 0
            except SystemExit as e:
                code = int(e.code or 0)
    finally:
        json.load = real_load
    return code, buf.getvalue()


def M(fname, fn):
    """mutator that applies fn to the table named fname (deep copy) only"""
    def m(name, obj):
        return fn(copy.deepcopy(obj)) if name == fname else obj
    return m


def M2(fnames, fn):
    def m(name, obj):
        return fn(copy.deepcopy(obj)) if name in fnames else obj
    return m


# ---- one mutation per pin: (tag that must appear on a red line, mutator) ----
def r4(o):
    for x in o["rows"]:
        if x["resid_max"] < 1e-8 and abs(x["lam1_median"]) > 1e-6:
            x["lam1_median"] = -0.015; x["relax_rate_median"] = 0.015
    return o


def r10a(o):
    for x in o["rows"]:
        if x["arm"] == "F6" and x["cloud"] == "A" and x["sigma"] == 5.0:
            x["r12"] = 0.5
    return o


def r10b(o):
    for x in o["rows"]:
        if x["arm"] == "F1" and x["cloud"] == "A" and x["kind"] == "jitter" and x["tau_j"] == 140.0:
            x["b1"] = 0.01
    return o


def r11h(o):
    for x in o["rows"]:
        if x["arm"] == "Salpha" and x["rail_ok"]:
            x["henrici_rel"] = 0.01; break
    return o


def r11g(o):
    for x in o["rows"]:
        if x["arm"] == "Seps":
            x["gap"] = 0.3; break
    return o


def r13b(o):
    for x in o["rows"]:
        if x["eps"] == 0.1:
            x["retention"] = {0.0: 0.02, 0.001: 0.1, 0.003: 0.3, 0.01: 0.5, 0.02: 0.72}[x["gamma"]]
    return o


def r13d(o):
    for x in o["rows"]:
        if x["cloud"] == "A":
            x["J_mad"] = 3
    return o


def r14(o):
    o["M2"]["staircase_q50_1e3_per_K"]["1.0"] = 0.5; return o


def r15a(o):
    o["tongue"]["0.1"]["gamma_star_meas"] = 0.012; return o


def r15b(o):
    o["vpin"]["0.03"]["max_speed"] = 0.004; return o


def r15c(o):
    o["vpin"]["0.1"]["max_speed"] = 0.015; o["vpin"]["0.03"]["max_speed"] = 0.0045
    o["tongue"]["0.1"]["gamma_star_meas"] = 0.015; o["tongue"]["0.03"]["gamma_star_meas"] = 0.0045
    return o


def r15d(o):
    o["tongue"]["0.1"]["rho"][-1] = 0.5; return o


def r17(o):
    for x in o["rows"]:
        if x["system"] == "IND_u":
            x["msd"] = [m * min(1.0, l / 100.0) for l, m in zip(x["lags"], x["msd"])]
    return o


def r18a(o):
    for x in o["rows"]:
        if x["well"] == "eps0.1_relax2000":
            x["ratio"]["T50_d0.1"] = 0.3; x["ratio"]["T200_d0.1"] = 0.3
    return o


def r18b(o):
    for x in o["rows"]:
        if x["well"] == "eps0.03_relax16000":
            x["ratio"]["T50_d0.3"] = 0.09; x["ratio"]["T200_d0.3"] = 0.09     # the sealed clause would now PASS
    return o


def r18c(o):
    for x in o["rows"]:
        if x["well"] == "eps0.03_relax16000":
            x["fp_resid"] = 5e-9; x["rail_ok"] = False
    return o


def r18d(o):
    for x in o["rows"]:
        if x["well"] == "eps0.03_relax16000":
            x["ratio"]["T50_d0.3"] = 0.05                                     # monotone again
    return o


CASES = [
    ("R4 has",                           M2(("stage1_marginal_measured.json", "stage1_contour_measured.json"), r4)),
    ("R10 pin: A's r12",                 M("stage1_coverage_measured.json", r10a)),
    ("R10 pin: A's jitter/matched",      M("stage1_coverage_measured.json", r10b)),
    ("R11 pin: a read row moves Henrici", M("stage2_nonnormal_measured.json", r11h)),
    ("R11 pin: the numerical-spectral gap", M("stage2_nonnormal_measured.json", r11g)),
    ("R13b pin: R(gamma) at eps=0.1 became monotone", M("stage3c_trapped_measured.json", r13b)),
    ("R13d T2 pin",                      M("stage3f_traversal2_measured.json", r13d)),
    ("R14 sealed: K=1",                  M("stage4_circlemap_measured.json", r14)),
    ("R15 sealed: gamma*_meas",          M("stage4b_ringtongue_measured.json", r15a)),
    ("R15 sealed: eps-scaling",          M("stage4b_ringtongue_measured.json", r15b)),
    ("R15 pin: gamma*_pred(0.1)",        M("stage4b_ringtongue_measured.json", r15c)),
    ("R15 sealed: rho",                  M("stage4b_ringtongue_measured.json", r15d)),
    ("R17 pin: IND_u saturation lag",    M("stage3e_msd_measured.json", r17)),
    ("R18 pin: the MSD well",            M("stage3h_well_delta_measured.json", r18a)),
    ("R18 pin: the sealed 0.3-rad clause", M("stage3h_well_delta_measured.json", r18b)),
    ("R18 rail: I1c well",               M("stage3h_well_delta_measured.json", r18c)),
    ("R18 pin: the I1c well's non-monotonic", M("stage3h_well_delta_measured.json", r18d)),
]


def main():
    # baseline must be green, or the red lines below prove nothing
    code0, out0 = run_mutated(lambda n, o: o)
    if code0 != 0:
        print("verify_ring_redpath: BASELINE IS RED — fix the board before red-pathing it")
        print(out0[-2000:])
        sys.exit(1)
    inert = []
    for tag, mut in CASES:
        code, out = run_mutated(mut)
        hits = [l.strip() for l in out.splitlines() if "FAIL:" in l and tag in l]
        status = "RED" if (code != 0 and hits) else "INERT"
        print(f"  [{status}] {tag}: exit={code}, {len(hits)} red line(s) naming the pin")
        if status != "RED":
            inert.append(tag)
    print(f"verify_ring_redpath: {len(CASES) - len(inert)}/{len(CASES)} pins turn red on their own finding")
    if inert:
        print("INERT pins:", inert)
        sys.exit(1)
    print("VERIFY_RING_REDPATH: PASS")


if __name__ == "__main__":
    main()
