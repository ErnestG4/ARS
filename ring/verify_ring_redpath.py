"""verify_ring_redpath.py — WHAT TURNS verify_ring.py RED.

A pin must be able to fail on the finding it records
(green_board_must_be_informative). This checker proves it for the pins listed
in CASES: each case mutates the banked table(s) in memory (json.load is
intercepted; no file on disk is touched), runs verify_ring.py under the
mutation, and requires at least one NEW red line — relative to an unmutated
baseline run — naming that pin. A case that leaves the board as it was is
INERT; a case that raises is a CRASH; either exits 1.

Coverage is what CASES enumerates, not "every pin": the 2026-09-20 review
pins (17 in commit 9eb843a, whose "each red-pathed" claim had no artifact
until this file) plus the R18 v3 pins and the R9/R10/R11/R13d/R17 chks the
final-verification critic found uncovered. Most cases mutate one value; a
few (R4, R15c, R18 rail) must move two fields that a real re-run would move
together.
Runs verify_ring.py ~30 times (about 2 s each).
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
            except Exception as e:                      # a crash is not a red line
                code = "CRASH"
                buf.write(f"\nCRASH: {type(e).__name__}: {e}\n")
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


def r18a(o):                                                                  # S5's basis: a read INSIDE the window
    for x in o["rows"]:
        if x["well"] == "eps0.1_relax2000":
            x["ratio"]["T50_d-0.1"] = 0.3
    return o


def r18b(o):
    for x in o["rows"]:
        if x["well"] == "eps0.03_relax16000":
            x["ratio"]["T50_d+0.3"] = 0.09; x["ratio"]["T200_d+0.3"] = 0.09   # the sealed clause would now PASS
    return o


def r18c(o):                                                                  # residual ALONE, flag untouched
    for x in o["rows"]:
        if x["well"] == "eps0.03_relax16000":
            x["fp_resid"] = 5e-9
    return o


def r18c2(o):                                                                 # a loosened table ceiling
    for q in o["instrument"]["params"]:
        if q["name"] == "fp_rail":
            q["value"] = 1e-3
    return o


def r18d(o):
    for x in o["rows"]:
        if x["well"] == "eps0.03_relax16000":
            x["ratio"]["T50_d+0.3"] = 0.05                                    # monotone again
    return o


def r18e(o):
    o["instrument"]["model"] = "ring_well_delta_v2"; return o


def r18f(o):                                                                  # T-dependence on the MSD well below 0.1
    for x in o["rows"]:
        if x["well"] == "eps0.1_relax2000":
            x["ratio"]["T50_d+0.05"] = 0.0
    return o


def r18g(o):                                                                  # I1c no longer anharmonic at +0.1
    for x in o["rows"]:
        if x["well"] == "eps0.03_relax16000":
            x["ratio"]["T200_d+0.1"] = 0.95
    return o


def r18h(o):                                                                  # MSD well reads symmetric/harmonic
    for x in o["rows"]:
        if x["well"] == "eps0.1_relax2000":
            x["ratio"]["T50_d-0.1"] = 0.99
    return o


def r18i(o):                                                                  # basin edge moves in
    for x in o["rows"]:
        if x["well"] == "eps0.1_relax2000":
            x["ratio"]["T50_d-0.2"] = -0.01
    return o


def r18j(o):                                                                  # I1c -delta side no longer stiff
    for x in o["rows"]:
        if x["well"] == "eps0.03_relax16000":
            x["ratio"]["T50_d-0.1"] = 0.9
    return o


def r17b(o):                                                                  # Stage 3e's typed lambda1 drifts from the well's
    o["lambda1_ref"] = -0.012; return o


def r9a(o):                                                                   # a loop survives ABOVE tau_c(A): the negative fires
    for x in o["rows"]:
        if x["cloud"] == "A" and x["arm"] == "jitter" and x["q"] == 0.5 and x["tau_j"] == 300.0:
            x["r12"] = 50.0
    return o


def r9b(o):                                                                   # E2 base detected
    for x in o["rows"]:
        if x["cloud"] == "E:400" and x["arm"] == "base" and x["q"] == 0.5:
            x["r12"] = 50.0
    return o


def r10c(o):                                                                  # tau_c(A) -> 200: matched b1 = 0.0 there (was a crash)
    for x in o["rows"]:
        if x["arm"] == "F1" and x["cloud"] == "A" and x["kind"] == "jitter" and x["tau_j"] == 140.0:
            x["r12"] = 5.0
    return o


def r11c(o):                                                                  # H_gain magnitude
    for x in o["rows"]:
        if x["arm"] == "Sgamma" and x["rail_ok"]:
            x["henrici_rel"] = 0.2; break
    return o


def r11d(o):                                                                  # fewer than 10 read rows
    for x in o["rows"]:
        if x["arm"] == "Seps":
            x["rail_ok"] = False
    return o


def r13d2(o):                                                                 # T2 C_ord M out of its recorded band
    for x in o["rows"]:
        if x["cloud"] == "C_ord":
            x["M"] = 0.95
    return o


def r13d3(o):
    for x in o["rows"]:
        if x["cloud"] == "C_perm":
            x["M"] = 0.8
    return o


def r13d4(o):
    for x in o["rows"]:
        if x["cloud"] == "D":
            x["readable"] = True; x["J_mad"] = 1; x["M"] = 1.0; x["mad"] = 0.0; x["net_turns"] = 0.0; x["n_steps"] = 1999
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
    ("R18 sealed (v3)",                  M("stage3h_well_delta_measured.json", r18a)),
    ("R18 pin: the sealed 0.3-rad clause", M("stage3h_well_delta_measured.json", r18b)),
    ("R18 rail: I1c well",               M("stage3h_well_delta_measured.json", r18c)),
    ("R18 rail: the table's fp_rail",    M("stage3h_well_delta_measured.json", r18c2)),
    ("R18 pin: the I1c well's non-monotonic", M("stage3h_well_delta_measured.json", r18d)),
    ("R18 table is",                     M("stage3h_well_delta_measured.json", r18e)),
    ("R18 the dynamic read depends on T", M("stage3h_well_delta_measured.json", r18f)),
    ("R18 pin: the I1c well is no longer anharmonic", M("stage3h_well_delta_measured.json", r18g)),
    ("R18 pin: the MSD well's recorded asymmetry", M("stage3h_well_delta_measured.json", r18h)),
    ("R18 pin: the MSD well's -delta basin edge", M("stage3h_well_delta_measured.json", r18i)),
    ("R18 pin: the I1c well's -delta side", M("stage3h_well_delta_measured.json", r18j)),
    ("R17/R18: Stage 3e's hand-typed lambda1_ref", M("stage3e_msd_measured.json", r17b)),
    ("R9 ph_topology_consistent",        M("stage1_ph_measured.json", r9a)),
    ("R9 pin: E2 base now detected",     M("stage1_ph_measured.json", r9b)),
    ("R10 pin: F1 tau_c moved",          M("stage1_coverage_measured.json", r10c)),
    ("R11 H_gain",                       M("stage2_nonnormal_measured.json", r11c)),
    ("R11 only",                         M("stage2_nonnormal_measured.json", r11d)),
    ("R13d T2 pin: C_ord",               M("stage3f_traversal2_measured.json", r13d2)),
    ("R13d T2 pin: C_perm",              M("stage3f_traversal2_measured.json", r13d3)),
    ("R13d T2: D became readable",       M("stage3f_traversal2_measured.json", r13d4)),
]


def red_lines(out):
    """the board's failure list: lines verify_ring.py prints as 'FAIL: ...' after
    the summary (a row's PROSE may contain 'FAIL:' — e.g. 'H_motion FAIL:' — and is not one)"""
    return {l.strip() for l in out.splitlines() if l.startswith("FAIL: ")}


def main():
    # Baseline captured, not required green: each case must add a NEW red
    # line naming its pin, so the row stays informative when verify_ring.py
    # is red for an unrelated reason (final-verification critic, 2026-09-20).
    code0, out0 = run_mutated(lambda n, o: o)
    base = red_lines(out0)
    if code0 == "CRASH":
        print("verify_ring_redpath: BASELINE CRASHES — nothing below is meaningful"); print(out0[-1500:]); sys.exit(1)
    print(f"  baseline: exit={code0}, {len(base)} red line(s)" + (" (board is red; cases are judged on NEW lines)" if base else ""))
    bad = []
    for tag, mut in CASES:
        code, out = run_mutated(mut)
        new = [l for l in red_lines(out) - base if tag in l]
        status = "CRASH" if code == "CRASH" else ("RED" if (code != 0 and new) else "INERT")
        print(f"  [{status}] {tag}: exit={code}, {len(new)} new red line(s) naming the pin")
        if status != "RED":
            bad.append((status, tag))
    print(f"verify_ring_redpath: {len(CASES) - len(bad)}/{len(CASES)} cases turn red on their own finding")
    if bad:
        print("NOT RED:", bad)
        sys.exit(1)
    print("VERIFY_RING_REDPATH: PASS")


if __name__ == "__main__":
    main()
